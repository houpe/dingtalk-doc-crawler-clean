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
    for label, emo in EMOJI_MAP.items():
        text = re.sub(rf"\[{re.escape(label)}\][ \t]*", f"{emo} ", text)
    text = re.sub(r"(?m)^\s*注意[:：]\s*", "⚠️ 注意：", text)
    text = re.sub(r"(?m)^\s*提示[:：]\s*", "💡 提示：", text)
    text = re.sub(r"(?m)^\s*说明[:：]\s*", "📝 说明：", text)
    text = re.sub(r"(?m)^\s*步骤[:：]\s*", "✅ 步骤：", text)
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
    # 标题计数器
    h2_counter = 0
    h3_counter = 0
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
                        h2_counter += 1
                        h3_counter = 0
                    else:
                        # 第一个 H1 保持
                        seen_top_h1 = True
                        inside_main_section = False
                elif original_level == 2 and inside_main_section:
                    # H2 在 main section 内降级为 H3
                    marks = "###"
                    original_level = 3
                    h3_counter += 1
                else:
                    # 其他情况：更新计数器
                    if original_level == 2:
                        h2_counter += 1
                        h3_counter = 0
                    elif original_level == 3:
                        h3_counter += 1
                
                cleaned = clean_heading_text(text)
                if cleaned:
                    # 添加序号
                    if original_level == 2:
                        line = f"{marks} {h2_counter}. {cleaned}"
                    elif original_level == 3:
                        line = f"{marks} {h2_counter}.{h3_counter} {cleaned}"
                    else:
                        # H1 不需要序号
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
            if label in {"机构限制", "时间限制", "操作校验", "手续费", "保价费",
                        "库存相关", "财务", "回单", "运单状态"}:
                append_block(make_container(value, "warning", label))
                i += 1
                continue

        if line.startswith(("例如", "比如")):
            content = line.strip()
            if content.startswith(("例如", "比如")):
                content = re.sub(r"^(例如|比如)\s*[,，:]?\s*", "", content)
            append_block(make_container(content, "tip", "示例说明"))
            i += 1
            continue

        if any(keyword in line for keyword in RULE_KEYWORDS):
            extra = next_line if next_line.startswith(("例如", "比如")) else None
            append_block(make_container(line, "danger", "重点提醒"))
            if extra:
                i += 2
            else:
                i += 1
            continue

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


def process_file(src: Path, dst: Path) -> None:
    md_text = src.read_text(encoding="utf-8", errors="ignore")
    md_text = optimize_text(md_text)
    md_text = restructure_markdown(md_text)
    md_text = merge_adjacent_containers(md_text)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(md_text, encoding="utf-8")


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
        for img_dir in images_src.rglob("images"):
            if img_dir.is_dir():
                rel_img = img_dir.relative_to(images_src)
                dst_img = images_dst / rel_img
                if not dst_img.exists():
                    shutil.copytree(img_dir, dst_img)
        print("Images copied.")

    print(f"Done! Reformatted {len(md_files)} files to {dst_dir}")


if __name__ == "__main__":
    main()
