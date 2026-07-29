from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import crud
import schemas

router = APIRouter(prefix="/api/stock", tags=["Stock & Zones"])

@router.get("/zones", response_model=List[schemas.ZoneStockageResponse])
def lister_zones(actif: bool = True, db: Session = Depends(get_db)):
    """Liste les zones de stockage (chambre froide, ambiant, etc.)."""
    return crud.get_zones_stockage(db, actif=actif)

@router.post("/zones", response_model=schemas.ZoneStockageResponse, status_code=201)
def creer_zone(data: schemas.ZoneStockageCreate, db: Session = Depends(get_db)):
    """Ajoute une zone de stockage."""
    return crud.create_zone_stockage(db, **data.model_dump())

@router.get("/zones/{zone_id}", response_model=schemas.ZoneStockageResponse)
def obtenir_zone(zone_id: int, db: Session = Depends(get_db)):
    """Détail d'une zone de stockage."""
    z = crud.get_zone_stockage(db, zone_id)
    if not z: raise HTTPException(404, f"Zone {zone_id} introuvable")
    return z

@router.get("/zones/{zone_id}/contenu", response_model=List[schemas.StockZoneResponse])
def contenu_zone(zone_id: int, db: Session = Depends(get_db)):
    """Liste le contenu actuel d'une zone de stockage."""
    return crud.get_stocks_zone(db, zone_id=zone_id)

@router.get("/stock", response_model=List[schemas.StockZoneResponse])
def lister_stocks(zone_id: int = None, produit_id: int = None,
                  db: Session = Depends(get_db)):
    """Liste tous les stocks en zone (filtrable par zone ou produit)."""
    return crud.get_stocks_zone(db, zone_id=zone_id, produit_id=produit_id)

@router.post("/stocker", response_model=schemas.StockZoneResponse, status_code=201)
def stocker_en_zone(data: schemas.StockZoneCreate, db: Session = Depends(get_db)):
    """Stocker un produit/lot dans une zone."""
    try:
        return crud.stocker_en_zone(db, zone_id=data.zone_id, produit_id=data.produit_id,
                                    quantite=data.quantite, lot_id=data.lot_id)
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/sortir/{stock_id}", response_model=schemas.StockZoneResponse)
def sortir_de_zone(stock_id: int, db: Session = Depends(get_db)):
    """Sortir un produit d'une zone de stockage."""
    sz = crud.sortir_de_zone(db, stock_id)
    if not sz: raise HTTPException(404, f"Stock {stock_id} introuvable")
    return sz
