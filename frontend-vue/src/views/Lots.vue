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
      <select v-model="filtreEtape" class="input" @change="loadLots" style="max-width:180px">
        <option value="">Toutes étapes</option>
        <option value="musserie">Musserie</option>
        <option value="production">Production</option>
        <option value="conditionnement">Conditionnement</option>
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
            <th>Poids Frais</th>
            <th>Traité</th>
            <th>Progression</th>
            <th>Statut</th>
            <th>Workflow</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="lot in lots" :key="lot.id">
            <tr @click="expandLot(lot.id)" style="cursor:pointer" :class="{ 'row-expanded': expanded === lot.id }">
              <td><strong>{{ lot.code_lot }}</strong></td>
              <td>{{ lot.type_fruit || lot.produit?.nom || '—' }}</td>
              <td>{{ formatKg(lot.poids_frais) }} kg</td>
              <td>
                <span v-if="getCumulTraite(lot) > 0" class="traite-val">{{ formatKg(getCumulTraite(lot)) }} kg</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td style="min-width:120px">
                <div class="progress-cell">
                  <div class="mini-progress">
                    <div class="mini-progress-fill" :style="{ width: lotProgressPct(lot) + '%' }"></div>
                  </div>
                  <span class="progress-pct">{{ lotProgressPct(lot) }}%</span>
                </div>
              </td>
              <td><StatusBadge :status="lot.statut" /></td>
              <td style="min-width:240px"><WorkflowProgress :statut="lot.statut" /></td>
              <td>
                <button v-if="toCanonical(lot.statut) === RECEPTION" class="btn btn-sm btn-primary" @click.stop="avancer(lot.id, EN_MUSSERIE)">→ Musserie</button>
                <button v-else-if="toCanonical(lot.statut) === EN_MUSSERIE" class="btn btn-sm btn-outline" @click.stop="$router.push('/musserie')">Ouvrir</button>
                <button v-else-if="toCanonical(lot.statut) === EN_PRODUCTION" class="btn btn-sm btn-outline" @click.stop="$router.push('/production')">Ouvrir</button>
                <button v-else-if="toCanonical(lot.statut) === EN_CONDITIONNEMENT" class="btn btn-sm btn-outline" @click.stop="$router.push('/conditionnement')">Ouvrir</button>
                <button v-else-if="toCanonical(lot.statut) === CONDITIONNE" class="btn btn-sm btn-outline" @click.stop="$router.push('/conditionnement')">Ouvrir</button>
                <span v-else class="text-muted" style="font-size:12px">Terminé</span>
              </td>
            </tr>
            <tr v-if="expanded === lot.id && etapes[lot.id]" class="etapes-row">
              <td colspan="8" style="padding:0">
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
                  <div v-if="hasCartons(lot)" class="carton-summary">
                    <span v-if="lot.export_cartons > 0"><strong>{{ lot.export_cartons }}</strong> exp</span>
                    <span v-if="lot.local_cartons > 0"><strong>{{ lot.local_cartons }}</strong> loc</span>
                    <span v-if="lot.fitini_fê_cartons > 0"><strong>{{ lot.fitini_fê_cartons }}</strong> fit</span>
                    <span v-if="lot.dechets_cartons > 0"><strong>{{ lot.dechets_cartons }}</strong> déc</span>
                    <span v-if="lot.rhum_cartons > 0"><strong>{{ lot.rhum_cartons }}</strong> rhum</span>
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

import { RECEPTION, EN_MUSSERIE, EN_PRODUCTION, CONDITIONNE, EN_STOCK, EXPEDIE, PERIME, toCanonical, TERMINE, EN_COURS, EN_ATTENTE } from '../utils/statuses'

const route = useRoute()
const lots = ref([])
const etapes = ref({})
const loading = ref(true)
const recherche = ref(route.query.q || '')
const filtreStatut = ref('')
const filtreEtape = ref('')
const expanded = ref(null)
const viewMode = ref('table')
const toast = useToastStore()

const statuts = [RECEPTION, EN_MUSSERIE, EN_PRODUCTION, CONDITIONNE, EN_STOCK, EXPEDIE, PERIME]

function formatKg(v) { return Math.round(v || 0).toLocaleString('fr-FR') }

function getCumulTraite(lot) {
  if (lot.statut === 'reception') return 0
  return lot.poids_frais - (lot.quantite_restante || lot.poids_frais)
}

function lotProgressPct(lot) {
  if (!lot.poids_frais) return 0
  const traite = getCumulTraite(lot)
  return Math.min(100, Math.round((traite / lot.poids_frais) * 100))
}

function hasCartons(lot) {
  return (lot.export_cartons || 0) + (lot.local_cartons || 0) + (lot.dechets_cartons || 0) + (lot.rhum_cartons || 0) + (lot['fitini_fê_cartons'] || 0) > 0
}

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
    if (filtreEtape.value) params.etape = filtreEtape.value
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
.filters { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.traite-val { font-weight: 600; color: var(--primary); }
.row-expanded { background: var(--surface); }
.progress-cell { display: flex; align-items: center; gap: 8px; }
.mini-progress { flex: 1; height: 6px; background: var(--border-light); border-radius: 3px; overflow: hidden; }
.mini-progress-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--success)); border-radius: 3px; transition: width 0.4s; }
.progress-pct { font-size: 11px; font-weight: 600; color: var(--text-secondary); min-width: 32px; text-align: right; }
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
.carton-summary { margin-top: 10px; padding: 8px 12px; background: var(--primary-50); border-radius: var(--radius-sm); font-size: 12px; color: var(--secondary); display: flex; gap: 12px; flex-wrap: wrap; }
.view-toggle { display: flex; gap: 4px; background: var(--surface); border-radius: var(--radius-sm); padding: 3px; }
.text-muted { color: var(--text-muted); }
@media (max-width: 768px) { .view-toggle { width: 100%; } .view-toggle button { flex: 1; } }
</style>
