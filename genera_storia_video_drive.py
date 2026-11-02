#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═════════════════════════════════════════════════════════════════════════════════
 IMMOBILIARE GIANCANI — GENERATORE AUTOMATICO STORIE DA VIDEO DRIVE (9:16)
═════════════════════════════════════════════════════════════════════════════════
 Flusso di lavoro per VIDEO SENZA TESTO caricati su Google Drive:
 1. Preleva il video muto/grezzo da Google Drive (o cartella locale).
 2. Estrae una frase che incuriosisce, stimola o dà prestigio all'agenzia
    rigorosamente dalla Colonna F della scheda/database 'FRASI_PRESTIGIO_STORIE'.
 3. Applica il Logo ufficiale in alto e un box semi-trasparente scuro (opacità 60%)
    in basso con la frase elegante e personal branding '— Immobiliare Giancani'.
 4. Aggiunge una base musicale professionale sincronizzata con dissolvenza finale.
 5. Invia automaticamente un'email con allegato MP4 e testo pronto per i social.
═════════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import re
import csv
import io
import time
import json
import random
import datetime
import argparse
import textwrap
import smtplib
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from PIL import Image, ImageDraw, ImageFont

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
MUSIC_DIR = os.path.join(BASE_DIR, "musica_sottofondo")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "video_storie_output")
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo_giancani_trasparente.png")
CSV_FRASI_LOCALE = os.path.join(BASE_DIR, "database_frasi_prestigio_storie.csv")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)

DEFAULT_SHEET_ID = os.environ.get("SPREADSHEET_ID") or "1s68pw0WEUcV0ZqltiahAqCp_r5rsycSjxKNh0VZQq_g"
DEFAULT_EMAIL = os.environ.get("DEST_EMAIL") or "giancaniimmobiliare@gmail.com"
BRANDING_SUFFIX = "— Immobiliare Giancani"


# ─────────────────────────────────────────────────────────────────────────────
# 1. LETTURA FRASI PRESTIGIO (RIGOROSAMENTE COLONNA F)
# ─────────────────────────────────────────────────────────────────────────────

def carica_frasi_prestigio(sheet_id=DEFAULT_SHEET_ID):
    """
    Carica le frasi dalla scheda Google Sheets 'FRASI_PRESTIGIO_STORIE',
    con fallback sul file CSV locale 'database_frasi_prestigio_storie.csv'.
    Estrae rigorosamente dalla Colonna F (indice 5, 0-based).
    """
    frasi = []
    
    # 1. Tentativo da Google Sheets
    url_sheet = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=FRASI_PRESTIGIO_STORIE"
    try:
        res = requests.get(url_sheet, verify=False, timeout=12)
        if res.status_code == 200 and len(res.text) > 100:
            reader = csv.reader(io.StringIO(res.text))
            rows = list(reader)
            # Verifica che sia la scheda attesa (intestazione contiene Categoria e Colonna F)
            if len(rows) > 1 and len(rows[0]) >= 6 and 'Categoria' in rows[0][1]:
                for r in rows[1:]:
                    if len(r) > 5 and r[5].strip():
                        frasi.append({
                            "id": r[0].strip() if len(r) > 0 else "1",
                            "categoria": r[1].strip() if len(r) > 1 else "Prestigio & Valore",
                            "titolo": r[2].strip() if len(r) > 2 else "L'Arte dell'Abitare",
                            "frase_slogan": r[3].strip() if len(r) > 3 else "",
                            "focus": r[4].strip() if len(r) > 4 else "Eccellenza",
                            "colonna_f": r[5].strip(),
                            "stato": r[6].strip() if len(r) > 6 else "Attivo"
                        })
                print(f"✅ Caricate {len(frasi)} frasi da Google Sheets (Scheda: FRASI_PRESTIGIO_STORIE).")
    except Exception as e:
        print(f"⚠️ Impossibile scaricare foglio online ({e}), uso archivio locale.")

    # 2. Fallback su CSV locale
    if not frasi and os.path.exists(CSV_FRASI_LOCALE):
        with open(CSV_FRASI_LOCALE, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            rows = list(reader)
            for r in rows[1:]:
                if len(r) > 5 and r[5].strip():
                    frasi.append({
                        "id": r[0].strip(),
                        "categoria": r[1].strip(),
                        "titolo": r[2].strip(),
                        "frase_slogan": r[3].strip(),
                        "focus": r[4].strip(),
                        "colonna_f": r[5].strip(),
                        "stato": r[6].strip() if len(r) > 6 else "Attivo"
                    })
        print(f"✅ Caricate {len(frasi)} frasi da database CSV locale.")

    return frasi


def seleziona_frase(frasi, phrase_id=None):
    """Seleziona la frase specificata o ne sceglie una a rotazione/casuale."""
    if not frasi:
        return {
            "id": "1",
            "categoria": "Prestigio & Valore",
            "titolo": "L'Arte dell'Abitare",
            "frase_slogan": "Il vero lusso è abitare dove respiri pace e libertà.",
            "colonna_f": f"Il vero lusso non è ciò che mostri, ma lo spazio, la luce e la quiete in cui scegli di vivere. La tua dimora ideale inizia da qui. {BRANDING_SUFFIX}"
        }

    if phrase_id:
        for f in frasi:
            if str(f["id"]) == str(phrase_id):
                return f

    return random.choice(frasi)


# ─────────────────────────────────────────────────────────────────────────────
# 2. RISOLUZIONE FILE VIDEO E MUSICALI DA DRIVE O LOCALE
# ─────────────────────────────────────────────────────────────────────────────

def risolvi_media_drive(risorsa_o_id, estensione=".mp4", cartella_fallback=None):
    if not risorsa_o_id:
        if cartella_fallback and os.path.exists(cartella_fallback):
            files = [os.path.join(cartella_fallback, f) for f in os.listdir(cartella_fallback) if f.endswith(estensione)]
            if files:
                return random.choice(files)
        return None

    if os.path.exists(risorsa_o_id):
        return os.path.abspath(risorsa_o_id)

    if cartella_fallback:
        candidato = os.path.join(cartella_fallback, risorsa_o_id)
        if os.path.exists(candidato):
            return candidato

    # Download da Google Drive
    drive_id = risorsa_o_id
    if "drive.google.com" in risorsa_o_id:
        m = re.search(r'(?:id=|\/d\/|folders\/)([a-zA-Z0-9_-]{25,})', risorsa_o_id)
        if m:
            drive_id = m.group(1)

    out_path = os.path.join(TEMP_DIR, f"drive_storia_{drive_id[:8]}{estensione}")
    print(f"📥 Download risorsa Google Drive (ID: {drive_id})...")
    
    url = f"https://drive.google.com/uc?export=download&id={drive_id}"
    session = requests.Session()
    r = session.get(url, stream=True, verify=False, timeout=30)
    for k, v in r.cookies.items():
        if k.startswith("download_warning"):
            url += f"&confirm={v}"
            r = session.get(url, stream=True, verify=False, timeout=30)
            break

    if r.status_code == 200:
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        print(f"✅ File Drive salvato: {out_path} ({os.path.getsize(out_path)} bytes)")
        return out_path
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 3. GENERAZIONE OVERLAY GRAFICO STORIA (LOGO IN ALTO + BOX PRESTIGIO IN BASSO)
# ─────────────────────────────────────────────────────────────────────────────

def get_font(font_name, size, fallback_bold=False):
    p = os.path.join(FONTS_DIR, font_name)
    if os.path.exists(p):
        try: return ImageFont.truetype(p, size)
        except Exception: pass
    win_f = ["georgiab.ttf" if fallback_bold else "georgia.ttf", "arialbd.ttf", "timesbd.ttf"]
    for wf in win_f:
        wp = os.path.join(r"C:\Windows\Fonts", wf)
        if os.path.exists(wp):
            try: return ImageFont.truetype(wp, size)
            except Exception: pass
    return ImageFont.load_default()


def disegna_testo_centrato(draw, testo, font, cy, cx, colore=(255, 255, 255, 255)):
    bbox = draw.textbbox((0, 0), testo, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((cx - w // 2, cy), testo, font=font, fill=colore)
    return cy + h


def genera_overlay_storia_drive(frase_item, output_path):
    """
    Costruisce gli overlay grafici 9:16 (1080x1920) per Storie:
    - In Alto: Logo Immobiliare Giancani protetto su backdrop semi-trasparente (salvato come _logo.png)
    - In Basso: Box luxury scuro (60% opacità) con cornice oro, categoria, titolo elegante,
                frase di stimolo/curiosità e chiusura — Immobiliare Giancani (salvato come _card.png)
    Ritorna: tupla (path_logo, path_card) per consentire l'animazione indipendente della slide.
    """
    W, H = 1080, 1920
    cx = W // 2

    # ── 1. LOGO IN ALTO (Y: 120 - 240) ──
    overlay_logo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            target_w = 520
            aspect = logo.size[1] / logo.size[0]
            target_h = int(target_w * aspect)
            logo_resized = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # Placca protettiva scura semi-trasparente con bordo oro sottile
            pad_x, pad_y = 35, 16
            bg_w = target_w + (pad_x * 2)
            bg_h = target_h + (pad_y * 2)
            logo_bg = Image.new("RGBA", (bg_w, bg_h), (0, 0, 0, 0))
            d_lbg = ImageDraw.Draw(logo_bg)
            d_lbg.rounded_rectangle([0, 0, bg_w, bg_h], radius=20, fill=(8, 10, 16, 150), outline=(212, 175, 55, 180), width=2)

            lx = (W - target_w) // 2
            ly = 130
            overlay_logo.paste(logo_bg, (lx - pad_x, ly - pad_y), logo_bg)
            overlay_logo.paste(logo_resized, (lx, ly), logo_resized)
        except Exception as eLogo:
            print(f"⚠️ Errore rendering logo: {eLogo}")

    logo_out_path = output_path.replace(".png", "_logo.png")
    overlay_logo.save(logo_out_path, "PNG")

    # ── 2. BOX SCURO PRESTIGIO & CURIOSITÀ IN BASSO (Y: 1240 - 1760) ──
    overlay_card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    card_w = 940
    card_h = 510
    card_x = (W - card_w) // 2
    card_y = 1240

    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    d_card = ImageDraw.Draw(card)
    # Nero 60% (153/255) con bordo oro caldo
    d_card.rounded_rectangle(
        [0, 0, card_w, card_h],
        radius=30,
        fill=(10, 12, 18, 155),
        outline=(212, 175, 55, 210),
        width=3
    )
    overlay_card.paste(card, (card_x, card_y), card)

    draw = ImageDraw.Draw(overlay_card)

    font_badge = get_font("Cinzel-Bold.ttf", 23, fallback_bold=True)
    font_titolo = get_font("PlayfairDisplay-Bold.ttf", 36, fallback_bold=True)
    font_frase = get_font("Lora-Bold.ttf", 29, fallback_bold=True)
    font_brand = get_font("Cinzel-Bold.ttf", 24, fallback_bold=True)

    # Categoria badge
    cat = frase_item.get("categoria", "PRESTIGIO & VALORE").upper()
    curr_y = card_y + 38
    curr_y = disegna_testo_centrato(draw, f"★  {cat}  ★", font_badge, curr_y, cx, colore=(212, 175, 55, 255)) + 12
    draw.line([(cx - 90, curr_y), (cx + 90, curr_y)], fill=(212, 175, 55, 180), width=2)
    curr_y += 20

    # Titolo hook
    titolo = frase_item.get("titolo", "L'Arte dell'Abitare")
    curr_y = disegna_testo_centrato(draw, titolo, font_titolo, curr_y, cx, colore=(255, 255, 255, 255)) + 18

    # Frase principale estratta dalla Colonna F
    testo_f = frase_item.get("colonna_f", "")
    # Pulisci eventuale suffisso per visualizzazione nella card grafica
    testo_grafica = re.sub(r'\s*—\s*Immobiliare Giancani\s*$', '', testo_f, flags=re.IGNORECASE).strip()
    # Normalizza metri quadri per esteso
    testo_grafica = re.sub(r'\b(mq|mq\.|m\^2|m²|MQ)\b', 'metri quadri', testo_grafica)

    righe_frase = textwrap.wrap(testo_grafica, width=44)
    for r in righe_frase[:4]:
        curr_y = disegna_testo_centrato(draw, r, font_frase, curr_y, cx, colore=(245, 245, 245, 255)) + 12

    # Footer Branding obbligatorio
    curr_y = card_y + card_h - 60
    draw.line([(cx - 110, curr_y - 12), (cx + 110, curr_y - 12)], fill=(212, 175, 55, 160), width=1)
    disegna_testo_centrato(draw, "— IMMOBILIARE GIANCANI —", font_brand, curr_y, cx, colore=(212, 175, 55, 255))

    card_out_path = output_path.replace(".png", "_card.png")
    overlay_card.save(card_out_path, "PNG")

    # Salva anche immagine combinata per retrocompatibilità
    combined = Image.alpha_composite(overlay_logo, overlay_card)
    combined.save(output_path, "PNG")

    print(f"🎨 Overlay Storia generati con successo:")
    print(f"   • Logo: {logo_out_path}")
    print(f"   • Card Animata: {card_out_path}")
    return logo_out_path, card_out_path


# ─────────────────────────────────────────────────────────────────────────────
# 4. MONTAGGIO VIDEO STORIA (1080x1920 @ 30fps)
# ─────────────────────────────────────────────────────────────────────────────

def ottieni_durata_video(video_path):
    cmd = [FFMPEG_EXE, "-i", video_path]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, errors="ignore")
    dur = 15.0
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            try:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
            except Exception:
                pass
    return max(4.0, dur)


def monta_video_storia(video_input, overlay_input, music_input, output_mp4):
    durata = ottieni_durata_video(video_input)
    print(f"🎬 Montaggio Storia Video (Durata: {durata:.2f}s, Formato 9:16)...")

    if isinstance(overlay_input, (tuple, list)) and len(overlay_input) >= 2:
        logo_png, card_png = overlay_input[0], overlay_input[1]
        card_slide_expr = "x=0:y='if(lte(t, 0.85), 550 - 550*sin(t*3.1415926/(2*0.85)), 0)'"
        filtri = [
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[vbase];"
            f"[vbase][1:v]overlay=0:0[vwithlogo];"
            f"[vwithlogo][2:v]overlay={card_slide_expr}[vout]"
        ]
        cmd = [
            FFMPEG_EXE, "-y",
            "-i", video_input,
            "-i", logo_png,
            "-i", card_png
        ]
        music_input_idx = 3
    else:
        overlay_png = overlay_input[0] if isinstance(overlay_input, (tuple, list)) else overlay_input
        filtri = [
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[vbase];"
            f"[vbase][1:v]overlay=0:0[vout]"
        ]
        cmd = [
            FFMPEG_EXE, "-y",
            "-i", video_input,
            "-i", overlay_png
        ]
        music_input_idx = 2

    fade_start = max(0, durata - 2.0)
    if music_input and os.path.exists(music_input):
        cmd.extend(["-stream_loop", "-1", "-i", music_input])
        filtri.append(
            f"[{music_input_idx}:a]atrim=0:{durata},afade=t=out:st={fade_start}:d=2.0,volume=0.38[aout]"
        )
        map_a = ["[aout]"]
    else:
        filtri.append(f"aevalsrc=0:d={durata}[aout]")
        map_a = ["[aout]"]

    cmd.extend([
        "-filter_complex", ";".join(filtri),
        "-map", "[vout]",
        "-map", map_a[0],
        "-t", str(durata),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        output_mp4
    ])

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="ignore")
    if proc.returncode != 0 or not os.path.exists(output_mp4):
        raise RuntimeError(f"FFmpeg fallito:\n{proc.stderr[-800:]}")

    print(f"✅ Video Storia completato: {output_mp4} ({os.path.getsize(output_mp4) / (1024*1024):.2f} MB)")
    return output_mp4


# ─────────────────────────────────────────────────────────────────────────────
# 5. INVIO AUTOMATICO EMAIL CON ALLEGATO MP4
# ─────────────────────────────────────────────────────────────────────────────

def invia_email_storia(destinatario, frase_item, video_path):
    titolo = frase_item.get("titolo", "Storia Prestigio")
    testo_colonna_f = frase_item.get("colonna_f", "")
    if BRANDING_SUFFIX not in testo_colonna_f:
        testo_colonna_f = f"{testo_colonna_f.strip()} {BRANDING_SUFFIX}"

    oggetto = f"Storia Pronta + Frase di Prestigio - {titolo}"
    corpo = (
        f"Ciao Antonio,\n\n"
        f"Ecco la nuova Storia video (formato 9:16) generata per i tuoi social!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 TESTO / CAPTION PRONTO DA COPIARE E INCOLLARE (Colonna F):\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{testo_colonna_f}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎬 Video in allegato: {os.path.basename(video_path)} ({os.path.getsize(video_path)/(1024*1024):.2f} MB)\n\n"
        f"— Immobiliare Giancani\n"
    )

    smtp_user = os.environ.get("SMTP_USER") or os.environ.get("EMAIL_USER") or "giancaniimmobiliare@gmail.com"
    smtp_password = os.environ.get("SMTP_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD") or os.environ.get("EMAIL_PASSWORD")
    smtp_host = os.environ.get("SMTP_HOST") or "smtp.gmail.com"
    smtp_port = int(os.environ.get("SMTP_PORT") or 587)

    if smtp_password:
        try:
            print(f"📧 Invio email a {destinatario}...")
            msg = MIMEMultipart()
            msg["From"] = f"Immobiliare Giancani <{smtp_user}>"
            msg["To"] = destinatario
            msg["Subject"] = oggetto
            msg.attach(MIMEText(corpo, "plain", "utf-8"))

            with open(video_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename=\"{os.path.basename(video_path)}\"")
            msg.attach(part)

            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [destinatario], msg.as_string())
            server.quit()
            print(f"✅ Email inviata con successo con allegato {os.path.basename(video_path)}!")
            return True
        except Exception as e:
            print(f"⚠️ Errore invio SMTP: {e}")
            
    print(f"ℹ️ File video pronto localmente in: {video_path}")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# 6. MASTER ORCHESTRATION & CLI
# ─────────────────────────────────────────────────────────────────────────────

def esegui_flusso_storia(video_drive=None, phrase_id=None, music_drive=None, email_dest=DEFAULT_EMAIL, output_path=None, custom_phrase=None):
    print("=" * 75)
    print("🚀 GENERATORE STORIE DA VIDEO SENZA TESTO DRIVE — IMMOBILIARE GIANCANI")
    print("=" * 75)

    # 1. Carica frasi da Colonna F o usa frase personalizzata
    if custom_phrase and custom_phrase.strip():
        text_clean = custom_phrase.strip()
        text_clean = re.sub(r'\b(mq|mq\.|m\^2|m²|MQ)\b', 'metri quadri', text_clean, flags=re.IGNORECASE)
        if not text_clean.endswith(BRANDING_SUFFIX):
            text_clean += f" {BRANDING_SUFFIX}"
        frase_scelta = {
            "id": "CUSTOM",
            "categoria": "Prestigio & Valore",
            "titolo": "Esperienza & Valore",
            "frase_slogan": custom_phrase.strip(),
            "focus": "Personal Branding",
            "colonna_f": text_clean
        }
    else:
        frasi = carica_frasi_prestigio()
        frase_scelta = seleziona_frase(frasi, phrase_id)
    print(f"📖 Frase Selezionata: [{frase_scelta.get('categoria')}] {frase_scelta.get('titolo')}")
    print(f"   Colonna F: {frase_scelta.get('colonna_f')}")

    # 2. Risolvi Video e Musica
    video_file = risolvi_media_drive(video_drive, estensione=".mp4", cartella_fallback=os.path.join(BASE_DIR, "clip_30s_generate"))
    if not video_file or not os.path.exists(video_file):
        raise FileNotFoundError("Nessun video trovato. Specifica --video o carica una clip.")

    musica_file = risolvi_media_drive(music_drive, estensione=".mp3", cartella_fallback=MUSIC_DIR)
    print(f"🎥 Video: {video_file}")
    print(f"🎵 Musica: {musica_file}")

    # 3. Overlay Grafico (Logo + Box Prestigio)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    overlay_path = os.path.join(TEMP_DIR, f"overlay_storia_{ts}.png")
    overlay_res = genera_overlay_storia_drive(frase_scelta, overlay_path)

    # 4. Rendering Video
    if not output_path:
        tit_clean = re.sub(r'[^a-zA-Z0-9_-]', '_', frase_scelta.get('titolo', 'storia').lower())[:25]
        output_path = os.path.join(OUTPUT_DIR, f"storia_{tit_clean}_{ts}.mp4")

    video_finale = monta_video_storia(video_file, overlay_res, musica_file, output_path)

    # 5. Invio Email
    invia_email_storia(email_dest, frase_scelta, video_finale)

    print("=" * 75)
    print("🎯 STORIA COMPLETATA CON SUCCESSO — IMMOBILIARE GIANCANI")
    print("=" * 75)
    return video_finale


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generatore Storie da Video Drive Senza Testo")
    parser.add_argument("--video", type=str, default=None, help="Video Drive ID/URL o locale")
    parser.add_argument("--phrase-id", type=str, default=None, help="ID Frase Prestigio (Colonna F)")
    parser.add_argument("--custom-phrase", type=str, default=None, help="Testo frase personalizzata (Colonna F)")
    parser.add_argument("--music", type=str, default=None, help="Musica Drive ID o locale")
    parser.add_argument("--email", type=str, default=DEFAULT_EMAIL, help="Email destinatario")
    parser.add_argument("--output", type=str, default=None, help="Percorso output MP4")

    args = parser.parse_args()
    esegui_flusso_storia(
        video_drive=args.video,
        phrase_id=args.phrase_id,
        custom_phrase=args.custom_phrase,
        music_drive=args.music,
        email_dest=args.email,
        output_path=args.output
    )
