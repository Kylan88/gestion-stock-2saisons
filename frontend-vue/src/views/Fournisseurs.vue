<template>
  <div class="page">
    <PageHeader title="Fournisseurs" subtitle="Gestion des fournisseurs">
      <template #actions>
        <button v-if="!showForm" class="btn btn-primary" @click="openCreate">+ Nouveau</button>
      </template>
    </PageHeader>

    <LoadingSpinner v-if="loading" />
    <template v-else>
      <div v-if="showForm" class="card anim-slide" style="margin-bottom:20px">
        <div class="card-header">
          <h3>{{ editingId ? 'Modifier le fournisseur' : 'Nouveau fournisseur' }}</h3>
          <button class="btn btn-ghost btn-sm" @click="showForm = false; resetForm()">✕</button>
        </div>
        <div class="form-card">
          <div class="form-row">
            <div class="form-group">
              <label>Nom *</label>
              <input ref="firstInput" v-model="form.nom" class="input" :class="{ 'input-error': errors.nom }" />
              <span v-if="errors.nom" class="field-error">{{ errors.nom }}</span>
            </div>
            <div class="form-group"><label>Contact</label><input v-model="form.contact" class="input" /></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>Téléphone</label><input v-model="form.telephone" class="input" /></div>
            <div class="form-group"><label>Email</label><input v-model="form.email" class="input" type="email" /></div>
          </div>
          <div class="form-group"><label>Adresse</label><input v-model="form.adresse" class="input" /></div>
          <div style="display:flex;gap:10px">
            <button class="btn btn-primary" :disabled="saving" @click="save">{{ saving ? '...' : (editingId ? 'Mettre à jour' : 'Créer') }}</button>
            <button class="btn btn-ghost" @click="showForm = false; resetForm()">Annuler</button>
          </div>
        </div>
      </div>

      <EmptyState v-if="filteredFournisseurs.length === 0" :text="recherche ? 'Aucun résultat' : 'Aucun fournisseur'" />

      <div v-else>
        <div class="filters">
          <input v-model="recherche" class="input" placeholder="Rechercher un fournisseur..." style="max-width:260px" />
        </div>
        <div class="table-wrap anim-fade">
          <table>
            <thead><tr><th>Nom</th><th>Contact</th><th>Téléphone</th><th>Email</th><th>Statut</th><th></th></tr></thead>
            <tbody>
              <tr v-for="f in paginatedFournisseurs" :key="f.id">
                <td><strong>{{ f.nom }}</strong></td>
                <td>{{ f.contact || '—' }}</td>
                <td>{{ f.telephone || '—' }}</td>
                <td>{{ f.email || '—' }}</td>
                <td><StatusBadge :status="f.actif ? 'disponible' : 'périmé'" /></td>
                <td>
                  <button class="btn btn-ghost btn-sm" @click="openEdit(f)" aria-label="Modifier le fournisseur">✎</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="totalPages > 1" class="pagination">
          <button class="btn btn-ghost btn-sm" :disabled="page === 1" @click="page--">←</button>
          <span class="page-info">{{ page }} / {{ totalPages }}</span>
          <button class="btn btn-ghost btn-sm" :disabled="page === totalPages" @click="page++">→</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { getFournisseurs, createFournisseur, updateFournisseur } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import EmptyState from '../components/EmptyState.vue'

const fournisseurs = ref([])
const loading = ref(true)
const saving = ref(false)
const showForm = ref(false)
const editingId = ref(null)
const recherche = ref('')
const page = ref(1)
const pageSize = 15
const toast = useToastStore()
const firstInput = ref(null)
const errors = reactive({ nom: '' })

const form = reactive({ nom: '', contact: '', telephone: '', email: '', adresse: '' })

function resetForm() {
  Object.assign(form, { nom: '', contact: '', telephone: '', email: '', adresse: '' })
  editingId.value = null
  errors.nom = ''
}

function openCreate() {
  resetForm()
  showForm.value = true
  nextTick(() => firstInput.value?.focus())
}

function openEdit(f) {
  editingId.value = f.id
  Object.assign(form, { nom: f.nom, contact: f.contact || '', telephone: f.telephone || '', email: f.email || '', adresse: f.adresse || '' })
  showForm.value = true
  nextTick(() => firstInput.value?.focus())
}

const filteredFournisseurs = computed(() => {
  if (!recherche.value) return fournisseurs.value
  const q = recherche.value.toLowerCase()
  return fournisseurs.value.filter(f => f.nom.toLowerCase().includes(q) || f.contact?.toLowerCase().includes(q))
})
const totalPages = computed(() => Math.ceil(filteredFournisseurs.value.length / pageSize))
const paginatedFournisseurs = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredFournisseurs.value.slice(start, start + pageSize)
})

async function load() {
  loading.value = true
  try { fournisseurs.value = await getFournisseurs() } finally { loading.value = false }
}

function validate() {
  errors.nom = form.nom ? '' : 'Le nom est requis'
  return !errors.nom
}

async function save() {
  if (!validate()) { toast.warning('Veuillez corriger les erreurs'); return }
  saving.value = true
  try {
    if (editingId.value) {
      await updateFournisseur(editingId.value, form)
      toast.success('Fournisseur mis à jour')
    } else {
      await createFournisseur(form)
      toast.success('Fournisseur créé')
    }
    showForm.value = false; resetForm(); await load()
  } finally { saving.value = false }
}

onMounted(load)
</script>

<style scoped>
.pagination { display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 16px; }
.page-info { font-size: 13px; color: var(--text-secondary); }
.input-error { border-color: var(--error) !important; }
.field-error { font-size: 11px; color: var(--error); margin-top: 3px; }
</style>
