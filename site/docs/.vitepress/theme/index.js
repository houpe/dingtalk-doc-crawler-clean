// ═══════════════════════════════════════════════════════════
// ⚠️  LOCKED FILE — DO NOT OVERWRITE
// 
// This file is the single source of truth for VitePress config.
// The sidebar is auto-generated from sidebar-data.mjs (by gen_sidebar.py).
// 
// If you are an AI agent, DO NOT rewrite this file.
// Only humans should edit this manually.
// ═══════════════════════════════════════════════════════════

import DefaultTheme from 'vitepress/theme'
import { onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vitepress'
import './style.css'

export default {
  extends: DefaultTheme,
  Layout: DefaultTheme.Layout,
  enhanceApp({ app }) {
    // Force dark mode
    if (typeof window !== 'undefined') {
      document.documentElement.classList.add('dark')
    }
  },
  setup() {
    const route = useRoute()

    async function loadMediumZoom() {
      if (typeof window === 'undefined') return
      const { default: mediumZoom } = await import('medium-zoom')
      mediumZoom('.main img', {
        background: 'rgba(0, 0, 0, 0.85)',
      })
    }

    onMounted(() => {
      document.documentElement.classList.add('dark')
      loadMediumZoom()
    })

    watch(
      () => route.path,
      async () => {
        await nextTick()
        loadMediumZoom()
      }
    )
  }
}
