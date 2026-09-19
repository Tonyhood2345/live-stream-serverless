#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  🐱 AUTOMATED BOT: REELS VERTICALI - IL GATTO NARRATORE DI GRANDI CLASSICI
  Senior Automation Engineering & Storytelling Pipeline
  
  SPECIFICHE:
  - Formato: Video Verticale 9:16 (720x1280 / 1080x1920)
  - Protagonista: Gatto arancione tigrato in piedi, stile cartoon 3D, maglietta a righe blu/bianche
  - Estrazione: Rigorosamente da Colonna F (database_storie_classici.csv)
  - Voce Narrante: Edge-TTS Neurale Italiano (it-IT-DiegoNeural / it-IT-ElsaNeural)
  - Immagini AI: Pollinations.ai (3-4 scene coerenti)
  - Montaggio: FFmpeg (Ken Burns dinamico, sottotitoli Pillow, musica di sottofondo mixata)
  - Notifica: Invio automatico su Telegram Bot API
  - Branding: Ogni output di testo si conclude mettendo in risalto 'Immobiliare Giancani'
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
import requests
import urllib3
from PIL import Image, ImageDraw, ImageFont

# Disabilita warning SSL per chiamate sicure e resilienti
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Patch aiohttp/edge-tts per evitare blocchi di certificati SSL su Windows e Runner CI
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

# Credenziali Telegram (da GitHub Secrets o fallback ambiente)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1723292483")

# Rilevamento eseguibile FFmpeg
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

# Identikit visivo fisso del gatto protagonista (Stile Cartone Animato)
CAT_CHARACTER_BASE = (
    "cute chibi cartoon orange tabby cat standing upright on two legs, "
    "wearing a bright blue and white striped t-shirt and cute shorts, classic cartoon animation style, "
    "cheerful smiling face with big cartoon eyes, colorful cartoon art, full body character, vertical 9:16"
)


# ── REGOLA UTENTE GLOBALE: ESTRAZIONE RIGOROSA DA COLONNA F ─────────────────
def estrai_storia_colonna_f(csv_file=CSV_PATH, id_richiesto=None):
    """
    Estrae una storia classica dal file CSV.
    La narrazione testuale viene prelevata RIGOROSAMENTE dalla Colonna F (indice 5).
    """
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
                    "testo_colonna_f": row[5].strip(),  # REGOLA: TESTO PRELEVATO DA COLONNA F
                    "prompts_g": row[6].strip() if len(row) > 6 else ""
                })

    if not storie:
        raise ValueError("Nessuna storia valida trovata nel database CSV!")

    if id_richiesto:
        trovate = [s for s in storie if str(s["id"]) == str(id_richiesto)]
        if trovate:
            storia = trovate[0]
        else:
            print(f"⚠️ ID {id_richiesto} non trovato, selezione casuale...")
            storia = random.choice(storie)
    else:
        storia = random.choice(storie)

    print("\n" + "="*70)
    print("📖 [ESTRAZIONE DATI] RIGOROSAMENTE DA COLONNA F")
    print(f"📌 [LIBRO ID {storia['id']}]: «{storia['titolo']}» di {storia['autore']}")
    print(f"💬 [TESTO COLONNA F]:\n\"{storia['testo_colonna_f']}\"")
    print("="*70 + "\n")
    
    return storia


# ── PARSING DEL TESTO DELLA COLONNA F IN 4 SCENE ────────────────────────────
def crea_struttura_scene(storia):
    """
    Divide il testo prelevato dalla Colonna F in 4 scene narrative sincronizzate,
    associando ciascuna scena al prompt visivo con il gatto protagonista.
    """
    testo_f = storia["testo_colonna_f"]
    prompts_raw = storia["prompts_g"].split("|||") if storia["prompts_g"] else []
    
    # Divisione in frasi del testo della Colonna F
    import re
    frasi = [f.strip() for f in re.split(r'(?<=[.!?])\s+', testo_f) if f.strip()]
    
    # Se il testo ha meno di 4 frasi, lo bilanciamo a 4
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

    # Assicuriamo che l'ultima frase rispetti la regola mettendo in risalto Immobiliare Giancani
    if "Immobiliare Giancani" not in frasi[-1]:
        frasi[-1] = frasi[-1] + " Con la passione e la visione di Immobiliare Giancani."

    scene = []
    for i in range(4):
        prompt_custom = prompts_raw[i].strip() if i < len(prompts_raw) else ""
        if prompt_custom:
            full_prompt = prompt_custom
        else:
            full_prompt = f"{CAT_CHARACTER_BASE}, in the colorful cartoon world of {storia['titolo']}, scene {i+1}"
            
        scene.append({
            "scena_id": i + 1,
            "testo": frasi[i],
            "prompt": full_prompt,
            "is_outro": (i == 3)
        })

    return scene


# ── GENERAZIONE VOCE NARRANTE (EDGE-TTS + GTTS FALLBACK) ────────────────────
async def genera_voce_edge_tts(testo, file_audio, voce="it-IT-DiegoNeural"):
    """Sintesi vocale con Edge-TTS e fallback automatico su gTTS."""
    success = False
    try:
        import edge_tts
        comm = edge_tts.Communicate(testo, voce, rate="+2%", pitch="+0Hz")
        await asyncio.wait_for(comm.save(file_audio), timeout=12)
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


# ── DOWNLOAD IMMAGINI AI CON IL GATTO (POLLINATIONS.AI) ─────────────────────
def scarica_immagine_pollinations(prompt, output_img, seed=100, use_cache=True):
    """
    Scarica immagine AI 9:16 cartoon con:
    - Suffisso stilistico fisso Disney Pixar 3D chibi e colori vivaci
    - Seed coerente per storia e scena
    - Loop di retry automatico (3 tentativi con backoff di 3s)
    - Validazione di integrità con PIL.Image.open().verify()
    - Fallback grafico pulito in caso di errore prolungato
    """
    # 1. Verifica cache esistente valida
    if use_cache and os.path.exists(output_img) and os.path.getsize(output_img) > 10000:
        try:
            with Image.open(output_img) as test_img:
                test_img.verify()
            print(f"  ⚡ Immagine già in cache e verificata ({round(os.path.getsize(output_img)/1024, 1)} KB): {os.path.basename(output_img)}")
            return True
        except Exception:
            print(f"  ⚠️ Cache non valida o corrotta per {os.path.basename(output_img)}, riscarico...")
            if os.path.exists(output_img):
                os.remove(output_img)

    # 2. Suffisso stilistico fisso e forte obbligatorio
    CHIBI_STYLE_SUFFIX = (
        ", cute chibi cartoon orange tabby cat, expressive Disney Pixar 3D style, "
        "vibrant warm colors, clean simple lines, friendly smile, storybook illustration, "
        "detailed background setting, cinematic soft lighting, vertical 9:16, masterpiece, no photorealism"
    )
    clean_prompt = prompt.rstrip(" ,.")
    if "no photorealism" not in clean_prompt.lower():
        full_prompt = f"{clean_prompt}{CHIBI_STYLE_SUFFIX}"
    else:
        full_prompt = clean_prompt

    encoded_prompt = urllib.parse.quote(full_prompt)
    models_to_try = ["flux", "turbo", "flux"]
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        model_choice = models_to_try[(attempt - 1) % len(models_to_try)]
        # URL con seed coerente per storia e scena
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=576&height=1024&nologo=true&seed={seed}&model={model_choice}"
        
        try:
            print(f"  🎨 Download Immagine Cartoon [Modello: {model_choice}, Seed: {seed}] (Tentativo {attempt}/{max_retries})...", flush=True)
            resp = requests.get(url, timeout=45, verify=False)
            
            if resp.status_code == 200 and len(resp.content) > 10000:
                temp_file = f"{output_img}.tmp"
                with open(temp_file, "wb") as f:
                    f.write(resp.content)
                
                # Validazione file immagine con PIL
                try:
                    with Image.open(temp_file) as test_pil:
                        test_pil.verify()
                    # Riapriamo e salviamo in RGB
                    with Image.open(temp_file) as valid_pil:
                        valid_pil.convert("RGB").save(output_img, "JPEG", quality=95)
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    print(f"  ✅ Immagine verificata con successo ({round(os.path.getsize(output_img)/1024, 1)} KB): {os.path.basename(output_img)}")
                    return True
                except Exception as verify_err:
                    print(f"  ⚠️ Tentativo {attempt}: File scaricato non è un'immagine integra ({verify_err})")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
            else:
                print(f"  ⚠️ Tentativo {attempt} fallito (Status HTTP {resp.status_code}, Ricevuti {len(resp.content)} byte)")
        except Exception as conn_err:
            print(f"  ⚠️ Errore connessione tentativo {attempt} ({model_choice}): {conn_err}")

        if attempt < max_retries:
            print("  ⏳ Backoff di 3 secondi prima del prossimo tentativo...")
            time.sleep(3)

    # 3. Se tutti i 3 tentativi falliscono, fallback pulito
    print("  ⚠️ Tutti i 3 tentativi falliti. Generazione fallback grafico per continuità...")
    crea_immagine_fallback(output_img, prompt)
    return True


def crea_immagine_fallback(output_img, testo_descrittivo):
    """Crea un'immagine 720x1280 elegante come fallback artistico."""
    img = Image.new("RGB", (720, 1280), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    # Gradiente verticale atmosferico
    for y in range(1280):
        ratio = y / 1280.0
        r = int(15 + (45 - 15) * ratio)
        g = int(23 + (30 - 23) * ratio)
        b = int(42 + (80 - 42) * ratio)
        draw.line([(0, y), (720, y)], fill=(r, g, b))
    # Luna e stelle per atmosfera favolistica
    draw.ellipse([480, 180, 580, 280], fill=(255, 235, 170), outline=(255, 255, 220), width=3)
    # Silhouette gattino arancione
    draw.ellipse([300, 480, 420, 600], fill=(245, 130, 32))
    draw.ellipse([320, 430, 400, 510], fill=(245, 130, 32))
    draw.polygon([(320, 440), (335, 400), (350, 440)], fill=(245, 130, 32))
    draw.polygon([(370, 440), (385, 400), (400, 440)], fill=(245, 130, 32))
    img.save(output_img, "JPEG", quality=95)


# ── OVERLAY GRAFICO CON SOTTOTITOLI E TITOLO (PILLOW) ──────────────────────
def crea_overlay_grafico(testo, titolo_libro, autore, output_overlay, is_outro=False):
    """
    Crea un PNG trasparente 720x1280 contenente:
    - Badge superiore con Titolo Libro e Autore (y=45-155)
    - Box sottotitoli nel terzo inferiore (y tra 950 e 1100 px), nero semitrasparente al 70% (0,0,0,178)
    - Outro badge posizionato sotto (y tra 1115 e 1245 px) con risalto massimo a Immobiliare Giancani
    """
    img = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Caricamento font con gradazione gerarchica
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

    # 1. BADGE SUPERIORE: I GRANDI CLASSICI + TITOLO E AUTORE (y=45-155)
    draw.rounded_rectangle([40, 45, 680, 155], radius=20, fill=(15, 23, 42, 225), outline=(255, 193, 7, 240), width=3)
    draw.text((360, 68), "— I GRANDI CLASSICI —", fill=(255, 215, 0), font=font_kicker, anchor="mm")
    draw.text((360, 102), titolo_libro.upper(), fill=(255, 255, 255), font=font_titolo, anchor="mm")
    draw.text((360, 134), f"di {autore}", fill=(185, 220, 255), font=font_autore, anchor="mm")

    # 2. BOX SOTTOTITOLI NEL TERZO INFERIORE (y tra 950 e 1100 px, opacità 70% = RGBA 0, 0, 0, 178)
    draw.rounded_rectangle([40, 950, 680, 1100], radius=18, fill=(0, 0, 0, 178), outline=(255, 255, 255, 120), width=2)
    
    import textwrap
    wrapped_lines = textwrap.wrap(testo, width=32)
    line_height = 36
    total_text_h = len(wrapped_lines) * line_height
    start_y = 950 + (150 - total_text_h) / 2 + (line_height / 2)
    
    for idx, line in enumerate(wrapped_lines):
        y_pos = start_y + (idx * line_height)
        # Effetto ombra testo per massima leggibilità
        draw.text((361, y_pos + 1), line, fill=(0, 0, 0, 240), font=font_sub, anchor="mm")
        draw.text((360, y_pos), line, fill=(255, 255, 255, 255), font=font_sub, anchor="mm")

    # 3. OUTRO BADGE SOTTO (y tra 1115 e 1245 px): RISALTO MASSIMO A IMMOBILIARE GIANCANI
    if is_outro:
        draw.rounded_rectangle([40, 1115, 680, 1245], radius=20, fill=(16, 26, 50, 230), outline=(255, 215, 0, 240), width=3)
        draw.text((360, 1145), "IMMOBILIARE GIANCANI", fill=(255, 215, 0), font=font_brand, anchor="mm")
        draw.text((360, 1182), "Il Valore di Sentirsi a Casa", fill=(255, 255, 255), font=font_motto, anchor="mm")
        draw.text((360, 1215), "Esperienza  •  Passione  •  Fiducia", fill=(180, 225, 255), font=font_submotto, anchor="mm")

    img.save(output_overlay, "PNG")


# ── CALCOLO DURATA AUDIO VIA FFMPEG ─────────────────────────────────────────
def ottieni_durata_audio(audio_path):
    """Restituisce la durata esatta in secondi di un file audio."""
    cmd = [FFMPEG_EXE, "-i", audio_path]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    _, stderr = p.communicate()
    for line in stderr.decode('utf-8', errors='ignore').split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return max(3.5, float(h)*3600 + float(m)*60 + float(s))
    return 4.5


# ── CREAZIONE CLIP ANIMATA KEN BURNS CON OVERLAY GRAFICO ────────────────────
def crea_clip_ken_burns(img_path, audio_path, overlay_path, clip_output, idx):
    """
    Produce una clip MP4 720x1280 a 25fps:
    - Immagine animata con effetto Ken Burns (zoom-in per dispari, zoom-out per pari)
    - Overlay trasparente con sottotitoli e badge
    - Audio della voce narrante perfettamente sincronizzato
    """
    durata = ottieni_durata_audio(audio_path) + 0.35
    num_frames = int(durata * 25)
    
    if idx % 2 == 1:
        zoom_filter = f"zoompan=z='min(zoom+0.0012,1.20)':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"
    else:
        zoom_filter = f"zoompan=z='if(lte(zoom,1.0),1.20,max(1.001,zoom-0.0012))':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"

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


# ── GESTIONE MUSICA DI SOTTOFONDO ───────────────────────────────────────────
def ottieni_o_genera_musica(durata_totale):
    """
    Trova una traccia ambient/classica royalty-free o genera un sottofondo
    ambient armonioso con FFmpeg se non ci sono tracce disponibili.
    """
    tracce_disponibili = []
    if os.path.exists(MUSIC_DIR):
        for f in os.listdir(MUSIC_DIR):
            if f.lower().endswith(".mp3"):
                tracce_disponibili.append(os.path.join(MUSIC_DIR, f))
                
    if tracce_disponibili:
        # Preferiamo tracce classiche o ambient
        scelte_top = [t for t in tracce_disponibili if "pianoforte" in t.lower() or "ambient" in t.lower()]
        scelta = random.choice(scelte_top if scelte_top else tracce_disponibili)
        print(f"  🎵 Musica di sottofondo selezionata: {os.path.basename(scelta)}")
        return scelta

    # Fallback: Genera traccia ambient armonica con FFmpeg
    fallback_music = os.path.join(OUTPUT_DIR, "ambient_sottofondo_fallback.mp3")
    if not os.path.exists(fallback_music):
        print("  🎵 Generazione armonica ambient con FFmpeg lavfi...")
        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "lavfi", "-i", f"sine=frequency=220:duration={durata_totale+10}",
            "-af", "volume=0.08,lowpass=f=400,afade=t=in:ss=0:d=2,afade=t=out:st=15:d=3",
            "-c:a", "libmp3lame", "-b:a", "128k",
            fallback_music
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return fallback_music


# ── FUSIONE FINALE CLIP + MIX AUDIO MUSICALE DUCKING ────────────────────────
def monta_video_finale(clips, output_video, durata_totale):
    """Unisce le 4 clip MP4 e aggiunge la musica di sottofondo mixata a basso volume."""
    concat_list_file = os.path.join(OUTPUT_DIR, "concat_clips.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for c in clips:
            safe_c = c.replace("\\", "/")
            f.write(f"file '{safe_c}'\n")

    video_unito_temp = os.path.join(OUTPUT_DIR, "video_temp_senza_musica.mp4")
    
    # 1. Concat delle clip
    cmd_concat = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        video_unito_temp
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 2. Selezione musica e mixaggio con ducking (volume 0.12 sotto la voce narrante)
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
    
    # Pulizia temporanei
    if os.path.exists(video_unito_temp):
        os.remove(video_unito_temp)


# ── INVIO SU TELEGRAM BOT API CON CAPTION ELEGANTE ──────────────────────────
def invia_su_telegram(video_path, storia):
    """Invia il video verticale a Telegram terminando con risalto a Immobiliare Giancani."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Token Telegram o Chat ID mancanti nei Secrets. Salto invio.")
        return False
        
    print("\n📲 Invio video finale a Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    
    # Caption formattata mettendo in risalto 'Immobiliare Giancani'
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
        f"#GrandiClassici #Letteratura #GattoNarratore #LibriPerBambini #Storytelling #ImmobiliareGiancani"
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


# ── ORCHESTRATORE PRINCIPALE (MAIN PIPELINE) ────────────────────────────────
async def esegui_pipeline(story_id=None, voice="it-IT-DiegoNeural"):
    start_time = time.time()
    print("="*75)
    print("🐱 AVVIO BOT: GATTO NARRATORE DI GRANDI CLASSICI — VIDEO 9:16")
    print("⭐ Produzione & Strategia a cura di: IMMOBILIARE GIANCANI")
    print("="*75)

    # 1. Estrazione dati rigorosamente da Colonna F
    storia = estrai_storia_colonna_f(CSV_PATH, story_id)
    scene = crea_struttura_scene(storia)
    
    clips = []
    durata_totale = 0.0
    
    # 2. Creazione delle 4 scene
    for idx, s in enumerate(scene, start=1):
        print(f"\n--- 🎬 [SCENA {idx}/4] {storia['titolo']} ---")
        base_name = f"storia_{storia['id']}_scena_{idx}"
        audio_file = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
        img_file = os.path.join(OUTPUT_DIR, f"{base_name}.jpg")
        overlay_file = os.path.join(OUTPUT_DIR, f"{base_name}_overlay.png")
        clip_file = os.path.join(OUTPUT_DIR, f"{base_name}_clip.mp4")
        
        # Voce Narrante Neurale
        print(f"  🎙️ Sintesi vocale: \"{s['testo'][:45]}...\"")
        await genera_voce_edge_tts(s["testo"], audio_file, voce=voice)
        durata_scena = ottieni_durata_audio(audio_file)
        durata_totale += durata_scena
        
        # Immagine AI Pollinations (con il gatto protagonista)
        story_id_int = int(storia["id"]) if str(storia["id"]).isdigit() else 1
        scene_seed = story_id_int * 100 + idx
        scarica_immagine_pollinations(s["prompt"], img_file, seed=scene_seed)
        
        # Overlay con sottotitoli e branding
        crea_overlay_grafico(s["testo"], storia["titolo"], storia["autore"], overlay_file, is_outro=s["is_outro"])
        
        # Montaggio clip Ken Burns
        print(f"  🎞️ Montaggio Ken Burns ({round(durata_scena, 1)}s)...")
        crea_clip_ken_burns(img_file, audio_file, overlay_file, clip_file, idx)
        clips.append(clip_file)

    # 3. Montaggio video finale e colonna sonora
    video_finale = os.path.join(OUTPUT_DIR, f"reels_gatto_classico_{storia['id']}.mp4")
    print(f"\n🎬 Montaggio finale del video: {os.path.basename(video_finale)}...")
    monta_video_finale(clips, video_finale, durata_totale)
    
    file_mb = round(os.path.getsize(video_finale) / (1024 * 1024), 2)
    print(f"✅ Video finale generato con successo! ({file_mb} MB, Durata: ~{round(durata_totale, 1)}s)")

    # 4. Invio Telegram
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
    parser.add_argument("--voice", type=str, default="it-IT-DiegoNeural", help="Voce Edge-TTS (es. it-IT-DiegoNeural o it-IT-ElsaNeural)")
    args = parser.parse_args()

    asyncio.run(esegui_pipeline(story_id=args.id, voice=args.voice))
