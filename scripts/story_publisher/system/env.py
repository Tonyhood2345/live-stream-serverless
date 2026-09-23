#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rilevamento Binari di Sistema (FFmpeg, yt-dlp), Font e Ambiente SSL
"""

import os
import ssl
import shutil
from PIL import ImageFont
from story_publisher.config import SCRIPTS_DIR, BASE_PROJECT_DIR

# Configurazione SSL globale non verificata per ambienti cloud / proxy
ssl._create_default_https_context = ssl._create_unverified_context
orig_create_default_context = ssl.create_default_context

def unverified_create_default_context(*args, **kwargs):
    c = orig_create_default_context(*args, **kwargs)
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c

ssl.create_default_context = unverified_create_default_context

def find_ffmpeg():
    """Localizza l'eseguibile FFmpeg nel workspace o nel sistema."""
    candidates = [
        shutil.which("ffmpeg"),
        os.path.join(BASE_PROJECT_DIR, "ffmpeg.exe"),
        os.path.join(SCRIPTS_DIR, "ffmpeg.exe"),
        "ffmpeg"
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return "ffmpeg"

def find_ytdlp():
    """Localizza l'eseguibile yt-dlp."""
    candidates = [
        shutil.which("yt-dlp"),
        "yt-dlp"
    ]
    for c in candidates:
        if c and (os.path.exists(c) or shutil.which(c)):
            return c
    return "yt-dlp"

def get_font(size, bold=False, font_type="sans"):
    """Carica font TrueType scalato e tipizzato per Windows e Linux (GitHub Actions)."""
    paths = []
    if font_type == "serif":
        paths = [
            "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/timesbd.ttf" if bold else "C:/Windows/Fonts/times.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
        ]
    elif font_type == "script":
        paths = [
            "C:/Windows/Fonts/segoescb.ttf" if bold else "C:/Windows/Fonts/segoesc.ttf",
            "C:/Windows/Fonts/brushsci.ttf",
            "C:/Windows/Fonts/georgiaz.ttf" if bold else "C:/Windows/Fonts/georgiai.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"
        ]
    else:  # sans
        paths = [
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]

    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()
