#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
🤖 BOT INTELLIGENTE ESTRAZIONE CHIAVI LIVE — TIKTOK & INSTAGRAM
═══════════════════════════════════════════════════════════════════════════════
Autore: Immobiliare Giancani
Descrizione:
1. Utilizza Playwright con il profilo persistente del browser (sessioni e cookie salvati).
2. Si collega a Instagram Live Producer e TikTok Live.
3. Se i siti cambiano struttura/selettori, interviene l'Intelligenza Artificiale
   (Groq / Gemini) per individuare visivamente o semanticamente URL RTMP e Stream Key.
4. Invia automaticamente le nuove chiavi alla Web App di DarIA (Google Apps Script)
   così la regia è subito pronta per la trasmissione multistream.
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import json
import time
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# Percorsi e configurazioni
BASE_DIR = Path(__file__).resolve().parent.parent
PROFILE_DIR = Path(os.environ.get("USERPROFILE", "C:/Users/immobiliare Giancani")) / ".antigravity" / "live_keys_bot_profile"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec"

# Pool chiavi Groq ridondanti (lette da ambiente o configurazione sicura)
GROQ_KEYS = [
    os.environ.get("GROQ_API_KEY", ""),
    os.environ.get("GROQ_API_KEY_2", ""),
    os.environ.get("GROQ_API_KEY_3", "")
]
# Rimuovi eventuali stringhe vuote
GROQ_KEYS = [k for k in GROQ_KEYS if k]


def chiama_ai_per_estrazione_chiavi(testo_pagina: str, piattaforma: str) -> dict:
    """
    Fallback IA (Groq): se i selettori HTML sono cambiati, l'LLM analizza
    il testo della pagina per estrarre con certezza l'URL RTMP e la Stream Key.
    """
    print(f"🧠 [IA FALLBACK] Analisi semantica della pagina {piattaforma} con Groq Llama-3.3...")
    prompt = f"""Sei un assistente tecnico esperto di streaming RTMP per Immobiliare Giancani.
Analizza il seguente contenuto estratto dalla pagina di {piattaforma} e individua:
1. "server_url": l'URL RTMP o RTMPS del server di trasmissione (es. rtmps://live-upload.instagram.com:443/rtmp/ o rtmp://live-push.tiktok-cdns.com/live/).
2. "stream_key": la chiave dello stream (stringa alfanumerica univoca per la diretta).

Testo della pagina:
---
{testo_pagina[:6000]}
---

Rispondi ESCLUSIVAMENTE con un oggetto JSON valido (nessun markdown, nessun commento):
{{
  "server_url": "...",
  "stream_key": "..."
}}
"""
    for k in GROQ_KEYS:
        try:
            req_data = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }).encode('utf-8')

            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=req_data,
                headers={
                    "Authorization": f"Bearer {k}",
                    "Content-Type": "application/json",
                    "User-Agent": "Giancani-LiveBot/1.0"
                }
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                res_body = json.loads(resp.read().decode('utf-8'))
                content = res_body["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                if parsed.get("stream_key"):
                    print(f"✅ [IA FALLBACK] Chiave individuata con successo da Groq!")
                    return parsed
        except Exception as e:
            print(f"⚠️ Tentativo Groq fallito ({e}), provo chiave successiva...")
            continue

    return {"server_url": "", "stream_key": ""}


def invia_chiavi_a_daria(tk_key: str = "", ig_key: str = "") -> bool:
    """
    Invia le chiavi catturate direttamente a Google Apps Script per la regia live.
    """
    print(f"📡 Invio chiavi live a DarIA Web App...")
    payload = {
        "action": "salva_chiavi_live",
        "tk_key": tk_key,
        "ig_key": ig_key,
        "fonte": "bot_automatico_locale"
    }

    try:
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            WEBAPP_URL,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode('utf-8'))
            print(f"✅ Risposta DarIA: {json.dumps(res, indent=2)}")
            print("🎉 Chiavi sincronizzate con successo nella regia! — Immobiliare Giancani")
            return True
    except Exception as e:
        print(f"❌ Errore durante l'invio a DarIA: {e}")
        # Prova via GET di fallback
        try:
            params = urllib.parse.urlencode({
                "action": "salva_chiavi_live",
                "tk_key": tk_key,
                "ig_key": ig_key
            })
            with urllib.request.urlopen(f"{WEBAPP_URL}?{params}", timeout=25) as r2:
                print(f"✅ Fallback GET riuscito: {r2.read().decode('utf-8')[:150]}")
                return True
        except Exception as e2:
            print(f"❌ Errore fallback GET: {e2}")
            return False


def estrai_instagram_live(page) -> tuple:
    """
    Accede a Instagram Web, apre il flusso 'Crea' -> 'Video in diretta',
    e recupera l'URL RTMP e la Stream Key per la trasmissione.
    """
    print("\n📸 [INSTAGRAM] Connessione a Instagram...")
    try:
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=45000)
        time.sleep(3)

        # Chiudi eventuali popup "Non ora"
        for txt in ["Non ora", "Not Now", "Rifiuta"]:
            try:
                btn_no = page.locator(f"button:has-text('{txt}')")
                if btn_no.count() > 0:
                    btn_no.first.click(timeout=2000)
            except Exception:
                pass

        # 1. Clicca su 'Crea'
        print("📸 [INSTAGRAM] Apertura menu 'Crea'...")
        crea_btn = page.locator("svg[aria-label*='Crea' i], svg[aria-label*='Create' i], span:has-text('Crea'), a:has-text('Crea')").first
        crea_btn.click()
        print("📸 [INSTAGRAM] Menu Crea aperto, attesa voce diretta...")

        # 2. Clicca su 'Video in diretta'
        live_btn = page.locator("span:has-text('Video in diretta'), a:has-text('Video in diretta'), div:has-text('Video in diretta')").last
        live_btn.wait_for(state="visible", timeout=12000)
        live_btn.click()
        print("📸 [INSTAGRAM] Configurazione diretta aperta...")

        # 3. Imposta titolo se richiesto e clicca 'Avanti'
        try:
            input_titolo = page.locator('input[placeholder*="titolo" i], input[placeholder*="title" i], textarea')
            if input_titolo.count() > 0:
                input_titolo.first.fill("Diretta Immobiliare Giancani — Opportunità Immobiliari Esclusive")
                time.sleep(1)
        except Exception:
            pass

        btn_avanti = page.locator("button:has-text('Avanti'), div[role='button']:has-text('Avanti')").first
        btn_avanti.wait_for(state="visible", timeout=12000)
        btn_avanti.click()
        print("📸 [INSTAGRAM] Generazione coordinate live in corso...")

        # 4. Attesa ed estrazione coordinate RTMP
        time.sleep(5)
        stream_url = ""
        stream_key = ""

        inputs = page.locator("input[type='text'], input[type='password']").all()
        for inp in inputs:
            val = inp.input_value().strip()
            if "rtmp" in val.lower():
                stream_url = val
            elif len(val) > 20 and not val.startswith("http"):
                stream_key = val

        # Fallback se non trovate da input
        if not stream_key:
            print("⚠️ Selettori standard non completi, avvio analisi semantica...")
            testo_completo = page.inner_text("body")
            res_ia = chiama_ai_per_estrazione_chiavi(testo_completo, "Instagram Live Producer")
            stream_url = res_ia.get("server_url", stream_url)
            stream_key = res_ia.get("stream_key", "")

        if stream_key:
            full_dest = stream_key if stream_key.startswith("rtmp") else (stream_url + stream_key)
            print(f"✅ [INSTAGRAM] Chiave RTMP catturata con successo! — Immobiliare Giancani")
            print(f"   URL: {stream_url}")
            print(f"   Key: {stream_key[:15]}... (totale {len(stream_key)} car.)")
            return stream_url, stream_key, full_dest
        else:
            print("❌ [INSTAGRAM] Impossibile recuperare la chiave automaticamente.")
            return "", "", ""

    except Exception as e:
        print(f"❌ [INSTAGRAM] Errore: {e}")
        return "", "", ""



def estrai_tiktok_live(page) -> tuple:
    """
    Accede a TikTok Live Producer / Live Center e recupera la Stream Key.
    """
    print("\n🎵 [TIKTOK] Connessione a TikTok LIVE Producer...")
    try:
        page.goto("https://www.tiktok.com/live/producer", wait_until="networkidle", timeout=35000)
        time.sleep(3)

        if "login" in page.url:
            print("⚠️ TikTok richiede il login! Completa l'accesso nella finestra...")
            page.wait_for_url(lambda u: "live" in u and "login" not in u, timeout=90000)
            print("✅ Login TikTok rilevato!")
            time.sleep(3)

        stream_url = ""
        stream_key = ""

        # Cerca campi RTMP nel DOM
        inputs = page.locator('input[type="text"], input[type="password"]')
        count = inputs.count()
        for i in range(count):
            val = inputs.nth(i).input_value()
            if "rtmp" in val.lower():
                stream_url = val
            elif len(val) > 15 and not val.startswith("http"):
                stream_key = val

        # Fallback IA se i selettori sono cambiati
        if not stream_key:
            print("⚠️ Selettori standard non trovati, avvio fallback IA per TikTok...")
            testo_completo = page.inner_text("body")
            res_ia = chiama_ai_per_estrazione_chiavi(testo_completo, "TikTok LIVE")
            stream_url = res_ia.get("server_url", stream_url)
            stream_key = res_ia.get("stream_key", "")

        if stream_key:
            full_dest = stream_key if stream_key.startswith("rtmp") else (stream_url + stream_key)
            print(f"✅ [TIKTOK] Chiave RTMP catturata: {stream_key[:10]}...")
            return stream_url, stream_key, full_dest
        else:
            print("ℹ️ [TIKTOK] Nessuna chiave trovata (verifica se l'account ha accesso a LIVE Producer).")
            return "", "", ""

    except Exception as e:
        print(f"❌ [TIKTOK] Errore: {e}")
        return "", "", ""


def sincronizza_sessione_su_github(session_file_path: Path):
    """Carica i cookie di sessione su GitHub in modo che il runner cloud li possa utilizzare in automatico."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        # Tenta lettura da file locale o configurazione sicura
        try:
            with open(BASE_DIR / ".token", "r") as tf:
                token = tf.read().strip()
        except Exception:
            token = os.environ.get("GH_TOKEN", "")

    repo = os.environ.get("GITHUB_REPO", "Tonyhood2345/live-stream-serverless")
    if not token or not session_file_path.exists():
        print("ℹ️ Token GitHub non configurato per l'upload automatico. La sessione rimane locale.")
        return
    try:
        import base64
        with open(session_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        url = f"https://api.github.com/repos/{repo}/contents/scripts/session_cookies.json"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Giancani-Bot"
        }
        sha = None
        try:
            req_get = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req_get, timeout=10) as r:
                sha = json.loads(r.read().decode("utf-8")).get("sha")
        except Exception:
            pass

        payload = {
            "message": "🔒 Aggiornamento cookie di sessione per live cloud — Immobiliare Giancani",
            "content": base64.b64encode(content.encode("utf-8")).decode()
        }
        if sha:
            payload["sha"] = sha

        req_put = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={**headers, "Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(req_put, timeout=20) as r2:
            print("🚀 Cookie sincronizzati su GitHub con successo! Da ora il cloud trasmette in autonomia!")
    except Exception as e:
        print(f"Avviso sincronizzazione sessione su GitHub: {e}")


def main():
    parser = argparse.ArgumentParser(description="Bot Estrazione Chiavi Live Social — Immobiliare Giancani")
    parser.add_argument("--login", action="store_true", help="Apre il browser per effettuare il login iniziale su Instagram/TikTok")
    parser.add_argument("--headless", action="store_true", help="Esegue il bot in background (senza mostrare la finestra)")
    parser.add_argument("--solo-ig", action="store_true", help="Estrae solo la chiave Instagram")
    parser.add_argument("--solo-tk", action="store_true", help="Estrae solo la chiave TikTok")
    args = parser.parse_args()

    print("═════════════════════════════════════════════════════════")
    print(" 🚀 AVVIO BOT ESTRAZIONE CHIAVI LIVE MULTISTREAM")
    print(" 🏢 Immobiliare Giancani")
    print(f" 📁 Profilo Sessioni: {PROFILE_DIR}")
    print("═════════════════════════════════════════════════════════")

    storage_path = BASE_DIR / "scripts" / "session_cookies.json"

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright non installato. Esegui: pip install playwright && playwright install chromium")
        sys.exit(1)

    with sync_playwright() as p:
        is_headless = args.headless and not args.login

        # Identificazione canale browser affidabile su Windows
        browser_channel = None
        if sys.platform == "win32":
            chrome_candidates = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
            ]
            edge_candidates = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            if any(os.path.exists(p) for p in chrome_candidates):
                browser_channel = "chrome"
            elif any(os.path.exists(p) for p in edge_candidates):
                browser_channel = "msedge"

        if args.login:
            print("\n🔑 MODALITÀ LOGIN INTERATTIVO — IMMOBILIARE GIANCANI:")
            print(" Sto aprendo la finestra del browser per farti accedere...")

            browser = None
            channels_to_try = [browser_channel, "msedge", None] if browser_channel else ["msedge", None]
            for ch in channels_to_try:
                try:
                    kw = {"headless": False, "args": ["--no-first-run", "--no-default-browser-check"]}
                    if ch:
                        kw["channel"] = ch
                    browser = p.chromium.launch(**kw)
                    print(f"✅ Finestra del browser aperta con successo (Canale: {ch or 'Chromium default'})!")
                    break
                except Exception as e_br:
                    print(f"⚠️ Avviso avvio ({e_br}), provo canale successivo...")
                    browser = None

            if not browser:
                print("❌ Errore: Impossibile avviare il browser. Verifica Edge o Chrome.")
                sys.exit(1)

            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()

            print("\n" + "="*60)
            print("👉 PASSO 1: ACCEDI A INSTAGRAM")
            print("   Effettua il login a Instagram nella finestra aperta.")
            print("="*60)
            try:
                page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=45000)
            except Exception as e_ig:
                print(f"Avviso caricamento Instagram: {e_ig}")
            input("\n👉 Quando hai completato l'accesso a Instagram, premi INVIO qui...\n")

            print("\n" + "="*60)
            print("👉 PASSO 2: ACCEDI A TIKTOK")
            print("   Effettua il login a TikTok nella stessa finestra.")
            print("="*60)
            try:
                page.goto("https://www.tiktok.com/", wait_until="domcontentloaded", timeout=45000)
            except Exception as e_tk:
                print(f"Avviso caricamento TikTok: {e_tk}")
            input("\n👉 Quando hai completato l'accesso a TikTok, premi INVIO qui...\n")

            # Salva ed esporta sessione
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            context.storage_state(path=str(storage_path))
            print(f"\n✅ Cookie di sessione estratti con successo!")
            sincronizza_sessione_su_github(storage_path)
            browser.close()
            print("\n" + "="*60)
            print("🎉 PROCEDURA COMPLETATA CON SUCCESSO! — Immobiliare Giancani")
            print("   Da questo momento il cloud server genera le chiavi da solo!")
            print("="*60)
            return

        browser = None
        for ch in [browser_channel, None]:
            try:
                kw = {
                    "headless": is_headless,
                    "args": [
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--disable-blink-features=AutomationControlled"
                    ]
                }
                if ch:
                    kw["channel"] = ch
                browser = p.chromium.launch(**kw)
                break
            except Exception:
                browser = None

        if not browser:
            browser = p.chromium.launch(headless=is_headless)

        context_kwargs = {"viewport": {"width": 1400, "height": 900}}
        if storage_path.exists():
            print(f"🍪 Caricamento cookie salvati da {storage_path.name}...")
            context_kwargs["storage_state"] = str(storage_path)

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        ig_dest = ""
        tk_dest = ""

        if not args.solo_tk:
            _, _, ig_dest = estrai_instagram_live(page)

        if not args.solo_ig:
            _, _, tk_dest = estrai_tiktok_live(page)

        # Invia subito le chiavi estratte a DarIA
        if ig_dest or tk_dest:
            invia_chiavi_a_daria(tk_key=tk_dest, ig_key=ig_dest)

        # Scrive immediatamente nei file temporanei per FFmpeg sul runner GitHub Actions e locale
        paths_to_try = [Path("/tmp"), Path(os.environ.get("TEMP", "."))]
        for p_dir in paths_to_try:
            try:
                p_dir.mkdir(parents=True, exist_ok=True)
                if tk_dest:
                    (p_dir / "tiktok_rtmp.txt").write_text(tk_dest, encoding="utf-8")
                if ig_dest:
                    (p_dir / "instagram_rtmp.txt").write_text(ig_dest, encoding="utf-8")
                print(f"📄 Endpoint RTMP salvati in {p_dir}")
                break
            except Exception:
                continue

        # Se abbiamo catturato Instagram, attendiamo che FFmpeg si colleghi e clicchiamo 'Trasmetti in diretta'
        if ig_dest and is_headless:
            print("⏳ [INSTAGRAM] In attesa che FFmpeg invii lo stream video per avviare la diretta...")
            for s in range(20):
                time.sleep(3)
                try:
                    btn_live = page.locator("button:has-text('Trasmetti in diretta'), div[role='button']:has-text('Trasmetti in diretta')")
                    if btn_live.count() > 0:
                        btn_live.first.click(timeout=3000)
                        print("🎉 [INSTAGRAM] Pulsante 'Trasmetti in diretta' premuto con successo! Diretta ONLINE!")
                        time.sleep(4)
                        break
                except Exception:
                    pass

        browser.close()

    print("\n═════════════════════════════════════════════════════════")
    print(" 🏁 OPERAZIONE COMPLETATA — Immobiliare Giancani")
    print("═════════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
