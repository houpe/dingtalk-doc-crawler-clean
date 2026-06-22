#!/usr/bin/env python3
"""
复制图片到 site/docs/ 并按顺序更新 markdown 文件中的远程 URL 为本地路径
"""
import re
import shutil
from pathlib import Path

OUTPUT_DIR = Path("output/根目录")
SITE_DOCS_DIR = Path("site/docs")

# 匹配远程阿里云 OSS 图片 URL
OSS_URL_PATTERN = re.compile(r'https://alidocs2?\.oss-cn-zhangjiakou\.aliyuncs\.com/res/[^)]+')

def copy_images():
    """复制 output/根目录 的图片到 site/docs"""
    print("📸 开始复制图片...")
    copied = 0
    for images_dir in OUTPUT_DIR.rglob("images"):
        if not images_dir.is_dir():
            continue
        rel_path = images_dir.relative_to(OUTPUT_DIR)
        target_dir = SITE_DOCS_DIR / rel_path
        target_dir.mkdir(parents=True, exist_ok=True)
        for img_file in images_dir.iterdir():
            if img_file.is_file() and img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                shutil.copy2(img_file, target_dir / img_file.name)
                copied += 1
    print(f"✅ 复制完成：{copied} 张图片")

def update_markdown_links():
    """更新 markdown 中的远程图片 URL 为本地路径"""
    print("\n📝 开始更新 markdown 图片引用...")
    updated = 0
    total_links = 0
    
    for md_file in OUTPUT_DIR.rglob("*.md"):
        content = md_file.read_text(encoding='utf-8')
        original = content
        
        # 找到所有远程图片 URL
        urls = OSS_URL_PATTERN.findall(content)
        if not urls:
            continue
        
        # 获取该 markdown 对应的 images 目录
        images_dir = md_file.parent / "images"
        if not images_dir.exists():
            print(f"  ⚠️ {md_file.name}: 有 {len(urls)} 个图片 URL 但无 images 目录")
            continue
        
        # 按文件名拼音/数字排序获取本地图片列表
        img_files = sorted([
            f for f in images_dir.iterdir() 
            if f.is_file() and f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        ])
        
        if len(img_files) != len(urls):
            print(f"  ⚠️ {md_file.name}: URL数={len(urls)}, 本地图片数={len(img_files)}")
        
        # 按顺序替换
        for url, local_path in zip(urls, img_files):
            rel_path = f"./images/{local_path.name}"
            # 替换所有出现的这个 URL
            content = content.replace(url, rel_path)
            total_links += 1
        
        if content != original:
            # 保存回 output
            md_file.write_text(content, encoding='utf-8')
            # 同时保存到 site/docs
            rel_path = md_file.relative_to(OUTPUT_DIR)
            site_file = SITE_DOCS_DIR / rel_path
            site_file.parent.mkdir(parents=True, exist_ok=True)
            site_file.write_text(content, encoding='utf-8')
            updated += 1
    
    print(f"✅ 更新完成：{updated} 个文件, {total_links} 个链接")

if __name__ == "__main__":
    # 先清空 site/docs 中的旧数据
    import shutil
    if SITE_DOCS_DIR.exists():
        shutil.rmtree(SITE_DOCS_DIR)
    SITE_DOCS_DIR.mkdir(parents=True)
    
    # 复制 markdown 文件
    print("📄 复制 markdown 文件...")
    for md_file in OUTPUT_DIR.rglob("*.md"):
        rel_path = md_file.relative_to(OUTPUT_DIR)
        target = SITE_DOCS_DIR / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(md_file, target)
    
    copy_images()
    update_markdown_links()
    print("\n🎉 完成！")
