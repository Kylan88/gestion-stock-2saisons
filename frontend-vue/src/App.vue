<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="logo-text">2Saisons</span>
      </div>

      <nav class="sidebar-nav">
        <router-link v-for="item in nav" :key="item.path" :to="item.path"
          class="nav-item" active-class="nav-active">
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="footer-dot"></div>
        <span>Bazré, Côte d'Ivoire</span>
      </div>
    </aside>

    <div class="main-wrapper">
      <header class="topbar">
        <div class="topbar-search">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" class="search-input" placeholder="Rechercher..." />
        </div>
        <div class="topbar-right">
          <div class="topbar-avatar">2S</div>
        </div>
      </header>

      <main class="main-content">
        <router-view />
      </main>
    </div>

    <AppToast />
  </div>
</template>

<script setup>
const nav = [
  { path: '/', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>', label: 'Dashboard' },
  { path: '/reception', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>', label: 'Réception' },
  { path: '/lots', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>', label: 'Lots' },
  { path: '/musserie', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6m-7-3.5l5.196-3m5.196-3L19 3.5M5 3.5l5.196 3m5.196 3L19 15.5"/></svg>', label: 'Musserie' },
  { path: '/production', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>', label: 'Production' },
  { path: '/conditionnement', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>', label: 'Conditionnement' },
  { path: '/stock', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>', label: 'Stock' },
  { path: '/produits', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>', label: 'Produits' },
  { path: '/fournisseurs', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>', label: 'Fournisseurs' },
  { path: '/commandes', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M9 14l2 2 4-4"/></svg>', label: 'Commandes' },
]
</script>

<style scoped>
.app-layout { display: flex; min-height: 100vh; }

/* ── Sidebar ── */
.sidebar {
  width: 240px; background: white; border-right: 1px solid var(--border);
  display: flex; flex-direction: column; flex-shrink: 0;
  position: sticky; top: 0; height: 100vh; z-index: 10;
}
.sidebar-logo {
  display: flex; align-items: center; gap: 10px;
  padding: 20px 20px; border-bottom: 1px solid var(--border-light);
}
.logo-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: var(--primary); color: white;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.logo-text { font-size: 18px; font-weight: 700; color: var(--dark); letter-spacing: -0.02em; }

.sidebar-nav { flex: 1; padding: 12px 10px; display: flex; flex-direction: column; gap: 2px; overflow-y: auto; }

.nav-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 14px;
  border-radius: var(--radius-sm); color: var(--text-secondary); text-decoration: none;
  font-size: 13px; font-weight: 500; transition: all 0.15s;
}
.nav-item:hover { background: var(--surface); color: var(--text); }
.nav-active {
  background: var(--primary-50); color: var(--primary); font-weight: 600;
  border: 1.5px solid var(--primary-light);
}
.nav-icon { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.nav-icon :deep(svg) { width: 20px; height: 20px; }

.sidebar-footer {
  padding: 16px 20px; border-top: 1px solid var(--border-light);
  display: flex; align-items: center; gap: 8px;
  font-size: 11px; color: var(--text-muted);
}
.footer-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--success); }

/* ── Main wrapper ── */
.main-wrapper { flex: 1; display: flex; flex-direction: column; min-width: 0; }

/* ── Topbar ── */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 32px; background: white; border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 5;
}
.topbar-search {
  position: relative; flex: 0 1 320px;
}
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }
.search-input {
  width: 100%; padding: 9px 14px 9px 38px; border: 1.5px solid var(--border);
  border-radius: var(--radius-sm); font-size: 13px; font-family: inherit;
  background: var(--surface); color: var(--text); outline: none; transition: all var(--transition);
}
.search-input:focus { border-color: var(--primary); background: white; box-shadow: 0 0 0 3px rgba(20,184,166,0.1); }
.search-input::placeholder { color: var(--text-muted); }
.topbar-right { display: flex; align-items: center; gap: 12px; }
.topbar-avatar {
  width: 36px; height: 36px; border-radius: 50%; background: var(--primary);
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
}

/* ── Content ── */
.main-content { flex: 1; padding: 28px 32px; overflow-y: auto; max-height: calc(100vh - 56px); }
</style>
