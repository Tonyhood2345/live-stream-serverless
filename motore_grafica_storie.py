#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
IMMOBILIARE GIANCANI — MOTORE GRAFICO UNIFICATO STORIE & POST (9:16 & 1:1)
═══════════════════════════════════════════════════════════════════════════════
Caratteristiche:
1. 4 Stili Grafici Professionali:
   - marketing_banner : Banner marketing immobiliare moderno con header, diagonal split footer,
                        elenco caratteristiche, codice riferimento, floating badges e CTA.
   - split_screen     : Layout split-screen promozionale con foto grande e scheda descrittiva.
   - luxury_glass     : Glassmorphism dorato luxury con effetto sfocato e bordi lucidi.
   - editorial        : Layout editoriale minimal chic con tipografia elegante.
2. Rotazione Sistematica Giornaliera dei Colori (7 giorni della settimana):
   - Lunedì    : Navy Blue & Crisp White
   - Martedì   : Luxury Black & Royal Gold
   - Mercoledì : Emerald Forest & Slate
   - Giovedì   : Bordeaux Prestige & Champagne
   - Venerdì   : Deep Tech Carbon & Electric Cyan
   - Sabato    : Royal Indigo & Warm Amber
   - Domenica  : Terracotta Sunset & Sand
3. Logo Trasparente Ufficiale:
   - Priorità assoluta ad 'logo_giancani_trasparente.png' (1600x409 RGBA).
4. Regole di Brand (RULE[user_global]):
   - Testi rigorosamente da Colonna F.
   - Superfici espresse sempre in 'metri quadri'.
   - Chiusura costante mettendo in risalto '— Immobiliare Giancani'.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import io
import sys
import re
import time
import uuid
import math
import random
import datetime
import urllib.request
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR) if os.path.basename(BASE_DIR) == 'scripts' else BASE_DIR
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
SCRATCH_DIR = os.path.join(PROJECT_DIR, "scratch")
os.makedirs(SCRATCH_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 1. ROTAZIONE SISTEMATICA GIORNALIERA DELLE PALETTE CROMATICHE
# ═══════════════════════════════════════════════════════════════════════════════

PALETTE_GIORNALIERE = {
    0: {  # Lunedì / Palette Attiva
        "id": "warm_yellow",
        "nome": "Giallo Solare & Slate Prestige",
        "giorno": "Giallo Solare",
        "primary_dark": (245, 190, 11, 255),       # #F5BE0B Giallo caldo solare intenso
        "primary_mid": (234, 165, 8, 255),        # #EAA508 Ambra dorata
        "primary_light": (254, 240, 138, 255),    # #FEF08A Crema luminoso
        "accent": (180, 83, 9, 255),              # #B45309 Ambra di contrasto
        "accent_light": (254, 243, 199, 255),
        "badge_bg": (24, 24, 27, 245),            # Nero grafite elegante
        "badge_txt": (250, 204, 21, 255),         # Giallo acceso
        "footer_bg": (245, 190, 11, 255),         # Fondo giallo pieno
        "footer_diag": (234, 165, 8, 255),        # Sfumatura gialla
        "card_bg": (255, 255, 255, 245),          # Card bianca nitida
        "border_color": (217, 119, 6, 200),
        "text_primary": (17, 24, 39, 255),        # Nero per contrasto su giallo
        "text_secondary": (55, 65, 81, 255),      # Grigio scuro
        "btn_cta_bg": (17, 24, 39, 255),          # Bottone scuro di risalto
        "bottom_bar_bg": (245, 190, 11, 255),     # Barra inferiore gialla
        "bottom_bar_txt": (17, 24, 39, 255)
    },
    1: {  # Martedì
        "id": "luxury_gold",
        "nome": "Luxury Black & Royal Gold",
        "giorno": "Martedì",
        "primary_dark": (18, 16, 14, 255),       # #12100E
        "primary_mid": (35, 30, 24, 255),
        "primary_light": (201, 163, 94, 255),    # #C9A35E
        "accent": (212, 168, 83, 255),           # Oro Giancani
        "accent_light": (245, 212, 133, 255),
        "badge_bg": (201, 163, 94, 245),
        "badge_txt": (18, 14, 10, 255),
        "footer_bg": (18, 15, 12, 255),
        "footer_diag": (28, 24, 18, 255),
        "card_bg": (20, 16, 12, 220),
        "border_color": (201, 163, 94, 180),
        "text_primary": (255, 255, 255, 255),
        "text_secondary": (230, 215, 190, 255),
        "btn_cta_bg": (201, 163, 94, 255),
        "bottom_bar_bg": (248, 245, 238, 255),
        "bottom_bar_txt": (24, 18, 12, 255)
    },
    2: {  # Mercoledì
        "id": "emerald_forest",
        "nome": "Emerald Forest & Slate",
        "giorno": "Mercoledì",
        "primary_dark": (6, 78, 59, 255),        # #064E3B
        "primary_mid": (4, 120, 87, 255),        # #047857
        "primary_light": (52, 211, 153, 255),    # #34D399 Menta
        "accent": (245, 158, 11, 255),           # Oro
        "accent_light": (209, 250, 229, 255),
        "badge_bg": (52, 211, 153, 240),
        "badge_txt": (6, 78, 59, 255),
        "footer_bg": (6, 78, 59, 255),
        "footer_diag": (10, 100, 75, 255),
        "card_bg": (6, 78, 59, 220),
        "border_color": (52, 211, 153, 180),
        "text_primary": (255, 255, 255, 255),
        "text_secondary": (226, 232, 240, 255),
        "btn_cta_bg": (4, 120, 87, 255),
        "bottom_bar_bg": (255, 255, 255, 255),
        "bottom_bar_txt": (6, 78, 59, 255)
    },
    3: {  # Giovedì
        "id": "bordeaux_wine",
        "nome": "Bordeaux Prestige & Champagne",
        "giorno": "Giovedì",
        "primary_dark": (74, 4, 4, 255),         # #4A0404
        "primary_mid": (127, 29, 29, 255),       # #7F1D1D
        "primary_light": (253, 230, 138, 255),   # #FDE68A Champagne
        "accent": (245, 158, 11, 255),
        "accent_light": (254, 243, 199, 255),
        "badge_bg": (253, 230, 138, 245),
        "badge_txt": (74, 4, 4, 255),
        "footer_bg": (74, 4, 4, 255),
        "footer_diag": (105, 15, 15, 255),
        "card_bg": (74, 4, 4, 220),
        "border_color": (253, 230, 138, 180),
        "text_primary": (255, 255, 255, 255),
        "text_secondary": (254, 243, 199, 255),
        "btn_cta_bg": (185, 28, 28, 255),
        "bottom_bar_bg": (255, 255, 255, 255),
        "bottom_bar_txt": (74, 4, 4, 255)
    },
    4: {  # Venerdì
        "id": "deep_tech_cyan",
        "nome": "Deep Tech Carbon & Electric Cyan",
        "giorno": "Venerdì",
        "primary_dark": (15, 23, 42, 255),       # #0F172A
        "primary_mid": (30, 41, 59, 255),        # #1E293B
        "primary_light": (6, 182, 212, 255),     # #06B6D4 Ciano
        "accent": (56, 189, 248, 255),           # #38BDF8
        "accent_light": (207, 250, 254, 255),
        "badge_bg": (6, 182, 212, 240),
        "badge_txt": (15, 23, 42, 255),
        "footer_bg": (15, 23, 42, 255),
        "footer_diag": (25, 35, 55, 255),
        "card_bg": (15, 23, 42, 220),
        "border_color": (6, 182, 212, 180),
        "text_primary": (255, 255, 255, 255),
        "text_secondary": (226, 232, 240, 255),
        "btn_cta_bg": (14, 165, 233, 255),
        "bottom_bar_bg": (255, 255, 255, 255),
        "bottom_bar_txt": (15, 23, 42, 255)
    },
    5: {  # Sabato
        "id": "royal_indigo",
        "nome": "Royal Indigo & Warm Amber",
        "giorno": "Sabato",
        "primary_dark": (30, 27, 75, 255),       # #1E1B4B
        "primary_mid": (55, 48, 163, 255),       # #3730A3
        "primary_light": (245, 158, 11, 255),    # #F59E0B Ambra
        "accent": (251, 191, 36, 255),
        "accent_light": (254, 243, 199, 255),
        "badge_bg": (245, 158, 11, 240),
        "badge_txt": (30, 27, 75, 255),
        "footer_bg": (30, 27, 75, 255),
        "footer_diag": (45, 40, 105, 255),
        "card_bg": (30, 27, 75, 220),
        "border_color": (245, 158, 11, 180),
        "text_primary": (255, 255, 255, 255),
        "text_secondary": (224, 231, 255, 255),
        "btn_cta_bg": (67, 56, 202, 255),
        "bottom_bar_bg": (255, 255, 255, 255),
        "bottom_bar_txt": (30, 27, 75, 255)
    },
    6: {  # Domenica
        "id": "terracotta_sunset",
        "nome": "Terracotta Sunset & Sand",
        "giorno": "Domenica",
        "primary_dark": (67, 20, 7, 255),        # #431407
        "primary_mid": (154, 52, 18, 255),       # #9A3412
        "primary_light": (252, 211, 77, 255),    # #FCD34D Sabbia
        "accent": (251, 146, 60, 255),           # Arancio caldo
        "accent_light": (255, 237, 213, 255),
        "badge_bg": (252, 211, 77, 245),
        "badge_txt": (67, 20, 7, 255),
        "footer_bg": (67, 20, 7, 255),
        "footer_diag": (95, 30, 12, 255),
        "card_bg": (67, 20, 7, 220),
        "border_color": (252, 211, 77, 180),
        "text_primary": (255, 255, 255, 255),
        "text_secondary": (254, 215, 170, 255),
        "btn_cta_bg": (194, 65, 12, 255),
        "bottom_bar_bg": (255, 255, 255, 255),
        "bottom_bar_txt": (67, 20, 7, 255)
    }
}

def get_palette_per_storia(slot_idx=None):
    """
    Restituisce una palette cromatica SEMPRE DIVERSA ad OGNI STORIA (rotazione continua dei 7 colori).
    Utilizza un salto a passo 3 per massimizzare il contrasto cromatico tra una storia e la successiva:
    es. Giallo Solare -> Cyan Tech -> Luxury Gold -> Terracotta -> Smeraldo -> Bordeaux -> Indigo.
    """
    if slot_idx is None:
        slot_idx = int(time.time() / 1800)
    pal_idx = (int(slot_idx) * 3 + 1) % len(PALETTE_GIORNALIERE)
    return PALETTE_GIORNALIERE.get(pal_idx, PALETTE_GIORNALIERE[0])

def get_palette_del_giorno(day_of_week=None, slot_idx=None):
    """
    Restituisce la palette cromatica associata.
    Se day_of_week è specificato manualmente (stringa o intero), rispetta la preferenza.
    Se None o automatico, ruota la palette ad OGNI SINGOLA STORIA per garantire colore sempre diverso.
    """
    if str(day_of_week).lower() in ["giallo", "yellow", "fondo_giallo", "warm_yellow", "sole"]:
        return PALETTE_GIORNALIERE[0]
    if slot_idx is not None:
        return get_palette_per_storia(slot_idx)
    if day_of_week is None or day_of_week == "auto":
        return get_palette_per_storia()
    try:
        day_idx = int(day_of_week) % 7
        return PALETTE_GIORNALIERE.get(day_idx, PALETTE_GIORNALIERE[0])
    except Exception:
        return get_palette_per_storia()

# ═══════════════════════════════════════════════════════════════════════════════
# 🗓️ 1.1 ROTAZIONE SISTEMATICA SETTIMANALE DELLE PALETTE CROMATICHE DI CONTESTO
# ═══════════════════════════════════════════════════════════════════════════════

PALETTE_SETTIMANALI = [
    {
        "id": "emerald_capellupo",
        "nome": "Smeraldo Capellupo & Salvia",
        "context_color": (16, 128, 98),       # #108062 Smeraldo/Teal come foto reference
        "context_rgba": (16, 128, 98, 185),
        "accent": (16, 128, 98, 255),
        "primary_dark": (16, 128, 98, 255),
        "highlight": (220, 38, 38),          # Rosso ribassato
        "text_dark": (30, 41, 59),
    },
    {
        "id": "navy_ocean",
        "nome": "Blu Oltremare & Zaffiro",
        "context_color": (30, 58, 138),       # #1E3A8A Navy Blue
        "context_rgba": (30, 58, 138, 185),
        "accent": (30, 58, 138, 255),
        "primary_dark": (30, 58, 138, 255),
        "highlight": (220, 38, 38),
        "text_dark": (30, 41, 59),
    },
    {
        "id": "bordeaux_royal",
        "nome": "Bordeaux Prestige & Rubino",
        "context_color": (136, 19, 55),       # #881337 Bordeaux
        "context_rgba": (136, 19, 55, 185),
        "accent": (136, 19, 55, 255),
        "primary_dark": (136, 19, 55, 255),
        "highlight": (220, 38, 38),
        "text_dark": (30, 41, 59),
    },
    {
        "id": "luxury_amber",
        "nome": "Oro Ambra & Bronzo",
        "context_color": (180, 83, 9),        # #B45309 Ambra dorata
        "context_rgba": (180, 83, 9, 185),
        "accent": (180, 83, 9, 255),
        "primary_dark": (180, 83, 9, 255),
        "highlight": (220, 38, 38),
        "text_dark": (30, 41, 59),
    },
    {
        "id": "mediterranean_cyan",
        "nome": "Ciano Petrolio & Egeo",
        "context_color": (14, 116, 144),      # #0E7490 Petrolio/Ciano
        "context_rgba": (14, 116, 144, 185),
        "accent": (14, 116, 144, 255),
        "primary_dark": (14, 116, 144, 255),
        "highlight": (220, 38, 38),
        "text_dark": (30, 41, 59),
    },
    {
        "id": "terracotta_sunset",
        "nome": "Terracotta & Tramonto",
        "context_color": (154, 52, 18),       # #9A3412 Terracotta
        "context_rgba": (154, 52, 18, 185),
        "accent": (154, 52, 18, 255),
        "primary_dark": (154, 52, 18, 255),
        "highlight": (220, 38, 38),
        "text_dark": (30, 41, 59),
    },
    {
        "id": "imperial_purple",
        "nome": "Viola Imperiale & Ametista",
        "context_color": (88, 28, 135),       # #581C87 Viola
        "context_rgba": (88, 28, 135, 185),
        "accent": (88, 28, 135, 255),
        "primary_dark": (88, 28, 135, 255),
        "highlight": (220, 38, 38),
        "text_dark": (30, 41, 59),
    },
    {
        "id": "forest_pine",
        "nome": "Verde Bosco & Pino",
        "context_color": (20, 83, 45),        # #14532D Bosco scuro
        "context_rgba": (20, 83, 45, 185),
        "accent": (20, 83, 45, 255),
        "primary_dark": (20, 83, 45, 255),
        "highlight": (220, 38, 38),
        "text_dark": (30, 41, 59),
    }
]

def get_palette_settimanale(dt=None, week_offset=0):
    """
    Restituisce la palette di contesto settimanale (cambia automaticamente ogni settimana).
    """
    if dt is None:
        try:
            from datetime import datetime, timezone, timedelta
            rome_tz = timezone(timedelta(hours=2))
            dt = datetime.now(rome_tz).date()
        except Exception:
            dt = datetime.date.today()
    week_num = dt.isocalendar()[1] + week_offset
    idx = week_num % len(PALETTE_SETTIMANALI)
    return PALETTE_SETTIMANALI[idx]

# ═══════════════════════════════════════════════════════════════════════════════
# 🏷️ 2. GESTIONE LOGO TRASPARENTE UFFICIALE IMMOBILIARE GIANCANI
# ═══════════════════════════════════════════════════════════════════════════════

def get_logo_trasparente_ufficiale(max_w=380, max_h=110, alpha=255):
    """
    Carica il logo trasparente ufficiale 'logo_giancani_trasparente.png',
    rispettando rigorosamente le proporzioni originali (1600x409).
    Nessun bordo bianco opaco, nessuna deformazione o schiacciamento.
    """
    candidati = [
        os.path.join(PROJECT_DIR, "assets", "logo_giancani_trasparente.png"),
        os.path.join(BASE_DIR, "assets", "logo_giancani_trasparente.png"),
        os.path.join(PROJECT_DIR, "assets", "logo_giancani.png"),
        os.path.join(BASE_DIR, "assets", "logo_giancani.png")
    ]
    logo_path = None
    for c in candidati:
        if os.path.exists(c) and os.path.getsize(c) > 500:
            logo_path = c
            break

    if not logo_path:
        return None

    try:
        im = Image.open(logo_path).convert('RGBA')
        if "trasparente" not in logo_path.lower():
            arr = np.array(im)
            r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            white_mask = (r > 230) & (g > 230) & (b > 230)
            arr[white_mask, 3] = 0
            im = Image.fromarray(arr)

        orig_w, orig_h = im.size
        scale = min(max_w / orig_w, max_h / orig_h)
        new_w = max(1, int(orig_w * scale))
        new_h = max(1, int(orig_h * scale))
        im_resized = im.resize((new_w, new_h), Image.LANCZOS)

        if alpha < 255:
            arr = np.array(im_resized)
            arr[:, :, 3] = (arr[:, :, 3].astype(float) * (alpha / 255.0)).astype(np.uint8)
            im_resized = Image.fromarray(arr)

        return im_resized
    except Exception as e:
        print(f"[LOGO] Errore caricamento logo trasparente: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 🔤 3. GESTIONE FONT TIPOGRAFICI SCALATI (CROSS-PLATFORM)
# ═══════════════════════════════════════════════════════════════════════════════

def get_font(size, bold=False, font_type="sans"):
    """Carica font TrueType per Windows e Linux (GitHub Actions)"""
    paths = []
    if font_type == "serif":
        paths = [
            "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/timesbd.ttf" if bold else "C:/Windows/Fonts/times.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
        ]
    elif font_type == "script":
        paths = [
            "C:/Windows/Fonts/segoescb.ttf" if bold else "C:/Windows/Fonts/segoesc.ttf",
            "C:/Windows/Fonts/brushsci.ttf",
            "C:/Windows/Fonts/georgiaz.ttf" if bold else "C:/Windows/Fonts/georgiai.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
        ]
    else:  # sans
        paths = [
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def formatta_metri_quadri(mq_raw):
    """Garantisce la dicitura per esteso 'metri quadri' (RULE[user_global])"""
    if not mq_raw:
        return "120 metri quadri"
    s = str(mq_raw).strip()
    s = re.sub(r'(?i)\b(?:mq|m²|m2)\b', '', s).strip()
    digits = re.search(r'\d+', s)
    num = digits.group(0) if digits else "120"
    return f"{num} metri quadri"

def draw_fitted_text(draw, text, box, max_font_size=28, min_font_size=14, font_type="sans",
                     fill=(30, 41, 59, 255), bold=False, line_spacing=6, align="left"):
    """
    Disegna il testo all'interno di un box prefissato (x, y, w, h).
    Scala automaticamente la dimensione del font verso il basso in modo che l'intero testo
    resti RIGOROSAMENTE all'interno dello spazio prefissato, senza mai sbordare.
    Se a dimensione minima il testo supera ancora l'altezza massima, tronca le ultime parole
    dell'ultima riga visibile inserendo '...' per preservare la geometria del layout.
    """
    x, y, w, h = box
    text_clean = re.sub(r'[\r\n\t]+', ' ', str(text or '')).strip()
    text_clean = re.sub(r'\s{2,}', ' ', text_clean)
    words = text_clean.split()
    if not words or w <= 0 or h <= 0:
        return y

    best_lines = []
    best_font = None
    best_line_h = 0

    # Ricerca font_size ideale decrescente
    for sz in range(int(max_font_size), int(min_font_size) - 1, -1):
        f = get_font(sz, bold=bold, font_type=font_type)
        lines = []
        curr = ""
        fits_horiz = True

        for word in words:
            candidate = f"{curr} {word}".strip()
            bb = draw.textbbox((0, 0), candidate, font=f)
            line_w = bb[2] - bb[0]
            if line_w <= w:
                curr = candidate
            else:
                if curr:
                    lines.append(curr)
                word_bb = draw.textbbox((0, 0), word, font=f)
                if (word_bb[2] - word_bb[0]) > w:
                    fits_horiz = False
                    break
                curr = word

        if curr:
            lines.append(curr)

        if not fits_horiz:
            continue

        test_bb = draw.textbbox((0, 0), "Ag", font=f)
        single_h = test_bb[3] - test_bb[1]
        tot_h = len(lines) * single_h + max(0, len(lines) - 1) * line_spacing

        if tot_h <= h:
            best_lines = lines
            best_font = f
            best_line_h = single_h
            break

    # Se anche a min_font_size supera l'altezza disponibile:
    if not best_lines:
        best_font = get_font(min_font_size, bold=bold, font_type=font_type)
        test_bb = draw.textbbox((0, 0), "Ag", font=best_font)
        best_line_h = test_bb[3] - test_bb[1]
        max_possible_lines = max(1, int((h + line_spacing) / (best_line_h + line_spacing)))

        lines = []
        curr = ""
        for word in words:
            candidate = f"{curr} {word}".strip()
            bb = draw.textbbox((0, 0), candidate, font=best_font)
            if (bb[2] - bb[0]) <= w:
                curr = candidate
            else:
                if curr:
                    lines.append(curr)
                curr = word
        if curr:
            lines.append(curr)

        best_lines = lines[:max_possible_lines]
        if len(lines) > max_possible_lines and best_lines:
            last = best_lines[-1]
            while last and (draw.textbbox((0, 0), last + "...", font=best_font)[2] - draw.textbbox((0, 0), last + "...", font=best_font)[0]) > w:
                parts = last.rsplit(' ', 1)
                if len(parts) > 1:
                    last = parts[0]
                else:
                    last = last[:-1]
            best_lines[-1] = last.rstrip(',.; ') + "..."

    curr_y = y
    for line in best_lines:
        bb = draw.textbbox((0, 0), line, font=best_font)
        line_w = bb[2] - bb[0]
        if align == "center":
            draw_x = x + (w - line_w) // 2
        elif align == "right":
            draw_x = x + w - line_w
        else:
            draw_x = x
        draw.text((draw_x, curr_y), line, font=best_font, fill=fill)
        curr_y += best_line_h + line_spacing

    return curr_y


# ── PRIMITIVE VETTORIALI LINE-ART PRECISE (RULE[user_global] & ICONE REFERENZE) ──

def draw_house_icon(draw, cx, cy, size, color, width=3):
    s = size / 2.0
    roof = [(cx, cy - s), (cx - s, cy), (cx + s, cy)]
    draw.polygon(roof, outline=color, width=width)
    body = [cx - s * 0.75, cy, cx + s * 0.75, cy + s * 0.9]
    draw.rectangle(body, outline=color, width=width)
    door = [cx - s * 0.22, cy + s * 0.35, cx + s * 0.22, cy + s * 0.9]
    draw.rectangle(door, outline=color, width=width)

def draw_bathtub_icon(draw, cx, cy, size, color, width=3):
    s = size / 2.0
    tub_y = cy - s * 0.2
    tub_h = s * 0.8
    tub_w = s * 1.6
    draw.rounded_rectangle([cx - tub_w/2, tub_y, cx + tub_w/2, tub_y + tub_h], radius=int(s*0.35), outline=color, width=width)
    draw.line([(cx - tub_w*0.55, tub_y), (cx + tub_w*0.55, tub_y)], fill=color, width=width)
    leg_l = [(cx - tub_w*0.35, tub_y + tub_h), (cx - tub_w*0.4, tub_y + tub_h + s*0.25)]
    leg_r = [(cx + tub_w*0.35, tub_y + tub_h), (cx + tub_w*0.4, tub_y + tub_h + s*0.25)]
    draw.line(leg_l, fill=color, width=width)
    draw.line(leg_r, fill=color, width=width)
    r_bub = s * 0.15
    draw.ellipse([cx - s*0.4 - r_bub, cy - s*0.6 - r_bub, cx - s*0.4 + r_bub, cy - s*0.6 + r_bub], outline=color, width=max(1, width-1))
    draw.ellipse([cx - s*0.1 - r_bub*0.8, cy - s*0.75 - r_bub*0.8, cx - s*0.1 + r_bub*0.8, cy - s*0.75 + r_bub*0.8], outline=color, width=max(1, width-1))
    draw.ellipse([cx + s*0.2 - r_bub*1.2, cy - s*0.55 - r_bub*1.2, cx + s*0.2 + r_bub*1.2, cy - s*0.55 + r_bub*1.2], outline=color, width=max(1, width-1))

def draw_bed_icon(draw, cx, cy, size, color, width=3):
    s = size / 2.0
    w = s * 1.5
    h = s * 1.1
    draw.line([(cx - w/2, cy - h/2), (cx - w/2, cy + h/2)], fill=color, width=width)
    draw.line([(cx + w/2, cy - h/4), (cx + w/2, cy + h/2)], fill=color, width=width)
    draw.line([(cx - w/2, cy + h/8), (cx + w/2, cy + h/8)], fill=color, width=width)
    draw.rounded_rectangle([cx - w*0.4, cy - h*0.25, cx - w*0.05, cy + h*0.05], radius=int(s*0.15), outline=color, width=width)
    draw.rounded_rectangle([cx + w*0.05, cy - h*0.25, cx + w*0.4, cy + h*0.05], radius=int(s*0.15), outline=color, width=width)

def draw_garage_icon(draw, cx, cy, size, color, width=3):
    s = size / 2.0
    draw.polygon([(cx, cy - s), (cx - s, cy - s*0.3), (cx + s, cy - s*0.3)], outline=color, width=width)
    draw.rectangle([cx - s*0.85, cy - s*0.3, cx + s*0.85, cy + s*0.85], outline=color, width=width)
    car_w = s * 1.1
    car_y = cy + s * 0.1
    draw.rounded_rectangle([cx - car_w/2, car_y, cx + car_w/2, cy + s*0.75], radius=int(s*0.2), outline=color, width=width)
    draw.ellipse([cx - car_w*0.35, cy + s*0.3, cx - car_w*0.15, cy + s*0.5], fill=color)
    draw.ellipse([cx + car_w*0.15, cy + s*0.3, cx + car_w*0.35, cy + s*0.5], fill=color)

def draw_elevator_icon(draw, cx, cy, size, color, width=3):
    s = size / 2.0
    draw.rectangle([cx - s*0.8, cy - s*0.8, cx + s*0.8, cy + s*0.8], outline=color, width=width)
    up_arrow = [(cx - s*0.3, cy - s*0.5), (cx - s*0.5, cy - s*0.2), (cx - s*0.1, cy - s*0.2)]
    draw.polygon(up_arrow, fill=color)
    down_arrow = [(cx + s*0.3, cy - s*0.2), (cx + s*0.1, cy - s*0.5), (cx + s*0.5, cy - s*0.5)]
    draw.polygon(down_arrow, fill=color)
    r_head = s * 0.16
    draw.ellipse([cx - s*0.3 - r_head, cy + s*0.05 - r_head, cx - s*0.3 + r_head, cy + s*0.05 + r_head], fill=color)
    draw.ellipse([cx + s*0.3 - r_head, cy + s*0.05 - r_head, cx + s*0.3 + r_head, cy + s*0.05 + r_head], fill=color)
    draw.line([(cx - s*0.3, cy + s*0.25), (cx - s*0.3, cy + s*0.65)], fill=color, width=width)
    draw.line([(cx + s*0.3, cy + s*0.25), (cx + s*0.3, cy + s*0.65)], fill=color, width=width)

def draw_pin_icon(draw, cx, cy, size, color):
    r = size / 2.0
    center_circle_y = cy - r * 0.3
    pts = []
    for angle in range(210, 331):
        rad = math.radians(angle)
        pts.append((cx + math.cos(rad) * r, center_circle_y + math.sin(rad) * r))
    pts.append((cx, cy + r))
    draw.polygon(pts, fill=color)
    draw.ellipse([cx - r*0.4, center_circle_y - r*0.4, cx + r*0.4, center_circle_y + r*0.4], fill=(255, 255, 255, 255))

def draw_phone_icon(draw, cx, cy, size, color):
    w = max(4, int(size * 0.55))
    h = max(6, int(size * 0.9))
    draw.rounded_rectangle([cx - w//2, cy - h//2, cx + w//2, cy + h//2], radius=max(2, int(size*0.12)), outline=color, width=max(2, int(size*0.08)))
    draw.ellipse([cx - int(size*0.06), cy + h//2 - int(size*0.16), cx + int(size*0.06), cy + h//2 - int(size*0.04)], fill=color)

def draw_chevrons(draw, start_x, start_y, height, color, count=4):
    for i in range(count):
        x = start_x + i * 22
        pts = [(x, start_y), (x + 14, start_y + height // 2), (x, start_y + height)]
        draw.line([(pts[0][0], pts[0][1]), (pts[1][0], pts[1][1])], fill=color, width=4)
        draw.line([(pts[1][0], pts[1][1]), (pts[2][0], pts[2][1])], fill=color, width=4)

def draw_vector_shower(draw, cx, cy, size, color=(255, 255, 255, 255), width=3):
    s = size / 2.0
    draw.line([(cx - s*0.6, cy + s*0.8), (cx - s*0.6, cy - s*0.5)], fill=color, width=width)
    draw.arc([cx - s*0.6, cy - s*0.8, cx + s*0.2, cy], start=180, end=270, fill=color, width=width)
    draw.line([(cx - s*0.2, cy - s*0.8), (cx + s*0.3, cy - s*0.8)], fill=color, width=width)
    head = [(cx + s*0.1, cy - s*0.6), (cx + s*0.5, cy - s*0.6), (cx + s*0.3, cy - s*0.8)]
    draw.polygon(head, outline=color, width=width)
    draw.line([(cx + s*0.15, cy - s*0.45), (cx + s*0.05, cy - s*0.15)], fill=color, width=max(1, width-1))
    draw.line([(cx + s*0.3, cy - s*0.45), (cx + s*0.3, cy - s*0.05)], fill=color, width=max(1, width-1))
    draw.line([(cx + s*0.45, cy - s*0.45), (cx + s*0.55, cy - s*0.15)], fill=color, width=max(1, width-1))

def draw_vector_sofa(draw, cx, cy, size, color=(255, 255, 255, 255), width=3):
    s = size / 2.0
    w = s * 1.6
    h = s * 0.9
    draw.rounded_rectangle([cx - w*0.45, cy - h*0.8, cx + w*0.45, cy + h*0.1], radius=int(s*0.2), outline=color, width=width)
    draw.rounded_rectangle([cx - w*0.42, cy - h*0.15, cx + w*0.42, cy + h*0.55], radius=int(s*0.15), outline=color, width=width)
    draw.rounded_rectangle([cx - w*0.5, cy - h*0.45, cx - w*0.3, cy + h*0.6], radius=int(s*0.15), outline=color, width=width)
    draw.rounded_rectangle([cx + w*0.3, cy - h*0.45, cx + w*0.5, cy + h*0.6], radius=int(s*0.15), outline=color, width=width)
    draw.line([(cx - w*0.38, cy + h*0.6), (cx - w*0.42, cy + h*0.85)], fill=color, width=width)
    draw.line([(cx + w*0.38, cy + h*0.6), (cx + w*0.42, cy + h*0.85)], fill=color, width=width)

def draw_vector_ruler_sqm(draw, cx, cy, size, color=(255, 255, 255, 255), width=3):
    s = size / 2.0
    pts = [(cx - s*0.8, cy + s*0.8), (cx + s*0.8, cy + s*0.8), (cx - s*0.8, cy - s*0.8)]
    draw.polygon(pts, outline=color, width=width)
    pts_in = [(cx - s*0.45, cy + s*0.45), (cx + s*0.25, cy + s*0.45), (cx - s*0.45, cy - s*0.25)]
    draw.polygon(pts_in, outline=color, width=max(1, width-1))
    for i in range(1, 4):
        tx = cx - s*0.8 + i * (s * 0.4)
        draw.line([(tx, cy + s*0.8), (tx, cy + s*0.6)], fill=color, width=max(1, width-1))

def draw_vector_laundry(draw, cx, cy, size, color=(255, 255, 255, 255), width=3):
    s = size / 2.0
    draw.rounded_rectangle([cx - s*0.75, cy - s*0.85, cx + s*0.75, cy + s*0.85], radius=int(s*0.2), outline=color, width=width)
    r_porthole = s * 0.42
    draw.ellipse([cx - r_porthole, cy - r_porthole + s*0.15, cx + r_porthole, cy + r_porthole + s*0.15], outline=color, width=width)
    draw.ellipse([cx - s*0.5, cy - s*0.65, cx - s*0.25, cy - s*0.4], outline=color, width=width)
    draw.line([(cx + s*0.1, cy - s*0.55), (cx + s*0.55, cy - s*0.55)], fill=color, width=width)

def draw_vector_check(draw, cx, cy, size, color=(255, 255, 255, 255), width=4):
    s = size / 2.0
    p1 = (cx - s * 0.65, cy - s * 0.05)
    p2 = (cx - s * 0.15, cy + s * 0.55)
    p3 = (cx + s * 0.7, cy - s * 0.6)
    draw.line([p1, p2], fill=color, width=width)
    draw.line([p2, p3], fill=color, width=width)

def get_clean_property_photo(media_info, target_size=(1080, 1920)):
    W, H = target_size
    im = media_info.get("fotoImage")
    if not im and media_info.get("fotoUrl"):
        url = str(media_info.get("fotoUrl"))
        if os.path.exists(url):
            try:
                im = Image.open(url).convert("RGB")
            except Exception:
                pass
        elif url.startswith("http"):
            try:
                r = requests.get(url, verify=False, timeout=12)
                if r.status_code == 200:
                    im = Image.open(io.BytesIO(r.content)).convert("RGB")
            except Exception:
                pass

    if not im:
        # Ricerca dinamica in assets/immobili_cache con rotazione/shuffle anti-ripetizione
        cache_dir = os.path.join(ASSETS_DIR, "immobili_cache")
        if os.path.exists(cache_dir):
            c_files = [os.path.join(cache_dir, f) for f in os.listdir(cache_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if c_files:
                import random
                random.shuffle(c_files)
                for cf in c_files:
                    try:
                        im = Image.open(cf).convert("RGB")
                        break
                    except Exception:
                        pass

    if not im:
        # Fallback online rotativo garantito
        fallback_urls = [
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?q=80&w=1200&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?q=80&w=1200&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?q=80&w=1200&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=1200&auto=format&fit=crop"
        ]
        import random
        random.shuffle(fallback_urls)
        for fb in fallback_urls:
            try:
                r = requests.get(fb, verify=False, timeout=10)
                if r.status_code == 200:
                    im = Image.open(io.BytesIO(r.content)).convert("RGB")
                    break
            except Exception:
                pass

    if not im:
        im = Image.new("RGB", (W, H), (140, 120, 100))
        d = ImageDraw.Draw(im)
        for y in range(H):
            d.line([(0, y), (W, y)], fill=(int(120 + 80*(y/H)), int(100 + 60*(y/H)), int(80 + 50*(y/H))))

    iw, ih = im.size
    scale = max(W / iw, H / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    im_sc = im.resize((nw, nh), Image.LANCZOS)
    cx = (nw - W) // 2
    cy = (nh - H) // 2
    return im_sc.crop((cx, cy, cx + W, cy + H))


# ═══════════════════════════════════════════════════════════════════════════════
# 🏛️ 4. STILE 1: MARKETING BANNER (9:16 - 1080x1920) [NUOVO LAYOUT RICHIESTO]
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_marketing_banner_9_16(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_marketing_banner_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = Image.new('RGBA', (W, H), palette["primary_dark"])
    draw = ImageDraw.Draw(canvas)

    titolo = str(media_info.get('titolo', 'VILLA FAVARA')).strip().upper()
    zona = str(media_info.get('zona', 'FAVARA (AG)')).strip().upper()
    if not zona or zona.lower() == 'none':
        zona = 'FAVARA ED AGRIGENTO'
    prezzo_raw = str(media_info.get('prezzo', 'Trattativa Riservata')).strip()
    if prezzo_raw.isdigit():
        prezzo_str = f"€ {int(prezzo_raw):,}".replace(",", ".")
    elif "€" not in prezzo_raw and any(c.isdigit() for c in prezzo_raw):
        prezzo_str = f"€ {prezzo_raw}"
    else:
        prezzo_str = prezzo_raw

    mq_str = formatta_metri_quadri(media_info.get('mq', '135'))
    codice_rif = str(media_info.get('codiceRif', media_info.get('tabName', 'GIANCANI #104'))).replace('_', ' ').upper()
    if not codice_rif.startswith('RIF.'):
        codice_rif = f"RIF. {codice_rif}"

    # ── 1. TOP HEADER (0 - 220 px) ──
    header_h = 220
    for y in range(header_h):
        ratio = y / header_h
        r = int(palette["primary_dark"][0] * (1 - ratio * 0.2))
        g = int(palette["primary_dark"][1] * (1 - ratio * 0.2))
        b = int(palette["primary_dark"][2] * (1 - ratio * 0.2))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    logo_box_x = 35
    logo_box_y = 35
    logo_box_w = 260
    logo_box_h = 150
    draw.rounded_rectangle(
        [logo_box_x, logo_box_y, logo_box_x + logo_box_w, logo_box_y + logo_box_h],
        radius=14,
        fill=(255, 255, 255, 255),
        outline=palette["accent"],
        width=2
    )

    logo_im = get_logo_trasparente_ufficiale(max_w=240, max_h=130)
    if logo_im:
        lw, lh = logo_im.size
        lx = logo_box_x + (logo_box_w - lw) // 2
        ly = logo_box_y + (logo_box_h - lh) // 2
        canvas.paste(logo_im, (lx, ly), mask=logo_im.split()[3])
    else:
        font_logo_fb = get_font(20, bold=True, font_type="serif")
        draw.text((logo_box_x + 20, logo_box_y + 60), "IMMOBILIARE\nGIANCANI", font=font_logo_fb, fill=(15, 23, 42, 255))

    text_area_x = logo_box_x + logo_box_w + 30
    font_localita = get_font(22, bold=True, font_type="sans")
    font_sub = get_font(16, bold=False, font_type="sans")

    draw_fitted_text(draw, titolo, (text_area_x, 42, W - text_area_x - 30, 44), max_font_size=32, min_font_size=18, bold=True, fill=palette["text_primary"])
    draw.text((text_area_x, 92), f"📍 {zona}", font=font_localita, fill=palette["accent"])
    draw.text((text_area_x, 134), "ESCLUSIVA RESIDENZIALE • IMMOBILIARE GIANCANI", font=font_sub, fill=palette["text_secondary"])

    draw.line([(0, header_h), (W, header_h)], fill=palette["accent"], width=3)

    # ── 2. CENTER SECTION: FOTOGRAFIA HD CON WATERMARK (223 - 1160 px) ──
    foto_y = header_h + 3
    foto_h = 934

    foto_im = media_info.get('fotoImage')
    if not foto_im:
        foto_url = media_info.get('fotoUrl')
        if foto_url and foto_url.startswith('http'):
            try:
                r_img = requests.get(foto_url, verify=False, timeout=12)
                if r_img.status_code == 200:
                    foto_im = Image.open(io.BytesIO(r_img.content)).convert('RGB')
            except Exception:
                pass

    if not foto_im:
        candidati_cache = [
            os.path.join(PROJECT_DIR, "output_carosello"),
            os.path.join(PROJECT_DIR, "assets")
        ]
        for cdir in candidati_cache:
            if os.path.exists(cdir):
                for f in os.listdir(cdir):
                    if f.endswith(('.jpg', '.png')) and 'logo' not in f.lower():
                        try:
                            foto_im = Image.open(os.path.join(cdir, f)).convert('RGB')
                            break
                        except Exception:
                            pass
                if foto_im:
                    break

    if not foto_im:
        foto_im = Image.new('RGB', (W, foto_h), (35, 45, 60))
        d_tmp = ImageDraw.Draw(foto_im)
        d_tmp.rectangle([20, 20, W - 20, foto_h - 20], outline=palette["accent"], width=3)

    fw, fh = foto_im.size
    scale = max(W / fw, foto_h / fh)
    crop_w = int(fw * scale)
    crop_h = int(fh * scale)
    foto_scaled = foto_im.resize((crop_w, crop_h), Image.LANCZOS)
    cx = (crop_w - W) // 2
    cy = (crop_h - foto_h) // 2
    foto_cropped = foto_scaled.crop((cx, cy, cx + W, cy + foto_h))
    canvas.paste(foto_cropped, (0, foto_y))

    watermark = get_logo_trasparente_ufficiale(max_w=460, max_h=150, alpha=85)
    if watermark:
        ww, wh = watermark.size
        wx = (W - ww) // 2
        wy = foto_y + (foto_h - wh) // 2
        canvas.paste(watermark, (wx, wy), mask=watermark.split()[3])

    # Floating Badges
    font_prezzo = get_font(30, bold=True, font_type="sans")
    p_box_h = 62
    pb_w = font_prezzo.getbbox(prezzo_str)[2] - font_prezzo.getbbox(prezzo_str)[0] + 50
    draw.rounded_rectangle(
        [40, foto_y + 35, 40 + pb_w, foto_y + 35 + p_box_h],
        radius=31,
        fill=palette["badge_bg"],
        outline=(255, 255, 255, 230),
        width=2
    )
    draw.text((40 + 25, foto_y + 48), prezzo_str, font=font_prezzo, fill=palette["badge_txt"])

    specs_y = foto_y + foto_h - 75
    badge_items = [
        f"📐 {mq_str}",
        "🚪 5 LOCALI",
        "🌅 VISTA PANORAMICA",
        "✨ RIFINITO"
    ]
    bx = 35
    font_spec = get_font(18, bold=True, font_type="sans")
    for b_txt in badge_items:
        tw = font_spec.getbbox(b_txt)[2] - font_spec.getbbox(b_txt)[0] + 28
        if bx + tw > W - 20:
            break
        draw.rounded_rectangle(
            [bx, specs_y, bx + tw, specs_y + 46],
            radius=23,
            fill=(10, 20, 35, 220),
            outline=palette["accent"],
            width=2
        )
        draw.text((bx + 14, specs_y + 11), b_txt, font=font_spec, fill=(255, 255, 255, 255))
        bx += tw + 14

    # ── 3. LOWER SECTION: DIAGONAL SPLIT DARK FOOTER (1160 - 1750 px) ──
    diag_start_y = foto_y + foto_h
    footer_end_y = 1750

    poly_points = [
        (0, diag_start_y),
        (W, diag_start_y - 35),
        (W, footer_end_y),
        (0, footer_end_y)
    ]
    draw.polygon(poly_points, fill=palette["footer_bg"])
    draw.line([(0, diag_start_y), (W, diag_start_y - 35)], fill=palette["accent"], width=4)

    # Box Riferimento
    rif_x = 45
    rif_y = diag_start_y + 35
    rif_w = 340
    rif_h = footer_end_y - rif_y - 30

    draw.rounded_rectangle(
        [rif_x, rif_y, rif_x + rif_w, rif_y + rif_h],
        radius=16,
        fill=palette["footer_diag"],
        outline=palette["border_color"],
        width=2
    )

    font_rif_lbl = get_font(18, bold=True, font_type="sans")
    font_rif_cod = get_font(28, bold=True, font_type="sans")
    font_rif_sub = get_font(15, bold=False, font_type="sans")

    draw.text((rif_x + 22, rif_y + 24), "CODICE IMMOBILE", font=font_rif_lbl, fill=palette["accent"])
    draw.text((rif_x + 22, rif_y + 60), codice_rif, font=font_rif_cod, fill=(255, 255, 255, 255))
    draw.line([(rif_x + 22, rif_y + 115), (rif_x + rif_w - 22, rif_y + 115)], fill=palette["border_color"], width=1)

    info_rif = [
        "✓ Disponibilità: Immediata",
        "✓ Tipologia: Residenziale",
        "✓ Condizioni: Eccellenti",
        "✓ Gestione: Esclusiva",
        "✓ Certificazione A+"
    ]
    iry = rif_y + 135
    for ir in info_rif:
        draw.text((rif_x + 22, iry), ir, font=font_rif_sub, fill=palette["text_secondary"])
        iry += 36

    # Box Caratteristiche & Descrizione Colonna F
    caratt_x = rif_x + rif_w + 30
    caratt_y = diag_start_y + 20
    caratt_w = W - caratt_x - 45
    avail_desc_h = footer_end_y - caratt_y - 85

    font_caratt_title = get_font(24, bold=True, font_type="sans")
    draw.text((caratt_x, caratt_y + 15), "DESCRIZIONE IMMOBILE", font=font_caratt_title, fill=palette["accent"])
    draw.line([(caratt_x, caratt_y + 54), (caratt_x + caratt_w, caratt_y + 54)], fill=palette["accent"], width=2)

    testo_f = str(media_info.get('testoF') or '').strip()
    if not testo_f:
        testo_f = f"Soluzione esclusiva di {mq_str} rifinita nei minimi dettagli, con ampi spazi luminosi e massima privacy ad Agrigento e Favara. — Immobiliare Giancani"
    elif "immobiliare giancani" not in testo_f.lower():
        testo_f += " — Immobiliare Giancani"

    draw_fitted_text(draw, testo_f, (caratt_x, caratt_y + 68, caratt_w, avail_desc_h), max_font_size=20, min_font_size=13, line_spacing=5, fill=(255, 255, 255, 255))

    # ── 4. BOTTOM SECTION: CTA BUTTON & WHITE CONTACT BAR (1750 - 1920 px) ──
    btn_w = 780
    btn_h = 70
    btn_x = (W - btn_w) // 2
    btn_y = 1715

    draw.rounded_rectangle(
        [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
        radius=35,
        fill=palette["btn_cta_bg"],
        outline=(255, 255, 255, 240),
        width=2
    )
    font_btn = get_font(26, bold=True, font_type="sans")
    btn_txt = "👉 CHIEDI INFORMAZIONI ADESSO"
    bw = font_btn.getbbox(btn_txt)[2] - font_btn.getbbox(btn_txt)[0]
    draw.text(((W - bw) // 2, btn_y + 18), btn_txt, font=font_btn, fill=(255, 255, 255, 255))

    bottom_bar_y = 1815
    draw.rectangle([0, bottom_bar_y, W, H], fill=palette["bottom_bar_bg"])
    draw.line([(0, bottom_bar_y), (W, bottom_bar_y)], fill=palette["accent"], width=2)

    font_contacts = get_font(20, bold=True, font_type="sans")
    font_brand_bottom = get_font(21, bold=True, font_type="serif")

    contacts_txt = "📍 Corso Vittorio Veneto 151, Favara (AG) • 📞 Tel. 320 166 7156"
    cw = font_contacts.getbbox(contacts_txt)[2] - font_contacts.getbbox(contacts_txt)[0]
    draw.text(((W - cw) // 2, bottom_bar_y + 16), contacts_txt, font=font_contacts, fill=palette["bottom_bar_txt"])

    brand_txt = "Esperienza, Trasparenza & Affidabilità — Immobiliare Giancani"
    brw = font_brand_bottom.getbbox(brand_txt)[2] - font_brand_bottom.getbbox(brand_txt)[0]
    draw.text(((W - brw) // 2, bottom_bar_y + 54), brand_txt, font=font_brand_bottom, fill=(180, 130, 40, 255))

    canvas.save(output_path, "PNG")
    print(f"✅ Layout Marketing Banner generato: {output_path} (Palette: {palette['nome']})")
    return output_path

# ═══════════════════════════════════════════════════════════════════════════════
# 🏛️ 5. STILI COMPLEMENTARI CON PALETTE DINAMICA DEL GIORNO
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_splitscreen_9_16(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_splitscreen_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = Image.new('RGBA', (W, H), palette["primary_dark"])
    draw = ImageDraw.Draw(canvas)

    logo_im = get_logo_trasparente_ufficiale(max_w=440, max_h=120)
    if logo_im:
        lw, lh = logo_im.size
        canvas.paste(logo_im, ((W - lw) // 2, 45), mask=logo_im.split()[3])
    else:
        font_b = get_font(34, bold=True, font_type="serif")
        txt = "IMMOBILIARE GIANCANI"
        tw = font_b.getbbox(txt)[2] - font_b.getbbox(txt)[0]
        draw.text(((W - tw) // 2, 60), txt, font=font_b, fill=palette["accent"])

    font_badge = get_font(20, bold=True, font_type="sans")
    badge_txt = "★ OPPORTUNITÀ ESCLUSIVA IN DIRETTA ★"
    badg_w = font_badge.getbbox(badge_txt)[2] - font_badge.getbbox(badge_txt)[0] + 44
    draw.rounded_rectangle([(W - badg_w)//2, 185, (W + badg_w)//2, 230], radius=14, fill=palette["primary_mid"], outline=palette["accent"], width=2)
    draw.text(((W - font_badge.getbbox(badge_txt)[2]) // 2, 196), badge_txt, font=font_badge, fill=(255, 255, 255, 255))

    box_x = 40
    box_y = 255
    box_w = W - 80
    box_h = 1290

    draw.rounded_rectangle([box_x - 3, box_y - 3, box_x + box_w + 3, box_y + box_h + 3], radius=24, fill=palette["accent"])
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=22, fill=(248, 249, 251, 255))

    foto_im = media_info.get('fotoImage')
    if not foto_im:
        foto_im = Image.new('RGB', (box_w, 750), (220, 225, 235))

    fw, fh = foto_im.size
    foto_box_h = 720
    scale = max(box_w / fw, foto_box_h / fh)
    im_scaled = foto_im.resize((int(fw * scale), int(fh * scale)), Image.LANCZOS)
    im_cropped = im_scaled.crop((0, 0, box_w, foto_box_h))
    canvas.paste(im_cropped, (box_x, box_y))

    wm = get_logo_trasparente_ufficiale(max_w=380, max_h=110, alpha=80)
    if wm:
        canvas.paste(wm, (box_x + (box_w - wm.size[0]) // 2, box_y + 300), mask=wm.split()[3])

    info_y = box_y + foto_box_h + 30
    titolo = str(media_info.get('titolo', 'Villa Favara Rifinita')).upper()
    zona = str(media_info.get('zona', 'Favara ed Agrigento')).upper()
    prezzo = str(media_info.get('prezzo', 'Trattativa Riservata'))
    mq = formatta_metri_quadri(media_info.get('mq', '135'))

    font_tit = get_font(30, bold=True, font_type="sans")
    font_zn = get_font(20, bold=False, font_type="sans")
    draw_fitted_text(draw, titolo, (box_x + 35, info_y, box_w - 70, 42), max_font_size=30, min_font_size=18, bold=True, fill=palette["primary_dark"][:3])
    draw.text((box_x + 35, info_y + 45), f"📍 {zona}", font=font_zn, fill=palette["primary_mid"][:3])

    p_box_w = 260
    draw.rounded_rectangle([box_x + 35, info_y + 90, box_x + 35 + p_box_w, info_y + 145], radius=10, fill=palette["badge_bg"])
    draw.text((box_x + 50, info_y + 102), prezzo, font=get_font(24, bold=True, font_type="sans"), fill=palette["badge_txt"])

    draw.rounded_rectangle([box_x + 35 + p_box_w + 20, info_y + 90, box_x + box_w - 35, info_y + 145], radius=10, fill=(240, 243, 248, 255), outline=palette["border_color"], width=1)
    draw.text((box_x + 35 + p_box_w + 35, info_y + 104), f"📐 {mq}", font=get_font(20, bold=True, font_type="sans"), fill=palette["primary_dark"][:3])

    testo_f = str(media_info.get('testoF', 'Immobile di alto profilo con finiture di pregio, ampi spazi luminosi e vista aperta. — Immobiliare Giancani'))
    if "immobiliare giancani" not in testo_f.lower():
        testo_f += " — Immobiliare Giancani"

    desc_avail_h = (box_y + box_h) - (info_y + 165) - 25
    draw_fitted_text(draw, testo_f, (box_x + 35, info_y + 165, box_w - 70, desc_avail_h), max_font_size=22, min_font_size=13, line_spacing=5, fill=(50, 60, 75, 255))

    btn_w = 800
    btn_h = 70
    btn_x = (W - btn_w) // 2
    btn_y = H - 230
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=35, fill=palette["btn_cta_bg"])
    draw.text(((W - 380) // 2, btn_y + 18), "SCOPRI TUTTI I DETTAGLI >", font=get_font(25, bold=True, font_type="sans"), fill=(255, 255, 255, 255))

    font_scr = get_font(24, bold=False, font_type="script")
    draw.text(((W - 480) // 2, H - 120), "La tua prossima casa ti aspetta — Immobiliare Giancani", font=font_scr, fill=palette["accent"])

    canvas.save(output_path, "PNG")
    print(f"✅ Layout Split Screen generato: {output_path}")
    return output_path

def crea_story_luxury_glass_9_16(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_luxury_glass_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    foto_im = media_info.get('fotoImage')
    if not foto_im:
        foto_im = Image.new('RGB', (W, H), (20, 25, 35))

    fw, fh = foto_im.size
    scale = max(W / fw, H / fh)
    bg_scaled = foto_im.resize((int(fw * scale), int(fh * scale)), Image.LANCZOS)
    bg_cropped = bg_scaled.crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(radius=28))

    canvas = bg_cropped.convert('RGBA')
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 140))
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    logo_im = get_logo_trasparente_ufficiale(max_w=420, max_h=115)
    if logo_im:
        lw, lh = logo_im.size
        canvas.paste(logo_im, ((W - lw) // 2, 50), mask=logo_im.split()[3])

    card_x = 45
    card_y = 200
    card_w = W - 90
    card_h = 1460

    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=28, fill=(15, 20, 30, 210), outline=palette["accent"], width=2)

    foto_inner_h = 750
    scale_in = max(card_w / fw, foto_inner_h / fh)
    in_scaled = foto_im.resize((int(fw * scale_in), int(fh * scale_in)), Image.LANCZOS)
    in_cropped = in_scaled.crop((0, 0, card_w - 4, foto_inner_h))
    canvas.paste(in_cropped, (card_x + 2, card_y + 2))

    wm = get_logo_trasparente_ufficiale(max_w=340, max_h=90, alpha=75)
    if wm:
        canvas.paste(wm, (card_x + (card_w - wm.size[0]) // 2, card_y + 320), mask=wm.split()[3])

    titolo = str(media_info.get('titolo', 'Residenza Esclusiva')).upper()
    prezzo = str(media_info.get('prezzo', 'Trattativa Riservata'))
    mq = formatta_metri_quadri(media_info.get('mq', '140'))

    dy = card_y + foto_inner_h + 35
    draw_fitted_text(draw, titolo, (card_x + 35, dy, card_w - 70, 42), max_font_size=32, min_font_size=18, bold=True, fill=(255, 255, 255, 255))
    draw.text((card_x + 35, dy + 48), f"💎 {prezzo} • 📐 {mq}", font=get_font(24, bold=True, font_type="sans"), fill=palette["accent"])

    testo_f = str(media_info.get('testoF', 'Un connubio perfetto tra design contemporaneo, comfort e posizione strategica ad Agrigento e Favara. — Immobiliare Giancani'))
    if "immobiliare giancani" not in testo_f.lower():
        testo_f += " — Immobiliare Giancani"

    btn_w = 700
    btn_h = 68
    btn_x = (W - btn_w) // 2
    btn_y = card_y + card_h - 110

    avail_desc_h = max(60, btn_y - (dy + 95) - 15)
    draw_fitted_text(draw, testo_f, (card_x + 35, dy + 95, card_w - 70, avail_desc_h), max_font_size=22, min_font_size=13, line_spacing=5, fill=(225, 230, 240, 255))
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=34, fill=palette["accent"])
    draw.text(((W - 320) // 2, btn_y + 18), "PRENOTA UNA VISITA >", font=get_font(24, bold=True, font_type="sans"), fill=(15, 20, 30, 255))

    font_scr = get_font(22, bold=False, font_type="script")
    draw.text(((W - 460) // 2, H - 150), "L'eccellenza immobiliare in Sicilia — Immobiliare Giancani", font=font_scr, fill=(240, 240, 240, 255))

    canvas.save(output_path, "PNG")
    print(f"✅ Layout Luxury Glass generato: {output_path}")
    return output_path

def crea_story_editorial_9_16(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_editorial_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = Image.new('RGBA', (W, H), (250, 249, 246, 255))
    draw = ImageDraw.Draw(canvas)

    draw.text((60, 50), "COLLEZIONE IMMOBILIARE", font=get_font(18, bold=True, font_type="sans"), fill=palette["primary_mid"][:3])
    draw.line([(60, 80), (W - 60, 80)], fill=palette["primary_mid"][:3], width=1)

    logo_im = get_logo_trasparente_ufficiale(max_w=340, max_h=95)
    if logo_im:
        canvas.paste(logo_im, (W - 60 - logo_im.size[0], 95), mask=logo_im.split()[3])

    titolo = str(media_info.get('titolo', 'Dimora Storica Favara')).upper()
    logo_space = (logo_im.size[0] + 30) if logo_im else 0
    draw_fitted_text(draw, titolo, (60, 95, W - 120 - logo_space, 50), max_font_size=36, min_font_size=18, bold=True, font_type="serif", fill=palette["primary_dark"][:3])

    foto_im = media_info.get('fotoImage')
    if not foto_im:
        foto_im = Image.new('RGB', (W - 120, 850), (220, 220, 220))

    fw, fh = foto_im.size
    target_w, target_h = W - 120, 880
    scale = max(target_w / fw, target_h / fh)
    im_sc = foto_im.resize((int(fw * scale), int(fh * scale)), Image.LANCZOS)
    im_cr = im_sc.crop((0, 0, target_w, target_h))
    canvas.paste(im_cr, (60, 220))

    wm = get_logo_trasparente_ufficiale(max_w=320, max_h=90, alpha=75)
    if wm:
        canvas.paste(wm, (60 + (target_w - wm.size[0]) // 2, 220 + 380), mask=wm.split()[3])

    sy = 1130
    zona = str(media_info.get('zona', 'Agrigento e Favara')).upper()
    prezzo = str(media_info.get('prezzo', 'Trattativa Riservata'))
    mq = formatta_metri_quadri(media_info.get('mq', '125'))

    draw.text((60, sy), f"LOCALITÀ: {zona}", font=get_font(20, bold=True, font_type="sans"), fill=palette["accent"][:3])
    draw.text((60, sy + 38), f"PREZZO: {prezzo}  |  SUPERFICIE: {mq}", font=get_font(24, bold=True, font_type="serif"), fill=palette["primary_dark"][:3])
    draw.line([(60, sy + 80), (W - 60, sy + 80)], fill=(200, 200, 200, 255), width=1)

    testo_f = str(media_info.get('testoF', 'Spazi generosi pensati per vivere ogni momento in serenità e bellezza. Finiture ricercate e contesto signorile. — Immobiliare Giancani'))
    if "immobiliare giancani" not in testo_f.lower():
        testo_f += " — Immobiliare Giancani"

    avail_desc_h = max(60, (H - 240) - (sy + 95) - 20)
    draw_fitted_text(draw, testo_f, (60, sy + 95, W - 120, avail_desc_h), max_font_size=22, min_font_size=13, line_spacing=5, fill=(60, 65, 75, 255))

    draw.rounded_rectangle([60, H - 240, W - 60, H - 170], radius=12, fill=palette["primary_dark"])
    draw.text(((W - 360) // 2, H - 222), "RICHIEDI SCHEDA COMPLETA >", font=get_font(22, bold=True, font_type="sans"), fill=(255, 255, 255, 255))

    font_sign = get_font(22, bold=False, font_type="script")
    draw.text(((W - 440) // 2, H - 120), "Firmato con cura — Immobiliare Giancani", font=font_sign, fill=palette["accent"][:3])

    canvas.save(output_path, "PNG")
    print(f"✅ Layout Editorial generato: {output_path}")
    return output_path

# ═══════════════════════════════════════════════════════════════════════════════
# 🏠 7. STILE "ROOM LABEL" — Foto ambiente + barra blu con nome stanza (ref img1)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_room_label_9_16(media_info, palette=None, output_path=None):
    """Foto ambiente a schermo intero con header logo + barra inferiore con nome stanza."""
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_room_label_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = Image.new("RGBA", (W, H), (20, 20, 30, 255))
    draw = ImageDraw.Draw(canvas)

    # ── Foto a schermo intero ──
    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl", "")
    foto_img = None
    try:
        if foto_url.startswith("http"):
            import io as _io
            resp = requests.get(foto_url, timeout=12)
            foto_img = Image.open(_io.BytesIO(resp.content)).convert("RGBA")
        elif foto_url and os.path.exists(foto_url):
            foto_img = Image.open(foto_url).convert("RGBA")
    except Exception:
        pass

    if foto_img:
        fw, fh = foto_img.size
        scale = max(W / fw, H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        foto_img = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - H) // 2
        canvas.paste(foto_img.crop((ox, oy, ox + W, oy + H)), (0, 0))

    # Overlay gradiente leggero top e bottom per leggibilità
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for y in range(200):
        alpha = int(180 * (1 - y / 200))
        ov_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    for y in range(H - 220, H):
        alpha = int(200 * ((y - (H - 220)) / 220))
        ov_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    # ── Header logo bianco su sfondo semitrasparente ──
    header_h = 160
    header_rect = Image.new("RGBA", (W, header_h), palette["primary_dark"][:3] + (230,))
    canvas.alpha_composite(header_rect, (0, 0))
    logo = get_logo_trasparente_ufficiale(max_w=320, max_h=110)
    if logo:
        lw, lh = logo.size
        lx = (W - lw) // 2
        ly = (header_h - lh) // 2
        canvas.alpha_composite(logo, (lx, ly))

    # ── Barra blu inferiore con nome stanza ──
    barra_h = 160
    barra_y = H - barra_h
    barra_rect = Image.new("RGBA", (W, barra_h), palette["primary_dark"][:3] + (250,))
    canvas.alpha_composite(barra_rect, (0, barra_y))
    draw = ImageDraw.Draw(canvas)

    # Nome stanza ricavato dal titolo o da testoF colonna F
    testo_f = str(media_info.get("testoF", "")).strip()
    titolo = str(media_info.get("titolo", "SOGGIORNO")).strip().upper()
    # Cerca nome ambiente nel titolo (SOGGIORNO, CUCINA, CAMERA, BAGNO, ecc.)
    ambienti_noti = ["SOGGIORNO", "CUCINA", "CAMERA", "BAGNO", "INGRESSO", "TERRAZZO",
                     "GIARDINO", "GARAGE", "CANTINA", "STUDIO", "SALA", "SALOTTO"]
    nome_stanza = titolo
    for amb in ambienti_noti:
        if amb in titolo.upper():
            nome_stanza = amb
            break

    draw_fitted_text(draw, nome_stanza, (30, barra_y + 15, W - 60, barra_h - 30), max_font_size=80, min_font_size=28, bold=True, align="center", fill=(255, 255, 255, 255))

    # Watermark logo leggero al centro
    wm_logo = get_logo_trasparente_ufficiale(max_w=400, max_h=140, alpha=55)
    if wm_logo:
        wl, wh = wm_logo.size
        canvas.alpha_composite(wm_logo, ((W - wl) // 2, (H - wh) // 2))

    # Brand finale (RULE user_global)
    font_brand = get_font(36, bold=False, font_type="sans")
    brand_txt = "— Immobiliare Giancani"
    bb = draw.textbbox((0, 0), brand_txt, font=font_brand)
    draw = ImageDraw.Draw(canvas)
    draw.text(((W - (bb[2]-bb[0])) // 2, H - barra_h - 46), brand_txt,
              font=font_brand, fill=(255, 255, 255, 180))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[ROOM_LABEL] Salvato: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🏡 8. STILE "IDEACASA LAYOUT" — Logo TL, titolo TR, foto centrale, footer split (ref img2)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_ideacasa_layout_9_16(media_info, palette=None, output_path=None):
    """Layout 1:1 adattato a 9:16: logo top-left, titolo bold top-right,
       foto centrale grande con watermark, footer split RIFERIMENTO | CARATTERISTICHE."""
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_ideacasa_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    titolo = str(media_info.get("titolo", "VILLA CON GIARDINO")).strip().upper()
    zona = str(media_info.get("zona", "FAVARA (AG)")).strip().upper()
    prezzo_raw = str(media_info.get("prezzo", "Trattativa Riservata")).strip()
    if prezzo_raw.isdigit():
        prezzo_str = f"€ {int(prezzo_raw):,}".replace(",", ".")
    elif "€" not in prezzo_raw and any(c.isdigit() for c in prezzo_raw):
        prezzo_str = f"€ {prezzo_raw}"
    else:
        prezzo_str = prezzo_raw
    mq_str = formatta_metri_quadri(media_info.get("mq", "135"))
    codice_rif = str(media_info.get("codiceRif", media_info.get("tabName", "GIANCANI"))).replace("_", " ").upper()
    # Estrai caratteristiche dal testoF (Colonna F) - max 6 bullet
    testo_f = str(media_info.get("testoF", "")).strip()
    caratteristiche = []
    if testo_f:
        lines = [l.strip("•●-– ").strip() for l in re.split(r"[\n|;]|(?<=\w)\. (?=[A-Z])", testo_f) if l.strip()]
        caratteristiche = lines[:6]
    if not caratteristiche:
        caratteristiche = [mq_str, prezzo_str, "Vista panoramica", "Finiture di pregio"]

    HEADER_H = 290  # altezza header — abbastanza per wrappare il titolo senza sforare
    PHOTO_H  = 990  # altezza foto centrale
    FOOTER_H = 430  # altezza footer split
    MARGIN_H = max(10, H - HEADER_H - PHOTO_H - FOOTER_H)  # margine bianco residuo

    # ── HEADER ──
    header_color = palette["primary_dark"]
    draw.rectangle([(0, 0), (W, HEADER_H)], fill=header_color)

    # Logo Giancani all'interno di un box bianco ad alto contrasto (come ref img IdeaCasa)
    logo = get_logo_trasparente_ufficiale(max_w=280, max_h=130)
    if logo:
        lw, lh = logo.size
        pad_x, pad_y = 18, 12
        card_w = lw + pad_x * 2
        card_h = lh + pad_y * 2
        card_x = 24
        card_y = (HEADER_H - card_h) // 2
        # Card bianca con angoli arrotondati ed ombra
        draw.rounded_rectangle([(card_x + 3, card_y + 3), (card_x + card_w + 3, card_y + card_h + 3)],
                                radius=18, fill=(0, 0, 0, 60))
        draw.rounded_rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)],
                                radius=18, fill=(255, 255, 255, 255),
                                outline=palette["accent"][:3] + (220,), width=2)
        canvas.alpha_composite(logo, (card_x + pad_x, card_y + pad_y))
        title_x = card_x + card_w + 24
    else:
        title_x = 40
    title_w = W - title_x - 24

    title_text = f"{titolo} — {zona}" if zona and zona not in titolo else titolo
    draw_fitted_text(draw, title_text, (title_x, 20, title_w, HEADER_H - 40), max_font_size=42, min_font_size=18, bold=True, line_spacing=6, fill=(255, 255, 255, 255))

    # ── PHOTO ──
    photo_y = HEADER_H
    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl", "")
    foto_img = None
    try:
        if foto_url.startswith("http"):
            import io as _io
            resp = requests.get(foto_url, timeout=12)
            foto_img = Image.open(_io.BytesIO(resp.content)).convert("RGBA")
        elif foto_url and os.path.exists(foto_url):
            foto_img = Image.open(foto_url).convert("RGBA")
    except Exception:
        pass

    draw.rectangle([(0, photo_y), (W, photo_y + PHOTO_H)], fill=(200, 200, 210, 255))
    if foto_img:
        fw, fh = foto_img.size
        scale = max(W / fw, PHOTO_H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        foto_img = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - PHOTO_H) // 2
        canvas.paste(foto_img.crop((ox, oy, ox + W, oy + PHOTO_H)).convert("RGB"), (0, photo_y))

    # Watermark logo centro foto
    wm = get_logo_trasparente_ufficiale(max_w=380, max_h=130, alpha=50)
    if wm:
        wl, wh = wm.size
        canvas.alpha_composite(wm, ((W - wl) // 2, photo_y + (PHOTO_H - wh) // 2))

    # Margine bianco
    margin_y = photo_y + PHOTO_H
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, margin_y), (W, margin_y + MARGIN_H)], fill=(255, 255, 255, 255))

    # ── FOOTER SPLIT ──
    footer_y = H - FOOTER_H
    draw.rectangle([(0, footer_y), (W, H)], fill=palette["primary_dark"])

    # Linea diagonale divisoria
    mid_x = W // 3
    draw.polygon([(0, footer_y), (mid_x + 60, footer_y), (mid_x - 10, H), (0, H)],
                 fill=palette["accent"][:3] + (255,))

    # Lato sinistro: RIFERIMENTO
    # Lato sinistro: RIFERIMENTO & PREZZO (testo bianco nitido)
    font_rif_lbl = get_font(36, bold=True, font_type="sans")
    font_rif_num = get_font(72, bold=True, font_type="sans")
    font_rif_prz = get_font(46, bold=True, font_type="sans")
    draw.text((30, footer_y + 24), "RIFERIMENTO", font=font_rif_lbl, fill=(255, 255, 255, 255))
    cod_clean = codice_rif.replace("RIF. ", "").strip()
    draw.text((30, footer_y + 72), cod_clean, font=font_rif_num, fill=(255, 255, 255, 255))
    draw.text((30, footer_y + 160), prezzo_str, font=font_rif_prz, fill=(255, 255, 255, 255))

    # Lato destro: CARATTERISTICHE (colonna pulita senza sovrapposizioni)
    car_x = mid_x + 80
    font_car_lbl = get_font(38, bold=True, font_type="sans")
    font_car_li  = get_font(30, bold=False, font_type="sans")
    draw.text((car_x, footer_y + 24), "CARATTERISTICHE", font=font_car_lbl, fill=(255, 255, 255, 255))
    
    # 4 caratteristiche con wrapping/troncamento sicuro per non sforare
    car_items = caratteristiche[:4]
    for i, car in enumerate(car_items):
        car_clean = car.strip()
        if len(car_clean) > 36:
            car_clean = car_clean[:34] + "…"
        y_c = footer_y + 78 + i * 46
        draw.text((car_x, y_c), f"• {car_clean}", font=font_car_li, fill=(255, 255, 255, 255))

    # Brand finale
    font_brand = get_font(34, bold=True, font_type="sans")
    brand_txt = "Immobiliare Giancani"
    bb = draw.textbbox((0, 0), brand_txt, font=font_brand)
    bx = (W - (bb[2] - bb[0])) // 2
    draw.text((bx, H - 52), brand_txt, font=font_brand, fill=palette["accent"])

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[IDEACASA] Salvato: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🃏 9. STILE "CASAIT CARD" — Card bianca su sfondo scuro, badge icone, bottone CTA (ref img3)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_casait_card_9_16(media_info, palette=None, output_path=None):
    """Card bianca centrata su sfondo scuro, header colorato logo+titolo,
       foto immobile, badge prezzo+icone, bottone CTA — Immobiliare Giancani."""
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_casait_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    # Sfondo scuro
    canvas = Image.new("RGBA", (W, H), (30, 30, 40, 255))
    draw = ImageDraw.Draw(canvas)
    # Gradiente sfondo sottile
    for y in range(H):
        alpha = int(40 * abs(math.sin(math.pi * y / H)))
        draw.line([(0, y), (W, y)], fill=palette["primary_dark"][:3] + (alpha,))

    # Card bianca arrotondata centrata
    CARD_MARGIN = 50
    CARD_W = W - CARD_MARGIN * 2
    CARD_TOP = 160
    CARD_BOTTOM = H - 220
    card_h = CARD_BOTTOM - CARD_TOP
    card_rect = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_rect)
    card_draw.rounded_rectangle(
        [(CARD_MARGIN, CARD_TOP), (W - CARD_MARGIN, CARD_BOTTOM)],
        radius=40, fill=(255, 255, 255, 255)
    )
    canvas.alpha_composite(card_rect)
    draw = ImageDraw.Draw(canvas)

    # ── Card Header colorato ──
    CARD_HEADER_H = 140
    head_rect = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    head_draw = ImageDraw.Draw(head_rect)
    head_draw.rounded_rectangle(
        [(CARD_MARGIN, CARD_TOP), (W - CARD_MARGIN, CARD_TOP + CARD_HEADER_H)],
        radius=40, fill=palette["primary_dark"][:3] + (255,)
    )
    # Ripristina angoli bassi header
    head_draw.rectangle(
        [(CARD_MARGIN, CARD_TOP + 40), (W - CARD_MARGIN, CARD_TOP + CARD_HEADER_H)],
        fill=palette["primary_dark"][:3] + (255,)
    )
    canvas.alpha_composite(head_rect)
    draw = ImageDraw.Draw(canvas)

    # Logo nella header card
    logo = get_logo_trasparente_ufficiale(max_w=260, max_h=100)
    if logo:
        lw, lh = logo.size
        canvas.alpha_composite(logo, (CARD_MARGIN + 20, CARD_TOP + (CARD_HEADER_H - lh) // 2))

    titolo = str(media_info.get("titolo", "Appartamento in Vendita")).strip()
    zona = str(media_info.get("zona", "Favara")).strip()
    tx_card = CARD_MARGIN + 290
    max_title_w = CARD_W - 290 - 20
    title_full = f"{titolo} — {zona}" if zona and zona not in titolo else titolo
    draw_fitted_text(draw, title_full, (tx_card, CARD_TOP + 14, max_title_w, CARD_HEADER_H - 28),
                     max_font_size=38, min_font_size=16, bold=True, line_spacing=4, fill=(255, 255, 255, 255))

    # ── Foto nella card ──
    FOTO_TOP = CARD_TOP + CARD_HEADER_H + 4
    FOTO_H = 640
    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl", "")
    try:
        if foto_url.startswith("http"):
            import io as _io
            resp = requests.get(foto_url, timeout=12)
            foto_img = Image.open(_io.BytesIO(resp.content)).convert("RGB")
        elif foto_url and os.path.exists(foto_url):
            foto_img = Image.open(foto_url).convert("RGB")
        else:
            foto_img = None
    except Exception:
        foto_img = None

    # Clip foto in area card
    foto_area_w = CARD_W
    if foto_img:
        fw, fh = foto_img.size
        scale = max(foto_area_w / fw, FOTO_H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        foto_img = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - foto_area_w) // 2
        oy = (nh - FOTO_H) // 2
        foto_crop = foto_img.crop((ox, oy, ox + foto_area_w, oy + FOTO_H))
        canvas.paste(foto_crop, (CARD_MARGIN, FOTO_TOP))
    else:
        draw.rectangle([(CARD_MARGIN, FOTO_TOP), (W - CARD_MARGIN, FOTO_TOP + FOTO_H)],
                       fill=(180, 180, 190))

    # ── Banda prezzo in basso sulla foto ──
    prezzo_raw = str(media_info.get("prezzo", "")).strip()
    if prezzo_raw.isdigit():
        prezzo_str = f"€ {int(prezzo_raw):,}".replace(",", ".")
    elif "€" not in prezzo_raw and any(c.isdigit() for c in prezzo_raw):
        prezzo_str = f"€ {prezzo_raw}"
    else:
        prezzo_str = prezzo_raw if prezzo_raw else "Trattativa Riservata"

    PRICE_BAR_H = 90
    price_bar_y = FOTO_TOP + FOTO_H - PRICE_BAR_H
    draw.rectangle([(CARD_MARGIN, price_bar_y), (CARD_MARGIN + 300, FOTO_TOP + FOTO_H)],
                   fill=palette["primary_dark"][:3] + (230,))
    font_prezzo = get_font(58, bold=True, font_type="sans")
    draw.text((CARD_MARGIN + 16, price_bar_y + 14), prezzo_str, font=font_prezzo, fill=(255, 255, 255, 255))

    # Badge icone (locali, bagni, mq) a destra in basso sulla foto
    mq_str = formatta_metri_quadri(media_info.get("mq", "120"))
    locali = str(media_info.get("locali", "4"))
    bagni  = str(media_info.get("bagni", "1"))
    badges = [(f"{locali}", "▦"), (f"{bagni}", "🛁"), (mq_str.split()[0], "📐")]
    badge_w, badge_h = 150, 90
    badges_total_w = len(badges) * (badge_w + 10) - 10
    badges_x_start = W - CARD_MARGIN - badges_total_w
    badges_y = FOTO_TOP + FOTO_H - badge_h - 10
    for i, (val, icon) in enumerate(badges):
        bx = badges_x_start + i * (badge_w + 10)
        draw.rounded_rectangle([(bx, badges_y), (bx + badge_w, badges_y + badge_h)],
                                radius=12, fill=(255, 255, 255, 230))
        font_badge_lbl = get_font(28, bold=False, font_type="sans")
        font_badge_val = get_font(38, bold=True, font_type="sans")
        draw.text((bx + 8, badges_y + 4), icon, font=font_badge_lbl, fill=palette["primary_dark"])
        draw.text((bx + 8, badges_y + 36), val, font=font_badge_val, fill=palette["primary_dark"])

    # ── Bottone CTA ──
    CTA_Y = FOTO_TOP + FOTO_H + 40
    CTA_H = 110
    CTA_W = CARD_W - 80
    CTA_X = CARD_MARGIN + 40
    draw.rounded_rectangle([(CTA_X, CTA_Y), (CTA_X + CTA_W, CTA_Y + CTA_H)],
                            radius=55, fill=palette["accent"][:3] + (255,))
    font_cta = get_font(52, bold=True, font_type="sans")
    cta_txt = "🔗 Scopri di più"
    bb = draw.textbbox((0, 0), cta_txt, font=font_cta)
    draw.text(((W - (bb[2] - bb[0])) // 2, CTA_Y + (CTA_H - (bb[3] - bb[1])) // 2),
              cta_txt, font=font_cta, fill=(255, 255, 255, 255))

    # Brand finale
    font_brand = get_font(40, bold=True, font_type="sans")
    brand_txt = "Immobiliare Giancani"
    bb = draw.textbbox((0, 0), brand_txt, font=font_brand)
    draw.text(((W - (bb[2] - bb[0])) // 2, CARD_BOTTOM + 30), brand_txt,
              font=font_brand, fill=(255, 255, 255, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[CASAIT_CARD] Salvato: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🏗️ 10. STILE "TECNOCASA MULTI" — Titolo bold, foto grande + 2 mini, badge, CTA (ref img4)
# ═══════════════════════════════════════════════════════════════════════════════

def _disegna_icona_vettoriale(draw, cx, cy, r, tipo, colore, fill_colore=None):
    """Disegna icone vettoriali pulite e geometricamente perfette senza emoji.
    Compatibile 100% con Pillow su Windows.
    Tipi: 'mq', 'letto', 'casa', 'pin', 'albero', 'euro', 'check', 'freccia_dx'
    """
    fill_c = fill_colore or colore
    r = int(r)
    if tipo == "mq":
        # Icona m²: quadrato con m² al centro
        draw.rounded_rectangle([(cx - r, cy - r), (cx + r, cy + r)], radius=4, outline=colore, width=2)
        font_mq = get_font(max(11, int(r * 1.05)), bold=True, font_type="sans")
        bb = draw.textbbox((0, 0), "m²", font=font_mq)
        draw.text((cx - (bb[2] - bb[0]) // 2, cy - (bb[3] - bb[1]) // 2 - 2), "m²", font=font_mq, fill=colore)
    elif tipo == "letto":
        # Icona letto: spalliera sinistra, telaio materasso, cuscino bianco, gamba destra
        draw.rectangle([(cx - r, cy - int(r * 0.7)), (cx - int(r * 0.72), cy + int(r * 0.7))], fill=fill_c)
        draw.rectangle([(cx + int(r * 0.72), cy + int(r * 0.05)), (cx + r, cy + int(r * 0.7))], fill=fill_c)
        draw.rectangle([(cx - int(r * 0.72), cy + int(r * 0.05)), (cx + int(r * 0.72), cy + int(r * 0.55))], fill=fill_c)
        # Cuscino
        draw.rounded_rectangle([(cx - int(r * 0.62), cy - int(r * 0.35)), (cx - int(r * 0.15), cy)], radius=3, fill=fill_colore or (255, 255, 255, 255))
        # Piegatura coperta
        draw.line([(cx - int(r * 0.05), cy + int(r * 0.05)), (cx - int(r * 0.05), cy + int(r * 0.55))], fill=fill_colore or (255, 255, 255, 255), width=2)
    elif tipo in ("casa", "home"):
        # Icona casa: tetto + corpo + porta
        draw.polygon([(cx, cy - r), (cx - r, cy - int(r * 0.05)), (cx + r, cy - int(r * 0.05))], fill=fill_c)
        draw.rectangle([(cx - int(r * 0.75), cy - int(r * 0.05)), (cx + int(r * 0.75), cy + int(r * 0.8))], fill=fill_c)
        draw.rectangle([(cx - int(r * 0.22), cy + int(r * 0.25)), (cx + int(r * 0.22), cy + int(r * 0.8))], fill=fill_colore or (255, 255, 255, 255))
    elif tipo in ("pin", "posizione"):
        # Spillo mappa
        pr = int(r * 0.65)
        draw.ellipse([(cx - pr, cy - r), (cx + pr, cy - r + pr * 2)], fill=fill_c)
        draw.polygon([(cx - pr + 2, cy - r + pr), (cx + pr - 2, cy - r + pr), (cx, cy + r)], fill=fill_c)
        hr = int(pr * 0.4)
        draw.ellipse([(cx - hr, cy - r + pr - hr), (cx + hr, cy - r + pr + hr)], fill=fill_colore or (255, 255, 255, 255))
    elif tipo in ("albero", "giardino"):
        # Chioma albero rotonda + tronco
        draw.ellipse([(cx - int(r * 0.75), cy - r), (cx + int(r * 0.75), cy + int(r * 0.3))], fill=fill_c)
        draw.rectangle([(cx - int(r * 0.18), cy + int(r * 0.25)), (cx + int(r * 0.18), cy + r)], fill=fill_c)
    elif tipo == "euro":
        font_eu = get_font(max(12, int(r * 1.5)), bold=True, font_type="sans")
        bb = draw.textbbox((0, 0), "€", font=font_eu)
        draw.text((cx - (bb[2] - bb[0]) // 2, cy - (bb[3] - bb[1]) // 2 - 2), "€", font=font_eu, fill=colore)
    elif tipo == "check":
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=fill_c)
        draw.line([(cx - int(r * 0.5), cy), (cx - int(r * 0.15), cy + int(r * 0.45)), (cx + int(r * 0.55), cy - int(r * 0.35))],
                  fill=fill_colore or (255, 255, 255, 255), width=max(2, int(r * 0.22)))
    elif tipo == "freccia_dx":
        draw.polygon([(cx - int(r * 0.5), cy - int(r * 0.7)), (cx - int(r * 0.5), cy + int(r * 0.7)), (cx + int(r * 0.7), cy)], fill=fill_c)


def _disegna_badge_icona(draw, canvas, bx, by, bw, bh, tipo_icona, etichetta, valore,
                          palette, font_lbl, font_val, bg_color=None):
    """Badge orizzontale con cerchio icona vettoriale a sinistra e testo."""
    bg = bg_color or (248, 250, 255)
    draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=14,
                            fill=bg, outline=palette["primary_dark"][:3] + (140,), width=2)
    # Cerchio icona
    ic_r = bh // 2 - 8
    ic_cx = bx + bh // 2
    ic_cy = by + bh // 2
    draw.ellipse([(ic_cx - ic_r, ic_cy - ic_r), (ic_cx + ic_r, ic_cy + ic_r)],
                 fill=palette["accent"][:3] + (255,))
    _disegna_icona_vettoriale(draw, ic_cx, ic_cy, ic_r - 5, tipo_icona,
                               (255, 255, 255, 255), fill_colore=(255, 255, 255, 255))
    # Testo
    tx = bx + bh + 8
    val_clean = str(valore)[:18]
    if etichetta:
        lbl_bb = draw.textbbox((0, 0), etichetta, font=font_lbl)
        val_bb = draw.textbbox((0, 0), val_clean, font=font_val)
        tot_h = (lbl_bb[3] - lbl_bb[1]) + (val_bb[3] - val_bb[1]) + 2
        sy = by + (bh - tot_h) // 2
        draw.text((tx, sy), etichetta, font=font_lbl, fill=(110, 115, 130))
        draw.text((tx, sy + (lbl_bb[3] - lbl_bb[1]) + 2), val_clean, font=font_val, fill=palette["primary_dark"])
    else:
        val_bb = draw.textbbox((0, 0), val_clean, font=font_val)
        sy = by + (bh - (val_bb[3] - val_bb[1])) // 2
        draw.text((tx, sy), val_clean, font=font_val, fill=palette["primary_dark"])



def crea_story_tecnocasa_multi_9_16(media_info, palette=None, output_path=None):
    """Layout 'Tecnocasa Multi' fedele all'immagine di riferimento:
       - Header bianco con titolo bold gigante + 3 caratteristiche con icone tonde a sinistra
       - Foto principale grande con Floating Price Badge (badge bianco con tab PREZZO verde)
       - 2 Mini foto affiancate con angoli arrotondati
       - Riga 3 caratteristiche con icone tonde
       - Bottone CTA pill 'CHIEDI FOTO E INFORMAZIONI'
       - Footer completo: Logo Giancani, Corso Vittorio Veneto 151 Favara (AG), Tel. 320 166 7156
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_tecnocasa_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # ── 1. DATI IMMOBILE ──
    titolo = str(media_info.get("titolo", "IMMOBILE DI PRESTIGIO")).strip().upper()
    zona = str(media_info.get("zona", "FAVARA - AGRIGENTO")).strip().upper()
    prezzo_raw = str(media_info.get("prezzo", "")).strip()
    if prezzo_raw.isdigit():
        prezzo_str = f"€ {int(prezzo_raw):,}".replace(",", ".")
    elif "€" not in prezzo_raw and any(c.isdigit() for c in prezzo_raw):
        prezzo_str = f"€ {prezzo_raw}"
    else:
        prezzo_str = prezzo_raw if prezzo_raw else "Trattativa Riservata"

    mq_val = formatta_metri_quadri(media_info.get("mq", "120"))
    locali = str(media_info.get("locali", "4")).strip()
    codice_rif = str(media_info.get("codiceRif", media_info.get("tabName", "RIF. GIANCANI"))).replace("_", " ").upper()
    testo_f = str(media_info.get("testoF", "")).strip()

    # ── 2. CARICAMENTO FOTO IMMOBILE (Supporto foto reali e multiple) ──
    foto_principale = None
    foto_secondaria = None
    foto_terziaria = None

    foto_list = []
    if isinstance(media_info.get("altreFoto"), list):
        foto_list.extend(media_info["altreFoto"])
    for k in ["fotoUrl", "mediaUrl", "foto_01", "foto_02", "foto_03"]:
        u = media_info.get(k)
        if u and u not in foto_list:
            foto_list.append(u)

    def _apri_img(src):
        if not src:
            return None
        try:
            if str(src).startswith("http"):
                import io as _io
                resp = requests.get(src, timeout=12, verify=False)
                return Image.open(_io.BytesIO(resp.content)).convert("RGB")
            elif os.path.exists(str(src)):
                return Image.open(str(src)).convert("RGB")
        except Exception:
            pass
        return None

    for f_item in foto_list:
        im = _apri_img(f_item)
        if im:
            if not foto_principale:
                foto_principale = im
            elif not foto_secondaria:
                foto_secondaria = im
            elif not foto_terziaria:
                foto_terziaria = im

    if foto_principale and not foto_secondaria:
        foto_secondaria = foto_principale.copy()
    if foto_principale and not foto_terziaria:
        foto_terziaria = foto_principale.copy()

    # ── 3. HEADER BIANCO (Y: 0 -> 440) ──
    HEADER_H = 440
    draw.rectangle([(0, 0), (W, HEADER_H)], fill=(255, 255, 255, 255))
    draw.rectangle([(0, 0), (14, HEADER_H)], fill=palette["accent"])

    words_title = titolo.split()
    line_big = " ".join(words_title[:2]) if words_title else "IMMOBILE ESCLUSIVO"
    line_med = " ".join(words_title[2:5]) if len(words_title) > 2 else ""

    font_tit_1 = get_font(78, bold=True, font_type="sans")
    font_tit_2 = get_font(58, bold=True, font_type="sans")
    font_sub = get_font(38, bold=False, font_type="sans")

    ty = 26
    draw.text((44, ty), line_big, font=font_tit_1, fill=palette["primary_dark"])
    ty += draw.textbbox((0, 0), line_big, font=font_tit_1)[3] + 4

    if line_med:
        draw.text((44, ty), line_med, font=font_tit_2, fill=palette["accent"])
        ty += draw.textbbox((0, 0), line_med, font=font_tit_2)[3] + 4

    draw.text((44, ty), zona, font=font_sub, fill=(110, 115, 130))
    ty += draw.textbbox((0, 0), zona, font=font_sub)[3] + 12

    draw.line([(44, ty), (W - 44, ty)], fill=palette["accent"][:3] + (100,), width=2)
    ty += 14

    badge_items = [
        ("mq", mq_val),
        ("letto", f"{locali} LOCALI"),
        ("pin", zona[:22])
    ]
    bx = 44
    for ico_tipo, val_txt in badge_items:
        r_ico = 22
        cy_ico = ty + r_ico
        cx_ico = bx + r_ico
        draw.ellipse([(cx_ico - r_ico, cy_ico - r_ico), (cx_ico + r_ico, cy_ico + r_ico)],
                     fill=(255, 255, 255, 255), outline=palette["accent"][:3] + (255,), width=2)
        _disegna_icona_vettoriale(draw, cx_ico, cy_ico, r_ico - 5, ico_tipo, palette["accent"][:3] + (255,))
        font_item = get_font(30, bold=True, font_type="sans")
        draw.text((cx_ico + r_ico + 12, cy_ico - 15), val_txt, font=font_item, fill=palette["primary_dark"])
        bx += 340

    # ── 4. FOTO PRINCIPALE (Y: 440 -> 1040, H=600) ──
    MAIN_Y = 440
    MAIN_H = 600
    draw.rectangle([(0, MAIN_Y), (W, MAIN_Y + MAIN_H)], fill=(220, 225, 235))

    if foto_principale:
        fw, fh = foto_principale.size
        scale = max(W / fw, MAIN_H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        f_res = foto_principale.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - MAIN_H) // 2
        canvas.paste(f_res.crop((ox, oy, ox + W, oy + MAIN_H)), (0, MAIN_Y))

    # Floating Price Badge in sovraimpressione in basso a sinistra della foto principale
    CARD_P_X = 40
    CARD_P_Y = MAIN_Y + MAIN_H - 120
    CARD_P_W = 410
    CARD_P_H = 140

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([(CARD_P_X + 4, CARD_P_Y + 4), (CARD_P_X + CARD_P_W + 4, CARD_P_Y + CARD_P_H + 4)],
                            radius=20, fill=(0, 0, 0, 45))
    draw.rounded_rectangle([(CARD_P_X, CARD_P_Y), (CARD_P_X + CARD_P_W, CARD_P_Y + CARD_P_H)],
                            radius=20, fill=(255, 255, 255, 255), outline=palette["accent"][:3] + (220,), width=3)

    TAG_W, TAG_H = 136, 34
    draw.rounded_rectangle([(CARD_P_X + 20, CARD_P_Y + 14), (CARD_P_X + 20 + TAG_W, CARD_P_Y + 14 + TAG_H)],
                            radius=8, fill=palette["accent"][:3] + (255,))
    font_tag = get_font(23, bold=True, font_type="sans")
    tag_bb = draw.textbbox((0, 0), "PREZZO", font=font_tag)
    draw.text((CARD_P_X + 20 + (TAG_W - (tag_bb[2]-tag_bb[0])) // 2, CARD_P_Y + 14 + (TAG_H - (tag_bb[3]-tag_bb[1])) // 2 - 1),
              "PREZZO", font=font_tag, fill=(255, 255, 255, 255))

    font_p_big = get_font(56, bold=True, font_type="sans")
    draw.text((CARD_P_X + 22, CARD_P_Y + 58), prezzo_str, font=font_p_big, fill=palette["accent"])

    # ── 5. DUE MINI FOTO AFFIANCATE (Y: 1080 -> 1390, H=310) ──
    MINI_Y = 1080
    MINI_H = 310
    MINI_W = (W - 80) // 2

    mini_configs = [
        (foto_secondaria, 30, 0),
        (foto_terziaria, 30 + MINI_W + 20, 60)
    ]

    for m_img, mx, offset_crop in mini_configs:
        draw.rounded_rectangle([(mx, MINI_Y), (mx + MINI_W, MINI_Y + MINI_H)],
                                radius=18, fill=(220, 225, 235))
        if m_img:
            try:
                tw, th = m_img.size
                scale = max(MINI_W / tw, MINI_H / th)
                nw, nh = int(tw * scale), int(th * scale)
                m_res = m_img.resize((nw, nh), Image.LANCZOS)
                ox = (nw - MINI_W) // 2
                oy = max(0, min(nh - MINI_H, (nh - MINI_H) // 2 + offset_crop))
                crop_m = m_res.crop((ox, oy, ox + MINI_W, oy + MINI_H))

                mask = Image.new("L", (MINI_W, MINI_H), 0)
                ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (MINI_W, MINI_H)], radius=18, fill=255)
                crop_rgba = crop_m.convert("RGBA")
                crop_rgba.putalpha(mask)
                canvas.alpha_composite(crop_rgba, (mx, MINI_Y))
            except Exception:
                pass

        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle([(mx, MINI_Y), (mx + MINI_W, MINI_Y + MINI_H)],
                                radius=18, outline=(255, 255, 255, 255), width=3)

    # ── 6. RIGA 3 CARATTERISTICHE (Y: 1415 -> 1515, H=100) ──
    FEAT_Y = 1415
    FEAT_H = 95
    lines_f = [l.strip().rstrip(".").strip() for l in re.split(r"[.\n|;]", testo_f) if l.strip() and len(l.strip()) > 3]
    if not lines_f:
        lines_f = ["Spazio esterno vivibile", "Finiture di pregio", "Posizione tranquilla"]
    feat_labels = lines_f[:3]
    feat_icons = ["casa", "check", "albero"]

    col_w = (W - 60) // 3
    for i, (f_txt, f_ico) in enumerate(zip(feat_labels, feat_icons)):
        fx = 30 + i * col_w
        ic_r = 24
        ic_cx = fx + 32
        ic_cy = FEAT_Y + FEAT_H // 2
        draw.ellipse([(ic_cx - ic_r, ic_cy - ic_r), (ic_cx + ic_r, ic_cy + ic_r)],
                     fill=palette["accent"][:3] + (255,))
        _disegna_icona_vettoriale(draw, ic_cx, ic_cy, ic_r - 5, f_ico, (255, 255, 255, 255))

        words = f_txt.upper().split()
        r1 = " ".join(words[:2]) if words else "CARATTERISTICA"
        r2 = " ".join(words[2:4]) if len(words) > 2 else ""
        font_f1 = get_font(23, bold=True, font_type="sans")
        font_f2 = get_font(21, bold=False, font_type="sans")
        tx = ic_cx + ic_r + 10
        draw.text((tx, ic_cy - 20), r1, font=font_f1, fill=palette["primary_dark"])
        if r2:
            draw.text((tx, ic_cy + 4), r2, font=font_f2, fill=(110, 115, 130))

        if i < 2:
            div_x = fx + col_w - 6
            draw.line([(div_x, FEAT_Y + 12), (div_x, FEAT_Y + FEAT_H - 12)], fill=(220, 225, 235), width=2)

    # ── 7. BOTTONE CTA 'CHIEDI FOTO E INFORMAZIONI' (Y: 1535 -> 1650, H=115) ──
    CTA_Y = 1535
    CTA_H = 115
    CTA_W = W - 140
    CTA_X = 70

    dash_col = palette["accent"][:3] + (180,)
    draw.line([(28, CTA_Y + 30), (52, CTA_Y + 45)], fill=dash_col, width=4)
    draw.line([(20, CTA_Y + 58), (50, CTA_Y + 58)], fill=dash_col, width=4)
    draw.line([(28, CTA_Y + 86), (52, CTA_Y + 71)], fill=dash_col, width=4)
    draw.line([(W - 28, CTA_Y + 30), (W - 52, CTA_Y + 45)], fill=dash_col, width=4)
    draw.line([(W - 20, CTA_Y + 58), (W - 50, CTA_Y + 58)], fill=dash_col, width=4)
    draw.line([(W - 28, CTA_Y + 86), (W - 52, CTA_Y + 71)], fill=dash_col, width=4)

    draw.rounded_rectangle([(CTA_X, CTA_Y), (CTA_X + CTA_W, CTA_Y + CTA_H)],
                            radius=CTA_H // 2, fill=palette["accent"][:3] + (255,))

    play_r = 30
    play_cx = CTA_X + 50
    play_cy = CTA_Y + CTA_H // 2
    draw.ellipse([(play_cx - play_r, play_cy - play_r), (play_cx + play_r, play_cy + play_r)],
                 fill=(255, 255, 255, 255))
    _disegna_icona_vettoriale(draw, play_cx + 2, play_cy, play_r - 12, "freccia_dx", palette["accent"][:3] + (255,))

    font_cta = get_font(44, bold=True, font_type="sans")
    cta_txt = "CHIEDI FOTO E INFORMAZIONI"
    cta_bb = draw.textbbox((0, 0), cta_txt, font=font_cta)
    cta_tx = play_cx + play_r + 20 + (CTA_W - (play_cx - CTA_X + play_r + 20) - (cta_bb[2] - cta_bb[0])) // 2
    draw.text((cta_tx, CTA_Y + (CTA_H - (cta_bb[3] - cta_bb[1])) // 2 - 2),
              cta_txt, font=font_cta, fill=(255, 255, 255, 255))

    # ── 8. FOOTER UFFICIALE CON RECAPITI (Y: 1680 -> 1920) ──
    FOOTER_Y = 1680
    draw.rectangle([(0, FOOTER_Y), (W, H)], fill=(255, 255, 255, 255))
    draw.line([(40, FOOTER_Y), (W - 40, FOOTER_Y)], fill=(225, 230, 240), width=2)

    logo = get_logo_trasparente_ufficiale(max_w=280, max_h=110)
    if logo:
        lw, lh = logo.size
        canvas.alpha_composite(logo, (36, FOOTER_Y + 20))

    draw = ImageDraw.Draw(canvas)
    draw.line([(340, FOOTER_Y + 18), (340, FOOTER_Y + 140)], fill=(220, 225, 235), width=2)

    rx = 365
    draw.text((rx, FOOTER_Y + 16), "IMMOBILIARE GIANCANI", font=get_font(34, bold=True), fill=palette["primary_dark"])
    draw.text((rx, FOOTER_Y + 62), "Corso Vittorio Veneto 151, Favara (AG)", font=get_font(26, bold=False), fill=(95, 100, 115))
    draw.text((rx, FOOTER_Y + 98), "Tel. 320 166 7156", font=get_font(30, bold=True), fill=palette["accent"])

    rif_w, rif_h = 280, 42
    rif_x = (W - rif_w) // 2
    rif_y = H - 54
    draw.rounded_rectangle([(rif_x, rif_y), (rif_x + rif_w, rif_y + rif_h)],
                            radius=rif_h // 2, fill=palette["primary_dark"])
    font_rif = get_font(23, bold=True, font_type="sans")
    rif_txt = f"{codice_rif}"
    rif_bb = draw.textbbox((0, 0), rif_txt, font=font_rif)
    draw.text((rif_x + (rif_w - (rif_bb[2] - rif_bb[0])) // 2, rif_y + (rif_h - (rif_bb[3] - rif_bb[1])) // 2 - 1),
              rif_txt, font=font_rif, fill=(255, 255, 255, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[TECNOCASA_MULTI] Salvato con successo: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 📡 11. CARD "ANNUNCIO DIRETTA LIVE" — A random ogni 30 minuti (25% prob)

# ═══════════════════════════════════════════════════════════════════════════════
# 📡 11. CARD "ANNUNCIO DIRETTA LIVE" — Nastro Diagonale con Orario & Dati Immobile
# ═══════════════════════════════════════════════════════════════════════════════

def crea_card_annuncio_diretta_9_16(media_info, orario_diretta=None, palette=None, output_path=None):
    """
    Card speciale di annuncio diretta live con modello Nastro Diagonale (9:16 Storie):
    - Foto immobile a schermo pieno con logo e badge DIRETTA
    - Nastro Diagonale Rosso: OPEN HOUSE IN DIRETTA / OGGI ALLE ORE {orario_diretta}
    - Sezione inferiore: location, titolo, testo Colonna F, prezzo, invito alla diretta e branding Giancani.
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"card_annuncio_diretta_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    split_y = 1020
    ribbon_h = 175
    angle_deg = -10
    # Colore coordinato alla palette del giorno del Bot Carosello
    ribbon_color = palette.get("primary_mid", (168, 24, 48))[:3] if palette else (168, 24, 48)
    ribbon_accent = palette.get("accent", (255, 240, 130))[:3] if palette else (255, 240, 130)

    if not orario_diretta:
        orario_diretta = media_info.get("orario_diretta") or media_info.get("orario")
        if not orario_diretta:
            # Di default l'annuncio mattutino/pomeridiano punta alla diretta serale delle 20:00
            orario_diretta = "20:00"

    # 1. Carica foto immobile
    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl") or media_info.get("foto_url", "")
    foto_img = None
    if isinstance(foto_url, Image.Image):
        foto_img = foto_url.convert("RGB")
    elif str(foto_url).startswith("http"):
        try:
            r = requests.get(foto_url, timeout=12, verify=False)
            foto_img = Image.open(io.BytesIO(r.content)).convert("RGB")
        except Exception:
            pass
    elif foto_url and os.path.exists(str(foto_url)):
        try:
            foto_img = Image.open(str(foto_url)).convert("RGB")
        except Exception:
            pass

    if foto_img:
        fw, fh = foto_img.size
        scale = max(W / fw, H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        f_res = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - H) // 2
        canvas = f_res.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
    else:
        canvas = Image.new("RGBA", (W, H), (230, 235, 245, 255))

    # 2. Taglio diagonale inferiore
    rad = math.radians(angle_deg)
    tan_a = math.tan(rad)
    y_left = split_y
    y_right = int(split_y + W * tan_a)
    
    bottom_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_bot = ImageDraw.Draw(bottom_bg)
    poly_bot = [(0, y_left), (W, y_right), (W, H), (0, H)]
    draw_bot.polygon(poly_bot, fill=(250, 250, 248, 255))
    canvas = Image.alpha_composite(canvas, bottom_bg)

    # 3. Nastro Diagonale Inclinato
    rw = int(W * 1.5)
    rh = ribbon_h
    ribbon_layer = Image.new("RGBA", (rw, rh), ribbon_color + (255,))
    draw_rib = ImageDraw.Draw(ribbon_layer)

    r1_txt = "OPEN HOUSE IN DIRETTA"
    r2_txt = f"OGGI ALLE ORE {orario_diretta}".upper()

    f_r1 = get_font(58, bold=True, font_type="sans")
    f_r2 = get_font(64, bold=True, font_type="sans")

    bb_r1 = draw_rib.textbbox((0, 0), r1_txt, font=f_r1)
    bb_r2 = draw_rib.textbbox((0, 0), r2_txt, font=f_r2)

    h_r1 = bb_r1[3] - bb_r1[1]
    h_r2 = bb_r2[3] - bb_r2[1]
    tot_h = h_r1 + h_r2 + 8
    start_y = (rh - tot_h) // 2

    draw_rib.text(((rw - (bb_r1[2]-bb_r1[0])) // 2, start_y), r1_txt, font=f_r1, fill=(255, 255, 255, 255))
    draw_rib.text(((rw - (bb_r2[2]-bb_r2[0])) // 2, start_y + h_r1 + 8), r2_txt, font=f_r2, fill=(255, 240, 130, 255))

    rot_ribbon = ribbon_layer.rotate(-angle_deg, expand=True, resample=Image.BICUBIC)
    rot_w, rot_h = rot_ribbon.size
    cx = W // 2
    cy_rib = int(split_y + (W / 2) * tan_a)
    rx = cx - (rot_w // 2)
    ry = cy_rib - (rot_h // 2)

    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_mask = rot_ribbon.split()[3]
    shadow_img = Image.new("RGBA", (rot_w, rot_h), (0, 0, 0, 85))
    shadow_img.putalpha(shadow_mask)
    shadow_layer.paste(shadow_img, (rx + 5, ry + 7), shadow_img)
    canvas = Image.alpha_composite(canvas, shadow_layer)
    canvas.alpha_composite(rot_ribbon, (rx, ry))

    # 4. Header: Logo a sinistra + Badge LIVE a destra
    draw = ImageDraw.Draw(canvas)
    logo = get_logo_trasparente_ufficiale(max_w=280, max_h=80)
    if logo:
        lw, lh = logo.size
        draw.rounded_rectangle([(36, 44), (36 + lw + 24, 44 + lh + 16)], radius=14, fill=(255, 255, 255, 240))
        canvas.alpha_composite(logo, (48, 52))
    else:
        draw.rounded_rectangle([(36, 44), (340, 108)], radius=14, fill=(255, 255, 255, 240))
        f_b = get_font(26, bold=True)
        draw.text((50, 62), "IMMOBILIARE GIANCANI", font=f_b, fill=ribbon_color)

    draw = ImageDraw.Draw(canvas)

    badge_w, badge_h = 200, 60
    bx = W - badge_w - 36
    by = 44
    draw.rounded_rectangle([(bx, by), (bx + badge_w, by + badge_h)], radius=badge_h // 2, fill=(220, 30, 30, 245))
    f_live_tag = get_font(28, bold=True)
    live_txt = "● DIRETTA"
    bb_lt = draw.textbbox((0, 0), live_txt, font=f_live_tag)
    draw.text((bx + (badge_w - (bb_lt[2]-bb_lt[0])) // 2, by + (badge_h - (bb_lt[3]-bb_lt[1])) // 2 - 1),
              live_txt, font=f_live_tag, fill=(255, 255, 255, 255))

    # 5. Sezione Inferiore con Dati Immobile da Colonna F
    pad_left = 50
    curr_y = y_left + 120

    zona = str(media_info.get("zona", "Favara (AG)")).strip().upper()
    titolo = str(media_info.get("titolo", "VILLA CON GIARDINO")).strip().upper()
    loc_txt = f"{zona} • {titolo}"
    f_loc = get_font(30, bold=True, font_type="sans")
    draw.text((pad_left, curr_y), loc_txt[:48], font=f_loc, fill=(100, 105, 120, 255))
    curr_y += draw.textbbox((0, 0), loc_txt, font=f_loc)[3] + 14

    f_tit = get_font(42, bold=True, font_type="sans")
    tit_lines = _wrap_text_lines(draw, titolo, f_tit, W - pad_left * 2)
    for tl in tit_lines[:2]:
        draw.text((pad_left, curr_y), tl, font=f_tit, fill=(20, 25, 35, 255))
        bb_tl = draw.textbbox((0, 0), tl, font=f_tit)
        curr_y += (bb_tl[3] - bb_tl[1]) + 8

    curr_y += 6

    testo_f = str(media_info.get("testoF", "")).strip()
    if not testo_f:
        mq_str = formatta_metri_quadri(media_info.get("mq", "150"))
        prezzo_str = str(media_info.get("prezzo", "Trattativa Riservata"))
        testo_f = f"Splendida soluzione di {mq_str} con ampi spazi e finiture di pregio. Prezzo: € {prezzo_str}."

    testo_f_clean = re.sub(r'[\r\n]+', ' ', testo_f)
    f_desc = get_font(28, bold=False, font_type="sans")
    desc_lines = _wrap_text_lines(draw, testo_f_clean, f_desc, W - pad_left * 2)
    for dl in desc_lines[:4]:
        draw.text((pad_left, curr_y), dl, font=f_desc, fill=(45, 52, 65, 255))
        bb_dl = draw.textbbox((0, 0), dl, font=f_desc)
        curr_y += (bb_dl[3] - bb_dl[1]) + 6

    curr_y += 12

    prezzo_val = str(media_info.get("prezzo", "")).strip()
    if prezzo_val:
        p_txt = f"PREZZO: € {prezzo_val}".upper()
        f_pr = get_font(32, bold=True, font_type="sans")
        draw.text((pad_left, curr_y), p_txt, font=f_pr, fill=ribbon_color)
        curr_y += draw.textbbox((0, 0), p_txt, font=f_pr)[3] + 12

    cta_direct = "Tour virtuale in diretta: collegati per fare domande in tempo reale!"
    f_cta_d = get_font(26, bold=True, font_type="sans")
    draw.text((pad_left, curr_y), cta_direct, font=f_cta_d, fill=(15, 23, 42, 255))
    curr_y += draw.textbbox((0, 0), cta_direct, font=f_cta_d)[3] + 16

    foot_h = 100
    foot_y = H - foot_h - 40
    foot_w = W - 80
    foot_x = 40
    draw.rounded_rectangle([(foot_x, foot_y), (foot_x + foot_w, foot_y + foot_h)],
                           radius=30, fill=(15, 23, 42, 240), outline=(255, 255, 255, 180), width=2)
    f_b1 = get_font(30, bold=True)
    f_b2 = get_font(24, bold=False)
    t1 = "IMMOBILIARE GIANCANI"
    t2 = "Corso Vittorio Veneto 151, Favara (AG) • Tel. 320 166 7156"
    bb_t1 = draw.textbbox((0, 0), t1, font=f_b1)
    bb_t2 = draw.textbbox((0, 0), t2, font=f_b2)
    draw.text(((W - (bb_t1[2]-bb_t1[0])) // 2, foot_y + 14), t1, font=f_b1, fill=(255, 255, 255, 255))
    draw.text(((W - (bb_t2[2]-bb_t2[0])) // 2, foot_y + 54), t2, font=f_b2, fill=(212, 168, 83, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[ANNUNCIO_DIRETTA_9_16] Salvato: {output_path}")
    return output_path

def crea_card_annuncio_diretta_1_1(media_info, orario_diretta=None, palette=None, output_path=None):
    """
    Card speciale di annuncio diretta live con modello Nastro Diagonale (1:1 Post Feed).
    """
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"card_annuncio_diretta_1x1_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    split_y = 540
    ribbon_h = 140
    angle_deg = -10
    ribbon_color = palette.get("primary_mid", (168, 24, 48))[:3] if palette else (168, 24, 48)
    ribbon_accent = palette.get("accent", (255, 240, 130))[:3] if palette else (255, 240, 130)

    if not orario_diretta:
        orario_diretta = media_info.get("orario_diretta") or media_info.get("orario")
        if not orario_diretta:
            orario_diretta = "20:00"

    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl") or media_info.get("foto_url", "")
    foto_img = None
    if isinstance(foto_url, Image.Image):
        foto_img = foto_url.convert("RGB")
    elif str(foto_url).startswith("http"):
        try:
            r = requests.get(foto_url, timeout=12, verify=False)
            foto_img = Image.open(io.BytesIO(r.content)).convert("RGB")
        except Exception:
            pass
    elif foto_url and os.path.exists(str(foto_url)):
        try:
            foto_img = Image.open(str(foto_url)).convert("RGB")
        except Exception:
            pass

    if foto_img:
        fw, fh = foto_img.size
        scale = max(W / fw, H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        f_res = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - H) // 2
        canvas = f_res.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
    else:
        canvas = Image.new("RGBA", (W, H), (230, 235, 245, 255))

    rad = math.radians(angle_deg)
    tan_a = math.tan(rad)
    y_left = split_y
    y_right = int(split_y + W * tan_a)
    
    bottom_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_bot = ImageDraw.Draw(bottom_bg)
    poly_bot = [(0, y_left), (W, y_right), (W, H), (0, H)]
    draw_bot.polygon(poly_bot, fill=(250, 250, 248, 255))
    canvas = Image.alpha_composite(canvas, bottom_bg)

    rw = int(W * 1.5)
    rh = ribbon_h
    ribbon_layer = Image.new("RGBA", (rw, rh), ribbon_color + (255,))
    draw_rib = ImageDraw.Draw(ribbon_layer)

    r1_txt = "OPEN HOUSE IN DIRETTA"
    r2_txt = f"OGGI ALLE ORE {orario_diretta}".upper()

    f_r1 = get_font(46, bold=True, font_type="sans")
    f_r2 = get_font(52, bold=True, font_type="sans")

    bb_r1 = draw_rib.textbbox((0, 0), r1_txt, font=f_r1)
    bb_r2 = draw_rib.textbbox((0, 0), r2_txt, font=f_r2)

    h_r1 = bb_r1[3] - bb_r1[1]
    h_r2 = bb_r2[3] - bb_r2[1]
    tot_h = h_r1 + h_r2 + 8
    start_y = (rh - tot_h) // 2

    draw_rib.text(((rw - (bb_r1[2]-bb_r1[0])) // 2, start_y), r1_txt, font=f_r1, fill=(255, 255, 255, 255))
    draw_rib.text(((rw - (bb_r2[2]-bb_r2[0])) // 2, start_y + h_r1 + 8), r2_txt, font=f_r2, fill=ribbon_accent + (255,))

    rot_ribbon = ribbon_layer.rotate(-angle_deg, expand=True, resample=Image.BICUBIC)
    rot_w, rot_h = rot_ribbon.size
    cx = W // 2
    cy_rib = int(split_y + (W / 2) * tan_a)
    rx = cx - (rot_w // 2)
    ry = cy_rib - (rot_h // 2)

    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_mask = rot_ribbon.split()[3]
    shadow_img = Image.new("RGBA", (rot_w, rot_h), (0, 0, 0, 85))
    shadow_img.putalpha(shadow_mask)
    shadow_layer.paste(shadow_img, (rx + 5, ry + 7), shadow_img)
    canvas = Image.alpha_composite(canvas, shadow_layer)
    canvas.alpha_composite(rot_ribbon, (rx, ry))

    draw = ImageDraw.Draw(canvas)
    logo = get_logo_trasparente_ufficiale(max_w=280, max_h=80)
    if logo:
        lw, lh = logo.size
        draw.rounded_rectangle([(30, 30), (30 + lw + 24, 30 + lh + 16)], radius=12, fill=(255, 255, 255, 240))
        canvas.alpha_composite(logo, (42, 38))
    else:
        draw.rounded_rectangle([(30, 30), (320, 85)], radius=12, fill=(255, 255, 255, 240))
        f_b = get_font(24, bold=True)
        draw.text((44, 45), "IMMOBILIARE GIANCANI", font=f_b, fill=ribbon_color)

    draw = ImageDraw.Draw(canvas)
    badge_w, badge_h = 170, 50
    bx = W - badge_w - 30
    by = 30
    draw.rounded_rectangle([(bx, by), (bx + badge_w, by + badge_h)], radius=badge_h // 2, fill=(220, 30, 30, 245))
    f_live_tag = get_font(24, bold=True)
    live_txt = "● DIRETTA"
    bb_lt = draw.textbbox((0, 0), live_txt, font=f_live_tag)
    draw.text((bx + (badge_w - (bb_lt[2]-bb_lt[0])) // 2, by + (badge_h - (bb_lt[3]-bb_lt[1])) // 2 - 1),
              live_txt, font=f_live_tag, fill=(255, 255, 255, 255))

    pad_left = 50
    curr_y = y_left + 85

    zona = str(media_info.get("zona", "Favara (AG)")).strip().upper()
    titolo = str(media_info.get("titolo", "VILLA CON GIARDINO")).strip().upper()
    loc_txt = f"{zona} • {titolo}"
    f_loc = get_font(24, bold=True, font_type="sans")
    draw.text((pad_left, curr_y), loc_txt[:45], font=f_loc, fill=(100, 105, 120, 255))
    curr_y += draw.textbbox((0, 0), loc_txt, font=f_loc)[3] + 12

    f_tit = get_font(34, bold=True, font_type="sans")
    tit_lines = _wrap_text_lines(draw, titolo, f_tit, W - pad_left * 2)
    for tl in tit_lines[:2]:
        draw.text((pad_left, curr_y), tl, font=f_tit, fill=(20, 25, 35, 255))
        bb_tl = draw.textbbox((0, 0), tl, font=f_tit)
        curr_y += (bb_tl[3] - bb_tl[1]) + 8

    curr_y += 6

    testo_f = str(media_info.get("testoF", "")).strip()
    if not testo_f:
        mq_str = formatta_metri_quadri(media_info.get("mq", "150"))
        prezzo_str = str(media_info.get("prezzo", "Trattativa Riservata"))
        testo_f = f"Splendida soluzione di {mq_str} con ampi spazi e finiture di pregio. Prezzo: € {prezzo_str}."

    testo_f_clean = re.sub(r'[\r\n]+', ' ', testo_f)
    f_desc = get_font(22, bold=False, font_type="sans")
    desc_lines = _wrap_text_lines(draw, testo_f_clean, f_desc, W - pad_left * 2)
    for dl in desc_lines[:2]:
        draw.text((pad_left, curr_y), dl, font=f_desc, fill=(45, 52, 65, 255))
        bb_dl = draw.textbbox((0, 0), dl, font=f_desc)
        curr_y += (bb_dl[3] - bb_dl[1]) + 6

    curr_y += 10

    prezzo_val = str(media_info.get("prezzo", "")).strip()
    if prezzo_val:
        p_txt = f"PREZZO: € {prezzo_val}".upper()
        f_pr = get_font(26, bold=True, font_type="sans")
        draw.text((pad_left, curr_y), p_txt, font=f_pr, fill=ribbon_color)
        curr_y += draw.textbbox((0, 0), p_txt, font=f_pr)[3] + 10

    cta_direct = "Tour virtuale in diretta: collegati per fare domande in tempo reale!"
    f_cta_d = get_font(20, bold=True, font_type="sans")
    draw.text((pad_left, curr_y), cta_direct, font=f_cta_d, fill=(15, 23, 42, 255))
    curr_y += draw.textbbox((0, 0), cta_direct, font=f_cta_d)[3] + 10

    f_sign = get_font(20, bold=True, font_type="sans")
    sign_txt = "Immobiliare Giancani • Corso Vittorio Veneto 151, Favara • Tel. 320 166 7156"
    draw.text((pad_left, curr_y), sign_txt, font=f_sign, fill=ribbon_color)

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[ANNUNCIO_DIRETTA_1_1] Salvato: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🏷️ 12. STILE "CAPELLUPO SIDEBAR CARD" — Card bianca su foto con fascia contestuale settimanale (ref img)
# ═══════════════════════════════════════════════════════════════════════════════

def _wrap_text_lines(draw, text, font, max_width):
    words = text.split()
    lines = []
    curr = ""
    for w in words:
        test = f"{curr} {w}".strip()
        bb = draw.textbbox((0, 0), test, font=font)
        if (bb[2] - bb[0]) <= max_width:
            curr = test
        else:
            if curr:
                lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)
    return lines

def crea_story_capellupo_sidebar_9_16(media_info, palette=None, output_path=None):
    """
    Stile Capellupo Sidebar 9:16 (Storia Facebook).
    - Foto a schermo intero
    - Fascia laterale sinistra con colore di contesto settimanale
    - Card bianca rettangolare in alto a sinistra con logo, indirizzo in bold, prezzo ribassato in rosso, descrizione da Colonna F
    - Footer elegante con recapiti agenzia e personal branding Immobiliare Giancani
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_capellupo_{uuid.uuid4().hex[:6]}.png")
    if palette is None:
        palette = get_palette_settimanale()

    sidebar_w = 400
    card_x, card_y = 75, 140
    card_w = 520
    pad_x = 30
    font_addr_size = 36
    font_price_size = 28
    font_desc_size = 25
    inner_w = card_w - (pad_x * 2)

    # 1. Carica foto immobile
    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl") or media_info.get("foto_url", "")
    foto_img = None
    if isinstance(foto_url, Image.Image):
        foto_img = foto_url.convert("RGB")
    elif str(foto_url).startswith("http"):
        try:
            r = requests.get(foto_url, timeout=12, verify=False)
            foto_img = Image.open(io.BytesIO(r.content)).convert("RGB")
        except Exception:
            pass
    elif foto_url and os.path.exists(str(foto_url)):
        try:
            foto_img = Image.open(str(foto_url)).convert("RGB")
        except Exception:
            pass

    if foto_img:
        fw, fh = foto_img.size
        scale = max(W / fw, H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        f_res = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - H) // 2
        canvas = f_res.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
    else:
        canvas = Image.new("RGBA", (W, H), (45, 55, 72, 255))

    # 2. Fascia laterale semitrasparente settimanale
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    draw_ov.rectangle([(0, 0), (sidebar_w, H)], fill=palette.get("context_rgba", (16, 128, 98, 185)))
    canvas = Image.alpha_composite(canvas, overlay)

    # 3. Pre-calcolo dati & altezza card dinamica
    dummy_draw = ImageDraw.Draw(canvas)
    titolo = str(media_info.get("titolo", "APPARTAMENTO PANORAMICO")).strip().upper()
    zona = str(media_info.get("zona", "AGRIGENTO")).strip().upper()
    via_clean = re.sub(r'^(APPARTAMENTO|VILLA|CASA|IMMOBILE|ATTICO|TERRENO)\s+', '', titolo, flags=re.IGNORECASE).strip()
    if not via_clean or len(via_clean) < 3:
        via_clean = "VIA EMPEDOCLE"

    f_addr = get_font(font_addr_size, bold=True, font_type="sans")
    addr_lines = _wrap_text_lines(dummy_draw, via_clean, f_addr, inner_w)
    if zona and zona not in via_clean:
        addr_lines.append(zona)

    prezzo_raw = str(media_info.get("prezzo", "140.000")).strip()
    if prezzo_raw.isdigit():
        prezzo_val = f"€{int(prezzo_raw):,}".replace(",", ".")
    elif any(c.isdigit() for c in prezzo_raw):
        prezzo_val = f"€{prezzo_raw.replace('€', '').strip()}"
    else:
        prezzo_val = prezzo_raw
    ribasso_txt = f"PREZZO RIBASSATO {prezzo_val}".upper() if (media_info.get("ribassato") or "ribassat" in str(media_info.get("testoF", "")).lower()) else f"PREZZO {prezzo_val}".upper()
    f_price = get_font(font_price_size, bold=True, font_type="sans")

    testo_f = str(media_info.get("testoF", "")).strip()
    if not testo_f:
        mq_str = formatta_metri_quadri(media_info.get("mq", "160"))
        testo_f = f"Appartamento di {mq_str} composto da salone doppio, cucina, 3 camere, 2 bagni e camerino."
    testo_pulito = re.sub(r'[\r\n]+', ' ', testo_f)
    f_desc = get_font(font_desc_size, bold=True, font_type="sans")
    desc_lines = _wrap_text_lines(dummy_draw, testo_pulito, f_desc, inner_w)

    needed_h = 24 + 80 + 14 + 4 + 14
    for l in addr_lines:
        bb = dummy_draw.textbbox((0, 0), l, font=f_addr)
        needed_h += (bb[3] - bb[1]) + 6
    needed_h += 12 + (dummy_draw.textbbox((0, 0), ribasso_txt, font=f_price)[3] - dummy_draw.textbbox((0, 0), ribasso_txt, font=f_price)[1]) + 16
    for l in desc_lines[:6]:
        bb = dummy_draw.textbbox((0, 0), l, font=f_desc)
        needed_h += (bb[3] - bb[1]) + 6
    needed_h += 24
    
    foot_h = 100
    foot_y = H - foot_h - 40
    max_card_h = foot_y - card_y - 25
    card_h = min(max_card_h, max(needed_h, 580))

    # Disegna Card Bianca con ombra
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(card_x + 6, card_y + 6), (card_x + card_w + 6, card_y + card_h + 6)], fill=(0, 0, 0, 55))
    draw.rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], fill=(255, 255, 255, 255))

    cy = card_y + 20

    # Logo Ufficiale Trasparente
    logo = get_logo_trasparente_ufficiale(max_w=inner_w - 20, max_h=80)
    if logo:
        lw, lh = logo.size
        lx = card_x + (card_w - lw) // 2
        canvas.alpha_composite(logo, (lx, cy))
        cy += lh + 14
    else:
        f_brand = get_font(28, bold=True)
        draw.text((card_x + pad_x, cy), "IMMOBILIARE GIANCANI", font=f_brand, fill=palette.get("context_color", (16, 128, 98)))
        cy += 45

    draw = ImageDraw.Draw(canvas)

    # Linea separatrice contestuale
    ctx_col = palette.get("context_color", (16, 128, 98))
    draw.line([(card_x + pad_x, cy), (card_x + card_w - pad_x, cy)], fill=ctx_col, width=3)
    cy += 14

    # Indirizzo & Zona
    for l in addr_lines:
        bb = draw.textbbox((0, 0), l, font=f_addr)
        tx = card_x + (card_w - (bb[2] - bb[0])) // 2
        draw.text((tx, cy), l, font=f_addr, fill=ctx_col)
        cy += (bb[3] - bb[1]) + 6

    cy += 8

    # Prezzo / Ribasso in Rosso
    hl_col = palette.get("highlight", (220, 38, 38))
    draw.text((card_x + pad_x, cy), ribasso_txt, font=f_price, fill=hl_col)
    bb_pr = draw.textbbox((card_x + pad_x, cy), ribasso_txt, font=f_price)
    draw.line([(bb_pr[0], bb_pr[3] + 2), (bb_pr[2], bb_pr[3] + 2)], fill=hl_col, width=2)
    cy += (bb_pr[3] - bb_pr[1]) + 16

    # Descrizione Colonna F perfettamente calibrata all'interno della card
    txt_dark = palette.get("text_dark", (30, 41, 59))
    avail_desc_h = max(60, (card_y + card_h) - cy - 20)
    draw_fitted_text(draw, testo_pulito, (card_x + pad_x, cy, inner_w, avail_desc_h), max_font_size=23, min_font_size=13, line_spacing=5, fill=txt_dark)

    # 4. Footer Ufficiale Storie — Immobiliare Giancani
    foot_h = 100
    foot_y = H - foot_h - 40
    foot_w = W - 80
    foot_x = 40
    draw.rounded_rectangle([(foot_x, foot_y), (foot_x + foot_w, foot_y + foot_h)],
                           radius=30, fill=(15, 23, 42, 235), outline=(255, 255, 255, 180), width=2)
    f_b1 = get_font(30, bold=True)
    f_b2 = get_font(24, bold=False)
    t1 = "IMMOBILIARE GIANCANI"
    t2 = "Corso Vittorio Veneto 151, Favara (AG) • Tel. 320 166 7156"
    bb_t1 = draw.textbbox((0, 0), t1, font=f_b1)
    bb_t2 = draw.textbbox((0, 0), t2, font=f_b2)
    draw.text(((W - (bb_t1[2]-bb_t1[0])) // 2, foot_y + 14), t1, font=f_b1, fill=(255, 255, 255, 255))
    draw.text(((W - (bb_t2[2]-bb_t2[0])) // 2, foot_y + 54), t2, font=f_b2, fill=(212, 168, 83, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[CAPELLUPO_SIDEBAR_9_16] Salvato: {output_path} (Tema: {palette.get('nome', 'Settimanale')})")
    return output_path

def crea_flyer_capellupo_sidebar_1_1(media_info, palette=None, output_path=None):
    """
    Stile Capellupo Sidebar 1:1 (Post Feed / Volantino).
    """
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_capellupo_{uuid.uuid4().hex[:6]}.png")
    if palette is None:
        palette = get_palette_settimanale()

    sidebar_w = 330
    card_x, card_y = 65, 80
    card_w = 450
    pad_x = 26
    font_addr_size = 32
    font_price_size = 26
    font_desc_size = 23
    inner_w = card_w - (pad_x * 2)

    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl") or media_info.get("foto_url", "")
    foto_img = None
    if isinstance(foto_url, Image.Image):
        foto_img = foto_url.convert("RGB")
    elif str(foto_url).startswith("http"):
        try:
            r = requests.get(foto_url, timeout=12, verify=False)
            foto_img = Image.open(io.BytesIO(r.content)).convert("RGB")
        except Exception:
            pass
    elif foto_url and os.path.exists(str(foto_url)):
        try:
            foto_img = Image.open(str(foto_url)).convert("RGB")
        except Exception:
            pass

    if foto_img:
        fw, fh = foto_img.size
        scale = max(W / fw, H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        f_res = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - H) // 2
        canvas = f_res.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
    else:
        canvas = Image.new("RGBA", (W, H), (45, 55, 72, 255))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    draw_ov.rectangle([(0, 0), (sidebar_w, H)], fill=palette.get("context_rgba", (16, 128, 98, 185)))
    canvas = Image.alpha_composite(canvas, overlay)

    dummy_draw = ImageDraw.Draw(canvas)
    titolo = str(media_info.get("titolo", "APPARTAMENTO PANORAMICO")).strip().upper()
    zona = str(media_info.get("zona", "AGRIGENTO")).strip().upper()
    via_clean = re.sub(r'^(APPARTAMENTO|VILLA|CASA|IMMOBILE|ATTICO|TERRENO)\s+', '', titolo, flags=re.IGNORECASE).strip()
    if not via_clean or len(via_clean) < 3:
        via_clean = "VIA EMPEDOCLE"

    f_addr = get_font(font_addr_size, bold=True, font_type="sans")
    addr_lines = _wrap_text_lines(dummy_draw, via_clean, f_addr, inner_w)
    if zona and zona not in via_clean:
        addr_lines.append(zona)

    prezzo_raw = str(media_info.get("prezzo", "140.000")).strip()
    if prezzo_raw.isdigit():
        prezzo_val = f"€{int(prezzo_raw):,}".replace(",", ".")
    elif any(c.isdigit() for c in prezzo_raw):
        prezzo_val = f"€{prezzo_raw.replace('€', '').strip()}"
    else:
        prezzo_val = prezzo_raw
    ribasso_txt = f"PREZZO RIBASSATO {prezzo_val}".upper() if (media_info.get("ribassato") or "ribassat" in str(media_info.get("testoF", "")).lower()) else f"PREZZO {prezzo_val}".upper()
    f_price = get_font(font_price_size, bold=True, font_type="sans")

    testo_f = str(media_info.get("testoF", "")).strip()
    if not testo_f:
        mq_str = formatta_metri_quadri(media_info.get("mq", "160"))
        testo_f = f"Appartamento di {mq_str} composto da salone doppio, cucina, 3 camere, 2 bagni e camerino."
    testo_pulito = re.sub(r'[\r\n]+', ' ', testo_f)
    f_desc = get_font(font_desc_size, bold=True, font_type="sans")
    desc_lines = _wrap_text_lines(dummy_draw, testo_pulito, f_desc, inner_w)

    needed_h = 24 + 80 + 14 + 4 + 14
    for l in addr_lines:
        bb = dummy_draw.textbbox((0, 0), l, font=f_addr)
        needed_h += (bb[3] - bb[1]) + 6
    needed_h += 12 + (dummy_draw.textbbox((0, 0), ribasso_txt, font=f_price)[3] - dummy_draw.textbbox((0, 0), ribasso_txt, font=f_price)[1]) + 16
    for l in desc_lines[:6]:
        bb = dummy_draw.textbbox((0, 0), l, font=f_desc)
        needed_h += (bb[3] - bb[1]) + 6
    needed_h += 24
    card_h = max(needed_h, 480)

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(card_x + 6, card_y + 6), (card_x + card_w + 6, card_y + card_h + 6)], fill=(0, 0, 0, 55))
    draw.rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], fill=(255, 255, 255, 255))

    cy = card_y + 20
    logo = get_logo_trasparente_ufficiale(max_w=inner_w - 20, max_h=80)
    if logo:
        lw, lh = logo.size
        lx = card_x + (card_w - lw) // 2
        canvas.alpha_composite(logo, (lx, cy))
        cy += lh + 14
    else:
        f_brand = get_font(28, bold=True)
        draw.text((card_x + pad_x, cy), "IMMOBILIARE GIANCANI", font=f_brand, fill=palette.get("context_color", (16, 128, 98)))
        cy += 45

    draw = ImageDraw.Draw(canvas)
    ctx_col = palette.get("context_color", (16, 128, 98))
    draw.line([(card_x + pad_x, cy), (card_x + card_w - pad_x, cy)], fill=ctx_col, width=3)
    cy += 14

    for l in addr_lines:
        bb = draw.textbbox((0, 0), l, font=f_addr)
        tx = card_x + (card_w - (bb[2] - bb[0])) // 2
        draw.text((tx, cy), l, font=f_addr, fill=ctx_col)
        cy += (bb[3] - bb[1]) + 6

    cy += 8
    hl_col = palette.get("highlight", (220, 38, 38))
    draw.text((card_x + pad_x, cy), ribasso_txt, font=f_price, fill=hl_col)
    bb_pr = draw.textbbox((card_x + pad_x, cy), ribasso_txt, font=f_price)
    draw.line([(bb_pr[0], bb_pr[3] + 2), (bb_pr[2], bb_pr[3] + 2)], fill=hl_col, width=2)
    cy += (bb_pr[3] - bb_pr[1]) + 16

    txt_dark = palette.get("text_dark", (30, 41, 59))
    for l in desc_lines[:6]:
        draw.text((card_x + pad_x, cy), l, font=f_desc, fill=txt_dark)
        bb_l = draw.textbbox((0, 0), l, font=f_desc)
        cy += (bb_l[3] - bb_l[1]) + 6

    # Tag contatto in basso a destra
    tag_w, tag_h = 440, 52
    tag_x = W - tag_w - 30
    tag_y = H - tag_h - 30
    draw.rounded_rectangle([(tag_x, tag_y), (tag_x + tag_w, tag_y + tag_h)],
                           radius=26, fill=(15, 23, 42, 235), outline=(255, 255, 255, 160), width=2)
    f_b1 = get_font(22, bold=True)
    t1 = "IMMOBILIARE GIANCANI • 320 166 7156"
    bb_t1 = draw.textbbox((0, 0), t1, font=f_b1)
    draw.text((tag_x + (tag_w - (bb_t1[2]-bb_t1[0])) // 2, tag_y + (tag_h - (bb_t1[3]-bb_t1[1])) // 2 - 1),
              t1, font=f_b1, fill=(255, 255, 255, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[CAPELLUPO_SIDEBAR_1_1] Salvato: {output_path} (Tema: {palette.get('nome', 'Settimanale')})")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🎀 13. STILE "GABETTI DIAGONAL RIBBON" — Nastro diagonale inclinato & sezione claim (ref img)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_gabetti_diagonal_9_16(media_info, palette=None, output_path=None):
    """
    Stile Gabetti Diagonal Ribbon 9:16 (Storia Facebook).
    - Foto grande in alto con logo protetto in alto a sinistra
    - Nastro diagonale inclinato con testo bold d'impatto
    - Sezione inferiore chiara con location, claim Colonna F e CTA valutazione
    - Footer elegante con recapiti agenzia — Immobiliare Giancani
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_gabetti_{uuid.uuid4().hex[:6]}.png")
    if palette is None:
        palette = get_palette_del_giorno()

    ribbon_color = palette.get("accent", (158, 26, 52))[:3]
    split_y = 1060
    ribbon_h = 160
    angle_deg = -10
    font_ribbon_size = 62
    font_loc_size = 28
    font_head_size = 38
    font_badge_size = 32
    font_cta_size = 24

    # 1. Carica foto immobile
    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl") or media_info.get("foto_url", "")
    foto_img = None
    if isinstance(foto_url, Image.Image):
        foto_img = foto_url.convert("RGB")
    elif str(foto_url).startswith("http"):
        try:
            r = requests.get(foto_url, timeout=12, verify=False)
            foto_img = Image.open(io.BytesIO(r.content)).convert("RGB")
        except Exception:
            pass
    elif foto_url and os.path.exists(str(foto_url)):
        try:
            foto_img = Image.open(str(foto_url)).convert("RGB")
        except Exception:
            pass

    if foto_img:
        fw, fh = foto_img.size
        scale = max(W / fw, H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        f_res = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - H) // 2
        canvas = f_res.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
    else:
        canvas = Image.new("RGBA", (W, H), (230, 235, 245, 255))

    # 2. Taglio diagonale inferiore
    rad = math.radians(angle_deg)
    tan_a = math.tan(rad)
    y_left = split_y
    y_right = int(split_y + W * tan_a)
    
    bottom_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_bot = ImageDraw.Draw(bottom_bg)
    poly_bot = [(0, y_left), (W, y_right), (W, H), (0, H)]
    draw_bot.polygon(poly_bot, fill=(248, 248, 246, 255))
    canvas = Image.alpha_composite(canvas, bottom_bg)

    # 3. Nastro Diagonale Ruotato
    rw = int(W * 1.5)
    rh = ribbon_h
    ribbon_layer = Image.new("RGBA", (rw, rh), ribbon_color + (255,))
    draw_rib = ImageDraw.Draw(ribbon_layer)

    titolo = str(media_info.get("titolo", "OPEN HOUSE")).strip().upper()
    prezzo_raw = str(media_info.get("prezzo", "")).strip()
    ribasso = media_info.get("ribassato") or "ribassat" in str(media_info.get("testoF", "")).lower()

    if media_info.get("nastro_r1") and media_info.get("nastro_r2"):
        r1_txt = str(media_info.get("nastro_r1")).upper()
        r2_txt = str(media_info.get("nastro_r2")).upper()
    elif ribasso:
        r1_txt = "PREZZO RIBASSATO"
        r2_txt = f"VENDITA ESCLUSIVA € {prezzo_raw}" if prezzo_raw else "VENDITA ESCLUSIVA"
    elif "OPEN HOUSE" in titolo:
        r1_txt = "OPEN HOUSE"
        r2_txt = "VENDUTO IN TEMPO RECORD"
    else:
        r1_txt = "NUOVA OPPORTUNITÀ"
        r2_txt = f"ESCLUSIVA GIANCANI € {prezzo_raw}" if prezzo_raw else "ESCLUSIVA GIANCANI"

    f_rib = get_font(font_ribbon_size, bold=True, font_type="sans")
    bb_r1 = draw_rib.textbbox((0, 0), r1_txt, font=f_rib)
    bb_r2 = draw_rib.textbbox((0, 0), r2_txt, font=f_rib)
    h_r1 = bb_r1[3] - bb_r1[1]
    h_r2 = bb_r2[3] - bb_r2[1]
    tot_h = h_r1 + h_r2 + 6
    start_y = (rh - tot_h) // 2

    draw_rib.text(((rw - (bb_r1[2]-bb_r1[0])) // 2, start_y), r1_txt, font=f_rib, fill=(255, 255, 255, 255))
    draw_rib.text(((rw - (bb_r2[2]-bb_r2[0])) // 2, start_y + h_r1 + 6), r2_txt, font=f_rib, fill=(255, 255, 255, 255))

    rot_ribbon = ribbon_layer.rotate(-angle_deg, expand=True, resample=Image.BICUBIC)
    rot_w, rot_h = rot_ribbon.size
    cx = W // 2
    cy_rib = int(split_y + (W / 2) * tan_a)
    rx = cx - (rot_w // 2)
    ry = cy_rib - (rot_h // 2)

    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_mask = rot_ribbon.split()[3]
    shadow_img = Image.new("RGBA", (rot_w, rot_h), (0, 0, 0, 80))
    shadow_img.putalpha(shadow_mask)
    shadow_layer.paste(shadow_img, (rx + 4, ry + 6), shadow_img)
    canvas = Image.alpha_composite(canvas, shadow_layer)
    canvas.alpha_composite(rot_ribbon, (rx, ry))

    # 4. Logo Ufficiale
    draw = ImageDraw.Draw(canvas)
    logo = get_logo_trasparente_ufficiale(max_w=280, max_h=80)
    if logo:
        lw, lh = logo.size
        draw.rounded_rectangle([(36, 46), (36 + lw + 24, 46 + lh + 16)], radius=14, fill=(255, 255, 255, 240))
        canvas.alpha_composite(logo, (48, 54))
    else:
        draw.rounded_rectangle([(36, 46), (340, 110)], radius=14, fill=(255, 255, 255, 240))
        f_b = get_font(26, bold=True)
        draw.text((50, 64), "IMMOBILIARE GIANCANI", font=f_b, fill=ribbon_color)

    draw = ImageDraw.Draw(canvas)

    # 5. Sezione Inferiore
    pad_left = 50
    curr_y = y_left + 110

    zona = str(media_info.get("zona", "Favara (AG)")).strip()
    loc_txt = f"{zona}: {titolo.title()}" if zona and zona.lower() not in titolo.lower() else titolo.title()
    f_loc = get_font(font_loc_size, bold=True, font_type="sans")
    draw.text((pad_left, curr_y), loc_txt[:48], font=f_loc, fill=(90, 95, 105, 255))
    curr_y += draw.textbbox((0, 0), loc_txt, font=f_loc)[3] + 16

    testo_f = str(media_info.get("testoF", "")).strip()
    foot_h = 100
    foot_y = H - foot_h - 40
    avail_desc_h = max(60, (foot_y - 20) - curr_y - 45)
    curr_y = draw_fitted_text(draw, testo_f, (pad_left, curr_y, W - pad_left * 2, min(avail_desc_h, 160)), max_font_size=font_head_size, min_font_size=15, bold=True, line_spacing=6, fill=(24, 28, 36, 255))
    curr_y += 12

    badge_claim = str(media_info.get("claim", "+10% Il nostro metodo funziona!"))
    f_badge = get_font(font_badge_size, bold=True, font_type="sans")
    draw.text((pad_left, curr_y), badge_claim, font=f_badge, fill=ribbon_color)
    curr_y += draw.textbbox((0, 0), badge_claim, font=f_badge)[3] + 14

    # Footer per Storie 9:16
    foot_h = 100
    foot_y = H - foot_h - 40
    foot_w = W - 80
    foot_x = 40
    draw.rounded_rectangle([(foot_x, foot_y), (foot_x + foot_w, foot_y + foot_h)],
                           radius=30, fill=(15, 23, 42, 235), outline=(255, 255, 255, 180), width=2)
    f_b1 = get_font(30, bold=True)
    f_b2 = get_font(24, bold=False)
    t1 = "IMMOBILIARE GIANCANI"
    t2 = "Corso Vittorio Veneto 151, Favara (AG) • Tel. 320 166 7156"
    bb_t1 = draw.textbbox((0, 0), t1, font=f_b1)
    bb_t2 = draw.textbbox((0, 0), t2, font=f_b2)
    draw.text(((W - (bb_t1[2]-bb_t1[0])) // 2, foot_y + 14), t1, font=f_b1, fill=(255, 255, 255, 255))
    draw.text(((W - (bb_t2[2]-bb_t2[0])) // 2, foot_y + 54), t2, font=f_b2, fill=(212, 168, 83, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[GABETTI_DIAGONAL_9_16] Salvato: {output_path}")
    return output_path

def crea_flyer_gabetti_diagonal_1_1(media_info, palette=None, output_path=None):
    """
    Stile Gabetti Diagonal Ribbon 1:1 (Post Feed / Volantino).
    """
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_gabetti_{uuid.uuid4().hex[:6]}.png")
    if palette is None:
        palette = get_palette_del_giorno()

    ribbon_color = palette.get("accent", (158, 26, 52))[:3]
    split_y = 570
    ribbon_h = 130
    angle_deg = -10
    font_ribbon_size = 54
    font_loc_size = 24
    font_head_size = 32
    font_badge_size = 28
    font_cta_size = 21

    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl") or media_info.get("foto_url", "")
    foto_img = None
    if isinstance(foto_url, Image.Image):
        foto_img = foto_url.convert("RGB")
    elif str(foto_url).startswith("http"):
        try:
            r = requests.get(foto_url, timeout=12, verify=False)
            foto_img = Image.open(io.BytesIO(r.content)).convert("RGB")
        except Exception:
            pass
    elif foto_url and os.path.exists(str(foto_url)):
        try:
            foto_img = Image.open(str(foto_url)).convert("RGB")
        except Exception:
            pass

    if foto_img:
        fw, fh = foto_img.size
        scale = max(W / fw, H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        f_res = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - H) // 2
        canvas = f_res.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
    else:
        canvas = Image.new("RGBA", (W, H), (230, 235, 245, 255))

    rad = math.radians(angle_deg)
    tan_a = math.tan(rad)
    y_left = split_y
    y_right = int(split_y + W * tan_a)
    
    bottom_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_bot = ImageDraw.Draw(bottom_bg)
    poly_bot = [(0, y_left), (W, y_right), (W, H), (0, H)]
    draw_bot.polygon(poly_bot, fill=(248, 248, 246, 255))
    canvas = Image.alpha_composite(canvas, bottom_bg)

    rw = int(W * 1.5)
    rh = ribbon_h
    ribbon_layer = Image.new("RGBA", (rw, rh), ribbon_color + (255,))
    draw_rib = ImageDraw.Draw(ribbon_layer)

    titolo = str(media_info.get("titolo", "OPEN HOUSE")).strip().upper()
    prezzo_raw = str(media_info.get("prezzo", "")).strip()
    ribasso = media_info.get("ribassato") or "ribassat" in str(media_info.get("testoF", "")).lower()

    if media_info.get("nastro_r1") and media_info.get("nastro_r2"):
        r1_txt = str(media_info.get("nastro_r1")).upper()
        r2_txt = str(media_info.get("nastro_r2")).upper()
    elif ribasso:
        r1_txt = "PREZZO RIBASSATO"
        r2_txt = f"VENDITA ESCLUSIVA € {prezzo_raw}" if prezzo_raw else "VENDITA ESCLUSIVA"
    elif "OPEN HOUSE" in titolo:
        r1_txt = "OPEN HOUSE"
        r2_txt = "VENDUTO IN TEMPO RECORD"
    else:
        r1_txt = "NUOVA OPPORTUNITÀ"
        r2_txt = f"ESCLUSIVA GIANCANI € {prezzo_raw}" if prezzo_raw else "ESCLUSIVA GIANCANI"

    f_rib = get_font(font_ribbon_size, bold=True, font_type="sans")
    bb_r1 = draw_rib.textbbox((0, 0), r1_txt, font=f_rib)
    bb_r2 = draw_rib.textbbox((0, 0), r2_txt, font=f_rib)
    h_r1 = bb_r1[3] - bb_r1[1]
    h_r2 = bb_r2[3] - bb_r2[1]
    tot_h = h_r1 + h_r2 + 6
    start_y = (rh - tot_h) // 2

    draw_rib.text(((rw - (bb_r1[2]-bb_r1[0])) // 2, start_y), r1_txt, font=f_rib, fill=(255, 255, 255, 255))
    draw_rib.text(((rw - (bb_r2[2]-bb_r2[0])) // 2, start_y + h_r1 + 6), r2_txt, font=f_rib, fill=(255, 255, 255, 255))

    rot_ribbon = ribbon_layer.rotate(-angle_deg, expand=True, resample=Image.BICUBIC)
    rot_w, rot_h = rot_ribbon.size
    cx = W // 2
    cy_rib = int(split_y + (W / 2) * tan_a)
    rx = cx - (rot_w // 2)
    ry = cy_rib - (rot_h // 2)

    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_mask = rot_ribbon.split()[3]
    shadow_img = Image.new("RGBA", (rot_w, rot_h), (0, 0, 0, 80))
    shadow_img.putalpha(shadow_mask)
    shadow_layer.paste(shadow_img, (rx + 4, ry + 6), shadow_img)
    canvas = Image.alpha_composite(canvas, shadow_layer)
    canvas.alpha_composite(rot_ribbon, (rx, ry))

    draw = ImageDraw.Draw(canvas)
    logo = get_logo_trasparente_ufficiale(max_w=280, max_h=80)
    if logo:
        lw, lh = logo.size
        draw.rounded_rectangle([(30, 30), (30 + lw + 24, 30 + lh + 16)], radius=12, fill=(255, 255, 255, 235))
        canvas.alpha_composite(logo, (42, 38))
    else:
        draw.rounded_rectangle([(30, 30), (320, 85)], radius=12, fill=(255, 255, 255, 235))
        f_b = get_font(24, bold=True)
        draw.text((44, 45), "IMMOBILIARE GIANCANI", font=f_b, fill=ribbon_color)

    draw = ImageDraw.Draw(canvas)
    pad_left = 50
    curr_y = y_left + 75

    zona = str(media_info.get("zona", "Favara (AG)")).strip()
    loc_txt = f"{zona}: {titolo.title()}" if zona and zona.lower() not in titolo.lower() else titolo.title()
    f_loc = get_font(font_loc_size, bold=True, font_type="sans")
    draw.text((pad_left, curr_y), loc_txt[:45], font=f_loc, fill=(90, 95, 105, 255))
    curr_y += draw.textbbox((0, 0), loc_txt, font=f_loc)[3] + 12

    testo_f = str(media_info.get("testoF", "")).strip()
    if not testo_f:
        testo_f = "Quando la strategia è corretta, si ottiene il massimo realizzo economico per il cliente."
    
    f_head = get_font(font_head_size, bold=True, font_type="sans")
    head_lines = _wrap_text_lines(draw, testo_f, f_head, W - pad_left * 2)
    for hl in head_lines[:3]:
        draw.text((pad_left, curr_y), hl, font=f_head, fill=(24, 28, 36, 255))
        bb_h = draw.textbbox((0, 0), hl, font=f_head)
        curr_y += (bb_h[3] - bb_h[1]) + 8

    curr_y += 8
    badge_claim = str(media_info.get("claim", "+10% Il nostro metodo funziona!"))
    f_badge = get_font(font_badge_size, bold=True, font_type="sans")
    draw.text((pad_left, curr_y), badge_claim, font=f_badge, fill=ribbon_color)
    curr_y += draw.textbbox((0, 0), badge_claim, font=f_badge)[3] + 10

    f_cta = get_font(font_cta_size, bold=False, font_type="sans")
    cta_txt = "Vuoi sapere quanto vale la tua? Valutazione gratuita in 24h"
    draw.text((pad_left, curr_y), cta_txt, font=f_cta, fill=(80, 85, 95, 255))
    curr_y += draw.textbbox((0, 0), cta_txt, font=f_cta)[3] + 8

    f_sign = get_font(font_cta_size, bold=True, font_type="sans")
    sign_txt = "Immobiliare Giancani • Corso Vittorio Veneto 151, Favara • Tel. 320 166 7156"
    draw.text((pad_left, curr_y), sign_txt, font=f_sign, fill=ribbon_color)

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[GABETTI_DIAGONAL_1_1] Salvato: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🌟 STILE 11: CAM HERO BADGE (1080x1920 & 1080x1080) — NUOVA GRAFICA REFERENCE 1
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_cam_hero_badge_9_16(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_cam_hero_badge_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = get_clean_property_photo(media_info, (W, H)).convert("RGBA")

    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for y in range(300):
        v_draw.line([(0, y), (W, y)], fill=(0, 0, 0, int(150 * (1 - y/300.0))))
    for y in range(H - 340, H):
        v_draw.line([(0, y), (W, y)], fill=(0, 0, 0, int(170 * ((y - (H - 340))/340.0))))
    canvas.alpha_composite(vignette)

    draw = ImageDraw.Draw(canvas)

    # Tag Top Left
    draw.rounded_rectangle([40, 60, 360, 116], radius=12, fill=(15, 23, 42, 210), outline=(255, 255, 255, 120), width=1)
    font_top_tag = get_font(20, bold=True, font_type="sans")
    draw.text((60, 74), "ESCLUSIVA GIANCANI", font=font_top_tag, fill=(255, 255, 255, 255))

    # Logo Top Right
    logo_im = get_logo_trasparente_ufficiale(max_w=340, max_h=95)
    if logo_im:
        lw, lh = logo_im.size
        pill_w, pill_h = lw + 36, lh + 20
        pill_x = W - pill_w - 40
        pill_y = 50
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=16, fill=(255, 255, 255, 235), outline=palette.get("accent", (212, 168, 83, 255)), width=2)
        canvas.paste(logo_im, (pill_x + 18, pill_y + 10), mask=logo_im.split()[3])

    # Floating Hero Badge
    badge_w = 920
    badge_x = (W - badge_w) // 2
    badge_y = 1100

    ribbon_h = 76
    ribbon_col = palette.get("primary_mid", (30, 58, 138, 255))
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + ribbon_h], radius=8, fill=ribbon_col)
    font_ribbon = get_font(38, bold=True, font_type="sans")
    rb_txt = "NUOVO IMMOBILE"
    rb_w = font_ribbon.getbbox(rb_txt)[2] - font_ribbon.getbbox(rb_txt)[0]
    draw.text((badge_x + (badge_w - rb_w) // 2, badge_y + 16), rb_txt, font=font_ribbon, fill=(255, 255, 255, 255))

    box_h = 240
    box_y = badge_y + ribbon_h
    glass_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glass_overlay)
    dark_c = palette.get("primary_dark", (15, 23, 42, 255))
    accent_c = palette.get("accent", (212, 168, 83, 255))
    g_draw.rounded_rectangle([badge_x, box_y, badge_x + badge_w, box_y + box_h], radius=8, fill=(dark_c[0], dark_c[1], dark_c[2], 215), outline=accent_c, width=2)
    canvas.alpha_composite(glass_overlay)
    draw = ImageDraw.Draw(canvas)

    titolo = media_info.get("titolo", "Villa con Parco e Vista Panoramica")
    zona = media_info.get("zona", "Favara (AG)")
    prezzo = media_info.get("prezzo", "€ 160.000")
    mq_val = formatta_metri_quadri(media_info.get("mq", "140"))

    font_tit = get_font(42, bold=True, font_type="sans")
    draw.text((badge_x + 45, box_y + 26), titolo[:38], font=font_tit, fill=(255, 255, 255, 255))

    font_zona = get_font(34, bold=False, font_type="sans")
    draw.text((badge_x + 45, box_y + 90), f"a {zona}", font=font_zona, fill=(240, 245, 255, 255))

    font_price_mq = get_font(32, bold=True, font_type="sans")
    warm_acc = palette.get("accent_warm", palette.get("accent", (245, 158, 11, 255)))
    draw.text((badge_x + 45, box_y + 158), f"{prezzo}   •   {mq_val}", font=font_price_mq, fill=warm_acc)

    # Footer Bar Contatti Giancani
    footer_y = H - 240
    footer_w = W - 80
    footer_x = 40
    draw.rounded_rectangle([footer_x, footer_y, footer_x + footer_w, footer_y + 160], radius=20, fill=(15, 23, 42, 235), outline=(255, 255, 255, 80), width=2)

    draw_phone_icon(draw, footer_x + 60, footer_y + 44, 28, accent_c)
    font_call = get_font(28, bold=True, font_type="sans")
    draw.text((footer_x + 95, footer_y + 28), "CONTATTACI: 320 166 7156", font=font_call, fill=accent_c)

    draw_pin_icon(draw, footer_x + 60, footer_y + 86, 26, (220, 38, 38, 255))
    font_addr = get_font(22, bold=False, font_type="sans")
    draw.text((footer_x + 95, footer_y + 74), "Sede Ufficiale: Corso Vittorio Veneto 151, Favara (AG)", font=font_addr, fill=(226, 232, 240, 255))

    font_sign = get_font(24, bold=True, font_type="serif")
    draw.text((footer_x + 50, footer_y + 115), "La tua prossima casa ti aspetta — Immobiliare Giancani", font=font_sign, fill=(255, 255, 255, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path

def crea_flyer_cam_hero_badge_1_1(media_info, palette=None, output_path=None):
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_cam_hero_badge_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = get_clean_property_photo(media_info, (W, H)).convert("RGBA")

    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for y in range(220):
        v_draw.line([(0, y), (W, y)], fill=(0, 0, 0, int(140 * (1 - y/220.0))))
    for y in range(H - 240, H):
        v_draw.line([(0, y), (W, y)], fill=(0, 0, 0, int(170 * ((y - (H - 240))/240.0))))
    canvas.alpha_composite(vignette)

    draw = ImageDraw.Draw(canvas)

    logo_im = get_logo_trasparente_ufficiale(max_w=280, max_h=80)
    if logo_im:
        lw, lh = logo_im.size
        pill_w, pill_h = lw + 30, lh + 16
        pill_x = W - pill_w - 30
        pill_y = 35
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=14, fill=(255, 255, 255, 235), outline=palette.get("accent", (212, 168, 83, 255)), width=2)
        canvas.paste(logo_im, (pill_x + 15, pill_y + 8), mask=logo_im.split()[3])

    draw.rounded_rectangle([30, 42, 330, 92], radius=10, fill=(15, 23, 42, 210), outline=(255, 255, 255, 120), width=1)
    font_top_tag = get_font(18, bold=True, font_type="sans")
    draw.text((48, 56), "ESCLUSIVA GIANCANI", font=font_top_tag, fill=(255, 255, 255, 255))

    badge_w = 900
    badge_x = (W - badge_w) // 2
    badge_y = 520

    ribbon_h = 66
    ribbon_col = palette.get("primary_mid", (30, 58, 138, 255))
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + ribbon_h], radius=8, fill=ribbon_col)
    font_ribbon = get_font(34, bold=True, font_type="sans")
    rb_txt = "NUOVO IMMOBILE"
    rb_w = font_ribbon.getbbox(rb_txt)[2] - font_ribbon.getbbox(rb_txt)[0]
    draw.text((badge_x + (badge_w - rb_w) // 2, badge_y + 14), rb_txt, font=font_ribbon, fill=(255, 255, 255, 255))

    box_h = 220
    box_y = badge_y + ribbon_h
    glass_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glass_overlay)
    dark_c = palette.get("primary_dark", (15, 23, 42, 255))
    accent_c = palette.get("accent", (212, 168, 83, 255))
    g_draw.rounded_rectangle([badge_x, box_y, badge_x + badge_w, box_y + box_h], radius=8, fill=(dark_c[0], dark_c[1], dark_c[2], 215), outline=accent_c, width=2)
    canvas.alpha_composite(glass_overlay)
    draw = ImageDraw.Draw(canvas)

    titolo = media_info.get("titolo", "Villa con Parco e Vista Panoramica")
    zona = media_info.get("zona", "Favara (AG)")
    prezzo = media_info.get("prezzo", "€ 160.000")
    mq_val = formatta_metri_quadri(media_info.get("mq", "140"))

    font_tit = get_font(38, bold=True, font_type="sans")
    draw.text((badge_x + 40, box_y + 24), titolo[:38], font=font_tit, fill=(255, 255, 255, 255))

    font_zona = get_font(30, bold=False, font_type="sans")
    draw.text((badge_x + 40, box_y + 82), f"a {zona}", font=font_zona, fill=(240, 245, 255, 255))

    font_price_mq = get_font(28, bold=True, font_type="sans")
    warm_acc = palette.get("accent_warm", palette.get("accent", (245, 158, 11, 255)))
    draw.text((badge_x + 40, box_y + 144), f"{prezzo}   •   {mq_val}", font=font_price_mq, fill=warm_acc)

    draw.rounded_rectangle([badge_x, H - 180, badge_x + badge_w, H - 40], radius=16, fill=(15, 23, 42, 235), outline=(255, 255, 255, 80), width=2)
    draw_phone_icon(draw, badge_x + 45, H - 146, 24, accent_c)
    font_call = get_font(24, bold=True, font_type="sans")
    draw.text((badge_x + 75, H - 160), "CONTATTACI: 320 166 7156", font=font_call, fill=accent_c)
    font_addr = get_font(20, bold=False, font_type="sans")
    draw.text((badge_x + 45, H - 110), "Corso Vittorio Veneto 151, Favara (AG) — Immobiliare Giancani", font=font_addr, fill=(226, 232, 240, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🌈 STILE 12: METROQUADRO GRADIENT (1080x1920 & 1080x1080) — NUOVA GRAFICA REFERENCE 2
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_metroquadro_gradient_9_16(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_metroquadro_gradient_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = get_clean_property_photo(media_info, (W, H)).convert("RGBA")

    grad_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(grad_layer)
    dark_c = palette.get("primary_dark", (10, 25, 47, 255))
    accent_c = palette.get("accent", (14, 165, 233, 255))
    grad_start_y = 520
    grad_end_y = 1180
    for y in range(grad_start_y, H):
        if y < grad_end_y:
            factor = (y - grad_start_y) / float(grad_end_y - grad_start_y)
            alpha = int(250 * (factor ** 1.35))
        else:
            alpha = 250
        g_draw.line([(0, y), (W, y)], fill=(dark_c[0], dark_c[1], dark_c[2], alpha))
    canvas.alpha_composite(grad_layer)

    draw = ImageDraw.Draw(canvas)

    # Logo Top Left
    logo_im = get_logo_trasparente_ufficiale(max_w=360, max_h=100)
    if logo_im:
        lw, lh = logo_im.size
        pill_w, pill_h = lw + 36, lh + 20
        pill_x = 40
        pill_y = 50
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=16, fill=(255, 255, 255, 235), outline=accent_c, width=2)
        canvas.paste(logo_im, (pill_x + 18, pill_y + 10), mask=logo_im.split()[3])

    # Badge Top Right
    draw.rounded_rectangle([W - 320, 60, W - 40, 116], radius=12, fill=(15, 23, 42, 210), outline=(255, 255, 255, 120), width=1)
    font_top = get_font(20, bold=True, font_type="sans")
    draw.text((W - 295, 74), "OPPORTUNITÀ TOP", font=font_top, fill=(255, 255, 255, 255))

    ind = media_info.get("indirizzo", "VIA RAFFAELLO").upper()
    zona = media_info.get("zona", "FAVARA (AG)").upper()
    prezzo = media_info.get("prezzo", "€ 160.000")
    mq_val = formatta_metri_quadri(media_info.get("mq", "120")).upper()
    piano = media_info.get("piano", "QUARTO PIANO").upper()
    bagni = str(media_info.get("bagni", "1"))
    camere = str(media_info.get("camere", "3"))

    curr_y = 860
    font_ind = get_font(46, bold=True, font_type="sans")
    bb_ind = font_ind.getbbox(ind)
    iw = bb_ind[2] - bb_ind[0]
    draw.text(((W - iw) // 2, curr_y), ind, font=font_ind, fill=(255, 255, 255, 255))
    curr_y += 62

    font_zona = get_font(34, bold=True, font_type="sans")
    zona_str = f"( {zona} )"
    bb_z = font_zona.getbbox(zona_str)
    zw = bb_z[2] - bb_z[0]
    draw.text(((W - zw) // 2, curr_y), zona_str, font=font_zona, fill=(255, 255, 255, 255))
    curr_y += 75

    font_price = get_font(72, bold=True, font_type="sans")
    bb_p = font_price.getbbox(prezzo)
    pw = bb_p[2] - bb_p[0]
    draw.text(((W - pw) // 2, curr_y), prezzo, font=font_price, fill=(255, 255, 255, 255))
    curr_y += 115

    # Icone Line-Art Bianche
    cx1 = 300
    cy1 = curr_y + 40
    draw_house_icon(draw, cx1, cy1, 74, (255, 255, 255, 255), width=3)
    font_icon_lbl = get_font(22, bold=True, font_type="sans")
    font_icon_sub = get_font(18, bold=True, font_type="sans")
    draw.text((cx1 + 55, cy1 - 20), mq_val, font=font_icon_lbl, fill=(255, 255, 255, 255))
    draw.text((cx1 + 55, cy1 + 8), piano, font=font_icon_sub, fill=(255, 255, 255, 220))

    cx2 = 740
    cy2 = curr_y + 40
    draw_bathtub_icon(draw, cx2, cy2, 74, (255, 255, 255, 255), width=3)
    font_num = get_font(44, bold=True, font_type="sans")
    draw.text((cx2 + 65, cy2 - 25), bagni, font=font_num, fill=(255, 255, 255, 255))

    curr_y += 130

    ix_bed = 210
    iy_bed = curr_y + 40
    draw_bed_icon(draw, ix_bed, iy_bed, 70, (255, 255, 255, 255), width=3)
    draw.text((ix_bed + 55, iy_bed - 24), camere, font=font_num, fill=(255, 255, 255, 255))

    ix_gar = 520
    iy_gar = curr_y + 40
    draw_garage_icon(draw, ix_gar, iy_gar, 72, (255, 255, 255, 255), width=3)
    draw.text((ix_gar + 55, iy_gar - 18), "BOX AUTO", font=font_icon_lbl, fill=(255, 255, 255, 255))
    draw.text((ix_gar + 55, iy_gar + 8), "24 METRI QUADRI", font=font_icon_sub, fill=(255, 255, 255, 220))

    ix_asc = 860
    iy_asc = curr_y + 40
    draw_elevator_icon(draw, ix_asc, iy_asc, 68, (255, 255, 255, 255), width=3)
    draw.text((ix_asc - 52, iy_asc + 44), "ASCENSORE", font=get_font(16, bold=True, font_type="sans"), fill=(255, 255, 255, 255))

    # Card Inferiore Bianca
    card_h = 160
    card_y = H - card_h - 40
    draw.rounded_rectangle([40, card_y, W - 40, card_y + card_h], radius=18, fill=(255, 255, 255, 245), outline=accent_c, width=2)

    font_card_head = get_font(26, bold=True, font_type="sans")
    draw.text((65, card_y + 24), "Immobiliare Giancani — Casa in vendita • Contattaci Subito", font=font_card_head, fill=(15, 23, 42, 255))

    font_card_sub = get_font(22, bold=False, font_type="sans")
    draw.text((65, card_y + 68), "Corso Vittorio Veneto 151, Favara • Tel. 320 166 7156", font=font_card_sub, fill=(51, 65, 85, 255))

    font_card_sign = get_font(20, bold=True, font_type="serif")
    mid_c = palette.get("primary_mid", (30, 58, 138, 255))
    draw.text((65, card_y + 110), "Esclusiva di vendita con assistenza completa — Immobiliare Giancani", font=font_card_sign, fill=mid_c)

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path

def crea_flyer_metroquadro_gradient_1_1(media_info, palette=None, output_path=None):
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_metroquadro_gradient_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = get_clean_property_photo(media_info, (W, H)).convert("RGBA")

    grad_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(grad_layer)
    dark_c = palette.get("primary_dark", (10, 25, 47, 255))
    accent_c = palette.get("accent", (14, 165, 233, 255))
    grad_start_y = 220
    grad_end_y = 650
    for y in range(grad_start_y, H):
        if y < grad_end_y:
            factor = (y - grad_start_y) / float(grad_end_y - grad_start_y)
            alpha = int(250 * (factor ** 1.35))
        else:
            alpha = 250
        g_draw.line([(0, y), (W, y)], fill=(dark_c[0], dark_c[1], dark_c[2], alpha))
    canvas.alpha_composite(grad_layer)

    draw = ImageDraw.Draw(canvas)

    logo_im = get_logo_trasparente_ufficiale(max_w=280, max_h=80)
    if logo_im:
        lw, lh = logo_im.size
        pill_w, pill_h = lw + 30, lh + 16
        pill_x = 35
        pill_y = 35
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=14, fill=(255, 255, 255, 235), outline=accent_c, width=2)
        canvas.paste(logo_im, (pill_x + 15, pill_y + 8), mask=logo_im.split()[3])

    ind = media_info.get("indirizzo", "VIA RAFFAELLO").upper()
    zona = media_info.get("zona", "FAVARA (AG)").upper()
    prezzo = media_info.get("prezzo", "€ 160.000")
    mq_val = formatta_metri_quadri(media_info.get("mq", "120")).upper()
    piano = media_info.get("piano", "QUARTO PIANO").upper()
    bagni = str(media_info.get("bagni", "1"))
    camere = str(media_info.get("camere", "3"))

    curr_y = 440
    font_ind = get_font(38, bold=True, font_type="sans")
    bb_ind = font_ind.getbbox(ind)
    iw = bb_ind[2] - bb_ind[0]
    draw.text(((W - iw) // 2, curr_y), ind, font=font_ind, fill=(255, 255, 255, 255))
    curr_y += 48

    font_zona = get_font(28, bold=True, font_type="sans")
    zona_str = f"( {zona} )"
    bb_z = font_zona.getbbox(zona_str)
    zw = bb_z[2] - bb_z[0]
    draw.text(((W - zw) // 2, curr_y), zona_str, font=font_zona, fill=(255, 255, 255, 255))
    curr_y += 58

    font_price = get_font(60, bold=True, font_type="sans")
    bb_p = font_price.getbbox(prezzo)
    pw = bb_p[2] - bb_p[0]
    draw.text(((W - pw) // 2, curr_y), prezzo, font=font_price, fill=(255, 255, 255, 255))
    curr_y += 88

    cx1 = 160
    cy1 = curr_y + 35
    draw_house_icon(draw, cx1, cy1, 64, (255, 255, 255, 255), width=3)
    font_icon_lbl = get_font(20, bold=True, font_type="sans")
    draw.text((cx1 + 45, cy1 - 18), mq_val, font=font_icon_lbl, fill=(255, 255, 255, 255))
    draw.text((cx1 + 45, cy1 + 6), piano, font=get_font(16, bold=True, font_type="sans"), fill=(255, 255, 255, 220))

    cx2 = 540
    cy2 = curr_y + 35
    draw_bathtub_icon(draw, cx2, cy2, 64, (255, 255, 255, 255), width=3)
    font_num = get_font(38, bold=True, font_type="sans")
    draw.text((cx2 + 55, cy2 - 20), bagni, font=font_num, fill=(255, 255, 255, 255))

    cx3 = 780
    cy3 = curr_y + 35
    draw_bed_icon(draw, cx3, cy3, 64, (255, 255, 255, 255), width=3)
    draw.text((cx3 + 55, cy3 - 20), camere, font=font_num, fill=(255, 255, 255, 255))

    card_h = 135
    card_y = H - card_h - 30
    draw.rounded_rectangle([35, card_y, W - 35, card_y + card_h], radius=16, fill=(255, 255, 255, 245), outline=accent_c, width=2)
    font_card_head = get_font(24, bold=True, font_type="sans")
    draw.text((60, card_y + 20), "Immobiliare Giancani — Casa in vendita • Tel. 320 166 7156", font=font_card_head, fill=(15, 23, 42, 255))
    font_card_sub = get_font(19, bold=False, font_type="sans")
    draw.text((60, card_y + 58), "Corso Vittorio Veneto 151, Favara (AG) — Assistenza notarile e tecnica", font=font_card_sub, fill=(51, 65, 85, 255))
    font_card_sign = get_font(18, bold=True, font_type="serif")
    mid_c = palette.get("primary_mid", (30, 58, 138, 255))
    draw.text((60, card_y + 92), "La tua prossima casa ti aspetta — Immobiliare Giancani", font=font_card_sign, fill=mid_c)

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path




# ═══════════════════════════════════════════════════════════════════════════════
# 🌊 STILE 14: C&B IMMOBILIARE CURVED WAVE (1080x1920 & 1080x1080)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_cb_curved_wave_9_16(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_cb_curved_wave_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    photo = get_clean_property_photo(media_info, (W, H))
    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    # 1. Onda superiore gialla in alto a destra
    wave_color = palette.get("primary_dark", (245, 190, 11, 255))
    top_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(top_layer)
    top_split_x = int(W * 0.40)
    b_draw.polygon([(top_split_x, 0), (W, 0), (W, int(H * 0.35)), (int(W * 0.56), 0)], fill=wave_color)
    canvas.paste(top_layer, (0, 0), top_layer)

    # 2. Taglio ad arco per la foto dell'immobile
    y_start_curve = int(H * 0.28)
    curve_points = []
    for y in range(y_start_curve, H + 1):
        progress = (y - y_start_curve) / float(H - y_start_curve)
        if progress < 0.35:
            x = int(W - (W - 360) * ((progress / 0.35)**0.75))
        elif progress < 0.75:
            p2 = (progress - 0.35) / 0.40
            x = int(360 + 35 * math.sin(p2 * math.pi))
        else:
            p3 = (progress - 0.75) / 0.25
            x = int(360 - 40 * p3)
        curve_points.append((max(0, x), y))

    mask = Image.new("L", (W, H), 0)
    m_draw = ImageDraw.Draw(mask)
    poly_photo = [(W, y_start_curve)] + curve_points + [(W, H)]
    m_draw.polygon(poly_photo, fill=255)

    fw, fh = photo.size
    scale = max(W / fw, (H - y_start_curve) / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    p_res = photo.resize((nw, nh), Image.LANCZOS)
    p_crop = p_res.crop(((nw - W) // 2, 0, (nw - W) // 2 + W, H))
    canvas.paste(p_crop, (0, 0), mask)

    # Campo giallo in basso a sinistra coordinato
    bottom_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bb_draw = ImageDraw.Draw(bottom_layer)
    bb_points = [(0, y_start_curve)] + curve_points + [(0, H)]
    bb_draw.polygon(bb_points, fill=wave_color)
    canvas.paste(bottom_layer, (0, 0), bottom_layer)

    draw_line = ImageDraw.Draw(canvas)
    for i in range(len(curve_points) - 1):
        draw_line.line([curve_points[i], curve_points[i+1]], fill=(255, 255, 255, 255), width=8)

    draw = ImageDraw.Draw(canvas)

    # 3. Logo in alto a sinistra
    logo = get_logo_trasparente_ufficiale(max_w=340, max_h=110)
    if logo:
        canvas.paste(logo, (50, 55), logo.split()[3])
    else:
        f_b = get_font(32, bold=True, font_type="sans")
        draw.text((60, 65), "IMMOBILIARE GIANCANI", font=f_b, fill=(18, 24, 38, 255))

    # 4. Pillola Bianca Orizzontale Fluttuante di Stato
    pill_w = int(W * 0.72)
    pill_h = 175
    pill_x = (W - pill_w) // 2
    pill_y = int(H * 0.16)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rounded_rectangle([pill_x + 8, pill_y + 12, pill_x + pill_w + 8, pill_y + pill_h + 12], radius=42, fill=(0, 0, 0, 48))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    canvas = Image.alpha_composite(canvas, shadow)
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=40, fill=(255, 255, 255, 255), outline=(225, 232, 245, 255), width=3)

    circle_r = 52
    cx = pill_x + 105
    cy = pill_y + pill_h // 2
    draw.ellipse([cx - circle_r, cy - circle_r, cx + circle_r, cy + circle_r], fill=wave_color)
    draw_vector_check(draw, cx, cy, 54, color=(255, 255, 255, 255), width=8)

    stato_txt = str(media_info.get("stato", "IN VENDITA")).upper()
    font_stato = get_font(68, bold=True, font_type="sans")
    draw.text((cx + 80, cy - 42), stato_txt, font=font_stato, fill=(12, 35, 95, 255))

    # 5. Badge Localizzazione in basso
    zona_txt = f"{media_info.get('zona', 'Favara Centro')}"
    font_loc = get_font(30, bold=True, font_type="sans")
    loc_x, loc_y = 35, H - 190

    draw.line([(loc_x, loc_y - 20), (loc_x + 220, loc_y - 20)], fill=(255, 255, 255, 210), width=4)
    draw_pin_icon(draw, loc_x + 22, loc_y + 16, 36, color=(255, 255, 255, 255))
    draw.text((loc_x + 52, loc_y), zona_txt, font=font_loc, fill=(255, 255, 255, 255))
    draw.text((loc_x + 52, loc_y + 45), "Immobiliare Giancani", font=get_font(21, bold=True, font_type="sans"), fill=(20, 20, 20, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


def crea_flyer_cb_curved_wave_1_1(media_info, palette=None, output_path=None):
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_cb_curved_wave_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    photo = get_clean_property_photo(media_info, (W, H))
    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    wave_color = palette.get("primary_dark", (245, 190, 11, 255))
    top_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(top_layer)
    b_draw.polygon([(int(W * 0.44), 0), (W, 0), (W, int(H * 0.38)), (int(W * 0.58), 0)], fill=wave_color)
    canvas.paste(top_layer, (0, 0), top_layer)

    y_start_curve = int(H * 0.32)
    curve_points = []
    for y in range(y_start_curve, H + 1):
        progress = (y - y_start_curve) / float(H - y_start_curve)
        if progress < 0.35:
            x = int(W - (W - 320) * ((progress / 0.35)**0.75))
        elif progress < 0.75:
            p2 = (progress - 0.35) / 0.40
            x = int(320 + 30 * math.sin(p2 * math.pi))
        else:
            p3 = (progress - 0.75) / 0.25
            x = int(320 - 30 * p3)
        curve_points.append((max(0, x), y))

    mask = Image.new("L", (W, H), 0)
    m_draw = ImageDraw.Draw(mask)
    poly_photo = [(W, y_start_curve)] + curve_points + [(W, H)]
    m_draw.polygon(poly_photo, fill=255)

    fw, fh = photo.size
    scale = max(W / fw, (H - y_start_curve) / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    p_res = photo.resize((nw, nh), Image.LANCZOS)
    p_crop = p_res.crop(((nw - W) // 2, 0, (nw - W) // 2 + W, H))
    canvas.paste(p_crop, (0, 0), mask)

    bottom_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bb_draw = ImageDraw.Draw(bottom_layer)
    bb_points = [(0, y_start_curve)] + curve_points + [(0, H)]
    bb_draw.polygon(bb_points, fill=wave_color)
    canvas.paste(bottom_layer, (0, 0), bottom_layer)

    draw_line = ImageDraw.Draw(canvas)
    for i in range(len(curve_points) - 1):
        draw_line.line([curve_points[i], curve_points[i+1]], fill=(255, 255, 255, 255), width=7)

    draw = ImageDraw.Draw(canvas)

    logo = get_logo_trasparente_ufficiale(max_w=290, max_h=90)
    if logo:
        canvas.paste(logo, (40, 40), logo.split()[3])

    pill_w, pill_h = int(W * 0.65), 135
    pill_x = (W - pill_w) // 2
    pill_y = int(H * 0.16)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rounded_rectangle([pill_x + 6, pill_y + 8, pill_x + pill_w + 6, pill_y + pill_h + 8], radius=32, fill=(0, 0, 0, 45))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    canvas = Image.alpha_composite(canvas, shadow)
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=30, fill=(255, 255, 255, 255), outline=(225, 232, 245, 255), width=3)
    circle_r = 42
    cx = pill_x + 80
    cy = pill_y + pill_h // 2
    draw.ellipse([cx - circle_r, cy - circle_r, cx + circle_r, cy + circle_r], fill=(16, 75, 195, 255))
    draw_vector_check(draw, cx, cy, 44, color=(255, 255, 255, 255), width=6)

    stato_txt = str(media_info.get("stato", "IN VENDITA")).upper()
    font_stato = get_font(52, bold=True, font_type="sans")
    draw.text((cx + 60, cy - 32), stato_txt, font=font_stato, fill=(12, 35, 95, 255))

    zona_txt = f"{media_info.get('zona', 'Favara Centro')}"
    loc_x, loc_y = 30, H - 145
    draw.line([(loc_x, loc_y - 15), (loc_x + 190, loc_y - 15)], fill=(255, 255, 255, 210), width=3)
    draw_pin_icon(draw, loc_x + 18, loc_y + 12, 30, color=(255, 255, 255, 255))
    draw.text((loc_x + 44, loc_y), zona_txt, font=get_font(25, bold=True, font_type="sans"), fill=(255, 255, 255, 255))
    draw.text((loc_x + 44, loc_y + 36), "Immobiliare Giancani", font=get_font(18, bold=True, font_type="sans"), fill=(215, 235, 255, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🏛️ STILE 15: PROFESSIONECASA SIDEBAR (1080x1920 & 1080x1080)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_professionecasa_sidebar_9_16(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_professionecasa_sidebar_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    photo = get_clean_property_photo(media_info, (W, H))
    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    sidebar_w = 280

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, sidebar_w, H], fill=(225, 29, 42, 255))

    fw, fh = photo.size
    rw = W - sidebar_w
    rh = H
    scale = max(rw / fw, rh / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    p_res = photo.resize((nw, nh), Image.LANCZOS)
    p_crop = p_res.crop(((nw - rw) // 2, 0, (nw - rw) // 2 + rw, rh))
    canvas.paste(p_crop.convert("RGBA"), (sidebar_w, 0))

    draw = ImageDraw.Draw(canvas)

    mq_val = str(formatta_metri_quadri(media_info.get("mq", "120"))).replace(" metri quadri", "").strip()
    bagni_val = str(media_info.get("bagni", "2"))
    vani_val = str(media_info.get("vani", media_info.get("camere", "5")))

    icons_data = [
        {"type": "sqm", "num": mq_val, "lbl": "METRI QUADRI"},
        {"type": "shower", "num": bagni_val, "lbl": "BAGNI"},
        {"type": "sofa", "num": vani_val, "lbl": "VANI"},
    ]
    font_num = get_font(38, bold=True, font_type="sans")
    font_lbl = get_font(19, bold=True, font_type="sans")

    y_start = 220
    step_y = 230
    for idx, it in enumerate(icons_data):
        curr_y = y_start + idx * step_y
        cx = sidebar_w // 2
        if it["type"] == "sqm":
            draw_vector_ruler_sqm(draw, cx, curr_y + 15, 60, color=(255, 255, 255, 255), width=3)
        elif it["type"] == "shower":
            draw_vector_shower(draw, cx, curr_y + 15, 60, color=(255, 255, 255, 255), width=3)
        elif it["type"] == "sofa":
            draw_vector_sofa(draw, cx, curr_y + 15, 60, color=(255, 255, 255, 255), width=3)

        bn = font_num.getbbox(it["num"])
        nw_b = bn[2] - bn[0]
        draw.text((cx - nw_b // 2, curr_y + 68), it["num"], font=font_num, fill=(255, 255, 255, 255))
        bl = font_lbl.getbbox(it["lbl"])
        lw_b = bl[2] - bl[0]
        draw.text((cx - lw_b // 2, curr_y + 118), it["lbl"], font=font_lbl, fill=(255, 255, 255, 255))
        draw.line([(35, curr_y + 185), (sidebar_w - 35, curr_y + 185)], fill=(255, 255, 255, 120), width=2)

    card_x = sidebar_w - 30
    card_y = 1030
    card_w = W - card_x - 30
    card_h = 750

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rectangle([card_x + 8, card_y + 10, card_x + card_w + 8, card_y + card_h + 10], fill=(0, 0, 0, 65))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    canvas = Image.alpha_composite(canvas, shadow)
    draw = ImageDraw.Draw(canvas)

    draw.rectangle([card_x, card_y, card_x + card_w, card_y + card_h], fill=(255, 255, 255, 255))

    chev_y = card_y + 40
    chev_poly = [(card_x - 35, chev_y + 30), (card_x, chev_y), (card_x, chev_y + 60)]
    draw.polygon(chev_poly, fill=(225, 29, 42, 255))

    tx = card_x + 40
    ty = card_y + 45

    tipologia_txt = str(media_info.get("tipologia", media_info.get("titolo", "APPARTAMENTO"))).upper()
    if len(tipologia_txt) > 38:
        tipologia_txt = tipologia_txt[:35] + "..."
    draw.text((tx, ty), tipologia_txt, font=get_font(23, bold=True, font_type="sans"), fill=(225, 29, 42, 255))
    ty += 48

    tit_txt = f"{media_info.get('zona', 'FAVARA')}, {media_info.get('indirizzo', '')}".strip().rstrip(',').upper()
    if not media_info.get('indirizzo'):
        tit_txt = f"{media_info.get('zona', 'FAVARA CENTRO')}".upper()
    draw.text((tx, ty), tit_txt, font=get_font(36, bold=True, font_type="sans"), fill=(15, 23, 42, 255))
    ty += 68

    draw.line([(tx, ty), (card_x + card_w - 40, ty)], fill=(226, 232, 240, 255), width=2)
    ty += 32

    # Testo descrittivo rigorosamente da Colonna F
    testo_col_f = str(media_info.get("testoF") or media_info.get("testo_col_f") or "Immobile selezionato e garantito da Immobiliare Giancani.")
    words = testo_col_f.split()
    bullets = []
    chunk = []
    for w in words:
        chunk.append(w)
        if len(" ".join(chunk)) > 36 or len(chunk) >= 5:
            bullets.append(" ".join(chunk).upper())
            chunk = []
            if len(bullets) >= 3:
                break
    if chunk and len(bullets) < 3:
        bullets.append(" ".join(chunk).upper())
    bullets.append("TUTELA COMPLETA — IMMOBILIARE GIANCANI")

    font_b = get_font(20, bold=True, font_type="sans")
    for b in bullets[:4]:
        draw_vector_check(draw, tx + 10, ty + 12, 22, color=(225, 29, 42, 255), width=3)
        draw.text((tx + 30, ty), b, font=font_b, fill=(51, 65, 85, 255))
        ty += 42

    ty += 15
    prezzo_txt = str(media_info.get("prezzo", "€ 149.000"))
    draw.text((tx, ty), prezzo_txt, font=get_font(56, bold=True, font_type="sans"), fill=(225, 29, 42, 255))

    logo = get_logo_trasparente_ufficiale(max_w=290, max_h=90)
    if logo:
        lw, lh = logo.size
        lx = card_x + card_w - lw - 40
        ly = card_y + card_h - lh - 40
        canvas.paste(logo, (lx, ly), logo.split()[3])

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


def crea_flyer_professionecasa_sidebar_1_1(media_info, palette=None, output_path=None):
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_professionecasa_sidebar_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    photo = get_clean_property_photo(media_info, (W, H))
    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    sidebar_w = 260

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, sidebar_w, H], fill=(225, 29, 42, 255))

    fw, fh = photo.size
    rw, rh = W - sidebar_w, H
    scale = max(rw / fw, rh / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    p_res = photo.resize((nw, nh), Image.LANCZOS)
    p_crop = p_res.crop(((nw - rw) // 2, 0, (nw - rw) // 2 + rw, rh))
    canvas.paste(p_crop.convert("RGBA"), (sidebar_w, 0))

    draw = ImageDraw.Draw(canvas)

    mq_val = str(formatta_metri_quadri(media_info.get("mq", "120"))).replace(" metri quadri", "").strip()
    bagni_val = str(media_info.get("bagni", "2"))
    vani_val = str(media_info.get("vani", media_info.get("camere", "5")))

    icons_data = [
        {"type": "sqm", "num": mq_val, "lbl": "METRI QUADRI"},
        {"type": "shower", "num": bagni_val, "lbl": "BAGNI"},
        {"type": "sofa", "num": vani_val, "lbl": "VANI"},
    ]
    y_start, step_y = 120, 180
    for idx, it in enumerate(icons_data):
        curr_y = y_start + idx * step_y
        cx = sidebar_w // 2
        if it["type"] == "sqm":
            draw_vector_ruler_sqm(draw, cx, curr_y + 10, 50, color=(255, 255, 255, 255), width=3)
        elif it["type"] == "shower":
            draw_vector_shower(draw, cx, curr_y + 10, 50, color=(255, 255, 255, 255), width=3)
        elif it["type"] == "sofa":
            draw_vector_sofa(draw, cx, curr_y + 10, 50, color=(255, 255, 255, 255), width=3)

        bn = get_font(32, bold=True, font_type="sans").getbbox(it["num"])
        nw_b = bn[2] - bn[0]
        draw.text((cx - nw_b // 2, curr_y + 52), it["num"], font=get_font(32, bold=True, font_type="sans"), fill=(255, 255, 255, 255))
        bl = get_font(16, bold=True, font_type="sans").getbbox(it["lbl"])
        lw_b = bl[2] - bl[0]
        draw.text((cx - lw_b // 2, curr_y + 92), it["lbl"], font=get_font(16, bold=True, font_type="sans"), fill=(255, 255, 255, 255))
        draw.line([(30, curr_y + 140), (sidebar_w - 30, curr_y + 140)], fill=(255, 255, 255, 120), width=2)

    card_x = sidebar_w - 25
    card_y = 520
    card_w = W - card_x - 25
    card_h = 520

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rectangle([card_x + 6, card_y + 8, card_x + card_w + 6, card_y + card_h + 8], fill=(0, 0, 0, 60))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    canvas = Image.alpha_composite(canvas, shadow)
    draw = ImageDraw.Draw(canvas)

    draw.rectangle([card_x, card_y, card_x + card_w, card_y + card_h], fill=(255, 255, 255, 255))

    chev_y = card_y + 35
    chev_poly = [(card_x - 30, chev_y + 25), (card_x, chev_y), (card_x, chev_y + 50)]
    draw.polygon(chev_poly, fill=(225, 29, 42, 255))

    tx = card_x + 35
    ty = card_y + 35

    tipologia_txt = str(media_info.get("tipologia", media_info.get("titolo", "SOLUZIONE INDIPENDENTE"))).upper()
    if len(tipologia_txt) > 34:
        tipologia_txt = tipologia_txt[:31] + "..."
    draw.text((tx, ty), tipologia_txt, font=get_font(20, bold=True, font_type="sans"), fill=(225, 29, 42, 255))
    ty += 38

    tit_txt = f"{media_info.get('zona', 'FAVARA')}, {media_info.get('indirizzo', '')}".strip().rstrip(',').upper()
    if not media_info.get('indirizzo'):
        tit_txt = f"{media_info.get('zona', 'FAVARA CENTRO')}".upper()
    draw.text((tx, ty), tit_txt, font=get_font(32, bold=True, font_type="sans"), fill=(15, 23, 42, 255))
    ty += 52

    draw.line([(tx, ty), (card_x + card_w - 35, ty)], fill=(226, 232, 240, 255), width=2)
    ty += 22

    bullets = [
        "PIANO TERRA CON AMPIA ZONA LIVING",
        "ZONA NOTTE CON CAMERE E TERRAZZO",
        "BOX AUTO E POSTO RISERVATO",
        "TUTELA COMPLETA — IMMOBILIARE GIANCANI"
    ]
    font_b = get_font(18, bold=True, font_type="sans")
    for b in bullets:
        draw_vector_check(draw, tx + 8, ty + 10, 18, color=(225, 29, 42, 255), width=3)
        draw.text((tx + 26, ty), b, font=font_b, fill=(51, 65, 85, 255))
        ty += 34

    ty += 10
    prezzo_txt = str(media_info.get("prezzo", "€ 149.000,00"))
    draw.text((tx, ty), prezzo_txt, font=get_font(46, bold=True, font_type="sans"), fill=(225, 29, 42, 255))

    logo = get_logo_trasparente_ufficiale(max_w=240, max_h=75)
    if logo:
        lw, lh = logo.size
        canvas.paste(logo, (card_x + card_w - lw - 30, card_y + card_h - lh - 30), logo.split()[3])

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🏡 STILE 13: TEMPOCASA MULTI-PHOTO (1080x1920 & 1080x1080) — NUOVA GRAFICA REFERENCE 3
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_tempocasa_multiphoto_9_16(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_tempocasa_multiphoto_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = Image.new("RGBA", (W, H), (252, 252, 253, 255))
    draw = ImageDraw.Draw(canvas)

    base_photo = get_clean_property_photo(media_info, (1200, 1200))
    bw, bh = base_photo.size

    col_w = 460
    col_x = 40
    start_y = 100
    gap = 25
    slot_h = 240

    crop_boxes = [
        (0, 0, bw, int(bh * 0.45)),
        (0, int(bh * 0.25), int(bw * 0.7), int(bh * 0.7)),
        (int(bw * 0.3), int(bh * 0.4), bw, bh),
        (0, int(bh * 0.55), bw, bh)
    ]

    pill_bg = palette.get("pill_bg", palette.get("primary_mid", (16, 128, 98, 255)))

    for i in range(4):
        slot_y = start_y + i * (slot_h + gap)
        cb = crop_boxes[i]
        part = base_photo.crop(cb).resize((col_w, slot_h), Image.LANCZOS)
        mask = Image.new("L", (col_w, slot_h), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.rounded_rectangle([0, 0, col_w, slot_h], radius=20, fill=255)
        draw.rounded_rectangle([col_x - 3, slot_y - 3, col_x + col_w + 3, slot_y + slot_h + 3], radius=23, fill=None, outline=pill_bg, width=3)
        canvas.paste(part, (col_x, slot_y), mask=mask)

    right_x = col_x + col_w + 45
    right_w = W - right_x - 40

    curr_ry = 130
    font_in = get_font(95, bold=True, font_type="sans")
    draw.text((right_x, curr_ry), "IN", font=font_in, fill=pill_bg)
    curr_ry += 95
    font_vendita = get_font(74, bold=True, font_type="sans")
    draw.text((right_x, curr_ry), "VENDITA", font=font_vendita, fill=pill_bg)
    curr_ry += 140

    locali = f"{media_info.get('camere', '3')} LOCALI"
    mq_val = formatta_metri_quadri(media_info.get('mq', '130')).upper()
    bagni = f"{media_info.get('bagni', '2')} BAGNI"

    font_spec = get_font(34, bold=True, font_type="sans")

    draw_house_icon(draw, right_x + 35, curr_ry + 20, 68, pill_bg, width=3)
    draw.text((right_x + 85, curr_ry + 4), locali, font=font_spec, fill=pill_bg)
    curr_ry += 105

    draw.rectangle([right_x + 8, curr_ry - 8, right_x + 62, curr_ry + 46], outline=pill_bg, width=3)
    draw.text((right_x + 18, curr_ry + 8), "m²", font=get_font(20, bold=True, font_type="sans"), fill=pill_bg)
    draw.text((right_x + 85, curr_ry + 4), mq_val, font=font_spec, fill=pill_bg)
    curr_ry += 105

    draw_bathtub_icon(draw, right_x + 35, curr_ry + 20, 68, pill_bg, width=3)
    draw.text((right_x + 85, curr_ry + 4), bagni, font=font_spec, fill=pill_bg)
    curr_ry += 140

    draw_pin_icon(draw, right_x + 20, curr_ry + 20, 48, (220, 38, 38, 255))
    ind_str = media_info.get("indirizzo", "Via Colombaia, 9, Favara")
    font_ind = get_font(26, bold=True, font_type="sans")
    dark_c = palette.get("primary_dark", (15, 23, 42, 255))
    draw.text((right_x + 60, curr_ry + 6), ind_str[:26], font=font_ind, fill=dark_c)
    curr_ry += 95

    prezzo = media_info.get("prezzo", "€ 275.000")
    pill_h = 110
    pill_w = right_w
    draw.rounded_rectangle([right_x, curr_ry, right_x + pill_w, curr_ry + pill_h], radius=32, fill=pill_bg)
    font_price = get_font(52, bold=True, font_type="sans")
    bb_pr = font_price.getbbox(prezzo)
    pr_w = bb_pr[2] - bb_pr[0]
    draw.text((right_x + (pill_w - pr_w) // 2, curr_ry + 24), prezzo, font=font_price, fill=(255, 255, 255, 255))

    footer_y = H - 360
    bar_h = 56
    draw.rectangle([0, footer_y, W, footer_y + bar_h], fill=pill_bg)
    font_c_lbl = get_font(28, bold=True, font_type="sans")
    draw.text((45, footer_y + 12), "CONTATTI", font=font_c_lbl, fill=(255, 255, 255, 255))
    draw_chevrons(draw, 220, footer_y + 16, 24, (255, 255, 255, 255), count=4)

    det_y = footer_y + bar_h + 30
    draw_phone_icon(draw, 60, det_y + 20, 32, pill_bg)
    font_tel = get_font(36, bold=True, font_type="sans")
    draw.text((95, det_y), "320 166 7156", font=font_tel, fill=(15, 23, 42, 255))

    draw_pin_icon(draw, 58, det_y + 70, 26, (220, 38, 38, 255))
    font_sede = get_font(24, bold=False, font_type="sans")
    draw.text((95, det_y + 58), "Corso Vittorio Veneto 151, Favara (AG)", font=font_sede, fill=(71, 85, 105, 255))

    font_sign = get_font(24, bold=True, font_type="serif")
    draw.text((45, det_y + 105), "— Immobiliare Giancani", font=font_sign, fill=pill_bg)

    logo_im = get_logo_trasparente_ufficiale(max_w=360, max_h=120)
    if logo_im:
        lw, lh = logo_im.size
        canvas.paste(logo_im, (W - lw - 45, det_y + 10), mask=logo_im.split()[3])

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path

def crea_flyer_tempocasa_multiphoto_1_1(media_info, palette=None, output_path=None):
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_tempocasa_multiphoto_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = Image.new("RGBA", (W, H), (252, 252, 253, 255))
    draw = ImageDraw.Draw(canvas)

    base_photo = get_clean_property_photo(media_info, (1000, 1000))
    bw, bh = base_photo.size

    col_w = 400
    col_x = 35
    start_y = 60
    gap = 20
    slot_h = 220

    crop_boxes = [
        (0, 0, bw, int(bh * 0.5)),
        (0, int(bh * 0.3), int(bw * 0.8), int(bh * 0.8)),
        (int(bw * 0.2), int(bh * 0.5), bw, bh)
    ]

    pill_bg = palette.get("pill_bg", palette.get("primary_mid", (16, 128, 98, 255)))

    for i in range(3):
        slot_y = start_y + i * (slot_h + gap)
        part = base_photo.crop(crop_boxes[i]).resize((col_w, slot_h), Image.LANCZOS)
        mask = Image.new("L", (col_w, slot_h), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.rounded_rectangle([0, 0, col_w, slot_h], radius=18, fill=255)
        draw.rounded_rectangle([col_x - 3, slot_y - 3, col_x + col_w + 3, slot_y + slot_h + 3], radius=21, fill=None, outline=pill_bg, width=3)
        canvas.paste(part, (col_x, slot_y), mask=mask)

    right_x = col_x + col_w + 40
    right_w = W - right_x - 35

    curr_ry = 65
    font_in = get_font(72, bold=True, font_type="sans")
    draw.text((right_x, curr_ry), "IN", font=font_in, fill=pill_bg)
    curr_ry += 70
    font_vendita = get_font(58, bold=True, font_type="sans")
    draw.text((right_x, curr_ry), "VENDITA", font=font_vendita, fill=pill_bg)
    curr_ry += 95

    locali = f"{media_info.get('camere', '3')} LOCALI"
    mq_val = formatta_metri_quadri(media_info.get('mq', '130')).upper()
    bagni = f"{media_info.get('bagni', '2')} BAGNI"

    font_spec = get_font(26, bold=True, font_type="sans")

    draw_house_icon(draw, right_x + 25, curr_ry + 15, 52, pill_bg, width=3)
    draw.text((right_x + 65, curr_ry + 2), locali, font=font_spec, fill=pill_bg)
    curr_ry += 68

    draw.rectangle([right_x + 6, curr_ry - 6, right_x + 46, curr_ry + 34], outline=pill_bg, width=3)
    draw.text((right_x + 14, curr_ry + 4), "m²", font=get_font(16, bold=True, font_type="sans"), fill=pill_bg)
    draw.text((right_x + 65, curr_ry + 2), mq_val, font=font_spec, fill=pill_bg)
    curr_ry += 68

    draw_bathtub_icon(draw, right_x + 25, curr_ry + 15, 52, pill_bg, width=3)
    draw.text((right_x + 65, curr_ry + 2), bagni, font=font_spec, fill=pill_bg)
    curr_ry += 80

    draw_pin_icon(draw, right_x + 15, curr_ry + 14, 38, (220, 38, 38, 255))
    ind_str = media_info.get("indirizzo", "Via Colombaia, 9, Favara")
    font_ind = get_font(22, bold=True, font_type="sans")
    dark_c = palette.get("primary_dark", (15, 23, 42, 255))
    draw.text((right_x + 45, curr_ry + 2), ind_str[:28], font=font_ind, fill=dark_c)
    curr_ry += 60

    prezzo = media_info.get("prezzo", "€ 275.000")
    pill_h = 85
    pill_w = right_w
    draw.rounded_rectangle([right_x, curr_ry, right_x + pill_w, curr_ry + pill_h], radius=24, fill=pill_bg)
    font_price = get_font(42, bold=True, font_type="sans")
    bb_pr = font_price.getbbox(prezzo)
    pr_w = bb_pr[2] - bb_pr[0]
    draw.text((right_x + (pill_w - pr_w) // 2, curr_ry + 18), prezzo, font=font_price, fill=(255, 255, 255, 255))

    footer_y = H - 230
    bar_h = 48
    draw.rectangle([0, footer_y, W, footer_y + bar_h], fill=pill_bg)
    font_c_lbl = get_font(24, bold=True, font_type="sans")
    draw.text((35, footer_y + 10), "CONTATTI", font=font_c_lbl, fill=(255, 255, 255, 255))
    draw_chevrons(draw, 180, footer_y + 13, 20, (255, 255, 255, 255), count=4)

    det_y = footer_y + bar_h + 20
    draw_phone_icon(draw, 50, det_y + 16, 26, pill_bg)
    font_tel = get_font(30, bold=True, font_type="sans")
    draw.text((75, det_y), "320 166 7156", font=font_tel, fill=(15, 23, 42, 255))

    draw_pin_icon(draw, 48, det_y + 55, 22, (220, 38, 38, 255))
    font_sede = get_font(20, bold=False, font_type="sans")
    draw.text((75, det_y + 44), "Corso Vittorio Veneto 151, Favara (AG)", font=font_sede, fill=(71, 85, 105, 255))

    font_sign = get_font(20, bold=True, font_type="serif")
    draw.text((35, det_y + 78), "— Immobiliare Giancani", font=font_sign, fill=pill_bg)

    logo_im = get_logo_trasparente_ufficiale(max_w=280, max_h=90)
    if logo_im:
        lw, lh = logo_im.size
        canvas.paste(logo_im, (W - lw - 35, det_y + 8), mask=logo_im.split()[3])

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 6. DISPATCHER GENERATORE UNIFICATO (13 stili + card diretta)
# ═══════════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════════
# 🌟 NUOVI 5 STILI GRAFICI UFFICIALI IMMOBILIARE GIANCANI (RICHIESTA UTENTE)
# ═══════════════════════════════════════════════════════════════════════════════

def _format_prezzo(p_raw):
    p_str = str(p_raw or "").strip()
    digits = "".join(c for c in p_str if c.isdigit())
    if digits:
        val = int(digits)
        return f"€ {val:,}".replace(",", ".")
    return p_str if p_str else "Trattativa Riservata"


def _estrai_foto_multiple(media_info, target_count=4):
    """Estrae fino a target_count foto dell'immobile, con fallback su crop intelligenti"""
    foto_list = []
    if isinstance(media_info.get("altreFoto"), list):
        foto_list.extend(media_info["altreFoto"])
    for k in ["fotoUrl", "mediaUrl", "foto_01", "foto_02", "foto_03", "foto_04"]:
        u = media_info.get(k)
        if u and u not in foto_list:
            foto_list.append(u)

    opened = []
    for src in foto_list:
        try:
            if isinstance(src, Image.Image):
                opened.append(src.convert("RGB"))
            elif str(src).startswith("http"):
                r = requests.get(src, timeout=10, verify=False)
                if r.status_code == 200:
                    opened.append(Image.open(io.BytesIO(r.content)).convert("RGB"))
            elif os.path.exists(str(src)):
                opened.append(Image.open(str(src)).convert("RGB"))
        except Exception:
            pass
        if len(opened) >= target_count:
            break

    if not opened:
        base = get_clean_property_photo(media_info, (1080, 1080))
        opened.append(base)

    # Se abbiamo meno foto di quante necessarie, creiamo crop intelligenti dalla foto principale
    while len(opened) < target_count:
        main = opened[0]
        mw, mh = main.size
        idx = len(opened)
        if idx == 1:
            # Crop centro-destra
            crop = main.crop((int(mw * 0.25), 0, mw, int(mh * 0.75)))
        elif idx == 2:
            # Crop centro-basso
            crop = main.crop((0, int(mh * 0.25), int(mw * 0.75), mh))
        else:
            # Crop centrale zoomato
            crop = main.crop((int(mw * 0.15), int(mh * 0.15), int(mw * 0.85), int(mh * 0.85)))
        opened.append(crop)

    return opened[:target_count]


# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 STILE 1: MALFATTI SIDEBAR 1975 (Fascia sinistra IN VENDITA & Dark Card)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_flyer_malfatti_sidebar_1_1(media_info, palette=None, output_path=None):
    """
    Stile 1 ispirato all'immagine 1 (media_1791469687584.jpg):
    - Formato Quadrato 1:1 (1080x1080)
    - Fascia laterale verticale sinistra (bordeaux / colore primario)
    - In alto a sinistra: Logo e indicazione prestigiosa
    - Testo verticale 'IN VENDITA' lungo la fascia
    - Foto dell'immobile a tutta altezza nella restante larghezza
    - Badge Rif. in alto a destra
    - Dark Card in basso a destra con Prezzo gigante bianco, Indirizzo e caratteristiche
    - Firma 'Immobiliare Giancani' in basso
    """
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_malfatti_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    sidebar_w = 150
    photo_w = W - sidebar_w
    bar_color = palette.get("primary_mid", (136, 19, 55, 255))  # Bordeaux / Brand color
    if bar_color[0] > 200 and bar_color[1] > 180: # Se giallo, usa accent per contrasto
        bar_color = (136, 19, 55, 255)

    canvas = Image.new("RGBA", (W, H), (20, 24, 30, 255))

    # 1. Foto immobile sulla destra
    foto = get_clean_property_photo(media_info, (photo_w, H))
    canvas.paste(foto, (sidebar_w, 0))

    # 2. Fascia laterale sinistra
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, 0), (sidebar_w, H)], fill=bar_color)

    # 2b. Logo o Monogramma in alto nella fascia sinistra
    logo = get_logo_trasparente_ufficiale(max_w=sidebar_w - 24, max_h=60)
    if logo:
        # Crea card bianca per contrasto se il logo ha colori scuri
        lw, lh = logo.size
        lx = (sidebar_w - lw) // 2
        ly = 30
        draw.rounded_rectangle([lx - 6, ly - 6, lx + lw + 6, ly + lh + 6], radius=8, fill=(255, 255, 255, 240))
        canvas.paste(logo, (lx, ly), logo)
    else:
        f_init = get_font(28, bold=True, font_type="sans")
        draw.text((sidebar_w // 2, 45), "IG", font=f_init, fill=(255, 255, 255, 255), anchor="mm")

    # Dicitura '1975' / Dal ...
    f_year = get_font(18, bold=True, font_type="sans")
    draw.text((sidebar_w // 2, 110), "GIANCANI", font=f_year, fill=(255, 255, 255, 230), anchor="mm")

    # 2c. Testo Verticale 'IN VENDITA' ruotato a 90 gradi
    txt_invendita = "IN  VENDITA"
    f_vert = get_font(34, bold=True, font_type="sans")
    # Disegna su immagine temporanea e ruota
    tb = draw.textbbox((0, 0), txt_invendita, font=f_vert)
    tw, th = tb[2] - tb[0] + 20, tb[3] - tb[1] + 10
    img_txt = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d_txt = ImageDraw.Draw(img_txt)
    d_txt.text((10, 5), txt_invendita, font=f_vert, fill=(255, 255, 255, 255))
    img_txt_rot = img_txt.rotate(90, expand=True)
    rx = (sidebar_w - img_txt_rot.width) // 2
    ry = H - img_txt_rot.height - 70
    canvas.paste(img_txt_rot, (rx, ry), img_txt_rot)

    # 3. Badge Rif. in alto a destra sulla foto
    codice_rif = str(media_info.get("codiceRif", "RIF. GIANCANI")).replace("_", " ").upper()
    if not codice_rif.startswith("RIF"):
        codice_rif = f"Rif. {codice_rif}"
    f_rif = get_font(22, bold=True, font_type="sans")
    rb = draw.textbbox((0, 0), codice_rif, font=f_rif)
    rw, rh = rb[2] - rb[0] + 32, rb[3] - rb[1] + 16
    rx_pos = W - rw - 24
    ry_pos = 24
    draw.rounded_rectangle([rx_pos, ry_pos, rx_pos + rw, ry_pos + rh], radius=10, fill=(24, 28, 36, 230))
    draw.text((rx_pos + 16, ry_pos + 8), codice_rif, font=f_rif, fill=(255, 255, 255, 255))

    # 4. Dark Card inferiore (occupa da sidebar_w a W)
    card_h = 250
    card_y = H - card_h
    # Sfondo scuro elegante
    draw.rectangle([(sidebar_w, card_y), (W, H)], fill=(20, 23, 28, 255))
    # Linea di stacco superiore
    draw.line([(sidebar_w, card_y), (W, card_y)], fill=(45, 52, 64, 255), width=2)

    # 4a. Prezzo Gigante Bianco
    prezzo_txt = _format_prezzo(media_info.get("prezzo"))
    f_prz = get_font(52, bold=True, font_type="sans")
    draw.text((sidebar_w + 40, card_y + 24), prezzo_txt, font=f_prz, fill=(255, 255, 255, 255))

    # 4b. Indirizzo e Comune
    titolo = str(media_info.get("titolo", "Favara")).strip().title()
    zona = str(media_info.get("zona", media_info.get("indirizzo", "Centro"))).strip()
    via_txt = f"{zona} — {titolo}" if zona and zona.lower() not in titolo.lower() else titolo
    if len(via_txt) > 42:
        via_txt = via_txt[:40] + "..."
    f_via = get_font(25, bold=False, font_type="sans")
    draw.text((sidebar_w + 42, card_y + 92), via_txt, font=f_via, fill=(203, 213, 225, 255))

    # 4c. Caratteristiche con barre divisorie bordeaux
    mq_txt = formatta_metri_quadri(media_info.get("mq", "90"))
    locali_txt = str(media_info.get("locali", "4")).strip() + " locali"
    bagni_txt = str(media_info.get("bagni", "2")).strip() + " bagni"

    f_spec = get_font(23, bold=True, font_type="sans")
    f_div = get_font(24, bold=True, font_type="sans")

    sx = sidebar_w + 42
    sy = card_y + 140

    draw.text((sx, sy), mq_txt, font=f_spec, fill=(255, 255, 255, 255))
    sx += draw.textbbox((0, 0), mq_txt, font=f_spec)[2] + 14

    draw.text((sx, sy - 2), "|", font=f_div, fill=bar_color)
    sx += 20

    draw.text((sx, sy), locali_txt, font=f_spec, fill=(255, 255, 255, 255))
    sx += draw.textbbox((0, 0), locali_txt, font=f_spec)[2] + 14

    draw.text((sx, sy - 2), "|", font=f_div, fill=bar_color)
    sx += 20

    draw.text((sx, sy), bagni_txt, font=f_spec, fill=(255, 255, 255, 255))

    # 4d. Firma 'Immobiliare Giancani' in basso a destra
    f_sign = get_font(20, bold=True, font_type="sans")
    draw.text((W - 36, H - 36), "Immobiliare Giancani", font=f_sign, fill=(225, 29, 72, 255), anchor="rb")

    canvas.convert("RGB").save(output_path, quality=95)
    return output_path


def crea_story_malfatti_sidebar_9_16(media_info, palette=None, output_path=None):
    """
    Versione 9:16 (1080x1920) dello Stile Malfatti Sidebar:
    - Foto a sviluppo verticale
    - Sidebar sinistra con logo e 'IN VENDITA'
    - Dark Card inferiore con prezzo, dettagli e testo narrativo da Colonna F
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_malfatti_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    sidebar_w = 160
    photo_w = W - sidebar_w
    bar_color = (136, 19, 55, 255)

    canvas = Image.new("RGBA", (W, H), (20, 24, 30, 255))

    # 1. Foto a tutto campo sulla destra
    foto = get_clean_property_photo(media_info, (photo_w, H))
    canvas.paste(foto, (sidebar_w, 0))

    # 2. Fascia laterale sinistra
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, 0), (sidebar_w, H)], fill=bar_color)

    # Logo in alto
    logo = get_logo_trasparente_ufficiale(max_w=sidebar_w - 20, max_h=65)
    if logo:
        lw, lh = logo.size
        lx = (sidebar_w - lw) // 2
        ly = 45
        draw.rounded_rectangle([lx - 6, ly - 6, lx + lw + 6, ly + lh + 6], radius=8, fill=(255, 255, 255, 240))
        canvas.paste(logo, (lx, ly), logo)

    # Testo verticale 'IN VENDITA' ruotato a 90 gradi
    txt_invendita = "IN   VENDITA"
    f_vert = get_font(42, bold=True, font_type="sans")
    tb = draw.textbbox((0, 0), txt_invendita, font=f_vert)
    tw, th = tb[2] - tb[0] + 20, tb[3] - tb[1] + 10
    img_txt = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d_txt = ImageDraw.Draw(img_txt)
    d_txt.text((10, 5), txt_invendita, font=f_vert, fill=(255, 255, 255, 255))
    img_txt_rot = img_txt.rotate(90, expand=True)
    rx = (sidebar_w - img_txt_rot.width) // 2
    ry = H - img_txt_rot.height - 120
    canvas.paste(img_txt_rot, (rx, ry), img_txt_rot)

    # Badge Rif in alto a destra
    codice_rif = str(media_info.get("codiceRif", "RIF. GIANCANI")).replace("_", " ").upper()
    if not codice_rif.startswith("RIF"):
        codice_rif = f"Rif. {codice_rif}"
    f_rif = get_font(24, bold=True, font_type="sans")
    rb = draw.textbbox((0, 0), codice_rif, font=f_rif)
    rw, rh = rb[2] - rb[0] + 34, rb[3] - rb[1] + 18
    draw.rounded_rectangle([W - rw - 30, 36, W - 30, 36 + rh], radius=12, fill=(24, 28, 36, 230))
    draw.text((W - rw - 13, 44), codice_rif, font=f_rif, fill=(255, 255, 255, 255))

    # Dark Card inferiore espansa (con testo Colonna F)
    card_h = 440
    card_y = H - card_h
    draw.rectangle([(sidebar_w, card_y), (W, H)], fill=(18, 22, 28, 255))
    draw.line([(sidebar_w, card_y), (W, card_y)], fill=(45, 52, 64, 255), width=2)

    # Prezzo Gigante
    prezzo_txt = _format_prezzo(media_info.get("prezzo"))
    f_prz = get_font(60, bold=True, font_type="sans")
    draw.text((sidebar_w + 40, card_y + 24), prezzo_txt, font=f_prz, fill=(255, 255, 255, 255))

    # Indirizzo
    titolo = str(media_info.get("titolo", "Favara")).strip().title()
    zona = str(media_info.get("zona", media_info.get("indirizzo", "Centro"))).strip()
    via_txt = f"{zona} — {titolo}" if zona and zona.lower() not in titolo.lower() else titolo
    f_via = get_font(28, bold=False, font_type="sans")
    draw.text((sidebar_w + 42, card_y + 98), via_txt, font=f_via, fill=(203, 213, 225, 255))

    # Caratteristiche
    mq_txt = formatta_metri_quadri(media_info.get("mq", "90"))
    locali_txt = str(media_info.get("locali", "4")).strip() + " locali"
    bagni_txt = str(media_info.get("bagni", "2")).strip() + " bagni"
    f_spec = get_font(25, bold=True, font_type="sans")
    sx = sidebar_w + 42
    sy = card_y + 144
    draw.text((sx, sy), mq_txt, font=f_spec, fill=(255, 255, 255, 255))
    sx += draw.textbbox((0, 0), mq_txt, font=f_spec)[2] + 14
    draw.text((sx, sy - 2), "|", font=f_spec, fill=bar_color)
    sx += 20
    draw.text((sx, sy), locali_txt, font=f_spec, fill=(255, 255, 255, 255))
    sx += draw.textbbox((0, 0), locali_txt, font=f_spec)[2] + 14
    draw.text((sx, sy - 2), "|", font=f_spec, fill=bar_color)
    sx += 20
    draw.text((sx, sy), bagni_txt, font=f_spec, fill=(255, 255, 255, 255))

    # Testo narrativo da Colonna F
    testo_f = str(media_info.get("testoF", "")).strip()
    if testo_f:
        draw_fitted_text(draw, testo_f, (sidebar_w + 42, card_y + 195, photo_w - 80, 165),
                         max_font_size=23, min_font_size=17, fill=(226, 232, 240, 255), line_spacing=6)

    # Firma
    f_sign = get_font(22, bold=True, font_type="sans")
    draw.text((W - 40, H - 36), "— Immobiliare Giancani", font=f_sign, fill=(225, 29, 72, 255), anchor="rb")

    canvas.convert("RGB").save(output_path, quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🏛️ STILE 2: SCHEDA CURVA ISTITUZIONALE / PRESTIGIO (Asta / Incarico Certificato)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_scheda_curva_9_16(media_info, palette=None, output_path=None):
    """
    Stile 2 ispirato all'immagine 2 (uploaded_media_0_1791469719854.jpg):
    - Layout Verticale 9:16 (1080x1920)
    - Foto immobile sullo sfondo
    - Overlay card a destra con curvatura morbida in alto a sinistra
    - Header con Logo e Titolo Istituzionale
    - Pill scura con icona casa: Tipologia Immobile
    - Sezione 2 con icona Location Pin: Comune e Indirizzo
    - Sezione 3 con icona Istituzione/Corte: Riferimento procedura/fascicolo
    - Prezzo e superficie in metri quadri
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_curva_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    # 1. Foto a tutto schermo con focus a sinistra
    foto = get_clean_property_photo(media_info, (W, H))
    canvas = foto.convert("RGBA")

    # 2. Overlay card sul lato destro (da x=490 a 1080, da y=200 a 1920)
    card_x = 490
    card_y = 200
    card_w = W - card_x
    card_h = H - card_y

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    # Creazione maschera con angolo superiore-sinistro arrotondato
    mask = Image.new("L", (card_w, card_h), 0)
    d_mask = ImageDraw.Draw(mask)
    d_mask.rounded_rectangle([(0, 0), (card_w + 100, card_h + 100)], radius=90, fill=255)

    # Sfondo card con gradiente rosso bordeaux profondo -> blu notte
    card_bg = Image.new("RGBA", (card_w, card_h), (115, 18, 36, 250))
    d_cbg = ImageDraw.Draw(card_bg)
    for y in range(card_h):
        ratio = y / float(card_h)
        r = int(115 * (1 - ratio) + 20 * ratio)
        g = int(18 * (1 - ratio) + 30 * ratio)
        b = int(36 * (1 - ratio) + 65 * ratio)
        d_cbg.line([(0, y), (card_w, y)], fill=(r, g, b, 250))

    canvas.paste(card_bg, (card_x, card_y), mask)

    draw = ImageDraw.Draw(canvas)

    # 3. Header della card
    # Logo Immobiliare Giancani in alto
    logo = get_logo_trasparente_ufficiale(max_w=220, max_h=65)
    if logo:
        canvas.paste(logo, (card_x + 35, card_y + 35), logo)

    # Divisore e dicitura Istituzionale
    draw.line([(card_x + 270, card_y + 40), (card_x + 270, card_y + 90)], fill=(255, 255, 255, 120), width=2)
    f_inst_title = get_font(18, bold=True, font_type="sans")
    f_inst_sub = get_font(14, bold=False, font_type="sans")
    draw.text((card_x + 285, card_y + 42), "IMMOBILIARE GIANCANI", font=f_inst_title, fill=(255, 255, 255, 255))
    draw.text((card_x + 285, card_y + 68), "Incarico Esclusivo Certificato", font=f_inst_sub, fill=(226, 232, 240, 220))

    # 4. Pill scura orizzontale con icona casetta: Tipologia Immobile
    pill_y = card_y + 140
    pill_w = card_w - 50
    pill_h = 130
    draw.rounded_rectangle([card_x - 30, pill_y, card_x + pill_w, pill_y + pill_h], radius=55, fill=(13, 40, 80, 255))

    # Icona Casa in cerchio bianco
    draw.ellipse([card_x - 10, pill_y + 15, card_x + 90, pill_y + 115], fill=(255, 255, 255, 255))
    draw_house_icon(draw, card_x + 40, pill_y + 65, size=46, color=(13, 40, 80, 255), width=4)

    tipologia = str(media_info.get("tipologia", "Abitazione Di Tipo Civile")).title()
    f_tipo = get_font(30, bold=True, font_type="sans")
    draw.text((card_x + 115, pill_y + 45), tipologia, font=f_tipo, fill=(255, 255, 255, 255))

    # 5. Sezione Indirizzo / Comune con icona Location Pin
    sec2_y = pill_y + 190
    draw.ellipse([card_x + 15, sec2_y + 10, card_x + 95, sec2_y + 90], fill=(13, 40, 80, 255))
    draw_pin_icon(draw, card_x + 55, sec2_y + 50, size=42, color=(255, 255, 255, 255))

    zona = str(media_info.get("zona", "Favara (AG)")).strip()
    f_loc_bold = get_font(34, bold=True, font_type="sans")
    draw.text((card_x + 120, sec2_y + 10), zona, font=f_loc_bold, fill=(255, 255, 255, 255))

    indirizzo = str(media_info.get("indirizzo", media_info.get("titolo", "Corso Vittorio Veneto"))).strip()
    f_loc_sub = get_font(23, bold=False, font_type="sans")
    draw.text((card_x + 120, sec2_y + 60), indirizzo[:32], font=f_loc_sub, fill=(226, 232, 240, 230))

    # 6. Sezione Procedura / Codice Rif con icona Tempio
    sec3_y = sec2_y + 150
    draw.ellipse([card_x + 15, sec3_y + 10, card_x + 95, sec3_y + 90], fill=(13, 40, 80, 255))
    # Tempio / Istituzione
    cx_t, cy_t = card_x + 55, sec3_y + 50
    draw.polygon([(cx_t - 20, cy_t - 10), (cx_t + 20, cy_t - 10), (cx_t, cy_t - 26)], fill=(255, 255, 255, 255))
    draw.line([(cx_t - 18, cy_t - 8), (cx_t + 18, cy_t - 8)], fill=(255, 255, 255, 255), width=3)
    for col_x in [cx_t - 14, cx_t - 5, cx_t + 5, cx_t + 14]:
        draw.line([(col_x, cy_t - 6), (col_x, cy_t + 14)], fill=(255, 255, 255, 255), width=3)
    draw.line([(cx_t - 20, cy_t + 16), (cx_t + 20, cy_t + 16)], fill=(255, 255, 255, 255), width=4)

    f_rif_title = get_font(32, bold=True, font_type="sans")
    draw.text((card_x + 120, sec3_y + 12), "Rif. Ufficiale", font=f_rif_title, fill=(255, 255, 255, 255))
    cod_rif = str(media_info.get("codiceRif", "Pratica GIANCANI #2026")).replace("_", " ").upper()
    f_rif_sub = get_font(24, bold=False, font_type="sans")
    draw.text((card_x + 120, sec3_y + 62), cod_rif, font=f_rif_sub, fill=(226, 232, 240, 230))

    # 7. Box Prezzo & Metri Quadri in risalto
    box_prz_y = sec3_y + 160
    draw.rounded_rectangle([card_x + 20, box_prz_y, W - 30, box_prz_y + 140], radius=16, fill=(15, 23, 42, 220), outline=(245, 190, 11, 200), width=2)
    f_prz_lbl = get_font(18, bold=True, font_type="sans")
    draw.text((card_x + 40, box_prz_y + 18), "PREZZO RICHIESTO:", font=f_prz_lbl, fill=(245, 190, 11, 255))

    prezzo_txt = _format_prezzo(media_info.get("prezzo"))
    f_prz_val = get_font(44, bold=True, font_type="sans")
    draw.text((card_x + 40, box_prz_y + 45), prezzo_txt, font=f_prz_val, fill=(255, 255, 255, 255))

    mq_txt = formatta_metri_quadri(media_info.get("mq", "120"))
    f_mq_val = get_font(22, bold=True, font_type="sans")
    draw.text((card_x + 40, box_prz_y + 98), f"📐 Superficie: {mq_txt}", font=f_mq_val, fill=(56, 189, 248, 255))

    # 8. Testo narrativo da Colonna F
    testo_f = str(media_info.get("testoF", "")).strip()
    if testo_f:
        draw_fitted_text(draw, testo_f, (card_x + 25, box_prz_y + 165, card_w - 55, 280),
                         max_font_size=23, min_font_size=16, fill=(241, 245, 249, 255), line_spacing=6)

    # Footer
    f_ft = get_font(22, bold=True, font_type="sans")
    draw.text((W - 35, H - 35), "— Immobiliare Giancani", font=f_ft, fill=(255, 255, 255, 230), anchor="rb")

    canvas.convert("RGB").save(output_path, quality=95)
    return output_path


def crea_flyer_scheda_curva_1_1(media_info, palette=None, output_path=None):
    """Versione 1:1 (1080x1080) dello Stile Scheda Curva Istituzionale"""
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_curva_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    foto = get_clean_property_photo(media_info, (W, H))
    canvas = foto.convert("RGBA")

    card_x = 440
    card_y = 60
    card_w = W - card_x
    card_h = H - card_y

    mask = Image.new("L", (card_w, card_h), 0)
    d_mask = ImageDraw.Draw(mask)
    d_mask.rounded_rectangle([(0, 0), (card_w + 100, card_h + 100)], radius=70, fill=255)

    card_bg = Image.new("RGBA", (card_w, card_h), (115, 18, 36, 250))
    d_cbg = ImageDraw.Draw(card_bg)
    for y in range(card_h):
        ratio = y / float(card_h)
        r = int(115 * (1 - ratio) + 20 * ratio)
        g = int(18 * (1 - ratio) + 30 * ratio)
        b = int(36 * (1 - ratio) + 65 * ratio)
        d_cbg.line([(0, y), (card_w, y)], fill=(r, g, b, 250))

    canvas.paste(card_bg, (card_x, card_y), mask)
    draw = ImageDraw.Draw(canvas)

    # Logo
    logo = get_logo_trasparente_ufficiale(max_w=200, max_h=55)
    if logo:
        canvas.paste(logo, (card_x + 30, card_y + 25), logo)

    # Pill Tipologia
    pill_y = card_y + 95
    pill_w = card_w - 40
    draw.rounded_rectangle([card_x - 20, pill_y, card_x + pill_w, pill_y + 90], radius=45, fill=(13, 40, 80, 255))
    draw.ellipse([card_x - 5, pill_y + 10, card_x + 65, pill_y + 80], fill=(255, 255, 255, 255))
    draw_house_icon(draw, card_x + 30, pill_y + 45, size=34, color=(13, 40, 80, 255), width=3)
    tipologia = str(media_info.get("tipologia", "Abitazione Civile")).title()
    f_tipo = get_font(25, bold=True, font_type="sans")
    draw.text((card_x + 85, pill_y + 30), tipologia, font=f_tipo, fill=(255, 255, 255, 255))

    # Indirizzo
    sec2_y = pill_y + 115
    draw.ellipse([card_x + 15, sec2_y + 5, card_x + 75, sec2_y + 65], fill=(13, 40, 80, 255))
    draw_pin_icon(draw, card_x + 45, sec2_y + 35, size=32, color=(255, 255, 255, 255))
    zona = str(media_info.get("zona", "Favara (AG)")).strip()
    f_loc = get_font(28, bold=True, font_type="sans")
    draw.text((card_x + 95, sec2_y + 8), zona, font=f_loc, fill=(255, 255, 255, 255))
    indirizzo = str(media_info.get("indirizzo", media_info.get("titolo", "Centro"))).strip()
    f_sub = get_font(20, bold=False, font_type="sans")
    draw.text((card_x + 95, sec2_y + 44), indirizzo[:28], font=f_sub, fill=(226, 232, 240, 230))

    # Box Prezzo
    box_prz_y = sec2_y + 95
    draw.rounded_rectangle([card_x + 20, box_prz_y, W - 25, box_prz_y + 110], radius=14, fill=(15, 23, 42, 220), outline=(245, 190, 11, 200), width=2)
    prezzo_txt = _format_prezzo(media_info.get("prezzo"))
    f_prz = get_font(38, bold=True, font_type="sans")
    draw.text((card_x + 35, box_prz_y + 16), prezzo_txt, font=f_prz, fill=(255, 255, 255, 255))
    mq_txt = formatta_metri_quadri(media_info.get("mq", "120"))
    f_mq = get_font(20, bold=True, font_type="sans")
    draw.text((card_x + 35, box_prz_y + 68), f"📐 Superficie: {mq_txt}", font=f_mq, fill=(56, 189, 248, 255))

    # Testo narrativo Colonna F
    testo_f = str(media_info.get("testoF", "")).strip()
    if testo_f:
        draw_fitted_text(draw, testo_f, (card_x + 20, box_prz_y + 130, card_w - 45, 430),
                         max_font_size=21, min_font_size=15, fill=(241, 245, 249, 255), line_spacing=6)

    # Firma
    f_ft = get_font(20, bold=True, font_type="sans")
    draw.text((W - 30, H - 28), "— Immobiliare Giancani", font=f_ft, fill=(255, 255, 255, 230), anchor="rb")

    canvas.convert("RGB").save(output_path, quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🖼️ STILE 3: CORNICE MINIMAL FINE ART & SIGILLO TONDO (Studio Zero24 Versilia)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_flyer_cornice_minimal_1_1(media_info, palette=None, output_path=None):
    """
    Stile 3 ispirato all'immagine 3 (media_1791469687578.jpg):
    - Formato Quadrato 1:1 (1080x1080)
    - Foto grande a tutto schermo protagonista assoluta
    - Bordo esterno color petrolio/teal o color palette (spessore ~36px)
    - Cornice interna sottile a filo (fine-art inset line)
    - Sigillo tondo bianco in basso a destra con logo Immobiliare Giancani
    - Badge discreto ed elegante con Prezzo e metri quadri
    """
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_minimal_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    border_color = (20, 148, 140, 255)  # Teal elegante come la reference
    BORDER_THICKNESS = 36
    INSET_GAP = 22

    # 1. Foto a pieno formato
    foto = get_clean_property_photo(media_info, (W, H))
    canvas = foto.convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # 2. Cornice esterna piena
    draw.rectangle([(0, 0), (W, BORDER_THICKNESS)], fill=border_color)               # Top
    draw.rectangle([(0, H - BORDER_THICKNESS), (W, H)], fill=border_color)           # Bottom
    draw.rectangle([(0, 0), (BORDER_THICKNESS, H)], fill=border_color)               # Left
    draw.rectangle([(W - BORDER_THICKNESS, 0), (W, H)], fill=border_color)           # Right

    # 3. Cornice interna sottile a filo (line-art geometrica)
    ix1 = BORDER_THICKNESS + INSET_GAP
    iy1 = BORDER_THICKNESS + INSET_GAP
    ix2 = W - BORDER_THICKNESS - INSET_GAP
    iy2 = H - BORDER_THICKNESS - INSET_GAP
    draw.rectangle([(ix1, iy1), (ix2, iy2)], outline=border_color, width=3)

    # 4. Badge Esteso Panoramico in basso a destra (Logo Bello Esteso!)
    seal_w, seal_h = 320, 85
    seal_x = ix2 - seal_w - 15
    seal_y = iy2 - seal_h - 15

    draw.rounded_rectangle([seal_x, seal_y, seal_x + seal_w, seal_y + seal_h], radius=16, fill=(255, 255, 255, 250), outline=border_color, width=2)
    logo = get_logo_trasparente_ufficiale(max_w=seal_w - 30, max_h=seal_h - 20)
    if logo:
        lw, lh = logo.size
        canvas.paste(logo, (seal_x + (seal_w - lw) // 2, seal_y + (seal_h - lh) // 2), logo)
    else:
        f_s_main = get_font(20, bold=True, font_type="sans")
        draw.text((seal_x + seal_w // 2, seal_y + seal_h // 2), "IMMOBILIARE GIANCANI", font=f_s_main, fill=(15, 23, 42, 255), anchor="mm")

    # 5. Badge Elegante in alto a sinistra con Prezzo e Superficie
    tag_x = ix1 + 20
    tag_y = iy1 + 20
    tag_w = 340
    tag_h = 95
    draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], radius=12, fill=(15, 23, 42, 220), outline=border_color, width=2)
    prezzo_txt = _format_prezzo(media_info.get("prezzo"))
    f_tag_prz = get_font(34, bold=True, font_type="sans")
    draw.text((tag_x + 18, tag_y + 14), prezzo_txt, font=f_tag_prz, fill=(255, 255, 255, 255))
    mq_txt = formatta_metri_quadri(media_info.get("mq", "120"))
    f_tag_mq = get_font(18, bold=True, font_type="sans")
    draw.text((tag_x + 20, tag_y + 58), f"📐 {mq_txt}", font=f_tag_mq, fill=(56, 189, 248, 255))

    canvas.convert("RGB").save(output_path, quality=95)
    return output_path


def crea_story_cornice_minimal_9_16(media_info, palette=None, output_path=None):
    """Versione 9:16 (1080x1920) dello Stile Cornice Minimal con Sigillo"""
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_minimal_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    border_color = (20, 148, 140, 255)
    BORDER_THICKNESS = 42
    INSET_GAP = 26

    foto = get_clean_property_photo(media_info, (W, H))
    canvas = foto.convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # Cornice esterna
    draw.rectangle([(0, 0), (W, BORDER_THICKNESS)], fill=border_color)
    draw.rectangle([(0, H - BORDER_THICKNESS), (W, H)], fill=border_color)
    draw.rectangle([(0, 0), (BORDER_THICKNESS, H)], fill=border_color)
    draw.rectangle([(W - BORDER_THICKNESS, 0), (W, H)], fill=border_color)

    # Cornice interna
    ix1 = BORDER_THICKNESS + INSET_GAP
    iy1 = BORDER_THICKNESS + INSET_GAP
    ix2 = W - BORDER_THICKNESS - INSET_GAP
    iy2 = H - BORDER_THICKNESS - INSET_GAP
    draw.rectangle([(ix1, iy1), (ix2, iy2)], outline=border_color, width=3)

    # Sigillo circolare
    seal_radius = 110
    seal_cx = ix2 - seal_radius - 20
    seal_cy = iy2 - seal_radius - 20
    draw.ellipse([seal_cx - seal_radius - 2, seal_cy - seal_radius - 2,
                  seal_cx + seal_radius + 2, seal_cy + seal_radius + 2], fill=(0, 0, 0, 60))
    draw.ellipse([seal_cx - seal_radius, seal_cy - seal_radius,
                  seal_cx + seal_radius, seal_cy + seal_radius], fill=(255, 255, 255, 255), outline=border_color, width=3)
    draw.ellipse([seal_cx - seal_radius + 10, seal_cy - seal_radius + 10,
                  seal_cx + seal_radius - 10, seal_cy + seal_radius - 10], outline=(203, 213, 225, 255), width=1)

    logo = get_logo_trasparente_ufficiale(max_w=165, max_h=65)
    if logo:
        lw, lh = logo.size
        canvas.paste(logo, (seal_cx - lw // 2, seal_cy - lh // 2 - 15), logo)

    f_s_sub = get_font(15, bold=True, font_type="sans")
    draw.text((seal_cx, seal_cy + 34), "ESCLUSIVA", font=f_s_sub, fill=border_color, anchor="mm")
    f_s_loc = get_font(13, bold=False, font_type="sans")
    draw.text((seal_cx, seal_cy + 55), "FAVARA (AG)", font=f_s_loc, fill=(100, 116, 139, 255), anchor="mm")

    # Card descrittiva in basso a sinistra (con testo Colonna F)
    card_w = ix2 - ix1 - (seal_radius * 2 + 50)
    card_h = 320
    card_x = ix1 + 20
    card_y = iy2 - card_h - 10
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16, fill=(15, 23, 42, 230), outline=border_color, width=2)

    prezzo_txt = _format_prezzo(media_info.get("prezzo"))
    f_prz = get_font(44, bold=True, font_type="sans")
    draw.text((card_x + 24, card_y + 18), prezzo_txt, font=f_prz, fill=(255, 255, 255, 255))

    mq_txt = formatta_metri_quadri(media_info.get("mq", "120"))
    f_mq = get_font(22, bold=True, font_type="sans")
    draw.text((card_x + 26, card_y + 72), f"📐 Superficie: {mq_txt}", font=f_mq, fill=(56, 189, 248, 255))

    testo_f = str(media_info.get("testoF", "")).strip()
    if testo_f:
        draw_fitted_text(draw, testo_f, (card_x + 24, card_y + 115, card_w - 48, 180),
                         max_font_size=21, min_font_size=15, fill=(241, 245, 249, 255), line_spacing=5)

    canvas.convert("RGB").save(output_path, quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🌿 STILE 4: STUDIO ZERO24 MODERN CARD (Petrolio/Teal + 4 Icone Specs)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_zero24_card_9_16(media_info, palette=None, output_path=None):
    """
    Stile 4 ispirato all'immagine 4 (media_1791469687589.jpg):
    - Formato Verticale 9:16 (1080x1920)
    - Badge fluttuante bianco in alto a sinistra con logo e slogan
    - Foto dell'immobile nella metà superiore
    - Metà inferiore color Petrolio / Teal profondo (#005F6A)
    - Titolo serif grande, sottotitolo, prezzo gigante
    - Riga con 4 icone specs: metri quadri, camere, bagni, giardino
    - Barra contatti bianca inferiore
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_zero24_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    teal_color = (0, 95, 106, 255)       # #005F6A Petrolio profondo elegante
    contact_bar_bg = (248, 250, 252, 255) # Bianco crema pulito

    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    # 1. Foto dell'immobile nella parte superiore (altezza 1100px)
    PHOTO_H = 1120
    foto = get_clean_property_photo(media_info, (W, PHOTO_H))
    canvas.paste(foto, (0, 0))

    # 2. Badge fluttuante bianco in alto a sinistra
    draw = ImageDraw.Draw(canvas)
    badge_x, badge_y = 40, 45
    badge_w, badge_h = 360, 130
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=16, fill=(255, 255, 255, 245), outline=(203, 213, 225, 200), width=1)

    logo = get_logo_trasparente_ufficiale(max_w=280, max_h=65)
    if logo:
        canvas.paste(logo, (badge_x + 35, badge_y + 14), logo)
    else:
        f_b_tit = get_font(26, bold=True, font_type="sans")
        draw.text((badge_x + 35, badge_y + 20), "IMMOBILIARE GIANCANI", font=f_b_tit, fill=(15, 23, 42, 255))

    f_slogan = get_font(14, bold=True, font_type="sans")
    draw.text((badge_x + badge_w // 2, badge_y + badge_h - 24), "LA TUA CASA, IL NOSTRO IMPEGNO.", font=f_slogan, fill=teal_color, anchor="mm")

    # 3. Blocco Inferiore Petrolio/Teal (da PHOTO_H a H - 150)
    CONTACT_H = 150
    block_y = PHOTO_H
    block_h = H - PHOTO_H - CONTACT_H
    draw.rectangle([(0, block_y), (W, block_y + block_h)], fill=teal_color)

    # 3a. Categoria centrata spaziata
    tipologia = str(media_info.get("tipologia", "VILLA INDIPENDENTE")).upper()
    f_cat = get_font(22, bold=True, font_type="sans")
    draw.text((W // 2, block_y + 40), tipologia, font=f_cat, fill=(204, 251, 241, 255), anchor="mm")

    # 3b. Titolo Grande Elegante Serif
    titolo = str(media_info.get("titolo", "Favara")).strip().title()
    f_tit = get_font(52, bold=True, font_type="serif")
    draw.text((W // 2, block_y + 95), titolo[:32], font=f_tit, fill=(255, 255, 255, 255), anchor="mm")

    # 3c. Sottotitolo
    zona = str(media_info.get("zona", "ZONA PANORAMICA")).upper()
    f_sub = get_font(24, bold=True, font_type="sans")
    draw.text((W // 2, block_y + 148), zona[:35], font=f_sub, fill=(153, 246, 228, 255), anchor="mm")

    # 3d. Prezzo Gigante
    prezzo_txt = _format_prezzo(media_info.get("prezzo"))
    f_prz = get_font(62, bold=True, font_type="sans")
    draw.text((W // 2, block_y + 225), prezzo_txt, font=f_prz, fill=(255, 255, 255, 255), anchor="mm")

    # 3e. Riga di 4 Icone Specs Disegnate
    icons_y = block_y + 310
    col_w = W // 4

    mq_txt = formatta_metri_quadri(media_info.get("mq", "130"))
    locali_txt = str(media_info.get("locali", "3")).strip() + " camere"
    bagni_txt = str(media_info.get("bagni", "2")).strip() + " bagni"
    extra_txt = "Giardino"

    f_ic_lbl = get_font(21, bold=True, font_type="sans")

    # Col 1: Metri Quadri (Ruler)
    cx1 = col_w // 2
    draw_vector_ruler_sqm(draw, cx1, icons_y, size=46, color=(255, 255, 255, 255), width=3)
    draw.text((cx1, icons_y + 48), mq_txt.replace("metri quadri", "mq"), font=f_ic_lbl, fill=(255, 255, 255, 255), anchor="mm")

    # Col 2: Camere (Letto)
    cx2 = col_w + col_w // 2
    draw_bed_icon(draw, cx2, icons_y, size=46, color=(255, 255, 255, 255), width=3)
    draw.text((cx2, icons_y + 48), locali_txt, font=f_ic_lbl, fill=(255, 255, 255, 255), anchor="mm")

    # Col 3: Bagni (Doccia)
    cx3 = col_w * 2 + col_w // 2
    draw_vector_shower(draw, cx3, icons_y, size=46, color=(255, 255, 255, 255), width=3)
    draw.text((cx3, icons_y + 48), bagni_txt, font=f_ic_lbl, fill=(255, 255, 255, 255), anchor="mm")

    # Col 4: Giardino / Terrazzo (Foglia / Casetta)
    cx4 = col_w * 3 + col_w // 2
    # Disegna foglia stilizzata
    s_leaf = 20
    draw.arc([cx4 - s_leaf, icons_y - s_leaf, cx4 + s_leaf, icons_y + s_leaf], start=0, end=90, fill=(255, 255, 255, 255), width=3)
    draw.arc([cx4 - s_leaf, icons_y - s_leaf, cx4 + s_leaf, icons_y + s_leaf], start=180, end=270, fill=(255, 255, 255, 255), width=3)
    draw.line([(cx4 - s_leaf, icons_y + s_leaf), (cx4 + s_leaf, icons_y - s_leaf)], fill=(255, 255, 255, 255), width=2)
    draw.text((cx4, icons_y + 48), extra_txt, font=f_ic_lbl, fill=(255, 255, 255, 255), anchor="mm")

    # Breve testo da Colonna F nello spazio rimanente
    testo_f = str(media_info.get("testoF", "")).strip()
    if testo_f:
        draw_fitted_text(draw, testo_f, (60, icons_y + 85, W - 120, 105),
                         max_font_size=20, min_font_size=15, fill=(241, 245, 249, 240), align="center")

    # 4. Barra Contatti Bianca Inferiore (H: 150px)
    cbar_y = H - CONTACT_H
    draw.rectangle([(0, cbar_y), (W, H)], fill=contact_bar_bg)
    draw.line([(0, cbar_y), (W, cbar_y)], fill=(203, 213, 225, 255), width=2)

    # 3 Colonne Contatti
    cw3 = W // 3

    # Colonna 1: Telefono
    cx_c1 = cw3 // 2
    draw_phone_icon(draw, cx_c1 - 70, cbar_y + 75, size=32, color=teal_color)
    f_cb_lbl = get_font(15, bold=False, font_type="sans")
    f_cb_val = get_font(21, bold=True, font_type="sans")
    draw.text((cx_c1 - 40, cbar_y + 45), "PER INFO", font=f_cb_lbl, fill=(100, 116, 139, 255))
    draw.text((cx_c1 - 40, cbar_y + 72), "320 166 7156", font=f_cb_val, fill=(15, 23, 42, 255))

    # Colonna 2: Sede / Rif
    cx_c2 = cw3 + cw3 // 2
    draw_pin_icon(draw, cx_c2 - 70, cbar_y + 75, size=32, color=teal_color)
    draw.text((cx_c2 - 40, cbar_y + 45), "SEDE FAVARA", font=f_cb_lbl, fill=(100, 116, 139, 255))
    cod_rif = str(media_info.get("codiceRif", "RIF. GIANCANI")).replace("_", " ").upper()
    draw.text((cx_c2 - 40, cbar_y + 72), cod_rif[:15], font=f_cb_val, fill=(15, 23, 42, 255))

    # Colonna 3: Sito Web
    cx_c3 = cw3 * 2 + cw3 // 2
    # Disegna icona mappamondo
    r_globe = 16
    draw.ellipse([cx_c3 - 70 - r_globe, cbar_y + 75 - r_globe, cx_c3 - 70 + r_globe, cbar_y + 75 + r_globe], outline=teal_color, width=2)
    draw.ellipse([cx_c3 - 70 - r_globe // 2, cbar_y + 75 - r_globe, cx_c3 - 70 + r_globe // 2, cbar_y + 75 + r_globe], outline=teal_color, width=2)
    draw.line([(cx_c3 - 70 - r_globe, cbar_y + 75), (cx_c3 - 70 + r_globe, cbar_y + 75)], fill=teal_color, width=2)

    draw.text((cx_c3 - 40, cbar_y + 45), "SCOPRI DI PIÙ SU", font=f_cb_lbl, fill=(100, 116, 139, 255))
    draw.text((cx_c3 - 40, cbar_y + 72), "GIANCANI.IT", font=f_cb_val, fill=teal_color)

    canvas.convert("RGB").save(output_path, quality=95)
    return output_path


def crea_flyer_zero24_card_1_1(media_info, palette=None, output_path=None):
    """Versione 1:1 (1080x1080) dello Stile Studio Zero24 Modern Card"""
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_zero24_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    teal_color = (0, 95, 106, 255)
    contact_bar_bg = (248, 250, 252, 255)

    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    # Foto superiore (altezza 560px)
    PHOTO_H = 560
    foto = get_clean_property_photo(media_info, (W, PHOTO_H))
    canvas.paste(foto, (0, 0))

    draw = ImageDraw.Draw(canvas)

    # Badge in alto a sinistra
    draw.rounded_rectangle([30, 30, 350, 125], radius=14, fill=(255, 255, 255, 245), outline=(203, 213, 225, 200), width=1)
    logo = get_logo_trasparente_ufficiale(max_w=240, max_h=55)
    if logo:
        canvas.paste(logo, (45, 40), logo)
    f_slogan = get_font(12, bold=True, font_type="sans")
    draw.text((190, 105), "LA TUA CASA, IL NOSTRO IMPEGNO.", font=f_slogan, fill=teal_color, anchor="mm")

    # Blocco Teal inferiore
    CONTACT_H = 110
    block_y = PHOTO_H
    block_h = H - PHOTO_H - CONTACT_H
    draw.rectangle([(0, block_y), (W, block_y + block_h)], fill=teal_color)

    tipologia = str(media_info.get("tipologia", "VILLA BIFAMILIARE")).upper()
    f_cat = get_font(18, bold=True, font_type="sans")
    draw.text((W // 2, block_y + 26), tipologia, font=f_cat, fill=(204, 251, 241, 255), anchor="mm")

    titolo = str(media_info.get("titolo", "Favara")).strip().title()
    f_tit = get_font(38, bold=True, font_type="serif")
    draw.text((W // 2, block_y + 65), titolo[:34], font=f_tit, fill=(255, 255, 255, 255), anchor="mm")

    prezzo_txt = _format_prezzo(media_info.get("prezzo"))
    f_prz = get_font(48, bold=True, font_type="sans")
    draw.text((W // 2, block_y + 130), prezzo_txt, font=f_prz, fill=(255, 255, 255, 255), anchor="mm")

    # 4 Icone Specs
    icons_y = block_y + 205
    col_w = W // 4
    mq_txt = formatta_metri_quadri(media_info.get("mq", "130"))
    locali_txt = str(media_info.get("locali", "3")).strip() + " camere"
    bagni_txt = str(media_info.get("bagni", "2")).strip() + " bagni"

    f_ic_lbl = get_font(18, bold=True, font_type="sans")

    cx1 = col_w // 2
    draw_vector_ruler_sqm(draw, cx1, icons_y, size=38, color=(255, 255, 255, 255), width=2)
    draw.text((cx1, icons_y + 40), mq_txt.replace("metri quadri", "mq"), font=f_ic_lbl, fill=(255, 255, 255, 255), anchor="mm")

    cx2 = col_w + col_w // 2
    draw_bed_icon(draw, cx2, icons_y, size=38, color=(255, 255, 255, 255), width=2)
    draw.text((cx2, icons_y + 40), locali_txt, font=f_ic_lbl, fill=(255, 255, 255, 255), anchor="mm")

    cx3 = col_w * 2 + col_w // 2
    draw_vector_shower(draw, cx3, icons_y, size=38, color=(255, 255, 255, 255), width=2)
    draw.text((cx3, icons_y + 40), bagni_txt, font=f_ic_lbl, fill=(255, 255, 255, 255), anchor="mm")

    cx4 = col_w * 3 + col_w // 2
    s_leaf = 16
    draw.arc([cx4 - s_leaf, icons_y - s_leaf, cx4 + s_leaf, icons_y + s_leaf], start=0, end=90, fill=(255, 255, 255, 255), width=2)
    draw.arc([cx4 - s_leaf, icons_y - s_leaf, cx4 + s_leaf, icons_y + s_leaf], start=180, end=270, fill=(255, 255, 255, 255), width=2)
    draw.line([(cx4 - s_leaf, icons_y + s_leaf), (cx4 + s_leaf, icons_y - s_leaf)], fill=(255, 255, 255, 255), width=2)
    draw.text((cx4, icons_y + 40), "Giardino", font=f_ic_lbl, fill=(255, 255, 255, 255), anchor="mm")

    # Testo narrativo Colonna F
    testo_f = str(media_info.get("testoF", "")).strip()
    if testo_f:
        draw_fitted_text(draw, testo_f, (50, icons_y + 75, W - 100, 85),
                         max_font_size=18, min_font_size=14, fill=(241, 245, 249, 240), align="center")

    # Barra contatti
    cbar_y = H - CONTACT_H
    draw.rectangle([(0, cbar_y), (W, H)], fill=contact_bar_bg)
    draw.line([(0, cbar_y), (W, cbar_y)], fill=(203, 213, 225, 255), width=2)

    cw3 = W // 3
    f_cb_lbl = get_font(13, bold=False, font_type="sans")
    f_cb_val = get_font(18, bold=True, font_type="sans")

    # Col 1
    cx_c1 = cw3 // 2
    draw_phone_icon(draw, cx_c1 - 55, cbar_y + 55, size=26, color=teal_color)
    draw.text((cx_c1 - 30, cbar_y + 32), "PER INFO", font=f_cb_lbl, fill=(100, 116, 139, 255))
    draw.text((cx_c1 - 30, cbar_y + 55), "320 166 7156", font=f_cb_val, fill=(15, 23, 42, 255))

    # Col 2
    cx_c2 = cw3 + cw3 // 2
    draw_pin_icon(draw, cx_c2 - 55, cbar_y + 55, size=26, color=teal_color)
    draw.text((cx_c2 - 30, cbar_y + 32), "SEDE FAVARA", font=f_cb_lbl, fill=(100, 116, 139, 255))
    cod_rif = str(media_info.get("codiceRif", "GIANCANI")).replace("_", " ").upper()
    draw.text((cx_c2 - 30, cbar_y + 55), cod_rif[:12], font=f_cb_val, fill=(15, 23, 42, 255))

    # Col 3
    cx_c3 = cw3 * 2 + cw3 // 2
    draw.text((cx_c3 - 30, cbar_y + 32), "SCOPRI DI PIÙ SU", font=f_cb_lbl, fill=(100, 116, 139, 255))
    draw.text((cx_c3 - 30, cbar_y + 55), "GIANCANI.IT", font=f_cb_val, fill=teal_color)

    canvas.convert("RGB").save(output_path, quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 📰 STILE 5: TECNOCASA GAZZETTA 4 FOTO (Grid 2x2 + Colonna F + OCCASIONE)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_tecnocasa_gazzetta_9_16(media_info, palette=None, output_path=None):
    """
    Stile 5 ispirato all'immagine 5 (uploaded_media_1_1791469719854.jpg):
    - Formato Verticale 9:16 (1080x1920)
    - Testata superiore bianca con logo Immobiliare Giancani grande
    - Banner orizzontale verde scuro: 'VENDESI [TITOLO IMMOBILE]'
    - Griglia a 4 Foto (2x2) separate da profili bianchi
    - Box descrittivo su sfondo bianco con testo da Colonna F
    - Prezzo gigante in verde + Badge 3D arancione 'OCCASIONE'
    - Footer contatti verde scuro completo
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_tecnocasa_grid_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    green_dark = (15, 81, 50, 255)     # #0F5132 Verde classico gazzetta immobiliare
    orange_badge = (245, 130, 32, 255)  # Arancio vibrante callout

    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # 1. Testata Superiore Bianca (H: 150px)
    HEADER_H = 150
    draw.rectangle([(0, 0), (W, HEADER_H)], fill=(255, 255, 255, 255))
    logo = get_logo_trasparente_ufficiale(max_w=380, max_h=95)
    if logo:
        lw, lh = logo.size
        canvas.paste(logo, ((W - lw) // 2, (HEADER_H - lh) // 2), logo)
    else:
        f_top = get_font(38, bold=True, font_type="sans")
        draw.text((W // 2, HEADER_H // 2), "IMMOBILIARE GIANCANI", font=f_top, fill=green_dark, anchor="mm")

    # 2. Banner Verde Titolo Vendesi (H: 75px)
    BANNER_H = 75
    banner_y = HEADER_H
    draw.rectangle([(0, banner_y), (W, banner_y + BANNER_H)], fill=green_dark)

    titolo = str(media_info.get("titolo", "VILLA PANORAMICA")).upper().strip()
    zona = str(media_info.get("zona", "FAVARA")).upper().strip()
    titolo_banner = f"VENDESI {titolo} - {zona}"
    if len(titolo_banner) > 42:
        titolo_banner = f"VENDESI {titolo}"[:40]
    f_ban = get_font(32, bold=True, font_type="sans")
    draw.text((W // 2, banner_y + BANNER_H // 2), titolo_banner, font=f_ban, fill=(255, 255, 255, 255), anchor="mm")

    # 3. Griglia a 4 Foto (2x2)
    # Area totale griglia: W x 820px
    grid_y = banner_y + BANNER_H
    grid_h = 820
    gutter = 6
    cell_w = (W - gutter) // 2
    cell_h = (grid_h - gutter) // 2

    quattro_foto = _estrai_foto_multiple(media_info, target_count=4)

    coords = [
        (0, grid_y, cell_w, cell_h),                                # Alto-SX
        (cell_w + gutter, grid_y, W - cell_w - gutter, cell_h),       # Alto-DX
        (0, grid_y + cell_h + gutter, cell_w, grid_h - cell_h - gutter), # Basso-SX
        (cell_w + gutter, grid_y + cell_h + gutter, W - cell_w - gutter, grid_h - cell_h - gutter) # Basso-DX
    ]

    for idx, (cx, cy, cw, ch) in enumerate(coords):
        im = quattro_foto[idx]
        # Adatta con crop centratura
        iw, ih = im.size
        scale = max(cw / iw, ch / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        im_sc = im.resize((nw, nh), Image.LANCZOS)
        ox = (nw - cw) // 2
        oy = (nh - ch) // 2
        im_crop = im_sc.crop((ox, oy, ox + cw, oy + ch))
        canvas.paste(im_crop, (cx, cy))

    # 4. Box Descrittivo su Sfondo Bianco
    desc_y = grid_y + grid_h + 20
    desc_h = 440

    # Sommario / Sintesi in grassetto
    mq_txt = formatta_metri_quadri(media_info.get("mq", "120"))
    locali_txt = str(media_info.get("locali", "4")).strip() + " vani"
    lead_txt = f"{titolo.title()} a {zona.title()} con superficie di {mq_txt} e {locali_txt}."
    f_lead = get_font(26, bold=True, font_type="sans")
    draw.text((40, desc_y), lead_txt[:55], font=f_lead, fill=(15, 23, 42, 255))

    # Testo esteso rigorosamente da Colonna F
    testo_f = str(media_info.get("testoF", "")).strip()
    if not testo_f:
        testo_f = "Splendida proprietà rifinita in ogni dettaglio, ideale come residenza principale o investimento di pregio nel territorio. — Immobiliare Giancani"

    draw_fitted_text(draw, testo_f, (40, desc_y + 40, W - 80, 240),
                     max_font_size=24, min_font_size=17, fill=(30, 41, 59, 255), line_spacing=6)

    # 5. Riga Prezzo Gigante & Badge 'OCCASIONE'
    prz_row_y = desc_y + 300
    prezzo_txt = _format_prezzo(media_info.get("prezzo"))
    f_prz_giga = get_font(68, bold=True, font_type="sans")
    draw.text((40, prz_row_y), prezzo_txt, font=f_prz_giga, fill=green_dark)

    # Badge 'OCCASIONE'
    badge_txt = "OCCASIONE"
    f_badge_occ = get_font(46, bold=True, font_type="sans")
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge_occ)
    bw, bh = bb[2] - bb[0] + 44, bb[3] - bb[1] + 24
    bx = W - bw - 40
    by = prz_row_y + 10

    # Bordo esterno giallo/arancio sagomato
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(255, 255, 255, 255), outline=orange_badge, width=4)
    # Testo arancione interno
    draw.text((bx + 22, by + 10), badge_txt, font=f_badge_occ, fill=orange_badge)

    # 6. Footer Contatti Verde Scuro (H: 210px in fondo)
    FOOTER_H = 210
    foot_y = H - FOOTER_H
    draw.rectangle([(0, foot_y), (W, H)], fill=green_dark)

    f_ft_hdr = get_font(24, bold=True, font_type="sans")
    draw.text((W // 2, foot_y + 28), "CONTATTI", font=f_ft_hdr, fill=(255, 255, 255, 255), anchor="mm")

    f_ft_tel = get_font(30, bold=True, font_type="sans")
    draw.text((W // 2, foot_y + 75), "TELEFONO / WHATSAPP: 320 166 7156", font=f_ft_tel, fill=(254, 240, 138, 255), anchor="mm")

    f_ft_sub = get_font(21, bold=False, font_type="sans")
    draw.text((W // 2, foot_y + 125), "Studio Immobiliare Giancani • Corso Vittorio Veneto 151 • Favara (AG)", font=f_ft_sub, fill=(241, 245, 249, 240), anchor="mm")

    f_ft_mail = get_font(19, bold=False, font_type="sans")
    draw.text((W // 2, foot_y + 165), "Email: immobiliaregiancani@gmail.com • www.immobiliaregiancani.it", font=f_ft_mail, fill=(203, 213, 225, 220), anchor="mm")

    canvas.convert("RGB").save(output_path, quality=95)
    return output_path


def crea_flyer_tecnocasa_gazzetta_1_1(media_info, palette=None, output_path=None):
    """Versione 1:1 (1080x1080) dello Stile Tecnocasa Gazzetta 4 Foto"""
    W, H = 1080, 1080
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"flyer_tecnocasa_grid_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    green_dark = (15, 81, 50, 255)
    orange_badge = (245, 130, 32, 255)

    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # Testata (H: 80px)
    draw.rectangle([(0, 0), (W, 80)], fill=(255, 255, 255, 255))
    logo = get_logo_trasparente_ufficiale(max_w=280, max_h=55)
    if logo:
        lw, lh = logo.size
        canvas.paste(logo, ((W - lw) // 2, (80 - lh) // 2), logo)

    # Banner Vendesi (H: 50px)
    draw.rectangle([(0, 80), (W, 130)], fill=green_dark)
    titolo = str(media_info.get("titolo", "VILLA PANORAMICA")).upper().strip()
    f_ban = get_font(24, bold=True, font_type="sans")
    draw.text((W // 2, 105), f"VENDESI {titolo[:38]}", font=f_ban, fill=(255, 255, 255, 255), anchor="mm")

    # Griglia 4 foto (H: 480px)
    grid_y = 130
    grid_h = 480
    gutter = 4
    cell_w = (W - gutter) // 2
    cell_h = (grid_h - gutter) // 2

    quattro_foto = _estrai_foto_multiple(media_info, target_count=4)
    coords = [
        (0, grid_y, cell_w, cell_h),
        (cell_w + gutter, grid_y, W - cell_w - gutter, cell_h),
        (0, grid_y + cell_h + gutter, cell_w, grid_h - cell_h - gutter),
        (cell_w + gutter, grid_y + cell_h + gutter, W - cell_w - gutter, grid_h - cell_h - gutter)
    ]
    for idx, (cx, cy, cw, ch) in enumerate(coords):
        im = quattro_foto[idx]
        iw, ih = im.size
        scale = max(cw / iw, ch / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        im_sc = im.resize((nw, nh), Image.LANCZOS)
        ox = (nw - cw) // 2
        oy = (nh - ch) // 2
        im_crop = im_sc.crop((ox, oy, ox + cw, oy + ch))
        canvas.paste(im_crop, (cx, cy))

    # Box Descrittivo
    desc_y = grid_y + grid_h + 15
    mq_txt = formatta_metri_quadri(media_info.get("mq", "120"))
    locali_txt = str(media_info.get("locali", "4")).strip() + " vani"
    lead_txt = f"{titolo.title()} — {mq_txt} • {locali_txt}"
    f_lead = get_font(22, bold=True, font_type="sans")
    draw.text((30, desc_y), lead_txt, font=f_lead, fill=(15, 23, 42, 255))

    testo_f = str(media_info.get("testoF", "")).strip()
    if not testo_f:
        testo_f = "Splendida residenza proposta in vendita esclusiva da Immobiliare Giancani."
    draw_fitted_text(draw, testo_f, (30, desc_y + 30, W - 60, 180),
                     max_font_size=19, min_font_size=14, fill=(30, 41, 59, 255), line_spacing=5)

    # Prezzo & OCCASIONE
    prz_row_y = desc_y + 225
    prezzo_txt = _format_prezzo(media_info.get("prezzo"))
    f_prz_giga = get_font(48, bold=True, font_type="sans")
    draw.text((30, prz_row_y), prezzo_txt, font=f_prz_giga, fill=green_dark)

    badge_txt = "OCCASIONE"
    f_badge_occ = get_font(32, bold=True, font_type="sans")
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge_occ)
    bw, bh = bb[2] - bb[0] + 32, bb[3] - bb[1] + 16
    bx = W - bw - 30
    by = prz_row_y + 4
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=10, fill=(255, 255, 255, 255), outline=orange_badge, width=3)
    draw.text((bx + 16, by + 8), badge_txt, font=f_badge_occ, fill=orange_badge)

    # Footer (H: 110px)
    FOOTER_H = 110
    foot_y = H - FOOTER_H
    draw.rectangle([(0, foot_y), (W, H)], fill=green_dark)

    f_ft_tel = get_font(23, bold=True, font_type="sans")
    draw.text((W // 2, foot_y + 30), "CONTATTI • TELEFONO / WHATSAPP: 320 166 7156", font=f_ft_tel, fill=(254, 240, 138, 255), anchor="mm")

    f_ft_sub = get_font(17, bold=False, font_type="sans")
    draw.text((W // 2, foot_y + 68), "Studio Immobiliare Giancani • Corso Vittorio Veneto 151 • Favara (AG)", font=f_ft_sub, fill=(241, 245, 249, 240), anchor="mm")

    canvas.convert("RGB").save(output_path, quality=95)
    return output_path



# ═══════════════════════════════════════════════════════════════════════════════
# 🔴 CARD STORIA LIVE SCREENSHOT (ORIGINALE RICHIESTA UTENTE + COLORE FONDO DINAMICO)
# ═══════════════════════════════════════════════════════════════════════════════

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

def crea_card_storia_live_screenshot_9_16(media_info, palette=None, output_path=None, usa_palette_bg=True):
    """
    Riproduce fedelmente la grafica dello screenshot della diretta live (1080x1920)
    con il supporto del colore di fondo dinamico della palette del giorno.
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"card_live_screenshot_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    # 1. Fallback robusto anti-blocco sulla foto dell'immobile
    cardX, cardY, cardW, cardH = 50, 230, 980, 870
    foto_immobile = get_clean_property_photo(media_info, target_size=(cardW, cardH))

    # 2. Sfondo Base Scuro Elegante con Blur della foto (proprio come in Index.html)
    canvas = Image.new("RGBA", (W, H), (6, 10, 20, 255))
    try:
        bg_blur = foto_immobile.resize((W, H)).filter(ImageFilter.GaussianBlur(32))
        canvas.paste(bg_blur.convert("RGBA"), (0, 0))
    except Exception:
        pass

    # Overlay scuro per contrasto
    overlay_bg = Image.new("RGBA", (W, H), (6, 10, 20, 185))
    canvas = Image.alpha_composite(canvas, overlay_bg)
    draw = ImageDraw.Draw(canvas)

    # Cornice esterna dorata leggera
    draw.rounded_rectangle([20, 20, W - 20, H - 20], radius=28, outline=(212, 168, 83, 110), width=3)

    # 3. Foto centrale con angoli arrotondati e cornice dorata
    mask_foto = Image.new("L", (cardW, cardH), 0)
    d_mf = ImageDraw.Draw(mask_foto)
    d_mf.rounded_rectangle([0, 0, cardW, cardH], radius=26, fill=255)
    canvas.paste(foto_immobile.convert("RGBA"), (cardX, cardY), mask_foto)

    # Cornice dorata attorno alla foto centrale
    draw.rounded_rectangle([cardX, cardY, cardX + cardW, cardY + cardH], radius=26, outline=(212, 175, 55, 220), width=3)

    # Watermark Logo Agenzia in alto a destra sulla foto (Badge Rettangolare Panoramico Esteso - Bello Esteso!)
    wm_w, wm_h = 290, 75
    wm_x = cardX + cardW - wm_w - 20
    wm_y = cardY + 20
    draw.rounded_rectangle([wm_x, wm_y, wm_x + wm_w, wm_y + wm_h], radius=16, fill=(255, 255, 255, 248), outline=(212, 168, 83, 245), width=2)
    logo_wm = get_logo_trasparente_ufficiale(max_w=wm_w - 28, max_h=wm_h - 18)
    if logo_wm:
        lw_wm, lh_wm = logo_wm.size
        canvas.paste(logo_wm, (wm_x + (wm_w - lw_wm) // 2, wm_y + (wm_h - lh_wm) // 2), logo_wm)
    else:
        f_wm_txt = get_font(20, bold=True, font_type="sans")
        draw.text((wm_x + wm_w // 2, wm_y + wm_h // 2), "IMMOBILIARE GIANCANI", font=f_wm_txt, fill=(15, 23, 42, 255), anchor="mm")

    # 4. Header: Logo Ufficiale in Pillola Bianca Splendente
    pill_w, pill_h = 480, 105
    pill_x = (W - pill_w) // 2
    pill_y = 55
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=22, fill=(255, 255, 255, 250), outline=(212, 168, 83, 160), width=1)
    logo_top = get_logo_trasparente_ufficiale(max_w=400, max_h=80)
    if logo_top:
        lw_t, lh_t = logo_top.size
        canvas.paste(logo_top, ((W - lw_t) // 2, pill_y + (pill_h - lh_t) // 2), logo_top)
    else:
        f_top_ig = get_font(34, bold=True, font_type="sans")
        draw.text((W // 2, pill_y + pill_h // 2), "IMMOBILIARE GIANCANI", font=f_top_ig, fill=(212, 175, 55, 255), anchor="mm")

    # Badge Rosso Live sotto al logo
    live_y = 175
    draw.rounded_rectangle([280, live_y, 800, live_y + 44], radius=22, fill=(220, 38, 38, 255))
    draw.ellipse([305, live_y + 13, 323, live_y + 31], fill=(255, 255, 255, 255))
    f_live = get_font(21, bold=True, font_type="sans")
    draw.text((W // 2 + 10, live_y + 22), "IN DIRETTA ORA • TOUR VIRTUALE", font=f_live, fill=(255, 255, 255, 255), anchor="mm")

    # 5. Scheda Informativa Inferiore con Colore di Fondo Dinamico
    cardY0 = 1135
    cardH0 = 735
    cardX0 = 50
    cardW0 = 980

    # Determinazione Colore Fondo Scheda (Giallo solare, Bordeaux, Emerald o Navy classico)
    if usa_palette_bg and palette:
        p_dark = palette.get("primary_dark", (11, 19, 38, 255))
        # Se è giallo brillante (chiaro), scuriamo elegantemente per mantenere il contrasto del testo
        if p_dark[0] > 200 and p_dark[1] > 160 and p_dark[2] < 100:
            # Giallo Solare -> fondo Slate scuro con riflesso oro ambrato caldo
            card_fill = (22, 28, 42, 245)
            border_gold = (245, 190, 11, 240)
        else:
            # Altri temi: usa tinta scura armoniosa del giorno
            r_c = max(10, int(p_dark[0] * 0.25))
            g_c = max(14, int(p_dark[1] * 0.25))
            b_c = max(24, int(p_dark[2] * 0.25))
            card_fill = (r_c, g_c, b_c, 245)
            border_gold = palette.get("accent", (212, 175, 55, 220))
    else:
        card_fill = (11, 19, 38, 245)
        border_gold = (212, 175, 55, 220)

    draw.rounded_rectangle([cardX0, cardY0, cardX0 + cardW0, cardY0 + cardH0], radius=30, fill=card_fill, outline=border_gold, width=3)

    # 5a. Badge Dorato: 'IMMOBILE IN VENDITA IN ESCLUSIVA'
    badge_txt = "IMMOBILE IN VENDITA IN ESCLUSIVA"
    f_bdg = get_font(20, bold=True, font_type="sans")
    bw = draw.textlength(badge_txt, font=f_bdg) + 56
    draw.rounded_rectangle([80, cardY0 + 26, int(80 + bw), cardY0 + 66], radius=12, fill=(180, 130, 20, 255))
    draw_house_icon(draw, 102, cardY0 + 46, size=24, color=(255, 255, 255, 255), width=2)
    draw.text((124, cardY0 + 46), badge_txt, font=f_bdg, fill=(255, 255, 255, 255), anchor="lm")

    # 5b. Titolo dell'Immobile (con a-capo o auto-fit)
    titolo = str(media_info.get("titolo", "APPARTAMENTO CORSO VITTORIO VENETO")).upper().strip()
    f_tit = get_font(36, bold=True, font_type="sans")
    if len(titolo) > 38:
        tit_lines = [titolo[:36] + "..."]
    else:
        tit_lines = [titolo]
    draw.text((80, cardY0 + 112), tit_lines[0], font=f_tit, fill=(255, 255, 255, 255))

    # 5c. Ambiente / Stanza (in azzurro)
    stanza = str(media_info.get("stanza", media_info.get("tipologia", "SALOTTO VUOTO"))).upper().strip()
    st_label = f"Ambiente: {stanza}"
    f_st = get_font(28, bold=True, font_type="sans")
    draw_pin_icon(draw, 96, cardY0 + 172, size=26, color=(56, 189, 248, 255))
    draw.text((120, cardY0 + 172), st_label[:40], font=f_st, fill=(56, 189, 248, 255), anchor="lm")

    # 5d. Superficie in 'metri quadri' (in giallo)
    mq_txt = formatta_metri_quadri(media_info.get("mq", "140"))
    f_mq = get_font(29, bold=True, font_type="sans")
    draw_vector_ruler_sqm(draw, 96, cardY0 + 225, size=26, color=(250, 204, 21, 255), width=2)
    draw.text((120, cardY0 + 225), f"Superficie: {mq_txt}", font=f_mq, fill=(250, 204, 21, 255), anchor="lm")

    # 5e. Prezzo (in verde)
    prezzo_txt = str(media_info.get("prezzo", "Trattativa Riservata")).strip()
    if prezzo_txt.isdigit():
        prezzo_txt = f"€ {int(prezzo_txt):,}".replace(",", ".")
    elif "€" not in prezzo_txt and any(c.isdigit() for c in prezzo_txt):
        prezzo_txt = f"€ {prezzo_txt}"
    f_pr = get_font(32, bold=True, font_type="sans")
    draw.text((80, cardY0 + 280), "💰", font=get_font(26, bold=True), fill=(74, 222, 128, 255), anchor="lm")
    draw.text((120, cardY0 + 280), f"Prezzo: {prezzo_txt}", font=f_pr, fill=(74, 222, 128, 255), anchor="lm")

    # 5f. Descrizione dalla Colonna F
    testo_f = str(media_info.get("testoF", "")).strip()
    if not testo_f:
        testo_f = "Immaginate la luce dorata che bagna gli ampi spazi di questo ambiente rifinito con cura, pronto a trasformarsi nel cuore pulsante della vostra nuova vita."
    clean_testo_f = re.sub(r'\s*—?\s*Immobiliare Giancani\s*$', '', testo_f).strip()
    testo_virgolettato = f'"{clean_testo_f}"'
    draw_fitted_text(draw, testo_virgolettato, (80, cardY0 + 325, 860, 150),
                     max_font_size=23, min_font_size=16, font_type="sans",
                     fill=(203, 213, 225, 255), line_spacing=6)

    # 5g. Banner CTA d'invito alla diretta con gradiente blu/ciano e bordo oro
    cta_y = cardY0 + 510
    cta_w = 900
    cta_x = (W - cta_w) // 2
    # Disegna gradiente blu
    cta_img = Image.new("RGBA", (cta_w, 75), (2, 132, 199, 255))
    d_cta = ImageDraw.Draw(cta_img)
    for x in range(cta_w):
        r_grad = int(30 + (2 - 30) * (x / cta_w))
        g_grad = int(58 + (132 - 58) * (x / cta_w))
        b_grad = int(138 + (199 - 138) * (x / cta_w))
        d_cta.line([(x, 0), (x, 75)], fill=(r_grad, g_grad, b_grad, 255))
    
    # Maschera arrotondata per CTA
    mask_cta = Image.new("L", (cta_w, 75), 0)
    d_mcta = ImageDraw.Draw(mask_cta)
    d_mcta.rounded_rectangle([0, 0, cta_w, 75], radius=18, fill=255)
    canvas.paste(cta_img, (cta_x, cta_y), mask_cta)
    draw.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + 75], radius=18, outline=(250, 204, 21, 255), width=2)

    f_cta_txt = get_font(26, bold=True, font_type="sans")
    draw.text((W // 2, cta_y + 37), "👉 ENTRA IN DIRETTA PER FARE DOMANDE!", font=f_cta_txt, fill=(255, 255, 255, 255), anchor="mm")

    # 5h. Footer Personal Branding Dorato
    f_foot = get_font(34, bold=True, font_type="sans")
    draw.text((W // 2, cardY0 + 665), "— Immobiliare Giancani —", font=f_foot, fill=(212, 175, 55, 255), anchor="mm")

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=96)
    print(f"[CARD_LIVE_SCREENSHOT_9_16] Generata con successo: {output_path}")
    return output_path




# ═══════════════════════════════════════════════════════════════════════════════
# 🌟 SEZIONE 7 GRAFICHE QUOTIDIANE DEFINITIVE (LUNEDÌ - DOMENICA)
# Ispirate ai Bot GitHub di Tonyhood2345 (C&B Wave, Metroquadro, ProfessioneCasa, Mindset)
# ═══════════════════════════════════════════════════════════════════════════════
import textwrap
import datetime

def _extract_story_field_colonna_f(media_info):
    """Estrae rigorosamente il testo narrativo della Colonna F senza duplicare il brand."""
    if not media_info or not isinstance(media_info, dict):
        return "Splendido immobile selezionato in esclusiva per te."
    val = (
        media_info.get("testoF")
        or media_info.get("descrizione")
        or media_info.get("colonna_f")
        or media_info.get("testo")
        or media_info.get("frase")
        or media_info.get("titolo")
        or "Splendido immobile selezionato in esclusiva."
    )
    # Rimuove eventuale firma già presente per evitare duplicazioni
    clean = re.sub(r'\s*—?\s*Immobiliare Giancani\s*$', '', str(val).strip(), flags=re.IGNORECASE).strip()
    return clean if clean else "Splendido immobile selezionato in esclusiva."

def _extract_story_field_mq(media_info):
    """Formatta la superficie sempre per esteso come 'metri quadri'."""
    val = media_info.get("mq") or media_info.get("superficie") or "120"
    s = str(val).strip()
    s = re.sub(r'(?i)\b(mq|m²|mq\.|m\^2)\b', 'metri quadri', s).strip()
    if "metri quadri" not in s.lower():
        num = re.search(r'\d+', s)
        return f"{num.group(0)} metri quadri" if num else f"{s} metri quadri"
    return s

def _extract_story_field_titolo(media_info):
    tit = media_info.get("titolo") or media_info.get("indirizzo") or media_info.get("nome") or "Opportunità Immobiliare"
    return str(tit).strip()

def _extract_story_field_prezzo(media_info):
    p = media_info.get("prezzo") or "Trattativa Riservata"
    p_str = str(p).strip()
    if p_str and p_str != "Trattativa Riservata" and not p_str.endswith("€") and not p_str.startswith("€"):
        p_str = f"€ {p_str}"
    return p_str

def _extract_story_field_zona(media_info):
    z = media_info.get("zona") or media_info.get("citta") or "Favara (AG)"
    return str(z).strip()

def _paste_logo_protetto(canvas, x, y, max_w=340, max_h=85, with_plate=True, plate_pad=12):
    """Incolla il logo ufficiale Giancani su placca protettiva ad alto contrasto."""
    logo = get_logo_trasparente_ufficiale(max_w=max_w, max_h=max_h)
    if not logo:
        # Fallback testo
        draw = ImageDraw.Draw(canvas)
        draw.text((x, y), "IMMOBILIARE GIANCANI", font=get_font(28, bold=True, font_type="sans"), fill=(185, 28, 28, 255))
        return
    bbox = logo.getbbox()
    if bbox:
        logo = logo.crop(bbox)
    ratio = min(max_w / logo.width, max_h / logo.height)
    lw, lh = max(10, int(logo.width * ratio)), max(10, int(logo.height * ratio))
    logo_s = logo.resize((lw, lh), Image.Resampling.LANCZOS)
    if with_plate:
        plate = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(plate)
        px1, py1 = x - plate_pad, y - plate_pad
        px2, py2 = x + lw + plate_pad, y + lh + plate_pad
        p_draw.rounded_rectangle([(px1, py1), (px2, py2)], radius=16, fill=(255, 255, 255, 252), outline=(210, 215, 225, 220), width=2)
        canvas.paste(plate, (0, 0), plate)
    canvas.paste(logo_s, (x, y), logo_s)

# --- 1. LUNEDÌ: C&B CURVED WAVE (NAVY BLUE & ORO CALDO) ---
def crea_story_daily_lunedi_cb_curved_wave(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_lunedi_cb_curved_{uuid.uuid4().hex[:6]}.png")
    
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = Image.new("RGBA", (W, H), (248, 249, 251, 255))
    header_h = 160

    # Header bianco
    h_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(h_layer)
    hd.rectangle([(0, 0), (W, header_h)], fill=(255, 255, 255, 255))
    wing_pts = [(int(W * 0.62), 0), (W, 0), (W, header_h), (int(W * 0.74), header_h)]
    hd.polygon(wing_pts, fill=(15, 23, 42, 255))
    canvas.paste(h_layer, (0, 0), h_layer)

    # Maschera curva ad onda per la foto
    body_h = H - header_h
    mask = Image.new("L", (W, body_h), 255)
    md = ImageDraw.Draw(mask)
    cut_w = int(W * 0.38)
    wave_pts = [(0, 0), (cut_w, 0)]
    for y in range(0, body_h + 1, 10):
        prog = y / float(body_h)
        x_val = int(cut_w * (1 - 0.35 * prog) + 25 * math.sin(prog * math.pi * 2))
        wave_pts.append((x_val, y))
    wave_pts.extend([(0, body_h), (0, 0)])
    md.polygon(wave_pts, fill=0)

    photo_crop = photo.crop((0, header_h, W, H))
    canvas.paste(photo_crop, (0, header_h), mask)

    # Colonna Navy a sinistra con bordo oro
    c_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c_layer)
    c_pts = [(0, header_h), (cut_w, header_h)]
    for y in range(0, body_h + 1, 10):
        prog = y / float(body_h)
        x_val = int(cut_w * (1 - 0.35 * prog) + 25 * math.sin(prog * math.pi * 2))
        c_pts.append((x_val, header_h + y))
    c_pts.extend([(0, H), (0, header_h)])
    cd.polygon(c_pts, fill=(15, 23, 42, 255))
    for i in range(len(c_pts) - 3):
        cd.line([c_pts[i+1], c_pts[i+2]], fill=(212, 168, 83, 255), width=4)
    canvas.paste(c_layer, (0, 0), c_layer)

    # Logo su header bianco
    _paste_logo_protetto(canvas, 45, 45, max_w=320, max_h=75, with_plate=False)

    draw = ImageDraw.Draw(canvas)

    # Pillola fluttuante con checkmark dorato • VENDE •
    pill_w, pill_h = 420, 68
    px, py = W - pill_w - 40, header_h + 40
    draw.rounded_rectangle([(px, py), (px + pill_w, py + pill_h)], radius=34, fill=(255, 255, 255, 250), outline=(212, 168, 83), width=3)
    draw.ellipse([(px + 10, py + 10), (px + 58, py + 58)], fill=(15, 23, 42))
    draw_vector_check(draw, px + 34, py + 34, size=22, color=(212, 168, 83, 255), width=3)
    draw.text((px + 74, py + 18), "• VENDE •", font=get_font(28, bold=True, font_type="sans"), fill=(15, 23, 42))

    # Icone vettoriali pure nella colonna sinistra
    mq_txt = _extract_story_field_mq(media_info)
    prezzo_txt = _extract_story_field_prezzo(media_info)
    icons_data = [
        (draw_vector_ruler_sqm, mq_txt),
        (draw_vector_sofa, "5 Vani"),
        (draw_vector_shower, "2 Bagni"),
        (draw_vector_laundry, "Ascensore")
    ]
    start_iy = header_h + 120
    for idx, (fn, lbl) in enumerate(icons_data):
        cy = start_iy + idx * 110
        cx = 95
        draw.ellipse([(cx - 28, cy - 28), (cx + 28, cy + 28)], fill=(30, 41, 59), outline=(212, 168, 83), width=2)
        fn(draw, cx, cy, size=24, color=(255, 255, 255))
        draw.text((cx + 42, cy - 12), lbl, font=get_font(18, bold=True, font_type="sans"), fill=(255, 255, 255))

    # Box Prezzo dorato
    p_box_y = start_iy + 4 * 110 + 30
    draw.rounded_rectangle([(25, p_box_y), (cut_w - 20, p_box_y + 90)], radius=14, fill=(212, 168, 83, 230))
    draw.text((40, p_box_y + 12), "PREZZO:", font=get_font(15, bold=True, font_type="sans"), fill=(15, 23, 42))
    draw.text((40, p_box_y + 36), prezzo_txt, font=get_font(30, bold=True, font_type="sans"), fill=(15, 23, 42))

    # Card Bianca Descrittiva (Colonna F)
    card_w = int(W * 0.70)
    card_h = 360
    cx = W - card_w - 40
    cy = H - card_h - 50
    draw.rounded_rectangle([(cx, cy), (cx + card_w, cy + card_h)], radius=22, fill=(255, 255, 255, 250), outline=(212, 168, 83, 160), width=2)
    draw.polygon([(cx + 20, cy + 25), (cx + 35, cy + 37), (cx + 20, cy + 50)], fill=(15, 23, 42))
    draw.text((cx + 45, cy + 24), _extract_story_field_titolo(media_info).upper()[:30], font=get_font(20, bold=True, font_type="sans"), fill=(15, 23, 42))

    col_f_text = _extract_story_field_colonna_f(media_info)
    lines = textwrap.wrap(f"“{col_f_text}”", width=34)
    txt_y = cy + 70
    for l in lines[:5]:
        draw.text((cx + 25, txt_y), l, font=get_font(21, bold=False, font_type="sans"), fill=(30, 41, 59))
        txt_y += 32

    draw.line([(cx + 25, cy + card_h - 55), (cx + card_w - 25, cy + card_h - 55)], fill=(226, 232, 240), width=1)
    draw.text((cx + 25, cy + card_h - 42), "📍 " + _extract_story_field_zona(media_info), font=get_font(18, bold=True, font_type="sans"), fill=(15, 23, 42))
    draw.text((cx + card_w - 250, cy + card_h - 42), "— Immobiliare Giancani", font=get_font(18, bold=True, font_type="sans"), fill=(212, 168, 83))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path

# --- 2. MARTEDÌ: METROQUADRO NOIR & ICONE (LUXURY BLACK & ROYAL GOLD) ---
def crea_story_daily_martedi_metroquadro(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_martedi_metroquadro_{uuid.uuid4().hex[:6]}.png")
    
    canvas = get_clean_property_photo(media_info, (W, H)).convert("RGBA")

    # Gradiente nero/bordeaux sfumato dal 35% in giù
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    mid_y = int(H * 0.35)
    for y in range(mid_y, H):
        ratio = (y - mid_y) / float(H - mid_y)
        alpha = int(255 * (ratio ** 1.35))
        gd.line([(0, y), (W, y)], fill=(18, 16, 14, alpha))
    canvas = Image.alpha_composite(canvas, grad)

    draw = ImageDraw.Draw(canvas)

    # Logo in alto protetto
    _paste_logo_protetto(canvas, 50, 50, max_w=340, max_h=85, with_plate=True)

    # Badge Oro "• VENDE •"
    badge_w, badge_h = 320, 75
    bx, by = W - badge_w - 50, 55
    draw.rounded_rectangle([(bx, by), (bx + badge_w, by + badge_h)], radius=18, fill=(201, 163, 94, 245), outline=(255, 255, 255, 220), width=2)
    draw.text((bx + 35, by + 18), "• VENDE •", font=get_font(32, bold=True, font_type="sans"), fill=(18, 16, 14))

    # Testo Colonna F in evidenza
    start_y = int(H * 0.48)
    draw.text((60, start_y), "DESCRIZIONE IMMOBILE (COLONNA F)", font=get_font(20, bold=True, font_type="sans"), fill=(201, 163, 94))
    draw.text((60, start_y + 35), _extract_story_field_titolo(media_info)[:35], font=get_font(38, bold=True, font_type="sans"), fill=(255, 255, 255))

    col_f_text = _extract_story_field_colonna_f(media_info)
    lines = textwrap.wrap(f"“{col_f_text}”", width=36)
    cur_y = start_y + 95
    for l in lines[:5]:
        draw.text((60, cur_y), l, font=get_font(26, bold=False, font_type="sans"), fill=(240, 240, 245))
        cur_y += 40

    # 4 Icone line art vettoriali orizzontali
    icon_y = cur_y + 80
    mq_txt = _extract_story_field_mq(media_info)
    icons = [
        (draw_vector_ruler_sqm, mq_txt),
        (draw_vector_sofa, "5 Vani"),
        (draw_vector_shower, "2 Bagni"),
        (draw_vector_laundry, "Lavanderia")
    ]
    col_w = W // len(icons)
    for i, (fn_draw, label) in enumerate(icons):
        cx = i * col_w + col_w // 2
        draw.ellipse([(cx - 38, icon_y - 38), (cx + 38, icon_y + 38)], fill=(30, 26, 22, 220), outline=(201, 163, 94), width=2)
        fn_draw(draw, cx, icon_y, size=34, color=(201, 163, 94))
        tw = draw.textlength(label, font=get_font(17, bold=True, font_type="sans"))
        draw.text((cx - tw // 2, icon_y + 48), label, font=get_font(17, bold=True, font_type="sans"), fill=(255, 255, 255))

    # Prezzo e Card Branding Finale
    card_y = H - 180
    draw.rounded_rectangle([(50, card_y), (W - 50, card_y + 120)], radius=20, fill=(255, 255, 255, 250), outline=(201, 163, 94), width=3)
    draw.text((80, card_y + 24), "PREZZO RICHIESTO:", font=get_font(18, bold=True, font_type="sans"), fill=(100, 100, 100))
    draw.text((80, card_y + 54), _extract_story_field_prezzo(media_info), font=get_font(42, bold=True, font_type="sans"), fill=(18, 16, 14))
    
    draw.text((W - 460, card_y + 42), "— Immobiliare Giancani", font=get_font(26, bold=True, font_type="sans"), fill=(185, 28, 28))
    draw.text((W - 460, card_y + 76), "Corso Vittorio Veneto 151, Favara", font=get_font(17, bold=False, font_type="sans"), fill=(60, 60, 60))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path

# --- 3. MERCOLEDÌ: PROFESSIONECASA (SIDEBAR ROSSA & CHEVRON) ---
def crea_story_daily_mercoledi_professionecasa(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_mercoledi_profcase_{uuid.uuid4().hex[:6]}.png")
    
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    side_w = int(W * 0.20)
    
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, 0), (side_w, H)], fill=(200, 16, 46, 255))

    # Foto a tutta altezza a destra
    body_w = W - side_w
    photo_crop = photo.crop((W - body_w, 0, W, H))
    canvas.paste(photo_crop, (side_w, 0))

    # Icone vettoriali nella sidebar
    mq_txt = _extract_story_field_mq(media_info)
    side_icons = [
        (draw_vector_ruler_sqm, "METRI QUADRI", mq_txt.split()[0]),
        (draw_vector_sofa, "VANI", "5"),
        (draw_vector_shower, "BAGNI", "2"),
        (draw_vector_laundry, "SERVIZI", "SI")
    ]
    step_y = H // 5
    for i, (fn_draw, lbl, val) in enumerate(side_icons, start=1):
        cy = i * step_y
        cx = side_w // 2
        draw.ellipse([(cx - 36, cy - 36), (cx + 36, cy + 36)], fill=(160, 10, 35), outline=(255, 255, 255, 230), width=2)
        fn_draw(draw, cx, cy - 8, size=30, color=(255, 255, 255))
        draw.text((cx, cy + 42), val, font=get_font(18, bold=True, font_type="sans"), fill=(255, 255, 255), anchor="mt")
        draw.text((cx, cy + 64), lbl, font=get_font(12, bold=False, font_type="sans"), fill=(255, 220, 220), anchor="mt")

    # Header: Logo protetto e Badge VENDE
    _paste_logo_protetto(canvas, side_w + 35, 45, max_w=340, max_h=80, with_plate=True)

    badge_w = 280
    draw.rounded_rectangle([(W - badge_w - 40, 45), (W - 40, 125)], radius=16, fill=(200, 16, 46, 250), outline=(255, 255, 255), width=2)
    draw.text((W - badge_w - 40 + 35, 65), "• VENDE •", font=get_font(32, bold=True, font_type="sans"), fill=(255, 255, 255))

    # Card bianca descrittiva in basso con chevron
    card_w = int(body_w * 0.88)
    card_h = 420
    card_x = side_w + (body_w - card_w) // 2
    card_y = H - card_h - 50

    draw.rounded_rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], radius=24, fill=(255, 255, 255, 250), outline=(200, 16, 46, 120), width=3)
    draw.polygon([(card_x + 25, card_y + 30), (card_x + 45, card_y + 45), (card_x + 25, card_y + 60)], fill=(200, 16, 46))
    draw.text((card_x + 55, card_y + 32), _extract_story_field_titolo(media_info).upper()[:30], font=get_font(22, bold=True, font_type="sans"), fill=(200, 16, 46))

    col_f_text = _extract_story_field_colonna_f(media_info)
    lines = textwrap.wrap(f"“{col_f_text}”", width=34)
    c_y = card_y + 85
    for l in lines[:5]:
        draw.text((card_x + 35, c_y), l, font=get_font(22, bold=False, font_type="sans"), fill=(31, 41, 55))
        c_y += 34

    draw.line([(card_x + 35, card_y + card_h - 75), (card_x + card_w - 35, card_y + card_h - 75)], fill=(229, 231, 235), width=2)
    draw.text((card_x + 35, card_y + card_h - 55), "PREZZO: " + _extract_story_field_prezzo(media_info), font=get_font(26, bold=True, font_type="sans"), fill=(200, 16, 46))
    draw.text((card_x + card_w - 270, card_y + card_h - 55), "— Immobiliare Giancani", font=get_font(20, bold=True, font_type="sans"), fill=(31, 41, 55))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path

# --- 4. GIOVEDÌ: ELITE FROSTED GLASS (ALTO CITAZIONE & BASSO BRANDING) ---
def crea_story_daily_giovedi_frosted_glass(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_giovedi_frosted_{uuid.uuid4().hex[:6]}.png")
    
    canvas = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 1. Card citazione in ALTO con bordo oro zecchino
    card_left = 60
    card_right = W - 60
    q_top = 90

    col_f_text = _extract_story_field_colonna_f(media_info)
    lines = textwrap.wrap(f"“{col_f_text}”", width=32)
    h_quote = len(lines[:5]) * 46 + 180
    q_bottom = q_top + h_quote

    draw.rounded_rectangle([(card_left, q_top), (card_right, q_bottom)], radius=32, fill=(10, 15, 24, 230), outline="#FFD700", width=3)
    draw.text((W // 2, q_top + 35), "◆ IMMOBILIARE GIANCANI VENDE ◆", font=get_font(28, bold=True, font_type="sans"), fill="#FFD700", anchor="mt")

    curr_y = q_top + 100
    for l in lines[:5]:
        draw.text((W // 2 + 1, curr_y + 1), l, font=get_font(25, bold=False, font_type="sans"), fill=(0, 0, 0, 180), anchor="mt")
        draw.text((W // 2, curr_y), l, font=get_font(25, bold=False, font_type="sans"), fill="#FFFFFF", anchor="mt")
        curr_y += 44

    curr_y += 10
    mq_txt = _extract_story_field_mq(media_info)
    prezzo_txt = _extract_story_field_prezzo(media_info)
    draw.text((W // 2, curr_y), f"{_extract_story_field_zona(media_info)} • {mq_txt} • {prezzo_txt}", font=get_font(22, bold=True, font_type="sans"), fill="#FFD700", anchor="mt")

    # 2. Banner branding in BASSO
    banner_h = 160
    banner_y = H - banner_h - 90
    draw.rounded_rectangle([(card_left, banner_y), (card_right, banner_y + banner_h)], radius=28, fill=(10, 15, 24, 230), outline="#FFD700", width=2)

    canvas = Image.alpha_composite(canvas, overlay)

    _paste_logo_protetto(canvas, card_left + 25, banner_y + 35, max_w=320, max_h=85, with_plate=True)

    b_draw = ImageDraw.Draw(canvas)
    text_x = card_left + 380
    b_draw.text((text_x, banner_y + 40), "IMMOBILIARE GIANCANI", font=get_font(30, bold=True, font_type="sans"), fill="#FFFFFF")
    b_draw.text((text_x, banner_y + 85), "ESCLUSIVA • SICUREZZA • VALORE", font=get_font(20, bold=False, font_type="sans"), fill="#FFD700")

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path

# --- 5. VENERDÌ: ARCO ARCHITETTONICO (SMERALDO & MENTA) ---
def crea_story_daily_venerdi_arco_architettonico(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_venerdi_arco_{uuid.uuid4().hex[:6]}.png")
    
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = Image.new("RGBA", (W, H), (6, 78, 59, 255))
    
    arch_margin = 60
    arch_top = 220
    arch_bottom = H - 380
    arch_w = W - 2 * arch_margin
    arch_radius = arch_w // 2

    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.pieslice([(arch_margin, arch_top), (W - arch_margin, arch_top + 2 * arch_radius)], 180, 0, fill=255)
    md.rectangle([(arch_margin, arch_top + arch_radius), (W - arch_margin, arch_bottom)], fill=255)

    canvas.paste(photo, (0, 0), mask)

    draw = ImageDraw.Draw(canvas)
    draw.arc([(arch_margin - 4, arch_top - 4), (W - arch_margin + 4, arch_top + 2 * arch_radius + 4)], 180, 0, fill=(52, 211, 153), width=4)
    draw.line([(arch_margin - 4, arch_top + arch_radius), (arch_margin - 4, arch_bottom)], fill=(52, 211, 153), width=4)
    draw.line([(W - arch_margin + 4, arch_top + arch_radius), (W - arch_margin + 4, arch_bottom)], fill=(52, 211, 153), width=4)
    draw.line([(arch_margin - 4, arch_bottom), (W - arch_margin + 4, arch_bottom)], fill=(52, 211, 153), width=4)

    _paste_logo_protetto(canvas, (W - 320) // 2, 60, max_w=320, max_h=80, with_plate=True)

    # Medaglione VENDE sulla chiave dell'arco
    med_w, med_h = 340, 70
    mx = (W - med_w) // 2
    my = arch_top + arch_radius - 35
    draw.rounded_rectangle([(mx, my), (mx + med_w, my + med_h)], radius=35, fill=(6, 78, 59, 245), outline=(52, 211, 153), width=3)
    draw.text((W // 2, my + 18), "• VENDE •", font=get_font(28, bold=True, font_type="sans"), fill=(255, 255, 255), anchor="mt")

    # Card inferiore con Colonna F
    card_y = H - 340
    draw.rounded_rectangle([(arch_margin, card_y), (W - arch_margin, card_y + 280)], radius=24, fill=(255, 255, 255, 248), outline=(52, 211, 153), width=2)
    
    draw.text((arch_margin + 35, card_y + 24), _extract_story_field_titolo(media_info).upper()[:28], font=get_font(22, bold=True, font_type="sans"), fill=(6, 78, 59))
    draw.text((W - arch_margin - 160, card_y + 24), _extract_story_field_prezzo(media_info), font=get_font(26, bold=True, font_type="sans"), fill=(6, 78, 59))

    col_f_text = _extract_story_field_colonna_f(media_info)
    lines = textwrap.wrap(f"“{col_f_text}”", width=36)
    c_y = card_y + 70
    for l in lines[:4]:
        draw.text((arch_margin + 35, c_y), l, font=get_font(20, bold=False, font_type="sans"), fill=(30, 41, 59))
        c_y += 30

    mq_txt = _extract_story_field_mq(media_info)
    draw.line([(arch_margin + 35, card_y + 215), (W - arch_margin - 35, card_y + 215)], fill=(229, 231, 235), width=1)
    draw.text((arch_margin + 35, card_y + 230), f"📍 {_extract_story_field_zona(media_info)} • {mq_txt}", font=get_font(18, bold=True, font_type="sans"), fill=(6, 78, 59))
    draw.text((W - arch_margin - 260, card_y + 230), "— Immobiliare Giancani", font=get_font(18, bold=True, font_type="sans"), fill=(5, 150, 105))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path

# --- 6. SABATO: GABETTI DIAGONAL (BORDEAUX & CHAMPAGNE) ---
def crea_story_daily_sabato_gabetti_diagonal(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_sabato_gabetti_{uuid.uuid4().hex[:6]}.png")
    
    canvas = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    poly_top = [(0, 0), (W, 0), (W, 280), (0, 390)]
    od.polygon(poly_top, fill=(74, 4, 4, 245))
    od.line([(0, 390), (W, 280)], fill=(253, 230, 138), width=5)

    poly_bottom = [(0, H - 460), (W, H - 350), (W, H), (0, H)]
    od.polygon(poly_bottom, fill=(74, 4, 4, 250))
    od.line([(0, H - 460), (W, H - 350)], fill=(253, 230, 138), width=5)

    canvas = Image.alpha_composite(canvas, overlay)

    _paste_logo_protetto(canvas, 45, 60, max_w=320, max_h=80, with_plate=True)

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([(W - 360, 65), (W - 45, 145)], radius=16, fill=(253, 230, 138), outline=(255, 255, 255), width=2)
    draw.text((W - 360 + 35, 85), "• VENDE •", font=get_font(32, bold=True, font_type="sans"), fill=(74, 4, 4))

    f_y = H - 410
    draw.text((60, f_y), _extract_story_field_titolo(media_info).upper()[:28], font=get_font(28, bold=True, font_type="sans"), fill=(253, 230, 138))
    draw.text((W - 240, f_y), _extract_story_field_prezzo(media_info), font=get_font(34, bold=True, font_type="sans"), fill="#FFFFFF")

    col_f_text = _extract_story_field_colonna_f(media_info)
    lines = textwrap.wrap(f"“{col_f_text}”", width=38)
    cur_y = f_y + 55
    for l in lines[:4]:
        draw.text((60, cur_y), l, font=get_font(22, bold=False, font_type="sans"), fill=(255, 255, 255))
        cur_y += 34

    mq_txt = _extract_story_field_mq(media_info)
    draw.line([(60, H - 100), (W - 60, H - 100)], fill=(253, 230, 138, 120), width=1)
    draw.text((60, H - 75), f"📐 {mq_txt} • 5 Vani", font=get_font(20, bold=True, font_type="sans"), fill=(253, 230, 138))
    draw.text((W - 320, H - 75), "— Immobiliare Giancani", font=get_font(22, bold=True, font_type="sans"), fill="#FFFFFF")

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path

# --- 7. DOMENICA: MINIMAL PASSEPARTOUT A BLOCCHI (TERRACOTTA & AMBRA) ---
def crea_story_daily_domenica_minimal_terracotta(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_domenica_terracotta_{uuid.uuid4().hex[:6]}.png")
    
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = Image.new("RGBA", (W, H), (255, 251, 235, 255))
    draw = ImageDraw.Draw(canvas)

    p_x1, p_y1 = 60, 240
    p_x2, p_y2 = W - 60, H - 460
    pw, ph = p_x2 - p_x1, p_y2 - p_y1

    fw, fh = photo.size
    scale = max(pw / fw, ph / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    photo_res = photo.resize((nw, nh), Image.Resampling.LANCZOS)
    photo_c = photo_res.crop(((nw - pw)//2, (nh - ph)//2, (nw - pw)//2 + pw, (nh - ph)//2 + ph))

    p_mask = Image.new("L", (pw, ph), 0)
    pm_draw = ImageDraw.Draw(p_mask)
    pm_draw.rounded_rectangle([(0, 0), (pw, ph)], radius=24, fill=255)
    canvas.paste(photo_c, (p_x1, p_y1), p_mask)

    draw.rounded_rectangle([(p_x1 - 3, p_y1 - 3), (p_x2 + 3, p_y2 + 3)], radius=26, outline=(124, 45, 18), width=3)

    _paste_logo_protetto(canvas, 60, 60, max_w=340, max_h=85, with_plate=False)

    b_w = 340
    draw.rounded_rectangle([(W - b_w - 60, 60), (W - 60, 140)], radius=20, fill=(124, 45, 18), outline=(245, 158, 11), width=2)
    draw.text((W - b_w - 60 + 35, 80), "• VENDE •", font=get_font(32, bold=True, font_type="sans"), fill=(255, 251, 235))

    b_y1 = H - 420
    draw.rounded_rectangle([(60, b_y1), (W - 60, H - 70)], radius=24, fill=(124, 45, 18, 255), outline=(245, 158, 11), width=2)

    draw.text((95, b_y1 + 25), _extract_story_field_titolo(media_info).upper()[:28], font=get_font(24, bold=True, font_type="sans"), fill=(245, 158, 11))
    draw.text((W - 280, b_y1 + 25), _extract_story_field_prezzo(media_info), font=get_font(34, bold=True, font_type="sans"), fill=(255, 255, 255))

    col_f_text = _extract_story_field_colonna_f(media_info)
    lines = textwrap.wrap(f"“{col_f_text}”", width=36)
    c_y = b_y1 + 75
    for l in lines[:4]:
        draw.text((95, c_y), l, font=get_font(22, bold=False, font_type="sans"), fill=(255, 251, 235))
        c_y += 34

    mq_txt = _extract_story_field_mq(media_info)
    draw.line([(95, H - 145), (W - 95, H - 145)], fill=(245, 158, 11, 140), width=1)
    draw.text((95, H - 120), f"📍 {_extract_story_field_zona(media_info)} • {mq_txt}", font=get_font(20, bold=True, font_type="sans"), fill=(245, 158, 11))
    draw.text((W - 350, H - 120), "— Immobiliare Giancani", font=get_font(20, bold=True, font_type="sans"), fill=(255, 255, 255))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path





# --- 8. TWILIGHT PENTHOUSE (BLU ZAFFIRO NOTTE & RAME ROSATO) ---
def crea_story_daily_twilight_penthouse(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_twilight_penthouse_{uuid.uuid4().hex[:6]}.png")
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = photo.copy()
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    # Vetrata fumé scuro superiore con sfumatura ramata
    grad_top = Image.new("RGBA", (W, 260), (11, 19, 43, 235))
    overlay.paste(grad_top, (0, 0))

    # Box inferiore in vetro scuro con cornice rame (#E07A5F)
    card_y = H - 450
    draw_ov.rounded_rectangle([(40, card_y), (W - 40, H - 50)], radius=26, fill=(11, 19, 43, 240), outline=(224, 122, 95), width=3)

    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    _paste_logo_protetto(canvas, 50, 50, max_w=320, max_h=80, with_plate=True)

    # Badge Rame "• VENDE •"
    b_w = 320
    draw.rounded_rectangle([(W - b_w - 50, 50), (W - 50, 130)], radius=18, fill=(224, 122, 95, 245), outline=(255, 255, 255), width=2)
    draw.text((W - b_w - 50 + 40, 70), "• VENDE •", font=get_font(32, bold=True, font_type="sans"), fill=(255, 255, 255))

    titolo = _extract_story_field_titolo(media_info)
    prezzo = _extract_story_field_prezzo(media_info)
    col_f = _extract_story_field_colonna_f(media_info)
    mq = _extract_story_field_mq(media_info)
    zona = _extract_story_field_zona(media_info)

    draw.text((75, card_y + 30), titolo.upper()[:32], font=get_font(26, bold=True, font_type="sans"), fill=(224, 122, 95))
    draw.text((W - 250, card_y + 30), prezzo, font=get_font(34, bold=True, font_type="sans"), fill="#FFFFFF")

    lines = textwrap.wrap(f"“{col_f}”", width=36)
    c_y = card_y + 85
    for l in lines[:4]:
        draw.text((75, c_y), l, font=get_font(22, bold=False, font_type="sans"), fill=(240, 245, 255))
        c_y += 34

    draw.line([(75, H - 125), (W - 75, H - 125)], fill=(224, 122, 95, 120), width=1)
    draw.text((75, H - 100), f"📍 {zona} • {mq}", font=get_font(20, bold=True, font_type="sans"), fill=(224, 122, 95))
    draw.text((W - 320, H - 100), "— Immobiliare Giancani", font=get_font(20, bold=True, font_type="sans"), fill="#FFFFFF")

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


# --- 9. TECH CARD MODERN (GRIGIO ANTRACITE & CIANO ELETTRICO) ---
def crea_story_daily_tech_card_modern(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_tech_card_{uuid.uuid4().hex[:6]}.png")
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = photo.copy()
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    # Floating Card Superiore asimmetrica
    draw_ov.rounded_rectangle([(40, 40), (W - 40, 160)], radius=20, fill=(15, 23, 42, 235), outline=(6, 182, 212), width=2)
    
    # Floating Card Inferiore High-Tech
    card_y = H - 460
    draw_ov.rounded_rectangle([(40, card_y), (W - 40, H - 50)], radius=24, fill=(15, 23, 42, 240), outline=(6, 182, 212), width=3)
    
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    _paste_logo_protetto(canvas, 60, 58, max_w=300, max_h=75, with_plate=True)

    # Badge Tech Ciano
    draw.rounded_rectangle([(W - 340, 58), (W - 60, 140)], radius=14, fill=(6, 182, 212), outline=(255, 255, 255), width=2)
    draw.text((W - 340 + 35, 76), "• VENDE •", font=get_font(32, bold=True, font_type="sans"), fill=(15, 23, 42))

    titolo = _extract_story_field_titolo(media_info)
    prezzo = _extract_story_field_prezzo(media_info)
    col_f = _extract_story_field_colonna_f(media_info)
    mq = _extract_story_field_mq(media_info)

    draw.text((75, card_y + 30), "OPPORTUNITÀ IMMOBILIARE GIANCANI", font=get_font(18, bold=True, font_type="sans"), fill=(6, 182, 212))
    draw.text((75, card_y + 60), titolo[:30], font=get_font(32, bold=True, font_type="sans"), fill="#FFFFFF")

    lines = textwrap.wrap(f"“{col_f}”", width=36)
    c_y = card_y + 115
    for l in lines[:4]:
        draw.text((75, c_y), l, font=get_font(22, bold=False, font_type="sans"), fill=(226, 232, 240))
        c_y += 34

    draw.line([(75, H - 130), (W - 75, H - 130)], fill=(6, 182, 212, 100), width=1)
    draw.text((75, H - 105), f"PREZZO: {prezzo} • {mq}", font=get_font(22, bold=True, font_type="sans"), fill=(6, 182, 212))
    draw.text((W - 320, H - 105), "— Immobiliare Giancani", font=get_font(20, bold=True, font_type="sans"), fill="#FFFFFF")

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


# --- 10. MEDITERRANEAN COASTAL (TURCHESE LAGUNA & SABBIA DORATA) ---
def crea_story_daily_mediterranean_coastal(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_mediterranean_coastal_{uuid.uuid4().hex[:6]}.png")
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = Image.new("RGBA", (W, H), (8, 145, 178, 255)) # Turchese mare

    # Foto incorniciata ad onde morbide
    p_x1, p_y1 = 50, 190
    p_x2, p_y2 = W - 50, H - 420
    pw, ph = p_x2 - p_x1, p_y2 - p_y1

    fw, fh = photo.size
    scale = max(pw / fw, ph / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    photo_res = photo.resize((nw, nh), Image.Resampling.LANCZOS)
    photo_c = photo_res.crop(((nw - pw)//2, (nh - ph)//2, (nw - pw)//2 + pw, (nh - ph)//2 + ph))

    p_mask = Image.new("L", (pw, ph), 0)
    pm_draw = ImageDraw.Draw(p_mask)
    pm_draw.rounded_rectangle([(0, 0), (pw, ph)], radius=32, fill=255)
    canvas.paste(photo_c, (p_x1, p_y1), p_mask)

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([(p_x1 - 3, p_y1 - 3), (p_x2 + 3, p_y2 + 3)], radius=34, outline=(245, 158, 11), width=4)

    _paste_logo_protetto(canvas, (W - 320) // 2, 50, max_w=320, max_h=80, with_plate=True)

    # Badge Pillola Sabbia Dorata
    b_w = 340
    draw.rounded_rectangle([(W - b_w) // 2, p_y1 - 30, (W + b_w) // 2, p_y1 + 35], radius=32, fill=(245, 158, 11), outline=(255, 255, 255), width=2)
    draw.text((W // 2, p_y1 - 12), "• VENDE •", font=get_font(28, bold=True, font_type="sans"), fill=(15, 23, 42), anchor="mt")

    titolo = _extract_story_field_titolo(media_info)
    prezzo = _extract_story_field_prezzo(media_info)
    col_f = _extract_story_field_colonna_f(media_info)
    mq = _extract_story_field_mq(media_info)
    zona = _extract_story_field_zona(media_info)

    # Card inferiore Sabbia Calda / Bianco
    card_y = H - 380
    draw.rounded_rectangle([(50, card_y), (W - 50, H - 50)], radius=24, fill=(255, 255, 255, 250), outline=(245, 158, 11), width=2)
    
    draw.text((85, card_y + 25), titolo.upper()[:30], font=get_font(24, bold=True, font_type="sans"), fill=(8, 145, 178))
    draw.text((W - 250, card_y + 25), prezzo, font=get_font(30, bold=True, font_type="sans"), fill=(8, 145, 178))

    lines = textwrap.wrap(f"“{col_f}”", width=36)
    c_y = card_y + 70
    for l in lines[:4]:
        draw.text((85, c_y), l, font=get_font(21, bold=False, font_type="sans"), fill=(30, 41, 59))
        c_y += 32

    draw.line([(85, H - 115), (W - 85, H - 115)], fill=(229, 231, 235), width=1)
    draw.text((85, H - 95), f"📍 {zona} • {mq}", font=get_font(19, bold=True, font_type="sans"), fill=(8, 145, 178))
    draw.text((W - 340, H - 95), "— Immobiliare Giancani", font=get_font(20, bold=True, font_type="sans"), fill=(245, 158, 11))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


# --- 11. VOGUE REAL ESTATE EDITORIAL (COPERTINA PATINATA & ORO) ---
def crea_story_daily_vogue_editorial(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_vogue_editorial_{uuid.uuid4().hex[:6]}.png")
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = photo.copy()
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    pad = 40
    draw_ov.rectangle([(pad, pad), (W - pad, H - pad)], outline=(212, 175, 55, 220), width=3)
    draw_ov.rectangle([(pad + 8, pad + 8), (W - pad - 8, H - pad - 8)], outline=(255, 255, 255, 120), width=1)

    for y in range(H - 520, H - pad):
        factor = (y - (H - 520)) / 520.0
        draw_ov.line([(pad, y), (W - pad, y)], fill=(10, 10, 12, int(240 * factor)))

    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    _paste_logo_protetto(canvas, 65, 65, max_w=320, max_h=80, with_plate=True)

    # Badge Vogue "• ESCLUSIVA VENDE •"
    draw.rounded_rectangle([(W - 390, 65), (W - 65, 135)], radius=12, fill=(212, 175, 55), outline=(255, 255, 255), width=2)
    draw.text((W - 390 + 30, 82), "• ESCLUSIVA VENDE •", font=get_font(24, bold=True, font_type="sans"), fill=(10, 10, 12))

    titolo = _extract_story_field_titolo(media_info)
    prezzo = _extract_story_field_prezzo(media_info)
    col_f = _extract_story_field_colonna_f(media_info)
    mq = _extract_story_field_mq(media_info)
    zona = _extract_story_field_zona(media_info)

    t_y = H - 460
    draw.text((70, t_y), "IMMOBILIARE GIANCANI PRESENTA", font=get_font(18, bold=True, font_type="sans"), fill=(212, 175, 55))
    draw.text((70, t_y + 35), titolo.upper()[:30], font=get_font(34, bold=True, font_type="sans"), fill="#FFFFFF")

    lines = textwrap.wrap(f"“{col_f}”", width=36)
    c_y = t_y + 90
    for l in lines[:4]:
        draw.text((70, c_y), l, font=get_font(22, bold=False, font_type="sans"), fill=(245, 245, 250))
        c_y += 34

    draw.line([(70, H - 110), (W - 70, H - 110)], fill=(212, 175, 55, 160), width=2)
    draw.text((70, H - 85), f"{prezzo} • {mq} • {zona}", font=get_font(22, bold=True, font_type="sans"), fill=(212, 175, 55))
    draw.text((W - 340, H - 85), "— Immobiliare Giancani", font=get_font(22, bold=True, font_type="sans"), fill="#FFFFFF")

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


# --- 12. DIAMOND PRESTIGE (ROMBO GEOMETRICO & PLATINO) ---
def crea_story_daily_diamond_prestige(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_diamond_prestige_{uuid.uuid4().hex[:6]}.png")
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = Image.new("RGBA", (W, H), (24, 24, 27, 255)) # Carbone scuro
    
    cx, cy = W // 2, int(H * 0.44)
    rx, ry = 460, 420
    
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    diamond_pts = [(cx, cy - ry), (cx + rx, cy), (cx, cy + ry), (cx - rx, cy)]
    md.polygon(diamond_pts, fill=255)

    canvas.paste(photo, (0, 0), mask)

    draw = ImageDraw.Draw(canvas)
    draw.polygon(diamond_pts, outline=(228, 228, 231), width=5)
    draw.polygon([(cx, cy - ry - 8), (cx + rx + 8, cy), (cx, cy + ry + 8), (cx - rx - 8, cy)], outline=(56, 189, 248), width=2)

    _paste_logo_protetto(canvas, (W - 320) // 2, 55, max_w=320, max_h=80, with_plate=True)

    # Badge Diamante VENDE
    b_w = 320
    draw.rounded_rectangle([(W - b_w) // 2, cy - ry - 35, (W + b_w) // 2, cy - ry + 35], radius=20, fill=(24, 24, 27), outline=(56, 189, 248), width=3)
    draw.text((W // 2, cy - ry - 16), "• VENDE •", font=get_font(28, bold=True, font_type="sans"), fill=(56, 189, 248), anchor="mt")

    titolo = _extract_story_field_titolo(media_info)
    prezzo = _extract_story_field_prezzo(media_info)
    col_f = _extract_story_field_colonna_f(media_info)
    mq = _extract_story_field_mq(media_info)

    card_y = H - 390
    draw.rounded_rectangle([(50, card_y), (W - 50, H - 50)], radius=24, fill=(39, 39, 42, 245), outline=(228, 228, 231), width=2)

    draw.text((80, card_y + 25), titolo.upper()[:30], font=get_font(26, bold=True, font_type="sans"), fill=(56, 189, 248))
    draw.text((W - 240, card_y + 25), prezzo, font=get_font(32, bold=True, font_type="sans"), fill="#FFFFFF")

    lines = textwrap.wrap(f"“{col_f}”", width=36)
    c_y = card_y + 75
    for l in lines[:4]:
        draw.text((80, c_y), l, font=get_font(21, bold=False, font_type="sans"), fill=(244, 244, 245))
        c_y += 32

    draw.line([(80, H - 115), (W - 80, H - 115)], fill=(113, 113, 122), width=1)
    draw.text((80, H - 95), f"📐 {mq}", font=get_font(20, bold=True, font_type="sans"), fill=(56, 189, 248))
    draw.text((W - 320, H - 95), "— Immobiliare Giancani", font=get_font(20, bold=True, font_type="sans"), fill="#FFFFFF")

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


# --- 13. COUNTRY CHIC SAGE (VERDE SALVIA & LINO TERRACOTTA) ---
def crea_story_daily_country_chic_sage(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_country_chic_sage_{uuid.uuid4().hex[:6]}.png")
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = Image.new("RGBA", (W, H), (63, 98, 18, 255)) # Verde Salvia d'olivo

    p_x1, p_y1 = 60, 210
    p_x2, p_y2 = W - 60, H - 420
    pw, ph = p_x2 - p_x1, p_y2 - p_y1

    fw, fh = photo.size
    scale = max(pw / fw, ph / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    photo_res = photo.resize((nw, nh), Image.Resampling.LANCZOS)
    photo_c = photo_res.crop(((nw - pw)//2, (nh - ph)//2, (nw - pw)//2 + pw, (nh - ph)//2 + ph))

    p_mask = Image.new("L", (pw, ph), 0)
    pm_draw = ImageDraw.Draw(p_mask)
    pm_draw.rounded_rectangle([(0, 0), (pw, ph)], radius=28, fill=255)
    canvas.paste(photo_c, (p_x1, p_y1), p_mask)

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([(p_x1 - 3, p_y1 - 3), (p_x2 + 3, p_y2 + 3)], radius=30, outline=(254, 243, 199), width=3)

    _paste_logo_protetto(canvas, 60, 55, max_w=320, max_h=80, with_plate=True)

    # Badge Salvia & Terracotta
    b_w = 320
    draw.rounded_rectangle([(W - b_w - 60, 55), (W - 60, 135)], radius=18, fill=(254, 243, 199), outline=(63, 98, 18), width=2)
    draw.text((W - b_w - 60 + 35, 75), "• VENDE •", font=get_font(32, bold=True, font_type="sans"), fill=(63, 98, 18))

    titolo = _extract_story_field_titolo(media_info)
    prezzo = _extract_story_field_prezzo(media_info)
    col_f = _extract_story_field_colonna_f(media_info)
    mq = _extract_story_field_mq(media_info)
    zona = _extract_story_field_zona(media_info)

    card_y = H - 380
    draw.rounded_rectangle([(60, card_y), (W - 60, H - 50)], radius=24, fill=(254, 243, 199, 252), outline=(163, 230, 53), width=2)

    draw.text((95, card_y + 25), titolo.upper()[:30], font=get_font(24, bold=True, font_type="sans"), fill=(63, 98, 18))
    draw.text((W - 260, card_y + 25), prezzo, font=get_font(30, bold=True, font_type="sans"), fill=(63, 98, 18))

    lines = textwrap.wrap(f"“{col_f}”", width=36)
    c_y = card_y + 70
    for l in lines[:4]:
        draw.text((95, c_y), l, font=get_font(21, bold=False, font_type="sans"), fill=(40, 50, 30))
        c_y += 32

    draw.line([(95, H - 115), (W - 95, H - 115)], fill=(217, 249, 157), width=2)
    draw.text((95, H - 95), f"🌿 {zona} • {mq}", font=get_font(20, bold=True, font_type="sans"), fill=(63, 98, 18))
    draw.text((W - 350, H - 95), "— Immobiliare Giancani", font=get_font(20, bold=True, font_type="sans"), fill=(185, 28, 28))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


# --- 14. CINEMATIC HERO WIDESCREEN (GOLD ANAMORPHIC) ---
def crea_story_daily_cinematic_hero(media_info, palette=None, output_path=None):
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_cinematic_hero_{uuid.uuid4().hex[:6]}.png")
    photo = get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    canvas = photo.copy()
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    # Maschera cinematografica con bande scure in alto e in basso
    draw_ov.rectangle([(0, 0), (W, 220)], fill=(0, 0, 0, 215))
    draw_ov.rectangle([(0, H - 460), (W, H)], fill=(0, 0, 0, 230))
    
    # Linee dorate di taglio anamorfico
    draw_ov.line([(0, 220), (W, 220)], fill=(212, 175, 55), width=3)
    draw_ov.line([(0, H - 460), (W, H - 460)], fill=(212, 175, 55), width=3)

    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    _paste_logo_protetto(canvas, 50, 55, max_w=320, max_h=80, with_plate=True)

    # Hero Badge Centrale "• IMMOBILIARE GIANCANI VENDE •"
    b_w = 460
    draw.rounded_rectangle([(W - b_w - 50, 55), (W - 50, 135)], radius=18, fill=(212, 175, 55), outline=(255, 255, 255), width=2)
    draw.text((W - b_w - 50 + 25, 75), "• GIANCANI VENDE •", font=get_font(28, bold=True, font_type="sans"), fill=(15, 23, 42))

    titolo = _extract_story_field_titolo(media_info)
    prezzo = _extract_story_field_prezzo(media_info)
    col_f = _extract_story_field_colonna_f(media_info)
    mq = _extract_story_field_mq(media_info)
    zona = _extract_story_field_zona(media_info)

    f_y = H - 420
    draw.text((60, f_y), titolo.upper()[:32], font=get_font(30, bold=True, font_type="sans"), fill=(212, 175, 55))
    draw.text((W - 240, f_y), prezzo, font=get_font(34, bold=True, font_type="sans"), fill="#FFFFFF")

    lines = textwrap.wrap(f"“{col_f}”", width=38)
    cur_y = f_y + 55
    for l in lines[:4]:
        draw.text((60, cur_y), l, font=get_font(22, bold=False, font_type="sans"), fill=(255, 255, 255))
        cur_y += 34

    draw.line([(60, H - 110), (W - 60, H - 110)], fill=(212, 175, 55, 120), width=1)
    draw.text((60, H - 85), f"📍 {zona} • {mq}", font=get_font(20, bold=True, font_type="sans"), fill=(212, 175, 55))
    draw.text((W - 320, H - 85), "— Immobiliare Giancani", font=get_font(22, bold=True, font_type="sans"), fill="#FFFFFF")

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=95)
    return output_path


def crea_story_9_16(media_info, style="auto", palette=None, output_path=None, day_of_week=None):
    """
    Dispatcher Principale Storie 9:16 (1080x1920) con Rotazione tra 14 Stili Master.
    - 1. C&B Curved Wave (Navy Blue & Oro Caldo)
    - 2. Metroquadro Noir & Icone Vettoriali (Luxury Black & Royal Gold)
    - 3. ProfessioneCasa Left Sidebar (Rosso Corsa Prestige)
    - 4. Elite Frosted Glass Card in Alto (Charcoal Fumé & Oro Zecchino)
    - 5. Arco Architettonico Galleria (Verde Smeraldo Bosco & Menta)
    - 6. Gabetti Dynamic Diagonal (Bordeaux Riserva & Oro Champagne)
    - 7. Minimal Passepartout a Blocchi (Terracotta Sunset & Ambra)
    - 8. Twilight Penthouse (Blu Zaffiro Notte & Rame Rosato)
    - 9. Tech Card Modern (Grigio Antracite & Ciano Elettrico)
    - 10. Mediterranean Coastal (Turchese Laguna & Sabbia Dorata)
    - 11. Vogue Real Estate (Copertina Patinata & Oro Antico)
    - 12. Diamond Prestige (Rombo Platino & Carbone)
    - 13. Country Chic Sage (Verde Salvia d'Olivo & Lino Crema)
    - 14. Cinematic Hero Widescreen (Gold Anamorphic & Nero Cinema)
    — Immobiliare Giancani
    """
    import datetime
    if day_of_week is None:
        day_of_week = datetime.datetime.now().weekday()
    else:
        try:
            day_of_week = int(day_of_week)
        except Exception:
            day_of_week = datetime.datetime.now().weekday()

    slot_30m = int(time.time() / 1800)
    if media_info and isinstance(media_info, dict):
        s_idx = media_info.get("story_index") or media_info.get("slot_index")
        if s_idx is not None:
            try:
                slot_30m = int(s_idx)
            except Exception:
                pass

    if palette is None:
        palette = get_palette_del_giorno(day_of_week, slot_idx=slot_30m)

    stili_14 = [
        "daily_lunedi",               # 1
        "daily_martedi",              # 2
        "daily_mercoledi",            # 3
        "daily_giovedi",              # 4
        "daily_venerdi",              # 5
        "daily_sabato",               # 6
        "daily_domenica",             # 7
        "twilight_penthouse",         # 8
        "tech_card_modern",           # 9
        "mediterranean_coastal",      # 10
        "vogue_editorial",            # 11
        "diamond_prestige",           # 12
        "country_chic_sage",          # 13
        "cinematic_hero"              # 14
    ]

    style_clean = str(style).lower().strip() if style else "auto"

    if style_clean in ("auto", "daily", "giorno", "settimanale", "rotazione"):
        # Rotazione tra i 14 stili basata sul giorno e sullo slot orario da 30 minuti
        chosen_idx = (day_of_week * 2 + (slot_30m % 2)) % 14
        style_clean = stili_14[chosen_idx]

    # Dispatcher 14 Stili Master
    # 1. C&B Curved Wave
    if style_clean in ("daily_lunedi", "lunedi", "cb_curved_wave", "cb", "curved_wave", "onda_curva"):
        return crea_story_daily_lunedi_cb_curved_wave(media_info, palette=palette, output_path=output_path)
    # 2. Metroquadro Noir
    elif style_clean in ("daily_martedi", "martedi", "metroquadro_gradient", "metroquadro", "gradient_specs", "sfumato"):
        return crea_story_daily_martedi_metroquadro(media_info, palette=palette, output_path=output_path)
    # 3. ProfessioneCasa
    elif style_clean in ("daily_mercoledi", "mercoledi", "professionecasa_sidebar", "professionecasa", "red_sidebar"):
        return crea_story_daily_mercoledi_professionecasa(media_info, palette=palette, output_path=output_path)
    # 4. Frosted Glass
    elif style_clean in ("daily_giovedi", "giovedi", "frosted_glass", "mindset", "luxury_glass", "glass"):
        return crea_story_daily_giovedi_frosted_glass(media_info, palette=palette, output_path=output_path)
    # 5. Arco Architettonico
    elif style_clean in ("daily_venerdi", "venerdi", "arco_architettonico", "arco", "galleria", "smeraldo"):
        return crea_story_daily_venerdi_arco_architettonico(media_info, palette=palette, output_path=output_path)
    # 6. Gabetti Diagonal
    elif style_clean in ("daily_sabato", "sabato", "gabetti_diagonal", "gabetti", "diagonal_ribbon", "nastro_diagonale"):
        return crea_story_daily_sabato_gabetti_diagonal(media_info, palette=palette, output_path=output_path)
    # 7. Minimal Terracotta
    elif style_clean in ("daily_domenica", "domenica", "minimal_terracotta", "terracotta", "passepartout"):
        return crea_story_daily_domenica_minimal_terracotta(media_info, palette=palette, output_path=output_path)
    # 8. Twilight Penthouse
    elif style_clean in ("twilight_penthouse", "twilight", "penthouse", "rame"):
        return crea_story_daily_twilight_penthouse(media_info, palette=palette, output_path=output_path)
    # 9. Tech Card Modern
    elif style_clean in ("tech_card_modern", "tech_card", "tech", "ciano"):
        return crea_story_daily_tech_card_modern(media_info, palette=palette, output_path=output_path)
    # 10. Mediterranean Coastal
    elif style_clean in ("mediterranean_coastal", "mediterranean", "coastal", "mare", "turchese"):
        return crea_story_daily_mediterranean_coastal(media_info, palette=palette, output_path=output_path)
    # 11. Vogue Editorial
    elif style_clean in ("vogue_editorial", "vogue", "copertina", "oro_antico"):
        return crea_story_daily_vogue_editorial(media_info, palette=palette, output_path=output_path)
    # 12. Diamond Prestige
    elif style_clean in ("diamond_prestige", "diamond", "rombo", "platino"):
        return crea_story_daily_diamond_prestige(media_info, palette=palette, output_path=output_path)
    # 13. Country Chic Sage
    elif style_clean in ("country_chic_sage", "country_chic", "sage", "salvia"):
        return crea_story_daily_country_chic_sage(media_info, palette=palette, output_path=output_path)
    # 14. Cinematic Hero
    elif style_clean in ("cinematic_hero", "cinematic", "anamorphic", "cinema"):
        return crea_story_daily_cinematic_hero(media_info, palette=palette, output_path=output_path)
    
    # Fallback su stili secondari storici
    elif style_clean in ("card_live", "storia_live", "live_screenshot", "live_card_screenshot"):
        return crea_card_storia_live_screenshot_9_16(media_info, palette=palette, output_path=output_path, usa_palette_bg=True)
    elif style_clean in ("cam_hero_badge", "cam", "hero_badge"):
        return crea_story_cam_hero_badge_9_16(media_info, palette=palette, output_path=output_path)
    elif style_clean in ("tempocasa_multiphoto", "tempocasa"):
        return crea_story_tempocasa_multiphoto_9_16(media_info, palette=palette, output_path=output_path)
    elif style_clean in ("capellupo_sidebar", "capellupo"):
        return crea_story_capellupo_sidebar_9_16(media_info, palette=palette, output_path=output_path)
    elif style_clean in ("marketing_banner", "marketing"):
        return crea_story_marketing_banner_9_16(media_info, palette=palette, output_path=output_path)
    elif style_clean in ("split_screen", "split"):
        return crea_story_splitscreen_9_16(media_info, palette=palette, output_path=output_path)
    else:
        # Default di garanzia
        return crea_story_daily_lunedi_cb_curved_wave(media_info, palette=palette, output_path=output_path)


def crea_flyer_1_1(media_info, style="auto", palette=None, output_path=None, day_of_week=None):
    slot_30m = int(time.time() / 1800)
    if media_info and isinstance(media_info, dict):
        s_idx = media_info.get("story_index") or media_info.get("slot_index")
        if s_idx is not None:
            try:
                slot_30m = int(s_idx)
            except Exception:
                pass

    if palette is None:
        palette = get_palette_del_giorno(day_of_week, slot_idx=slot_30m)

    stili_disponibili = [
        "cb_curved_wave",
        "metroquadro_gradient",
        "professionecasa_sidebar",
        "cam_hero_badge",
        "tempocasa_multiphoto",
        "gabetti_diagonal",
        "capellupo_sidebar",
        "malfatti_sidebar",
        "scheda_curva",
        "cornice_minimal",
        "zero24_card",
        "tecnocasa_gazzetta",
        "card_live",
        "storia_live",
    ]

    if not style or style == "auto":
        style = stili_disponibili[slot_30m % len(stili_disponibili)]

    style = style.lower().strip()

    if style in ("cb_curved_wave", "cb", "curved_wave", "onda_curva"):
        return crea_flyer_cb_curved_wave_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("professionecasa_sidebar", "professionecasa", "red_sidebar"):
        return crea_flyer_professionecasa_sidebar_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("metroquadro_gradient", "metroquadro", "gradient_specs", "sfumato"):
        return crea_flyer_metroquadro_gradient_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("cam_hero_badge", "cam", "hero_badge", "floating_badge"):
        return crea_flyer_cam_hero_badge_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("tempocasa_multiphoto", "tempocasa", "multiphoto_specs", "in_vendita"):
        return crea_flyer_tempocasa_multiphoto_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("capellupo_sidebar", "capellupo", "sidebar_card"):
        return crea_flyer_capellupo_sidebar_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("gabetti_diagonal", "gabetti", "diagonal_ribbon"):
        return crea_flyer_gabetti_diagonal_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("malfatti_sidebar", "malfatti", "sidebar_invendita", "in_vendita_sidebar"):
        return crea_flyer_malfatti_sidebar_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("scheda_curva", "curva", "istituzionale", "scheda_curva_prestigio", "asta"):
        return crea_flyer_scheda_curva_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("cornice_minimal", "cornice", "sigillo", "minimal_frame", "fine_art"):
        return crea_flyer_cornice_minimal_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("zero24_card", "zero24", "studiozero24", "teal_card", "modern_card"):
        return crea_flyer_zero24_card_1_1(media_info, palette=palette, output_path=output_path)
    elif style in ("tecnocasa_gazzetta",
        "card_live",
        "storia_live", "tecnocasa_grid", "grid_4foto", "occasione"):
        return crea_flyer_tecnocasa_gazzetta_1_1(media_info, palette=palette, output_path=output_path)
    else:
        return crea_flyer_cb_curved_wave_1_1(media_info, palette=palette, output_path=output_path)



