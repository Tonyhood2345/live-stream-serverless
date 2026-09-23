#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connettività di Rete, Download Foto Immobile e Controllo Stato Live
"""

import os
import io
import re
import json
import uuid
import random
import urllib.request
import urllib.parse
import requests
from PIL import Image, ImageStat
from story_publisher.config import (
    GH_TOKEN, GH_REPO, CACHE_IMMOBILI_DIR,
    GUARANTEED_FALLBACK_IMAGES
)

def is_image_valid_and_not_black(image_obj, min_mean=20, min_max=40):
    """Verifica che l'immagine sia valida e non nera/vuota."""
    if not image_obj:
        return False
    try:
        gray = image_obj.convert('L').resize((60, 60))
        stat = ImageStat.Stat(gray)
        mean_b = stat.mean[0]
        ext_min, ext_max = gray.getextrema()
        if mean_b < min_mean or ext_max < min_max:
            print(f"[ANTI-BLACK] Immagine scartata: luminosità media {mean_b:.1f}, picco {ext_max}")
            return False
        return True
    except Exception as e:
        print(f"[ANTI-BLACK] Errore verifica immagine: {e}")
        return False

def normalizza_foto_url(url):
    """
    Normalizza qualsiasi link Google Drive / Docs / ID in URL CDN diretta lh3 ad altissima risoluzione.
    Supporta:
    - https://drive.google.com/file/d/{ID}/view
    - https://drive.google.com/open?id={ID}
    - https://drive.google.com/uc?id={ID}
    - {ID} puro da 25+ caratteri
    - URL diretti http/https già validi
    """
    if not url:
        return None
    url_str = str(url).strip()
    if "drive.google.com" in url_str or "docs.google.com" in url_str:
        m = re.search(r'[-\w]{25,}', url_str)
        if m:
            return f"https://lh3.googleusercontent.com/d/{m.group(0)}"
    elif re.match(r'^[-\w]{25,}$', url_str):
        return f"https://lh3.googleusercontent.com/d/{url_str}"
    elif "lh3.googleusercontent.com" in url_str:
        return url_str
    return url_str

def scarica_foto_url(url):
    """
    Scarica un'immagine autentica e in alta definizione dell'immobile assicurandosi che non sia corrotta o nera.
    Se il download primario fallisce, ricorre automaticamente alle foto in cache locale o al catalogo di riserva garantito.
    """
    url_norm = normalizza_foto_url(url)

    # 1. Tentativo di download diretto tramite URL normalizzato
    if url_norm and str(url_norm).startswith("http"):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            resp = requests.get(url_norm, headers=headers, verify=False, timeout=18)
            if resp.status_code == 200 and len(resp.content) > 3000:
                img = Image.open(io.BytesIO(resp.content)).convert('RGBA')
                if is_image_valid_and_not_black(img):
                    try:
                        cached_file = os.path.join(CACHE_IMMOBILI_DIR, f"cached_{uuid.uuid4().hex[:8]}.jpg")
                        img.convert('RGB').save(cached_file, "JPEG", quality=92)
                    except Exception:
                        pass
                    return img
        except Exception as eDl:
            print(f"Avviso scaricamento foto ({str(url_norm)[:60]}...): {eDl}")

    # 2. Controllo cache locale: foto autentiche precedentemente salvate
    if os.path.exists(CACHE_IMMOBILI_DIR):
        cache_files = [os.path.join(CACHE_IMMOBILI_DIR, f) for f in os.listdir(CACHE_IMMOBILI_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if cache_files:
            random.shuffle(cache_files)
            for cf in cache_files:
                try:
                    if os.path.getsize(cf) > 5000:
                        im_c = Image.open(cf).convert('RGBA')
                        if is_image_valid_and_not_black(im_c):
                            print(f"[CACHE LOCALE] Utilizzata foto autentica da archivio: {os.path.basename(cf)}")
                            return im_c
                except Exception:
                    pass

    # 3. Fallback di garanzia: immagini professionali ad alta definizione da catalogo di riserva
    for fb_url in GUARANTEED_FALLBACK_IMAGES:
        try:
            resp_fb = requests.get(fb_url, verify=False, timeout=12, headers={'User-Agent': 'Mozilla/5.0'})
            if resp_fb.status_code == 200 and len(resp_fb.content) > 3000:
                im_fb = Image.open(io.BytesIO(resp_fb.content)).convert('RGBA')
                if is_image_valid_and_not_black(im_fb):
                    return im_fb
        except Exception:
            continue

    return None

def check_is_live_active():
    """
    Verifica se la diretta live streaming continua (video/multistream) è attualmente in corso.
    Esclude rigorosamente i workflow di pubblicazione storie orarie / offline.
    """
    gh_workflow = os.environ.get("GITHUB_WORKFLOW", "").lower()
    if os.environ.get("GITHUB_ACTIONS") == "true":
        if ("offline" in gh_workflow or "storie" in gh_workflow or "story" in gh_workflow):
            # Se siamo dentro il runner del bot storie orarie, non siamo la diretta streaming
            return False, None
        if "live" in gh_workflow or "stream" in gh_workflow or "multistream" in gh_workflow:
            return True, "local_github_runner"

    try:
        headers = {
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Giancani-StoriesBot"
        }
        url = f"https://api.github.com/repos/{GH_REPO}/actions/runs?status=in_progress"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for run in data.get('workflow_runs', []):
                path = run.get('path', '').lower()
                name = run.get('name', '').lower()
                # Considera solo i veri flussi di diretta streaming video continua
                if ('storie' in path or 'offline' in path or 'storie' in name or 'offline' in name):
                    continue
                if 'live-stream' in path or 'multistream' in name or 'diretta' in name or 'stream' in name:
                    return True, run.get('id')
    except Exception as e:
        print(f"Avviso verifica status live su GitHub: {e}")
    return False, None
