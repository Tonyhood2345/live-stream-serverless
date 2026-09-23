#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regole Fondamentali di Business & Personal Branding
1. Testi prelevati rigorosamente dalla Colonna F
2. Superfici espresse sempre per esteso in 'metri quadri'
3. Personal branding obbligatorio con chiusura '— Immobiliare Giancani'
"""

import re
from story_publisher.config import BRAND_CLAIM

def normalize_mq(val):
    """
    Garantisce la dicitura 'metri quadri' per le superfici come da regola globale.
    Nessuna abbreviazione come 'mq', 'mq.', 'm²' o 'MQ' è consentita.
    """
    if not val:
        return "120 metri quadri"
    val = str(val).strip()
    val = re.sub(r'(?i)\bmq\.?|\bm²', 'metri quadri', val)
    if "metri quadri" not in val.lower():
        val = f"{val} metri quadri"
    # Pulisce doppi spazi
    val = re.sub(r'\s+', ' ', val).strip()
    return val

def format_personal_branding(testo):
    """
    Assicura che ogni testo o copy generato termini evidenziando '— Immobiliare Giancani'.
    """
    if not testo:
        return f"Opportunità esclusiva {BRAND_CLAIM}"
    testo = str(testo).strip()
    if BRAND_CLAIM not in testo and "Immobiliare Giancani" not in testo:
        testo = f"{testo} {BRAND_CLAIM}"
    elif testo.endswith("Immobiliare Giancani") and not testo.endswith(BRAND_CLAIM):
        testo = testo.replace("Immobiliare Giancani", BRAND_CLAIM)
    return testo

def get_testo_colonna_f(media_info, fallback="Splendida opportunità immobiliare selezionata per te."):
    """
    Estrae rigorosamente il testo parlato o descrittivo dalla Colonna F (TESTO_PARLATO_DARIA).
    Normalizza le superfici in metri quadri e appone il personal branding in chiusura.
    """
    testo = ""
    if isinstance(media_info, dict):
        testo = (
            media_info.get("testo_f")
            or media_info.get("TESTO_PARLATO_DARIA")
            or media_info.get("colonna_f")
            or media_info.get("descrizione")
            or media_info.get("descrizione_estesa")
            or ""
        )
    if not testo or not str(testo).strip():
        testo = fallback

    testo = normalize_mq(testo)
    return format_personal_branding(testo)
