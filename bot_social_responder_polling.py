#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═════════════════════════════════════════════════════════════════════════════════
IMMOBILIARE GIANCANI — BOT AUTO-RESPONDER SOCIAL (MESSENGER, FACEBOOK, INSTAGRAM)
═════════════════════════════════════════════════════════════════════════════════
Funzionalità:
1. POLLING CONTINUO MESSENGER:
   - Monitora le conversazioni private di Facebook Messenger (Page ID 234931856561526).
   - Se un utente invia un messaggio e non ha ancora ricevuto risposta, invia
     immediatamente una risposta professionale, cortese e profilata.
   - Fornisce recapiti diretti di Antonio Giancani (320 166 7156) e sede a Favara.

2. POLLING COMMENTI FACEBOOK:
   - Monitora i commenti su tutti i post recenti della Pagina Facebook.
   - Risponde a ciascun commento non ancora evaso (prezzo, disponibilità, info).
   - Invita a proseguire su Messenger privato (m.me/234931856561526) o al telefono.

3. POLLING COMMENTI INSTAGRAM:
   - Monitora i commenti sui media recenti dell'account @giancani_immobiliare.
   - Risponde tempestivamente invitando a contattare l'agenzia.

4. REGISTRO PERSISTENTE ANTI-DUPLICAZIONE:
   - Salva gli ID di messaggi e commenti gestiti in 'risposte_social_inviate.json'.
   - Nessun cliente riceve mai risposte duplicate.

5. NOTIFICHE DI MONITORAGGIO SU TELEGRAM (1723292483):
   - Notifica istantanea ogni volta che un cliente viene servito dal bot.

6. CONFORMITÀ REGOLE MANDATORIE:
   - Ogni testo generato si conclude tassativamente mettendo in massimo risalto:
     '— Immobiliare Giancani'
   - Superfici espresse per esteso come 'metri quadri'.
═════════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import json
import random
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Directory e percorsi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "risposte_social_inviate.json")

# Credenziali Meta Graph API
FB_PAGE_ID = (os.environ.get("FB_PAGE_ID") or "234931856561526").strip()
FB_PAGE_TOKEN = (os.environ.get("FB_PAGE_TOKEN") or "EAAZAH7q8wRZAEBS3ZAfEIpFIcXPJ87gDZAY8QjpGvBSjgC44c22JVeZAiDxMOM85JRMKM2T1hLgekBCkT0z5geNsb3KxAhMr7W7xlOGVKJsdKV9rZCEKLupIy1uNaDkVZAXmFtn0stiB212odWJ2ZCZBtlWkZAzy5wmPfKyZC3g27g6RXs0FK2GiYc5MeqaZCZBuoYjIyreTZAxwOqtfESifVw").strip()
IG_ACCOUNT_ID = os.environ.get("IG_ACCOUNT_ID", "17841400301393511").strip()

# Telegram
TELEGRAM_BOT_TOKEN = "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M"
TELEGRAM_CHAT_ID = "1723292483"

POLL_INTERVAL_SECONDS = 60  # Controllo ogni 60 secondi


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def carica_stato():
    """Carica l'elenco degli ID già evasi"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "messaggi_gestiti": set(data.get("messaggi_gestiti", [])),
                    "commenti_gestiti": set(data.get("commenti_gestiti", []))
                }
        except Exception as e:
            log(f"⚠️ Avviso lettura stato: {e}")
    return {"messaggi_gestiti": set(), "commenti_gestiti": set()}


def salva_stato(stato):
    """Salva lo stato persistente"""
    try:
        data = {
            "messaggi_gestiti": list(stato["messaggi_gestiti"])[-3000:],
            "commenti_gestiti": list(stato["commenti_gestiti"])[-3000:],
            "ultimo_aggiornamento": datetime.now().isoformat()
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"⚠️ Errore salvataggio stato: {e}")


def invia_telegram(notifica_md):
    """Invia notifica di recapito ad Antonio Giancani su Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": notifica_md,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        requests.post(url, json=payload, timeout=10, verify=False)
    except Exception as e:
        log(f"⚠️ Errore Telegram: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 💬 GENERATORE RISPOSTE INTELLIGENTI CON BRANDING OBBLIGATORIO
# ═════════════════════════════════════════════════════════════════════════════

def genera_risposta_commento(nome_utente, testo_commento):
    """Genera una risposta su misura per commenti pubblici (FB/IG)"""
    testo_basso = (testo_commento or "").lower()
    saluto = f"Ciao {nome_utente}! 😊" if nome_utente and "None" not in nome_utente else "Salve! 😊"

    if any(k in testo_basso for k in ["prezzo", "costo", "prix", "quanto", "cifra", "euro", "€"]):
        corpo = (
            f"{saluto} Grazie mille per il tuo interesse verso questa splendida proprietà! 🏡✨\n"
            f"Trattandosi di un immobile esclusivo con finiture curate e di pregio, trattiamo con la massima riservatezza "
            f"per tutelare sia il venditore che il futuro acquirente.\n\n"
            f"💬 Ti invito a scriverci un messaggio privato qui su Messenger 👉 https://m.me/234931856561526 "
            f"per ricevere subito foto dettagliate, la scheda tecnica completa e il valore riservato!\n\n"
            f"📲 Oppure puoi contattare direttamente il titolare Antonio Giancani al 320 166 7156 (anche WhatsApp) "
            f"per fissare un sopralluogo dedicato senza impegno.\n\n"
            f"— Immobiliare Giancani"
        )
    elif any(k in testo_basso for k in ["disponibile", "ancora", "venduto", "trova", "dove"]):
        corpo = (
            f"{saluto} Sì, la soluzione immobiliare è attualmente disponibile e visionabile! 🗝️🏡\n\n"
            f"📍 Ci troviamo a Favara e operiamo su tutta la provincia di Agrigento.\n"
            f"Per concordare una visita sul posto o ricevere la scheda descrittiva, scrivici subito in privato su Messenger "
            f"👉 https://m.me/234931856561526 oppure chiama Antonio Giancani al 320 166 7156.\n\n"
            f"— Immobiliare Giancani"
        )
    else:
        corpo = (
            f"{saluto} Grazie di cuore per aver commentato! Siamo felici del tuo riscontro. 🏡✨\n\n"
            f"Per qualsiasi informazione approfondita, dettagli riservati, planimetrie e appuntamenti dedicati, "
            f"siamo a tua completa disposizione in privato su Messenger 👉 https://m.me/234931856561526 "
            f"o al numero 320 166 7156 (Antonio Giancani).\n\n"
            f"— Immobiliare Giancani"
        )
    return corpo


def genera_risposta_messenger(nome_utente, testo_messaggio):
    """Genera risposta automatica accogliente per Messenger"""
    saluto = f"Gentile {nome_utente}," if nome_utente and "None" not in nome_utente else "Gentile Cliente,"
    return (
        f"{saluto} grazie per aver contattato Immobiliare Giancani! 😊🏡\n\n"
        f"Ho ricevuto il suo messaggio con il massimo interesse. Il titolare Antonio Giancani e la nostra segreteria "
        f"hanno preso in carico la sua richiesta.\n\n"
        f"Per offrirle la massima assistenza personalizzata, inviarle foto in alta definizione, schede riservate "
        f"o concordare una visita gratuita presso l'immobile:\n"
        f"📞 Può contattare direttamente Antonio Giancani al 320 166 7156 (disponibile anche su WhatsApp)\n"
        f"📍 Oppure venirci a trovare in sede a Favara (AG), in Corso Vittorio Veneto 151.\n\n"
        f"Ci indichi pure a quale immobile o zona è interessato, così da fornirle tutti i dettagli in anteprima esclusiva!\n\n"
        f"— Immobiliare Giancani"
    )


# ═════════════════════════════════════════════════════════════════════════════
# 📬 1. GESTORE MESSENGER (CONVERSAZIONI PRIVATE)
# ═════════════════════════════════════════════════════════════════════════════

def elabora_conversazioni_messenger(stato):
    """Controlla le conversazioni di Messenger ed evade messaggi non risposti"""
    log("🔍 [MESSENGER] Controllo messaggi in arrivo...")
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/conversations?fields=id,snippet,updated_time,participants,unread_count&access_token={FB_PAGE_TOKEN}"
    try:
        r = requests.get(url, verify=False, timeout=15)
        if r.status_code != 200:
            log(f"⚠️ Errore fetch conversazioni: {r.status_code} {r.text}")
            return

        convs = r.json().get("data", [])
        for c in convs:
            conv_id = c.get("id")
            # Fetch ultimi messaggi della conversazione
            url_msg = f"https://graph.facebook.com/v19.0/{conv_id}/messages?fields=id,message,from,created_time&limit=5&access_token={FB_PAGE_TOKEN}"
            r_msg = requests.get(url_msg, verify=False, timeout=15)
            if r_msg.status_code != 200:
                continue

            messages = r_msg.json().get("data", [])
            if not messages:
                continue

            ultimo_msg = messages[0]
            msg_id = ultimo_msg.get("id")
            sender = ultimo_msg.get("from", {})
            sender_id = sender.get("id")
            sender_name = sender.get("name") or "Cliente"
            testo = ultimo_msg.get("message") or ""

            # Se l'ultimo messaggio è inviato dalla pagina stessa, non occorre rispondere
            if sender_id == FB_PAGE_ID:
                continue

            # Se già evaso
            if msg_id in stato["messaggi_gestiti"]:
                continue

            # Trova l'ID utente PSID per la risposta
            psid = sender_id
            if not psid:
                for p in c.get("participants", {}).get("data", []):
                    if p.get("id") != FB_PAGE_ID:
                        psid = p.get("id")
                        break

            if not psid:
                continue

            log(f"📩 [NUOVO MESSAGGIO DA RISPONDERE] Da {sender_name} (ID {psid}): '{testo[:60]}...'")

            risposta = genera_risposta_messenger(sender_name, testo)

            # Invia messaggio via Graph API
            send_url = f"https://graph.facebook.com/v19.0/me/messages?access_token={FB_PAGE_TOKEN}"
            send_payload = {
                "recipient": {"id": psid},
                "message": {"text": risposta}
            }
            r_send = requests.post(send_url, json=send_payload, verify=False, timeout=15)

            if r_send.status_code == 200:
                log(f"✅ [MESSENGER RISPOSTA INVIATA] a {sender_name} con successo!")
                stato["messaggi_gestiti"].add(msg_id)
                salva_stato(stato)

                # Notifica su Telegram
                tg_txt = (
                    f"💬 *NUOVO MESSAGGIO MESSENGER RISPOSTO*\n\n"
                    f"👤 *Cliente:* {sender_name}\n"
                    f"❓ *Messaggio cliente:* «{testo}»\n\n"
                    f"🤖 *Risposta automatica inviata:*\n{risposta}"
                )
                invia_telegram(tg_txt)
            else:
                log(f"⚠️ Errore invio Messenger a {sender_name}: {r_send.text}")
                # Segna comunque come gestito per evitare loop su account disattivati o bloccati
                stato["messaggi_gestiti"].add(msg_id)
                salva_stato(stato)

    except Exception as e:
        log(f"⚠️ Errore controllo Messenger: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 💬 2. GESTORE COMMENTI FACEBOOK (BACHECA E POST)
# ═════════════════════════════════════════════════════════════════════════════

def elabora_commenti_facebook(stato):
    """Controlla i post recenti e risponde a tutti i commenti in sospeso"""
    log("🔍 [FB COMMENTS] Controllo commenti sui post recenti...")
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed?fields=id,message,comments{{id,message,from,created_time,comment_count}}&limit=15&access_token={FB_PAGE_TOKEN}"
    try:
        r = requests.get(url, verify=False, timeout=15)
        if r.status_code != 200:
            log(f"⚠️ Errore fetch feed FB: {r.status_code} {r.text}")
            return

        posts = r.json().get("data", [])
        for p in posts:
            cmts = p.get("comments", {}).get("data", [])
            for c in cmts:
                c_id = c.get("id")
                c_from = c.get("from", {})
                from_id = c_from.get("id")
                from_name = c_from.get("name") or "Utente Facebook"
                c_text = c.get("message") or ""

                # Salta commenti scritti dalla pagina stessa
                if from_id == FB_PAGE_ID:
                    continue

                if c_id in stato["commenti_gestiti"]:
                    continue

                # Verifica se abbiamo già risposto direttamente a questo commento
                url_sub = f"https://graph.facebook.com/v19.0/{c_id}/comments?fields=id,from,message&access_token={FB_PAGE_TOKEN}"
                r_sub = requests.get(url_sub, verify=False, timeout=10)
                already_replied = False
                if r_sub.status_code == 200:
                    for sc in r_sub.json().get("data", []):
                        if sc.get("from", {}).get("id") == FB_PAGE_ID or "Immobiliare Giancani" in (sc.get("from", {}).get("name") or ""):
                            already_replied = True
                            break

                if already_replied:
                    stato["commenti_gestiti"].add(c_id)
                    continue

                log(f"💬 [NUOVO COMMENTO FB] Post {p.get('id')} da {from_name}: '{c_text}'")

                risposta = genera_risposta_commento(from_name, c_text)

                # Pubblica risposta
                rep_url = f"https://graph.facebook.com/v19.0/{c_id}/comments"
                r_rep = requests.post(rep_url, data={"message": risposta, "access_token": FB_PAGE_TOKEN}, verify=False, timeout=15)

                if r_rep.status_code == 200:
                    log(f"✅ [FB RISPOSTA COMMENTO INVIATA] a {from_name}!")
                    stato["commenti_gestiti"].add(c_id)
                    salva_stato(stato)

                    # Notifica Telegram
                    tg_txt = (
                        f"📝 *NUOVO COMMENTO FACEBOOK RISPOSTO*\n\n"
                        f"👤 *Autore:* {from_name}\n"
                        f"❓ *Commento:* «{c_text}»\n\n"
                        f"🤖 *Risposta pubblicata:*\n{risposta}"
                    )
                    invia_telegram(tg_txt)
                else:
                    log(f"⚠️ Errore risposta commento FB: {r_rep.text}")

    except Exception as e:
        log(f"⚠️ Errore commenti FB: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 📸 3. GESTORE COMMENTI INSTAGRAM
# ═════════════════════════════════════════════════════════════════════════════

def elabora_commenti_instagram(stato):
    """Controlla i post Instagram e risponde ai commenti"""
    log("🔍 [IG COMMENTS] Controllo commenti su Instagram...")
    url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media?fields=id,caption,comments{{id,text,from,timestamp,replies{{id,from,text}}}}&limit=15&access_token={FB_PAGE_TOKEN}"
    try:
        r = requests.get(url, verify=False, timeout=15)
        if r.status_code != 200:
            log(f"⚠️ Errore fetch IG media: {r.status_code} {r.text}")
            return

        media_list = r.json().get("data", [])
        for m in media_list:
            cmts = m.get("comments", {}).get("data", [])
            for c in cmts:
                c_id = c.get("id")
                c_from = c.get("from", {})
                from_user = c_from.get("username") or "Utente Instagram"
                from_id = c_from.get("id")
                c_text = c.get("text") or ""

                if from_id == IG_ACCOUNT_ID:
                    continue

                if c_id in stato["commenti_gestiti"]:
                    continue

                # Controlla se abbiamo già risposto
                replies = c.get("replies", {}).get("data", [])
                already_replied = any(rep.get("from", {}).get("id") == IG_ACCOUNT_ID for rep in replies)
                if already_replied:
                    stato["commenti_gestiti"].add(c_id)
                    continue

                log(f"📸 [NUOVO COMMENTO IG] Media {m.get('id')} da @{from_user}: '{c_text}'")

                risposta = genera_risposta_commento(from_user, c_text)

                # Rispondi al commento IG
                rep_url = f"https://graph.facebook.com/v19.0/{c_id}/replies"
                r_rep = requests.post(rep_url, data={"message": risposta, "access_token": FB_PAGE_TOKEN}, verify=False, timeout=15)

                if r_rep.status_code == 200:
                    log(f"✅ [IG RISPOSTA COMMENTO INVIATA] a @{from_user}!")
                    stato["commenti_gestiti"].add(c_id)
                    salva_stato(stato)

                    # Notifica Telegram
                    tg_txt = (
                        f"📸 *NUOVO COMMENTO INSTAGRAM RISPOSTO*\n\n"
                        f"👤 *Autore:* @{from_user}\n"
                        f"❓ *Commento:* «{c_text}»\n\n"
                        f"🤖 *Risposta pubblicata:*\n{risposta}"
                    )
                    invia_telegram(tg_txt)
                else:
                    log(f"⚠️ Errore risposta commento IG: {r_rep.text}")
                    stato["commenti_gestiti"].add(c_id)
                    salva_stato(stato)

    except Exception as e:
        log(f"⚠️ Errore commenti IG: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 🚀 CICLO PRINCIPALE DEMONE
# ═════════════════════════════════════════════════════════════════════════════

def esegui_ciclo_risposte(stato):
    """Esegue un passaggio completo su tutti i canali"""
    elabora_conversazioni_messenger(stato)
    elabora_commenti_facebook(stato)
    elabora_commenti_instagram(stato)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Bot Auto-Responder Social Immobiliare Giancani")
    parser.add_argument("--once", action="store_true", help="Esegue un solo ciclo ed esce")
    parser.add_argument("--interval", type=int, default=POLL_INTERVAL_SECONDS, help="Intervallo polling in secondi")
    parser.add_argument("--cycles", type=int, default=0, help="Numero massimo di cicli da eseguire prima di uscire (0 = infinito)")
    args = parser.parse_args()

    log("══════════════════════════════════════════════════════════════════════")
    log("🤖 AVVIO BOT AUTO-RESPONDER SOCIAL — IMMOBILIARE GIANCANI")
    log("   Piattaforme monitorate: Messenger, Facebook Comments, Instagram")
    log(f"   Intervallo Polling: {args.interval}s")
    if args.cycles > 0:
        log(f"   Cicli impostati: {args.cycles} (Durata totale: ~{args.cycles * args.interval}s)")
    log("   Canale notifiche: Telegram (Chat ID 1723292483)")
    log("══════════════════════════════════════════════════════════════════════")

    stato = carica_stato()
    log(f"📁 Stato caricato: {len(stato['messaggi_gestiti'])} messaggi, {len(stato['commenti_gestiti'])} commenti già evasi.")

    if args.once:
        esegui_ciclo_risposte(stato)
        log("✅ Ciclo singolo completato. — Immobiliare Giancani")
        return

    ciclo = 1
    while True:
        try:
            log(f"🔄 Inizio controllo #{ciclo}...")
            esegui_ciclo_risposte(stato)
            log(f"⏳ Ciclo #{ciclo} terminato. Prossimo controllo tra {args.interval} secondi...")
        except Exception as e:
            log(f"❌ Errore imprevisto nel ciclo: {e}")

        if args.cycles > 0 and ciclo >= args.cycles:
            log(f"🏁 Raggiunto numero massimo di cicli ({args.cycles}). Uscita regolare. — Immobiliare Giancani")
            break

        ciclo += 1
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
