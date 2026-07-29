from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import crud
import schemas

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=schemas.DashboardStats)
def stats_dashboard(db: Session = Depends(get_db)):
    """Statistiques globales (stock + production)."""
    return crud.get_stats_dashboard(db)

@router.get("/production", response_model=schemas.DashboardProduction)
def stats_production(db: Session = Depends(get_db)):
    """Statistiques dédiées à la production (lots, étapes, séchoirs, rendement)."""
    return crud.get_stats_production(db)

@router.get("/stock-bas", response_model=List[schemas.ProduitResponse])
def stock_bas(db: Session = Depends(get_db)):
    return crud.get_produits_stock_bas(db)

@router.get("/rupture", response_model=List[schemas.ProduitResponse])
def rupture(db: Session = Depends(get_db)):
    return crud.get_produits_rupture(db)

@router.get("/derniers-mouvements", response_model=List[schemas.MouvementResponse])
def derniers_mouvements(db: Session = Depends(get_db)):
    return crud.get_mouvements(db, limite=10)
