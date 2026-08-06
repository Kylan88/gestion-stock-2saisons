import pytest

import crud
import models
import schemas
import statuses
from database import Base, SessionLocal, engine


@pytest.fixture(autouse=True)
def isolated_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_product(db, name="Produit test", stock=10):
    product = models.Produit(nom=name, stock_actuel=stock, prix_unitaire=100)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def test_negative_stock_movement_is_rejected_at_api_boundary():
    with pytest.raises(ValueError):
        schemas.MouvementCreate(produit_id=1, type_mouvement="entree", quantite=-1)


def test_stock_movement_cannot_be_negative(db):
    product = create_product(db)

    with pytest.raises(ValueError):
        crud.entree_stock(db, product.id, -1)
    with pytest.raises(ValueError):
        crud.sortie_stock(db, product.id, -1)


def test_zone_capacity_is_enforced(db):
    product = create_product(db)
    zone = models.ZoneStockage(nom="Chambre froide", capacite_kg=5, actif=True)
    db.add(zone)
    db.commit()

    crud.stocker_en_zone(db, zone.id, product.id, 4)
    with pytest.raises(ValueError, match="Capacité"):
        crud.stocker_en_zone(db, zone.id, product.id, 2)


def test_dashboard_uses_canonical_statuses(db):
    product = create_product(db)
    lot = models.Lot(code_lot="LOT-STOCK", produit_id=product.id, statut=statuses.EN_STOCK)
    step = models.EtapeProduction(lot=lot, etape="production", ordre=2, statut=statuses.TERMINE)
    db.add_all([lot, step])
    db.commit()

    dashboard = crud.get_stats_dashboard(db)
    production = crud.get_stats_production(db)

    assert dashboard["lots_en_stock"] == 1
    assert dashboard["lots_en_production"] == 0
    assert production["etapes_terminees"] == 1


def test_conditionnement_requires_finished_production_and_uses_its_weight(db):
    product = create_product(db, name="Mangue")
    lot = models.Lot(code_lot="LOT-COND", produit_id=product.id, poids_frais=20, statut=statuses.EN_PRODUCTION)
    production = models.EtapeProduction(
        lot=lot, etape="production", ordre=2, statut=statuses.TERMINE, poids_sortie=10,
    )
    conditionnement = models.EtapeProduction(lot=lot, etape="conditionnement", ordre=3, statut=statuses.EN_ATTENTE)
    db.add_all([lot, production, conditionnement])
    db.commit()

    result = crud.valider_conditionnement(db, lot.id, export_sachets=4, export_poids_sachet=2.5)
    db.refresh(conditionnement)
    db.refresh(lot)

    assert result["reference"] == 10
    assert conditionnement.poids_entree == 10
    assert lot.statut == statuses.CONDITIONNE
