# 2Saisons – Gestion de Stock & Production

Application de gestion de stock et traçabilité de production pour **2Saisons**, entreprise agroalimentaire spécialisée dans la transformation de fruits séchés (Bazré, Côte d'Ivoire).

## Processus de production

```
Réception → Musserie (Tri) → Production (Chariots → Dryers) → Conditionnement → Stock
```

## Démarrage

### Backend (FastAPI + PostgreSQL)

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

- API : http://localhost:8000
- Swagger : http://localhost:8000/docs

### Frontend (Vue 3 + Vite)

```bash
cd frontend-vue
npm install
npm run dev
```

- Application : http://localhost:8080

## Structure du projet

```
2saisons/
├── backend/
│   ├── main.py               # Point d'entrée FastAPI
│   ├── database.py           # Connexion PostgreSQL
│   ├── models.py             # Modèles ORM (10 tables)
│   ├── schemas.py            # Validation Pydantic
│   ├── crud.py               # Logique métier
│   ├── seed.py               # Données de démo
│   └── routers/
│       ├── lots.py           # CRUD lots
│       ├── production.py     # Musserie + Production (chariots)
│       ├── conditionnement.py # Conditionnement (4 flux)
│       ├── produits.py       # Catalogue produits
│       ├── commandes.py      # Commandes clients
│       ├── stock_zones.py    # Zones de stockage
│       ├── dashboard.py      # Statistiques
│       ├── mouvements.py     # Mouvements de stock
│       ├── rendements.py     # Rendements
│       └── stock_zones.py    # Gestion zones
├── frontend-vue/
│   ├── src/
│   │   ├── views/            # 10 pages
│   │   │   ├── Dashboard.vue
│   │   │   ├── Reception.vue
│   │   │   ├── Lots.vue
│   │   │   ├── Musserie.vue
│   │   │   ├── Production.vue
│   │   │   ├── Conditionnement.vue
│   │   │   ├── Stock.vue
│   │   │   ├── Produits.vue
│   │   │   ├── Fournisseurs.vue
│   │   │   └── Commandes.vue
│   │   ├── api/index.js      # Client API (axios)
│   │   ├── components/       # Composants réutilisables
│   │   ├── stores/toast.js   # Notifications
│   │   └── style.css         # Design system
│   └── vite.config.js        # Proxy /api → backend
└── README.md
```

## Modèles de données

| Table | Description |
|-------|-------------|
| `categories` | Catégories de produits |
| `fournisseurs` | Fournisseurs (nom libre) |
| `produits` | Catalogue produits |
| `lots` | Lots avec type_fruit, fournisseur_nom, poids, cartons |
| `etapes_production` | Étapes : musserie, production, conditionnement |
| `chariots` | Chariots (dryer, heures remplissage/entrée) |
| `mouvements_stock` | Entrées/sorties |
| `zones_stockage` | Zones froid/ambiant |
| `stocks_zone` | Contenu des zones |
| `commandes` / `lignes_commande` | Commandes clients |

## Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/lots/` | Liste des lots |
| POST | `/api/lots/` | Créer un lot (type_fruit + fournisseur_nom) |
| POST | `/api/production/musserie/{lot_id}` | Saisie journalière musserie (cumul) |
| POST | `/api/production/valider/{lot_id}` | Valider production (chariots → dryer) |
| POST | `/api/conditionnement/lots/{lot_id}` | Valider conditionnement (4 flux) |
| GET | `/api/dashboard/stats` | Statistiques |
| GET | `/api/produits/` | Catalogue produits |
| GET | `/api/commandes/` | Commandes clients |

## Stack technique

- **Backend** : Python, FastAPI, SQLAlchemy, PostgreSQL 18
- **Frontend** : Vue 3, Vite, Vue Router, Pinia, Axios
- **Design** : CSS vanilla, palette teal/vert, Plus Jakarta Sans

## Données de démo

Le seed inclut :
- 5 catégories, 9 produits, 3 fournisseurs
- 5 lots (Mangue Kent, Banane, Ananas...)
- 9 étapes de production
- 3 zones de stockage
- 4 mouvements de stock
