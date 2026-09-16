"""Test bout-en-bout du workflow complet 2Saisons (CRUD direct, sans HTTP).

Chaine testee :
  reception -> musserie (2 jours) -> production chariots -> conditionnement
  -> transfert CF -> reconditionnement sachets 100g (+ stats, rappels, anomalies)

Usage :
  cd C:\\2saison\\backend; python scripts/test_workflow_full.py

Le lot de test (LOT-TEST-WF-*) est supprime en fin de run (reussite ou echec).
"""
import sys
import os
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import SessionLocal
import crud
import models
import schemas
import statuses

CODE = f"LOT-TEST-WF-{int(time.time()) % 100000}"
results = []


def step(name, fn):
    try:
        detail = fn()
        results.append((name, True, detail))
        print(f"[OK] {name} — {detail}")
    except Exception as e:
        results.append((name, False, f"{type(e).__name__}: {e}"))
        print(f"[FAIL] {name} — {type(e).__name__}: {e}")
        traceback.print_exc()


def main():
    db = SessionLocal()
    lot_id = None
    try:
        # 0. Zones (requises pour le transfert)
        def _zones():
            zs = crud.get_zones_stockage(db, actif=True)
            if len(zs) < 1:
                crud.create_zone_stockage(db, nom="CF-TEST-1", type_zone="froid", capacite_kg=0, actif=True)
                crud.create_zone_stockage(db, nom="CF-TEST-2", type_zone="froid", capacite_kg=0, actif=True)
                zs = crud.get_zones_stockage(db, actif=True)
            assert len(zs) >= 1, "aucune zone"
            return f"{len(zs)} zone(s), defaut id={zs[0].id}"
        step("0. zones stockage", _zones)
        zone_id = crud.get_zones_stockage(db, actif=True)[0].id

        # 1. Reception
        def _reception():
            nonlocal lot_id
            lot = crud.create_lot(
                db, code_lot=CODE, type_fruit="mangue kent",
                fournisseur_nom="TEST-WF", poids_frais=3000.0, notes="lot test workflow",
            )
            lot_id = lot.id
            assert lot.statut == statuses.RECEPTION, f"statut={lot.statut}"
            assert lot.quantite_restante == 3000.0, f"reste={lot.quantite_restante}"
            return f"{lot.code_lot} id={lot.id} reste={lot.quantite_restante}"
        step("1. reception (lot cree)", _reception)

        # 2. Musserie jour 1 (D1 partiel) — tri retiré du lot, pas de l'envoi, 2 décimales, MAJ par dryer/jour
        def _musserie_j1():
            ep = crud.valider_musserie(
                db, lot_id, fruits_murs_kg=2000.0, dechets_tri_kg=50.0,
                dechets_lavage_kg=20.0, retour_non_mur_kg=30.0,
                dechets_production_kg=15.0, operateur="test", dryer=1,
            )
            lot = crud.get_lot(db, lot_id)
            assert lot.statut == statuses.EN_MUSSERIE, f"statut={lot.statut}"
            assert lot.quantite_restante == 950.0, f"reste={lot.quantite_restante} (attendu 3000-2000-50 tri)"
            assert ep.poids_sortie == round(2000 - 30 - 20 - 15, 2), f"sortie={ep.poids_sortie} (tri non déduit)"
            assert f"{ep.poids_sortie:.2f}" == "1935.00", "format 2 décimales"
            return f"sortie={ep.poids_sortie:.2f} reste={lot.quantite_restante:.2f}"
        step("2. musserie J1 D1", _musserie_j1)

        # 2b. MAJ même dryer même jour — une seule validation par dryer/jour (écrasement, pas cumul)
        def _musserie_j1_maj():
            ep_before = db.query(models.EtapeProduction).filter(models.EtapeProduction.lot_id==lot_id, models.EtapeProduction.etape=="musserie", models.EtapeProduction.dryer==1, models.EtapeProduction.statut!=statuses.TERMINE).first()
            id_before = ep_before.id if ep_before else None
            ep = crud.valider_musserie(
                db, lot_id, fruits_murs_kg=2100.0, dechets_tri_kg=60.0,
                dechets_lavage_kg=20.0, retour_non_mur_kg=30.0,
                dechets_production_kg=15.0, operateur="test", dryer=1,
            )
            lot = crud.get_lot(db, lot_id)
            # MAJ : même id, pas de cumul
            assert ep.id == id_before, f"MAJ doit garder même id {id_before} vs {ep.id}"
            assert lot.quantite_restante == 840.0, f"reste={lot.quantite_restante} (3000-2100-60)"
            assert ep.poids_sortie == round(2100 - 30 - 20 - 15, 2), f"sortie={ep.poids_sortie}"
            # remettre les valeurs initiales pour la suite du workflow (2100->2000)
            ep2 = crud.valider_musserie(
                db, lot_id, fruits_murs_kg=2000.0, dechets_tri_kg=50.0,
                dechets_lavage_kg=20.0, retour_non_mur_kg=30.0,
                dechets_production_kg=15.0, operateur="test", dryer=1,
            )
            assert ep2.id == id_before, "retour aux valeurs initiales doit garder même id"
            assert db.get(models.Lot, lot_id).quantite_restante == 950.0
            return f"MAJ OK id={ep.id} sortie={ep.poids_sortie:.2f} reste={lot.quantite_restante:.2f}"
        step("2b. MAJ musserie J1 D1 (même dryer/jour)", _musserie_j1_maj)

        # 3. Cloture jour (reste > 0 -> reste en_musserie)
        def _cloture_jour():
            from datetime import date
            res = crud.cloturer_musserie(db, lot_id, date.today().isoformat())
            lot = crud.get_lot(db, lot_id)
            assert lot.statut == statuses.EN_MUSSERIE, f"statut={lot.statut}"
            assert res["action"] == "jour", f"action={res['action']}"
            return f"action=jour statut={lot.statut}"
        step("3. cloture musserie jour", _cloture_jour)

        # 4. Musserie jour 2 (solde) + cloture finale -> en_production
        def _musserie_j2():
            crud.valider_musserie(
                db, lot_id, fruits_murs_kg=1000.0, dechets_tri_kg=20.0,
                dechets_lavage_kg=10.0, retour_non_mur_kg=10.0,
                dechets_production_kg=5.0, operateur="test", dryer=1,
                reste_kg=0,
            )
            res = crud.cloturer_musserie(db, lot_id)
            lot = crud.get_lot(db, lot_id)
            assert lot.statut == statuses.EN_PRODUCTION, f"statut={lot.statut}"
            assert res["action"] == "tout", f"action={res['action']}"
            return f"statut={lot.statut}"
        step("4. musserie J2 + cloture finale", _musserie_j2)

        # 5. Production chariots D1 (<= musserie sortie * 1.05)
        def _production():
            chariots = [
                {"numero_chariot": 1, "heure_remplissage": "08:00", "heure_entree_sechoir": "09:00"},
                {"numero_chariot": 2, "heure_remplissage": "08:30", "heure_entree_sechoir": "09:30"},
            ]
            res = crud.valider_production(
                db, lot_id, dryer=1, nbre_chariots=2, quantite_totale=900.0,
                operateur="test", chariots=chariots,
            )
            ep = res["etape"]
            assert ep.statut == statuses.EN_COURS, f"statut={ep.statut}"
            assert ep.poids_sortie == 900.0 - 15.0, f"sortie={ep.poids_sortie}"
            return f"etape={ep.id} entree={ep.poids_entree} sortie={ep.poids_sortie}"
        step("5. production D1 chariots", _production)

        # 6. Cloture production -> en_conditionnement
        def _cloture_prod():
            crud.cloturer_production(db, lot_id)
            lot = crud.get_lot(db, lot_id)
            assert lot.statut == statuses.EN_CONDITIONNEMENT, f"statut={lot.statut}"
            return f"statut={lot.statut}"
        step("6. cloture production", _cloture_prod)

        # 7. Conditionnement (global)
        def _conditionnement():
            # flux continu : on conditionne toute la référence (885 kg) pour pouvoir clôturer
            res = crud.valider_conditionnement(
                db, lot_id, export_cartons=50, local_cartons=9, responsable="test",
            )
            assert res["total_flux"] == round((50 * 6) * 2.5 + (9 * 6) * 2.5, 2), f"flux={res['total_flux']}"
            assert res["reference"] > 0, "reference manquante"
            return f"flux={res['total_flux']} ref={res['reference']}"
        step("7. conditionnement saisie", _conditionnement)

        # 8. Cloture conditionnement -> conditionne
        def _cloture_cond():
            res = crud.cloturer_conditionnement(db, lot_id)
            lot = crud.get_lot(db, lot_id)
            assert lot.statut == statuses.CONDITIONNE, f"statut={lot.statut}"
            assert lot.poids_sec_final == 885.0, f"sec={lot.poids_sec_final}"
            return f"sec={lot.poids_sec_final} rendement={lot.rendement_global}"
        step("8. cloture conditionnement", _cloture_cond)

        # 9. Transfert chambre froide -> en_stock
        def _transfert():
            lignes = [
                schemas.DemandeTransfertLigneCreate(type_flux="local", nb_cartons=2, zone_id=zone_id),
                schemas.DemandeTransfertLigneCreate(type_flux="export", nb_cartons=1, zone_id=zone_id),
            ]
            dem = crud.creer_demande_transfert(db, lot_id, lignes, responsable="test")
            crud.valider_demande_transfert(db, dem.id)
            lot = crud.get_lot(db, lot_id)
            assert lot.statut == statuses.EN_STOCK, f"statut={lot.statut}"
            return f"demande={dem.id} statut={lot.statut}"
        step("9. transfert CF", _transfert)

        # 10. Reconditionnement sachets 100g
        def _recond():
            res = crud.creer_reconditionnement(
                db, lot_id, type_source="local", nb_cartons_entree=1,
                dechet_kg=0.1, nb_sachets_sortis=150, responsable="test",
            )
            assert res["nb_sachets_100g_sortie"] > 0, "0 sachet"
            p = db.query(models.Produit).filter(models.Produit.nom == "Sachet 100g local").first()
            assert p is not None and (p.stock_actuel or 0) > 0, "produit non alimente"
            return f"sachets={res['nb_sachets_100g_sortie']} stock={p.stock_actuel}"
        step("10. reconditionnement 100g", _recond)

        # 11. Stats / rappels / anomalies (ne doivent pas crasher)
        def _stats():
            s = crud.get_production_stats(db)
            r = crud.get_rappels(db)
            a = crud.detecter_anomalies(db)
            assert isinstance(s, dict) and isinstance(r, list) and isinstance(a, list)
            return f"stats dryers={s.get('total_dryers')} rappels={len(r)} anomalies={len(a)}"
        step("11. stats/rappels/anomalies", _stats)

    finally:
        # Nettoyage du lot de test (meme en echec)
        try:
            if lot_id:
                db.query(models.Chariot).filter(models.Chariot.lot_id == lot_id).delete()
                db.query(models.EtapeProduction).filter(models.EtapeProduction.lot_id == lot_id).delete()
                db.query(models.ConditionnementEntry).filter(models.ConditionnementEntry.lot_id == lot_id).delete()
                db.query(models.StockZone).filter(models.StockZone.lot_id == lot_id).delete()
                dem_ids = [d.id for d in db.query(models.DemandeTransfert).filter(models.DemandeTransfert.lot_id == lot_id).all()]
                if dem_ids:
                    db.query(models.DemandeTransfertLigne).filter(models.DemandeTransfertLigne.demande_id.in_(dem_ids)).delete()
                    db.query(models.DemandeTransfert).filter(models.DemandeTransfert.id.in_(dem_ids)).delete()
                db.query(models.Reconditionnement).filter(models.Reconditionnement.lot_id == lot_id).delete()
                db.query(models.MouvementStock).filter(models.MouvementStock.lot_id == lot_id).delete()
                db.query(models.Lot).filter(models.Lot.id == lot_id).delete()
                db.commit()
                # recalcule Cartons (stock_min) des produits flux depuis les demandes restantes
                from collections import defaultdict
                tot = defaultdict(int)
                for l in db.query(models.DemandeTransfertLigne).join(
                    models.DemandeTransfert,
                    models.DemandeTransfertLigne.demande_id == models.DemandeTransfert.id,
                ).filter(models.DemandeTransfert.statut == "validee").all():
                    tot[l.type_flux] += l.nb_cartons
                labels = {"local": "Local", "export": "Export", "fitini_fe": "Fitini Fê",
                          "dechets": "Déchets", "rhum": "Rhum arrangé"}
                for flux, nom in labels.items():
                    p = db.query(models.Produit).filter(models.Produit.nom == nom).first()
                    if p:
                        p.stock_min = float(tot.get(flux, 0))
                # supprime les produits "Sachet 100g" orphelins crees par le test
                for p in db.query(models.Produit).filter(models.Produit.nom.like("Sachet 100g%")).all():
                    refs = db.query(models.StockZone).filter(models.StockZone.produit_id == p.id).count()
                    if refs == 0:
                        db.delete(p)
                db.commit()
                print(f"[CLEAN] lot test {CODE} supprime")
        except Exception as e:
            print(f"[CLEAN-FAIL] {e}")
        finally:
            db.close()

    failed = [r for r in results if not r[1]]
    print(f"\n=== {len(results) - len(failed)}/{len(results)} etapes OK ===")
    if failed:
        print("Echecs :", [r[0] for r in failed])
        sys.exit(1)
    print("Workflow complet OK")


if __name__ == "__main__":
    main()
