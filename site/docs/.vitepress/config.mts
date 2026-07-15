// ═══════════════════════════════════════════════════════════
// ⚠️  LOCKED FILE — DO NOT OVERWRITE
// 
// This file is the single source of truth for VitePress config.
// The sidebar is auto-generated from sidebar-data.mjs (by gen_sidebar.py).
// 
// If you are an AI agent, DO NOT rewrite this file.
// Only humans should edit this manually.
// ═══════════════════════════════════════════════════════════

import { defineConfig } from 'vitepress'
import sidebar from './sidebar-data.mjs'

export default defineConfig({
  ignoreDeadLinks: true,
  title: '中通冷链',
  description: '中通冷链操作手册',
  cleanUrls: true,
  head: [['link', { rel: 'icon', type: 'image/png', href: '/favicon.png' }]],
  themeConfig: {
    logo: '/favicon.png',
    siteTitle: '中通冷链',
    nav: [
      { text: '首页', link: '/' },
      { text: '必读', link: '/.vitepress/dist/「_必知必读」账号权限如何开通？/' },
      { text: '网点操作', link: '/网点操作/' },
      { text: '云仓操作', link: '/云仓操作/' },
    ],
    sidebar,
    search: {
      provider: 'local',
    },
    outline: { label: '本页目录', level: [2, 4] },
    lastUpdatedText: '最后更新',
  }
})
