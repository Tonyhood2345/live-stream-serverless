#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connettore Instagram Stories
"""

def pubblica_storia_instagram(ig_user_id, page_token, video_path):
    """
    Pubblicazione Instagram gestita secondo le impostazioni correnti di sistema.
    """
    print("ℹ️ Pubblicazione su Instagram DISABILITATA su richiesta dell'utente (solo Facebook attivo).")
    return {
        "nome": "Instagram Stories (@giancani_immobiliare)",
        "success": True,
        "skipped": True,
        "story_id": "DISABLED",
        "metodo": "Disabilitato su richiesta utente"
    }
