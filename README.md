# 2Saisons – Gestion de Stock & Production

Application de gestion de stock et traçabilité de production pour **2Saisons**, entreprise agroalimentaire spécialisée dans la transformation de fruits séchés (Bazré, Côte d'Ivoire).

## Processus de production (flux continu)

```
Réception → Musserie (Tri) → Production (Chariots → Dryers) → Conditionnement (5 flux) → Chambre froide → Stock → Commandes
```

Plusieurs lots peuvent être traités le même jour. Il n'y a **plus de clôture finale manuelle** : chaque saisie journalière passe toujours (lot épuisé ou non) et le lot bascule **seul** vers `conditionne` quand il est épuisé (reste ≤ 0, productions terminées, flux non vide).

## Règles métier

| Règle | Détail |
|-------|--------|
| Chiffres uniques | Reste, traité, sortie, perte : une seule formule côté backend, affichée partout pareil |
| Musserie | 1 saisie par (lot, dryer, jour) — la 2e écrase ; sortie = mûrs − retours − lavage − déchets (tri exclu, c'est un écart lot) |
| Production | Entrée = frais net musserie, sortie = pulpe chargée ; clôturer = valider la journée, le lot reste ouvert |
| Conditionnement | 5 flux (export, local, déchets, rhum, fitini fê) ; saisie par dryer J+1 sur poids sec ; « Valider la journée » ne ferme jamais le lot |
| Stock auto | Chaque saisie alimente la chambre froide (delta uniquement, idempotent) ; le transfert manuel ne peut renvoyer que le reste |
| Reconditionnement | Cartons local/fitini fê → sachets 100 g (+ rhum arrangé obtenu : cartons, sachets, vrac kg → stock Rhum arrangé) |
| Fournisseurs | Annuaire lecture seule regroupé depuis les réceptions (pas de formulaire) |

## Démarrage

### Backend (FastAPI + PostgreSQL / SQLite)

```bash
cd backend

# Créer la base PostgreSQL
psql -U postgres -c "CREATE DATABASE saisons_stock;"

# Configurer l'URL de la base
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/saisons_stock"

# Lancer le seed (données de démo)
python seed.py

# Lancer le serveur
python -m uvicorn main:app --reload
```

Sans `DATABASE_URL`, repli automatique sur SQLite (`saisons_stock.db`).

- API : http://localhost:8000
- Swagger : http://localhost:8000/docs

### Frontend (Vue 3 + Vite)

```bash
cd frontend-vue
npm install
npm run dev
```

- Application : http://localhost:8080

### Docker

```bash
docker compose up --build
```

## Tests

```bash
cd backend
python -m pytest tests -q
```

14 tests de règles métier (`tests/test_business_rules.py`) : quantités négatives rejetées, capacité zones, statuts canoniques, lot partiel (frais/pulpe/sec séparés), bascule auto lot épuisé, auto-stock sans doublon, reconditionnement rhum, rattrapage manuel.

## Structure du projet

```
2saisons/
├── backend/
│   ├── main.py               # Point d'entrée FastAPI (+ migrations légères)
│   ├── database.py           # Moteur SQLAlchemy + session
│   ├── config.py             # URL base (PostgreSQL / SQLite)
│   ├── models.py             # Modèles ORM (17 tables)
│   ├── schemas.py            # Validation Pydantic (rejet des négatifs)
│   ├── crud.py               # Logique métier
│   ├── statuses.py           # Statuts canoniques + workflow
│   ├── seed.py               # Données de démo
│   └── routers/
│       ├── lots.py           # CRUD lots
│       ├── production.py     # Musserie + Production (chariots, dryers)
│       ├── conditionnement.py # Conditionnement global + par dryer J+1
│       ├── transfert.py      # Transferts chambre froide + reconditionnement
│       ├── produits.py       # Catalogue produits
│       ├── commandes.py      # Commandes clients
│       ├── stock_zones.py    # Zones + contenu stock
│       ├── dashboard.py      # Statistiques
│       ├── mouvements.py     # Mouvements de stock
│       ├── rendements.py     # Rendements
│       └── search.py         # Recherche globale
├── frontend-vue/
│   ├── src/
│   │   ├── views/            # 15 pages
│   │   │   ├── Dashboard.vue
│   │   │   ├── Reception.vue
│   │   │   ├── Lots.vue
│   │   │   ├── Musserie.vue
│   │   │   ├── Production.vue
│   │   │   ├── ProductionChariots.vue
│   │   │   ├── Conditionnement.vue
│   │   │   ├── TransfertChambreFroid.vue
│   │   │   ├── Reconditionnement.vue
│   │   │   ├── Stock.vue
│   │   │   ├── Produits.vue
│   │   │   ├── Fournisseurs.vue
│   │   │   ├── Commandes.vue
│   │   │   ├── Anomalies.vue
│   │   │   └── Historique.vue
│   │   ├── api/index.js      # Client API (axios)
│   │   ├── components/       # Composants réutilisables
│   │   ├── stores/           # toast, theme
│   │   └── style.css         # Design system
│   └── vite.config.js        # Proxy /api → backend
└── README.md
```

## Modèles de données

| Table | Description |
|-------|-------------|
| `categories` | Catégories de produits |
| `fournisseurs` | Fournisseurs (référentiel, nom libre) |
| `produits` | Catalogue produits |
| `lots` | Lots : type_fruit, fournisseur_nom, poids, cartons (5 flux) |
| `etapes_production` | Étapes : musserie, production, conditionnement (+ poids sec) |
| `chariots` | Chariots par dryer (heures remplissage/entrée séchoir) |
| `mouvements_stock` | Entrées/sorties |
| `zones_stockage` | Zones froid/ambiant |
| `stocks_zone` | Contenu des zones (kg + sachets) |
| `conditionnement_entries` | Saisies par lot/dryer/jour (J+1) |
| `demandes_transfert` + `lignes_demande_transfert` | Transferts chambre froide (manuels + auto) |
| `reconditionnements` | Sachets 100g + rhum arrangé obtenu |
| `commandes` / `lignes_commande` | Commandes clients |
| `production_entries` / `company_settings` | Rendements + config dryers |

## Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET/POST | `/api/lots/` | Liste / créer un lot |
| POST | `/api/production/musserie/{lot_id}` | Saisie journalière musserie (1/jour/dryer) |
| POST | `/api/production/musserie/{lot_id}/cloturer?date=` | Clôturer la musserie du jour |
| POST | `/api/production/valider/{lot_id}` | Valider production (chariots → dryer) |
| POST | `/api/production/cloturer/{lot_id}?date=` | Valider la journée (lot reste ouvert) |
| POST | `/api/conditionnement/lots/{lot_id}` | Saisie conditionnement (5 flux, alimente le stock) |
| POST | `/api/conditionnement/lots/{lot_id}/dryer` | Saisie par dryer J+1 (poids sec) |
| POST | `/api/conditionnement/lots/{lot_id}/cloturer?date=` | Valider la journée (bascule auto si épuisé) |
| POST/GET | `/api/stock/demande-transfert` | Transferts manuels (reste uniquement) |
| POST | `/api/stock/reconditionnement` | Sachets 100g + rhum arrangé |
| GET | `/api/dashboard/stats` | Statistiques |
| GET | `/api/search/` | Recherche globale |

## Stack technique

- **Backend** : Python, FastAPI, SQLAlchemy, PostgreSQL (16 via Docker) / SQLite, pytest
- **Frontend** : Vue 3, Vite, Vue Router, Pinia, Axios
- **Design** : CSS vanilla, palette teal/vert

## Données de démo

Le seed inclut :
- 5 catégories, 11 produits, 3 fournisseurs
- 4 lots (1 en stock, 1 en production, 1 en musserie, 1 en réception)
- 2 chambres froides, stocks et mouvements d'exemple
