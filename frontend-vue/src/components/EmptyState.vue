<template>
  <div class="empty anim-fade">
    <div class="empty-icon">{{ icon }}</div>
    <div class="empty-text">{{ text }}</div>
    <p v-if="subtext" style="margin-top:6px;font-size:13px;color:var(--text-muted)">{{ subtext }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({ icon: { type: String, default: '—' }, text: { type: String, default: 'Aucune donnée' }, subtext: String })
</script>
