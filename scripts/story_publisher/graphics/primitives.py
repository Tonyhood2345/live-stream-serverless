#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Primitive Vettoriali e Componenti Grafici per Pillow
"""

import math
import random
import re
from PIL import ImageStat
from story_publisher.system.env import get_font

def is_image_valid_and_not_black(image_obj, min_mean=20, min_max=40):
    """Verifica che l'immagine sia valida e non nera/vuota."""
    if not image_obj:
        return False
    try:
        gray = image_obj.convert('L').resize((60, 60))
        stat = ImageStat.Stat(gray)
        mean_b = stat.mean[0]
        ext_min, ext_max = gray.getextrema()
        if mean_b < min_mean or ext_max < min_max:
            return False
        return True
    except Exception:
        return False

def draw_skyline(draw, y_base, width, color=(148, 163, 184, 180)):
    """Disegna una skyline stilizzata di tetti e palazzi italiani lungo il margine inferiore."""
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
    """Disegna un badge circolare line-art con etichetta sotto."""
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
    """Calcola un prezzo originario barrato realistico (+25-30%) se non specificato."""
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

def draw_fitted_text(draw, text, box, max_font_size=28, min_font_size=14, font_type="sans",
                     fill=(30, 41, 59, 255), bold=False, line_spacing=6, align="left"):
    """
    Disegna il testo all'interno del box prefissato (x, y, w, h).
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

