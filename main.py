#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  🎬 BOT REELS MULTI-MODALITÀ MASTER & SOCIAL DISPATCHER
  - Generazione rapida (modello turbo/standard anti-timeout)
  - Vero Stile Cartone Animato 2D Disegnato a Mano (No sfondi digitali generici)
  - Varietà garantita: illustrazioni d'azione diverse per ogni scena
  - Risoluzione 9:16 reale con Smart Crop-Fit (Zero deformazioni)
  - Badge Titolo presente SOLO all'inizio per la prima scena (poi scompare)
  - Sottotitoli Comic Pop ad altissima leggibilità
  - Routing Social Completo (Telegram, YouTube x2, Facebook Pagine x3)
==============================================================================
"""

import os
import sys
import csv
import json
import time
import random
import asyncio
import argparse
import subprocess
import urllib.parse
import re
import datetime
import requests
import urllib3
from PIL import Image, ImageDraw, ImageFont, ImageOps

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Patch aiohttp per ambienti CI e Runner
try:
    import aiohttp
    orig_ws_connect = aiohttp.ClientSession.ws_connect
    def patched_ws_connect(self, *args, **kwargs):
        kwargs['ssl'] = False
        return orig_ws_connect(self, *args, **kwargs)
    aiohttp.ClientSession.ws_connect = patched_ws_connect
except Exception:
    pass

# ── CONFIGURAZIONI GLOBALI & PATH ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "video_storie_output")
CSV_CLASSICI_PATH = os.path.join(BASE_DIR, "database_storie_classici.csv")
CSV_BIBBIA_PATH = os.path.join(BASE_DIR, "database_storie_bibliche.csv")
CSV_MITOLOGIA_PATH = os.path.join(BASE_DIR, "database_storie_mitologia.csv")
CSV_PILLOLE_PATH = os.path.join(BASE_DIR, "database_pillole_immobiliari_legali.csv")
MUSIC_DIR = os.path.join(BASE_DIR, "musica_sottofondo")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── CREDENZIALI SOCIAL ─────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1723292483")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@immobiliaregiancani")

# Pagine Facebook
FB_PAGE_ID_ANTONIO = os.environ.get("FB_PAGE_ID", "108297671444008")
FB_PAGE_TOKEN_ANTONIO = os.environ.get("FB_PAGE_TOKEN", "EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia")

FB_PAGE_ID_GIANCANI = os.environ.get("FB_PAGE_ID_GIANCANI", FB_PAGE_ID_ANTONIO)
FB_PAGE_TOKEN_GIANCANI = os.environ.get("FB_PAGE_TOKEN_GIANCANI", FB_PAGE_TOKEN_ANTONIO)

FB_PAGE_ID_BIBBIA = os.environ.get("FB_PAGE_ID_BIBBIA", FB_PAGE_ID_ANTONIO)
FB_PAGE_TOKEN_BIBBIA = os.environ.get("FB_PAGE_TOKEN_BIBBIA", FB_PAGE_TOKEN_ANTONIO)

# YouTube OAuth API
YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN_GIANCANI = os.environ.get("YOUTUBE_REFRESH_TOKEN_GIANCANI", "")
YOUTUBE_REFRESH_TOKEN_BIBBIA = os.environ.get("YOUTUBE_REFRESH_TOKEN_BIBBIA", "")

def get_ffmpeg_binary():
    import shutil
    binary = shutil.which("ffmpeg")
    if binary: return binary
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        local_win = os.path.join(BASE_DIR, "ffmpeg.exe")
        if os.path.exists(local_win): return local_win
        return "ffmpeg"

FFMPEG_EXE = get_ffmpeg_binary()

# ── STILI PROMPT: CARTONE ANIMATO 2D LEGGERI E VELOCI ───────────────────────
STYLE_HEADER = {
    "mitologia": "2D classic colorful cartoon animation cel, bold clean ink outlines, Greek mythology fairytale, expressive characters in action, daylight, vertical 9:16",
    "bibbia": "2D colorful cartoon storybook cel, clean outlines, bright warm colors, expressive characters in action, daylight, vertical 9:16",
    "standard": "2D fairytale cartoon animation cel, clean outlines, rich warm colors, fairytale book aesthetic, vertical 9:16",
    "pillole": "2D modern vector cartoon, clean outlines, bright real estate office, architectural plans, vertical 9:16"
}

STYLE_NEGATIVES = (
    "--no 3d render, cgi, photorealistic, realistic, oil painting, digital landscape, 3d game asset, "
    "blurry, dark, gloomy, empty scenery without characters, photo, monochrome, black screen"
)

# ── ESTRAZIONE RIGOROSA DA CSV ──────────────────────────────────────────────
def estrai_storia_colonna_f(id_richiesto=None, mode="standard"):
    mode = mode.lower()
    if mode in ["mitologia", "mito"]:
        csv_file = CSV_MITOLOGIA_PATH if os.path.exists(CSV_MITOLOGIA_PATH) else CSV_CLASSICI_PATH
        target_mode = "mitologia"
    elif mode in ["bibbia", "fede"]:
        csv_file = CSV_BIBBIA_PATH
        target_mode = "bibbia"
    elif mode in ["pillole", "legale", "immobiliare"]:
        csv_file = CSV_PILLOLE_PATH
        target_mode = "pillole"
    else:
        csv_file = CSV_CLASSICI_PATH
        target_mode = "standard"

    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Database CSV non trovato: {csv_file}")

    storie = []
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row or len(row) < 4:
                continue

            if target_mode == "bibbia":
                storie.append({
                    "id": row[0].strip(),
                    "titolo": row[1].strip(),
                    "autore": row[2].strip(),
                    "categoria": "bibbia",
                    "testo_colonna_f": row[3].strip(),
                    "prompts_g": row[4].strip() if len(row) > 4 else ""
                })
            elif target_mode == "pillole":
                col_f = row[5].strip() if len(row) > 5 else row[3].strip()
                storie.append({
                    "id": row[0].strip(),
                    "titolo": row[2].strip() if len(row) > 2 else row[1].strip(),
                    "autore": row[3].strip() if len(row) > 3 else "Immobiliare Giancani",
                    "categoria": "pillole",
                    "testo_colonna_f": col_f,
                    "prompts_g": ""
                })
            elif target_mode == "mitologia" and csv_file == CSV_MITOLOGIA_PATH:
                col_f = row[5].strip() if len(row) > 5 else row[3].strip()
                storie.append({
                    "id": row[0].strip(),
                    "titolo": row[1].strip(),
                    "autore": row[2].strip() if len(row) > 2 else "Miti dell'Antica Grecia",
                    "categoria": "mitologia",
                    "testo_colonna_f": col_f,
                    "prompts_g": row[6].strip() if len(row) > 6 else ""
                })
            else:
                if len(row) >= 6:
                    genere = row[4].strip() if len(row) > 4 else ""
                    is_mito = any(k in (genere + " " + row[1]).lower() for k in ["mito", "greco", "olimp", "medusa", "perseo", "zeus", "atalanta", "odissea", "iliade", "pan", "paride"])
                    cat_item = "mitologia" if is_mito else "standard"
                    storie.append({
                        "id": row[0].strip(),
                        "titolo": row[1].strip(),
                        "autore": row[2].strip(),
                        "genere": genere,
                        "categoria": cat_item,
                        "testo_colonna_f": row[5].strip(),
                        "prompts_g": row[6].strip() if len(row) > 6 else ""
                    })

    if not storie:
        raise ValueError(f"Nessuna storia trovata in: {csv_file}")

    if target_mode == "mitologia":
        candidati = [s for s in storie if s.get("categoria") == "mitologia"]
        if not candidati: candidati = storie
    elif target_mode == "standard":
        candidati = [s for s in storie if s.get("categoria") == "standard"]
        if not candidati: candidati = storie
    else:
        candidati = storie

    if id_richiesto:
        trovate = [s for s in candidati if str(s["id"]).lower() == str(id_richiesto).lower()]
        storia = trovate[0] if trovate else random.choice(candidati)
    else:
        storia = random.choice(candidati)

    print("\n" + "="*70)
    print(f"📖 [EPISODIO] ID: {storia['id']} | Modalità: {target_mode.upper()}")
    print(f"📌 Titolo: «{storia['titolo']}»")
    print("="*70 + "\n")
    return storia, target_mode

# ── STRUTTURA SCENE ESTESA (2m30s - 3m00s) ──────────────────────────────────
def crea_struttura_scene(storia, target_mode):
    testo_f = storia["testo_colonna_f"]

    if "|||" in testo_f:
        frasi_raw = [f.strip() for f in testo_f.split("|||") if f.strip()]
    else:
        frasi_raw = [f.strip() for f in re.split(r'(?<=[.!?])\s+', testo_f) if f.strip()]

    frasi = []
    chunk = ""
    target_chunk_len = 110 if target_mode in ["standard", "mitologia"] else 130

    for f in frasi_raw:
        if len(chunk) + len(f) < target_chunk_len:
            chunk = (chunk + " " + f).strip()
        else:
            if chunk: frasi.append(chunk)
            chunk = f
    if chunk:
        frasi.append(chunk)

    if not frasi:
        frasi = [testo_f]

    if target_mode == "mitologia":
        if not any(k in frasi[0].lower() for k in ["mito", "leggenda"]):
            frasi[0] = f"Oggi vi raccontiamo un mito leggendario: {storia['titolo']}. {frasi[0]}"
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + ". Grandi miti insegnano che determinazione e armonia superano ogni ostacolo. Per la tua casa, scegli la sicurezza di Immobiliare Giancani."
    elif target_mode == "standard":
        if not any(k in frasi[0].lower() for k in ["classici", "gatto", "libro"]):
            frasi[0] = f"Il nostro gatto narratore vi racconta un grande classico: {storia['titolo']} di {storia['autore']}! {frasi[0]}"
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + ". Le grandi storie costruiscono il futuro con passione. Con l'affidabilità di Immobiliare Giancani."
    elif target_mode == "pillole":
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + ". Per una compravendita sicura e tutelata in ogni fase, affidati all'esperienza di Immobiliare Giancani."
    else:
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + " — Con la cura e l'affidabilità di Immobiliare Giancani."

    prompts_raw = [p.strip() for p in storia.get("prompts_g", "").split("|||") if p.strip()]
    scene = []
    num_scene = len(frasi)
    header_style = STYLE_HEADER[target_mode]

    for i in range(num_scene):
        p_custom = prompts_raw[i] if i < len(prompts_raw) else ""
        clean_custom = p_custom.replace("pixar 3d style,", "").replace("vertical 9:16", "").strip(" ,.") if p_custom else frasi[i][:65]

        if target_mode == "standard":
            if i == 0:
                full_p = f"{header_style}, cute smiling little orange tabby cat wearing blue sailor striped shirt, sitting on open book {STYLE_NEGATIVES}"
            else:
                full_p = f"{header_style}, action scene: {clean_custom}, dynamic characters {STYLE_NEGATIVES}"
        elif target_mode == "mitologia":
            full_p = f"{header_style}, myth of {storia['titolo']}, scene: {clean_custom}, expressive animated Greek mythological figures in action {STYLE_NEGATIVES}, --no cat, animal pet"
        elif target_mode == "pillole":
            full_p = f"{header_style}, practical real estate guide: {clean_custom} {STYLE_NEGATIVES}, --no cat, animal"
        else:
            full_p = f"{header_style}, sacred history {storia['titolo']}: {clean_custom}, expressive animated biblical characters {STYLE_NEGATIVES}, --no cat, animal"

        scene.append({
            "scena_id": i + 1,
            "testo": frasi[i],
            "prompt": full_p,
            "is_intro": (i == 0),
            "is_outro": (i == num_scene - 1)
        })

    return scene

# ── VOCE NARRANTE NEURALE ───────────────────────────────────────────────────
async def genera_voce_edge_tts(testo, file_audio, voce="it-IT-ElsaNeural"):
    success = False
    try:
        import edge_tts
        comm = edge_tts.Communicate(testo, voce, rate="-5%", pitch="+0Hz")
        await asyncio.wait_for(comm.save(file_audio), timeout=30)
        if os.path.exists(file_audio) and os.path.getsize(file_audio) > 1000:
            success = True
    except Exception as e:
        print(f"  ⚠️ Edge-TTS avviso ({e}), attivo fallback gTTS...")

    if not success:
        try:
            from gtts import gTTS
            tts = gTTS(text=testo, lang='it', slow=False)
            tts.save(file_audio)
            success = True
        except Exception as err:
            print(f"  ❌ Errore fallback gTTS: {err}")
            
    return success

# ── ADATTAMENTO NATIVO 9:16 (SMART CROP CENTRALE SENZA DEFORMAZIONI) ────────
def ritaglia_e_adatta_9_16(sorgente_path, destinazione_path, target_size=(720, 1280)):
    with Image.open(sorgente_path) as im:
        im_rgb = im.convert("RGB")
        im_crop = ImageOps.fit(im_rgb, target_size, Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        im_crop.save(destinazione_path, "JPEG", quality=95)

# ── DOWNLOAD IMMAGINI OTTIMIZZATO (VELOCE, DIVERSO PER SCENA, STILE 2D) ─────
ULTIMA_IMMAGINE_VALIDA = None

def scarica_immagine_pollinations(prompt, output_img, seed=100, target_mode="standard", is_intro=False):
    global ULTIMA_IMMAGINE_VALIDA

    # 1. Controllo cache valida
    if os.path.exists(output_img) and os.path.getsize(output_img) > 15000:
        try:
            with Image.open(output_img) as im_chk:
                im_chk.verify()
            ULTIMA_IMMAGINE_VALIDA = output_img
            return True
        except Exception:
            if os.path.exists(output_img): os.remove(output_img)

    # 2. Master gatto solo per i Grandi Classici
    assets_dir = os.path.join(BASE_DIR, "assets")
    if target_mode == "standard" and is_intro:
        cat_ref = os.path.join(assets_dir, "cat_master_reference.jpg")
        if os.path.exists(cat_ref):
            try:
                ritaglia_e_adatta_9_16(cat_ref, output_img)
                ULTIMA_IMMAGINE_VALIDA = output_img
                return True
            except Exception:
                pass

    # 3. Prompt compatto e mirato per prevenire timeout da parsing
    clean_p = prompt.replace("traditional 2D hand-drawn animated film cel,", "2D cartoon animation,")
    clean_p = clean_p.replace("classic cartoon storybook illustration,", "storybook cel,")
    clean_p = clean_p.strip(" ,.")[:175]
    encoded = urllib.parse.quote(clean_p)

    # 4. Strategia a risposta rapida (Timeout 16s su modelli leggeri)
    endpoints = [
        f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&nologo=true&seed={seed}&model=turbo",
        f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&nologo=true&seed={seed + 88}",
        f"https://image.pollinations.ai/prompt/{encoded}?width=576&height=1024&nologo=true&seed={seed + 199}&model=turbo"
    ]

    for attempt, url in enumerate(endpoints, start=1):
        ts = int(time.time() * 1000)
        url_with_ts = f"{url}&ts={ts}"
        try:
            print(f"  🎨 [Download Scena 2D] Tentativo {attempt}/3...", flush=True)
            resp = requests.get(url_with_ts, timeout=(6, 16), verify=False, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and len(resp.content) > 10000:
                tmp_file = f"{output_img}.tmp"
                with open(tmp_file, "wb") as f:
                    f.write(resp.content)
                try:
                    with Image.open(tmp_file) as valid_pil:
                        valid_pil.verify()
                    ritaglia_e_adatta_9_16(tmp_file, output_img)
                    if os.path.exists(tmp_file): os.remove(tmp_file)
                    print(f"  ✅ Scena scaricata con successo in stile Cartone 2D!")
                    ULTIMA_IMMAGINE_VALIDA = output_img
                    time.sleep(3)
                    return True
                except Exception:
                    if os.path.exists(tmp_file): os.remove(tmp_file)
        except Exception as e_net:
            print(f"  ⚠️ Tentativo {attempt} fallito ({e_net.__class__.__name__}), cambio endpoint...")
        time.sleep(2)

    # 5. Continuità visiva: riutilizzo ultima immagine valida solo come emergenza
    if ULTIMA_IMMAGINE_VALIDA and os.path.exists(ULTIMA_IMMAGINE_VALIDA):
        print(f"  🔄 [Continuità Visiva] Riutilizzo ultima illustrazione cartoon...")
        ritaglia_e_adatta_9_16(ULTIMA_IMMAGINE_VALIDA, output_img)
        return True

    # 6. Fallback illustrato d'emergenza luminoso (MAI nero o vuoto)
    print(f"  🎨 [Emergenza] Generazione sfondo solare illustrato...")
    img = Image.new("RGB", (720, 1280), color=(45, 100, 180))
    draw = ImageDraw.Draw(img)
    for y in range(1280):
        ratio = y / 1280.0
        r = int(50 + ratio * 80)
        g = int(120 + ratio * 90)
        b = int(210 + ratio * 30)
        draw.line([(0, y), (720, y)], fill=(r, g, b))
    draw.ellipse([260, 180, 460, 380], fill=(255, 220, 100))
    img.save(output_img, "JPEG", quality=95)
    ULTIMA_IMMAGINE_VALIDA = output_img
    return True

# ── OVERLAY GRAFICO: BADGE TITOLO (SOLO SCENA 1) & SOTTOTITOLI 3D POP ───────
def crea_overlay_grafico(testo, titolo_libro, autore, output_overlay, is_intro=False, is_outro=False, target_mode="standard", idx=1):
    img = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def carica_font_comic(size_target):
        font_candidates = [
            os.path.join(BASE_DIR, "assets", "fonts", "KomikaAxis.ttf"),
            os.path.join(BASE_DIR, "assets", "fonts", "Bangers.ttf"),
            os.path.join(BASE_DIR, "assets", "fonts", "Montserrat-Black.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "C:\\Windows\\Fonts\\comicbd.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf"
        ]
        for f in font_candidates:
            if os.path.exists(f):
                try: return ImageFont.truetype(f, size_target)
                except: pass
        return ImageFont.load_default()

    font_title_badge = carica_font_comic(34)
    font_category_badge = carica_font_comic(22)
    font_sub = carica_font_comic(34)
    font_brand = carica_font_comic(30)

    # 1. BADGE TITOLO: PRESENTE RIGOROSAMENTE SOLO NELLA PRIMA SCENA (idx == 1)
    if is_intro and idx == 1:
        if target_mode == "pillole":
            draw.rounded_rectangle([45, 55, 675, 135], radius=18, fill=(12, 18, 30, 225), outline=(235, 190, 85, 240), width=2)
            draw.text((360, 95), "PILLOLA IMMOBILIARE & LEGALE", fill=(255, 230, 150), font=font_category_badge, anchor="mm")
        else:
            card_top = 110
            card_bottom = 235
            draw.rounded_rectangle([38, card_top + 4, 682, card_bottom + 4], radius=22, fill=(0, 0, 0, 190))
            draw.rounded_rectangle([35, card_top, 685, card_bottom], radius=20, fill=(12, 20, 36, 230), outline=(255, 215, 65, 255), width=3)
            
            etichette = {
                "mitologia": "★ MITI DELL'ANTICA GRECIA ★",
                "bibbia": "★ STORIE DELLA BIBBIA ★",
                "standard": "★ I GRANDI CLASSICI ★"
            }
            cat_text = etichette.get(target_mode, "★ GRANDE STORIA ★")
            draw.text((360, card_top + 34), cat_text, fill=(255, 215, 75), font=font_category_badge, anchor="mm")
            
            titolo_display = titolo_libro.upper()
            if len(titolo_display) > 25:
                titolo_display = titolo_display[:23] + "..."
            draw.text((360, card_top + 84), titolo_display, fill=(255, 255, 255), font=font_title_badge, anchor="mm")

    # 2. SOTTOTITOLI STILE CARTOON STICKER (Contorno spesso e ombra 3D)
    import textwrap
    lines = textwrap.wrap(testo, width=25)
    line_h = 48
    total_h = len(lines) * line_h
    start_y = 1040 - (total_h // 2)

    for l_idx, line in enumerate(lines):
        y_pos = start_y + (l_idx * line_h)
        for offset in range(1, 6):
            draw.text((360 + offset, y_pos + offset), line, fill=(0, 0, 0, 255), font=font_sub, anchor="mm")
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx != 0 or dy != 0:
                    draw.text((360 + dx, y_pos + dy), line, fill=(0, 0, 0, 255), font=font_sub, anchor="mm")
        colore_faccia = (255, 255, 220) if l_idx % 2 == 0 else (255, 235, 120)
        draw.text((360, y_pos), line, fill=colore_faccia, font=font_sub, anchor="mm")

    # 3. OUTRO CARD (Scena finale)
    if is_outro:
        draw.rounded_rectangle([45, 1090, 675, 1225], radius=18, fill=(10, 15, 25, 235), outline=(245, 195, 75, 245), width=2)
        draw.text((360, 1135), "IMMOBILIARE GIANCANI", fill=(245, 205, 85), font=font_brand, anchor="mm")
        draw.text((360, 1180), "La Guida Sicura per la Tua Prossima Casa", fill=(255, 255, 255), font=font_category_badge, anchor="mm")

    img.save(output_overlay, "PNG")

# ── CALCOLO DURATA AUDIO ───────────────────────────────────────────────────
def ottieni_durata_audio(audio_path):
    cmd = [FFMPEG_EXE, "-i", audio_path]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    _, stderr = p.communicate()
    for line in stderr.decode('utf-8', errors='ignore').split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return max(4.0, float(h)*3600 + float(m)*60 + float(s))
    return 8.0

# ── MONTAGGIO CLIP: KEN BURNS CON PRE-SCALING 9:16 (NESSUN ALLARGAMENTO) ────
def crea_clip_ken_burns(img_path, audio_path, overlay_path, clip_output, idx):
    durata = ottieni_durata_audio(audio_path) + 0.35
    num_frames = int(durata * 25)

    if idx % 2 == 1:
        zoom_filter = f"zoompan=z='min(zoom+0.0009,1.15)':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"
    else:
        zoom_filter = f"zoompan=z='if(lte(zoom,1.0),1.15,max(1.001,zoom-0.0009))':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"

    filter_complex = (
        f"[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,{zoom_filter}[bg];"
        f"[bg][1:v]overlay=0:0[v]"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", img_path,
        "-i", overlay_path,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(durata),
        clip_output
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# ── MONTAGGIO VIDEO FINALE ─────────────────────────────────────────────────
def monta_video_finale(clips, output_video, durata_totale):
    concat_list = os.path.join(OUTPUT_DIR, "concat_clips.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c.replace(os.sep, '/')}'\n")

    video_temp = os.path.join(OUTPUT_DIR, "temp_video_nomusic.mp4")
    subprocess.run([
        FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list, "-c", "copy", video_temp
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    fallback_music = os.path.join(OUTPUT_DIR, "ambient_fallback.mp3")
    if not os.path.exists(fallback_music):
        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "lavfi", "-i", f"sine=frequency=196:duration={durata_totale+10}",
            "-af", "volume=0.08,lowpass=f=400,afade=t=in:ss=0:d=2,afade=t=out:st=15:d=3",
            "-c:a", "libmp3lame", "-b:a", "128k", fallback_music
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    filter_mix = (
        f"[1:a]volume=0.09,afade=t=in:ss=0:d=1.5,afade=t=out:st={max(2, durata_totale - 2.5)}:d=2.5[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    cmd_mix = [
        FFMPEG_EXE, "-y",
        "-i", video_temp,
        "-stream_loop", "-1", "-i", fallback_music,
        "-filter_complex", filter_mix,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", output_video
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    if os.path.exists(video_temp):
        os.remove(video_temp)

# ── ROUTING SOCIAL MULTI-CANALE ─────────────────────────────────────────────
def invia_su_telegram(video_path, storia, target_mode):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    testo_p = storia['testo_colonna_f'].replace('|||', ' ')
    estratto = testo_p[:330] + "..." if len(testo_p) > 330 else testo_p

    caption = (
        f"🎬 <b>{storia['titolo']}</b> ({target_mode.upper()})\n\n"
        f"«{estratto}»\n\n"
        f"⭐ <b>IMMOBILIARE GIANCANI</b>"
    )

    destinazioni = [TELEGRAM_CHAT_ID]
    if TELEGRAM_CHANNEL_ID and TELEGRAM_CHANNEL_ID not in destinazioni:
        destinazioni.append(TELEGRAM_CHANNEL_ID)

    for chat in destinazioni:
        try:
            with open(video_path, "rb") as vf:
                requests.post(url, data={"chat_id": chat, "caption": caption, "parse_mode": "HTML"}, files={"video": vf}, timeout=120)
            print(f"✅ [TELEGRAM] Inviato a {chat}")
        except Exception as e:
            print(f"❌ [TELEGRAM] Errore: {e}")
    return True

def pubblica_facebook_reel_su_pagina(page_id, page_token, video_path, caption, label=""):
    if not page_token or not page_id: return False
    try:
        url_reels = f"https://graph.facebook.com/v19.0/{page_id}/video_reels"
        r1 = requests.post(url_reels, data={"upload_phase": "start", "access_token": page_token}, timeout=25).json()
        vid, up_url = r1.get("video_id"), r1.get("upload_url")
        if not vid or not up_url: return False

        with open(video_path, "rb") as vf:
            v_bytes = vf.read()
        headers = {"Authorization": f"OAuth {page_token}", "offset": "0", "file_size": str(len(v_bytes)), "Content-Type": "application/octet-stream"}
        requests.post(up_url, data=v_bytes, headers=headers, timeout=180)

        requests.post(url_reels, data={"upload_phase": "finish", "access_token": page_token, "video_id": vid, "video_state": "PUBLISHED", "description": caption}, timeout=35)
        print(f"✅ [FACEBOOK REEL] Pubblicato su: {label}")
        return True
    except Exception as e:
        print(f"❌ [FACEBOOK REEL] Errore su {label}: {e}")
        return False

def pubblica_facebook_post_testuale(page_id, page_token, testo, label=""):
    if not page_token or not page_id: return False
    try:
        url_feed = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        requests.post(url_feed, data={"message": testo, "access_token": page_token}, timeout=25)
        print(f"✅ [FACEBOOK POST] Pubblicato su: {label}")
        return True
    except Exception as e:
        print(f"❌ [FACEBOOK POST] Errore su {label}: {e}")
        return False

def ottieni_access_token_da_refresh(refresh_token):
    if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET or not refresh_token:
        return None
    try:
        url_token = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": YOUTUBE_CLIENT_ID,
            "client_secret": YOUTUBE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        res = requests.post(url_token, data=data, timeout=15).json()
        return res.get("access_token")
    except Exception:
        return None

def pubblica_youtube_short(video_path, titolo, descrizione, tags, refresh_token, nome_canale=""):
    access_token = ottieni_access_token_da_refresh(refresh_token)
    if not access_token:
        print(f"⚠️ [YOUTUBE] Token mancante per {nome_canale}. Salto upload.")
        return False
    try:
        url_upload = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
        meta = {
            "snippet": {"title": f"{titolo} #Shorts"[:100], "description": f"{descrizione}\n\n#Shorts", "tags": tags, "categoryId": "22"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }
        headers_init = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=UTF-8", "X-Upload-Content-Type": "video/mp4"}
        r_init = requests.post(url_upload, json=meta, headers=headers_init, timeout=25)
        upload_location = r_init.headers.get("Location")
        if not upload_location: return False

        with open(video_path, "rb") as vf: v_data = vf.read()
        headers_put = {"Authorization": f"Bearer {access_token}", "Content-Type": "video/mp4"}
        r_upload = requests.put(upload_location, data=v_data, headers=headers_put, timeout=240)
        if r_upload.status_code in [200, 201]:
            print(f"✅ [YOUTUBE SHORTS] Pubblicato su: {nome_canale}!")
            return True
    except Exception as ey:
        print(f"❌ [YOUTUBE] Errore su {nome_canale}: {ey}")
    return False

def esegui_routing_pubblicazione(video_path, storia, target_mode):
    print("\n" + "="*70)
    print(f"🚀 [DISPATCHER SOCIAL] Distribuzione in corso per: {target_mode.upper()}")
    print("="*70)

    testo_pulito = storia['testo_colonna_f'].replace('|||', ' ').strip()
    titolo = storia['titolo']

    # 1. Telegram (Tutti)
    invia_su_telegram(video_path, storia, target_mode)

    # 2. Routing specifico per modalità
    if target_mode == "bibbia":
        caption = f"📖 STORIE DELLA BIBBIA — «ETERNO NOSTRA GIUSTIZIA»\n\n📜 {titolo}\n\n«{testo_pulito[:450]}...»\n\n#StorieBibliche #Bibbia #EternoNostraGiustizia"
        pubblica_facebook_reel_su_pagina(FB_PAGE_ID_BIBBIA, FB_PAGE_TOKEN_BIBBIA, video_path, caption, "FB Eterno Nostra Giustizia")
        pubblica_facebook_reel_su_pagina(FB_PAGE_ID_ANTONIO, FB_PAGE_TOKEN_ANTONIO, video_path, caption, "FB Antonio Giancani")
        pubblica_youtube_short(video_path, f"Storia Biblica: {titolo}", caption, ["Bibbia", "Eterno nostra giustizia"], YOUTUBE_REFRESH_TOKEN_BIBBIA, "Eterno nostra giustizia")

    elif target_mode == "mitologia":
        caption = f"🏛️ MITI DELL'ANTICA GRECIA\n\n⚡ {titolo}\n\n«{testo_pulito[:450]}...»\n\nCon la visione e la determinazione di Immobiliare Giancani.\n\n#MitologiaGreca #MitiGreci #AntonioGiancani"
        pubblica_facebook_reel_su_pagina(FB_PAGE_ID_ANTONIO, FB_PAGE_TOKEN_ANTONIO, video_path, caption, "FB Antonio Giancani")

    elif target_mode == "pillole":
        caption = f"🏢 PILLOLA IMMOBILIARE & TUTELA LEGALE\n\n📜 {titolo}\n\n«{testo_pulito[:450]}...»\n\nPer una compravendita sicura, rivolgiti a Immobiliare Giancani.\n\n#ImmobiliareGiancani #ConsulenzaLegale #Casa"
        pubblica_facebook_reel_su_pagina(FB_PAGE_ID_GIANCANI, FB_PAGE_TOKEN_GIANCANI, video_path, caption, "FB Immobiliare Giancani (Reel)")
        
        post_completo = f"🏢 PILLOLA DEL GIORNO: {titolo.upper()}\n\n{storia['testo_colonna_f'].replace('|||', chr(10)+chr(10))}\n\n━━━━━━━━━━━━━━━━━━━━\n🏠 IMMOBILIARE GIANCANI\nAffidabilità e Tutela per la Tua Casa."
        pubblica_facebook_post_testuale(FB_PAGE_ID_GIANCANI, FB_PAGE_TOKEN_GIANCANI, post_completo, "FB Immobiliare Giancani (Post)")
        pubblica_facebook_reel_su_pagina(FB_PAGE_ID_ANTONIO, FB_PAGE_TOKEN_ANTONIO, video_path, caption, "FB Antonio Giancani")
        pubblica_youtube_short(video_path, f"Pillola Immobiliare: {titolo}", caption, ["Immobiliare Giancani", "Casa"], YOUTUBE_REFRESH_TOKEN_GIANCANI, "Immobiliare Giancani")

    else:  # standard libri classici
        caption = f"📚 I GRANDI CLASSICI DELLA LETTERATURA\n\n📖 {titolo} di {storia.get('autore', '')}\n\n«{testo_pulito[:450]}...»\n\nCon la passione di Immobiliare Giancani.\n\n#GrandiClassici #Libri #AntonioGiancani"
        pubblica_facebook_reel_su_pagina(FB_PAGE_ID_ANTONIO, FB_PAGE_TOKEN_ANTONIO, video_path, caption, "FB Antonio Giancani")

# ── ORCHESTRATORE PIPELINE ──────────────────────────────────────────────────
async def esegui_pipeline(story_id=None, voice="it-IT-ElsaNeural", mode="standard"):
    storia, target_mode = estrai_storia_colonna_f(id_richiesto=story_id, mode=mode)
    scene = crea_struttura_scene(storia, target_mode)

    clips = []
    durata_totale = 0.0

    print(f"🎬 Avvio produzione di {len(scene)} scene per target 2:30 - 3:00 minuti...")

    for idx, s in enumerate(scene, start=1):
        base_name = f"{target_mode}_{storia['id']}_scena_{idx}"
        audio_file = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
        img_file = os.path.join(OUTPUT_DIR, f"{base_name}.jpg")
        overlay_file = os.path.join(OUTPUT_DIR, f"{base_name}_ov.png")
        clip_file = os.path.join(OUTPUT_DIR, f"{base_name}_clip.mp4")

        # 1. Voce narrante
        await genera_voce_edge_tts(s["testo"], audio_file, voce=voice)
        durata_totale += ottieni_durata_audio(audio_file)

        # 2. Immagine Cartoon 2D rapida
        seed = int(storia["id"]) * 100 + idx if str(storia["id"]).isdigit() else idx * 100
        scarica_immagine_pollinations(s["prompt"], img_file, seed=seed, target_mode=target_mode, is_intro=s["is_intro"])

        # 3. Overlay Comic Pop (Badge Titolo presente SOLO su scena 1)
        crea_overlay_grafico(s["testo"], storia["titolo"], storia.get("autore", ""), overlay_file, is_intro=s["is_intro"], is_outro=s["is_outro"], target_mode=target_mode, idx=idx)

        # 4. Clip Ken Burns
        crea_clip_ken_burns(img_file, audio_file, overlay_file, clip_file, idx)
        clips.append(clip_file)

    video_finale = os.path.join(OUTPUT_DIR, f"reel_{target_mode}_{storia['id']}.mp4")
    monta_video_finale(clips, video_finale, durata_totale)

    minuti = int(durata_totale // 60)
    secondi = int(durata_totale % 60)
    print("\n" + "="*70)
    print(f"🎉 VIDEO COMPLETATO: {video_finale}")
    print(f"⏱️ Durata Effettiva: {minuti}m {secondi}s")
    print("="*70 + "\n")

    esegui_routing_pubblicazione(video_finale, storia, target_mode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot Reels Multi-Modalità Master")
    parser.add_argument("--mode", type=str, default="standard", 
                        choices=["standard", "bibbia", "pillole", "mitologia"])
    parser.add_argument("--id", type=str, default=None)
    parser.add_argument("--voice", type=str, default="it-IT-ElsaNeural")
    args = parser.parse_args()

    asyncio.run(esegui_pipeline(story_id=args.id, voice=args.voice, mode=args.mode))
