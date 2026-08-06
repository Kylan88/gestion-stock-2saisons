<template>
  <div class="app-layout">
    <!-- Mobile overlay -->
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-logo">
        <img src="/2saisons.jpeg" alt="2Saisons" class="logo-img" />
        <span class="logo-text">2Saisons</span>
      </div>

      <nav class="sidebar-nav">
        <router-link v-for="item in nav" :key="item.path" :to="item.path"
          class="nav-item" active-class="nav-active" @click="sidebarOpen = false">
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
        <div class="topbar-left">
          <button class="hamburger" @click="sidebarOpen = !sidebarOpen" aria-label="Menu">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <nav class="breadcrumbs" v-if="breadcrumbs.length > 1">
            <template v-for="(crumb, i) in breadcrumbs" :key="i">
              <router-link v-if="crumb.path" :to="crumb.path" class="breadcrumb-link">{{ crumb.label }}</router-link>
              <span v-else class="breadcrumb-current">{{ crumb.label }}</span>
              <span v-if="i < breadcrumbs.length - 1" class="breadcrumb-sep">/</span>
            </template>
          </nav>
        </div>
        <div class="topbar-search">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            type="text"
            class="search-input"
            placeholder="Rechercher un lot..."
            v-model="searchQuery"
            @keydown.enter="goSearch"
          />
        </div>
        <div class="topbar-right">
          <div class="topbar-avatar">2S</div>
        </div>
      </header>

      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="route" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <AppToast />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const sidebarOpen = ref(false)

function goSearch() {
  if (!searchQuery.value.trim()) return
  router.push({ path: '/lots', query: { q: searchQuery.value.trim() } })
  searchQuery.value = ''
}

const routeLabels = {
  '/': 'Dashboard',
  '/reception': 'Réception',
  '/lots': 'Lots',
  '/musserie': 'Musserie',
  '/production': 'Production',
  '/conditionnement': 'Conditionnement',
  '/stock': 'Stock',
  '/stock/transfert': 'Transfert CF',
  '/stock/reconditionnement': 'Reconditionnement',
  '/produits': 'Produits',
  '/fournisseurs': 'Fournisseurs',
  '/commandes': 'Commandes',
  '/anomalies': 'Anomalies',
  '/historique': 'Historique',
}

const breadcrumbs = computed(() => {
  const path = route.path
  const crumbs = [{ label: 'Accueil', path: '/' }]
  if (path === '/') return crumbs
  const segments = path.split('/').filter(Boolean)
  let builtPath = ''
  for (const seg of segments) {
    builtPath += '/' + seg
    const label = routeLabels[builtPath]
    if (label) {
      crumbs.push({ label, path: builtPath === path ? null : builtPath })
    }
  }
  return crumbs
})

const nav = [
  { path: '/', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>', label: 'Dashboard' },
  { path: '/reception', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>', label: 'Réception' },
  { path: '/lots', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>', label: 'Lots' },
  { path: '/musserie', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6m-7-3.5l5.196-3m5.196-3L19 3.5M5 3.5l5.196 3m5.196 3L19 15.5"/></svg>', label: 'Musserie' },
  { path: '/production', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>', label: 'Production' },
  { path: '/conditionnement', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>', label: 'Conditionnement' },
  { path: '/stock', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>', label: 'Stock' },
  { path: '/stock/transfert', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>', label: 'Transfert CF' },
  { path: '/stock/reconditionnement', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><line x1="12" y1="12" x2="12" y2="21"/></svg>', label: 'Reconditionnement' },
  { path: '/produits', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>', label: 'Produits' },
  { path: '/fournisseurs', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>', label: 'Fournisseurs' },
  { path: '/commandes', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M9 14l2 2 4-4"/></svg>', label: 'Commandes' },
  { path: '/anomalies', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>', label: 'Anomalies' },
  { path: '/historique', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>', label: 'Historique' },
]
</script>

<style scoped>
.app-layout { display: flex; min-height: 100vh; }

/* ── Sidebar ── */
.sidebar {
  width: 256px; background: var(--secondary); border-right: 1px solid rgba(255,255,255,0.08);
  display: flex; flex-direction: column; flex-shrink: 0;
  position: sticky; top: 0; height: 100vh; z-index: 10;
}
.sidebar-logo {
  display: flex; align-items: center; gap: 10px;
  padding: 22px 20px; border-bottom: 1px solid rgba(255,255,255,0.1);
}
.logo-img {
  width: 38px; height: 38px; border-radius: 12px;
  object-fit: cover; flex-shrink: 0; border: 1px solid rgba(255,255,255,0.2);
}
.logo-text { font-family: 'DM Serif Display', Georgia, serif; font-size: 21px; font-weight: 400; color: white; letter-spacing: -0.02em; }

.sidebar-nav { flex: 1; padding: 16px 12px; display: flex; flex-direction: column; gap: 4px; overflow-y: auto; }

.nav-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 12px;
  border-radius: var(--radius-sm); color: #C9D8CE; text-decoration: none;
  font-size: 12px; font-weight: 600; transition: color var(--transition), background var(--transition), transform var(--transition), box-shadow var(--transition);
}
.nav-item:hover { background: rgba(255,255,255,0.08); color: white; transform: translateX(2px); }
.nav-active {
  background: rgba(185,229,201,0.16); color: white; font-weight: 700;
  box-shadow: inset 3px 0 0 var(--primary-light);
}
.nav-icon { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.nav-icon :deep(svg) { width: 20px; height: 20px; }

.sidebar-footer {
  padding: 17px 20px; border-top: 1px solid rgba(255,255,255,0.1);
  display: flex; align-items: center; gap: 8px;
  font-size: 11px; color: #AEBFB3;
}
.footer-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--primary-light); box-shadow: 0 0 0 4px rgba(185,229,201,0.1); }

/* ── Main wrapper ── */
.main-wrapper { flex: 1; display: flex; flex-direction: column; min-width: 0; }

/* ── Topbar ── */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  min-height: 70px; padding: 12px 36px; background: rgba(255,255,255,0.92); border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 5; gap: 16px;
  backdrop-filter: blur(12px);
}
.topbar-left { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.hamburger {
  display: none; background: none; border: none; cursor: pointer;
  padding: 6px; border-radius: var(--radius-sm); color: var(--text-secondary);
}
.hamburger:hover { background: var(--surface); }
.breadcrumbs { display: flex; align-items: center; gap: 7px; font-size: 12px; white-space: nowrap; }
.breadcrumb-link { color: var(--text-muted); text-decoration: none; transition: color 0.15s; }
.breadcrumb-link:hover { color: var(--primary); }
.breadcrumb-current { color: var(--text); font-weight: 500; }
.breadcrumb-sep { color: var(--text-muted); font-size: 11px; }

.topbar-search {
  position: relative; flex: 0 1 320px;
}
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }
.search-input {
  width: 100%; min-height: 38px; padding: 8px 14px 8px 38px; border: 1px solid var(--border);
  border-radius: 99px; font-size: 12px; font-family: inherit;
  background: var(--surface); color: var(--text); outline: none; transition: all var(--transition);
}
.search-input:focus { border-color: var(--primary); background: white; box-shadow: 0 0 0 3px rgba(22,91,61,0.1); }
.search-input::placeholder { color: var(--text-muted); }
.topbar-right { display: flex; align-items: center; gap: 12px; }
.topbar-avatar {
  width: 38px; height: 38px; border-radius: 50%; background: var(--primary);
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 800; box-shadow: 0 3px 8px rgba(22,91,61,0.2);
}

.route-enter-active, .route-leave-active { transition: opacity 0.22s ease, transform 0.22s ease; }
.route-enter-from { opacity: 0; transform: translateY(8px); }
.route-leave-to { opacity: 0; transform: translateY(-5px); }

/* ── Content ── */
.main-content { flex: 1; padding: 34px 36px 48px; overflow-y: auto; max-height: calc(100vh - 70px); }

/* ── Mobile ── */
.sidebar-overlay {
  display: none; position: fixed; inset: 0; background: rgba(15,23,42,0.3);
  z-index: 9; backdrop-filter: blur(2px);
}
@media (max-width: 768px) {
  .sidebar {
    position: fixed; left: -260px; top: 0; height: 100vh;
    transition: left 0.25s ease; z-index: 11;
  }
  .sidebar-open { left: 0; }
  .sidebar-overlay { display: block; }
  .hamburger { display: flex; }
  .breadcrumbs { display: none; }
  .topbar { padding: 12px 16px; }
  .topbar-search { flex: 1; min-width: 0; }
  .main-content { padding: 16px; }
}
</style>
