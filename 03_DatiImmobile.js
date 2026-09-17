// ═══════════════════════════════════════════════════════════════════════
// 📁 MODULO 03: ESTRAZIONE DATI IMMOBILE & ROTAZIONE STANZE
// Estrae rigorosamente i testi parlati dalla Colonna F e calcola la pertinenza stanze
// ═══════════════════════════════════════════════════════════════════════

/**
 * Recupera il foglio dell'immobile attivo o di default
 */
function getActiveImmobileSheet(ss, tabName) {
  try {
    if (!ss) ss = getSpreadsheetSicuro();
    if (!ss) return null;
    if (tabName) {
      var s = ss ? ss.getSheetByName(tabName) : null;
      if (s) return s;
    }
    var props = PropertiesService.getScriptProperties();
    var activeTab = props.getProperty('ACTIVE_IMMOBILE_TAB') || 'VILLA_FAVARA_RIFINITA';
    if (activeTab) {
      var sAct = ss ? ss.getSheetByName(activeTab) : null;
      if (sAct) return sAct;
    }
    var sVilla = ss ? ss.getSheetByName('VILLA_FAVARA_RIFINITA') : null;
    if (sVilla) return sVilla;
    var sFavara = ss ? ss.getSheetByName('Villa_Favara') : null;
    if (sFavara) return sFavara;
    var allSheets = ss.getSheets();
    return (allSheets && allSheets.length > 0) ? allSheets[0] : null;
  } catch(e) {
    inviaAllertaErroreTelegram("03_DatiImmobile.js", "getActiveImmobileSheet", e.toString());
    return null;
  }
}

/**
 * Imposta l'immobile attivo in diretta
 */
function setImmobileAttivoInDiretta(tabName) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName(tabName) : null;
    if (!sheet) return { success: false, error: "Scheda immobile '" + tabName + "' non trovata." };
    
    PropertiesService.getScriptProperties().setProperty('ACTIVE_IMMOBILE_TAB', tabName);
    inviaNotificaCambioImmobileTelegram(tabName);
    return { success: true, tabName: tabName };
  } catch(e) {
    inviaAllertaErroreTelegram("03_DatiImmobile.js", "setImmobileAttivoInDiretta", e.toString());
    return { success: false, error: e.toString() };
  }
}

/**
 * Restituisce l'elenco degli immobili (fogli) disponibili escludendo tutti i fogli di regia/sistema
 */
function getElencoImmobiliDisponibili() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheets = ss ? ss.getSheets() : null;
    var props = PropertiesService.getScriptProperties();
    var activeTab = props.getProperty('ACTIVE_IMMOBILE_TAB') || '';

    var ignorati = [
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
      'NOTIZIE_SPORT_ATTUALITA',
      'NOZIONI_IMMOBILIARI',
      'DIRETTA_O_DARIA_E_DARIO_INFLUENCER',
      'DIALOGHI_DUO',
      'STORYTELLER_CITTA',
      'BATTUTE_DARIO',
      'STORIE_FAVARA_AGRIGENTO',
      'STORIE_CITTA',
      'NOTIZIE_CITTA',
      'DIALOGHI_AVAT_TUTTI'
    ];

    var immobili = [];

    if (sheets) {
      for (var i = 0; i < sheets.length; i++) {
        var sName = sheets[i].getName();
        var sUpper = sName.toUpperCase().trim();
        if (sUpper.indexOf('DIALOGHI_') === 0 || sUpper.indexOf('POST_') === 0 || sUpper.indexOf('STATISTICHE_') === 0) {
          continue;
        }
        if (ignorati.indexOf(sUpper) === -1) {
          var cleanName = sName.replace(/_/g, ' ');
          var lastRow = sheets[i].getLastRow();
          var prezzo = '';
          var mq = '';
          var primaStanza = '';
          var fotoUrl = '';
          var testoF = '';
          var zona = '';
          var totFoto = Math.max(0, lastRow - 1);

          if (lastRow >= 2) {
            try {
              var r2 = sheets[i].getRange(2, 1, 1, 9).getValues()[0];
              // Colonna A (Indice 0): Media URL / Copertina
              if (r2[0]) fotoUrl = convertiUrlDriveDirect(String(r2[0]).trim());
              // Colonna B (Indice 1): Prezzo
              if (r2[1]) {
                var pStr = String(r2[1]).trim();
                if (pStr) {
                  if (pStr.toLowerCase().indexOf('trattativa') !== -1 || pStr.toLowerCase() === 'riservata') {
                    prezzo = 'Trattativa Riservata';
                  } else if (pStr.indexOf('€') === -1 && pStr.match(/\d/)) {
                    prezzo = '€ ' + pStr;
                  } else {
                    prezzo = pStr;
                  }
                }
              }
              // Colonna C (Indice 2): Metri Quadri
              if (r2[2]) {
                var mqStr = String(r2[2]).trim();
                if (mqStr) {
                  mq = mqStr.replace(/\s*m[q²]\b/gi, ' mq');
                  if (mq.toLowerCase().indexOf('mq') === -1 && mq.toLowerCase().indexOf('metri') === -1) {
                    mq += ' mq';
                  }
                }
              }
              // Colonna D (Indice 3): Prima Stanza / Titolo
              if (r2[3]) primaStanza = String(r2[3]).trim();
              // Colonna F (Indice 5): Rigorosamente Colonna F per il testo parlato!
              if (r2[5]) testoF = String(r2[5]).trim();
              // Colonna H (Indice 7): Ticker / Zona / Riferimento
              if (r2[7]) {
                var tStr = String(r2[7]).trim();
                if (tStr && tStr.length <= 40 && tStr.toLowerCase().indexOf('giancani') === -1) {
                  zona = tStr;
                }
              }
            } catch(eRow) {
              console.warn("Errore lettura riga 2 per " + sName + ":", eRow);
            }
          }

          // Integrazione dati da SCHEDA_IMMOBILE se salvati in precedenza
          try {
            var rawProp = props.getProperty("SCHEDA_IMMOBILE_" + sName);
            if (rawProp) {
              var objProp = JSON.parse(rawProp);
              if (!prezzo && objProp.prezzo) prezzo = objProp.prezzo;
              if (!mq && objProp.metriQuadri) mq = objProp.metriQuadri;
              if (!zona && objProp.zona) zona = objProp.zona;
            }
          } catch(eProp) {}

          // Normalizzazione testo Colonna F con chiusura obbligatoria Immobiliare Giancani
          if (testoF) {
            testoF = pulisciTestoPerTTSBackend(testoF);
          } else {
            testoF = "Splendida opportunità immobiliare curata nei minimi dettagli. — Immobiliare Giancani";
          }

          // Costruzione etichetta descrittiva e inconfondibile per le tendine
          var labelDettagli = [];
          if (prezzo) labelDettagli.push(prezzo);
          if (mq) labelDettagli.push(mq);
          if (zona) labelDettagli.push('[' + zona + ']');
          if (totFoto > 0) labelDettagli.push('(' + totFoto + ' foto)');

          var labelCompleta = cleanName;
          if (labelDettagli.length > 0) {
            labelCompleta += ' — ' + labelDettagli.join(' | ');
          }

          immobili.push({
            name: sName,
            tabName: sName,
            nome: cleanName,
            label: labelCompleta,
            prezzo: prezzo || 'Trattativa Riservata',
            mq: mq || '120 mq',
            zona: zona || '',
            primaStanza: primaStanza || 'Panoramica Immobile',
            fotoUrl: fotoUrl || 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=600&auto=format&fit=crop',
            totFoto: totFoto,
            testoColonnaF: testoF,
            isCurrent: false,
            isAttivo: false
          });
        }
      }
    }

    // Se non ci sono immobili o se activeTab è invalido/nullo, seleziona il primo immobile reale
    var hasActiveMatch = false;
    if (activeTab && ignorati.indexOf(activeTab.toUpperCase()) === -1) {
      for (var j = 0; j < immobili.length; j++) {
        if (immobili[j].name === activeTab) {
          immobili[j].isCurrent = true;
          immobili[j].isAttivo = true;
          hasActiveMatch = true;
          break;
        }
      }
    }

    if (!hasActiveMatch && immobili.length > 0) {
      immobili[0].isCurrent = true;
      immobili[0].isAttivo = true;
      activeTab = immobili[0].name;
      props.setProperty('ACTIVE_IMMOBILE_TAB', activeTab);
    }

    immobili.success = true;
    immobili.immobili = immobili;
    immobili.attivo = activeTab;

    return immobili;
  } catch(e) {
    inviaAllertaErroreTelegram("03_DatiImmobile.js", "getElencoImmobiliDisponibili", e.toString());
    var fallback = [];
    fallback.success = false;
    fallback.immobili = [];
    fallback.error = e.toString();
    return fallback;
  }
}

/**
 * Converte ID o URL di Google Drive in CDN diretta
 */
function convertiUrlDriveDirect(url) {
  if (!url) return '';
  var str = url.toString().trim();
  if (str.startsWith('http://') || str.startsWith('https://')) {
    var idMatch = str.match(/[-\w]{25,}/);
    if (idMatch && (str.indexOf('drive.google.com') !== -1 || str.indexOf('docs.google.com') !== -1)) {
      return 'https://lh3.googleusercontent.com/d/' + idMatch[0];
    }
    return str;
  }
  if (str.match(/^[-\w]{25,}$/)) {
    return 'https://lh3.googleusercontent.com/d/' + str;
  }
  return str;
}

/**
 * 🎬 CAROSELLO INTELLIGENTE VIDEO POST_YOUTUBE (> 1 MINUTO)
 * Preleva rigorosamente i testi da Colonna F, imposta la rotazione video a 75 secondi,
 * genera l'intro vocale breve per DarIA e DarIO con invito alla chat,
 * e memorizza il link video corrente per le risposte automatiche.
 */
function getCaroselloPostYouTube(direction) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Post_YouTube') : null;
    var props = PropertiesService.getScriptProperties();

    if (!sheet || sheet.getLastRow() < 2) {
      return {
        success: false,
        isYouTubeCarousel: true,
        stanza: "Canale YouTube Immobiliare Giancani",
        tipoMedia: "video",
        durataSec: 75,
        mediaUrl: "https://www.youtube.com/embed/zekP_9iFLK0?autoplay=1&controls=0&rel=0&enablejsapi=1",
        watchUrl: "https://www.youtube.com/watch?v=zekP_9iFLK0",
        videoId: "zekP_9iFLK0",
        testoDaLeggere: "Scoprite tutti i nostri video e le nostre proposte immobiliari esclusive sul canale YouTube ufficiale. Scrivete LINK nei commenti per ricevere il link del video in chat! — Immobiliare Giancani",
        testo: "Scoprite tutti i nostri video e le nostre proposte immobiliari esclusive sul canale YouTube ufficiale. Scrivete LINK nei commenti per ricevere il link del video in chat! — Immobiliare Giancani",
        titolo: "Canale Ufficiale Immobiliare Giancani",
        prezzo: "Trattativa Riservata",
        mq: "metri quadri",
        citta: "Favara ed Agrigento"
      };
    }

    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(2, 1, lastRow - 1, 10).getValues(); // Legge fino a Col J (durata per-video)
    var videoList = [];

    for (var r = 0; r < data.length; r++) {
      var rawUrl = String(data[r][0] || '').trim(); // Col A: URL_MEDIA (embed)
      var prezzo = String(data[r][1] || 'Trattativa Riservata').trim(); // Col B
      var rawMq  = String(data[r][2] || 'YouTube').trim(); // Col C
      var titolo = String(data[r][3] || 'Immobile Esclusivo').trim(); // Col D
      var tipoM  = String(data[r][4] || 'video').trim().toLowerCase(); // Col E
      var descrF = String(data[r][5] || '').trim(); // Col F: Testo parlato DarIA (RIGOROSO)
      var thumb  = String(data[r][6] || '').trim(); // Col G: Anteprima
      var ticker = String(data[r][7] || '').trim(); // Col H: Ticker
      var linkDiretto = String(data[r][8] || '').trim(); // Col I: Link YouTube diretto
      var durataSec   = parseInt(data[r][9], 10);  // Col J: Durata per-video (secondi)
      if (isNaN(durataSec) || durataSec < 10) durataSec = 75; // Fallback default 75s

      if (!rawUrl && !titolo) continue;

      // Estrazione accurata Video ID (supporta embed, watch, youtu.be, shorts)
      var vId = '';
      var m = rawUrl.match(/(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|shorts\/|.*[?&]v=)|(?:\/|^))([a-zA-Z0-9_-]{11})/i);
      if (m && m[1]) {
        vId = m[1];
      } else if (thumb) {
        var mThumb = thumb.match(/\/vi\/([a-zA-Z0-9_-]{11})\//);
        if (mThumb && mThumb[1]) vId = mThumb[1];
      }

      if (!vId && rawUrl.length === 11) vId = rawUrl;
      if (!vId) continue; // Salta rigorosamente righe senza un video YouTube valido

      var embedUrl = vId
        ? ('https://www.youtube.com/embed/' + vId + '?autoplay=1&controls=0&rel=0&enablejsapi=1')
        : rawUrl;
      // Usa linkDiretto (Col I) se disponibile, altrimenti costruisci da videoId
      var watchUrl = linkDiretto && linkDiretto.startsWith('http') ? linkDiretto
        : (vId ? ('https://www.youtube.com/watch?v=' + vId)
               : (rawUrl.startsWith('http') ? rawUrl : 'https://www.youtube.com/@immobiliaregiancani761'));

      // Formattazione rigorosa MQ -> metri quadri
      var mqPulito = rawMq.replace(/(\d+)\s*(?:mq|m²|m2)\b/gi, "$1 metri quadri")
                          .replace(/\b(?:mq|m²|m2)\b/gi, "metri quadri")
                          .replace(/\bMQ\b/g, "metri quadri");
      if (mqPulito === 'YouTube' || mqPulito === 'Shorts' || !mqPulito) {
        mqPulito = "metri quadri";
      }

      // Estrazione rigorosa Colonna F per personal branding
      var testoF = descrF;
      if (!testoF || testoF.length < 5) {
        testoF = "Vi presentiamo questa speciale proposta immobiliare in vendita: " + titolo + ". Un'opportunità prestigiosa curata da Immobiliare Giancani.";
      }
      testoF = pulisciTestoPerTTSBackend(testoF);

      videoList.push({
        riga: r + 2,
        urlEmbed: embedUrl,
        watchUrl: watchUrl,
        videoId: vId,
        prezzo: prezzo,
        mq: mqPulito,
        titolo: titolo,
        tipoMedia: 'video',
        testoColonnaF: testoF,
        thumbnail: thumb,
        durataSec: durataSec, // Colonna J: durata per-video (default 75s)
        ticker: ticker || ('🎬 ' + titolo.substring(0, 70) + ' — Immobiliare Giancani')
      });
    }

    if (videoList.length === 0) {
      return {
        success: false,
        isYouTubeCarousel: true,
        stanza: "Video Canale YouTube",
        tipoMedia: "video",
        durataSec: 75,
        mediaUrl: "https://www.youtube.com/embed/zekP_9iFLK0?autoplay=1&controls=0&rel=0",
        watchUrl: "https://www.youtube.com/watch?v=zekP_9iFLK0",
        videoId: "zekP_9iFLK0",
        testoDaLeggere: "Tutte le migliori proposte in video con Immobiliare Giancani.",
        testo: "Tutte le migliori proposte in video con Immobiliare Giancani."
      };
    }

    // Gestione Indice Rotazione Carosello
    var idxKey = 'YOUTUBE_CAROUSEL_INDEX';
    var currentIndex = parseInt(props.getProperty(idxKey) || '0', 10);
    if (isNaN(currentIndex) || currentIndex < 0 || currentIndex >= videoList.length) currentIndex = 0;

    direction = (direction || 'next').toString().toLowerCase().trim();
    if (direction === 'next') {
      currentIndex = (currentIndex + 1) % videoList.length;
    } else if (direction === 'prev') {
      currentIndex = (currentIndex - 1 + videoList.length) % videoList.length;
    } else if (direction === 'first') {
      currentIndex = 0;
    }

    props.setProperty(idxKey, currentIndex.toString());
    var currentVideo = videoList[currentIndex];

    // Memorizza in tempo reale il video corrente per la risposta automatica in chat/commenti
    props.setProperty('CURRENT_CAROUSEL_VIDEO_URL', currentVideo.watchUrl);
    props.setProperty('CURRENT_CAROUSEL_VIDEO_TITLE', currentVideo.titolo);
    props.setProperty('CURRENT_CAROUSEL_VIDEO_ID', currentVideo.videoId || '');

    // 🎙️ INTRO VOCALE BREVE (15-20s): DarIA descrive ed invita alla chat, DarIO rinforza
    var testoPuro = currentVideo.testoColonnaF.replace(/—\s*Immobiliare\s*Giancani/gi, '').trim();
    var frasi = testoPuro.split(/[.!?]+/).map(function(s){ return s.trim(); }).filter(function(s){ return s.length > 10; });
    var primaFraseF = frasi.length > 0 ? frasi[0] : ("Ecco a voi " + currentVideo.titolo);
    if (primaFraseF.length > 130) primaFraseF = primaFraseF.substring(0, 125) + '...';

    // Invito esplicito a chiedere il link nei commenti
    var dariaIntro = primaFraseF + ". Scrivete subito LINK nei commenti per ricevere il link diretto del video e tutte le informazioni complete in chat! — Immobiliare Giancani";
    var darioIntro = "Esatto DarIA! Chiedete il link nei commenti e ve lo invieremo all'istante in chat, oppure chiamateci al 3201667156 per prenotare la vostra visita esclusiva con Immobiliare Giancani!";

    if (typeof pulisciFrasePerDirettaLive === 'function') {
      dariaIntro = pulisciFrasePerDirettaLive(dariaIntro);
      darioIntro = pulisciFrasePerDirettaLive(darioIntro);
    }

    // Modalità Carosello è rigorosamente SENZA AVATAR (video a schermo pieno con audio originale)
    var modalitaAv = props.getProperty('MODALITA_AVATAR') || 'VUOTO';
    var testoIntroLetto = (modalitaAv === 'CON_AVATAR') ? dariaIntro : '';

    return {
      success: true,
      isYouTubeCarousel: true,
      stanza: currentVideo.titolo,
      tipoMedia: "video",
      is360: false,
      mediaUrl: currentVideo.urlEmbed,
      videoUrl: currentVideo.urlEmbed,
      watchUrl: currentVideo.watchUrl,
      fotoUrl: currentVideo.thumbnail || "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop",
      videoId: currentVideo.videoId,
      durataSec: currentVideo.durataSec || 75, // Durata da Col J, fallback 75s
      testoDaLeggere: testoIntroLetto,
      testo: testoIntroLetto,
      dariaIntro: dariaIntro,
      darioIntro: darioIntro,
      testoColonnaF: currentVideo.testoColonnaF,
      indiceCorrente: currentIndex,
      totaleMedia: videoList.length,
      modalitaAvatar: modalitaAv,
      titolo: currentVideo.titolo,
      prezzo: currentVideo.prezzo,
      mq: currentVideo.mq,
      citta: "Favara ed Agrigento",
      lingua: props.getProperty('LINGUA_DARIA') || "it-IT",
      linkAnnuncio: currentVideo.watchUrl,
      ticker: currentVideo.ticker,
      stileGrafica: (typeof getStileGraficaDiretta === 'function') ? getStileGraficaDiretta() : 'modern_broadcast',
      scalaLogoAgenzia: (typeof getScalaLogoAgenzia === 'function') ? getScalaLogoAgenzia() : 1.0,
      configVoci: getConfigurazioneVoci(),
      coppiaAvatar: getCoppiaAvatarAttiva(),
      musicaPlaylist: (typeof getMusicaSottofondo === 'function') ? getMusicaSottofondo().playlist : []
    };
  } catch(e) {
    inviaAllertaErroreTelegram("03_DatiImmobile.js", "getCaroselloPostYouTube", e.toString());
    return {
      success: false,
      isYouTubeCarousel: true,
      stanza: "Video Canale YouTube",
      tipoMedia: "video",
      durataSec: 75,
      mediaUrl: "https://www.youtube.com/embed/zekP_9iFLK0?autoplay=1&controls=0&rel=0",
      watchUrl: "https://www.youtube.com/watch?v=zekP_9iFLK0",
      videoId: "zekP_9iFLK0",
      testoDaLeggere: "I migliori video immobiliari curati da Immobiliare Giancani.",
      testo: "I migliori video immobiliari curati da Immobiliare Giancani."
    };
  }
}

/**
 * 🔗 Restituisce il link, titolo e ID del video attualmente trasmesso nel carosello
 */
function getLinkVideoCorrente() {
  try {
    var props = PropertiesService.getScriptProperties();
    var url = props.getProperty('CURRENT_CAROUSEL_VIDEO_URL');
    var titolo = props.getProperty('CURRENT_CAROUSEL_VIDEO_TITLE');
    var vidId = props.getProperty('CURRENT_CAROUSEL_VIDEO_ID');

    if (url && titolo) {
      return { url: url, titolo: titolo, videoId: vidId || '' };
    }

    // Se non è ancora memorizzato, preleva il primo video dal foglio Post_YouTube
    var carosello = getCaroselloPostYouTube('current');
    if (carosello && carosello.watchUrl) {
      return {
        url: carosello.watchUrl,
        titolo: carosello.titolo || 'Immobile Esclusivo',
        videoId: carosello.videoId || ''
      };
    }

    return {
      url: 'https://www.youtube.com/@immobiliaregiancani761',
      titolo: 'Canale Ufficiale Immobiliare Giancani',
      videoId: ''
    };
  } catch(e) {
    return {
      url: 'https://www.youtube.com/@immobiliaregiancani761',
      titolo: 'Canale Ufficiale Immobiliare Giancani',
      videoId: ''
    };
  }
}

/**
 * 🏠 ESTRAZIONE DATI IMMOBILE & RICERCA STANZE (Colonna F)
 */
function getImmobileData(direction) {
  try {
    var ss = getSpreadsheetSicuro();
    var props = PropertiesService.getScriptProperties();
    var activeTab = props.getProperty('ACTIVE_IMMOBILE_TAB') || 'VILLA_FAVARA_RIFINITA';

    // 🌙 VERIFICA PROGRAMMA SERALE AUTOMATICO (19:00 - 01:00)
    // Se siamo nella fascia 19:00 - 01:00 e il programma serale è attivo,
    // trasmetti rigorosamente l'immobile del palinsesto serale con equa rotazione!
    try {
      var nowRome = new Date(new Date().toLocaleString("en-US", { timeZone: "Europe/Rome" }));
      var hRome = nowRome.getHours();
      var isSerale = (hRome >= 19 || hRome < 1);
      var progSeraleAttivo = props.getProperty('PROGRAMMA_SERALE_ATTIVO') !== 'false';
      
      if (isSerale && progSeraleAttivo && typeof getImmobileSeraleDelGiorno === 'function') {
        var immSerale = getImmobileSeraleDelGiorno();
        if (immSerale && immSerale.tabName) {
          activeTab = immSerale.tabName;
        }
      }
    } catch(eSerale) {}

    // Se la scheda attiva è Post_YouTube, attiva il Carosello Video Intelligente (> 1 minuto)
    if (activeTab && activeTab.toUpperCase() === 'POST_YOUTUBE') {
      return getCaroselloPostYouTube(direction);
    }

    var sheet = getActiveImmobileSheet(ss, activeTab);
    
    if (!sheet || sheet.getLastRow() < 2) {
      return {
        stanza: "Panoramica Immobile",
        tipoMedia: "foto",
        mediaUrl: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop",
        testoDaLeggere: "Benvenuti in questa splendida proprietà esclusiva in Sicilia. — Immobiliare Giancani",
        testo: "Benvenuti in questa splendida proprietà esclusiva in Sicilia. — Immobiliare Giancani",
        prezzo: "Trattativa Riservata",
        citta: "Favara ed Agrigento",
        lingua: "it-IT"
      };
    }

    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(2, 1, lastRow - 1, 10).getValues();
    
    var mediaRows = [];
    var esclusioni = getEsclusioniMediaLive();
    
    for (var r = 0; r < data.length; r++) {
      var rowIdx = r + 2;
      if (esclusioni[rowIdx]) continue; // Salta media esclusi
      
      var urlM = convertiUrlDriveDirect(String(data[r][0] || '').trim());
      if (!urlM || (!urlM.startsWith('http') && !urlM.startsWith('https'))) continue;
      
      var stName = String(data[r][3] || '').trim() || ('Ambiente ' + (r + 1));
      var tMedia = String(data[r][4] || 'foto').toLowerCase().trim();
      if (tMedia !== '360' && tMedia !== 'video') tMedia = 'foto';
      
      // ESTRAZIONE RIGOROSA COLONNA F (Indice 5)
      var testoF = String(data[r][5] || '').trim();
      if (stName.match(/bagno|toilette|wc|servizio|servizi/i) && (!testoF || testoF.length < 5 || testoF.indexOf('spazio rifinito') !== -1)) {
        testoF = "Ci troviamo adesso nel bagno di questo appartamento, uno spazio intimo dedicato al relax. Ma trovarci qui apre una riflessione astratta affascinante su quelle parti e pertinenze che spesso desideriamo in una casa ma che in questo appartamento non sono presenti: come una zona spa privata con sauna finlandese, o un secondo bagno en-suite! La forza di Immobiliare Giancani è proprio questa: saper immaginare e realizzare ogni potenziale nascosto. — Immobiliare Giancani";
      } else if (!testoF || testoF.length < 5) {
        testoF = "Ammirate " + stName + ": uno spazio rifinito, arioso e luminoso pronto ad accogliervi. — Immobiliare Giancani";
      }
      testoF = pulisciTestoPerTTSBackend(testoF);

      mediaRows.push({
        idx: r,
        rowIndex: rowIdx,
        url: urlM,
        stanza: stName,
        tipo: tMedia,
        testo: testoF
      });
    }

    if (mediaRows.length === 0) {
      return {
        stanza: "Panoramica Immobile",
        tipoMedia: "foto",
        mediaUrl: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop",
        testoDaLeggere: "Benvenuti in questa proprietà esclusiva curata da Immobiliare Giancani.",
        testo: "Benvenuti in questa proprietà esclusiva curata da Immobiliare Giancani."
      };
    }

    var indexKey = 'MEDIA_IDX_' + sheet.getName();
    var currentIndex = parseInt(props.getProperty(indexKey) || '0', 10);
    if (isNaN(currentIndex) || currentIndex < 0 || currentIndex >= mediaRows.length) currentIndex = 0;

    direction = (direction || 'next').toString().toLowerCase().trim();
    var chatRequester = null;
    var commentoLiveInOnda = null;

    if (direction === 'current') {
      // 1. Controlla prima se c'è un commento da social o chat in attesa di andare in onda
      if (typeof prelevaProssimoCommentoLive === 'function') {
        var cLive = prelevaProssimoCommentoLive();
        if (cLive) {
          commentoLiveInOnda = cLive;
          if (cLive.stanza) {
            direction = cLive.stanza;
          }
          chatRequester = (cLive.piattaforma ? ('[' + cLive.piattaforma + '] ') : '') + (cLive.autore || 'Spettatore');
        }
      }

      // 2. Fallback alla richiesta stanza chat semplice se non c'era commento live
      if (!commentoLiveInOnda && typeof getRichiestaStanzaChatPendente === 'function') {
        var pReq = getRichiestaStanzaChatPendente();
        if (pReq && pReq.hasRequest && pReq.stanza) {
          direction = pReq.stanza;
          chatRequester = pReq.autore || 'un nostro spettatore';
        }
      }
    }

    if (direction === 'next') {
      currentIndex = (currentIndex + 1) % mediaRows.length;
    } else if (direction === 'prev') {
      currentIndex = (currentIndex - 1 + mediaRows.length) % mediaRows.length;
    } else if (direction !== 'current') {
      // 🔍 RICERCA STANZA CHAT INTELLIGENTE AD ALTA PRECISIONE
      var queryRaw = direction;
      var stopWords = ['vorrei', 'vedere', 'fai', 'puoi', 'mostra', 'mostrami', 'voglio', 'cerco', 'trova', 'il', 'la', 'lo', 'i', 'gli', 'le', 'un', 'una', 'uno', 'di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra', 'mi', 'ti', 'ci', 'vi', 'che', 'si', 'ho', 'ha', 'daria', 'dario', 'fammi', 'perfavore', 'grazie', 'metti', 'mettimi', 'passa', 'vai', 'apri', 'carica', 'cambia', 'porta', 'visualizza', 'per favore', 'favore', 'gentilmente', 'adesso', 'ora', 'subito', 'piacere', 'stanze', 'stanza', 'foto', 'ambiente'];
      
      var cleanQuery = queryRaw;
      stopWords.forEach(function(sw) {
        cleanQuery = cleanQuery.replace(new RegExp('\\b' + sw + '\\b', 'gi'), ' ');
      });
      var tokens = cleanQuery.split(/\s+/).filter(function(w) { return w.length >= 2; });
      if (tokens.length === 0) tokens = [queryRaw];

      var sinonimiStanze = {
        'cucina': ['cucina', 'cucinino', 'cottura', 'angolo cottura', 'veranda coperta', 'pranzo', 'tavolo'],
        'salotto': ['salotto', 'soggiorno', 'sala', 'salone', 'living', 'zona giorno', 'divano', 'tv'],
        'soggiorno': ['soggiorno', 'salotto', 'sala', 'salone', 'living', 'zona giorno', 'divano', 'tv'],
        'bagno': ['bagno', 'servizio', 'wc', 'doccia', 'toilette', 'lavanderia', 'vasca', 'sanitari', 'bagnetto'],
        'camera': ['camera', 'letto', 'matrimoniale', 'cameretta', 'notte', 'singola', 'doppia', 'stanza da letto', 'zona notte', 'armadio'],
        'cameretta': ['cameretta', 'camera', 'letto', 'singola', 'doppia', 'ragazzi', 'bambini'],
        'balcone': ['balcone', 'veranda', 'terrazzo', 'terrazza', 'vista esterna', 'affaccio'],
        'terrazzo': ['terrazzo', 'terrazza', 'balcone', 'veranda', 'solarium', 'panoramica'],
        'cancello': ['cancello', 'entrata', 'passo carraio', 'ingresso', 'portone', 'porta'],
        'ingresso': ['ingresso', 'entrata', 'disimpegno', 'corridoio', 'cancello', 'atrio'],
        'magazzino': ['magazzino', 'garage', 'box', 'deposito', 'cantina', 'posto auto'],
        'garage': ['garage', 'box', 'posto auto', 'magazzino', 'rimessa'],
        'esterno': ['esterno', 'campagna', 'giardino', 'vista esterno', 'prospetto', 'facciata', 'cortile', 'piazzale']
      };

      var numeriMappa = { 'prima': 0, 'primo': 0, '1': 0, 'uno': 0, 'seconda': 1, 'secondo': 1, '2': 1, 'due': 1, 'terza': 2, 'terzo': 2, '3': 2, 'tre': 2, 'quarta': 3, 'quarto': 3, '4': 3, 'quattro': 3, 'quinta': 4, 'quinto': 4, '5': 4, 'cinque': 4 };

      var bestMatch = null;
      var maxScore = 0;

      for (var mIdx = 0; mIdx < mediaRows.length; mIdx++) {
        var rItem = mediaRows[mIdx];
        var st = (rItem.stanza || '').toLowerCase();
        var tf = (rItem.testo || '').toLowerCase();
        var score = 0;

        tokens.forEach(function(tok) {
          if (numeriMappa[tok] !== undefined && numeriMappa[tok] === mIdx) score += 150;
        });

        if (st === queryRaw || st === cleanQuery.trim()) {
          score += 200;
        } else if (queryRaw.indexOf(st) !== -1 || (st.length > 3 && cleanQuery.indexOf(st) !== -1)) {
          score += 120;
        }

        tokens.forEach(function(tok) {
          if (tok.length >= 3 && st.indexOf(tok) !== -1) score += 80;
        });

        for (var rKey in sinonimiStanze) {
          var synList = sinonimiStanze[rKey];
          var queryHasSyn = synList.some(function(s) { return queryRaw.indexOf(s) !== -1; });
          if (queryHasSyn) {
            var stanzaHasSyn = synList.some(function(s) { return st.indexOf(s) !== -1; });
            if (stanzaHasSyn) {
              score += 100;
              synList.forEach(function(s) {
                if (queryRaw.indexOf(s) !== -1 && st.indexOf(s) !== -1) score += 40;
              });
            }
          }
        }

        tokens.forEach(function(tok) {
          if (tok.length >= 4 && tf.indexOf(tok) !== -1) score += 25;
        });

        if (score > maxScore) {
          maxScore = score;
          bestMatch = { item: rItem, mIdx: mIdx };
        }
      }

      if (bestMatch && maxScore > 0) {
        currentIndex = bestMatch.mIdx;
      }
    }

    props.setProperty(indexKey, currentIndex.toString());
    var selected = mediaRows[currentIndex] || mediaRows[0];
    var modalitaAv = props.getProperty('MODALITA_AVATAR') || 'CON_AVATAR';
    var cleanTitle = (activeTab || 'Dimora Esclusiva').replace(/_/g, ' ');
    var rawPrezzo = (data[selected.idx] && data[selected.idx][1]) ? String(data[selected.idx][1]).trim() : '';
    var prezzoFinale = rawPrezzo;
    if (prezzoFinale) {
      var soloNum = prezzoFinale.replace(/[^\d]/g, '');
      if (soloNum) {
        prezzoFinale = parseInt(soloNum, 10).toLocaleString('it-IT') + ' €';
      }
    } else {
      prezzoFinale = "Trattativa Riservata";
    }

    var rawZona = (cleanTitle.indexOf('Favara') !== -1) ? "Favara (AG)" :
                  (cleanTitle.indexOf('Aragona') !== -1) ? "Aragona (AG)" :
                  (cleanTitle.indexOf('Agrigento') !== -1 || cleanTitle.indexOf('Mosè') !== -1) ? "Agrigento" : "Favara ed Agrigento";

    var stanzeUniche = [];
    mediaRows.forEach(function(mr) {
      if (mr.stanza && stanzeUniche.indexOf(mr.stanza) === -1) {
        stanzeUniche.push(mr.stanza);
      }
    });

    return {
      success: true,
      stanza: selected.stanza,
      tipoMedia: selected.tipo,
      is360: (selected.tipo === '360'),
      mediaUrl: selected.url,
      fotoUrl: selected.url,
      testoDaLeggere: selected.testo,
      testo: selected.testo,
      indiceCorrente: currentIndex,
      totaleMedia: mediaRows.length,
      modalitaAvatar: modalitaAv,
      richiestaDaChat: chatRequester,
      commentoLiveInOnda: commentoLiveInOnda,
      titolo: cleanTitle,
      prezzo: prezzoFinale,
      zona: rawZona,
      elencoStanze: stanzeUniche,
      scalaLogoAgenzia: (typeof getScalaLogoAgenzia === 'function') ? getScalaLogoAgenzia() : 1.0,
      stileGrafica: (typeof getStileGraficaDiretta === 'function') ? getStileGraficaDiretta() : 'modern_broadcast',
      mq: String(data[selected.idx] && data[selected.idx][2] ? data[selected.idx][2] : "120 metri quadri").replace(/(\d+)\s*(?:mq|m²|m2)\b/gi, "$1 metri quadri").replace(/\b(?:mq|m²)\b/gi, "metri quadri").replace(/\bMQ\b/g, "metri quadri"),
      citta: rawZona,
      lingua: props.getProperty('LINGUA_DARIA') || "it-IT",
      linkAnnuncio: "https://www.immobiliaregiancani.it",
      battutaDario: getBattutaDarioCasuale(),
      storiaCitta: getStoriaCittaCasuale(),
      notiziaSport: getNotiziaSportCasuale(),
      nozioneImmobiliare: getNozioneImmobiliareCasuale(),
      dialogoDuo: getDialogoDuoCasuale(),
      interventoDario: getInterventoDarioMultischeda(currentIndex, selected.stanza),
      streamZoom: getZoomDiretta(),
      configVoci: getConfigurazioneVoci(),
      coppiaAvatar: getCoppiaAvatarAttiva(),
      dialoghiAvatTutti: getDialoghiAvatTuttiList(),
      posizioneSetAvatar: (typeof getPosizioneSetAvatar === 'function') ? getPosizioneSetAvatar().posizione : (props.getProperty('POSIZIONE_SET_AVATAR') || 'destra'),
      spotSchermoCentrale: (typeof getSpotSchermoCentrale === 'function') ? getSpotSchermoCentrale().spot : [],
      musicaPlaylist: (typeof getMusicaSottofondo === 'function') ? getMusicaSottofondo().playlist : []
    };

  } catch(e) {
    inviaAllertaErroreTelegram("03_DatiImmobile.js", "getImmobileData", e.toString());
    return {
      stanza: "Ambiente Immobile",
      tipoMedia: "foto",
      mediaUrl: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop",
      testoDaLeggere: "Benvenuti in questa splendida proprietà — Immobiliare Giancani",
      testo: "Benvenuti in questa splendida proprietà — Immobiliare Giancani",
      prezzo: "Trattativa Riservata",
      mq: "120 metri quadri",
      battutaDario: getBattutaDarioCasuale(),
      storiaCitta: getStoriaCittaCasuale(),
      notiziaSport: getNotiziaSportCasuale(),
      nozioneImmobiliare: getNozioneImmobiliareCasuale(),
      dialogoDuo: getDialogoDuoCasuale(),
      interventoDario: getInterventoDarioMultischeda(0),
      streamZoom: getZoomDiretta(),
      configVoci: getConfigurazioneVoci(),
      coppiaAvatar: getCoppiaAvatarAttiva(),
      posizioneSetAvatar: 'destra',
      dialoghiAvatTutti: getDialoghiAvatTuttiFallback(),
      commentoLiveInOnda: null
    };
  }
}

/**
 * Gestione Filtri & Esclusioni Media
 */
function getEsclusioniMediaLive() {
  try {
    var raw = PropertiesService.getScriptProperties().getProperty('ESCLUSIONI_MEDIA_LIVE') || '{}';
    return JSON.parse(raw);
  } catch(e) {
    return {};
  }
}

function toggleEsclusioneMediaLive(rowIndex) {
  try {
    var esclusioni = getEsclusioniMediaLive();
    esclusioni[rowIndex] = !esclusioni[rowIndex];
    PropertiesService.getScriptProperties().setProperty('ESCLUSIONI_MEDIA_LIVE', JSON.stringify(esclusioni));
    return { success: true, escluso: esclusioni[rowIndex] };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function salvaFiltroMediaLive(filtro) {
  try {
    PropertiesService.getScriptProperties().setProperty('FILTRO_MEDIA_LIVE', filtro || 'TUTTI');
    return { success: true };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function getFiltroMediaLive() {
  try {
    return PropertiesService.getScriptProperties().getProperty('FILTRO_MEDIA_LIVE') || 'TUTTI';
  } catch(e) {
    return 'TUTTI';
  }
}

/**
 * 👥 GESTIONE CONDUTTORI AVATAR IN ONDA (DARIA & DARIO)
 * Permette di selezionare 1 donna e 1 uomo alla volta (coppia in conduzione).
 * Supporta cambio istantaneo in tempo reale durante la diretta streaming.
 */
function getCoppiaAvatarAttiva() {
  try {
    var props = PropertiesService.getScriptProperties();
    var donna = props.getProperty('AVATAR_DONNA_ATTIVO') || 'daria_bionda';
    var uomo = props.getProperty('AVATAR_UOMO_ATTIVO') || 'dario_biondo';
    return {
      donna: donna,
      uomo: uomo
    };
  } catch(e) {
    return { donna: 'daria_bionda', uomo: 'dario_biondo' };
  }
}

function impostaAvatarInOnda(donnaId, uomoId) {
  try {
    var props = PropertiesService.getScriptProperties();
    var cur = getCoppiaAvatarAttiva();

    var donneValide = ['daria_bionda', 'daria_rossa', 'daria_bronde', 'daria_classica'];
    var uominiValidi = ['dario_biondo', 'dario_rosso', 'dario_bronde', 'dario_classico'];

    var nuovaDonna = donnaId && donneValide.indexOf(donnaId) !== -1 ? donnaId : cur.donna;
    var nuovoUomo = uomoId && uominiValidi.indexOf(uomoId) !== -1 ? uomoId : cur.uomo;

    props.setProperty('AVATAR_DONNA_ATTIVO', nuovaDonna);
    props.setProperty('AVATAR_UOMO_ATTIVO', nuovoUomo);

    return {
      success: true,
      coppia: {
        donna: nuovaDonna,
        uomo: nuovoUomo
      },
      message: 'Coppia conduttori aggiornata in diretta!'
    };
  } catch(e) {
    inviaAllertaErroreTelegram("03_DatiImmobile.js", "impostaAvatarInOnda", e.toString());
    return { success: false, error: e.toString() };
  }
}

function impostaLinguaDariaImmediata(lang, testo) {
  try {
    PropertiesService.getScriptProperties().setProperty('LINGUA_DARIA', lang || 'it-IT');
    return { success: true, lingua: lang };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function getMusicaSottofondo() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', playlist: [] };

    // 1. Controlla prima il foglio dedicato "Musica_Sottofondo"
    var mSheet = ss.getSheetByName('Musica_Sottofondo');
    var playlist = [];
    if (mSheet && mSheet.getLastRow() >= 2) {
      var lastRow = mSheet.getLastRow();
      var rows = mSheet.getRange(2, 1, lastRow - 1, 4).getValues();
      for (var i = 0; i < rows.length; i++) {
        var titolo = String(rows[i][0] || '').trim(); // Colonna A = Titolo
        var urlMp3 = String(rows[i][1] || '').trim(); // Colonna B = URL MP3 / Google Drive
        var stile  = String(rows[i][2] || 'Lounge').trim(); // Colonna C = Stile
        var attiva = String(rows[i][3] || 'SI').toUpperCase().trim(); // Colonna D = Attiva

        if (urlMp3 && (attiva === 'SI' || attiva === 'SÌ' || attiva === 'YES' || attiva === '1' || attiva === '')) {
          playlist.push({
            titolo: titolo || ('Brano ' + (i + 1)),
            url: convertiUrlDriveDirect(urlMp3),
            stile: stile
          });
        }
      }
    }

    if (playlist.length > 0) {
      return { success: true, url: playlist[0].url, playlist: playlist };
    }

    // 2. Fallback: cerca riga 'musica' o 'bg_music' in Impostazioni_Social
    var sSheet = ss.getSheetByName('Impostazioni_Social');
    var musicaUrl = '';
    if (sSheet) {
      var data = sSheet.getDataRange().getValues();
      for (var r = 0; r < data.length; r++) {
        var p = String(data[r][0] || '').trim().toLowerCase();
        if (p.indexOf('musica') !== -1 || p.indexOf('bg_music') !== -1) {
          musicaUrl = String(data[r][1] || data[r][5] || '').trim();
          if (musicaUrl) break;
        }
      }
    }

    if (!musicaUrl) musicaUrl = 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Sicilian_Sunset.mp3';
    return {
      success: true,
      url: musicaUrl,
      playlist: [
        { titolo: 'Sicilian Sunset', url: 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Sicilian_Sunset.mp3', stile: 'Acoustic Lounge / Emozione' },
        { titolo: 'Calma del Mediodía', url: 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Calma_del_Mediodia.mp3', stile: 'Chillout Ambient / Eleganza' },
        { titolo: 'Back Road Out of Town', url: 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Back_Road_Out_of_Town.mp3', stile: 'Soft Acoustic Groove / Modern House' }
      ]
    };
  } catch(e) {
    return {
      success: false,
      url: 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Sicilian_Sunset.mp3',
      playlist: [
        { titolo: 'Sicilian Sunset', url: 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Sicilian_Sunset.mp3', stile: 'Acoustic Lounge / Emozione' },
        { titolo: 'Calma del Mediodía', url: 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Calma_del_Mediodia.mp3', stile: 'Chillout Ambient / Eleganza' },
        { titolo: 'Back Road Out of Town', url: 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Back_Road_Out_of_Town.mp3', stile: 'Soft Acoustic Groove / Modern House' }
      ]
    };
  }
}

function popolaMusicaSottofondoRoyaltyFree() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, error: 'Spreadsheet non trovato' };

    var sheet = ss.getSheetByName('Musica_Sottofondo');
    if (!sheet) {
      sheet = ss.insertSheet('Musica_Sottofondo');
    } else {
      sheet.clearContents();
    }
    sheet.getRange(1, 1, 1, 4).setValues([['Titolo_Brano_A', 'URL_Audio_MP3_B', 'Genere_Stile_C', 'Attiva_D']]);
    sheet.getRange('A1:D1').setFontWeight('bold').setBackground('#27ae60').setFontColor('#ffffff');

    var playlistSafe = [
      ['Sicilian Sunset', 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Sicilian_Sunset.mp3', 'Acoustic Lounge / Emozione', 'SI'],
      ['Calma del Mediodía', 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Calma_del_Mediodia.mp3', 'Chillout Ambient / Eleganza', 'SI'],
      ['Back Road Out of Town', 'https://raw.githubusercontent.com/Tonyhood2345/live-stream-serverless/main/assets/musica/Back_Road_Out_of_Town.mp3', 'Soft Acoustic Groove / Modern House', 'SI']
    ];

    playlistSafe.forEach(function(row) {
      sheet.appendRow(row);
    });

    return {
      success: true,
      messaggio: "Foglio 'Musica_Sottofondo' aggiornato con le musiche ufficiali di Immobiliare Giancani!",
      count: playlistSafe.length,
      playlist: playlistSafe
    };
  } catch(e) {
    inviaAllertaErroreTelegram("03_DatiImmobile.js", "popolaMusicaSottofondoRoyaltyFree", e.toString());
    return { success: false, error: e.toString() };
  }
}

// ═══════════════════════════════════════════════════════════════════════
// 🎭 GESTIONE BATTUTE COMICHE & IRONICHE DARIO (RIGOROSAMENTE COLONNA F)
// ═══════════════════════════════════════════════════════════════════════

/**
 * Inizializza e popola il foglio 'Battute_Dario' se non esiste.
 * Le battute sono rigorosamente collocate nella Colonna F (Indice 5)
 */
function inizializzaFoglioBattuteDario() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, error: "Spreadsheet non accessibile" };

    var sheet = ss.getSheetByName('Battute_Dario');
    if (!sheet) {
      sheet = ss.insertSheet('Battute_Dario');
      sheet.appendRow([
        'ID_A',
        'Categoria_B',
        'Ambiente_C',
        'Tono_D',
        'Autore_E',
        'Battuta_Dario_Colonna_F',
        'Attiva_G'
      ]);
      sheet.getRange('A1:G1').setFontWeight('bold').setBackground('#c9a35e').setFontColor('#120c04');
    }

    if (sheet.getLastRow() < 2) {
      var battuteIniziali = [
        ['BAT_01', 'Comica', 'Soggiorno', 'Ironico', 'DarIO', 'DarIA, in questo soggiorno ci starebbe un maxi schermo così grande che i vicini guarderebbero la partita gratis dalla collina di fronte! — Immobiliare Giancani', 'SI'],
        ['BAT_02', 'Divertente', 'Cucina', 'Comico', 'DarIO', 'Questa cucina è così luminosa e invitante che persino la mia pasta al forno surgelata sembrerà un piatto da stella Michelin! — Immobiliare Giancani', 'SI'],
        ['BAT_03', 'Ironica', 'Terrazzo', 'Solare', 'DarIO', 'Guardando questo balcone panoramico mi è venuta un idea geniale: mi trasferisco qui io e la diretta la facciamo direttamente in ciabatte e prendisole! — Immobiliare Giancani', 'SI'],
        ['BAT_04', 'Comica', 'Camera Notte', 'Divertente', 'DarIO', 'Stanza matrimoniale fantastica e insonorizzata: finalmente un posto dove posso cantare sotto la doccia senza che il quartiere chiami i rinforzi! — Immobiliare Giancani', 'SI'],
        ['BAT_05', 'Ironica', 'Bagno', 'Comico', 'DarIO', 'Con un bagno così elegante e spazioso, le signore non ci metteranno più due ore a prepararsi: ce ne metteranno almeno quattro con gran piacere! — Immobiliare Giancani', 'SI'],
        ['BAT_06', 'Divertente', 'Mercato', 'Ironico', 'DarIO', 'DarIA, diciamolo chiaramente: comprare questa casa conviene persino al portafoglio, visti i prezzi e il valore che solo Immobiliare Giancani sa garantire! — Immobiliare Giancani', 'SI'],
        ['BAT_07', 'Solare', 'Panoramica', 'Divertente', 'DarIO', 'Un terrazzo così spettacolare che il tramonto di Agrigento sembra fatto su misura per essere fotografato e postato ogni singolo giorno! — Immobiliare Giancani', 'SI'],
        ['BAT_08', 'Comica', 'Garage', 'Comico', 'DarIO', 'Questo garage è così capiente che ci entra l auto, la moto, la bicicletta e persino tutte le scarpe che DarIA nasconde al marito! — Immobiliare Giancani', 'SI'],
        ['BAT_09', 'Ironica', 'Spazi Ampi', 'Ironico', 'DarIO', 'Spazi ampi e ariosi: pensate che c è così tanto spazio che se litighi con tua moglie ci metti tre giorni per incontrarla di nuovo in corridoio! — Immobiliare Giancani', 'SI'],
        ['BAT_10', 'Divertente', 'Luminosità', 'Solare', 'DarIO', 'Con una luminosità naturale del genere, risparmiate sulla bolletta elettrica e vi fate pure la tintarella direttamente sul divano! — Immobiliare Giancani', 'SI'],
        ['BAT_11', 'Comica', 'Ospiti', 'Comico', 'DarIO', 'Se prendete questa casa, il vero problema sarà cacciare via gli amici che verranno per un caffè e non vorranno più andarsene prima di cena! — Immobiliare Giancani', 'SI'],
        ['BAT_12', 'Ironica', 'Cucina', 'Divertente', 'DarIO', 'Cucina da veri chef: qui anche chi brucia l acqua per il tè si sentirà all istante il nuovo Cannavacciuolo di Favara! — Immobiliare Giancani', 'SI'],
        ['BAT_13', 'Solare', 'Terrazza Estiva', 'Comico', 'DarIO', 'DarIA, io qui ci vedo già le cene d estate con gli arancini caldi e la brezza marina che rinfresca la serata: firmo io l offerta adesso? — Immobiliare Giancani', 'SI'],
        ['BAT_14', 'Divertente', 'Finiture', 'Ironico', 'DarIO', 'Con queste finiture di pregio, anche il robot aspirapolvere si metterà la cravatta per pulire il pavimento con rispetto! — Immobiliare Giancani', 'SI'],
        ['BAT_15', 'Solare', 'Posizione', 'Divertente', 'DarIO', 'Posizione strategica e vista incantevole: qui la sveglia del lunedì mattina sembra quasi una carezza e non un dramma quotidiano! — Immobiliare Giancani', 'SI'],
        ['BAT_16', 'Comica', 'Diretta Live', 'Comico', 'DarIO', 'DarIA, se gli spettatori in chat non bloccano subito questa dimora, vi avverto che domani mattina ci porto già i miei scatoloni! — Immobiliare Giancani', 'SI']
      ];

      battuteIniziali.forEach(function(row) {
        sheet.appendRow(row);
      });
    }

    return { success: true, count: Math.max(0, sheet.getLastRow() - 1) };
  } catch(e) {
    inviaAllertaErroreTelegram("03_DatiImmobile.js", "inizializzaFoglioBattuteDario", e.toString());
    return { success: false, error: e.toString() };
  }
}

/**
 * Aggiorna il foglio Battute_Dario già esistente per allineare il personal branding ad Immobiliare Giancani
 */
function aggiornaFoglioBattuteDarioBranding() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, error: "Spreadsheet non accessibile" };
    var sheet = ss.getSheetByName('Battute_Dario');
    if (!sheet || sheet.getLastRow() < 2) return inizializzaFoglioBattuteDario();

    var lastRow = sheet.getLastRow();
    var range = sheet.getRange(2, 6, lastRow - 1, 1);
    var values = range.getValues();
    var updated = false;

    for (var r = 0; r < values.length; r++) {
      var val = String(values[r][0] || '').trim();
      if (val) {
        var newVal = val.replace(/—\s*Antonio\s*Giancani/gi, '— Immobiliare Giancani')
                        .replace(/Antonio\s*Giancani/gi, 'Immobiliare Giancani');
        newVal = newVal.replace(/(—\s*Immobiliare\s*Giancani)+/gi, '— Immobiliare Giancani').trim();
        if (newVal.indexOf('Immobiliare Giancani') === -1) {
          newVal = newVal + ' — Immobiliare Giancani';
        }
        if (newVal !== val) {
          values[r][0] = newVal;
          updated = true;
        }
      }
    }
    if (updated) {
      range.setValues(values);
    }
    return { success: true, updated: updated, count: values.length };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * Restituisce l'elenco completo delle battute di DarIO estraendole rigorosamente da Colonna F (Indice 5)
 */
function getBattuteDarioList() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return getBattuteDarioFallback();

    var sheet = ss.getSheetByName('Battute_Dario');
    if (!sheet || sheet.getLastRow() < 2) {
      inizializzaFoglioBattuteDario();
      sheet = ss.getSheetByName('Battute_Dario');
    }

    if (!sheet || sheet.getLastRow() < 2) return getBattuteDarioFallback();

    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(2, 1, lastRow - 1, 7).getValues();
    var battute = [];

    for (var r = 0; r < data.length; r++) {
      var colF = String(data[r][5] || '').trim(); // RIGOROSAMENTE COLONNA F (Indice 5)
      var attiva = String(data[r][6] || 'SI').trim().toUpperCase();
      if (colF && (attiva === 'SI' || attiva === 'SÌ' || attiva === 'YES' || attiva === '1' || attiva === '')) {
        var pulita = pulisciTestoPerTTSBackend(colF);
        pulita = pulita.replace(/—\s*Antonio\s*Giancani/gi, '— Immobiliare Giancani')
                       .replace(/Antonio\s*Giancani/gi, 'Immobiliare Giancani');
        pulita = pulita.replace(/(—\s*Immobiliare\s*Giancani)+/gi, '— Immobiliare Giancani').trim();
        if (pulita.indexOf('Immobiliare Giancani') === -1) {
          pulita = pulita + ' — Immobiliare Giancani';
        }
        battute.push(pulita);
      }
    }

    return battute.length > 0 ? battute : getBattuteDarioFallback();
  } catch(e) {
    return getBattuteDarioFallback();
  }
}

/**
 * Estrae una battuta casuale di DarIO da Colonna F
 */
function getBattutaDarioCasuale() {
  try {
    var lista = getBattuteDarioList();
    var idx = Math.floor(Math.random() * lista.length);
    var b = lista[idx] || "DarIA, con questa casa l affare è assicurato: parliamo di un eccellenza assoluta! — Immobiliare Giancani";
    b = b.replace(/—\s*Antonio\s*Giancani/gi, '— Immobiliare Giancani')
         .replace(/Antonio\s*Giancani/gi, 'Immobiliare Giancani');
    b = b.replace(/(—\s*Immobiliare\s*Giancani)+/gi, '— Immobiliare Giancani').trim();
    if (b.indexOf('Immobiliare Giancani') === -1) {
      b = b.trim() + ' — Immobiliare Giancani';
    }
    return b;
  } catch(e) {
    return "DarIA, con questa casa l affare è assicurato: parliamo di un eccellenza assoluta! — Immobiliare Giancani";
  }
}

function getBattuteDarioFallback() {
  return [
    "DarIA, in questo soggiorno ci starebbe un maxi schermo così grande che i vicini guarderebbero la partita gratis dalla collina di fronte! — Immobiliare Giancani",
    "Questa cucina è così luminosa e invitante che persino la mia pasta al forno surgelata sembrerà un piatto da stella Michelin! — Immobiliare Giancani",
    "Guardando questo balcone panoramico mi è venuta un idea geniale: mi trasferisco qui io e la diretta la facciamo direttamente in ciabatte e prendisole! — Immobiliare Giancani",
    "Stanza matrimoniale fantastica e insonorizzata: finalmente un posto dove posso cantare sotto la doccia senza che il quartiere chiami i rinforzi! — Immobiliare Giancani",
    "Con un bagno così elegante e spazioso, le signore non ci metteranno più due ore a prepararsi: ce ne metteranno almeno quattro con gran piacere! — Immobiliare Giancani",
    "Questo garage è così capiente che ci entra l auto, la moto, la bicicletta e persino tutte le scarpe che DarIA nasconde al marito! — Immobiliare Giancani",
    "Spazi ampi e ariosi: pensate che c è così tanto spazio che se litighi con tua moglie ci metti tre giorni per incontrarla di nuovo in corridoio! — Immobiliare Giancani",
    "Con queste finiture di pregio, anche il robot aspirapolvere si metterà la cravatta per pulire il pavimento con rispetto! — Immobiliare Giancani"
  ];
}

/**
 * Restituisce l'elenco delle notizie sportive e attualità da Colonna F (Indice 5)
 */
function getNotizieSportList() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return getNotizieSportFallback();

    var sheet = ss.getSheetByName('Notizie_Sport_Attualita');
    if (!sheet || sheet.getLastRow() < 2) return getNotizieSportFallback();

    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(2, 1, lastRow - 1, Math.max(sheet.getLastColumn(), 6)).getValues();
    var items = [];

    for (var r = 0; r < data.length; r++) {
      var colF = String(data[r][5] || '').trim(); // RIGOROSAMENTE COLONNA F (Indice 5)
      if (colF && colF.length > 5) {
        var pulita = pulisciTestoPerTTSBackend(colF);
        items.push(pulita);
      }
    }
    return items.length > 0 ? items : getNotizieSportFallback();
  } catch(e) {
    return getNotizieSportFallback();
  }
}

function getNotiziaSportCasuale() {
  try {
    var lista = getNotizieSportList();
    var idx = Math.floor(Math.random() * lista.length);
    return lista[idx] || getNotizieSportFallback()[0];
  } catch(e) {
    return getNotizieSportFallback()[0];
  }
}

function getNotizieSportFallback() {
  return [
    "Notizia flash sportiva: Serie A in grande spolvero con sfide mozzafiato per la vetta della classifica e grandissimo spettacolo. — Immobiliare Giancani",
    "Notizia flash sportiva: Notti magiche di Champions League con i top club d Europa pronti a darsi battaglia sul campo. — Immobiliare Giancani",
    "Grande momento per il tennis italiano con i nostri campioni protagonisti nei tornei più prestigiosi del mondo. — Immobiliare Giancani"
  ];
}

/**
 * Restituisce l'elenco delle pillole e nozioni immobiliari da Colonna F (Indice 5)
 */
function getNozioniImmobiliariList() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return getNozioniImmobiliariFallback();

    var sheet = ss.getSheetByName('Nozioni_Immobiliari');
    if (!sheet || sheet.getLastRow() < 2) return getNozioniImmobiliariFallback();

    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(2, 1, lastRow - 1, Math.max(sheet.getLastColumn(), 6)).getValues();
    var items = [];

    for (var r = 0; r < data.length; r++) {
      var colF = String(data[r][5] || '').trim(); // RIGOROSAMENTE COLONNA F (Indice 5)
      if (colF && colF.length > 5) {
        var pulita = pulisciTestoPerTTSBackend(colF);
        items.push(pulita);
      }
    }
    return items.length > 0 ? items : getNozioniImmobiliariFallback();
  } catch(e) {
    return getNozioniImmobiliariFallback();
  }
}

function getNozioneImmobiliareCasuale() {
  try {
    var lista = getNozioniImmobiliariList();
    var idx = Math.floor(Math.random() * lista.length);
    return lista[idx] || getNozioniImmobiliariFallback()[0];
  } catch(e) {
    return getNozioniImmobiliariFallback()[0];
  }
}

function getNozioniImmobiliariFallback() {
  return [
    "Il rogito notarile rappresenta l atto pubblico definitivo con cui si formalizza il trasferimento della proprietà con la massima garanzia giuridica. — Immobiliare Giancani",
    "La conformità catastale e urbanistica è il requisito fondamentale per comprare e vendere casa in totale tranquillità e sicurezza. — Immobiliare Giancani",
    "Una corretta valutazione dell immobile e un efficiente classe energetica valorizzano l investimento nel tempo. — Immobiliare Giancani"
  ];
}

/**
 * Restituisce l'elenco delle battute duo da Colonna F (Indice 5)
 */
function getDialoghiDuoList() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return getDialoghiDuoFallback();

    var sheet = ss.getSheetByName('Dialoghi_Duo');
    if (!sheet || sheet.getLastRow() < 2) return getDialoghiDuoFallback();

    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(2, 1, lastRow - 1, Math.max(sheet.getLastColumn(), 6)).getValues();
    var items = [];

    for (var r = 0; r < data.length; r++) {
      var colF = String(data[r][5] || '').trim(); // RIGOROSAMENTE COLONNA F (Indice 5)
      if (colF && colF.length > 5) {
        var pulita = pulisciTestoPerTTSBackend(colF);
        items.push(pulita);
      }
    }
    return items.length > 0 ? items : getDialoghiDuoFallback();
  } catch(e) {
    return getDialoghiDuoFallback();
  }
}

function getDialogoDuoCasuale() {
  try {
    var lista = getDialoghiDuoList();
    var idx = Math.floor(Math.random() * lista.length);
    return lista[idx] || getDialoghiDuoFallback()[0];
  } catch(e) {
    return getDialoghiDuoFallback()[0];
  }
}

function getDialoghiDuoFallback() {
  return [
    "DarIA, secondo me il caffè viene molto più buono nelle case proposte da Immobiliare Giancani! — Immobiliare Giancani",
    "DarIA, la scienza non l ha ancora confermato al cento per cento, ma la felicità di una casa nuova rende tutto più sereno! — Immobiliare Giancani",
    "Amici in ascolto, mettete tanti Like e condividete la diretta: trovare la casa perfetta non è mai stato così divertente! — Immobiliare Giancani"
  ];
}

/**
 * Estrae una storia della città casuale da Colonna F
 */
function getStoriaCittaCasuale() {
  try {
    if (typeof getStorieCittaList === 'function') {
      var lista = getStorieCittaList();
      if (lista && lista.length > 0) {
        var idx = Math.floor(Math.random() * lista.length);
        var s = lista[idx];
        if (s) return pulisciTestoPerTTSBackend(s);
      }
    }
  } catch(e) {}
  return "Favara è celebre nel mondo per il Farm Cultural Park: un polo di arte contemporanea a cielo aperto unico e straordinario. — Immobiliare Giancani";
}

/**
 * Intervento multischeda alternato per DarIO:
 * Alterna dinamicamente tra:
 * 1. Battute Comiche (Battute_Dario)
 * 2. Storia & Territorio (Storyteller_Citta)
 * 3. Sport & Attualità (Notizie_Sport_Attualita)
 * 4. Nozioni & Consigli Immobiliari (Nozioni_Immobiliari)
 * 5. Dialoghi & Battute Duo (Dialoghi_Duo)
 */
function getInterventoDarioMultischeda(roomIndex, roomName) {
  try {
    if (roomName && String(roomName).toLowerCase().match(/bagno|toilette|wc|servizio|servizi/i)) {
      return {
        tipo: 'bagno_astratto',
        categoria: 'bagno_astratto',
        testo: "DarIA, hai colto nel segno! Il bagno è il luogo delle grandi riflessioni. E pensavo proprio a quante volte si cerca una stanza introvabile in un classico appartamento, come una palestra privata, una lavanderia esterna o una spa interna. Ma la forza di Immobiliare Giancani è proprio questa: saper trasformare i desideri astratti in progetti concreti per ogni cliente! — Immobiliare Giancani",
        speakerLabel: '🛁 DARIO • RIFLESSIONE BAGNO & SPA'
      };
    }

    var rotazione = ['battuta', 'citta', 'sport', 'nozione', 'dialogo'];
    var rIndex = (typeof roomIndex === 'number' && !isNaN(roomIndex)) ? roomIndex : Math.floor(Math.random() * rotazione.length);
    var categoria = rotazione[Math.abs(rIndex) % rotazione.length];

    var res = {
      tipo: categoria,
      categoria: categoria,
      testo: '',
      speakerLabel: ''
    };

    if (categoria === 'battuta') {
      res.testo = getBattutaDarioCasuale();
      res.speakerLabel = '💻 DARIO • BATTUTA LIVE & UMORE';
    } else if (categoria === 'citta') {
      res.testo = getStoriaCittaCasuale();
      res.speakerLabel = '🏛️ DARIO • STORIA & TERRITORIO';
    } else if (categoria === 'sport') {
      res.testo = getNotiziaSportCasuale();
      res.speakerLabel = '⚽ DARIO • SPORT & ATTUALITÀ';
    } else if (categoria === 'nozione') {
      res.testo = getNozioneImmobiliareCasuale();
      res.speakerLabel = '📋 DARIO • CONSIGLIO IMMOBILIARE';
    } else {
      res.testo = getDialogoDuoCasuale();
      res.speakerLabel = '🎭 DARIO • DIALOGO IN DIRETTA';
    }

    return res;
  } catch(e) {
    return {
      tipo: 'battuta',
      categoria: 'battuta',
      testo: getBattutaDarioCasuale(),
      speakerLabel: '💻 DARIO • ANALISI MERCATO & BATTUTA'
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════
// 🔍 GESTIONE ZOOM CALIBRATO DIRETTA (50% - 250%)
// ═══════════════════════════════════════════════════════════════════════

function salvaZoomDiretta(val) {
  try {
    var num = parseInt(val, 10);
    if (isNaN(num)) num = 125;
    if (num < 50) num = 50;
    if (num > 250) num = 250;

    var props = PropertiesService.getScriptProperties();
    props.setProperty('STREAM_ZOOM', num.toString());
    return { success: true, zoom: num };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function getZoomDiretta() {
  try {
    var raw = PropertiesService.getScriptProperties().getProperty('STREAM_ZOOM');
    var num = parseInt(raw, 10);
    if (isNaN(num) || num < 50 || num > 250) return 125;
    return num;
  } catch(e) {
    return 125;
  }
}

// ═══════════════════════════════════════════════════════════════════════
// 🗣️ GESTIONE CONFIGURAZIONE VOCI REGIA (DARIA & DARIO)
// ═══════════════════════════════════════════════════════════════════════

function salvaConfigurazioneVoci(cfg) {
  try {
    cfg = cfg || {};
    var props = PropertiesService.getScriptProperties();
    if (cfg.voceDaria !== undefined) props.setProperty('VOCE_DARIA', String(cfg.voceDaria));
    if (cfg.voceDario !== undefined) props.setProperty('VOCE_DARIO', String(cfg.voceDario));
    if (cfg.pitchDaria !== undefined) props.setProperty('PITCH_DARIA', String(cfg.pitchDaria));
    if (cfg.pitchDario !== undefined) props.setProperty('PITCH_DARIO', String(cfg.pitchDario));
    if (cfg.rateDaria !== undefined) props.setProperty('RATE_DARIA', String(cfg.rateDaria));
    if (cfg.rateDario !== undefined) props.setProperty('RATE_DARIO', String(cfg.rateDario));

    return { success: true, config: getConfigurazioneVoci() };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function getConfigurazioneVoci() {
  try {
    var props = PropertiesService.getScriptProperties();
    return {
      voceDaria: props.getProperty('VOCE_DARIA') || 'it-IT-ElsaNeural',
      voceDario: props.getProperty('VOCE_DARIO') || 'it-IT-DiegoNeural',
      pitchDaria: parseFloat(props.getProperty('PITCH_DARIA') || '1.18'),
      pitchDario: parseFloat(props.getProperty('PITCH_DARIO') || '0.84'),
      rateDaria: parseFloat(props.getProperty('RATE_DARIA') || '1.02'),
      rateDario: parseFloat(props.getProperty('RATE_DARIO') || '0.98')
    };
  } catch(e) {
    return {
      voceDaria: 'it-IT-ElsaNeural', voceDario: 'it-IT-DiegoNeural',
      pitchDaria: 1.18, pitchDario: 0.84,
      rateDaria: 1.02, rateDario: 0.98
    };
  }
}


// ═══════════════════════════════════════════════════════════════════════
// 🎭 GESTORE FOGLIO 'Dialoghi_avat_tutti' & SINCRONIZZAZIONE VOCI AVATAR
// ═══════════════════════════════════════════════════════════════════════

/**
 * Parser CSV di supporto
 */
function parseCsvLineBackend(line) {
  if (!line) return [];
  var str = line.toString();
  var result = [];
  var cur = '';
  var inQuotes = false;
  for (var i = 0; i < str.length; i++) {
    var c = str[i];
    if (c === '"') {
      if (inQuotes && i + 1 < str.length && str[i + 1] === '"') {
        cur += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (c === ',' && !inQuotes) {
      result.push(cur.trim());
      cur = '';
    } else {
      cur += c;
    }
  }
  result.push(cur.trim());
  return result;
}

/**
 * Estrae e sincronizza tutti i dialoghi degli avatar dal foglio 'Dialoghi_avat_tutti'
 * Estrae rigorosamente i testi da Colonna F (Indice 5) per il testo recitato
 * (con fallback su Colonna C se Colonna F non è ancora popolata).
 * Ogni battuta viene processata per pronuncia vocale (mq -> metri quadri)
 * e termina evidenziando 'Immobiliare Giancani' per il personal branding.
 */
function getDialoghiAvatTuttiList() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return getDialoghiAvatTuttiFallback();

    var sheet = ss.getSheetByName('Dialoghi_avat_tutti');
    if (!sheet || sheet.getLastRow() < 2) return getDialoghiAvatTuttiFallback();

    var lastRow = sheet.getLastRow();
    var maxCol = sheet.getMaxColumns();
    var numColsToRead = Math.min(Math.max(sheet.getLastColumn(), 1), maxCol);
    var data = sheet.getRange(2, 1, lastRow - 1, numColsToRead).getValues();
    var sceneList = [];

    // Mappa configurazioni personaggi ufficiali
    var charProfiles = {
      'daria': { nome: 'Daria', label: '[DARIA]', colore: '#FFB6C1', voce: 'it-IT-ElsaNeural', pitch: 1.18, rate: 1.02, isGuest: false },
      'dario': { nome: 'DarIO', label: '[DARIO]', colore: '#00BFFF', voce: 'it-IT-DiegoNeural', pitch: 0.84, rate: 0.98, isGuest: false },
      'beatrice': { nome: 'Beatrice', label: '[BEATRICE]', colore: '#E6E6FA', voce: 'it-IT-IsabellaNeural', pitch: 1.10, rate: 1.05, isGuest: true },
      'tina': { nome: 'Tina', label: '[TINA]', colore: '#FFA500', voce: 'it-IT-FabiolaNeural', pitch: 1.22, rate: 1.00, isGuest: true },
      'chiara': { nome: 'Chiara', label: '[CHIARA]', colore: '#98FB98', voce: 'it-IT-PalmiraNeural', pitch: 0.98, rate: 0.98, isGuest: true },
      'walter': { nome: 'Walter', label: '[WALTER]', colore: '#FFD700', voce: 'it-IT-GiuseppeNeural', pitch: 0.78, rate: 1.02, isGuest: true },
      'ugo': { nome: 'Ugo', label: '[UGO]', colore: '#FF6347', voce: 'it-IT-GianniNeural', pitch: 0.88, rate: 0.92, isGuest: true },
      'leo': { nome: 'Leo', label: '[LEO]', colore: '#00FFCC', voce: 'it-IT-PierluigiNeural', pitch: 0.95, rate: 1.06, isGuest: true }
    };

    for (var r = 0; r < data.length; r++) {
      var row = data[r];
      var idDialogo = String(row[0] || (r + 1)).trim();
      var rawPersonaggio = String(row[1] || 'daria').toLowerCase().trim();
      var nomeOriginaleB = String(row[1] || '').trim();

      // Risoluzione ID personaggio
      var whoId = 'daria';
      if (rawPersonaggio.indexOf('daria') !== -1) whoId = 'daria';
      else if (rawPersonaggio.indexOf('dario') !== -1) whoId = 'dario';
      else if (rawPersonaggio.indexOf('beatrice') !== -1) whoId = 'beatrice';
      else if (rawPersonaggio.indexOf('tina') !== -1) whoId = 'tina';
      else if (rawPersonaggio.indexOf('chiara') !== -1) whoId = 'chiara';
      else if (rawPersonaggio.indexOf('walter') !== -1) whoId = 'walter';
      else if (rawPersonaggio.indexOf('ugo') !== -1) whoId = 'ugo';
      else if (rawPersonaggio.indexOf('leo') !== -1) whoId = 'leo';

      var prof = charProfiles[whoId] || charProfiles['daria'];

      // ESTRAZIONE RIGOROSA COLONNA F (Indice 5)
      var testoF = (numColsToRead >= 6) ? String(row[5] || '').trim() : '';
      var rawTesto = testoF;
      if (!rawTesto || rawTesto.length < 5) {
        rawTesto = String(row[2] || '').trim(); // Fallback se Colonna F non ancora popolata
      }

      if (!rawTesto || rawTesto.length < 3) continue;

      // Pulizia testo: conversione mq -> metri quadri e firma '— Immobiliare Giancani'
      var testoPulito = pulisciTestoPerTTSBackend(rawTesto);

      sceneList.push({
        idDialogo: idDialogo,
        idScena: idDialogo + '_' + (r + 1),
        riga: r + 2,
        who: whoId,
        speaker: whoId.toUpperCase(),
        nome: prof.nome || (nomeOriginaleB ? (nomeOriginaleB.charAt(0).toUpperCase() + nomeOriginaleB.slice(1)) : whoId.toUpperCase()),
        personaggioColonnaB: nomeOriginaleB || prof.nome,
        labelTopBar: prof.label,
        coloreHex: prof.colore,
        boxDestroOspite: prof.isGuest ? whoId.toUpperCase() : 'DARIO',
        isGuest: prof.isGuest,
        voce: prof.voce,
        pitch: prof.pitch,
        rate: prof.rate,
        testoRecitato: testoPulito
      });
    }

    return sceneList.length > 0 ? sceneList : getDialoghiAvatTuttiFallback();
  } catch(e) {
    console.error("Errore getDialoghiAvatTuttiList:", e);
    return getDialoghiAvatTuttiFallback();
  }
}

/**
 * Organizza e impagina il foglio 'Dialoghi_avat_tutti' in colonne separate e strutturate,
 * posizionando il Testo Recitato rigorosamente in Colonna F (Indice 5, Colonna 6).
 */
function organizzaFoglioDialoghiAvatTutti() {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, error: "Spreadsheet non trovato" };
    var sheet = ss.getSheetByName('Dialoghi_avat_tutti');
    if (!sheet) return { success: false, error: "Foglio Dialoghi_avat_tutti non trovato" };

    var lastRow = sheet.getLastRow();
    if (lastRow < 2) return { success: false, error: "Foglio vuoto o senza dati" };

    // Se il foglio ha meno di 7 colonne, aggiungi colonne sufficienti
    var curMaxCols = sheet.getMaxColumns();
    if (curMaxCols < 7) {
      sheet.insertColumnsAfter(curMaxCols, 7 - curMaxCols);
    }

    var charProfiles = {
      'daria': { label: '[DARIA]', colore: '#FFB6C1', voce: 'it-IT-ElsaNeural' },
      'dario': { label: '[DARIO]', colore: '#00BFFF', voce: 'it-IT-DiegoNeural' },
      'beatrice': { label: '[BEATRICE]', colore: '#E6E6FA', voce: 'it-IT-IsabellaNeural' },
      'tina': { label: '[TINA]', colore: '#FFA500', voce: 'it-IT-FabiolaNeural' },
      'chiara': { label: '[CHIARA]', colore: '#98FB98', voce: 'it-IT-PalmiraNeural' },
      'walter': { label: '[WALTER]', colore: '#FFD700', voce: 'it-IT-GiuseppeNeural' },
      'ugo': { label: '[UGO]', colore: '#FF6347', voce: 'it-IT-GianniNeural' },
      'leo': { label: '[LEO]', colore: '#00FFCC', voce: 'it-IT-PierluigiNeural' }
    };

    var data = sheet.getRange(1, 1, lastRow, 3).getValues();
    var outRows = [];

    // Header standard con Colonna F rigorosamente dedicata a Testo Recitato
    outRows.push([
      "ID_Dialogo",
      "Personaggio",
      "Battuta_Originale",
      "Label_TopBar",
      "Colore_Hex",
      "Testo_Recitato", // RIGOROSAMENTE COLONNA F (Colonna 6, Indice 5)
      "Voce_Assegnata"
    ]);

    for (var r = 1; r < data.length; r++) {
      var id = data[r][0] || (r);
      var pers = String(data[r][1] || 'daria').toLowerCase().trim();
      var orig = String(data[r][2] || '').trim();

      var whoId = 'daria';
      if (pers.indexOf('daria') !== -1) whoId = 'daria';
      else if (pers.indexOf('dario') !== -1) whoId = 'dario';
      else if (pers.indexOf('beatrice') !== -1) whoId = 'beatrice';
      else if (pers.indexOf('tina') !== -1) whoId = 'tina';
      else if (pers.indexOf('chiara') !== -1) whoId = 'chiara';
      else if (pers.indexOf('walter') !== -1) whoId = 'walter';
      else if (pers.indexOf('ugo') !== -1) whoId = 'ugo';
      else if (pers.indexOf('leo') !== -1) whoId = 'leo';

      var prof = charProfiles[whoId] || charProfiles['daria'];
      var txtPulito = pulisciTestoPerTTSBackend(orig);

      outRows.push([
        id,
        whoId,
        orig,
        prof.label,
        prof.colore,
        txtPulito, // RIGOROSAMENTE COLONNA F!
        prof.voce
      ]);
    }

    sheet.getRange(1, 1, outRows.length, 7).setValues(outRows);
    SpreadsheetApp.flush();
    return { success: true, righeOrganizzate: outRows.length - 1, colonne: 7 };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * Fallback dialoghi copione con tutti gli 8 personaggi integrati
 */
function getDialoghiAvatTuttiFallback() {
  return [
    {
      idScena: "1",
      who: "dario",
      speaker: "DARIO",
      labelTopBar: "[DARIO]",
      coloreHex: "#00BFFF",
      boxDestroOspite: "DARIO",
      voce: "it-IT-DiegoNeural",
      pitch: 0.84,
      rate: 0.98,
      testoRecitato: "DarIA, guarda che ingresso luminoso! Qui non serve nemmeno accendere la luce per trovare le chiavi di casa! — Immobiliare Giancani"
    },
    {
      idScena: "2",
      who: "daria",
      speaker: "DARIA",
      labelTopBar: "[DARIA]",
      coloreHex: "#FFB6C1",
      boxDestroOspite: "DARIO",
      voce: "it-IT-ElsaNeural",
      pitch: 1.18,
      rate: 1.02,
      testoRecitato: "La luce naturale riscalda l'anima Dario, e con la cura di Immobiliare Giancani ogni spazio è pensato per accogliere la famiglia con gioia! — Immobiliare Giancani"
    },
    {
      idScena: "3",
      who: "beatrice",
      speaker: "BEATRICE",
      labelTopBar: "[BEATRICE]",
      coloreHex: "#E6E6FA",
      boxDestroOspite: "BEATRICE",
      voce: "it-IT-IsabellaNeural",
      pitch: 1.10,
      rate: 1.05,
      testoRecitato: "I toni pastello di questo corridoio creano una transizione perfetta verso la zona notte, donando calma ed equilibrio visivo. — Immobiliare Giancani"
    },
    {
      idScena: "4",
      who: "dario",
      speaker: "DARIO",
      labelTopBar: "[DARIO]",
      coloreHex: "#00BFFF",
      boxDestroOspite: "DARIO",
      voce: "it-IT-DiegoNeural",
      pitch: 0.84,
      rate: 0.98,
      testoRecitato: "E soprattutto c'è spazio per una scarpiera dove nascondere tutte le mie scarpe da ginnastica prima che Daria le veda! — Immobiliare Giancani"
    },
    {
      idScena: "5",
      who: "ugo",
      speaker: "UGO",
      labelTopBar: "[UGO]",
      coloreHex: "#FF6347",
      boxDestroOspite: "UGO",
      voce: "it-IT-GianniNeural",
      pitch: 0.88,
      rate: 0.92,
      testoRecitato: "Daria, ho ispezionato il quadro elettrico: interruttori magnetotermici differenziali separati per ogni stanza. Protezione totale da cortocircuiti! — Immobiliare Giancani"
    },
    {
      idScena: "6",
      who: "daria",
      speaker: "DARIA",
      labelTopBar: "[DARIA]",
      coloreHex: "#FFB6C1",
      boxDestroOspite: "DARIO",
      voce: "it-IT-ElsaNeural",
      pitch: 1.18,
      rate: 1.02,
      testoRecitato: "La sicurezza dell'impianto elettrico è la base per la serenità di chi ha bambini piccoli, un punto fermo garantito da Immobiliare Giancani! — Immobiliare Giancani"
    },
    {
      idScena: "7",
      who: "walter",
      speaker: "WALTER",
      labelTopBar: "[WALTER]",
      coloreHex: "#FFD700",
      boxDestroOspite: "WALTER",
      voce: "it-IT-GiuseppeNeural",
      pitch: 0.78,
      rate: 1.02,
      testoRecitato: "Notate la posizione: siamo a due passi da scuole e negozi. Questo significa zero svalutazione e massima rivendibilità nel tempo! — Immobiliare Giancani"
    },
    {
      idScena: "8",
      who: "tina",
      speaker: "TINA",
      labelTopBar: "[TINA]",
      coloreHex: "#FFA500",
      boxDestroOspite: "TINA",
      voce: "it-IT-FabiolaNeural",
      pitch: 1.22,
      rate: 1.00,
      testoRecitato: "Significa soprattutto che i bambini possono andare a piedi a scuola senza ansie per le mamme, una vera benedizione quotidiana! — Immobiliare Giancani"
    },
    {
      idScena: "9",
      who: "chiara",
      speaker: "CHIARA",
      labelTopBar: "[CHIARA]",
      coloreHex: "#98FB98",
      boxDestroOspite: "CHIARA",
      voce: "it-IT-PalmiraNeural",
      pitch: 0.98,
      rate: 0.98,
      testoRecitato: "Questo giardino d'inverno è una favola: ci vedo già le piante curate con amore e i piccoli che fanno i compiti al sole. — Immobiliare Giancani"
    },
    {
      idScena: "10",
      who: "leo",
      speaker: "LEO",
      labelTopBar: "[LEO]",
      coloreHex: "#00FFCC",
      boxDestroOspite: "LEO",
      voce: "it-IT-PierluigiNeural",
      pitch: 0.95,
      rate: 1.06,
      testoRecitato: "A due passi dalla Valle dei Templi e dal cuore vivo di Favara, questa posizione offre una vivibilità fantastica per chi cerca radici e bellezza. — Immobiliare Giancani"
    }
  ];
}
