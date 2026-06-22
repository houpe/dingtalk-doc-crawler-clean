#!/usr/bin/env python3
"""只下载 markdown 文件中的图片，不重新抓取文档"""
from pathlib import Path
from dws_crawler import download_all_images
import sys

def main():
    print("=" * 60)
    print("开始下载图片（仅下载，不重新抓取文档）")
    print("=" * 60)
    
    output_dir = Path("output")
    if not output_dir.exists():
        print("错误：output 目录不存在")
        sys.exit(1)
    
    # 统计当前状态
    md_files = list(output_dir.rglob("*.md"))
    images_dirs = list(output_dir.rglob("images"))
    
    print(f"找到 {len(md_files)} 个 markdown 文件")
    print(f"已有 {len(images_dirs)} 个 images 目录")
    print()
    
    # 下载图片
    stats = download_all_images(output_dir)
    
    print()
    print("=" * 60)
    print("下载统计：")
    print(f"  成功: {stats['success']}")
    print(f"  失败: {stats['failed']}")
    print(f"  跳过: {stats['skipped']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
