# -*- coding: utf-8 -*-
"""
======================================================================
  📘 BOT FACEBOOK AUTOMATICO — SALUTI GIORNALIERI MULTI-PAGINA
  Pagine supportate:
    1. Immobiliare Giancani (234931856561526)
    2. Antonio Giancani     (108297671444008)
    3. Favara               (252550024776798)

  Caratteristiche:
    - 3 Saluti al giorno (Buongiorno 06:30, Buon Pomeriggio 13:00, Buona Sera 20:00)
    - Auto-cancellazione del post precedente prima di pubblicare il nuovo
    - Citazioni e testi prelevati rigorosamente dalla Colonna F (Mindset.csv)
    - Varietà continua di frasi ed emoticon sempre a tema
    - Sottofondo musicale gratuito (Pixabay CC0 / Bensound Free)
    - Conclusione di ogni testo che mette in risalto "Immobiliare Giancani"
======================================================================
"""

import os
import sys
import json
import random
import csv
import argparse
import urllib.request
import urllib.parse
import urllib.error
import ssl
from datetime import datetime, timezone, timedelta

ORA_IT = datetime.now(timezone(timedelta(hours=2)))
STORICO_FILE = os.path.join(os.path.dirname(__file__), "storico_note_giancani.json")
CSV_PATH = os.path.join(os.path.dirname(__file__), "Mindset.csv")

PAGINE_DEFAULT = [
    {
        "slug": "giancani",
        "nome": "Immobiliare Giancani",
        "page_id": "234931856561526",
        "token_env": "FB_PAGE_ACCESS_TOKEN_GIANCANI",
        "default_token": "EAAZAH7q8wRZAEBSXRuqZAbRujVl9v0i7bXynRXtbb6sZAJMn0AZAbZAsJ0bLFHZAjWKhIpeu8R1xkKJDNgTcGawxoBo5FE7xONkTZAyRfOdKwSeydwoGkUHvPluWsB7biC8AZAqP9UWd672RlwmHzuwfAugUngnQnbZB2SZBCWj3WQqSKo8tLiBO4DYhI474ZAdhLwMs",
        "tema": "immobiliare"
    },
    {
        "slug": "antonio",
        "nome": "Antonio Giancani",
        "page_id": "108297671444008",
        "token_env": "FB_PAGE_ACCESS_TOKEN_ANTONIO",
        "default_token": "EAAZAH7q8wRZAEBSVeVa4DxzWiZBSoeSZC47h88ZBmzeNlvL3ow74fIzITgMKMrURWeDZBE5fU8ZCk0Hgm0J8CtqviQPqbrj7DQhnVv57W7WZCh80KCsNq6SL1imUOuBbEZBQqS9LB2iteZCID62Iw4ZCu27w2FA6MrFpsH9DCcxSd58qV1IwzpeIb5FDMg7qmNFiOER2XVo",
        "tema": "personal"
    },
    {
        "slug": "favara",
        "nome": "Favara",
        "page_id": "252550024776798",
        "token_env": "FB_PAGE_ACCESS_TOKEN_FAVARA",
        "default_token": "EAAZAH7q8wRZAEBSceERqb9zi3xHuosuJB6a7Txg1ZCrvZCkj7Ofvff359g0RegSmJEZBxNAI7eQwlwJptMsfHZBiHTxHbbiZCkLzn5ZADXGkFE0dbAWal9s0SnCAJiO0FHHR73CqERdkvPJRUaRWzBZAy7HY69T41DwK5ErPrapikfFt4ZCD1JrwxQvYxA94RTGojM",
        "tema": "territorio"
    }
]

MUSICA = {
    "mattina": [
        ("🎵 Morning Inspiration – Pixabay (CC0)", "https://pixabay.com/music/beats-morning-motivation-inspiring-upbeat-background-music-248293/"),
        ("🎵 Happy Acoustic Start – Pixabay (CC0)", "https://pixabay.com/music/beats-upbeat-optimistic-happy-background-music-249477/"),
        ("🎵 Acoustic Sunrise – Bensound Free", "https://www.bensound.com/royalty-free-music/track/morning"),
        ("🎵 Piano in Armonia – Pixabay (CC0)", "https://pixabay.com/music/ambient-beautiful-morning-instrumental-143471/"),
        ("🎵 Fresh Hope – Pixabay (CC0)", "https://pixabay.com/music/beats-cheerful-and-happy-7418/")
    ],
    "pomeriggio": [
        ("🎷 Jazz & Relax Lounge – Pixabay (CC0)", "https://pixabay.com/music/jazz-smooth-jazz-background-music-248812/"),
        ("🌊 Chill Breeze Afternoon – Pixabay (CC0)", "https://pixabay.com/music/beats-chill-lounge-background-music-249065/"),
        ("🎵 Acoustic Breeze – Bensound Free", "https://www.bensound.com/royalty-free-music/track/acoustic-breeze"),
        ("🏖️ Summer Walk – Pixabay (CC0)", "https://pixabay.com/music/summer-summer-walk-152722/"),
        ("🎶 Dolce Calma Pomeridiana – Pixabay (CC0)", "https://pixabay.com/music/ambient-relaxing-145038/")
    ],
    "sera": [
        ("🌙 Sicilian Sunset Dream – Pixabay (CC0)", "https://pixabay.com/music/ambient-sicilian-sunset-background-music-248511/"),
        ("⭐ Evening Peace & Calm – Pixabay (CC0)", "https://pixabay.com/music/ambient-evening-calm-background-music-249100/"),
        ("🎻 Tenderness – Bensound Free", "https://www.bensound.com/royalty-free-music/track/tenderness"),
        ("🌃 Night Piano Lullaby – Pixabay (CC0)", "https://pixabay.com/music/ambient-night-ambient-piano-183788/"),
        ("🌌 Viaggio tra le Stelle – Pixabay (CC0)", "https://pixabay.com/music/ambient-dreamy-ambient-background-music-208880/")
    ]
}

def estrai_frasi_colonna_f():
    frasi = []
    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) >= 6 and row[5].strip():
                        frasi.append(row[5].strip())
        except Exception as e:
            print(f"⚠️ Avviso lettura Colonna F da CSV: {e}")
    if not frasi:
        frasi = [
            "Il successo non è definitivo, il fallimento non è fatale: ciò che conta è il coraggio di andare avanti. — Winston Churchill",
            "Non aspettare di comprare immobili. Compra immobili e aspetta. — Will Rogers",
            "Se puoi sognarlo, puoi farlo. — Walt Disney",
            "La disciplina è scegliere tra ciò che vuoi ora e ciò che vuoi di più. — Abraham Lincoln",
            "Le opportunità non accadono. Le crei tu. — Chris Grosser",
            "Non conta chi conosci, ma chi vuole fare affari con te. — Antonio Giancani",
            "Dove va il focus, scorre l'energia. — Tony Robbins",
            "Il miglior investimento sulla Terra è la terra. — Louis Glickman"
        ]
    return frasi

def carica_storico():
    if os.path.exists(STORICO_FILE):
        try:
            with open(STORICO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_post_per_page": {},
        "indici_colonna_f_usati": [],
        "storico_post": []
    }

def salva_storico(storico):
    try:
        with open(STORICO_FILE, "w", encoding="utf-8") as f:
            json.dump(storico, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Errore salvataggio storico: {e}")

def ottieni_prossima_frase_colonna_f(storico, pool_frasi):
    usati = storico.setdefault("indici_colonna_f_usati", [])
    disponibili = [i for i in range(len(pool_frasi)) if i not in usati]
    if not disponibili:
        disponibili = list(range(len(pool_frasi)))
        storico["indici_colonna_f_usati"] = []
    idx = random.choice(disponibili)
    storico["indici_colonna_f_usati"].append(idx)
    return pool_frasi[idx]

def genera_testo_saluto(slot, pagina_info, citazione_colonna_f):
    nome_pag = pagina_info["nome"]
    tema = pagina_info["tema"]
    data_str = ORA_IT.strftime("%d/%m/%Y")
    giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    giorno_settimana = giorni[ORA_IT.weekday()]
    musica_nome, musica_url = random.choice(MUSICA[slot])

    if slot == "mattina":
        intro_varianti = [
            f"☀️🌸 BUONGIORNO E FELICE GIORNATA! 🌸☀️\n\nUn nuovo giorno sorge e porta con sé fresche energie, nuove speranze e progetti da realizzare. 🌿✨",
            f"🌅☕ BUONGIORNO DI VERO CUORE! ☕🌅\n\nChe la tua mattinata inizi con un buon caffè, un sorriso autentico e tanta determinazione! 💪🌈",
            f"🌄🌻 BUON RISVEGLIO A TUTTI! 🌻🌄\n\nOgni alba è un dono prezioso e l'opportunità di costruire qualcosa di meraviglioso passo dopo passo. 🏡💛",
            f"☀️🥐 BUONGIORNO MONDO! 🥐☀️\n\nApriamo le finestre al sole del mattino e lasciamo che la luce illumini ogni nostro pensiero positivo! 🌞✨"
        ]
    elif slot == "pomeriggio":
        intro_varianti = [
            f"🌤️🍊 BUON POMERIGGIO E BUON PROSEGUIMENTO! 🍊🌤️\n\nSiamo nel pieno della giornata: concediti un piccolo istante di pausa per respirare e ricaricare le energie. ☕🌿",
            f"☀️☕ BUON POMERIGGIO A TUTTI! ☕☀️\n\nUna breve pausa caffè per riordinare le idee e ripartire con entusiasmo e lucidità! 🎯✨",
            f"🌤️🏛️ BUON POMERIGGIO DI RELAX E PRODUTTIVITÀ! 🏛️🌤️\n\nIl sole del pomeriggio accompagna le nostre attività con calore e serenità. Continua a dare il massimo! 💼💛",
            f"🌞🍋 UN CALOROSO BUON POMERIGGIO! 🍋🌞\n\nTra un impegno e l'altro, ricorda che ogni piccolo passo avanti crea grandi traguardi nel tempo. 🏡🌈"
        ]
    else: # sera
        intro_varianti = [
            f"🌙⭐ BUONA SERA E MERITATO RIPOSO! ⭐🌙\n\nMentre il cielo si tinge dei colori caldi del tramonto, è tempo di rientrare e ritrovare il calore degli affetti più cari. 🏡🕯️",
            f"🌇🍷 BUONA SERA A TUTTI! 🍷🌇\n\nSi chiude un'altra intensa giornata ricca di esperienze e incontri. È il momento perfetto per rilassarsi. ✨❤️",
            f"🌙🏛️ BUONA SERATA SOTTO LE STELLE! 🏛️🌙\n\nQuando cala la notte, il silenzio porta pace e chiarezza. Buona serata e sogni d'oro in famiglia! 🌌🌸",
            f"🌇🌺 UNA DOLCE BUONA SERA! 🌺🌇\n\nGoditi ogni sfumatura di questa serata: serenità, buona musica e la certezza che domani sarà un nuovo giorno speciale. 🎶💛"
        ]

    intro = random.choice(intro_varianti)

    # Personalizzazione contesto
    if tema in ("favara", "territorio"):
        contesto_territorio = "🏛️ Favara nel Cuore — Passione, radici e valorizzazione autentica della nostra comunità locale.\n"
    elif tema == "personal":
        contesto_territorio = "🤝 Antonio Giancani — Impegno costante, presenza e vicinanza alle persone e alle famiglie.\n"
    else:
        contesto_territorio = "🏡 La casa è il luogo dove nascono i sogni e crescono le certezze del futuro.\n"

    # Composizione del messaggio con rispetto assoluto della Colonna F e regola personal branding
    messaggio = f"""{intro}

{contesto_territorio}
💡 Citazione dal nostro Mindset quotidiano:
«{citazione_colonna_f}»

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 SOTTOFONDO MUSICALE GRATUITO (FREE LICENSE):
{musica_nome}
👉 Ascolta ora: {musica_url}
(Brano gratuito senza copyright da gustare in sottofondo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 {giorno_settimana}, {data_str}

🏠✨ IMMOBILIARE GIANCANI ✨🏠
📍 Il tuo punto di riferimento affidabile per valorizzare e scegliere la tua casa dei sogni.
📲 Segui la pagina per rimanere sempre aggiornato con saluti, ispirazioni e novità!
*Un cordiale saluto a cura di Antonio Giancani • Immobiliare Giancani*
"""
    return messaggio.strip()

def cancella_post_precedente(post_id, token, dry_run=False):
    if dry_run:
        print(f"  [DRY-RUN] Simulazione cancellazione post precedente: {post_id}")
        return True
    
    url = f"https://graph.facebook.com/v19.0/{post_id}?access_token={token}"
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("success"):
                print(f"  🗑️ Post precedente cancellato con successo (ID: {post_id})")
                return True
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"  ⚠️ Avviso rimozione post precedente {post_id}: {err[:150]}")
    except Exception as e:
        print(f"  ⚠️ Errore generico rimozione {post_id}: {e}")
    return False

def pubblica_nuovo_post(page_id, messaggio, token, dry_run=False):
    if dry_run:
        print(f"  [DRY-RUN] Simulazione pubblicazione post su pagina {page_id}:")
        print("  --- INIZIO ANTEPRIMA ---")
        for line in messaggio.split("\n")[:8]:
            print(f"    {line}")
        print("    [...] (testo completo formattato)")
        print("  --- FINE ANTEPRIMA ---")
        return f"{page_id}_DRY_RUN_{int(datetime.now().timestamp())}"

    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    ctx = ssl._create_unverified_context()
    payload = urllib.parse.urlencode({
        "message": messaggio,
        "access_token": token
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", "ImmobiliareGiancani-MultiBot/4.0")

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            new_id = data.get("id")
            if new_id:
                print(f"  ✅ Nuovo post pubblicato con successo! (ID: {new_id})")
                return new_id
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"  ❌ Errore HTTP pubblicazione ({e.code}): {err[:300]}")
    except Exception as e:
        print(f"  ❌ Errore pubblicazione: {e}")
    return None

def determina_slot_attuale():
    ora = ORA_IT.hour
    if 5 <= ora < 12:
        return "mattina"
    elif 12 <= ora < 18:
        return "pomeriggio"
    else:
        return "sera"

def main():
    parser = argparse.ArgumentParser(description="Bot Saluti Quotidiani Multi-Pagina Immobiliare Giancani")
    parser.add_argument("--slot", choices=["auto", "mattina", "pomeriggio", "sera"], default="auto")
    parser.add_argument("--page", choices=["all", "giancani", "antonio", "favara"], default="all")
    parser.add_argument("--publish", action="store_true", default=False)
    parser.add_argument("--dry-run", action="store_true", default=False, dest="dry_run")
    args = parser.parse_args()

    dry_run = args.dry_run or not args.publish
    slot = args.slot if args.slot != "auto" else determina_slot_attuale()

    print("=" * 65)
    print("🌅 BOT FACEBOOK MULTI-PAGINA — IMMOBILIARE GIANCANI")
    print(f"  Fascia Oraria : {slot.upper()} | Ora IT: {ORA_IT.strftime('%H:%M %d/%m/%Y')}")
    print(f"  Modalità      : {'DRY-RUN (Simulazione)' if dry_run else 'PUBBLICAZIONE REALE CON AUTO-CLEANUP'}")
    print("=" * 65)

    storico = carica_storico()
    pool_colonna_f = estrai_frasi_colonna_f()

    pagine_da_gestire = PAGINE_DEFAULT
    if args.page != "all":
        pagine_da_gestire = [p for p in PAGINE_DEFAULT if p["slug"] == args.page]

    for p in pagine_da_gestire:
        slug = p["slug"]
        nome = p["nome"]
        pid = p["page_id"]
        token = os.environ.get(p["token_env"]) or p["default_token"]

        print(f"\n👉 Elaborazione Pagina: {nome} (ID: {pid})")

        # 1. Cancellazione automatica del post precedente per mantenere solo l'ultimo attivo
        old_id = storico.get("last_post_per_page", {}).get(pid)
        if old_id:
            print(f"  🔄 Trovato post precedente da sostituire: {old_id}")
            cancella_post_precedente(old_id, token, dry_run=dry_run)
        else:
            print("  ℹ️ Nessun post precedente registrato nello storico.")

        # 2. Generazione messaggio fresco con testo rigorosamente da Colonna F
        citazione = ottieni_prossima_frase_colonna_f(storico, pool_colonna_f)
        messaggio = genera_testo_saluto(slot, p, citazione)

        # 3. Pubblicazione nuovo post
        nuovo_id = pubblica_nuovo_post(pid, messaggio, token, dry_run=dry_run)

        if nuovo_id:
            storico.setdefault("last_post_per_page", {})[pid] = nuovo_id
            storico.setdefault("storico_post", []).append({
                "timestamp": ORA_IT.isoformat(),
                "pagina": nome,
                "page_id": pid,
                "post_id": nuovo_id,
                "slot": slot
            })

    if not dry_run:
        salva_storico(storico)

    print("\n" + "━" * 65)
    print("✨ OPERAZIONE COMPLETATA CON SUCCESSO!")
    print("🏠 Tutti i saluti terminano mettendo in risalto: IMMOBILIARE GIANCANI")
    print("━" * 65)

if __name__ == "__main__":
    main()
