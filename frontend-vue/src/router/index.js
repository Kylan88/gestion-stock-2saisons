import { createRouter, createWebHistory } from 'vue-router'

import Reception from '../views/Reception.vue'
import Dashboard from '../views/Dashboard.vue'
import Lots from '../views/Lots.vue'
import Musserie from '../views/Musserie.vue'
import Production from '../views/Production.vue'
import Conditionnement from '../views/Conditionnement.vue'
import Stock from '../views/Stock.vue'
import Produits from '../views/Produits.vue'
import Fournisseurs from '../views/Fournisseurs.vue'
import Commandes from '../views/Commandes.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/reception', name: 'Reception', component: Reception },
  { path: '/lots', name: 'Lots', component: Lots },
  { path: '/musserie', name: 'Musserie', component: Musserie },
  { path: '/production', name: 'Production', component: Production },
  { path: '/conditionnement', name: 'Conditionnement', component: Conditionnement },
  { path: '/stock', name: 'Stock', component: Stock },
  { path: '/produits', name: 'Produits', component: Produits },
  { path: '/fournisseurs', name: 'Fournisseurs', component: Fournisseurs },
  { path: '/commandes', name: 'Commandes', component: Commandes },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
