#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  YOUTUBE SHORTS UPLOADER & INTEGRATION ENGINE
  Gestione Multi-Canale:
  - Canale 1: Storie della Mitologia Greca (Ore 11:00)
  - Canale 2: Storie della Bibbia — «Eterno Nostra Giustizia» (Ore 20:00)
  
  Conforme alla regola globale di brand Immobiliare Giancani e Colonna F.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import json
import time
import datetime
import ssl
import urllib3
import requests

# Patch SSL per ambiente Windows e certificati locali
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

orig_session_init = requests.Session.__init__
def patched_session_init(self, *args, **kwargs):
    orig_session_init(self, *args, **kwargs)
    self.verify = False
requests.Session.__init__ = patched_session_init

try:
    import httplib2
    orig_http_init = httplib2.Http.__init__
    def patched_http_init(self, *args, **kwargs):
        kwargs['disable_ssl_certificate_validation'] = True
        orig_http_init(self, *args, **kwargs)
    httplib2.Http.__init__ = patched_http_init
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "video_storie_output")

# Configurazioni Canali YouTube Dedicati
CANALI_YOUTUBE = {
    "mitologia": {
        "nome_canale": "Storie della Mitologia Greca",
        "descrizione_canale": "I grandi miti dell'Olimpo, eroi e leggende dell'Antica Grecia raccontati in 2 minuti.",
        "cred_file": os.path.join(BASE_DIR, "credentials_youtube_mitologia.json"),
        "token_file": os.path.join(BASE_DIR, "token_youtube_mitologia.json"),
        "default_tags": ["Mitologia Greca", "Miti Greci", "Olimpo", "Eroi Greci", "Storia Antica", "Shorts", "YouTube Shorts", "Immobiliare Giancani", "Antonio Giancani"]
    },
    "bibbia": {
        "nome_canale": "Storie della Bibbia — Eterno Nostra Giustizia",
        "descrizione_canale": "I grandi racconti e insegnamenti della Bibbia in animazione 2D in 2 minuti.",
        "cred_file": os.path.join(BASE_DIR, "credentials_youtube_bibbia.json"),
        "token_file": os.path.join(BASE_DIR, "token_youtube_bibbia.json"),
        "default_tags": ["Storie della Bibbia", "Bibbia", "Eterno Nostra Giustizia", "Fede", "Antico Testamento", "Shorts", "YouTube Shorts", "Immobiliare Giancani", "Antonio Giancani"]
    },
    "giancani": {
        "nome_canale": "Immobiliare Giancani (@immobiliaregiancani761)",
        "descrizione_canale": "Canale Ufficiale Immobiliare Giancani - Live Tour, Storie e Opportunità Immobiliari a Favara e Agrigento con DarIA e Antonio Giancani.",
        "cred_file": os.path.join(BASE_DIR, "client_secret.json"),
        "token_file": os.path.join(BASE_DIR, "token_youtube_giancani.json"),
        "default_tags": ["Immobiliare Giancani", "Favara", "Agrigento", "DarIA", "Case in Vendita", "Diretta Live", "Shorts", "YouTube Shorts", "Antonio Giancani"]
    }
}


def genera_metadati_youtube(video_path, storia, mode="mitologia"):
    """
    Genera metadati ottimizzati SEO per YouTube Shorts (<60s verticale)
    rispettando rigorosamente il testo di Colonna F e il personal branding di Immobiliare Giancani.
    """
    m_lower = mode.lower()
    if "mitologia" in m_lower:
        mode_key = "mitologia"
    elif "bibbia" in m_lower:
        mode_key = "bibbia"
    else:
        mode_key = "giancani"
    config = CANALI_YOUTUBE.get(mode_key, CANALI_YOUTUBE["giancani"])
    
    titolo = storia.get("titolo", "Racconto Epico")
    colonna_f = storia.get("testo_colonna_f", "").replace("|||", "\n\n").strip()
    storia_id = storia.get("id", "1")

    if mode_key == "mitologia":
        short_title = f"{titolo} in 2 Minuti | Miti dell'Antica Grecia #Shorts"
        header = f"🏛️ {titolo.upper()} — STORIE DELLA MITOLOGIA GRECA IN 2 MINUTI 🏛️"
        hashtags = "#Shorts #MitologiaGreca #MitiGreci #Olimpo #Eroi #CulturaClassica #ImmobiliareGiancani #AntonioGiancani"
    elif mode_key == "bibbia":
        short_title = f"{titolo} in 2 Minuti | Storie della Bibbia #Shorts"
        header = f"📖 {titolo.upper()} — STORIE DELLA BIBBIA («ETERNO NOSTRA GIUSTIZIA») 📖"
        hashtags = "#Shorts #StorieDellaBibbia #Bibbia #Fede #ParolaDiDio #EternoNostraGiustizia #ImmobiliareGiancani #AntonioGiancani"
    elif "pillole" in m_lower:
        short_title = f"{titolo} | Pillole Immobiliari & Legali #Shorts"
        header = f"🏢 {titolo.upper()} — PILLOLE IMMOBILIARI & LEGALI CON DARIA 🏢"
        hashtags = "#Shorts #ImmobiliareGiancani #PilloleImmobiliari #ConsulenzaLegale #Favara #Agrigento #DarIA #AntonioGiancani"
    elif "standard" in m_lower or "gatto" in m_lower or "libri" in m_lower:
        short_title = f"{titolo} | Il Gatto Racconta i Grandi Classici #Shorts"
        header = f"🐱 {titolo.upper()} — I GRANDI LIBRI CLASSICI RACCONTATI DAL GATTO 🐱"
        hashtags = "#Shorts #GrandiClassici #Libri #GattoNarratore #Cultura #ImmobiliareGiancani #AntonioGiancani"
    else:
        short_title = f"{titolo} | Immobiliare Giancani con DarIA #Shorts"
        header = f"🏠 {titolo.upper()} — IMMOBILIARE GIANCANI CON DARIA 🏠"
        hashtags = "#Shorts #ImmobiliareGiancani #DarIA #CaseInVendita #Favara #Agrigento #AntonioGiancani"

    # Troncamento titolo se supera i 100 caratteri (limite max di YouTube)
    if len(short_title) > 95:
        short_title = short_title[:90] + " #Shorts"

    description = (
        f"{header}\n\n"
        f"📜 Narrazione Ufficiale (Colonna F):\n"
        f"«{colonna_f}»\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 Produzione, Strategia e Personal Branding:\n"
        f"🏠 IMMOBILIARE GIANCANI — Favara (Agrigento)\n"
        f"🌐 Sito Web Ufficiale: https://immobiliaregiancani.it\n"
        f"👤 A cura di Antonio Giancani\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{hashtags}"
    )

    tags = list(config["default_tags"])
    tags.append(titolo)

    payload = {
        "channel_target": config["nome_canale"],
        "mode": mode_key,
        "story_id": storia_id,
        "video_file": os.path.basename(video_path),
        "video_path": os.path.abspath(video_path),
        "snippet": {
            "title": short_title,
            "description": description,
            "tags": tags,
            "categoryId": "27",  # Education / Cultura
            "defaultLanguage": "it"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        },
        "generated_at": datetime.datetime.now().isoformat()
    }

    out_json = os.path.join(OUTPUT_DIR, f"youtube_metadata_{mode_key}_{storia_id}.json")
    with open(out_json, "w", encoding="utf-8") as jf:
        json.dump(payload, jf, ensure_ascii=False, indent=2)

    print(f"\n📺 [YOUTUBE SHORTS INTEGRATION] Metadati generati per {config['nome_canale']}:")
    print(f"  📌 Titolo: {short_title}")
    print(f"  📄 File Metadati salvato in: {os.path.basename(out_json)}")
    return payload, out_json


SCOPES_YOUTUBE = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]


def ottieni_credenziali_youtube(mode="mitologia", interactive=False):
    """
    Recupera credenziali OAuth2 valide per il canale specificato:
    1. Da variabile d'ambiente (GitHub Actions Secrets: YOUTUBE_TOKEN_GIANCANI_JSON o YOUTUBE_TOKEN_*)
    2. Da file token locale (token_youtube_giancani.json, token_youtube.json, etc.) con auto-refresh
    3. Se interactive=True o credenziali mancanti, avvia il flusso browser locale
    """
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    m_lower = mode.lower()
    if "mitologia" in m_lower:
        mode_key = "mitologia"
    elif "bibbia" in m_lower:
        mode_key = "bibbia"
    else:
        mode_key = "giancani"

    config = CANALI_YOUTUBE.get(mode_key, CANALI_YOUTUBE["giancani"])
    token_file = config["token_file"]
    cred_file = config["cred_file"]
    env_token_var = f"YOUTUBE_TOKEN_{mode_key.upper()}_JSON"

    creds = None

    # 1. Da variabile d'ambiente (GitHub Actions)
    candidates_env = [env_token_var, "YOUTUBE_TOKEN_GIANCANI_JSON", "YOUTUBE_TOKEN_MITOLOGIA_JSON", "YOUTUBE_TOKEN_JSON"]
    for ev in candidates_env:
        if os.environ.get(ev):
            try:
                token_data = json.loads(os.environ[ev])
                creds = Credentials.from_authorized_user_info(token_data, SCOPES_YOUTUBE)
                if creds and creds.valid:
                    break
            except Exception as e_env:
                print(f"  ⚠️ Warning parsing token da env {ev}: {e_env}")

    # 2. Da file token su disco con fallback a token_youtube_giancani.json / token_youtube.json
    if not creds:
        candidate_files = [
            token_file,
            os.path.join(BASE_DIR, "token_youtube_giancani.json"),
            os.path.join(BASE_DIR, "token_youtube.json"),
            os.path.join(BASE_DIR, "token_youtube_mitologia.json"),
            os.path.join(BASE_DIR, "diretta_live_project", "token_youtube.json")
        ]
        for cf in candidate_files:
            if os.path.exists(cf) and os.path.getsize(cf) > 100:
                try:
                    creds = Credentials.from_authorized_user_file(cf, SCOPES_YOUTUBE)
                    token_file = cf
                    break
                except Exception as e_f:
                    print(f"  ⚠️ Warning lettura token file {cf}: {e_f}")

    # 3. Refresh automatico se scaduto
    if creds:
        if creds.expired and creds.refresh_token:
            try:
                print(f"  🔄 Aggiornamento token OAuth per {config['nome_canale']}...")
                creds.refresh(Request())
                with open(token_file, "w", encoding="utf-8") as tf:
                    tf.write(creds.to_json())
                print("  ✅ Token aggiornato e salvato con successo.")
            except Exception as e_ref:
                print(f"  ⚠️ Errore refresh token: {e_ref}")
                creds = None

    # 4. Flusso interattivo di autorizzazione iniziale (browser)
    if (not creds or not creds.valid) and (interactive or not os.path.exists(token_file)):
        if os.path.exists(cred_file):
            try:
                from google_auth_oauthlib.flow import InstalledAppFlow
                print("\n" + "="*70, flush=True)
                print(f"🔑 [AUTORIZZAZIONE YOUTUBE] Collegamento: {config['nome_canale']}", flush=True)
                print("Si apre il browser per accedere con l'account Google associato al canale.", flush=True)
                print("="*70 + "\n", flush=True)
                flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES_YOUTUBE)
                creds = flow.run_local_server(
                    port=0,
                    prompt="consent",
                    access_type="offline",
                    authorization_prompt_message="👉 Apri questo link per autorizzare l'accesso a YouTube:\n{url}\n\nIn attesa di autorizzazione...\n"
                )
                with open(token_file, "w", encoding="utf-8") as tf:
                    tf.write(creds.to_json())
                print(f"\n✅ [SUCCESSO] Canale «{config['nome_canale']}» collegato con successo!", flush=True)
                print(f"💾 File di autenticazione salvato in: {os.path.basename(token_file)}\n", flush=True)
            except Exception as e_flow:
                print(f"  ❌ Errore durante l'autorizzazione OAuth: {e_flow}", flush=True)
                return None
        else:
            print(f"  ⚠️ File credenziali client non trovato: {cred_file}")

    return creds if (creds and creds.valid) else None


def pubblica_video_youtube(video_path, metadata_payload, mode="mitologia"):
    """
    Effettua l'upload effettivo del video tramite YouTube Data API v3 se configurato,
    oppure predispone il pacchetto pronto per caricamento istantaneo.
    """
    m_lower = mode.lower()
    if "mitologia" in m_lower:
        mode_key = "mitologia"
    elif "bibbia" in m_lower:
        mode_key = "bibbia"
    else:
        mode_key = "giancani"
    config = CANALI_YOUTUBE.get(mode_key, CANALI_YOUTUBE["giancani"])
    
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        creds = ottieni_credenziali_youtube(mode=mode_key, interactive=False)

        if creds and creds.valid:
            import google_auth_httplib2
            import httplib2
            http_client = httplib2.Http(disable_ssl_certificate_validation=True)
            auth_http = google_auth_httplib2.AuthorizedHttp(creds, http=http_client)
            youtube = build("youtube", "v3", http=auth_http)
            body = {
                "snippet": metadata_payload["snippet"],
                "status": metadata_payload["status"]
            }
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
            print(f"\n🚀 [YouTube API] Upload in corso su {config['nome_canale']}...")
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = request.execute()
            yt_video_id = response.get("id")
            yt_url = f"https://youtube.com/shorts/{yt_video_id}"
            print(f"  ✅ [YouTube Shorts] Pubblicato con successo! URL: {yt_url}")
            return yt_url
        else:
            print(f"  ℹ️ [YouTube Shorts] Per attivare l'upload diretto su «{config['nome_canale']}», avvia una volta 'python collega_canale_youtube.py'.")
    except Exception as e_yt:
        print(f"  ⚠️ Warning connessione diretta YouTube Data API: {e_yt}")

    print(f"  ℹ️ [YouTube Shorts] Canale «{config['nome_canale']}»: pacchetto metadati e video 9:16 (<60s) pronto e registrato!")
    return None
