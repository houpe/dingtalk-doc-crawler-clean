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
  const deployHelpBetaCommand =
    `tar --no-mac-metadata -C '${distDir}' -cf /tmp/help-beta-vitepress.tar . && ` +
    `scp -o BatchMode=yes -o ConnectTimeout=15 /tmp/help-beta-vitepress.tar root@121.199.175.111:/tmp/help-beta-vitepress.tar && ` +
    `ssh -o BatchMode=yes -o ConnectTimeout=15 root@121.199.175.111 "mkdir -p /tmp/help-beta-backup && ` +
    `tar -C /www/wwwroot/help.beta.ztocc.com -cf /tmp/help-beta-backup/help.beta.ztocc.com-$(date +%Y%m%d%H%M%S).tar --exclude=.well-known . && ` +
    `find /www/wwwroot/help.beta.ztocc.com -mindepth 1 -maxdepth 1 ! -name '.well-known' -exec rm -rf {} + && ` +
    `tar -C /www/wwwroot/help.beta.ztocc.com -xf /tmp/help-beta-vitepress.tar"`;
  const deployHoupeWikiCommand =
    `tar --no-mac-metadata -C '${distDir}' -cf /tmp/houpe-wiki-vitepress.tar . && ` +
    `scp -o BatchMode=yes -o ConnectTimeout=15 /tmp/houpe-wiki-vitepress.tar root@42.192.205.206:/tmp/houpe-wiki-vitepress.tar && ` +
    `ssh -o BatchMode=yes -o ConnectTimeout=15 root@42.192.205.206 "mkdir -p /zto /tmp/houpe-wiki-backup && ` +
    `tar -C /zto -cf /tmp/houpe-wiki-backup/wiki.houpe.top-$(date +%Y%m%d%H%M%S).tar . && ` +
    `find /zto -mindepth 1 -maxdepth 1 -exec rm -rf {} + && ` +
    `tar -C /zto -xf /tmp/houpe-wiki-vitepress.tar"`;

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
      label: '增量抓取钉钉文档',
      description:
        '第一步的子任务：只重新下载新增或有更新的钉钉文档和图片，并根据系统更新日志生成待核对手册清单；不会优化、构建或部署。',
      command: 'python3',
      args: ['src/dws_crawler.py'],
      cwd: config.projectRoot,
    },
    {
      key: 'pipeline-crawl-full',
      label: '全量重抓钉钉文档',
      description:
        '清空本地 output 和抓取状态后，从钉钉完整重新下载 Markdown 和图片；首次初始化、状态异常或需彻底对齐时使用。不会优化、构建或部署。',
      command: 'python3',
      args: ['src/dws_crawler.py', '--full'],
      cwd: config.projectRoot,
    },
    {
      key: 'content-generate',
      label: '过滤并优化文档',
      description:
        '第一步的子任务：过滤并优化 output，使用 GPT 5.5 做语义增强（增量，只处理有更新的文档），生成 output_optimized；不会写入 site/docs、构建站点或部署。',
      command: 'bash',
      args: [
        '-lc',
        'set -a; [ -f .env ] && source .env; set +a; ' +
        'DOC_OPTIMIZER_API_URL="${DOC_OPTIMIZER_API_URL:-https://sub2api-qbxihjpy.sealoshzh.site/v1/chat/completions}" ' +
        'DOC_OPTIMIZER_MODEL="${DOC_OPTIMIZER_MODEL:-gpt-5.5}" ' +
        'DOC_OPTIMIZER_WIRE_API="${DOC_OPTIMIZER_WIRE_API:-chat}" ' +
        'python3 src/pipeline.py --source ./output --content-only --use-ai --model "${DOC_OPTIMIZER_MODEL:-gpt-5.5}"',
      ],
      cwd: config.projectRoot,
    },
    {
      key: 'content-generate-full',
      label: '全量重优化文档',
      description:
        '第一步的子任务：忽略增量，强制用 GPT 5.5 重新优化 output 全部文档，生成 output_optimized。产物异常或想彻底重刷时使用；耗时较长。不会写入 site/docs、构建站点或部署。',
      command: 'bash',
      args: [
        '-lc',
        'set -a; [ -f .env ] && source .env; set +a; ' +
        'DOC_OPTIMIZER_API_URL="${DOC_OPTIMIZER_API_URL:-https://sub2api-qbxihjpy.sealoshzh.site/v1/chat/completions}" ' +
        'DOC_OPTIMIZER_MODEL="${DOC_OPTIMIZER_MODEL:-gpt-5.5}" ' +
        'DOC_OPTIMIZER_WIRE_API="${DOC_OPTIMIZER_WIRE_API:-chat}" ' +
        'python3 src/pipeline.py --source ./output --content-only --use-ai --force-optimize --model "${DOC_OPTIMIZER_MODEL:-gpt-5.5}"',
      ],
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
      key: 'deploy-help-beta-site-dist',
      label: '部署到帮助中心',
      description:
        '打包当前 site/docs/.vitepress/dist，备份并覆盖 https://help.beta.ztocc.com 的站点目录，同时保留远端 .well-known。',
      command: 'bash',
      args: ['-lc', deployHelpBetaCommand],
      cwd: config.projectRoot,
    },
    {
      key: 'verify-help-beta-online',
      label: '校验帮助中心',
      description:
        '只读请求 https://help.beta.ztocc.com 首页，检查标题和描述元信息是否为预期内容。',
      command: 'bash',
      args: [
        '-lc',
        `set -euo pipefail; page=$(curl -fsS --connect-timeout 10 --max-time 20 "https://help.beta.ztocc.com/"); grep -Fq '<title>中通冷链</title>' <<<"$page"; grep -Fq '<meta name="description" content="中通冷链操作手册">' <<<"$page"; printf '%s\\n' '<title>中通冷链</title>' '<meta name="description" content="中通冷链操作手册">'`,
      ],
      cwd: config.projectRoot,
    },
    {
      key: 'deploy-houpe-wiki-site-dist',
      label: '部署到 wiki.houpe.top',
      description:
        '打包当前 site/docs/.vitepress/dist，备份并覆盖 https://wiki.houpe.top/ 的站点目录。',
      command: 'bash',
      args: ['-lc', deployHoupeWikiCommand],
      cwd: config.projectRoot,
    },
    {
      key: 'verify-houpe-wiki-online',
      label: '校验 wiki.houpe.top',
      description:
        '只读请求 https://wiki.houpe.top/ 首页，检查标题和描述元信息是否为预期内容。',
      command: 'bash',
      args: [
        '-lc',
        `set -euo pipefail; page=$(curl -fsS --connect-timeout 10 --max-time 20 "https://wiki.houpe.top/"); grep -Fq '<title>中通冷链</title>' <<<"$page"; grep -Fq '<meta name="description" content="中通冷链操作手册">' <<<"$page"; printf '%s\\n' '<title>中通冷链</title>' '<meta name="description" content="中通冷链操作手册">'`,
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
  'deploy-help-beta-flow': Object.freeze({
    key: 'deploy-help-beta-flow',
    label: '部署帮助中心',
    description:
      '校验当前 dist 后，部署到 https://help.beta.ztocc.com 并校验线上首页；不会重新抓取或构建。',
    steps: Object.freeze([
      'validate-site-dist',
      'deploy-help-beta-site-dist',
      'verify-help-beta-online',
    ]),
  }),
  'deploy-houpe-wiki-flow': Object.freeze({
    key: 'deploy-houpe-wiki-flow',
    label: '部署 wiki.houpe.top',
    description:
      '校验当前 dist 后，部署到 https://wiki.houpe.top/ 并校验线上首页；不会重新抓取或构建。',
    steps: Object.freeze([
      'validate-site-dist',
      'deploy-houpe-wiki-site-dist',
      'verify-houpe-wiki-online',
    ]),
  }),
  'full-release-help-beta-flow': Object.freeze({
    key: 'full-release-help-beta-flow',
    label: '全量一键发布到帮助中心',
    description:
      '依次执行文档生成、本地站点构建，再发布到 https://help.beta.ztocc.com 并校验；任一步失败即停止。',
    steps: Object.freeze([
      'pipeline-crawl',
      'content-generate',
      'site-build-local',
      'validate-site-dist',
      'deploy-help-beta-site-dist',
      'verify-help-beta-online',
    ]),
  }),
  'full-release-houpe-wiki-flow': Object.freeze({
    key: 'full-release-houpe-wiki-flow',
    label: '全量一键发布到 wiki.houpe.top',
    description:
      '依次执行文档生成、本地站点构建，再发布到 https://wiki.houpe.top/ 并校验；任一步失败即停止。',
    steps: Object.freeze([
      'pipeline-crawl',
      'content-generate',
      'site-build-local',
      'validate-site-dist',
      'deploy-houpe-wiki-site-dist',
      'verify-houpe-wiki-online',
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
