function cloneTask(task) {
  return {
    key: task.key,
    label: task.label,
    description: task.description,
    command: task.command,
    args: [...task.args],
    cwd: task.cwd,
  };
}

function deepFreezeTask(task) {
  Object.freeze(task.args);
  return Object.freeze(task);
}

function buildTaskList(config) {
  const distDir = `${config.docsDir}/.vitepress/dist`;
  const deployCommand =
    `tar --no-mac-metadata -C '${distDir}' -cf /tmp/help-beta-vitepress.tar . && ` +
    `scp /tmp/help-beta-vitepress.tar root@121.199.175.111:/tmp/help-beta-vitepress.tar && ` +
    `ssh root@121.199.175.111 "mkdir -p /tmp/help-beta-backup && ` +
    `tar -C /www/wwwroot/help.beta.ztocc.com -cf /tmp/help-beta-backup/help.beta.ztocc.com-$(date +%Y%m%d%H%M%S).tar --exclude=.well-known . && ` +
    `find /www/wwwroot/help.beta.ztocc.com -mindepth 1 -maxdepth 1 ! -name '.well-known' -exec rm -rf {} + && ` +
    `tar -C /www/wwwroot/help.beta.ztocc.com -xf /tmp/help-beta-vitepress.tar"`;

  return [
    {
      key: 'docs-sidebar',
      label: '刷新侧边栏',
      description:
        '扫描 site/docs，更新自动生成的目录 index.md 和侧边栏数据；不会构建或部署站点。',
      command: 'python3',
      args: ['../src/gen_sidebar.py', 'docs'],
      cwd: config.cwd,
    },
    {
      key: 'docs-build',
      label: '构建站点',
      description:
        '使用当前 site/docs 构建 VitePress，产物写入 .vitepress/dist；不会刷新侧边栏或部署。',
      command: 'npm',
      args: ['run', 'build'],
      cwd: config.cwd,
    },
    {
      key: 'docs-refresh',
      label: '刷新并构建站点',
      description:
        '先刷新目录索引和侧边栏，再构建 VitePress dist；适合调整目录、文件名或增删文档后使用。',
      command: 'npm',
      args: ['run', 'docs:refresh'],
      cwd: config.cwd,
    },
    {
      key: 'pipeline-crawl',
      label: '抓取钉钉文档',
      description:
        '第一步的子任务：清理旧 output 后，从固定钉钉知识库重新抓取 Markdown 和图片；不会优化、构建或部署。',
      command: 'python3',
      args: ['src/dws_crawler.py'],
      cwd: config.projectRoot,
    },
    {
      key: 'content-generate',
      label: '过滤并优化文档',
      description:
        '第一步的子任务：过滤并优化 output，生成 output_optimized；不会写入 site/docs、构建站点或部署。',
      command: 'python3',
      args: ['src/pipeline.py', '--source', './output', '--content-only'],
      cwd: config.projectRoot,
    },
    {
      key: 'site-build-local',
      label: '从优化结果生成本地站点',
      description:
        '第二步的子任务：使用 output_optimized 重建 site/docs、侧边栏和 VitePress dist；本机刷新即可预览，不会部署服务器。',
      command: 'python3',
      args: ['src/pipeline.py', '--source', './output_optimized', '--site-only', '--no-serve'],
      cwd: config.projectRoot,
    },
    {
      key: 'validate-site-dist',
      label: '校验本地构建产物',
      description:
        '部署前比较 site/docs 的 Markdown 数量与 dist 页面数量，并检查首页和 404 页面；不会修改文件或部署。',
      command: 'node',
      args: ['lib/validate-site-dist.js'],
      cwd: config.cwd,
    },
    {
      key: 'deploy-site-dist',
      label: '部署站点 dist',
      description:
        '打包当前 site/docs/.vitepress/dist，备份并覆盖 help.beta.ztocc.com 的站点目录，同时保留远端 .well-known。',
      command: 'bash',
      args: ['-lc', deployCommand],
      cwd: config.projectRoot,
    },
    {
      key: 'verify-online',
      label: '校验线上站点',
      description:
        '只读请求 help.beta.ztocc.com 首页，检查标题和描述元信息是否为预期内容。',
      command: 'bash',
      args: [
        '-lc',
        `set -euo pipefail; page=$(curl -fsS "https://help.beta.ztocc.com/"); grep -Fq '<title>中通冷链</title>' <<<"$page"; grep -Fq '<meta name="description" content="中通冷链操作手册">' <<<"$page"; printf '%s\\n' '<title>中通冷链</title>' '<meta name="description" content="中通冷链操作手册">'`,
      ],
      cwd: config.projectRoot,
    },
  ];
}

const COMPOSITE_TASKS = Object.freeze({
  'content-flow': Object.freeze({
    key: 'content-flow',
    label: '第一步：文档生成流程',
    description:
      '钉钉拉取 → 过滤并优化，产出 output 和 output_optimized；不会修改 site/docs、构建站点或部署。',
    steps: Object.freeze(['pipeline-crawl', 'content-generate']),
  }),
  'local-site-flow': Object.freeze({
    key: 'local-site-flow',
    label: '第二步：本地站点流程',
    description:
      '读取 output_optimized，生成 site/docs、侧边栏和 dist；通过本机 4000 端口预览，不会部署服务器。',
    steps: Object.freeze(['site-build-local']),
  }),
  'deploy-flow': Object.freeze({
    key: 'deploy-flow',
    label: '第三步：部署到服务器',
    description:
      '部署当前 site/docs/.vitepress/dist，完成远端备份与覆盖后校验线上首页；不会重新抓取或构建。',
    steps: Object.freeze(['validate-site-dist', 'deploy-site-dist', 'verify-online']),
  }),
  'full-release-flow': Object.freeze({
    key: 'full-release-flow',
    label: '全量一键流程',
    description:
      '依次执行文档生成、本地站点构建、服务器部署和线上校验；任一步失败即停止。',
    steps: Object.freeze([
      'pipeline-crawl',
      'content-generate',
      'site-build-local',
      'validate-site-dist',
      'deploy-site-dist',
      'verify-online',
    ]),
  }),
});

export function createTaskCatalog(config) {
  return Object.freeze(
    Object.fromEntries(
      buildTaskList(config).map((task) => [task.key, deepFreezeTask(cloneTask(task))]),
    ),
  );
}

export function createCompositeTaskSteps(taskKey) {
  return COMPOSITE_TASKS[taskKey] ? [...COMPOSITE_TASKS[taskKey].steps] : null;
}

export function getCompositeTaskDefinition(taskKey) {
  const task = COMPOSITE_TASKS[taskKey];

  if (!task) {
    return null;
  }

  return {
    key: task.key,
    label: task.label,
    description: task.description,
    steps: [...task.steps],
  };
}

export function listCompositeTaskDefinitions() {
  return Object.values(COMPOSITE_TASKS).map((task) => ({
    key: task.key,
    label: task.label,
    description: task.description,
  }));
}
