<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Produits</h1>
        <p class="page-subtitle">Catalogue des produits</p>
      </div>
      <button v-if="!showForm" class="btn btn-primary" @click="showForm = true">+ Nouveau</button>
    </div>

    <LoadingSpinner v-if="loading" />
    <template v-else>
      <div v-if="showForm" class="card anim-slide" style="margin-bottom:20px">
        <div class="card-header">
          <h3>Nouveau produit</h3>
          <button class="btn btn-ghost btn-sm" @click="showForm = false; resetForm()">✕</button>
        </div>
        <div class="form-card">
          <div class="form-row">
            <div class="form-group"><label>Nom *</label><input v-model="form.nom" class="input" /></div>
            <div class="form-group">
              <label>Catégorie</label>
              <select v-model="form.categorie_id" class="input">
                <option value="">Sélectionner...</option>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.nom }}</option>
              </select>
            </div>
            <div class="form-group"><label>Unité</label><input v-model="form.unite_mesure" class="input" /></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>Stock min</label><input type="number" v-model.number="form.stock_min" class="input" step="0.1" /></div>
            <div class="form-group"><label>Stock actuel</label><input type="number" v-model.number="form.stock_actuel" class="input" step="0.1" /></div>
            <div class="form-group"><label>Prix unitaire (FCFA)</label><input type="number" v-model.number="form.prix_unitaire" class="input" /></div>
          </div>
          <div style="display:flex;gap:10px">
            <button class="btn btn-primary" :disabled="saving" @click="save">{{ saving ? '...' : 'Créer' }}</button>
            <button class="btn btn-ghost" @click="showForm = false; resetForm()">Annuler</button>
          </div>
        </div>
      </div>

      <div v-if="produits.length === 0" class="empty anim-fade">
        <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
        <div class="empty-text">Aucun produit</div>
      </div>

      <div v-else class="table-wrap anim-fade">
        <table>
          <thead><tr><th>Nom</th><th>Catégorie</th><th>Stock</th><th>Min</th><th>Prix</th><th>Statut</th></tr></thead>
          <tbody>
            <tr v-for="p in produits" :key="p.id">
              <td><strong>{{ p.nom }}</strong></td>
              <td>{{ p.categorie?.nom || '—' }}</td>
              <td>{{ p.stock_actuel }} {{ p.unite_mesure }}</td>
              <td>{{ p.stock_min }}</td>
              <td>{{ Number(p.prix_unitaire).toLocaleString() }} F</td>
              <td><StatusBadge :status="p.stock_actuel <= 0 ? 'rupture' : p.stock_actuel <= p.stock_min ? 'stock bas' : 'disponible'" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getProduits, createProduit, getCategories } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'

const produits = ref([])
const categories = ref([])
const loading = ref(true)
const saving = ref(false)
const showForm = ref(false)
const toast = useToastStore()
const form = reactive({ nom: '', categorie_id: '', unite_mesure: 'kg', stock_min: 0, stock_actuel: 0, prix_unitaire: 0 })
function resetForm() { Object.assign(form, { nom: '', categorie_id: '', unite_mesure: 'kg', stock_min: 0, stock_actuel: 0, prix_unitaire: 0 }) }

async function load() {
  loading.value = true
  try { [produits.value, categories.value] = await Promise.all([getProduits(), getCategories()]) } finally { loading.value = false }
}

async function save() {
  if (!form.nom) { toast.warning('Nom requis'); return }
  saving.value = true
  try {
    await createProduit({ ...form, categorie_id: form.categorie_id ? Number(form.categorie_id) : null })
    toast.success('Produit créé'); showForm.value = false; resetForm(); await load()
  } finally { saving.value = false }
}

onMounted(load)
</script>
