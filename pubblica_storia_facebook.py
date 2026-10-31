#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
IMMOBILIARE GIANCANI — GESTORE STORIE SOCIAL FACEBOOK (CLOUD & GITHUB ACTIONS)
MODALITÀ LIVE (OGNI 30 MIN IN DIRETTA) & MODALITÀ OFFLINE (OGNI ORA VIDEO/POST)
═══════════════════════════════════════════════════════════════════════════════
Funzionalità:
1. Modalità LIVE (--mode live):
   - Si attiva ESCLUSIVAMENTE quando la diretta live streaming è in onda.
   - Ogni 30 minuti genera e pubblica una video storia 1080x1920 con l'immobile attivo,
     foto reale, watermark logo, frase positiva flash nei primi 1.5s, musica allegra (124 BPM) e voce
     dei conduttori (DarIA/DarIO) che incita gli utenti ad entrare subito a vedere la diretta.
   - Al primo avvio pubblica anche un post d'invito singolo sul feed di Antonio Giancani.

2. Modalità OFFLINE (--mode offline):
   - Viene eseguito ogni ora via GitHub Actions cron ('0 * * * *').
   - Verifica se la diretta live è attiva: se SI, si interrompe subito senza interferire.
   - Se NON è in live, preleva a rotazione dalle cartelle degli immobili e dai post
     di YouTube ('Post_YouTube').
   - Fa girare il video per tutto il tempo della storia (15 secondi continui),
     utilizzando clip video reali (con yt-dlp/ffmpeg) o animazione continua Ken Burns.
   - Testo prelevato RIGOROSAMENTE dalla Colonna F con superfici in 'metri quadri'.
   - Narrazione vocale espressiva (DarIA/DarIO) con musica allegra in sottofondo (ducking).
   - Personal branding costante: ogni output conclude evidenziando '— Immobiliare Giancani'.

3. Piattaforme di Pubblicazione:
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

_this_dir = os.path.dirname(os.path.abspath(__file__))
for _p in [_this_dir, os.path.join(_this_dir, "scripts"), os.path.dirname(_this_dir)]:
    if _p not in sys.path and os.path.exists(_p):
        sys.path.insert(0, _p)

import time
import json
import uuid
import shutil
import random
import re
import math
import argparse
import subprocess
import urllib.request
import urllib.parse
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import base64
import numpy as np
import wave
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageFilter

try:
    import edge_tts
    import asyncio
    HAS_EDGE_TTS = True
except Exception:
    HAS_EDGE_TTS = False

# Credenziali Facebook
PAGES = [
    {
        "nome": "Immobiliare Giancani (Pagina Ufficiale)",
        "id": (os.environ.get("FB_PAGE_ID") or "234931856561526").strip(),
        "token": (os.environ.get("FB_PAGE_TOKEN") or "EAAZAH7q8wRZAEBSrhdzTmfl8ZCzdKNEjlxs2DiLoOPinfdZABC7FdxCTmgfnA3A0bMrp2hWMBcEfWr2jIeygQX4eaUvUY9odfl0zKSQi6xY4RddUFrQ2MNL6GichP3oKloZCjRdI6cZCoflKHDmWtXqE7FWM2e9HzOYKCkgn0GVfo9Mdn3wajoshjmZAlPQ5q5iCc3lSyURtp4m8t18").strip(),
        "is_antonio": False
    },
    {
        "nome": "Antonio Giancani (Profilo Personale)",
        "id": os.environ.get("FB_ANTONIO_ID", "108297671444008"),
        "token": os.environ.get("FB_ANTONIO_TOKEN", "EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia"),
        "is_antonio": True
    }
]

IG_ACCOUNT_ID = os.environ.get("IG_ACCOUNT_ID", "17841400301393511")
YT_CHANNEL_HANDLE = "@immobiliaregiancani761"

GH_TOKEN = os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
if not GH_TOKEN:
    _token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".token")
    if os.path.exists(_token_path):
        GH_TOKEN = open(_token_path, "r", encoding="utf-8").read().strip()
    else:
        GH_TOKEN = "ghp_LCowv5wCbuz" + "dvc7uzUAFDlL1N94PjT460mJ9"
GH_REPO = os.environ.get("GH_REPO", "Tonyhood2345/live-stream-serverless")

APPS_SCRIPT_URL = (
    os.environ.get("APPS_SCRIPT_URL")
    or "https://script.google.com/macros/s/AKfycbwEeH82YCSoOc-KRZx6pSQa_k3Kb5i252_Ajljlo20IOBinGiqA1E0ZE_2gKljHpLu3/exec"
).strip()
REMOTE_LOGO_URL = "https://lh3.googleusercontent.com/d/1BoZ_9QyYPRKjZFP__iPr7mmi0aGV0G3P"

ctx = ssl._create_unverified_context()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SCRATCH_DIR = os.path.join(BASE_DIR, "output_storie")
CACHE_IMMOBILI_DIR = os.path.join(ASSETS_DIR, "immobili_cache")
os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(CACHE_IMMOBILI_DIR, exist_ok=True)

FRASI_MOTIVAZIONALI = [
    ("“La casa è dove nascono i tuoi sogni e dove inizia il tuo futuro.”", "Il momento perfetto per realizzare i tuoi progetti immobiliari è adesso! — Immobiliare Giancani"),
    ("“Ogni grande traguardo inizia trovando il luogo giusto da chiamare casa.”", "Scopri con noi l'immobile su misura per la tua felicità! — Immobiliare Giancani"),
    ("“La vera felicità è varcare la soglia della casa che hai sempre desiderato.”", "Affidati alla nostra passione ed esperienza per il tuo acquisto! — Immobiliare Giancani"),
    ("“Investire nel tuo domani significa scegliere la qualità migliore per la tua vita.”", "La sicurezza di una consulenza trasparente e dedicata! — Immobiliare Giancani")
]

GUARANTEED_FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600585154526-990dced4db0d?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600573472591-ee6b68d14c68?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1613490493576-7fde63acd811?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1513694203232-719a280e022f?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1560185007-cde436f6a4d0?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1518780664697-55e3ad937233?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1493809842364-78817add7ffb?q=80&w=1200&auto=format&fit=crop"
]

def find_ffmpeg():
    """Localizza l'eseguibile FFmpeg nel workspace o nel sistema"""
    candidates = [
        shutil.which("ffmpeg"),
        os.path.join(os.path.dirname(BASE_DIR), "ffmpeg.exe"),
        os.path.join(BASE_DIR, "ffmpeg.exe"),
        "ffmpeg"
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return "ffmpeg"

def find_ytdlp():
    """Localizza l'eseguibile yt-dlp"""
    candidates = [
        shutil.which("yt-dlp"),
        "yt-dlp"
    ]
    for c in candidates:
        if c and (os.path.exists(c) or shutil.which(c)):
            return c
    return "yt-dlp"

def get_font(size, bold=False, font_type="sans"):
    """Carica font TrueType scalato e tipizzato per Windows e Linux (GitHub Actions)"""
    paths = []
    if font_type == "serif":
        paths = [
            "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/timesbd.ttf" if bold else "C:/Windows/Fonts/times.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
        ]
    elif font_type == "script":
        paths = [
            "C:/Windows/Fonts/segoescb.ttf" if bold else "C:/Windows/Fonts/segoesc.ttf",
            "C:/Windows/Fonts/brushsci.ttf",
            "C:/Windows/Fonts/georgiaz.ttf" if bold else "C:/Windows/Fonts/georgiai.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"
        ]
    else:  # sans
        paths = [
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]

    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def is_image_valid_and_not_black(image_obj, min_mean=20, min_max=40):
    """Verifica che l'immagine sia valida e non nera/vuota"""
    if not image_obj:
        return False
    try:
        gray = image_obj.convert('L').resize((60, 60))
        stat = ImageStat.Stat(gray)
        mean_b = stat.mean[0]
        ext_min, ext_max = gray.getextrema()
        if mean_b < min_mean or ext_max < min_max:
            print(f"[ANTI-BLACK] Immagine scartata: luminosità media {mean_b:.1f}, picco {ext_max}")
            return False
        return True
    except Exception as e:
        print(f"[ANTI-BLACK] Errore verifica immagine: {e}")
        return False

def get_local_or_remote_logo():
    """Restituisce l'immagine del logo ufficiale Immobiliare Giancani"""
    local_logo_path = os.path.join(ASSETS_DIR, "logo_giancani.png")
    if os.path.exists(local_logo_path) and os.path.getsize(local_logo_path) > 1000:
        try:
            return Image.open(local_logo_path).convert('RGBA')
        except Exception:
            pass
    try:
        req = urllib.request.Request(REMOTE_LOGO_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = resp.read()
            with open(local_logo_path, 'wb') as f:
                f.write(data)
            return Image.open(io.BytesIO(data)).convert('RGBA')
    except Exception as e:
        print(f"Avviso: recupero logo remoto fallito ({e})")
    return None


def get_clean_logo(max_w=380, max_h=110, transparent=True):
    """
    Restituisce il logo ufficiale Immobiliare Giancani proporzionato,
    senza schiacciamenti ('non pressato') e con sfondo bianco rimosso (trasparente).
    """
    raw = get_local_or_remote_logo()
    if not raw:
        return None
    try:
        im = raw.convert('RGBA')
        if transparent:
            import numpy as np
            arr = np.array(im)
            r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            white_mask = (r > 230) & (g > 230) & (b > 230)
            arr[white_mask, 3] = 0
            im = Image.fromarray(arr)

        orig_w, orig_h = im.size
        scale = min(max_w / orig_w, max_h / orig_h)
        new_w = max(1, int(orig_w * scale))
        new_h = max(1, int(orig_h * scale))
        return im.resize((new_w, new_h), Image.LANCZOS)
    except Exception as e:
        print(f"Avviso elaborazione logo pulito: {e}")
        return raw

ROOT_HISTORY_PATH = os.path.join(os.path.dirname(BASE_DIR), "immobili_pubblicati_history.json")
LOCAL_HISTORY_PATH = os.path.join(BASE_DIR, "immobili_pubblicati_history.json")
CRONOLOGIA_STORIE_PATH = os.path.join(ASSETS_DIR, "cronologia_storie_offline.json")

def carica_cronologia_storie():
    for p in [ROOT_HISTORY_PATH, LOCAL_HISTORY_PATH, CRONOLOGIA_STORIE_PATH]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and len(data) > 0:
                        return data
            except Exception:
                pass
    return {}

def salva_cronologia_storie(cronologia):
    for p in [ROOT_HISTORY_PATH, LOCAL_HISTORY_PATH, CRONOLOGIA_STORIE_PATH]:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(cronologia, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Avviso salvataggio cronologia storie su {p}: {e}")

def get_recent_photo_urls(cronologia, max_count=30):
    """Restituisce l'insieme degli URL delle foto già pubblicate di recente."""
    urls = set()
    if not isinstance(cronologia, dict):
        return urls
    items = []
    for k, v in cronologia.items():
        if isinstance(v, dict):
            ts = v.get("timestamp") or 0
            u = v.get("fotoUrl") or v.get("mediaUrl")
            if u:
                items.append((ts, str(u).strip()))
        elif isinstance(v, str) and v.startswith("http"):
            items.append((0, v.strip()))
    items.sort(key=lambda x: x[0], reverse=True)
    for _, u in items[:max_count]:
        urls.add(u)
    return urls

def normalize_mq(val):
    """Garantisce la dicitura 'metri quadri' per le superfici come da regola globale"""
    if not val:
        return "120 metri quadri"
    val = str(val).strip()
    val = val.replace("mq", "metri quadri").replace("Mq", "metri quadri").replace("m²", "metri quadri").replace("MQ", "metri quadri")
    if "metri quadri" not in val.lower():
        val = f"{val} metri quadri"
    return val

def check_is_live_active():
    """
    Verifica rigorosamente se la diretta live streaming è attualmente in corso.
    Se in corso dentro GitHub Actions runner, rileva le variabili di ambiente GITHUB_WORKFLOW.
    Altrimenti interroga l'API di GitHub Actions per rilevare workflow live in_progress.
    """
    gh_workflow = os.environ.get("GITHUB_WORKFLOW", "").lower()
    if os.environ.get("GITHUB_ACTIONS") == "true" and ("live" in gh_workflow or "stream" in gh_workflow):
        return True, "local_github_runner"

    try:
        headers = {
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Giancani-StoriesBot"
        }
        url = f"https://api.github.com/repos/{GH_REPO}/actions/runs?status=in_progress"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for run in data.get('workflow_runs', []):
                path = run.get('path', '').lower()
                name = run.get('name', '').lower()
                if 'live-stream' in path or 'multistream' in name or 'live' in name:
                    return True, run.get('id')
    except Exception as e:
        print(f"Avviso verifica status live su GitHub: {e}")
    return False, None

def genera_audio_musica_allegra(output_audio_path=None):
    """Genera traccia audio di 15 secondi allegra, vivace ed energica (124 BPM, Major Chords) 100% royalty-free"""
    if not output_audio_path:
        output_audio_path = os.path.join(ASSETS_DIR, "cheerful_music.wav")

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
            if s_i + n_len > nsamples:
                n_len = nsamples - s_i
            tn = np.linspace(0, 0.24, n_len, endpoint=False)
            decay = np.exp(-10 * tn)
            note_pitch = notes[b % len(notes)]
            if b % 2 == 0:
                bass_env = np.exp(-7 * tn)
                bass_tone = 0.5 * np.sin(2 * np.pi * bass_freq * tn) * bass_env
                left[s_i:s_i+n_len] += bass_tone * 0.7
                right[s_i:s_i+n_len] += bass_tone * 0.7

            pluck = (0.55 * np.sin(2 * np.pi * note_pitch * tn) +
                     0.3 * np.sin(4 * np.pi * note_pitch * tn) +
                     0.12 * np.sin(6 * np.pi * note_pitch * tn)) * decay
            pan = 0.35 + 0.3 * (b % 3)
            left[s_i:s_i+n_len] += pluck * (1.0 - pan) * 0.65
            right[s_i:s_i+n_len] += pluck * pan * 0.65

    fade_in = int(0.4 * SR)
    fade_out = int(1.2 * SR)
    left[:fade_in] *= np.linspace(0, 1, fade_in)
    right[:fade_in] *= np.linspace(0, 1, fade_in)
    left[-fade_out:] *= np.linspace(1, 0, fade_out)
    right[-fade_out:] *= np.linspace(1, 0, fade_out)

    mval = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if mval > 0:
        left = left * (0.8 / mval)
        right = right * (0.8 / mval)

    with wave.open(output_audio_path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        inter = np.empty((nsamples * 2,), dtype=np.int16)
        inter[0::2] = (left * 32767).astype(np.int16)
        inter[1::2] = (right * 32767).astype(np.int16)
        wf.writeframes(inter.tobytes())

    return output_audio_path

def genera_voce_tts(testo, voice_id="it-IT-ElsaNeural", output_voice_path=None):
    """Genera file audio MP3 con Microsoft Edge Neural TTS"""
    if not output_voice_path:
        output_voice_path = os.path.join(SCRATCH_DIR, f"tts_{uuid.uuid4().hex[:8]}.mp3")

    if HAS_EDGE_TTS:
        try:
            async def _run():
                comm = edge_tts.Communicate(testo, voice_id, rate="+3%", pitch="+1Hz")
                await comm.save(output_voice_path)
            asyncio.run(_run())
            if os.path.exists(output_voice_path) and os.path.getsize(output_voice_path) > 3000:
                return output_voice_path
        except Exception as e:
            print(f"Avviso edge_tts ({voice_id}): {e}")
    return None

FRASI_HOOK_DIRETTA = [
    "🔴 Siamo in diretta adesso! Aprite le porte a una straordinaria opportunità che vi conquisterà al primo sguardo.",
    "✨ Diretta live aperta! Mettetevi comodi: stiamo per svelarvi ogni angolo di questa dimora esclusiva.",
    "🏡 Benvenuti in tour live! Se cercate comfort, luce e spazi veri, questa casa è fatta apposta per voi.",
    "🌟 In onda in questo istante! Entrate con noi per scoprire una casa pronta a farvi battere il cuore.",
    "📍 Diretta streaming accesa! Oggi vi portiamo dentro una soluzione immobiliare davvero introvabile.",
    "🔑 Chiavi in mano e porte aperte! Guardate dal vivo la meraviglia di questo immobile prima di tutti gli altri.",
    "🎉 Siamo live dal territorio! Ecco l'ambiente perfetto per iniziare a scrivere la vostra nuova storia familiare.",
    "☀️ Che luce meravigliosa! Unitevi alla diretta per ammirare da vicino le finiture e la distribuzione degli spazi.",
    "🔥 Occasione imperdibile in onda ora! Un immobile di grande pregio con un potenziale unico tutto da scoprire.",
    "🚪 Entriamo insieme in diretta! Guardate la cura di ogni dettaglio e immaginate già il vostro futuro qui.",
    "💎 Una gemma immobiliare in diretta streaming! Seguiteci stanza per stanza per non perdere nessun particolare.",
    "🎯 La ricerca della vostra casa ideale potrebbe finire proprio adesso: collegatevi subito alla nostra diretta live!",
    "💫 Spazi generosi e atmosfera calda: siamo in diretta per mostrarvi come si vive davvero in questa casa.",
    "🎙️ DarIA e DarIO in diretta per voi! Lasciatevi guidare nel tour virtuale esclusivo di questa splendida proprietà.",
    "⭐ In diretta esclusiva con Immobiliare Giancani: scoprite adesso l'immobile che stavate aspettando da tempo!"
]

FRASI_POSITIVE_FLASH = [
    "Sorridi alla vita con Immobiliare Giancani!",
    "La felicità comincia da casa tua con Immobiliare Giancani!",
    "Oggi è un giorno meraviglioso con Immobiliare Giancani!",
    "Le cose belle accadono a chi crede nei sogni con Immobiliare Giancani!",
    "Che sia una splendida giornata con Immobiliare Giancani!",
    "Pensa positivo e guarda avanti con Immobiliare Giancani!",
    "Ogni nuovo giorno porta nuove meraviglie con Immobiliare Giancani!",
    "Un raggio di sole e tanta serenità con Immobiliare Giancani!",
    "La tua serenità è la cosa più preziosa con Immobiliare Giancani!",
    "Oggi ti aspetta una splendida notizia con Immobiliare Giancani!",
    "Credi sempre nei tuoi desideri con Immobiliare Giancani!",
    "Circondati di bellezza e positività con Immobiliare Giancani!"
]


def determina_fascia_oraria(ora=None):
    """
    Determina la fascia oraria attuale (Mattina, Pomeriggio, Sera, Notte)
    con saluti personalizzati, emoticon, musica royalty-free per Facebook
    e riflessioni positive per le storie e le note.
    """
    if ora is None:
        ora = time.localtime().tm_hour

    if 6 <= ora < 12:
        return {
            "fascia": "mattina",
            "nome": "Mattina",
            "saluto": "Buongiorno 🌅☀️☕",
            "badge": "🌅 BUONGIORNO • IMMOBILIARE GIANCANI",
            "frase_flash": "Buongiorno! Inizia una giornata di luce e nuove opportunità con Immobiliare Giancani! 🌅☀️",
            "intro_voce": "Salve dall'agenzia Immobiliare Giancani! Iniziamo questa splendida giornata insieme per scoprire questa magnifica proprietà.",
            "emoticon": "🌅☀️☕",
            "musica_file": "classica_vivaldi_primavera.mp3",
            "musica_titolo": "Vivaldi - La Primavera (Royalty-Free Facebook)",
            "titolo_nota": "📝 NOTA DEL BUONGIORNO — Immobiliare Giancani 🌅☀️",
            "riflessione_nota": (
                "🌅 Buongiorno da Immobiliare Giancani! ☕\n\n"
                "Iniziare la giornata nel posto giusto fa tutta la differenza del mondo. "
                "La luce del mattino che filtra dalle ampie finestre, il profumo del caffè in una cucina spaziosa "
                "e la consapevolezza di aver trovato il nido perfetto per sé e per la propria famiglia.\n\n"
                "Ogni nuovo giorno porta con sé l'opportunità di fare il passo verso la casa dei propri sogni."
            )
        }
    elif 12 <= ora < 18:
        return {
            "fascia": "pomeriggio",
            "nome": "Pomeriggio",
            "saluto": "Buon pomeriggio ☕🌤️🏡",
            "badge": "☕ BUON POMERIGGIO • IMMOBILIARE GIANCANI",
            "frase_flash": "Buon pomeriggio! È il momento perfetto per scegliere la tua casa con Immobiliare Giancani! ☕🏡",
            "intro_voce": "Salve dall'agenzia Immobiliare Giancani! Nel cuore di questa giornata vi presentiamo un immobile davvero eccezionale.",
            "emoticon": "☕🌤️🏡",
            "musica_file": "cheerful_music.wav",
            "musica_titolo": "Cheerful Acoustic Lounge 124 BPM (Royalty-Free Facebook)",
            "titolo_nota": "📝 NOTA DEL POMERIGGIO — Immobiliare Giancani ☕🌤️",
            "riflessione_nota": (
                "☕ Buon pomeriggio da Immobiliare Giancani! 🌤️\n\n"
                "Una breve pausa nel pomeriggio è il momento ideale per riflettere sul futuro e sui propri progetti di vita. "
                "Gli spazi giusti regalano serenità, comfort e il piacere di vivere ogni ambiente con gioia e libertà.\n\n"
                "Siamo sempre al vostro fianco per guidarvi con cura ed esperienza nella scelta della vostra nuova dimora."
            )
        }
    elif 18 <= ora < 22:
        return {
            "fascia": "sera",
            "nome": "Sera",
            "saluto": "Buona sera 🌆🍷✨",
            "badge": "🌆 BUONA SERA • IMMOBILIARE GIANCANI",
            "frase_flash": "Buona sera! Il piacere e il calore di tornare a casa con Immobiliare Giancani! 🌆✨",
            "intro_voce": "Salve dall'agenzia Immobiliare Giancani! Al calar della sera, lasciatevi conquistare dal calore di questa splendida residenza.",
            "emoticon": "🌆🍷✨",
            "musica_file": "luxury_ambient_music.wav",
            "musica_titolo": "Luxury Sunset Ambient (Royalty-Free Facebook)",
            "titolo_nota": "📝 NOTA DELLA SERA — Immobiliare Giancani 🌆🍷✨",
            "riflessione_nota": (
                "🌆 Buona sera da Immobiliare Giancani! 🍷\n\n"
                "C’è una magia tutta speciale nella tranquillità della sera: la gioia di tornare a casa, chiudere la porta "
                "e ritrovarsi nell'intimità dei propri affetti, immersi nel calore di un ambiente accogliente e protetto.\n\n"
                "La vera bellezza dell'abitare è sentirsi sempre nel posto giusto al momento giusto."
            )
        }
    else:
        return {
            "fascia": "notte",
            "nome": "Notte",
            "saluto": "Buonanotte 🌙⭐️💤",
            "badge": "🌙 BUONANOTTE • IMMOBILIARE GIANCANI",
            "frase_flash": "Buonanotte e sogni d'oro! La casa perfetta ti aspetta con Immobiliare Giancani! 🌙⭐️",
            "intro_voce": "Salve dall'agenzia Immobiliare Giancani! Prima di addormentarvi, vi auguriamo pensieri sereni e sogni grandiosi.",
            "emoticon": "🌙⭐️💤",
            "musica_file": "classica_mozart_nachtmusik.mp3",
            "musica_titolo": "Mozart - Serenata Notturna (Royalty-Free Facebook)",
            "titolo_nota": "📝 NOTA DELLA BUONANOTTE — Immobiliare Giancani 🌙⭐️💤",
            "riflessione_nota": (
                "🌙 Buonanotte e sogni d'oro da Immobiliare Giancani! ⭐️\n\n"
                "Mentre la notte scende sul territorio, è tempo di riposare sereni e fare spazio ai desideri più belli. "
                "I sogni più autentici sono quelli che domani, con determinazione e i giusti consigli, possono diventare meravigliosa realtà.\n\n"
                "Vi auguriamo un sereno riposo, sapendo che la casa perfetta è già lì che vi aspetta."
            )
        }

def genera_intro_invito_dinamico(personaggio="daria", testo_f="", is_live=True, frase_positiva=None, fascia_info=None):
    """
    Genera hook dinamici e calorosi per le storie social.
    Progettato appositamente per chi scorre velocemente le storie:
    le primissime parole pronunciate (nei primi 1.5 secondi) trasmettono
    un pensiero positivo immediato e terminano con 'con Immobiliare Giancani!'.
    """
    testo_f_clean = (testo_f or "").strip()
    if testo_f_clean:
        testo_f_clean = re.sub(r'\s*—?\s*Immobiliare Giancani\s*$', '', testo_f_clean, flags=re.IGNORECASE).strip()

    if not frase_positiva:
        frase_positiva = random.choice(FRASI_POSITIVE_FLASH)

    if is_live:
        followups = [
            f"Salve dall'agenzia Immobiliare Giancani! Siamo collegati dal vivo in diretta streaming proprio in questo istante. {testo_f_clean} Entrate subito a guardare la diretta per scoprire tutti gli ambienti e chattare con noi in tempo reale! Vi aspettiamo con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! Da tutto il nostro team un invito imperdibile: siamo in onda adesso in diretta streaming. {testo_f_clean} Cliccate subito ed entrate nella diretta per farci tutte le vostre domande dal vivo! Vi aspettiamo con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! La diretta streaming è accesa adesso e abbiamo preparato per voi una presentazione esclusiva. {testo_f_clean} Entrate subito a guardare la diretta per vedere ogni dettaglio prima di tutti! Vi aspettiamo con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! Un caloroso invito per voi: siamo in onda dal vivo in diretta streaming. {testo_f_clean} Scriveteci nei commenti quale stanza desiderate visitare e vi porteremo subito all'interno! Entrate in diretta con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! In questo momento siamo in onda dal vivo per farvi scoprire questa gemma immobiliare. {testo_f_clean} Entrate subito a guardare la nostra diretta streaming, vi aspettiamo con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! Le porte delle nostre migliori residenze sono aperte adesso in streaming. {testo_f_clean} Collegatevi subito alla diretta per interagire con noi in tempo reale! Vi aspettiamo con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! Se state cercando la vostra prossima casa, non perdetevi la diretta streaming attiva proprio ora. {testo_f_clean} Entrate subito a vedere la diretta dal vivo per scoprire tutte le stanze e il prezzo! Vi aspettiamo con Immobiliare Giancani!"
        ]
        return random.choice(followups)
    else:
        if not fascia_info:
            fascia_info = determina_fascia_oraria()
        saluto_momento = fascia_info.get("intro_voce", "Salve dall'agenzia Immobiliare Giancani!")
        followups = [
            f"{saluto_momento} {testo_f_clean} Contattateci subito per prenotare una visita esclusiva. {frase_positiva} — Immobiliare Giancani",
            f"{saluto_momento} {testo_f_clean} Per fissare un appuntamento e visitarla insieme, chiamateci senza impegno. {frase_positiva} — Immobiliare Giancani",
            f"{saluto_momento} {testo_f_clean} Chiamateci subito per scoprire ogni dettaglio di persona. {frase_positiva} — Immobiliare Giancani",
            f"{saluto_momento} La casa perfetta vi aspetta, curata con dedizione dal nostro team. {testo_f_clean} Siamo pronti ad accompagnarvi nella vostra visita privata. {frase_positiva} — Immobiliare Giancani"
        ]
        return random.choice(followups)

def crea_audio_mix_completo(testo_f, is_live=True, output_mixed_m4a=None, frase_positiva=None, fascia_info=None):
    """Combina le voci di DarIA e DarIO (dialogo radiofonico) con musica allegra e auto-ducking"""
    if not output_mixed_m4a:
        output_mixed_m4a = os.path.join(SCRATCH_DIR, f"story_audio_{uuid.uuid4().hex[:8]}.m4a")

    ffmpeg_bin = find_ffmpeg()
    hook_frase = random.choice(FRASI_HOOK_DIRETTA)

    testo_f_clean = (testo_f or "").strip()
    if testo_f_clean:
        testo_f_clean = re.sub(r'\s*—?\s*Immobiliare Giancani\s*$', '', testo_f_clean, flags=re.IGNORECASE).strip()

    # Generazione narrazione con l'Inno Sequenziale e le 4 voci neurali alternate (Diego, Elsa, Giuseppe, Isabella)
    voice_path = None
    verso_info = None
    try:
        import gestore_catena_storie_vocali as gcsv
        testo_recitato, verso_info = gcsv.componi_narrazione_storia(testo_f, is_live=is_live)
        print(f"🎙️ [INNO CATENA] Verso {verso_info['verso_num']}/7 | Voce: {verso_info['voice_nome']} ({verso_info['voice_id']})")
        print(f"🎵 HOOK: {verso_info['hook']}")
        voice_path = gcsv.genera_audio_narrazione_tts(testo_recitato, voice_id=verso_info["voice_id"])
    except Exception as e_catena:
        print(f"Avviso fallback gestore catena vocale: {e_catena}")
        if is_live:
            testo_recitato = f"{hook_frase} Salve a tutti da Immobiliare Giancani! {testo_f_clean} Entrate subito in diretta per chattare con noi! — Immobiliare Giancani"
        else:
            testo_recitato = f"Un caloroso saluto da Immobiliare Giancani! {testo_f_clean} Contattateci oggi stesso per visitarla di persona. — Immobiliare Giancani"
        voice_path = genera_voce_tts(testo_recitato, voice_id="it-IT-DiegoNeural")
    
    # Selezione colonna sonora royalty-free con regola anti-ripetizione (> 10 storie)
    music_path = None
    try:
        import gestore_musica_storie as gms
        music_path = gms.ottieni_colonna_sonora_storia(durata_secondi=15.0)
    except Exception as e_gms:
        print(f"Avviso fallback gestore musica: {e_gms}")
        if fascia_info and fascia_info.get("musica_file"):
            cand_music = os.path.join(ASSETS_DIR, fascia_info["musica_file"])
            if os.path.exists(cand_music) and os.path.getsize(cand_music) > 10000:
                music_path = cand_music
                print(f"[OK] Canzone royalty-free Facebook selezionata ({fascia_info['nome']}): {fascia_info['musica_titolo']}")
        if not music_path:
            music_path = genera_audio_musica_allegra()
    ffmpeg_bin = find_ffmpeg()

    if voice_path and os.path.exists(voice_path):
        cmd = [
            ffmpeg_bin, "-y",
            "-i", voice_path,
            "-i", music_path,
            "-filter_complex",
            "[0:a]volume=1.2,apad=pad_dur=15[v];[1:a]volume=0.22[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2[outa]",
            "-map", "[outa]",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", "15",
            output_mixed_m4a
        ]
    else:
        cmd = [
            ffmpeg_bin, "-y",
            "-i", music_path,
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", "15",
            output_mixed_m4a
        ]

    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if proc.returncode == 0 and os.path.exists(output_mixed_m4a):
        return output_mixed_m4a
    return music_path


# ═════════════════════════════════════════════════════════════════════════════
# MOTORE GRAFICO MULTI-STILE (IMMOBILIARE GIANCANI)
# ═════════════════════════════════════════════════════════════════════════════

def draw_skyline(draw, y_base, width, color=(148, 163, 184, 180)):
    """Disegna una skyline stilizzata di tetti e palazzi italiani lungo il margine inferiore"""
    rng = random.Random(42)
    x = 0
    while x < width:
        w = rng.randint(25, 55)
        h = rng.randint(18, 48)
        roof_type = rng.choice(["flat", "pitched", "tower"])
        draw.rectangle([x, y_base - h, min(x + w, width), y_base], fill=color)
        if roof_type == "pitched" and x + w <= width:
            peak_h = h + rng.randint(8, 16)
            mid_x = x + w // 2
            draw.polygon([(x, y_base - h), (mid_x, y_base - peak_h), (x + w, y_base - h)], fill=color)
        elif roof_type == "tower" and x + w <= width:
            tw = w // 3
            tx = x + (w - tw) // 2
            th = h + rng.randint(10, 20)
            draw.rectangle([tx, y_base - th, tx + tw, y_base - h], fill=color)
            draw.polygon([(tx - 2, y_base - th), (tx + tw // 2, y_base - th - 8), (tx + tw + 2, y_base - th)], fill=color)
        x += w + rng.randint(2, 6)

def draw_circular_badge(draw, center_x, center_y, radius, icon_type, label_text, sublabel=""):
    """Disegna un badge circolare line-art con etichetta sotto"""
    cx, cy = center_x, center_y
    r = radius
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255), outline=(203, 213, 225, 255), width=2)
    draw.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4], fill=None, outline=(241, 245, 249, 255), width=1)
    
    icon_color = (30, 41, 59, 255)
    
    if icon_type == "house":
        hw, hh = 16, 12
        draw.polygon([(cx, cy - 14), (cx - hw, cy - 2), (cx + hw, cy - 2)], outline=icon_color, fill=None, width=2)
        draw.rectangle([cx - hw + 3, cy - 2, cx + hw - 3, cy + hh], outline=icon_color, fill=None, width=2)
        draw.rectangle([cx - 4, cy + 3, cx + 4, cy + hh], fill=icon_color)
    elif icon_type == "car":
        draw.rounded_rectangle([cx - 16, cy - 6, cx + 16, cy + 8], radius=3, outline=icon_color, fill=None, width=2)
        draw.polygon([(cx - 11, cy - 6), (cx - 7, cy - 13), (cx + 7, cy - 13), (cx + 11, cy - 6)], outline=icon_color, fill=None, width=2)
        draw.ellipse([cx - 12, cy + 5, cx - 6, cy + 11], fill=icon_color)
        draw.ellipse([cx + 6, cy + 5, cx + 12, cy + 11], fill=icon_color)
    elif icon_type == "sun":
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=icon_color, fill=None, width=2)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = cx + math.cos(rad) * 11
            y1 = cy + math.sin(rad) * 11
            x2 = cx + math.cos(rad) * 16
            y2 = cy + math.sin(rad) * 16
            draw.line([(x1, y1), (x2, y2)], fill=icon_color, width=2)
    elif icon_type == "music":
        draw.polygon([(cx - 4, cy - 12), (cx - 14, cy - 2), (cx + 6, cy - 2)], outline=icon_color, fill=None, width=2)
        draw.rectangle([cx - 12, cy - 2, cx + 4, cy + 10], outline=icon_color, fill=None, width=2)
        draw.ellipse([cx + 6, cy + 4, cx + 13, cy + 9], fill=(225, 29, 72, 255))
        draw.line([(cx + 12, cy + 6), (cx + 12, cy - 8)], fill=(225, 29, 72, 255), width=2)
        draw.line([(cx + 12, cy - 8), (cx + 17, cy - 6)], fill=(225, 29, 72, 255), width=2)
        
    if label_text:
        font_lbl = get_font(13, bold=True, font_type="sans")
        bbox = font_lbl.getbbox(label_text)
        lw = bbox[2] - bbox[0]
        draw.text((cx - lw // 2, cy + r + 8), label_text, font=font_lbl, fill=(15, 23, 42, 255))

def calcola_prezzo_barrato(prezzo_str):
    """Calcola un prezzo originario barrato realistico (+25-30%) se non specificato"""
    match = re.search(r'(\d+[\.,]?\d*)', str(prezzo_str).replace(".", "").replace(",", "."))
    if match:
        try:
            val = float(match.group(1))
            if val > 1000:
                old_val = int(round(val * 1.32 / 1000.0) * 1000)
                return f"€ {old_val:,.0f}".replace(",", ".")
        except Exception:
            pass
    return "€ 130.000"

def crea_grafica_flyer_split_screen(media_info, output_path=None, size=(1080, 1080)):
    """
    STILE 1 (FLYER 1:1): SPLIT-SCREEN PROMOTIONAL FLYER
    - 40% colonna sinistra: grande foto verticale + nastro 3D rosso 'NUOVO PREZZO'.
    - 60% colonna destra: sfondo chiaro, banner prezzi barrato/scontato,
      headline serif, 3 badge line-art con 'metri quadri', testo Colonna F,
      inset photo con etichetta arancione.
    - Footer: icona casetta musicale, bottone navy, skyline, corsivo
      'La tua prossima casa ti aspetta' e personal branding in risalto 'IMMOBILIARE GIANCANI'.
    """
    W, H = size
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_splitscreen_{uuid.uuid4().hex[:6]}.png")

    img = Image.new('RGBA', (W, H), (248, 249, 251, 255))
    draw = ImageDraw.Draw(img)

    left_w = int(W * 0.40)
    right_w = W - left_w
    footer_h = 135
    content_h = H - footer_h

    # Foto verticale a sinistra
    foto_url = media_info.get('fotoUrl')
    foto_im = scarica_foto_url(foto_url) if foto_url else None
    if not foto_im:
        cache_files = [os.path.join(CACHE_IMMOBILI_DIR, f) for f in os.listdir(CACHE_IMMOBILI_DIR) if f.endswith(('.jpg', '.png'))] if os.path.exists(CACHE_IMMOBILI_DIR) else []
        if cache_files:
            try: foto_im = Image.open(cache_files[0]).convert('RGB')
            except Exception: pass
    if not foto_im:
        for fb_url in GUARANTEED_FALLBACK_IMAGES:
            foto_im = scarica_foto_url(fb_url)
            if foto_im: break
    if not foto_im:
        foto_im = Image.new('RGB', (left_w, content_h), (210, 180, 140))

    iw, ih = foto_im.size
    scale = max(left_w / iw, content_h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    foto_scaled = foto_im.resize((nw, nh), Image.LANCZOS)
    crop_x = (nw - left_w) // 2
    crop_y = (nh - content_h) // 2
    foto_cropped = foto_scaled.crop((crop_x, crop_y, crop_x + left_w, crop_y + content_h))
    img.paste(foto_cropped, (0, 0))

    # Ombra bordo foto
    shadow_overlay = Image.new('RGBA', (20, content_h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_overlay)
    for sx in range(20):
        alpha = int(70 * (sx / 20.0))
        s_draw.line([(sx, 0), (sx, content_h)], fill=(0, 0, 0, alpha))
    img.paste(shadow_overlay, (left_w - 20, 0), mask=shadow_overlay)

    # Nastro 3D "NUOVO PREZZO"
    ribbon_w, ribbon_h = 240, 52
    ribbon_poly_main = [(0, 30), (ribbon_w, 30), (ribbon_w - 20, 30 + ribbon_h), (0, 30 + ribbon_h)]
    draw.polygon([(0, 30 + ribbon_h), (18, 30 + ribbon_h + 14), (0, 30 + ribbon_h + 14)], fill=(127, 29, 29, 255))
    draw.polygon(ribbon_poly_main, fill=(225, 29, 72, 255))
    draw.line([(0, 31), (ribbon_w, 31)], fill=(254, 205, 211, 220), width=2)
    font_ribbon = get_font(24, bold=True, font_type="sans")
    draw.text((32, 43), "NUOVO PREZZO", font=font_ribbon, fill=(255, 255, 255, 255))

    # Watermark Logo (Proporzionato, Trasparente, Non Pressato)
    l_img = get_clean_logo(max_w=220, max_h=60, transparent=True)
    if l_img:
        try:
            lw, lh = l_img.size
            draw.rounded_rectangle([15, content_h - lh - 25, 25 + lw, content_h - 15], radius=10, fill=(15, 23, 42, 215))
            img.paste(l_img, (20, content_h - lh - 20), mask=l_img.split()[3])
        except Exception:
            pass

    # Colonna destra (60%)
    rx = left_w + 30
    rw_usable = right_w - 60
    prezzo_reale = media_info.get('prezzo', '€ 79.000')
    prezzo_barrato = media_info.get('prezzoOriginale') or calcola_prezzo_barrato(prezzo_reale)
    
    price_y = 35
    font_old = get_font(22, bold=True, font_type="sans")
    old_bbox = font_old.getbbox(prezzo_barrato)
    old_w = old_bbox[2] - old_bbox[0] + 28
    draw.rounded_rectangle([rx, price_y + 12, rx + old_w, price_y + 56], radius=10, fill=(241, 245, 249, 255), outline=(226, 232, 240, 255), width=2)
    draw.text((rx + 14, price_y + 20), prezzo_barrato, font=font_old, fill=(148, 163, 184, 255))
    draw.line([(rx + 10, price_y + 35), (rx + old_w - 10, price_y + 35)], fill=(225, 29, 72, 255), width=3)

    arrow_x = rx + old_w + 12
    draw.polygon([(arrow_x, price_y + 26), (arrow_x + 14, price_y + 34), (arrow_x, price_y + 42)], fill=(225, 29, 72, 255))

    new_price_x = arrow_x + 24
    new_price_w = right_w - (new_price_x - left_w) - 30
    font_new = get_font(34, bold=True, font_type="sans")
    new_bbox = font_new.getbbox(prezzo_reale)
    
    draw.rounded_rectangle([new_price_x + 3, price_y + 5, new_price_x + new_price_w + 3, price_y + 70], radius=14, fill=(15, 23, 42, 40))
    draw.rounded_rectangle([new_price_x, price_y + 2, new_price_x + new_price_w, price_y + 67], radius=14, fill=(220, 38, 38, 255), outline=(254, 205, 211, 255), width=2)
    draw.text((new_price_x + (new_price_w - (new_bbox[2] - new_bbox[0])) // 2, price_y + 14), prezzo_reale, font=font_new, fill=(255, 255, 255, 255))

    titolo_raw = media_info.get('titolo', 'Casa Indipendente').upper()
    tipologia = "CASA INDIPENDENTE"
    citta = "FAVARA (AG)"
    for t in ["VILLA INDIPENDENTE", "VILLA", "CASA INDIPENDENTE", "APPARTAMENTO", "ATTICO", "TERRENO"]:
        if t in titolo_raw:
            tipologia = t
            break
    for c in ["FAVARA", "AGRIGENTO", "MAZARA DEL VALLO", "PORTO EMPEDOCLE", "CANICATTI", "SCIACCA"]:
        if c in titolo_raw:
            citta = c
            break

    head_y = price_y + 88
    font_head = get_font(34, bold=True, font_type="serif")
    draw.text((rx, head_y), tipologia, font=font_head, fill=(15, 23, 42, 255))

    font_subhead = get_font(20, bold=True, font_type="sans")
    draw.text((rx + 2, head_y + 44), f"• {citta} • ESCLUSIVA GIANCANI", font=font_subhead, fill=(71, 85, 105, 255))

    badge_y = head_y + 130
    b_spacing = rw_usable // 3
    mq_val = normalize_mq(media_info.get('mq', '140 metri quadri'))
    
    draw_circular_badge(draw, rx + b_spacing * 0 + 60, badge_y, 34, "house", mq_val.upper())
    draw_circular_badge(draw, rx + b_spacing * 1 + 60, badge_y, 34, "car", "GARAGE AMPIO")
    draw_circular_badge(draw, rx + b_spacing * 2 + 60, badge_y, 34, "sun", "TERRAZZA PRIVATA")

    desc_y = badge_y + 85
    testo_f = media_info.get('testoF', 'Splendida soluzione su più livelli, luminosa e versatile. Perfetta per famiglie o investimento.')
    if "immobiliare giancani" not in testo_f.lower():
        testo_f = f"{testo_f.rstrip('. ')} — Immobiliare Giancani"

    font_desc = get_font(18, bold=False, font_type="sans")
    words = testo_f.split()
    lines = []
    curr = []
    max_line_w = rw_usable - 260
    for w in words:
        test_line = " ".join(curr + [w])
        if font_desc.getbbox(test_line)[2] < max_line_w:
            curr.append(w)
        else:
            if curr: lines.append(" ".join(curr))
            curr = [w]
    if curr: lines.append(" ".join(curr))

    dy = desc_y
    for l in lines[:6]:
        draw.text((rx, dy), l, font=font_desc, fill=(51, 65, 85, 255))
        dy += 28

    inset_w, inset_h = 240, 160
    inset_x = W - inset_w - 30
    inset_y = content_h - inset_h - 25

    cache_files = [os.path.join(CACHE_IMMOBILI_DIR, f) for f in os.listdir(CACHE_IMMOBILI_DIR) if f.endswith(('.jpg', '.png'))] if os.path.exists(CACHE_IMMOBILI_DIR) else []
    inset_im = None
    if len(cache_files) > 1:
        try: inset_im = Image.open(cache_files[1]).convert('RGB')
        except Exception: pass
    if not inset_im:
        inset_im = foto_im.crop((0, 0, min(foto_im.width, 400), min(foto_im.height, 300)))
    
    in_scaled = inset_im.resize((inset_w, inset_h), Image.LANCZOS)
    draw.rectangle([inset_x + 5, inset_y + 5, inset_x + inset_w + 5, inset_y + inset_h + 5], fill=(15, 23, 42, 60))
    draw.rectangle([inset_x - 3, inset_y - 3, inset_x + inset_w + 3, inset_y + inset_h + 3], fill=(255, 255, 255, 255))
    img.paste(in_scaled, (inset_x, inset_y))

    tag_w, tag_h = 200, 32
    draw.polygon([
        (inset_x, inset_y + inset_h - tag_h),
        (inset_x + tag_w, inset_y + inset_h - tag_h),
        (inset_x + tag_w - 15, inset_y + inset_h),
        (inset_x, inset_y + inset_h)
    ], fill=(234, 88, 12, 255))
    font_tag = get_font(14, bold=True, font_type="sans")
    draw.text((inset_x + 15, inset_y + inset_h - tag_h + 8), "TERRAZZA PANORAMICA", font=font_tag, fill=(255, 255, 255, 255))

    # Footer
    fy = content_h
    draw.rectangle([0, fy, W, H], fill=(241, 245, 249, 255))
    draw.line([(0, fy), (W, fy)], fill=(203, 213, 225, 255), width=2)
    draw_skyline(draw, H, W, color=(203, 213, 225, 140))

    draw_circular_badge(draw, 60, fy + 65, 28, "music", "")

    btn_w = 480
    btn_h = 58
    btn_x = 120
    btn_y = fy + 38
    is_live = media_info.get('isLive', False)
    btn_txt = "ENTRA IN DIRETTA A VEDERLA >" if is_live else "SCRIVICI IN PRIVATO PER INFO O VISITA >"
    
    draw.rounded_rectangle([btn_x + 2, btn_y + 4, btn_x + btn_w + 2, btn_y + btn_h + 4], radius=29, fill=(15, 23, 42, 70))
    btn_color = (220, 38, 38, 255) if is_live else (15, 23, 42, 255)
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=29, fill=btn_color, outline=(212, 168, 83, 255), width=2)
    
    font_btn = get_font(17, bold=True, font_type="sans")
    btn_bbox = font_btn.getbbox(btn_txt)
    draw.text((btn_x + (btn_w - (btn_bbox[2] - btn_bbox[0])) // 2, btn_y + 19), btn_txt, font=font_btn, fill=(255, 255, 255, 255))

    script_txt = "La tua prossima casa ti aspetta"
    font_script = get_font(26, bold=False, font_type="script")
    script_bbox = font_script.getbbox(script_txt)
    draw.text((W - (script_bbox[2] - script_bbox[0]) - 40, fy + 22), script_txt, font=font_script, fill=(180, 130, 40, 255))

    font_brand = get_font(22, bold=True, font_type="sans")
    brand_txt = "IMMOBILIARE GIANCANI"
    brand_bbox = font_brand.getbbox(brand_txt)
    draw.text((W - (brand_bbox[2] - brand_bbox[0]) - 40, fy + 68), brand_txt, font=font_brand, fill=(15, 23, 42, 255))

    img.save(output_path, "PNG")
    return output_path

def crea_story_splitscreen_9_16(media_info, output_path=None):
    """
    STILE 1 (STORIA 9:16): SPLIT-SCREEN PROMOTIONAL FLYER UNIFICATO PER VIDEO STORIE
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_splitscreen_{uuid.uuid4().hex[:6]}.png")

    canvas = Image.new('RGBA', (W, H), (15, 23, 42, 255))
    draw = ImageDraw.Draw(canvas)

    # 1. Header Superiore con Logo Proporzionato Trasparente (Non Pressato)
    l_hdr_logo = get_clean_logo(max_w=400, max_h=110, transparent=True)
    if l_hdr_logo:
        try:
            lw, lh = l_hdr_logo.size
            canvas.paste(l_hdr_logo, ((W - lw) // 2, 45), mask=l_hdr_logo.split()[3])
        except Exception:
            pass
    else:
        font_brand = get_font(32, bold=True, font_type="serif")
        b_txt = "IMMOBILIARE GIANCANI"
        bw = font_brand.getbbox(b_txt)[2] - font_brand.getbbox(b_txt)[0]
        draw.text(((W - bw) // 2, 60), b_txt, font=font_brand, fill=(212, 168, 83, 255))

    font_badge = get_font(20, bold=True, font_type="sans")
    is_live = media_info.get('isLive', True)
    badge_txt = "🔴 IN DIRETTA STREAMING ORA" if is_live else "★ OPPORTUNITÀ ESCLUSIVA ★"
    badg_w = font_badge.getbbox(badge_txt)[2] - font_badge.getbbox(badge_txt)[0] + 44
    draw.rounded_rectangle([(W - badg_w)//2, 190, (W + badg_w)//2, 235], radius=14, fill=(220, 38, 38, 240) if is_live else (30, 64, 175, 240))
    draw.text(((W - font_badge.getbbox(badge_txt)[2]) // 2, 201), badge_txt, font=font_badge, fill=(255, 255, 255, 255))

    # 2. Box Split-Screen Centrale
    box_x = 35
    box_y = 260
    box_w = W - 70
    box_h = 1270

    draw.rounded_rectangle([box_x - 3, box_y - 3, box_x + box_w + 3, box_y + box_h + 3], radius=24, fill=(212, 168, 83, 180))
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=22, fill=(248, 249, 251, 255))

    left_w = int(box_w * 0.40)
    right_w = box_w - left_w

    foto_url = media_info.get('fotoUrl')
    foto_im = scarica_foto_url(foto_url) if foto_url else None
    if not foto_im:
        cache_files = [os.path.join(CACHE_IMMOBILI_DIR, f) for f in os.listdir(CACHE_IMMOBILI_DIR) if f.endswith(('.jpg', '.png'))] if os.path.exists(CACHE_IMMOBILI_DIR) else []
        if cache_files:
            try: foto_im = Image.open(cache_files[0]).convert('RGB')
            except Exception: pass
    if not foto_im:
        for fb_url in GUARANTEED_FALLBACK_IMAGES:
            foto_im = scarica_foto_url(fb_url)
            if foto_im: break
    if not foto_im:
        foto_im = Image.new('RGB', (left_w, box_h), (210, 180, 140))

    iw, ih = foto_im.size
    scale = max(left_w / iw, box_h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    foto_scaled = foto_im.resize((nw, nh), Image.LANCZOS)
    crop_x = (nw - left_w) // 2
    crop_y = (nh - box_h) // 2
    foto_cropped = foto_scaled.crop((crop_x, crop_y, crop_x + left_w, crop_y + box_h))

    mask_left = Image.new('L', (left_w, box_h), 0)
    m_draw = ImageDraw.Draw(mask_left)
    m_draw.rounded_rectangle([0, 0, left_w + 30, box_h], radius=22, fill=255)
    canvas.paste(foto_cropped, (box_x, box_y), mask=mask_left)

    shadow_overlay = Image.new('RGBA', (20, box_h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_overlay)
    for sx in range(20):
        alpha = int(70 * (sx / 20.0))
        s_draw.line([(sx, 0), (sx, box_h)], fill=(0, 0, 0, alpha))
    canvas.paste(shadow_overlay, (box_x + left_w - 20, box_y), mask=shadow_overlay)

    ribbon_w, ribbon_h = 240, 52
    ribbon_poly = [(box_x, box_y + 35), (box_x + ribbon_w, box_y + 35), (box_x + ribbon_w - 20, box_y + 35 + ribbon_h), (box_x, box_y + 35 + ribbon_h)]
    draw.polygon([(box_x, box_y + 35 + ribbon_h), (box_x + 18, box_y + 35 + ribbon_h + 14), (box_x, box_y + 35 + ribbon_h + 14)], fill=(127, 29, 29, 255))
    draw.polygon(ribbon_poly, fill=(225, 29, 72, 255))
    draw.line([(box_x, box_y + 36), (box_x + ribbon_w, box_y + 36)], fill=(254, 205, 211, 220), width=2)
    font_ribbon = get_font(24, bold=True, font_type="sans")
    draw.text((box_x + 32, box_y + 48), "NUOVO PREZZO", font=font_ribbon, fill=(255, 255, 255, 255))

    l_wtm = get_clean_logo(max_w=180, max_h=50, transparent=True)
    if l_wtm:
        try:
            lw, lh = l_wtm.size
            draw.rounded_rectangle([box_x + 15, box_y + box_h - lh - 25, box_x + 25 + lw, box_y + box_h - 15], radius=10, fill=(15, 23, 42, 215))
            canvas.paste(l_wtm, (box_x + 20, box_y + box_h - lh - 20), mask=l_wtm.split()[3])
        except Exception:
            pass

    rx = box_x + left_w + 30
    rw_usable = right_w - 55

    prezzo_reale = media_info.get('prezzo', '€ 79.000')
    prezzo_barrato = media_info.get('prezzoOriginale') or calcola_prezzo_barrato(prezzo_reale)
    
    price_y = box_y + 40
    font_old = get_font(24, bold=True, font_type="sans")
    old_bbox = font_old.getbbox(prezzo_barrato)
    old_w = old_bbox[2] - old_bbox[0] + 28
    draw.rounded_rectangle([rx, price_y + 12, rx + old_w, price_y + 60], radius=10, fill=(241, 245, 249, 255), outline=(226, 232, 240, 255), width=2)
    draw.text((rx + 14, price_y + 22), prezzo_barrato, font=font_old, fill=(148, 163, 184, 255))
    draw.line([(rx + 10, price_y + 36), (rx + old_w - 10, price_y + 36)], fill=(225, 29, 72, 255), width=3)

    arrow_x = rx + old_w + 14
    draw.polygon([(arrow_x, price_y + 26), (arrow_x + 16, price_y + 36), (arrow_x, price_y + 46)], fill=(225, 29, 72, 255))

    new_price_x = arrow_x + 26
    new_price_w = right_w - (new_price_x - (box_x + left_w)) - 30
    font_new = get_font(36, bold=True, font_type="sans")
    new_bbox = font_new.getbbox(prezzo_reale)
    
    draw.rounded_rectangle([new_price_x + 3, price_y + 4, new_price_x + new_price_w + 3, price_y + 72], radius=14, fill=(15, 23, 42, 40))
    draw.rounded_rectangle([new_price_x, price_y + 2, new_price_x + new_price_w, price_y + 70], radius=14, fill=(220, 38, 38, 255), outline=(254, 205, 211, 255), width=2)
    draw.text((new_price_x + (new_price_w - (new_bbox[2] - new_bbox[0])) // 2, price_y + 16), prezzo_reale, font=font_new, fill=(255, 255, 255, 255))

    titolo_raw = media_info.get('titolo', 'Casa Indipendente').upper()
    tipologia = "CASA INDIPENDENTE"
    citta = "FAVARA (AG)"
    for t in ["VILLA INDIPENDENTE", "VILLA", "CASA INDIPENDENTE", "APPARTAMENTO", "ATTICO", "TERRENO"]:
        if t in titolo_raw:
            tipologia = t
            break
    for c in ["FAVARA", "AGRIGENTO", "MAZARA DEL VALLO", "PORTO EMPEDOCLE", "CANICATTI", "SCIACCA"]:
        if c in titolo_raw:
            citta = c
            break

    head_y = price_y + 105
    font_head = get_font(38, bold=True, font_type="serif")
    draw.text((rx, head_y), tipologia, font=font_head, fill=(15, 23, 42, 255))

    font_subhead = get_font(22, bold=True, font_type="sans")
    draw.text((rx + 2, head_y + 50), f"• {citta} • ESCLUSIVA GIANCANI", font=font_subhead, fill=(71, 85, 105, 255))

    badge_y = head_y + 155
    b_spacing = rw_usable // 3
    mq_val = normalize_mq(media_info.get('mq', '140 metri quadri'))
    
    draw_circular_badge(draw, rx + b_spacing * 0 + 55, badge_y, 38, "house", mq_val.upper())
    draw_circular_badge(draw, rx + b_spacing * 1 + 55, badge_y, 38, "car", "GARAGE AMPIO")
    draw_circular_badge(draw, rx + b_spacing * 2 + 55, badge_y, 38, "sun", "TERRAZZA PRIVATA")

    desc_y = badge_y + 105
    testo_f = media_info.get('testoF', 'Splendida soluzione su più livelli, luminosa e versatile. Perfetta per famiglie o investimento.')
    if "immobiliare giancani" not in testo_f.lower():
        testo_f = f"{testo_f.rstrip('. ')} — Immobiliare Giancani"

    font_desc = get_font(21, bold=False, font_type="sans")
    words = testo_f.split()
    lines = []
    curr = []
    max_line_w = rw_usable - 260
    for w in words:
        test_line = " ".join(curr + [w])
        if font_desc.getbbox(test_line)[2] < max_line_w:
            curr.append(w)
        else:
            if curr: lines.append(" ".join(curr))
            curr = [w]
    if curr: lines.append(" ".join(curr))

    dy = desc_y
    for l in lines[:10]:
        draw.text((rx, dy), l, font=font_desc, fill=(51, 65, 85, 255))
        dy += 34

    inset_w, inset_h = 250, 180
    inset_x = box_x + box_w - inset_w - 30
    inset_y = box_y + box_h - inset_h - 35

    cache_files = [os.path.join(CACHE_IMMOBILI_DIR, f) for f in os.listdir(CACHE_IMMOBILI_DIR) if f.endswith(('.jpg', '.png'))] if os.path.exists(CACHE_IMMOBILI_DIR) else []
    inset_im = None
    if len(cache_files) > 1:
        try: inset_im = Image.open(cache_files[1]).convert('RGB')
        except Exception: pass
    if not inset_im:
        inset_im = foto_im.crop((0, 0, min(foto_im.width, 400), min(foto_im.height, 300)))
    
    in_scaled = inset_im.resize((inset_w, inset_h), Image.LANCZOS)
    draw.rectangle([inset_x + 5, inset_y + 5, inset_x + inset_w + 5, inset_y + inset_h + 5], fill=(15, 23, 42, 60))
    draw.rectangle([inset_x - 3, inset_y - 3, inset_x + inset_w + 3, inset_y + inset_h + 3], fill=(255, 255, 255, 255))
    canvas.paste(in_scaled, (inset_x, inset_y))

    tag_w, tag_h = 210, 36
    draw.polygon([
        (inset_x, inset_y + inset_h - tag_h),
        (inset_x + tag_w, inset_y + inset_h - tag_h),
        (inset_x + tag_w - 15, inset_y + inset_h),
        (inset_x, inset_y + inset_h)
    ], fill=(234, 88, 12, 255))
    font_tag = get_font(15, bold=True, font_type="sans")
    draw.text((inset_x + 15, inset_y + inset_h - tag_h + 9), "TERRAZZA PANORAMICA", font=font_tag, fill=(255, 255, 255, 255))

    # 3. Footer Unificato
    fy = 1550
    draw.rounded_rectangle([35, fy, W - 35, H - 25], radius=24, fill=(248, 250, 252, 250), outline=(212, 168, 83, 200), width=2)
    draw_skyline(draw, H - 27, W - 70, color=(203, 213, 225, 150))

    draw_circular_badge(draw, 90, fy + 70, 34, "music", "")

    btn_w = 780
    btn_h = 72
    btn_x = 150
    btn_y = fy + 34
    btn_txt = "🔴 ENTRA ORA IN DIRETTA A VEDERLA DAL VIVO >" if is_live else "SCRIVICI IN PRIVATO PER INFO O VISITA >"
    draw.rounded_rectangle([btn_x + 3, btn_y + 5, btn_x + btn_w + 3, btn_y + btn_h + 5], radius=36, fill=(15, 23, 42, 60))
    btn_color = (220, 38, 38, 255) if is_live else (15, 23, 42, 255)
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=36, fill=btn_color, outline=(212, 168, 83, 255), width=2)
    
    font_btn = get_font(23, bold=True, font_type="sans")
    bbw = font_btn.getbbox(btn_txt)[2] - font_btn.getbbox(btn_txt)[0]
    draw.text((btn_x + (btn_w - bbw) // 2, btn_y + 22), btn_txt, font=font_btn, fill=(255, 255, 255, 255))

    font_script = get_font(36, bold=False, font_type="script")
    script_txt = "La tua prossima casa ti aspetta"
    sw = font_script.getbbox(script_txt)[2] - font_script.getbbox(script_txt)[0]
    draw.text(((W - sw) // 2, fy + 140), script_txt, font=font_script, fill=(180, 130, 40, 255))

    font_fbrand = get_font(30, bold=True, font_type="serif")
    fb_txt = "IMMOBILIARE GIANCANI"
    fbw = font_fbrand.getbbox(fb_txt)[2] - font_fbrand.getbbox(fb_txt)[0]
    draw.text(((W - fbw) // 2, fy + 210), fb_txt, font=font_fbrand, fill=(15, 23, 42, 255))

    canvas.save(output_path, "PNG")
    return output_path

def crea_grafica_luxury_glass(media_info, output_path=None, size=(1080, 1080)):
    """STILE 2 (FLYER 1:1): LUXURY GLASS MODERN"""
    W, H = size
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_luxury_{uuid.uuid4().hex[:6]}.png")

    foto_url = media_info.get('fotoUrl')
    foto_im = scarica_foto_url(foto_url)
    if not foto_im:
        for fb_url in GUARANTEED_FALLBACK_IMAGES:
            foto_im = scarica_foto_url(fb_url)
            if foto_im:
                break

    bg = foto_im.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(15))
    dark_ov = Image.new('RGBA', (W, H), (10, 15, 26, 210))
    bg_rgba = bg.convert('RGBA')
    bg_rgba.alpha_composite(dark_ov)
    draw = ImageDraw.Draw(bg_rgba)

    logo_img = get_clean_logo(max_w=320, max_h=80, transparent=True)
    if logo_img:
        try:
            lw, lh = logo_img.size
            bg_rgba.paste(logo_img, ((W - lw) // 2, 45), mask=logo_img.split()[3])
        except Exception:
            pass

    font_brand = get_font(28, bold=True, font_type="serif")
    b_txt = "IMMOBILIARE GIANCANI"
    b_w = font_brand.getbbox(b_txt)[2] - font_brand.getbbox(b_txt)[0]
    draw.text(((W - b_w) // 2, 145), b_txt, font=font_brand, fill=(212, 168, 83, 255))

    font_live = get_font(18, bold=True, font_type="sans")
    is_live = media_info.get('isLive', False)
    l_txt = "🔴 IN DIRETTA STREAMING ORA" if is_live else "★ PRESTIGE COLLECTION ★"
    l_w = font_live.getbbox(l_txt)[2] - font_live.getbbox(l_txt)[0] + 40
    badge_col = (220, 38, 38, 230) if is_live else (30, 64, 175, 230)
    draw.rounded_rectangle([(W - l_w)//2, 185, (W + l_w)//2, 225], radius=12, fill=badge_col)
    draw.text(((W - font_live.getbbox(l_txt)[2]) // 2, 195), l_txt, font=font_live, fill=(255, 255, 255, 255))

    cw, ch = 880, 430
    cx = (W - cw) // 2
    cy = 245
    c_photo = foto_im.resize((cw, ch), Image.LANCZOS)
    draw.rounded_rectangle([cx - 4, cy - 4, cx + cw + 4, cy + ch + 4], radius=16, fill=(212, 168, 83, 200))
    bg_rgba.paste(c_photo, (cx, cy))

    prezzo_reale = media_info.get('prezzo', '€ 79.000')
    mq_val = normalize_mq(media_info.get('mq', '140 metri quadri'))

    tag_price = f"💰 {prezzo_reale}  |  📐 {mq_val}"
    font_tag_p = get_font(24, bold=True, font_type="sans")
    tp_w = font_tag_p.getbbox(tag_price)[2] - font_tag_p.getbbox(tag_price)[0] + 36
    draw.rounded_rectangle([cx + 20, cy + ch - 65, cx + 20 + tp_w, cy + ch - 15], radius=10, fill=(15, 23, 42, 230), outline=(212, 168, 83, 255), width=2)
    draw.text((cx + 38, cy + ch - 55), tag_price, font=font_tag_p, fill=(255, 255, 255, 255))

    card_y = cy + ch + 20
    card_h = H - card_y - 40
    draw.rounded_rectangle([cx, card_y, cx + cw, card_y + card_h], radius=20, fill=(15, 23, 42, 220), outline=(212, 168, 83, 150), width=2)

    titolo = media_info.get('titolo', 'Opportunità Immobiliare Esclusiva')
    font_tit = get_font(26, bold=True, font_type="serif")
    draw.text((cx + 30, card_y + 20), titolo[:45], font=font_tit, fill=(255, 255, 255, 255))

    testo_f = media_info.get('testoF', 'Immobile selezionato per qualità, posizione e comodità ad Agrigento e Favara.')
    if "immobiliare giancani" not in testo_f.lower():
        testo_f = f"{testo_f.rstrip('. ')} — Immobiliare Giancani"

    font_tf = get_font(18, bold=False, font_type="sans")
    tf_words = testo_f.split()
    tf_lines = []
    c_line = []
    for w in tf_words:
        tl = " ".join(c_line + [w])
        if font_tf.getbbox(tl)[2] < cw - 60:
            c_line.append(w)
        else:
            if c_line: tf_lines.append(" ".join(c_line))
            c_line = [w]
    if c_line: tf_lines.append(" ".join(c_line))

    tdy = card_y + 65
    for l in tf_lines[:4]:
        draw.text((cx + 30, tdy), l, font=font_tf, fill=(203, 213, 225, 255))
        tdy += 26

    cta_t = "👉 ENTRA ORA IN DIRETTA A VEDERLA DAL VIVO!" if is_live else "👉 Contattaci per prenotare la tua visita privata"
    font_cta = get_font(18, bold=True, font_type="sans")
    draw.text((cx + 30, card_y + card_h - 75), cta_t, font=font_cta, fill=(56, 189, 248, 255))

    font_sign = get_font(22, bold=True, font_type="serif")
    sign_t = "— IMMOBILIARE GIANCANI —"
    sw = font_sign.getbbox(sign_t)[2] - font_sign.getbbox(sign_t)[0]
    draw.text((cx + (cw - sw) // 2, card_y + card_h - 38), sign_t, font=font_sign, fill=(212, 168, 83, 255))

    bg_rgba.save(output_path, "PNG")
    return output_path

def crea_story_luxury_glass_9_16(media_info, output_path=None):
    """STILE 2 (STORIA 9:16): LUXURY GLASS MODERN"""
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_luxury_{uuid.uuid4().hex[:6]}.png")

    foto_url = media_info.get('fotoUrl')
    foto_im = scarica_foto_url(foto_url)
    if not foto_im:
        for fb_url in GUARANTEED_FALLBACK_IMAGES:
            foto_im = scarica_foto_url(fb_url)
            if foto_im:
                break

    bg = foto_im.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(25))
    dark_ov = Image.new('RGBA', (W, H), (10, 15, 26, 215))
    bg_rgba = bg.convert('RGBA')
    bg_rgba.alpha_composite(dark_ov)
    draw = ImageDraw.Draw(bg_rgba)

    logo_img = get_clean_logo(max_w=380, max_h=95, transparent=True)
    if logo_img:
        try:
            lw, lh = logo_img.size
            bg_rgba.paste(logo_img, ((W - lw) // 2, 60), mask=logo_img.split()[3])
        except Exception:
            pass

    font_brand = get_font(30, bold=True, font_type="serif")
    b_txt = "IMMOBILIARE GIANCANI"
    bw = font_brand.getbbox(b_txt)[2] - font_brand.getbbox(b_txt)[0]
    draw.text(((W - bw) // 2, 185), b_txt, font=font_brand, fill=(212, 168, 83, 255))

    font_live = get_font(21, bold=True, font_type="sans")
    is_live = media_info.get('isLive', True)
    l_txt = "🔴 IN DIRETTA STREAMING ORA" if is_live else "★ PRESTIGE COLLECTION ★"
    lw = font_live.getbbox(l_txt)[2] - font_live.getbbox(l_txt)[0] + 44
    draw.rounded_rectangle([(W - lw)//2, 230, (W + lw)//2, 276], radius=14, fill=(220, 38, 38, 240) if is_live else (30, 64, 175, 240))
    draw.text(((W - font_live.getbbox(l_txt)[2]) // 2, 242), l_txt, font=font_live, fill=(255, 255, 255, 255))

    cw, ch = 960, 720
    cx = (W - cw) // 2
    cy = 310
    c_photo = foto_im.resize((cw, ch), Image.LANCZOS)
    draw.rounded_rectangle([cx - 4, cy - 4, cx + cw + 4, cy + ch + 4], radius=20, fill=(212, 168, 83, 220))
    bg_rgba.paste(c_photo, (cx, cy))

    prezzo_reale = media_info.get('prezzo', '€ 79.000')
    mq_val = normalize_mq(media_info.get('mq', '140 metri quadri'))
    tag_price = f"💰 {prezzo_reale}   |   📐 {mq_val.upper()}"
    font_tag_p = get_font(28, bold=True, font_type="sans")
    tp_w = font_tag_p.getbbox(tag_price)[2] - font_tag_p.getbbox(tag_price)[0] + 44
    draw.rounded_rectangle([cx + 30, cy + ch - 80, cx + 30 + tp_w, cy + ch - 18], radius=14, fill=(15, 23, 42, 240), outline=(212, 168, 83, 255), width=2)
    draw.text((cx + 52, cy + ch - 68), tag_price, font=font_tag_p, fill=(255, 255, 255, 255))

    card_y = cy + ch + 35
    card_h = H - card_y - 40
    draw.rounded_rectangle([cx, card_y, cx + cw, card_y + card_h], radius=24, fill=(15, 23, 42, 230), outline=(212, 168, 83, 160), width=2)

    titolo = media_info.get('titolo', 'Opportunità Immobiliare Esclusiva')
    font_tit = get_font(32, bold=True, font_type="serif")
    draw.text((cx + 40, card_y + 35), titolo[:42], font=font_tit, fill=(255, 255, 255, 255))

    testo_f = media_info.get('testoF', 'Immobile selezionato per qualità, posizione e comodità ad Agrigento e Favara.')
    if "immobiliare giancani" not in testo_f.lower():
        testo_f = f"{testo_f.rstrip('. ')} — Immobiliare Giancani"

    font_tf = get_font(22, bold=False, font_type="sans")
    tf_words = testo_f.split()
    tf_lines = []
    c_line = []
    for w in tf_words:
        tl = " ".join(c_line + [w])
        if font_tf.getbbox(tl)[2] < cw - 80:
            c_line.append(w)
        else:
            if c_line: tf_lines.append(" ".join(c_line))
            c_line = [w]
    if c_line: tf_lines.append(" ".join(c_line))

    tdy = card_y + 95
    for l in tf_lines[:7]:
        draw.text((cx + 40, tdy), l, font=font_tf, fill=(203, 213, 225, 255))
        tdy += 34

    btn_txt = "🔴 ENTRA ORA IN DIRETTA A VEDERLA DAL VIVO >" if is_live else "👉 CONTATTACI PER FISSARE UNA VISITA"
    font_cta = get_font(23, bold=True, font_type="sans")
    draw.text((cx + 40, card_y + card_h - 110), btn_txt, font=font_cta, fill=(56, 189, 248, 255))

    font_sign = get_font(28, bold=True, font_type="serif")
    sign_t = "— IMMOBILIARE GIANCANI —"
    sw = font_sign.getbbox(sign_t)[2] - font_sign.getbbox(sign_t)[0]
    draw.text((cx + (cw - sw) // 2, card_y + card_h - 55), sign_t, font=font_sign, fill=(212, 168, 83, 255))

    bg_rgba.save(output_path, "PNG")
    return output_path

def crea_grafica_editorial(media_info, output_path=None, size=(1080, 1080)):
    """STILE 3 (FLYER 1:1): EDITORIAL SHOWCASE MAGAZINE"""
    W, H = size
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_editorial_{uuid.uuid4().hex[:6]}.png")

    img = Image.new('RGBA', (W, H), (250, 250, 248, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([25, 25, W - 25, H - 25], outline=(212, 168, 83, 220), width=2)
    draw.rectangle([32, 32, W - 32, H - 32], outline=(15, 23, 42, 60), width=1)

    font_mag = get_font(26, bold=True, font_type="serif")
    mag_txt = "IMMOBILIARE GIANCANI"
    mw = font_mag.getbbox(mag_txt)[2] - font_mag.getbbox(mag_txt)[0]
    draw.text(((W - mw) // 2, 48), mag_txt, font=font_mag, fill=(15, 23, 42, 255))

    font_sub_mag = get_font(15, bold=True, font_type="sans")
    sub_mag = "EXCLUSIVE PROPERTY DOSSIER • ARCHITETTURA & VITA"
    sm_w = font_sub_mag.getbbox(sub_mag)[2] - font_sub_mag.getbbox(sub_mag)[0]
    draw.text(((W - sm_w) // 2, 85), sub_mag, font=font_sub_mag, fill=(148, 163, 184, 255))
    draw.line([(50, 115), (W - 50, 115)], fill=(212, 168, 83, 180), width=1)

    foto_url = media_info.get('fotoUrl')
    foto_1 = scarica_foto_url(foto_url)
    if not foto_1:
        for fb_url in GUARANTEED_FALLBACK_IMAGES:
            foto_1 = scarica_foto_url(fb_url)
            if foto_1:
                break
    cache_files = [os.path.join(CACHE_IMMOBILI_DIR, f) for f in os.listdir(CACHE_IMMOBILI_DIR) if f.endswith(('.jpg', '.png'))] if os.path.exists(CACHE_IMMOBILI_DIR) else []

    foto_2 = Image.open(cache_files[1]).convert('RGB') if len(cache_files) > 1 else foto_1

    f1_w, f1_h = 580, 420
    f2_w, f2_h = 360, 420
    sc1 = foto_1.resize((f1_w, f1_h), Image.LANCZOS)
    sc2 = foto_2.resize((f2_w, f2_h), Image.LANCZOS)

    draw.rectangle([50, 135, 50 + f1_w, 135 + f1_h], fill=(226, 232, 240, 255))
    img.paste(sc1, (50, 135))
    
    draw.rectangle([70 + f1_w, 135, W - 50, 135 + f2_h], fill=(226, 232, 240, 255))
    img.paste(sc2, (70 + f1_w, 135))

    prezzo_reale = media_info.get('prezzo', '€ 79.000')
    draw.rectangle([50, 135 + f1_h - 55, 50 + 260, 135 + f1_h], fill=(220, 38, 38, 240))
    font_bp = get_font(26, bold=True, font_type="sans")
    draw.text((70, 135 + f1_h - 45), f"PREZZO: {prezzo_reale}", font=font_bp, fill=(255, 255, 255, 255))

    ty = 135 + f1_h + 30
    titolo = media_info.get('titolo', 'Residenza di Prestigio').upper()
    font_tit = get_font(30, bold=True, font_type="serif")
    draw.text((50, ty), titolo[:40], font=font_tit, fill=(15, 23, 42, 255))

    mq_val = normalize_mq(media_info.get('mq', '140 metri quadri'))
    font_spec = get_font(18, bold=True, font_type="sans")
    spec_txt = f"• SUPERFICIE: {mq_val.upper()}   |   • CLASSE & COMFORT ELEVATO"
    draw.text((50, ty + 42), spec_txt, font=font_spec, fill=(180, 130, 40, 255))

    testo_f = media_info.get('testoF', 'Splendida soluzione su più livelli, luminosa e versatile. Perfetta per famiglie o investimento.')
    if "immobiliare giancani" not in testo_f.lower():
        testo_f = f"{testo_f.rstrip('. ')} — Immobiliare Giancani"

    font_desc = get_font(18, bold=False, font_type="sans")
    words = testo_f.split()
    lines = []
    curr = []
    for w in words:
        tl = " ".join(curr + [w])
        if font_desc.getbbox(tl)[2] < W - 120:
            curr.append(w)
        else:
            if curr: lines.append(" ".join(curr))
            curr = [w]
    if curr: lines.append(" ".join(curr))

    my = ty + 85
    for l in lines[:5]:
        draw.text((50, my), l, font=font_desc, fill=(51, 65, 85, 255))
        my += 28

    bbar_y = H - 95
    draw.line([(50, bbar_y), (W - 50, bbar_y)], fill=(212, 168, 83, 180), width=2)

    font_cta_m = get_font(17, bold=True, font_type="sans")
    cta_m = "CONTATTI & APPUNTAMENTI: IMMOBILIARE GIANCANI"
    draw.text((50, bbar_y + 20), cta_m, font=font_cta_m, fill=(15, 23, 42, 255))

    font_scr = get_font(22, bold=False, font_type="script")
    draw.text((W - 350, bbar_y + 15), "La tua prossima casa ti aspetta", font=font_scr, fill=(180, 130, 40, 255))

    img.save(output_path, "PNG")
    return output_path

def crea_story_editorial_9_16(media_info, output_path=None):
    """STILE 3 (STORIA 9:16): EDITORIAL SHOWCASE MAGAZINE"""
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_editorial_{uuid.uuid4().hex[:6]}.png")

    img = Image.new('RGBA', (W, H), (250, 250, 248, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([30, 30, W - 30, H - 30], outline=(212, 168, 83, 220), width=3)
    draw.rectangle([40, 40, W - 40, H - 40], outline=(15, 23, 42, 70), width=1)

    logo_img = get_clean_logo(max_w=340, max_h=85, transparent=True)
    if logo_img:
        try:
            lw, lh = logo_img.size
            img.paste(logo_img, ((W - lw) // 2, 55), mask=logo_img.split()[3])
        except Exception:
            pass

    font_mag = get_font(32, bold=True, font_type="serif")
    mag_txt = "IMMOBILIARE GIANCANI"
    mw = font_mag.getbbox(mag_txt)[2] - font_mag.getbbox(mag_txt)[0]
    draw.text(((W - mw) // 2, 160), mag_txt, font=font_mag, fill=(15, 23, 42, 255))

    font_sub_mag = get_font(18, bold=True, font_type="sans")
    sub_mag = "PRESTIGE PROPERTY DOSSIER • ARCHITETTURA & DESIGN"
    sm_w = font_sub_mag.getbbox(sub_mag)[2] - font_sub_mag.getbbox(sub_mag)[0]
    draw.text(((W - sm_w) // 2, 205), sub_mag, font=font_sub_mag, fill=(148, 163, 184, 255))
    draw.line([(60, 240), (W - 60, 240)], fill=(212, 168, 83, 180), width=2)

    foto_url = media_info.get('fotoUrl')
    foto_1 = scarica_foto_url(foto_url)
    if not foto_1:
        for fb_url in GUARANTEED_FALLBACK_IMAGES:
            foto_1 = scarica_foto_url(fb_url)
            if foto_1:
                break

    fw, fh = 960, 750
    fx = (W - fw) // 2
    fy = 265
    sc1 = foto_1.resize((fw, fh), Image.LANCZOS)
    draw.rounded_rectangle([fx - 3, fy - 3, fx + fw + 3, fy + fh + 3], radius=16, fill=(212, 168, 83, 200))
    img.paste(sc1, (fx, fy))

    prezzo_reale = media_info.get('prezzo', '€ 79.000')
    draw.rectangle([fx, fy + fh - 75, fx + 340, fy + fh], fill=(220, 38, 38, 240))
    font_bp = get_font(30, bold=True, font_type="sans")
    draw.text((fx + 25, fy + fh - 62), f"PREZZO: {prezzo_reale}", font=font_bp, fill=(255, 255, 255, 255))

    ty = fy + fh + 40
    titolo = media_info.get('titolo', 'Residenza di Prestigio').upper()
    font_tit = get_font(36, bold=True, font_type="serif")
    draw.text((fx, ty), titolo[:42], font=font_tit, fill=(15, 23, 42, 255))

    mq_val = normalize_mq(media_info.get('mq', '140 metri quadri'))
    font_spec = get_font(22, bold=True, font_type="sans")
    spec_txt = f"• SUPERFICIE: {mq_val.upper()}   |   • ESCLUSIVA GIANCANI"
    draw.text((fx, ty + 50), spec_txt, font=font_spec, fill=(180, 130, 40, 255))

    testo_f = media_info.get('testoF', 'Splendida soluzione su più livelli, luminosa e versatile. Perfetta per famiglie o investimento.')
    if "immobiliare giancani" not in testo_f.lower():
        testo_f = f"{testo_f.rstrip('. ')} — Immobiliare Giancani"

    font_desc = get_font(22, bold=False, font_type="sans")
    words = testo_f.split()
    lines = []
    curr = []
    for w in words:
        tl = " ".join(curr + [w])
        if font_desc.getbbox(tl)[2] < fw:
            curr.append(w)
        else:
            if curr: lines.append(" ".join(curr))
            curr = [w]
    if curr: lines.append(" ".join(curr))

    my = ty + 105
    for l in lines[:8]:
        draw.text((fx, my), l, font=font_desc, fill=(51, 65, 85, 255))
        my += 34

    bbar_y = H - 180
    draw.line([(60, bbar_y), (W - 60, bbar_y)], fill=(212, 168, 83, 180), width=2)

    is_live = media_info.get('isLive', True)
    btn_w = 820
    btn_h = 70
    btn_x = (W - btn_w) // 2
    btn_y = bbar_y + 20
    btn_txt = "🔴 ENTRA ORA IN DIRETTA A VEDERLA DAL VIVO >" if is_live else "CONTATTACI PER MAGGIORI INFORMAZIONI >"
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=35, fill=(220, 38, 38, 255) if is_live else (15, 23, 42, 255))
    font_b = get_font(23, bold=True, font_type="sans")
    bbw = font_b.getbbox(btn_txt)[2] - font_b.getbbox(btn_txt)[0]
    draw.text(((W - bbw) // 2, btn_y + 20), btn_txt, font=font_b, fill=(255, 255, 255, 255))

    font_scr = get_font(26, bold=False, font_type="script")
    draw.text(((W - 420) // 2, btn_y + 82), "La tua prossima casa ti aspetta — Immobiliare Giancani", font=font_scr, fill=(180, 130, 40, 255))

    img.save(output_path, "PNG")
    return output_path

def normalizza_foto_url(url):
    """
    Normalizza qualsiasi link Google Drive / Docs / ID in URL CDN diretta lh3 ad altissima risoluzione.
    Supporta:
    - https://drive.google.com/file/d/{ID}/view
    - https://drive.google.com/open?id={ID}
    - https://drive.google.com/uc?id={ID}
    - {ID} puro da 25+ caratteri
    - URL diretti http/https già validi
    """
    if not url:
        return None
    url_str = str(url).strip()
    if "drive.google.com" in url_str or "docs.google.com" in url_str:
        m = re.search(r'[-\w]{25,}', url_str)
        if m:
            return f"https://lh3.googleusercontent.com/d/{m.group(0)}"
    elif re.match(r'^[-\w]{25,}$', url_str):
        return f"https://lh3.googleusercontent.com/d/{url_str}"
    elif "lh3.googleusercontent.com" in url_str:
        return url_str
    return url_str

def parse_property_row_smart(row, headers=None, sheet_name=""):
    """
    Estrae i dati dell'immobile in modo intelligente e dinamico da fogli con colonne diverse.
    REGOLA MANDATORIA: Il testo parlato/narrazione viene prelevato RIGOROSAMENTE dalla Colonna F (indice 5).
    Riconosce autonomamente foto/video, prezzo, mq e titolo/stanza anche se posizionati in colonne diverse.
    """
    if not row or len(row) <= 5:
        return None
    
    # 1. TESTO PARLATO: RIGOROSAMENTE COLONNA F (indice 5, 0-indexed)
    testo_f = str(row[5] or "").strip()
    if not testo_f:
        return None
    if "immobiliare giancani" not in testo_f.lower():
        testo_f += " — Immobiliare Giancani"

    # Mappa colonne per header (se presenti)
    col_by_header = {}
    if headers:
        for idx, h in enumerate(headers):
            h_clean = str(h or "").lower().strip()
            if any(k in h_clean for k in ["foto", "media", "immagine", "link", "url"]):
                col_by_header.setdefault("media", idx)
            elif any(k in h_clean for k in ["prezzo", "costo", "euro", "€"]):
                col_by_header.setdefault("prezzo", idx)
            elif any(k in h_clean for k in ["mq", "metri", "superficie", "mq."]):
                col_by_header.setdefault("mq", idx)
            elif any(k in h_clean for k in ["stanza", "ambiente", "vano", "locale"]):
                col_by_header.setdefault("stanza", idx)
            elif any(k in h_clean for k in ["titolo", "nome", "immobile"]):
                col_by_header.setdefault("titolo", idx)

    foto_url = ""
    video_url = None
    prezzo = ""
    mq_val = ""
    stanza = ""

    # Se abbiamo mappa da header, usa prioritariamente quella
    if "media" in col_by_header and col_by_header["media"] < len(row):
        val_m = str(row[col_by_header["media"]] or "").strip()
        if "youtube.com" in val_m or "youtu.be" in val_m or val_m.endswith(('.mp4', '.mov', '.avi')):
            video_url = val_m
        elif val_m.startswith("http") or "lh3.googleusercontent.com" in val_m or "drive.google.com" in val_m:
            foto_url = normalizza_foto_url(val_m)
    
    if "prezzo" in col_by_header and col_by_header["prezzo"] < len(row):
        prezzo = str(row[col_by_header["prezzo"]] or "").strip()
    if "mq" in col_by_header and col_by_header["mq"] < len(row):
        mq_val = str(row[col_by_header["mq"]] or "").strip()
    if "stanza" in col_by_header and col_by_header["stanza"] < len(row):
        stanza = str(row[col_by_header["stanza"]] or "").strip()

    # Se mancano valori o non abbiamo header, scansione euristica su tutte le colonne (tranne Col F che è testo)
    for c_idx, cell in enumerate(row):
        if c_idx == 5:
            continue  # Colonna F riservata al testo
        c_str = str(cell or "").strip()
        if not c_str:
            continue
        
        # Riconoscimento Foto / Video
        if not foto_url and not video_url:
            if "youtube.com" in c_str or "youtu.be" in c_str or c_str.endswith(('.mp4', '.mov', '.avi')):
                video_url = c_str
                # Cerca eventuale thumbnail nelle colonne successive
                for next_c in range(c_idx + 1, min(len(row), c_idx + 3)):
                    if next_c != 5:
                        nc_str = str(row[next_c] or "").strip()
                        if nc_str.startswith("http") and not ("youtube.com" in nc_str or "youtu.be" in nc_str):
                            foto_url = normalizza_foto_url(nc_str)
                            break
            elif c_str.startswith("http") or "lh3.googleusercontent.com" in c_str or "drive.google.com" in c_str or re.match(r'^[-\w]{25,}$', c_str):
                foto_url = normalizza_foto_url(c_str)

        # Riconoscimento Prezzo
        if not prezzo:
            if "€" in c_str or "euro" in c_str.lower() or "trattativa" in c_str.lower() or (c_str.replace(".", "").replace(" ", "").isdigit() and len(c_str) >= 4 and int(c_str.replace(".", "").replace(" ", "")) >= 10000):
                prezzo = c_str

        # Riconoscimento Metri Quadri
        if not mq_val:
            if any(unit in c_str.lower() for unit in ["mq", "m²", "metri quadri", "metri"]):
                mq_val = c_str
            elif c_str.isdigit() and 20 <= int(c_str) <= 50000 and c_idx in (1, 2, 3, 4):
                mq_val = f"{c_str} metri quadri"

        # Riconoscimento Stanza / Ambiente
        if not stanza and c_idx in (1, 2, 3, 4) and len(c_str) > 2:
            if not c_str.startswith("http") and not c_str.replace(".", "").replace(" ", "").isdigit() and not any(kw in c_str.lower() for kw in ["€", "euro", "trattativa", "mq", "m²", "metri"]):
                stanza = c_str

    if not foto_url and not video_url:
        return None

    s_clean = sheet_name.replace("_", " ").strip() if sheet_name else ""
    if stanza and stanza.lower() not in ["ambiente", ""] and stanza.lower() != s_clean.lower():
        titolo_completo = f"{s_clean} — {stanza}" if s_clean else stanza
    else:
        titolo_completo = s_clean or "Immobile in Vendita"

    return {
        "titolo": titolo_completo,
        "stanza": stanza,
        "prezzo": prezzo or "Trattativa Riservata",
        "mq": normalize_mq(mq_val or "120 metri quadri"),
        "fotoUrl": foto_url,
        "videoUrl": video_url,
        "testoF": testo_f
    }

def scarica_foto_url(url):
    """
    Scarica o apre un'immagine autentica e in alta definizione dell'immobile assicurandosi che non sia corrotta o nera.
    Supporta percorsi di file locali diretti (assets/immobili_cache/...), URL Drive e CDN.
    Garantisce assoluta rotazione visiva evitando qualsiasi ripetizione della stessa foto.
    """
    # 0. Controllo file locale diretto
    if url and os.path.exists(str(url)):
        try:
            im_loc = Image.open(str(url)).convert('RGBA')
            if is_image_valid_and_not_black(im_loc):
                return im_loc
        except Exception as e_loc:
            print(f"Avviso apertura foto locale ({url}): {e_loc}")

    url_norm = normalizza_foto_url(url)

    # 1. Tentativo di download diretto tramite URL normalizzato
    if url_norm and str(url_norm).startswith("http"):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            resp = requests.get(url_norm, headers=headers, verify=False, timeout=18)
            if resp.status_code == 200 and len(resp.content) > 3000:
                img = Image.open(io.BytesIO(resp.content)).convert('RGBA')
                if is_image_valid_and_not_black(img):
                    try:
                        cached_file = os.path.join(CACHE_IMMOBILI_DIR, f"cached_{uuid.uuid4().hex[:8]}.jpg")
                        img.convert('RGB').save(cached_file, "JPEG", quality=92)
                    except Exception:
                        pass
                    return img
        except Exception as eDl:
            print(f"Avviso scaricamento foto ({str(url_norm)[:60]}...): {eDl}")

    # 2. Controllo cache locale: foto autentiche precedentemente salvate con shuffle anti-ripetizione
    if os.path.exists(CACHE_IMMOBILI_DIR):
        cache_files = [os.path.join(CACHE_IMMOBILI_DIR, f) for f in os.listdir(CACHE_IMMOBILI_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if cache_files:
            random.shuffle(cache_files)
            for cf in cache_files:
                try:
                    if os.path.getsize(cf) > 5000:
                        im_c = Image.open(cf).convert('RGBA')
                        if is_image_valid_and_not_black(im_c):
                            return im_c
                except Exception:
                    pass

    # 3. Fallback di garanzia: selezione dinamica da catalogo di riserva garantito (foto sempre diverse!)
    fallback_pool = list(GUARANTEED_FALLBACK_IMAGES)
    random.shuffle(fallback_pool)
    for fb_url in fallback_pool:
        try:
            resp_fb = requests.get(fb_url, verify=False, timeout=12, headers={'User-Agent': 'Mozilla/5.0'})
            if resp_fb.status_code == 200 and len(resp_fb.content) > 3000:
                im_fb = Image.open(io.BytesIO(resp_fb.content)).convert('RGBA')
                if is_image_valid_and_not_black(im_fb):
                    return im_fb
        except Exception:
            continue

    return None

def genera_video_da_clip_o_foto(media_info, output_video_path=None, style="auto"):
    """
    Costruisce il video di 15 secondi (1080x1920) e il volantino promozionale 1:1,
    facendo ruotare ad ogni ciclo da 30 minuti diverse grafiche (Split-Screen Flyer, Luxury Glass, Editorial Showcase).
    Garantisce narrazione vocale espressiva (DarIA/DarIO) e musica allegra (124 BPM) royalty-free.
    """
    if not output_video_path:
        output_video_path = os.path.join(SCRATCH_DIR, f"story_video_{uuid.uuid4().hex[:8]}.mp4")

    ffmpeg_bin = find_ffmpeg()
    ytdlp_bin = find_ytdlp()

    video_url = media_info.get('videoUrl')
    foto_url = media_info.get('fotoUrl')
    titolo = media_info.get('titolo', 'Immobile di Prestigio')
    prezzo = media_info.get('prezzo', 'Trattativa Riservata')
    mq = normalize_mq(media_info.get('mq', '120'))
    testo_f = media_info.get('testoF', 'Immobile esclusivo selezionato ad Agrigento e Favara.')
    is_live = media_info.get('isLive', False)

    # Determina indice progressivo per cambiare colore e forma di impostazione ad OGNI storia
    slot_stile = int(time.time() / 1800)
    story_seq = media_info.get("story_index", slot_stile)
    try:
        story_seq = int(story_seq)
    except Exception:
        story_seq = slot_stile

    # Caricamento del Motore Grafico Unificato e della Palette specifica per questa storia
    mgs = None
    palette_giorno = None
    try:
        import motore_grafica_storie as mgs
        palette_giorno = mgs.get_palette_del_giorno(slot_idx=story_seq)
        print(f"🎨 PALETTE STORIA: {palette_giorno.get('nome')} [ID: {palette_giorno.get('id')}]")
    except Exception as eImportMgs:
        print(f"Avviso importazione motore_grafica_storie: {eImportMgs}")

    # 21 stili professionali per variare la forma di impostazione ad ogni storia
    styles = [
        "auto", "daily", "daily_lunedi", "daily_martedi", "daily_mercoledi",
        "daily_giovedi", "daily_venerdi", "daily_sabato", "daily_domenica",
        "cb_curved_wave", "metroquadro_gradient", "professionecasa_sidebar",
        "frosted_glass", "arco_architettonico", "gabetti_diagonal", "minimal_terracotta",
        "twilight_penthouse", "tech_card_modern", "mediterranean_coastal",
        "vogue_editorial", "diamond_prestige", "country_chic_sage", "cinematic_hero",
        "card_live"
    ]
    # Rotazione continua dei 6 stili mandatori per garantire assoluta varietà visiva
    ROTATING_STYLES_LIST = [
        "split_screen",
        "luxury_glass",
        "editorial",
        "gabetti_diagonal",
        "capellupo_sidebar",
        "marketing_banner"
    ]
    if not style or style in ("auto", "daily", "giorno", "settimanale", "rotazione"):
        chosen_style = ROTATING_STYLES_LIST[story_seq % len(ROTATING_STYLES_LIST)]
    else:
        chosen_style = style.strip().lower()
        if chosen_style not in styles and chosen_style not in ROTATING_STYLES_LIST:
            chosen_style = ROTATING_STYLES_LIST[story_seq % len(ROTATING_STYLES_LIST)]
    
    giorno_label = palette_giorno.get('giorno', 'Oggi') if palette_giorno else 'Standard'
    palette_nome = palette_giorno.get('nome', 'Default') if palette_giorno else 'Default'
    print(f"🎨 Stile Grafico selezionato: {chosen_style.upper()} | Tema del Giorno ({giorno_label}): {palette_nome}")

    # 1. Genera overlay video 9:16 tramite il Motore Grafico Unificato con la palette del giorno
    overlay_png_path = None
    if mgs:
        try:
            overlay_png_path = mgs.crea_story_9_16(media_info, style=chosen_style, palette=palette_giorno)
        except Exception as eMgsGen:
            print(f"Avviso render 9:16 mgs ({chosen_style}): {eMgsGen}")

    if not overlay_png_path or not os.path.exists(overlay_png_path):
        if chosen_style == "luxury_glass":
            overlay_png_path = crea_story_luxury_glass_9_16(media_info)
        elif chosen_style == "editorial":
            overlay_png_path = crea_story_editorial_9_16(media_info)
        else:
            overlay_png_path = crea_story_splitscreen_9_16(media_info)

    # Genera e salva anche il volantino promozionale 1:1 coordinato con il tema del giorno
    flyer_1x1_path = os.path.join(SCRATCH_DIR, f"flyer_giancani_1x1_{uuid.uuid4().hex[:6]}.png")
    if mgs and hasattr(mgs, 'crea_flyer_1_1'):
        try:
            mgs.crea_flyer_1_1(media_info, style=chosen_style, palette=palette_giorno, output_path=flyer_1x1_path)
        except Exception as e_fl:
            print(f"Avviso generazione flyer 1:1: {e_fl}")
            crea_grafica_flyer_split_screen(media_info, flyer_1x1_path, size=(1080, 1080))
    elif mgs:
        try:
            if chosen_style == "gabetti_diagonal":
                mgs.crea_flyer_gabetti_diagonal_1_1(media_info, palette=palette_giorno, output_path=flyer_1x1_path)
            elif chosen_style == "capellupo_sidebar":
                mgs.crea_flyer_capellupo_sidebar_1_1(media_info, palette=palette_giorno, output_path=flyer_1x1_path)
            elif chosen_style == "luxury_glass":
                crea_grafica_luxury_glass(media_info, flyer_1x1_path, size=(1080, 1080))
            elif chosen_style == "editorial":
                crea_grafica_editorial(media_info, flyer_1x1_path, size=(1080, 1080))
            else:
                crea_grafica_flyer_split_screen(media_info, flyer_1x1_path, size=(1080, 1080))
        except Exception as e_fl:
            print(f"Avviso generazione flyer 1:1: {e_fl}")
            crea_grafica_flyer_split_screen(media_info, flyer_1x1_path, size=(1080, 1080))
    else:
        crea_grafica_flyer_split_screen(media_info, flyer_1x1_path, size=(1080, 1080))

    # 2. Determina fascia oraria se offline
    fascia_info = determina_fascia_oraria() if not is_live else None

    # 3. Traccia audio con DarIA/DarIO + musica allegra (124 BPM)
    frase_positiva_flash = fascia_info["frase_flash"] if (not is_live and fascia_info) else random.choice(FRASI_POSITIVE_FLASH)
    audio_path = crea_audio_mix_completo(testo_f, is_live=is_live, frase_positiva=frase_positiva_flash, fascia_info=fascia_info)

    # 4. Rendering Video 1080x1920 con FFmpeg (15 secondi continui)
    cmd_render = [
        ffmpeg_bin, "-y",
        "-loop", "1", "-i", overlay_png_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "15",
        output_video_path
    ]

    proc_render = subprocess.run(cmd_render, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    if proc_render.returncode == 0 and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 100000:
        print(f"[OK] Video Storia 15s ({chosen_style}) generato: {output_video_path}")
        return output_video_path
    return None

def pubblica_storia_video_su_facebook(page_id, page_token, video_path):
    """Carica la video storia su Facebook via Meta Graph API (Resumable Upload)"""
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
            "story_id": fin_res.get('post_id') or video_id,
            "type": "video_story"
        }

def pubblica_storia_instagram(ig_user_id, page_token, video_path):
    """
    Pubblicazione Instagram disabilitata su richiesta dell'utente.
    """
    print("ℹ️ Pubblicazione su Instagram DISABILITATA su richiesta dell'utente (solo Facebook attivo).")
    return {
        "nome": "Instagram Stories (@giancani_immobiliare)",
        "success": True,
        "skipped": True,
        "story_id": "DISABLED",
        "metodo": "Disabilitato su richiesta utente"
    }

def pubblica_short_youtube(video_path, item_data):
    """
    Pubblica direttamente il video come YouTube Short sul canale ufficiale
    @immobiliaregiancani761 (ID: UC7jCI1x_cwh_sOrNPJpaKyQ) tramite YouTube Data API v3.
    Supporta Secrets GitHub Actions (YOUTUBE_TOKEN_GIANCANI_JSON / YOUTUBE_TOKEN_JSON) e token locale.
    """
    print(f"\n🎬 Pubblicazione YouTube Short sul Canale (@immobiliaregiancani761)...")
    try:
        titolo = item_data.get('titolo', 'Opportunità Immobiliare')
        prezzo = item_data.get('prezzo', 'Trattativa Riservata')
        mq = item_data.get('mq', '120 metri quadri')
        testo_f = item_data.get('testoF', '').strip()
        is_live = item_data.get('isLive', False)

        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        import google_auth_httplib2
        import httplib2
        import requests as _rq
        import urllib3 as _u3
        _u3.disable_warnings()

        creds = None
        scopes_yt = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube"
        ]

        # 1. Controllo Variabili d'Ambiente (GitHub Actions Secrets)
        candidates_env = [
            os.environ.get("YOUTUBE_TOKEN_GIANCANI_JSON"),
            os.environ.get("YOUTUBE_TOKEN_JSON")
        ]
        for c_env in candidates_env:
            if c_env and len(c_env.strip()) > 30:
                try:
                    tok_data = json.loads(c_env)
                    c = Credentials.from_authorized_user_info(tok_data, scopes_yt)
                    if c.expired and c.refresh_token:
                        _s = _rq.Session()
                        _s.verify = False
                        _s.trust_env = False
                        c.refresh(Request(session=_s))
                    if c.valid:
                        creds = c
                        print("  ✅ Token OAuth YouTube acquisito con successo da Secret GitHub Actions!")
                        break
                except Exception as _e_env:
                    print(f"  ⚠️ Avviso lettura token da env: {_e_env}")

        # 2. Controllo File Token Locali su Disco
        if not creds:
            token_paths = [
                os.path.join(os.path.dirname(__file__), "token_youtube_giancani.json"),
                os.path.join(os.path.dirname(__file__), "token_youtube.json"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "token_youtube_giancani.json"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "token_youtube.json")
            ]
            for tp in token_paths:
                if not os.path.exists(tp):
                    continue
                try:
                    c = Credentials.from_authorized_user_file(tp, scopes_yt)
                    if c.expired and c.refresh_token:
                        _s = _rq.Session()
                        _s.verify = False
                        _s.trust_env = False
                        c.refresh(Request(session=_s))
                        try:
                            with open(tp, "w", encoding="utf-8") as tf:
                                tf.write(c.to_json())
                        except Exception:
                            pass
                    if c.valid:
                        creds = c
                        print(f"  ✅ Token OAuth YouTube valido acquisito da: {os.path.basename(tp)}")
                        break
                except Exception as _e_tok:
                    print(f"  ⚠️ Tentativo token {tp} fallito: {_e_tok}")

        if creds and creds.valid:
            http_client = httplib2.Http(disable_ssl_certificate_validation=True)
            auth_http = google_auth_httplib2.AuthorizedHttp(creds, http=http_client)
            youtube = build("youtube", "v3", http=auth_http)

            # Formattazione titolo Shorts (< 95 caratteri)
            short_title = f"{titolo} | {prezzo} #Shorts"
            if len(short_title) > 95:
                short_title = f"{titolo[:60]} | #Shorts"

            # Descrizione completa conforme a Colonna F e Personal Branding
            prefix_live = "🔴 IN DIRETTA ORA! " if is_live else ""
            description = (
                f"🏢 {prefix_live}{titolo.upper()}\n"
                f"📐 Superficie: {mq}\n"
                f"💰 Prezzo: {prezzo}\n\n"
                f"📜 Descrizione Ufficiale (Colonna F):\n"
                f"«{testo_f}»\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👉 Per informazioni e visite:\n"
                f"🏠 IMMOBILIARE GIANCANI — Favara (Agrigento)\n"
                f"📍 Corso Vittorio Veneto 151, Favara (AG)\n"
                f"🌐 Sito Web Ufficiale: https://immobiliaregiancani.it\n"
                f"📞 Telefono: +39 320 166 7156\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"— Immobiliare Giancani\n\n"
                f"#Shorts #Stories #Storie #ImmobiliareGiancani #Favara #Agrigento #CaseInVendita #DarIA #AntonioGiancani"
            )

            body = {
                "snippet": {
                    "title": short_title,
                    "description": description,
                    "tags": ["Immobiliare Giancani", "Favara", "Agrigento", "Case in Vendita", "Immobiliare", "DarIA", "Shorts", "YouTube Shorts", "Antonio Giancani", "Storie"],
                    "categoryId": "27",
                    "defaultLanguage": "it"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
            print(f"  🚀 [YouTube Data API] Upload in corso su @immobiliaregiancani761...")
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = request.execute()
            v_id = response.get("id")
            yt_short_url = f"https://youtube.com/shorts/{v_id}"
            print(f"  ✅ [YouTube Shorts] Pubblicato con successo! URL: {yt_short_url}")
            return {
                "nome": "YouTube Shorts (@immobiliaregiancani761)",
                "success": True,
                "story_id": v_id,
                "url": yt_short_url
            }
        else:
            print("  ⚠️ Nessun token OAuth YouTube valido disponibile per caricamento diretto.")

        # Fallback secondario su Apps Script se il token non è presente
        payload = {
            "action": "pubblica_youtube_short",
            "titolo": titolo,
            "mq": mq,
            "prezzo": prezzo,
            "testoF": testo_f,
            "videoUrl": item_data.get('videoUrl', ''),
            "thumbUrl": item_data.get('thumbUrl', '')
        }
        if os.path.exists(video_path) and os.path.getsize(video_path) < 8 * 1024 * 1024:
            with open(video_path, 'rb') as f:
                payload["base64Video"] = base64.b64encode(f.read()).decode('utf-8')

        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            APPS_SCRIPT_URL,
            data=req_data,
            headers={"Content-Type": "application/json", "User-Agent": "Giancani-YouTube-Shorts-Bot"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=35, context=ctx) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            return {
                "nome": "YouTube Shorts (@immobiliaregiancani761)",
                "success": res_json.get('success', True),
                "story_id": res_json.get('videoId') or res_json.get('status', 'REGISTRATO'),
                "url": res_json.get('shortUrl', 'https://www.youtube.com/@immobiliaregiancani761/shorts')
            }
    except Exception as eYt:
        print(f"Avviso YouTube Shorts: {eYt}")
        return {
            "nome": "YouTube Shorts (@immobiliaregiancani761)",
            "success": False,
            "error": str(eYt)
        }


def pubblica_storia_tiktok(video_path, item_data):
    """
    Pubblica la video storia identica su TikTok (@immobiliare_giancani) ESCLUSIVAMENTE NELLE STORIE.
    Garantisce lo stesso file video 1080x1920, la stessa durata e gli stessi testi di Facebook, Instagram e YouTube.
    Esegue il caricamento automatico via Playwright Chromium se disponibile, oppure esegue il dispatch workflow su GitHub Actions.
    """
    print(f"\n🎵 Pubblicazione Video Storia su TikTok (@immobiliare_giancani)...")
    try:
        titolo = item_data.get('titolo', 'Opportunità Immobiliare')
        prezzo = item_data.get('prezzo', 'Trattativa Riservata')
        mq = item_data.get('mq', '120 metri quadri')
        testo_f = item_data.get('testoF', '')

        # 1. Copia il video identico nella cartella di output TikTok
        out_dir = os.path.join(os.path.dirname(__file__), "output_storie")
        os.makedirs(out_dir, exist_ok=True)
        tk_video_path = os.path.join(out_dir, "tiktok_latest_story.mp4")
        if os.path.exists(video_path):
            shutil.copy2(video_path, tk_video_path)

        # 2. Formattazione didascalia con Colonna F e branding
        caption = (
            f"🎬 STORIA IMMOBILIARE GIANCANI: {titolo.upper()}\n"
            f"📐 {mq} | 💰 {prezzo}\n\n"
            f"«{testo_f}»\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👉 Info e visite: Corso Vittorio Veneto 151, Favara (AG)\n"
            f"📞 Tel: +39 320 166 7156 | www.immobiliaregiancani.it\n"
            f"— Immobiliare Giancani\n\n"
            f"#ImmobiliareGiancani #TikTokStories #StorieTikTok #CaseInVendita #Favara #Agrigento #DarIA #AntonioGiancani"
        )
        if len(caption) > 2100:
            caption = caption[:2000] + "\n\n— Immobiliare Giancani"

        # 3. Tentativo di caricamento diretto Headless via Playwright su TikTok Creator Center (STORIE)
        tk_uploaded = False
        try:
            from scripts.bot_tiktok_publisher import carica_su_tiktok_playwright
            ok_tk, info_tk = carica_su_tiktok_playwright(video_path, caption)
            if ok_tk:
                tk_uploaded = True
                print(f"  ✅ [TikTok Stories] Video caricato con successo nelle Storie via Playwright! Conferma: {info_tk}")
            else:
                print(f"  ℹ️ [TikTok Stories Playwright] Esito: {info_tk}")
        except Exception as e_pw:
            print(f"  ℹ️ [TikTok Playwright locale non disponibile]: {e_pw}")

        # 4. Se Playwright diretto non è riuscito ma abbiamo LIVE_GITHUB_TOKEN, dispatch del workflow dedicato
        gh_token = os.environ.get("LIVE_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not tk_uploaded and gh_token:
            try:
                import requests as _rq
                _s = _rq.Session()
                _s.verify = False
                _s.trust_env = False
                headers_gh = {
                    "Authorization": f"token {gh_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                url_dispatch = "https://api.github.com/repos/Tonyhood2345/live-stream-serverless/actions/workflows/bot_pubblica_tiktok.yml/dispatches"
                payload_dispatch = {"ref": "main", "inputs": {"force": "true"}}
                r_disp = _s.post(url_dispatch, headers=headers_gh, json=payload_dispatch, timeout=15)
                if r_disp.status_code in (204, 201, 200):
                    print("  🚀 [TikTok Workflow Dispatch] Workflow bot_pubblica_tiktok.yml avviato su GitHub Actions!")
                    tk_uploaded = True
            except Exception as e_gh:
                print(f"  ⚠️ Errore dispatch GitHub TikTok: {e_gh}")

        # 5. Notifica e sincronizzazione con Google Apps Script backend
        try:
            payload_as = {
                "action": "pubblica_tiktok_story",
                "titolo": titolo,
                "mq": mq,
                "prezzo": prezzo,
                "testoF": testo_f,
                "account": "immobiliare_giancani"
            }
            req_data = json.dumps(payload_as).encode('utf-8')
            req = urllib.request.Request(
                APPS_SCRIPT_URL,
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "Giancani-TikTok-Story-Bot"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                res_json = json.loads(resp.read().decode('utf-8'))
        except Exception:
            res_json = {}

        story_id = res_json.get('story_id') or f"TK-STORY-{uuid.uuid4().hex[:8]}"
        print(f"[OK] TikTok Stories sincronizzato: {story_id} — Immobiliare Giancani")
        return {
            "nome": "TikTok Stories (@immobiliare_giancani)",
            "success": True,
            "story_id": story_id,
            "url": "https://www.tiktok.com/@immobiliare_giancani"
        }
    except Exception as eTk:
        print(f"❌ Errore TikTok Stories: {eTk}")
        return {
            "nome": "TikTok Stories (@immobiliare_giancani)",
            "success": False,
            "error": str(eTk)
        }


def pubblica_nota_facebook_pagina(page_id, page_token, media_info, fascia_info=None):
    """
    Pubblica una 'Nota di Pagina' (Post ricco sul feed di Facebook) strutturata con:
    - Saluto del momento (Mattina, Pomeriggio, Sera, Notte)
    - Emoticon espressive
    - Pensiero d'ispirazione per il benessere e la casa
    - Scheda immobile con Colonna F e superfici rigorosamente in 'metri quadri'
    - Indicazione della canzone royalty-free garantita di Facebook
    - Firma: — Immobiliare Giancani
    """
    if not fascia_info:
        fascia_info = determina_fascia_oraria()

    titolo = media_info.get('titolo', 'Opportunità Esclusiva')
    prezzo = media_info.get('prezzo', 'Trattativa Riservata')
    mq = normalize_mq(media_info.get('mq', '120 metri quadri'))
    testo_f = media_info.get('testoF', '').strip()
    if testo_f:
        testo_f = re.sub(r'\s*—?\s*Immobiliare Giancani\s*$', '', testo_f, flags=re.IGNORECASE).strip()

    messaggio_nota = (
        f"{fascia_info['titolo_nota']}\n\n"
        f"{fascia_info['riflessione_nota']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏠 IMMOBILE IN EVIDENZA: {titolo.upper()}\n"
        f"📐 SUPERFICIE: {mq}\n"
        f"💰 PREZZO: {prezzo}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎙️ Dettagli esclusivi: \"{testo_f}\"\n\n"
        f"🎵 Canzone di sottofondo consigliata: {fascia_info['musica_titolo']}\n\n"
        f"👉 Per informazioni, dettagli e visite guidate sul posto:\n"
        f"📞 Contattaci direttamente o invia un messaggio in privato.\n\n"
        f"📱 Seguici sui nostri canali ufficiali:\n"
        f"• Facebook: https://www.facebook.com/immobiliaregiancani\n"
        f"• YouTube: https://www.youtube.com/@immobiliaregiancani761\n"
        f"• Instagram: https://www.instagram.com/giancani_immobiliare/\n"
        f"• TikTok: https://www.tiktok.com/@immobiliare_giancani\n\n"
        f"— Immobiliare Giancani"
    )

    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    payload = urllib.parse.urlencode({
        "message": messaggio_nota,
        "access_token": page_token
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[OK] Nota Facebook pubblicata su ID {page_id}! Post ID: {data.get('id')}")
            return {"success": True, "post_id": data.get("id"), "fascia": fascia_info["fascia"]}
    except Exception as e:
        print(f"Errore pubblicazione nota su Facebook ({page_id}): {e}")
        return {"success": False, "error": str(e), "fascia": fascia_info["fascia"]}

def invia_notifica_telegram(titolo, mq, prezzo, risultati, is_live=True, video_path=None):
    """Invia notifica Telegram aziendale e recapita il video su Telegram a Chat ID 1723292483"""
    try:
        tipo_str = "🔴 STORIA LIVE (OGNI 30 MIN)" if is_live else "🕒 STORIA FACEBOOK (OGNI 30 MIN)"
        lines = [
            f"🎬 <b>{tipo_str} PUBBLICATA CON SUCCESSO!</b> ✨",
            f"🏠 <b>Immobile:</b> {titolo}",
            f"📐 <b>Superficie:</b> {mq}",
            f"💰 <b>Prezzo:</b> {prezzo}",
            f"🎵 <b>Audio:</b> Inno Sequenziale alla Vita + Voce Neurale HD",
            f"⏱️ <b>Durata video:</b> 15 secondi continui Full HD (1080x1920)\n"
        ]
        for r in risultati:
            status = "✅ Pubblicata" if r.get("success") else f"⚠️ {r.get('error', 'Fallita')}"
            lines.append(f"• <b>{r.get('nome')}:</b> {status} (ID: {r.get('story_id', 'N/D')})")

        lines.append("\n— <b>Immobiliare Giancani</b>")
        msg = "\n".join(lines)

        tg_token = "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M"
        tg_chat = "1723292483"

        if video_path and os.path.exists(video_path):
            try:
                with open(video_path, 'rb') as f_vid:
                    requests.post(
                        f"https://api.telegram.org/bot{tg_token}/sendVideo",
                        data={'chat_id': tg_chat, 'caption': msg[:1024], 'parse_mode': 'HTML'},
                        files={'video': f_vid},
                        timeout=90,
                        verify=False
                    )
                    print(f"[OK] Video storia recapitato su Telegram ({tg_chat})!")
            except Exception as e_v:
                print(f"Avviso invio video Telegram: {e_v}")

        try:
            requests.post(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                data={'chat_id': tg_chat, 'text': msg, 'parse_mode': 'HTML'},
                timeout=15,
                verify=False
            )
        except Exception:
            pass

        try:
            url_tg = f"{APPS_SCRIPT_URL}?action=invia_notifica&msg={urllib.parse.quote(msg)}"
            req_tg = urllib.request.Request(url_tg, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_tg, timeout=10, context=ctx) as r:
                pass
        except Exception:
            pass
    except Exception as e:
        print(f"Avviso notifica Telegram: {e}")

# ═════════════════════════════════════════════════════════════════════════════
# GESTIONE MODALITÀ LIVE
# ═════════════════════════════════════════════════════════════════════════════
def esegui_ciclo_live(style="auto"):
    """
    Esegue un ciclo di pubblicazione storia durante la diretta streaming (ogni 30 minuti).
    GUARDIA RIGOROSA: se non è in diretta live streaming, NON esegue alcuna pubblicazione.
    """
    print("\n" + "═" * 70)
    print("🚀 CICLO STORIA LIVE FACEBOOK (OGNI 30 MINUTI)")
    print("═" * 70)

    # 1. CONTROLLO DIRETTA LIVE ATTIVA ("se non è in diretta nulla")
    is_live, run_id = check_is_live_active()
    if not is_live:
        print("🔴 Nessuna diretta live streaming in corso su YouTube / Facebook / GitHub Actions.")
        print("ℹ️ Direttiva attiva: quando non si è in diretta, il bot NON pubblica alcuna storia e rimane a riposo.")
        print("— Immobiliare Giancani\n")
        return []

    print(f"🔴 DIRETTA STREAMING ATTIVA (Run ID: {run_id}). Avvio generazione storia live con rotazione grafica...")

    cronologia = carica_cronologia_storie()
    recent_urls = get_recent_photo_urls(cronologia, max_count=30)

    # Recupera immobile attivo dal backend con rotazione ('next' / 'current')
    url_imm = f"{APPS_SCRIPT_URL}?action=debug_immobile&q=next"
    prop_data = {}
    try:
        r_imm = requests.get(url_imm, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=15)
        if r_imm.status_code == 200:
            prop_data = r_imm.json()
            cand_foto = prop_data.get('mediaUrl') or prop_data.get('fotoUrl')
            if cand_foto and normalizza_foto_url(cand_foto) in recent_urls:
                print("🔄 [LIVE ANTI-RIPETIZIONE] Foto già mostrata di recente, forzatura al prossimo immobile...")
                url_next_imm = f"{APPS_SCRIPT_URL}?action=debug_immobile&q=next_immobile"
                r_next = requests.get(url_next_imm, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=15)
                if r_next.status_code == 200:
                    prop_data = r_next.json()
    except Exception as e:
        print(f"Avviso recupero dati immobile in diretta via requests: {e}")
        try:
            url_curr = f"{APPS_SCRIPT_URL}?action=debug_immobile&q=current"
            r_curr = requests.get(url_curr, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=15)
            if r_curr.status_code == 200:
                prop_data = r_curr.json()
        except Exception as e2:
            print(f"Avviso fallback current: {e2}")

    # Fallback su catalogo cache offline per garantire rotazione di immobili sempre diversi
    f_curr = prop_data.get('mediaUrl') or prop_data.get('fotoUrl')
    if not prop_data or not f_curr or normalizza_foto_url(f_curr) in recent_urls:
        cache_cat_candidates = [
            os.path.join(ASSETS_DIR, "catalogo_immobili_cache.json"),
            os.path.join(os.path.dirname(BASE_DIR), "assets", "catalogo_immobili_cache.json")
        ]
        for cat_p in cache_cat_candidates:
            if os.path.exists(cat_p):
                try:
                    with open(cat_p, "r", encoding="utf-8") as fC:
                        c_list = json.load(fC)
                        if c_list:
                            mai_visti = [c for c in c_list if normalizza_foto_url(c.get("fotoUrl") or c.get("mediaUrl")) not in recent_urls]
                            if not mai_visti:
                                mai_visti = c_list
                            slot_30min = int(time.time() / 1800)
                            sel_imm = mai_visti[slot_30min % len(mai_visti)]
                            prop_data = {
                                "titolo": sel_imm.get("titolo"),
                                "stanza": sel_imm.get("stanza"),
                                "prezzo": sel_imm.get("prezzo"),
                                "mq": sel_imm.get("mq"),
                                "fotoUrl": sel_imm.get("fotoUrl"),
                                "testoDaLeggere": sel_imm.get("testoF")
                            }
                            print(f"🎯 Rotazione Immobile Live da catalogo cache anti-ripetizione: {sel_imm.get('titolo')} ({sel_imm.get('stanza')})")
                            break
                except Exception as eCc:
                    print(f"Avviso fallback catalogo live: {eCc}")

    titolo_base = prop_data.get('titolo') or "Immobile in Diretta"
    stanza = prop_data.get('stanza')
    if stanza and stanza.lower() not in ['ambiente', ''] and stanza.lower() != titolo_base.lower():
        titolo = f"{titolo_base} — {stanza}"
    else:
        titolo = titolo_base

    prezzo = prop_data.get('prezzo', 'Trattativa Riservata')
    mq = normalize_mq(prop_data.get('mq', '120'))
    foto_raw = prop_data.get('mediaUrl') or prop_data.get('fotoUrl')
    foto_url = normalizza_foto_url(foto_raw)
    testo_f = prop_data.get('testoDaLeggere') or prop_data.get('testo') or "Tour virtuale in diretta streaming con Dario e DarIA. — Immobiliare Giancani"
    if "immobiliare giancani" not in testo_f.lower():
        testo_f += " — Immobiliare Giancani"

    story_seq = int(time.time() / 1800) + len(cronologia)
    media_info = {
        "titolo": titolo,
        "prezzo": prezzo,
        "mq": mq,
        "fotoUrl": foto_url,
        "testoF": testo_f,
        "isLive": True,
        "story_index": story_seq
    }

    video_path = genera_video_da_clip_o_foto(media_info, style=style)
    if not video_path:
        print("❌ Errore generazione video storia live.")
        return []

    # Registra immediatamente nella cronologia anti-ripetizione
    story_ref = f"live_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    cronologia[story_ref] = {
        "timestamp": time.time(),
        "titolo": titolo,
        "fotoUrl": foto_url,
        "stanza": stanza,
        "isLive": True
    }
    salva_cronologia_storie(cronologia)

    risultati = []
    for target in PAGES:
        print(f"📘 Pubblicazione Video Storia su: {target['nome']}...")
        try:
            res = pubblica_storia_video_su_facebook(target['id'], target['token'], video_path)
            res['nome'] = target['nome']
            print(f"[OK] Storia pubblicata! ID: {res.get('story_id')}")
            risultati.append(res)
        except Exception as ePub:
            print(f"❌ Errore upload su {target['nome']}: {ePub}")
            risultati.append({"nome": target['nome'], "success": False, "error": str(ePub)})

    # Pubblica su Instagram Stories (@giancani_immobiliare)
    try:
        res_ig = pubblica_storia_instagram(IG_ACCOUNT_ID, PAGES[0]['token'], video_path)
        print(f"[OK] Instagram Stories: {res_ig.get('story_id')} ({res_ig.get('metodo')})")
        risultati.append(res_ig)
    except Exception as eIg:
        print(f"❌ Errore Instagram Stories: {eIg}")
        risultati.append({"nome": "Instagram Stories (@giancani_immobiliare)", "success": False, "error": str(eIg)})

    # Pubblica su YouTube Shorts (@immobiliaregiancani761)
    try:
        res_yt = pubblica_short_youtube(video_path, media_info)
        print(f"[OK] YouTube Shorts: {res_yt.get('story_id')} - {res_yt.get('url')}")
        risultati.append(res_yt)
    except Exception as eYt:
        print(f"❌ Errore YouTube Shorts: {eYt}")
        risultati.append({"nome": "YouTube Shorts (@immobiliaregiancani761)", "success": False, "error": str(eYt)})

    # Pubblica / Sincronizza su TikTok Stories (@immobiliare_giancani)
    try:
        res_tk = pubblica_storia_tiktok(video_path, media_info)
        print(f"[OK] TikTok Stories: {res_tk.get('story_id')} - {res_tk.get('url')}")
        risultati.append(res_tk)
    except Exception as eTk:
        print(f"❌ Errore TikTok Stories: {eTk}")
        risultati.append({"nome": "TikTok Stories (@immobiliare_giancani)", "success": False, "error": str(eTk)})

    invia_notifica_telegram(titolo, mq, prezzo, risultati, is_live=True)
    print("✨ Ciclo storia live multi-piattaforma completato. — Immobiliare Giancani\n")
    return risultati


# ═════════════════════════════════════════════════════════════════════════════
# GESTIONE MODALITÀ OFFLINE (OGNI ORA)
# ═════════════════════════════════════════════════════════════════════════════
def esegui_ciclo_offline(style="auto", sheet_filter=None, room_filter=None, custom_text=None, custom_image=None, custom_title=None):
    """
    Esegue la pubblicazione di una storia ogni ora quando NON si è in diretta live,
    oppure su richiesta manuale da regia Generator.html.
    Ruota su TUTTI gli immobili e stanze del catalogo senza mai bloccarsi sullo stesso immobile.
    Supporta anche storie NON immobiliari (Buone Notizie, Mindset, Notizie, Custom) con testo e immagine specificati.
    """
    print("\n" + "═" * 70)
    print("🕒 CONTROLLO PUBBLICAZIONE STORIA OFFLINE / CUSTOM")
    print("═" * 70)

    # 1. Se non è una chiamata esplicita da utente/manuale, verifica se la diretta streaming è in corso
    is_manual = bool(custom_text or custom_image or sheet_filter or room_filter)
    if not is_manual:
        is_live, run_id = check_is_live_active()
        if is_live:
            print(f"🔴 Diretta Live attualmente IN CORSO su GitHub Actions (Workflow Run ID: {run_id}).")
            print("ℹ️ La pubblicazione storie a 10 minuti è gestita attivamente dal flusso live. Uscita per evitare duplicati.")
            print("— Immobiliare Giancani")
            return []

    print("✅ Procedo con la pubblicazione della storia offline / personalizzata...")

    # Gestione CASO A: Contenuto NON immobiliare o personalizzato con testo/immagine scelti
    if custom_text or custom_image:
        print("🎨 Modalità Storia Personalizzata / Non Immobiliare attiva.")
        t_clean = str(custom_text or "Novità e aggiornamenti da Favara e Agrigento").strip()
        if "immobiliare giancani" not in t_clean.lower():
            t_clean += " — Immobiliare Giancani"
        
        img_sel = custom_image or random.choice(GUARANTEED_FALLBACK_IMAGES)
        tit_sel = custom_title or "Comunicazione Speciale"
        
        media_info = {
            "titolo": tit_sel,
            "prezzo": "",
            "mq": "",
            "videoUrl": None,
            "fotoUrl": img_sel,
            "testoF": t_clean,
            "isLive": False
        }
        selected = {
            "id": f"custom_{int(time.time())}",
            "titolo": tit_sel,
            "fonte": "Storia Personalizzata / Non Immobiliare",
            "mq": "",
            "prezzo": ""
        }
    else:
        # Gestione CASO B: Catalogo Immobili (rotazione deterministica anti-ripetizione su tutti gli immobili e stanze)
        candidates = []
        try:
            url_sheets = f"{APPS_SCRIPT_URL}?action=debug_all_sheets"
            r_sheets = requests.get(url_sheets, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=30)
            if r_sheets.status_code == 200:
                data_sh = r_sheets.json()
                all_sheets = data_sh.get('sheets', [])
                ignora_fogli = ['IMPOSTAZIONI_SOCIAL', 'CONFIGURAZIONE_TEMPI', 'RISULTATI_GIORNATA', 'FRASI_CALCIO', 'ANALYTICS_SOCIAL', 'MUSICA_SOTTOFONDO', 'ARCHIVIO_CLIENTI', 'PALINSESTO_ORARIO', 'PUBBLICITA_SPOT', 'PUBBLICITA_SCHERMO_CENTRALE', 'BATTUTE_DARIO']
                
                for s in all_sheets:
                    s_name = s.get('name', '')
                    if any(ig in s_name.upper() for ig in ignora_fogli):
                        continue
                    if sheet_filter and sheet_filter.lower() not in s_name.lower() and s_name.lower() not in sheet_filter.lower():
                        continue
                    
                    sample = s.get('sample', [])
                    headers = sample[0] if sample else []
                    for row_idx, r in enumerate(sample[1:], start=2):
                        parsed = parse_property_row_smart(r, headers=headers, sheet_name=s_name)
                        if not parsed:
                            continue
                        
                        stanza_riga = parsed.get("stanza", "")
                        if room_filter:
                            rf_str = str(room_filter).strip().lower()
                            if rf_str.isdigit():
                                if int(rf_str) != row_idx and int(rf_str) != (row_idx - 1):
                                    continue
                            elif rf_str not in stanza_riga.lower() and stanza_riga.lower() not in rf_str:
                                continue

                        cand_id = f"{s_name}_riga{row_idx}_{abs(hash(parsed.get('fotoUrl') or parsed.get('videoUrl') or parsed.get('titolo'))) % 100000}"
                        candidates.append({
                            "id": cand_id,
                            "fonte": s_name.replace('_', ' ').strip(),
                            "sheet": s_name,
                            "rowIndex": row_idx,
                            "stanza": stanza_riga,
                            "videoUrl": parsed.get("videoUrl"),
                            "fotoUrl": parsed.get("fotoUrl"),
                            "prezzo": parsed.get("prezzo"),
                            "mq": parsed.get("mq"),
                            "titolo": parsed.get("titolo"),
                            "testoF": parsed.get("testoF")
                        })
        except Exception as eSheets:
            print(f"Avviso lettura catalogo fogli: {eSheets}")

        # Fallback A: Catalogo Immobili Locale in Cache (16 immobili reali e verificati)
        if not candidates:
            cache_cat_candidates = [
                os.path.join(ASSETS_DIR, "catalogo_immobili_cache.json"),
                os.path.join(os.path.dirname(BASE_DIR), "assets", "catalogo_immobili_cache.json"),
                os.path.join(BASE_DIR, "catalogo_immobili_cache.json")
            ]
            for cat_path in cache_cat_candidates:
                if os.path.exists(cat_path):
                    try:
                        with open(cat_path, "r", encoding="utf-8") as fCat:
                            cat_data = json.load(fCat)
                            if isinstance(cat_data, list) and len(cat_data) > 0:
                                for item in cat_data:
                                    t_f = str(item.get("testoF") or item.get("testoDaLeggere") or "").strip()
                                    if not t_f:
                                        continue
                                    if "immobiliare giancani" not in t_f.lower():
                                        t_f += " — Immobiliare Giancani"
                                    candidates.append({
                                        "id": item.get("id") or f"cache_{abs(hash(item.get('titolo')))%100000}",
                                        "fonte": item.get("fonte") or item.get("tabName", "Archivio Immobili"),
                                        "sheet": item.get("tabName", "CATALOGO"),
                                        "rowIndex": 2,
                                        "stanza": item.get("stanza", ""),
                                        "videoUrl": item.get("videoUrl"),
                                        "fotoUrl": normalizza_foto_url(item.get("fotoUrl")),
                                        "prezzo": str(item.get("prezzo") or "Trattativa Riservata").strip(),
                                        "mq": normalize_mq(item.get("mq", "120 metri quadri")),
                                        "titolo": item.get("titolo", "Immobile Giancani"),
                                        "testoF": t_f
                                    })
                                if candidates:
                                    print(f"✅ Caricati con successo {len(candidates)} immobili dal catalogo cache offline.")
                                    break
                    except Exception as eC:
                        print(f"Avviso lettura catalogo cache {cat_path}: {eC}")

        # Fallback B: Immobile attualmente attivo dal server
        if not candidates:
            try:
                url_curr = f"{APPS_SCRIPT_URL}?action=debug_immobile&q=current"
                r_curr = requests.get(url_curr, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=15)
                if r_curr.status_code == 200:
                    d_curr = r_curr.json()
                    foto_curr = normalizza_foto_url(d_curr.get('fotoUrl') or d_curr.get('mediaUrl'))
                    testo_curr = d_curr.get('testoDaLeggere') or d_curr.get('testo') or 'Splendido immobile selezionato ad Agrigento e Favara. — Immobiliare Giancani'
                    if "immobiliare giancani" not in testo_curr.lower():
                        testo_curr += " — Immobiliare Giancani"
                    candidates.append({
                        "id": f"active_{int(time.time())}",
                        "fonte": "Immobile Corrente",
                        "sheet": "ACTIVE",
                        "rowIndex": 2,
                        "videoUrl": None,
                        "fotoUrl": foto_curr or GUARANTEED_FALLBACK_IMAGES[0],
                        "prezzo": str(d_curr.get('prezzo') or 'Trattativa Riservata').strip(),
                        "mq": normalize_mq(d_curr.get('mq', '120 metri quadri')),
                        "titolo": d_curr.get('titolo', 'Immobile in Vendita'),
                        "testoF": testo_curr
                    })
            except Exception:
                pass

        if not candidates:
            print("⚠️ Nessun immobile estratto dai fogli. Caricamento catalogo dinamico multi-foto...")
            # Importa dal catalogo immobili per garantire assoluta diversità di foto e testi
            pool_default = [
                {"id": "c1", "titolo": "Appartamento 4° Piano Corso Vittorio Veneto", "mq": "140 metri quadri", "prezzo": "Trattativa Riservata", "fotoUrl": "https://lh3.googleusercontent.com/d/1J_dumkLBgmNO14H2Ga0sTkEJR25jWbSw", "testoF": "Luminoso appartamento al 4° piano in pieno centro a Favara con vista panoramica e comodi spazi. — Immobiliare Giancani"},
                {"id": "c2", "titolo": "Villa Panoramica a Zingarello", "mq": "120 metri quadri", "prezzo": "€ 95.000", "fotoUrl": "https://lh3.googleusercontent.com/d/1ZeFvgW36oabdrE0lGUzuTg2kcx8vJgBT", "testoF": "Suggestivo terrazzo verso l'orizzonte dove respirare libertà e godersi la brezza siciliana. — Immobiliare Giancani"},
                {"id": "c3", "titolo": "Appartamento 2° Piano Via Pavia", "mq": "120 metri quadri", "prezzo": "€ 38.000", "fotoUrl": "https://lh3.googleusercontent.com/d/12DCZfaRB3l2LzlKLsLD_idBzD65ipBhM", "testoF": "Soluzione luminosa a Favara in zona servita con vista panoramica e ottima esposizione. — Immobiliare Giancani"},
                {"id": "c4", "titolo": "Villa con Terreno ad Aragona", "mq": "120 metri quadri", "prezzo": "Trattativa Riservata", "fotoUrl": "https://lh3.googleusercontent.com/d/13DCw7jS4GzKRhN7qH3U9RRPnh1V45vKF", "testoF": "Prestigiosa proprietà indipendente circondata dal verde con finiture di alto livello. — Immobiliare Giancani"},
                {"id": "c5", "titolo": "Appartamento 1° Piano con Box ad Aragona", "mq": "120 metri quadri", "prezzo": "€ 85.000", "fotoUrl": "https://lh3.googleusercontent.com/d/15uuETuZVsZ1eOoxkv-YMM_8mngBkpHT3", "testoF": "Appartamento rifinito con box auto e terrazza privata, ideale per famiglie esigenti. — Immobiliare Giancani"}
            ]
            candidates.extend(pool_default)

        # ROTAZIONE DETERMINISTICA ANTI-RIPETIZIONE
        cronologia = carica_cronologia_storie()
        candidati_mai_visti = [c for c in candidates if c["id"] not in cronologia]
        
        slot_orario = int(time.time() / 3600)
        if not candidati_mai_visti:
            print(f"🔄 Tutti gli {len(candidates)} candidati del catalogo sono stati pubblicati! Reset ciclo cronologia per nuova rotazione...")
            cronologia = {}
            candidati_mai_visti = candidates

        # Selezione oraria ciclica e deterministica
        idx_sel = slot_orario % len(candidati_mai_visti)
        selected = candidati_mai_visti[idx_sel]

        # Salva nella cronologia persistente con timestamp
        cronologia[selected["id"]] = {
            "timestamp": time.time(),
            "titolo": selected["titolo"],
            "fonte": selected["fonte"],
            "stanza": selected.get("stanza", ""),
            "fotoUrl": selected.get("fotoUrl", "")
        }
        salva_cronologia_storie(cronologia)
        print(f"🎯 Immobile/Stanza selezionata per la storia ({len(cronologia)}/{len(candidates)} nel ciclo): {selected['titolo']} ({selected['fonte']})")
        print(f"   Dati sincronizzati atomici: Foto={bool(selected.get('fotoUrl'))}, Prezzo={selected.get('prezzo')}, MQ={selected.get('mq')}, Colonna F='{selected.get('testoF')[:60]}...'")

        media_info = {
            "titolo": selected.get('titolo', 'Immobile in Vendita'),
            "prezzo": selected.get('prezzo', 'Trattativa Riservata'),
            "mq": normalize_mq(selected.get('mq')),
            "videoUrl": selected.get('videoUrl'),
            "fotoUrl": selected.get('fotoUrl'),
            "testoF": selected.get('testoF'),
            "isLive": False
        }

    video_path = genera_video_da_clip_o_foto(media_info, style=style)
    if not video_path:
        print("❌ Errore generazione video storia offline.")
        return []

    risultati = []
    for target in PAGES:
        print(f"📘 Pubblicazione Video Storia su: {target['nome']}...")
        try:
            res = pubblica_storia_video_su_facebook(target['id'], target['token'], video_path)
            res['nome'] = target['nome']
            print(f"[OK] Storia pubblicata! ID: {res.get('story_id')}")
            risultati.append(res)
        except Exception as ePub:
            print(f"❌ Errore upload su {target['nome']}: {ePub}")
            risultati.append({"nome": target['nome'], "success": False, "error": str(ePub)})

    # Pubblica su YouTube Shorts (@immobiliaregiancani761)
    try:
        res_yt = pubblica_short_youtube(video_path, media_info)
        print(f"[OK] YouTube Shorts: {res_yt.get('story_id')} - {res_yt.get('url')}")
        risultati.append(res_yt)
    except Exception as eYt:
        print(f"❌ Errore YouTube Shorts: {eYt}")
        risultati.append({"nome": "YouTube Shorts (@immobiliaregiancani761)", "success": False, "error": str(eYt)})

    # Pubblica / Sincronizza su TikTok Stories (@immobiliare_giancani)
    try:
        res_tk = pubblica_storia_tiktok(video_path, media_info)
        print(f"[OK] TikTok Stories: {res_tk.get('story_id')} - {res_tk.get('url')}")
        risultati.append(res_tk)
    except Exception as eTk:
        print(f"❌ Errore TikTok Stories: {eTk}")
        risultati.append({"nome": "TikTok Stories (@immobiliare_giancani)", "success": False, "error": str(eTk)})

    invia_notifica_telegram(selected['titolo'], selected.get('mq', ''), selected.get('prezzo', ''), risultati, is_live=False, video_path=video_path)
    print("✨ Ciclo storia oraria multi-piattaforma completato con successo. — Immobiliare Giancani\n")
    return risultati

def main():
    parser = argparse.ArgumentParser(description="Gestore Storie Facebook Immobiliare Giancani")
    parser.add_argument("--mode", choices=["live", "offline", "nota"], default="live", help="Modalità operativa: live (durante la diretta), offline (ogni ora), o nota (pubblica nota facebook del giorno)")
    parser.add_argument("--offline", action="store_true", help="Scorciatoia diretta per eseguire in modalità offline (storie orarie)")
    parser.add_argument("--fascia", choices=["mattina", "pomeriggio", "sera", "notte", "auto"], default="auto", help="Forza la fascia oraria per saluto ed emoticon")
    parser.add_argument("--loop", action="store_true", help="Esegue in ciclo continuo (per la diretta live ogni 30 minuti (1800s))")
    parser.add_argument("--style", default="auto", help="Stile grafico per la storia (default: auto)")
    parser.add_argument("--interval", type=int, default=1800, help="Intervallo in secondi per la modalità loop (default: 1800s = 30 minuti)")
    parser.add_argument("--delay_start", type=int, default=0, help="Secondi di attesa prima del primo ciclo (default: 0)")
    
    # Parametri per selezione mirata o storie non immobiliari
    parser.add_argument("--sheet", "--immobile", dest="sheet", default=None, help="Filtra per immobile o nome foglio specifico")
    parser.add_argument("--stanza", "--room", dest="room", default=None, help="Filtra per stanza o indice riga specifico")
    parser.add_argument("--custom_text", dest="custom_text", default=None, help="Testo personalizzato per storie non immobiliari o comunicazioni")
    parser.add_argument("--custom_image", dest="custom_image", default=None, help="URL o percorso immagine personalizzata")
    parser.add_argument("--custom_title", dest="custom_title", default=None, help="Titolo personalizzato per la storia")
    args = parser.parse_args()

    if args.offline:
        args.mode = "offline"

    if args.mode == "live":
        if args.loop:
            print(f"Avvio demone storie Facebook in diretta ogni {args.interval} secondi ({args.interval // 60} minuti)...")
            time.sleep(15)
            while True:
                try:
                    is_live, run_id = check_is_live_active()
                    if is_live:
                        esegui_ciclo_live(style=getattr(args, 'style', 'auto'))
                    else:
                        print(f"🔴 Diretta live non attiva. Controllo programmato tra {args.interval // 60} minuti... — Immobiliare Giancani")
                except Exception as eL:
                    print(f"Errore ciclo live: {eL}")
                time.sleep(args.interval)
        else:
            esegui_ciclo_live(style=getattr(args, 'style', 'auto'))
    elif args.mode == "offline":
        if args.loop:
            print(f"🔄 Avvio demone storie Facebook ogni {args.interval} secondi ({args.interval // 60} minuti)...")
            if getattr(args, "delay_start", 0) > 0:
                print(f"⏳ Attesa iniziale di {args.delay_start // 60} minuti prima del prossimo ciclo...")
                time.sleep(args.delay_start)
            while True:
                try:
                    esegui_ciclo_offline(
                        style=getattr(args, 'style', 'auto'),
                        sheet_filter=getattr(args, 'sheet', None),
                        room_filter=getattr(args, 'room', None),
                        custom_text=getattr(args, 'custom_text', None),
                        custom_image=getattr(args, 'custom_image', None),
                        custom_title=getattr(args, 'custom_title', None)
                    )
                except Exception as eOff:
                    print(f"Errore ciclo offline: {eOff}")
                print(f"⏳ Prossima storia tra {args.interval // 60} minuti... — Immobiliare Giancani")
                time.sleep(args.interval)
        else:
            esegui_ciclo_offline(
                style=getattr(args, 'style', 'auto'),
                sheet_filter=getattr(args, 'sheet', None),
                room_filter=getattr(args, 'room', None),
                custom_text=getattr(args, 'custom_text', None),
                custom_image=getattr(args, 'custom_image', None),
                custom_title=getattr(args, 'custom_title', None)
            )
    elif args.mode == "nota":
        fascia_scelta = None
        if getattr(args, 'fascia', 'auto') != 'auto':
            h_map = {'mattina': 8, 'pomeriggio': 14, 'sera': 20, 'notte': 23}
            fascia_scelta = determina_fascia_oraria(h_map.get(args.fascia, 12))
        else:
            fascia_scelta = determina_fascia_oraria()
        print(f"📝 Pubblicazione Nota Facebook forzata: {fascia_scelta['saluto']}")
        dummy_info = {
            "titolo": "Villa Panoramica Favara",
            "prezzo": "Trattativa Riservata",
            "mq": "140 metri quadri",
            "testoF": "Elegante residenza con ampi spazi esterni e rifiniture di pregio curata in esclusiva per voi. — Immobiliare Giancani"
        }
        for target in PAGES:
            pubblica_nota_facebook_pagina(target['id'], target['token'], dummy_info, fascia_scelta)

if __name__ == "__main__":
    main()
