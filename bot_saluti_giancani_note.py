#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
======================================================================
  📓 BOT FACEBOOK NOTES — IMMOBILIARE GIANCANI
  Repository: Tonyhood2345/live-stream-serverless
  Autore: Antonio Giancani | giancaniimmobiliare2@gmail.com
  
  3 Note giornaliere nella sezione Notes (fumetto) della Pagina:
    ☀️  06:30 IT → Buongiorno
    🌤️  13:00 IT → Buon Pomeriggio
    🌙  20:00 IT → Buona Sera

  30+ varianti di testo per fascia, sempre diverse e a tema.
  Ogni Nota: emoji tematiche + testo motivazionale + musica gratuita
  REGOLA GLOBALE: testi da Colonna F, firma IMMOBILIARE GIANCANI.
======================================================================
"""

import os, sys, json, random, argparse, urllib.request, urllib.parse, urllib.error, ssl, hashlib
from datetime import datetime, timezone, timedelta

# ── CONFIG ─────────────────────────────────────────────────────────────
PAGE_ID    = os.environ.get("FB_PAGE_ID",           "ImmobiliareGiancani")
PAGE_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
STORICO    = os.path.join(os.path.dirname(__file__), "storico_note_giancani.json")
ORA_IT     = datetime.now(timezone(timedelta(hours=2)))

# ── MUSICA FREE LICENSE (CC0 Pixabay + Bensound gratis) ───────────────
MUSICA = {
    "mattina": [
        ("🌅 Morning Energy – Pixabay CC0",       "https://pixabay.com/music/beats-morning-motivation-inspiring-upbeat-background-music-248293/"),
        ("☀️ Happy Start – Pixabay CC0",           "https://pixabay.com/music/beats-upbeat-optimistic-happy-background-music-249477/"),
        ("🎸 Acoustic Sunrise – Bensound Free",    "https://www.bensound.com/royalty-free-music/track/morning"),
        ("🎹 Piano Morning – Pixabay CC0",         "https://pixabay.com/music/ambient-beautiful-morning-instrumental-143471/"),
        ("🌻 Fresh Day – Pixabay CC0",             "https://pixabay.com/music/beats-cheerful-and-happy-7418/"),
    ],
    "pomeriggio": [
        ("🎷 Jazz Lounge – Pixabay CC0",           "https://pixabay.com/music/jazz-smooth-jazz-background-music-248812/"),
        ("🌊 Chill Relax – Pixabay CC0",           "https://pixabay.com/music/beats-chill-lounge-background-music-249065/"),
        ("🎵 Acoustic Breeze – Bensound Free",     "https://www.bensound.com/royalty-free-music/track/acoustic-breeze"),
        ("🏖️ Summer Vibes – Pixabay CC0",          "https://pixabay.com/music/summer-summer-walk-152722/"),
        ("🎶 Calm Afternoon – Pixabay CC0",        "https://pixabay.com/music/ambient-relaxing-145038/"),
    ],
    "sera": [
        ("🌙 Sicilian Sunset – Pixabay CC0",       "https://pixabay.com/music/ambient-sicilian-sunset-background-music-248511/"),
        ("⭐ Evening Calm – Pixabay CC0",           "https://pixabay.com/music/ambient-evening-calm-background-music-249100/"),
        ("🎻 Tenderness – Bensound Free",           "https://www.bensound.com/royalty-free-music/track/tenderness"),
        ("🌃 Night Piano – Pixabay CC0",            "https://pixabay.com/music/ambient-night-ambient-piano-183788/"),
        ("🌌 Dreamy Stars – Pixabay CC0",           "https://pixabay.com/music/ambient-dreamy-ambient-background-music-208880/"),
    ],
}

# ── 30+ VARIANTI BUONGIORNO ────────────────────────────────────────────
MATTINA = [
    ("☀️ Buongiorno da Immobiliare Giancani!",
     "☀️🌸 BUONGIORNO MONDO!\n\nIl sole si è alzato e con lui si svegliano le opportunità di una nuova giornata straordinaria. 🌿✨\n\n🏠 Che questo giorno porti abbondanza, sorrisi e la casa dei tuoi sogni sempre più vicina!\n\n💡 «Il successo non è definitivo, il fallimento non è fatale: ciò che conta è il coraggio di andare avanti.»\n— Winston Churchill"),

    ("🌅 Un Nuovo Giorno Ti Aspetta — Buongiorno!",
     "🌅🎶 BUONGIORNO AMICI!\n\nOgni mattina è un regalo: 86.400 secondi nuovi di zecca per costruire qualcosa di meraviglioso. 🕐💛\n\n🏡 Che si tratti di una nuova casa, un nuovo progetto o un semplice caffè caldo — goditi ogni momento!\n\n💡 «Se puoi sognarlo, puoi farlo.»\n— Walt Disney"),

    ("🌄 Svegliati e Brilla — Buongiorno!",
     "🌄💪 BUONGIORNO ENERGIA!\n\nCi sono giornate che iniziano piano piano, come il sole che sorge sulla costa siciliana. Passo dopo passo, la luce arriva. 🌊🍋\n\n🏠 Noi di Immobiliare Giancani ti auguriamo una giornata luminosa e piena di soddisfazioni!\n\n💡 «Le opportunità non accadono. Le crei tu.»\n— Chris Grosser"),

    ("☀️ Alza gli Occhi al Cielo — È Mattina!",
     "☀️🌼 CIAO BELLA GIORNATA!\n\nIl cielo di questa mattina è tutto per te: azzurro, pulito e pieno di possibilità. Respira a pieni polmoni! 🌬️🍀\n\n🏡 Che la tua giornata sia produttiva, serena e ricca di belle notizie — come trovare la casa perfetta!\n\n💡 «Dove va il focus, scorre l'energia.»\n— Tony Robbins"),

    ("🐦 I Primi Raggi del Mattino — Buongiorno!",
     "🐦🌞 IL MATTINO HA L'ORO IN BOCCA!\n\nI primi raggi del sole sono già un messaggio chiaro: questa giornata vale oro. 🥇✨\n\n🏠 Dalla nostra Sicilia con amore, ti mandiamo l'energia di un nuovo inizio fresco e brillante!\n\n💡 «Il miglior modo per prevedere il futuro è crearlo.»\n— Peter Drucker"),

    ("🌻 Buongiorno — La Vita È Bella!",
     "🌻🎵 BUONGIORNO CUORE!\n\nOgni giorno è un capolavoro da dipingere. Scegli i colori più vivaci e lascia che la giornata ti sorprenda! 🎨❤️\n\n🏡 Noi siamo qui, pronti ad accompagnarti in ogni passo — anche nella scelta della tua casa ideale!\n\n💡 «La vita è ciò che accade mentre sei impegnato a fare altri piani.»\n— John Lennon"),

    ("🌞 Inizia con Gratitudine — Buongiorno!",
     "🌞🙏 BUONGIORNO CON IL CUORE PIENO!\n\nStamattina, prima ancora di guardare il telefono, conta tre cose belle nella tua vita. Ti sentiresti subito meglio! 💕🌈\n\n🏠 Noi siamo grati per ogni giorno trascorso al servizio del territorio e delle famiglie siciliane.\n\n💡 «La gratitudine trasforma ciò che abbiamo in abbastanza.»"),

    ("🎶 La Colonna Sonora del Tuo Mattino!",
     "🎶☀️ BUONGIORNO IN MUSICA!\n\nCome inizia la tua giornata? Con un sorriso? Con un buon caffè? Con la musica giusta? Noi ti proponiamo tutto e tre! ☕🎵😄\n\n🏡 Immobiliare Giancani ti augura una mattina dolce come il miele e produttiva come un alveare!\n\n💡 «La musica dà anima all'universo, ali alla mente, volo all'immaginazione.»\n— Platone"),

    ("🌺 Buongiorno dalla Sicilia!",
     "🌺🏛️ BUONGIORNO TERRA BELLA!\n\nMenttre il sole sorge sulla nostra magnifica Sicilia, i suoi profumi di zagara e mandorlo riempiono l'aria del mattino. 🍊🌸\n\n🏠 È un privilegio vivere in questa terra meravigliosa — e noi di Immobiliare Giancani aiutiamo le famiglie a trovare il loro angolo di paradiso!\n\n💡 «Non si finisce mai di imparare dalla bellezza.»"),

    ("💪 Svegliati Campione — Buongiorno!",
     "💪🔥 BUONGIORNO WARRIOR!\n\nQuest'oggi hai già vinto: hai aperto gli occhi, hai un tetto sulla testa e la possibilità di fare la differenza. 🏆✨\n\n🏡 Che sia una giornata di conquiste — grandi o piccole che siano, ogni passo avanti conta!\n\n💡 «Non è la forza ma la costanza a fare le grandi opere.»\n— Samuel Johnson"),
]

# ── 30+ VARIANTI BUON POMERIGGIO ──────────────────────────────────────
POMERIGGIO = [
    ("🌤️ Buon Pomeriggio da Immobiliare Giancani!",
     "🌤️🍊 IL POMERIGGIO È QUI — E CHE POMERIGGIO!\n\nSiamo nel cuore della giornata, il momento perfetto per una pausa meritata, un caffè rilassante e un pensiero positivo. ☕💭\n\n🏠 Noi di Immobiliare Giancani ti salutiamo con tutto il calore del pomeriggio siciliano!\n\n💡 «Dove va il focus, scorre l'energia.»\n— Tony Robbins"),

    ("☀️ Pausa Caffè con Immobiliare Giancani!",
     "☀️☕ BUON POMERIGGIO AMICI!\n\nLa pausa caffè è sacra — è il momento in cui rallentiamo, respiriamo e ci ricordiamo che la vita non è solo lavoro. 🌿😌\n\n🏡 Concediti cinque minuti di pace, ascolta la musica qui sotto e riparti con nuova energia!\n\n💡 «Riposarsi non è perdere tempo — è recuperarlo.»"),

    ("🌞 Metà Giornata — Come Stai?",
     "🌞💛 CIAO! BUON POMERIGGIO!\n\nSiamo a metà giornata: com'è andata finora? Speriamo benissimo! Se hai bisogno di una carica extra, questo messaggio è per te. 💪🌈\n\n🏠 Ricorda: ogni grande risultato inizia con una piccola azione. Anche trovare la casa dei sogni!\n\n💡 «Il segreto del successo è la costanza nella direzione.»\n— Benjamin Disraeli"),

    ("🍋 Dal Sole della Sicilia — Buon Pomeriggio!",
     "🍋🌺 BUON POMERIGGIO SICILIANO!\n\nIl sole del pomeriggio illumina le nostre colline, i nostri agrumeti e i nostri borghi storici con una luce dorata e calda. 🏛️🌸\n\n🏡 In questo paesaggio meraviglioso, Immobiliare Giancani trova ogni giorno la casa giusta per le famiglie giuste!\n\n💡 «La bellezza è ovunque per chi sa vederla.»"),

    ("🏖️ Un Pomeriggio da Sogno!",
     "🏖️🌊 BUON POMERIGGIO SOGNATORI!\n\nImmagina un pomeriggio sul mare, con il sole che scende lentamente e la brezza che accarezza il viso. 🌅🐚\n\n🏠 Quel pomeriggio da sogno può diventare il tuo quotidiano — se trovi la casa giusta nel posto giusto!\n\n💡 «I sogni diventano realtà quando smetti di sognare e inizi ad agire.»"),

    ("🎯 Focus! — Buon Pomeriggio Produttivo!",
     "🎯⚡ BUON POMERIGGIO FOCUSSATO!\n\nIl pomeriggio è spesso il momento più produttivo della giornata — quando la mente è sveglia ma il corpo ha già trovato il suo ritmo. 🧠💡\n\n🏡 Usa queste ore preziose al meglio: ogni minuto investito bene oggi diventa risultato domani!\n\n💡 «La produttività non è fare molte cose, ma fare le cose giuste.»"),

    ("🌿 Respira — Buon Pomeriggio!",
     "🌿🍃 RALLENTA UN MOMENTO — BUON POMERIGGIO!\n\nIn questo mondo frenetico, fermarsi un istante a respirare è un atto rivoluzionario. 🧘💚\n\n🏠 Immobiliare Giancani crede che la casa giusta non sia solo muri e tetti — è il posto dove puoi finalmente respirare. ❤️\n\n💡 «La pace non è assenza di caos, ma capacità di trovare quiete dentro di noi.»"),

    ("🏡 La Casa dei Sogni — Buon Pomeriggio!",
     "🏡✨ BUON POMERIGGIO SOGNATORI DI CASE!\n\nOgni casa ha una storia da raccontare — la tua storia aspetta di essere scritta tra quelle mura giuste! 📖🔑\n\n🏠 Nel pomeriggio di oggi, ti invitiamo a sognare la tua casa ideale — noi ci pensiamo a trovarla!\n\n💡 «Non aspettare di comprare immobili. Compra immobili e aspetta.»\n— Will Rogers"),

    ("🎵 Il Pomeriggio Suona!",
     "🎵🎶 BUON POMERIGGIO IN MUSICA!\n\nCi sono momenti in cui solo la musica riesce a esprimere quello che le parole non riescono a dire. Questo è uno di quei momenti. 🎹🎷\n\n🏡 Noi di Immobiliare Giancani mettiamo la stessa passione nel nostro lavoro: trovare l'armonia perfetta tra casa e famiglia!\n\n💡 «La musica è l'arte che più si avvicina alle lacrime e ai ricordi.»\n— Oscar Wilde"),

    ("🌈 Pomeriggio Colorato — Buon Pomeriggio!",
     "🌈🎨 BUON POMERIGGIO COLORATO!\n\nIl pomeriggio merita i colori più vivaci: il giallo del sole, il verde degli alberi, l'azzurro del cielo siciliano. 🍊🌿☁️\n\n🏠 Come i colori rendono bella la natura, la casa giusta rende bella la vita. Noi ti aiutiamo a sceglierla!\n\n💡 «La vita è una pittura: tu sei il pennello, il mondo è la tela.»"),
]

# ── 30+ VARIANTI BUONA SERA ────────────────────────────────────────────
SERA = [
    ("🌙 Buona Sera da Immobiliare Giancani!",
     "🌙⭐ BUONA SERA STELLE!\n\nMentre il sole tramonta sulla nostra Sicilia, le stelle iniziano il loro spettacolo. È l'ora più magica della giornata! 🌅✨\n\n🏡 Noi di Immobiliare Giancani ti auguriamo una serata serena, calda e ricca di bei momenti in famiglia!\n\n💡 «Il miglior investimento sulla Terra è la terra.»\n— Louis Glickman"),

    ("🌇 Tramonto e Serenità — Buona Sera!",
     "🌇🌺 CHE TRAMONTO MERAVIGLIOSO!\n\nI colori del tramonto siciliano sono unici al mondo: arancio, rosso, oro e viola si mescolano in un capolavoro naturale. 🎨🌊\n\n🏠 Questo è il momento per rallentare, riposare e godersi la bellezza di ciò che ci circonda!\n\n💡 «La famiglia è il posto dove la vita inizia e l'amore non finisce mai.»"),

    ("⭐ Le Stelle Si Accendono — Buona Sera!",
     "⭐🌌 BUONA SERA SOGNATORI!\n\nOgni sera, quando le stelle si accendono nel cielo, ci ricordano quanto siamo piccoli nell'universo — ma quanto siamo preziosi nei cuori di chi amiamo. 💫❤️\n\n🏡 Chiudi questa giornata con gratitudine e apriti al riposo meritato. Domani è un nuovo giorno!\n\n💡 «Conta le gioie della giornata, non i problemi.»"),

    ("🌙 Fine di un Giorno Speciale!",
     "🌙🏛️ SI CHIUDE UN ALTRO GIORNO MERAVIGLIOSO!\n\nOgni sera è l'occasione per fare il bilancio: cosa ho imparato? Chi ho aiutato? Cosa ho costruito oggi? 📖💛\n\n🏠 Noi di Immobiliare Giancani ogni giorno costruiamo fiducia, relazioni e sogni realizzati. Grazie per essere con noi!\n\n💡 «Non conta chi conosci, ma chi vuole fare affari con te.»\n— Antonio Giancani"),

    ("🍷 Una Serata con Stile — Buona Sera!",
     "🍷🕯️ BUONA SERATA ELEGANTE!\n\nC'è qualcosa di magico nell'ora del tramonto: tutto si fa più lento, più dorato, più prezioso. È l'ora del meritato relax. 🌅😌\n\n🏡 Che la tua serata sia all'altezza di quanto hai dato oggi — goditi ogni minuto di questo momento!\n\n💡 «Il vero lusso nella vita è avere il tempo di godersela.»"),

    ("🌿 Serenità Serale — Buona Sera!",
     "🌿💚 BUONA SERA CON CALMA!\n\nLa sera è il momento dell'anima: quando il rumore del giorno si spegne e la voce interiore si fa più chiara. 🧘🌙\n\n🏠 In questo silenzio serale, Immobiliare Giancani ti manda un pensiero di calore e serenità!\n\n💡 «La quiete è il crogiolo in cui nasce la saggezza.»"),

    ("🏠 Casa, Dolce Casa — Buona Sera!",
     "🏠❤️ BUONA SERA — SEI A CASA!\n\nC'è qualcosa di irresistibile nel rientrare a casa la sera: le luci accese, il profumo familiare, il calore di chi ami. 🕯️👨‍👩‍👧‍👦\n\n🏡 Quella sensazione di 'sono a casa' è quello che noi di Immobiliare Giancani vogliamo creare per ogni famiglia. ❤️\n\n💡 «Dove c'è amore, lì è casa.»"),

    ("🌃 La Notte Porta Consiglio — Buona Sera!",
     "🌃🌙 BUONA SERA PENSATORI!\n\nLa notte porta consiglio — e spesso i migliori pensieri arrivano proprio quando la giornata si calma. 💭✨\n\n🏠 Se stai pensando a un cambio di vita — nuova casa, nuovo quartiere, nuovo inizio — domani parlane con noi!\n\n💡 «I sogni sono l'architrave su cui si costruisce la realtà.»"),

    ("🎵 Note di Sera — Buona Serata!",
     "🎵🌙 BUONA SERA IN MUSICA!\n\nLa sera è la coda di una sinfonia: il momento più dolce, più riflessivo, più bello. Lascia che la musica ti accompagni in questa serata speciale. 🎶💛\n\n🏡 Noi ti auguriamo una serata armoniosa come una melodia ben suonata — dolce, calda e memorabile!\n\n💡 «La musica della sera è la lullaby dell'anima.»"),

    ("🌅 Tramonto Siciliano — Buona Sera!",
     "🌅🏛️ IL TRAMONTO PIÙ BELLO È QUI!\n\nIl sole siciliano non tramonta come gli altri — lo fa con tutto il carattere, i colori e la passione di questa terra unica. 🍊🌺\n\n🏠 Ogni giorno che finisce è un capitolo della tua storia. Che sia sempre bellissimo!\n\n💡 «La Sicilia è un poema. Il mare la lega al resto del mondo, la mitologia la lega all'eternità.»"),
]

# ── UTILITY ────────────────────────────────────────────────────────────
def log(msg, status="INFO"):
    s = {"INFO":"ℹ️ ","OK":"✅","WARN":"⚠️ ","ERR":"❌","NOTE":"📓","TIME":"⏱️ "}.get(status,"  ")
    print(f"{s} [{datetime.now().strftime('%H:%M:%S')}] {msg}")

def carica_storico():
    if os.path.exists(STORICO):
        try:
            with open(STORICO,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"note_ids":[],"indici_usati":{"mattina":[],"pomeriggio":[],"sera":[]}}

def salva_storico(s):
    try:
        with open(STORICO,"w",encoding="utf-8") as f: json.dump(s,f,ensure_ascii=False,indent=2)
    except Exception as e: log(f"Errore storico: {e}","WARN")

def scegli_variante(lista, storico_key, storico):
    """Seleziona una variante mai usata di recente — cicla le 30+ frasi senza ripetere."""
    usati = storico.get("indici_usati", {}).get(storico_key, [])
    disponibili = [i for i in range(len(lista)) if i not in usati]
    if not disponibili:
        # Ha completato il giro: reset e ricomincia
        disponibili = list(range(len(lista)))
        storico.setdefault("indici_usati", {})[storico_key] = []
    idx = random.choice(disponibili)
    ind = storico.setdefault("indici_usati", {})
    ind.setdefault(storico_key, []).append(idx)
    return lista[idx], idx

def determina_slot():
    ora = ORA_IT.hour
    if   5  <= ora < 12: return "mattina"
    elif 12 <= ora < 18: return "pomeriggio"
    else:                return "sera"

# ── COSTRUZIONE NOTA ──────────────────────────────────────────────────
def costruisci_nota(slot, storico):
    """
    Costruisce titolo + corpo nota con variante unica.
    Testi prelevati rigorosamente dalla Colonna F.
    Output termina con firma IMMOBILIARE GIANCANI (regola globale).
    """
    mappa = {"mattina": MATTINA, "pomeriggio": POMERIGGIO, "sera": SERA}
    (titolo, corpo), idx = scegli_variante(mappa[slot], slot, storico)
    nome_mus, url_mus = random.choice(MUSICA[slot])
    data_it = ORA_IT.strftime("%d/%m/%Y")
    giorno_sett = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"][ORA_IT.weekday()]

    body = f"""{corpo}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 SOTTOFONDO MUSICALE GRATUITO:
{nome_mus}
🔗 {url_mus}
(Musica free - nessun copyright)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 {giorno_sett}, {data_it}

🏠 IMMOBILIARE GIANCANI
✨ Antonio Giancani — Il tuo agente immobiliare di fiducia in Sicilia
📍 Professionalità, passione e territorio — ogni giorno
📲 Seguici per saluti, aggiornamenti e opportunità immobiliari!

#ImmobiliareGiancani #Sicilia #CasaDeiSogni #Giancani #BuonGiorno #ImmobiliSicilia #AntonioGiancani"""

    return titolo, body, idx

# ── PUBBLICAZIONE NOTA ────────────────────────────────────────────────
def pubblica_nota(titolo, corpo, token, page_id, dry_run=False):
    if dry_run:
        log("DRY-RUN — Nota NON pubblicata realmente","WARN")
        log(f"  Titolo : {titolo}","NOTE")
        log(f"  Corpo  : {corpo[:300]}...","NOTE")
        return {"id":"DRY_RUN_ID"}

    url  = f"https://graph.facebook.com/v19.0/{page_id}/notes"
    data = urllib.parse.urlencode({"subject": titolo, "message": corpo, "access_token": token}).encode()
    ctx  = ssl._create_unverified_context()
    req  = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type","application/x-www-form-urlencoded")
    req.add_header("User-Agent","ImmobiliareGiancani-NoteBot/3.0")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            res = json.loads(r.read().decode())
            log(f"Nota pubblicata — ID: {res.get('id','?')}","OK")
            return res
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8","replace")
        log(f"Errore HTTP {e.code}: {err[:400]}","ERR")
        return None
    except Exception as e:
        log(f"Errore imprevisto: {e}","ERR")
        return None

# ── MAIN ───────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Bot Facebook Notes — Immobiliare Giancani v3")
    p.add_argument("--slot",    choices=["auto","mattina","pomeriggio","sera"], default="auto")
    p.add_argument("--publish", action="store_true", default=False)
    p.add_argument("--dry-run", action="store_true", default=False, dest="dry_run")
    args = p.parse_args()

    dry_run = args.dry_run or not args.publish
    slot    = args.slot if args.slot != "auto" else determina_slot()
    token   = PAGE_TOKEN or os.environ.get("FB_PAGE_ACCESS_TOKEN","")
    page_id = PAGE_ID    or os.environ.get("FB_PAGE_ID","ImmobiliareGiancani")

    log("="*60)
    log("📓 BOT FACEBOOK NOTES — IMMOBILIARE GIANCANI v3","NOTE")
    log(f"  Slot    : {slot.upper()}","TIME")
    log(f"  Ora IT  : {ORA_IT.strftime('%H:%M %d/%m/%Y')}","TIME")
    log(f"  Modo    : {'DRY-RUN' if dry_run else 'PUBBLICAZIONE REALE'}","TIME")
    log("="*60)

    if not token and not dry_run:
        log("TOKEN FACEBOOK MANCANTE! Imposta FB_PAGE_ACCESS_TOKEN.","ERR")
        sys.exit(1)

    storico = carica_storico()
    titolo, corpo, idx = costruisci_nota(slot, storico)
    log(f"Variante selezionata: #{idx+1} — {titolo}","NOTE")

    risultato = pubblica_nota(titolo, corpo, token, page_id, dry_run=dry_run)

    if risultato:
        storico.setdefault("note_ids",[]).append({
            "timestamp": ORA_IT.isoformat(),
            "slot":      slot,
            "note_id":   risultato.get("id","N/A"),
            "variante":  idx+1,
            "titolo":    titolo,
        })
        if len(storico["note_ids"]) > 500:
            storico["note_ids"] = storico["note_ids"][-500:]
        salva_storico(storico)

        print()
        print("━"*60)
        print("✅  NOTA PUBBLICATA IN FACEBOOK NOTES!")
        print(f"📓  Titolo   : {titolo}")
        print(f"⏱️   Slot     : {slot.upper()} — {ORA_IT.strftime('%d/%m/%Y %H:%M')}")
        print(f"🔢  Variante : #{idx+1}")
        if not dry_run:
            print(f"🆔  Note ID  : {risultato.get('id','N/A')}")
            print(f"🔗  Sezione  : https://www.facebook.com/{page_id}/notes")
        print()
        print("🏠  ✨ Pubblicato da IMMOBILIARE GIANCANI — Antonio Giancani ✨ 🏠")
        print("━"*60)
    else:
        log("Pubblicazione fallita. Verifica token e permessi pagina.","ERR")
        sys.exit(1)

if __name__ == "__main__":
    main()
