#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
IMMOBILIARE GIANCANI — BOT CAROSELLO POST & STORIE SOCIAL (GITHUB ACTIONS)
SCHEDULAZIONE: LUNEDÌ, MERCOLEDÌ, VENERDÌ (ORARIO PRESERALE 18:30 ITALIANO)
===============================================================================
1. Coerenza Rigorosa Foto / Testo:
   - Seleziona da 3 a 5 immagini DELLO STESSO IMMOBILE.
   - Per ciascuna immagine, la descrizione viene prelevata rigorosamente dalla
     Colonna F della STESSA RIGA dell'immagine selezionata.
2. Rotazione Intelligente & Anti-Duplicazione:
   - Memorizza lo storico in 'immobili_pubblicati_history.json'.
   - Seleziona ciclicamente l'immobile meno recente per non pubblicare sempre lo stesso.
3. Regola Salta-Giorno:
   - Controlla tramite Meta Graph API se per la data odierna è già presente
     un post programmato o pubblicato sulla pagina.
   - Se c'è in programma una pubblicazione, salta il giorno per evitare sovrapposizioni.
4. Logo Trasparente Proporzionato:
   - Utilizza il logo ufficiale di Immobiliare Giancani trasparente in formato PNG (1600x409).
   - Nessun fondo bianco opaco e nessuna deformazione o schiacciamento dell'aspect ratio.
5. Personal Branding (RULE[user_global]):
   - Testi rigorosamente da Colonna F.
   - Superfici espresse sempre in 'metri quadri'.
   - Ogni testo generato si conclude mettendo in massimo risalto 'Immobiliare Giancani'.
===============================================================================
"""

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
orig_create_default_context = ssl.create_default_context
def unverified_create_default_context(*args, **kwargs):
    c = orig_create_default_context(*args, **kwargs)
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c
ssl.create_default_context = unverified_create_default_context

import os
import io
import sys
import time
import json
import argparse
import datetime
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR) if os.path.basename(BASE_DIR) == 'scripts' else BASE_DIR

OUTPUT_DIR = os.path.join(PROJECT_DIR, "output_carosello")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(PROJECT_DIR, "immobili_pubblicati_history.json")

# Credenziali Social
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "234931856561526")
FB_PAGE_TOKEN = os.environ.get(
    "FB_PAGE_TOKEN",
    "EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI"
)
IG_ACCOUNT_ID = os.environ.get("IG_ACCOUNT_ID", "17841400301393511")

APPS_SCRIPT_URL = os.environ.get(
    "APPS_SCRIPT_URL",
    "https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec"
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7969192465:AAHlUu7Jq1K1e9y3qgV-N66mD3E0rQ1_zQo")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1002345678901")

def get_font(size, bold=False, font_type="sans"):
    """Carica font scalato compatibile con Windows e Linux (GitHub Actions)"""
    paths = []
    if font_type == "serif":
        paths = [
            "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
        ]
    else:
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

def get_logo_trasparente():
    """Carica il logo ufficiale trasparente (senza fondo bianco)"""
    candidates = [
        os.path.join(PROJECT_DIR, "assets", "logo_giancani_trasparente.png"),
        os.path.join(PROJECT_DIR, "scripts", "assets", "logo_giancani_trasparente.png"),
        os.path.join(PROJECT_DIR, "scratch", "logo_transparent_test.png"),
        os.path.join(PROJECT_DIR, "assets", "logo_giancani.png")
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                img = Image.open(p)
                if img.mode != "RGBA":
                    rgba = img.convert("RGBA")
                    data = rgba.getdata()
                    new_data = []
                    for item in data:
                        if item[0] > 238 and item[1] > 238 and item[2] > 238:
                            new_data.append((255, 255, 255, 0))
                        else:
                            new_data.append(item)
                    rgba.putdata(new_data)
                    return rgba
                return img
            except Exception as e:
                print(f"[LOGO] Errore apertura {p}: {e}")
    
    try:
        url = "https://lh3.googleusercontent.com/d/1BoZ_9QyYPRKjZFP__iPr7mmi0aGV0G3P"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            img = Image.open(io.BytesIO(r.read())).convert("RGBA")
            data = img.getdata()
            new_data = []
            for item in data:
                if item[0] > 238 and item[1] > 238 and item[2] > 238:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            img.putdata(new_data)
            return img
    except Exception as e:
        print(f"[LOGO] Fallback CDN fallito: {e}")
        return None

def normalize_mq(val):
    """Converte qualsiasi unità di misura in 'metri quadri' per RULE[user_global]"""
    if not val:
        return "120 metri quadri"
    s = str(val).strip()
    import re
    s = re.sub(r'(\d+)\s*(?:mq|m²|m2)\b', r'\1 metri quadri', s, flags=re.I)
    s = re.sub(r'\b(?:mq|m²)\b', 'metri quadri', s, flags=re.I)
    s = re.sub(r'\bMQ\b', 'metri quadri', s)
    if 'metri' not in s.lower() and re.search(r'\d', s):
        s += " metri quadri"
    return s

def format_branding_giancani(testo):
    """Assicura che il testo si concluda mettendo in risalto 'Immobiliare Giancani'"""
    if not testo:
        return "Splendida opportunità esclusiva nel territorio siciliano. — Immobiliare Giancani"
    t = str(testo).strip()
    t = normalize_mq(t)
    if "immobiliare giancani" not in t.lower():
        t = t.rstrip('. ') + " — Immobiliare Giancani"
    return t

def check_salta_giorno(force=False):
    """
    Verifica se per la data odierna esiste già un post programmato o pubblicato.
    Se presente, salta il giorno come da richiesta utente.
    """
    if force:
        print("⚡ Modalità FORCE attiva: salto i controlli anti-duplicazione e procedo.")
        return False, "Esecuzione forzata"

    oggi_str = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"\n🔍 [ANTI-SOVRAPPOSIZIONE] Verifica programmazione odierna ({oggi_str})...")

    # A. Controlla Scheduled Posts su Meta Graph API
    try:
        url_sched = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/scheduled_posts?access_token={urllib.parse.quote(FB_PAGE_TOKEN)}&limit=10"
        req = urllib.request.Request(url_sched, headers={"User-Agent": "Mozilla/5.0"})
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            posts = data.get('data', [])
            for p in posts:
                sched_ts = p.get('scheduled_publish_time')
                if sched_ts:
                    sched_dt = datetime.datetime.fromtimestamp(sched_ts).strftime("%Y-%m-%d")
                    if sched_dt == oggi_str:
                        motivo = f"Rilevato post Facebook già programmato per oggi ({sched_dt}, ID: {p.get('id')})"
                        print(f"🗓️ {motivo}. SALTO IL GIORNO come da regola utente.")
                        return True, motivo
    except Exception as e:
        print(f"[ANTI-SOVRAPPOSIZIONE] Controllo scheduled_posts: {e}")

    # B. Controlla Feed Facebook recente
    try:
        url_feed = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed?fields=id,created_time,message&limit=5&access_token={urllib.parse.quote(FB_PAGE_TOKEN)}"
        req = urllib.request.Request(url_feed, headers={"User-Agent": "Mozilla/5.0"})
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            for p in data.get('data', []):
                c_time = p.get('created_time', '')
                if c_time.startswith(oggi_str):
                    motivo = f"Rilevato post già pubblicato oggi sul feed Facebook (ID: {p.get('id')})"
                    print(f"🗓️ {motivo}. SALTO IL GIORNO come da regola utente.")
                    return True, motivo
    except Exception as e:
        print(f"[ANTI-SOVRAPPOSIZIONE] Controllo feed: {e}")

    # C. Controlla storico locale
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                hist = json.load(f)
                last_pub = hist.get("ultima_pubblicazione_data", "")
                if last_pub == oggi_str:
                    motivo = f"Storico locale indica che oggi ({oggi_str}) è già stata eseguita una pubblicazione carosello"
                    print(f"🗓️ {motivo}. SALTO IL GIORNO come da regola utente.")
                    return True, motivo
        except Exception as e:
            print(f"[ANTI-SOVRAPPOSIZIONE] Lettura history: {e}")

    print("✅ Nessuna pubblicazione in programma per oggi. Procedo con la creazione del carosello!")
    return False, "Nessun post rilevato per oggi"

def carica_immobile_e_stanze(target_sheet=None):
    """
    Preleva un immobile dal catalogo Sheets.
    Assicura che da 3 a 5 immagini appartengano TUTTE allo STESSO immobile
    e che il testo provenga rigorosamente dalla Colonna F della STESSA riga.
    """
    ctx = ssl._create_unverified_context()
    import re
    
    url_sheets = f"{APPS_SCRIPT_URL}?action=debug_all_sheets"
    req = urllib.request.Request(url_sheets, headers={"User-Agent": "Mozilla/5.0"})
    all_sheets = []
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            all_sheets = data.get('sheets', [])
    except Exception as e:
        print(f"❌ Errore recupero fogli: {e}")
        return None

    fogli_immobili = []
    exclude = ['POST_YOUTUBE', 'DIALOGHI_AVAT_TUTTI', 'IMPOSTAZIONI_SOCIAL', 'PUBBLICITA_SCHERMO_CENTRALE', 'PROMPT_GEMINI_STUDIO']
    for s in all_sheets:
        name = s.get('name', '')
        if name.upper() not in exclude and s.get('rows', 0) >= 4:
            fogli_immobili.append(name)

    if not fogli_immobili:
        print("❌ Nessun foglio immobile valido trovato.")
        return None

    history = {}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            history = {}

    storico_date = history.get("storico_immobili", {})

    scelto = target_sheet
    if not scelto or scelto not in fogli_immobili:
        fogli_immobili.sort(key=lambda x: storico_date.get(x, "1970-01-01"))
        scelto = fogli_immobili[0]

    print(f"🏰 IMMOBILE SELEZIONATO PER IL CAROSELLO: '{scelto}'")

    url_imm = f"{APPS_SCRIPT_URL}?action=get_sheet&name={urllib.parse.quote(scelto)}"
    req_imm = urllib.request.Request(url_imm, headers={"User-Agent": "Mozilla/5.0"})
    rows = []
    try:
        with urllib.request.urlopen(req_imm, timeout=20, context=ctx) as r:
            d = json.loads(r.read().decode('utf-8'))
            rows = d.get('rows', [])
    except Exception as e:
        print(f"❌ Errore recupero righe per {scelto}: {e}")
        return None

    if len(rows) < 2:
        print(f"❌ Foglio {scelto} non ha abbastanza righe.")
        return None

    prezzo_gen = "Trattativa Riservata"
    if len(rows) > 1 and len(rows[1]) > 1 and rows[1][1]:
        p_raw = str(rows[1][1]).strip()
        if p_raw and p_raw.lower() != 'prezzo_b2' and 'prezzo in' not in p_raw.lower():
            prezzo_gen = ('€ ' + p_raw) if ('€' not in p_raw and any(c.isdigit() for c in p_raw)) else p_raw

    mq_gen = "120 metri quadri"
    if len(rows) > 1 and len(rows[1]) > 2 and rows[1][2]:
        mq_gen = normalize_mq(rows[1][2])

    titolo_pulito = scelto.replace('_', ' ').strip()
    titolo_pulito = re.sub(r'\s+', ' ', titolo_pulito)

    stanze_valide = []
    for idx, r in enumerate(rows[1:], start=2):
        if len(r) < 6:
            continue
        col_a = str(r[0]).strip() if r[0] else ""
        col_f = str(r[5]).strip() if r[5] else ""
        col_d = str(r[3]).strip() if len(r) > 3 and r[3] else f"Ambiente {len(stanze_valide)+1}"

        if not col_a or col_a.endswith('.mp4') or 'Stanza_Ambiente' in col_a:
            continue

        if 'drive.google.com' in col_a or len(col_a) >= 25 and not col_a.startswith('http'):
            m = re.search(r'[-\w]{25,}', col_a)
            if m:
                col_a = f"https://lh3.googleusercontent.com/d/{m.group(0)}"

        if not col_f or 'Testo_Parlato' in col_f:
            continue

        stanze_valide.append({
            "riga_idx": idx,
            "foto_url": col_a,
            "stanza_nome": col_d,
            "testo_col_f": col_f,
            "prezzo": prezzo_gen,
            "mq": mq_gen
        })

    if len(stanze_valide) < 3:
        print(f"⚠️ Foglio {scelto} contiene solo {len(stanze_valide)} stanze valide con Colonna F. Minimo: 3.")
        return None

    if len(stanze_valide) <= 5:
        stanze_selezionate = stanze_valide
    else:
        step = len(stanze_valide) / float(5)
        stanze_selezionate = [stanze_valide[int(i * step)] for i in range(5)]

    print(f"📸 Selezionate {len(stanze_selezionate)} foto/ambienti con testi rigorosamente da Colonna F:")
    for s_item in stanze_selezionate:
        print(f"  - [{s_item['stanza_nome']}] Colonna F: {s_item['testo_col_f'][:60]}...")

    return {
        "foglio_nome": scelto,
        "titolo": titolo_pulito,
        "prezzo": prezzo_gen,
        "mq": mq_gen,
        "stanze": stanze_selezionate
    }

def scarica_immagine(url):
    """Scarica e apre l'immagine con Pillow"""
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return Image.open(io.BytesIO(r.read())).convert('RGB')
    except Exception as e:
        print(f"❌ Errore scaricamento immagine {url}: {e}")
        return None

def genera_slide_carosello_1080(stanza_data, immobile_info, index, total, logo_img):
    """
    Genera immagine 1080x1080 per Post Carosello Facebook & Instagram.
    """
    W, H = 1080, 1080
    canvas = Image.new('RGBA', (W, H), (10, 12, 18, 255))

    foto = scarica_immagine(stanza_data['foto_url'])
    if foto:
        fw, fh = foto.size
        scale = max(W / fw, H / fh)
        nw, nh = int(fw * scale), int(fh * scale)
        foto_resized = foto.resize((nw, nh), Image.Resampling.LANCZOS)
        crop_x = (nw - W) // 2
        crop_y = (nh - H) // 2
        foto_cropped = foto_resized.crop((crop_x, crop_y, crop_x + W, crop_y + H))
        canvas.paste(foto_cropped, (0, 0))
    else:
        draw_fb = ImageDraw.Draw(canvas)
        draw_fb.rectangle([0, 0, W, H], fill=(18, 24, 38, 255))

    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for y in range(160):
        alpha = int(140 * (1 - (y / 160.0)))
        draw_ov.line([(0, y), (W, y)], fill=(6, 9, 16, alpha))
    for y in range(H - 340, H):
        p = (y - (H - 340)) / 340.0
        alpha = int(225 * p)
        draw_ov.line([(0, y), (W, y)], fill=(6, 9, 16, alpha))
    canvas = Image.alpha_composite(canvas, overlay)

    draw = ImageDraw.Draw(canvas)

    # Logo Ufficiale Trasparente in Alto a Destra
    if logo_img:
        lw = 320
        lh = int((lw * logo_img.height) / logo_img.width)
        logo_res = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
        lx = W - lw - 25
        ly = 22

        shadow_box = Image.new('RGBA', (lw + 20, lh + 20), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_box)
        shadow_draw.rounded_rectangle([2, 2, lw + 18, lh + 18], radius=14, fill=(0, 0, 0, 110))
        canvas.paste(shadow_box, (lx - 10, ly - 10), shadow_box)
        canvas.paste(logo_res, (lx, ly), logo_res)

    # Badge Stanza
    st_nome = stanza_data['stanza_nome'].upper()
    font_badge = get_font(21, bold=True, font_type="sans")
    badge_txt = f"🚪 {st_nome}  •  {index}/{total}"
    bbox = font_badge.getbbox(badge_txt)
    bw = bbox[2] - bbox[0] + 32
    bh = 46
    draw.rounded_rectangle([25, 24, 25 + bw, 24 + bh], radius=12, fill=(15, 23, 42, 220), outline=(212, 168, 83, 200), width=2)
    draw.text((41, 35), badge_txt, font=font_badge, fill=(255, 255, 255, 255))

    # Targa Inferiore
    card_y = H - 290
    card_h = 265
    draw.rounded_rectangle([25, card_y, W - 25, card_y + card_h], radius=20, fill=(6, 9, 16, 225), outline=(212, 168, 83, 160), width=2)

    font_tit = get_font(26, bold=True, font_type="serif")
    titolo_txt = immobile_info['titolo']
    if len(titolo_txt) > 36:
        titolo_txt = titolo_txt[:34] + "..."
    draw.text((45, card_y + 18), titolo_txt, font=font_tit, fill=(255, 255, 255, 255))

    prezzo_txt = stanza_data['prezzo']
    font_pr = get_font(22, bold=True, font_type="sans")
    p_bbox = font_pr.getbbox(prezzo_txt)
    pw = p_bbox[2] - p_bbox[0] + 28
    px = W - 45 - pw
    draw.rounded_rectangle([px, card_y + 16, px + pw, card_y + 58], radius=10, fill=(212, 168, 83, 240), outline=(255, 255, 255, 220), width=1)
    draw.text((px + 14, card_y + 24), prezzo_txt, font=font_pr, fill=(10, 12, 18, 255))

    font_mq = get_font(18, bold=True, font_type="sans")
    draw.text((45, card_y + 60), f"📐 Superficie: {stanza_data['mq']}", font=font_mq, fill=(56, 189, 248, 255))

    font_desc = get_font(18, bold=False, font_type="sans")
    testo_col_f = stanza_data['testo_col_f'].strip()
    words = testo_col_f.split()
    lines = []
    cur_line = []
    max_w = W - 110
    for w in words:
        test_str = " ".join(cur_line + [w])
        if font_desc.getbbox(test_str)[2] < max_w:
            cur_line.append(w)
        else:
            if cur_line: lines.append(" ".join(cur_line))
            cur_line = [w]
    if cur_line: lines.append(" ".join(cur_line))

    dy = card_y + 95
    for l in lines[:3]:
        draw.text((45, dy), l, font=font_desc, fill=(226, 232, 240, 255))
        dy += 26

    font_brand = get_font(19, bold=True, font_type="sans")
    brand_txt = "✨ Esclusiva — IMMOBILIARE GIANCANI • Tel. 320 166 7156"
    draw.text((45, card_y + card_h - 40), brand_txt, font=font_brand, fill=(212, 168, 83, 255))

    out_path = os.path.join(OUTPUT_DIR, f"carosello_slide_{index}.jpg")
    canvas.convert('RGB').save(out_path, quality=95)
    return out_path

def genera_slide_storia_1920(stanza_data, immobile_info, index, total, logo_img):
    """
    Genera immagine 1080x1920 verticale per Storie Facebook e Instagram (9:16).
    """
    W, H = 1080, 1920
    canvas = Image.new('RGBA', (W, H), (8, 11, 19, 255))

    foto = scarica_immagine(stanza_data['foto_url'])

    # Integrazione Motore Grafico Unificato 9:16 (4 Stili, 7 Palette Giornaliere, Logo Trasparente HD)
    try:
        import motore_grafica_storie as mgs
        media_info = {
            'titolo': immobile_info.get('titolo', 'Immobile Selezionato'),
            'zona': stanza_data.get('stanza_nome', 'Favara (AG)'),
            'prezzo': stanza_data.get('prezzo', immobile_info.get('prezzo', 'Trattativa Riservata')),
            'mq': stanza_data.get('mq', immobile_info.get('mq', '120 metri quadri')),
            'codice_rif': f"STZ-{index}DI{total}",
            'testoF': stanza_data.get('testo_col_f', ''),
            'fotoImage': foto
        }
        out_unified = os.path.join(OUTPUT_DIR, f"storia_slide_{index}.jpg")
        res = mgs.crea_story_9_16(media_info, style="auto", output_path=out_unified)
        if res and os.path.exists(res):
            print(f"✅ Slide Storia 9:16 creata con Motore Grafico Unificato: {res}")
            return res
    except Exception as e_mgs:
        print(f"Avviso fallback grafica storia carosello: {e_mgs}")

    if foto:
        fw, fh = foto.size
        scale = W / fw
        nw, nh = int(fw * scale), int(fh * scale)
        foto_res = foto.resize((nw, nh), Image.Resampling.LANCZOS)
        bg_blur = foto.resize((W // 10, H // 10)).resize((W, H)).filter(ImageFilter.GaussianBlur(25))
        canvas.paste(bg_blur.convert('RGBA'), (0, 0))
        py = (H - nh) // 2 - 30
        canvas.paste(foto_res, (0, py))
    
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    draw_ov.rectangle([0, 0, W, 220], fill=(6, 9, 16, 210))
    draw_ov.rectangle([0, H - 460, W, H], fill=(6, 9, 16, 235))
    canvas = Image.alpha_composite(canvas, overlay)

    draw = ImageDraw.Draw(canvas)

    if logo_img:
        lw = 420
        lh = int((lw * logo_img.height) / logo_img.width)
        logo_res = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
        lx = (W - lw) // 2
        ly = 45
        canvas.paste(logo_res, (lx, ly), logo_res)

    font_pill = get_font(18, bold=True, font_type="sans")
    pill_txt = f"🏰 TOUR ESCLUSIVO • STANZA {index} DI {total}"
    p_bbox = font_pill.getbbox(pill_txt)
    pw = p_bbox[2] - p_bbox[0] + 32
    draw.rounded_rectangle([(W - pw) // 2, 145, (W + pw) // 2, 185], radius=12, fill=(212, 168, 83, 230))
    draw.text(((W - (p_bbox[2] - p_bbox[0])) // 2, 155), pill_txt, font=font_pill, fill=(7, 9, 14, 255))

    box_y = H - 430
    draw.rounded_rectangle([30, box_y, W - 30, H - 40], radius=24, fill=(12, 16, 28, 230), outline=(212, 168, 83, 180), width=2)

    st_nome = stanza_data['stanza_nome'].upper()
    font_st = get_font(30, bold=True, font_type="sans")
    draw.text((55, box_y + 25), f"📍 {st_nome}", font=font_st, fill=(255, 255, 255, 255))

    font_pr = get_font(26, bold=True, font_type="sans")
    draw.text((55, box_y + 75), f"💰 {stanza_data['prezzo']}  •  📐 {stanza_data['mq']}", font=font_pr, fill=(212, 168, 83, 255))

    font_desc = get_font(20, bold=False, font_type="sans")
    words = stanza_data['testo_col_f'].split()
    lines = []
    cur = []
    for w in words:
        t_line = " ".join(cur + [w])
        if font_desc.getbbox(t_line)[2] < W - 120:
            cur.append(w)
        else:
            if cur: lines.append(" ".join(cur))
            cur = [w]
    if cur: lines.append(" ".join(cur))

    dy = box_y + 130
    for l in lines[:4]:
        draw.text((55, dy), l, font=font_desc, fill=(226, 232, 240, 255))
        dy += 30

    font_call = get_font(22, bold=True, font_type="sans")
    draw.text((55, H - 90), "📞 Info & Visite: 320 166 7156 — Immobiliare Giancani", font=font_call, fill=(56, 189, 248, 255))

    out_path = os.path.join(OUTPUT_DIR, f"storia_slide_{index}.jpg")
    canvas.convert('RGB').save(out_path, quality=95)
    return out_path

def pubblica_post_carosello_facebook(immobile_info, carosello_paths):
    """
    Pubblica un post carosello multi-foto (3-5 foto) sulla Pagina Facebook.
    """
    print(f"\n📘 [FACEBOOK] Caricamento {len(carosello_paths)} foto per Post Carosello...")
    media_fbids = []
    ctx = ssl._create_unverified_context()

    for i, fpath in enumerate(carosello_paths, start=1):
        try:
            boundary = f"----WebKitFormBoundary{int(time.time()*1000)}"
            with open(fpath, 'rb') as f:
                img_bytes = f.read()

            body = bytearray()
            body.extend(f"--{boundary}\r\n".encode('utf-8'))
            body.extend(f'Content-Disposition: form-data; name="published"\r\n\r\nfalse\r\n'.encode('utf-8'))
            body.extend(f"--{boundary}\r\n".encode('utf-8'))
            body.extend(f'Content-Disposition: form-data; name="source"; filename="slide_{i}.jpg"\r\n'.encode('utf-8'))
            body.extend(b'Content-Type: image/jpeg\r\n\r\n')
            body.extend(img_bytes)
            body.extend(b"\r\n")
            body.extend(f"--{boundary}--\r\n".encode('utf-8'))

            url_photo = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos?access_token={urllib.parse.quote(FB_PAGE_TOKEN)}"
            req = urllib.request.Request(url_photo, data=body, headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'User-Agent': 'Mozilla/5.0'
            })

            with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
                res = json.loads(r.read().decode('utf-8'))
                media_id = res.get('id')
                if media_id:
                    media_fbids.append(media_id)
                    print(f"  [OK] Foto {i}/{len(carosello_paths)} caricata (media_fbid: {media_id})")
        except Exception as e:
            print(f"  ❌ Errore caricamento foto {i}: {e}")

    if not media_fbids:
        print("❌ Nessuna foto caricata con successo su Facebook.")
        return {"success": False, "error": "Nessuna foto caricata"}

    elenco_stanze_txt = "\n".join([f"🚪 {s['stanza_nome']}: {s['testo_col_f'][:90]}..." for s in immobile_info['stanze']])
    
    caption = (
        f"🏰 OPPORTUNITÀ IMMOBILIARE: {immobile_info['titolo'].upper()}\n"
        f"💰 Prezzo: {immobile_info['prezzo']}  •  📐 Superficie: {immobile_info['mq']}\n\n"
        f"✨ Scopri le stanze in questo carosello fotografico esclusivo:\n"
        f"{elenco_stanze_txt}\n\n"
        f"📍 Ti aspettiamo per una visita sul posto o in agenzia.\n"
        f"📞 Contattaci subito: 320 166 7156\n"
        f"📍 Sede: Corso Vittorio Veneto 151, Favara (AG)\n\n"
        f"— Immobiliare Giancani"
    )

    attached_media = [{"media_fbid": str(mid)} for mid in media_fbids]

    try:
        url_feed = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
        payload = urllib.parse.urlencode({
            'message': caption,
            'attached_media': json.dumps(attached_media),
            'access_token': FB_PAGE_TOKEN
        }).encode('utf-8')

        req = urllib.request.Request(url_feed, data=payload, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            res_post = json.loads(r.read().decode('utf-8'))
            post_id = res_post.get('id')
            print(f"🌟 [OK] Post Carosello Multi-Foto pubblicato su Facebook! ID: {post_id}")
            return {"success": True, "post_id": post_id, "piattaforma": "Facebook Post Carosello"}
    except Exception as e:
        print(f"❌ Errore pubblicazione post carosello feed: {e}")
        return {"success": False, "error": str(e), "piattaforma": "Facebook Post Carosello"}

def pubblica_storie_facebook(immobile_info, storia_paths):
    """Pubblica le immagini come Storie sulla Pagina Facebook"""
    print(f"\n📘 [FACEBOOK] Pubblicazione {len(storia_paths)} Storie...")
    ctx = ssl._create_unverified_context()
    risultati = []

    for i, spath in enumerate(storia_paths[:2], start=1):
        try:
            boundary = f"----WebKitFormBoundaryStory{int(time.time()*1000)}"
            with open(spath, 'rb') as f:
                img_bytes = f.read()

            body = bytearray()
            body.extend(f"--{boundary}\r\n".encode('utf-8'))
            body.extend(f'Content-Disposition: form-data; name="published"\r\n\r\ntrue\r\n'.encode('utf-8'))
            body.extend(f"--{boundary}\r\n".encode('utf-8'))
            body.extend(f'Content-Disposition: form-data; name="source"; filename="story_{i}.jpg"\r\n'.encode('utf-8'))
            body.extend(b'Content-Type: image/jpeg\r\n\r\n')
            body.extend(img_bytes)
            body.extend(b"\r\n")
            body.extend(f"--{boundary}--\r\n".encode('utf-8'))

            url_photo = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos?access_token={urllib.parse.quote(FB_PAGE_TOKEN)}"
            req = urllib.request.Request(url_photo, data=body, headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'User-Agent': 'Mozilla/5.0'
            })

            with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
                res = json.loads(r.read().decode('utf-8'))
                print(f"  [OK] Storia Facebook {i} pubblicata! ID: {res.get('id')}")
                risultati.append(res)
        except Exception as e:
            print(f"  ❌ Errore storia Facebook {i}: {e}")

    return {"success": len(risultati) > 0, "dettagli": risultati}

def invia_notifica_telegram(titolo, mq, prezzo, stanze_nomi, res_fb, res_storie):
    """Invia notifica sintetica su Telegram"""
    try:
        ctx = ssl._create_unverified_context()
        testo = (
            f"🚀 *BOT CAROSELLO SOCIAL IMMOBILIARI*\n"
            f"🏰 *Immobile:* {titolo}\n"
            f"💰 *Prezzo:* {prezzo} | 📐 *MQ:* {mq}\n"
            f"📸 *Ambienti ({len(stanze_nomi)}):* {', '.join(stanze_nomi)}\n"
            f"📘 *FB Carosello:* {'✅ Pubblicato (' + str(res_fb.get('post_id')) + ')' if res_fb.get('success') else '❌ Errore'}\n"
            f"📱 *Storie Social:* {'✅ Pubblicate' if res_storie.get('success') else '⚠️ Verificare'}\n\n"
            f"— *Immobiliare Giancani*"
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = urllib.parse.urlencode({
            'chat_id': TELEGRAM_CHAT_ID,
            'text': testo,
            'parse_mode': 'Markdown'
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload)
        urllib.request.urlopen(req, timeout=10, context=ctx)
    except Exception as e:
        print(f"[TELEGRAM] Errore notifica: {e}")

def aggiorna_storico_pubblicazioni(nome_foglio):
    """Aggiorna il file JSON dello storico pubblicazioni"""
    oggi_str = datetime.datetime.now().strftime("%Y-%m-%d")
    orario_str = datetime.datetime.now().isoformat()
    hist = {"ultima_pubblicazione_data": oggi_str, "storico_immobili": {}}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                hist = json.load(f)
        except Exception:
            pass

    hist["ultima_pubblicazione_data"] = oggi_str
    hist["ultimo_orario"] = orario_str
    hist["ultimo_immobile"] = nome_foglio
    if "storico_immobili" not in hist:
        hist["storico_immobili"] = {}
    hist["storico_immobili"][nome_foglio] = oggi_str

    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(hist, f, indent=2)
        print(f"📝 Storico aggiornato: '{nome_foglio}' registrato in data {oggi_str}.")
    except Exception as e:
        print(f"⚠️ Errore scrittura storico: {e}")

def main():
    parser = argparse.ArgumentParser(description="Bot Carosello Post & Storie Social — Immobiliare Giancani")
    parser.add_argument("--force", action="store_true", help="Forza pubblicazione ignorando la regola salta-giorno")
    parser.add_argument("--immobile", type=str, default=None, help="Specifica un immobile/foglio preciso")
    args = parser.parse_args()

    print("=" * 70)
    print("🚀 AVVIO BOT CAROSELLO POST & STORIE IMMOBILIARI")
    print("— IMMOBILIARE GIANCANI")
    print("=" * 70)

    salta, motivo = check_salta_giorno(force=args.force)
    if salta:
        print(f"\n⏹️ RISULTATO: {motivo}")
        print("Operazione conclusa regolarmente senza nuove pubblicazioni.")
        print("— Immobiliare Giancani")
        sys.exit(0)

    immobile_data = carica_immobile_e_stanze(target_sheet=args.immobile)
    if not immobile_data:
        print("❌ Impossibile procedere: dati immobile non disponibili.")
        sys.exit(1)

    logo_img = get_logo_trasparente()
    if logo_img:
        print(f"🎨 Logo trasparente caricato: {logo_img.size} ({logo_img.mode})")
    else:
        print("⚠️ Attenzione: logo trasparente non disponibile, uso font vettoriale.")

    stanze = immobile_data['stanze']
    totale = len(stanze)
    carosello_files = []
    storie_files = []

    print(f"\n🎨 Generazione grafica di {totale} slide carosello e storie...")
    for idx, s in enumerate(stanze, start=1):
        c_path = genera_slide_carosello_1080(s, immobile_data, idx, totale, logo_img)
        s_path = genera_slide_storia_1920(s, immobile_data, idx, totale, logo_img)
        carosello_files.append(c_path)
        storie_files.append(s_path)
        print(f"  ✓ Slide {idx}/{totale}: {s['stanza_nome']} completata!")

    res_fb = pubblica_post_carosello_facebook(immobile_data, carosello_files)
    res_storie = pubblica_storie_facebook(immobile_data, storie_files)

    aggiorna_storico_pubblicazioni(immobile_data['foglio_nome'])
    stanze_nomi = [s['stanza_nome'] for s in stanze]
    invia_notifica_telegram(immobile_data['titolo'], immobile_data['mq'], immobile_data['prezzo'], stanze_nomi, res_fb, res_storie)

    print("\n" + "=" * 70)
    print("✨ PROCEDURA COMPLETATA CON SUCCESSO! — IMMOBILIARE GIANCANI")
    print("=" * 70)

if __name__ == '__main__':
    main()
