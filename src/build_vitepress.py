#!/usr/bin/env python3
"""从 output_optimized 生成 VitePress 站点并启动预览"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output_optimized"
SITE_DIR = ROOT / "site"
DOCS_DIR = SITE_DIR / "docs"
VP_DIR = DOCS_DIR / ".vitepress"

INDEX_MD = """---
layout: home
hero:
  name: "中通冷链操作手册"
  tagline: 系统操作指南与网点帮助中心
  actions:
    - theme: brand
      text: 开始阅读
      link: /一、网点操作/02客户下单篇/关于客户自主下单，网点必知
    - theme: alt
      text: 必知必读
      link: /「*必知必读」账号权限如何开通？/系统如何访问？APP如何下载？
features:
  - title: 必知必读
    details: 账号权限开通、系统访问方式等基础准备
  - title: 网点操作
    details: 客户下单、运单管理、品控、财务结算等网点日常操作
  - title: 中心操作
    details: 司机操作、调度、PDA扫描、小程序等中心流程
  - title: 云仓操作
    details: WMS仓储管理、入库出库、盘点、仓库实施等
---
"""


def clean_docs():
    """清理旧的 docs 目录"""
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True)
    VP_DIR.mkdir(parents=True)


def copy_content():
    """将 output_optimized 复制到 docs/"""
    for item in (OUTPUT_DIR / "根目录").iterdir():
        dst = DOCS_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)

    (DOCS_DIR / "index.md").write_text(INDEX_MD, encoding="utf-8")


def md_files_in_dir(d: Path) -> list[str]:
    """递归获取目录下所有 md 文件的相对路径（不含扩展名），排序"""
    files = []
    for f in sorted(d.rglob("*.md")):
        if f.name == "index.md":
            continue
        rel = f.relative_to(DOCS_DIR)
        files.append(str(rel.with_suffix("")))
    return files


def build_sidebar_section(folder: Path, base_path: str) -> list[dict]:
    """构建单个文件夹（一级章节）的侧边栏条目"""
    items = []
    subdirs = sorted([p for p in folder.iterdir() if p.is_dir()])
    md_files = sorted([f for f in folder.iterdir() if f.is_file() and f.suffix == ".md"])

    # 先加文件，再加子目录
    for f in md_files:
        name = f.stem
        link = f"{base_path}/{f.stem}"
        items.append({"text": name, "link": link})

    for d in subdirs:
        sub_base = f"{base_path}/{d.name}"
        section = {
            "text": d.name,
            "collapsed": True,
            "items": []
        }
        for f in sorted(d.rglob("*.md")):
            rel = f.relative_to(DOCS_DIR)
            link = str(rel.with_suffix(""))
            section["items"].append({"text": f.stem, "link": link})
        if section["items"]:
            items.append(section)

    return items


def build_sidebar() -> list[dict]:
    """构建完整侧边栏"""
    sidebar = []
    for folder in sorted([p for p in DOCS_DIR.iterdir() if p.is_dir()]):
        base_path = str(folder.relative_to(DOCS_DIR))
        section = {
            "text": folder.name,
            "collapsed": True,
            "items": build_sidebar_section(folder, base_path)
        }
        sidebar.append(section)
    return sidebar


def write_config(sidebar: list[dict]):
    """写入 VitePress 配置（Pinia 风格主题）"""
    config = '''import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '中通冷链操作手册',
  description: '系统操作指南与网点帮助中心',
  lang: 'zh-CN',

  themeConfig: {
    logo: '/favicon.png',
    nav: [
      { text: '首页', link: '/' },
      { text: '网点操作', link: '/一、网点操作/02客户下单篇/关于客户自主下单，网点必知' },
      { text: '中心操作', link: '/二、中心操作/01司机操作篇/到达中心如何进行靠台操作？' },
      { text: '云仓操作', link: '/三、云仓操作/BMS操作/01 基础资料篇/1. 创建仓库、货主、员工、' },
    ],

    sidebar: ''' + json.dumps(sidebar, ensure_ascii=False, indent=6) + ''',

    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索文档', buttonAriaLabel: '搜索文档' },
          modal: {
            noResultsText: '无法找到相关结果',
            resetButtonTitle: '清除查询条件',
            footer: { selectText: '选择', navigateText: '切换' },
          },
        },
      },
    },

    outline: {
      level: [2, 3],
      label: '页面导航',
    },

    lastUpdated: { text: '最后更新于' },

    docFooter: {
      prev: '上一篇',
      next: '下一篇',
    },

    footer: {
      message: '中通冷链系统操作手册',
    },

    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '菜单',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
  },
})
'''
    (VP_DIR / "config.mts").write_text(config, encoding="utf-8")


def write_style():
    """写入 Pinia 风格的自定义样式"""
    css = """/* Pinia 风格主题色 */
:root {
  --vp-c-brand-1: #42b883;
  --vp-c-brand-2: #33a06f;
  --vp-c-brand-3: #42b883;
  --vp-c-brand-soft: rgba(66, 184, 131, 0.14);
  --vp-c-brand-1: #42b883;
  --vp-home-hero-name-color: transparent;
  --vp-home-hero-name-background: -webkit-linear-gradient(
    120deg,
    #42b883 30%,
    #35495e
  );
  --vp-home-hero-image-background-image: linear-gradient(
    -45deg,
    #42b88380 30%,
    #35495e80
  );
  --vp-home-hero-image-filter: blur(44px);
}

@media (min-width: 640px) {
  :root {
    --vp-home-hero-image-filter: blur(56px);
  }
}

@media (min-width: 960px) {
  :root {
    --vp-home-hero-image-filter: blur(68px);
  }
}

.dark {
  --vp-c-brand-1: #42b883;
  --vp-c-brand-2: #33a06f;
  --vp-c-brand-3: #42b883;
  --vp-c-brand-soft: rgba(66, 184, 131, 0.16);
}

/* Feature cards */
:root {
  --vp-feature-icon-color: var(--vp-c-brand-1);
}

/* 侧边栏当前项高亮 */
.VPSidebarItem.is-active > .item .link {
  color: var(--vp-c-brand-1) !important;
}

/* 链接颜色 */
.vp-doc a {
  color: var(--vp-c-brand-1);
}

.vp-doc a:hover {
  color: var(--vp-c-brand-2);
}
"""
    theme_dir = VP_DIR / "theme"
    theme_dir.mkdir(exist_ok=True)
    (theme_dir / "custom.css").write_text(css, encoding="utf-8")
    (theme_dir / "index.ts").write_text(
        'import DefaultTheme from "vitepress/theme"\nimport "./custom.css"\n\nexport default DefaultTheme\n',
        encoding="utf-8"
    )


def copy_assets():
    """复制 favicon"""
    public_dir = DOCS_DIR / "public"
    public_dir.mkdir(exist_ok=True)
    favicon = ROOT / "assets" / "favicon.png"
    if favicon.exists():
        shutil.copy2(favicon, public_dir / "favicon.png")


def main():
    print("=" * 50)
    print("  构建 VitePress 站点（Pinia 风格）")
    print("=" * 50)

    if not OUTPUT_DIR.exists():
        print(f"错误：找不到 {OUTPUT_DIR}")
        print("请先运行：python3.10 src/reformat_md.py -s output -o output_optimized")
        sys.exit(1)

    print("\n[1/5] 清理旧文件...")
    clean_docs()

    print("[2/5] 复制文档...")
    copy_content()

    print("[3/5] 生成侧边栏...")
    sidebar = build_sidebar()
    write_config(sidebar)

    print("[4/5] 写入主题样式...")
    write_style()
    copy_assets()

    count = sum(1 for _ in DOCS_DIR.rglob("*.md")) - 1
    print(f"[5/5] 共 {count} 篇文档")
    print(f"\n站点准备完成！运行：")
    print(f"  cd site && npx vitepress dev docs --port 4000")


if __name__ == "__main__":
    main()
