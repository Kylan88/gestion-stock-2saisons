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
.page-title { font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 700; color: #111827; margin-bottom: 4px; letter-spacing: -0.02em; }
.page-subtitle { color: #6b7280; font-size: 14px; max-width: 620px; }
.page-actions { display: flex; gap: 10px; flex-shrink: 0; }
</style>
