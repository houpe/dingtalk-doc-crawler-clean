import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vitepress_source import VitePressSource
from sync import SyncService


class FakeMaxKBClient:
    def __init__(self):
        self.created = []
        self.deleted = []
        self.next_id = 1

    def create_document(self, name, paragraphs):
        self.created.append({"name": name, "paragraphs": paragraphs})
        doc = {"id": f"doc-{self.next_id}"}
        self.next_id += 1
        return doc

    def delete_document(self, document_id):
        self.deleted.append(document_id)


class VitePressSourceTest(unittest.TestCase):
    def test_scans_manual_markdown_and_skips_indexes_and_generated_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root / "index.md", "# Home")
            self.write(root / "一、网点操作" / "index.md", "# Section")
            self.write(root / "一、网点操作" / "03订单运单篇" / "订单管理操作说明.md", "# 订单功能操作说明书")
            self.write(root / "二、中心操作" / "02调度任务篇" / "调度任务操作说明书.md", "## 业务场景")
            self.write(root / ".vitepress" / "config.md", "# Config")
            self.write(root / "public" / "manual.md", "# Public")
            self.write(root / "node_modules" / "pkg" / "README.md", "# Package")

            docs = VitePressSource(root).list_documents()

        self.assertEqual([doc.source_id for doc in docs], [
            "vitepress:一、网点操作/03订单运单篇/订单管理操作说明.md",
            "vitepress:二、中心操作/02调度任务篇/调度任务操作说明书.md",
        ])
        self.assertEqual(docs[0].name, "一、网点操作 / 03订单运单篇 / 订单管理操作说明")
        self.assertEqual(docs[1].content, "## 业务场景")

    @staticmethod
    def write(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class SyncServiceVitePressTest(unittest.TestCase):
    def test_full_sync_creates_updates_skips_and_deletes_only_vitepress_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            state_file = Path(tmp) / "state.json"
            VitePressSourceTest.write(root / "一、网点操作" / "新手册.md", "# 新手册\n\n内容")
            VitePressSourceTest.write(root / "二、中心操作" / "旧手册.md", "# 旧手册\n\n新版内容")
            state_file.write_text(json.dumps({
                "vitepress:二、中心操作/旧手册.md": {
                    "document_id": "old-doc",
                    "name": "二、中心操作 / 旧手册",
                    "hash": "stale",
                    "source": "vitepress",
                },
                "vitepress:三、云仓操作/已删除.md": {
                    "document_id": "deleted-doc",
                    "name": "三、云仓操作 / 已删除",
                    "hash": "gone",
                    "source": "vitepress",
                },
                "42": {
                    "document_id": "bookstack-doc",
                    "name": "BookStack old doc",
                    "hash": "legacy",
                },
            }), encoding="utf-8")
            fake_maxkb = FakeMaxKBClient()

            with patch("config.VITEPRESS_DOCS_DIR", str(root)), patch("config.STATE_FILE", str(state_file)):
                service = SyncService(maxkb_client=fake_maxkb)
                stats = service.full_sync()

            saved_state = json.loads(state_file.read_text(encoding="utf-8"))

        self.assertEqual(stats, {"created": 1, "updated": 1, "deleted": 1, "skipped": 0, "errors": 0})
        self.assertEqual(fake_maxkb.deleted, ["old-doc", "deleted-doc"])
        self.assertEqual([item["name"] for item in fake_maxkb.created], [
            "一、网点操作 / 新手册",
            "二、中心操作 / 旧手册",
        ])
        self.assertIn("42", saved_state)
        self.assertNotIn("vitepress:三、云仓操作/已删除.md", saved_state)
        self.assertEqual(saved_state["vitepress:一、网点操作/新手册.md"]["source"], "vitepress")

    def test_dry_run_reports_manual_count_without_creating_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            state_file = Path(tmp) / "state.json"
            VitePressSourceTest.write(root / "一、网点操作" / "手册.md", "# 手册")
            VitePressSourceTest.write(root / "一、网点操作" / "index.md", "# Index")
            state_file.write_text("{}", encoding="utf-8")
            fake_maxkb = FakeMaxKBClient()

            with patch("config.VITEPRESS_DOCS_DIR", str(root)), patch("config.STATE_FILE", str(state_file)):
                service = SyncService(maxkb_client=fake_maxkb)
                result = service.dry_run()

        self.assertEqual(result["manuals"], 1)
        self.assertEqual(fake_maxkb.created, [])


if __name__ == "__main__":
    unittest.main()
