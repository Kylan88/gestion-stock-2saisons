# 2Saisons – API REST + Frontend

Gestion de stock et traçabilité de production pour **2Saisons**, entreprise agroalimentaire spécialisée dans la transformation de fruits séchés (Bazré, Côte d'Ivoire).

## Processus de production couvert

```
Réception → Musserie (Tri & Lavage) → Production (Mise en claies)
 → Séchage (Dryers) → Conditionnement → Stock & Expédition
```

Chaque lot est tracé à travers les 4 étapes avec poids entrants/sortants, rendement, opérateur.

## 🚀 Démarrage rapide (sans Docker)

```bash
cd 2saisons
python start.py
```

- 🌐 Frontend : http://localhost:8080
- 📘 API Swagger : http://localhost:8000/docs
- 🔍 Health : http://localhost:8000/health

## 🐳 Démarrage avec Docker

```bash
docker compose up -d
```

## 🗂️ Structure du projet

```
2saisons/
├── backend/                  # API FastAPI
│   ├── main.py               # Point d'entrée
│   ├── config.py             # Configuration DB
│   ├── database.py           # SQLAlchemy engine
│   ├── models.py             # Modèles ORM (11 tables)
│   ├── schemas.py            # Pydantic schemas
│   ├── crud.py               # Logique métier
│   ├── seed.py               # Données de démo
│   ├── routers/
│   │   ├── produits.py       # /api/produits
│   │   ├── mouvements.py     # /api/mouvements
│   │   ├── lots.py           # /api/lots
│   │   ├── commandes.py      # /api/commandes
│   │   ├── dashboard.py      # /api/dashboard
│   │   ├── production.py     # /api/production
│   │   ├── sechoirs.py       # /api/sechoirs
│   │   ├── stock_zones.py    # /api/stock/zones
│   │   ├── rendements.py     # /api/rendements
│   │   ├── claies.py         # /api/claies
│   │   └── conditionnement.py # /api/conditionnement
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Interface NiceGUI
│   ├── main.py               # App standalone
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml        # PostgreSQL + API + Frontend
├── start.py                  # Lancement local
├── .env                      # Configuration
└── README.md
```

## 🔌 API Endpoints

### Produits
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/produits/` | Liste des produits (filtres: actif, recherche, categorie_id) |
| GET | `/api/produits/{id}` | Détail produit |
| POST | `/api/produits/` | Créer un produit |
| PUT | `/api/produits/{id}` | Modifier un produit |
| DELETE | `/api/produits/{id}` | Désactiver un produit |
| GET | `/api/produits/alertes/stock-bas` | Produits sous seuil minimum |
| GET | `/api/produits/alertes/rupture` | Produits en rupture |

### Mouvements de Stock
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/mouvements/` | Historique (filtres: produit_id, type, date_debut, date_fin) |
| POST | `/api/mouvements/entree` | Entrée de stock |
| POST | `/api/mouvements/sortie` | Sortie de stock |
| GET | `/api/mouvements/types/liste` | Types de mouvements possibles |

### Lots & Traçabilité
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/lots/` | Liste des lots (filtres: statut, recherche, produit_id) |
| GET | `/api/lots/{id}` | Détail lot avec étapes |
| POST | `/api/lots/` | Créer un lot (génère 4 étapes automatiquement) |
| PUT | `/api/lots/{id}/statut` | Changer le statut d'un lot |
| GET | `/api/lots/statuts/liste` | Statuts possibles |

### Production (Étapes)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/production/etapes?lot_id=X` | Étapes d'un lot |
| GET | `/api/production/etapes/{id}` | Détail d'une étape |
| POST | `/api/production/etapes/{id}/demarrer` | Démarrer une étape |
| PUT | `/api/production/etapes/{id}/terminer` | Terminer avec poids sortie |
| PUT | `/api/production/etapes/{id}` | Mise à jour partielle |
| GET | `/api/production/lots/{id}/parcours` | Traçabilité complète |

### Séchoirs & Sessions de Séchage
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/sechoirs/` | Liste des séchoirs |
| POST | `/api/sechoirs/` | Ajouter un séchoir |
| PUT | `/api/sechoirs/{id}` | Modifier un séchoir |
| GET | `/api/sechoirs/{id}/sessions` | Sessions d'un séchoir |
| GET | `/api/sechoirs/sessions/` | Toutes les sessions |
| POST | `/api/sechoirs/sessions/` | Créer/démarrer une session |
| PUT | `/api/sechoirs/sessions/{id}/terminer` | Terminer avec mesures |

### Claies (découpe & séchage par dryer)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/claies/lot/{lot_id}` | Claies d'un lot |
| GET | `/api/claies/lot/{lot_id}/total` | Total chargé/sorti + alerte perte à la découpe |
| GET | `/api/claies/sechoir/{sechoir_id}` | Claies chargées dans un séchoir |
| POST | `/api/claies/` | Charger une nouvelle claie (code CL-NNN auto) |
| PUT | `/api/claies/{id}/sortir` | Sortir une claie (poids, qualité visuelle) |

### Conditionnement
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/conditionnement/lots/{lot_id}` | Valide le conditionnement : répartition export/local/déchets, vérifie le bilan matière (alerte si écart > 2%), calcule le rendement global, alimente les 2 chambres froides |

### Stock & Zones
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/stock/zones` | Zones de stockage (froid, ambiant) |
| POST | `/api/stock/zones` | Ajouter une zone |
| GET | `/api/stock/zones/{id}/contenu` | Contenu d'une zone |
| GET | `/api/stock/stock` | Stocks en zone (filtres: zone_id, produit_id) |
| POST | `/api/stock/stocker` | Entrer en zone |
| POST | `/api/stock/sortir/{id}` | Sortir de zone |

### Commandes
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/commandes/` | Liste des commandes (filtres: statut, recherche) |
| GET | `/api/commandes/{id}` | Détail commande |
| POST | `/api/commandes/` | Créer commande |
| PUT | `/api/commandes/{id}/statut` | Changer statut |

### Dashboard
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/dashboard/stats` | Statistiques globales (stock + production) |
| GET | `/api/dashboard/production` | KPIs production |
| GET | `/api/dashboard/stock-bas` | Alertes stock bas |
| GET | `/api/dashboard/derniers-mouvements` | 10 derniers mouvements |

### Rendements
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/rendements/lots/{id}` | Détail rendement d'un lot |
| GET | `/api/rendements/moyen` | Rendement moyen global |
| GET | `/api/rendements/lots` | Synthèse tous lots |

### Référentiels
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/categories` | Catégories de produits |
| POST | `/api/categories` | Ajouter une catégorie |
| GET | `/api/fournisseurs` | Fournisseurs |
| POST | `/api/fournisseurs` | Ajouter un fournisseur |

## 🗄️ Modèles de données (12 tables)

- `categories` — Catégories de produits
- `fournisseurs` — Fournisseurs de matières premières
- `produits` — Produits finis et semi-finis
- `lots` — Lots avec traçabilité complète (dont conditionnement: export/local/déchets, bilan matière)
- `etapes_production` — Suivi des 4 étapes par lot
- `sechoirs` — Équipements de séchage
- `claies` — Grilles de fruits découpées, assignées à un dryer (Module 3-4)
- `sessions_sechage` — Sessions de séchage (température, durée, rendement)
- `mouvements_stock` — Entrées/sorties/ajustements
- `zones_stockage` — Zones de stockage (froid local, froid export, ambiant)
- `stocks_zone` — Produits stockés en zone (avec compteur sachets pour le local)
- `commandes` / `lignes_commande` — Commandes clients
