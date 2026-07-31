from database import SessionLocal, engine, Base
from models import (Categorie, Fournisseur, Produit, Lot, MouvementStock,
                    Commande, LigneCommande, EtapeProduction,
                    ZoneStockage, StockZone, DemandeTransfert, DemandeTransfertLigne,
                    Reconditionnement)
from datetime import datetime, timedelta

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

        lots = [
            Lot(code_lot="LOT-2026-001", type_fruit="Mangue", fournisseur_nom="Coopérative Korhogo",
                produit_id=produits[0].id, fournisseur_id=fournisseurs[0].id,
                statut="en stock", quantite_initiale=500, quantite_restante=200,
                poids_frais=500, poids_sec_final=0, rendement_global=None,
                date_reception=datetime(2026, 6, 15)),
            Lot(code_lot="LOT-2026-002", type_fruit="Banane", fournisseur_nom="Ferme Bio Man",
                produit_id=produits[1].id, fournisseur_id=fournisseurs[1].id,
                statut="en stock", quantite_initiale=350, quantite_restante=120,
                poids_frais=350, poids_sec_final=0, rendement_global=None,
                date_reception=datetime(2026, 6, 20)),
            Lot(code_lot="LOT-2026-003", type_fruit="Mangue",
                produit_id=produits[3].id, fournisseur_id=fournisseurs[0].id,
                statut="en stock", quantite_initiale=200, quantite_restante=180,
                poids_frais=0, poids_sec_final=200, rendement_global=None,
                date_reception=datetime(2026, 7, 1), date_peremption=datetime(2027, 6, 28)),
            Lot(code_lot="LOT-2026-004", type_fruit="Banane",
                statut="en production", quantite_initiale=150, quantite_restante=150,
                poids_frais=350, poids_sec_final=0, rendement_global=None,
                date_reception=datetime(2026, 7, 5)),
            Lot(code_lot="LOT-2026-005", type_fruit="Ananas", fournisseur_nom="Marché de Bouaké",
                produit_id=produits[2].id, fournisseur_id=fournisseurs[2].id,
                statut="réception", quantite_initiale=200, quantite_restante=200,
                poids_frais=200, poids_sec_final=0, rendement_global=None,
                date_reception=datetime(2026, 7, 22)),
        ]
        db.add_all(lots); db.flush()

        # Étapes de production (3 étapes : musserie, production, conditionnement)
        etapes = [
            # Lot 1 : complet
            EtapeProduction(lot_id=lots[0].id, etape="musserie", ordre=1, statut="terminé",
                date_debut=datetime(2026, 6, 16, 8, 0), date_fin=datetime(2026, 6, 16, 12, 0),
                poids_entree=500, poids_sortie=450, perte=50, rendement_pourcentage=90.0,
                operateur="Kouassi J.", fruits_murs_kg=450, dechets_tri_kg=30,
                dechets_lavage_kg=10, retour_non_mur_kg=5, dechets_production_kg=5),
            EtapeProduction(lot_id=lots[0].id, etape="production", ordre=2, statut="terminé",
                date_debut=datetime(2026, 6, 17, 8, 0), date_fin=datetime(2026, 6, 17, 16, 0),
                poids_entree=450, poids_sortie=440, perte=10, rendement_pourcentage=97.8,
                operateur="Kouassi J."),
            EtapeProduction(lot_id=lots[0].id, etape="conditionnement", ordre=3, statut="terminé",
                date_debut=datetime(2026, 6, 21, 8, 0), date_fin=datetime(2026, 6, 21, 14, 0),
                poids_entree=440, poids_sortie=435, perte=5, rendement_pourcentage=98.9,
                operateur="Diallo M."),
            # Lot 4 : en cours (musserie terminée, production en cours)
            EtapeProduction(lot_id=lots[3].id, etape="musserie", ordre=1, statut="terminé",
                date_debut=datetime(2026, 7, 6, 8, 0), date_fin=datetime(2026, 7, 6, 13, 0),
                poids_entree=350, poids_sortie=320, perte=30, rendement_pourcentage=91.4,
                operateur="Kouassi J.", fruits_murs_kg=320, dechets_tri_kg=15,
                dechets_lavage_kg=8, retour_non_mur_kg=4, dechets_production_kg=3),
            EtapeProduction(lot_id=lots[3].id, etape="production", ordre=2, statut="en_cours",
                date_debut=datetime(2026, 7, 7, 8, 0), date_fin=None,
                poids_entree=320, poids_sortie=0, perte=0, rendement_pourcentage=None,
                operateur="Kouassi J."),
            EtapeProduction(lot_id=lots[3].id, etape="conditionnement", ordre=3, statut="en_attente"),
            # Lot 5 : réception, étapes vides
            EtapeProduction(lot_id=lots[4].id, etape="musserie", ordre=1, statut="en_attente"),
            EtapeProduction(lot_id=lots[4].id, etape="production", ordre=2, statut="en_attente"),
            EtapeProduction(lot_id=lots[4].id, etape="conditionnement", ordre=3, statut="en_attente"),
        ]
        db.add_all(etapes)

        lot1 = lots[0]
        lot1.poids_sec_final = 435
        lot1.rendement_global = 87.0

        zones = [
            ZoneStockage(nom="Chambre Froide 1", type_zone="froid", usage="local",
                        temperature_consigne=4, capacite_kg=1000),
            ZoneStockage(nom="Chambre Froide 2", type_zone="froid", usage="export",
                        temperature_consigne=2, capacite_kg=500),
        ]
        db.add_all(zones); db.flush()

        stocks_zone = [
            StockZone(zone_id=zones[0].id, lot_id=lots[2].id, produit_id=produits[3].id,
                      quantite=180, date_entree=datetime(2026, 7, 2)),
            StockZone(zone_id=zones[1].id, lot_id=lots[1].id, produit_id=produits[1].id,
                      quantite=120, sachets=1200, date_entree=datetime(2026, 6, 22)),
        ]
        db.add_all(stocks_zone)

        now = datetime.now()
        mouvements = [
            MouvementStock(produit_id=produits[0].id, lot_id=lots[0].id, type_mouvement="entrée",
                quantite=500, quantite_avant=0, quantite_apres=500,
                motif="Réception fruits frais", responsable="Kouassi J.",
                date_mouvement=now - timedelta(days=38)),
            MouvementStock(produit_id=produits[3].id, lot_id=lots[2].id, type_mouvement="entrée",
                quantite=200, quantite_avant=0, quantite_apres=200,
                motif="Production lot séché", responsable="N'Guessan P.",
                date_mouvement=now - timedelta(days=22)),
            MouvementStock(produit_id=produits[3].id, lot_id=lots[2].id, type_mouvement="sortie",
                quantite=20, quantite_avant=200, quantite_apres=180,
                motif="Expédition client Abidjan", responsable="Diallo M.",
                date_mouvement=now - timedelta(days=5)),
            MouvementStock(produit_id=produits[0].id, lot_id=lots[0].id, type_mouvement="sortie",
                quantite=300, quantite_avant=500, quantite_apres=200,
                motif="Transfert vers musserie", responsable="Kouassi J.",
                date_mouvement=now - timedelta(days=30)),
        ]
        db.add_all(mouvements)
        db.commit()

        print("[OK] Données de démonstration insérées avec succès !")
        print(f"   {len(cats)} catégories, {len(produits)} produits, {len(fournisseurs)} fournisseurs")
        print(f"   {len(lots)} lots, {len(etapes)} étapes, {len(zones)} zones")
        print(f"   {len(stocks_zone)} stocks zone, {len(mouvements)} mouvements")

    finally:
        db.close()

if __name__ == "__main__":
    print("Seed 2Saisons - Insertion des données de démonstration")
    print("=" * 50)
    seed_database()
