# 2Saisons — Frontend (Vue 3 + Vite)

Application de gestion de stock & production (Bazré, Côte d'Ivoire).
Voir le [README racine](../README.md) pour les règles métier et l'API.

## Commandes

```bash
npm install
npm run dev      # http://localhost:8080 (proxy /api → http://localhost:8000)
npm run build    # build production (image Docker nginx)
npm run preview  # prévisualiser le build
npm test -- --run  # tests vitest
```

## Pages (routes)

| Route | Page |
|-------|------|
| `/` | Dashboard |
| `/reception` | Réception (création lots) |
| `/lots` | Lots (+ poids total reçu, rendement) |
| `/murisserie` | Murisserie (saisie du jour + historique) |
| `/production` | Rendements par dryer/fruit/lot |
| `/production/chariots` | Chariots (dryers guidés, reste à charger, récapitulatif) |
| `/conditionnement` | Conditionnement J+1 + historique |
| `/stock/transfert` | Transferts chambre froide (manuel) |
| `/stock` | Stock par zone |
| `/stock/reconditionnement` | Sachets 100g + rhum arrangé |
| `/produits` | Catalogue (stock kg, cartons) |
| `/fournisseurs` | Annuaire (depuis réceptions) |
| `/commandes` | Commandes clients |
| `/anomalies` | Anomalies + rappels |
| `/historique` | Historique global (5 onglets) |

## Export Excel

Les 17 vrais tableaux s'exportent en `.xlsx` via `src/utils/exportExcel.js`
(ExcelJS : thème navy, filtres auto, volets gelés, largeurs auto).
Pages multi-tableaux (Réception, Production, Historique) → un onglet par tableau.

## Conventions d'affichage

- Poids : 2 décimales max (`maximumFractionDigits: 2`), entiers sans zéros parasites.
- Dates jour : comparées en local (`todayLocal`), jamais en UTC.
