import os
import sys
import ssl
import json
import urllib.request
import urllib.parse

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

PAGE_ID = os.environ.get("FB_PAGE_ID", "234931856561526").strip()
PAGE_TOKEN = (os.environ.get("FB_PAGE_TOKEN") or os.environ.get("FB_PAGE_ACCESS_TOKEN", "")).strip()

if not PAGE_TOKEN:
    PAGE_TOKEN = "EAAZAH7q8wRZAEBS3ZAfEIpFIcXPJ87gDZAY8QjpGvBSjgC44c22JVeZAiDxMOM85JRMKM2T1hLgekBCkT0z5geNsb3KxAhMr7W7xlOGVKJsdKV9rZCEKLupIy1uNaDkVZAXmFtn0stiB212odWJ2ZCZBtlWkZAzy5wmPfKyZC3g27g6RXs0FK2GiYc5MeqaZCZBuoYjIyreTZAxwOqtfESifVw"

print(f"📘 Creazione evento Live Video via Meta Graph API su Pagina ID: {PAGE_ID}...")

url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/live_videos"
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
            print(f"🔗 Stream URL: {stream_url}")
            with open("/tmp/facebook_rtmp.txt", "w", encoding="utf-8") as f:
                f.write(stream_url)
            sys.exit(0)
        else:
            print("⚠️ Nessun stream_url restituito:", data)
except Exception as e:
    print(f"❌ Errore creazione diretta Facebook: {e}")

sys.exit(1)
