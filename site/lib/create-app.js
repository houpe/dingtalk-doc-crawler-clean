import express from 'express';

export function createApp({ config, registerRoutes }) {
  const app = express();
  app.use(express.json({ limit: '10mb' }));

  registerRoutes(app, { config, express });

  return app;
}
