#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
IMMOBILIARE GIANCANI — GESTORE COLONNE SONORE ROYALTY-FREE PER STORIE & SOCIAL
═══════════════════════════════════════════════════════════════════════════════
Caratteristiche:
1. 100% Senza Diritti d'Autore (Royalty-Free):
   - Nessun blocco o strike copyright su Facebook, Instagram, YouTube Shorts, TikTok.
2. Regola Rigorosa Anti-Ripetizione (> 10 Storie):
   - Mantiene uno storico persistente in 'storico_musica_storie.json'.
   - Esclude categoricamente le musiche utilizzate nelle ultime 10 storie.
   - Rotazione continua su un catalogo di 14 brani MP3 reali + 4 generatori
     procedurali tematici (totale 18 tracce disponibili).
3. Normalizzazione & Taglio Dinamico (15s):
   - Dissolvenza in ingresso (fade-in 0.5s) e in uscita (fade-out 1.5s).
4. Ducking Vocale per i Conduttori:
   - Mix audio professionale con la voce di DarIA o DarIO (voce 1.2x, musica 0.22x).
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import io
import sys
import json
import time
import random
import shutil
import subprocess
import wave
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR) if os.path.basename(BASE_DIR) == 'scripts' else BASE_DIR

# Directory musicali e cache
MUSICA_DIR_PROJECT = os.path.join(PROJECT_DIR, "musica_sottofondo")
MUSICA_DIR_PARENT = os.path.join(os.path.dirname(PROJECT_DIR), "musica_sottofondo")
OUTPUT_AUDIO_DIR = os.path.join(PROJECT_DIR, "audio_generati_mp3")
os.makedirs(OUTPUT_AUDIO_DIR, exist_ok=True)

STORICO_MUSICA_FILE = os.path.join(PROJECT_DIR, "storico_musica_storie.json")
BUFFER_ANTI_RIPETIZIONE = 10

# ═══════════════════════════════════════════════════════════════════════════════
# 🎵 1. CATALOGO BRANI ROYALTY-FREE (14 MP3 REALI + 4 PROCEDURALI)
# ═══════════════════════════════════════════════════════════════════════════════

TRACCE_ROYALTY_FREE_MP3 = [
    {
        "id": "back_road_town",
        "nome": "Back Road Out of Town",
        "file": "Back Road Out of Town.mp3",
        "genere": "Acoustic / Country Folk",
        "mood": "Caldo, accogliente, ideale per case indipendenti e ville di campagna"
    },
    {
        "id": "calma_mediodia",
        "nome": "Calma del Mediodia",
        "file": "Calma del Mediodia.mp3",
        "genere": "Spanish Guitar / Relax",
        "mood": "Mediterraneo, solare, perfetto per la Sicilia e dimore estive"
    },
    {
        "id": "sicilian_sunset",
        "nome": "Sicilian Sunset",
        "file": "Sicilian Sunset.mp3",
        "genere": "Acoustic Sunset / Ambient",
        "mood": "Suggestivo, emozionale, valorizza tramonti e verande panoramiche"
    },
    {
        "id": "ambient_calma_2",
        "nome": "Ambient Calma Serale",
        "file": "ambient_calma_2.mp3",
        "genere": "Ambient Chill",
        "mood": "Puro relax, atmosfera tranquilla e rilassante per interni"
    },
    {
        "id": "ambient_ispirazione_1",
        "nome": "Ambient Ispirazione & Futuro",
        "file": "ambient_ispirazione_1.mp3",
        "genere": "Uplifting Ambient",
        "mood": "Ispirazionale, trasmette fiducia e nuovi inizi abitativi"
    },
    {
        "id": "ambient_profondo_3",
        "nome": "Ambient Profondo & Trasparenza",
        "file": "ambient_profondo_3.mp3",
        "genere": "Deep Ambient",
        "mood": "Elegante, solido, ideale per residenze moderne ed esclusive"
    },
    {
        "id": "cinematic_emozione_6",
        "nome": "Cinematic Emozione d'Autore",
        "file": "cinematic_emozione_6.mp3",
        "genere": "Cinematic Emotional",
        "mood": "Coinvolgente ed emozionale per proprietà di grande pregio"
    },
    {
        "id": "cinematic_film_5",
        "nome": "Cinematic Film & Architettura",
        "file": "cinematic_film_5.mp3",
        "genere": "Cinematic Epic",
        "mood": "Imponente e dinamico, valorizza facciate e ampi spazi"
    },
    {
        "id": "electronic_modern_9",
        "nome": "Electronic Modern Smart Living",
        "file": "electronic_modern_9.mp3",
        "genere": "Modern Electronic / Future",
        "mood": "Fresco, contemporaneo, ideale per attici e domotica"
    },
    {
        "id": "jazz_eleganza_8",
        "nome": "Jazz Eleganza & Stile",
        "file": "jazz_eleganza_8.mp3",
        "genere": "Smooth Jazz",
        "mood": "Sofisticato e raffinato, perfetto per palazzi d'epoca"
    },
    {
        "id": "jazz_lounge_business_7",
        "nome": "Jazz Lounge Business",
        "file": "jazz_lounge_business_7.mp3",
        "genere": "Lounge Jazz",
        "mood": "Professionale, accogliente, consulenza di alto livello"
    },
    {
        "id": "jazz_lounge_business_8",
        "nome": "Jazz Lounge Prestige",
        "file": "jazz_lounge_business_8.mp3",
        "genere": "Lounge Prestige",
        "mood": "Distinto e piacevole, valorizza investimenti commerciali"
    },
    {
        "id": "pianoforte_armonia_4",
        "nome": "Pianoforte Armonia di Casa",
        "file": "pianoforte_armonia_4.mp3",
        "genere": "Piano Solo",
        "mood": "Intimo, caldo, parla direttamente al cuore della famiglia"
    },
    {
        "id": "pianoforte_classico_3",
        "nome": "Pianoforte Classico Tradizione",
        "file": "pianoforte_classico_3.mp3",
        "genere": "Classical Piano",
        "mood": "Nobiltà e prestigio senza tempo"
    }
]

GENERATORI_PROCEDURALI = [
    {
        "id": "proc_cheerful_pop",
        "nome": "Sintetizzatore Acustico 124 BPM",
        "genere": "Acoustic Pop 100% Royalty-Free",
        "mood": "Solare, ritmato e brillante per storie Instagram/Facebook veloci"
    },
    {
        "id": "proc_luxury_lounge",
        "nome": "Sintetizzatore Luxury Lounge",
        "genere": "Gold Lounge Ambient",
        "mood": "Bassi vellutati e accordi maggiori per immobili di lusso"
    },
    {
        "id": "proc_mediterranean_guitar",
        "nome": "Sintetizzatore Chitarra Mediterranea",
        "genere": "Mediterranean Acoustic Arpeggio",
        "mood": "Colori caldi della Sicilia, verande e luce naturale"
    },
    {
        "id": "proc_ambient_prestige",
        "nome": "Sintetizzatore Ambient Prestige",
        "genere": "Minimal Ambient Harp",
        "mood": "Design minimalista e sensazione di ampiezza"
    }
]

ALL_TRACKS = TRACCE_ROYALTY_FREE_MP3 + GENERATORI_PROCEDURALI

def find_ffmpeg():
    """Localizza FFmpeg su Windows o Linux (GitHub Actions)"""
    candidates = [
        shutil.which("ffmpeg"),
        os.path.join(PROJECT_DIR, "ffmpeg.exe"),
        os.path.join(os.path.dirname(PROJECT_DIR), "ffmpeg.exe"),
        "ffmpeg"
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return "ffmpeg"

def trova_file_mp3_reale(nome_file):
    """Cerca il file MP3 nelle cartelle consentite"""
    percorsi = [
        os.path.join(MUSICA_DIR_PROJECT, nome_file),
        os.path.join(MUSICA_DIR_PARENT, nome_file),
        os.path.join(PROJECT_DIR, "assets", nome_file),
        os.path.join(PROJECT_DIR, nome_file)
    ]
    for p in percorsi:
        if os.path.exists(p) and os.path.getsize(p) > 5000:
            return p
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# 🔄 2. GESTIONE STORICO & REGOLA ANTI-RIPETIZIONE (> 10 STORIE)
# ═══════════════════════════════════════════════════════════════════════════════

def carica_storico_musiche():
    """Carica lo storico persistente delle tracce musicali utilizzate"""
    if os.path.exists(STORICO_MUSICA_FILE):
        try:
            with open(STORICO_MUSICA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("ultime_musiche", [])
        except Exception as e:
            print(f"Avviso lettura storico musiche: {e}")
    return []

def salva_storico_musiche(cronologia):
    """Salva atomicamente lo storico aggiornato"""
    try:
        data = {
            "regola": "Nessuna musica uguale per oltre 10 storie consecutive",
            "totale_tracce_disponibili": len(ALL_TRACKS),
            "buffer_anti_ripetizione": BUFFER_ANTI_RIPETIZIONE,
            "ultimo_aggiornamento": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ultime_musiche": cronologia[-50:]  # Mantieni le ultime 50 voci
        }
        tmp_file = STORICO_MUSICA_FILE + ".tmp"
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        if os.path.exists(STORICO_MUSICA_FILE):
            os.remove(STORICO_MUSICA_FILE)
        os.rename(tmp_file, STORICO_MUSICA_FILE)
    except Exception as e:
        print(f"Avviso salvataggio storico musiche: {e}")

def seleziona_prossima_traccia_musicale(escludi_id=None):
    """
    Seleziona la traccia musicale per la prossima storia applicando
    la regola che NON deve essere uguale a nessuna delle ultime 10 storie!
    """
    cronologia = carica_storico_musiche()
    ultimi_10_usati = cronologia[-BUFFER_ANTI_RIPETIZIONE:] if len(cronologia) >= BUFFER_ANTI_RIPETIZIONE else cronologia
    
    # Se un brano è stato espressamente escluso in questo turno
    if escludi_id:
        ultimi_10_usati = list(ultimi_10_usati) + [escludi_id]

    # Trova tutti i brani disponibili che NON sono negli ultimi 10
    candidati = [t for t in ALL_TRACKS if t["id"] not in ultimi_10_usati]

    # Se per assurdo tutti i brani fossero finiti nel buffer (non possibile con 18 brani e buffer 10)
    if not candidati:
        meno_recente = cronologia[0] if cronologia else ALL_TRACKS[0]["id"]
        candidati = [t for t in ALL_TRACKS if t["id"] == meno_recente]

    # Priorità ai file MP3 fisici esistenti sul disco
    candidati_fisici = []
    candidati_proc = []
    for c in candidati:
        if "file" in c and trova_file_mp3_reale(c["file"]):
            candidati_fisici.append(c)
        else:
            candidati_proc.append(c)

    if candidati_fisici:
        # Seleziona con preferenza tra i brani fisici non usati nelle ultime 10 storie
        scelta = random.choice(candidati_fisici)
    else:
        scelta = random.choice(candidati_proc if candidati_proc else ALL_TRACKS)

    # Aggiorna lo storico persistente
    cronologia.append(scelta["id"])
    salva_storico_musiche(cronologia)

    print(f"🎵 [MUSICA SELEZIONATA]: '{scelta['nome']}' ({scelta['genere']})")
    print(f"   🛡️ Anti-ripetizione attiva: esclusi gli ultimi {len(ultimi_10_usati)} brani usati.")
    return scelta

# ═══════════════════════════════════════════════════════════════════════════════
# 🎹 3. SINTETIZZATORE PROCEDURALE Tematico (100% Fallback Autonomo)
# ═══════════════════════════════════════════════════════════════════════════════

def sintetizza_traccia_procedurale(stile_id, output_path, durata=15.0, bpm=124):
    """
    Genera un file WAV a 44.1kHz stereo armonizzato secondo lo stile specificato.
    Garantito al 100% royalty-free e generato matematicamente.
    """
    SR = 44100
    nsamples = int(SR * durata)
    BEAT = 60.0 / bpm

    left = np.zeros(nsamples, dtype=np.float32)
    right = np.zeros(nsamples, dtype=np.float32)

    if stile_id == "proc_luxury_lounge":
        # Accordi vellutati Dmaj9 - Gmaj7 - Em9 - A7sus4
        prog = [
            ([293.66, 369.99, 440.00, 554.37, 659.25], 73.42),
            ([196.00, 246.94, 293.66, 369.99, 440.00], 98.00),
            ([164.81, 196.00, 246.94, 293.66, 369.99], 82.41),
            ([220.00, 293.66, 329.63, 440.00, 587.33], 110.00),
        ]
        pl_decay = 7.0
    elif stile_id == "proc_mediterranean_guitar":
        # Chitarra acustica solare Am - Fmaj7 - C - G
        prog = [
            ([220.00, 261.63, 329.63, 440.00], 110.00),
            ([174.61, 261.63, 329.63, 440.00], 87.31),
            ([261.63, 329.63, 392.00, 523.25], 130.81),
            ([196.00, 246.94, 293.66, 392.00], 98.00),
        ]
        pl_decay = 9.0
    elif stile_id == "proc_ambient_prestige":
        # Arpeggio arpa minimalista Emaj9 - C#m9 - F#m7 - B11
        prog = [
            ([329.63, 415.30, 493.88, 622.25], 82.41),
            ([277.18, 329.63, 415.30, 554.37], 69.30),
            ([185.00, 220.00, 277.18, 369.99], 92.50),
            ([246.94, 329.63, 369.99, 493.88], 123.47),
        ]
        pl_decay = 6.0
    else:  # proc_cheerful_pop
        # Allegro classico C - G - Am - F
        prog = [
            ([261.63, 329.63, 392.00, 523.25], 130.81),
            ([246.94, 293.66, 392.00, 493.88], 98.00),
            ([220.00, 261.63, 329.63, 440.00], 110.00),
            ([220.00, 261.63, 349.23, 440.00], 87.31),
        ]
        pl_decay = 10.0

    chord_dur = durata / len(prog)

    for c_idx, (notes, bass_freq) in enumerate(prog):
        c_start = c_idx * chord_dur
        num_beats = int(chord_dur / (BEAT / 2))
        for b in range(num_beats):
            note_t0 = c_start + b * (BEAT / 2)
            if note_t0 >= durata: break
            s_i = int(note_t0 * SR)
            n_len = int(0.26 * SR)
            if s_i + n_len > nsamples:
                n_len = nsamples - s_i
            tn = np.linspace(0, 0.26, n_len, endpoint=False)
            decay = np.exp(-pl_decay * tn)
            note_pitch = notes[b % len(notes)]
            if b % 2 == 0:
                bass_env = np.exp(-5.5 * tn)
                bass_tone = 0.45 * np.sin(2 * np.pi * bass_freq * tn) * bass_env
                left[s_i:s_i+n_len] += bass_tone * 0.7
                right[s_i:s_i+n_len] += bass_tone * 0.7

            pluck = (0.55 * np.sin(2 * np.pi * note_pitch * tn) +
                     0.30 * np.sin(4 * np.pi * note_pitch * tn) +
                     0.15 * np.sin(6 * np.pi * note_pitch * tn)) * decay
            pan = 0.35 + 0.3 * (b % 3)
            left[s_i:s_i+n_len] += pluck * (1.0 - pan) * 0.65
            right[s_i:s_i+n_len] += pluck * pan * 0.65

    # Dissolvenze
    fade_in = int(0.4 * SR)
    fade_out = int(1.4 * SR)
    left[:fade_in] *= np.linspace(0, 1, fade_in)
    right[:fade_in] *= np.linspace(0, 1, fade_in)
    left[-fade_out:] *= np.linspace(1, 0, fade_out)
    right[-fade_out:] *= np.linspace(1, 0, fade_out)

    mval = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if mval > 0:
        left = left * (0.8 / mval)
        right = right * (0.8 / mval)

    with wave.open(output_path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        inter = np.empty((nsamples * 2,), dtype=np.int16)
        inter[0::2] = (left * 32767).astype(np.int16)
        inter[1::2] = (right * 32767).astype(np.int16)
        wf.writeframes(inter.tobytes())

    return output_path

# ═══════════════════════════════════════════════════════════════════════════════
# 🎚️ 4. OTTIENI COLONNA SONORA PRONTA (15s CON FADE-IN & FADE-OUT)
# ═══════════════════════════════════════════════════════════════════════════════

def ottieni_colonna_sonora_storia(output_path=None, durata_secondi=15.0):
    """
    Seleziona la traccia ruotata con anti-ripetizione (> 10 storie)
    e produce il file audio ritagliato e dissolto pronto per il video.
    """
    traccia = seleziona_prossima_traccia_musicale()

    if not output_path:
        output_path = os.path.join(OUTPUT_AUDIO_DIR, f"bgm_{traccia['id']}_{int(time.time())}.m4a")

    ffmpeg_bin = find_ffmpeg()

    # Caso 1: Traccia MP3 Reale sul disco
    if "file" in traccia:
        mp3_path = trova_file_mp3_reale(traccia["file"])
        if mp3_path and os.path.exists(mp3_path):
            try:
                # Fade in 0.5s e Fade out 1.5s prima della fine
                st_fade_out = max(0.0, durata_secondi - 1.5)
                cmd = [
                    ffmpeg_bin, "-y",
                    "-ss", "0",
                    "-i", mp3_path,
                    "-t", str(durata_secondi),
                    "-af", f"afade=t=in:ss=0:d=0.5,afade=t=out:st={st_fade_out}:d=1.5,volume=0.85",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    output_path
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                    print(f"✅ Traccia MP3 pronta: {output_path} (Brano: {traccia['nome']})")
                    return output_path
            except Exception as e:
                print(f"Avviso elaborazione FFmpeg per {traccia['file']}: {e}")

    # Caso 2: Sintetizzatore Procedurale (Garantito al 100%)
    wav_temp = os.path.join(OUTPUT_AUDIO_DIR, f"temp_synth_{traccia['id']}.wav")
    sintetizza_traccia_procedurale(traccia["id"], wav_temp, durata=durata_secondi)

    try:
        cmd = [
            ffmpeg_bin, "-y",
            "-i", wav_temp,
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(wav_temp):
            os.remove(wav_temp)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 5000:
            print(f"✅ Traccia procedurale pronta: {output_path} (Stile: {traccia['nome']})")
            return output_path
    except Exception:
        # Ritorna direttamente il WAV se FFmpeg non converte
        return wav_temp

    return output_path

# ═══════════════════════════════════════════════════════════════════════════════
# 🎙️ 5. MIX VOCALE CON DUCKING AUTOMATICO (DARIA/DARIO + BGM)
# ═══════════════════════════════════════════════════════════════════════════════

def crea_audio_mix_storia_con_voce(voce_path, output_mixed_path=None, durata_secondi=15.0):
    """
    Combina la narrazione vocale di DarIA o DarIO con la colonna sonora
    selezionata tramite regola anti-ripetizione (> 10 storie).
    Esegue ducking: voce chiara a 1.25x, musica in sottofondo a 0.22x.
    """
    if not output_mixed_path:
        output_mixed_path = os.path.join(OUTPUT_AUDIO_DIR, f"story_mix_{uuid_hex()}.m4a")

    bgm_path = ottieni_colonna_sonora_storia(durata_secondi=durata_secondi)
    ffmpeg_bin = find_ffmpeg()

    if voce_path and os.path.exists(voce_path) and os.path.getsize(voce_path) > 3000:
        cmd = [
            ffmpeg_bin, "-y",
            "-i", voce_path,
            "-i", bgm_path,
            "-filter_complex",
            f"[0:a]volume=1.25,apad=pad_dur={durata_secondi}[v];"
            f"[1:a]volume=0.22,afade=t=in:ss=0:d=0.4,afade=t=out:st={durata_secondi-1.5}:d=1.5[m];"
            f"[v][m]amix=inputs=2:duration=first:dropout_transition=2[outa]",
            "-map", "[outa]",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(durata_secondi),
            output_mixed_path
        ]
    else:
        # Se non c'è voce, musica piena ma controllata a 0.85x
        cmd = [
            ffmpeg_bin, "-y",
            "-i", bgm_path,
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(durata_secondi),
            output_mixed_path
        ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(output_mixed_path) and os.path.getsize(output_mixed_path) > 10000:
            return output_mixed_path
    except Exception as e:
        print(f"Avviso mix FFmpeg: {e}")

    return bgm_path

def uuid_hex():
    import uuid
    return uuid.uuid4().hex[:8]

if __name__ == "__main__":
    print("🎵 Test Gestore Colonne Sonore Royalty-Free...")
    cron = carica_storico_musiche()
    print(f"Cronologia attuale: {cron[-10:] if cron else 'vuota'}")
    t = seleziona_prossima_traccia_musicale()
    print(f"Traccia scelta: {t['nome']}")
    out = ottieni_colonna_sonora_storia(durata_secondi=15.0)
    print(f"File generato: {out}")
