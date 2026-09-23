#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Package Core: Regole di Business, Personal Branding e Cronologia"""
from .compliance import normalize_mq, format_personal_branding, get_testo_colonna_f
from .history import carica_cronologia_storie, salva_cronologia_storie

__all__ = [
    "normalize_mq",
    "format_personal_branding",
    "get_testo_colonna_f",
    "carica_cronologia_storie",
    "salva_cronologia_storie"
]
