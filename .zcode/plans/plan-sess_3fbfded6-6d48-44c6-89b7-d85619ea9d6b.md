## 目标
文档页 URL 改用钉钉 nodeId（`/d/nodeId`），永久稳定；同时旧 URL 用重定向表兼容。

## 核心数据流
```
output/.dws-crawl-state.json (nodeId → path)   ← 唯一 nodeId 来源
  ↓ stage_vitepress 读取它，构建 path→nodeId 反查表
site/docs/ 下每个 .md 对应一个 nodeId
  ↓ VitePress rewrites: 物理路径.md → d/nodeId
  ↓ sidebar link 也改成 /d/nodeId
最终 URL: /d/nodeId（稳定不变）
```

## 改动清单

### 1. 透传 nodeId 到 stage 4（打通最大障碍）
`stage_optimize` 结束时，把 `output/.dws-crawl-state.json` 复制一份到 `output_optimized/.dws-crawl-state.json`。这样 stage 4 从 `output_optimized` 构建时，能读到 nodeId → path 映射。
- **注意**：state 里的 path 是 `output/根目录/一、网点操作/...`，而 stage 4 的 docs_dir 经过栏目改名（`一、网点操作` → `网点操作`）。所以匹配时要规范化路径（去掉顶层序号前缀），用 `normalize_order_path` 或类似逻辑做模糊匹配。

### 2. 生成 rewrites 映射（pipeline.py stage_vitepress）
在 `_vp_copy_content` 之后、VitePress build 之前，扫描 `docs_dir` 下所有 .md：
- 对每个文件，用规范化路径反查 state，找到对应 nodeId
- 构建 `rewrites = { "网点操作/08其他设置篇/业务员码设置.md": "d/nodeId" }`
- 写入 config.mts 的 `rewrites` 字段（动态生成，不手写 config）

### 3. sidebar link 改用 nodeId（gen_sidebar.py）
`build_sidebar` 生成叶子文档 link 时，改为查 nodeId 映射表，输出 `/d/nodeId`。目录（栏目/篇）无 nodeId，保留中文名 link（如 `/网点操作/`）。
- gen_sidebar.py 接收一个 `node_id_map: dict[str, str]`（path → nodeId），在 `main()` 里从 state 文件加载传入。

### 4. 目录 index.md 链接也改（gen_sidebar.py _ensure_dir_index）
`_ensure_dir_index` 生成的文档链接也要从 `./文档名` 改成 `/d/nodeId`，否则目录页点击文档跳到旧 URL。

### 5. 旧 URL 重定向表（Express 服务端）
部署后旧 URL（如 `/「必知必读」账号权限如何开通？/...`）会 404。在 Express `server.js` / `register-app-routes.js` 加一张重定向表：
- `pipeline` 在构建时生成 `site/redirects.json`（旧 path → 新 nodeId URL）
- 服务端启动时加载，对匹配的旧 URL 返回 301 跳转
- 旧 path 来源：对比「上次部署的 git 历史 site/docs 路径」与「当前路径」，找出变化的；或维护一张历史路径表

### 6. config.mts nav 修复
当前 nav 里有个错误的死链接 `/dist/「_必知必读」...`，改成正确的 nodeId 或栏目链接。

## 不改的部分
- 物理文件名仍保持中文（便于排查），只通过 rewrites 改 URL
- `ignoreDeadLinks: true` 保留（过渡期避免构建报错）
- 文档正文内的相互链接：暂不处理（靠 ignoreDeadLinks 兜底，后续可扩展 post_process.py 转换）

## 风险与回退
- rewrites 是 build 时静态映射，每个 nodeId 一条规则，68 篇文档规模无性能问题
- 万一 nodeId 匹配失败（路径规范化不一致），该文档 URL 退化回物理路径名（不致命）
- 旧 URL 重定向表是增量维护的，第一次部署只覆盖已知变化（账号权限栏目）

## 验证
1. 本地构建后，确认 sidebar link 是 `/d/nodeId` 格式
2. curl 测试 `/d/某nodeId` 返回 200
3. 旧 URL `/「必知必读」...` 返回 301 跳转到新 URL
4. 全量测试不破坏