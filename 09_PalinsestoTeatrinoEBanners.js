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
  'IMPOSTAZIONI_SOCIAL',
  'PUBBLICITA_SPOT',
  'CALCIO_FRASI',
  'FRASI_CALCIO',
  'RISULTATI_CALCIO',
  'RISULTATI_GIORNATA',
  'CONFIGURAZIONE_TEMPI',
  'TEATRINO',
  'TEATRINO_COMICO',
  'BANNER_CTA',
  'REPORT_PROPRIETARIO',
  'REGIA_IMMOBILE',
  '360',
  'PALINSESTO_ORARIO',
  'MUSICA_SOTTOFONDO',
  'ARCHIVIO_CLIENTI',
  'ANALYTICS_SOCIAL',
  'POST_FACEBOOK',
  'POST_YOUTUBE',
  'PUBBLICITA_SCHERMO_CENTRALE',
  'NOTIZIE_SPORT_ATTUALITA',
  'NOZIONI_IMMOBILIARI',
  'DIRETTA_O_DARIA_E_DARIO_INFLUENCER',
  'DIALOGHI_DUO',
  'STORYTELLER_CITTA',
  'BATTUTE_DARIO',
  'STORIE_FAVARA_AGRIGENTO',
  'STORIE_CITTA',
  'NOTIZIE_CITTA'
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
      var lastR = sheets[i].getLastRow();
      if (FOGLI_SISTEMA_ESCLUSI.indexOf(sUpper) === -1 && lastR >= 2) {
        disponibili.push({
          tabName: sName,
          titolo: sName.replace(/_/g, ' '),
          righe: lastR
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
// ═══════════════════════════════════════════════════════════════════════
// 📅 SEZIONE: CALENDARIO PALINSESTO DIRETTE SERALI (19:00 - 01:00)
// 🔄 EQUA ROTAZIONE AD ESAURIMENTO COMPLETO: NESSUNA RIPETIZIONE
//    Finché tutti gli immobili non sono andati in onda nel ciclo corrente!
// Personal Branding: Immobiliare Giancani
// ═══════════════════════════════════════════════════════════════════════

/**
 * Restituisce lo stato dettagliato dell'equa rotazione ad esaurimento completo
 */
function getDatiRotazioneEqua() {
  try {
    var props = PropertiesService.getScriptProperties();
    var rawRot = props.getProperty('ROTAZIONE_EQUA_STATO');
    var fogliRes = getFogliDisponibiliPerPalinsesto();
    var tuttiFogli = (fogliRes && fogliRes.success) ? fogliRes.fogli : [];

    var stato = null;
    if (rawRot) {
      try {
        stato = JSON.parse(rawRot);
      } catch(e) { stato = null; }
    }

    if (!stato) {
      stato = {
        cicloAttivo: 1,
        andatiInOnda: [],
        storicoDate: {},
        cicliCompletati: 0,
        ultimoAggiornamento: new Date().toISOString()
      };
    }

    // Mappa di tutti i tabName validi a catalogo
    var tuttiTabMap = {};
    var tuttiTabList = [];
    for (var i = 0; i < tuttiFogli.length; i++) {
      var tName = tuttiFogli[i].tabName;
      tuttiTabMap[tName] = tuttiFogli[i];
      tuttiTabList.push(tName);
    }

    // Pulisci andatiInOnda da eventuali tab eliminate o duplicate
    var andatiFiltrati = [];
    var andatiSet = {};
    for (var j = 0; j < (stato.andatiInOnda || []).length; j++) {
      var aTab = stato.andatiInOnda[j];
      if (tuttiTabMap[aTab] && !andatiSet[aTab]) {
        andatiFiltrati.push(aTab);
        andatiSet[aTab] = true;
      }
    }
    stato.andatiInOnda = andatiFiltrati;

    // Calcola rimanenti che NON sono ancora andati in onda
    var rimanenti = [];
    for (var k = 0; k < tuttiTabList.length; k++) {
      var candTab = tuttiTabList[k];
      if (!andatiSet[candTab]) {
        rimanenti.push(candTab);
      }
    }

    var totale = tuttiTabList.length;
    var cicloCompleto = (totale > 0 && rimanenti.length === 0);

    return {
      success: true,
      cicloAttivo: stato.cicloAttivo || 1,
      cicliCompletati: stato.cicliCompletati || 0,
      totaleImmobili: totale,
      andatiInOnda: stato.andatiInOnda,
      conteggioAndatiInOnda: stato.andatiInOnda.length,
      rimanenti: rimanenti,
      conteggioRimanenti: rimanenti.length,
      percentualeAvanzamento: totale > 0 ? Math.round((stato.andatiInOnda.length / totale) * 100) : 0,
      cicloCompleto: cicloCompleto,
      programmaSeraleAttivo: props.getProperty('PROGRAMMA_SERALE_ATTIVO') !== 'false',
      tuttiFogli: tuttiFogli,
      storicoDate: stato.storicoDate || {}
    };
  } catch(e) {
    console.error("Errore getDatiRotazioneEqua:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * Registra che un immobile è andato in onda stasera.
 * Se tutti gli immobili del catalogo hanno completato il giro, chiude il ciclo corrente
 * con notifica Telegram e resetta la coda per il nuovo ciclo equo.
 */
function registraImmobileAndatoInOnda(tabName) {
  try {
    if (!tabName) return { success: false, error: "Nome tab non specificato" };
    var props = PropertiesService.getScriptProperties();
    var rotData = getDatiRotazioneEqua();
    if (!rotData.success) return rotData;

    var andati = rotData.andatiInOnda.slice();
    var storicoDate = rotData.storicoDate || {};
    var ciclo = rotData.cicloAttivo;
    var completati = rotData.cicliCompletati;
    var oraIso = new Date().toISOString();

    if (andati.indexOf(tabName) === -1) {
      andati.push(tabName);
    }
    storicoDate[tabName] = oraIso;

    var totale = rotData.totaleImmobili;
    var cicloFinitoOra = (totale > 0 && andati.length >= totale);

    if (cicloFinitoOra) {
      completati++;
      var nuovoCiclo = ciclo + 1;
      var nuovoStato = {
        cicloAttivo: nuovoCiclo,
        andatiInOnda: [], // Reset per il nuovo ciclo
        storicoDate: storicoDate,
        cicliCompletati: completati,
        ultimoAggiornamento: oraIso
      };
      props.setProperty('ROTAZIONE_EQUA_STATO', JSON.stringify(nuovoStato));

      // Notifica Telegram di traguardo ciclo completato
      if (typeof inviaNotificaTelegram === 'function') {
        var msgCiclo = "🎉 <b>CICLO DI EQUA ROTAZIONE COMPLETATO!</b> 🏆✨\n\n" +
                       "Tutti i <b>" + totale + " immobili a catalogo</b> sono andati in onda nella diretta serale (19:00 - 01:00).\n" +
                       "Nessun immobile è stato trascurato: a ciascun proprietario è stata garantita parità di esposizione su tutti i canali!\n\n" +
                       "🔄 <b>AVVIO AUTOMATICO CICLO #" + nuovoCiclo + "</b>: la rotazione equa riparte con lo stesso principio rigoroso.\n\n" +
                       "— <b>Immobiliare Giancani</b>";
        inviaNotificaTelegram(msgCiclo, null, "HTML");
      }

      return {
        success: true,
        cicloFinito: true,
        cicloCompletato: ciclo,
        nuovoCiclo: nuovoCiclo,
        messaggio: "Ciclo #" + ciclo + " completato! Avviato Ciclo #" + nuovoCiclo
      };
    } else {
      var statoAggiornato = {
        cicloAttivo: ciclo,
        andatiInOnda: andati,
        storicoDate: storicoDate,
        cicliCompletati: completati,
        ultimoAggiornamento: oraIso
      };
      props.setProperty('ROTAZIONE_EQUA_STATO', JSON.stringify(statoAggiornato));
      return {
        success: true,
        cicloFinito: false,
        cicloAttivo: ciclo,
        andatiCount: andati.length,
        rimanentiCount: Math.max(0, totale - andati.length)
      };
    }
  } catch(e) {
    console.error("Errore registraImmobileAndatoInOnda:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * Resetta manualmente il ciclo di rotazione equa
 */
function resetCicloRotazioneEqua() {
  try {
    var props = PropertiesService.getScriptProperties();
    var rotData = getDatiRotazioneEqua();
    var nuovoStato = {
      cicloAttivo: (rotData.cicloAttivo || 1) + 1,
      andatiInOnda: [],
      storicoDate: rotData.storicoDate || {},
      cicliCompletati: rotData.cicliCompletati || 0,
      ultimoAggiornamento: new Date().toISOString()
    };
    props.setProperty('ROTAZIONE_EQUA_STATO', JSON.stringify(nuovoStato));
    return { success: true, messaggio: "Ciclo resettato con successo.", stato: getDatiRotazioneEqua() };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 🔄 AUTO-PROGRAMMA ROTAZIONE EQUA SENZA RIPETIZIONI (7 GIORNI)
 * Assegna ai 7 giorni della settimana esclusivamente gli immobili che NON sono ancora
 * andati in onda nel ciclo corrente. Se i rimanenti sono meno di 7, chiude il ciclo e
 * preleva i restanti dal ciclo successivo: NESSUN IMMOBILE SI RIPETE PRIMA CHE TUTTI ABBIANO TRASMESSO.
 */
function autoProgrammaRotazioneEquaSettimanale() {
  try {
    var rotData = getDatiRotazioneEqua();
    if (!rotData.success) return rotData;

    var tuttiFogli = rotData.tuttiFogli || [];
    if (tuttiFogli.length === 0) {
      return { success: false, error: "Nessun immobile disponibile a catalogo." };
    }

    var giorniSettimana = [
      { id: 'lunedi', nome: 'Lunedì', orario: '19:00 - 01:00' },
      { id: 'martedi', nome: 'Martedì', orario: '19:00 - 01:00' },
      { id: 'mercoledi', nome: 'Mercoledì', orario: '19:00 - 01:00' },
      { id: 'giovedi', nome: 'Giovedì', orario: '19:00 - 01:00' },
      { id: 'venerdi', nome: 'Venerdì', orario: '19:00 - 01:00' },
      { id: 'sabato', nome: 'Sabato', orario: '19:00 - 01:00' },
      { id: 'domenica', nome: 'Domenica', orario: '19:00 - 01:00' }
    ];

    var rimanenti = rotData.rimanenti.slice();
    // Se non ci sono rimanenti (ciclo già al 100%), tutti tornano disponibili per il nuovo ciclo
    if (rimanenti.length === 0) {
      for (var f = 0; f < tuttiFogli.length; f++) {
        rimanenti.push(tuttiFogli[f].tabName);
      }
    }

    // Pool sequenziale di selezione equa senza ripetizioni
    var codaScelta = rimanenti.slice();
    // Se la coda ha meno di 7 elementi, aggiungi dal catalogo generale (nuovo ciclo) evitando duplicati immediati
    if (codaScelta.length < giorniSettimana.length) {
      for (var k = 0; k < tuttiFogli.length; k++) {
        var tCand = tuttiFogli[k].tabName;
        if (codaScelta.indexOf(tCand) === -1) {
          codaScelta.push(tCand);
          if (codaScelta.length >= giorniSettimana.length) break;
        }
      }
    }

    // Mappa rapida tabName -> titolo
    var titoloMap = {};
    for (var m = 0; m < tuttiFogli.length; m++) {
      titoloMap[tuttiFogli[m].tabName] = tuttiFogli[m].titolo;
    }

    var nuovoCalendario = [];
    for (var i = 0; i < giorniSettimana.length; i++) {
      var g = giorniSettimana[i];
      var tabScelto = codaScelta[i % codaScelta.length] || (tuttiFogli[0] ? tuttiFogli[0].tabName : 'VILLA_FAVARA_RIFINITA');
      var titScelto = titoloMap[tabScelto] || tabScelto.replace(/_/g, ' ');

      nuovoCalendario.push({
        id: g.id,
        giorno: g.nome,
        orario: g.orario,
        tabImmobile: tabScelto,
        titoloImmobile: titScelto,
        attivo: true
      });
    }

    // Salva il nuovo calendario programmato
    salvaCalendarioPalinsestoSettimanale({ calendario: nuovoCalendario, skipTelegram: false });

    return {
      success: true,
      calendario: nuovoCalendario,
      statoRotazione: getDatiRotazioneEqua(),
      messaggio: "Palinsesto programmato con equa rotazione! Nessun immobile ripetuto prima dell'esaurimento del catalogo."
    };
  } catch(e) {
    console.error("Errore autoProgrammaRotazioneEquaSettimanale:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * Recupera il calendario settimanale delle dirette serali (19:00 - 01:00)
 * Inclusivo di stato di equa rotazione e giorno attivo
 */
function getCalendarioPalinsestoSettimanale() {
  try {
    var props = PropertiesService.getScriptProperties();
    var rawCal = props.getProperty('PALINSESTO_CALENDARIO_SETTIMANALE');
    var fogliRes = getFogliDisponibiliPerPalinsesto();
    var fogliDisponibili = (fogliRes && fogliRes.success) ? fogliRes.fogli : [];
    var rotData = getDatiRotazioneEqua();

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
      for (var k = 0; k < calendario.length; k++) {
        if (!calendario[k].orario) calendario[k].orario = '19:00 - 01:00';
      }
    }

    // Giorno corrente in orario Roma
    var nowRome = new Date(new Date().toLocaleString("en-US", { timeZone: "Europe/Rome" }));
    var dayOfWeek = nowRome.getDay(); // 0 = Domenica, 1 = Lunedì...
    var mappaGiornoId = ['domenica', 'lunedi', 'martedi', 'mercoledi', 'giovedi', 'venerdi', 'sabato'];
    var giornoIdOggi = mappaGiornoId[dayOfWeek] || 'lunedi';

    return {
      success: true,
      calendario: calendario,
      fogliDisponibili: fogliDisponibili,
      giornoIdOggi: giornoIdOggi,
      fasciaOrariaUfficiale: '19:00 - 01:00',
      rotazioneEqua: rotData,
      programmaSeraleAttivo: props.getProperty('PROGRAMMA_SERALE_ATTIVO') !== 'false'
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

    // Assicura l'installazione dei trigger automatici 19:00 - 01:00
    assicuraTriggerProgrammaSerale();

    var rotData = getDatiRotazioneEqua();

    // Costruisci il messaggio Telegram dettagliato
    var righe = [];
    righe.push("📅 <b>PALINSESTO DIRETTE SERALI AGGIORNATO (19:00 - 01:00)</b>\n");
    righe.push("Programmazione ufficiale delle dirette serali con regola di <b>Equa Rotazione ad Esaurimento</b>.");
    righe.push("<i>Nessun immobile si ripete prima che tutti gli altri abbiano effettuato il passaggio in diretta.</i>\n");
    righe.push("📊 <b>Stato Rotazione:</b> Ciclo #" + (rotData.cicloAttivo || 1) + " • " + (rotData.conteggioAndatiInOnda || 0) + "/" + (rotData.totaleImmobili || 0) + " già andati in onda (" + (rotData.percentualeAvanzamento || 0) + "% completato)\n");

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

    var notificaResult = { success: false };
    if (!payload.skipTelegram && typeof inviaNotificaTelegram === 'function') {
      notificaResult = inviaNotificaTelegram(testoTelegram, null, "HTML");
    }

    return {
      success: true,
      calendario: cal,
      telegram: notificaResult,
      rotazioneEqua: rotData,
      messaggio: "Palinsesto serale (19:00 - 01:00) salvato con successo e notifica Telegram inviata!"
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
 * Restituisce l'immobile designato per stasera dal palinsesto serale (19:00 - 01:00)
 */
function getImmobileSeraleDelGiorno() {
  try {
    var calRes = getCalendarioPalinsestoSettimanale();
    if (!calRes || !calRes.success || !calRes.calendario) return null;

    var gId = calRes.giornoIdOggi || 'lunedi';
    for (var i = 0; i < calRes.calendario.length; i++) {
      if (calRes.calendario[i].id === gId) {
        return {
          tabName: calRes.calendario[i].tabImmobile,
          titolo: calRes.calendario[i].titoloImmobile,
          giorno: calRes.calendario[i].giorno,
          orario: calRes.calendario[i].orario
        };
      }
    }
    return null;
  } catch(e) {
    console.error("Errore getImmobileSeraleDelGiorno:", e);
    return null;
  }
}

/**
 * ⏰ ESECUZIONE AUTOMATICA SERALE ALLE ORE 19:00
 * Attiva l'immobile del giorno, lo registra nella rotazione equa,
 * aggiorna la regia e invia notifica Telegram istituzionale.
 */
function eseguiCheckPalinsestoSerale19_01() {
  try {
    var props = PropertiesService.getScriptProperties();
    var attivo = props.getProperty('PROGRAMMA_SERALE_ATTIVO') !== 'false';
    if (!attivo) {
      console.log("Programma serale disattivato dall'utente.");
      return;
    }

    var immSerale = getImmobileSeraleDelGiorno();
    if (!immSerale || !immSerale.tabName) {
      console.warn("Nessun immobile programmato trovato per stasera.");
      return;
    }

    // 1. Imposta l'immobile attivo nella regia
    props.setProperty('ACTIVE_IMMOBILE_TAB', immSerale.tabName);

    // 2. Registra l'immobile come andato in onda nel ciclo equo
    var regRes = registraImmobileAndatoInOnda(immSerale.tabName);

    // 3. Notifica Telegram ufficiale di inizio diretta serale
    if (typeof inviaNotificaTelegram === 'function') {
      var rot = getDatiRotazioneEqua();
      var msg = "🌙 <b>INIZIO DIRETTA SERALE (19:00 - 01:00)!</b> 🏠✨\n\n" +
                "I conduttori <b>DarIA</b> e <b>DarIO</b> sono in onda con la presentazione esclusiva di:\n" +
                "🏠 <b>" + (immSerale.titolo || immSerale.tabName.replace(/_/g, ' ')).toUpperCase() + "</b>\n\n" +
                "📊 <b>Equa Rotazione:</b> " + (rot.conteggioAndatiInOnda || 1) + " di " + (rot.totaleImmobili || 20) + " immobili andati in onda (Ciclo #" + (rot.cicloAttivo || 1) + ")\n" +
                "📐 Descrizioni dettagliate da <b>Colonna F</b> con superfici espresse in <b>metri quadri</b>.\n" +
                "💬 Gli spettatori possono richiedere le singole stanze nei commenti live!\n\n" +
                "— <b>Immobiliare Giancani</b>";
      inviaNotificaTelegram(msg, null, "HTML");
    }

    // 4. Se è configurata la diretta streaming, assicurati che sia attiva
    if (typeof avviaDirettaMultistream === 'function' && props.getProperty('AUTO_STREAM_START_SERALE') === 'true') {
      avviaDirettaMultistream();
    }
  } catch(e) {
    console.error("Errore eseguiCheckPalinsestoSerale19_01:", e);
    if (typeof inviaAllertaErroreTelegram === 'function') {
      inviaAllertaErroreTelegram("09_PalinsestoTeatrinoEBanners.js", "eseguiCheckPalinsestoSerale19_01", e.toString());
    }
  }
}

/**
 * ⏰ CHIUSURA AUTOMATICA SERALE ALLE ORE 01:00
 * Conclude la sessione serale e predispone il sistema per il giorno successivo.
 */
function eseguiChiusuraPalinsestoSerale01() {
  try {
    var props = PropertiesService.getScriptProperties();
    var attivo = props.getProperty('PROGRAMMA_SERALE_ATTIVO') !== 'false';
    if (!attivo) return;

    if (typeof inviaNotificaTelegram === 'function') {
      var msg = "🏁 <b>FINE DIRETTA SERALE (19:00 - 01:00)</b> 🌙\n\n" +
                "La trasmissione serale si è conclusa regolarmente.\n" +
                "I nostri avatar DarIA e DarIO torneranno in onda domani sera alle 19:00 con il prossimo immobile in equa rotazione.\n\n" +
                "— <b>Immobiliare Giancani</b>";
      inviaNotificaTelegram(msg, null, "HTML");
    }
  } catch(e) {
    console.error("Errore eseguiChiusuraPalinsestoSerale01:", e);
  }
}

/**
 * Attiva o disattiva l'azionamento automatico del programma serale (19:00 - 01:00)
 */
function attivaProgrammaSeraleAutomatico(attivo) {
  try {
    var props = PropertiesService.getScriptProperties();
    var statoBool = (attivo === true || attivo === 'true');
    props.setProperty('PROGRAMMA_SERALE_ATTIVO', statoBool ? 'true' : 'false');

    if (statoBool) {
      assicuraTriggerProgrammaSerale();
    }

    if (typeof inviaNotificaTelegram === 'function') {
      var icona = statoBool ? "🟢" : "🔴";
      var statoTesto = statoBool ? "ATTIVATO (19:00 - 01:00)" : "DISATTIVATO";
      inviaNotificaTelegram(icona + " <b>PROGRAMMA SERALE AUTOMATICO " + statoTesto + "</b>\n\n" +
                            "Modalità: Equa Rotazione senza ripetizioni fino a catalogo esaurito.\n\n" +
                            "— <b>Immobiliare Giancani</b>", null, "HTML");
    }

    return {
      success: true,
      attivo: statoBool,
      messaggio: "Programma serale automatico " + (statoBool ? "attivato" : "disattivato") + " con successo."
    };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * Assicura l'esistenza dei trigger giornalieri per le 19:00 e 01:00 senza duplicati
 */
function assicuraTriggerProgrammaSerale() {
  try {
    var triggers = ScriptApp.getProjectTriggers();
    var has19 = false;
    var has01 = false;
    for (var i = 0; i < triggers.length; i++) {
      var hf = triggers[i].getHandlerFunction();
      if (hf === 'eseguiCheckPalinsestoSerale19_01') has19 = true;
      if (hf === 'eseguiChiusuraPalinsestoSerale01') has01 = true;
    }

    if (!has19) {
      ScriptApp.newTrigger('eseguiCheckPalinsestoSerale19_01')
        .timeBased()
        .atHour(19)
        .everyDays(1)
        .inTimezone('Europe/Rome')
        .create();
    }
    if (!has01) {
      ScriptApp.newTrigger('eseguiChiusuraPalinsestoSerale01')
        .timeBased()
        .atHour(1)
        .everyDays(1)
        .inTimezone('Europe/Rome')
        .create();
    }
  } catch(e) {
    console.warn("assicuraTriggerProgrammaSerale:", e);
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




// ═══════════════════════════════════════════════════════════════════════
// 📺 GESTORE SCHERMO CENTRALE SPOT & PUBBLICITÀ CON CADENZA IN SECONDI
// Foglio Google dedicato: 'Pubblicita_Schermo_Centrale'
// Colonna A: URL Media (foto/video/clip)
// Colonna B: Durata in secondi (cadenza per-riga)
// Colonna C: Titolo / Messaggio promozionale
// Colonna D: Tipo Media ('foto' o 'video')
// Colonna E: Attivo ('SI' / 'NO')
// Personal Branding: Immobiliare Giancani
// ═══════════════════════════════════════════════════════════════════════

/**
 * Restituisce l'elenco degli spot pubblicitari configurati per lo schermo centrale
 * con la rispettiva durata in secondi estratta rigorosamente dalla Colonna B
 */
function getSpotSchermoCentrale() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheetName = 'Pubblicita_Schermo_Centrale';
    var sheet = ss ? ss.getSheetByName(sheetName) : null;

    // Se il foglio non esiste, crealo automaticamente con intestazioni e righe campione
    if (ss && !sheet) {
      sheet = ss.insertSheet(sheetName);
      sheet.getRange(1, 1, 1, 5).setValues([
        ['URL_MEDIA', 'SECONDI_CADENZA', 'TITOLO_PUBBLICITA', 'TIPO_MEDIA', 'ATTIVO']
      ]);
      sheet.getRange(2, 1, 3, 5).setValues([
        [
          'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop',
          8,
          'Immobiliare Giancani — Immobili e Ville di Prestigio',
          'foto',
          'SI'
        ],
        [
          'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?q=80&w=1200&auto=format&fit=crop',
          10,
          'Valutazione Professionale Gratuita del Tuo Immobile',
          'foto',
          'SI'
        ],
        [
          'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?q=80&w=1200&auto=format&fit=crop',
          6,
          'Virtual Tour 360° e Dirette Streaming Show',
          'foto',
          'SI'
        ]
      ]);
      sheet.setFrozenRows(1);
    }

    if (!sheet || sheet.getLastRow() < 2) {
      return {
        success: true,
        spot: [
          {
            url: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop',
            durataSec: 8,
            titolo: 'Immobiliare Giancani — Immobili Esclusivi',
            tipo: 'foto'
          }
        ]
      };
    }

    var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 5).getValues();
    var listaSpot = [];

    for (var r = 0; r < data.length; r++) {
      var rawUrl = String(data[r][0] || '').trim();
      var rawSec = parseInt(data[r][1], 10);
      var durataSec = (!isNaN(rawSec) && rawSec >= 2) ? rawSec : 8; // Default 8s se non specificato
      var titolo = String(data[r][2] || 'Immobiliare Giancani').trim();
      var tipo = String(data[r][3] || 'foto').trim().toLowerCase();
      var attivo = String(data[r][4] || 'SI').trim().toUpperCase();

      if (attivo === 'SI' && rawUrl) {
        var mediaUrl = (typeof convertiUrlDriveDirect === 'function') ? convertiUrlDriveDirect(rawUrl) : rawUrl;
        listaSpot.push({
          url: mediaUrl,
          durataSec: durataSec,
          titolo: titolo,
          tipo: (tipo === 'video' || mediaUrl.indexOf('.mp4') !== -1) ? 'video' : 'foto',
          riga: r + 2
        });
      }
    }

    if (listaSpot.length === 0) {
      listaSpot.push({
        url: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop',
        durataSec: 8,
        titolo: 'Immobiliare Giancani',
        tipo: 'foto'
      });
    }

    return { success: true, spot: listaSpot };
  } catch(e) {
    console.error("Errore getSpotSchermoCentrale:", e);
    return { success: false, spot: [], error: e.toString() };
  }
}

/**
 * Salva la posizione del set degli avatar impostata da Generator (sinistra, centro, destra)
 */
function salvaPosizioneSetAvatar(pos) {
  try {
    var p = String(pos || 'destra').toLowerCase().trim();
    if (['sinistra', 'centro', 'destra'].indexOf(p) === -1) p = 'destra';
    PropertiesService.getScriptProperties().setProperty('POSIZIONE_SET_AVATAR', p);
    return { success: true, posizione: p };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function getPosizioneSetAvatar() {
  try {
    var p = PropertiesService.getScriptProperties().getProperty('POSIZIONE_SET_AVATAR') || 'destra';
    return { success: true, posizione: p };
  } catch(e) {
    return { success: false, posizione: 'destra' };
  }
}
