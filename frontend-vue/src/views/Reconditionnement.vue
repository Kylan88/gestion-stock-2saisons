<template>
  <div class="page">
    <PageHeader title="Reconditionnement" subtitle="Transformer des cartons en sachets de 100g" />

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
            <span class="recond-avail">{{ lot.local_cartons }} cartons</span>
          </div>
          <div class="recond-body">
            <div class="form-group">
              <label>Cartons à transformer</label>
              <input type="number" v-model.number="form[lot.id].local" class="input" min="0" :max="lot.local_cartons" @input="calcRecond(lot.id)" />
            </div>
            <div class="recond-result">
              <span>Sachets 100g obtenus : <strong>{{ resultRecond(form[lot.id].local || 0, lot.local_poids_sachet) }}</strong></span>
              <span>Poids total : <strong>{{ ((resultRecond(form[lot.id].local || 0, lot.local_poids_sachet) * 0.1)).toFixed(1) }} kg</strong></span>
            </div>
          </div>
        </div>

        <div v-if="lot.fitini_fê_cartons > 0" class="recond-card">
          <div class="recond-head" style="border-left-color:#8B5CF6">
            <span>Fitini Fê</span>
            <span class="recond-avail">{{ lot.fitini_fê_cartons }} cartons</span>
          </div>
          <div class="recond-body">
            <div class="form-group">
              <label>Cartons à transformer</label>
              <input type="number" v-model.number="form[lot.id].fitini" class="input" min="0" :max="lot.fitini_fê_cartons" @input="calcRecond(lot.id)" />
            </div>
            <div class="recond-result">
              <span>Sachets 100g obtenus : <strong>{{ resultRecond(form[lot.id].fitini || 0, lot.fitini_fê_poids_sachet) }}</strong></span>
              <span>Poids total : <strong>{{ ((resultRecond(form[lot.id].fitini || 0, lot.fitini_fê_poids_sachet) * 0.1)).toFixed(1) }} kg</strong></span>
            </div>
          </div>
        </div>

        <div v-if="lot.local_cartons === 0 && lot.fitini_fê_cartons === 0" class="no-flux">
          Aucun carton disponible pour le reconditionnement
        </div>
      </div>

      <div v-if="lot.local_cartons > 0 || lot.fitini_fê_cartons > 0" class="form-row" style="margin-top:14px">
        <div class="form-group" style="flex:1">
          <label>Responsable</label>
          <input v-model="form[lot.id].responsable" class="input" placeholder="Nom" />
        </div>
        <div class="form-group" style="flex:0">
          <label>&nbsp;</label>
          <button class="btn btn-primary" :disabled="!canSubmit(lot.id) || saving" @click="valider(lot)">
            {{ saving ? 'Création...' : 'Créer le reconditionnement' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="historique.length > 0" style="margin-top:24px">
      <h2 style="font-size:16px;font-weight:600;margin-bottom:12px">Historique</h2>
      <table class="table">
        <thead><tr><th>Date</th><th>Lot</th><th>Source</th><th>Cartons</th><th>Sachets 100g</th><th>Poids</th></tr></thead>
        <tbody>
          <tr v-for="r in historique" :key="r.id">
            <td>{{ new Date(r.date_reconditionnement).toLocaleDateString() }}</td>
            <td>{{ r.lot_id }}</td>
            <td>{{ r.type_source }}</td>
            <td>{{ r.nb_cartons_entree }}</td>
            <td>{{ r.nb_sachets_100g_sortie }}</td>
            <td>{{ (r.nb_sachets_100g_sortie * 0.1).toFixed(1) }} kg</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLots, creerReconditionnement, getReconditionnements } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import PageHeader from '../components/PageHeader.vue'

const lots = ref([])
const historique = ref([])
const loading = ref(true)
const saving = ref(false)
const toast = useToastStore()
const form = reactive({})

function resultRecond(cartons, poidsSachet) {
  return cartons * 6 * Math.round(poidsSachet / 0.1)
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
    lots.value = raw.filter(l => l.statut === 'terminé' && (l.local_cartons > 0 || l.fitini_fê_cartons > 0))
    for (const lot of lots.value) {
      form[lot.id] = reactive({ local: 0, fitini: 0, responsable: '' })
    }
    historique.value = await getReconditionnements()
  } finally { loading.value = false }
}

async function valider(lot) {
  saving.value = true
  try {
    const d = form[lot.id]
    if (d.local > 0) {
      await creerReconditionnement({ lot_id: lot.id, type_source: 'local', nb_cartons_entree: d.local, responsable: d.responsable })
      toast.success(`Reconditionnement local créé : ${resultRecond(d.local, lot.local_poids_sachet)} sachets 100g`)
    }
    if (d.fitini > 0) {
      await creerReconditionnement({ lot_id: lot.id, type_source: 'fitini_fê', nb_cartons_entree: d.fitini, responsable: d.responsable })
      toast.success(`Reconditionnement fitini fê créé : ${resultRecond(d.fitini, lot.fitini_fê_poids_sachet)} sachets 100g`)
    }
    await load()
  } finally { saving.value = false }
}

onMounted(load)
</script>

<style scoped>
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
