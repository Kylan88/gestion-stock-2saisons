<template>
  <div
    class="card stat-card"
    :class="[statusClass, $attrs.class]"
    @mouseenter="hover = true"
    @mouseleave="hover = false"
    :style="hover ? 'transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);' : ''"
  >
    <div style="display:flex;align-items:flex-start;justify-content:space-between">
      <div style="flex:1">
        <p style="font-size:14px;font-weight:500;color:#6b7280;margin-bottom:8px">{{ title }}</p>
        <p style="font-size:28px;font-weight:700;color:#111827">{{ value }}</p>
        <div v-if="trend" style="margin-top:8px;display:flex;align-items:center;gap:4px">
          <svg :class="trend.isPositive ? 'text-green-600' : 'text-red-600'" style="width:16px;height:16px" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path v-if="trend.isPositive" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
          </svg>
          <span :class="trend.isPositive ? 'text-green-600' : 'text-red-600'" style="font-size:12px;font-weight:500">{{ trend.value }}</span>
        </div>
      </div>
      <div v-if="icon" class="stat-icon" :class="iconClass">
        <slot name="icon"><span v-html="icon"></span></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
const props = defineProps({
  title: String,
  value: [String, Number],
  icon: String,
  trend: Object,
  status: { type: String, default: 'neutral' }
})
const hover = ref(false)
const statusClass = computed(() => ({
  success: 'stat-success',
  warning: 'stat-warning',
  error: 'stat-error',
  info: 'stat-info',
  neutral: 'stat-neutral'
}[props.status] || 'stat-neutral'))
const iconClass = computed(() => ({
  success: 'icon-success',
  warning: 'icon-warning',
  error: 'icon-error',
  info: 'icon-info',
  neutral: 'icon-neutral'
}[props.status] || 'icon-neutral'))
</script>

<style scoped>
.stat-card { border-width: 2px; transition: all 0.2s; }
.stat-success { background: #f0fdf4; border-color: #dcfce7; color: #15803d; }
.stat-warning { background: #fffbeb; border-color: #fef3c7; color: #d97706; }
.stat-error { background: #fef2f2; border-color: #fecaca; color: #dc2626; }
.stat-info { background: #eff6ff; border-color: #dbeafe; color: #2563eb; }
.stat-neutral { background: #f9fafb; border-color: #f3f4f6; color: #6b7280; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.icon-success { background: #dcfce7; color: #16a34a; }
.icon-warning { background: #fef3c7; color: #d97706; }
.icon-error { background: #fee2e2; color: #dc2626; }
.icon-info { background: #dbeafe; color: #2563eb; }
.icon-neutral { background: #f3f4f6; color: #6b7280; }
</style>
