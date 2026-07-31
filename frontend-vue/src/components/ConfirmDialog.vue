<template>
  <Teleport to="body">
    <div v-if="show" class="confirm-overlay" @click.self="$emit('cancel')">
      <div class="confirm-dialog anim-slide" role="dialog" aria-modal="true" :aria-label="title">
        <div class="confirm-icon" :class="'confirm-' + variant">
          <svg v-if="variant === 'danger'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          <svg v-else-if="variant === 'warning'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        </div>
        <div class="confirm-body">
          <h3 class="confirm-title">{{ title }}</h3>
          <p class="confirm-message">{{ message }}</p>
        </div>
        <div class="confirm-actions">
          <button class="btn btn-outline btn-sm" @click="$emit('cancel')">{{ cancelText }}</button>
          <button class="btn btn-sm" :class="variant === 'danger' ? 'btn-danger' : 'btn-primary'" @click="$emit('confirm')">
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: 'Confirmer' },
  message: { type: String, default: 'Êtes-vous sûr ?' },
  confirmText: { type: String, default: 'Confirmer' },
  cancelText: { type: String, default: 'Annuler' },
  variant: { type: String, default: 'warning' },
})
defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-overlay {
  position: fixed; inset: 0; z-index: 9998;
  background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(2px);
  display: flex; align-items: center; justify-content: center;
  animation: fadeIn 0.15s ease;
}
.confirm-dialog {
  background: white; border-radius: var(--radius-md); padding: 28px;
  max-width: 400px; width: 90%; box-shadow: var(--shadow-lg);
  display: flex; flex-direction: column; align-items: center; text-align: center; gap: 16px;
}
.confirm-icon {
  width: 48px; height: 48px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.confirm-danger { background: #FEE2E2; color: var(--error); }
.confirm-warning { background: #FEF3C7; color: #D97706; }
.confirm-info { background: #EFF6FF; color: var(--info); }
.confirm-title { font-size: 16px; font-weight: 600; color: var(--dark); }
.confirm-message { font-size: 13px; color: var(--text-secondary); margin: 0; }
.confirm-actions { display: flex; gap: 10px; margin-top: 4px; }
</style>
