<template>
  <div class="page">
    <PageHeader title="Historique global" subtitle="Consultation de toutes les étapes de production">
      <template #actions>
        <button class="btn btn-outline btn-sm" @click="loadData">↻ Actualiser</button>
        <button v-if="data.length > 0" class="btn btn-outline btn-sm" @click="exportCSV">↓ Export CSV</button>
      </template>
    </PageHeader>

    <WorkflowFrame
      :step="5"
      eyebrow="Suivi complet"
      title="Historique de production"
      description="Retrouvez toutes les saisies musserie, production, conditionnement et transferts du site."
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

    <!-- MUSSERIE -->
    <div v-else-if="activeTab === 'musserie'" class="anim-fade">
      <div v-if="filteredData.length === 0" class="empty"><div class="empty-text">Aucun enregistrement musserie</div></div>
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
import { getHistoriqueMusserie, getHistoriqueProduction, getHistoriqueConditionnement, getDemandesTransfert } from '../api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import WorkflowFrame from '../components/WorkflowFrame.vue'

const tabs = [
  { key: 'musserie', label: 'Musserie' },
  { key: 'production', label: 'Production' },
  { key: 'conditionnement', label: 'Conditionnement' },
  { key: 'transfert', label: 'Transfert CF' },
]

const activeTab = ref('musserie')
const data = ref([])
const loading = ref(false)
const recherche = ref('')
const counts = ref({})

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
    const code = (e.lot?.code_lot || '').toLowerCase()
    const fruit = (e.lot?.type_fruit || '').toLowerCase()
    return code.includes(q) || fruit.includes(q)
  })
})

async function loadData() {
  loading.value = true
  data.value = []
  try {
    const [mus, prod, cond, transf] = await Promise.all([
      getHistoriqueMusserie(),
      getHistoriqueProduction(),
      getHistoriqueConditionnement(),
      getDemandesTransfert(),
    ])
    counts.value = { musserie: mus.length, production: prod.length, conditionnement: cond.length, transfert: transf.length }
    if (activeTab.value === 'musserie') data.value = mus
    else if (activeTab.value === 'production') data.value = prod
    else if (activeTab.value === 'conditionnement') data.value = cond
    else if (activeTab.value === 'transfert') data.value = transf
  } finally { loading.value = false }
}

function switchTab(key) {
  activeTab.value = key
}

function exportCSV() {
  const rows = filteredData.value
  if (!rows.length) return
  const keys = Object.keys(rows[0])
  const csv = [
    keys.join(';'),
    ...rows.map(r => keys.map(k => {
      let v = r[k]
      if (v && typeof v === 'object') v = JSON.stringify(v)
      return `"${(v ?? '').toString().replace(/"/g, '""')}"`
    }).join(';'))
  ].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${activeTab.value}_historique.csv`
  a.click()
  URL.revokeObjectURL(url)
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

.table-wrap { overflow-x: auto; }
.table { min-width: 800px; }
</style>
