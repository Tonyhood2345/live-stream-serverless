#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════
🤖 BOT RILANCIO IMMOBILI SOCIAL (GITHUB ACTIONS) — IMMOBILIARE GIANCANI
═══════════════════════════════════════════════════════════════════════
Funzionamento:
1. Controlla se oggi sono già stati pubblicati nuovi immobili o video su WordPress.
2. Se NON ci sono nuove pubblicazioni oggi:
   - Seleziona un immobile in rotazione dall'archivio Google Sheets degli immobili dell'ultimo anno.
   - Preleva rigorosamente il testo ufficiale dalla Colonna F.
   - Garantisce la dicitura 'metri quadri' per esteso e il personal branding '— Immobiliare Giancani'.
   - Genera i link di conferma e rifiuto tramite l'endpoint WordPress.
   - Invia la scheda con foto e pulsanti interattivi ad Antonio su Telegram (1723292483).
3. Antonio decide se rilanciare cliccando 'SÌ' o 'NO' dal suo smartphone.
"""

import sys
import os
import json
import datetime
import urllib.parse
import requests

requests.packages.urllib3.disable_warnings()

# Credenziali e costanti di sistema
TELEGRAM_TOKEN  = os.environ.get("TELEGRAM_TOKEN", "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M")
ANTONIO_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1723292483")
WP_BASE         = os.environ.get("WP_BASE_URL", "https://www.immobiliaregiancani.it")
WP_TOKEN        = os.environ.get("WP_API_TOKEN", "wpmcp_fc2b5449")
WA_CHANNEL_URL  = "https://whatsapp.com/channel/0029VaCGIA1LY6d1frzuDu2N"
SHEET_API_URL   = "https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec?action=get_elenco_immobili"
CACHE_PATH      = os.path.join(os.path.dirname(__file__), "assets", "catalogo_immobili_cache.json")
STATE_PATH      = os.path.join(os.path.dirname(__file__), "data", "last_reposted_index.json")


def check_new_publications_today():
    """Controlla se oggi sono già stati pubblicati nuovi post su WordPress."""
    today_str = datetime.date.today().isoformat()
    try:
        r = requests.get(f"{WP_BASE}/wp-json/wp/v2/posts?per_page=5", verify=False, timeout=15)
        if r.status_code == 200:
            posts = r.json()
            for p in posts:
                # Verifica data pubblicazione
                p_date = p.get("date", "")
                if p_date.startswith(today_str):
                    print(f"ℹ️ Nuova pubblicazione già presente oggi: Post ID {p.get('id')} ({p.get('title', {}).get('rendered', '')})")
                    return True
    except Exception as e:
        print(f"⚠️ Errore controllo post WordPress: {e}")
    return False


def load_immobili_catalog():
    """Carica il catalogo completo degli immobili da Google Sheets o cache."""
    immobili = []
    try:
        r = requests.get(SHEET_API_URL, verify=False, timeout=25)
        if r.status_code == 200:
            data = r.json()
            immobili = data.get("immobili", [])
            print(f"✅ Recuperati {len(immobili)} elementi da Google Sheets!")
    except Exception as e:
        print(f"⚠️ Fallback cache causa errore fetch Sheets: {e}")

    if not immobili and os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                immobili = json.load(f)
            print(f"✅ Recuperati {len(immobili)} immobili dal file cache locale!")
        except Exception as e:
            print(f"❌ Errore lettura cache: {e}")

    # Filtra solo gli immobili commerciali/residenziali reali
    ignora_parole = ["pose avatar", "impostazioni", "pubblicita", "battute", "archivio", "spot", "analytics", "palinsesto", "frasi", "risultati"]
    validi = []
    for imm in immobili:
        nome = imm.get("nome") or imm.get("tabName") or imm.get("titolo") or ""
        if any(w in nome.lower() for w in ignora_parole):
            continue
        foto = imm.get("fotoUrl")
        if not foto or not str(foto).startswith("http"):
            continue
        validi.append(imm)

    return validi


def get_next_property_in_rotation(validi):
    """Gestisce la rotazione progressiva degli immobili dall'archivio annuale."""
    if not validi:
        return None

    last_idx = -1
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
                last_idx = state.get("last_index", -1)
        except Exception:
            last_idx = -1

    next_idx = (last_idx + 1) % len(validi)

    # Salva il nuovo indice
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "last_index": next_idx,
                "updated_at": datetime.datetime.now().isoformat(),
                "property_name": validi[next_idx].get("nome") or validi[next_idx].get("tabName")
            }, f, indent=2)
    except Exception as e:
        print(f"⚠️ Errore salvataggio state index: {e}")

    return validi[next_idx]


def main():
    force_run = "--force" in sys.argv

    print("═══════════════════════════════════════════════════════════════════")
    print("🤖 AVVIO BOT RILANCIO IMMOBILI SOCIAL — IMMOBILIARE GIANCANI")
    print(f"📅 Data/Ora: {datetime.datetime.now().isoformat()}")
    print("═══════════════════════════════════════════════════════════════════")

    # 1. Verifica se oggi c'è già una nuova pubblicazione
    if not force_run:
        has_new = check_new_publications_today()
        if has_new:
            print("✅ Nessun rilancio necessario: una nuova proprietà o video è già stata pubblicata oggi.")
            return

    # 2. Carica archivio
    immobili = load_immobili_catalog()
    if not immobili:
        print("❌ Nessun immobile valido trovato nell'archivio.")
        return

    # 3. Seleziona immobile in rotazione
    sel = get_next_property_in_rotation(immobili)
    if not sel:
        print("❌ Errore selezione immobile.")
        return

    titolo = sel.get("nome") or sel.get("tabName") or sel.get("titolo") or "Immobile di Pregio"
    titolo = titolo.replace("_", " ").strip()

    prezzo = sel.get("prezzo") or "Trattativa Riservata"
    if str(prezzo).isdigit():
        prezzo = f"€ {int(prezzo):,}".replace(",", ".")

    # Dicitura metri quadri per esteso obbligatoria
    mq = str(sel.get("mq") or "120 metri quadri")
    mq = mq.replace("mq.", "metri quadri").replace("mq", "metri quadri").replace("m²", "metri quadri").replace("MQ", "metri quadri")
    if "metri quadri" not in mq:
        mq = f"{mq} metri quadri"

    # Foto pubblica ad alta definizione
    foto_url = sel.get("fotoUrl") or ""
    if "drive.google.com" in foto_url or "googleusercontent.com" in foto_url or not foto_url.startswith("http"):
        foto_pubblica = "https://www.immobiliaregiancani.it/wp-content/uploads/2026/10/Villa-Esclusiva-con-Giardino-e-Vista-Panoramica-1.jpg"
    else:
        foto_pubblica = foto_url

    # Testo rigoroso da Colonna F
    testo_f = sel.get("testoColonnaF") or sel.get("testoF") or ""
    testo_f = testo_f.replace("mq.", "metri quadri").replace("mq", "metri quadri").replace("m²", "metri quadri").replace("MQ", "metri quadri")
    if "immobiliare giancani" not in testo_f.lower():
        testo_f = testo_f.strip() + "\n\n— Immobiliare Giancani"

    print(f"🏠 Immobile selezionato per la proposta: {titolo}")
    print(f"💰 Prezzo: {prezzo} | 📐 {mq}")

    # 4. Registra lo stage su WordPress
    repost_id = f"repost_{int(datetime.datetime.now().timestamp())}"
    stage_payload = {
        "token": WP_TOKEN,
        "id": repost_id,
        "titolo": titolo,
        "citta": sel.get("citta", "Favara"),
        "prezzo": prezzo,
        "superficie": mq,
        "descrizione": testo_f,
        "foto_url": foto_pubblica,
        "tipo": sel.get("tipologia", "Appartamento")
    }

    try:
        r_stage = requests.post(f"{WP_BASE}/wp-json/giancani/v1/stage-repost", json=stage_payload, verify=False, timeout=20)
        if r_stage.status_code != 200:
            print(f"❌ Errore staging WordPress: {r_stage.status_code} - {r_stage.text}")
            return
        stage_res = r_stage.json()
        approve_url = stage_res.get("approve_url")
        reject_url = stage_res.get("reject_url")
    except Exception as e:
        print(f"❌ Eccezione durante staging su WordPress: {e}")
        return

    # 5. Invia la proposta con i pulsanti a Telegram
    tg_caption = f"""🔔 *PROPOSTA RILANCIO PUBBLICITÀ IMMOBILIARE*

Oggi non ci sono state nuove pubblicazioni.
Vuoi rilanciare questa proprietà dall'archivio su tutti i social (Facebook, Instagram, Threads, WhatsApp, Sito)?

🏠 *{titolo}*
💰 *Prezzo:* {prezzo}
📐 *Superficie:* {mq}

📜 *Testo Ufficiale (Colonna F):*
«{testo_f[:260]}...»

📲 *Canale WhatsApp:* {WA_CHANNEL_URL}

👉 *Scegli se approvare o saltare:*"""

    tg_payload = {
        "chat_id": ANTONIO_CHAT_ID,
        "photo": foto_pubblica,
        "caption": tg_caption,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps({
            "inline_keyboard": [
                [
                    {"text": "🚀 SÌ, RILANCIA PUBBLICITÀ", "url": approve_url},
                    {"text": "❌ NO, SALTA OGGI", "url": reject_url}
                ]
            ]
        })
    }

    try:
        r_tg = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto", data=tg_payload, verify=False, timeout=25)
        if r_tg.status_code == 200:
            print("🚀 Proposta di rilancio inviata con successo su Telegram ad Antonio!")
        else:
            print(f"⚠️ Errore invio Telegram: {r_tg.status_code} - {r_tg.text}")
    except Exception as e:
        print(f"❌ Eccezione invio Telegram: {e}")

    print("═══════════════════════════════════════════════════════════════════")
    print("🏁 ESECUZIONE COMPLETATA CON SUCCESSO — IMMOBILIARE GIANCANI")
    print("═══════════════════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
