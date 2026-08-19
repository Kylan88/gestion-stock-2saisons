<template>
  <div class="workflow-bar">
    <div
      v-for="(step, i) in WORKFLOW"
      :key="step.key"
      class="wf-step"
      :class="{
        'wf-done': stepIndex(step.key) < currentIndex,
        'wf-current': stepIndex(step.key) === currentIndex,
        'wf-pending': stepIndex(step.key) > currentIndex,
      }"
    >
      <div class="wf-dot">
        <svg v-if="stepIndex(step.key) < currentIndex" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        <span v-else-if="stepIndex(step.key) === currentIndex" class="wf-pulse"></span>
        <span v-else class="wf-num">{{ i + 1 }}</span>
      </div>
      <span class="wf-label">{{ step.label }}</span>
      <div v-if="i < WORKFLOW.length - 1" class="wf-line" :class="{ 'wf-line-done': stepIndex(step.key) < currentIndex }"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { toCanonical } from '../utils/statuses'

const WORKFLOW = [
  { key: 'reception', label: 'Réception' },
  { key: 'en_musserie', label: 'Musserie' },
  { key: 'en_production', label: 'Production' },
  { key: 'conditionne', label: 'Conditionnement' },
  { key: 'en_stock', label: 'Stock' },
]

const props = defineProps({
  statut: { type: String, default: '' },
})

const currentIndex = computed(() => {
  const canonical = toCanonical(props.statut)
  const idx = WORKFLOW.findIndex(s => s.key === canonical)
  return idx >= 0 ? idx : 0
})

function stepIndex(key) {
  return WORKFLOW.findIndex(s => s.key === key)
}
</script>

<style scoped>
.workflow-bar {
  display: flex; align-items: center; gap: 0;
  padding: 8px 0; overflow-x: auto;
}
.wf-step {
  display: flex; align-items: center; gap: 4px; position: relative;
  white-space: nowrap;
}
.wf-dot {
  width: 26px; height: 26px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; transition: all 0.3s ease;
}
.wf-done .wf-dot { background: var(--success); color: white; }
.wf-current .wf-dot { background: var(--primary); color: white; box-shadow: 0 0 0 4px rgba(22,91,61,0.16); }
.wf-pending .wf-dot { background: var(--surface); color: var(--text-muted); border: 1.5px solid var(--border); }
.wf-label { font-size: 11px; font-weight: 500; color: var(--text-secondary); }
.wf-done .wf-label { color: var(--success); font-weight: 600; }
.wf-current .wf-label { color: var(--primary); font-weight: 600; }
.wf-pending .wf-label { color: var(--text-muted); }
.wf-line {
  width: 24px; height: 2px; background: var(--border);
  margin: 0 2px; flex-shrink: 0; transition: background 0.3s;
}
.wf-line-done { background: var(--success); }
.wf-pulse {
  width: 8px; height: 8px; border-radius: 50%; background: white;
  animation: pulse 1.5s ease infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.3); }
}
</style>
