#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  🎬 BOT REELS MULTI-MODALITÀ COMPLETO
  Modalità supportate:
    1. --mode mitologia  -> Miti greci/epica classica (ZERO GATTO, Stile Epic Comic)
    2. --mode bibbia     -> Storie bibliche (ZERO GATTO, Stile Incisione Sacra)
    3. --mode standard   -> Grandi libri classici (GATTO SIMPATICO NARRATORE)
    4. --mode pillole    -> Pillole immobiliari e legali (ZERO GATTO, Stile Notarile/Ufficio)
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

# ── STILI VISIVI SPECIFICI PER MODALITÀ ──────────────────────────────────────
STYLE_PROMPTS = {
    "mitologia": (
        "Classic graphic novel art style, dynamic Greek mythology epic illustration, "
        "dramatic lighting, ancient temple ruins, bold ink contours, cel shading, rich cinematic colors. "
        "--no cat, feline, kitten, animal pet, 3d render, photo, bad anatomy"
    ),
    "bibbia": (
        "Antique sacred storybook illustration, luminous watercolor wash, fine vintage botanical engraving on parchment texture, "
        "solemn spiritual atmosphere, warm ochre and dusty blue tones. "
        "--no cat, kitten, animal, pet, 3d render, CGI, glossy"
    ),
    "standard": (
        "Antique storybook watercolor illustration, whimsical classic fairytale aesthetic, "
        "fine ink line art, detailed textures, soft lighting on aged cream parchment paper. "
        "--no 3d render, CGI, photorealistic"
    ),
    "pillole": (
        "Professional modern real estate and legal concept illustration, prestigious notary office desk, "
        "architectural house blueprints, signed legal contract, warm ambient indoor office lighting, elegant clean lines. "
        "--no cat, kitten, feline, dog, pet, animal, cartoon cat, 3d render, CGI"
    )
}

# ── ESTRAZIONE DATI CSV CON SELEZIONE MODALITÀ RIGOROSA ──────────────────────
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
                # Classici o Mitologia (estratti dallo stesso CSV)
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
        raise ValueError(f"Nessuna storia trovata nel database: {csv_file}")

    # Filtraggio preciso
    if target_mode == "mitologia":
        candidati = [s for s in storie if s.get("categoria") == "mitologia"]
        if not candidati:
            candidati = storie  # fallback se nessun record è taggato esplicitamente
    elif target_mode == "standard":
        candidati = [s for s in storie if s.get("categoria") == "standard"]
        if not candidati:
            candidati = storie
    else:
        candidati = storie

    if id_richiesto:
        trovate = [s for s in candidati if str(s["id"]).lower() == str(id_richiesto).lower()]
        storia = trovate[0] if trovate else random.choice(candidati)
    else:
        storia = random.choice(candidati)

    print("\n" + "="*70)
    print(f"📖 [SELEZIONE EPISODIO] ID: {storia['id']} | Modalità: {target_mode.upper()}")
    print(f"📌 Titolo: «{storia['titolo']}» ({storia.get('autore', '')})")
    print("="*70 + "\n")
    return storia, target_mode

# ── PARSING DELLE SCENE (ESTESA: 90s - 150s) ────────────────────────────────
def crea_struttura_scene(storia, target_mode):
    testo_f = storia["testo_colonna_f"]

    if "|||" in testo_f:
        frasi_raw = [f.strip() for f in testo_f.split("|||") if f.strip()]
    else:
        frasi_raw = [f.strip() for f in re.split(r'(?<=[.!?])\s+', testo_f) if f.strip()]

    frasi = []
    chunk = ""
    for f in frasi_raw:
        if len(chunk) + len(f) < 130:
            chunk = (chunk + " " + f).strip()
        else:
            if chunk:
                frasi.append(chunk)
            chunk = f
    if chunk:
        frasi.append(chunk)

    if not frasi:
        frasi = [testo_f]

    # Hook e Brand Closing personalizzati
    if target_mode == "mitologia":
        if not any(k in frasi[0].lower() for k in ["mito", "leggenda", "due minuti", "in 2 minuti"]):
            frasi[0] = f"I grandi miti in due minuti: {storia['titolo']}. {frasi[0]}"
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + ". Grandi sfide e decisioni storiche richiedono visione e solidità. Affidati alla guida sicura di Immobiliare Giancani."
            
    elif target_mode == "pillole":
        if not any(k in frasi[0].lower() for k in ["pillola", "notaio", "immobiliare", "guida"]):
            frasi[0] = f"Pillola immobiliare e legale: {storia['titolo']}. {frasi[0]}"
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + ". Per una compravendita sicura, trasparente e tutelata, scegli la competenza di Immobiliare Giancani."
            
    elif target_mode == "bibbia":
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + " — Con la cura e l'affidabilità di Immobiliare Giancani."
            
    else:  # standard libri classici
        if not any(k in frasi[0].lower() for k in ["classici", "due minuti", "gatto"]):
            frasi[0] = f"I grandi classici in due minuti con il nostro gatto curioso: {storia['titolo']} di {storia['autore']}! {frasi[0]}"
        if "Immobiliare Giancani" not in frasi[-1]:
            frasi[-1] = frasi[-1].rstrip(".") + ". Con la passione per le grandi storie di Immobiliare Giancani."

    prompts_raw = [p.strip() for p in storia.get("prompts_g", "").split("|||") if p.strip()]

    scene = []
    num_scene = len(frasi)
    base_style = STYLE_PROMPTS[target_mode]

    for i in range(num_scene):
        p_custom = prompts_raw[i] if i < len(prompts_raw) else ""
        clean_custom = p_custom.replace("pixar 3d style,", "").replace("vertical 9:16", "").strip(" ,.") if p_custom else frasi[i][:65]

        if target_mode == "standard":
            if i == 0:
                full_p = "Cute smiling orange tabby kitten wearing sailor striped t-shirt on antique open book, watercolor wash --no human, 3d"
            else:
                full_p = f"{base_style}, scene from {storia['titolo']}: {clean_custom} --no 3d, photo"
        elif target_mode == "pillole":
            full_p = f"{base_style}, practical legal guide on {storia['titolo']}: {clean_custom}"
        elif target_mode == "mitologia":
            full_p = f"{base_style}, heroic Greek myth {storia['titolo']}: {clean_custom}"
        else:  # bibbia
            full_p = f"{base_style}, sacred scene {storia['titolo']}: {clean_custom}"

        scene.append({
            "scena_id": i + 1,
            "testo": frasi[i],
            "prompt": full_p,
            "is_intro": (i == 0),
            "is_outro": (i == num_scene - 1)
        })

    return scene

# ── GENERAZIONE AUDIO CON EDGE-TTS ──────────────────────────────────────────
async def genera_voce_edge_tts(testo, file_audio, voce="it-IT-ElsaNeural"):
    success = False
    try:
        import edge_tts
        # Cadenza rilassata (-4%) per durata 90s-150s
        comm = edge_tts.Communicate(testo, voce, rate="-4%", pitch="+0Hz")
        await asyncio.wait_for(comm.save(file_audio), timeout=25)
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

# ── DOWNLOAD IMMAGINE SENZA INQUINAMENTI (POLLINATIONS) ──────────────────────
def scarica_immagine_pollinations(prompt, output_img, seed=100, target_mode="standard", is_intro=False):
    if os.path.exists(output_img) and os.path.getsize(output_img) > 10000:
        return True

    assets_dir = os.path.join(BASE_DIR, "assets")

    # Il gatto di riferimento entra SOLO nella prima scena dei Grandi Classici (STANDARD)
    if target_mode == "standard" and is_intro:
        cat_ref = os.path.join(assets_dir, "cat_master_reference.jpg")
        if os.path.exists(cat_ref):
            try:
                with Image.open(cat_ref) as cimg:
                    cimg.convert("RGB").resize((720, 1280), Image.Resampling.LANCZOS).save(output_img, "JPEG", quality=95)
                return True
            except Exception:
                pass

    clean_p = prompt.replace("2D cartoon animation style,", "").strip(" ,.")[:220]
    encoded = urllib.parse.quote(clean_p)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&nologo=true&seed={seed}&model=turbo"

    for attempt in range(2):
        try:
            resp = requests.get(url, timeout=(5, 12), verify=False, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(output_img, "wb") as f:
                    f.write(resp.content)
                return True
        except Exception:
            time.sleep(1.5)

    # Fallback con tinte scure a tutto schermo
    tinte = {
        "pillole": (20, 26, 38),
        "mitologia": (32, 22, 16),
        "bibbia": (30, 24, 18),
        "standard": (18, 24, 34)
    }
    img = Image.new("RGB", (720, 1280), color=tinte.get(target_mode, (20, 20, 20)))
    img.save(output_img, "JPEG", quality=95)
    return True

# ── OVERLAY GRAFICO: FONT GRANDI SCALABILI, ZERO RIQUADRI CIECHI ─────────────
def crea_overlay_grafico(testo, titolo_libro, output_overlay, is_intro=False, is_outro=False, target_mode="standard"):
    img = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def load_safe_font(size_target):
        system_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "arialbd.ttf"
        ]
        for f in system_fonts:
            if os.path.exists(f):
                try: return ImageFont.truetype(f, size_target)
                except: pass
        return ImageFont.load_default()

    font_sub = load_safe_font(34)
    font_badge = load_safe_font(22)
    font_brand = load_safe_font(30)

    # 1. Nessun banner fisso gigante. Solo pill compatto trasparente nei primi secondi
    if is_intro:
        tag_nomi = {
            "mitologia": "MITOLOGIA CLASSICA IN 2 MINUTI",
            "bibbia": "STORIE DELLA BIBBIA IN 2 MINUTI",
            "pillole": "PILLOLA IMMOBILIARE & TUTELA LEGALE",
            "standard": "I GRANDI CLASSICI IN 2 MINUTI"
        }
        draw.rounded_rectangle([60, 60, 660, 125], radius=16, fill=(12, 16, 26, 195), outline=(225, 185, 80, 220), width=2)
        draw.text((360, 92), tag_nomi.get(target_mode, titolo_libro.upper()), fill=(255, 245, 220), font=font_badge, anchor="mm")

    # 2. Sottotitoli Moderni: Font grandi, NESSUN riquadro cieco, contorno nero 3px
    import textwrap
    lines = textwrap.wrap(testo, width=28)
    line_h = 44
    total_h = len(lines) * line_h
    start_y = 1040 - (total_h // 2)

    for idx, line in enumerate(lines):
        y_pos = start_y + (idx * line_h)
        # Bordo spesso nero per renderlo leggibile su qualsiasi sfondo
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx != 0 or dy != 0:
                    draw.text((360 + dx, y_pos + dy), line, fill=(0, 0, 0, 255), font=font_sub, anchor="mm")
        # Testo principale brillante
        draw.text((360, y_pos), line, fill=(255, 252, 240), font=font_sub, anchor="mm")

    # 3. Outro Card elegante
    if is_outro:
        draw.rounded_rectangle([50, 1100, 670, 1225], radius=16, fill=(12, 16, 26, 235), outline=(230, 190, 80, 230), width=2)
        draw.text((360, 1140), "IMMOBILIARE GIANCANI", fill=(235, 195, 95), font=font_brand, anchor="mm")
        draw.text((360, 1185), "Il Valore della Sicurezza per la Tua Casa", fill=(245, 245, 250), font=font_badge, anchor="mm")

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
            return max(3.5, float(h)*3600 + float(m)*60 + float(s))
    return 6.0

# ── MONTAGGIO CLIP CON KEN BURNS ───────────────────────────────────────────
def crea_clip_ken_burns(img_path, audio_path, overlay_path, clip_output, idx):
    durata = ottieni_durata_audio(audio_path) + 0.35
    num_frames = int(durata * 25)

    if idx % 2 == 1:
        zoom_filter = f"zoompan=z='min(zoom+0.0010,1.18)':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"
    else:
        zoom_filter = f"zoompan=z='if(lte(zoom,1.0),1.18,max(1.001,zoom-0.0010))':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"

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

# ── MONTAGGIO VIDEO FINALE CON AUDIO DUCKING ────────────────────────────────
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

# ── SOCIAL SHARING AUTOMATICO ───────────────────────────────────────────────
def invia_su_telegram(video_path, storia, target_mode):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
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
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        return False
    try:
        url_reels = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/video_reels"
        r1 = requests.post(url_reels, data={"upload_phase": "start", "access_token": FB_PAGE_TOKEN}, timeout=25).json()
        vid, up_url = r1.get("video_id"), r1.get("upload_url")
        if not vid or not up_url: return False

        with open(video_path, "rb") as vf:
            v_bytes = vf.read()
        headers = {"Authorization": f"OAuth {FB_PAGE_TOKEN}", "offset": "0", "file_size": str(len(v_bytes)), "Content-Type": "application/octet-stream"}
        requests.post(up_url, data=v_bytes, headers=headers, timeout=180)

        caption = f"📖 {storia['titolo']} - {target_mode.upper()}\n\nCon la tutela e l'esperienza di Immobiliare Giancani."
        requests.post(url_reels, data={"upload_phase": "finish", "access_token": FB_PAGE_TOKEN, "video_id": vid, "video_state": "PUBLISHED", "description": caption}, timeout=35)
        print("✅ Reel Facebook pubblicato!")
        return True
    except Exception as e:
        print(f"❌ Errore Facebook Reel: {e}")
        return False

def dividi_e_pubblica_storie_facebook(video_path, clips, storia):
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        return False
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
    print("✅ Storie Facebook sequenziali pubblicate!")
    return True

# ── ORCHESTRATORE PIPELINE ──────────────────────────────────────────────────
async def esegui_pipeline(story_id=None, voice="it-IT-ElsaNeural", mode="standard"):
    storia, target_mode = estrai_storia_colonna_f(id_richiesto=story_id, mode=mode)
    scene = crea_struttura_scene(storia, target_mode)

    clips = []
    durata_totale = 0.0

    for idx, s in enumerate(scene, start=1):
        base_name = f"{target_mode}_{storia['id']}_scena_{idx}"
        audio_file = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
        img_file = os.path.join(OUTPUT_DIR, f"{base_name}.jpg")
        overlay_file = os.path.join(OUTPUT_DIR, f"{base_name}_ov.png")
        clip_file = os.path.join(OUTPUT_DIR, f"{base_name}_clip.mp4")

        # Voce narrante
        await genera_voce_edge_tts(s["testo"], audio_file, voce=voice)
        durata_totale += ottieni_durata_audio(audio_file)

        # Immagine coerente
        seed = int(storia["id"]) * 100 + idx if str(storia["id"]).isdigit() else idx * 100
        scarica_immagine_pollinations(s["prompt"], img_file, seed=seed, target_mode=target_mode, is_intro=s["is_intro"])

        # Overlay moderno
        crea_overlay_grafico(s["testo"], storia["titolo"], overlay_file, is_intro=s["is_intro"], is_outro=s["is_outro"], target_mode=target_mode)

        # Clip Ken Burns
        crea_clip_ken_burns(img_file, audio_file, overlay_file, clip_file, idx)
        clips.append(clip_file)

    video_finale = os.path.join(OUTPUT_DIR, f"reel_{target_mode}_{storia['id']}.mp4")
    monta_video_finale(clips, video_finale, durata_totale)

    minuti = int(durata_totale // 60)
    secondi = int(durata_totale % 60)
    print(f"\n🎉 Durata finale video: {minuti}m {secondi}s")

    # Invio Social
    invia_su_telegram(video_finale, storia, target_mode)
    pubblica_reel_facebook(video_finale, storia, target_mode)
    dividi_e_pubblica_storie_facebook(video_finale, clips, storia)

# ── ENTRY POINT CLI ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot Reels Multi-Modalità Master")
    parser.add_argument("--mode", type=str, default="standard", 
                        choices=["standard", "bibbia", "pillole", "mitologia"],
                        help="Modalità: standard (libri classici con gatto), mitologia (miti greci), bibbia (storie sacre), pillole (notarile/legale)")
    parser.add_argument("--id", type=str, default=None, help="ID della riga CSV")
    parser.add_argument("--voice", type=str, default="it-IT-ElsaNeural", help="Voce Edge-TTS")
    args = parser.parse_args()

    asyncio.run(esegui_pipeline(story_id=args.id, voice=args.voice, mode=args.mode))
