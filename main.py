#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  🎬 MAIN PIPELINE ENTRYPOINT -> bot_reels_master.py
  Direzione Tecnica, Regia & Personal Branding: IMMOBILIARE GIANCANI
==============================================================================
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from bot_reels_master import *

if __name__ == "__main__":
    import asyncio
    import argparse
    import datetime

    parser = argparse.ArgumentParser(description="Bot Reels Master — Pipeline Video 9:16 Multi-Canale")
    parser.add_argument("--mode", type=str, default=None, choices=["standard", "bibbia", "pillole", "mitologia"], help="Modalità bot")
    parser.add_argument("--id", type=str, default=None, help="ID specifico della storia o pillola da generare")
    parser.add_argument("--voice", type=str, default=None, help="Voce personalizzata")
    parser.add_argument("--json", action="store_true", help="Genera solo lo schema JSON")
    parser.add_argument("--solo-telegram", action="store_true", help="Invia solo ed esclusivamente su Telegram")
    args = parser.parse_args()

    mode_effettivo = args.mode
    if not mode_effettivo:
        ora_utc = datetime.datetime.now(datetime.timezone.utc).hour
        # Schedule cron:
        # 04:00 UTC (ore 06:00 Roma) -> pillole
        # 16:00 UTC (ore 18:00 Roma) -> mitologia
        # 18:00 UTC (ore 20:00 Roma) -> bibbia
        if 2 <= ora_utc < 10:
            mode_effettivo = "pillole"
        elif 10 <= ora_utc < 17:
            mode_effettivo = "mitologia"
        else:
            mode_effettivo = "bibbia"

    asyncio.run(esegui_pipeline(story_id=args.id, voice=args.voice, mode=mode_effettivo, output_json_only=args.json, solo_telegram=args.solo_telegram))
