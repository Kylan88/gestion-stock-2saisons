import sys, os, httpx
from nicegui import ui
from contextlib import contextmanager
from datetime import datetime

API_URL = os.getenv("API_URL", "http://localhost:8000")
API = f"{API_URL}/api"

client = httpx.Client(base_url=API, timeout=15.0)
def api_get(path): r = client.get(path); r.raise_for_status(); return r.json()
def api_post(path, data): r = client.post(path, json=data); r.raise_for_status(); return r.json()
def api_put(path, data): r = client.put(path, json=data); r.raise_for_status(); return r.json()

ui.add_head_html("""
<style>
:root { --primary: #a04100; --secondary: #3f6653; --tertiary: #116c4a; --error: #ba1a1a; --surface: #f4fafd; }
body { font-family: 'Inter', sans-serif; background: var(--surface); }
.q-header { background: var(--secondary) !important; }
.dc { background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0c0b2; }
.sv { font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 600; color: var(--primary); }
.sl { font-size: 13px; color: #584237; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
.frm { min-width: 600px; }
</style>""", shared=True)

NAV = [
    ("/","Dashboard"),("/lots","Lots"),("/reception","Réception"),("/musserie","Musserie"),
    ("/claies","Claies"),("/sechage","Séchage"),("/conditionnement","Conditionnement"),
    ("/commandes","Commandes"),("/produits","Produits"),("/fournisseurs","Fournisseurs"),("/stock","Stock")
]

@contextmanager
def layout():
    with ui.header(elevated=True).classes("items-center justify-between"):
        ui.label("2Saisons").classes("text-h6 text-white q-ml-md")
        with ui.row().classes("gap-1"):
            for p, l in NAV:
                ui.link(l, p).classes("text-white q-px-sm")
    with ui.column().classes("w-full q-pa-lg"): yield

def refresh():
    ui.open(ui.context.client.page.path)

# ── DASHBOARD ──
@ui.page("/")
def page_dashboard():
    with layout():
        ui.label("Tableau de Bord").classes("text-h4 q-mb-md")
        try:
            s = api_get("/dashboard/stats")
            p = api_get("/dashboard/production")
            with ui.grid(columns=4).classes("w-full q-mb-lg gap-4"):
                for lbl, key, fmt in [
                    ("Produits", s["total_produits"], None), ("Stock Bas", s["produits_stock_bas"], None),
                    ("Lots Actifs", s["total_lots_actifs"], None), ("Valeur Stock", s["valeur_stock"], "FCFA"),
                    ("Lots en Prod.", s["lots_en_production"], None), ("Séchage", s["sessions_sechage_en_cours"], None),
                    ("Rendement Moyen", f"{s['rendement_moyen'] or '-'}", "%"), ("Stock Froid", s["stock_froid_kg"], "kg")]:
                    v = f"{key:,.0f} {fmt}" if fmt and isinstance(key,(int,float)) else str(key)
                    with ui.card().classes("dc"):
                        ui.label(v).classes("sv"); ui.label(lbl).classes("sl")
            with ui.grid(columns=3).classes("w-full gap-4"):
                for lbl, val in [("Étapes Terminées",p["etapes_terminees"]),("En Cours",p["etapes_en_cours"]),
                    ("Séchoirs Occupés",p["sechoirs_occupes"]),("Disponibles",p["sechoirs_disponibles"]),
                   ("Production Aujourd'hui",f"{p['production_jour_kg']:.0f} kg"),("Lots Suivis",p["lots_suivi"])]:
                    with ui.card().classes("dc"):
                        ui.label(str(val)).classes("sv"); ui.label(lbl).classes("sl")
            stocks = api_get("/dashboard/stock-bas")
            if stocks:
                with ui.card().classes("dc q-mt-md"):
                    ui.label("Alertes Stock").classes("text-h6")
                    for pr in stocks[:5]:
                        st = "RUPTURE" if pr["stock_actuel"]<=0 else "BAS"
                        ui.label(f"  {pr['nom']}: {pr['stock_actuel']:.0f} / {pr['stock_min']:.0f} ({st})")
        except Exception as e:
            ui.label(f"API: {e}").classes("text-negative")

# ── LOTS (vue d'ensemble) ──
@ui.page("/lots")
def page_lots():
    with layout():
        ui.label("Tous les Lots").classes("text-h4 q-mb-md")
        try:
            for l in api_get("/lots/"):
                with ui.card().classes("dc w-full q-mb-sm"):
                    with ui.row().classes("items-center justify-between"):
                        ui.label(l['code_lot']).classes("text-h6")
                        ui.chip(l['statut'], selectable=False).props(
                            f"color={'positive' if l['statut'] in ('en stock','terminé') else 'warning' if 'séchage' in l['statut'] else 'primary'}")
                    pn = l["produit"]["nom"] if l.get("produit") else "-"
                    fn = l["fournisseur"]["nom"] if l.get("fournisseur") else "-"
                    r = f" | Rendement: {l['rendement_global']}%" if l.get("rendement_global") else ""
                    ui.label(f"{pn} | {fn} | {l['quantite_initiale']:.0f} kg → {l['quantite_restante']:.0f} kg{r}").classes("text-body2")
                    # Mini barre des étapes
                    etapes = l.get("etapes", [])
                    if etapes:
                        with ui.row().classes("gap-2 items-center q-mt-xs"):
                            for e in etapes:
                                cls = {"terminé":"✅","en_cours":"⏳","en_attente":"⬜"}
                                ui.label(f"{cls.get(e['statut'],'⬜')} {e['etape']}").classes("text-body2")
        except Exception as e: ui.label(f"Erreur: {e}").classes("text-negative")

# ── RÉCEPTION ──
@ui.page("/reception")
def page_reception():
    with layout():
        ui.label("Réception — Créer un Lot").classes("text-h4 q-mb-md")
        try:
            prods = {p["id"]:p["nom"] for p in api_get("/produits/")}
            fours = {f["id"]:f["nom"] for f in api_get("/fournisseurs/")}
            with ui.card().classes("dc frm"):
                with ui.row().classes("gap-4"):
                    p = ui.select(prods, label="Produit", with_input=True).classes("w-64")
                    f = ui.select(fours, label="Fournisseur", with_input=True).classes("w-64")
                with ui.row().classes("gap-4"):
                    q = ui.number("Quantité (kg)", min=0.1, value=100).classes("w-32")
                    pf = ui.number("Poids frais (kg)", min=0.1, value=100).classes("w-32")
                notes = ui.input("Notes").classes("w-full")
                code = f"LOT-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
                ui.label(f"Code lot généré : {code}").classes("text-grey")
                def save():
                    try:
                        api_post("/lots/", {"code_lot":code,"produit_id":p.value,"fournisseur_id":f.value,
                                            "quantite_initiale":q.value,"poids_frais":pf.value,
                                            "quantite_restante":q.value,"notes":notes.value or ""})
                        ui.notify("Lot créé !", type="positive"); refresh()
                    except Exception as e: ui.notify(f"Erreur: {e}", type="negative")
                ui.button("Valider la Réception", on_click=save).props("color=primary")
            # Liste des lots en réception
            lots = api_get("/lots/?statut=réception")
            if lots:
                ui.label("Lots en attente").classes("text-h6 q-mt-md")
                for l in lots:
                    with ui.card().classes("dc w-full q-mb-xs"):
                        pn = l["produit"]["nom"] if l.get("produit") else "-"
                        ui.label(f"{l['code_lot']} — {pn} — {l['quantite_initiale']:.0f} kg").classes("text-body2")
        except Exception as e: ui.label(f"Erreur: {e}").classes("text-negative")

# ── MUSSERIE ──
@ui.page("/musserie")
def page_musserie():
    with layout():
        ui.label("Musserie — Tri & Lavage").classes("text-h4 q-mb-md")
        try:
            lots_rec = {l["id"]:f"{l['code_lot']} ({l.get('produit',{}).get('nom','?')})" for l in api_get("/lots/") if l["statut"]=="réception"}
            lots_prod = {l["id"]:f"{l['code_lot']} ({l.get('produit',{}).get('nom','?')})" for l in api_get("/lots/") if l["statut"]=="en musserie"}
            if lots_rec:
                ui.label("Démarrer la musserie").classes("text-h6")
                with ui.card().classes("dc frm q-mb-md"):
                    lot = ui.select(lots_rec, label="Lot", with_input=True).classes("w-64")
                    op = ui.input("Opérateur", value="Opérateur").classes("w-48")
                    ui.button("Démarrer", on_click=lambda: (
                        api_put(f"/lots/{lot.value}/statut", {"statut":"en musserie"}),
                        api_post(f"/production/etapes/{api_get(f'/production/etapes?lot_id={lot.value}')[0]['id']}/demarrer", {"operateur":op.value}),
                        ui.notify("Musserie démarrée", type="positive"), refresh()
                    )).props("color=primary")
            if lots_prod:
                ui.label("Terminer la musserie").classes("text-h6 q-mt-md")
                with ui.card().classes("dc frm"):
                    lot = ui.select(lots_prod, label="Lot", with_input=True).classes("w-64")
                    ps = ui.number("Poids sortie (kg net trié)", min=0.1, value=0).classes("w-48")
                    op = ui.input("Opérateur", value="Opérateur").classes("w-48")
                    def terminer():
                        lid = lot.value
                        etapes = api_get(f"/production/etapes?lot_id={lid}")
                        ep = [e for e in etapes if e["etape"]=="musserie"][0]
                        api_put(f"/production/etapes/{ep['id']}/terminer", {"poids_sortie":ps.value,"operateur":op.value})
                        api_put(f"/lots/{lid}/statut", {"statut":"en production"})
                        ui.notify("Musserie terminée", type="positive"); refresh()
                    ui.button("Terminer", on_click=terminer).props("color=warning")
        except Exception as e: ui.label(f"Erreur: {e}").classes("text-negative")

# ── CLAIES ──
@ui.page("/claies")
def page_claies():
    with layout():
        ui.label("Claies — Chargement / Déchargement").classes("text-h4 q-mb-md")
        try:
            lots_prod = {l["id"]:f"{l['code_lot']}" for l in api_get("/lots/") if l["statut"]=="en production"}
            sechoirs = {s["id"]:f"{s['nom']} ({s['capacite_kg']:.0f}kg)" for s in api_get("/sechoirs/") if s["statut"]=="disponible"}
            if lots_prod and sechoirs:
                ui.label("Charger une claie dans un dryer").classes("text-h6")
                with ui.card().classes("dc frm q-mb-md"):
                    with ui.row().classes("gap-4"):
                        lot = ui.select(lots_prod, label="Lot", with_input=True).classes("w-48")
                        sech = ui.select(sechoirs, label="Séchoir", with_input=True).classes("w-64")
                    with ui.row().classes("gap-4"):
                        pc = ui.number("Poids chargé (kg)", min=0.1, value=8.0).classes("w-32")
                        op = ui.input("Responsable", value="Opérateur").classes("w-48")
                    def charger():
                        c = api_post("/claies/", {"lot_id":lot.value,"sechoir_id":sech.value,"poids_charge":pc.value,"responsable_chargement":op.value})
                        ui.notify(f"Claie {c['code_claie']} chargée", type="positive"); refresh()
                    ui.button("Charger", on_click=charger).props("color=primary")
            # Claies en séchage
            claies_sech = api_get("/claies/lot/4")  # on listera toutes via un meilleur endpoint
            # Lister les claies en cours par séchoir
            ui.label("Claies en séchage").classes("text-h6 q-mt-md")
            for s in api_get("/sechoirs/"):
                cl = api_get(f"/claies/sechoir/{s['id']}")
                if cl:
                    with ui.card().classes("dc w-full q-mb-xs"):
                        ui.label(f"{s['nom']} — {len(cl)} claie(s)").classes("text-bold")
                        for c in cl:
                            ln = c["lot"]["code_lot"] if c.get("lot") else "?"
                            ui.label(f"  {c['code_claie']} | Lot {ln} | {c['poids_charge']:.1f} kg | {c['statut']}").classes("text-body2")
                            if c["statut"] == "en_séchage":
                                with ui.row().classes("gap-2 items-center"):
                                    ps = ui.number("Poids sortie", min=0.1, value=c["poids_charge"]*0.25, step=0.1).classes("w-32")
                                    qv = ui.select(["conforme","trop_sec","pas_assez_sec"], label="Qualité", value="conforme").classes("w-40")
                                    ui.button("Sortir", on_click=lambda cid=c["id"], psv=ps, qvv=qv: (
                                        api_put(f"/claies/{cid}/sortir", {"poids_sortie":psv.value,"qualite_visuelle":qvv.value,"responsable_sortie":"Opérateur"}),
                                        ui.notify("Claie sortie", type="positive"), refresh()
                                    )).props("flat dense color=warning")
        except Exception as e: ui.label(f"Erreur: {e}").classes("text-negative")

# ── SÉCHAGE ──
@ui.page("/sechage")
def page_sechage():
    with layout():
        ui.label("Séchage — Sessions Dryers").classes("text-h4 q-mb-md")
        try:
            lots_sech = {l["id"]:l["code_lot"] for l in api_get("/lots/") if l["statut"]=="en production" or l["statut"]=="en séchage"}
            sechoirs = {s["id"]:s["nom"] for s in api_get("/sechoirs/")}
            ui.label("Nouvelle session").classes("text-h6")
            with ui.card().classes("dc frm q-mb-md"):
                with ui.row().classes("gap-4"):
                    lot = ui.select(lots_sech, label="Lot", with_input=True).classes("w-48")
                    sech = ui.select(sechoirs, label="Séchoir", with_input=True).classes("w-48")
                with ui.row().classes("gap-4"):
                    tc = ui.number("Température consigne (°C)", min=30, max=90, value=55).classes("w-48")
                    he = ui.number("Humidité entrée (%)", min=0, max=100, value=80).classes("w-48")
                    pe = ui.number("Poids entrée (kg)", min=0.1, value=0).classes("w-32")
                def demarrer():
                    s = api_post("/sechoirs/sessions/", {"lot_id":lot.value,"sechoir_id":sech.value,
                        "temperature_consigne":tc.value,"humidite_entree":he.value,"poids_entree":pe.value or 0,
                        "date_debut":datetime.now().isoformat(),"statut":"en_cours"})
                    api_put(f"/lots/{lot.value}/statut", {"statut":"en séchage"})
                    ui.notify("Session démarrée", type="positive"); refresh()
                ui.button("Démarrer le séchage", on_click=demarrer).props("color=primary")
            # Sessions en cours
            ui.label("Sessions en cours").classes("text-h6 q-mt-md")
            sessions = api_get("/sechoirs/sessions/?statut=en_cours")
            for s in sessions:
                with ui.card().classes("dc w-full q-mb-xs"):
                    sn = s.get("sechoir",{}).get("nom","?")
                    ln = s.get("lot",{}).get("code_lot","?")
                    ui.label(f"{sn} — Lot {ln}").classes("text-bold")
                    ui.label(f"Temp: {s['temperature_consigne']}°C | Poids: {s['poids_entree']:.0f} kg | Humidité: {s.get('humidite_entree','-')}%").classes("text-body2")
                    with ui.row().classes("gap-2 items-center"):
                        ps = ui.number("Poids sortie (kg)", min=0.1, value=s["poids_entree"]*0.25).classes("w-32")
                        tm = ui.number("Temp. moyenne (°C)", value=s["temperature_consigne"]).classes("w-32")
                        hs = ui.number("Humidité sortie (%)", min=0, max=100, value=12).classes("w-32")
                        ui.button("Terminer", on_click=lambda sid=s["id"], psv=ps, tmv=tm, hsv=hs: (
                            api_put(f"/sechoirs/sessions/{sid}/terminer", {"poids_sortie":psv.value,"temperature_moyenne":tmv.value,"humidite_sortie":hsv.value}),
                            ui.notify("Session terminée !", type="positive"), refresh()
                        )).props("flat dense color=warning")
        except Exception as e: ui.label(f"Erreur: {e}").classes("text-negative")

# ── CONDITIONNEMENT ──
@ui.page("/conditionnement")
def page_conditionnement():
    with layout():
        ui.label("Conditionnement — Bilan Matière").classes("text-h4 q-mb-md")
        try:
            lots_cond = {l["id"]:f"{l['code_lot']} — {l.get('produit',{}).get('nom','?')} ({l['statut']})"
                        for l in api_get("/lots/") if l["statut"] in ("en stock","en séchage","conditionné")}
            if lots_cond:
                with ui.card().classes("dc frm"):
                    lot = ui.select(lots_cond, label="Lot à conditionner", with_input=True).classes("w-80")
                    ui.label("Vérification du bilan matière").classes("text-bold q-mt-md")
                    ui.label("Le total des 3 flux doit correspondre au poids sorti du dryer (écart max 2%).").classes("text-grey text-body2")
                    with ui.row().classes("gap-4 q-mt-md"):
                        pe = ui.number("Export vrac (kg)", min=0, value=0).classes("w-32")
                        sl = ui.number("Sachets local (unités de 100g)", min=0, value=0).classes("w-48")
                    with ui.row().classes("gap-4"):
                        pd = ui.number("Déchets (kg)", min=0, value=0).classes("w-32")
                        pa = ui.number("Autres (kg)", min=0, value=0).classes("w-32")
                    op = ui.input("Responsable", value="Opérateur").classes("w-48")
                    notes = ui.input("Notes").classes("w-full")
                    def valider():
                        lid = lot.value
                        r = api_post(f"/conditionnement/lots/{lid}", {"poids_export":pe.value,"sachets_local":sl.value,
                            "poids_dechets_finaux":pd.value,"poids_autres":pa.value,"responsable":op.value,"notes":notes.value or ""})
                        if r.get("alerte_ecart_bilan"):
                            ui.notify(f"⚠️ ALERTE: écart de {r['ecart_bilan_pourcentage']}% > 2%", type="warning")
                        else:
                            ui.notify(f"✅ Bilan OK. Rendement: {r['rendement_global']}%", type="positive")
                        refresh()
                    ui.button("Valider le Conditionnement", on_click=valider).props("color=primary")
            # Derniers lots conditionnés
            ui.label("Derniers lots traités").classes("text-h6 q-mt-md")
            for l in api_get("/lots/")[:5]:
                if l.get("rendement_global"):
                    pn = l.get("produit",{}).get("nom","?")
                    ui.label(f"{l['code_lot']} — {pn} — Rendement: {l['rendement_global']}% — {l['statut']}").classes("text-body2")
        except Exception as e: ui.label(f"Erreur: {e}").classes("text-negative")

# ── COMMANDES ──
@ui.page("/commandes")
def page_commandes():
    with layout():
        ui.label("Commandes Clients").classes("text-h4 q-mb-md")
        try:
            prods = {p["id"]:f"{p['nom']} ({p['stock_actuel']:.0f} kg dispo)" for p in api_get("/produits/")}
            with ui.card().classes("dc frm q-mb-md"):
                ui.label("Nouvelle Commande").classes("text-h6")
                cn = ui.input("Client").classes("w-64"); cc = ui.input("Contact").classes("w-64")
                lignes = []
                def ajout_ligne():
                    with ui.card().classes("dc q-mb-xs"):
                        p = ui.select(prods, label="Produit", with_input=True).classes("w-64")
                        q = ui.number("Quantité (kg)", min=0.1, value=10).classes("w-32")
                        lignes.append({"p":p,"q":q})
                ui.button("+ Ajouter un produit", on_click=ajout_ligne).props("flat color=primary")
                ui.button("Créer la Commande", on_click=lambda: (
                    api_post("/commandes/", {"client_nom":cn.value,"client_contact":cc.value or "",
                        "lignes":[{"produit_id":l["p"].value,"quantite":l["q"].value} for l in lignes]}),
                    ui.notify("Commande créée", type="positive"), refresh()
                )).props("color=primary")
            # Liste des commandes
            for c in api_get("/commandes/"):
                with ui.card().classes("dc w-full q-mb-xs"):
                    with ui.row().classes("items-center justify-between"):
                        ui.label(f"Client: {c['client_nom']}").classes("text-h6")
                        ui.chip(c['statut'], selectable=False).props(f"color={'positive' if c['statut']=='livrée' else 'warning'}")
                    ui.label(f"Total: {c['total_ht']:,.0f} FCFA | {c['date_commande'][:10]}").classes("text-body2")
                    for l in c.get("lignes",[]):
                        pn = l["produit"]["nom"] if l.get("produit") else "-"
                        ui.label(f"  {pn} x {l['quantite']:.0f} kg @ {l['prix_unitaire']:,.0f} F").classes("text-body2")
        except Exception as e: ui.label(f"Erreur: {e}").classes("text-negative")

# ── PRODUITS ──
@ui.page("/produits")
def page_produits():
    with layout():
        ui.label("Produits").classes("text-h4 q-mb-md")
        try:
            cats = {c["id"]:c["nom"] for c in api_get("/categories")}
            with ui.card().classes("dc frm q-mb-md"):
                ui.label("Nouveau produit").classes("text-h6")
                with ui.row().classes("gap-4"):
                    n = ui.input("Nom").classes("w-48")
                    c = ui.select(cats, label="Catégorie", with_input=True).classes("w-48")
                with ui.row().classes("gap-4"):
                    um = ui.select(["kg","bouteille","unité","sachet"], label="Unité", value="kg").classes("w-32")
                    pu = ui.number("Prix unitaire (FCFA)", min=0, value=0).classes("w-48")
                    sm = ui.number("Stock minimum", min=0, value=50).classes("w-32")
                ui.button("Créer", on_click=lambda: (
                    api_post("/produits/", {"nom":n.value,"categorie_id":c.value,"unite_mesure":um.value,
                        "prix_unitaire":pu.value,"stock_min":sm.value}), ui.notify("Produit créé", type="positive"), refresh()
                )).props("color=primary")
            # Tableau
            for p in api_get("/produits/"):
                st = "OK" if p["stock_actuel"]>p["stock_min"] else ("BAS" if p["stock_actuel"]>0 else "RUPTURE")
                cat = p["categorie"]["nom"] if p.get("categorie") else "-"
                with ui.card().classes("dc w-full q-mb-xs"):
                    with ui.row().classes("justify-between"):
                        ui.label(p['nom']).classes("text-bold")
                        ui.chip(st, selectable=False).props(f"color={'positive' if st=='OK' else 'negative' if st=='RUPTURE' else 'warning'}")
                    ui.label(f"{cat} | Stock: {p['stock_actuel']:.0f}/{p['stock_min']:.0f} {p['unite_mesure']} | {p['prix_unitaire']:,.0f} F").classes("text-body2")
        except Exception as e: ui.label(f"Erreur: {e}").classes("text-negative")

# ── FOURNISSEURS ──
@ui.page("/fournisseurs")
def page_fournisseurs():
    with layout():
        ui.label("Fournisseurs").classes("text-h4 q-mb-md")
        try:
            with ui.card().classes("dc frm q-mb-md"):
                ui.label("Nouveau fournisseur").classes("text-h6")
                with ui.row().classes("gap-4"):
                    n = ui.input("Nom").classes("w-48"); ct = ui.input("Contact").classes("w-48")
                with ui.row().classes("gap-4"):
                    t = ui.input("Téléphone").classes("w-48"); e = ui.input("Email").classes("w-48")
                ui.button("Ajouter", on_click=lambda: (
                    api_post("/fournisseurs/", {"nom":n.value,"contact":ct.value,"telephone":t.value,"email":e.value}),
                    ui.notify("Fournisseur ajouté", type="positive"), refresh()
                )).props("color=primary")
            for f in api_get("/fournisseurs/"):
                with ui.card().classes("dc w-full q-mb-xs"):
                    ui.label(f['nom']).classes("text-bold")
                    ui.label(f"{f['contact']} | {f['telephone']} | {f['email']}").classes("text-body2")
        except Exception as e: ui.label(f"Erreur: {e}").classes("text-negative")

# ── STOCK ──
@ui.page("/stock")
def page_stock():
    with layout():
        ui.label("Stock & Mouvements").classes("text-h4 q-mb-md")
        try:
            prods = {p["id"]:p["nom"] for p in api_get("/produits/")}
            zones = {z["id"]:f"{z['nom']} ({z['type_zone']})" for z in api_get("/stock/zones")}
            ui.label("Mouvement de Stock").classes("text-h6")
            with ui.card().classes("dc frm q-mb-md"):
                with ui.row().classes("gap-4"):
                    t = ui.toggle(["Entrée","Sortie","Transfert zone"], value="Entrée").props("color=primary")
                    p = ui.select(prods, label="Produit", with_input=True).classes("w-48")
                with ui.row().classes("gap-4"):
                    q = ui.number("Quantité", min=0.1, value=10).classes("w-32")
                    m = ui.input("Motif", value="Saisie manuelle").classes("w-64")
                with ui.row().classes("gap-4"):
                    z = ui.select(zones, label="Zone de stockage", with_input=True).classes("w-64")
                    op = ui.input("Responsable", value="Opérateur").classes("w-48")
                def save_mvt():
                    if t.value == "Transfert zone":
                        api_post("/stock/stocker", {"zone_id":z.value,"produit_id":p.value,"quantite":q.value})
                        ui.notify("Stocké en zone", type="positive")
                    elif t.value == "Entrée":
                        api_post("/mouvements/entree", {"produit_id":p.value,"type_mouvement":"entrée","quantite":q.value,"motif":m.value,"responsable":op.value})
                        ui.notify("Entrée enregistrée", type="positive")
                    else:
                        api_post("/mouvements/sortie", {"produit_id":p.value,"type_mouvement":"sortie","quantite":q.value,"motif":m.value,"responsable":op.value})
                        ui.notify("Sortie enregistrée", type="positive")
                    refresh()
                ui.button("Enregistrer", on_click=save_mvt).props("color=primary")
            # Derniers mouvements
            ui.label("Derniers mouvements").classes("text-h6")
            for m in api_get("/mouvements/?limite=10"):
                pn = m["produit"]["nom"] if m.get("produit") else "-"
                with ui.card().classes("dc w-full q-mb-xs"):
                    c = "#116c4a" if m["type_mouvement"]=="entrée" else "#ba1a1a"
                    ui.label(f"{m['date_saisie'][:16]} | ").style(f"color:{c}").classes("text-bold").add_text(f"{m['type_mouvement']} — {pn} — {m['quantite']:.0f} kg | {m.get('motif','-')}")
        except Exception as e: ui.label(f"Erreur: {e}").classes("text-negative")

def lancer():
    ui.run(title="2Saisons - Gestion de Production", host="0.0.0.0", port=8080, dark=False, reload=False, show=False)

if __name__ == "__main__":
    print("2Saisons - Frontend")
    print(f"API: {API_URL}")
    print("http://localhost:8080")
    lancer()
