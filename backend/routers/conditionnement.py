from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
