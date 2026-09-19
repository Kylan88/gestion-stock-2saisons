<template>
  <div class="page">
    <PageHeader title="Reconditionnement" subtitle="Transformer des cartons en sachets de 100g">
      <template #actions>
        <div class="tabs">
          <button class="tab" :class="{ active: activeView === 'saisie' }" @click="activeView = 'saisie'">Saisie</button>
          <button class="tab" :class="{ active: activeView === 'historique' }" @click="activeView = 'historique'; loadHistorique()">Historique</button>
        </div>
      </template>
    </PageHeader>

    <div v-if="activeView === 'historique'" class="anim-fade" key="historique">
      <LoadingSpinner v-if="loadingHist" />
      <div v-if="!loadingHist && historique.length === 0" class="empty">
        <div class="empty-text">Aucun reconditionnement enregistré</div>
      </div>
      <div v-if="!loadingHist && historique.length > 0" class="table-wrap">
        <table class="table">
          <thead><tr><th>Date</th><th>Lot</th><th>Source</th><th>Cartons</th><th>Sachets</th><th>Déchet kg</th></tr></thead>
          <tbody>
            <tr v-for="r in historique" :key="r.id">
              <td>{{ formatDateHist(r.date_reconditionnement) }}</td>
              <td><strong>{{ lotCode(r.lot_id) }}</strong></td>
              <td>{{ r.type_source }}</td>
              <td>{{ r.nb_cartons_entree }}</td>
              <td>{{ fmt(r.nb_sachets_100g_sortie) }}</td>
              <td>{{ fmt(r.dechet_kg ?? 0) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="anim-fade" key="saisie">
    <LoadingSpinner v-if="loading" />
    <div v-else-if="lots.length === 0" class="empty anim-fade">
      <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
      <div class="empty-text">Aucun lot avec cartons disponibles</div>
    </div>

    <div v-for="lot in lots" :key="lot.id" class="card anim-fade" style="margin-bottom:16px">
      <div class="card-header" style="margin-bottom:14px">
        <div style="display:flex;align-items:center;gap:10px">
          <strong>{{ lot.code_lot }}</strong>
          <span style="color:var(--text-secondary);font-size:13px">{{ lot.type_fruit || lot.produit?.nom }}</span>
        </div>
      </div>

      <div class="recond-grid">
        <div v-if="lot.local_cartons > 0" class="recond-card">
          <div class="recond-head" style="border-left-color:#0F766E">
            <span>Local</span>
            <span class="recond-avail">{{ lot.local_cartons }} cartons · Stock {{ stockInitial(lot.id,'local') }} sachets</span>
          </div>
          <div class="recond-body">
            <div class="form-row">
              <div class="form-group" style="flex:1">
                <label>Cartons à transformer</label>
                <input type="number" v-model.number="form[lot.id].local" class="input" min="0" :max="lot.local_cartons" />
              </div>
              <div class="form-group" style="flex:1">
                <label>Déchet (kg)</label>
                <input type="number" v-model.number="form[lot.id].local_dechet" class="input" step="0.1" min="0" placeholder="0" />
              </div>
              <div class="form-group" style="flex:1">
                <label>Sortis — réellement obtenus</label>
                <input type="number" v-model.number="form[lot.id].local_sortis" class="input" min="0" placeholder="Ex : 142 (1 carton ≠ toujours 150)" />
              </div>
            </div>
            <div class="recond-result">
              <span>Estimation : <strong>{{ resultRecond(form[lot.id].local || 0, lot.local_poids_sachet) }}</strong> sachets</span>
              <span>En stock : <strong>{{ stockFinal(lot.id,'local', lot.local_poids_sachet) }}</strong> sachets</span>
            </div>
            <div class="form-row" style="margin-top:8px">
              <div class="form-group" style="flex:1">
                <label>Rhum arrangé obtenu (cartons)</label>
                <input type="number" v-model.number="form[lot.id].local_rhum" class="input" min="0" placeholder="0" />
              </div>
              <div class="form-group" style="flex:1">
                <label>Rhum arrangé (sachets vrac)</label>
                <input type="number" v-model.number="form[lot.id].local_rhum_sachets" class="input" min="0" placeholder="0" />
              </div>
              <div class="form-group" style="flex:1">
                <label>Rhum en vrac (kg)</label>
                <input type="number" v-model.number="form[lot.id].local_rhum_vrac" class="input" step="0.1" min="0" placeholder="ex. 1,2" />
              </div>
            </div>
          </div>
        </div>

        <div v-if="lot.fitini_fe_cartons > 0" class="recond-card">
          <div class="recond-head" style="border-left-color:#8B5CF6">
            <span>Fitini Fê</span>
            <span class="recond-avail">{{ lot.fitini_fe_cartons }} cartons · Stock {{ stockInitial(lot.id,'fitini_fe') }} sachets</span>
          </div>
          <div class="recond-body">
            <div class="form-row">
              <div class="form-group" style="flex:1">
                <label>Cartons à transformer</label>
                <input type="number" v-model.number="form[lot.id].fitini" class="input" min="0" :max="lot.fitini_fe_cartons" />
              </div>
              <div class="form-group" style="flex:1">
                <label>Déchet (kg)</label>
                <input type="number" v-model.number="form[lot.id].fitini_dechet" class="input" step="0.1" min="0" placeholder="0" />
              </div>
              <div class="form-group" style="flex:1">
                <label>Sortis — réellement obtenus</label>
                <input type="number" v-model.number="form[lot.id].fitini_sortis" class="input" min="0" placeholder="Ex : 142 (1 carton ≠ toujours 150)" />
              </div>
            </div>
            <div class="recond-result">
              <span>Estimation : <strong>{{ resultRecond(form[lot.id].fitini || 0, lot.fitini_fe_poids_sachet) }}</strong> sachets</span>
              <span>En stock : <strong>{{ stockFinal(lot.id,'fitini_fe', lot.fitini_fe_poids_sachet) }}</strong> sachets</span>
            </div>
            <div class="form-row" style="margin-top:8px">
              <div class="form-group" style="flex:1">
                <label>Rhum arrangé obtenu (cartons)</label>
                <input type="number" v-model.number="form[lot.id].fitini_rhum" class="input" min="0" placeholder="0" />
              </div>
              <div class="form-group" style="flex:1">
                <label>Rhum arrangé (sachets vrac)</label>
                <input type="number" v-model.number="form[lot.id].fitini_rhum_sachets" class="input" min="0" placeholder="0" />
              </div>
              <div class="form-group" style="flex:1">
                <label>Rhum en vrac (kg)</label>
                <input type="number" v-model.number="form[lot.id].fitini_rhum_vrac" class="input" step="0.1" min="0" placeholder="ex. 1,2" />
              </div>
            </div>
          </div>
        </div>

        <div v-if="lot.local_cartons === 0 && lot.fitini_fe_cartons === 0" class="no-flux">
          Aucun carton disponible pour le reconditionnement
        </div>
      </div>

      <div v-if="lot.local_cartons > 0 || lot.fitini_fe_cartons > 0" class="form-row" style="margin-top:14px">
        <div class="form-group" style="flex:1">
          <label>Responsable</label>
          <input v-model="form[lot.id].responsable" class="input" placeholder="Nom" />
        </div>
        <div class="form-group" style="flex:1">
          <label>Chambre (rhum obtenu)</label>
          <select v-model="form[lot.id].zone_id" class="input">
            <option :value="null">Défaut (1re froide)</option>
            <option v-for="z in zones" :key="z.id" :value="z.id">{{ z.nom }}</option>
          </select>
        </div>
        <div class="form-group" style="flex:0">
          <label>&nbsp;</label>
          <button class="btn btn-primary" :disabled="!canSubmit(lot.id) || saving" @click="valider(lot)">
            {{ saving ? 'Reconditionnement...' : 'Reconditionner' }}
          </button>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLots, creerReconditionnement, getReconditionnements, getStock, getZonesStock } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import PageHeader from '../components/PageHeader.vue'
import { toCanonical, CONDITIONNE, EN_STOCK, EN_MUSSERIE, EN_PRODUCTION, EN_CONDITIONNEMENT } from '../utils/statuses'

const lots = ref([])
const historique = ref([])
const loading = ref(true)
const loadingHist = ref(false)
const activeView = ref('saisie')
const saving = ref(false)
const toast = useToastStore()
const form = reactive({})
const stocks = ref({})
const zones = ref([])

function fmt(v) { const n = Number(v); return Number.isFinite(n) ? n.toFixed(2) : '—' }
function resultRecond(cartons, poidsSachet) {
  return cartons * 6 * Math.round(poidsSachet / 0.1)
}
function formatDateHist(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
async function loadHistorique() {
  loadingHist.value = true
  try { historique.value = await getReconditionnements() } finally { loadingHist.value = false }
}
function lotCode(lotId) {
  return lots.value.find(l => Number(l.id) === Number(lotId))?.code_lot || ('Lot #' + lotId)
}
function stockInitial(lotId, type) {
  const key = lotId + '_' + type
  return stocks.value[key] ?? 0
}
function stockFinal(lotId, type, poidsSachet) {
  const d = form[lotId]
  if (!d) return stockInitial(lotId, type)
  const dechet = type === 'local' ? (d.local_dechet || 0) : (d.fitini_dechet || 0)
  const sortis = type === 'local' ? (d.local_sortis || 0) : (d.fitini_sortis || 0)
  const dechetSachets = Math.round(dechet / 0.1)
  return Math.max(0, stockInitial(lotId, type) + sortis - dechetSachets)
}
function calcRecond(lotId) {}

function canSubmit(lotId) {
  const d = form[lotId]
  if (!d) return false
  return (d.local > 0 || d.fitini > 0)
}

async function load() {
  loading.value = true
  try {
    const raw = await getLots()
    // Flux continu : tout lot avec des cartons local/fitini_fe, quel que soit
    // son statut (le backend contrôle les dispos, sans filtre statut).
    lots.value = raw.filter(l => [EN_MUSSERIE, EN_PRODUCTION, EN_CONDITIONNEMENT, CONDITIONNE, EN_STOCK].includes(toCanonical(l.statut)) && (l.local_cartons > 0 || l.fitini_fe_cartons > 0))
    try {
      const z = await getZonesStock()
      zones.value = (z || []).filter(zz => zz.actif)
    } catch { zones.value = [] }
    const defZone = (zones.value.find(zz => zz.type_zone === 'froid') || zones.value[0])?.id ?? null
    for (const lot of lots.value) {
      form[lot.id] = reactive({ local: 0, local_dechet: 0, local_sortis: 0, local_rhum: 0, local_rhum_sachets: 0, local_rhum_vrac: 0, fitini: 0, fitini_dechet: 0, fitini_sortis: 0, fitini_rhum: 0, fitini_rhum_sachets: 0, fitini_rhum_vrac: 0, zone_id: defZone, responsable: '' })
    }
    // Vrai stock de sachets 100g par lot (issu de la chambre froide, auto + manuel)
    try {
      const st = await getStock()
      for (const s of (st || [])) {
        if (!s.lot_id || !(s.sachets > 0)) continue
        const pname = s.produit?.nom || ''
        const type = pname === 'Sachet 100g local' ? 'local' : pname === 'Sachet 100g fitini_fe' ? 'fitini_fe' : null
        if (!type) continue
        const k = s.lot_id + '_' + type
        stocks.value[k] = (stocks.value[k] || 0) + s.sachets
      }
    } catch {}
    if (activeView.value === 'historique') await loadHistorique()
  } finally { loading.value = false }
}

async function valider(lot) {
  saving.value = true
  try {
    const d = form[lot.id]
    if (d.local > 0) {
      const res = await creerReconditionnement({ lot_id: lot.id, type_source: 'local', nb_cartons_entree: d.local, dechet_kg: d.local_dechet || 0, nb_sachets_sortis: d.local_sortis || 0, rhum_cartons_sortie: d.local_rhum || 0, rhum_sachets_sortis: d.local_rhum_sachets || 0, rhum_poids_vrac_kg: d.local_rhum_vrac || 0, zone_id: d.zone_id ?? null, responsable: d.responsable })
      toast.success(`Reconditionnement local créé : ${resultRecond(d.local, lot.local_poids_sachet)} sachets` + rhumMsg(res?.rhum))
    }
    if (d.fitini > 0) {
      const res = await creerReconditionnement({ lot_id: lot.id, type_source: 'fitini_fe', nb_cartons_entree: d.fitini, dechet_kg: d.fitini_dechet || 0, nb_sachets_sortis: d.fitini_sortis || 0, rhum_cartons_sortie: d.fitini_rhum || 0, rhum_sachets_sortis: d.fitini_rhum_sachets || 0, rhum_poids_vrac_kg: d.fitini_rhum_vrac || 0, zone_id: d.zone_id ?? null, responsable: d.responsable })
      toast.success(`Reconditionnement fitini fê créé : ${resultRecond(d.fitini, lot.fitini_fe_poids_sachet)} sachets` + rhumMsg(res?.rhum))
    }
    await load()
  } finally { saving.value = false }
}
function rhumMsg(rhum) {
  if (rhum?.alimente) {
    const vrac = rhum.vrac_kg ? ` + ${rhum.vrac_kg} kg vrac` : ''
    return ` — rhum +${rhum.cartons || 0} cartons / ${rhum.sachets || 0} sachets${vrac} (${rhum.zone})`
  }
  return ''
}

onMounted(load)
</script>

<style scoped>
.tabs { display:flex; gap:4px; border:1px solid var(--border); border-radius:var(--radius-sm); overflow:hidden; }
.tab { padding:6px 16px; background:var(--surface); border:none; cursor:pointer; font-size:13px; font-weight:500; color:var(--text-muted); transition:all 0.2s; }
.tab:hover { color:var(--primary); }
.tab.active { background:var(--primary); color:white; font-weight:600; }
.table-wrap { overflow-x:auto; }
.recond-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 14px; }
.recond-card { border: 1px solid var(--border); border-radius: var(--radius-sm); overflow: hidden; }
.recond-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; background: var(--surface); font-size: 13px; font-weight: 600;
  border-left: 3px solid;
}
.recond-avail { font-size: 12px; color: var(--text-muted); }
.recond-body { padding: 12px 14px; }
.recond-result { display: flex; gap: 16px; font-size: 12px; color: var(--text-muted); margin-top: 8px; }
.no-flux { padding: 12px; text-align: center; color: var(--text-muted); font-size: 13px; grid-column: 1 / -1; }
</style>
