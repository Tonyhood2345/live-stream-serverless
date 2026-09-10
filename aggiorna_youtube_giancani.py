#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
🤖 SINCRONIZZATORE NOTTURNO YOUTUBE — IMMOBILIARE GIANCANI
=============================================================================
Canale: https://www.youtube.com/@immobiliaregiancani761
Channel ID: UC7jCI1x_cwh_sOrNPJpaKyQ
Foglio Google: Post_YouTube
Schedulazione: Ogni notte alle ore 02:00

Struttura Standard Colonne Scheda Immobile:
- Colonna A (1): URL_MEDIA (Embed YouTube)
- Colonna B (2): PREZZO (Prezzo estratto o 'Trattativa Riservata')
- Colonna C (3): MQ ('Canale YouTube' o metratura)
- Colonna D (4): TITOLO_VIDEO (Titolo pulito dell'immobile)
- Colonna E (5): TIPO_MEDIA ('video' / 'youtube')
- Colonna F (6): TESTO_PARLATO (Rigorosamente Colonna F con firma Immobiliare Giancani)
- Colonna G (7): URL_ANTEPRIMA (Miniatura HQ)
- Colonna H (8): TESTO_TICKER (Testo per banner)
- Colonna I (9): LINK_YOUTUBE (Link diretto)
- Colonna J (10): DURATA_SEC (Secondi di permanenza a schermo)
=============================================================================
"""

import sys
import os
import json
import re
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
from datetime import datetime

CANALE_HANDLE = "@immobiliaregiancani761"
CHANNEL_ID = "UC7jCI1x_cwh_sOrNPJpaKyQ"
YOUTUBE_RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
WEBAPP_EXEC_URL = "https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec"


def estrai_prezzo_da_testo(testo):
    """Estrae un prezzo veritiero dal titolo/descrizione (es. 75.000, 33.000 euro) evitando date."""
    if not testo:
        return "Trattativa Riservata"
    
    # Cerca pattern tipo 75.000, 120.000, 33000 euro, 75k
    m_euro = re.search(r'(\d{2,3}[\.\s]?\d{3})\s*(?:€|euro|\.000)', testo, re.IGNORECASE)
    if m_euro:
        val = m_euro.group(1).replace(' ', '.').replace(',', '.')
        if not val.endswith('.000') and '.' not in val:
            val = f"{val[:2]}.{val[2:]}"
        return f"{val} €"
    
    m_num = re.search(r'([2-9]\d{1,2}\.000)', testo)
    if m_num:
        return f"{m_num.group(1)} €"
        
    return "Trattativa Riservata"


def estrai_video_youtube():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Connessione al canale YouTube: {CANALE_HANDLE} (ID: {CHANNEL_ID})...")
    req = urllib.request.Request(
        YOUTUBE_RSS_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    
    for tentativo_rss in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                xml_data = response.read()
            break  # Uscita dal loop se ok
        except Exception as e:
            print(f"⚠️ Feed RSS YouTube tentativo {tentativo_rss}/3: {e}")
            if tentativo_rss == 3:
                print("❌ Feed RSS YouTube non raggiungibile dopo 3 tentativi. Operazione annullata.")
                return []
            import time as _t; _t.sleep(tentativo_rss * 8)

    root = ET.fromstring(xml_data)
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'yt': 'http://www.youtube.com/xml/schemas/2015',
        'media': 'http://search.yahoo.com/mrss/'
    }

    video_list = []
    entries = root.findall('atom:entry', ns)
    print(f"🎬 Trovati {len(entries)} video pubblicati sul canale.")

    for entry in entries:
        video_id = entry.find('yt:videoId', ns).text if entry.find('yt:videoId', ns) is not None else ""
        raw_title = entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else "Video Immobile"
        published_raw = entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else ""
        published = published_raw.split('T')[0] if published_raw else datetime.now().strftime('%Y-%m-%d')
        
        media_group = entry.find('media:group', ns)
        description = ""
        thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        
        if media_group is not None:
            desc_elem = media_group.find('media:description', ns)
            if desc_elem is not None and desc_elem.text:
                description = desc_elem.text.strip()
            thumb_elem = media_group.find('media:thumbnail', ns)
            if thumb_elem is not None and 'url' in thumb_elem.attrib:
                thumb_url = thumb_elem.attrib['url']
        
        # Pulisci titolo per evitare titoli come solo una data
        titolo_pulito = raw_title.strip()
        if re.match(r'^\d{1,2}\s+[A-Za-z]+\s+\d{4}$', titolo_pulito):
            titolo_pulito = f"Immobile in Evidenza ({titolo_pulito})"
            
        prezzo_estratto = estrai_prezzo_da_testo(raw_title + " " + description)
        
        link_yt = f"https://www.youtube.com/watch?v={video_id}"
        embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0&controls=0&rel=0"
        
        # REGOLA GLOBALE: Testo parlato da Colonna F con firma Immobiliare Giancani
        testo_col_f = description if description and len(description) > 20 else f"Presentazione video dell'immobile: {titolo_pulito}. Contattateci subito per maggiori informazioni o per prenotare una visita."
        if "Immobiliare Giancani" not in testo_col_f:
            testo_col_f = f"{testo_col_f.strip()} — Presentato da Immobiliare Giancani."

        ticker_text = f"🎬 VIDEO YOUTUBE: {titolo_pulito} — Immobiliare Giancani"

        # Struttura allineata al 100% alle 10 Colonne Standard delle Schede Immobile
        video_data = {
            "colA_urlMedia": embed_url,
            "colB_prezzo": prezzo_estratto,
            "colC_mq": "YouTube",
            "colD_titolo": titolo_pulito,
            "colE_tipoMedia": "video",
            "colF_testo": testo_col_f,
            "colG_thumb": thumb_url,
            "colH_ticker": ticker_text,
            "colI_link": link_yt,
            "colJ_durataSec": 90,
            "videoId": video_id,
            "dataPubb": published
        }
        video_list.append(video_data)
        print(f"  -> ✅ [OK] Titolo: '{titolo_pulito}' | Prezzo: '{prezzo_estratto}' | ID: {video_id}")

    return video_list


def invia_al_foglio_google(video_list, max_tentativi=3):
    if not video_list:
        print("⚠️ Nessun video da sincronizzare.")
        return False
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📤 Invio {len(video_list)} video al Google Sheet Post_YouTube...")
    payload = {
        "action": "SYNC_YOUTUBE_FROM_PYTHON",
        "channel": CANALE_HANDLE,
        "channelId": CHANNEL_ID,
        "videos": video_list
    }
    
    data_bytes = json.dumps(payload).encode('utf-8')

    for tentativo in range(1, max_tentativi + 1):
        try:
            req = urllib.request.Request(
                WEBAPP_EXEC_URL,
                data=data_bytes,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=45) as res:
                res_body = res.read().decode('utf-8')
                print(f"✅ Risposta GAS: {res_body[:200]}")
                print(f"🎉 Sincronizzazione completata! {len(video_list)} video allineati — Immobiliare Giancani")
                return True
        except Exception as e:
            print(f"⚠️ Invio tentativo {tentativo}/{max_tentativi} fallito: {e}")
            if tentativo < max_tentativi:
                wait = tentativo * 10
                print(f"  ⏳ Riprovo tra {wait} secondi...")
                import time as _t; _t.sleep(wait)

    print(f"❌ Tutti i {max_tentativi} tentativi di invio falliti. Sincronizzazione non completata.")
    return False


def main():
    print("=========================================================")
    print(" 🚀 AVVIO SINCRONIZZAZIONE CANALE YOUTUBE ALLE 02:00")
    print("=========================================================")
    videos = estrai_video_youtube()
    if videos:
        invia_al_foglio_google(videos)
    print("=========================================================")
    print(" 🏁 PROCEDURA COMPLETATA.")
    print("=========================================================")


if __name__ == "__main__":
    main()
