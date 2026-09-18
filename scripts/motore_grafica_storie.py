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
    font_titolo = get_font(32, bold=True, font_type="sans")
    font_localita = get_font(22, bold=True, font_type="sans")
    font_sub = get_font(16, bold=False, font_type="sans")

    tit_clean = titolo if len(titolo) <= 32 else titolo[:30] + "..."
    draw.text((text_area_x, 48), tit_clean, font=font_titolo, fill=palette["text_primary"])
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

    # Box Caratteristiche
    caratt_x = rif_x + rif_w + 30
    caratt_y = diag_start_y + 20
    caratt_w = W - caratt_x - 45

    font_caratt_title = get_font(24, bold=True, font_type="sans")
    draw.text((caratt_x, caratt_y + 15), "CARATTERISTICHE PRINCIPALI", font=font_caratt_title, fill=palette["accent"])
    draw.line([(caratt_x, caratt_y + 54), (caratt_x + caratt_w, caratt_y + 54)], fill=palette["accent"], width=2)

    amenities = [
        "• Ampio ingresso accogliente & living",
        "• Soggiorno spazioso e luminoso",
        "• Cucina abitabile rifinita nei dettagli",
        "• 2 Bagni moderni con sanitari di pregio",
        "• Camere da letto ampie e confortevoli",
        "• Balconi vivibili con vista panoramica",
        "• Climatizzazione autonoma & infissi termici",
        "• Zona tranquilla e ben servita da tutti i servizi"
    ]

    font_amenity = get_font(19, bold=False, font_type="sans")
    amy = caratt_y + 75
    for am in amenities:
        draw.text((caratt_x, amy), am, font=font_amenity, fill=(255, 255, 255, 255))
        amy += 44

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

    contacts_txt = "📞 Tel: 0922 123456 • 📱 Cell: 340 1234567 • Corso Vittorio Veneto, Favara (AG)"
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
    font_zn = get_font(21, bold=True, font_type="sans")
    font_desc = get_font(21, bold=False, font_type="sans")

    draw.text((box_x + 35, info_y), titolo[:34], font=font_tit, fill=palette["primary_dark"][:3])
    draw.text((box_x + 35, info_y + 45), f"📍 {zona}", font=font_zn, fill=palette["primary_mid"][:3])

    p_box_w = 260
    draw.rounded_rectangle([box_x + 35, info_y + 90, box_x + 35 + p_box_w, info_y + 145], radius=10, fill=palette["badge_bg"])
    draw.text((box_x + 50, info_y + 102), prezzo, font=get_font(24, bold=True, font_type="sans"), fill=palette["badge_txt"])

    draw.rounded_rectangle([box_x + 35 + p_box_w + 20, info_y + 90, box_x + box_w - 35, info_y + 145], radius=10, fill=(240, 243, 248, 255), outline=palette["border_color"], width=1)
    draw.text((box_x + 35 + p_box_w + 35, info_y + 104), f"📐 {mq}", font=get_font(20, bold=True, font_type="sans"), fill=palette["primary_dark"][:3])

    testo_f = str(media_info.get('testoF', 'Immobile di alto profilo con finiture di pregio, ampi spazi luminosi e vista aperta. — Immobiliare Giancani'))
    lines = [testo_f[i:i+48] for i in range(0, min(len(testo_f), 240), 48)]
    dy = info_y + 175
    for l in lines[:4]:
        draw.text((box_x + 35, dy), l, font=font_desc, fill=(50, 60, 75, 255))
        dy += 34

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
    draw.text((card_x + 35, dy), titolo[:32], font=get_font(32, bold=True, font_type="sans"), fill=(255, 255, 255, 255))
    draw.text((card_x + 35, dy + 48), f"💎 {prezzo} • 📐 {mq}", font=get_font(24, bold=True, font_type="sans"), fill=palette["accent"])

    testo_f = str(media_info.get('testoF', 'Un connubio perfetto tra design contemporaneo, comfort e posizione strategica ad Agrigento e Favara. — Immobiliare Giancani'))
    lines = [testo_f[i:i+46] for i in range(0, min(len(testo_f), 240), 46)]
    ty = dy + 105
    for l in lines[:4]:
        draw.text((card_x + 35, ty), l, font=get_font(20, bold=False, font_type="sans"), fill=(225, 230, 240, 255))
        ty += 34

    btn_w = 700
    btn_h = 68
    btn_x = (W - btn_w) // 2
    btn_y = card_y + card_h - 110
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
    draw.text((60, 105), titolo[:28], font=get_font(38, bold=True, font_type="serif"), fill=palette["primary_dark"][:3])

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
    lines = [testo_f[i:i+46] for i in range(0, min(len(testo_f), 240), 46)]
    dy = sy + 105
    for l in lines[:5]:
        draw.text((60, dy), l, font=get_font(21, bold=False, font_type="sans"), fill=(60, 65, 75, 255))
        dy += 35

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

    font_stanza = get_font(90, bold=True, font_type="sans")
    bbox = draw.textbbox((0, 0), nome_stanza, font=font_stanza)
    tx = (W - (bbox[2] - bbox[0])) // 2
    ty = barra_y + (barra_h - (bbox[3] - bbox[1])) // 2
    draw.text((tx, ty), nome_stanza, font=font_stanza, fill=(255, 255, 255, 255))

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

    HEADER_H = 220  # altezza header
    PHOTO_H  = 1060  # altezza foto centrale (più grande per 9:16)
    FOOTER_H = 430  # altezza footer split
    MARGIN_H = H - HEADER_H - PHOTO_H - FOOTER_H  # margine bianco tra foto e footer

    # ── HEADER ──
    header_color = palette["primary_dark"]
    draw.rectangle([(0, 0), (W, HEADER_H)], fill=header_color)

    logo = get_logo_trasparente_ufficiale(max_w=280, max_h=140)
    if logo:
        lw, lh = logo.size
        ly = (HEADER_H - lh) // 2
        canvas.alpha_composite(logo, (24, ly))

    # Titolo top-right
    font_tit = get_font(56, bold=True, font_type="sans")
    title_text = f"{titolo}\n- {zona}"
    title_x = 330
    title_w = W - title_x - 24
    # Wrapping manuale
    words = title_text.replace("\n", " \n ").split()
    lines_out = []
    current = ""
    for w in words:
        if w == "\n":
            lines_out.append(current.strip())
            current = ""
        else:
            test = (current + " " + w).strip()
            bb = draw.textbbox((0, 0), test, font=font_tit)
            if bb[2] - bb[0] > title_w and current:
                lines_out.append(current.strip())
                current = w
            else:
                current = test
    if current:
        lines_out.append(current.strip())

    total_th = sum(draw.textbbox((0, 0), l, font=font_tit)[3] - draw.textbbox((0, 0), l, font=font_tit)[1] + 8 for l in lines_out)
    ty_start = (HEADER_H - total_th) // 2
    for li, line in enumerate(lines_out):
        bb = draw.textbbox((0, 0), line, font=font_tit)
        draw.text((title_x, ty_start), line, font=font_tit, fill=(255, 255, 255, 255))
        ty_start += (bb[3] - bb[1]) + 8

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
    font_rif_lbl = get_font(42, bold=True, font_type="sans")
    font_rif_num = get_font(90, bold=True, font_type="sans")
    draw.text((30, footer_y + 30), "RIFERIMENTO", font=font_rif_lbl, fill=(255, 255, 255, 255))
    draw.text((30, footer_y + 90), codice_rif.replace("RIF. ", ""), font=font_rif_num, fill=palette["accent"])

    # Lato destro: CARATTERISTICHE
    car_x = mid_x + 80
    font_car_lbl = get_font(44, bold=True, font_type="sans")
    font_car_li  = get_font(34, bold=False, font_type="sans")
    draw.text((car_x, footer_y + 22), "CARATTERISTICHE", font=font_car_lbl, fill=(255, 255, 255, 255))
    half = math.ceil(len(caratteristiche) / 2)
    left_col  = caratteristiche[:half]
    right_col = caratteristiche[half:]
    col2_x = car_x + (W - car_x - 30) // 2
    for i, car in enumerate(left_col):
        y_c = footer_y + 88 + i * 55
        draw.text((car_x, y_c), f"• {car}", font=font_car_li, fill=(255, 255, 255, 255))
    for i, car in enumerate(right_col):
        y_c = footer_y + 88 + i * 55
        draw.text((col2_x, y_c), f"• {car}", font=font_car_li, fill=(255, 255, 255, 255))

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
    font_tit_card = get_font(44, bold=True, font_type="sans")
    max_title_w = CARD_W - 290 - 20
    words_t = titolo.split()
    line1, line2 = "", ""
    for w in words_t:
        test = (line1 + " " + w).strip()
        bb = draw.textbbox((0, 0), test, font=font_tit_card)
        if bb[2] - bb[0] <= max_title_w:
            line1 = test
        else:
            line2 = (line2 + " " + w).strip()
    tx_card = CARD_MARGIN + 290
    draw.text((tx_card, CARD_TOP + 18), line1, font=font_tit_card, fill=(255, 255, 255, 255))
    if line2:
        draw.text((tx_card, CARD_TOP + 68), line2, font=font_tit_card, fill=palette["accent"])
    else:
        draw.text((tx_card, CARD_TOP + 68), zona, font=font_tit_card, fill=palette["accent"])

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

def crea_story_tecnocasa_multi_9_16(media_info, palette=None, output_path=None):
    """Titolo bold grande in alto, foto principale + 2 mini affiancate,
       badge icone, prezzo grande, bottone CTA, footer logo + recapiti."""
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_tecnocasa_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()

    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # Estrai dati da Colonna F (testoF) e campi
    titolo = str(media_info.get("titolo", "IMMOBILE DI PRESTIGIO")).strip().upper()
    zona = str(media_info.get("zona", "FAVARA - AGRIGENTO")).strip().upper()
    prezzo_raw = str(media_info.get("prezzo", "")).strip()
    if prezzo_raw.isdigit():
        prezzo_str = f"€ {int(prezzo_raw):,}".replace(",", ".")
    elif "€" not in prezzo_raw and any(c.isdigit() for c in prezzo_raw):
        prezzo_str = f"€ {prezzo_raw}"
    else:
        prezzo_str = prezzo_raw if prezzo_raw else "Trattativa Riservata"
    mq_str = formatta_metri_quadri(media_info.get("mq", "120"))
    locali = str(media_info.get("locali", "4"))
    testo_f = str(media_info.get("testoF", "")).strip()  # Colonna F
    codice_rif = str(media_info.get("codiceRif", media_info.get("tabName", "RIF. GIANCANI"))).replace("_"," ").upper()

    # ── TITOLO BOLD GRANDE sopra (top 0-480) ──
    TITLE_AREA_H = 480

    # Sfondo bianco + accent line sinistra
    draw.rectangle([(0, 0), (W, TITLE_AREA_H)], fill=(255, 255, 255, 255))
    draw.rectangle([(0, 0), (12, TITLE_AREA_H)], fill=palette["accent"])

    # Titolo in 2-3 righe bold grandi (font ~88 per le prime parole chiave)
    words_title = titolo.split()
    font_big = get_font(96, bold=True, font_type="sans")
    font_med = get_font(64, bold=True, font_type="sans")
    font_sub = get_font(46, bold=False, font_type="sans")

    # Prima riga: prime 2-3 parole in grande
    line_big = " ".join(words_title[:2])
    line_med = " ".join(words_title[2:4]) if len(words_title) > 2 else ""
    line_sub = zona

    ty = 30
    draw.text((40, ty), line_big, font=font_big, fill=palette["primary_dark"])
    ty += draw.textbbox((0, 0), line_big, font=font_big)[3] + 6
    if line_med:
        draw.text((40, ty), line_med, font=font_med, fill=palette["accent"])
        ty += draw.textbbox((0, 0), line_med, font=font_med)[3] + 6
    # Sottotitolo zona + linea divisoria
    draw.text((40, ty), line_sub, font=font_sub, fill=(100, 100, 120))
    ty += draw.textbbox((0, 0), line_sub, font=font_sub)[3] + 10
    draw.line([(40, ty + 4), (W - 40, ty + 4)], fill=palette["accent"], width=4)

    # Badge caratteristiche sopra foto
    ty += 22
    icon_badges = [(f"📐  {mq_str}", "mq"), (f"🛏️  {locali} LOCALI", "locali")]
    font_badge = get_font(40, bold=False, font_type="sans")
    for badge_txt, _ in icon_badges:
        draw.text((40, ty), badge_txt, font=font_badge, fill=palette["primary_dark"])
        ty += 56

    # ── FOTO PRINCIPALE grande (480 - 1120) ──
    MAIN_FOTO_TOP = TITLE_AREA_H
    MAIN_FOTO_H = 640
    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl", "")
    foto_img = None
    try:
        if foto_url.startswith("http"):
            import io as _io
            resp = requests.get(foto_url, timeout=12)
            foto_img = Image.open(_io.BytesIO(resp.content)).convert("RGB")
        elif foto_url and os.path.exists(foto_url):
            foto_img = Image.open(foto_url).convert("RGB")
    except Exception:
        pass

    draw.rectangle([(0, MAIN_FOTO_TOP), (W, MAIN_FOTO_TOP + MAIN_FOTO_H)], fill=(190, 190, 200))
    if foto_img:
        fw, fh = foto_img.size
        scale = max(W / fw, MAIN_FOTO_H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        foto_img = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - W) // 2
        oy = (nh - MAIN_FOTO_H) // 2
        canvas.paste(foto_img.crop((ox, oy, ox + W, oy + MAIN_FOTO_H)), (0, MAIN_FOTO_TOP))

    # ── 2 FOTO MINI affiancate ──
    MINI_TOP = MAIN_FOTO_TOP + MAIN_FOTO_H + 12
    MINI_H = 310
    MINI_W = (W - 36) // 2
    # Per demo usiamo la stessa foto scalata diversamente
    for i in range(2):
        mx = 12 + i * (MINI_W + 12)
        draw.rounded_rectangle([(mx, MINI_TOP), (mx + MINI_W, MINI_TOP + MINI_H)],
                                radius=16, fill=(200, 200, 210))
        if foto_img:
            try:
                thumb = foto_img.copy()
                tw, th = thumb.size
                scale2 = max(MINI_W / tw, MINI_H / th)
                nw2, nh2 = int(tw * scale2), int(th * scale2)
                thumb = thumb.resize((nw2, nh2), Image.LANCZOS)
                # offset diverso per variare
                ox2 = (nw2 - MINI_W) // 2
                oy2 = (nh2 - MINI_H) // 2 + i * 50
                oy2 = max(0, min(oy2, nh2 - MINI_H))
                mini_crop = thumb.crop((ox2, oy2, ox2 + MINI_W, oy2 + MINI_H))
                # mask arrotondata
                mask = Image.new("L", (MINI_W, MINI_H), 0)
                ImageDraw.Draw(mask).rounded_rectangle([(0,0),(MINI_W,MINI_H)], radius=16, fill=255)
                mini_rgba = mini_crop.convert("RGBA")
                mini_rgba.putalpha(mask)
                canvas.alpha_composite(mini_rgba, (mx, MINI_TOP))
            except Exception:
                pass

    # ── PREZZO GRANDE + Badge icone feature ──
    PRICE_TOP = MINI_TOP + MINI_H + 24
    font_price_lbl = get_font(36, bold=False, font_type="sans")
    font_price_big = get_font(90, bold=True, font_type="sans")
    draw.text((40, PRICE_TOP), "PREZZO", font=font_price_lbl, fill=(130, 130, 150))
    draw.text((40, PRICE_TOP + 46), prezzo_str, font=font_price_big, fill=palette["primary_dark"])

    # Feature badges orizzontali
    testo_f_short = testo_f[:80] if testo_f else "Posizione esclusiva · Vista panoramica · Finiture di pregio"
    feat_list = [f.strip() for f in re.split(r"[\n|•;]", testo_f_short) if f.strip()][:3]
    FEAT_TOP = PRICE_TOP + 166
    feat_bar_h = 68
    feat_w = (W - 48) // max(len(feat_list), 1)
    font_feat = get_font(30, bold=False, font_type="sans")
    for i, feat in enumerate(feat_list):
        fx = 12 + i * (feat_w + 12)
        draw.rounded_rectangle([(fx, FEAT_TOP), (fx + feat_w, FEAT_TOP + feat_bar_h)],
                                radius=34, outline=palette["primary_dark"][:3] + (200,), width=3,
                                fill=(248, 248, 255))
        bb = draw.textbbox((0, 0), feat, font=font_feat)
        tx = fx + (feat_w - (bb[2]-bb[0])) // 2
        ty_f = FEAT_TOP + (feat_bar_h - (bb[3]-bb[1])) // 2
        draw.text((tx, ty_f), feat, font=font_feat, fill=palette["primary_dark"])

    # ── BOTTONE CTA ──
    CTA_TOP = FEAT_TOP + feat_bar_h + 28
    CTA_H = 120
    CTA_W = W - 80
    draw.rounded_rectangle([(40, CTA_TOP), (40 + CTA_W, CTA_TOP + CTA_H)],
                            radius=60, fill=palette["accent"][:3] + (255,))
    font_cta = get_font(52, bold=True, font_type="sans")
    cta_txt = "▶ CHIEDI FOTO E INFORMAZIONI"
    bb = draw.textbbox((0, 0), cta_txt, font=font_cta)
    draw.text(((W - (bb[2]-bb[0])) // 2, CTA_TOP + (CTA_H - (bb[3]-bb[1])) // 2),
              cta_txt, font=font_cta, fill=(255, 255, 255, 255))

    # ── FOOTER logo + recapiti ──
    FOOTER_TOP = CTA_TOP + CTA_H + 16
    FOOTER_H = H - FOOTER_TOP
    if FOOTER_H < 60:
        FOOTER_H = 60
    draw.rectangle([(0, FOOTER_TOP), (W, H)], fill=palette["primary_dark"])
    logo = get_logo_trasparente_ufficiale(max_w=260, max_h=90)
    if logo:
        lw, lh = logo.size
        canvas.alpha_composite(logo, (24, FOOTER_TOP + (FOOTER_H - lh) // 2))

    font_recapiti = get_font(34, bold=False, font_type="sans")
    recapiti = "📞 0922 123456  |  immobiliaregiancani.it"
    draw.text((320, FOOTER_TOP + 8), "Immobiliare Giancani", font=get_font(38, bold=True), fill=palette["accent"])
    draw.text((320, FOOTER_TOP + 52), recapiti, font=font_recapiti, fill=(220, 220, 230))
    draw.text((W - 300, FOOTER_TOP + 22), codice_rif, font=font_recapiti, fill=(200, 200, 220))

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[TECNOCASA_MULTI] Salvato: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 📡 11. CARD "ANNUNCIO DIRETTA LIVE" — A random ogni 30 minuti (25% prob)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_card_annuncio_diretta_9_16(media_info, orario_diretta=None, palette=None, output_path=None):
    """Card speciale di annuncio diretta live con foto immobile, orario, invito a partecipare.
       Usa i colori del giorno — Immobiliare Giancani."""
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"card_annuncio_diretta_{uuid.uuid4().hex[:6]}.png")
    if not palette:
        palette = get_palette_del_giorno()
    if not orario_diretta:
        now = datetime.datetime.now()
        # Prossima mezz'ora tonda
        minutes = now.minute
        if minutes < 30:
            orario_diretta = now.replace(minute=30, second=0).strftime("%H:%M")
        else:
            orario_diretta = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0).strftime("%H:%M")

    canvas = Image.new("RGBA", (W, H), palette["primary_dark"])
    draw = ImageDraw.Draw(canvas)

    # Sfondo gradiente dinamico
    for y in range(H):
        ratio = y / H
        r = int(palette["primary_dark"][0] * (1 - ratio * 0.5) + palette["primary_mid"][0] * ratio * 0.5)
        g = int(palette["primary_dark"][1] * (1 - ratio * 0.5) + palette["primary_mid"][1] * ratio * 0.5)
        b = int(palette["primary_dark"][2] * (1 - ratio * 0.5) + palette["primary_mid"][2] * ratio * 0.5)
        draw.line([(0, y), (W, y)], fill=(max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b)), 255))

    # ── LIVE badge top ──
    badge_live_w, badge_live_h = 220, 74
    badge_x = (W - badge_live_w) // 2
    badge_y = 60
    draw.rounded_rectangle([(badge_x, badge_y), (badge_x + badge_live_w, badge_y + badge_live_h)],
                            radius=37, fill=(220, 30, 30, 255))
    font_live = get_font(50, bold=True, font_type="sans")
    draw.text((badge_x + 24, badge_y + 10), "● LIVE", font=font_live, fill=(255, 255, 255))

    # Logo Giancani
    logo = get_logo_trasparente_ufficiale(max_w=400, max_h=130)
    if logo:
        lw, lh = logo.size
        canvas.alpha_composite(logo, ((W - lw) // 2, badge_y + badge_live_h + 30))

    # ── Titolo invito ──
    font_invito_big = get_font(88, bold=True, font_type="sans")
    font_invito_med = get_font(58, bold=False, font_type="sans")
    inv_y = badge_y + badge_live_h + 200

    testo_invito_lines = ["UNISCITI ALLA", "DIRETTA STREAMING!"]
    for line in testo_invito_lines:
        bb = draw.textbbox((0, 0), line, font=font_invito_big)
        draw.text(((W - (bb[2]-bb[0])) // 2, inv_y), line, font=font_invito_big, fill=(255, 255, 255, 255))
        inv_y += (bb[3]-bb[1]) + 14

    # ── Orario ──
    font_orario_lbl = get_font(48, bold=False, font_type="sans")
    font_orario_big = get_font(160, bold=True, font_type="sans")
    draw.text(((W - draw.textbbox((0,0), "Entriamo LIVE alle:", font=font_orario_lbl)[2]) // 2,
               inv_y + 20), "Entriamo LIVE alle:", font=font_orario_lbl, fill=(220, 220, 240))
    inv_y += 80
    bb_ora = draw.textbbox((0, 0), orario_diretta, font=font_orario_big)
    draw.text(((W - (bb_ora[2]-bb_ora[0])) // 2, inv_y), orario_diretta,
              font=font_orario_big, fill=palette["accent"])
    inv_y += (bb_ora[3]-bb_ora[1]) + 20

    # ── Foto immobile circolare (o rettangolare arrotondata) ──
    FOTO_TOP = inv_y + 20
    FOTO_SIDE = 600
    FOTO_X = (W - FOTO_SIDE) // 2

    foto_url = media_info.get("fotoUrl") or media_info.get("mediaUrl", "")
    foto_img = None
    try:
        if foto_url.startswith("http"):
            import io as _io
            resp = requests.get(foto_url, timeout=12)
            foto_img = Image.open(_io.BytesIO(resp.content)).convert("RGB")
        elif foto_url and os.path.exists(foto_url):
            foto_img = Image.open(foto_url).convert("RGB")
    except Exception:
        pass

    # Frame colorato intorno alla foto
    frame_pad = 14
    draw.rounded_rectangle(
        [(FOTO_X - frame_pad, FOTO_TOP - frame_pad),
         (FOTO_X + FOTO_SIDE + frame_pad, FOTO_TOP + FOTO_SIDE + frame_pad)],
        radius=40, fill=palette["accent"][:3] + (255,)
    )

    if foto_img:
        fw, fh = foto_img.size
        scale = max(FOTO_SIDE / fw, FOTO_SIDE / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        foto_img = foto_img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - FOTO_SIDE) // 2
        oy = (nh - FOTO_SIDE) // 2
        foto_crop = foto_img.crop((ox, oy, ox + FOTO_SIDE, oy + FOTO_SIDE))
        # Mask arrotondata
        mask = Image.new("L", (FOTO_SIDE, FOTO_SIDE), 0)
        ImageDraw.Draw(mask).rounded_rectangle([(0,0),(FOTO_SIDE,FOTO_SIDE)], radius=28, fill=255)
        foto_rgba = foto_crop.convert("RGBA")
        foto_rgba.putalpha(mask)
        canvas.alpha_composite(foto_rgba, (FOTO_X, FOTO_TOP))

    # Titolo immobile sotto foto
    titolo = str(media_info.get("titolo", "Immobile Esclusivo")).strip()
    testo_f = str(media_info.get("testoF", "")).strip()  # Colonna F
    font_tit_im = get_font(48, bold=True, font_type="sans")
    bb_tit = draw.textbbox((0, 0), titolo, font=font_tit_im)
    tit_y = FOTO_TOP + FOTO_SIDE + 24
    draw.text(((W - (bb_tit[2]-bb_tit[0])) // 2, tit_y), titolo, font=font_tit_im, fill=(255, 255, 255, 255))

    # Snippet dal testo F (Colonna F) — max 80 caratteri
    snippet = testo_f[:80].strip() + ("…" if len(testo_f) > 80 else "") if testo_f else ""
    if snippet:
        font_snip = get_font(34, bold=False, font_type="sans")
        bb_snip = draw.textbbox((0, 0), snippet, font=font_snip)
        draw.text(((W - (bb_snip[2]-bb_snip[0])) // 2, tit_y + 66), snippet,
                  font=font_snip, fill=(210, 210, 230))

    # ── Brand finale prominente ──
    font_brand = get_font(46, bold=True, font_type="sans")
    brand_txt = "— Immobiliare Giancani —"
    bb_br = draw.textbbox((0, 0), brand_txt, font=font_brand)
    draw.text(((W - (bb_br[2]-bb_br[0])) // 2, H - 80), brand_txt,
              font=font_brand, fill=palette["accent"])

    canvas = canvas.convert("RGB")
    canvas.save(output_path, "PNG", quality=97)
    print(f"[ANNUNCIO_DIRETTA] Salvato: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 6. DISPATCHER GENERATORE UNIFICATO (8 stili + card diretta)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_9_16(media_info, style="auto", palette=None, output_path=None, day_of_week=None):
    if palette is None:
        palette = get_palette_del_giorno(day_of_week)

    stili_disponibili = [
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

    if style in ("marketing_banner", "marketing", "banner"):
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
        return crea_story_marketing_banner_9_16(media_info, palette=palette, output_path=output_path)
