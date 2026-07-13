import tempfile
import unittest
from pathlib import Path

from src import doc_quality


class DocQualityTest(unittest.TestCase):
    def test_reports_missing_frontmatter_and_h1_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            md = root / "业务员码设置.md"
            md.write_text("# 司机派送常见问题\n\n正文", encoding="utf-8")

            issues = doc_quality.analyze_docs(root)

            self.assertEqual(len(issues), 1)
            self.assertIn("缺少 title/description frontmatter", issues[0].issues)
            self.assertTrue(any("H1 与文件名不一致" in item for item in issues[0].issues))

    def test_accepts_well_structured_doc(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            md = root / "业务员码设置.md"
            md.write_text(
                '---\ntitle: "业务员码设置"\ndescription: "业务员码设置的操作说明。"\n---\n\n'
                "# 业务员码设置\n\n"
                "## 适用场景\n\n用于维护业务员码。\n"
                "## 操作步骤\n\n"
                "1. 打开系统。\n2. 点击保存。\n"
                "## 注意事项\n\n以系统实际展示为准。\n",
                encoding="utf-8",
            )

            issues = doc_quality.analyze_docs(root)

            self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
