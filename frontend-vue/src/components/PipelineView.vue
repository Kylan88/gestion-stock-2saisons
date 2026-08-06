<template>
  <div class="pipeline">
    <div v-for="col in columns" :key="col.key" class="pipeline-col">
      <div class="col-header" :style="{ borderColor: col.color }">
        <span class="col-title">{{ col.label }}</span>
        <span class="col-count" :style="{ background: col.color + '20', color: col.color }">{{ col.lots.length }}</span>
      </div>
      <div class="col-body">
        <div v-if="col.lots.length === 0" class="col-empty">Aucun lot</div>
        <div v-for="lot in col.lots" :key="lot.id" class="lot-card" @click="$emit('selectLot', lot)">
          <div class="lot-top">
            <strong class="lot-code">{{ lot.code_lot }}</strong>
            <span class="lot-poids">{{ lot.poids_frais }} kg</span>
          </div>
          <div class="lot-mid">
            <span class="lot-fruit">{{ lot.type_fruit || lot.produit?.nom || '—' }}</span>
            <span v-if="lot.rendement_global" class="lot-rdt">{{ lot.rendement_global }}%</span>
          </div>
          <div v-if="col.key === 'reception'" class="lot-action">
            <button class="btn btn-sm btn-primary" @click.stop="$emit('avancer', lot.id, 'en_musserie')">→ Musserie</button>
          </div>
          <div v-else-if="col.key === 'en_musserie'" class="lot-action">
            <button class="btn btn-sm btn-outline" @click.stop="$emit('goMusserie')">Ouvrir</button>
          </div>
          <div v-else-if="col.key === 'conditionne'" class="lot-action">
            <button class="btn btn-sm btn-outline" @click.stop="$emit('goTransfert')">Transférer CF</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { toCanonical } from '../utils/statuses'

const COLS = [
  { key: 'reception', label: 'Réception', color: '#165B3D' },
  { key: 'en_musserie', label: 'Musserie', color: '#F59E0B' },
  { key: 'en_production', label: 'Production', color: '#3B82F6' },
  { key: 'conditionne', label: 'Conditionnement', color: '#8B5CF6' },
  { key: 'en_stock', label: 'Stock', color: '#22C55E' },
]

const props = defineProps({
  lots: { type: Array, default: () => [] },
})

defineEmits(['selectLot', 'avancer', 'goMusserie', 'goTransfert'])

const columns = computed(() => {
  return COLS.map(col => ({
    ...col,
    lots: props.lots.filter(l => toCanonical(l.statut) === col.key),
  }))
})
</script>

<style scoped>
.pipeline { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; }
.pipeline-col {
  flex: 1; min-width: 200px; max-width: 260px;
  background: var(--surface); border-radius: var(--radius-md);
  display: flex; flex-direction: column;
}
.col-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; border-left: 3px solid;
  background: white; border-radius: var(--radius-md) var(--radius-md) 0 0;
}
.col-title { font-size: 13px; font-weight: 600; color: var(--dark); }
.col-count {
  padding: 2px 8px; border-radius: 99px;
  font-size: 11px; font-weight: 700;
}
.col-body { padding: 8px; display: flex; flex-direction: column; gap: 8px; flex: 1; overflow-y: auto; max-height: 420px; }
.col-empty { text-align: center; padding: 20px; color: var(--text-muted); font-size: 12px; }

.lot-card {
  background: white; border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 12px;
  cursor: pointer; transition: all 0.15s;
}
.lot-card:hover { box-shadow: var(--shadow-sm); border-color: var(--primary-light); }
.lot-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.lot-code { font-size: 13px; color: var(--dark); }
.lot-poids { font-size: 11px; color: var(--text-muted); }
.lot-mid { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.lot-fruit { font-size: 12px; color: var(--text-secondary); }
.lot-rdt { font-size: 11px; font-weight: 600; color: var(--primary); }
.lot-action { display: flex; justify-content: flex-end; }
</style>
