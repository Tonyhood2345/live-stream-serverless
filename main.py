#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  🎬 BOT REELS: GRANDI CLASSICI, BIBBIA E PILLOLE IMMOBILIARI
  Target Durata Estesa: 90s - 150s (1m30s - 2m30s)
  Fullscreen 9:16, Sottotitoli Dinamici, Multi-Social Automation
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

# ── CONFIGURAZIONI GLOBALI ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "video_storie_output")
CSV_PATH = os.path.join(BASE_DIR, "database_storie_classici.csv")
CSV_BIBBIA_PATH = os.path.join(BASE_DIR, "database_storie_bibliche.csv")
CSV_PILLOLE_PATH = os.path.join(BASE_DIR, "database_pillole_immobiliari_legali.csv")
MUSIC_DIR = os.path.join(BASE_DIR, "musica_sottofondo")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Credenziali Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1723292483")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@immobiliaregiancani")

# Credenziali Facebook Page
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

ANTIQUE_STORYBOOK_STYLE = (
    "Antique storybook illustration style, vintage botanical engraving fused with luminous watercolor wash. "
    "Fine ink line art, detailed cross-hatching textures, and clean calligraphic contours. "
    "Hand-painted soft watercolor palette in deep indigo, dusty blue, and warm ochre on aged cream parchment paper texture. "
    "Celestial starburst motifs, delicate gold leaf foil accents, engraved nautical and astronomical chart elements. "
    "Whimsical classic fairytale aesthetic, rich detailed linework, warm atmospheric lighting, masterclass literary print quality. "
    "--no 3d render, CGI, glossy, photorealistic"
)

# ── ESTRAZIONE DATI DA COLONNA F ────────────────────────────────────────────
def estrai_storia_colonna_f(csv_file=None, id_richiesto=None, mode="standard"):
    if not csv_file:
        if mode == "bibbia":
            csv_file = CSV_BIBBIA_PATH
        elif mode == "pillole":
            csv_file = CSV_PILLOLE_PATH
        else:
            csv_file = CSV_PATH

    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Database storie non trovato: {csv_file}")
        
    storie = []
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or len(row) < 4:
                continue
            if mode == "bibbia":
                storie.append({
                    "id": row[0].strip(),
                    "titolo": row[1].strip(),
                    "autore": row[2].strip(),
                    "anno": "Antico Testamento",
                    "genere": "Bibbia",
                    "categoria": "BIBBIA",
                    "testo_colonna_f": row[3].strip(),
                    "prompts_g": row[4].strip() if len(row) > 4 else "",
                    "stato": row[5].strip() if len(row) > 5 else "pronto"
                })
            elif mode == "pillole":
                col_f = row[5].strip() if len(row) > 5 else row[3].strip()
                storie.append({
                    "id": row[0].strip(),
                    "titolo": row[2].strip() if len(row) > 2 else row[1].strip(),
                    "autore": row[3].strip() if len(row) > 3 else "Immobiliare Giancani",
                    "anno": "Normativa Vigente",
                    "genere": "Pillola Immobiliare",
                    "categoria": "PILLOLE",
                    "testo_colonna_f": col_f,
                    "prompts_g": "",
                    "stato": row[-1].strip()
                })
            else:
                if len(row) >= 6:
                    storie.append({
                        "id": row[0].strip(),
                        "titolo": row[1].strip(),
                        "autore": row[2].strip(),
                        "anno": row[3].strip() if len(row) > 3 else "",
                        "genere": row[4].strip() if len(row) > 4 else "",
                        "categoria": "STANDARD",
                        "testo_colonna_f": row[5].strip(),
                        "prompts_g": row[6].strip() if len(row) > 6 else ""
                    })

    if not storie:
        raise ValueError(f"Nessuna storia valida trovata nel database: {csv_file}")

    if id_richiesto:
        trovate = [s for s in storie if str(s["id"]) == str(id_richiesto)]
        storia = trovate[0] if trovate else random.choice(storie)
    else:
        storia = random.choice(storie)

    print("\n" + "="*70)
    print("📖 [ESTRAZIONE DATI] RIGOROSAMENTE DA COLONNA F")
    print(f"📌 [MODALITÀ {storia.get('categoria', mode).upper()} - ID {storia['id']}]: «{storia['titolo']}»")
    print("="*70 + "\n")
    return storia

# ── STRUTTURAZIONE SCENE (TARGET: 90s - 150s) ──────────────────────────────
def crea_struttura_scene(storia, mode="standard"):
    categoria = storia.get("categoria", mode).upper()
    testo_f = storia["testo_colonna_f"]

    # Parsing blocchi di testo
    if "|||" in testo_f:
        frasi_raw = [f.strip() for f in testo_f.split("|||") if f.strip()]
    else:
        frasi_raw = [f.strip() for f in re.split(r'(?<=[.!?])\s+', testo_f) if f.strip()]

    # Riorganizzazione per ottenere 7-10 scene narrative stabili
    frasi = []
    chunk = ""
    for f in frasi_raw:
        if len(chunk) + len(f) < 135:
            chunk = (chunk + " " + f).strip()
        else:
            if chunk:
                frasi.append(chunk)
            chunk = f
    if chunk:
        frasi.append(chunk)

    if not frasi:
        frasi = [testo_f]

    # Hook iniziale moderno
    if categoria == "STANDARD":
        if not any(hk in frasi[0].lower() for hk in ["ecco a voi", "due minuti", "in 2 minuti"]):
            frasi[0] = f"I grandi classici in due minuti: {storia['titolo']} di {storia['autore']}. {frasi[0]}"

    # Chiusura con branding esplicito
    if "Immobiliare Giancani" not in frasi[-1]:
        frasi[-1] = frasi[-1].rstrip(".") + ". Grandi traguardi si raggiungono con strategia e dedizione. La tua casa con Immobiliare Giancani."

    prompts_raw = [p.strip() for p in storia["prompts_g"].split("|||") if p.strip()] if storia.get("prompts_g") else []

    scene = []
    num_scene = len(frasi)
    for i in range(num_scene):
        prompt_custom = prompts_raw[i] if i < len(prompts_raw) else ""
        if prompt_custom:
            p_clean = prompt_custom.replace("pixar 3d style,", "").replace("vertical 9:16", "").strip(" ,.")
            if categoria == "STANDARD":
                if i == 0:
                    full_p = "Antique storybook watercolor, cute smiling orange tabby kitten in blue striped sailor shirt, on open book looking at celestial star --no human, 3d"
                else:
                    full_p = f"Antique storybook watercolor: {storia['titolo']} - {p_clean[:70]} --no girl, 3d, photo"
            else:
                full_p = f"Antique storybook illustration: {storia['titolo']} - {p_clean[:70]} --no cat, kitten, 3d, photo"
        else:
            if categoria == "STANDARD":
                full_p = f"Antique storybook watercolor illustration, scene from {storia['titolo']}: {frasi[i][:65]} --no 3d, photo"
            else:
                full_p = f"Antique storybook illustration, vintage engraving: {storia['titolo']} - {frasi[i][:65]} --no cat, animal, 3d, photo"

        scene.append({
            "scena_id": i + 1,
            "testo": frasi[i],
            "prompt": full_p,
            "is_intro": (i == 0),
            "is_outro": (i == num_scene - 1)
        })

    return scene

# ── GENERAZIONE VOCE NEURALE NARRATIVA (EDGE-TTS) ───────────────────────────
async def genera_voce_edge_tts(testo, file_audio, voce="it-IT-ElsaNeural"):
    success = False
    try:
        import edge_tts
        # Cadenza rilassata (-4%) per lettura epica e distesa
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

# ── DOWNLOAD IMMAGINE 9:16 (POLLINATIONS) ───────────────────────────────────
def scarica_immagine_pollinations(prompt, output_img, seed=100, categoria="STANDARD", is_intro=False):
    if os.path.exists(output_img) and os.path.getsize(output_img) > 10000:
        return True

    cat_upper = str(categoria).upper()
    assets_dir = os.path.join(BASE_DIR, "assets")

    if "STANDARD" in cat_upper and is_intro:
        cat_ref = os.path.join(assets_dir, "cat_master_reference.jpg")
        if os.path.exists(cat_ref):
            try:
                with Image.open(cat_ref) as cimg:
                    cimg.convert("RGB").resize((720, 1280), Image.Resampling.LANCZOS).save(output_img, "JPEG", quality=95)
                return True
            except Exception:
                pass

    clean_p = prompt.replace("2D cartoon animation style,", "").strip(" ,.")[:200]
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

    # Fallback su colore armonico scuro
    img = Image.new("RGB", (720, 1280), color=(18, 24, 38))
    img.save(output_img, "JPEG", quality=95)
    return True

# ── OVERLAY GRAFICO MODERNO A TUTTO SCHERMO ─────────────────────────────────
def crea_overlay_grafico(testo, titolo_libro, autore, output_overlay, is_intro=False, is_outro=False, categoria="STANDARD"):
    img = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    fonts_dir = os.path.join(BASE_DIR, "assets", "fonts")
    def load_font(filename, fallbacks, size):
        p = os.path.join(fonts_dir, filename)
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
        for fb in fallbacks:
            try: return ImageFont.truetype(fb, size)
            except: pass
        return ImageFont.load_default()

    font_intro = load_font("Cinzel-Bold.ttf", ["georgiab.ttf", "arialbd.ttf"], 22)
    font_sub = load_font("Lora-Bold.ttf", ["arialbd.ttf", "helvetica.ttf"], 27)
    font_brand = load_font("Cinzel-Bold.ttf", ["georgiab.ttf", "arialbd.ttf"], 28)
    font_claim = load_font("PlayfairDisplay-Bold.ttf", ["georgia.ttf", "arial.ttf"], 20)

    # Pill Intro nei primi secondi
    if is_intro:
        draw.rounded_rectangle([60, 60, 660, 125], radius=20, fill=(15, 20, 32, 200), outline=(212, 175, 55, 220), width=2)
        draw.text((360, 92), f"{titolo_libro.upper()} — {autore}", fill=(245, 220, 150), font=font_intro, anchor="mm")

    # Sottotitoli dinamici (Pill compatto semi-trasparente)
    import textwrap
    lines = textwrap.wrap(testo, width=38)
    line_h = 35
    padding = 20
    box_w = 650
    box_h = len(lines) * line_h + padding * 2
    box_y = 1010 - (box_h // 2)
    box_x = 35

    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=16, fill=(12, 16, 26, 190), outline=(212, 175, 55, 160), width=1)

    start_y = box_y + padding + (line_h // 2)
    for idx, line in enumerate(lines):
        y_pos = start_y + (idx * line_h)
        draw.text((361, y_pos + 1), line, fill=(0, 0, 0, 240), font=font_sub, anchor="mm")
        draw.text((360, y_pos), line, fill=(255, 252, 245), font=font_sub, anchor="mm")

    # Outro Card
    if is_outro:
        draw.rounded_rectangle([40, 1100, 680, 1235], radius=18, fill=(14, 18, 30, 235), outline=(234, 198, 108, 240), width=2)
        draw.text((360, 1140), "IMMOBILIARE GIANCANI", fill=(234, 198, 108), font=font_brand, anchor="mm")
        draw.text((360, 1185), "Il Valore di Sentirsi a Casa", fill=(255, 255, 255), font=font_claim, anchor="mm")

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

# ── CLIP CON KEN BURNS ─────────────────────────────────────────────────────
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

# ── MUSICA E MIXAGGIO ──────────────────────────────────────────────────────
def ottieni_o_genera_musica(durata_totale):
    tracce = []
    if os.path.exists(MUSIC_DIR):
        for f in os.listdir(MUSIC_DIR):
            if f.lower().endswith(".mp3"):
                tracce.append(os.path.join(MUSIC_DIR, f))
    if tracce:
        return random.choice(tracce)

    fallback_music = os.path.join(OUTPUT_DIR, "ambient_fallback.mp3")
    if not os.path.exists(fallback_music):
        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "lavfi", "-i", f"sine=frequency=220:duration={durata_totale+10}",
            "-af", "volume=0.07,lowpass=f=400,afade=t=in:ss=0:d=2,afade=t=out:st=15:d=3",
            "-c:a", "libmp3lame", "-b:a", "128k", fallback_music
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return fallback_music

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

    musica_file = ottieni_o_genera_musica(durata_totale)
    filter_mix = (
        f"[1:a]volume=0.10,afade=t=in:ss=0:d=1.5,afade=t=out:st={max(2, durata_totale - 2.5)}:d=2.5[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    cmd_mix = [
        FFMPEG_EXE, "-y",
        "-i", video_temp,
        "-stream_loop", "-1", "-i", musica_file,
        "-filter_complex", filter_mix,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", output_video
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    if os.path.exists(video_temp):
        os.remove(video_temp)

# ── INVIO SOCIAL AUTOMATICO (TELEGRAM & META) ────────────────────────────────
def invia_su_telegram(video_path, storia):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Token Telegram non configurati. Salto invio.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    testo_p = storia['testo_colonna_f'].replace('|||', ' ')
    estratto = testo_p[:300] + "..." if len(testo_p) > 300 else testo_p

    caption = (
        f"📖 <b>{storia['titolo']}</b>\n"
        f"✍️ <i>{storia.get('autore', '')}</i>\n\n"
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

def pubblica_reel_facebook(video_path, storia):
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        print("⚠️ Credenziali Facebook mancanti. Salto Reel.")
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

        caption = f"📖 {storia['titolo']} - {storia.get('autore', '')}\n\nCon l'affidabilità di Immobiliare Giancani."
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

# ── ORCHESTRATORE ───────────────────────────────────────────────────────────
async def esegui_pipeline(story_id=None, voice="it-IT-ElsaNeural", mode="standard", output_json_only=False):
    start_time = time.time()
    storia = estrai_storia_colonna_f(id_richiesto=story_id, mode=mode)
    scene = crea_struttura_scene(storia, mode=mode)

    clips = []
    durata_totale = 0.0

    for idx, s in enumerate(scene, start=1):
        base_name = f"{mode}_{storia['id']}_scena_{idx}"
        audio_file = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
        img_file = os.path.join(OUTPUT_DIR, f"{base_name}.jpg")
        overlay_file = os.path.join(OUTPUT_DIR, f"{base_name}_ov.png")
        clip_file = os.path.join(OUTPUT_DIR, f"{base_name}_clip.mp4")

        await genera_voce_edge_tts(s["testo"], audio_file, voce=voice)
        durata_totale += ottieni_durata_audio(audio_file)

        seed = int(storia["id"]) * 100 + idx if str(storia["id"]).isdigit() else idx * 100
        scarica_immagine_pollinations(s["prompt"], img_file, seed=seed, categoria=storia.get("categoria", mode), is_intro=s["is_intro"])
        crea_overlay_grafico(s["testo"], storia["titolo"], storia["autore"], overlay_file, is_intro=s["is_intro"], is_outro=s["is_outro"], categoria=storia.get("categoria", mode))
        crea_clip_ken_burns(img_file, audio_file, overlay_file, clip_file, idx)
        clips.append(clip_file)

    video_finale = os.path.join(OUTPUT_DIR, f"reel_{mode}_{storia['id']}.mp4")
    monta_video_finale(clips, video_finale, durata_totale)

    minuti = int(durata_totale // 60)
    secondi = int(durata_totale % 60)
    print(f"\n🎉 Durata finale video: {minuti}m {secondi}s")

    # Pubblicazioni
    invia_su_telegram(video_finale, storia)
    pubblica_reel_facebook(video_finale, storia)
    dividi_e_pubblica_storie_facebook(video_finale, clips, storia)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default=None, choices=["standard", "bibbia", "pillole"])
    parser.add_argument("--id", type=str, default=None)
    parser.add_argument("--voice", type=str, default="it-IT-ElsaNeural")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    mode_effettivo = args.mode
    if not mode_effettivo:
        import datetime
        ora_utc = datetime.datetime.now(datetime.timezone.utc).hour
        mode_effettivo = "pillole" if 2 <= ora_utc <= 8 else "bibbia"

    asyncio.run(esegui_pipeline(story_id=args.id, voice=args.voice, mode=mode_effettivo, output_json_only=args.json))
