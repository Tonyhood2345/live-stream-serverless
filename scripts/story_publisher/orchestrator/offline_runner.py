#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
IMMOBILIARE GIANCANI — ORCHESTRATORE MODALITÀ OFFLINE (ROTAZIONE STORIE ORARIE)
═══════════════════════════════════════════════════════════════════════════════
Carica il catalogo reale degli immobili tramite l'endpoint ad alte prestazioni
'get_elenco_immobili' e fallback su catalogo locale sincronizzato.
Garantisce la rotazione continua senza mai ripetere lo stesso immobile o la
stessa immagine consecutivamente.
Estrazione rigorosa Colonna F e branding '— Immobiliare Giancani'.
"""

import os
import json
import time
import random
import hashlib
import urllib.parse
import requests

from story_publisher.config import PAGES, APPS_SCRIPT_URL, GUARANTEED_FALLBACK_IMAGES, ASSETS_DIR, SCRIPTS_DIR
from story_publisher.system.network import check_is_live_active, normalizza_foto_url
from story_publisher.core.compliance import normalize_mq
from story_publisher.core.history import carica_cronologia_storie, salva_cronologia_storie, get_recent_photo_urls
from story_publisher.video.video_engine import genera_video_da_clip_o_foto
from story_publisher.publishers.facebook import pubblica_storia_video_su_facebook
from story_publisher.publishers.youtube import pubblica_short_youtube
from story_publisher.publishers.tiktok import pubblica_storia_tiktok
from story_publisher.publishers.telegram import invia_notifica_telegram

# Catalogo di riserva garantito con immobili REALI di Immobiliare Giancani (foto HD e Colonna F)
DEFAULT_REAL_IMMOBILI = [
    {
        "id": "Appartamento_4_Piano_corso_Vittorio_Veneto__cover",
        "tabName": "Appartamento_4°_Piano_corso_Vittorio_Veneto_",
        "fonte": "Appartamento 4° Piano corso Vittorio Veneto",
        "titolo": "Appartamento 4° Piano corso Vittorio Veneto",
        "prezzo": "Trattativa Riservata",
        "mq": "140 metri quadri",
        "stanza": "Salotto Panoramico",
        "fotoUrl": "https://lh3.googleusercontent.com/d/1J_dumkLBgmNO14H2Ga0sTkEJR25jWbSw",
        "testoF": "Immaginate la luce dorata del tramonto favarese che bagna i 140 metri quadri di questo salotto, pronto a trasformarsi nel cuore pulsante della vostra nuova vita. Vista panoramica e comodità al terzo piano con ascensore — Immobiliare Giancani"
    },
    {
        "id": "Cannero_Riviera_lago_Maggiore__cover",
        "tabName": "Cannero_Riviera_lago_Maggiore_",
        "fonte": "Cannero Riviera Lago Maggiore",
        "titolo": "Cannero Riviera Lago Maggiore",
        "prezzo": "€ 15.000",
        "mq": "90 metri quadri",
        "stanza": "Camera da Letto Rifinita",
        "fotoUrl": "https://lh3.googleusercontent.com/d/1ySiRhbdekzjRk4wqrmQdYQmb-mM3BtUZ",
        "testoF": "Splendido immobile affacciato sul panorama mozzafiato del lago, ideale come oasi di relax e investimento esclusivo — Immobiliare Giancani"
    },
    {
        "id": "Terreno_17000_mq_Favara_cover",
        "tabName": "Terreno_17.000_mq_a_35.000€",
        "fonte": "Terreno 17.000 mq a 35.000€",
        "titolo": "Terreno Panoramico 17.000 mq a Favara",
        "prezzo": "€ 35.000",
        "mq": "17000 metri quadri",
        "stanza": "Terreno vista drone inizio strada",
        "fotoUrl": "https://lh3.googleusercontent.com/d/1G5wxLG8wt_hDB-MiHG7a4C6chIpW94_T",
        "testoF": "Immaginate di alzare lo sguardo verso il cielo, dove l’aria di Favara si respira a pieni polmoni e il silenzio della natura vi avvolge. Su questi ampi diciassette mila metri quadri, tra ulivi secolari, sorge il vostro sogno concreto — Immobiliare Giancani"
    },
    {
        "id": "Villa_Zingarello_cover",
        "tabName": "Villa_Zingarello",
        "fonte": "Villa Zingarello",
        "titolo": "Villa Esclusiva a Zingarello",
        "prezzo": "€ 95.000",
        "mq": "120 metri quadri",
        "stanza": "Villa vista esterna da drone Lato Ovest",
        "fotoUrl": "https://lh3.googleusercontent.com/d/1ZeFvgW36oabdrE0lGUzuTg2kcx8vJgBT",
        "testoF": "Aprite le porte ed entrate in questo suggestivo terrazzo: una magnifica apertura verso l'orizzonte dove respirare libertà e godersi la brezza siciliana. 120 metri quadri di puro fascino proposto a € 95000 — Immobiliare Giancani"
    },
    {
        "id": "Appartamento_2_piano_Via_Pavia_cover",
        "tabName": "Appartamento_2_piano_Via_Pavia_Con_vista_panoramica_",
        "fonte": "Appartamento Via Pavia con Vista",
        "titolo": "Appartamento Via Pavia con Vista Panoramica",
        "prezzo": "€ 38.000",
        "mq": "120 metri quadri",
        "stanza": "Camera da letto matrimoniale",
        "fotoUrl": "https://lh3.googleusercontent.com/d/12DCZfaRB3l2LzlKLsLD_idBzD65ipBhM",
        "testoF": "Immagina di svegliarti con la luce dorata del mattino che ti accarezza, aprendo le finestre su una vista panoramica che abbraccia tutta Favara. In questi 120 metri quadri, ogni angolo respira serenità — Immobiliare Giancani"
    },
    {
        "id": "Villa_Favara_cover",
        "tabName": "Villa_Favara",
        "fonte": "Villa Favara",
        "titolo": "Villa Indipendente con Veranda a Favara",
        "prezzo": "Trattativa Riservata",
        "mq": "160 metri quadri",
        "stanza": "Soggiorno e Giardino",
        "fotoUrl": "https://lh3.googleusercontent.com/d/14MR9QVuoOv7PJ62g5rtOm4zw0UqmAl8N",
        "testoF": "Dimora di prestigio con rifiniture ricercate, corte panoramica e grandi vetrate luminose per vivere ogni stagione nella privacy assoluta — Immobiliare Giancani"
    },
    {
        "id": "Appartamento_via_Antares_cover",
        "tabName": "Appartamento_via_Antares_villaggio_Mosè_",
        "fonte": "Appartamento Villaggio Mosè",
        "titolo": "Appartamento Rifinito Villaggio Mosè",
        "prezzo": "Trattativa Riservata",
        "mq": "120 metri quadri",
        "stanza": "Disimpegno e Cucina",
        "fotoUrl": "https://lh3.googleusercontent.com/d/1M0DJGYeQo4sqZ_Q23nom7ODVcYc2Ty1s",
        "testoF": "Soluzione moderna ed elegante al Villaggio Mosè, adiacente a tutti i servizi e a pochi minuti dal mare di San Leone — Immobiliare Giancani"
    },
    {
        "id": "Villa_Aragona_cover",
        "tabName": "Villa_Aragona",
        "fonte": "Villa Aragona",
        "titolo": "Villa con Terreno ad Aragona",
        "prezzo": "Trattativa Riservata",
        "mq": "210 metri quadri",
        "stanza": "Camera da letto Matrimoniale",
        "fotoUrl": "https://lh3.googleusercontent.com/d/13DCw7jS4GzKRhN7qH3U9RRPnh1V45vKF",
        "testoF": "Magnifica proprietà immersa nella tranquillità, dotata di ampie verande, parco alberato e spazi ideali per tutta la famiglia — Immobiliare Giancani"
    }
]

def _carica_catalogo_cache():
    """Tenta di caricare il catalogo salvato in locale."""
    paths = [
        os.path.join(ASSETS_DIR, "catalogo_immobili_cache.json"),
        os.path.join(SCRIPTS_DIR, "assets", "catalogo_immobili_cache.json"),
        os.path.join(os.path.dirname(SCRIPTS_DIR), "assets", "catalogo_immobili_cache.json")
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return data
            except Exception:
                pass
    return None

def _salva_catalogo_cache(catalogo):
    """Salva il catalogo scaricato nei percorsi di asset."""
    paths = [
        os.path.join(ASSETS_DIR, "catalogo_immobili_cache.json"),
        os.path.join(SCRIPTS_DIR, "assets", "catalogo_immobili_cache.json")
    ]
    for p in paths:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(catalogo, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

def fetch_all_property_candidates(sheet_filter=None, room_filter=None):
    """
    Recupera tutti i candidati immobili e stanze:
    1. Endpoint nativo rapido Apps Script: action=get_elenco_immobili (richiede < 10 secondi)
    2. Fallback su catalogo_immobili_cache.json (16+ immobili reali memorizzati)
    3. Fallback su DEFAULT_REAL_IMMOBILI
    """
    candidates = []
    ignora = ['pose avatar', 'impostazioni', 'configurazione', 'risultati', 'frasi', 'spot', 'pubblicita', 'battute', 'archivio', 'palinsesto', 'analytics', 'musica']

    # 1. Chiamata API REST ad alte prestazioni
    try:
        url_elenco = f"{APPS_SCRIPT_URL}?action=get_elenco_immobili"
        print(f"📡 Interrogazione catalogo rapido Google Sheets ({url_elenco[:60]}...)...")
        r = requests.get(url_elenco, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=30)
        if r.status_code == 200 and r.text.strip().startswith('{'):
            data = r.json()
            raw_immobili = data.get('immobili', [])
            for imm in raw_immobili:
                nome = imm.get('nome') or imm.get('name') or imm.get('tabName') or ''
                if any(ig in nome.lower() for ig in ignora):
                    continue
                tab = imm.get('tabName') or imm.get('name') or nome
                foto = imm.get('fotoUrl')
                if not foto or not str(foto).startswith('http'):
                    continue
                col_f = str(imm.get('testoColonnaF') or '').strip()
                if "immobiliare giancani" not in col_f.lower():
                    col_f += " — Immobiliare Giancani"

                cand_id = f"{tab}_cover"
                candidates.append({
                    "id": cand_id,
                    "sheet": tab,
                    "tabName": tab,
                    "fonte": nome,
                    "titolo": nome,
                    "stanza": imm.get('primaStanza', 'Panoramica'),
                    "prezzo": str(imm.get('prezzo', 'Trattativa Riservata')).strip(),
                    "mq": normalize_mq(imm.get('mq', '120 metri quadri')),
                    "fotoUrl": normalizza_foto_url(foto),
                    "totFoto": imm.get('totFoto', 1),
                    "testoF": col_f,
                    "videoUrl": None
                })
            if candidates:
                print(f"✅ Catalogo sincronizzato in tempo reale: {len(candidates)} immobili estratti.")
                _salva_catalogo_cache(candidates)
    except Exception as eApi:
        print(f"⚠️ Avviso connessione API catalogo: {eApi}")

    # 2. Fallback su cache locale
    if not candidates:
        cache_data = _carica_catalogo_cache()
        if cache_data:
            print(f"📦 Caricamento catalogo da cache locale persistente ({len(cache_data)} immobili)...")
            for item in cache_data:
                candidates.append({
                    "id": item.get("id") or f"{item.get('tabName')}_cover",
                    "sheet": item.get('tabName'),
                    "tabName": item.get('tabName'),
                    "fonte": item.get('fonte') or item.get('titolo'),
                    "titolo": item.get('titolo'),
                    "stanza": item.get('stanza', 'Panoramica'),
                    "prezzo": item.get('prezzo', 'Trattativa Riservata'),
                    "mq": normalize_mq(item.get('mq', '120 metri quadri')),
                    "fotoUrl": normalizza_foto_url(item.get('fotoUrl')),
                    "totFoto": item.get('totFoto', 1),
                    "testoF": item.get('testoF') or item.get('testoColonnaF'),
                    "videoUrl": None
                })

    # 3. Fallback su catalogo reale garantito incorporato
    if not candidates:
        print("ℹ️ Utilizzo catalogo reale garantito incorporato...")
        for item in DEFAULT_REAL_IMMOBILI:
            candidates.append({
                "id": item["id"],
                "sheet": item["tabName"],
                "tabName": item["tabName"],
                "fonte": item["fonte"],
                "titolo": item["titolo"],
                "stanza": item["stanza"],
                "prezzo": item["prezzo"],
                "mq": normalize_mq(item["mq"]),
                "fotoUrl": item["fotoUrl"],
                "totFoto": 1,
                "testoF": item["testoF"],
                "videoUrl": None
            })

    # Applicazione filtri opzionali
    if sheet_filter:
        sf_low = str(sheet_filter).strip().lower()
        candidates = [c for c in candidates if sf_low in c['titolo'].lower() or sf_low in c['sheet'].lower()]

    return candidates

def _espandi_stanze_immobile_se_possibile(selected_prop, recent_photos):
    """
    Tenta di interrogare il singolo foglio dell'immobile scelto per scoprire
    tutte le sue stanze e foto interne, offrendo massima varietà visiva.
    """
    tab_name = selected_prop.get("tabName") or selected_prop.get("sheet")
    if not tab_name or selected_prop.get("totFoto", 1) <= 1:
        return selected_prop

    try:
        url_sheet = f"{APPS_SCRIPT_URL}?action=get_sheet&name={urllib.parse.quote(tab_name)}"
        r = requests.get(url_sheet, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=18)
        if r.status_code == 200 and r.text.strip().startswith('{'):
            d = r.json()
            rows = d.get('rows', [])
            stanze_valide = []
            for r_idx, row in enumerate(rows[1:], start=2):
                if len(row) > 5 and row[5] and str(row[5]).strip():
                    f_url = normalizza_foto_url(str(row[0] or ''))
                    if not f_url and len(row) > 6:
                        f_url = normalizza_foto_url(str(row[6] or ''))
                    if not f_url or not f_url.startswith('http'):
                        continue
                    
                    stanza_nome = str(row[3] or row[0] or '').strip()
                    testo_riga = str(row[5]).strip()
                    if "immobiliare giancani" not in testo_riga.lower():
                        testo_riga += " — Immobiliare Giancani"

                    s_hash = hashlib.md5(f"{tab_name}_{r_idx}_{f_url}".encode()).hexdigest()[:8]
                    stanze_valide.append({
                        "id": f"{tab_name}_riga{r_idx}_{s_hash}",
                        "fotoUrl": f_url,
                        "stanza": stanza_nome,
                        "testoF": testo_riga,
                        "titolo": f"{selected_prop['titolo']} — {stanza_nome}" if stanza_nome and stanza_nome.lower() not in ['ambiente', ''] else selected_prop['titolo']
                    })

            if stanze_valide:
                # Privilegia stanze con foto mai viste di recente
                stanze_mai_viste = [s for s in stanze_valide if s['fotoUrl'] not in recent_photos]
                scelta_stanza = random.choice(stanze_mai_viste or stanze_valide)
                selected_prop["id"] = scelta_stanza["id"]
                selected_prop["fotoUrl"] = scelta_stanza["fotoUrl"]
                selected_prop["stanza"] = scelta_stanza["stanza"]
                selected_prop["titolo"] = scelta_stanza["titolo"]
                selected_prop["testoF"] = scelta_stanza["testoF"]
                print(f"🏠 Stanza specifica selezionata: '{scelta_stanza['stanza']}' (Foto URL: {scelta_stanza['fotoUrl'][:50]}...)")
    except Exception as eSheet:
        print(f"ℹ️ Dettaglio stanze non disponibile via foglio singolo ({eSheet}), utilizzo cover principale.")

    return selected_prop

def esegui_ciclo_offline(style="auto", sheet_filter=None, room_filter=None, custom_text=None, custom_image=None, custom_title=None):
    """
    Esegue la pubblicazione oraria programmata offline con equa rotazione
    anti-ripetizione su tutti gli immobili e le stanze del catalogo.
    """
    print("\n" + "═" * 70)
    print("🕒 CONTROLLO PUBBLICAZIONE STORIA OFFLINE / CATALOGO")
    print("═" * 70)

    is_manual = bool(custom_text or custom_image or sheet_filter or room_filter)
    if not is_manual:
        is_live, run_id = check_is_live_active()
        if is_live:
            print(f"ℹ️ Diretta Live streaming rilevata (Run ID: {run_id}). Procedo regolarmente con la storia oraria.")
        else:
            print("ℹ️ Nessuna diretta live streaming attiva. Esecuzione storia oraria catalogo.")

    print("✅ Procedo con la selezione dell'immobile e la generazione della storia...")

    # CASO A: Contenuto Custom o non immobiliare
    if custom_text or custom_image:
        print("🎨 Modalità Storia Personalizzata / Non Immobiliare attiva.")
        t_clean = str(custom_text or "Novità e aggiornamenti da Favara e Agrigento").strip()
        if "immobiliare giancani" not in t_clean.lower():
            t_clean += " — Immobiliare Giancani"

        img_sel = custom_image or random.choice(GUARANTEED_FALLBACK_IMAGES)
        tit_sel = custom_title or "Comunicazione Speciale"

        media_info = {
            "titolo": tit_sel,
            "prezzo": "",
            "mq": "",
            "videoUrl": None,
            "fotoUrl": img_sel,
            "testoF": t_clean,
            "isLive": False
        }
        selected = {
            "id": f"custom_{int(time.time())}",
            "titolo": tit_sel,
            "fonte": "Storia Personalizzata / Non Immobiliare",
            "mq": "",
            "prezzo": "",
            "fotoUrl": img_sel
        }
    else:
        # CASO B: Catalogo Immobili Reale
        candidates = fetch_all_property_candidates(sheet_filter=sheet_filter, room_filter=room_filter)
        if not candidates:
            print("❌ Impossibile recuperare immobili dal catalogo.")
            return []

        # ROTAZIONE CASUALE ANTI-RIPETIZIONE CON CRONOLOGIA PERSISTENTE
        cronologia = carica_cronologia_storie()
        recent_photos = get_recent_photo_urls(cronologia)

        # Candidati mai visti (sia per ID immobile sia per foto pubblicata di recente)
        candidati_mai_visti = [
            c for c in candidates 
            if c["id"] not in cronologia and c.get("fotoUrl") not in recent_photos
        ]

        if not candidati_mai_visti:
            print(f"🔄 Tutte le foto/immobili del catalogo ({len(candidates)}) sono state pubblicate di recente!")
            print("   Reset controllato della cronologia preservando gli ultimi elementi per evitare doppioni consecutivi...")
            items_sorted = sorted(
                cronologia.items(),
                key=lambda x: x[1].get("timestamp", 0) if isinstance(x[1], dict) else 0
            )
            # Conserva solo gli ultimi elementi (fino a 4) per garantire varietà
            n_keep = min(4, max(1, len(candidates) // 3))
            ultimi = dict(items_sorted[-n_keep:]) if len(items_sorted) >= n_keep else {}
            cronologia = ultimi
            recent_photos = get_recent_photo_urls(cronologia)

            candidati_mai_visti = [
                c for c in candidates 
                if c["id"] not in cronologia and c.get("fotoUrl") not in recent_photos
            ]
            if not candidati_mai_visti:
                ultima_foto = items_sorted[-1][1].get("fotoUrl") if items_sorted else None
                candidati_mai_visti = [c for c in candidates if c.get("fotoUrl") != ultima_foto] or candidates

        # Selezione casuale tra i candidati non ancora pubblicati
        selected_raw = random.choice(candidati_mai_visti)

        # Approfondimento stanza se disponibile
        selected = _espandi_stanze_immobile_se_possibile(selected_raw, recent_photos)

        # Registrazione cronologia
        cronologia[selected["id"]] = {
            "timestamp": time.time(),
            "titolo": selected["titolo"],
            "fonte": selected.get("fonte", selected["titolo"]),
            "stanza": selected.get("stanza", ""),
            "fotoUrl": selected.get("fotoUrl", "")
        }
        salva_cronologia_storie(cronologia)

        print(f"🎯 Immobile selezionato A CASO per la storia ({len(cronologia)} pubblicati nel ciclo su {len(candidates)} totali):")
        print(f"   Titolo: {selected['titolo']} ({selected.get('fonte', '')})")
        print(f"   Dati sincronizzati atomici: Prezzo={selected.get('prezzo')}, MQ={selected.get('mq')}, Foto={bool(selected.get('fotoUrl'))}")
        print(f"   Colonna F: '{selected.get('testoF', '')[:70]}...'")

        media_info = {
            "titolo": selected.get('titolo', 'Immobile in Vendita'),
            "prezzo": selected.get('prezzo', 'Trattativa Riservata'),
            "mq": normalize_mq(selected.get('mq', '120 metri quadri')),
            "videoUrl": selected.get('videoUrl'),
            "fotoUrl": selected.get('fotoUrl'),
            "testoF": selected.get('testoF'),
            "isLive": False
        }

    video_path = genera_video_da_clip_o_foto(media_info, style=style)
    if not video_path:
        print("❌ Errore generazione video storia offline.")
        return []

    risultati = []
    for target in PAGES:
        print(f"📘 Pubblicazione Video Storia su: {target['nome']}...")
        try:
            res = pubblica_storia_video_su_facebook(target['id'], target['token'], video_path)
            res['nome'] = target['nome']
            print(f"[OK] Storia pubblicata! ID: {res.get('story_id')}")
            risultati.append(res)
        except Exception as ePub:
            print(f"❌ Errore upload su {target['nome']}: {ePub}")
            risultati.append({"nome": target['nome'], "success": False, "error": str(ePub)})

    # YouTube Shorts (@immobiliaregiancani761)
    try:
        res_yt = pubblica_short_youtube(video_path, media_info)
        print(f"[OK] YouTube Shorts: {res_yt.get('story_id')} - {res_yt.get('url')}")
        risultati.append(res_yt)
    except Exception as eYt:
        print(f"❌ Errore YouTube Shorts: {eYt}")
        risultati.append({"nome": "YouTube Shorts (@immobiliaregiancani761)", "success": False, "error": str(eYt)})

    # TikTok Stories (@immobiliare_giancani)
    try:
        res_tk = pubblica_storia_tiktok(video_path, media_info)
        print(f"[OK] TikTok Stories: {res_tk.get('story_id')} - {res_tk.get('url')}")
        risultati.append(res_tk)
    except Exception as eTk:
        print(f"❌ Errore TikTok Stories: {eTk}")
        risultati.append({"nome": "TikTok Stories (@immobiliare_giancani)", "success": False, "error": str(eTk)})

    invia_notifica_telegram(selected['titolo'], selected.get('mq', ''), selected.get('prezzo', ''), risultati, is_live=False)
    print("✨ Ciclo storia oraria multi-piattaforma completato con successo. — Immobiliare Giancani\n")
    return risultati
