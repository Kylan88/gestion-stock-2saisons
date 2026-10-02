<template>
  <div class="page">
    <PageHeader title="Historique global" subtitle="Consultation de toutes les étapes de production">
      <template #actions>
        <button class="btn btn-outline btn-sm" @click="loadData">↻ Actualiser</button>
        <button v-if="data.length > 0" class="btn btn-outline btn-sm" @click="exportXLSX">↓ Export Excel</button>
      </template>
    </PageHeader>

    <WorkflowFrame
      :step="5"
      eyebrow="Suivi complet"
      title="Historique de production"
      description="Retrouvez toutes les saisies murisserie, production, conditionnement et transferts du site."
    >
      <template #meta>
        <div class="flow-metric">
          <strong>{{ totalEntries }}</strong>
          <span>session(s)</span>
        </div>
      </template>
    </WorkflowFrame>

    <div class="hist-filters compact-search">
      <div class="tabs">
        <button v-for="t in tabs" :key="t.key" class="tab" :class="{ active: activeTab === t.key }" @click="switchTab(t.key)">
          {{ t.label }}
          <span class="tab-count">{{ counts[t.key] || 0 }}</span>
        </button>
      </div>
      <input v-model="recherche" class="input hist-search" placeholder="Rechercher un lot..." />
    </div>

    <LoadingSpinner v-if="loading" />

    <!-- MURISSERIE -->
    <div v-else-if="activeTab === 'murisserie'" class="anim-fade">
      <div v-if="filteredData.length === 0" class="empty"><div class="empty-text">Aucun enregistrement murisserie</div></div>
      <div v-else class="table-wrap">
        <table>
          <thead><tr><th>Date</th><th>Lot</th><th>Dryer</th><th>Fruits mûrs</th><th>Tri</th><th>Lavage</th><th>Dép.</th><th>Sortie</th><th>Rdt</th><th>Opérateur</th></tr></thead>
          <tbody>
            <tr v-for="e in filteredData" :key="e.id">
              <td>{{ fmtDate(e.date_debut) }}</td>
              <td><strong>{{ e.lot?.code_lot || e.lot_id }}</strong></td>
              <td>{{ e.dryer ? 'D'+e.dryer : '—' }}</td>
              <td>{{ e.fruits_murs_kg }} kg</td>
              <td>{{ e.dechets_tri_kg }} kg</td>
              <td>{{ e.dechets_lavage_kg }} kg</td>
              <td>{{ e.dechets_production_kg }} kg</td>
              <td>{{ e.poids_sortie }} kg</td>
              <td>{{ e.rendement_pourcentage ? e.rendement_pourcentage+'%' : '—' }}</td>
              <td>{{ e.operateur || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- PRODUCTION -->
    <div v-else-if="activeTab === 'production'" class="anim-fade">
      <div v-if="filteredData.length === 0" class="empty"><div class="empty-text">Aucun enregistrement production</div></div>
      <div v-else class="table-wrap">
        <table>
          <thead><tr><th>Date</th><th>Lot</th><th>Dryer</th><th>Chariots</th><th>Claies</th><th>Entrée</th><th>Sortie</th><th>Rdt</th><th>Opérateur</th></tr></thead>
          <tbody>
            <tr v-for="e in filteredData" :key="e.id">
              <td>{{ fmtDate(e.date_debut) }}</td>
              <td><strong>{{ e.lot?.code_lot || e.lot_id }}</strong></td>
              <td>{{ e.dryer ? 'D'+e.dryer : '—' }}</td>
              <td>{{ e.nbre_chariots || '—' }}</td>
              <td>{{ e.total_claies || '—' }}</td>
              <td>{{ e.poids_entree }} kg</td>
              <td>{{ e.poids_sortie || '—' }} kg</td>
              <td>{{ e.rendement_pourcentage ? e.rendement_pourcentage+'%' : '—' }}</td>
              <td>{{ e.operateur || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- CONDITIONNEMENT -->
    <div v-else-if="activeTab === 'conditionnement'" class="anim-fade">
      <div v-if="filteredData.length === 0" class="empty"><div class="empty-text">Aucun enregistrement conditionnement</div></div>
      <div v-else class="table-wrap">
        <table>
          <thead><tr><th>Date</th><th>Lot</th><th>Statut</th><th>Entrée</th><th>Sortie</th><th>Rdt</th><th>Opérateur</th></tr></thead>
          <tbody>
            <tr v-for="e in filteredData" :key="e.id">
              <td>{{ fmtDate(e.date_debut) }}</td>
              <td><strong>{{ e.lot?.code_lot || e.lot_id }}</strong></td>
              <td><StatusBadge :status="e.statut" /></td>
              <td>{{ e.poids_entree }} kg</td>
              <td>{{ e.poids_sortie || '—' }} kg</td>
              <td>{{ e.rendement_pourcentage ? e.rendement_pourcentage+'%' : '—' }}</td>
              <td>{{ e.operateur || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- RECONDITIONNEMENT -->
    <div v-else-if="activeTab === 'reconditionnement'" class="anim-fade">
      <div v-if="filteredData.length === 0" class="empty"><div class="empty-text">Aucun reconditionnement enregistré</div></div>
      <div v-else class="table-wrap">
        <table>
          <thead><tr><th>Date</th><th>Lot</th><th>Source</th><th>Cartons</th><th>Sachets est.</th><th>Sortis</th><th>Déchet kg</th><th>Rhum obtenu</th><th>Responsable</th></tr></thead>
          <tbody>
            <tr v-for="e in filteredData" :key="e.id">
              <td>{{ fmtDate(e.date_reconditionnement) }}</td>
              <td><strong>{{ lotCode(e.lot_id) }}</strong></td>
              <td>{{ e.type_source }}</td>
              <td>{{ e.nb_cartons_entree }}</td>
              <td>{{ e.nb_sachets_100g_sortie }}</td>
              <td>{{ e.nb_sachets_sortis }}</td>
              <td>{{ e.dechet_kg ?? 0 }}</td>
              <td>{{ rhumTxt(e) }}</td>
              <td>{{ e.responsable || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TRANSFERT CF -->
    <div v-else-if="activeTab === 'transfert'" class="anim-fade">
      <div v-if="filteredData.length === 0" class="empty"><div class="empty-text">Aucune demande de transfert</div></div>
      <div v-else class="table-wrap">
        <table>
          <thead><tr><th>Date</th><th>Lot</th><th>Statut</th><th>Responsable</th><th>Détail</th></tr></thead>
          <tbody>
            <tr v-for="e in filteredData" :key="e.id">
              <td>{{ fmtDate(e.date_demande || e.date_creation) }}</td>
              <td><strong>{{ e.lot?.code_lot || e.lot_id }}</strong></td>
              <td><StatusBadge :status="e.statut" /></td>
              <td>{{ e.responsable || '—' }}</td>
              <td>
                <div class="lignes-list">
                  <span v-for="(l, i) in (e.lignes || [])" :key="i" class="line-chip">
                    {{ l.nb_cartons }} {{ l.type_flux }} → {{ l.zone?.nom || '—' }}
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { getHistoriqueMurisserie, getHistoriqueProduction, getHistoriqueConditionnement, getDemandesTransfert, getReconditionnements, getLots } from '../api'
import { exportExcel, todayStamp } from '../utils/exportExcel'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import WorkflowFrame from '../components/WorkflowFrame.vue'

const tabs = [
  { key: 'murisserie', label: 'Murisserie' },
  { key: 'production', label: 'Production' },
  { key: 'conditionnement', label: 'Conditionnement' },
  { key: 'reconditionnement', label: 'Reconditionnement' },
  { key: 'transfert', label: 'Transfert CF' },
]

const activeTab = ref('murisserie')
const data = ref([])
const loading = ref(false)
const recherche = ref('')
const counts = ref({})
const lotsMap = ref({})

const totalEntries = computed(() => {
  return Object.values(counts.value).reduce((s, c) => s + c, 0)
})

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const filteredData = computed(() => {
  if (!recherche.value) return data.value
  const q = recherche.value.toLowerCase()
  return data.value.filter(e => {
    const code = (e.lot?.code_lot || lotCode(e.lot_id) || '').toLowerCase()
    const fruit = (e.lot?.type_fruit || '').toLowerCase()
    return code.includes(q) || fruit.includes(q)
  })
})

function lotCode(lotId) {
  if (lotId == null) return ''
  return lotsMap.value[lotId] || ('Lot #' + lotId)
}

function rhumTxt(e) {
  const parts = []
  if (e.rhum_cartons_sortie) parts.push(`${e.rhum_cartons_sortie} cart.`)
  if (e.rhum_sachets_sortis) parts.push(`${e.rhum_sachets_sortis} sach.`)
  if (e.rhum_poids_vrac_kg) parts.push(`${e.rhum_poids_vrac_kg} kg vrac`)
  return parts.length ? parts.join(' / ') : '—'
}

async function loadData() {
  loading.value = true
  data.value = []
  try {
    const [mus, prod, cond, reco, transf, lots] = await Promise.all([
      getHistoriqueMurisserie(),
      getHistoriqueProduction(),
      getHistoriqueConditionnement(),
      getReconditionnements(),
      getDemandesTransfert(),
      getLots().catch(() => []),
    ])
    lotsMap.value = Object.fromEntries((lots || []).map(l => [l.id, l.code_lot]))
    counts.value = { murisserie: mus.length, production: prod.length, conditionnement: cond.length, reconditionnement: reco.length, transfert: transf.length }
    if (activeTab.value === 'murisserie') data.value = mus
    else if (activeTab.value === 'production') data.value = prod
    else if (activeTab.value === 'conditionnement') data.value = cond
    else if (activeTab.value === 'reconditionnement') data.value = reco
    else if (activeTab.value === 'transfert') data.value = transf
  } finally { loading.value = false }
}

function switchTab(key) {
  activeTab.value = key
}

function exportXLSX() {
  const rows = filteredData.value
  if (!rows.length) return
  const d = (v) => v ? new Date(v).toLocaleDateString('fr-FR') : ''
  const lotOf = (e) => e.lot?.code_lot || e.lot_id
  const dryerOf = (e) => e.dryer ? 'D' + e.dryer : ''
  const rdtOf = (e) => e.rendement_pourcentage != null ? e.rendement_pourcentage + '%' : ''
  let headers = [], data = []
  if (activeTab.value === 'murisserie') {
    headers = ['Date', 'Lot', 'Dryer', 'Fruits mûrs (kg)', 'Tri (kg)', 'Lavage (kg)', 'Déchets prod. (kg)', 'Sortie (kg)', 'Rendement', 'Opérateur']
    data = rows.map(e => [d(e.date_debut), lotOf(e), dryerOf(e), e.fruits_murs_kg ?? '', e.dechets_tri_kg ?? '', e.dechets_lavage_kg ?? '', e.dechets_production_kg ?? '', e.poids_sortie ?? '', rdtOf(e), e.operateur || ''])
  } else if (activeTab.value === 'production') {
    headers = ['Date', 'Lot', 'Dryer', 'Chariots', 'Claies', 'Entrée (kg)', 'Sortie (kg)', 'Rendement', 'Opérateur']
    data = rows.map(e => [d(e.date_debut), lotOf(e), dryerOf(e), e.nbre_chariots ?? '', e.total_claies ?? '', e.poids_entree ?? '', e.poids_sortie ?? '', rdtOf(e), e.operateur || ''])
  } else if (activeTab.value === 'conditionnement') {
    headers = ['Date', 'Lot', 'Statut', 'Entrée (kg)', 'Sortie (kg)', 'Rendement', 'Opérateur']
    data = rows.map(e => [d(e.date_debut), lotOf(e), e.statut || '', e.poids_entree ?? '', e.poids_sortie ?? '', rdtOf(e), e.operateur || ''])
  } else if (activeTab.value === 'reconditionnement') {
    headers = ['Date', 'Lot', 'Source', 'Cartons', 'Sachets est.', 'Sortis', 'Déchet (kg)', 'Rhum obtenu', 'Responsable']
    data = rows.map(e => [d(e.date_reconditionnement), lotCode(e.lot_id), e.type_source || '', e.nb_cartons_entree ?? '', e.nb_sachets_100g_sortie ?? '', e.nb_sachets_sortis ?? '', e.dechet_kg ?? 0, rhumTxt(e), e.responsable || ''])
  } else {
    headers = ['Date', 'Lot', 'Statut', 'Responsable', 'Détail']
    data = rows.map(e => [d(e.date_demande || e.date_creation), lotOf(e), e.statut || '', e.responsable || '', (e.lignes || []).map(l => `${l.nb_cartons} ${l.type_flux} → ${l.zone?.nom || ''}`).join(' | ')])
  }
  const tabLabel = tabs.find(t => t.key === activeTab.value)?.label || activeTab.value
  exportExcel(headers, data, `historique-${activeTab.value}-${todayStamp()}.xlsx`, tabLabel)
}

watch(activeTab, () => loadData(), { immediate: true })
</script>

<style scoped>
.flow-metric { display: flex; flex-direction: column; }
.flow-metric strong { font-family: 'DM Serif Display', Georgia, serif; font-size: 25px; line-height: 0.9; color: var(--lime); }
.flow-metric span { margin-top: 4px; color: #C6D8CC; font-size: 9px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }

.hist-filters { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; gap: 16px; flex-wrap: wrap; }
.tabs { display: flex; gap: 4px; border-bottom: 2px solid var(--border); padding-bottom: 0; }
.tab {
  padding: 10px 18px; border: none; background: none; cursor: pointer;
  font-size: 14px; font-weight: 500; color: var(--text-muted);
  border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.2s;
  display: flex; align-items: center; gap: 6px;
}
.tab:hover { color: var(--primary); }
.tab.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }
.tab-count {
  background: var(--surface); color: var(--text-muted); padding: 1px 7px;
  border-radius: 99px; font-size: 11px; font-weight: 600;
}
.tab.active .tab-count { background: var(--primary-50); color: var(--primary); }
.hist-search { max-width: 240px; }
.lignes-list { display: flex; flex-wrap: wrap; gap: 4px; }
.line-chip {
  display: inline-block; padding: 2px 8px;
  background: var(--primary-50); color: var(--primary); border-radius: 10px;
  font-size: 11px; font-weight: 500;
}

/* Compact for search input */
.compact-search .hist-search {
  min-height: 32px;
  padding: 5px 10px;
  font-size: 12px;
  max-width: 200px;
}

.table-wrap { overflow: auto; max-height: 380px; }
.table { min-width: 800px; }
</style>
