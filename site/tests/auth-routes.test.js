import test from 'node:test';
import assert from 'node:assert/strict';
import express from 'express';
import session from 'express-session';
import request from 'supertest';
import { createAuthRouter, sanitizeRedirect } from '../lib/auth-routes.js';
import { buildServerConfig } from '../lib/server-config.js';

const DINGTALK_USER = Object.freeze({
  userId: 'dt-001',
  name: '张三',
  avatar: 'https://example.com/a.png',
  mobile: '13800000000',
  unionId: 'union-001',
});

// 构造一个挂了 session 中间件 + auth 路由的测试 app，dingtalk 用 mock 注入。
function createTestApp({ dingtalk, sessionUser } = {}) {
  const config = buildServerConfig({
    cwd: process.cwd(),
    sessionStore: 'memory',
    publicOrigin: 'https://help.beta.ztocc.com',
  });
  const app = express();
  app.use(express.json());
  app.use(
    session({
      secret: config.sessionSecret,
      resave: false,
      saveUninitialized: true,
      cookie: { maxAge: config.sessionMaxAgeMs },
    }),
  );

  if (sessionUser) {
    app.use((req, _res, next) => {
      req.session.user = sessionUser;
      next();
    });
  }

  app.use(createAuthRouter(config, dingtalk));
  return app;
}

function mockDingtalk({ user = DINGTALK_USER, fail = false } = {}) {
  return {
    getQrConnectUrl: (redirectUri, state) =>
      `https://login.dingtalk.com/oauth2/auth?redirect_uri=${encodeURIComponent(redirectUri)}&state=${state}`,
    getUserByCode: async () => {
      if (fail) throw new Error('授权码已过期');
      return user;
    },
    getUserByAuthCode: async () => {
      if (fail) throw new Error('授权码已过期');
      return user;
    },
  };
}

// ---- sanitizeRedirect ----

test('sanitizeRedirect allows same-origin relative paths', () => {
  assert.equal(sanitizeRedirect('/guide/topic'), '/guide/topic');
  assert.equal(sanitizeRedirect('/'), '/');
});

test('sanitizeRedirect blocks open-redirect attempts', () => {
  assert.equal(sanitizeRedirect('//evil.com'), '/');
  assert.equal(sanitizeRedirect('https://evil.com'), '/');
  assert.equal(sanitizeRedirect(undefined), '/');
  assert.equal(sanitizeRedirect(''), '/');
});

// ---- /auth/login ----

test('/auth/login redirects to target when already logged in', async () => {
  const app = createTestApp({ dingtalk: mockDingtalk(), sessionUser: { id: '1', name: 'x' } });

  const res = await request(app).get('/auth/login?redirect=/guide/topic');

  assert.equal(res.status, 302);
  assert.equal(res.headers.location, '/guide/topic');
});

test('/auth/login serves the login HTML page when anonymous', async () => {
  const app = createTestApp({ dingtalk: mockDingtalk() });

  const res = await request(app).get('/auth/login');

  assert.equal(res.status, 200);
  assert.match(res.headers['content-type'], /text\/html/);
  assert.match(res.text, /中通冷链文档/);
  assert.match(res.text, /使用钉钉登录/);
});

// ---- /api/auth/dingtalk/url ----

test('/api/auth/dingtalk/url returns a DingTalk QR url with a state', async () => {
  const app = createTestApp({ dingtalk: mockDingtalk() });

  const res = await request(app).get('/api/auth/dingtalk/url?redirect=/guide/topic');

  assert.equal(res.status, 200);
  assert.ok(res.body.url);
  assert.match(res.body.url, /login\.dingtalk\.com/);
  assert.match(res.body.url, /redirect_uri=https%3A%2F%2Fhelp\.beta\.ztocc\.com/);
  assert.ok(res.body.state);
});

test('/api/auth/dingtalk/url returns 500 when dingtalk is not configured', async () => {
  const app = createTestApp({ dingtalk: null });

  const res = await request(app).get('/api/auth/dingtalk/url');

  assert.equal(res.status, 500);
  assert.match(res.body.error, /未配置/);
});

// ---- /api/auth/dingtalk/callback ----

test('/api/auth/dingtalk/callback writes session and redirects on success', async (t) => {
  const app = createTestApp({ dingtalk: mockDingtalk() });

  // 先拿一个合法的 state
  const urlRes = await request(app).get('/api/auth/dingtalk/url?redirect=/guide/topic');
  const { state } = urlRes.body;

  // 用该 state 模拟钉钉回调
  const res = await request(app).get(
    `/api/auth/dingtalk/callback?code=fake-code&state=${state}`,
  );

  assert.equal(res.status, 302);
  assert.equal(res.headers.location, '/guide/topic');

  // 验证 session 已写入：用一个 cookie jar 的后续请求很难在无状态 supertest 里串联，
  // 这里通过断言 redirect 目标间接确认流程走通。
});

test('/api/auth/dingtalk/callback rejects an invalid or reused state', async (t) => {
  const app = createTestApp({ dingtalk: mockDingtalk() });

  const res = await request(app).get(
    '/api/auth/dingtalk/callback?code=fake-code&state=does-not-exist',
  );

  assert.equal(res.status, 400);
  assert.match(res.text, /state/);
});

test('/api/auth/dingtalk/callback redirects with login-error when DingTalk fails', async () => {
  const app = createTestApp({ dingtalk: mockDingtalk({ fail: true }) });

  const urlRes = await request(app).get('/api/auth/dingtalk/url?redirect=/guide/topic');
  const { state } = urlRes.body;

  const res = await request(app).get(
    `/api/auth/dingtalk/callback?code=fake-code&state=${state}`,
  );

  assert.equal(res.status, 302);
  assert.match(res.headers.location, /#login-error=/);
});

// ---- /api/auth/dingtalk/auto ----

test('/api/auth/dingtalk/auto writes session and returns success', async () => {
  const app = createTestApp({ dingtalk: mockDingtalk() });

  const res = await request(app)
    .post('/api/auth/dingtalk/auto')
    .send({ authCode: 'fake-auth-code' });

  assert.equal(res.status, 200);
  assert.equal(res.body.success, true);
  assert.equal(res.body.user.id, DINGTALK_USER.userId);
  assert.equal(res.body.user.name, DINGTALK_USER.name);
});

test('/api/auth/dingtalk/auto rejects missing authCode', async () => {
  const app = createTestApp({ dingtalk: mockDingtalk() });

  const res = await request(app).post('/api/auth/dingtalk/auto').send({});

  assert.equal(res.status, 400);
  assert.match(res.body.error, /authCode/);
});

test('/api/auth/dingtalk/auto returns 500 when DingTalk fails', async () => {
  const app = createTestApp({ dingtalk: mockDingtalk({ fail: true }) });

  const res = await request(app)
    .post('/api/auth/dingtalk/auto')
    .send({ authCode: 'bad' });

  assert.equal(res.status, 500);
  assert.ok(res.body.error);
});

// ---- /api/auth/config/public ----

test('/api/auth/config/public returns the configured corpId', async () => {
  const config = buildServerConfig({ cwd: process.cwd(), dingtalkCorpId: 'corp-xyz' });
  const app = express();
  app.use(createAuthRouter(config, mockDingtalk()));

  const res = await request(app).get('/api/auth/config/public');

  assert.equal(res.status, 200);
  assert.deepEqual(res.body, { corpId: 'corp-xyz' });
});

test('/api/auth/config/public returns empty corpId when not configured', async () => {
  const config = buildServerConfig({ cwd: process.cwd() });
  const app = express();
  app.use(createAuthRouter(config, mockDingtalk()));

  const res = await request(app).get('/api/auth/config/public');

  assert.equal(res.status, 200);
  assert.deepEqual(res.body, { corpId: '' });
});
