<template>
  <div class="page">
    <PageHeader title="Production" subtitle="Entrées journalières — kg frais, dryers remplis, rendement pulpe">
      <template #actions>
        <button class="btn btn-primary" @click="showConfig = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          Config
        </button>
        <button class="btn btn-primary" @click="showForm = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Nouvelle entrée
        </button>
      </template>
    </PageHeader>

    <!-- KPIs -->
    <div class="kpi-grid anim-fade">
      <div class="kpi-card">
        <div class="kpi-label">Total kg frais</div>
        <div class="kpi-value">{{ formatKg(stats.total_kg_frais) }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Dryers remplis</div>
        <div class="kpi-value">{{ stats.total_dryers }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Rendement moyen</div>
        <div class="kpi-value">{{ (stats.rendement_moyen * 100).toFixed(1) }}%</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Pulpe obtenue</div>
        <div class="kpi-value">{{ formatKg(Object.values(stats.par_fruit).reduce((s, f) => s + (f.pulpe_obtenue_kg || 0), 0)) }}</div>
      </div>
    </div>

    <!-- Filtres -->
    <div class="card anim-fade" style="margin-top:16px">
      <div class="form-row" style="gap:16px; flex-wrap:wrap; margin-bottom:12px">
        <div class="form-group" style="flex:1; min-width:180px">
          <label>Date début</label>
          <input type="date" v-model="filters.date_from" class="form-input" @change="loadEntries" />
        </div>
        <div class="form-group" style="flex:1; min-width:180px">
          <label>Date fin</label>
          <input type="date" v-model="filters.date_to" class="form-input" @change="loadEntries" />
        </div>
        <div class="form-group" style="flex:1; min-width:180px">
          <label>Type fruit</label>
          <select v-model="filters.fruit_type" class="form-input" @change="loadEntries">
            <option value="">Tous</option>
            <option v-for="ft in config.fruit_types" :key="ft" :value="ft">{{ ft }}</option>
          </select>
        </div>
        <div class="form-group" style="flex:1; min-width:180px">
          <label>Saison</label>
          <select v-model="filters.saison_id" class="form-input" @change="loadEntries">
            <option value="">Toutes</option>
            <option v-for="s in saisons" :key="s.id" :value="s.id">{{ s.nom }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Tableau des entrées -->
    <div class="card anim-fade" style="margin-top:16px">
      <LoadingSpinner v-if="loading" />
      <div v-else-if="entries.length === 0" class="empty">
        <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
        <div class="empty-text">Aucune entrée de production</div>
        <div class="empty-sub">Cliquez sur "Nouvelle entrée" pour commencer</div>
      </div>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Fruit</th>
              <th>Kg frais</th>
              <th>Dryers</th>
              <th>Pulpe obtenue (kg)</th>
              <th>Rendement</th>
              <th>Notes</th>
              <th style="width:60px"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in entries" :key="e.id">
              <td>{{ formatDate(e.date) }}</td>
              <td><span class="fruit-badge">{{ e.fruit_type }}</span></td>
              <td>{{ formatKg(e.poids_frais_kg) }}</td>
              <td><strong>{{ e.nb_dryers }}</strong></td>
              <td>{{ formatKg(e.pulpe_obtenue_kg) }}</td>
              <td><span class="rendement-badge" :class="rendementClass(e.rendement)">{{ (e.rendement * 100).toFixed(1) }}%</span></td>
              <td>{{ e.notes || '—' }}</td>
              <td>
                <button class="btn btn-ghost btn-sm" @click="confirmDelete(e)" title="Supprimer">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Stats par fruit -->
    <div v-if="Object.keys(stats.par_fruit).length > 0" class="card anim-fade" style="margin-top:16px">
      <div class="card-header" style="margin-bottom:12px"><strong>Par type de fruit</strong></div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Fruit</th>
              <th>Entrées</th>
              <th>Kg frais</th>
              <th>Dryers</th>
              <th>Pulpe (kg)</th>
              <th>Rendement</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(f, fruit) in stats.par_fruit" :key="fruit">
              <td><span class="fruit-badge">{{ fruit }}</span></td>
              <td>{{ f.entries }}</td>
              <td>{{ formatKg(f.kg_frais) }}</td>
              <td>{{ f.dryers }}</td>
              <td>{{ formatKg(f.pulpe_obtenue_kg) }}</td>
              <td><span class="rendement-badge" :class="rendementClass(f.rendement)">{{ (f.rendement * 100).toFixed(1) }}%</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Config -->
    <div v-if="showConfig" class="modal-overlay" @click.self="showConfig = false">
      <div class="modal" style="max-width:480px">
        <div class="modal-header">
          <h3>Configuration Production</h3>
          <button class="modal-close" @click="showConfig = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Capacité dryer (kg pulpe)</label>
            <input type="number" step="0.1" min="1" v-model.number="configForm.dryer_capacity_kg" class="form-input" />
          </div>
          <div class="form-group">
            <label>Types de fruits (séparés par virgule)</label>
            <input type="text" v-model="configForm.fruit_types_str" class="form-input" placeholder="mangue, ananas, goyave" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showConfig = false">Annuler</button>
          <button class="btn btn-primary" @click="saveConfig">Enregistrer</button>
        </div>
      </div>
    </div>

    <!-- Modal Nouvelle entrée -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal" style="max-width:520px">
        <div class="modal-header">
          <h3>Nouvelle entrée de production</h3>
          <button class="modal-close" @click="showForm = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group" style="flex:1">
              <label>Date</label>
              <input type="date" v-model="form.date" class="form-input" />
            </div>
            <div class="form-group" style="flex:1">
              <label>Type fruit</label>
              <select v-model="form.fruit_type" class="form-input">
                <option value="" disabled>Sélectionner</option>
                <option v-for="ft in config.fruit_types" :key="ft" :value="ft">{{ ft }}</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group" style="flex:1">
              <label>Poids frais (kg)</label>
              <input type="number" step="0.1" min="0.1" v-model.number="form.poids_frais_kg" class="form-input" />
            </div>
            <div class="form-group" style="flex:1">
              <label>Nombre de dryers</label>
              <input type="number" min="1" v-model.number="form.nb_dryers" class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>Saison</label>
            <select v-model="form.saison_id" class="form-input">
              <option value="">— Sans saison —</option>
              <option v-for="s in saisons" :key="s.id" :value="s.id">{{ s.nom }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="form.notes" class="form-input" rows="2" placeholder="Observations..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showForm = false">Annuler</button>
          <button class="btn btn-primary" @click="submitForm" :disabled="submitting">{{ submitting ? 'Enregistrement...' : 'Enregistrer' }}</button>
        </div>
      </div>
    </div>

    <!-- Modal Confirmation suppression -->
    <div v-if="deleteConfirm" class="modal-overlay" @click.self="deleteConfirm = null">
      <div class="modal" style="max-width:400px">
        <div class="modal-header"><h3>Confirmer la suppression</h3></div>
        <div class="modal-body">
          <p>Supprimer l'entrée du {{ formatDate(deleteConfirm.date) }} ({{ formatKg(deleteConfirm.poids_frais_kg) }} kg, {{ deleteConfirm.fruit_type }}) ?</p>
          <p class="text-warning">Cette action est irréversible.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="deleteConfirm = null">Annuler</button>
          <button class="btn btn-danger" @click="executeDelete">Supprimer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useToastStore } from '../stores/toast'
import PageHeader from '../components/PageHeader.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const toast = useToastStore()

// API
const apiBase = '/api/production'

async function api(path, options = {}) {
  const res = await fetch(`${apiBase}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erreur serveur' }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

// State
const loading = ref(false)
const entries = ref([])
const stats = ref({ total_kg_frais: 0, total_dryers: 0, rendement_moyen: 0, par_fruit: {} })
const config = ref({ dryer_capacity_kg: 1500, fruit_types: ['mangue', 'ananas', 'goyave'] })
const saisons = ref([])

const filters = ref({ date_from: '', date_to: '', fruit_type: '', saison_id: '' })

const showConfig = ref(false)
const showForm = ref(false)
const submitting = ref(false)
const deleteConfirm = ref(null)

const form = ref({
  date: new Date().toISOString().split('T')[0],
  fruit_type: '',
  poids_frais_kg: null,
  nb_dryers: 1,
  saison_id: '',
  notes: ''
})

const configForm = ref({
  dryer_capacity_kg: 1500,
  fruit_types_str: 'mangue, ananas, goyave'
})

// Computed
const rendementClass = (r) => {
  if (r >= 0.7) return 'rendement-good'
  if (r >= 0.5) return 'rendement-warn'
  return 'rendement-low'
}

// Loaders
async function loadConfig() {
  try {
    const c = await api('/config')
    config.value = c
    configForm.value.dryer_capacity_kg = c.dryer_capacity_kg
    configForm.value.fruit_types_str = (c.fruit_types || []).join(', ')
  } catch (e) {
    toast.error('Erreur config: ' + e.message)
  }
}

async function loadSaisons() {
  try {
    const res = await fetch('/api/saisons')
    if (res.ok) saisons.value = await res.json()
  } catch {}
}

async function loadEntries() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filters.value.date_from) params.set('date_from', filters.value.date_from)
    if (filters.value.date_to) params.set('date_to', filters.value.date_to)
    if (filters.value.fruit_type) params.set('fruit_type', filters.value.fruit_type)
    if (filters.value.saison_id) params.set('saison_id', filters.value.saison_id)
    params.set('skip', '0')
    params.set('limit', '200')
    entries.value = await api(`/entries?${params.toString()}`)
  } catch (e) {
    toast.error('Erreur chargement: ' + e.message)
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    stats.value = await api('/stats')
  } catch (e) {
    toast.error('Erreur stats: ' + e.message)
  }
}

async function loadAll() {
  await Promise.all([loadConfig(), loadSaisons(), loadEntries(), loadStats()])
}

// Actions
async function saveConfig() {
  try {
    const fruitTypes = configForm.value.fruit_types_str.split(',').map(s => s.trim()).filter(Boolean)
    await api('/config', { method: 'PUT', body: JSON.stringify({ dryer_capacity_kg: configForm.value.dryer_capacity_kg, fruit_types: fruitTypes }) })
    toast.success('Configuration mise à jour')
    showConfig.value = false
    await Promise.all([loadConfig(), loadEntries(), loadStats()])
  } catch (e) {
    toast.error('Erreur: ' + e.message)
  }
}

async function submitForm() {
  if (!form.value.fruit_type || !form.value.poids_frais_kg) {
    toast.error('Remplissez les champs obligatoires')
    return
  }
  submitting.value = true
  try {
    await api('/entries', { method: 'POST', body: JSON.stringify(form.value) })
    toast.success('Entrée enregistrée')
    showForm.value = false
    form.value = { date: new Date().toISOString().split('T')[0], fruit_type: '', poids_frais_kg: null, nb_dryers: 1, saison_id: '', notes: '' }
    await Promise.all([loadEntries(), loadStats()])
  } catch (e) {
    toast.error('Erreur: ' + e.message)
  } finally {
    submitting.value = false
  }
}

function confirmDelete(entry) {
  deleteConfirm.value = entry
}

async function executeDelete() {
  if (!deleteConfirm.value) return
  try {
    await api(`/entries/${deleteConfirm.value.id}`, { method: 'DELETE' })
    toast.success('Entrée supprimée')
    deleteConfirm.value = null
    await Promise.all([loadEntries(), loadStats()])
  } catch (e) {
    toast.error('Erreur: ' + e.message)
  }
}

function formatKg(v) {
  return (v || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('fr-FR')
}

// Init
onMounted(loadAll)

// Watch filtres
watch(filters, loadEntries, { deep: true })
</script>

<style scoped>
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 8px; }
.kpi-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 20px; }
.kpi-label { font-size: 12px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.kpi-value { font-size: 28px; font-weight: 700; color: var(--dark); font-family: 'Source Serif 4', Georgia, serif; }

.fruit-badge { display: inline-block; padding: 2px 8px; border-radius: 99px; font-size: 11px; font-weight: 700; background: var(--primary-light); color: var(--primary); }
.rendement-badge { font-weight: 700; font-size: 13px; }
.rendement-good { color: var(--success); }
.rendement-warn { color: var(--warning); }
.rendement-low { color: var(--error); }

.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.4); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 20px; backdrop-filter: blur(2px); animation: fadeIn 0.2s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.modal { background: var(--card); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); width: 100%; max-height: 90vh; overflow-y: auto; animation: slideUp 0.25s var(--ease); }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--border); }
.modal-header h3 { font-size: 16px; font-weight: 600; color: var(--dark); }
.modal-close { background: none; border: none; font-size: 22px; color: var(--text-muted); cursor: pointer; line-height: 1; padding: 4px; }
.modal-close:hover { color: var(--text); }
.modal-body { padding: 20px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 20px; border-top: 1px solid var(--border); }

.text-warning { color: var(--warning); font-size: 13px; margin-top: 8px; }
</style>