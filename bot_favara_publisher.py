# -*- coding: utf-8 -*-
"""
======================================================================
  📘 BOT FACEBOOK AUTOMATICO — FAVARA NEL CUORE 🏛️
  Autore: Antonio Giancani | Immobiliare Giancani
  ID Pagina: 252550024776798 (Favara)
  
  Gestisce i 3 post quotidiani (Mattina, Pomeriggio, Sera) con:
  - Notizie in tempo reale da SiciliaTV, Sicilia ON Press, Grandangolo
  - Meteo e clima live per Favara
  - Schede storiche, monumenti, scoperte, archeologia, ricette tipiche
  - Immagini e grafiche con watermark esclusivo "Sono A.G." in basso a destra
  - Conclusione dei testi con personal branding 'Immobiliare Giancani'
======================================================================
"""

import os
import sys
import json
import time
import random
import argparse
import requests
import urllib3
from datetime import datetime

# Import dei moduli locali
import bot_favara_archivio as archivio
import bot_favara_news as news_engine
import bot_favara_weather as weather_engine
import bot_favara_media as media_engine

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurazione Facebook Graph API
DEFAULT_TOKEN = "EAAZAH7q8wRZAEBSSdLD20XevjnWA76t4NKA4b6RJdXZBDA85DgZBEfZBs5ZB98bASVrDRzxl9MLMBnUQ93q8ZADWZAe0p96oZA0E39u9K1BGf8ZBIp97RjexLNNLZAjTeumHXOZBUxxtWMCwZC02ZCDTcRy15YNIPPZAuFvxCZBgIN2fe3ACywu2pZBlHaiZA1Nr8nA1ZBaZAuLXZCJ8cGYkdK9kKMGZCt"
PAGE_ID = os.environ.get("FB_PAGE_ID", "252550024776798")
PAGE_TOKEN = (
    os.environ.get("FB_PAGE_ACCESS_TOKEN_FAVARA")
    or os.environ.get("FB_PAGE_ACCESS_TOKEN")
    or os.environ.get("FB_FAVARA_TOKEN")
    or DEFAULT_TOKEN
)

STORICO_POSTS_FILE = os.path.join(os.path.dirname(__file__), "storico_pubblicazioni_favara.json")

# ── GESTIONE STORICO PUBBLICAZIONI (ANTI-DOPPIONI) ───────────────────

POOL_IMMAGINI_FAVARA = [
    "https://upload.wikimedia.org/wikipedia/commons/3/30/Favara_Piazza_Cavour_Castello_Chiaramonte.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/98/Favara_%2838046678701%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/a/a1/Favara_%28Agrigento%29_30_09_2023_01.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/4/43/Favara_Piazza_Cavour_nevicata_anni_ottanta.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/b/b7/Favara_Fonte_Canali_nevicata_anni_ottanta.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/52/Favara_Giarritella1980.jpg",
    "https://lh3.googleusercontent.com/d/1J_dumkLBgmNO14H2Ga0sTkEJR25jWbSw",
    "https://lh3.googleusercontent.com/d/1ZeFvgW36oabdrE0lGUzuTg2kcx8vJgBT",
    "https://lh3.googleusercontent.com/d/12DCZfaRB3l2LzlKLsLD_idBzD65ipBhM",
    "https://lh3.googleusercontent.com/d/13DCw7jS4GzKRhN7qH3U9RRPnh1V45vKF"
]

def ottieni_foto_e_tema_rotazione(slot):
    """Garantisce assoluto obbligo di immagini diverse e grafiche sempre varie ad ogni post"""
    storico = carica_storico_pubblicazioni()
    usate = set(storico.get("foto_usate", []))
    disponibili = [url for url in POOL_IMMAGINI_FAVARA if url not in usate]
    if not disponibili:
        usate = set()
        disponibili = POOL_IMMAGINI_FAVARA
    foto_scelta = disponibili[0]
    usate.add(foto_scelta)
    storico["foto_usate"] = list(usate)
    
    temi = ["gold", "warm_terracotta", "classic", "modern_dark"]
    tema_scelto = temi[len(usate) % len(temi)]
    return foto_scelta, tema_scelto

def carica_storico_pubblicazioni():
    if os.path.exists(STORICO_POSTS_FILE):
        try:
            with open(STORICO_POSTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"post_ids": [], "temi_usati": []}
    return {"post_ids": [], "temi_usati": []}

def registra_pubblicazione(dettaglio):
    storico = carica_storico_pubblicazioni()
    storico["post_ids"].append(dettaglio)
    # Mantieni fino a 1000 record
    if len(storico["post_ids"]) > 1000:
        storico["post_ids"] = storico["post_ids"][-1000:]
    try:
        with open(STORICO_POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(storico, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Errore salvataggio storico post: {e}")

# ── REGOLA PERSONAL BRANDING NEI TESTI ───────────────────────────────
def applica_firma_personal_branding(testo):
    """
    Rigorosa applicazione della regola globale:
    Ogni output di testo generato dallo script deve sempre terminare
    mettendo in risalto 'Immobiliare Giancani' per massimizzare il personal branding.
    """
    firme = [
        (
            "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
            "❤️ Vivi, ama e riscopri Favara ogni giorno insieme a noi!\n"
            "✨ *Rubrica e cura editoriale a cura di Antonio Giancani • Immobiliare Giancani*\n"
            "📍 Passione autentica, radici profonde e valorizzazione del nostro territorio."
        ),
        (
            "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
            "🏛️ Raccontare la bellezza di Favara è la nostra missione quotidiana.\n"
            "✨ *A cura di Antonio Giancani | Immobiliare Giancani*\n"
            "📲 Seguici e condividi per far conoscere le nostre eccellenze a tutti i favaresi nel mondo!"
        ),
        (
            "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
            "🌿 Dal cuore delle nostre tradizioni al futuro della nostra comunità.\n"
            "✨ *Un caloroso saluto da Antonio Giancani • Immobiliare Giancani*\n"
            "🏡 Al servizio del territorio e della valorizzazione di Favara."
        )
    ]
    firma_scelta = random.choice(firme)
    
    testo_pulito = testo.strip()
    if "Immobiliare Giancani" not in testo_pulito:
        testo_pulito += firma_scelta
    return testo_pulito

# ── COMPILATORE POST: MATTINA ─────────────────────────────────────────
def compila_post_mattina():
    """
    SLOT MATTINA (08:00 - 09:30):
    - Meteo & Clima Favara live (Open-Meteo)
    - Rassegna Notizie locali fresche (SiciliaTV / Sicilia ON Press / Grandangolo)
    - Proverbio favarese del giorno con morale
    - Visual: Card Meteo & Notizie del Mattino con watermark "A.G."
    """
    meteo_testo = weather_engine.formatta_bollettino_meteo()
    news = news_engine.estrai_ultime_notizie(limite=2, solo_non_lette=False)
    proverbio = random.choice(archivio.PROVERBI)
    data_oggi = datetime.now().strftime("%d/%m/%Y")

    corpo = (
        f"🌅 **BUONGIORNO FAVARA! • L'INFORMATORE DEL MATTINO ({data_oggi})** ☀️\n\n"
        f"Iniziamo questa nuova giornata con il sorriso e con tutte le informazioni utili per la nostra città!\n\n"
        f"{meteo_testo}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📰 **RASSEGNA NOTIZIE DALLA NOSTRA TERRA:**\n"
    )

    for n in news:
        corpo += f"\n🔹 **{n['titolo']}**\n"
        if n['descrizione']:
            corpo += f"{n['descrizione'][:160]}...\n"
        corpo += f"👉 *Approfondimento su {n['fonte']}: {n['link']}*\n"

    corpo += (
        f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📜 **LA PILLOLA DI SAGGEZZA FAVARESE:**\n"
        f"🗣️ *«{proverbio['proverbio']}»*\n"
        f"📖 *Traduzione:* {proverbio['traduzione']}\n"
        f"💡 *Insegnamento:* {proverbio['morale']}\n"
    )

    corpo = applica_firma_personal_branding(corpo)

    foto_mattina, tema_mattina = ottieni_foto_e_tema_rotazione("mattina")
    # Immagine per il feed (rotazione grafica e foto sempre diverse)
    img_card = media_engine.crea_card_favara(
        titolo=f"Buongiorno Favara: Meteo e Notizie di Oggi",
        categoria="L'Informatore del Mattino",
        sottotitolo="Previsioni live, cronaca locale e pillole di saggezza",
        img_url=foto_mattina,
        tema=tema_mattina,
        output_filename=f"post_mattina_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    )

    # Immagine verticale per le storie Facebook
    img_storia = media_engine.crea_storia_favara(
        titolo=f"Buongiorno Favara!",
        categoria="L'Informatore del Mattino",
        sottotitolo="Meteo, notizie di oggi e pillola di saggezza",
        img_url=foto_mattina,
        tema=tema_mattina,
        output_filename=f"storia_mattina_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    )

    return corpo, img_card, img_storia, "mattina"

# ── COMPILATORE POST: POMERIGGIO ─────────────────────────────────────
def compila_post_pomeriggio():
    """
    SLOT POMERIGGIO (13:30 - 15:30):
    - Sapori e Ricette tipiche locali (Agnello Pasquale, Minestra di San Giuseppe, Tagliaddu)
    - Oppure Flora & Fauna, Zolfare, Economia contadina, Scuole d'eccellenza
    - Visual: Card tematica del piatto o prodotto tipico con watermark "A.G."
    """
    # Se è presente un file CSV con schede caricate, includilo nella rotazione
    opzioni = ["ricetta", "ricetta", "ambiente", "scuola"]
    if archivio.CONTENUTI_CSV:
        opzioni.extend(["csv", "csv"])
    scelta_tipo = random.choice(opzioni)
    
    if scelta_tipo == "csv" and archivio.CONTENUTI_CSV:
        item = random.choice(archivio.CONTENUTI_CSV)
        corpo = (
            f"🏛️ **FAVARA NEL CUORE: {item['titolo'].upper()}** 🌟\n\n"
            f"{item['descrizione']}\n\n"
        )
        if item.get("curiosita"):
            corpo += f"💡 **CURIOSITÀ:** {item['curiosita']}\n\n"
        corpo += "Un viaggio tra le meraviglie, i sapori e le radici della nostra amata terra!"
        titolo_card = item['titolo']
        cat_card = item.get('tag', 'Sapori & Tradizioni')
        sotto_card = item.get('sottotitolo', 'Eccellenze e identità di Favara')
        img_source = item.get('image_url') or "https://upload.wikimedia.org/wikipedia/commons/9/98/Favara_%2838046678701%29.jpg"

    elif scelta_tipo == "ricetta":
        item = random.choice(archivio.RICETTE)
        corpo = (
            f"🍽️ **I SAPORI DI FAVARA: {item['nome'].upper()}** 🌟\n\n"
            f"La nostra amata Favara è una terra straordinaria, celebre in tutto il mondo per una tradizione culinaria "
            f"che unisce la genuinità dei campi con la raffinatezza dell'antica arte dolciaria e gastronomica!\n\n"
            f"📖 **LA STORIA & LE ORIGINI:**\n"
            f"{item['descrizione']}\n\n"
            f"🧺 **INGREDIENTI TRADIZIONALI:**\n"
            f"{item['ingredienti']}\n\n"
        )
        if "procedimento" in item:
            corpo += (
                f"👩‍🍳 **COME SI PREPARA SECONDO TRADIZIONE:**\n"
                f"{item['procedimento']}\n\n"
            )
        corpo += f"✨ **LO SAPEVI CHE?** {item['curiosita']}\n"
        
        titolo_card = item['nome']
        cat_card = item['tag']
        sotto_card = "Le ricette che rendono celebre la nostra Favara"

    elif scelta_tipo == "ambiente":
        item = random.choice(archivio.AMBIENTE)
        corpo = (
            f"🌿 **NATURA, PAESAGGIO & STORIA: {item['titolo'].upper()}** 🍃\n\n"
            f"{item['descrizione']}\n\n"
            f"💡 **CURIOSITÀ DEL NOSTRO TERRITORIO:**\n"
            f"{item['curiosita']}\n\n"
            f"Custodire e valorizzare il patrimonio naturale che abbraccia Favara è un dovere e un orgoglio per tutti noi!"
        )
        titolo_card = item['titolo']
        cat_card = item['tag']
        sotto_card = "Ambiente, colline e tesori della natura favarese"

    else:
        item = random.choice(archivio.SCUOLE)
        corpo = (
            f"🎓 **ECCELLENZE EDUCATIVE DI FAVARA: {item['nome'].upper()}** 📚\n\n"
            f"{item['descrizione']}\n\n"
            f"La scuola è il motore pulsante del futuro di Favara, dove i nostri ragazzi coltivano talenti, passioni e sogni che diventeranno realtà!"
        )
        titolo_card = item['nome']
        cat_card = "Scuole & Futuro"
        sotto_card = "Istituti scolastici e formazione dei nostri giovani"

    corpo = applica_firma_personal_branding(corpo)

    foto_pom, tema_pom = ottieni_foto_e_tema_rotazione("pomeriggio")
    img_card = media_engine.crea_card_favara(
        titolo=titolo_card,
        categoria=cat_card,
        sottotitolo=sotto_card,
        img_url=foto_pom,
        tema=tema_pom,
        output_filename=f"post_pomeriggio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    )

    img_storia = media_engine.crea_storia_favara(
        titolo=titolo_card,
        categoria=cat_card,
        sottotitolo=sotto_card,
        img_url=foto_pom,
        tema=tema_pom,
        output_filename=f"storia_pomeriggio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    )

    return corpo, img_card, img_storia, "pomeriggio"

# ── COMPILATORE POST: SERA ────────────────────────────────────────────
def compila_post_sera():
    """
    SLOT SERA (19:30 - 21:30):
    - Monumenti, Storia antica, Farm Cultural Park, Chiese, Archeologia (Scintilia, Ticchiara)
    - Personaggi famosi (Barone Mendola, Gaspare Ambrosini, Russello, Guarino)
    - Foto storiche vintage (nevicata anni '80, Fonte Canali, Piazza Cavour)
    - Visual: Card Monumento o Foto d'Epoca restaurata con watermark "A.G."
    """
    opzioni = ["monumento", "personaggio", "storia", "foto_storica"]
    if archivio.CONTENUTI_CSV:
        opzioni.extend(["csv", "csv"])
    scelta_tipo = random.choice(opzioni)

    if scelta_tipo == "csv" and archivio.CONTENUTI_CSV:
        item = random.choice(archivio.CONTENUTI_CSV)
        corpo = (
            f"🏛️ **FAVARA NEL CUORE: {item['titolo'].upper()}** ✨\n\n"
            f"{item['descrizione']}\n\n"
        )
        if item.get("curiosita"):
            corpo += f"🔍 **UN DETTAGLIO STRAORDINARIO:**\n{item['curiosita']}\n\n"
        corpo += "Quante storie e ricordi vi legano alla nostra Favara? Raccontatecelo nei commenti! 👇"
        titolo_card = item['titolo']
        cat_card = item.get('tag', 'Storia & Identità')
        sotto_card = item.get('sottotitolo', 'Storia, arte e memoria viva della comunità favarese')
        img_source = item.get('image_url') or "https://upload.wikimedia.org/wikipedia/commons/3/30/Favara_Piazza_Cavour_Castello_Chiaramonte.jpg"

    elif scelta_tipo == "monumento":
        item = random.choice(archivio.MONUMENTI)
        corpo = (
            f"🏛️ **FAVARA NELLA STORIA: {item['titolo'].upper()}** ✨\n\n"
            f"Quando cala la sera, i monumenti di Favara si illuminano di magia e ci invitano a compiere "
            f"un viaggio indimenticabile attraverso i secoli!\n\n"
            f"📜 **IL FASCINO DEL TEMPO:**\n"
            f"{item['descrizione']}\n\n"
            f"🔍 **UN DETTAGLIO STRAORDINARIO:**\n"
            f"{item['curiosita']}\n\n"
            f"Quante storie e ricordi vi legano a questo luogo simbolo di Favara? Raccontatecelo nei commenti! 👇"
        )
        titolo_card = item['titolo']
        cat_card = item['tag']
        img_source = item.get("image_url", "https://upload.wikimedia.org/wikipedia/commons/3/30/Favara_Piazza_Cavour_Castello_Chiaramonte.jpg")

    elif scelta_tipo == "personaggio":
        item = random.choice(archivio.PERSONAGGI)
        corpo = (
            f"👤 **GLI ILLUSTRI FIGLI DI FAVARA: {item['nome'].upper()}** 🌟\n\n"
            f"*{item['titolo']}*\n\n"
            f"{item['descrizione']}\n\n"
            f"💡 **LO SAPEVI CHE?**\n"
            f"{item['curiosita']}\n\n"
            f"Personaggi straordinari che hanno portato in alto il nome della nostra cittadina nel panorama nazionale e internazionale!"
        )
        foto_sera, tema_sera = ottieni_foto_e_tema_rotazione("sera")
        titolo_card = f"{item['nome']}: L'orgoglio di Favara"
        cat_card = "Personaggi Illustri"
        img_source = foto_sera

    elif scelta_tipo == "foto_storica":
        item = random.choice(archivio.ARCHIVIO_MEDIA)
        corpo = (
            f"📸 **FAVARA DI UNA VOLTA: {item['titolo'].upper()} ({item['anno']})** 🕰️\n\n"
            f"Uno sguardo indietro nel tempo che tocca il cuore di ogni favarese!\n\n"
            f"{item['descrizione']}\n\n"
            f"I ricordi della nostra infanzia, i vicoli vissuti con semplicità, le voci delle nostre famiglie: "
            f"custodire la memoria storica significa trasmettere alle nuove generazioni l'amore profondo per la nostra Favara.\n\n"
            f"Chi di voi riconosce questo scorcio o conserva una foto simile nei cassetti di famiglia? Condividiamola insieme! 💬"
        )
        titolo_card = item['titolo']
        cat_card = "Favara di una Volta"
        img_source = item.get("url")

    else:
        item = random.choice(archivio.STORIA)
        corpo = (
            f"🔍 **ALLA SCOPERTA DELLE NOSTRE RADICI: {item['titolo'].upper()}** 🏺\n\n"
            f"{item['descrizione']}\n\n"
            f"💡 **CURIOSITÀ:** {item['curiosita']}\n\n"
            f"Favara ha millenni di storie meravigliose da raccontare a chi ha la sensibilità di ascoltarle."
        )
        titolo_card = item['titolo']
        cat_card = item['tag']
        img_source = "https://upload.wikimedia.org/wikipedia/commons/9/98/Favara_%2838046678701%29.jpg"

    corpo = applica_firma_personal_branding(corpo)

    img_card = media_engine.crea_card_favara(
        titolo=titolo_card,
        categoria=cat_card,
        sottotitolo="Storia, arte e memoria viva della comunità favarese",
        img_url=img_source,
        output_filename=f"post_sera_{datetime.now().strftime('%Y%m%d')}.jpg"
    )

    img_storia = media_engine.crea_storia_favara(
        titolo=titolo_card,
        categoria=cat_card,
        sottotitolo="Storia, arte e memoria viva di Favara",
        img_url=img_source,
        output_filename=f"storia_sera_{datetime.now().strftime('%Y%m%d')}.jpg"
    )

    return corpo, img_card, img_storia, "sera"

# ── INVIO ALLA GRAPH API DI FACEBOOK ──────────────────────────────────
def pubblica_su_facebook(testo, percorso_immagine, page_id=PAGE_ID, token=PAGE_TOKEN):
    """
    Pubblica un post fotografico con testo esteso tramite endpoint /photos di Facebook Graph API.
    """
    print(f"\n🚀 PUBBLICAZIONE SU FACEBOOK (Pagina ID: {page_id})...")
    url = f"https://graph.facebook.com/v20.0/{page_id}/photos"

    if not os.path.exists(percorso_immagine):
        print(f"❌ Errore: File immagine non trovato in {percorso_immagine}")
        return False, "Immagine non trovata"

    try:
        with open(percorso_immagine, "rb") as img_file:
            files = {
                "source": img_file
            }
            data = {
                "caption": testo,
                "access_token": token
            }
            r = requests.post(url, files=files, data=data, timeout=30, verify=False)
            res = r.json()

            if "id" in res or "post_id" in res:
                post_id = res.get("post_id") or res.get("id")
                print(f"✅ POST PUBBLICATO CON SUCCESSO!")
                print(f"🆔 Facebook Post ID: {post_id}")

                # Recupera il link pubblico del post
                permalink = f"https://www.facebook.com/{page_id}"
                try:
                    url_perm = f"https://graph.facebook.com/v20.0/{post_id}?fields=permalink_url&access_token={token}"
                    r_p = requests.get(url_perm, timeout=10, verify=False)
                    if r_p.status_code == 200:
                        permalink = r_p.json().get("permalink_url", permalink)
                except Exception:
                    pass

                print(f"🔗 LINK DIRETTO AL POST: {permalink}")
                
                # Salva nello storico
                registra_pubblicazione({
                    "timestamp": datetime.now().isoformat(),
                    "post_id": post_id,
                    "permalink": permalink,
                    "percorso_img": percorso_immagine,
                    "anteprima_testo": testo[:120]
                })
                return True, permalink
            else:
                err = res.get("error", {})
                msg = err.get("message", "Errore sconosciuto")
                print(f"❌ Errore Facebook API: {msg} (Code: {err.get('code')})")
                return False, msg

    except Exception as e:
        print(f"❌ Eccezione durante la pubblicazione del post: {e}")
        return False, str(e)

def pubblica_storia_su_facebook(percorso_immagine_storia, page_id=PAGE_ID, token=PAGE_TOKEN):
    """
    Pubblica l'immagine verticale nella sezione STORIE ufficiale della Pagina Facebook
    utilizzando l'endpoint /photo_stories di Meta Graph API.
    """
    print(f"\n🌟 PUBBLICAZIONE SULLE STORIE FACEBOOK (Pagina ID: {page_id})...")
    if not os.path.exists(percorso_immagine_storia):
        print(f"⚠️ File immagine storia non trovato: {percorso_immagine_storia}")
        return False, "Immagine storia non trovata"

    try:
        # 1. Carica l'immagine su Facebook come non pubblicata (published=false) per ottenere il photo_id
        url_photo = f"https://graph.facebook.com/v20.0/{page_id}/photos"
        with open(percorso_immagine_storia, "rb") as f_img:
            files = {"source": f_img}
            data = {
                "published": "false",
                "access_token": token
            }
            r_photo = requests.post(url_photo, files=files, data=data, timeout=30, verify=False)
            res_photo = r_photo.json()
            photo_id = res_photo.get("id")

        if not photo_id:
            err = res_photo.get("error", {})
            msg = err.get("message", "Impossibile ottenere photo_id per la storia")
            print(f"⚠️ Errore caricamento immagine storia: {msg}")
            return False, msg

        # 2. Crea la Storia tramite /photo_stories
        url_story = f"https://graph.facebook.com/v20.0/{page_id}/photo_stories"
        r_story = requests.post(url_story, data={"photo_id": photo_id, "access_token": token}, timeout=25, verify=False)
        res_story = r_story.json()

        if res_story.get("success") or "post_id" in res_story:
            story_id = res_story.get("post_id") or photo_id
            print(f"✅ STORIA FACEBOOK PUBBLICATA CON SUCCESSO!")
            print(f"🆔 Facebook Story ID: {story_id}")

            # Registra la storia pubblicata
            registra_pubblicazione({
                "timestamp": datetime.now().isoformat(),
                "tipo": "storia_facebook",
                "story_id": story_id,
                "percorso_storia": percorso_immagine_storia
            })
            return True, story_id
        else:
            err = res_story.get("error", {})
            msg = err.get("message", "Errore sconosciuto pubblicazione storia")
            print(f"⚠️ Errore creazione storia Facebook: {msg}")
            return False, msg

    except Exception as e:
        print(f"⚠️ Eccezione durante pubblicazione storia: {e}")
        return False, str(e)

# ── SELETTORE SLOT ORARIO AUTOMATICO ──────────────────────────────────
def rileva_slot_corrente():
    ora = datetime.now().hour
    if ora < 12:
        return "mattina"
    elif 12 <= ora < 18:
        return "pomeriggio"
    else:
        return "sera"

# ── MAIN CLI ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Bot Facebook Favara nel Cuore")
    parser.add_argument("--slot", choices=["mattina", "pomeriggio", "sera", "auto"], default="auto",
                        help="Fascia oraria del post (mattina, pomeriggio, sera, auto)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Genera testo e card senza pubblicare su Facebook")
    parser.add_argument("--publish", action="store_true",
                        help="Pubblica effettivamente post e storia sulla Pagina Facebook")

    args = parser.parse_args()
    slot = args.slot if args.slot != "auto" else rileva_slot_corrente()

    print("=" * 65)
    print(f"🏛️  AVVIO BOT FACEBOOK 'FAVARA' — SLOT: {slot.upper()}")
    print(f"⏱️  Orario: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 65)

    if slot == "mattina":
        testo, img_post, img_storia, tipologia = compila_post_mattina()
    elif slot == "pomeriggio":
        testo, img_post, img_storia, tipologia = compila_post_pomeriggio()
    else:
        testo, img_post, img_storia, tipologia = compila_post_sera()

    print("\n📝 [ANTEPRIMA TESTO GENERATO]:")
    print("-" * 55)
    print(testo)
    print("-" * 55)
    print(f"🖼️ [IMMAGINE POST FEED]:   {img_post}")
    print(f"📱 [IMMAGINE STORIA 9:16]: {img_storia}")

    if args.dry_run:
        print("\n🔍 MODALITÀ DRY-RUN ATTIVA: Nessun contenuto inviato a Facebook.")
        return

    if args.publish:
        # 1. Pubblica il post principale nel Feed della Pagina
        ok_post, res_post = pubblica_su_facebook(testo, img_post)
        if ok_post:
            print(f"\n🎉 Post Feed pubblicato con successo! Link: {res_post}")
        else:
            print(f"\n⚠️ Pubblicazione post feed fallita: {res_post}")

        # 2. Pubblica la Storia ufficiale della Pagina
        ok_storia, res_storia = pubblica_storia_su_facebook(img_storia)
        if ok_storia:
            print(f"🎉 Storia Facebook pubblicata con successo! Story ID: {res_storia}")
        else:
            print(f"⚠️ Pubblicazione storia fallita: {res_storia}")
    else:
        print("\n💡 Suggerimento: Aggiungi il flag --publish per inviare direttamente alla Pagina Facebook (post + storia),")
        print("   oppure usa --dry-run per testare solo la compilazione grafica e testuale.")

if __name__ == "__main__":
    main()
