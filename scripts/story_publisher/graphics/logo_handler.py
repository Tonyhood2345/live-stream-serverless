#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestione e Sanificazione Logo Ufficiale Immobiliare Giancani
Rimozione sfondi spuri, mantenimento proporzioni ('non pressato') e mascheratura alpha
"""

import os
import io
import urllib.request
import numpy as np
from PIL import Image
from story_publisher.config import ASSETS_DIR, REMOTE_LOGO_URL
from story_publisher.system.env import unverified_create_default_context

def get_local_or_remote_logo():
    """Restituisce l'immagine del logo ufficiale Immobiliare Giancani."""
    local_logo_path = os.path.join(ASSETS_DIR, "logo_giancani.png")
    if os.path.exists(local_logo_path) and os.path.getsize(local_logo_path) > 1000:
        try:
            return Image.open(local_logo_path).convert('RGBA')
        except Exception:
            pass
    try:
        ctx = unverified_create_default_context()
        req = urllib.request.Request(REMOTE_LOGO_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = resp.read()
            with open(local_logo_path, 'wb') as f:
                f.write(data)
            return Image.open(io.BytesIO(data)).convert('RGBA')
    except Exception as e:
        print(f"Avviso: recupero logo remoto fallito ({e})")
    return None

def get_clean_logo(max_w=380, max_h=110, transparent=True):
    """
    Restituisce il logo ufficiale Immobiliare Giancani proporzionato,
    senza schiacciamenti ('non pressato') e con sfondo bianco rimosso (trasparente).
    """
    raw = get_local_or_remote_logo()
    if not raw:
        return None
    try:
        im = raw.convert('RGBA')
        if transparent:
            arr = np.array(im)
            r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            white_mask = (r > 230) & (g > 230) & (b > 230)
            arr[white_mask, 3] = 0
            im = Image.fromarray(arr)

        orig_w, orig_h = im.size
        scale = min(max_w / orig_w, max_h / orig_h)
        new_w = max(1, int(orig_w * scale))
        new_h = max(1, int(orig_h * scale))
        return im.resize((new_w, new_h), Image.LANCZOS)
    except Exception as e:
        print(f"Avviso elaborazione logo pulito: {e}")
        return raw
