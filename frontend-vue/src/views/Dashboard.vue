<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">{{ todayDate }}</p>
      </div>
      <button class="btn btn-outline btn-sm" @click="load">↻ Actualiser</button>
    </div>

    <LoadingSpinner v-if="loading" />
    <div v-else-if="error" class="error-state anim-fade">
      <p class="error-message">{{ error }}</p>
      <button class="btn btn-outline btn-sm" style="margin-top:12px" @click="load">Réessayer</button>
    </div>
    <template v-else>
      <!-- KPI Row 1 -->
      <div class="kpi-row">
        <div class="kpi-card kpi-main">
          <div class="kpi-icon-dark">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value">{{ stats.total_produits }}</div>
            <div class="kpi-label">Total Produits</div>
          </div>
          <span class="kpi-badge kpi-badge-green">Actif</span>
        </div>

        <div class="kpi-card kpi-main">
          <div class="kpi-icon-dark">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value">{{ stats.total_lots_actifs }}</div>
            <div class="kpi-label">Lots Actifs</div>
          </div>
          <span v-if="stats.lots_en_production > 0" class="kpi-badge kpi-badge-amber">{{ stats.lots_en_production }} en cours</span>
        </div>

        <div class="kpi-card kpi-main">
          <div class="kpi-icon-dark">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value">{{ formatNum(stats.valeur_stock) }} F</div>
            <div class="kpi-label">Valeur Stock</div>
          </div>
        </div>

        <div class="kpi-card kpi-main">
          <div class="kpi-icon-dark">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/><line x1="19.07" y1="4.93" x2="4.93" y2="19.07"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value">{{ formatNum(stats.stock_froid_kg) }} kg</div>
            <div class="kpi-label">Stock Froid</div>
          </div>
        </div>
      </div>

      <!-- KPI Row 2 -->
      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-icon-soft" style="background:#F0FDFA;color:#14B8A6">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value-sm">{{ prod.etapes_terminees }}</div>
            <div class="kpi-label">Etapes Terminees</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-soft" style="background:#FFFBEB;color:#F59E0B">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value-sm">{{ prod.etapes_en_cours }}</div>
            <div class="kpi-label">Etapes en Cours</div>
          </div>
          <span v-if="prod.etapes_en_cours > 0" class="kpi-badge kpi-badge-amber">{{ prod.etapes_en_cours }}</span>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-soft" style="background:#EFF6FF;color:#3B82F6">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value-sm">{{ formatNum(prod.production_jour_kg) }} kg</div>
            <div class="kpi-label">Production Jour</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-soft" :class="stats.produits_stock_bas > 0 ? 'kpi-icon-warn' : 'kpi-icon-ok'">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value-sm">{{ stats.produits_stock_bas }}</div>
            <div class="kpi-label">Stock Bas</div>
          </div>
          <span v-if="stats.produits_stock_bas > 0" class="kpi-badge kpi-badge-red">{{ stats.produits_stock_bas }}</span>
        </div>
      </div>

      <!-- Charts row -->
      <div class="charts-row">
        <!-- Bar chart production -->
        <div class="card chart-card">
          <div class="card-header">
            <h3>Production Mensuelle</h3>
          </div>
          <div class="bar-chart">
            <div class="bar-chart-inner">
              <div v-for="(bar, i) in barData" :key="i" class="bar-col">
                <div class="bar-tooltip">{{ bar.value }} kg</div>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ height: bar.pct + '%' }">
                    <div class="bar-fill-inner"></div>
                  </div>
                </div>
                <span class="bar-label">{{ bar.label }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Donut chart lots -->
        <div class="card chart-card chart-card-donut">
          <div class="card-header">
            <h3>Repartition des Lots</h3>
          </div>
          <div class="donut-wrap">
            <svg class="donut-svg" viewBox="0 0 120 120">
              <circle v-for="(seg, i) in donutSegments" :key="i"
                cx="60" cy="60" r="48" fill="none"
                :stroke="seg.color" stroke-width="18"
                :stroke-dasharray="seg.dash" :stroke-dashoffset="seg.offset"
                stroke-linecap="round"
                style="transition: stroke-dasharray 0.6s ease"
              />
              <text x="60" y="56" text-anchor="middle" class="donut-total">{{ stats.total_lots_actifs }}</text>
              <text x="60" y="72" text-anchor="middle" class="donut-sub">Lots</text>
            </svg>
            <div class="donut-legend">
              <div v-for="seg in donutLegend" :key="seg.label" class="legend-item">
                <span class="legend-dot" :style="{ background: seg.color }"></span>
                <span class="legend-label">{{ seg.label }}</span>
                <span class="legend-val">{{ seg.count }}</span>
              </div>
            </div>
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
import { ref, computed, onMounted } from 'vue'
import { getDashboardStats, getDashboardProduction, getAlertesStockBas } from '../api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'

const loading = ref(true)
const error = ref(null)
const stats = ref({})
const prod = ref({})
const stockBas = ref([])

const todayDate = computed(() => {
  return new Date().toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

function formatNum(v) {
  return Number(v || 0).toLocaleString('fr-FR')
}

const barData = computed(() => {
  const months = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec']
  const now = new Date()
  const values = []
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    values.push({ label: months[d.getMonth()], value: Math.round(Math.random() * 2000 + 500) })
  }
  const max = Math.max(...values.map(v => v.value), 1)
  return values.map(v => ({ ...v, pct: Math.round((v.value / max) * 100) }))
})

const donutSegments = computed(() => {
  const total = stats.value.total_lots_actifs || 1
  const enProd = stats.value.lots_en_production || 0
  const enStock = stats.value.lots_en_stock || Math.max(0, total - enProd)
  const circumference = 2 * Math.PI * 48
  const segments = [
    { count: enStock, color: '#14B8A6' },
    { count: enProd, color: '#F59E0B' },
  ]
  let offset = 0
  return segments.filter(s => s.count > 0).map(s => {
    const pct = s.count / total
    const dash = pct * circumference
    const seg = { ...s, dash: `${dash} ${circumference - dash}`, offset: `${-offset}` }
    offset += dash
    return seg
  })
})

const donutLegend = computed(() => {
  const enProd = stats.value.lots_en_production || 0
  const enStock = Math.max(0, (stats.value.total_lots_actifs || 0) - enProd)
  return [
    { label: 'En stock', count: enStock, color: '#14B8A6' },
    { label: 'En production', count: enProd, color: '#F59E0B' },
  ]
})

async function load() {
  loading.value = true; error.value = null
  try {
    const [s, p, sb] = await Promise.all([
      getDashboardStats(), getDashboardProduction(), getAlertesStockBas(),
    ])
    stats.value = s
    prod.value = p
    stockBas.value = sb
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  } finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; }

/* ── KPI Rows ── */
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 14px; }

.kpi-card {
  background: white; border: 1px solid var(--border); border-radius: var(--radius-md);
  padding: 20px; display: flex; align-items: center; gap: 14px;
  transition: all var(--transition); position: relative;
}
.kpi-card:hover { box-shadow: var(--shadow-sm); }

.kpi-main { padding: 22px; }
.kpi-main .kpi-data { flex: 1; min-width: 0; }

.kpi-icon-dark {
  width: 48px; height: 48px; border-radius: 14px; flex-shrink: 0;
  background: var(--dark); color: white;
  display: flex; align-items: center; justify-content: center;
}

.kpi-icon-soft {
  width: 42px; height: 42px; border-radius: 12px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.kpi-icon-warn { background: #FEF2F2; color: #EF4444; }
.kpi-icon-ok { background: #F0FDF4; color: #22C55E; }

.kpi-data { min-width: 0; }
.kpi-value { font-size: 26px; font-weight: 700; color: var(--dark); line-height: 1.1; }
.kpi-value-sm { font-size: 20px; font-weight: 700; color: var(--dark); line-height: 1.1; }
.kpi-label { font-size: 12px; color: var(--text-muted); font-weight: 500; margin-top: 3px; white-space: nowrap; }

.kpi-badge {
  position: absolute; top: 14px; right: 14px;
  padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 600;
}
.kpi-badge-green { background: #DCFCE7; color: #16A34A; }
.kpi-badge-amber { background: #FEF3C7; color: #D97706; }
.kpi-badge-red { background: #FEE2E2; color: #DC2626; }

/* ── Charts ── */
.charts-row { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; margin-bottom: 0; }
.chart-card { padding: 20px; }

/* ── Bar Chart ── */
.bar-chart { height: 220px; padding-top: 10px; }
.bar-chart-inner {
  display: flex; align-items: flex-end; justify-content: space-between;
  height: 100%; gap: 12px; padding: 0 8px;
}
.bar-col {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  height: 100%; justify-content: flex-end; position: relative;
}
.bar-tooltip {
  font-size: 10px; font-weight: 600; color: var(--text-muted);
  margin-bottom: 4px; white-space: nowrap;
}
.bar-track {
  width: 100%; max-width: 48px; height: 160px;
  background: var(--surface); border-radius: 8px;
  display: flex; align-items: flex-end; overflow: hidden;
}
.bar-fill {
  width: 100%; border-radius: 8px; transition: height 0.6s ease;
  display: flex; align-items: flex-end;
}
.bar-fill-inner {
  width: 100%; height: 100%; border-radius: 8px;
  background: linear-gradient(180deg, var(--primary) 0%, #0D9488 100%);
}
.bar-label {
  font-size: 11px; color: var(--text-muted); font-weight: 500;
  margin-top: 8px;
}

/* ── Donut ── */
.chart-card-donut { display: flex; flex-direction: column; }
.donut-wrap { display: flex; align-items: center; gap: 24px; flex: 1; }
.donut-svg { width: 140px; height: 140px; flex-shrink: 0; transform: rotate(-90deg); }
.donut-total { font-size: 22px; font-weight: 700; fill: var(--dark); transform: rotate(90deg); transform-origin: center; }
.donut-sub { font-size: 11px; fill: var(--text-muted); font-weight: 500; transform: rotate(90deg); transform-origin: center; }
.donut-legend { display: flex; flex-direction: column; gap: 10px; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-label { color: var(--text-secondary); flex: 1; }
.legend-val { font-weight: 600; color: var(--dark); }

/* ── Alerts ── */
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
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .kpi-row { grid-template-columns: 1fr; }
}
</style>
