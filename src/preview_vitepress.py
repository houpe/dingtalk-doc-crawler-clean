#!/usr/bin/env python3
"""构建并预览 VitePress 站点（直接从 output_optimized 开始）"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# 动态导入 stage_vitepress 及其依赖
from src.pipeline import stage_vitepress


def main():
    print("准备 VitePress 预览...")
    
    # Stage 3 输出（output_optimized/）没有 "根目录/" 子目录
    # stage_vitepress 期望结构为 source/"根目录"/xxx.md
    # 所以需要创建软链接
    
    src = ROOT / "output_optimized"
    if not src.exists():
        print(f"错误：找不到 {src}")
        print(f"请先运行：python3.10 src/reformat_md.py -s output -o output_optimized")
        sys.exit(1)
    
    # 临时创建 output_optimized/根目录 -> output_optimized 自身的软链接
    link = src / "根目录"
    if not link.exists():
        import os
        os.symlink(".", link, target_is_directory=True)
        print(f"已创建临时软链接：{link.relative_to(ROOT)}")
    
    try:
        print("\n启动 Stage 4：构建 VitePress 站点...")
        result = stage_vitepress(src, serve=True)
        print(f"\n完成！VitePress 正在运行 http://localhost:4000")
    finally:
        # 清理软链接
        if link.exists() and link.is_symlink():
            link.unlink()
            print(f"已清理临时软链接")


if __name__ == "__main__":
    main()
