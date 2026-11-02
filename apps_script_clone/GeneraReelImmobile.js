/**
 * ═════════════════════════════════════════════════════════════════════════════
 * 🎬 IMMOBILIARE GIANCANI — GENERATORE VIDEO REEL IMMOBILI (APPS SCRIPT INTEGRATION)
 * ═════════════════════════════════════════════════════════════════════════════
 * 
 * Flusso:
 * 1. Aggiunge menu interattivo su Google Sheets ("🎬 Video Reel Giancani").
 * 2. Legge la riga selezionata (o specificata) prelevando il testo da Colonna F (indice 6).
 * 3. Invia la richiesta a GitHub Actions (workflow genera_reel_immobile.yml) per
 *    eseguire il montaggio video (FFmpeg) con card grafica scura semitrasparente a sinistra,
 *    musica sincronizzata ed invio email automatico con allegato MP4 e copy per i social.
 * 4. Funziona sia con trigger manuale da foglio, sia programmaticamente da altre pipeline.
 * ═════════════════════════════════════════════════════════════════════════════
 */

// ── 1. MENU PERSONALIZZATO IN GOOGLE SHEETS ──────────────────────────────────
function onOpen() {
  try {
    SpreadsheetApp.getUi()
      .createMenu('🎬 Reel & Storie Giancani')
      .addItem('🚀 Genera Reel da Riga Immobile (Colonna F)', 'generaReelDaRigaSelezionata')
      .addItem('🔢 Genera Reel Inserendo Numero Riga...', 'generaReelPromptRiga')
      .addSeparator()
      .addItem('📱 Genera Storia 9:16 da Video Drive (Frasi Prestigio)', 'generaStoriaDaVideoDriveUI')
      .addItem('📜 Sincronizza Foglio Frasi Prestigio (FRASI_PRESTIGIO_STORIE)', 'sincronizzaFrasiPrestigioUI')
      .addToUi();
  } catch (e) {
    Logger.log('Menu non visualizzabile in questo contesto: ' + e);
  }
}

// ── 2. TRIGGER DA RIGA CORRENTE ──────────────────────────────────────────────
function generaReelDaRigaSelezionata() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var riga = sheet.getActiveCell().getRow();

  if (riga < 2) {
    SpreadsheetApp.getUi().alert('⚠️ Attenzione', 'Seleziona una riga con i dati dell\'immobile (riga 2 o successiva).', SpreadsheetApp.getUi().ButtonSet.OK);
    return;
  }

  generaReelPerRiga(riga);
}

// ── 3. TRIGGER CON PROMPT NUMERO RIGA ────────────────────────────────────────
function generaReelPromptRiga() {
  var ui = SpreadsheetApp.getUi();
  var risposta = ui.prompt('🎬 Generazione Reel Immobile', 'Inserisci il numero della riga del foglio da elaborare:', ui.ButtonSet.OK_CANCEL);

  if (risposta.getSelectedButton() == ui.Button.OK) {
    var num = parseInt(risposta.getResponseText().trim(), 10);
    if (isNaN(num) || num < 2) {
      ui.alert('Numero riga non valido.');
      return;
    }
    generaReelPerRiga(num);
  }
}

// ── 4. ELABORAZIONE RIGA & INVIO A GITHUB ACTIONS ────────────────────────────
function generaReelPerRiga(numeroRiga) {
  var sheet = SpreadsheetApp.getActiveSheet();
  
  // Colonna F è la colonna 6 (1-based)
  var cellaF = sheet.getRange(numeroRiga, 6).getValue();
  var testoColonnaF = String(cellaF || '').trim();

  if (!testoColonnaF) {
    var ui = SpreadsheetApp.getUi();
    ui.alert('⚠️ Colonna F Vuota', 'La Colonna F alla riga ' + numeroRiga + ' non contiene alcuna descrizione o dato per l\'immobile.', ui.ButtonSet.OK);
    return;
  }

  // Cerca se nella riga ci sono link video (es. Colonna L/12 o Colonna T/20)
  var videoDriveLink = '';
  try {
    var colVideo = sheet.getRange(numeroRiga, 12).getValue();
    if (colVideo && String(colVideo).includes('drive.google.com')) {
      videoDriveLink = String(colVideo);
    }
  } catch (e) {
    // ignora se non presente
  }

  var emailDestinatario = (typeof CONFIG !== 'undefined' && CONFIG.PRIMARY_EMAIL) ? CONFIG.PRIMARY_EMAIL : 'giancaniimmobiliare@gmail.com';

  SpreadsheetApp.getActiveSpreadsheet().toast('🚀 Invio richiesta elaborazione Reel per riga ' + numeroRiga + '...', 'Immobiliare Giancani', 5);

  var esito = dispatchGitHubWorkflowReel({
    riga_foglio: String(numeroRiga),
    email_destinatario: emailDestinatario,
    video_drive_id: videoDriveLink,
    musica_drive_id: '',
    forza_testo_colonna_f: testoColonnaF
  });

  if (esito.success) {
    SpreadsheetApp.getUi().alert(
      '🎬 Generazione Reel Avviata!',
      'La richiesta di generazione del video Reel per la riga ' + numeroRiga + ' è stata inviata a GitHub Actions con successo.\n\n' +
      '• Riceverai il file MP4 montato e il copy pronto direttamente via email su:\n' + emailDestinatario + '\n\n' +
      '— Immobiliare Giancani',
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  } else {
    SpreadsheetApp.getUi().alert(
      '❌ Errore Invio',
      'Si è verificato un errore durante l\'invio a GitHub Actions:\n' + esito.error + '\n\n' +
      'Verifica che il token GitHub sia configurato correttamente.',
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  }
}

// ── 5. DISPATCH VERSO GITHUB REST API ────────────────────────────────────────
function dispatchGitHubWorkflowReel(params) {
  var ghUser = (typeof CONFIG !== 'undefined' && CONFIG.GITHUB_USER) ? CONFIG.GITHUB_USER : 'Tonyhood2345';
  var ghRepo = 'live-stream-serverless';
  var ghToken = (typeof CONFIG !== 'undefined' && CONFIG.GITHUB_TOKEN) ? CONFIG.GITHUB_TOKEN : '';

  if (!ghToken) {
    return { success: false, error: 'Token GitHub non trovato in CONFIG.GITHUB_TOKEN' };
  }

  var url = 'https://api.github.com/repos/' + ghUser + '/' + ghRepo + '/actions/workflows/genera_reel_immobile.yml/dispatches';
  var payload = {
    ref: 'main',
    inputs: {
      riga_foglio: params.riga_foglio || '2',
      email_destinatario: params.email_destinatario || 'giancaniimmobiliare@gmail.com',
      video_drive_id: params.video_drive_id || '',
      musica_drive_id: params.musica_drive_id || '',
      forza_testo_colonna_f: params.forza_testo_colonna_f || ''
    }
  };

  var options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': 'token ' + ghToken,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'Giancani-AppsScript-Reels'
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    var response = UrlFetchApp.fetch(url, options);
    var code = response.getResponseCode();

    if (code === 204 || code === 200 || code === 201) {
      Logger.log('✅ Workflow genera_reel_immobile.yml avviato con successo!');
      return { success: true };
    } else {
      // Fallback a repository_dispatch
      var urlRepoDisp = 'https://api.github.com/repos/' + ghUser + '/' + ghRepo + '/dispatches';
      var payloadRepo = {
        event_type: 'genera_reel_immobile',
        client_payload: params
      };
      var resRepo = UrlFetchApp.fetch(urlRepoDisp, {
        method: 'post',
        contentType: 'application/json',
        headers: options.headers,
        payload: JSON.stringify(payloadRepo),
        muteHttpExceptions: true
      });
      if (resRepo.getResponseCode() === 204 || resRepo.getResponseCode() === 200) {
        return { success: true };
      }
      return { success: false, error: 'HTTP ' + code + ': ' + response.getContentText() };
    }
  } catch (err) {
    Logger.log('❌ Eccezione dispatch GitHub: ' + err);
    return { success: false, error: String(err) };
  }
}

// ── 6. INVIO EMAIL NATIVO DA APPS SCRIPT (CON ALLEGATO) ──────────────────────
function inviaEmailConVideoAllegato(destinatario, titoloImmobile, testoColonnaF, videoFileId) {
  var videoFile = DriveApp.getFileById(videoFileId);
  var videoBlob = videoFile.getBlob();

  var oggetto = "Video pronto + Dati Immobile - " + titoloImmobile;
  var corpo = "Ciao Antonio,\n\n" +
              "Ecco il video Reel generato con successo e pronto per la pubblicazione!\n\n" +
              "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
              "📋 COPY PRONTO DA INCOLLARE SUI SOCIAL (Facebook, Instagram, TikTok):\n" +
              "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +
              testoColonnaF + "\n\n" +
              "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
              "— Immobiliare Giancani";

  MailApp.sendEmail({
    to: destinatario,
    subject: oggetto,
    body: corpo,
    attachments: [videoBlob]
  });

  Logger.log('✅ Email inviata con successo via MailApp a ' + destinatario);
}



// ── 7. MENU & FUNZIONI STORIE 9:16 DA VIDEO DRIVE (FRASI PRESTIGIO) ──────────

function generaStoriaDaVideoDriveUI() {
  var ui = SpreadsheetApp.getUi();
  var risposta = ui.prompt(
    '🎬 Generazione Storia 9:16 (Video Drive)',
    'Inserisci l\'ID o URL Google Drive del video senza testo (oppure lascia vuoto per usare il video più recente caricato in Drive):',
    ui.ButtonSet.OK_CANCEL
  );

  if (risposta.getSelectedButton() == ui.Button.OK) {
    var videoInput = risposta.getResponseText().trim();
    var emailDest = (typeof CONFIG !== 'undefined' && CONFIG.PRIMARY_EMAIL) ? CONFIG.PRIMARY_EMAIL : 'giancaniimmobiliare@gmail.com';

    SpreadsheetApp.getActiveSpreadsheet().toast('🚀 Invio generazione Storia 9:16 a GitHub Actions...', 'Immobiliare Giancani', 5);

    var res = dispatchGitHubWorkflowStoria({
      video_drive: videoInput,
      frase_id: '',
      custom_phrase: '',
      musica_drive: '',
      email_destinatario: emailDest
    });

    if (res.success) {
      ui.alert(
        '🎬 Generazione Storia Avviata!',
        'La storia 9:16 con Logo Giancani e Frase di Prestigio (Colonna F) è in fase di montaggio.\n\n' +
        'Riceverai il file MP4 e il copy pronto direttamente via email su:\n' + emailDest + '\n\n' +
        '— Immobiliare Giancani',
        ui.ButtonSet.OK
      );
    } else {
      ui.alert('❌ Errore Invio', 'Si è verificato un errore:\n' + res.error, ui.ButtonSet.OK);
    }
  }
}

function dispatchGitHubWorkflowStoria(params) {
  var ghUser = (typeof CONFIG !== 'undefined' && CONFIG.GITHUB_USER) ? CONFIG.GITHUB_USER : 'Tonyhood2345';
  var ghRepo = 'live-stream-serverless';
  var ghToken = (typeof CONFIG !== 'undefined' && CONFIG.GITHUB_TOKEN) ? CONFIG.GITHUB_TOKEN : '';

  if (!ghToken) {
    return { success: false, error: 'Token GitHub non trovato in CONFIG.GITHUB_TOKEN' };
  }

  var url = 'https://api.github.com/repos/' + ghUser + '/' + ghRepo + '/actions/workflows/genera_storia_drive.yml/dispatches';
  var payload = {
    ref: 'main',
    inputs: {
      video_drive: params.video_drive || '',
      frase_id: params.frase_id || '',
      custom_phrase: params.custom_phrase || '',
      musica_drive: params.musica_drive || '',
      email_destinatario: params.email_destinatario || 'giancaniimmobiliare@gmail.com'
    }
  };

  var options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': 'token ' + ghToken,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'Giancani-AppsScript-Storie'
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    var response = UrlFetchApp.fetch(url, options);
    var code = response.getResponseCode();
    if (code === 204 || code === 200 || code === 201) {
      return { success: true };
    } else {
      return { success: false, error: 'HTTP ' + code + ': ' + response.getContentText() };
    }
  } catch (e) {
    return { success: false, error: String(e) };
  }
}

function sincronizzaFrasiPrestigioUI() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = 'FRASI_PRESTIGIO_STORIE';
  var sheet = ss.getSheetByName(sheetName);
  var isNew = false;
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    isNew = true;
  }

  if (isNew || sheet.getLastRow() < 2) {
    sheet.clear();
    sheet.appendRow([
      'ID',
      'Categoria',
      'Titolo_Gancio',
      'Frase_Slogan',
      'Focus_Prestigio',
      'Colonna_F_Testo_Elaborazione',
      'Stato'
    ]);
    sheet.getRange('A1:G1').setFontWeight('bold').setBackground('#c9a35e').setFontColor('#ffffff');

    var frasiIniziali = [
      ['1', 'Prestigio & Valore', "L'Arte dell'Abitare", 'Il vero lusso è lo spazio la luce e la quiete in cui scegli di vivere.', 'Esclusività e Silenzio', "Il vero lusso non è ciò che mostri, ma lo spazio, la luce e la quiete in cui scegli di vivere. La tua dimora ideale inizia da qui. — Immobiliare Giancani", 'Attivo'],
      ['2', 'Prestigio & Valore', 'Oltre le Semplici Mura', 'Ogni casa ha un anima ma solo chi sa guardare oltre sa valorizzarne il pregio.', 'Consulenza Sartoriale', "Ogni casa ha un'anima, ma solo chi sa guardare oltre sa valorizzarne il reale pregio. Esperienza e riservatezza al tuo servizio. — Immobiliare Giancani", 'Attivo'],
      ['3', 'Curiosità & Emozione', 'La Sensazione di Casa', 'Ti sei mai chiesto perché certe case ti fanno sentire a casa al primo istante?', 'Intrigo Emozionale', "Ti sei mai chiesto perché certe case ti fanno sentire a casa fin dal primo istante in cui varchi la soglia? Scopri la magia dei dettagli. — Immobiliare Giancani", 'Attivo'],
      ['4', 'Curiosità & Emozione', 'Vivere o Abitare?', 'C è una differenza profonda tra avere un tetto e avere un luogo che ti rispecchia.', 'Distinzione e Gusto', "C'è una differenza profonda tra un semplice immobile e un luogo progettato per rispecchiare chi sei veramente. Fai spazio al tuo stile. — Immobiliare Giancani", 'Attivo'],
      ['5', 'Stimolo & Ambizione', 'Il Valore del Tuo Tempo', 'La dimora perfetta è quella che regala tempo serenità e bellezza ogni giorno.', 'Comfort e Benessere', "La dimora perfetta è quella che ti restituisce tempo prezioso, serenità e armonia ogni giorno. Scegli di vivere meglio. — Immobiliare Giancani", 'Attivo'],
      ['6', 'Stimolo & Ambizione', 'Non Rimandare il Futuro', 'Il momento migliore per scegliere la qualità della tua vita è adesso.', 'Decisione e Chiarezza', "Il momento migliore per scegliere la qualità della tua vita è adesso. Esplora le nostre proposte selezionate con cura. — Immobiliare Giancani", 'Attivo'],
      ['7', 'Sicurezza & Garanzia', 'Tranquillità Assoluta', 'La serenità di acquistare senza alcuna sorpresa non ha prezzo.', 'Garanzia e Tutela', "La serenità di acquistare senza alcuna sorpresa non ha prezzo. Verifichiamo ogni dettaglio prima, durante e dopo il rogito. — Immobiliare Giancani", 'Attivo'],
      ['8', 'Prestigio & Valore', 'Stile Senza Tempo', 'L eleganza non è farsi notare ma farsi ricordare.', 'Eleganza Architettonica', "L'eleganza autentica non è farsi notare, ma farsi ricordare. Trova la dimora che esprime al meglio la tua personalità. — Immobiliare Giancani", 'Attivo'],
      ['9', 'Curiosità & Emozione', 'Il Tuo Nuovo Capitolo', 'E se la casa che hai sempre sognato fosse molto più vicina di quanto immagini?', 'Opportunità Riservata', "E se la casa che hai sempre sognato fosse molto più vicina di quanto immagini? Il tuo prossimo capitolo comincia da qui. — Immobiliare Giancani", 'Attivo'],
      ['10', 'Stimolo & Ambizione', 'Spazi da Vivere', 'Immagina di svegliarti ogni giorno dove libertà e vista si fondono.', 'Lifestyle Esclusivo', "Immagina di svegliarti ogni giorno in un ambiente dove libertà, vista e comfort si fondono. Trasforma la tua immaginazione in realtà. — Immobiliare Giancani", 'Attivo']
    ];

    for (var i = 0; i < frasiIniziali.length; i++) {
      sheet.appendRow(frasiIniziali[i]);
    }
  }

  SpreadsheetApp.getUi().alert(
    '✅ Foglio Frasi Sincronizzato',
    'La scheda "FRASI_PRESTIGIO_STORIE" è attiva e configurata con la Colonna F per le Storie dei Video Drive.\n\n— Immobiliare Giancani',
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}
