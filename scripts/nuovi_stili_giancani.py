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
    - Elenco 3 Step con icone line-art pulite:
      1. Consulenza dedicata
      2. Assistenza nella compravendita (fino al rogito)
      3. Promozione dell'immobile
    - Hero Photo con plastico di casa, chiavi o rogito
    - Card CTA arrotondata 'CONTATTACI' con telefono, email e sede
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
    font_maxi = mgs.get_font(68, bold=True, font_type="sans")
    draw.text((70, 200), "AL TUO FIANCO,", font=font_maxi, fill=theme_color)
    draw.text((70, 280), "PASSO DOPO PASSO", font=font_maxi, fill=theme_color)
    
    # 3. I 3 Step con Icone a sinistra
    step_y = 390
    step_gap = 145
    
    steps = [
        ("Consulenza\ndedicata", "💬"),
        ("Assistenza nella\ncompravendita", "🤝"),
        ("Promozione\ndell'immobile", "📢")
    ]
    
    font_step_text = mgs.get_font(36, bold=True, font_type="sans")
    font_step_ico = mgs.get_font(42, bold=False, font_type="sans")
    
    for i, (st_text, st_ico) in enumerate(steps):
        curr_y = step_y + i * step_gap
        
        # Cerchio icona con bordo in colore tema
        cx, cy = 120, curr_y + 30
        draw.ellipse([(cx - 45, cy - 45), (cx + 45, cy + 45)], outline=theme_color, width=3, fill=(245, 248, 250))
        draw.text((cx, cy), st_ico, font=font_step_ico, fill=theme_color, anchor="mm")
        
        # Testo del punto
        draw.text((195, curr_y + 30), st_text, font=font_step_text, fill=(30, 41, 59), anchor="lm")
        
        # Linea divisoria orizzontale leggera
        if i < 2:
            draw.line([(70, curr_y + 90), (520, curr_y + 90)], fill=(226, 232, 240), width=2)

    # 4. Hero Photo Immobile / Mano che regge la casa (posizionata a destra/centro)
    photo = mgs.get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    pw, ph = 940, 680
    fw, fh = photo.size
    scale = max(pw / fw, ph / fh)
    nw, nh = int(fw * scale), int(fh * scale)
    photo_res = photo.resize((nw, nh), Image.Resampling.LANCZOS)
    photo_crop = photo_res.crop(((nw - pw)//2, (nh - ph)//2, (nw - pw)//2 + pw, (nh - ph)//2 + ph))
    
    # Maschera con angoli arrotondati
    p_mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(p_mask).rounded_rectangle([(0, 0), (pw, ph)], radius=32, fill=255)
    
    photo_x = 70
    photo_y = 860
    _draw_shadow(canvas, (photo_x, photo_y, photo_x + pw, photo_y + ph), radius=32, shadow_color=(0, 0, 0, 60), blur=18, offset=(0, 8))
    canvas.paste(photo_crop, (photo_x, photo_y), p_mask)

    # 5. Card CTA Inferiore "CONTATTACI" (in colore del giorno)
    card_w = 940
    card_h = 240
    cx1 = 70
    cx2 = cx1 + card_w
    cy1 = 1590
    cy2 = cy1 + card_h
    
    _draw_shadow(canvas, (cx1, cy1, cx2, cy2), radius=36, shadow_color=(0, 0, 0, 70), blur=16, offset=(0, 8))
    draw.rounded_rectangle([(cx1, cy1), (cx2, cy2)], radius=36, fill=theme_color)
    
    font_cta_head = mgs.get_font(52, bold=True, font_type="sans")
    font_cta_phone = mgs.get_font(42, bold=True, font_type="sans")
    font_cta_info = mgs.get_font(30, bold=False, font_type="sans")
    
    draw.text((W // 2, cy1 + 55), "CONTATTACI", font=font_cta_head, fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, cy1 + 125), "📞 320 166 7156  •  immobiliaregiancani.it", font=font_cta_phone, fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, cy1 + 185), "📍 Corso Vittorio Veneto 151, Favara (AG)", font=font_cta_info, fill=(255, 255, 255), anchor="mm")

    # Baffo decorativo angolo in basso a destra (come nella reference)
    draw.pieslice([(W - 120, H - 120), (W + 80, H + 80)], start=180, end=270, fill=theme_color)

    canvas.save(output_path, "PNG", quality=95)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# 3. STILE "I NOSTRI SERVIZI A 360°" (Reference Foto 2)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_story_servizi_360_9_16(media_info, palette=None, output_path=None):
    """
    Stile 'I Nostri Servizi a 360°':
    - Logo Giancani e titolo 'I NOSTRI SERVIZI'
    - Ribbon/Banner 'AFFIDATI ALLA NOSTRA AGENZIA, TI OFFRIAMO UN SERVIZIO A 360°'
    - Griglia 6 Card bianche sagomate con icone e descrizioni:
      1. Valutazione Gratuita
      2. Assistenza fino al Rogito
      3. Gestione Visite all'Immobile
      4. Conoscenza Dettagliata della Zona
      5. Canali Cartacei e Digitali
      6. Servizio Fotografico & Tour 360°
    - Banner WhatsApp / Chiama Ora con recapiti completi
    """
    W, H = 1080, 1920
    if not output_path:
        output_path = os.path.join(SCRATCH_DIR, f"story_servizi_{uuid.uuid4().hex[:6]}.png")
        
    colors = _get_daily_colors(palette)
    theme_color = colors["primary"]
    
    canvas = Image.new("RGBA", (W, H), (248, 250, 252, 255))
    draw = ImageDraw.Draw(canvas)
    
    # 1. Header Logo
    logo = mgs.get_logo_trasparente_ufficiale(max_w=440, max_h=110)
    if logo:
        lw, lh = logo.size
        canvas.paste(logo, ((W - lw) // 2, 45), logo)

    # 2. Titolo "I NOSTRI SERVIZI"
    font_title = mgs.get_font(68, bold=True, font_type="sans")
    font_sub = mgs.get_font(30, bold=False, font_type="sans")
    
    draw.text((70, 175), "I NOSTRI SERVIZI", font=font_title, fill=theme_color)
    draw.text((70, 250), "Affidati alla nostra esperienza, ci prendiamo cura", font=font_sub, fill=(70, 80, 95))
    draw.text((70, 290), "di ogni dettaglio per te con la massima sicurezza.", font=font_sub, fill=(70, 80, 95))

    # 3. Ribbon Orizzontale a 360° (con angoli arrotondati e bordo)
    rx1, ry1 = 70, 345
    rx2, ry2 = W - 70, 445
    _draw_shadow(canvas, (rx1, ry1, rx2, ry2), radius=50, shadow_color=(0, 0, 0, 50), blur=12, offset=(0, 6))
    draw.rounded_rectangle([(rx1, ry1), (rx2, ry2)], radius=50, fill=theme_color)
    
    font_ribbon = mgs.get_font(30, bold=True, font_type="sans")
    draw.text((W // 2, ry1 + 32), "AFFIDATI ALLA NOSTRA AGENZIA,", font=font_ribbon, fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, ry1 + 68), "TI OFFRIAMO UN SERVIZIO A 360°", font=mgs.get_font(34, bold=True), fill=(255, 255, 255), anchor="mm")

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
        ("GESTIONE DELLE\nVISITE", "Organizziamo e gestiamo le visite in modo professionale.", "🏠"),
        ("CONOSCENZA\nDELLA ZONA", "Conosciamo a fondo Favara e Agrigento da generazioni.", "📍"),
        ("RIVISTE E\nCANALI SOCIAL", "Pubblicità costante e mirata sui massimi canali online.", "📢"),
        ("SERVIZIO FOTO &\nVIRTUAL TOUR", "Valorizziamo la tua casa con foto e tour professionali.", "📸")
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
        
        # Descrizione
        # Word wrap su 2 righe
        words = c_desc.split()
        line1 = " ".join(words[:5])
        line2 = " ".join(words[5:])
        draw.text((cx1 + 25, cy1 + 130), line1, font=font_c_desc, fill=(71, 85, 105))
        draw.text((cx1 + 25, cy1 + 165), line2, font=font_c_desc, fill=(71, 85, 105))

    # 5. Bottone WhatsApp / Consulenza
    btn_w = 780
    btn_h = 90
    bx1 = (W - btn_w) // 2
    bx2 = bx1 + btn_w
    by1 = 1320
    by2 = by1 + btn_h
    
    _draw_shadow(canvas, (bx1, by1, bx2, by2), radius=45, shadow_color=(0, 0, 0, 60), blur=14, offset=(0, 6))
    draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=45, fill=theme_color)
    
    font_btn = mgs.get_font(28, bold=True, font_type="sans")
    draw.text((W // 2, by1 + btn_h // 2), "💬 CONTATTACI PER UNA CONSULENZA GRATUITA!", font=font_btn, fill=(255, 255, 255), anchor="mm")

    # 6. Footer Ufficiale con Recapiti Completi
    fx1, fy1 = 70, 1450
    fx2, fy2 = W - 70, 1680
    draw.rounded_rectangle([(fx1, fy1), (fx2, fy2)], radius=28, fill=(30, 41, 59))
    
    # Mini logo / dicitura
    draw.text((W // 2, fy1 + 45), "IMMOBILIARE GIANCANI", font=mgs.get_font(34, bold=True), fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, fy1 + 95), "📍 Corso Vittorio Veneto 151, Favara (AG)", font=mgs.get_font(28), fill=(226, 232, 240), anchor="mm")
    draw.text((W // 2, fy1 + 145), "📞 320 166 7156  •  www.immobiliaregiancani.it", font=mgs.get_font(30, bold=True), fill=colors["accent"], anchor="mm")
    draw.text((W // 2, fy1 + 195), "— Immobiliare Giancani", font=mgs.get_font(26, bold=True), fill=(255, 255, 255), anchor="mm")

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

    # 3. Griglia 4 Foto Immobiliari (2 colonne x 2 righe)
    grid_top_y = 210
    card_w = 450
    card_h = 580
    gap_x = 60
    gap_y = 50
    start_x = 60
    
    # Dati per le 4 card
    items = [
        ("Commerciale", "Via Veneto", "Favara", "IN VENDITA"),
        ("Casa Indipendente", "Centro Storico", "Favara", "VENDUTO"),
        ("Villa Panoramica", "C.da San Calogero", "Favara", "IN VENDITA"),
        ("Appartamento", "Corso Vittorio Veneto", "Favara", "VENDUTO")
    ]
    
    # Prepara foto
    main_photo = mgs.get_clean_property_photo(media_info, (W, H)).convert("RGBA")
    
    font_badge = mgs.get_font(26, bold=True, font_type="sans")
    font_sub_badge = mgs.get_font(18, bold=False, font_type="sans")
    font_status = mgs.get_font(28, bold=True, font_type="sans")
    font_contact = mgs.get_font(18, bold=True, font_type="sans")

    for idx, (cat, via, citta, status) in enumerate(items):
        col = idx % 2
        row = idx // 2
        
        cx1 = start_x + col * (card_w + gap_x)
        cx2 = cx1 + card_w
        cy1 = grid_top_y + row * (card_h + gap_y)
        cy2 = cy1 + card_h
        
        # Ombra card
        _draw_shadow(canvas, (cx1, cy1, cx2, cy2), radius=16, shadow_color=(0, 0, 0, 40), blur=12, offset=(0, 6))
        
        # Sfondo card bianca
        draw.rounded_rectangle([(cx1, cy1), (cx2, cy2)], radius=16, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
        
        # Foto interna (occupa la parte centrale della card)
        photo_box_h = 360
        ph_crop = main_photo.resize((card_w, photo_box_h), Image.Resampling.LANCZOS)
        canvas.paste(ph_crop, (cx1, cy1 + 100))
        
        # Badge curvo categoria in alto a sinistra
        bw, bh = 220, 90
        draw.rounded_rectangle([(cx1 + 15, cy1 + 10), (cx1 + 15 + bw, cy1 + 10 + bh)], radius=18, fill=theme_color)
        draw.text((cx1 + 25 + bw // 2, cy1 + 38), cat.upper(), font=font_badge, fill=(255, 255, 255), anchor="mm")
        draw.text((cx1 + 25 + bw // 2, cy1 + 72), f"{via} - {citta}", font=font_sub_badge, fill=(240, 245, 250), anchor="mm")
        
        # Nastro Status a bandiera ("IN VENDITA" o "VENDUTO")
        rib_color = (220, 38, 38) if status == "VENDUTO" else theme_color
        rw, rh = 210, 50
        draw.rounded_rectangle([(cx1 + 15, cy1 + photo_box_h + 30), (cx1 + 15 + rw, cy1 + photo_box_h + 30 + rh)], radius=8, fill=rib_color)
        draw.text((cx1 + 15 + rw // 2, cy1 + photo_box_h + 30 + rh // 2), status, font=font_status, fill=(255, 255, 255), anchor="mm")
        
        # Mini barra contatti sotto la foto
        draw.text((cx1 + 25, cy2 - 35), "IMMOBILIARE GIANCANI", font=font_contact, fill=theme_color)
        draw.text((cx2 - 25, cy2 - 35), "📞 320 166 7156", font=font_contact, fill=(30, 41, 59), anchor="ra")

    # 4. Sticker calligrafico in basso a sinistra
    font_sticker = mgs.get_font(48, bold=False, font_type="script")
    draw.text((220, H - 280), "Selezionati Giancani", font=font_sticker, fill=(220, 38, 38), anchor="mm")
    
    # 5. Footer con brand ufficiale
    draw.text((W // 2, H - 120), "COMPRA E VENDI CASA IN SICUREZZA", font=mgs.get_font(34, bold=True), fill=theme_color, anchor="mm")
    draw.text((W // 2, H - 70), "— Immobiliare Giancani  •  Favara (AG)", font=mgs.get_font(28, bold=True), fill=(71, 85, 105), anchor="mm")

    canvas.save(output_path, "PNG", quality=95)
    return output_path
