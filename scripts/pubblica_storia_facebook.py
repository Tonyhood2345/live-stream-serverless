#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
IMMOBILIARE GIANCANI — GESTORE STORIE SOCIAL FACEBOOK (CLOUD & GITHUB ACTIONS)
MODALITÀ LIVE (OGNI 30 MIN IN DIRETTA) & MODALITÀ OFFLINE (OGNI ORA VIDEO/POST)
═══════════════════════════════════════════════════════════════════════════════
Architettura Modulare v2.0:
Questo file funge da Facade ed Entry Point retrocompatibile per l'intero
package modulare 'story_publisher', preservando la compatibilità completa con:
- GitHub Actions CI/CD workflows ('remote_live_stream.yml', cron orario)
- Trigger automatizzati ogni 30 minuti durante la diretta streaming
- Script batch locali e comandi CLI

Tutti i moduli interni sono disaccoppiati in 'story_publisher/':
- config.py: credenziali, costanti, token
- core/: conformità Colonna F, normalizzazione metri quadri, personal branding
- system/: rilevamento binari (FFmpeg/yt-dlp), font e connessioni
- audio/: Edge-TTS neurale, copywriter e ducking audio
- graphics/: primitive vettoriali, logo sanificato e template (Split-Screen, Luxury, Editorial)
- video/: compositing video 1080x1920 con animazione Ken Burns
- publishers/: connettori per Facebook, Instagram, YouTube Shorts, TikTok e Telegram
- orchestrator/: runner live e offline

— Immobiliare Giancani
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys

# Assicura che la directory degli script sia nel sys.path
_this_dir = os.path.dirname(os.path.abspath(__file__))
for _p in [_this_dir, os.path.dirname(_this_dir)]:
    if _p not in sys.path and os.path.exists(_p):
        sys.path.insert(0, _p)

# Importazione di tutte le componenti dal package modulare story_publisher
from story_publisher import (
    PAGES,
    IG_ACCOUNT_ID,
    YT_CHANNEL_HANDLE,
    APPS_SCRIPT_URL,
    REMOTE_LOGO_URL,
    BRAND_NAME,
    BRAND_CLAIM,
    normalize_mq,
    format_personal_branding,
    get_testo_colonna_f,
    carica_cronologia_storie,
    salva_cronologia_storie,
    find_ffmpeg,
    find_ytdlp,
    get_font,
    normalizza_foto_url,
    scarica_foto_url,
    check_is_live_active,
    genera_voce_tts,
    determina_fascia_oraria,
    genera_intro_invito_dinamico,
    genera_audio_musica_allegra,
    crea_audio_mix_completo,
    draw_skyline,
    draw_circular_badge,
    calcola_prezzo_barrato,
    is_image_valid_and_not_black,
    get_local_or_remote_logo,
    get_clean_logo,
    genera_video_da_clip_o_foto,
    pubblica_storia_video_su_facebook,
    pubblica_nota_facebook_pagina,
    pubblica_storia_instagram,
    pubblica_short_youtube,
    pubblica_storia_tiktok,
    invia_notifica_telegram,
    esegui_ciclo_live,
    esegui_ciclo_offline,
    main
)

from story_publisher.graphics.templates.splitscreen import crea_grafica_flyer_split_screen, crea_story_splitscreen_9_16
from story_publisher.graphics.templates.luxury_glass import crea_grafica_luxury_glass, crea_story_luxury_glass_9_16
from story_publisher.graphics.templates.editorial import crea_grafica_editorial, crea_story_editorial_9_16

if __name__ == "__main__":
    main()
