from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import crud

router = APIRouter(prefix="/api/rendements", tags=["Rendements"])

@router.get("/lots/{lot_id}")
def rendements_lot(lot_id: int, db: Session = Depends(get_db)):
    """Calcul détaillé des rendements pour un lot (frais → sec)."""
    result = crud.calculer_rendements_lot(db, lot_id)
    if not result:
        raise HTTPException(404, f"Lot {lot_id} introuvable")
    return result

@router.get("/moyen")
def rendement_moyen_global(db: Session = Depends(get_db)):
    """Rendement moyen global tous lots confondus."""
    return {
        "rendement_moyen_pourcentage": crud.get_rendement_moyen_global(db)
    }

@router.get("/lots")
def synthese_rendements(db: Session = Depends(get_db)):
    """Synthèse des rendements pour tous les lots avec données complètes."""
    lots = crud.get_lots(db)
    resultats = []
    for lot in lots:
        if lot.poids_frais > 0:
            resultats.append({
                "lot_id": lot.id,
                "code_lot": lot.code_lot,
                "produit": lot.produit.nom if lot.produit else None,
                "poids_frais": lot.poids_frais,
                "poids_sec": lot.poids_sec_final,
                "rendement": lot.rendement_global,
                "statut": lot.statut,
            })
    return {
        "total_lots_avec_donnees": len(resultats),
        "rendement_moyen": crud.get_rendement_moyen_global(db),
        "lots": resultats,
    }
