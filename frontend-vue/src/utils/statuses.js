// Frontend status utilities: canonical names / normalization / labels / badge classes
export const RECEPTION = 'reception'
export const EN_MUSSERIE = 'en_musserie'
export const EN_PRODUCTION = 'en_production'
export const EN_SECHAGE = 'en_sechage'
export const CONDITIONNE = 'conditionne'
export const EN_STOCK = 'en_stock'
export const EXPEDIE = 'expedie'
export const PERIME = 'perime'

export const EN_ATTENTE = 'en_attente'
export const EN_COURS = 'en_cours'
export const TERMINE = 'termine'
export const VALIDEE = 'validee'
export const VALIDE = 'valide'
export const ANNULEE = 'annulee'

const LEGACY_MAP = {
  [RECEPTION]: ['réception', 'reception'],
  [EN_MUSSERIE]: ['en musserie', 'en_musserie', 'en-musserie'],
  [EN_PRODUCTION]: ['en production', 'en_production', 'en-production'],
  [EN_SECHAGE]: ['en séchage', 'en sechage', 'en_sechage', 'ensechage'],
  [CONDITIONNE]: ['conditionné', 'conditionne', 'conditionne'],
  [EN_STOCK]: ['en stock', 'en_stock'],
  [EXPEDIE]: ['expédié', 'expedie', 'expedie'],
  [PERIME]: ['périmé', 'perime'],
  [EN_ATTENTE]: ['en_attente', 'en attente', 'en-attente'],
  [EN_COURS]: ['en_cours', 'en cours', 'en-cours'],
  [TERMINE]: ['terminé', 'termine'],
  [VALIDEE]: ['validee', 'validée'],
  [VALIDE]: ['valide', 'validé'],
  [ANNULEE]: ['annulee', 'annulée'],
}

function normalizeKey(s) {
  if (!s) return ''
  let str = String(s).trim().toLowerCase()
  // remove accents
  str = str.normalize('NFKD').replace(/\p{Diacritic}/gu, '')
  str = str.replace(/[-_ ]+/g, '_')
  return str
}

const normalizedToCanonical = {}
Object.entries(LEGACY_MAP).forEach(([can, arr]) => {
  arr.forEach(v => normalizedToCanonical[normalizeKey(v)] = can)
  normalizedToCanonical[normalizeKey(can)] = can
})

export function toCanonical(status) {
  const k = normalizeKey(status)
  return normalizedToCanonical[k] || status
}

export const LABELS = {
  [RECEPTION]: 'Réception',
  [EN_MUSSERIE]: 'En musserie',
  [EN_PRODUCTION]: 'En production',
  [EN_SECHAGE]: 'En séchage',
  [CONDITIONNE]: 'Conditionné',
  [EN_STOCK]: 'En stock',
  [EXPEDIE]: 'Expédié',
  [PERIME]: 'Périmé',
  [EN_ATTENTE]: 'En attente',
  [EN_COURS]: 'En cours',
  [TERMINE]: 'Terminé',
  [VALIDEE]: 'Validée',
  [VALIDE]: 'Validé',
  [ANNULEE]: 'Annulée',
}

export const BADGE_CLASS = {
  [RECEPTION]: 'badge-primary',
  [EN_MUSSERIE]: 'badge-warning',
  [EN_PRODUCTION]: 'badge-info',
  [CONDITIONNE]: 'badge-primary',
  [EN_STOCK]: 'badge-success',
  [EXPEDIE]: 'badge-secondary',
  [PERIME]: 'badge-error',
  [TERMINE]: 'badge-success',
  [EN_COURS]: 'badge-warning',
  [EN_ATTENTE]: 'badge-muted',
  [VALIDEE]: 'badge-success',
  [VALIDE]: 'badge-success',
  [ANNULEE]: 'badge-error',
}

export function labelFor(status) {
  const c = toCanonical(status)
  return LABELS[c] || String(status).replace(/_/g, ' ')
}

export function classFor(status) {
  const c = toCanonical(status)
  return BADGE_CLASS[c] || 'badge-muted'
}
