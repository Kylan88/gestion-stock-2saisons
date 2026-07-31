from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from datetime import datetime
from typing import Optional, List

import models
from models import (
    Produit, Categorie, Fournisseur, Lot, MouvementStock,
    Commande, LigneCommande, EtapeProduction, Chariot,
    ZoneStockage, StockZone, DemandeTransfert, DemandeTransfertLigne,
    Reconditionnement
)

# ── PRODUITS ──

def get_produits(db: Session, actif: bool = True, skip: int = 0, limit: int = 100,
                 recherche: Optional[str] = None, categorie_id: Optional[int] = None) -> List[Produit]:
    q = db.query(Produit).options(joinedload(Produit.categorie))
    if actif:
        q = q.filter(Produit.actif == True)
    if recherche:
        q = q.filter(Produit.nom.ilike(f"%{recherche}%"))
    if categorie_id is not None:
        q = q.filter(Produit.categorie_id == categorie_id)
    return q.order_by(Produit.nom).offset(skip).limit(limit).all()

def get_produit(db: Session, produit_id: int) -> Optional[Produit]:
    return db.query(Produit).options(joinedload(Produit.categorie)).filter(Produit.id == produit_id).first()

def create_produit(db: Session, **data) -> Produit:
    p = Produit(**data)
    db.add(p); db.commit(); db.refresh(p)
    return p

def update_produit(db: Session, produit_id: int, **data) -> Optional[Produit]:
    p = get_produit(db, produit_id)
    if not p: return None
    for k, v in data.items():
        if v is not None and hasattr(p, k):
            setattr(p, k, v)
    db.commit(); db.refresh(p)
    return p

def delete_produit(db: Session, produit_id: int) -> bool:
    p = db.get(Produit, produit_id)
    if not p: return False
    p.actif = False
    db.commit()
    return True

def count_produits(db: Session, actif: bool = True) -> int:
    q = db.query(func.count(Produit.id))
    if actif: q = q.filter(Produit.actif == True)
    return q.scalar()

# ── MOUVEMENTS DE STOCK ──

def entree_stock(db: Session, produit_id: int, quantite: float, lot_id: Optional[int] = None,
                 motif: str = "", reference_doc: str = "", responsable: str = "") -> MouvementStock:
    p = db.get(Produit, produit_id)
    if not p:
        raise ValueError(f"Produit {produit_id} introuvable")
    qte_avant = p.stock_actuel
    p.stock_actuel += quantite
    mvt = MouvementStock(
        produit_id=produit_id, lot_id=lot_id,
        type_mouvement="entrée", quantite=quantite,
        quantite_avant=qte_avant, quantite_apres=p.stock_actuel,
        motif=motif, reference_doc=reference_doc,
        responsable=responsable, date_saisie=datetime.now()
    )
    db.add(mvt)
    if lot_id:
        lot = db.get(Lot, lot_id)
        if lot: lot.quantite_restante += quantite
    db.commit(); db.refresh(mvt)
    return mvt

def sortie_stock(db: Session, produit_id: int, quantite: float, lot_id: Optional[int] = None,
                 motif: str = "", reference_doc: str = "", responsable: str = "") -> MouvementStock:
    p = db.get(Produit, produit_id)
    if not p:
        raise ValueError(f"Produit {produit_id} introuvable")
    if p.stock_actuel < quantite:
        raise ValueError(f"Stock insuffisant pour {p.nom}: {p.stock_actuel:.1f} < {quantite:.1f}")
    qte_avant = p.stock_actuel
    p.stock_actuel -= quantite
    mvt = MouvementStock(
        produit_id=produit_id, lot_id=lot_id,
        type_mouvement="sortie", quantite=quantite,
        quantite_avant=qte_avant, quantite_apres=p.stock_actuel,
        motif=motif, reference_doc=reference_doc,
        responsable=responsable, date_saisie=datetime.now()
    )
    db.add(mvt)
    if lot_id:
        lot = db.get(Lot, lot_id)
        if lot: lot.quantite_restante -= quantite
    db.commit(); db.refresh(mvt)
    return mvt

def get_mouvements(db: Session, produit_id: Optional[int] = None,
                   type_mvt: Optional[str] = None, limite: int = 100,
                   date_debut: Optional[str] = None, date_fin: Optional[str] = None) -> List[MouvementStock]:
    q = db.query(MouvementStock).options(
        joinedload(MouvementStock.produit), joinedload(MouvementStock.lot)
    )
    if produit_id:
        q = q.filter(MouvementStock.produit_id == produit_id)
    if type_mvt:
        q = q.filter(MouvementStock.type_mouvement == type_mvt)
    if date_debut:
        q = q.filter(MouvementStock.date_saisie >= date_debut)
    if date_fin:
        q = q.filter(MouvementStock.date_saisie <= f"{date_fin} 23:59:59")
    return q.order_by(MouvementStock.date_saisie.desc()).limit(limite).all()

# ── ALERTES ──

def get_produits_stock_bas(db: Session) -> List[Produit]:
    return db.query(Produit).options(joinedload(Produit.categorie)).filter(
        Produit.actif == True, Produit.stock_actuel <= Produit.stock_min, Produit.stock_actuel > 0
    ).order_by(Produit.stock_actuel.asc()).all()

def get_produits_rupture(db: Session) -> List[Produit]:
    return db.query(Produit).options(joinedload(Produit.categorie)).filter(
        Produit.actif == True, Produit.stock_actuel <= 0
    ).all()

# ── LOTS ──

def get_lots(db: Session, statut: Optional[str] = None, skip: int = 0, limit: int = 100,
             recherche: Optional[str] = None, produit_id: Optional[int] = None) -> List[Lot]:
    q = db.query(Lot).options(joinedload(Lot.produit), joinedload(Lot.fournisseur),
                              joinedload(Lot.etapes))
    if statut:
        q = q.filter(Lot.statut == statut)
    if recherche:
        q = q.filter(Lot.code_lot.ilike(f"%{recherche}%"))
    if produit_id is not None:
        q = q.filter(Lot.produit_id == produit_id)
    return q.order_by(Lot.date_reception.desc()).offset(skip).limit(limit).all()

def get_lot(db: Session, lot_id: int) -> Optional[Lot]:
    return db.query(Lot).options(
        joinedload(Lot.produit), joinedload(Lot.fournisseur),
        joinedload(Lot.etapes)
    ).filter(Lot.id == lot_id).first()

def create_lot(db: Session, **data) -> Lot:
    lot = Lot(**data)
    if not lot.quantite_restante:
        lot.quantite_restante = lot.poids_frais
    db.add(lot); db.flush()
    etapes_defaut = [
        ("musserie", 1), ("production", 2), ("conditionnement", 3)
    ]
    for nom_etape, ordre in etapes_defaut:
        ep = EtapeProduction(lot_id=lot.id, etape=nom_etape, ordre=ordre, statut="en_attente")
        db.add(ep)
    db.commit(); db.refresh(lot)
    return lot

def changer_statut_lot(db: Session, lot_id: int, nouveau_statut: str) -> Optional[Lot]:
    lot = db.get(Lot, lot_id)
    if not lot: return None
    lot.statut = nouveau_statut
    db.commit(); db.refresh(lot)
    return lot

def count_lots_actifs(db: Session) -> int:
    return db.query(func.count(Lot.id)).filter(
        Lot.statut.notin_(["expédié", "périmé"])
    ).scalar()

# ── ETAPES DE PRODUCTION ──

def get_etapes_lot(db: Session, lot_id: int) -> List[EtapeProduction]:
    return db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id
    ).order_by(EtapeProduction.ordre).all()

def get_etape(db: Session, etape_id: int) -> Optional[EtapeProduction]:
    return db.get(EtapeProduction, etape_id)

def demarrer_etape(db: Session, etape_id: int, operateur: str = "") -> Optional[EtapeProduction]:
    ep = db.get(EtapeProduction, etape_id)
    if not ep: return None
    ep.statut = "en_cours"
    ep.date_debut = datetime.now()
    if operateur:
        ep.operateur = operateur
    etapes = get_etapes_lot(db, ep.lot_id)
    for i, e in enumerate(etapes):
        if e.id == ep.id and i > 0:
            prev = etapes[i - 1]
            if prev.poids_sortie > 0 and ep.poids_entree == 0:
                ep.poids_entree = prev.poids_sortie
            break
    db.commit(); db.refresh(ep)
    return ep

# ── MUSSERIE (cumul journalier) ──

def valider_musserie(db: Session, lot_id: int,
                     fruits_murs_kg: float = 0.0,
                     dechets_tri_kg: float = 0.0,
                     dechets_lavage_kg: float = 0.0,
                     retour_non_mur_kg: float = 0.0,
                     dechets_production_kg: float = 0.0,
                     operateur: str = "") -> Optional[EtapeProduction]:
    lot = db.get(Lot, lot_id)
    if not lot:
        raise ValueError(f"Lot {lot_id} introuvable")
    ep = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "musserie"
    ).first()
    if not ep:
        ep = EtapeProduction(lot_id=lot_id, etape="musserie", ordre=1, statut="en_cours")
        db.add(ep); db.flush()
    if ep.statut == "en_attente":
        ep.statut = "en_cours"
        ep.date_debut = datetime.now()
    if operateur:
        ep.operateur = operateur

    ep.fruits_murs_kg = (ep.fruits_murs_kg or 0) + fruits_murs_kg
    ep.dechets_tri_kg = (ep.dechets_tri_kg or 0) + dechets_tri_kg
    ep.dechets_lavage_kg = (ep.dechets_lavage_kg or 0) + dechets_lavage_kg
    ep.retour_non_mur_kg = (ep.retour_non_mur_kg or 0) + retour_non_mur_kg
    ep.dechets_production_kg = (ep.dechets_production_kg or 0) + dechets_production_kg

    poids_sortie = max(0, ep.fruits_murs_kg - ep.retour_non_mur_kg - ep.dechets_lavage_kg - ep.dechets_production_kg)
    ep.poids_sortie = round(poids_sortie, 2)
    perte = ep.dechets_tri_kg + ep.dechets_lavage_kg + ep.dechets_production_kg
    ep.perte = round(perte, 2)
    total_consomme = poids_sortie + perte
    ep.rendement_pourcentage = round((poids_sortie / total_consomme) * 100, 1) if total_consomme > 0 else None

    base_restant = lot.quantite_restante or lot.poids_frais or 0
    delta = fruits_murs_kg + dechets_tri_kg - retour_non_mur_kg
    lot.quantite_restante = round(max(0, base_restant - delta), 2)
    if lot.statut == "réception":
        lot.statut = "en musserie"

    db.commit()
    db.refresh(ep)
    return ep

# ── PRODUCTION (chargement chariots → séchoir) ──

DRYER_CONFIG = {1: {"chariots": 6, "claies": 42}, 2: {"chariots": 12, "claies": 20}}

def valider_production(db: Session, lot_id: int, dryer: int, nbre_chariots: int,
                       quantite_totale: float, operateur: str = "",
                       chariots: list = None) -> dict:
    lot = db.get(Lot, lot_id)
    if not lot:
        raise ValueError(f"Lot {lot_id} introuvable")
    config = DRYER_CONFIG.get(dryer)
    if not config:
        raise ValueError(f"Dryer {dryer} invalide (1 ou 2)")
    if nbre_chariots > config["chariots"]:
        raise ValueError(f"Dryer {dryer} prend max {config['chariots']} chariots")

    ep = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "production"
    ).first()
    if not ep:
        ep = EtapeProduction(lot_id=lot_id, etape="production", ordre=2, statut="en_cours")
        db.add(ep); db.flush()

    ep.statut = "en_cours"
    if not ep.date_debut:
        ep.date_debut = datetime.now()
    ep.operateur = operateur

    for c_data in (chariots or []):
        chariot = Chariot(
            etape_production_id=ep.id, lot_id=lot_id,
            numero_chariot=c_data.get("numero_chariot", 0),
            dryer=dryer,
            nbre_chariots=nbre_chariots,
            total_claies=config["claies"] * nbre_chariots,
            quantite_totale=quantite_totale,
            operateur=operateur,
            heure_remplissage=c_data.get("heure_remplissage", ""),
            heure_entree_sechoir=c_data.get("heure_entree_sechoir", ""),
        )
        db.add(chariot)

    db.flush()

    all_chariots = db.query(Chariot).filter(Chariot.etape_production_id == ep.id).all()
    dryers_seen = {}
    for c in all_chariots:
        if c.dryer not in dryers_seen:
            dryers_seen[c.dryer] = {"dryer": c.dryer, "nbre_chariots": c.nbre_chariots, "total_claies": c.total_claies, "quantite_totale": c.quantite_totale}
    ep.poids_entree = sum(d["quantite_totale"] for d in dryers_seen.values())
    ep.poids_sortie = ep.poids_entree
    ep.total_claies = sum(d["total_claies"] for d in dryers_seen.values())
    ep.dryer = None
    ep.nbre_chariots = None
    ep.notes = " + ".join(f"Dryer {d['dryer']} ({d['nbre_chariots']} chariots)" for d in dryers_seen.values())

    db.commit(); db.refresh(ep)
    return {"etape": ep, "dryers": list(dryers_seen.values())}


def cloturer_production(db: Session, lot_id: int) -> Optional[EtapeProduction]:
    ep = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "production"
    ).first()
    if not ep:
        raise ValueError(f"Aucune étape production pour le lot {lot_id}")
    ep.statut = "terminé"
    ep.date_fin = datetime.now()
    db.commit(); db.refresh(ep)
    return ep


def get_dryers_production(db: Session, lot_id: int) -> list:
    ep = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "production"
    ).first()
    if not ep:
        return []
    chariots = db.query(Chariot).filter(Chariot.etape_production_id == ep.id).order_by(Chariot.id).all()
    dryers = {}
    for c in chariots:
        d = c.dryer
        if d not in dryers:
            dryers[d] = {"dryer": d, "nbre_chariots": c.nbre_chariots, "total_claies": c.total_claies, "quantite_totale": c.quantite_totale, "operateur": c.operateur or "", "chariots": []}
        dryers[d]["chariots"].append({
            "id": c.id, "numero_chariot": c.numero_chariot,
            "heure_remplissage": c.heure_remplissage, "heure_entree_sechoir": c.heure_entree_sechoir,
        })
    return list(dryers.values())

# ── CONDITIONNEMENT (cartons) ──

def valider_conditionnement(db: Session, lot_id: int,
                            export_cartons: int = 0, export_sachets: int = 0, export_poids_sachet: float = 2.5,
                            local_cartons: int = 0, local_sachets: int = 0, local_poids_sachet: float = 2.5,
                            dechets_cartons: int = 0, dechets_sachets: int = 0, dechets_poids_sachet: float = 2.5,
                            rhum_cartons: int = 0, rhum_sachets: int = 0, rhum_poids_sachet: float = 2.5,
                            fitini_fê_cartons: int = 0, fitini_fê_sachets: int = 0, fitini_fê_poids_sachet: float = 2.5,
                            responsable: str = "", notes: str = "") -> dict:
    lot = get_lot(db, lot_id)
    if not lot:
        raise ValueError(f"Lot {lot_id} introuvable")

    is_mangue = lot.produit and "mangue" in lot.produit.nom.lower()
    if not is_mangue:
        rhum_cartons = 0; rhum_sachets = 0; rhum_poids_sachet = 2.5

    poids_export = round((export_cartons * 6 + export_sachets) * export_poids_sachet, 2)
    poids_local = round((local_cartons * 6 + local_sachets) * local_poids_sachet, 2)
    poids_dechets = round((dechets_cartons * 6 + dechets_sachets) * dechets_poids_sachet, 2)
    poids_rhum = round((rhum_cartons * 6 + rhum_sachets) * rhum_poids_sachet, 2)
    poids_fitini = round((fitini_fê_cartons * 6 + fitini_fê_sachets) * fitini_fê_poids_sachet, 2)
    total_flux = round(poids_export + poids_local + poids_dechets + poids_rhum + poids_fitini, 2)

    etape_cond = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "conditionnement"
    ).first()
    reference = etape_cond.poids_entree if etape_cond else 0.0

    ecart_pourcentage = None
    if reference and reference > 0:
        ecart_pourcentage = round(abs(reference - total_flux) / reference * 100, 2)

    lot.export_cartons = export_cartons; lot.export_sachets = export_sachets
    lot.export_poids_sachet = export_poids_sachet
    lot.local_cartons = local_cartons; lot.local_sachets = local_sachets
    lot.local_poids_sachet = local_poids_sachet
    lot.dechets_cartons = dechets_cartons; lot.dechets_sachets = dechets_sachets
    lot.dechets_poids_sachet = dechets_poids_sachet
    lot.rhum_cartons = rhum_cartons; lot.rhum_sachets = rhum_sachets
    lot.rhum_poids_sachet = rhum_poids_sachet
    lot.fitini_fê_cartons = fitini_fê_cartons; lot.fitini_fê_sachets = fitini_fê_sachets
    lot.fitini_fê_poids_sachet = fitini_fê_poids_sachet
    lot.ecart_bilan_pourcentage = ecart_pourcentage
    lot.poids_sec_final = total_flux
    if lot.poids_frais > 0:
        lot.rendement_global = round((total_flux / lot.poids_frais) * 100, 1)
    if notes:
        lot.notes = (lot.notes + " | " if lot.notes else "") + notes
    lot.statut = "terminé"

    etape_cond.statut = "termine"
    etape_cond.date_fin = datetime.now()
    etape_cond.poids_sortie = total_flux
    etape_cond.rendement_pourcentage = lot.rendement_global

    db.commit(); db.refresh(lot)

    return {
        "lot_id": lot_id,
        "code_lot": lot.code_lot,
        "poids_export": poids_export,
        "poids_local": poids_local,
        "poids_dechets": poids_dechets,
        "poids_rhum": poids_rhum,
        "poids_fitini_fê": poids_fitini,
        "total_flux": total_flux,
        "reference": round(reference, 2) if reference else 0.0,
        "ecart_bilan_pourcentage": ecart_pourcentage,
        "rendement_global": lot.rendement_global,
        "statut_lot": lot.statut,
        "poids_sec_final": total_flux,
    }

# ── ZONES DE STOCKAGE ──

def get_zones_stockage(db: Session, actif: bool = True) -> List[ZoneStockage]:
    q = db.query(ZoneStockage)
    if actif: q = q.filter(ZoneStockage.actif == True)
    return q.order_by(ZoneStockage.nom).all()

def get_zone_stockage(db: Session, zone_id: int) -> Optional[ZoneStockage]:
    return db.get(ZoneStockage, zone_id)

def create_zone_stockage(db: Session, **data) -> ZoneStockage:
    z = ZoneStockage(**data)
    db.add(z); db.commit(); db.refresh(z)
    return z

def get_stocks_zone(db: Session, zone_id: Optional[int] = None,
                    produit_id: Optional[int] = None) -> List[StockZone]:
    q = db.query(StockZone).options(
        joinedload(StockZone.zone), joinedload(StockZone.lot), joinedload(StockZone.produit)
    ).filter(StockZone.date_sortie.is_(None))
    if zone_id is not None:
        q = q.filter(StockZone.zone_id == zone_id)
    if produit_id is not None:
        q = q.filter(StockZone.produit_id == produit_id)
    return q.order_by(StockZone.date_entree.desc()).all()

def stocker_en_zone(db: Session, zone_id: int, produit_id: int,
                    quantite: float, lot_id: Optional[int] = None) -> StockZone:
    sz = StockZone(zone_id=zone_id, lot_id=lot_id, produit_id=produit_id,
                   quantite=quantite, date_entree=datetime.now())
    db.add(sz); db.commit(); db.refresh(sz)
    return sz

def sortir_de_zone(db: Session, stock_zone_id: int) -> Optional[StockZone]:
    sz = db.get(StockZone, stock_zone_id)
    if not sz: return None
    sz.date_sortie = datetime.now()
    db.commit(); db.refresh(sz)
    return sz

# ── COMMANDES ──

def get_commandes(db: Session, skip: int = 0, limit: int = 100,
                  statut: Optional[str] = None, recherche: Optional[str] = None) -> List[Commande]:
    q = db.query(Commande).options(
        joinedload(Commande.lignes).joinedload(LigneCommande.produit)
    )
    if statut:
        q = q.filter(Commande.statut == statut)
    if recherche:
        q = q.filter(Commande.client_nom.ilike(f"%{recherche}%"))
    return q.order_by(Commande.date_commande.desc()).offset(skip).limit(limit).all()

def get_commande(db: Session, commande_id: int) -> Optional[Commande]:
    return db.query(Commande).options(
        joinedload(Commande.lignes).joinedload(LigneCommande.produit)
    ).filter(Commande.id == commande_id).first()

def create_commande(db: Session, client_nom: str, lignes_data: list,
                    date_livraison_prevue=None, notes="") -> Commande:
    cmd = Commande(client_nom=client_nom, date_livraison_prevue=date_livraison_prevue,
                   notes=notes, statut="en_attente")
    db.add(cmd); db.flush()
    total = 0.0
    for ligne in lignes_data:
        p = db.get(Produit, ligne["produit_id"])
        prix = ligne.get("prix_unitaire", p.prix_unitaire if p else 0)
        li = LigneCommande(commande_id=cmd.id, produit_id=ligne["produit_id"],
                           lot_id=ligne.get("lot_id"), quantite=ligne["quantite"],
                           prix_unitaire=prix)
        db.add(li)
        total += ligne["quantite"] * prix
    cmd.total_ht = total
    db.commit(); db.refresh(cmd)
    return cmd

def update_commande_statut(db: Session, commande_id: int, statut: str) -> Optional[Commande]:
    cmd = db.get(Commande, commande_id)
    if not cmd: return None
    cmd.statut = statut
    if statut == "livrée":
        cmd.date_livraison_reelle = datetime.now()
    db.commit(); db.refresh(cmd)
    return cmd

def get_commandes_en_attente_count(db: Session) -> int:
    return db.query(func.count(Commande.id)).filter(
        Commande.statut.in_(["en_attente", "préparée"])
    ).scalar()

# ── CATÉGORIES ──

def get_categories(db: Session) -> List[Categorie]:
    return db.query(Categorie).order_by(Categorie.nom).all()

def create_categorie(db: Session, nom: str, couleur: str = "#a04100", description: str = "") -> Categorie:
    c = Categorie(nom=nom, couleur=couleur, description=description)
    db.add(c); db.commit(); db.refresh(c)
    return c

# ── FOURNISSEURS ──

def get_fournisseurs(db: Session, actif: bool = True) -> List[Fournisseur]:
    q = db.query(Fournisseur)
    if actif: q = q.filter(Fournisseur.actif == True)
    return q.order_by(Fournisseur.nom).all()

def get_fournisseur(db: Session, fournisseur_id: int) -> Optional[Fournisseur]:
    return db.get(Fournisseur, fournisseur_id)

def create_fournisseur(db: Session, **data) -> Fournisseur:
    f = Fournisseur(**data)
    db.add(f); db.commit(); db.refresh(f)
    return f

def update_fournisseur(db: Session, fournisseur_id: int, **data) -> Optional[Fournisseur]:
    f = db.get(Fournisseur, fournisseur_id)
    if not f: return None
    for k, v in data.items():
        setattr(f, k, v)
    db.commit(); db.refresh(f)
    return f

# ── RENDEMENTS ──

def calculer_rendements_lot(db: Session, lot_id: int) -> dict:
    lot = get_lot(db, lot_id)
    if not lot: return {}
    etapes = get_etapes_lot(db, lot_id)
    rendements = []
    for ep in etapes:
        if ep.poids_entree > 0 and ep.poids_sortie > 0:
            rendements.append({
                "etape": ep.etape,
                "poids_entree": ep.poids_entree,
                "poids_sortie": ep.poids_sortie,
                "perte": ep.perte,
                "rendement": ep.rendement_pourcentage,
            })
    return {
        "lot_id": lot_id,
        "code_lot": lot.code_lot,
        "produit": lot.produit.nom if lot.produit else None,
        "poids_frais_total": lot.poids_frais,
        "poids_sec_final": lot.poids_sec_final,
        "rendement_global": lot.rendement_global,
        "etapes": rendements,
    }

def get_rendement_moyen_global(db: Session) -> Optional[float]:
    result = db.query(func.avg(Lot.rendement_global)).filter(
        Lot.rendement_global.isnot(None)
    ).scalar()
    return round(result, 1) if result else None

# ── DASHBOARD ──

def get_stats_dashboard(db: Session) -> dict:
    lots_en_prod = db.query(func.count(Lot.id)).filter(
        Lot.statut.notin_(["expédié", "périmé", "en stock"])
    ).scalar()
    stock_froid = db.query(func.coalesce(func.sum(StockZone.quantite), 0)).filter(
        StockZone.date_sortie.is_(None),
        StockZone.zone_id.in_(
            db.query(ZoneStockage.id).filter(ZoneStockage.type_zone == "froid")
        )
    ).scalar()
    return {
        "total_produits": count_produits(db),
        "total_mouvements": db.query(func.count(MouvementStock.id)).scalar(),
        "total_lots_actifs": count_lots_actifs(db),
        "produits_stock_bas": len(get_produits_stock_bas(db)),
        "produits_rupture": len(get_produits_rupture(db)),
        "valeur_stock": sum(
            p.stock_actuel * p.prix_unitaire
            for p in db.query(Produit).filter(Produit.actif == True).all()
        ),
        "commandes_en_attente": get_commandes_en_attente_count(db),
        "lots_en_production": lots_en_prod,
        "rendement_moyen": get_rendement_moyen_global(db),
        "stock_froid_kg": round(stock_froid, 1),
    }

def get_stats_production(db: Session) -> dict:
    lots_suivi = db.query(func.count(Lot.id)).filter(
        Lot.poids_frais > 0
    ).scalar()
    etapes_terminees = db.query(func.count(EtapeProduction.id)).filter(
        EtapeProduction.statut == "terminé"
    ).scalar()
    etapes_en_cours = db.query(func.count(EtapeProduction.id)).filter(
        EtapeProduction.statut == "en_cours"
    ).scalar()
    aujourdhui = datetime.now().strftime("%Y-%m-%d")
    prod_jour = db.query(func.coalesce(func.sum(EtapeProduction.poids_sortie), 0)).filter(
        func.date(EtapeProduction.date_fin) == aujourdhui
    ).scalar()
    return {
        "lots_suivi": lots_suivi,
        "etapes_terminees": etapes_terminees,
        "etapes_en_cours": etapes_en_cours,
        "rendement_moyen_frais_sec": get_rendement_moyen_global(db),
        "production_jour_kg": round(prod_jour, 1),
    }

# ── DEMANDE DE TRANSFERT CHAMBRE FROIDE ──

def creer_demande_transfert(db: Session, lot_id: int, lignes: list,
                            responsable: str = "", notes: str = "") -> "DemandeTransfert":
    from models import DemandeTransfert, DemandeTransfertLigne, ZoneStockage
    lot = get_lot(db, lot_id)
    if not lot:
        raise ValueError(f"Lot {lot_id} introuvable")
    if lot.statut != "terminé":
        raise ValueError(f"Le lot {lot.code_lot} n'a pas terminé le conditionnement")

    demande = DemandeTransfert(lot_id=lot_id, responsable=responsable, notes=notes)
    db.add(demande)
    db.flush()

    for l in lignes:
        zone = db.get(ZoneStockage, l.zone_id)
        if not zone:
            raise ValueError(f"Zone {l.zone_id} introuvable")
        if l.type_flux == "local":
            available = lot.local_cartons
        elif l.type_flux == "fitini_fê":
            available = lot.fitini_fê_cartons
        else:
            raise ValueError(f"Type flux inconnu : {l.type_flux}")
        if l.nb_cartons > available:
            raise ValueError(f"Pas assez de cartons {l.type_flux} : {available} disponibles, {l.nb_cartons} demandés")

        ligne = DemandeTransfertLigne(
            demande_id=demande.id, type_flux=l.type_flux,
            nb_cartons=l.nb_cartons, zone_id=l.zone_id,
        )
        db.add(ligne)

    db.commit(); db.refresh(demande)
    return demande


def valider_demande_transfert(db: Session, demande_id: int) -> "DemandeTransfert":
    from models import DemandeTransfert, DemandeTransfertLigne, StockZone, Produit
    demande = db.get(DemandeTransfert, demande_id)
    if not demande:
        raise ValueError(f"Demande {demande_id} introuvable")
    if demande.statut != "en_attente":
        raise ValueError(f"Demande déjà {demande.statut}")

    lot = get_lot(db, demande.lot_id)
    lignes = db.query(DemandeTransfertLigne).filter(DemandeTransfertLigne.demande_id == demande_id).all()

    produit_local = db.query(Produit).filter(Produit.nom == "Local").first()
    produit_fitini = db.query(Produit).filter(Produit.nom == "Fitini Fê").first()

    for ligne in lignes:
        if ligne.type_flux == "local":
            produit = produit_local
            poids_sachet = lot.local_poids_sachet
        else:
            produit = produit_fitini
            poids_sachet = lot.fitini_fê_poids_sachet
        if not produit:
            raise ValueError(f"Produit introuvable pour {ligne.type_flux}")

        quantite = round(ligne.nb_cartons * 6 * poids_sachet, 2)
        stock = StockZone(
            zone_id=ligne.zone_id, lot_id=lot.id, produit_id=produit.id,
            quantite=quantite, sachets=ligne.nb_cartons * 6,
        )
        db.add(stock)
        ligne.statut = "validee"

    demande.statut = "validee"
    lot.statut_transfert = "valide"
    db.commit(); db.refresh(demande)
    return demande


def annuler_demande_transfert(db: Session, demande_id: int) -> "DemandeTransfert":
    from models import DemandeTransfert
    demande = db.get(DemandeTransfert, demande_id)
    if not demande:
        raise ValueError(f"Demande {demande_id} introuvable")
    demande.statut = "annulee"
    db.commit(); db.refresh(demande)
    return demande


def get_demandes_transfert(db: Session, lot_id: int = None, statut: str = None):
    from models import DemandeTransfert
    q = db.query(DemandeTransfert)
    if lot_id:
        q = q.filter(DemandeTransfert.lot_id == lot_id)
    if statut:
        q = q.filter(DemandeTransfert.statut == statut)
    return q.order_by(DemandeTransfert.date_demande.desc()).all()


def get_demande_transfert(db: Session, demande_id: int):
    from models import DemandeTransfert
    return db.get(DemandeTransfert, demande_id)


# ── RECONDITIONNEMENT (sachets 100g) ──

def creer_reconditionnement(db: Session, lot_id: int, type_source: str,
                            nb_cartons_entree: int, responsable: str = "",
                            notes: str = "") -> dict:
    from models import Reconditionnement, StockZone, Produit
    lot = get_lot(db, lot_id)
    if not lot:
        raise ValueError(f"Lot {lot_id} introuvable")

    if type_source == "local":
        disponible = lot.local_cartons
        poids_sachet = lot.local_poids_sachet
    elif type_source == "fitini_fê":
        disponible = lot.fitini_fê_cartons
        poids_sachet = lot.fitini_fê_poids_sachet
    else:
        raise ValueError(f"Type source inconnu : {type_source}")

    if nb_cartons_entree > disponible:
        raise ValueError(f"Pas assez de cartons {type_source} : {disponible} dispo, {nb_cartons_entree} demandés")

    nb_sachets_100g = nb_cartons_entree * 6 * round(poids_sachet / 0.1)

    produit = db.query(Produit).filter(Produit.nom == f"Sachet 100g {type_source}").first()
    if not produit:
        produit = Produit(nom=f"Sachet 100g {type_source}", unite_mesure="unité",
                          stock_actuel=0, categorie_id=None)
        db.add(produit); db.flush()

    stock_exist = db.query(StockZone).filter(
        StockZone.lot_id == lot_id, StockZone.produit_id == produit.id,
        StockZone.date_sortie.is_(None)
    ).first()
    if stock_exist:
        stock_exist.quantite += nb_sachets_100g * 0.1
        stock_exist.sachets = (stock_exist.sachets or 0) + nb_sachets_100g
    else:
        stock_new = StockZone(
            zone_id=1, lot_id=lot_id, produit_id=produit.id,
            quantite=round(nb_sachets_100g * 0.1, 2), sachets=nb_sachets_100g,
        )
        db.add(stock_new)

    if type_source == "local":
        lot.local_cartons -= nb_cartons_entree
    else:
        lot.fitini_fê_cartons -= nb_cartons_entree

    recond = Reconditionnement(
        lot_id=lot_id, type_source=type_source,
        nb_cartons_entree=nb_cartons_entree,
        nb_sachets_100g_sortie=nb_sachets_100g,
        responsable=responsable, notes=notes,
    )
    db.add(recond)
    db.commit(); db.refresh(recond)

    return {
        "id": recond.id, "lot_id": lot_id, "type_source": type_source,
        "nb_cartons_entree": nb_cartons_entree,
        "nb_sachets_100g_sortie": nb_sachets_100g,
        "poids_total_kg": round(nb_sachets_100g * 0.1, 2),
    }


def get_reconditionnements(db: Session, lot_id: int = None):
    from models import Reconditionnement
    q = db.query(Reconditionnement)
    if lot_id:
        q = q.filter(Reconditionnement.lot_id == lot_id)
    return q.order_by(Reconditionnement.date_reconditionnement.desc()).all()


# ── DETECTION D'ANOMALIES ──

def detecter_anomalies(db: Session) -> list:
    from models import EtapeProduction, StockZone
    anomalies = []
    lots = db.query(Lot).filter(Lot.statut.notin_(["expédié", "périmé"])).all()
    for lot in lots:
        etapes = get_etapes_lot(db, lot.id)

        if lot.statut in ["en production", "en conditionnement", "terminé"]:
            musserie = next((e for e in etapes if e.etape == "musserie"), None)
            if not musserie or musserie.statut != "terminé":
                anomalies.append({"lot": lot.code_lot, "lot_id": lot.id, "type": "production_sans_musserie",
                                  "message": f"{lot.code_lot} est en {lot.statut} mais n'a pas de musserie terminée",
                                  "severite": "error"})

        if lot.statut in ["en conditionnement", "terminé"]:
            prod = next((e for e in etapes if e.etape == "production"), None)
            if not prod or prod.statut != "terminé":
                anomalies.append({"lot": lot.code_lot, "lot_id": lot.id, "type": "conditionnement_sans_production",
                                  "message": f"{lot.code_lot} est en {lot.statut} mais la production n'est pas terminée",
                                  "severite": "error"})

        if lot.statut == "terminé":
            cond = next((e for e in etapes if e.etape == "conditionnement"), None)
            if not cond or cond.statut != "termine":
                anomalies.append({"lot": lot.code_lot, "lot_id": lot.id, "type": "termine_sans_conditionnement",
                                  "message": f"{lot.code_lot} est terminé mais le conditionnement n'est pas fait",
                                  "severite": "warning"})

            if lot.statut_transfert == "en_attente":
                has_local = lot.local_cartons > 0
                has_fitini = lot.fitini_fê_cartons > 0
                if has_local or has_fitini:
                    anomalies.append({"lot": lot.code_lot, "lot_id": lot.id, "type": "pas_de_transfert",
                                      "message": f"{lot.code_lot} a des cartons non transférés en chambre froide",
                                      "severite": "warning"})

    return anomalies


# ── HISTORIQUE MUSSERIE ──

def get_historique_musserie(db: Session, lot_id: int = None):
    from models import EtapeProduction
    q = db.query(EtapeProduction).filter(EtapeProduction.etape == "musserie")
    if lot_id:
        q = q.filter(EtapeProduction.lot_id == lot_id)
    return q.order_by(EtapeProduction.date_debut.desc()).all()


def get_historique_production(db: Session, lot_id: int = None):
    from models import EtapeProduction
    q = db.query(EtapeProduction).filter(EtapeProduction.etape == "production")
    if lot_id:
        q = q.filter(EtapeProduction.lot_id == lot_id)
    return q.order_by(EtapeProduction.date_debut.desc()).all()


def get_historique_conditionnement(db: Session, lot_id: int = None):
    from models import EtapeProduction
    q = db.query(EtapeProduction).filter(EtapeProduction.etape == "conditionnement")
    if lot_id:
        q = q.filter(EtapeProduction.lot_id == lot_id)
    return q.order_by(EtapeProduction.date_debut.desc()).all()
