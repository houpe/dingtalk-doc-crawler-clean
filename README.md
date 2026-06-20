# 钉钉文档一条龙 Pipeline

从钉钉知识库抓取文档 → 过滤 → 规则/AI 优化 → 构建 VitePress 站点（含在线编辑），一个命令搞定。

为「中通冷链操作手册」文档站服务，覆盖网点、中心、云仓、冷运运、网络货运、财务中心六大业务模块。

## 安装

```bash
# Python 依赖
pip install -r requirements.txt

# dws CLI（Stage 1 抓取钉钉文档需要）
# 需自行安装并登录 dws，确保 `dws doc list` 可用

# Node 依赖（Stage 4 VitePress 构建时会自动 npm install）
```

## 用法

```bash
# 完整一条龙（抓取 → 过滤 → 优化 → 构建预览）
python3 src/pipeline.py "钉钉文档分享URL"

# 从已有 output 目录开始（最常用，跳过抓取）
python3 src/pipeline.py --source ./output

# 构建后直接部署到服务器
python3 src/pipeline.py --source ./output --deploy fast   # 只传非图片文件
python3 src/pipeline.py --source ./output --deploy full   # 全量重传

# 单独启动 VitePress 预览（不走 pipeline）
cd site && npx vitepress dev docs --port 4001
```

## 流水线

```
Stage 1: 抓取 (dws_crawler.py)
    ↓  调 dws CLI 从钉钉 API 拉文档 + 下载图片到 images/
Stage 2: 过滤 (pipeline.py::stage_filter)
    ↓  就地删除文件名含「日志/周报/月报/记录/更新/历史」的文档
Stage 3: 优化 (reformat_md.py + 可选 optimize_md_deepseek.py)
    ↓  规则引擎清理（标题/列表/容器），AI 默认关闭
Stage 4: VitePress 构建 (pipeline.py::stage_vitepress + post_process.py)
    ↓  生成站点 + Express 后端 + Monaco 在线编辑器
```

| Stage | 输入 | 输出 |
|-------|------|------|
| 1 | URL | `output/根目录/` |
| 2 | `output/` | `output/`（就地删除） |
| 3 | `output/` | `output_optimized/`（规则）或 `output_reformatted/` + `output_optimized/`（AI） |
| 4 | `output_optimized/` | `site/docs/` → `site/docs/.vitepress/dist/` |

## 项目结构

```
.
├── src/
│   ├── pipeline.py               # 一条龙主入口（四阶段编排 + VitePress 生成 + 部署）
│   ├── dws_crawler.py            # Stage 1: dws CLI 抓取钉钉文档 + 下载图片
│   ├── reformat_md.py            # Stage 3: MD 规则优化（标题去 **/去序号、列表、容器）
│   ├── optimize_md_deepseek.py   # Stage 3 可选: DeepSeek AI 语义优化
│   ├── post_process.py           # Stage 4: 构建前兜底（清 HTML、修图链、删死链）
│   ├── build_vitepress.py        # 从 output_optimized 直接构建（带临时软链接）
│   ├── preview_vitepress.py      # 从 output_optimized 直接预览
│   └── download_images_only.py   # 只补下载图片，不重抓文档
├── assets/
│   └── favicon.png               # 站点图标
├── output/                       # 原始抓取（gitignore）
├── output_optimized/             # 规则优化后（gitignore）
├── output_reformatted/           # AI 模式中间产物（gitignore）
├── site/                         # VitePress 站点
│   ├── docs/                     # 文档源 + 各业务分类目录
│   │   └── .vitepress/           # 配置/主题（持久化，pipeline 不覆写）
│   ├── server.js                 # Express 后端 + JWT 登录 + 构建 API（pipeline 生成）
│   └── package.json
├── scripts/
│   └── copy_images.py            # 辅助：复制图片到 site/docs 并改本地引用
├── tests/
├── docs/                         # 设计/计划文档
│   ├── workflow.md               # 工作流详解
│   └── plan-md-optimization.md   # MD 优化完成记录
└── requirements.txt
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 钉钉文档分享 URL（与 `--source` 二选一） | - |
| `--source DIR` | 已有 MD 目录，跳过 Stage 1 | - |
| `--no-ai` | 跳过 AI 优化，仅规则引擎（**默认启用**） | true |
| `--use-ai` | 启用 DeepSeek AI 语义优化 | false |
| `--model MODEL` | DeepSeek 模型 | deepseek-chat |
| `--no-serve` | 构建完不启动本地预览 | false |
| `--deploy fast\|full` | 部署到服务器 | - |
| `--exclude KW` | 追加排除关键字（可多次使用） | - |

## 在线编辑闭环

Stage 4 不仅构建静态站，还会生成：

- **`server.js`** — Express 后端，提供 JWT 登录、`GET/PUT /api/docs/:path`（读写 MD）、`POST /api/build`（触发 VitePress 重建）。默认 `admin/admin123`，可用环境变量 `ADMIN_USER`/`ADMIN_PASS`/`JWT_SECRET`/`PORT` 覆盖。
- **`public/edit.html`** — Monaco 编辑器 + Markdown 实时预览页，登录后可在线改文档并保存触发重建。
- **主题注入** — 已登录用户页面右下角会出现「✏️ 编辑」悬浮按钮，跳转到对应文档编辑页。

启动：`node site/server.js`（默认 `http://localhost:4000`，编辑入口 `/edit.html`）。

## 主题与配置持久化

`site/docs/.vitepress/` 下的 `config.mts`、`theme/` 只在**首次**创建，后续 pipeline 运行**不会覆写**，避免主题改动被冲掉。`sidebar-data.mjs` 则每次运行自动重新生成（扫描目录结构）。

## 部署

通过 scp + tar 部署到服务器（默认 `root@42.192.205.206:/zto`，可用 `DEPLOY_HOST`/`DEPLOY_PATH` 环境变量覆盖）：

- `fast` — 只传非图片文件（增量、快）
- `full` — 全量重传（含图片）

部署后访问 `https://houpe.top/zto/`。

## 依赖

- **Python**: requests, beautifulsoup4, lxml, Markdown, pytest
- **Node**: VitePress 1.6+, Vue 3.5+, Express, jsonwebtoken, medium-zoom
- **外部工具**: `dws` CLI（钉钉文档 API）、DeepSeek API（可选，仅 `--use-ai` 时）

MIT License
