#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestione Cronologia e Deduplicazione Storie Social
"""

import os
import json
from story_publisher.config import SCRIPTS_DIR, BASE_PROJECT_DIR, ASSETS_DIR

ROOT_HISTORY_PATH = os.path.join(BASE_PROJECT_DIR, "immobili_pubblicati_history.json")
LOCAL_HISTORY_PATH = os.path.join(SCRIPTS_DIR, "immobili_pubblicati_history.json")
CRONOLOGIA_STORIE_PATH = os.path.join(ASSETS_DIR, "cronologia_storie_offline.json")
ROOT_ASSETS_CRONOLOGIA = os.path.join(BASE_PROJECT_DIR, "assets", "cronologia_storie_offline.json")

ALL_HISTORY_PATHS = [
    ROOT_HISTORY_PATH,
    LOCAL_HISTORY_PATH,
    CRONOLOGIA_STORIE_PATH,
    ROOT_ASSETS_CRONOLOGIA
]

def carica_cronologia_storie():
    """Carica la cronologia di pubblicazione per evitare duplicati recenti."""
    for p in ALL_HISTORY_PATHS:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and len(data) > 0:
                        return data
            except Exception:
                pass
    return {}

def salva_cronologia_storie(cronologia):
    """Salva la cronologia di pubblicazione aggiornata in tutti i percorsi previsti."""
    for p in ALL_HISTORY_PATHS:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(cronologia, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Avviso salvataggio cronologia storie su {p}: {e}")

def get_recent_photo_urls(cronologia):
    """Restituisce l'insieme degli URL delle foto già pubblicate nello storico."""
    urls = set()
    if not isinstance(cronologia, dict):
        return urls
    for k, v in cronologia.items():
        if isinstance(v, dict):
            u = v.get("fotoUrl") or v.get("mediaUrl")
            if u:
                urls.add(str(u).strip())
        elif isinstance(v, str) and v.startswith("http"):
            urls.add(v.strip())
    return urls

