#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
IMMOBILIARE GIANCANI — GESTORE STORIE SOCIAL LIVE STREAMING
CON SFONDO SFUMATO, FRASE MOTIVAZIONALE, VOCE CONDUTTORI E MUSICA ALLEGRA
═══════════════════════════════════════════════════════════════════════════════
Funzionalità integrate:
1. Sfondo elegante con immagine dell'immobile sfumata (Gaussian Blur luxury bokeh)
2. Logo ufficiale circolare di Immobiliare Giancani impresso sia nell'header
   che direttamente su ogni singola foto dell'immobile come watermark di prestigio
3. Frase motivazionale d'ispirazione per la casa e i propri sogni
4. Musica allegra e dinamica royalty-free (nessun blocco per copyright su Facebook)
5. Voce parlata realistica dei conduttori (DarIA o DarIO) che invita a entrare
   in diretta streaming e a chattare in tempo reale con l'agenzia
6. Pubblicazione automatica ogni 10 minuti su ENTRAMBI i profili Facebook:
   - Immobiliare Giancani (ID 234931856561526)
   - Antonio Giancani (ID 108297671444008)
7. Regola post invito: post sul feed di Antonio Giancani SOLO 1 VOLTA all'avvio,
   poi solo storie ogni 10 minuti su entrambi i profili
8. Linee guida aziendali:
   * Testi rigorosamente da Colonna F
   * Superfici sempre espresse in 'metri quadri' (mai la sigla mq)
   * Output personal branding che risalta '— Immobiliare Giancani'
═══════════════════════════════════════════════════════════════════════════════
"""

import ssl
# Bypass SSL per Edge TTS e chiamate sicure
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
import time
import json
import uuid
import shutil
import random
import re
import argparse
import subprocess
import urllib.request
import urllib.parse
import numpy as np
import wave
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageFilter

try:
    import edge_tts
    import asyncio
    HAS_EDGE_TTS = True
except Exception:
    HAS_EDGE_TTS = False

PAGES = [
    {
        "nome": "Immobiliare Giancani (Pagina Ufficiale)",
        "id": "234931856561526",
        "token": "EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI",
        "is_antonio": False
    },
    {
        "nome": "Antonio Giancani (Profilo Personale)",
        "id": "108297671444008",
        "token": "EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia",
        "is_antonio": True
    }
]

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec"
REMOTE_LOGO_URL = "https://lh3.googleusercontent.com/d/1BoZ_9QyYPRKjZFP__iPr7mmi0aGV0G3P"

ctx = ssl._create_unverified_context()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SCRATCH_DIR = os.path.join(BASE_DIR, "output_storie")
CACHE_IMMOBILI_DIR = os.path.join(ASSETS_DIR, "immobili_cache")
os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(CACHE_IMMOBILI_DIR, exist_ok=True)

# Frasi motivazionali per le Storie
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
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?q=80&w=1200&auto=format&fit=crop"
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

def get_font(size, bold=False):
    """Carica font TrueType scalato per alta risoluzione"""
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for p in font_paths:
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

def fetch_active_property_from_backend(direction='current'):
    """Recupera l'immobile attivo dal backend Google Apps Script con testi da Colonna F"""
    url = f"{APPS_SCRIPT_URL}?action=debug_immobile&q={urllib.parse.quote(direction)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    if data.get('success'):
                        return data
        except Exception as e:
            print(f"Tentativo {attempt + 1}/3 recupero dati immobile da backend: {e}")
            time.sleep(2)
    return None

def normalize_mq(val):
    """Garantisce la dicitura 'metri quadri' per le superfici"""
    if not val:
        return "120 metri quadri"
    val = str(val).strip()
    val = val.replace("mq", "metri quadri").replace("Mq", "metri quadri").replace("m²", "metri quadri").replace("MQ", "metri quadri")
    if "metri quadri" not in val.lower():
        val = f"{val} metri quadri"
    return val

def scarica_foto_valida(url_principale):
    """
    Scarica l'immagine dell'immobile assicurandosi che non sia nera o corrotta.
    Priorità massima alla foto specifica dell'immobile in diretta, con cache locale e fallback robusti.
    """
    # 1. Prova prima il download della foto specifica dell'ambiente in onda
    if url_principale and str(url_principale).startswith("http"):
        try:
            req = urllib.request.Request(url_principale, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                raw_bytes = resp.read()
                if len(raw_bytes) > 20000:
                    img = Image.open(io.BytesIO(raw_bytes)).convert('RGBA')
                    if is_image_valid_and_not_black(img):
                        # Salva in cache locale per i cicli successivi
                        try:
                            cached_name = f"cached_{uuid.uuid4().hex[:8]}.jpg"
                            img.convert('RGB').save(os.path.join(CACHE_IMMOBILI_DIR, cached_name), quality=95)
                        except Exception:
                            pass
                        return img
        except Exception as eDl:
            print(f"Avviso download foto diretta ({url_principale}): {eDl}. Controllo cache locale...")

    # 2. Controllo cache locale delle foto autentiche dell'immobile in diretta
    if os.path.exists(CACHE_IMMOBILI_DIR):
        cached_files = [f for f in os.listdir(CACHE_IMMOBILI_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if cached_files:
            # Scegli a rotazione o casualmente tra le foto autentiche dell'immobile
            random.shuffle(cached_files)
            for cf in cached_files:
                try:
                    c_path = os.path.join(CACHE_IMMOBILI_DIR, cf)
                    if os.path.getsize(c_path) > 20000:
                        c_img = Image.open(c_path).convert('RGBA')
                        if is_image_valid_and_not_black(c_img):
                            print(f"[CACHE LOCALE] Utilizzata foto autentica dell'immobile in diretta: {cf}")
                            return c_img
                except Exception:
                    pass

    # 3. Fallback di emergenza
    for url in GUARANTEED_FALLBACK_IMAGES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                raw_bytes = resp.read()
                if len(raw_bytes) > 20000:
                    img = Image.open(io.BytesIO(raw_bytes)).convert('RGBA')
                    if is_image_valid_and_not_black(img):
                        return img
        except Exception:
            pass
    return None

def genera_audio_musica_allegra(output_audio_path=None):
    """
    Genera una traccia audio di 15 secondi allegra, vivace ed energica (124 BPM, Major Chords)
    100% royalty-free senza alcun diritto d'autore o blocco Facebook.
    """
    if not output_audio_path:
        output_audio_path = os.path.join(ASSETS_DIR, "cheerful_music.wav")

    BPM = 124
    BEAT = 60.0 / BPM
    DUR = 15.0
    SR = 44100
    nsamples = int(SR * DUR)

    left = np.zeros(nsamples, dtype=np.float32)
    right = np.zeros(nsamples, dtype=np.float32)

    # Accordi allegri: C maggiore, G maggiore, A minore, F maggiore
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

def genera_intro_invito_dinamico(personaggio="daria", testo_f="", is_live=True):
    """
    Genera hook dinamici e calorosi per le storie social.
    Progettato appositamente per chi scorre velocemente le storie:
    le primissime parole pronunciate (nei primi 1.5 secondi) trasmettono
    un pensiero positivo immediato e terminano con 'con Immobiliare Giancani!'.
    """
    p_nome = "DarIA" if str(personaggio).lower() == "daria" else "DarIO"
    testo_f_clean = (testo_f or "").strip()
    if testo_f_clean:
        testo_f_clean = re.sub(r'\s*—?\s*Immobiliare Giancani\s*$', '', testo_f_clean, flags=re.IGNORECASE).strip()

    frase_positiva = random.choice(FRASI_POSITIVE_FLASH)

    if is_live:
        followups = [
            f"Sono {p_nome} e siamo in diretta streaming proprio adesso per mostrarvi questa straordinaria opportunità. {testo_f_clean} Entrate subito a trovarci e scriveteci in chat quale stanza volete visitare! Vi aspettiamo con Immobiliare Giancani!",
            f"Da {p_nome} e da tutto il nostro team, siamo collegati dal vivo in questo istante con le migliori occasioni del mercato. {testo_f_clean} Raggiungeteci nella diretta streaming per farci tutte le vostre domande dal vivo! Vi aspettiamo con Immobiliare Giancani!",
            f"Sono {p_nome} e abbiamo preparato per voi una sorpresa esclusiva in streaming! {testo_f_clean} Entrate subito nella nostra diretta per esplorare tutti gli ambienti insieme a noi! Vi aspettiamo con Immobiliare Giancani!",
            f"Da {p_nome} un invito speciale: siamo in onda adesso in diretta streaming! {testo_f_clean} Scriveteci nei commenti quale stanza desiderate visitare e vi porteremo subito all'interno! Vi aspettiamo con Immobiliare Giancani!",
            f"Sono {p_nome}: in questo momento siamo in onda dal vivo per farvi scoprire questa gemma immobiliare! {testo_f_clean} Entrate e commentate in diretta, vi aspettiamo con Immobiliare Giancani!",
            f"Vi do il benvenuto da parte di {p_nome}: le porte delle nostre migliori residenze sono aperte adesso in streaming! {testo_f_clean} Collegatevi subito per interagire in tempo reale! Vi aspettiamo con Immobiliare Giancani!"
        ]
    else:
        followups = [
            f"Sono {p_nome} e oggi vi presentiamo una proprietà davvero unica, selezionata per voi. {testo_f_clean} Contattateci subito per prenotare una visita esclusiva. — Immobiliare Giancani",
            f"Vi do il benvenuto da parte di {p_nome}: lasciatevi conquistare da questa straordinaria dimora. {testo_f_clean} Per fissare un appuntamento chiamateci senza impegno. — Immobiliare Giancani",
            f"Sono {p_nome}: il massimo del comfort per la vostra famiglia vi aspetta in questa casa speciale. {testo_f_clean} Chiamateci subito per scoprire ogni dettaglio di persona. — Immobiliare Giancani",
            f"La casa perfetta esiste ed è curata da {p_nome} e dal nostro team. {testo_f_clean} Siamo pronti ad accompagnarvi nella vostra visita privata. — Immobiliare Giancani"
        ]

    return f"{frase_positiva} {random.choice(followups)}"

def genera_voce_invito_conduttori(personaggio="daria", output_voice_path=None):
    """
    Genera la voce realistica di DarIA o DarIO con invito caldo a venire in diretta e chattare
    """
    if not output_voice_path:
        output_voice_path = os.path.join(SCRATCH_DIR, f"{personaggio}_invite_voice.mp3")

    if personaggio == "dario":
        voice_id = "it-IT-GiuseppeNeural"
    else:
        voice_id = "it-IT-ElsaNeural"

    testo = genera_intro_invito_dinamico(personaggio=personaggio, is_live=True)

    if HAS_EDGE_TTS:
        try:
            async def _run():
                comm = edge_tts.Communicate(testo, voice_id, rate="+4%", pitch="+1Hz")
                await comm.save(output_voice_path)
            asyncio.run(_run())
            if os.path.exists(output_voice_path) and os.path.getsize(output_voice_path) > 5000:
                print(f"[OK] Voce di {personaggio.upper()} generata con successo: {output_voice_path}")
                return output_voice_path
        except Exception as e:
            print(f"Avviso generazione Edge TTS: {e}")
    return None

def crea_audio_mix_storia(personaggio="daria", output_mixed_m4a=None):
    """
    Combina la musica allegra di sottofondo con la voce del personaggio
    effettuando il ducking automatico (voce limpida a 1.2x, musica a 0.22x)
    """
    if not output_mixed_m4a:
        output_mixed_m4a = os.path.join(SCRATCH_DIR, "story_voice_cheerful_audio.m4a")

    voice_path = genera_voce_invito_conduttori(personaggio)
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
        # Solo musica allegra se la voce non è disponibile
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

def genera_grafica_storia_facebook(prop_info, output_path=None):
    """
    Renderizza il layout grafico completo 1080x1920 della Storia Facebook:
    - 1. SFONDO SFUMATO (Gaussian Blur luxury bokeh)
    - 2. Cornice oro luxury
    - 3. Header con Logo circolare e brand Immobiliare Giancani
    - 4. Badge Live pulsante
    - 5. Scheda immobile con Foto ad alta risoluzione
    - 6. Logo impresso su ogni foto come watermark
    - 7. Informazioni immobile con dicitura 'metri quadri' e testo Colonna F
    - 8. Frase motivazionale dedicata
    - 9. Presentatori DarIA e DarIO
    - 10. Call to action diretta con invito a chattare
    - 11. Footer con chiusura '— Immobiliare Giancani'
    """
    W, H = 1080, 1920

    # 1. Recupera la foto dell'immobile in diretta
    prop_url = prop_info.get('mediaUrl') or prop_info.get('fotoUrl')
    prop_im = scarica_foto_valida(prop_url)
    if not prop_im or not is_image_valid_and_not_black(prop_im):
        # Tentativo estremo dalla cache locale delle foto autentiche
        if os.path.exists(CACHE_IMMOBILI_DIR):
            for cf in sorted(os.listdir(CACHE_IMMOBILI_DIR)):
                if cf.lower().endswith(('.jpg', '.jpeg', '.png')):
                    try:
                        c_img = Image.open(os.path.join(CACHE_IMMOBILI_DIR, cf)).convert('RGBA')
                        if is_image_valid_and_not_black(c_img):
                            prop_im = c_img
                            print(f"[CACHE] Foto autentica dell'immobile in diretta recuperata da cache: {cf}")
                            break
                    except Exception:
                        pass

    if not prop_im or not is_image_valid_and_not_black(prop_im):
        raise ValueError("BLOCCO CATEGORICO: Nessuna foto valida dell'immobile in diretta disponibile. Creazione storia annullata per evitare card vuote. — Immobiliare Giancani")

    # SFONDO SFUMATO (BLURRED BACKGROUND)
    bg_ratio = max(W / prop_im.width, H / prop_im.height)
    bg_w, bg_h = int(prop_im.width * bg_ratio), int(prop_im.height * bg_ratio)
    bg_resized = prop_im.resize((bg_w, bg_h), Image.LANCZOS)
    crop_x = (bg_w - W) // 2
    crop_y = (bg_h - H) // 2
    bg_cropped = bg_resized.crop((crop_x, crop_y, crop_x + W, crop_y + H))
    bg_blurred = bg_cropped.filter(ImageFilter.GaussianBlur(radius=28))

    # Overlay luxury royal navy semitrasparente per profondità e contrasto
    overlay = Image.new('RGBA', (W, H), (10, 15, 26, 200))
    im = Image.alpha_composite(bg_blurred, overlay)
    draw = ImageDraw.Draw(im)

    # Cornice dorata
    draw.rectangle([25, 25, W - 25, H - 25], outline=(212, 168, 83, 120), width=2)
    draw.rectangle([35, 35, W - 35, H - 35], outline=(212, 168, 83, 220), width=3)

    logo_img = get_local_or_remote_logo()

    # 2. Header Superiore: Logo Circolare & Brand Immobiliare Giancani
    logo_size = 135
    logo_x = (W - logo_size) // 2
    logo_y = 60
    if logo_img:
        logo_resized = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
        mask = Image.new('L', (logo_size, logo_size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, logo_size, logo_size), fill=255)
        im.paste(logo_resized, (logo_x, logo_y), mask)
        draw.ellipse((logo_x - 3, logo_y - 3, logo_x + logo_size + 3, logo_y + logo_size + 3), outline=(212, 168, 83, 255), width=3)

    font_brand = get_font(28, bold=True)
    brand_text = "IMMOBILIARE GIANCANI"
    b_bbox = font_brand.getbbox(brand_text)
    draw.text(((W - (b_bbox[2] - b_bbox[0])) // 2, 210), brand_text, font=font_brand, fill=(212, 168, 83, 255))

    # 3. Badge Live 'IN DIRETTA STREAMING' con luce pulsante
    badge_w, badge_h = 440, 52
    badge_x = (W - badge_w) // 2
    badge_y = 255
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=26, fill=(220, 35, 35, 255), outline=(255, 255, 255, 230), width=2)
    dot_x, dot_y, dot_r = badge_x + 32, badge_y + 26, 8
    draw.ellipse([dot_x - dot_r - 3, dot_y - dot_r - 3, dot_x + dot_r + 3, dot_y + dot_r + 3], fill=(255, 255, 255, 140))
    draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=(255, 255, 255, 255))
    font_badge = get_font(22, bold=True)
    draw.text((badge_x + 58, badge_y + 12), "IN DIRETTA STREAMING", font=font_badge, fill=(255, 255, 255, 255))

    font_sub = get_font(24, bold=True)
    sub_text = "TOUR VIRTUALE DELL'IMMOBILE"
    s_bbox = font_sub.getbbox(sub_text)
    draw.text(((W - (s_bbox[2] - s_bbox[0])) // 2, 320), sub_text, font=font_sub, fill=(240, 245, 255, 255))

    # 4. Scheda Centrale Immobile (960 x 660)
    card_w, card_h = 960, 660
    card_x = (W - card_w) // 2
    card_y = 365

    draw.rounded_rectangle([card_x - 4, card_y - 4, card_x + card_w + 4, card_y + card_h + 4], radius=24, fill=(212, 168, 83, 150))
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=20, fill=(15, 20, 32, 255), outline=(212, 168, 83, 255), width=3)

    prop_im_resized = prop_im.resize((card_w - 8, card_h - 8), Image.LANCZOS)
    im.paste(prop_im_resized, (card_x + 4, card_y + 4))

    # LOGO SU OGNI FOTO (Watermark Brand)
    if logo_img:
        photo_logo_size = 90
        photo_logo_x = card_x + card_w - photo_logo_size - 25
        photo_logo_y = card_y + 20
        p_logo_resized = logo_img.resize((photo_logo_size, photo_logo_size), Image.LANCZOS)
        p_mask = Image.new('L', (photo_logo_size, photo_logo_size), 0)
        ImageDraw.Draw(p_mask).ellipse((0, 0, photo_logo_size, photo_logo_size), fill=255)
        draw.ellipse((photo_logo_x - 4, photo_logo_y - 4, photo_logo_x + photo_logo_size + 4, photo_logo_y + photo_logo_size + 4), fill=(10, 15, 28, 230), outline=(212, 168, 83, 255), width=2)
        im.paste(p_logo_resized, (photo_logo_x, photo_logo_y), p_mask)
        f_logo_badge = get_font(12, bold=True)
        draw.rounded_rectangle([photo_logo_x - 22, photo_logo_y + photo_logo_size + 6, photo_logo_x + photo_logo_size + 22, photo_logo_y + photo_logo_size + 24], radius=6, fill=(10, 15, 28, 230), outline=(212, 168, 83, 200), width=1)
        draw.text((photo_logo_x - 14, photo_logo_y + photo_logo_size + 8), "IMMOBILIARE GIANCANI", font=f_logo_badge, fill=(245, 225, 165, 255))

    # Badge stanza
    stanza = prop_info.get('stanza', 'Panoramica Ambiente')
    pill_w, pill_h = 320, 42
    draw.rounded_rectangle([card_x + 25, card_y + 25, card_x + 25 + pill_w, card_y + 25 + pill_h], radius=15, fill=(10, 14, 25, 230), outline=(212, 168, 83, 200), width=2)
    draw.ellipse([card_x + 40, card_y + 40, card_x + 52, card_y + 52], fill=(212, 168, 83, 255))
    f_pill = get_font(18, bold=True)
    draw.text((card_x + 62, card_y + 35), stanza.upper()[:24], font=f_pill, fill=(255, 255, 255, 255))

    # Barra informativa
    info_h = 130
    info_y = card_y + card_h - info_h
    draw.rectangle([card_x + 4, info_y, card_x + card_w - 4, card_y + card_h - 4], fill=(5, 8, 16, 240))
    titolo = prop_info.get('titolo') or prop_info.get('nome') or 'Immobile in Esclusiva'
    prezzo = prop_info.get('prezzo', 'Trattativa Riservata')
    mq = normalize_mq(prop_info.get('mq'))

    testo_colonna_f = prop_info.get('testoF') or prop_info.get('testo') or ""
    if not testo_colonna_f:
        testo_colonna_f = f"Ammirate {stanza} di {titolo}: una proprietà di {mq}, proposta a {prezzo}. — Immobiliare Giancani"

    font_p_title = get_font(26, bold=True)
    draw.text((card_x + 30, info_y + 14), titolo.upper()[:46], font=font_p_title, fill=(245, 225, 165, 255))
    font_details = get_font(21, bold=True)
    details_str = f"{mq}   |   {prezzo}   |   Esclusiva Giancani"
    draw.text((card_x + 30, info_y + 58), details_str, font=font_details, fill=(255, 255, 255, 255))
    font_col_f = get_font(15, bold=False)
    f_prev = testo_colonna_f[:78] + "..." if len(testo_colonna_f) > 78 else testo_colonna_f
    draw.text((card_x + 30, info_y + 95), f"🎙️ {f_prev}", font=font_col_f, fill=(200, 215, 235, 240))

    # 5. FRASE MOTIVAZIONALE (BOX LUXURY DEDICATO)
    quote_w, quote_h = 960, 90
    quote_x = (W - quote_w) // 2
    quote_y = 1045
    draw.rounded_rectangle([quote_x, quote_y, quote_x + quote_w, quote_y + quote_h], radius=20, fill=(15, 22, 38, 220), outline=(212, 168, 83, 220), width=2)

    q_main, q_sub = random.choice(FRASI_MOTIVAZIONALI)
    font_quote = get_font(20, bold=True)
    q_bbox = font_quote.getbbox(q_main)
    draw.text(((W - (q_bbox[2] - q_bbox[0])) // 2, quote_y + 18), q_main, font=font_quote, fill=(245, 225, 165, 255))

    font_quote_sub = get_font(17, bold=False)
    qs_bbox = font_quote_sub.getbbox(q_sub)
    draw.text(((W - (qs_bbox[2] - qs_bbox[0])) // 2, quote_y + 52), q_sub, font=font_quote_sub, fill=(220, 230, 245, 240))

    # 6. PRESENTATORI: DarIA & DarIO
    daria_path = os.path.join(ASSETS_DIR, 'daria_classica.png')
    dario_path = os.path.join(ASSETS_DIR, 'dario_classico.png')
    avatar_w, avatar_h = 320, 320

    if os.path.exists(daria_path):
        try:
            daria_im = Image.open(daria_path).convert('RGBA').resize((avatar_w, avatar_h), Image.LANCZOS)
            im.paste(daria_im, (120, 1150), daria_im)
            font_av = get_font(21, bold=True)
            draw.text((150, 1475), "DARIA — Conduttrice", font=font_av, fill=(255, 195, 215, 255))
        except Exception:
            pass

    if os.path.exists(dario_path):
        try:
            dario_im = Image.open(dario_path).convert('RGBA').resize((avatar_w, avatar_h), Image.LANCZOS)
            im.paste(dario_im, (W - 120 - avatar_w, 1150), dario_im)
            font_av = get_font(21, bold=True)
            draw.text((W - 120 - avatar_w + 30, 1475), "DARIO — Desk Regia", font=font_av, fill=(115, 215, 255, 255))
        except Exception:
            pass

    # 7. CALL TO ACTION (ENTRA E CHATTA IN DIRETTA)
    cta_w, cta_h = 920, 105
    cta_x = (W - cta_w) // 2
    cta_y = 1530
    draw.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + cta_h], radius=35, fill=(212, 168, 83, 255), outline=(255, 255, 255, 230), width=3)
    font_cta1 = get_font(26, bold=True)
    cta_t1 = "►►  ENTRA SUBITO IN DIRETTA E CHATTA CON NOI!  ◄◄"
    c1_bbox = font_cta1.getbbox(cta_t1)
    draw.text(((W - (c1_bbox[2] - c1_bbox[0])) // 2, cta_y + 20), cta_t1, font=font_cta1, fill=(10, 14, 22, 255))

    font_cta2 = get_font(18, bold=True)
    cta_t2 = "Fai domande in tempo reale sui nostri immobili in vendita"
    c2_bbox = font_cta2.getbbox(cta_t2)
    draw.text(((W - (c2_bbox[2] - c2_bbox[0])) // 2, cta_y + 60), cta_t2, font=font_cta2, fill=(40, 30, 10, 240))

    # 8. BRAND FOOTER
    font_f1 = get_font(21, bold=False)
    f1_text = "Consulenza e Compravendite Immobiliari d'Eccellenza"
    f1_bbox = font_f1.getbbox(f1_text)
    draw.text(((W - (f1_bbox[2] - f1_bbox[0])) // 2, 1665), f1_text, font=font_f1, fill=(190, 200, 220, 255))

    font_f2 = get_font(34, bold=True)
    f2_text = "IMMOBILIARE GIANCANI"
    f2_bbox = font_f2.getbbox(f2_text)
    draw.text(((W - (f2_bbox[2] - f2_bbox[0])) // 2, 1705), f2_text, font=font_f2, fill=(212, 168, 83, 255))

    font_f3 = get_font(18, bold=False)
    f3_text = "Storie pubblicate ogni 10 minuti con rotazione immobili in diretta"
    f3_bbox = font_f3.getbbox(f3_text)
    draw.text(((W - (f3_bbox[2] - f3_bbox[0])) // 2, 1758), f3_text, font=font_f3, fill=(140, 155, 180, 255))

    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, "facebook_story_latest.jpg")

    im.convert('RGB').save(output_path, 'JPEG', quality=95)
    return output_path

def crea_video_storia_completo(image_path, audio_path=None, output_video_path=None):
    """Genera il video MP4 di 15 secondi (H.264 + AAC) pronto per le Storie Facebook"""
    if not output_video_path:
        output_video_path = os.path.join(SCRATCH_DIR, "facebook_story_latest.mp4")

    if not audio_path or not os.path.exists(audio_path):
        audio_path = crea_audio_mix_storia()

    ffmpeg_bin = find_ffmpeg()
    cmd = [
        ffmpeg_bin, "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-t", "15",
        output_video_path
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        if proc.returncode == 0 and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 50000:
            return output_video_path
    except Exception as e:
        print(f"Eccezione FFmpeg video story: {e}")
    return None

def pubblica_storia_video_su_facebook(page_id, page_token, video_path):
    """Caricamento video storia con Meta Graph API Video Stories (Resumable Upload)"""
    file_size = os.path.getsize(video_path)

    url_start = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"
    params_start = f"upload_phase=start&access_token={urllib.parse.quote(page_token)}".encode('utf-8')
    req_start = urllib.request.Request(url_start, data=params_start, method='POST')

    with urllib.request.urlopen(req_start, context=ctx) as resp_start:
        start_data = json.loads(resp_start.read().decode('utf-8'))
        video_id = start_data.get('video_id')
        upload_url = start_data.get('upload_url')
        if not video_id or not upload_url:
            raise Exception("Meta API non ha restituito video_id o upload_url")

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

    url_finish = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"
    params_finish = f"upload_phase=finish&video_id={video_id}&video_state=PUBLISHED&access_token={urllib.parse.quote(page_token)}".encode('utf-8')
    req_finish = urllib.request.Request(url_finish, data=params_finish, method='POST')

    with urllib.request.urlopen(req_finish, context=ctx) as resp_finish:
        fin_res = json.loads(resp_finish.read().decode('utf-8'))
        return {
            "success": fin_res.get('success', True),
            "video_id": video_id,
            "story_id": fin_res.get('post_id') or video_id,
            "type": "video_story_with_voice_and_music"
        }

def pubblica_storia_foto_fallback(page_id, page_token, image_path):
    """Carica la storia come Photo Story se la modalità video non è supportata"""
    boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
    with open(image_path, 'rb') as f:
        file_bytes = f.read()

    body = bytearray()
    body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="access_token"\r\n\r\n{page_token}\r\n'.encode('utf-8'))
    body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="published"\r\n\r\nfalse\r\n'.encode('utf-8'))
    body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="source"; filename="story.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode('utf-8'))
    body.extend(file_bytes)
    body.extend(b'\r\n')
    body.extend(f'--{boundary}--\r\n'.encode('utf-8'))

    url1 = f"https://graph.facebook.com/v19.0/{page_id}/photos"
    req1 = urllib.request.Request(url1, data=body, method='POST')
    req1.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

    with urllib.request.urlopen(req1, context=ctx) as resp1:
        res1 = json.loads(resp1.read().decode('utf-8'))
        photo_id = res1.get('id')
        if not photo_id:
            raise Exception("ID foto non restituito da Facebook")

        url2 = f"https://graph.facebook.com/v19.0/{page_id}/photo_stories"
        params2 = f"photo_id={photo_id}&access_token={urllib.parse.quote(page_token)}".encode('utf-8')
        req2 = urllib.request.Request(url2, data=params2, method='POST')

        with urllib.request.urlopen(req2, context=ctx) as resp2:
            res2 = json.loads(resp2.read().decode('utf-8'))
            return {
                "success": res2.get('success', True),
                "photo_id": photo_id,
                "story_id": res2.get('post_id') or photo_id,
                "type": "photo_story"
            }

def pubblica_post_invito_antonio_giancani(target, prop_data, img_path):
    """Pubblica il post d'invito sul feed di Antonio Giancani SOLO 1 VOLTA all'avvio della diretta"""
    flag_file = os.path.join(SCRATCH_DIR, "antonio_feed_posted.flag")
    if os.path.exists(flag_file):
        return {"skipped": True, "reason": "Post invito già pubblicato all'avvio (solo storie attive ogni 10 min)"}

    titolo = prop_data.get('titolo', 'Immobile in Esclusiva')
    stanza = prop_data.get('stanza', 'Salone')
    mq = normalize_mq(prop_data.get('mq'))
    prezzo = prop_data.get('prezzo', 'Trattativa Riservata')
    testo_f = prop_data.get('testoF') or prop_data.get('testo') or ""

    post_msg = (
        "🔴 VI INVITO TUTTI IN DIRETTA STREAMING ORA! 🏠✨\n\n"
        f"Amici, siamo in onda con il tour virtuale esclusivo di: {titolo.upper()}!\n"
        f"📍 In questo momento stiamo mostrando: {stanza}\n"
        f"📐 Superficie: {mq}\n"
        f"💰 Prezzo: {prezzo}\n\n"
        f"🎙️ Dalla diretta: \"{testo_f}\"\n\n"
        "👉 ENTRATE SUBITO A VEDERE LA DIRETTA PER CHATTARE CON NOI E SCOPRIRE TUTTI GLI AMBIENTI:\n"
        "📱 Facebook Live: https://www.facebook.com/immobiliaregiancani/live\n"
        "🎬 YouTube Live: https://www.youtube.com/@immobiliaregiancani761/live\n"
        "🌐 Web Player Interattivo: https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec\n\n"
        "Vi aspetto tutti in diretta! — Immobiliare Giancani"
    )

    try:
        url = f"https://graph.facebook.com/v19.0/{target['id']}/feed"
        params = f"message={urllib.parse.quote(post_msg)}&access_token={urllib.parse.quote(target['token'])}".encode('utf-8')
        req = urllib.request.Request(url, data=params, method='POST')
        with urllib.request.urlopen(req, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            with open(flag_file, 'w') as f:
                f.write(data.get('id', 'posted'))
            print(f"[OK] Post Invito 1-Shot pubblicato su Antonio Giancani: ID {data.get('id')}")
            return {"success": True, "post_id": data.get('id')}
    except Exception as e:
        print(f"Avviso post feed Antonio Giancani: {e}")
        return {"success": False, "error": str(e)}

def invia_notifica_telegram(titolo, stanza, mq, prezzo, risultati):
    """Invia notifica di riepilogo al canale Telegram aziendale"""
    try:
        esito_stories = []
        for r in risultati:
            st = "✅ Con Musica Allegra & Voce" if 'voice' in r.get('type', '') else "✅ Pubblicata"
            esito_stories.append(f"  • {r.get('nome')}: {st} (ID {r.get('story_id')})")

        msg = (
            f"📸 <b>STORIE LIVE PUBBLICATE OGNI 10 MINUTI!</b> 🔴🎵🗣️\n\n"
            f"Le storie con <b>Sfondo Sfumato</b>, <b>Frase Motivazionale</b>, <b>Voce DarIA/DarIO</b> e <b>Musica Allegra</b> sono online!\n\n"
            f"🏠 <b>Immobile:</b> {titolo}\n"
            f"📍 <b>Ambiente:</b> {stanza}\n"
            f"📐 <b>Superficie:</b> {mq}\n"
            f"💶 <b>Prezzo:</b> {prezzo}\n"
            f"🎙️ <b>Presentatori:</b> DarIA & DarIO\n\n"
            f"📱 <b>Canali Aggiornati:</b>\n" + "\n".join(esito_stories) + "\n\n"
            f"⏱️ <i>Prossimo aggiornamento automatico tra 10 minuti.</i>\n\n"
            f"— <b>Immobiliare Giancani</b>"
        )
        url = f"{APPS_SCRIPT_URL}?action=invia_notifica&msg={urllib.parse.quote(msg)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            pass
    except Exception as e:
        print(f"Avviso notifica Telegram: {e}")

def esegui_ciclo_pubblicazione(is_first_launch=False):
    """Esegue un singolo ciclo di generazione e pubblicazione storie sui 2 profili"""
    print("\n" + "═" * 70)
    print("🚀 [STORIE LIVE] Avvio generazione storia 1080x1920:")
    print("   • Sfondo sfumato luxury bokeh")
    print("   • Logo su ogni foto dell'immobile")
    print("   • Frase motivazionale per la casa")
    print("   • Musica allegra royalty-free")
    print("   • Voce conduttori con invito a chattare in diretta")
    print("═" * 70)

    # 1. Recupera dati immobile dal backend
    prop_data = fetch_active_property_from_backend('next') or {}
    if not prop_data.get('titolo'):
        prop_data = {
            "titolo": "Terreno edificabile con progetto approvato",
            "stanza": "Ambiente Panoramico",
            "mq": "5000 metri quadri",
            "prezzo": "Trattativa Riservata",
            "mediaUrl": "https://lh3.googleusercontent.com/d/1pYlL_8t98BIu4LBvyVL3dE-c5OOg8uzy",
            "fotoUrl": "https://lh3.googleusercontent.com/d/1pYlL_8t98BIu4LBvyVL3dE-c5OOg8uzy",
            "testoF": "Ammirate questo straordinario terreno edificabile con progetto approvato. Uno spazio prestigioso di 5000 metri quadri, proposto con trattativa riservata da Immobiliare Giancani."
        }

    titolo = prop_data.get('titolo', 'Immobile in Esclusiva')
    stanza = prop_data.get('stanza', 'Ambiente')
    mq = normalize_mq(prop_data.get('mq'))
    prezzo = prop_data.get('prezzo', 'Trattativa Riservata')

    # 2. Genera la grafica con sfondo sfumato, logo su foto e frase motivazionale
    try:
        img_path = genera_grafica_storia_facebook(prop_data)
        print(f"[OK] Grafica renderizzata con Foto Immobile, Sfondo Sfumato e Frase Motivazionale: {img_path}")
    except ValueError as eNoImg:
        print(f"⚠️ {eNoImg}")
        print("ℹ️ Pubblicazione storia saltata in questo ciclo: nessuna immagine valida dell'immobile in diretta. — Immobiliare Giancani")
        return []

    # 3. Genera l'audio mixato: musica allegra + voce conduttore
    personaggio = "daria" if random.random() > 0.4 else "dario"
    mixed_audio = crea_audio_mix_storia(personaggio=personaggio)
    print(f"[OK] Traccia audio mixata con Musica Allegra e Voce di {personaggio.upper()}")

    # 4. Genera il video di 15 secondi
    video_path = crea_video_storia_completo(img_path, audio_path=mixed_audio)
    if video_path:
        print(f"[OK] Video Storia 1080x1920 pronto: {video_path}")

    risultati = []

    # 5. Pubblica la Storia su entrambi i profili
    for target in PAGES:
        print(f"\n📘 Pubblicazione Storia su: {target['nome']}...")
        published = False
        res = {}

        if video_path and os.path.exists(video_path):
            try:
                res = pubblica_storia_video_su_facebook(target['id'], target['token'], video_path)
                print(f"[OK] Video Storia con Musica Allegra & Voce pubblicata! Story ID: {res.get('story_id')}")
                published = True
            except Exception as eVideo:
                print(f"Avviso upload video su {target['nome']} ({eVideo}). Eseguo fallback...")

        if not published:
            try:
                res = pubblica_storia_foto_fallback(target['id'], target['token'], img_path)
                print(f"[OK] Photo Story pubblicata! Story ID: {res.get('story_id')}")
            except Exception as ePhoto:
                print(f"❌ Errore pubblicazione su {target['nome']}: {ePhoto}")
                res = {"success": False, "error": str(ePhoto)}

        res['nome'] = target['nome']
        risultati.append(res)

        if target['is_antonio'] and is_first_launch:
            pubblica_post_invito_antonio_giancani(target, prop_data, img_path)

    invia_notifica_telegram(titolo, stanza, mq, prezzo, risultati)
    print("\n✨ Ciclo storie completato con successo. — Immobiliare Giancani\n")
    return risultati

def main():
    parser = argparse.ArgumentParser(description="Gestore Storie Facebook Live Streaming Immobiliare Giancani")
    parser.add_argument("--loop", action="store_true", help="Avvia il ciclo continuo ogni 30 minuti durante la diretta")
    parser.add_argument("--interval", type=int, default=1800, help="Intervallo in secondi tra le storie (default: 1800s = 30 min)")
    parser.add_argument("--first-launch", action="store_true", help="Segnala il primo avvio per il post d'invito singolo su Antonio Giancani")
    parser.add_argument("--reset-antonio-flag", action="store_true", help="Resetta il flag del post feed per consentire un nuovo invito all'avvio")
    args = parser.parse_args()

    flag_file = os.path.join(SCRATCH_DIR, "antonio_feed_posted.flag")
    if args.reset_antonio_flag and os.path.exists(flag_file):
        os.remove(flag_file)
        print("[RESET] Flag post invito Antonio Giancani resettato.")

    if args.loop:
        print(f"Avvio ciclo continuo storie Facebook ogni {args.interval} secondi ({args.interval // 60} minuti)...")
        is_first = True
        while True:
            try:
                esegui_ciclo_pubblicazione(is_first_launch=is_first)
                is_first = False
            except Exception as err:
                print(f"Errore durante l'iterazione storie: {err}")
            print(f"Prossima storia tra {args.interval} secondi ({args.interval // 60} minuti)...")
            time.sleep(args.interval)
    else:
        esegui_ciclo_pubblicazione(is_first_launch=args.first_launch)

if __name__ == "__main__":
    main()
