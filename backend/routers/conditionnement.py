from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
import crud
import schemas

router = APIRouter(prefix="/api/conditionnement", tags=["Conditionnement"])

@router.post("/lots/{lot_id}", response_model=dict)
def valider_conditionnement(lot_id: int, data: schemas.ConditionnementCreate,
                            db: Session = Depends(get_db)):
    """Enregistre une session journalière de conditionnement (cumul)."""
    try:
        return crud.valider_conditionnement(db, lot_id, **data.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/lots/{lot_id}/cloturer", response_model=dict)
def cloturer_conditionnement(lot_id: int, db: Session = Depends(get_db)):
    """Clôture le conditionnement et passe le lot à conditionne."""
    try:
        return crud.cloturer_conditionnement(db, lot_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


# ── PAR DRYER J+1 ──

@router.get("/dryers-disponibles")
def dryers_disponibles(lot_id: int = Query(...), date: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Dryers dont la production a eu lieu hier → dispo aujourd'hui."""
    return crud.get_conditionnement_dryers_disponibles(db, lot_id, date)

@router.post("/lots/{lot_id}/dryer", response_model=dict)
def valider_conditionnement_dryer(lot_id: int, data: schemas.ConditionnementEntryCreate, db: Session = Depends(get_db)):
    """Conditionnement pour 1 dryer à J+1 (vérifie prod veille)."""
    try:
        res = crud.valider_conditionnement_dryer(db, lot_id, data.dryer, **data.model_dump(exclude={"dryer"}))
        return {"ok": True, "entry_id": res["entry"].id, "lot_id": lot_id, "dryer": data.dryer}
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/entries", response_model=list[schemas.ConditionnementEntryResponse])
def list_entries(lot_id: Optional[int] = None, date: Optional[str] = None, dryer: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_conditionnement_entries_dryer(db, lot_id, date, dryer)
