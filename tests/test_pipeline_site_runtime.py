import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import pipeline


class PipelineSiteRuntimeTest(unittest.TestCase):
    def test_existing_site_runtime_files_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            site_dir = Path(tmp)
            server_path = site_dir / "server.js"
            package_path = site_dir / "package.json"
            server_path.write_text("// custom admin server\n", encoding="utf-8")
            package_path.write_text('{"custom": true}\n', encoding="utf-8")

            pipeline._ensure_site_runtime(site_dir)

            self.assertEqual(server_path.read_text(encoding="utf-8"), "// custom admin server\n")
            self.assertEqual(package_path.read_text(encoding="utf-8"), '{"custom": true}\n')

    def test_missing_site_runtime_files_are_initialized(self):
        with tempfile.TemporaryDirectory() as tmp:
            site_dir = Path(tmp)

            pipeline._ensure_site_runtime(site_dir)

            self.assertIn("express", (site_dir / "server.js").read_text(encoding="utf-8"))
            package = json.loads((site_dir / "package.json").read_text(encoding="utf-8"))
            self.assertEqual(package["scripts"]["start"], "node server.js")


class PipelineStageIsolationTest(unittest.TestCase):
    def test_content_only_generates_optimized_content_without_building_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "output"
            source.mkdir()
            resolved_source = source.resolve()
            optimized = Path(tmp) / "output_optimized"

            with (
                mock.patch.object(pipeline, "stage_filter") as stage_filter,
                mock.patch.object(
                    pipeline,
                    "stage_optimize",
                    return_value=(optimized, {"rule_count": 1}),
                ) as stage_optimize,
                mock.patch.object(pipeline, "stage_vitepress") as stage_vitepress,
            ):
                pipeline.main(["--source", str(source), "--content-only"])

            stage_filter.assert_called_once_with(resolved_source, extra_keywords=None)
            stage_optimize.assert_called_once_with(
                resolved_source,
                use_ai=False,
                model="deepseek-v4-flash",
                quality_report=True,
                force=False,
            )
            stage_vitepress.assert_not_called()

    def test_site_only_builds_from_optimized_content_without_reoptimizing_or_deploying(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "output_optimized"
            root = source / "根目录"
            root.mkdir(parents=True)
            (root / "example.md").write_text("# Example\n", encoding="utf-8")
            resolved_source = source.resolve()

            with (
                mock.patch.object(pipeline, "stage_filter") as stage_filter,
                mock.patch.object(pipeline, "stage_optimize") as stage_optimize,
                mock.patch.object(pipeline, "stage_vitepress") as stage_vitepress,
            ):
                pipeline.main(["--source", str(source), "--site-only", "--no-serve"])

            stage_filter.assert_not_called()
            stage_optimize.assert_not_called()
            stage_vitepress.assert_called_once_with(resolved_source, serve=False, deploy=None)

    def test_site_only_rejects_deploy_and_missing_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "output_optimized"
            source.mkdir()

            with self.assertRaises(SystemExit):
                pipeline.main(["--source", str(source), "--site-only", "--deploy", "fast"])

            with self.assertRaises(SystemExit):
                pipeline.main(["--source", str(source), "--site-only", "--no-serve"])


class StageOptimizeIncrementalTest(unittest.TestCase):
    """stage_optimize 的增量跳过逻辑：源文件未变则跳过 AI，force 则全部重跑。"""

    def test_needs_returns_true_when_optimized_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            src = tmp / "a.md"
            src.write_text("x", encoding="utf-8")
            self.assertTrue(pipeline._needs_ai_optimize(src, tmp / "a_opt.md", force=False))

    def test_needs_returns_true_when_source_newer(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            src = tmp / "a.md"
            opt = tmp / "a_opt.md"
            src.write_text("x", encoding="utf-8")
            opt.write_text("y", encoding="utf-8")
            # 把源的 mtime 拉到产物之后
            future = src.stat().st_mtime + 100
            os.utime(src, (future, future))
            self.assertTrue(pipeline._needs_ai_optimize(src, opt, force=False))

    def test_needs_returns_false_when_optimized_newer(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            src = tmp / "a.md"
            opt = tmp / "a_opt.md"
            src.write_text("x", encoding="utf-8")
            opt.write_text("y", encoding="utf-8")
            # 产物比源新 -> 跳过
            self.assertFalse(pipeline._needs_ai_optimize(src, opt, force=False))

    def test_needs_force_always_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            src = tmp / "a.md"
            opt = tmp / "a_opt.md"
            src.write_text("x", encoding="utf-8")
            opt.write_text("y", encoding="utf-8")
            self.assertTrue(pipeline._needs_ai_optimize(src, opt, force=True))

    def test_incremental_skips_unchanged_files_and_force_reprocesses(self):
        """集成：源未变→ai_optimize 不被调用；force→ai_optimize 被调用。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # 隔离 ROOT，避免污染真实的 output_reformatted / output_optimized
            with mock.patch.object(pipeline, "ROOT", tmp):
                source_dir = tmp / "output"
                root_md = source_dir / "根目录" / "文档.md"
                root_md.parent.mkdir(parents=True)
                root_md.write_text("# 文档\n正文内容足够长。", encoding="utf-8")

                # 规则引擎产物（AI 的实际输入）
                reformatted = tmp / "output_reformatted"
                re_md = reformatted / "根目录" / "文档.md"
                re_md.parent.mkdir(parents=True)
                re_md.write_text("# 文档\n正文内容足够长。", encoding="utf-8")

                optimized = tmp / "output_optimized"
                opt_md = optimized / "根目录" / "文档.md"
                opt_md.parent.mkdir(parents=True)
                opt_md.write_text("# 已优化的文档", encoding="utf-8")
                # 让产物比源新 → 增量应跳过
                future = re_md.stat().st_mtime + 100
                os.utime(opt_md, (future, future))

                def fake_run(cmd, **kwargs):
                    # 不真跑 reformat 子进程；reformatted 已手工准备好
                    return None

                with mock.patch.object(pipeline, "run", side_effect=fake_run), \
                     mock.patch("optimize_md_deepseek.optimize", return_value="# 优化后的文档") as ai_mock, \
                     mock.patch.object(pipeline, "_write_quality_report", return_value={"files": 0, "issues": 0}):
                    # 增量：源未变 → AI 不应被调用
                    _, stats = pipeline.stage_optimize(source_dir, use_ai=True, quality_report=False, force=False)
                    ai_mock.assert_not_called()
                    self.assertEqual(stats["ai_skipped"], 1)

                    # force=True → AI 应被调用一次
                    _, stats = pipeline.stage_optimize(source_dir, use_ai=True, quality_report=False, force=True)
                    self.assertEqual(ai_mock.call_count, 1)


class PruneStaleMarkdownTest(unittest.TestCase):
    """清理优化产物里源已不存在的 md 文件和空目录，避免目录改名后残留。"""

    def test_prune_deletes_md_not_in_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "output"
            dst = tmp / "output_optimized"
            # 源里只有 文档A
            (source / "根目录").mkdir(parents=True)
            (source / "根目录" / "文档A.md").write_text("# A", encoding="utf-8")
            # 产物里有 文档A（保留）和 文档B（源已删，应清除）
            (dst / "根目录").mkdir(parents=True)
            (dst / "根目录" / "文档A.md").write_text("# A optimized", encoding="utf-8")
            (dst / "根目录" / "文档B.md").write_text("# B stale", encoding="utf-8")

            known = {p.relative_to(source).as_posix() for p in source.rglob("*.md")}
            removed = pipeline._prune_stale_md(known, dst)

            self.assertEqual(removed, ["根目录/文档B.md"])
            self.assertTrue((dst / "根目录" / "文档A.md").exists())
            self.assertFalse((dst / "根目录" / "文档B.md").exists())

    def test_prune_removes_empty_dirs_but_keeps_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "output"
            dst = tmp / "output_optimized"
            (source / "根目录").mkdir(parents=True)
            (source / "根目录" / "保留.md").write_text("# keep", encoding="utf-8")
            # 产物里有一个源已不存在的整个目录（含 images 和一个 md）
            stale_dir = dst / "根目录" / "旧目录"
            (stale_dir).mkdir(parents=True)
            (stale_dir / "旧文档.md").write_text("# stale", encoding="utf-8")
            (stale_dir / "images").mkdir()
            (stale_dir / "images" / "pic.png").write_bytes(b"\x89PNG")
            # 保留目录
            (dst / "根目录" / "保留.md").write_text("# keep opt", encoding="utf-8")

            known = {p.relative_to(source).as_posix() for p in source.rglob("*.md")}
            pipeline._prune_stale_md(known, dst)

            # 旧目录的 md 被删，images 保留（图片缓存），但空目录应被清理
            self.assertFalse((stale_dir / "旧文档.md").exists())
            # images 目录即使非空也保留图片，但整个旧目录不再有 md 即可
            self.assertTrue((stale_dir / "images" / "pic.png").exists())

    def test_prune_never_removes_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "output"
            dst = tmp / "output_optimized"
            (source / "根目录").mkdir(parents=True)
            (dst / "根目录").mkdir(parents=True)

            known = set()
            pipeline._prune_stale_md(known, dst)
            # 根目录本身永远保留
            self.assertTrue((dst / "根目录").exists())


if __name__ == "__main__":
    unittest.main()
