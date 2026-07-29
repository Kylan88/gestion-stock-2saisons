from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import crud
import schemas

router = APIRouter(prefix="/api/conditionnement", tags=["Conditionnement"])

@router.post("/lots/{lot_id}", response_model=dict)
def valider_conditionnement(lot_id: int, data: schemas.ConditionnementCreate,
                            db: Session = Depends(get_db)):
    """
    Valide le conditionnement d'un lot : répartit en cartons (export/local/déchets/rhum),
    1 carton = 6 sachets × poids_sachet (défaut 2.5 kg). Vérifie l'écart bilan > 2%.
    """
    try:
        return crud.valider_conditionnement(db, lot_id, **data.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e))
