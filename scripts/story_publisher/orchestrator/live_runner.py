#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestratore Modalità LIVE (durante la diretta streaming, ogni 30 minuti)
"""

import json
import urllib.request
import requests

from story_publisher.config import PAGES, IG_ACCOUNT_ID, APPS_SCRIPT_URL
from story_publisher.system.env import unverified_create_default_context
from story_publisher.system.network import check_is_live_active, normalizza_foto_url
from story_publisher.core.compliance import normalize_mq
from story_publisher.video.video_engine import genera_video_da_clip_o_foto
from story_publisher.publishers.facebook import pubblica_storia_video_su_facebook
from story_publisher.publishers.instagram import pubblica_storia_instagram
from story_publisher.publishers.youtube import pubblica_short_youtube
from story_publisher.publishers.tiktok import pubblica_storia_tiktok
from story_publisher.publishers.telegram import invia_notifica_telegram

def esegui_ciclo_live(style="auto"):
    """
    Esegue un ciclo di pubblicazione storia durante la diretta streaming (ogni 30 minuti).
    GUARDIA RIGOROSA: se non è in diretta live streaming, NON esegue alcuna pubblicazione.
    """
    print("\n" + "═" * 70)
    print("🚀 CICLO STORIA LIVE FACEBOOK (OGNI 30 MINUTI)")
    print("═" * 70)

    # 1. CONTROLLO DIRETTA LIVE ATTIVA ("se non è in diretta nulla")
    is_live, run_id = check_is_live_active()
    if not is_live:
        print("🔴 Nessuna diretta live streaming in corso su YouTube / Facebook / GitHub Actions.")
        print("ℹ️ Direttiva attiva: quando non si è in diretta, il bot NON pubblica alcuna storia e rimane a riposo.")
        print("— Immobiliare Giancani\n")
        return []

    print(f"🔴 DIRETTA STREAMING ATTIVA (Run ID: {run_id}). Avvio generazione storia live con rotazione grafica...")

    ctx = unverified_create_default_context()
    # Recupera immobile attivo dal backend
    url_imm = f"{APPS_SCRIPT_URL}?action=debug_immobile&q=current"
    prop_data = {}
    try:
        r_imm = requests.get(url_imm, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=20)
        if r_imm.status_code == 200:
            prop_data = r_imm.json()
    except Exception as e:
        print(f"Avviso recupero dati immobile in diretta via requests: {e}")
        try:
            req_imm = urllib.request.Request(url_imm, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_imm, timeout=20, context=ctx) as resp:
                prop_data = json.loads(resp.read().decode('utf-8'))
        except Exception as e2:
            print(f"Avviso fallback urllib: {e2}")

    titolo_base = prop_data.get('titolo') or "Immobile in Diretta"
    stanza = prop_data.get('stanza')
    if stanza and stanza.lower() not in ['ambiente', ''] and stanza.lower() != titolo_base.lower():
        titolo = f"{titolo_base} — {stanza}"
    else:
        titolo = titolo_base

    prezzo = prop_data.get('prezzo', 'Trattativa Riservata')
    mq = normalize_mq(prop_data.get('mq', '120'))
    foto_raw = prop_data.get('mediaUrl') or prop_data.get('fotoUrl')
    foto_url = normalizza_foto_url(foto_raw)
    testo_f = prop_data.get('testoDaLeggere') or prop_data.get('testo') or "Tour virtuale in diretta streaming con Dario e DarIA. — Immobiliare Giancani"

    media_info = {
        "titolo": titolo,
        "prezzo": prezzo,
        "mq": mq,
        "fotoUrl": foto_url,
        "testoF": testo_f,
        "isLive": True
    }

    video_path = genera_video_da_clip_o_foto(media_info, style=style)
    if not video_path:
        print("❌ Errore generazione video storia live.")
        return []

    risultati = []
    for target in PAGES:
        print(f"📘 Pubblicazione Video Storia su: {target['nome']}...")
        try:
            res = pubblica_storia_video_su_facebook(target['id'], target['token'], video_path)
            res['nome'] = target['nome']
            print(f"[OK] Storia pubblicata! ID: {res.get('story_id')}")
            risultati.append(res)
        except Exception as ePub:
            print(f"❌ Errore upload su {target['nome']}: {ePub}")
            risultati.append({"nome": target['nome'], "success": False, "error": str(ePub)})

    # Pubblica su Instagram Stories (@giancani_immobiliare)
    try:
        res_ig = pubblica_storia_instagram(IG_ACCOUNT_ID, PAGES[0]['token'], video_path)
        print(f"[OK] Instagram Stories: {res_ig.get('story_id')} ({res_ig.get('metodo')})")
        risultati.append(res_ig)
    except Exception as eIg:
        print(f"❌ Errore Instagram Stories: {eIg}")
        risultati.append({"nome": "Instagram Stories (@giancani_immobiliare)", "success": False, "error": str(eIg)})

    # Pubblica su YouTube Shorts (@immobiliaregiancani761)
    try:
        res_yt = pubblica_short_youtube(video_path, media_info)
        print(f"[OK] YouTube Shorts: {res_yt.get('story_id')} - {res_yt.get('url')}")
        risultati.append(res_yt)
    except Exception as eYt:
        print(f"❌ Errore YouTube Shorts: {eYt}")
        risultati.append({"nome": "YouTube Shorts (@immobiliaregiancani761)", "success": False, "error": str(eYt)})

    # Pubblica / Sincronizza su TikTok Stories (@immobiliare_giancani)
    try:
        res_tk = pubblica_storia_tiktok(video_path, media_info)
        print(f"[OK] TikTok Stories: {res_tk.get('story_id')} - {res_tk.get('url')}")
        risultati.append(res_tk)
    except Exception as eTk:
        print(f"❌ Errore TikTok Stories: {eTk}")
        risultati.append({"nome": "TikTok Stories (@immobiliare_giancani)", "success": False, "error": str(eTk)})

    invia_notifica_telegram(titolo, mq, prezzo, risultati, is_live=True)
    print("✨ Ciclo storia live multi-piattaforma completato. — Immobiliare Giancani\n")
    return risultati
