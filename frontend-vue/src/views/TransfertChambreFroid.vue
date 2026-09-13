<template>
  <div class="page">
    <PageHeader title="Transfert Chambre Froide" subtitle="Envoyer les cartons conditionnés vers la chambre froide" />

    <LoadingSpinner v-if="loading" />
    <div v-else-if="lots.length === 0" class="empty anim-fade">
      <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
      <div class="empty-text">Aucun lot terminé en attente de transfert</div>
    </div>

    <div v-for="lot in lots" :key="lot.id" class="card anim-fade" style="margin-bottom:16px">
      <div class="card-header" style="margin-bottom:14px">
        <div style="display:flex;align-items:center;gap:10px">
          <strong>{{ lot.code_lot }}</strong>
          <span style="color:var(--text-secondary);font-size:13px">{{ lot.type_fruit || lot.produit?.nom }}</span>
          <StatusBadge :status="lot.statut_transfert || 'en_attente'" />
        </div>
      </div>

      <div v-if="lot.statut_transfert === 'valide'" class="transfert-ok">
        Transfert validé
      </div>

      <div v-else class="transfert-form">
        <div class="transfert-fluxes">
          <div v-for="flux in getFluxesForLot(lot)" :key="flux.key" class="transfert-flux" :class="{'has-error': (form[lot.id][flux.key + '_cartons']||0) > lot[flux.field]}">
            <div class="flux-info">
              <span class="flux-badge" :style="{background: flux.color}">{{ flux.label }}</span>
              <span>{{ lot[flux.field] }} cartons disponibles</span>
              <span v-if="(form[lot.id][flux.key + '_cartons']||0) > lot[flux.field]" class="field-error" style="margin-left:auto">Dépasse max {{ lot[flux.field] }}</span>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Cartons à transférer</label>
                <input type="number" v-model.number="form[lot.id][flux.key + '_cartons']" class="input" min="0" :max="lot[flux.field]" :placeholder="'max ' + lot[flux.field]" />
              </div>
              <div class="form-group">
                <label>Chambre froide</label>
                <select v-model="form[lot.id][flux.key + '_zone_id']" class="input">
                  <option disabled value="">Choisir chambre</option>
                  <option v-for="z in zones" :key="z.id" :value="z.id">{{ z.nom }}</option>
                </select>
              </div>
            </div>
          </div>
          <div v-if="getFluxesForLot(lot).length === 0" class="no-flux">
            Aucun carton à transférer pour ce lot
          </div>
        </div>

        <div class="form-row" style="margin-top:14px">
          <div class="form-group" style="flex:1">
            <label>Responsable</label>
            <input v-model="form[lot.id].responsable" class="input" placeholder="Nom" />
          </div>
          <div class="form-group" style="flex:2">
            <label>Notes</label>
            <input v-model="form[lot.id].notes" class="input" placeholder="Observations" />
          </div>
          <div class="form-group" style="flex:0">
            <label>&nbsp;</label>
            <button class="btn btn-primary" :disabled="!canSubmit(lot.id) || saving" @click="valider(lot)">
              {{ saving ? 'Envoi...' : 'Confirmer le transfert' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="demandes.length > 0" style="margin-top:24px">
      <h2 style="font-size:16px;font-weight:600;margin-bottom:12px">Demandes récentes</h2>
      <div v-for="d in demandes" :key="d.id" class="card anim-fade" style="margin-bottom:8px;padding:12px 16px">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <strong>{{ d.lot?.code_lot || d.lot_id }}</strong>
            <span style="margin-left:8px;font-size:12px;color:var(--text-muted)">{{ new Date(d.date_demande).toLocaleDateString() }}</span>
          </div>
          <StatusBadge :status="d.statut" />
        </div>
        <div style="margin-top:6px;font-size:12px;color:var(--text-muted)">
          <span v-for="l in d.lignes" :key="l.id" style="margin-right:12px">
            {{ l.type_flux }}: {{ l.nb_cartons }} → CF{{ l.zone_id }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLots, getZonesStock, creerDemandeTransfert, validerDemandeTransfert, getDemandesTransfert } from '../api'
import { useToastStore } from '../stores/toast'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import StatusBadge from '../components/StatusBadge.vue'
import PageHeader from '../components/PageHeader.vue'
import { toCanonical, CONDITIONNE, EN_STOCK } from '../utils/statuses'

const lots = ref([])
const demandes = ref([])
const zones = ref([])
const loading = ref(true)
const saving = ref(false)
const toast = useToastStore()
const form = reactive({})

const fluxConfig = [
  { key: 'export', label: 'Export', field: 'export_cartons', color: '#00853E' },
  { key: 'local', label: 'Local', field: 'local_cartons', color: '#0B2E20' },
  { key: 'fitini_fe', label: 'Fitini Fê', field: 'fitini_fe_cartons', color: '#8B5CF6' },
  { key: 'dechets', label: 'Déchets', field: 'dechets_cartons', color: '#ef4444' },
  { key: 'rhum', label: 'Rhum', field: 'rhum_cartons', color: '#d97706' },
]
function getFluxesForLot(lot) {
  return fluxConfig.filter(f => (lot[f.field] || 0) > 0)
}
function initForm(lotId, lot) {
  const init = { responsable: '', notes: '' }
  const defaultZone = zones.value[0]?.id || 1
  for (const f of fluxConfig) {
    init[f.key + '_cartons'] = lot[f.field] || 0
    init[f.key + '_zone_id'] = defaultZone
  }
  form[lotId] = reactive(init)
}

function canSubmit(lotId) {
  const d = form[lotId]
  if (!d || !d.responsable?.trim()) return false
  return fluxConfig.some(f => (d[f.key + '_cartons'] || 0) > 0)
}

async function load() {
  loading.value = true
  try {
    const [raw, z] = await Promise.all([getLots(), getZonesStock()])
    zones.value = z.filter(z => z.actif)
    lots.value = raw.filter(l => toCanonical(l.statut) === CONDITIONNE)
    for (const lot of lots.value) {
      initForm(lot.id, lot)
    }
    demandes.value = await getDemandesTransfert()
  } finally { loading.value = false }
}

async function valider(lot) {
  saving.value = true
  try {
    const d = form[lot.id]
    if (!d.responsable?.trim()) { toast.warning('Responsable requis'); return }
    const lignes = []
    for (const f of fluxConfig) {
      const nb = d[f.key + '_cartons'] || 0
      if (nb > 0) {
        if (nb > (lot[f.field] || 0)) { toast.error(`${f.label}: ${nb} dépasse ${lot[f.field]}`); return }
        lignes.push({ type_flux: f.key, nb_cartons: nb, zone_id: d[f.key + '_zone_id'] })
      }
    }
    if (!lignes.length) { toast.warning('Saisir au moins un flux'); return }
    const demande = await creerDemandeTransfert({
      lot_id: lot.id, responsable: d.responsable.trim(), notes: d.notes, lignes,
    })
    await validerDemandeTransfert(demande.id)
    toast.success(`Transfert confirmé pour ${lot.code_lot}`)
    await load()
  } catch(e) {
    toast.error(e.response?.data?.detail || e.message)
  } finally { saving.value = false }
}

onMounted(load)
</script>

<style scoped>
.transfert-fluxes { margin-bottom: 14px; }
.transfert-flux { padding: 12px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); margin-bottom: 10px; }
.flux-info { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-size: 13px; }
.flux-badge { padding: 2px 8px; border-radius: 99px; color: white; font-size: 11px; font-weight: 600; }
.transfert-ok { padding: 16px; background: var(--success-light); border: 1px solid var(--success); border-radius: var(--radius-sm); text-align: center; font-weight: 600; color: var(--success); }
.no-flux { padding: 12px; text-align: center; color: var(--text-muted); font-size: 13px; }
</style>
