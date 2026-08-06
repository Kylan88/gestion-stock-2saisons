<template>
  <div class="page">
    <PageHeader title="Historique global" subtitle="Consultation de toutes les étapes de production" />

    <div class="tabs">
      <button v-for="t in tabs" :key="t.key" class="tab" :class="{ active: activeTab === t.key }" @click="switchTab(t.key)">
        {{ t.label }}
      </button>
    </div>

    <LoadingSpinner v-if="loading" />

    <!-- MUSSERIE -->
    <div v-else-if="activeTab === 'musserie'" class="anim-fade">
      <div v-if="data.length === 0" class="empty"><div class="empty-text">Aucun enregistrement musserie</div></div>
      <table v-else class="table">
        <thead><tr><th>Date</th><th>Lot</th><th>Fruit</th><th>Poids manipulé</th><th>Poids en musserie</th><th>Opérateur</th></tr></thead>
        <tbody>
          <tr v-for="e in data" :key="e.id">
            <td>{{ fmtDate(e.date_debut) }}</td>
            <td><strong>{{ e.lot?.code_lot || e.lot_id }}</strong></td>
            <td>{{ e.lot?.type_fruit || '—' }}</td>
            <td>{{ e.poids_entree }} kg</td>
            <td>{{ e.poids_sortie }} kg</td>
            <td>{{ e.operateur || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- PRODUCTION -->
    <div v-else-if="activeTab === 'production'" class="anim-fade">
      <div v-if="data.length === 0" class="empty"><div class="empty-text">Aucun enregistrement production</div></div>
      <table v-else class="table">
        <thead><tr><th>Date</th><th>Lot</th><th>Séchoir</th><th>Poids entrée</th><th>Poids sortie</th><th>Opérateur</th></tr></thead>
        <tbody>
          <tr v-for="e in data" :key="e.id">
            <td>{{ fmtDate(e.date_debut) }}</td>
            <td><strong>{{ e.lot?.code_lot || e.lot_id }}</strong></td>
            <td>{{ e.dryer_id || '—' }}</td>
            <td>{{ e.poids_entree }} kg</td>
            <td>{{ e.poids_sortie || '—' }} kg</td>
            <td>{{ e.operateur || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- CONDITIONNEMENT -->
    <div v-else-if="activeTab === 'conditionnement'" class="anim-fade">
      <div v-if="data.length === 0" class="empty"><div class="empty-text">Aucun enregistrement conditionnement</div></div>
      <table v-else class="table">
        <thead><tr><th>Date début</th><th>Date fin</th><th>Lot</th><th>Statut</th><th>Poids entrée</th><th>Poids sortie</th><th>Rendement</th><th>Opérateur</th></tr></thead>
        <tbody>
          <tr v-for="e in data" :key="e.id">
            <td>{{ fmtDate(e.date_debut) }}</td>
            <td>{{ fmtDate(e.date_fin) }}</td>
            <td><strong>{{ e.lot?.code_lot || e.lot_id }}</strong></td>
            <td><StatusBadge :status="e.statut" /></td>
            <td>{{ e.poids_entree }} kg</td>
            <td>{{ e.poids_sortie || '—' }} kg</td>
            <td>{{ e.rendement_pourcentage ? e.rendement_pourcentage + '%' : '—' }}</td>
            <td>{{ e.operateur || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- TRANSFERT CF -->
    <div v-else-if="activeTab === 'transfert'" class="anim-fade">
      <div v-if="data.length === 0" class="empty"><div class="empty-text">Aucune demande de transfert</div></div>
      <table v-else class="table">
        <thead><tr><th>Date</th><th>Lot</th><th>Statut</th><th>Responsable</th><th>Lignes</th><th>Notes</th></tr></thead>
        <tbody>
          <tr v-for="e in data" :key="e.id">
            <td>{{ fmtDate(e.date_creation) }}</td>
            <td><strong>{{ e.lot?.code_lot || e.lot_id }}</strong></td>
            <td><StatusBadge :status="e.statut" /></td>
            <td>{{ e.responsable || '—' }}</td>
            <td>
              <span v-for="(l, i) in (e.lignes || [])" :key="i" class="line-chip">{{ l.type_flux }} → {{ l.zone?.nom || '—' }}</span>
            </td>
            <td>{{ e.notes || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getHistoriqueMusserie, getHistoriqueProduction, getHistoriqueConditionnement, getDemandesTransfert } from '../api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'

const tabs = [
  { key: 'musserie', label: 'Musserie' },
  { key: 'production', label: 'Production' },
  { key: 'conditionnement', label: 'Conditionnement' },
  { key: 'transfert', label: 'Transfert CF' },
]

const activeTab = ref('musserie')
const data = ref([])
const loading = ref(false)

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function loadData() {
  loading.value = true
  data.value = []
  try {
    if (activeTab.value === 'musserie') data.value = await getHistoriqueMusserie()
    else if (activeTab.value === 'production') data.value = await getHistoriqueProduction()
    else if (activeTab.value === 'conditionnement') data.value = await getHistoriqueConditionnement()
    else if (activeTab.value === 'transfert') data.value = await getDemandesTransfert()
  } finally { loading.value = false }
}

function switchTab(key) {
  activeTab.value = key
}

watch(activeTab, () => loadData(), { immediate: true })
</script>

<style scoped>
.tabs {
  display: flex; gap: 4px; margin-bottom: 20px;
  border-bottom: 2px solid var(--border); padding-bottom: 0;
}
.tab {
  padding: 10px 18px; border: none; background: none; cursor: pointer;
  font-size: 14px; font-weight: 500; color: var(--text-muted);
  border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.2s;
}
.tab:hover { color: var(--primary); }
.tab.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }
.line-chip {
  display: inline-block; padding: 2px 8px; margin: 1px 2px;
  background: var(--primary-50); color: var(--primary); border-radius: 10px;
  font-size: 11px; font-weight: 500;
}
</style>
