# -*- coding: utf-8 -*-
"""
======================================================================
  🎨 MOTORE GRAFICO MULTIMEDIALE — CARDS & FOTO CON WATERMARK
  Progetto: Bot Facebook Ufficiale "Favara"
  Autore: Antonio Giancani | Immobiliare Giancani
  
  Regola specifica:
  - NON mettere il logo dell'agenzia immobiliare sulle foto/grafiche.
  - Applicare rigorosamente la firma 'Sono A.G.' in basso a destra.
======================================================================
"""

import os
import io
import requests
import urllib3
from PIL import Image, ImageDraw, ImageFont, ImageFilter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "media_favara")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Font candidati multipiattaforma (Windows & Linux Ubuntu / GitHub Actions)
FONT_CANDIDATES_BOLD = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
FONT_CANDIDATES_REGULAR = [
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]

FONT_BOLD = "bold"
FONT_REGULAR = "regular"

def ottieni_font(tipo_o_percorso, dimensione):
    """Carica un font TrueType multipiattaforma (Windows e Linux)."""
    if tipo_o_percorso == "bold":
        candidati = FONT_CANDIDATES_BOLD
    elif tipo_o_percorso == "regular":
        candidati = FONT_CANDIDATES_REGULAR
    else:
        candidati = [tipo_o_percorso] + FONT_CANDIDATES_BOLD

    for c in candidati:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, dimensione)
            except Exception:
                continue

    try:
        return ImageFont.load_default(size=dimensione)
    except Exception:
        return ImageFont.load_default()

def scarica_o_crea_base(img_url=None, width=1080, height=1080, tema="gold"):
    """
    Scarica l'immagine dalla rete o genera uno sfondo gradient professionale
    ispirato ai colori caldi della terra siciliana (pietra calcarea, tufo, oro, blu mare).
    """
    img_base = None
    
    if img_url:
        try:
            headers = {"User-Agent": "Mozilla/5.0 FavaraBot/1.0"}
            r = requests.get(img_url, headers=headers, timeout=12, verify=False)
            if r.status_code == 200:
                raw_img = Image.open(io.BytesIO(r.content)).convert("RGBA")
                # Crop proporzionale per riempire 1080x1080 (cover)
                aspect_target = width / height
                aspect_raw = raw_img.width / raw_img.height

                if aspect_raw > aspect_target:
                    new_w = int(raw_img.height * aspect_target)
                    left = (raw_img.width - new_w) // 2
                    raw_img = raw_img.crop((left, 0, left + new_w, raw_img.height))
                else:
                    new_h = int(raw_img.width / aspect_target)
                    top = (raw_img.height - new_h) // 2
                    raw_img = raw_img.crop((0, top, raw_img.width, top + new_h))

                img_base = raw_img.resize((width, height), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"⚠️ Impossibile scaricare immagine ({e}), creazione sfondo generativo...")

    if img_base is None:
        # Genera sfondo elegante con gradiente caldo
        img_base = Image.new("RGBA", (width, height), (22, 28, 36, 255))
        draw_grad = ImageDraw.Draw(img_base)
        
        # Colori tematici siciliani
        if tema == "gold":
            c_top = (45, 30, 15)
            c_bot = (15, 12, 8)
        elif tema == "blue":
            c_top = (15, 32, 55)
            c_bot = (8, 16, 28)
        else:
            c_top = (35, 22, 38)
            c_bot = (12, 8, 16)

        for y in range(height):
            ratio = y / height
            r = int(c_top[0] * (1 - ratio) + c_bot[0] * ratio)
            g = int(c_top[1] * (1 - ratio) + c_bot[1] * ratio)
            b = int(c_top[2] * (1 - ratio) + c_bot[2] * ratio)
            draw_grad.line([(0, y), (width, y)], fill=(r, g, b, 255))

    return img_base

def applica_overlay_scuro(img, top_alpha=120, bot_alpha=200):
    """Applica gradienti scuri in alto e in basso per garantire massima leggibilità del testo."""
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    # Gradiente in alto (per badge o data)
    top_band = int(h * 0.22)
    for y in range(top_band):
        alpha = int(top_alpha * (1 - y / top_band))
        draw_ov.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

    # Gradiente in basso (per titolo e watermark)
    bot_band = int(h * 0.42)
    start_y = h - bot_band
    for y in range(start_y, h):
        ratio = (y - start_y) / bot_band
        alpha = int(bot_alpha * ratio)
        draw_ov.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

    return Image.alpha_composite(img, overlay)

def crea_card_favara(titolo, categoria, sottotitolo="", img_url=None, output_filename=None, tema="gold"):
    """
    Genera un'immagine Facebook ad alto impatto grafico con:
    - Badge tematico
    - Titolo e sottotitolo formattati
    - In basso a destra il contrassegno d'autore "Sono A.G." (NO logo immobiliare)
    """
    w, h = 1080, 1080
    base = scarica_o_crea_base(img_url, w, h, tema=tema)
    base = applica_overlay_scuro(base)
    draw = ImageDraw.Draw(base)

    # 1. BADGE CATEGORIA (In alto a sinistra)
    font_badge = ottieni_font(FONT_BOLD, 28)
    badge_text = f"  FAVARA  •  {categoria.upper()}  "
    bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw, bh = bbox_b[2] - bbox_b[0] + 30, bbox_b[3] - bbox_b[1] + 20
    
    badge_x, badge_y = 50, 50
    # Rettangolo stondato con sfondo caldo/ambrato
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + bw, badge_y + bh],
        radius=12,
        fill=(220, 165, 30, 230),
        outline=(255, 255, 255, 220),
        width=2
    )
    draw.text((badge_x + 15, badge_y + 10), badge_text, font=font_badge, fill=(20, 15, 5, 255))

    # 2. TITOLO IN BASSO
    font_titolo = ottieni_font(FONT_BOLD, 52)
    font_sotto = ottieni_font(FONT_REGULAR, 32)

    # Spezza il titolo se troppo lungo
    parole = titolo.split()
    righe = []
    riga_corrente = ""
    for p in parole:
        test_riga = f"{riga_corrente} {p}".strip()
        bbox = draw.textbbox((0, 0), test_riga, font=font_titolo)
        if (bbox[2] - bbox[0]) < (w - 120):
            riga_corrente = test_riga
        else:
            if riga_corrente:
                righe.append(riga_corrente)
            riga_corrente = p
    if riga_corrente:
        righe.append(riga_corrente)
    
    # Limita a massimo 3 righe per il titolo
    righe = righe[:3]
    
    # Posizione di partenza del titolo
    interlinea = 64
    altezza_blocco_testo = len(righe) * interlinea + (45 if sottotitolo else 0)
    pos_y = h - 140 - altezza_blocco_testo

    for r in righe:
        # Ombreggiatura leggera per contrasto
        draw.text((52, pos_y + 2), r, font=font_titolo, fill=(0, 0, 0, 200))
        draw.text((50, pos_y), r, font=font_titolo, fill=(255, 255, 255, 255))
        pos_y += interlinea

    if sottotitolo:
        pos_y += 10
        # Sottotitolo in colore avorio dorato
        draw.text((52, pos_y + 2), sottotitolo[:65], font=font_sotto, fill=(0, 0, 0, 180))
        draw.text((50, pos_y), sottotitolo[:65], font=font_sotto, fill=(240, 220, 180, 255))

    # ── 3. WATERMARK REGOLA ESCLUSIVA: "A.G." IN BASSO A DESTRA ─────
    # NON METTERE IL LOGO DELL'AGENZIA IMMOBILIARE
    font_watermark = ottieni_font(FONT_BOLD, 30)
    wm_text = "A.G."
    bbox_wm = draw.textbbox((0, 0), wm_text, font=font_watermark)
    wm_w = bbox_wm[2] - bbox_wm[0]
    wm_h = bbox_wm[3] - bbox_wm[1]

    # Pillola elegante in basso a destra
    pad_x = 22
    pad_y = 10
    box_w = wm_w + (pad_x * 2)
    box_h = wm_h + (pad_y * 2)
    box_x = w - box_w - 50
    box_y = h - box_h - 45

    # Sfondo pillola semi-trasparente scuro con bordo dorato
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=14,
        fill=(10, 12, 16, 210),
        outline=(220, 180, 70, 230),
        width=2
    )
    # Testo "A.G." bianco brillante
    draw.text((box_x + pad_x, box_y + pad_y - 2), wm_text, font=font_watermark, fill=(255, 255, 255, 255))

    # Salvataggio
    if not output_filename:
        output_filename = f"favara_post_{int(os.path.getmtime(__file__))}.jpg"
    
    out_path = os.path.join(OUTPUT_DIR, output_filename)
    final_img = base.convert("RGB")
    final_img.save(out_path, "JPEG", quality=93)
    print(f"✅ Card generata con successo: {out_path}")
    return out_path

def crea_storia_favara(titolo, categoria, sottotitolo="", img_url=None, output_filename=None, tema="gold"):
    """
    Genera un'immagine verticale ad altissima risoluzione (1080x1920, 9:16)
    specificamente ottimizzata per le STORIE di Facebook della Pagina Favara.
    Include badge tematico, titolo leggibile, call-to-action e firma 'A.G.' in basso a destra.
    """
    w, h = 1080, 1920
    base = scarica_o_crea_base(img_url, w, h)
    
    # Applica overlay protettivo scuro per le storie (top 20%, bottom 45%)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    # Gradiente superiore (per badge)
    for y in range(350):
        alpha = int(140 * (1 - y / 350))
        draw_ov.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
        
    # Gradiente inferiore (per blocco testo e callout)
    start_y = h - 750
    for y in range(start_y, h):
        ratio = (y - start_y) / 750
        alpha = int(220 * ratio)
        draw_ov.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

    base = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(base)

    # 1. BADGE STORIA (In alto a sinistra, distanziato dal bordo per la UI delle storie)
    font_badge = ottieni_font(FONT_BOLD, 30)
    badge_text = f"  🏛️ FAVARA  •  {categoria.upper()}  "
    bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw, bh = bbox_b[2] - bbox_b[0] + 36, bbox_b[3] - bbox_b[1] + 24
    
    badge_x, badge_y = 60, 180  # Spazio per la barra superiore delle storie Facebook
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + bw, badge_y + bh],
        radius=14,
        fill=(220, 165, 30, 235),
        outline=(255, 255, 255, 220),
        width=2
    )
    draw.text((badge_x + 18, badge_y + 12), badge_text, font=font_badge, fill=(15, 10, 5, 255))

    # 2. TITOLO E CONTENUTO NELLA PARTE INFERIORE
    font_titolo = ottieni_font(FONT_BOLD, 56)
    font_sotto = ottieni_font(FONT_REGULAR, 34)
    font_cta = ottieni_font(FONT_BOLD, 32)

    parole = titolo.split()
    righe = []
    riga_corrente = ""
    for p in parole:
        test_riga = f"{riga_corrente} {p}".strip()
        bbox = draw.textbbox((0, 0), test_riga, font=font_titolo)
        if (bbox[2] - bbox[0]) < (w - 120):
            riga_corrente = test_riga
        else:
            if riga_corrente:
                righe.append(riga_corrente)
            riga_corrente = p
    if riga_corrente:
        righe.append(riga_corrente)
    
    righe = righe[:4]
    interlinea = 70
    altezza_testo = len(righe) * interlinea + (50 if sottotitolo else 0) + 120
    pos_y = h - 260 - altezza_testo

    for r in righe:
        draw.text((62, pos_y + 2), r, font=font_titolo, fill=(0, 0, 0, 220))
        draw.text((60, pos_y), r, font=font_titolo, fill=(255, 255, 255, 255))
        pos_y += interlinea

    if sottotitolo:
        pos_y += 12
        draw.text((62, pos_y + 2), sottotitolo[:65], font=font_sotto, fill=(0, 0, 0, 190))
        draw.text((60, pos_y), sottotitolo[:65], font=font_sotto, fill=(240, 220, 180, 255))
        pos_y += 50

    # Call-to-action per la storia
    pos_y += 20
    cta_text = "📲 Leggi il racconto completo nel post della pagina!"
    draw.text((62, pos_y + 2), cta_text, font=font_cta, fill=(0, 0, 0, 180))
    draw.text((60, pos_y), cta_text, font=font_cta, fill=(180, 230, 255, 255))

    # ── 3. WATERMARK REGOLA ESCLUSIVA: "A.G." IN BASSO A DESTRA ─────
    font_watermark = ottieni_font(FONT_BOLD, 32)
    wm_text = "A.G."
    bbox_wm = draw.textbbox((0, 0), wm_text, font=font_watermark)
    wm_w = bbox_wm[2] - bbox_wm[0]
    wm_h = bbox_wm[3] - bbox_wm[1]

    pad_x = 24
    pad_y = 12
    box_w = wm_w + (pad_x * 2)
    box_h = wm_h + (pad_y * 2)
    box_x = w - box_w - 60
    box_y = h - box_h - 120  # Margine per evitare la barra inferiore dell'app Facebook

    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=14,
        fill=(10, 12, 16, 215),
        outline=(220, 180, 70, 230),
        width=2
    )
    draw.text((box_x + pad_x, box_y + pad_y - 2), wm_text, font=font_watermark, fill=(255, 255, 255, 255))

    # Salvataggio
    if not output_filename:
        output_filename = f"storia_favara_{int(os.path.getmtime(__file__))}.jpg"
    
    out_path = os.path.join(OUTPUT_DIR, output_filename)
    final_img = base.convert("RGB")
    final_img.save(out_path, "JPEG", quality=93)
    print(f"✅ Storia generata con successo: {out_path}")
    return out_path

if __name__ == "__main__":
    print("🎨 Test generazione card grafica con watermark 'A.G.'...")
    test_img = crea_card_favara(
        titolo="Il Castello Chiaramonte nel Cuore di Favara",
        categoria="Monumenti & Storia",
        sottotitolo="Oltre sette secoli di fascino e cultura a Piazza Cavour",
        img_url="https://upload.wikimedia.org/wikipedia/commons/3/30/Favara_Piazza_Cavour_Castello_Chiaramonte.jpg",
        output_filename="test_castello_chiaramonte.jpg"
    )
    test_storia = crea_storia_favara(
        titolo="Il Castello Chiaramonte nel Cuore di Favara",
        categoria="Monumenti & Storia",
        sottotitolo="Oltre sette secoli di fascino e cultura a Piazza Cavour",
        img_url="https://upload.wikimedia.org/wikipedia/commons/3/30/Favara_Piazza_Cavour_Castello_Chiaramonte.jpg",
        output_filename="test_storia_castello.jpg"
    )
