from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
import models

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.get("/")
def global_search(q: str = Query(..., min_length=1, description="Recherche globale"), db: Session = Depends(get_db)):
    """Recherche globale : lots, produits, fournisseurs, zones, commandes."""
    like = f"%{q}%"
    # Lots
    lots = db.query(models.Lot).filter(
        or_(models.Lot.code_lot.ilike(like), models.Lot.type_fruit.ilike(like), models.Lot.fournisseur_nom.ilike(like))
    ).limit(8).all()
    # Produits
    produits = db.query(models.Produit).filter(models.Produit.nom.ilike(like)).limit(8).all()
    # Fournisseurs
    fournisseurs = db.query(models.Fournisseur).filter(models.Fournisseur.nom.ilike(like)).limit(8).all()
    # Zones
    zones = db.query(models.ZoneStockage).filter(models.ZoneStockage.nom.ilike(like)).limit(8).all()
    # Commandes
    commandes = db.query(models.Commande).filter(models.Commande.client_nom.ilike(like)).limit(8).all()

    return {
        "query": q,
        "lots": [{"id": l.id, "code_lot": l.code_lot, "type_fruit": l.type_fruit, "statut": l.statut} for l in lots],
        "produits": [{"id": p.id, "nom": p.nom} for p in produits],
        "fournisseurs": [{"id": f.id, "nom": f.nom} for f in fournisseurs],
        "zones": [{"id": z.id, "nom": z.nom, "type_zone": z.type_zone} for z in zones],
        "commandes": [{"id": c.id, "client_nom": c.client_nom, "statut": c.statut} for c in commandes],
    }
