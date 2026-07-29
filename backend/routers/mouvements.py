from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import crud
import schemas

router = APIRouter(prefix="/api/mouvements", tags=["Mouvements"])

@router.get("/", response_model=List[schemas.MouvementResponse])
def liste_mouvements(
    produit_id: Optional[int] = None,
    type_mouvement: Optional[str] = None,
    date_debut: Optional[str] = Query(None, description="YYYY-MM-DD"),
    date_fin: Optional[str] = Query(None, description="YYYY-MM-DD"),
    limite: int = Query(100, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """Historique des mouvements avec filtres par produit, type et période."""
    return crud.get_mouvements(db, produit_id=produit_id, type_mvt=type_mouvement,
                               limite=limite, date_debut=date_debut, date_fin=date_fin)

@router.get("/{mouvement_id}", response_model=schemas.MouvementResponse)
def obtenir_mouvement(mouvement_id: int, db: Session = Depends(get_db)):
    mvt = db.query(crud.MouvementStock).options(
        crud.joinedload(crud.MouvementStock.produit),
        crud.joinedload(crud.MouvementStock.lot)
    ).filter(crud.MouvementStock.id == mouvement_id).first()
    if not mvt:
        raise HTTPException(404, f"Mouvement {mouvement_id} introuvable")
    return mvt

@router.post("/entree", response_model=schemas.MouvementResponse, status_code=201)
def creer_entree(data: schemas.MouvementCreate, db: Session = Depends(get_db)):
    try:
        params = data.model_dump(exclude={"type_mouvement"})
        return crud.entree_stock(db, **params)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/sortie", response_model=schemas.MouvementResponse, status_code=201)
def creer_sortie(data: schemas.MouvementCreate, db: Session = Depends(get_db)):
    try:
        params = data.model_dump(exclude={"type_mouvement"})
        return crud.sortie_stock(db, **params)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/types/liste", response_model=List[str])
def liste_types_mouvements():
    return ["entrée", "sortie", "ajustement", "perte", "transfert"]
