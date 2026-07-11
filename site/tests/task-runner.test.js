import test from 'node:test';
import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
import { createTaskCatalog } from '../lib/admin-tasks.js';
import { createTaskRunner } from '../lib/task-runner.js';
import { buildServerConfig } from '../lib/server-config.js';

function createSpawnStub() {
  const calls = [];

  function spawnImpl(command, args, options) {
    const child = new EventEmitter();
    child.stdout = new EventEmitter();
    child.stderr = new EventEmitter();
    child.kill = () => {
      child.emit('close', 143);
    };

    calls.push({ command, args, options, child });
    return child;
  }

  return { calls, spawnImpl };
}

test('createTaskRunner exposes single and composite task controls', async () => {
  const { calls, spawnImpl } = createSpawnStub();
  const config = buildServerConfig({ cwd: '/tmp/example-site' });
  const catalog = createTaskCatalog(config);
  const runner = createTaskRunner({ spawnImpl });
  const definition = catalog['docs-build'];

  const run = runner.start(definition);

  assert.equal(calls.length, 1);
  assert.equal(calls[0].command, 'npm');
  assert.deepEqual(calls[0].args, ['run', 'build']);
  assert.equal(calls[0].options.cwd, '/tmp/example-site');
  assert.equal(calls[0].options.detached, process.platform !== 'win32');
  assert.equal(calls[0].options.env.PYTHONUNBUFFERED, '1');

  const runningLogs = [
    '>>> 开始: 构建站点 (docs-build)',
    '命令: npm run build',
    '目录: /tmp/example-site',
  ];

  let status = runner.getStatus();
  assert.equal(status.running, true);
  assert.deepEqual(status.activeTask, {
    id: status.activeTask.id,
    key: 'docs-build',
    label: '构建站点',
    command: 'npm',
    args: ['run', 'build'],
    cwd: '/tmp/example-site',
    status: 'running',
    startedAt: status.activeTask.startedAt,
    finishedAt: null,
    exitCode: null,
    logs: runningLogs,
    error: null,
  });
  assert.equal(status.lastTask, null);
  assert.deepEqual(runner.getLogs(), runningLogs);

  calls[0].child.stdout.emit('data', Buffer.from('\u001b[32mbuild ok\u001b[0m\n'));
  calls[0].child.emit('close', 0);
  await run.completed;

  status = runner.getStatus();
  assert.equal(status.running, false);
  assert.equal(status.activeTask, null);
  assert.deepEqual(status.lastTask, {
    id: status.lastTask.id,
    key: 'docs-build',
    label: '构建站点',
    command: 'npm',
    args: ['run', 'build'],
    cwd: '/tmp/example-site',
    status: 'success',
    startedAt: status.lastTask.startedAt,
    finishedAt: status.lastTask.finishedAt,
    exitCode: 0,
    logs: [
      ...runningLogs,
      '[stdout] build ok',
      '<<< 完成: 构建站点 (docs-build), exit=0',
    ],
    error: null,
  });
  assert.deepEqual(runner.getLogs(), [
    ...runningLogs,
    '[stdout] build ok',
    '<<< 完成: 构建站点 (docs-build), exit=0',
  ]);
});

test('createTaskRunner enforces the single-task lock with the required error message', async () => {
  const { calls, spawnImpl } = createSpawnStub();
  const config = buildServerConfig({ cwd: '/tmp/example-site' });
  const catalog = createTaskCatalog(config);
  const runner = createTaskRunner({ spawnImpl });

  const firstRun = runner.start(catalog['docs-sidebar']);

  assert.throws(() => runner.start(catalog['docs-refresh']), /已有任务正在运行/);
  assert.equal(calls.length, 1);

  calls[0].child.emit('close', 0);
  await firstRun.completed;
});

test('createTaskRunner stop marks the run as stopped and clears active task', async () => {
  const { calls, spawnImpl } = createSpawnStub();
  const config = buildServerConfig({ cwd: '/tmp/example-site' });
  const catalog = createTaskCatalog(config);
  const runner = createTaskRunner({ spawnImpl });

  const run = runner.start(catalog['content-generate']);
  calls[0].child.stderr.emit('data', Buffer.from('building\n'));

  runner.stop();
  await assert.rejects(run.completed, /Task stopped/);
  await new Promise((resolve) => setImmediate(resolve));

  const status = runner.getStatus();
  assert.equal(status.running, false);
  assert.equal(status.activeTask, null);
  assert.deepEqual(status.lastTask, {
    id: status.lastTask.id,
    key: 'content-generate',
    label: '过滤并优化文档',
    command: 'python3',
    args: ['src/pipeline.py', '--source', './output', '--content-only'],
    cwd: '/tmp',
    status: 'stopped',
    startedAt: status.lastTask.startedAt,
    finishedAt: status.lastTask.finishedAt,
    exitCode: null,
    logs: [
      '>>> 开始: 过滤并优化文档 (content-generate)',
      '命令: python3 src/pipeline.py --source ./output --content-only',
      '目录: /tmp',
      '[stderr] building',
      '<<< 已停止: 过滤并优化文档 (content-generate)',
    ],
    error: null,
  });
  assert.ok(status.lastTask.finishedAt);
  assert.deepEqual(runner.getLogs(), [
    '>>> 开始: 过滤并优化文档 (content-generate)',
    '命令: python3 src/pipeline.py --source ./output --content-only',
    '目录: /tmp',
    '[stderr] building',
    '<<< 已停止: 过滤并优化文档 (content-generate)',
  ]);
});

test('createTaskRunner stop reports when there is no running task', () => {
  const { calls, spawnImpl } = createSpawnStub();
  const runner = createTaskRunner({ spawnImpl });

  assert.throws(() => runner.stop(), /当前没有运行中的任务/);
  assert.equal(calls.length, 0);
});

test('createTaskRunner rejects invalid task definitions before spawn', () => {
  const { calls, spawnImpl } = createSpawnStub();
  const runner = createTaskRunner({ spawnImpl });

  assert.throws(() => runner.start(null), /Invalid task definition/);
  assert.equal(calls.length, 0);
});

test('createTaskRunner can be created with default dependencies', () => {
  const runner = createTaskRunner();

  assert.equal(typeof runner.getStatus, 'function');
  assert.equal(typeof runner.start, 'function');
  assert.equal(typeof runner.startComposite, 'function');
  assert.equal(typeof runner.stop, 'function');
  assert.equal(typeof runner.getLogs, 'function');
});

test('createTaskRunner clears the lock when spawn throws synchronously', async () => {
  const config = buildServerConfig({ cwd: '/tmp/example-site' });
  const catalog = createTaskCatalog(config);
  let calls = 0;
  const runner = createTaskRunner({
    spawnImpl() {
      calls += 1;
      throw new Error('spawn failed');
    },
  });

  const run = runner.start(catalog['docs-build']);

  await assert.rejects(run.completed, /spawn failed/);
  assert.equal(calls, 1);
  assert.equal(runner.getStatus().running, false);
  assert.equal(runner.getStatus().lastTask.status, 'failed');
});

test('late close events from an old run do not clear a newer active run', async () => {
  const { calls, spawnImpl } = createSpawnStub();
  const config = buildServerConfig({ cwd: '/tmp/example-site' });
  const catalog = createTaskCatalog(config);
  const runner = createTaskRunner({ spawnImpl });

  const firstRun = runner.start(catalog['docs-build']);
  calls[0].child.emit('error', new Error('first failed'));
  await assert.rejects(firstRun.completed, /first failed/);

  const secondRun = runner.start(catalog['docs-sidebar']);
  calls[0].child.emit('close', 1);
  assert.equal(runner.getStatus().activeTask.key, 'docs-sidebar');

  calls[1].child.emit('close', 0);
  await secondRun.completed;
});

test('createTaskRunner joins split stream chunks before formatting log lines', async () => {
  const { calls, spawnImpl } = createSpawnStub();
  const config = buildServerConfig({ cwd: '/tmp/example-site' });
  const catalog = createTaskCatalog(config);
  const runner = createTaskRunner({ spawnImpl });
  const run = runner.start(catalog['docs-build']);

  calls[0].child.stdout.emit('data', Buffer.from('\u001b[3'));
  calls[0].child.stdout.emit('data', Buffer.from('2mhel'));
  calls[0].child.stdout.emit('data', Buffer.from('lo\u001b[0m\n  ind'));
  calls[0].child.stdout.emit('data', Buffer.from('ented\n\npartial'));

  const chineseLine = Buffer.from('中文日志\n');
  calls[0].child.stderr.emit('data', chineseLine.subarray(0, 1));
  calls[0].child.stderr.emit('data', chineseLine.subarray(1, 4));
  calls[0].child.stderr.emit('data', chineseLine.subarray(4));

  assert.deepEqual(runner.getLogs().slice(3), [
    '[stdout] hello',
    '[stdout]   indented',
    '[stdout]',
    '[stderr] 中文日志',
  ]);

  calls[0].child.emit('close', 0);
  await run.completed;

  assert.deepEqual(runner.getLogs().slice(3), [
    '[stdout] hello',
    '[stdout]   indented',
    '[stdout]',
    '[stderr] 中文日志',
    '[stdout] partial',
    '<<< 完成: 构建站点 (docs-build), exit=0',
  ]);
});

test('createTaskRunner records only one terminal result after process errors', async () => {
  const { calls, spawnImpl } = createSpawnStub();
  const config = buildServerConfig({ cwd: '/tmp/example-site' });
  const catalog = createTaskCatalog(config);
  const runner = createTaskRunner({ spawnImpl });
  const run = runner.start(catalog['docs-build']);

  calls[0].child.stdout.emit('data', Buffer.from('partial output'));
  calls[0].child.emit('error', new Error('boom'));
  await assert.rejects(run.completed, /boom/);

  calls[0].child.emit('close', 0);
  await new Promise((resolve) => setImmediate(resolve));

  assert.deepEqual(runner.getLogs().slice(3), [
    '[stdout] partial output',
    '!!! 进程错误: boom',
    '<<< 失败: 构建站点 (docs-build), process-error',
  ]);
});

test('createTaskRunner streams Python output before the process exits', async () => {
  const runner = createTaskRunner();
  const run = runner.start({
    key: 'python-stream',
    label: 'Python 实时输出',
    command: 'python3',
    args: [
      '-c',
      'import time; print("first line"); time.sleep(1); print("second line")',
    ],
    cwd: process.cwd(),
  });

  try {
    const deadline = Date.now() + 3000;

    while (
      Date.now() < deadline &&
      runner.getStatus().running &&
      !runner.getLogs().includes('[stdout] first line')
    ) {
      await new Promise((resolve) => setTimeout(resolve, 20));
    }

    assert.equal(runner.getStatus().running, true);
    assert.ok(runner.getLogs().includes('[stdout] first line'));
  } finally {
    if (runner.getStatus().running) {
      runner.stop();
    }
    await run.completed.catch(() => {});
  }
});
