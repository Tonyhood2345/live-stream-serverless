#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connettore Meta Graph API per Facebook
Gestisce la pubblicazione di Storie Video (Resumable Upload) e Note / Post sul Feed.
"""

import os
import json
import urllib.request
import urllib.parse
from story_publisher.system.env import unverified_create_default_context
from story_publisher.core.compliance import normalize_mq
from story_publisher.audio.copywriter import determina_fascia_oraria

def pubblica_storia_video_su_facebook(page_id, page_token, video_path):
    """Carica la video storia su Facebook via Meta Graph API (Resumable Upload)."""
    file_size = os.path.getsize(video_path)
    ctx = unverified_create_default_context()

    # 1. Start Phase
    url_start = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"
    params_start = f"upload_phase=start&access_token={urllib.parse.quote(page_token)}".encode('utf-8')
    req_start = urllib.request.Request(url_start, data=params_start, method='POST')

    with urllib.request.urlopen(req_start, context=ctx) as resp_start:
        start_data = json.loads(resp_start.read().decode('utf-8'))
        video_id = start_data.get('video_id')
        upload_url = start_data.get('upload_url')
        if not video_id or not upload_url:
            raise Exception("Meta API non ha restituito video_id o upload_url")

    # 2. Upload Phase
    with open(video_path, 'rb') as f:
        video_bytes = f.read()

    req_upload = urllib.request.Request(upload_url, data=video_bytes, method='POST')
    req_upload.add_header('Authorization', f'OAuth {page_token}')
    req_upload.add_header('offset', '0')
    req_upload.add_header('file_size', str(file_size))
    req_upload.add_header('Content-Type', 'application/octet-stream')

    with urllib.request.urlopen(req_upload, context=ctx) as resp_upload:
        up_res = json.loads(resp_upload.read().decode('utf-8'))
        if not up_res.get('success'):
            raise Exception(f"Upload fallito: {up_res}")

    # 3. Finish Phase
    url_finish = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"
    params_finish = f"upload_phase=finish&video_id={video_id}&video_state=PUBLISHED&access_token={urllib.parse.quote(page_token)}".encode('utf-8')
    req_finish = urllib.request.Request(url_finish, data=params_finish, method='POST')

    with urllib.request.urlopen(req_finish, context=ctx) as resp_finish:
        fin_res = json.loads(resp_finish.read().decode('utf-8'))
        return {
            "success": fin_res.get('success', True),
            "video_id": video_id,
            "story_id": fin_res.get('post_id') or video_id,
            "type": "video_story"
        }

def pubblica_nota_facebook_pagina(page_id, page_token, media_info, fascia_info=None):
    """
    Pubblica una 'Nota di Pagina' (Post ricco sul feed di Facebook) strutturata con:
    - Saluto del momento (Mattina, Pomeriggio, Sera, Notte)
    - Emoticon espressive
    - Pensiero d'ispirazione per il benessere e la casa
    - Scheda immobile con Colonna F e superfici rigorosamente in 'metri quadri'
    - Indicazione della canzone royalty-free garantita di Facebook
    - Firma: — Immobiliare Giancani
    """
    ctx = unverified_create_default_context()
    if not fascia_info:
        fascia_info = determina_fascia_oraria()

    titolo = media_info.get('titolo', 'Opportunità Esclusiva')
    prezzo = media_info.get('prezzo', 'Trattativa Riservata')
    mq = normalize_mq(media_info.get('mq', '120 metri quadri'))
    testo_f = media_info.get('testoF', '').strip()
    if testo_f:
        import re
        testo_f = re.sub(r'\s*—?\s*Immobiliare Giancani\s*$', '', testo_f, flags=re.IGNORECASE).strip()

    messaggio_nota = (
        f"{fascia_info['titolo_nota']}\n\n"
        f"{fascia_info['riflessione_nota']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏠 IMMOBILE IN EVIDENZA: {titolo.upper()}\n"
        f"📐 SUPERFICIE: {mq}\n"
        f"💰 PREZZO: {prezzo}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎙️ Dettagli esclusivi: \"{testo_f}\"\n\n"
        f"🎵 Canzone di sottofondo consigliata: {fascia_info['musica_titolo']}\n\n"
        f"👉 Per informazioni, dettagli e visite guidate sul posto:\n"
        f"📞 Contattaci direttamente o invia un messaggio in privato.\n\n"
        f"📱 Seguici sui nostri canali ufficiali:\n"
        f"• Facebook: https://www.facebook.com/immobiliaregiancani\n"
        f"• YouTube: https://www.youtube.com/@immobiliaregiancani761\n"
        f"• Instagram: https://www.instagram.com/giancani_immobiliare/\n"
        f"• TikTok: https://www.tiktok.com/@immobiliare_giancani\n\n"
        f"— Immobiliare Giancani"
    )

    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    payload = urllib.parse.urlencode({
        "message": messaggio_nota,
        "access_token": page_token
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[OK] Nota Facebook pubblicata su ID {page_id}! Post ID: {data.get('id')}")
            return {"success": True, "post_id": data.get("id"), "fascia": fascia_info["fascia"]}
    except Exception as e:
        print(f"Errore pubblicazione nota su Facebook ({page_id}): {e}")
        return {"success": False, "error": str(e), "fascia": fascia_info["fascia"]}
