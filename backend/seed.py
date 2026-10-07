"""Seed 2Saisons — régénéré depuis les saisies réelles de test.

- Valeurs exactes rejouées (lots, étapes, chariots, zones, stocks,
  transferts, reconditionnements, conditionnements dryer).
- Dates re-ancrées : le jour le plus récent devient aujourd'hui,
  écarts relatifs préservés (chaînes J+1 intactes).
"""
from database import SessionLocal, engine, Base
from models import (Categorie, Fournisseur, Produit, Lot, MouvementStock,
                    Commande, LigneCommande, EtapeProduction, Chariot,
                    ZoneStockage, StockZone, DemandeTransfert, DemandeTransfertLigne,
                    Reconditionnement, ConditionnementEntry)
from datetime import datetime, timedelta
from sqlalchemy import text
import statuses

# Décalage appliqué à toutes les dates : le jour le plus récent
# de la capture devient aujourd'hui (relatifs préservés).
OFFSET = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.fromisoformat("2026-10-06 00:00:00")


def _dt(s):
    """'YYYY-MM-DD HH:MM:SS' + décalage (max->aujourd'hui), ou None."""
    if not s:
        return None
    return datetime.fromisoformat(s) + OFFSET


def seed_database():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
    db = SessionLocal()
    try:
        if db.query(Lot).count() > 0:
            print("[INFO] Base déjà initialisée.")
            return

        # ── Catalogue (tel que saisi) ──
        db.add(Produit(id=1, nom='Export', categorie_id=None, unite_mesure='kg',
                       stock_min=0.0, stock_actuel=960.0, cartons=64.0,
                       prix_unitaire=0.0, description='', actif=True))
        db.add(Produit(id=2, nom='Local', categorie_id=None, unite_mesure='kg',
                       stock_min=0.0, stock_actuel=795.0, cartons=53.0,
                       prix_unitaire=0.0, description='', actif=True))
        db.add(Produit(id=3, nom='Fitini Fê', categorie_id=None, unite_mesure='kg',
                       stock_min=0.0, stock_actuel=435.0, cartons=29.0,
                       prix_unitaire=0.0, description='', actif=True))
        db.add(Produit(id=4, nom='Déchets', categorie_id=None, unite_mesure='kg',
                       stock_min=0.0, stock_actuel=135.0, cartons=9.0,
                       prix_unitaire=0.0, description='', actif=True))
        db.add(Produit(id=5, nom='Rhum arrangé', categorie_id=None, unite_mesure='kg',
                       stock_min=0.0, stock_actuel=128.0, cartons=8.0,
                       prix_unitaire=0.0, description='', actif=True))
        db.add(Produit(id=6, nom='Sachet 100g local', categorie_id=None, unite_mesure='sachet 100g',
                       stock_min=0.0, stock_actuel=1392.0, cartons=0.0,
                       prix_unitaire=0.0, description='', actif=True))
        db.flush()

        # ── Zones ──
        db.add(ZoneStockage(id=1, nom='Chambre Froide 1', type_zone='froid', usage=None,
                             temperature_consigne=None, capacite_kg=0.0, actif=True))
        db.add(ZoneStockage(id=2, nom='Chambre Froide 2', type_zone='froid', usage=None,
                             temperature_consigne=None, capacite_kg=0.0, actif=True))
        db.flush()

        # ── Lots (saisies réelles) ──
        db.add(Lot(id=1, code_lot='Lot 01', type_fruit='mangue kent',
                   fournisseur_nom='AG', produit_id=None, fournisseur_id=None,
                   statut='en_murisserie', quantite_initiale=0.0, quantite_restante=8483.6,
                   poids_frais=33637.700000000004, poids_sec_final=2595.0, rendement_global=7.7,
                   export_cartons=64, export_sachets=0, export_poids_sachet=2.5,
                   local_cartons=63, local_sachets=0, local_poids_sachet=2.5,
                   dechets_cartons=9, dechets_sachets=0, dechets_poids_sachet=2.5,
                   rhum_cartons=8, rhum_sachets=0, rhum_poids_sachet=2.5,
                   fitini_fe_cartons=29, fitini_fe_sachets=0, fitini_fe_poids_sachet=2.5,
                   statut_transfert='valide', ecart_bilan_pourcentage=78.9,
                   date_reception=_dt('2026-09-21 00:00:00'), date_fabrication=_dt(None),
                   date_peremption=_dt(None), notes=''))
        db.add(Lot(id=2, code_lot='Lot 2', type_fruit='mangue kent',
                   fournisseur_nom='AZ', produit_id=None, fournisseur_id=None,
                   statut='en_murisserie', quantite_initiale=0.0, quantite_restante=24728.73,
                   poids_frais=28647.73, poids_sec_final=0.0, rendement_global=None,
                   export_cartons=0, export_sachets=0, export_poids_sachet=2.5,
                   local_cartons=0, local_sachets=0, local_poids_sachet=2.5,
                   dechets_cartons=0, dechets_sachets=0, dechets_poids_sachet=2.5,
                   rhum_cartons=0, rhum_sachets=0, rhum_poids_sachet=2.5,
                   fitini_fe_cartons=0, fitini_fe_sachets=0, fitini_fe_poids_sachet=2.5,
                   statut_transfert='en_attente', ecart_bilan_pourcentage=None,
                   date_reception=_dt('2026-10-06 00:00:00'), date_fabrication=_dt(None),
                   date_peremption=_dt(None), notes=''))
        db.flush()

        # ── Étapes ──
        db.add(EtapeProduction(id=1, lot_id=1, etape='murisserie', ordre=1, statut='termine',
            date_debut=_dt('2026-09-21 11:31:19'), date_fin=_dt('2026-09-21 11:33:31'),
            poids_entree=0.0, poids_sortie=2562.3, poids_sec_kg=None,
            perte=1238.6, rendement_pourcentage=89.7, operateur='TED', notes='',
            fruits_murs_kg=2856.5, dechets_tri_kg=986.5, dechets_lavage_kg=86.5,
            retour_non_mur_kg=42.1, retour_mure_kg=0.0, dechets_production_kg=165.6,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=1, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=2, lot_id=1, etape='murisserie', ordre=1, statut='termine',
            date_debut=_dt('2026-09-21 11:32:11'), date_fin=_dt('2026-09-21 11:33:31'),
            poids_entree=0.0, poids_sortie=2208.1, poids_sec_kg=None,
            perte=119.9, rendement_pourcentage=86.7, operateur='TED', notes='',
            fruits_murs_kg=2546.5, dechets_tri_kg=0.0, dechets_lavage_kg=65.6,
            retour_non_mur_kg=43.2, retour_mure_kg=175.3, dechets_production_kg=54.3,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=2, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=3, lot_id=1, etape='production', ordre=2, statut='termine',
            date_debut=_dt('2026-09-21 11:31:19'), date_fin=_dt('2026-09-21 11:38:30'),
            poids_entree=2562.3, poids_sortie=1575.0, poids_sec_kg=None,
            perte=987.3, rendement_pourcentage=None, operateur='ted', notes='Dryer 1 (6 chariots)',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=165.6,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=1, nbre_chariots=6, total_claies=252))
        db.add(EtapeProduction(id=4, lot_id=1, etape='production', ordre=2, statut='termine',
            date_debut=_dt('2026-09-21 11:32:11'), date_fin=_dt('2026-09-21 11:38:30'),
            poids_entree=2208.1, poids_sortie=1500.0, poids_sec_kg=None,
            perte=708.1, rendement_pourcentage=None, operateur='ted', notes='Dryer 2 (12 chariots)',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=54.3,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=2, nbre_chariots=12, total_claies=240))
        db.add(EtapeProduction(id=5, lot_id=1, etape='conditionnement', ordre=3, statut='en_cours',
            date_debut=_dt('2026-09-22 09:50:07'), date_fin=_dt('2026-10-03 12:33:47'),
            poids_entree=12300.0, poids_sortie=2595.0, poids_sec_kg=None,
            perte=0.0, rendement_pourcentage=7.7, operateur='', notes='',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=0.0,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=None, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=6, lot_id=1, etape='murisserie', ordre=1, statut='termine',
            date_debut=_dt('2026-09-23 15:31:12'), date_fin=_dt('2026-09-23 15:31:49'),
            poids_entree=0.0, poids_sortie=2558.6, poids_sec_kg=None,
            perte=555.4, rendement_pourcentage=92.7, operateur='TED', notes='',
            fruits_murs_kg=2758.6, dechets_tri_kg=395.5, dechets_lavage_kg=74.5,
            retour_non_mur_kg=40.1, retour_mure_kg=0.0, dechets_production_kg=85.4,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=1, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=7, lot_id=1, etape='murisserie', ordre=1, statut='termine',
            date_debut=_dt('2026-09-23 15:31:23'), date_fin=_dt('2026-09-23 15:31:49'),
            poids_entree=0.0, poids_sortie=2141.7, poids_sec_kg=None,
            perte=181.8, rendement_pourcentage=80.9, operateur='TED', notes='',
            fruits_murs_kg=2648.4, dechets_tri_kg=0.0, dechets_lavage_kg=95.4,
            retour_non_mur_kg=62.3, retour_mure_kg=262.6, dechets_production_kg=86.4,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=2, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=8, lot_id=1, etape='production', ordre=2, statut='termine',
            date_debut=_dt('2026-09-23 15:31:12'), date_fin=_dt('2026-09-23 15:37:43'),
            poids_entree=2562.3, poids_sortie=1575.0, poids_sec_kg=None,
            perte=987.3, rendement_pourcentage=None, operateur='TED', notes='Dryer 1 (6 chariots)',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=165.6,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=1, nbre_chariots=6, total_claies=252))
        db.add(EtapeProduction(id=9, lot_id=1, etape='production', ordre=2, statut='termine',
            date_debut=_dt('2026-09-23 15:31:23'), date_fin=_dt('2026-09-23 15:37:43'),
            poids_entree=2208.1, poids_sortie=1500.0, poids_sec_kg=None,
            perte=708.1, rendement_pourcentage=None, operateur='TED', notes='Dryer 2 (12 chariots)',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=54.3,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=2, nbre_chariots=12, total_claies=240))
        db.add(EtapeProduction(id=10, lot_id=1, etape='murisserie', ordre=1, statut='termine',
            date_debut=_dt('2026-09-28 10:37:00'), date_fin=_dt('2026-09-28 10:37:09'),
            poids_entree=0.0, poids_sortie=2461.5, poids_sec_kg=None,
            perte=342.2, rendement_pourcentage=93.0, operateur='TED', notes='',
            fruits_murs_kg=2646.7, dechets_tri_kg=200.0, dechets_lavage_kg=56.8,
            retour_non_mur_kg=43.0, retour_mure_kg=0.0, dechets_production_kg=85.4,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=1, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=11, lot_id=1, etape='murisserie', ordre=1, statut='termine',
            date_debut=_dt('2026-09-28 10:37:05'), date_fin=_dt('2026-09-28 10:37:09'),
            poids_entree=0.0, poids_sortie=2197.9, poids_sec_kg=None,
            perte=199.0, rendement_pourcentage=85.4, operateur='TED', notes='',
            fruits_murs_kg=2574.7, dechets_tri_kg=0.0, dechets_lavage_kg=134.5,
            retour_non_mur_kg=24.4, retour_mure_kg=153.4, dechets_production_kg=64.5,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=2, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=12, lot_id=1, etape='production', ordre=2, statut='termine',
            date_debut=_dt('2026-09-28 10:37:00'), date_fin=_dt('2026-09-28 10:40:37'),
            poids_entree=2562.3, poids_sortie=1575.0, poids_sec_kg=None,
            perte=987.3, rendement_pourcentage=None, operateur='TED', notes='Dryer 1 (6 chariots)',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=165.6,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=1, nbre_chariots=6, total_claies=252))
        db.add(EtapeProduction(id=13, lot_id=1, etape='production', ordre=2, statut='termine',
            date_debut=_dt('2026-09-28 10:37:05'), date_fin=_dt('2026-09-28 10:40:37'),
            poids_entree=2197.9, poids_sortie=1500.0, poids_sec_kg=None,
            perte=697.9, rendement_pourcentage=None, operateur='TED', notes='Dryer 2 (12 chariots)',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=64.5,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=2, nbre_chariots=12, total_claies=240))
        db.add(EtapeProduction(id=14, lot_id=1, etape='murisserie', ordre=1, statut='termine',
            date_debut=_dt('2026-10-02 13:22:48'), date_fin=_dt('2026-10-02 13:23:00'),
            poids_entree=0.0, poids_sortie=2321.6, poids_sec_kg=None,
            perte=189.0, rendement_pourcentage=86.5, operateur='TED', notes='',
            fruits_murs_kg=2685.4, dechets_tri_kg=0.0, dechets_lavage_kg=96.5,
            retour_non_mur_kg=21.4, retour_mure_kg=153.4, dechets_production_kg=92.5,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=2, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=15, lot_id=1, etape='murisserie', ordre=1, statut='termine',
            date_debut=_dt('2026-10-02 13:22:55'), date_fin=_dt('2026-10-02 13:23:00'),
            poids_entree=0.0, poids_sortie=2582.4, poids_sec_kg=None,
            perte=333.1, rendement_pourcentage=92.8, operateur='TED', notes='',
            fruits_murs_kg=2783.4, dechets_tri_kg=153.3, dechets_lavage_kg=84.4,
            retour_non_mur_kg=21.2, retour_mure_kg=0.0, dechets_production_kg=95.4,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=1, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=16, lot_id=1, etape='production', ordre=2, statut='termine',
            date_debut=_dt('2026-10-02 13:22:48'), date_fin=_dt('2026-10-02 13:26:19'),
            poids_entree=2197.9, poids_sortie=1500.0, poids_sec_kg=None,
            perte=697.9, rendement_pourcentage=None, operateur='TED', notes='Dryer 2 (12 chariots)',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=64.5,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=2, nbre_chariots=12, total_claies=240))
        db.add(EtapeProduction(id=17, lot_id=1, etape='production', ordre=2, statut='termine',
            date_debut=_dt('2026-10-02 13:22:55'), date_fin=_dt('2026-10-02 13:26:19'),
            poids_entree=2562.3, poids_sortie=1575.0, poids_sec_kg=None,
            perte=987.3, rendement_pourcentage=None, operateur='TED', notes='Dryer 1 (6 chariots)',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=165.6,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=1, nbre_chariots=6, total_claies=252))
        db.add(EtapeProduction(id=18, lot_id=2, etape='murisserie', ordre=1, statut='termine',
            date_debut=_dt('2026-10-06 14:35:08'), date_fin=_dt('2026-10-06 14:36:41'),
            poids_entree=0.0, poids_sortie=2353.4, poids_sec_kg=None,
            perte=1522.3, rendement_pourcentage=89.0, operateur='TED', notes='',
            fruits_murs_kg=2645.6, dechets_tri_kg=1273.4, dechets_lavage_kg=95.5,
            retour_non_mur_kg=43.3, retour_mure_kg=0.0, dechets_production_kg=153.4,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=1, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=19, lot_id=1, etape='murisserie', ordre=1, statut='termine',
            date_debut=_dt('2026-10-06 14:36:18'), date_fin=_dt('2026-10-06 14:36:33'),
            poids_entree=0.0, poids_sortie=2194.4, poids_sec_kg=None,
            perte=425.3, rendement_pourcentage=85.6, operateur='TED', notes='',
            fruits_murs_kg=2564.4, dechets_tri_kg=245.4, dechets_lavage_kg=94.4,
            retour_non_mur_kg=43.6, retour_mure_kg=146.5, dechets_production_kg=85.5,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=2, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=20, lot_id=1, etape='production', ordre=2, statut='termine',
            date_debut=_dt('2026-10-06 14:36:18'), date_fin=_dt('2026-10-06 14:58:42'),
            poids_entree=2194.4, poids_sortie=0.0, poids_sec_kg=None,
            perte=0.0, rendement_pourcentage=None, operateur='TED', notes='',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=0.0,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=2, nbre_chariots=None, total_claies=None))
        db.add(EtapeProduction(id=21, lot_id=2, etape='production', ordre=2, statut='termine',
            date_debut=_dt('2026-10-06 14:35:08'), date_fin=_dt('2026-10-06 14:59:06'),
            poids_entree=2353.4, poids_sortie=1575.0, poids_sec_kg=None,
            perte=778.4, rendement_pourcentage=None, operateur='TED', notes='Dryer 1 (6 chariots)',
            fruits_murs_kg=0.0, dechets_tri_kg=0.0, dechets_lavage_kg=0.0,
            retour_non_mur_kg=0.0, retour_mure_kg=0.0, dechets_production_kg=153.4,
            quantite_acceptee_kg=0.0, quantite_transferee_kg=0.0,
            stock_restant_kg=0.0, stock_lendemain_kg=0.0,
            dryer=1, nbre_chariots=6, total_claies=252))
        db.flush()

        # ── Chariots ──
        db.add(Chariot(id=1, etape_production_id=3, lot_id=1,
            numero_chariot=1, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='ted',
            heure_remplissage='11:35', heure_entree_dryer='11:35',
            created_at=_dt('2026-09-21 11:36:31')))
        db.add(Chariot(id=2, etape_production_id=3, lot_id=1,
            numero_chariot=2, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='ted',
            heure_remplissage='11:35', heure_entree_dryer='11:35',
            created_at=_dt('2026-09-21 11:36:31')))
        db.add(Chariot(id=3, etape_production_id=3, lot_id=1,
            numero_chariot=3, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='ted',
            heure_remplissage='11:35', heure_entree_dryer='11:35',
            created_at=_dt('2026-09-21 11:36:31')))
        db.add(Chariot(id=4, etape_production_id=3, lot_id=1,
            numero_chariot=4, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='ted',
            heure_remplissage='11:35', heure_entree_dryer='11:35',
            created_at=_dt('2026-09-21 11:36:31')))
        db.add(Chariot(id=5, etape_production_id=3, lot_id=1,
            numero_chariot=5, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='ted',
            heure_remplissage='11:35', heure_entree_dryer='11:35',
            created_at=_dt('2026-09-21 11:36:31')))
        db.add(Chariot(id=6, etape_production_id=3, lot_id=1,
            numero_chariot=6, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='ted',
            heure_remplissage='11:35', heure_entree_dryer='11:36',
            created_at=_dt('2026-09-21 11:36:31')))
        db.add(Chariot(id=7, etape_production_id=4, lot_id=1,
            numero_chariot=1, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:36', heure_entree_dryer='11:36',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=8, etape_production_id=4, lot_id=1,
            numero_chariot=2, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:36', heure_entree_dryer='11:36',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=9, etape_production_id=4, lot_id=1,
            numero_chariot=3, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:36', heure_entree_dryer='11:36',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=10, etape_production_id=4, lot_id=1,
            numero_chariot=4, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:36', heure_entree_dryer='11:37',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=11, etape_production_id=4, lot_id=1,
            numero_chariot=5, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:37', heure_entree_dryer='11:37',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=12, etape_production_id=4, lot_id=1,
            numero_chariot=6, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:37', heure_entree_dryer='11:37',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=13, etape_production_id=4, lot_id=1,
            numero_chariot=7, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:37', heure_entree_dryer='11:37',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=14, etape_production_id=4, lot_id=1,
            numero_chariot=8, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:37', heure_entree_dryer='11:37',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=15, etape_production_id=4, lot_id=1,
            numero_chariot=9, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:37', heure_entree_dryer='11:37',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=16, etape_production_id=4, lot_id=1,
            numero_chariot=10, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:37', heure_entree_dryer='11:37',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=17, etape_production_id=4, lot_id=1,
            numero_chariot=11, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:37', heure_entree_dryer='11:37',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=18, etape_production_id=4, lot_id=1,
            numero_chariot=12, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='ted',
            heure_remplissage='11:37', heure_entree_dryer='11:37',
            created_at=_dt('2026-09-21 11:38:09')))
        db.add(Chariot(id=19, etape_production_id=8, lot_id=1,
            numero_chariot=1, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='15:34', heure_entree_dryer='15:34',
            created_at=_dt('2026-09-23 15:35:44')))
        db.add(Chariot(id=20, etape_production_id=8, lot_id=1,
            numero_chariot=2, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='15:34', heure_entree_dryer='15:34',
            created_at=_dt('2026-09-23 15:35:44')))
        db.add(Chariot(id=21, etape_production_id=8, lot_id=1,
            numero_chariot=3, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='15:34', heure_entree_dryer='15:34',
            created_at=_dt('2026-09-23 15:35:44')))
        db.add(Chariot(id=22, etape_production_id=8, lot_id=1,
            numero_chariot=4, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='15:34', heure_entree_dryer='15:34',
            created_at=_dt('2026-09-23 15:35:44')))
        db.add(Chariot(id=23, etape_production_id=8, lot_id=1,
            numero_chariot=5, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='15:34', heure_entree_dryer='15:34',
            created_at=_dt('2026-09-23 15:35:44')))
        db.add(Chariot(id=24, etape_production_id=8, lot_id=1,
            numero_chariot=6, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='15:35', heure_entree_dryer='15:35',
            created_at=_dt('2026-09-23 15:35:44')))
        db.add(Chariot(id=25, etape_production_id=9, lot_id=1,
            numero_chariot=1, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:35', heure_entree_dryer='15:35',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=26, etape_production_id=9, lot_id=1,
            numero_chariot=2, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:36', heure_entree_dryer='15:36',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=27, etape_production_id=9, lot_id=1,
            numero_chariot=3, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:36', heure_entree_dryer='15:36',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=28, etape_production_id=9, lot_id=1,
            numero_chariot=4, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:36', heure_entree_dryer='15:36',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=29, etape_production_id=9, lot_id=1,
            numero_chariot=5, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:36', heure_entree_dryer='15:36',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=30, etape_production_id=9, lot_id=1,
            numero_chariot=6, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:36', heure_entree_dryer='15:36',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=31, etape_production_id=9, lot_id=1,
            numero_chariot=7, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:36', heure_entree_dryer='15:36',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=32, etape_production_id=9, lot_id=1,
            numero_chariot=8, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:36', heure_entree_dryer='15:36',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=33, etape_production_id=9, lot_id=1,
            numero_chariot=9, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:36', heure_entree_dryer='15:36',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=34, etape_production_id=9, lot_id=1,
            numero_chariot=10, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:36', heure_entree_dryer='15:36',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=35, etape_production_id=9, lot_id=1,
            numero_chariot=11, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:36', heure_entree_dryer='15:36',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=36, etape_production_id=9, lot_id=1,
            numero_chariot=12, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='15:37', heure_entree_dryer='15:37',
            created_at=_dt('2026-09-23 15:37:33')))
        db.add(Chariot(id=37, etape_production_id=12, lot_id=1,
            numero_chariot=1, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='10:38', heure_entree_dryer='10:38',
            created_at=_dt('2026-09-28 10:39:04')))
        db.add(Chariot(id=38, etape_production_id=12, lot_id=1,
            numero_chariot=2, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='10:38', heure_entree_dryer='10:38',
            created_at=_dt('2026-09-28 10:39:04')))
        db.add(Chariot(id=39, etape_production_id=12, lot_id=1,
            numero_chariot=3, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='10:38', heure_entree_dryer='10:38',
            created_at=_dt('2026-09-28 10:39:04')))
        db.add(Chariot(id=40, etape_production_id=12, lot_id=1,
            numero_chariot=4, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='10:38', heure_entree_dryer='10:38',
            created_at=_dt('2026-09-28 10:39:04')))
        db.add(Chariot(id=41, etape_production_id=12, lot_id=1,
            numero_chariot=5, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='10:38', heure_entree_dryer='10:38',
            created_at=_dt('2026-09-28 10:39:04')))
        db.add(Chariot(id=42, etape_production_id=12, lot_id=1,
            numero_chariot=6, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='10:38', heure_entree_dryer='10:38',
            created_at=_dt('2026-09-28 10:39:04')))
        db.add(Chariot(id=43, etape_production_id=13, lot_id=1,
            numero_chariot=1, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:39', heure_entree_dryer='10:39',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=44, etape_production_id=13, lot_id=1,
            numero_chariot=2, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:39', heure_entree_dryer='10:39',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=45, etape_production_id=13, lot_id=1,
            numero_chariot=3, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:39', heure_entree_dryer='10:39',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=46, etape_production_id=13, lot_id=1,
            numero_chariot=4, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:39', heure_entree_dryer='10:39',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=47, etape_production_id=13, lot_id=1,
            numero_chariot=5, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:39', heure_entree_dryer='10:39',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=48, etape_production_id=13, lot_id=1,
            numero_chariot=6, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:39', heure_entree_dryer='10:39',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=49, etape_production_id=13, lot_id=1,
            numero_chariot=7, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:39', heure_entree_dryer='10:39',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=50, etape_production_id=13, lot_id=1,
            numero_chariot=8, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:39', heure_entree_dryer='10:39',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=51, etape_production_id=13, lot_id=1,
            numero_chariot=9, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:39', heure_entree_dryer='10:39',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=52, etape_production_id=13, lot_id=1,
            numero_chariot=10, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:40', heure_entree_dryer='10:40',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=53, etape_production_id=13, lot_id=1,
            numero_chariot=11, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:40', heure_entree_dryer='10:40',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=54, etape_production_id=13, lot_id=1,
            numero_chariot=12, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='10:40', heure_entree_dryer='10:40',
            created_at=_dt('2026-09-28 10:40:29')))
        db.add(Chariot(id=55, etape_production_id=16, lot_id=1,
            numero_chariot=1, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:23', heure_entree_dryer='13:23',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=56, etape_production_id=16, lot_id=1,
            numero_chariot=2, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:23', heure_entree_dryer='13:23',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=57, etape_production_id=16, lot_id=1,
            numero_chariot=3, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:23', heure_entree_dryer='13:24',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=58, etape_production_id=16, lot_id=1,
            numero_chariot=4, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:24', heure_entree_dryer='13:24',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=59, etape_production_id=16, lot_id=1,
            numero_chariot=5, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:24', heure_entree_dryer='13:24',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=60, etape_production_id=16, lot_id=1,
            numero_chariot=6, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:24', heure_entree_dryer='13:24',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=61, etape_production_id=16, lot_id=1,
            numero_chariot=7, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:24', heure_entree_dryer='13:24',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=62, etape_production_id=16, lot_id=1,
            numero_chariot=8, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:24', heure_entree_dryer='13:24',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=63, etape_production_id=16, lot_id=1,
            numero_chariot=9, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:24', heure_entree_dryer='13:24',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=64, etape_production_id=16, lot_id=1,
            numero_chariot=10, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:24', heure_entree_dryer='13:24',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=65, etape_production_id=16, lot_id=1,
            numero_chariot=11, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:24', heure_entree_dryer='13:24',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=66, etape_production_id=16, lot_id=1,
            numero_chariot=12, dryer=2, nbre_chariots=12,
            total_claies=240, quantite_totale=1500.0, operateur='TED',
            heure_remplissage='13:24', heure_entree_dryer='13:24',
            created_at=_dt('2026-10-02 13:25:04')))
        db.add(Chariot(id=67, etape_production_id=17, lot_id=1,
            numero_chariot=1, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='13:25', heure_entree_dryer='13:25',
            created_at=_dt('2026-10-02 13:25:52')))
        db.add(Chariot(id=68, etape_production_id=17, lot_id=1,
            numero_chariot=2, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='13:25', heure_entree_dryer='13:25',
            created_at=_dt('2026-10-02 13:25:52')))
        db.add(Chariot(id=69, etape_production_id=17, lot_id=1,
            numero_chariot=3, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='13:25', heure_entree_dryer='13:25',
            created_at=_dt('2026-10-02 13:25:52')))
        db.add(Chariot(id=70, etape_production_id=17, lot_id=1,
            numero_chariot=4, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='13:25', heure_entree_dryer='13:25',
            created_at=_dt('2026-10-02 13:25:52')))
        db.add(Chariot(id=71, etape_production_id=17, lot_id=1,
            numero_chariot=5, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='13:25', heure_entree_dryer='13:25',
            created_at=_dt('2026-10-02 13:25:52')))
        db.add(Chariot(id=72, etape_production_id=17, lot_id=1,
            numero_chariot=6, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='13:25', heure_entree_dryer='13:25',
            created_at=_dt('2026-10-02 13:25:52')))
        db.add(Chariot(id=73, etape_production_id=21, lot_id=2,
            numero_chariot=1, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='14:38', heure_entree_dryer='14:38',
            created_at=_dt('2026-10-06 14:39:23')))
        db.add(Chariot(id=74, etape_production_id=21, lot_id=2,
            numero_chariot=2, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='14:38', heure_entree_dryer='14:38',
            created_at=_dt('2026-10-06 14:39:23')))
        db.add(Chariot(id=75, etape_production_id=21, lot_id=2,
            numero_chariot=3, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='14:38', heure_entree_dryer='14:38',
            created_at=_dt('2026-10-06 14:39:23')))
        db.add(Chariot(id=76, etape_production_id=21, lot_id=2,
            numero_chariot=4, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='14:38', heure_entree_dryer='14:38',
            created_at=_dt('2026-10-06 14:39:23')))
        db.add(Chariot(id=77, etape_production_id=21, lot_id=2,
            numero_chariot=5, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='14:38', heure_entree_dryer='14:39',
            created_at=_dt('2026-10-06 14:39:23')))
        db.add(Chariot(id=78, etape_production_id=21, lot_id=2,
            numero_chariot=6, dryer=1, nbre_chariots=6,
            total_claies=252, quantite_totale=1575.0, operateur='TED',
            heure_remplissage='14:39', heure_entree_dryer='14:39',
            created_at=_dt('2026-10-06 14:39:23')))
        db.flush()

        # ── Stocks en zone ──
        db.add(StockZone(id=1, zone_id=1, lot_id=1, produit_id=1,
            quantite=270.0, sachets=108,
            date_entree=_dt('2026-09-22 09:50:39'), date_sortie=_dt(None)))
        db.add(StockZone(id=2, zone_id=1, lot_id=1, produit_id=2,
            quantite=150.0, sachets=60,
            date_entree=_dt('2026-09-22 09:50:39'), date_sortie=_dt(None)))
        db.add(StockZone(id=3, zone_id=1, lot_id=1, produit_id=3,
            quantite=135.0, sachets=54,
            date_entree=_dt('2026-09-22 09:50:39'), date_sortie=_dt(None)))
        db.add(StockZone(id=4, zone_id=2, lot_id=1, produit_id=4,
            quantite=60.0, sachets=24,
            date_entree=_dt('2026-09-22 09:50:39'), date_sortie=_dt(None)))
        db.add(StockZone(id=5, zone_id=2, lot_id=1, produit_id=5,
            quantite=30.0, sachets=12,
            date_entree=_dt('2026-09-22 09:50:39'), date_sortie=_dt(None)))
        db.add(StockZone(id=6, zone_id=1, lot_id=1, produit_id=6,
            quantite=139.2, sachets=1392,
            date_entree=_dt('2026-09-22 09:53:49'), date_sortie=_dt(None)))
        db.add(StockZone(id=7, zone_id=1, lot_id=1, produit_id=5,
            quantite=6.6, sachets=2,
            date_entree=_dt('2026-09-22 09:53:49'), date_sortie=_dt(None)))
        db.add(StockZone(id=8, zone_id=1, lot_id=1, produit_id=5,
            quantite=1.4, sachets=0,
            date_entree=_dt('2026-09-22 11:36:25'), date_sortie=_dt(None)))
        db.add(StockZone(id=9, zone_id=1, lot_id=1, produit_id=2,
            quantite=150.0, sachets=60,
            date_entree=_dt('2026-09-29 08:27:58'), date_sortie=_dt(None)))
        db.add(StockZone(id=10, zone_id=1, lot_id=1, produit_id=3,
            quantite=120.0, sachets=48,
            date_entree=_dt('2026-09-29 08:27:58'), date_sortie=_dt(None)))
        db.add(StockZone(id=11, zone_id=1, lot_id=1, produit_id=1,
            quantite=180.0, sachets=72,
            date_entree=_dt('2026-09-29 08:27:58'), date_sortie=_dt(None)))
        db.add(StockZone(id=12, zone_id=1, lot_id=1, produit_id=4,
            quantite=15.0, sachets=6,
            date_entree=_dt('2026-09-29 08:27:58'), date_sortie=_dt(None)))
        db.add(StockZone(id=13, zone_id=1, lot_id=1, produit_id=5,
            quantite=30.0, sachets=12,
            date_entree=_dt('2026-09-29 08:27:58'), date_sortie=_dt(None)))
        db.add(StockZone(id=14, zone_id=1, lot_id=1, produit_id=2,
            quantite=135.0, sachets=54,
            date_entree=_dt('2026-09-29 08:28:41'), date_sortie=_dt(None)))
        db.add(StockZone(id=15, zone_id=1, lot_id=1, produit_id=3,
            quantite=75.0, sachets=30,
            date_entree=_dt('2026-09-29 08:28:41'), date_sortie=_dt(None)))
        db.add(StockZone(id=16, zone_id=1, lot_id=1, produit_id=1,
            quantite=195.0, sachets=78,
            date_entree=_dt('2026-09-29 08:28:41'), date_sortie=_dt(None)))
        db.add(StockZone(id=17, zone_id=1, lot_id=1, produit_id=4,
            quantite=15.0, sachets=6,
            date_entree=_dt('2026-09-29 08:28:41'), date_sortie=_dt(None)))
        db.add(StockZone(id=18, zone_id=1, lot_id=1, produit_id=5,
            quantite=30.0, sachets=12,
            date_entree=_dt('2026-09-29 08:28:41'), date_sortie=_dt(None)))
        db.add(StockZone(id=19, zone_id=1, lot_id=1, produit_id=2,
            quantite=195.0, sachets=78,
            date_entree=_dt('2026-10-03 12:32:27'), date_sortie=_dt(None)))
        db.add(StockZone(id=20, zone_id=1, lot_id=1, produit_id=3,
            quantite=60.0, sachets=24,
            date_entree=_dt('2026-10-03 12:32:27'), date_sortie=_dt(None)))
        db.add(StockZone(id=21, zone_id=1, lot_id=1, produit_id=1,
            quantite=165.0, sachets=66,
            date_entree=_dt('2026-10-03 12:32:27'), date_sortie=_dt(None)))
        db.add(StockZone(id=22, zone_id=1, lot_id=1, produit_id=4,
            quantite=30.0, sachets=12,
            date_entree=_dt('2026-10-03 12:32:27'), date_sortie=_dt(None)))
        db.add(StockZone(id=23, zone_id=1, lot_id=1, produit_id=5,
            quantite=15.0, sachets=6,
            date_entree=_dt('2026-10-03 12:32:27'), date_sortie=_dt(None)))
        db.add(StockZone(id=24, zone_id=1, lot_id=1, produit_id=2,
            quantite=165.0, sachets=66,
            date_entree=_dt('2026-10-03 12:33:01'), date_sortie=_dt(None)))
        db.add(StockZone(id=25, zone_id=1, lot_id=1, produit_id=3,
            quantite=45.0, sachets=18,
            date_entree=_dt('2026-10-03 12:33:01'), date_sortie=_dt(None)))
        db.add(StockZone(id=26, zone_id=1, lot_id=1, produit_id=1,
            quantite=150.0, sachets=60,
            date_entree=_dt('2026-10-03 12:33:01'), date_sortie=_dt(None)))
        db.add(StockZone(id=27, zone_id=1, lot_id=1, produit_id=4,
            quantite=15.0, sachets=6,
            date_entree=_dt('2026-10-03 12:33:01'), date_sortie=_dt(None)))
        db.add(StockZone(id=28, zone_id=1, lot_id=1, produit_id=5,
            quantite=15.0, sachets=6,
            date_entree=_dt('2026-10-03 12:33:01'), date_sortie=_dt(None)))
        db.flush()

        # ── Transferts ──
        db.add(DemandeTransfert(id=1, lot_id=1, date_demande=_dt('2026-09-22 09:50:39'),
            responsable='TED', statut='validee', notes=''))
        db.add(DemandeTransfert(id=2, lot_id=1, date_demande=_dt('2026-09-29 08:27:58'),
            responsable='auto-journalier', statut='validee', notes='Auto conditionnement 2026-09-29'))
        db.add(DemandeTransfert(id=3, lot_id=1, date_demande=_dt('2026-09-29 08:28:41'),
            responsable='auto-journalier', statut='validee', notes='Auto conditionnement 2026-09-29'))
        db.add(DemandeTransfert(id=4, lot_id=1, date_demande=_dt('2026-10-03 12:32:27'),
            responsable='auto-journalier', statut='validee', notes='Auto conditionnement 2026-10-03'))
        db.add(DemandeTransfert(id=5, lot_id=1, date_demande=_dt('2026-10-03 12:33:01'),
            responsable='auto-journalier', statut='validee', notes='Auto conditionnement 2026-10-03'))
        db.flush()
        db.add(DemandeTransfertLigne(id=1, demande_id=1, type_flux='export',
            nb_cartons=18, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=2, demande_id=1, type_flux='local',
            nb_cartons=20, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=3, demande_id=1, type_flux='fitini_fe',
            nb_cartons=9, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=4, demande_id=1, type_flux='dechets',
            nb_cartons=4, zone_id=2, statut='validee'))
        db.add(DemandeTransfertLigne(id=5, demande_id=1, type_flux='rhum',
            nb_cartons=2, zone_id=2, statut='validee'))
        db.add(DemandeTransfertLigne(id=6, demande_id=2, type_flux='local',
            nb_cartons=10, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=7, demande_id=2, type_flux='fitini_fe',
            nb_cartons=8, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=8, demande_id=2, type_flux='export',
            nb_cartons=12, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=9, demande_id=2, type_flux='dechets',
            nb_cartons=1, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=10, demande_id=2, type_flux='rhum',
            nb_cartons=2, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=11, demande_id=3, type_flux='local',
            nb_cartons=9, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=12, demande_id=3, type_flux='fitini_fe',
            nb_cartons=5, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=13, demande_id=3, type_flux='export',
            nb_cartons=13, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=14, demande_id=3, type_flux='dechets',
            nb_cartons=1, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=15, demande_id=3, type_flux='rhum',
            nb_cartons=2, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=16, demande_id=4, type_flux='local',
            nb_cartons=13, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=17, demande_id=4, type_flux='fitini_fe',
            nb_cartons=4, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=18, demande_id=4, type_flux='export',
            nb_cartons=11, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=19, demande_id=4, type_flux='dechets',
            nb_cartons=2, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=20, demande_id=4, type_flux='rhum',
            nb_cartons=1, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=21, demande_id=5, type_flux='local',
            nb_cartons=11, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=22, demande_id=5, type_flux='fitini_fe',
            nb_cartons=3, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=23, demande_id=5, type_flux='export',
            nb_cartons=10, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=24, demande_id=5, type_flux='dechets',
            nb_cartons=1, zone_id=1, statut='validee'))
        db.add(DemandeTransfertLigne(id=25, demande_id=5, type_flux='rhum',
            nb_cartons=1, zone_id=1, statut='validee'))
        db.flush()

        # ── Reconditionnements ──
        db.add(Reconditionnement(id=1, lot_id=1, date_reconditionnement=_dt('2026-09-22 09:53:49'),
            type_source='local', nb_cartons_entree=4,
            nb_sachets_100g_sortie=600, dechet_kg=0.0, nb_sachets_sortis=510,
            rhum_cartons_sortie=0, rhum_sachets_sortis=2,
            rhum_poids_sachet=2.5, rhum_poids_vrac_kg=1.6,
            responsable='TED', notes='', statut='termine'))
        db.add(Reconditionnement(id=2, lot_id=1, date_reconditionnement=_dt('2026-09-22 11:36:25'),
            type_source='local', nb_cartons_entree=4,
            nb_sachets_100g_sortie=600, dechet_kg=0.0, nb_sachets_sortis=590,
            rhum_cartons_sortie=0, rhum_sachets_sortis=0,
            rhum_poids_sachet=2.5, rhum_poids_vrac_kg=1.4,
            responsable='TED', notes='', statut='termine'))
        db.add(Reconditionnement(id=3, lot_id=1, date_reconditionnement=_dt('2026-09-22 11:38:26'),
            type_source='local', nb_cartons_entree=2,
            nb_sachets_100g_sortie=300, dechet_kg=0.0, nb_sachets_sortis=292,
            rhum_cartons_sortie=0, rhum_sachets_sortis=0,
            rhum_poids_sachet=2.5, rhum_poids_vrac_kg=0.0,
            responsable='TTED', notes='', statut='termine'))
        db.flush()

        # ── Conditionnements dryer ──
        db.add(ConditionnementEntry(id=1, lot_id=1, date=_dt('2026-09-22 09:48:21'), dryer=1,
            export_cartons=10, export_sachets=0, export_poids_sachet=2.5,
            local_cartons=8, local_sachets=0, local_poids_sachet=2.5,
            dechets_cartons=2, dechets_sachets=0, dechets_poids_sachet=2.5,
            rhum_cartons=1, rhum_sachets=0, rhum_poids_sachet=2.5,
            fitini_fe_cartons=5, fitini_fe_sachets=0, fitini_fe_poids_sachet=2.5,
            responsable='TED', notes=''))
        db.add(ConditionnementEntry(id=2, lot_id=1, date=_dt('2026-09-22 09:49:02'), dryer=2,
            export_cartons=8, export_sachets=0, export_poids_sachet=2.5,
            local_cartons=12, local_sachets=0, local_poids_sachet=2.5,
            dechets_cartons=2, dechets_sachets=0, dechets_poids_sachet=2.5,
            rhum_cartons=1, rhum_sachets=0, rhum_poids_sachet=2.5,
            fitini_fe_cartons=4, fitini_fe_sachets=0, fitini_fe_poids_sachet=2.5,
            responsable='TED', notes=''))
        db.add(ConditionnementEntry(id=3, lot_id=1, date=_dt('2026-09-29 08:27:58'), dryer=1,
            export_cartons=12, export_sachets=0, export_poids_sachet=2.5,
            local_cartons=10, local_sachets=0, local_poids_sachet=2.5,
            dechets_cartons=1, dechets_sachets=0, dechets_poids_sachet=2.5,
            rhum_cartons=2, rhum_sachets=0, rhum_poids_sachet=2.5,
            fitini_fe_cartons=8, fitini_fe_sachets=0, fitini_fe_poids_sachet=2.5,
            responsable='TED', notes=''))
        db.add(ConditionnementEntry(id=4, lot_id=1, date=_dt('2026-09-29 08:28:41'), dryer=2,
            export_cartons=13, export_sachets=0, export_poids_sachet=2.5,
            local_cartons=9, local_sachets=0, local_poids_sachet=2.5,
            dechets_cartons=1, dechets_sachets=0, dechets_poids_sachet=2.5,
            rhum_cartons=2, rhum_sachets=0, rhum_poids_sachet=2.5,
            fitini_fe_cartons=5, fitini_fe_sachets=0, fitini_fe_poids_sachet=2.5,
            responsable='TED', notes=''))
        db.add(ConditionnementEntry(id=5, lot_id=1, date=_dt('2026-10-03 12:32:27'), dryer=1,
            export_cartons=11, export_sachets=0, export_poids_sachet=2.5,
            local_cartons=13, local_sachets=0, local_poids_sachet=2.5,
            dechets_cartons=2, dechets_sachets=0, dechets_poids_sachet=2.5,
            rhum_cartons=1, rhum_sachets=0, rhum_poids_sachet=2.5,
            fitini_fe_cartons=4, fitini_fe_sachets=0, fitini_fe_poids_sachet=2.5,
            responsable='TED', notes=''))
        db.add(ConditionnementEntry(id=6, lot_id=1, date=_dt('2026-10-03 12:33:01'), dryer=2,
            export_cartons=10, export_sachets=0, export_poids_sachet=2.5,
            local_cartons=11, local_sachets=0, local_poids_sachet=2.5,
            dechets_cartons=1, dechets_sachets=0, dechets_poids_sachet=2.5,
            rhum_cartons=1, rhum_sachets=0, rhum_poids_sachet=2.5,
            fitini_fe_cartons=3, fitini_fe_sachets=0, fitini_fe_poids_sachet=2.5,
            responsable='TED', notes=''))
        db.flush()

        # Séquences postgres (ids explicites ci-dessus).
        if engine.dialect.name == "postgresql":
            for _t in ["produits", "lots", "etapes_production", "chariots", "zones_stockage",
                       "stocks_zone", "demandes_transfert", "lignes_demande_transfert",
                       "reconditionnements", "conditionnement_entries"]:
                with engine.begin() as _c:
                    _c.execute(text(f"SELECT setval(pg_get_serial_sequence('{_t}', 'id'), (SELECT MAX(id) FROM {_t}))"))
        db.commit()
        print("[OK] Seed depuis saisies reelles : 2 lots, 21 etapes.")
    finally:
        db.close()


if __name__ == "__main__":
    print("Seed 2Saisons - depuis saisies reelles")
    print("=" * 50)
    seed_database()
