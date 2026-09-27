#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BOT REELS 9:16 — GRANDI CLASSICI DELLA LETTERATURA (CON GATTO NARRATORE)
================================================================================
- Tema: I Più Grandi Capolavori della Letteratura Mondiale (Riassunto 2 Minuti)
- Personaggio Core: Gatto Ginger con t-shirt a righe marinaio bianche e blu
- Stile Visivo: Antique Storybook Illustration (Incisione botanica vintage, acquerello, inchiostro fine)
- Voce Neurale: it-IT-ElsaNeural (Dolce, fiabesca e coinvolgente)
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
        description="Bot Reels 9:16 — Grandi Classici della Letteratura — Invio Esclusivo Telegram"
    )
    parser.add_argument("--id", type=str, default=None, help="ID del libro classico (es. 1 per Il Piccolo Principe)")
    parser.add_argument("--voice", type=str, default="it-IT-ElsaNeural", help="Voce Edge-TTS (default: it-IT-ElsaNeural)")
    parser.add_argument("--json", action="store_true", help="Stampa solo lo schema JSON senza montare il video")
    parser.add_argument("--anche-social", action="store_true", help="Se abilitato pubblica anche sui social (default: SOLO TELEGRAM)")
    args = parser.parse_args()

    print("=" * 80)
    print("🐱 AVVIO BOT DEDICATO: GRANDI CLASSICI DELLA LETTERATURA")
    print("📚 Formato: Riassunto Completo in 2 Minuti | Layout 9:16")
    print("🎨 Stile: Antique Storybook Illustration (Protagonista: Gatto con t-shirt a righe)")
    print("🛡️ Destinazione attiva: SOLO ED ESCLUSIVAMENTE TELEGRAM")
    print("⭐ Produzione e Personal Branding: IMMOBILIARE GIANCANI")
    print("=" * 80)

    # Esecuzione pipeline in modalità standard (classici) con invio esclusivo su Telegram
    solo_tg = not args.anche_social
    asyncio.run(esegui_pipeline(
        story_id=args.id,
        voice=args.voice,
        mode="standard",
        output_json_only=args.json,
        solo_telegram=solo_tg
    ))

    print("\n" + "=" * 80)
    print("✅ BOT GRANDI CLASSICI: ESECUZIONE COMPLETATA CON SUCCESSO!")
    print("📲 Video recapitato con successo ed esclusivamente su Telegram.")
    print("⭐ Progetto e Personal Branding curati con passione da IMMOBILIARE GIANCANI ⭐")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
