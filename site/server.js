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
