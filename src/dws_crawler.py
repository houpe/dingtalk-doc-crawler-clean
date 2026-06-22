#!/usr/bin/env python3
"""使用 dws CLI 从钉钉知识库拉取文档"""
import json
import subprocess
import sys
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

EXCLUDE_KEYWORDS = ["日志", "周报", "月报", "记录", "更新", "历史"]
# 精确排除的文件名（不含扩展名）：占位模板文档，含无法解析的示例链接，不应抓取。
EXCLUDE_FILE_NAMES = {"操作说明模板"}
WORKSPACE_ID = "dN0G7JJOWjJ4jmWY"


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
        try:
            data = run_cmd(cmd)
            all_nodes.extend(data.get("nodes", []))
            if not data.get("hasMore", False):
                break
            page_token = data.get("pageToken")
        except subprocess.CalledProcessError as e:
            print(f"  [警告] 列出文件夹 {folder_id} 失败: exit code {e.returncode}")
            break
    return all_nodes


def download_doc(node_id: str, name: str, output_dir: Path) -> bool:
    """下载单个文档"""
    try:
        result = subprocess.run(
            ["dws", "doc", "read", "--node", node_id, "--content-format", "markdown", "--format", "json"],
            capture_output=True, text=True, check=True, timeout=60
        )
        data = json.loads(result.stdout) if result.stdout else {}
        content = data.get("markdown", "")
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"  [错误] {name}: {e}")
        return False
    
    if not content:
        print(f"  [跳过] {name} (内容为空)")
        return False
    
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
    file_path = output_dir / f"{safe_name}.md"
    file_path.write_text(content, encoding='utf-8')
    print(f"  [下载] {name}")
    return True


def process_folder(folder_id: str, folder_name: str, base_dir: Path, depth=0):
    """递归处理文件夹"""
    if should_exclude(folder_name):
        print(f"{'  ' * depth}[排除] 文件夹: {folder_name}")
        return
    
    indent = "  " * depth
    print(f"{indent}[处理] 文件夹: {folder_name}")
    
    # 创建文件夹
    output_dir = base_dir / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 列出文件夹内容
    nodes = list_folder_nodes(folder_id)
    
    for node in nodes:
        node_name = node.get("name", "")
        node_type = node.get("nodeType", "")
        node_id = node.get("nodeId", "")
        
        if should_exclude(node_name):
            print(f"{indent}  [排除] {node_name}")
            continue
        
        if node_type == "folder":
            process_folder(node_id, node_name, output_dir, depth + 1)
        elif node_type == "file" and node.get("extension") == "adoc":
            download_doc(node_id, node_name, output_dir)


def sanitize_filename(filename: str) -> str:
    """清理文件名以符合文件系统要求"""
    # 替换非法字符为下划线
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


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


def main():
    print(f"开始从钉钉知识库拉取文档...")
    print(f"知识库: {WORKSPACE_ID}")
    print(f"排除关键词: {EXCLUDE_KEYWORDS}")
    
    output_dir = Path("output")
    output_base = output_dir / "根目录"
    output_base.mkdir(parents=True, exist_ok=True)
    
    # 列出所有顶层节点
    nodes = list_workspace_nodes(WORKSPACE_ID)
    
    for node in nodes:
        node_name = node.get("name", "")
        node_type = node.get("nodeType", "")
        node_id = node.get("nodeId", "")
        
        if should_exclude(node_name):
            print(f"[排除] {node_name}")
            continue
        
        if node_type == "folder":
            process_folder(node_id, node_name, output_base)
        elif node_type == "file" and node.get("extension") == "adoc":
            download_doc(node_id, node_name, output_base)
    
    print("\n文档拉取完成！")
    
    # 下载所有图片
    download_all_images(output_dir)


if __name__ == "__main__":
    main()