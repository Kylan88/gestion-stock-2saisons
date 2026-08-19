<template>
  <div class="empty-state anim-fade">
    <div class="empty-state-icon">
      <span v-if="icon !== '—'">{{ icon }}</span>
      <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
    </div>
    <div class="empty-state-title">{{ text }}</div>
    <p v-if="subtext" class="empty-state-subtext">{{ subtext }}</p>
    <div v-if="$slots.default" class="empty-state-action">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '—' },
  text: { type: String, default: 'Aucune donnée' },
  subtext: String,
})
</script>

<style scoped>
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 48px 20px; text-align: center;
}
.empty-state-icon {
  width: 56px; height: 56px; border-radius: 16px;
  background: var(--surface); display: flex; align-items: center; justify-content: center;
  margin-bottom: 16px; font-size: 28px; font-weight: 300; color: var(--border);
}
.empty-state-icon svg { color: var(--text-muted); }
.empty-state-title { font-size: 15px; font-weight: 600; color: var(--dark); margin-bottom: 4px; }
.empty-state-subtext { font-size: 13px; color: var(--text-muted); margin: 0; }
.empty-state-action { margin-top: 16px; }
</style>
