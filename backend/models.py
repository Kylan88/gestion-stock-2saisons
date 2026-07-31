from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class Categorie(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, unique=True)
    description = Column(Text, default="")
    couleur = Column(String(7), default="#a04100")
    produits = relationship("Produit", back_populates="categorie")

class Fournisseur(Base):
    __tablename__ = "fournisseurs"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False)
    contact = Column(String(100), default="")
    telephone = Column(String(50), default="")
    email = Column(String(100), default="")
    adresse = Column(Text, default="")
    actif = Column(Boolean, default=True)
    lots = relationship("Lot", back_populates="fournisseur")

class Produit(Base):
    __tablename__ = "produits"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False)
    categorie_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    unite_mesure = Column(String(20), default="kg")
    stock_min = Column(Float, default=0.0)
    stock_actuel = Column(Float, default=0.0)
    prix_unitaire = Column(Float, default=0.0)
    description = Column(Text, default="")
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.now)

    categorie = relationship("Categorie", back_populates="produits")
    mouvements = relationship("MouvementStock", back_populates="produit")
    lots = relationship("Lot", back_populates="produit")

class Lot(Base):
    __tablename__ = "lots"
    id = Column(Integer, primary_key=True, index=True)
    code_lot = Column(String(50), nullable=False, unique=True)
    type_fruit = Column(String(100), default="")
    fournisseur_nom = Column(String(200), default="")
    produit_id = Column(Integer, ForeignKey("produits.id"), nullable=True)
    fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"), nullable=True)
    statut = Column(String(20), default="réception")
    quantite_initiale = Column(Float, default=0.0)
    quantite_restante = Column(Float, default=0.0)
    poids_frais = Column(Float, default=0.0)
    poids_sec_final = Column(Float, default=0.0)
    rendement_global = Column(Float, nullable=True)
    # Conditionnement — cartons export
    export_cartons = Column(Integer, default=0)
    export_sachets = Column(Integer, default=0)
    export_poids_sachet = Column(Float, default=2.5)
    # Conditionnement — cartons local
    local_cartons = Column(Integer, default=0)
    local_sachets = Column(Integer, default=0)
    local_poids_sachet = Column(Float, default=2.5)
    # Conditionnement — cartons déchets
    dechets_cartons = Column(Integer, default=0)
    dechets_sachets = Column(Integer, default=0)
    dechets_poids_sachet = Column(Float, default=2.5)
    # Conditionnement — cartons rhum arrangé
    rhum_cartons = Column(Integer, default=0)
    rhum_sachets = Column(Integer, default=0)
    rhum_poids_sachet = Column(Float, default=2.5)
    # Conditionnement — fitini fê (produit fini vendable)
    fitini_fê_cartons = Column(Integer, default=0)
    fitini_fê_sachets = Column(Integer, default=0)
    fitini_fê_poids_sachet = Column(Float, default=2.5)
    # Stock transfert chambre froide
    statut_transfert = Column(String(20), default="en_attente")
    ecart_bilan_pourcentage = Column(Float, nullable=True)
    date_reception = Column(DateTime, default=datetime.now)
    date_fabrication = Column(DateTime, nullable=True)
    date_peremption = Column(DateTime, nullable=True)
    notes = Column(Text, default="")

    produit = relationship("Produit", back_populates="lots")
    fournisseur = relationship("Fournisseur", back_populates="lots")
    mouvements = relationship("MouvementStock", back_populates="lot")
    etapes = relationship("EtapeProduction", back_populates="lot", order_by="EtapeProduction.ordre")

class EtapeProduction(Base):
    __tablename__ = "etapes_production"
    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    etape = Column(String(50), nullable=False)
    ordre = Column(Integer, default=0)
    statut = Column(String(20), default="en_attente")
    date_debut = Column(DateTime, nullable=True)
    date_fin = Column(DateTime, nullable=True)
    poids_entree = Column(Float, default=0.0)
    poids_sortie = Column(Float, default=0.0)
    perte = Column(Float, default=0.0)
    rendement_pourcentage = Column(Float, nullable=True)
    operateur = Column(String(100), default="")
    notes = Column(Text, default="")
    # Musserie — détails de tri
    fruits_murs_kg = Column(Float, default=0.0)
    dechets_tri_kg = Column(Float, default=0.0)
    dechets_lavage_kg = Column(Float, default=0.0)
    retour_non_mur_kg = Column(Float, default=0.0)
    dechets_production_kg = Column(Float, default=0.0)
    # Production — chariots/dryer
    dryer = Column(Integer, nullable=True)
    nbre_chariots = Column(Integer, nullable=True)
    total_claies = Column(Integer, nullable=True)

    lot = relationship("Lot", back_populates="etapes")
    chariots = relationship("Chariot", back_populates="etape")

class Chariot(Base):
    __tablename__ = "chariots"
    id = Column(Integer, primary_key=True, index=True)
    etape_production_id = Column(Integer, ForeignKey("etapes_production.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    numero_chariot = Column(Integer, nullable=False)
    dryer = Column(Integer, nullable=False, default=1)
    nbre_chariots = Column(Integer, nullable=False, default=1)
    total_claies = Column(Integer, nullable=False, default=0)
    quantite_totale = Column(Float, default=0.0)
    operateur = Column(String(100), default="")
    heure_remplissage = Column(String(10), default="")
    heure_entree_sechoir = Column(String(10), default="")
    created_at = Column(DateTime, default=datetime.now)

    etape = relationship("EtapeProduction", back_populates="chariots")
    lot = relationship("Lot")

class MouvementStock(Base):
    __tablename__ = "mouvements_stock"
    id = Column(Integer, primary_key=True, index=True)
    produit_id = Column(Integer, ForeignKey("produits.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=True)
    type_mouvement = Column(String(20), nullable=False)
    quantite = Column(Float, nullable=False)
    quantite_avant = Column(Float, default=0.0)
    quantite_apres = Column(Float, default=0.0)
    motif = Column(Text, default="")
    reference_doc = Column(String(100), default="")
    responsable = Column(String(100), default="")
    date_mouvement = Column(DateTime, default=datetime.now)
    date_saisie = Column(DateTime, default=datetime.now)

    produit = relationship("Produit", back_populates="mouvements")
    lot = relationship("Lot", back_populates="mouvements")

class ZoneStockage(Base):
    __tablename__ = "zones_stockage"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    type_zone = Column(String(20), default="ambiant")
    usage = Column(String(20), nullable=True)
    temperature_consigne = Column(Float, nullable=True)
    capacite_kg = Column(Float, default=0.0)
    actif = Column(Boolean, default=True)
    stocks = relationship("StockZone", back_populates="zone")

class StockZone(Base):
    __tablename__ = "stocks_zone"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones_stockage.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=True)
    produit_id = Column(Integer, ForeignKey("produits.id"), nullable=False)
    quantite = Column(Float, default=0.0)
    sachets = Column(Integer, nullable=True)
    date_entree = Column(DateTime, default=datetime.now)
    date_sortie = Column(DateTime, nullable=True)

    zone = relationship("ZoneStockage", back_populates="stocks")
    lot = relationship("Lot")
    produit = relationship("Produit")

class Commande(Base):
    __tablename__ = "commandes"
    id = Column(Integer, primary_key=True, index=True)
    client_nom = Column(String(200), nullable=False)
    client_contact = Column(String(100), default="")
    date_commande = Column(DateTime, default=datetime.now)
    date_livraison_prevue = Column(DateTime, nullable=True)
    date_livraison_reelle = Column(DateTime, nullable=True)
    statut = Column(String(20), default="en_attente")
    notes = Column(Text, default="")
    total_ht = Column(Float, default=0.0)

    lignes = relationship("LigneCommande", back_populates="commande")

class LigneCommande(Base):
    __tablename__ = "lignes_commande"
    id = Column(Integer, primary_key=True, index=True)
    commande_id = Column(Integer, ForeignKey("commandes.id"), nullable=False)
    produit_id = Column(Integer, ForeignKey("produits.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=True)
    quantite = Column(Float, nullable=False)
    prix_unitaire = Column(Float, default=0.0)

    commande = relationship("Commande", back_populates="lignes")
    produit = relationship("Produit")
    lot = relationship("Lot")

# ── DEMANDE DE TRANSFERT CHAMBRE FROIDE ──

class DemandeTransfert(Base):
    __tablename__ = "demandes_transfert"
    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    date_demande = Column(DateTime, default=datetime.now)
    responsable = Column(String(100), default="")
    statut = Column(String(20), default="en_attente")
    notes = Column(Text, default="")

    lot = relationship("Lot")
    lignes = relationship("DemandeTransfertLigne", back_populates="demande")

class DemandeTransfertLigne(Base):
    __tablename__ = "lignes_demande_transfert"
    id = Column(Integer, primary_key=True, index=True)
    demande_id = Column(Integer, ForeignKey("demandes_transfert.id"), nullable=False)
    type_flux = Column(String(50), nullable=False)
    nb_cartons = Column(Integer, nullable=False)
    zone_id = Column(Integer, ForeignKey("zones_stockage.id"), nullable=False)
    statut = Column(String(20), default="en_attente")

    demande = relationship("DemandeTransfert", back_populates="lignes")
    zone = relationship("ZoneStockage")

# ── RECONDITIONNEMENT (sachets 100g) ──

class Reconditionnement(Base):
    __tablename__ = "reconditionnements"
    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    date_reconditionnement = Column(DateTime, default=datetime.now)
    type_source = Column(String(50), nullable=False)
    nb_cartons_entree = Column(Integer, nullable=False)
    nb_sachets_100g_sortie = Column(Integer, default=0)
    responsable = Column(String(100), default="")
    notes = Column(Text, default="")
    statut = Column(String(20), default="termine")

    lot = relationship("Lot")
