<template>
  <div class="page">
    <PageHeader title="Musserie & Tri" subtitle="Tri et pesée journalière des fruits — chaque saisie s'ajoute au cumul du lot">
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
      :step="2"
      eyebrow="Préparation & tri"
      title="Valoriser chaque kilogramme"
      description="Suivez les pertes, le retour non mûr et le rendement de chaque dryer au fil des journées."
    >
      <template #meta><div class="flow-metric"><strong>{{ lots.length }}</strong><span>lots actifs</span></div></template>
    </WorkflowFrame>

    <div v-if="activeView === 'historique'" class="anim-fade" key="historique">
      <LoadingSpinner v-if="loadingHist" />
      <div v-if="!loadingHist && historique.length === 0" class="empty">
        <div class="empty-text">Aucune saisie de musserie enregistrée</div>
      </div>
      <div v-if="!loadingHist && historique.length > 0" class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Date</th><th>Lot</th><th>Dryer</th><th>Fruits mûrs</th><th>Tri</th>
              <th>Lavage</th><th>Déchets prod.</th><th>Retour</th><th>Poids sortie</th><th>Rendement</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ep in historique" :key="ep.id">
              <td>{{ formatDate(ep.date_debut) }}</td>
              <td><strong>{{ ep.lot?.code_lot || ep.lot_id }}</strong></td>
              <td>{{ ep.dryer ? 'D' + ep.dryer : '—' }}</td>
              <td>{{ ep.fruits_murs_kg }}</td>
              <td>{{ ep.dechets_tri_kg }}</td>
              <td>{{ ep.dechets_lavage_kg }}</td>
              <td>{{ ep.dechets_production_kg }}</td>
              <td>{{ ep.retour_non_mur_kg }}</td>
              <td>{{ ep.poids_sortie }}</td>
              <td>{{ ep.rendement_pourcentage ? ep.rendement_pourcentage + '%' : '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="anim-fade" key="saisie">
      <LoadingSpinner v-if="loading" />
      <div v-if="lots.length === 0" class="empty anim-fade">
        <div class="empty-icon empty-no-emoji">—</div>
        <div class="empty-text">Aucun lot en attente de musserie</div>
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
            <span class="lot-recap"><strong>{{ lot.poids_frais }}</strong> kg reçu</span>
            <span class="lot-recap reste">Reste : <strong>{{ resteATraiter(lot) }} kg</strong></span>
          </div>
        </div>

        <!-- Barre de progression -->
        <div class="lot-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressMusserie(lot) + '%' }"></div>
          </div>
          <span class="progress-label">{{ progressMusserie(lot) }}% traité</span>
        </div>

        <!-- Cumul enregistré -->
        <div v-if="getEtapes(lot).length > 0" class="cumul-section">
          <div class="cumul-section-title">Déjà enregistré</div>
          <div class="cumul-row">
            <div v-for="ep in getEtapes(lot)" :key="ep.id" class="cumul-box">
              <div class="cumul-box-header">Dryer {{ ep.dryer || '—' }}</div>
              <div class="cumul-box-body">
                <div class="cumul-stat"><span>Fruits mûrs</span><strong>{{ round(ep.fruits_murs_kg) }} kg</strong></div>
                <div class="cumul-stat"><span>Tri</span><strong>{{ round(ep.dechets_tri_kg) }} kg</strong></div>
                <div class="cumul-stat"><span>Lavage</span><strong>{{ round(ep.dechets_lavage_kg) }} kg</strong></div>
                <div class="cumul-stat"><span>Déchets prod.</span><strong>{{ round(ep.dechets_production_kg) }} kg</strong></div>
                <div class="cumul-stat"><span>Retour non mûr</span><strong>{{ round(ep.retour_non_mur_kg) }} kg</strong></div>
              </div>
              <div class="cumul-box-footer">
                <span>→ Sortie : <strong>{{ round(ep.poids_sortie) }} kg</strong></span>
                <span v-if="ep.rendement_pourcentage" class="badge-rendement">{{ ep.rendement_pourcentage }}%</span>
              </div>
            </div>
          </div>

          <!-- Total cumulé -->
          <div class="cumul-total">
            <span>Total traité : <strong>{{ totalCumulFruits(lot) }} kg</strong></span>
            <span>→ Production : <strong>{{ totalCumulProd(lot) }} kg</strong></span>
            <span>Perte : <strong>{{ totalCumulPerte(lot) }} kg</strong></span>
            <span v-if="totalCumulRendement(lot) != null" class="rendement-val">Rendement : <strong>{{ totalCumulRendement(lot) }}%</strong></span>
          </div>

          <div class="cloture-row">
            <button class="btn btn-success" :disabled="cloturing || !canCloturerJour(lot)" @click="cloturerJour(lot)">
              {{ cloturing ? 'Clôture...' : 'Clôturer aujourd\'hui' }}
            </button>
          </div>
        </div>

        <!-- Résumé calculé en temps réel -->
        <div v-if="getEtapes(lot).length > 0" class="resume-section">
          <div class="resume-section-title">Résumé de la saisie</div>
          <div class="resume-grid">
            <div class="resume-item">
              <span class="resume-label">Fruits mûrs aujourd'hui</span>
              <strong class="resume-value">{{ sumFruitsMursJour(lot) }} kg</strong>
            </div>
            <div class="resume-item">
              <span class="resume-label">Pertes totales aujourd'hui</span>
              <strong class="resume-value text-error">{{ sumPertesJour(lot) }} kg</strong>
            </div>
            <div class="resume-item">
              <span class="resume-label">Production estimée</span>
              <strong class="resume-value text-success">{{ round(sumFruitsMursJour(lot) - sumPertesJour(lot)) }} kg</strong>
            </div>
            <div class="resume-item">
              <span class="resume-label">Reste pour demain</span>
              <strong class="resume-value text-warning">{{ sumResteJour(lot) }} kg</strong>
            </div>
          </div>
        </div>

        <!-- Formulaire de saisie unifié -->
        <div class="saisie-section">
          <div class="saisie-section-title">{{ getEtapes(lot).length > 0 ? 'Ajouter la journée' : 'Première saisie' }}</div>

          <div class="dryers-form-row compact">
            <div v-for="d in [1, 2]" :key="d" class="dryer-form">
              <div class="dryer-title">Dryer {{ d }}</div>

              <!-- Fruits mûrs -->
              <div class="form-group">
                <label class="input-label">Fruits mûrs *</label>
                <input type="number" v-model.number="f[lot.id][d].fruits_murs_kg" class="input compact" step="0.1" min="0" @input="onInput(lot.id, d)" />
              </div>

              <!-- Pertes groupées -->
              <div class="form-group">
                <div class="pertes-grid">
                  <div class="perte-item">
                    <label class="input-label">Tri (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].dechets_tri_kg" class="input input-sm compact" step="0.1" min="0" @input="onInput(lot.id, d)" />
                  </div>
                  <div class="perte-item">
                    <label class="input-label">Lavage (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].dechets_lavage_kg" class="input input-sm compact" step="0.1" min="0" @input="onInput(lot.id, d)" />
                  </div>
                  <div class="perte-item">
                    <label class="input-label">Déchets prod. (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].dechets_production_kg" class="input input-sm compact" step="0.1" min="0" @input="onInput(lot.id, d)" />
                  </div>
                </div>
              </div>

              <!-- Retour non mûr -->
              <div class="form-group">
                <label class="input-label">Retour non mûr (kg)</label>
                <input type="number" v-model.number="f[lot.id][d].retour_non_mur_kg" class="input compact" step="0.1" min="0" @input="onInput(lot.id, d)" />
              </div>

              <!-- Reste et opérateur -->
              <div class="form-row">
                <div class="form-group" style="flex:1">
                  <label class="input-label">Reste demain (kg)</label>
                  <input type="number" v-model.number="f[lot.id][d].reste_kg" class="input compact" step="0.1" min="0" @input="onInput(lot.id, d)" />
                </div>
                <div class="form-group" style="flex:1">
                  <label class="input-label">Opérateur</label>
                  <input v-model="f[lot.id][d].operateur" class="input compact" placeholder="Nom" />
                </div>
              </div>

              <!-- Bilan calculé du dryer -->
              <div v-if="bilanJ[lot.id]?.[d]" class="bilan-jour">
                <div class="bilan-line">
                  <span class="bilan-prod">Production : <strong>{{ round(bilanJ[lot.id][d].prod) }} kg</strong></span>
                  <span class="bilan-detail">= {{ bilanJ[lot.id][d].gross }} − {{ bilanJ[lot.id][d].retour }} − {{ bilanJ[lot.id][d].lavage }} − {{ bilanJ[lot.id][d].dechets_prod }}</span>
                </div>
                <div class="bilan-line" v-if="bilanJ[lot.id][d].reste != null">
                  <span>Reste : <strong>{{ bilanJ[lot.id][d].reste }} kg</strong></span>
                </div>
              </div>

              <button class="btn btn-primary btn-sm" style="width:100%;margin-top:8px"
                :disabled="!f[lot.id][d].fruits_murs_kg || saving[d]" @click="enregistrer(lot, d)">
{{ saving[d] ? '...' : 'Enreg.' }}
</button>
              </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { getLots, getProductionsEtapes, validerMusserie, cloturerMusserie, getHistoriqueMusserie } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import WorkflowFrame from '../components/WorkflowFrame.vue'
import { toCanonical, RECEPTION, EN_MUSSERIE, TERMINE } from '../utils/statuses'

const lots = ref([])
const etapesData = ref({})
const loading = ref(true)
const saving = reactive({ 1: false, 2: false })
const cloturing = ref(false)
const toast = useToastStore()
const f = reactive({})
const bilanJ = reactive({})

const showHistorique = ref(false)
const historique = ref([])
const loadingHist = ref(false)
const activeView = ref('saisie')

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function loadHistorique() {
  loadingHist.value = true
  try { historique.value = await getHistoriqueMusserie() } finally { loadingHist.value = false }
}

watch(showHistorique, (v) => { if (v) loadHistorique() })

function round(v) { return Math.round((v || 0) * 100) / 100 }

function getEtapes(lot) {
  return (etapesData.value[lot.id] || []).filter(e => e.etape === 'musserie')
}

function getEtapeForDryer(lot, dryer) {
  return getEtapes(lot).find(e => e.dryer === dryer) || null
}

function todayLocal() {
  const d = new Date()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

function canCloturerJour(lot) {
  const today = todayLocal()
  return getEtapes(lot).some(e =>
    e.date_debut && String(e.date_debut).slice(0, 10) === today && toCanonical(e.statut) !== TERMINE
  )
}

function totalCumulFruits(lot) {
  return round(getEtapes(lot).reduce((s, e) => s + (e.fruits_murs_kg || 0), 0))
}
function totalCumulProd(lot) {
  return round(getEtapes(lot).reduce((s, e) => s + (e.poids_sortie || 0), 0))
}
function totalCumulPerte(lot) {
  return round(getEtapes(lot).reduce((s, e) => s + (e.perte || 0), 0))
}
function totalCumulRendement(lot) {
  const eps = getEtapes(lot)
  if (!eps.length) return null
  const totalFM = eps.reduce((s, e) => s + (e.fruits_murs_kg || 0), 0)
  const totalPS = eps.reduce((s, e) => s + (e.poids_sortie || 0), 0)
  return totalFM > 0 ? Math.round((totalPS / totalFM) * 1000) / 10 : null
}

function progressMusserie(lot) {
  if (!lot.poids_frais) return 0
  return Math.min(100, Math.round((totalCumulFruits(lot) / lot.poids_frais) * 100))
}

function resteATraiter(lot) {
  return round(Math.max(0, (lot.poids_frais || 0) - totalCumulFruits(lot)))
}

// Fonctions pour le résumé de saisie en temps réel
function sumFruitsMursJour(lot) {
  let total = 0
  for (let d = 1; d <= 2; d++) {
    if (f[lot.id]?.[d]?.fruits_murs_kg) {
      total += Number(f[lot.id][d].fruits_murs_kg)
    }
  }
  return round(total)
}

function sumPertesJour(lot) {
  let total = 0
  for (let d = 1; d <= 2; d++) {
    const fd = f[lot.id]?.[d]
    if (fd) {
      total += Number(fd.dechets_tri_kg || 0) + Number(fd.dechets_lavage_kg || 0) + Number(fd.dechets_production_kg || 0)
    }
  }
  return round(total)
}

function sumResteJour(lot) {
  let total = 0
  for (let d = 1; d <= 2; d++) {
    if (f[lot.id]?.[d]?.reste_kg != null && f[lot.id][d].reste_kg !== '') {
      total += Number(f[lot.id][d].reste_kg)
    }
  }
  return round(total)
}

function onInput(lotId, dryer) {
  recalc(lotId, dryer)
}

function recalc(lotId, dryer) {
  const d = f[lotId]?.[dryer]
  if (!d || !d.fruits_murs_kg) { if (bilanJ[lotId]) bilanJ[lotId][dryer] = null; return }
  const gross = d.fruits_murs_kg || 0
  const retour = d.retour_non_mur_kg || 0
  const lavage = d.dechets_lavage_kg || 0
  const dechets_prod = d.dechets_production_kg || 0
  const prod = Math.max(0, gross - retour - lavage - dechets_prod)
  const reste = d.reste_kg != null && d.reste_kg !== '' ? Number(d.reste_kg) : null
  if (!bilanJ[lotId]) bilanJ[lotId] = {}
  bilanJ[lotId][dryer] = {
    gross: round(gross), retour: round(retour), lavage: round(lavage),
    dechets_prod: round(dechets_prod), prod: round(prod), reste: reste != null ? round(reste) : null,
  }
}

function initForm(lotId, dryer) {
  if (!f[lotId]) f[lotId] = {}
  if (!f[lotId][dryer]) {
    f[lotId][dryer] = reactive({
      fruits_murs_kg: null, dechets_tri_kg: 0, dechets_lavage_kg: 0,
      retour_non_mur_kg: 0, dechets_production_kg: 0, reste_kg: null, operateur: '',
    })
  }
}

function recalcAll(lotId) {
  recalc(lotId, 1)
  recalc(lotId, 2)
}

async function load() {
  loading.value = true
  try {
    const raw = await getLots()
    const filtered = raw.filter(l => [RECEPTION, EN_MUSSERIE].includes(toCanonical(l.statut)))
    for (const lot of filtered) {
      etapesData.value[lot.id] = await getProductionsEtapes(lot.id)
      initForm(lot.id, 1)
      initForm(lot.id, 2)
      recalcAll(lot.id)
    }
    lots.value = filtered
  } finally { loading.value = false }
}

async function enregistrer(lot, dryer) {
  saving[dryer] = true
  try {
    const reste = f[lot.id][dryer].reste_kg
    await validerMusserie(lot.id, {
      fruits_murs_kg: Number(f[lot.id][dryer].fruits_murs_kg) || 0,
      dechets_tri_kg: Number(f[lot.id][dryer].dechets_tri_kg) || 0,
      dechets_lavage_kg: Number(f[lot.id][dryer].dechets_lavage_kg) || 0,
      retour_non_mur_kg: Number(f[lot.id][dryer].retour_non_mur_kg) || 0,
      dechets_production_kg: Number(f[lot.id][dryer].dechets_production_kg) || 0,
      operateur: f[lot.id][dryer].operateur || '',
      dryer: dryer,
      reste_kg: reste === '' || reste == null ? null : Number(reste),
    })
    toast.success(`Dryer ${dryer} enregistré pour ${lot.code_lot}`)
    await load()
  } catch (e) {
    const msg = e.response?.data?.detail || e.message
    toast.error(typeof msg === 'string' ? msg : 'Erreur lors de l\'enregistrement')
  } finally { saving[dryer] = false }
}

async function cloturerJour(lot) {
  cloturing.value = true
  try {
    const today = todayLocal()
    const res = await cloturerMusserie(lot.id, today)
    if (res?.lot?.statut?.includes('production')) {
      toast.success(`Musserie clôturée pour ${lot.code_lot} — passage en production`)
    } else {
      toast.success(`Journée musserie clôturée pour ${lot.code_lot} — lot reste en musserie`)
    }
    await load()
  } catch (e) {
    const msg = e.response?.data?.detail || e.message
    toast.error(msg)
  } finally { cloturing.value = false }
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

/* Progress bar */
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

/* Cumul section */
.cumul-section { border-top: 1px solid var(--border-light); padding-top: 14px; margin-top: 14px; }
.cumul-section-title { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px; margin-bottom: 10px; }
.cumul-row { display: flex; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }
.cumul-box { flex: 1; min-width: 280px; background: var(--success-light); border: 1px solid rgba(22,101,32,0.2); border-radius: var(--radius-sm); overflow: hidden; }
.cumul-box-header { padding: 8px 14px; font-weight: 700; font-size: 13px; color: #166534; background: rgba(22,101,32,0.08); border-bottom: 1px solid rgba(22,101,32,0.15); }
.cumul-box-body { padding: 10px 14px; display: flex; flex-direction: column; gap: 6px; }
.cumul-stat { display: flex; justify-content: space-between; font-size: 12px; }
.cumul-stat span { color: #15803D; }
.cumul-stat strong { color: #166534; }
.cumul-box-footer { padding: 8px 14px; border-top: 1px solid rgba(22,101,32,0.15); display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #166534; }
.badge-rendement { background: var(--primary); color: white; padding: 2px 8px; border-radius: 99px; font-size: 11px; font-weight: 700; }

.cumul-total {
  display: flex; flex-wrap: wrap; gap: 12px 20px; padding: 10px 14px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: 13px; color: var(--text-secondary);
}
.cumul-total strong { color: var(--dark); }
.rendement-val { color: var(--primary); }
.rendement-val strong { color: var(--primary); }

.cloture-row { margin-top: 12px; text-align: right; }

/* Resume section */
.resume-section { border-top: 2px solid var(--primary); padding: 10px; margin-top: 14px; background: var(--surface); border-radius: var(--radius); }
.resume-section-title { font-size: 10px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px; margin-bottom: 8px; }
.resume-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.resume-item { display: flex; flex-direction: column; gap: 2px; padding: 6px; background: var(--surface); border-radius: var(--radius-sm); border: 1px solid var(--border-light); }
.resume-label { font-size: 9px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; }
.resume-value { font-size: 13px; font-weight: 700; }
.resume-value.text-error { color: #DC2626; }
.resume-value.text-success { color: #166534; }
.resume-value.text-warning { color: #D97706; }

/* Saisie section */
.saisie-section { border-top: 1px solid var(--border-light); padding-top: 12px; margin-top: 12px; }
.saisie-section-title { font-size: 10px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px; margin-bottom: 8px; }
.dryers-form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.dryer-form { min-width: 0; padding: 10px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); }
.dryer-title { font-size: 12px; font-weight: 600; color: var(--dark); margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid var(--border-light); }
.form-group { margin-bottom: 10px; }
.form-group label, .input-label { display: block; font-size: 10px; font-weight: 500; color: var(--text-muted); margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.3px; }
.bilan-jour { padding: 8px 10px; background: var(--surface); border: 1px solid var(--border-light); border-radius: var(--radius-sm); font-size: 11px; margin-top: 8px; }
.bilan-line { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.bilan-detail { font-size: 10px; color: var(--text-muted); }
.bilan-prod { font-weight: 600; color: var(--primary); }
.empty-no-emoji { font-size: 28px; font-weight: 300; color: var(--border); }

.table-wrap { overflow-x: auto; }

@media (max-width: 768px) { .dryers-form-row { grid-template-columns: 1fr !important; } }

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
