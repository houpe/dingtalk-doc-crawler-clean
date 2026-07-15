import express from 'express';
import { createSessionMiddleware } from './auth-session.js';

export function createApp({ config, registerRoutes }) {
  const app = express();
  app.set('trust proxy', 1);
  app.use(express.json({ limit: '10mb' }));
  app.use(createSessionMiddleware(config));

  registerRoutes(app, { config, express });

  return app;
}
