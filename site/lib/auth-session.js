import session from 'express-session';
import { RedisStore } from 'connect-redis';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { createClient: redisCreateClient } = require('ioredis');

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
