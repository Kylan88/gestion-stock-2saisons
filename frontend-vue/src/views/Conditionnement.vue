<template>
  <div class="page">
    <PageHeader title="Conditionnement" subtitle="Mise en cartons — 1 carton = 6 sachets — saisie journalière cumulée">
      <template #actions>
        <button class="btn btn-outline" @click="showHistorique = !showHistorique">
          {{ showHistorique ? 'Retour' : 'Historique' }}
        </button>
      </template>
    </PageHeader>

    <!-- HISTORIQUE -->
    <div v-if="showHistorique" class="anim-fade">
      <LoadingSpinner v-if="loadingHist" />
      <div v-else-if="historique.length === 0" class="empty">
        <div class="empty-text">Aucun conditionnement enregistré</div>
      </div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Date début</th>
            <th>Date fin</th>
            <th>Lot</th>
            <th>Statut</th>
            <th>Poids entrée</th>
            <th>Poids sortie</th>
            <th>Rendement</th>
            <th>Opérateur</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ep in historique" :key="ep.id">
            <td>{{ formatDate(ep.date_debut) }}</td>
            <td>{{ formatDate(ep.date_fin) }}</td>
            <td><strong>{{ ep.lot?.code_lot || ep.lot_id }}</strong></td>
            <td><StatusBadge :status="ep.statut" /></td>
            <td>{{ ep.poids_entree }} kg</td>
            <td>{{ ep.poids_sortie || '—' }} kg</td>
            <td>{{ ep.rendement_pourcentage ? ep.rendement_pourcentage + '%' : '—' }}</td>
            <td>{{ ep.operateur || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- FORMULAIRE -->
    <div v-else>
      <LoadingSpinner v-if="loading" />
      <div v-else-if="lots.length === 0" class="empty anim-fade">
        <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
        <div class="empty-text">Aucun lot en attente de conditionnement</div>
      </div>

      <div v-for="lot in lots" :key="lot.id" class="card anim-fade" style="margin-bottom:16px">
        <div class="card-header" style="margin-bottom:0">
          <div style="display:flex;align-items:center;gap:10px">
            <strong>{{ lot.code_lot }}</strong>
            <span style="color:var(--text-secondary);font-size:13px">{{ lot.type_fruit || lot.produit?.nom }}</span>
            <StatusBadge :status="lot.statut" />
          </div>
          <span style="font-size:13px;color:var(--text-muted)">Réf. entrée : <strong>{{ refEntree(lot) }} kg</strong></span>
        </div>

        <!-- Déjà conditionné (cumul enregistré) -->
        <div v-if="hasCumul(lot)" class="etape-section">
          <div class="cumul-cond">
            <div class="cumul-cond-title">Déjà conditionné (cumul)</div>
            <div class="cumul-cond-grid">
              <div v-for="flux in getFluxList(lot)" :key="'cum-'+flux.key" class="cumul-cond-item">
                <span class="cumul-cond-label">{{ flux.label }}</span>
                <span class="cumul-cond-val"><strong>{{ getCumulCartons(lot, flux.key) }}</strong> cartons · <strong>{{ getCumulSachets(lot, flux.key) }}</strong> sachets · {{ cumulPoidsFlux(lot, flux.key) }} kg</span>
              </div>
            </div>
            <div class="cumul-cond-total">
              Total cumulé : <strong>{{ totalCumulPoids(lot) }} kg</strong>
              <span v-if="ecartCumul(lot) != null"> — Écart : <strong>{{ ecartCumul(lot) }}%</strong></span>
            </div>
          </div>

          <div style="margin-top:12px;text-align:right">
            <button class="btn btn-success" :disabled="cloturing" @click="confirmClotureLot = lot">
              {{ cloturing ? 'Clôture...' : 'Clôturer le conditionnement' }}
            </button>
          </div>
        </div>

        <!-- Formulaire ajout journalier -->
        <div class="cond-form">
          <div class="cond-form-title">{{ hasCumul(lot) ? 'Ajouter la journée' : 'Nouveau conditionnement' }}</div>
          <div class="flux-grid">
            <div v-for="flux in getFluxList(lot)" :key="flux.key" class="flux-card">
              <div class="flux-head" :style="{ borderColor: flux.color }">
                <span>{{ flux.label }}</span>
                <span class="flux-weight">{{ fluxPoids(lot.id, flux.key) }} kg</span>
              </div>
              <div class="flux-inputs">
                <div class="form-group">
                  <label>Cartons</label>
                  <input type="number" v-model.number="form[lot.id][flux.key + '_cartons']" class="input" min="0" @input="recalc(lot.id)" />
                </div>
                <div class="form-group">
                  <label>Sachets indiv.</label>
                  <input type="number" v-model.number="form[lot.id][flux.key + '_sachets']" class="input" min="0" @input="recalc(lot.id)" />
                </div>
                <div class="form-group">
                  <label>Poids/sachet</label>
                  <input type="number" v-model.number="form[lot.id][flux.key + '_poids_sachet']" class="input" step="0.1" min="0" @input="recalc(lot.id)" />
                </div>
              </div>
            </div>
          </div>

          <div class="bilan-bar">
            <span>Ajout : <strong>{{ totalPoids(lot.id) }} kg</strong></span>
            <span>Écart : <strong>{{ ecartVal(lot.id) ?? '—' }}%</strong></span>
          </div>

          <div class="form-row" style="margin-top:14px">
            <div class="form-group" style="flex:1">
              <label>Responsable</label>
              <input v-model="form[lot.id].responsable" class="input" placeholder="Nom" />
            </div>
            <div class="form-group" style="flex:2">
              <label>Notes</label>
              <input v-model="form[lot.id].notes" class="input" placeholder="Observations" />
            </div>
            <div class="form-group" style="flex:0">
              <label>&nbsp;</label>
              <button class="btn btn-primary" :disabled="totalPoids(lot.id) <= 0 || saving" @click="enregistrer(lot)">
                {{ saving ? '...' : 'Enregistrer' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TRANSFERT CF PANEL -->
    <div v-if="!showHistorique && transfertLots.length > 0" style="margin-top:24px">
      <h2 style="font-size:16px;font-weight:600;margin-bottom:12px;color:var(--dark)">Transfert Chambre Froide</h2>
      <div v-for="lot in transfertLots" :key="'tf-'+lot.id" class="card anim-fade" style="margin-bottom:12px;border-left:3px solid var(--primary)">
        <div class="card-header" style="margin-bottom:12px">
          <div style="display:flex;align-items:center;gap:8px">
            <strong>{{ lot.code_lot }}</strong>
            <span style="font-size:12px;color:var(--text-muted)">
              {{ lot.export_cartons || 0 }} export · {{ lot.local_cartons || 0 }} local · {{ lot['fitini_fê_cartons'] || 0 }} fitini · {{ lot.dechets_cartons || 0 }} déchets · {{ lot.rhum_cartons || 0 }} rhum
            </span>
          </div>
        </div>
        <div class="tf-flux-grid">
          <div v-for="tf in transfertFluxes" :key="tf.key" v-if="lot[tf.cartons_field] > 0" class="tf-flux-row">
            <label class="tf-flux-label">{{ tf.label }} ({{ lot[tf.cartons_field] }} cartons dispo)</label>
            <div style="display:flex;gap:6px">
              <input type="number" v-model.number="transfertForm[lot.id][tf.key + '_cartons']" class="input" min="0" :max="lot[tf.cartons_field]" placeholder="Cartons" style="flex:1" />
              <select v-model="transfertForm[lot.id][tf.key + '_zone_id']" class="input" style="flex:1">
                <option v-for="z in zones" :key="z.id" :value="z.id">{{ z.nom }}</option>
              </select>
            </div>
          </div>
        </div>
        <div class="form-row" style="margin-top:10px">
          <div class="form-group" style="flex:1"><label>Responsable</label><input v-model="transfertForm[lot.id].responsable" class="input" placeholder="Nom" /></div>
          <div class="form-group" style="flex:0">
            <label>&nbsp;</label>
            <button class="btn btn-primary btn-sm" :disabled="savingTransfert || !canTransfert(lot.id)" @click="transférer(lot)">
              {{ savingTransfert ? '...' : 'Transférer' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :show="!!confirmClotureLot"
      title="Clôturer le conditionnement ?"
      :message="'Terminer le conditionnement pour ' + (confirmClotureLot?.code_lot || '') + ' ? Le lot passera en chambre froide. Cette action est irréversible.'"
      confirmText="Clôturer"
      variant="warning"
      @confirm="cloturer(confirmClotureLot)"
      @cancel="confirmClotureLot = null"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { getLots, getProductionsEtapes, validerConditionnement, cloturerConditionnement, getHistoriqueConditionnement, getZonesStock, creerDemandeTransfert, validerDemandeTransfert } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { toCanonical, EN_PRODUCTION, CONDITIONNE } from '../utils/statuses'

const lots = ref([])
const zones = ref([])
const loading = ref(true)
const saving = ref(false)
const cloturing = ref(false)
const form = reactive({})
const etapesData = ref({})
const refs = reactive({})
const ecarts = reactive({})
const toast = useToastStore()
const confirmClotureLot = ref(null)

const showHistorique = ref(false)
const historique = ref([])
const loadingHist = ref(false)

const transfertLots = ref([])
const transfertForm = reactive({})
const savingTransfert = ref(false)

const transfertFluxes = [
  { key: 'export', label: 'Export', cartons_field: 'export_cartons' },
  { key: 'local', label: 'Local', cartons_field: 'local_cartons' },
  { key: 'fitini_fê', label: 'Fitini Fê', cartons_field: 'fitini_fê_cartons' },
  { key: 'dechets', label: 'Déchets', cartons_field: 'dechets_cartons' },
  { key: 'rhum', label: 'Rhum', cartons_field: 'rhum_cartons' },
]

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function loadHistorique() {
  loadingHist.value = true
  try { historique.value = await getHistoriqueConditionnement() } finally { loadingHist.value = false }
}

watch(showHistorique, (v) => { if (v) loadHistorique() })

const allFluxes = [
  { key: 'export', label: 'Export', color: '#165B3D' },
  { key: 'local', label: 'Local', color: '#0B2E20' },
  { key: 'fitini_fê', label: 'Fitini Fê', color: '#8B5CF6' },
  { key: 'dechets', label: 'Déchets', color: '#EF4444' },
  { key: 'rhum', label: 'Rhum (mangue uniquement)', color: '#D97706' },
]

function getFluxList(lot) {
  const nom = lot.type_fruit || lot.produit?.nom || ''
  const isMangue = nom.toLowerCase().includes('mangue')
  return allFluxes.filter(f => f.key !== 'rhum' || isMangue)
}

function refEntree(lot) { return refs[lot.id] ?? 0 }

function fluxPoids(lotId, key) {
  const d = form[lotId]
  if (!d) return 0
  const c = d[key + '_cartons'] || 0
  const s = d[key + '_sachets'] || 0
  const p = d[key + '_poids_sachet'] || 2.5
  return Math.round(((c * 6) + s) * p * 100) / 100
}

function totalPoids(lotId) { return allFluxes.reduce((s, fl) => s + fluxPoids(lotId, fl.key), 0) }

function ecartVal(lotId) {
  const ref = refs[lotId] || 0
  const total = totalPoids(lotId)
  if (!ref || !total) return null
  return Math.round(Math.abs(ref - total) / ref * 10000) / 100
}

function recalc(lotId) { ecarts[lotId] = ecartVal(lotId) }

function hasCumul(lot) {
  return (lot.export_cartons || 0) + (lot.local_cartons || 0) + (lot.dechets_cartons || 0) +
         (lot.rhum_cartons || 0) + (lot['fitini_fê_cartons'] || 0) > 0
}

function getCumulCartons(lot, key) {
  const field = key === 'fitini_fê' ? 'fitini_fê_cartons' : key + '_cartons'
  return lot[field] || 0
}
function getCumulSachets(lot, key) {
  const field = key === 'fitini_fê' ? 'fitini_fê_sachets' : key + '_sachets'
  return lot[field] || 0
}
function cumulPoidsFlux(lot, key) {
  const cartons = getCumulCartons(lot, key)
  const sachets = getCumulSachets(lot, key)
  const pField = key === 'fitini_fê' ? 'fitini_fê_poids_sachet' : key + '_poids_sachet'
  const p = lot[pField] || 2.5
  return Math.round(((cartons * 6) + sachets) * p * 100) / 100
}
function totalCumulPoids(lot) {
  return Math.round(getFluxList(lot).reduce((s, fl) => s + cumulPoidsFlux(lot, fl.key), 0) * 100) / 100
}
function ecartCumul(lot) {
  const ref = refs[lot.id] || 0
  const total = totalCumulPoids(lot)
  if (!ref || !total) return null
  return Math.round(Math.abs(ref - total) / ref * 10000) / 100
}

async function load() {
  loading.value = true
  try {
    const [raw, z] = await Promise.all([getLots(), getZonesStock()])
    zones.value = z.filter(zz => zz.actif)

    const result = []
    const filtered = raw.filter(l => [EN_PRODUCTION, CONDITIONNE].includes(toCanonical(l.statut)))
    for (const lot of filtered) {
      etapesData.value[lot.id] = await getProductionsEtapes(lot.id)
      const epProd = etapesData.value[lot.id].find(e => e.etape === 'production')
      if (epProd && toCanonical(epProd.statut) !== 'termine') continue
      result.push(lot)
      if (!form[lot.id]) {
        form[lot.id] = reactive({
          export_cartons: 0, export_sachets: 0, export_poids_sachet: lot.export_poids_sachet || 2.5,
          local_cartons: 0, local_sachets: 0, local_poids_sachet: lot.local_poids_sachet || 2.5,
          fitini_fê_cartons: 0, fitini_fê_sachets: 0, fitini_fê_poids_sachet: lot['fitini_fê_poids_sachet'] || 2.5,
          dechets_cartons: 0, dechets_sachets: 0, dechets_poids_sachet: lot.dechets_poids_sachet || 2.5,
          rhum_cartons: 0, rhum_sachets: 0, rhum_poids_sachet: lot.rhum_poids_sachet || 2.5,
          responsable: '', notes: '',
        })
      }
      refs[lot.id] = etapesData.value[lot.id].find(e => e.etape === 'conditionnement')?.poids_entree || 0
      recalc(lot.id)
    }
    lots.value = result

    transfertLots.value = raw.filter(l => {
      if (toCanonical(l.statut) !== CONDITIONNE) return false
      return transfertFluxes.some(tf => (l[tf.cartons_field] || 0) > 0)
    })
    for (const lot of transfertLots.value) {
      if (!transfertForm[lot.id]) {
        const tfInit = {}
        for (const tf of transfertFluxes) {
          tfInit[tf.key + '_cartons'] = lot[tf.cartons_field] || 0
          tfInit[tf.key + '_zone_id'] = zones.value[0]?.id || 1
        }
        tfInit.responsable = ''
        tfInit.notes = ''
        transfertForm[lot.id] = reactive(tfInit)
      }
    }
  } finally { loading.value = false }
}

async function enregistrer(lot) {
  saving.value = true
  try {
    await validerConditionnement(lot.id, form[lot.id])
    toast.success(`Conditionnement enregistré pour ${lot.code_lot}`)
    await load()
  } finally { saving.value = false }
}

async function cloturer(lot) {
  confirmClotureLot.value = null
  cloturing.value = true
  try {
    await cloturerConditionnement(lot.id)
    toast.success(`Conditionnement clôturé pour ${lot.code_lot} — passage en chambre froide`)
    await load()
  } finally { cloturing.value = false }
}

function canTransfert(lotId) {
  const d = transfertForm[lotId]
  if (!d) return false
  return transfertFluxes.some(tf => (d[tf.key + '_cartons'] || 0) > 0 && d[tf.key + '_zone_id'])
}

async function transférer(lot) {
  const d = transfertForm[lot.id]
  if (!d) return
  savingTransfert.value = true
  try {
    const lignes = []
    for (const tf of transfertFluxes) {
      const nb = d[tf.key + '_cartons'] || 0
      if (nb > 0) lignes.push({ type_flux: tf.key, nb_cartons: nb, zone_id: d[tf.key + '_zone_id'] })
    }
    if (!lignes.length) return
    const demande = await creerDemandeTransfert({ lot_id: lot.id, responsable: d.responsable, notes: d.notes, lignes })
    await validerDemandeTransfert(demande.id)
    toast.success(`Transfert CF validé pour ${lot.code_lot}`)
    await load()
  } finally { savingTransfert.value = false }
}

onMounted(load)
</script>

<style scoped>
.etape-section { border-top: 1px solid var(--border-light); margin-top: 14px; padding-top: 14px; }
.cumul-cond { padding: 12px 14px; background: var(--success-light); border-radius: var(--radius-sm); margin-bottom: 10px; }
.cumul-cond-title { font-size: 12px; font-weight: 600; text-transform: uppercase; color: #166534; margin-bottom: 8px; letter-spacing: 0.3px; }
.cumul-cond-grid { display: flex; flex-wrap: wrap; gap: 6px 20px; font-size: 12px; color: #15803D; }
.cumul-cond-item { display: flex; gap: 6px; }
.cumul-cond-label { font-weight: 600; }
.cumul-cond-val { }
.cumul-cond-total { margin-top: 8px; font-size: 13px; font-weight: 600; color: #166534; }
.cond-form { padding-top: 14px; }
.cond-form-title { font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px; margin-bottom: 8px; }
.flux-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 14px; }
.flux-card { border: 1px solid var(--border); border-radius: var(--radius-sm); overflow: hidden; }
.flux-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; background: var(--surface); font-size: 13px; font-weight: 600;
  border-left: 3px solid;
}
.flux-weight { font-size: 14px; font-weight: 700; color: var(--dark); }
.flux-inputs { padding: 12px 14px; display: flex; flex-direction: column; gap: 8px; }
.bilan-bar {
  display: flex; align-items: center; gap: 16px; padding: 10px 14px;
  border-radius: var(--radius-sm); font-size: 12px; flex-wrap: wrap;
  background: var(--surface); color: var(--text-secondary);
}
@media (max-width: 768px) { .flux-grid { grid-template-columns: 1fr !important; } }
.tf-flux-grid { display: flex; flex-direction: column; gap: 8px; padding: 0 14px; }
.tf-flux-row { display: flex; flex-direction: column; gap: 4px; }
.tf-flux-label { font-size: 12px; font-weight: 600; color: var(--text-secondary); }
</style>
