const POLL_INTERVAL_MS = 750;

const statusOutput = document.querySelector('#status-output');
const statusSummary = document.querySelector('#status-summary');
const statusBadge = document.querySelector('#status-badge');
const logOutput = document.querySelector('#log-output');
const stopButton = document.querySelector('#stop-task');
const refreshStatusButton = document.querySelector('#refresh-status');
const clearLogsButton = document.querySelector('#clear-logs');

const groupContainers = {
  content: document.querySelector('#group-content'),
  site: document.querySelector('#group-site'),
  deploy: document.querySelector('#group-deploy'),
  full: document.querySelector('#group-full'),
};

const groupDefinitions = [
  {
    id: 'content',
    taskKeys: ['content-flow', 'pipeline-crawl', 'content-generate'],
  },
  {
    id: 'site',
    taskKeys: ['local-site-flow', 'site-build-local', 'docs-sidebar', 'docs-build', 'docs-refresh'],
  },
  {
    id: 'deploy',
    taskKeys: ['deploy-flow', 'validate-site-dist', 'deploy-site-dist', 'verify-online'],
  },
  {
    id: 'full',
    taskKeys: ['full-release-flow'],
  },
];

let taskButtons = [];
let currentStatus = { running: false, activeTask: null, lastTask: null };
let currentLogOwnerId = null;
let latestLogLines = [];
let hiddenLogLineCount = 0;

function formatTaskLabel(task) {
  if (!task) {
    return '暂无任务';
  }

  return `${task.label} (${task.key})`;
}

function formatTime(value) {
  if (!value) {
    return '未知时间';
  }

  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('zh-CN', { hour12: false });
}

function formatStatusSummary(status) {
  if (status.running && status.activeTask) {
    if (status.activeTask.status === 'stopping') {
      return `正在停止：${formatTaskLabel(status.activeTask)}`;
    }

    return `运行中：${formatTaskLabel(status.activeTask)}，开始于 ${formatTime(status.activeTask.startedAt)}`;
  }

  if (status.lastTask) {
    return `最近任务：${formatTaskLabel(status.lastTask)}，状态：${status.lastTask.status}，完成于 ${formatTime(status.lastTask.finishedAt)}`;
  }

  return '当前没有运行中的任务。';
}

function updateStatusBadge(status) {
  const stopping = status.running && status.activeTask?.status === 'stopping';
  const badgeText = stopping
    ? '正在停止'
    : status.running
      ? '运行中'
    : status.lastTask
      ? `最近：${status.lastTask.status}`
      : '空闲';

  const badgeClass = stopping ? 'stopping' : status.running ? 'running' : status.lastTask?.status || '';

  statusBadge.className = `badge${badgeClass ? ` ${badgeClass}` : ''}`;
  statusBadge.textContent = badgeText;
}

function setButtonsDisabled(status) {
  const running = Boolean(status.running);
  taskButtons.forEach((button) => {
    button.disabled = running;
  });
  stopButton.disabled = !running || status.activeTask?.status === 'stopping';
}

function createTaskCard(task) {
  const card = document.createElement('article');
  card.className = 'task-card';

  const button = document.createElement('button');
  button.type = 'button';
  button.dataset.task = task.key;
  button.textContent = task.label;

  const description = document.createElement('p');
  description.id = `task-description-${task.key}`;
  description.className = 'task-description';
  description.textContent = task.description;
  button.setAttribute('aria-describedby', description.id);

  button.addEventListener('click', () => {
    void runTask(task.key);
  });

  card.append(button, description);
  return { card, button };
}

function renderTaskGroups(tasks) {
  const taskMap = new Map(tasks.map((task) => [task.key, task]));
  taskButtons = [];

  groupDefinitions.forEach((group) => {
    const container = groupContainers[group.id];
    container.textContent = '';

    const groupTasks = group.taskKeys.map((key) => taskMap.get(key)).filter(Boolean);

    if (groupTasks.length === 0) {
      const empty = document.createElement('span');
      empty.className = 'empty-state';
      empty.textContent = '暂无可用任务';
      container.append(empty);
      return;
    }

    groupTasks.forEach((task) => {
      const { card, button } = createTaskCard(task);
      taskButtons.push(button);
      container.append(card);
    });
  });

  setButtonsDisabled(currentStatus);
}

function renderLogs() {
  const visibleLines = latestLogLines.slice(hiddenLogLineCount);
  logOutput.textContent = visibleLines.length > 0 ? visibleLines.join('\n') : '暂无日志';
  logOutput.scrollTop = logOutput.scrollHeight;
}

function syncLogOwner(status) {
  const nextOwnerId = status.activeTask?.id || status.lastTask?.id || null;

  if (nextOwnerId !== currentLogOwnerId) {
    currentLogOwnerId = nextOwnerId;
    hiddenLogLineCount = 0;
  }
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  let payload = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message = payload?.message || payload?.error || '请求失败';
    throw new Error(message);
  }

  return payload;
}

async function refreshTasks() {
  const tasks = await fetchJson('/api/admin/tasks');
  renderTaskGroups(Array.isArray(tasks) ? tasks : []);
}

async function refreshStatus() {
  const status = await fetchJson('/api/admin/status');
  currentStatus = status;
  syncLogOwner(status);
  statusSummary.textContent = formatStatusSummary(status);
  statusOutput.textContent = JSON.stringify(status, null, 2);
  updateStatusBadge(status);
  setButtonsDisabled(status);
}

async function refreshLogs() {
  const logs = await fetchJson('/api/admin/logs');
  latestLogLines = Array.isArray(logs) ? logs : logs?.logs || [];

  if (hiddenLogLineCount > latestLogLines.length) {
    hiddenLogLineCount = 0;
  }

  renderLogs();
}

async function refreshAll() {
  try {
    await refreshStatus();
    await refreshLogs();
  } catch (error) {
    statusSummary.textContent = `获取状态失败：${error.message}`;
    statusOutput.textContent = error.stack || String(error);
    updateStatusBadge({ running: false, lastTask: { status: 'failed' } });
  }
}

async function runTask(taskKey) {
  try {
    await fetchJson(`/api/admin/tasks/${taskKey}`, { method: 'POST' });
    hiddenLogLineCount = 0;
    await refreshAll();
  } catch (error) {
    window.alert(error.message || '任务启动失败');
  }
}

stopButton.addEventListener('click', async () => {
  try {
    await fetchJson('/api/admin/stop', { method: 'POST' });
    await refreshAll();
  } catch (error) {
    window.alert(error.message || '停止任务失败');
  }
});

refreshStatusButton.addEventListener('click', () => {
  void refreshAll();
});

clearLogsButton.addEventListener('click', () => {
  hiddenLogLineCount = latestLogLines.length;
  renderLogs();
});

await refreshTasks();
await refreshAll();

window.setInterval(() => {
  void refreshAll();
}, POLL_INTERVAL_MS);
