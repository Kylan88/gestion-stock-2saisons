<template>
  <div class="page">
    <PageHeader title="Réception" subtitle="Enregistrer un nouveau lot de fruits frais">
      <template #actions>
        <button v-if="!showForm" class="btn btn-primary" @click="showForm = true; resetForm(); $nextTick(() => firstInput?.focus())">
          + Nouveau Lot
        </button>
      </template>
    </PageHeader>

    <WorkflowFrame
      :step="1"
      eyebrow="Entrée matière première"
      title="Contrôler chaque arrivée"
      description="Créez le lot, associez sa provenance puis orientez-le vers le tri en toute confiance."
    >
      <template #meta>
        <div class="flow-metric">
          <strong>{{ lots.length }}</strong>
          <span>à trier</span>
        </div>
      </template>
    </WorkflowFrame>

    <!-- Formulaire de création -->
    <div v-if="showForm" class="card anim-slide" style="margin-bottom:20px">
      <div class="card-header">
        <h3 class="card-title">Nouvelle réception</h3>
        <button class="btn btn-ghost btn-sm" @click="closeForm()" aria-label="Fermer">✕ Fermer</button>
      </div>

      <div class="form-card compact">
        <div class="form-grid">
          <!-- Colonne gauche - Identification -->
          <div class="form-col">
            <div class="form-group">
              <label>Code lot *</label>
              <input ref="firstInput" v-model="form.code_lot" class="input" placeholder="LOT-2026-XXX" />
            </div>

            <div class="form-group">
              <label>Type de fruit *</label>
              <input v-model="form.type_fruit" class="input" placeholder="Ex: Mangue Kent, Ananas, Banane..." />
            </div>

            <div class="form-group">
              <label>Fournisseur</label>
              <input v-model="form.fournisseur_nom" class="input" placeholder="Nom du fournisseur" />
            </div>
          </div>

          <!-- Colonne droite - Détails -->
          <div class="form-col">
            <div class="form-group">
              <label>Poids frais (kg) *</label>
              <input type="number" v-model.number="form.poids_frais" class="input" step="0.1" min="0" />
            </div>

            <div class="form-group">
              <label>Date réception</label>
              <input type="date" v-model="form.date_reception" class="input" />
            </div>

            <div class="form-group">
              <label>Notes</label>
              <textarea v-model="form.notes" class="input" placeholder="Observations éventuelles (qualité, dimensions...)" rows="3" />
            </div>
          </div>
        </div>

        <!-- Barre d'actions -->
        <div class="action-bar">
          <div class="action-info" v-if="form.poids_frais">
            Total estimé : <strong>{{ formatPoids(form.poids_frais) }} kg</strong>
          </div>
          <div style="display:flex;gap:10px;justify-content:flex-end">
            <button class="btn btn-ghost" @click="closeForm()">Annuler</button>
            <button class="btn btn-primary" :disabled="!canSave || saving" @click="save">
              <span v-if="saving">Enregistrement...</span>
              <span v-else>Créer le lot</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Liste des lots -->
    <LoadingSpinner v-if="loading" />
    <template v-else>
      <EmptyState v-if="lots.length === 0" text="Aucun lot réceptionné" subtext="Créez votre premier lot avec le bouton ci-dessus">
        <button v-if="!showForm" class="btn btn-outline" @click="showForm = true; resetForm(); $nextTick(() => firstInput?.focus())">
          + Nouveau Lot
        </button>
      </EmptyState>

      <div v-else class="table-wrap anim-fade">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <div style="font-size:13px;color:var(--text-muted)">
            <strong>{{ lots.length }}</strong> lot(s) en réception
          </div>
          <button v-if="!showForm" class="btn btn-outline btn-sm" @click="showForm = true; resetForm(); $nextTick(() => firstInput?.focus())">
            + Nouveau Lot
          </button>
        </div>

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
              <td>{{ lot.date_reception?.slice(0, 10) }}</td>
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
import { ref, reactive, onMounted, nextTick, computed, watch } from 'vue'
import { getLots, createLot, updateLotStatut, getFournisseurs } from '../api'
import { getProductionConfig } from '../api'
import { RECEPTION, EN_MUSSERIE } from '../utils/statuses'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import EmptyState from '../components/EmptyState.vue'
import WorkflowProgress from '../components/WorkflowProgress.vue'
import WorkflowFrame from '../components/WorkflowFrame.vue'

const lots = ref([])
const loading = ref(true)
const saving = ref(false)
const showForm = ref(false)
const toast = useToastStore()
const firstInput = ref(null)
const fournisseurs = ref([])
const fruitTypes = ref([])

const form = reactive({
  code_lot: '',
  type_fruit: '',
  fournisseur_id: '',
  fournisseur_nom: '',
  poids_frais: null,
  date_reception: '',
  notes: '',
})

const today = new Date().toISOString().split('T')[0]

const canSave = computed(() => {
  return form.code_lot.length >= 3 && form.type_fruit && form.poids_frais > 0
})

function formatPoids(kg) {
  if (!kg) return '0'
  if (kg >= 1000) return (kg / 1000).toFixed(2) + ' t'
  return kg + ' kg'
}

function resetForm() {
  form.code_lot = ''
  form.type_fruit = ''
  form.fournisseur_id = ''
  form.fournisseur_nom = ''
  form.poids_frais = null
  form.date_reception = today
  form.notes = ''
}

function closeForm() {
  showForm.value = false
  resetForm()
}

watch(showForm, (v) => {
  if (v) nextTick(() => firstInput.value?.focus())
})

async function loadConfig() {
  try {
    const cfg = await getProductionConfig()
    fruitTypes.value = cfg.fruit_types || ['Mangue', 'Ananas', 'Banane', 'Autre']
  } catch (e) {
    fruitTypes.value = ['Mangue', 'Ananas', 'Banane', 'Autre']
  }
}

async function loadFournisseurs() {
  try {
    fournisseurs.value = await getFournisseurs({ actif: true })
  } catch (e) {
    fournisseurs.value = []
  }
}

async function load() {
  loading.value = true
  try {
    lots.value = await getLots({ statut: RECEPTION })
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!form.code_lot || !form.type_fruit || !form.poids_frais) {
    toast.warning('Veuillez remplir le code lot, le type de fruit et le poids')
    return
  }
  saving.value = true
  try {
    const payload = {
      code_lot: form.code_lot,
      type_fruit: form.type_fruit,
      fournisseur_id: form.fournisseur_id || null,
      fournisseur_nom: fournisseurs.value.find(f => f.id == form.fournisseur_id)?.nom || '',
      poids_frais: form.poids_frais || 0,
      date_reception: form.date_reception ? new Date(form.date_reception).toISOString() : undefined,
      notes: form.notes,
    }
    await createLot(payload)
    toast.success('Lot créé avec succès')
    closeForm()
    await load()
  } finally {
    saving.value = false
  }
}

async function lancerMusserie(lot) {
  try {
    await updateLotStatut(lot.id, EN_MUSSERIE)
    toast.success(`${lot.code_lot} envoyé en musserie`)
    await load()
  } catch {}
}

onMounted(async () => {
  await Promise.all([loadConfig(), loadFournisseurs()])
  await load()
})
</script>

<style scoped>
.flow-metric { display: flex; flex-direction: column; }
.flow-metric strong { font-family: 'Source Serif 4', Georgia, serif; font-size: 25px; line-height: 0.9; color: var(--lime); }
.flow-metric span { margin-top: 4px; color: #C6D8CC; font-size: 9px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.form-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
  margin-top: 8px;
}

.action-info {
  font-size: 13px;
  color: var(--text-secondary);
}
.action-info strong { color: var(--dark); font-weight: 700; }

@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr !important; }
  .action-bar { flex-direction: column; gap: 12px; text-align: right; }
}
</style>