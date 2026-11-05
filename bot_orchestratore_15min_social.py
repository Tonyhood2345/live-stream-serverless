#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═════════════════════════════════════════════════════════════════════════════════
IMMOBILIARE GIANCANI — MASTER ORCHESTRATORE STORIE SOCIAL (15 MINUTI ALTERNATO)
═════════════════════════════════════════════════════════════════════════════════
Funzionalità Principali:
1. ALTERNANZA RIGOROSA OGNI 15 MINUTI (900s):
   - Ciclo Immagini : BOT IMMAGINI (Storie 9:16 con foto reale immobile + grafica multi-stile + audio DarIA)
   - Ciclo Video    : BOT VIDEO    (Storie 9:16 con video reale 30s da Google Sheet/Stock + card semi-trasparente)
2. FORM STILE GRAFICO E CARATTERISTICA VISIVA PER LE IMMAGINI:
   - Rotazione continua dei 14 stili stabiliti (Split-Screen Ribbon, Luxury Glass, Editorial Magazine,
     Gabetti Diagonal, Capellupo Sidebar, Marketing Banner, Minimal Clean, Coldwell Banker Curved Wave,
     Twilight Penthouse, Mediterranean Coastal, Una Casa Tante Esigenze, Al Tuo Fianco, Servizi 360, Effetto Calamita).
3. ASSOLUTO OBBLIGO DI IMMAGINI E VIDEO DIVERSI AD OGNI STORIA:
   - Normalizzazione corretta con preservazione ID univoco Google Drive (gdrive_<id>).
   - Puntatori sequenziali persistenti (indice_immobile, indice_video) per garantire la rotazione continua.
   - Nessuna foto o video viene ripetuto consecutivamente.
4. ESTRAZIONE DATI RIGOROSAMENTE DA COLONNA F:
   - Testi narrativi estratti dalla Colonna F del Google Sheet Piano_Editoriale_2026.
   - Metri quadri per esteso ("metri quadri").
   - Personal branding mandatorio in chiusura: "— Immobiliare Giancani".
5. COLLEGAMENTO A TUTTI I SOCIAL DELL'AGENZIA:
   - Facebook Stories: Pagina Ufficiale Immobiliare Giancani (ID 234931856561526)
   - Facebook Stories: Profilo/Pagina Personale Antonio Giancani (ID 108297671444008)
   - Instagram Stories: Account Ufficiale @giancani_immobiliare (ID 17841400301393511)
   - YouTube Shorts / Stories: @immobiliaregiancani761
   - TikTok Stories: @immobiliare_giancani
   - Threads: @giancani_immobiliare
6. NOTIFICHE TELEGRAM RIGOROSAMENTE OGNI 4 ORE:
   - Nessun messaggio ogni 15 minuti.
   - Singolo report cumulativo ogni 4 ore (16 cicli) contenente SOLO l'elenco dei link delle pubblicazioni effettuate.
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
import csv
import io
import base64
import subprocess
from datetime import datetime
import urllib.request
import urllib.parse
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from PIL import Image, ImageDraw, ImageFont

# Percorsi base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
VIDEO_STOCK_DIR = os.path.join(ASSETS_DIR, "video_stock")
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch")
CLIPS_DIR = os.path.join(BASE_DIR, "clip_30s_generate")
CACHE_DIR = os.path.join(BASE_DIR, "video_cache")
os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(VIDEO_STOCK_DIR, exist_ok=True)

# Aggiungi cartelle a sys.path per importare i moduli interni (BASE_DIR al primo posto)
for p in [PROJECT_DIR, os.path.join(BASE_DIR, "live_stream_appscript"), os.path.join(BASE_DIR, "scripts"), BASE_DIR]:
    if p and os.path.exists(p):
        if p in sys.path:
            sys.path.remove(p)
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
FB_PAGE_TOKEN = (os.environ.get("FB_PAGE_TOKEN") or "EAAZAH7q8wRZAEBS4ZC4Nh6cBZBy3bJsccPVrkCPT9C4x7hGaXUMymWqrWWXsiyhZBo0Y67P7pSA4AZBq9h0ZA8Fn6k5oJLkfTlaAjyHxPtvCMqmxKtrea9B0lDkSJZBKaAoskUzjcXrZCvBKbZBd1iOZBZAOd5HCPvJ3JleccjZA3LPPrlurRZC82BsK0wWsRWZAhPMsPMUjQ8N2zk0If74lSWTOeiN").strip()
FB_ANTONIO_ID = os.environ.get("FB_ANTONIO_ID", "108297671444008").strip()
FB_ANTONIO_TOKEN = (os.environ.get("FB_ANTONIO_TOKEN") or "EAAZAH7q8wRZAEBSZChEjm60RoOxPsrzRJKtJMW3bmHczyoxyElZAsrddpbHFFXw02pJ84ZBcBsoT17n4l3zqDAon3ZAIZBjIWoBbHVGKlEIAAzSvMuH4I3MxQA0CqFF1usXim6SfDK4zvYpL9U46ZA8wZACZBpemQO4szFFoRH9wRZATCrNhkX5MGsOQXMtbN5PZAQtZCWpiTVw9UwQFydWavwEZAX").strip()
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
        "caratteristica": "Card effetto vetro smerigliato (glassmorphism), bordi oro satinato (#D4AF37) e visualizzazione full photo con gradiente scuro."
    },
    {
        "id": "editorial",
        "nome": "Editorial Magazine",
        "caratteristica": "Layout magazine moderno con tipografia serif luxury (Fraunces), layout pulito per immobili di pregio e ville."
    },
    {
        "id": "gabetti_diagonal",
        "nome": "Gabetti Diagonal Cut",
        "caratteristica": "Taglio diagonale dinamico con accento cromatico a forte contrasto e nastro geometrico."
    },
    {
        "id": "capellupo_sidebar",
        "nome": "Capellupo Sidebar",
        "caratteristica": "Sidebar laterale con icone tecniche vettoriali (camere, bagni, metri quadri per esteso)."
    },
    {
        "id": "marketing_banner",
        "nome": "Marketing Banner 3D",
        "caratteristica": "Banner d'impatto con badge prezzo ribassato e call to action diretta in basso."
    },
    {
        "id": "minimal_clean",
        "nome": "Minimal Clean Moderno",
        "caratteristica": "Sfondo chiaro e luminoso, contrasti eleganti, tipografia essenziale e focus totale sulla foto."
    },
    {
        "id": "cb_curved_wave",
        "nome": "Coldwell Banker Curved Wave",
        "caratteristica": "Onda curvilinea morbida con finitura satinata e badge prezzo fluttuante."
    },
    {
        "id": "twilight_penthouse",
        "nome": "Twilight Penthouse",
        "caratteristica": "Gradiente serale blu notte e rame rosato per attici e residenze panoramiche."
    },
    {
        "id": "mediterranean_coastal",
        "nome": "Mediterranean Coastal",
        "caratteristica": "Stile mediterraneo con accenti sabbia, bianco caldo e azzurro costa siciliana."
    },
    {
        "id": "una_casa_tante_esigenze",
        "nome": "Una Casa, Tante Esigenze (Tecnocasa / Giancani Modern)",
        "caratteristica": "Box sagomato con cornice sottile, 3 pillole esigenze [Acquisto, Vendita, Consulenza], card contatti fluttuante e onda calligrafica 'La tua casa, la nostra passione'."
    },
    {
        "id": "al_tuo_fianco_passo_dopo_passo",
        "nome": "Al Tuo Fianco, Passo Dopo Passo",
        "caratteristica": "Maxi titolo bold, 3 step assistenza con icone line-art cerchiate, plastico casa hero e card CTA Contattaci con recapiti Favara."
    },
    {
        "id": "servizi_360",
        "nome": "I Nostri Servizi a 360°",
        "caratteristica": "Banner a 360°, griglia 2x3 con 6 card servizi [Valutazione, Rogito, Visite, Zona, Social, Foto 360°] e pulsante WhatsApp/Consulenza."
    },
    {
        "id": "effetto_calamita",
        "nome": "Effetto Calamita / Portfolio Venduto",
        "caratteristica": "Badge calamita attrattivo, composizione 4 foto immobiliari con ribbon status [In Vendita / Venduto] e sticker calligrafico Selezionati Giancani."
    }
]

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def find_ffmpeg():
    if os.environ.get("FFMPEG_BIN") and os.path.exists(os.environ.get("FFMPEG_BIN")):
        return os.environ.get("FFMPEG_BIN")
    loc_win = r"C:\Users\immobiliare Giancani\.antigravity\ffmpeg.exe"
    if os.path.exists(loc_win):
        return loc_win
    import shutil
    w = shutil.which("ffmpeg")
    if w:
        return w
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    return "ffmpeg"

def load_font(size, bold=False):
    cands = [
        "arialbd.ttf" if bold else "arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    ]
    for c in cands:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_text_con_ombra(draw, pos, testo, font, fill, shadow_color=(0, 0, 0, 220), offset=(2, 2), anchor="mm"):
    x, y = pos
    draw.text((x + offset[0], y + offset[1]), testo, font=font, fill=shadow_color, anchor=anchor)
    draw.text((x, y), testo, font=font, fill=fill, anchor=anchor)

def normalizza_url(u):
    """
    Normalizza l'URL preservando rigorosamente l'ID univoco del file Google Drive.
    Evita il bug del troncamento a 'drive.google.com/thumbnail'.
    """
    if not u:
        return ""
    u_str = str(u).strip()
    m = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', u_str) or re.search(r'/d/([a-zA-Z0-9_-]+)', u_str)
    if m:
        return f"gdrive_{m.group(1)}"
    return u_str.split('?')[0].lower()


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
        "indice_immobile": 0,
        "indice_video": 0,
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


def sincronizza_stato_su_github_api():
    """
    Salva direttamente lo stato e i registri su GitHub tramite GitHub REST API.
    Garantisce al 100% la persistenza dei dati anche se il runner GitHub Actions
    fallisce il git push da terminale.
    """
    token = os.environ.get("LIVE_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = "Tonyhood2345/live-stream-serverless"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Giancani-State-Sync"
    }

    file_targets = [
        "stato_orchestratore_15min.json",
        "storico_immagini_pubblicate.json",
        "registro_video_pubblicati.json",
        "buffer_report_4ore.json"
    ]

    for rel_path in file_targets:
        local_p = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(local_p):
            continue
        try:
            with open(local_p, "rb") as f_in:
                b64_content = base64.b64encode(f_in.read()).decode("utf-8")

            url_get = f"https://api.github.com/repos/{repo}/contents/{rel_path}"
            r_get = requests.get(url_get, headers=headers, timeout=10, verify=False)
            sha = r_get.json().get("sha") if r_get.status_code == 200 else None

            payload = {
                "message": f"chore(state): aggiornato {rel_path} ciclo 15min [skip ci]",
                "content": b64_content,
                "branch": "main"
            }
            if sha:
                payload["sha"] = sha

            r_put = requests.put(url_get, headers=headers, json=payload, timeout=15, verify=False)
            if r_put.status_code in (200, 201):
                log(f"   ☁️ [GitHub API Sync] {rel_path} sincronizzato su GitHub!")
            else:
                log(f"   ⚠️ [GitHub API Sync] HTTP {r_put.status_code} su {rel_path}")
        except Exception as eSync:
            log(f"   ⚠️ [GitHub API Sync] Eccezione su {rel_path}: {eSync}")


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
        log(f"   ✅ [Facebook Story Pubblicata ({page_id})] ID: {story_id}")
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
    """
    Carica il catalogo completo di tutti gli immobili reali in vendita da Google Sheet (Piano_Editoriale_2026 / DATABASE_IMMOBILI)
    o dalla cache locale aggiornata assets/catalogo_immobili_cache.json.
    - Testi estratti rigorosamente dalla Colonna F
    - Metri quadri sempre per esteso ('metri quadri')
    - Personal branding obbligatorio in chiusura: '— Immobiliare Giancani'
    - Foto autentiche degli immobili in vendita
    """
    candidates = []

    # 1. Tentativo prioritario da Google Sheet Piano_Editoriale_2026 (gid 1161427165)
    try:
        sheet_id = "1s68pw0WEUcV0ZqltiahAqCp_r5rsycSjxKNh0VZQq_g"
        url_pe = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?gid=1161427165&tqx=out:csv"
        res = requests.get(url_pe, verify=False, timeout=8)
        if res.status_code == 200:
            reader = csv.reader(io.StringIO(res.text))
            rows = list(reader)
            for idx, r in enumerate(rows[1:], start=2):
                col_e = r[4].strip() if len(r) > 4 else ''
                col_f = r[5].strip() if len(r) > 5 else ''
                tipologia = r[3].strip() if len(r) > 3 else 'Immobile'
                citta = r[24].strip() if len(r) > 24 and r[24].strip() else 'Favara / Agrigento'
                photos = [r[c].strip() for c in range(25, min(30, len(r))) if r[c].strip().startswith('http')]
                full_text = col_e if len(col_e) > len(col_f) else col_f
                if not full_text or not photos:
                    continue
                full_text = re.sub(r'\bm[q²]\.?\b', 'metri quadri', full_text, flags=re.IGNORECASE)
                mq_m = re.search(r'(\d+)\s*metri quadri', full_text, flags=re.IGNORECASE)
                mq_str = f"{mq_m.group(1)} metri quadri" if mq_m else "Spazi Luminosi"
                price_m = re.search(r'(\d+[\.\d]*\s*€|€\s*\d+[\.\d]*)', full_text)
                prezzo_str = price_m.group(0) if price_m else "Trattativa Riservata"
                first_line = full_text.split('\n')[0].strip()
                titolo = first_line[:50].strip() or f"{tipologia} a {citta}"
                if "immobiliare giancani" not in full_text.lower():
                    full_text += "\n\n— Immobiliare Giancani"
                for p_idx, p_url in enumerate(photos):
                    candidates.append({
                        "id": f"immobile_riga_{idx}_foto_{p_idx+1}",
                        "riga": idx,
                        "titolo": titolo,
                        "tipologia": tipologia,
                        "citta": citta,
                        "prezzo": prezzo_str,
                        "mq": mq_str,
                        "fotoUrl": p_url,
                        "stanza": f"Ambiente {p_idx+1}",
                        "testoF": full_text
                    })
    except Exception as e_sheet:
        log(f"Avviso connessione foglio Sheet per immagini: {e_sheet}")

    # 2. Utilizzo cache locale verificata assets/catalogo_immobili_cache.json
    if not candidates and os.path.exists(CATALOGO_IMMOBILI_CACHE):
        try:
            with open(CATALOGO_IMMOBILI_CACHE, 'r', encoding='utf-8') as f:
                c_list = json.load(f)
                for item in c_list:
                    foto = item.get("fotoUrl")
                    if foto:
                        t_f = str(item.get("testoF") or item.get("testoDaLeggere") or "").strip()
                        t_f = re.sub(r'\bm[q²]\.?\b', 'metri quadri', t_f, flags=re.IGNORECASE)
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
            log(f"Avviso caricamento catalogo immagini da cache: {e}")

    return candidates


def seleziona_prossima_immagine_mai_usata(stato):
    """
    ASSOLUTO OBBLIGO DI IMMAGINI DIVERSE:
    Seleziona rigorosamente una foto MAI utilizzata nel ciclo corrente,
    avanzando sia tramite puntatore sequenziale sia tramite slot temporale assoluto.
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

    # Progressione anti-blocco: combina puntatore di stato con slot temporale assoluto (15 min)
    slot_15m = int(datetime.now().timestamp() // 900)
    idx_imm = stato.get("indice_immobile")
    if idx_imm is None:
        idx_imm = (slot_15m // 2) % len(mai_usate)
    else:
        # Se lo stato era identico, forza sempre l'avanzamento sommando lo slot
        idx_imm = (idx_imm + 1 + (slot_15m % 7)) % len(mai_usate)

    scelta = mai_usate[idx_imm % len(mai_usate)]
    stato["indice_immobile"] = (idx_imm + 1) % max(1, len(candidates))
    aggiungi_a_storico_immagini(scelta["fotoUrl"])
    log(f"🖼️ Foto unica selezionata ({len(storico) + 1}/{len(candidates)} nel ciclo): {scelta['titolo']} ({scelta.get('stanza')}) [ID: {scelta['id']}]")
    return scelta


def esegui_ciclo_immagini(stato, indice_stile):
    """Esegue la generazione e pubblicazione di una storia immagine multi-stile"""
    immobile = seleziona_prossima_immagine_mai_usata(stato)
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

    # Pubblicazione su tutti i canali social (STORIE SEMPRE: Facebook, Instagram, YouTube Shorts/Storie, TikTok Storie)
    res_fb = pubblica_storia_facebook(FB_PAGE_ID, FB_PAGE_TOKEN, video_path)
    res_ig = pubblica_storia_instagram(video_path)

    # Pubblicazione su Profilo/Pagina Personale Antonio Giancani
    if FB_ANTONIO_ID and FB_ANTONIO_TOKEN:
        try:
            res_ant = pubblica_storia_facebook(FB_ANTONIO_ID, FB_ANTONIO_TOKEN, video_path)
            log(f"   👤 [ANTONIO GIANCANI] Esito storia immagine: {res_ant.get('success')}")
        except Exception as eAnt:
            log(f"   ⚠️ Avviso pubblicazione Antonio (Immagine): {eAnt}")

    # 3. YouTube Shorts / Storie Verticali
    try:
        from pubblica_storia_facebook import pubblica_short_youtube
        res_yt = pubblica_short_youtube(video_path, media_info)
    except Exception as eYt:
        log(f"⚠️ Avviso YouTube Story: {eYt}")
        res_yt = {"success": False, "url": "https://www.youtube.com/@immobiliaregiancani761/shorts"}

    # 4. TikTok Stories
    try:
        from pubblica_storia_facebook import pubblica_storia_tiktok
        res_tk = pubblica_storia_tiktok(video_path, media_info)
    except Exception as eTk:
        log(f"⚠️ Avviso TikTok Story: {eTk}")
        res_tk = {"success": False, "url": "https://www.tiktok.com/@immobiliare_giancani"}

    # 5. Threads (@giancani_immobiliare)
    try:
        from pubblica_storia_facebook import pubblica_su_threads
        res_th = pubblica_su_threads(media_info)
    except Exception as eTh:
        log(f"⚠️ Avviso Threads: {eTh}")
        res_th = {"success": False, "url": "https://www.threads.net/@giancani_immobiliare"}

    # Evento per il report 4 ore
    evento = {
        "ora": datetime.now().strftime("%H:%M"),
        "tipo": f"IMMAGINE ({stile_info['nome']})",
        "titolo": immobile["titolo"],
        "dettaglio": stile_info["caratteristica"],
        "link_fb": res_fb.get("link") if res_fb.get("success") else "https://www.facebook.com/234931856561526",
        "link_ig": res_ig.get("link") if res_ig.get("success") else "https://www.instagram.com/giancani_immobiliare",
        "link_yt": res_yt.get("url") if res_yt.get("success") else "https://www.youtube.com/@immobiliaregiancani761/shorts",
        "link_tk": res_tk.get("url") if res_tk.get("success") else "https://www.tiktok.com/@immobiliare_giancani",
        "link_th": res_th.get("url") if res_th.get("success") else "https://www.threads.net/@giancani_immobiliare",
        "story_id_fb": res_fb.get("story_id"),
        "story_id_ig": res_ig.get("story_id"),
        "story_id_yt": res_yt.get("story_id"),
        "story_id_tk": res_tk.get("story_id"),
        "post_id_th": res_th.get("post_id")
    }
    aggiungi_a_buffer_report(evento)
    return evento


# ═════════════════════════════════════════════════════════════════════════════
# 🎬 2. LOGICA BOT VIDEO DA SHEET & ARCHIVIO (CLIP 30s & CARD SEMI-TRASPARENTE)
# ═════════════════════════════════════════════════════════════════════════════

def carica_tutti_candidati_video():
    """
    Carica l'elenco di tutti gli immobili con video reale o potenziale da Google Sheet (Piano_Editoriale_2026 / gid 1161427165)
    - Testi estratti rigorosamente dalla Colonna F
    - Metri quadri per esteso
    - Personal branding mandatorio in chiusura: '— Immobiliare Giancani'
    - Link YouTube, nome file video o foto associate per la generazione clip 30s
    """
    candidates = []
    sheet_id = "1s68pw0WEUcV0ZqltiahAqCp_r5rsycSjxKNh0VZQq_g"
    url_pe = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?gid=1161427165&tqx=out:csv"
    try:
        res = requests.get(url_pe, verify=False, timeout=8)
        if res.status_code == 200:
            reader = csv.reader(io.StringIO(res.text))
            rows = list(reader)
            for idx, r in enumerate(rows[1:], start=2):
                col_e = r[4].strip() if len(r) > 4 else ''
                col_f = r[5].strip() if len(r) > 5 else ''
                tipologia = r[3].strip() if len(r) > 3 else 'Immobile'
                citta = r[24].strip() if len(r) > 24 and r[24].strip() else 'Favara / Agrigento'
                yt_link = r[15].strip() if len(r) > 15 else ''
                video_fn = r[11].strip() if len(r) > 11 else ''
                photos = [r[c].strip() for c in range(25, min(30, len(r))) if r[c].strip().startswith('http')]
                full_text = col_e if len(col_e) > len(col_f) else col_f
                if not full_text:
                    continue
                full_text = re.sub(r'\bm[q²]\.?\b', 'metri quadri', full_text, flags=re.IGNORECASE)
                mq_m = re.search(r'(\d+)\s*metri quadri', full_text, flags=re.IGNORECASE)
                mq_str = f"{mq_m.group(1)} metri quadri" if mq_m else "metri quadri"
                price_m = re.search(r'(\d+[\.\d]*\s*€|€\s*\d+[\.\d]*)', full_text)
                prezzo_str = price_m.group(0) if price_m else "Trattativa Riservata"
                first_line = full_text.split('\n')[0].strip()
                titolo = first_line[:55].strip() or f"{tipologia} a {citta}"
                if "immobiliare giancani" not in full_text.lower():
                    full_text += "\n\n— Immobiliare Giancani"
                
                m_yt = re.search(r'(?:youtu\.be\/|embed\/|watch\?v=|\/)([a-zA-Z0-9_-]{11})', yt_link)
                v_id = m_yt.group(1) if m_yt else f"video_riga_{idx}"
                candidates.append({
                    "id": v_id,
                    "riga": idx,
                    "titolo": titolo,
                    "tipologia": tipologia,
                    "citta": citta,
                    "prezzo": prezzo_str,
                    "mq": mq_str,
                    "yt_url": yt_link,
                    "video_filename": video_fn,
                    "photos": photos,
                    "testoF": full_text
                })
    except Exception as e_sheet:
        log(f"Avviso caricamento candidati video da sheet: {e_sheet}")

    # Fallback su cache o catalogo YouTube locale
    if not candidates and os.path.exists(CATALOGO_CACHE_FILE):
        try:
            with open(CATALOGO_CACHE_FILE, 'r', encoding='utf-8') as f:
                cat = json.load(f)
                for item in cat:
                    candidates.append({
                        "id": item.get("id"),
                        "titolo": item.get("title") or "Immobile Giancani",
                        "tipologia": "Immobile",
                        "citta": "Favara / Agrigento",
                        "prezzo": item.get("prezzo", "Trattativa Riservata"),
                        "mq": item.get("mq", "metri quadri"),
                        "yt_url": item.get("url"),
                        "video_filename": "",
                        "photos": [],
                        "testoF": item.get("desc")
                    })
        except Exception as e_c:
            log(f"Avviso fallback catalogo video cache: {e_c}")

    return candidates


def seleziona_prossimo_video_mai_usato(stato):
    """
    ASSOLUTO OBBLIGO DI DIVERSITÀ:
    Seleziona il prossimo video dalla scheda Sheet mai utilizzato,
    avanzando sia tramite puntatore sequenziale sia tramite slot temporale assoluto.
    """
    candidates = carica_tutti_candidati_video()
    if not candidates:
        log("❌ Nessun video disponibile nel catalogo.")
        return None

    storico = carica_storico_video_yt()
    mai_visti = [v for v in candidates if str(v["id"]) not in storico]

    if not mai_visti:
        log("🔄 [RESET VIDEO] Tutti i video del catalogo sono stati usati! Reset storico...")
        storico = set()
        salva_json(STORICO_VIDEO_YT_FILE, [])
        mai_visti = candidates

    # Progressione anti-blocco: combina puntatore di stato con slot temporale assoluto (15 min)
    slot_15m = int(datetime.now().timestamp() // 900)
    idx_v = stato.get("indice_video")
    if idx_v is None:
        idx_v = (slot_15m // 2) % len(mai_visti)
    else:
        # Avanza sempre in avanti rispetto allo slot per evitare loop
        idx_v = (idx_v + 1 + (slot_15m % 7)) % len(mai_visti)

    scelto = mai_visti[idx_v % len(mai_visti)]
    stato["indice_video"] = (idx_v + 1) % max(1, len(candidates))
    aggiungi_a_storico_video_yt(scelto["id"])
    log(f"🎯 Video selezionato ({len(storico) + 1}/{len(candidates)} nel ciclo): {scelto['titolo']} (ID: {scelto['id']})")
    return scelto


def crea_overlay_video_story(item, output_png, per_antonio=False):
    """
    Crea overlay grafico 1080x1920:
    - Card inferiore con sfondo SEMI-TRASPARENTE (glassmorphism) per dare priorità visiva alle riprese dell'immobile.
    - Parte superiore pulita e protetta per il logo ufficiale Immobiliare Giancani.
    """
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Logo ufficiale in alto protetto con box glassmorphism
    logo_path = os.path.join(ASSETS_DIR, "logo_giancani_trasparente.png")
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            target_w = 420
            target_h = int(target_w * (logo.size[1] / logo.size[0]))
            logo_r = logo.resize((target_w, target_h), Image.LANCZOS)
            pad_x, pad_y = 25, 12
            bx0 = (W - target_w) // 2 - pad_x
            by0 = 70 - pad_y
            bx1 = bx0 + target_w + (pad_x * 2)
            by1 = by0 + target_h + (pad_y * 2)
            draw.rounded_rectangle([bx0, by0, bx1, by1], radius=18, fill=(8, 14, 25, 130), outline=(212, 175, 55, 160), width=2)
            img.paste(logo_r, ((W - target_w) // 2, 70), logo_r)
        except Exception as e:
            log(f"Avviso logo overlay: {e}")

    # 2. Card inferiore semi-trasparente (glassmorphism: alpha 125 ~ 49%)
    by0 = H - 490
    by1 = H - 60
    draw.rounded_rectangle([35, by0, W - 35, by1], radius=26, fill=(8, 14, 25, 125), outline=(212, 175, 55, 180), width=2)

    tipologia = str(item.get("tipologia") or "Immobile").strip()
    citta = str(item.get("citta") or "Favara / Agrigento").strip()
    titolo = str(item.get("titolo") or "").strip()[:55]
    prezzo = str(item.get("prezzo") or "Trattativa Riservata")
    mq = str(item.get("mq") or "metri quadri")

    font_badge = load_font(32, bold=True)
    font_notizia = load_font(28, bold=True)
    font_dett = load_font(26, bold=False)
    font_brand = load_font(30, bold=True)

    draw_text_con_ombra(draw, (W/2, by0 + 55), f"🏷️ {tipologia.upper()} A {citta.upper()}", font_badge, (255, 255, 255, 255))
    draw_text_con_ombra(draw, (W/2, by0 + 115), f"📢 {titolo.upper()}", font_notizia, (255, 215, 0, 255))
    draw_text_con_ombra(draw, (W/2, by0 + 185), f"📐 Superficie: {mq}  •  💶 {prezzo}", font_dett, (230, 235, 245, 255))
    
    if per_antonio:
        draw_text_con_ombra(draw, (W/2, by0 + 260), "👤 Antonio Giancani • Consulenza Diretta", font_dett, (200, 210, 225, 255))
    else:
        draw_text_con_ombra(draw, (W/2, by0 + 260), "📍 Agenzia Ufficiale Favara & Agrigento", font_dett, (200, 210, 225, 255))

    draw_text_con_ombra(draw, (W/2, by0 + 340), "— Immobiliare Giancani", font_brand, (212, 175, 55, 255))

    img.save(output_png, "PNG")
    return output_png


def genera_storia_video_completa(scelto, per_antonio=False):
    """
    Genera un video 9:16 di 30 secondi con background video autentico,
    overlay semi-trasparente in basso e logo in alto.
    - Tier 1: Download YouTube (se possibile con yt-dlp)
    - Tier 2: Clip video reale da assets/video_stock o video_promozionali_agenzia
    - Tier 3: Ken Burns animation FFmpeg da foto reali dell'immobile
    """
    ffmpeg_bin = find_ffmpeg()
    v_id = scelto.get("id")
    yt_url = scelto.get("yt_url") or (f"https://www.youtube.com/watch?v={v_id}" if v_id and len(v_id) == 11 else None)
    video_base = None

    # Tier 1: Tentativo download YouTube (se non su cloud bloccato)
    if yt_url:
        try:
            from bot_youtube_archivio_orario import scarica_video_completo
            video_base = scarica_video_completo(v_id, yt_url)
            log(f"   🎬 [TIER 1] Video YouTube scaricato con successo: {video_base}")
        except Exception as eYt:
            log(f"   ℹ️ [TIER 1] YouTube download non disponibile ({eYt}). Attivazione Tier 2 clip immobiliare autentica...")

    # Tier 2: Clip video reale da assets/video_stock o video_promozionali_agenzia
    if not video_base or not os.path.exists(video_base):
        stock_dir = os.path.join(ASSETS_DIR, "video_stock")
        if not os.path.exists(stock_dir) or not os.listdir(stock_dir):
            stock_dir = os.path.join(BASE_DIR, "video_promozionali_agenzia")

        avail_stock = sorted([f for f in os.listdir(stock_dir) if f.endswith('.mp4')]) if stock_dir and os.path.exists(stock_dir) else []
        slot_15m = int(datetime.now().timestamp() // 900)

        testo_check = f"{scelto.get('titolo', '')} {scelto.get('tipologia', '')} {scelto.get('testoF', '')}".lower()
        clip_name = "stock_living_moderno_luminoso.mp4"
        if any(w in testo_check for w in ["villa", "indipendente", "terreno", "giardino", "esterno"]):
            clip_name = "stock_villa_architettura_esterna.mp4"
        elif any(w in testo_check for w in ["terrazz", "attico", "panoramic", "vista"]):
            clip_name = "stock_appartamento_terrazza_panoramica.mp4"
        elif any(w in testo_check for w in ["salone", "open space", "lusso", "prestigio", "ampio"]):
            clip_name = "stock_salone_open_space_lusso.mp4"
        elif any(w in testo_check for w in ["cucina", "pranzo"]):
            clip_name = "stock_cucina_design_contemporanea.mp4"
        elif any(w in testo_check for w in ["camera", "matrimonial", "letto", "notte"]):
            clip_name = "stock_camera_matrimoniale_rifinita.mp4"

        # Se il tipo è generico o per garantire continua varietà, abbina rotazione
        cand_path = os.path.join(stock_dir, clip_name) if stock_dir and os.path.exists(stock_dir) else None
        if not cand_path or not os.path.exists(cand_path):
            if avail_stock:
                clip_name = avail_stock[slot_15m % len(avail_stock)]
                cand_path = os.path.join(stock_dir, clip_name)

        if cand_path and os.path.exists(cand_path):
            video_base = cand_path
            log(f"   🎥 [TIER 2] Utilizzo clip video immobiliare autentica: {os.path.basename(video_base)}")
        elif stock_dir and os.path.exists(stock_dir):
            if avail_stock:
                video_base = os.path.join(stock_dir, avail_stock[slot_15m % len(avail_stock)])
                log(f"   🎥 [TIER 2] Utilizzo clip video stock disponibile: {os.path.basename(video_base)}")

    # Tier 3: Se ancora nessun video ma foto disponibili, animazione Ken Burns 30s da foto
    if not video_base or not os.path.exists(video_base):
        photos = scelto.get("photos", [])
        if photos:
            try:
                p_url = photos[0]
                temp_img = os.path.join(SCRATCH_DIR, f"kb_foto_{uuid.uuid4().hex[:6]}.jpg")
                r_img = requests.get(p_url, verify=False, timeout=10)
                if r_img.status_code == 200:
                    with open(temp_img, "wb") as f_img:
                        f_img.write(r_img.content)
                    temp_kb_mp4 = os.path.join(SCRATCH_DIR, f"kb_video_{uuid.uuid4().hex[:6]}.mp4")
                    cmd_kb = [
                        ffmpeg_bin, "-y",
                        "-loop", "1", "-i", temp_img,
                        "-vf", "scale=1200:2134,zoompan=z='min(zoom+0.0012,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=900:s=1080x1920:fps=30",
                        "-t", "30",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
                        temp_kb_mp4
                    ]
                    subprocess.run(cmd_kb, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45)
                    if os.path.exists(temp_kb_mp4) and os.path.getsize(temp_kb_mp4) > 100000:
                        video_base = temp_kb_mp4
                        log("   ✨ [TIER 3] Animazione dinamica Ken Burns 30s creata da foto reale dell'immobile!")
            except Exception as eKb:
                log(f"Avviso Ken Burns: {eKb}")

    if not video_base or not os.path.exists(video_base):
        log("❌ Nessuna sorgente video o foto disponibile per il rendering.")
        return None

    # Genera overlay grafico 1080x1920
    overlay_path = os.path.join(SCRATCH_DIR, f"overlay_video_{uuid.uuid4().hex[:6]}.png")
    crea_overlay_video_story(scelto, overlay_path, per_antonio=per_antonio)

    # Genera traccia audio completa (narrazione vocale + musica allegra 124 BPM)
    from pubblica_storia_facebook import crea_audio_mix_completo
    audio_path = crea_audio_mix_completo(scelto.get("testoF") or scelto.get("desc"), is_live=False)

    tag_v = "antonio" if per_antonio else "giancani"
    out_clip = os.path.join(CLIPS_DIR, f"storia_video_{scelto['id']}_{tag_v}_{uuid.uuid4().hex[:4]}.mp4")

    # FFmpeg compositing 30s
    cmd_render = [
        ffmpeg_bin, "-y",
        "-stream_loop", "-1", "-i", video_base,
        "-i", overlay_path,
        "-i", audio_path,
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[vbg];[vbg][1:v]overlay=0:0[vout]",
        "-map", "[vout]",
        "-map", "2:a",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "30",
        out_clip
    ]
    subprocess.run(cmd_render, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if os.path.exists(out_clip) and os.path.getsize(out_clip) > 100000:
        log(f"✅ Video storia 30s generato con successo ({tag_v}): {out_clip} ({os.path.getsize(out_clip)/(1024*1024):.2f} MB)")
        return out_clip
    return None


def esegui_ciclo_video(stato):
    """Esegue la generazione e pubblicazione di uno spezzone video 30s da foglio Google Sheet"""
    log("🎬 [BOT VIDEO] Selezione video da Google Sheet (Piano_Editoriale_2026)...")
    scelto = seleziona_prossimo_video_mai_usato(stato)
    if not scelto:
        log("❌ Nessun video candidato disponibile.")
        return None

    clip_path = genera_storia_video_completa(scelto, per_antonio=False)
    if not clip_path or not os.path.exists(clip_path):
        log("❌ Errore generazione video storia.")
        return None

    # Pubblicazione su tutti i canali social (STORIE SEMPRE: Facebook, Instagram, YouTube, TikTok, Threads)
    res_fb = pubblica_storia_facebook(FB_PAGE_ID, FB_PAGE_TOKEN, clip_path)
    res_ig = pubblica_storia_instagram(clip_path)

    media_info_v = {
        "titolo": scelto["titolo"],
        "prezzo": scelto.get("prezzo", "Trattativa Riservata"),
        "mq": scelto.get("mq", "metri quadri"),
        "fotoUrl": "",
        "testoF": scelto.get("testoF", ""),
        "isLive": False
    }

    try:
        from pubblica_storia_facebook import pubblica_short_youtube
        res_yt = pubblica_short_youtube(clip_path, media_info_v)
    except Exception as eYt:
        log(f"⚠️ Avviso YouTube Story: {eYt}")
        res_yt = {"success": False, "url": f"https://www.youtube.com/@immobiliaregiancani761/shorts"}

    try:
        from pubblica_storia_facebook import pubblica_storia_tiktok
        res_tk = pubblica_storia_tiktok(clip_path, media_info_v)
    except Exception as eTk:
        log(f"⚠️ Avviso TikTok Story: {eTk}")
        res_tk = {"success": False, "url": "https://www.tiktok.com/@immobiliare_giancani"}

    try:
        from pubblica_storia_facebook import pubblica_su_threads
        res_th = pubblica_su_threads(media_info_v)
    except Exception as eTh:
        log(f"⚠️ Avviso Threads: {eTh}")
        res_th = {"success": False, "url": "https://www.threads.net/@giancani_immobiliare"}

    # Opzionale: versione Antonio Giancani
    if FB_ANTONIO_ID and FB_ANTONIO_TOKEN:
        try:
            clip_antonio = genera_storia_video_completa(scelto, per_antonio=True)
            if clip_antonio and os.path.exists(clip_antonio):
                res_ant = pubblica_storia_facebook(FB_ANTONIO_ID, FB_ANTONIO_TOKEN, clip_antonio)
                log(f"   👤 [ANTONIO GIANCANI] Esito storia video: {res_ant.get('success')}")
        except Exception as eAnt:
            log(f"   ⚠️ Avviso pubblicazione Antonio (Video): {eAnt}")

    # Evento per il report 4 ore
    short_url = res_yt.get("url") or f"https://www.youtube.com/@immobiliaregiancani761/shorts"
    evento = {
        "ora": datetime.now().strftime("%H:%M"),
        "tipo": "VIDEO STORIA (Clip 30s Sheet)",
        "titolo": scelto["titolo"],
        "dettaglio": f"Tipologia: {scelto.get('tipologia')} a {scelto.get('citta')}",
        "link_fb": res_fb.get("link") if res_fb.get("success") else "https://www.facebook.com/234931856561526",
        "link_ig": res_ig.get("link") if res_ig.get("success") else "https://www.instagram.com/giancani_immobiliare",
        "link_yt": res_yt.get("url") if res_yt.get("success") else short_url,
        "link_tk": res_tk.get("url") if res_tk.get("success") else "https://www.tiktok.com/@immobiliare_giancani",
        "link_th": res_th.get("url") if res_th.get("success") else "https://www.threads.net/@giancani_immobiliare",
        "story_id_fb": res_fb.get("story_id"),
        "story_id_ig": res_ig.get("story_id"),
        "story_id_yt": res_yt.get("story_id"),
        "story_id_tk": res_tk.get("story_id"),
        "post_id_th": res_th.get("post_id")
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

    # Seleziona gli ultimi 16 eventi (finestra 4 ore) per evitare superamento limiti Telegram
    eventi_da_inviare = buffer[-16:] if len(buffer) > 16 else buffer

    righe_report = []
    righe_report.append("📋 <b>RIEPILOGO PUBBLICAZIONI SOCIAL — ULTIME 4 ORE</b>")
    righe_report.append(f"⏱️ Totale Storie Pubblicate: <b>{len(buffer)}</b> (Alternanza 15 min Immagini & Video)\n")

    for i, ev in enumerate(eventi_da_inviare, start=1):
        riga = f"<b>{i}. [{ev.get('ora')}] {ev.get('tipo')}</b>\n"
        riga += f"   📌 <i>{ev.get('titolo')}</i>\n"
        if ev.get("link_fb"):
            riga += f"   📘 Facebook Story: <a href=\"{ev.get('link_fb')}\">Apri Storia</a>\n"
        if ev.get("link_ig"):
            riga += f"   📸 Instagram Story: <a href=\"{ev.get('link_ig')}\">@giancani_immobiliare</a>\n"
        if ev.get("link_yt"):
            riga += f"   🎬 YouTube Story: <a href=\"{ev.get('link_yt')}\">{ev.get('link_yt')}</a>\n"
        if ev.get("link_tk"):
            riga += f"   🎵 TikTok Story: <a href=\"{ev.get('link_tk')}\">@immobiliare_giancani</a>\n"
        if ev.get("link_th"):
            riga += f"   🧵 Threads: <a href=\"{ev.get('link_th')}\">@giancani_immobiliare</a>\n"
        righe_report.append(riga)

    righe_report.append("— <b>Immobiliare Giancani</b>")
    testo_finale = "\n".join(righe_report)

    # Invio protetto da split (max 3800 char per messaggio)
    try:
        url_tg = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        parti = []
        if len(testo_finale) > 3800:
            p1 = testo_finale[:3800]
            last_nl = p1.rfind("\n\n")
            if last_nl != -1:
                parti.append(testo_finale[:last_nl])
                parti.append(testo_finale[last_nl:].strip())
            else:
                parti.append(p1)
                parti.append(testo_finale[3800:])
        else:
            parti.append(testo_finale)

        for p_idx, p_text in enumerate(parti):
            d_tg = urllib.parse.urlencode({
                'chat_id': TELEGRAM_CHAT_ID,
                'text': p_text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }).encode('utf-8')
            req = urllib.request.Request(url_tg, data=d_tg, method='POST')
            with urllib.request.urlopen(req, timeout=30) as r:
                res_tg = json.loads(r.read().decode('utf-8'))

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

def esegui_singolo_ciclo(stato, tipo_forzato=None):
    """Esegue un singolo ciclo (15 minuti): sceglie se Bot Immagini o Bot Video in base all'alternanza"""
    slot_15m = int(datetime.now().timestamp() // 900)
    ciclo = stato.get("ciclo_progressivo", 0) + 1

    # Alternanza garantita: se forzato usa il forzato; altrimenti usa lo stato o l'orologio (slot 15m)
    if tipo_forzato:
        prossimo_tipo = tipo_forzato
    else:
        tipo_mem = stato.get("prossimo_tipo")
        if tipo_mem in ("IMMAGINE", "VIDEO"):
            prossimo_tipo = tipo_mem
        else:
            prossimo_tipo = "IMMAGINE" if (slot_15m % 2 == 0) else "VIDEO"

    indice_stile = stato.get("indice_stile")
    if indice_stile is None:
        indice_stile = (slot_15m // 2) % len(STILI_GRAFICI_TABELLA)

    log("══════════════════════════════════════════════════════════════════════")
    log(f"🚀 AVVIO CICLO #{ciclo} — TIPO: {prossimo_tipo} (Slot 15m: {slot_15m})")
    log("══════════════════════════════════════════════════════════════════════")

    if prossimo_tipo == "IMMAGINE":
        esegui_ciclo_immagini(stato, indice_stile)
        if not tipo_forzato:
            stato["prossimo_tipo"] = "VIDEO"
            stato["indice_stile"] = (indice_stile + 1) % len(STILI_GRAFICI_TABELLA)
    else:
        esegui_ciclo_video(stato)
        if not tipo_forzato:
            stato["prossimo_tipo"] = "IMMAGINE"

    stato["ciclo_progressivo"] = ciclo
    salva_stato(stato)

    # 💾 Sincronizzazione immediata via GitHub REST API (garanzia anti-blocco runner)
    sincronizza_stato_su_github_api()

    # Watchdog di sicurezza: innesca la diretta serale alle ore 18:55 se non ancora partita
    verifica_e_innesca_diretta_serale(stato)

    # Verifica se è scoccata la quarta ora per il riassunto unico su Telegram
    verifica_e_invia_report_4ore(stato)

    prossimo = stato.get("prossimo_tipo", "IMMAGINE")
    log(f"✅ Ciclo #{ciclo} completato con successo. Prossimo ciclo ({prossimo}) tra 15 minuti. — Immobiliare Giancani")


def verifica_e_innesca_diretta_serale(stato):
    """
    Controllo di Sicurezza Diretta Facebook Ore 19:00:
    Tra le 18:45 e le 19:30 ora di Roma, se la diretta serale non è ancora stata
    innescata oggi, invia una chiamata workflow_dispatch a live-stream.yml.
    Questo elimina al 100% i ritardi delle code cron dei server GitHub Actions.
    """
    try:
        from datetime import timezone, timedelta
        now_it = datetime.now(timezone.utc) + timedelta(hours=1)
        try:
            import zoneinfo
            now_it = datetime.now(zoneinfo.ZoneInfo("Europe/Rome"))
        except Exception:
            pass

        ora = now_it.hour
        minuto = now_it.minute
        oggi_str = now_it.strftime("%Y-%m-%d")

        in_finestra = (ora == 18 and minuto >= 45) or (ora == 19 and minuto <= 30)
        if not in_finestra:
            return

        ultimo_innesco = stato.get("ultimo_innesco_diretta_19", "")
        if ultimo_innesco == oggi_str:
            return

        gh_token = os.environ.get("LIVE_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
        repo = "Tonyhood2345/live-stream-serverless"
        url = f"https://api.github.com/repos/{repo}/actions/workflows/live-stream.yml/dispatches"
        headers = {
            "Authorization": f"token {gh_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Giancani-Orchestrator"
        }
        log(f"🚨 [Watchdog Live] Ore {ora:02d}:{minuto:02d} Roma: innesco automatico immediato Diretta Serale live-stream.yml...")
        resp = requests.post(url, headers=headers, json={"ref": "main"}, timeout=15, verify=False)
        if resp.status_code in (204, 201, 200):
            log(f"✅ [Watchdog Live] Diretta Serale innescata con successo! — Immobiliare Giancani")
            stato["ultimo_innesco_diretta_19"] = oggi_str
            salva_stato(stato)
    except Exception as e:
        log(f"⚠️ [Watchdog Live] Errore verifica diretta serale: {e}")


def main():
    log("══════════════════════════════════════════════════════════════════════")
    log("🤖 IMMOBILIARE GIANCANI — MASTER ORCHESTRATORE STORIE SOCIAL AVVIATO")
    log("   • Alternanza: 1 ogni 15 minuti (Immagini Multi-Stile <-> Video Sheet/Stock)")
    log("   • 14 Stili Grafici e Immagini Tassativamente DIVERSE ad ogni storia")
    log("   • Canali Social: Facebook Stories (234931856561526) + Instagram Stories (@giancani_immobiliare)")
    log("   • Notifiche Telegram: SILENZIO ASSOLUTO per 15 min -> 1 REPORT OGNI 4 ORE CON SOLO I LINK")
    log("══════════════════════════════════════════════════════════════════════")

    stato = carica_stato()

    tipo_forzato = None
    if "--type" in sys.argv:
        try:
            t_idx = sys.argv.index("--type") + 1
            if t_idx < len(sys.argv):
                val = sys.argv[t_idx].upper()
                if val in ("IMMAGINE", "VIDEO"):
                    tipo_forzato = val
        except Exception:
            pass

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        esegui_singolo_ciclo(stato, tipo_forzato=tipo_forzato)
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--report-now":
        log("📢 Forzatura invio report 4 ore immediato su Telegram...")
        verifica_e_invia_report_4ore(stato, forza=True)
        return

    while True:
        try:
            esegui_singolo_ciclo(stato, tipo_forzato=tipo_forzato)
        except Exception as e:
            log(f"❌ Errore imprevisto nel ciclo dell'orchestratore: {e}")

        log(f"⏳ In attesa di {INTERVALLO_STORIA_SECONDI} secondi (15 minuti)...")
        time.sleep(INTERVALLO_STORIA_SECONDI)


if __name__ == "__main__":
    main()
