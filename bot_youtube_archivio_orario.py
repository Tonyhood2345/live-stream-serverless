#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 BOT COMPLETO PERPETUO: ARCHIVIO YOUTUBE 1 ANNO -> DRIVE/LOCALE -> CLIP 30s GRAFICHE -> PUBBLICAZIONE 1 OGNI ORA
Brand: Immobiliare Giancani & Antonio Giancani
Canali:
  1. Pagina Facebook: Immobiliare Giancani (ID 234931856561526)
  2. Profilo/Pagina Facebook: Antonio Giancani (ID 108297671444008) con invito dinamico a visitare Immobiliare Giancani
  3. Google Sheet: foglio 'Post_YouTube' via Apps Script WebApp
  4. Telegram Bot: Notifica & Video Clip su Chat ID 1723292483
"""

import os
import sys
import time
import json
import random
import re
import subprocess
import urllib.request
import urllib.parse
import ssl
from datetime import datetime
import yt_dlp
from PIL import Image, ImageDraw, ImageFont

# Disabilita verifica SSL per connessioni Windows
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

import shutil

# Percorsi Binari e Cartelle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_BIN = os.environ.get("FFMPEG_BIN") or shutil.which("ffmpeg") or (r"C:\Users\immobiliare Giancani\.antigravity\ffmpeg.exe" if os.path.exists(r"C:\Users\immobiliare Giancani\.antigravity\ffmpeg.exe") else "ffmpeg")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "video_youtube_scaricati")
CLIPS_DIR = os.path.join(BASE_DIR, "clip_30s_generate")
REGISTRO_FILE = os.path.join(BASE_DIR, "registro_video_pubblicati_orari.json")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

# Parametri Master Canale & WebApp
CHANNEL_ID = "UC7jCI1x_cwh_sOrNPJpaKyQ"
CHANNEL_URL = f"https://www.youtube.com/channel/{CHANNEL_ID}/videos"
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec"

# Pagine Facebook Target
PAGES = [
    {
        "nome": "Immobiliare Giancani (Pagina Ufficiale)",
        "id": (os.environ.get("FB_PAGE_ID") or "234931856561526").strip(),
        "token": (os.environ.get("FB_PAGE_TOKEN") or "EAAZAH7q8wRZAEBS3ZAfEIpFIcXPJ87gDZAY8QjpGvBSjgC44c22JVeZAiDxMOM85JRMKM2T1hLgekBCkT0z5geNsb3KxAhMr7W7xlOGVKJsdKV9rZCEKLupIy1uNaDkVZAXmFtn0stiB212odWJ2ZCZBtlWkZAzy5wmPfKyZC3g27g6RXs0FK2GiYc5MeqaZCZBuoYjIyreTZAxwOqtfESifVw").strip(),
        "is_antonio": False
    },
    {
        "nome": "Antonio Giancani (Profilo Personale)",
        "id": os.environ.get("FB_ANTONIO_ID", "108297671444008"),
        "token": os.environ.get("FB_ANTONIO_TOKEN", "EAAZAH7q8wRZAEBS3ZAfEIpFIcXPJ87gDZAY8QjpGvBSjgC44c22JVeZAiDxMOM85JRMKM2T1hLgekBCkT0z5geNsb3KxAhMr7W7xlOGVKJsdKV9rZCEKLupIy1uNaDkVZAXmFtn0stiB212odWJ2ZCZBtlWkZAzy5wmPfKyZC3g27g6RXs0FK2GiYc5MeqaZCZBuoYjIyreTZAxwOqtfESifVw"),
        "is_antonio": True
    }
]

# Telegram
TELEGRAM_BOT_TOKEN = "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M"
TELEGRAM_CHAT_ID = "1723292483"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def carica_registro():
    if os.path.exists(REGISTRO_FILE):
        try:
            with open(REGISTRO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def salva_registro(lista):
    with open(REGISTRO_FILE, 'w', encoding='utf-8') as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)


def ottieni_durata_video(video_path):
    """Calcola la durata in secondi del file video usando ffmpeg.exe"""
    try:
        cmd = [FFMPEG_BIN, "-i", video_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
        out = res.stderr or res.stdout
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", out)
        if m:
            h, mn, s = float(m.group(1)), float(m.group(2)), float(m.group(3))
            return h * 3600 + mn * 60 + s
    except Exception as ex:
        log(f"Avviso calcolo durata con ffmpeg: {ex}")
    return 60.0


def estrai_tipologia_e_notizia(titolo, desc):
    """
    Estrae tipologia, comune e sintesi notizia dalla descrizione e titolo del video.
    Esempio esatto richiesto dall'utente: 'vende appartamento a favara vedi in descrizione'
    """
    testo_completo = f"{titolo} {desc}".lower()

    # 1. Rileva Azione (Vende / Affitta)
    azione = "Vende"
    if "affitt" in testo_completo or "locazion" in testo_completo:
        azione = "Affitta"
    elif "vend" in testo_completo or "vendesi" in testo_completo:
        azione = "Vende"

    # 2. Rileva Tipologia Immobile
    tipologia = "Appartamento"
    if "villa" in testo_completo:
        tipologia = "Villa Indipendente"
    elif "attico" in testo_completo or "mansarda" in testo_completo:
        tipologia = "Attico con Terrazzo"
    elif "commerciale" in testo_completo or "negozio" in testo_completo or "locale" in testo_completo:
        tipologia = "Locale Commerciale"
    elif "terreno" in testo_completo:
        tipologia = "Terreno Edificabile"
    elif "magazzino" in testo_completo or "garage" in testo_completo or "box" in testo_completo:
        tipologia = "Magazzino / Box"
    elif "casa autonoma" in testo_completo or "casa singola" in testo_completo or "fabbricato" in testo_completo:
        tipologia = "Casa Autonoma"
    elif "appartament" in testo_completo:
        tipologia = "Appartamento"

    # 3. Rileva Comune
    comune = "Favara"
    if "san leone" in testo_completo:
        comune = "San Leone (AG)"
    elif "agrigento" in testo_completo:
        comune = "Agrigento"
    elif "porto empedocle" in testo_completo:
        comune = "Porto Empedocle"
    elif "canicattì" in testo_completo or "canicatti" in testo_completo:
        comune = "Canicattì"
    elif "palma di montechiaro" in testo_completo:
        comune = "Palma di Montechiaro"
    elif "aragona" in testo_completo:
        comune = "Aragona"
    elif "favara" in testo_completo:
        comune = "Favara"

    # Notizia sintetica (conforme alla formulazione indicata dall'utente)
    notizia_sintetica = f"{azione} {tipologia.lower()} a {comune} — vedi in descrizione"
    return tipologia, comune, notizia_sintetica


CATALOGO_CACHE_FILE = os.path.join(BASE_DIR, "catalogo_youtube_cache.json")


def estrai_e_popola_sheet():
    """1. Estrae l'indice di tutti i video dell'ultimo anno e aggiorna Google Sheet (Post_YouTube)"""
    # Se presente cache recente (< 24 ore), usala
    if os.path.exists(CATALOGO_CACHE_FILE):
        try:
            mtime = os.path.getmtime(CATALOGO_CACHE_FILE)
            if (time.time() - mtime) < 86400: # 24 ore
                with open(CATALOGO_CACHE_FILE, 'r', encoding='utf-8') as f:
                    cat = json.load(f)
                    if len(cat) > 10:
                        log(f"📦 Utilizzo catalogo video locale in cache ({len(cat)} video registrati).")
                        return cat
        except Exception as e_cache:
            log(f"Avviso lettura cache: {e_cache}")

    log("📥 [1/4] Estrazione catalogo video canale YouTube (a ritroso 1 anno)...")

    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'nocheckcertificate': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        res = ydl.extract_info(CHANNEL_URL, download=False)
        entries = res.get('entries', [])

    log(f"   -> Trovati {len(entries)} video sul canale YouTube.")

    videos_for_sheet = []
    catalog = []

    for e in entries:
        vid_id = e.get('id')
        title = e.get('title') or "Immobile di Prestigio"
        desc = e.get('description') or f"Presentazione esclusiva: {title}. Per maggiori informazioni contattaci subito!"

        # Prezzo euristico
        prezzo = "Trattativa Riservata"
        if "€" in desc:
            m = re.search(r'(\d{2,3}[\.\s]?\d{3})\s*€', desc)
            if m:
                prezzo = f"{m.group(1).replace(' ', '.')} €"

        # Regola di progetto: Superfici rigorosamente in "metri quadri"
        desc_pulita = desc.replace("mq", "metri quadri").replace("m²", "metri quadri").replace("MQ", "metri quadri")

        # Regola di progetto: Personal branding finale "— Immobiliare Giancani"
        if not desc_pulita.endswith("— Immobiliare Giancani"):
            desc_pulita += "\n\n— Immobiliare Giancani"

        thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"

        videos_for_sheet.append({
            "videoId": vid_id,
            "titolo": title,
            "descrizione": desc_pulita,
            "thumbnail": thumb,
            "prezzo": prezzo,
            "isShort": False
        })

        catalog.append({
            "id": vid_id,
            "title": title,
            "desc": desc_pulita,
            "prezzo": prezzo,
            "thumb": thumb,
            "url": f"https://www.youtube.com/watch?v={vid_id}"
        })

    # Salva cache locale
    try:
        with open(CATALOGO_CACHE_FILE, 'w', encoding='utf-8') as f_c:
            json.dump(catalog, f_c, indent=2, ensure_ascii=False)
    except Exception as e_w:
        log(f"Avviso salvataggio cache: {e_w}")

    # Popolamento Google Sheet via WebApp Apps Script
    try:
        payload = {
            "action": "salva_video_youtube_batch",
            "videos": videos_for_sheet
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(WEBAPP_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            resp = json.loads(r.read().decode('utf-8'))
            log(f"✅ Google Sheet aggiornato: {resp.get('message', 'OK')}")
    except Exception as ex:
        log(f"⚠️ Avviso aggiornamento Google Sheet: {ex}")

    return catalog


def scarica_video_completo(video_id, watch_url):
    """2. Scarica il video intero nella cartella locale/drive (se non già presente)"""
    out_tmpl = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    if os.path.exists(out_tmpl) and os.path.getsize(out_tmpl) > 500000:
        log(f"   -> Video già presente in archivio locale: {out_tmpl}")
        return out_tmpl

    log(f"⬇️ [2/4] Download video YouTube ({video_id}) in corso...")
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': out_tmpl,
        'quiet': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'mweb', 'web']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([watch_url])

    log(f"✅ Video scaricato con successo ({os.path.getsize(out_tmpl) / (1024*1024):.1f} MB): {out_tmpl}")
    return out_tmpl


def draw_text_con_ombra(draw, pos, testo, font, fill, shadow_color=(0, 0, 0, 220), offset=(2, 2), anchor="mm"):
    """Disegna un testo con una morbida ombra scura per renderlo leggibile sopra sfondi semitrasparenti"""
    x, y = pos
    draw.text((x + offset[0], y + offset[1]), testo, font=font, fill=shadow_color, anchor=anchor)
    draw.text((x, y), testo, font=font, fill=fill, anchor=anchor)


def crea_overlay_grafica(meta, per_antonio=False):
    """
    Crea un overlay grafico trasparente 1080x1920.
    Nessun form o elemento in alto per non coprire il logo originale del video.
    Card inferiore con SFONDO SEMI-TRASPARENTE (glassmorphism) per dare massima priorità alle immagini dell'immobile.
    """
    W, H = 1080, 1920
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    tipologia, comune, notizia_sintetica = estrai_tipologia_e_notizia(meta.get('title', ''), meta.get('desc', ''))

    def load_font(size, bold=False):
        cands = [
            "arialbd.ttf" if bold else "arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
        ]
        for c in cands:
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
        return ImageFont.load_default()

    font_badge = load_font(34, bold=True)
    font_notizia = load_font(30, bold=True)
    font_cta = load_font(32, bold=True)
    font_url = load_font(30, bold=True)
    font_firm = load_font(24, bold=False)

    # NOTA: PARTE SUPERIORE COMPLETAMENTE LIBERA PER IL LOGO ORIGINALE DEL VIDEO
    # (Nessun rettangolo, nessun banner e nessun form in alto)

    # Card Unificata Luxury in Basso SEMI-TRASPARENTE (Alpha: 110 su 255 = ~43% per dare priorità alle immagini)
    by0 = H - 470
    by1 = H - 70
    draw.rounded_rectangle([35, by0, W - 35, by1], radius=28, fill=(8, 14, 25, 110), outline=(212, 175, 55, 170), width=2)

    # 1. Badge Tipologia & Comune
    draw_text_con_ombra(draw, (W / 2, by0 + 50), f"🏷️ {tipologia.upper()} A {comune.upper()}", font_badge, (255, 255, 255, 255))

    # 2. Notizia specifica (come richiesto dall'utente: "vende appartamento a favara vedi in descrizione")
    draw_text_con_ombra(draw, (W / 2, by0 + 105), f"📢 {notizia_sintetica.upper()}", font_notizia, (255, 215, 0, 255))

    # Separatore dorato sottile semitrasparente
    draw.line([70, by0 + 140, W - 70, by0 + 140], fill=(212, 175, 55, 140), width=1)

    short_url = f"https://youtu.be/{meta['id']}"

    if per_antonio:
        # Invito dinamico per la pagina Antonio Giancani
        frasi_antonio = [
            ("👉 GUARDA IL TOUR COMPLETO", "Clicca e vai sulla pagina: IMMOBILIARE GIANCANI"),
            ("✨ SCOPRI TUTTI I DETTAGLI", "Tutte le foto e il video su: IMMOBILIARE GIANCANI"),
            ("🏡 VUOI VISITARE L'IMMOBILE?", "Trovi la scheda completa su: IMMOBILIARE GIANCANI")
        ]
        titolo_invito, sub_invito = random.choice(frasi_antonio)
        draw_text_con_ombra(draw, (W / 2, by0 + 185), titolo_invito, font_cta, (255, 215, 0, 255))
        draw_text_con_ombra(draw, (W / 2, by0 + 240), sub_invito, font_notizia, (255, 255, 255, 255))
        draw_text_con_ombra(draw, (W / 2, by0 + 295), f"🔗 Link: {short_url}", font_url, (78, 168, 254, 255))
        draw_text_con_ombra(draw, (W / 2, by0 + 355), "— Immobiliare Giancani", font_firm, (220, 230, 245, 255))
    else:
        # Versione per Immobiliare Giancani
        draw_text_con_ombra(draw, (W / 2, by0 + 185), "👉 VEDI IL VIDEO COMPLETO E DETTAGLI", font_cta, (255, 215, 0, 255))
        draw_text_con_ombra(draw, (W / 2, by0 + 240), "Link diretto disponibile nel primo commento:", font_notizia, (240, 240, 240, 255))
        draw_text_con_ombra(draw, (W / 2, by0 + 295), f"🔗 Link: {short_url}", font=font_url, fill=(78, 168, 254, 255))
        draw_text_con_ombra(draw, (W / 2, by0 + 355), "— Immobiliare Giancani", font=font_firm, fill=(220, 230, 245, 255))

    overlay_filename = f"overlay_{meta['id']}_{'antonio' if per_antonio else 'giancani'}.png"
    overlay_path = os.path.join(CLIPS_DIR, overlay_filename)
    overlay.save(overlay_path, "PNG")
    return overlay_path


def genera_clip_30s(video_locale, meta, per_antonio=False):
    """3. Taglia 30 secondi casuali dal video completo e applica l'overlay verticale 9:16"""
    dur_totale = ottieni_durata_video(video_locale)
    max_start = max(0, int(dur_totale - 35))
    start_time = random.randint(0, max_start) if max_start > 0 else 0

    log(f"✂️ [3/4] Creazione spezzone 30s (da sec {start_time} su {dur_totale:.0f}s totali)...")

    overlay_png = crea_overlay_grafica(meta, per_antonio=per_antonio)
    tag_versione = "antonio" if per_antonio else "giancani"
    out_clip = os.path.join(CLIPS_DIR, f"clip_30s_{meta['id']}_{tag_versione}_{start_time}.mp4")

    cmd = [
        FFMPEG_BIN, "-y",
        "-ss", str(start_time),
        "-t", "30",
        "-i", video_locale,
        "-i", overlay_png,
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[vbg];[vbg][1:v]overlay=0:0[vout]",
        "-map", "[vout]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        out_clip
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    log(f"✅ Clip 30s generata ({tag_versione}): {out_clip}")
    return out_clip


def pubblica_video_story_facebook(target, video_path):
    """4. Pubblica la clip su Facebook via Graph API v19.0 video_stories"""
    nome = target['nome']
    page_id = target['id']
    page_token = target['token']
    file_size = os.path.getsize(video_path)

    log(f"🚀 [4/4] Pubblicazione video story su {nome}...")

    try:
        # Phase 1: Start
        start_url = f'https://graph.facebook.com/v19.0/{page_id}/video_stories'
        start_data = urllib.parse.urlencode({'upload_phase': 'start', 'access_token': page_token}).encode('utf-8')
        req_start = urllib.request.Request(start_url, data=start_data, method='POST')

        with urllib.request.urlopen(req_start, timeout=30, context=ctx) as r_s:
            res_start = json.loads(r_s.read().decode('utf-8'))
            video_id = res_start['video_id']
            upload_url = res_start['upload_url']

        # Phase 2: Upload
        with open(video_path, 'rb') as f:
            video_bytes = f.read()

        req_upload = urllib.request.Request(upload_url, data=video_bytes, method='POST')
        req_upload.add_header('Authorization', f'OAuth {page_token}')
        req_upload.add_header('offset', '0')
        req_upload.add_header('file_size', str(file_size))
        req_upload.add_header('Content-Type', 'application/octet-stream')

        with urllib.request.urlopen(req_upload, timeout=90, context=ctx) as r_u:
            res_upload = json.loads(r_u.read().decode('utf-8'))
            if not res_upload.get('success', False):
                raise Exception(f"Upload non riuscito: {res_upload}")

        # Phase 3: Finish
        finish_url = f'https://graph.facebook.com/v19.0/{page_id}/video_stories'
        finish_data = urllib.parse.urlencode({
            'upload_phase': 'finish',
            'video_id': video_id,
            'video_state': 'PUBLISHED',
            'access_token': page_token
        }).encode('utf-8')
        req_finish = urllib.request.Request(finish_url, data=finish_data, method='POST')

        with urllib.request.urlopen(req_finish, timeout=30, context=ctx) as r_f:
            res_finish = json.loads(r_f.read().decode('utf-8'))

        post_id = res_finish.get('post_id') or video_id
        log(f"🎉 Storia pubblicata con successo su {nome}! (Story ID: {post_id})")
        return post_id
    except urllib.error.HTTPError as he:
        err_content = he.read().decode('utf-8', errors='ignore')
        log(f"⚠️ Errore Facebook Graph API ({nome} - HTTP {he.code}): {err_content}")
        raise
    except Exception as ex:
        log(f"⚠️ Errore pubblicazione storia su {nome}: {ex}")
        raise


def invia_telegram(meta, video_clip_path):
    """Invia notifica formattata e recapita la video clip 30s su Telegram (Chat ID 1723292483)"""
    try:
        tipologia, comune, notizia = estrai_tipologia_e_notizia(meta.get('title', ''), meta.get('desc', ''))
        short_url = f"https://youtu.be/{meta['id']}"

        caption = (
            f"🎬 <b>NUOVA CLIP 30s DALL'ARCHIVIO YOUTUBE PUBBLICATA!</b> 🚀\n\n"
            f"🏠 <b>Tipologia:</b> {tipologia} a {comune}\n"
            f"📢 <b>Notizia:</b> {notizia}\n"
            f"📌 <b>Titolo:</b> {meta.get('title')}\n"
            f"🔗 <b>Video YouTube:</b> <a href=\"{short_url}\">{short_url}</a>\n"
            f"⏱️ <i>Prossima clip differente programmata tra 1 ora.</i>\n\n"
            f"— <b>Immobiliare Giancani</b>"
        )

        # Tentativo invio diretto della video clip MP4 su Telegram
        if os.path.exists(video_clip_path) and os.path.getsize(video_clip_path) < 48 * 1024 * 1024:
            try:
                import requests
                url_video = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
                with open(video_clip_path, 'rb') as f_v:
                    files = {'video': (os.path.basename(video_clip_path), f_v, 'video/mp4')}
                    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
                    res_v = requests.post(url_video, data=data, files=files, verify=False, timeout=180)
                    if res_v.status_code == 200:
                        log("✅ Clip video 30s e notifica recapitate su Telegram (Chat 1723292483).")
                        return
                    else:
                        log(f"Avviso invio video Telegram HTTP {res_v.status_code}: {res_v.text}")
            except Exception as e_vid:
                log(f"Avviso invio video telegram: {e_vid}")

        # Fallback notifica testo
        d_tg = urllib.parse.urlencode({'chat_id': TELEGRAM_CHAT_ID, 'text': caption, 'parse_mode': 'HTML'}).encode()
        req_tg = urllib.request.Request(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage', data=d_tg, method='POST')
        urllib.request.urlopen(req_tg, timeout=20, context=ctx)
        log("✅ Notifica inviata su Telegram (Chat 1723292483).")
    except Exception as ex:
        log(f"Avviso invio notifica Telegram: {ex}")


def esegui_ciclo_orario():
    """Esegue un ciclo orario completo: seleziona video non ancora pubblicato, taglia 30s, grafica e pubblica"""
    log("======================================================================")
    log("⏰ AVVIO CICLO DI PUBBLICAZIONE VIDEO YOUTUBE (1 OGNI ORA)")
    log("======================================================================")

    catalog = estrai_e_popola_sheet()
    if not catalog:
        log("❌ Catalogo vuoto o non accessibile. Riprovo al prossimo ciclo.")
        return

    registro = carica_registro()
    gia_pubblicati = set(registro)

    candidati = [v for v in catalog if v['id'] not in gia_pubblicati]
    if not candidati:
        log("🔄 Tutti i video del catalogo sono stati pubblicati. Riavvio rotazione da capo!")
        registro = []
        salva_registro(registro)
        candidati = catalog

    scelto = candidati[0]
    log(f"🎯 Video selezionato per questa ora: {scelto['title']} (ID: {scelto['id']})")

    # 1. Download del video completo
    video_locale = scarica_video_completo(scelto['id'], scelto['url'])

    # 2. Generazione clip per Immobiliare Giancani e pubblicazione
    clip_giancani = None
    try:
        clip_giancani = genera_clip_30s(video_locale, scelto, per_antonio=False)
        pubblica_video_story_facebook(PAGES[0], clip_giancani)
    except Exception as ex_g:
        log(f"⚠️ Segnalazione storia su {PAGES[0]['nome']}: {ex_g}")

    # 3. Generazione clip con invito dinamico per Antonio Giancani e pubblicazione
    clip_antonio = None
    try:
        clip_antonio = genera_clip_30s(video_locale, scelto, per_antonio=True)
        pubblica_video_story_facebook(PAGES[1], clip_antonio)
    except Exception as ex_a:
        log(f"⚠️ Segnalazione storia su {PAGES[1]['nome']}: {ex_a}")

    # 4. Notifica Telegram aziendale e recapito video
    clip_da_inviare = clip_giancani or clip_antonio or video_locale
    invia_telegram(scelto, clip_da_inviare)

    # 5. Salva nel registro storico per garantire 1 diverso ogni ora
    registro.append(scelto['id'])
    salva_registro(registro)
    log(f"✅ Ciclo orario completato. Video {scelto['id']} archiviato nel registro.")
    log(f"⏱️ In attesa di 1 ora (3600 secondi) per il prossimo video...")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        esegui_ciclo_orario()
    else:
        while True:
            try:
                esegui_ciclo_orario()
            except Exception as e:
                log(f"❌ Errore critico nel ciclo orario: {e}")
            time.sleep(3600)
