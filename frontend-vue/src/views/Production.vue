<template>
  <div class="page">
     <PageHeader title="Production" subtitle="Chargement des chariots et mise au séchoir — saisie journalière cumulative">
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

    <!-- HISTORIQUE -->
    <div v-if="activeView === 'historique'" class="anim-fade">
      <LoadingSpinner v-if="loadingHist" />
      <div v-else-if="historique.length === 0" class="empty">
        <div class="empty-text">Aucune production enregistrée</div>
      </div>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Lot</th>
              <th>Poids entrée</th>
              <th>Poids sortie</th>
              <th>Rendement</th>
              <th>Dryer</th>
              <th>Chariots</th>
              <th>Opérateur</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ep in historique" :key="ep.id">
              <td>{{ formatDate(ep.date_debut) }}</td>
              <td><strong>{{ ep.lot?.code_lot || ep.lot_id }}</strong></td>
              <td>{{ ep.poids_entree }} kg</td>
              <td>{{ ep.poids_sortie || '—' }} kg</td>
              <td>{{ ep.rendement_pourcentage ? ep.rendement_pourcentage + '%' : '—' }}</td>
              <td>{{ ep.dryer ? 'D' + ep.dryer : '—' }}</td>
              <td>{{ ep.nbre_chariots || '—' }}</td>
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
        <div class="empty-text">Aucun lot en attente de production</div>
      </div>

      <div v-for="lot in lots" :key="lot.id" class="card anim-fade" style="margin-bottom:16px">
        <div class="card-header" style="margin-bottom:0">
          <div style="display:flex;align-items:center;gap:10px">
            <strong>{{ lot.code_lot }}</strong>
            <span style="color:var(--text-secondary);font-size:13px">{{ lot.type_fruit || lot.produit?.nom }}</span>
            <StatusBadge :status="lot.statut" />
          </div>
          <div style="display:flex;gap:16px;font-size:13px">
            <span style="color:var(--text-muted)">Reçu : <strong>{{ lot.poids_frais }} kg</strong></span>
            <span style="color:var(--primary)">Restant : <strong>{{ lot.quantite_restante || lot.poids_frais }} kg</strong></span>
          </div>
        </div>

        <!-- Musserie disponible pour production aujourd'hui -->
        <div v-if="musserieData[lot.id] && musserieData[lot.id].length > 0" class="musserie-available">
          <div class="musserie-available-title">Musserie du jour (à charger) :</div>
          <div class="musserie-available-grid">
            <div v-for="m in musserieData[lot.id]" :key="m.dryer" class="musserie-available-item">
              <span class="musserie-dryer">Dryer {{ m.dryer }}</span>
              <strong class="musserie-poids">{{ m.poids_sortie }} kg</strong>
            </div>
          </div>
        </div>

         <!-- Dryers déjà enregistrés -->
         <div v-if="dryers[lot.id] && dryers[lot.id].length > 0" class="cumul-section">
          <div class="cumul-section-title">Dryers enregistrés ({{ dryers[lot.id].length }})</div>
          <div class="cumul-row">
            <div v-for="d in dryers[lot.id]" :key="d.dryer" class="cumul-box">
              <div class="cumul-box-header">Dryer {{ d.dryer }}</div>
              <div class="cumul-box-body">
                <div class="cumul-stat"><span>Chariots</span><strong>{{ d.nbre_chariots }}</strong></div>
                <div class="cumul-stat"><span>Claies</span><strong>{{ d.total_claies }}</strong></div>
                <div class="cumul-stat"><span>Production</span><strong>{{ d.quantite_totale }} kg</strong></div>
              </div>
              <div class="cumul-chariots">
                <span v-for="c in d.chariots" :key="c.id" class="chariot-pill">
                  C{{ c.numero_chariot }} {{ c.heure_remplissage }}→{{ c.heure_entree_sechoir }}
                </span>
              </div>
            </div>
          </div>

          <div class="cumul-total">
            <span>Total produit : <strong>{{ totalAllDryers(lot.id) }} kg</strong></span>
            <span>Chariots : <strong>{{ totalChariots(lot.id) }}</strong></span>
            <span>Claies : <strong>{{ totalClaies(lot.id) }}</strong></span>
          </div>

          <div class="cloture-row">
            <button class="btn btn-success" :disabled="cloturing" @click="confirmClotureLot = lot">
              {{ cloturing ? 'Clôture...' : 'Clôturer la production' }}
            </button>
          </div>
        </div>

         <!-- Formulaire nouveau dryer -->
         <div class="prod-form compact">
           <div class="dryers-title" style="margin-top:12px">
             {{ dryers[lot.id] && dryers[lot.id].length > 0 ? 'Ajouter un dryer' : 'Nouveau dryer' }}
           </div>

           <!-- Dryer + configuration -->
           <div class="form-row">
             <div class="form-group">
               <label class="input-label">Dryer *</label>
               <select v-model="f[lot.id].dryer" class="input compact" @change="onDryerChange(lot.id)">
                 <option :value="1">Dryer 1 — 6 chariots, 42 claies/chariot</option>
                 <option :value="2">Dryer 2 — 12 chariots, 20 claies/chariot</option>
               </select>
             </div>
             <div class="form-group">
               <label class="input-label">Nombre de chariots *</label>
               <input type="number" v-model.number="f[lot.id].nbre_chariots" class="input compact" min="1" :max="maxChariots(lot.id)" @input="calcQté(lot.id)" />
             </div>
           </div>

          <!-- Résumé calculé -->
          <div v-if="f[lot.id].nbre_chariots && f[lot.id].dryer" class="prod-resume">
            <div class="resume-item">
              <span class="resume-label">Claies/chariot</span>
              <span class="resume-val">{{ claiesPerChariot(lot.id) }}</span>
            </div>
            <div class="resume-item">
              <span class="resume-label">Total claies</span>
              <span class="resume-val">{{ totalClaies(lot.id) }}</span>
            </div>
            <div class="resume-item">
              <span class="resume-label">Qté par claie</span>
              <span class="resume-val">{{ kgParClaie(lot.id) }} kg</span>
            </div>
            <div class="resume-item resume-total">
              <span class="resume-label">Qté totale</span>
              <span class="resume-val">{{ qtéTotale(lot.id) }} kg</span>
            </div>
          </div>

           <!-- Tableau chariots -->
           <div v-if="f[lot.id].nbre_chariots > 0" class="chariot-table">
             <div class="chariot-header">
               <span class="ch-num">N° chariot</span>
               <span class="ch-time">Heure remplissage</span>
               <span class="ch-time">Heure entrée séchoir</span>
               <span class="ch-action"></span>
             </div>
             <div v-for="i in f[lot.id].nbre_chariots" :key="i" class="chariot-row" :class="{ 'chariot-ok': f[lot.id].chariots[i-1].enregistre }">
               <span class="ch-num">{{ i }}</span>
               <input type="time" v-model="f[lot.id].chariots[i-1].heure_remplissage" class="input ch-input compact" :disabled="f[lot.id].chariots[i-1].enregistre" required />
               <input type="time" v-model="f[lot.id].chariots[i-1].heure_entree_sechoir" class="input ch-input compact" :disabled="f[lot.id].chariots[i-1].enregistre" required />
               <button v-if="!f[lot.id].chariots[i-1].enregistre" class="btn btn-sm btn-outline" :disabled="!f[lot.id].chariots[i-1].heure_remplissage || !f[lot.id].chariots[i-1].heure_entree_sechoir" @click="enregistrerChariot(lot.id, i-1)">Enreg.</button>
               <span v-else class="ch-check">OK</span>
             </div>
           </div>

           <!-- Opérateur + valider -->
           <div class="form-row" style="margin-top:14px">
             <div class="form-group" style="flex:2">
               <label class="input-label">Opérateur</label>
               <input v-model="f[lot.id].operateur" class="input compact" placeholder="Nom" />
             </div>
             <div class="form-group" style="flex:0">
               <label class="input-label">&nbsp;</label>
               <button class="btn btn-primary" :disabled="!canSubmit(lot.id) || saving" @click="enregistrer(lot)">
                 {{ saving ? 'Enregistrement...' : 'Enregistrer ce dryer' }}
               </button>
             </div>
           </div>

          <!-- Clôturer -->
          <div v-if="dryers[lot.id] && dryers[lot.id].length > 0" style="margin-top:12px;text-align:right">
            <button class="btn btn-success" :disabled="cloturing" @click="confirmClotureLot = lot">
              {{ cloturing ? 'Clôture...' : 'Clôturer la production' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :show="!!confirmClotureLot"
      title="Clôturer la production ?"
      :message="'Terminer la production pour ' + (confirmClotureLot?.code_lot || '') + ' ? Cette action est irréversible.'"
      confirmText="Clôturer"
      variant="warning"
      @confirm="cloturer(confirmClotureLot)"
      @cancel="confirmClotureLot = null"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { getLots, getProductionsEtapes, validerProduction, getDryersProduction, cloturerProduction, getHistoriqueProduction, getMusserieByDateDryer } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import PageHeader from '../components/PageHeader.vue'
import { toCanonical, EN_MUSSERIE, EN_PRODUCTION, TERMINE } from '../utils/statuses'

const DRYER = { 1: { chariots: 6, claies: 42, kg_par_claie: 6.25 }, 2: { chariots: 12, claies: 20, kg_par_claie: 6.5 } }

const showHistorique = ref(false)
const historique = ref([])
const loadingHist = ref(false)
const confirmClotureLot = ref(null)

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function loadHistorique() {
  loadingHist.value = true
  try { historique.value = await getHistoriqueProduction() } finally { loadingHist.value = false }
}

watch(showHistorique, (v) => { if (v) loadHistorique() })

const lots = ref([])
const loading = ref(true)
const saving = ref(false)
const cloturing = ref(false)
const toast = useToastStore()
const f = reactive({})
const dryers = reactive({})
const etapesData = reactive({})
const musserieData = reactive({}) // { lotId: { dryer: { date: poids_sortie } } }
const activeView = ref('saisie')

function maxChariots(lotId) { return DRYER[f[lotId]?.dryer || 1].chariots }
function claiesPerChariot(lotId) { return DRYER[f[lotId]?.dryer || 1].claies }
function kgParClaie(lotId) { return DRYER[f[lotId]?.dryer || 1].kg_par_claie }
function totalClaies(lotId) { return (f[lotId]?.nbre_chariots || 0) * claiesPerChariot(lotId) }
function qtéTotale(lotId) { return Math.round(totalClaies(lotId) * kgParClaie(lotId) * 100) / 100 }
function canSubmit(lotId) {
  const d = f[lotId]
  if (!d || !d.dryer || d.nbre_chariots <= 0) return false
  return d.chariots.every(c => c.enregistre)
}
function onDryerChange(lotId) {
  const d = f[lotId]
  d.nbre_chariots = maxChariots(lotId)
  rebuildChariots(lotId)
}
function rebuildChariots(lotId) {
  const d = f[lotId]
  const n = d.nbre_chariots || 0
  while (d.chariots.length < n) d.chariots.push({ heure_remplissage: '', heure_entree_sechoir: '', enregistre: false })
  while (d.chariots.length > n) d.chariots.pop()
}
function calcQté(lotId) { rebuildChariots(lotId) }

function enregistrerChariot(lotId, index) {
  f[lotId].chariots[index].enregistre = true
  toast.success(`Chariot ${index + 1} enregistré`)
}

function totalAllDryers(lotId) {
  if (!dryers[lotId]) return 0
  return dryers[lotId].reduce((sum, d) => sum + d.quantite_totale, 0)
}

function totalChariots(lotId) {
  if (!dryers[lotId]) return 0
  return dryers[lotId].reduce((sum, d) => sum + (d.nbre_chariots || 0), 0)
}

function getMusseriePoids(lotId, dryer) {
  const data = musserieData[lotId]
  if (!data) return 0
  const entry = data.find(m => m.dryer === dryer)
  return entry?.poids_sortie || 0
}

function initForm(lotId) {
  if (!f[lotId]) {
    const d = 1
    const n = DRYER[d].chariots
    f[lotId] = reactive({
      dryer: d, nbre_chariots: n,
      operateur: '', chariots: Array.from({ length: n }, () => ({ heure_remplissage: '', heure_entree_sechoir: '', enregistre: false })),
    })
  }
}

function resetForm(lotId) {
  if (f[lotId]) {
    const d = 1
    const n = DRYER[d].chariots
    f[lotId].dryer = d
    f[lotId].nbre_chariots = n
    f[lotId].chariots = Array.from({ length: n }, () => ({ heure_remplissage: '', heure_entree_sechoir: '', enregistre: false }))
    f[lotId].operateur = ''
  }
}

async function loadDryers(lotId) {
  const data = await getDryersProduction(lotId)
  dryers[lotId] = data
}

async function loadMusserieForToday(lotId) {
    const today = new Date().toISOString().split('T')[0]
    try {
      const data = await getMusserieByDateDryer(lotId, today)
      musserieData[lotId] = data
    } catch {
      musserieData[lotId] = []
    }
  }

  async function load() {
    loading.value = true
    try {
      const raw = await getLots()
      const filtered = raw.filter(l => [EN_MUSSERIE, EN_PRODUCTION].includes(toCanonical(l.statut)))
      const result = []
      for (const lot of filtered) {
        const etapes = await getProductionsEtapes(lot.id)
        const prodEtapes = etapes.filter(e => e.etape === 'production')
        if (prodEtapes.length > 0 && prodEtapes.every(e => toCanonical(e.statut) === TERMINE)) {
          continue
        }
        result.push(lot)
        initForm(lot.id)
        await loadDryers(lot.id)
        await loadMusserieForToday(lot.id)
      }
      lots.value = result
    } finally { loading.value = false }
  }

async function enregistrer(lot) {
  saving.value = true
  try {
    await validerProduction(lot.id, {
      dryer: f[lot.id].dryer,
      nbre_chariots: f[lot.id].nbre_chariots,
      quantite_totale: qtéTotale(lot.id),
      operateur: f[lot.id].operateur || '',
      chariots: f[lot.id].chariots.map(c => ({
        numero_chariot: f[lot.id].chariots.indexOf(c) + 1,
        heure_remplissage: c.heure_remplissage || '',
        heure_entree_sechoir: c.heure_entree_sechoir || '',
      })),
    })
    toast.success(`Dryer ${f[lot.id].dryer} enregistré`)
    resetForm(lot.id)
    await loadDryers(lot.id)
  } finally { saving.value = false }
}

async function cloturer(lot) {
  confirmClotureLot.value = null
  cloturing.value = true
  try {
    await cloturerProduction(lot.id)
    toast.success(`Production clôturée pour ${lot.code_lot}`)
    await load()
  } finally { cloturing.value = false }
}

onMounted(load)
</script>

<style scoped>
.prod-saisie { padding-top: 14px; }
.prod-resume {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 14px;
  background: var(--surface);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-light);
}
.resume-item { display: flex; flex-direction: column; gap: 2px; }
.resume-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; }
.resume-val { font-size: 14px; font-weight: 700; color: var(--dark); }
.resume-total { 
  border-left: 2px solid var(--primary); 
  padding-left: 12px; 
}
.resume-total .resume-val { color: var(--primary); }

.dryer-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 14px;
}

.input-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 4px;
}

.input-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.chariot-table { border: 1px solid var(--border); border-radius: var(--radius-sm); overflow: hidden; margin-bottom: 14px; }
.chariot-header {
  display: grid; grid-template-columns: 50px 1fr 1fr 110px;
  padding: 8px 14px; background: var(--surface); font-size: 11px;
  font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px;
}
.chariot-row {
  display: grid; grid-template-columns: 50px 1fr 1fr 110px;
  padding: 6px 14px; border-top: 1px solid var(--border-light);
  align-items: center; font-size: 13px;
}
.ch-num { font-weight: 600; color: var(--dark); }
.ch-input { font-size: 13px; }
.ch-action { display: flex; align-items: center; justify-content: center; }
.ch-check { font-weight: 700; color: var(--success); font-size: 13px; }
.chariot-ok { background: var(--success-light); }

.cumul-section { border-top: 1px solid var(--border-light); padding-top: 14px; margin-top: 14px; }
.cumul-section-title { font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px; margin-bottom: 8px; }
.cumul-row { display: flex; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }
.cumul-box { flex: 1; min-width: 200px; background: var(--success-light); border: 1px solid rgba(22,101,32,0.2); border-radius: var(--radius-sm); overflow: hidden; }
.cumul-box-header { padding: 6px 14px; font-weight: 700; font-size: 13px; color: #166534; background: rgba(22,101,32,0.08); border-bottom: 1px solid rgba(22,101,32,0.15); }
.cumul-box-body { padding: 8px 14px; display: flex; flex-direction: column; gap: 4px; }
.cumul-stat { display: flex; justify-content: space-between; font-size: 12px; }
.cumul-stat span { color: #15803D; }
.cumul-stat strong { color: #166534; }
.cumul-chariots { display: flex; flex-wrap: wrap; gap: 4px; padding: 6px 14px; }
.chariot-pill {
  font-size: 10px; padding: 2px 8px; background: white; border: 1px solid var(--success);
  border-radius: 99px; color: var(--text-muted);
}

.cumul-total {
  display: flex; flex-wrap: wrap; gap: 12px 20px; padding: 10px 14px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: 13px; color: var(--text-secondary);
}
.cumul-total strong { color: var(--dark); }

.cloture-row { margin-top: 12px; text-align: right; }

.musserie-available {
  margin-top: 12px; padding: 12px;
  background: var(--info-light); border: 1px solid var(--info); border-radius: var(--radius-sm);
}
.musserie-available-title { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--info); letter-spacing: 0.3px; margin-bottom: 8px; }
.musserie-available-grid { display: flex; gap: 16px; flex-wrap: wrap; }
.musserie-available-item { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.musserie-dryer { color: var(--text-secondary); }
.musserie-poids { color: var(--info); font-weight: 700; }

.saisie-section { border-top: 1px solid var(--border-light); padding-top: 14px; margin-top: 14px; }
.saisie-section-title { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px; margin-bottom: 10px; }

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

@media (max-width: 768px) { 
  .chariot-header, .chariot-row { grid-template-columns: 40px 1fr 1fr 80px; }
  .dryer-selector { grid-template-columns: 1fr !important; }
  .prod-resume { grid-template-columns: 1fr 1fr !important; }
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
