# 钉钉文档知识库 - 工作流说明

## 项目结构

```
dingtalk-doc-crawler-clean/
── src/
│   ├── dws_crawler.py           # 从钉钉拉取文档 + 下载图片
│   ├── pipeline.py              # 全流程编排（拉取/过滤/优化/构建）
│   ├── reformat_md.py           # MD 规则优化（标题去序号/列表规范化/容器修复）
│   ├── post_process.py          # 后处理（HTML清理/图片替换/死链修复/空图删除）
│   └── optimize_md_deepseek.py  # DeepSeek AI 深度优化（可选）
├── output/                      # 原始拉取结果（输出目录）
│   └── 根目录/                  # 按钉钉目录结构存放的 md + 图片
├── output_optimized/            # 规则引擎优化后的结果
├── site/                        # VitePress 站点
│   ├── docs/                    # 文档源文件
│   │   ├── index.md             # 首页（含 Vue 组件）
│   │   ├── 「*必知必读」/         # 各分类目录
│   │   ├── 一、网点操作/
│   │   └── .vitepress/          # ← 主题配置（持久化，pipeline 不覆写）
│   │       ├── config.mts       # VitePress 配置
│   │       └── theme/           # 自定义主题
│   └── package.json
└── docs/
    └── workflow.md              # ← 你正在看的文件
```

## 一键命令

### 完整流程（拉取 → 过滤 → 优化 → 构建 → 预览）

```bash
python3 src/pipeline.py "钉钉文档分享URL"
```

### 从本地 output 构建（跳过拉取，最常用）

```bash
python3 src/pipeline.py --source ./output
```

### 构建后直接部署到服务器

```bash
python3 src/pipeline.py --source ./output --deploy fast
python3 src/pipeline.py --source ./output --deploy full   # 全量上传
```

### 单独启动 VitePress 预览

```bash
cd site && npx vitepress dev docs --port 4001
```

### 构建生产版本

```bash
cd site && npx vitepress build docs
```

## 处理流程详解

```
 ┌──────────────┐
 │  dws_crawler │  从钉钉 API 拉取文档，保存到 output/根目录/
 │   (Stage 1)  │  ✓ 下载图片到 images/ 子目录
 ──────┬───────┘  ✓ 按钉钉目录结构组织
        │
        ▼
 ┌──────────────┐
 │   pipeline   │  Stage 2: 过滤（删除含"日志/周报/月报"等关键词的文档）
 │  (Stage 2-3) │  Stage 3: 规则引擎优化（reformat_md.py）
 ──────┬───────┘  ✓ 输出到 output_optimized/根目录/
        │
        ▼
 ┌──────────────┐
 │ post_process │  后处理（HTML 清理 + 图片修复 + 死链修复）
 │              │  ✓ 自动扫描每个 md 同级 images/ 目录
 └─────────────┘  ✓ 远程 OSS URL → 本地 ./images/xxx.png
        │          ✓ 移除不存在的图片引用
        ▼          ✓ 修复相对路径死链和邮箱链接
 ──────────────┐
 │   VitePress  │  Stage 4: 构建 VitePress 站点
 │   (Stage 4)  │  ✓ 复制到 site/docs/
 └──────┬───────┘  ✓ 自动刷新 sidebar-data
        │          ✓ npm install + npx vitepress build
        ▼
 ┌──────────────┐
 │   浏览器预览  │  http://localhost:4001
 ──────────────┘
```

## 各脚本作用

### `dws_crawler.py` — 拉取文档

- 调用 `dws` CLI 从钉钉知识库拉取所有文档
- 自动下载所有图片，保存到 `images/` 子目录
- 按钉钉目录结构输出
- **排除关键词**：`日志`, `周报`, `月报`, `记录`, `更新`, `历史`

### `pipeline.py` — 全流程编排

| Stage | 作用 | 输入 | 输出 |
|-------|------|------|------|
| 1 | 抓取 | URL | `output/` |
| 2 | 过滤 | `output/` | `output/`（就地删除匹配的） |
| 3 | 优化 | `output/` | `output_optimized/` |
| 4 | VitePress | `output_optimized/` | `site/docs/` → `.vitepress/dist/` |

**重要改动**（防止主题被覆盖）：
- Stage 4 的 `config.mts`、`theme/` 目录**只在首次创建**，后续不覆写
- `post_process.py` 自动在构建前执行

### `reformat_md.py` — MD 规则优化

**文本处理**：
- 标题去序号（`一、` → 空，`01.` → 空）
- 规范化有序/无序列表
- 合并相邻容器
- 修复钉钉 `:::` 特殊语法
- 关闭未闭合的 `:::` 容器
- 移除"更多操作索引"
- 标题中去除 `**` 包裹

**图片处理**：
- 复制 `images/` 目录到目标输出

### `post_process.py` — 后处理（关键！）

VitePress 构建前执行，修复所有已知构建错误：

1. **HTML 清理**
   - 移除 `<u>`, `<font>`, `<sub>`, `<sup>` 等 Vue 不兼容标签
   - 转换 `<li>`/`<ul>` 为 bullet 点
   - **保护 `<script>`/`<style>` 块不被处理**

2. **图片修复**
   - 远程 `alidocs2.oss.cn-zhangjiakou.aliyuncs.com` URL → 本地 `./images/xxx.png`
   - 按出现顺序匹配同目录下 `images/` 中的文件
   - 移除 `![...]( "")` 等空 src 图片
   - 移除指向不存在文件的图片引用

3. **死链修复**
   - 移除 `/../` 前缀
   - 邮箱链接转为纯文本
   - Alidocs 附件链接转为纯文本
   - 移除模板占位链接

4. **空白行清理**
   - 限制连续空行不超过 2 行

## 主题与配置持久化

`site/docs/.vitepress/` 下的文件是**持久化的**：

- `config.mts` — VitePress 配置（端口、侧边栏、搜索等）
- `sidebar-data.mjs` — **每次运行自动生成**（扫描目录结构）
- `theme/index.js` + `theme/style.css` — 自定义主题

> ⚠️ **pipeline.py 不会覆盖这些文件**（只在不存在的时创建）

## 更新文档的标准流程

```bash
# Step 1: 拉取最新文档（首次或需要重新拉取时）
python3 src/dws_crawler.py

# Step 2: 全流程重建
python3 src/pipeline.py --source ./output

# Step 3: 在浏览器中预览
# 打开 http://localhost:4001

# Step 4: 部署
python3 src/pipeline.py --source ./output --deploy fast
```

## 常见问题

| 现象 | 原因 | 解决 |
|------|------|------|
| `Element is missing end tag` | md 中有未闭合的 HTML 标签 | `post_process.py` 自动清理 |
| `Found dead link` | 侧边栏/文档引用了不存在的路径 | 检查链接目标文件是否存在 |
| VitePress 卡在 npm install | 首次安装慢 | 等它完成即可 |
| 图片无法显示 | 本地图片目录和 md 不在同一层级 | `post_process.py` 会在同目录下找 `images/` |
| config/theme 被覆盖 | 旧版 pipeline | 已修复：只在不存在的时创建 |
| 首页 Vue 组件损坏 | HTML 清理太激进 | 已修复：`<script>`/`<style>` 受保护 |
