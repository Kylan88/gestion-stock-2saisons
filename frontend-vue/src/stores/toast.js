import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({ toasts: [], nextId: 0 }),
  actions: {
    add(message, type = 'info', duration = 4000) {
      const id = this.nextId++
      this.toasts.push({ id, message, type })
      if (duration > 0) {
        setTimeout(() => this.remove(id), duration)
      }
      return id
    },
    success(msg, duration) { return this.add(msg, 'success', duration) },
    error(msg, duration) { return this.add(msg, 'error', duration ?? 6000) },
    warning(msg, duration) { return this.add(msg, 'warning', duration) },
    info(msg, duration) { return this.add(msg, 'info', duration) },
    remove(id) {
      const idx = this.toasts.findIndex(t => t.id === id)
      if (idx !== -1) this.toasts.splice(idx, 1)
    },
  },
})
