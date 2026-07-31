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

        <div v-if="getEtape(lot)" class="etape-section">
          <!-- Cumul déjà saisi -->
          <div v-if="getEtape(lot).fruits_murs_kg > 0" class="cumul-box anim-fade">
            <div class="cumul-header">Cumul des sessions sur ce lot</div>
            <div class="cumul-details">
              <span>Total traite : <strong>{{ round(getEtape(lot).fruits_murs_kg) }} kg</strong></span>
              <span>Parti en production : <strong>{{ round(getEtape(lot).poids_sortie) }} kg</strong></span>
              <span>Tri : {{ round(getEtape(lot).dechets_tri_kg) }} kg</span>
              <span>Lavage : {{ round(getEtape(lot).dechets_lavage_kg) }} kg</span>
              <span>Dechets prod. : {{ round(getEtape(lot).dechets_production_kg) }} kg</span>
              <span>Retour non mur : {{ round(getEtape(lot).retour_non_mur_kg) }} kg</span>
              <span v-if="getEtape(lot).rendement_pourcentage" style="font-weight:600;color:var(--primary)">
                Rendement : {{ getEtape(lot).rendement_pourcentage }}%
              </span>
            </div>
          </div>

          <!-- Saisie du jour -->
          <div class="form-card">
            <div class="jour-card">
              <div class="jour-label">Poids total manipulé du jour <strong>↓</strong></div>
              <div class="form-row">
                <div class="form-group">
                  <label>Fruits mûrs du jour (kg) *</label>
                  <input type="number" v-model.number="f[lot.id].fruits_murs_kg" class="input" step="0.1" min="0" @input="recalc(lot.id)" />
                </div>
                <div class="form-group">
                  <label>Déchets tri (kg)</label>
                  <input type="number" v-model.number="f[lot.id].dechets_tri_kg" class="input" step="0.1" min="0" @input="recalc(lot.id)" />
                </div>
              </div>
              <div class="jour-sous">
                <div class="jour-subtitle">Déduit des fruits mûrs du jour</div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Retour non mûr (kg)</label>
                    <input type="number" v-model.number="f[lot.id].retour_non_mur_kg" class="input" step="0.1" min="0" @input="recalc(lot.id)" />
                  </div>
                  <div class="form-group">
                    <label>Déchets lavage (kg)</label>
                    <input type="number" v-model.number="f[lot.id].dechets_lavage_kg" class="input" step="0.1" min="0" @input="recalc(lot.id)" />
                  </div>
                  <div class="form-group">
                    <label>Déchets production (kg)</label>
                    <input type="number" v-model.number="f[lot.id].dechets_production_kg" class="input" step="0.1" min="0" @input="recalc(lot.id)" />
                  </div>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Opérateur</label>
                  <input v-model="f[lot.id].operateur" class="input" placeholder="Nom" />
                </div>
              </div>
            </div>

            <!-- Bilan du jour -->
            <div v-if="bilanJ[lot.id]" class="bilan-jour">
              <div class="bilan-ligne">
                <span class="bilan-prod">Part en production : <strong>{{ bilanJ[lot.id].prod }} kg</strong></span>
                <span class="bilan-detail">= {{ bilanJ[lot.id].gross }} &minus; retour {{ bilanJ[lot.id].retour }} &minus; lavage {{ bilanJ[lot.id].lavage }} &minus; prod {{ bilanJ[lot.id].prodDechet }}</span>
              </div>
              <div class="bilan-ligne">
                <span>Retire du lot : <strong>{{ bilanJ[lot.id].brut }} kg</strong></span>
                <span>&minus; Retour non mur : <strong>{{ bilanJ[lot.id].retour }} kg</strong></span>
                <span class="bilan-net">Retrait net : <strong>{{ bilanJ[lot.id].retire }} kg</strong></span>
                <span class="bilan-restant">Restant : <strong>{{ bilanJ[lot.id].nouveauRestant }} kg</strong></span>
              </div>
            </div>

            <button class="btn btn-primary" :disabled="!f[lot.id].fruits_murs_kg || saving" @click="enregistrer(lot)">
              {{ saving ? 'Enregistrement...' : 'Enregistrer la journée' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { getLots, getProductionsEtapes, validerMusserie, getHistoriqueMusserie } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'

const lots = ref([])
const etapesData = ref({})
const loading = ref(true)
const saving = ref(false)
const toast = useToastStore()
const f = reactive({})
const bilanJ = reactive({})

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

function getEtape(lot) {
  return etapesData.value[lot.id]?.find(e => e.etape === 'musserie')
}

function recalc(lotId) {
  const d = f[lotId]
  if (!d || !d.fruits_murs_kg) { bilanJ[lotId] = null; return }
  const gross = d.fruits_murs_kg || 0
  const retour = d.retour_non_mur_kg || 0
  const lavage = d.dechets_lavage_kg || 0
  const prodDechet = d.dechets_production_kg || 0
  const tri = d.dechets_tri_kg || 0
  const prod = Math.max(0, gross - retour - lavage - prodDechet)
  const brut = gross + tri
  const retire = brut - retour
  const lot = lots.value.find(l => l.id === lotId)
  const restant = (lot?.quantite_restante ?? lot?.poids_frais ?? 0)
  bilanJ[lotId] = {
    gross: round(gross), retour: round(retour), lavage: round(lavage),
    prodDechet: round(prodDechet), tri: round(tri),
    prod: round(prod), brut: round(brut), retire: round(retire),
    nouveauRestant: round(restant - retire),
  }
}

function initForm(lotId, lot) {
  if (!f[lotId]) {
    f[lotId] = reactive({
      fruits_murs_kg: null, dechets_tri_kg: 0, dechets_lavage_kg: 0,
      retour_non_mur_kg: 0, dechets_production_kg: 0, operateur: '',
    })
  }
}

async function load() {
  loading.value = true
  try {
    const raw = await getLots()
    lots.value = raw.filter(l => ['réception', 'en musserie'].includes(l.statut))
    for (const lot of lots.value) {
      etapesData.value[lot.id] = await getProductionsEtapes(lot.id)
      initForm(lot.id, lot)
    }
  } finally { loading.value = false }
}

async function enregistrer(lot) {
  saving.value = true
  try {
    await validerMusserie(lot.id, {
      fruits_murs_kg: f[lot.id].fruits_murs_kg,
      dechets_tri_kg: f[lot.id].dechets_tri_kg || 0,
      dechets_lavage_kg: f[lot.id].dechets_lavage_kg || 0,
      retour_non_mur_kg: f[lot.id].retour_non_mur_kg || 0,
      dechets_production_kg: f[lot.id].dechets_production_kg || 0,
      operateur: f[lot.id].operateur || '',
    })
    toast.success(`Session musserie enregistrée pour ${lot.code_lot}`)
    await load()
  } finally { saving.value = false }
}

onMounted(load)
</script>

<style scoped>
.etape-section { border-top: 1px solid var(--border-light); margin-top: 14px; padding-top: 14px; }
.cumul-box { padding: 12px; background: var(--success-light); border-radius: var(--radius-sm); margin-bottom: 14px; }
.cumul-header { font-weight: 600; margin-bottom: 6px; font-size: 13px; color: #166534; }
.cumul-details { display: flex; flex-wrap: wrap; gap: 8px 16px; font-size: 12px; color: #15803D; }
.bilan-jour { padding: 10px 14px; background: var(--surface); border-radius: var(--radius-sm); font-size: 12px; margin-bottom: 12px; }
.bilan-ligne { display: flex; gap: 16px; flex-wrap: wrap; }
.jour-card { border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px; margin-bottom: 14px; }
.jour-label { font-size: 13px; font-weight: 600; margin-bottom: 10px; color: var(--dark); }
.jour-sous { background: var(--surface); border-radius: var(--radius-sm); padding: 10px; margin-bottom: 10px; }
.jour-subtitle { font-size: 11px; font-weight: 500; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.3px; }
.empty-no-emoji { font-size: 28px; font-weight: 300; color: var(--border); }
.bilan-detail { font-size: 11px; color: var(--text-muted); }
.bilan-prod { font-weight: 600; color: var(--primary); }
.bilan-net { font-weight: 600; color: var(--accent); }
.bilan-restant { font-weight: 700; color: var(--dark); }
</style>
