import re
import tempfile
import unittest
from pathlib import Path

from src import pipeline


ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "site" / "docs"


class CleanSectionUrlTest(unittest.TestCase):
    def test_top_level_sections_do_not_start_with_chinese_ordinals(self):
        legacy_dirs = sorted(
            path.name
            for path in DOCS_DIR.iterdir()
            if path.is_dir() and re.match(r"^[一二三四五六七八九十]+、", path.name)
        )

        self.assertEqual([], legacy_dirs)

    def test_home_nav_and_sidebar_use_clean_section_urls(self):
        old_urls = [
            "/一、网点操作/",
            "/二、中心操作/",
            "/三、云仓操作/",
            "/四、网络货运/",
            "/「必知必读」账号权限如何开通？/",
            "/「*必知必读」账号权限如何开通？/",
        ]
        files = [
            DOCS_DIR / "index.md",
            DOCS_DIR / ".vitepress" / "config.mts",
            DOCS_DIR / ".vitepress" / "sidebar-data.mjs",
        ]
        content = "\n".join(path.read_text(encoding="utf-8") for path in files)

        for old_url in old_urls:
            self.assertNotIn(old_url, content)

        for new_url in [
            "/「_必知必读」账号权限如何开通？/",
            "/网点操作/",
            "/中心操作/",
            "/云仓操作/",
            "/网络货运/",
        ]:
            self.assertIn(new_url, content)

    def test_pipeline_copy_normalizes_legacy_top_level_section_names(self):
        with self.subTest("legacy source directory"):
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                src = tmp_path / "src"
                dst = tmp_path / "dst"
                legacy_doc = src / "一、网点操作" / "手册.md"
                legacy_doc.parent.mkdir(parents=True)
                legacy_doc.write_text("# 手册", encoding="utf-8")

                pipeline._vp_copy_content(src, dst)

                self.assertFalse((dst / "一、网点操作").exists())
                self.assertTrue((dst / "网点操作" / "手册.md").exists())


if __name__ == "__main__":
    unittest.main()
