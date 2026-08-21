from datetime import datetime
from typing import ClassVar, Optional, List
from pydantic import BaseModel, Field, model_validator


class ValidatedInput(BaseModel):
    """Base schema preventing invalid negative quantities at the API boundary."""
    non_negative_fields: ClassVar[set[str]] = set()
    positive_fields: ClassVar[set[str]] = set()

    @model_validator(mode="after")
    def validate_numeric_ranges(self):
        for field in self.non_negative_fields:
            value = getattr(self, field, None)
            if value is not None and value < 0:
                raise ValueError(f"{field} must be greater than or equal to zero")
        for field in self.positive_fields:
            value = getattr(self, field, None)
            if value is not None and value <= 0:
                raise ValueError(f"{field} must be greater than zero")
        return self

class CategorieBase(BaseModel):
    nom: str; description: str = ""; couleur: str = "#a04100"
class CategorieCreate(CategorieBase): pass
class CategorieResponse(CategorieBase):
    id: int
    class Config: from_attributes = True

class FournisseurBase(BaseModel):
    nom: str; contact: str = ""; telephone: str = ""; email: str = ""
    adresse: str = ""; actif: bool = True
class FournisseurCreate(FournisseurBase): pass
class FournisseurResponse(FournisseurBase):
    id: int
    class Config: from_attributes = True

class ProduitBase(ValidatedInput):
    non_negative_fields = {"stock_min", "stock_actuel", "prix_unitaire"}
    nom: str; categorie_id: Optional[int] = None; unite_mesure: str = "kg"
    stock_min: float = 0.0; stock_actuel: float = 0.0; prix_unitaire: float = 0.0
    description: str = ""; actif: bool = True
class ProduitCreate(ProduitBase): pass
class ProduitUpdate(ValidatedInput):
    non_negative_fields = {"stock_min", "stock_actuel", "prix_unitaire"}
    nom: Optional[str] = None; categorie_id: Optional[int] = None
    unite_mesure: Optional[str] = None; stock_min: Optional[float] = None
    stock_actuel: Optional[float] = None; prix_unitaire: Optional[float] = None
    description: Optional[str] = None; actif: Optional[bool] = None
class ProduitResponse(ProduitBase):
    id: int; date_creation: datetime
    categorie: Optional[CategorieResponse] = None
    class Config: from_attributes = True

class LotBase(ValidatedInput):
    non_negative_fields = {
        "quantite_initiale", "quantite_restante", "poids_frais", "poids_sec_final", "rendement_global",
        "export_cartons", "export_sachets", "export_poids_sachet", "local_cartons", "local_sachets",
        "local_poids_sachet", "dechets_cartons", "dechets_sachets", "dechets_poids_sachet", "rhum_cartons",
        "rhum_sachets", "rhum_poids_sachet", "fitini_fê_cartons", "fitini_fê_sachets", "fitini_fê_poids_sachet",
    }
    code_lot: str; type_fruit: str = ""; fournisseur_nom: str = ""
    produit_id: Optional[int] = None; fournisseur_id: Optional[int] = None
    statut: str = "réception"; quantite_initiale: float = 0.0
    quantite_restante: float = 0.0; poids_frais: float = 0.0
    poids_sec_final: float = 0.0; rendement_global: Optional[float] = None
    export_cartons: int = 0; export_sachets: int = 0; export_poids_sachet: float = 2.5
    local_cartons: int = 0; local_sachets: int = 0; local_poids_sachet: float = 2.5
    dechets_cartons: int = 0; dechets_sachets: int = 0; dechets_poids_sachet: float = 2.5
    rhum_cartons: int = 0; rhum_sachets: int = 0; rhum_poids_sachet: float = 2.5
    fitini_fê_cartons: int = 0; fitini_fê_sachets: int = 0; fitini_fê_poids_sachet: float = 2.5
    statut_transfert: str = "en_attente"
    ecart_bilan_pourcentage: Optional[float] = None
    date_reception: datetime = Field(default_factory=datetime.now)
    date_fabrication: Optional[datetime] = None; date_peremption: Optional[datetime] = None
    notes: str = ""
class LotCreate(LotBase): pass
class EtapeResume(BaseModel):
    id: int; etape: str; ordre: int; statut: str
    date_debut: Optional[datetime] = None; date_fin: Optional[datetime] = None
    poids_entree: float = 0.0; poids_sortie: float = 0.0
    perte: float = 0.0; rendement_pourcentage: Optional[float] = None
    operateur: str = ""
    fruits_murs_kg: float = 0.0; dechets_tri_kg: float = 0.0
    dechets_lavage_kg: float = 0.0; retour_non_mur_kg: float = 0.0
    dechets_production_kg: float = 0.0
    class Config: from_attributes = True

class LotResponse(LotBase):
    id: int; produit: Optional[ProduitResponse] = None
    fournisseur: Optional[FournisseurResponse] = None
    etapes: List[EtapeResume] = []
    class Config: from_attributes = True

class EtapeProductionBase(ValidatedInput):
    non_negative_fields = {
        "poids_entree", "poids_sortie", "perte", "rendement_pourcentage", "fruits_murs_kg",
        "dechets_tri_kg", "dechets_lavage_kg", "retour_non_mur_kg", "dechets_production_kg",
    }
    lot_id: int; etape: str; ordre: int = 0; statut: str = "en_attente"
    date_debut: Optional[datetime] = None; date_fin: Optional[datetime] = None
    poids_entree: float = 0.0; poids_sortie: float = 0.0
    perte: float = 0.0; rendement_pourcentage: Optional[float] = None
    operateur: str = ""; notes: str = ""
    fruits_murs_kg: float = 0.0; dechets_tri_kg: float = 0.0
    dechets_lavage_kg: float = 0.0; retour_non_mur_kg: float = 0.0
    dechets_production_kg: float = 0.0
    dryer: Optional[int] = None
    nbre_chariots: Optional[int] = None
    total_claies: Optional[int] = None
class EtapeProductionCreate(EtapeProductionBase): pass
class EtapeProductionUpdate(ValidatedInput):
    non_negative_fields = {
        "poids_entree", "poids_sortie", "fruits_murs_kg", "dechets_tri_kg", "dechets_lavage_kg",
        "retour_non_mur_kg", "dechets_production_kg",
    }
    statut: Optional[str] = None; date_fin: Optional[datetime] = None
    poids_entree: Optional[float] = None
    poids_sortie: Optional[float] = None; operateur: Optional[str] = None
    notes: Optional[str] = None
    fruits_murs_kg: Optional[float] = None; dechets_tri_kg: Optional[float] = None
    dechets_lavage_kg: Optional[float] = None; retour_non_mur_kg: Optional[float] = None
    dechets_production_kg: Optional[float] = None
class EtapeProductionResponse(EtapeProductionBase):
    id: int
    class Config: from_attributes = True

class MusserieCreate(ValidatedInput):
    non_negative_fields = {
        "fruits_murs_kg", "dechets_tri_kg", "dechets_lavage_kg", "retour_non_mur_kg",
        "dechets_production_kg", "reste_kg",
    }
    fruits_murs_kg: float = 0.0
    dechets_tri_kg: float = 0.0
    dechets_lavage_kg: float = 0.0
    retour_non_mur_kg: float = 0.0
    dechets_production_kg: float = 0.0
    operateur: str = ""
    dryer: int = 0
    reste_kg: Optional[float] = None

class ConditionnementCreate(ValidatedInput):
    non_negative_fields = {
        "export_cartons", "export_sachets", "export_poids_sachet", "local_cartons", "local_sachets",
        "local_poids_sachet", "dechets_cartons", "dechets_sachets", "dechets_poids_sachet", "rhum_cartons",
        "rhum_sachets", "rhum_poids_sachet", "fitini_fê_cartons", "fitini_fê_sachets", "fitini_fê_poids_sachet",
    }
    export_cartons: int = 0
    export_sachets: int = 0
    export_poids_sachet: float = 2.5
    local_cartons: int = 0
    local_sachets: int = 0
    local_poids_sachet: float = 2.5
    dechets_cartons: int = 0
    dechets_sachets: int = 0
    dechets_poids_sachet: float = 2.5
    rhum_cartons: int = 0
    rhum_sachets: int = 0
    rhum_poids_sachet: float = 2.5
    fitini_fê_cartons: int = 0
    fitini_fê_sachets: int = 0
    fitini_fê_poids_sachet: float = 2.5
    responsable: str = ""
    notes: str = ""

class MouvementBase(ValidatedInput):
    positive_fields = {"quantite"}
    produit_id: int; lot_id: Optional[int] = None; type_mouvement: str
    quantite: float; motif: str = ""; reference_doc: str = ""; responsable: str = ""
class MouvementCreate(MouvementBase): pass
class MouvementResponse(MouvementBase):
    id: int; quantite_avant: float; quantite_apres: float; date_saisie: datetime
    produit: Optional[ProduitResponse] = None; lot: Optional[LotResponse] = None
    class Config: from_attributes = True

class ZoneStockageBase(ValidatedInput):
    non_negative_fields = {"capacite_kg"}
    nom: str; type_zone: str = "ambiant"; usage: Optional[str] = None
    temperature_consigne: Optional[float] = None
    capacite_kg: float = 0.0; actif: bool = True
class ZoneStockageCreate(ZoneStockageBase): pass
class ZoneStockageResponse(ZoneStockageBase):
    id: int
    class Config: from_attributes = True

class StockZoneBase(ValidatedInput):
    positive_fields = {"quantite"}
    non_negative_fields = {"sachets"}
    zone_id: int; lot_id: Optional[int] = None; produit_id: int; quantite: float = 0.0
    sachets: Optional[int] = None
class StockZoneCreate(StockZoneBase): pass
class StockZoneResponse(StockZoneBase):
    id: int; date_entree: datetime; date_sortie: Optional[datetime] = None
    zone: Optional[ZoneStockageResponse] = None; lot: Optional[LotResponse] = None
    produit: Optional[ProduitResponse] = None
    class Config: from_attributes = True

class LigneCommandeBase(ValidatedInput):
    positive_fields = {"quantite"}
    non_negative_fields = {"prix_unitaire"}
    produit_id: int; lot_id: Optional[int] = None; quantite: float; prix_unitaire: float = 0.0
class CommandeBase(BaseModel):
    client_nom: str; client_contact: str = ""; date_livraison_prevue: Optional[datetime] = None
    notes: str = ""; statut: str = "en_attente"
class CommandeCreate(CommandeBase): lignes: List[LigneCommandeBase]
class LigneCommandeResponse(LigneCommandeBase):
    id: int; produit: Optional[ProduitResponse] = None; lot: Optional[LotResponse] = None
    class Config: from_attributes = True

class CommandeResponse(CommandeBase):
    id: int; date_commande: datetime; total_ht: float; lignes: List[LigneCommandeResponse] = []
    class Config: from_attributes = True

class ChariotCreate(ValidatedInput):
    positive_fields = {"numero_chariot"}
    numero_chariot: int
    heure_remplissage: str = ""
    heure_entree_sechoir: str = ""

class ChariotResponse(BaseModel):
    id: int; etape_production_id: int; lot_id: int
    numero_chariot: int; dryer: int; nbre_chariots: int; total_claies: int
    quantite_totale: float; operateur: str
    heure_remplissage: str; heure_entree_sechoir: str
    created_at: Optional[datetime] = None
    class Config: from_attributes = True

class ProductionCreate(ValidatedInput):
    positive_fields = {"dryer", "nbre_chariots", "quantite_totale"}
    dryer: int
    nbre_chariots: int
    quantite_totale: float
    operateur: str = ""
    chariots: List[ChariotCreate] = []

class DashboardStats(BaseModel):
    total_produits: int; total_mouvements: int; total_lots_actifs: int
    produits_stock_bas: int; produits_rupture: int; valeur_stock: float
    commandes_en_attente: int; lots_en_production: int; lots_en_stock: int
    rendement_moyen: Optional[float] = None; stock_froid_kg: float = 0.0

class DashboardProduction(BaseModel):
    lots_suivi: int; etapes_terminees: int; etapes_en_cours: int
    rendement_moyen_frais_sec: Optional[float] = None
    production_jour_kg: float = 0.0
    musserie_jour_kg: float = 0.0
    conditionnement_jour_kg: float = 0.0

# ── DEMANDE DE TRANSFERT CHAMBRE FROIDE ──

class DemandeTransfertLigneCreate(ValidatedInput):
    positive_fields = {"nb_cartons"}
    type_flux: str
    nb_cartons: int
    zone_id: int

class DemandeTransfertCreate(BaseModel):
    lot_id: int
    responsable: str = ""
    notes: str = ""
    lignes: List[DemandeTransfertLigneCreate]

class DemandeTransfertLigneResponse(BaseModel):
    id: int; type_flux: str; nb_cartons: int; zone_id: int; statut: str
    zone: Optional[ZoneStockageResponse] = None
    class Config: from_attributes = True

class DemandeTransfertResponse(BaseModel):
    id: int; lot_id: int; date_demande: datetime; responsable: str
    statut: str; notes: str
    lignes: List[DemandeTransfertLigneResponse] = []
    lot: Optional[LotResponse] = None
    class Config: from_attributes = True

# ── RECONDITIONNEMENT (sachets 100g) ──

class ReconditionnementCreate(ValidatedInput):
    positive_fields = {"nb_cartons_entree"}
    lot_id: int
    type_source: str
    nb_cartons_entree: int
    responsable: str = ""
    notes: str = ""

class ReconditionnementResponse(BaseModel):
    id: int; lot_id: int; date_reconditionnement: datetime
    type_source: str; nb_cartons_entree: int; nb_sachets_100g_sortie: int
    responsable: str; notes: str; statut: str
    class Config: from_attributes = True


# ── PRODUCTION / RENDEMENT (Entrées journalières) ──

class CompanySettingsBase(BaseModel):
    dryer_capacity_kg: float = 1500.0
    fruit_types: List[str] = ["mangue", "ananas", "goyave"]

class CompanySettingsUpdate(BaseModel):
    dryer_capacity_kg: Optional[float] = None
    fruit_types: Optional[List[str]] = None

class CompanySettingsResponse(CompanySettingsBase):
    class Config: from_attributes = True


class ProductionEntryCreate(ValidatedInput):
    positive_fields = {"poids_frais_kg", "nb_dryers"}
    date: datetime
    fruit_type: str
    poids_frais_kg: float
    nb_dryers: int = 1
    notes: str = ""
    saison_id: Optional[int] = None

class ProductionEntryResponse(BaseModel):
    id: int
    date: datetime
    fruit_type: str
    poids_frais_kg: float
    nb_dryers: int
    notes: str
    saison_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    # Champs calculés
    pulpe_obtenue_kg: float
    rendement: float
    class Config: from_attributes = True


class ProductionStats(BaseModel):
    total_kg_frais: float
    total_dryers: int
    rendement_moyen: float
    par_fruit: dict
