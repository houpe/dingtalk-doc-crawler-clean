import { readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import express from 'express';
import {
  createTaskCatalog,
  getCompositeTaskDefinition,
  listCompositeTaskDefinitions,
} from './admin-tasks.js';
import { createTaskRunner } from './task-runner.js';
import { createDingtalk } from './dingtalk.js';
import { createAuthRouter } from './auth-routes.js';

function buildLoginRedirect(config, req) {
  const originalUrl = req.originalUrl || req.url || '/';
  const separator = config.authLoginUrl.includes('?') ? '&' : '?';
  return `${config.authLoginUrl}${separator}redirect=${encodeURIComponent(originalUrl)}`;
}

// 本地预览（浏览器与 server 同机）免钉钉登录：仅放行 127.0.0.1 / localhost 来源，
// 远程（公网/局域网其他设备）访问仍走钉钉登录，不影响正式环境安全。
function isLocalRequest(req) {
  const ip = req.ip || '';
  const host = (req.hostname || req.headers?.host || '').split(':')[0];
  return (
    ip === '127.0.0.1' ||
    ip === '::1' ||
    ip === '::ffff:127.0.0.1' ||
    host === 'localhost' ||
    host === '127.0.0.1'
  );
}

function buildRequireAuth(config, { redirect = false } = {}) {
  return function requireAuth(req, res, next) {
    if (!config.authRequired || req.session?.user || isLocalRequest(req)) {
      req.user = req.session?.user || null;
      return next();
    }

    if (redirect) {
      return res.redirect(302, buildLoginRedirect(config, req));
    }

    res.status(401).json({ error: '未登录' });
  };
}

function safeDocPath(config, relativePath) {
  if (!relativePath || typeof relativePath !== 'string') {
    return null;
  }

  const fullPath = resolve(config.docsDir, relativePath.replace(/\.md$/, '') + '.md');

  if (
    !fullPath.startsWith(config.docsDir + '/') &&
    !fullPath.startsWith(config.docsDir + '\\')
  ) {
    return null;
  }

  return fullPath;
}

function isLoopbackAddress(address) {
  return (
    typeof address === 'string' &&
    (/^127\.\d+\.\d+\.\d+$/.test(address) ||
      address === '::1' ||
      /^::ffff:127\.\d+\.\d+\.\d+$/.test(address))
  );
}

function isLoopbackHostname(hostname) {
  const normalized = typeof hostname === 'string' ? hostname.replace(/^\[|\]$/g, '') : '';
  return (
    normalized === 'localhost' ||
    normalized.endsWith('.localhost') ||
    isLoopbackAddress(normalized)
  );
}

function hasLocalHostHeader(req) {
  const host = req.headers.host;

  if (typeof host !== 'string') {
    return false;
  }

  try {
    return isLoopbackHostname(new URL(`http://${host}`).hostname);
  } catch {
    return false;
  }
}

function hasTrustedBrowserOrigin(req) {
  const origin = req.headers.origin;

  if (origin !== undefined) {
    if (typeof origin !== 'string' || origin === 'null') {
      return false;
    }

    try {
      const originUrl = new URL(origin);
      return (
        (originUrl.protocol === 'http:' || originUrl.protocol === 'https:') &&
        isLoopbackHostname(originUrl.hostname)
      );
    } catch {
      return false;
    }
  }

  return req.headers['sec-fetch-site'] !== 'cross-site';
}

function normalizeForwardedAddress(value) {
  if (typeof value !== 'string') {
    return null;
  }

  let normalized = value.trim();

  if (!normalized || normalized.toLowerCase() === 'unknown') {
    return null;
  }

  if (normalized.startsWith('"') && normalized.endsWith('"')) {
    normalized = normalized.slice(1, -1);
  }

  if (normalized.startsWith('[')) {
    const closingBracketIndex = normalized.indexOf(']');
    if (closingBracketIndex !== -1) {
      return normalized.slice(1, closingBracketIndex);
    }
  }

  if (/^\d+\.\d+\.\d+\.\d+:\d+$/.test(normalized)) {
    return normalized.replace(/:\d+$/, '');
  }

  return normalized;
}

function readForwardedAddresses(req) {
  const addresses = [];
  const xForwardedFor = req.headers['x-forwarded-for'];
  const xRealIp = req.headers['x-real-ip'];
  const forwarded = req.headers.forwarded;

  if (typeof xForwardedFor === 'string') {
    addresses.push(...xForwardedFor.split(',').map((entry) => normalizeForwardedAddress(entry)));
  }

  if (typeof xRealIp === 'string') {
    addresses.push(normalizeForwardedAddress(xRealIp));
  }

  if (typeof forwarded === 'string') {
    const forwardedMatches = forwarded.match(/for=("[^"]+"|\[[^\]]+\]|[^;,]+)/gi) || [];
    addresses.push(
      ...forwardedMatches.map((entry) => normalizeForwardedAddress(entry.replace(/^for=/i, ''))),
    );
  }

  return addresses.filter(Boolean);
}

function requireLocalOnly(req, res, next) {
  const socketAddress = req.socket?.remoteAddress;
  const forwardedAddresses = readForwardedAddresses(req);

  if (
    isLoopbackAddress(socketAddress) &&
    forwardedAddresses.every((address) => isLoopbackAddress(address)) &&
    hasLocalHostHeader(req) &&
    hasTrustedBrowserOrigin(req)
  ) {
    return next();
  }

  if ((req.originalUrl || req.path).startsWith('/api/')) {
    return res.status(403).json({ error: '仅允许本机访问' });
  }

  res.status(403).type('text/plain').send('仅允许本机访问');
}

function cloneTaskDefinition(task) {
  return {
    key: task.key,
    label: task.label,
    description: task.description,
  };
}

function listTaskDefinitions(taskCatalog) {
  return [
    ...Object.values(taskCatalog).map((task) => cloneTaskDefinition(task)),
    ...listCompositeTaskDefinitions(),
  ];
}

function consumeTaskCompletion(run, taskType) {
  if (!run?.completed || typeof run.completed.catch !== 'function') {
    return;
  }

  void run.completed.catch((error) => {
    if (error?.message !== 'Task stopped') {
      console.error(`[admin-task] ${taskType} failed:`, error);
    }
  });
}

export function registerAppRoutes(
  app,
  {
    config,
    express: contextExpress = express,
    taskCatalog = createTaskCatalog(config),
    taskRunner = createTaskRunner(),
  },
) {
  const requireAuth = buildRequireAuth(config);
  const requireSiteAuth = buildRequireAuth(config, { redirect: true });
  const adminRouter = contextExpress.Router();

  // 钉钉登录：仅在配置了 AppKey 时启用，避免未配置环境报错。
  const dingtalk = config.dingtalkAppKey
    ? createDingtalk({ appKey: config.dingtalkAppKey, appSecret: config.dingtalkAppSecret })
    : null;
  app.use(createAuthRouter(config, dingtalk));

  app.use(
    '/admin-static',
    requireLocalOnly,
    contextExpress.static(join(config.cwd, 'admin'), { index: false }),
  );

  app.get(['/admin', '/admin/'], requireLocalOnly, (_req, res) => {
    res.sendFile(join(config.cwd, 'admin', 'index.html'));
  });

  app.get(['/api/auth/check', '/api/auth/me'], (req, res) => {
    res.json({
      loggedIn: Boolean(!config.authRequired || req.session?.user),
      user: req.session?.user || null,
    });
  });

  app.post(['/api/logout', '/api/auth/logout'], (req, res) => {
    req.session?.destroy(() => res.json({ ok: true }));
  });

  adminRouter.use(requireLocalOnly);

  adminRouter.get('/tasks', (_req, res) => {
    res.json(listTaskDefinitions(taskCatalog));
  });

  adminRouter.get('/status', (_req, res) => {
    res.json(taskRunner.getStatus());
  });

  adminRouter.get('/logs', (_req, res) => {
    res.json(taskRunner.getLogs());
  });

  adminRouter.post('/tasks/:taskKey', (req, res) => {
    const taskKey = req.params.taskKey;
    const compositeTask = getCompositeTaskDefinition(taskKey);

    try {
      if (compositeTask) {
        const run = taskRunner.startComposite({
          key: compositeTask.key,
          label: compositeTask.label,
          steps: compositeTask.steps,
          catalog: taskCatalog,
        });
        consumeTaskCompletion(run, 'composite run');
        return res.status(202).json({
          ok: true,
          runId: run.runId,
          status: taskRunner.getStatus(),
        });
      }

      const task = taskCatalog[taskKey];

      if (!task) {
        return res.status(404).json({ error: '任务不存在' });
      }

      const run = taskRunner.start(task);
      consumeTaskCompletion(run, 'run');
      res.status(202).json({
        ok: true,
        runId: run.runId,
        status: taskRunner.getStatus(),
      });
    } catch (error) {
      res.status(409).json({ error: error.message });
    }
  });

  adminRouter.post('/stop', (_req, res) => {
    try {
      const task = taskRunner.stop();
      res.json({ ok: true, task });
    } catch (error) {
      res.status(409).json({ error: error.message });
    }
  });

  app.use('/api/admin', adminRouter);

  app.get('/api/docs/:path(*)', requireAuth, (req, res) => {
    const filePath = safeDocPath(config, req.params.path);

    if (!filePath) {
      return res.status(403).json({ error: '非法路径' });
    }

    try {
      res.json({ content: readFileSync(filePath, 'utf-8'), path: req.params.path });
    } catch {
      res.status(404).json({ error: '文件不存在' });
    }
  });

  app.put('/api/docs/:path(*)', requireAuth, (req, res) => {
    const filePath = safeDocPath(config, req.params.path);

    if (!filePath) {
      return res.status(403).json({ error: '非法路径' });
    }

    if (!req.body.content) {
      return res.status(400).json({ error: '内容为空' });
    }

    const relativePath = req.params.path.replace(/\.md$/, '') + '.md';

    if (!relativePath.startsWith('guide/')) {
      return res.status(403).json({ error: '路径非法' });
    }

    try {
      writeFileSync(filePath, req.body.content, 'utf-8');
      res.json({ ok: true, path: relativePath });
    } catch (error) {
      res.status(500).json({ error: '保存失败: ' + error.message });
    }
  });

  app.post('/api/build', requireAuth, (_req, res) => {
    const task = taskCatalog['docs-build'];

    if (!task) {
      return res.status(500).json({ error: '构建任务未配置' });
    }

    try {
      const run = taskRunner.start(task);
      consumeTaskCompletion(run, 'editor build');
      res.json({ ok: true, message: '构建已启动', runId: run.runId });
    } catch (error) {
      res.status(409).json({ error: error.message });
    }
  });

  app.use((req, res, next) => {
    if (req.url.startsWith('/api/')) {
      return next();
    }

    return requireSiteAuth(req, res, next);
  });

  // VitePress 内部链接均为 clean URL（/foo/ 形式），但产物文件是 foo.html。
  // 在静态中间件前去掉末尾斜杠，交给 express.static 的 extensions 补 .html，
  // 否则 /foo/ 会被当作目录请求而 404。
  app.use((req, res, next) => {
    if (req.method === 'GET' && !req.url.startsWith('/api/')) {
      const qi = req.url.indexOf('?');
      const path = qi === -1 ? req.url : req.url.slice(0, qi);
      const query = qi === -1 ? '' : req.url.slice(qi);
      if (path.length > 1 && path.endsWith('/')) {
        req.url = path.slice(0, -1) + query;
      }
    }
    next();
  });

  // 旧中文 URL → /d/<nodeId> 稳定 URL 重定向（必须在 express.static 之前）。
  // 钉钉改名后物理路径变化，旧链接会指向旧路径；此处从 redirects.json 查表做 301 跳转。
  let redirectMap = {};
  try {
    const redirectsFile = join(config.publicDir || join(config.docsDir, 'public'), 'redirects.json');
    redirectMap = JSON.parse(readFileSync(redirectsFile, 'utf-8'));
  } catch { /* redirects.json 不存在或解析失败，忽略 */ }
  app.use((req, res, next) => {
    if (req.method !== 'GET' || req.url.startsWith('/api/') || req.url.startsWith('/d/')) {
      return next();
    }
    const rawPath = req.url.split('?')[0].split('#')[0];
    // redirects.json 的 key 是中文原文，req.url 是 URL 编码的，需解码后匹配
    let path;
    try { path = decodeURIComponent(rawPath); } catch { path = rawPath; }
    const normalized = path.endsWith('/') && path.length > 1 ? path.slice(0, -1) : path;
    const target = redirectMap[normalized] || redirectMap[path];
    if (target) {
      return res.redirect(301, target);
    }
    next();
  });

  // VitePress emits `guide/topic.html` for the clean URL `/guide/topic`.
  // Resolve that HTML before the SPA fallback so server-rendered markup always
  // matches the page Vue hydrates on direct navigation.
  app.use(
    express.static(config.distDir, {
      extensions: ['html'],
      index: 'index.html',
    }),
  );

  app.use('*', (req, res, next) => {
    if (req.url.startsWith('/api/')) {
      return next();
    }

    res.status(404).sendFile(join(config.distDir, '404.html'), (error) => {
      if (!error) {
        return;
      }

      if (error.code === 'ENOENT') {
        res.status(404).type('text/plain').send('页面不存在');
        return;
      }

      next(error);
    });
  });
}
