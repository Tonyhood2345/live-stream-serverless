#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BOT REELS 9:16 — STORIE BIBLICHE («ETERNO NOSTRA GIUSTIZIA»)
================================================================================
- Tema: Storie e Racconti della Sacra Bibbia (Ore 20:00)
- Stile Visivo: Cartone Animato 2D con personaggi biblici espressivi (David, Mosè, ecc.), NO GATTO
- Voce Neurale: it-IT-GiuseppeNeural (Solenne, saggia e calda)
- Canale: Eterno nostra giustizia
- Destinazione per questo test: SOLO ED ESCLUSIVAMENTE TELEGRAM
- Regola Globale: Testi prelevati rigorosamente dalla Colonna F
- Personal Branding Finale: IMMOBILIARE GIANCANI
================================================================================
"""

import sys
import os
import asyncio
import argparse

# Percorso base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import esegui_pipeline

def main():
    parser = argparse.ArgumentParser(
        description="Bot Reels 9:16 — Storie Bibliche («Eterno Nostra Giustizia») — Invio Esclusivo Telegram"
    )
    parser.add_argument("--id", type=str, default=None, help="ID della storia biblica (es. 1 per Davide e Golia, 2 per Mar Rosso)")
    parser.add_argument("--voice", type=str, default="it-IT-GiuseppeNeural", help="Voce Edge-TTS (default: it-IT-GiuseppeNeural)")
    parser.add_argument("--json", action="store_true", help="Stampa solo lo schema JSON senza montare il video")
    parser.add_argument("--anche-social", action="store_true", help="Se abilitato pubblica anche sui social (default: SOLO TELEGRAM)")
    args = parser.parse_args()

    print("=" * 80)
    print("📖 AVVIO BOT DEDICATO: STORIE BIBLICHE («ETERNO NOSTRA GIUSTIZIA»)")
    print("🎯 Modalità: BIBBIA | Formato: Verticale 9:16 (2 Minuti)")
    print("🛡️ Destinazione attiva: SOLO ED ESCLUSIVAMENTE TELEGRAM")
    print("⭐ Produzione e Personal Branding: IMMOBILIARE GIANCANI")
    print("=" * 80)

    # Esecuzione pipeline in modalità bibbia con invio esclusivo su Telegram
    solo_tg = not args.anche_social
    asyncio.run(esegui_pipeline(
        story_id=args.id,
        voice=args.voice,
        mode="bibbia",
        output_json_only=args.json,
        solo_telegram=solo_tg
    ))

    print("\n" + "=" * 80)
    print("✅ BOT STORIE BIBLICHE: ESECUZIONE COMPLETATA CON SUCCESSO!")
    print("📲 Video recapitato con successo ed esclusivamente su Telegram.")
    print("⭐ Progetto e Personal Branding curati con passione da IMMOBILIARE GIANCANI ⭐")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
