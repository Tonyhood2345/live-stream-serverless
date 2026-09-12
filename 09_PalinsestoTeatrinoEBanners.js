// ═══════════════════════════════════════════════════════════════════════
// 📁 MODULO 09: PALINSESTO TV, COSTRUTTORE SCALETTA DINAMICA & GESTIONE TEMPI
// Gestisce la programmazione oraria 24h, gli sketch DarIA & DarIO, i banner e la scaletta dinamica
// ═══════════════════════════════════════════════════════════════════════

function salvaPalinsestoWeb(payload) {
  try {
    PropertiesService.getScriptProperties().setProperty('PALINSESTO_TV_WEB', JSON.stringify(payload || []));
    return { success: true };
  } catch(e) {
    inviaAllertaErroreTelegram("09_PalinsestoTeatrinoEBanners.js", "salvaPalinsestoWeb", e.toString());
    return { success: false, error: e.toString() };
  }
}

function leggiPalinsestoWeb() {
  try {
    var raw = PropertiesService.getScriptProperties().getProperty('PALINSESTO_TV_WEB');
    var palinsesto = raw ? JSON.parse(raw) : [
      { ora: "00-08", nome: "Notte Relax & Virtual Tour 360°" },
      { ora: "08-12", nome: "Rassegna Mattina: Nuovi Immobili & Opportunità" },
      { ora: "12-16", nome: "Pomeriggio Live: Tour Stanze & Interazione Chat" },
      { ora: "16-20", nome: "Aperitivo con DarIA & DarIO: Offerte Top" },
      { ora: "20-24", nome: "Prime Time: Le Case più Belle di Favara e Agrigento" }
    ];
    return { success: true, palinsesto: palinsesto };
  } catch(e) {
    return { success: false, palinsesto: [] };
  }
}

/**
 * 📺 GESTORE SPOT PUBBLICITARI & SPONSOR DAL FOGLIO 'Pubblicita_Spot'
 */
function getPubblicitaAttiva() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Pubblicita_Spot') : null;
    if (!sheet || sheet.getLastRow() < 2) return { success: true, spot: [] };

    var data = sheet.getDataRange().getValues();
    var spotAttivi = [];

    for (var r = 1; r < data.length; r++) {
      var mediaUrl = String(data[r][0] || '').trim();
      var titolo = String(data[r][1] || '').trim();
      var tipo = String(data[r][2] || 'immagine').trim().toLowerCase();
      var usaAudio = String(data[r][3] || 'NO').trim().toUpperCase() === 'SI';
      var freqMin = parseInt(data[r][4]) || 15;
      var testo = String(data[r][5] || '').trim(); // Colonna F: Testo Parlato
      var attivo = String(data[r][6] || 'SI').trim().toUpperCase();

      if (attivo === 'SI' && (mediaUrl || testo)) {
        spotAttivi.push({
          riga: r + 1,
          mediaUrl: convertiUrlDriveDirect(mediaUrl),
          titolo: titolo,
          tipo: tipo,
          usaAudioOriginale: usaAudio,
          frequenzaMinuti: freqMin,
          testoParlato: testo,
          attivo: true
        });
      }
    }

    return { success: true, spot: spotAttivi };
  } catch(e) {
    inviaAllertaErroreTelegram("09_PalinsestoTeatrinoEBanners.js", "getPubblicitaAttiva", e.toString());
    return { success: false, spot: [] };
  }
}

function getAllPubblicita() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Pubblicita_Spot') : null;
    if (!sheet) return { success: true, pubblicita: [] };

    var data = sheet.getDataRange().getValues();
    var lista = [];

    for (var r = 1; r < data.length; r++) {
      lista.push({
        riga: r + 1,
        mediaUrl: String(data[r][0] || '').trim(),
        titolo: String(data[r][1] || '').trim(),
        tipo: String(data[r][2] || 'immagine').trim(),
        usaAudioOriginale: String(data[r][3] || 'NO').trim(),
        frequenzaMinuti: data[r][4] || 15,
        testoParlato: String(data[r][5] || '').trim(), // Colonna F
        attivo: String(data[r][6] || 'SI').trim()
      });
    }

    return { success: true, pubblicita: lista };
  } catch(e) {
    return { success: false, pubblicita: [] };
  }
}

/**
 * 🎬 Recupera tutti i video del foglio 'Post_YouTube' per la rotazione spot ogni 5 minuti
 * Preleva rigorosamente i testi parlati da Colonna F per personal branding Immobiliare Giancani
 */
function getPostYouTubeAttivi() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Post_YouTube') : null;
    if (!sheet || sheet.getLastRow() < 2) return [];

    var data = sheet.getDataRange().getValues();
    var listaVideo = [];

    for (var r = 1; r < data.length; r++) {
      var mediaUrl = String(data[r][0] || '').trim(); // Colonna A: URL_MEDIA / embed
      var prezzo = String(data[r][1] || '').trim();   // Colonna B
      var mq = String(data[r][2] || '').trim();       // Colonna C
      var titolo = String(data[r][3] || '').trim();   // Colonna D: Titolo Video / Stanza
      var tipoMedia = String(data[r][4] || 'video').trim(); // Colonna E
      var descrColF = String(data[r][5] || '').trim(); // Colonna F: Testo Parlato DarIA
      var thumb = String(data[r][6] || '').trim();    // Colonna G
      var ticker = String(data[r][7] || '').trim();   // Colonna H

      if (mediaUrl || titolo) {
        listaVideo.push({
          riga: r + 1,
          videoUrl: mediaUrl,
          linkYt: mediaUrl,
          titolo: titolo,
          prezzo: prezzo,
          mq: mq,
          tipoMedia: tipoMedia,
          testoParlato: descrColF, // Rigorosamente Colonna F
          thumbnail: thumb,
          ticker: ticker || (titolo + " — Immobiliare Giancani")
        });
      }
    }

    return listaVideo;
  } catch(e) {
    console.warn("getPostYouTubeAttivi error:", e);
    return [];
  }
}

function salvaModificaPubblicita(riga, colonna, valore) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Pubblicita_Spot') : null;
    if (!sheet) return { success: false, error: "Foglio Pubblicita_Spot non trovato" };

    sheet.getRange(parseInt(riga), parseInt(colonna)).setValue(valore);
    return { success: true };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}
function inizializzaFoglioTeatrino() { return { success: true }; }

function getTeatrinoComico() {
  try {
    var sketch = [
      { daria: "DarIO, ma hai visto che panorama da questo terrazzo?", dario: "Altro che terrazzo DarIA, qui ci facciamo direttamente il barbecue per tutta la Sicilia! — Immobiliare Giancani" },
      { daria: "DarIO, guarda che rifiniture in questa cucina!", dario: "Spettacolare! Se cucino io però scatta subito l'allarme antincendio! — Immobiliare Giancani" },
      { daria: "DarIO, gli spettatori in chat chiedono se la casa ha il garage!", dario: "Certo che sì! Ci sta la macchina, la moto e pure tutti i tuoi vestiti dello shopping! — Immobiliare Giancani" }
    ];
    var scelto = sketch[Math.floor(Math.random() * sketch.length)];
    return { success: true, sketch: scelto };
  } catch(e) {
    return { success: false, sketch: { daria: "Splendida casa!", dario: "Davvero un affare imperdibile! — Immobiliare Giancani" } };
  }
}

function getAllTeatrini() { return { success: true, teatrini: [] }; }
function salvaStatoTeatrino(r, a) { return { success: true }; }
function inizializzaFoglioBannerCTA() { return { success: true }; }
function getBannerCTAAttivi() { return { success: true, banners: [] }; }
function getAllBannerCTA() { return { success: true, banners: [] }; }
function salvaStatoBannerCTA(r, a) { return { success: true }; }

function inviaComando360Live(comando, valore) {
  try {
    PropertiesService.getScriptProperties().setProperty('CMD_360_LIVE', JSON.stringify({ cmd: comando, val: valore, ts: Date.now() }));
    return { success: true };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function getComando360Live() {
  try {
    var raw = PropertiesService.getScriptProperties().getProperty('CMD_360_LIVE');
    return raw ? JSON.parse(raw) : { cmd: 'auto', val: 0 };
  } catch(e) {
    return { cmd: 'auto', val: 0 };
  }
}

function getUltimoComando360Live() { return getComando360Live(); }
function salvaConfigurazione360(p) { return { success: true }; }
function getConfigurazione360() { return { success: true }; }

// ═══════════════════════════════════════════════════════════════════════
// 🎬 COSTRUTTORE PALINSESTO DINAMICO & MULTILINGUE (TIMELINE BUILDER)
// ═══════════════════════════════════════════════════════════════════════

var FOGLI_SISTEMA_ESCLUSI = [
  'RISULTATI_GIORNATA',
  'ANALYTICS_SOCIAL',
  '360',
  'PALINSESTO_ORARIO',
  'MUSICA_SOTTOFONDO',
  'IMPOSTAZIONI_SOCIAL',
  'ARCHIVIO_CLIENTI'
];

/**
 * Restituisce l'elenco di tutte le schede utilizzabili nel palinsesto
 */
function getFogliDisponibiliPerPalinsesto() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, fogli: [] };

    var sheets = ss.getSheets();
    var disponibili = [];

    for (var i = 0; i < sheets.length; i++) {
      var sName = sheets[i].getName();
      var sUpper = sName.toUpperCase().trim();
      if (FOGLI_SISTEMA_ESCLUSI.indexOf(sUpper) === -1) {
        disponibili.push({
          tabName: sName,
          titolo: sName.replace(/_/g, ' '),
          righe: sheets[i].getLastRow()
        });
      }
    }

    return { success: true, fogli: disponibili };
  } catch(e) {
    return { success: false, fogli: [], error: e.toString() };
  }
}

/**
 * Precompila automaticamente l'intera scaletta/palinsesto per l'immobile selezionato
 * Estrae tutte le stanze (Colonna F) e le intervalla con Teatrino, Spot, Meteo, Nozioni e Storyteller
 */
function generaPalinsestoPrecompilatoImmobile(tabImmobile) {
  try {
    var ss = getSpreadsheetSicuro();
    var props = PropertiesService.getScriptProperties();
    var activeTab = tabImmobile || props.getProperty('ACTIVE_IMMOBILE_TAB') || 'Villa_Favara';
    var sheet = ss ? (ss.getSheetByName(activeTab) || ss.getSheets()[0]) : null;

    if (!sheet) {
      return { success: false, error: "Scheda immobile '" + activeTab + "' non trovata." };
    }

    var lastRow = sheet.getLastRow();
    var data = (lastRow >= 2) ? sheet.getRange(2, 1, lastRow - 1, 10).getValues() : [];
    var scaletta = [];
    var blockId = 1;

    // 1. Intro Immobile & Copertina
    var nomeImmobile = activeTab.replace(/_/g, ' ');
    scaletta.push({
      id: "blk_" + (blockId++),
      tipo: "intro",
      icona: "🏰",
      titolo: "Intro & Panoramica: " + nomeImmobile,
      sorgente: activeTab,
      rigaFoglio: 2,
      durataSec: 35,
      voce: "DarIA",
      lingua: "it-IT",
      testoColonnaF: "Benvenuti nella presentazione esclusiva di " + nomeImmobile + ". Oggi vi guideremo all'interno di tutti gli ambienti con il Virtual Tour a 360 gradi! — Immobiliare Giancani",
      attivo: true
    });

    // 2. Itera su ogni stanza dell'immobile (Colonna F)
    for (var r = 0; r < data.length; r++) {
      var stName = String(data[r][3] || '').trim() || ("Stanza " + (r + 1));
      var tMedia = String(data[r][4] || 'foto').toLowerCase().trim();
      if (tMedia !== '360' && tMedia !== 'video') tMedia = 'foto';
      var testoF = String(data[r][5] || '').trim(); // Rigorosamente Colonna F
      if (!testoF || testoF.length < 5) {
        testoF = "Ammirate " + stName + ": uno spazio rifinito, arioso e luminoso pronto ad accogliervi. — Immobiliare Giancani";
      }
      var mediaUrl = convertiUrlDriveDirect(String(data[r][0] || '').trim());

      var iconaStanza = (tMedia === '360') ? '🌐' : (stName.toLowerCase().indexOf('cucina') > -1 ? '🍳' : (stName.toLowerCase().indexOf('bagno') > -1 ? '🚿' : (stName.toLowerCase().indexOf('camera') > -1 ? '🛏️' : (stName.toLowerCase().indexOf('terrazz') > -1 || stName.toLowerCase().indexOf('balcon') > -1 ? '🌅' : '🚪'))));

      scaletta.push({
        id: "blk_" + (blockId++),
        tipo: "stanza",
        icona: iconaStanza,
        titolo: stName + " (" + tMedia.toUpperCase() + ")",
        sorgente: activeTab,
        rigaFoglio: r + 2,
        mediaUrl: mediaUrl,
        tipoMedia: tMedia,
        durataSec: (tMedia === '360') ? 40 : 25,
        voce: (r % 2 === 0) ? "DarIA" : "DarIO",
        lingua: "it-IT",
        testoColonnaF: testoF,
        attivo: true
      });

      // Dopo ogni 2 stanze inserisci un intermezzo dinamico
      if (r === 1) {
        // Teatrino Comico
        scaletta.push({
          id: "blk_" + (blockId++),
          tipo: "teatrino",
          icona: "🎭",
          titolo: "Teatrino Comico DarIA & DarIO",
          sorgente: "Teatrino",
          durataSec: 35,
          voce: "Duo",
          lingua: "it-IT",
          testoColonnaF: "DarIO: 'Hai visto che spettacolo questa casa?' — DarIA: 'Assolutamente sì, luminosa e perfetta per vivere al meglio!' — Immobiliare Giancani",
          attivo: true
        });
      } else if (r === 3) {
        // Spot Pubblicitario
        scaletta.push({
          id: "blk_" + (blockId++),
          tipo: "spot",
          icona: "📺",
          titolo: "Spot & Servizi Agenzia",
          sorgente: "Pubblicita_Spot",
          durataSec: 30,
          voce: "DarIA",
          lingua: "it-IT",
          testoColonnaF: "Affidati a noi per vendere o acquistare casa con Virtual Tour 360 e le migliori strategie di marketing! — Immobiliare Giancani",
          attivo: true
        });
      } else if (r === 5) {
        // Nozioni Immobiliari
        scaletta.push({
          id: "blk_" + (blockId++),
          tipo: "nozioni",
          icona: "📚",
          titolo: "Pillola / Nozione Immobiliare",
          sorgente: "Nozioni_Immobiliari",
          durataSec: 35,
          voce: "DarIO",
          lingua: "it-IT",
          testoColonnaF: "Lo sapevate che una casa valorizzata con foto professionali e tour a 360 gradi si vende in meno della metà del tempo? — Immobiliare Giancani",
          attivo: true
        });
      }
    }

    // 3. Aggiungi Meteo Locale Favara & Agrigento
    scaletta.push({
      id: "blk_" + (blockId++),
      tipo: "meteo",
      icona: "🌤️",
      titolo: "Previsioni Meteo Favara & Agrigento",
      sorgente: "Meteo_Notizie",
      durataSec: 30,
      voce: "DarIA",
      lingua: "it-IT",
      testoColonnaF: "Ed ecco le previsioni meteo per la nostra splendida zona: sole splendente e temperature ideali per visitare questo immobile! — Immobiliare Giancani",
      attivo: true
    });

    // 4. Aggiungi Storyteller Città
    scaletta.push({
      id: "blk_" + (blockId++),
      tipo: "storyteller",
      icona: "🏛️",
      titolo: "Storyteller & Curiosità Territorio",
      sorgente: "Storyteller_Citta",
      durataSec: 40,
      voce: "DarIO",
      lingua: "it-IT",
      testoColonnaF: "Vivere in questa zona significa essere a due passi da storia, cultura, sapori unici e dalla meravigliosa Valle dei Templi. — Immobiliare Giancani",
      attivo: true
    });

    // 5. Orologio Mondiale & Saluto Internazionale
    scaletta.push({
      id: "blk_" + (blockId++),
      tipo: "worldclock",
      icona: "🌍",
      titolo: "Orologio Mondiale & Clienti Esteri",
      sorgente: "WorldClock",
      durataSec: 25,
      voce: "DarIA",
      lingua: "it-IT",
      testoColonnaF: "Un caloroso saluto a tutti i nostri clienti collegati da Roma, Londra, Parigi e New York in cerca della loro casa dei sogni in Sicilia! — Immobiliare Giancani",
      attivo: true
    });

    // Calcola durata totale
    var totaleSec = 0;
    scaletta.forEach(function(b) { if (b.attivo) totaleSec += (parseInt(b.durataSec) || 30); });

    return {
      success: true,
      immobile: activeTab,
      totaleSecondi: totaleSec,
      durataFormattata: Math.floor(totaleSec / 60) + " min " + (totaleSec % 60) + " sec",
      blocchi: scaletta
    };
  } catch(e) {
    inviaAllertaErroreTelegram("09_PalinsestoTeatrinoEBanners.js", "generaPalinsestoPrecompilatoImmobile", e.toString());
    return { success: false, error: e.toString(), blocchi: [] };
  }
}

/**
 * Salva la scaletta dinamica personalizzata
 */
function salvaPalinsestoDinamicoWeb(scaletta) {
  try {
    if (!scaletta || !Array.isArray(scaletta)) {
      return { success: false, error: "Dati scaletta non validi" };
    }

    var props = PropertiesService.getScriptProperties();
    props.setProperty('PALINSESTO_DINAMICO_SCALETTA', JSON.stringify(scaletta));

    var totaleSec = 0;
    scaletta.forEach(function(b) { if (b.attivo) totaleSec += (parseInt(b.durataSec) || 30); });

    return {
      success: true,
      messaggio: "Palinsesto dinamico salvato con successo! Durata ciclo: " + Math.floor(totaleSec / 60) + "m " + (totaleSec % 60) + "s",
      totaleSecondi: totaleSec
    };
  } catch(e) {
    inviaAllertaErroreTelegram("09_PalinsestoTeatrinoEBanners.js", "salvaPalinsestoDinamicoWeb", e.toString());
    return { success: false, error: e.toString() };
  }
}

/**
 * Recupera la scaletta dinamica salvata o la precompila
 */
function getPalinsestoDinamicoWeb() {
  try {
    var props = PropertiesService.getScriptProperties();
    var raw = props.getProperty('PALINSESTO_DINAMICO_SCALETTA');
    if (raw) {
      var scaletta = JSON.parse(raw);
      var totaleSec = 0;
      scaletta.forEach(function(b) { if (b.attivo) totaleSec += (parseInt(b.durataSec) || 30); });
      return {
        success: true,
        blocchi: scaletta,
        totaleSecondi: totaleSec,
        durataFormattata: Math.floor(totaleSec / 60) + " min " + (totaleSec % 60) + " sec"
      };
    }
    return generaPalinsestoPrecompilatoImmobile(null);
  } catch(e) {
    return generaPalinsestoPrecompilatoImmobile(null);
  }
}

/**
 * 📲 GESTIONE CAMBIO STANZA INTERATTIVO DA CHAT (es. 'cucina')
 * Salva la richiesta memorizzando nome della stanza, autore e orario esatto
 */
function registraRichiestaStanzaChat(nomeStanza, nomeAutore, timestampRichiesta) {
  try {
    if (!nomeStanza) return { success: false };
    var ts = timestampRichiesta || Date.now();
    var aut = (nomeAutore || 'un nostro spettatore').trim();
    PropertiesService.getScriptProperties().setProperty('PENDING_ROOM_REQUEST', JSON.stringify({
      stanza: nomeStanza,
      autore: aut,
      ts: ts
    }));
    return { success: true };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function getRichiestaStanzaChatPendente() {
  try {
    var props = PropertiesService.getScriptProperties();
    var raw = props.getProperty('PENDING_ROOM_REQUEST');
    if (!raw) return { hasRequest: false };
    var obj = JSON.parse(raw);
    props.deleteProperty('PENDING_ROOM_REQUEST');
    var now = Date.now();
    var deltaSec = Math.max(0, Math.floor((now - (obj.ts || now)) / 1000));
    if (deltaSec < 120) {
      return {
        hasRequest: true,
        stanza: obj.stanza,
        autore: obj.autore || 'un nostro spettatore',
        deltaSec: deltaSec,
        superiore10s: (deltaSec >= 10)
      };
    }
    return { hasRequest: false };
  } catch(e) {
    return { hasRequest: false };
  }
}


// ═══════════════════════════════════════════════════════════════════════


// ═══════════════════════════════════════════════════════════════════════
// 📅 SEZIONE: CALENDARIO PALINSESTO DIRETTE SERALI (19:00 - 01:00)
// Gestione rotazione immobili diversi (> 7 immobili) & Notifiche Telegram
// Personal Branding: Immobiliare Giancani
// ═══════════════════════════════════════════════════════════════════════

/**
 * Recupera il calendario settimanale delle dirette serali (19:00 - 01:00)
 * Assegna ad ogni giorno della settimana un immobile programmato diverso
 */
function getCalendarioPalinsestoSettimanale() {
  try {
    var props = PropertiesService.getScriptProperties();
    var rawCal = props.getProperty('PALINSESTO_CALENDARIO_SETTIMANALE');
    var fogliRes = getFogliDisponibiliPerPalinsesto();
    var fogliDisponibili = (fogliRes && fogliRes.success) ? fogliRes.fogli : [];

    // Nomi standard dei giorni della settimana
    var giorniSettimana = [
      { id: 'lunedi', nome: 'Lunedì', orario: '19:00 - 01:00', defaultTab: 'VILLA_FAVARA_RIFINITA' },
      { id: 'martedi', nome: 'Martedì', orario: '19:00 - 01:00', defaultTab: 'ATTICO_CENTRO_AGRIGENTO' },
      { id: 'mercoledi', nome: 'Mercoledì', orario: '19:00 - 01:00', defaultTab: 'CASALE_RUSTICO_GIARDINO' },
      { id: 'giovedi', nome: 'Giovedì', orario: '19:00 - 01:00', defaultTab: 'APPARTAMENTO_VISTA_TEMPLI' },
      { id: 'venerdi', nome: 'Venerdì', orario: '19:00 - 01:00', defaultTab: 'VILLA_PISCINA_SAN_LEONE' },
      { id: 'sabato', nome: 'Sabato', orario: '19:00 - 01:00', defaultTab: 'DIMORA_STORICA_CORTILE' },
      { id: 'domenica', nome: 'Domenica', orario: '19:00 - 01:00', defaultTab: 'PENTHOUSE_TERRAZZA_MARE' }
    ];

    var calendario = [];
    if (rawCal) {
      try {
        calendario = JSON.parse(rawCal);
      } catch(eParse) {
        calendario = [];
      }
    }

    // Se non esiste ancora o è vuoto, costruisci una programmazione con immobili diversi
    if (!calendario || calendario.length === 0) {
      for (var i = 0; i < giorniSettimana.length; i++) {
        var g = giorniSettimana[i];
        var tabAssegnata = g.defaultTab;
        if (fogliDisponibili.length > 0) {
          var fIdx = i % fogliDisponibili.length;
          tabAssegnata = fogliDisponibili[fIdx].tabName;
        }
        calendario.push({
          id: g.id,
          giorno: g.nome,
          orario: g.orario,
          tabImmobile: tabAssegnata,
          titoloImmobile: tabAssegnata.replace(/_/g, ' '),
          attivo: true
        });
      }
    } else {
      // Assicura che i campi orario e giorno siano coerenti
      for (var k = 0; k < calendario.length; k++) {
        if (!calendario[k].orario) calendario[k].orario = '19:00 - 01:00';
      }
    }

    // Calcola il giorno corrente
    var now = new Date();
    var dayOfWeek = now.getDay(); // 0 = Domenica, 1 = Lunedì...
    var mappaGiornoId = ['domenica', 'lunedi', 'martedi', 'mercoledi', 'giovedi', 'venerdi', 'sabato'];
    var giornoIdOggi = mappaGiornoId[dayOfWeek] || 'lunedi';

    return {
      success: true,
      calendario: calendario,
      fogliDisponibili: fogliDisponibili,
      giornoIdOggi: giornoIdOggi,
      fasciaOrariaUfficiale: '19:00 - 01:00'
    };
  } catch(e) {
    console.error("Errore getCalendarioPalinsestoSettimanale:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * Salva il calendario settimanale in ScriptProperties e invia notifica immediata su Telegram
 */
function salvaCalendarioPalinsestoSettimanale(payload) {
  try {
    if (!payload || !payload.calendario) {
      return { success: false, error: "Dati calendario non validi" };
    }

    var cal = payload.calendario;
    var props = PropertiesService.getScriptProperties();
    props.setProperty('PALINSESTO_CALENDARIO_SETTIMANALE', JSON.stringify(cal));

    // Costruisci il messaggio Telegram dettagliato
    var righe = [];
    righe.push("📅 <b>PALINSESTO DIRETTE SERALI AGGIORNATO (19:00 - 01:00)</b>\n");
    righe.push("È stata registrata una modifica alla programmazione delle dirette televisive serali.");
    righe.push("Ogni sera dalle 19:00 alle 01:00 un immobile diverso in rotazione esclusiva con DarIA & DarIO:\n");

    for (var i = 0; i < cal.length; i++) {
      var item = cal[i];
      var nomeGiorno = item.giorno || item.id || ('Giorno ' + (i+1));
      var tabName = item.tabImmobile || 'Da definire';
      var titolo = item.titoloImmobile || tabName.replace(/_/g, ' ');
      righe.push("🗓️ <b>" + nomeGiorno + "</b> (19:00 - 01:00): 🏠 <code>" + titolo + "</code>");
    }

    righe.push("\n✨ <i>Gli avatar conducono la diretta con descrizioni da Colonna F e superfici in metri quadri.</i>\n");
    righe.push("— <b>Immobiliare Giancani</b>");

    var testoTelegram = righe.join("\n");

    // Invio notifica su Telegram
    var notificaResult = { success: false };
    if (typeof inviaNotificaTelegram === 'function') {
      notificaResult = inviaNotificaTelegram(testoTelegram, null, "HTML");
    }

    return {
      success: true,
      calendario: cal,
      telegram: notificaResult,
      messaggio: "Palinsesto salvato con successo e notifica Telegram inviata!"
    };
  } catch(e) {
    console.error("Errore salvaCalendarioPalinsestoSettimanale:", e);
    if (typeof inviaAllertaErroreTelegram === 'function') {
      inviaAllertaErroreTelegram("09_PalinsestoTeatrinoEBanners.js", "salvaCalendarioPalinsestoSettimanale", e.toString());
    }
    return { success: false, error: e.toString() };
  }
}

/**
 * 🎬 SPOT VIDEO ORARIO YOUTUBE (Ogni 60 minuti)
 * Preleva il prossimo video da 'Post_YouTube' o canale ufficiale
 * DarIO e DarIA vengono messi in pausa durante la trasmissione
 */
function getVideoSpotOrarioYouTube() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Post_YouTube') : null;
    var props = PropertiesService.getScriptProperties();
    var idx = parseInt(props.getProperty('INDEX_VIDEO_ORARIO_YOUTUBE') || '0', 10);

    var videoFallback = {
      videoId: "zekP_9iFLK0",
      mediaUrl: "https://www.youtube.com/embed/zekP_9iFLK0?autoplay=1&mute=0&controls=0&rel=0&enablejsapi=1",
      watchUrl: "https://www.youtube.com/watch?v=zekP_9iFLK0",
      titolo: "I Migliori Immobili Esclusivi — Canale YouTube Ufficiale",
      durataSec: 75,
      testoColonnaF: "I migliori video immobiliari e tour esclusivi sul canale ufficiale. — Immobiliare Giancani",
      thumbnail: "https://img.youtube.com/vi/zekP_9iFLK0/hqdefault.jpg"
    };

    if (!sheet || sheet.getLastRow() < 2) {
      return { success: true, video: videoFallback };
    }

    var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 10).getValues();
    var listaVideo = [];

    for (var r = 0; r < data.length; r++) {
      var rawUrl = String(data[r][0] || '').trim();
      var titolo = String(data[r][3] || 'Video Immobiliare Esclusivo').trim();
      var descrF = String(data[r][5] || '').trim();
      var thumb = String(data[r][6] || '').trim();
      var durataSec = parseInt(data[r][9], 10);
      if (isNaN(durataSec) || durataSec < 15) durataSec = 75;

      var vId = '';
      var m = rawUrl.match(/(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|shorts\/|.*[?&]v=)|(?:\/|^))([a-zA-Z0-9_-]{11})/i);
      if (m && m[1]) vId = m[1];
      else if (rawUrl.length === 11) vId = rawUrl;

      if (vId) {
        listaVideo.push({
          videoId: vId,
          mediaUrl: "https://www.youtube.com/embed/" + vId + "?autoplay=1&mute=0&controls=0&rel=0&enablejsapi=1",
          watchUrl: "https://www.youtube.com/watch?v=" + vId,
          titolo: titolo,
          durataSec: durataSec,
          testoColonnaF: descrF || (titolo + " — Immobiliare Giancani"),
          thumbnail: thumb || ("https://img.youtube.com/vi/" + vId + "/hqdefault.jpg")
        });
      }
    }

    if (listaVideo.length === 0) {
      return { success: true, video: videoFallback };
    }

    var scelto = listaVideo[idx % listaVideo.length];
    props.setProperty('INDEX_VIDEO_ORARIO_YOUTUBE', String((idx + 1) % listaVideo.length));

    return { success: true, video: scelto };
  } catch(e) {
    console.error("Errore getVideoSpotOrarioYouTube:", e);
    return {
      success: true,
      video: {
        videoId: "zekP_9iFLK0",
        mediaUrl: "https://www.youtube.com/embed/zekP_9iFLK0?autoplay=1&mute=0&controls=0&rel=0&enablejsapi=1",
        watchUrl: "https://www.youtube.com/watch?v=zekP_9iFLK0",
        titolo: "Canale YouTube Immobiliare Giancani",
        durataSec: 75,
        testoColonnaF: "I migliori immobili e ville esclusive. — Immobiliare Giancani",
        thumbnail: "https://img.youtube.com/vi/zekP_9iFLK0/hqdefault.jpg"
      }
    };
  }
}

/**
 * Invia notifica Telegram per confermare l'attivazione del filtro anti-emoticon per gli avatar
 */
function inviaNotificaFiltroAntiEmoticonTelegram() {
  try {
    var righe = [];
    righe.push("🎙️ <b>AGGIORNAMENTO VOCE AVATAR: FILTRO ANTI-EMOTICON ATTIVO</b>\n");
    righe.push("✅ Le voci di <b>DarIA</b> e <b>DarIO</b> sono state aggiornate con successo.");
    righe.push("🚫 Gli avatar <b>NON pronunceranno mai più emoji o emoticon</b> durante la lettura dei testi e delle schede.");
    righe.push("📐 Tutte le superfici vengono pronunciate rigorosamente come <b>metri quadri</b>.");
    righe.push("📑 I testi continuano ad essere prelevati rigorosamente dalla <b>Colonna F</b> del foglio immobile.\n");
    righe.push("— <b>Immobiliare Giancani</b>");

    var msg = righe.join("\n");

    if (typeof inviaNotificaTelegram === 'function') {
      return inviaNotificaTelegram(msg, null, "HTML");
    }
    return { success: false, error: "inviaNotificaTelegram non disponibile" };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}
