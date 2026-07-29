<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">Vue d'ensemble de la production et du stock</p>
      </div>
      <button class="btn btn-outline btn-sm" @click="load">↻ Actualiser</button>
    </div>

    <LoadingSpinner v-if="loading" />
    <div v-else-if="error" class="error-state anim-fade">
      <p class="error-message">{{ error }}</p>
      <button class="btn btn-outline btn-sm" style="margin-top:12px" @click="load">Réessayer</button>
    </div>
    <template v-else>
      <!-- KPIs principaux -->
      <div class="kpi-grid">
        <div class="kpi-card" v-for="k in kpis" :key="k.label">
          <div class="kpi-icon" :style="{ background: k.bg }">
            <span v-html="k.icon"></span>
          </div>
          <div class="kpi-data">
            <div class="kpi-value">{{ k.value }}</div>
            <div class="kpi-label">{{ k.label }}</div>
          </div>
        </div>
      </div>

      <!-- Production -->
      <div class="section-header">
        <h2>Production</h2>
      </div>
      <div class="kpi-grid kpi-grid-4">
        <div class="kpi-card" v-for="k in prodKpis" :key="k.label">
          <div class="kpi-icon" :style="{ background: k.bg }">
            <span v-html="k.icon"></span>
          </div>
          <div class="kpi-data">
            <div class="kpi-value">{{ k.value }}</div>
            <div class="kpi-label">{{ k.label }}</div>
          </div>
        </div>
      </div>

      <!-- Alertes stock bas -->
      <div v-if="stockBas.length" class="card" style="margin-top:20px">
        <div class="card-header">
          <h3 style="display:flex;align-items:center;gap:8px">
            <span class="status-dot status-dot-warning"></span>
            Alertes Stock Bas
          </h3>
        </div>
        <div class="alert-list">
          <div v-for="p in stockBas.slice(0, 5)" :key="p.id" class="alert-row">
            <div class="alert-info">
              <span class="alert-nom">{{ p.nom }}</span>
              <span class="alert-cat">{{ p.categorie?.nom }}</span>
            </div>
            <div class="alert-qte">
              {{ p.stock_actuel }} / {{ p.stock_min }} {{ p.unite_mesure }}
            </div>
            <StatusBadge :status="p.stock_actuel <= 0 ? 'rupture' : 'stock bas'" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboardStats, getDashboardProduction, getAlertesStockBas } from '../api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'

const loading = ref(true)
const error = ref(null)
const kpis = ref([])
const prodKpis = ref([])
const stockBas = ref([])

const icons = {
  products: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>',
  alert: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
  box: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>',
  money: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
  chart: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
  snow: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/><line x1="19.07" y1="4.93" x2="4.93" y2="19.07"/></svg>',
  check: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
  clock: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
}

async function load() {
  loading.value = true; error.value = null
  try {
    const [s, p, sb] = await Promise.all([
      getDashboardStats(), getDashboardProduction(), getAlertesStockBas(),
    ])
    stockBas.value = sb

    kpis.value = [
      { label: 'Total Produits', value: s.total_produits, icon: icons.products, bg: '#F0FDFA' },
      { label: 'Stock Bas', value: s.produits_stock_bas, icon: icons.alert, bg: s.produits_stock_bas > 0 ? '#FEF2F2' : '#F0FDF4' },
      { label: 'Lots Actifs', value: s.total_lots_actifs, icon: icons.box, bg: '#F0FDFA' },
      { label: 'Valeur Stock', value: `${Number(s.valeur_stock).toLocaleString()} F`, icon: icons.money, bg: '#FFFBEB' },
      { label: 'Stock Froid', value: `${s.stock_froid_kg} kg`, icon: icons.snow, bg: '#EFF6FF' },
    ]
    prodKpis.value = [
      { label: 'Lots en Production', value: s.lots_en_production, icon: icons.chart, bg: '#F0FDFA' },
      { label: 'Étapes Terminées', value: p.etapes_terminees, icon: icons.check, bg: '#F0FDF4' },
      { label: 'Étapes en Cours', value: p.etapes_en_cours, icon: icons.clock, bg: '#FFFBEB' },
      { label: 'Production Jour', value: `${p.production_jour_kg} kg`, icon: icons.chart, bg: '#EFF6FF' },
    ]
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  } finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; }
.section-header { margin: 24px 0 16px; }
.section-header h2 { font-size: 16px; font-weight: 600; color: var(--dark); }
.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 8px; }
.kpi-grid-4 { grid-template-columns: repeat(4, 1fr); }
.kpi-card {
  background: white; border: 1px solid var(--border); border-radius: var(--radius-md);
  padding: 18px; display: flex; align-items: center; gap: 14px;
  transition: all var(--transition);
}
.kpi-card:hover { box-shadow: var(--shadow-sm); }
.kpi-icon {
  width: 44px; height: 44px; border-radius: 12px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; color: var(--primary);
}
.kpi-data { min-width: 0; }
.kpi-value { font-size: 22px; font-weight: 700; color: var(--dark); line-height: 1.1; }
.kpi-label { font-size: 11px; color: var(--text-muted); font-weight: 500; margin-top: 2px; white-space: nowrap; }
.alert-list { display: flex; flex-direction: column; }
.alert-row {
  display: flex; align-items: center; gap: 16px; padding: 10px 0;
  border-bottom: 1px solid var(--border-light); font-size: 13px;
}
.alert-row:last-child { border-bottom: none; }
.alert-info { flex: 1; display: flex; flex-direction: column; gap: 1px; }
.alert-nom { font-weight: 600; color: var(--dark); }
.alert-cat { font-size: 12px; color: var(--text-muted); }
.alert-qte { color: var(--text-secondary); font-size: 12px; }

@media (max-width: 1024px) {
  .kpi-grid { grid-template-columns: repeat(3, 1fr); }
  .kpi-grid-4 { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .kpi-grid, .kpi-grid-4 { grid-template-columns: repeat(2, 1fr); }
}
</style>
