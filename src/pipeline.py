#!/usr/bin/env python3
"""
钉钉文档一条龙 Pipeline
Stage 1: 抓取 → Stage 2: 过滤 → Stage 3: 优化 → Stage 4: VitePress 构建

Usage:
    python3 pipeline.py <url>                        # 全量一条龙
    python3 pipeline.py --source ./output            # 从已有 MD 开始
    python3 pipeline.py --source ./output --no-ai    # 跳过 AI 优化
    python3 pipeline.py --source ./output --deploy full  # 部署到服务器
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
SITE_DIR = ROOT / "site"
DEPLOY_HOST = os.environ.get("DEPLOY_HOST", "root@42.192.205.206")
DEPLOY_PATH = os.environ.get("DEPLOY_PATH", "/zto")

EXCLUDE_KEYWORDS = ["日志", "周报", "月报", "记录", "更新", "历史"]

# 精确排除的文件名（不含扩展名）。这些是占位/模板文档，含无法解析的示例链接，
# 不应进入站点。用精确匹配避免误伤业务文档。
EXCLUDE_FILE_NAMES = {"操作说明模板"}


# ── 输出工具 ────────────────────────────────────────────────────

def banner(stage: str) -> None:
    print(f"\n{'═' * 60}")
    print(f"  {stage}")
    print(f"{'═' * 60}\n")


def summary_line(label: str, value: str) -> None:
    print(f"  {label}: {value}")


def divider() -> None:
    print(f"  {'─' * 56}")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kwargs)


def run_capture(cmd: list[str], **kwargs) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, check=True, **kwargs)
    return r.stdout


def fmt_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(seconds, 60)
    return f"{int(m)}m{s:.0f}s"


# ── Stage 1: 抓取钉钉文档 ──────────────────────────────────────

def stage_crawl(url: str, output_dir: Path) -> dict:
    banner("Stage 1/4: 抓取钉钉文档")
    t0 = time.time()

    if output_dir.exists():
        print(f"  清理旧输出: {output_dir}")
        shutil.rmtree(output_dir)

    print(f"  抓取 URL: {url}")
    print()
    run([sys.executable, str(ROOT / "src" / "crawler.py"), url, "-o", str(output_dir)])

    elapsed = time.time() - t0

    root_dir = output_dir / "根目录"
    md_files = list(root_dir.rglob("*.md")) if root_dir.exists() else []
    img_files = list(root_dir.rglob("images/*")) if root_dir.exists() else []
    dirs = [d for d in (root_dir.rglob("*")) if d.is_dir() and d.name != "images"]

    divider()
    summary_line("文档总数", str(len(md_files)))
    summary_line("文件夹数", str(len(dirs)))
    summary_line("图片数", f"{len(img_files)} 张")
    summary_line("耗时", fmt_time(elapsed))

    return {"md_count": len(md_files), "img_count": len(img_files), "elapsed": elapsed}


# ── Stage 2: 过滤排除文档 ──────────────────────────────────────

def stage_filter(output_dir: Path, extra_keywords: list[str] | None = None) -> dict:
    banner("Stage 2/4: 过滤排除文档")
    t0 = time.time()

    keywords = EXCLUDE_KEYWORDS[:]
    if extra_keywords:
        keywords.extend(extra_keywords)

    print(f"  排除关键字: {' | '.join(keywords)}")
    print()

    root_dir = output_dir / "根目录"
    if not root_dir.exists():
        print("  无根目录，跳过过滤")
        return {"excluded": 0, "kept": 0, "elapsed": 0}

    pattern = re.compile("|".join(re.escape(kw) for kw in keywords))

    excluded_files: list[tuple[str, str]] = []

    for md_file in sorted(root_dir.rglob("*.md")):
        title = md_file.stem
        reason = None
        m = pattern.search(title)
        if m:
            reason = m.group()
        elif title in EXCLUDE_FILE_NAMES:
            reason = "占位模板"
        if reason:
            rel = md_file.relative_to(root_dir)
            excluded_files.append((str(rel), reason))
            md_file.unlink(missing_ok=True)

    for rel_path, kw in excluded_files:
        print(f"  [排除] {rel_path} (命中: {kw})")

    _cleanup_empty_dirs(root_dir)

    remaining = list(root_dir.rglob("*.md"))
    elapsed = time.time() - t0

    divider()
    summary_line("排除", f"{len(excluded_files)} 个")
    summary_line("保留", f"{len(remaining)} 个")
    summary_line("耗时", fmt_time(elapsed))

    return {"excluded": len(excluded_files), "kept": len(remaining), "elapsed": elapsed}


def _cleanup_empty_dirs(root: Path) -> None:
    changed = True
    while changed:
        changed = False
        for d in sorted(root.rglob("*"), reverse=True):
            if not d.is_dir() or d.name == "images":
                continue
            has_content = any(
                child.is_file() and child.suffix == ".md"
                for child in d.rglob("*")
            )
            if not has_content:
                shutil.rmtree(d, ignore_errors=True)
                changed = True


# ── Stage 3: Markdown 优化 ─────────────────────────────────────

def stage_optimize(output_dir: Path, use_ai: bool = False, model: str = "deepseek-chat") -> tuple[Path, dict]:
    banner("Stage 3/4: Markdown 优化")
    t0 = time.time()

    if use_ai:
        reformatted = ROOT / "output_reformatted"
        if reformatted.exists():
            shutil.rmtree(reformatted)
        rule_output = reformatted
    else:
        rule_output = ROOT / "output_optimized"

    if rule_output.exists() and rule_output.resolve() != output_dir.resolve():
        shutil.rmtree(rule_output)

    print("  [规则引擎] 开始处理...")
    run([sys.executable, str(ROOT / "src" / "reformat_md.py"),
         "-s", str(output_dir), "-o", str(rule_output)])
    rule_count = len(list(rule_output.rglob("*.md")))
    rule_time = time.time() - t0
    print(f"  [规则引擎] 处理 {rule_count} 个文件 ✓ {fmt_time(rule_time)}")

    if not use_ai:
        elapsed = time.time() - t0
        divider()
        summary_line("规则引擎", f"{rule_count} 个 ✓ {fmt_time(rule_time)}")
        summary_line("AI 优化", "已跳过（加 --use-ai 启用）")
        summary_line("耗时", fmt_time(elapsed))
        return rule_output, {"rule_count": rule_count, "ai_success": 0, "ai_fail": 0, "elapsed": elapsed}

    print(f"\n  [DeepSeek AI] 模型: {model}")
    optimized = ROOT / "output_optimized"
    if optimized.exists():
        shutil.rmtree(optimized)

    ai_t0 = time.time()
    md_files = _discover_md(reformatted)
    total = len(md_files)
    failed: list[str] = []

    sys.path.insert(0, str(ROOT / "src"))
    from optimize_md_deepseek import optimize as ai_optimize

    for idx, src in enumerate(md_files, 1):
        rel = src.relative_to(reformatted)
        dst = optimized / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        md_text = src.read_text(encoding="utf-8", errors="ignore")
        if len(md_text.strip()) < 10:
            dst.write_text(md_text, encoding="utf-8")
            print(f"    [{idx}/{total}] {rel} (空文件，跳过)")
            continue

        file_t0 = time.time()
        ok = False
        for attempt in range(1, 4):
            try:
                result = ai_optimize(md_text, model=model)
                dst.write_text(result, encoding="utf-8")
                ok = True
                break
            except Exception as e:
                if attempt == 3:
                    failed.append(str(rel))
                    dst.write_text(md_text, encoding="utf-8")
                    print(f"    [{idx}/{total}] {rel} FAILED (retry 3/3): {e}")
                else:
                    time.sleep(2)

        if ok:
            dt = time.time() - file_t0
            print(f"    [{idx}/{total}] {rel} ✓ {dt:.1f}s")

    _copy_images(reformatted, optimized)

    ai_time = time.time() - ai_t0
    elapsed = time.time() - t0
    ai_success = total - len(failed)

    divider()
    summary_line("规则引擎", f"{rule_count} 个 ✓ {fmt_time(rule_time)}")
    summary_line("AI 优化", f"{ai_success}/{total} 成功, {len(failed)} 失败, {fmt_time(ai_time)}")
    if failed:
        print(f"  失败文件: {failed}")
    summary_line("耗时", fmt_time(elapsed))

    return optimized, {
        "rule_count": rule_count,
        "ai_success": ai_success,
        "ai_fail": len(failed),
        "failed_files": failed,
        "elapsed": elapsed,
    }


def _discover_md(root: Path) -> list[Path]:
    exclude = {".git", "__pycache__", "node_modules", "images", "skills", "docs"}
    found: list[Path] = []

    def walk(d: Path) -> None:
        for child in sorted(d.iterdir()):
            if child.name in exclude:
                continue
            if child.is_dir():
                walk(child)
            elif child.suffix.lower() == ".md":
                found.append(child)

    walk(root)
    return found


def _copy_images(src_dir: Path, dst_dir: Path) -> None:
    for img_dir in src_dir.rglob("images"):
        if img_dir.is_dir():
            rel = img_dir.relative_to(src_dir)
            dst = dst_dir / rel
            if not dst.exists():
                shutil.copytree(img_dir, dst)


# ── Stage 4: VitePress 构建 ───────────────────────────────────

VP_CONFIG_MTS = """import { defineConfig } from 'vitepress'
import sidebar from './sidebar-data.mjs'

export default defineConfig({
  ignoreDeadLinks: true,
  lang: 'zh-CN',
  title: '中通冷链',
  description: '中通冷链操作手册',
  cleanUrls: true,
  lastUpdated: true,

  head: [['link', { rel: 'icon', type: 'image/png', href: '/favicon.png' }]],

  themeConfig: {
    logo: '/favicon.png',

    nav: [
      { text: '操作手册', link: '/guide/' },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/houpe/dingtalk-doc-crawler' },
    ],

    sidebar: sidebar,

    footer: {
      message: '中通冷链操作手册',
      copyright: `Copyright © ${new Date().getFullYear()} 中通冷链`,
    },

    search: {
      provider: 'local',
      options: { locales: { root: { translations: { button: { buttonText: '搜索文档' } } } } },
    },

    outline: { label: '本页目录', level: [2, 4] },

    docFooter: { prev: '上一篇', next: '下一篇' },

    lastUpdated: { text: '最后更新于' },

    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '菜单',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
  },
})
"""

VP_STYLE_CSS = """:root {
  --vp-c-brand-1: #3eaf7c;
  --vp-c-brand-2: #3aa876;
  --vp-c-brand-3: #2e8a5f;
  --vp-c-brand-soft: rgba(62, 175, 124, 0.14);
  --vp-button-brand-border: transparent;
  --vp-button-brand-text: #fff;
  --vp-button-brand-bg: #3eaf7c;
  --vp-button-brand-hover-border: transparent;
  --vp-button-brand-hover-text: #fff;
  --vp-button-brand-hover-bg: #3aa876;
  --vp-button-brand-active-border: transparent;
  --vp-button-brand-active-text: #fff;
  --vp-button-brand-active-bg: #2e8a5f;
}

:root.dark {
  --vp-c-brand-1: #4dd895;
  --vp-c-brand-2: #3eaf7c;
  --vp-c-brand-3: #3aa876;
  --vp-c-brand-soft: rgba(77, 216, 149, 0.14);
}

.VPHero .name {
  color: var(--vp-c-brand-1) !important;
}

.VPFeature {
  border-radius: 12px;
  border: 1px solid var(--vp-c-divider);
  transition: border-color 0.25s, box-shadow 0.25s;
}

.VPFeature:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 0 0 1px var(--vp-c-brand-soft);
}

.VPSidebarItem .text {
  font-size: 14px;
}

.vp-edit-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 100;
  padding: 10px 20px;
  border-radius: 999px;
  background: var(--vp-c-brand-1);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  box-shadow: 0 4px 16px rgba(62,175,124,0.35);
  transition: transform 0.15s, box-shadow 0.15s;
  line-height: 1;
}
.vp-edit-fab:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(62,175,124,0.5);
}

.medium-zoom-overlay {
  z-index: 30;
}

.medium-zoom-overlay,
.medium-zoom-image--opened {
  z-index: 30;
}
"""

VP_INDEX_MD = """---
layout: home

hero:
  name: 中通冷链
  text: 操作手册
  tagline: 覆盖网点、中心、云仓、网络货运全链路业务操作
  image:
    src: /home-hero.png
    alt: 中通冷链
  actions:
    - theme: brand
      text: 开始阅读
      link: /网点操作/
    - theme: alt
      text: 账号权限
      link: /「必知必读」账号权限如何开通？/

features:
  - icon: 📌
    title: 必知必读
    details: 账号权限开通、系统访问方式、APP 下载等基础准备。
    link: /「必知必读」账号权限如何开通？/
    linkText: 查看文档
  - icon: 🏠
    title: 网点操作
    details: 客户下单、运单管理、品控质量、结算财务、考核相关、物料购买等全流程操作指南。
    link: /网点操作/
    linkText: 查看文档
  - icon: 🏢
    title: 中心操作
    details: 司机接单发车、调度任务管理、PDA 扫描操作、小程序使用、数据统计看板。
    link: /中心操作/
    linkText: 查看文档
  - icon: 📦
    title: 云仓操作
    details: WMS/OMS/BMS 仓储管理、出入库作业、基础资料配置、规则策略等。
    link: /云仓操作/
    linkText: 查看文档
  - icon: 🚛
    title: 网络货运
    details: 网络货运货主注册、操作说明等。
    link: /网络货运/
    linkText: 查看文档
---
"""


# ── Server (Express 后端 + API) ─────────────────────────────────

SERVER_JS = r"""
import { readFileSync, writeFileSync } from 'fs';
import { resolve, join } from 'path';
import { spawn } from 'child_process';
import express from 'express';
import jwt from 'jsonwebtoken';

const DOCS_DIR = join(process.cwd(), 'docs');
const DIST_DIR = join(DOCS_DIR, '.vitepress/dist');
const JWT_SECRET = process.env.JWT_SECRET || 'zto-doc-secret-change-me';
const PORT = parseInt(process.env.PORT || '4000');
const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.ADMIN_PASS || 'admin123';

function getCookie(req, name) {
  const c = (req.headers.cookie || '').split('; ').find(r => r.startsWith(name + '='));
  return c ? c.split('=')[1] : null;
}

function requireAuth(req, res, next) {
  const token = getCookie(req, 'jwt');
  if (!token) return res.status(401).json({ error: '未登录' });
  try { req.user = jwt.verify(token, JWT_SECRET); next(); }
  catch { res.status(401).json({ error: '登录过期' }); }
}

function safeDocPath(p) {
  if (!p || typeof p !== 'string') return null;
  const full = resolve(DOCS_DIR, (p || '').replace(/\.md$/, '') + '.md');
  if (!full.startsWith(DOCS_DIR + '/') && !full.startsWith(DOCS_DIR + '\\')) return null;
  return full;
}

const app = express();
app.use(express.json({ limit: '10mb' }));
app.use(express.static(DIST_DIR, { index: false }));

app.use('*', (req, res, next) => {
  if (req.url.startsWith('/api/')) return next();
  res.sendFile(join(DIST_DIR, 'index.html'));
});

app.get('/api/auth/check', (req, res) => {
  const token = getCookie(req, 'jwt');
  if (!token) return res.json({ loggedIn: false });
  try { const u = jwt.verify(token, JWT_SECRET); res.json({ loggedIn: true, user: u.username }); }
  catch { res.json({ loggedIn: false }); }
});

app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (username === ADMIN_USER && password === ADMIN_PASS) {
    const token = jwt.sign({ username }, JWT_SECRET, { expiresIn: '4h' });
    res.cookie('jwt', token, { httpOnly: true, maxAge: 14400000, sameSite: 'lax' });
    res.json({ ok: true });
  } else res.status(401).json({ error: '用户名或密码错误' });
});

app.post('/api/logout', (req, res) => { res.clearCookie('jwt'); res.json({ ok: true }); });

app.get('/api/docs/:path(*)', requireAuth, (req, res) => {
  const fp = safeDocPath(req.params.path);
  if (!fp) return res.status(403).json({ error: '非法路径' });
  try { res.json({ content: readFileSync(fp, 'utf-8'), path: req.params.path }); }
  catch { res.status(404).json({ error: '文件不存在' }); }
});

app.put('/api/docs/:path(*)', requireAuth, (req, res) => {
  const fp = safeDocPath(req.params.path);
  if (!fp) return res.status(403).json({ error: '非法路径' });
  if (!req.body.content) return res.status(400).json({ error: '内容为空' });
  const rel = req.params.path.replace(/\.md$/, '') + '.md';
  if (!rel.startsWith('guide/')) return res.status(403).json({ error: '路径非法' });
  try { writeFileSync(fp, req.body.content, 'utf-8'); res.json({ ok: true, path: rel }); }
  catch (e) { res.status(500).json({ error: '保存失败: ' + e.message }); }
});

app.post('/api/build', requireAuth, (req, res) => {
  res.json({ ok: true, message: '构建已启动' });
  const child = spawn('npx', ['vitepress', 'build', 'docs'], {
    cwd: process.cwd(), stdio: 'pipe', env: { ...process.env },
  });
  child.stdout.on('data', d => console.log('[build]', String(d).trim()));
  child.stderr.on('data', d => console.error('[build]', String(d).trim()));
  child.on('close', code => console.log('[build] exit code:', code));
});

app.listen(PORT, () => {
  console.log('\n   中通冷链文档 - http://localhost:' + PORT);
  console.log('   编辑入口: http://localhost:' + PORT + '/edit.html');
  console.log('   登录账号:', ADMIN_USER);
  console.log('\n  Ctrl+C 停止\n');
});
"""


# ── 独立编辑页 (Monaco Editor + Live Preview) ──────────────────

EDIT_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>文档编辑 - 中通冷链</title>
<link rel="icon" type="image/png" href="/favicon.png">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--green:#3eaf7c;--green-dark:#2e8a5f;--bg:#0f172a;--card:#1e293b;--text:#e2e8f0;--muted:#94a3b8;--border:#334155;--danger:#ef4444}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;background:var(--bg);color:var(--text);height:100vh;overflow:hidden}
a{color:var(--green)}
#login-view{display:flex;align-items:center;justify-content:center;height:100vh}
.login-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:48px 40px;width:400px;text-align:center}
.login-card .logo{font-size:40px;margin-bottom:16px;display:block}
.login-card h2{font-size:22px;margin-bottom:4px}
.login-card .sub{color:var(--muted);font-size:14px;margin-bottom:32px}
.login-card input{width:100%;padding:12px 16px;border:1px solid var(--border);border-radius:10px;background:var(--bg);color:var(--text);font-size:15px;margin-bottom:16px;outline:none;transition:border-color .2s}
.login-card input:focus{border-color:var(--green)}
.login-card button{width:100%;padding:12px;background:var(--green);border:none;border-radius:10px;color:#fff;font-size:15px;font-weight:600;cursor:pointer;transition:background .2s}
.login-card button:hover{background:var(--green-dark)}
.login-card .err{color:var(--danger);font-size:13px;margin-top:12px;min-height:20px}
#editor-view{display:none;flex-direction:column;height:100vh}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:10px 20px;background:var(--card);border-bottom:1px solid var(--border)}
.topbar .file-path{font-size:14px;color:var(--muted);font-family:monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:50%}
.topbar .actions{display:flex;gap:8px;align-items:center}
.topbar .user-tag{font-size:13px;color:var(--green);margin-right:8px}
.btn{padding:8px 18px;border:1px solid var(--border);border-radius:8px;background:transparent;color:var(--text);font-size:13px;cursor:pointer;transition:all .2s;white-space:nowrap}
.btn:hover{border-color:var(--green);color:var(--green)}
.btn.primary{background:var(--green);border-color:var(--green);color:#fff}
.btn.primary:hover{background:var(--green-dark);border-color:var(--green-dark);color:#fff}
.btn.danger:hover{border-color:var(--danger);color:var(--danger)}
.btn:disabled{opacity:.5;cursor:not-allowed}
.split{flex:1;display:flex;overflow:hidden}
.editor-pane{flex:1;border-right:1px solid var(--border);position:relative}
.preview-pane{flex:1;overflow-y:auto;padding:24px 32px;background:#fff;color:#1a1a1a}
.preview-pane h1{font-size:28px;margin:16px 0 12px;letter-spacing:-.02em}
.preview-pane h2{font-size:22px;margin:20px 0 10px;border-bottom:1px solid #e5e7eb;padding-bottom:6px}
.preview-pane h3{font-size:18px;margin:16px 0 8px}
.preview-pane h4{font-size:16px;margin:14px 0 6px}
.preview-pane p{line-height:1.7;margin:8px 0;font-size:15px}
.preview-pane ul{padding-left:24px;margin:8px 0}
.preview-pane li{line-height:1.8}
.preview-pane table{border-collapse:collapse;width:100%;margin:12px 0}
.preview-pane th,.preview-pane td{border:1px solid #e5e7eb;padding:8px 12px;font-size:14px}
.preview-pane th{background:#f9fafb;font-weight:600}
.preview-pane blockquote{border-left:4px solid var(--green);padding:8px 16px;margin:12px 0;color:#64748b;background:#f8fafc;border-radius:4px}
.preview-pane code{background:#f1f5f9;padding:2px 6px;border-radius:4px;font-size:13px}
.preview-pane pre{background:#1e293b;color:#e2e8f0;padding:16px;border-radius:8px;overflow-x:auto;margin:12px 0}
.preview-pane pre code{background:none;padding:0;color:inherit}
.preview-pane img{max-width:100%;border-radius:8px;margin:12px 0}
.preview-pane hr{border:none;border-top:1px solid #e5e7eb;margin:20px 0}
.status-bar{padding:10px 20px;background:#1e293b;border-top:1px solid var(--border);display:none;flex-direction:column;max-height:200px;overflow-y:auto}
.status-bar .row{display:flex;align-items:center;gap:8px;font-size:13px}
.status-bar .dot{width:8px;height:8px;border-radius:50%;background:#eab308;animation:pulse 1s infinite}
.status-bar .dot.done{background:var(--green);animation:none}
.status-bar .dot.fail{background:var(--danger);animation:none}
.status-bar pre{font-size:12px;color:var(--muted);font-family:monospace;white-space:pre-wrap;margin-top:6px;max-height:120px;overflow-y:auto}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
@media(max-width:768px){.split{flex-direction:column}.preview-pane{display:none}}
</style>
</head>
<body>
<div id="login-view">
  <form class="login-card" onsubmit="doLogin(event)">
    <span class="logo">🍍</span>
    <h2>中通冷链 · 文档编辑</h2>
    <p class="sub">需要登录后才能编辑文档</p>
    <input id="inp-user" type="text" placeholder="用户名" autocomplete="username" autofocus>
    <input id="inp-pass" type="password" placeholder="密码" autocomplete="current-password">
    <button type="submit">登 录</button>
    <div id="login-err" class="err"></div>
  </form>
</div>
<div id="editor-view">
  <div class="topbar">
    <span id="file-path" class="file-path"></span>
    <div class="actions">
      <span id="user-tag" class="user-tag"></span>
      <button id="btn-save" class="btn primary" onclick="saveDoc()">保存</button>
      <button id="btn-build" class="btn" onclick="triggerBuild()">构建</button>
      <button class="btn danger" onclick="doLogout()">退出</button>
    </div>
  </div>
  <div class="split">
    <div class="editor-pane" id="editor-container"></div>
    <div class="preview-pane" id="preview-pane"></div>
  </div>
  <div id="status-bar" class="status-bar">
    <div class="row"><span id="status-dot" class="dot"></span><span id="status-text">构建中...</span></div>
    <pre id="status-log"></pre>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs/loader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
let editor = null;
let currentPath = '';
let saveTimer = null;

async function checkAuth() {
  try { const r = await fetch('/api/auth/check'); const d = await r.json(); return d.loggedIn; } catch { return false; }
}

async function doLogin(e) {
  e.preventDefault();
  const errEl = document.getElementById('login-err');
  errEl.textContent = '';
  const username = document.getElementById('inp-user').value.trim();
  const password = document.getElementById('inp-pass').value;
  if (!username || !password) { errEl.textContent = '请输入用户名和密码'; return; }
  try {
    const r = await fetch('/api/login', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({username, password}) });
    const d = await r.json();
    if (!r.ok) { errEl.textContent = d.error || '登录失败'; return; }
    showEditor();
  } catch (e) { errEl.textContent = '网络错误: ' + e.message; }
}

async function doLogout() {
  await fetch('/api/logout', { method: 'POST' });
  location.reload();
}

function showLoginView() {
  document.getElementById('login-view').style.display = 'flex';
  document.getElementById('editor-view').style.display = 'none';
}

async function showEditor() {
  document.getElementById('login-view').style.display = 'none';
  document.getElementById('editor-view').style.display = 'flex';
  const r = await fetch('/api/auth/check');
  const d = await r.json();
  if (d.user) document.getElementById('user-tag').textContent = '👤 ' + d.user;
  currentPath = new URLSearchParams(location.search).get('path') || '';
  document.getElementById('file-path').textContent = currentPath ? currentPath + '.md' : '';
  if (currentPath) loadDoc();
}

async function loadDoc() {
  if (!currentPath) return;
  const r = await fetch('/api/docs/' + currentPath);
  if (!r.ok) { if (r.status === 401) { showLoginView(); return; } return; }
  const d = await r.json();
  initEditor(d.content);
  renderPreview(d.content);
}

async function saveDoc() {
  if (!currentPath || !editor) return;
  const btn = document.getElementById('btn-save');
  btn.disabled = true; btn.textContent = '保存中...';
  try {
    const r = await fetch('/api/docs/' + currentPath, {
      method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ content: editor.getValue() }),
    });
    if (!r.ok) { alert('保存失败: ' + (await r.json()).error); return; }
    btn.textContent = '已保存 ✓';
    setTimeout(() => btn.textContent = '保存', 2000);
  } catch (e) { alert('保存失败: ' + e.message); }
  finally { btn.disabled = false; }
}

async function triggerBuild() {
  const btn = document.getElementById('btn-build');
  btn.disabled = true; btn.textContent = '构建中...';
  const bar = document.getElementById('status-bar');
  const dot = document.getElementById('status-dot');
  const txt = document.getElementById('status-text');
  bar.style.display = 'flex';
  dot.className = 'dot'; txt.textContent = '构建中...';
  try {
    const r = await fetch('/api/build', { method: 'POST' });
    if (!r.ok) { txt.textContent = '构建启动失败'; dot.className = 'dot fail'; return; }
    await new Promise(rs => setTimeout(rs, 30000));
    txt.textContent = '构建完成 ✓'; dot.className = 'dot done';
  } catch (e) { txt.textContent = '错误: ' + e.message; dot.className = 'dot fail'; }
  finally { btn.disabled = false; btn.textContent = '构建'; }
}

function initEditor(content) {
  if (editor) { try { editor.dispose(); } catch {} editor = null; }
  const container = document.getElementById('editor-container');
  container.innerHTML = '';
  require.config({ paths: { 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs' } });
  require(['vs/editor/editor.main'], function () {
    monaco.editor.defineTheme('dark-soft', {
      base: 'vs-dark', inherit: true, rules: [],
      colors: { 'editor.background': '#0f172a', 'editor.foreground': '#e2e8f0', 'editorLineNumber.foreground': '#475569' },
    });
    editor = monaco.editor.create(container, {
      value: content, language: 'markdown', theme: 'dark-soft',
      wordWrap: 'on', automaticLayout: true, minimap: { enabled: false },
      fontSize: 14, lineHeight: 22, scrollBeyondLastLine: false,
      tabSize: 2, padding: { top: 16, bottom: 16 },
      smoothScrolling: true, cursorBlinking: 'smooth',
    });
    editor.onDidChangeModelContent(() => {
      clearTimeout(saveTimer);
      saveTimer = setTimeout(() => renderPreview(editor.getValue()), 300);
    });
  });
}

function renderPreview(md) {
  document.getElementById('preview-pane').innerHTML = marked.parse(md || '');
}

(function init() {
  checkAuth().then(async ok => {
    if (!ok) { showLoginView(); return; }
    currentPath = new URLSearchParams(location.search).get('path') || '';
    if (currentPath) { showEditor(); } else { showEditor(); }
   });
})();
</script>
</body>
</html>"""


# ── 主题编辑按钮注入 ────────────────────────────────────────────

THEME_JS_TPL = r"""import DefaultTheme from "vitepress/theme"
import { onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vitepress'
import mediumZoom from 'medium-zoom'
import "./style.css"

export default {
  extends: DefaultTheme,
  setup() {
    const route = useRoute()
    const initZoom = () => {
      mediumZoom('.main img', {
        background: 'rgba(0, 0, 0, 0.85)',
      })
    }
    onMounted(() => {
      initZoom()
    })
    watch(
      () => route.path,
      () => nextTick(() => initZoom())
    )
  }
}

if (typeof window !== "undefined") {
  async function checkAuth() {
    try {
      const r = await fetch('/api/auth/check');
      const d = await r.json();
      return !!d.loggedIn;
    } catch { return false; }
  }

  function showEditBtn() {
    if (document.getElementById('vp-edit-fab')) return;
    const btn = document.createElement('a');
    btn.id = 'vp-edit-fab';
    btn.textContent = '✏️ 编辑';
    btn.className = 'vp-edit-fab';
    btn.href = '#';
    btn.onclick = (e) => {
      e.preventDefault();
      let p = location.pathname.replace(/^\/+|\/+$/g, '');
      if (p.startsWith('guide/')) p = p.replace('guide/', '');
      location.href = '/edit.html?path=' + encodeURIComponent(p);
    };
    document.body.appendChild(btn);
  }

  (async () => {
    if (await checkAuth()) showEditBtn();
  })();

  window.addEventListener('hashchange', () => {
    setTimeout(async () => {
      if (!document.getElementById('vp-edit-fab')) {
        if (await checkAuth()) showEditBtn();
      }
    }, 500);
  });
}
"""


def stage_vitepress(source_dir: Path, serve: bool = True, deploy: str | None = None) -> dict:
    banner("Stage 4/4: 构建 VitePress 站点")
    t0 = time.time()

    sd = SITE_DIR
    sd.mkdir(parents=True, exist_ok=True)
    build_dir_existing = sd / "docs" / ".vitepress" / "dist"
    if build_dir_existing.exists():
        shutil.rmtree(build_dir_existing)

    src_root = source_dir / "根目录"
    if not src_root.exists():
        print(f"  错误: 找不到 {src_root}")
        sys.exit(1)

    docs_dir = sd / "docs"
    vp_dir = docs_dir / ".vitepress"
    public_dir = docs_dir / "public"

    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(vp_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)

    # 构建前清理 docs_dir 下的旧内容，避免上次构建遗留的文档/目录残留
    # （如已删除的文档、废弃的模块目录、操作说明模板.md 的死链）。
    # 保护 .vitepress（配置/主题持久化）和 public（edit.html/favicon）。
    _clean_docs_content(docs_dir)

    _vp_copy_content(src_root, docs_dir)

    # 首页 index.md：仅在不存在时用 VP_INDEX_MD 模板创建（hero + features 首页）。
    # 已存在则保留（用户定制内容不被覆盖）。
    index_md = docs_dir / "index.md"
    if not index_md.exists():
        index_md.write_text(VP_INDEX_MD, encoding="utf-8")

    # Generate sidebar from actual directory structure
    run([sys.executable, str(ROOT / "src" / "gen_sidebar.py"), str(docs_dir)])

    # 防御：清理可能残留的 .js 配置文件。
    # VitePress 会优先加载 config.js / sidebar-data.js（而非 .mts/.mjs），
    # 若存在旧版 .js 配置，会让 pipeline 生成的 .mts/.mjs 配置失效，
    # 表现为 sidebar 显示陈旧结构。每次构建前删除，确保 .mts/.mjs 生效。
    for stale in ("config.js", "sidebar-data.js", "config.ts", "sidebar-data.ts"):
        stale_path = vp_dir / stale
        if stale_path.exists():
            stale_path.unlink()

    config_mts = vp_dir / "config.mts"
    if not config_mts.exists():
        config_mts.write_text(VP_CONFIG_MTS, encoding="utf-8")

    theme_dir = vp_dir / "theme"
    theme_dir.mkdir(exist_ok=True)
    if not (theme_dir / "index.js").exists():
        (theme_dir / "index.js").write_text(THEME_JS_TPL, encoding="utf-8")
    if not (theme_dir / "style.css").exists():
        (theme_dir / "style.css").write_text(VP_STYLE_CSS, encoding="utf-8")

    (public_dir / ".nojekyll").write_text("", encoding="utf-8")
    (public_dir / "edit.html").write_text(EDIT_HTML, encoding="utf-8")
    # 从 assets/ 拷贝静态资源到 public/（favicon、首页 hero 图等）
    # 这些是站点的固定资源，每次构建都从 assets 同步，避免 public 被清空后丢失
    for asset_name in ("favicon.png", "home-hero.png"):
        src_asset = ROOT / "assets" / asset_name
        if src_asset.exists():
            shutil.copy2(src_asset, public_dir / asset_name)

    (sd / "server.js").write_text(SERVER_JS.lstrip(), encoding="utf-8")

    (sd / "package.json").write_text(
        json.dumps({
            "name": "zto-docs",
            "version": "1.0.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vitepress dev docs --port 4000",
                "build": "vitepress build docs",
                "preview": "vitepress preview docs --port 4000",
                "start": "node server.js",
            },
            "devDependencies": {
                "vitepress": "^1.6.0",
                "vue": "^3.5.0",
                "express": "^4.21.0",
                "jsonwebtoken": "^9.0.2",
                "medium-zoom": "^1.1.0",
            },
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    md_count = len(list(docs_dir.rglob("*.md"))) - 1  # subtract index.md
    summary_line("MD 文件数", str(md_count))

    img_fixed = _fix_image_references(docs_dir)
    if img_fixed:
        summary_line("图片引用修复", f"{img_fixed} 处 ✓")

    print("\n  Post-process (HTML cleanup + image fix + link fix)...")
    pp_t0 = time.time()
    run([sys.executable, str(ROOT / "src" / "post_process.py"), str(docs_dir)])
    summary_line("Post-process", fmt_time(time.time() - pp_t0))

    print("\n  npm install...")
    install_t0 = time.time()
    run(["npm", "install"], cwd=str(sd))
    summary_line("npm install", fmt_time(time.time() - install_t0))

    print("\n  VitePress build...")
    build_dir_local = docs_dir / ".vitepress" / "dist"

    build_t0 = time.time()
    run(["npx", "vitepress", "build", "docs"], cwd=str(sd))
    build_time = time.time() - build_t0

    asset_count = sum(len(files) for _, _, files in os.walk(build_dir_local)) if build_dir_local.exists() else 0
    summary_line("VitePress build", f"{md_count} 页面, {asset_count} 资源 ✓ {fmt_time(build_time)}")

    elapsed = time.time() - t0

    if deploy:
        _deploy(build_dir_local, mode=deploy)
    elif serve:
        print(f"\n  启动文档服务 (含在线编辑): http://localhost:4000")
        print(f"  编辑入口: http://localhost:4000/edit.html")
        print(f"  Ctrl+C 停止\n")
        try:
            run(["node", "server.js"], cwd=str(sd))
        except KeyboardInterrupt:
            print("\n  服务已停止")

    divider()
    summary_line("构建耗时", fmt_time(elapsed))

    return {"pages": md_count, "assets": asset_count, "elapsed": elapsed}


def _clean_docs_content(docs_dir: Path) -> None:
    """清理 docs_dir 下的旧文档内容，但保留 .vitepress / public / node_modules。

    每次构建都应基于最新的源文件，避免上次构建遗留的废弃目录、已删除文档
    或模板文件（死链）残留下来导致构建失败或站点内容陈旧。
    保护首页 index.md（用户定制的 hero/features 首页，不应被清理覆盖）。
    """
    KEEP = {".vitepress", "public", "node_modules", "index.md"}
    for item in os.listdir(docs_dir):
        if item in KEEP:
            continue
        p = docs_dir / item
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()


def _vp_copy_content(src: Path, dst: Path) -> None:
    for item in sorted(os.listdir(src)):
        s = src / item
        safe_name = re.sub(r'[?<>:"|*]', '', item)
        safe_name = _clean_top_level_section_name(safe_name)
        d = dst / safe_name
        if s.is_dir():
            if s.name == "images":
                if d.exists():
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                os.makedirs(d, exist_ok=True)
                _vp_copy_content(s, d)
        elif item.endswith(".md"):
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, d)


_TOP_LEVEL_SECTION_RENAMES = {
    "一、网点操作": "网点操作",
    "二、中心操作": "中心操作",
    "三、云仓操作": "云仓操作",
    "四、网络货运": "网络货运",
}


def _clean_top_level_section_name(name: str) -> str:
    return _TOP_LEVEL_SECTION_RENAMES.get(name, name)


_IMG_REF_PATTERN = re.compile(r'(!\[([^\]]*)\]\(([^)]+\.png)\))')
_IMG_PREFIX_PATTERN = re.compile(r'(img_\d+)_')


def _fix_image_references(docs_dir: Path) -> int:
    fixed = 0
    for md_file in docs_dir.rglob("*.md"):
        img_dir = md_file.parent / "images"
        if not img_dir.is_dir():
            continue
        actual = {}
        for img in os.listdir(img_dir):
            m = _IMG_PREFIX_PATTERN.match(img)
            if m:
                actual[m.group(1)] = img

        content = md_file.read_text(encoding="utf-8", errors="ignore")
        original = content

        def _patch(m):
            nonlocal fixed
            alt, path = m.group(2), m.group(3)
            basename = os.path.basename(path)
            pm = _IMG_PREFIX_PATTERN.match(basename)
            if pm:
                prefix = pm.group(1)
                if prefix in actual and actual[prefix] != basename:
                    fixed += 1
                    d = os.path.dirname(path)
                    new_path = f"{d}/{actual[prefix]}" if d else actual[prefix]
                    return f"![{alt}]({new_path})"
            return m.group(0)

        content = _IMG_REF_PATTERN.sub(_patch, content)
        if content != original:
            md_file.write_text(content, encoding="utf-8")

    return fixed


_SIDEBAR_STRIP_PATTERN = re.compile(
    r"^(?:"
    r"[一二三四五六七八九十百零〇两]+\s*[、.．\s]\s*"
    r"|0?\d+(?:[\-\.]\d+)*(?=[\u4e00-\u9fffA-Za-z「【{])"
    r"|0?\d+(?:[\-\.]\d+)*[\s、.．:\-\)\]）】]"
    r"|[\(（]\d+[\)）.]\s*"
    r"|[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]\s*"
    r"|第\s*[一二三四五六七八九十百零〇两\d]+\s*[章节步项条部分]\s*[:：、.\-]?\s*"
    r")+"
)


def _clean_sidebar_text(text: str) -> str:
    text = _SIDEBAR_STRIP_PATTERN.sub("", text)
    text = text.strip("：:- \t\n\r")
    return text or text


_GENERATED_INDEX_HEADINGS = {"## 分类", "## 文档"}
_GENERATED_INDEX_LINK_RE = re.compile(r"^- (?:\*\*)?\[[^\]]+\]\(\./[^)]*\)(?:\*\*)?$")


def _is_generated_dir_index(content: str) -> bool:
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    if len(lines) <= 1:
        return True
    if not lines[0].startswith("# "):
        return False

    for line in lines[1:]:
        if line in _GENERATED_INDEX_HEADINGS or line == "_（本目录暂无文档）_":
            continue
        if _GENERATED_INDEX_LINK_RE.match(line):
            continue
        return False
    return True


def _build_sidebar(guide_dir: Path, vp_dir: Path) -> list:
    items = _vp_build_sidebar(guide_dir, "")
    mjs = "export default " + json.dumps(items, ensure_ascii=False, indent=2) + "\n"
    (vp_dir / "sidebar-data.mjs").write_text(mjs, encoding="utf-8")
    return items


def _ensure_dir_index(dir_path: Path, sub_items: list[dict]) -> None:
    """确保目录有一个 index.md：自动生成「文章列表」索引页。

    已存在且不是自动生成样式的 index.md（用户手写了内容）不覆盖。
    直接读取 dir_path 的真实子项来生成链接，避免依赖清理过的标题文本。
    """
    index_md = dir_path / "index.md"
    title = _clean_sidebar_text(dir_path.name)

    if index_md.exists():
        content = index_md.read_text(encoding="utf-8")
        if not _is_generated_dir_index(content):
            return

    # 直接读真实子项，分类生成链接（链接用真实名字，标题用清理后名字）
    sub_dirs = sorted([
        d for d in os.listdir(dir_path)
        if (dir_path / d).is_dir() and d != "images" and not d.startswith(".")
    ])
    sub_mds = sorted([
        m for m in os.listdir(dir_path)
        if m.endswith(".md") and m != "index.md"
    ])

    parts = [f"# {title}\n"]

    if sub_dirs:
        parts.append("## 分类\n")
        for d in sub_dirs:
            parts.append(f"- **[{_clean_sidebar_text(d)}](./{d}/)**")
        parts.append("")

    if sub_mds:
        parts.append("## 文档\n")
        for m in sub_mds:
            stem = m[:-3]  # 去 .md
            parts.append(f"- [{_clean_sidebar_text(stem)}](./{stem})")
        parts.append("")

    if not sub_dirs and not sub_mds:
        parts.append("_（本目录暂无文档）_\n")

    index_md.write_text("\n".join(parts), encoding="utf-8")


def _flatten_docs(dir_path: Path, rel_prefix: str) -> list[dict]:
    """递归拍平目录下所有层级的文章，返回扁平的 link 列表。

    用于模块内部：把「篇章/子篇章/.../文章」的层级结构全部拍平，
    让文章直接挂到模块分组下，避免侧边栏层级过深。
    """
    items: list[dict] = []
    entries = sorted(os.listdir(dir_path))
    dirs = [i for i in entries if (dir_path / i).is_dir() and i != "images" and not i.startswith(".")]
    mds = [i for i in entries if i.endswith(".md")]

    # 先本目录直属文章
    for md in sorted(mds):
        if md == "index.md":
            continue
        raw_title = md.replace(".md", "")
        title = _clean_sidebar_text(raw_title)
        # rel_prefix 形如 "/网点操作/01物料购买篇"，拼接后去掉 .md（clean URL）
        link = f"{rel_prefix}/{raw_title}".replace("//", "/")
        items.append({"text": title, "link": link})

    # 再递归子目录，把里面的文章提上来
    for d in sorted(dirs):
        full = dir_path / d
        sub_rel = f"{rel_prefix}/{d}"
        # 子目录若无任何 md，跳过（避免空分组）
        if not any(full.rglob("*.md")):
            continue
        # 子目录拍平后的文章（同时为子目录生成 index 页）
        sub_items = _flatten_docs(full, sub_rel)
        _ensure_dir_index(full, sub_items)
        items.extend(sub_items)

    return items


def _vp_build_sidebar(dir_path: Path, rel_prefix: str) -> list:
    """递归生成保留层级的 sidebar：分类作为分组，文章作为叶子。

    层级：模块(一级) → 篇章(二级) → 文章(三级)，若篇章下还有文件夹则继续递归。
    不显式设置 collapsed，由 VitePress 默认行为决定展开/折叠。
    """
    items: list[dict] = []
    entries = sorted(os.listdir(dir_path))
    dirs = [i for i in entries if (dir_path / i).is_dir() and i != "images" and not i.startswith(".")]
    mds = [i for i in entries if i.endswith(".md")]

    for d in sorted(dirs):
        full = dir_path / d
        sub_rel = f"{rel_prefix}/{d}"
        sub_items = _vp_build_sidebar(full, sub_rel)
        if not sub_items:
            continue
        _ensure_dir_index(full, sub_items)
        items.append({
            "text": _clean_sidebar_text(d),
            "items": sub_items,
        })

    for md in sorted(mds):
        if md == "index.md":
            continue
        raw_title = md.replace(".md", "")
        title = _clean_sidebar_text(raw_title)
        link = f"{rel_prefix}/{raw_title}".replace("//", "/")
        items.append({"text": title, "link": link})

    return items


# ── 部署 ────────────────────────────────────────────────────────

def _deploy(site_dir: Path, mode: str = "fast") -> None:
    print("\n  部署到服务器...")
    tmp_tar = "/tmp/vitepress-deploy.tar"
    if os.path.exists(tmp_tar):
        os.remove(tmp_tar)

    if mode == "full":
        tar_args = ["tar", "--no-mac-metadata", "-C", str(site_dir), "-cf", tmp_tar, "."]
    else:
        tar_args = [
            "tar", "--no-mac-metadata",
            "--exclude=*.png", "--exclude=*.jpg", "--exclude=*.jpeg",
            "--exclude=*.gif", "--exclude=*.webp", "--exclude=*.svg",
            "-C", str(site_dir), "-cf", tmp_tar, ".",
        ]
    run(tar_args)

    tar_size = os.path.getsize(tmp_tar) / 1024 / 1024
    summary_line("打包大小", f"{tar_size:.1f} MB")

    upload_t0 = time.time()
    run(["scp", tmp_tar, f"{DEPLOY_HOST}:{tmp_tar}"])
    upload_time = time.time() - upload_t0
    summary_line("上传耗时", fmt_time(upload_time))

    if mode == "full":
        ssh_cmd = (
            f"mkdir -p '{DEPLOY_PATH}' && "
            f"rm -rf '{DEPLOY_PATH}'/* && "
            f"tar -C '{DEPLOY_PATH}' -xf {tmp_tar} && "
            f"find '{DEPLOY_PATH}' -name '._*' -type f -delete && "
            f"rm -f {tmp_tar}"
        )
    else:
        ssh_cmd = (
            f"mkdir -p '{DEPLOY_PATH}' && "
            f"find '{DEPLOY_PATH}' -type f ! \\( "
            f"  -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o "
            f"  -iname '*.gif' -o -iname '*.webp' -o -iname '*.svg' "
            f"\\) -delete && "
            f"tar -C '{DEPLOY_PATH}' -xf {tmp_tar} && "
            f"find '{DEPLOY_PATH}' -name '._*' -type f -delete && "
            f"rm -f {tmp_tar}"
        )
    run(["ssh", DEPLOY_HOST, ssh_cmd])

    os.remove(tmp_tar)
    summary_line("部署完成", f"https://houpe.top/zto/")


# ── Main ────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="钉钉文档一条龙: 抓取 → 过滤 → 优化 → VitePress",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("url", nargs="?", help="钉钉文档分享 URL")
    parser.add_argument("--source", default=None,
                        help="已有 MD 目录（跳过 Stage 1 抓取）")
    parser.add_argument("--no-ai", action="store_true", default=True,
                        help="跳过 AI 优化，仅规则引擎（默认启用）")
    parser.add_argument("--use-ai", action="store_true",
                        help="启用 DeepSeek AI 语义优化（默认关闭）")
    parser.add_argument("--model", default="deepseek-chat",
                        help="DeepSeek 模型 (default: deepseek-chat)")
    parser.add_argument("--no-serve", action="store_true",
                        help="构建完不启动本地预览")
    parser.add_argument("--deploy", choices=["fast", "full"], default=None,
                        help="部署到服务器: fast=只传非图片, full=全部重传")
    parser.add_argument("--exclude", action="append", default=[],
                        help="追加排除关键字（可多次使用）")
    args = parser.parse_args()

    total_t0 = time.time()

    # ── Stage 1: 抓取 ──
    if args.source:
        source = Path(args.source).resolve()
        if not source.exists():
            print(f"源目录不存在: {source}")
            sys.exit(1)
    elif args.url:
        stage_crawl(args.url, OUTPUT_DIR)
        source = OUTPUT_DIR
    else:
        parser.error("需要提供钉钉文档 URL，或用 --source 指定已有 MD 目录")

    # ── Stage 2: 过滤 ──
    extra_kw = args.exclude if args.exclude else None
    stage_filter(source, extra_keywords=extra_kw)

    # ── Stage 3: 优化 ──
    optimized, opt_stats = stage_optimize(
        source,
        use_ai=args.use_ai,
        model=args.model,
    )

    # ── Stage 4: VitePress ──
    # ── Stage 4: VitePress 构建 ──
    stage_vitepress(
        optimized,
        serve=not args.no_serve and not args.deploy,
        deploy=args.deploy,
    )

    # ── 总结 ──
    total_elapsed = time.time() - total_t0
    print(f"\n{'═' * 60}")
    print(f"  完成! 总耗时: {fmt_time(total_elapsed)}")
    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    main()
