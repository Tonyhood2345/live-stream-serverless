#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
NUOVI STILI GRAFICI STORIE 9:16 (1080x1920) — IMMOBILIARE GIANCANI
═══════════════════════════════════════════════════════════════════════════════
Stili ispirati alle grafiche top-performing di settore:
1. UNA CASA, TANTE ESIGENZE (Living Hero + 3 Pillole Esigenze + Card Contatti Sagomata + Onda Cursiva)
2. AL TUO FIANCO, PASSO DOPO PASSO (3 Step Assistenza + Plastico / Rogito Hero + Card Contattaci)
3. I NOSTRI SERVIZI A 360° (Griglia 6 Card Servizi con Icone + Banner + CTA WhatsApp)
4. EFFETTO CALAMITA / PORTFOLIO MULTI-FOTO (Griglia 4 Card Immobili con Ribbon Status + Calamita)

Tutti gli stili si adattano automaticamente:
- Al Logo Ufficiale Trasparente Immobiliare Giancani
- Alla Palette Cromatica del Giorno (cambia ogni giorno / ad ogni storia)
- Ai dati e testi estratti rigorosamente dalla Colonna F
- Personal branding: "— Immobiliare Giancani"
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import uuid
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import motore_grafica_storie as mgs

SCRATCH_DIR = os.path.join(BASE_DIR, "scratch")
os.makedirs(SCRATCH_DIR, exist_ok=True)


def _get_daily_colors(palette=None):
    """Estrae i colori principali dal tema del giorno"""
    if not palette:
        palette = mgs.get_palette_del_giorno()
    
    # Colore primario scuro (es. Smeraldo, Navy, Bordeaux, Indigo, Terracotta)
    primary_dark = palette.get("primary_dark") or palette.get("context_color") or (16, 128, 98)
    if len(primary_dark) == 4:
        primary_dark = primary_dark[:3]
        
    # Accento (oro, giallo o tinta coordinata)
    accent = palette.get("accent") or (234, 179, 8)
    if len(accent) == 4:
        accent = accent[:3]
        
    # Colore evidenziatore (es. rosso ribassato o nastro)
    highlight = palette.get("highlight") or (220, 38, 38)
    if len(highlight) == 4:
        highlight = highlight[:3]

    return {
        "primary": primary_dark,
        "accent": accent,
        "highlight": highlight,
        "bg_light": (250, 250, 252),
        "text_dark": (30, 41, 59),
        "text_muted": (100, 116, 139),
        "white": (255, 255, 255)
    }


def _draw_rounded_card(draw, box, radius=24, fill=(255, 255, 255, 255), outline=None, width=1):
    """Disegna un rettangolo arrotondato pulito"""
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _draw_shadow(image, box, radius=24, shadow_color=(0, 0, 0, 70), blur=15, offset=(0, 8)):
    """Aggiunge un'ombra morbida realistica sotto un elemento"""
    x1, y1, x2, y2 = box
    w = (x2 - x1) + blur * 4
    h = (y2 - y1) + blur * 4
    
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)
    s_box = [blur * 2, blur * 2, blur * 2 + (x2 - x1), blur * 2 + (y2 - y1)]
    s_draw.rounded_rectangle(s_box, radius=radius, fill=shadow_color)
    shadow_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(blur))
    
    paste_x = x1 - blur * 2 + offset[0]
    paste_y = y1 - blur * 2 + offset[1]
    image.paste(shadow_blurred, (paste_x, paste_y), shadow_blurred)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. STILE "UNA CASA, TANTE ESIGENZE" (Reference Foto 4 e 5)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_una_casa_tante_esigenze_9_16(media_info, palette=None, output_path=None):
    """
    Stile 'Una Casa, Tante Esigenze':
    - Logo ufficiale Giancani in alto
    - Box sagomato con cornice sottile nel colore del giorno
    - Titolo 'UNA CASA, TANTE ESIGENZE' + sottotitolo 'Ti ascoltiamo e costruiamo un percorso su misura.'
    - 3 Pillole orizzontali: [ 🏠 ACQUISTO ] [ 🏷️ VENDITA ] [ 👤 CONSULENZA ]
    - Living contemporaneo / Villa in grande risalto centrale
    - Card inferiore sagomata nel colore del giorno con CHIAMA ORA 320 1667156 e sede Favara
    - Onda inferiore morbida con firma corsiva 'La tua casa, la nostra passione' e casetta stilizzata
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_esigenze_{uuid.uuid4().hex[:6]}.png")
        
    colors = _get_daily_colors(palette)
    theme_color = colors["primary"]
    
    # 1. Canvas bianco latte / perla elegante
    canvas = Image.new("RGBA", (W, H), (252, 252, 253, 255))
    
    # 2. Foto immobile (Living / Villa ad alta risoluzione)
    photo = mgs.get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    
    # Dimensioni e posizione foto: occupa la porzione medio-bassa
    photo_box_y = 660
    photo_h = 1000
    
    fw, fh = photo.size
    scale = max(W / fw, photo_h / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    photo_res = photo.resize((nw, nh), Image.Resampling.LANCZOS)
    photo_crop = photo_res.crop(((nw - W)//2, (nh - photo_h)//2, (nw - W)//2 + W, (nh - photo_h)//2 + photo_h))
    canvas.paste(photo_crop, (0, photo_box_y))
    
    # Sfumatura morbida in alto sulla foto per fondersi col bianco dello sfondo superiore
    fade_top = Image.new("RGBA", (W, 120), (252, 252, 253, 255))
    fade_mask = Image.new("L", (W, 120))
    for fy in range(120):
        alpha_val = int(255 * (1.0 - fy / 120.0))
        for fx in range(W):
            fade_mask.putpixel((fx, fy), alpha_val)
    canvas.paste(fade_top, (0, photo_box_y), fade_mask)

    draw = ImageDraw.Draw(canvas)

    # 3. Logo ufficiale Giancani centrato in alto
    logo = mgs.get_logo_trasparente_ufficiale(max_w=460, max_h=120)
    if logo:
        lw, lh = logo.size
        lx = (W - lw) // 2
        canvas.paste(logo, (lx, 50), logo)

    # 4. Box con cornice architettonica sottile (in colore del giorno)
    bx1, by1 = 70, 185
    bx2, by2 = W - 70, 505
    frame_w = 4
    
    # Cornice con accento stilizzato
    draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=12, outline=theme_color, width=frame_w)
    
    # Maschera piccola per apertura superiore/inferiore stile architettonico elegante
    draw.rectangle([(bx1 + 100, by1 - 6), (bx2 - 100, by1 + 6)], fill=(252, 252, 253, 255))
    
    # Testo Titolo nel box
    font_titolo = mgs.get_font(64, bold=True, font_type="sans")
    font_sub = mgs.get_font(32, bold=False, font_type="sans")
    
    titolo_r1 = "UNA CASA,"
    titolo_r2 = "TANTE ESIGENZE"
    sub_r1 = "Ti ascoltiamo e costruiamo"
    sub_r2 = "un percorso su misura."
    
    draw.text((W // 2, by1 + 55), titolo_r1, font=font_titolo, fill=theme_color, anchor="mm")
    draw.text((W // 2, by1 + 125), titolo_r2, font=font_titolo, fill=theme_color, anchor="mm")
    draw.text((W // 2, by1 + 215), sub_r1, font=font_sub, fill=(35, 45, 55), anchor="mm")
    draw.text((W // 2, by1 + 258), sub_r2, font=font_sub, fill=(35, 45, 55), anchor="mm")

    # 5. Le 3 Pillole Sagomate Orizzontali: [ 🏠 ACQUISTO ] [ 🏷️ VENDITA ] [ 👤 CONSULENZA ]
    pill_y = 535
    pill_h = 76
    pill_w = 280
    gap = 25
    start_x = (W - (pill_w * 3 + gap * 2)) // 2
    
    pills_data = [
        ("ACQUISTO", "🏠"),
        ("VENDITA", "🏷️"),
        ("CONSULENZA", "👤")
    ]
    
    font_pill = mgs.get_font(28, bold=True, font_type="sans")
    font_ico = mgs.get_font(30, bold=False, font_type="sans")
    
    for idx, (p_text, p_ico) in enumerate(pills_data):
        px1 = start_x + idx * (pill_w + gap)
        px2 = px1 + pill_w
        py1 = pill_y
        py2 = py1 + pill_h
        
        # Ombra morbida sotto la pillola
        _draw_shadow(canvas, (px1, py1, px2, py2), radius=38, shadow_color=(0, 0, 0, 45), blur=8, offset=(0, 4))
        
        # Sfondo pillola in tinta del giorno
        draw.rounded_rectangle([(px1, py1), (px2, py2)], radius=38, fill=theme_color)
        
        # Testo e icona
        full_label = f"{p_ico}  {p_text}"
        draw.text((px1 + pill_w // 2, py1 + pill_h // 2), full_label, font=font_pill, fill=(255, 255, 255), anchor="mm")

    # 6. Card Contatti Sagomata Fluttuante in Basso (Identica alla Reference 5)
    card_w = 840
    card_h = 190
    cx1 = (W - card_w) // 2
    cx2 = cx1 + card_w
    cy1 = 1475
    cy2 = cy1 + card_h
    
    # Ombra pronunciata sotto la card
    _draw_shadow(canvas, (cx1, cy1, cx2, cy2), radius=48, shadow_color=(0, 0, 0, 80), blur=20, offset=(0, 10))
    
    # Sfondo card in tema del giorno
    draw.rounded_rectangle([(cx1, cy1), (cx2, cy2)], radius=48, fill=theme_color)
    
    # Icona Cornetta / Telefono a sinistra
    ico_box_w = 110
    ico_center_x = cx1 + 90
    ico_center_y = cy1 + card_h // 2
    draw.ellipse([(ico_center_x - 45, ico_center_y - 45), (ico_center_x + 45, ico_center_y + 45)], outline=(255, 255, 255), width=4)
    font_tel_ico = mgs.get_font(42, bold=True, font_type="sans")
    draw.text((ico_center_x, ico_center_y), "📞", font=font_tel_ico, fill=(255, 255, 255), anchor="mm")
    
    # Testi Telefono e Dati
    font_chiama = mgs.get_font(26, bold=True, font_type="sans")
    font_num = mgs.get_font(60, bold=True, font_type="sans")
    font_addr = mgs.get_font(30, bold=False, font_type="sans")
    
    draw.text((cx1 + 175, cy1 + 42), "CHIAMA ORA", font=font_chiama, fill=(255, 255, 255), anchor="lm")
    draw.text((cx1 + 175, cy1 + 95), "320 1667156", font=font_num, fill=(255, 255, 255), anchor="lm")
    
    # Riga divisoria interna sottile
    draw.line([(cx1 + 175, cy1 + 130), (cx2 - 50, cy1 + 130)], fill=(255, 255, 255, 120), width=2)
    draw.text((cx1 + 175, cy1 + 158), "📍 Favara • Corso Vittorio Veneto 151", font=font_addr, fill=(255, 255, 255), anchor="lm")

    # 7. Onda Curva Inferiore e Firma Calligrafica "La tua casa, la nostra passione"
    wave_h = 170
    wave_y = H - wave_h
    
    # Creazione maschera per onda decorativa
    wave_layer = Image.new("RGBA", (W, wave_h), (0, 0, 0, 0))
    w_draw = ImageDraw.Draw(wave_layer)
    
    # Disegna poligono curva morbida
    curve_pts = [(0, 60)]
    for wx in range(0, W + 1, 10):
        # Onda sinusoidale leggera
        wy = int(50 - 25 * math.sin((wx / W) * math.pi))
        curve_pts.append((wx, wy))
    curve_pts.extend([(W, wave_h), (0, wave_h)])
    w_draw.polygon(curve_pts, fill=theme_color)
    
    # Bordo superiore dorato/accento sull'onda
    for wx in range(0, W, 2):
        wy = int(50 - 25 * math.sin((wx / W) * math.pi))
        w_draw.line([(wx, wy), (wx + 2, wy)], fill=(255, 255, 255, 160), width=3)
        
    canvas.paste(wave_layer, (0, wave_y), wave_layer)
    
    # Scritta corsiva della firma
    font_script = mgs.get_font(42, bold=False, font_type="script")
    draw_final = ImageDraw.Draw(canvas)
    draw_final.text((W // 2 - 40, H - 75), "La tua casa, la nostra passione", font=font_script, fill=(255, 255, 255), anchor="mm")
    
    # Icona casetta con cuore line-art a destra della firma
    hx, hy = W // 2 + 330, H - 75
    draw_final.line([(hx - 25, hy + 10), (hx, hy - 20), (hx + 25, hy + 10)], fill=(255, 255, 255), width=3)
    draw_final.line([(hx - 20, hy + 10), (hx - 20, hy + 25), (hx + 20, hy + 25), (hx + 20, hy + 10)], fill=(255, 255, 255), width=3)
    draw_final.text((hx, hy + 10), "♥", font=mgs.get_font(20, bold=True), fill=(255, 255, 255), anchor="mm")

    canvas.save(output_path, "PNG", quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 2. STILE "AL TUO FIANCO, PASSO DOPO PASSO" (Reference Foto 3)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_al_tuo_fianco_passo_dopo_passo_9_16(media_info, palette=None, output_path=None):
    """
    Stile 'Al Tuo Fianco, Passo Dopo Passo':
    - Logo ufficiale Giancani in alto
    - Maxi Titolo bold nel colore del giorno: 'AL TUO FIANCO, PASSO DOPO PASSO'
    - Colonna sinistra con i 3 step di accompagnamento con icone e divisori
    - Colonna destra con foto immobile / plastico casa ad alta definizione
    - Card CTA arrotondata 'CONTATTACI' con telefono, email e sede
    - Angolo decorativo in basso a destra
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_fianco_{uuid.uuid4().hex[:6]}.png")
        
    colors = _get_daily_colors(palette)
    theme_color = colors["primary"]
    
    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Logo ufficiale in alto
    logo = mgs.get_logo_trasparente_ufficiale(max_w=460, max_h=120)
    if logo:
        lw, lh = logo.size
        canvas.paste(logo, ((W - lw) // 2, 50), logo)
        
    # 2. Maxi Titolo "AL TUO FIANCO, PASSO DOPO PASSO"
    font_maxi = mgs.get_font(64, bold=True, font_type="sans")
    draw.text((70, 200), "AL TUO FIANCO,", font=font_maxi, fill=theme_color)
    draw.text((70, 275), "PASSO DOPO PASSO", font=font_maxi, fill=theme_color)
    
    # 3. I 3 Step con Icone a sinistra (allineati a sinistra)
    step_y = 390
    step_gap = 180
    
    steps = [
        ("Consulenza\ndedicata", "💬"),
        ("Assistenza nella\ncompravendita", "🤝"),
        ("Promozione\ndell'immobile", "📢")
    ]
    
    font_step_text = mgs.get_font(34, bold=True, font_type="sans")
    font_step_ico = mgs.get_font(40, bold=False, font_type="sans")
    
    for i, (st_text, st_ico) in enumerate(steps):
        curr_y = step_y + i * step_gap
        
        # Cerchio icona con bordo in colore tema
        cx, cy = 115, curr_y + 40
        draw.ellipse([(cx - 40, cy - 40), (cx + 40, cy + 40)], outline=theme_color, width=3, fill=(245, 248, 250))
        draw.text((cx, cy), st_ico, font=font_step_ico, fill=theme_color, anchor="mm")
        
        # Testo del punto
        draw.text((175, curr_y + 40), st_text, font=font_step_text, fill=(30, 41, 59), anchor="lm")
        
        # Linea divisoria orizzontale leggera sotto lo step
        if i < 2:
            draw.line([(70, curr_y + 115), (480, curr_y + 115)], fill=(226, 232, 240), width=2)

    # 4. Hero Photo Immobile (posizionata nella parte destra/centrale con sagomatura elegante)
    photo = mgs.get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    pw, ph = 540, 720
    fw, fh = photo.size
    scale = max(pw / fw, ph / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    photo_res = photo.resize((nw, nh), Image.Resampling.LANCZOS)
    photo_crop = photo_res.crop(((nw - pw)//2, (nh - ph)//2, (nw - pw)//2 + pw, (nh - ph)//2 + ph))
    
    # Maschera con angoli arrotondati
    p_mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(p_mask).rounded_rectangle([(0, 0), (pw, ph)], radius=36, fill=255)
    
    photo_x = 480
    photo_y = 390
    _draw_shadow(canvas, (photo_x, photo_y, photo_x + pw, photo_y + ph), radius=36, shadow_color=(0, 0, 0, 70), blur=20, offset=(0, 10))
    canvas.paste(photo_crop, (photo_x, photo_y), p_mask)
    
    # Bordo attorno alla foto
    draw.rounded_rectangle([(photo_x, photo_y), (photo_x + pw, photo_y + ph)], radius=36, outline=theme_color, width=3)

    # 5. Dati Immobile in pillola sotto la foto (Prezzo e Metri Quadri)
    prezzo_txt = str(media_info.get("prezzo", "Trattativa Riservata"))
    mq_txt = str(media_info.get("mq", "")).replace("mq", "metri quadri").replace("m²", "metri quadri")
    
    pill_info_y = 1170
    draw.rounded_rectangle([(70, pill_info_y), (W - 70, pill_info_y + 110)], radius=24, fill=(245, 248, 250), outline=(226, 232, 240), width=2)
    draw.text((110, pill_info_y + 55), f"🏷️ {prezzo_txt}", font=mgs.get_font(36, bold=True), fill=theme_color, anchor="lm")
    if mq_txt:
        draw.text((W - 110, pill_info_y + 55), f"📐 {mq_txt}", font=mgs.get_font(32, bold=False), fill=(71, 85, 105), anchor="rm")

    # 6. Card CTA Inferiore "CONTATTACI" (in colore del giorno)
    card_w = 940
    card_h = 240
    cx1 = 70
    cx2 = cx1 + card_w
    cy1 = 1380
    cy2 = cy1 + card_h
    
    _draw_shadow(canvas, (cx1, cy1, cx2, cy2), radius=36, shadow_color=(0, 0, 0, 70), blur=16, offset=(0, 8))
    draw.rounded_rectangle([(cx1, cy1), (cx2, cy2)], radius=36, fill=theme_color)
    
    font_cta_head = mgs.get_font(52, bold=True, font_type="sans")
    font_cta_phone = mgs.get_font(42, bold=True, font_type="sans")
    font_cta_info = mgs.get_font(30, bold=False, font_type="sans")
    
    draw.text((W // 2, cy1 + 55), "CONTATTACI", font=font_cta_head, fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, cy1 + 125), "📞 320 1667156  •  immobiliaregiancani.it", font=font_cta_phone, fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, cy1 + 185), "📍 Favara • Corso Vittorio Veneto 151", font=font_cta_info, fill=(255, 255, 255), anchor="mm")

    # Baffo decorativo angolo in basso a destra (come nella reference)
    draw.pieslice([(W - 140, H - 140), (W + 100, H + 100)], start=180, end=270, fill=theme_color)
    draw.pieslice([(W - 80, H - 80), (W + 120, H + 120)], start=180, end=270, fill=colors["accent"])

    # Personal branding in basso a sinistra
    draw.text((70, H - 70), "— Immobiliare Giancani", font=mgs.get_font(30, bold=True), fill=theme_color, anchor="lm")

    canvas.save(output_path, "PNG", quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 3. STILE "I NOSTRI SERVIZI A 360°" (Reference Foto 2)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_servizi_360_9_16(media_info, palette=None, output_path=None):
    """
    Stile 'I Nostri Servizi a 360°':
    - Sfondo superiore con foto agenzia/interior sfocata e logo Giancani
    - Titolo 'I NOSTRI SERVIZI'
    - Ribbon/Banner 'AFFIDATI ALLA NOSTRA AGENZIA, TI OFFRIAMO UN SERVIZIO A 360°'
    - Griglia 6 Card bianche sagomate con icone e descrizioni:
      1. Valutazione Gratuita
      2. Assistenza fino al Rogito
      3. Gestione Visite all'Immobile
      4. Conoscenza Dettagliata della Zona
      5. Canali Cartacei e Digitali
      6. Servizio Fotografico & Tour 360°
    - Calligrafico 'Siamo qui per te!' con freccia
    - Banner WhatsApp / Chiama Ora con recapiti completi
    - Footer Giancani con forme geometriche coordinate
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_servizi_{uuid.uuid4().hex[:6]}.png")
        
    colors = _get_daily_colors(palette)
    theme_color = colors["primary"]
    
    canvas = Image.new("RGBA", (W, H), (248, 250, 252, 255))
    
    # 1. Header con foto sfumata / profondità di campo
    photo = mgs.get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    header_h = 360
    ph_crop = photo.resize((W, int(photo.size[1] * (W / photo.size[0]))), Image.Resampling.LANCZOS)
    ph_crop = ph_crop.crop((0, 0, W, header_h))
    ph_blurred = ph_crop.filter(ImageFilter.GaussianBlur(8))
    
    # Maschera gradiente che sfuma gradualmente nel bianco
    grad_mask = Image.new("L", (W, header_h), 0)
    for gy in range(header_h):
        alpha = int(255 * (1.0 - (gy / header_h) ** 1.5))
        for gx in range(W):
            grad_mask.putpixel((gx, gy), alpha)
            
    canvas.paste(ph_blurred, (0, 0), grad_mask)
    
    draw = ImageDraw.Draw(canvas)
    
    # Logo ufficiale in alto con leggero backing protettivo
    logo = mgs.get_logo_trasparente_ufficiale(max_w=460, max_h=120)
    if logo:
        lw, lh = logo.size
        draw.rounded_rectangle([((W - lw) // 2 - 20, 35), ((W + lw) // 2 + 20, 35 + lh + 10)], radius=16, fill=(255, 255, 255, 230))
        canvas.paste(logo, ((W - lw) // 2, 40), logo)

    # 2. Titolo "I NOSTRI SERVIZI"
    font_title = mgs.get_font(64, bold=True, font_type="sans")
    font_sub = mgs.get_font(28, bold=False, font_type="sans")
    
    draw.text((70, 185), "I NOSTRI SERVIZI", font=font_title, fill=theme_color)
    draw.text((70, 258), "Affidati alla nostra esperienza, ci prendiamo cura", font=font_sub, fill=(50, 60, 75))
    draw.text((70, 298), "di ogni dettaglio per te con la massima trasparenza.", font=font_sub, fill=(50, 60, 75))

    # 3. Ribbon Orizzontale a 360° (con angoli arrotondati e bordo)
    rx1, ry1 = 70, 355
    rx2, ry2 = W - 70, 455
    _draw_shadow(canvas, (rx1, ry1, rx2, ry2), radius=50, shadow_color=(0, 0, 0, 50), blur=12, offset=(0, 6))
    draw.rounded_rectangle([(rx1, ry1), (rx2, ry2)], radius=50, fill=theme_color)
    
    # Icona casetta a sinistra del ribbon
    draw.text((rx1 + 45, ry1 + 50), "🏠", font=mgs.get_font(42), fill=(255, 255, 255), anchor="mm")
    
    font_ribbon = mgs.get_font(26, bold=True, font_type="sans")
    draw.text((W // 2 + 20, ry1 + 32), "AFFIDATI ALLA NOSTRA AGENZIA,", font=font_ribbon, fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2 + 20, ry1 + 68), "TI OFFRIAMO UN SERVIZIO A 360°", font=mgs.get_font(32, bold=True), fill=(255, 255, 255), anchor="mm")

    # 4. Griglia 6 Card Servizi (2 colonne x 3 righe)
    card_w = 445
    card_h = 240
    gap_x = 30
    gap_y = 25
    grid_start_x = 75
    grid_start_y = 485
    
    servizi_list = [
        ("VALUTAZIONE\nGRATUITA", "Valutiamo il tuo immobile in modo preciso e gratuito.", "⚖️"),
        ("ASSISTENZA\nFINO AL ROGITO", "Ti seguiamo passo dopo passo fino al rogito notarile.", "📋"),
        ("GESTIONE DELLE\nVISITE", "Organizziamo e gestiamo le visite con clienti qualificati.", "🏠"),
        ("CONOSCENZA\nDELLA ZONA", "Conosciamo a fondo Favara e Agrigento da generazioni.", "📍"),
        ("RIVISTE E\nCANALI SOCIAL", "Pubblicità mirata e sponsorizzata sui principali social.", "📢"),
        ("SERVIZIO FOTO &\nVIRTUAL TOUR", "Valorizziamo la tua casa con foto e video ad alta resa.", "📸")
    ]
    
    font_c_title = mgs.get_font(24, bold=True, font_type="sans")
    font_c_desc = mgs.get_font(20, bold=False, font_type="sans")
    font_c_ico = mgs.get_font(38, bold=False, font_type="sans")
    
    for i, (c_title, c_desc, c_ico) in enumerate(servizi_list):
        col = i % 2
        row = i // 2
        
        cx1 = grid_start_x + col * (card_w + gap_x)
        cx2 = cx1 + card_w
        cy1 = grid_start_y + row * (card_h + gap_y)
        cy2 = cy1 + card_h
        
        # Ombra morbida
        _draw_shadow(canvas, (cx1, cy1, cx2, cy2), radius=22, shadow_color=(0, 0, 0, 30), blur=10, offset=(0, 4))
        
        # Sfondo card bianca con sottile contorno in tinta
        draw.rounded_rectangle([(cx1, cy1), (cx2, cy2)], radius=22, fill=(255, 255, 255), outline=(226, 232, 240), width=2)
        
        # Icona in alto a sinistra
        draw.text((cx1 + 45, cy1 + 50), c_ico, font=font_c_ico, fill=theme_color, anchor="mm")
        
        # Titolo card
        draw.text((cx1 + 95, cy1 + 50), c_title, font=font_c_title, fill=theme_color, anchor="lm")
        
        # Linea divisoria interna
        draw.line([(cx1 + 25, cy1 + 95), (cx2 - 25, cy1 + 95)], fill=(241, 245, 249), width=2)
        
        # Descrizione su 2 righe
        words = c_desc.split()
        line1 = " ".join(words[:5])
        line2 = " ".join(words[5:])
        draw.text((cx1 + 25, cy1 + 130), line1, font=font_c_desc, fill=(71, 85, 105))
        draw.text((cx1 + 25, cy1 + 165), line2, font=font_c_desc, fill=(71, 85, 105))

    # 5. Bottone WhatsApp / Consulenza con "Siamo qui per te!" a sinistra
    draw.text((160, 1345), "Siamo qui\nper te! ➔", font=mgs.get_font(28, bold=True, font_type="serif"), fill=theme_color, anchor="mm")
    
    btn_w = 660
    btn_h = 95
    bx1 = 340
    bx2 = bx1 + btn_w
    by1 = 1300
    by2 = by1 + btn_h
    
    _draw_shadow(canvas, (bx1, by1, bx2, by2), radius=48, shadow_color=(0, 0, 0, 60), blur=14, offset=(0, 6))
    draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=48, fill=theme_color)
    
    font_btn = mgs.get_font(25, bold=True, font_type="sans")
    draw.text(((bx1 + bx2) // 2, by1 + btn_h // 2), "💬 CONTATTACI PER UNA CONSULENZA GRATUITA!", font=font_btn, fill=(255, 255, 255), anchor="mm")

    # 6. Footer Ufficiale con Recapiti Completi e Forme Geometriche
    fx1, fy1 = 70, 1435
    fx2, fy2 = W - 70, 1680
    draw.rounded_rectangle([(fx1, fy1), (fx2, fy2)], radius=28, fill=(30, 41, 59))
    
    # Mini logo / dicitura
    draw.text((W // 2, fy1 + 45), "IMMOBILIARE GIANCANI", font=mgs.get_font(34, bold=True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, fy1 + 95), "📍 Corso Vittorio Veneto 151, Favara (AG)", font=mgs.get_font(28), fill=(226, 232, 240), anchor="mm")
    draw.text((W // 2, fy1 + 145), "📞 320 166 7156  •  www.immobiliaregiancani.it", font=mgs.get_font(30, bold=True), fill=colors["accent"], anchor="mm")
    draw.text((W // 2, fy1 + 195), "— Immobiliare Giancani", font=mgs.get_font(26, bold=True), fill=(255, 255, 255), anchor="mm")

    # Angoli decorativi coordinati
    draw.pieslice([(W - 120, H - 120), (W + 60, H + 60)], start=180, end=270, fill=theme_color)

    canvas.save(output_path, "PNG", quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 4. STILE "EFFETTO CALAMITA / PORTFOLIO" (Reference Foto 1)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_effetto_calamita_9_16(media_info, palette=None, output_path=None):
    """
    Stile 'Effetto Calamita / Portfolio Venduto & In Vendita':
    - Logo Giancani e badge 'EFFETTO CALAMITA'
    - Griglia 4 foto immobiliari con badge tipologia curvo (Commerciale, Villa, Appartamento, Casa)
    - Nastro 'VENDUTO' o 'IN VENDITA' in risalto su ogni foto
    - Mini recapiti agenzia sotto ogni elemento
    - Sticker calligrafico 'Selezionati Giancani'
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_calamita_{uuid.uuid4().hex[:6]}.png")
        
    colors = _get_daily_colors(palette)
    theme_color = colors["primary"]
    
    canvas = Image.new("RGBA", (W, H), (252, 252, 254, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Logo in alto a sinistra
    logo = mgs.get_logo_trasparente_ufficiale(max_w=400, max_h=100)
    if logo:
        canvas.paste(logo, (60, 50), logo)

    # 2. Badge Calamita in alto a destra
    cal_x, cal_y = W - 320, 45
    draw.text((cal_x + 130, cal_y + 35), "🧲", font=mgs.get_font(55), fill=theme_color, anchor="mm")
    draw.text((cal_x + 130, cal_y + 80), "EFFETTO", font=mgs.get_font(28, bold=True), fill=theme_color, anchor="mm")
    draw.text((cal_x + 130, cal_y + 115), "CALAMITA", font=mgs.get_font(38, bold=True), fill=theme_color, anchor="mm")

    # 3. Griglia 4 Foto Immobiliari Sfalsate (Tutte "IN VENDITA")
    card_w = 450
    card_h = 520
    
    # 4 posizioni sfalsate - Tutte rigorosamente "IN VENDITA"
    card_positions = [
        (55, 210, "COMMERCIALE", "Via Veneto", "Favara", "IN VENDITA"),
        (575, 320, "CASA CIELO TERRA", "Centro Storico", "Favara", "IN VENDITA"),
        (55, 780, "VILLA CON TERRENO", "C.da San Calogero", "Favara", "IN VENDITA"),
        (575, 890, "APPARTAMENTO", "Corso V. Veneto", "Favara", "IN VENDITA")
    ]
    
    # Prepara foto
    main_photo = mgs.get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    
    font_badge = mgs.get_font(24, bold=True, font_type="sans")
    font_sub_badge = mgs.get_font(18, bold=False, font_type="sans")
    font_status = mgs.get_font(26, bold=True, font_type="sans")
    font_contact = mgs.get_font(16, bold=True, font_type="sans")

    for (cx1, cy1, cat, via, citta, status) in card_positions:
        cx2 = cx1 + card_w
        cy2 = cy1 + card_h
        
        # Ombra card
        _draw_shadow(canvas, (cx1, cy1, cx2, cy2), radius=16, shadow_color=(0, 0, 0, 45), blur=12, offset=(0, 6))
        
        # Sfondo card bianca
        draw.rounded_rectangle([(cx1, cy1), (cx2, cy2)], radius=16, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
        
        # Foto interna (occupa la parte centrale della card)
        photo_box_h = 320
        ph_crop = main_photo.resize((card_w, photo_box_h), Image.Resampling.LANCZOS)
        canvas.paste(ph_crop, (cx1, cy1 + 95))
        
        # Badge curvo categoria in alto a sinistra (con sagomatura ad arco)
        bw, bh = 240, 85
        draw.rounded_rectangle([(cx1 + 10, cy1 + 8), (cx1 + 10 + bw, cy1 + 8 + bh)], radius=18, fill=theme_color)
        draw.text((cx1 + 10 + bw // 2, cy1 + 32), cat, font=font_badge, fill=(255, 255, 255), anchor="mm")
        draw.text((cx1 + 10 + bw // 2, cy1 + 65), f"{via} • {citta}", font=font_sub_badge, fill=(240, 245, 250), anchor="mm")
        
        # Nastro Status a bandiera con freccia ("IN VENDITA")
        # Colore verde smeraldo o tema del giorno per massimo richiamo positivo
        rw, rh = 210, 48
        rib_y = cy1 + photo_box_h + 15
        draw.rounded_rectangle([(cx1 + 10, rib_y), (cx1 + 10 + rw, rib_y + rh)], radius=8, fill=theme_color)
        draw.text((cx1 + 10 + rw // 2, rib_y + rh // 2), "IN VENDITA", font=font_status, fill=(255, 255, 255), anchor="mm")
        
        # Mini barra contatti sotto la foto
        draw.text((cx1 + 15, cy2 - 25), "IMMOBILIARE GIANCANI", font=font_contact, fill=theme_color)
        draw.text((cx2 - 15, cy2 - 25), "📞 320 166 7156", font=font_contact, fill=(30, 41, 59), anchor="ra")

    # 4. Timbro Calligrafico "IN VENDITA" in basso a sinistra
    stamp_x, stamp_y = 220, 1500
    font_stamp = mgs.get_font(56, bold=True, font_type="sans")
    font_month = mgs.get_font(48, bold=False, font_type="script")
    draw.text((stamp_x, stamp_y), "IN VENDITA", font=font_stamp, fill=(225, 29, 72), anchor="mm")
    draw.text((stamp_x + 10, stamp_y + 55), "Selezionati Giancani", font=font_month, fill=(234, 88, 12), anchor="mm")
    
    # 5. Footer con brand ufficiale
    draw.text((W // 2, H - 160), "COMPRA E VENDI CASA IN TOTALE SICUREZZA", font=mgs.get_font(34, bold=True), fill=theme_color, anchor="mm")
    draw.text((W // 2, H - 105), "📍 Favara • Corso Vittorio Veneto 151  •  📞 320 166 7156", font=mgs.get_font(28), fill=(71, 85, 105), anchor="mm")
    draw.text((W // 2, H - 55), "— Immobiliare Giancani", font=mgs.get_font(30, bold=True), fill=theme_color, anchor="mm")

    canvas.save(output_path, "PNG", quality=95)
    return output_path
