<template>
  <div v-if="rappels.length" class="rappels-banner">
    <div class="rappels-header">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <strong>{{ rappels.length }} lot(s) en attente</strong>
      <span style="font-size:11px;color:var(--text-muted)">— musserie d'hier sans chariots aujourd'hui ou étape bloquée >24h</span>
    </div>
    <div class="rappels-list">
      <div v-for="r in rappels" :key="r.lot_id + '_' + r.dryer + '_' + r.etape" class="rappel-item" :class="r.severite">
        <span class="rappel-lot">{{ r.code_lot }}</span>
        <span class="rappel-msg">{{ r.message }}</span>
        <router-link v-if="r.etape==='production'" :to="'/production/chariots'" class="btn btn-sm btn-outline">Aller → Chariots</router-link>
        <router-link v-else-if="r.etape==='musserie'" :to="'/musserie'" class="btn btn-sm btn-outline">Aller → Musserie</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRappels } from '../api'
const rappels = ref([])
onMounted(async () => { try { rappels.value = await getRappels(24) } catch {} })
</script>

<style scoped>
.rappels-banner{ background:#FFFBEB; border:1px solid #FDE68A; border-radius:var(--radius-md); padding:12px 16px; margin-bottom:16px}
.rappels-header{ display:flex; align-items:center; gap:8px; font-size:13px; color:#92400E; margin-bottom:8px}
.rappels-list{ display:flex; flex-direction:column; gap:6px}
.rappel-item{ display:flex; align-items:center; gap:10px; padding:8px 12px; background:white; border:1px solid #FDE68A; border-radius:8px; font-size:12px; flex-wrap:wrap}
.rappel-item.error{ border-color:#FCA5A5; background:#FEF2F2}
.rappel-lot{ font-weight:700; color:var(--dark)}
.rappel-msg{ flex:1; color:var(--text-secondary)}
</style>
