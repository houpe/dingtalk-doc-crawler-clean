#!/usr/bin/env python3
"""nodeId 与站点路径之间的映射工具。

钉钉文档有永久不变的 nodeId，但文件名/目录名会随钉钉标题变化。
本模块把 output/.dws-crawl-state.json 里的 nodeId → path 映射加载出来，
并做路径规范化，让 stage 4 构建 site/docs 时能把每个 .md 文件关联到 nodeId，
从而用 /d/<nodeId> 作为稳定 URL。
"""
from __future__ import annotations

import json
from pathlib import Path

# 顶层栏目在 site/docs 里用的名字 ↔ 钉钉原始目录名（带序号前缀）
_TOP_LEVEL_RENAMES = {
    "一、网点操作": "网点操作",
    "二、中心操作": "中心操作",
    "三、云仓操作": "云仓操作",
    "四、网络货运": "网络货运",
}
# 反向：site/docs 名 → 钉钉原始名
_TOP_LEVEL_REVERSE = {v: k for k, v in _TOP_LEVEL_RENAMES.items()}


def normalize_state_path_to_docs(state_path: str) -> str:
    """把 state 里的 path（根目录/一、网点操作/.../x.md）转成 docs_dir 相对路径。

    去掉「根目录/」前缀，并把顶层栏目从「一、网点操作」改成「网点操作」。
    """
    parts = state_path.removeprefix("根目录/").split("/")
    if parts:
        parts[0] = _TOP_LEVEL_RENAMES.get(parts[0], parts[0])
    return "/".join(parts)


def normalize_docs_path_to_state(docs_path: str) -> str:
    """反向：docs_dir 相对路径 → state 里的 path 格式。"""
    parts = docs_path.split("/")
    if parts:
        parts[0] = _TOP_LEVEL_REVERSE.get(parts[0], parts[0])
    return "根目录/" + "/".join(parts)


def load_node_id_map(source_dir: Path) -> dict[str, str]:
    """从 source_dir/.dws-crawl-state.json 加载 docs_path → nodeId 映射。

    source_dir 可以是 output 或 output_optimized（stage_optimize 会复制 state 过去）。
    Returns:
        { "网点操作/08其他设置篇/业务员码设置.md": "nodeId123", ... }
    """
    state_file = source_dir / ".dws-crawl-state.json"
    if not state_file.is_file():
        return {}

    data = json.loads(state_file.read_text(encoding="utf-8"))
    nodes = data.get("nodes", data)
    mapping: dict[str, str] = {}
    for node_id, info in nodes.items():
        state_path = info.get("path", "")
        if not state_path:
            continue
        docs_path = normalize_state_path_to_docs(state_path)
        mapping[docs_path] = node_id
    return mapping


def build_redirects(old_paths: list[str], node_id_map: dict[str, str]) -> dict[str, str]:
    """构建旧 URL → 新 URL 的重定向表。

    Args:
        old_paths: 旧的 docs 路径列表（如 ['「必知必读」账号权限如何开通？/系统访问及APP下载.md']）
        node_id_map: 当前 docs_path → nodeId 映射
    Returns:
        { "/旧URL": "/d/nodeId" }
    """
    redirects: dict[str, str] = {}
    for old_path in old_paths:
        # 旧路径可能匹配当前某个 nodeId（如果只是栏目改名但文件名没变，
        # 需要按文件名反查）。这里简单实现：按末段文件名匹配。
        old_filename = old_path.rsplit("/", 1)[-1].removesuffix(".md")
        for docs_path, node_id in node_id_map.items():
            current_filename = docs_path.rsplit("/", 1)[-1].removesuffix(".md")
            if current_filename == old_filename:
                old_url = "/" + old_path.removesuffix(".md")
                redirects[old_url] = f"/d/{node_id}"
                break
    return redirects
