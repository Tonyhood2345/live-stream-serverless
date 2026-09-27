#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BOT REELS 9:16 — MITOLOGIA GRECA («MITI DELL'ANTICA GRECIA», ORE 11:00)
================================================================================
- Tema: Miti e Leggende degli Eroi dell'Antica Grecia (Perseo, Icaro, ecc.)
- Stile Visivo: Cartone Animato 2D Cel Art con eroi e creature mitologiche, NO GATTO
- Voce Neurale: it-IT-DiegoNeural (Maschile epico, narrativo e teatrale)
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
        description="Bot Reels 9:16 — Mitologia Greca — Invio Esclusivo Telegram"
    )
    parser.add_argument("--id", type=str, default=None, help="ID del mito greco (es. 1 per Perseo e Medusa, 2 per Dedalo e Icaro)")
    parser.add_argument("--voice", type=str, default="it-IT-DiegoNeural", help="Voce Edge-TTS (default: it-IT-DiegoNeural)")
    parser.add_argument("--json", action="store_true", help="Stampa solo lo schema JSON senza montare il video")
    parser.add_argument("--anche-social", action="store_true", help="Se abilitato pubblica anche sui social (default: SOLO TELEGRAM)")
    args = parser.parse_args()

    print("=" * 80)
    print("🏛️ AVVIO BOT DEDICATO: MITOLOGIA GRECA («MITI DELL'ANTICA GRECIA»)")
    print("⚔️ Formato: Racconto Epico Culturale in 2 Minuti | Layout Verticale 9:16")
    print("🎨 Stile: 3D Pixar / Disney Animation (Stile Immagine di Riferimento Utente)")
    print("🛡️ Destinazione attiva: SOLO ED ESCLUSIVAMENTE TELEGRAM")
    print("⭐ Rubrica Culturale offerta da: IMMOBILIARE GIANCANI")
    print("=" * 80)

    # Esecuzione pipeline in modalità mitologia con invio esclusivo su Telegram
    solo_tg = not args.anche_social
    asyncio.run(esegui_pipeline(
        story_id=args.id,
        voice=args.voice,
        mode="mitologia",
        output_json_only=args.json,
        solo_telegram=solo_tg
    ))

    print("\n" + "=" * 80)
    print("✅ BOT MITOLOGIA GRECA: ESECUZIONE COMPLETATA CON SUCCESSO!")
    print("📲 Video recapitato con successo ed esclusivamente su Telegram.")
    print("⭐ Progetto e Personal Branding curati con passione da IMMOBILIARE GIANCANI ⭐")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
