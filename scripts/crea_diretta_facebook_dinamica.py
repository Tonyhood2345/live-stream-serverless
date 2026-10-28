#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
🔴 CREAZIONE DIRETTA FACEBOOK LIVE DINAMICA — IMMOBILIARE GIANCANI
═══════════════════════════════════════════════════════════════════════════════
Crea automaticamente una sessione Facebook Live attiva tramite Meta Graph API
per la Pagina Ufficiale Immobiliare Giancani (ID: 234931856561526).
Salva l'endpoint RTMP pronto per FFmpeg in /tmp/facebook_rtmp.txt.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import ssl
import json
import urllib.request
import urllib.parse
from pathlib import Path

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

PAGE_ID = os.environ.get("FB_PAGE_ID", "234931856561526").strip()
PAGE_TOKEN = (os.environ.get("FB_PAGE_TOKEN") or os.environ.get("FB_PAGE_ACCESS_TOKEN", "")).strip()

# Token attivo Immobiliare Giancani
TOKEN_DEFAULT = "EAAZAH7q8wRZAEBSzTkBqcUBDxlorlwv7dNR1WWCAlimAmfCUjjeIYT6viHp9aCEnWtZBNVpGGSuE7qtZBRKTnWBmvkLFxCHZBGFKaPxvAAYyiWN2p3goYm37d8JTKwo9JOhGGSI5qE7oZBWr1pH8BHjYDlHHu6yJvRywZCYnyuBIuZAS7Maj9Bx49WtpIH9W8ddJBgPVu9GMF92UWLg6"

if not PAGE_TOKEN:
    PAGE_TOKEN = TOKEN_DEFAULT

print(f"📘 [FACEBOOK LIVE] Inizializzazione diretta su Pagina ID: {PAGE_ID}...")

url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/live_videos"
payload = urllib.parse.urlencode({
    "status": "LIVE_NOW",
    "title": "🔴 DIRETTA IMMOBILIARE GIANCANI — Visite e Annunci Esclusivi",
    "description": "Segui la trasmissione in diretta streaming con DarIA e DarIO! Visita gli immobili in vendita ad Agrigento e provincia.\n\n— Immobiliare Giancani",
    "access_token": PAGE_TOKEN
}).encode("utf-8")

req = urllib.request.Request(url, data=payload, method="POST")
try:
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        stream_url = data.get("secure_stream_url") or data.get("stream_url")
        video_id = data.get("id")
        if stream_url:
            print(f"✅ Diretta Facebook creata con successo! Video ID: {video_id}")
            print(f"🔗 Stream URL: {stream_url[:60]}...")
            
            # Scrive l'endpoint in tutti i percorsi standard
            targets = [
                Path("/tmp/facebook_rtmp.txt"),
                Path("facebook_rtmp.txt"),
                Path(os.environ.get("TEMP", ".")) / "facebook_rtmp.txt"
            ]
            for t in targets:
                try:
                    t.parent.mkdir(parents=True, exist_ok=True)
                    t.write_text(stream_url.strip(), encoding="utf-8")
                except Exception:
                    pass
                    
            if video_id:
                try:
                    Path("/tmp/facebook_live_id.txt").write_text(str(video_id), encoding="utf-8")
                except Exception:
                    pass
                    
            print("📄 Endpoint Facebook Live salvato con successo! — Immobiliare Giancani")
            sys.exit(0)
        else:
            print("⚠️ Nessun stream_url restituito:", data)
except Exception as e:
    print(f"❌ Errore creazione diretta Facebook: {e}")

sys.exit(1)
