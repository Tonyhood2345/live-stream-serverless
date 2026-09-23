#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import io
import uuid
import random
import re
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from story_publisher.config import ASSETS_DIR, SCRATCH_DIR, CACHE_IMMOBILI_DIR, GUARANTEED_FALLBACK_IMAGES, BRAND_NAME, BRAND_CLAIM
from story_publisher.system.env import get_font
from story_publisher.system.network import scarica_foto_url, is_image_valid_and_not_black
from story_publisher.core.compliance import normalize_mq, format_personal_branding
from story_publisher.graphics.primitives import draw_skyline, draw_circular_badge, calcola_prezzo_barrato, draw_fitted_text
from story_publisher.graphics.logo_handler import get_clean_logo

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

    avail_desc_h = (bbar_y - 20) - (ty + 85)
    draw_fitted_text(draw, testo_f, (50, ty + 85, W - 100, avail_desc_h), max_font_size=18, min_font_size=12, line_spacing=4, fill=(51, 65, 85, 255))

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

    avail_desc_h = (bbar_y - 20) - (ty + 105)
    draw_fitted_text(draw, testo_f, (fx, ty + 105, fw, avail_desc_h), max_font_size=22, min_font_size=13, line_spacing=5, fill=(51, 65, 85, 255))

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

