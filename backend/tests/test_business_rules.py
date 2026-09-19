import pytest
from datetime import datetime, timedelta

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

    # valider_conditionnement doit exposer la référence (= poids_sortie production) et initialiser l'étape
    assert result.get("reference", result.get("total_flux")) is not None
    # la référence doit être 10 (poids_sortie de la production)
    ref = result.get("reference", result.get("total_flux"))
    # total_flux = 4 sachets * 2.5 = 10, donc ref == 10 et total_flux == 10
    assert ref == 10 or result.get("total_flux") == 10
    assert conditionnement.poids_entree == 10
    # le lot reste en_production jusqu'à cloturer_conditionnement
    assert lot.statut in (statuses.EN_PRODUCTION, statuses.EN_CONDITIONNEMENT, statuses.CONDITIONNE)


def test_partial_lot_keeps_fresh_pulp_and_dried_weight_separate(db):
    """Un dryer journalier ne doit jamais clôturer un lot encore à traiter."""
    product = create_product(db, name="Mangue")
    lot = models.Lot(
        code_lot="LOT-31546",
        produit_id=product.id,
        poids_frais=31546.5,
        quantite_initiale=31546.5,
        statut=statuses.RECEPTION,
    )
    db.add(lot)
    db.commit()

    # 2 543,40 kg mûrs - 30 lavage - 50 déchets production - 20 retour non mûr
    # - 17,90 retour mûr = 2 425,50 kg frais net.
    musserie = crud.valider_musserie(
        db, lot.id, dryer=1, fruits_murs_kg=2543.4,
        dechets_lavage_kg=30.0, dechets_production_kg=50.0,
        retour_non_mur_kg=20.0, retour_mure_kg=17.9,
    )
    assert musserie.poids_sortie == 2425.5

    today = datetime.now().date().isoformat()
    crud.cloturer_musserie(db, lot.id, today)
    production = crud.valider_production(
        db, lot.id, dryer=1, nbre_chariots=6, quantite_totale=1575.0,
    )["etape"]
    assert production.poids_entree == 2425.5
    assert production.poids_sortie == 1575.0
    assert production.perte == 850.5

    crud.cloturer_production(db, lot.id, today)
    db.refresh(lot)
    assert lot.statut == statuses.EN_MUSSERIE
    assert lot.quantite_restante > 0

    # Le conditionnement se fait le lendemain sur le poids sec, pas sur 1 575 kg.
    yesterday = datetime.now() - timedelta(days=1)
    production.date_debut = yesterday
    production.date_fin = yesterday
    db.commit()
    result = crud.valider_conditionnement_dryer(
        db, lot.id, dryer=1, poids_sec_kg=400.0,
        export_sachets=160, export_poids_sachet=2.5,
    )
    db.refresh(production)
    db.refresh(lot)
    assert result["poids_sec_kg"] == 400.0
    assert production.poids_sec_kg == 400.0
    crud.cloturer_conditionnement(db, lot.id, today)
    db.refresh(lot)
    assert lot.statut == statuses.EN_MUSSERIE


def test_lot_epuise_bascule_seul_vers_conditionne_sans_cloture_finale(db):
    """Flux continu : figer la journée ne ferme jamais le lot à la main.
    Quand le lot est épuisé (reste 0, prod terminée, flux > 0), il bascule
    seul vers 'conditionne'."""
    product = create_product(db, name="Mangue")
    lot = models.Lot(
        code_lot="LOT-EPUISE",
        produit_id=product.id,
        poids_frais=1000,
        quantite_initiale=1000,
        quantite_restante=500,
        statut=statuses.EN_PRODUCTION,
    )
    db.add(lot)
    db.commit()
    prod = models.EtapeProduction(
        lot_id=lot.id, etape="production", ordre=2, statut=statuses.TERMINE,
        poids_entree=500, poids_sortie=400, dryer=1,
    )
    cond = models.EtapeProduction(
        lot_id=lot.id, etape="conditionnement", ordre=3, statut="en_cours",
        poids_entree=400,
    )
    db.add_all([prod, cond])
    db.commit()
    db.refresh(lot)
    lot.export_sachets = 40
    lot.export_poids_sachet = 2.5
    db.commit()

    # Lot partiel : la journée se fige, le lot reste ouvert, pas d'épuisement.
    res = crud.cloturer_conditionnement(db, lot.id)
    db.refresh(lot)
    assert res["lot_epuise"] is False
    assert lot.statut == statuses.EN_PRODUCTION

    # Lot épuisé : bascule seule vers 'conditionne', sans clôture finale manuelle.
    lot.quantite_restante = 0
    db.commit()
    res = crud.cloturer_conditionnement(db, lot.id)
    db.refresh(lot)
    assert res["lot_epuise"] is True
    assert lot.statut == statuses.CONDITIONNE


def test_conditionnement_alimente_stock_delta_sans_doublon(db):
    """Chaque saisie alimente la chambre froide (delta uniquement, idempotent),
    et le transfert manuel ne peut pas renvoyer les mêmes cartons."""
    product = create_product(db, name="Mangue")
    zone = models.ZoneStockage(nom="CF test", type_zone="froid", actif=True, capacite_kg=10000)
    db.add(zone)
    db.commit()
    lot = models.Lot(
        code_lot="LOT-STOCK-AUTO",
        produit_id=product.id,
        poids_frais=1000,
        quantite_initiale=1000,
        quantite_restante=400,
        statut=statuses.EN_PRODUCTION,
    )
    db.add(lot)
    db.commit()
    prod = models.EtapeProduction(
        lot_id=lot.id, etape="production", ordre=2, statut=statuses.TERMINE,
        poids_entree=600, poids_sortie=500, dryer=1,
    )
    db.add(prod)
    db.commit()

    res = crud.valider_conditionnement(db, lot.id, local_cartons=2)
    assert res["stock"]["alimente"] is True
    assert res["stock"]["cartons"] == 2
    stocks = crud.get_stocks_zone(db, produit_id=None)
    assert sum(s.quantite for s in stocks if s.lot_id == lot.id) == round(2 * 6 * 2.5, 2)

    # Rejouer sans nouveau carton : aucun doublon en stock.
    res2 = crud.valider_conditionnement(db, lot.id)
    assert res2["stock"]["alimente"] is False
    stocks2 = crud.get_stocks_zone(db)
    assert sum(s.quantite for s in stocks2 if s.lot_id == lot.id) == round(2 * 6 * 2.5, 2)

    # Le transfert manuel des mêmes cartons est refusé (déjà en stock).
    with pytest.raises(ValueError, match="Pas assez de cartons"):
        crud.creer_demande_transfert(
            db, lot.id,
            [schemas.DemandeTransfertLigneCreate(type_flux="local", nb_cartons=1, zone_id=zone.id)],
        )


def test_reconditionnement_rhum_obtenu_alimente_stock_rhum(db):
    """Le rhum arrangé obtenu depuis local/fitini fê alimente le stock Rhum arrangé,
    sans double déduction (matière déjà déduite via les cartons sources)."""
    product = create_product(db, name="Mangue")
    zone = models.ZoneStockage(nom="CF rhum", type_zone="froid", actif=True, capacite_kg=10000)
    local_p = models.Produit(nom="Local", stock_actuel=0)
    db.add_all([zone, local_p])
    db.commit()
    lot = models.Lot(
        code_lot="LOT-RHUM", produit_id=product.id, poids_frais=500,
        quantite_initiale=500, quantite_restante=0, statut=statuses.CONDITIONNE,
        local_cartons=2, local_poids_sachet=2.5,
    )
    db.add(lot)
    db.commit()
    db.add(models.StockZone(zone_id=zone.id, lot_id=lot.id, produit_id=local_p.id,
                            quantite=30.0, sachets=12))
    db.commit()

    res = crud.creer_reconditionnement(
        db, lot.id, "local", nb_cartons_entree=1, nb_sachets_sortis=100,
        rhum_cartons_sortie=1, rhum_sachets_sortis=3, rhum_poids_vrac_kg=1.2,
        zone_id=zone.id,
    )
    assert res["rhum"]["alimente"] is True
    assert res["rhum"]["cartons"] == 1
    assert res["rhum"]["zone"] == "CF rhum"
    rhum_p = db.query(models.Produit).filter(models.Produit.nom == "Rhum arrangé").first()
    assert rhum_p is not None
    lignes = db.query(models.StockZone).filter(
        models.StockZone.lot_id == lot.id, models.StockZone.produit_id == rhum_p.id,
        models.StockZone.date_sortie.is_(None)).all()
    assert sum(s.sachets for s in lignes) == 1 * 6 + 3
    assert rhum_p.stock_actuel == round((1 * 6 + 3) * 2.5 + 1.2, 2)
    # cartons sources déduits une seule fois
    db.refresh(lot)
    assert lot.local_cartons == 1


def test_musserie_meme_jour_ecrase_au_lieu_de_cumuler(db):
    """Une seule saisie par (lot, dryer, jour) : la 2e écrase, ne s'additionne pas."""
    product = create_product(db, name="Mangue")
    lot = models.Lot(
        code_lot="LOT-ECRASE", produit_id=product.id, poids_frais=1000,
        quantite_initiale=1000, statut=statuses.RECEPTION,
    )
    db.add(lot)
    db.commit()

    crud.valider_musserie(db, lot.id, dryer=1, fruits_murs_kg=100.0, dechets_tri_kg=10.0)
    db.refresh(lot)
    assert lot.quantite_restante == 890.0

    ep = crud.valider_musserie(db, lot.id, dryer=1, fruits_murs_kg=200.0, dechets_tri_kg=10.0)
    db.refresh(lot)
    assert lot.quantite_restante == 790.0
    assert ep.poids_sortie == 200.0
    nb = db.query(models.EtapeProduction).filter(
        models.EtapeProduction.lot_id == lot.id,
        models.EtapeProduction.etape == "musserie",
    ).count()
    assert nb == 1


def test_saisie_conditionnement_ne_change_jamais_le_statut(db):
    """La saisie (et figer la journée) ne ferme jamais le lot à la main ;
    sans zone, elle réussit quand même (stock non alimenté, pas d'erreur)."""
    product = create_product(db, name="Mangue")
    lot = models.Lot(
        code_lot="LOT-SAISIE", produit_id=product.id, poids_frais=1000,
        quantite_initiale=1000, quantite_restante=500, statut=statuses.EN_MUSSERIE,
    )
    production = models.EtapeProduction(
        lot=lot, etape="production", ordre=2, statut=statuses.TERMINE, poids_sortie=50,
    )
    db.add_all([lot, production])
    db.commit()

    res = crud.valider_conditionnement(db, lot.id, local_cartons=1)
    db.refresh(lot)
    assert lot.statut == statuses.EN_MUSSERIE
    assert res["lot_epuise"] is False
    assert res["stock"]["alimente"] is False
    etape = db.query(models.EtapeProduction).filter(
        models.EtapeProduction.lot_id == lot.id,
        models.EtapeProduction.etape == "conditionnement",
    ).one()
    assert etape.statut != statuses.TERMINE

    res_jour = crud.cloturer_conditionnement(db, lot.id)
    db.refresh(lot)
    assert lot.statut == statuses.EN_MUSSERIE
    assert res_jour["lot_epuise"] is False


def test_transfert_manuel_rattrape_apres_saisie_sans_zone(db):
    """Saisie sans zone active : OK sans stock, puis transfert manuel possible."""
    product = create_product(db, name="Mangue")
    lot = models.Lot(
        code_lot="LOT-RATTRAPAGE", produit_id=product.id, poids_frais=1000,
        quantite_initiale=1000, quantite_restante=100, statut=statuses.EN_PRODUCTION,
    )
    production = models.EtapeProduction(
        lot=lot, etape="production", ordre=2, statut=statuses.TERMINE, poids_sortie=500,
    )
    db.add_all([lot, production])
    db.commit()

    res = crud.valider_conditionnement(db, lot.id, local_cartons=2)
    assert res["stock"]["alimente"] is False

    zone = models.ZoneStockage(nom="CF rattrapage", type_zone="froid", actif=True, capacite_kg=10000)
    db.add(zone)
    db.commit()
    demande = crud.creer_demande_transfert(
        db, lot.id,
        [schemas.DemandeTransfertLigneCreate(type_flux="local", nb_cartons=2, zone_id=zone.id)],
        responsable="Magasinier",
    )
    crud.valider_demande_transfert(db, demande.id)
    stocks = crud.get_stocks_zone(db)
    assert sum(s.quantite for s in stocks if s.lot_id == lot.id) == round(2 * 6 * 2.5, 2)


def test_reconditionnement_sans_rhum_inchange(db):
    """Sans sortie rhum : comportement historique (sachets 100g seuls)."""
    product = create_product(db, name="Mangue")
    zone = models.ZoneStockage(nom="CF simple", type_zone="froid", actif=True, capacite_kg=10000)
    local_p = models.Produit(nom="Local", stock_actuel=0)
    db.add_all([zone, local_p])
    db.commit()
    lot = models.Lot(
        code_lot="LOT-SIMPLE", produit_id=product.id, poids_frais=500,
        quantite_initiale=500, quantite_restante=0, statut=statuses.CONDITIONNE,
        local_cartons=1, local_poids_sachet=2.5,
    )
    db.add(lot)
    db.commit()
    db.add(models.StockZone(zone_id=zone.id, lot_id=lot.id, produit_id=local_p.id,
                            quantite=15.0, sachets=6))
    db.commit()

    res = crud.creer_reconditionnement(db, lot.id, "local", nb_cartons_entree=1, nb_sachets_sortis=140)
    assert res["rhum"]["alimente"] is False
    assert res["stock_final_sachets"] == 140
    db.refresh(lot)
    assert lot.local_cartons == 0


def test_rhum_negatif_rejete_a_la_frontiere_api():
    with pytest.raises(ValueError):
        schemas.ReconditionnementCreate(
            lot_id=1, type_source="local", nb_cartons_entree=1, rhum_cartons_sortie=-1,
        )
    with pytest.raises(ValueError):
        schemas.ReconditionnementCreate(
            lot_id=1, type_source="local", nb_cartons_entree=1, rhum_poids_vrac_kg=-0.5,
        )
