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

    avail_desc_h = (box_y + box_h) - desc_y - 25
    draw_fitted_text(draw, testo_f, (rx, desc_y, rw_usable - 260, avail_desc_h), max_font_size=21, min_font_size=13, line_spacing=5, fill=(51, 65, 85, 255))

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

