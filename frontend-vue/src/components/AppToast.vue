<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="store.toasts.length" class="toast-backdrop"></div>
    </Transition>
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div v-for="t in store.toasts" :key="t.id" class="toast" :class="'toast-' + t.type">
        <span class="toast-icon">
          <svg v-if="t.type==='success'" width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
          <svg v-else-if="t.type==='error'" width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          <svg v-else-if="t.type==='warning'" width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
        </span>
        <span class="toast-message">{{ t.message }}</span>
        <button class="toast-close" @click="store.remove(t.id)" aria-label="Fermer">×</button>
        <div class="toast-progress" :style="{ animationDuration: (t.type==='success'?3000:t.type==='error'?5000:t.type==='warning'?4500:4000)+'ms' }"></div>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { useToastStore } from '../stores/toast'
const store = useToastStore()
</script>

<style scoped>
.toast-backdrop { position: fixed; inset: 0; background: rgba(17,24,39,0.25); backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); z-index: 9998; pointer-events: none; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.toast-enter-active { animation: toastSlideDown 0.4s cubic-bezier(0.25,0.46,0.45,0.94); }
.toast-leave-active { animation: toastSlideUp 0.3s ease-in forwards; }
@keyframes toastSlideDown { from { opacity:0; transform: translateY(-100%) scale(0.9); } to { opacity:1; transform: translateY(0) scale(1); } }
@keyframes toastSlideUp { from { opacity:1; transform: translateY(0) scale(1); } to { opacity:0; transform: translateY(-100%) scale(0.9); } }
.toast-move { transition: transform 0.3s ease; }
</style>
