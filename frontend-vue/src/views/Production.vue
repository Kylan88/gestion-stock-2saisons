<template>
  <div class="page">
    <PageHeader title="Production" subtitle="Chargement des chariots et mise au séchoir">
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
        <div class="empty-text">Aucune production enregistrée</div>
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
            <th>Dryer</th>
            <th>Chariots</th>
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
            <td>{{ ep.dryer || '—' }}</td>
            <td>{{ ep.nbre_chariots || '—' }}</td>
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

        <!-- Dryers déjà enregistrés -->
        <div v-if="dryers[lot.id] && dryers[lot.id].length > 0" class="dryers-list">
          <div class="dryers-title">Dryers enregistrés ({{ dryers[lot.id].length }})</div>
          <div v-for="d in dryers[lot.id]" :key="d.dryer" class="dryer-entry">
            <div class="dryer-header">
              <span class="dryer-badge">Dryer {{ d.dryer }}</span>
              <span class="dryer-info">{{ d.nbre_chariots }} chariots — {{ d.total_claies }} claies — {{ d.quantite_totale }} kg</span>
            </div>
            <div class="dryer-chariots">
              <span v-for="c in d.chariots" :key="c.id" class="dryer-chariot-pill">
                C{{ c.numero_chariot }} {{ c.heure_remplissage }}→{{ c.heure_entree_sechoir }}
              </span>
            </div>
          </div>
          <div class="dryers-total">
            <strong>Total : {{ totalAllDryers(lot.id) }} kg</strong>
          </div>
        </div>

        <!-- Formulaire nouveau dryer -->
        <div class="prod-form">
          <div class="dryers-title" style="margin-top:12px">
            {{ dryers[lot.id] && dryers[lot.id].length > 0 ? 'Ajouter un dryer' : 'Nouveau dryer' }}
          </div>

          <!-- Dryer + configuration -->
          <div class="form-row">
            <div class="form-group">
              <label>Dryer *</label>
              <select v-model="f[lot.id].dryer" class="input" @change="onDryerChange(lot.id)">
                <option :value="1">Dryer 1 — 6 chariots, 42 claies/chariot</option>
                <option :value="2">Dryer 2 — 12 chariots, 20 claies/chariot</option>
              </select>
            </div>
            <div class="form-group">
              <label>Nombre de chariots *</label>
              <input type="number" v-model.number="f[lot.id].nbre_chariots" class="input" min="1" :max="maxChariots(lot.id)" @input="calcQté(lot.id)" />
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
              <input type="time" v-model="f[lot.id].chariots[i-1].heure_remplissage" class="input ch-input" :disabled="f[lot.id].chariots[i-1].enregistre" required />
              <input type="time" v-model="f[lot.id].chariots[i-1].heure_entree_sechoir" class="input ch-input" :disabled="f[lot.id].chariots[i-1].enregistre" required />
              <button v-if="!f[lot.id].chariots[i-1].enregistre" class="btn btn-sm btn-outline" :disabled="!f[lot.id].chariots[i-1].heure_remplissage || !f[lot.id].chariots[i-1].heure_entree_sechoir" @click="enregistrerChariot(lot.id, i-1)">Enregistrer</button>
              <span v-else class="ch-check">OK</span>
            </div>
          </div>

          <!-- Opérateur + valider -->
          <div class="form-row" style="margin-top:14px">
            <div class="form-group" style="flex:2">
              <label>Opérateur</label>
              <input v-model="f[lot.id].operateur" class="input" placeholder="Nom" />
            </div>
            <div class="form-group" style="flex:0">
              <label>&nbsp;</label>
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
import { getLots, getProductionsEtapes, validerProduction, getDryersProduction, cloturerProduction, getHistoriqueProduction } from '../api'
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

async function load() {
  loading.value = true
  try {
    const raw = await getLots()
    const filtered = raw.filter(l => [EN_MUSSERIE, EN_PRODUCTION].includes(toCanonical(l.statut)))
    const result = []
    for (const lot of filtered) {
      const etapes = await getProductionsEtapes(lot.id)
      const epProd = etapes.find(e => e.etape === 'production')
      if (epProd && toCanonical(epProd.statut) === TERMINE) {
        continue
      }
      result.push(lot)
      initForm(lot.id)
      await loadDryers(lot.id)
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
.prod-form { padding-top: 14px; }
.prod-resume {
  display: flex; gap: 16px; padding: 12px 16px; margin-bottom: 14px;
  background: var(--surface); border-radius: var(--radius-sm); flex-wrap: wrap;
}
.resume-item { display: flex; flex-direction: column; gap: 2px; }
.resume-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; }
.resume-val { font-size: 16px; font-weight: 700; color: var(--dark); }
.resume-highlight { color: var(--primary); }
.resume-total { border-left: 2px solid var(--primary); padding-left: 12px; }
.chariot-table { border: 1px solid var(--border); border-radius: var(--radius-sm); overflow: hidden; margin-bottom: 14px; }
.chariot-header {
  display: grid; grid-template-columns: 80px 1fr 1fr;
  padding: 8px 14px; background: var(--surface); font-size: 11px;
  font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px;
}
.chariot-row {
  display: grid; grid-template-columns: 80px 1fr 1fr;
  padding: 6px 14px; border-top: 1px solid var(--border-light);
  align-items: center; font-size: 13px;
}
.ch-num { font-weight: 600; color: var(--dark); }
.ch-input { font-size: 13px; }
.ch-action { width: 100px; text-align: center; }
.ch-check { font-weight: 700; color: var(--success); font-size: 13px; }
.chariot-ok { background: var(--success-light); }

.dryers-list { padding: 14px 0 0; }
.dryers-title { font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px; margin-bottom: 8px; }
.dryer-entry { padding: 10px 14px; background: var(--success-light); border: 1px solid var(--success); border-radius: var(--radius-sm); margin-bottom: 8px; }
.dryer-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.dryer-badge { font-weight: 700; color: var(--success); font-size: 13px; }
.dryer-info { font-size: 13px; color: var(--text-muted); }
.dryer-chariots { display: flex; flex-wrap: wrap; gap: 6px; }
.dryer-chariot-pill {
  font-size: 11px; padding: 2px 8px; background: white; border: 1px solid var(--success);
  border-radius: 99px; color: var(--text-muted);
}
.dryers-total { text-align: right; font-size: 14px; color: var(--primary); padding: 4px 0; }
@media (max-width: 768px) { .chariot-grid { grid-template-columns: 1fr !important; } .dryer-chariots { gap: 4px; } }
</style>
