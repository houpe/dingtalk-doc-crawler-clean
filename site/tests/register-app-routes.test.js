import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import request from 'supertest';
import { createApp } from '../lib/create-app.js';
import { buildServerConfig } from '../lib/server-config.js';
import { registerAppRoutes } from '../lib/register-app-routes.js';

const TEST_USER = Object.freeze({ id: 'ding-user-1', name: '测试用户' });

function createTestApp({ cwd = process.cwd(), remoteAddress, taskCatalog, taskRunner, user } = {}) {
  const config = buildServerConfig({ cwd, sessionStore: 'memory' });
  return createApp({
    config,
    registerRoutes(app, context) {
      if (remoteAddress) {
        app.use((req, _res, next) => {
          Object.defineProperty(req.socket, 'remoteAddress', {
            value: remoteAddress,
            configurable: true,
          });
          next();
        });
      }

      if (user) {
        app.use((req, _res, next) => {
          req.session.user = user;
          next();
        });
      }

      registerAppRoutes(app, { ...context, taskCatalog, taskRunner });
    },
  });
}

function createStaticSiteFixture(t) {
  const cwd = mkdtempSync(join(tmpdir(), 'zto-docs-site-'));
  const distDir = join(cwd, 'docs', '.vitepress', 'dist');

  mkdirSync(join(distDir, 'guide'), { recursive: true });
  writeFileSync(join(distDir, 'index.html'), '<!doctype html><title>ROOT</title>ROOT');
  writeFileSync(join(distDir, '404.html'), '<!doctype html><title>NOT FOUND</title>NOT FOUND');
  writeFileSync(join(distDir, 'guide', 'index.html'), '<!doctype html><title>GUIDE</title>GUIDE');
  writeFileSync(join(distDir, 'guide', 'topic.html'), '<!doctype html><title>TOPIC</title>TOPIC');

  t.after(() => rmSync(cwd, { recursive: true, force: true }));

  return cwd;
}

test('registerAppRoutes redirects anonymous VitePress requests to central auth', async (t) => {
  const app = createTestApp({ cwd: createStaticSiteFixture(t) });

  const response = await request(app).get('/guide/topic');

  assert.equal(response.status, 302);
  assert.equal(response.headers.location, '/auth/login?redirect=%2Fguide%2Ftopic');
});

test('registerAppRoutes serves generated VitePress clean URLs for authenticated users', async (t) => {
  const app = createTestApp({ cwd: createStaticSiteFixture(t), user: TEST_USER });

  const pageResponse = await request(app).get('/guide/topic');
  const sectionResponse = await request(app).get('/guide/');
  const missingResponse = await request(app).get('/missing');

  assert.equal(pageResponse.status, 200);
  assert.match(pageResponse.text, /TOPIC/);
  assert.doesNotMatch(pageResponse.text, /ROOT/);

  assert.equal(sectionResponse.status, 200);
  assert.match(sectionResponse.text, /GUIDE/);

  assert.equal(missingResponse.status, 404);
  assert.match(missingResponse.text, /NOT FOUND/);
});

test('registerAppRoutes serves the admin console shell at /admin', async () => {
  const app = createTestApp();

  const response = await request(app).get('/admin');

  assert.equal(response.status, 200);
  assert.match(response.headers['content-type'], /text\/html/);
  assert.match(response.text, /文档控制台/);
  assert.match(response.text, /当前状态/);
  assert.match(response.text, /运行日志/);
});

test('registerAppRoutes reports anonymous auth state as logged out', async () => {
  const app = createTestApp();

  const response = await request(app).get('/api/auth/check');

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, { loggedIn: false });
});

test('registerAppRoutes reports central session auth state as logged in', async () => {
  const app = createTestApp({ user: TEST_USER });

  const response = await request(app).get('/api/auth/me');

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, { loggedIn: true, user: TEST_USER });
});

test('registerAppRoutes rejects non-local access to /admin and /api/admin/tasks', async () => {
  const app = createTestApp({ remoteAddress: '10.20.30.40' });

  const adminResponse = await request(app).get('/admin');
  const tasksResponse = await request(app).get('/api/admin/tasks');

  assert.equal(adminResponse.status, 403);
  assert.match(adminResponse.text, /仅允许本机访问/);
  assert.equal(tasksResponse.status, 403);
  assert.deepEqual(tasksResponse.body, { error: '仅允许本机访问' });
});

test('registerAppRoutes rejects proxied remote access to /admin even when the socket address is loopback', async () => {
  const app = createTestApp({ remoteAddress: '127.0.0.1' });

  const response = await request(app)
    .get('/admin')
    .set('x-forwarded-for', '198.51.100.20');

  assert.equal(response.status, 403);
  assert.match(response.text, /仅允许本机访问/);
});

test('legacy editor build endpoint uses the shared task runner lock', async () => {
  const taskCatalog = Object.freeze({
    'docs-build': Object.freeze({
      key: 'docs-build',
      label: '构建站点',
      command: 'npm',
      args: Object.freeze(['run', 'build']),
      cwd: '/tmp/example-site',
    }),
  });
  const starts = [];
  const taskRunner = {
    getStatus() {
      return { running: false, activeTask: null, lastTask: null };
    },
    getLogs() {
      return [];
    },
    start(task) {
      starts.push(task);
      return { runId: 'run-1', completed: Promise.resolve() };
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createTestApp({ taskCatalog, taskRunner, user: TEST_USER });

  const response = await request(app).post('/api/build').send({});

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, { ok: true, message: '构建已启动', runId: 'run-1' });
  assert.deepEqual(starts, [taskCatalog['docs-build']]);
});

test('legacy editor build endpoint returns conflict when another task holds the runner lock', async () => {
  const taskCatalog = Object.freeze({
    'docs-build': Object.freeze({
      key: 'docs-build',
      label: '构建站点',
      command: 'npm',
      args: Object.freeze(['run', 'build']),
      cwd: '/tmp/example-site',
    }),
  });
  const taskRunner = {
    getStatus() {
      return { running: true, activeTask: { id: 'run-1' }, lastTask: null };
    },
    getLogs() {
      return [];
    },
    start() {
      throw new Error('已有任务正在运行');
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createTestApp({ taskCatalog, taskRunner, user: TEST_USER });

  const response = await request(app).post('/api/build').send({});

  assert.equal(response.status, 409);
  assert.deepEqual(response.body, { error: '已有任务正在运行' });
});
