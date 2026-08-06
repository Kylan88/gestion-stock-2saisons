<template>
  <div class="page">
    <PageHeader title="Lots de Production" subtitle="Suivi de tous les lots et leurs étapes">
      <template #actions>
        <div class="view-toggle">
          <button class="btn btn-sm" :class="viewMode === 'table' ? 'btn-primary' : 'btn-ghost'" @click="viewMode = 'table'">Table</button>
          <button class="btn btn-sm" :class="viewMode === 'pipeline' ? 'btn-primary' : 'btn-ghost'" @click="viewMode = 'pipeline'">Pipeline</button>
        </div>
        <button class="btn btn-outline btn-sm" @click="doPrint">Imprimer</button>
        <button class="btn btn-outline btn-sm" @click="doExport">CSV</button>
      </template>
    </PageHeader>

    <div class="filters">
      <input v-model="recherche" class="input" placeholder="Rechercher code lot..." @input="debouncedLoad" style="max-width:260px" />
      <select v-model="filtreStatut" class="input" @change="loadLots" style="max-width:180px">
        <option value="">Tous les statuts</option>
        <option v-for="s in statuts" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <LoadingSpinner v-if="loading" />
    <div v-else-if="lots.length === 0" class="empty anim-fade">
        <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
        <div class="empty-text">Aucun lot trouvé</div>
    </div>

    <!-- Pipeline View -->
    <PipelineView v-else-if="viewMode === 'pipeline'" :lots="lots"
      @avancer="avancer" @goMusserie="$router.push('/musserie')" @goTransfert="$router.push('/stock/transfert')" />

    <!-- Table View -->
    <div v-else class="table-wrap anim-fade">
      <table>
        <thead>
          <tr>
            <th>Code Lot</th>
            <th>Produit</th>
            <th>Fournisseur</th>
            <th>Poids</th>
            <th>Rendement</th>
            <th>Statut</th>
            <th>Workflow</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="lot in lots" :key="lot.id">
            <tr @click="expandLot(lot.id)" style="cursor:pointer">
              <td><strong>{{ lot.code_lot }}</strong></td>
              <td>{{ lot.type_fruit || lot.produit?.nom || '—' }}</td>
              <td>{{ lot.fournisseur_nom || lot.fournisseur?.nom || '—' }}</td>
              <td>{{ lot.poids_frais }} kg</td>
              <td>{{ lot.rendement_global ? lot.rendement_global + '%' : '—' }}</td>
              <td><StatusBadge :status="lot.statut" /></td>
              <td style="min-width:260px"><WorkflowProgress :statut="lot.statut" /></td>
              <td>
                <button v-if="toCanonical(lot.statut) === RECEPTION" class="btn btn-sm btn-primary" @click.stop="avancer(lot.id, EN_MUSSERIE)">→ Musserie</button>
                <button v-else-if="toCanonical(lot.statut) === EN_MUSSERIE" class="btn btn-sm btn-outline" @click.stop="$router.push('/musserie')">Ouvrir</button>
                <button v-else-if="toCanonical(lot.statut) === CONDITIONNE" class="btn btn-sm btn-outline" @click.stop="$router.push('/conditionnement')">Conditionner</button>
              </td>
            </tr>
            <tr v-if="expanded === lot.id && etapes[lot.id]" class="etapes-row">
              <td colspan="7" style="padding:0">
                <div class="etapes-expand anim-expand">
                  <div v-for="e in etapes[lot.id]" :key="e.id" class="etape-item">
                    <div class="etape-left">
                      <span class="status-dot" :class="{
                        'status-dot-active': toCanonical(e.statut) === TERMINE,
                        'status-dot-warning': toCanonical(e.statut) === EN_COURS,
                        'status-dot-error': toCanonical(e.statut) === EN_ATTENTE
                      }"></span>
                      <span class="etape-nom">{{ e.etape }}</span>
                      <StatusBadge :status="e.statut" />
                    </div>
                    <div class="etape-right">
                      <span v-if="e.operateur" class="etape-op">{{ e.operateur }}</span>
                      <span v-if="e.poids_entree" class="etape-pds">{{ e.poids_entree }} → {{ e.poids_sortie || '?' }} kg</span>
                      <span v-if="e.rendement_pourcentage" class="etape-rdt">{{ e.rendement_pourcentage }}%</span>
                    </div>
                  </div>
                  <div v-if="lot.export_cartons > 0" class="carton-summary">
                    Export: {{ lot.export_cartons }} cart. · Local: {{ lot.local_cartons }} cart. · Déchets: {{ lot.dechets_cartons }} cart. · Rhum: {{ lot.rhum_cartons }} cart.
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getLots, getProductionsEtapes, updateLotStatut } from '../api'
import { useToastStore } from '../stores/toast'
import { exportCsv } from '../utils/exportCsv'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import WorkflowProgress from '../components/WorkflowProgress.vue'
import PipelineView from '../components/PipelineView.vue'

import { RECEPTION, EN_MUSSERIE, EN_PRODUCTION, EN_SECHAGE, CONDITIONNE, EN_STOCK, EXPEDIE, PERIME, toCanonical, TERMINE, EN_COURS, EN_ATTENTE } from '../utils/statuses'

const route = useRoute()
const lots = ref([])
const etapes = ref({})
const loading = ref(true)
const recherche = ref(route.query.q || '')
const filtreStatut = ref('')
const expanded = ref(null)
const viewMode = ref('table')
const toast = useToastStore()

const statuts = [RECEPTION, EN_MUSSERIE, EN_PRODUCTION, CONDITIONNE, EN_STOCK, EXPEDIE, PERIME]

let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadLots(), 300)
}

async function loadLots() {
  loading.value = true
  try {
    const params = {}
    if (filtreStatut.value) params.statut = filtreStatut.value
    if (recherche.value) params.recherche = recherche.value
    lots.value = await getLots(params)
  } finally { loading.value = false }
}

async function expandLot(id) {
  if (expanded.value === id) { expanded.value = null; return }
  expanded.value = id
  if (!etapes.value[id]) {
    etapes.value[id] = await getProductionsEtapes(id)
  }
}

async function avancer(id, statut) {
  try {
    await updateLotStatut(id, statut)
    toast.success('Statut mis à jour')
    await loadLots()
  } catch {}
}

function doPrint() { window.print() }

function doExport() {
  const headers = ['Code Lot', 'Type Fruit', 'Poids Frais (kg)', 'Statut', 'Fournisseur', 'Date Réception']
  const rows = lots.value.map(l => [l.code_lot, l.type_fruit || '', l.poids_frais, l.statut, l.fournisseur_nom || '', l.date_reception ? new Date(l.date_reception).toLocaleDateString('fr-FR') : ''])
  exportCsv(headers, rows, 'lots.csv')
}

onMounted(loadLots)
</script>

<style scoped>
.etapes-row td { background: var(--surface); padding: 0 !important; }
.etapes-expand { padding: 14px 20px; }
.etape-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 0; border-bottom: 1px solid var(--border-light); font-size: 13px;
}
.etape-item:last-child { border-bottom: none; }
.etape-left { display: flex; align-items: center; gap: 10px; }
.etape-nom { font-weight: 600; min-width: 120px; text-transform: capitalize; }
.etape-right { display: flex; align-items: center; gap: 14px; color: var(--text-secondary); font-size: 12px; }
.carton-summary { margin-top: 10px; padding: 8px 12px; background: var(--primary-50); border-radius: var(--radius-sm); font-size: 12px; color: var(--secondary); }
.view-toggle { display: flex; gap: 4px; background: var(--surface); border-radius: var(--radius-sm); padding: 3px; }
@media (max-width: 768px) { .view-toggle { width: 100%; } .view-toggle button { flex: 1; } }
</style>
