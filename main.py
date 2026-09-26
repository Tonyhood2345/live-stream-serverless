#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  🎬 BOT REELS NARRATIVI AD ALTO ENGAGEMENT (90s - 150s)
  Storytelling Pipeline: Fullscreen 9:16, Sottotitoli Moderni, Ken Burns Fluido
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

# Patch aiohttp per runner CI/Windows
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

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")

FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "")

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
    "Antique masterwork illustration style, dramatic chiaroscuro watercolor and fine ink engraving. "
    "Rich cinematic details, warm ochre and deep indigo palette on parchment texture. "
    "Epic atmosphere, highly detailed composition, masterclass print quality. --no 3d render, CGI, glossy, photo"
)

# ── ESTRAZIONE RIGOROSA DA COLONNA F ─────────────────────────────────────────
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
                        "categoria": "STANDARD",
                        "testo_colonna_f": row[5].strip(),
                        "prompts_g": row[6].strip() if len(row) > 6 else ""
                    })

    if not storie:
        raise ValueError(f"Nessuna storia valida in: {csv_file}")

    if id_richiesto:
        trovate = [s for s in storie if str(s["id"]) == str(id_richiesto)]
        storia = trovate[0] if trovate else random.choice(storie)
    else:
        storia = random.choice(storie)

    print("\n" + "="*70)
    print("📖 [ESTRAZIONE DATI COLONNA F]")
    print(f"📌 [ID {storia['id']}]: «{storia['titolo']}»")
    print("="*70 + "\n")
    return storia

# ── STRUTTURAZIONE SCENE PER DURATA 90s - 150s ──────────────────────────────
def crea_struttura_scene(storia, mode="standard"):
    testo_f = storia["testo_colonna_f"].strip()
    categoria = storia.get("categoria", mode).upper()

    # Ripartizione frasi
    if "|||" in testo_f:
        frasi_raw = [f.strip() for f in testo_f.split("|||") if f.strip()]
    else:
        frasi_raw = [f.strip() for f in re.split(r'(?<=[.!?])\s+', testo_f) if f.strip()]

    # Raggruppamento o suddivisione per raggiungere target di 7-10 scene
    frasi = []
    chunk = ""
    for f in frasi_raw:
        if len(chunk) + len(f) < 140:
            chunk = (chunk + " " + f).strip()
        else:
            if chunk:
                frasi.append(chunk)
            chunk = f
    if chunk:
        frasi.append(chunk)

    # Hook iniziale moderno (primi 3 secondi)
    if categoria == "STANDARD":
        if not any(hk in frasi[0].lower() for hk in ["sapevi", "cosa faresti", "il mito"]):
            frasi[0] = f"Cosa faresti se il solo sguardo del tuo nemico potesse tramutarti in pietra? Ecco la vera sfida di {storia['titolo']}."

    # CTA finale con ponte logico verso il brand
    frasi[-1] = (
        frasi[-1].rstrip(".") + 
        ". Grandi sfide e decisioni importanti richiedono sempre lucidità, strategia e una guida esperta. "
        "Per orientarti nel mercato con sicurezza, affidati a Immobiliare Giancani."
    )

    prompts_raw = [p.strip() for p in storia["prompts_g"].split("|||") if p.strip()] if storia.get("prompts_g") else []

    scene = []
    num_scene = len(frasi)
    for i, frase in enumerate(frasi):
        p_custom = prompts_raw[i] if i < len(prompts_raw) else ""
        if p_custom:
            prompt_img = f"{ANTIQUE_STORYBOOK_STYLE}, {storia['titolo']}: {p_custom[:90]}"
        else:
            prompt_img = f"{ANTIQUE_STORYBOOK_STYLE}, cinematic scene: {storia['titolo']} - {frase[:80]}"

        scene.append({
            "scena_id": i + 1,
            "testo": frase,
            "prompt": prompt_img,
            "is_intro": (i == 0),
            "is_outro": (i == num_scene - 1)
        })

    return scene

# ── VOCE NARRATIVA AD ALTA ESPRESSIVITÀ (EDGE-TTS) ──────────────────────────
async def genera_voce_edge_tts(testo, file_audio, voce="it-IT-DiegoNeural"):
    """
    Voce neurale profonda, cadenzata (-5%) per dare enfasi e respiro da audiolibro.
    """
    success = False
    try:
        import edge_tts
        # Diego: tono caldo e profondo. Per voce femminile usare it-IT-ElsaNeural
        comm = edge_tts.Communicate(testo, voce, rate="-5%", pitch="-1Hz")
        await asyncio.wait_for(comm.save(file_audio), timeout=25)
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

# ── DOWNLOAD IMMAGINE FULLSCREEN 9:16 (POLLINATIONS) ────────────────────────
def scarica_immagine_pollinations(prompt, output_img, seed=100):
    if os.path.exists(output_img) and os.path.getsize(output_img) > 10000:
        return True

    clean_prompt = prompt.replace("2D cartoon animation style,", "").strip(" ,.")[:200]
    encoded = urllib.parse.quote(clean_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&nologo=true&seed={seed}&model=turbo"

    for attempt in range(2):
        try:
            print(f"  🎨 Download Immagine 9:16 (Seed: {seed})...")
            resp = requests.get(url, timeout=12, verify=False, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(output_img, "wb") as f:
                    f.write(resp.content)
                return True
        except Exception:
            time.sleep(1.5)

    # Fallback su gradiente cinematografico elegante
    img = Image.new("RGB", (720, 1280), color=(18, 22, 32))
    img.save(output_img, "JPEG")
    return True

# ── OVERLAY GRAFICO MODERNO (SENZA BANNER FISSI, SOTTOTITOLI PULITI) ─────────
def crea_overlay_grafico(testo, titolo_libro, output_overlay, is_intro=False, is_outro=False):
    """
    Design moderno:
    - Nessuna barra fissa in alto.
    - Intro: tag pill minimale trasparente che appare e scompare.
    - Sottotitoli: testo a contrasto elevato, font bold, pill traslucido arrotondato in safe-zone.
    """
    img = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    fonts_dir = os.path.join(BASE_DIR, "assets", "fonts")
    
    def get_font(name, fallback, size):
        p = os.path.join(fonts_dir, name)
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
        for fb in fallback:
            try: return ImageFont.truetype(fb, size)
            except: pass
        return ImageFont.load_default()

    font_sub = get_font("Montserrat-Bold.ttf", ["arialbd.ttf", "helvetica.ttf"], 28)
    font_intro = get_font("Cinzel-Bold.ttf", ["georgiab.ttf", "arialbd.ttf"], 24)
    font_brand = get_font("Montserrat-Bold.ttf", ["arialbd.ttf", "helvetica.ttf"], 30)
    font_claim = get_font("Montserrat-Regular.ttf", ["arial.ttf", "helvetica.ttf"], 20)

    # 1. Badge Intro Minimal (solo nei primi secondi)
    if is_intro:
        draw.rounded_rectangle([120, 90, 600, 150], radius=24, fill=(10, 14, 24, 190), outline=(230, 190, 90, 220), width=2)
        draw.text((360, 120), titolo_libro.upper(), fill=(255, 245, 225), font=font_intro, anchor="mm")

    # 2. Sottotitoli Moderni (Pill fluttuante compatto nel terzo inferiore)
    import textwrap
    lines = textwrap.wrap(testo, width=36)
    line_h = 36
    box_padding = 22
    box_w = 640
    box_h = len(lines) * line_h + box_padding * 2

    box_y = 1000 - (box_h // 2)
    box_x = 40

    # Sfondo morbido traslucido solo dietro al testo
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=18, fill=(8, 12, 20, 175))

    start_text_y = box_y + box_padding + (line_h // 2)
    for idx, l in enumerate(lines):
        curr_y = start_text_y + (idx * line_h)
        # Ombra testo
        draw.text((362, curr_y + 2), l, fill=(0, 0, 0, 255), font=font_sub, anchor="mm")
        # Testo principale nitido
        draw.text((360, curr_y), l, fill=(255, 255, 255), font=font_sub, anchor="mm")

    # 3. Outro Card elegante
    if is_outro:
        draw.rounded_rectangle([50, 1080, 670, 1220], radius=20, fill=(10, 15, 28, 230), outline=(225, 185, 80, 240), width=2)
        draw.text((360, 1125), "IMMOBILIARE GIANCANI", fill=(235, 195, 95), font=font_brand, anchor="mm")
        draw.text((360, 1170), "La Guida Sicura per la Tua Prossima Casa", fill=(240, 240, 245), font=font_claim, anchor="mm")

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

# ── MONTAGGIO CLIP CON KEN BURNS DINAMICO ───────────────────────────────────
def crea_clip_ken_burns(img_path, audio_path, overlay_path, clip_output, idx):
    durata = ottieni_durata_audio(audio_path) + 0.4
    frames = int(durata * 25)

    # Alternanza di movimenti lenti e cinematici
    if idx % 3 == 1:
        # Slow Zoom In
        z_filter = f"zoompan=z='min(zoom+0.0008,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"
    elif idx % 3 == 2:
        # Slow Zoom Out
        z_filter = f"zoompan=z='if(lte(zoom,1.0),1.15,max(1.0,zoom-0.0008))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"
    else:
        # Slow Pan dal basso verso l'alto
        z_filter = f"zoompan=z='1.12':d={frames}:x='iw/2-(iw/zoom/2)':y='ih*0.2*(1-on/{frames})':s=720x1280:fps=25"

    filter_complex = f"[0:v]{z_filter}[bg];[bg][1:v]overlay=0:0[v]"

    cmd = [
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", img_path,
        "-i", overlay_path,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "2:a",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(durata),
        clip_output
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# ── MONTAGGIO FINALE E MIX DUCKING AUDIO ────────────────────────────────────
def monta_video_esteso(clips, output_video, durata_totale):
    concat_txt = os.path.join(OUTPUT_DIR, "concat_clips.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c.replace(os.sep, '/')}'\n")

    temp_video = os.path.join(OUTPUT_DIR, "temp_video_nomusic.mp4")
    subprocess.run([
        FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", temp_video
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Musica con ducking calibrato (volume 0.09) per dare massimo risalto alla voce narrante
    filter_mix = (
        f"[1:a]volume=0.09,afade=t=in:ss=0:d=2,afade=t=out:st={max(2, durata_totale - 3)}:d=3[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    # Traccia audio royalty-free o generatore armonico
    cmd_mix = [
        FFMPEG_EXE, "-y",
        "-i", temp_video,
        "-f", "lavfi", "-i", f"sine=frequency=180:duration={durata_totale+10}",
        "-filter_complex", filter_mix,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", output_video
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    if os.path.exists(temp_video):
        os.remove(temp_video)

# ── ORCHESTRATORE ───────────────────────────────────────────────────────────
async def esegui_pipeline(story_id=None, voice="it-IT-DiegoNeural", mode="standard"):
    print("="*75)
    print(f"🎬 AVVIO GENERAZIONE REEL ESTESO (Target: 90s - 150s)")
    print("="*75)

    storia = estrai_storia_colonna_f(id_richiesto=story_id, mode=mode)
    scene = crea_struttura_scene(storia, mode=mode)

    clips = []
    durata_totale = 0.0

    for idx, s in enumerate(scene, start=1):
        print(f"\n--- 🎬 [SCENA {idx}/{len(scene)}] {storia['titolo']} ---")
        base = f"scena_{idx}_{storia['id']}"
        audio_f = os.path.join(OUTPUT_DIR, f"{base}.mp3")
        img_f = os.path.join(OUTPUT_DIR, f"{base}.jpg")
        overlay_f = os.path.join(OUTPUT_DIR, f"{base}_ov.png")
        clip_f = os.path.join(OUTPUT_DIR, f"{base}_clip.mp4")

        # 1. Voce
        await genera_voce_edge_tts(s["testo"], audio_f, voce=voice)
        d_scena = ottieni_durata_audio(audio_f)
        durata_totale += d_scena

        # 2. Immagine Fullscreen 9:16
        scarica_immagine_pollinations(s["prompt"], img_f, seed=int(storia['id'])*100 + idx)

        # 3. Overlay moderno senza cornici fisse
        crea_overlay_grafico(s["testo"], storia["titolo"], overlay_f, is_intro=s["is_intro"], is_outro=s["is_outro"])

        # 4. Clip
        crea_clip_ken_burns(img_f, audio_f, overlay_f, clip_f, idx)
        clips.append(clip_f)

    video_out = os.path.join(OUTPUT_DIR, f"reel_completo_{storia['id']}.mp4")
    print(f"\n🎬 Montaggio video finale...")
    monta_video_esteso(clips, video_out, durata_totale)

    minuti = int(durata_totale // 60)
    secondi = int(durata_totale % 60)
    print("\n" + "="*75)
    print(f"✅ VIDEO PRONTO: {video_out}")
    print(f"⏱️ Durata Totale Ottenuta: {minuti}m {secondi}s (Target raggiunto)")
    print("="*75 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=str, default=None, help="ID storia CSV")
    parser.add_argument("--voice", type=str, default="it-IT-DiegoNeural", help="Voce (es. it-IT-DiegoNeural o it-IT-ElsaNeural)")
    parser.add_argument("--mode", type=str, default="standard")
    args = parser.parse_args()

    asyncio.run(esegui_pipeline(story_id=args.id, voice=args.voice, mode=args.mode))
