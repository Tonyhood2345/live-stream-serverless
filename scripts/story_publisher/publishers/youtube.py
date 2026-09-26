#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connettore Ufficiale YouTube Shorts (@immobiliaregiancani761)
Sincronizzazione video promozionali verticali di DarIA tramite YouTube Data API v3 (OAuth2).
Canale ID: UC7jCI1x_cwh_sOrNPJpaKyQ (giancaniimmobiliare2@gmail.com)
"""

import os
import json
import base64
import urllib.request
from story_publisher.config import APPS_SCRIPT_URL
from story_publisher.system.env import unverified_create_default_context


def ottieni_client_youtube():
    """Recupera il client YouTube autenticato tramite OAuth2 token."""
    search_dirs = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ]
    token_names = [
        "token_youtube.json",
        "token_youtube_giancani.json",
        "token_youtube_mitologia.json"
    ]

    token_path = None
    for d in search_dirs:
        for tn in token_names:
            candidate = os.path.join(d, tn)
            if os.path.exists(candidate) and os.path.getsize(candidate) > 100:
                token_path = candidate
                break
        if token_path:
            break

    # Variabile d'ambiente GitHub Actions
    env_token = os.environ.get("YOUTUBE_TOKEN_GIANCANI_JSON") or os.environ.get("YOUTUBE_TOKEN_MITOLOGIA_JSON")

    if not token_path and not env_token:
        return None

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import google_auth_httplib2
        import httplib2

        scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
        if env_token:
            creds = Credentials.from_authorized_user_info(json.loads(env_token), scopes)
        else:
            creds = Credentials.from_authorized_user_file(token_path, scopes)

        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                if token_path:
                    with open(token_path, "w", encoding="utf-8") as tf:
                        tf.write(creds.to_json())
            except Exception as e_rf:
                print(f"  ⚠️ Warning refresh token YouTube: {e_rf}")

        if creds.valid:
            http_client = httplib2.Http(disable_ssl_certificate_validation=True)
            auth_http = google_auth_httplib2.AuthorizedHttp(creds, http=http_client)
            return build("youtube", "v3", http=auth_http)
    except Exception as e_c:
        print(f"  ⚠️ Warning inizializzazione YouTube API: {e_c}")
    return None


def pubblica_short_youtube(video_path, item_data):
    """
    Pubblica direttamente il video come YouTube Short sul canale ufficiale
    @immobiliaregiancani761 (ID: UC7jCI1x_cwh_sOrNPJpaKyQ) tramite YouTube Data API v3.
    """
    print("\n🎬 Pubblicazione YouTube Short sul Canale (@immobiliaregiancani761)...")
    try:
        titolo = item_data.get('titolo', 'Opportunità Immobiliare')
        prezzo = item_data.get('prezzo', 'Trattativa Riservata')
        mq = item_data.get('mq', '120 metri quadri')
        testo_f = item_data.get('testoF', '').strip()
        is_live = item_data.get('isLive', False)

        # 1. Upload diretto con YouTube Data API v3
        youtube = ottieni_client_youtube()
        if youtube and os.path.exists(video_path):
            from googleapiclient.http import MediaFileUpload

            short_title = f"{titolo} | {prezzo} #Shorts"
            if len(short_title) > 95:
                short_title = f"{titolo[:60]} | #Shorts"

            prefix_live = "🔴 IN DIRETTA ORA! " if is_live else ""
            description = (
                f"🏢 {prefix_live}{titolo.upper()}\n"
                f"📐 Superficie: {mq}\n"
                f"💰 Prezzo: {prezzo}\n\n"
                f"📜 Descrizione Ufficiale DarIA (Colonna F):\n"
                f"«{testo_f}»\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👉 Per informazioni e visite:\n"
                f"🏠 IMMOBILIARE GIANCANI — Favara (Agrigento)\n"
                f"📍 Corso Vittorio Veneto 151, Favara (AG)\n"
                f"🌐 Sito Web Ufficiale: https://immobiliaregiancani.it\n"
                f"📞 Telefono: +39 320 166 7156\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"#Shorts #ImmobiliareGiancani #Favara #Agrigento #CaseInVendita #DarIA #AntonioGiancani"
            )

            body = {
                "snippet": {
                    "title": short_title,
                    "description": description,
                    "tags": ["Immobiliare Giancani", "Favara", "Agrigento", "Case in Vendita", "Immobiliare", "DarIA", "Shorts", "YouTube Shorts", "Antonio Giancani"],
                    "categoryId": "27",
                    "defaultLanguage": "it"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
            print("  🚀 [YouTube Data API] Upload in corso su @immobiliaregiancani761...")
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = request.execute()
            v_id = response.get("id")
            yt_short_url = f"https://youtube.com/shorts/{v_id}"
            print(f"  ✅ [YouTube Shorts] Pubblicato con successo! URL: {yt_short_url}")
            return {
                "nome": "YouTube Shorts (@immobiliaregiancani761)",
                "success": True,
                "story_id": v_id,
                "url": yt_short_url
            }

        # 2. Fallback secondario su Apps Script
        ctx = unverified_create_default_context()
        payload = {
            "action": "pubblica_youtube_short",
            "titolo": titolo,
            "mq": mq,
            "prezzo": prezzo,
            "testoF": testo_f,
            "videoUrl": item_data.get('videoUrl', ''),
            "thumbUrl": item_data.get('thumbUrl', '')
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
