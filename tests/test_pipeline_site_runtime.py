import json
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
                model="deepseek-chat",
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


if __name__ == "__main__":
    unittest.main()
