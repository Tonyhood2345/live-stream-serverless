#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaccia a Riga di Comando (CLI) per Story Publisher
"""

import time
import argparse
from story_publisher.config import PAGES
from story_publisher.system.network import check_is_live_active
from story_publisher.audio.copywriter import determina_fascia_oraria
from story_publisher.publishers.facebook import pubblica_nota_facebook_pagina
from story_publisher.orchestrator.live_runner import esegui_ciclo_live
from story_publisher.orchestrator.offline_runner import esegui_ciclo_offline

def main():
    parser = argparse.ArgumentParser(description="Gestore Storie Social Immobiliare Giancani")
    parser.add_argument("--mode", choices=["live", "offline", "nota"], default="live", help="Modalità operativa: live (durante la diretta), offline (ogni ora), o nota (pubblica nota facebook del giorno)")
    parser.add_argument("--offline", action="store_true", help="Scorciatoia diretta per eseguire in modalità offline (storie orarie)")
    parser.add_argument("--fascia", choices=["mattina", "pomeriggio", "sera", "notte", "auto"], default="auto", help="Forza la fascia oraria per saluto ed emoticon")
    parser.add_argument("--loop", action="store_true", help="Esegue in ciclo continuo (per la diretta live ogni 30 minuti (1800s))")
    parser.add_argument("--style", default="auto", help="Stile grafico per la storia (default: auto)")
    parser.add_argument("--interval", type=int, default=1800, help="Intervallo in secondi per la modalità loop (default: 1800s = 30 minuti)")

    # Parametri per selezione mirata o storie non immobiliari
    parser.add_argument("--sheet", "--immobile", dest="sheet", default=None, help="Filtra per immobile o nome foglio specifico")
    parser.add_argument("--stanza", "--room", dest="room", default=None, help="Filtra per stanza o indice riga specifico")
    parser.add_argument("--custom_text", dest="custom_text", default=None, help="Testo personalizzato per storie non immobiliari o comunicazioni")
    parser.add_argument("--custom_image", dest="custom_image", default=None, help="URL o percorso immagine personalizzata")
    parser.add_argument("--custom_title", dest="custom_title", default=None, help="Titolo personalizzato per la storia")
    args = parser.parse_args()

    if args.offline:
        args.mode = "offline"

    if args.mode == "live":
        if args.loop:
            print(f"Avvio demone storie Facebook in diretta ogni {args.interval} secondi ({args.interval // 60} minuti)...")
            time.sleep(15)
            while True:
                try:
                    is_live, run_id = check_is_live_active()
                    if is_live:
                        esegui_ciclo_live(style=getattr(args, 'style', 'auto'))
                    else:
                        print(f"🔴 Diretta live non attiva. Controllo programmato tra {args.interval // 60} minuti... — Immobiliare Giancani")
                except Exception as eL:
                    print(f"Errore ciclo live: {eL}")
                time.sleep(args.interval)
        else:
            esegui_ciclo_live(style=getattr(args, 'style', 'auto'))
    elif args.mode == "offline":
        esegui_ciclo_offline(
            style=getattr(args, 'style', 'auto'),
            sheet_filter=getattr(args, 'sheet', None),
            room_filter=getattr(args, 'room', None),
            custom_text=getattr(args, 'custom_text', None),
            custom_image=getattr(args, 'custom_image', None),
            custom_title=getattr(args, 'custom_title', None)
        )
    elif args.mode == "nota":
        fascia_scelta = None
        if getattr(args, 'fascia', 'auto') != 'auto':
            h_map = {'mattina': 8, 'pomeriggio': 14, 'sera': 20, 'notte': 23}
            fascia_scelta = determina_fascia_oraria(h_map.get(args.fascia, 12))
        else:
            fascia_scelta = determina_fascia_oraria()
        print(f"📝 Pubblicazione Nota Facebook forzata: {fascia_scelta['saluto']}")
        dummy_info = {
            "titolo": "Villa Panoramica Favara",
            "prezzo": "Trattativa Riservata",
            "mq": "140 metri quadri",
            "testoF": "Elegante residenza con ampi spazi esterni e rifiniture di pregio curata in esclusiva per voi. — Immobiliare Giancani"
        }
        for target in PAGES:
            pubblica_nota_facebook_pagina(target['id'], target['token'], dummy_info, fascia_scelta)

if __name__ == "__main__":
    main()
