import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const stylesheet = readFileSync(join(process.cwd(), 'docs/.vitepress/theme/style.css'), 'utf8');
const themeScript = readFileSync(join(process.cwd(), 'docs/.vitepress/theme/index.js'), 'utf8');

test('dark mode gives inline emphasis a distinct color and stronger weight', () => {
  assert.match(
    stylesheet,
    /:root\.dark \.vp-doc strong\s*\{[^}]*color:\s*#fde68a;[^}]*font-weight:\s*750;/s,
  );
});

test('dark mode gives inline code a visible contrast treatment', () => {
  assert.match(
    stylesheet,
    /:root\.dark \.vp-doc :not\(pre\) > code\s*\{[^}]*border:[^;]+;[^}]*font-weight:\s*650;/s,
  );
});

test('sidebar gives each navigation level a distinct size and contrast', () => {
  assert.match(stylesheet, /\.VPSidebarItem\.level-0[^}]*font-size:\s*16px;[^}]*color:\s*var\(--vp-c-text-1\);/s);
  assert.match(stylesheet, /\.VPSidebarItem\.level-1[^}]*font-size:\s*15px;[^}]*color:\s*var\(--vp-c-text-2\);/s);
  assert.match(stylesheet, /\.VPSidebarItem\.level-2[^}]*font-size:\s*14px;[^}]*color:\s*var\(--vp-c-text-3\);/s);
  assert.match(stylesheet, /\.VPSidebarItem\.is-active[^}]*color:\s*var\(--vp-c-brand-1\);/s);
});

test('sidebar uses a subtle tree guide and an active-row treatment', () => {
  assert.match(stylesheet, /\.VPSidebarItem \.items\s*\{[^}]*border-left:\s*1px solid var\(--zto-sidebar-tree\);/s);
  assert.match(stylesheet, /\.VPSidebarItem \.items > \.VPSidebarItem::before\s*\{[^}]*border-top:\s*1px solid var\(--zto-sidebar-tree\);/s);
  assert.match(stylesheet, /\.VPSidebarItem\.is-active > \.item,[^}]*\{[^}]*background:\s*var\(--vp-c-brand-soft\);/s);
});

test('images taller than 800px are proportionally constrained to 500px', () => {
  assert.match(themeScript, /naturalHeight\s*>\s*800/);
  assert.match(
    stylesheet,
    /\.vp-doc img\.vp-doc-tall-image\s*\{[^}]*max-height:\s*500px;[^}]*width:\s*auto;/s,
  );
});
