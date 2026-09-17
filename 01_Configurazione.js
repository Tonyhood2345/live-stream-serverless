// ═══════════════════════════════════════════════════════════════════════
// 📁 MODULO 01: CONFIGURAZIONE & UTILITY DI BASE
// Gestisce costanti globali, cache sicura, utility di inclusione e coda audio
// ═══════════════════════════════════════════════════════════════════════

const SHEET_ID = '1V1U67iYY7G4UyRw-D5QJgIcltH2QM34ifFfqEr9T7TE';
const DRIVE_MASTER_FOLDER_ID = '1ftayZvmtRjwIxZd_ctBSy0wuTH_3lijM';

/**
 * Recupera l'istanza dello Spreadsheet in modo sicuro con fallback
 */
function getSpreadsheetSicuro() {
  try {
    return SpreadsheetApp.openById(SHEET_ID);
  } catch(e) {
    try {
      return SpreadsheetApp.getActiveSpreadsheet();
    } catch(e2) {
      console.error("Errore getSpreadsheetSicuro:", e2);
      return null;
    }
  }
}

const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec';

/**
 * Esegue il fetch di un URL con cache integrata e gestione errori
 */
function fetchUrlSicuroConCache(url, options, cacheSeconds, fallbackObj) {
  try {
    var cache = CacheService.getScriptCache();
    url = (url || '').replace(/\{/g, '%7B').replace(/\}/g, '%7D');
    var cacheKey = 'FETCH_' + Utilities.base64Encode(url).substring(0, 50);
    var cached = cache.get(cacheKey);
    if (cached) {
      return {
        getResponseCode: function() { return 200; },
        getContentText: function() { return cached; }
      };
    }
    var res = UrlFetchApp.fetch(url, options || { muteHttpExceptions: true });
    if (res.getResponseCode() === 200) {
      cache.put(cacheKey, res.getContentText(), cacheSeconds || 60);
    }
    return res;
  } catch(e) {
    console.warn("fetchUrlSicuroConCache fallback:", e.toString());
    return {
      getResponseCode: function() { return 500; },
      getContentText: function() { return JSON.stringify(fallbackObj || {}); }
    };
  }
}

/**
 * Pulisce il testo da caratteri speciali per la sintesi vocale TTS
 */
function pulisciTestoPerTTSBackend(testo) {
  if (!testo) return "";
  var t = testo.toString()
    .replace(/\(.*?\)/g, '')
    .replace(/\[.*?\]/g, '')
    .replace(/[#*_\`~]/g, '')
    // Sostituzione rigorosa di mq -> metri quadri per pronuncia vocale naturale
    .replace(/(\d+)\s*(?:mq|m²|m2)\b/gi, '$1 metri quadri')
    .replace(/\b(?:mq|m²)\b/gi, 'metri quadri')
    .replace(/\bMQ\b/g, 'metri quadri')
    .replace(/Antonio\s*Giancani/gi, 'Immobiliare Giancani')
    .replace(/—\s*Immobiliare Giancani/gi, '— Immobiliare Giancani')
    .replace(/\s+/g, ' ')
    .trim();
  if (t.indexOf('Immobiliare Giancani') === -1) {
    t += ' — Immobiliare Giancani';
  }
  return t;
}

/**
 * Include file HTML in altri template Google Apps Script
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/**
 * Gestione configurazione Piper TTS / Azure TTS
 */
function getPiperTTSConfig() {
  try {
    var props = PropertiesService.getScriptProperties();
    return {
      success: true,
      endpoint: props.getProperty('PIPER_TTS_ENDPOINT') || 'http://localhost:5000',
      voceDaria: props.getProperty('PIPER_VOCE_DARIA') || 'it_IT-paola-medium',
      voceDario: props.getProperty('PIPER_VOCE_DARIO') || 'it_IT-riccardo-x_low',
      attivo: props.getProperty('PIPER_TTS_ATTIVO') === 'true'
    };
  } catch(e) {
    inviaAllertaErroreTelegram("01_Configurazione.js", "getPiperTTSConfig", e.toString());
    return { success: false, error: e.toString() };
  }
}

function salvaPiperTTSConfig(payload) {
  try {
    var props = PropertiesService.getScriptProperties();
    if (payload.endpoint) props.setProperty('PIPER_TTS_ENDPOINT', payload.endpoint);
    if (payload.voceDaria) props.setProperty('PIPER_VOCE_DARIA', payload.voceDaria);
    if (payload.voceDario) props.setProperty('PIPER_VOCE_DARIO', payload.voceDario);
    if (payload.attivo !== undefined) props.setProperty('PIPER_TTS_ATTIVO', payload.attivo.toString());
    return { success: true };
  } catch(e) {
    inviaAllertaErroreTelegram("01_Configurazione.js", "salvaPiperTTSConfig", e.toString());
    return { success: false, error: e.toString() };
  }
}

/**
 * 🏷️ Gestione Dimensione Scala Logo Agenzia in Diretta
 * Valore decimale (es. 0.75, 1.0, 1.35, 1.70)
 */
function getScalaLogoAgenzia() {
  try {
    var raw = PropertiesService.getScriptProperties().getProperty('SCALA_LOGO_AGENZIA');
    var val = parseFloat(raw);
    return (!isNaN(val) && val >= 0.5 && val <= 3.0) ? val : 1.0;
  } catch(e) {
    return 1.0;
  }
}

function salvaScalaLogoAgenzia(scala) {
  try {
    var val = parseFloat(scala) || 1.0;
    if (val < 0.5) val = 0.5;
    if (val > 3.0) val = 3.0;
    PropertiesService.getScriptProperties().setProperty('SCALA_LOGO_AGENZIA', val.toString());
    return { success: true, scala: val, message: 'Dimensione logo aggiornata a ' + Math.round(val * 100) + '% — Immobiliare Giancani' };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 🎨 GESTIONE STILE GRAFICO DIRETTA STREAMING
 * Valori supportati: 'modern_broadcast', 'editorial_minimal', 'tech_dark', 'comic_pop'
 */
function getStileGraficaDiretta() {
  try {
    var raw = PropertiesService.getScriptProperties().getProperty('STILE_GRAFICA_DIRETTA');
    var validi = ['modern_broadcast', 'editorial_minimal', 'tech_dark', 'comic_pop'];
    return (raw && validi.indexOf(raw) !== -1) ? raw : 'modern_broadcast';
  } catch(e) {
    return 'modern_broadcast';
  }
}

function salvaStileGraficaDiretta(stile) {
  try {
    var validi = ['modern_broadcast', 'editorial_minimal', 'tech_dark', 'comic_pop'];
    var st = String(stile || 'modern_broadcast').toLowerCase().trim();
    if (validi.indexOf(st) === -1) st = 'modern_broadcast';
    PropertiesService.getScriptProperties().setProperty('STILE_GRAFICA_DIRETTA', st);
    return { success: true, stile: st, message: 'Stile grafica diretta aggiornato a ' + st + ' — Immobiliare Giancani' };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}


/**
 * Gestione Coda Audio Attiva
 */
function getCodaAudioAttiva() {
  try {
    var raw = PropertiesService.getScriptProperties().getProperty('CODA_AUDIO_ATTIVA');
    return raw ? JSON.parse(raw) : [];
  } catch(e) {
    return [];
  }
}

function salvaCodaAudioAttiva(coda) {
  try {
    PropertiesService.getScriptProperties().setProperty('CODA_AUDIO_ATTIVA', JSON.stringify(coda || []));
  } catch(e) {
    console.error("salvaCodaAudioAttiva:", e);
  }
}

function aggiungiInCodaAudio(item) {
  try {
    var coda = getCodaAudioAttiva();
    coda.push(item);
    salvaCodaAudioAttiva(coda);
  } catch(e) {
    console.error("aggiungiInCodaAudio:", e);
  }
}

function popCodaAudio() {
  try {
    var coda = getCodaAudioAttiva();
    if (coda.length === 0) return null;
    var item = coda.shift();
    salvaCodaAudioAttiva(coda);
    return item;
  } catch(e) {
    return null;
  }
}

/**
 * Inizializzazione Foglio Configurazione Tempi Regia
 */
function inizializzaFoglioConfigurazioneTempi() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Configurazione_Tempi') : null;
    if (!sheet) {
      sheet = ss.insertSheet('Configurazione_Tempi');
      sheet.appendRow(['Parametro', 'Descrizione', 'Valore', 'Unita']);
      sheet.appendRow(['DURATA_FOTO', 'Permanenza singola foto', 12, 'Secondi']);
      sheet.appendRow(['DURATA_MUSICA', 'Durata rotazione brano', 3, 'Minuti']);
      sheet.appendRow(['FREQ_PUBBLICITA', 'Frequenza spot sponsor', 10, 'Minuti']);
      sheet.appendRow(['FREQ_YOUTUBE', 'Frequenza video YouTube', 20, 'Minuti']);
      sheet.appendRow(['FREQ_METEO', 'Frequenza bollettino meteo', 15, 'Minuti']);
      sheet.appendRow(['FREQ_NOTIZIE', 'Frequenza flash notizie', 10, 'Minuti']);
      sheet.appendRow(['FREQ_TEATRINO', 'Frequenza sketch comico', 5, 'Minuti']);
    }
  } catch(e) {
    console.error("inizializzaFoglioConfigurazioneTempi:", e);
  }
}

function getConfigurazioneTempiRegia() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Configurazione_Tempi') : null;
    if (!sheet) {
      inizializzaFoglioConfigurazioneTempi();
      sheet = ss.getSheetByName('Configurazione_Tempi');
    }
    var res = {
      durataFotoSec: 12,
      rotazioneMusicaMin: 3,
      freqPubblicitaMin: 10,
      freqYouTubeMin: 20,
      freqMeteoMin: 15,
      freqNotizieMin: 10,
      freqTeatrinoMin: 5
    };
    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var i = 1; i < data.length; i++) {
        var p = String(data[i][0] || '').trim().toUpperCase();
        var v = parseFloat(data[i][2]);
        if (!isNaN(v) && v > 0) {
          if (p === 'DURATA_FOTO') res.durataFotoSec = v;
          if (p === 'DURATA_MUSICA') res.rotazioneMusicaMin = v;
          if (p === 'FREQ_PUBBLICITA') res.freqPubblicitaMin = v;
          if (p === 'FREQ_YOUTUBE') res.freqYouTubeMin = v;
          if (p === 'FREQ_METEO') res.freqMeteoMin = v;
          if (p === 'FREQ_NOTIZIE') res.freqNotizieMin = v;
          if (p === 'FREQ_TEATRINO') res.freqTeatrinoMin = v;
        }
      }
    }
    return { success: true, tempi: res };
  } catch(e) {
    inviaAllertaErroreTelegram("01_Configurazione.js", "getConfigurazioneTempiRegia", e.toString());
    return { success: false, error: e.toString() };
  }
}

function salvaConfigurazioneTempiRegia(payload) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Configurazione_Tempi') : null;
    if (!sheet) {
      inizializzaFoglioConfigurazioneTempi();
      sheet = ss.getSheetByName('Configurazione_Tempi');
    }
    if (sheet && payload) {
      var data = sheet.getDataRange().getValues();
      var paramMap = {
        'DURATA_FOTO': payload.durataFotoSec,
        'DURATA_MUSICA': payload.rotazioneMusicaMin,
        'FREQ_PUBBLICITA': payload.freqPubblicitaMin,
        'FREQ_YOUTUBE': payload.freqYouTubeMin,
        'FREQ_METEO': payload.freqMeteoMin,
        'FREQ_NOTIZIE': payload.freqNotizieMin,
        'FREQ_TEATRINO': payload.freqTeatrinoMin
      };
      for (var i = 1; i < data.length; i++) {
        var p = String(data[i][0] || '').trim().toUpperCase();
        if (paramMap[p] !== undefined && paramMap[p] !== null) {
          sheet.getRange(i + 1, 3).setValue(paramMap[p]);
        }
      }
      SpreadsheetApp.flush();
    }
    return { success: true, messaggio: "Tempi di regia salvati con successo nel foglio!" };
  } catch(e) {
    inviaAllertaErroreTelegram("01_Configurazione.js", "salvaConfigurazioneTempiRegia", e.toString());
    return { success: false, error: e.toString() };
  }
}

/**
 * 🎭 CONTROLLO MODALITÀ AVATAR IN DIRETTA (CON_AVATAR / VUOTO)
 */
function impostaModalitaAvatar(mode) {
  try {
    var cleanMode = (mode === 'VUOTO') ? 'VUOTO' : 'CON_AVATAR';
    PropertiesService.getScriptProperties().setProperty('MODALITA_AVATAR', cleanMode);
    
    var msg = (cleanMode === 'CON_AVATAR')
      ? "✅ Avatar DarIA & DarIO attivati in onda!"
      : "⚪ Avatar rimossi: trasmissione solo immobile a tutto schermo.";
      
    return { success: true, mode: cleanMode, message: msg };
  } catch(e) {
    inviaAllertaErroreTelegram("01_Configurazione.js", "impostaModalitaAvatar", e.toString());
    return { success: false, error: e.toString() };
  }
}

function getModalitaAvatar() {
  try {
    var mode = PropertiesService.getScriptProperties().getProperty('MODALITA_AVATAR') || 'CON_AVATAR';
    return { success: true, mode: mode };
  } catch(e) {
    return { success: false, mode: 'CON_AVATAR' };
  }
}

// 🚀 Allineamento Progetto Completo 13 Moduli — Immobiliare Giancani
