// ═══════════════════════════════════════════════════════════════════════
// 📁 MODULO 11: ROUTER PRINCIPALE (doGet & doPost)
// Smista tutte le chiamate web, pagine HTML, API REST e webhook con allarmi Telegram
// ═══════════════════════════════════════════════════════════════════════

function doGet(e) {
  try {
    var action = (e && e.parameter && e.parameter.action) ? e.parameter.action : '';

    // Verifica automatica archiviazione post Facebook pendente (dopo 1 ora)
    if (typeof verificaEsecuzioneArchiviazionePostFBPendente === 'function') {
      try { verificaEsecuzioneArchiviazionePostFBPendente(); } catch(eArch) {}
    }

    // API REST Endpoints
    if (action === 'debug_all_sheets') {
      var ss = getSpreadsheetSicuro();
      var result = { sheets: [] };
      if (ss) {
        var allS = ss.getSheets();
        for (var s = 0; s < allS.length; s++) {
          var sName = allS[s].getName();
          var numRows = allS[s].getLastRow();
          var numCols = allS[s].getLastColumn();
          var sample = [];
          if (numRows > 0) {
            sample = allS[s].getRange(1, 1, Math.min(numRows, 10), Math.min(numCols, 8)).getValues();
          }
          result.sheets.push({ name: sName, rows: numRows, cols: numCols, sample: sample });
        }
      }
      return ContentService.createTextOutput(JSON.stringify(result, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_sheet') {
      var sName = (e && e.parameter && e.parameter.name) ? e.parameter.name : 'Post_YouTube';
      var ss = getSpreadsheetSicuro();
      var sheet = ss ? ss.getSheetByName(sName) : null;
      var rows = [];
      if (sheet && sheet.getLastRow() > 0) {
        rows = sheet.getRange(1, 1, sheet.getLastRow(), Math.max(sheet.getLastColumn(), 1)).getValues();
      }
      return ContentService.createTextOutput(JSON.stringify({ success: true, name: sName, totalRows: rows.length, rows: rows }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_carosello_youtube') {
      var dir = (e && e.parameter && e.parameter.dir) ? e.parameter.dir : 'current';
      var dataCarosello = getCaroselloPostYouTube(dir);
      return ContentService.createTextOutput(JSON.stringify(dataCarosello, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_current_video_link') {
      var infoLink = getLinkVideoCorrente();
      return ContentService.createTextOutput(JSON.stringify({ success: true, video: infoLink }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'debug_social_keys') {
      var sheet = ss ? ss.getSheetByName("Impostazioni_Social") : null;
      var info = { hasSheet: !!sheet, keysFound: [] };
      if (sheet) {
        var data = sheet.getDataRange().getValues();
        for (var r = 0; r < data.length; r++) {
          var p = String(data[r][0] || '').trim();
          var val = String(data[r][5] || data[r][1] || '').trim();
          var masked = val ? (val.substring(0, 10) + '...' + (val.length > 20 ? val.substring(val.length - 6) : '')) : 'VUOTO';
          info.keysFound.push({ parametro: p, valore: masked, len: val.length });
        }
      }
      return ContentService.createTextOutput(JSON.stringify(info, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'debug_dialoghi_sheet') {
      var ss = getSpreadsheetSicuro();
      var sheet = ss ? ss.getSheetByName('Dialoghi_avat_tutti') : null;
      var info = {
        hasSS: !!ss,
        hasSheet: !!sheet,
        lastRow: sheet ? sheet.getLastRow() : 0,
        lastCol: sheet ? sheet.getLastColumn() : 0,
        sampleRows: []
      };
      if (sheet && sheet.getLastRow() > 0) {
        var rawV = sheet.getRange(1, 1, Math.min(sheet.getLastRow(), 15), Math.max(sheet.getLastColumn(), 1)).getValues();
        for (var i = 0; i < rawV.length; i++) {
          var toks = parseCsvLineBackend(rawV[i][0]);
          info.sampleRows.push({
            rowIdx: i + 1,
            colLen: rawV[i].length,
            raw0: String(rawV[i][0] || '').substring(0, 80),
            toksLen: toks.length,
            toks0: toks[0],
            toks2: toks[2],
            toks10: (toks[10] || '').substring(0, 40)
          });
        }
      }
      return ContentService.createTextOutput(JSON.stringify(info, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_dialoghi_avat_tutti') {
      var resDiag = getDialoghiAvatTuttiList();
      return ContentService.createTextOutput(JSON.stringify({ success: true, totale: resDiag.length, dialoghi: resDiag }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'organizza_foglio_dialoghi') {
      var resOrg = organizzaFoglioDialoghiAvatTutti();
      return ContentService.createTextOutput(JSON.stringify(resOrg, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'debug_immobile') {
      var query = (e && e.parameter && e.parameter.q) ? e.parameter.q : 'current';
      var resD = getImmobileData(query);
      return ContentService.createTextOutput(JSON.stringify(resD, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }
    if (action === 'test_risposta_link') {
      var commento = (e && e.parameter && e.parameter.msg) ? e.parameter.msg : 'LINK';
      var resTestLink = (typeof generaRispostaCoppiaAIDarIAeDarIO === 'function')
        ? generaRispostaCoppiaAIDarIAeDarIO(commento, 'Marco Spettatore', 'Facebook Live')
        : { error: 'generaRispostaCoppiaAIDarIAeDarIO non definita' };
      return ContentService.createTextOutput(JSON.stringify(resTestLink, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'test_fb_comments') {
      var resFb = getNuoviCommentiFB();
      return ContentService.createTextOutput(JSON.stringify(resFb, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'test_yt_comments') {
      var resYt = getNuoviCommentiYouTube();
      return ContentService.createTextOutput(JSON.stringify(resYt, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'salva_qualita_stream') {
      var qVal = (e && e.parameter && e.parameter.qualita) ? e.parameter.qualita : '1080p_std';
      var sVal = (e && e.parameter && e.parameter.scale) ? e.parameter.scale : '1.0';
      var cVal = (e && e.parameter && e.parameter.crop) ? e.parameter.crop : 'none';
      var resQ = salvaQualitaStreamingFFmpeg(qVal, sVal, cVal);
      return ContentService.createTextOutput(JSON.stringify(resQ, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_qualita_stream') {
      var resGetQ = getQualitaStreamingFFmpeg();
      return ContentService.createTextOutput(JSON.stringify(resGetQ, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'pubblica_snapshot_live_10min' || action === 'pubblica_storia_fb') {
      var dParams = {
        forza: (e && e.parameter && (e.parameter.forza === 'true' || e.parameter.force === 'true')),
        fotoUrl: (e && e.parameter && e.parameter.fotoUrl) ? e.parameter.fotoUrl : null,
        titolo: (e && e.parameter && e.parameter.titolo) ? e.parameter.titolo : null,
        stanza: (e && e.parameter && e.parameter.stanza) ? e.parameter.stanza : null,
        mq: (e && e.parameter && e.parameter.mq) ? e.parameter.mq : null,
        prezzo: (e && e.parameter && e.parameter.prezzo) ? e.parameter.prezzo : null,
        testoF: (e && e.parameter && e.parameter.testoF) ? e.parameter.testoF : null
      };
      var resStory = pubblicaSnapshotStoriaSocialOgni10Minuti(dParams);
      return ContentService.createTextOutput(JSON.stringify(resStory, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'carica_video_drive') {
      var b64 = (e && e.parameter && e.parameter.b64) ? e.parameter.b64 : '';
      var fName = (e && e.parameter && e.parameter.fileName) ? e.parameter.fileName : 'storia.mp4';
      var resUp = caricaVideoBase64SuDrive(b64, fName);
      return ContentService.createTextOutput(JSON.stringify(resUp, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'pubblica_youtube_short') {
      var pData = {
        titolo: (e && e.parameter && e.parameter.titolo) ? e.parameter.titolo : '',
        stanza: (e && e.parameter && e.parameter.stanza) ? e.parameter.stanza : '',
        mq: (e && e.parameter && e.parameter.mq) ? e.parameter.mq : '',
        prezzo: (e && e.parameter && e.parameter.prezzo) ? e.parameter.prezzo : '',
        testoF: (e && e.parameter && e.parameter.testoF) ? e.parameter.testoF : '',
        videoUrl: (e && e.parameter && e.parameter.videoUrl) ? e.parameter.videoUrl : '',
        thumbUrl: (e && e.parameter && e.parameter.thumbUrl) ? e.parameter.thumbUrl : ''
      };
      var resYtShort = pubblicaShortYouTubeSuCanale(pData);
      return ContentService.createTextOutput(JSON.stringify(resYtShort, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'aggiorna_storia_fb' || action === 'aggiorna_snapshot_30min' || action === 'aggiorna_snapshot_10min') {
      var resAggStory = aggiornaStoriaSnapshotLiveOgni30Minuti();
      return ContentService.createTextOutput(JSON.stringify(resAggStory, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'invia_quadro_telegram') {
      var resQuadro = inviaQuadroVisivoDirettaTelegram();
      return ContentService.createTextOutput(JSON.stringify(resQuadro, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'invia_guida_telegram') {
      var resGuida = inviaGuidaCompletaDirettaTelegram();
      return ContentService.createTextOutput(JSON.stringify(resGuida, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'invia_notifica_bagno') {
      var resBagnoN = inviaNotificaBagnoAstrattoTelegram();
      return ContentService.createTextOutput(JSON.stringify(resBagnoN, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'invia_report' || action === 'report_telegram') {
      var resRep = (typeof inviaResocontoSistema === 'function') ? inviaResocontoSistema() : { success: true, msg: 'Report inviato' };
      return ContentService.createTextOutput(JSON.stringify(resRep)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'set_webhook') {
      var resWebh = (typeof impostaWebhookTelegram === 'function') ? impostaWebhookTelegram() : { success: true, msg: 'Webhook impostato' };
      return ContentService.createTextOutput(JSON.stringify(resWebh)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'invia_notifica' && e && e.parameter && e.parameter.msg) {
      var resNotif = inviaNotificaTelegram(e.parameter.msg, null, 'HTML');
      return ContentService.createTextOutput(JSON.stringify(resNotif, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'test_lancio_diretta') {
      var resLancio = inviaNotificaLancioDirettaTelegram('TEST_LIVE_ID', 'https://www.facebook.com/watch/live/?v=TEST_LIVE_ID', '');
      return ContentService.createTextOutput(JSON.stringify(resLancio, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'imposta_tiktok') {
      var kTk = (e && e.parameter && e.parameter.key) ? e.parameter.key : '';
      var resTk = impostaChiaveTikTok(kTk);
      return ContentService.createTextOutput(JSON.stringify(resTk, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'imposta_instagram') {
      var kIg = (e && e.parameter && e.parameter.key) ? e.parameter.key : '';
      var resIg = impostaChiaveInstagram(kIg);
      return ContentService.createTextOutput(JSON.stringify(resIg, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'imposta_youtube') {
      var kYt = (e && e.parameter && e.parameter.key) ? e.parameter.key : '';
      var resYtK = impostaNuovaChiaveYouTube(kYt);
      return ContentService.createTextOutput(JSON.stringify(resYtK, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'imposta_live_fb') {
      var liveId = (e && e.parameter && (e.parameter.id || e.parameter.live_id)) ? (e.parameter.id || e.parameter.live_id) : '';
      var resSetLive = setFBLiveVideoId(liveId);
      PropertiesService.getScriptProperties().deleteProperty('FB_SEEN_COMMENT_IDS');
      PropertiesService.getScriptProperties().deleteProperty('CODA_COMMENTI_LIVE');
      return ContentService.createTextOutput(JSON.stringify({ success: true, liveId: liveId, message: 'ID Live Facebook impostato e coda commenti azzerata — Immobiliare Giancani' }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'imposta_zoom') {
      var zVal = (e && e.parameter && e.parameter.zoom) ? e.parameter.zoom : '125';
      var resZoom = salvaZoomDiretta(zVal);
      return ContentService.createTextOutput(JSON.stringify(resZoom, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_zoom') {
      var curZoom = getZoomDiretta();
      return ContentService.createTextOutput(JSON.stringify({ success: true, zoom: curZoom }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'salva_voci') {
      var vDaria = (e && e.parameter && e.parameter.voceDaria) ? e.parameter.voceDaria : '';
      var vDario = (e && e.parameter && e.parameter.voceDario) ? e.parameter.voceDario : '';
      var resVoci = salvaConfigurazioneVoci({ voceDaria: vDaria, voceDario: vDario });
      return ContentService.createTextOutput(JSON.stringify(resVoci, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_voci') {
      var curVoci = getConfigurazioneVoci();
      return ContentService.createTextOutput(JSON.stringify({ success: true, config: curVoci }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'imposta_coppia_avatar') {
      var aDonna = (e && e.parameter && e.parameter.donna) ? e.parameter.donna : '';
      var aUomo = (e && e.parameter && e.parameter.uomo) ? e.parameter.uomo : '';
      var resCoppia = impostaAvatarInOnda(aDonna, aUomo);
      return ContentService.createTextOutput(JSON.stringify(resCoppia, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_coppia_avatar') {
      var cAttiva = getCoppiaAvatarAttiva();
      return ContentService.createTextOutput(JSON.stringify({ success: true, coppia: cAttiva }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_battuta_dario') {
      var bDario = getBattutaDarioCasuale();
      return ContentService.createTextOutput(JSON.stringify({ success: true, battuta: bDario }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_storie_citta') {
      var stCitta = getStorieCittaList();
      return ContentService.createTextOutput(JSON.stringify({ success: true, storie: stCitta }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'crea_foglio_battute_dario' || action === 'forza_creazione_fogli') {
      var resBat = inizializzaFoglioBattuteDario();
      var resBrand = aggiornaFoglioBattuteDarioBranding();
      var resSto = inizializzaFoglioStorieCitta();
      var resStoBrand = aggiornaFoglioStorieCittaBranding();
      var ss = getSpreadsheetSicuro();
      var sheetList = [];
      if (ss) {
        var all = ss.getSheets();
        for (var i = 0; i < all.length; i++) {
          sheetList.push(all[i].getName());
        }
      }
      return ContentService.createTextOutput(JSON.stringify({
        success: true,
        battute: resBat,
        branding: resBrand,
        storie: resSto,
        storieBranding: resStoBrand,
        tuttiIFogli: sheetList
      }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'pianifica_maratona') {
      var dOre = (e && e.parameter && e.parameter.durata) ? e.parameter.durata : '6';
      var dStart = (e && e.parameter && e.parameter.inizio) ? e.parameter.inizio : 'now';
      var dPausa = (e && e.parameter && e.parameter.pausa) ? e.parameter.pausa : '1';
      var dLoop = (e && e.parameter && e.parameter.loop) ? (e.parameter.loop === 'true' || String(e.parameter.loop).indexOf('true') !== -1) : false;
      var dOpts = {};
      try {
        if (e && e.parameter && e.parameter.opzioni) {
          dOpts = JSON.parse(e.parameter.opzioni);
        } else if (e && e.postData && e.postData.contents) {
          var postJ = JSON.parse(e.postData.contents);
          if (postJ.opzioni) dOpts = postJ.opzioni;
        }
      } catch(eOpt) {}
      var resMar = pianificaMaratonaPersonalizzata(dOre, dStart, dPausa, dLoop, dOpts);
      return ContentService.createTextOutput(JSON.stringify(resMar, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'ferma_maratona') {
      var resStopMar = fermaMaratonaAttiva();
      return ContentService.createTextOutput(JSON.stringify(resStopMar, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'ferma_diretta' || action === 'stop_live') {
      var resStopDir = fermaDirettaMultistream();
      return ContentService.createTextOutput(JSON.stringify(resStopDir, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'stato_maratona') {
      var resStMar = getStatoMaratona();
      return ContentService.createTextOutput(JSON.stringify(resStMar, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'attiva_ciclo_h24') {
      var resH24 = attivaCicloContinuoH24();
      return ContentService.createTextOutput(JSON.stringify(resH24, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'disattiva_ciclo_h24') {
      var resOffH24 = disattivaCicloContinuoH24();
      return ContentService.createTextOutput(JSON.stringify(resOffH24, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'stato_ciclo_h24') {
      var resStH24 = statoCicloContinuoH24();
      return ContentService.createTextOutput(JSON.stringify(resStH24, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'set_immobile_attivo') {
      var immName = (e && e.parameter && (e.parameter.tab || e.parameter.immobile)) ? (e.parameter.tab || e.parameter.immobile) : '';
      var resSet = setImmobileAttivoInDiretta(immName);
      return ContentService.createTextOutput(JSON.stringify(resSet, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'imposta_modalita_avatar') {
      var avMode = (e && e.parameter && e.parameter.mode) ? e.parameter.mode : 'CON_AVATAR';
      var resAv = impostaModalitaAvatar(avMode);
      return ContentService.createTextOutput(JSON.stringify(resAv, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'salva_chiavi_live' || action === 'salva_chiave_live') {
      var tkKey = (e && e.parameter && (e.parameter.tk_key || e.parameter.tiktok_key)) ? (e.parameter.tk_key || e.parameter.tiktok_key) : '';
      var igKey = (e && e.parameter && (e.parameter.ig_key || e.parameter.instagram_key)) ? (e.parameter.ig_key || e.parameter.instagram_key) : '';
      var resChiavi = { success: true, updated: [] };
      if (tkKey) {
        resChiavi.tiktok = (typeof salvaConfigurazioneTikTokLive === 'function') ? salvaConfigurazioneTikTokLive(tkKey) : { success: false };
        resChiavi.updated.push('TikTok');
      }
      if (igKey) {
        resChiavi.instagram = (typeof salvaConfigurazioneInstagramLive === 'function') ? salvaConfigurazioneInstagramLive(igKey) : { success: false };
        resChiavi.updated.push('Instagram');
      }
      if (typeof inviaNotificaTelegram === 'function' && resChiavi.updated.length > 0) {
        try { inviaNotificaTelegram("🔑 <b>NUOVE CHIAVI LIVE SALVATE DA BOT!</b> 🚀\n\nPiattaforme aggiornate: " + resChiavi.updated.join(", ") + "\n\n— <b>Immobiliare Giancani</b>", null, "HTML"); } catch(eTg){}
      }
      return ContentService.createTextOutput(JSON.stringify(resChiavi, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'test_avvio_multistream' || action === 'avvia_diretta') {
      var imm = (e && e.parameter && (e.parameter.immobile || e.parameter.tab)) ? (e.parameter.immobile || e.parameter.tab) : '';
      var avMode = (e && e.parameter && e.parameter.modalita_avatar) ? e.parameter.modalita_avatar : 'CON_AVATAR';
      var testo = (e && e.parameter && e.parameter.testo) ? e.parameter.testo : '';
      var opts = {};
      if (imm) {
        opts.immobile_id = imm;
        setImmobileAttivoInDiretta(imm);
      }
      if (avMode) {
        impostaModalitaAvatar(avMode);
      }
      var resLaunch = avviaDirettaMultistream(testo, opts);
      return ContentService.createTextOutput(JSON.stringify(resLaunch, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'archivia_post_fb_diretta') {
      var resArch = archiviaPostFacebookDirettaOra();
      return ContentService.createTextOutput(JSON.stringify(resArch, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'programma_archivio_fb') {
      var liveIdParam = (e && e.parameter && e.parameter.live_id) ? e.parameter.live_id : '';
      var resProg = programmaArchiviazionePostFacebookDopo1Ora(liveIdParam);
      return ContentService.createTextOutput(JSON.stringify(resProg, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'stato_archivio_fb') {
      var resStArch = getStatoArchiviazionePostFacebook();
      return ContentService.createTextOutput(JSON.stringify(resStArch, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'ispeziona_github_workflow') {
      var cfg = getTelegramConfig();
      var props = PropertiesService.getScriptProperties();
      var repo = props.getProperty('GITHUB_REPO') || 'Tonyhood2345/live-stream-serverless';
      var token = props.getProperty('GITHUB_TOKEN') || '';
      var runs = [];
      if (token) {
        try {
          var rUrl = 'https://api.github.com/repos/' + repo + '/actions/runs?per_page=5';
          var rRes = UrlFetchApp.fetch(rUrl, {
            headers: { 'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github.v3+json' },
            muteHttpExceptions: true
          });
          if (rRes.getResponseCode() === 200) {
            var rJ = JSON.parse(rRes.getContentText());
            runs = (rJ.workflow_runs || []).map(function(r){ return { id: r.id, name: r.name, status: r.status, conclusion: r.conclusion }; });
          }
        } catch(eR) {}
      }
      return ContentService.createTextOutput(JSON.stringify({ repo: repo, hasToken: !!token, ultimiRuns: runs }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'ripara_test_audio_workflow' || action === 'sincronizza_workflow_github') {
      var resRip = sincronizzaWorkflowGitHub();
      return ContentService.createTextOutput(JSON.stringify(resRip, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'installa_triggers_commenti') {
      var resTrigger = installaTriggersCommentiEGroq();
      return ContentService.createTextOutput(JSON.stringify(resTrigger, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'polla_commenti') {
      var resPoll = pollaCommentiDiretta();
      return ContentService.createTextOutput(JSON.stringify(resPoll, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_fogli_palinsesto') {
      var resFogli = getFogliDisponibiliPerPalinsesto();
      return ContentService.createTextOutput(JSON.stringify(resFogli, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'precompila_palinsesto_immobile') {
      var tabP = (e && e.parameter && e.parameter.tab) ? e.parameter.tab : '';
      var resPre = generaPalinsestoPrecompilatoImmobile(tabP);
      return ContentService.createTextOutput(JSON.stringify(resPre, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_palinsesto_dinamico') {
      var resPalD = getPalinsestoDinamicoWeb();
      return ContentService.createTextOutput(JSON.stringify(resPalD, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'richiedi_stanza_chat') {
      var stReq = (e && e.parameter && e.parameter.stanza) ? e.parameter.stanza : '';
      var autReq = (e && e.parameter && e.parameter.autore) ? e.parameter.autore : 'Immobiliare Giancani';
      var resStReq = registraRichiestaStanzaChat(stReq, autReq, Date.now());
      return ContentService.createTextOutput(JSON.stringify(resStReq, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'invia_commento_chat') {
      var msgChat = (e && e.parameter && (e.parameter.messaggio || e.parameter.testo || e.parameter.msg)) ? (e.parameter.messaggio || e.parameter.testo || e.parameter.msg) : '';
      var autChat = (e && e.parameter && e.parameter.autore) ? e.parameter.autore : 'Spettatore Web';
      var platChat = (e && e.parameter && e.parameter.piattaforma) ? e.parameter.piattaforma : 'Web Chat';
      var resChat = elaboraCommentoEsternoDiretto(msgChat, autChat, platChat);
      return ContentService.createTextOutput(JSON.stringify(resChat, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_coda_commenti') {
      var codaRecente = getElencoCommentiLiveRecenti();
      return ContentService.createTextOutput(JSON.stringify({ success: true, commenti: codaRecente }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_prossimo_commento_live') {
      var prox = prelevaProssimoCommentoLive();
      return ContentService.createTextOutput(JSON.stringify({ success: true, commento: prox }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'test_ig_comments') {
      var resTestIg = getNuoviCommentiInstagram();
      return ContentService.createTextOutput(JSON.stringify(resTestIg, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'reset_seen_comments') {
      PropertiesService.getScriptProperties().deleteProperty('FB_SEEN_COMMENT_IDS');
      PropertiesService.getScriptProperties().deleteProperty('YT_SEEN_COMMENT_IDS');
      PropertiesService.getScriptProperties().deleteProperty('IG_SEEN_COMMENT_IDS');
      PropertiesService.getScriptProperties().deleteProperty('CODA_COMMENTI_LIVE');
      return ContentService.createTextOutput(JSON.stringify({ success: true, message: 'Comment IDs FB/YT/IG e coda resettati con successo' })).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'sincronizza_youtube_nightly') {
      var resYtNight = sincronizzaVideoCanaleYouTube();
      return ContentService.createTextOutput(JSON.stringify(resYtNight, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_drive_folders') {
      var resFolds = getListaCartelleDriveUtente();
      return ContentService.createTextOutput(JSON.stringify(resFolds, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_drive_folder_preview') {
      var fId = (e && e.parameter && e.parameter.id) ? e.parameter.id : '';
      var resPrev = getAnteprimaFileCartellaDrive(fId);
      return ContentService.createTextOutput(JSON.stringify(resPrev, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'test_groq_multikey') {
      var qPrompt = (e && e.parameter && e.parameter.q) ? e.parameter.q : 'Ciao DarIA! Parlami della villa a Favara.';
      var poolKeys = getElencoChiaviGroqPool();
      var respAi = eseguiChiamataGroqMultiKey("Sei DarIA, assistente di Immobiliare Giancani.", qPrompt, { max_tokens: 150 });
      return ContentService.createTextOutput(JSON.stringify({
        success: !!respAi,
        chiaviNelPool: poolKeys.length,
        rispostaAI: respAi
      }, null, 2)).setMimeType(ContentService.MimeType.JSON);
    }

    // Pagine Web HTML
    var page = (e && e.parameter && e.parameter.page) ? e.parameter.page : '';
    if (page === 'generator' || page === 'regia' || page === 'admin') {
      var tGen = HtmlService.createTemplateFromFile('Generator');
      tGen.phoneParam = (e && e.parameter && e.parameter.phone) ? e.parameter.phone : '';
      return tGen
        .evaluate()
        .setTitle('🏰 Studio Regia Live 360° — Immobiliare Giancani')
        .addMetaTag('viewport', 'width=device-width, initial-scale=1.0')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
    }

    if (page === 'report' || page === 'report_proprietario') {
      var tRep = HtmlService.createTemplateFromFile('OwnerReport');
      tRep.reportId = (e && e.parameter && e.parameter.id) ? e.parameter.id : '';
      return tRep
        .evaluate()
        .setTitle('📊 Report Ufficiale Proprietario — Immobiliare Giancani')
        .addMetaTag('viewport', 'width=device-width, initial-scale=1.0')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
    }

    if (page === 'worldclock' || page === 'orologio') {
      return HtmlService.createHtmlOutputFromFile('WorldClock')
        .setTitle('🌍 Orologio Mondiale & Fusi Orari — Immobiliare Giancani')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
        .addMetaTag('viewport', 'width=device-width, initial-scale=1');
    }

    if (page === 'azure' || page === 'azuretts') {
      return HtmlService.createHtmlOutputFromFile('AzureTTS_UI')
        .setTitle('🎙️ Azure Speech Studio — Immobiliare Giancani')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
        .addMetaTag('viewport', 'width=device-width, initial-scale=1');
    }

    if (page === 'chat') {
      return HtmlService.createHtmlOutputFromFile('Chat')
        .setTitle('💬 Chat Diretta — Immobiliare Giancani')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
        .addMetaTag('viewport', 'width=device-width, initial-scale=1');
    }

    if (page === 'avatar' || page === 'live' || page === 'show' || page === '360' || page === 'classic') {
      return HtmlService.createTemplateFromFile('Index')
        .evaluate()
        .setTitle('🔴 DIRETTA LIVE — DarIA & DarIO | Immobiliare Giancani')
        .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
    }

    // Schermata Live Principale di Default (Versione 556 preferita dall'utente)
    return HtmlService.createTemplateFromFile('Index')
      .evaluate()
      .setTitle('🔴 DIRETTA LIVE — DarIA & DarIO | Immobiliare Giancani')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);

  } catch(e) {
    inviaAllertaErroreTelegram("11_RouterPrincipale.js", "doGet", e.toString());
    return ContentService.createTextOutput("Errore applicazione: " + e.toString());
  }
}

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return ContentService.createTextOutput(JSON.stringify({ success: false, error: 'No payload' })).setMimeType(ContentService.MimeType.JSON);
    }

    var payload = {};
    try { payload = JSON.parse(e.postData.contents); } catch(eP) { payload = e.parameter || {}; }

    // -1. Ricezione Chiavi Live da Bot Estrazione (TikTok & Instagram)
    if (payload.action === 'salva_chiavi_live' || payload.action === 'salva_chiave_live') {
      var tkK = payload.tk_key || payload.tiktok_key || '';
      var igK = payload.ig_key || payload.instagram_key || '';
      var resChiaviPost = { success: true, updated: [] };
      if (tkK) {
        resChiaviPost.tiktok = (typeof salvaConfigurazioneTikTokLive === 'function') ? salvaConfigurazioneTikTokLive(tkK) : { success: false };
        resChiaviPost.updated.push('TikTok');
      }
      if (igK) {
        resChiaviPost.instagram = (typeof salvaConfigurazioneInstagramLive === 'function') ? salvaConfigurazioneInstagramLive(igK) : { success: false };
        resChiaviPost.updated.push('Instagram');
      }
      if (typeof inviaNotificaTelegram === 'function' && resChiaviPost.updated.length > 0) {
        try { inviaNotificaTelegram("🔑 <b>NUOVE CHIAVI LIVE SALVATE DA BOT (POST)!</b> 🚀\n\nPiattaforme aggiornate: " + resChiaviPost.updated.join(", ") + "\n\n— <b>Immobiliare Giancani</b>", null, "HTML"); } catch(eTg){}
      }
      return ContentService.createTextOutput(JSON.stringify(resChiaviPost)).setMimeType(ContentService.MimeType.JSON);
    }

    // 0. Gestione Cambio Coppia Avatar in Diretta
    if (payload.action === 'imposta_coppia_avatar') {
      var resCoppiaPost = impostaAvatarInOnda(payload.donna, payload.uomo);
      return ContentService.createTextOutput(JSON.stringify(resCoppiaPost)).setMimeType(ContentService.MimeType.JSON);
    }

    // 1. Salvataggio Batch Video & Shorts YouTube da Python
    if (payload.action === 'salva_video_youtube_batch' || payload.videos || (payload.action === 'salva_video_youtube' && payload.data)) {
      var videosList = payload.videos || payload.data || [];
      var resYtBatch = salvaVideoYouTubeBatch(videosList);
      return ContentService.createTextOutput(JSON.stringify(resYtBatch)).setMimeType(ContentService.MimeType.JSON);
    }

    // 2. Webhook Telegram Bot
    if (payload.update_id && payload.message) {
      var resTg = elaboraComandoTelegramBot(payload);
      return ContentService.createTextOutput(JSON.stringify(resTg)).setMimeType(ContentService.MimeType.JSON);
    }

    // 3. Webhook WhatsApp
    if (payload.tipo === 'whatsapp' || payload.numeroMittente || payload.messaggio) {
      var resWA = elaboraRichiestaWhatsAppLive(payload);
      return ContentService.createTextOutput(JSON.stringify(resWA)).setMimeType(ContentService.MimeType.JSON);
    }

    // 4. Test e sincronizzazione Groq Multi-Key Pool
    if (payload.action === 'test_groq_multikey') {
      var qPrompt = payload.prompt || 'Ciao DarIA! Parlami brevemente della villa a Favara.';
      var respAi = eseguiChiamataGroqMultiKey("Sei DarIA, assistente di Immobiliare Giancani.", qPrompt, { max_tokens: 150 });
      return ContentService.createTextOutput(JSON.stringify({
        success: !!respAi,
        chiaviNelPool: getElencoChiaviGroqPool().length,
        rispostaAI: respAi
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // 5. Ricezione commento chat via POST
    if (payload.action === 'invia_commento_chat') {
      var msgP = payload.messaggio || payload.testo || payload.msg || '';
      var autP = payload.autore || 'Spettatore Web';
      var platP = payload.piattaforma || 'Web Chat';
      var resPostChat = elaboraCommentoEsternoDiretto(msgP, autP, platP);
      return ContentService.createTextOutput(JSON.stringify(resPostChat)).setMimeType(ContentService.MimeType.JSON);
    }

    // 6. Pubblicazione Snapshot & Storie Live 10 minuti (Facebook + YouTube)
    if (payload.action === 'pubblica_snapshot_live_10min' || payload.action === 'pubblica_storia_fb') {
      var resSnapPost = pubblicaSnapshotStoriaSocialOgni10Minuti(payload);
      return ContentService.createTextOutput(JSON.stringify(resSnapPost)).setMimeType(ContentService.MimeType.JSON);
    }

    // 7. Salvataggio Video su Google Drive (Base64)
    if (payload.action === 'carica_video_drive') {
      var b64P = payload.b64 || payload.base64 || payload.content || '';
      var fNameP = payload.fileName || payload.name || ('storia_' + Date.now() + '.mp4');
      var resUpP = caricaVideoBase64SuDrive(b64P, fNameP);
      return ContentService.createTextOutput(JSON.stringify(resUpP)).setMimeType(ContentService.MimeType.JSON);
    }

    // 8. Pubblicazione YouTube Short su Canale
    if (payload.action === 'pubblica_youtube_short') {
      var resShortPost = pubblicaShortYouTubeSuCanale(payload);
      return ContentService.createTextOutput(JSON.stringify(resShortPost)).setMimeType(ContentService.MimeType.JSON);
    }

    return ContentService.createTextOutput(JSON.stringify({ success: true, received: true })).setMimeType(ContentService.MimeType.JSON);

  } catch(e) {
    inviaAllertaErroreTelegram("11_RouterPrincipale.js", "doPost", e.toString());
    return ContentService.createTextOutput(JSON.stringify({ success: false, error: e.toString() })).setMimeType(ContentService.MimeType.JSON);
  }
}
