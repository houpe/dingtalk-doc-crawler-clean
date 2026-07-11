import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import request from 'supertest';
import { createApp } from '../lib/create-app.js';
import { registerAppRoutes } from '../lib/register-app-routes.js';
import { buildServerConfig } from '../lib/server-config.js';

test('GET /admin returns the admin console shell with grouped sections', async () => {
  const config = buildServerConfig({ cwd: process.cwd() });
  const app = createApp({ config, registerRoutes: registerAppRoutes });

  const response = await request(app).get('/admin');

  assert.equal(response.status, 200);
  assert.match(response.headers['content-type'], /text\/html/);
  assert.match(response.text, /文档控制台/);
  assert.match(response.text, /1\. 文档生成/);
  assert.match(response.text, /2\. 本地站点构建与预览/);
  assert.match(response.text, /3\. 部署到服务器/);
  assert.match(response.text, /全量流程（可选）/);
  assert.match(response.text, /当前状态/);
  assert.match(response.text, /运行日志/);
  assert.match(response.text, /admin-static\/admin\.css/);
  assert.match(response.text, /admin-static\/admin\.js/);
});

test('admin page groups tasks into three isolated stages and an optional full flow', () => {
  const script = readFileSync(join(process.cwd(), 'admin', 'admin.js'), 'utf8');

  assert.match(script, /pipeline-crawl/);
  assert.match(script, /content-generate/);
  assert.match(script, /content-flow/);
  assert.match(script, /site-build-local/);
  assert.match(script, /local-site-flow/);
  assert.match(script, /validate-site-dist/);
  assert.match(script, /deploy-flow/);
  assert.match(script, /full-release-flow/);
  assert.doesNotMatch(script, /full-site-flow/);
  assert.doesNotMatch(script, /full-pipeline-flow/);
  assert.doesNotMatch(script, /pipeline-deploy-fast/);
});

test('admin page exposes manual refresh and local log clearing controls', async () => {
  const config = buildServerConfig({ cwd: process.cwd() });
  const app = createApp({ config, registerRoutes: registerAppRoutes });

  const response = await request(app).get('/admin');
  const script = readFileSync(join(process.cwd(), 'admin', 'admin.js'), 'utf8');

  assert.match(response.text, /id="refresh-status"/);
  assert.match(response.text, /id="clear-logs"/);
  assert.match(script, /refresh-status/);
  assert.match(script, /clear-logs/);
});

test('admin page links to the locally served site preview', async () => {
  const config = buildServerConfig({ cwd: process.cwd() });
  const app = createApp({ config, registerRoutes: registerAppRoutes });

  const response = await request(app).get('/admin');

  assert.match(response.text, /id="preview-site"/);
  assert.match(response.text, /href="\/"/);
  assert.match(response.text, /target="_blank"/);
  assert.match(response.text, /rel="noopener"/);
  assert.match(response.text, /预览本地站点/);
});

test('admin page renders every task button as a card with a visible description', async () => {
  const config = buildServerConfig({ cwd: process.cwd() });
  const app = createApp({ config, registerRoutes: registerAppRoutes });
  const response = await request(app).get('/admin');
  const script = readFileSync(join(process.cwd(), 'admin', 'admin.js'), 'utf8');
  const styles = readFileSync(join(process.cwd(), 'admin', 'admin.css'), 'utf8');

  assert.match(script, /createTaskCard/);
  assert.match(script, /task\.description/);
  assert.match(script, /task-description-/);
  assert.match(script, /aria-describedby/);
  assert.match(styles, /\.task-card/);
  assert.match(styles, /\.task-description/);
  assert.match(response.text, /id="stop-task-description"/);
  assert.match(response.text, /不会回滚已生成文件或已经完成的部署/);
});
