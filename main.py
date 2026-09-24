#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  🐱 AUTOMATED BOT: REELS VERTICALI - IL GATTO NARRATORE DI GRANDI CLASSICI
  Senior Automation Engineering & Storytelling Pipeline
   
  SPECIFICHE:
  - Formato: Video Verticale 9:16 (720x1280)
  - Protagonista: Gatto arancione tigrato UMANIZZATO (antropomorfo, postura eretta,
    zampe usate come mani espressive, maglietta vintage a righe blu e bianche)
  - Stile Visivo: Antique Storybook Illustration (Incisione botanica/astronomica,
    acquerello luminoso indigo/ocra, accenti foglia d'oro, carta pergamena)
  - Estrazione: Rigorosamente da Colonna F (database_storie_classici.csv)
  - Voce Narrante: Edge-TTS Neurale Italiano (it-IT-DiegoNeural / it-IT-ElsaNeural)
  - Immagini AI: Pollinations.ai con Seed coerente e fallback grafico resiliente
  - Montaggio: FFmpeg (Ken Burns dinamico, sottotitoli Pillow, musica mixata)
  - Notifica: Invio automatico su Telegram Bot API
  - Branding: Mette costantemente in risalto 'Immobiliare Giancani'
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

# Patch aiohttp per runner CI e ambienti Windows
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
MUSIC_DIR = os.path.join(BASE_DIR, "musica_sottofondo")

os.makedirs(OUTPUT_DIR, exist_ok=True)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1723292483")

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

# ── PERSONAGGIO UMANIZZATO E STILE GRAFICO FUSI ────────────────────────────
CAT_HUMANIZED_CHARACTER = (
    "A charming fully anthropomorphic orange tabby cat character behaving like a gentle human storyteller, "
    "standing tall and upright on two hind legs with perfect human posture, expressive front paws gesturing like human hands, "
    "wearing a classic vintage navy blue and white horizontal striped sailor shirt, warm intelligent eyes, friendly gentle smile"
)

ART_STYLE_PROMPT = (
    "Antique storybook illustration style, vintage botanical engraving fused with luminous watercolor wash. "
    "Fine ink line art, detailed cross-hatching textures, and clean calligraphic contours. "
    "Hand-painted soft watercolor palette in deep indigo, dusty blue, and warm ochre on aged cream parchment paper texture. "
    "Celestial starburst motifs, delicate gold leaf foil accents, engraved nautical and astronomical chart elements. "
    "Whimsical classic fairytale aesthetic, rich detailed linework, warm atmospheric lighting, masterclass literary print quality. "
    "--no 3d render, CGI, glossy, photorealistic, plastic, octane render, unreal engine"
)


# ── ESTRAZIONE RIGOROSA DA COLONNA F ────────────────────────────────────────
def estrai_storia_colonna_f(csv_file=CSV_PATH, id_richiesto=None):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Database storie non trovato: {csv_file}")
        
    storie = []
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 6:
                storie.append({
                    "id": row[0].strip(),
                    "titolo": row[1].strip(),
                    "autore": row[2].strip(),
                    "anno": row[3].strip() if len(row) > 3 else "",
                    "genere": row[4].strip() if len(row) > 4 else "",
                    "testo_colonna_f": row[5].strip(),
                    "prompts_g": row[6].strip() if len(row) > 6 else ""
                })

    if not storie:
        raise ValueError("Nessuna storia valida trovata nel database CSV!")

    if id_richiesto:
        trovate = [s for s in storie if str(s["id"]) == str(id_richiesto)]
        storia = trovate[0] if trovate else random.choice(storie)
    else:
        storia = random.choice(storie)

    print("\n" + "="*70)
    print("📖 [ESTRAZIONE DATI] RIGOROSAMENTE DA COLONNA F")
    print(f"📌 [LIBRO ID {storia['id']}]: «{storia['titolo']}» di {storia['autore']}")
    print(f"💬 [TESTO COLONNA F]:\n\"{storia['testo_colonna_f']}\"")
    print("="*70 + "\n")
    
    return storia


# ── STRUTTURAZIONE DELLE 4 SCENE NARRATIVE ──────────────────────────────────
def crea_struttura_scene(storia):
    testo_f = storia["testo_colonna_f"]
    prompts_raw = storia["prompts_g"].split("|||") if storia["prompts_g"] else []
    
    frasi = [f.strip() for f in re.split(r'(?<=[.!?])\s+', testo_f) if f.strip()]
    
    while len(frasi) < 4:
        if len(frasi) == 3:
            frasi.insert(2, "Un viaggio ricco di emozioni e di scoperte indimenticabili.")
        elif len(frasi) == 2:
            frasi.insert(1, "Ogni pagina svela un mondo fantastico da esplorare.")
            frasi.insert(2, "Un'avventura che tocca il cuore di grandi e piccini.")
        else:
            frasi = [
                frasi[0],
                "Un'avventura straordinaria che ci trasporta lontano.",
                "Il coraggio e la fantasia illuminano ogni passo.",
                "Con la passione e la cura di Immobiliare Giancani."
            ]

    if "Immobiliare Giancani" not in frasi[-1]:
        frasi[-1] = frasi[-1] + " Con la passione e la visione di Immobiliare Giancani."

    scene = []
    for i in range(4):
        prompt_custom = prompts_raw[i].strip() if i < len(prompts_raw) else ""
        if prompt_custom:
            scene_desc = prompt_custom
        else:
            scene_desc = f"immersed in the timeless literary world of {storia['titolo']}, scene {i+1}"
            
        scene.append({
            "scena_id": i + 1,
            "testo": frasi[i],
            "scene_desc": scene_desc,
            "is_outro": (i == 3)
        })

    return scene


# ── GENERAZIONE VOCE NARRANTE (EDGE-TTS + GTTS FALLBACK) ────────────────────
async def genera_voce_edge_tts(testo, file_audio, voce="it-IT-DiegoNeural"):
    success = False
    try:
        import edge_tts
        comm = edge_tts.Communicate(testo, voce, rate="+2%", pitch="+0Hz")
        await asyncio.wait_for(comm.save(file_audio), timeout=14)
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
            print(f"  ❌ Errore anche nel fallback gTTS: {err}")
            
    return success


# ── DOWNLOAD IMMAGINI AI CON STILE INK & WATERCOLOR (POLLINATIONS) ───────────
def scarica_immagine_pollinations(scene_desc, output_img, seed=100, use_cache=True):
    if use_cache and os.path.exists(output_img) and os.path.getsize(output_img) > 10000:
        try:
            with Image.open(output_img) as test_img:
                test_img.verify()
            print(f"  ⚡ Immagine in cache verificata: {os.path.basename(output_img)}")
            return True
        except Exception:
            if os.path.exists(output_img):
                os.remove(output_img)

    # Bonifica rigorosa da qualsiasi residuo 3D / CGI ereditato dal CSV
    parole_da_rimuovere = [
        "pixar 3d style", "3d pixar", "disney pixar", "pixar style", "pixar",
        "3d render", "render 3d", "chibi 3d", "cgi", "octane render", "unreal engine"
    ]
    clean_desc = scene_desc
    for w in parole_da_rimuovere:
        clean_desc = re.sub(re.escape(w), "", clean_desc, flags=re.IGNORECASE)
    clean_desc = re.sub(r'\s+', ' ', clean_desc).strip(" ,.")

    # Composizione rigorosa: Personaggio Umanizzato + Dettaglio Scena + Stile Grafico Scelto
    full_prompt = f"{CAT_HUMANIZED_CHARACTER}, {clean_desc}. {ART_STYLE_PROMPT}"
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    models_to_try = ["flux", "turbo", "flux"]
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        model_choice = models_to_try[(attempt - 1) % len(models_to_try)]
        # Risoluzione verticale 720x1280
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true&seed={seed}&model={model_choice}"
        
        try:
            print(f"  🎨 Download Immagine Ink&Wash [Modello: {model_choice}, Seed: {seed}] (Tentativo {attempt}/{max_retries})...", flush=True)
            resp = requests.get(url, timeout=50, verify=False)
            
            if resp.status_code == 200 and len(resp.content) > 10000:
                temp_file = f"{output_img}.tmp"
                with open(temp_file, "wb") as f:
                    f.write(resp.content)
                
                try:
                    with Image.open(temp_file) as test_pil:
                        test_pil.verify()
                    with Image.open(temp_file) as valid_pil:
                        valid_pil.convert("RGB").save(output_img, "JPEG", quality=95)
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    print(f"  ✅ Immagine verificata ({round(os.path.getsize(output_img)/1024, 1)} KB): {os.path.basename(output_img)}")
                    return True
                except Exception as verify_err:
                    print(f"  ⚠️ File corrotto ({verify_err})")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
            else:
                print(f"  ⚠️ Tentativo {attempt} fallito (Status HTTP {resp.status_code})")
        except Exception as conn_err:
            print(f"  ⚠️ Errore tentativo {attempt}: {conn_err}")

        if attempt < max_retries:
            time.sleep(3)

    print("  ⚠️ Fallback grafico attivato...")
    crea_immagine_fallback(output_img, scene_desc)
    return True


def crea_immagine_fallback(output_img, testo_descrittivo):
    """Fallback armonizzato con la palette acquerello pergamena & blu polvere."""
    img = Image.new("RGB", (720, 1280), color=(245, 238, 220))
    draw = ImageDraw.Draw(img)
    for y in range(1280):
        ratio = y / 1280.0
        r = int(245 - (245 - 28) * ratio)
        g = int(238 - (238 - 45) * ratio)
        b = int(220 - (220 - 75) * ratio)
        draw.line([(0, y), (720, y)], fill=(r, g, b))
    
    draw.ellipse([260, 200, 460, 400], outline=(218, 165, 32), width=3)
    draw.ellipse([280, 220, 440, 380], fill=(255, 248, 230), outline=(218, 165, 32), width=1)
    draw.rectangle([280, 750, 440, 830], fill=(240, 230, 210), outline=(139, 69, 19), width=2)
    img.save(output_img, "JPEG", quality=95)


# ── OVERLAY GRAFICO CON SOTTOTITOLI E TITOLO (PILLOW) ──────────────────────
def crea_overlay_grafico(testo, titolo_libro, autore, output_overlay, is_outro=False):
    img = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font_kicker = ImageFont.truetype("arial.ttf", 20)
        font_titolo = ImageFont.truetype("arialbd.ttf", 26)
        font_autore = ImageFont.truetype("arial.ttf", 22)
        font_sub = ImageFont.truetype("arialbd.ttf", 26)
        font_brand = ImageFont.truetype("arialbd.ttf", 30)
        font_motto = ImageFont.truetype("arial.ttf", 22)
        font_submotto = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        try:
            font_kicker = ImageFont.truetype("DejaVuSans.ttf", 20)
            font_titolo = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
            font_autore = ImageFont.truetype("DejaVuSans.ttf", 22)
            font_sub = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
            font_brand = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
            font_motto = ImageFont.truetype("DejaVuSans.ttf", 22)
            font_submotto = ImageFont.truetype("DejaVuSans.ttf", 18)
        except Exception:
            font_kicker = font_titolo = font_autore = font_sub = font_brand = font_motto = font_submotto = ImageFont.load_default()

    # 1. BADGE SUPERIORE: Cornice blu notte e oro satinato (y=45-155)
    draw.rounded_rectangle([40, 45, 680, 155], radius=20, fill=(15, 23, 42, 230), outline=(245, 158, 11, 245), width=3)
    draw.text((360, 68), "— I GRANDI CLASSICI —", fill=(255, 215, 0), font=font_kicker, anchor="mm")
    draw.text((360, 102), titolo_libro.upper(), fill=(255, 255, 255), font=font_titolo, anchor="mm")
    draw.text((360, 134), f"di {autore}", fill=(185, 220, 255), font=font_autore, anchor="mm")

    # 2. BOX SOTTOTITOLI: Terzo inferiore (y=950-1100)
    draw.rounded_rectangle([40, 950, 680, 1100], radius=18, fill=(0, 0, 0, 185), outline=(255, 255, 255, 130), width=2)
    
    import textwrap
    wrapped_lines = textwrap.wrap(testo, width=32)
    line_height = 36
    total_text_h = len(wrapped_lines) * line_height
    start_y = 950 + (150 - total_text_h) / 2 + (line_height / 2)
    
    for idx, line in enumerate(wrapped_lines):
        y_pos = start_y + (idx * line_height)
        draw.text((361, y_pos + 1), line, fill=(0, 0, 0, 255), font=font_sub, anchor="mm")
        draw.text((360, y_pos), line, fill=(255, 255, 255, 255), font=font_sub, anchor="mm")

    # 3. OUTRO BADGE (y=1115-1245): Brand Identity Immobiliare Giancani
    if is_outro:
        draw.rounded_rectangle([40, 1115, 680, 1245], radius=20, fill=(16, 26, 50, 235), outline=(245, 158, 11, 245), width=3)
        draw.text((360, 1145), "IMMOBILIARE GIANCANI", fill=(255, 215, 0), font=font_brand, anchor="mm")
        draw.text((360, 1182), "Il Valore di Sentirsi a Casa", fill=(255, 255, 255), font=font_motto, anchor="mm")
        draw.text((360, 1215), "Esperienza  •  Passione  •  Fiducia", fill=(180, 225, 255), font=font_submotto, anchor="mm")

    img.save(output_overlay, "PNG")


# ── FFMPEG AUDIO & VIDEO PIPELINE ───────────────────────────────────────────
def ottieni_durata_audio(audio_path):
    cmd = [FFMPEG_EXE, "-i", audio_path]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    _, stderr = p.communicate()
    for line in stderr.decode('utf-8', errors='ignore').split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return max(3.5, float(h)*3600 + float(m)*60 + float(s))
    return 4.5


def crea_clip_ken_burns(img_path, audio_path, overlay_path, clip_output, idx):
    durata = ottieni_durata_audio(audio_path) + 0.35
    num_frames = int(durata * 25)
    
    if idx % 2 == 1:
        zoom_filter = f"zoompan=z='min(zoom+0.0012,1.18)':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"
    else:
        zoom_filter = f"zoompan=z='if(lte(zoom,1.0),1.18,max(1.001,zoom-0.0012))':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"

    filter_complex = f"[0:v]{zoom_filter}[bg];[bg][1:v]overlay=0:0[v]"
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", img_path,
        "-i", overlay_path,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "2:a",
        "-c:v", "libx264", "-preset", "fast", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(durata),
        clip_output
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def ottieni_o_genera_musica(durata_totale):
    tracce_disponibili = []
    if os.path.exists(MUSIC_DIR):
        for f in os.listdir(MUSIC_DIR):
            if f.lower().endswith(".mp3"):
                tracce_disponibili.append(os.path.join(MUSIC_DIR, f))
                
    if tracce_disponibili:
        scelte_top = [t for t in tracce_disponibili if "pianoforte" in t.lower() or "ambient" in t.lower()]
        scelta = random.choice(scelte_top if scelte_top else tracce_disponibili)
        print(f"  🎵 Musica di sottofondo selezionata: {os.path.basename(scelta)}")
        return scelta

    fallback_music = os.path.join(OUTPUT_DIR, "ambient_sottofondo_fallback.mp3")
    if not os.path.exists(fallback_music):
        print("  🎵 Generazione audio d'atmosfera con FFmpeg lavfi...")
        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "lavfi", "-i", f"sine=frequency=220:duration={durata_totale+10}",
            "-af", "volume=0.08,lowpass=f=400,afade=t=in:ss=0:d=2,afade=t=out:st=15:d=3",
            "-c:a", "libmp3lame", "-b:a", "128k",
            fallback_music
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return fallback_music


def monta_video_finale(clips, output_video, durata_totale):
    concat_list_file = os.path.join(OUTPUT_DIR, "concat_clips.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for c in clips:
            safe_c = c.replace("\\", "/")
            f.write(f"file '{safe_c}'\n")

    video_unito_temp = os.path.join(OUTPUT_DIR, "video_temp_senza_musica.mp4")
    
    cmd_concat = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        video_unito_temp
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    musica_file = ottieni_o_genera_musica(durata_totale)
    filter_mix = (
        f"[1:a]volume=0.12,afade=t=in:ss=0:d=1.5,afade=t=out:st={max(2, durata_totale - 2.5)}:d=2.5[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    
    cmd_mix = [
        FFMPEG_EXE, "-y",
        "-i", video_unito_temp,
        "-stream_loop", "-1", "-i", musica_file,
        "-filter_complex", filter_mix,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_video
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    if os.path.exists(video_unito_temp):
        os.remove(video_unito_temp)


# ── TELEGRAM BOT API ────────────────────────────────────────────────────────
def invia_su_telegram(video_path, storia):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Token Telegram o Chat ID mancanti nei Secrets. Salto invio.")
        return False
        
    print("\n📲 Invio video finale a Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    
    caption = (
        f"🐱 *IL GATTO NARRATORE DI GRANDI CLASSICI*\n\n"
        f"📖 *{storia['titolo']}* ({storia['anno']})\n"
        f"✍️ Autore: *{storia['autore']}*\n"
        f"🎭 Genere: _{storia['genere']}_\n\n"
        f"💬 *Estratto e Narrazione (Colonna F):*\n"
        f"«_{storia['testo_colonna_f']}_»\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 *Produzione e Personal Branding:*\n"
        f"🏠 ⭐ *IMMOBILIARE GIANCANI* ⭐\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"#GrandiClassici #Letteratura #GattoNarratore #AntiqueIllustration #Storytelling #ImmobiliareGiancani"
    )
    
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "✨ Sito Web Immobiliare Giancani", "url": "https://immobiliaregiancani.it"}
            ],
            [
                {"text": "🔄 Altra Storia Classica", "callback_data": "NUOVA_STORIA"}
            ]
        ]
    }
    
    try:
        with open(video_path, "rb") as vf:
            files = {"video": vf}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "parse_mode": "Markdown",
                "supports_streaming": True,
                "reply_markup": json.dumps(inline_keyboard)
            }
            resp = requests.post(url, data=data, files=files, timeout=90, verify=False)
            if resp.status_code == 200:
                print("✅ Video inviato con successo su Telegram!")
                return True
            else:
                print(f"❌ Errore risposta Telegram ({resp.status_code}): {resp.text}")
                return False
    except Exception as ex:
        print(f"❌ Errore durante l'invio su Telegram: {ex}")
        return False


# ── PIPELINE PRINCIPALE ─────────────────────────────────────────────────────
async def esegui_pipeline(story_id=None, voice="it-IT-DiegoNeural"):
    start_time = time.time()
    print("="*75)
    print("🐱 AVVIO BOT: GATTO NARRATORE UMANIZZATO (INK & WASH FIABESCO) — 9:16")
    print("⭐ Produzione & Strategia a cura di: IMMOBILIARE GIANCANI")
    print("="*75)

    storia = estrai_storia_colonna_f(CSV_PATH, story_id)
    scene = crea_struttura_scene(storia)
    
    clips = []
    durata_totale = 0.0
    
    for idx, s in enumerate(scene, start=1):
        print(f"\n--- 🎬 [SCENA {idx}/4] {storia['titolo']} ---")
        base_name = f"storia_{storia['id']}_scena_{idx}"
        audio_file = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
        img_file = os.path.join(OUTPUT_DIR, f"{base_name}.jpg")
        overlay_file = os.path.join(OUTPUT_DIR, f"{base_name}_overlay.png")
        clip_file = os.path.join(OUTPUT_DIR, f"{base_name}_clip.mp4")
        
        # Audio TTS
        print(f"  🎙️ Sintesi vocale: \"{s['testo'][:45]}...\"")
        await genera_voce_edge_tts(s["testo"], audio_file, voce=voice)
        durata_scena = ottieni_durata_audio(audio_file)
        durata_totale += durata_scena
        
        # Immagine AI
        story_id_int = int(storia["id"]) if str(storia["id"]).isdigit() else 1
        scene_seed = story_id_int * 100 + idx
        scarica_immagine_pollinations(s["scene_desc"], img_file, seed=scene_seed)
        
        # Overlay grafico
        crea_overlay_grafico(s["testo"], storia["titolo"], storia["autore"], overlay_file, is_outro=s["is_outro"])
        
        # Clip Ken Burns
        print(f"  🎞️ Montaggio Ken Burns ({round(durata_scena, 1)}s)...")
        crea_clip_ken_burns(img_file, audio_file, overlay_file, clip_file, idx)
        clips.append(clip_file)

    # Rendering Finale
    video_finale = os.path.join(OUTPUT_DIR, f"reels_gatto_classico_{storia['id']}.mp4")
    print(f"\n🎬 Montaggio finale del video: {os.path.basename(video_finale)}...")
    monta_video_finale(clips, video_finale, durata_totale)
    
    file_mb = round(os.path.getsize(video_finale) / (1024 * 1024), 2)
    print(f"✅ Video finale generato con successo! ({file_mb} MB, Durata: ~{round(durata_totale, 1)}s)")

    invia_su_telegram(video_finale, storia)

    elapsed = round(time.time() - start_time, 1)
    print("\n" + "="*75)
    print(f"✨ PIPELINE COMPLETATA CON SUCCESSO IN {elapsed} SECONDI!")
    print("⭐ PROGETTO E REALIZZAZIONE: IMMOBILIARE GIANCANI ⭐")
    print("="*75 + "\n")


# ── ENTRY POINT CLI ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot Gatto Narratore di Grandi Classici (GitHub Actions)")
    parser.add_argument("--id", type=str, default=None, help="ID specifico della storia da generare")
    parser.add_argument("--voice", type=str, default="it-IT-DiegoNeural", help="Voce Edge-TTS")
    args = parser.parse_args()

    asyncio.run(esegui_pipeline(story_id=args.id, voice=args.voice))
