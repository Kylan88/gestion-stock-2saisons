<template>
  <div class="page">
    <PageHeader title="Produits" subtitle="Catalogue des produits">
      <template #actions>
        <button v-if="!showForm" class="btn btn-primary" @click="openCreate">+ Nouveau</button>
      </template>
    </PageHeader>

    <LoadingSpinner v-if="loading" />
    <template v-else>
      <div v-if="showForm" class="card anim-slide" style="margin-bottom:20px">
        <div class="card-header">
          <h3>{{ editingId ? 'Modifier le produit' : 'Nouveau produit' }}</h3>
          <button class="btn btn-ghost btn-sm" @click="showForm = false; resetForm()">✕</button>
        </div>
        <div class="form-card">
          <div class="form-row">
            <div class="form-group">
              <label>Nom *</label>
              <input ref="firstInput" v-model="form.nom" class="input" :class="{ 'input-error': errors.nom }" />
              <span v-if="errors.nom" class="field-error">{{ errors.nom }}</span>
            </div>
            <div class="form-group">
              <label>Catégorie</label>
              <select v-model="form.categorie_id" class="input">
                <option value="">Sélectionner...</option>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.nom }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Unité</label>
              <input v-model="form.unite_mesure" class="input" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Stock min</label>
              <input type="number" v-model.number="form.stock_min" class="input" step="0.1" min="0" />
            </div>
            <div class="form-group">
              <label>Stock actuel</label>
              <input type="number" v-model.number="form.stock_actuel" class="input" step="0.1" min="0" />
            </div>
            <div class="form-group">
              <label>Prix unitaire (FCFA)</label>
              <input type="number" v-model.number="form.prix_unitaire" class="input" min="0" />
            </div>
          </div>
          <div style="display:flex;gap:10px">
            <button class="btn btn-primary" :disabled="saving" @click="save">{{ saving ? '...' : (editingId ? 'Mettre à jour' : 'Créer') }}</button>
            <button class="btn btn-ghost" @click="showForm = false; resetForm()">Annuler</button>
          </div>
        </div>
      </div>

      <EmptyState v-if="filteredProduits.length === 0" :text="recherche ? 'Aucun résultat' : 'Aucun produit'" />

      <div v-else>
        <div class="filters">
          <input v-model="recherche" class="input" placeholder="Rechercher un produit..." style="max-width:260px" />
        </div>
        <div class="table-wrap anim-fade">
          <table>
            <thead><tr><th>Nom</th><th>Catégorie</th><th>Stock</th><th>Min</th><th>Prix</th><th>Statut</th><th></th></tr></thead>
            <tbody>
              <tr v-for="p in paginatedProduits" :key="p.id">
                <td><strong>{{ p.nom }}</strong></td>
                <td>{{ p.categorie?.nom || '—' }}</td>
                <td>{{ p.stock_actuel }} {{ p.unite_mesure }}</td>
                <td>{{ p.stock_min }}</td>
                <td>{{ Number(p.prix_unitaire).toLocaleString() }} F</td>
                <td><StatusBadge :status="p.stock_actuel <= 0 ? 'rupture' : p.stock_actuel <= p.stock_min ? 'stock bas' : 'disponible'" /></td>
                <td>
                  <button class="btn btn-ghost btn-sm" @click="openEdit(p)" aria-label="Modifier le produit">✎</button>
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

    <ConfirmDialog :show="showConfirm" title="Supprimer ce produit ?" message="Cette action est irréversible." confirmText="Supprimer" variant="danger" @confirm="confirmDelete" @cancel="showConfirm = false" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { getProduits, createProduit, updateProduit, getCategories } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import PageHeader from '../components/PageHeader.vue'
import EmptyState from '../components/EmptyState.vue'

const produits = ref([])
const categories = ref([])
const loading = ref(true)
const saving = ref(false)
const showForm = ref(false)
const editingId = ref(null)
const recherche = ref('')
const page = ref(1)
const pageSize = 15
const toast = useToastStore()
const showConfirm = ref(false)
const firstInput = ref(null)
const errors = reactive({ nom: '' })

const form = reactive({ nom: '', categorie_id: '', unite_mesure: 'kg', stock_min: 0, stock_actuel: 0, prix_unitaire: 0 })

function resetForm() {
  Object.assign(form, { nom: '', categorie_id: '', unite_mesure: 'kg', stock_min: 0, stock_actuel: 0, prix_unitaire: 0 })
  editingId.value = null
  errors.nom = ''
}

function openCreate() {
  resetForm()
  showForm.value = true
  nextTick(() => firstInput.value?.focus())
}

function openEdit(p) {
  editingId.value = p.id
  Object.assign(form, { nom: p.nom, categorie_id: p.categorie?.id || '', unite_mesure: p.unite_mesure || 'kg', stock_min: p.stock_min, stock_actuel: p.stock_actuel, prix_unitaire: p.prix_unitaire })
  showForm.value = true
  nextTick(() => firstInput.value?.focus())
}

const filteredProduits = computed(() => {
  if (!recherche.value) return produits.value
  const q = recherche.value.toLowerCase()
  return produits.value.filter(p => p.nom.toLowerCase().includes(q) || p.categorie?.nom?.toLowerCase().includes(q))
})
const totalPages = computed(() => Math.ceil(filteredProduits.value.length / pageSize))
const paginatedProduits = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredProduits.value.slice(start, start + pageSize)
})

async function load() {
  loading.value = true
  try { [produits.value, categories.value] = await Promise.all([getProduits(), getCategories()]) } finally { loading.value = false }
}

function validate() {
  errors.nom = form.nom ? '' : 'Le nom est requis'
  return !errors.nom
}

async function save() {
  if (!validate()) { toast.warning('Veuillez corriger les erreurs'); return }
  saving.value = true
  try {
    const payload = { ...form, categorie_id: form.categorie_id ? Number(form.categorie_id) : null }
    if (editingId.value) {
      await updateProduit(editingId.value, payload)
      toast.success('Produit mis à jour')
    } else {
      await createProduit(payload)
      toast.success('Produit créé')
    }
    showForm.value = false; resetForm(); await load()
  } finally { saving.value = false }
}

function confirmDelete() { showConfirm.value = false }

onMounted(load)
</script>

<style scoped>
.pagination { display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 16px; }
.page-info { font-size: 13px; color: var(--text-secondary); }
.input-error { border-color: var(--error) !important; }
.field-error { font-size: 11px; color: var(--error); margin-top: 3px; }
</style>
