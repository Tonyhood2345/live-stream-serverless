#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ecosistema Automazione Live Stream & Storie Social — Immobiliare Giancani
Package Story Publisher Modulare
"""

__version__ = "2.0.0"
__author__ = "Immobiliare Giancani"

from .config import (
    PAGES, IG_ACCOUNT_ID, YT_CHANNEL_HANDLE, APPS_SCRIPT_URL,
    REMOTE_LOGO_URL, BRAND_NAME, BRAND_CLAIM
)
from .core.compliance import normalize_mq, format_personal_branding, get_testo_colonna_f
from .core.history import carica_cronologia_storie, salva_cronologia_storie
from .system.env import find_ffmpeg, find_ytdlp, get_font
from .system.network import normalizza_foto_url, scarica_foto_url, check_is_live_active
from .audio.voice_tts import genera_voce_tts
from .audio.copywriter import determina_fascia_oraria, genera_intro_invito_dinamico
from .audio.mixer import genera_audio_musica_allegra, crea_audio_mix_completo
from .graphics.primitives import draw_skyline, draw_circular_badge, calcola_prezzo_barrato, is_image_valid_and_not_black
from .graphics.logo_handler import get_local_or_remote_logo, get_clean_logo
from .video.video_engine import genera_video_da_clip_o_foto
from .publishers.facebook import pubblica_storia_video_su_facebook, pubblica_nota_facebook_pagina
from .publishers.instagram import pubblica_storia_instagram
from .publishers.youtube import pubblica_short_youtube
from .publishers.tiktok import pubblica_storia_tiktok
from .publishers.telegram import invia_notifica_telegram
from .orchestrator.live_runner import esegui_ciclo_live
from .orchestrator.offline_runner import esegui_ciclo_offline
from .cli import main

__all__ = [
    "PAGES",
    "IG_ACCOUNT_ID",
    "YT_CHANNEL_HANDLE",
    "APPS_SCRIPT_URL",
    "REMOTE_LOGO_URL",
    "BRAND_NAME",
    "BRAND_CLAIM",
    "normalize_mq",
    "format_personal_branding",
    "get_testo_colonna_f",
    "carica_cronologia_storie",
    "salva_cronologia_storie",
    "find_ffmpeg",
    "find_ytdlp",
    "get_font",
    "normalizza_foto_url",
    "scarica_foto_url",
    "check_is_live_active",
    "genera_voce_tts",
    "determina_fascia_oraria",
    "genera_intro_invito_dinamico",
    "genera_audio_musica_allegra",
    "crea_audio_mix_completo",
    "draw_skyline",
    "draw_circular_badge",
    "calcola_prezzo_barrato",
    "is_image_valid_and_not_black",
    "get_local_or_remote_logo",
    "get_clean_logo",
    "genera_video_da_clip_o_foto",
    "pubblica_storia_video_su_facebook",
    "pubblica_nota_facebook_pagina",
    "pubblica_storia_instagram",
    "pubblica_short_youtube",
    "pubblica_storia_tiktok",
    "invia_notifica_telegram",
    "esegui_ciclo_live",
    "esegui_ciclo_offline",
    "main"
]
