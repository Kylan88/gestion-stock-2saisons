from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import crud
import schemas

router = APIRouter(prefix="/api/produits", tags=["Produits"])

@router.get("/", response_model=List[schemas.ProduitResponse])
def liste_produits(
    actif: bool = True,
    recherche: Optional[str] = Query(None, description="Recherche par nom"),
    categorie_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Liste des produits avec recherche et filtres."""
    return crud.get_produits(db, actif=actif, skip=skip, limit=limit,
                             recherche=recherche, categorie_id=categorie_id)

@router.get("/{produit_id}", response_model=schemas.ProduitResponse)
def obtenir_produit(produit_id: int, db: Session = Depends(get_db)):
    p = crud.get_produit(db, produit_id)
    if not p: raise HTTPException(404, f"Produit {produit_id} introuvable")
    return p

@router.post("/", response_model=schemas.ProduitResponse, status_code=201)
def creer_produit(data: schemas.ProduitCreate, db: Session = Depends(get_db)):
    return crud.create_produit(db, **data.model_dump())

@router.put("/{produit_id}", response_model=schemas.ProduitResponse)
def modifier_produit(produit_id: int, data: schemas.ProduitUpdate, db: Session = Depends(get_db)):
    p = crud.update_produit(db, produit_id, **data.model_dump(exclude_unset=True))
    if not p: raise HTTPException(404, f"Produit {produit_id} introuvable")
    return p

@router.delete("/{produit_id}")
def supprimer_produit(produit_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_produit(db, produit_id)
    if not ok: raise HTTPException(404, f"Produit {produit_id} introuvable")
    return {"message": "Produit désactivé", "id": produit_id}

@router.get("/alertes/stock-bas", response_model=List[schemas.ProduitResponse])
def alertes_stock_bas(db: Session = Depends(get_db)):
    return crud.get_produits_stock_bas(db)

@router.get("/alertes/rupture", response_model=List[schemas.ProduitResponse])
def alertes_rupture(db: Session = Depends(get_db)):
    return crud.get_produits_rupture(db)
