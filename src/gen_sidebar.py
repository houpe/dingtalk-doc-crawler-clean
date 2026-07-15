#!/usr/bin/env python3
"""从 site/docs/ 目录结构自动生成 sidebar-data.mjs

这是唯一允许修改 sidebar 的入口。config.mts 从此文件 import sidebar。
pipeline.py 会在每次构建时自动调用此脚本。

Usage:
    python3 src/gen_sidebar.py              # 默认 site/docs
    python3 src/gen_sidebar.py /path/to/docs
"""
import os, json, re, sys
from pathlib import Path
from number_headings import assign_tree_numbers, clean_title, _is_duplicate

STRIP_RE = re.compile(
    r"^(?:"
    r"[一二三四五六七八九十百零〇两]+\s*[、.．\s]\s*"
    r"|0?\d+(?:[\-\.]\d+)*(?=[\u4e00-\u9fffA-Za-z「【{])"
    r"|0?\d+(?:[\-\.]\d+)*[\s、.．:\-\)\]）】]"
    r"|[\(（]\d+[\)）.]\s*"
    r"|第\s*[一二三四五六七八九十百零〇两\d]+\s*[章节步项条部分]\s*[:：、.\-]?\s*"
    r")+"
)

SKIP_DIRS = {"images", ".vitepress", "public", "node_modules", ".git", "__pycache__"}
INDEX_SECTION_HEADINGS = {"## 分类", "## 文档"}
INDEX_LINK_RE = re.compile(r"^- (?:\*\*)?\[[^\]]+\]\(\./[^)]*\)(?:\*\*)?$")
TOP_LEVEL_SECTION_ORDER = {
    "网点操作": 1,
    "中心操作": 2,
    "云仓操作": 3,
    "网络货运": 4,
}
TOP_LEVEL_PATH_RENAMES = {
    "一、网点操作": "网点操作",
    "二、中心操作": "中心操作",
    "三、云仓操作": "云仓操作",
    "四、网络货运": "网络货运",
}


def strip_operation_instruction(text: str) -> str:
    """移除仅用于文件命名的“操作说明（书）”，保留真实链接文件名。"""
    cleaned = text.replace("操作说明书", "").replace("操作说明", "")
    cleaned = re.sub(r"_{2,}", "_", cleaned)
    cleaned = re.sub(r"[-_]{2,}", "-", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip(" _：:-\t\n\r") or text


def clean(text: str) -> str:
    text = STRIP_RE.sub("", text)
    text = strip_operation_instruction(text)
    return text.strip("：:- \t\n\r") or text


def directory_sort_key(name: str, *, is_top_level: bool) -> tuple[int, str]:
    """首页与侧边栏使用相同的一级栏目顺序，其余目录保持名称排序。"""
    label = clean(name)
    if not is_top_level:
        return (100, label)
    if "必知必读" in label:
        return (0, label)
    return (TOP_LEVEL_SECTION_ORDER.get(label, 100), label)


def normalize_order_path(path: str) -> str:
    """把钉钉原始路径转换为 site/docs 使用的路径。"""
    parts = path.removeprefix("根目录/").split("/")
    if parts:
        parts[0] = TOP_LEVEL_PATH_RENAMES.get(parts[0], parts[0])
    return "/".join(parts)


def _has_docs(dir_path: Path) -> bool:
    return any(path.name != "index.md" for path in dir_path.rglob("*.md"))


FRONTMATTER_RE = re.compile(r"\A---\n[\s\S]*?\n---\n?")


def strip_frontmatter(content: str) -> str:
    return FRONTMATTER_RE.sub("", content, count=1).lstrip("\n")


def _is_generated_index(content: str) -> bool:
    content = strip_frontmatter(content)
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    if len(lines) <= 1:
        return True
    if not lines[0].startswith("# "):
        return False

    for line in lines[1:]:
        if line in INDEX_SECTION_HEADINGS or line == "_（本目录暂无文档）_":
            continue
        if INDEX_LINK_RE.match(line):
            continue
        return False
    return True


def build_sidebar(dir_path: Path, rel_prefix: str = "", tree: dict | None = None) -> list:
    items = []
    try:
        entries = sorted(os.listdir(dir_path))
    except PermissionError:
        return items

    dirs = [
        i for i in entries
        if (dir_path / i).is_dir() and i not in SKIP_DIRS
        and not i.startswith(".") and not _is_duplicate(i)
    ]
    mds = [
        i for i in entries
        if i.endswith(".md") and i != "index.md"
        and not i.startswith(".") and not _is_duplicate(i)
    ]

    def node_rel(name: str, is_dir: bool) -> str:
        rel = f"{rel_prefix}/{name}" if rel_prefix else name
        return rel if is_dir else rel + ".md"

    def disp(name: str, is_dir: bool) -> str:
        rel = node_rel(name, is_dir)
        if tree and rel in tree:
            return tree[rel]["display"]
        return clean_title(name)

    def base_key(name: str, is_dir: bool) -> list[int]:
        rel = node_rel(name, is_dir)
        if tree and rel in tree:
            return [int(x) for x in tree[rel]["base"].split(".")]
        return [10 ** 9]

    for d in sorted(dirs, key=lambda n: base_key(n, True)):
        full = dir_path / d
        sub_rel = node_rel(d, True)
        sub_items = build_sidebar(full, sub_rel, tree)

        # If no sub-items found, add direct md files as items
        if not sub_items:
            sub_mds = sorted(
                [i for i in os.listdir(full)
                 if i.endswith(".md") and i != "index.md"
                 and not i.startswith(".") and not _is_duplicate(i)],
                key=lambda n: base_key(n, False),
            )
            for md in sub_mds:
                raw = md.replace(".md", "")
                sub_items.append({"text": disp(raw, False), "link": f"/{sub_rel}/{raw}"})

        if sub_items:
            # `collapsed` 同时启用 VitePress 的折叠箭头：一级栏目保持展开，
            # 二级及更深目录默认收起，当前文章所在分支会由 VitePress 自动展开。
            items.append({
                "text": disp(d, True),
                "collapsed": bool(rel_prefix),
                "items": sub_items
            })
            # 为目录生成 index.md，使 /模块名/ 这种目录 URL 可访问
            _ensure_dir_index(full, sub_items, clean_title(d), tree)

    for md in sorted(mds, key=lambda n: base_key(n[:-3], False)):
        raw = md.replace(".md", "")
        link = f"/{rel_prefix}/{raw}" if rel_prefix else f"/{raw}"
        items.append({"text": disp(raw, False), "link": link})

    return items


def _yaml_quote(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _frontmatter(title: str) -> str:
    description = f"{title}目录下的操作文档列表。"
    return "---\n" + f"title: {_yaml_quote(title)}\n" + f"description: {_yaml_quote(description)}\n" + "---\n\n"


def _ensure_dir_index(dir_path: Path, sub_items: list[dict], title: str, tree: dict | None = None) -> None:
    """为目录生成 index.md（文章列表页），使 /目录名/ URL 可访问。

    title 传入的是已清洗（无编号）的目录名，编号由 number_headings 在构建阶段统一烤入。
    已存在且不是自动生成样式的 index.md（用户手写）不覆盖。
    """
    index_md = dir_path / "index.md"

    if index_md.exists():
        content = index_md.read_text(encoding="utf-8")
        if not _is_generated_index(content):
            return

    parts = [_frontmatter(title) + f"# {title}\n"]
    entries = sorted(os.listdir(dir_path))
    sub_dirs = [
        d for d in entries
        if (dir_path / d).is_dir()
        and d not in SKIP_DIRS
        and not d.startswith(".")
        and not _is_duplicate(d)
        and _has_docs(dir_path / d)
    ]
    docs = [
        md for md in entries
        if md.endswith(".md") and md != "index.md"
        and not md.startswith(".") and not _is_duplicate(md)
    ]

    if sub_dirs:
        parts.append("## 分类\n")
        for d in sub_dirs:
            parts.append(f"- **[{clean_title(d)}](./{d}/)**")
        parts.append("")

    if docs:
        parts.append("## 文档\n")
        for md in docs:
            name = md[:-3]
            parts.append(f"- [{clean_title(name)}](./{name})")
        parts.append("")

    if not sub_dirs and not docs:
        parts.append("_（本目录暂无文档）_\n")

    index_md.write_text("\n".join(parts), encoding="utf-8")


def main():
    if len(sys.argv) > 1:
        docs_dir = Path(sys.argv[1]).resolve()
    else:
        docs_dir = Path(__file__).resolve().parent.parent / "site" / "docs"

    if not docs_dir.exists():
        print(f"Error: {docs_dir} not found")
        sys.exit(1)

    vp_dir = docs_dir / ".vitepress"
    vp_dir.mkdir(exist_ok=True)

    # 标题自动编号：一次性计算整棵文档树的编号（顶层中文、深层阿拉伯）
    tree = assign_tree_numbers(docs_dir)

    data = build_sidebar(docs_dir, tree=tree)

    # Count articles
    total = 0
    def count(items):
        nonlocal total
        for i in items:
            if "link" in i:
                total += 1
            if "items" in i:
                count(i["items"])
    count(data)

    mjs = "export default " + json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    (vp_dir / "sidebar-data.mjs").write_text(mjs, encoding="utf-8")

    print(f"✓ sidebar-data.mjs generated: {total} articles, {len(data)} sections")


if __name__ == "__main__":
    main()
