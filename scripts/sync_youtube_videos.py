#!/usr/bin/env python3
"""
🎬 SYNC NOTTURNO VIDEO & SHORTS YOUTUBE (Ore 22:00 Italiana)
Estrae tutti i video pubblici e gli Shorts dal canale YouTube @immobiliaregiancani761
e ripopola automaticamente il foglio Google Sheet 'Post_YouTube'.
"""

import os
import re
import sys
import json
import ssl
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse

CHANNEL_ID = "UC7jCI1x_cwh_sOrNPJpaKyQ"
CHANNEL_HANDLE = "@immobiliaregiancani761"
GAS_WEBAPP_URL = os.environ.get(
    "GAS_WEBAPP_URL",
    "https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec"
)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

ctx = ssl._create_unverified_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
}

def extract_yt_initial_data(html):
    """Estrae l'oggetto JSON ytInitialData dalla pagina HTML di YouTube"""
    try:
        m = re.search(r'var ytInitialData\s*=\s*({.+?});</script>', html)
        if not m:
            m = re.search(r'window\["ytInitialData"\]\s*=\s*({.+?});</script>', html)
        if m:
            return json.loads(m.group(1))
    except Exception as e:
        print(f"⚠️ Errore estrazione ytInitialData: {e}")
    return None

def get_videos_from_channel_page(tab="videos"):
    """Scansiona la pagina /videos o /shorts estraendo tutti i video pubblici"""
    url = f"https://www.youtube.com/{CHANNEL_HANDLE}/{tab}"
    print(f"🌐 Scansione diretta pagina: {url}")
    videos = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            html = r.read().decode("utf-8")
        
        data = extract_yt_initial_data(html)
        if not data:
            # Fallback regex per videoId
            ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            unique_ids = list(dict.fromkeys(ids))
            for v_id in unique_ids:
                videos.append({
                    "videoId": v_id,
                    "titolo": f"Video YouTube ({v_id})",
                    "descrizione": "Splendida presentazione video del canale YouTube di Immobiliare Giancani.",
                    "thumbnail": f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg",
                    "isShort": (tab == "shorts"),
                    "prezzo": "Trattativa Riservata"
                })
            print(f"✅ Trovati {len(videos)} video via regex da /{tab}.")
            return videos

        # Estrazione ricorsiva dei nodi videoRenderer / richItemRenderer
        def parse_items(obj):
            if isinstance(obj, dict):
                if "videoRenderer" in obj:
                    vr = obj["videoRenderer"]
                    v_id = vr.get("videoId")
                    tit_obj = vr.get("title", {})
                    tit = tit_obj.get("runs", [{}])[0].get("text", "") or tit_obj.get("simpleText", "")
                    desc_obj = vr.get("descriptionSnippet", {})
                    descr = desc_obj.get("runs", [{}])[0].get("text", "") if desc_obj else ""
                    thumb_list = vr.get("thumbnail", {}).get("thumbnails", [])
                    thumb = thumb_list[-1]["url"] if thumb_list else f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg"
                    if v_id:
                        videos.append({
                            "videoId": v_id,
                            "titolo": tit or f"Video ({v_id})",
                            "descrizione": descr or f"Video del canale YouTube Immobiliare Giancani.",
                            "thumbnail": thumb,
                            "isShort": (tab == "shorts"),
                            "prezzo": "Trattativa Riservata"
                        })
                elif "reelItemRenderer" in obj:
                    rr = obj["reelItemRenderer"]
                    v_id = rr.get("videoId")
                    headline = rr.get("headline", {}).get("simpleText", "")
                    thumb_list = rr.get("thumbnail", {}).get("thumbnails", [])
                    thumb = thumb_list[-1]["url"] if thumb_list else f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg"
                    if v_id:
                        videos.append({
                            "videoId": v_id,
                            "titolo": headline or f"Shorts ({v_id})",
                            "descrizione": f"Shorts del canale YouTube Immobiliare Giancani.",
                            "thumbnail": thumb,
                            "isShort": True,
                            "prezzo": "Trattativa Riservata"
                        })
                for v in obj.values():
                    parse_items(v)
            elif isinstance(obj, list):
                for item in obj:
                    parse_items(item)

        parse_items(data)
        print(f"✅ Trovati {len(videos)} elementi da /{tab}.")
    except Exception as e:
        print(f"⚠️ Errore lettura {url}: {e}")
    return videos

def get_videos_from_rss():
    """Recupera gli ultimi video pubblici dal feed RSS ufficiale"""
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
    print(f"📡 Lettura Feed RSS: {rss_url}")
    videos = []
    try:
        req = urllib.request.Request(rss_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
            xml_data = r.read().decode("utf-8")
        
        root = ET.fromstring(xml_data)
        atom_ns = "{http://www.w3.org/2005/Atom}"
        yt_ns = "{http://www.youtube.com/xml/schemas/2015}"
        media_ns = "{http://search.yahoo.com/mrss/}"

        for entry in root.findall(f"{atom_ns}entry"):
            v_id_el = entry.find(f"{yt_ns}videoId")
            v_id = v_id_el.text if v_id_el is not None else ""
            title_el = entry.find(f"{atom_ns}title")
            title = title_el.text if title_el is not None else ""
            
            descr = ""
            thumb = f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg"
            group = entry.find(f"{media_ns}group")
            if group is not None:
                desc_el = group.find(f"{media_ns}description")
                if desc_el is not None and desc_el.text:
                    descr = desc_el.text
                th_el = group.find(f"{media_ns}thumbnail")
                if th_el is not None and "url" in th_el.attrib:
                    thumb = th_el.attrib["url"]

            is_short = ("#shorts" in title.lower() or "short" in title.lower())

            if v_id:
                videos.append({
                    "videoId": v_id,
                    "titolo": title,
                    "descrizione": descr,
                    "thumbnail": thumb,
                    "isShort": is_short,
                    "prezzo": "Trattativa Riservata"
                })
        print(f"✅ Trovati {len(videos)} video da RSS.")
    except Exception as e:
        print(f"⚠️ Errore RSS: {e}")
    return videos

def invia_notifica_telegram(msg):
    """Invia notifica Telegram se configurata"""
    token = TELEGRAM_BOT_TOKEN
    chat_id = TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10, context=ctx)
    except Exception as e:
        print(f"Telegram notice error: {e}")

def main():
    print("🎬 AVVIO SINCRONIZZAZIONE NOTTURNA YOUTUBE (22:00)...")
    
    all_videos = {}

    # 1. Scansiona Video standard
    for v in get_videos_from_channel_page("videos"):
        all_videos[v["videoId"]] = v

    # 2. Scansiona Shorts
    for v in get_videos_from_channel_page("shorts"):
        if v["videoId"] not in all_videos:
            all_videos[v["videoId"]] = v
        else:
            all_videos[v["videoId"]]["isShort"] = True

    # 3. Scansiona Feed RSS per testi completi
    for v in get_videos_from_rss():
        if v["videoId"] not in all_videos:
            all_videos[v["videoId"]] = v
        else:
            if v.get("descrizione") and len(v["descrizione"]) > len(all_videos[v["videoId"]].get("descrizione", "")):
                all_videos[v["videoId"]]["descrizione"] = v["descrizione"]
            if v.get("titolo") and len(v["titolo"]) > len(all_videos[v["videoId"]].get("titolo", "")):
                all_videos[v["videoId"]]["titolo"] = v["titolo"]

    final_list = list(all_videos.values())
    print(f"📊 Totale complessivo video & Shorts individuati: {len(final_list)}")

    if not final_list:
        print("⚠️ Nessun video estratto. Chiamata fallback a Google Apps Script...")
        try:
            url_fb = f"{GAS_WEBAPP_URL}?action=sincronizza_youtube_nightly"
            req = urllib.request.Request(url_fb, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
                res_fb = json.loads(r.read().decode("utf-8"))
                print("Risposta fallback:", res_fb)
        except Exception as eFb:
            print("Errore fallback:", eFb)
        return

    # 4. Invia dati a Google Apps Script per ripopolare 'Post_YouTube'
    payload = {
        "action": "salva_video_youtube_batch",
        "videos": final_list
    }

    try:
        data_json = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            GAS_WEBAPP_URL,
            data=data_json,
            headers={"Content-Type": "application/json", "User-Agent": "Antigravity-YouTube-Sync/1.0"}
        )
        with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
            res_txt = r.read().decode("utf-8")
            print(f"📥 Risposta Google Apps Script: {res_txt}")
            res_json = json.loads(res_txt)
            if res_json.get("success"):
                print(f"🎉 SUCCESSO! Foglio Post_YouTube ripopolato con {len(final_list)} video!")
            else:
                print(f"⚠️ Avviso GAS: {res_json.get('error')}")
    except Exception as e:
        print(f"❌ Errore durante il salvataggio in Google Apps Script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
