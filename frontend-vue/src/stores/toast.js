import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({ toasts: [], nextId: 0 }),
  actions: {
    add(message, type = 'info', duration = 4000) {
      const id = this.nextId++
      // newestOnTop + limit 3 comme 2saisons-app
      this.toasts.unshift({ id, message, type })
      if (this.toasts.length > 3) this.toasts.pop()
      if (duration > 0) {
        setTimeout(() => this.remove(id), duration)
      }
      return id
    },
    success(msg, duration = 3000) { return this.add(msg, 'success', duration) },
    error(msg, duration = 5000) { return this.add(msg, 'error', duration) },
    warning(msg, duration = 4500) { return this.add(msg, 'warning', duration) },
    info(msg, duration = 4000) { return this.add(msg, 'info', duration) },
    remove(id) {
      const idx = this.toasts.findIndex(t => t.id === id)
      if (idx !== -1) this.toasts.splice(idx, 1)
    },
  },
})
