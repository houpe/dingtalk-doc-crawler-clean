import tempfile
import unittest
from pathlib import Path

from src import dws_crawler


class DwsCrawlerOutputTest(unittest.TestCase):
    def test_prepare_output_directory_removes_stale_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            stale_dir = output_dir / "根目录" / "旧目录"
            stale_dir.mkdir(parents=True)
            (stale_dir / "已删除文档.md").write_text("stale", encoding="utf-8")

            output_base = dws_crawler.prepare_output_directory(output_dir)

            self.assertEqual(output_base, output_dir / "根目录")
            self.assertTrue(output_base.is_dir())
            self.assertFalse((output_base / "旧目录" / "已删除文档.md").exists())


if __name__ == "__main__":
    unittest.main()
