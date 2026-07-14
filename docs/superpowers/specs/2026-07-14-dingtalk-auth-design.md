# 设计文档：为 help.beta.ztocc.com 文档站接入钉钉鉴权

- **日期**：2026-07-14
- **状态**：已确认，待编写实现计划
- **范围**：仅 `help.beta.ztocc.com` 域名与其 Express 服务器逻辑
- **参考实现**：`/Users/houpe/Documents/我的开发项目/houpe-auth`（DingTalk OAuth2 + Redis Session SSO）

## 1. 背景与现状

文档站 `site/` 是一个 VitePress 静态站点 + Express 后端（`server.js`），部署到 `help.beta.ztocc.com`。鉴权骨架已搭好 70%，但登录入口从未实现：

| 已具备 | 缺失 |
|---|---|
| Session 中间件 `lib/auth-session.js`（express-session，Redis 优先回退内存） | 登录入口 `/auth/login`（页面 + 路由） |
| 鉴权闸门 `buildRequireAuth`（未登录 302 → `/auth/login`） | 钉钉 OAuth 逻辑 |
| `/api/auth/check`、`/api/auth/me`、`/api/logout` | 4 个钉钉登录端点 |
| `server-config.js`（secret、redis 配置） | 钉钉凭证与 origin 配置 |
| `jsonwebtoken` 依赖（声明但从未使用） | `axios` 依赖（钉钉接口需要） |

**后果**：默认配置下（`AUTH_REQUIRED` 未设 → true），所有访客被重定向到 `/auth/login`，该路径 404，站点实质锁死；只有设 `AUTH_REQUIRED=false` 才开放。

## 2. 目标与非目标

### 目标
- 在 `help.beta.ztocc.com` 上实现钉钉 OAuth2 登录（PC 扫码 + 钉钉 App 内自动登录）
- 复用现有 session 中间件与鉴权闸门，仅补全登录入口
- 全企业成员登录即放行，无需白名单/部门判断
- session 存 Redis 优先，回退内存

### 非目标
- 不做跨域 cookie 共享 SSO（help.beta.ztocc.com 与 www.houpe.top 不同域）
- 不改 VitePress 配置（LOCKED 文件）
- 不做白名单、部门/角色级权限
- 不引入管理员后台（admin 控制台仍走现有 loopback-only 守卫，独立于本次鉴权）

## 3. 整体架构与请求流

所有鉴权发生在 Express 服务端。VitePress 产物是纯静态文件，不参与鉴权。

### PC 扫码登录流程

```
用户访问 https://help.beta.ztocc.com/网点操作/...
  │
  │ requireSiteAuth 检查 req.session.user → 无
  ↓
302 → /auth/login?redirect=/网点操作/...
  │
  │ 登录页加载，用户点击"使用钉钉登录"
  ↓
GET /api/auth/dingtalk/url?redirect=...
  │ 生成 state 存入内存 Map（5分钟TTL，单次使用）
  ↓
302 → https://login.dingtalk.com/oauth2/auth?...&state=xxx
  │ 用户扫码授权，钉钉回调
  ↓
GET /api/auth/dingtalk/callback?code=xxx&state=xxx
  │ 校验 state → dingtalk.getUserByCode(code) → 写 req.session.user → save()
  ↓
302 → 原始 redirect 页面（已登录，放行）
```

### 钉钉 App 内自动登录流程

```
登录页 JS 检测 navigator.userAgent 含 'dingtalk'
  │ 加载 dingtalk-jsapi，调用 requestAuthCode({corpId}) 获取 authCode
  ↓
POST /api/auth/dingtalk/auto  body: {authCode}
  │ dingtalk.getUserByAuthCode(authCode) → 写 session.user → save()
  ↓
返回 {success:true, user}，前端 location.href = redirect
```

### 路径约定

所有钉钉相关路由扁平挂在根路径，命名与现有 `/api/auth/check`、`/api/auth/logout` 一致：

| 路径 | 说明 |
|---|---|
| `/auth/login` | 登录页（复用 `server-config.js` 的 `authLoginUrl` 默认值） |
| `/api/auth/dingtalk/url` | 生成 state，返回钉钉扫码 URL |
| `/api/auth/dingtalk/callback` | OAuth2 回调入口 |
| `/api/auth/dingtalk/auto` | 钉钉 App 内自动登录 |
| `/api/auth/config/public` | 登录页读取 corpId（只读公开） |

钉钉应用回调白名单填：`https://help.beta.ztocc.com/api/auth/dingtalk/callback`

## 4. 新增文件与改动清单

### 新增 3 个文件

| 文件 | 职责 |
|---|---|
| `site/lib/dingtalk.js` | 钉钉接口封装，ESM。导出 `createDingtalk(config)` 工厂返回 `{getAccessToken, getQrConnectUrl, getUserByCode, getUserByAuthCode}` |
| `site/lib/auth-routes.js` | 登录路由注册器 `createAuthRouter(config, dingtalk)`，返回 Express Router |
| `site/public/login.html` | 登录页前端 |

### 改动 3 个文件（最小侵入）

| 文件 | 改动 |
|---|---|
| `site/lib/register-app-routes.js` | 在路由注册开头 `app.use(createAuthRouter(config, dingtalk))` |
| `site/lib/server-config.js` | 新增 `dingtalkAppKey`、`dingtalkAppSecret`、`publicOrigin`、`dingtalkCorpId` 配置项 |
| `site/package.json` | dependencies 加 `axios` |

### 完全不改

`server.js`、`lib/create-app.js`、`lib/auth-session.js`、VitePress config（LOCKED）、theme、admin。

## 5. 模块设计细节

### 5.1 `lib/dingtalk.js`

从 houpe-auth/dingtalk.js 移植，两处适配：

1. **CommonJS → ESM**：`require('axios')` → `import axios`；`module.exports` → `export`
2. **凭证注入**：不直接读 `process.env`，改为工厂函数 `createDingtalk(config)` 接收 `{appKey, appSecret}`，与现有 `createSessionMiddleware(config)` 风格一致，便于测试 mock

```javascript
import axios from 'axios';

export function createDingtalk({ appKey, appSecret }) {
  let tokenCache = { token: null, expires: 0 };

  async function getAccessToken() { /* 同 houpe-auth */ }
  function getQrConnectUrl(redirectUri, state) { /* 同 houpe-auth */ }
  async function getUserByCode(code) { /* 同 houpe-auth，含 unionId 富化 */ }
  async function getUserByAuthCode(authCode) { /* 同 houpe-auth topapi 路径 */ }

  return { getAccessToken, getQrConnectUrl, getUserByCode, getUserByAuthCode };
}
```

钉钉 API 端点（照搬 houpe-auth）：
- `https://oapi.dingtalk.com/gettoken` — 企业 access_token
- `https://api.dingtalk.com/v1.0/oauth2/userAccessToken` — code 换 accessToken（OAuth2 v1.0）
- `https://api.dingtalk.com/v1.0/contact/users/me` — 用户基本信息
- `https://oapi.dingtalk.com/topapi/user/getbyunionid` — unionId → userId
- `https://oapi.dingtalk.com/topapi/v2/user/getuserinfo` — authCode → userId（App内）
- `https://oapi.dingtalk.com/topapi/v2/user/get` — userId → 完整用户信息

`normalizeError(err)` 照搬：`AccessTokenPermissionDenied` → "无权限访问钉钉应用"；`invalid code` → "授权码已过期"。

### 5.2 `lib/auth-routes.js`

```javascript
import { Router } from 'express';
import crypto from 'node:crypto';
import { join } from 'node:path';

export function createAuthRouter(config, dingtalk) {
  const router = Router();
  const loginStates = new Map(); // state -> {redirect, expires}

  // 已登录则直接跳转 redirect；否则返回登录页
  router.get('/auth/login', (req, res) => { /* ... */ });

  // 生成 state + 返回钉钉扫码 URL
  router.get('/api/auth/dingtalk/url', (req, res) => { /* ... */ });

  // OAuth2 回调：校验 state → getUserByCode → 写 session → save → redirect
  router.get('/api/auth/dingtalk/callback', async (req, res) => { /* ... */ });

  // 钉钉 App 内自动登录
  router.post('/api/auth/dingtalk/auto', async (req, res) => { /* ... */ });

  // 登录页读取 corpId（只读公开）
  router.get('/api/auth/config/public', (_req, res) => {
    res.json({ corpId: config.dingtalkCorpId || '' });
  });

  return router;
}
```

#### 关键实现要点

**state CSRF 保护**：
```javascript
const state = crypto.randomBytes(16).toString('hex');
loginStates.set(state, { redirect, expires: Date.now() + 5 * 60 * 1000 });
setTimeout(() => loginStates.delete(state), 5 * 60 * 1000);
```
回调时 `loginStates.delete(state)` 单次使用，不存在或已过期返回 400。

**session 写入坑（houpe-auth 坑 #5）**：必须 `req.session.save(cb)` 完成后再 redirect，否则 Redis 异步写未完成就跳走，目标页仍判为未登录：
```javascript
req.session.user = { id, name, avatar, mobile, unionId };
req.session.save((err) => {
  if (err) console.error('[auth] session save error:', err.message);
  res.redirect(saved.redirect);
});
```

**session.user 结构**：`{ id, name, avatar, mobile, unionId }` —— 与现有测试 `register-app-routes.test.js` 用的 `{id:'ding-user-1', name:'测试用户'}` 兼容（多余字段无害）。

**回调 URL 拼接**：用 `config.publicOrigin`：
```javascript
const callbackUrl = `${config.publicOrigin}/api/auth/dingtalk/callback`;
```

### 5.3 `public/login.html`

从 houpe-auth/public/login.html 移植，改动：

1. **标题**：`产品部统一认证` → `中通冷链文档`；副标题改为 `操作手册 · 请使用钉钉登录`
2. **BASE 常量**：`''`（本站根路径，无 nginx 子路径挂载）
3. **接口路径**：`/api/dingtalk/url` → `/api/auth/dingtalk/url`；`/api/dingtalk/auto` → `/api/auth/dingtalk/auto`
4. **去掉 `/api/config/public` 远程加载的多系统切换展示**：本站无多系统列表。标题/副标题直接写死（"中通冷链文档" / "操作手册 · 请使用钉钉登录"）。
5. **登录页 footer**：改为"中通冷链"
6. **corpId 来源**：页面加载时 fetch `GET /api/auth/config/public`（见 §5.2 新增端点）获取 `config.dingtalkCorpId`，避免硬编码；取不到则回退默认值 `dingj7jagakjrccgceq3`（与 houpe-auth 一致）。该端点成本极低且只读公开。

### 5.4 `lib/server-config.js` 改动

新增配置项（从环境变量读，带默认值）：
```javascript
dingtalkAppKey = process.env.DINGTALK_APP_KEY || '',
dingtalkAppSecret = process.env.DINGTALK_APP_SECRET || '',
publicOrigin = process.env.PUBLIC_ORIGIN || 'https://help.beta.ztocc.com',
dingtalkCorpId = process.env.DINGTALK_CORP_ID || '',
```

加到返回对象中。其余配置不动。

### 5.5 `lib/register-app-routes.js` 改动

在文件顶部 import：
```javascript
import { createDingtalk } from './dingtalk.js';
import { createAuthRouter } from './auth-routes.js';
```

在 `registerAppRoutes` 函数体开头（所有路由注册之前）：
```javascript
const dingtalk = createDingtalk({
  appKey: config.dingtalkAppKey,
  appSecret: config.dingtalkAppSecret,
});
app.use(createAuthRouter(config, dingtalk));
```

现有 `/api/auth/check`、`/api/auth/me`、`/api/logout` 端点保持不变（它们与 auth-routes 路由不冲突）。

### 5.6 `package.json` 改动

dependencies 新增：`"axios": "^1.7.0"`

## 6. 配置与部署

### 新增环境变量（写入 `site/.env.example`）

```
# 钉钉鉴权
DINGTALK_APP_KEY=           # 钉钉企业应用 AppKey
DINGTALK_APP_SECRET=        # 钉钉企业应用 AppSecret
DINGTALK_CORP_ID=           # 企业 corpId（App内自动登录用，可选）
PUBLIC_ORIGIN=https://help.beta.ztocc.com   # 拼接钉钉回调URL

# Session（沿用现有）
SESSION_SECRET=             # session 签名密钥（必须设置，勿用默认值）
AUTH_REQUIRED=true          # 默认开启鉴权

# Redis（可选，配置即启用）
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=2
```

### 钉钉开放平台操作

应用「登录回调地址」白名单加入：`https://help.beta.ztocc.com/api/auth/dingtalk/callback`

### 部署到 help.beta.ztocc.com

服务器（`root@121.199.175.111`）需：
1. 安装 Redis（若要用 Redis session）
2. 配置 `.env`（DINGTALK_*、SESSION_SECRET、PUBLIC_ORIGIN、REDIS_*）
3. `npm install`（装 axios）
4. 重启 Node 服务（现有 admin 控制台的部署任务不涉及 auth 代码改动，正常 `docs-deploy-beta` 部署静态产物后，服务端代码需单独 `git pull` + 重启）

> **注意**：现有部署任务 `admin-tasks.js` 只部署 VitePress 静态 dist（tar+scp+解压），不部署 Express 服务端代码。本次新增的 `lib/dingtalk.js`、`lib/auth-routes.js`、`public/login.html` 需在服务器上 `git pull` 后重启 `node server.js`。部署文档需补充说明。

## 7. 安全考量

- **trust proxy: 1 + cookie.secure: false**：保持不变。help.beta.ztocc.com 走 nginx TLS 终止，Express 在内网，secure:false 正确
- **session 防篡改**：cookie 由 express-session 用 SESSION_SECRET 做 HMAC 签名，必须设置强随机 SESSION_SECRET（勿用默认 `houpe-auth-dev-secret`）
- **CSRF（OAuth state）**：随机 16 字节 hex，内存 Map，5分钟过期，单次使用
- **开放重定向防护**：回调后 redirect 取自 loginStates（服务端存储），非用户可控参数；登录页的 redirect 参数仅用于前端跳转，服务端 callback 只信任 state 绑定的值
- **全企业成员可访问**：登录成功即放行，无白名单。`isAdmin` 等管理逻辑不在本次范围

## 8. 测试策略

现有测试 `tests/register-app-routes.test.js` 已覆盖鉴权闸门（未登录 302、已登录 200）。新增测试 `tests/auth-routes.test.js` 覆盖：

1. **`/auth/login` 已登录 → 302 redirect**：mock session.user 存在
2. **`/auth/login` 未登录 → 200 返回登录页 HTML**
3. **`/api/auth/dingtalk/url` → 返回含 state 的钉钉 URL**：mock dingtalk.getQrConnectUrl
4. **`/api/auth/dingtalk/callback` 有效 state → 写 session + 302**：mock dingtalk.getUserByCode
5. **`/api/auth/dingtalk/callback` 无效/过期 state → 400**
6. **`/api/auth/dingtalk/callback` 钉钉接口失败 → 302 带 #login-error**
7. **`/api/auth/dingtalk/auto` 成功 → 写 session + 200 {success,user}**
8. **`/api/auth/dingtalk/auto` 缺 authCode → 400**

测试用依赖注入：`createAuthRouter(config, mockDingtalk)`，mock dingtalk 的各方法返回固定 user。session 用 memory store（现有测试模式）。

## 9. 验收标准

- [ ] 未登录访问任意文档页 → 302 跳 `/auth/login`
- [ ] `/auth/login` 展示钉钉登录页
- [ ] 点击登录 → 跳钉钉扫码 → 回调后登录成功 → 跳回原页面
- [ ] 钉钉 App 内打开 → 自动登录
- [ ] `/api/auth/check` 登录后返回 `{loggedIn:true, user:{...}}`
- [ ] `/api/logout` 后重新变为未登录
- [ ] Redis 配置时 session 持久化（重启服务不丢登录态，7天有效）
- [ ] 不配 Redis 时回退内存存储，功能正常
- [ ] `npm test` 全绿（含新增 auth-routes 测试）
