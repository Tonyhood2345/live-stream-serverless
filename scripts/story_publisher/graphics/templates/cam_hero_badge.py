#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stile CAM Hero Badge (9:16 & 1:1)
Foto full-bleed protagonista, logo ufficiale in evidenza su box protetto,
badge fluttuante a due livelli (ribbon solido "NUOVO IMMOBILE" + box semi-trasparente),
recapiti completi e rotazione cromatica giornaliera.
— Immobiliare Giancani
"""

import os
import motore_grafica_storie as mgs

def crea_story_cam_hero_badge_9_16(media_info, palette=None, output_path=None):
    return mgs.crea_story_cam_hero_badge_9_16(media_info, palette=palette, output_path=output_path)

def crea_flyer_cam_hero_badge_1_1(media_info, palette=None, output_path=None):
    return mgs.crea_flyer_cam_hero_badge_1_1(media_info, palette=palette, output_path=output_path)
