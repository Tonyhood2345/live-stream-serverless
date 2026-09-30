#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  🎬 BOT REELS MASTER — PIPELINE AUTOMATIZZATA MULTI-CANALE (9:16)
  Direzione Tecnica, Regia & Storytelling: IMMOBILIARE GIANCANI
  
  SPECIFICHE OPERATIVE:
  1. File Master: bot_reels_master.py (Architettura centralizzata e modulare)
  2. Download Immagini Pollinations Anti-Timeout:
     - Prompt compatto (max 175 car.) con stile Cartoon Cel Art 2D
     - Negative prompt obbligatorio anti-3D/fotorealismo
     - Motore 'turbo' o default (no flux), timeout 16s, anti-cache &ts= e pausa 3s
  3. Overlay Grafico:
     - Badge titolo superiore ESCLUSIVAMENTE sulla prima scena (is_intro and idx == 1)
     - Sottotitoli stile Comic Sticker (doppio contorno 360°, ombra profonda, font solare)
  4. Routing Social e Pubblicazione Centralizzata:
     - TUTTI -> Telegram (Chat e Canale @immobiliaregiancani)
     - BIBBIA -> FB 'Eterno nostra giustizia', FB 'Antonio Giancani', YT Shorts 'Eterno nostra giustizia'
     - MITOLOGIA (Ore 18:00) -> FB 'Antonio Giancani'
     - PILLOLE (Ore 06:00) -> FB 'Immobiliare Giancani' (Reel + Post Colonna F), FB 'Antonio Giancani', YT Shorts 'Immobiliare Giancani'
     - LIBRI (Grandi Classici) -> FB 'Antonio Giancani'
  5. Regola Globale: Testi prelevati rigorosamente dalla Colonna F.
     Ogni output si conclude mettendo in risalto 'Immobiliare Giancani'.
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
import shutil
import datetime
import requests
import urllib3
import io
import base64
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Integrazione YouTube Shorts
try:
    from youtube_uploader import genera_metadati_youtube, pubblica_video_youtube
except Exception:
    genera_metadati_youtube = None
    pubblica_video_youtube = None

# Integrazione TikTok Reels (@immobiliare_giancani)
try:
    from tiktok_uploader import pubblica_video_tiktok
except Exception:
    pubblica_video_tiktok = None

# Disabilita warning SSL per chiamate resilienti
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Patch aiohttp per evitare blocchi certificati SSL su Windows e Runner CI
try:
    import aiohttp
    orig_ws_connect = aiohttp.ClientSession.ws_connect
    def patched_ws_connect(self, *args, **kwargs):
        kwargs['ssl'] = False
        return orig_ws_connect(self, *args, **kwargs)
    aiohttp.ClientSession.ws_connect = patched_ws_connect
except Exception:
    pass


# ── MOTORE ANTI-DISTORSIONE: ADATTAMENTO 9:16 CON PROPORZIONI RIGOROSE ─────
def adatta_immagine_9_16(im, target_w=720, target_h=1280):
    """
    Adatta qualsiasi immagine al target verticale 9:16 (720x1280) preservando
    RIGOROSAMENTE le proporzioni anatomiche e compositive con ImageOps.fit (smart center-crop).
    Elimina alla radice ogni problema di allungamento o distorsione dei disegni.
    """
    return ImageOps.fit(im.convert("RGB"), (target_w, target_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


# ── CONFIGURAZIONI GLOBALI ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "video_storie_output")
CSV_PATH = os.path.join(BASE_DIR, "database_storie_classici.csv")
CSV_BIBBIA_PATH = os.path.join(BASE_DIR, "database_storie_bibliche.csv")
CSV_MITOLOGIA_PATH = os.path.join(BASE_DIR, "database_storie_mitologia.csv")
CSV_PILLOLE_PATH = os.path.join(BASE_DIR, "database_pillole_immobiliari_legali.csv")
MUSIC_DIR = os.path.join(BASE_DIR, "musica_sottofondo")
CUSTOM_IMG_DIR = os.path.join(BASE_DIR, "immagini_personalizzate")

# Voci neurali distinte per ciascun bot / rubrica
VOICES_BY_MODE = {
    "mitologia": "it-IT-DiegoNeural",     # Maschile epico e narrativo (Ore 18:00)
    "bibbia":    "it-IT-GiuseppeNeural",  # Maschile solenne e saggio (Ore 20:00)
    "standard":  "it-IT-ElsaNeural",      # Femminile dolce e fiabesca per i Grandi Classici
    "pillole":   "it-IT-IsabellaNeural"   # Femminile chiara e professionale per la tutela immobiliare (Ore 06:00)
}

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CUSTOM_IMG_DIR, exist_ok=True)

# Credenziali Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1723292483")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@immobiliaregiancani")

# Credenziali Google Gemini, Together AI (FLUX) e Replicate (SDXL)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY", "")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")

env_local = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_local):
    try:
        with open(env_local, "r", encoding="utf-8") as ef:
            for eline in ef:
                eline = eline.strip()
                if not eline or eline.startswith("#"):
                    continue
                if eline.startswith("GEMINI_API_KEY=") and not GEMINI_API_KEY:
                    GEMINI_API_KEY = eline.split("=", 1)[1].strip().strip('"').strip("'")
                elif eline.startswith("TOGETHER_API_KEY=") and not TOGETHER_API_KEY:
                    TOGETHER_API_KEY = eline.split("=", 1)[1].strip().strip('"').strip("'")
                elif eline.startswith("REPLICATE_API_TOKEN=") and not REPLICATE_API_TOKEN:
                    REPLICATE_API_TOKEN = eline.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass

# Credenziali Facebook Pages
FB_PAGE_ID_ANTONIO = os.environ.get("FB_PAGE_ID_ANTONIO", os.environ.get("FB_PAGE_ID", "108297671444008"))
FB_PAGE_TOKEN_ANTONIO = os.environ.get("FB_PAGE_ACCESS_TOKEN_ANTONIO", os.environ.get("FB_PAGE_TOKEN", "EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia"))

FB_PAGE_ID_GIANCANI = os.environ.get("FB_PAGE_ID_GIANCANI", "234931856561526")
FB_PAGE_TOKEN_GIANCANI = os.environ.get("FB_PAGE_ACCESS_TOKEN_GIANCANI", os.environ.get("FB_PAGE_TOKEN_GIANCANI", "EAAZAH7q8wRZAEBSXRuqZAbRujVl9v0i7bXynRXtbb6sZAJMn0AZAbZAsJ0bLFHZAjWKhIpeu8R1xkKJDNgTcGawxoBo5FE7xONkTZAyRfOdKwSeydwoGkUHvPluWsB7biC8AZAqP9UWd672RlwmHzuwfAugUngnQnbZB2SZBCWj3WQqSKo8tLiBO4DYhI474ZAdhLwMs"))

FB_PAGE_ID_ETERNO = os.environ.get("FB_PAGE_ID_ETERNO", "")
FB_PAGE_TOKEN_ETERNO = os.environ.get("FB_PAGE_ACCESS_TOKEN_ETERNO", "")

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

# Stile Disney/Pixar Obbligatorio — Alta Definizione 3D Animazione
CARTOON_STYLE_PREFIX = "Pixar Disney 3D animation style, vibrant rich colors, expressive charming characters, cinematic lighting, detailed background, vertical 9:16"
MANDATORY_NEGATIVE_PROMPT = "--no photo, realistic, dark, gloomy, ugly, flat, blurry, low quality, sketch, watermark"


# ── REGOLA UTENTE GLOBALE: ESTRAZIONE RIGOROSA DA COLONNA F ─────────────────
def estrai_storia_colonna_f(csv_file=None, id_richiesto=None, mode="standard"):
    """
    Estrae una storia classica, biblica, mitologica o pillola immobiliare dal CSV.
    La narrazione testuale viene prelevata RIGOROSAMENTE dalla Colonna F.
    """
    if not csv_file:
        if mode == "bibbia":
            csv_file = CSV_BIBBIA_PATH
        elif mode == "mitologia":
            csv_file = CSV_MITOLOGIA_PATH
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
                col_f = row[5].strip() if len(row) > 5 and row[5].strip() not in ['pronto', 'pubblicato', 'bozza'] else row[3].strip()
                prompts = row[6].strip() if len(row) > 6 else (row[4].strip() if len(row) > 4 else "")
                stato = row[7].strip() if len(row) > 7 else (row[5].strip() if len(row) > 5 else "pronto")
                storie.append({
                    "id": row[0].strip(),
                    "titolo": row[1].strip(),
                    "autore": row[2].strip() if len(row) > 2 else "Sacra Scrittura",
                    "riferimento_biblico": row[2].strip() if len(row) > 2 else "",
                    "personaggi": row[1].strip(),
                    "ambientazione": row[3].strip() if len(row) > 3 else "Antico Testamento",
                    "morale": row[4].strip() if len(row) > 4 else "",
                    "anno": "Antico Testamento",
                    "genere": "Bibbia",
                    "categoria": "BIBBIA",
                    "testo_colonna_f": col_f,
                    "prompts_g": prompts,
                    "stato": stato
                })
            elif mode == "mitologia":
                col_f = row[5].strip() if len(row) > 5 else row[3].strip()
                storie.append({
                    "id": row[0].strip(),
                    "titolo": row[1].strip(),
                    "personaggi": row[2].strip() if len(row) > 2 else "",
                    "autore": row[2].strip() if len(row) > 2 else "Miti dell'Antica Grecia",
                    "ambientazione": row[3].strip() if len(row) > 3 else "Antica Grecia",
                    "morale": row[4].strip() if len(row) > 4 else "",
                    "anno": "Epoca Classica",
                    "genere": "Mitologia Greca",
                    "categoria": "MITOLOGIA",
                    "testo_colonna_f": col_f,
                    "prompts_g": row[6].strip() if len(row) > 6 else "",
                    "stato": row[7].strip() if len(row) > 7 else "pronto"
                })
            elif mode == "pillole":
                col_f = row[5].strip() if len(row) > 5 else row[3].strip()
                storie.append({
                    "id": row[0].strip(),
                    "titolo": row[2].strip() if len(row) > 2 else row[1].strip(),
                    "argomento": row[2].strip() if len(row) > 2 else "",
                    "normativa": row[3].strip() if len(row) > 3 else "",
                    "autore": "Antonio Giancani - Immobiliare Giancani",
                    "anno": "Normativa Vigente",
                    "genere": row[1].strip() if len(row) > 1 else "Diritto Immobiliare",
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
                        "genere": row[4].strip() if len(row) > 4 else "Grande Classico",
                        "categoria": "STANDARD",
                        "testo_colonna_f": row[5].strip(),
                        "prompts_g": row[6].strip() if len(row) > 6 else ""
                    })

    if not storie:
        raise ValueError(f"Nessuna storia valida trovata nel database CSV: {csv_file}")

    tracker_file = os.path.join(BASE_DIR, f"stato_rotazione_{mode}.json")

    if id_richiesto:
        trovate = [s for s in storie if str(s["id"]) == str(id_richiesto)]
        if trovate:
            storia = trovate[0]
        else:
            print(f"⚠️ ID {id_richiesto} non trovato, selezione progressiva...")
            storia = storie[0]
    else:
        # SELEZIONE PROGRESSIVA SEQUENZIALE
        ultimo_id = 0
        if os.path.exists(tracker_file):
            try:
                with open(tracker_file, "r", encoding="utf-8") as tf:
                    tdata = json.load(tf)
                    ultimo_id = int(tdata.get("ultimo_id", 0))
            except Exception:
                ultimo_id = 0

        candidati = [s for s in storie if int(s["id"]) > ultimo_id]
        if candidati:
            storia = candidati[0]
        else:
            print(f"🔄 Tutte le storie della serie completate! Riavvio ciclo progressivo dal primo episodio...")
            storia = storie[0]

        print(f"📈 [SELEZIONE PROGRESSIVA]: Selezionata Storia #{storia['id']}: «{storia['titolo']}» (Precedente completata: #{ultimo_id})")

    print("\n" + "="*70)
    print("📖 [ESTRAZIONE DATI] RIGOROSAMENTE DA COLONNA F")
    print(f"📌 [MODALITÀ {storia.get('categoria', mode).upper()} - ID {storia['id']}]: «{storia['titolo']}» ({storia['autore']})")
    print(f"💬 [TESTO COLONNA F / SCRIPT]:\n\"{storia['testo_colonna_f']}\"")
    print("="*70 + "\n")
    
    return storia


# ── PARSING DEL TESTO DELLA COLONNA F IN SCENE NARRATIVE ────────────────────
def crea_struttura_scene(storia, mode="standard"):
    """Divide la narrazione di Colonna F nelle scene verticali 9:16."""
    categoria = storia.get("categoria", mode).upper()
    
    # Scene JSON predefinite se presenti in prompts_g
    if storia.get("prompts_g") and storia["prompts_g"].startswith("["):
        try:
            raw_scenes = json.loads(storia["prompts_g"])
            scene = []
            for i, rs in enumerate(raw_scenes):
                t_scena = rs.get("voiceover_chunk") or rs.get("overlay_text") or ""
                scene.append({
                    "scena_id": rs.get("id", i),
                    "testo": t_scena,
                    "prompt": rs.get("prompt", ""),
                    "type": rs.get("type", "story"),
                    "duration": rs.get("duration", 4.5),
                    "is_outro": (i == len(raw_scenes) - 1)
                })
            return scene
        except Exception as e:
            print(f"⚠️ Errore parsing prompts_g JSON: {e}")

    # Parsing testuale automatico da Colonna F
    frasi = [f.strip() for f in re.split(r'(?<=[.!?])\s+', storia["testo_colonna_f"]) if f.strip()]
    if not frasi:
        frasi = [storia["testo_colonna_f"]]
        
    scene = []
    # Scena 1 (Hook / Intro)
    scene.append({
        "scena_id": 0,
        "testo": f"{storia['titolo'].upper()} in 2 minuti. {frasi[0]}",
        "prompt": f"{storia['titolo']}, scene 1 introduction",
        "type": "hook",
        "duration": 4.5,
        "is_outro": False
    })
    
    # Scene successive
    for idx, f in enumerate(frasi[1:], start=1):
        scene.append({
            "scena_id": idx,
            "testo": f,
            "prompt": f"{storia['titolo']}, action scene {idx}",
            "type": "story",
            "duration": 4.5,
            "is_outro": (idx == len(frasi) - 1)
        })
    return scene


# ── GENERATORE VOCE NARRATRICE GOOGLE GEMINI TTS ────────────────────────────
def genera_voce_gemini_tts(testo, file_audio, voice_name="Charon"):
    """Sintesi vocale neurale avanzata con le API di Google Gemini."""
    if not GEMINI_API_KEY:
        return False
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": testo}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            }
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            cands = data.get("candidates", [])
            if cands:
                parts = cands[0].get("content", {}).get("parts", [])
                for p in parts:
                    if "inlineData" in p and "data" in p["inlineData"]:
                        pcm_bytes = base64.b64decode(p["inlineData"]["data"])
                        raw_pcm = file_audio + ".raw.pcm"
                        with open(raw_pcm, "wb") as pf:
                            pf.write(pcm_bytes)
                        cmd = [
                            FFMPEG_EXE, "-y",
                            "-f", "s16le", "-ar", "24000", "-ac", "1",
                            "-i", raw_pcm,
                            "-c:a", "libmp3lame", "-b:a", "192k",
                            file_audio
                        ]
                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                        if os.path.exists(raw_pcm):
                            os.remove(raw_pcm)
                        print(f"  🎙️ [GEMINI NARRATORE AI] Voce umana generata con successo da Gemini ({voice_name})!")
                        return True
    except Exception as e_gem_tts:
        print(f"  ⚠️ Avviso Gemini TTS ({e_gem_tts}), passaggio a voce neurale Diego...")
    return False


# ── GENERAZIONE VOCE NARRANTE (GEMINI TTS + EDGE-TTS + GTTS FALLBACK) ───────
async def genera_voce_edge_tts(testo, file_audio, voce="it-IT-DiegoNeural"):
    """Sintesi vocale neurale con priorità a Gemini TTS (Charon) e fallback su Edge-TTS."""
    if "gemini" in str(voce).lower() or voce in ["Charon", "Fenrir", "Puck", "Aoede"] or "it-IT-DiegoNeural" in str(voce):
        gem_voice = "Charon" if "diego" in str(voce).lower() else (voce.replace("gemini-", "") if "gemini" in str(voce).lower() else voce)
        if genera_voce_gemini_tts(testo, file_audio, voice_name=gem_voice):
            return True

    success = False
    voce_edge = "it-IT-DiegoNeural" if "gemini" in str(voce).lower() else voce
    try:
        import edge_tts
        comm = edge_tts.Communicate(testo, voce_edge, rate="-2%", pitch="+0Hz")
        await asyncio.wait_for(comm.save(file_audio), timeout=15)
        if os.path.exists(file_audio) and os.path.getsize(file_audio) > 1000:
            success = True
    except Exception as e:
        print(f"  ⚠️ Edge-TTS avviso ({e}), attivo fallback gTTS...")

    if not success:
        try:
            from gtts import gTTS
            tts = gTTS(text=testo, lang='it', slow=False)
            tts.save(file_audio)
            print("  🔊 [gTTS Fallback] Voce generata con Google TTS")
            success = True
        except Exception as eg:
            print(f"  ⚠️ Fallback su tono sintetico: {eg}")
            cmd = [
                FFMPEG_EXE, "-y",
                "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                "-t", "4.5", "-q:a", "9", "-acodec", "libmp3lame",
                file_audio
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            success = True
    return success


# ── OTTIMIZZAZIONE DOWNLOAD IMMAGINI (ANTI-TIMEOUT POLLINATIONS - PUNTO 2) ──
def genera_prompt_compatto(raw_prompt):
    """
    Formatta il prompt in stile Disney/Pixar alta definizione (max 200 car. parte soggetto)
    anteponendo SEMPRE lo stile Disney/Pixar 3D e il negative prompt obbligatorio.
    - Stile: Pixar Disney 3D animation, vibrant colors, cinematic lighting
    - Negative: no photo, realistic, dark, ugly, flat, low quality
    """
    clean = re.sub(r"--no.*", "", raw_prompt, flags=re.IGNORECASE)
    clean = clean.replace(CARTOON_STYLE_PREFIX, "")
    clean = re.sub(r"Pixar Disney 3D animation style,?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"3D Pixar Disney animation style,?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"2D cartoon animation style,?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"classic animated movie cel art,?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"high quality 3D render,?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"vertical 9:16,?\s*", "", clean, flags=re.IGNORECASE)
    clean = clean.strip(" ,.")

    # Soggetto fino a 200 caratteri per massimizzare la qualità Disney
    max_subject_len = max(30, 200 - len(CARTOON_STYLE_PREFIX) - 2)
    subject = clean[:max_subject_len].rstrip(" ,.")
    positive_compact = f"{CARTOON_STYLE_PREFIX}, {subject}".strip(" ,.")

    return f"{positive_compact} {MANDATORY_NEGATIVE_PROMPT}"


def genera_immagine_together_flux(prompt, output_img):
    """
    Genera immagine in stile Disney/Pixar 3D con Together AI (FLUX.1-schnell o FLUX.1-schnell-Free).
    """
    if not TOGETHER_API_KEY:
        return False
    url = "https://api.together.xyz/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    clean_prompt = genera_prompt_compatto(prompt)
    models = ["black-forest-labs/FLUX.1-schnell-Free", "black-forest-labs/FLUX.1-schnell"]
    for m in models:
        payload = {
            "model": m,
            "prompt": clean_prompt,
            "width": 576,
            "height": 1024,
            "steps": 4,
            "n": 1,
            "response_format": "b64_json"
        }
        try:
            print(f"  ⚡ [TOGETHER AI] Tentativo FLUX [{m}]...", flush=True)
            r = requests.post(url, json=payload, headers=headers, timeout=28, verify=False)
            if r.status_code == 200:
                data = r.json()
                b64_img = data.get("data", [{}])[0].get("b64_json")
                if b64_img:
                    raw_bytes = base64.b64decode(b64_img)
                    with Image.open(io.BytesIO(raw_bytes)) as pil_img:
                        adatta_immagine_9_16(pil_img).save(output_img, "JPEG", quality=95)
                    print(f"  ✅ [TOGETHER FLUX] Immagine Disney generata con successo ({round(os.path.getsize(output_img)/1024, 1)} KB): {os.path.basename(output_img)}")
                    return True
            else:
                print(f"  ⚠️ Together AI HTTP {r.status_code}: {r.text[:140]}")
        except Exception as e:
            print(f"  ⚠️ Errore Together AI: {e}")
    return False


def genera_immagine_replicate_sdxl(prompt, output_img):
    """
    Genera immagine in stile Disney/Pixar 3D con Replicate (Stability AI SDXL).
    """
    if not REPLICATE_API_TOKEN:
        return False
    url = "https://api.replicate.com/v1/models/stability-ai/sdxl/predictions"
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }
    clean_prompt = genera_prompt_compatto(prompt)
    payload = {
        "input": {
            "prompt": clean_prompt,
            "negative_prompt": "ugly, low quality, dark, black background, deformed, blurry, realistic photo",
            "width": 768,
            "height": 1344,
            "num_inference_steps": 25
        }
    }
    try:
        print(f"  ⚡ [REPLICATE SDXL] Avvio predizione SDXL...", flush=True)
        r = requests.post(url, json=payload, headers=headers, timeout=50, verify=False)
        if r.status_code in (200, 201):
            pred = r.json()
            output_urls = pred.get("output")
            if not output_urls and pred.get("status") in ("starting", "processing"):
                get_url = pred.get("urls", {}).get("get")
                for _ in range(12):
                    time.sleep(3)
                    r_poll = requests.get(get_url, headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}"}, timeout=15, verify=False)
                    if r_poll.status_code == 200:
                        poll_data = r_poll.json()
                        if poll_data.get("status") == "succeeded":
                            output_urls = poll_data.get("output")
                            break
                        elif poll_data.get("status") == "failed":
                            break
            if output_urls:
                img_url = output_urls[0] if isinstance(output_urls, list) else output_urls
                r_img = requests.get(img_url, timeout=25, verify=False)
                if r_img.status_code == 200:
                    with Image.open(io.BytesIO(r_img.content)) as pil_img:
                        adatta_immagine_9_16(pil_img).save(output_img, "JPEG", quality=95)
                    print(f"  ✅ [REPLICATE SDXL] Immagine Disney generata con successo ({round(os.path.getsize(output_img)/1024, 1)} KB): {os.path.basename(output_img)}")
                    return True
        else:
            print(f"  ⚠️ Replicate HTTP {r.status_code}: {r.text[:140]}")
    except Exception as e:
        print(f"  ⚠️ Errore Replicate: {e}")
    return False



def scarica_immagine_pollinations(prompt, output_img, seed=100, use_cache=True, categoria="STANDARD", is_intro=False, idx=1, story_id="1"):
    """
    Gestisce la fornitura dell'immagine 9:16 con ottimizzazioni anti-timeout Pollinations:
    1. Priorità massima: Asset personalizzati o pre-renderizzati per continuità
    2. Cache locale valida
    3. Download Pollinations con prompt compatto (max 175 car.), negative prompt obbligatorio,
       motore 'turbo' o default (MAI 'flux'), timeout 16s, anti-cache &ts= e pausa di 3 secondi
    4. Fallback su Master Artwork corrispondente
    """
    cat_upper = str(categoria).upper()
    assets_dir = os.path.join(BASE_DIR, "assets")
    custom_dir = CUSTOM_IMG_DIR

    # 1. Controllo immagini personalizzate utente
    if os.path.exists(custom_dir):
        possible_custom = [
            f"scena_{idx}.jpg", f"scena_{idx}.png", f"scena_{idx}.jpeg",
            f"{idx}.jpg", f"{idx}.png",
            f"mitologia_{story_id}_scena_{idx}.jpg", f"bibbia_{story_id}_scena_{idx}.jpg"
        ]
        for custom_name in possible_custom:
            cpath = os.path.join(custom_dir, custom_name)
            if os.path.exists(cpath) and os.path.getsize(cpath) > 1000:
                try:
                    with Image.open(cpath) as cim:
                        adatta_immagine_9_16(cim).save(output_img, "JPEG", quality=95)
                    print(f"  📸 [IMMAGINE PERSONALIZZATA] Scena {idx} applicata da: {custom_name}")
                    return True
                except Exception as ec:
                    print(f"  ⚠️ Errore caricamento immagine personalizzata {custom_name}: {ec}")

    # 2. Asset pre-renderizzati Disney/Pixar — pool di varianti per massima varietà
    if "MITOLOGIA" in cat_upper or "BIBBIA" in cat_upper:
        prefix = "mitologia" if "MITOLOGIA" in cat_upper else "bibbia"
        cartoons_dir = os.path.join(assets_dir, f"{prefix}_scene_cartoons")
        
        # Cerca le varianti disponibili v1/v2/v3 (pool Disney/Pixar)
        varianti = []
        for v in [1, 2, 3]:
            vpath = os.path.join(cartoons_dir, f"{prefix}_{story_id}_scena_{idx}_v{v}.jpg")
            if os.path.exists(vpath) and os.path.getsize(vpath) > 10000:
                varianti.append(vpath)
        
        # Compatibilità retroattiva: cerca anche il file senza suffisso variante
        old_path = os.path.join(cartoons_dir, f"{prefix}_{story_id}_scena_{idx}.jpg")
        if not varianti and os.path.exists(old_path) and os.path.getsize(old_path) > 1000:
            varianti.append(old_path)
        
        if varianti:
            # Selezione casuale dalla pool → video sempre diverso ad ogni run!
            chosen = random.choice(varianti)
            try:
                with Image.open(chosen) as mim:
                    adatta_immagine_9_16(mim).save(output_img, "JPEG", quality=95)
                variante_label = os.path.basename(chosen)
                print(f"  🎨 [DISNEY ASSET {prefix.upper()}] Scena {idx} (variante casuale): {variante_label}")
                return True
            except Exception as em:
                print(f"  ⚠️ Avviso caricamento asset {os.path.basename(chosen)}: {em}")


    # 3. Verifica cache esistente valida
    if use_cache and os.path.exists(output_img) and os.path.getsize(output_img) > 10000:
        try:
            with Image.open(output_img) as test_img:
                test_img.verify()
            print(f"  ⚡ Immagine in cache verificata ({round(os.path.getsize(output_img)/1024, 1)} KB): {os.path.basename(output_img)}")
            return True
        except Exception:
            if os.path.exists(output_img):
                os.remove(output_img)

    # 4. Motore Primario A: Together AI (FLUX.1-schnell Disney/Pixar)
    if TOGETHER_API_KEY:
        if genera_immagine_together_flux(prompt, output_img):
            return True

    # 5. Motore Primario B: Replicate (Stability AI SDXL Disney/Pixar)
    if REPLICATE_API_TOKEN:
        if genera_immagine_replicate_sdxl(prompt, output_img):
            return True

    # 6. Motore Alternativo: Pollinations.ai (con stile Disney/Pixar)
    full_prompt = genera_prompt_compatto(prompt)
    encoded_prompt = urllib.parse.quote(full_prompt)

    # Motori ammessi: 'turbo' prima (migliore qualità Disney/Pixar), poi default
    models_to_try = ["turbo", None]
    max_retries = 2

    for attempt in range(1, max_retries + 1):
        model_choice = models_to_try[(attempt - 1) % len(models_to_try)]
        model_param = f"&model={model_choice}" if model_choice else ""
        
        # Parametro dinamico anti-cache &ts= con timestamp in ms e seed variabile per garantire varietà
        ts_val = int(time.time() * 1000)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=576&height=1024&nologo=true&seed={seed}{model_param}&ts={ts_val}"
        
        try:
            print(f"  🎨 Download Immagine Cartoon [Modello: {model_choice or 'default'}, Seed: {seed}] (Tentativo {attempt}/{max_retries}, Timeout: 16s)...", flush=True)
            # Timeout rigoroso a 16 secondi
            resp = requests.get(url, timeout=(4, 16), verify=False, headers={"User-Agent": "Mozilla/5.0"})
            
            if resp.status_code == 200 and len(resp.content) > 10000:
                temp_file = f"{output_img}.tmp"
                with open(temp_file, "wb") as f:
                    f.write(resp.content)
                
                try:
                    with Image.open(temp_file) as test_pil:
                        test_pil.verify()
                    with Image.open(temp_file) as valid_pil:
                        adatta_immagine_9_16(valid_pil).save(output_img, "JPEG", quality=95)
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    print(f"  ✅ Immagine scaricata e adattata 9:16 ({round(os.path.getsize(output_img)/1024, 1)} KB): {os.path.basename(output_img)}")
                    
                    # Pausa obbligatoria di 3 secondi tra i download andati a buon fine
                    print("  ⏳ Pausa di 3 secondi tra i download...", flush=True)
                    time.sleep(3)
                    return True
                except Exception as verify_err:
                    print(f"  ⚠️ Tentativo {attempt}: Immagine scaricata non valida ({verify_err})")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
            else:
                print(f"  ⚠️ Tentativo {attempt} fallito (Status HTTP {resp.status_code})")
        except Exception as conn_err:
            print(f"  ⚠️ Errore connessione tentativo {attempt} ({model_choice}): {conn_err}")

        if attempt < max_retries:
            time.sleep(2)

    # 5. Fallback su Master Artwork corrispondente
    print(f"  🎨 Applicazione Master Artwork di riserva per {cat_upper}...")
    crea_immagine_fallback(output_img, prompt, categoria=categoria, idx=idx, story_id=story_id)
    return True


def crea_immagine_fallback(output_img, testo_descrittivo, categoria="STANDARD", idx=1, story_id="1"):
    """Applica il master artwork di riserva mantenendo proporzioni perfette."""
    assets_dir = os.path.join(BASE_DIR, "assets")
    cat_upper = str(categoria).upper()
    
    if "BIBBIA" in cat_upper:
        master_art = os.path.join(assets_dir, "bibbia_master_fallback.jpg")
    elif "MITOLOGIA" in cat_upper:
        master_art = os.path.join(assets_dir, "mitologia_master_fallback.jpg")
    elif "PILLOLE" in cat_upper:
        master_art = os.path.join(assets_dir, "pillola_master_fallback.jpg")
    else:
        master_art = os.path.join(assets_dir, "cat_master_reference.jpg")
        
    if os.path.exists(master_art):
        try:
            with Image.open(master_art) as im:
                adatta_immagine_9_16(im).save(output_img, "JPEG", quality=95)
            print(f"  🖼️ Master Artwork [{os.path.basename(master_art)}] applicata con successo (9:16)!")
            return
        except Exception as e:
            print(f"  ⚠️ Errore caricamento master artwork: {e}")

    # Fallback: gradiente colorato vivace variabile per scena (no sfondo nero!)
    cat_upper_fb = str(categoria).upper()
    idx_int = int(idx) if str(idx).isdigit() else 1

    # Palette colori vibranti per categoria — stile Disney/Pixar
    if "MITOLOGIA" in cat_upper_fb:
        palettes = [
            [(25, 85, 160), (80, 160, 230), (200, 230, 255)],  # Blu Egeo
            [(140, 80, 20), (210, 150, 60), (255, 220, 140)],  # Oro antico
            [(60, 20, 110), (130, 60, 180), (220, 170, 255)],  # Viola olimpico
            [(20, 100, 60), (60, 170, 110), (170, 240, 200)],  # Verde bosco
            [(160, 30, 30), (220, 80, 50), (255, 200, 150)],   # Rosso fuoco
            [(20, 60, 120), (50, 130, 200), (180, 220, 255)],  # Azzurro mare
        ]
    elif "BIBBIA" in cat_upper_fb:
        palettes = [
            [(180, 130, 20), (230, 190, 80), (255, 245, 200)],  # Oro sacro
            [(30, 70, 140), (70, 130, 200), (200, 225, 255)],   # Blu cielo
            [(100, 40, 10), (170, 100, 40), (240, 200, 150)],   # Terra sacra
            [(20, 80, 50), (60, 150, 90), (180, 240, 200)],     # Verde palma
            [(120, 30, 30), (190, 80, 60), (255, 200, 170)],    # Porpora biblica
            [(60, 40, 100), (120, 90, 170), (220, 200, 255)],   # Viola mistico
        ]
    elif "PILLOLE" in cat_upper_fb:
        palettes = [
            [(20, 70, 130), (50, 130, 200), (180, 220, 255)],  # Blu professionale
            [(10, 90, 70), (30, 160, 120), (160, 230, 210)],   # Verde studio
            [(100, 50, 10), (180, 110, 40), (240, 200, 150)],  # Marmo caldo
            [(50, 20, 100), (110, 70, 170), (210, 190, 255)],  # Blu scuro elegante
            [(130, 30, 20), (200, 80, 50), (255, 200, 180)],   # Rosso ufficio
            [(20, 60, 90), (50, 120, 160), (180, 220, 250)],   # Grigio acciaio
        ]
    else:
        palettes = [
            [(40, 60, 100), (80, 120, 180), (200, 220, 255)],
            [(80, 40, 20), (150, 90, 50), (240, 200, 160)],
            [(20, 80, 60), (60, 150, 100), (180, 240, 210)],
            [(100, 30, 80), (170, 80, 150), (240, 200, 230)],
            [(40, 40, 40), (100, 100, 120), (200, 210, 220)],
            [(60, 80, 20), (120, 160, 50), (210, 240, 160)],
        ]

    palette = palettes[(idx_int - 1) % len(palettes)]
    c1, c2, c3 = palette

    # Gradiente verticale a 3 colori
    img = Image.new("RGB", (576, 1024))
    pixels = img.load()
    h = 1024
    for y in range(h):
        if y < h // 2:
            t = y / (h // 2)
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
        else:
            t = (y - h // 2) / (h // 2)
            r = int(c2[0] + (c3[0] - c2[0]) * t)
            g = int(c2[1] + (c3[1] - c2[1]) * t)
            b = int(c2[2] + (c3[2] - c2[2]) * t)
        for x in range(576):
            pixels[x, y] = (r, g, b)

    img.save(output_img, "JPEG", quality=95)
    print(f"  🌈 Sfondo gradiente colorato applicato (scena {idx}, palette {(idx_int-1)%len(palettes)+1})")


# ── OVERLAY GRAFICO: TITOLO INTRO & SOTTOTITOLI COMIC STICKER (PUNTO 3) ─────
def crea_overlay_grafico(testo, titolo_libro, autore, output_overlay, is_outro=False, categoria="STANDARD", idx=1, is_intro=False):
    """
    Crea un PNG trasparente 720x1280 contenente:
    1. Badge Titolo Superiore: renderizzato ESCLUSIVAMENTE sulla prima scena (is_intro and idx == 1).
       Nelle scene successive scompare completamente per lasciare piena visibilità all'illustrazione.
    2. Sottotitoli in stile Comic Sticker:
       - Doppio contorno spesso a 360° (stroke 6px nero)
       - Ombra profonda a sbalzo (offset +5, +5)
       - Font solare / giallo chiaro ad altissima leggibilità
       - Nessun box rettangolare di sfondo
    3. Outro badge finale con risalto massimo a Immobiliare Giancani.
    """
    img = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    fonts_dir = os.path.join(BASE_DIR, "assets", "fonts")
    cinzel_path = os.path.join(fonts_dir, "Cinzel-Bold.ttf")
    playfair_path = os.path.join(fonts_dir, "PlayfairDisplay-Bold.ttf")
    lora_path = os.path.join(fonts_dir, "Lora-Bold.ttf")

    def carica_font(path, fallback_list, size):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        for fb in fallback_list:
            try:
                return ImageFont.truetype(fb, size)
            except Exception:
                continue
        # Fallback avanzato per ambienti Linux / GitHub Actions
        linux_system_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        for lsf in linux_system_fonts:
            if os.path.exists(lsf):
                try:
                    return ImageFont.truetype(lsf, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    font_kicker = carica_font(cinzel_path, ["georgiab.ttf", "pala.ttf", "arialbd.ttf"], 21)
    font_hero_title = carica_font(cinzel_path, ["georgiab.ttf", "palab.ttf", "arialbd.ttf"], 33)
    font_titolo = carica_font(playfair_path, ["georgiab.ttf", "palab.ttf", "arialbd.ttf"], 28)
    font_autore = carica_font(lora_path, ["georgia.ttf", "palai.ttf", "arial.ttf"], 22)
    font_brand = carica_font(cinzel_path, ["georgiab.ttf", "palab.ttf", "arialbd.ttf"], 30)
    font_submotto = carica_font(lora_path, ["georgia.ttf", "pala.ttf", "arial.ttf"], 18)

    cat_upper = str(categoria).upper()

    # 1. BADGE TITOLO SUPERIORE: ESCLUSIVAMENTE SULLA PRIMA SCENA (is_intro and idx == 1)
    if is_intro and idx == 1:
        if "MITOLOGIA" in cat_upper:
            # Stile Ellenico Mitologia Greca (Ore 18:00)
            draw.rounded_rectangle([32, 45, 688, 205], radius=20, fill=(11, 27, 61, 240), outline=(212, 175, 55, 250), width=3)
            draw.rounded_rectangle([38, 51, 682, 199], radius=16, outline=(243, 229, 171, 140), width=1)
            draw.text((360, 75), "🏛️ — STORIE DELLA MITOLOGIA GRECA — 🏛️", fill=(245, 215, 110), font=font_kicker, anchor="mm")
            draw.text((361, 126), titolo_libro.upper(), fill=(0, 0, 0, 240), font=font_hero_title, anchor="mm")
            draw.text((360, 125), titolo_libro.upper(), fill=(255, 255, 255), font=font_hero_title, anchor="mm")
            draw.text((360, 175), "⚡ Eroi e Leggende dell'Olimpo in 2 Minuti ⚡", fill=(215, 230, 255), font=font_autore, anchor="mm")
        elif "BIBBIA" in cat_upper:
            draw.rounded_rectangle([40, 40, 680, 155], radius=16, fill=(18, 24, 38, 225), outline=(212, 175, 55, 230), width=2)
            draw.rounded_rectangle([46, 46, 674, 149], radius=12, outline=(212, 175, 55, 100), width=1)
            draw.text((360, 65), "— STORIE DELLA BIBBIA —", fill=(234, 198, 108), font=font_kicker, anchor="mm")
            draw.text((360, 98), titolo_libro.upper(), fill=(255, 252, 245), font=font_titolo, anchor="mm")
            draw.text((360, 132), f"di {autore}", fill=(210, 225, 245), font=font_autore, anchor="mm")
        elif "PILLOLE" in cat_upper:
            draw.rounded_rectangle([40, 40, 680, 155], radius=16, fill=(14, 24, 40, 230), outline=(212, 175, 55, 230), width=2)
            draw.rounded_rectangle([46, 46, 674, 149], radius=12, outline=(212, 175, 55, 100), width=1)
            draw.text((360, 65), "— PILLOLE IMMOBILIARI & LEGALI —", fill=(234, 198, 108), font=font_kicker, anchor="mm")
            draw.text((360, 98), titolo_libro.upper(), fill=(255, 252, 245), font=font_titolo, anchor="mm")
            draw.text((360, 132), f"a cura di {autore}", fill=(210, 225, 245), font=font_autore, anchor="mm")
        else:
            draw.rounded_rectangle([40, 40, 680, 155], radius=16, fill=(18, 24, 38, 225), outline=(212, 175, 55, 230), width=2)
            draw.rounded_rectangle([46, 46, 674, 149], radius=12, outline=(212, 175, 55, 100), width=1)
            draw.text((360, 65), "— I GRANDI CLASSICI IN 2 MINUTI —", fill=(234, 198, 108), font=font_kicker, anchor="mm")
            draw.text((360, 98), titolo_libro.upper(), fill=(255, 252, 245), font=font_titolo, anchor="mm")
            draw.text((360, 132), f"di {autore}", fill=(210, 225, 245), font=font_autore, anchor="mm")
    # DOPO LA PRIMA SCENA (idx > 1): IL TITOLO SCOMPARE PER LASCIARE PIENA VISIBILITÀ ALL'ILLUSTRAZIONE

    # 2. SOTTOTITOLI IN STILE COMIC STICKER (Doppio contorno 360°, ombra profonda a sbalzo, font solare)
    import textwrap
    font_comic = carica_font(cinzel_path, ["impact.ttf", "arialbd.ttf", "arial.ttf"], 35)
    wrapped_lines = textwrap.wrap(testo, width=32)
    line_height = 46
    total_h = len(wrapped_lines) * line_height
    start_y = (1040 if not is_outro else 970) - (total_h // 2)

    colore_font_solare = (255, 245, 95)  # Giallo chiaro solare brillante
    colore_bianco_puro = (255, 255, 255)

    for l_idx, line in enumerate(wrapped_lines):
        y_pos = start_y + (l_idx * line_height)
        testo_color = colore_font_solare if (l_idx == 0 or len(wrapped_lines) == 1) else colore_bianco_puro

        # a) Ombra profonda a sbalzo (+5, +5)
        draw.text((360 + 5, y_pos + 5), line, fill=(0, 0, 0, 255), font=font_comic, anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0, 255))
        # b) Doppio contorno spesso a 360° (stroke 6px)
        draw.text((360, y_pos), line, fill=(0, 0, 0, 255), font=font_comic, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, 255))
        # c) Testo frontale solare con rifinitura interna
        draw.text((360, y_pos), line, fill=testo_color, font=font_comic, anchor="mm", stroke_width=2, stroke_fill=(20, 20, 20, 255))

    # 3. OUTRO BADGE (y tra 1115 e 1245 px): Personal Branding Immobiliare Giancani
    if is_outro:
        outro_bg = (11, 27, 61, 240) if "MITOLOGIA" in cat_upper else (16, 22, 36, 235)
        draw.rounded_rectangle([35, 1115, 685, 1245], radius=18, fill=outro_bg, outline=(234, 198, 108, 245), width=2)
        draw.rounded_rectangle([41, 1121, 679, 1239], radius=14, outline=(212, 175, 55, 110), width=1)

        if "MITOLOGIA" in cat_upper:
            draw.text((360, 1145), "🏛️ RUBRICA MITI E CULTURA CLASSICA 🏛️", fill=(245, 215, 110), font=font_submotto, anchor="mm")
            draw.text((360, 1180), "IMMOBILIARE GIANCANI", fill=(255, 255, 255), font=font_brand, anchor="mm")
            draw.text((360, 1215), "⚡ Grandi Miti in 2 Minuti | Valori che Superano il Tempo ⚡", fill=(215, 230, 255), font=font_submotto, anchor="mm")
        elif "BIBBIA" in cat_upper:
            draw.text((360, 1145), "📖 RUBRICA SPIRITUALE E SAPIENZIALE 📖", fill=(234, 198, 108), font=font_submotto, anchor="mm")
            draw.text((360, 1180), "IMMOBILIARE GIANCANI", fill=(255, 255, 255), font=font_brand, anchor="mm")
            draw.text((360, 1215), "«Eterno Nostra Giustizia» • Parola di Vita e Speranza", fill=(210, 225, 245), font=font_submotto, anchor="mm")
        elif "PILLOLE" in cat_upper:
            draw.text((360, 1145), "🏢 LA TUA GUIDA IMMOBILIARE & LEGALE 🏢", fill=(234, 198, 108), font=font_submotto, anchor="mm")
            draw.text((360, 1180), "IMMOBILIARE GIANCANI", fill=(255, 255, 255), font=font_brand, anchor="mm")
            draw.text((360, 1215), "Compravendite Sicure e Consulenza Esperta a Favara & Agrigento", fill=(210, 225, 245), font=font_submotto, anchor="mm")
        else:
            draw.text((360, 1145), "📚 I GRANDI CLASSICI DELLA LETTERATURA 📚", fill=(234, 198, 108), font=font_submotto, anchor="mm")
            draw.text((360, 1180), "IMMOBILIARE GIANCANI", fill=(255, 255, 255), font=font_brand, anchor="mm")
            draw.text((360, 1215), "Coltiviamo la Cultura e l'Amore per le Belle Storie", fill=(210, 225, 245), font=font_submotto, anchor="mm")

    img.save(output_overlay, "PNG")


# ── MONTAGGIO VIDEO: KEN BURNS & CONCATENAZIONE CLIP ────────────────────────
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


def crea_clip_ken_burns(img_path, audio_path, overlay_path, output_clip, idx):
    """Genera una clip video 9:16 con effetto Ken Burns cinematografico dinamico."""
    durata = ottieni_durata_audio(audio_path) + 0.35
    total_frames = max(30, int(durata * 25))
    
    # Movimenti camera alternati
    if idx % 3 == 1:
        z_expr = f"min(zoom+0.00065,1.14)"
        x_expr = f"(iw-iw/zoom)/2"
        y_expr = f"(ih-ih/zoom)/2"
    elif idx % 3 == 2:
        z_expr = f"max(1.14-0.00065*on,1.0)"
        x_expr = f"(iw-iw/zoom)/2"
        y_expr = f"(ih-ih/zoom)/2"
    else:
        z_expr = "1.06"
        x_expr = f"(iw-iw/zoom)*(sin(on/{total_frames}*3.1415)/2+0.5)"
        y_expr = f"(ih-ih/zoom)/2"

    vf = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s=720x1280:fps=25[kb];"
        f"[kb][1:v]overlay=0:0[v]"
    )
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", img_path,
        "-i", overlay_path,
        "-i", audio_path,
        "-filter_complex", vf,
        "-map", "[v]",
        "-map", "2:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(round(durata, 2)),
        output_clip
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def monta_video_finale(clips, output_video, durata_totale):
    """Concatena tutte le scene e mixa la musica di sottofondo d'atmosfera."""
    list_file = os.path.join(OUTPUT_DIR, "clips_concat.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c.replace(os.sep, '/')}'\n")
            
    temp_concat = os.path.join(OUTPUT_DIR, "temp_concat_video.mp4")
    cmd_concat = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        temp_concat
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # Selezione traccia musicale
    music_files = [os.path.join(MUSIC_DIR, f) for f in os.listdir(MUSIC_DIR) if f.endswith((".mp3", ".wav"))] if os.path.exists(MUSIC_DIR) else []
    
    if music_files:
        chosen_music = random.choice(music_files)
        print(f"  🎵 Musica di sottofondo: {os.path.basename(chosen_music)}")
        cmd_mix = [
            FFMPEG_EXE, "-y",
            "-i", temp_concat,
            "-stream_loop", "-1", "-i", chosen_music,
            "-filter_complex",
            f"[1:a]volume=0.11,afade=t=out:st={max(1, durata_totale-2)}:d=2[bg];[0:a][bg]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            output_video
        ]
        subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    else:
        shutil.copy(temp_concat, output_video)
        
    for tmp in [list_file, temp_concat]:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


# ── FORMATTAZIONE DIDASCALIA SOCIAL PER IL PERSONAL BRANDING ────────────────
def formatta_caption_social(storia):
    """
    Formatta la didascalia rispettando RIGOROSAMENTE Colonna F e il brand Immobiliare Giancani.
    Genera testi ricchi, accattivanti e specificamente inerenti alla trama e ai personaggi del video.
    """
    testo_col_f = storia.get('testo_colonna_f', '').replace('|||', '\n\n').strip()
    cat = storia.get("categoria", "STANDARD").upper()
    titolo = storia.get("titolo", "Racconto Epico")
    personaggi = storia.get("personaggi", "")
    ambientazione = storia.get("ambientazione", "")
    morale = storia.get("morale", "")
    normativa = storia.get("normativa", "")

    if cat == "MITOLOGIA":
        header = f"🏛️ {titolo.upper()} — STORIE DELLA MITOLOGIA GRECA (IN 2 MINUTI) 🏛️"
        sub_info = "📜 Rubrica Culturale Miti dell'Antica Grecia\n⏱️ Riassunto Narrativo Verticale 9:16\n🎨 Stile: Cartoon Animation Cel Art"
        extra_meta = []
        if personaggi:
            extra_meta.append(f"👥 Protagonisti: {personaggi}")
        if ambientazione:
            extra_meta.append(f"📍 Luogo: {ambientazione}")
        if morale:
            extra_meta.append(f"💡 Morale & Insegnamento: {morale}")
        meta_blocco = "\n".join(extra_meta) + "\n\n" if extra_meta else ""
        cta = "💬 Qual è il mito greco che ti affascina di più? Condividi la tua opinione nei commenti e iscriviti per non perdere i prossimi episodi ogni giorno alle 18:00!"
        tags = "#MitologiaGreca #MitiGreci #Olimpo #CulturaClassica #Reels #Shorts #AntonioGiancani #ImmobiliareGiancani"

    elif cat == "BIBBIA":
        header = f"📖 {titolo.upper()} — STORIE DELLA BIBBIA («ETERNO NOSTRA GIUSTIZIA») 📖"
        rif = storia.get("riferimento_biblico", storia.get("autore", "Antico Testamento"))
        sub_info = f"📜 Riferimento: {rif}\n⏱️ Riassunto Narrativo in 2 Minuti\n🎨 Stile: Cartoon Cel Art Animato 2D"
        extra_meta = []
        if ambientazione:
            extra_meta.append(f"📍 Ambientazione: {ambientazione}")
        if morale:
            extra_meta.append(f"💡 Insegnamento di Fede: {morale}")
        meta_blocco = "\n".join(extra_meta) + "\n\n" if extra_meta else ""
        cta = "🙏 Ti è piaciuta questa meditazione? Condividi questo messaggio di fede e speranza con chi ami e seguici ogni sera alle ore 20:00."
        tags = "#StorieBibliche #Bibbia #EternoNostraGiustizia #Fede #ParolaDiDio #Reels #Shorts #AntonioGiancani #ImmobiliareGiancani"

    elif cat == "PILLOLE":
        header = f"🏢 {titolo.upper()} — PILLOLE IMMOBILIARI & LEGALI QUOTIDIANE 🏢"
        sub_info = f"⚖️ Normativa: {normativa if normativa else 'Codice Civile e Normativa Vigente'}\n⏱️ Guida Pratica Rapida in 2 Minuti\n👤 A cura di Antonio Giancani"
        meta_blocco = ""
        cta = "💬 Hai dubbi o domande su compravendite, normative o mutui? Scrivici nei commenti o in privato per una consulenza su misura per il tuo immobile!"
        tags = "#Immobiliare #DirittoImmobiliare #Normativa #ConsulenzaLegale #Casa #Favara #Agrigento #Reels #Shorts #ImmobiliareGiancani"

    else:
        autore = storia.get('autore', '')
        anno = storia.get('anno', '')
        header = f"📚 {titolo.upper()} — I GRANDI CLASSICI DELLA LETTERATURA 📚"
        sub_info = f"📖 Opera di {autore} ({anno})\n⏱️ Riassunto Narrativo in 2 Minuti\n🎨 Stile: Antique Storybook Illustration"
        meta_blocco = ""
        cta = "📖 Hai mai letto questo capolavoro? Scrivi il tuo passaggio o libro preferito nei commenti!"
        tags = "#GrandiClassici #Letteratura #Cultura #Libri #Reels #Shorts #AntonioGiancani #ImmobiliareGiancani"

    caption = (
        f"{header}\n\n"
        f"{sub_info}\n\n"
        f"{meta_blocco}"
        f"💬 Narrazione Ufficiale (Colonna F):\n"
        f"«{testo_col_f}»\n\n"
        f"{cta}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 Produzione, Consulenza & Personal Branding:\n"
        f"⭐ IMMOBILIARE GIANCANI ⭐\n"
        f"📍 Sede: Favara & Agrigento | Consulenza e Vendita Immobiliari di Prestigio\n"
        f"🌐 Sito Web: https://immobiliaregiancani.it\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{tags}\n\n"
        f"🌟 Contenuto a cura di IMMOBILIARE GIANCANI"
    )
    return caption


def formatta_caption_telegram(storia):
    """Formatta la didascalia specifica per Telegram con tag HTML e limite caratteri a norma."""
    testo_col_f = storia.get('testo_colonna_f', '').replace('|||', ' ').strip()
    estratto = testo_col_f[:500] + "..." if len(testo_col_f) > 500 else testo_col_f
    cat = storia.get("categoria", "STANDARD").upper()
    titolo = storia.get("titolo", "Racconto Epico")

    if cat == "MITOLOGIA":
        icona = "🏛️"
        sub = "Miti dell'Antica Grecia (Ore 18:00)"
        tags = "#MitologiaGreca #Olimpo #Cultura #ImmobiliareGiancani"
    elif cat == "BIBBIA":
        icona = "📖"
        sub = "Storie della Bibbia (Ore 20:00)"
        tags = "#Bibbia #Fede #EternoNostraGiustizia #ImmobiliareGiancani"
    elif cat == "PILLOLE":
        icona = "🏢"
        sub = "Pillole Immobiliari & Legali (Ore 06:00)"
        tags = "#Immobiliare #Casa #Favara #Agrigento #ImmobiliareGiancani"
    else:
        icona = "📚"
        sub = "I Grandi Classici della Letteratura"
        tags = "#GrandiClassici #Libri #Cultura #ImmobiliareGiancani"

    caption = (
        f"{icona} <b>{titolo.upper()}</b>\n"
        f"<i>{sub}</i>\n\n"
        f"💬 <b>Narrazione (Colonna F):</b>\n"
        f"«{estratto}»\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ <b>IMMOBILIARE GIANCANI</b> ⭐\n"
        f"📍 Favara & Agrigento | https://immobiliaregiancani.it\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{tags}\n\n"
        f"🌟 Contenuto a cura di <b>IMMOBILIARE GIANCANI</b>"
    )
    return caption


# ── INVIO TELEGRAM BOT E CANALE ─────────────────────────────────────────────
def invia_su_telegram(video_path, storia):
    """Invia il video verticale su Telegram (Chat e Canale @immobiliaregiancani)."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Token Telegram o Chat ID mancanti. Salto invio.")
        return False
        
    print("\n📲 [TELEGRAM] Invio video su Chat e Canale...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    caption = formatta_caption_telegram(storia)
    
    inline_keyboard = {
        "inline_keyboard": [
            [{"text": "✨ Sito Web Immobiliare Giancani", "url": "https://immobiliaregiancani.it"}]
        ]
    }
    
    destinazioni = [TELEGRAM_CHAT_ID]
    if TELEGRAM_CHANNEL_ID and TELEGRAM_CHANNEL_ID not in destinazioni:
        destinazioni.append(TELEGRAM_CHANNEL_ID)
        
    almeno_uno_inviato = False
    for chat_target in destinazioni:
        try:
            with open(video_path, "rb") as vf:
                files = {"video": (os.path.basename(video_path), vf, "video/mp4")}
                data = {
                    "chat_id": chat_target,
                    "caption": caption[:1024],
                    "parse_mode": "HTML",
                    "supports_streaming": True,
                    "reply_markup": json.dumps(inline_keyboard)
                }
                resp = requests.post(url, data=data, files=files, verify=False, timeout=90)
                rdata = resp.json()
                if rdata.get("ok"):
                    print(f"  ✅ Video inviato con successo a {chat_target}!")
                    almeno_uno_inviato = True
                else:
                    print(f"  ⚠️ Errore invio a {chat_target}: {rdata.get('description')}")
        except Exception as e:
            print(f"  ❌ Errore connessione Telegram verso {chat_target}: {e}")

    return almeno_uno_inviato


def pubblica_reel_su_pagina_facebook(page_id, page_token, video_path, storia, nome_pagina="Facebook"):
    """Pubblica un Reel su una specifica pagina Facebook con descrizione ottimizzata da Colonna F."""
    if not page_id or not page_token:
        print(f"  ⚠️ Credenziali mancanti per Pagina Facebook '{nome_pagina}'. Salto.")
        return False

    # 🛡️ BLOCCO MANDATORIO BRAND: sulla Pagina Immobiliare Giancani sono ammessi SOLO contenuti immobiliari!
    if str(page_id).strip() == str(FB_PAGE_ID_GIANCANI).strip():
        cat = (storia.get('categoria') or storia.get('genere') or '').upper()
        if "PILLOLE" not in cat and "IMMOBIL" not in cat:
            print(f"  🛑 [BLOCCO SICUREZZA BRAND] Rifiutata pubblicazione di '{cat}' sulla Pagina Immobiliare Giancani: la pagina è riservata esclusivamente ai contenuti immobiliari! — Immobiliare Giancani")
            return False
        
    print(f"\n🎥 [FACEBOOK REEL] Pubblicazione sulla pagina '{nome_pagina}' (ID: {page_id})...")
    url_reels = f"https://graph.facebook.com/v19.0/{page_id}/video_reels"
    
    try:
        # Start Phase
        r1 = requests.post(url_reels, data={"upload_phase": "start", "access_token": page_token}, verify=False, timeout=25)
        res1 = r1.json()
        vid = res1.get("video_id")
        up_url = res1.get("upload_url")
        if not vid or not up_url:
            print(f"  ❌ Errore avvio Reel su {nome_pagina}: {res1}")
            return False
            
        # Upload Phase
        file_size = os.path.getsize(video_path)
        headers = {
            "Authorization": f"OAuth {page_token}",
            "offset": "0",
            "file_size": str(file_size),
            "Content-Type": "application/octet-stream"
        }
        with open(video_path, "rb") as vf:
            video_bytes = vf.read()
            
        print(f"  📤 Caricamento Reel ({round(file_size/(1024*1024), 2)} MB) su {nome_pagina}...")
        r2 = requests.post(up_url, data=video_bytes, headers=headers, verify=False, timeout=180)
        if r2.status_code != 200:
            print(f"  ❌ Errore upload binary Reel su {nome_pagina}: {r2.text}")
            return False
            
        # Finish Phase
        caption = formatta_caption_social(storia)
        r3 = requests.post(url_reels, data={
            "upload_phase": "finish",
            "access_token": page_token,
            "video_id": vid,
            "video_state": "PUBLISHED",
            "description": caption
        }, verify=False, timeout=35)
        res3 = r3.json()
        if res3.get("success"):
            print(f"  ✅ [FACEBOOK REEL] Pubblicato con successo su '{nome_pagina}'! (Post ID: {res3.get('post_id', vid)})")
            return True
        else:
            print(f"  ⚠️ Risposta Finish Reel su {nome_pagina}: {res3}")
            return False
    except Exception as e:
        print(f"  ❌ Errore pubblicazione Reel su {nome_pagina}: {e}")
        return False


# ── PUBBLICAZIONE STORIA FACEBOOK (META GRAPH API VIDEO_STORIES) ────────────
def pubblica_storia_facebook(page_id, page_token, video_path, nome_pagina="Facebook"):
    """
    Carica un video come Storia di Facebook via Meta Graph API v19.0 /video_stories.
    Ideale per card video da 10-60 secondi con audio, grafica e musica.
    """
    if not page_id or not page_token:
        print(f"  ⚠️ Credenziali mancanti per Storia Facebook '{nome_pagina}'. Salto.")
        return False
    if not os.path.exists(video_path):
        print(f"  ⚠️ Video storia non trovato: {video_path}")
        return False

    file_size = os.path.getsize(video_path)
    url_stories = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"

    try:
        # Phase 1: Start
        r1 = requests.post(url_stories, data={"upload_phase": "start", "access_token": page_token}, verify=False, timeout=25)
        res1 = r1.json()
        vid = res1.get("video_id")
        up_url = res1.get("upload_url")
        if not vid or not up_url:
            print(f"  ⚠️ Errore start Storia Facebook su {nome_pagina}: {res1}")
            return False

        # Phase 2: Binary Upload
        headers = {
            "Authorization": f"OAuth {page_token}",
            "offset": "0",
            "file_size": str(file_size),
            "Content-Type": "application/octet-stream"
        }
        with open(video_path, "rb") as vf:
            v_bytes = vf.read()

        r2 = requests.post(up_url, data=v_bytes, headers=headers, verify=False, timeout=120)
        if r2.status_code != 200:
            print(f"  ⚠️ Errore upload binary Storia su {nome_pagina}: {r2.text}")
            return False

        # Phase 3: Finish
        r3 = requests.post(url_stories, data={
            "upload_phase": "finish",
            "access_token": page_token,
            "video_id": vid,
            "video_state": "PUBLISHED"
        }, verify=False, timeout=30)
        res3 = r3.json()
        if res3.get("success", True):
            print(f"  ✅ [FACEBOOK STORIA] Pubblicata con successo su '{nome_pagina}'! (Story Video ID: {vid})")
            return True
        else:
            print(f"  ⚠️ Risposta Finish Storia su {nome_pagina}: {res3}")
            return False
    except Exception as e:
        print(f"  ⚠️ Eccezione pubblicazione Storia Facebook su {nome_pagina}: {e}")
        return False


def dividi_e_pubblica_storie_facebook(video_path, clips, storia, page_id, page_token, nome_pagina="Facebook"):
    """
    Pubblica la storia su Facebook Stories:
    1. Se presenti le clip delle scene, pubblica la prima clip (hook introduttivo da ~10-15s, perfetto per Stories)
       e le clip narrative principali sequenziali.
    2. Se il video finale è sotto i 60s, carica il video completo come Storia.
    """
    if not page_id or not page_token:
        return False

    # 🛡️ BLOCCO MANDATORIO BRAND: sulla Pagina Immobiliare Giancani sono ammessi SOLO contenuti immobiliari!
    if str(page_id).strip() == str(FB_PAGE_ID_GIANCANI).strip():
        cat = (storia.get('categoria') or storia.get('genere') or '').upper()
        if "PILLOLE" not in cat and "IMMOBIL" not in cat:
            print(f"  🛑 [BLOCCO SICUREZZA BRAND] Rifiutate Storie di '{cat}' sulla Pagina Immobiliare Giancani: la pagina è riservata esclusivamente ai contenuti immobiliari! — Immobiliare Giancani")
            return False

    print(f"\n📱 [FACEBOOK STORIE] Pubblicazione sequenziale su '{nome_pagina}' (ID: {page_id})...")
    pubblicata = False

    # 1. Pubblica la prima clip/hook (card introduttiva della storia con titolo)
    if clips and len(clips) > 0 and os.path.exists(clips[0]):
        clip_intro = clips[0]
        print(f"  📤 Invio Card 1 (Intro Hook) come Storia Facebook...")
        if pubblica_storia_facebook(page_id, page_token, clip_intro, nome_pagina):
            pubblicata = True

        # Se abbiamo almeno 3 clip, pubblichiamo anche la scena centrale e l'outro come card sequenziali
        if len(clips) >= 3 and os.path.exists(clips[-1]):
            time.sleep(2)
            print(f"  📤 Invio Card 2 (Climax & Morale) come Storia Facebook...")
            if pubblica_storia_facebook(page_id, page_token, clips[-1], nome_pagina):
                pubblicata = True

    # 2. Se non avevamo clips o come fallback, proviamo con il video principale
    if not pubblicata and os.path.exists(video_path):
        dur = ottieni_durata_audio(video_path) if os.path.exists(video_path) else 0
        if dur <= 65:
            print(f"  📤 Invio video completo ({round(dur, 1)}s) come Storia Facebook...")
            pubblicata = pubblica_storia_facebook(page_id, page_token, video_path, nome_pagina)

    return pubblicata


# ── PUBBLICAZIONE POST TESTUALE FACEBOOK (COLONNA F) ────────────────────────
def pubblica_post_testuale_facebook(page_id, page_token, storia, nome_pagina="Facebook"):
    """Pubblica un post testuale con testo estratto rigorosamente da Colonna F."""
    if not page_id or not page_token:
        return False
        
    print(f"\n📝 [FACEBOOK POST TESTUALE] Pubblicazione su '{nome_pagina}'...")
    url_feed = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    testo_col_f = storia.get('testo_colonna_f', '').replace('|||', '\n\n').strip()
    
    messaggio = (
        f"🏢 {storia.get('titolo', 'GUIDA PRATICA').upper()}\n"
        f"📜 Guida e Tutela Legale Quotidiana a cura di Antonio Giancani\n\n"
        f"{testo_col_f}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ IMMOBILIARE GIANCANI ⭐\n"
        f"📍 Favara & Agrigento | Consulenza e Vendita Immobiliari di Prestigio\n"
        f"🌐 https://immobiliaregiancani.it\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"#ImmobiliareGiancani #AntonioGiancani #Favara #Agrigento #Casa #ConsulenzaImmobiliare\n\n"
        f"🌟 Contenuto a cura di IMMOBILIARE GIANCANI"
    )
    try:
        r = requests.post(url_feed, data={"message": messaggio, "access_token": page_token}, verify=False, timeout=25)
        res = r.json()
        if res.get("id"):
            print(f"  ✅ [POST TESTUALE] Pubblicato con successo su '{nome_pagina}'! (ID: {res.get('id')})")
            return True
        else:
            print(f"  ⚠️ Errore post testuale su {nome_pagina}: {res}")
            return False
    except Exception as e:
        print(f"  ❌ Errore post testuale su {nome_pagina}: {e}")
        return False


# ── PUBBLICAZIONE SULLA PAGINA DI ANTONIO GIANCANI ─────────────────────────
def pubblica_reel_facebook(video_path, storia):
    """Wrapper per pubblicazione Reel sulla pagina personale di Antonio Giancani."""
    return pubblica_reel_su_pagina_facebook(
        FB_PAGE_ID_ANTONIO,
        FB_PAGE_TOKEN_ANTONIO,
        video_path,
        storia,
        nome_pagina="Antonio Giancani"
    )


# ── DISPATCHER SOCIAL: ESEGUI ROUTING PUBBLICAZIONE (PUNTO 4) ───────────────
def esegui_routing_pubblicazione(video_path, clips, storia, mode="standard", solo_telegram=False):
    """
    Dispatcher centralizzato di pubblicazione multicanale:
    - TUTTI i contenuti -> Telegram (Chat e Canale @immobiliaregiancani)
    - BIBBIA (Ore 20:00) -> FB Reel & Storie 'Antonio Giancani', FB 'Eterno nostra giustizia', YT Shorts 'Eterno nostra giustizia'
    - MITOLOGIA (Ore 18:00) -> FB Reel & Storie 'Antonio Giancani' (+ 'Immobiliare Giancani'), YT Shorts 'Storie della Mitologia Greca'
    - PILLOLE (Ore 06:00) -> FB Reel & Storie & Post Colonna F 'Immobiliare Giancani', FB Reel & Storie 'Antonio Giancani', YT Shorts 'Immobiliare Giancani'
    - LIBRI (Grandi Classici) -> FB Reel & Storie 'Antonio Giancani' (+ 'Immobiliare Giancani'), YT Shorts 'Immobiliare Giancani'
    Tutti i post includono descrizioni ricche, contestuali e terminate con IMMOBILIARE GIANCANI.
    """
    mode_lower = mode.lower()
    print("\n" + "="*75)
    print(f"📡 [ROUTING SOCIAL & PUBBLICAZIONE MULTICANALE] Categoria: {mode.upper()}")
    print("⭐ Supervisione Strategica e Personal Branding: IMMOBILIARE GIANCANI ⭐")
    print("="*75)

    # 1. Telegram (TUTTI i contenuti obbligatoriamente su Chat e Canale Broadcast)
    invia_su_telegram(video_path, storia)

    if solo_telegram:
        print("\n🔒 [MODALITÀ ESCLUSIVA TELEGRAM] Invio completato unicamente su Telegram come richiesto.")
        print("⭐ Produzione e Personal Branding: IMMOBILIARE GIANCANI ⭐\n")
        return

    # 2. Routing multicanale in base al tema
    if "bibbia" in mode_lower:
        # a) Pagina Facebook "Eterno nostra giustizia" (Reel + Storie se configurato)
        if FB_PAGE_ID_ETERNO and FB_PAGE_TOKEN_ETERNO:
            pubblica_reel_su_pagina_facebook(FB_PAGE_ID_ETERNO, FB_PAGE_TOKEN_ETERNO, video_path, storia, "Eterno nostra giustizia")
            dividi_e_pubblica_storie_facebook(video_path, clips, storia, FB_PAGE_ID_ETERNO, FB_PAGE_TOKEN_ETERNO, "Eterno nostra giustizia")
        else:
            print("  ℹ️ [FB Eterno nostra giustizia]: Token non configurato. Aggiungi FB_PAGE_ACCESS_TOKEN_ETERNO e FB_PAGE_ID_ETERNO nei secret per attivare.")

        # b) Pagina Facebook "Antonio Giancani" (Reel + Storie)
        pubblica_reel_facebook(video_path, storia)
        dividi_e_pubblica_storie_facebook(video_path, clips, storia, FB_PAGE_ID_ANTONIO, FB_PAGE_TOKEN_ANTONIO, "Antonio Giancani")

        # c) Canale YouTube Shorts "Eterno nostra giustizia"
        if genera_metadati_youtube and pubblica_video_youtube:
            try:
                yt_payload, _ = genera_metadati_youtube(video_path, storia, mode="bibbia")
                pubblica_video_youtube(video_path, yt_payload, mode="bibbia")
            except Exception as e_yt:
                print(f"  ⚠️ Warning YouTube Bibbia: {e_yt}")

    elif "mitologia" in mode_lower:
        # a) Pagina Facebook "Antonio Giancani" (Reel + Storie)
        pubblica_reel_facebook(video_path, storia)
        dividi_e_pubblica_storie_facebook(video_path, clips, storia, FB_PAGE_ID_ANTONIO, FB_PAGE_TOKEN_ANTONIO, "Antonio Giancani")

        # b) Pagina Facebook "Immobiliare Giancani" -> ESCLUSA TASSATIVAMENTE DA MITOLOGIA
        print("  🚫 [POLICY BRAND] Mitologia Greca esclusa dalla Pagina Immobiliare Giancani (riservata ai soli contenuti immobiliari). — Immobiliare Giancani")

        # c) Canale YouTube Shorts "Storie della Mitologia Greca" (Ore 18:00)
        if genera_metadati_youtube and pubblica_video_youtube:
            try:
                yt_payload, _ = genera_metadati_youtube(video_path, storia, mode="mitologia")
                pubblica_video_youtube(video_path, yt_payload, mode="mitologia")
            except Exception as e_yt:
                print(f"  ⚠️ Warning YouTube Shorts Mitologia: {e_yt}")

    elif "pillole" in mode_lower:
        # a) Pagina Facebook "Immobiliare Giancani" (Reel + Storie + Post testuale Colonna F)
        if FB_PAGE_ID_GIANCANI and FB_PAGE_TOKEN_GIANCANI:
            pubblica_reel_su_pagina_facebook(FB_PAGE_ID_GIANCANI, FB_PAGE_TOKEN_GIANCANI, video_path, storia, "Immobiliare Giancani")
            dividi_e_pubblica_storie_facebook(video_path, clips, storia, FB_PAGE_ID_GIANCANI, FB_PAGE_TOKEN_GIANCANI, "Immobiliare Giancani")
            pubblica_post_testuale_facebook(FB_PAGE_ID_GIANCANI, FB_PAGE_TOKEN_GIANCANI, storia, "Immobiliare Giancani")
        else:
            print("  ℹ️ [FB Immobiliare Giancani]: Token non configurato. Aggiungi FB_PAGE_ACCESS_TOKEN_GIANCANI nei secret per attivare.")

        # b) Pagina Facebook "Antonio Giancani" (Reel + Storie)
        pubblica_reel_facebook(video_path, storia)
        dividi_e_pubblica_storie_facebook(video_path, clips, storia, FB_PAGE_ID_ANTONIO, FB_PAGE_TOKEN_ANTONIO, "Antonio Giancani")

        # c) Canale YouTube Shorts "Immobiliare Giancani"
        if genera_metadati_youtube and pubblica_video_youtube:
            try:
                yt_payload, _ = genera_metadati_youtube(video_path, storia, mode="giancani")
                pubblica_video_youtube(video_path, yt_payload, mode="giancani")
            except Exception as e_yt:
                print(f"  ⚠️ Warning YouTube Giancani: {e_yt}")

    else:
        # Grandi Classici (Standard) -> FB Antonio Giancani (Reel + Storie) + YouTube Shorts
        pubblica_reel_facebook(video_path, storia)
        dividi_e_pubblica_storie_facebook(video_path, clips, storia, FB_PAGE_ID_ANTONIO, FB_PAGE_TOKEN_ANTONIO, "Antonio Giancani")

        # Pagina Facebook "Immobiliare Giancani" -> ESCLUSA TASSATIVAMENTE DA CONTENUTI NON IMMOBILIARI
        print("  🚫 [POLICY BRAND] Grandi Classici / Libri esclusi dalla Pagina Immobiliare Giancani (riservata ai soli contenuti immobiliari). — Immobiliare Giancani")

        if genera_metadati_youtube and pubblica_video_youtube:
            try:
                yt_payload, _ = genera_metadati_youtube(video_path, storia, mode="standard")
                pubblica_video_youtube(video_path, yt_payload, mode="giancani")
            except Exception as e_yt:
                print(f"  ⚠️ Warning YouTube Classici: {e_yt}")


# ── ORCHESTRATORE PRINCIPALE (MAIN PIPELINE) ────────────────────────────────
async def esegui_pipeline(story_id=None, voice=None, mode="standard", output_json_only=False, solo_telegram=False):
    start_time = time.time()
    
    if not voice:
        voice = VOICES_BY_MODE.get(mode, "it-IT-ElsaNeural")

    mode_titles = {
        "mitologia": "STORIE DELLA MITOLOGIA GRECA (ORE 18:00)",
        "bibbia": "STORIE BIBLICHE — «ETERNO NOSTRA GIUSTIZIA» (ORE 20:00)",
        "standard": "GRANDI CLASSICI DELLA LETTERATURA (RIASSUNTO 2 MINUTI)",
        "pillole": "PILLOLE IMMOBILIARI & LEGALI QUOTIDIANE (ORE 06:00)"
    }
    mode_name = mode_titles.get(mode, "GRANDI CLASSICI")
    
    print("="*75)
    print(f"🎬 AVVIO BOT REELS MASTER: {mode_name} — VIDEO 9:16")
    print(f"🎙️ Voce Narrante Selezionata: {voice}")
    print("⭐ Produzione & Strategia a cura di: IMMOBILIARE GIANCANI")
    print("="*75)

    # 1. Estrazione dati rigorosamente da Colonna F
    storia = estrai_storia_colonna_f(id_richiesto=story_id, mode=mode)
    scene = crea_struttura_scene(storia, mode=mode)

    if output_json_only:
        json_out_file = os.path.join(OUTPUT_DIR, f"episodio_{mode}_{storia['id']}.json")
        payload_json = {
            "meta": {
                "titolo": storia["titolo"],
                "autore": storia["autore"],
                "categoria": storia.get("categoria", mode),
                "orario_post": "18:00" if mode == "mitologia" else ("06:00" if mode == "pillole" else "20:00")
            },
            "audio_script": storia["testo_colonna_f"],
            "scenes": scene
        }
        json_str = json.dumps(payload_json, ensure_ascii=False, indent=2)
        with open(json_out_file, "w", encoding="utf-8") as jf:
            jf.write(json_str)
        print(f"✅ Schema JSON salvato in: {json_out_file}")
        return
    
    clips = []
    durata_totale = 0.0
    
    # 2. Creazione delle scene del riassunto (2 minuti)
    for idx, s in enumerate(scene, start=1):
        print(f"\n--- 🎬 [SCENA {idx}/{len(scene)}] {storia['titolo']} ---")
        base_name = f"{mode}_{storia['id']}_scena_{idx}"
        audio_file = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
        img_file = os.path.join(OUTPUT_DIR, f"{base_name}.jpg")
        overlay_file = os.path.join(OUTPUT_DIR, f"{base_name}_overlay.png")
        clip_file = os.path.join(OUTPUT_DIR, f"{base_name}_clip.mp4")
        
        # Voce Narrante Neurale
        text_voce = s["testo"] if s["testo"] else f"{storia['titolo']}, in due minuti."
        print(f"  🎙️ Sintesi vocale: \"{text_voce[:45]}...\"")
        await genera_voce_edge_tts(text_voce, audio_file, voce=voice)
        durata_scena = ottieni_durata_audio(audio_file)
        durata_totale += durata_scena
        
        # Download Immagine con ottimizzazione anti-timeout
        story_id_int = int(storia["id"]) if str(storia["id"]).isdigit() else 1
        scene_seed = story_id_int * 100 + idx
        scarica_immagine_pollinations(
            s["prompt"],
            img_file,
            seed=scene_seed,
            categoria=storia.get("categoria", mode),
            is_intro=(idx == 1),
            idx=idx,
            story_id=storia["id"]
        )
        
        # Overlay: Titolo badge solo scena 1, sottotitoli Comic Sticker
        crea_overlay_grafico(
            s["testo"], 
            storia["titolo"], 
            storia["autore"], 
            overlay_file, 
            is_outro=s["is_outro"], 
            categoria=storia.get("categoria", mode),
            idx=idx,
            is_intro=(idx == 1)
        )
        
        # Montaggio Ken Burns della scena
        print(f"  🎞️ Montaggio Ken Burns ({round(durata_scena, 1)}s)...")
        crea_clip_ken_burns(img_file, audio_file, overlay_file, clip_file, idx)
        clips.append(clip_file)

    # 3. Montaggio video finale e colonna sonora
    video_finale = os.path.join(OUTPUT_DIR, f"reels_{mode}_{storia['id']}.mp4")
    print(f"\n🎬 Montaggio finale del video: {os.path.basename(video_finale)}...")
    monta_video_finale(clips, video_finale, durata_totale)
    
    file_mb = round(os.path.getsize(video_finale) / (1024 * 1024), 2)
    print(f"✅ Video finale generato con successo! ({file_mb} MB, Durata: ~{round(durata_totale, 1)}s)")

    # 4. Routing Social e Pubblicazione Centralizzata (Punto 4)
    esegui_routing_pubblicazione(video_finale, clips, storia, mode=mode, solo_telegram=solo_telegram)

    # 5. Salvataggio stato di rotazione progressiva (evita sovrapposizioni)
    try:
        tracker_file = os.path.join(BASE_DIR, f"stato_rotazione_{mode}.json")
        id_num = int(storia["id"]) if str(storia["id"]).isdigit() else storia["id"]
        with open(tracker_file, "w", encoding="utf-8") as tf:
            json.dump({
                "ultimo_id": id_num,
                "titolo": storia["titolo"],
                "data_completamento": time.strftime("%Y-%m-%d %H:%M:%S")
            }, tf, indent=2, ensure_ascii=False)
        print(f"📈 [ROTAZIONE PROGRESSIVA]: Stato aggiornato -> Ultimo ID completato: {storia['id']} («{storia['titolo']}»)")
    except Exception as e_track:
        print(f"⚠️ Avviso aggiornamento tracker rotazione: {e_track}")

    elapsed = round(time.time() - start_time, 1)
    print("\n" + "="*75)
    print(f"✨ PIPELINE COMPLETATA CON SUCCESSO IN {elapsed} SECONDI!")
    print("⭐ PROGETTO E REALIZZAZIONE: IMMOBILIARE GIANCANI ⭐")
    print("="*75 + "\n")


# ── ENTRY POINT CLI ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot Reels Master — Pipeline Video 9:16 Multi-Canale")
    parser.add_argument("--mode", type=str, default=None, choices=["standard", "bibbia", "pillole", "mitologia"], help="Modalità bot")
    parser.add_argument("--id", type=str, default=None, help="ID specifico della storia o pillola da generare")
    parser.add_argument("--voice", type=str, default=None, help="Voce personalizzata")
    parser.add_argument("--json", action="store_true", help="Genera solo lo schema JSON")
    parser.add_argument("--solo-telegram", action="store_true", help="Invia solo ed esclusivamente su Telegram")
    args = parser.parse_args()

    mode_effettivo = args.mode
    if not mode_effettivo:
        import datetime
        ora_utc = datetime.datetime.now(datetime.timezone.utc).hour
        # Schedule cron:
        # 04:00 UTC (ore 06:00 Roma) -> pillole
        # 16:00 UTC (ore 18:00 Roma) -> mitologia
        # 18:00 UTC (ore 20:00 Roma) -> bibbia
        if 2 <= ora_utc < 10:
            mode_effettivo = "pillole"
        elif 10 <= ora_utc < 17:
            mode_effettivo = "mitologia"
        else:
            mode_effettivo = "bibbia"

    asyncio.run(esegui_pipeline(story_id=args.id, voice=args.voice, mode=mode_effettivo, output_json_only=args.json, solo_telegram=args.solo_telegram))
