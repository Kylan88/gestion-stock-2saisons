import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import AppToast from './components/AppToast.vue'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.component('AppToast', AppToast)
app.mount('#app')
