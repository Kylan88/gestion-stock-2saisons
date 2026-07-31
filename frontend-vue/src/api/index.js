import axios from 'axios'
import { useToastStore } from '../stores/toast'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  r => r,
  err => {
    const msg = err.response?.data?.detail || err.message || 'Erreur serveur'
    try {
      const toast = useToastStore()
      toast.error(msg)
    } catch {}
    return Promise.reject(err)
  }
)

export default api

// ── Produits ──
export async function getProduits(params = {}) {
  const { data } = await api.get('/produits/', { params })
  return data
}
export async function getProduit(id) {
  const { data } = await api.get(`/produits/${id}`)
  return data
}
export async function createProduit(payload) {
  const { data } = await api.post('/produits/', payload)
  return data
}
export async function updateProduit(id, payload) {
  const { data } = await api.put(`/produits/${id}`, payload)
  return data
}
export async function getAlertesStockBas() {
  const { data } = await api.get('/produits/alertes/stock-bas')
  return data
}

// ── Fournisseurs ──
export async function getFournisseurs(params = {}) {
  const { data } = await api.get('/fournisseurs/', { params })
  return data
}
export async function getFournisseur(id) {
  const { data } = await api.get(`/fournisseurs/${id}`)
  return data
}
export async function createFournisseur(payload) {
  const { data } = await api.post('/fournisseurs/', payload)
  return data
}
export async function updateFournisseur(id, payload) {
  const { data } = await api.put(`/fournisseurs/${id}`, payload)
  return data
}

// ── Lots ──
export async function getLots(params = {}) {
  const { data } = await api.get('/lots/', { params })
  return data
}
export async function getLot(id) {
  const { data } = await api.get(`/lots/${id}`)
  return data
}
export async function createLot(payload) {
  const { data } = await api.post('/lots/', payload)
  return data
}
export async function updateLotStatut(id, statut) {
  const { data } = await api.put(`/lots/${id}/statut`, null, { params: { statut } })
  return data
}

// ── Production / Étapes ──
export async function getProductionsEtapes(lotId) {
  const { data } = await api.get('/production/etapes', { params: { lot_id: lotId } })
  return data
}
export async function demarrerEtape(etapeId, operateur = '') {
  const { data } = await api.post(`/production/etapes/${etapeId}/demarrer`, null, { params: { operateur } })
  return data
}
export async function updateEtape(etapeId, payload) {
  const { data } = await api.put(`/production/etapes/${etapeId}`, payload)
  return data
}
export async function validerMusserie(lotId, payload) {
  const { data } = await api.post(`/production/musserie/${lotId}`, payload)
  return data
}
export async function validerProduction(lotId, payload) {
  const { data } = await api.post(`/production/valider/${lotId}`, payload)
  return data
}
export async function getDryersProduction(lotId) {
  const { data } = await api.get(`/production/dryers/${lotId}`)
  return data
}
export async function cloturerProduction(lotId) {
  const { data } = await api.post(`/production/cloturer/${lotId}`)
  return data
}

// ── Conditionnement ──
export async function validerConditionnement(lotId, payload) {
  const { data } = await api.post(`/conditionnement/lots/${lotId}`, payload)
  return data
}

// ── Stock / Zones ──
export async function getZonesStock(params = {}) {
  const { data } = await api.get('/stock/zones', { params })
  return data
}
export async function getStock(params = {}) {
  const { data } = await api.get('/stock/stock', { params })
  return data
}
export async function stockerProduit(payload) {
  const { data } = await api.post('/stock/stocker', payload)
  return data
}
export async function sortirStock(stockId) {
  const { data } = await api.post(`/stock/sortir/${stockId}`)
  return data
}
export async function getContenuZone(zoneId) {
  const { data } = await api.get(`/stock/zones/${zoneId}/contenu`)
  return data
}

// ── Dashboard ──
export async function getDashboardStats() {
  const { data } = await api.get('/dashboard/stats')
  return data
}
export async function getDashboardProduction() {
  const { data } = await api.get('/dashboard/production')
  return data
}

// ── Commandes ──
export async function getCommandes(params = {}) {
  const { data } = await api.get('/commandes/', { params })
  return data
}
export async function getCommande(id) {
  const { data } = await api.get(`/commandes/${id}`)
  return data
}
export async function createCommande(payload) {
  const { data } = await api.post('/commandes/', payload)
  return data
}
export async function updateCommandeStatut(id, statut) {
  const { data } = await api.put(`/commandes/${id}/statut`, null, { params: { statut } })
  return data
}
export async function getStatutsCommandes() {
  const { data } = await api.get('/commandes/statuts/liste')
  return data
}

// ── Catégories ──
export async function getCategories() {
  const { data } = await api.get('/categories')
  return data
}

// ── Transfert chambre froide ──
export async function creerDemandeTransfert(payload) {
  const { data } = await api.post('/stock/demande-transfert', payload)
  return data
}
export async function getDemandesTransfert(params = {}) {
  const { data } = await api.get('/stock/demandes-transfert', { params })
  return data
}
export async function validerDemandeTransfert(id) {
  const { data } = await api.post(`/stock/demande-transfert/${id}/valider`)
  return data
}
export async function annulerDemandeTransfert(id) {
  const { data } = await api.post(`/stock/demande-transfert/${id}/annuler`)
  return data
}

// ── Reconditionnement (sachets 100g) ──
export async function creerReconditionnement(payload) {
  const { data } = await api.post('/stock/reconditionnement', payload)
  return data
}
export async function getReconditionnements(params = {}) {
  const { data } = await api.get('/stock/reconditionnements', { params })
  return data
}

// ── Historique Musserie ──
export async function getHistoriqueMusserie(params = {}) {
  const { data } = await api.get('/production/musserie/historique', { params })
  return data
}

// ── Historique Production ──
export async function getHistoriqueProduction(params = {}) {
  const { data } = await api.get('/production/production/historique', { params })
  return data
}

// ── Historique Conditionnement ──
export async function getHistoriqueConditionnement(params = {}) {
  const { data } = await api.get('/production/conditionnement/historique', { params })
  return data
}

// ── Anomalies ──
export async function getAnomalies() {
  const { data } = await api.get('/production/anomalies')
  return data
}
