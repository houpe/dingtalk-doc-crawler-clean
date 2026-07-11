import test from 'node:test';
import assert from 'node:assert/strict';
import { buildServerConfig } from '../lib/server-config.js';

test('buildServerConfig pins docs and dist directories under site cwd', () => {
  const cwd = '/tmp/example-site';
  const config = buildServerConfig({ cwd, host: '127.0.0.1', port: '4010' });

  assert.equal(config.cwd, cwd);
  assert.equal(config.host, '127.0.0.1');
  assert.equal(config.port, 4010);
  assert.equal(config.docsDir, '/tmp/example-site/docs');
  assert.equal(config.distDir, '/tmp/example-site/docs/.vitepress/dist');
  assert.match(config.projectRoot, /\/tmp$/);
});
