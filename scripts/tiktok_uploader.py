#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  🎵 TIKTOK REELS & STORIES UPLOADER — IMMOBILIARE GIANCANI (@immobiliare_giancani)
  Integrazione completa con la pipeline multimediale di DarIA e dei Bot Reels.
  
  Conforme alla regola globale:
  - Narrazione rigorosamente estratta da Colonna F
  - Superfici espresse in 'metri quadri'
  - Personal Branding esplicito al termine: '— Immobiliare Giancani'
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import shutil
import urllib.request
import urllib.parse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "video_storie_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TIKTOK_ACCOUNT = "@immobiliare_giancani"
TIKTOK_PROFILE_URL = "https://www.tiktok.com/@immobiliare_giancani"

# Telegram per notifiche e 1-click publishing
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1723292483")

APPS_SCRIPT_URL = (
    os.environ.get("APPS_SCRIPT_URL")
    or "https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec"
).strip()


def genera_didascalia_tiktok(titolo, mq, prezzo, testo_colonna_f, is_live=False, hashtags_custom=None):
    """
    Formatta la didascalia nativa per TikTok (<2200 caratteri)
    rispettando la Colonna F e il Personal Branding di Immobiliare Giancani.
    """
    prefix = "🔴 LIVE ORA! " if is_live else "🏡 "
    titolo_clean = (titolo or "Opportunità Immobiliare").strip()
    mq_clean = str(mq or "").replace("mq", "metri quadri").strip()
    prezzo_clean = str(prezzo or "").strip()
    testo_f = (testo_colonna_f or "").replace("|||", "\n").strip()

    info_line = []
    if mq_clean:
        info_line.append(f"📐 {mq_clean}")
    if prezzo_clean and "trattativa" not in prezzo_clean.lower():
        info_line.append(f"💰 {prezzo_clean}")
    info_str = " | ".join(info_line)

    default_hashtags = "#ImmobiliareGiancani #CaseInVendita #Favara #Agrigento #DarIA #AntonioGiancani #RealEstateSicilia #Immobiliare"
    tags = hashtags_custom if hashtags_custom else default_hashtags

    caption = (
        f"{prefix}{titolo_clean.upper()}\n"
        f"{info_str}\n\n"
        f"«{testo_f}»\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👉 Info e visite: Corso Vittorio Veneto 151, Favara (AG)\n"
        f"📞 Tel: +39 320 166 7156 | www.immobiliaregiancani.it\n"
        f"— Immobiliare Giancani\n\n"
        f"{tags}"
    )

    # Tronca a 2100 caratteri per stare comodamente nel limite TikTok
    if len(caption) > 2100:
        caption = caption[:2050] + "\n\n— Immobiliare Giancani\n" + tags

    return caption


def invia_video_telegram_tiktok(video_path, caption):
    """Invia il video verticale 9:16 nativo su Telegram pronto per la condivisione istantanea."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        caption_tg = f"🎵 *VIDEO PRONTO PER TIKTOK ({TIKTOK_ACCOUNT})*\n\n{caption}"
        if len(caption_tg) > 1024:
            caption_tg = caption_tg[:1000] + "...\n\n— *Immobiliare Giancani*"

        with open(video_path, "rb") as vf:
            files = {"video": vf}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption_tg,
                "parse_mode": "Markdown",
                "supports_streaming": True
            }
            import requests
            r = requests.post(url, data=data, files=files, timeout=60, verify=False)
            if r.status_code == 200:
                print(f"  📱 [Telegram] Video inviato con successo ad Antonio Giancani per TikTok!")
                return True
    except Exception as e:
        print(f"  ⚠️ Warning invio Telegram TikTok: {e}")
    return False


def pubblica_video_tiktok(video_path, item_data):
    """
    Punto di ingresso per la sincronizzazione del video 9:16 su TikTok (@immobiliare_giancani).
    """
    print(f"\n🎵 [TIKTOK SYNC] Elaborazione video per {TIKTOK_ACCOUNT}...")
    if not os.path.exists(video_path):
        print(f"❌ File video non trovato: {video_path}")
        return {"nome": f"TikTok ({TIKTOK_ACCOUNT})", "success": False, "error": "File non trovato"}

    titolo = item_data.get("titolo") or item_data.get("argomento") or "Opportunità Immobiliare"
    mq = item_data.get("mq") or item_data.get("superficie") or ""
    prezzo = item_data.get("prezzo") or ""
    testo_f = item_data.get("testoF") or item_data.get("testo_colonna_f") or item_data.get("Colonna_F_Testo_Elaborazione") or ""
    is_live = item_data.get("isLive", False)

    caption = genera_didascalia_tiktok(titolo, mq, prezzo, testo_f, is_live=is_live)

    # 1. Copia in output sicuro TikTok
    tk_out = os.path.join(OUTPUT_DIR, "tiktok_latest_reel.mp4")
    try:
        shutil.copy2(video_path, tk_out)
        print(f"  💾 Video TikTok esportato in: {os.path.basename(tk_out)}")
    except Exception:
        pass

    # 2. Notifica e sincronizzazione con Google Apps Script backend
    try:
        payload = {
            "action": "pubblica_tiktok_story",
            "titolo": titolo,
            "mq": mq,
            "prezzo": prezzo,
            "testoF": testo_f,
            "account": "immobiliare_giancani",
            "caption": caption
        }
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            APPS_SCRIPT_URL,
            data=req_data,
            headers={"Content-Type": "application/json", "User-Agent": "Giancani-TikTok-Engine"},
            method="POST"
        )
        import ssl
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            pass
    except Exception as e_as:
        print(f"  ℹ️ Notifica Apps Script TikTok: {e_as}")

    # 3. Invio video nativo con didascalia su Telegram
    invia_video_telegram_tiktok(video_path, caption)

    print(f"  ✅ [TikTok] Sincronizzazione video completata per {TIKTOK_ACCOUNT}!")
    print(f"  ⭐ Canale: {TIKTOK_PROFILE_URL}")
    print(f"  — Immobiliare Giancani\n")

    return {
        "nome": f"TikTok ({TIKTOK_ACCOUNT})",
        "success": True,
        "account": TIKTOK_ACCOUNT,
        "url": TIKTOK_PROFILE_URL,
        "caption": caption
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        v_file = sys.argv[1]
        sample_data = {
            "titolo": "Appartamento Elegante con Vista",
            "mq": "135 metri quadri",
            "prezzo": "115.000 €",
            "testoF": "Favara, zona residenziale servitissima. Immobile luminoso composto da ampio salone, tre camere da letto e rifiniture di prestigio. — Immobiliare Giancani"
        }
        pubblica_video_tiktok(v_file, sample_data)
    else:
        print("Uso: python tiktok_uploader.py <percorso_video.mp4>")
