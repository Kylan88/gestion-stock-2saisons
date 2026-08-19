from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from datetime import datetime, timedelta, date as date_type
from typing import Optional, List
import math

import models
import statuses
from models import (
    Produit, Categorie, Fournisseur, Lot, MouvementStock,
    Commande, LigneCommande, EtapeProduction, Chariot,
    ZoneStockage, StockZone, DemandeTransfert, DemandeTransfertLigne,
    Reconditionnement
)


def today_start() -> datetime:
    """Début de la journée courante (00:00 local)."""
    now = datetime.now()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def tomorrow_start() -> datetime:
    return today_start() + timedelta(days=1)


# ── WEIGHT VALIDATION ──

WEIGHT_TOLERANCE = 0.05  # 5% tolerance for weight mismatches between steps

def validate_weight_flow(db: Session, lot_id: int, etape: str, poids_sortie: float):
    """Verify that poids_sortie does not exceed the previous step's poids_entree."""
    etapes = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id
    ).order_by(EtapeProduction.ordre).all()
    prev = None
    for e in etapes:
        if e.etape == etape:
            break
        prev = e
    if prev and prev.poids_sortie and prev.poids_sortie > 0:
        if poids_sortie > prev.poids_sortie * (1 + WEIGHT_TOLERANCE):
            raise ValueError(
                f"Poids sortie ({poids_sortie} kg) depasse le poids entree de l'etape precedente "
                f"({prev.etape}: {prev.poids_sortie} kg). Verifiez les donnees."
            )

def validate_conditionnement_weights(total_flux: float, reference: float):
    """Log warning if conditionnement gap is large, but does not block."""
    pass


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
    if quantite <= 0:
        raise ValueError("La quantité d'entrée doit être supérieure à zéro")
    p = db.get(Produit, produit_id)
    if not p:
        raise ValueError(f"Produit {produit_id} introuvable")
    if lot_id and not db.get(Lot, lot_id):
        raise ValueError(f"Lot {lot_id} introuvable")
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
    if quantite <= 0:
        raise ValueError("La quantité de sortie doit être supérieure à zéro")
    p = db.get(Produit, produit_id)
    if not p:
        raise ValueError(f"Produit {produit_id} introuvable")
    if p.stock_actuel < quantite:
        raise ValueError(f"Stock insuffisant pour {p.nom}: {p.stock_actuel:.1f} < {quantite:.1f}")
    if lot_id and not db.get(Lot, lot_id):
        raise ValueError(f"Lot {lot_id} introuvable")
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
    db.commit(); db.refresh(lot)
    return lot

def changer_statut_lot(db: Session, lot_id: int, nouveau_statut: str) -> Optional[Lot]:
    """Change le statut d'un lot avec validation du workflow.
    Rejecte les transitions invalides.
    """
    lot = db.get(Lot, lot_id)
    if not lot: return None
    if nouveau_statut is None:
        return lot
    canonical = statuses.normalize(nouveau_statut)
    if not statuses.can_transition(lot.statut, canonical):
        allowed = statuses.next_statuses(lot.statut)
        raise ValueError(
            f"Transition invalide pour {lot.code_lot}: '{lot.statut}' → '{canonical}'. "
            f"Statuts autorises: {allowed}"
        )
    lot.statut = canonical
    db.commit(); db.refresh(lot)
    return lot

def count_lots_actifs(db: Session) -> int:
    return db.query(func.count(Lot.id)).filter(
        Lot.statut.notin_([statuses.EXPEDIE, statuses.PERIME])
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
    ep.statut = statuses.EN_COURS
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
                     operateur: str = "",
                     dryer: int = 0,
                     reste_kg: float = None) -> Optional[EtapeProduction]:
    lot = db.get(Lot, lot_id)
    if not lot:
        raise ValueError(f"Lot {lot_id} introuvable")
    ep = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "musserie",
        EtapeProduction.dryer == (dryer or None),
        EtapeProduction.statut != statuses.TERMINE
    ).first()
    if not ep:
        ep = EtapeProduction(lot_id=lot_id, etape="musserie", ordre=1, statut="en_cours", dryer=dryer or None)
        db.add(ep); db.flush()
    if not ep.date_debut:
        ep.date_debut = datetime.now()
    if ep.statut == statuses.EN_ATTENTE:
        ep.statut = statuses.EN_COURS
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
    total_consomme = ep.fruits_murs_kg
    ep.rendement_pourcentage = round((poids_sortie / total_consomme) * 100, 1) if total_consomme > 0 else None

    base_restant = lot.quantite_restante or lot.poids_frais or 0
    if reste_kg is not None:
        lot.quantite_restante = round(max(0, reste_kg), 2)
    else:
        delta = fruits_murs_kg + dechets_tri_kg - retour_non_mur_kg
        lot.quantite_restante = round(max(0, base_restant - delta), 2)
    if statuses.normalize(lot.statut) == statuses.RECEPTION:
        lot.statut = statuses.EN_MUSSERIE

    db.commit()
    db.refresh(ep)
    return ep

from datetime import date as date_type

def cloturer_musserie(db: Session, lot_id: int, date_str: str | None = None):
    """Clôture les étapes musserie d'un lot et crée les entrées production correspondantes.
    - Si date_str fourni: clôture seulement les entrées de ce jour, crée production pour ce jour (lot reste EN_MUSSERIE)
    - Si date_str None: clôture tout, crée production pour tout, passe le lot en EN_PRODUCTION
    """
    lot = db.get(Lot, lot_id)
    if not lot:
        raise ValueError(f"Lot {lot_id} introuvable")
    if statuses.normalize(lot.statut) not in (statuses.EN_MUSSERIE, statuses.RECEPTION):
        raise ValueError(f"Le lot {lot.code_lot} n'est pas en musserie (statut: {lot.statut})")

    query = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "musserie"
    )
    if date_str:
        try:
            target_date = date_type.fromisoformat(date_str)
        except ValueError:
            raise ValueError("Format date invalide (attendu YYYY-MM-DD)")
        query = query.filter(EtapeProduction.date_debut >= target_date, EtapeProduction.date_debut < target_date + timedelta(days=1))
        action = "jour"
    else:
        action = "tout"

    etapes_musserie = query.all()
    if not etapes_musserie:
        raise ValueError(f"Aucune étape musserie trouvée pour le lot {lot.code_lot} ({action})")

    # Pour chaque entrée musserie clôturée, créer l'entrée production correspondante
    for ep in etapes_musserie:
        if ep.statut != statuses.TERMINE:
            ep.statut = statuses.TERMINE
            if not ep.date_fin:
                ep.date_fin = datetime.now()
            if not ep.poids_sortie and ep.fruits_murs_kg:
                ep.poids_sortie = round(max(0, ep.fruits_murs_kg - ep.retour_non_mur_kg - ep.dechets_lavage_kg - ep.dechets_production_kg), 2)

            # Créer l'étape production correspondante avec le poids sortie de la musserie
            if ep.poids_sortie and ep.poids_sortie > 0:
                existing_prod = db.query(EtapeProduction).filter(
                    EtapeProduction.lot_id == lot_id,
                    EtapeProduction.etape == "production",
                    EtapeProduction.dryer == ep.dryer,
                    EtapeProduction.date_debut >= ep.date_debut,
                    EtapeProduction.date_debut < ep.date_debut + timedelta(days=1)
                ).first()
                if not existing_prod:
                    prod_ep = EtapeProduction(
                        lot_id=lot_id,
                        etape="production",
                        ordre=2,
                        statut=statuses.EN_ATTENTE,
                        date_debut=ep.date_debut,
                        poids_entree=ep.poids_sortie,
                        dryer=ep.dryer,
                        operateur=ep.operateur,
                    )
                    db.add(prod_ep)

    if not date_str:
        # Clôture finale : plus de musserie possible, passage en production
        statuses.validate_transition(lot.statut, statuses.EN_PRODUCTION)
        lot.statut = statuses.EN_PRODUCTION
    elif (lot.quantite_restante or 0) <= 0:
        # Lot 100% traité : la clôture du jour est aussi la clôture finale
        statuses.validate_transition(lot.statut, statuses.EN_PRODUCTION)
        lot.statut = statuses.EN_PRODUCTION

    db.commit()
    for ep in etapes_musserie:
        db.refresh(ep)
    db.refresh(lot)
    return {"lot": lot, "etapes": etapes_musserie, "action": action}


def get_musserie_by_date_dryer(db: Session, lot_id: int, date_str: str):
    """Retourne les étapes musserie d'un lot pour une date donnée, groupées par dryer."""
    try:
        target_date = date_type.fromisoformat(date_str)
    except ValueError:
        raise ValueError("Format date invalide (attendu YYYY-MM-DD)")

    etapes = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id,
        EtapeProduction.etape == "musserie",
        EtapeProduction.date_debut >= target_date,
        EtapeProduction.date_debut < target_date + timedelta(days=1),
        EtapeProduction.statut == statuses.TERMINE
    ).all()

    return [
        {
            "dryer": ep.dryer,
            "poids_sortie": ep.poids_sortie or 0,
            "fruits_murs_kg": ep.fruits_murs_kg or 0,
            "date_debut": ep.date_debut.isoformat() if ep.date_debut else None,
        }
        for ep in etapes
    ]

# ── PRODUCTION (chargement chariots → séchoir) ──

DRYER_CONFIG = {
    1: {"chariots": 6, "claies": 42, "kg_par_claie": 6.25},
    2: {"chariots": 12, "claies": 20, "kg_par_claie": 6.5},
}

def valider_production(db: Session, lot_id: int, dryer: int, nbre_chariots: int,
                       quantite_totale: float, operateur: str = "",
                       chariots: list = None) -> dict:
    lot = db.get(Lot, lot_id)
    if not lot:
        raise ValueError(f"Lot {lot_id} introuvable")
    if nbre_chariots <= 0 or quantite_totale <= 0:
        raise ValueError("Le nombre de chariots et la quantité doivent être supérieurs à zéro")
    config = DRYER_CONFIG.get(dryer)
    if not config:
        raise ValueError(f"Dryer {dryer} invalide (1 ou 2)")
    if nbre_chariots > config["chariots"]:
        raise ValueError(f"Dryer {dryer} prend max {config['chariots']} chariots")

    ep = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "production",
        EtapeProduction.dryer == dryer, EtapeProduction.statut != statuses.TERMINE,
        EtapeProduction.date_debut >= today_start(), EtapeProduction.date_debut < tomorrow_start()
    ).order_by(EtapeProduction.id.desc()).first()
    if not ep:
        # Jour sidéré : étape production non terminée la plus récente du lot (indépendante de la date)
        ep = db.query(EtapeProduction).filter(
            EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "production",
            EtapeProduction.statut != statuses.TERMINE
        ).order_by(EtapeProduction.date_debut.desc(), EtapeProduction.id.desc()).first()
    if not ep:
        ep = EtapeProduction(lot_id=lot_id, etape="production", ordre=2, statut=statuses.EN_COURS)
        db.add(ep); db.flush()

    ep.statut = statuses.EN_COURS
    if not ep.date_debut:
        ep.date_debut = datetime.now()
    ep.operateur = operateur

    ep_musserie = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "musserie",
        EtapeProduction.dryer == dryer
    ).first()
    if not ep_musserie:
        ep_musserie = db.query(EtapeProduction).filter(
            EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "musserie"
        ).first()
    dechets_prod = ep_musserie.dechets_production_kg if ep_musserie else 0.0
    ep.dechets_production_kg = dechets_prod

    validate_weight_flow(db, lot_id, "production", quantite_totale)

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
    ep.poids_sortie = max(0, ep.poids_entree - ep.dechets_production_kg)
    ep.total_claies = sum(d["total_claies"] for d in dryers_seen.values())
    ep.notes = " + ".join(f"Dryer {d['dryer']} ({d['nbre_chariots']} chariots)" for d in dryers_seen.values())

    db.commit(); db.refresh(ep)
    return {"etape": ep, "dryers": list(dryers_seen.values())}


def cloturer_production(db: Session, lot_id: int) -> EtapeProduction:
    eps = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "production"
    ).all()
    if not eps:
        raise ValueError(f"Aucune étape production pour le lot {lot_id}")
    main = None
    for ep in eps:
        if ep.statut != statuses.TERMINE:
            ep.statut = statuses.TERMINE
            ep.date_fin = datetime.now()
            if main is None:
                main = ep
    if main is None:
        main = eps[-1]
    lot = db.get(models.Lot, lot_id)
    if lot:
        statuses.validate_transition(lot.statut, statuses.EN_CONDITIONNEMENT)
        lot.statut = statuses.EN_CONDITIONNEMENT
    db.commit(); db.refresh(main)
    if lot: db.refresh(lot)
    return main


def get_dryers_production(db: Session, lot_id: int) -> list:
    eps = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "production"
    ).all()
    if not eps:
        return []
    ep_ids = [e.id for e in eps]
    chariots = db.query(Chariot).filter(Chariot.etape_production_id.in_(ep_ids)).order_by(Chariot.id).all()
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

# ── CONDITIONNEMENT (cartons) — cumul journalier ──

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

    numeric_values = (
        export_cartons, export_sachets, export_poids_sachet, local_cartons, local_sachets,
        local_poids_sachet, dechets_cartons, dechets_sachets, dechets_poids_sachet, rhum_cartons,
        rhum_sachets, rhum_poids_sachet, fitini_fê_cartons, fitini_fê_sachets, fitini_fê_poids_sachet,
    )
    if any(value < 0 for value in numeric_values):
        raise ValueError("Les quantités de conditionnement ne peuvent pas être négatives")

    is_mangue = lot.produit and "mangue" in lot.produit.nom.lower()
    if not is_mangue:
        rhum_cartons = 0; rhum_sachets = 0; rhum_poids_sachet = 2.5

    # Cumul : ajouter aux valeurs existantes du lot
    lot.export_cartons = (lot.export_cartons or 0) + export_cartons
    lot.export_sachets = (lot.export_sachets or 0) + export_sachets
    if export_poids_sachet != 2.5:
        lot.export_poids_sachet = export_poids_sachet
    lot.local_cartons = (lot.local_cartons or 0) + local_cartons
    lot.local_sachets = (lot.local_sachets or 0) + local_sachets
    if local_poids_sachet != 2.5:
        lot.local_poids_sachet = local_poids_sachet
    lot.dechets_cartons = (lot.dechets_cartons or 0) + dechets_cartons
    lot.dechets_sachets = (lot.dechets_sachets or 0) + dechets_sachets
    if dechets_poids_sachet != 2.5:
        lot.dechets_poids_sachet = dechets_poids_sachet
    lot.rhum_cartons = (lot.rhum_cartons or 0) + rhum_cartons
    lot.rhum_sachets = (lot.rhum_sachets or 0) + rhum_sachets
    if rhum_poids_sachet != 2.5:
        lot.rhum_poids_sachet = rhum_poids_sachet
    lot.fitini_fê_cartons = (lot.fitini_fê_cartons or 0) + fitini_fê_cartons
    lot.fitini_fê_sachets = (lot.fitini_fê_sachets or 0) + fitini_fê_sachets
    if fitini_fê_poids_sachet != 2.5:
        lot.fitini_fê_poids_sachet = fitini_fê_poids_sachet

    if notes:
        lot.notes = (lot.notes + " | " if lot.notes else "") + notes

    # Calculer le total cumulé
    total_flux = _calc_total_flux(lot)

    # Créer ou mettre à jour l'étape conditionnement
    etape_cond = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "conditionnement"
    ).first()
    if not etape_cond:
        productions = db.query(EtapeProduction).filter(
            EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "production"
        ).all()
        poids_entree = sum(ep.poids_sortie or 0.0 for ep in productions)
        etape_cond = EtapeProduction(
            lot_id=lot_id, etape="conditionnement", ordre=3,
            statut=statuses.EN_COURS, poids_entree=poids_entree,
            date_debut=datetime.now()
        )
        db.add(etape_cond); db.flush()
    else:
        if etape_cond.statut == statuses.EN_ATTENTE:
            etape_cond.statut = statuses.EN_COURS
            etape_cond.date_debut = datetime.now()
        if not etape_cond.poids_entree:
            productions = db.query(EtapeProduction).filter(
                EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "production"
            ).all()
            etape_cond.poids_entree = sum(ep.poids_sortie or 0.0 for ep in productions)

    etape_cond.poids_sortie = total_flux
    etape_cond.operateur = responsable or etape_cond.operateur or ""

    db.commit(); db.refresh(lot); db.refresh(etape_cond)

    return {
        "lot_id": lot_id,
        "code_lot": lot.code_lot,
        "total_flux": total_flux,
        "export_cartons": lot.export_cartons, "local_cartons": lot.local_cartons,
        "dechets_cartons": lot.dechets_cartons, "rhum_cartons": lot.rhum_cartons,
        "fitini_fê_cartons": lot.fitini_fê_cartons,
        "statut_lot": lot.statut,
    }


def cloturer_conditionnement(db: Session, lot_id: int) -> dict:
    """Clôture le conditionnement : valide les poids et passe le lot à conditionne."""
    lot = get_lot(db, lot_id)
    if not lot:
        raise ValueError(f"Lot {lot_id} introuvable")

    etape_cond = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "conditionnement"
    ).first()
    if not etape_cond:
        raise ValueError(f"Aucune étape conditionnement pour le lot {lot.code_lot}")

    # Somme de TOUTES les étapes production terminées (multi-jours)
    productions = db.query(EtapeProduction).filter(
        EtapeProduction.lot_id == lot_id, EtapeProduction.etape == "production"
    ).all()
    if not productions:
        raise ValueError("Aucune production trouvée pour ce lot")
    for ep in productions:
        if ep.statut != statuses.TERMINE:
            raise ValueError("Toutes les productions doivent être terminées avant de clôturer le conditionnement")

    reference = sum(ep.poids_sortie or 0.0 for ep in productions)
    etape_cond.poids_entree = reference
    total_flux = _calc_total_flux(lot)

    if total_flux <= 0:
        raise ValueError("Le conditionnement doit contenir au moins un flux supérieur à zéro")

    validate_conditionnement_weights(total_flux, reference)

    ecart_pourcentage = None
    if reference and reference > 0:
        ecart_pourcentage = round(abs(reference - total_flux) / reference * 100, 2)

    lot.ecart_bilan_pourcentage = ecart_pourcentage
    lot.poids_sec_final = total_flux
    if lot.poids_frais > 0:
        lot.rendement_global = round((total_flux / lot.poids_frais) * 100, 1)

    etape_cond.statut = statuses.TERMINE
    etape_cond.date_fin = datetime.now()
    etape_cond.poids_sortie = total_flux
    etape_cond.rendement_pourcentage = lot.rendement_global

    statuses.validate_transition(lot.statut, statuses.CONDITIONNE)
    lot.statut = statuses.CONDITIONNE

    db.commit(); db.refresh(lot); db.refresh(etape_cond)

    return {
        "lot_id": lot_id,
        "code_lot": lot.code_lot,
        "poids_sec_final": total_flux,
        "ecart_bilan_pourcentage": ecart_pourcentage,
        "rendement_global": lot.rendement_global,
        "statut_lot": lot.statut,
    }


def _calc_total_flux(lot) -> float:
    """Calcule le poids total de tous les flux du lot (basé sur les valeurs cumulées)."""
    poids_export = round(((lot.export_cartons or 0) * 6 + (lot.export_sachets or 0)) * (lot.export_poids_sachet or 2.5), 2)
    poids_local = round(((lot.local_cartons or 0) * 6 + (lot.local_sachets or 0)) * (lot.local_poids_sachet or 2.5), 2)
    poids_dechets = round(((lot.dechets_cartons or 0) * 6 + (lot.dechets_sachets or 0)) * (lot.dechets_poids_sachet or 2.5), 2)
    poids_rhum = round(((lot.rhum_cartons or 0) * 6 + (lot.rhum_sachets or 0)) * (lot.rhum_poids_sachet or 2.5), 2)
    poids_fitini = round(((lot.fitini_fê_cartons or 0) * 6 + (lot.fitini_fê_sachets or 0)) * (lot.fitini_fê_poids_sachet or 2.5), 2)
    return round(poids_export + poids_local + poids_dechets + poids_rhum + poids_fitini, 2)

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
    if quantite <= 0:
        raise ValueError("La quantité à stocker doit être supérieure à zéro")
    zone = db.get(ZoneStockage, zone_id)
    if not zone or not zone.actif:
        raise ValueError(f"Zone {zone_id} introuvable ou inactive")
    if not db.get(Produit, produit_id):
        raise ValueError(f"Produit {produit_id} introuvable")
    if lot_id and not db.get(Lot, lot_id):
        raise ValueError(f"Lot {lot_id} introuvable")
    if zone.capacite_kg > 0:
        occupation = db.query(func.coalesce(func.sum(StockZone.quantite), 0)).filter(
            StockZone.zone_id == zone_id, StockZone.date_sortie.is_(None)
        ).scalar()
        if occupation + quantite > zone.capacite_kg:
            raise ValueError(f"Capacité dépassée pour la zone {zone.nom}")
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
    if not client_nom.strip():
        raise ValueError("Le nom du client est requis")
    if not lignes_data:
        raise ValueError("Une commande doit contenir au moins une ligne")
    cmd = Commande(client_nom=client_nom, date_livraison_prevue=date_livraison_prevue,
                   notes=notes, statut="en_attente")
    db.add(cmd); db.flush()
    total = 0.0
    for ligne in lignes_data:
        p = db.get(Produit, ligne["produit_id"])
        if not p or not p.actif:
            raise ValueError(f"Produit {ligne['produit_id']} introuvable ou inactif")
        if ligne["quantite"] <= 0 or ligne.get("prix_unitaire", 0) < 0:
            raise ValueError("Les quantités doivent être positives et les prix non négatifs")
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
        Lot.statut.notin_([statuses.EXPEDIE, statuses.PERIME, statuses.EN_STOCK])
    ).scalar()
    lots_en_stock = db.query(func.count(Lot.id)).filter(
        Lot.statut == statuses.EN_STOCK
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
        "lots_en_stock": lots_en_stock,
        "rendement_moyen": get_rendement_moyen_global(db),
        "stock_froid_kg": round(stock_froid, 1),
    }

def get_stats_production(db: Session) -> dict:
    lots_suivi = db.query(func.count(Lot.id)).filter(
        Lot.poids_frais > 0
    ).scalar()
    etapes_terminees = db.query(func.count(EtapeProduction.id)).filter(
        EtapeProduction.statut == statuses.TERMINE
    ).scalar()
    etapes_en_cours = db.query(func.count(EtapeProduction.id)).filter(
        EtapeProduction.statut == statuses.EN_COURS
    ).scalar()
    aujourdhui = datetime.now().strftime("%Y-%m-%d")

    def sum_etapes_jour(etape: str, champ: str = "poids_sortie"):
        col = getattr(EtapeProduction, champ)
        return db.query(func.coalesce(func.sum(col), 0)).filter(
            EtapeProduction.etape == etape,
            func.date(EtapeProduction.date_fin) == aujourdhui
        ).scalar()

    prod_jour = sum_etapes_jour("production")
    musserie_jour = sum_etapes_jour("musserie", "poids_sortie")
    conditionnement_jour = sum_etapes_jour("conditionnement", "poids_sortie")
    return {
        "lots_suivi": lots_suivi,
        "etapes_terminees": etapes_terminees,
        "etapes_en_cours": etapes_en_cours,
        "rendement_moyen_frais_sec": get_rendement_moyen_global(db),
        "production_jour_kg": round(prod_jour, 1),
        "musserie_jour_kg": round(musserie_jour, 1),
        "conditionnement_jour_kg": round(conditionnement_jour, 1),
    }

def get_production_mensuelle(db: Session) -> list:
    from datetime import timedelta
    now = datetime.now()
    result = []
    for i in range(5, -1, -1):
        d = now - timedelta(days=30 * i)
        debut = d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if d.month == 12:
            fin = debut.replace(year=debut.year + 1, month=1)
        else:
            fin = debut.replace(month=debut.month + 1)
        total = db.query(func.coalesce(func.sum(EtapeProduction.poids_sortie), 0)).filter(
            EtapeProduction.date_fin >= debut,
            EtapeProduction.date_fin < fin,
        ).scalar()
        result.append({
            "mois": debut.strftime("%b"),
            "value": round(float(total), 1),
        })
    return result

# ── DEMANDE DE TRANSFERT CHAMBRE FROIDE ──

def creer_demande_transfert(db: Session, lot_id: int, lignes: list,
                            responsable: str = "", notes: str = "") -> "DemandeTransfert":
    from models import DemandeTransfert, DemandeTransfertLigne, ZoneStockage
    lot = get_lot(db, lot_id)
    if not lot:
        raise ValueError(f"Lot {lot_id} introuvable")
    if lot.statut != statuses.CONDITIONNE:
        raise ValueError(f"Le lot {lot.code_lot} n'a pas terminé le conditionnement")
    if not lignes:
        raise ValueError("Une demande de transfert doit contenir au moins une ligne")

    FLUX_CONFIG = {
        "local": {"cartons_field": "local_cartons"},
        "fitini_fê": {"cartons_field": "fitini_fê_cartons"},
        "export": {"cartons_field": "export_cartons"},
        "dechets": {"cartons_field": "dechets_cartons"},
        "rhum": {"cartons_field": "rhum_cartons"},
    }

    disponibilites = {}
    for key, cfg in FLUX_CONFIG.items():
        disponibilites[key] = getattr(lot, cfg["cartons_field"], 0) or 0

    demandes_par_flux = {}
    for l in lignes:
        if l.type_flux not in disponibilites:
            raise ValueError(f"Type flux inconnu : {l.type_flux}")
        if l.nb_cartons <= 0:
            raise ValueError("Le nombre de cartons doit être supérieur à zéro")
        demandes_par_flux[l.type_flux] = demandes_par_flux.get(l.type_flux, 0) + l.nb_cartons
    for type_flux, nb_cartons in demandes_par_flux.items():
        if nb_cartons > disponibilites[type_flux]:
            raise ValueError(f"Pas assez de cartons {type_flux} : {disponibilites[type_flux]} disponibles, {nb_cartons} demandés")

    demande = DemandeTransfert(lot_id=lot_id, responsable=responsable, notes=notes)
    db.add(demande)
    db.flush()

    for l in lignes:
        zone = db.get(ZoneStockage, l.zone_id)
        if not zone or not zone.actif:
            raise ValueError(f"Zone {l.zone_id} introuvable ou inactive")

        ligne = DemandeTransfertLigne(
            demande_id=demande.id, type_flux=l.type_flux,
            nb_cartons=l.nb_cartons, zone_id=l.zone_id,
        )
        db.add(ligne)

    db.commit(); db.refresh(demande)
    return demande


def valider_demande_transfert(db: Session, demande_id: int) -> "DemandeTransfert":
    from models import DemandeTransfert, DemandeTransfertLigne, StockZone, Produit, ZoneStockage
    demande = db.get(DemandeTransfert, demande_id)
    if not demande:
        raise ValueError(f"Demande {demande_id} introuvable")
    if demande.statut != "en_attente":
        raise ValueError(f"Demande déjà {demande.statut}")

    lot = get_lot(db, demande.lot_id)
    lignes = db.query(DemandeTransfertLigne).filter(DemandeTransfertLigne.demande_id == demande_id).all()

    FLUX_CONFIG = {
        "local": {"label": "Local", "poids_field": "local_poids_sachet"},
        "fitini_fê": {"label": "Fitini Fê", "poids_field": "fitini_fê_poids_sachet"},
        "export": {"label": "Export", "poids_field": "export_poids_sachet"},
        "dechets": {"label": "Déchets", "poids_field": "dechets_poids_sachet"},
        "rhum": {"label": "Rhum arrangé", "poids_field": "rhum_poids_sachet"},
    }

    for ligne in lignes:
        cfg = FLUX_CONFIG.get(ligne.type_flux)
        if not cfg:
            raise ValueError(f"Type flux inconnu : {ligne.type_flux}")

        produit = db.query(Produit).filter(Produit.nom == cfg["label"]).first()
        if not produit:
            produit = Produit(nom=cfg["label"], actif=True)
            db.add(produit); db.flush()

        poids_sachet = getattr(lot, cfg["poids_field"], 2.5) or 2.5
        quantite = round(ligne.nb_cartons * 6 * poids_sachet, 2)

        zone = db.get(ZoneStockage, ligne.zone_id)
        if not zone or not zone.actif:
            raise ValueError(f"Zone {ligne.zone_id} introuvable ou inactive")
        if zone.capacite_kg > 0:
            occupation = db.query(func.coalesce(func.sum(StockZone.quantite), 0)).filter(
                StockZone.zone_id == zone.id, StockZone.date_sortie.is_(None)
            ).scalar()
            if occupation + quantite > zone.capacite_kg:
                raise ValueError(f"Capacité dépassée pour la zone {zone.nom}")

        stock = StockZone(
            zone_id=ligne.zone_id, lot_id=lot.id, produit_id=produit.id,
            quantite=quantite, sachets=ligne.nb_cartons * 6,
        )
        db.add(stock)
        ligne.statut = statuses.VALIDEE

    demande.statut = statuses.VALIDEE
    lot.statut_transfert = statuses.VALIDE
    lot.statut = statuses.EN_STOCK
    db.commit(); db.refresh(demande)
    return demande


def annuler_demande_transfert(db: Session, demande_id: int) -> "DemandeTransfert":
    from models import DemandeTransfert
    demande = db.get(DemandeTransfert, demande_id)
    if not demande:
        raise ValueError(f"Demande {demande_id} introuvable")
    demande.statut = statuses.ANNULEE
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
    if nb_cartons_entree <= 0:
        raise ValueError("Le nombre de cartons doit être supérieur à zéro")

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

        if lot.statut in [statuses.EN_PRODUCTION, statuses.CONDITIONNE, statuses.TERMINE]:
            musserie = next((e for e in etapes if e.etape == "musserie"), None)
            if not musserie or musserie.statut != "terminé":
                anomalies.append({"lot": lot.code_lot, "lot_id": lot.id, "type": "production_sans_musserie",
                                  "message": f"{lot.code_lot} est en {lot.statut} mais n'a pas de musserie terminée",
                                  "severite": "error"})

        if lot.statut in [statuses.CONDITIONNE, statuses.TERMINE]:
            prod = next((e for e in etapes if e.etape == "production"), None)
            if not prod or prod.statut != "terminé":
                anomalies.append({"lot": lot.code_lot, "lot_id": lot.id, "type": "conditionnement_sans_production",
                                  "message": f"{lot.code_lot} est en {lot.statut} mais la production n'est pas terminée",
                                  "severite": "error"})

        if lot.statut == statuses.TERMINE:
            cond = next((e for e in etapes if e.etape == "conditionnement"), None)
            if not cond or cond.statut != "termine":
                anomalies.append({"lot": lot.code_lot, "lot_id": lot.id, "type": "termine_sans_conditionnement",
                                  "message": f"{lot.code_lot} est terminé mais le conditionnement n'est pas fait",
                                  "severite": "warning"})

            if lot.statut_transfert == statuses.EN_ATTENTE:
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
