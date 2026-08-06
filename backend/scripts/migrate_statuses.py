"""
Migration script: normalize status string values in DB to canonical constants from statuses.py
Usage: python migrate_statuses.py
This script updates lots.statut, etapes_production.statut, demandes_transfert.statut,
lignes_demande_transfert.statut, reconditionnements.statut and lot.statut_transfert.
It prints a summary of changes.
"""
import unicodedata
from collections import defaultdict
import sys, os
# ensure package imports from backend/ work when running script from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models
import statuses

TABLES_AND_ATTRS = [
    (models.Lot, 'statut'),
    (models.Lot, 'statut_transfert'),
    (models.EtapeProduction, 'statut'),
    (models.DemandeTransfert, 'statut'),
    (models.DemandeTransfertLigne, 'statut'),
    (models.Reconditionnement, 'statut'),
]

# mapping canonical -> legacy variants
LEGACY_MAP = {
    statuses.RECEPTION: ["réception", "reception"],
    statuses.EN_MUSSERIE: ["en musserie", "en_musserie", "en-musserie"],
    statuses.EN_PRODUCTION: ["en production", "en_production", "en-production"],
    statuses.EN_SECHAGE: ["en séchage", "en sechage", "en_sechage", "ensechage"],
    statuses.CONDITIONNE: ["conditionné", "conditionne", "conditionne"] ,
    statuses.EN_STOCK: ["en stock", "en_stock"],
    statuses.EXPEDIE: ["expédié", "expedie", "expedie"],
    statuses.PERIME: ["périmé", "perime"],
    statuses.EN_ATTENTE: ["en_attente", "en attente", "en-attente"],
    statuses.EN_COURS: ["en_cours", "en cours", "en-cours"],
    statuses.TERMINE: ["terminé", "termine", "termine"]
}

# build normalized lookup
def normalize_key(s: str) -> str:
    if s is None:
        return ""
    s = s.strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    for ch in [' ', '-', '_']:
        s = s.replace(ch, '_')
    return s

NORMALIZED_TO_CANONICAL = {}
for can, legacy_list in LEGACY_MAP.items():
    for l in legacy_list:
        NORMALIZED_TO_CANONICAL[normalize_key(l)] = can
# ensure canonical values map to themselves
for can in LEGACY_MAP.keys():
    NORMALIZED_TO_CANONICAL[normalize_key(can)] = can


def migrate():
    session = SessionLocal()
    summary = defaultdict(int)
    updated_rows = 0
    try:
        for model_cls, attr in TABLES_AND_ATTRS:
            q = session.query(model_cls).all()
            for row in q:
                current = getattr(row, attr, None)
                norm = normalize_key(current if current is not None else "")
                canonical = NORMALIZED_TO_CANONICAL.get(norm)
                if canonical and current != canonical:
                    setattr(row, attr, canonical)
                    summary[f"{model_cls.__tablename__}.{attr}"] += 1
                    updated_rows += 1
        if updated_rows > 0:
            session.commit()
        else:
            session.rollback()
    except Exception as e:
        session.rollback()
        print("ERROR during migration:", e)
        raise
    finally:
        session.close()

    print("Migration complete.")
    if updated_rows == 0:
        print("No rows needed changes.")
    else:
        print(f"Total rows updated: {updated_rows}")
        for k, v in summary.items():
            print(f"  {k}: {v}")

if __name__ == '__main__':
    print("Starting status normalization migration...")
    migrate()
