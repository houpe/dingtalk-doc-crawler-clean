import { readFileSync, writeFileSync } from 'fs';
import { resolve, join } from 'path';
import { spawn } from 'child_process';
import express from 'express';
import jwt from 'jsonwebtoken';

const DOCS_DIR = join(process.cwd(), 'docs');
const DIST_DIR = join(DOCS_DIR, '.vitepress/dist');
const JWT_SECRET = process.env.JWT_SECRET || 'zto-doc-secret-change-me';
const PORT = parseInt(process.env.PORT || '4000');
const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.ADMIN_PASS || 'admin123';

function getCookie(req, name) {
  const c = (req.headers.cookie || '').split('; ').find(r => r.startsWith(name + '='));
  return c ? c.split('=')[1] : null;
}

function requireAuth(req, res, next) {
  const token = getCookie(req, 'jwt');
  if (!token) return res.status(401).json({ error: '未登录' });
  try { req.user = jwt.verify(token, JWT_SECRET); next(); }
  catch { res.status(401).json({ error: '登录过期' }); }
}

function safeDocPath(p) {
  if (!p || typeof p !== 'string') return null;
  const full = resolve(DOCS_DIR, (p || '').replace(/\.md$/, '') + '.md');
  if (!full.startsWith(DOCS_DIR + '/') && !full.startsWith(DOCS_DIR + '\\')) return null;
  return full;
}

const app = express();
app.use(express.json({ limit: '10mb' }));
app.use(express.static(DIST_DIR, { index: false }));

app.use('*', (req, res, next) => {
  if (req.url.startsWith('/api/')) return next();
  res.sendFile(join(DIST_DIR, 'index.html'));
});

app.get('/api/auth/check', (req, res) => {
  const token = getCookie(req, 'jwt');
  if (!token) return res.json({ loggedIn: false });
  try { const u = jwt.verify(token, JWT_SECRET); res.json({ loggedIn: true, user: u.username }); }
  catch { res.json({ loggedIn: false }); }
});

app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (username === ADMIN_USER && password === ADMIN_PASS) {
    const token = jwt.sign({ username }, JWT_SECRET, { expiresIn: '4h' });
    res.cookie('jwt', token, { httpOnly: true, maxAge: 14400000, sameSite: 'lax' });
    res.json({ ok: true });
  } else res.status(401).json({ error: '用户名或密码错误' });
});

app.post('/api/logout', (req, res) => { res.clearCookie('jwt'); res.json({ ok: true }); });

app.get('/api/docs/:path(*)', requireAuth, (req, res) => {
  const fp = safeDocPath(req.params.path);
  if (!fp) return res.status(403).json({ error: '非法路径' });
  try { res.json({ content: readFileSync(fp, 'utf-8'), path: req.params.path }); }
  catch { res.status(404).json({ error: '文件不存在' }); }
});

app.put('/api/docs/:path(*)', requireAuth, (req, res) => {
  const fp = safeDocPath(req.params.path);
  if (!fp) return res.status(403).json({ error: '非法路径' });
  if (!req.body.content) return res.status(400).json({ error: '内容为空' });
  const rel = req.params.path.replace(/\.md$/, '') + '.md';
  if (!rel.startsWith('guide/')) return res.status(403).json({ error: '路径非法' });
  try { writeFileSync(fp, req.body.content, 'utf-8'); res.json({ ok: true, path: rel }); }
  catch (e) { res.status(500).json({ error: '保存失败: ' + e.message }); }
});

app.post('/api/build', requireAuth, (req, res) => {
  res.json({ ok: true, message: '构建已启动' });
  const child = spawn('npx', ['vitepress', 'build', 'docs'], {
    cwd: process.cwd(), stdio: 'pipe', env: { ...process.env },
  });
  child.stdout.on('data', d => console.log('[build]', String(d).trim()));
  child.stderr.on('data', d => console.error('[build]', String(d).trim()));
  child.on('close', code => console.log('[build] exit code:', code));
});

app.listen(PORT, () => {
  console.log('\n   中通冷链文档 - http://localhost:' + PORT);
  console.log('   编辑入口: http://localhost:' + PORT + '/edit.html');
  console.log('   登录账号:', ADMIN_USER);
  console.log('\n  Ctrl+C 停止\n');
});
