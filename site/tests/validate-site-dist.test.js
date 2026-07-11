import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { validateSiteDist } from '../lib/validate-site-dist.js';

function createFixture(t) {
  const cwd = mkdtempSync(join(tmpdir(), 'zto-dist-validation-'));
  const docsDir = join(cwd, 'docs');
  const distDir = join(docsDir, '.vitepress', 'dist');

  mkdirSync(join(docsDir, 'guide'), { recursive: true });
  mkdirSync(join(distDir, 'guide'), { recursive: true });
  writeFileSync(join(docsDir, 'index.md'), '# Home\n');
  writeFileSync(join(docsDir, 'guide', 'topic.md'), '# Topic\n');
  writeFileSync(join(distDir, 'index.html'), '<!doctype html>Home');
  writeFileSync(join(distDir, '404.html'), '<!doctype html>Not found');
  writeFileSync(join(distDir, 'edit.html'), '<!doctype html>Edit');
  writeFileSync(join(distDir, 'guide', 'topic.html'), '<!doctype html>Topic');

  t.after(() => rmSync(cwd, { recursive: true, force: true }));
  return { docsDir, distDir };
}

test('validateSiteDist accepts a complete VitePress build', (t) => {
  const fixture = createFixture(t);

  assert.deepEqual(validateSiteDist(fixture), {
    markdownCount: 2,
    generatedHtmlCount: 2,
  });
});

test('validateSiteDist rejects a partial build before deployment', (t) => {
  const fixture = createFixture(t);
  writeFileSync(join(fixture.docsDir, 'guide', 'missing.md'), '# Missing\n');

  assert.throws(
    () => validateSiteDist(fixture),
    /构建产物不完整：Markdown 3 个，页面 HTML 2 个/,
  );
});
