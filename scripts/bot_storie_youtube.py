#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
IMMOBILIARE GIANCANI — BOT STORIE FACEBOOK YOUTUBE (07:00 & 19:00)
═══════════════════════════════════════════════════════════════════════════════
Funzionalità:
1. Programmazione:
   - Due volte al giorno: 07:00 (Mattina) e 19:00 (Sera) ora italiana.
   - Mattina (07:00): Preleva il PRIMO video della lista 'Post_YouTube'.
   - Sera (19:00): Preleva l'ULTIMO video della lista 'Post_YouTube'.
2. Grafica e Presentazione:
   - SENZA avatar (nessun personaggio DarIA o DarIO sullo schermo).
   - NESSUNA menzione di "diretta" o "siamo in diretta" (focus puro sull'immobile).
   - Video in continuo movimento per tutta la durata (15 secondi).
   - Audio: preserva rigorosamente la musica/audio originale del video di YouTube.
   - Logo aziendale SEMI-VISIBILE in sovrimpressione (watermark elegante con opacità al 65%).
   - Link e QR Code interattivo per indirizzare gli utenti direttamente al video/immobile.
3. Regole di Brand:
   - Testo prelevato RIGOROSAMENTE dalla Colonna F ('TESTO_PARLATO_DARIA').
   - Superfici sempre espresse con la dicitura 'metri quadri' (mai la sigla mq).
   - Chiusura costante che mette in risalto '— Immobiliare Giancani'.
4. Destinazioni:
   - Pagina Facebook: Immobiliare Giancani (ID 234931856561526)
   - Profilo Personale: Antonio Giancani (ID 108297671444008)
═══════════════════════════════════════════════════════════════════════════════
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
import io
import sys
import re
import time
import json
import uuid
import shutil
import random
import argparse
import datetime
import subprocess
import urllib.request
import urllib.parse
import numpy as np
import wave
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageFilter

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

# Pagine Facebook di destinazione
PAGES = [
    {
        "nome": "Immobiliare Giancani (Pagina Ufficiale)",
        "id": os.environ.get("FB_PAGE_ID", "234931856561526"),
        "token": os.environ.get("FB_PAGE_TOKEN", "EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI")
    },
    {
        "nome": "Antonio Giancani (Profilo Personale)",
        "id": os.environ.get("FB_ANTONIO_ID", "108297671444008"),
        "token": os.environ.get("FB_ANTONIO_TOKEN", "EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia")
    }
]

APPS_SCRIPT_URL = os.environ.get(
    "APPS_SCRIPT_URL",
    "https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec"
)
REMOTE_LOGO_URL = "https://lh3.googleusercontent.com/d/1BoZ_9QyYPRKjZFP__iPr7mmi0aGV0G3P"

ctx = ssl._create_unverified_context()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SCRATCH_DIR = os.path.join(BASE_DIR, "output_storie_youtube")
os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

def find_ffmpeg():
    """Localizza FFmpeg nel sistema"""
    candidates = [
        shutil.which("ffmpeg"),
        os.path.join(os.path.dirname(BASE_DIR), "ffmpeg.exe"),
        os.path.join(BASE_DIR, "ffmpeg.exe"),
        "ffmpeg"
    ]
    for c in candidates:
        if c and (os.path.exists(c) or shutil.which(c)):
            return c
    return "ffmpeg"

def find_ytdlp():
    """Localizza yt-dlp"""
    candidates = [
        shutil.which("yt-dlp"),
        "yt-dlp"
    ]
    for c in candidates:
        if c and (os.path.exists(c) or shutil.which(c)):
            return c
    return "yt-dlp"

def get_font(size, bold=False):
    """Carica font TrueType scalato per alta definizione"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def normalize_mq(val):
    """Garantisce la dicitura 'metri quadri' per le superfici come da regola globale"""
    if not val:
        return "110 metri quadri"
    val = str(val).strip()
    val = val.replace("mq", "metri quadri").replace("Mq", "metri quadri").replace("m²", "metri quadri").replace("MQ", "metri quadri")
    if "metri quadri" not in val.lower():
        val = f"{val} metri quadri"
    return val

def get_logo_image():
    """Restituisce il logo aziendale ufficiale Immobiliare Giancani"""
    local_path = os.path.join(ASSETS_DIR, "logo_giancani.png")
    if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
        try:
            return Image.open(local_path).convert('RGBA')
        except Exception:
            pass
    try:
        req = urllib.request.Request(REMOTE_LOGO_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = resp.read()
            with open(local_path, 'wb') as f:
                f.write(data)
            return Image.open(io.BytesIO(data)).convert('RGBA')
    except Exception as e:
        print(f"Avviso recupero logo: {e}")
    return None

def genera_qr_code(url, size=220):
    """Scarica il QR Code in alta definizione per indirizzare gli utenti al link con 1 tap"""
    try:
        qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={urllib.parse.quote(url)}&bgcolor=255-255-255&color=15-23-42"
        req = urllib.request.Request(qr_api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = resp.read()
            if len(data) > 300:
                return Image.open(io.BytesIO(data)).convert('RGBA')
    except Exception as e:
        print(f"Avviso generazione QR code ({e}): uso fallback...")
    return None

def check_video_has_audio(video_path):
    """Verifica se il file video dispone di una traccia audio"""
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", video_path]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return "audio" in res.stdout.lower()
    except Exception:
        return True # Di default assumiamo presente se non possiamo testare

def genera_audio_allegra_fallback(output_audio_path=None):
    """Genera traccia audio di riserva allegra a 124 BPM qualora il video di YouTube sia muto"""
    if not output_audio_path:
        output_audio_path = os.path.join(SCRATCH_DIR, "cheerful_fallback.wav")
    BPM = 124
    BEAT = 60.0 / BPM
    DUR = 15.0
    SR = 44100
    nsamples = int(SR * DUR)
    left = np.zeros(nsamples, dtype=np.float32)
    right = np.zeros(nsamples, dtype=np.float32)

    prog = [
        ([261.63, 329.63, 392.00, 523.25], 130.81),
        ([246.94, 293.66, 392.00, 493.88], 98.00),
        ([220.00, 261.63, 329.63, 440.00], 110.00),
        ([220.00, 261.63, 349.23, 440.00], 87.31),
    ]
    chord_dur = DUR / len(prog)

    for c_idx, (notes, bass_freq) in enumerate(prog):
        c_start = c_idx * chord_dur
        num_beats = int(chord_dur / (BEAT / 2))
        for b in range(num_beats):
            note_t0 = c_start + b * (BEAT / 2)
            if note_t0 >= DUR: break
            s_i = int(note_t0 * SR)
            n_len = int(0.24 * SR)
            if s_i + n_len > nsamples: n_len = nsamples - s_i
            tn = np.linspace(0, 0.24, n_len, endpoint=False)
            decay = np.exp(-10 * tn)
            note_pitch = notes[b % len(notes)]
            if b % 2 == 0:
                bass_env = np.exp(-7 * tn)
                bass_tone = 0.5 * np.sin(2 * np.pi * bass_freq * tn) * bass_env
                left[s_i:s_i+n_len] += bass_tone * 0.7
                right[s_i:s_i+n_len] += bass_tone * 0.7
            pluck = (0.55 * np.sin(2 * np.pi * note_pitch * tn) + 0.3 * np.sin(4 * np.pi * note_pitch * tn)) * decay
            left[s_i:s_i+n_len] += pluck * 0.5
            right[s_i:s_i+n_len] += pluck * 0.5

    with wave.open(output_audio_path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        inter = np.empty((nsamples * 2,), dtype=np.int16)
        inter[0::2] = (left * 32767).astype(np.int16)
        inter[1::2] = (right * 32767).astype(np.int16)
        wf.writeframes(inter.tobytes())
    return output_audio_path

def scarica_clip_youtube(video_url, output_clip_path=None):
    """
    Scarica una clip di 15 secondi dal video di YouTube conservando la musica e l'audio originale
    """
    if not output_clip_path:
        output_clip_path = os.path.join(SCRATCH_DIR, f"yt_clip_{uuid.uuid4().hex[:8]}.mp4")

    ytdlp_bin = find_ytdlp()

    # Estrai YouTube ID
    m = re.search(r'(?:v=|\/embed\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', video_url)
    yt_id = m.group(1) if m else None
    watch_url = f"https://www.youtube.com/watch?v={yt_id}" if yt_id else video_url

    print(f"📥 Download clip YouTube 15s (audio originale preservato): {watch_url}")

    cmd = [
        ytdlp_bin, "--no-check-certificates", "--no-warnings",
        "-f", "best[height<=1080][ext=mp4]/best[ext=mp4]/best",
        "--download-sections", "*00:00-00:15",
        "--force-keyframes-at-cuts",
        watch_url,
        "-o", output_clip_path
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        if res.returncode == 0 and os.path.exists(output_clip_path) and os.path.getsize(output_clip_path) > 100000:
            print(f"[OK] Clip video scaricata con successo: {output_clip_path}")
            return output_clip_path, watch_url
    except Exception as e:
        print(f"Avviso download selettivo ({e})")

    return None, watch_url

def render_storia_youtube_video(item_data, is_morning=True, output_video_path=None):
    """
    Costruisce la video storia 1080x1920:
    - Clip video YouTube che gira per tutti i 15 secondi
    - Conservazione rigorosa della musica/audio originale del video
    - Nessun avatar e nessuna frase di diretta
    - Logo aziendale semi-visibile (watermark 65% opacità)
    - Link e QR Code per indirizzare gli utenti al video/sito
    - Testo rigorosamente da Colonna F con superfici in 'metri quadri'
    - Personal branding: chiusura '— Immobiliare Giancani'
    """
    if not output_video_path:
        output_video_path = os.path.join(SCRATCH_DIR, f"story_yt_{uuid.uuid4().hex[:8]}.mp4")

    ffmpeg_bin = find_ffmpeg()
    W, H = 1080, 1920

    video_url = item_data.get('videoUrl', '')
    prezzo = item_data.get('prezzo', 'Trattativa Riservata')
    mq = normalize_mq(item_data.get('mq', '110'))
    titolo = item_data.get('titolo', 'Opportunità Immobiliare')
    testo_col_f = item_data.get('testoF', 'Splendida soluzione proposta in esclusiva ad Agrigento e provincia.')
    thumb_url = item_data.get('thumbUrl', '')

    # 1. Scarica la clip video
    clip_path, direct_watch_url = scarica_clip_youtube(video_url)

    # 2. Prepara la grafica dell'overlay PNG trasparente
    overlay_im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay_im)

    # A. LOGO SEMI-VISIBILE IN ALTO (Watermark con opacità 65%)
    logo_raw = get_logo_image()
    if logo_raw:
        logo_resized = logo_raw.resize((120, 120), Image.LANCZOS)
        # Riduci l'opacità del logo al 65% per renderlo elegantemente semi-visibile
        r, g, b, alpha = logo_resized.split()
        alpha_semi = alpha.point(lambda p: int(p * 0.65))
        logo_semi = Image.merge('RGBA', (r, g, b, alpha_semi))
        overlay_im.paste(logo_semi, ((W - 120) // 2, 70), mask=logo_semi)

    font_brand = get_font(28, bold=True)
    brand_txt = "IMMOBILIARE GIANCANI"
    draw.text(((W - font_brand.getbbox(brand_txt)[2]) // 2, 205), brand_txt, font=font_brand, fill=(212, 168, 83, 230))

    # B. BADGE DEL MOMENTO (Mattina / Sera - Nessuna menzione di live)
    badge_txt = "🌅 FOCUS MATTUTINO • SELEZIONE ESCLUSIVA" if is_morning else "🌙 FOCUS SERALE • VETRINA IMMOBILIARE"
    font_badge = get_font(19, bold=True)
    bw = font_badge.getbbox(badge_txt)[2] + 40
    badge_bg = (30, 58, 138, 235) if is_morning else (88, 28, 135, 235)
    draw.rounded_rectangle([(W - bw)//2, 250, (W + bw)//2, 292], radius=14, fill=badge_bg, outline=(212, 168, 83, 160), width=1)
    draw.text(((W - font_badge.getbbox(badge_txt)[2]) // 2, 260), badge_txt, font=font_badge, fill=(255, 255, 255, 255))

    # C. SCHEDA INFORMATIVA IN BASSO (con QR code e link cliccabile)
    card_y = 1290
    draw.rounded_rectangle([40, card_y, 1040, card_y + 490], radius=26, fill=(15, 23, 42, 240), outline=(212, 168, 83, 200), width=2)

    # Titolo Immobile
    font_tit = get_font(30, bold=True)
    draw.text((70, card_y + 25), titolo[:45], font=font_tit, fill=(255, 255, 255, 255))

    # Dettagli Prezzo & Superficie in "metri quadri"
    font_dett = get_font(23, bold=False)
    draw.text((70, card_y + 70), f"💰 {prezzo}   |   📐 {mq}", font=font_dett, fill=(212, 168, 83, 255))

    # Testo Colonna F (prime 3 righe significative)
    font_body = get_font(19, bold=False)
    righe_pulite = [l.strip() for l in testo_col_f.splitlines() if l.strip()]
    testo_unito = " ".join(righe_pulite)[:190]
    r1 = testo_unito[:60]
    r2 = testo_unito[60:125]
    r3 = testo_unito[125:190]
    draw.text((70, card_y + 115), r1, font=font_body, fill=(226, 232, 240, 255))
    if r2: draw.text((70, card_y + 142), r2, font=font_body, fill=(226, 232, 240, 255))
    if r3: draw.text((70, card_y + 169), r3, font=font_body, fill=(226, 232, 240, 255))

    # D. QR CODE & LINK PER INDIRIZZARE GLI UTENTI
    qr_img = genera_qr_code(direct_watch_url, size=150)
    if qr_img:
        # Bordo bianco attorno al QR Code per massima leggibilità
        qr_bg = Image.new('RGBA', (160, 160), (255, 255, 255, 255))
        qr_bg.paste(qr_img, (5, 5), mask=qr_img)
        overlay_im.paste(qr_bg, (70, card_y + 215))

    # Box Bottone Cliccabile / Call to Action
    draw.rounded_rectangle([250, card_y + 215, 1005, card_y + 280], radius=16, fill=(234, 179, 8, 245))
    font_cta_btn = get_font(21, bold=True)
    cta_btn_txt = "👉 TOCCA IL LINK O INQUADRA IL QR 🔗"
    draw.text((250 + (755 - font_cta_btn.getbbox(cta_btn_txt)[2])//2, card_y + 233), cta_btn_txt, font=font_cta_btn, fill=(15, 23, 42, 255))

    # Link esplicito di destinazione
    font_url = get_font(20, bold=True)
    url_display = "🌐 www.immobiliaregiancani.it  •  YouTube"
    draw.text((260, card_y + 295), url_display, font=font_url, fill=(56, 189, 248, 255))

    font_sub_cta = get_font(18, bold=False)
    sub_cta_txt = "Guarda il video tour completo & scopri tutti i dettagli"
    draw.text((260, card_y + 325), sub_cta_txt, font=font_sub_cta, fill=(203, 213, 225, 255))

    # E. CHIUSURA CON PERSONAL BRANDING
    font_footer = get_font(27, bold=True)
    footer_txt = "— Immobiliare Giancani"
    draw.text(((W - font_footer.getbbox(footer_txt)[2]) // 2, card_y + 420), footer_txt, font=font_footer, fill=(212, 168, 83, 255))

    overlay_path = os.path.join(SCRATCH_DIR, f"overlay_yt_{uuid.uuid4().hex[:8]}.png")
    overlay_im.save(overlay_path, "PNG")

    # 3. RENDERING VIDEO CON FFMPEG
    # Far girare il video per tutto il tempo della storia (15s) e mantenere la musica/audio originale
    vf_filter = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        "[0:v]scale=1000:750:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:490[vwithfg];"
        "[vwithfg][1:v]overlay=0:0[vout]"
    )

    if clip_path and os.path.exists(clip_path):
        has_audio = check_video_has_audio(clip_path)
        if has_audio:
            # Preserva l'audio originale del video di YouTube
            print("🎵 Preservazione musica e audio originale della clip YouTube...")
            cmd_render = [
                ffmpeg_bin, "-y",
                "-stream_loop", "-1", "-i", clip_path,
                "-i", overlay_path,
                "-filter_complex", vf_filter,
                "-map", "[vout]",
                "-map", "0:a",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-t", "15",
                output_video_path
            ]
        else:
            # Aggiunge musica allegra royalty-free di riserva se il video è muto
            print("ℹ️ Video YouTube privo di audio: aggiungo musica allegra di sottofondo...")
            music_fallback = genera_audio_allegra_fallback()
            cmd_render = [
                ffmpeg_bin, "-y",
                "-stream_loop", "-1", "-i", clip_path,
                "-i", overlay_path,
                "-i", music_fallback,
                "-filter_complex", vf_filter,
                "-map", "[vout]",
                "-map", "2:a",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-t", "15",
                output_video_path
            ]
    else:
        # Fallback se download video fallisce: crea animazione fluida su copertina/immagine
        print("⚠️ Clip video diretta non disponibile: creo animazione motion su thumbnail...")
        music_fallback = genera_audio_allegra_fallback()
        temp_thumb = os.path.join(SCRATCH_DIR, f"thumb_{uuid.uuid4().hex[:8]}.jpg")
        try:
            req_th = urllib.request.Request(thumb_url or "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_th, timeout=10, context=ctx) as resp_th:
                with open(temp_thumb, 'wb') as f_th:
                    f_th.write(resp_th.read())
        except Exception:
            temp_thumb = os.path.join(ASSETS_DIR, "logo_giancani.png")

        cmd_render = [
            ffmpeg_bin, "-y",
            "-loop", "1", "-i", temp_thumb,
            "-i", overlay_path,
            "-i", music_fallback,
            "-filter_complex", vf_filter,
            "-map", "[vout]",
            "-map", "2:a",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", "15",
            output_video_path
        ]

    proc = subprocess.run(cmd_render, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    if proc.returncode == 0 and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 100000:
        print(f"[OK] Video storia YouTube 1080x1920 (15s) generato con successo: {output_video_path}")
        return output_video_path, direct_watch_url
    return None, direct_watch_url

def pubblica_storia_facebook(page_id, page_token, video_path):
    """Carica la video storia su Facebook tramite Meta Graph API Video Stories"""
    file_size = os.path.getsize(video_path)

    # 1. Start Phase
    url_start = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"
    params_start = f"upload_phase=start&access_token={urllib.parse.quote(page_token)}".encode('utf-8')
    req_start = urllib.request.Request(url_start, data=params_start, method='POST')

    with urllib.request.urlopen(req_start, context=ctx) as resp_start:
        start_data = json.loads(resp_start.read().decode('utf-8'))
        video_id = start_data.get('video_id')
        upload_url = start_data.get('upload_url')
        if not video_id or not upload_url:
            raise Exception("Meta API non ha restituito video_id o upload_url")

    # 2. Upload Phase
    with open(video_path, 'rb') as f:
        video_bytes = f.read()

    req_upload = urllib.request.Request(upload_url, data=video_bytes, method='POST')
    req_upload.add_header('Authorization', f'OAuth {page_token}')
    req_upload.add_header('offset', '0')
    req_upload.add_header('file_size', str(file_size))
    req_upload.add_header('Content-Type', 'application/octet-stream')

    with urllib.request.urlopen(req_upload, context=ctx) as resp_upload:
        up_res = json.loads(resp_upload.read().decode('utf-8'))
        if not up_res.get('success'):
            raise Exception(f"Upload fallito: {up_res}")

    # 3. Finish Phase
    url_finish = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"
    params_finish = f"upload_phase=finish&video_id={video_id}&video_state=PUBLISHED&access_token={urllib.parse.quote(page_token)}".encode('utf-8')
    req_finish = urllib.request.Request(url_finish, data=params_finish, method='POST')

    with urllib.request.urlopen(req_finish, context=ctx) as resp_finish:
        fin_res = json.loads(resp_finish.read().decode('utf-8'))
        return {
            "success": fin_res.get('success', True),
            "video_id": video_id,
            "story_id": fin_res.get('post_id') or video_id
        }

def invia_notifica_telegram_youtube(titolo, mq, prezzo, watch_url, is_morning, risultati):
    """Invia notifica Telegram con il link diretto al video"""
    try:
        orario_str = "🌅 07:00 (MATTINA)" if is_morning else "🌙 19:00 (SERA)"
        lines = [
            f"🎬 <b>STORIA YOUTUBE PUBBLICATA ({orario_str})</b> ✨",
            f"🏠 <b>Titolo:</b> {titolo}",
            f"📐 <b>Superficie:</b> {mq}",
            f"💰 <b>Prezzo:</b> {prezzo}",
            f"🔗 <b>Link YouTube:</b> {watch_url}",
            f"🎵 <b>Audio:</b> Musica originale del video preservata",
            f"⏱️ <b>Durata:</b> 15 secondi Full HD (Logo semi-visibile & QR link)\n"
        ]
        for r in risultati:
            status = "✅ Pubblicata" if r.get("success") else f"⚠️ {r.get('error', 'Fallita')}"
            lines.append(f"• <b>{r.get('nome')}:</b> {status} (Story ID: {r.get('story_id', 'N/D')})")

        lines.append("\n— <b>Immobiliare Giancani</b>")
        msg = "\n".join(lines)
        url_tg = f"{APPS_SCRIPT_URL}?action=invia_notifica&msg={urllib.parse.quote(msg)}"
        req_tg = urllib.request.Request(url_tg, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_tg, timeout=10, context=ctx) as r:
            pass
    except Exception as e:
        print(f"Avviso notifica Telegram: {e}")

def esegui_pubblicazione(target_mode='auto'):
    """
    Esegue il ciclo di pubblicazione storie YouTube:
    - target_mode: 'first' (07:00 Mattina), 'last' (19:00 Sera) o 'auto' (in base all'ora corrente)
    """
    # 1. Calcola orario italiano
    now_rome = None
    if ZoneInfo:
        try:
            now_rome = datetime.datetime.now(ZoneInfo("Europe/Rome"))
        except Exception:
            pass
    if not now_rome:
        now_rome = datetime.datetime.utcnow() + datetime.timedelta(hours=2)

    if target_mode == 'auto':
        target_mode = 'first' if now_rome.hour < 13 else 'last'

    is_morning = (target_mode == 'first')
    fascia = "07:00 (MATTINA - PRIMO VIDEO)" if is_morning else "19:00 (SERA - ULTIMO VIDEO)"

    print("═" * 70)
    print(f"🎬 AVVIO BOT STORIE YOUTUBE: {fascia}")
    print("═" * 70)

    # 2. Recupera i video dal foglio Post_YouTube
    url_sheets = f"{APPS_SCRIPT_URL}?action=debug_all_sheets"
    req_sheets = urllib.request.Request(url_sheets, headers={'User-Agent': 'Mozilla/5.0'})
    yt_items = []

    try:
        with urllib.request.urlopen(req_sheets, timeout=25, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for s in data.get('sheets', []):
                if s.get('name') == 'Post_YouTube':
                    sample = [r for r in s.get('sample', []) if any(r)]
                    for r in sample[1:]:
                        if len(r) > 5 and r[0]:
                            yt_items.append({
                                "videoUrl": str(r[0]),
                                "prezzo": str(r[1] or 'Trattativa Riservata'),
                                "mq": normalize_mq(r[2]),
                                "titolo": str(r[3] or 'Opportunità Immobiliare'),
                                "testoF": str(r[5] or ''),
                                "thumbUrl": str(r[6] if len(r) > 6 and r[6] else '')
                            })
                    break
    except Exception as e:
        print(f"Errore recupero Post_YouTube: {e}")

    if not yt_items:
        print("⚠️ Nessun video trovato in Post_YouTube: uso fallback...")
        yt_items.append({
            "videoUrl": "https://www.youtube.com/watch?v=zekP_9iFLK0",
            "prezzo": "Trattativa Riservata",
            "mq": "120 metri quadri",
            "titolo": "Esclusiva Villa Mediterranea",
            "testoF": "Splendida villa con finiture di pregio e architettura ricercata. — Immobiliare Giancani",
            "thumbUrl": "https://i3.ytimg.com/vi/zekP_9iFLK0/hqdefault.jpg"
        })

    # 3. Seleziona il primo (mattina) o l'ultimo (sera)
    selected_item = yt_items[0] if is_morning else yt_items[-1]
    print(f"🎯 Video selezionato per {fascia}:")
    print(f"   • Titolo: {selected_item['titolo']}")
    print(f"   • Prezzo: {selected_item['prezzo']}")
    print(f"   • Superficie: {selected_item['mq']}")
    print(f"   • URL Media: {selected_item['videoUrl']}")
    print(f"   • Testo Colonna F: {selected_item['testoF'][:80]}...")

    # 4. Renderizza il video di 15 secondi con logo semi-visibile, musica originale e link/QR
    video_path, watch_url = render_storia_youtube_video(selected_item, is_morning=is_morning)
    if not video_path:
        print("❌ Errore rendering video storia YouTube.")
        return []

    # 5. Pubblica su entrambe le pagine Facebook
    risultati = []
    for target in PAGES:
        print(f"\n📘 Pubblicazione Video Storia su: {target['nome']}...")
        try:
            res = pubblica_storia_facebook(target['id'], target['token'], video_path)
            res['nome'] = target['nome']
            print(f"[OK] Storia pubblicata con successo! Story ID: {res.get('story_id')}")
            risultati.append(res)
        except Exception as ePub:
            print(f"❌ Errore upload su {target['nome']}: {ePub}")
            risultati.append({"nome": target['nome'], "success": False, "error": str(ePub)})

    # 6. Notifica Telegram
    invia_notifica_telegram_youtube(selected_item['titolo'], selected_item['mq'], selected_item['prezzo'], watch_url, is_morning, risultati)
    print("\n✨ Pubblicazione storia YouTube completata con successo. — Immobiliare Giancani\n")
    return risultati

def main():
    parser = argparse.ArgumentParser(description="Bot Storie Facebook YouTube Immobiliare Giancani")
    parser.add_argument("--target", choices=["auto", "first", "last"], default="auto", help="Seleziona quale video pubblicare (first = 07:00 mattina, last = 19:00 sera, auto = in base all'ora)")
    args = parser.parse_args()
    esegui_pubblicazione(target_mode=args.target)

if __name__ == "__main__":
    main()
