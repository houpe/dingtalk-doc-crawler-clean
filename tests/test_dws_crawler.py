import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import dws_crawler


def workspace_file(node_id="node-1", update_time=1, name="操作手册"):
    return {
        "nodeId": node_id,
        "updateTime": update_time,
        "name": name,
        "nodeType": "file",
        "extension": "adoc",
    }


def write_document(_node_id, name, output_dir):
    path = output_dir / f"{dws_crawler.sanitize_filename(name)}.md"
    path.write_text("# 文档", encoding="utf-8")
    return path


def write_changed_document(_node_id, name, output_dir):
    path = output_dir / f"{dws_crawler.sanitize_filename(name)}.md"
    path.write_text("# 操作手册\n新步骤\n保留内容", encoding="utf-8")
    return path


class DwsCrawlerOutputTest(unittest.TestCase):
    def test_prepare_output_directory_preserves_documents_for_incremental_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            stale_document = output_dir / "根目录" / "旧目录" / "文档.md"
            stale_document.parent.mkdir(parents=True)
            stale_document.write_text("existing", encoding="utf-8")

            output_base = dws_crawler.prepare_output_directory(output_dir)

            self.assertEqual(output_base, output_dir / "根目录")
            self.assertTrue(stale_document.exists())

    def test_prepare_output_directory_removes_documents_for_full_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            stale_document = output_dir / "根目录" / "旧目录" / "文档.md"
            stale_document.parent.mkdir(parents=True)
            stale_document.write_text("stale", encoding="utf-8")

            output_base = dws_crawler.prepare_output_directory(output_dir, full=True)

            self.assertEqual(output_base, output_dir / "根目录")
            self.assertFalse(stale_document.exists())

    def test_unchanged_document_is_not_read_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            nodes = [workspace_file()]

            with patch.object(dws_crawler, "list_workspace_nodes", return_value=nodes), patch.object(
                dws_crawler, "download_doc", side_effect=write_document
            ), patch.object(
                dws_crawler, "download_images_from_markdown", return_value={"failed": 0}
            ):
                first = dws_crawler.sync_documents(output_dir)

            with patch.object(dws_crawler, "list_workspace_nodes", return_value=nodes), patch.object(
                dws_crawler, "download_doc", side_effect=AssertionError("不应重新读取正文")
            ):
                second = dws_crawler.sync_documents(output_dir)

            self.assertEqual(first["downloaded"], 1)
            self.assertEqual(second, {"downloaded": 0, "skipped": 1, "removed": 0, "failed": 0})

    def test_changed_and_deleted_documents_update_local_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            root = output_dir / "根目录"
            root.mkdir(parents=True)
            changed = root / "旧名称.md"
            deleted = root / "已删除.md"
            changed.write_text("old", encoding="utf-8")
            deleted.write_text("old", encoding="utf-8")
            dws_crawler.save_state(
                output_dir,
                {
                    "node-1": {"updateTime": 1, "path": "根目录/旧名称.md", "imagesComplete": True},
                    "node-2": {"updateTime": 1, "path": "根目录/已删除.md", "imagesComplete": True},
                },
            )

            with patch.object(
                dws_crawler, "list_workspace_nodes", return_value=[workspace_file("node-1", 2, "新名称")]
            ), patch.object(dws_crawler, "download_doc", side_effect=write_document), patch.object(
                dws_crawler, "download_images_from_markdown", return_value={"failed": 0}
            ):
                stats = dws_crawler.sync_documents(output_dir)

            self.assertEqual(stats, {"downloaded": 1, "skipped": 0, "removed": 1, "failed": 0})
            self.assertFalse(changed.exists())
            self.assertFalse(deleted.exists())
            self.assertTrue((root / "新名称.md").exists())
            self.assertEqual(dws_crawler.load_state(output_dir)["node-1"]["updateTime"], 2)

    def test_incremental_sync_removes_untracked_legacy_documents_after_a_rename(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            root = output_dir / "根目录"
            current = root / "新名称.md"
            legacy = root / "旧目录" / "旧名称.md"
            current.parent.mkdir(parents=True)
            legacy.parent.mkdir(parents=True)
            current.write_text("current", encoding="utf-8")
            legacy.write_text("legacy", encoding="utf-8")
            dws_crawler.save_state(
                output_dir,
                {
                    "node-1": {
                        "updateTime": 1,
                        "path": "根目录/新名称.md",
                        "imagesComplete": True,
                    }
                },
            )

            with patch.object(
                dws_crawler, "list_workspace_nodes", return_value=[workspace_file("node-1", 1, "新名称")]
            ):
                stats = dws_crawler.sync_documents(output_dir)

            self.assertEqual(stats, {"downloaded": 0, "skipped": 1, "removed": 1, "failed": 0})
            self.assertTrue(current.exists())
            self.assertFalse(legacy.exists())
            report = json.loads(dws_crawler.report_path(output_dir).read_text(encoding="utf-8"))
            self.assertEqual(report["changes"], [{
                "status": "清理残留",
                "path": "根目录/旧目录/旧名称.md",
            }])

    def test_incomplete_images_force_a_retry_even_when_update_time_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            document = output_dir / "根目录" / "操作手册.md"
            document.parent.mkdir(parents=True)
            document.write_text("old", encoding="utf-8")
            dws_crawler.save_state(
                output_dir,
                {"node-1": {"updateTime": 1, "path": "根目录/操作手册.md", "imagesComplete": False}},
            )

            with patch.object(dws_crawler, "list_workspace_nodes", return_value=[workspace_file()]), patch.object(
                dws_crawler, "download_doc", side_effect=write_document
            ) as download, patch.object(
                dws_crawler, "download_images_from_markdown", return_value={"failed": 0}
            ):
                stats = dws_crawler.sync_documents(output_dir)

            self.assertEqual(download.call_count, 1)
            self.assertEqual(stats["downloaded"], 1)
            self.assertTrue(dws_crawler.load_state(output_dir)["node-1"]["imagesComplete"])

    def test_change_report_names_the_document_and_its_line_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            document = output_dir / "根目录" / "操作手册.md"
            document.parent.mkdir(parents=True)
            document.write_text("# 操作手册\n旧步骤\n保留内容", encoding="utf-8")
            dws_crawler.save_state(
                output_dir,
                {"node-1": {"updateTime": 1, "path": "根目录/操作手册.md", "imagesComplete": True}},
            )

            with patch.object(dws_crawler, "list_workspace_nodes", return_value=[workspace_file(update_time=2)]), patch.object(
                dws_crawler, "download_doc", side_effect=write_changed_document
            ), patch.object(
                dws_crawler, "download_images_from_markdown", return_value={"failed": 0}
            ):
                dws_crawler.sync_documents(output_dir)

            report = json.loads(dws_crawler.report_path(output_dir).read_text(encoding="utf-8"))
            self.assertEqual(report["summary"]["downloaded"], 1)
            self.assertEqual(report["changes"][0]["status"], "更新")
            self.assertEqual(report["changes"][0]["path"], "根目录/操作手册.md")
            self.assertEqual(report["changes"][0]["content"]["addedLines"], 1)
            self.assertEqual(report["changes"][0]["content"]["removedLines"], 1)
            self.assertIn("+ 新步骤", report["changes"][0]["content"]["preview"])
            self.assertIn("- 旧步骤", report["changes"][0]["content"]["preview"])

    def test_incremental_update_keeps_previous_image_cache(self):
        """更新单篇文档不应逐张删除共享 images 目录中的旧图。"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            root = output_dir / "根目录"
            document = root / "操作手册.md"
            images_dir = root / "images"
            old_image = images_dir / "操作手册_1_old.png"
            images_dir.mkdir(parents=True)
            document.write_text("# 操作手册\n![旧图](./images/操作手册_1_old.png)\n", encoding="utf-8")
            old_image.write_bytes(b"old-image")
            dws_crawler.save_state(
                output_dir,
                {"node-1": {"updateTime": 1, "path": "根目录/操作手册.md", "imagesComplete": True}},
            )

            with patch.object(
                dws_crawler, "list_workspace_nodes", return_value=[workspace_file(update_time=2)]
            ), patch.object(dws_crawler, "download_doc", side_effect=write_changed_document), patch.object(
                dws_crawler, "download_images_from_markdown", return_value={"failed": 0}
            ):
                stats = dws_crawler.sync_documents(output_dir)

            self.assertEqual(stats["downloaded"], 1)
            self.assertTrue(old_image.exists())

    def test_system_changelog_is_collected_despite_the_general_update_exclusion(self):
        documents = dws_crawler.collect_documents(
            [workspace_file("log-1", 1, "中通仓链 20260709系统更新日志")]
        )

        self.assertTrue(documents["log-1"]["isChangelog"])

    def test_obsolete_documents_are_excluded_even_when_they_are_system_changelogs(self):
        documents = dws_crawler.collect_documents([
            workspace_file("obsolete-1", 1, "车辆操作说明（作废）"),
            workspace_file("obsolete-log", 1, "中通仓链系统更新日志（作废）"),
        ])

        self.assertTrue(dws_crawler.should_exclude("车辆操作说明（作废）"))
        self.assertEqual(documents, {})

    def test_changelog_review_matches_feature_to_manual_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            changelog_path = output_dir / "根目录" / "中通仓链 20260709系统更新日志.md"
            manual_path = output_dir / "根目录" / "06_出库作业.md"
            changelog_path.parent.mkdir(parents=True)
            changelog_path.write_text(
                "## 💡 **【出库计划】支持按承运公司查询**\n\n优化点：便于按承运公司查询\n",
                encoding="utf-8",
            )
            manual_path.write_text("# 出库作业\n\n出库计划支持创建和查询。", encoding="utf-8")
            documents = {
                "log-1": {
                    "name": "中通仓链 20260709系统更新日志",
                    "path": "根目录/中通仓链 20260709系统更新日志.md",
                    "updateTime": 2,
                    "isChangelog": True,
                },
                "manual-1": {
                    "name": "06_出库作业",
                    "path": "根目录/06_出库作业.md",
                    "updateTime": 1,
                    "isChangelog": False,
                },
            }

            review = dws_crawler.build_changelog_review(output_dir, documents)

            self.assertEqual(review["summary"], {"logs": 1, "updates": 1, "candidateArticles": 1})
            candidate = review["logs"][0]["entries"][0]["candidates"][0]
            self.assertEqual(candidate["name"], "06_出库作业")
            self.assertEqual(candidate["match"], "正文")


if __name__ == "__main__":
    unittest.main()
