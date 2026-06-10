# 钉钉文档一条龙 Pipeline

从钉钉抓取文档 → 过滤 → 优化 → 构建 GitBook 站点，一个命令搞定。

## 安装

```bash
pip install -r requirements.txt
```

## 用法

```bash
# 完整一条龙（抓取 → 过滤 → 优化 → 本地预览）
python3 pipeline.py https://alidocs.dingtalk.com/i/p/xxxxx

# 从已有 output 目录开始
python3 pipeline.py --source ./output

# 跳过 AI 优化
python3 pipeline.py --source ./output --no-ai

# 部署到服务器
python3 pipeline.py --source ./output --deploy full
```

## 流水线

```
Stage 1: 抓取 (crawler.py)
    ↓
Stage 2: 过滤 (排除日志/周报/月报/记录/更新等文档)
    ↓
Stage 3: 优化 (规则引擎 reformat_md.py → DeepSeek AI optimize_md_deepseek.py)
    ↓
Stage 4: GitBook 构建 (HonKit → 本地预览 or 部署)
```

## 项目结构

```
.
├── pipeline.py                  # 一条龙主入口
├── crawler.py                   # 爬虫入口
├── reformat_md.py               # 规则引擎优化
├── optimize_md_deepseek.py      # DeepSeek AI 优化
├── requirements.txt
├── dingtalk_docs_html/
│   ├── crawler_core.py          # 爬虫核心
│   └── site_builder.py          # 站点构建核心
├── tests/
│   └── test_manual_restructure.py
├── docs/
│   └── pipeline-plan.md         # 设计文档
└── output/                      # 抓取输出（gitignore）
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 钉钉文档分享 URL | - |
| `--source DIR` | 已有 MD 目录（跳过抓取） | - |
| `--no-ai` | 跳过 AI 优化 | false |
| `--model MODEL` | DeepSeek 模型 | deepseek-chat |
| `--no-serve` | 不启动本地预览 | false |
| `--deploy fast\|full` | 部署到服务器 | - |
| `--exclude KW` | 追加排除关键字 | - |

## 依赖

- requests, beautifulsoup4, lxml
- HonKit (GitBook 兼容, npx 自动调用)
- DeepSeek API (可选)

MIT License
