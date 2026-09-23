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

    avail_desc_h = (card_y + card_h - 90) - (card_y + 65)
    draw_fitted_text(draw, testo_f, (cx + 30, card_y + 65, cw - 60, avail_desc_h), max_font_size=18, min_font_size=12, line_spacing=4, fill=(203, 213, 225, 255))

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

    avail_desc_h = (card_y + card_h - 130) - (card_y + 95)
    draw_fitted_text(draw, testo_f, (cx + 40, card_y + 95, cw - 80, avail_desc_h), max_font_size=22, min_font_size=13, line_spacing=5, fill=(203, 213, 225, 255))

    btn_txt = "🔴 ENTRA ORA IN DIRETTA A VEDERLA DAL VIVO >" if is_live else "👉 CONTATTACI PER FISSARE UNA VISITA"
    font_cta = get_font(23, bold=True, font_type="sans")
    draw.text((cx + 40, card_y + card_h - 110), btn_txt, font=font_cta, fill=(56, 189, 248, 255))

    font_sign = get_font(28, bold=True, font_type="serif")
    sign_t = "— IMMOBILIARE GIANCANI —"
    sw = font_sign.getbbox(sign_t)[2] - font_sign.getbbox(sign_t)[0]
    draw.text((cx + (cw - sw) // 2, card_y + card_h - 55), sign_t, font=font_sign, fill=(212, 168, 83, 255))

    bg_rgba.save(output_path, "PNG")
    return output_path

