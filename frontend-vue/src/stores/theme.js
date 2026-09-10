import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const themeMode = ref(localStorage.getItem('theme-mode') || 'light')
  const resolvedTheme = ref('light')

  function resolveTheme() {
    if (themeMode.value === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return themeMode.value
  }

  function applyTheme() {
    resolvedTheme.value = resolveTheme()
    const root = document.documentElement
    if (resolvedTheme.value === 'dark') root.classList.add('dark')
    else root.classList.remove('dark')
  }

  function setThemeMode(mode) {
    themeMode.value = mode
    localStorage.setItem('theme-mode', mode)
    applyTheme()
  }

  // init
  applyTheme()

  // watch system preference when auto
  if (themeMode.value === 'auto') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme)
  }
  watch(themeMode, () => {
    applyTheme()
  })

  return { themeMode, resolvedTheme: computed(() => resolvedTheme.value), setThemeMode }
})
