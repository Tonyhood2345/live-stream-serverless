#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copywriting Persuasivo per Storie, Fasce Orarie e Hook Emozionali
Rispetta rigorosamente il personal branding con chiusura '— Immobiliare Giancani'
"""

import time
import random
import re
from story_publisher.config import BRAND_CLAIM

FRASI_POSITIVE_FLASH = [
    "Sorridi alla vita con Immobiliare Giancani!",
    "La felicità comincia da casa tua con Immobiliare Giancani!",
    "Oggi è un giorno meraviglioso con Immobiliare Giancani!",
    "Le cose belle accadono a chi crede nei sogni con Immobiliare Giancani!",
    "Che sia una splendida giornata con Immobiliare Giancani!",
    "Pensa positivo e guarda avanti con Immobiliare Giancani!",
    "Ogni nuovo giorno porta nuove meraviglie con Immobiliare Giancani!",
    "Un raggio di sole e tanta serenità con Immobiliare Giancani!",
    "La tua serenità è la cosa più preziosa con Immobiliare Giancani!",
    "Oggi ti aspetta una splendida notizia con Immobiliare Giancani!",
    "Credi sempre nei tuoi desideri con Immobiliare Giancani!",
    "Circondati di bellezza e positività con Immobiliare Giancani!"
]

def determina_fascia_oraria(ora=None):
    """
    Determina la fascia oraria attuale (Mattina, Pomeriggio, Sera, Notte)
    con saluti personalizzati, emoticon, musica royalty-free per Facebook
    e riflessioni positive per le storie e le note.
    """
    if ora is None:
        ora = time.localtime().tm_hour

    if 6 <= ora < 12:
        return {
            "fascia": "mattina",
            "nome": "Mattina",
            "saluto": "Buongiorno 🌅☀️☕",
            "badge": "🌅 BUONGIORNO • IMMOBILIARE GIANCANI",
            "frase_flash": "Buongiorno! Inizia una giornata di luce e nuove opportunità con Immobiliare Giancani! 🌅☀️",
            "intro_voce": "Salve dall'agenzia Immobiliare Giancani! Iniziamo questa splendida giornata insieme per scoprire questa magnifica proprietà.",
            "emoticon": "🌅☀️☕",
            "musica_file": "classica_vivaldi_primavera.mp3",
            "musica_titolo": "Vivaldi - La Primavera (Royalty-Free Facebook)",
            "titolo_nota": "📝 NOTA DEL BUONGIORNO — Immobiliare Giancani 🌅☀️",
            "riflessione_nota": (
                "🌅 Buongiorno da Immobiliare Giancani! ☕\n\n"
                "Iniziare la giornata nel posto giusto fa tutta la differenza del mondo. "
                "La luce del mattino che filtra dalle ampie finestre, il profumo del caffè in una cucina spaziosa "
                "e la consapevolezza di aver trovato il nido perfetto per sé e per la propria famiglia.\n\n"
                "Ogni nuovo giorno porta con sé l'opportunità di fare il passo verso la casa dei propri sogni."
            )
        }
    elif 12 <= ora < 18:
        return {
            "fascia": "pomeriggio",
            "nome": "Pomeriggio",
            "saluto": "Buon pomeriggio ☕🌤️🏡",
            "badge": "☕ BUON POMERIGGIO • IMMOBILIARE GIANCANI",
            "frase_flash": "Buon pomeriggio! È il momento perfetto per scegliere la tua casa con Immobiliare Giancani! ☕🏡",
            "intro_voce": "Salve dall'agenzia Immobiliare Giancani! Nel cuore di questa giornata vi presentiamo un immobile davvero eccezionale.",
            "emoticon": "☕🌤️🏡",
            "musica_file": "cheerful_music.wav",
            "musica_titolo": "Cheerful Acoustic Lounge 124 BPM (Royalty-Free Facebook)",
            "titolo_nota": "📝 NOTA DEL POMERIGGIO — Immobiliare Giancani ☕🌤️",
            "riflessione_nota": (
                "☕ Buon pomeriggio da Immobiliare Giancani! 🌤️\n\n"
                "Una breve pausa nel pomeriggio è il momento ideale per riflettere sul futuro e sui propri progetti di vita. "
                "Gli spazi giusti regalano serenità, comfort e il piacere di vivere ogni ambiente con gioia e libertà.\n\n"
                "Siamo sempre al vostro fianco per guidarvi con cura ed esperienza nella scelta della vostra nuova dimora."
            )
        }
    elif 18 <= ora < 22:
        return {
            "fascia": "sera",
            "nome": "Sera",
            "saluto": "Buona sera 🌆🍷✨",
            "badge": "🌆 BUONA SERA • IMMOBILIARE GIANCANI",
            "frase_flash": "Buona sera! Il piacere e il calore di tornare a casa con Immobiliare Giancani! 🌆✨",
            "intro_voce": "Salve dall'agenzia Immobiliare Giancani! Al calar della sera, lasciatevi conquistare dal calore di questa splendida residenza.",
            "emoticon": "🌆🍷✨",
            "musica_file": "luxury_ambient_music.wav",
            "musica_titolo": "Luxury Sunset Ambient (Royalty-Free Facebook)",
            "titolo_nota": "📝 NOTA DELLA SERA — Immobiliare Giancani 🌆🍷✨",
            "riflessione_nota": (
                "🌆 Buona sera da Immobiliare Giancani! 🍷\n\n"
                "C’è una magia tutta speciale nella tranquillità della sera: la gioia di tornare a casa, chiudere la porta "
                "e ritrovarsi nell'intimità dei propri affetti, immersi nel calore di un ambiente accogliente e protetto.\n\n"
                "La vera bellezza dell'abitare è sentirsi sempre nel posto giusto al momento giusto."
            )
        }
    else:
        return {
            "fascia": "notte",
            "nome": "Notte",
            "saluto": "Buonanotte 🌙⭐️💤",
            "badge": "🌙 BUONANOTTE • IMMOBILIARE GIANCANI",
            "frase_flash": "Buonanotte e sogni d'oro! La casa perfetta ti aspetta con Immobiliare Giancani! 🌙⭐️",
            "intro_voce": "Salve dall'agenzia Immobiliare Giancani! Prima di addormentarvi, vi auguriamo pensieri sereni e sogni grandiosi.",
            "emoticon": "🌙⭐️💤",
            "musica_file": "classica_mozart_nachtmusik.mp3",
            "musica_titolo": "Mozart - Serenata Notturna (Royalty-Free Facebook)",
            "titolo_nota": "📝 NOTA DELLA BUONANOTTE — Immobiliare Giancani 🌙⭐️💤",
            "riflessione_nota": (
                "🌙 Buonanotte e sogni d'oro da Immobiliare Giancani! ⭐️\n\n"
                "Mentre la notte scende sul territorio, è tempo di riposare sereni e fare spazio ai desideri più belli. "
                "I sogni più autentici sono quelli che domani, con determinazione e i giusti consigli, possono diventare meravigliosa realtà.\n\n"
                "Vi auguriamo un sereno riposo, sapendo che la casa perfetta è già lì che vi aspetta."
            )
        }

def genera_intro_invito_dinamico(personaggio="daria", testo_f="", is_live=True, frase_positiva=None, fascia_info=None):
    """
    Genera hook dinamici e calorosi per le storie social.
    Progettato appositamente per chi scorre velocemente le storie:
    le primissime parole pronunciate trasmettono un pensiero positivo immediato
    e terminano con personal branding '— Immobiliare Giancani'.
    """
    testo_f_clean = (testo_f or "").strip()
    if testo_f_clean:
        testo_f_clean = re.sub(r'\s*—?\s*Immobiliare Giancani\s*$', '', testo_f_clean, flags=re.IGNORECASE).strip()

    if not frase_positiva:
        frase_positiva = random.choice(FRASI_POSITIVE_FLASH)

    if is_live:
        followups = [
            f"Salve dall'agenzia Immobiliare Giancani! Siamo collegati dal vivo in diretta streaming proprio in questo istante. {testo_f_clean} Entrate subito a guardare la diretta per scoprire tutti gli ambienti e chattare con noi in tempo reale! Vi aspettiamo con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! Da tutto il nostro team un invito imperdibile: siamo in onda adesso in diretta streaming. {testo_f_clean} Cliccate subito ed entrate nella diretta per farci tutte le vostre domande dal vivo! Vi aspettiamo con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! La diretta streaming è accesa adesso e abbiamo preparato per voi una presentazione esclusiva. {testo_f_clean} Entrate subito a guardare la diretta per vedere ogni dettaglio prima di tutti! Vi aspettiamo con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! Un caloroso invito per voi: siamo in onda dal vivo in diretta streaming. {testo_f_clean} Scriveteci nei commenti quale stanza desiderate visitare e vi porteremo subito all'interno! Entrate in diretta con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! In questo momento siamo in onda dal vivo per farvi scoprire questa gemma immobiliare. {testo_f_clean} Entrate subito a guardare la nostra diretta streaming, vi aspettiamo con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! Le porte delle nostre migliori residenze sono aperte adesso in streaming. {testo_f_clean} Collegatevi subito alla diretta per interagire con noi in tempo reale! Vi aspettiamo con Immobiliare Giancani!",
            f"Salve dall'agenzia Immobiliare Giancani! Se state cercando la vostra prossima casa, non perdetevi la diretta streaming attiva proprio ora. {testo_f_clean} Entrate subito a vedere la diretta dal vivo per scoprire tutte le stanze e il prezzo! Vi aspettiamo con Immobiliare Giancani!"
        ]
        return random.choice(followups)
    else:
        if not fascia_info:
            fascia_info = determina_fascia_oraria()
        saluto_momento = fascia_info.get("intro_voce", "Salve dall'agenzia Immobiliare Giancani!")
        followups = [
            f"{saluto_momento} {testo_f_clean} Contattateci subito per prenotare una visita esclusiva. {frase_positiva} {BRAND_CLAIM}",
            f"{saluto_momento} {testo_f_clean} Per fissare un appuntamento e visitarla insieme, chiamateci senza impegno. {frase_positiva} {BRAND_CLAIM}",
            f"{saluto_momento} {testo_f_clean} Chiamateci subito per scoprire ogni dettaglio di persona. {frase_positiva} {BRAND_CLAIM}",
            f"{saluto_momento} La casa perfetta vi aspetta, curata con dedizione dal nostro team. {testo_f_clean} Siamo pronti ad accompagnarvi nella vostra visita privata. {frase_positiva} {BRAND_CLAIM}"
        ]
        return random.choice(followups)
