#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connettore YouTube Shorts (@immobiliaregiancani761)
Sincronizzazione video promozionali verticali tramite backend Google Apps Script.
"""

import os
import json
import base64
import urllib.request
from story_publisher.config import APPS_SCRIPT_URL
from story_publisher.system.env import unverified_create_default_context

def pubblica_short_youtube(video_path, item_data):
    """
    Pubblica o registra il video come YouTube Short sul canale @immobiliaregiancani761.
    Comunica con l'endpoint Apps Script per indicizzazione e pubblicazione diretta.
    """
    print("\n🎬 Pubblicazione YouTube Short sul Canale (@immobiliaregiancani761)...")
    ctx = unverified_create_default_context()
    try:
        titolo = item_data.get('titolo', 'Opportunità Immobiliare')
        prezzo = item_data.get('prezzo', 'Trattativa Riservata')
        mq = item_data.get('mq', '120 metri quadri')
        testo_f = item_data.get('testoF', '')
        video_url = item_data.get('videoUrl', '')
        thumb_url = item_data.get('thumbUrl', '')

        payload = {
            "action": "pubblica_youtube_short",
            "titolo": titolo,
            "mq": mq,
            "prezzo": prezzo,
            "testoF": testo_f,
            "videoUrl": video_url,
            "thumbUrl": thumb_url
        }

        if os.path.exists(video_path) and os.path.getsize(video_path) < 8 * 1024 * 1024:
            with open(video_path, 'rb') as f:
                payload["base64Video"] = base64.b64encode(f.read()).decode('utf-8')

        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            APPS_SCRIPT_URL,
            data=req_data,
            headers={"Content-Type": "application/json", "User-Agent": "Giancani-YouTube-Shorts-Bot"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=35, context=ctx) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            return {
                "nome": "YouTube Shorts (@immobiliaregiancani761)",
                "success": res_json.get('success', True),
                "story_id": res_json.get('videoId') or res_json.get('status', 'REGISTRATO'),
                "url": res_json.get('shortUrl', 'https://www.youtube.com/@immobiliaregiancani761/shorts')
            }
    except Exception as eYt:
        print(f"Avviso YouTube Shorts: {eYt}")
        return {
            "nome": "YouTube Shorts (@immobiliaregiancani761)",
            "success": False,
            "error": str(eYt)
        }
