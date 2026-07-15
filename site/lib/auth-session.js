import session from 'express-session';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { createClient: redisCreateClient } = require('ioredis');

// connect-redis@7 以默认导出提供 RedisStore，@9 改为命名导出。
// 用 createRequire 动态 require 绕过 ESM 静态导入的版本差异，
// 取 default 或 RedisStore 命名导出，兼容两个主版本。
// 注意：与 ioredis 配合必须用 @7（@9 的 SET 对象语法不兼容 ioredis，会报 ERR syntax error）。
const connectRedisModule = require('connect-redis');
const RedisStore = connectRedisModule.default || connectRedisModule.RedisStore || connectRedisModule;

function createRedisClient(config) {
  if (config.redisUrl) {
    return redisCreateClient(config.redisUrl, {
      db: config.redisDb,
      password: config.redisPassword || undefined,
      retryStrategy: (times) => Math.min(times * 200, 5000),
    });
  }

  return redisCreateClient({
    host: config.redisHost,
    port: config.redisPort,
    password: config.redisPassword || undefined,
    db: config.redisDb,
    retryStrategy: (times) => Math.min(times * 200, 5000),
  });
}

export function createSessionMiddleware(config) {
  const options = {
    secret: config.sessionSecret,
    resave: false,
    saveUninitialized: false,
    name: 'connect.sid',
    cookie: {
      secure: false,
      sameSite: 'lax',
      maxAge: config.sessionMaxAgeMs,
      path: '/',
    },
  };

  if (config.sessionStore === 'redis') {
    const redisClient = createRedisClient(config);
    redisClient.on('error', (error) => console.error('[redis]', error.message));
    redisClient.on('ready', () => console.log('[redis] connected'));
    options.store = new RedisStore({ client: redisClient, prefix: config.redisSessionPrefix });
  }

  return session(options);
}
