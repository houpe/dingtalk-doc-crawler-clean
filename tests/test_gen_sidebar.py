import tempfile
import unittest
from pathlib import Path

from src import gen_sidebar
from src import pipeline


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class GenSidebarIndexTest(unittest.TestCase):
    def test_parent_index_links_to_child_directories_and_rewrites_stale_generated_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp)
            section = docs_dir / "二、中心操作"
            write(section / "01司机操作篇" / "运输任务操作说明书.md", "# 运输任务")
            write(section / "02调度任务篇" / "调度任务操作说明书.md", "# 调度任务")
            write(
                section / "index.md",
                "# 中心操作\n\n## 分类\n\n- **[司机操作篇](./)**\n- **[调度任务篇](./)**\n",
            )

            gen_sidebar.build_sidebar(docs_dir)

            content = (section / "index.md").read_text(encoding="utf-8")

        self.assertIn("- **[司机操作篇](./01司机操作篇/)**", content)
        self.assertIn("- **[调度任务篇](./02调度任务篇/)**", content)
        self.assertNotIn("- **[司机操作篇](./)**", content)
        self.assertNotIn("- **[调度任务篇](./)**", content)

    def test_custom_index_content_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp)
            section = docs_dir / "一、网点操作"
            custom_content = "# 网点操作\n\n这里是人工维护的说明。"
            write(section / "01物料购买篇" / "如何物料购买充值？.md", "# 充值")
            write(section / "index.md", custom_content)

            gen_sidebar.build_sidebar(docs_dir)

            content = (section / "index.md").read_text(encoding="utf-8")

        self.assertEqual(content, custom_content)


class PipelineIndexTest(unittest.TestCase):
    def test_pipeline_rewrites_stale_generated_parent_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            section = Path(tmp) / "二、中心操作"
            write(section / "01司机操作篇" / "运输任务操作说明书.md", "# 运输任务")
            write(section / "02调度任务篇" / "调度任务操作说明书.md", "# 调度任务")
            write(
                section / "index.md",
                "# 中心操作\n\n## 分类\n\n- **[司机操作篇](./)**\n- **[调度任务篇](./)**\n",
            )

            pipeline._ensure_dir_index(section, [])

            content = (section / "index.md").read_text(encoding="utf-8")

        self.assertIn("- **[司机操作篇](./01司机操作篇/)**", content)
        self.assertIn("- **[调度任务篇](./02调度任务篇/)**", content)
        self.assertNotIn("- **[司机操作篇](./)**", content)
        self.assertNotIn("- **[调度任务篇](./)**", content)

if __name__ == "__main__":
    unittest.main()
