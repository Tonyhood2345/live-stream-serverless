#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═════════════════════════════════════════════════════════════════════════════════
 IMMOBILIARE GIANCANI — GENERATORE AUTOMATICO VIDEO REEL IMMOBILIARE (9:16)
═════════════════════════════════════════════════════════════════════════════════
 Flusso di lavoro:
 1. Lettura dati da Google Sheets (Rigorosamente Colonna F).
 2. Estrazione dati: Titolo/Tipologia, Prezzo, Caratteristiche in maiuscolo, Telefono.
 3. Normalizzazione superfici con dicitura "metri quadri" per esteso.
 4. Montaggio video Reel 9:16 (1080x1920 @ 30fps) con FFmpeg / Pillow:
    - Box verticale semitrasparente scuro a sinistra (nero opacità 60%, 40-45% larghezza, angoli arrotondati).
    - Testo centrato bianco: Titolo corsivo, "RICHIESTA" + Prezzo grande, bullet points maiuscoli, "CHIAMACI" + tel.
    - Sincronizzazione traccia musicale tagliata alla durata esatta con fade-out.
 5. Invio automatico email con file .mp4 in allegato, oggetto strutturato e corpo con testo originale di Colonna F.
 6. Personal branding obbligatorio in chiusura: '— Immobiliare Giancani'.
═════════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import re
import csv
import io
import time
import json
import datetime
import argparse
import textwrap
import smtplib
import subprocess
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from PIL import Image, ImageDraw, ImageFont

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
MUSIC_DIR = os.path.join(BASE_DIR, "musica_sottofondo")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "video_storie_output")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)

# Configurazioni di default
DEFAULT_SHEET_ID = os.environ.get("SPREADSHEET_ID") or "1s68pw0WEUcV0ZqltiahAqCp_r5rsycSjxKNh0VZQq_g"
DEFAULT_GID = os.environ.get("SHEET_GID") or "1161427165"
DEFAULT_EMAIL = os.environ.get("DEST_EMAIL") or "giancaniimmobiliare@gmail.com"
DEFAULT_PHONE = "320 1667156"
BRANDING_SUFFIX = "— Immobiliare Giancani"


# ─────────────────────────────────────────────────────────────────────────────
# 1. LETTURA DATI DA GOOGLE SHEETS (COLONNA F)
# ─────────────────────────────────────────────────────────────────────────────

def leggi_colonna_f_da_google_sheet(sheet_id=DEFAULT_SHEET_ID, gid=DEFAULT_GID, riga_target=2):
    """
    Scarica il foglio Google Sheets in formato CSV ed estrae il testo
    rigorosamente dalla Colonna F (indice 5, 0-based) della riga indicata.
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    print(f"📥 Connessione a Google Sheets: {sheet_id} (gid: {gid})...")
    
    headers = {"User-Agent": "Giancani-Automation-Bot/1.0"}
    res = requests.get(url, headers=headers, verify=False, timeout=20)
    if not res.ok:
        raise RuntimeError(f"Impossibile leggere Google Sheets (HTTP {res.status_code}) da {url}")
    
    reader = csv.reader(io.StringIO(res.text))
    righe = list(reader)
    
    if len(righe) < riga_target:
        raise ValueError(f"La riga richiesta ({riga_target}) non esiste. Totale righe nel foglio: {len(righe)}")
    
    riga = righe[riga_target - 1]  # 1-based index
    if len(riga) <= 5:
        raise ValueError(f"La riga {riga_target} ha solo {len(riga)} colonne. Colonna F (indice 5) non presente.")
    
    testo_colonna_f = riga[5].strip()
    print(f"✅ Dati estratti con successo da Colonna F (Riga {riga_target}): {testo_colonna_f[:80]}...")
    return testo_colonna_f


# ─────────────────────────────────────────────────────────────────────────────
# 2. PARSING & ESTRAZIONE DATI CHIAVE DALLA COLONNA F
# ─────────────────────────────────────────────────────────────────────────────

def estrai_dati_immobile(testo_f):
    """
    Analizza il testo della Colonna F ed estrae:
    - Titolo / Tipologia immobile
    - Prezzo / Richiesta
    - Max 5-6 caratteristiche salienti in maiuscolo
    - Numero di telefono
    - Normalizza le superfici in 'metri quadri' per esteso
    - Garantisce chiusura con personal branding '— Immobiliare Giancani'
    """
    if not testo_f:
        testo_f = "Immobile di Pregio in Vendita. Ampia metratura e rifiniture curate. — Immobiliare Giancani"
    
    # Regola mandatoria: dicitura metri quadri per esteso
    testo_f_normalizzato = re.sub(r'\b(mq|mq\.|m\^2|m²|MQ)\b', 'metri quadri', testo_f)
    
    # Assicura firma branding in chiusura
    if BRANDING_SUFFIX not in testo_f_normalizzato:
        testo_completo = f"{testo_f_normalizzato.strip()}\n\n{BRANDING_SUFFIX}"
    else:
        testo_completo = testo_f_normalizzato.strip()

    # 1. Tipologia / Titolo
    titolo = "Immobile Esclusivo"
    tipologie = [
        "ATTICO PANORAMICO", "ATTICO", "APPARTAMENTO", "VILLA SINGOLA", "VILLA BIFAMILIARE",
        "VILLA DI PRESTIGIO", "VILLA", "CASA SINGOLA", "CASA INDIPENDENTE", "PALAZZINA",
        "LOCALE COMMERCIALE", "VILLETTA", "MANSARDA", "RUSTICO", "TERRENO EDIFICABILE"
    ]
    for tip in tipologie:
        if re.search(r'\b' + re.escape(tip) + r'\b', testo_f_normalizzato, re.IGNORECASE):
            titolo = tip.title()
            break
            
    # Se il testo ha una prima riga chiara di titolo (es. "FAVARA - VENDESI ATTICO")
    prime_righe = [r.strip() for r in testo_f_normalizzato.splitlines() if r.strip()]
    if prime_righe:
        prima = prime_righe[0]
        if len(prima) < 45 and not any(k in prima.lower() for k in ['richiesta', 'euro', '€', 'chiamaci', 'tel']):
            # Pulisci prefissi comuni
            prima_pulita = re.sub(r'^(favara|agrigento|vendesi|proponiamo in vendita|esclusiva)\s*[-:]*\s*', '', prima, flags=re.IGNORECASE).strip()
            if len(prima_pulita) >= 4:
                titolo = prima_pulita.title()

    # 2. Prezzo / Richiesta
    prezzo = "Trattativa Riservata"
    pattern_prezzo = r'(?:(?:richiesta|prezzo)[:\s]*€?\s*([\d\.,]+)|€\s*([\d\.,]+)|([\d\.,]+)\s*€)'
    m_prezzo = re.search(pattern_prezzo, testo_f_normalizzato, re.IGNORECASE)
    if m_prezzo:
        num = m_prezzo.group(1) or m_prezzo.group(2) or m_prezzo.group(3)
        if num and any(c.isdigit() for c in num):
            num = num.strip().rstrip('.')
            prezzo = f"€ {num}"

    # 3. Numero di Telefono
    telefono = DEFAULT_PHONE
    m_tel = re.search(r'(?:\+?39\s*)?(?:3\d{2}[\s.-]?\d{6,7}|09\d{2}[\s.-]?\d{5,7})', testo_f_normalizzato)
    if m_tel:
        telefono = m_tel.group(0).strip()

    # 4. Max 5-6 Caratteristiche Principali in Maiuscolo
    caratteristiche = []
    regole_features = [
        (r'(\d+)\s*(?:comod[ie]|spazios[ie]|luminos[ie])?\s*camere(?:\s+da\s+letto)?', r'\1 CAMERE DA LETTO'),
        (r'camera\s+matrimoniale', 'CAMERA MATRIMONIALE'),
        (r'(\d+)\s*(?:modern[ie]|ampi)?\s*bagni', r'\1 BAGNI'),
        (r'(?:doppio\s+servizio|doppi\s+servizi)', 'DOPPIO SERVIZIO'),
        (r'cucina\s+abitabile', 'CUCINA ABITABILE'),
        (r'angolo\s+cottura', 'ZONA COTTURA'),
        (r'(?:ampio\s+soggiorno|salone\s+doppio|luminoso\s+salone)', 'AMPIO SOGGIORNO'),
        (r'garage(?:\s+privato)?(?:\s+di\s+\d+\s+metri\s+quadri)?', 'GARAGE PRIVATO'),
        (r'posto\s+auto', 'POSTO AUTO RISERVATO'),
        (r'terrazzo(?:\s+a\s+livello)?(?:\s+panoramico)?', 'TERRAZZO A LIVELLO'),
        (r'veranda(?:\s+coperta)?', 'AMPIA VERANDA'),
        (r'balcon(?:e|i)\s+panoramic[oi]', 'BALCONI PANORAMICI'),
        (r'giardino(?:\s+privato)?', 'GIARDINO PRIVATO'),
        (r'ascensore', 'ASCENSORE AL PIANO'),
        (r'climatizzat[oa]|riscaldamento\s+autonomo', 'TERMOAUTONOMO CLIMATIZZATO'),
        (r'rifiniture\s+di\s+pregio|ristrutturat[oa]', 'RIFINITURE DI PREGIO'),
        (r'nuova\s+costruzione', 'NUOVA COSTRUZIONE')
    ]

    for pat, label in regole_features:
        m = re.search(pat, testo_f_normalizzato, re.IGNORECASE)
        if m:
            val = m.expand(label).upper().strip()
            if val not in caratteristiche:
                caratteristiche.append(val)
        if len(caratteristiche) >= 6:
            break

    # Se non sono state trovate abbastanza caratteristiche, estrai frasi significative
    if len(caratteristiche) < 4:
        spezzoni = re.split(r'[,;\n]', testo_f_normalizzato)
        for s in spezzoni:
            s_clean = s.strip().upper()
            if 6 <= len(s_clean) <= 30 and not any(k in s_clean for k in ['RICHIESTA', 'PREZZO', 'EURO', '€', 'CHIAMACI', 'TEL', 'GIANCANI', 'WWW']):
                if s_clean not in caratteristiche:
                    caratteristiche.append(s_clean)
            if len(caratteristiche) >= 5:
                break

    # Se ancora vuoto, fallback elegante
    if not caratteristiche:
        caratteristiche = [
            "ZONA RESIDENZIALE",
            "AMPI SPAZI LUMINOSI",
            "FINITURE DI PREGIO",
            "OTTIMO INVESTIMENTO"
        ]

    return {
        "titolo": titolo,
        "prezzo": prezzo,
        "caratteristiche": caratteristiche[:6],
        "telefono": telefono,
        "testo_originale": testo_completo
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. DOWNLOAD DA GOOGLE DRIVE O RISORSA ESTERNA
# ─────────────────────────────────────────────────────────────────────────────

def risolvi_file_multimediale(risorsa_o_id, estensione_output, cartella_fallback=None):
    """
    Riconosce se la risorsa è:
    - Un file locale esistente.
    - Un link o ID di Google Drive (lo scarica).
    - Un nome file presente in una cartella locale di fallback.
    """
    if not risorsa_o_id:
        if cartella_fallback and os.path.exists(cartella_fallback):
            file_disponibili = [os.path.join(cartella_fallback, f) for f in os.listdir(cartella_fallback) if f.endswith(estensione_output)]
            if file_disponibili:
                return file_disponibili[0]
        return None

    # 1. File locale diretto
    if os.path.exists(risorsa_o_id):
        return os.path.abspath(risorsa_o_id)

    # 2. Controllo nella cartella di fallback
    if cartella_fallback:
        candidato = os.path.join(cartella_fallback, risorsa_o_id)
        if os.path.exists(candidato):
            return candidato

    # 3. Google Drive ID o URL
    drive_id = risorsa_o_id
    if "drive.google.com" in risorsa_o_id:
        m = re.search(r'(?:id=|\/d\/|folders\/)([a-zA-Z0-9_-]{25,})', risorsa_o_id)
        if m:
            drive_id = m.group(1)

    # Download da Google Drive
    out_path = os.path.join(TEMP_DIR, f"drive_download_{drive_id[:8]}{estensione_output}")
    print(f"📥 Download risorsa Google Drive (ID: {drive_id})...")
    
    url_export = f"https://drive.google.com/uc?export=download&id={drive_id}"
    session = requests.Session()
    response = session.get(url_export, stream=True, verify=False, timeout=30)
    
    # Controllo eventuale token di conferma per file grandi
    for k, v in response.cookies.items():
        if k.startswith("download_warning"):
            url_export += f"&confirm={v}"
            response = session.get(url_export, stream=True, verify=False, timeout=30)
            break
            
    if response.status_code == 200:
        with open(out_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        print(f"✅ File Drive salvato con successo: {out_path} ({os.path.getsize(out_path)} bytes)")
        return out_path
    else:
        print(f"⚠️ Errore download Google Drive ({response.status_code}).")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 4. COSTRUZIONE OVERLAY GRAFICO PRESTIGIOSO (REEL 9:16)
# ─────────────────────────────────────────────────────────────────────────────

def carica_font_sicuro(nome_file, dimensione, fallback_bold=False):
    percorso = os.path.join(FONTS_DIR, nome_file)
    if os.path.exists(percorso):
        try:
            return ImageFont.truetype(percorso, dimensione)
        except Exception:
            pass
    # Windows font fallbacks
    win_fonts = ["georgiab.ttf" if fallback_bold else "georgia.ttf", "arialbd.ttf" if fallback_bold else "arial.ttf", "timesbd.ttf"]
    for wf in win_fonts:
        w_path = os.path.join(r"C:\Windows\Fonts", wf)
        if os.path.exists(w_path):
            try:
                return ImageFont.truetype(w_path, dimensione)
            except Exception:
                pass
    return ImageFont.load_default()


def disegna_testo_centrato(draw, testo, font, cy, cx, colore=(255, 255, 255, 255)):
    bbox = draw.textbbox((0, 0), testo, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = cx - (w // 2)
    draw.text((x, cy), testo, font=font, fill=colore)
    return cy + h


def genera_overlay_card_sinistra(dati_immobile, output_path):
    """
    Costruisce la scheda grafica Reel (1080x1920):
    - Box verticale sul lato sinistro (40-45% larghezza schermo, nero 60% opacità, angoli arrotondati).
    - Testo centrato in bianco:
      * Titolo elegante/corsivo in alto
      * 'RICHIESTA' + Prezzo ben grande
      * Caratteristiche in stampatello maiuscolo con elenco puntato
      * 'CHIAMACI' + Numero di telefono
    """
    W, H = 1080, 1920
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # Geometria Box Sinistro (42% larghezza schermo)
    box_x1 = 45
    box_w = 460
    box_x2 = box_x1 + box_w
    box_y1 = 120
    box_y2 = 1800
    box_h = box_y2 - box_y1
    cx = box_x1 + (box_w // 2)

    # Creazione Card con opacità 60% (153 su 255)
    card = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    draw_card = ImageDraw.Draw(card)
    
    # Sfondo nero 60% + Bordo dorato luxury satinato
    draw_card.rounded_rectangle(
        [0, 0, box_w, box_h],
        radius=30,
        fill=(8, 10, 14, 153),
        outline=(212, 175, 55, 200),
        width=3
    )
    overlay.paste(card, (box_x1, box_y1), card)

    draw = ImageDraw.Draw(overlay)

    # Tipografia raffinata
    font_titolo = carica_font_sicuro("PlayfairDisplay-Bold.ttf", 36, fallback_bold=True)
    font_label = carica_font_sicuro("Lora-Bold.ttf", 22, fallback_bold=True)
    font_prezzo = carica_font_sicuro("Cinzel-Bold.ttf", 46, fallback_bold=True)
    font_caratteristica = carica_font_sicuro("Lora-Bold.ttf", 24, fallback_bold=True)
    font_call = carica_font_sicuro("Cinzel-Bold.ttf", 24, fallback_bold=True)
    font_telefono = carica_font_sicuro("Cinzel-Bold.ttf", 34, fallback_bold=True)
    font_brand = carica_font_sicuro("Lora-Bold.ttf", 20, fallback_bold=True)

    # ── 0. LOGO UFFICIALE IMMOBILIARE GIANCANI (IN ALTO NELLA CARD) ──
    logo_path = os.path.join(BASE_DIR, "assets", "logo_giancani_trasparente.png")
    curr_y = box_y1 + 45
    if os.path.exists(logo_path):
        try:
            logo_img = Image.open(logo_path).convert("RGBA")
            lw = 360
            lh = int(logo_img.height * (lw / logo_img.width))
            logo_resized = logo_img.resize((lw, lh), Image.LANCZOS)
            lx = cx - (lw // 2)
            overlay.paste(logo_resized, (lx, curr_y), logo_resized)
            curr_y += lh + 20
            # Divisore dorato sotto il logo
            draw.line([(cx - 85, curr_y), (cx + 85, curr_y)], fill=(212, 175, 55, 220), width=2)
            curr_y += 30
        except Exception as e:
            print(f"Avviso logo: {e}")

    # ── 1. TITOLO IN ALTO (Corsivo / Elegante) ──
    titolo_testo = dati_immobile["titolo"]
    righe_titolo = textwrap.wrap(titolo_testo, width=18)
    for riga in righe_titolo[:3]:
        curr_y = disegna_testo_centrato(draw, riga, font_titolo, curr_y, cx, colore=(255, 255, 255, 255)) + 8

    # Divisore decorativo superiore
    draw.line([(cx - 75, curr_y + 12), (cx + 75, curr_y + 12)], fill=(212, 175, 55, 220), width=2)
    curr_y += 38

    # ── 2. RICHIESTA & PREZZO GRANDE ──
    curr_y = disegna_testo_centrato(draw, "RICHIESTA", font_label, curr_y, cx, colore=(212, 175, 55, 255)) + 8
    curr_y = disegna_testo_centrato(draw, dati_immobile["prezzo"], font_prezzo, curr_y, cx, colore=(255, 255, 255, 255)) + 25

    # Divisore decorativo intermedio
    draw.line([(cx - 110, curr_y), (cx + 110, curr_y)], fill=(212, 175, 55, 140), width=1)
    curr_y += 45

    # ── 3. CARATTERISTICHE PRINCIPALI (Stampatello Maiuscolo) ──
    caratteristiche = dati_immobile["caratteristiche"]
    for feat in caratteristiche:
        # Se una caratteristica è lunga, spezzala con grazia
        riga_feat = f"•  {feat.upper()}"
        curr_y = disegna_testo_centrato(draw, riga_feat, font_caratteristica, curr_y, cx, colore=(245, 245, 245, 255)) + 38

    # ── 4. IN BASSO: CHIAMACI & TELEFONO ──
    bottom_start = box_y2 - 200
    draw.line([(cx - 100, bottom_start - 20), (cx + 100, bottom_start - 20)], fill=(212, 175, 55, 200), width=2)
    
    bottom_y = disegna_testo_centrato(draw, "CHIAMACI", font_call, bottom_start, cx, colore=(212, 175, 55, 255)) + 8
    bottom_y = disegna_testo_centrato(draw, dati_immobile["telefono"], font_telefono, bottom_y, cx, colore=(255, 255, 255, 255)) + 12
    disegna_testo_centrato(draw, "Immobiliare Giancani", font_brand, bottom_y, cx, colore=(212, 175, 55, 220))

    overlay.save(output_path, "PNG")
    print(f"🎨 Overlay card semitrasparente generato: {output_path}")
    return output_path


# ─────────────────────────────────────────────────────────────────────────────
# 5. MONTAGGIO VIDEO REEL CON FFMPEG (1080x1920 @ 30fps)
# ─────────────────────────────────────────────────────────────────────────────

def ottieni_durata_video(video_path):
    cmd = [FFMPEG_EXE, "-i", video_path]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, errors="ignore")
    dur = 15.0  # default
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            try:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
            except Exception:
                pass
    return max(3.0, dur)


def monta_video_reel(video_input, overlay_png, music_input, output_mp4):
    """
    Esegue il montaggio completo via FFmpeg:
    - Riscala e croppa il video sorgente per riempire il formato Reel 9:16 (1080x1920).
    - Applica sul lato sinistro l'overlay con card semitrasparente scura.
    - Taglia la musica di sottofondo alla durata esatta del video con fade-out audio.
    - Esporta il file finale MP4 ottimizzato.
    """
    durata = ottieni_durata_video(video_input)
    print(f"🎬 Avvio montaggio video (Durata: {durata:.2f}s, Risoluzione: 1080x1920 @ 30fps)...")

    # Animazione slide-in della card da sinistra con decelerazione sinusoidale (Ease-Out)
    overlay_expr = "x='if(lte(t, 0.85), -530 + 530*sin(t*3.1415926/(2*0.85)), 0)':y=0"
    filtri = [
        # Video: scale + crop centrato a 1080x1920
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[vbase];"
        f"[vbase][1:v]overlay={overlay_expr}[vout]"
    ]
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", video_input,
        "-i", overlay_png
    ]

    fade_start = max(0, durata - 2.0)
    if music_input and os.path.exists(music_input):
        cmd.extend(["-stream_loop", "-1", "-i", music_input])
        filtri.append(
            f"[2:a]atrim=0:{durata},afade=t=out:st={fade_start}:d=2.0,volume=0.38[aout]"
        )
        map_audio = ["[aout]"]
    else:
        # Fallback audio muto
        filtri.append(
            f"aevalsrc=0:d={durata}[aout]"
        )
        map_audio = ["[aout]"]

    cmd.extend([
        "-filter_complex", ";".join(filtri),
        "-map", "[vout]",
        "-map", map_audio[0],
        "-t", str(durata),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        output_mp4
    ])

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="ignore")
    if proc.returncode != 0 or not os.path.exists(output_mp4):
        raise RuntimeError(f"FFmpeg fallito:\n{proc.stderr[-800:]}")
    
    dimensione_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"✅ Video Reel completato con successo: {output_mp4} ({dimensione_mb:.2f} MB)")
    return output_mp4


# ─────────────────────────────────────────────────────────────────────────────
# 6. INVIO AUTOMATICO EMAIL CON ALLEGATO MP4
# ─────────────────────────────────────────────────────────────────────────────

def invia_email_con_allegato(destinatario, titolo_immobile, testo_colonna_f, video_mp4_path):
    """
    Invia un'email con il video in allegato:
    - Oggetto: 'Video pronto + Dati Immobile - [Titolo/Riferimento Immobile]'
    - Corpo dell'email: Testo completo originale preso dalla Colonna F
    - Allegato: File .mp4 generato
    Supporta SMTP Gmail (con GMAIL_APP_PASSWORD o SMTP_PASSWORD) oppure fallback su Apps Script WebApp.
    """
    oggetto = f"Video pronto + Dati Immobile - {titolo_immobile}"
    
    # Corpo email con istruzioni chiare e copy pronto all'uso
    corpo_email = (
        f"Ciao Antonio,\n\n"
        f"Ecco il video Reel generato con successo e pronto per la pubblicazione!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 COPY PRONTO DA INCOLLARE SUI SOCIAL (Facebook, Instagram, TikTok):\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{testo_colonna_f}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎬 Video in allegato: {os.path.basename(video_mp4_path)} ({os.path.getsize(video_mp4_path) / (1024*1024):.2f} MB)\n\n"
        f"— Immobiliare Giancani\n"
    )

    # Metodo A: SMTP standard (Gmail o configurato)
    smtp_user = os.environ.get("SMTP_USER") or os.environ.get("EMAIL_USER") or "giancaniimmobiliare@gmail.com"
    smtp_password = os.environ.get("SMTP_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD") or os.environ.get("EMAIL_PASSWORD")
    smtp_host = os.environ.get("SMTP_HOST") or "smtp.gmail.com"
    smtp_port = int(os.environ.get("SMTP_PORT") or 587)

    if smtp_password:
        try:
            print(f"📧 Invio email via SMTP ({smtp_host}:{smtp_port}) a {destinatario}...")
            msg = MIMEMultipart()
            msg["From"] = f"Immobiliare Giancani <{smtp_user}>"
            msg["To"] = destinatario
            msg["Subject"] = oggetto
            msg.attach(MIMEText(corpo_email, "plain", "utf-8"))

            with open(video_mp4_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename=\"{os.path.basename(video_mp4_path)}\"")
            msg.attach(part)

            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [destinatario], msg.as_string())
            server.quit()
            print(f"✅ Email inviata con successo a {destinatario} con allegato {os.path.basename(video_mp4_path)}!")
            return True
        except Exception as e:
            print(f"⚠️ Errore invio SMTP: {e}. Tento fallback...")

    # Metodo B: Notifica tramite Google Apps Script WebApp se configurato
    apps_script_url = os.environ.get("APPS_SCRIPT_URL")
    if apps_script_url:
        try:
            print("🌐 Invio notifica a Google Apps Script WebApp...")
            payload = {
                "action": "video_reel_pronto",
                "destinatario": destinatario,
                "oggetto": oggetto,
                "testo_f": testo_colonna_f,
                "nome_file": os.path.basename(video_mp4_path)
            }
            r = requests.post(apps_script_url, json=payload, verify=False, timeout=15)
            if r.status_code in (200, 201):
                print("✅ Notifica WebApp completata con successo.")
                return True
        except Exception as e_as:
            print(f"⚠️ Errore WebApp: {e_as}")

    print(f"ℹ️ File video pronto localmente in: {video_mp4_path}")
    print(f"ℹ️ Per abilitare l'invio automatico via Gmail, imposta la variabile d'ambiente GMAIL_APP_PASSWORD.")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# 7. FUNZIONE MASTER DI ORCHESTRAZIONE
# ─────────────────────────────────────────────────────────────────────────────

def esegui_flusso_completo(
    riga=2,
    sheet_id=DEFAULT_SHEET_ID,
    gid=DEFAULT_GID,
    testo_manuale=None,
    video_drive=None,
    musica_drive=None,
    email_dest=DEFAULT_EMAIL,
    output_path=None
):
    print("=" * 75)
    print("🚀 AVVIO FLUSSO REEL IMMOBILIARE GIANCANI")
    print("=" * 75)

    # 1. Lettura Dati da Colonna F
    if testo_manuale:
        print("📄 Utilizzo testo Colonna F fornito manualmente.")
        testo_f = testo_manuale
    else:
        testo_f = leggi_colonna_f_da_google_sheet(sheet_id=sheet_id, gid=gid, riga_target=riga)

    # 2. Parsing Dati
    dati = estrai_dati_immobile(testo_f)
    print(f"📋 Dati Estratti:")
    print(f"   • Titolo:          {dati['titolo']}")
    print(f"   • Prezzo:          {dati['prezzo']}")
    print(f"   • Caratteristiche: {', '.join(dati['caratteristiche'])}")
    print(f"   • Telefono:        {dati['telefono']}")

    # 3. Risoluzione Risorse Video e Musica
    video_file = risolvi_file_multimediale(
        video_drive,
        estensione_output=".mp4",
        cartella_fallback=os.path.join(BASE_DIR, "clip_30s_generate")
    )
    if not video_file or not os.path.exists(video_file):
        raise FileNotFoundError(f"Impossibile trovare il file video. Specifica --video o carica una clip.")

    musica_file = risolvi_file_multimediale(
        musica_drive,
        estensione_output=".mp3",
        cartella_fallback=MUSIC_DIR
    )
    print(f"🎥 Video sorgente: {video_file}")
    print(f"🎵 Traccia audio:  {musica_file if musica_file else 'Nessuna (Audio muto)'}")

    # 4. Generazione Overlay Card
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") if 'datetime' in globals() else str(int(time.time()))
    overlay_path = os.path.join(TEMP_DIR, f"overlay_reel_{timestamp}.png")
    genera_overlay_card_sinistra(dati, overlay_path)

    # 5. Montaggio Video
    if not output_path:
        nome_pulito = re.sub(r'[^a-zA-Z0-9_-]', '_', dati["titolo"].lower())[:25]
        output_path = os.path.join(OUTPUT_DIR, f"reel_{nome_pulito}_{timestamp}.mp4")

    video_finale = monta_video_reel(video_file, overlay_path, musica_file, output_path)

    # 6. Invio Email
    invia_email_con_allegato(
        destinatario=email_dest,
        titolo_immobile=dati["titolo"],
        testo_colonna_f=dati["testo_originale"],
        video_mp4_path=video_finale
    )

    print("=" * 75)
    print("🎯 FLUSSO COMPLETATO CON SUCCESSO — IMMOBILIARE GIANCANI")
    print("=" * 75)
    return video_finale


# ─────────────────────────────────────────────────────────────────────────────
# 8. CLI ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automazione Video Reel Immobiliare Giancani")
    parser.add_argument("--row", type=int, default=2, help="Numero riga Google Sheets (default: 2)")
    parser.add_argument("--sheet-id", type=str, default=DEFAULT_SHEET_ID, help="Google Sheet ID")
    parser.add_argument("--gid", type=str, default=DEFAULT_GID, help="GID Scheda Google Sheets")
    parser.add_argument("--text", type=str, default=None, help="Testo Colonna F manuale (per test)")
    parser.add_argument("--video", type=str, default=None, help="File locale, Google Drive ID o URL del video")
    parser.add_argument("--music", type=str, default=None, help="File locale, Google Drive ID o nome brano mp3")
    parser.add_argument("--email", type=str, default=DEFAULT_EMAIL, help="Email destinatario per consegna")
    parser.add_argument("--output", type=str, default=None, help="Percorso file MP4 finale")

    args = parser.parse_args()
    esegui_flusso_completo(
        riga=args.row,
        sheet_id=args.sheet_id,
        gid=args.gid,
        testo_manuale=args.text,
        video_drive=args.video,
        musica_drive=args.music,
        email_dest=args.email,
        output_path=args.output
    )
