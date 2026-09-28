"""Seed 2Saisons — données de démo cohérentes avec les flux actuels.

- Dates relatives (aujourd'hui / hier) pour que les pages journalières
  (murisserie du jour, chariots, conditionnement J+1) affichent des données.
- Murisserie/production saisies via crud (calculs sortie/perte/reste garantis).
- Transfert, reconditionnement et commande via crud (stocksnames cohérents).
"""
from database import SessionLocal, engine, Base
from models import (Categorie, Fournisseur, Produit, Lot, MouvementStock,
                    EtapeProduction, Chariot, ZoneStockage, StockZone)
from datetime import datetime, timedelta
import crud
import statuses

DRYER_CONFIG = {
    1: {"chariots": 6, "claies": 42, "kg_par_claie": 6.25},
    2: {"chariots": 12, "claies": 20, "kg_par_claie": 6.25},
}


def _make_chariots(db, ep, dryer, n, total_kg, operateur, heure_remplissage="08:00", heure_entree_dryer="09:00"):
    """Crée n chariots pour une étape production (poids réparti)."""
    config = DRYER_CONFIG.get(dryer, {"chariots": 6, "claies": 42})
    n = min(n, config["chariots"])
    q = round(total_kg / n, 2) if n else 0
    for i in range(1, n + 1):
        db.add(Chariot(
            etape_production_id=ep.id, lot_id=ep.lot_id,
            numero_chariot=i, dryer=dryer, nbre_chariots=n,
            total_claies=config["claies"] * n, quantite_totale=q,
            operateur=operateur,
            heure_remplissage=heure_remplissage, heure_entree_dryer=heure_entree_dryer,
        ))


def seed_database():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
    db = SessionLocal()
    now = datetime.now()
    today = now.replace(hour=8, minute=0, second=0, microsecond=0)
    hier = today - timedelta(days=1)

    try:
        if db.query(Categorie).count() > 0:
            print("[INFO] Base déjà initialisée.")
            return

        # ── Référentiels ──
        cf = Categorie(nom="Fruits Frais", description="Matières premières", couleur="#3f6653")
        cd = Categorie(nom="Fruits Séchés", description="Produits finis", couleur="#116c4a")
        db.add_all([cf,
                    Categorie(nom="Semi-Séchés", description="Produits en cours", couleur="#a04100"),
                    cd,
                    Categorie(nom="Transformés", description="Jus, confitures", couleur="#584237"),
                    Categorie(nom="Emballage", description="Matériel d'emballage", couleur="#8c7166")])
        db.flush()

        fournisseurs = [
            Fournisseur(nom="Coopérative de Bazré", contact="Kouassi Jean", telephone="+225 01 02 03 04"),
            Fournisseur(nom="Plantations du Sud", contact="Diallo Moussa", telephone="+225 05 06 07 08"),
            Fournisseur(nom="Ferme Agro-Bélier", contact="N'Guessan Paul", telephone="+225 09 10 11 12"),
            Fournisseur(nom="Marché de Bouaké", contact="Traoré Awa", telephone="+225 07 08 09 10"),
        ]
        db.add_all(fournisseurs)
        db.flush()

        # Catalogue : frais + produits de flux (noms exacts attendus par les flux).
        produits = {
            "mangue_frais": Produit(nom="Mangue Kent", categorie_id=cf.id, unite_mesure="kg", prix_unitaire=400),
            "ananas_frais": Produit(nom="Ananas", categorie_id=cf.id, unite_mesure="kg", prix_unitaire=500),
            "banane_frais": Produit(nom="Banane", categorie_id=cf.id, unite_mesure="kg", prix_unitaire=300),
            "local": Produit(nom="Local", categorie_id=cd.id, unite_mesure="kg", prix_unitaire=1800),
            "export": Produit(nom="Export", categorie_id=cd.id, unite_mesure="kg", prix_unitaire=2500),
            "fitini": Produit(nom="Fitini Fê", categorie_id=cd.id, unite_mesure="kg", prix_unitaire=2000),
            "dechets": Produit(nom="Déchets", categorie_id=cd.id, unite_mesure="kg", prix_unitaire=200),
            "rhum": Produit(nom="Rhum arrangé", categorie_id=cd.id, unite_mesure="kg", prix_unitaire=3000),
        }
        db.add_all(produits.values())
        db.flush()

        zones = [
            ZoneStockage(nom="Chambre Froide 1", type_zone="froid", usage="local",
                         temperature_consigne=4, capacite_kg=1000),
            ZoneStockage(nom="Chambre Froide 2", type_zone="froid", usage="export",
                         temperature_consigne=2, capacite_kg=500),
        ]
        db.add_all(zones)
        db.flush()

        # ── LOT 1 : Mangue terminée, en stock (historique complet) ──
        # Murisserie : J1 net 300 + tri 10 ; J2 net 200 + tri 8 → reste 0.
        lot1 = Lot(code_lot="LOT-2026-001", type_fruit="Mangue",
                   fournisseur_nom="Coopérative de Bazré",
                   produit_id=produits["mangue_frais"].id, fournisseur_id=fournisseurs[0].id,
                   statut=statuses.CONDITIONNE, quantite_initiale=500, quantite_restante=0,
                   poids_frais=500, poids_sec_final=435, rendement_global=87.0,
                   ecart_bilan_pourcentage=2.25,
                   export_cartons=12, export_poids_sachet=2.5,
                   local_cartons=8, local_poids_sachet=2.5,
                   dechets_cartons=4, dechets_poids_sachet=2.5,
                   rhum_cartons=2, rhum_poids_sachet=2.5,
                   fitini_fe_cartons=3, fitini_fe_poids_sachet=2.5,
                   date_reception=today - timedelta(days=32))
        db.add(lot1)
        db.flush()
        j1, j2 = today - timedelta(days=30), today - timedelta(days=29)
        db.add_all([
            EtapeProduction(lot_id=lot1.id, etape="murisserie", ordre=1, statut=statuses.TERMINE, dryer=1,
                            date_debut=j1, date_fin=j1 + timedelta(hours=4),
                            fruits_murs_kg=300, dechets_tri_kg=10, dechets_lavage_kg=8,
                            retour_non_mur_kg=5, retour_mure_kg=0, dechets_production_kg=5,
                            poids_sortie=282, perte=23, rendement_pourcentage=94.0, operateur="Kouassi J."),
            EtapeProduction(lot_id=lot1.id, etape="murisserie", ordre=1, statut=statuses.TERMINE, dryer=2,
                            date_debut=j2, date_fin=j2 + timedelta(hours=3),
                            fruits_murs_kg=200, dechets_tri_kg=8, dechets_lavage_kg=5,
                            retour_non_mur_kg=3, retour_mure_kg=0, dechets_production_kg=4,
                            poids_sortie=188, perte=17, rendement_pourcentage=94.0, operateur="Kouassi J."),
        ])
        db.flush()
        p1j1 = EtapeProduction(lot_id=lot1.id, etape="production", ordre=2, statut=statuses.TERMINE, dryer=1,
                               date_debut=j2, date_fin=j2 + timedelta(hours=8),
                               poids_entree=282, poids_sortie=270, perte=12, rendement_pourcentage=95.7,
                               poids_sec_kg=270, nbre_chariots=5, total_claies=210,
                               operateur="Kouassi J.", notes="Dryer 1 (5 chariots)")
        p1j2 = EtapeProduction(lot_id=lot1.id, etape="production", ordre=2, statut=statuses.TERMINE, dryer=2,
                               date_debut=j2 + timedelta(days=1), date_fin=j2 + timedelta(days=1, hours=8),
                               poids_entree=188, poids_sortie=175, perte=13, rendement_pourcentage=93.1,
                               poids_sec_kg=175, nbre_chariots=12, total_claies=240,
                               operateur="Kouassi J.", notes="Dryer 2 (12 chariots)")
        cond1 = EtapeProduction(lot_id=lot1.id, etape="conditionnement", ordre=3, statut=statuses.TERMINE,
                                date_debut=j2 + timedelta(days=3), date_fin=j2 + timedelta(days=3, hours=6),
                                poids_entree=445, poids_sortie=435, perte=10, rendement_pourcentage=87.0,
                                operateur="Diallo M.")
        db.add_all([p1j1, p1j2, cond1])
        db.flush()
        _make_chariots(db, p1j1, 1, 5, 270, "Kouassi J.")
        _make_chariots(db, p1j2, 2, 12, 175, "Kouassi J.")
        db.flush()

        # ── LOT 2 : Ananas en murisserie, saisie du jour ouverte ──
        lot2 = Lot(code_lot="LOT-2026-002", type_fruit="Ananas",
                   fournisseur_nom="Plantations du Sud",
                   produit_id=produits["ananas_frais"].id, fournisseur_id=fournisseurs[1].id,
                   statut=statuses.RECEPTION, quantite_initiale=350, quantite_restante=350,
                   poids_frais=350, date_reception=today - timedelta(days=2))
        db.add(lot2)
        db.flush()
        crud.valider_murisserie(db, lot2.id, dryer=1, fruits_murs_kg=120.0,
                                dechets_tri_kg=4.0, dechets_lavage_kg=3.0,
                                retour_non_mur_kg=2.0, dechets_production_kg=2.0,
                                operateur="Kouassi J.")

        # ── LOT 3 : Mangue, murisserie du jour clôturée → production du jour en cours ──
        lot3 = Lot(code_lot="LOT-2026-003", type_fruit="Mangue",
                   fournisseur_nom="Ferme Agro-Bélier",
                   produit_id=produits["mangue_frais"].id, fournisseur_id=fournisseurs[2].id,
                   statut=statuses.RECEPTION, quantite_initiale=2000, quantite_restante=2000,
                   poids_frais=2000, date_reception=today - timedelta(days=3))
        db.add(lot3)
        db.flush()
        crud.valider_murisserie(db, lot3.id, dryer=1, fruits_murs_kg=1800.0,
                                dechets_tri_kg=30.0, dechets_lavage_kg=20.0,
                                retour_non_mur_kg=10.0, dechets_production_kg=30.0,
                                operateur="Kouassi J.")
        crud.cloturer_murisserie(db, lot3.id, today.date().isoformat())
        crud.valider_production(
            db, lot3.id, dryer=1, nbre_chariots=6, quantite_totale=1575.0,
            operateur="Kouassi J.",
            chariots=[{"numero_chariot": i + 1, "heure_remplissage": f"08:{i:02d}",
                       "heure_entree_dryer": f"09:{i:02d}"} for i in range(6)],
        )

        # ── LOT 4 : Banane, production d'hier → conditionnement dispo aujourd'hui ──
        # Murisserie hier : net 695 + tri 20 → reste 85.
        lot4 = Lot(code_lot="LOT-2026-004", type_fruit="Banane",
                   fournisseur_nom="Marché de Bouaké",
                   produit_id=produits["banane_frais"].id, fournisseur_id=fournisseurs[3].id,
                   statut=statuses.EN_CONDITIONNEMENT, quantite_initiale=800, quantite_restante=85,
                   poids_frais=800, date_reception=today - timedelta(days=4))
        db.add(lot4)
        db.flush()
        db.add(EtapeProduction(lot_id=lot4.id, etape="murisserie", ordre=1, statut=statuses.TERMINE, dryer=2,
                               date_debut=hier, date_fin=hier + timedelta(hours=4),
                               fruits_murs_kg=700, dechets_tri_kg=20, dechets_lavage_kg=15,
                               retour_non_mur_kg=10, retour_mure_kg=5, dechets_production_kg=25,
                               poids_sortie=645, perte=60, rendement_pourcentage=92.1,
                               operateur="Kouassi J."))
        db.flush()
        prod4 = EtapeProduction(lot_id=lot4.id, etape="production", ordre=2, statut=statuses.TERMINE, dryer=2,
                                date_debut=hier, date_fin=hier + timedelta(hours=8),
                                poids_entree=645, poids_sortie=600, perte=45,
                                poids_sec_kg=150, nbre_chariots=5, total_claies=100,
                                operateur="Kouassi J.", notes="Dryer 2 (5 chariots)")
        db.add(prod4)
        db.flush()
        _make_chariots(db, prod4, 2, 5, 600, "Kouassi J.")
        db.flush()
        # Conditionnement du jour (150 kg secs : 100 export + 50 local).
        crud.valider_conditionnement_dryer(db, lot4.id, dryer=2, poids_sec_kg=150.0,
                                           export_cartons=2, export_sachets=28, export_poids_sachet=2.5,
                                           local_sachets=20, local_poids_sachet=2.5,
                                           responsable="Diallo M.")
        # Demande de transfert en attente (page Transfert).
        # Note : les 2 cartons export du lot 4 sont déjà en chambre froide
        # (auto-stock à la saisie) — on demande le reliquat fitini du lot 1.
        from schemas import DemandeTransfertLigneCreate
        crud.creer_demande_transfert(
            db, lot1.id,
            [DemandeTransfertLigneCreate(type_flux="fitini_fe", nb_cartons=3, zone_id=zones[0].id)],
            responsable="Diallo M.", notes="Démo : transfert en attente",
        )

        # ── LOT 5 : Mangue en réception aujourd'hui ──
        lot5 = Lot(code_lot="LOT-2026-005", type_fruit="Mangue",
                   fournisseur_nom="Coopérative de Bazré",
                   produit_id=produits["mangue_frais"].id, fournisseur_id=fournisseurs[0].id,
                   statut=statuses.RECEPTION, quantite_initiale=400, quantite_restante=400,
                   poids_frais=400, date_reception=today)
        db.add(lot5)
        db.flush()

        # ── Transfert lot 1 → chambre froide (lot épuisé → EN_STOCK) ──
        from schemas import DemandeTransfertLigneCreate as Ligne
        dem1 = crud.creer_demande_transfert(
            db, lot1.id,
            [Ligne(type_flux="local", nb_cartons=8, zone_id=zones[0].id),
             Ligne(type_flux="export", nb_cartons=12, zone_id=zones[1].id)],
            responsable="Diallo M.", notes="Démo : transfert validé",
        )
        crud.valider_demande_transfert(db, dem1.id)

        # ── Reconditionnement lot 1 (2 cartons local → sachets 100g) ──
        crud.creer_reconditionnement(db, lot1.id, "local", nb_cartons_entree=2,
                                     dechet_kg=1.0, nb_sachets_sortis=280,
                                     responsable="N'Guessan P.", notes="Démo")

        # ── Commande en attente ──
        crud.create_commande(
            db, client_nom="Marché Central Abidjan",
            lignes_data=[
                {"produit_id": produits["local"].id, "lot_id": lot1.id,
                 "quantite": 2, "unite": "carton", "prix_unitaire": 1800},
                {"produit_id": produits["export"].id, "lot_id": lot1.id,
                 "quantite": 1, "unite": "carton", "prix_unitaire": 2500},
            ],
            notes="Démo : commande en attente",
        )

        db.add_all([
            MouvementStock(produit_id=produits["mangue_frais"].id, lot_id=lot1.id,
                           type_mouvement="entrée", quantite=500,
                           quantite_avant=0, quantite_apres=500,
                           motif="Réception fruits frais", responsable="Kouassi J.",
                           date_mouvement=today - timedelta(days=32)),
            MouvementStock(produit_id=produits["local"].id, lot_id=lot1.id,
                           type_mouvement="entrée", quantite=120,
                           quantite_avant=0, quantite_apres=120,
                           motif="Transfert chambre froide", responsable="Diallo M.",
                           date_mouvement=today - timedelta(days=27)),
            MouvementStock(produit_id=produits["ananas_frais"].id, lot_id=lot2.id,
                           type_mouvement="entrée", quantite=350,
                           quantite_avant=0, quantite_apres=350,
                           motif="Réception fruits frais", responsable="Kouassi J.",
                           date_mouvement=today - timedelta(days=2)),
        ])
        db.commit()

        print("[OK] Données de démonstration insérées avec succès !")
        print("   5 catégories, 8 produits catalogue, 4 fournisseurs")
        print("   5 lots (1 en stock, 1 en murisserie + 1 en production du jour, "
              "1 à conditionner, 1 en réception)")
        print("   2 zones, 1 transfert validé + 1 en attente, 1 reconditionnement, 1 commande")

    finally:
        db.close()


if __name__ == "__main__":
    print("Seed 2Saisons - Insertion des données de démonstration")
    print("=" * 50)
    seed_database()
