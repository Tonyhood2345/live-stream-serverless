#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motore di Rendering Video FFmpeg
Assembla la storia video verticale a 1080x1920 @ 30fps con animazione Ken Burns,
audio mix dinamico (ducking) e volantino 1:1 promozionale coordinato.
"""

import os
import time
import uuid
import random
import subprocess

from story_publisher.config import SCRATCH_DIR
from story_publisher.system.env import find_ffmpeg, find_ytdlp
from story_publisher.core.compliance import normalize_mq
from story_publisher.audio.copywriter import determina_fascia_oraria, FRASI_POSITIVE_FLASH
from story_publisher.audio.mixer import crea_audio_mix_completo
from story_publisher.graphics.templates.splitscreen import crea_grafica_flyer_split_screen, crea_story_splitscreen_9_16
from story_publisher.graphics.templates.luxury_glass import crea_grafica_luxury_glass, crea_story_luxury_glass_9_16
from story_publisher.graphics.templates.editorial import crea_grafica_editorial, crea_story_editorial_9_16

def genera_video_da_clip_o_foto(media_info, output_video_path=None, style="auto"):
    """
    Costruisce il video di 15 secondi (1080x1920) e il volantino promozionale 1:1,
    facendo ruotare ad ogni ciclo da 30 minuti diverse grafiche (Split-Screen Flyer, Luxury Glass, Editorial Showcase).
    Garantisce narrazione vocale espressiva (DarIA/DarIO) e musica allegra (124 BPM) royalty-free.
    """
    if not output_video_path:
        output_video_path = os.path.join(SCRATCH_DIR, f"story_video_{uuid.uuid4().hex[:8]}.mp4")

    ffmpeg_bin = find_ffmpeg()
    ytdlp_bin = find_ytdlp()

    video_url = media_info.get('videoUrl')
    foto_url = media_info.get('fotoUrl')
    titolo = media_info.get('titolo', 'Immobile di Prestigio')
    prezzo = media_info.get('prezzo', 'Trattativa Riservata')
    mq = normalize_mq(media_info.get('mq', '120'))
    testo_f = media_info.get('testoF', 'Immobile esclusivo selezionato ad Agrigento e Favara.')
    is_live = media_info.get('isLive', False)

    # Caricamento del Motore Grafico Unificato e del Tema Giornaliero se disponibile
    mgs = None
    palette_giorno = None
    try:
        import motore_grafica_storie as mgs
        palette_giorno = mgs.get_palette_del_giorno()
        print(f"🗓️ TEMA GIORNALIERO ATTIVO ({palette_giorno.get('giorno')}): {palette_giorno.get('nome')} [ID: {palette_giorno.get('id')}]")
    except Exception as eImportMgs:
        print(f"Avviso importazione motore_grafica_storie: {eImportMgs}")

    # 10 stili professionali contestualizzati al tema del giorno
    styles = [
        "gabetti_diagonal", "capellupo_sidebar", "marketing_banner", "split_screen",
        "luxury_glass", "editorial", "room_label", "ideacasa_layout", "casait_card", "tecnocasa_multi"
    ]
    if not style or style == "auto":
        slot_stile = int(time.time() / 1800)
        chosen_style = styles[slot_stile % len(styles)]
    else:
        chosen_style = style.strip().lower()
        if chosen_style not in styles:
            chosen_style = "gabetti_diagonal"

    giorno_label = palette_giorno.get('giorno', 'Oggi') if palette_giorno else 'Standard'
    palette_nome = palette_giorno.get('nome', 'Default') if palette_giorno else 'Default'
    print(f"🎨 Stile Grafico selezionato: {chosen_style.upper()} | Tema del Giorno ({giorno_label}): {palette_nome}")

    # 1. Genera overlay video 9:16 tramite il Motore Grafico Unificato con la palette del giorno
    overlay_png_path = None
    if mgs:
        try:
            overlay_png_path = mgs.crea_story_9_16(media_info, style=chosen_style, palette=palette_giorno)
        except Exception as eMgsGen:
            print(f"Avviso render 9:16 mgs ({chosen_style}): {eMgsGen}")

    if not overlay_png_path or not os.path.exists(overlay_png_path):
        if chosen_style == "luxury_glass":
            overlay_png_path = crea_story_luxury_glass_9_16(media_info)
        elif chosen_style == "editorial":
            overlay_png_path = crea_story_editorial_9_16(media_info)
        else:
            overlay_png_path = crea_story_splitscreen_9_16(media_info)

    # Genera e salva anche il volantino promozionale 1:1 coordinato con il tema del giorno
    flyer_1x1_path = os.path.join(SCRATCH_DIR, f"flyer_giancani_1x1_{uuid.uuid4().hex[:6]}.png")
    if mgs:
        try:
            if chosen_style == "gabetti_diagonal":
                mgs.crea_flyer_gabetti_diagonal_1_1(media_info, palette=palette_giorno, output_path=flyer_1x1_path)
            elif chosen_style == "capellupo_sidebar":
                mgs.crea_flyer_capellupo_sidebar_1_1(media_info, palette=palette_giorno, output_path=flyer_1x1_path)
            elif chosen_style == "luxury_glass":
                crea_grafica_luxury_glass(media_info, flyer_1x1_path, size=(1080, 1080))
            elif chosen_style == "editorial":
                crea_grafica_editorial(media_info, flyer_1x1_path, size=(1080, 1080))
            else:
                crea_grafica_flyer_split_screen(media_info, flyer_1x1_path, size=(1080, 1080))
        except Exception as e_fl:
            print(f"Avviso generazione flyer 1:1: {e_fl}")
            crea_grafica_flyer_split_screen(media_info, flyer_1x1_path, size=(1080, 1080))
    else:
        crea_grafica_flyer_split_screen(media_info, flyer_1x1_path, size=(1080, 1080))

    # 2. Determina fascia oraria se offline
    fascia_info = determina_fascia_oraria() if not is_live else None

    # 3. Traccia audio con DarIA/DarIO + musica allegra (124 BPM)
    frase_positiva_flash = fascia_info["frase_flash"] if (not is_live and fascia_info) else random.choice(FRASI_POSITIVE_FLASH)
    audio_path = crea_audio_mix_completo(testo_f, is_live=is_live, frase_positiva=frase_positiva_flash, fascia_info=fascia_info)

    # 4. Rendering Video 1080x1920 con FFmpeg (15 secondi continui)
    cmd_render = [
        ffmpeg_bin, "-y",
        "-loop", "1", "-i", overlay_png_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "15",
        output_video_path
    ]

    proc_render = subprocess.run(cmd_render, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    if proc_render.returncode == 0 and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 100000:
        print(f"[OK] Video Storia 15s ({chosen_style}) generato: {output_video_path}")
        return output_video_path
    return None
