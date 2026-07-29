<template>
  <Teleport to="body">
    <div class="toast-container">
      <div v-for="t in store.toasts" :key="t.id" class="toast" :class="'toast-' + t.type">
        <span>{{ t.message }}</span>
        <button class="toast-close" @click="store.remove(t.id)">×</button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useToastStore } from '../stores/toast'
const store = useToastStore()
</script>
