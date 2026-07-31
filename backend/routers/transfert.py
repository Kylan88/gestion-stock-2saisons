from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_db
import crud
import schemas

router = APIRouter(prefix="/api/stock", tags=["Transfert & Reconditionnement"])

# ── DEMANDES DE TRANSFERT CHAMBRE FROIDE ──

@router.post("/demande-transfert", response_model=schemas.DemandeTransfertResponse)
def creer_demande(data: schemas.DemandeTransfertCreate, db: Session = Depends(get_db)):
    try:
        return crud.creer_demande_transfert(db, data.lot_id, data.lignes, data.responsable, data.notes)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/demandes-transfert", response_model=List[schemas.DemandeTransfertResponse])
def lister_demandes(lot_id: Optional[int] = None, statut: Optional[str] = None,
                    db: Session = Depends(get_db)):
    return crud.get_demandes_transfert(db, lot_id, statut)

@router.get("/demande-transfert/{demande_id}", response_model=schemas.DemandeTransfertResponse)
def obtenir_demande(demande_id: int, db: Session = Depends(get_db)):
    d = crud.get_demande_transfert(db, demande_id)
    if not d:
        raise HTTPException(404, "Demande introuvable")
    return d

@router.post("/demande-transfert/{demande_id}/valider", response_model=schemas.DemandeTransfertResponse)
def valider_demande(demande_id: int, db: Session = Depends(get_db)):
    try:
        return crud.valider_demande_transfert(db, demande_id)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/demande-transfert/{demande_id}/annuler", response_model=schemas.DemandeTransfertResponse)
def annuler_demande(demande_id: int, db: Session = Depends(get_db)):
    try:
        return crud.annuler_demande_transfert(db, demande_id)
    except ValueError as e:
        raise HTTPException(400, str(e))

# ── RECONDITIONNEMENT (sachets 100g) ──

@router.post("/reconditionnement")
def creer_reconditionnement(data: schemas.ReconditionnementCreate, db: Session = Depends(get_db)):
    try:
        return crud.creer_reconditionnement(db, data.lot_id, data.type_source,
                                            data.nb_cartons_entree, data.responsable, data.notes)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/reconditionnements")
def lister_reconditionnements(lot_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_reconditionnements(db, lot_id)
