# 2Saisons – Gestion de Stock & Production

Application de gestion de stock et traçabilité de production pour **2Saisons**, entreprise agroalimentaire spécialisée dans la transformation de fruits séchés (Bazré, Côte d'Ivoire).

## Processus de production (flux continu)

```
Réception → Murisserie (Tri) → Production (Chariots → Dryers) → Conditionnement (5 flux) → Chambre froide → Stock → Commandes
```

Plusieurs lots peuvent être traités le même jour. Il n'y a **plus de clôture finale manuelle** : chaque saisie journalière passe toujours (lot épuisé ou non) et le lot bascule **seul** vers `conditionne` quand il est épuisé (reste ≤ 0, productions terminées, flux non vide).

## Règles métier

| Règle | Détail |
|-------|--------|
| Chiffres uniques | Reste, traité, sortie, perte : une seule formule côté backend, affichée partout pareil |
| Murisserie | 1 saisie par (lot, dryer, jour) — la 2e écrase ; sortie = mûrs − retours − lavage − déchets (tri exclu, c'est un écart lot) |
| Production | Entrée = frais net murisserie, sortie = pulpe chargée ; clôturer = valider la journée, le lot reste ouvert |
| Conditionnement | 5 flux (export, local, déchets, rhum, fitini fê) ; saisie par dryer J+1 sur poids sec ; « Valider la journée » ne ferme jamais le lot |
| Transfert manuel | Seule la validation d'une demande de transfert met la chambre froide en stock (plus d'auto-stock) ; on ne peut demander que le reste (conditionné − déjà transféré) |
| Reconditionnement | Cartons local/fitini fê → sachets 100 g (+ rhum arrangé obtenu : cartons, sachets, vrac kg → stock Rhum arrangé) ; déduit le produit source (kg + cartons) |
| Produits | `stock_actuel` en kg (sachets 100g convertis × 0,1 au total), `cartons` dédiés, `stock_min` = seuil d'alerte uniquement |
| Fournisseurs | Annuaire lecture seule regroupé depuis les réceptions (pas de formulaire) |
| Excel | Les 17 vrais tableaux s'exportent en `.xlsx` (thème navy, filtres, volets gelés) ; plus de CSV |

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
docker compose up --build -d
```

- API : http://localhost:8000 (Swagger : `/docs`)
- Frontend : http://localhost:8080 (proxy `/api` → API)
- PostgreSQL 16 interne (volume `pgdata`) ; le seed tourne au démarrage de l'API

## Tests

```bash
cd backend
python -m pytest tests -q
```

15 tests de règles métier (`tests/test_business_rules.py`) : quantités négatives rejetées, capacité zones, statuts canoniques, lot partiel (frais/pulpe/sec séparés), bascule auto lot épuisé, saisie sans auto-stock + transfert manuel requis, reconditionnement rhum, murisserie 1/jour/dryer.

```bash
cd frontend-vue
npm test -- --run   # 3 tests vitest (export Excel : normalisation + classeur stylé)
```

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
│       ├── production.py     # Murisserie + Production (chariots, dryers)
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
│   │   │   ├── Murisserie.vue
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
│   │   ├── api/index.js      # Client API (axios, base `/api`)
│   │   ├── components/       # Composants réutilisables (dont ConfirmDialog)
│   │   ├── utils/exportExcel.js # Export .xlsx (exceljs, thème navy)
│   │   ├── tests/exportExcel.test.js
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
| `produits` | Catalogue (stock kg, `cartons` dédiés, `stock_min` = seuil) |
| `lots` | Lots : type_fruit, fournisseur_nom, poids, cartons (5 flux) |
| `etapes_production` | Étapes : murisserie, production, conditionnement (+ poids sec) |
| `chariots` | Chariots par dryer (heures remplissage/entrée dryer) |
| `mouvements_stock` | Entrées/sorties |
| `zones_stockage` | Zones froid/ambiant |
| `stocks_zone` | Contenu des zones (kg + sachets) |
| `conditionnement_entries` | Saisies par lot/dryer/jour (J+1) |
| `demandes_transfert` + `lignes_demande_transfert` | Transferts chambre froide manuels |
| `reconditionnements` | Sachets 100g + rhum arrangé obtenu |
| `commandes` / `lignes_commande` | Commandes clients |
| `production_entries` / `company_settings` | Rendements + config dryers |

## Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET/POST | `/api/lots/` | Liste / créer un lot |
| POST | `/api/production/murisserie/{lot_id}` | Saisie journalière murisserie (1/jour/dryer) |
| POST | `/api/production/murisserie/{lot_id}/cloturer?date=` | Clôturer la murisserie du jour |
| POST | `/api/production/valider/{lot_id}` | Valider production (chariots → dryer) |
| POST | `/api/production/cloturer/{lot_id}?date=` | Valider la journée (lot reste ouvert) |
| POST | `/api/conditionnement/lots/{lot_id}` | Saisie conditionnement (5 flux, cumul lot) |
| POST | `/api/conditionnement/lots/{lot_id}/dryer` | Saisie par dryer J+1 (poids sec) |
| POST | `/api/conditionnement/lots/{lot_id}/cloturer?date=` | Valider la journée (bascule auto si épuisé) |
| POST/GET | `/api/stock/demande-transfert` | Transferts manuels (demande + validation = stock) |
| POST | `/api/stock/reconditionnement` | Sachets 100g + rhum arrangé |
| GET | `/api/dashboard/stats` | Statistiques |
| GET | `/api/search/` | Recherche globale |

## Stack technique

- **Backend** : Python, FastAPI, SQLAlchemy, PostgreSQL (16 via Docker) / SQLite, pytest
- **Frontend** : Vue 3, Vite, Vue Router, Pinia, Axios, ExcelJS, Vitest
- **Design** : CSS vanilla, palette teal/vert

## Données de démo

Le seed rejoue des saisies réelles de test (valeurs exactes) avec dates re-ancrées
(le jour le plus récent devient aujourd'hui, écarts préservés pour les chaînes J+1) :
2 lots en murisserie, 78 chariots, stocks zone, transferts, reconditionnements.
Ne s'applique qu'aux bases vierges.
