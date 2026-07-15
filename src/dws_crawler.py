#!/usr/bin/env python3
"""使用 dws CLI 从钉钉知识库拉取文档（默认增量同步）。"""
import argparse
import difflib
import json
import shutil
import subprocess
import sys
import re
from pathlib import Path
import urllib.request
import hashlib
from datetime import datetime, timezone

EXCLUDE_KEYWORDS = ["日志", "周报", "月报", "记录", "更新", "历史", "作废"]
# 精确排除的文件名（不含扩展名）：占位模板文档，含无法解析的示例链接，不应抓取。
EXCLUDE_FILE_NAMES = {"操作说明模板"}
WORKSPACE_ID = "dN0G7JJOWjJ4jmWY"
STATE_FILE_NAME = ".dws-crawl-state.json"
REPORT_FILE_NAME = ".dws-crawl-last-report.json"
CHANGELOG_REVIEW_FILE_NAME = ".dws-changelog-review.json"
DIFF_PREVIEW_LIMIT = 12


def run_cmd(cmd: list[str], check=True):
    """执行命令并返回结果"""
    result = subprocess.run(cmd, capture_output=True, text=True, check=check, timeout=60)
    if result.stdout:
        return json.loads(result.stdout)
    return {}


def should_exclude(name: str) -> bool:
    """检查文件名是否包含排除关键词，或命中精确排除名单"""
    if any(kw in name for kw in EXCLUDE_KEYWORDS):
        return True
    # 去掉扩展名后精确匹配（如 "操作说明模板.md" -> "操作说明模板"）
    stem = name.rsplit(".", 1)[0] if "." in name else name
    return stem in EXCLUDE_FILE_NAMES


def is_system_changelog(name: str) -> bool:
    """系统更新日志用于判断待更正手册，不能被通用“更新”排除规则跳过。"""
    return "系统更新日志" in name


def list_workspace_nodes(workspace_id: str) -> list[dict]:
    """列出知识库顶层节点（支持分页）"""
    all_nodes = []
    page_token = None
    while True:
        cmd = ["dws", "doc", "list", "--workspace", workspace_id, "--format", "json"]
        if page_token:
            cmd.extend(["--page-token", page_token])
        data = run_cmd(cmd)
        all_nodes.extend(data.get("nodes", []))
        if not data.get("hasMore", False):
            break
        page_token = data.get("pageToken")
    return all_nodes


def list_folder_nodes(folder_id: str) -> list[dict]:
    """列出文件夹下的所有节点（支持分页）"""
    all_nodes = []
    page_token = None
    while True:
        cmd = ["dws", "doc", "list", "--folder", folder_id, "--format", "json"]
        if page_token:
            cmd.extend(["--page-token", page_token])
        data = run_cmd(cmd)
        all_nodes.extend(data.get("nodes", []))
        if not data.get("hasMore", False):
            break
        page_token = data.get("pageToken")
    return all_nodes


def download_doc(node_id: str, name: str, output_dir: Path) -> Path | None:
    """下载单个文档，并返回写入路径。"""
    try:
        result = subprocess.run(
            ["dws", "doc", "read", "--node", node_id, "--content-format", "markdown", "--format", "json"],
            capture_output=True, text=True, check=True, timeout=60
        )
        data = json.loads(result.stdout) if result.stdout else {}
        content = data.get("markdown", "")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, json.JSONDecodeError) as e:
        print(f"  [错误] {name}: {e}")
        return None
    
    if not content:
        print(f"  [跳过] {name} (内容为空)")
        return None
    
    safe_name = sanitize_filename(name)
    file_path = output_dir / f"{safe_name}.md"
    file_path.write_text(content, encoding='utf-8')
    print(f"  [下载] {name}")
    return file_path


def sanitize_filename(filename: str) -> str:
    """清理文件名以符合文件系统要求"""
    # 替换非法字符为下划线
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename).strip()
    return "_" if sanitized in {"", ".", ".."} else sanitized


def download_images_from_markdown(md_file: Path, images_dir: Path) -> dict:
    """从 markdown 文件中下载所有远程图片到 images 目录"""
    content = md_file.read_text(encoding="utf-8")
    # 匹配 markdown 图片语法: ![alt](url) 或 ![alt](url "title")
    img_pattern = r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)"
    img_matches = re.findall(img_pattern, content)
    
    # 匹配 HTML img 标签: <img src="url"...>
    html_img_pattern = r'<img\s+[^>]*src="([^"]+)"[^>]*>'
    html_img_matches = re.findall(html_img_pattern, content, re.IGNORECASE)
    
    result = {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    if not img_matches and not html_img_matches:
        return result
    
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # 处理 markdown 图片
    for idx, (alt, url) in enumerate(img_matches, 1):
        if not url.startswith("http"):
            result["skipped"] += 1
            continue
        
        result["total"] += 1
        try:
            # 生成文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            ext = ".png"
            if ".jpg" in url or ".jpeg" in url:
                ext = ".jpg"
            elif ".gif" in url:
                ext = ".gif"
            elif ".webp" in url:
                ext = ".webp"
            
            safe_name = sanitize_filename(md_file.stem)
            local_name = f"{safe_name}_{idx}_{url_hash}{ext}"
            local_path = images_dir / local_name
            
            # 下载图片
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    local_path.write_bytes(response.read())
                    # 替换 URL 为本地路径
                    rel_path = local_path.relative_to(md_file.parent)
                    old_text = f"![{alt}]({url})"
                    new_text = f"![{alt}]({rel_path})"
                    content = content.replace(old_text, new_text)
                    result["success"] += 1
                    print(f"    [图片] {local_name} ✓")
                else:
                    result["failed"] += 1
                    print(f"    [图片失败] {url[:50]}... : HTTP {response.status}")
        except Exception as e:
            print(f"    [图片失败] {url[:50]}... : {e}")
            result["failed"] += 1
    
    # 处理 HTML 图片
    for idx, url in enumerate(html_img_matches, 1):
        if not url.startswith("http"):
            result["skipped"] += 1
            continue
        
        result["total"] += 1
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            ext = ".png"
            if ".jpg" in url or ".jpeg" in url:
                ext = ".jpg"
            elif ".gif" in url:
                ext = ".gif"
            elif ".webp" in url:
                ext = ".webp"
            
            safe_name = sanitize_filename(md_file.stem)
            local_name = f"{safe_name}_html_{idx}_{url_hash}{ext}"
            local_path = images_dir / local_name
            
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    local_path.write_bytes(response.read())
                    rel_path = local_path.relative_to(md_file.parent)
                    content = content.replace(url, str(rel_path))
                    result["success"] += 1
                    print(f"    [图片] {local_name} ✓")
                else:
                    result["failed"] += 1
                    print(f"    [图片失败] {url[:50]}... : HTTP {response.status}")
        except Exception as e:
            print(f"    [图片失败] {url[:50]}... : {e}")
            result["failed"] += 1
    
    # 保存修改后的 markdown
    if result["success"] > 0:
        md_file.write_text(content, encoding="utf-8")
    
    return result


def download_all_images(output_dir: Path) -> dict:
    """扫描所有 markdown 文件并下载其中的远程图片"""
    print("\n开始下载图片...")
    total_stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0, "files": 0}
    
    for md_file in output_dir.rglob("*.md"):
        total_stats["files"] += 1
        # 为每个 markdown 文件创建对应的 images 目录
        images_dir = md_file.parent / "images"
        stats = download_images_from_markdown(md_file, images_dir)
        
        for key in ["total", "success", "failed", "skipped"]:
            total_stats[key] += stats[key]
    
    print(f"\n图片下载完成！")
    print(f"  处理文件: {total_stats['files']} 个")
    print(f"  下载图片: {total_stats['success']}/{total_stats['total']} 张")
    if total_stats["failed"] > 0:
        print(f"  失败: {total_stats['failed']} 张")
    
    return total_stats


def prepare_output_directory(output_dir: Path, *, full: bool = False) -> Path:
    """准备原始文档目录；仅 ``--full`` 时清空已有结果。"""
    if full and output_dir.exists():
        shutil.rmtree(output_dir)

    output_base = output_dir / "根目录"
    output_base.mkdir(parents=True, exist_ok=True)
    return output_base


def state_path(output_dir: Path) -> Path:
    return output_dir / STATE_FILE_NAME


def report_path(output_dir: Path) -> Path:
    """返回最近一次抓取变更报告的保存位置。"""
    return output_dir / REPORT_FILE_NAME


def changelog_review_path(output_dir: Path) -> Path:
    return output_dir / CHANGELOG_REVIEW_FILE_NAME


def load_state(output_dir: Path) -> dict[str, dict]:
    """加载上一次成功同步的节点状态；损坏状态不会阻塞全量重新比对。"""
    path = state_path(output_dir)
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        nodes = data.get("nodes", data)
        if not isinstance(nodes, dict):
            raise ValueError("nodes 不是对象")
        return {node_id: value for node_id, value in nodes.items() if isinstance(value, dict)}
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"[警告] 状态文件无法读取，将重新下载需要比对的文档：{error}")
        return {}


def save_state(output_dir: Path, nodes: dict[str, dict]) -> None:
    """原子保存同步状态，避免中途停止留下半份 JSON。"""
    path = state_path(output_dir)
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")
    payload = {"version": 1, "nodes": nodes}
    temporary_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(path)


def save_report(output_dir: Path, stats: dict[str, int], changes: list[dict], error: str | None = None) -> None:
    """保存本次同步的可回看变更清单。"""
    path = report_path(output_dir)
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")
    payload = {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": stats,
        "changes": changes,
    }
    if error:
        payload["error"] = error
    temporary_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(path)


def summarize_markdown_changes(previous: str, current: str) -> dict:
    """生成适合日志和 JSON 报告的行级 Markdown 差异摘要。"""
    added_lines: list[str] = []
    removed_lines: list[str] = []
    for line in difflib.unified_diff(
        previous.splitlines(),
        current.splitlines(),
        fromfile="旧版本",
        tofile="新版本",
        lineterm="",
    ):
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            added_lines.append(line[1:])
        elif line.startswith("-"):
            removed_lines.append(line[1:])

    preview = [f"+ {line[:180]}" for line in added_lines[:DIFF_PREVIEW_LIMIT]]
    remaining = DIFF_PREVIEW_LIMIT - len(preview)
    preview.extend(f"- {line[:180]}" for line in removed_lines[:remaining])
    return {
        "addedLines": len(added_lines),
        "removedLines": len(removed_lines),
        "preview": preview,
    }


def print_change(change: dict) -> None:
    """把单条变更用管理台日志中易读的形式输出。"""
    status = change["status"]
    path = change.get("path") or change.get("previousPath") or change.get("nodeId", "未知文档")
    print(f"  [{status}] {path}")
    if change.get("previousPath") and change["previousPath"] != change.get("path"):
        print(f"    路径: {change['previousPath']} → {change['path']}")
    if "previousUpdateTime" in change and "updateTime" in change:
        print(f"    更新时间: {change['previousUpdateTime']} → {change.get('updateTime')}")
    elif "previousUpdateTime" in change:
        print(f"    最后更新时间: {change['previousUpdateTime']}")
    if "content" in change:
        content = change["content"]
        print(f"    内容行变更: +{content['addedLines']} / -{content['removedLines']}")
        for line in content["preview"]:
            print(f"      {line}")
    if "lineCount" in change:
        print(f"    文档内容: {change['lineCount']} 行")
    if change.get("imagesFailed"):
        print(f"    图片下载失败: {change['imagesFailed']} 张，将在下次增量时重试")


def _normalize_match_text(text: str) -> str:
    return re.sub(r"[\s\W_]+", "", text, flags=re.UNICODE).lower()


def extract_changelog_entries(markdown: str) -> list[dict]:
    """提取系统更新日志中的功能名称和“优化点”说明。"""
    entries: list[dict] = []
    sections = re.split(r"(?=^##\s+)", markdown, flags=re.MULTILINE)

    for section in sections:
        heading_match = re.search(r"^##\s+.*?【([^】]+)】", section, flags=re.MULTILINE)
        if not heading_match:
            continue
        feature = heading_match.group(1).strip()
        plain = re.sub(r"<[^>]+>", "", section)
        plain = plain.replace("**", "")
        detail_match = re.search(r"优化点[：:]\s*([^\n]+)", plain)
        entries.append({
            "feature": feature,
            "detail": detail_match.group(1).strip() if detail_match else "",
        })

    return entries


def build_changelog_review(output_dir: Path, documents: dict[str, dict]) -> dict:
    """用系统更新日志的功能关键词匹配可能需要更正的操作手册。"""
    manuals = [
        {"nodeId": node_id, **document}
        for node_id, document in documents.items()
        if not document.get("isChangelog") and (output_dir / document["path"]).is_file()
    ]
    logs = []

    for node_id, document in documents.items():
        if not document.get("isChangelog"):
            continue
        source_path = output_dir / document["path"]
        if not source_path.is_file():
            continue

        entries = []
        for entry in extract_changelog_entries(source_path.read_text(encoding="utf-8")):
            keyword = _normalize_match_text(entry["feature"])
            candidates = []
            if keyword:
                for manual in manuals:
                    content = (output_dir / manual["path"]).read_text(encoding="utf-8")
                    title_match = keyword in _normalize_match_text(manual["name"])
                    content_match = keyword in _normalize_match_text(content)
                    if title_match or content_match:
                        candidates.append({
                            "nodeId": manual["nodeId"],
                            "path": manual["path"],
                            "name": manual["name"],
                            "match": "标题" if title_match else "正文",
                        })
            entries.append({**entry, "candidates": candidates})

        logs.append({
            "nodeId": node_id,
            "path": document["path"],
            "name": document["name"],
            "updateTime": document.get("updateTime"),
            "entries": entries,
        })

    entry_count = sum(len(log["entries"]) for log in logs)
    candidate_count = sum(
        len(entry["candidates"])
        for log in logs
        for entry in log["entries"]
    )
    return {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "logs": len(logs),
            "updates": entry_count,
            "candidateArticles": candidate_count,
        },
        "logs": logs,
    }


def save_changelog_review(output_dir: Path, review: dict) -> None:
    path = changelog_review_path(output_dir)
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")
    temporary_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary_path.replace(path)


def print_changelog_review(review: dict) -> None:
    summary = review["summary"]
    if not summary["logs"]:
        print("更新日志核对：未发现系统更新日志。")
        return

    print(
        "更新日志核对："
        f"{summary['logs']} 篇日志、{summary['updates']} 项更新、"
        f"{summary['candidateArticles']} 篇候选手册。"
    )
    for log in review["logs"]:
        for entry in log["entries"]:
            candidates = entry["candidates"]
            if candidates:
                names = "、".join(candidate["name"] for candidate in candidates)
                print(f"  [待核对] {entry['feature']} → {names}")
            else:
                print(f"  [未匹配] {entry['feature']}（请人工指定对应手册）")


def relative_document_path(parent: Path, name: str) -> str:
    """返回位于 output 下的安全 Markdown 相对路径。"""
    return (parent / f"{sanitize_filename(name)}.md").as_posix()


def collect_documents(nodes: list[dict], parent: Path = Path("根目录"), depth: int = 0) -> dict[str, dict]:
    """遍历钉钉目录，只收集元数据，不读取文档正文。"""
    documents: dict[str, dict] = {}
    indent = "  " * depth

    for node in nodes:
        node_name = node.get("name", "")
        node_type = node.get("nodeType", "")
        node_id = node.get("nodeId", "")

        if not node_id or not node_name:
            print(f"{indent}[跳过] 缺少 nodeId 或名称的节点")
            continue
        changelog = is_system_changelog(node_name)
        # 系统更新日志可绕过“更新”关键词，但标记为作废的任何文档都不能进入站点。
        if should_exclude(node_name) and (not changelog or "作废" in node_name):
            print(f"{indent}[排除] {node_name}")
            continue

        if node_type == "folder":
            print(f"{indent}[扫描] 文件夹: {node_name}")
            children = list_folder_nodes(node_id)
            documents.update(
                collect_documents(children, parent / sanitize_filename(node_name), depth + 1)
            )
        elif node_type == "file" and node.get("extension") == "adoc":
            documents[node_id] = {
                "updateTime": node.get("updateTime"),
                "path": relative_document_path(parent, node_name),
                "name": node_name,
                "isChangelog": changelog,
            }

    # dict 保留钉钉列表接口的顺序；把它保存下来供站点侧边栏复用。
    for order, document in enumerate(documents.values()):
        document["order"] = order
    return documents


def remove_document_artifacts(output_dir: Path, relative_path: str | None) -> None:
    """删除某份 Markdown 及其以文档名开头的本地图片。"""
    if not relative_path:
        return

    document_path = output_dir / relative_path
    try:
        document_path.relative_to(output_dir / "根目录")
    except ValueError:
        print(f"[警告] 忽略输出目录之外的状态路径: {relative_path}")
        return

    if document_path.exists():
        document_path.unlink()

    images_dir = document_path.parent / "images"
    image_prefix = f"{document_path.stem}_"
    if images_dir.is_dir():
        for image_path in images_dir.iterdir():
            if image_path.is_file() and image_path.name.startswith(image_prefix):
                image_path.unlink()
        try:
            images_dir.rmdir()
        except OSError:
            pass

    # 自下而上清除空目录，但永远不移除 output/根目录 本身。
    current = document_path.parent
    output_base = output_dir / "根目录"
    while current != output_base and current.is_dir():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def remove_orphaned_documents(output_dir: Path, known_paths: set[str]) -> list[str]:
    """删除不在本次目录快照或保留状态中的旧 Markdown。

    早期版本在目录/文件改名后可能留下未被状态文件追踪的 Markdown。
    这些文件会在后续优化、建站时被继续复制，形成重复栏目。
    """
    output_base = output_dir / "根目录"
    if not output_base.is_dir():
        return []

    orphaned_paths = sorted(
        document_path.relative_to(output_dir).as_posix()
        for document_path in output_base.rglob("*.md")
        if document_path.relative_to(output_dir).as_posix() not in known_paths
    )
    for relative_path in orphaned_paths:
        remove_document_artifacts(output_dir, relative_path)

    return orphaned_paths


def sync_documents(output_dir: Path, *, full: bool = False) -> dict[str, int]:
    """根据 nodeId + updateTime 增量同步钉钉文档和图片。"""
    prepare_output_directory(output_dir, full=full)
    previous_state = {} if full else load_state(output_dir)

    # 目录遍历必须完整成功，才允许依据本次快照删除本地已消失的文档。
    try:
        current_documents = collect_documents(list_workspace_nodes(WORKSPACE_ID))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, json.JSONDecodeError) as error:
        print(f"[错误] 无法完成目录扫描，未删除本地文件，也未更新状态：{error}")
        stats = {"downloaded": 0, "skipped": 0, "removed": 0, "failed": 1}
        save_report(output_dir, stats, [], str(error))
        return stats

    next_state: dict[str, dict] = {}
    stats = {"downloaded": 0, "skipped": 0, "removed": 0, "failed": 0}
    changes: list[dict] = []

    for node_id, document in current_documents.items():
        old = previous_state.get(node_id, {})
        current_path = document["path"]
        destination = output_dir / current_path
        unchanged = (
            old.get("updateTime") == document.get("updateTime")
            and old.get("path") == current_path
            and old.get("imagesComplete") is not False
            and destination.is_file()
        )

        if unchanged:
            next_state[node_id] = {**old, "order": document.get("order")}
            stats["skipped"] += 1
            print(f"  [未变化] {document['name']}")
            continue

        previous_path = old.get("path")
        previous_content = None
        if previous_path:
            previous_document = output_dir / previous_path
            if previous_document.is_file():
                previous_content = previous_document.read_text(encoding="utf-8")

        destination.parent.mkdir(parents=True, exist_ok=True)
        downloaded_path = download_doc(node_id, document["name"], destination.parent)
        if downloaded_path is None:
            # 保留旧状态，让下次继续尝试本次变更；不要把一次请求失败误判为删除。
            if old:
                next_state[node_id] = old
            stats["failed"] += 1
            change = {
                "status": "读取失败",
                "nodeId": node_id,
                "path": current_path,
                "updateTime": document.get("updateTime"),
            }
            if previous_path:
                change["previousPath"] = previous_path
                change["previousUpdateTime"] = old.get("updateTime")
            changes.append(change)
            print_change(change)
            continue

        # 文档改名、移动或内容更新时，图片需要跟随 Markdown 一并刷新。
        if old.get("path") and old.get("path") != current_path:
            remove_document_artifacts(output_dir, old["path"])
        images_dir = destination.parent / "images"
        image_prefix = f"{destination.stem}_"
        if images_dir.is_dir():
            for image_path in images_dir.iterdir():
                if image_path.is_file() and image_path.name.startswith(image_prefix):
                    image_path.unlink()
        image_stats = download_images_from_markdown(destination, images_dir)
        images_complete = image_stats["failed"] == 0
        next_state[node_id] = {
            "updateTime": document.get("updateTime"),
            "path": current_path,
            "imagesComplete": images_complete,
            "order": document.get("order"),
        }
        stats["downloaded"] += 1
        if not images_complete:
            stats["failed"] += 1

        current_content = destination.read_text(encoding="utf-8")
        if not old:
            change = {
                "status": "新增",
                "nodeId": node_id,
                "path": current_path,
                "updateTime": document.get("updateTime"),
                "lineCount": len(current_content.splitlines()),
                "imagesFailed": image_stats["failed"],
            }
        elif old.get("imagesComplete") is False and old.get("updateTime") == document.get("updateTime") and previous_path == current_path:
            change = {
                "status": "图片重试",
                "nodeId": node_id,
                "path": current_path,
                "updateTime": document.get("updateTime"),
                "imagesFailed": image_stats["failed"],
            }
        else:
            change = {
                "status": "更新" if previous_path == current_path else "移动/改名",
                "nodeId": node_id,
                "path": current_path,
                "previousPath": previous_path,
                "updateTime": document.get("updateTime"),
                "previousUpdateTime": old.get("updateTime"),
                "content": summarize_markdown_changes(previous_content or "", current_content),
                "imagesFailed": image_stats["failed"],
            }
        changes.append(change)
        print_change(change)

    for node_id, old in previous_state.items():
        if node_id not in current_documents:
            remove_document_artifacts(output_dir, old.get("path"))
            stats["removed"] += 1
            change = {
                "status": "删除",
                "nodeId": node_id,
                "path": old.get("path"),
                "previousUpdateTime": old.get("updateTime"),
            }
            changes.append(change)
            print_change(change)

    known_paths = {
        document["path"]
        for document in current_documents.values()
    }
    known_paths.update(
        document["path"]
        for document in next_state.values()
        if isinstance(document.get("path"), str)
    )
    for relative_path in remove_orphaned_documents(output_dir, known_paths):
        stats["removed"] += 1
        change = {"status": "清理残留", "path": relative_path}
        changes.append(change)
        print_change(change)

    save_state(output_dir, next_state)
    save_report(output_dir, stats, changes)
    changelog_review = build_changelog_review(output_dir, current_documents)
    save_changelog_review(output_dir, changelog_review)
    print(
        "\n同步完成："
        f"下载/更新 {stats['downloaded']}，未变化 {stats['skipped']}，"
        f"删除 {stats['removed']}，失败 {stats['failed']}。"
    )
    print(f"变更报告: {report_path(output_dir)}（本次 {len(changes)} 项变更）")
    print_changelog_review(changelog_review)
    print(f"更新日志核对报告: {changelog_review_path(output_dir)}")
    return stats


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从钉钉知识库增量同步文档")
    parser.add_argument(
        "--full",
        action="store_true",
        help="清空本地 output 和状态文件后，从钉钉全量重新抓取。",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    mode = "全量重新抓取" if args.full else "增量同步"
    print(f"开始从钉钉知识库{mode}...")
    print(f"知识库: {WORKSPACE_ID}")
    print(f"排除关键词: {EXCLUDE_KEYWORDS}")
    stats = sync_documents(Path("output"), full=args.full)
    return 1 if stats["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
