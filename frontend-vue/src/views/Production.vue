<template>
  <div class="page">
    <PageHeader title="Production" subtitle="Rendement par dryer — frais total (sans tri) → pulpe capacité (6,25 kg × claies)">
      <template #actions>
        <button class="btn btn-primary" @click="showConfig = true">Config</button>
      </template>
    </PageHeader>

    <!-- KPIs -->
    <div class="kpi-grid anim-fade">
      <div class="kpi-card">
        <div class="kpi-label">Total kg frais <small style="font-weight:400;text-transform:none;letter-spacing:0">(hors tri)</small></div>
        <div class="kpi-value">{{ formatKg(stats.total_kg_frais) }}</div>
        <div class="kpi-sub">fruits_murs − lavage − production − retour (tri exclu)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total pulpe capacité</div>
        <div class="kpi-value">{{ formatKg(stats.total_pulpe_capacity_kg) }}</div>
        <div class="kpi-sub">D1 1575 kg (6×42×6,25) · D2 1500 kg (12×20×6,25)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Dryers remplis</div>
        <div class="kpi-value">{{ stats.total_dryers }}</div>
        <div class="kpi-sub">1 entrée = 1 dryer</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Rendement moyen</div>
        <div class="kpi-value">{{ (stats.rendement_global * 100).toFixed(1) }}%</div>
        <div class="kpi-sub">capacité / frais total</div>
      </div>
    </div>

    <!-- Filtres -->
    <div class="filters-bar card anim-fade">
      <div class="filter-item">
        <label><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> Date début</label>
        <input type="date" v-model="filters.date_from" class="input" @change="loadEntries" />
      </div>
      <div class="filter-item">
        <label><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> Date fin</label>
        <input type="date" v-model="filters.date_to" class="input" @change="loadEntries" />
      </div>
      <div class="filter-item">
        <label><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 13c0 3.87 3.13 7 7 7s7-3.13 7-7-3.13-7-7-7-7 3.13-7 7z"/><path d="M9 13c0 2.21 1.79 4 4 4s4-1.79 4-4-1.79-4-4-4-4 1.79-4 4z"/></svg> Type fruit</label>
        <select v-model="filters.fruit_type" class="input" @change="loadEntries">
          <option value="">Tous fruits</option>
          <option v-for="ft in config.fruit_types" :key="ft" :value="ft">{{ ft }}</option>
        </select>
      </div>
      <button v-if="filters.date_from || filters.date_to || filters.fruit_type" class="btn btn-ghost btn-sm" style="align-self:flex-end" @click="filters={date_from:'',date_to:'',fruit_type:''}; loadEntries()">Effacer</button>
    </div>

    <!-- Tableau par dryer -->
    <div class="card anim-fade" style="margin-top:16px">
      <LoadingSpinner v-if="loading" />
      <div v-else-if="entries.length === 0" class="empty">
        <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
        <div class="empty-text">Aucune production</div>
        <div class="empty-sub">Termine une musserie (avec dryer 1 ou 2) pour voir le rendement</div>
      </div>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Lot</th>
              <th>Dryer</th>
              <th>Fruit</th>
              <th>Frais total*</th>
              <th>Pulpe</th>
              <th>Rendement</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="e in entries" :key="e.lot_id + '_' + e.date + '_D' + e.dryer">
              <tr class="row-clickable" @click="expandedKey === e.lot_id + '_' + e.date + '_D' + e.dryer ? expandedKey='' : expandedKey=e.lot_id + '_' + e.date + '_D' + e.dryer" style="cursor:pointer">
                <td>{{ formatDate(e.date) }}</td>
                <td><strong>{{ e.code_lot }}</strong></td>
                <td><span class="dryer-badge" :class="e.dryer===1?'dryer1':'dryer2'">D{{ e.dryer }} · {{ e.pulpe_capacity_kg===1575 ? '6×42' : '12×20' }}</span></td>
                <td><span class="fruit-badge">{{ e.fruit_type }}</span></td>
                <td style="font-weight:700">{{ formatKg(e.frais_total_kg) }}</td>
                <td style="font-weight:700">{{ formatKg(e.pulpe_capacity_kg) }}</td>
                <td><span class="rendement-badge" :class="rendementClass(e.rendement)">{{ (e.rendement * 100).toFixed(1) }}%</span></td>
                <td style="font-size:11px;color:var(--text-muted)">{{ expandedKey === e.lot_id + '_' + e.date + '_D' + e.dryer ? '▲' : '▼' }}</td>
              </tr>
              <tr v-if="expandedKey === e.lot_id + '_' + e.date + '_D' + e.dryer" class="detail-row">
                <td colspan="8" style="background:var(--surface);padding:12px 16px">
                  <div style="display:flex;gap:16px;flex-wrap:wrap;font-size:12px">
                    <span><strong>Fruits mûrs:</strong> {{ formatKg(e.fruits_murs_kg) }}</span>
                    <span>− Lavage {{ formatKg(e.dechets_lavage_kg) }}</span>
                    <span>− Production {{ formatKg(e.dechets_production_kg) }}</span>
                    <span>− Retour {{ formatKg(e.retour_non_mur_kg) }}</span>
                    <span>= <strong>Frais net {{ formatKg(e.frais_total_kg) }}</strong> → Pulpe {{ formatKg(e.pulpe_capacity_kg) }}</span>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
        <div style="font-size:11px;color:var(--text-muted);margin-top:8px">* Frais total = fruits_murs − lavage − production − retour (tri exclu).</div>
      </div>
    </div>

    <!-- Par dryer -->
    <div v-if="stats.par_dryer && Object.keys(stats.par_dryer).length" class="card anim-fade" style="margin-top:16px">
      <div class="card-header"><strong>Par dryer</strong> <span style="font-size:11px;color:var(--text-muted)">capacité fixe : D1 1575 kg (6×42×6,25) · D2 1500 kg (12×20×6,25)</span></div>
      <div class="table-wrap">
        <table class="table">
          <thead><tr><th>Dryer</th><th>Entrées</th><th>Capacité unitaire</th><th>Kg frais *</th><th>Pulpe capacité</th><th>Rendement</th></tr></thead>
          <tbody>
            <tr v-for="(d,k) in stats.par_dryer" :key="k">
              <td><span class="dryer-badge" :class="d.dryer===1?'dryer1':'dryer2'">D{{ d.dryer }}</span></td>
              <td>{{ d.entries }}</td>
              <td>{{ formatKg(d.capacity_kg) }}</td>
              <td>{{ formatKg(d.kg_frais) }}</td>
              <td>{{ formatKg(d.pulpe_capacity_kg) }}</td>
              <td><span class="rendement-badge" :class="rendementClass(d.rendement)">{{ (d.rendement*100).toFixed(1) }}%</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Par fruit -->
    <div v-if="Object.keys(stats.par_fruit).length" class="card anim-fade" style="margin-top:16px">
      <div class="card-header"><strong>Par type de fruit</strong></div>
      <div class="table-wrap">
        <table class="table">
          <thead><tr><th>Fruit</th><th>Dryers</th><th>Kg frais *</th><th>Pulpe</th><th>Rendement</th></tr></thead>
          <tbody>
            <tr v-for="(f,fruit) in stats.par_fruit" :key="fruit">
              <td><span class="fruit-badge">{{ fruit }}</span></td>
              <td>{{ f.dryers }}</td>
              <td>{{ formatKg(f.kg_frais) }}</td>
              <td>{{ formatKg(f.pulpe_capacity_kg) }}</td>
              <td><span class="rendement-badge" :class="rendementClass(f.rendement)">{{ (f.rendement*100).toFixed(1) }}%</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Par lot -->
    <div v-if="Object.keys(stats.par_lot).length" class="card anim-fade" style="margin-top:16px">
      <div class="card-header"><strong>Par lot (cumulé)</strong></div>
      <div class="table-wrap">
        <table class="table">
          <thead><tr><th>Lot</th><th>Fruit</th><th>Dryers</th><th>Kg frais *</th><th>Pulpe capacité</th><th>Rendement global</th></tr></thead>
          <tbody>
            <tr v-for="(l,k) in stats.par_lot" :key="k">
              <td><strong>{{ l.code_lot }}</strong></td>
              <td><span class="fruit-badge">{{ l.fruit_type }}</span></td>
              <td>{{ l.dryers }}</td>
              <td>{{ formatKg(l.kg_frais) }}</td>
              <td>{{ formatKg(l.pulpe_capacity_kg) }}</td>
              <td><span class="rendement-badge" :class="rendementClass(l.rendement_global)">{{ (l.rendement_global*100).toFixed(1) }}%</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Config -->
    <div v-if="showConfig" class="modal-overlay" @click.self="showConfig=false">
      <div class="modal" style="max-width:520px">
        <div class="modal-header"><h3>Configuration Production</h3><button class="modal-close" @click="showConfig=false">×</button></div>
        <div class="modal-body" style="display:flex;flex-direction:column;gap:16px">
          <div class="form-group">
            <label>Dryer 1 capacité (kg) — 6 chariots × 42 claies × 6,25</label>
            <input type="number" step="0.1" min="1" v-model.number="configForm.dryer1_capacity_kg" class="form-input" />
            <div class="field-hint">Défaut 1575 kg</div>
          </div>
          <div class="form-group">
            <label>Dryer 2 capacité (kg) — 12 chariots × 20 claies × 6,25</label>
            <input type="number" step="0.1" min="1" v-model.number="configForm.dryer2_capacity_kg" class="form-input" />
            <div class="field-hint">Défaut 1500 kg</div>
          </div>
          <div class="form-group">
            <label>Types de fruits (virgule)</label>
            <input type="text" v-model="configForm.fruit_types_str" class="form-input" placeholder="mangue kent, mangue Brooks, ananas, banane" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showConfig=false">Annuler</button>
          <button class="btn btn-primary" @click="saveConfig">Enregistrer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useToastStore } from '../stores/toast'
import PageHeader from '../components/PageHeader.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
const toast = useToastStore()
const apiBase = '/api/production'
async function api(path, options={}) {
  const res = await fetch(`${apiBase}${path}`, { headers:{'Content-Type':'application/json', ...options.headers}, ...options })
  if(!res.ok){ const err=await res.json().catch(()=>({detail:'Erreur'})); throw new Error(err.detail||`HTTP ${res.status}`)}
  return res.json()
}
const loading=ref(false)
const entries=ref([])
const expandedKey=ref('')
const stats=ref({total_kg_frais:0,total_pulpe_kg:0,total_pulpe_capacity_kg:0,total_dryers:0,rendement_global:0,par_fruit:{},par_lot:{},par_dryer:{}})
const config=ref({dryer_capacity_kg:1500,dryer1_capacity_kg:1575,dryer2_capacity_kg:1500,fruit_types:['mangue kent','mangue Brooks','ananas','banane']})
const filters=ref({date_from:'',date_to:'',fruit_type:''})
const showConfig=ref(false)
const configForm=ref({dryer1_capacity_kg:1575,dryer2_capacity_kg:1500,fruit_types_str:'mangue kent, mangue Brooks, ananas, banane'})
const rendementClass=r=> r>=0.6 ? 'rendement-good' : r>=0.45 ? 'rendement-warn' : 'rendement-low'
async function loadConfig(){
  try{ const c=await api('/config'); config.value=c; configForm.value.dryer1_capacity_kg=c.dryer1_capacity_kg??1575; configForm.value.dryer2_capacity_kg=c.dryer2_capacity_kg??1500; configForm.value.fruit_types_str=(c.fruit_types||[]).join(', ') }catch(e){ toast.error('Config: '+e.message)}
}
async function loadEntries(){
  loading.value=true
  try{
    const p=new URLSearchParams()
    if(filters.value.date_from) p.set('date_from',filters.value.date_from)
    if(filters.value.date_to) p.set('date_to',filters.value.date_to)
    if(filters.value.fruit_type) p.set('fruit_type',filters.value.fruit_type)
    p.set('skip','0'); p.set('limit','200')
    entries.value=await api(`/entries?${p}`)
  }catch(e){ toast.error(e.message)} finally{ loading.value=false}
}
async function loadStats(){ try{ stats.value=await api('/stats')}catch(e){ toast.error(e.message)}}
async function loadAll(){ await Promise.all([loadConfig(),loadEntries(),loadStats()])}
async function saveConfig(){
  try{
    const fruitTypes=configForm.value.fruit_types_str.split(',').map(s=>s.trim()).filter(Boolean)
    await api('/config',{method:'PUT', body: JSON.stringify({dryer1_capacity_kg:configForm.value.dryer1_capacity_kg, dryer2_capacity_kg:configForm.value.dryer2_capacity_kg, fruit_types:fruitTypes})})
    toast.success('Config mise à jour'); showConfig.value=false; await loadAll()
  }catch(e){ toast.error(e.message)}
}
function formatKg(v){ return (v||0).toLocaleString('fr-FR',{minimumFractionDigits:2, maximumFractionDigits:2})}
function formatDate(d){ return new Date(d).toLocaleDateString('fr-FR')}
onMounted(loadAll)
watch(filters,loadEntries,{deep:true})
</script>

<style scoped>
.kpi-grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:16px; margin-bottom:8px}
.kpi-card{ background:var(--card); border:1px solid var(--border); border-radius:var(--radius-md); padding:18px}
.kpi-label{ font-size:11px; color:var(--text-muted); font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px}
.kpi-value{ font-size:26px; font-weight:700; color:var(--dark); font-family:'Source Serif 4',Georgia,serif}
.kpi-sub{ font-size:11px; color:var(--text-muted); margin-top:4px}
.row-clickable:hover{ background:var(--surface)}
.filters-bar{ display:flex; gap:16px; flex-wrap:wrap; align-items:flex-end; padding:16px 18px; background:var(--surface); border:1px solid var(--border-light); margin-top:16px}
.filter-item{ flex:1; min-width:160px; display:flex; flex-direction:column; gap:6px}
.filter-item label{ display:flex; align-items:center; gap:6px; font-size:10px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em; margin:0}
.filter-item .input{ min-height:38px; background:white}
.fruit-badge{ display:inline-block; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:700; background:var(--primary-light); color:var(--primary)}
.dryer-badge{ display:inline-flex; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:800}
.dryer1{ background:#DBEAFE; color:#1E40AF} .dryer2{ background:#FEF3C7; color:#92400E}
.rendement-badge{ font-weight:700; font-size:13px} .rendement-good{ color:var(--success)} .rendement-warn{ color:var(--warning)} .rendement-low{ color:var(--error)}
.modal-overlay{ position:fixed; inset:0; background:rgba(15,23,42,0.4); display:flex; align-items:center; justify-content:center; z-index:50; padding:20px; backdrop-filter:blur(2px)}
.modal{ background:var(--card); border-radius:var(--radius-lg); box-shadow:var(--shadow-lg); width:100%; max-height:90vh; overflow-y:auto}
.modal-header{ display:flex; align-items:center; justify-content:space-between; padding:16px 20px; border-bottom:1px solid var(--border)}
.modal-header h3{ font-size:16px; font-weight:600}
.modal-close{ background:none; border:none; font-size:22px; color:var(--text-muted); cursor:pointer}
.modal-body{ padding:20px} .modal-footer{ display:flex; justify-content:flex-end; gap:10px; padding:16px 20px; border-top:1px solid var(--border)}
</style>
