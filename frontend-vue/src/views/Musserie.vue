<template>
  <div class="page">
    <PageHeader title="Musserie & Tri" subtitle="Tri et pesée journalière des fruits — chaque saisie s'ajoute au cumul du lot">
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
        <div class="empty-text">Aucune saisie de musserie enregistrée</div>
      </div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Lot</th>
            <th>Dryer</th>
            <th>Fruits murs</th>
            <th>Dechets tri</th>
            <th>Retour non mûr</th>
            <th>Lavage</th>
            <th>Prod dechets</th>
            <th>Poids sortie</th>
            <th>Perte</th>
            <th>Rendement</th>
            <th>Opérateur</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ep in historique" :key="ep.id">
            <td>{{ formatDate(ep.date_debut) }}</td>
            <td><strong>{{ ep.lot?.code_lot || ep.lot_id }}</strong></td>
            <td>{{ ep.dryer ? 'Dryer ' + ep.dryer : '—' }}</td>
            <td>{{ ep.fruits_murs_kg }} kg</td>
            <td>{{ ep.dechets_tri_kg }} kg</td>
            <td>{{ ep.retour_non_mur_kg }} kg</td>
            <td>{{ ep.dechets_lavage_kg }} kg</td>
            <td>{{ ep.dechets_production_kg }} kg</td>
            <td>{{ ep.poids_sortie }} kg</td>
            <td>{{ ep.perte }} kg</td>
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
        <div class="empty-icon empty-no-emoji">—</div>
        <div class="empty-text">Aucun lot en attente de musserie</div>
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

        <!-- Total cumul tous dryers -->
        <div v-if="getEtapes(lot).length > 0" class="etape-section">
          <div class="cumul-row">
            <div v-for="ep in getEtapes(lot)" :key="ep.id" class="cumul-box anim-fade">
              <div class="cumul-header">Dryer {{ ep.dryer || '—' }}</div>
              <div class="cumul-details">
                <span>Traité : <strong>{{ round(ep.fruits_murs_kg) }} kg</strong></span>
                <span>→ Production : <strong>{{ round(ep.poids_sortie) }} kg</strong></span>
                <span>Tri : {{ round(ep.dechets_tri_kg) }} kg</span>
                <span>Lavage : {{ round(ep.dechets_lavage_kg) }} kg</span>
                <span>Dechets prod. : {{ round(ep.dechets_production_kg) }} kg</span>
                <span>Retour : {{ round(ep.retour_non_mur_kg) }} kg</span>
                <span v-if="ep.rendement_pourcentage" style="font-weight:600;color:var(--primary)">
                  Rendement : {{ ep.rendement_pourcentage }}%
                </span>
              </div>
            </div>
          </div>

          <div class="cumul-total">
            <span>Total traité : <strong>{{ totalCumulFruits(lot) }} kg</strong></span>
            <span>→ Production : <strong>{{ totalCumulProd(lot) }} kg</strong></span>
            <span>Perte : <strong>{{ totalCumulPerte(lot) }} kg</strong></span>
            <span v-if="totalCumulRendement(lot) != null" style="color:var(--primary)">
              Rendement : <strong>{{ totalCumulRendement(lot) }}%</strong>
            </span>
          </div>

          <div style="margin-top:12px;text-align:right">
            <button class="btn btn-success" :disabled="cloturing" @click="confirmClotureLot = lot">
              {{ cloturing ? 'Clôture...' : 'Clôturer la musserie' }}
            </button>
          </div>
        </div>

        <!-- Deux formulaires Dryer 1 / Dryer 2 côte à côte -->
        <div class="dryers-form-row">
          <div v-for="d in [1, 2]" :key="d" class="dryer-form">
            <div class="dryer-title">Dryer {{ d }}</div>

            <!-- Si cumul existant, afficher résumé + formulaire nouveau jour -->
            <div v-if="getEtapeForDryer(lot, d)" class="jour-card jour-existant">
              <div class="jour-sous" style="background:var(--success-light)">
                <div class="jour-subtitle" style="color:#166534">Déjà enregistré (cumul)</div>
                <div class="cumul-details" style="font-size:13px">
                  <span>Fruits mûrs : <strong>{{ round(getEtapeForDryer(lot, d).fruits_murs_kg) }} kg</strong></span>
                  <span>Production : <strong>{{ round(getEtapeForDryer(lot, d).poids_sortie) }} kg</strong></span>
                </div>
              </div>

              <div class="jour-sous">
                <div class="jour-subtitle">Ajouter la journée</div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Fruits mûrs (kg) *</label>
                    <input type="number" v-model.number="f[lot.id][d].fruits_murs_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                  </div>
                  <div class="form-group">
                    <label>Déchets tri (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].dechets_tri_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Retour non mûr (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].retour_non_mur_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                  </div>
                  <div class="form-group">
                    <label>Déchets lavage (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].dechets_lavage_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                  </div>
                  <div class="form-group">
                    <label>Déchets production (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].dechets_production_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group" style="flex:1">
                    <label>Reste pour demain (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].reste_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                  </div>
                  <div class="form-group" style="flex:1">
                    <label>Opérateur</label>
                    <input v-model="f[lot.id][d].operateur" class="input" placeholder="Nom" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Pas encore de cumul → formulaire complet -->
            <div v-else class="jour-card">
              <div class="form-row">
                <div class="form-group">
                  <label>Fruits mûrs (kg) *</label>
                  <input type="number" v-model.number="f[lot.id][d].fruits_murs_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                </div>
                <div class="form-group">
                  <label>Déchets tri (kg)</label>
                  <input type="number" v-model.number="f[lot.id][d].dechets_tri_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                </div>
              </div>
              <div class="jour-sous">
                <div class="jour-subtitle">Déduit des fruits mûrs</div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Retour non mûr (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].retour_non_mur_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                  </div>
                  <div class="form-group">
                    <label>Déchets lavage (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].dechets_lavage_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                  </div>
                  <div class="form-group">
                    <label>Déchets production (kg)</label>
                    <input type="number" v-model.number="f[lot.id][d].dechets_production_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                  </div>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group" style="flex:1">
                  <label>Reste pour demain (kg)</label>
                  <input type="number" v-model.number="f[lot.id][d].reste_kg" class="input" step="0.1" min="0" @input="recalc(lot.id, d)" />
                </div>
                <div class="form-group" style="flex:1">
                  <label>Opérateur</label>
                  <input v-model="f[lot.id][d].operateur" class="input" placeholder="Nom" />
                </div>
              </div>
            </div>

            <!-- Bilan du jour (calculé en temps réel) -->
            <div v-if="bilanJ[lot.id]?.[d]" class="bilan-jour">
              <div class="bilan-ligne">
                <span class="bilan-prod">→ Ajout : <strong>{{ bilanJ[lot.id][d].prod }} kg</strong></span>
                <span class="bilan-detail">= {{ bilanJ[lot.id][d].gross }} − retour {{ bilanJ[lot.id][d].retour }} − lavage {{ bilanJ[lot.id][d].lavage }}</span>
              </div>
              <div class="bilan-ligne" v-if="bilanJ[lot.id][d].reste != null">
                <span>Reste pour demain : <strong>{{ bilanJ[lot.id][d].reste }} kg</strong></span>
              </div>
            </div>

            <button class="btn btn-primary btn-sm" style="width:100%;margin-top:8px"
              :disabled="!f[lot.id][d].fruits_murs_kg || saving[d]" @click="enregistrer(lot, d)">
              {{ saving[d] ? '...' : 'Enregistrer Dryer ' + d }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :show="!!confirmClotureLot"
      title="Clôturer la musserie ?"
      :message="'Terminer la musserie pour ' + (confirmClotureLot?.code_lot || '') + ' ? Le lot passera en production. Cette action est irréversible.'"
      confirmText="Clôturer"
      variant="warning"
      @confirm="cloturer(confirmClotureLot)"
      @cancel="confirmClotureLot = null"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { getLots, getProductionsEtapes, validerMusserie, cloturerMusserie, getHistoriqueMusserie } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { toCanonical, RECEPTION, EN_MUSSERIE } from '../utils/statuses'

const lots = ref([])
const etapesData = ref({})
const loading = ref(true)
const saving = reactive({ 1: false, 2: false })
const cloturing = ref(false)
const toast = useToastStore()
const f = reactive({})
const bilanJ = reactive({})
const confirmClotureLot = ref(null)

const showHistorique = ref(false)
const historique = ref([])
const loadingHist = ref(false)

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

function recalc(lotId, dryer) {
  const d = f[lotId]?.[dryer]
  if (!d || !d.fruits_murs_kg) { if (bilanJ[lotId]) bilanJ[lotId][dryer] = null; return }
  const gross = d.fruits_murs_kg || 0
  const retour = d.retour_non_mur_kg || 0
  const lavage = d.dechets_lavage_kg || 0
  const prod = Math.max(0, gross - retour - lavage)
  const reste = d.reste_kg != null && d.reste_kg !== '' ? Number(d.reste_kg) : null
  if (!bilanJ[lotId]) bilanJ[lotId] = {}
  bilanJ[lotId][dryer] = {
    gross: round(gross), retour: round(retour), lavage: round(lavage),
    prod: round(prod), reste: reste != null ? round(reste) : null,
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
    await validerMusserie(lot.id, {
      fruits_murs_kg: f[lot.id][dryer].fruits_murs_kg,
      dechets_tri_kg: f[lot.id][dryer].dechets_tri_kg || 0,
      dechets_lavage_kg: f[lot.id][dryer].dechets_lavage_kg || 0,
      retour_non_mur_kg: f[lot.id][dryer].retour_non_mur_kg || 0,
      dechets_production_kg: f[lot.id][dryer].dechets_production_kg || 0,
      operateur: f[lot.id][dryer].operateur || '',
      dryer: dryer,
      reste_kg: f[lot.id][dryer].reste_kg != null ? f[lot.id][dryer].reste_kg : undefined,
    })
    toast.success(`Dryer ${dryer} enregistré pour ${lot.code_lot}`)
    await load()
  } finally { saving[dryer] = false }
}

async function cloturer(lot) {
  confirmClotureLot.value = null
  cloturing.value = true
  try {
    await cloturerMusserie(lot.id)
    toast.success(`Musserie clôturée pour ${lot.code_lot} — passage en production`)
    await load()
  } finally { cloturing.value = false }
}

onMounted(load)
</script>

<style scoped>
.etape-section { border-top: 1px solid var(--border-light); margin-top: 14px; padding-top: 14px; }
.cumul-row { display: flex; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }
.cumul-box { flex: 1; min-width: 280px; padding: 12px; background: var(--success-light); border-radius: var(--radius-sm); }
.cumul-header { font-weight: 600; margin-bottom: 6px; font-size: 13px; color: #166534; }
.cumul-details { display: flex; flex-wrap: wrap; gap: 8px 16px; font-size: 12px; color: #15803D; }
.cumul-total {
  display: flex; flex-wrap: wrap; gap: 12px 20px; padding: 10px 14px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: 13px; color: var(--text-secondary);
}
.dryers-form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 14px; }
.dryer-form { min-width: 0; }
.dryer-title { font-size: 14px; font-weight: 700; color: var(--dark); margin-bottom: 8px; padding-left: 2px; }
.jour-card { border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px; display: flex; flex-direction: column; gap: 10px; }
.jour-existant { border-color: var(--success); border-width: 1.5px; }
.jour-sous { background: var(--surface); border-radius: var(--radius-sm); padding: 10px; }
.jour-subtitle { font-size: 11px; font-weight: 500; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.3px; }
.bilan-jour { padding: 10px 14px; background: var(--surface); border-radius: var(--radius-sm); font-size: 12px; }
.bilan-ligne { display: flex; gap: 16px; flex-wrap: wrap; }
.bilan-detail { font-size: 11px; color: var(--text-muted); }
.bilan-prod { font-weight: 600; color: var(--primary); }
.empty-no-emoji { font-size: 28px; font-weight: 300; color: var(--border); }
@media (max-width: 768px) { .dryers-form-row { grid-template-columns: 1fr !important; } }
</style>
