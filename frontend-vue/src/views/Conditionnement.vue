<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Conditionnement</h1>
        <p class="page-subtitle">Mise en cartons — 1 carton = 6 sachets</p>
      </div>
    </div>

    <LoadingSpinner v-if="loading" />
    <div v-else-if="lots.length === 0" class="empty anim-fade">
      <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
      <div class="empty-text">Aucun lot en attente de conditionnement</div>
    </div>

    <div v-for="lot in lots" :key="lot.id" class="card anim-fade" style="margin-bottom:16px">
      <div class="card-header" style="margin-bottom:14px">
        <div style="display:flex;align-items:center;gap:10px">
          <strong>{{ lot.code_lot }}</strong>
          <span style="color:var(--text-secondary);font-size:13px">{{ lot.type_fruit || lot.produit?.nom }}</span>
          <StatusBadge :status="lot.statut" />
        </div>
        <span style="font-size:13px;color:var(--text-muted)">Réf. entrée : <strong>{{ refEntree(lot) }} kg</strong></span>
      </div>

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
        <span>Total flux : <strong>{{ totalPoids(lot.id) }} kg</strong></span>
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
          <button class="btn btn-primary" @click="valider(lot)">Valider</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLots, getProductionsEtapes, validerConditionnement } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'

const lots = ref([])
const loading = ref(true)
const form = reactive({})
const etapesData = ref({})
const refs = reactive({})
const ecarts = reactive({})
const toast = useToastStore()

const allFluxes = [
  { key: 'export', label: 'Export', color: '#14B8A6' },
  { key: 'local', label: 'Local', color: '#0F766E' },
  { key: 'dechets', label: 'Déchets', color: '#EF4444' },
  { key: 'rhum', label: 'Rhum (mangue uniquement)', color: '#D97706' },
]

function getFluxList(lot) {
  const nom = lot.type_fruit || lot.produit?.nom || ''
  const isMangue = nom.toLowerCase().includes('mangue')
  return allFluxes.filter(f => f.key !== 'rhum' || isMangue)
}

function refEntree(lot) { return refs[lot.id] ?? 0 }
function totalPoids(lotId) { return allFluxes.reduce((s, fl) => s + fluxPoids(lotId, fl.key), 0) }
function ecartVal(lotId) { return ecarts[lotId] ?? null }
function fluxPoids(lotId, key) {
  const d = form[lotId]
  if (!d) return 0
  const c = d[key + '_cartons'] || 0
  const s = d[key + '_sachets'] || 0
  const p = d[key + '_poids_sachet'] || 2.5
  return Math.round(((c * 6) + s) * p * 100) / 100
}
function recalc(lotId) {
  const ref = refs[lotId] || 0
  const total = totalPoids(lotId)
  ecarts[lotId] = ref > 0 ? Math.round(Math.abs(ref - total) / ref * 10000) / 100 : null
}

async function load() {
  loading.value = true
  try {
    const raw = await getLots()
    lots.value = raw.filter(l => ['en production', 'en conditionnement'].includes(l.statut))
    for (const lot of lots.value) {
      etapesData.value[lot.id] = await getProductionsEtapes(lot.id)
      const cond = etapesData.value[lot.id].find(e => e.etape === 'conditionnement')
      refs[lot.id] = cond?.poids_entree || 0
      form[lot.id] = reactive({
        export_cartons: 0, export_sachets: 0, export_poids_sachet: 2.5,
        local_cartons: 0, local_sachets: 0, local_poids_sachet: 2.5,
        dechets_cartons: 0, dechets_sachets: 0, dechets_poids_sachet: 2.5,
        rhum_cartons: 0, rhum_sachets: 0, rhum_poids_sachet: 2.5,
        responsable: '', notes: '',
      })
      recalc(lot.id)
    }
  } finally { loading.value = false }
}

async function valider(lot) {
  try {
    await validerConditionnement(lot.id, form[lot.id])
    toast.success(`Conditionnement validé pour ${lot.code_lot}`)
    setTimeout(() => load(), 1500)
  } catch {}
}

onMounted(load)
</script>

<style scoped>
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
}
.bilan-bar { background: var(--surface); color: var(--text-secondary); }
</style>
