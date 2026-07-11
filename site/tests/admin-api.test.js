import test from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import { createApp } from '../lib/create-app.js';
import { buildServerConfig } from '../lib/server-config.js';
import { registerAppRoutes } from '../lib/register-app-routes.js';

function createAdminApiApp({ remoteAddress, taskCatalog, taskRunner } = {}) {
  const config = buildServerConfig({ cwd: process.cwd() });
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

      registerAppRoutes(app, { ...context, taskCatalog, taskRunner });
    },
  });
}

const COMPOSITE_TASK_RESPONSES = [
  {
    key: 'content-flow',
    label: '第一步：文档生成流程',
    description:
      '钉钉拉取 → 过滤并优化，产出 output 和 output_optimized；不会修改 site/docs、构建站点或部署。',
  },
  {
    key: 'local-site-flow',
    label: '第二步：本地站点流程',
    description:
      '读取 output_optimized，生成 site/docs、侧边栏和 dist；通过本机 4000 端口预览，不会部署服务器。',
  },
  {
    key: 'deploy-flow',
    label: '第三步：部署到服务器',
    description:
      '部署当前 site/docs/.vitepress/dist，完成远端备份与覆盖后校验线上首页；不会重新抓取或构建。',
  },
  {
    key: 'full-release-flow',
    label: '全量一键流程',
    description:
      '依次执行文档生成、本地站点构建、服务器部署和线上校验；任一步失败即停止。',
  },
];

test('GET /api/admin/tasks returns public labels and descriptions without execution details', async () => {
  const taskCatalog = Object.freeze({
    'docs-build': Object.freeze({
      key: 'docs-build',
      label: '构建站点',
      description: '构建当前文档，不部署。',
      command: 'npm',
      args: Object.freeze(['run', 'build']),
      cwd: '/tmp/example-site',
    }),
  });
  const taskRunner = {
    getStatus() {
      return { running: false, activeTask: null, lastTask: null };
    },
    getLogs() {
      return ['build ok'];
    },
    start() {
      throw new Error('should not start');
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createAdminApiApp({ taskCatalog, taskRunner });

  const response = await request(app).get('/api/admin/tasks');

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, [
    { key: 'docs-build', label: '构建站点', description: '构建当前文档，不部署。' },
    ...COMPOSITE_TASK_RESPONSES,
  ]);
  assert.equal(
    response.body.every(
      (task) => Object.keys(task).sort().join(',') === 'description,key,label',
    ),
    true,
  );
});

test('GET /api/admin/tasks includes planned one-click flow entries for the admin page', async () => {
  const taskCatalog = Object.freeze({
    'pipeline-crawl': Object.freeze({
      key: 'pipeline-crawl',
      label: 'Pipeline 抓取',
      description: '抓取钉钉文档。',
      command: 'python3',
      args: Object.freeze(['src/dws_crawler.py']),
      cwd: '/tmp/example-project',
    }),
    'content-generate': Object.freeze({
      key: 'content-generate',
      label: '过滤并优化文档',
      description: '生成优化结果。',
      command: 'python3',
      args: Object.freeze(['src/pipeline.py', '--source', './output', '--content-only']),
      cwd: '/tmp/example-project',
    }),
  });
  const taskRunner = {
    getStatus() {
      return { running: false, activeTask: null, lastTask: null };
    },
    getLogs() {
      return [];
    },
    start() {
      throw new Error('should not start');
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createAdminApiApp({ taskCatalog, taskRunner });

  const response = await request(app).get('/api/admin/tasks');

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, [
    { key: 'pipeline-crawl', label: 'Pipeline 抓取', description: '抓取钉钉文档。' },
    { key: 'content-generate', label: '过滤并优化文档', description: '生成优化结果。' },
    ...COMPOSITE_TASK_RESPONSES,
  ]);
});

test('GET /api/admin/status returns idle state', async () => {
  const taskRunner = {
    getStatus() {
      return { running: false, activeTask: null, lastTask: null };
    },
    getLogs() {
      return [];
    },
    start() {
      throw new Error('should not start');
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createAdminApiApp({ taskCatalog: Object.freeze({}), taskRunner });

  const response = await request(app).get('/api/admin/status');

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, { running: false, activeTask: null, lastTask: null });
});

test('GET /api/admin/logs returns the current log list', async () => {
  const taskRunner = {
    getStatus() {
      return { running: true, activeTask: { id: 'run-1' }, lastTask: null };
    },
    getLogs() {
      return ['line 1', 'line 2'];
    },
    start() {
      throw new Error('should not start');
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createAdminApiApp({ taskCatalog: Object.freeze({}), taskRunner });

  const response = await request(app).get('/api/admin/logs');

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, ['line 1', 'line 2']);
});

test('POST /api/admin/tasks/:taskKey starts a task and returns run info', async () => {
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
      return {
        running: true,
        activeTask: {
          id: 'run-1',
          key: 'docs-build',
          label: '构建站点',
          command: 'npm',
          args: ['run', 'build'],
          cwd: '/tmp/example-site',
          status: 'running',
          startedAt: '2026-07-10T10:00:00.000Z',
          finishedAt: null,
          exitCode: null,
          logs: [],
          error: null,
        },
        lastTask: null,
      };
    },
    getLogs() {
      return ['building'];
    },
    start(definition) {
      starts.push(definition);
      return { runId: 'run-1', completed: Promise.resolve() };
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createAdminApiApp({ taskCatalog, taskRunner });

  const response = await request(app).post('/api/admin/tasks/docs-build').send({});

  assert.equal(response.status, 202);
  assert.deepEqual(response.body, {
    ok: true,
    runId: 'run-1',
    status: {
      running: true,
      activeTask: {
        id: 'run-1',
        key: 'docs-build',
        label: '构建站点',
        command: 'npm',
        args: ['run', 'build'],
        cwd: '/tmp/example-site',
        status: 'running',
        startedAt: '2026-07-10T10:00:00.000Z',
        finishedAt: null,
        exitCode: null,
        logs: [],
        error: null,
      },
      lastTask: null,
    },
  });
  assert.deepEqual(starts, [
    {
      key: 'docs-build',
      label: '构建站点',
      command: 'npm',
      args: ['run', 'build'],
      cwd: '/tmp/example-site',
    },
  ]);
});

test('POST /api/admin/tasks/:taskKey consumes the completed promise to avoid unhandled rejections', async () => {
  const taskCatalog = Object.freeze({
    'docs-build': Object.freeze({
      key: 'docs-build',
      label: '构建站点',
      command: 'npm',
      args: Object.freeze(['run', 'build']),
      cwd: '/tmp/example-site',
    }),
  });
  let catchAttached = false;
  const taskRunner = {
    getStatus() {
      return { running: true, activeTask: { id: 'run-1' }, lastTask: null };
    },
    getLogs() {
      return [];
    },
    start() {
      return {
        runId: 'run-1',
        completed: {
          catch(handler) {
            catchAttached = typeof handler === 'function';
            return Promise.resolve();
          },
        },
      };
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createAdminApiApp({ taskCatalog, taskRunner });

  const response = await request(app).post('/api/admin/tasks/docs-build').send({});

  assert.equal(response.status, 202);
  assert.equal(catchAttached, true);
});

test('POST /api/admin/tasks/:taskKey uses the configured composite label and consumes completion', async () => {
  const taskCatalog = Object.freeze({
    'docs-sidebar': Object.freeze({
      key: 'docs-sidebar',
      label: '刷新侧边栏',
      command: 'python3',
      args: Object.freeze(['../src/gen_sidebar.py', 'docs']),
      cwd: '/tmp/example-site',
    }),
    'docs-build': Object.freeze({
      key: 'docs-build',
      label: '构建站点',
      command: 'npm',
      args: Object.freeze(['run', 'build']),
      cwd: '/tmp/example-site',
    }),
    'deploy-site-dist': Object.freeze({
      key: 'deploy-site-dist',
      label: '部署站点 dist',
      command: 'bash',
      args: Object.freeze(['-lc', 'deploy']),
      cwd: '/tmp/example-project',
    }),
    'verify-online': Object.freeze({
      key: 'verify-online',
      label: '校验线上站点',
      command: 'bash',
      args: Object.freeze(['-lc', 'verify']),
      cwd: '/tmp/example-project',
    }),
  });
  const starts = [];
  let catchAttached = false;
  const taskRunner = {
    getStatus() {
      return { running: true, activeTask: { id: 'run-1', key: 'deploy-flow' }, lastTask: null };
    },
    getLogs() {
      return [];
    },
    startComposite(definition) {
      starts.push(definition);
      return {
        runId: 'run-1',
        completed: {
          catch(handler) {
            catchAttached = typeof handler === 'function';
            return Promise.resolve();
          },
        },
      };
    },
    start() {
      throw new Error('should not start a single task');
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createAdminApiApp({ taskCatalog, taskRunner });

  const response = await request(app).post('/api/admin/tasks/deploy-flow').send({});

  assert.equal(response.status, 202);
  assert.equal(response.body.runId, 'run-1');
  assert.equal(catchAttached, true);
  assert.deepEqual(starts, [
    {
      key: 'deploy-flow',
      label: '第三步：部署到服务器',
      steps: ['validate-site-dist', 'deploy-site-dist', 'verify-online'],
      catalog: taskCatalog,
    },
  ]);
});

test('POST /api/admin/tasks/:taskKey returns 404 for unknown tasks', async () => {
  const taskRunner = {
    getStatus() {
      return { running: false, activeTask: null, lastTask: null };
    },
    getLogs() {
      return [];
    },
    start() {
      throw new Error('should not start');
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createAdminApiApp({ taskCatalog: Object.freeze({}), taskRunner });

  const response = await request(app).post('/api/admin/tasks/missing').send({});

  assert.equal(response.status, 404);
  assert.deepEqual(response.body, { error: '任务不存在' });
});

test('POST /api/admin/stop stops the current task', async () => {
  const taskRunner = {
    getStatus() {
      return { running: true, activeTask: { id: 'run-1' }, lastTask: null };
    },
    getLogs() {
      return ['building'];
    },
    start() {
      throw new Error('should not start');
    },
    stop() {
      return {
        id: 'run-1',
        key: 'docs-build',
        label: '构建站点',
        command: 'npm',
        args: ['run', 'build'],
        cwd: '/tmp/example-site',
        status: 'stopped',
        startedAt: '2026-07-10T10:00:00.000Z',
        finishedAt: '2026-07-10T10:01:00.000Z',
        exitCode: null,
        logs: ['building'],
        error: null,
      };
    },
  };
  const app = createAdminApiApp({ taskCatalog: Object.freeze({}), taskRunner });

  const response = await request(app).post('/api/admin/stop').send({});

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, {
    ok: true,
    task: {
      id: 'run-1',
      key: 'docs-build',
      label: '构建站点',
      command: 'npm',
      args: ['run', 'build'],
      cwd: '/tmp/example-site',
      status: 'stopped',
      startedAt: '2026-07-10T10:00:00.000Z',
      finishedAt: '2026-07-10T10:01:00.000Z',
      exitCode: null,
      logs: ['building'],
      error: null,
    },
  });
});

test('admin api returns conflict when the runner cannot start or stop tasks', async () => {
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
      return { running: false, activeTask: null, lastTask: null };
    },
    getLogs() {
      return [];
    },
    start() {
      throw new Error('已有任务正在运行');
    },
    stop() {
      throw new Error('当前没有运行中的任务');
    },
  };
  const app = createAdminApiApp({ taskCatalog, taskRunner });

  const startResponse = await request(app).post('/api/admin/tasks/docs-build').send({});
  const stopResponse = await request(app).post('/api/admin/stop').send({});

  assert.equal(startResponse.status, 409);
  assert.deepEqual(startResponse.body, { error: '已有任务正在运行' });
  assert.equal(stopResponse.status, 409);
  assert.deepEqual(stopResponse.body, { error: '当前没有运行中的任务' });
});

test('admin api rejects non-local access', async () => {
  const app = createAdminApiApp({ remoteAddress: '10.20.30.40' });

  const tasksResponse = await request(app).get('/api/admin/tasks');

  assert.equal(tasksResponse.status, 403);
  assert.deepEqual(tasksResponse.body, { error: '仅允许本机访问' });
});

test('admin api rejects proxied remote requests even when the socket address is loopback', async () => {
  const app = createAdminApiApp({ remoteAddress: '127.0.0.1' });

  const tasksResponse = await request(app)
    .get('/api/admin/tasks')
    .set('x-forwarded-for', '203.0.113.10');

  assert.equal(tasksResponse.status, 403);
  assert.deepEqual(tasksResponse.body, { error: '仅允许本机访问' });
});

test('admin api rejects cross-site task requests before starting a process', async () => {
  let starts = 0;
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
      return { running: false, activeTask: null, lastTask: null };
    },
    getLogs() {
      return [];
    },
    start() {
      starts += 1;
      return { runId: 'run-1', completed: Promise.resolve() };
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createAdminApiApp({ taskCatalog, taskRunner });

  const response = await request(app)
    .post('/api/admin/tasks/docs-build')
    .set('Origin', 'https://evil.example')
    .send({});
  const fetchMetadataResponse = await request(app)
    .post('/api/admin/tasks/docs-build')
    .set('Sec-Fetch-Site', 'cross-site')
    .send({});

  assert.equal(response.status, 403);
  assert.deepEqual(response.body, { error: '仅允许本机访问' });
  assert.equal(fetchMetadataResponse.status, 403);
  assert.equal(starts, 0);
});

test('admin api accepts a loopback origin and rejects a non-loopback host', async () => {
  const taskRunner = {
    getStatus() {
      return { running: false, activeTask: null, lastTask: null };
    },
    getLogs() {
      return [];
    },
    start() {
      throw new Error('should not start');
    },
    stop() {
      throw new Error('should not stop');
    },
  };
  const app = createAdminApiApp({ taskCatalog: Object.freeze({}), taskRunner });

  const localOriginResponse = await request(app)
    .get('/api/admin/tasks')
    .set('Origin', 'http://127.0.0.1:4000');
  const remoteHostResponse = await request(app)
    .get('/api/admin/tasks')
    .set('Host', 'evil.example');

  assert.equal(localOriginResponse.status, 200);
  assert.equal(remoteHostResponse.status, 403);
});
