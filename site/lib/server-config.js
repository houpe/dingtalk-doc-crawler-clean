import { join, resolve } from 'node:path';

export function buildServerConfig({
  cwd = process.cwd(),
  host = process.env.HOST || '127.0.0.1',
  port = process.env.PORT || '4000',
  sessionSecret = process.env.SESSION_SECRET || process.env.JWT_SECRET || 'houpe-auth-dev-secret',
  authLoginUrl = process.env.AUTH_LOGIN_URL || '/auth/login',
  authRequired = process.env.AUTH_REQUIRED !== 'false',
  sessionStore =
    process.env.AUTH_SESSION_STORE ||
    (process.env.REDIS_URL || process.env.REDIS_HOST || process.env.REDIS_PASSWORD
      ? 'redis'
      : 'memory'),
  sessionMaxAgeDays = Number(process.env.SESSION_MAX_AGE_DAYS || '7'),
  redisUrl = process.env.REDIS_URL || '',
  redisHost = process.env.REDIS_HOST || 'localhost',
  redisPort = Number(process.env.REDIS_PORT || '6379'),
  redisPassword = process.env.REDIS_PASSWORD || '',
  redisDb = Number(process.env.REDIS_DB || '2'),
  redisSessionPrefix = process.env.REDIS_SESSION_PREFIX || 'gis:sess:',
  dingtalkAppKey = process.env.DINGTALK_APP_KEY || '',
  dingtalkAppSecret = process.env.DINGTALK_APP_SECRET || '',
  dingtalkCorpId = process.env.DINGTALK_CORP_ID || '',
  publicOrigin = process.env.PUBLIC_ORIGIN || 'https://help.beta.ztocc.com',
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
    sessionSecret,
    authLoginUrl,
    authRequired,
    sessionStore,
    sessionMaxAgeMs: sessionMaxAgeDays * 24 * 60 * 60 * 1000,
    redisUrl,
    redisHost,
    redisPort,
    redisPassword,
    redisDb,
    redisSessionPrefix,
    dingtalkAppKey,
    dingtalkAppSecret,
    dingtalkCorpId,
    publicOrigin,
  };
}
