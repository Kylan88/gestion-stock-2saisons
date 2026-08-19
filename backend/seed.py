from database import SessionLocal, engine, Base
from models import (Categorie, Fournisseur, Produit, Lot, MouvementStock,
                    Commande, LigneCommande, EtapeProduction, Chariot,
                    ZoneStockage, StockZone, DemandeTransfert, DemandeTransfertLigne,
                    Reconditionnement)
from datetime import datetime, timedelta
import statuses

DRYER_CONFIG = {
    1: {"chariots": 6, "claies": 42, "kg_par_claie": 6.25},
    2: {"chariots": 12, "claies": 20, "kg_par_claie": 6.5},
}


def _make_chariots(db, ep, dryer, n, total_kg, operateur, heure_remplissage="08:00", heure_entree_sechoir="09:00"):
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
            heure_remplissage=heure_remplissage, heure_entree_sechoir=heure_entree_sechoir,
        ))


def seed_database():
    import sqlalchemy
    try:
        Base.metadata.create_all(bind=engine)
    except:
        pass
    db = SessionLocal()

    try:
        if db.query(Categorie).count() > 0:
            print("[INFO] Base déjà initialisée.")
            return

        cats = [
            Categorie(nom="Fruits Frais", description="Matières premières", couleur="#3f6653"),
            Categorie(nom="Semi-Séchés", description="Produits en cours", couleur="#a04100"),
            Categorie(nom="Fruits Séchés", description="Produits finis", couleur="#116c4a"),
            Categorie(nom="Transformés", description="Jus, confitures", couleur="#584237"),
            Categorie(nom="Emballage", description="Matériel d'emballage", couleur="#8c7166"),
        ]
        db.add_all(cats); db.flush()
        cf, cs, cd, ct, ce = cats

        fournisseurs = [
            Fournisseur(nom="Coopérative de Bazré", contact="Kouassi Jean", telephone="+225 01 02 03 04"),
            Fournisseur(nom="Plantations du Sud", contact="Diallo Moussa", telephone="+225 05 06 07 08"),
            Fournisseur(nom="Ferme Agro-Bélier", contact="N'Guessan Paul", telephone="+225 09 10 11 12"),
        ]
        db.add_all(fournisseurs); db.flush()

        produits = [
            Produit(nom="Ananas Victoria", categorie_id=cf.id, unite_mesure="kg",
                    stock_min=100, stock_actuel=500, prix_unitaire=500),
            Produit(nom="Mangue Kent", categorie_id=cf.id, unite_mesure="kg",
                    stock_min=100, stock_actuel=350, prix_unitaire=400),
            Produit(nom="Banane Plantin", categorie_id=cf.id, unite_mesure="kg",
                    stock_min=80, stock_actuel=20, prix_unitaire=300),
            Produit(nom="Ananas Séché", categorie_id=cd.id, unite_mesure="kg",
                    stock_min=50, stock_actuel=180, prix_unitaire=2500),
            Produit(nom="Mangue Séchée", categorie_id=cd.id, unite_mesure="kg",
                    stock_min=50, stock_actuel=120, prix_unitaire=2200),
            Produit(nom="Banane Séchée", categorie_id=cd.id, unite_mesure="kg",
                    stock_min=30, stock_actuel=45, prix_unitaire=1800),
            Produit(nom="Jus d'Ananas", categorie_id=ct.id, unite_mesure="bouteille",
                    stock_min=200, stock_actuel=80, prix_unitaire=1500),
            Produit(nom="Confiture de Mangue", categorie_id=ct.id, unite_mesure="bouteille",
                    stock_min=100, stock_actuel=250, prix_unitaire=2000),
            Produit(nom="Carton d'Expédition", categorie_id=ce.id, unite_mesure="unité",
                    stock_min=500, stock_actuel=1200, prix_unitaire=250),
            Produit(nom="Fitini Fê", categorie_id=cd.id, unite_mesure="kg",
                    stock_min=30, stock_actuel=0, prix_unitaire=2000),
            Produit(nom="Local Séché", categorie_id=cd.id, unite_mesure="kg",
                    stock_min=30, stock_actuel=0, prix_unitaire=1800),
        ]
        db.add_all(produits); db.flush()

        # ── LOT 1 : Mangue 100% terminé, multi-journées ──
        # Réception → musserie (2 jours) → production (2 jours) → conditionnement → en stock
        lot1 = Lot(code_lot="LOT-2026-001", type_fruit="Mangue",
                   fournisseur_nom="Coopérative de Bazré",
                   produit_id=produits[1].id, fournisseur_id=fournisseurs[0].id,
                   statut=statuses.EN_STOCK, quantite_initiale=500, quantite_restante=0,
                   poids_frais=500, poids_sec_final=445, rendement_global=89.0,
                   date_reception=datetime(2026, 6, 15))
        db.add(lot1); db.flush()

        mus1_j1 = EtapeProduction(lot_id=lot1.id, etape="musserie", ordre=1,
            statut=statuses.TERMINE, dryer=1,
            date_debut=datetime(2026, 6, 16, 8, 0), date_fin=datetime(2026, 6, 16, 12, 0),
            fruits_murs_kg=300, dechets_tri_kg=10, dechets_lavage_kg=8,
            retour_non_mur_kg=5, dechets_production_kg=5,
            poids_sortie=282, perte=23, rendement_pourcentage=94.0, operateur="Kouassi J.")
        mus1_j2 = EtapeProduction(lot_id=lot1.id, etape="musserie", ordre=1,
            statut=statuses.TERMINE, dryer=2,
            date_debut=datetime(2026, 6, 17, 8, 0), date_fin=datetime(2026, 6, 17, 11, 0),
            fruits_murs_kg=200, dechets_tri_kg=8, dechets_lavage_kg=5,
            retour_non_mur_kg=3, dechets_production_kg=4,
            poids_sortie=180, perte=17, rendement_pourcentage=90.0, operateur="Kouassi J.")
        prod1_j1 = EtapeProduction(lot_id=lot1.id, etape="production", ordre=2,
            statut=statuses.TERMINE, dryer=1,
            date_debut=datetime(2026, 6, 17, 8, 0), date_fin=datetime(2026, 6, 17, 16, 0),
            poids_entree=282, poids_sortie=270, perte=12, rendement_pourcentage=95.7,
            nbre_chariots=5, total_claies=210, operateur="Kouassi J.",
            notes="Dryer 1 (5 chariots)")
        prod1_j2 = EtapeProduction(lot_id=lot1.id, etape="production", ordre=2,
            statut=statuses.TERMINE, dryer=2,
            date_debut=datetime(2026, 6, 18, 8, 0), date_fin=datetime(2026, 6, 18, 16, 0),
            poids_entree=180, poids_sortie=175, perte=5, rendement_pourcentage=97.2,
            nbre_chariots=12, total_claies=240, operateur="Kouassi J.",
            notes="Dryer 2 (12 chariots)")
        cond1 = EtapeProduction(lot_id=lot1.id, etape="conditionnement", ordre=3,
            statut=statuses.TERMINE,
            date_debut=datetime(2026, 6, 21, 8, 0), date_fin=datetime(2026, 6, 21, 14, 0),
            poids_entree=445, poids_sortie=445, perte=0, rendement_pourcentage=100.0,
            operateur="Diallo M.")
        db.add_all([mus1_j1, mus1_j2, prod1_j1, prod1_j2, cond1]); db.flush()
        _make_chariots(db, prod1_j1, 1, 5, 282, "Kouassi J.")
        _make_chariots(db, prod1_j2, 2, 12, 180, "Kouassi J.")

        # ── LOT 2 : Ananas en production (musserie terminée, production multi-jours en cours) ──
        lot2 = Lot(code_lot="LOT-2026-002", type_fruit="Ananas",
                   fournisseur_nom="Plantations du Sud",
                   produit_id=produits[0].id, fournisseur_id=fournisseurs[1].id,
                   statut=statuses.EN_PRODUCTION, quantite_initiale=350, quantite_restante=0,
                   poids_frais=350, poids_sec_final=0, rendement_global=None,
                   date_reception=datetime(2026, 6, 20))
        db.add(lot2); db.flush()

        mus2_j1 = EtapeProduction(lot_id=lot2.id, etape="musserie", ordre=1,
            statut=statuses.TERMINE, dryer=1,
            date_debut=datetime(2026, 7, 1, 8, 0), date_fin=datetime(2026, 7, 1, 12, 0),
            fruits_murs_kg=350, dechets_tri_kg=15, dechets_lavage_kg=8,
            retour_non_mur_kg=4, dechets_production_kg=3,
            poids_sortie=335, perte=26, rendement_pourcentage=95.7, operateur="Kouassi J.")
        prod2_j1 = EtapeProduction(lot_id=lot2.id, etape="production", ordre=2,
            statut=statuses.TERMINE, dryer=1,
            date_debut=datetime(2026, 7, 2, 8, 0), date_fin=datetime(2026, 7, 2, 16, 0),
            poids_entree=335, poids_sortie=320, perte=15, rendement_pourcentage=95.5,
            nbre_chariots=6, total_claies=252, operateur="Kouassi J.",
            notes="Dryer 1 (6 chariots)")
        prod2_j2 = EtapeProduction(lot_id=lot2.id, etape="production", ordre=2,
            statut=statuses.EN_COURS, dryer=2,
            date_debut=datetime.now(), date_fin=None,
            poids_entree=0, poids_sortie=0, perte=0, rendement_pourcentage=None,
            nbre_chariots=0, total_claies=0, operateur="",
            notes="Dryer 2 (chargement du jour)")
        db.add_all([mus2_j1, prod2_j1, prod2_j2]); db.flush()
        _make_chariots(db, prod2_j1, 1, 6, 335, "Kouassi J.")

        # ── LOT 3 : Mangue en musserie (saisie du jour en cours → clôture quotidienne) ──
        lot3 = Lot(code_lot="LOT-2026-003", type_fruit="Mangue",
                   fournisseur_nom="Ferme Agro-Bélier",
                   produit_id=produits[1].id, fournisseur_id=fournisseurs[2].id,
                   statut=statuses.EN_MUSSERIE, quantite_initiale=200, quantite_restante=200,
                   poids_frais=200, poids_sec_final=0, rendement_global=None,
                   date_reception=datetime(2026, 7, 22))
        db.add(lot3); db.flush()

        now = datetime.now()
        mus3_jour = EtapeProduction(lot_id=lot3.id, etape="musserie", ordre=1,
            statut=statuses.EN_COURS, dryer=1,
            date_debut=now, date_fin=None,
            fruits_murs_kg=80, dechets_tri_kg=5, dechets_lavage_kg=3,
            retour_non_mur_kg=2, dechets_production_kg=2,
            poids_sortie=73, perte=10, rendement_pourcentage=91.2, operateur="Kouassi J.")
        db.add(mus3_jour); db.flush()

        # ── LOT 4 : Banane en réception (pas encore d'étapes) ──
        lot4 = Lot(code_lot="LOT-2026-004", type_fruit="Banane",
                   fournisseur_nom="Marché de Bouaké",
                   produit_id=produits[2].id, fournisseur_id=fournisseurs[2].id,
                   statut=statuses.RECEPTION, quantite_initiale=150, quantite_restante=150,
                   poids_frais=150, poids_sec_final=0, rendement_global=None,
                   date_reception=datetime(2026, 7, 25))
        db.add(lot4); db.flush()

        zones = [
            ZoneStockage(nom="Chambre Froide 1", type_zone="froid", usage="local",
                        temperature_consigne=4, capacite_kg=1000),
            ZoneStockage(nom="Chambre Froide 2", type_zone="froid", usage="export",
                        temperature_consigne=2, capacite_kg=500),
        ]
        db.add_all(zones); db.flush()

        stocks_zone = [
            StockZone(zone_id=zones[0].id, lot_id=lot1.id, produit_id=produits[4].id,
                      quantite=180, date_entree=datetime(2026, 7, 2)),
            StockZone(zone_id=zones[1].id, lot_id=lot1.id, produit_id=produits[4].id,
                      quantite=120, sachets=1200, date_entree=datetime(2026, 6, 22)),
        ]
        db.add_all(stocks_zone)

        mouvements = [
            MouvementStock(produit_id=produits[1].id, lot_id=lot1.id, type_mouvement="entrée",
                quantite=500, quantite_avant=0, quantite_apres=500,
                motif="Réception fruits frais", responsable="Kouassi J.",
                date_mouvement=now - timedelta(days=64)),
            MouvementStock(produit_id=produits[4].id, lot_id=lot1.id, type_mouvement="entrée",
                quantite=300, quantite_avant=0, quantite_apres=300,
                motif="Production lot séché", responsable="N'Guessan P.",
                date_mouvement=now - timedelta(days=22)),
            MouvementStock(produit_id=produits[4].id, lot_id=lot1.id, type_mouvement="sortie",
                quantite=20, quantite_avant=300, quantite_apres=280,
                motif="Expédition client Abidjan", responsable="Diallo M.",
                date_mouvement=now - timedelta(days=5)),
            MouvementStock(produit_id=produits[1].id, lot_id=lot1.id, type_mouvement="sortie",
                quantite=500, quantite_avant=500, quantite_apres=0,
                motif="Transfert vers musserie", responsable="Kouassi J.",
                date_mouvement=now - timedelta(days=63)),
        ]
        db.add_all(mouvements)
        db.commit()

        print("[OK] Données de démonstration insérées avec succès !")
        print(f"   {len(cats)} catégories, {len(produits)} produits, {len(fournisseurs)} fournisseurs")
        print(f"   4 lots (1 en stock, 1 en production, 1 en musserie, 1 en réception)")
        print(f"   2 zones, {len(stocks_zone)} stocks zone, {len(mouvements)} mouvements")

    finally:
        db.close()

if __name__ == "__main__":
    print("Seed 2Saisons - Insertion des données de démonstration")
    print("=" * 50)
    seed_database()
