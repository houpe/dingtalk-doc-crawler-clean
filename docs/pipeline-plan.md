# 钉钉文档一条龙 Pipeline 设计文档

## 概述

将钉钉文档爬取、过滤、优化、GitBook 构建整合为单文件 CLI 工具 `pipeline.py`，一个命令完成全流程。

## 流水线架构

```
钉钉文档 URL
    │
    ▼
┌─────────────────────────────────┐
│  Stage 1: 抓取                   │  crawler.py
│  调用 crawler_core 递归抓取       │
│  输出: output/根目录/...          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Stage 2: 过滤                   │  pipeline.py 内置
│  排除标题含排除关键字的文档         │
│  输出: output/ (原地删除)         │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Stage 3a: 规则引擎优化           │  reformat_md.py
│  标题层级/列表/blockquote 重排    │
│  输出: output_reformatted/       │
├─────────────────────────────────┤
│  Stage 3b: DeepSeek AI 优化      │  optimize_md_deepseek.py
│  模型: deepseek-chat (Flash)     │
│  输出: output_optimized/         │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Stage 4: GitBook 构建           │  HonKit (gitbook 兼容)
│  生成 SUMMARY.md + book.json     │
│  HonKit build → _book/           │
│  本地 serve 或部署到服务器         │
└─────────────────────────────────┘
```

## Stage 2: 文档过滤规则

### 排除关键字

标题/文件名中包含以下任一关键字的文档将被排除：

```
日志、周报、月报、记录、更新
```

### 匹配逻辑

- 遍历 `output/根目录/` 下所有 `.md` 文件
- 取文件名（去掉 `.md` 后缀）与关键字做包含匹配
- 同时检查所在目录名（用于过滤以"更新日志"命名的文件夹）
- 删除命中的 `.md` 文件
- 删除变为空的目录
- **不过滤 images 目录**

### 过滤输出示例

```
  [排除] 中通仓链20260320系统更新日志.md (命中: 日志)
  [排除] 中通仓链20260226系统更新日志.md (命中: 日志)
  [排除] 中通冷链20260210系统更新日志.md (命中: 日志)
  ...
  排除: 9 个, 保留: 135 个
```

## CLI 接口

```bash
# 完整一条龙（抓取 → 过滤 → 优化 → 本地预览）
python3 pipeline.py https://alidocs.dingtalk.com/i/p/xxxxx

# 从已有 output 开始（跳过抓取）
python3 pipeline.py --source ./output

# 只跑规则引擎，不调 AI
python3 pipeline.py --source ./output --no-ai

# 本地预览但不自动 serve
python3 pipeline.py --source ./output --no-serve

# 部署到服务器
python3 pipeline.py --source ./output --deploy fast
python3 pipeline.py --source ./output --deploy full   # 含图片全量重传

# 指定 AI 模型
python3 pipeline.py --source ./output --model deepseek-reasoner
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 钉钉文档分享 URL（位置参数） | 无 |
| `--source DIR` | 已有 MD 目录（跳过 Stage 1） | 无 |
| `--no-ai` | 跳过 DeepSeek AI，仅规则引擎 | false |
| `--no-serve` | 构建完不启动本地预览 | false |
| `--deploy fast\|full` | 部署到服务器 | 不部署 |
| `--model MODEL` | DeepSeek 模型名 | deepseek-chat |
| `--exclude KW` | 追加排除关键字 | 无 |

## 进度输出格式

```
════════════════════════════════════════════════════════════
  Stage 1/4: 抓取钉钉文档
════════════════════════════════════════════════════════════
  文档名称: 中通冷链操作手册
  顶级节点: 8
  文档总数: 152 | 文件夹: 23
  图片下载: 234 张
  耗时: 45.2s

════════════════════════════════════════════════════════════
  Stage 2/4: 过滤排除文档
════════════════════════════════════════════════════════════
  排除关键字: 日志|周报|月报|记录|更新
  [排除] 中通仓链20260320系统更新日志.md (命中: 日志)
  [排除] 中通仓链20260226系统更新日志.md (命中: 日志)
  [排除] 中通冷链20260210系统更新日志.md (命中: 日志)
  [排除] 中通仓链20260312系统更新日志.md (命中: 日志)
  [排除] 中通仓链20260324系统更新日志.md (命中: 日志)
  [排除] 中通冷链 20260312系统更新日志.md (命中: 日志)
  [排除] 中通冷链 20260324系统更新日志.md (命中: 日志)
  [排除] 19. WMS业务需求池（新旧需求会不断更新）.md (命中: 更新)
  [排除] 这趟任务超时了哪里可以看到轨迹、停车记录?.md (命中: 记录)
  ─────────────────────────────────────────────────────────
  排除: 9 个 | 保留: 135 个

════════════════════════════════════════════════════════════
  Stage 3/4: Markdown 优化
════════════════════════════════════════════════════════════
  [规则引擎] 处理 135 个文件 ✓ 0.8s
  [DeepSeek Flash] 模型: deepseek-chat
    [  1/135] 系统如何访问APP如何下载.md ✓ 1.2s
    [  2/135] 系统账号如何开通权限如何配置.md ✓ 0.9s
    ...
    [130/135] xxx.md ✓ 1.1s
    [131/135] xxx.md FAILED (retry 3/3): timeout
    ...
  ─────────────────────────────────────────────────────────
  规则引擎: 135 个 ✓ 0.8s
  AI 优化: 130/135 成功, 5 失败, 耗时: 312.4s

════════════════════════════════════════════════════════════
  Stage 4/4: 构建 GitBook
════════════════════════════════════════════════════════════
  生成 SUMMARY.md: 109 条目
  生成 book.json: plugins=[-lunr, -search, search]
  HonKit build: 109 页面, 1195 资源 ✓ 8.3s
  本地预览: http://localhost:4000

════════════════════════════════════════════════════════════
  完成! 总耗时: 368.5s
════════════════════════════════════════════════════════════
```

## 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `pipeline.py` | **重写** | 整合全部 4 阶段 + 过滤 + 详情输出 |
| `optimize_md_deepseek.py` | **小改** | 加 `--model` 参数，支持切换模型 |
| `gitbook/book.json` | **改** | 插件精简为 HonKit 兼容 |
| `setup_gitbook.py` | **删除** | 逻辑并入 pipeline.py |
| `crawler.py` | 不动 | |
| `reformat_md.py` | 不动 | |
| `deploy_site.sh` | 不动 | 旧部署脚本保留，pipeline 自带部署逻辑 |
| `dingtalk_docs_html/*` | 不动 | |

## GitBook 配置

使用 HonKit（GitBook CLI 的活跃维护 fork），兼容 GitBook 格式。

### book.json

```json
{
  "title": "中通冷链文档中心",
  "language": "zh",
  "plugins": ["-lunr", "-search", "search"]
}
```

### SUMMARY.md 自动生成

- 遍历优化后的 MD 目录树
- 每个子目录自动生成 `README.md` 作为章节页
- URL 中空格/特殊字符做 percent-encode
- 目录层级映射为 GitBook 导航层级

### 构建命令

```bash
npx honkit build <gitbook-dir> <output-dir>
npx honkit serve <gitbook-dir>              # 本地预览 http://localhost:4000
```

## 部署（可选）

默认本地 serve 预览。加 `--deploy` 时推送到服务器：

- 服务器: `root@42.192.205.206`
- 路径: `/zto/`
- URL: `https://wiki.houpe.top/`
- `fast` 模式：只传非图片文件（保留远端图片）
- `full` 模式：全量重传（含图片）

## 部署流程

```
本地 _book/ → tar 打包 → scp 上传 → ssh 解压 → 完成
```
