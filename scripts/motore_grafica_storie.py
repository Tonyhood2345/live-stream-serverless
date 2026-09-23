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
    0: {  # Lunedì
        "id": "navy_blue",
        "nome": "Navy Blue & Crisp White",
        "giorno": "Lunedì",
        "primary_dark": (10, 25, 47, 255),       # #0A192F
        "primary_mid": (30, 58, 138, 255),       # #1E3A8A
        "primary_light": (14, 165, 233, 255),    # #0EA5E9
        "accent": (245, 158, 11, 255),           # #F59E0B Oro caldo
        "accent_light": (254, 243, 199, 255),
        "badge_bg": (245, 158, 11, 240),
        "badge_txt": (15, 23, 42, 255),
        "footer_bg": (10, 25, 47, 255),
        "footer_diag": (15, 35, 65, 255),
        "card_bg": (15, 23, 42, 220),
        "border_color": (30, 58, 138, 180),
        "text_primary": (255, 255, 255, 255),
        "text_secondary": (203, 213, 225, 255),
        "btn_cta_bg": (220, 38, 38, 255),        # Rosso vivo per CTA o accento
        "bottom_bar_bg": (255, 255, 255, 255),
        "bottom_bar_txt": (15, 23, 42, 255)
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

def get_palette_del_giorno(day_of_week=None):
    """
    Restituisce la palette cromatica associata in modo sistematico al giorno corrente
    (oppure a day_of_week 0..6 se specificato).
    """
    if day_of_week is None:
        try:
            from datetime import datetime, timezone, timedelta
            rome_tz = timezone(timedelta(hours=2))
            day_of_week = datetime.now(rome_tz).weekday()
        except Exception:
            day_of_week = datetime.datetime.now().weekday()
    day_idx = int(day_of_week) % 7
    return PALETTE_GIORNALIERE.get(day_idx, PALETTE_GIORNALIERE[0])

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
            # Di default l'annuncio mattutino/pomeridiano punta alla diretta serale delle 19:00
            orario_diretta = "19:00"

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
            orario_diretta = "19:00"

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
# 🎯 6. DISPATCHER GENERATORE UNIFICATO (10 stili + card diretta)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_9_16(media_info, style="auto", palette=None, output_path=None, day_of_week=None):
    if palette is None:
        palette = get_palette_del_giorno(day_of_week)

    stili_disponibili = [
        "gabetti_diagonal",
        "capellupo_sidebar",
        "marketing_banner",
        "split_screen",
        "luxury_glass",
        "editorial",
        "room_label",
        "ideacasa_layout",
        "casait_card",
        "tecnocasa_multi",
    ]

    if not style or style == "auto":
        slot_30m = int(time.time() / 1800)
        style = stili_disponibili[slot_30m % len(stili_disponibili)]

    style = style.lower().strip()

    if style in ("gabetti_diagonal", "gabetti", "diagonal_ribbon", "nastro_diagonale"):
        return crea_story_gabetti_diagonal_9_16(media_info, palette=palette, output_path=output_path)
    elif style in ("capellupo_sidebar", "capellupo", "sidebar_card", "scheda_laterale"):
        return crea_story_capellupo_sidebar_9_16(media_info, palette=palette, output_path=output_path)
    elif style in ("marketing_banner", "marketing", "banner"):
        return crea_story_marketing_banner_9_16(media_info, palette=palette, output_path=output_path)
    elif style in ("split_screen", "split"):
        return crea_story_splitscreen_9_16(media_info, palette=palette, output_path=output_path)
    elif style in ("luxury_glass", "luxury", "glass"):
        return crea_story_luxury_glass_9_16(media_info, palette=palette, output_path=output_path)
    elif style in ("editorial", "minimal"):
        return crea_story_editorial_9_16(media_info, palette=palette, output_path=output_path)
    elif style in ("room_label", "room", "ambiente"):
        return crea_story_room_label_9_16(media_info, palette=palette, output_path=output_path)
    elif style in ("ideacasa_layout", "ideacasa", "idea_casa"):
        return crea_story_ideacasa_layout_9_16(media_info, palette=palette, output_path=output_path)
    elif style in ("casait_card", "casait", "card"):
        return crea_story_casait_card_9_16(media_info, palette=palette, output_path=output_path)
    elif style in ("tecnocasa_multi", "tecnocasa", "multi"):
        return crea_story_tecnocasa_multi_9_16(media_info, palette=palette, output_path=output_path)
    elif style in ("annuncio_diretta", "diretta", "live_card"):
        return crea_card_annuncio_diretta_9_16(media_info, palette=palette, output_path=output_path)
    else:
        return crea_story_gabetti_diagonal_9_16(media_info, palette=palette, output_path=output_path)


