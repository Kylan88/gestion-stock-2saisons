<template>
  <div class="loading">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" class="spinner">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" opacity="0.2" />
      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
    </svg>
    <span>{{ text }}</span>
  </div>
</template>

<script setup>
defineProps({ text: { type: String, default: 'Chargement...' } })
</script>

<style scoped>
.spinner { animation: spin 0.8s linear infinite; color: var(--primary); }
@keyframes spin { to { transform: rotate(360deg); } }
.loading { display: flex; align-items: center; gap: 10px; padding: 60px 0; color: var(--text-muted); justify-content: center; font-size: 14px; }
</style>
