<template>
  <div class="app-layout">
    <!-- Mobile overlay -->
    <Transition name="fade">
      <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>
    </Transition>

    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-logo">
        <img src="/2saisons.jpeg" alt="2Saisons" class="logo-img" />
        <div>
          <span class="logo-text">2Saisons</span>
          <span class="logo-kicker">ATELIER DE PRODUCTION</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div v-for="group in navGroups" :key="group.label" class="nav-group">
          <span class="nav-group-label">{{ group.label }}</span>
          <router-link v-for="item in group.items" :key="item.path" :to="item.path"
            class="nav-item" active-class="nav-active" @click="sidebarOpen = false">
            <span class="nav-icon" v-html="item.icon"></span>
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
        </div>
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
          <button @click="toggleTheme" :title="themeStore.resolvedTheme === 'dark' ? 'Mode clair' : 'Mode sombre'" style="padding:8px;border-radius:8px;border:none;background:transparent;cursor:pointer;color:#6b7280">
            <svg v-if="themeStore.resolvedTheme === 'dark'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          </button>
          <div class="topbar-status"><span class="topbar-status-dot"></span>Opérations en direct</div>
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
import { useThemeStore } from './stores/theme'
const themeStore = useThemeStore()
function toggleTheme() { themeStore.setThemeMode(themeStore.resolvedTheme === 'dark' ? 'light' : 'dark') }

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
  '/production/chariots': 'Production Chariots',
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

const navItems = [
  { path: '/', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>', label: 'Dashboard' },
  { path: '/reception', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>', label: 'Réception' },
  { path: '/lots', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>', label: 'Lots' },
  { path: '/musserie', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6m-7-3.5l5.196-3m5.196-3L19 3.5M5 3.5l5.196 3m5.196 3L19 15.5"/></svg>', label: 'Musserie' },
  { path: '/production', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="M8 11h8M8 15h8M8 7h8"/></svg>', label: 'Production' },
  { path: '/production/chariots', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>', label: 'Chariots' },
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

const navGroups = [
  { label: 'Vue d\'ensemble', items: [navItems[0]] },
  { label: 'Flux de production', items: navItems.slice(1, 7) },
  { label: 'Stock & ventes', items: navItems.slice(7, 12) },
  { label: 'Suivi', items: navItems.slice(12) },
]
</script>

<style scoped>
.app-layout { display: flex; min-height: 100vh; background: #f9fafb; }

/* ── Sidebar — identique 2saisons-app ── */
.sidebar {
  width: 256px; background: white; border-right: 1px solid #e5e7eb;
  display: flex; flex-direction: column; flex-shrink: 0;
  position: fixed; top: 0; left: 0; height: 100vh; z-index: 50; overflow-y: auto;
}
.sidebar-logo {
  display: flex; align-items: center; gap: 12px;
  padding: 20px; border-bottom: 1px solid #f3f4f6;
}
.logo-img { width: 40px; height: 40px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
.logo-text { display: block; font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 700; color: #111827; line-height: 1; }
.logo-kicker { display: block; margin-top: 2px; color: #6b7280; font-size: 10px; letter-spacing: 0.08em; font-weight: 600; text-transform: uppercase; }

.sidebar-nav { flex: 1; padding: 12px; display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }
.nav-group { display: flex; flex-direction: column; gap: 4px; }
.nav-group-label { padding: 0 12px 4px; color: #9ca3af; font-size: 10px; letter-spacing: 0.08em; font-weight: 700; text-transform: uppercase; }

.nav-item {
  display: flex; align-items: center; gap: 12px; padding: 12px 16px;
  border-radius: 8px; color: #374151; text-decoration: none;
  font-size: 13px; font-weight: 500; transition: all 0.2s; will-change: transform;
}
.nav-item:hover { background: #f3f4f6; color: #111827; transform: scale(1.02) translateX(2px); }
.nav-item:active { transform: scale(0.98); }
.nav-active {
  background: linear-gradient(to right, #16a34a, #22c55e); color: white !important; font-weight: 600;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}
.nav-active .nav-icon { color: white !important; }
.nav-active:hover { transform: scale(1.02) translateX(2px); }
.nav-icon { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: #6b7280; transition: color 0.2s; }
.nav-icon :deep(svg) { width: 20px; height: 20px; stroke-width: 2; }

.sidebar-footer {
  padding: 12px; border-top: 1px solid #e5e7eb;
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: #6b7280;
}
.footer-dot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; }

/* ── Main wrapper ── */
.main-wrapper { flex: 1; display: flex; flex-direction: column; min-width: 0; margin-left: 256px; min-height: 100vh; }

/* ── Topbar — identique 2saisons-app ── */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  min-height: 64px; padding: 12px 32px; background: white; border-bottom: 1px solid #e5e7eb;
  position: sticky; top: 0; z-index: 30; gap: 16px;
}
.topbar-left { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.hamburger {
  display: none; background: none; border: none; cursor: pointer;
  padding: 8px; border-radius: 8px; color: #6b7280;
}
.hamburger:hover { background: #f3f4f6; }
.breadcrumbs { display: flex; align-items: center; gap: 6px; font-size: 13px; white-space: nowrap; }
.breadcrumb-link { color: #6b7280; text-decoration: none; }
.breadcrumb-link:hover { color: #00853E; }
.breadcrumb-current { color: #111827; font-weight: 600; }
.breadcrumb-sep { color: #d1d5db; font-size: 12px; }

.topbar-search { position: relative; flex: 0 1 320px; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #9ca3af; }
.search-input {
  width: 100%; min-height: 36px; padding: 8px 14px 8px 36px; border: 1px solid #e5e7eb;
  border-radius: 8px; font-size: 13px; font-family: inherit;
  background: white; color: #111827; outline: none; transition: all 0.2s;
}
.search-input:focus { border-color: #00853E; box-shadow: 0 0 0 2px rgba(0,133,62,0.15); }
.search-input::placeholder { color: #9ca3af; }
.topbar-right { display: flex; align-items: center; gap: 12px; }
.topbar-status { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border: 1px solid #e5e7eb; border-radius: 9999px; background: white; color: #374151; font-size: 11px; font-weight: 600; }
.topbar-status-dot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; }
.topbar-avatar {
  width: 36px; height: 36px; border-radius: 50%; background: #00853E;
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
}

.route-enter-active, .route-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.route-enter-from { opacity: 0; transform: translateY(8px); }
.route-leave-to { opacity: 0; transform: translateY(-5px); }

/* ── Content ── */
.main-content { flex: 1; padding: 32px; background: #f9fafb; min-height: calc(100vh - 64px); }

/* ── Mobile ── */
.sidebar-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 40; }
:global(.dark) .sidebar { background: #1f2937; border-color: #374151; }
:global(.dark) .sidebar-logo { border-color: #374151; }
:global(.dark) .logo-text { color: #f9fafb; }
:global(.dark) .nav-item { color: #d1d5db; }
:global(.dark) .nav-item:hover { background: #374151; color: #f9fafb; }
:global(.dark) .topbar { background: #1f2937; border-color: #374151; }
:global(.dark) .main-content { background: #111827; }
:global(.dark) .search-input { background: #374151; border-color: #4b5563; color: #f9fafb; }
@media (max-width: 1024px) {
  .sidebar { transform: translateX(-100%); transition: transform 0.25s ease; }
  .sidebar-open { transform: translateX(0); }
  .sidebar-overlay { display: block; }
  .hamburger { display: flex; }
  .main-wrapper { margin-left: 0; }
  .breadcrumbs { display: none; }
  .topbar { padding: 12px 16px; }
  .topbar-status { display: none; }
  .main-content { padding: 16px; }
}
</style>
