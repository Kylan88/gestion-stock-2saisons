import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import AppToast from './components/AppToast.vue'

const pinia = createPinia()
const app = createApp(App)
app.use(pinia)
app.use(router)
app.component('AppToast', AppToast)
// init theme avant mount pour que .dark soit effectif dès le premier rendu
import { useThemeStore } from './stores/theme'
const themeStore = useThemeStore(pinia)
if (themeStore.resolvedTheme === 'dark') document.documentElement.classList.add('dark')
else document.documentElement.classList.remove('dark')
app.mount('#app')
