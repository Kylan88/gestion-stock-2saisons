<template>
  <div class="page">
    <PageHeader title="Produits" subtitle="Catalogue des produits">
      <template #actions>
        <button v-if="!showForm" class="btn btn-outline btn-sm" @click="doExport">CSV</button>
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
              <label>Catégorie *</label>
              <select ref="firstInput" v-model="form.categorie_id" class="input" :class="{ 'input-error': errors.nom }">
                <option value="">Sélectionner...</option>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.nom }}</option>
              </select>
              <span v-if="errors.nom" class="field-error">{{ errors.nom }}</span>
            </div>
            <div class="form-group">
              <label>Unité</label>
              <input v-model="form.unite_mesure" class="input" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Cartons</label>
              <input type="number" v-model.number="form.stock_min" class="input" step="1" min="0" placeholder="Nombre de cartons" />
            </div>
            <div class="form-group">
              <label>Stock actuel</label>
              <input type="number" v-model.number="form.stock_actuel" class="input" step="0.1" min="0" />
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
        <div class="filters" style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
          <input v-model="recherche" class="input" placeholder="Rechercher un produit..." style="max-width:260px" />
          <select v-model="selectedLotId" class="input" style="max-width:260px" title="Filtrer par lot disponible">
            <option value="">Tous les lots</option>
            <option v-for="l in lotsDisponibles" :key="l.id" :value="String(l.id)">{{ l.code_lot }}{{ l.type_fruit ? ' — ' + l.type_fruit : '' }}</option>
          </select>
          <label style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);cursor:pointer">
            <input type="checkbox" v-model="showZeroStock" /> Afficher stock 0
          </label>
          <span v-if="!showZeroStock" style="font-size:11px;color:var(--text-muted)">— masqués quand stock = 0</span>
        </div>
        <div class="table-wrap anim-fade">
          <table>
            <thead><tr><th>Catégorie</th><th>Stock</th><th>Cartons</th><th>Statut</th><th></th></tr></thead>
            <tbody>
              <tr v-for="p in paginatedProduits" :key="p.id">
                <td><strong>{{ p.categorie?.nom || p.nom }}</strong></td>
                <td>{{ fmt2(p.stock_actuel) }} {{ p.unite_mesure }}</td>
                <td>{{ p.stock_min }}</td>
                <td><StatusBadge :status="p.stock_actuel > 0 ? 'disponible' : 'rupture'" /></td>
                <td>
                  <button class="btn btn-ghost btn-sm" @click="openEdit(p)" aria-label="Modifier le produit">✎</button>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr style="font-weight:700;background:var(--surface);border-top:2px solid var(--border)">
                <td>Totaux ({{ filteredProduits.length }})</td>
                <td>{{ fmt2(totalStock) }}</td>
                <td>{{ totalCartons }}</td>
                <td></td>
                <td></td>
              </tr>
            </tfoot>
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
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import { getProduits, createProduit, updateProduit, getCategories, getStock } from '../api'
import { useToastStore } from '../stores/toast'
import { exportCsv } from '../utils/exportCsv'
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

const form = reactive({ nom: '', categorie_id: '', unite_mesure: 'kg', stock_min: 0, stock_actuel: 0 })

function resetForm() {
  Object.assign(form, { nom: '', categorie_id: '', unite_mesure: 'kg', stock_min: 0, stock_actuel: 0 })
  editingId.value = null
  errors.nom = ''
}
function categorieNom(id) {
  return categories.value.find(c => String(c.id) === String(id))?.nom || ''
}

function openCreate() {
  resetForm()
  showForm.value = true
  nextTick(() => firstInput.value?.focus())
}

function openEdit(p) {
  editingId.value = p.id
  Object.assign(form, { nom: p.nom, categorie_id: p.categorie?.id || '', unite_mesure: p.unite_mesure || 'kg', stock_min: p.stock_min, stock_actuel: p.stock_actuel })
  showForm.value = true
  nextTick(() => firstInput.value?.focus())
}

const showZeroStock = ref(false)
const selectedLotId = ref('')
const lotsDisponibles = ref([])
const produitsParLot = ref({}) // { lotId: Set(produitId) }
const filteredProduits = computed(() => {
  let res = produits.value
  if (!showZeroStock.value) res = res.filter(p => Number(p.stock_actuel) > 0)
  if (selectedLotId.value) {
    const ids = produitsParLot.value[selectedLotId.value]
    if (!ids) return []
    res = res.filter(p => ids.has(p.id))
  }
  if (!recherche.value) return res
  const q = recherche.value.toLowerCase()
  return res.filter(p => p.nom.toLowerCase().includes(q) || p.categorie?.nom?.toLowerCase().includes(q))
})
const totalPages = computed(() => Math.ceil(filteredProduits.value.length / pageSize))
const paginatedProduits = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredProduits.value.slice(start, start + pageSize)
})
const totalStock = computed(() => filteredProduits.value.reduce((s, p) => s + Number(p.stock_actuel || 0), 0))
const totalCartons = computed(() => filteredProduits.value.reduce((s, p) => s + Number(p.stock_min || 0), 0))
watch([recherche, selectedLotId, showZeroStock], () => { page.value = 1 })
function fmt2(v) { const n = Number(v); return Number.isFinite(n) ? n.toFixed(2) : '0.00' }

async function load() {
  loading.value = true
  try {
    const [prods, cats, stocks] = await Promise.all([getProduits(), getCategories(), getStock()])
    produits.value = prods
    categories.value = cats
    // Lots disponibles = lots avec au moins une ligne de stock > 0 en zone.
    const lotsMap = new Map()
    const parLot = {}
    for (const s of (stocks || [])) {
      if (!s?.lot?.id || !(Number(s.quantite) > 0)) continue
      const lotId = String(s.lot.id)
      if (!lotsMap.has(lotId)) lotsMap.set(lotId, s.lot)
      if (!parLot[lotId]) parLot[lotId] = new Set()
      if (s.produit_id) parLot[lotId].add(s.produit_id)
      else if (s.produit?.id) parLot[lotId].add(s.produit.id)
    }
    lotsDisponibles.value = [...lotsMap.values()].sort((a, b) => (a.code_lot || '').localeCompare(b.code_lot || ''))
    produitsParLot.value = parLot
    if (selectedLotId.value && !parLot[selectedLotId.value]) selectedLotId.value = ''
  } finally { loading.value = false }
}

function validate() {
  errors.nom = form.categorie_id ? '' : 'La catégorie est requise'
  if (!form.categorie_id) return false
  // nom backend = nom de la catégorie
  form.nom = categorieNom(form.categorie_id) || form.nom
  errors.nom = form.nom ? '' : 'La catégorie est requise'
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

function doExport() {
  const headers = ['Catégorie', 'Stock Actuel', 'Cartons', 'Unité']
  const rows = filteredProduits.value.map(p => [p.categorie?.nom || p.nom, p.stock_actuel, p.stock_min, p.unite_mesure])
  exportCsv(headers, rows, 'produits.csv')
}

onMounted(load)
</script>

<style scoped>
.pagination { display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 16px; }
.page-info { font-size: 13px; color: var(--text-secondary); }
.input-error { border-color: var(--error) !important; }
.field-error { font-size: 11px; color: var(--error); margin-top: 3px; }
</style>
