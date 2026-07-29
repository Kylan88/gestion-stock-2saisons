"""
2Saisons — API REST de Gestion de Stock.
Point d'entree FastAPI.

Lancement : uvicorn main:app --reload
Ou : python main.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from routers import produits, mouvements, lots, commandes, dashboard
from routers import production, stock_zones, rendements
from routers import conditionnement
import crud
import schemas

# ── Creation des tables au demarrage ──
Base.metadata.create_all(bind=engine)

# ── Application FastAPI ──
app = FastAPI(
    title="2Saisons - API Gestion de Stock",
    description="""
    API REST de gestion de stock pour 2Saisons, entreprise agroalimentaire
    specialisee dans la transformation de fruits seches a Bazre (Cote d'Ivoire).

    ## Fonctionnalites
    * Gestion des produits, categories et fournisseurs
    * Entrees / sorties de stock avec historique complet
    * Traçabilite par lot (de la reception a l'expedition)
    * Commandes clients
    * Alertes de reapprovisionnement
    * Dashboard avec statistiques

    ## Documentation interactive
    * Swagger UI : `/docs`
    * ReDoc : `/redoc`
    """,
    version="1.0.0",
    contact={"name": "2Saisons", "email": "contact@2saisons.ci"},
)

# ── CORS (pour le frontend) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routage ──
app.include_router(produits.router)
app.include_router(mouvements.router)
app.include_router(lots.router)
app.include_router(commandes.router)
app.include_router(dashboard.router)
app.include_router(production.router)
app.include_router(stock_zones.router)
app.include_router(rendements.router)
app.include_router(conditionnement.router)

# ── Routes utilitaires ──

@app.get("/")
def root():
    """Racine de l'API."""
    return {
        "application": "2Saisons - Gestion de Stock",
        "version": "1.0.0",
        "endpoints": {
            "produits": "/api/produits",
            "mouvements": "/api/mouvements",
            "lots": "/api/lots",
            "commandes": "/api/commandes",
            "dashboard": "/api/dashboard",
            "production": "/api/production",
            "stock_zones": "/api/stock/zones",
            "rendements": "/api/rendements",
            "conditionnement": "/api/conditionnement",
        },
        "docs": "/docs",
        "redoc": "/redoc",
    }

@app.get("/api/categories", response_model=list[schemas.CategorieResponse], tags=["Referentiels"])
def liste_categories(db: Session = Depends(get_db)):
    """Liste des categories de produits."""
    return crud.get_categories(db)

@app.post("/api/categories", response_model=schemas.CategorieResponse, status_code=201, tags=["Referentiels"])
def creer_categorie(data: schemas.CategorieCreate, db: Session = Depends(get_db)):
    """Ajoute une nouvelle categorie de produits."""
    return crud.create_categorie(db, **data.model_dump())

@app.get("/api/fournisseurs", response_model=list[schemas.FournisseurResponse], tags=["Referentiels"])
def liste_fournisseurs(actif: bool = True, db: Session = Depends(get_db)):
    """Liste des fournisseurs."""
    return crud.get_fournisseurs(db, actif=actif)

@app.get("/api/fournisseurs/{fournisseur_id}", response_model=schemas.FournisseurResponse, tags=["Referentiels"])
def obtenir_fournisseur(fournisseur_id: int, db: Session = Depends(get_db)):
    """Detail d'un fournisseur."""
    f = crud.get_fournisseur(db, fournisseur_id)
    if not f: raise HTTPException(404, "Fournisseur introuvable")
    return f

@app.post("/api/fournisseurs", response_model=schemas.FournisseurResponse, status_code=201, tags=["Referentiels"])
def creer_fournisseur(data: schemas.FournisseurCreate, db: Session = Depends(get_db)):
    """Ajoute un nouveau fournisseur."""
    return crud.create_fournisseur(db, **data.model_dump())

@app.put("/api/fournisseurs/{fournisseur_id}", response_model=schemas.FournisseurResponse, tags=["Referentiels"])
def modifier_fournisseur(fournisseur_id: int, data: schemas.FournisseurCreate, db: Session = Depends(get_db)):
    """Modifie un fournisseur."""
    f = crud.update_fournisseur(db, fournisseur_id, **data.model_dump())
    if not f: raise HTTPException(404, "Fournisseur introuvable")
    return f

@app.get("/health")
def health_check():
    """Verification de l'etat du service."""
    return {"status": "ok", "service": "2saisons-api"}

# ── Point d'entree ──
if __name__ == "__main__":
    import uvicorn
    print("=== 2Saisons - API de Gestion de Stock ===")
    print(f"Swagger : http://localhost:8000/docs")
    print(f"ReDoc   : http://localhost:8000/redoc")
    print(f"Health  : http://localhost:8000/health")
    print(f"API     : http://localhost:8000/")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
