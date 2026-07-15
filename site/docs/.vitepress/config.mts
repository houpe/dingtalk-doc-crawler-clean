import { defineConfig } from 'vitepress'
import sidebar from './sidebar-data.mjs'
import rewrites from './rewrites-data.mjs'

export default defineConfig({
  ignoreDeadLinks: true,
  lang: 'zh-CN',
  title: '中通冷链',
  description: '中通冷链操作手册',
  cleanUrls: true,
  lastUpdated: true,
  rewrites,

  head: [['link', { rel: 'icon', type: 'image/png', href: '/favicon.png' }]],

  themeConfig: {
    logo: '/favicon.png',

    nav: [
      { text: '首页', link: '/' },
      { text: '网点操作', link: '/网点操作/' },
      { text: '云仓操作', link: '/云仓操作/' },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/houpe/dingtalk-doc-crawler' },
    ],

    sidebar: sidebar,

    footer: {
      message: '中通冷链操作手册',
      copyright: `Copyright © ${new Date().getFullYear()} 中通冷链`,
    },

    search: {
      provider: 'local',
      options: { locales: { root: { translations: { button: { buttonText: '搜索文档' } } } } },
    },

    outline: { label: '本页目录', level: [2, 4] },

    docFooter: { prev: '上一篇', next: '下一篇' },

    lastUpdated: { text: '最后更新于' },

    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '菜单',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
  },
})
