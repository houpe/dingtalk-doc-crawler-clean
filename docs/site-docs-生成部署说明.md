# site/docs 生成与部署说明

## 适用场景

本文档适用于下面这套工作方式：

- 直接维护 `site/docs/` 里的 `.md` 文档
- 使用 VitePress 构建站点
- 将构建产物部署到线上站点 `https://help.beta.ztocc.com/`

当前线上服务器信息：

- 服务器：`root@121.199.175.111`
- 站点目录：`/www/wwwroot/help.beta.ztocc.com`

## 目录说明

### 文档源目录

- `site/docs/`

你平时改文档，主要就是改这里：

- 各业务文档：`site/docs/**/*.md`
- 站点配置：`site/docs/.vitepress/config.mts`
- 侧边栏数据：`site/docs/.vitepress/sidebar-data.mjs`
- 主题文件：`site/docs/.vitepress/theme/*`

### 构建产物目录

- `site/docs/.vitepress/dist/`

这个目录是最终部署到服务器上的静态站点文件。

## 平时怎么改

### 1. 只改文案内容

如果你只是修改某篇文档正文，比如：

- 改标题
- 改文字说明
- 替换图片
- 增删段落

这种情况下通常只需要：

1. 修改 `site/docs` 下对应的 `.md`
2. 重新构建站点
3. 部署 `dist`

### 2. 改了目录或文件名

如果你做了这些事：

- 新增文档
- 删除文档
- 修改目录名
- 修改文件名
- 希望左侧栏结构或顺序变化

那就要先重生成侧边栏，再构建站点。

## 推荐命令

### 一条命令完成“侧边栏刷新 + 构建”

在 `site/` 目录执行：

```bash
npm run docs:refresh
```

这个命令会自动做两件事：

1. 执行 `python3 ../src/gen_sidebar.py docs`
2. 执行 `vitepress build docs`

### 只重生成侧边栏

```bash
npm run docs:sidebar
```

### 只构建站点

```bash
npm run build
```

## 标准流程

### 场景一：只改文档内容

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm run build
```

构建完成后，部署：

```bash
tar --no-mac-metadata -C /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site/docs/.vitepress/dist -cf /tmp/help-beta-vitepress.tar .
scp /tmp/help-beta-vitepress.tar root@121.199.175.111:/tmp/help-beta-vitepress.tar
ssh root@121.199.175.111 "mkdir -p /tmp/help-beta-backup && tar -C /www/wwwroot/help.beta.ztocc.com -cf /tmp/help-beta-backup/help.beta.ztocc.com-$(date +%Y%m%d%H%M%S).tar --exclude=.well-known . && find /www/wwwroot/help.beta.ztocc.com -mindepth 1 -maxdepth 1 ! -name '.well-known' -exec rm -rf {} + && tar -C /www/wwwroot/help.beta.ztocc.com -xf /tmp/help-beta-vitepress.tar"
```

## 本机管理控制台

在 `site/` 目录启动文档服务：

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm start
```

浏览器打开：

```text
http://127.0.0.1:4000/admin
```

控制台仅允许本机访问，不需要额外登录，支持：

- 第一步“文档生成”：清理旧 `output`，从钉钉重新拉取，再过滤和优化为 `output_optimized`
- 第二步“本地站点构建与预览”：读取 `output_optimized`，重建 `site/docs`、侧边栏和 VitePress `dist`
- 第三步“部署到服务器”：先校验本地构建是否完整，再备份并部署 `dist`，最后检查线上首页
- 全量一键流程：严格按第一步 → 第二步 → 第三步串行执行
- 状态与日志：自动轮询、手动刷新、清空当前页面日志显示、停止当前任务

三个阶段互相隔离：

- 第一步只生成 `output/` 和 `output_optimized/`，不会修改 `site/docs`，也不会部署。
- 第二步只根据 `output_optimized/` 生成本地站点，构建完成后刷新 `http://127.0.0.1:4000/` 即可预览，不会部署服务器。
- 第三步只使用已经生成的 `site/docs/.vitepress/dist/`，不会重新抓取或构建；页面数量校验不通过时会在部署前停止。

控制台仍保留“刷新侧边栏”“构建站点”“刷新并构建站点”三个单步工具，仅用于直接手动修改 `site/docs` 后的维护，不属于从钉钉重新生成的主流程。

同一时间只允许执行一个任务。任务运行时其他任务按钮会禁用；点击“停止当前任务”会终止当前进程组，并且组合流程不会继续执行后续步骤。

本地站点流程会自动使用 `--site-only --no-serve`，因此不会再次过滤优化，也不会启动另一个常驻预览服务。Pipeline 只会在 `site/server.js` 或 `site/package.json` 缺失时初始化这些文件，不会覆盖现有管理台实现。

### 管理台常见问题

#### 页面返回“仅允许本机访问”

请直接使用 `http://127.0.0.1:4000/admin`，不要通过外部域名、反向代理或局域网 IP 访问。

#### 提示“已有任务正在运行”

等待当前任务结束，或先点击“停止当前任务”。后端也会执行单任务锁校验，不能通过重复请求绕过。

#### 文档生成提示源目录不存在

先执行“抓取钉钉文档”，并确认项目根目录存在 `output/根目录/`。

#### 本地站点流程提示优化结果不存在

先完成第一步，并确认项目根目录存在 `output_optimized/根目录/`。第二步不会自动重新抓取或重新优化。

#### 部署或线上校验失败

检查 SSH 权限、服务器连通性、`site/docs/.vitepress/dist/` 是否存在，以及 `https://help.beta.ztocc.com/` 是否可访问。失败日志会保留在控制台中。

### 场景二：改了目录结构、文件名、左侧栏

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm run docs:refresh
```

然后部署：

```bash
tar --no-mac-metadata -C /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site/docs/.vitepress/dist -cf /tmp/help-beta-vitepress.tar .
scp /tmp/help-beta-vitepress.tar root@121.199.175.111:/tmp/help-beta-vitepress.tar
ssh root@121.199.175.111 "mkdir -p /tmp/help-beta-backup && tar -C /www/wwwroot/help.beta.ztocc.com -cf /tmp/help-beta-backup/help.beta.ztocc.com-$(date +%Y%m%d%H%M%S).tar --exclude=.well-known . && find /www/wwwroot/help.beta.ztocc.com -mindepth 1 -maxdepth 1 ! -name '.well-known' -exec rm -rf {} + && tar -C /www/wwwroot/help.beta.ztocc.com -xf /tmp/help-beta-vitepress.tar"
```

## 如何验证是否部署成功

### 1. 先看目标页面

直接打开线上页面，例如：

- `https://help.beta.ztocc.com/网点操作/08其他设置篇/业务员码设置`

### 2. 用命令快速查关键字

例如确认某段旧内容已经消失：

```bash
curl -s "https://help.beta.ztocc.com/%E7%BD%91%E7%82%B9%E6%93%8D%E4%BD%9C/08%E5%85%B6%E4%BB%96%E8%AE%BE%E7%BD%AE%E7%AF%87/%E4%B8%9A%E5%8A%A1%E5%91%98%E7%A0%81%E8%AE%BE%E7%BD%AE" | grep -n "直播回放\|业务员（非代理点）画GIS培训.mp4\|业务员编码怎么用"
```

### 3. 看服务器文件时间

```bash
ssh root@121.199.175.111 "stat -c '%y %n' /www/wwwroot/help.beta.ztocc.com/index.html /www/wwwroot/help.beta.ztocc.com/网点操作/08其他设置篇/业务员码设置.html"
```

## 侧边栏说明

### `VPSidebarNav` 是怎么来的

左侧栏不是写在某一个单独的 `.md` 里。

它来自：

- `site/docs/.vitepress/config.mts` 中的 `sidebar`
- `sidebar` 实际引用 `site/docs/.vitepress/sidebar-data.mjs`

其中：

- `sidebar-data.mjs` 是自动生成的
- 生成脚本是：`src/gen_sidebar.py`

### 什么时候会影响左侧栏

下面这些改动通常会影响左侧栏：

- 修改目录名
- 修改 `.md` 文件名
- 新增或删除 `.md`
- 修改侧边栏生成逻辑

### 注意

- 不建议长期手改 `site/docs/.vitepress/sidebar-data.mjs`
- 因为下一次执行 `npm run docs:sidebar` 或 `npm run docs:refresh` 时，它会被重新生成
- 如果要长期控制排序规则，应该改 `src/gen_sidebar.py`

## 配置文件说明

### 可以长期保留的文件

- `site/docs/.vitepress/config.mts`
- `site/docs/.vitepress/theme/index.js`
- `site/docs/.vitepress/theme/style.css`

这些文件属于站点配置和主题，一般不靠扫描 `site/docs` 自动推导出来。

### 自动生成的文件

- `site/docs/.vitepress/sidebar-data.mjs`
- `site/docs/.vitepress/dist/*`

## 常见问题

### 1. 我改了 md，线上没变

通常是以下原因之一：

- 改完没有重新构建
- 构建后没有部署 `dist`
- 部署到了错误服务器
- 浏览器缓存未刷新

### 2. 左侧栏顺序不对

原因一般不是 `md` 正文，而是：

- 目录名排序
- 文件名排序
- `src/gen_sidebar.py` 的生成规则

### 3. 左侧栏出现 `index 2`

说明源码目录里存在类似这种重复文件：

- `site/docs/index 2.md`

这类文件会被自动收进侧边栏，建议删除后重新执行：

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm run docs:refresh
```

## 最常用的两条命令

### 刷新侧边栏并构建

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm run docs:refresh
```

### 构建后部署到线上

```bash
tar --no-mac-metadata -C /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site/docs/.vitepress/dist -cf /tmp/help-beta-vitepress.tar .
scp /tmp/help-beta-vitepress.tar root@121.199.175.111:/tmp/help-beta-vitepress.tar
ssh root@121.199.175.111 "mkdir -p /tmp/help-beta-backup && tar -C /www/wwwroot/help.beta.ztocc.com -cf /tmp/help-beta-backup/help.beta.ztocc.com-$(date +%Y%m%d%H%M%S).tar --exclude=.well-known . && find /www/wwwroot/help.beta.ztocc.com -mindepth 1 -maxdepth 1 ! -name '.well-known' -exec rm -rf {} + && tar -C /www/wwwroot/help.beta.ztocc.com -xf /tmp/help-beta-vitepress.tar"
```
