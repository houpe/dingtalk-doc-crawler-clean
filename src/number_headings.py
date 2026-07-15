#!/usr/bin/env python3
"""文档树自动编号工具。

需求：
- 按文档树顺序自动给「目录（tree）」与「标题本身」生成层级编号。
  * 顶层章节用中文数字：一. 二. 三. ...
  * 更深层级用阿拉伯数字：2.1 / 2.1.1 / 2.1.1.1 ...
- 标题里已有的编号（如 01、1.、①、第一篇）按新顺序重新推导。
- 转换时去掉标题里的 `-` 和 `_`（用户反馈影响太奇怪）。

设计：
- `assign_tree_numbers(docs_dir)` 遍历整棵树，给每个目录/文档分配编号，
  返回 rel_path -> {display, base, depth, is_dir}。
  - display：用于侧边栏/导航展示的文本（已带编号 + 清洗后的标题）。
  - base：用于该文档内部标题继续编号的阿拉伯点分串（如 "2.1.1"）。
- `number_markdown(path, base)` 把连续编号烤进该文档的 H1..H6 文本。
- `clean_title(text)` 清洗标题（去 - _、去已有编号、去“操作说明”等）。
"""
from __future__ import annotations

import re
from pathlib import Path

SKIP_DIRS = {".vitepress", "public", "node_modules", ".git", "__pycache__"}

# 顶层栏目固定顺序（用于决定章节号）：必知必读=1，网点=2，中心=3，云仓=4，网络货运=5
TOP_ORDER = ["必知必读", "账号权限", "网点操作", "中心操作", "云仓操作", "网络货运"]

# 标题开头已有的各种编号写法，需先清除再重新编号
_LEAD_NUM_RE = re.compile(
    r"^(?:"
    r"0?\d+(?:[\-\.]\d+)*(?=[\u4e00-\u9fffA-Za-z「【{])"  # 01物料 / 2.3场景
    r"|第\s*[一二三四五六七八九十百零〇两\d]+\s*[章节篇部部分步项条]\s*[:：、.\-]?\s*"
    r"|[（(]?\d+[)）.、]\s*"
    r"|[①②③④⑤⑥⑦⑧⑨⑩]\s*"
    r"|[一二三四五六七八九十]+[.、]\s*"
    r")"
)

_CN = "零一二三四五六七八九十"


def cn(n: int) -> str:
    """阿拉伯数字转中文数字（1-99）。"""
    if n <= 0:
        return str(n)
    if n <= 10:
        return _CN[n]
    if n < 20:
        return "十" + _CN[n - 10]
    if n < 100:
        t, o = divmod(n, 10)
        return _CN[t] + "十" + (_CN[o] if o else "")
    return str(n)


def clean_title(title: str) -> str:
    """清洗标题：去掉 - _、已有编号（循环剥除所有前导编号）、操作说明/书、首尾装饰符与多余空白。"""
    t = title.strip()
    # 用户明确要求去掉 - 和 _
    t = t.replace("-", "").replace("_", "")
    # 去掉"操作说明书 / 操作说明"这类只用于文件命名的词
    t = t.replace("操作说明书", "").replace("操作说明", "")
    # 循环剥除开头已有的编号（可能有多层旧编号残留）
    for _ in range(10):  # 最多剥 10 层，防止死循环
        t = t.lstrip()   # 确保编号在行首（处理空格间隔）
        nt = _LEAD_NUM_RE.sub("", t)
        if nt != t:
            t = nt
            continue
        # 兜底：剥除行首孤立的数字+空白（处理正则 lookahead 因空格失配的情况）
        nt2 = re.sub(r'^\d+[\s\.、:：\-]*', '', t, count=1)
        if nt2 == t:
            break
        t = nt2
    # 去掉首尾装饰符号与标点
    t = t.strip(" ·•●、，。：:-\t\n\r")
    # 合并内部空白
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _top_sort_key(node: Path) -> tuple:
    c = clean_title(node.name)
    for i, key in enumerate(TOP_ORDER):
        if key in c:
            return (0, i, c)
    return (1, 0, c)


def _child_sort_key(name: str) -> tuple:
    """子节点排序：带数字前缀的按数值，其余按名称。"""
    m = re.match(r"^(\d+)", name)
    if m:
        return (0, int(m.group(1)), name)
    return (1, 0, name)


def _is_duplicate(name: str) -> bool:
    """判定抓取产生的重名副本（如 `01物料购买篇 2`、`index 2.md`、`images 2`）。"""
    stem = name[:-3] if name.endswith(".md") else name
    return re.search(r"\s+\d+$", stem) is not None


def _walk(node: Path, stack: list[int], docs_dir: Path, result: dict) -> None:
    rel = node.relative_to(docs_dir).as_posix()
    display_name = node.stem if node.suffix.lower() == ".md" else node.name
    if len(stack) == 1:
        display = cn(stack[0]) + ". " + clean_title(display_name)
    else:
        display = ".".join(str(x) for x in stack) + " " + clean_title(display_name)
    base = ".".join(str(x) for x in stack)
    result[rel] = {
        "display": display,
        "base": base,
        "depth": len(stack),
        "is_dir": node.is_dir(),
    }

    if not node.is_dir():
        return

    children = [
        c
        for c in node.iterdir()
        if (c.is_dir() or c.name.endswith(".md"))
        and c.name != "images"
        and not c.name.startswith(".")
        and not _is_duplicate(c.name)
    ]
    # 目录的 index.md 是自动生成的落地页，继承父目录编号，不占用子项序号
    index_md = None
    real_children = []
    for c in children:
        if c.is_dir():
            real_children.append(c)
        elif c.name == "index.md":
            index_md = c
        else:
            real_children.append(c)
    if index_md is not None:
        rel_i = index_md.relative_to(docs_dir).as_posix()
        result[rel_i] = {"display": display, "base": base, "depth": len(stack), "is_dir": False}

    real_children.sort(key=lambda c: _child_sort_key(c.name))
    for k, c in enumerate(real_children, start=1):
        _walk(c, stack + [k], docs_dir, result)


def assign_tree_numbers(docs_dir: Path) -> dict:
    """遍历 docs 目录树，给每个目录/文档分配层级编号。

    Returns:
        { rel_posix_path: {"display": str, "base": str, "depth": int, "is_dir": bool} }
        - 对目录：rel 为相对路径（无扩展名）。
        - 对文档：rel 为相对路径（含 .md）。
    """
    docs_dir = Path(docs_dir)
    result: dict = {}
    top_dirs = [
        p
        for p in docs_dir.iterdir()
        if p.is_dir() and p.name not in SKIP_DIRS and not p.name.startswith(".")
    ]
    top_dirs.sort(key=_top_sort_key)
    for ci, d in enumerate(top_dirs, start=1):
        _walk(d, [ci], docs_dir, result)
    return result


def number_markdown(path: Path, base: str) -> bool:
    """给单个 markdown 文档的标题烤入层级编号（H1..H6），侧边栏编号独立。

    正文编号体系（页内独立，不携带侧边栏 base 路径）：
    - H1  不加编号（文章标题本身，侧边栏已承担层级）
    - H2  中文序号：一、 二、 三、 ……
    - H3  阿拉伯点分：1.1  1.2  2.1 ……（随 H2 递增）
    - H4  括号数字：(1) (2) ……（每个 H3 下重置）
    标题文本先经 clean_title 清洗（去 - _、已有编号）。

    Returns:
        是否有修改。
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    in_code = False

    # 跳过 frontmatter
    if lines and lines[0].strip() == "---":
        out.append(lines[0])
        i = 1
        while i < len(lines):
            out.append(lines[i])
            if lines[i].strip() == "---":
                i += 1
                break
            i += 1

    h2_counter = 0                 # H2 中文序号计数
    h3_counter = 0                 # H3 在 H2 下计数
    h4_counter = 0                 # H4 在 H3 下计数（每 H3 重置）
    heading_re = re.compile(r"^(#{1,6})\s+(.*)$")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = not in_code
            out.append(line)
            i += 1
            continue
        if in_code:
            out.append(line)
            i += 1
            continue

        m = heading_re.match(line)
        if m:
            level = len(m.group(1))
            title = clean_title(m.group(2))
            if level == 1:
                # 文章标题本身不加编号（侧边栏已承担）
                new_title = title
            elif level == 2:
                h2_counter += 1
                h3_counter = 0
                h4_counter = 0
                new_title = f"{cn(h2_counter)}、{title}"
            elif level == 3:
                h3_counter += 1
                h4_counter = 0
                new_title = f"{h2_counter}.{h3_counter} {title}"
            elif level == 4:
                h4_counter += 1
                new_title = f"({h4_counter}) {title}"
            else:
                # H5/H6 兜底：不编号
                new_title = title
            out.append(f"{'#' * level} {new_title}" if new_title else line)
        else:
            out.append(line)
        i += 1

    new_text = "\n".join(out)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False
