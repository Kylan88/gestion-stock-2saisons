<template>
  <div class="page">
    <PageHeader title="Commandes" subtitle="Gestion des commandes clients">
      <template #actions>
        <button v-if="!showForm" class="btn btn-outline btn-sm" @click="doExport">CSV</button>
        <button v-if="!showForm" class="btn btn-primary" @click="showForm = true">+ Nouvelle</button>
      </template>
    </PageHeader>

    <LoadingSpinner v-if="loading" />
    <template v-else>
      <div v-if="showForm" class="card anim-slide" style="margin-bottom:20px">
        <div class="card-header">
          <h3>Nouvelle commande</h3>
          <button class="btn btn-ghost btn-sm" @click="showForm = false; resetForm()" aria-label="Fermer">✕</button>
        </div>
        <div class="form-card">
          <div class="form-row">
            <div class="form-group"><label>Client * — nom du client</label><input ref="firstInput" v-model="form.client_nom" class="input" placeholder="Ex : Marché Central" /></div>
            <div class="form-group"><label>Contact — téléphone ou personne à joindre</label><input v-model="form.client_contact" class="input" placeholder="Ex : 07 00 00 00 00" /></div>
            <div class="form-group"><label>Livraison prévue — date souhaitée</label><input type="date" v-model="form.date_livraison_prevue" class="input" /></div>
          </div>
          <div class="form-group"><label>Notes — observations libres</label><input v-model="form.notes" class="input" placeholder="Ex : livraison en 2 fois" /></div>
          <div class="form-group">
            <label>Lignes de commande — une ligne = un produit + un lot (optionnel) + une quantité en kg</label>
            <div v-for="(ligne, i) in form.lignes" :key="i" class="ligne-row" style="flex-wrap:wrap">
              <select v-model="ligne.produit_id" class="input" style="flex:2;min-width:140px">
                <option value="">Choisir un produit...</option>
                <option v-for="p in produits" :key="p.id" :value="p.id">{{ produitLabel(p) }}</option>
              </select>
              <select v-model="ligne.lot_id" class="input" style="flex:2;min-width:140px">
                <option value="">Lot (optionnel — précise la traçabilité)...</option>
                <option v-for="l in lots" :key="l.id" :value="l.id">{{ l.code_lot }} — {{ l.statut }}</option>
              </select>
              <input type="number" v-model.number="ligne.quantite" class="input" style="flex:1;min-width:90px" :placeholder="ligne.produit_id && isSachet(produits.find(x => Number(x.id) === Number(ligne.produit_id))) ? 'Qté en sachets' : 'Qté en cartons'" min="0" />
              <button class="btn btn-ghost btn-sm" @click="form.lignes.splice(i, 1)" aria-label="Supprimer la ligne">✕</button>
              <div v-if="ligne.produit_id" style="flex-basis:100%;font-size:11px;color:var(--text-muted)">
                Dispo : {{ dispoTxt(ligne) || '…' }}
                <span v-if="ligne.quantite > dispoNombre(ligne)" class="field-error"> — insuffisant !</span>
              </div>
            </div>
            <button class="btn btn-sm btn-outline" style="margin-top:8px" @click="form.lignes.push({ produit_id: '', lot_id: '', quantite: 0 })">+ Ajouter ligne</button>
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
        <div class="filters">
          <input v-model="recherche" class="input" placeholder="Rechercher client..." style="max-width:260px" />
        </div>
        <EmptyState v-if="filteredCommandes.length === 0" :text="recherche ? 'Aucun résultat' : 'Aucune commande'" />
        <div v-for="cmd in filteredCommandes" :key="cmd.id" class="card anim-fade" style="margin-bottom:10px">
          <div class="card-header" style="margin-bottom:0">
            <div style="display:flex;align-items:center;gap:10px">
              <strong>{{ cmd.client_nom }}</strong>
              <StatusBadge :status="cmd.statut" />
            </div>
            <div style="display:flex;align-items:center;gap:16px;font-size:13px;color:var(--text-secondary)">
              <span>{{ new Date(cmd.date_commande).toLocaleDateString() }}</span>
              <span v-if="cmd.date_livraison_prevue">Livr. {{ new Date(cmd.date_livraison_prevue).toLocaleDateString() }}</span>
            </div>
          </div>
          <div v-if="cmd.lignes?.length" class="cmd-lignes">
            <div v-for="l in cmd.lignes" :key="l.id" class="cmd-ligne">
              <span>{{ produitLabel(l.produit || { nom: 'Produit #' + l.produit_id }) }}<small v-if="l.lot" style="margin-left:6px;color:var(--text-muted)">lot {{ l.lot.code_lot }}</small></span>
              <span>{{ l.quantite }} {{ unitePluriel(uniteLigne(l)) }}</span>
            </div>
          </div>
          <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
            <button v-if="cmd.statut === 'en_attente'" class="btn btn-sm btn-outline" @click="changerStatut(cmd.id, 'préparée')">Préparer</button>
            <button v-if="cmd.statut === 'préparée'" class="btn btn-sm btn-primary" @click="changerStatut(cmd.id, 'livrée')">Livrer (décrémente le stock)</button>
            <button v-if="cmd.statut === 'en_attente' || cmd.statut === 'préparée'" class="btn btn-sm btn-ghost" @click="changerStatut(cmd.id, 'annulée')">Annuler</button>
            <button class="btn btn-sm btn-outline" @click="openBL(cmd)">BL / Imprimer</button>
          </div>
        </div>
      </div>
    </template>

    <div v-if="blCmd" class="modal-overlay" @click.self="blCmd = null">
      <div class="modal bl-doc" style="max-width:640px">
        <div class="bl-head">
          <div>
            <div class="bl-title">BON DE LIVRAISON</div>
            <div class="bl-num">N° BL-{{ String(blCmd.id).padStart(4, '0') }}</div>
          </div>
          <div class="bl-date">{{ new Date(blCmd.date_commande).toLocaleDateString('fr-FR') }}</div>
        </div>
        <div class="bl-client">
          <div><strong>Client :</strong> {{ blCmd.client_nom }}</div>
          <div v-if="blCmd.client_contact"><strong>Contact :</strong> {{ blCmd.client_contact }}</div>
          <div v-if="blCmd.date_livraison_prevue"><strong>Livraison prévue :</strong> {{ new Date(blCmd.date_livraison_prevue).toLocaleDateString('fr-FR') }}</div>
          <div v-if="blCmd.date_livraison_reelle"><strong>Livrée le :</strong> {{ new Date(blCmd.date_livraison_reelle).toLocaleDateString('fr-FR') }}</div>
          <div><strong>Statut :</strong> {{ blCmd.statut }}</div>
        </div>
        <table class="table bl-table">
          <thead><tr><th>Produit</th><th>Lot</th><th>Qté</th></tr></thead>
          <tbody>
            <tr v-for="l in blCmd.lignes" :key="l.id">
              <td>{{ produitLabel(l.produit || { nom: 'Produit #' + l.produit_id }) }}</td>
              <td>{{ l.lot?.code_lot || '—' }}</td>
              <td>{{ l.quantite }} {{ unitePluriel(uniteLigne(l)) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="blCmd.notes" class="bl-notes">Notes : {{ blCmd.notes }}</div>
        <div class="bl-sign">
          <div class="bl-sign-box">Signature client<br /><br />_________________</div>
          <div class="bl-sign-box">Signature magasin<br /><br />_________________</div>
        </div>
        <div class="modal-footer no-print">
          <button class="btn btn-ghost" @click="blCmd = null">Fermer</button>
          <button class="btn btn-primary" @click="printBL">Imprimer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import { getCommandes, createCommande, updateCommandeStatut, getProduits, getLots, getStock } from '../api'
import { useToastStore } from '../stores/toast'
import { exportCsv } from '../utils/exportCsv'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import EmptyState from '../components/EmptyState.vue'

const commandes = ref([])
const produits = ref([])
const lots = ref([])
const stocks = ref([])
const loading = ref(true)
const saving = ref(false)
const showForm = ref(false)
const recherche = ref('')
const toast = useToastStore()
const firstInput = ref(null)
const blCmd = ref(null)
const form = reactive({ client_nom: '', client_contact: '', date_livraison_prevue: '', notes: '', lignes: [] })
function resetForm() { form.client_nom = ''; form.client_contact = ''; form.date_livraison_prevue = ''; form.notes = ''; form.lignes = [] }
const fluxField = { 'Local': 'local_cartons', 'Export': 'export_cartons', 'Fitini Fê': 'fitini_fe_cartons', 'Déchets': 'dechets_cartons', 'Rhum arrangé': 'rhum_cartons' }
function produitLabel(p) {
  if (!p) return '—'
  if (p.nom === 'Sachet 100g fitini_fe') return 'FF (100g fitini fê)'
  if (p.nom === 'Sachet 100g local') return '100g (local)'
  if (p.nom === 'Fitini Fê') return 'FF (carton)'
  return p.nom
}
function isSachet(p) {
  return !!p && (p.nom?.startsWith('Sachet 100g') || p.unite_mesure === 'sachet 100g')
}
function dispoStock(produitId, lotId) {
  if (!produitId) return 0
  return stocks.value
    .filter(s => Number(s.produit_id) === Number(produitId) && (!lotId || Number(s.lot_id) === Number(lotId)))
    .reduce((t, s) => t + Number(s.quantite || 0), 0)
}
function dispoSachets(produitId, lotId) {
  if (!produitId) return 0
  return stocks.value
    .filter(s => Number(s.produit_id) === Number(produitId) && (!lotId || Number(s.lot_id) === Number(lotId)))
    .reduce((t, s) => t + Number(s.sachets || 0), 0)
}
function uniteDeProduit(p) { return isSachet(p) ? 'sachet' : 'carton' }
function unitePluriel(u) { return u === 'sachet' ? 'sachets' : 'cartons' }
function dispoNombre(ligne) {
  const p = produits.value.find(x => Number(x.id) === Number(ligne.produit_id))
  if (!p) return 0
  if (isSachet(p)) return dispoSachets(ligne.produit_id, ligne.lot_id)
  if (ligne.lot_id) {
    const lot = lots.value.find(x => Number(x.id) === Number(ligne.lot_id))
    const field = fluxField[p.nom]
    if (lot && field) return Number(lot[field] || 0)
  }
  return Number(p.stock_min || 0)
}
function dispoTxt(ligne) {
  const p = produits.value.find(x => Number(x.id) === Number(ligne.produit_id))
  if (!p) return ''
  const kg = formatNum(dispoStock(ligne.produit_id, ligne.lot_id))
  const u = uniteDeProduit(p)
  return `${formatNum(dispoNombre(ligne))} ${unitePluriel(u)} (${kg} kg)`
}
function uniteLigne(l) {
  if (l.unite === 'sachet' || l.unite === 'carton' || l.unite === 'kg') return l.unite
  const p = l.produit || produits.value.find(x => Number(x.id) === Number(l.produit_id))
  return uniteDeProduit(p)
}
function formatNum(v) { return Number(v || 0).toLocaleString('fr-FR') }
function openBL(cmd) { blCmd.value = cmd }
function printBL() { window.print() }

watch(showForm, (v) => { if (v) nextTick(() => firstInput.value?.focus()) })

const filteredCommandes = computed(() => {
  if (!recherche.value) return commandes.value
  const q = recherche.value.toLowerCase()
  return commandes.value.filter(c => c.client_nom.toLowerCase().includes(q))
})

async function load() {
  loading.value = true
  try { [commandes.value, produits.value, lots.value, stocks.value] = await Promise.all([getCommandes(), getProduits(), getLots(), getStock()]) } finally { loading.value = false }
}

async function save() {
  if (!form.client_nom || !form.lignes.length) { toast.warning('Nom client et au moins une ligne requis'); return }
  saving.value = true
  try {
    await createCommande({
      client_nom: form.client_nom, client_contact: form.client_contact,
      date_livraison_prevue: form.date_livraison_prevue ? new Date(form.date_livraison_prevue).toISOString() : null,
      notes: form.notes, lignes: form.lignes.map(l => {
        const p = produits.value.find(x => Number(x.id) === Number(l.produit_id))
        return { produit_id: Number(l.produit_id), lot_id: l.lot_id ? Number(l.lot_id) : null, quantite: l.quantite, unite: uniteDeProduit(p) }
      }),
    })
    toast.success('Commande créée'); showForm.value = false; resetForm(); await load()
  } finally { saving.value = false }
}

async function changerStatut(id, statut) {
  try { await updateCommandeStatut(id, statut); toast.success('Statut mis à jour'); await load() } catch {}
}

function doExport() {
  const headers = ['Client', 'Date', 'Statut', 'Lignes']
  const rows = filteredCommandes.value.map(c => [c.client_nom || '', c.date_commande ? new Date(c.date_commande).toLocaleDateString('fr-FR') : '', c.statut, (c.lignes || []).map(l => `${produitLabel(l.produit)}${l.lot ? ' (' + l.lot.code_lot + ')' : ''}: ${l.quantite} ${unitePluriel(uniteLigne(l))}`).join(' | ')])
  exportCsv(headers, rows, 'commandes.csv')
}

onMounted(load)
</script>

<style scoped>
.cmd-lignes { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border-light); display: flex; flex-direction: column; gap: 4px; }
.cmd-ligne { display: flex; justify-content: space-between; font-size: 13px; color: var(--text-secondary); padding: 4px 0; }
.ligne-row { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(17,24,39,0.45); display: flex; align-items: flex-start; justify-content: center; z-index: 100; padding: 32px 16px; overflow-y: auto; }
.modal { background: white; border-radius: 12px; width: 100%; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
.modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 14px 20px; border-top: 1px solid var(--border-light); }
.bl-doc { padding: 28px 32px; color: #111827; }
.bl-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.bl-title { font-size: 20px; font-weight: 800; letter-spacing: 0.04em; }
.bl-num { font-size: 14px; font-weight: 700; color: #00853E; }
.bl-date { font-size: 13px; color: #6b7280; }
.bl-client { font-size: 13px; display: flex; flex-direction: column; gap: 2px; margin-bottom: 14px; }
.bl-table { margin-bottom: 12px; }
.bl-total { text-align: right; font-size: 15px; margin-bottom: 8px; }
.bl-notes { font-size: 12px; color: #6b7280; margin-bottom: 20px; }
.bl-sign { display: flex; gap: 24px; margin: 24px 0 8px; }
.bl-sign-box { flex: 1; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; font-size: 12px; color: #6b7280; min-height: 90px; }
@media print {
  body * { visibility: hidden; }
  .bl-doc, .bl-doc * { visibility: visible; }
  .bl-doc { position: absolute; left: 0; top: 0; width: 100%; max-width: 100%; box-shadow: none; margin: 0; }
  .modal-overlay { position: static; background: none; padding: 0; overflow: visible; }
  .no-print { display: none !important; }
}
</style>
