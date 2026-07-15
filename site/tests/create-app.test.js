import test from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import express from 'express';
import { createApp } from '../lib/create-app.js';
import { buildServerConfig } from '../lib/server-config.js';

test('createApp delegates route registration to registerRoutes', async () => {
  const config = buildServerConfig({ cwd: '/tmp/example-site', sessionStore: 'memory' });
  let called = false;

  const app = createApp({
    config,
    registerRoutes(appInstance, context) {
      called = true;
      assert.ok(appInstance);
      assert.equal(context.config, config);
      assert.equal(context.express, express);

      appInstance.get('/health', (_req, res) => {
        res.json({ ok: true });
      });
    },
  });

  const response = await request(app).get('/health');

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, { ok: true });
  assert.equal(called, true);
});
