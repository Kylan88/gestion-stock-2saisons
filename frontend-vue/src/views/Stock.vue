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
      <div class="zones-grid">
        <div v-for="zone in zones" :key="zone.id" class="card anim-fade">
          <div class="card-header">
            <div style="display:flex;align-items:center;gap:10px">
              <div class="zone-icon-wrap" :class="zone.type_zone === 'froid' ? 'zone-froid' : 'zone-ambiant'">
                <svg v-if="zone.type_zone === 'froid'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20M6 6l12 12M18 6l-12 12"/></svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              </div>
              <div>
                <h3>{{ zone.nom }}</h3>
                <span style="font-size:11px;color:var(--text-muted)">{{ zone.capacite_kg }} kg max</span>
              </div>
            </div>
            <StatusBadge :status="zone.actif ? 'disponible' : 'périmé'" />
          </div>
          <div class="zone-capacity">
            <div class="zone-capacity-head"><span>Occupation</span><strong>{{ formatKg(zoneTotal(zone)) }} / {{ formatKg(zone.capacite_kg) }} kg</strong></div>
            <div class="zone-capacity-track"><span :style="{ width: zoneCapacityPercent(zone) + '%' }"></span></div>
          </div>
          <div v-if="(stocksByZone[zone.id] || []).length" class="zone-stocks">
            <div v-for="s in stocksByZone[zone.id]" :key="s.id" class="stock-row">
              <div class="stock-info">
                <span class="stock-produit">{{ s.produit?.nom }}</span>
                <span v-if="s.lot" class="stock-lot">{{ s.lot.code_lot }}</span>
              </div>
              <div class="stock-qte">
                <strong>{{ s.quantite }} kg</strong>
                <span v-if="s.sachets" style="font-size:11px;color:var(--text-muted)">{{ s.sachets }} sachets</span>
              </div>
            </div>
          </div>
          <div v-else class="stock-empty">Aucun stock</div>
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
function zoneCapacityPercent(zone) {
  if (!zone.capacite_kg) return 0
  return Math.min(100, Math.round((zoneTotal(zone) / zone.capacite_kg) * 100))
}
function formatKg(value) { return Number(value || 0).toLocaleString('fr-FR', { maximumFractionDigits: 1 }) }

onMounted(load)
</script>

<style scoped>
.flow-metric { display: flex; flex-direction: column; }
.flow-metric strong { font-family: 'DM Serif Display', Georgia, serif; font-size: 25px; line-height: 0.9; color: var(--lime); }
.flow-metric span { margin-top: 4px; color: #C6D8CC; font-size: 9px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
.zones-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 18px; }
.zones-grid > .card { position: relative; overflow: hidden; }
.zones-grid > .card::after { content: ''; position: absolute; width: 120px; height: 120px; border-radius: 50%; right: -55px; top: -60px; background: var(--primary-50); z-index: 0; }
.zones-grid > .card > * { position: relative; z-index: 1; }
.zone-icon-wrap {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 18px;
}
.zone-froid { background: #EFF6FF; }
.zone-ambiant { background: var(--primary-50); }
.zone-capacity { padding: 11px 0 3px; }
.zone-capacity-head { display: flex; justify-content: space-between; gap: 10px; color: var(--text-muted); font-size: 10px; font-weight: 700; }
.zone-capacity-head strong { color: var(--dark); font-size: 10px; }
.zone-capacity-track { height: 6px; margin-top: 7px; overflow: hidden; border-radius: 99px; background: var(--border-light); }
.zone-capacity-track span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--primary), var(--lime)); transition: width 0.45s var(--ease); }
.zone-stocks { border-top: 1px solid var(--border-light); margin-top: 12px; padding-top: 12px; display: flex; flex-direction: column; gap: 8px; }
.stock-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; }
.stock-info { display: flex; align-items: center; gap: 8px; }
.stock-produit { font-weight: 500; }
.stock-lot { font-size: 11px; color: var(--text-muted); background: var(--surface); padding: 2px 8px; border-radius: 4px; }
.stock-qte { text-align: right; display: flex; flex-direction: column; gap: 1px; }
.stock-empty { color: var(--text-muted); font-size: 13px; text-align: center; padding: 16px 0; border-top: 1px solid var(--border-light); margin-top: 12px; }
@media (max-width: 768px) { .zones-grid { grid-template-columns: 1fr !important; } }
</style>
