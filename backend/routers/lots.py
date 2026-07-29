from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import crud
import schemas

router = APIRouter(prefix="/api/lots", tags=["Lots"])

@router.get("/", response_model=List[schemas.LotResponse])
def liste_lots(
    statut: Optional[str] = None,
    recherche: Optional[str] = Query(None, description="Recherche par code lot"),
    produit_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Liste tous les lots, filtrable par statut, recherche texte ou produit."""
    return crud.get_lots(db, statut=statut, recherche=recherche,
                         produit_id=produit_id, skip=skip, limit=limit)

@router.get("/statuts/liste", response_model=List[str])
def liste_statuts():
    """Liste des statuts possibles pour les lots."""
    return ["réception", "en musserie", "en production", "en séchage",
            "conditionné", "en stock", "expédié", "périmé"]

@router.get("/{lot_id}", response_model=schemas.LotResponse)
def obtenir_lot(lot_id: int, db: Session = Depends(get_db)):
    """Détail d'un lot avec son produit, fournisseur et étapes."""
    lot = crud.get_lot(db, lot_id)
    if not lot:
        raise HTTPException(404, f"Lot {lot_id} introuvable")
    return lot

@router.post("/", response_model=schemas.LotResponse, status_code=201)
def creer_lot(data: schemas.LotCreate, db: Session = Depends(get_db)):
    """Crée un nouveau lot avec les 4 étapes de production automatiquement."""
    return crud.create_lot(db, **data.model_dump())

@router.put("/{lot_id}/statut", response_model=schemas.LotResponse)
def mettre_a_jour_statut(lot_id: int, statut: str = Query(..., description="Nouveau statut"),
                         db: Session = Depends(get_db)):
    """Change le statut d'un lot (ex: réception → en musserie → etc.)."""
    lot = crud.changer_statut_lot(db, lot_id, statut)
    if not lot:
        raise HTTPException(404, f"Lot {lot_id} introuvable")
    return lot
