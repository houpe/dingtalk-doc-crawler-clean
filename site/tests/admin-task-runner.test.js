import test from 'node:test';
import assert from 'node:assert/strict';
import { createTaskRunner as createCompatibilityRunner } from '../lib/admin-task-runner.js';
import { createTaskRunner } from '../lib/task-runner.js';

test('admin-task-runner keeps the legacy import path compatible', () => {
  assert.equal(createCompatibilityRunner, createTaskRunner);
});
