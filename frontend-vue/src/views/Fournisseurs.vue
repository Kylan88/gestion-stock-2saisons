<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Fournisseurs</h1>
        <p class="page-subtitle">Gestion des fournisseurs</p>
      </div>
      <button v-if="!showForm" class="btn btn-primary" @click="showForm = true">+ Nouveau</button>
    </div>

    <LoadingSpinner v-if="loading" />
    <template v-else>
      <div v-if="showForm" class="card anim-slide" style="margin-bottom:20px">
        <div class="card-header">
          <h3>Nouveau fournisseur</h3>
          <button class="btn btn-ghost btn-sm" @click="showForm = false; resetForm()">✕</button>
        </div>
        <div class="form-card">
          <div class="form-row">
            <div class="form-group"><label>Nom *</label><input v-model="form.nom" class="input" /></div>
            <div class="form-group"><label>Contact</label><input v-model="form.contact" class="input" /></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>Téléphone</label><input v-model="form.telephone" class="input" /></div>
            <div class="form-group"><label>Email</label><input v-model="form.email" class="input" type="email" /></div>
          </div>
          <div class="form-group"><label>Adresse</label><input v-model="form.adresse" class="input" /></div>
          <div style="display:flex;gap:10px">
            <button class="btn btn-primary" :disabled="saving" @click="save">{{ saving ? '...' : 'Créer' }}</button>
            <button class="btn btn-ghost" @click="showForm = false; resetForm()">Annuler</button>
          </div>
        </div>
      </div>

      <div v-if="fournisseurs.length === 0" class="empty anim-fade">
        <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
        <div class="empty-text">Aucun fournisseur</div>
      </div>

      <div v-else class="table-wrap anim-fade">
        <table>
          <thead><tr><th>Nom</th><th>Contact</th><th>Téléphone</th><th>Email</th><th>Statut</th></tr></thead>
          <tbody>
            <tr v-for="f in fournisseurs" :key="f.id">
              <td><strong>{{ f.nom }}</strong></td>
              <td>{{ f.contact || '—' }}</td>
              <td>{{ f.telephone || '—' }}</td>
              <td>{{ f.email || '—' }}</td>
              <td><StatusBadge :status="f.actif ? 'disponible' : 'périmé'" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getFournisseurs, createFournisseur } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'

const fournisseurs = ref([])
const loading = ref(true)
const saving = ref(false)
const showForm = ref(false)
const toast = useToastStore()
const form = reactive({ nom: '', contact: '', telephone: '', email: '', adresse: '' })
function resetForm() { Object.assign(form, { nom: '', contact: '', telephone: '', email: '', adresse: '' }) }

async function load() {
  loading.value = true
  try { fournisseurs.value = await getFournisseurs() } finally { loading.value = false }
}

async function save() {
  if (!form.nom) { toast.warning('Nom requis'); return }
  saving.value = true
  try { await createFournisseur(form); toast.success('Fournisseur créé'); showForm.value = false; resetForm(); await load() } finally { saving.value = false }
}

onMounted(load)
</script>
