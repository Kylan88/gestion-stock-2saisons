from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import crud
import schemas

router = APIRouter(prefix="/api/commandes", tags=["Commandes"])

@router.get("/", response_model=List[schemas.CommandeResponse])
def liste_commandes(
    statut: Optional[str] = None,
    recherche: Optional[str] = Query(None, description="Recherche par client"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Liste des commandes avec filtres."""
    return crud.get_commandes(db, skip=skip, limit=limit,
                              statut=statut, recherche=recherche)

@router.get("/{commande_id}", response_model=schemas.CommandeResponse)
def obtenir_commande(commande_id: int, db: Session = Depends(get_db)):
    cmd = crud.get_commande(db, commande_id)
    if not cmd:
        raise HTTPException(404, f"Commande {commande_id} introuvable")
    return cmd

@router.post("/", response_model=schemas.CommandeResponse, status_code=201)
def creer_commande(data: schemas.CommandeCreate, db: Session = Depends(get_db)):
    return crud.create_commande(
        db,
        client_nom=data.client_nom,
        lignes_data=[l.model_dump() for l in data.lignes],
        date_livraison_prevue=data.date_livraison_prevue,
        notes=data.notes,
    )

@router.put("/{commande_id}/statut", response_model=schemas.CommandeResponse)
def mettre_a_jour_statut(commande_id: int,
                         statut: str = Query(..., description="en_attente, préparée, expédiée, livrée, annulée"),
                         db: Session = Depends(get_db)):
    """Change le statut d'une commande."""
    cmd = crud.update_commande_statut(db, commande_id, statut)
    if not cmd:
        raise HTTPException(404, f"Commande {commande_id} introuvable")
    return cmd

@router.get("/statuts/liste", response_model=List[str])
def liste_statuts_commandes():
    return ["en_attente", "préparée", "expédiée", "livrée", "annulée"]
