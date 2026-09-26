#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  🎬 BOT REELS MULTI-MODALITÀ MASTER (2m30s - 3m00s)
  1. Banner superiore SOLO per Agenzia Immobiliare (Pillole)
  2. Font stile Cartoon/Fumetto grande con stroke marcato (NO riquadri opachi)
  3. Controllo integrità download Pollinations con retry e fallback garantito
  4. Durata reale 150s - 180s con narrazione ricca ed estesa per Mitologia e Libri
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
import requests
import urllib3
from PIL import Image, ImageDraw, ImageFont

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import aiohttp
    orig_ws_connect = aiohttp.ClientSession.ws_connect
    def patched_ws_connect(self, *args, **kwargs):
        kwargs['ssl'] = False
        return orig_ws_connect(self, *args, **kwargs)
    aiohttp.ClientSession.ws_connect = patched_ws_connect
except Exception:
    pass

# ── CONFIGURAZIONI AMBIENTE & PATH ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "video_storie_output")
CSV_CLASSICI_PATH = os.path.join(BASE_DIR, "database_storie_classici.csv")
CSV_BIBBIA_PATH = os.path.join(BASE_DIR, "database_storie_bibliche.csv")
CSV_PILLOLE_PATH = os.path.join(BASE_DIR, "database_pillole_immobiliari_legali.csv")
MUSIC_DIR = os.path.join(BASE_DIR, "musica_sottofondo")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Credenziali Social
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1723292483")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@immobiliaregiancani")

FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "108297671444008")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia")

def get_ffmpeg_binary():
    import shutil
    binary = shutil.which("ffmpeg")
    if binary:
        return binary
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        local_win = os.path.join(BASE_DIR, "ffmpeg.exe")
        if os.path.exists(local_win):
            return local_win
        return "ffmpeg"

FFMPEG_EXE = get_ffmpeg_binary()

# ── PROMPT VISIVI SPECIALIZZATI ─────────────────────────────────────────────
STYLE_PROMPTS = {
    "mitologia": (
        "Dynamic 2D animated comic book style, Greek mythology epic fantasy, vibrant saturated colors, "
        "bold black ink outlines, cel shading, heroic composition, cinematic lighting. "
        "--no 3d render, CGI, glossy, photorealistic, bad anatomy, cat, feline, pet"
    ),
    "bibbia": (
        "Luminous classical sacred art illustration, warm golden atmosphere, soft detailed line art, "
        "reverent narrative painting on aged paper texture. --no cat, kitten, animal, 3d, CGI"
    ),
    "standard": (
        "Whimsical classic cartoon storybook illustration, rich colorful hand-drawn style, bold ink contours, "
        "cozy fairytale lighting, high quality story cel. --no 3d render, CGI, glossy, photo"
    ),
    "pillole": (
        "Modern clean vector illustration, prestigious notary and real estate office, architectural blueprint, "
        "elegant desk, bright ambient lighting. --no cat, feline, dog, pet, animal, 3d, CGI"
    )
}

# ── ESTRAZIONE RIGOROSA DA CSV ──────────────────────────────────────────────
def estrai_storia_colonna_f(id_richiesto=None, mode="standard"):
    mode = mode.lower()
    if mode in ["mitologia", "mito"]:
        csv_file = CSV_CLASSICI_PATH
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
            else:
                if len(row) >= 6:
                    genere = row[4].strip() if len(row) > 4 else ""
                    is_mito = any(k in (genere + " " + row[1]).lower() for k in ["mito", "greco", "olimp", "medusa", "perseo", "zeus", "odissea", "iliade"])
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

# ── STRUTTURA SCENE ESTESA (2m30s - 3m00s / 150s - 180s) ───────────────────
def crea_struttura_scene(storia, target_mode):
    testo_f = storia["testo_colonna_f"]

    # Separazione per frasi chiare
    if "|||" in testo_f:
        frasi_raw = [f.strip() for f in testo_f.split("|||") if f.strip()]
    else:
        frasi_raw = [f.strip() for f in re.split(r'(?<=[.!?])\s+', testo_f) if f.strip()]

    # Riorganizzazione in blocchi narrativi distesi per target 2:30 - 3:00 min
    # Per raggiungere 150-180 secondi con Edge-TTS servono circa 11-14 scene da 11-13 secondi
    frasi = []
    chunk = ""
    target_chunk_len = 110 if target_mode in ["standard", "mitologia"] else 135

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

    # Hook iniziale moderno
    if target_mode == "mitologia":
        if not any(k in frasi[0].lower() for k in ["mito", "leggenda"]):
            frasi[0] = f"I grandi miti della storia: {storia['titolo']}. {frasi[0]}"
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + ". Grandi sfide e imprese leggendarie insegnano che la strategia vince ogni ostacolo. Per la tua casa, scegli la guida sicura di Immobiliare Giancani."
    elif target_mode == "standard":
        if not any(k in frasi[0].lower() for k in ["classici", "gatto", "libro"]):
            frasi[0] = f"Oggi con il nostro gatto narratore esploriamo un capolavoro: {storia['titolo']} di {storia['autore']}. {frasi[0]}"
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + ". Le grandi storie continuano a ispirare le nostre scelte. Con la passione e la cura di Immobiliare Giancani."
    elif target_mode == "pillole":
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + ". Per una compravendita senza rischi e tutelata in ogni dettaglio, affidati all'esperienza di Immobiliare Giancani."
    else:
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + " — Con l'affidabilità di Immobiliare Giancani."

    prompts_raw = [p.strip() for p in storia.get("prompts_g", "").split("|||") if p.strip()]
    scene = []
    num_scene = len(frasi)
    base_style = STYLE_PROMPTS[target_mode]

    for i in range(num_scene):
        p_custom = prompts_raw[i] if i < len(prompts_raw) else ""
        clean_custom = p_custom.replace("pixar 3d style,", "").replace("vertical 9:16", "").strip(" ,.") if p_custom else frasi[i][:70]

        if target_mode == "standard":
            if i == 0:
                full_p = "Cute smiling orange tabby kitten wearing sailor striped t-shirt on open antique book, colorful cartoon style --no human, 3d"
            else:
                full_p = f"{base_style}, scene from {storia['titolo']}: {clean_custom} --no 3d, photo"
        elif target_mode == "mitologia":
            full_p = f"{base_style}, Greek epic myth {storia['titolo']}: {clean_custom} --no cat, kitten, animal pet"
        elif target_mode == "pillole":
            full_p = f"{base_style}, legal real estate guide {storia['titolo']}: {clean_custom}"
        else:
            full_p = f"{base_style}, sacred Bible history {storia['titolo']}: {clean_custom}"

        scene.append({
            "scena_id": i + 1,
            "testo": frasi[i],
            "prompt": full_p,
            "is_intro": (i == 0),
            "is_outro": (i == num_scene - 1)
        })

    return scene

# ── VOCE NEURALE DISTESA ────────────────────────────────────────────────────
async def genera_voce_edge_tts(testo, file_audio, voce="it-IT-ElsaNeural"):
    success = False
    try:
        import edge_tts
        # Cadenza rallentata (-5%) per dare respiro narrativo e raggiungere i 2:30 - 3:00 min
        comm = edge_tts.Communicate(testo, voce, rate="-5%", pitch="+0Hz")
        await asyncio.wait_for(comm.save(file_audio), timeout=30)
        if os.path.exists(file_audio) and os.path.getsize(file_audio) > 1000:
            success = True
    except Exception as e:
        print(f"  ⚠️ Edge-TTS avviso ({e}), fallback gTTS...")

    if not success:
        try:
            from gtts import gTTS
            tts = gTTS(text=testo, lang='it', slow=False)
            tts.save(file_audio)
            success = True
        except Exception as err:
            print(f"  ❌ Errore fallback gTTS: {err}")
            
    return success

# ── DOWNLOAD IMMAGINE CON CONTROLLO INTEGRITÀ E RETRY ───────────────────────
def scarica_immagine_pollinations(prompt, output_img, seed=100, target_mode="standard", is_intro=False):
    # 1. Verifica cache integra
    if os.path.exists(output_img) and os.path.getsize(output_img) > 15000:
        try:
            with Image.open(output_img) as im_chk:
                im_chk.verify()
            return True
        except Exception:
            if os.path.exists(output_img): os.remove(output_img)

    # 2. Master Gatto solo per Standard Intro
    assets_dir = os.path.join(BASE_DIR, "assets")
    if target_mode == "standard" and is_intro:
        cat_ref = os.path.join(assets_dir, "cat_master_reference.jpg")
        if os.path.exists(cat_ref):
            try:
                with Image.open(cat_ref) as cimg:
                    cimg.convert("RGB").resize((720, 1280), Image.Resampling.LANCZOS).save(output_img, "JPEG", quality=95)
                return True
            except Exception:
                pass

    # 3. Pulizia prompt
    clean_p = prompt.replace("2D cartoon animation style,", "").strip(" ,.")[:220]
    encoded = urllib.parse.quote(clean_p)

    # 4. Multi-retry su Pollinations con fallback seed
    for attempt in range(1, 4):
        curr_seed = seed + (attempt * 17)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&nologo=true&seed={curr_seed}&model=turbo"
        try:
            resp = requests.get(url, timeout=(6, 15), verify=False, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and len(resp.content) > 12000:
                tmp_file = f"{output_img}.tmp"
                with open(tmp_file, "wb") as f:
                    f.write(resp.content)
                # Verifica validità reale dell'immagine
                try:
                    with Image.open(tmp_file) as valid_pil:
                        valid_pil.verify()
                    with Image.open(tmp_file) as final_pil:
                        final_pil.convert("RGB").save(output_img, "JPEG", quality=95)
                    if os.path.exists(tmp_file): os.remove(tmp_file)
                    return True
                except Exception:
                    if os.path.exists(tmp_file): os.remove(tmp_file)
        except Exception as e_net:
            print(f"  ⚠️ Tentativo {attempt} immagine fallito ({e_net}), riprovo...")
        time.sleep(1.5)

    # 5. Sistema di controllo garantito: genera sfondo ad alta risoluzione senza crash
    print(f"  🎨 Attivato generatore di riserva per {target_mode.upper()}...")
    colori_tema = {
        "mitologia": (38, 24, 18),
        "standard": (20, 28, 42),
        "bibbia": (34, 26, 16),
        "pillole": (18, 26, 38)
    }
    col = colori_tema.get(target_mode, (24, 24, 24))
    img = Image.new("RGB", (720, 1280), color=col)
    draw = ImageDraw.Draw(img)
    for y in range(1280):
        ratio = y / 1280.0
        r = int(col[0] * (1 - ratio * 0.4))
        g = int(col[1] * (1 - ratio * 0.4))
        b = int(col[2] * (1 - ratio * 0.4))
        draw.line([(0, y), (720, y)], fill=(r, g, b))
    img.save(output_img, "JPEG", quality=95)
    return True

# ── OVERLAY GRAFICO: FONT CARTOON & ZERO BANNER (ECCETTO PILLOLE) ───────────
def crea_overlay_grafico(testo, titolo_libro, output_overlay, is_intro=False, is_outro=False, target_mode="standard"):
    img = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Ricerca font stile Cartoon / Comic arrotondato
    def load_cartoon_font(size_target):
        cartoon_candidates = [
            os.path.join(BASE_DIR, "assets", "fonts", "KomikaAxis.ttf"),
            os.path.join(BASE_DIR, "assets", "fonts", "Bangers.ttf"),
            os.path.join(BASE_DIR, "assets", "fonts", "ComicSansMS.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "C:\\Windows\\Fonts\\comicbd.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf"
        ]
        for f in cartoon_candidates:
            if os.path.exists(f):
                try: return ImageFont.truetype(f, size_target)
                except: pass
        return ImageFont.load_default()

    font_sub = load_cartoon_font(35)
    font_badge = load_cartoon_font(23)
    font_brand = load_cartoon_font(32)

    # 1. BANNER SUPERIORE: PRESENTE SOLO ED ESCLUSIVAMENTE PER L'AGENZIA IMMOBILIARE (PILLOLE)
    if target_mode == "pillole" and is_intro:
        draw.rounded_rectangle([50, 50, 670, 125], radius=16, fill=(12, 18, 30, 220), outline=(225, 185, 80, 230), width=2)
        draw.text((360, 87), "PILLOLA IMMOBILIARE & LEGALE", fill=(245, 225, 150), font=font_badge, anchor="mm")

    # 2. SOTTOTITOLI STILE CARTOON: Font grande, vivace, NO riquadri neri ciechi, doppio contorno nero marcato
    import textwrap
    lines = textwrap.wrap(testo, width=27)
    line_h = 46
    total_h = len(lines) * line_h
    start_y = 1030 - (total_h // 2)

    for idx, line in enumerate(lines):
        y_pos = start_y + (idx * line_h)
        # Outline spesso stile fumetto (stroke da 4px)
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx != 0 or dy != 0:
                    draw.text((360 + dx, y_pos + dy), line, fill=(0, 0, 0, 255), font=font_sub, anchor="mm")
        # Colore testo vivace e chiaro stile cartone animato
        draw.text((360, y_pos), line, fill=(255, 255, 240), font=font_sub, anchor="mm")

    # 3. OUTRO CARD (Solo scena finale)
    if is_outro:
        draw.rounded_rectangle([45, 1090, 675, 1225], radius=18, fill=(10, 15, 25, 235), outline=(235, 190, 80, 240), width=2)
        draw.text((360, 1135), "IMMOBILIARE GIANCANI", fill=(235, 195, 95), font=font_brand, anchor="mm")
        draw.text((360, 1180), "La Guida Sicura per la Tua Prossima Casa", fill=(250, 250, 255), font=font_badge, anchor="mm")

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

# ── MONTAGGIO CLIP KEN BURNS ───────────────────────────────────────────────
def crea_clip_ken_burns(img_path, audio_path, overlay_path, clip_output, idx):
    durata = ottieni_durata_audio(audio_path) + 0.35
    num_frames = int(durata * 25)

    if idx % 2 == 1:
        zoom_filter = f"zoompan=z='min(zoom+0.0009,1.16)':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"
    else:
        zoom_filter = f"zoompan=z='if(lte(zoom,1.0),1.16,max(1.001,zoom-0.0009))':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"

    filter_complex = f"[0:v]{zoom_filter}[bg];[bg][1:v]overlay=0:0[v]"

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

# ── SOCIAL SHARING ──────────────────────────────────────────────────────────
def invia_su_telegram(video_path, storia, target_mode):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    testo_p = storia['testo_colonna_f'].replace('|||', ' ')
    estratto = testo_p[:300] + "..." if len(testo_p) > 300 else testo_p

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
            print(f"✅ Video inviato a Telegram ({chat})")
        except Exception as e:
            print(f"❌ Errore Telegram: {e}")
    return True

def pubblica_reel_facebook(video_path, storia, target_mode):
    if not FB_PAGE_TOKEN or not FB_PAGE_ID: return False
    try:
        url_reels = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/video_reels"
        r1 = requests.post(url_reels, data={"upload_phase": "start", "access_token": FB_PAGE_TOKEN}, timeout=25).json()
        vid, up_url = r1.get("video_id"), r1.get("upload_url")
        if not vid or not up_url: return False

        with open(video_path, "rb") as vf:
            v_bytes = vf.read()
        headers = {"Authorization": f"OAuth {FB_PAGE_TOKEN}", "offset": "0", "file_size": str(len(v_bytes)), "Content-Type": "application/octet-stream"}
        requests.post(up_url, data=v_bytes, headers=headers, timeout=180)

        caption = f"📖 {storia['titolo']} - {target_mode.upper()}\n\nCon la sicurezza di Immobiliare Giancani."
        requests.post(url_reels, data={"upload_phase": "finish", "access_token": FB_PAGE_TOKEN, "video_id": vid, "video_state": "PUBLISHED", "description": caption}, timeout=35)
        print("✅ Reel Facebook pubblicato!")
        return True
    except Exception as e:
        print(f"❌ Errore Facebook Reel: {e}")
        return False

def dividi_e_pubblica_storie_facebook(video_path, clips, storia):
    if not FB_PAGE_TOKEN or not FB_PAGE_ID: return False
    url_stories = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/video_stories"
    for idx, s_clip in enumerate(clips, 1):
        try:
            r1 = requests.post(url_stories, data={"upload_phase": "start", "access_token": FB_PAGE_TOKEN}, timeout=20).json()
            vid, up_url = r1.get("video_id"), r1.get("upload_url")
            if not vid or not up_url: continue

            with open(s_clip, "rb") as cf:
                c_bytes = cf.read()
            headers = {"Authorization": f"OAuth {FB_PAGE_TOKEN}", "offset": "0", "file_size": str(len(c_bytes)), "Content-Type": "application/octet-stream"}
            requests.post(up_url, data=c_bytes, headers=headers, timeout=90)
            requests.post(url_stories, data={"upload_phase": "finish", "access_token": FB_PAGE_TOKEN, "video_id": vid, "video_state": "PUBLISHED"}, timeout=25)
            time.sleep(2)
        except Exception:
            pass
    print("✅ Storie Facebook pubblicate!")
    return True

# ── ORCHESTRATORE PIPELINE ──────────────────────────────────────────────────
async def esegui_pipeline(story_id=None, voice="it-IT-ElsaNeural", mode="standard"):
    storia, target_mode = estrai_storia_colonna_f(id_richiesto=story_id, mode=mode)
    scene = crea_struttura_scene(storia, target_mode)

    clips = []
    durata_totale = 0.0

    print(f"🎬 Inizio generazione {len(scene)} scene per target 2:30 - 3:00 minuti...")

    for idx, s in enumerate(scene, start=1):
        base_name = f"{target_mode}_{storia['id']}_scena_{idx}"
        audio_file = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
        img_file = os.path.join(OUTPUT_DIR, f"{base_name}.jpg")
        overlay_file = os.path.join(OUTPUT_DIR, f"{base_name}_ov.png")
        clip_file = os.path.join(OUTPUT_DIR, f"{base_name}_clip.mp4")

        # 1. Voce
        await genera_voce_edge_tts(s["testo"], audio_file, voce=voice)
        durata_totale += ottieni_durata_audio(audio_file)

        # 2. Immagine con retry
        seed = int(storia["id"]) * 100 + idx if str(storia["id"]).isdigit() else idx * 100
        scarica_immagine_pollinations(s["prompt"], img_file, seed=seed, target_mode=target_mode, is_intro=s["is_intro"])

        # 3. Overlay moderno stile Cartoon
        crea_overlay_grafico(s["testo"], storia["titolo"], overlay_file, is_intro=s["is_intro"], is_outro=s["is_outro"], target_mode=target_mode)

        # 4. Clip video
        crea_clip_ken_burns(img_file, audio_file, overlay_file, clip_file, idx)
        clips.append(clip_file)

    video_finale = os.path.join(OUTPUT_DIR, f"reel_{target_mode}_{storia['id']}.mp4")
    monta_video_finale(clips, video_finale, durata_totale)

    minuti = int(durata_totale // 60)
    secondi = int(durata_totale % 60)
    print("\n" + "="*70)
    print(f"🎉 VIDEO COMPLETATO: {video_finale}")
    print(f"⏱️ Durata Effettiva Ottenuta: {minuti} minuti e {secondi} secondi")
    print("="*70 + "\n")

    # Pubblicazioni Social
    invia_su_telegram(video_finale, storia, target_mode)
    pubblica_reel_facebook(video_finale, storia, target_mode)
    dividi_e_pubblica_storie_facebook(video_finale, clips, storia)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot Reels Multi-Modalità Master")
    parser.add_argument("--mode", type=str, default="standard", 
                        choices=["standard", "bibbia", "pillole", "mitologia"])
    parser.add_argument("--id", type=str, default=None)
    parser.add_argument("--voice", type=str, default="it-IT-ElsaNeural")
    args = parser.parse_args()

    asyncio.run(esegui_pipeline(story_id=args.id, voice=args.voice, mode=args.mode))
