<template>
  <span class="badge" :class="badgeClass">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'
import { labelFor, classFor } from '../utils/statuses'

const props = defineProps({ status: { type: String, default: '' } })

const badgeClass = computed(() => classFor(props.status))
const label = computed(() => labelFor(props.status))
</script>
