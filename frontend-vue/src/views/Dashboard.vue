<template>
  <div class="page">
    <section class="dashboard-hero">
      <div>
        <span class="dashboard-eyebrow">VUE D'ENSEMBLE</span>
        <h1 class="dashboard-title">Atelier de production</h1>
        <p class="dashboard-subtitle">{{ todayDate }}</p>
      </div>
      <div class="dashboard-snapshot">
        <span class="snapshot-label">Stock chambre froide</span>
        <strong>{{ formatKg(stats.stock_froid_kg || 0) }} <small>kg</small></strong>
        <span class="snapshot-meta"><i></i>{{ stats.lots_en_stock || 0 }} lots prêts</span>
      </div>
      <div class="dashboard-actions">
        <button class="btn btn-outline btn-sm" @click="load">↻ Actualiser</button>
        <button class="btn btn-outline btn-sm" @click="doPrint">Imprimer</button>
      </div>
    </section>

    <LoadingSpinner v-if="loading" />
    <div v-else-if="error" class="error-state anim-fade">
      <p class="error-message">{{ error }}</p>
      <button class="btn btn-outline btn-sm" style="margin-top:12px" @click="load">Réessayer</button>
    </div>
    <template v-else>

      <!-- Pipeline workflow -->
      <div class="pipeline-caption">
        <span>Flux de production</span>
        <span>{{ lotsEnCours.length }} lots en cours</span>
      </div>
      <div class="pipeline-row">
        <div class="pipeline-stage">
          <div class="pipeline-icon" style="background:#FEF3C7;color:#D97706">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          </div>
          <div class="pipeline-info">
            <span class="pipeline-value">{{ lotsMusserie.length }}</span>
            <span class="pipeline-label">En Musserie</span>
          </div>
          <span class="pipeline-weight">{{ formatKg(totalMusserieJour) }} kg/jour</span>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-stage">
          <div class="pipeline-icon" style="background:#DBEAFE;color:#2563EB">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <div class="pipeline-info">
            <span class="pipeline-value">{{ lotsProduction.length }}</span>
            <span class="pipeline-label">En Production</span>
          </div>
          <span class="pipeline-weight">{{ formatKg(totalProductionJour) }} kg/jour</span>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-stage">
          <div class="pipeline-icon" style="background:#EDE9FE;color:#7C3AED">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
          </div>
          <div class="pipeline-info">
            <span class="pipeline-value">{{ lotsConditionnement.length }}</span>
            <span class="pipeline-label">Conditionnement</span>
          </div>
          <span class="pipeline-weight">{{ formatKg(totalConditionnementJour) }} kg/jour</span>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-stage">
          <div class="pipeline-icon" style="background:#D1FAE5;color:#059669">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <div class="pipeline-info">
            <span class="pipeline-value">{{ stats.lots_en_stock }}</span>
            <span class="pipeline-label">En Stock</span>
          </div>
          <span class="pipeline-weight">{{ formatKg(stats.stock_froid_kg || 0) }} kg total</span>
        </div>
      </div>

      <!-- KPIs -->
      <div class="kpi-row">
        <div class="kpi-card kpi-main">
          <div class="kpi-icon-dark">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value">{{ stats.total_produits }}</div>
            <div class="kpi-label">Produits</div>
          </div>
        </div>
        <div class="kpi-card kpi-main">
          <div class="kpi-icon-dark">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value">{{ stats.total_lots_actifs }}</div>
            <div class="kpi-label">Lots Actifs</div>
          </div>
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
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          </div>
          <div class="kpi-data">
            <div class="kpi-value">{{ formatNum(stats.rendement_moyen || 0) }}%</div>
            <div class="kpi-label">Rendement Moyen</div>
          </div>
        </div>
      </div>

      <!-- Charts row -->
      <div class="charts-row">
        <div class="card chart-card">
          <div class="card-header"><h3>Production Mensuelle (kg)</h3></div>
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
        <div class="card chart-card chart-card-donut">
          <div class="card-header"><h3>Répartition des Lots</h3></div>
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

      <!-- Lots en cours -->
      <div v-if="lotsEnCours.length" class="card" style="margin-top:20px">
        <div class="card-header"><h3>Lots en Cours de Traitement</h3></div>
        <div class="lots-list">
          <div v-for="lot in lotsEnCours" :key="lot.id" class="lot-row">
            <div class="lot-row-left">
              <strong>{{ lot.code_lot }}</strong>
              <span class="lot-row-fruit">{{ lot.type_fruit }}</span>
            </div>
            <div class="lot-row-progress">
              <div class="mini-progress">
                <div class="mini-progress-fill" :style="{ width: lotProgressPct(lot) + '%' }"></div>
              </div>
              <span class="lot-row-pct">{{ lotProgressPct(lot) }}%</span>
            </div>
            <StatusBadge :status="lot.statut" />
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
            <div class="alert-qte">{{ p.stock_actuel }} / {{ p.stock_min }} {{ p.unite_mesure }}</div>
            <StatusBadge :status="p.stock_actuel <= 0 ? 'rupture' : 'stock bas'" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDashboardStats, getDashboardProduction, getAlertesStockBas, getDashboardProductionMensuelle, getLots, getProductionsEtapes } from '../api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { toCanonical, EN_MUSSERIE, EN_PRODUCTION, CONDITIONNE, EN_STOCK } from '../utils/statuses'

const loading = ref(true)
const error = ref(null)
const stats = ref({})
const prod = ref({})
const stockBas = ref([])
const prodMensuelle = ref([])
const allLots = ref([])
const etapesData = ref({})

const todayDate = computed(() => {
  return new Date().toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

function formatNum(v) { return Number(v || 0).toLocaleString('fr-FR') }
function formatKg(v) { return Math.round(v || 0).toLocaleString('fr-FR') }

const lotsMusserie = computed(() => allLots.value.filter(l => [EN_MUSSERIE].includes(toCanonical(l.statut))))
const lotsProduction = computed(() => allLots.value.filter(l => [EN_PRODUCTION].includes(toCanonical(l.statut))))
const lotsConditionnement = computed(() => allLots.value.filter(l => [CONDITIONNE].includes(toCanonical(l.statut))))

const totalMusserieJour = computed(() => prod.value.musserie_jour_kg || 0)
const totalProductionJour = computed(() => prod.value.production_jour_kg || 0)
const totalConditionnementJour = computed(() => prod.value.conditionnement_jour_kg || 0)

const lotsEnCours = computed(() => {
  return allLots.value.filter(l => [EN_MUSSERIE, EN_PRODUCTION, CONDITIONNE].includes(toCanonical(l.statut)))
})

function round(v) { return Math.round((v || 0) * 100) / 100 }

function getEtapes(lotId) {
  return etapesData.value[lotId] || []
}

function getMusserieEtapes(lotId) {
  return getEtapes(lotId).filter(e => e.etape === 'musserie')
}

function getProductionEtapes(lotId) {
  return getEtapes(lotId).filter(e => e.etape === 'production')
}

function getConditionnementEtapes(lotId) {
  return getEtapes(lotId).filter(e => e.etape === 'conditionnement')
}

function totalCumulFruitsMusserie(lotId) {
  return round(getMusserieEtapes(lotId).reduce((s, e) => s + (e.fruits_murs_kg || 0), 0))
}

function totalCumulPoidsSortieProduction(lotId) {
  return round(getProductionEtapes(lotId).reduce((s, e) => s + (e.poids_sortie || 0), 0))
}

function totalCumulPoidsSortieConditionnement(lotId) {
  return round(getConditionnementEtapes(lotId).reduce((s, e) => s + (e.poids_sortie || 0), 0))
}

function lotProgressPct(lot) {
  const statut = toCanonical(lot.statut)
  const poidsTotal = lot.poids_frais || 0
  if (!poidsTotal) return 0

  if (statut === EN_MUSSERIE) {
    const traite = totalCumulFruitsMusserie(lot.id)
    return Math.min(100, Math.round((traite / poidsTotal) * 100))
  }
  if (statut === EN_PRODUCTION) {
    const traite = totalCumulPoidsSortieProduction(lot.id)
    const entreeProd = getEtapes(lot.id).find(e => e.etape === 'production')?.poids_entree || 0
    const base = entreeProd || poidsTotal
    return Math.min(100, Math.round((traite / base) * 100))
  }
  if (statut === CONDITIONNE) {
    const traite = totalCumulPoidsSortieConditionnement(lot.id)
    const entreeCond = getEtapes(lot.id).find(e => e.etape === 'conditionnement')?.poids_entree || 0
    const base = entreeCond || poidsTotal
    return Math.min(100, Math.round((traite / base) * 100))
  }
  if (statut === EN_STOCK) return 100
  return 0
}

const barData = computed(() => {
  if (!prodMensuelle.value.length) return []
  const values = prodMensuelle.value
  const max = Math.max(...values.map(v => v.value), 1)
  return values.map(v => ({ label: v.mois, value: Math.round(v.value), pct: Math.round((v.value / max) * 100) }))
})

const donutSegments = computed(() => {
  const total = stats.value.total_lots_actifs || 1
  const enMusserie = lotsMusserie.value.length
  const enProduction = lotsProduction.value.length
  const enConditionnement = lotsConditionnement.value.length
  const enStock = stats.value.lots_en_stock || 0
  const circumference = 2 * Math.PI * 48
  const segments = [
    { count: enStock, color: '#165B3D' },
    { count: enConditionnement, color: '#7C3AED' },
    { count: enProduction, color: '#2563EB' },
    { count: enMusserie, color: '#D97706' },
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

const donutLegend = computed(() => [
  { label: 'En stock', count: stats.value.lots_en_stock || 0, color: '#165B3D' },
  { label: 'Conditionnement', count: lotsConditionnement.value.length, color: '#7C3AED' },
  { label: 'Production', count: lotsProduction.value.length, color: '#2563EB' },
  { label: 'Musserie', count: lotsMusserie.value.length, color: '#D97706' },
])

async function load() {
  loading.value = true; error.value = null
  try {
    const [s, p, sb, pm, lots] = await Promise.all([
      getDashboardStats(), getDashboardProduction(), getAlertesStockBas(), getDashboardProductionMensuelle(), getLots(),
    ])
    stats.value = s
    prod.value = p
    stockBas.value = sb
    prodMensuelle.value = pm
    allLots.value = lots

    // Fetch etapes for each lot to calculate real progress
    for (const lot of lots) {
      if ([EN_MUSSERIE, EN_PRODUCTION, CONDITIONNE].includes(toCanonical(lot.statut))) {
        etapesData.value[lot.id] = await getProductionsEtapes(lot.id)
      }
    }
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  } finally { loading.value = false }
}

function doPrint() { window.print() }

onMounted(load)
</script>

<style scoped>
.dashboard-hero {
  display: grid; grid-template-columns: minmax(0, 1fr) auto auto; align-items: center; gap: 22px;
  margin-bottom: 26px; padding: 26px 28px; overflow: hidden; position: relative;
  border: 1px solid rgba(22, 91, 61, 0.15); border-radius: var(--radius-xl);
  background: linear-gradient(112deg, #0C3424 0%, #165B3D 58%, #247A53 100%);
  box-shadow: 0 18px 35px rgba(11, 46, 32, 0.16);
}
.dashboard-hero::after {
  content: ''; position: absolute; width: 260px; height: 260px; border-radius: 50%;
  right: -92px; top: -150px; background: rgba(198, 238, 140, 0.15); box-shadow: 0 0 0 38px rgba(198, 238, 140, 0.06);
}
.dashboard-hero > * { position: relative; z-index: 1; }
.dashboard-eyebrow { display: block; margin-bottom: 8px; color: var(--lime); font-size: 10px; font-weight: 800; letter-spacing: 0.14em; }
.dashboard-title { margin: 0; color: white; font-size: 34px; font-weight: 400; letter-spacing: -0.03em; }
.dashboard-subtitle { margin-top: 7px; color: #C9E0D0; font-size: 12px; text-transform: capitalize; }
.dashboard-snapshot {
  min-width: 168px; padding: 13px 16px; border: 1px solid rgba(255,255,255,0.16); border-radius: var(--radius-md);
  background: rgba(4, 35, 23, 0.22); color: white; backdrop-filter: blur(10px);
}
.snapshot-label { display: block; color: #BFDDC9; font-size: 10px; font-weight: 700; letter-spacing: 0.04em; }
.dashboard-snapshot strong { display: block; margin: 1px 0 5px; font-size: 24px; line-height: 1.2; letter-spacing: -0.04em; }
.dashboard-snapshot small { font-size: 12px; font-weight: 700; color: #C9E0D0; letter-spacing: 0; }
.snapshot-meta { display: flex; align-items: center; gap: 6px; color: #D8EADD; font-size: 10px; font-weight: 600; }
.snapshot-meta i { width: 6px; height: 6px; border-radius: 50%; background: var(--lime); box-shadow: 0 0 0 3px rgba(198,238,140,0.12); }
.dashboard-actions { display: flex; gap: 8px; }
.dashboard-actions .btn-outline { background: rgba(255,255,255,0.11); border-color: rgba(255,255,255,0.24); color: white; }
.dashboard-actions .btn-outline:hover { background: white; border-color: white; color: var(--primary); }

/* Pipeline */
.pipeline-caption { display: flex; justify-content: space-between; align-items: center; margin: 0 4px 9px; color: var(--text-muted); font-size: 11px; font-weight: 700; }
.pipeline-caption span:first-child { color: var(--dark); font-size: 13px; }
.pipeline-row {
  display: flex; align-items: center; gap: 0; margin-bottom: 20px;
  background: rgba(255,255,255,0.9); border: 1px solid rgba(221,230,222,0.9); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm); padding: 20px; overflow-x: auto;
}
.pipeline-stage {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px;
  min-width: 140px;
}
.pipeline-icon {
  width: 48px; height: 48px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center; box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
}
.pipeline-info { display: flex; flex-direction: column; align-items: center; }
.pipeline-value { font-size: 28px; font-weight: 700; color: var(--dark); line-height: 1; }
.pipeline-label { font-size: 11px; color: var(--text-muted); font-weight: 500; margin-top: 2px; }
.pipeline-weight { font-size: 11px; color: var(--text-secondary); font-weight: 600; }
.pipeline-arrow { font-size: 20px; color: var(--border); padding: 0 8px; flex-shrink: 0; }

/* KPIs */
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 14px; }
.kpi-card {
  background: white; border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: 20px; display: flex; align-items: center; gap: 14px;
  transition: all var(--transition); position: relative;
  animation: cardReveal 0.45s var(--ease) both;
}
.kpi-card:nth-child(2) { animation-delay: 0.04s; }
.kpi-card:nth-child(3) { animation-delay: 0.08s; }
.kpi-card:nth-child(4) { animation-delay: 0.12s; }
.kpi-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }

@keyframes cardReveal {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.kpi-main { padding: 22px; }
.kpi-main .kpi-data { flex: 1; min-width: 0; }

.kpi-icon-dark {
  width: 48px; height: 48px; border-radius: 14px; flex-shrink: 0;
  background: var(--secondary); color: white;
  display: flex; align-items: center; justify-content: center;
}

.kpi-data { min-width: 0; }
.kpi-value { font-size: 26px; font-weight: 700; color: var(--dark); line-height: 1.1; }
.kpi-label { font-size: 12px; color: var(--text-muted); font-weight: 500; margin-top: 3px; white-space: nowrap; }

/* Charts */
.charts-row { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; margin-bottom: 0; }
.chart-card { padding: 20px; }

.bar-chart { height: 220px; padding-top: 10px; }
.bar-chart-inner {
  display: flex; align-items: flex-end; justify-content: space-between;
  height: 100%; gap: 12px; padding: 0 8px;
}
.bar-col {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  height: 100%; justify-content: flex-end; position: relative;
}
.bar-tooltip { font-size: 10px; font-weight: 600; color: var(--text-muted); margin-bottom: 4px; white-space: nowrap; }
.bar-track {
  width: 100%; max-width: 48px; height: 160px;
  background: var(--surface); border-radius: 8px;
  display: flex; align-items: flex-end; overflow: hidden;
}
.bar-fill { width: 100%; border-radius: 8px; transition: height 0.7s var(--ease); display: flex; align-items: flex-end; }
.bar-fill-inner { width: 100%; height: 100%; border-radius: 8px; background: linear-gradient(180deg, var(--primary) 0%, var(--secondary) 100%); }
.bar-label { font-size: 11px; color: var(--text-muted); font-weight: 500; margin-top: 8px; }

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

/* Lots en cours */
.lots-list { display: flex; flex-direction: column; }
.lot-row {
  display: flex; align-items: center; gap: 16px; padding: 12px 0;
  border-bottom: 1px solid var(--border-light);
}
.lot-row:last-child { border-bottom: none; }
.lot-row-left { display: flex; flex-direction: column; gap: 2px; min-width: 140px; }
.lot-row-fruit { font-size: 12px; color: var(--text-muted); }
.lot-row-progress { flex: 1; display: flex; align-items: center; gap: 10px; }
.mini-progress { flex: 1; height: 6px; background: var(--border-light); border-radius: 3px; overflow: hidden; }
.mini-progress-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--success)); border-radius: 3px; transition: width 0.4s; }
.lot-row-pct { font-size: 11px; font-weight: 600; color: var(--text-secondary); min-width: 32px; text-align: right; }

/* Alerts */
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
  .dashboard-hero { grid-template-columns: 1fr auto; }
  .dashboard-actions { grid-column: 1 / -1; }
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
  .pipeline-row { padding: 14px; }
  .pipeline-stage { min-width: 100px; }
}
@media (max-width: 640px) {
  .dashboard-hero { grid-template-columns: 1fr; gap: 16px; padding: 22px; }
  .dashboard-title { font-size: 30px; }
  .dashboard-snapshot { width: 100%; }
  .dashboard-actions { width: 100%; }
  .dashboard-actions .btn { flex: 1; }
  .kpi-row { grid-template-columns: 1fr; }
  .pipeline-arrow { display: none; }
  .pipeline-row { flex-direction: column; gap: 12px; }
}
</style>
