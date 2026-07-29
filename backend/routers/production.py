from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import crud
import schemas
from models import Lot

router = APIRouter(prefix="/api/production", tags=["Production"])

@router.post("/musserie/{lot_id}", response_model=schemas.EtapeProductionResponse)
def valider_musserie(lot_id: int, data: schemas.MusserieCreate,
                     db: Session = Depends(get_db)):
    """Enregistre une session journalière de musserie (cumul)."""
    try:
        ep = crud.valider_musserie(db, lot_id, **data.model_dump())
        if not ep:
            raise HTTPException(404, f"Lot {lot_id} introuvable")
        return ep
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/valider/{lot_id}", response_model=schemas.EtapeProductionResponse)
def valider_production(lot_id: int, data: schemas.ProductionCreate,
                       db: Session = Depends(get_db)):
    """Valide l'étape production : chargement chariots → séchoir."""
    try:
        ep = crud.valider_production(db, lot_id, **data.model_dump())
        return ep
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/etapes", response_model=List[schemas.EtapeProductionResponse])
def lister_etapes(lot_id: int = Query(..., description="ID du lot"),
                  db: Session = Depends(get_db)):
    """Liste les étapes de production d'un lot (musserie → conditionnement)."""
    return crud.get_etapes_lot(db, lot_id)

@router.get("/etapes/{etape_id}", response_model=schemas.EtapeProductionResponse)
def obtenir_etape(etape_id: int, db: Session = Depends(get_db)):
    """Détail d'une étape de production."""
    ep = crud.get_etape(db, etape_id)
    if not ep: raise HTTPException(404, f"Étape {etape_id} introuvable")
    return ep

@router.post("/etapes/{etape_id}/demarrer", response_model=schemas.EtapeProductionResponse)
def demarrer_etape(etape_id: int, operateur: str = Query("", description="Nom de l'opérateur"),
                   db: Session = Depends(get_db)):
    """Démarre une étape de production (passe de 'en_attente' à 'en_cours')."""
    ep = crud.demarrer_etape(db, etape_id, operateur=operateur)
    if not ep: raise HTTPException(404, f"Étape {etape_id} introuvable")
    return ep

@router.put("/etapes/{etape_id}", response_model=schemas.EtapeProductionResponse)
def mettre_a_jour_etape(etape_id: int, data: schemas.EtapeProductionUpdate,
                        db: Session = Depends(get_db)):
    """Met à jour une étape (poids entrée, notes, etc.). Calcule perte/rendement si statut=terminé."""
    ep = crud.get_etape(db, etape_id)
    if not ep: raise HTTPException(404, f"Étape {etape_id} introuvable")
    upd = data.model_dump(exclude_unset=True)
    if upd:
        from models import EtapeProduction as EPM
        db.query(EPM).filter(EPM.id == etape_id).update(upd)
        db.commit()
        db.refresh(ep)
    # Calculer perte et rendement si l'étape est terminée
    if ep.statut == "terminé" and ep.poids_entree > 0 and ep.poids_sortie > 0:
        ep.perte = round(ep.poids_entree - ep.poids_sortie, 2)
        ep.rendement_pourcentage = round((ep.poids_sortie / ep.poids_entree) * 100, 1)
        db.commit()
        db.refresh(ep)
    # Si dernière étape, mettre à jour le rendement global du lot
    if ep.etape == "conditionnement" and ep.statut == "terminé" and ep.poids_sortie > 0:
        lot = db.get(Lot, ep.lot_id)
        if lot:
            lot.poids_sec_final = ep.poids_sortie
            if lot.poids_frais > 0:
                lot.rendement_global = round((ep.poids_sortie / lot.poids_frais) * 100, 1)
            lot.statut = "en stock"
            db.commit()
    return ep
