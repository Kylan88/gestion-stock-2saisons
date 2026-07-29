<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Production</h1>
        <p class="page-subtitle">Chargement des chariots et mise au séchoir</p>
      </div>
    </div>

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

      <div class="prod-form">
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
            <span class="resume-val">2.5 kg</span>
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
              {{ saving ? 'Enregistrement...' : 'Tout valider' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLots, getProductionsEtapes, validerProduction } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'

const DRYER = { 1: { chariots: 6, claies: 42 }, 2: { chariots: 12, claies: 20 } }
const QTÉ_PAR_CLAIE = 2.5

const lots = ref([])
const loading = ref(true)
const saving = ref(false)
const toast = useToastStore()
const f = reactive({})

function maxChariots(lotId) { return DRYER[f[lotId]?.dryer || 1].chariots }
function claiesPerChariot(lotId) { return DRYER[f[lotId]?.dryer || 1].claies }
function totalClaies(lotId) { return (f[lotId]?.nbre_chariots || 0) * claiesPerChariot(lotId) }
function qtéTotale(lotId) { return Math.round(totalClaies(lotId) * QTÉ_PAR_CLAIE * 100) / 100 }
function canSubmit(lotId) {
  const d = f[lotId]
  if (!d || !d.dryer || d.nbre_chariots <= 0) return false
  return d.chariots.every(c => c.enregistre)
}
function onDryerChange(lotId) {
  const d = f[lotId]
  if (d.nbre_chariots > maxChariots(lotId)) d.nbre_chariots = maxChariots(lotId)
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

function initForm(lotId) {
  if (!f[lotId]) {
    f[lotId] = reactive({
      dryer: 1, nbre_chariots: 1,
      operateur: '', chariots: [{ heure_remplissage: '', heure_entree_sechoir: '', enregistre: false }],
    })
  }
}

async function load() {
  loading.value = true
  try {
    const raw = await getLots()
    lots.value = raw.filter(l => l.statut === 'en production')
    for (const lot of lots.value) {
      const etapes = await getProductionsEtapes(lot.id)
      const epMusserie = etapes.find(e => e.etape === 'musserie')
      const epProd = etapes.find(e => e.etape === 'production')
      if (epProd && epProd.statut === 'terminé') continue
      initForm(lot.id)
    }
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
    toast.success(`Production validée pour ${lot.code_lot}`)
    await load()
  } finally { saving.value = false }
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
</style>
