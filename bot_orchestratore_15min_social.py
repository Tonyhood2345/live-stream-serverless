#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═════════════════════════════════════════════════════════════════════════════════
IMMOBILIARE GIANCANI — MASTER ORCHESTRATORE STORIE SOCIAL (15 MINUTI ALTERNATO)
═════════════════════════════════════════════════════════════════════════════════
Funzionalità Principali:
1. ALTERNANZA RIGOROSA OGNI 15 MINUTI (900s):
   - Ciclo Dispari : BOT IMMAGINI (Storie 9:16 con foto reale immobile + grafica multi-stile + audio)
   - Ciclo Pari    : BOT VIDEO    (Clip 30s da archivio YouTube con card semi-trasparente)
2. FORM STILE GRAFICO E CARATTERISTICA VISIVA PER LE IMMAGINI:
   - Rotazione continua dei 6 stili stabiliti:
     * split_screen      : 40% foto verticale sinistra 3D ribbon, 60% scheda immobile destra
     * luxury_glass      : Glassmorphism dorato, bordi satinati, full photo con gradiente scuro
     * editorial         : Magazine chic moderno, serif luxury (Fraunces), layout minimal
     * gabetti_diagonal  : Taglio diagonale dinamico ad alto contrasto
     * capellupo_sidebar : Sidebar laterale con icone tecniche (camere, bagni, metri quadri)
     * marketing_banner  : Banner promozionale con badge prezzo e CTA diretta
3. ASSOLUTO OBBLIGO DI IMMAGINI DIVERSE AD OGNI STORIA:
   - Registro storico persistente delle immagini utilizzate.
   - Nessuna foto viene ripetuta finché tutte le immagini del catalogo non sono state pubblicate.
4. COLLEGAMENTO A TUTTI I SOCIAL DELL'AGENZIA:
   - Facebook Stories: Pagina Ufficiale Immobiliare Giancani (ID 234931856561526)
   - Instagram Stories: Account Ufficiale @giancani_immobiliare (ID 17841400301393511)
   - Profilo Antonio Giancani: (ID 108297671444008) con invito dinamico a visitare la pagina ufficiale
5. NOTIFICHE TELEGRAM RIGOROSAMENTE OGNI 4 ORE:
   - Nessun messaggio inviato ogni 15 minuti.
   - Singolo report cumulativo ogni 4 ore contenente SOLO l'elenco dei link delle pubblicazioni fatte.
   - Chiusura formale: — Immobiliare Giancani
═════════════════════════════════════════════════════════════════════════════════
"""

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
orig_create_default_context = ssl.create_default_context
def unverified_create_default_context(*args, **kwargs):
    c = orig_create_default_context(*args, **kwargs)
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c
ssl.create_default_context = unverified_create_default_context

import os
import sys
import time
import json
import uuid
import random
import re
import subprocess
from datetime import datetime
import urllib.request
import urllib.parse
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Percorsi base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch")
CLIPS_DIR = os.path.join(BASE_DIR, "clip_30s_generate")
CACHE_DIR = os.path.join(BASE_DIR, "video_cache")
os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Aggiungi cartelle a sys.path per importare i moduli interni
for p in [BASE_DIR, os.path.join(BASE_DIR, "scripts"), os.path.join(BASE_DIR, "live_stream_appscript"), PROJECT_DIR]:
    if p not in sys.path and os.path.exists(p):
        sys.path.insert(0, p)

# File di stato e registri persistenti
STATO_ORCHESTRATORE_FILE = os.path.join(BASE_DIR, "stato_orchestratore_15min.json")
STORICO_IMMAGINI_FILE = os.path.join(BASE_DIR, "storico_immagini_pubblicate.json")
STORICO_VIDEO_YT_FILE = os.path.join(BASE_DIR, "registro_video_pubblicati.json")
BUFFER_REPORT_4ORE_FILE = os.path.join(BASE_DIR, "buffer_report_4ore.json")
CATALOGO_CACHE_FILE = os.path.join(BASE_DIR, "catalogo_youtube_cache.json")
CATALOGO_IMMOBILI_CACHE = os.path.join(ASSETS_DIR, "catalogo_immobili_cache.json")

# Credenziali e Social
FB_PAGE_ID = (os.environ.get("FB_PAGE_ID") or "234931856561526").strip()
FB_PAGE_TOKEN = (os.environ.get("FB_PAGE_TOKEN") or "EAAZAH7q8wRZAEBS3ZAfEIpFIcXPJ87gDZAY8QjpGvBSjgC44c22JVeZAiDxMOM85JRMKM2T1hLgekBCkT0z5geNsb3KxAhMr7W7xlOGVKJsdKV9rZCEKLupIy1uNaDkVZAXmFtn0stiB212odWJ2ZCZBtlWkZAzy5wmPfKyZC3g27g6RXs0FK2GiYc5MeqaZCZBuoYjIyreTZAxwOqtfESifVw").strip()
FB_ANTONIO_ID = os.environ.get("FB_ANTONIO_ID", "108297671444008").strip()
IG_ACCOUNT_ID = os.environ.get("IG_ACCOUNT_ID", "17841400301393511").strip()
YT_CHANNEL_HANDLE = "@immobiliaregiancani761"
CHANNEL_URL = f"https://www.youtube.com/{YT_CHANNEL_HANDLE}/videos"

# Telegram
TELEGRAM_BOT_TOKEN = "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M"
TELEGRAM_CHAT_ID = "1723292483"

# Intervalli
INTERVALLO_STORIA_SECONDI = 900     # 15 minuti
INTERVALLO_REPORT_SECONDI = 14400   # 4 ore (4 * 3600s)

# Form Stili Grafici e Caratteristiche Visive per le Immagini
STILI_GRAFICI_TABELLA = [
    {
        "id": "split_screen",
        "nome": "Split-Screen 3D Ribbon",
        "caratteristica": "40% colonna sinistra foto verticale con nastro 3D, 60% colonna destra con scheda immobile, badge prezzo e finiture."
    },
    {
        "id": "luxury_glass",
        "nome": "Luxury Glassmorphism",
        "caratteristica": "Card effetto vetro smerigliato (glassmorphism), bordi oro satinato e visualizzazione full photo con gradiente scuro."
    },
    {
        "id": "editorial",
        "nome": "Editorial Magazine",
        "caratteristica": "Layout magazine moderno con tipografia serif luxury (Fraunces), layout pulito per immobili di pregio e ville."
    },
    {
        "id": "gabetti_diagonal",
        "nome": "Gabetti Diagonal Cut",
        "caratteristica": "Taglio diagonale dinamico con accento cromatico a forte contrasto."
    },
    {
        "id": "capellupo_sidebar",
        "nome": "Capellupo Sidebar",
        "caratteristica": "Sidebar laterale con icone tecniche (camere, bagni, metri quadri)."
    },
    {
        "id": "marketing_banner",
        "nome": "Marketing Banner",
        "caratteristica": "Banner d'impatto con badge prezzo ribassato e call to action diretta."
    }
]

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def normalizza_url(u):
    if not u:
        return ""
    return str(u).strip().split('?')[0].lower()

# ═════════════════════════════════════════════════════════════════════════════
# 💾 GESTIONE REGISTRI PERSISTENTI (STATO, IMMAGINI, VIDEO, BUFFER 4 ORE)
# ═════════════════════════════════════════════════════════════════════════════

def carica_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default
    return default

def salva_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"Avviso salvataggio {os.path.basename(path)}: {e}")

def carica_stato():
    return carica_json(STATO_ORCHESTRATORE_FILE, {
        "ciclo_progressivo": 0,
        "prossimo_tipo": "IMMAGINE", # ALTERNA: IMMAGINE -> VIDEO
        "indice_stile": 0,
        "ultimo_report_4ore_ts": time.time()
    })

def salva_stato(stato):
    salva_json(STATO_ORCHESTRATORE_FILE, stato)

def carica_storico_immagini():
    return set(carica_json(STORICO_IMMAGINI_FILE, []))

def aggiungi_a_storico_immagini(foto_url):
    storico = carica_storico_immagini()
    storico.add(normalizza_url(foto_url))
    salva_json(STORICO_IMMAGINI_FILE, list(storico))

def carica_storico_video_yt():
    return set(carica_json(STORICO_VIDEO_YT_FILE, []))

def aggiungi_a_storico_video_yt(vid_id):
    storico = carica_storico_video_yt()
    storico.add(str(vid_id).strip())
    salva_json(STORICO_VIDEO_YT_FILE, list(storico))

def carica_buffer_report():
    return carica_json(BUFFER_REPORT_4ORE_FILE, [])

def aggiungi_a_buffer_report(evento):
    buffer = carica_buffer_report()
    buffer.append(evento)
    salva_json(BUFFER_REPORT_4ORE_FILE, buffer)

def azzera_buffer_report():
    salva_json(BUFFER_REPORT_4ORE_FILE, [])


# ═════════════════════════════════════════════════════════════════════════════
# 🌐 PUBBLICAZIONE SOCIAL UNIFICATA (FACEBOOK + INSTAGRAM + ANTONIO GIANCANI)
# ═════════════════════════════════════════════════════════════════════════════

def pubblica_storia_facebook(page_id, page_token, video_path):
    """Pubblica video storia su Pagina Facebook tramite Meta Graph API /video_stories"""
    try:
        file_size = os.path.getsize(video_path)
        # 1. Start Phase
        url_start = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"
        params_start = f"upload_phase=start&access_token={urllib.parse.quote(page_token)}".encode('utf-8')
        req_start = urllib.request.Request(url_start, data=params_start, method='POST')
        with urllib.request.urlopen(req_start, timeout=30) as resp:
            start_data = json.loads(resp.read().decode('utf-8'))
            video_id = start_data.get('video_id')
            upload_url = start_data.get('upload_url')

        if not video_id or not upload_url:
            return {"success": False, "error": "Nessun video_id o upload_url ricevuto"}

        # 2. Upload binario
        with open(video_path, 'rb') as f_v:
            v_bytes = f_v.read()

        req_up = urllib.request.Request(
            upload_url,
            data=v_bytes,
            headers={
                "Authorization": f"OAuth {page_token}",
                "offset": "0",
                "file_size": str(file_size)
            },
            method="POST"
        )
        with urllib.request.urlopen(req_up, timeout=120) as resp_up:
            up_res = json.loads(resp_up.read().decode('utf-8'))

        # 3. Finish Phase
        url_fin = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"
        params_fin = f"upload_phase=finish&video_id={video_id}&video_state=PUBLISHED&access_token={urllib.parse.quote(page_token)}".encode('utf-8')
        req_fin = urllib.request.Request(url_fin, data=params_fin, method='POST')
        with urllib.request.urlopen(req_fin, timeout=30) as resp_fin:
            fin_res = json.loads(resp_fin.read().decode('utf-8'))

        story_id = fin_res.get('post_id') or video_id
        link_fb = f"https://www.facebook.com/stories/{page_id}"
        log(f"   ✅ [Facebook Story Pubblicata] ID: {story_id}")
        return {"success": True, "story_id": story_id, "link": link_fb}
    except Exception as e:
        log(f"   ⚠️ Avviso Facebook Story ({page_id}): {e}")
        return {"success": False, "error": str(e)}


def pubblica_storia_instagram(video_path):
    """Pubblica video storia su Instagram Stories (@giancani_immobiliare) via Resumable Upload"""
    try:
        # 1. Init container resumable
        init_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"
        data = {
            'media_type': 'STORIES',
            'upload_type': 'resumable',
            'access_token': FB_PAGE_TOKEN
        }
        r_init = requests.post(init_url, data=data, verify=False, timeout=30)
        if r_init.status_code != 200:
            return {"success": False, "error": f"Init container fallito: {r_init.text}"}
        
        res_init = r_init.json()
        container_id = res_init['id']
        upload_uri = res_init['uri']

        # 2. Upload binario
        file_size = os.path.getsize(video_path)
        with open(video_path, 'rb') as f:
            video_bytes = f.read()

        headers = {
            'Authorization': f'OAuth {FB_PAGE_TOKEN}',
            'offset': '0',
            'file_size': str(file_size)
        }
        r_up = requests.post(upload_uri, headers=headers, data=video_bytes, verify=False, timeout=120)
        if r_up.status_code != 200:
            return {"success": False, "error": f"Upload binario fallito: {r_up.text}"}

        # 3. Attesa elaborazione container
        for _ in range(12):
            time.sleep(4)
            st_url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code,status&access_token={FB_PAGE_TOKEN}"
            r_st = requests.get(st_url, verify=False, timeout=15)
            st_data = r_st.json()
            status = st_data.get('status_code')
            if status == 'FINISHED':
                break
            elif status == 'ERROR':
                return {"success": False, "error": f"Errore processing IG: {st_data}"}

        # 4. Pubblicazione finale
        pub_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish"
        r_pub = requests.post(pub_url, data={'creation_id': container_id, 'access_token': FB_PAGE_TOKEN}, verify=False, timeout=30)
        if r_pub.status_code == 200:
            story_id = r_pub.json().get('id')
            link_ig = "https://www.instagram.com/giancani_immobiliare/"
            log(f"   📸 [Instagram Story Pubblicata] ID: {story_id}")
            return {"success": True, "story_id": story_id, "link": link_ig}
        else:
            return {"success": False, "error": r_pub.text}
    except Exception as e:
        log(f"   ⚠️ Avviso Instagram Story: {e}")
        return {"success": False, "error": str(e)}


# ═════════════════════════════════════════════════════════════════════════════
# 📸 1. LOGICA BOT IMMAGINI (MULTI-STILE & ASSOLUTO OBBLIGO IMMAGINI DIVERSE)
# ═════════════════════════════════════════════════════════════════════════════

def carica_tutti_candidati_immagini():
    """Carica il catalogo completo di tutti gli immobili e foto disponibili"""
    candidates = []
    if os.path.exists(CATALOGO_IMMOBILI_CACHE):
        try:
            with open(CATALOGO_IMMOBILI_CACHE, 'r', encoding='utf-8') as f:
                c_list = json.load(f)
                for item in c_list:
                    foto = item.get("fotoUrl")
                    if foto:
                        t_f = str(item.get("testoF") or item.get("testoDaLeggere") or "").strip()
                        if "immobiliare giancani" not in t_f.lower():
                            t_f += "\n\n— Immobiliare Giancani"
                        candidates.append({
                            "id": item.get("id"),
                            "titolo": item.get("titolo") or "Immobile Giancani",
                            "stanza": item.get("stanza", "Ambiente"),
                            "prezzo": item.get("prezzo", "Trattativa Riservata"),
                            "mq": item.get("mq", "120 metri quadri"),
                            "fotoUrl": foto,
                            "testoF": t_f
                        })
        except Exception as e:
            log(f"Avviso caricamento catalogo immagini: {e}")

    # Fallback aggiuntivo dalle immagini locali in assets/immobili_cache
    local_cache_dir = os.path.join(ASSETS_DIR, "immobili_cache")
    if os.path.exists(local_cache_dir):
        for fname in os.listdir(local_cache_dir):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                full_p = os.path.join(local_cache_dir, fname)
                candidates.append({
                    "id": f"local_{fname}",
                    "titolo": "Residenza Esclusiva ad Agrigento e Favara",
                    "stanza": "Vista Esclusiva",
                    "prezzo": "Trattativa Riservata",
                    "mq": "140 metri quadri",
                    "fotoUrl": full_p,
                    "testoF": "Soluzione immobiliare di assoluto pregio, finiture curate e massimo comfort abitativo a Favara e Agrigento. — Immobiliare Giancani"
                })

    return candidates


def seleziona_prossima_immagine_mai_usata():
    """
    ASSOLUTO OBBLIGO DI IMMAGINI DIVERSE:
    Seleziona rigorosamente una foto MAI utilizzata nel ciclo corrente.
    Se tutte le foto del catalogo sono state usate, azzera lo storico e ricomincia.
    """
    candidates = carica_tutti_candidati_immagini()
    if not candidates:
        log("❌ Nessuna immagine disponibile nel catalogo.")
        return None

    storico = carica_storico_immagini()

    mai_usate = [c for c in candidates if normalizza_url(c["fotoUrl"]) not in storico]

    if not mai_usate:
        log("🔄 [RESET ANTI-RIPETIZIONE] Tutte le immagini del catalogo sono state mostrate! Azzero lo storico per una nuova rotazione...")
        storico = set()
        salva_json(STORICO_IMMAGINI_FILE, [])
        mai_usate = candidates

    scelta = mai_usate[0]
    aggiungi_a_storico_immagini(scelta["fotoUrl"])
    log(f"🖼️ Foto unica selezionata ({len(storico) + 1}/{len(candidates)} nel ciclo): {scelta['titolo']} ({scelta.get('stanza')})")
    return scelta


def esegui_ciclo_immagini(indice_stile):
    """Esegue la generazione e pubblicazione di una storia immagine multi-stile"""
    immobile = seleziona_prossima_immagine_mai_usata()
    if not immobile:
        return None

    # Rotazione Stile Grafico
    stile_info = STILI_GRAFICI_TABELLA[indice_stile % len(STILI_GRAFICI_TABELLA)]
    stile_scelto = stile_info["id"]

    log(f"🎨 [BOT IMMAGINI] Stile Grafico: {stile_info['nome']} ({stile_scelto.upper()})")
    log(f"   ℹ️ Caratteristica Visiva: {stile_info['caratteristica']}")

    # Generazione video 15s con il motore di rendering
    from pubblica_storia_facebook import genera_video_da_clip_o_foto
    media_info = {
        "titolo": immobile["titolo"],
        "prezzo": immobile["prezzo"],
        "mq": immobile["mq"],
        "fotoUrl": immobile["fotoUrl"],
        "testoF": immobile["testoF"],
        "isLive": False,
        "story_index": indice_stile
    }

    video_path = genera_video_da_clip_o_foto(media_info, style=stile_scelto)
    if not video_path or not os.path.exists(video_path):
        log("❌ Errore rendering video storia immagine.")
        return None

    # Pubblicazione su tutti i social
    res_fb = pubblica_storia_facebook(FB_PAGE_ID, FB_PAGE_TOKEN, video_path)
    res_ig = pubblica_storia_instagram(video_path)

    # Evento per il report 4 ore
    evento = {
        "ora": datetime.now().strftime("%H:%M"),
        "tipo": f"IMMAGINE ({stile_info['nome']})",
        "titolo": immobile["titolo"],
        "dettaglio": stile_info["caratteristica"],
        "link_fb": res_fb.get("link") if res_fb.get("success") else "Errore / In attesa",
        "link_ig": res_ig.get("link") if res_ig.get("success") else "Errore / In attesa",
        "story_id_fb": res_fb.get("story_id"),
        "story_id_ig": res_ig.get("story_id")
    }
    aggiungi_a_buffer_report(evento)
    return evento


# ═════════════════════════════════════════════════════════════════════════════
# 🎬 2. LOGICA BOT VIDEO ARCHIVIO YOUTUBE (CLIP 30s & CARD SEMI-TRASPARENTE)
# ═════════════════════════════════════════════════════════════════════════════

def esegui_ciclo_video_youtube():
    """Esegue la generazione e pubblicazione di uno spezzone video 30s da archivio YouTube"""
    from bot_youtube_archivio_orario import (
        estrai_e_popola_sheet, scarica_video_completo, genera_clip_30s, PAGES
    )

    log("🎬 [BOT VIDEO] Selezione video da archivio YouTube (1 anno a ritroso)...")
    catalog = estrai_e_popola_sheet()
    if not catalog:
        log("❌ Catalogo YouTube vuoto o non accessibile.")
        return None

    storico_video = carica_storico_video_yt()
    mai_visti = [v for v in catalog if v['id'] not in storico_video]

    if not mai_visti:
        log("🔄 [RESET VIDEO] Tutti i video del catalogo sono stati usati! Reset storico...")
        storico_video = set()
        salva_json(STORICO_VIDEO_YT_FILE, [])
        mai_visti = catalog

    scelto = mai_visti[0]
    aggiungi_a_storico_video_yt(scelto['id'])
    log(f"🎯 Video YouTube selezionato: {scelto['title']} (ID: {scelto['id']})")

    # 1. Download video completo con fallback resiliente
    try:
        video_locale = scarica_video_completo(scelto['id'], scelto['url'])
    except Exception as eDl:
        log(f"⚠️ Impossibile scaricare video YouTube da server cloud: {eDl}")
        log("🔄 Esecuzione fallback immediato: generazione storia immagine multi-stile!")
        indice_stile = carica_stato().get("indice_stile", 0)
        return esegui_ciclo_immagini(indice_stile)

    # 2. Generazione clip 30s con card inferiore semi-trasparente e top libero per logo
    clip_path = genera_clip_30s(video_locale, scelto, per_antonio=False)

    # 3. Pubblicazione su tutti i social
    res_fb = pubblica_storia_facebook(FB_PAGE_ID, FB_PAGE_TOKEN, clip_path)
    res_ig = pubblica_storia_instagram(clip_path)

    # Opzionale: versione Antonio Giancani
    try:
        clip_antonio = genera_clip_30s(video_locale, scelto, per_antonio=True)
        pubblica_storia_facebook(FB_ANTONIO_ID, FB_PAGE_TOKEN, clip_antonio)
    except Exception as eAnt:
        log(f"   ⚠️ Avviso pubblicazione Antonio: {eAnt}")

    # Evento per il report 4 ore
    short_url = f"https://youtu.be/{scelto['id']}"
    evento = {
        "ora": datetime.now().strftime("%H:%M"),
        "tipo": "VIDEO YOUTUBE (Clip 30s Archivio)",
        "titolo": scelto["title"],
        "dettaglio": f"Fonte YouTube: {short_url}",
        "link_fb": res_fb.get("link") if res_fb.get("success") else "Errore / In attesa",
        "link_ig": res_ig.get("link") if res_ig.get("success") else "Errore / In attesa",
        "link_yt": short_url,
        "story_id_fb": res_fb.get("story_id"),
        "story_id_ig": res_ig.get("story_id")
    }
    aggiungi_a_buffer_report(evento)
    return evento


# ═════════════════════════════════════════════════════════════════════════════
# 📬 3. NOTIFICA TELEGRAM SOLO OGNI 4 ORE CON SOLO I LINK DEGLI INVII FATTI
# ═════════════════════════════════════════════════════════════════════════════

def verifica_e_invia_report_4ore(stato, forza=False):
    """
    Controlla se sono trascorse 4 ore (14400 secondi) o 16 cicli.
    Invia un SINGOLO messaggio Telegram con SOLO l'elenco dei link e titoli.
    """
    ora_attuale = time.time()
    ultimo_ts = stato.get("ultimo_report_4ore_ts", ora_attuale)
    tempo_trascorso = ora_attuale - ultimo_ts

    buffer = carica_buffer_report()

    # Invia se sono passate 4 ore o se ci sono almeno 16 invii (1 ogni 15 min = 16 in 4 ore) o su forzatura
    if not forza and tempo_trascorso < INTERVALLO_REPORT_SECONDI and len(buffer) < 16:
        log(f"⏱️ Buffer 4 ore in accumulo: {len(buffer)} pubblicazioni registrate. Prossimo report Telegram tra {int((INTERVALLO_REPORT_SECONDI - tempo_trascorso)/60)} minuti.")
        return False

    if not buffer:
        log("ℹ️ Nessuna pubblicazione nel buffer per il report 4 ore.")
        stato["ultimo_report_4ore_ts"] = ora_attuale
        salva_stato(stato)
        return False

    log(f"📨 [REPORT 4 ORE TELEGRAM] Elaborazione riassunto per {len(buffer)} pubblicazioni effettuate...")

    righe_report = []
    righe_report.append("📋 <b>RIEPILOGO PUBBLICAZIONI SOCIAL — ULTIME 4 ORE</b>")
    righe_report.append(f"⏱️ Totale Storie Pubblicate: <b>{len(buffer)}</b> (Alternanza 15 min Immagini & Video)\n")

    for i, ev in enumerate(buffer, start=1):
        riga = f"<b>{i}. [{ev.get('ora')}] {ev.get('tipo')}</b>\n"
        riga += f"   📌 <i>{ev.get('titolo')}</i>\n"
        if ev.get("link_yt"):
            riga += f"   🔗 YouTube: <a href=\"{ev.get('link_yt')}\">{ev.get('link_yt')}</a>\n"
        if ev.get("link_fb"):
            riga += f"   📘 Facebook Story: <a href=\"{ev.get('link_fb')}\">Apri Storia</a>\n"
        if ev.get("link_ig"):
            riga += f"   📸 Instagram Story: <a href=\"{ev.get('link_ig')}\">@giancani_immobiliare</a>\n"
        righe_report.append(riga)

    righe_report.append("— <b>Immobiliare Giancani</b>")
    testo_finale = "\n".join(righe_report)

    try:
        url_tg = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        d_tg = urllib.parse.urlencode({
            'chat_id': TELEGRAM_CHAT_ID,
            'text': testo_finale,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }).encode('utf-8')
        req = urllib.request.Request(url_tg, data=d_tg, method='POST')
        with urllib.request.urlopen(req, timeout=30) as r:
            res_tg = json.loads(r.read().decode('utf-8'))
            if res_tg.get('ok'):
                log("✅ Report 4 ore inviato con successo su Telegram (Chat ID 1723292483).")
                azzera_buffer_report()
                stato["ultimo_report_4ore_ts"] = ora_attuale
                salva_stato(stato)
                return True
    except Exception as eTg:
        log(f"❌ Errore invio report Telegram 4 ore: {eTg}")

    return False


# ═════════════════════════════════════════════════════════════════════════════
# 🔄 4. CICLO MASTER DELL'ORCHESTRATORE (1 OGNI 15 MINUTI ALTERNATO)
# ═════════════════════════════════════════════════════════════════════════════

def esegui_singolo_ciclo(stato):
    """Esegue un singolo ciclo (15 minuti): sceglie se Bot Immagini o Bot Video in base all'alternanza"""
    ciclo = stato.get("ciclo_progressivo", 0) + 1
    prossimo_tipo = stato.get("prossimo_tipo", "IMMAGINE")
    indice_stile = stato.get("indice_stile", 0)

    log("══════════════════════════════════════════════════════════════════════")
    log(f"🚀 AVVIO CICLO #{ciclo} — TIPO: {prossimo_tipo} (Intervallo: 15 min)")
    log("══════════════════════════════════════════════════════════════════════")

    if prossimo_tipo == "IMMAGINE":
        esegui_ciclo_immagini(indice_stile)
        stato["prossimo_tipo"] = "VIDEO"
        stato["indice_stile"] = (indice_stile + 1) % len(STILI_GRAFICI_TABELLA)
    else:
        esegui_ciclo_video_youtube()
        stato["prossimo_tipo"] = "IMMAGINE"

    stato["ciclo_progressivo"] = ciclo
    salva_stato(stato)

    # Verifica se è scoccata la quarta ora per il riassunto unico su Telegram
    verifica_e_invia_report_4ore(stato)

    log(f"✅ Ciclo #{ciclo} completato con successo. Prossimo ciclo ({stato['prossimo_tipo']}) tra 15 minuti.")


def main():
    log("══════════════════════════════════════════════════════════════════════")
    log("🤖 IMMOBILIARE GIANCANI — MASTER ORCHESTRATORE STORIE SOCIAL AVVIATO")
    log("   • Alternanza: 1 ogni 15 minuti (Immagini Multi-Stile <-> Video Archivio YouTube)")
    log("   • 6 Stili Grafici e Immagini Tassativamente DIVERSE ad ogni storia")
    log("   • Canali Social: Facebook Stories (234931856561526) + Instagram Stories (@giancani_immobiliare)")
    log("   • Notifiche Telegram: SILENZIO ASSOLUTO per 15 min -> 1 REPORT OGNI 4 ORE CON SOLO I LINK")
    log("══════════════════════════════════════════════════════════════════════")

    stato = carica_stato()

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        esegui_singolo_ciclo(stato)
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--report-now":
        log("📢 Forzatura invio report 4 ore immediato su Telegram...")
        verifica_e_invia_report_4ore(stato, forza=True)
        return

    while True:
        try:
            esegui_singolo_ciclo(stato)
        except Exception as e:
            log(f"❌ Errore imprevisto nel ciclo dell'orchestratore: {e}")

        log(f"⏳ In attesa di {INTERVALLO_STORIA_SECONDI} secondi (15 minuti)...")
        time.sleep(INTERVALLO_STORIA_SECONDI)


if __name__ == "__main__":
    main()
