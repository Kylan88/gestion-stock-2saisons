<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Commandes</h1>
        <p class="page-subtitle">Gestion des commandes clients</p>
      </div>
      <button v-if="!showForm" class="btn btn-primary" @click="showForm = true">+ Nouvelle</button>
    </div>

    <LoadingSpinner v-if="loading" />
    <template v-else>
      <div v-if="showForm" class="card anim-slide" style="margin-bottom:20px">
        <div class="card-header">
          <h3>Nouvelle commande</h3>
          <button class="btn btn-ghost btn-sm" @click="showForm = false; resetForm()">✕</button>
        </div>
        <div class="form-card">
          <div class="form-row">
            <div class="form-group"><label>Client *</label><input v-model="form.client_nom" class="input" /></div>
            <div class="form-group"><label>Contact</label><input v-model="form.client_contact" class="input" /></div>
            <div class="form-group"><label>Livraison prévue</label><input type="date" v-model="form.date_livraison_prevue" class="input" /></div>
          </div>
          <div class="form-group"><label>Notes</label><input v-model="form.notes" class="input" /></div>
          <div class="form-group">
            <label>Lignes de commande</label>
            <div v-for="(ligne, i) in form.lignes" :key="i" class="ligne-row">
              <select v-model="ligne.produit_id" class="input" style="flex:2">
                <option value="">Produit...</option>
                <option v-for="p in produits" :key="p.id" :value="p.id">{{ p.nom }}</option>
              </select>
              <input type="number" v-model.number="ligne.quantite" class="input" style="flex:1" placeholder="Qté" min="0" />
              <input type="number" v-model.number="ligne.prix_unitaire" class="input" style="flex:1" placeholder="Prix" min="0" />
              <button class="btn btn-ghost btn-sm" @click="form.lignes.splice(i, 1)">✕</button>
            </div>
            <button class="btn btn-sm btn-outline" style="margin-top:8px" @click="form.lignes.push({ produit_id: '', quantite: 0, prix_unitaire: 0 })">+ Ajouter ligne</button>
          </div>
          <div style="display:flex;gap:10px">
            <button class="btn btn-primary" :disabled="saving" @click="save">{{ saving ? '...' : 'Créer la commande' }}</button>
            <button class="btn btn-ghost" @click="showForm = false; resetForm()">Annuler</button>
          </div>
        </div>
      </div>

      <div v-if="commandes.length === 0" class="empty anim-fade">
        <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
        <div class="empty-text">Aucune commande</div>
      </div>

      <div v-else>
        <div v-for="cmd in commandes" :key="cmd.id" class="card anim-fade" style="margin-bottom:10px">
          <div class="card-header" style="margin-bottom:0">
            <div style="display:flex;align-items:center;gap:10px">
              <strong>{{ cmd.client_nom }}</strong>
              <StatusBadge :status="cmd.statut" />
            </div>
            <div style="display:flex;align-items:center;gap:16px;font-size:13px;color:var(--text-secondary)">
              <span>{{ new Date(cmd.date_commande).toLocaleDateString() }}</span>
              <span v-if="cmd.date_livraison_prevue">Livr. {{ new Date(cmd.date_livraison_prevue).toLocaleDateString() }}</span>
              <strong style="color:var(--dark)">{{ Number(cmd.total_ht).toLocaleString() }} F</strong>
            </div>
          </div>
          <div v-if="cmd.lignes?.length" class="cmd-lignes">
            <div v-for="l in cmd.lignes" :key="l.id" class="cmd-ligne">
              <span>{{ l.produit?.nom || 'Produit #' + l.produit_id }}</span>
              <span>{{ l.quantite }} × {{ Number(l.prix_unitaire).toLocaleString() }} F</span>
            </div>
          </div>
          <div v-if="cmd.statut !== 'livrée'" style="margin-top:10px;display:flex;gap:8px">
            <button v-if="cmd.statut === 'en_attente'" class="btn btn-sm btn-outline" @click="changerStatut(cmd.id, 'préparée')">Préparer</button>
            <button v-if="cmd.statut === 'préparée'" class="btn btn-sm btn-primary" @click="changerStatut(cmd.id, 'livrée')">Livrer</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getCommandes, createCommande, updateCommandeStatut, getProduits } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'

const commandes = ref([])
const produits = ref([])
const loading = ref(true)
const saving = ref(false)
const showForm = ref(false)
const toast = useToastStore()
const form = reactive({ client_nom: '', client_contact: '', date_livraison_prevue: '', notes: '', lignes: [] })
function resetForm() { form.client_nom = ''; form.client_contact = ''; form.date_livraison_prevue = ''; form.notes = ''; form.lignes = [] }

async function load() {
  loading.value = true
  try { [commandes.value, produits.value] = await Promise.all([getCommandes(), getProduits()]) } finally { loading.value = false }
}

async function save() {
  if (!form.client_nom || !form.lignes.length) { toast.warning('Nom client et au moins une ligne requis'); return }
  saving.value = true
  try {
    await createCommande({
      client_nom: form.client_nom, client_contact: form.client_contact,
      date_livraison_prevue: form.date_livraison_prevue ? new Date(form.date_livraison_prevue).toISOString() : null,
      notes: form.notes, lignes: form.lignes.map(l => ({ produit_id: Number(l.produit_id), quantite: l.quantite, prix_unitaire: l.prix_unitaire })),
    })
    toast.success('Commande créée'); showForm.value = false; resetForm(); await load()
  } finally { saving.value = false }
}

async function changerStatut(id, statut) {
  try { await updateCommandeStatut(id, statut); toast.success('Statut mis à jour'); await load() } catch {}
}

onMounted(load)
</script>

<style scoped>
.cmd-lignes { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border-light); display: flex; flex-direction: column; gap: 4px; }
.cmd-ligne { display: flex; justify-content: space-between; font-size: 13px; color: var(--text-secondary); padding: 4px 0; }
.ligne-row { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
</style>
