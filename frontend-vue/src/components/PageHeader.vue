<template>
  <div class="page-header">
    <div>
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="page-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({ title: String, subtitle: String })
</script>

<style scoped>
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; gap: 16px; flex-wrap: wrap; }
.page-title { position: relative; font-size: 30px; font-weight: 400; margin-bottom: 7px; }
.page-title::before { content: ''; display: inline-block; width: 22px; height: 3px; margin: 0 9px 7px 0; border-radius: 99px; background: var(--lime); }
.page-subtitle { color: var(--text-muted); font-size: 13px; max-width: 620px; }
.page-actions { display: flex; gap: 10px; flex-shrink: 0; }
</style>
