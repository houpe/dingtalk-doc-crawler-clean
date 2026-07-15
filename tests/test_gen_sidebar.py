import tempfile
import unittest
from pathlib import Path

from src import gen_sidebar
from src import pipeline


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class GenSidebarIndexTest(unittest.TestCase):
    def test_top_level_sections_follow_the_home_page_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp)
            for section in [
                "网络货运",
                "云仓操作",
                "中心操作",
                "网点操作",
                "「_必知必读」账号权限如何开通？",
            ]:
                write(docs_dir / section / "手册.md", "# 手册")

            items = gen_sidebar.build_sidebar(docs_dir)

        self.assertEqual(
            [item["text"] for item in items],
            ["「_必知必读」账号权限如何开通？", "网点操作", "中心操作", "云仓操作", "网络货运"],
        )

    def test_sidebar_uses_saved_dingtalk_order_for_directories_and_articles(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp)
            write(docs_dir / "中心操作" / "B.md", "# B")
            write(docs_dir / "网点操作" / "Z.md", "# Z")
            write(docs_dir / "网点操作" / "A.md", "# A")

            items = gen_sidebar.build_sidebar(docs_dir, order_map={
                "网点操作/Z.md": 0,
                "网点操作/A.md": 1,
                "中心操作/B.md": 2,
            })

        self.assertEqual([item["text"] for item in items], ["网点操作", "中心操作"])
        self.assertEqual([item["text"] for item in items[0]["items"]], ["Z", "A"])

    def test_sidebar_makes_groups_collapsible_without_hiding_top_level_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp)
            write(docs_dir / "网点操作" / "客户下单篇" / "扫码下单.md", "# 扫码下单")

            items = gen_sidebar.build_sidebar(docs_dir)

        self.assertFalse(items[0]["collapsed"])
        self.assertTrue(items[0]["items"][0]["collapsed"])

    def test_normalize_order_path_matches_the_site_section_names(self):
        self.assertEqual(
            gen_sidebar.normalize_order_path("根目录/一、网点操作/02客户下单篇/客户如何通过电商平台下单？.md"),
            "网点操作/02客户下单篇/客户如何通过电商平台下单？.md",
        )

    def test_sidebar_titles_hide_operation_instruction_suffix_without_changing_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp)
            write(docs_dir / "WMS操作" / "01_创建仓库、货主、员工_操作说明书.md", "# 创建仓库")

            items = gen_sidebar.build_sidebar(docs_dir)

        article = items[0]["items"][0]
        self.assertEqual(article["text"], "01_创建仓库、货主、员工")
        self.assertEqual(article["link"], "/WMS操作/01_创建仓库、货主、员工_操作说明书")

    def test_sidebar_titles_collapse_adjacent_hyphens_and_underscores(self):
        self.assertEqual(gen_sidebar.clean("单据-_入库单"), "单据-入库单")
        self.assertEqual(gen_sidebar.clean("基础数据_-仓库管理"), "基础数据-仓库管理")

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
