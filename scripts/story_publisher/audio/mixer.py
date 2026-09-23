#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sound Design, Generazione Audio Procedurale e Ducking FFmpeg
"""

import os
import uuid
import random
import subprocess
import wave
import numpy as np
from story_publisher.config import ASSETS_DIR, SCRATCH_DIR
from story_publisher.system.env import find_ffmpeg
from story_publisher.audio.voice_tts import genera_voce_tts
from story_publisher.audio.copywriter import determina_fascia_oraria, genera_intro_invito_dinamico

def genera_audio_musica_allegra(output_audio_path=None):
    """
    Genera traccia audio di 15 secondi allegra, vivace ed energica (124 BPM, Major Chords) 100% royalty-free.
    """
    if not output_audio_path:
        output_audio_path = os.path.join(ASSETS_DIR, "cheerful_music.wav")

    BPM = 124
    BEAT = 60.0 / BPM
    DUR = 15.0
    SR = 44100
    nsamples = int(SR * DUR)

    left = np.zeros(nsamples, dtype=np.float32)
    right = np.zeros(nsamples, dtype=np.float32)

    prog = [
        ([261.63, 329.63, 392.00, 523.25], 130.81),
        ([246.94, 293.66, 392.00, 493.88], 98.00),
        ([220.00, 261.63, 329.63, 440.00], 110.00),
        ([220.00, 261.63, 349.23, 440.00], 87.31),
    ]

    chord_dur = DUR / len(prog)

    for c_idx, (notes, bass_freq) in enumerate(prog):
        c_start = c_idx * chord_dur
        num_beats = int(chord_dur / (BEAT / 2))
        for b in range(num_beats):
            note_t0 = c_start + b * (BEAT / 2)
            if note_t0 >= DUR:
                break
            s_i = int(note_t0 * SR)
            n_len = int(0.24 * SR)
            if s_i + n_len > nsamples:
                n_len = nsamples - s_i
            tn = np.linspace(0, 0.24, n_len, endpoint=False)
            decay = np.exp(-10 * tn)
            note_pitch = notes[b % len(notes)]
            if b % 2 == 0:
                bass_env = np.exp(-7 * tn)
                bass_tone = 0.5 * np.sin(2 * np.pi * bass_freq * tn) * bass_env
                left[s_i:s_i+n_len] += bass_tone * 0.7
                right[s_i:s_i+n_len] += bass_tone * 0.7

            pluck = (0.55 * np.sin(2 * np.pi * note_pitch * tn) +
                     0.3 * np.sin(4 * np.pi * note_pitch * tn) +
                     0.12 * np.sin(6 * np.pi * note_pitch * tn)) * decay
            pan = 0.35 + 0.3 * (b % 3)
            left[s_i:s_i+n_len] += pluck * (1.0 - pan) * 0.65
            right[s_i:s_i+n_len] += pluck * pan * 0.65

    fade_in = int(0.4 * SR)
    fade_out = int(1.2 * SR)
    left[:fade_in] *= np.linspace(0, 1, fade_in)
    right[:fade_in] *= np.linspace(0, 1, fade_in)
    left[-fade_out:] *= np.linspace(1, 0, fade_out)
    right[-fade_out:] *= np.linspace(1, 0, fade_out)

    mval = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if mval > 0:
        left = left * (0.8 / mval)
        right = right * (0.8 / mval)

    with wave.open(output_audio_path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        inter = np.empty((nsamples * 2,), dtype=np.int16)
        inter[0::2] = (left * 32767).astype(np.int16)
        inter[1::2] = (right * 32767).astype(np.int16)
        wf.writeframes(inter.tobytes())

    return output_audio_path

def crea_audio_mix_completo(testo_f, is_live=True, output_mixed_m4a=None, frase_positiva=None, fascia_info=None):
    """
    Combina la voce narrante (DarIA o DarIO) con la musica di sottofondo royalty-free
    e applica ducking audio con FFmpeg (musica a volume ridotto mentre la voce parla).
    """
    if not output_mixed_m4a:
        output_mixed_m4a = os.path.join(SCRATCH_DIR, f"story_audio_{uuid.uuid4().hex[:8]}.m4a")

    personaggio = "daria" if random.random() > 0.4 else "dario"
    voice_id = "it-IT-GiuseppeNeural" if personaggio == "dario" else "it-IT-ElsaNeural"

    if not fascia_info and not is_live:
        fascia_info = determina_fascia_oraria()

    testo_voce = genera_intro_invito_dinamico(
        personaggio=personaggio,
        testo_f=testo_f,
        is_live=is_live,
        frase_positiva=frase_positiva,
        fascia_info=fascia_info
    )

    voice_path = genera_voce_tts(testo_voce, voice_id=voice_id)

    # Selezione colonna sonora royalty-free con regola anti-ripetizione (> 10 storie)
    music_path = None
    try:
        import gestore_musica_storie as gms
        music_path = gms.ottieni_colonna_sonora_storia(durata_secondi=15.0)
    except Exception as e_gms:
        print(f"Avviso fallback gestore musica: {e_gms}")
        if fascia_info and fascia_info.get("musica_file"):
            cand_music = os.path.join(ASSETS_DIR, fascia_info["musica_file"])
            if os.path.exists(cand_music) and os.path.getsize(cand_music) > 10000:
                music_path = cand_music
                print(f"[OK] Canzone royalty-free Facebook selezionata ({fascia_info['nome']}): {fascia_info['musica_titolo']}")
        if not music_path:
            music_path = genera_audio_musica_allegra()

    ffmpeg_bin = find_ffmpeg()

    if voice_path and os.path.exists(voice_path):
        cmd = [
            ffmpeg_bin, "-y",
            "-i", voice_path,
            "-i", music_path,
            "-filter_complex",
            "[0:a]volume=1.2,apad=pad_dur=15[v];[1:a]volume=0.22[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2[outa]",
            "-map", "[outa]",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", "15",
            output_mixed_m4a
        ]
    else:
        cmd = [
            ffmpeg_bin, "-y",
            "-i", music_path,
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", "15",
            output_mixed_m4a
        ]

    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if proc.returncode == 0 and os.path.exists(output_mixed_m4a):
        return output_mixed_m4a
    return music_path
