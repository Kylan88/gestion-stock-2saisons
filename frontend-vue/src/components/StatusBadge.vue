<template>
  <span class="badge" :class="[badgeClass, sizeClass]" :title="label">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'
import { labelFor, classFor } from '../utils/statuses'

const props = defineProps({
  status: { type: String, default: '' },
  size: { type: String, default: 'md', validator: v => ['sm', 'md', 'lg'].includes(v) },
})

const badgeClass = computed(() => classFor(props.status))
const label = computed(() => labelFor(props.status))
const sizeClass = computed(() => `badge-${props.size}`)
</script>

<style scoped>
.badge {
  display: inline-flex; align-items: center; font-weight: 600;
  border-radius: 99px; white-space: nowrap;
}
.badge-sm { font-size: 10px; padding: 2px 8px; }
.badge-md { font-size: 11px; padding: 3px 10px; }
.badge-lg { font-size: 12px; padding: 5px 14px; }
</style>
