<template>
  <div class="page">
    <PageHeader title="Conditionnement" subtitle="Mise en cartons — saisie journalière cumulative">
      <template #actions>
        <div class="tabs">
          <button class="tab" :class="{ active: activeView === 'saisie' }" @click="activeView = 'saisie'">
            Saisie
          </button>
          <button class="tab" :class="{ active: activeView === 'historique' }" @click="activeView = 'historique'; loadHistorique()">
            Historique
          </button>
        </div>
      </template>
    </PageHeader>

    <WorkflowFrame
      :step="4"
      eyebrow="Finition & répartition"
      title="Composer la sortie du lot"
      description="Répartissez chaque production par flux, contrôlez l'écart et préparez le transfert vers les zones de stockage."
    >
      <template #meta><div class="flow-metric"><strong>{{ lots.length }}</strong><span>à finaliser</span></div></template>
    </WorkflowFrame>

    <!-- HISTORIQUE -->
    <div v-if="activeView === 'historique'" class="anim-fade">
      <LoadingSpinner v-if="loadingHist" />
      <div v-else-if="historique.length === 0" class="empty">
        <div class="empty-text">Aucun conditionnement enregistré</div>
      </div>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Date</th><th>Lot</th><th>Poids entrée</th><th>Poids sortie</th><th>Rendement</th><th>Opérateur</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ep in historique" :key="ep.id">
              <td>{{ formatDate(ep.date_debut) }}</td>
              <td><strong>{{ ep.lot?.code_lot || ep.lot_id }}</strong></td>
              <td>{{ ep.poids_entree }} kg</td>
              <td>{{ ep.poids_sortie || '—' }} kg</td>
              <td>{{ ep.rendement_pourcentage ? ep.rendement_pourcentage + '%' : '—' }}</td>
              <td>{{ ep.operateur || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- FORMULAIRE -->
    <div v-else-if="activeView === 'saisie'">
      <LoadingSpinner v-if="loading" />
      <div v-else-if="lots.length === 0" class="empty anim-fade">
        <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
        <div class="empty-text">Aucun lot en attente de conditionnement</div>
      </div>

      <div v-for="lot in lots" :key="lot.id" class="card lot-card anim-fade">
        <!-- Header lot -->
        <div class="lot-header">
          <div class="lot-header-left">
            <strong class="lot-code">{{ lot.code_lot }}</strong>
            <span class="lot-fruit">{{ lot.type_fruit || lot.produit?.nom }}</span>
            <StatusBadge :status="lot.statut" />
          </div>
          <div class="lot-header-right">
            <span class="lot-recap">Production : <strong>{{ refEntree(lot) }} kg</strong></span>
            <span class="lot-recap reste">Reste : <strong>{{ resteConditionnement(lot) }} kg</strong></span>
          </div>
        </div>

        <!-- Barre de progression -->
        <div class="lot-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressConditionnement(lot) + '%' }"></div>
          </div>
          <span class="progress-label">{{ progressConditionnement(lot) }}% conditionné</span>
        </div>

        <!-- Déjà conditionné -->
        <div v-if="hasCumul(lot)" class="cumul-section">
          <div class="cumul-section-title">Déjà conditionné</div>
          <div class="flux-grid">
            <div v-for="flux in getFluxList(lot)" :key="'cum-'+flux.key" class="flux-card">
              <div class="flux-head" :style="{ borderColor: flux.color }">
                <span>{{ flux.label }}</span>
                <span class="flux-weight">{{ cumulPoidsFlux(lot, flux.key) }} kg</span>
              </div>
              <div class="flux-cumul-body">
                <span><strong>{{ getCumulCartons(lot, flux.key) }}</strong> cartons</span>
                <span><strong>{{ getCumulSachets(lot, flux.key) }}</strong> sachets</span>
                <span>{{ getPoidsSachet(lot, flux.key) }} kg/sachet</span>
              </div>
            </div>
          </div>

          <div class="cumul-total">
            <span>Total conditionné : <strong>{{ totalCumulPoids(lot) }} kg</strong></span>
            <span v-if="ecartCumul(lot) != null">Écart : <strong>{{ ecartCumul(lot) }}%</strong></span>
          </div>

          <div class="cloture-row">
            <button class="btn btn-success" :disabled="cloturing" @click="confirmClotureLot = lot">
              {{ cloturing ? 'Clôture...' : 'Clôturer le conditionnement' }}
            </button>
          </div>
        </div>

         <!-- Formulaire ajout journalier -->
         <div class="saisie-section compact">
           <div class="saisie-section-title">{{ hasCumul(lot) ? 'Ajouter la journée' : 'Premier conditionnement' }}</div>
           <div class="flux-grid">
             <div v-for="flux in getFluxList(lot)" :key="flux.key" class="flux-card">
               <div class="flux-head" :style="{ borderColor: flux.color }">
                 <span>{{ flux.label }}</span>
                 <span class="flux-weight">{{ fluxPoids(lot.id, flux.key) }} kg</span>
               </div>
               <div class="flux-inputs">
                 <div class="form-row-flux">
                   <div class="form-group">
                     <label class="input-label">Cartons</label>
                     <input type="number" v-model.number="form[lot.id][flux.key + '_cartons']" class="input input-sm compact" min="0" @input="recalc(lot.id)" />
                   </div>
                   <div class="form-group">
                     <label class="input-label">Sachets indiv.</label>
                     <input type="number" v-model.number="form[lot.id][flux.key + '_sachets']" class="input input-sm compact" min="0" @input="recalc(lot.id)" />
                   </div>
                 </div>
                 <div class="form-group">
                   <label class="input-label">Poids/sachet</label>
                   <input type="number" v-model.number="form[lot.id][flux.key + '_poids_sachet']" class="input input-sm compact" step="0.1" min="0" @input="recalc(lot.id)" />
                 </div>
               </div>
             </div>
           </div>

           <div class="bilan-bar">
             <span>Ajout : <strong>{{ totalPoids(lot.id) }} kg</strong></span>
             <span>Écart : <strong>{{ ecartVal(lot.id) ?? '—' }}%</strong></span>
           </div>

           <div class="form-row" style="margin-top:14px">
             <div class="form-group" style="flex:2">
               <label class="input-label">Responsable</label>
               <input v-model="form[lot.id].responsable" class="input compact" placeholder="Nom" />
             </div>
             <div class="form-group" style="flex:1">
               <label class="input-label">Notes</label>
               <input v-model="form[lot.id].notes" class="input compact" placeholder="Observations" />
             </div>
             <div class="form-group" style="flex:0">
               <label class="input-label">&nbsp;</label>
               <button class="btn btn-primary" :disabled="totalPoids(lot.id) <= 0 || saving" @click="enregistrer(lot)">
                 {{ saving ? '...' : 'Enreg.' }}
               </button>
             </div>
           </div>
         </div>
      </div>
    </div>

    <!-- TRANSFERT CF PANEL -->
    <div v-if="!showHistorique && transfertLots.length > 0" class="transfert-panel">
      <h2 class="transfert-title">Transfert Chambre Froide</h2>
      <div v-for="lot in transfertLots" :key="'tf-'+lot.id" class="card lot-card anim-fade tf-card">
        <div class="tf-lot-header">
          <strong class="lot-code">{{ lot.code_lot }}</strong>
          <span class="tf-summary">
            {{ lot.export_cartons || 0 }} exp · {{ lot.local_cartons || 0 }} loc ·
            {{ lot['fitini_fê_cartons'] || 0 }} fit · {{ lot.dechets_cartons || 0 }} déc ·
            {{ lot.rhum_cartons || 0 }} rhum
          </span>
        </div>

        <div class="tf-flux-grid">
          <template v-for="tf in transfertFluxes" :key="tf.key">
        <div v-if="lot[tf.cartons_field] > 0" class="tf-flux-row">
               <div class="tf-flux-head">
                 <span class="tf-flux-label">{{ tf.label }}</span>
                 <span class="tf-flux-dispo">{{ lot[tf.cartons_field] }} dispo</span>
               </div>
               <div class="tf-flux-inputs">
                 <input type="number" v-model.number="transfertForm[lot.id][tf.key + '_cartons']" class="input input-sm compact" min="0" :max="lot[tf.cartons_field]" />
                 <select v-model="transfertForm[lot.id][tf.key + '_zone_id']" class="input input-sm compact">
                   <option v-for="z in zones" :key="z.id" :value="z.id">{{ z.nom }}</option>
                 </select>
               </div>
             </div>
          </template>
        </div>

<div class="tf-footer">
           <div class="form-group"><label class="input-label">Responsable</label><input v-model="transfertForm[lot.id].responsable" class="input input-sm compact" placeholder="Nom" /></div>
           <button class="btn btn-primary btn-sm" :disabled="savingTransfert || !canTransfert(lot.id)" @click="transférer(lot)">
             {{ savingTransfert ? '...' : 'Transférer' }}
           </button>
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
import WorkflowFrame from '../components/WorkflowFrame.vue'
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

const activeView = ref('saisie')
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
function getPoidsSachet(lot, key) {
  const field = key === 'fitini_fê' ? 'fitini_fê_poids_sachet' : key + '_poids_sachet'
  return lot[field] || 2.5
}
function cumulPoidsFlux(lot, key) {
  const cartons = getCumulCartons(lot, key)
  const sachets = getCumulSachets(lot, key)
  const p = getPoidsSachet(lot, key)
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

function resteConditionnement(lot) {
  const ref = refEntree(lot)
  const cond = totalCumulPoids(lot)
  return Math.round(Math.max(0, ref - cond) * 100) / 100
}

function progressConditionnement(lot) {
  const ref = refEntree(lot)
  if (!ref) return 0
  return Math.min(100, Math.round((totalCumulPoids(lot) / ref) * 100))
}

async function load() {
  loading.value = true
  try {
    const [raw, z] = await Promise.all([getLots(), getZonesStock()])
    zones.value = z.filter(zz => zz.actif)

    const result = []
    const filtered = raw.filter(l => [EN_PRODUCTION, EN_CONDITIONNEMENT, CONDITIONNE].includes(toCanonical(l.statut)))
    for (const lot of filtered) {
      etapesData.value[lot.id] = await getProductionsEtapes(lot.id)
      const prodEtapes = etapesData.value[lot.id].filter(e => e.etape === 'production')
      if (prodEtapes.length > 0 && prodEtapes.some(e => ['termine', 'en_cours'].includes(toCanonical(e.statut)))) {
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
        refs[lot.id] = etapesData.value[lot.id].find(e => e.etape === 'conditionnement')?.poids_entree
          || prodEtapes.reduce((sum, ep) => sum + (Number(ep.poids_sortie) || 0), 0)
          || 0
        recalc(lot.id)
      }
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
.tabs {
  display: flex;
  gap: 4px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.tab {
  padding: 6px 16px;
  background: var(--surface);
  border: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  transition: all 0.2s;
}
.tab:hover { color: var(--primary); }
.tab.active {
  background: var(--primary);
  color: white;
  font-weight: 600;
}

.flow-metric { display: flex; flex-direction: column; }
.flow-metric strong { font-family: 'DM Serif Display', Georgia, serif; font-size: 25px; line-height: 0.9; color: var(--lime); }
.flow-metric span { margin-top: 4px; color: #C6D8CC; font-size: 9px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
.lot-card { margin-bottom: 20px; }
.lot-header {
  display: flex; justify-content: space-between; align-items: center;
  padding-bottom: 12px; border-bottom: 1px solid var(--border-light);
}
.lot-header-left { display: flex; align-items: center; gap: 10px; }
.lot-code { font-size: 15px; }
.lot-fruit { color: var(--text-secondary); font-size: 13px; }
.lot-header-right { display: flex; gap: 16px; font-size: 13px; color: var(--text-muted); }
.lot-recap strong { color: var(--dark); }
.lot-recap.reste strong { color: var(--primary); }

.lot-progress {
  display: flex; align-items: center; gap: 12px; padding: 12px 0;
}
.progress-bar {
  flex: 1; height: 8px; background: var(--border-light); border-radius: 4px; overflow: hidden;
}
.progress-fill {
  height: 100%; background: linear-gradient(90deg, var(--primary), var(--success));
  border-radius: 4px; transition: width 0.4s ease;
}
.progress-label { font-size: 12px; font-weight: 600; color: var(--text-secondary); white-space: nowrap; }

.cumul-section { border-top: 1px solid var(--border-light); padding-top: 14px; margin-top: 14px; }
.cumul-section-title { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px; margin-bottom: 10px; }

.flux-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 14px; }
.flux-card { border: 1px solid var(--border); border-radius: var(--radius-sm); overflow: hidden; }
.flux-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; background: var(--surface); font-size: 13px; font-weight: 600;
  border-left: 3px solid;
}
.flux-weight { font-size: 14px; font-weight: 700; color: var(--dark); }
.flux-cumul-body { padding: 10px 14px; display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--text-secondary); }
.flux-cumul-body strong { color: var(--dark); }

.cumul-total {
  display: flex; flex-wrap: wrap; gap: 12px 20px; padding: 10px 14px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: 13px; color: var(--text-secondary);
}
.cumul-total strong { color: var(--dark); }

.cloture-row { margin-top: 12px; text-align: right; }

.saisie-section { border-top: 1px solid var(--border-light); padding-top: 14px; margin-top: 14px; }
.saisie-section-title { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px; margin-bottom: 10px; }

.flux-inputs { padding: 12px 14px; display: flex; flex-direction: column; gap: 8px; }
.form-row-flux { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }

@media (max-width: 500px) { .form-row-flux { grid-template-columns: 1fr; } }

.bilan-bar {
  display: flex; align-items: center; gap: 16px; padding: 10px 14px;
  border-radius: var(--radius-sm); font-size: 12px; flex-wrap: wrap;
  background: var(--surface); color: var(--text-secondary);
}

.tf-flux-grid { display: flex; flex-direction: column; gap: 10px; padding: 0 14px 12px; }
.tf-flux-row { 
  display: flex; 
  flex-direction: column; 
  gap: 6px; 
  padding: 10px; 
  border: 1px solid var(--border-light); 
  border-radius: var(--radius-sm); 
  background: var(--surface);
}
.tf-flux-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
}
.tf-flux-label { color: var(--dark); }
.tf-flux-dispo { color: var(--text-muted); font-weight: 400; }
.tf-flux-inputs { display: flex; gap: 8px; }
.tf-flux-inputs .input-sm {
  font-size: 12px;
  padding: 4px 8px;
}
.tf-flux-inputs input { flex: 2; }
.tf-flux-inputs select { flex: 1; }
.tf-footer { display: flex; align-items: flex-end; gap: 12px; padding: 0 14px 14px; }
.tf-footer .form-group { margin-bottom: 0; }

.transfert-panel { margin-top: 24px; }
.transfert-title { font-size: 16px; font-weight: 600; margin-bottom: 12px; color: var(--dark); }
.tf-lot-header { padding: 0 14px; border-bottom: 1px solid var(--border-light); margin-bottom: 10px; }
.tf-lot-header strong { font-size: 14px; }
.tf-summary { display: block; margin-top: 4px; font-size: 11px; color: var(--text-muted); }

.input-sm {
  font-size: 12px;
  padding: 4px 8px;
}

.input-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 2px;
}

@media (max-width: 768px) { 
  .flux-grid { grid-template-columns: 1fr !important; }
  .tf-flux-inputs { flex-direction: column; }
  .tf-footer { flex-direction: column; }
}

/* Compact inputs for production flux */
.compact .input {
  min-height: 32px;
  padding: 5px 10px;
  font-size: 12px;
}
.compact .input-sm {
  min-height: 28px;
  padding: 3px 8px;
  font-size: 11px;
}
</style>
