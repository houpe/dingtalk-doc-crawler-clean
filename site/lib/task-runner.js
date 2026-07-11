import { spawn } from 'node:child_process';
import { StringDecoder } from 'node:string_decoder';
import { stripVTControlCharacters } from 'node:util';

function cloneTask(task) {
  if (!task) {
    return null;
  }

  const cloned = {
    key: task.key,
    label: task.label,
  };

  if (typeof task.command === 'string') {
    cloned.command = task.command;
  }

  if (Array.isArray(task.args)) {
    cloned.args = [...task.args];
  }

  if (typeof task.cwd === 'string') {
    cloned.cwd = task.cwd;
  }

  if (Array.isArray(task.steps)) {
    cloned.steps = [...task.steps];
  }

  return cloned;
}

function cloneRun(run) {
  if (!run) {
    return null;
  }

  return {
    id: run.id,
    ...cloneTask(run.task),
    status: run.status,
    startedAt: run.startedAt,
    finishedAt: run.finishedAt,
    exitCode: run.exitCode,
    logs: [...run.logs],
    error: run.error,
  };
}

function appendLog(run, chunk) {
  const lines = stripVTControlCharacters(String(chunk))
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  run.logs.push(...lines);
}

function appendStreamLine(run, line, stream) {
  const cleaned = stripVTControlCharacters(line).trimEnd();
  run.logs.push(cleaned ? `[${stream}] ${cleaned}` : `[${stream}]`);
}

function createStreamLogger(run, stream) {
  let buffer = '';
  const decoder = new StringDecoder('utf8');

  return {
    append(chunk) {
      const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(String(chunk));
      buffer += decoder.write(bytes);

      const lineBreak = /\r\n|\n|\r(?!$)/g;
      let lineStart = 0;
      let match;

      while ((match = lineBreak.exec(buffer))) {
        appendStreamLine(run, buffer.slice(lineStart, match.index), stream);
        lineStart = match.index + match[0].length;
      }

      buffer = buffer.slice(lineStart);
    },
    flush() {
      buffer += decoder.end();

      if (buffer.endsWith('\r')) {
        buffer = buffer.slice(0, -1);
      }

      if (buffer.length > 0) {
        appendStreamLine(run, buffer, stream);
      }

      buffer = '';
    },
  };
}

function formatCommand(definition) {
  const args = definition.args.map((arg) =>
    /^[\w./:@%+=,-]+$/.test(arg) ? arg : JSON.stringify(arg),
  );

  return [definition.command, ...args].join(' ');
}

function appendTaskStart(run, definition) {
  appendLog(run, `>>> 开始: ${definition.label} (${definition.key})`);
  appendLog(run, `命令: ${formatCommand(definition)}`);
  appendLog(run, `目录: ${definition.cwd}`);
}

function isValidTaskDefinition(definition) {
  return Boolean(
    definition &&
      typeof definition.key === 'string' &&
      typeof definition.label === 'string' &&
      typeof definition.command === 'string' &&
      Array.isArray(definition.args) &&
      typeof definition.cwd === 'string',
  );
}

function taskExitError(code) {
  const error = new Error(`Task exited with code ${code}`);
  error.exitCode = code;
  return error;
}

function terminateChildProcessTree(child, signal = 'SIGTERM') {
  if (process.platform !== 'win32' && Number.isInteger(child?.pid)) {
    try {
      process.kill(-child.pid, signal);
      return;
    } catch {
      // Fall back to the direct child when a process group is unavailable.
    }
  }

  if (typeof child?.kill === 'function') {
    try {
      child.kill(signal);
    } catch {
      // The process may already have exited between the status check and signal.
    }
  }
}

export function createTaskRunner({
  spawnImpl = spawn,
  now = () => new Date().toISOString(),
} = {}) {
  let lastTask = null;
  let activeRun = null;
  let activeChild = null;
  let runCounter = 0;

  function assertIdle() {
    if (activeRun) {
      throw new Error('已有任务正在运行');
    }
  }

  function createRun(task) {
    let resolveRun;
    let rejectRun;
    const completed = new Promise((resolve, reject) => {
      resolveRun = resolve;
      rejectRun = reject;
    });

    const run = {
      id: `run-${++runCounter}`,
      task: cloneTask(task),
      status: 'running',
      startedAt: now(),
      finishedAt: null,
      exitCode: null,
      logs: [],
      error: null,
      forceKillTimer: null,
      resolve: resolveRun,
      reject: rejectRun,
    };

    activeRun = run;

    return { run, completed };
  }

  function finalizeRun(run, status, exitCode, error) {
    run.status = status;
    run.exitCode = exitCode;
    run.error = error || null;
    run.finishedAt = run.finishedAt || now();
    if (activeRun === run) {
      lastTask = run;
      activeRun = null;
      activeChild = null;
    }

    if (run.forceKillTimer) {
      clearTimeout(run.forceKillTimer);
      run.forceKillTimer = null;
    }
  }

  function runOne(definition, run) {
    appendTaskStart(run, definition);

    return new Promise((resolve, reject) => {
      let child;

      try {
        child = spawnImpl(definition.command, definition.args, {
          cwd: definition.cwd,
          detached: process.platform !== 'win32',
          env: { ...process.env, PYTHONUNBUFFERED: '1' },
          stdio: 'pipe',
        });
      } catch (error) {
        appendLog(run, `!!! 启动失败: ${error.message}`);
        appendLog(run, `<<< 失败: ${definition.label} (${definition.key}), spawn-error`);
        reject(error);
        return;
      }

      activeChild = child;
      let settled = false;
      const stdoutLogger = createStreamLogger(run, 'stdout');
      const stderrLogger = createStreamLogger(run, 'stderr');

      const flushStreamLogs = () => {
        stdoutLogger.flush();
        stderrLogger.flush();
      };

      const settle = (handler, value, appendTerminalLog) => {
        if (settled) {
          return;
        }

        settled = true;
        flushStreamLogs();
        appendTerminalLog();
        if (activeChild === child) {
          activeChild = null;
        }
        handler(value);
      };

      if (child.stdout?.on) {
        child.stdout.on('data', (chunk) => {
          if (!settled) {
            stdoutLogger.append(chunk);
          }
        });
      }

      if (child.stderr?.on) {
        child.stderr.on('data', (chunk) => {
          if (!settled) {
            stderrLogger.append(chunk);
          }
        });
      }

      child.on('error', (error) => {
        settle(reject, error, () => {
          appendLog(run, `!!! 进程错误: ${error.message}`);
          appendLog(run, `<<< 失败: ${definition.label} (${definition.key}), process-error`);
        });
      });
      child.on('close', (code) => {
        settle(resolve, code, () => {
          if (run.status === 'stopping') {
            appendLog(run, `<<< 已停止: ${definition.label} (${definition.key})`);
          } else if (code === 0) {
            appendLog(run, `<<< 完成: ${definition.label} (${definition.key}), exit=0`);
          } else {
            appendLog(run, `<<< 失败: ${definition.label} (${definition.key}), exit=${code}`);
          }
        });
      });
    });
  }

  function completeSuccess(run) {
    finalizeRun(run, 'success', 0, null);
    run.resolve(cloneRun(run));
  }

  function completeFailure(run, error) {
    const exitCode = Number.isInteger(error?.exitCode) ? error.exitCode : null;
    finalizeRun(run, 'failed', exitCode, error?.message || String(error));
    run.reject(error);
  }

  function completeStopped(run) {
    finalizeRun(run, 'stopped', null, null);
  }

  function start(definition) {
    assertIdle();

    if (!isValidTaskDefinition(definition)) {
      throw new Error('Invalid task definition');
    }

    const { run, completed } = createRun(definition);

    void (async () => {
      try {
        const code = await runOne(definition, run);

        if (run.status === 'stopping') {
          completeStopped(run);
          return;
        }

        if (code !== 0) {
          throw taskExitError(code);
        }

        completeSuccess(run);
      } catch (error) {
        if (run.status === 'stopping') {
          completeStopped(run);
        } else {
          completeFailure(run, error);
        }
      }
    })();

    return {
      runId: run.id,
      completed,
    };
  }

  function startComposite({ key, label, steps, catalog }) {
    assertIdle();

    if (typeof key !== 'string' || typeof label !== 'string' || !Array.isArray(steps)) {
      throw new Error('Invalid composite task definition');
    }

    const definitions = steps.map((stepKey) => {
      const definition = catalog?.[stepKey];

      if (!isValidTaskDefinition(definition)) {
        throw new Error(`Unknown composite task step: ${stepKey}`);
      }

      return definition;
    });

    const { run, completed } = createRun({ key, label, steps });

    void (async () => {
      try {
        for (const definition of definitions) {
          if (run.status === 'stopping') {
            completeStopped(run);
            return;
          }

          const code = await runOne(definition, run);

          if (run.status === 'stopping') {
            completeStopped(run);
            return;
          }

          if (code !== 0) {
            throw taskExitError(code);
          }
        }

        completeSuccess(run);
      } catch (error) {
        if (run.status === 'stopping') {
          completeStopped(run);
        } else {
          completeFailure(run, error);
        }
      }
    })();

    return {
      runId: run.id,
      completed,
    };
  }

  function getStatus() {
    return {
      running: activeRun !== null,
      activeTask: cloneRun(activeRun),
      lastTask: cloneRun(lastTask),
    };
  }

  function stop() {
    if (!activeRun) {
      throw new Error('当前没有运行中的任务');
    }

    if (activeRun.status === 'stopping') {
      throw new Error('任务正在停止');
    }

    const run = activeRun;
    const child = activeChild;
    run.status = 'stopping';
    run.reject(new Error('Task stopped'));

    terminateChildProcessTree(child);

    if (!child) {
      completeStopped(run);
    } else {
      run.forceKillTimer = setTimeout(() => {
        if (activeRun === run && run.status === 'stopping' && activeChild === child) {
          terminateChildProcessTree(child, 'SIGKILL');
        }
      }, 5000);
      run.forceKillTimer.unref?.();
    }

    return cloneRun(run);
  }

  function getLogs() {
    if (activeRun) {
      return [...activeRun.logs];
    }

    return lastTask ? [...lastTask.logs] : [];
  }

  return {
    getStatus,
    start,
    startComposite,
    stop,
    getLogs,
  };
}
