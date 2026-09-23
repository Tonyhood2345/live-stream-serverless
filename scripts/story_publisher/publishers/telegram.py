#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connettore Notifiche Telegram Staff Immobiliare Giancani
"""

import urllib.request
import urllib.parse
from story_publisher.config import APPS_SCRIPT_URL
from story_publisher.system.env import unverified_create_default_context

def invia_notifica_telegram(titolo, mq, prezzo, risultati, is_live=True):
    """Invia notifica Telegram aziendale con riepilogo dello stato di pubblicazione."""
    ctx = unverified_create_default_context()
    try:
        tipo_str = "🔴 STORIA LIVE (OGNI 30 MIN)" if is_live else "🕒 STORIA ORARIA (OFFLINE)"
        lines = [
            f"🎬 <b>{tipo_str} PUBBLICATA CON SUCCESSO!</b> ✨",
            f"🏠 <b>Immobile:</b> {titolo}",
            f"📐 <b>Superficie:</b> {mq}",
            f"💰 <b>Prezzo:</b> {prezzo}",
            f"🎵 <b>Audio:</b> Musica Allegra (124 BPM) + Voce Neural HD",
            f"⏱️ <b>Durata video:</b> 15 secondi continui Full HD\n"
        ]
        for r in risultati:
            status = "✅ Pubblicata" if r.get("success") else f"⚠️ {r.get('error', 'Fallita')}"
            lines.append(f"• <b>{r.get('nome')}:</b> {status} (ID: {r.get('story_id', 'N/D')})")

        lines.append("\n— <b>Immobiliare Giancani</b>")
        msg = "\n".join(lines)
        url_tg = f"{APPS_SCRIPT_URL}?action=invia_notifica&msg={urllib.parse.quote(msg)}"
        req_tg = urllib.request.Request(url_tg, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_tg, timeout=10, context=ctx) as _:
            pass
    except Exception as e:
        print(f"Avviso notifica Telegram: {e}")
