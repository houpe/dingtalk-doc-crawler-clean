import { Router } from 'express';
import crypto from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const LOGIN_HTML_PATH = join(__dirname, '..', 'public', 'login.html');

const STATE_TTL_MS = 5 * 60 * 1000;

// 钉钉登录路由。移植自 houpe-auth/server.js 的登录部分，改为可注入的 Router，
// 由 register-app-routes.js 挂载。dingtalk 依赖注入便于测试。
export function createAuthRouter(config, dingtalk) {
  const router = Router();
  const loginStates = new Map(); // state -> { redirect, expires }

  // 已登录则直接跳转 redirect；否则返回登录页。
  router.get('/auth/login', (req, res) => {
    const redirect = sanitizeRedirect(req.query.redirect);
    if (req.session?.user) {
      return res.redirect(redirect);
    }
    res.type('text/html').send(readFileSync(LOGIN_HTML_PATH, 'utf-8'));
  });

  // 生成 CSRF state（5分钟TTL，单次使用），返回钉钉扫码 URL。
  router.get('/api/auth/dingtalk/url', (req, res) => {
    if (!dingtalk) {
      return res.status(500).json({ error: '钉钉鉴权未配置' });
    }
    const redirect = sanitizeRedirect(req.query.redirect);
    const state = crypto.randomBytes(16).toString('hex');
    loginStates.set(state, { redirect, expires: Date.now() + STATE_TTL_MS });
    setTimeout(() => loginStates.delete(state), STATE_TTL_MS);

    const callbackUrl = `${config.publicOrigin}/api/auth/dingtalk/callback`;
    res.json({ url: dingtalk.getQrConnectUrl(callbackUrl, state), state });
  });

  // OAuth2 回调：校验 state → getUserByCode → 写 session → save → redirect。
  router.get('/api/auth/dingtalk/callback', async (req, res) => {
    const { code, state } = req.query;
    const saved = loginStates.get(state);
    loginStates.delete(state);
    if (!saved) return res.status(400).send('无效的 state 参数');

    try {
      const user = await dingtalk.getUserByCode(code);
      req.session.user = {
        id: user.userId,
        name: user.name,
        avatar: user.avatar,
        mobile: user.mobile,
        unionId: user.unionId,
      };
      console.log(`[auth] QR login: ${user.name} (${user.userId})`);
      // 必须等 session 落库后再跳转（houpe-auth 坑 #5：Redis 异步写未完成就 redirect）。
      req.session.save((err) => {
        if (err) console.error('[auth] session save error:', err.message);
        res.redirect(saved.redirect);
      });
    } catch (err) {
      console.error('[auth] QR callback error:', err.message);
      res.redirect(`${saved.redirect}#login-error=${encodeURIComponent(err.message)}`);
    }
  });

  // 钉钉 App 内自动登录：requestAuthCode 拿到 authCode，换企业用户。
  router.post('/api/auth/dingtalk/auto', async (req, res) => {
    if (!dingtalk) {
      return res.status(500).json({ error: '钉钉鉴权未配置' });
    }
    const { authCode } = req.body;
    if (!authCode) return res.status(400).json({ error: '缺少 authCode' });

    try {
      const user = await dingtalk.getUserByAuthCode(authCode);
      req.session.user = {
        id: user.userId,
        name: user.name,
        avatar: user.avatar,
        mobile: user.mobile,
        unionId: user.unionId,
      };
      console.log(`[auth] Auto login: ${user.name} (${user.userId})`);
      req.session.save((err) => {
        if (err) console.error('[auth] session save error:', err.message);
        res.json({ success: true, user: req.session.user });
      });
    } catch (err) {
      console.error('[auth] Auto login error:', err.message);
      res.status(500).json({ error: err.message });
    }
  });

  // 登录页读取 corpId（只读公开，App 内自动登录用）。
  router.get('/api/auth/config/public', (_req, res) => {
    res.json({ corpId: config.dingtalkCorpId || '' });
  });

  return router;
}

// 只允许站内相对路径跳转，防止开放重定向。空值/非法值回退首页。
function sanitizeRedirect(value) {
  if (typeof value === 'string' && value.startsWith('/') && !value.startsWith('//')) {
    return value;
  }
  return '/';
}

export { sanitizeRedirect };
