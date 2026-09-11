<template>
  <div class="page">
    <PageHeader title="Stock & Zones" subtitle="Gestion des stocks par zone de stockage">
      <template #actions>
        <button class="btn btn-outline btn-sm" @click="doPrint">Imprimer</button>
      </template>
    </PageHeader>

    <WorkflowFrame
      :step="5"
      eyebrow="Disponibilité & conservation"
      title="Visualiser le stock prêt"
      description="Consultez le contenu de chaque zone et repérez rapidement les volumes disponibles pour la suite des opérations."
    >
      <template #meta><div class="flow-metric"><strong>{{ zones.length }}</strong><span>zones actives</span></div></template>
    </WorkflowFrame>

    <LoadingSpinner v-if="loading" />
    <template v-else>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px;margin-bottom:24px">
        <StatCard title="Stock total" :value="formatKg(zones.reduce((s,z)=>s+zoneTotal(z),0)) + ' kg'" status="success">
          <template #icon><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg></template>
        </StatCard>
        <StatCard v-for="zone in zones" :key="'kpi-'+zone.id" :title="zone.nom" :value="formatKg(zoneTotal(zone)) + ' kg'" :status="zone.type_zone==='froid'?'info':'neutral'">
          <template #icon>
            <svg v-if="zone.type_zone==='froid'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20M6 6l12 12M18 6l-12 12"/></svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>
          </template>
        </StatCard>
        <StatCard title="Lots stockés" :value="Object.values(stocksByZone).flat().length" status="neutral">
          <template #icon><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></template>
        </StatCard>
      </div>
      <div class="zones-grid">
        <div v-for="zone in zones" :key="zone.id" class="card anim-fade zone-card">
          <div class="card-header">
            <div style="display:flex;align-items:center;gap:10px">
              <div class="zone-icon-wrap" :class="zone.type_zone === 'froid' ? 'zone-froid' : 'zone-ambiant'">
                <svg v-if="zone.type_zone === 'froid'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20M6 6l12 12M18 6l-12 12"/></svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              </div>
              <div>
                <h3>{{ zone.nom }}</h3>
                <span style="font-size:11px;color:var(--text-muted)">{{ (stocksByZone[zone.id] || []).length }} lot(s) · {{ formatKg(zoneTotal(zone)) }} kg</span>
              </div>
            </div>
            <StatusBadge :status="zone.actif ? 'disponible' : 'périmé'" />
          </div>
          <div v-if="(stocksByZone[zone.id] || []).length" class="zone-stocks">
            <div v-for="s in stocksByZone[zone.id]" :key="s.id" class="stock-row">
              <div class="stock-info">
                <div class="stock-icon" :class="s.produit?.nom?.toLowerCase().includes('export') ? 'icon-export' : s.produit?.nom?.toLowerCase().includes('local') ? 'icon-local' : 'icon-default'">{{ (s.produit?.nom||'?').charAt(0) }}</div>
                <div>
                  <div class="stock-produit">{{ s.produit?.nom }}</div>
                  <div style="display:flex;gap:6px;align-items:center">
                    <span v-if="s.lot" class="stock-lot">{{ s.lot.code_lot }}</span>
                    <span style="font-size:10px;color:var(--text-muted)">{{ s.date_entree?.slice(0,10) }}</span>
                  </div>
                </div>
              </div>
              <div class="stock-qte">
                <strong>{{ s.quantite }} kg</strong>
                <span v-if="s.sachets" style="font-size:11px;color:var(--text-muted)">{{ s.sachets }} sachets</span>
              </div>
            </div>
          </div>
          <div v-else class="stock-empty">
            <div class="stock-empty-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            </div>
            <div class="stock-empty-title">Aucun stock dans {{ zone.nom }}</div>
            <div class="stock-empty-sub">Les lots transférés depuis le conditionnement apparaîtront ici</div>
            <router-link to="/conditionnement" class="btn btn-ghost btn-sm" style="margin-top:8px">Aller au conditionnement →</router-link>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getZonesStock, getContenuZone } from '../api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import WorkflowFrame from '../components/WorkflowFrame.vue'
import StatCard from '../components/StatCard.vue'

const zones = ref([])
const stocksByZone = reactive({})
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    const z = await getZonesStock()
    zones.value = z
    const contents = await Promise.all(z.map(zone => getContenuZone(zone.id)))
    z.forEach((zone, i) => { stocksByZone[zone.id] = contents[i] })
  } finally { loading.value = false }
}

function doPrint() { window.print() }

function zoneTotal(zone) {
  return (stocksByZone[zone.id] || []).reduce((total, stock) => total + Number(stock.quantite || 0), 0)
}
function formatKg(value) { return Number(value || 0).toLocaleString('fr-FR', { maximumFractionDigits: 1 }) }

onMounted(load)
</script>

<style scoped>
.flow-metric { display: flex; flex-direction: column; }
.flow-metric strong { font-family: 'DM Serif Display', Georgia, serif; font-size: 25px; line-height: 0.9; color: var(--lime); }
.flow-metric span { margin-top: 4px; color: #C6D8CC; font-size: 9px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
.zones-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; }
.zones-grid > .card.zone-card { position: relative; overflow: hidden; border-top:3px solid var(--primary); animation: fadeIn 0.4s ease both; }
.zones-grid > .card.zone-card:nth-child(1) { animation-delay: 0.05s; } .zones-grid > .card.zone-card:nth-child(2) { animation-delay: 0.12s; }
.zones-grid > .card.zone-card::after { content: ''; position: absolute; width: 120px; height: 120px; border-radius: 50%; right: -55px; top: -60px; background: var(--primary-50); z-index: 0; }
.zones-grid > .card.zone-card > * { position: relative; z-index: 1; }
.zone-icon-wrap { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink:0}
.zone-froid { background: #EFF6FF; color:var(--info)}
.zone-ambiant { background: var(--primary-50); }
.zone-stocks { border-top: 1px solid var(--border-light); margin-top: 14px; padding-top: 12px; display: flex; flex-direction: column; gap: 8px; }
.stock-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; font-size: 13px; background:var(--surface); border:1px solid var(--border-light); border-radius:var(--radius-sm)}
.stock-row:hover{ border-color:var(--border); background:white}
.stock-info { display: flex; align-items: center; gap: 10px; }
.stock-icon{ width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:800; flex-shrink:0}
.icon-export{ background:#DBEAFE; color:var(--info)} .icon-local{ background:#DCFCE7; color:#00853E} .icon-default{ background:var(--primary-50); color:var(--primary)}
.stock-produit { font-weight: 600; font-size:13px}
.stock-lot { font-size: 11px; color: var(--text-muted); background: white; padding: 2px 8px; border-radius: 4px; border:1px solid var(--border-light)}
.stock-qte { text-align: right; display: flex; flex-direction: column; gap: 1px; }
.stock-empty { color: var(--text-muted); font-size: 13px; text-align: center; padding: 32px 0; border-top: 1px solid var(--border-light); margin-top: 12px; display:flex; flex-direction:column; gap:6px; align-items:center; animation: fadeIn 0.5s ease both; }
.stock-empty:nth-child(1) { animation-delay: 0.05s; } .stock-empty:nth-child(2) { animation-delay: 0.1s; }
.stock-empty-icon { width:48px; height:48px; border-radius:50%; background: var(--surface); border:1px solid var(--border-light); display:flex; align-items:center; justify-content:center; color: var(--text-muted); animation: float 3s ease-in-out infinite; }
.stock-empty-title { font-weight:600; color: var(--text-secondary); font-size:13px}
.stock-empty-sub { font-size:11px; color: var(--text-muted); max-width:260px}
@keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
@keyframes fadeIn { from { opacity:0; transform: translateY(8px); } to { opacity:1; transform: translateY(0); } }
.stock-summary{ border-left:3px solid var(--primary)}
@media (max-width: 768px) { .zones-grid { grid-template-columns: 1fr !important; } }
</style>
