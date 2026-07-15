#!/usr/bin/env python3
"""落地页 / 导航入口链接自愈工具。

问题背景：
    钉钉文档标题会带特殊字符（如下划线「_」、全角书名号「」、全角问号「？」），
    这些字符会原样进入目录名，从而成为 VitePress 的路由片段。
    此前首页 hero/feature 与导航的入口链接是「写死」的字符串，与真实目录名不一致，
    导致点击后 404。

解法：
    构建时根据关键词在目录树中「发现」真实的章节入口链接，用它覆盖写死的链接，
    做到与钉钉真实目录名永远一致、随重生成自愈。
"""
from __future__ import annotations

import re
from pathlib import Path

# 首页 / 导航里引用「账号权限」章节的链接（YAML / JS 两种写法）
_INDEX_LINK_RE = re.compile(r'link:\s*(/[^\s"]*必知必读[^\s"]*)')
_CONFIG_LINK_RE = re.compile(r"link:\s*'(/[^']*必知必读[^']*)'")


def discover_section_link(docs_dir: Path, *keywords: str) -> str | None:
    """根据关键词在 docs 目录树里查找匹配章节，返回站点链接（如 '/xxx/'）。

    Args:
        docs_dir: VitePress 的 docs 根目录。
        keywords: 章节目录名需同时包含的全部关键词，例如 "账号权限", "必知必读"。

    Returns:
        形如 "/「_必知必读」账号权限如何开通？/" 的链接；找不到返回 None。
    """
    docs_dir = Path(docs_dir)
    matches: list[Path] = []
    for entry in docs_dir.rglob("*"):
        if entry.is_dir() and all(k in entry.name for k in keywords):
            matches.append(entry)
    if not matches:
        return None
    # 取层级最浅、名字最短的，避免命中深层同名目录
    matches.sort(key=lambda p: (len(p.relative_to(docs_dir).parts), len(p.name)))
    rel = matches[0].relative_to(docs_dir)
    return "/" + "/".join(rel.parts) + "/"


def repair_landing_links(docs_dir: Path) -> bool:
    """把首页 index.md 与导航 config 里写死的章节入口链接，修正为真实目录链接。

    只改包含「必知必读」的 link 行，保留其余用户定制内容。
    返回是否有修改。
    """
    docs_dir = Path(docs_dir)
    target = discover_section_link(docs_dir, "账号权限", "必知必读")
    if not target:
        return False

    changed = False

    index_md = docs_dir / "index.md"
    if index_md.exists():
        text = index_md.read_text(encoding="utf-8")
        new_text = _INDEX_LINK_RE.sub(f"link: {target}", text)
        if new_text != text:
            index_md.write_text(new_text, encoding="utf-8")
            changed = True

    for cfg_name in ("config.mts", "config.js"):
        cfg = docs_dir / ".vitepress" / cfg_name
        if not cfg.exists():
            continue
        text = cfg.read_text(encoding="utf-8")
        new_text = _CONFIG_LINK_RE.sub(f"link: '{target}'", text)
        if new_text != text:
            cfg.write_text(new_text, encoding="utf-8")
            changed = True

    return changed


def fill_index_template(template: str, docs_dir: Path) -> str:
    """用真实章节链接替换模板中的 __ACCOUNT_PERM_LINK__ 占位符。"""
    target = discover_section_link(docs_dir, "账号权限", "必知必读") or "/「_必知必读」账号权限如何开通？/"
    return template.replace("__ACCOUNT_PERM_LINK__", target)
