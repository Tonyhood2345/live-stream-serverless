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
CSV_BIBBIA_PATH = os.path.join(BASE_DIR, "database_storie_bibliche.csv")
CSV_PILLOLE_PATH = os.path.join(BASE_DIR, "database_pillole_immobiliari_legali.csv")
MUSIC_DIR = os.path.join(BASE_DIR, "musica_sottofondo")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Credenziali Telegram (da GitHub Secrets o fallback ambiente)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1723292483")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@immobiliaregiancani")

# Credenziali Facebook Page (Pagina Ufficiale / Profilo di Antonio Giancani)
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "108297671444008")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia")


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

# ── ROUTING CONDIZIONALE STILI & PERSONAGGIO CORE ───────────────────────────
CORE_CAT_CHARACTER = "Small expressive ginger tabby cat with bright green eyes and distinct white paws"

# Identikit visivo fisso del gatto protagonista (Stile Cartone Animato 2D con contorni neri e colori vivaci)
CAT_CHARACTER_BASE = (
    "2D cartoon animation style, cute anthropomorphic orange tabby cat standing on two legs, "
    "wearing a bright blue and white horizontally striped t-shirt, sweet friendly smile, "
    "large expressive round cartoon eyes, white paws, bold clean black ink contour lines, "
    "bright vibrant saturated colors, classic 2D cel animation art, vertical 9:16"
)

BIBLICAL_PROMPT_PREFIX = "[CLASSICAL BIBLICAL OIL/WARM WATERCOLOR STYLE]"
STANDARD_PROMPT_PREFIX = "[2D CLEAN VECTOR WEBCOMIC STYLE, THICK OUTLINES, FLAT SHADING]"


# ── REGOLA UTENTE GLOBALE: ESTRAZIONE RIGOROSA DA COLONNA F ─────────────────
def estrai_storia_colonna_f(csv_file=None, id_richiesto=None, mode="standard"):
    """
    Estrae una storia classica, biblica o pillola immobiliare dal file CSV corrispondente.
    La narrazione testuale viene prelevata RIGOROSAMENTE dalla Colonna F (o script_audio).
    """
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
                # id,titolo,riferimento_biblico,script_audio,prompt_scene_json,stato_pubblicazione
                storie.append({
                    "id": row[0].strip(),
                    "titolo": row[1].strip(),
                    "autore": row[2].strip(),  # Riferimento biblico
                    "anno": "Antico Testamento",
                    "genere": "Bibbia",
                    "categoria": "BIBBIA",
                    "testo_colonna_f": row[3].strip(),  # script_audio / Colonna F
                    "prompts_g": row[4].strip() if len(row) > 4 else "",
                    "stato": row[5].strip() if len(row) > 5 else "pronto"
                })
            elif mode == "pillole":
                # ID,Categoria,Argomento,Normativa_Riferimento,Orario,Colonna_F_Testo_Elaborazione,Stato
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
                # Standard Grandi Classici
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
        raise ValueError(f"Nessuna storia valida trovata nel database CSV: {csv_file}")

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
    print(f"📌 [MODALITÀ {storia.get('categoria', mode).upper()} - ID {storia['id']}]: «{storia['titolo']}» ({storia['autore']})")
    print(f"💬 [TESTO COLONNA F / SCRIPT]:\n\"{storia['testo_colonna_f']}\"")
    print("="*70 + "\n")
    
    return storia


# ── PARSING DEL TESTO DELLA COLONNA F IN SCENE NARRATIVE (RIASSUNTO 2 MINUTI) ─
def crea_struttura_scene(storia, mode="standard"):
    """
    Divide il testo prelevato rigorosamente dalla Colonna F nelle scene narrative
    necessarie a comporre il riassunto di 2 minuti, associando i prompt visivi corretti.
    Supporta scene JSON predefinite (come in database biblico) o parsing testuale automatico.
    """
    categoria = storia.get("categoria", mode).upper()
    
    # Se prompts_g contiene JSON valido di scene (come in database_storie_bibliche.csv)
    if storia.get("prompts_g") and storia["prompts_g"].strip().startswith("["):
        try:
            scenes_json = json.loads(storia["prompts_g"].strip())
            if isinstance(scenes_json, list) and len(scenes_json) > 0:
                scene = []
                for sc in scenes_json:
                    text_chunk = sc.get("voiceover_chunk") or sc.get("overlay_text", "")
                    prompt_str = sc.get("prompt", "")
                    scene.append({
                        "scena_id": sc.get("id", len(scene)),
                        "testo": text_chunk,
                        "prompt": prompt_str,
                        "type": sc.get("type", "story"),
                        "duration": sc.get("duration", 4.5),
                        "is_outro": (sc.get("id") == scenes_json[-1].get("id"))
                    })
                # Garanzia Personal Branding su ultima scena
                if scene and "Immobiliare Giancani" not in scene[-1]["testo"]:
                    scene[-1]["testo"] += " — Immobiliare Giancani"
                return scene
        except Exception as e_json:
            print(f"  ⚠️ Warning parsing JSON scene: {e_json}")

    testo_f = storia["testo_colonna_f"]
    prompts_raw = [p.strip() for p in storia["prompts_g"].split("|||") if p.strip()] if storia.get("prompts_g") else []
    
    # Suddivisione testo Colonna F in blocchi di scena
    if "|||" in testo_f:
        frasi = [f.strip() for f in testo_f.split("|||") if f.strip()]
    else:
        import re
        frasi = [f.strip() for f in re.split(r'(?<=[.!?])\s+', testo_f) if f.strip()]
    
    num_scene = max(len(prompts_raw), len(frasi), 4)
    while len(frasi) < num_scene:
        frasi.append("Un percorso ricco di ispirazione, saggezza e scoperte indimenticabili.")

    # Regola Utente: Prima della narrazione pronuncia la frase hook "Ecco a voi in 2 minuti..."
    hook_keywords = ["ecco a voi in 2 minuti", "ecco a voi, in 2 minuti", "in 2 minuti ecco uno"]
    has_hook = any(hk in frasi[0].lower() for hk in hook_keywords)
    if not has_hook:
        frasi[0] = f"Ecco a voi, in 2 minuti: {storia['titolo']}! E iniziamo con la narrazione: {frasi[0]}"

    # Assicuriamo che l'ultima scena rispetti la regola globale mettendo in risalto Immobiliare Giancani
    if "Immobiliare Giancani" not in frasi[-1]:
        frasi[-1] = frasi[-1].rstrip(".") + ". Con la passione, la cura e l'affidabilità di Immobiliare Giancani."

    scene = []
    for i in range(num_scene):
        prompt_custom = prompts_raw[i].strip() if i < len(prompts_raw) else ""
        if prompt_custom:
            full_prompt = prompt_custom
        elif categoria == "BIBBIA":
            # Routing Bibbia: Gatto spettatore silenzioso e rispettoso
            full_prompt = (
                f"{BIBLICAL_PROMPT_PREFIX}, Biblical event in {storia['titolo']}: {frasi[i][:70]}, "
                f"dramatic golden ambient lighting, sacred atmosphere, with a {CORE_CAT_CHARACTER} "
                f"sitting silently in the corner foreground as a respectful, awe-struck witness, 9:16 composition"
            )
        elif categoria == "PILLOLE":
            # Routing Pillole Immobiliari
            full_prompt = (
                f"[LUXURY REAL ESTATE ARCHITECTURE STYLE], elegant modern home interior, {storia['titolo']}, "
                f"with a {CORE_CAT_CHARACTER} sitting proudly next to architectural blueprint, warm sunlight, 9:16 composition"
            )
        else:
            # Routing Standard Libri
            full_prompt = f"{CAT_CHARACTER_BASE}, in the classical animated cartoon world of {storia['titolo']}, scene {i+1}"
            
        scene.append({
            "scena_id": i + 1,
            "testo": frasi[i],
            "prompt": full_prompt,
            "type": "story",
            "duration": 4.5,
            "is_outro": (i == num_scene - 1)
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

    # 2. Suffisso stilistico fisso: rispetta lo stile Biblico, Luxury o Cartone 2D
    if "[CLASSICAL BIBLICAL" in prompt or "[LUXURY REAL ESTATE" in prompt or "[2D CLEAN VECTOR" in prompt:
        full_prompt = prompt
    else:
        CARTOON_STYLE_SUFFIX = (
            ", 2D cartoon animation style, classic animated movie cel art, bold clean black ink contour outlines, "
            "vivid bright saturated colors, crisp cel shading, cheerful lively animated background, "
            "vertical 9:16, masterpiece --no 3d render, CGI, glossy, photorealistic, realistic cat, humans"
        )
        clean_prompt = prompt.replace("pixar 3d style,", "").replace("pixar 3d style", "").rstrip(" ,.")
        if "no 3d" not in clean_prompt.lower() and "no 3d render" not in clean_prompt.lower():
            full_prompt = f"{clean_prompt}{CARTOON_STYLE_SUFFIX}"
        else:
            full_prompt = clean_prompt

    encoded_prompt = urllib.parse.quote(full_prompt)
    models_to_try = ["turbo", "flux", "turbo"]
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
    
    # Caricamento font classici per libri illustrati e fiabe
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
        return ImageFont.load_default()

    font_kicker = carica_font(cinzel_path, ["georgiab.ttf", "pala.ttf", "arialbd.ttf"], 22)
    font_titolo = carica_font(playfair_path, ["georgiab.ttf", "palab.ttf", "arialbd.ttf"], 28)
    font_autore = carica_font(lora_path, ["georgia.ttf", "palai.ttf", "arial.ttf"], 22)
    font_sub = carica_font(lora_path, ["georgiab.ttf", "palab.ttf", "arialbd.ttf"], 26)
    font_brand = carica_font(cinzel_path, ["georgiab.ttf", "palab.ttf", "arialbd.ttf"], 30)
    font_motto = carica_font(playfair_path, ["georgia.ttf", "palab.ttf", "arial.ttf"], 21)
    font_submotto = carica_font(lora_path, ["georgia.ttf", "pala.ttf", "arial.ttf"], 18)

    # 1. BADGE SUPERIORE: Stile Frontespizio / Libro Classico (y=40-155)
    draw.rounded_rectangle([40, 40, 680, 155], radius=16, fill=(18, 24, 38, 225), outline=(212, 175, 55, 230), width=2)
    draw.rounded_rectangle([46, 46, 674, 149], radius=12, outline=(212, 175, 55, 100), width=1)
    draw.text((360, 65), "— I GRANDI CLASSICI IN 2 MINUTI —", fill=(234, 198, 108), font=font_kicker, anchor="mm")
    draw.text((360, 98), titolo_libro.upper(), fill=(255, 252, 245), font=font_titolo, anchor="mm")
    draw.text((360, 132), f"di {autore}", fill=(210, 225, 245), font=font_autore, anchor="mm")

    # 2. BOX SOTTOTITOLI DINAMICO NEL TERZO INFERIORE
    import textwrap
    wrapped_lines = textwrap.wrap(testo, width=44)
    line_height = 32
    padding = 20
    box_h = max(95, len(wrapped_lines) * line_height + padding * 2)
    
    if is_outro:
        box_b = 1100
        box_t = box_b - box_h
    else:
        box_t = 1040 - (box_h // 2)
        box_b = box_t + box_h
        
    draw.rounded_rectangle([35, box_t, 685, box_b], radius=16, fill=(15, 20, 32, 220), outline=(212, 175, 55, 210), width=2)
    draw.rounded_rectangle([41, box_t + 6, 679, box_b - 6], radius=12, outline=(212, 175, 55, 90), width=1)
    
    start_y = box_t + padding + (line_height / 2)
    for idx, line in enumerate(wrapped_lines):
        y_pos = start_y + (idx * line_height)
        # Effetto ombra testo per massima leggibilità
        draw.text((361, y_pos + 1), line, fill=(0, 0, 0, 240), font=font_sub, anchor="mm")
        draw.text((360, y_pos), line, fill=(255, 252, 245), font=font_sub, anchor="mm")

    # 3. OUTRO BADGE SOTTO (y tra 1115 e 1245 px): RISALTO MASSIMO A IMMOBILIARE GIANCANI
    if is_outro:
        draw.rounded_rectangle([35, 1115, 685, 1245], radius=18, fill=(16, 22, 36, 235), outline=(234, 198, 108, 240), width=2)
        draw.rounded_rectangle([41, 1121, 679, 1239], radius=14, outline=(212, 175, 55, 100), width=1)
        draw.text((360, 1146), "IMMOBILIARE GIANCANI", fill=(234, 198, 108), font=font_brand, anchor="mm")
        draw.text((360, 1182), "Il Valore di Sentirsi a Casa", fill=(255, 255, 255), font=font_motto, anchor="mm")
        draw.text((360, 1214), "Esperienza  •  Passione  •  Fiducia", fill=(195, 215, 240), font=font_submotto, anchor="mm")

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
    
    # Caption formattata per Telegram (max 1024 caratteri consentiti per video)
    testo_pulito = storia['testo_colonna_f'].replace('|||', ' ')
    if len(testo_pulito) > 350:
        estratto_display = testo_pulito[:330] + "..."
    else:
        estratto_display = testo_pulito

    categoria = storia.get("categoria", "STANDARD").upper()
    if categoria == "BIBBIA":
        header = "📖 <b>STORIE BIBLICHE — «ETERNO NOSTRA GIUSTIZIA»</b>"
        sub_info = (
            f"📜 <b>{storia['titolo']}</b> ({storia.get('autore', '')})\n"
            f"⏱️ Formato: <i>Riassunto Completo in 2 Minuti</i>\n"
            f"🎨 Stile: <i>Biblico Tradizionale / Acquerello Caldo</i>"
        )
        tags = "#StorieBibliche #EternoNostraGiustizia #Fede #ParolaDiDio #ImmobiliareGiancani"
    elif categoria == "PILLOLE":
        header = "🏢 <b>PILLOLA IMMOBILIARE & LEGALE (ORE 06:00)</b>"
        sub_info = (
            f"📜 <b>{storia['titolo']}</b>\n"
            f"⏱️ Formato: <i>Consiglio Esperto in 2 Minuti</i>\n"
            f"👔 Rubrica: <i>Guida Pratica & Tutela Legale</i>"
        )
        tags = "#Immobiliare #ConsulenzaLegale #Casa #PillolaDelGiorno #Favara #Agrigento #ImmobiliareGiancani"
    else:
        header = "🐱 <b>IL GATTO NARRATORE DI GRANDI CLASSICI</b>"
        sub_info = (
            f"📖 <b>{storia['titolo']}</b> ({storia.get('anno', '')})\n"
            f"✍️ Autore: <b>{storia.get('autore', '')}</b>\n"
            f"⏱️ Formato: <i>Riassunto Completo in 2 Minuti</i>\n"
            f"🎭 Genere: <i>{storia.get('genere', '')}</i>"
        )
        tags = "#GrandiClassici #Letteratura #GattoNarratore #Storytelling #ImmobiliareGiancani"

    caption = (
        f"{header}\n\n"
        f"{sub_info}\n\n"
        f"💬 <b>Estratto Narrazione (Colonna F):</b>\n"
        f"«<i>{estratto_display}</i>»\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 <b>Produzione e Personal Branding:</b>\n"
        f"🏠 ⭐ <b>IMMOBILIARE GIANCANI</b> ⭐\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{tags}"
    )
    
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "✨ Sito Web Immobiliare Giancani", "url": "https://immobiliaregiancani.it"}
            ],
            [
                {"text": "🔄 Altro Contenuto", "callback_data": "NUOVA_STORIA"}
            ]
        ]
    }
    
    destinazioni = [TELEGRAM_CHAT_ID]
    if TELEGRAM_CHANNEL_ID and TELEGRAM_CHANNEL_ID not in destinazioni:
        destinazioni.append(TELEGRAM_CHANNEL_ID)
        
    almeno_uno_inviato = False
    for chat_target in destinazioni:
        try:
            with open(video_path, "rb") as vf:
                files = {"video": vf}
                data = {
                    "chat_id": chat_target,
                    "caption": caption,
                    "parse_mode": "HTML",
                    "supports_streaming": True,
                    "reply_markup": json.dumps(inline_keyboard)
                }
                resp = requests.post(url, data=data, files=files, timeout=90, verify=False)
                if resp.status_code == 200:
                    print(f"✅ Video inviato con successo su Telegram a {chat_target}!")
                    almeno_uno_inviato = True
                    # Invia anche il testo integrale del riassunto se lungo
                    if len(testo_pulito) > 350:
                        msg_testo = (
                            f"📜 <b>TESTO INTEGRALE NARRATO (COLONNA F)</b>\n"
                            f"📖 <b>{storia['titolo']}</b>\n\n"
                            f"{storia['testo_colonna_f'].replace('|||', chr(10) + chr(10))}\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"⭐ Con la passione e l'affidabilità di <b>Immobiliare Giancani</b>."
                        )
                        requests.post(
                            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                            json={"chat_id": chat_target, "text": msg_testo, "parse_mode": "HTML"},
                            timeout=20,
                            verify=False
                        )
                else:
                    if "bot is not a member" in resp.text:
                        print(f"ℹ️ Canale {chat_target}: per ricevere i video direttamente nel canale, aggiungi @Antigravity1981bot come Amministratore.")
                    else:
                        print(f"❌ Risposta Telegram per {chat_target} ({resp.status_code}): {resp.text}")
        except Exception as ex:
            print(f"❌ Errore durante l'invio su Telegram a {chat_target}: {ex}")

    return almeno_uno_inviato


# ── PUBBLICAZIONE FACEBOOK REEL SULLA PAGINA DI ANTONIO GIANCANI ─────────────
def pubblica_reel_facebook(video_path, storia):
    """
    Pubblica il video verticale di 2 minuti come Reel ufficiale
    sulla Pagina Facebook di Antonio Giancani (ID 108297671444008).
    """
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        print("⚠️ Credenziali Facebook mancanti. Salto pubblicazione Reel.")
        return False
        
    print(f"\n🎥 [FACEBOOK REEL] Pubblicazione sulla pagina di Antonio Giancani (ID: {FB_PAGE_ID})...")
    url_reels = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/video_reels"
    
    try:
        # 1. Start Phase
        r1 = requests.post(url_reels, data={"upload_phase": "start", "access_token": FB_PAGE_TOKEN}, verify=False, timeout=25)
        res1 = r1.json()
        vid = res1.get("video_id")
        up_url = res1.get("upload_url")
        if not vid or not up_url:
            print(f"❌ Errore avvio Reel Facebook: {res1}")
            return False
            
        # 2. Upload Phase
        file_size = os.path.getsize(video_path)
        headers = {
            "Authorization": f"OAuth {FB_PAGE_TOKEN}",
            "offset": "0",
            "file_size": str(file_size),
            "Content-Type": "application/octet-stream"
        }
        with open(video_path, "rb") as vf:
            video_bytes = vf.read()
            
        print(f"  📤 Caricamento video ({round(file_size/(1024*1024), 2)} MB) su server Meta...")
        r2 = requests.post(up_url, data=video_bytes, headers=headers, verify=False, timeout=180)
        if r2.status_code != 200:
            print(f"❌ Errore upload binary Reel: {r2.text}")
            return False
            
        # 3. Finish Phase
        testo_pulito = storia['testo_colonna_f'].replace('|||', ' ')
        caption = (
            f"🐱 IL GATTO NARRATORE DI GRANDI CLASSICI\n\n"
            f"Ecco a voi in 2 minuti: {storia['titolo']} ({storia['anno']}) di {storia['autore']}!\n\n"
            f"{testo_pulito[:450]}...\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 Produzione e Personal Branding:\n"
            f"⭐ IMMOBILIARE GIANCANI ⭐\n"
            f"Il Valore di Sentirsi a Casa\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"#Reels #GrandiClassici #Letteratura #AntonioGiancani #ImmobiliareGiancani #Libri #Storytelling"
        )
        r3 = requests.post(url_reels, data={
            "upload_phase": "finish",
            "access_token": FB_PAGE_TOKEN,
            "video_id": vid,
            "video_state": "PUBLISHED",
            "description": caption
        }, verify=False, timeout=35)
        res3 = r3.json()
        if res3.get("success"):
            print(f"✅ [FACEBOOK REEL] Pubblicato con successo sulla pagina di Antonio Giancani! (Post ID: {res3.get('post_id', vid)})")
            return True
        else:
            print(f"⚠️ Risposta Finish Reel: {res3}")
            return False
    except Exception as e:
        print(f"❌ Errore pubblicazione Reel Facebook: {e}")
        return False


# ── DIVISIONE IN STORIE & PUBBLICAZIONE SEQUENZIALE SU FACEBOOK ─────────────
def dividi_e_pubblica_storie_facebook(video_path, clips, storia):
    """
    Divide il video narrativo nelle sue storie e le pubblica in sequenza su
    Facebook Stories della pagina di Antonio Giancani per coprire l'intero video di 2 minuti.
    """
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        print("⚠️ Credenziali Facebook mancanti. Salto pubblicazione Storie.")
        return False

    print(f"\n📱 [FACEBOOK STORIE] Divisione e pubblicazione sequenziale per coprire tutto il video...")
    url_stories = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/video_stories"
    
    # Le clip delle singole scene (da ~15s ciascuna) corrispondono esattamente alle storie sequenziali
    story_files = [c for c in clips if os.path.exists(c)]
    total_storie = len(story_files)
    if total_storie == 0:
        print("⚠️ Nessuna clip storia disponibile.")
        return False

    print(f"  🎬 Totale Storie sequenziali da pubblicare: {total_storie} (ciascuna ~15s per coprire i 2 minuti)")
    success_count = 0
    
    for idx, s_clip in enumerate(story_files, 1):
        try:
            print(f"  📤 [Storia {idx}/{total_storie}] Caricamento ({round(os.path.getsize(s_clip)/1024, 1)} KB)...", flush=True)
            # 1. Start Story
            r1 = requests.post(url_stories, data={"upload_phase": "start", "access_token": FB_PAGE_TOKEN}, verify=False, timeout=20)
            res1 = r1.json()
            vid = res1.get("video_id")
            up_url = res1.get("upload_url")
            if not vid or not up_url:
                print(f"    ⚠️ Errore start story {idx}: {res1}")
                continue
                
            # 2. Upload Bytes
            file_size = os.path.getsize(s_clip)
            headers = {
                "Authorization": f"OAuth {FB_PAGE_TOKEN}",
                "offset": "0",
                "file_size": str(file_size),
                "Content-Type": "application/octet-stream"
            }
            with open(s_clip, "rb") as cf:
                clip_bytes = cf.read()
            r2 = requests.post(up_url, data=clip_bytes, headers=headers, verify=False, timeout=90)
            
            # 3. Finish Story
            r3 = requests.post(url_stories, data={
                "upload_phase": "finish",
                "access_token": FB_PAGE_TOKEN,
                "video_id": vid,
                "video_state": "PUBLISHED"
            }, verify=False, timeout=30)
            res3 = r3.json()
            if res3.get("success"):
                print(f"    ✅ [Storia {idx}/{total_storie}] Pubblicata con successo online! (Post ID: {res3.get('post_id')})")
                success_count += 1
            else:
                print(f"    ⚠️ Risposta finish story {idx}: {res3}")
                
            time.sleep(2)
        except Exception as e_st:
            print(f"    ❌ Errore pubblicazione storia {idx}: {e_st}")

    print(f"✨ [FACEBOOK STORIE] Pubblicate con successo {success_count}/{total_storie} storie sulla pagina di Antonio Giancani!")
    return success_count > 0


def genera_json_esecuzione(storia, scene, mode="standard"):
    """Genera lo schema JSON dell'episodio rispettando la struttura pipeline richiesta."""
    cat = "BIBBIA" if mode == "bibbia" or storia.get("categoria") == "BIBBIA" else "STANDARD"
    orario = "06:00" if mode == "pillole" else "20:00"
    
    payload = {
        "meta": {
            "titolo": storia["titolo"],
            "autore": storia["autore"],
            "categoria": cat,
            "orario_post": orario
        },
        "audio_script": storia["testo_colonna_f"],
        "scenes": []
    }
    
    for idx, s in enumerate(scene):
        sc_id = s.get("scena_id", idx)
        dur = s.get("duration", 4.5)
        pr = s.get("prompt", "")
        if idx == 0 and s.get("type") == "hook":
            payload["scenes"].append({
                "id": sc_id,
                "type": "hook",
                "duration": dur,
                "overlay_text": f"{storia['titolo'].upper()} - {storia['autore']} - in 2 minuti",
                "prompt": pr
            })
        else:
            payload["scenes"].append({
                "id": sc_id,
                "type": "story",
                "duration": dur,
                "voiceover_chunk": s["testo"],
                "prompt": pr
            })
            
    return payload


# ── ORCHESTRATORE PRINCIPALE (MAIN PIPELINE) ────────────────────────────────
async def esegui_pipeline(story_id=None, voice="it-IT-DiegoNeural", mode="standard", output_json_only=False):
    start_time = time.time()
    mode_titles = {
        "bibbia": "STORIE BIBLICHE — «ETERNO NOSTRA GIUSTIZIA»",
        "standard": "GRANDI CLASSICI DELLA LETTERATURA (RIASSUNTO 2 MINUTI)",
        "pillole": "PILLOLE IMMOBILIARI & LEGALI QUOTIDIANE (ORE 06:00)"
    }
    mode_name = mode_titles.get(mode, "GRANDI CLASSICI")
    
    print("="*75)
    print(f"🎬 AVVIO BOT REELS: {mode_name} — VIDEO 9:16")
    print("⭐ Produzione & Strategia a cura di: IMMOBILIARE GIANCANI")
    print("="*75)

    # 1. Estrazione dati rigorosamente da Colonna F
    storia = estrai_storia_colonna_f(id_richiesto=story_id, mode=mode)
    scene = crea_struttura_scene(storia, mode=mode)

    # Se richiesta solo generazione JSON di esecuzione
    if output_json_only:
        payload_json = genera_json_esecuzione(storia, scene, mode=mode)
        json_str = json.dumps(payload_json, ensure_ascii=False, indent=2)
        print("\n" + "="*70)
        print("📄 [SCHEMA JSON DI ESECUZIONE EPISODIO]:")
        print(json_str)
        print("="*70 + "\n")
        json_out_file = os.path.join(OUTPUT_DIR, f"episodio_{mode}_{storia['id']}.json")
        with open(json_out_file, "w", encoding="utf-8") as jf:
            jf.write(json_str)
        print(f"✅ JSON salvato in: {json_out_file}")
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
        
        # Immagine AI Pollinations
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
    video_finale = os.path.join(OUTPUT_DIR, f"reels_{mode}_{storia['id']}.mp4")
    print(f"\n🎬 Montaggio finale del video: {os.path.basename(video_finale)}...")
    monta_video_finale(clips, video_finale, durata_totale)
    
    file_mb = round(os.path.getsize(video_finale) / (1024 * 1024), 2)
    print(f"✅ Video finale generato con successo! ({file_mb} MB, Durata: ~{round(durata_totale, 1)}s)")

    # 4. Invio Telegram Bot
    invia_su_telegram(video_finale, storia)

    # 5. Pubblicazione come Reel su Pagina Facebook di Antonio Giancani
    pubblica_reel_facebook(video_finale, storia)

    # 6. Divisione e Pubblicazione come Storie sequenziali per coprire tutto il video
    dividi_e_pubblica_storie_facebook(video_finale, clips, storia)

    elapsed = round(time.time() - start_time, 1)
    print("\n" + "="*75)
    print(f"✨ PIPELINE COMPLETATA CON SUCCESSO IN {elapsed} SECONDI!")
    print("⭐ PROGETTO E REALIZZAZIONE: IMMOBILIARE GIANCANI ⭐")
    print("="*75 + "\n")


# ── ENTRY POINT CLI ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot Reels Multi-Modalità (Bibbia, Grandi Classici, Pillole 06:00)")
    parser.add_argument("--mode", type=str, default=None, choices=["standard", "bibbia", "pillole"], help="Modalità bot (bibbia, standard, pillole)")
    parser.add_argument("--id", type=str, default=None, help="ID specifico della storia o pillola da generare")
    parser.add_argument("--voice", type=str, default="it-IT-DiegoNeural", help="Voce Edge-TTS (es. it-IT-DiegoNeural o it-IT-ElsaNeural)")
    parser.add_argument("--json", action="store_true", help="Genera e stampa solo il JSON di esecuzione senza montare il video")
    args = parser.parse_args()

    mode_effettivo = args.mode
    if not mode_effettivo:
        import datetime
        ora_utc = datetime.datetime.now(datetime.timezone.utc).hour
        # Schedule cron: 04:00 UTC (ore 06:00 Roma) -> pillole
        # Schedule cron: 18:00 UTC (ore 20:00 Roma) -> bibbia
        if 2 <= ora_utc <= 8:
            mode_effettivo = "pillole"
        else:
            mode_effettivo = "bibbia"

    asyncio.run(esegui_pipeline(story_id=args.id, voice=args.voice, mode=mode_effettivo, output_json_only=args.json))
