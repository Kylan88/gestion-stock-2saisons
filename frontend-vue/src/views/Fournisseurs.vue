<template>
  <div class="page">
    <PageHeader title="Fournisseurs" subtitle="Annuaire alimenté par les réceptions — les fournisseurs sont créés via les lots" />

    <LoadingSpinner v-if="loading" />
    <template v-else>
      <EmptyState v-if="fournisseurs.length === 0" text="Aucun fournisseur" subtext="Enregistrez un lot en réception avec un nom de fournisseur">
        <router-link to="/reception" class="btn btn-outline">+ Nouveau Lot</router-link>
      </EmptyState>

      <div v-else>
        <div class="filters">
          <input v-model="recherche" class="input" placeholder="Rechercher un fournisseur..." style="max-width:260px" />
        </div>
        <div class="table-wrap anim-fade">
          <table>
            <thead><tr><th>Nom</th><th>Lots</th><th>Poids total</th><th>Dernière réception</th></tr></thead>
            <tbody>
              <tr v-for="f in paginatedFournisseurs" :key="f.nom">
                <td><strong>{{ f.nom }}</strong></td>
                <td>{{ f.nb_lots }}</td>
                <td>{{ formatKg(f.poids_total) }} kg</td>
                <td>{{ f.derniere_reception || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="totalPages > 1" class="pagination">
          <button class="btn btn-ghost btn-sm" :disabled="page === 1" @click="page--">←</button>
          <span class="page-info">{{ page }} / {{ totalPages }}</span>
          <button class="btn btn-ghost btn-sm" :disabled="page === totalPages" @click="page++">→</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getLots } from '../api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import PageHeader from '../components/PageHeader.vue'
import EmptyState from '../components/EmptyState.vue'

const fournisseurs = ref([])
const loading = ref(true)
const recherche = ref('')
const page = ref(1)
const pageSize = 15

function formatKg(v) { return Math.round(v || 0).toLocaleString('fr-FR') }

const filteredFournisseurs = computed(() => {
  if (!recherche.value) return fournisseurs.value
  const q = recherche.value.toLowerCase()
  return fournisseurs.value.filter(f => f.nom.toLowerCase().includes(q))
})
const totalPages = computed(() => Math.ceil(filteredFournisseurs.value.length / pageSize))
const paginatedFournisseurs = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredFournisseurs.value.slice(start, start + pageSize)
})

async function load() {
  loading.value = true
  try {
    // Regroupe les noms saisis en réception (fournisseur_nom des lots)
    const lots = await getLots()
    const map = new Map()
    for (const lot of (lots || [])) {
      const nom = (lot.fournisseur_nom || '').trim()
      if (!nom) continue
      if (!map.has(nom)) map.set(nom, { nom, nb_lots: 0, poids_total: 0, derniere_reception: '' })
      const e = map.get(nom)
      e.nb_lots += 1
      e.poids_total += Number(lot.poids_frais || 0)
      const d = (lot.date_reception || '').slice(0, 10)
      if (d && d > e.derniere_reception) e.derniere_reception = d
    }
    fournisseurs.value = [...map.values()].sort((a, b) => a.nom.localeCompare(b.nom, 'fr'))
  } finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.filters { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.pagination { display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 16px; }
.page-info { font-size: 13px; color: var(--text-secondary); }
</style>
