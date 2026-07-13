import unittest

from src import reformat_md


class BoldLabelNormalizationTest(unittest.TestCase):
    def test_moves_label_colon_outside_bold_markers(self):
        source = "- **公司：**可以理解为仓库结算主体。\n\n**注意：**总部员工才使用权限管理。"

        result = reformat_md.normalize_bold_label_punctuation(source)

        self.assertEqual(
            result,
            "- **公司**：可以理解为仓库结算主体。\n\n**注意**：总部员工才使用权限管理。",
        )

    def test_preserves_code_fence_examples(self):
        source = "```md\n**公司：**可以保留为示例\n```\n\n**部门：**需要关联仓库。"

        result = reformat_md.normalize_bold_label_punctuation(source)

        self.assertEqual(
            result,
            "```md\n**公司：**可以保留为示例\n```\n\n**部门**：需要关联仓库。",
        )

    def test_inserts_a_separator_after_a_bracketed_bold_label(self):
        source = "2. **\\[WMS对接\\]**OMS创建货主保存->自动同步货主信息到WMS中"

        result = reformat_md.normalize_adjacent_bold_content(source)

        self.assertEqual(
            result,
            "2. **\\[WMS对接\\]** OMS创建货主保存->自动同步货主信息到WMS中",
        )

    def test_converts_malformed_bold_markers_to_reliable_strong_tags(self):
        source = (
            '会判断"**上级库存余额"**是否满足；\n'
            '**2.[点击立即接单]**点击立即接单；\n'
            '**[OMS创建****出库单(2B)****]**1.1，填写信息；\n'
            '`**代码示例不改**`\n'
            '```md\n**代码块示例不改**\n```'
        )

        result = reformat_md.normalize_bold_markup(source)

        self.assertEqual(
            result,
            '会判断"<strong>上级库存余额</strong>"是否满足；\n'
            '<strong>2.[点击立即接单]</strong>点击立即接单；\n'
            '<strong>[OMS创建出库单(2B)]</strong>1.1，填写信息；\n'
            '`**代码示例不改**`\n'
            '```md\n**代码块示例不改**\n```',
        )

    def test_removes_escaped_four_asterisk_placeholder(self):
        source = '当前差错已在\\*\\*\\*\\*,不可申诉。'

        result = reformat_md.normalize_bold_markup(source)

        self.assertEqual(result, '当前差错已在,不可申诉。')

    def test_removes_operation_instruction_from_document_h1_only(self):
        source = "# 创建仓库、货主、员工 操作说明书\n\n## 操作说明\n\n正文"

        result = reformat_md.strip_operation_instruction_from_title(source)

        self.assertEqual(result, "# 创建仓库、货主、员工\n\n## 操作说明\n\n正文")

    def test_collapses_adjacent_hyphen_and_underscore_in_document_h1(self):
        result = reformat_md.strip_operation_instruction_from_title("# 单据-_入库单\n\n正文")

        self.assertEqual(result, "# 单据-入库单\n\n正文")

    def test_adds_frontmatter_and_uses_filename_as_h1(self):
        source = "# 司机派送常见问题\n\n✨ <strong>业务员编码在哪里看？</strong>✨"
        result = reformat_md.ensure_document_structure(
            source,
            reformat_md.Path("/tmp/业务员码设置.md"),
        )

        self.assertIn('title: "业务员码设置"', result)
        self.assertIn('description: "业务员码设置的操作说明。"', result)
        self.assertIn("# 业务员码设置", result)
        self.assertNotIn("# 司机派送常见问题", result)

    def test_cleans_markdown_escape_residue(self):
        source = "# 2C出库作业\\\n\nPC端操作\\+ PDA端操作\n\n路径：出库 -\\> 出库包裹"
        result = reformat_md.normalize_markdown_escapes(source)

        self.assertEqual(result, "# 2C出库作业\n\nPC端操作+ PDA端操作\n\n路径：出库 -> 出库包裹")

    def test_enriches_sparse_document_with_manual_sections(self):
        source = "# 旧标题\n\n点击保存后查看状态。"
        result = reformat_md.ensure_document_structure(
            source,
            reformat_md.Path("/tmp/包仓仓位明细.md"),
        )

        self.assertIn("## 适用场景", result)
        self.assertIn("## 前置条件", result)
        self.assertIn("## 操作入口", result)
        self.assertIn("## 操作步骤", result)
        self.assertIn("## 操作结果", result)
        self.assertIn("## 注意事项", result)
        self.assertIn("## 常见问题", result)
        self.assertIn("点击保存后查看状态。", result)


if __name__ == "__main__":
    unittest.main()
