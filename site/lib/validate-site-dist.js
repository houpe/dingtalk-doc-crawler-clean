import { existsSync, readdirSync } from 'node:fs';
import { basename, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

function collectFiles(root, { skipDirectoryNames = new Set() } = {}) {
  if (!existsSync(root)) {
    throw new Error(`目录不存在: ${root}`);
  }

  const files = [];

  function walk(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      if (entry.isDirectory()) {
        if (!skipDirectoryNames.has(entry.name)) {
          walk(join(directory, entry.name));
        }
        continue;
      }

      if (entry.isFile()) {
        files.push(join(directory, entry.name));
      }
    }
  }

  walk(root);
  return files;
}

export function validateSiteDist({ docsDir, distDir }) {
  const requiredFiles = [join(distDir, 'index.html'), join(distDir, '404.html')];

  for (const filePath of requiredFiles) {
    if (!existsSync(filePath)) {
      throw new Error(`构建产物不完整，缺少: ${filePath}`);
    }
  }

  const markdownCount = collectFiles(docsDir, {
    skipDirectoryNames: new Set(['.vitepress']),
  }).filter((filePath) => extname(filePath).toLowerCase() === '.md').length;

  const generatedHtmlCount = collectFiles(distDir).filter((filePath) => {
    if (extname(filePath).toLowerCase() !== '.html') {
      return false;
    }

    return !new Set(['404.html', 'edit.html']).has(basename(filePath));
  }).length;

  if (markdownCount === 0) {
    throw new Error(`site/docs 中没有 Markdown: ${docsDir}`);
  }

  if (generatedHtmlCount !== markdownCount) {
    throw new Error(
      `构建产物不完整：Markdown ${markdownCount} 个，页面 HTML ${generatedHtmlCount} 个`,
    );
  }

  return { markdownCount, generatedHtmlCount };
}

function main() {
  const cwd = process.cwd();
  const docsDir = join(cwd, 'docs');
  const distDir = join(docsDir, '.vitepress', 'dist');
  const result = validateSiteDist({ docsDir, distDir });

  console.log(`构建产物校验通过：Markdown ${result.markdownCount} 个，页面 HTML ${result.generatedHtmlCount} 个`);
}

if (resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    main();
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
