<template>
  <span class="badge" :class="badgeClass">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ status: { type: String, default: '' } })

const map = {
  'réception': 'badge-primary', 'en musserie': 'badge-warning',
  'en production': 'badge-info', 'en conditionnement': 'badge-primary',
  'en stock': 'badge-success', 'expédié': 'badge-secondary', 'périmé': 'badge-error',
  'terminé': 'badge-success', 'en_cours': 'badge-warning',
  'en_attente': 'badge-muted', 'en cours': 'badge-warning',
  'disponible': 'badge-success', 'en_marche': 'badge-warning',
  'en_panne': 'badge-error', 'rupture': 'badge-error', 'stock bas': 'badge-warning',
}

const badgeClass = computed(() => map[props.status] || 'badge-muted')
const label = computed(() => props.status.replace(/_/g, ' '))
</script>
