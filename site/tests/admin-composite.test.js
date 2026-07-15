import test from 'node:test';
import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
import { createTaskRunner } from '../lib/task-runner.js';

const TEST_TIMESTAMP = '2026-07-11T13:40:00.000Z';
const testNow = () => TEST_TIMESTAMP;
const withTimestamp = (lines) => lines.map((line) => '[2026-07-11 21:40:00] ' + line);

function createSpawnStub() {
  const calls = [];

  function spawnImpl(command, args, options) {
    const child = new EventEmitter();
    child.stdout = new EventEmitter();
    child.stderr = new EventEmitter();
    child.killedWith = null;
    child.kill = (signal) => {
      child.killedWith = signal;
      child.emit('close', 143);
    };
    calls.push({ command, args, options, child });
    return child;
  }

  return { calls, spawnImpl };
}

function createCatalog() {
  return Object.freeze({
    first: Object.freeze({
      key: 'first',
      label: '第一步',
      command: 'first-command',
      args: Object.freeze(['--first']),
      cwd: '/tmp/first',
    }),
    second: Object.freeze({
      key: 'second',
      label: '第二步',
      command: 'second-command',
      args: Object.freeze(['--second']),
      cwd: '/tmp/second',
    }),
  });
}

function flushEvents() {
  return new Promise((resolve) => setImmediate(resolve));
}

test('startComposite runs steps serially and combines their logs', async () => {
  const { calls, spawnImpl } = createSpawnStub();
  const catalog = createCatalog();
  const runner = createTaskRunner({ spawnImpl, now: testNow });

  const run = runner.startComposite({
    key: 'content-flow',
    label: '第一步：文档生成流程',
    steps: ['first', 'second'],
    catalog,
  });

  assert.equal(calls.length, 1);
  assert.equal(calls[0].command, 'first-command');
  calls[0].child.stdout.emit('data', 'first output\n');
  calls[0].child.emit('close', 0);
  await flushEvents();

  assert.equal(calls.length, 2);
  assert.equal(calls[1].command, 'second-command');
  calls[1].child.stderr.emit('data', 'second output\n');
  calls[1].child.emit('close', 0);

  const completed = await run.completed;
  assert.equal(completed.status, 'success');
  assert.equal(completed.exitCode, 0);
  assert.deepEqual(completed.logs, withTimestamp([
    '>>> 开始: 第一步 (first)',
    '命令: first-command --first',
    '目录: /tmp/first',
    '[stdout] first output',
    '<<< 完成: 第一步 (first), exit=0',
    '>>> 开始: 第二步 (second)',
    '命令: second-command --second',
    '目录: /tmp/second',
    '[stderr] second output',
    '<<< 完成: 第二步 (second), exit=0',
  ]));
  assert.equal(runner.getStatus().running, false);
  assert.deepEqual(runner.getLogs(), completed.logs);
});

test('startComposite stops after the first failed step', async () => {
  const { calls, spawnImpl } = createSpawnStub();
  const runner = createTaskRunner({ spawnImpl });

  const run = runner.startComposite({
    key: 'full-release-flow',
    label: '全量一键流程',
    steps: ['first', 'second'],
    catalog: createCatalog(),
  });

  calls[0].child.stderr.emit('data', 'failed output\n');
  calls[0].child.emit('close', 2);

  await assert.rejects(run.completed, /Task exited with code 2/);
  assert.equal(calls.length, 1);
  const status = runner.getStatus();
  assert.equal(status.running, false);
  assert.equal(status.lastTask.status, 'failed');
  assert.equal(status.lastTask.exitCode, 2);
  assert.equal(status.lastTask.error, 'Task exited with code 2');
});

test('stop terminates the active composite child and prevents later steps', async () => {
  const { calls, spawnImpl } = createSpawnStub();
  const runner = createTaskRunner({ spawnImpl });

  const run = runner.startComposite({
    key: 'local-site-flow',
    label: '第二步：本地站点流程',
    steps: ['first', 'second'],
    catalog: createCatalog(),
  });

  const stopped = runner.stop();
  await assert.rejects(run.completed, /Task stopped/);
  await flushEvents();

  assert.equal(calls[0].child.killedWith, 'SIGTERM');
  assert.equal(calls.length, 1);
  assert.equal(stopped.status, 'stopping');
  assert.equal(runner.getStatus().lastTask.status, 'stopped');
});

test('stop keeps the single-task lock until the child process closes', async () => {
  const calls = [];
  const runner = createTaskRunner({
    spawnImpl(command, args, options) {
      const child = new EventEmitter();
      child.stdout = new EventEmitter();
      child.stderr = new EventEmitter();
      child.kill = (signal) => {
        child.killedWith = signal;
      };
      calls.push({ command, args, options, child });
      return child;
    },
  });
  const catalog = createCatalog();
  const run = runner.start(catalog.first);

  const stopping = runner.stop();
  await assert.rejects(run.completed, /Task stopped/);

  assert.equal(stopping.status, 'stopping');
  assert.equal(runner.getStatus().running, true);
  assert.throws(() => runner.start(catalog.second), /已有任务正在运行/);

  calls[0].child.emit('close', 143);
  await flushEvents();

  assert.equal(runner.getStatus().running, false);
  assert.equal(runner.getStatus().lastTask.status, 'stopped');

  const secondRun = runner.start(catalog.second);
  calls[1].child.emit('close', 0);
  await secondRun.completed;
});

test('startComposite validates every step before spawning', () => {
  const { calls, spawnImpl } = createSpawnStub();
  const runner = createTaskRunner({ spawnImpl });

  assert.throws(
    () =>
      runner.startComposite({
        key: 'broken-flow',
        label: '错误流程',
        steps: ['first', 'missing'],
        catalog: createCatalog(),
      }),
    /Unknown composite task step: missing/,
  );
  assert.equal(calls.length, 0);
  assert.equal(runner.getStatus().running, false);
});
