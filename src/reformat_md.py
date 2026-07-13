#!/usr/bin/env python3
"""Batch restructure markdown files using the same rules as site_builder.

Reads MD files from output/, applies text optimization + manual restructuring,
and writes cleaned MD files to a parallel output directory (default: output_reformatted/).

Usage:
    python3 reformat_md.py                     # process all MD files under output/
    python3 reformat_md.py -o ./clean          # output to ./clean instead
    python3 reformat_md.py -n 5                # process only first 5 files (dry run)
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "output"

EMOJI_MAP = {
    "魔法棒挥动": "🪄",
    "灯泡": "💡",
    "必知必读": "📌",
    "流泪": "😢",
    "星星转动": "✨",
    "钉子": "📌",
    "握手": "🤝",
    "广播": "📢",
    "幼苗": "🌱",
    "鞠躬": "🙇",
    "警告": "⚠️",
    "跳舞": "💃",
    "问号": "❓",
    "捂脸哭": "🥹",
    "加油": "💪",
    "你强": "👍",
}

CIRCLED_NUMS = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
LEADING_EMOJIS = tuple(sorted(set(EMOJI_MAP.values()), key=len, reverse=True))
EMOJI_PATTERN = "|".join(re.escape(e) for e in LEADING_EMOJIS)

HEADING_LABELS = {
    "规则概览", "适用范围", "适用对象", "前置条件", "操作入口",
    "权限说明", "上架操作", "网点申购明细查询", "撤销购买", "撤销的限制",
    "撤销成功后", "收货完成", "物流轨迹", "库存相关", "财务", "回单",
    "运单状态", "常见问题", "结果说明", "使用说明",
}

# 容器类型映射：tip（提示信息）、warning（注意事项）、danger（重点警告）、info（普通信息）
NOTE_LABELS = {
    "注": ("warning", "注意事项"),
    "注释": ("warning", "注意事项"),
    "ps": ("warning", "注意事项"),
    "PS": ("warning", "注意事项"),
    "备注": ("warning", "注意事项"),
    "提示": ("tip", "操作提示"),
    "说明": ("tip", "补充说明"),
}

RULE_KEYWORDS = (
    "仅", "必须", "不可", "不允许", "仅支持", "仅允许", "需在", "截止",
    "限制", "校验", "手续费", "返还", "退还", "禁止", "不可删除",
    "库存不足", "余额不足", "自动取消",
)

PLACEHOLDER_LINES = {"待完善", "待补充", "补充中", "TBD", "TODO"}
TRANSITION_TO_ORDERED = {"流程说明", "操作流程", "操作流程说明", "步骤如下", "流程如下", "推荐顺序"}
TRANSITION_TO_BULLET = {"清单如下", "如下清单", "清单", "补充"}

# 独立成行的纯数字/序号（含 span 包裹），需要删除
_ISOLATED_NUM_RE = re.compile(
    r"^(?:<[^>]+>)?[\s]*(?:0\d+|\d{1,2})[\s]*(?:</[^>]+>)?$"
)

# 容器语法错误修复：::: 后紧接数字（如 ::: 1. xxx）
_BROKEN_CONTAINER_RE = re.compile(r"^:::\s*(\d+\.)")


def strip_html_tags(text: str) -> str:
    """剥离 HTML span/div/p 标签，提取纯文本内容"""
    text = re.sub(r"<span[^>]*>", "", text)
    text = re.sub(r"</span>", "", text)
    text = re.sub(r"<div[^>]*>", "", text)
    text = re.sub(r"</div>", "", text)
    text = re.sub(r"<p[^>]*>", "", text)
    text = re.sub(r"</p>", "", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    return text


def fix_broken_containers(md_text: str) -> str:
    """修复 ::: 1. xxx 这类错误的容器语法"""
    def _fix(m):
        return "::: info " + m.group(1)
    return re.sub(_BROKEN_CONTAINER_RE, _fix, md_text)


def _normalize_line(line: str) -> str:
    line = line.replace("\xa0", " ")
    line = re.sub(r"[ \t]+", " ", line)
    return line.strip()


def strip_leading_markers(text: str) -> str:
    text = text.strip()
    patterns = (
        rf"^[{CIRCLED_NUMS}]\s*",
        r"^[（(]\d+[）)]\s*",
        r"^0\d+(?:-\d+)*(?=[\u4e00-\u9fffA-Za-z])\s*",
        r"^\d+\s+",
        r"^[A-Za-z]\s*[)）.．、:-]\s*",
        # 复杂序号模式：如 "4.第四步"、"5.第五步"
        r"^\d+\.\s*第\s*[一二三四五六七八九十百零〇两\d]+\s*[章节步项条部分]\s*[:：、.\-]?\s*",
        r"^第\s*[一二三四五六七八九十百零〇两\d]+\s*[章节步项条部分]\s*[:：、.\-]?\s*",
        r"^步骤\s*[一二三四五六七八九十百零〇两\d]+\s*[:：、.\-]?\s*",
        r"^\d+(?:\.\d+)*\s*[:：、.)．\-]\s*",
        r"^[一二三四五六七八九十百零〇两]+\s*[、.)．\-]\s*",
    )
    changed = True
    while changed:
        changed = False
        for pattern in patterns:
            updated = re.sub(pattern, "", text)
            if updated != text:
                text = updated
                changed = True
        for emoji in LEADING_EMOJIS:
            updated = re.sub(rf"^{re.escape(emoji)}\s*", "", text)
            if updated != text:
                text = updated
                changed = True
    return text.strip()


def strip_decorative_emoji_edges(text: str) -> str:
    if not text:
        return text
    text = re.sub(rf"^(?:{EMOJI_PATTERN})\s*", "", text)
    text = re.sub(rf"\s*(?:{EMOJI_PATTERN})+$", "", text)
    return text.strip()


def clean_heading_text(text: str) -> str:
    text = strip_leading_markers(text)
    text = strip_decorative_emoji_edges(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def optimize_text(md_text: str) -> str:
    text = md_text
    # 1. 剥离 HTML 标签（span/div/p），提取纯文本
    text = strip_html_tags(text)
    # 2. 钉钉 emoji 替换
    for label, emo in EMOJI_MAP.items():
        text = re.sub(rf"\[{re.escape(label)}\][ \t]*", f"{emo} ", text)
    # 3. 标签化文字替换
    text = re.sub(r"(?m)^\s*注意[:：]\s*", "⚠️ 注意：", text)
    text = re.sub(r"(?m)^\s*提示[:：]\s*", "💡 提示：", text)
    text = re.sub(r"(?m)^\s*说明[:：]\s*", "📝 说明：", text)
    text = re.sub(r"(?m)^\s*步骤[:：]\s*", "✅ 步骤：", text)
    # 4. 修复错误的容器语法
    text = fix_broken_containers(text)
    # 5. 清理行内多余空格和行尾空格
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _is_special_line(line: str) -> bool:
    return bool(
        re.match(r"^(#{1,6}\s|[-*]\s+|\d+[.)、]\s+|!\[|>|```|\|)", line)
        or line.startswith("<")
    )


def _is_question_line(line: str) -> bool:
    return len(line) <= 42 and line.endswith(("？", "?"))


def _normalize_list_marker(line: str) -> str:
    return re.sub(r"^(\d+(?:\.\d+)*)\.(\S)", r"\1. \2", line)


def _extract_plain_step_item(line: str) -> tuple[str, str] | None:
    patterns = (
        (r"^[（(](\d+)[)）]\s*(.+)$", "ordered"),
        (r"^(\d+)[、.)．]\s*(.+)$", "ordered"),
        (r"^(\d+)\s+(.+)$", "ordered"),
        (r"^[A-Za-z][)）.．、:-]\s*(.+)$", "bullet"),
    )
    for pattern, kind in patterns:
        match = re.match(pattern, line)
        if not match:
            continue
        content = match.group(match.lastindex).strip()
        if not content:
            return None
        return kind, strip_leading_markers(content)
    return None


def _extract_deep_heading_step(text: str) -> str | None:
    if re.match(r"^\d+\.\d+", text):
        return None
    match = re.match(r"^[（(]?(\d+)[)）、.．]\s*(.+)$", text)
    if not match:
        return None
    content = match.group(2).strip()
    return content or None


def _is_short_list_fragment(line: str) -> bool:
    text = line.strip()
    if len(text) < 2 or len(text) > 20:
        return False
    if text.endswith(("？", "?")):
        return False
    if re.search(r"[，。；：:！？!?/<>]", text):
        return False
    if re.match(r"^[#>*!-]", text):
        return False
    if re.match(r"^[（(]?\d+[)）.、]", text):
        return False
    return True


def _strip_fragment_tail(text: str) -> str:
    return text.strip().strip("、,，;；")


def make_container(content: str, container_type: str = "info", title: str = "") -> str:
    """生成 VitePress 自定义容器
    
    支持的类型: info, tip, warning, danger, details
    """
    if title:
        return f"::: {container_type} {title}\n{content.strip()}\n:::"
    return f"::: {container_type}\n{content.strip()}\n:::"


def _transition_mode_for_text(text: str) -> str | None:
    base = strip_leading_markers(text).strip().strip("：:")
    if base in TRANSITION_TO_ORDERED:
        return "ordered"
    if base in TRANSITION_TO_BULLET:
        return "bullet"
    if base.endswith("包括大类") or base.endswith("如下"):
        return "bullet"
    return None


def _should_demote_heading_text(text: str) -> bool:
    base = strip_leading_markers(text).strip()
    if base in PLACEHOLDER_LINES:
        return True
    if not base.endswith(("：", ":")):
        return False
    plain = base.strip("：:")
    return plain in TRANSITION_TO_ORDERED | TRANSITION_TO_BULLET


def restructure_markdown(md_text: str) -> str:
    lines = md_text.splitlines()
    out: list[str] = []
    in_code = False
    current_level = 0
    seen_top_h1 = False
    inside_main_section = False
    list_mode: str | None = None
    intro_list_mode: str | None = None
    ordered_list_index = 0
    in_toc_section = False
    i = 0

    def close_list() -> None:
        nonlocal list_mode, ordered_list_index
        if list_mode and out and out[-1] != "":
            out.append("")
        list_mode = None
        ordered_list_index = 0

    def append_block(block: str) -> None:
        close_list()
        out.append(block)
        out.append("")

    def append_list_item(kind: str, content: str) -> None:
        nonlocal list_mode, ordered_list_index
        content = content.strip()
        if not content:
            return
        if list_mode and list_mode != kind and out and out[-1] != "":
            out.append("")
            list_mode = None
            ordered_list_index = 0
        if list_mode is None and out and out[-1] != "":
            out.append("")
        if kind == "ordered":
            if list_mode != "ordered":
                ordered_list_index = 0
            ordered_list_index += 1
            marker = f"{ordered_list_index}. "
        else:
            marker = "- "
        out.append(f"{marker}{content}")
        list_mode = kind

    while i < len(lines):
        raw = lines[i]
        line = _normalize_line(raw)
        next_line = ""
        for j in range(i + 1, len(lines)):
            next_line = _normalize_line(lines[j])
            if next_line:
                break

        if in_toc_section:
            if not line:
                i += 1
                continue
            if line.startswith("#"):
                in_toc_section = False
            elif not line.startswith(("-", "*")) and not re.match(r"^\d+[.\s、)\]）】]", line):
                in_toc_section = False
            else:
                i += 1
                continue

        # 跳过独立成行的纯数字序号行（如 "01" "02" "001"）
        if _ISOLATED_NUM_RE.match(line):
            i += 1
            continue

        if not line:
            intro_list_mode = None
            close_list()
            if out and out[-1] != "":
                out.append("")
            i += 1
            continue

        if line.startswith("```"):
            intro_list_mode = None
            close_list()
            in_code = not in_code
            out.append(line)
            i += 1
            continue

        if in_code:
            intro_list_mode = None
            close_list()
            out.append(raw.rstrip("\n"))
            i += 1
            continue

        line = _normalize_list_marker(line)

        if line.startswith("#"):
            heading_match = re.match(r"^(#{1,6})\s*(.+)$", line)
            if heading_match:
                marks, text = heading_match.groups()
                text = text.strip()
                if re.match(r"^目录$", text):
                    in_toc_section = True
                    i += 1
                    continue
                if len(marks) >= 4:
                    deep_step = _extract_deep_heading_step(text)
                    if deep_step:
                        append_list_item("ordered", deep_step)
                        i += 1
                        continue
                normalized_heading = strip_leading_markers(text).strip()
                if _should_demote_heading_text(text):
                    if normalized_heading in PLACEHOLDER_LINES:
                        append_block(make_container(normalized_heading, "tip", "补充说明"))
                    else:
                        append_block(f"**{normalized_heading}**")
                    intro_list_mode = _transition_mode_for_text(normalized_heading)
                    i += 1
                    continue
                
                # 原始标题级别
                original_level = len(marks)
                
                # 调整标题级别
                if original_level == 1:
                    if seen_top_h1:
                        # 后续 H1 降级为 H2
                        marks = "##"
                        inside_main_section = True
                        original_level = 2
                    else:
                        # 第一个 H1 保持
                        seen_top_h1 = True
                        inside_main_section = False
                elif original_level == 2 and inside_main_section:
                    # H2 在 main section 内降级为 H3
                    marks = "###"
                    original_level = 3
                
                cleaned = clean_heading_text(text)
                if cleaned:
                    # 不添加数字序号（原文档已有 01、02 等结构编号，重复添加会导致冗余）
                    line = f"{marks} {cleaned}"
                else:
                    line = f"{marks} {text}"
            else:
                line = re.sub(r"^(#+)\s*", r"\1 ", line)
            append_block(line)
            current_level = min(len(line) - len(line.lstrip("#")), 3)
            intro_list_mode = _transition_mode_for_text(text if heading_match else line)
            i += 1
            continue

        existing_list = re.match(r"^[-*]\s+|^\d+[.)、]\s+", line)
        if _is_special_line(line):
            if existing_list:
                kind = "bullet" if line.startswith(("-", "*")) else "ordered"
                if list_mode and list_mode != kind and out and out[-1] != "":
                    out.append("")
                    list_mode = None
                if list_mode is None and out and out[-1] != "":
                    out.append("")
                out.append(line)
                list_mode = kind
                intro_list_mode = None
                i += 1
                continue
            intro_list_mode = None
            close_list()
            out.append(line)
            if line.startswith("!["):
                out.append("")
            i += 1
            continue

        if line == "目录":
            in_toc_section = True
            i += 1
            continue

        if line.endswith("概览") and len(line) <= 12:
            append_block(f"## {line}")
            current_level = 2
            intro_list_mode = None
            i += 1
            continue

        if line in HEADING_LABELS:
            level = "##" if current_level <= 1 else "###"
            append_block(f"{level} {line}")
            current_level = 2 if level == "##" else 3
            intro_list_mode = None
            i += 1
            continue

        path_match = re.match(r"^(菜单路径|路径)[:：]\s*(.+)$", line)
        if path_match:
            pretty = re.sub(r"\s*[-/]\s*", " > ", path_match.group(2).strip())
            append_block(f"> **操作入口**：{pretty}")
            intro_list_mode = None
            i += 1
            continue

        note_match = re.match(r"^(注释|注|PS|ps|备注|提示|说明)[:：]\s*(.*)$", line)
        if note_match:
            raw_label = note_match.group(1)
            container_type, label = NOTE_LABELS.get(raw_label, ("tip", "补充说明"))
            content = note_match.group(2).strip()
            if content:
                append_block(make_container(content, container_type, label))
            else:
                append_block(f"### {label}")
            current_level = 3
            intro_list_mode = None
            i += 1
            continue

        if line in PLACEHOLDER_LINES:
            append_block(make_container(line, "tip", "补充说明"))
            intro_list_mode = None
            i += 1
            continue

        plain_step = _extract_plain_step_item(line)
        if plain_step:
            kind, content = plain_step
            append_list_item(kind, content)
            i += 1
            continue

        if intro_list_mode == "bullet" and _is_short_list_fragment(line):
            append_list_item("bullet", _strip_fragment_tail(line))
            i += 1
            continue

        if intro_list_mode == "ordered" and not next_line.startswith("#"):
            append_list_item("ordered", strip_leading_markers(line).strip("：: "))
            i += 1
            continue

        intro_list_mode = None

        if _is_question_line(line):
            level = "##" if current_level <= 1 else "###"
            append_block(f"{level} {line}")
            current_level = 2 if level == "##" else 3
            i += 1
            continue

        label_match = re.match(r"^([^\s:：]{2,14})[:：]\s*(.+)$", line)
        if label_match:
            label = label_match.group(1).strip()
            value = label_match.group(2).strip()
            if label in HEADING_LABELS:
                append_block(f"### {label}")
                append_block(value)
                current_level = 3
                i += 1
                continue
        # 注：原有关键词→容器（danger/warning/tip）规则已移除。
        # 规则过宽（"仅/必须/限制"等词在正文高频出现）+ _fix_dingtalk_callout
        # 的 ::: 配对 bug，会把命中行之后的大段正文误吞进 blockquote，
        # 导致整篇文章 60-86% 变成引用块。正文保持原样不再装容器。

        append_block(line)
        i += 1

    close_list()
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


def merge_adjacent_containers(md_text: str) -> str:
    """合并相邻的同类型 VitePress 容器"""
    lines = md_text.splitlines()
    out: list[str] = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 检测容器开始 ::: type [title]
        container_match = re.match(r"^:::\s*(tip|warning|danger|info|details)\s*(.*)", line)
        if container_match:
            container_type = container_match.group(1)
            container_title = container_match.group(2).strip()
            container_lines: list[str] = []
            i += 1
            
            # 收集容器内容直到 :::
            while i < len(lines) and not lines[i].strip().startswith(":::"):
                container_lines.append(lines[i])
                i += 1
            
            # 跳过结束 :::
            if i < len(lines):
                i += 1
            
            # 跳过空行，检查是否还有同类型容器
            while i < len(lines) and lines[i].strip() == "":
                i += 1
            
            # 合并后续同类型同标题的容器
            while i < len(lines):
                next_container = re.match(r"^:::\s*(tip|warning|danger|info|details)\s*(.*)", lines[i])
                if next_container and next_container.group(1) == container_type:
                    next_title = next_container.group(2).strip()
                    if next_title == container_title:
                        i += 1
                        while i < len(lines) and not lines[i].strip().startswith(":::"):
                            container_lines.append(lines[i])
                            i += 1
                        if i < len(lines):
                            i += 1
                        while i < len(lines) and lines[i].strip() == "":
                            i += 1
                        continue
                break
            
            # 输出合并后的容器
            if container_title:
                out.append(f"::: {container_type} {container_title}")
            else:
                out.append(f"::: {container_type}")
            for cl in container_lines:
                out.append(cl)
            out.append(":::")
            out.append("")
            continue
        
        out.append(line)
        i += 1
    
    # 清理末尾空行
    while out and out[-1] == "":
        out.pop()
    
    return "\n".join(out)


def discover_md_files(root: Path) -> list[Path]:
    exclude = {".git", "__pycache__", ".pytest_cache", ".ruff_cache",
               "site", ".venv", "venv", "node_modules", "skills", "docs"}
    found: list[Path] = []

    def walk(d: Path) -> None:
        for child in sorted(d.iterdir()):
            if child.name in exclude:
                continue
            if child.is_dir():
                walk(child)
            elif child.suffix.lower() == ".md":
                found.append(child)

    walk(root)
    return found


def _normalize_ordered_list_numbers(md_text: str) -> str:
    """将连续 `1. ` 的有序列表项规范化为递增序号 1. 2. 3. ...（支持 blockquote 嵌套）"""
    lines = md_text.splitlines()
    out: list[str] = []
    counter = 0
    empty_lines_buffer: list[str] = []

    def flush():
        for el in empty_lines_buffer:
            out.append(el)
        empty_lines_buffer.clear()

    def is_blank(s: str) -> bool:
        return s.strip() == "" or re.match(r"^>+\s*$", s)

    for line in lines:
        stripped = line.strip()
        # 检查是否是以 `1.` 开头的有序列表项（含 blockquote 嵌套）
        m = re.match(r"^(>+\s*)1\.\s+(.+)$", stripped) if stripped else None
        if m:
            flush()
            counter += 1
            prefix = m.group(1)
            content = m.group(2)
            out.append(f"{prefix}{counter}. {content}")
        elif is_blank(line):
            # 空行或 `>` 视为空
            empty_lines_buffer.append(line)
        else:
            flush()
            out.append(line)
            counter = 0
    flush()
    return "\n".join(out)


def strip_bold_in_headings(md_text: str) -> str:
    """清理标题中的 ** 包裹，保持标题格式统一"""
    lines = md_text.splitlines()
    out = []
    for line in lines:
        # 匹配标题行并清理其中的 **
        if re.match(r'^#{1,6}\s+', line):
            # 清理标题中的 **
            line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
        out.append(line)
    return "\n".join(out)


def normalize_bold_label_punctuation(md_text: str) -> str:
    """将 ``**标签：**说明`` 规范为渲染器兼容的 ``**标签**：说明``。

    当前 VitePress 的 Markdown 渲染器不会把前一种紧邻中文的写法识别为
    strong 标签，会把两个星号直接显示在页面上。代码块中的示例文本不改动。
    """
    lines = md_text.splitlines()
    out = []
    in_fence = False

    for line in lines:
        if re.match(r"^\s*(?:```|~~~)", line):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            line = re.sub(r"\*\*([^*\n]*?\S)([：:])\*\*", r"**\1**\2", line)
        out.append(line)

    return "\n".join(out)


def normalize_adjacent_bold_content(md_text: str) -> str:
    """修复 ``**[标签]**正文`` 这类紧邻标签导致的星号裸露。

    Markdown 的强调分隔符紧邻方括号标签和中文正文时，VitePress 会把结尾
    ``**`` 视为普通字符。只对 ``[标签]``（含钉钉导出的转义方括号）补一个
    分隔空格；代码块中的示例不改动。
    """
    lines = md_text.splitlines()
    out = []
    in_fence = False
    bracketed_label = re.compile(
        r"(\*\*(?:\\?\[[^*\n]+?\\?\]|【[^*\n]+?】)\*\*)(?=[\u4e00-\u9fffA-Za-z0-9])"
    )

    for line in lines:
        if re.match(r"^\s*(?:```|~~~)", line):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            line = bracketed_label.sub(r"\1 ", line)
        out.append(line)

    return "\n".join(out)


def normalize_bold_markup(md_text: str) -> str:
    """将正文中的钉钉加粗标记规范为稳定的 HTML ``strong`` 标签。

    钉钉导出的 ``**`` 可能紧邻中文、方括号、引号，或出现嵌套的 ``****``。
    这些写法在 VitePress 的 Markdown 解析规则下会把星号直接显示出来。
    在格式化完成后统一改为 HTML 标签，避免解析器边界规则影响渲染；围栏代码块
    和行内代码保持原文，便于保留 Markdown 示例。
    """
    lines = md_text.splitlines()
    out = []
    in_fence = False

    def normalize_segment(segment: str) -> str:
        # 修复 ``**外层****内层****尾部**`` 这类嵌套导出，合成一对强调标记。
        previous = None
        while previous != segment:
            previous = segment
            segment = re.sub(
                r"\*\*([^*\n]+)\*\*\*\*([^*\n]+)\*\*\*\*([^*\n]+)\*\*",
                r"**\1\2\3**",
                segment,
            )

        # 修复 ``\"**标签\"**`` / ``“**标签”**``，保留引号在强调范围外。
        segment = re.sub(
            r'(["“])\*\*([^*\n]+?)(["”])\*\*',
            r"\1<strong>\2</strong>\3",
            segment,
        )
        segment = re.sub(r"\*\*([^*\n]+?)\*\*", r"<strong>\1</strong>", segment)

        # 剩余的孤立标记没有可恢复的强调范围，去掉以免直接显示在页面上。
        segment = segment.replace("**", "")
        return re.sub(r"(?:\\\*){4,}", "", segment)

    for line in lines:
        if re.match(r"^\s*(?:```|~~~)", line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        # 仅处理行内代码外的普通正文。
        parts = re.split(r"(`[^`]*`)", line)
        out.append("".join(
            part if index % 2 else normalize_segment(part)
            for index, part in enumerate(parts)
        ))

    return "\n".join(out)


def strip_operation_instruction_from_title(md_text: str) -> str:
    """移除文章 H1 中仅用于文件命名的“操作说明（书）”。"""
    lines = md_text.splitlines()
    out = []
    for line in lines:
        if line.startswith("# "):
            title = _clean_title_text(line[2:])
            line = f"# {title}"
        out.append(line)
    return "\n".join(out)


_FRONTMATTER_RE = re.compile(r"\A---\n[\s\S]*?\n---\n?")
_GENERATED_FRONTMATTER_KEYS = {"title", "description"}


def _clean_title_text(title: str) -> str:
    """清理用于页面标题/侧边栏展示的标题文本。"""
    title = title.replace("\\", "")
    title = title.replace("操作说明书", "").replace("操作说明", "")
    title = title.replace("_", "-")
    title = re.sub(r"[-]{2,}", "-", title)
    title = re.sub(r"\s{2,}", " ", title)
    return title.strip(" _：:-\t\n\r") or "未命名文档"


def _title_from_path(src: Path) -> str:
    """从文件路径推断稳定标题，避免钉钉正文标题与文件名不一致。"""
    raw = src.parent.name if src.name == "index.md" else src.stem
    return _clean_title_text(raw)


def _yaml_quote(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _frontmatter_block(title: str, description: str) -> str:
    return "---\n" + f"title: {_yaml_quote(title)}\n" + f"description: {_yaml_quote(description)}\n" + "---\n\n"


def _strip_existing_generated_frontmatter(md_text: str) -> str:
    """移除旧的 title/description frontmatter，保留非本脚本生成的复杂首页配置。"""
    match = _FRONTMATTER_RE.match(md_text)
    if not match:
        return md_text
    block = match.group(0)
    body = md_text[match.end():]
    keys = {
        line.split(":", 1)[0].strip()
        for line in block.splitlines()[1:-1]
        if ":" in line and not line.startswith(" ")
    }
    if keys and keys.issubset(_GENERATED_FRONTMATTER_KEYS):
        return body.lstrip("\n")
    return md_text


def normalize_markdown_escapes(md_text: str) -> str:
    """清理钉钉/转换器残留的 Markdown 转义，跳过围栏代码块。"""
    lines = md_text.splitlines()
    out: list[str] = []
    in_fence = False
    for line in lines:
        if re.match(r"^\s*(?:```|~~~)", line):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            line = re.sub(r"\\([+>\[\]()._-])", r"\1", line)
            if re.match(r"^#{1,6}\s+", line):
                line = line.rstrip("\\ ")
            line = line.replace(" - > ", " -> ")
        out.append(line)
    return "\n".join(out)


def ensure_document_structure(md_text: str, src: Path) -> str:
    """统一 frontmatter、H1 和短文档结构。"""
    title = _title_from_path(src)
    description = f"{title}的操作说明。"
    text = _strip_existing_generated_frontmatter(md_text).lstrip("\n")
    lines = text.splitlines()

    first_h1_idx = next((i for i, line in enumerate(lines) if re.match(r"^#\s+", line)), None)
    if first_h1_idx is None:
        lines.insert(0, f"# {title}")
        lines.insert(1, "")
    else:
        lines[first_h1_idx] = f"# {title}"
        if first_h1_idx > 0 and any(line.strip() for line in lines[:first_h1_idx]):
            prefix = lines[:first_h1_idx]
            rest = lines[first_h1_idx:]
            lines = rest[:1] + [""] + prefix + [""] + rest[1:]

    body_after_h1 = "\n".join(lines[1:]).strip()
    has_subheading = any(re.match(r"^##\s+", line) for line in lines[1:])
    is_index = src.name == "index.md"
    if body_after_h1 and not has_subheading and not is_index:
        lines = [lines[0], "", "## 操作步骤", ""] + [line for line in lines[1:] if line.strip() or line == ""]

    # 压缩多余空行，避免插入结构时产生大段空白。
    compact: list[str] = []
    blank_count = 0
    for line in lines:
        if line.strip():
            compact.append(line.rstrip())
            blank_count = 0
        else:
            blank_count += 1
            if blank_count <= 1:
                compact.append("")
    while compact and compact[-1] == "":
        compact.pop()

    return _frontmatter_block(title, description) + "\n".join(compact) + "\n"


def strip_blockquotes(md_text: str) -> str:
    """去掉所有正文级 blockquote（行首的 > 前缀）。

    钉钉文档作者常把「第一步/第二步」整段用引用块组织，渲染成大段灰色块，
    视觉效果差且不符合操作手册的阅读习惯。去掉 > 前缀让内容回归正常正文。
    保留 ::: tip/warning/danger 这类 VitePress 容器（它们不用 > 表示）。
    """
    lines = md_text.splitlines()
    out = []
    for line in lines:
        # 去掉行首的 > 或 > （含多层嵌套 > > 或 >> ）
        stripped = line.lstrip()
        if stripped.startswith(">"):
            # 循环去掉所有层级的 > 前缀及其后空格（处理 > > *例如 这种多层）
            content = stripped
            while content.startswith(">"):
                content = re.sub(r"^>\s*", "", content)
            out.append(content)
        else:
            out.append(line)
    return "\n".join(out)


def remove_trailing_index(md_text: str) -> str:
    """移除文件末尾的"更多操作索引"导航内容"""
    lines = md_text.splitlines()
    out = []
    in_index_section = False
    
    for line in lines:
        # 检测"更多操作索引"关键词
        if '更多操作索引' in line:
            in_index_section = True
            continue
        
        # 如果已进入索引区域，检查是否是索引内容
        if in_index_section:
            # 索引区域的特征：包含 📌、1️⃣、2️⃣、3️⃣ 等
            if re.match(r'^[\s>]*[\s]*(必知必会|网点|中心|云仓|黑眼圈)', line):
                continue
            # 遇到 --- 分隔线也跳过
            if line.strip() == '---':
                continue
            # 如果是空行且之前是索引内容，继续跳过
            if line.strip() == '':
                continue
            # 其他内容说明索引区域结束
            in_index_section = False
        
        out.append(line)
    
    # 清理末尾多余空行
    while out and out[-1].strip() == '':
        out.pop()
    
    return "\n".join(out)


def process_file(src: Path, dst: Path) -> None:
    md_text = src.read_text(encoding="utf-8", errors="ignore")
    md_text = optimize_text(md_text)
    md_text = restructure_markdown(md_text)
    md_text = merge_adjacent_containers(md_text)
    # 后处理：修复钉钉原文 `:::` 块（非 VitePress 容器）
    md_text = _fix_dingtalk_callout(md_text)
    # 后处理：去掉所有正文级 blockquote（> 前缀）
    md_text = strip_blockquotes(md_text)
    # 后处理：修复未闭合的容器（关键！）
    md_text = fix_unclosed_containers(md_text)
    # 后处理：规范化有序列表序号
    md_text = _normalize_ordered_list_numbers(md_text)
    # 后处理：清理标题中的 ** 包裹
    md_text = strip_bold_in_headings(md_text)
    # 后处理：修复 ``**标签：**说明`` 在 VitePress 中被显示为星号的问题
    md_text = normalize_bold_label_punctuation(md_text)
    # 后处理：修复 ``**[标签]**正文`` 紧邻导致的星号裸露
    md_text = normalize_adjacent_bold_content(md_text)
    # 后处理：统一修复钉钉导出的异常强调标记，避免页面显示原始星号
    md_text = normalize_bold_markup(md_text)
    # 后处理：标题不展示仅用于文件命名的“操作说明（书）”
    md_text = strip_operation_instruction_from_title(md_text)
    # 后处理：清理钉钉/转换器残留的转义符
    md_text = normalize_markdown_escapes(md_text)
    # 后处理：移除"更多操作索引"内容
    md_text = remove_trailing_index(md_text)
    # 后处理：统一 frontmatter、H1 和短文档结构
    md_text = ensure_document_structure(md_text, src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(md_text, encoding="utf-8")


def fix_unclosed_containers(md_text: str) -> str:
    """修复未闭合的 VitePress 容器。
    
    问题::: warning 后跟内容，没有闭合标记，导致整个后续内容被包住
    解决：
    1. 遇到标题时，如果前一个容器未闭合，先闭合它
    2. 处理嵌套在 blockquote (> ) 内的标题
    3. 处理连续多个容器的情况
    """
    lines = md_text.splitlines()
    out: list[str] = []
    container_stack: list[str] = []  # 跟踪开放的容器类型
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 去除 blockquote 前缀后检查标题
        # 例如 "> ## 第二步" 应该被识别为标题
        content_after_quote = stripped.lstrip('>').strip()
        is_heading = re.match(r'^#{1,6}\s+', content_after_quote)
        
        # 如果遇到标题，先闭合所有未闭合的容器
        if is_heading and container_stack:
            for _ in range(len(container_stack)):
                out.append(':::')
                out.append('')  # 空行
            container_stack.clear()
        
        # 检查容器开始 ::: type（包括在 blockquote 内的情况）
        container_in_quote = re.match(r'^>\s*:::\s+(tip|warning|danger|info|details)', stripped)
        container_start = re.match(r'^:::\s+(tip|warning|danger|info|details)(\s+.*)?', stripped)
        
        if container_in_quote:
            container_type = container_in_quote.group(1)
            container_stack.append(container_type)
            out.append(line)
            continue
        
        if container_start:
            container_type = container_start.group(1)
            container_stack.append(container_type)
            out.append(line)
            continue
        
        # 检查容器结束 :::（包括在 blockquote 内的情况）
        if stripped == ':::' or stripped == '> :::':
            if container_stack:
                container_stack.pop()
            out.append(line)
            continue
        
        # 检查行内容器结束 ::: 后跟其他内容
        if re.match(r'^:::\s*$', content_after_quote):
            if container_stack:
                container_stack.pop()
            out.append(line)
            continue
        
        out.append(line)
    
    # 文件结束时，如果还有未闭合的容器，全部闭合
    while container_stack:
        out.append(':::')
        out.append('')
        container_stack.pop()
    
    return "\n".join(out)


_VP_CONTAINER_TYPES = {'tip', 'warning', 'danger', 'info', 'details'}


def _fix_dingtalk_callout(md_text: str) -> str:
    """将钉钉原文的 `:::` 引用块转为 VitePress blockquote/容器"""
    lines = md_text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^:::(.*)$", line.strip())
        if m:
            rest = m.group(1).strip()
            # 检查是否是有效的 VitePress 容器开头
            is_vp = False
            for vp_type in _VP_CONTAINER_TYPES:
                if rest == vp_type or rest.startswith(f"{vp_type} "):
                    is_vp = True
                    break
            if is_vp:
                out.append(line)
                i += 1
                continue
            # 非 VitePress 容器 → 转为 blockquote 块
            i += 1
            block_content: list[str] = []
            # 如果 `:::` 后面有内容，先处理
            if rest:
                block_content.append(rest)
            # 收集到配对的结束 `:::`（如果有的话）
            while i < len(lines):
                curr = lines[i]
                if curr.strip() == ":::":
                    i += 1
                    break
                block_content.append(curr)
                i += 1
            # 将收集到的块转为 blockquote
            for bline in block_content:
                content = bline.strip()
                if content:
                    out.append(f"> {content}")
                else:
                    out.append(">")
            out.append("")
            continue
        else:
            out.append(line)
        i += 1
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch restructure markdown files")
    parser.add_argument("-s", "--source", default=str(SOURCE_DIR),
                        help="Source directory (default: output/)")
    parser.add_argument("-o", "--output", default=None,
                        help="Output directory (default: output_reformatted/)")
    parser.add_argument("-n", "--limit", type=int, default=None,
                        help="Only process first N files")
    args = parser.parse_args()

    src_dir = Path(args.source).resolve()
    dst_dir = Path(args.output).resolve() if args.output else src_dir.parent / "output_reformatted"

    if not src_dir.exists():
        print(f"Source directory not found: {src_dir}")
        sys.exit(1)

    md_files = discover_md_files(src_dir)
    if not md_files:
        print("No markdown files found.")
        sys.exit(1)

    if args.limit:
        md_files = md_files[:args.limit]

    print(f"Processing {len(md_files)} files -> {dst_dir}")

    for idx, src in enumerate(md_files, 1):
        rel = src.relative_to(src_dir)
        dst = dst_dir / rel
        process_file(src, dst)
        if idx % 50 == 0 or idx == len(md_files):
            print(f"  [{idx}/{len(md_files)}] done")

    images_src = src_dir / "根目录"
    images_dst = dst_dir / "根目录"
    if images_src.exists():
        print("Copying images...")
        copied = 0
        skipped = 0
        for img_dir in images_src.rglob("images"):
            if img_dir.is_dir():
                rel_img = img_dir.relative_to(images_src)
                dst_img = images_dst / rel_img
                dst_img.mkdir(parents=True, exist_ok=True)
                for img_file in img_dir.iterdir():
                    if img_file.is_file() and img_file.suffix.lower() in ('.png','.jpg','.jpeg','.gif','.webp','.svg'):
                        try:
                            import shutil as _shutil
                            _shutil.copy2(img_file, dst_img / img_file.name)
                            copied += 1
                        except (FileNotFoundError, PermissionError, OSError) as e:
                            skipped += 1
        print(f"Images: {copied} copied, {skipped} skipped.")

    print(f"Done! Reformatted {len(md_files)} files to {dst_dir}")


if __name__ == "__main__":
    main()
