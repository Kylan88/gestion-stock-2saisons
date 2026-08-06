<template>
  <div class="page">
    <PageHeader title="Réception" subtitle="Enregistrer un nouveau lot de fruits frais">
      <template #actions>
        <button v-if="!showForm" class="btn btn-primary" @click="showForm = true">+ Nouveau Lot</button>
      </template>
    </PageHeader>

    <LoadingSpinner v-if="loading" />
    <template v-else>
      <!-- Formulaire -->
      <div v-if="showForm" class="card anim-slide" style="margin-bottom:20px">
        <div class="card-header">
          <h3>Nouvelle réception</h3>
          <button class="btn btn-ghost btn-sm" @click="showForm = false; resetForm()" aria-label="Fermer">✕ Fermer</button>
        </div>
        <div class="form-card">
          <div class="form-row">
            <div class="form-group">
              <label>Code lot *</label>
              <input ref="firstInput" v-model="form.code_lot" class="input" placeholder="LOT-2026-XXX" />
            </div>
            <div class="form-group">
              <label>Type de fruit *</label>
              <select v-model="form.type_fruit" class="input">
                <option value="">Sélectionner...</option>
                <option>Mangue Kent</option>
                <option>Mangue Brooks</option>
                <option>Banane</option>
                <option>Ananas</option>
                <option>Autre</option>
              </select>
            </div>
            <div class="form-group">
              <label>Fournisseur</label>
              <input v-model="form.fournisseur_nom" class="input" placeholder="Nom du fournisseur" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Poids frais (kg) *</label>
              <input type="number" v-model.number="form.poids_frais" class="input" step="0.1" min="0" />
            </div>
            <div class="form-group">
              <label>Date réception</label>
              <input type="date" v-model="form.date_reception" class="input" />
            </div>
          </div>
          <div class="form-group">
            <label>Notes</label>
            <input v-model="form.notes" class="input" placeholder="Observations éventuelles" />
          </div>
          <div style="display:flex;gap:10px">
            <button class="btn btn-primary" :disabled="saving" @click="save">
              {{ saving ? 'Enregistrement...' : 'Enregistrer le lot' }}
            </button>
            <button class="btn btn-ghost" @click="showForm = false; resetForm()">Annuler</button>
          </div>
        </div>
      </div>

      <!-- Liste -->
      <EmptyState v-if="lots.length === 0" text="Aucun lot réceptionné" subtext="Créez votre premier lot avec le bouton ci-dessus" />

      <div v-else class="table-wrap anim-fade">
        <table>
          <thead>
            <tr>
              <th>Code Lot</th>
              <th>Produit</th>
              <th>Fournisseur</th>
              <th>Poids</th>
              <th>Date</th>
              <th>Statut</th>
              <th>Workflow</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lot in lots" :key="lot.id">
              <td><strong>{{ lot.code_lot }}</strong></td>
              <td>{{ lot.type_fruit || lot.produit?.nom || '—' }}</td>
              <td>{{ lot.fournisseur_nom || lot.fournisseur?.nom || '—' }}</td>
              <td>{{ lot.poids_frais }} kg</td>
              <td>{{ lot.date_reception?.slice(0,10) }}</td>
              <td><StatusBadge :status="lot.statut" /></td>
              <td style="min-width:260px"><WorkflowProgress :statut="lot.statut" /></td>
              <td>
                <button class="btn btn-sm btn-primary" @click="lancerMusserie(lot)">→ Musserie</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { getLots, createLot, updateLotStatut } from '../api'
import { RECEPTION, EN_MUSSERIE } from '../utils/statuses'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import EmptyState from '../components/EmptyState.vue'
import WorkflowProgress from '../components/WorkflowProgress.vue'

const lots = ref([])
const loading = ref(true)
const saving = ref(false)
const showForm = ref(false)
const toast = useToastStore()
const firstInput = ref(null)

const form = reactive({
  code_lot: '', type_fruit: '', fournisseur_nom: '', poids_frais: null,
  date_reception: '', notes: '',
})

function resetForm() {
  form.code_lot = ''; form.type_fruit = ''; form.fournisseur_nom = ''
  form.poids_frais = null; form.date_reception = ''; form.notes = ''
}

watch(showForm, (v) => { if (v) nextTick(() => firstInput.value?.focus()) })

async function load() {
  loading.value = true
  try {
  lots.value = await getLots({ statut: RECEPTION })
  } finally { loading.value = false }
}

async function save() {
  if (!form.code_lot || !form.type_fruit) {
    toast.warning('Veuillez remplir le code lot et le type de fruit'); return
  }
  saving.value = true
  try {
    await createLot({
      code_lot: form.code_lot,
      type_fruit: form.type_fruit,
      fournisseur_nom: form.fournisseur_nom,
      poids_frais: form.poids_frais || 0,
      date_reception: form.date_reception ? new Date(form.date_reception).toISOString() : undefined,
      notes: form.notes,
    })
    toast.success('Lot créé avec succès')
    showForm.value = false; resetForm(); await load()
  } finally { saving.value = false }
}

async function lancerMusserie(lot) {
  try {
    await updateLotStatut(lot.id, EN_MUSSERIE)
    toast.success(`${lot.code_lot} envoyé en musserie`)
    await load()
  } catch {}
}

onMounted(load)
</script>
