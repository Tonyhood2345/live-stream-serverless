#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Package Audio: Sintesi Vocale Edge-TTS, Copywriting e Ducking Sonoro"""
from .voice_tts import genera_voce_tts
from .copywriter import determina_fascia_oraria, genera_intro_invito_dinamico, FRASI_POSITIVE_FLASH
from .mixer import genera_audio_musica_allegra, crea_audio_mix_completo

__all__ = [
    "genera_voce_tts",
    "determina_fascia_oraria",
    "genera_intro_invito_dinamico",
    "FRASI_POSITIVE_FLASH",
    "genera_audio_musica_allegra",
    "crea_audio_mix_completo"
]
