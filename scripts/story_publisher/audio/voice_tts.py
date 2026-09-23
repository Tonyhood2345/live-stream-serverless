#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sintesi Vocale Neurale (Edge-TTS)
Elsa per DarIA, Diego/Giuseppe per DarIO
"""

import os
import uuid
import asyncio
from story_publisher.config import SCRATCH_DIR

try:
    import edge_tts
    HAS_EDGE_TTS = True
except Exception:
    HAS_EDGE_TTS = False

def genera_voce_tts(testo, voice_id="it-IT-ElsaNeural", output_voice_path=None):
    """Genera file audio MP3 con Microsoft Edge Neural TTS."""
    if not output_voice_path:
        output_voice_path = os.path.join(SCRATCH_DIR, f"tts_{uuid.uuid4().hex[:8]}.mp3")

    if HAS_EDGE_TTS:
        try:
            async def _run():
                comm = edge_tts.Communicate(testo, voice_id, rate="+3%", pitch="+1Hz")
                await comm.save(output_voice_path)
            asyncio.run(_run())
            if os.path.exists(output_voice_path) and os.path.getsize(output_voice_path) > 3000:
                return output_voice_path
        except Exception as e:
            print(f"Avviso edge_tts ({voice_id}): {e}")
    return None
