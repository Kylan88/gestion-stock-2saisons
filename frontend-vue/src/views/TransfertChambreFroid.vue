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
          <div v-if="lot.local_cartons > 0" class="transfert-flux">
            <div class="flux-info">
              <span class="flux-badge" style="background:#0F766E">Local</span>
              <span>{{ lot.local_cartons }} cartons disponibles</span>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Cartons à transférer</label>
                <input type="number" v-model.number="form[lot.id].local_cartons" class="input" min="0" :max="lot.local_cartons" />
              </div>
              <div class="form-group">
                <label>Chambre froide</label>
                <select v-model="form[lot.id].local_zone_id" class="input">
                  <option v-for="z in zones" :key="z.id" :value="z.id">{{ z.nom }}</option>
                </select>
              </div>
            </div>
          </div>

          <div v-if="lot.fitini_fê_cartons > 0" class="transfert-flux">
            <div class="flux-info">
              <span class="flux-badge" style="background:#8B5CF6">Fitini Fê</span>
              <span>{{ lot.fitini_fê_cartons }} cartons disponibles</span>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Cartons à transférer</label>
                <input type="number" v-model.number="form[lot.id].fitini_cartons" class="input" min="0" :max="lot.fitini_fê_cartons" />
              </div>
              <div class="form-group">
                <label>Chambre froide</label>
                <select v-model="form[lot.id].fitini_zone_id" class="input">
                  <option v-for="z in zones" :key="z.id" :value="z.id">{{ z.nom }}</option>
                </select>
              </div>
            </div>
          </div>

          <div v-if="lot.local_cartons === 0 && lot.fitini_fê_cartons === 0" class="no-flux">
            Aucun carton local ou fitini fê à transférer
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

const lots = ref([])
const demandes = ref([])
const zones = ref([])
const loading = ref(true)
const saving = ref(false)
const toast = useToastStore()
const form = reactive({})

function initForm(lotId, lot) {
  form[lotId] = reactive({
    local_cartons: 0, local_zone_id: 1,
    fitini_cartons: 0, fitini_zone_id: 1,
    responsable: '', notes: '',
  })
}

function canSubmit(lotId) {
  const d = form[lotId]
  if (!d) return false
  return (d.local_cartons > 0 || d.fitini_cartons > 0)
}

async function load() {
  loading.value = true
  try {
    const [raw, z] = await Promise.all([getLots(), getZonesStock()])
    zones.value = z.filter(z => z.actif)
    lots.value = raw.filter(l => l.statut === 'terminé')
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
    const lignes = []
    if (d.local_cartons > 0) lignes.push({ type_flux: 'local', nb_cartons: d.local_cartons, zone_id: d.local_zone_id })
    if (d.fitini_cartons > 0) lignes.push({ type_flux: 'fitini_fê', nb_cartons: d.fitini_cartons, zone_id: d.fitini_zone_id })

    const demande = await creerDemandeTransfert({
      lot_id: lot.id, responsable: d.responsable, notes: d.notes, lignes,
    })
    await validerDemandeTransfert(demande.id)
    toast.success(`Transfert confirmé pour ${lot.code_lot}`)
    await load()
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
