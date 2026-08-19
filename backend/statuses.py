# Canonical status constants for 2Saisons backend
# Use snake_case without accents to avoid comparison issues.
RECEPTION = "reception"
EN_MUSSERIE = "en_musserie"
EN_PRODUCTION = "en_production"
EN_CONDITIONNEMENT = "en_conditionnement"
CONDITIONNE = "conditionne"
EN_STOCK = "en_stock"
EXPEDIE = "expedie"
PERIME = "perime"

EN_ATTENTE = "en_attente"
EN_COURS = "en_cours"
TERMINE = "termine"
VALIDEE = "validee"
VALIDE = "valide"
ANNULEE = "annulee"

STATUTS_LOT = [RECEPTION, EN_MUSSERIE, EN_PRODUCTION, EN_CONDITIONNEMENT, CONDITIONNE, EN_STOCK, EXPEDIE, PERIME]

# Normalization helpers
import unicodedata

# Map canonical -> legacy variants (common historical spellings/accents)
_LEGACY_MAP = {
    RECEPTION: ['réception', 'reception'],
    EN_MUSSERIE: ['en musserie', 'en_musserie', 'en-musserie'],
    EN_PRODUCTION: ['en production', 'en_production', 'en-production'],
    EN_CONDITIONNEMENT: ['en conditionnement', 'en_conditionnement', 'en-conditionnement'],
    CONDITIONNE: ['conditionné', 'conditionne', 'conditionne'],
    EN_STOCK: ['en stock', 'en_stock'],
    EXPEDIE: ['expédié', 'expedie', 'expedie'],
    PERIME: ['périmé', 'perime'],
    EN_ATTENTE: ['en_attente', 'en attente', 'en-attente'],
    EN_COURS: ['en_cours', 'en cours', 'en-cours'],
    TERMINE: ['terminé', 'termine', 'termine'],
    VALIDEE: ['validee', 'validée', 'validee'],
    VALIDE: ['valide', 'validé'],
    ANNULEE: ['annulee', 'annulée', 'annulee'],
}

# Build normalized lookup
_normalized_to_canonical = {}

def _normalize_key(s: str) -> str:
    if s is None:
        return ''
    s = str(s).strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    for ch in [' ', '-', '_']:
        s = s.replace(ch, '_')
    return s

for can, variants in _LEGACY_MAP.items():
    for v in variants:
        _normalized_to_canonical[_normalize_key(v)] = can
    _normalized_to_canonical[_normalize_key(can)] = can


def normalize(status: str) -> str:
    """Return the canonical status string if known, otherwise return the original trimmed value."""
    if status is None:
        return status
    key = _normalize_key(status)
    return _normalized_to_canonical.get(key, status.strip())


def is_lot_status(status: str) -> bool:
    """Check if status is one of the canonical lot statuses."""
    return normalize(status) in STATUTS_LOT


# ── Workflow validation ──
# Order defines the valid production pipeline
WORKFLOW_ORDER = [RECEPTION, EN_MUSSERIE, EN_PRODUCTION, EN_CONDITIONNEMENT, CONDITIONNE, EN_STOCK]
TERMINAL_STATUSES = [EXPEDIE, PERIME]

# Allowed transitions: from -> set of allowed "to"
TRANSITIONS = {
    RECEPTION: {EN_MUSSERIE},
    EN_MUSSERIE: {EN_PRODUCTION},
    EN_PRODUCTION: {EN_CONDITIONNEMENT},
    EN_CONDITIONNEMENT: {CONDITIONNE},
    CONDITIONNE: {EN_STOCK},
    EN_STOCK: {EXPEDIE, PERIME},
    EXPEDIE: set(),
    PERIME: set(),
}


def can_transition(from_status: str, to_status: str) -> bool:
    """Check if a status transition is allowed in the workflow."""
    src = normalize(from_status)
    dst = normalize(to_status)
    if src not in TRANSITIONS:
        return False
    return dst in TRANSITIONS.get(src, set())


def next_statuses(current: str) -> list:
    """Return the list of valid next statuses from the current one."""
    cur = normalize(current)
    return sorted(TRANSITIONS.get(cur, set()))


def validate_transition(from_status: str, to_status: str):
    """Raise ValueError if the transition is not allowed."""
    if not can_transition(from_status, to_status):
        raise ValueError(
            f"Transition invalide: '{from_status}' → '{to_status}'. "
            f"Statuts autorises: {sorted(TRANSITIONS.get(normalize(from_status), set()))}"
        )
