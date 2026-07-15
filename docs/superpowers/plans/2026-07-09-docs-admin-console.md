# Docs Admin Console Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-only `/admin` console in the existing `site` service that can run `site/docs` tasks, `pipeline` tasks, deployment, and online verification with single-task locking and live logs.

**Architecture:** Split the current `site/server.js` into a small boot file plus reusable modules for task definitions, task runner state, deployment helpers, and admin routes. Use fixed task keys mapped to trusted commands, expose JSON APIs for status/logs/task start/stop, and serve a lightweight static admin page from Express. Keep execution local, reserve SSH only for deployment, and gate concurrency with one in-memory active task lock.

**Tech Stack:** Node.js ESM, Express, child_process `spawn`, static HTML/CSS/JS, `node:test`, `supertest`

---

### Task 1: Restructure the `site` server for testable admin modules

**Files:**
- Create: `site/lib/server-config.js`
- Create: `site/lib/create-app.js`
- Modify: `site/server.js`
- Modify: `site/package.json`
- Test: `site/tests/server-config.test.js`

- [ ] **Step 1: Add a test script and HTTP test dependency**

Update [package.json](file:///Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site/package.json) scripts and devDependencies to support Node test execution.

```json
{
  "scripts": {
    "dev": "vitepress dev docs --port 4000",
    "build": "vitepress build docs",
    "docs:sidebar": "python3 ../src/gen_sidebar.py docs",
    "docs:refresh": "npm run docs:sidebar && vitepress build docs",
    "preview": "vitepress preview docs --port 4000",
    "start": "node server.js",
    "test": "node --test tests/*.test.js"
  },
  "devDependencies": {
    "vitepress": "^1.6.0",
    "vue": "^3.5.0",
    "express": "^4.21.0",
    "jsonwebtoken": "^9.0.2",
    "medium-zoom": "^1.1.0",
    "supertest": "^7.1.1"
  }
}
```

- [ ] **Step 2: Install dependencies and verify test runner boots**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm install
npm test
```

Expected: `npm install` succeeds, `npm test` reports no tests or zero failures.

- [ ] **Step 3: Write the failing config test**

Create `site/tests/server-config.test.js`:

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { buildServerConfig } from '../lib/server-config.js';

test('buildServerConfig pins docs and dist directories under site cwd', () => {
  const cwd = '/tmp/example-site';
  const config = buildServerConfig({ cwd, host: '127.0.0.1', port: '4010' });

  assert.equal(config.cwd, cwd);
  assert.equal(config.host, '127.0.0.1');
  assert.equal(config.port, 4010);
  assert.equal(config.docsDir, '/tmp/example-site/docs');
  assert.equal(config.distDir, '/tmp/example-site/docs/.vitepress/dist');
  assert.match(config.projectRoot, /\/tmp$/);
});
```

- [ ] **Step 4: Run the test to confirm it fails**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test -- --test-name-pattern="buildServerConfig"
```

Expected: FAIL with module not found for `../lib/server-config.js`.

- [ ] **Step 5: Implement reusable server config**

Create `site/lib/server-config.js`:

```js
import { join, resolve } from 'path';

export function buildServerConfig({
  cwd = process.cwd(),
  host = process.env.HOST || '127.0.0.1',
  port = process.env.PORT || '4000',
} = {}) {
  const siteCwd = resolve(cwd);
  const docsDir = join(siteCwd, 'docs');
  const distDir = join(docsDir, '.vitepress', 'dist');
  const projectRoot = resolve(siteCwd, '..');

  return {
    cwd: siteCwd,
    host,
    port: parseInt(port, 10),
    docsDir,
    distDir,
    projectRoot,
  };
}
```

- [ ] **Step 6: Extract app bootstrapping**

Create `site/lib/create-app.js`:

```js
import express from 'express';

export function createApp({ config, registerRoutes }) {
  const app = express();
  app.use(express.json({ limit: '10mb' }));

  registerRoutes(app, { config });

  return app;
}
```

Modify `site/server.js` to become a thin boot file:

```js
import { createServer } from 'node:http';
import { buildServerConfig } from './lib/server-config.js';
import { createApp } from './lib/create-app.js';
import { registerAppRoutes } from './lib/register-app-routes.js';

const config = buildServerConfig();
const app = createApp({ config, registerRoutes: registerAppRoutes });
const server = createServer(app);

server.listen(config.port, config.host, () => {
  console.log(`\n   中通冷链文档 - http://${config.host}:${config.port}`);
  console.log(`   管理入口: http://${config.host}:${config.port}/admin`);
  console.log('\n  Ctrl+C 停止\n');
});
```

- [ ] **Step 7: Re-run the focused test**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test -- --test-name-pattern="buildServerConfig"
```

Expected: PASS.

- [ ] **Step 8: Commit the server split baseline**

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean
git add site/package.json site/server.js site/lib/server-config.js site/lib/create-app.js site/tests/server-config.test.js
git commit -m "feat(site): split server bootstrap for admin console"
```

### Task 2: Add fixed admin task definitions and the single-task runner

**Files:**
- Create: `site/lib/admin-tasks.js`
- Create: `site/lib/task-runner.js`
- Create: `site/tests/task-runner.test.js`
- Modify: `site/lib/server-config.js`

- [ ] **Step 1: Write the failing task definition test**

Create `site/tests/task-runner.test.js`:

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { buildServerConfig } from '../lib/server-config.js';
import { createTaskCatalog } from '../lib/admin-tasks.js';

test('task catalog exposes docs, pipeline, deploy and verify commands', () => {
  const config = buildServerConfig({ cwd: '/tmp/site' });
  const catalog = createTaskCatalog(config);

  assert.ok(catalog['docs-refresh']);
  assert.ok(catalog['pipeline-crawl']);
  assert.ok(catalog['deploy-site-dist']);
  assert.ok(catalog['verify-online']);
  assert.equal(catalog['docs-refresh'].cwd, '/tmp/site');
  assert.equal(catalog['pipeline-build'].cwd, '/tmp');
});
```

- [ ] **Step 2: Run the task test and confirm it fails**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test -- --test-name-pattern="task catalog"
```

Expected: FAIL with module not found for `../lib/admin-tasks.js`.

- [ ] **Step 3: Implement trusted task definitions**

Create `site/lib/admin-tasks.js`:

```js
export function createTaskCatalog(config) {
  const deployCommand =
    "tar --no-mac-metadata -C " +
    `${config.distDir} -cf /tmp/help-beta-vitepress.tar . && ` +
    "scp /tmp/help-beta-vitepress.tar root@121.199.175.111:/tmp/help-beta-vitepress.tar && " +
    "ssh root@121.199.175.111 \"mkdir -p /tmp/help-beta-backup && " +
    "tar -C /www/wwwroot/help.beta.ztocc.com -cf /tmp/help-beta-backup/help.beta.ztocc.com-$(date +%Y%m%d%H%M%S).tar --exclude=.well-known . && " +
    "find /www/wwwroot/help.beta.ztocc.com -mindepth 1 -maxdepth 1 ! -name '.well-known' -exec rm -rf {} + && " +
    "tar -C /www/wwwroot/help.beta.ztocc.com -xf /tmp/help-beta-vitepress.tar\"";

  return {
    'docs-sidebar': { key: 'docs-sidebar', label: '生成侧边栏', cwd: config.cwd, command: 'npm', args: ['run', 'docs:sidebar'] },
    'docs-build': { key: 'docs-build', label: '构建站点', cwd: config.cwd, command: 'npm', args: ['run', 'build'] },
    'docs-refresh': { key: 'docs-refresh', label: '一键刷新站点', cwd: config.cwd, command: 'npm', args: ['run', 'docs:refresh'] },
    'pipeline-crawl': { key: 'pipeline-crawl', label: '从钉钉拉取', cwd: config.projectRoot, command: 'python3', args: ['src/dws_crawler.py'] },
    'pipeline-build': { key: 'pipeline-build', label: '执行 pipeline', cwd: config.projectRoot, command: 'python3', args: ['src/pipeline.py', '--source', './output'] },
    'pipeline-deploy-fast': { key: 'pipeline-deploy-fast', label: 'pipeline 快速部署', cwd: config.projectRoot, command: 'python3', args: ['src/pipeline.py', '--source', './output', '--deploy', 'fast'] },
    'deploy-site-dist': { key: 'deploy-site-dist', label: '部署到正式服务器', cwd: config.projectRoot, command: 'bash', args: ['-lc', deployCommand] },
    'verify-online': {
      key: 'verify-online',
      label: '查看线上版本',
      cwd: config.projectRoot,
      command: 'bash',
      args: ['-lc', "curl -s https://help.beta.ztocc.com/ | grep -n '中通冷链\\|操作手册'"],
    },
  };
}
```

- [ ] **Step 4: Write the failing single-task lock test**

Append to `site/tests/task-runner.test.js`:

```js
import { createTaskRunner } from '../lib/task-runner.js';

test('task runner rejects a second task while one is running', async () => {
  const runner = createTaskRunner({
    spawnImpl() {
      return {
        stdout: { on() {} },
        stderr: { on() {} },
        on(event, handler) {
          if (event === 'close') this._close = handler;
        },
        kill() { this.killed = true; },
      };
    },
  });

  runner.start({ key: 'docs-refresh', label: '刷新', cwd: '/tmp', command: 'npm', args: ['run', 'docs:refresh'] });

  assert.throws(
    () => runner.start({ key: 'docs-build', label: '构建', cwd: '/tmp', command: 'npm', args: ['run', 'build'] }),
    /已有任务正在运行/
  );
});
```

- [ ] **Step 5: Run the task runner test and confirm failure**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test -- --test-name-pattern="已有任务正在运行"
```

Expected: FAIL because `createTaskRunner` does not exist yet.

- [ ] **Step 6: Implement the in-memory runner**

Create `site/lib/task-runner.js`:

```js
import { spawn } from 'child_process';

export function createTaskRunner({ spawnImpl = spawn } = {}) {
  let activeTask = null;
  let lastTask = null;
  let activeChild = null;

  function toSnapshot(task) {
    return task ? { ...task, logs: [...task.logs] } : null;
  }

  return {
    getStatus() {
      return {
        activeTask: toSnapshot(activeTask),
        lastTask: toSnapshot(lastTask),
        running: Boolean(activeTask),
      };
    },

    start(definition) {
      if (activeTask) throw new Error('已有任务正在运行');

      const task = {
        id: `task-${Date.now()}`,
        key: definition.key,
        label: definition.label,
        status: 'running',
        startedAt: new Date().toISOString(),
        finishedAt: null,
        exitCode: null,
        logs: [],
      };

      const child = spawnImpl(definition.command, definition.args, {
        cwd: definition.cwd,
        stdio: 'pipe',
        env: { ...process.env },
      });

      activeTask = task;
      activeChild = child;

      child.stdout.on('data', (chunk) => task.logs.push(String(chunk)));
      child.stderr.on('data', (chunk) => task.logs.push(String(chunk)));
      child.on('close', (code) => {
        task.exitCode = code;
        task.finishedAt = new Date().toISOString();
        task.status = code === 0 ? 'success' : 'failed';
        lastTask = task;
        activeTask = null;
        activeChild = null;
      });

      return toSnapshot(task);
    },

    stop() {
      if (!activeTask || !activeChild) throw new Error('当前没有运行中的任务');
      activeChild.kill('SIGTERM');
      activeTask.status = 'stopped';
      activeTask.finishedAt = new Date().toISOString();
      lastTask = activeTask;
      activeTask = null;
      activeChild = null;
    },

    getLogs() {
      return (activeTask || lastTask)?.logs ?? [];
    },
  };
}
```

- [ ] **Step 7: Re-run task tests**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test -- --test-name-pattern="task"
```

Expected: PASS for the task catalog and single-task lock tests.

- [ ] **Step 8: Commit task infrastructure**

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean
git add site/lib/admin-tasks.js site/lib/task-runner.js site/lib/server-config.js site/tests/task-runner.test.js
git commit -m "feat(site): add admin task catalog and runner"
```

### Task 3: Expose admin APIs and local-only access rules

**Files:**
- Create: `site/lib/register-app-routes.js`
- Create: `site/tests/admin-api.test.js`
- Modify: `site/server.js`
- Modify: `site/lib/create-app.js`

- [ ] **Step 1: Write the failing admin status API test**

Create `site/tests/admin-api.test.js`:

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import { createApp } from '../lib/create-app.js';
import { registerAppRoutes } from '../lib/register-app-routes.js';
import { buildServerConfig } from '../lib/server-config.js';

test('GET /api/admin/status returns idle state', async () => {
  const config = buildServerConfig({ cwd: process.cwd() });
  const app = createApp({ config, registerRoutes: registerAppRoutes });

  const response = await request(app).get('/api/admin/status');

  assert.equal(response.status, 200);
  assert.equal(response.body.running, false);
});
```

- [ ] **Step 2: Run the API test and confirm failure**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test -- --test-name-pattern="GET /api/admin/status"
```

Expected: FAIL because `register-app-routes.js` is missing.

- [ ] **Step 3: Implement route registration with fixed admin APIs**

Create `site/lib/register-app-routes.js`:

```js
import { join } from 'path';
import { createTaskCatalog } from './admin-tasks.js';
import { createTaskRunner } from './task-runner.js';

const runner = createTaskRunner();

export function registerAppRoutes(app, { config }) {
  const tasks = createTaskCatalog(config);

  app.get('/api/admin/tasks', (_req, res) => {
    res.json(Object.values(tasks).map(({ key, label }) => ({ key, label })));
  });

  app.get('/api/admin/status', (_req, res) => {
    res.json(runner.getStatus());
  });

  app.get('/api/admin/logs', (_req, res) => {
    res.json({ logs: runner.getLogs() });
  });

  app.post('/api/admin/tasks/:taskKey', (req, res) => {
    const definition = tasks[req.params.taskKey];
    if (!definition) return res.status(404).json({ errorCode: 'TASK_NOT_FOUND', message: '任务不存在' });

    try {
      const task = runner.start(definition);
      res.json({ ok: true, task });
    } catch (error) {
      res.status(409).json({ errorCode: 'TASK_ALREADY_RUNNING', message: error.message });
    }
  });

  app.post('/api/admin/stop', (_req, res) => {
    try {
      runner.stop();
      res.json({ ok: true });
    } catch (error) {
      res.status(409).json({ errorCode: 'NO_ACTIVE_TASK', message: error.message });
    }
  });

  app.get('/admin', (_req, res) => {
    res.sendFile(join(config.cwd, 'admin', 'index.html'));
  });

  app.use(express.static(config.distDir, { index: false }));
  app.use('/admin-static', express.static(join(config.cwd, 'admin')));
  app.use('*', (req, res, next) => {
    if (req.url.startsWith('/api/')) return next();
    res.sendFile(join(config.distDir, 'index.html'));
  });
}
```

Also update `site/lib/create-app.js` to pass the same `app` object into route registration only once:

```js
import express from 'express';

export function createApp({ config, registerRoutes }) {
  const app = express();
  app.use(express.json({ limit: '10mb' }));
  registerRoutes(app, { config, express });
  return app;
}
```

Adjust `register-app-routes.js` signature accordingly:

```js
export function registerAppRoutes(app, { config, express }) {
  // same logic, using provided express
}
```

- [ ] **Step 4: Bind the HTTP server to localhost explicitly**

Ensure `site/server.js` listens with `config.host` where default host is `127.0.0.1`:

```js
server.listen(config.port, config.host, () => {
  console.log(`\n   中通冷链文档 - http://${config.host}:${config.port}`);
  console.log(`   管理入口: http://${config.host}:${config.port}/admin`);
  console.log('\n  Ctrl+C 停止\n');
});
```

- [ ] **Step 5: Re-run the admin API test**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test -- --test-name-pattern="admin"
```

Expected: PASS for idle status response.

- [ ] **Step 6: Commit the admin API slice**

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean
git add site/lib/register-app-routes.js site/lib/create-app.js site/server.js site/tests/admin-api.test.js
git commit -m "feat(site): add admin task APIs"
```

### Task 4: Build the `/admin` page with grouped buttons and live polling

**Files:**
- Create: `site/admin/index.html`
- Create: `site/admin/admin.css`
- Create: `site/admin/admin.js`
- Test: `site/tests/admin-page.test.js`
- Modify: `site/lib/register-app-routes.js`

- [ ] **Step 1: Write the failing admin page smoke test**

Create `site/tests/admin-page.test.js`:

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import { createApp } from '../lib/create-app.js';
import { registerAppRoutes } from '../lib/register-app-routes.js';
import { buildServerConfig } from '../lib/server-config.js';

test('GET /admin returns the admin console shell', async () => {
  const config = buildServerConfig({ cwd: process.cwd() });
  const app = createApp({ config, registerRoutes: registerAppRoutes });

  const response = await request(app).get('/admin');

  assert.equal(response.status, 200);
  assert.match(response.text, /文档控制台/);
  assert.match(response.text, /site\/docs 流程/);
});
```

- [ ] **Step 2: Run the admin page test and confirm failure**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test -- --test-name-pattern="文档控制台"
```

Expected: FAIL because `site/admin/index.html` does not exist.

- [ ] **Step 3: Create the admin HTML shell**

Create `site/admin/index.html`:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>文档控制台</title>
    <link rel="stylesheet" href="/admin-static/admin.css" />
  </head>
  <body>
    <main class="page">
      <header class="hero">
        <h1>文档控制台</h1>
        <p>本机执行生成、拉取、优化、构建，部署时再连接正式服务器。</p>
      </header>

      <section class="panel" id="status-panel">
        <h2>当前状态</h2>
        <pre id="status-output">加载中...</pre>
      </section>

      <section class="panel">
        <h2>site/docs 流程</h2>
        <div class="actions">
          <button data-task="docs-sidebar">生成侧边栏</button>
          <button data-task="docs-build">构建站点</button>
          <button data-task="docs-refresh">一键刷新站点</button>
        </div>
      </section>

      <section class="panel">
        <h2>pipeline 流程</h2>
        <div class="actions">
          <button data-task="pipeline-crawl">从钉钉拉取</button>
          <button data-task="pipeline-build">执行 pipeline</button>
          <button data-task="full-pipeline-flow">一键全流程</button>
        </div>
      </section>

      <section class="panel">
        <h2>部署与校验</h2>
        <div class="actions">
          <button data-task="deploy-site-dist">部署到正式服务器</button>
          <button data-task="verify-online">查看线上版本</button>
          <button id="stop-task" class="danger">停止当前任务</button>
        </div>
      </section>

      <section class="panel">
        <h2>运行日志</h2>
        <pre id="log-output">暂无日志</pre>
      </section>
    </main>

    <script type="module" src="/admin-static/admin.js"></script>
  </body>
</html>
```

- [ ] **Step 4: Add minimal styling and polling script**

Create `site/admin/admin.css`:

```css
body { margin: 0; font-family: Inter, system-ui, sans-serif; background: #0f172a; color: #e2e8f0; }
.page { max-width: 1200px; margin: 0 auto; padding: 32px; }
.panel { background: #111827; border: 1px solid #334155; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
.actions { display: flex; flex-wrap: wrap; gap: 12px; }
button { padding: 10px 16px; border-radius: 10px; border: 0; cursor: pointer; background: #22c55e; color: #052e16; font-weight: 700; }
button.danger { background: #ef4444; color: white; }
pre { white-space: pre-wrap; word-break: break-word; background: #020617; padding: 16px; border-radius: 12px; min-height: 120px; }
```

Create `site/admin/admin.js`:

```js
const statusOutput = document.querySelector('#status-output');
const logOutput = document.querySelector('#log-output');
const buttons = [...document.querySelectorAll('[data-task]')];
const stopButton = document.querySelector('#stop-task');

async function refreshStatus() {
  const response = await fetch('/api/admin/status');
  const data = await response.json();
  statusOutput.textContent = JSON.stringify(data, null, 2);
  buttons.forEach((button) => { button.disabled = data.running; });
  stopButton.disabled = !data.running;
}

async function refreshLogs() {
  const response = await fetch('/api/admin/logs');
  const data = await response.json();
  logOutput.textContent = (data.logs || []).join('');
}

async function runTask(taskKey) {
  const response = await fetch(`/api/admin/tasks/${taskKey}`, { method: 'POST' });
  if (!response.ok) {
    const error = await response.json();
    alert(error.message || '任务启动失败');
  }
  await refreshStatus();
  await refreshLogs();
}

buttons.forEach((button) => {
  button.addEventListener('click', () => runTask(button.dataset.task));
});

stopButton.addEventListener('click', async () => {
  await fetch('/api/admin/stop', { method: 'POST' });
  await refreshStatus();
});

setInterval(async () => {
  await refreshStatus();
  await refreshLogs();
}, 1500);

await refreshStatus();
await refreshLogs();
```

- [ ] **Step 5: Re-run the admin page smoke test**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test -- --test-name-pattern="文档控制台"
```

Expected: PASS.

- [ ] **Step 6: Commit the admin UI shell**

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean
git add site/admin/index.html site/admin/admin.css site/admin/admin.js site/tests/admin-page.test.js
git commit -m "feat(site): add local admin console page"
```

### Task 5: Add composite tasks, stop support, and deployment verification tests

**Files:**
- Modify: `site/lib/admin-tasks.js`
- Modify: `site/lib/task-runner.js`
- Modify: `site/lib/register-app-routes.js`
- Create: `site/tests/admin-composite.test.js`
- Modify: `docs/site-docs-生成部署说明.md`

- [ ] **Step 1: Write the failing composite-task test**

Create `site/tests/admin-composite.test.js`:

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { createCompositeTaskSteps } from '../lib/admin-tasks.js';

test('full-site-flow expands to sidebar, build, deploy, verify steps', () => {
  const steps = createCompositeTaskSteps('full-site-flow');
  assert.deepEqual(steps, ['docs-sidebar', 'docs-build', 'deploy-site-dist', 'verify-online']);
});
```

- [ ] **Step 2: Run the composite test and confirm failure**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test -- --test-name-pattern="full-site-flow"
```

Expected: FAIL because `createCompositeTaskSteps` does not exist.

- [ ] **Step 3: Extend task definitions for one-click flows**

Update `site/lib/admin-tasks.js`:

```js
export function createCompositeTaskSteps(taskKey) {
  const flows = {
    'full-site-flow': ['docs-sidebar', 'docs-build', 'deploy-site-dist', 'verify-online'],
    'full-pipeline-flow': ['pipeline-crawl', 'pipeline-build', 'deploy-site-dist', 'verify-online'],
  };

  return flows[taskKey] ?? null;
}
```

- [ ] **Step 4: Teach the runner to execute serial substeps**

Update `site/lib/task-runner.js` with a composite runner entrypoint:

```js
async startComposite({ key, label, steps, catalog }) {
  if (activeTask) throw new Error('已有任务正在运行');

  const composite = {
    id: `task-${Date.now()}`,
    key,
    label,
    status: 'running',
    startedAt: new Date().toISOString(),
    finishedAt: null,
    exitCode: null,
    logs: [],
  };

  activeTask = composite;

  for (const stepKey of steps) {
    const definition = catalog[stepKey];
    composite.logs.push(`\n>>> ${definition.label}\n`);
    const result = await runOne(definition, composite.logs);
    if (result !== 0) {
      composite.status = 'failed';
      composite.exitCode = result;
      composite.finishedAt = new Date().toISOString();
      lastTask = composite;
      activeTask = null;
      return toSnapshot(composite);
    }
  }

  composite.status = 'success';
  composite.exitCode = 0;
  composite.finishedAt = new Date().toISOString();
  lastTask = composite;
  activeTask = null;
  return toSnapshot(composite);
}
```

Refactor `runOne()` as an internal Promise helper so single tasks and composite tasks share the same logging path.

- [ ] **Step 5: Wire composite routes and stop behavior**

Update `site/lib/register-app-routes.js` route handler:

```js
import { createTaskCatalog, createCompositeTaskSteps } from './admin-tasks.js';

app.post('/api/admin/tasks/:taskKey', async (req, res) => {
  const taskKey = req.params.taskKey;
  const steps = createCompositeTaskSteps(taskKey);

  try {
    if (steps) {
      const task = await runner.startComposite({
        key: taskKey,
        label: taskKey === 'full-site-flow' ? '站点一键流程' : 'Pipeline 一键流程',
        steps,
        catalog: tasks,
      });
      return res.json({ ok: true, task });
    }

    const definition = tasks[taskKey];
    if (!definition) return res.status(404).json({ errorCode: 'TASK_NOT_FOUND', message: '任务不存在' });

    const task = runner.start(definition);
    return res.json({ ok: true, task });
  } catch (error) {
    return res.status(409).json({ errorCode: 'TASK_ALREADY_RUNNING', message: error.message });
  }
});
```

- [ ] **Step 6: Document the admin console usage**

Append to [site-docs-生成部署说明.md](file:///Users/houpe/Documents/%E6%88%91%E7%9A%84%E5%BC%80%E5%8F%91%E9%A1%B9%E7%9B%AE/dingtalk-doc-crawler-clean/docs/site-docs-%E7%94%9F%E6%88%90%E9%83%A8%E7%BD%B2%E8%AF%B4%E6%98%8E.md):

```md
## 本机管理控制台

在 `site/` 目录启动：

```bash
npm start
```

打开：

```text
http://127.0.0.1:4000/admin
```

控制台支持：

- `site/docs` 流程
- `pipeline` 流程
- 正式环境部署
- 线上校验

同一时间只允许执行一个任务。
```

- [ ] **Step 7: Run the full test suite**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm test
```

Expected: PASS for `server-config`, `task-runner`, `admin-api`, `admin-page`, and `admin-composite`.

- [ ] **Step 8: Run manual verification commands**

Run:

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean/site
npm run docs:refresh
npm start
```

Then manually verify:

```text
1. Open http://127.0.0.1:4000/admin
2. Click "生成侧边栏"
3. Click "构建站点"
4. Click "查看线上版本"
5. Start a long task and verify other buttons disable
6. Click "停止当前任务" and verify status changes
```

Expected: All page actions respond, logs update, and single-task locking holds.

- [ ] **Step 9: Commit the final admin console**

```bash
cd /Users/houpe/Documents/我的开发项目/dingtalk-doc-crawler-clean
git add site/lib/admin-tasks.js site/lib/task-runner.js site/lib/register-app-routes.js site/admin site/tests docs/site-docs-生成部署说明.md
git commit -m "feat(site): add local docs admin console"
```
