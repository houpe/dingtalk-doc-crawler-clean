import { join, resolve } from 'node:path';

export function buildServerConfig({
  cwd = process.cwd(),
  host = process.env.HOST || '127.0.0.1',
  port = process.env.PORT || '4000',
  jwtSecret = process.env.JWT_SECRET || 'zto-doc-secret-change-me',
  adminUser = process.env.ADMIN_USER || 'admin',
  adminPass = process.env.ADMIN_PASS || 'admin123',
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
    jwtSecret,
    adminUser,
    adminPass,
  };
}
