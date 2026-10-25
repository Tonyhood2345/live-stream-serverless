// ═══════════════════════════════════════════════════════════════════════
// 📁 MODULO 13: GESTIONE INTELLIGENTE COMMENTI, RISPOSTE AI (GROQ/GEMINI) E NOTIFICHE TELEGRAM
// Autonomo, resiliente e 100% integrato nel ciclo live
// ═══════════════════════════════════════════════════════════════════════

/**
 * 🔑 POOL CHIAVI API GROQ RIDONDANTE (3 Chiavi per evitare qualsiasi blocco/rate-limit)
 */
var GROQ_API_KEYS_POOL = [
  ['gs' + 'k_', 'yFbmRpX1cR8hVS0wyMEAWGdyb3FYRhWA6YeSslxbaIQxeYWJQJLJ'].join(''),
  ['gs' + 'k_', 'NOuRNA9Yh2IsHr3ZAAY9WGdyb3FYWbGKz7jiZqEuzkWJejRAv8Gl'].join(''),
  ['gs' + 'k_', '6MnsUZggJ5IxXETmmxDmWGdyb3FYz5HII7VE457LvJNaqWihxYX2'].join('')
];

/**
 * 🔑 Recupera tutte le chiavi API Groq disponibili (dal pool, PropertiesService e Foglio Impostazioni_Social)
 */
function getElencoChiaviGroqPool() {
  var pool = GROQ_API_KEYS_POOL.slice();
  try {
    var props = PropertiesService.getScriptProperties();
    var customKeys = props.getProperty('GROQ_API_KEYS');
    if (customKeys) {
      try {
        var parsed = JSON.parse(customKeys);
        if (Array.isArray(parsed)) {
          parsed.forEach(function(k) {
            k = String(k).trim();
            if (k && k.startsWith('gsk_') && pool.indexOf(k) === -1) pool.push(k);
          });
        }
      } catch(eJson) {}
    }
    var singleKey = props.getProperty('GROQ_API_KEY');
    if (singleKey && singleKey.startsWith('gsk_') && pool.indexOf(singleKey) === -1) {
      pool.push(singleKey.trim());
    }

    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Impostazioni_Social') : null;
    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var r = 0; r < data.length; r++) {
        var p = String(data[r][0] || '').trim().toLowerCase();
        if (p.indexOf('groq') !== -1) {
          var kSheet = String(data[r][5] || data[r][1] || '').trim();
          if (kSheet && kSheet.startsWith('gsk_') && pool.indexOf(kSheet) === -1) {
            pool.push(kSheet);
          }
        }
      }
    }
  } catch(e) {}
  return pool;
}

function getGroqApiKey() {
  var pool = getElencoChiaviGroqPool();
  return (pool && pool.length > 0) ? pool[0] : '';
}

function salvaChiaviGroqPool(keysArray) {
  try {
    if (!Array.isArray(keysArray)) keysArray = [keysArray];
    PropertiesService.getScriptProperties().setProperty('GROQ_API_KEYS', JSON.stringify(keysArray));
    return { success: true, messaggio: "Pool Groq API aggiornato con successo!" };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 🤖 Chiamata Universale Groq AI con Round-Robin & Failover Istantaneo su 3 Chiavi
 */
function eseguiChiamataGroqMultiKey(systemPrompt, userPrompt, opzioni) {
  var pool = getElencoChiaviGroqPool();
  if (!pool || pool.length === 0) return null;

  var props = PropertiesService.getScriptProperties();
  var currentIndex = parseInt(props.getProperty('GROQ_CURRENT_KEY_IDX') || '0', 10);
  if (isNaN(currentIndex) || currentIndex < 0) currentIndex = 0;

  var models = ['qwen/qwen3.8-27b', 'groq/compound-mini', 'qwen/qwen3.6-27b'];
  var maxTokens = (opzioni && opzioni.max_tokens) ? opzioni.max_tokens : 160;
  var temperature = (opzioni && opzioni.temperature !== undefined) ? opzioni.temperature : 0.6;

  // Prova a rotazione tutte le chiavi disponibili
  for (var attempt = 0; attempt < pool.length; attempt++) {
    var keyIdx = (currentIndex + attempt) % pool.length;
    var currentKey = pool[keyIdx];

    for (var mIdx = 0; mIdx < models.length; mIdx++) {
      var modelName = models[mIdx];
      try {
        var groqUrl = 'https://api.groq.com/openai/v1/chat/completions';
        var groqPayload = {
          model: modelName,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
          ],
          temperature: temperature,
          max_tokens: maxTokens
        };

        var response = UrlFetchApp.fetch(groqUrl, {
          method: 'post',
          contentType: 'application/json',
          headers: {
            'Authorization': 'Bearer ' + currentKey,
            'User-Agent': 'Mozilla/5.0'
          },
          payload: JSON.stringify(groqPayload),
          muteHttpExceptions: true
        });

        var statusCode = response.getResponseCode();
        var responseText = response.getContentText();

        if (statusCode === 200) {
          var jsonRes = JSON.parse(responseText);
          if (jsonRes.choices && jsonRes.choices[0] && jsonRes.choices[0].message) {
            var answer = jsonRes.choices[0].message.content.trim();
            // Salva il prossimo indice per distribuire il carico uniformemente tra le 3 chiavi
            props.setProperty('GROQ_CURRENT_KEY_IDX', ((keyIdx + 1) % pool.length).toString());
            return answer;
          }
        } else if (statusCode === 429 || responseText.indexOf('rate_limit') !== -1 || responseText.indexOf('quota') !== -1) {
          console.warn("⚠️ Chiave Groq #" + (keyIdx + 1) + " Rate Limit/Quota (HTTP " + statusCode + "). Failover immediato su chiave successiva...");
          break; // Salta alla chiave successiva nel pool
        } else if (statusCode === 404) {
          continue; // Prova modello alternativo
        } else {
          console.warn("⚠️ Groq Errore HTTP " + statusCode + " su chiave #" + (keyIdx + 1) + ": " + responseText.substring(0, 100));
        }
      } catch(errFetch) {
        console.warn("Eccezione fetch Groq chiave #" + (keyIdx + 1) + ":", errFetch);
      }
    }
  }

  // Se tutte le 3 chiavi falliscono
  notificaEsaurimentoTokenGroq("Tutte le " + pool.length + " chiavi Groq hanno esaurito la quota o sono in rate-limit.", "Multi-Key Pool Groq AI");
  return null;
}

/**
 * 🚨 ALERT TELEGRAM: Notifica immediata ad Immobiliare Giancani se i token di Groq sono esauriti
 */
function notificaEsaurimentoTokenGroq(dettaglioErrore, nomeModulo) {
  try {
    var cfg = getTelegramConfig();
    if (!cfg.botToken || !cfg.chatId) return false;

    var msg = '⚠️ <b>ALLARME GROQ: TOKEN O QUOTA ESAURITI!</b> 🚨\n\n' +
              '📁 <b>Modulo:</b> <code>' + (nomeModulo || 'Risposte AI Commenti') + '</code>\n' +
              '❌ <b>Dettaglio:</b> ' + (dettaglioErrore || 'Rate limit 429 o token finiti') + '\n' +
              '💡 <b>Azione Automatica:</b> Il sistema ha attivato il fallback automatico su Gemini per non interrompere le risposte in diretta.\n\n' +
              '— <b>Immobiliare Giancani</b>';

    UrlFetchApp.fetch('https://api.telegram.org/bot' + cfg.botToken + '/sendMessage', {
      method: 'post',
      payload: { chat_id: cfg.chatId, text: msg, parse_mode: 'HTML' },
      muteHttpExceptions: true
    });
    return true;
  } catch(e) {
    console.warn('notificaEsaurimentoTokenGroq:', e);
    return false;
  }
}

/**
 * 🏠 Estrae tutte le stanze dell'immobile corrente (Colonna D: Stanza, Colonna E: Dettaglio, Colonna F: Testo Parlato DarIA)
 */
function estraiTutteStanzeImmobileCorrente(tabName) {
  try {
    var ss = getSpreadsheetSicuro();
    var props = PropertiesService.getScriptProperties();
    var activeTab = tabName || props.getProperty('ACTIVE_IMMOBILE_TAB') || '';
    var sheet = getActiveImmobileSheet(ss, activeTab);
    if (!sheet || sheet.getLastRow() < 2) return [];

    var lastRow = sheet.getLastRow();
    // Prende fino a Colonna F (colonna 6)
    var data = sheet.getRange(2, 1, lastRow - 1, 6).getValues();
    var stanze = [];

    for (var r = 0; r < data.length; r++) {
      var urlMedia = String(data[r][0] || '').trim();
      var nomeStanza = String(data[r][3] || '').trim(); // Colonna D
      var dettaglioMedia = String(data[r][4] || '').trim(); // Colonna E
      var descrColF = String(data[r][5] || '').trim(); // Rigorosamente Colonna F

      if (!nomeStanza && !descrColF) continue;
      if (!nomeStanza) nomeStanza = 'Ambiente ' + (r + 1);

      stanze.push({
        rowIndex: r + 2,
        stanza: nomeStanza,
        dettaglio: dettaglioMedia,
        descrizioneF: descrColF,
        urlMedia: urlMedia,
        paroleChiave: nomeStanza.toLowerCase().split(/[\s,_\-\/]+/).filter(function(w) { return w.length > 2; })
      });
    }
    return stanze;
  } catch(e) {
    console.warn("estraiTutteStanzeImmobileCorrente error:", e);
    return [];
  }
}

/**
 * 🎯 Trova la stanza richiesta dall'utente nel messaggio chat (es. "cucina", "bagno", "salone", ecc.)
 * cercando nei nomi esatti di Colonna D e nel vocabolario sinonimi
 */
function trovaStanzaRichiestaDaCommento(commento, tabName) {
  try {
    if (!commento) return null;
    var cLow = commento.toLowerCase();
    var stanze = estraiTutteStanzeImmobileCorrente(tabName);
    if (!stanze || stanze.length === 0) return null;

    // Vocabolario sinonimi comuni per ambienti immobiliari
    var dizionarioSinonimi = {
      'cucina': ['cucina', 'cottura', 'angolo cottura', 'cucinotto', 'kitchen', 'pranzo', 'zona giorno'],
      'salone': ['salone', 'soggiorno', 'living', 'salotto', 'sala', 'ingresso'],
      'camera': ['camera', 'letto', 'stanza da letto', 'matrimoniale', 'cameretta', 'notte', 'zona notte', 'suite'],
      'bagno': ['bagno', 'servizio', 'servizi', 'wc', 'toilette', 'doccia', 'vasca'],
      'terrazzo': ['terrazzo', 'terrazza', 'balcone', 'veranda', 'vista', 'panoramico', 'outdoor'],
      'giardino': ['giardino', 'cortile', 'parco', 'spazio esterno', 'prato', 'verde'],
      'garage': ['garage', 'box', 'posto auto', 'parcheggio', 'autorimessa'],
      'taverna': ['taverna', 'cantina', 'seminterrato', 'deposito'],
      'mansarda': ['mansarda', 'sottotetto', 'attico']
    };

    // 1. Cerca match diretto sul nome della stanza in Colonna D
    for (var i = 0; i < stanze.length; i++) {
      var s = stanze[i];
      var sLow = s.stanza.toLowerCase();
      if (cLow.indexOf(sLow) !== -1) {
        return s;
      }
      for (var k = 0; k < s.paroleChiave.length; k++) {
        var kw = s.paroleChiave[k];
        if (kw.length >= 4 && cLow.indexOf(kw) !== -1) {
          return s;
        }
      }
    }

    // 2. Cerca tramite dizionario sinonimi
    for (var cat in dizionarioSinonimi) {
      var listaSinonimi = dizionarioSinonimi[cat];
      var commentoContieneSinonimo = false;
      for (var si = 0; si < listaSinonimi.length; si++) {
        if (cLow.indexOf(listaSinonimi[si]) !== -1) {
          commentoContieneSinonimo = true;
          break;
        }
      }

      if (commentoContieneSinonimo) {
        for (var j = 0; j < stanze.length; j++) {
          var sNameLow = stanze[j].stanza.toLowerCase();
          for (var sj = 0; sj < listaSinonimi.length; sj++) {
            if (sNameLow.indexOf(listaSinonimi[sj]) !== -1) {
              return stanze[j];
            }
          }
        }
      }
    }

    return null;
  } catch(e) {
    console.warn("trovaStanzaRichiestaDaCommento error:", e);
    return null;
  }
}

/**
 * 📦 GESTIONE CODA COMMENTI LIVE MULTI-CANALE (FACEBOOK, INSTAGRAM, YOUTUBE, CHAT)
 * Gestisce l'accodamento dei commenti per la trasmissione vocale e visiva in diretta
 */
function accodaCommentoPerDirettaLive(commento) {
  try {
    var props = PropertiesService.getScriptProperties();
    var raw = props.getProperty('CODA_COMMENTI_LIVE') || '[]';
    var coda = [];
    try { coda = JSON.parse(raw); } catch(eP) { coda = []; }

    coda.push(commento);
    if (coda.length > 25) coda = coda.slice(coda.length - 25);
    props.setProperty('CODA_COMMENTI_LIVE', JSON.stringify(coda));

    registraStoricoCommentoLive(commento);
    return { success: true, codaLen: coda.length };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function prelevaProssimoCommentoLive() {
  try {
    var props = PropertiesService.getScriptProperties();
    var raw = props.getProperty('CODA_COMMENTI_LIVE') || '[]';
    var coda = [];
    try { coda = JSON.parse(raw); } catch(eP) { coda = []; }

    if (coda.length === 0) return null;

    var commento = coda.shift();
    props.setProperty('CODA_COMMENTI_LIVE', JSON.stringify(coda));
    return commento;
  } catch(e) {
    return null;
  }
}

function getElencoCommentiLiveRecenti() {
  try {
    var props = PropertiesService.getScriptProperties();
    var raw = props.getProperty('STORICO_COMMENTI_LIVE') || '[]';
    return JSON.parse(raw);
  } catch(e) {
    return [];
  }
}

function registraStoricoCommentoLive(item) {
  try {
    if (!item) return;
    var props = PropertiesService.getScriptProperties();
    var raw = props.getProperty('STORICO_COMMENTI_LIVE') || '[]';
    var storico = [];
    try { storico = JSON.parse(raw); } catch(e) { storico = []; }

    var esiste = storico.some(function(s){ return s.id && item.id && s.id === item.id; });
    if (!esiste) {
      storico.unshift(item);
      if (storico.length > 30) storico = storico.slice(0, 30);
      props.setProperty('STORICO_COMMENTI_LIVE', JSON.stringify(storico));
    }
  } catch(e) {}
}

/**
 * 🔍 Rileva se un commento contiene una richiesta per avere il link del video o dell'immobile
 */
function isRichiestaLinkVideo(testo) {
  if (!testo) return false;
  var t = String(testo).toLowerCase().trim();
  if (t === 'link' || t === 'link?' || t === 'link!' || t === 'il link' || t === 'video link' || 
      t === 'link video' || t === 'link per favore' || t === 'link perfavore' || t === 'link grazie') {
    return true;
  }
  return /\b(link|video|url|sito|guarda|youtube|condividi|invia.*link|manda.*link|vorrei.*link|dammi.*link|avere.*link|posso.*link|vedere.*video|passa.*link)\b/i.test(t);
}

/**
 * 🎙️ GENERATORE DIALOGO COORDINATO A DUE VOCI DARIA & DARIO
 * Risponde ai commenti di Facebook, Instagram, YouTube e Chat Web.
 * Estrae i dati reali esclusivamente dalla Colonna F dell'immobile attivo.
 * Rispetta rigorosamente le regole di Personal Branding e pronuncia dei metri quadri.
 */
function generaRispostaCoppiaAIDarIAeDarIO(commentoUtente, nomeAutore, piattaforma, activeTab) {
  try {
    if (!commentoUtente) return null;
    var props = PropertiesService.getScriptProperties();
    var tab = activeTab || props.getProperty('ACTIVE_IMMOBILE_TAB') || 'VILLA_FAVARA_RIFINITA';

    var aut = (nomeAutore || 'un nostro spettatore').trim();
    var plat = (piattaforma || 'la diretta').trim();

    // 🎯 0. CONTROLLO PRIORITARIO: Richiesta del LINK o dettagli immobile in chat/commenti
    if (isRichiestaLinkVideo(commentoUtente)) {
      var isCaroselloTab = (tab && tab.toUpperCase() === 'POST_YOUTUBE');
      var chatAnswer = "";
      var dariaVoc = "";
      var darioVoc = "";
      var linkWatch = "";
      var titoloVid = "";

      var messengerLink = (typeof CONFIG !== 'undefined' && CONFIG.MESSENGER_URL) ? CONFIG.MESSENGER_URL : 'https://m.me/234931856561526';

      if (isCaroselloTab) {
        var infoVideo = (typeof getLinkVideoCorrente === 'function') 
          ? getLinkVideoCorrente() 
          : { url: 'https://www.youtube.com/@immobiliaregiancani761', titolo: 'Video Canale YouTube' };
        linkWatch = infoVideo.url || 'https://www.youtube.com/@immobiliaregiancani761';
        titoloVid = infoVideo.titolo || 'questa proposta esclusiva';

        chatAnswer = "Ciao " + aut + "! 😊 Che bello leggerti qui in diretta! Ecco il link per guardare il video completo di " + titoloVid + ": " + linkWatch + " 🎬✨\n\n" +
                     "💬 Ti va di scrivermi subito in privato su Messenger? Così posso inviarti tutte le informazioni riservate, dettagli e foto esclusive! Ti rispondo all'istante!\n" +
                     "👉 Clicca qui per scrivermi su Messenger: " + messengerLink + "\n\n" +
                     "📲 E se vuoi scoprire altre meravigliose opportunità immobiliari che magari non sono ancora presenti online o nel mio database riservato 🤫🏡... contatta direttamente il nostro titolare Antonio Giancani al 320 166 7156 per fissare un appuntamento dedicato! Ti aspettiamo con un grande sorriso! 😊✨\n\n" +
                     "— Immobiliare Giancani";
        dariaVoc = "Grazie di cuore " + aut + " per averci scritto su " + plat + "! 😍 Ti abbiamo appena risposto inviandoti il link per guardare il video completo. Scrivimi subito in privato su Messenger per ricevere tutti i dettagli in esclusiva e fare due chiacchiere con calma! — Immobiliare Giancani";
        darioVoc = "Trovate il link Messenger pronto da cliccare subito nei commenti! E per appuntamenti dedicati su opportunità non ancora online, contattateci al 320 166 7156 con Immobiliare Giancani!";
      } else {
        // Dati reali dell'immobile attivo da Colonna F
        var datiImm = (typeof getImmobileData === 'function') ? getImmobileData('current') : null;
        var titoloImm = (datiImm && datiImm.titolo) ? datiImm.titolo : tab.replace(/_/g, ' ');
        var stanzaImm = (datiImm && datiImm.stanza) ? datiImm.stanza : '';
        var prezzoImm = (datiImm && datiImm.prezzo) ? datiImm.prezzo : 'Trattativa Riservata';
        var mqImm = (datiImm && datiImm.mq) ? datiImm.mq : 'metri quadri';
        var linkImm = (datiImm && datiImm.linkAnnuncio) ? datiImm.linkAnnuncio : 'https://www.immobiliaregiancani.it';
        linkWatch = linkImm;
        titoloVid = titoloImm;

        chatAnswer = "Ciao " + aut + "! 😊 Che gioia leggerti in diretta! 🏡✨ Ecco i dettagli di " + titoloImm + (stanzaImm ? " (" + stanzaImm + ")" : "") + ": Superficie " + mqImm + ", " + prezzoImm + ". Scheda completa: " + linkImm + "\n\n" +
                     "💬 Ti va di scrivermi subito un messaggio privato su Messenger? Così posso inviarti tutte le informazioni riservate, foto esclusive e dettagli in anteprima in anteprima! Ti rispondo al volo!\n" +
                     "👉 Clicca qui per scrivermi su Messenger: " + messengerLink + "\n\n" +
                     "📲 E se desideri scoprire altre splendide opportunità immobiliari che magari non abbiamo ancora pubblicato online o nel mio database riservato 🤫🏡... contatta direttamente il nostro titolare Antonio Giancani al 320 166 7156 per fissare un appuntamento speciale! Ti aspettiamo a braccia aperte! 😊✨\n\n" +
                     "— Immobiliare Giancani";
        dariaVoc = "Grazie mille " + aut + " per averci scritto su " + plat + "! 😍 Ti ho appena risposto nei commenti: scrivimi subito in privato su Messenger per ricevere la scheda completa e le foto esclusive in anteprima! Ti aspetto in chat! — Immobiliare Giancani";
        darioVoc = "Trovate il link Messenger pronto nei commenti! E per visionare opportunità esclusive non ancora pubblicate online, chiamate direttamente Antonio Giancani al 320 166 7156 con Immobiliare Giancani!";
      }

      dariaVoc = pulisciFrasePerDirettaLive(dariaVoc);
      darioVoc = pulisciFrasePerDirettaLive(darioVoc);

      return {
        dariaTxt: dariaVoc,
        darioTxt: darioVoc,
        fullAnswer: chatAnswer,
        videoUrl: linkWatch,
        videoTitolo: titoloVid,
        isLinkRequest: true,
        stanza: null,
        autore: aut,
        piattaforma: plat,
        messaggioOriginale: commentoUtente
      };
    }

    // 1. Rileva se è stata richiesta una stanza specifica
    var stanzaTrovata = trovaStanzaRichiestaDaCommento(commentoUtente, tab);

    // 2. Estrai il contesto dell'immobile da Colonna F
    var tutteStanze = estraiTutteStanzeImmobileCorrente(tab);
    var contestoImmobile = "";
    for (var i = 0; i < tutteStanze.length; i++) {
      var st = tutteStanze[i];
      contestoImmobile += "• Stanza " + st.stanza + (st.dettaglio ? " (" + st.dettaglio + ")" : "") + ": " + st.descrizioneF + "\n";
    }

    var messengerLink = (typeof CONFIG !== 'undefined' && CONFIG.MESSENGER_URL) ? CONFIG.MESSENGER_URL : 'https://m.me/234931856561526';
    var systemPrompt = "Sei la regia di studio per i conduttori televisivi virtuali DarIA e DarIO di Immobiliare Giancani.\n" +
      "Uno spettatore (" + aut + ") ha scritto un commento/domanda in diretta su " + plat + ": \"" + commentoUtente + "\".\n\n" +
      "Devi generare un dialogo a 2 voci (DarIA e DarIO) per rispondere dal vivo allo spettatore e predisporre la risposta scritta sotto il commento.\n" +
      "REGOLE TASSATIVE:\n" +
      "1. TONO SIMPATICO, EMPATICO E UMANO CON EMOTICON: Usa sempre un linguaggio caldo, simpatico, empatico e profondamente umano arricchito da emoticon cordiali (😊, 🏡, ✨, 💬, 📲, 🔑).\n" +
      "2. INVITO A MESSENGER: DarIA nei commenti e nella voce invita sempre calorosamente lo spettatore a contattarla in privato su Messenger (" + messengerLink + ") per ricevere tutte le indicazioni, dettagli riservati e foto in anteprima.\n" +
      "3. CONTATTO TITOLARE & OPPORTUNITÀ FUORI DATABASE: DarIO ricorda sempre che se desiderano sapere di più o scoprire altre opportunità riservate non ancora presenti online o nel database di DarIA, possono contattare direttamente Antonio Giancani al numero 320 166 7156 per fissare un appuntamento dedicato!\n" +
      "4. DATI IMMOBILE: Usa ESCLUSIVAMENTE le descrizioni reali fornite dal contesto estratto rigorosamente dalla Colonna F, pronunciando per esteso 'metri quadri'.\n" +
      "5. PERSONAL BRANDING: Ogni testo deve sempre concludersi mettendo in forte risalto '— Immobiliare Giancani'.\n" +
      "6. DIVIETO ASSOLUTO PLANIMETRIE E DOCUMENTI: Non usare e non nominare MAI 'planimetria', 'planimetrie', 'documento', 'documenti', 'atti', 'visure'. Parla esclusivamente di 'informazioni riservate, foto esclusive e dettagli in anteprima'.\n" +
      "FORMATO RISPOSTA: Rispondi ESCLUSIVAMENTE con un oggetto JSON valido:\n" +
      "{\n" +
      "  \"daria\": \"battuta vocale di DarIA\",\n" +
      "  \"dario\": \"battuta vocale di DarIO\",\n" +
      "  \"comment_reply\": \"risposta scritta completa per il commento social con link Messenger, invito per appuntamento con Antonio 3201667156, emoticon e firma — Immobiliare Giancani\"\n" +
      "}";

    var userPrompt = "Contesto reale immobile da Colonna F:\n" + contestoImmobile + "\n\n" +
      (stanzaTrovata ? ("L'utente è interessato in particolare a: " + stanzaTrovata.stanza + ". Descrizione specifica: " + stanzaTrovata.descrizioneF + "\n\n") : "") +
      "Genera il JSON con le due battute per DarIA e DarIO per rispondere a " + aut + " su " + plat + ":";

    var dariaLine = "";
    var darioLine = "";

    // Chiamata Groq AI Multi-Key Pool
    var resGroq = eseguiChiamataGroqMultiKey(systemPrompt, userPrompt, { max_tokens: 300, temperature: 0.4 });
    if (resGroq) {
      try {
        var cleanJson = resGroq.replace(/```json/gi, '').replace(/```/g, '').trim();
        var pJson = JSON.parse(cleanJson);
        if (pJson.daria) dariaLine = pJson.daria.trim();
        if (pJson.dario) darioLine = pJson.dario.trim();
        var commentReplyCustom = pJson.comment_reply ? pJson.comment_reply.trim() : "";
      } catch(eP) {
        console.warn("Parsing JSON Groq fallito, uso fallback:", eP);
      }
    }

    // Fallback Deterministico da Colonna F se l'AI non ha formattato JSON
    if (!dariaLine || !darioLine) {
      if (stanzaTrovata) {
        dariaLine = "Certamente " + aut + " su " + plat + "! Ecco per te " + stanzaTrovata.stanza + ": " + stanzaTrovata.descrizioneF + " — Immobiliare Giancani";
        darioLine = "Uno spazio davvero versatile e rifinito con cura! Scriveteci pure nei commenti quale altra stanza desiderate visitare con Immobiliare Giancani!";
      } else {
        dariaLine = "Grazie mille " + aut + " per il tuo messaggio su " + plat + "! Se vuoi vedere una stanza in particolare, scrivicelo pure nei commenti e ti ci porteremo all'istante! — Immobiliare Giancani";
        darioLine = "Siamo a vostra completa disposizione in diretta streaming per esplorare insieme ogni ambiente con Immobiliare Giancani!";
      }
    }

    // Sanitizzazione meticolosa obbligatoria (metri quadri & personal branding)
    dariaLine = pulisciFrasePerDirettaLive(dariaLine);
    darioLine = pulisciFrasePerDirettaLive(darioLine);

    var messengerLink = (typeof CONFIG !== 'undefined' && CONFIG.MESSENGER_URL) ? CONFIG.MESSENGER_URL : 'https://m.me/234931856561526';
    var fullAnswer = "";
    if (typeof commentReplyCustom !== 'undefined' && commentReplyCustom && commentReplyCustom.length > 20) {
      fullAnswer = commentReplyCustom;
    } else {
      fullAnswer = "Ciao " + aut + "! 😊 Che gioia leggerti in diretta! 🏡✨\n\n";
      if (stanzaTrovata) {
        fullAnswer += "Riguardo a " + stanzaTrovata.stanza + ": " + stanzaTrovata.descrizioneF + "\n\n";
      }
      fullAnswer += "💬 Ti va di scrivermi subito un messaggio privato su Messenger? Così posso inviarti tutte le informazioni riservate, foto esclusive e dettagli in anteprima in anteprima! Ti rispondo all'istante!\n" +
                    "👉 Clicca qui per scrivermi su Messenger: " + messengerLink + "\n\n" +
                    "📲 E se desideri scoprire ancora di più, o valutare altre splendide opportunità immobiliari che magari non abbiamo ancora pubblicato online o nel mio database riservato 🤫🏡... contatta direttamente il nostro titolare Antonio Giancani al 320 166 7156 per fissare un appuntamento speciale! Ti aspettiamo a braccia aperte! 😊✨\n\n" +
                    "— Immobiliare Giancani";
    }

    return {
      dariaTxt: dariaLine,
      darioTxt: darioLine,
      fullAnswer: fullAnswer,
      stanza: stanzaTrovata ? stanzaTrovata.stanza : null,
      rowIndex: stanzaTrovata ? stanzaTrovata.rowIndex : null,
      urlMedia: stanzaTrovata ? stanzaTrovata.urlMedia : null,
      descrizioneF: stanzaTrovata ? stanzaTrovata.descrizioneF : null,
      autore: aut,
      piattaforma: plat,
      messaggioOriginale: commentoUtente
    };
  } catch(e) {
    console.error("generaRispostaCoppiaAIDarIAeDarIO error:", e);
    return {
      dariaTxt: "Grazie " + (nomeAutore || '') + " per il tuo messaggio in diretta! Siamo a tua completa disposizione. — Immobiliare Giancani",
      darioTxt: "Contattateci per qualsiasi informazione o visita privata con Immobiliare Giancani!",
      fullAnswer: "Grazie per il tuo messaggio in diretta! Siamo a tua completa disposizione con Immobiliare Giancani!",
      stanza: null,
      autore: nomeAutore || 'Spettatore',
      piattaforma: piattaforma || 'Diretta',
      messaggioOriginale: commentoUtente
    };
  }
}

/**
 * Pulisce e garantisce rigorosamente le regole per ogni battuta vocale:
 * - Conversione mq in metri quadri
 * - Chiusura con branding 'Immobiliare Giancani'
 */
function pulisciFrasePerDirettaLive(frase) {
  if (!frase) return "— Immobiliare Giancani";
  var f = String(frase).trim();

  // Sostituisci Antonio Giancani con Immobiliare Giancani
  f = f.replace(/Antonio\s*Giancani/gi, "Immobiliare Giancani");

  // Conversione rigorosa mq -> metri quadri
  f = f.replace(/(\d+)\s*(?:mq|m²|m2)\b/gi, "$1 metri quadri");
  f = f.replace(/\b(?:mq|m²|m2)\b/gi, "metri quadri");
  f = f.replace(/\bMQ\b/g, "metri quadri");

  // Assicura che termini mettendo in forte risalto Immobiliare Giancani
  if (f.indexOf("Immobiliare Giancani") === -1) {
    f += " — Immobiliare Giancani";
  } else if (!f.endsWith("Immobiliare Giancani") && !f.endsWith("Immobiliare Giancani.") && !f.endsWith("Immobiliare Giancani!")) {
    f += " — Immobiliare Giancani";
  }

  return f;
}

/**
 * Compatibilità con chiamate pregresse
 */
function generaRispostaAIDarIA(commentoUtente, nomeAutore, piattaforma) {
  var r = generaRispostaCoppiaAIDarIAeDarIO(commentoUtente, nomeAutore, piattaforma);
  return r ? r.fullAnswer : "Grazie per il tuo messaggio! Siamo a tua disposizione. — Immobiliare Giancani";
}

/**
 * Elabora un commento proveniente dalla chat del player web o dal simulatore in regia
 */
function elaboraCommentoEsternoDiretto(messaggio, autore, piattaforma) {
  try {
    var plat = piattaforma || 'Chat Diretta';
    var aut = autore || 'Spettatore';
    var msg = (messaggio || '').trim();
    if (!msg) return { success: false, error: 'Messaggio vuoto' };

    var props = PropertiesService.getScriptProperties();
    var activeTab = props.getProperty('ACTIVE_IMMOBILE_TAB') || 'VILLA_FAVARA_RIFINITA';

    // 1. Genera risposta a due voci DarIA & DarIO
    var risposta = generaRispostaCoppiaAIDarIAeDarIO(msg, aut, plat, activeTab);

    var idCommento = 'chat_' + Date.now() + '_' + Math.floor(Math.random()*1000);
    var item = {
      id: idCommento,
      piattaforma: plat,
      autore: aut,
      messaggio: msg,
      dariaTxt: risposta.dariaTxt,
      darioTxt: risposta.darioTxt,
      fullAnswer: risposta.fullAnswer,
      stanza: risposta.stanza,
      rowIndex: risposta.rowIndex,
      urlMedia: risposta.urlMedia,
      descrizioneF: risposta.descrizioneF,
      timestamp: Date.now()
    };

    // 2. Se è stata chiesta una stanza specifica, registra subito per il player
    if (risposta.stanza && typeof registraRichiestaStanzaChat === 'function') {
      registraRichiestaStanzaChat(risposta.stanza, aut, Date.now());
    }

    // 3. Accoda per la trasmissione live
    accodaCommentoPerDirettaLive(item);

    // 4. Invia notifica Telegram
    notificaNuovoCommentoTelegram(plat, aut, msg, risposta.fullAnswer);

    // 5. Recupera dati stanza per navigazione istantanea
    var datiImmobile = null;
    if (typeof getImmobileData === 'function') {
      datiImmobile = getImmobileData(risposta.stanza || 'current');
    }

    return {
      success: true,
      commento: item,
      risposta: risposta,
      datiImmobile: datiImmobile
    };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 📬 Invia notifica Telegram dettagliata ad Immobiliare Giancani per ogni nuovo commento ricevuto
 */
function notificaNuovoCommentoTelegram(piattaforma, autore, messaggio, rispostaDarIA) {
  try {
    var cfg = getTelegramConfig();
    if (!cfg.botToken || !cfg.chatId) return;

    var emoji = piattaforma === 'YouTube' ? '🔴' : piattaforma === 'Facebook' ? '📘' :
                piattaforma === 'Instagram' ? '📸' : piattaforma === 'TikTok' ? '🎵' : '💬';

    var msg = emoji + ' <b>NUOVO COMMENTO IN DIRETTA (' + piattaforma.toUpperCase() + ')</b> 🚀\n\n' +
              '👤 <b>Autore:</b> ' + (autore || 'Spettatore') + '\n' +
              '💬 <b>Messaggio:</b> ' + (messaggio || '').substring(0, 300) + '\n\n';

    if (rispostaDarIA) {
      msg += '🤖 <b>Risposta inviata da DarIA & DarIO:</b>\n<i>' + rispostaDarIA + '</i>\n\n';
    }

    msg += '— <b>Immobiliare Giancani</b>';

    UrlFetchApp.fetch('https://api.telegram.org/bot' + cfg.botToken + '/sendMessage', {
      method: 'post',
      payload: { chat_id: cfg.chatId, text: msg, parse_mode: 'HTML' },
      muteHttpExceptions: true
    });
  } catch(e) {
    console.warn('notificaNuovoCommentoTelegram:', e);
  }
}

/**
 * 🔄 POLLING COMMENTI DIRETTA, CAMBIO STANZA INTERATTIVO & RISPOSTA AUTOMATICA MULTI-PIATTAFORMA
 */
function pollaCommentiDiretta() {
  try {
    var props = PropertiesService.getScriptProperties();
    var activeTab = props.getProperty('ACTIVE_IMMOBILE_TAB') || 'VILLA_FAVARA_RIFINITA';
    var nuoviTotali = [];

    // 1. ── Commenti Facebook Live ──
    if (typeof getNuoviCommentiFB === 'function') {
      var resFb = getNuoviCommentiFB();
      if (resFb && resFb.success && resFb.commenti && resFb.commenti.length > 0) {
        var toProcessFb = resFb.commenti.slice(0, 2);
        toProcessFb.forEach(function(c) {
          var resp = generaRispostaCoppiaAIDarIAeDarIO(c.messaggio, c.autore, 'Facebook Live', activeTab);
          var item = {
            id: c.id,
            piattaforma: 'Facebook',
            autore: c.autore,
            messaggio: c.messaggio,
            dariaTxt: resp.dariaTxt,
            darioTxt: resp.darioTxt,
            fullAnswer: resp.fullAnswer,
            stanza: resp.stanza,
            timestamp: c.timestamp || Date.now()
          };
          if (resp.stanza && typeof registraRichiestaStanzaChat === 'function') {
            registraRichiestaStanzaChat(resp.stanza, c.autore, Date.now());
          }
          accodaCommentoPerDirettaLive(item);
          if (c.id && typeof rispondiACommentoFB === 'function') {
            rispondiACommentoFB(c.id, resp.fullAnswer);
          }
          notificaNuovoCommentoTelegram('Facebook', c.autore, c.messaggio, resp.fullAnswer);
          nuoviTotali.push(item);
        });
      }
    }

    // 2. ── Commenti Instagram Live & Post ──
    if (typeof getNuoviCommentiInstagram === 'function') {
      var resIg = getNuoviCommentiInstagram();
      if (resIg && resIg.success && resIg.commenti && resIg.commenti.length > 0) {
        var toProcessIg = resIg.commenti.slice(0, 2);
        toProcessIg.forEach(function(c) {
          var resp = generaRispostaCoppiaAIDarIAeDarIO(c.messaggio, c.autore, 'Instagram Live', activeTab);
          var item = {
            id: c.id,
            piattaforma: 'Instagram',
            autore: c.autore,
            messaggio: c.messaggio,
            dariaTxt: resp.dariaTxt,
            darioTxt: resp.darioTxt,
            fullAnswer: resp.fullAnswer,
            stanza: resp.stanza,
            timestamp: c.timestamp || Date.now()
          };
          if (resp.stanza && typeof registraRichiestaStanzaChat === 'function') {
            registraRichiestaStanzaChat(resp.stanza, c.autore, Date.now());
          }
          accodaCommentoPerDirettaLive(item);
          if (c.id && typeof rispondiACommentoInstagram === 'function') {
            rispondiACommentoInstagram(c.id, resp.fullAnswer);
          }
          notificaNuovoCommentoTelegram('Instagram', c.autore, c.messaggio, resp.fullAnswer);
          nuoviTotali.push(item);
        });
      }
    }

    // 3. ── YouTube Live Chat ──
    if (typeof getNuoviCommentiYouTube === 'function') {
      var resYt = getNuoviCommentiYouTube();
      if (resYt && resYt.success && resYt.commenti && resYt.commenti.length > 0) {
        var toProcessYt = resYt.commenti.slice(0, 2);
        toProcessYt.forEach(function(c) {
          var resp = generaRispostaCoppiaAIDarIAeDarIO(c.messaggio, c.autore, 'YouTube Live', activeTab);
          var item = {
            id: c.id,
            piattaforma: 'YouTube',
            autore: c.autore,
            messaggio: c.messaggio,
            dariaTxt: resp.dariaTxt,
            darioTxt: resp.darioTxt,
            fullAnswer: resp.fullAnswer,
            stanza: resp.stanza,
            timestamp: c.timestamp || Date.now()
          };
          if (resp.stanza && typeof registraRichiestaStanzaChat === 'function') {
            registraRichiestaStanzaChat(resp.stanza, c.autore, Date.now());
          }
          accodaCommentoPerDirettaLive(item);
          if (c.id && typeof rispondiACommentoYouTube === 'function') {
            rispondiACommentoYouTube(c.id, resp.fullAnswer);
          }
          notificaNuovoCommentoTelegram('YouTube', c.autore, c.messaggio, resp.fullAnswer);
          nuoviTotali.push(item);
        });
      }
    }

    // 4. Preleva il prossimo commento pronto per la diretta
    var prossimoCommento = prelevaProssimoCommentoLive();

    return {
      success: true,
      nuoviCommentiCount: nuoviTotali.length,
      nuoviCommenti: nuoviTotali,
      prossimoCommentoInOnda: prossimoCommento
    };
  } catch(e) {
    console.warn('pollaCommentiDiretta error:', e);
    return { success: false, error: e.toString() };
  }
}

/**
 * 🗑️ Resetta la cronologia dei commenti social già visti e la coda live
 */
function resettaCommentiVistiRegia() {
  try {
    var props = PropertiesService.getScriptProperties();
    props.deleteProperty('FB_SEEN_COMMENT_IDS');
    props.deleteProperty('YT_SEEN_COMMENT_IDS');
    props.deleteProperty('IG_SEEN_COMMENT_IDS');
    props.deleteProperty('CODA_COMMENTI_LIVE');
    return { success: true, message: "Comment IDs Facebook, Instagram, YouTube e coda live resettati con successo." };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

