#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestratore Modalità OFFLINE (rotazione oraria catalogo immobili e contenuti personalizzati)
"""

import time
import random
import hashlib
import requests

from story_publisher.config import PAGES, APPS_SCRIPT_URL, GUARANTEED_FALLBACK_IMAGES
from story_publisher.system.network import check_is_live_active, normalizza_foto_url
from story_publisher.core.compliance import normalize_mq
from story_publisher.core.history import carica_cronologia_storie, salva_cronologia_storie, get_recent_photo_urls
from story_publisher.video.video_engine import genera_video_da_clip_o_foto
from story_publisher.publishers.facebook import pubblica_storia_video_su_facebook
from story_publisher.publishers.youtube import pubblica_short_youtube
from story_publisher.publishers.tiktok import pubblica_storia_tiktok
from story_publisher.publishers.telegram import invia_notifica_telegram

DEFAULT_FALLBACK_IMMOBILI = [
    {
        "id": "default_favara_villa_giardino",
        "fonte": "Villa Giardino Favara",
        "titolo": "Villa Esclusiva con Giardino a Favara",
        "prezzo": "Trattativa Riservata",
        "mq": "160 metri quadri",
        "testoF": "Splendida soluzione indipendente con ampio giardino privato, verande panoramiche, rifiniture di alto pregio e massimo comfort ad Agrigento e Favara. — Immobiliare Giancani",
        "fotoUrl": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "id": "default_agrigento_attico_panoramico",
        "fonte": "Attico Vista Valle",
        "titolo": "Attico Panoramico Vista Valle dei Templi",
        "prezzo": "€ 145.000",
        "mq": "135 metri quadri",
        "testoF": "Elegante attico con terrazza a livello dominante il mare e la Valle, salone doppio, tre camere e ambienti inondati di luce naturale. — Immobiliare Giancani",
        "fotoUrl": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "id": "default_favara_appartamento_moderno",
        "fonte": "Appartamento Corso Favara",
        "titolo": "Appartamento Moderno Rifinito in Centro",
        "prezzo": "€ 89.000",
        "mq": "120 metri quadri",
        "testoF": "Spazioso appartamento ristrutturato con materiali di prima scelta, climatizzato, con cucina abitabile e balconi su corso principale. — Immobiliare Giancani",
        "fotoUrl": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "id": "default_residenza_aragona_villa",
        "fonte": "Dimora di Prestigio Aragona",
        "titolo": "Villa Padronale Immersa nel Verde",
        "prezzo": "Trattativa Riservata",
        "mq": "210 metri quadri",
        "testoF": "Dimora di prestigio con corte esterna in pietra, piscina, depandance e parco piantumato per chi cerca quiete e assoluta privacy. — Immobiliare Giancani",
        "fotoUrl": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "id": "default_casa_indipendente_terrazzo",
        "fonte": "Casa Indipendente Favara",
        "titolo": "Casa Indipendente con Garage e Terrazza",
        "prezzo": "€ 68.000",
        "mq": "150 metri quadri",
        "testoF": "Soluzione autonoma cielo-terra su più livelli con garage carrabile, zona giorno accogliente e terrazza ideale per momenti all'aperto. — Immobiliare Giancani",
        "fotoUrl": "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?q=80&w=1200&auto=format&fit=crop"
    }
]

def esegui_ciclo_offline(style="auto", sheet_filter=None, room_filter=None, custom_text=None, custom_image=None, custom_title=None):
    """
    Esegue la pubblicazione di una storia ogni ora quando NON si è in diretta live,
    oppure su richiesta manuale da regia Generator.html.
    Ruota su TUTTI gli immobili e stanze del catalogo senza mai bloccarsi sullo stesso immobile.
    Supporta anche storie NON immobiliari (Buone Notizie, Mindset, Notizie, Custom) con testo e immagine specificati.
    """
    print("\n" + "═" * 70)
    print("🕒 CONTROLLO PUBBLICAZIONE STORIA OFFLINE / CUSTOM")
    print("═" * 70)

    # 1. Log informativo stato diretta streaming (il bot orario offline pubblica comunque senza bloccarsi)
    is_manual = bool(custom_text or custom_image or sheet_filter or room_filter)
    if not is_manual:
        is_live, run_id = check_is_live_active()
        if is_live:
            print(f"ℹ️ Diretta Live streaming rilevata (Workflow Run ID: {run_id}). Procedo regolarmente con la storia oraria programmata.")
        else:
            print("ℹ️ Nessuna diretta live streaming attiva. Esecuzione storia oraria catalogo.")

    print("✅ Procedo con la pubblicazione della storia offline / personalizzata...")

    # Gestione CASO A: Contenuto NON immobiliare o personalizzato con testo/immagine scelti
    if custom_text or custom_image:
        print("🎨 Modalità Storia Personalizzata / Non Immobiliare attiva.")
        t_clean = str(custom_text or "Novità e aggiornamenti da Favara e Agrigento").strip()
        if "immobiliare giancani" not in t_clean.lower():
            t_clean += " — Immobiliare Giancani"

        img_sel = custom_image or random.choice(GUARANTEED_FALLBACK_IMAGES)
        tit_sel = custom_title or "Comunicazione Speciale"

        media_info = {
            "titolo": tit_sel,
            "prezzo": "",
            "mq": "",
            "videoUrl": None,
            "fotoUrl": img_sel,
            "testoF": t_clean,
            "isLive": False
        }
        selected = {
            "id": f"custom_{int(time.time())}",
            "titolo": tit_sel,
            "fonte": "Storia Personalizzata / Non Immobiliare",
            "mq": "",
            "prezzo": ""
        }
    else:
        # Gestione CASO B: Catalogo Immobili (rotazione deterministica anti-ripetizione su tutti gli immobili e stanze)
        candidates = []
        try:
            url_sheets = f"{APPS_SCRIPT_URL}?action=debug_all_sheets"
            r_sheets = requests.get(url_sheets, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=30)
            if r_sheets.status_code == 200:
                data_sh = r_sheets.json()
                all_sheets = data_sh.get('sheets', [])
                ignora_fogli = ['IMPOSTAZIONI_SOCIAL', 'CONFIGURAZIONE_TEMPI', 'RISULTATI_GIORNATA', 'FRASI_CALCIO', 'ANALYTICS_SOCIAL', 'MUSICA_SOTTOFONDO', 'ARCHIVIO_CLIENTI', 'PALINSESTO_ORARIO', 'PUBBLICITA_SPOT', 'PUBBLICITA_SCHERMO_CENTRALE', 'BATTUTE_DARIO']

                for s in all_sheets:
                    s_name = s.get('name', '')
                    if any(ig in s_name.upper() for ig in ignora_fogli):
                        continue
                    if sheet_filter and sheet_filter.lower() not in s_name.lower() and s_name.lower() not in sheet_filter.lower():
                        continue

                    sample = s.get('sample', [])
                    for row_idx, r in enumerate(sample[1:], start=2):
                        if len(r) > 5 and r[5] and str(r[5]).strip():
                            raw_media = str(r[0] or '').strip()
                            foto_url = ""
                            video_url = None

                            if 'youtube.com' in raw_media or 'youtu.be' in raw_media:
                                video_url = raw_media
                                if len(r) > 6 and str(r[6]).startswith('http'):
                                    foto_url = normalizza_foto_url(str(r[6]).strip())
                            elif raw_media.endswith(('.mp4', '.mov', '.avi')):
                                video_url = raw_media
                            elif raw_media.startswith('http') or 'lh3.googleusercontent.com' in raw_media or 'drive.google.com' in raw_media:
                                foto_url = normalizza_foto_url(raw_media)

                            if not foto_url and not video_url:
                                continue

                            stanza_riga = str(r[3] or '').strip() if len(r) > 3 else ''
                            if room_filter:
                                rf_str = str(room_filter).strip().lower()
                                if rf_str.isdigit():
                                    if int(rf_str) != row_idx and int(rf_str) != (row_idx - 1):
                                        continue
                                elif rf_str not in stanza_riga.lower() and stanza_riga.lower() not in rf_str:
                                    continue

                            s_clean = s_name.replace('_', ' ').strip()
                            if stanza_riga and stanza_riga.lower() not in ['ambiente', ''] and stanza_riga.lower() != s_clean.lower():
                                titolo_atomico = f"{s_clean} — {stanza_riga}"
                            else:
                                titolo_atomico = s_clean

                            hash_seed = f"{s_name}_{row_idx}_{foto_url or raw_media or titolo_atomico}"
                            hash_cand = hashlib.md5(hash_seed.encode('utf-8')).hexdigest()[:8]
                            cand_id = f"{s_name}_riga{row_idx}_{hash_cand}"
                            testo_riga = str(r[5]).strip()
                            if "immobiliare giancani" not in testo_riga.lower():
                                testo_riga += " — Immobiliare Giancani"

                            candidates.append({
                                "id": cand_id,
                                "fonte": s_clean,
                                "sheet": s_name,
                                "rowIndex": row_idx,
                                "stanza": stanza_riga,
                                "videoUrl": video_url,
                                "fotoUrl": foto_url,
                                "prezzo": str(r[1] or 'Trattativa Riservata').strip(),
                                "mq": normalize_mq(r[2]),
                                "titolo": titolo_atomico,
                                "testoF": testo_riga
                            })
        except Exception as eSheets:
            print(f"Avviso lettura catalogo fogli: {eSheets}")

        # 2. Controllo duplicazione foto nel pool dei candidati estratti dai fogli
        candidati_foto_uniche = []
        foto_viste_nel_pool = set()
        for c in candidates:
            f_url = c.get("fotoUrl")
            if f_url:
                if f_url in foto_viste_nel_pool:
                    continue
                foto_viste_nel_pool.add(f_url)
            candidati_foto_uniche.append(c)
        candidates = candidati_foto_uniche

        if not candidates:
            # Fallback intelligente su immobile attivo da Apps Script
            try:
                url_curr = f"{APPS_SCRIPT_URL}?action=debug_immobile&q=current"
                r_curr = requests.get(url_curr, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=15)
                if r_curr.status_code == 200:
                    d_curr = r_curr.json()
                    foto_curr = normalizza_foto_url(d_curr.get('fotoUrl') or d_curr.get('mediaUrl'))
                    testo_curr = d_curr.get('testoDaLeggere') or d_curr.get('testo') or 'Splendido immobile selezionato ad Agrigento e Favara. — Immobiliare Giancani'
                    if "immobiliare giancani" not in testo_curr.lower():
                        testo_curr += " — Immobiliare Giancani"
                    candidates.append({
                        "id": f"active_{int(time.time())}",
                        "fonte": "Immobile Corrente",
                        "sheet": "ACTIVE",
                        "rowIndex": 2,
                        "videoUrl": None,
                        "fotoUrl": foto_curr or GUARANTEED_FALLBACK_IMAGES[0],
                        "prezzo": str(d_curr.get('prezzo') or 'Trattativa Riservata').strip(),
                        "mq": normalize_mq(d_curr.get('mq', '120 metri quadri')),
                        "titolo": d_curr.get('titolo', 'Immobile in Vendita'),
                        "testoF": testo_curr
                    })
            except Exception:
                pass

        if not candidates:
            print("⚠️ Nessun immobile estratto dai fogli. Utilizzo catalogo immobili di riserva garantiti...")
            candidates.extend(DEFAULT_FALLBACK_IMMOBILI)

        # ROTAZIONE CASUALE ANTI-RIPETIZIONE CON CRONOLOGIA PERSISTENTE E ANTI-DOPPIONI FOTO
        cronologia = carica_cronologia_storie()
        recent_photos = get_recent_photo_urls(cronologia)

        # Filtra candidati mai visti sia per ID univoco sia per URL foto già pubblicata
        candidati_mai_visti = [
            c for c in candidates 
            if c["id"] not in cronologia and (not c.get("fotoUrl") or c.get("fotoUrl") not in recent_photos)
        ]

        if not candidati_mai_visti:
            print(f"🔄 Tutte le foto/immobili del catalogo ({len(candidates)}) sono state pubblicate di recente!")
            print("   Reset controllato della cronologia preservando gli ultimi elementi per evitare ripetizioni consecutive...")
            items_sorted = sorted(
                cronologia.items(),
                key=lambda x: x[1].get("timestamp", 0) if isinstance(x[1], dict) else 0
            )
            # Conserva solo gli ultimi elementi (fino a 5 o metà catalogo)
            n_keep = min(5, max(1, len(candidates) // 2))
            ultimi = dict(items_sorted[-n_keep:]) if len(items_sorted) >= n_keep else {}
            cronologia = ultimi
            recent_photos = get_recent_photo_urls(cronologia)

            candidati_mai_visti = [
                c for c in candidates 
                if c["id"] not in cronologia and (not c.get("fotoUrl") or c.get("fotoUrl") not in recent_photos)
            ]
            if not candidati_mai_visti:
                ultima_foto = items_sorted[-1][1].get("fotoUrl") if items_sorted else None
                candidati_mai_visti = [c for c in candidates if c.get("fotoUrl") != ultima_foto] or candidates

        # SELEZIONE CASUALE TRA GLI IMMOBILI MAI VISTI (come richiesto: immobili a caso con info relative)
        selected = random.choice(candidati_mai_visti)

        # Salva nella cronologia persistente con timestamp e fotoUrl
        cronologia[selected["id"]] = {
            "timestamp": time.time(),
            "titolo": selected["titolo"],
            "fonte": selected["fonte"],
            "stanza": selected.get("stanza", ""),
            "fotoUrl": selected.get("fotoUrl", "")
        }
        salva_cronologia_storie(cronologia)
        print(f"🎯 Immobile selezionato A CASO per la storia ({len(cronologia)} pubblicati nel ciclo su {len(candidates)} totali):")
        print(f"   Titolo: {selected['titolo']} ({selected['fonte']})")
        print(f"   Dati sincronizzati atomici: Prezzo={selected.get('prezzo')}, MQ={selected.get('mq')}, Foto={bool(selected.get('fotoUrl'))}")
        print(f"   Colonna F: '{selected.get('testoF')[:70]}...'")

        media_info = {
            "titolo": selected.get('titolo', 'Immobile in Vendita'),
            "prezzo": selected.get('prezzo', 'Trattativa Riservata'),
            "mq": normalize_mq(selected.get('mq')),
            "videoUrl": selected.get('videoUrl'),
            "fotoUrl": selected.get('fotoUrl'),
            "testoF": selected.get('testoF'),
            "isLive": False
        }

    video_path = genera_video_da_clip_o_foto(media_info, style=style)
    if not video_path:
        print("❌ Errore generazione video storia offline.")
        return []

    risultati = []
    for target in PAGES:
        print(f"📘 Pubblicazione Video Storia su: {target['nome']}...")
        try:
            res = pubblica_storia_video_su_facebook(target['id'], target['token'], video_path)
            res['nome'] = target['nome']
            print(f"[OK] Storia pubblicata! ID: {res.get('story_id')}")
            risultati.append(res)
        except Exception as ePub:
            print(f"❌ Errore upload su {target['nome']}: {ePub}")
            risultati.append({"nome": target['nome'], "success": False, "error": str(ePub)})

    # Pubblica su YouTube Shorts (@immobiliaregiancani761)
    try:
        res_yt = pubblica_short_youtube(video_path, media_info)
        print(f"[OK] YouTube Shorts: {res_yt.get('story_id')} - {res_yt.get('url')}")
        risultati.append(res_yt)
    except Exception as eYt:
        print(f"❌ Errore YouTube Shorts: {eYt}")
        risultati.append({"nome": "YouTube Shorts (@immobiliaregiancani761)", "success": False, "error": str(eYt)})

    # Pubblica / Sincronizza su TikTok Stories (@immobiliare_giancani)
    try:
        res_tk = pubblica_storia_tiktok(video_path, media_info)
        print(f"[OK] TikTok Stories: {res_tk.get('story_id')} - {res_tk.get('url')}")
        risultati.append(res_tk)
    except Exception as eTk:
        print(f"❌ Errore TikTok Stories: {eTk}")
        risultati.append({"nome": "TikTok Stories (@immobiliare_giancani)", "success": False, "error": str(eTk)})

    invia_notifica_telegram(selected['titolo'], selected.get('mq', ''), selected.get('prezzo', ''), risultati, is_live=False)
    print("✨ Ciclo storia oraria multi-piattaforma completato con successo. — Immobiliare Giancani\n")
    return risultati
