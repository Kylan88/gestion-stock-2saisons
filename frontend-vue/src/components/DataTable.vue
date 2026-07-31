<template>
  <div>
    <div v-if="searchable" class="filters">
      <input v-model="search" class="input" :placeholder="searchPlaceholder" style="max-width:260px" />
    </div>
    <div v-if="filteredRows.length === 0" class="empty anim-fade">
      <div class="empty-icon" style="font-size:28px;font-weight:300;color:var(--border)">—</div>
      <div class="empty-text">{{ emptyText }}</div>
    </div>
    <template v-else>
      <div class="table-wrap anim-fade">
        <table>
          <thead>
            <tr>
              <th v-for="col in columns" :key="col.key" :style="col.sortable !== false ? 'cursor:pointer;user-select:none' : ''" @click="col.sortable !== false && toggleSort(col.key)">
                {{ col.label }}
                <span v-if="sortKey === col.key" class="sort-icon">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in paginatedRows" :key="row.id" :class="{ 'clickable-row': $attrs.onRowclick }" @click="$emit('rowclick', row)">
              <slot name="row" :row="row" />
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="totalPages > 1" class="pagination">
        <button class="btn btn-ghost btn-sm" :disabled="page === 1" @click="page--">←</button>
        <span class="page-info">{{ page }} / {{ totalPages }}</span>
        <button class="btn btn-ghost btn-sm" :disabled="page === totalPages" @click="page++">→</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  rows: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
  pageSize: { type: Number, default: 15 },
  searchable: { type: Boolean, default: false },
  searchPlaceholder: { type: String, default: 'Rechercher...' },
  emptyText: { type: String, default: 'Aucune donnée' },
  searchFields: { type: Array, default: () => [] },
})

defineEmits(['rowclick'])

const search = ref('')
const sortKey = ref('')
const sortDir = ref('asc')
const page = ref(1)

watch(() => props.rows, () => { page.value = 1 })

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

const filteredRows = computed(() => {
  let result = [...props.rows]
  if (search.value && props.searchFields.length) {
    const q = search.value.toLowerCase()
    result = result.filter(row =>
      props.searchFields.some(f => String(row[f] || '').toLowerCase().includes(q))
    )
  }
  if (sortKey.value) {
    result.sort((a, b) => {
      const va = a[sortKey.value] ?? ''
      const vb = b[sortKey.value] ?? ''
      const cmp = String(va).localeCompare(String(vb), 'fr', { numeric: true })
      return sortDir.value === 'asc' ? cmp : -cmp
    })
  }
  return result
})

const totalPages = computed(() => Math.ceil(filteredRows.value.length / props.pageSize))
const paginatedRows = computed(() => {
  const start = (page.value - 1) * props.pageSize
  return filteredRows.value.slice(start, start + props.pageSize)
})
</script>

<style scoped>
.pagination { display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 16px; }
.page-info { font-size: 13px; color: var(--text-secondary); }
.sort-icon { font-size: 10px; margin-left: 4px; color: var(--primary); }
.clickable-row { cursor: pointer; }
</style>
