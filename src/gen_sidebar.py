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


def clean(text: str) -> str:
    text = STRIP_RE.sub("", text)
    return text.strip("：:- \t\n\r") or text


def build_sidebar(dir_path: Path, rel_prefix: str = "") -> list:
    items = []
    try:
        entries = sorted(os.listdir(dir_path))
    except PermissionError:
        return items

    dirs = [i for i in entries
            if (dir_path / i).is_dir() and i not in SKIP_DIRS and not i.startswith(".")]
    mds = [i for i in entries if i.endswith(".md") and i != "index.md"]

    for d in sorted(dirs):
        full = dir_path / d
        sub_rel = f"{rel_prefix}/{d}" if rel_prefix else d
        sub_items = build_sidebar(full, sub_rel)

        # If no sub-items found, add direct md files as items
        if not sub_items:
            sub_mds = sorted([i for i in os.listdir(full)
                              if i.endswith(".md") and i != "index.md"
                              and not i.startswith(".")])
            for md in sub_mds:
                raw = md.replace(".md", "")
                sub_items.append({
                    "text": clean(raw),
                    "link": f"/{sub_rel}/{raw}"
                })

        if sub_items:
            items.append({
                "text": clean(d),
                "collapsed": True,
                "items": sub_items
            })

    for md in sorted(mds):
        raw = md.replace(".md", "")
        link = f"/{rel_prefix}/{raw}" if rel_prefix else f"/{raw}"
        items.append({"text": clean(raw), "link": link})

    return items


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

    data = build_sidebar(docs_dir)

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
