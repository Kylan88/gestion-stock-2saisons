<template>
  <div class="page">
    <PageHeader title="Anomalies" subtitle="Détection des lots avec workflow incomplet" />

    <LoadingSpinner v-if="loading" />

    <div v-else-if="anomalies.length === 0" class="empty anim-fade">
      <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--success)">OK</div>
      <div class="empty-text">Aucune anomalie détectée</div>
    </div>

    <div v-else class="anomalies-list anim-fade">
      <div v-for="(a, i) in anomalies" :key="i" class="anomalie-card" :class="'sev-' + a.severite">
        <div class="anomalie-header">
          <span class="anomalie-icon">
            <svg v-if="a.severite === 'error'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          </span>
          <div>
            <strong>{{ a.lot }}</strong>
            <span class="anomalie-type">{{ a.type }}</span>
          </div>
        </div>
        <div class="anomalie-message">{{ a.message }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAnomalies } from '../api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import PageHeader from '../components/PageHeader.vue'

const anomalies = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    anomalies.value = await getAnomalies()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.anomalies-list { display: flex; flex-direction: column; gap: 10px; }
.anomalie-card { padding: 14px 16px; border-radius: var(--radius-sm); border: 1px solid var(--border); }
.anomalie-card.sev-error { border-left: 4px solid var(--error); background: #FEF2F2; }
.anomalie-card.sev-warning { border-left: 4px solid #F59E0B; background: #FFFBEB; }
.anomalie-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.anomalie-icon { font-weight: 800; font-size: 16px; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }
.sev-error .anomalie-icon { color: var(--error); background: #FEE2E2; }
.sev-warning .anomalie-icon { color: #F59E0B; background: #FEF3C7; }
.anomalie-type { font-size: 11px; color: var(--text-muted); margin-left: 6px; }
.anomalie-message { font-size: 13px; color: var(--text-secondary); }
</style>
