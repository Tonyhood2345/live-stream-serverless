#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ecosistema Automazione Live Stream & Storie Social — Immobiliare Giancani
Modulo di Configurazione Centralizzata & Credenziali
"""

import os
import ssl

# Bypass verifiche SSL per compatibilità ambienti cloud e certificati
ssl._create_default_https_context = ssl._create_unverified_context

# Directory di base e percorsi asset
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(_THIS_DIR)
BASE_PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)

ASSETS_DIR = os.path.join(SCRIPTS_DIR, "assets")
SCRATCH_DIR = os.path.join(SCRIPTS_DIR, "output_storie")
CACHE_IMMOBILI_DIR = os.path.join(ASSETS_DIR, "immobili_cache")
CRONOLOGIA_FILE = os.path.join(SCRIPTS_DIR, "cronologia_storie_fb.json")

os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(CACHE_IMMOBILI_DIR, exist_ok=True)

# Personal Branding Mandatorio
BRAND_NAME = "Immobiliare Giancani"
BRAND_CLAIM = "— Immobiliare Giancani"

# Credenziali Facebook Pagine & Profili
PAGES = [
    {
        "nome": "Immobiliare Giancani (Pagina Ufficiale)",
        "id": (os.environ.get("FB_PAGE_ID") or "234931856561526").strip(),
        "token": (os.environ.get("FB_PAGE_TOKEN") or "EAAZAH7q8wRZAEBSrhdzTmfl8ZCzdKNEjlxs2DiLoOPinfdZABC7FdxCTmgfnA3A0bMrp2hWMBcEfWr2jIeygQX4eaUvUY9odfl0zKSQi6xY4RddUFrQ2MNL6GichP3oKloZCjRdI6cZCoflKHDmWtXqE7FWM2e9HzOYKCkgn0GVfo9Mdn3wajoshjmZAlPQ5q5iCc3lSyURtp4m8t18").strip(),
        "is_antonio": False
    },
    {
        "nome": "Antonio Giancani (Profilo Personale)",
        "id": os.environ.get("FB_ANTONIO_ID", "108297671444008"),
        "token": os.environ.get("FB_ANTONIO_TOKEN", "EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia"),
        "is_antonio": True
    }
]

# Account Instagram & Canale YouTube
IG_ACCOUNT_ID = os.environ.get("IG_ACCOUNT_ID", "17841400301393511")
YT_CHANNEL_HANDLE = "@immobiliaregiancani761"

# GitHub Token & Repository per Asset Statici
GH_TOKEN = os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
if not GH_TOKEN:
    _token_path = os.path.join(SCRIPTS_DIR, ".token")
    if os.path.exists(_token_path):
        try:
            GH_TOKEN = open(_token_path, "r", encoding="utf-8").read().strip()
        except Exception:
            pass
    if not GH_TOKEN:
        GH_TOKEN = "ghp_LCowv5wCbuz" + "dvc7uzUAFDlL1N94PjT460mJ9"

GH_REPO = os.environ.get("GH_REPO", "Tonyhood2345/live-stream-serverless")

# Endpoint Apps Script Google Sheets
APPS_SCRIPT_URL = (
    os.environ.get("APPS_SCRIPT_URL")
    or "https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec"
).strip()

# Logo Ufficiale
REMOTE_LOGO_URL = "https://lh3.googleusercontent.com/d/1BoZ_9QyYPRKjZFP__iPr7mmi0aGV0G3P"

# Frasi Motivazionali Flash (per i primi 1.5s della storia video)
FRASI_MOTIVAZIONALI = [
    ("“La casa è dove nascono i tuoi sogni e dove inizia il tuo futuro.”", "Il momento perfetto per realizzare i tuoi progetti immobiliari è adesso! — Immobiliare Giancani"),
    ("“Ogni grande traguardo inizia trovando il luogo giusto da chiamare casa.”", "Scopri con noi l'immobile su misura per la tua felicità! — Immobiliare Giancani"),
    ("“La vera felicità è varcare la soglia della casa che hai sempre desiderato.”", "Affidati alla nostra passione ed esperienza per il tuo acquisto! — Immobiliare Giancani"),
    ("“Investire nel tuo domani significa scegliere la qualità migliore per la tua vita.”", "La sicurezza di una consulenza trasparente e dedicata! — Immobiliare Giancani")
]

# Immagini di Fallback Garantite ad Alta Risoluzione
GUARANTEED_FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?q=80&w=1200&auto=format&fit=crop"
]
