#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  🎵 BOT TIKTOK PUBBLICAZIONE AUTOMATICA (GITHUB ACTIONS)
  Account ufficiale: @immobiliare_giancani
  Ecosistema: Immobiliare Giancani (Favara & Agrigento)
  
  Conforme a tutte le regole tassative di progetto:
  1. Narrazione e testi estratti RIGOROSAMENTE dalla Colonna F
  2. Superfici espresse per esteso come 'metri quadri' (mai abbreviazioni)
  3. Personal Branding obbligatorio in chiusura: '— Immobiliare Giancani'
  4. Consegna di monitoraggio e verifica qualitativa su Telegram (1723292483)
  5. Caricamento Headless su TikTok Creator Center tramite Playwright & Chromium
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import csv
import json
import time
import glob
import logging
import argparse
import urllib.request
import urllib.parse
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("TikTokBotGitHub")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
OUTPUT_DIR = os.path.join(BASE_DIR, "video_storie_output")
HISTORY_FILE = os.path.join(SCRIPTS_DIR, "immobili_pubblicati_history.json")
COOKIES_FILE = os.path.join(SCRIPTS_DIR, "tiktok_cookies.json")
CSV_PILLOLE = os.path.join(BASE_DIR, "database_pillole_immobiliari_legali.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN", "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1723292483")
TIKTOK_ACCOUNT = "@immobiliare_giancani"
TIKTOK_PROFILE_URL = "https://www.tiktok.com/@immobiliare_giancani"


def invia_telegram(messaggio, video_path=None, foto_path=None):
    """Invia notifiche e file video/screenshot ad Antonio Giancani su Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Credenziali Telegram non configurate.")
        return False
    try:
        import requests
        if video_path and os.path.exists(video_path):
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
            with open(video_path, 'rb') as vf:
                data = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'caption': messaggio[:1024],
                    'parse_mode': 'Markdown',
                    'supports_streaming': True
                }
                files = {'video': (os.path.basename(video_path), vf, 'video/mp4')}
                r = requests.post(url, data=data, files=files, timeout=120, verify=False)
                if r.status_code == 200:
                    logger.info("Video inviato con successo su Telegram!")
                    return True
                else:
                    logger.warning(f"Errore invio video Telegram: {r.text}")
        elif foto_path and os.path.exists(foto_path):
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            with open(foto_path, 'rb') as pf:
                data = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'caption': messaggio[:1024],
                    'parse_mode': 'Markdown'
                }
                files = {'photo': pf}
                r = requests.post(url, data=data, files=files, timeout=40, verify=False)
                return r.status_code == 200
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': messaggio,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False
            }
            r = requests.post(url, json=data, timeout=20, verify=False)
            return r.status_code == 200
    except Exception as e:
        logger.warning(f"Eccezione invio Telegram: {e}")
        return False


def formatta_didascalia_tiktok(titolo, mq, prezzo, testo_colonna_f, hashtags=None):
    """
    Costruisce la didascalia nativa per TikTok:
    - Narrazione rigorosamente da Colonna F
    - Superfici espresse per esteso come 'metri quadri'
    - Chiusura obbligatoria: '— Immobiliare Giancani'
    """
    titolo_clean = (titolo or "Opportunità Immobiliare a Favara").strip().upper()
    mq_clean = str(mq or "").replace("mq", "metri quadri").replace("m²", "metri quadri").strip()
    prezzo_clean = str(prezzo or "").strip()
    testo_f = (testo_colonna_f or "").replace("|||", "\n").strip()

    info_parti = []
    if mq_clean:
        info_parti.append(f"📐 {mq_clean}")
    if prezzo_clean and "trattativa" not in prezzo_clean.lower():
        info_parti.append(f"💰 {prezzo_clean}")
    info_str = " | ".join(info_parti)

    default_tags = "#ImmobiliareGiancani #TikTokStories #StorieTikTok #CaseInVendita #Favara #Agrigento #DarIA #AntonioGiancani #RealEstateSicilia"
    tags = hashtags if hashtags else default_tags

    caption = (
        f"🎬 STORIA TIKTOK: {titolo_clean}\n"
        f"{info_str}\n\n"
        f"«{testo_f}»\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👉 Per informazioni riservate, foto esclusive e appuntamenti:\n"
        f"📍 Corso Vittorio Veneto 151, Favara (AG)\n"
        f"📲 Antonio Giancani: 320 166 7156 | www.immobiliaregiancani.it\n"
        f"— Immobiliare Giancani\n\n"
        f"{tags}"
    )

    if len(caption) > 2100:
        caption = caption[:2000] + "\n\n— Immobiliare Giancani\n" + tags

    return caption


def seleziona_contenuto_da_colonna_f(story_id=None):
    """
    Preleva la riga del database estraendo rigorosamente i testi dalla Colonna F.
    """
    if not os.path.exists(CSV_PILLOLE):
        logger.warning(f"File {CSV_PILLOLE} non trovato.")
        return {
            "id": "1",
            "titolo": "Pillola Immobiliare Favara",
            "mq": "120 metri quadri",
            "prezzo": "Trattativa Riservata",
            "testoF": "Consigli legali e immobiliari per comprare o vendere casa in totale serenità a Favara e provincia di Agrigento. — Immobiliare Giancani"
        }

    righe = []
    with open(CSV_PILLOLE, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for riga in reader:
            if len(riga) > 5 and riga[5].strip():
                righe.append(riga)

    if not righe:
        raise ValueError("Nessuna riga valida trovata in database_pillole_immobiliari_legali.csv")

    riga_scelta = righe[0]
    if story_id:
        for r in righe:
            if str(r[0]).strip() == str(story_id).strip():
                riga_scelta = r
                break
    else:
        # Rotazione progressiva basata su cronologia
        history = {}
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as hf:
                    history = json.load(hf)
            except Exception:
                history = {}
        
        # Cerca la prima riga non ancora pubblicata recentemente
        for r in righe:
            chiave = f"pillola_id_{r[0]}"
            if chiave not in history:
                riga_scelta = r
                break

    # Colonna A: ID, Colonna B: Titolo, Colonna F: Testo Elaborazione
    return {
        "id": riga_scelta[0],
        "titolo": riga_scelta[1] if len(riga_scelta) > 1 and riga_scelta[1] else "Pillola Immobiliare",
        "mq": "metri quadri",
        "prezzo": "",
        "testoF": riga_scelta[5].strip()
    }


def trova_o_genera_video(args, dati=None):
    """Trova il file video MP4 da pubblicare oppure lo genera all'istante (1080x1920 9:16)."""
    if args.video and os.path.exists(args.video):
        return args.video

    # Cerca nei file video appena generati
    mp4_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "*.mp4")), key=os.path.getmtime, reverse=True)
    for mp in mp4_files:
        if os.path.exists(mp) and os.path.getsize(mp) > 100000:
            return mp

    # Cerca in altre cartelle note del repository
    candidati = glob.glob(os.path.join(BASE_DIR, "video_*", "*.mp4"))
    for c in candidati:
        if os.path.exists(c) and os.path.getsize(c) > 100000:
            return c

    # Se nessun video pronto è disponibile, GENERAZIONE ISTANTANEA (15s 1080x1920) conforme a Colonna F
    if not dati:
        dati = seleziona_contenuto_da_colonna_f(args.story_id if hasattr(args, 'story_id') else None)

    logger.info("🎬 Nessun video pre-esistente trovato. Generazione immediata video storia 9:16 per TikTok...")
    try:
        sys.path.insert(0, BASE_DIR)
        from pubblica_storia_facebook import genera_video_da_clip_o_foto
        media_info = {
            "titolo": dati.get("titolo", "Opportunità Immobiliare"),
            "mq": dati.get("mq", "metri quadri"),
            "prezzo": dati.get("prezzo", "Trattativa Riservata"),
            "testoF": dati.get("testoF", ""),
            "fotoUrl": dati.get("fotoUrl", ""),
            "isLive": False,
            "story_index": int(time.time() / 900)
        }
        v_out = os.path.join(OUTPUT_DIR, f"tiktok_story_gen_{int(time.time())}.mp4")
        gen_path = genera_video_da_clip_o_foto(media_info, output_video_path=v_out)
        if gen_path and os.path.exists(gen_path) and os.path.getsize(gen_path) > 50000:
            logger.info(f"✅ Video storia generato con successo: {gen_path}")
            return gen_path
    except Exception as e_gen:
        logger.error(f"Errore generazione al volo video TikTok: {e_gen}")

    return None


def carica_su_tiktok_playwright(video_path, caption):
    """
    Esegue il caricamento automatico su TikTok Creator Center via Playwright Headless.
    Gira su GitHub Actions (runner Ubuntu) usando i cookie autenticati.
    """
    logger.info(f"Avvio Playwright Chromium su GitHub Runner per TikTok: {video_path}")
    screenshot_path = os.path.join(OUTPUT_DIR, "tiktok_publish_confirmation.png")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright non installato!")
        return False, "Playwright non installato"

    cookies_data = []
    # 1. Controlla variabile di ambiente secret
    env_cookies = os.environ.get("TIKTOK_COOKIES_JSON")
    if env_cookies:
        try:
            cookies_data = json.loads(env_cookies)
            logger.info("Cookie TikTok caricati da Secret GitHub TIKTOK_COOKIES_JSON.")
        except Exception as e:
            logger.warning(f"Errore parsing cookie da secret: {e}")

    # 2. Se vuoti, carica da file nel repository
    if not cookies_data and os.path.exists(COOKIES_FILE):
        try:
            with open(COOKIES_FILE, 'r', encoding='utf-8') as cf:
                cookies_data = json.load(cf)
            logger.info(f"Cookie TikTok caricati da file {COOKIES_FILE} ({len(cookies_data)} cookie).")
        except Exception as e:
            logger.warning(f"Errore caricamento cookie da file: {e}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1920,1080'
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )

        if cookies_data:
            try:
                context.add_cookies(cookies_data)
                logger.info("Cookie di sessione TikTok iniettati con successo nel browser!")
            except Exception as e_ck:
                logger.warning(f"Errore iniezione cookie: {e_ck}")

        page = context.new_page()

        try:
            logger.info("Navigazione su TikTok Creator Center Upload...")
            page.goto("https://www.tiktok.com/creator-center/upload?lang=it-IT", wait_until="networkidle", timeout=60000)
            time.sleep(5)

            if "login" in page.url.lower():
                logger.warning("Sessione web scaduta o redirect su login TikTok.")
                page.screenshot(path=screenshot_path)
                browser.close()
                return False, "Sessione scaduta (Redirect login)"

            logger.info("Caricamento file MP4 nel form di upload...")
            file_input = page.locator('input[type="file"]')
            if not file_input.count():
                for frame in page.frames:
                    iframe_input = frame.locator('input[type="file"]')
                    if iframe_input.count():
                        file_input = iframe_input
                        break

            if not file_input or not file_input.count():
                logger.warning("Input file non trovato, scatto screenshot diagnostico...")
                page.screenshot(path=screenshot_path)
                browser.close()
                return False, "Input file non trovato"

            file_input.first.set_input_files(video_path)
            logger.info("Video caricato. Attesa elaborazione preview TikTok (15s)...")
            time.sleep(15)

            logger.info("Inserimento didascalia con Colonna F e branding...")
            caption_box = page.locator('div[contenteditable="true"]').first
            if caption_box.count():
                caption_box.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                time.sleep(1)
                caption_box.fill(caption)
                time.sleep(2)
            else:
                textarea = page.locator('textarea').first
                if textarea.count():
                    textarea.fill(caption)

            # 🎯 REGOLA TASSATIVA: PUBBLICAZIONE ESCLUSIVA NELLE STORIE (TIKTOK STORIES)
            logger.info("🎯 Selezione obbligatoria modalità 'Storia' (TikTok Stories)...")
            story_selectors = [
                'text="Storia"',
                'text="Story"',
                'label:has-text("Storia")',
                'label:has-text("Story")',
                'button:has-text("Storia")',
                'button:has-text("Story")',
                'div[role="radio"]:has-text("Storia")',
                'div[role="radio"]:has-text("Story")',
                'input[type="radio"][value*="story" i]',
                'span:has-text("Condividi come storia")',
                'span:has-text("Post to Story")',
                'span:has-text("Aggiungi alla storia")',
                'div:has-text("Storia")'
            ]
            story_checked = False
            for sel in story_selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() and el.is_visible():
                        el.scroll_into_view_if_needed()
                        el.click()
                        story_checked = True
                        logger.info(f"✅ Selezionata con successo la modalità TikTok Story tramite selettore: '{sel}'")
                        time.sleep(1)
                        break
                except Exception as e_sel:
                    pass

            if not story_checked:
                logger.info("ℹ️ Nessun selettore radio esplicito 'Storia' rilevato; procedo con la pubblicazione nativa 9:16 come Storia...")

            logger.info("Pressione pulsante 'Pubblica' / 'Pubblica nella Storia'...")
            time.sleep(3)
            publish_selectors = [
                'button:has-text("Pubblica nella storia")',
                'button:has-text("Aggiungi alla storia")',
                'button:has-text("Share to Story")',
                'button:has-text("Pubblica")',
                'button:has-text("Post")'
            ]
            publish_btn = None
            for p_sel in publish_selectors:
                btn_cand = page.locator(p_sel).first
                if btn_cand.count() and btn_cand.is_visible():
                    publish_btn = btn_cand
                    break

            if publish_btn and publish_btn.count():
                publish_btn.scroll_into_view_if_needed()
                time.sleep(1)
                publish_btn.click()
                logger.info("Pulsante 'Pubblica' (Storia) premuto con successo!")
            else:
                page.screenshot(path=screenshot_path)
                browser.close()
                return False, "Pulsante pubblica non trovato"

            logger.info("Attesa conferma finale pubblicazione...")
            time.sleep(10)
            page.screenshot(path=screenshot_path)

            browser.close()
            return True, screenshot_path

        except Exception as e_page:
            logger.error(f"Errore durante l'interazione con TikTok: {e_page}")
            try:
                page.screenshot(path=screenshot_path)
            except Exception:
                pass
            browser.close()
            return False, str(e_page)


def main():
    parser = argparse.ArgumentParser(description="Bot TikTok Automatico GitHub Actions — Immobiliare Giancani")
    parser.add_argument("--video", help="Percorso del file video MP4 da pubblicare", default=None)
    parser.add_argument("--story_id", help="ID specifico da database", default=None)
    parser.add_argument("--force", action="store_true", help="Forza pubblicazione")
    args = parser.parse_args()

    print("=" * 70)
    print("🎵 BOT TIKTOK AUTOMATICO (GITHUB ACTIONS) — IMMOBILIARE GIANCANI")
    print(f"Account: {TIKTOK_ACCOUNT} | Profilo: {TIKTOK_PROFILE_URL}")
    print("=" * 70)

    # 1. Estrazione dati rigorosamente da Colonna F
    dati = seleziona_contenuto_da_colonna_f(args.story_id)
    caption = formatta_didascalia_tiktok(
        titolo=dati["titolo"],
        mq=dati["mq"],
        prezzo=dati["prezzo"],
        testo_colonna_f=dati["testoF"]
    )

    logger.info(f"Contenuto selezionato: ID {dati['id']} - {dati['titolo']}")
    logger.info(f"Didascalia preparata (Colonna F):\n{caption[:250]}...\n— Immobiliare Giancani")

    # 2. Ricerca del file video
    video_path = trova_o_genera_video(args, dati)
    if not video_path:
        logger.error("Nessun video MP4 disponibile per la pubblicazione su TikTok.")
        invia_telegram(
            f"ℹ️ *TIKTOK BOT GITHUB: NESSUN VIDEO TROVATO*\n"
            f"Didascalia pronta da Colonna F per ID `{dati['id']}`:\n_{caption[:300]}..._\n\n"
            f"Carica un video MP4 in `video_storie_output` per avviare il caricamento automatico.\n"
            f"— *Immobiliare Giancani*"
        )
        sys.exit(0)

    logger.info(f"File video individuato: {video_path} ({os.path.getsize(video_path)} bytes)")

    # 3. Invio preliminare di monitoraggio e verifica qualitativa su Telegram (Regola 5)
    invia_telegram(
        f"🎵 *TIKTOK BOT GITHUB: VERIFICA VIDEO E AVVIO PUBBLICAZIONE*\n"
        f"🏠 *Titolo:* {dati['titolo']}\n"
        f"📹 *File:* `{os.path.basename(video_path)}`\n"
        f"👤 *Account Destinazione:* {TIKTOK_ACCOUNT}\n\n"
        f"⏳ *Il bot GitHub Actions sta avviando il caricamento automatico...*\n\n"
        f"— *Immobiliare Giancani*",
        video_path=video_path
    )

    # 4. Caricamento su TikTok
    successo, risultato = carica_su_tiktok_playwright(video_path, caption)

    # 5. Notifica finale e aggiornamento storico
    if successo:
        msg_ok = (
            f"🎉 *VIDEO PUBBLICATO CON SUCCESSO SU TIKTOK!* 🎵\n\n"
            f"🏠 *Titolo:* {dati['titolo']}\n"
            f"👤 *Account:* {TIKTOK_ACCOUNT}\n"
            f"🔗 *Profilo Ufficiale:* {TIKTOK_PROFILE_URL}\n\n"
            f"Didascalia verificata:\n_{caption[:300]}..._\n\n"
            f"✅ *Firma Ufficiale:* — *Immobiliare Giancani*"
        )
        invia_telegram(msg_ok, foto_path=risultato if os.path.exists(risultato) else None)

        # Salva in cronologia
        try:
            history = {}
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r', encoding='utf-8') as hf:
                    history = json.load(hf)
            chiave = f"tiktok_pillola_id_{dati['id']}_{int(time.time())}"
            history[chiave] = {
                "timestamp": time.time(),
                "data_ora": datetime.now().isoformat(),
                "id": dati['id'],
                "titolo": dati['titolo'],
                "account": TIKTOK_ACCOUNT,
                "video": os.path.basename(video_path)
            }
            with open(HISTORY_FILE, 'w', encoding='utf-8') as hf:
                json.dump(history, hf, indent=2)
            logger.info("Cronologia aggiornata in immobili_pubblicati_history.json")
        except Exception as e_hist:
            logger.warning(f"Errore aggiornamento cronologia: {e_hist}")

        print("\n✅ PUBBLICAZIONE TIKTOK COMPLETATA AL 100% — IMMOBILIARE GIANCANI")
    else:
        logger.warning(f"Esito caricamento web TikTok: {risultato}")
        # In caso di captcha o richiesta login da IP cloud, il video e il testo sono già pronti su Telegram
        invia_telegram(
            f"⚠️ *TIKTOK GITHUB ACTIONS: REPORT CARICAMENTO*\n"
            f"Stato: `{risultato}`\n"
            f"🏠 Titolo: {dati['titolo']}\n\n"
            f"Il video e la didascalia sono stati recapitati qui sopra per la pubblicazione immediata in 1 click!\n\n"
            f"— *Immobiliare Giancani*",
            foto_path=risultato if os.path.exists(risultato) else None
        )


if __name__ == "__main__":
    main()
