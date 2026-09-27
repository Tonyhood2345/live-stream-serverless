#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BOT REELS 9:16 — PILLOLE IMMOBILIARI & LEGALI QUOTIDIANE (ORE 06:00)
================================================================================
- Tema: Consulenza immobiliare, tecnica e legale per vendere o acquistare casa
- Stile Visivo: Corporate elegante, grafiche informative chiare, NO GATTO
- Voce Neurale: it-IT-IsabellaNeural (Chiara, autorevole, professionale)
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
        description="Bot Reels 9:16 — Pillole Immobiliari & Legali (Ore 06:00) — Invio Esclusivo Telegram"
    )
    parser.add_argument("--id", type=str, default=None, help="ID della pillola immobiliare (es. 1 per Rogito Notarile, 2 per Conformità Urbanistica)")
    parser.add_argument("--voice", type=str, default="it-IT-IsabellaNeural", help="Voce Edge-TTS (default: it-IT-IsabellaNeural)")
    parser.add_argument("--json", action="store_true", help="Stampa solo lo schema JSON senza montare il video")
    parser.add_argument("--anche-social", action="store_true", help="Se abilitato pubblica anche sui social (default: SOLO TELEGRAM)")
    args = parser.parse_args()

    print("=" * 80)
    print("🏢 AVVIO BOT DEDICATO: PILLOLE IMMOBILIARI & LEGALI (ORE 06:00)")
    print("📋 Formato: Consulenza Esperta in 2 Minuti | Layout Verticale 9:16")
    print("🛡️ Destinazione attiva: SOLO ED ESCLUSIVAMENTE TELEGRAM")
    print("⭐ Produzione e Personal Branding: IMMOBILIARE GIANCANI")
    print("=" * 80)

    # Esecuzione pipeline in modalità pillole con invio esclusivo su Telegram
    solo_tg = not args.anche_social
    asyncio.run(esegui_pipeline(
        story_id=args.id,
        voice=args.voice,
        mode="pillole",
        output_json_only=args.json,
        solo_telegram=solo_tg
    ))

    print("\n" + "=" * 80)
    print("✅ BOT PILLOLE IMMOBILIARI: ESECUZIONE COMPLETATA CON SUCCESSO!")
    print("📲 Video recapitato con successo ed esclusivamente su Telegram.")
    print("⭐ Progetto e Personal Branding curati con passione da IMMOBILIARE GIANCANI ⭐")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
