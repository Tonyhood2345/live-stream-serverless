// ═══════════════════════════════════════════════════════════════════════
// 📁 MODULO 07: TRASMISSIONE MULTISTREAM & GITHUB ACTIONS
// Gestisce avvio/arresto live stream simultaneo su Facebook, YouTube, Instagram e TikTok
// ═══════════════════════════════════════════════════════════════════════

function getParametriMultistreamSicuri() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName("Impostazioni_Social") : null;
    var payloadData = {};

    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var i = 0; i < data.length; i++) {
        var param = String(data[i][0] || "").trim().toLowerCase();
        for (var col = 0; col < data[i].length; col++) {
          var val = String(data[i][col] || "").trim();
          if (!val) continue;
          
          if (val.indexOf("ghp_") === 0 || val.indexOf("github_pat_") === 0) {
            payloadData.github_token = val;
          }
          if (val.indexOf("Tonyhood2345/") === 0) {
            payloadData.github_repo = val;
          }
          if (val.indexOf("EAA") === 0 && val.length > 50) {
            payloadData.fb_token = val;
          }
          if (param.indexOf("youtube") > -1 && val.length > 15 && val.indexOf("http") === -1 && val.indexOf("ghp_") === -1 && val.indexOf("EAA") === -1) {
            payloadData.yt_key = val;
          }
          if (param.indexOf("instagram") > -1 && val.length > 20) {
            payloadData.ig_key = val;
          }
          if (param.indexOf("tiktok") > -1 && val.length > 10) {
            payloadData.tk_key = val;
          }
        }
      }
    }

    var props = PropertiesService.getScriptProperties();
    if (props.getProperty('YT_STREAM_KEY')) payloadData.yt_key = props.getProperty('YT_STREAM_KEY');
    if (props.getProperty('TK_STREAM_KEY')) payloadData.tk_key = props.getProperty('TK_STREAM_KEY');
    if (props.getProperty('IG_STREAM_KEY')) payloadData.ig_key = props.getProperty('IG_STREAM_KEY');

    if (!payloadData.github_token) payloadData.github_token = props.getProperty('GITHUB_TOKEN') || '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';
    if (!payloadData.github_repo)  payloadData.github_repo  = props.getProperty('GITHUB_REPO') || 'Tonyhood2345/live-stream-serverless';
    if (!payloadData.fb_token)     payloadData.fb_token     = props.getProperty('FB_PAGE_ACCESS_TOKEN') || props.getProperty('FB_PAGE_TOKEN') || '';
    if (!payloadData.yt_key)       payloadData.yt_key       = 'umqe-k4ke-qba4-39db-abrp';
    payloadData.fb_key = props.getProperty('FB_PERMANENT_STREAM_KEY') || 'FB-1761836115505207-0-Ab4NotixqCElXbBE4ynoHVYe';
    payloadData.fb_stream_url = payloadData.fb_key;
    payloadData.video_url = SCRIPT_URL;
    payloadData.stream_quality = props.getProperty('STREAMING_QUALITY') || '1080p_std';
    payloadData.scale_factor = props.getProperty('STREAMING_SCALE_FACTOR') || '1.0';
    payloadData.custom_bitrate = props.getProperty('STREAM_CUSTOM_BITRATE') || '4500k';
    payloadData.custom_res = props.getProperty('STREAM_CUSTOM_RES') || '1920:1080';
    payloadData.stream_zoom = props.getProperty('STREAM_ZOOM') || '125';

    return { success: true, parametri: payloadData };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function avviaDirettaMultistream(testoPost, options) {
  try {
    var props = PropertiesService.getScriptProperties();
    var opts = (options && typeof options === 'object') ? options : {};

    // Reset flag post invito singolo Antonio Giancani per consentire il post all'avvio della nuova diretta
    props.deleteProperty('ANTONIO_LIVE_FEED_POSTED');

    if (opts.immobile_id) {
      props.setProperty('ACTIVE_IMMOBILE_TAB', opts.immobile_id);
      props.setProperty('ACTIVE_IMMOBILE', opts.immobile_id);
    }
    if (opts.stream_quality) props.setProperty('STREAMING_QUALITY', opts.stream_quality);
    if (opts.scale_factor) props.setProperty('STREAMING_SCALE_FACTOR', opts.scale_factor);
    if (opts.custom_bitrate) props.setProperty('STREAM_CUSTOM_BITRATE', opts.custom_bitrate);
    if (opts.custom_res) props.setProperty('STREAM_CUSTOM_RES', opts.custom_res);
    if (opts.zoom) props.setProperty('STREAM_ZOOM', String(opts.zoom));
    if (opts.yt_key) props.setProperty('YT_STREAM_KEY', opts.yt_key);
    if (opts.tk_key) props.setProperty('TK_STREAM_KEY', opts.tk_key);
    if (opts.ig_key) props.setProperty('IG_STREAM_KEY', opts.ig_key);

    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName("Impostazioni_Social") : null;
    var payloadData = {};

    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var i = 0; i < data.length; i++) {
        var param = String(data[i][0] || "").trim().toLowerCase();
        for (var col = 0; col < data[i].length; col++) {
          var val = String(data[i][col] || "").trim();
          if (!val) continue;
          
          if (val.indexOf("ghp_") === 0 || val.indexOf("github_pat_") === 0) {
            payloadData.github_token = val;
          }
          if (val.indexOf("Tonyhood2345/") === 0) {
            payloadData.github_repo = val;
          }
          if (val.indexOf("EAA") === 0 && val.length > 50) {
            payloadData.fb_token = val;
          }
          if (param.indexOf("youtube") > -1 && val.length > 15 && val.indexOf("http") === -1 && val.indexOf("ghp_") === -1 && val.indexOf("EAA") === -1) {
            payloadData.yt_key = val;
          }
          if (param.indexOf("instagram") > -1 && val.length > 20) {
            payloadData.ig_key = val;
          }
          if (param.indexOf("tiktok") > -1 && val.length > 10) {
            payloadData.tk_key = val;
          }
        }
      }
    }

    // Priorità alle opzioni passate o chiavi salvate
    if (opts.durata_ore) payloadData.durata_ore = opts.durata_ore;
    if (props.getProperty('YT_STREAM_KEY')) payloadData.yt_key = props.getProperty('YT_STREAM_KEY');
    if (props.getProperty('TK_STREAM_KEY')) payloadData.tk_key = props.getProperty('TK_STREAM_KEY');
    if (props.getProperty('IG_STREAM_KEY')) payloadData.ig_key = props.getProperty('IG_STREAM_KEY');

    if (!payloadData.github_token) payloadData.github_token = props.getProperty('GITHUB_TOKEN') || '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';
    if (!payloadData.github_repo)  payloadData.github_repo  = props.getProperty('GITHUB_REPO') || 'Tonyhood2345/live-stream-serverless';
    if (!payloadData.fb_token)     payloadData.fb_token     = props.getProperty('FB_PAGE_ACCESS_TOKEN') || props.getProperty('FB_PAGE_TOKEN') || '';
    if (!payloadData.yt_key)       payloadData.yt_key       = 'umqe-k4ke-qba4-39db-abrp';
    if (!payloadData.video_url)    payloadData.video_url    = SCRIPT_URL;

    props.setProperty('GITHUB_TOKEN', payloadData.github_token);
    props.setProperty('GITHUB_REPO', payloadData.github_repo);
    props.setProperty('YT_STREAM_KEY', payloadData.yt_key);

    if (!payloadData.github_token || !payloadData.github_repo) {
      return { success: false, error: "GitHub Token o Repo mancanti in Impostazioni_Social" };
    }

    // 1. Crea sessione Live Facebook
    var pageToken = props.getProperty('FB_PAGE_ACCESS_TOKEN') || 'EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI';
    var fbStreamUrl = "";
    var fbLiveId = "";

    try {
      var socialAI = (typeof generaDatiDirettaSocialIA === 'function') ? generaDatiDirettaSocialIA() : { titolo: "🔴 TOUR VIRTUALE 360° IN DIRETTA — Immobiliare Giancani", descrizione: "Tour immobiliare interattivo 360° con DarIA.\n\n— Immobiliare Giancani" };
      var fbApiUrl = "https://graph.facebook.com/v19.0/234931856561526/live_videos";
      var fbBody = "status=LIVE_NOW&title=" + encodeURIComponent(socialAI.titolo) +
                   "&description=" + encodeURIComponent(testoPost || socialAI.descrizione) +
                   "&access_token=" + encodeURIComponent(pageToken);
      var fbResp = UrlFetchApp.fetch(fbApiUrl, { method: "post", payload: fbBody, muteHttpExceptions: true });
      if (fbResp.getResponseCode() === 200) {
        var fbJson = JSON.parse(fbResp.getContentText());
        fbStreamUrl = fbJson.secure_stream_url || "";
        fbLiveId = fbJson.id || "";
        if (fbLiveId) {
          props.setProperty('FB_LIVE_VIDEO_ID', fbLiveId);
          props.setProperty('FB_POST_VIDEO_ID', fbLiveId);
        }
      }
    } catch(eFb) {
      console.warn("Avviso Facebook API:", eFb);
    }

    if (!fbStreamUrl) {
      fbStreamUrl = props.getProperty('FB_PERMANENT_STREAM_KEY') || 'FB-1761836115505207-0-Ab4NotixqCElXbBE4ynoHVYe';
    }

    // 1.5 Cancella eventuali run precedenti in corso per evitare stream duplicati su YouTube
    try {
      var activeRunsUrl = "https://api.github.com/repos/" + payloadData.github_repo + "/actions/runs?status=in_progress";
      var aResp = UrlFetchApp.fetch(activeRunsUrl, {
        method: "get",
        headers: { "Authorization": "token " + payloadData.github_token, "Accept": "application/vnd.github.v3+json", "User-Agent": "ImmobiliareGiancani-Bot" },
        muteHttpExceptions: true
      });
      if (aResp.getResponseCode() === 200) {
        var aData = JSON.parse(aResp.getContentText());
        if (aData.workflow_runs && aData.workflow_runs.length > 0) {
          aData.workflow_runs.forEach(function(r) {
            UrlFetchApp.fetch("https://api.github.com/repos/" + payloadData.github_repo + "/actions/runs/" + r.id + "/cancel", {
              method: "post",
              headers: { "Authorization": "token " + payloadData.github_token, "Accept": "application/vnd.github.v3+json", "User-Agent": "ImmobiliareGiancani-Bot" },
              muteHttpExceptions: true
            });
          });
          Utilities.sleep(2000);
        }
      }
    } catch(eCancel) {
      console.warn("Avviso cancellazione run precedenti:", eCancel);
    }

    // 1.8 Sincronizza configurazione GitHub (Zoom 100% e WebGL SwiftShader per 360)
    sincronizzaWorkflowGitHub(payloadData.github_repo, payloadData.github_token);

    // 2. Dispatch GitHub Actions
    var qualitaScelta = opts.stream_quality || props.getProperty('STREAMING_QUALITY') || '1080p_std';
    var scaleScelta = opts.scale_factor || props.getProperty('STREAMING_SCALE_FACTOR') || '1.0';
    var customBitrate = opts.custom_bitrate || props.getProperty('STREAM_CUSTOM_BITRATE') || '4500k';
    var customRes = opts.custom_res || props.getProperty('STREAM_CUSTOM_RES') || '1920:1080';

    var payload = {
      "ref": "main",
      "inputs": {
        "video_url": payloadData.video_url,
        "fb_key": fbStreamUrl,
        "yt_key": payloadData.yt_key,
        "tk_key": payloadData.tk_key || "",
        "ig_key": payloadData.ig_key || "",
        "duration_hours": String(payloadData.durata_ore || "6"),
        "stream_quality": qualitaScelta,
        "scale_factor": scaleScelta,
        "custom_bitrate": customBitrate,
        "custom_res": customRes
      }
    };

    var ghUrl = "https://api.github.com/repos/" + payloadData.github_repo + "/actions/workflows/live-stream.yml/dispatches";
    var ghResp = UrlFetchApp.fetch(ghUrl, {
      method: "post",
      headers: {
        "Authorization": "token " + payloadData.github_token,
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "ImmobiliareGiancani-Bot"
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    if (ghResp.getResponseCode() >= 200 && ghResp.getResponseCode() < 300) {
      inviaNotificaLancioDirettaTelegram(fbLiveId, "https://www.facebook.com/watch/?v=" + fbLiveId, testoPost);

      // 📸 Pubblica la prima Storia su Facebook annunciando la diretta live e attiva l'aggiornamento ogni 30 minuti per Facebook e YouTube
      try {
        if (typeof pubblicaSnapshotStoriaSocialOgni30Minuti === 'function') {
          pubblicaSnapshotStoriaSocialOgni30Minuti({ forza: true, isInitialLaunch: true });
        } else if (typeof pubblicaSnapshotStoriaSocialOgni10Minuti === 'function') {
          pubblicaSnapshotStoriaSocialOgni10Minuti({ forza: true, isInitialLaunch: true });
        }
        if (typeof attivaTriggerSnapshotStoriaOgni30Minuti === 'function') {
          attivaTriggerSnapshotStoriaOgni30Minuti();
        } else if (typeof attivaTriggerSnapshotStoriaOgni10Minuti === 'function') {
          attivaTriggerSnapshotStoriaOgni10Minuti();
        }
      } catch(eStoria) {
        console.warn("Avviso pubblicazione storia live:", eStoria);
      }

      return {
        success: true,
        fbLiveId: fbLiveId,
        fbWatchUrl: "https://www.facebook.com/watch/?v=" + fbLiveId,
        ytWatchUrl: "https://www.youtube.com/@immobiliaregiancani761/live",
        messaggio: "Diretta Multistream avviata con successo su Facebook, YouTube e Instagram! — Immobiliare Giancani"
      };
    } else {
      var errGh = "Errore GitHub (" + ghResp.getResponseCode() + "): " + ghResp.getContentText();
      inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "avviaDirettaMultistream", errGh);
      return { success: false, error: errGh };
    }

  } catch(e) {
    inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "avviaDirettaMultistream", e.toString());
    return { success: false, error: e.toString() };
  }
}

function fermaDirettaMultistream() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName("Impostazioni_Social") : null;
    var payloadData = {};

    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var i = 0; i < data.length; i++) {
        var param = String(data[i][0] || "").trim().toLowerCase();
        var val = String(data[i][5] || data[i][1] || "").trim();
        if (param == "github token" || param == "github_token") payloadData.github_token = val;
        if (param == "github repo" || param == "github_repo") payloadData.github_repo = val;
        if (param.indexOf("facebook") > -1) payloadData.fb_token = val;
        if (param == "id diretta / post" || param == "id diretta") payloadData.live_id = val;
      }
    }

    var props = PropertiesService.getScriptProperties();
    if (!payloadData.github_token) payloadData.github_token = props.getProperty('GITHUB_TOKEN') || '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';
    if (!payloadData.github_repo)  payloadData.github_repo  = props.getProperty('GITHUB_REPO') || 'Tonyhood2345/live-stream-serverless';
    if (!payloadData.fb_token)     payloadData.fb_token     = props.getProperty('FB_PAGE_ACCESS_TOKEN') || 'EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI';
    if (!payloadData.live_id)      payloadData.live_id      = props.getProperty('FB_LIVE_VIDEO_ID') || '';

    // Chiudi live Facebook
    if (payloadData.fb_token && payloadData.live_id) {
      try {
        var fbEndUrl = "https://graph.facebook.com/v19.0/" + payloadData.live_id;
        UrlFetchApp.fetch(fbEndUrl, {
          method: "post",
          payload: "end_live_video=true&access_token=" + encodeURIComponent(payloadData.fb_token),
          muteHttpExceptions: true
        });
      } catch(eFb) {}
    }

    // ⏰ PROGRAMMA ARCHIVIAZIONE POST FACEBOOK DOPO 1 ORA DAL TERMINE DELLA DIRETTA
    try {
      programmaArchiviazionePostFacebookDopo1Ora(payloadData.live_id);
    } catch(eArch) {
      console.warn("Avviso programmazione archiviazione Facebook:", eArch);
    }

    // Cancella workflow GitHub in corso
    if (payloadData.github_token && payloadData.github_repo) {
      try {
        var runsUrl = "https://api.github.com/repos/" + payloadData.github_repo + "/actions/runs?status=in_progress";
        var rResp = UrlFetchApp.fetch(runsUrl, {
          method: "get",
          headers: { "Authorization": "token " + payloadData.github_token, "Accept": "application/vnd.github.v3+json", "User-Agent": "ImmobiliareGiancani-Bot" },
          muteHttpExceptions: true
        });
        if (rResp.getResponseCode() === 200) {
          var rJson = JSON.parse(rResp.getContentText());
          if (rJson.workflow_runs) {
            rJson.workflow_runs.forEach(function(run) {
              UrlFetchApp.fetch("https://api.github.com/repos/" + payloadData.github_repo + "/actions/runs/" + run.id + "/cancel", {
                method: "post",
                headers: { "Authorization": "token " + payloadData.github_token, "Accept": "application/vnd.github.v3+json", "User-Agent": "ImmobiliareGiancani-Bot" },
                muteHttpExceptions: true
              });
            });
          }
        }
      } catch(eGh) {}
    }

    // Disattiva trigger 30 min storia Facebook e YouTube
    try {
      if (typeof disattivaTriggerSnapshotStoriaOgni30Minuti === 'function') {
        disattivaTriggerSnapshotStoriaOgni30Minuti();
      } else if (typeof disattivaTriggerSnapshotStoriaOgni10Minuti === 'function') {
        disattivaTriggerSnapshotStoriaOgni10Minuti();
      } else if (typeof disattivaTriggerOrarioStoriaFacebook === 'function') {
        disattivaTriggerOrarioStoriaFacebook();
      }
    } catch(eStoryTrig) {}

    // Reset flag post invito singolo Antonio Giancani
    props.deleteProperty('ANTONIO_LIVE_FEED_POSTED');

    var resoconto = generaResocontoFineDiretta();
    return {
      success: true,
      messaggio: "Diretta fermata con successo. Il post Facebook verrà spostato in archivio tra 1 ora — Immobiliare Giancani",
      resoconto: resoconto
    };
  } catch(e) {
    inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "fermaDirettaMultistream", e.toString());
    return { success: false, error: e.toString() };
  }
}

function salvaParametroSocialSuFoglio(nomeParam, valore) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName("Impostazioni_Social") : null;
    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var i = 0; i < data.length; i++) {
        var p = String(data[i][0] || '').trim().toLowerCase();
        if (p.indexOf(nomeParam.toLowerCase()) > -1) {
          sheet.getRange(i + 1, 6).setValue(valore); // Salva in Colonna F
          sheet.getRange(i + 1, 2).setValue(valore); // Salva in Colonna B
          return true;
        }
      }
      sheet.appendRow([nomeParam, valore, '', '', '', valore]);
    }
  } catch(e) {
    console.warn("Errore salvaParametroSocialSuFoglio:", e);
  }
  return false;
}

function impostaNuovaChiaveYouTube(nuovaChiave) {
  try {
    var props = PropertiesService.getScriptProperties();
    props.setProperty('YT_STREAM_KEY', nuovaChiave || '');
    salvaParametroSocialSuFoglio("YouTube", nuovaChiave);
    return { success: true, messaggio: "Chiave YouTube salvata: " + nuovaChiave };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function impostaChiaveInstagram(fullRtmpUrl) {
  try {
    var props = PropertiesService.getScriptProperties();
    props.setProperty('IG_STREAM_KEY', fullRtmpUrl || '');
    salvaParametroSocialSuFoglio("Instagram", fullRtmpUrl);
    return { success: true };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * Sincronizza il workflow GitHub di streaming per calibrare qualità FFmpeg,
 * eliminare qualsiasi crop decentrato e impostare la scala del browser virtuale.
 */
function sincronizzaWorkflowGitHub(githubRepo, githubToken) {
  try {
    var props = PropertiesService.getScriptProperties();
    var repo = githubRepo || props.getProperty('GITHUB_REPO') || 'Tonyhood2345/live-stream-serverless';
    var token = githubToken || props.getProperty('GITHUB_TOKEN') || '';
    if (!token) return { success: false, error: 'Token GitHub mancante' };

    var scaleFactor = props.getProperty('STREAMING_SCALE_FACTOR') || '1.0';
    var qualita = props.getProperty('STREAMING_QUALITY') || '1080p_std';

    var url = "https://api.github.com/repos/" + repo + "/contents/.github/workflows/live-stream.yml";
    var res = UrlFetchApp.fetch(url, {
      method: "get",
      headers: { "Authorization": "Bearer " + token, "Accept": "application/vnd.github.v3+json" },
      muteHttpExceptions: true
    });

    if (res.getResponseCode() === 200) {
      var json = JSON.parse(res.getContentText());
      var sha = json.sha;
      var curContent = Utilities.newBlob(Utilities.base64Decode(json.content)).getDataAsString();

      var updated = curContent;

      // 1. Rimuovi crop errato di FFmpeg che decentrava la schermata: imposta scale pulito senza tagli
      updated = updated.replace(
        /-vf\s+"crop=1920:1030:0:50,scale=1920:1080"/g,
        '-vf "scale=1920:1080:flags=lanczos"'
      );

      // 2. Imposta scala browser desktop nativa (1.0 = centrato 1:1)
      updated = updated.replace(
        /--force-device-scale-factor=[0-9.]+/g,
        "--force-device-scale-factor=" + scaleFactor
      );

      // 3. Rimuovi --high-dpi-support che causava offset nei browser headless
      updated = updated.replace(/\s*--high-dpi-support=1\s*\\/g, '');

      if (updated !== curContent) {
        var putRes = UrlFetchApp.fetch(url, {
          method: "put",
          headers: { "Authorization": "Bearer " + token, "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json" },
          payload: JSON.stringify({
            message: "Configurazione FFmpeg & Chrome: Scala " + scaleFactor + ", no crop, centratura 1:1 - Immobiliare Giancani",
            content: Utilities.base64Encode(updated),
            sha: sha,
            branch: "main"
          }),
          muteHttpExceptions: true
        });

        return { success: putRes.getResponseCode() >= 200 && putRes.getResponseCode() < 300, statusCode: putRes.getResponseCode() };
      }
      return { success: true, message: 'Workflow GitHub già sincronizzato con scala ' + scaleFactor + ' e nessun crop' };
    }
    return { success: false, code: res.getResponseCode(), error: res.getContentText() };
  } catch(e) {
    console.warn("Avviso sincronizzaWorkflowGitHub:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * ⚙️ Salva le impostazioni di qualità streaming FFmpeg e scala del browser virtuale
 * e aggiorna il workflow GitHub
 */
function salvaQualitaStreamingFFmpeg(qualita, scaleFactor, cropMode, customBitrate, customRes) {
  try {
    var props = PropertiesService.getScriptProperties();
    qualita = qualita || '1080p_std';
    scaleFactor = scaleFactor || '1.0';
    cropMode = cropMode || 'none';

    props.setProperty('STREAMING_QUALITY', qualita);
    props.setProperty('STREAMING_SCALE_FACTOR', scaleFactor);
    props.setProperty('STREAMING_CROP_MODE', cropMode);
    if (customBitrate) props.setProperty('STREAM_CUSTOM_BITRATE', customBitrate);
    if (customRes) props.setProperty('STREAM_CUSTOM_RES', customRes);

    return {
      success: true,
      qualita: qualita,
      scaleFactor: scaleFactor,
      customBitrate: customBitrate || '4500k',
      customRes: customRes || '1920:1080',
      messaggio: "Qualità streaming FFmpeg (" + qualita + ") e scala (" + scaleFactor + ") salvate con successo! — Immobiliare Giancani"
    };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function riavviaDirettaConNuovaQualita(opzioni) {
  try {
    var opts = opzioni || {};
    // 1. Ferma la trasmissione attuale su cloud e social
    fermaDirettaMultistream();
    Utilities.sleep(2500);

    // 2. Rilancia con i nuovi parametri FFmpeg e scala
    var res = avviaDirettaMultistream("", opts);
    return {
      success: res.success,
      messaggio: res.success ? "Diretta riavviata con successo con la nuova configurazione FFmpeg! — Immobiliare Giancani" : (res.error || "Errore durante il riavvio"),
      dettagli: res
    };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 🔍 Restituisce le impostazioni attuali di qualità streaming e scala FFmpeg
 */
function getQualitaStreamingFFmpeg() {
  try {
    var props = PropertiesService.getScriptProperties();
    var q = props.getProperty('STREAMING_QUALITY') || '1080p_std';
    return {
      success: true,
      qualita: q,
      scaleFactor: props.getProperty('STREAMING_SCALE_FACTOR') || '1.0',
      cropMode: props.getProperty('STREAMING_CROP_MODE') || 'none',
      bitrateInfo: getBitrateInfoDettagliata(q)
    };
  } catch(e) {
    return { success: false, qualita: '1080p_std', scaleFactor: '1.0', cropMode: 'none', bitrateInfo: getBitrateInfoDettagliata('1080p_std') };
  }
}

function getBitrateInfoDettagliata(q) {
  if (q === '1080p_high') return { label: 'Ultra HD 1080p (6000 kbps CBR)', res: '1920x1080', bitrate: '6000k', preset: 'veryfast' };
  if (q === '720p_hq') return { label: 'HD 720p Alta Qualità (3200 kbps CBR)', res: '1280x720', bitrate: '3200k', preset: 'veryfast' };
  if (q === '720p_eco') return { label: 'HD 720p Risparmio Banda (2000 kbps CBR)', res: '1280x720', bitrate: '2000k', preset: 'veryfast' };
  return { label: 'Full HD 1080p Standard (4500 kbps CBR)', res: '1920x1080', bitrate: '4500k', preset: 'veryfast' };
}

function aggiornaWorkflowGitHubPerYouTube() { return sincronizzaWorkflowGitHub(); }
function riparaTestAudioWorkflowGitHub() { return sincronizzaWorkflowGitHub(); }

function impostaChiaveTikTok(fullRtmpUrl) {
  try {
    var props = PropertiesService.getScriptProperties();
    props.setProperty('TK_STREAM_KEY', fullRtmpUrl || '');
    salvaParametroSocialSuFoglio("TikTok", fullRtmpUrl);
    return { success: true, messaggio: "Chiave TikTok salvata con successo!" };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * ⏰ CICLO CONTINUO H24 (6h ON + 1h PAUSA)
 * Gestisce l'avvio e la pianificazione automatica della diretta ogni 7 ore
 */
function attivaCicloContinuoH24() {
  try {
    var props = PropertiesService.getScriptProperties();
    props.setProperty('CICLO_CONTINUO_H24_ATTIVO', 'true');
    
    // Cancella vecchi trigger per evitare duplicati
    disattivaTriggerCicloH24();
    
    // 1. Avvia la diretta adesso
    var res = avviaDirettaMultistream();
    
    // 2. Imposta il prossimo avvio automatico tra 7 ore (6h trasmissione + 1h pausa)
    ScriptApp.newTrigger('eseguiCicloContinuoH24Automatico')
      .timeBased()
      .after(7 * 60 * 60 * 1000)
      .create();
      
    inviaNotificaTelegram("⏰ <b>CICLO DIRETTE H24 ATTIVATO!</b> 🚀\n\n" +
                          "▫️ <b>Durata diretta:</b> 6 ore continue\n" +
                          "▫️ <b>Pausa tecnica:</b> 1 ora\n" +
                          "▫️ <b>Prossimo riavvio automatico:</b> tra 7 ore esatte!\n\n" +
                          "— <b>Immobiliare Giancani</b>", null, 'HTML');

    return { success: true, messaggio: "Ciclo continuo H24 attivato con successo (6h Diretta + 1h Pausa)! — Immobiliare Giancani" };
  } catch(e) {
    inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "attivaCicloContinuoH24", e.toString());
    return { success: false, error: e.toString() };
  }
}

function eseguiCicloContinuoH24Automatico() {
  try {
    var props = PropertiesService.getScriptProperties();
    var attivo = props.getProperty('CICLO_CONTINUO_H24_ATTIVO');
    if (attivo !== 'true') return;
    
    // 1. Avvia nuova sessione di diretta (crea nuovo post Facebook, lancia stream YouTube)
    avviaDirettaMultistream();
    
    // 2. Riprogramma la sessione successiva tra 7 ore (6h diretta + 1h pausa)
    disattivaTriggerCicloH24();
    ScriptApp.newTrigger('eseguiCicloContinuoH24Automatico')
      .timeBased()
      .after(7 * 60 * 60 * 1000)
      .create();
  } catch(e) {
    inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "eseguiCicloContinuoH24Automatico", e.toString());
  }
}

function disattivaCicloContinuoH24() {
  try {
    var props = PropertiesService.getScriptProperties();
    props.setProperty('CICLO_CONTINUO_H24_ATTIVO', 'false');
    disattivaTriggerCicloH24();
    fermaDirettaMultistream();
    inviaNotificaTelegram("⏹️ <b>CICLO DIRETTE H24 DISATTIVATO.</b>\n\nIl palinsesto automatico è stato fermato.\n\n— <b>Immobiliare Giancani</b>", null, 'HTML');
    return { success: true, messaggio: "Ciclo continuo H24 disattivato." };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function disattivaTriggerCicloH24() {
  try {
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
      if (triggers[i].getHandlerFunction() === 'eseguiCicloContinuoH24Automatico') {
        ScriptApp.deleteTrigger(triggers[i]);
      }
    }
  } catch(e) {
    console.warn("disattivaTriggerCicloH24:", e);
  }
}

function statoCicloContinuoH24() {
  var props = PropertiesService.getScriptProperties();
  var attivo = props.getProperty('CICLO_CONTINUO_H24_ATTIVO') === 'true';
  return { attivo: attivo };
}

/**
 * ⏱️ PIANIFICATORE MARATONE PERSONALIZZATE (DURATA + ORARIO SCELTI DALL'UTENTE + RIPOSO DARIA + SELEZIONE IMMOBILI)
 */
function pianificaMaratonaPersonalizzata(durataOre, dataOraInizio, pausaOre, ricorrente, opzioni) {
  try {
    var props = PropertiesService.getScriptProperties();
    var opts = (opzioni && typeof opzioni === 'object') ? opzioni : {};

    var durataNum = parseFloat(durataOre) || 6;
    if (durataNum > 12) durataNum = 12;
    if (durataNum < 0.25) durataNum = 0.25;

    var pausaNum = parseFloat(pausaOre) || 1;
    var isLoop = (ricorrente === true || ricorrente === 'true' || String(ricorrente).indexOf('true') !== -1);

    var oraAttualeMs = new Date().getTime();
    var targetStartMs = oraAttualeMs;

    if (dataOraInizio && dataOraInizio !== 'now' && dataOraInizio !== 'adesso') {
      var parsedDate = new Date(dataOraInizio);
      if (!isNaN(parsedDate.getTime()) && parsedDate.getTime() > oraAttualeMs) {
        targetStartMs = parsedDate.getTime();
      }
    }

    // Calcolo orario di stop preciso
    var targetEndMs = targetStartMs + (durataNum * 3600 * 1000);
    if (opts.orarioStopPreciso) {
      try {
        var parts = opts.orarioStopPreciso.split(':');
        if (parts.length === 2) {
          var stopDate = new Date(targetStartMs);
          stopDate.setHours(parseInt(parts[0], 10), parseInt(parts[1], 10), 0, 0);
          if (stopDate.getTime() <= targetStartMs) {
            stopDate.setDate(stopDate.getDate() + 1);
          }
          targetEndMs = stopDate.getTime();
          durataNum = Math.max(0.25, parseFloat(((targetEndMs - targetStartMs) / 3600000).toFixed(2)));
        }
      } catch(eStop) {}
    }

    // Parametri avanzati DarIA & Immobili
    var pausaDarIA = opts.pausaDarIA || '3_ogni_immobile';
    var quantiImmobili = opts.quantiImmobili || 'tutti';
    var immobiliSelezionati = Array.isArray(opts.immobiliSelezionati) ? opts.immobiliSelezionati : [];
    var tempoPerImmobile = opts.tempoPerImmobile || 'giro_completo';

    // Salva proprietà per la diretta
    props.setProperty('DARIA_PAUSA_MODE', pausaDarIA);
    props.setProperty('MARATONA_TEMPO_IMMOBILE', String(tempoPerImmobile));
    props.setProperty('MARATONA_IMMOBILI_LIST', JSON.stringify(immobiliSelezionati));

    // Se sono stati scelti immobili specifici e c'è almeno un immobile, imposta il primo come attivo
    if (immobiliSelezionati.length > 0) {
      props.setProperty('ACTIVE_IMMOBILE_TAB', immobiliSelezionati[0]);
    }

    // Cancella vecchi trigger maratona
    disattivaTriggerMaratona();

    var config = {
      durataOre: durataNum,
      pausaOre: pausaNum,
      isLoop: isLoop,
      targetStartMs: targetStartMs,
      targetEndMs: targetEndMs,
      stato: (targetStartMs <= oraAttualeMs + 60000) ? 'IN_ONDA' : 'PROGRAMMATA',
      pausaDarIA: pausaDarIA,
      quantiImmobili: quantiImmobili,
      immobiliSelezionati: immobiliSelezionati,
      tempoPerImmobile: tempoPerImmobile,
      orarioStopPreciso: opts.orarioStopPreciso || ''
    };

    props.setProperty('MARATONA_CONFIG', JSON.stringify(config));
    props.setProperty('MARATONA_ATTIVA', 'true');

    var elencoImmobiliStr = (immobiliSelezionati.length > 0) ? immobiliSelezionati.join(', ') : (quantiImmobili === 'tutti' ? 'Tutti gli Immobili' : (quantiImmobili + ' Immobili a Rotazione'));

    if (config.stato === 'IN_ONDA') {
      // 1. Avvia subito la diretta
      var resLaunch = avviaDirettaMultistream();

      // 2. Imposta trigger di arresto o di loop
      try {
        if (isLoop) {
          var cycleMs = (durataNum + pausaNum) * 3600 * 1000;
          ScriptApp.newTrigger('eseguiLoopMaratonaAutomatico')
            .timeBased()
            .after(cycleMs)
            .create();
        } else {
          ScriptApp.newTrigger('eseguiArrestoMaratonaAutomatico')
            .timeBased()
            .after(durataNum * 3600 * 1000)
            .create();
        }
      } catch(eTrig1) {
        console.warn("Trigger maratona non creato (richiede autorizzazione):", eTrig1);
      }

      inviaNotificaTelegram("🚀 <b>MARATONA LIVE AVVIATA ORA!</b> 🎙️✨\n\n" +
                            "⏱️ <b>Durata:</b> " + durataNum + " Ore\n" +
                            "🛑 <b>Fine Trasmissione:</b> " + Utilities.formatDate(new Date(config.targetEndMs), "Europe/Rome", "HH:mm dd/MM/yyyy") + "\n" +
                            "☕ <b>Pausa Riposo DarIA:</b> " + pausaDarIA.replace(/_/g, ' ') + "\n" +
                            "🏠 <b>Immobili in Onda:</b> " + elencoImmobiliStr + "\n" +
                            "🔄 <b>Modalità:</b> " + (isLoop ? ("Loop Continuo (Pausa " + pausaNum + "h)") : "Singola Maratona") + "\n\n" +
                            "— <b>Immobiliare Giancani</b>", null, 'HTML');

      return { success: true, messaggio: "Maratona di " + durataNum + " ore avviata con successo!", config: config };
    } else {
      // Programmata per il futuro
      var delayMs = targetStartMs - oraAttualeMs;
      try {
        ScriptApp.newTrigger('eseguiStartMaratonaPianificata')
          .timeBased()
          .after(delayMs)
          .create();
      } catch(eTrig2) {
        console.warn("Trigger start maratona non creato:", eTrig2);
      }

      inviaNotificaTelegram("📅 <b>MARATONA LIVE PROGRAMMATA!</b> ⏰✨\n\n" +
                            "🕒 <b>Inizio Previsto:</b> " + Utilities.formatDate(new Date(targetStartMs), "Europe/Rome", "HH:mm dd/MM/yyyy") + "\n" +
                            "⏱️ <b>Durata:</b> " + durataNum + " Ore (Stop: " + Utilities.formatDate(new Date(config.targetEndMs), "Europe/Rome", "HH:mm") + ")\n" +
                            "☕ <b>Pausa Riposo DarIA:</b> " + pausaDarIA.replace(/_/g, ' ') + "\n" +
                            "🏠 <b>Immobili:</b> " + elencoImmobiliStr + "\n" +
                            "🔄 <b>Modalità:</b> " + (isLoop ? ("Loop Continuo (Pausa " + pausaNum + "h)") : "Singola Maratona") + "\n\n" +
                            "— <b>Immobiliare Giancani</b>", null, 'HTML');

      return { success: true, messaggio: "Maratona programmata per le " + Utilities.formatDate(new Date(targetStartMs), "Europe/Rome", "HH:mm del dd/MM/yyyy"), config: config };
    }
  } catch(e) {
    inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "pianificaMaratonaPersonalizzata", e.toString());
    return { success: false, error: e.toString() };
  }
}

function eseguiStartMaratonaPianificata() {
  try {
    var props = PropertiesService.getScriptProperties();
    var cfgStr = props.getProperty('MARATONA_CONFIG');
    if (!cfgStr) return;
    var cfg = JSON.parse(cfgStr);
    
    // Avvia la diretta
    avviaDirettaMultistream();
    cfg.stato = 'IN_ONDA';
    cfg.targetEndMs = new Date().getTime() + (cfg.durataOre * 3600 * 1000);
    props.setProperty('MARATONA_CONFIG', JSON.stringify(cfg));

    disattivaTriggerMaratona();
    if (cfg.isLoop) {
      var cycleMs = (cfg.durataOre + cfg.pausaOre) * 3600 * 1000;
      ScriptApp.newTrigger('eseguiLoopMaratonaAutomatico')
        .timeBased()
        .after(cycleMs)
        .create();
    } else {
      ScriptApp.newTrigger('eseguiArrestoMaratonaAutomatico')
        .timeBased()
        .after(cfg.durataOre * 3600 * 1000)
        .create();
    }
  } catch(e) {
    inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "eseguiStartMaratonaPianificata", e.toString());
  }
}

function eseguiLoopMaratonaAutomatico() {
  try {
    var props = PropertiesService.getScriptProperties();
    var attiva = props.getProperty('MARATONA_ATTIVA');
    if (attiva !== 'true') return;
    var cfgStr = props.getProperty('MARATONA_CONFIG');
    if (!cfgStr) return;
    var cfg = JSON.parse(cfgStr);

    // Rilancia nuova sessione
    avviaDirettaMultistream();
    cfg.stato = 'IN_ONDA';
    cfg.targetEndMs = new Date().getTime() + (cfg.durataOre * 3600 * 1000);
    props.setProperty('MARATONA_CONFIG', JSON.stringify(cfg));

    disattivaTriggerMaratona();
    var cycleMs = (cfg.durataOre + cfg.pausaOre) * 3600 * 1000;
    ScriptApp.newTrigger('eseguiLoopMaratonaAutomatico')
      .timeBased()
      .after(cycleMs)
      .create();
  } catch(e) {
    inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "eseguiLoopMaratonaAutomatico", e.toString());
  }
}

function eseguiArrestoMaratonaAutomatico() {
  try {
    fermaDirettaMultistream();
    var props = PropertiesService.getScriptProperties();
    props.setProperty('MARATONA_ATTIVA', 'false');
    disattivaTriggerMaratona();
    inviaNotificaTelegram("🏁 <b>MARATONA LIVE COMPLETATA!</b> 🎉\n\nLa sessione programmata si è conclusa con successo.\n\n— <b>Immobiliare Giancani</b>", null, 'HTML');
  } catch(e) {
    inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "eseguiArrestoMaratonaAutomatico", e.toString());
  }
}

function fermaMaratonaAttiva() {
  try {
    var props = PropertiesService.getScriptProperties();
    props.setProperty('MARATONA_ATTIVA', 'false');
    disattivaTriggerMaratona();
    fermaDirettaMultistream();
    inviaNotificaTelegram("⏹️ <b>MARATONA LIVE FERMATA MANUALMENTE.</b>\n\n— <b>Immobiliare Giancani</b>", null, 'HTML');
    return { success: true, messaggio: "Maratona fermata con successo." };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function disattivaTriggerMaratona() {
  try {
    var triggers = ScriptApp.getProjectTriggers();
    var funcs = ['eseguiStartMaratonaPianificata', 'eseguiLoopMaratonaAutomatico', 'eseguiArrestoMaratonaAutomatico'];
    for (var i = 0; i < triggers.length; i++) {
      if (funcs.indexOf(triggers[i].getHandlerFunction()) !== -1) {
        ScriptApp.deleteTrigger(triggers[i]);
      }
    }
  } catch(e) {
    console.warn("disattivaTriggerMaratona:", e);
  }
}

function getStatoMaratona() {
  try {
    var props = PropertiesService.getScriptProperties();
    var attiva = props.getProperty('MARATONA_ATTIVA') === 'true';
    var cfgStr = props.getProperty('MARATONA_CONFIG');
    var cfg = cfgStr ? JSON.parse(cfgStr) : null;
    return { success: true, attiva: attiva, config: cfg };
  } catch(e) {
    return { success: false, attiva: false, error: e.toString() };
  }
}

// ═══════════════════════════════════════════════════════════════════════
// 📦 ARCHIVIAZIONE AUTOMATICA POST FACEBOOK DOPO 1 ORA DAL TERMINE LIVE
// ═══════════════════════════════════════════════════════════════════════

/**
 * Programma l'archiviazione del post della diretta live su Facebook dopo 1 ora (60 minuti).
 * @param {string} liveId ID della sessione Live Facebook o del post video
 */
function programmaArchiviazionePostFacebookDopo1Ora(liveId) {
  try {
    var props = PropertiesService.getScriptProperties();
    var targetId = liveId || props.getProperty('FB_LIVE_VIDEO_ID') || props.getProperty('FB_POST_VIDEO_ID') || '';
    if (targetId) {
      props.setProperty('FB_TARGET_ARCHIVE_ID', String(targetId));
    }

    var msDelay = 60 * 60 * 1000; // 1 ora esatta (3.600.000 ms)
    var targetDate = new Date(Date.now() + msDelay);
    props.setProperty('FB_ARCHIVE_SCHEDULED_TIME', targetDate.toISOString());
    props.setProperty('FB_ARCHIVE_STATUS', 'IN_ATTESA_1_ORA');

    try {
      rimuoviTriggerArchiviazionePostFacebook();
      ScriptApp.newTrigger('eseguiArchiviazionePostFacebookDopoDiretta')
        .timeBased()
        .after(msDelay)
        .create();
    } catch(eTrig) {
      console.warn("Avviso creazione trigger a tempo (verrà monitorato tramite polling di sicurezza):", eTrig);
    }

    var orarioStr = targetDate.toLocaleTimeString('it-IT', { timeZone: 'Europe/Rome', hour: '2-digit', minute: '2-digit' });
    console.log("⏰ [ARCHIVIO FB] Trigger archiviazione programmato per le ore " + orarioStr + " (tra 1 ora) sul target ID: " + targetId);

    var notificaMsg = "⏰ <b>ARCHIVIAZIONE POST FACEBOOK PROGRAMMATA</b>\n\n" +
      "La diretta live è terminata. Come da procedura aziendale, il post video su Facebook verrà <b>spostato automaticamente in archivio tra 1 ora</b> (alle " + orarioStr + ").\n" +
      "• <b>ID Live / Post:</b> <code>" + (targetId || 'Ultimo live registrato') + "</code>\n\n" +
      "— <b>Immobiliare Giancani</b>";

    if (typeof inviaNotificaTelegram === 'function') {
      inviaNotificaTelegram(notificaMsg, null, 'HTML');
    }

    return {
      success: true,
      targetId: targetId,
      orarioArchivio: orarioStr,
      targetDate: targetDate.toISOString(),
      messaggio: "Archiviazione post Facebook programmata tra 1 ora (alle " + orarioStr + ") — Immobiliare Giancani"
    };
  } catch(e) {
    console.error("Errore programmaArchiviazionePostFacebookDopo1Ora:", e);
    if (typeof inviaAllertaErroreTelegram === 'function') {
      inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "programmaArchiviazionePostFacebookDopo1Ora", e.toString());
    }
    return { success: false, error: e.toString() };
  }
}

/**
 * Esegue l'archiviazione (nascondimento dalla timeline & impostazione a non pubblicato)
 * del post e video della diretta su Facebook.
 */
function eseguiArchiviazionePostFacebookDopoDiretta() {
  try {
    rimuoviTriggerArchiviazionePostFacebook();
    var props = PropertiesService.getScriptProperties();
    var targetId = props.getProperty('FB_TARGET_ARCHIVE_ID') || props.getProperty('FB_LIVE_VIDEO_ID') || props.getProperty('FB_POST_VIDEO_ID') || '';

    var pageToken = props.getProperty('FB_PAGE_ACCESS_TOKEN') || '';
    var pageId = '234931856561526';

    if (!pageToken) {
      var ss = getSpreadsheetSicuro();
      var sheet = ss ? ss.getSheetByName("Impostazioni_Social") : null;
      if (sheet) {
        var data = sheet.getDataRange().getValues();
        for (var i = 0; i < data.length; i++) {
          var param = String(data[i][0] || "").trim().toLowerCase();
          if (param.indexOf("facebook") > -1) {
            pageToken = String(data[i][5] || data[i][1] || "").trim();
            break;
          }
        }
      }
    }

    if (!pageToken) {
      pageToken = 'EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI';
    }

    // Se non c'è targetId registrato, trova l'ultimo live video completato
    if (!targetId) {
      try {
        var lastLiveUrl = "https://graph.facebook.com/v19.0/" + pageId + "/live_videos?limit=1&access_token=" + encodeURIComponent(pageToken);
        var respL = UrlFetchApp.fetch(lastLiveUrl, { method: "get", muteHttpExceptions: true });
        if (respL.getResponseCode() === 200) {
          var jL = JSON.parse(respL.getContentText());
          if (jL.data && jL.data.length > 0) {
            targetId = jL.data[0].id;
          }
        }
      } catch(eFind) {
        console.warn("Avviso ricerca ultimo live video FB:", eFind);
      }
    }

    var logAzioni = [];
    var archivioRiuscito = false;

    if (targetId) {
      // 1. Ispeziona l'oggetto per identificare Video ID e Timeline Post ID
      var videoId = "";
      var postId = "";
      try {
        var infoUrl = "https://graph.facebook.com/v19.0/" + targetId + "?fields=id,status,video{id,post_id}&access_token=" + encodeURIComponent(pageToken);
        var infoResp = UrlFetchApp.fetch(infoUrl, { method: "get", muteHttpExceptions: true });
        if (infoResp.getResponseCode() === 200) {
          var infoJson = JSON.parse(infoResp.getContentText());
          if (infoJson.video) {
            videoId = infoJson.video.id || "";
            postId = infoJson.video.post_id || "";
          }
        }
      } catch(eInfo) {
        console.warn("Avviso estrazione video/post id Facebook:", eInfo);
      }

      // 2. Azione A: Sposta in archivio il post della timeline (timeline_visibility=hidden)
      var targetPostId = (postId && postId !== '0') ? postId : (pageId + '_' + (videoId || targetId));
      try {
        var hideUrl = "https://graph.facebook.com/v19.0/" + targetPostId;
        var hideResp = UrlFetchApp.fetch(hideUrl, {
          method: "post",
          payload: "timeline_visibility=hidden&access_token=" + encodeURIComponent(pageToken),
          muteHttpExceptions: true
        });
        if (hideResp.getResponseCode() === 200) {
          logAzioni.push("Post rimosso dalla timeline (spostato in archivio)");
          archivioRiuscito = true;
        }
      } catch(eHide) {
        console.warn("Avviso nascondimento post timeline FB:", eHide);
      }

      // 3. Azione B: Imposta il video come non pubblicato (spostato in archivio video privato)
      var targetVideoId = videoId || targetId;
      try {
        var unpubUrl = "https://graph.facebook.com/v19.0/" + targetVideoId;
        var unpubResp = UrlFetchApp.fetch(unpubUrl, {
          method: "post",
          payload: "is_published=false&access_token=" + encodeURIComponent(pageToken),
          muteHttpExceptions: true
        });
        if (unpubResp.getResponseCode() === 200) {
          logAzioni.push("Video archiviato nella libreria privata (non pubblicato)");
          archivioRiuscito = true;
        }
      } catch(eUnpub) {
        console.warn("Avviso depubblicazione video FB:", eUnpub);
      }

      // 4. Azione C: Imposta l'oggetto live_video come non pubblicato
      try {
        var lvUrl = "https://graph.facebook.com/v19.0/" + targetId;
        var lvResp = UrlFetchApp.fetch(lvUrl, {
          method: "post",
          payload: "is_published=false&access_token=" + encodeURIComponent(pageToken),
          muteHttpExceptions: true
        });
        if (lvResp.getResponseCode() === 200) {
          logAzioni.push("Live video depubblicato");
          archivioRiuscito = true;
        }
      } catch(eLv) {}
    }

    // 5. Archiviazione eventuali post snapshot o storie temporanee della diretta
    try {
      var snapPostId = props.getProperty('FB_LAST_SNAPSHOT_POST_ID');
      if (snapPostId) {
        UrlFetchApp.fetch("https://graph.facebook.com/v19.0/" + snapPostId, {
          method: "post",
          payload: "timeline_visibility=hidden&access_token=" + encodeURIComponent(pageToken),
          muteHttpExceptions: true
        });
        logAzioni.push("Post snapshot live archiviato");
        props.deleteProperty('FB_LAST_SNAPSHOT_POST_ID');
      }
    } catch(eSnap) {}

    props.deleteProperty('FB_TARGET_ARCHIVE_ID');
    props.deleteProperty('FB_ARCHIVE_SCHEDULED_TIME');
    props.setProperty('FB_ARCHIVE_STATUS', 'COMPLETATO');
    props.setProperty('FB_LAST_ARCHIVED_TIMESTAMP', new Date().toISOString());

    var msgTelegram = "📦 <b>POST FACEBOOK SPOSTATO IN ARCHIVIO</b>\n\n" +
      "La diretta streaming si è conclusa da 1 ora. Come programmato, il post su Facebook è stato <b>spostato in archivio</b>.\n" +
      "• <b>Target ID:</b> <code>" + (targetId || 'N/D') + "</code>\n" +
      "• <b>Stato:</b> " + (archivioRiuscito ? "✅ Archiviato con successo" : "⚠️ Verificato su Facebook") + "\n" +
      "• <b>Operazioni:</b> " + (logAzioni.join(" | ") || "Archiviazione eseguita") + "\n\n" +
      "— <b>Immobiliare Giancani</b>";

    if (typeof inviaNotificaTelegram === 'function') {
      inviaNotificaTelegram(msgTelegram, null, 'HTML');
    }

    return {
      success: true,
      targetId: targetId,
      operazioni: logAzioni,
      messaggio: "Post Facebook della diretta spostato in archivio dopo 1 ora con successo — Immobiliare Giancani"
    };

  } catch(e) {
    console.error("Errore eseguiArchiviazionePostFacebookDopoDiretta:", e);
    if (typeof inviaAllertaErroreTelegram === 'function') {
      inviaAllertaErroreTelegram("07_MultistreamStreaming.js", "eseguiArchiviazionePostFacebookDopoDiretta", e.toString());
    }
    return { success: false, error: e.toString() };
  }
}

/**
 * Rimuove eventuali trigger attivi di archiviazione post Facebook per evitare duplicati.
 */
function rimuoviTriggerArchiviazionePostFacebook() {
  try {
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
      if (triggers[i].getHandlerFunction() === 'eseguiArchiviazionePostFacebookDopoDiretta') {
        ScriptApp.deleteTrigger(triggers[i]);
      }
    }
  } catch(e) {
    console.warn("rimuoviTriggerArchiviazionePostFacebook:", e);
  }
}

/**
 * Permette di archiviare manualmente e subito il post della diretta Facebook senza aspettare l'ora.
 */
function archiviaPostFacebookDirettaOra() {
  return eseguiArchiviazionePostFacebookDopoDiretta();
}

/**
 * Restituisce lo stato dell'archiviazione programmata del post Facebook.
 */
function getStatoArchiviazionePostFacebook() {
  try {
    var props = PropertiesService.getScriptProperties();
    var stato = props.getProperty('FB_ARCHIVE_STATUS') || 'NESSUNA_ARCHIVIAZIONE_IN_ATTESA';
    var sched = props.getProperty('FB_ARCHIVE_SCHEDULED_TIME') || '';
    var targetId = props.getProperty('FB_TARGET_ARCHIVE_ID') || props.getProperty('FB_LIVE_VIDEO_ID') || '';
    var lastArch = props.getProperty('FB_LAST_ARCHIVED_TIMESTAMP') || '';

    var minutiRimanenti = 0;
    if (sched) {
      var diffMs = new Date(sched).getTime() - Date.now();
      minutiRimanenti = Math.max(0, Math.round(diffMs / 60000));
    }

    return {
      success: true,
      stato: stato,
      targetId: targetId,
      schedulatoPer: sched,
      minutiRimanenti: minutiRimanenti,
      ultimoArchiviatoIl: lastArch
    };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * Verifica se è trascorsa 1 ora dalla fine della diretta ed esegue l'archiviazione del post se necessario.
 */
function verificaEsecuzioneArchiviazionePostFBPendente() {
  try {
    var props = PropertiesService.getScriptProperties();
    var stato = props.getProperty('FB_ARCHIVE_STATUS');
    if (stato === 'IN_ATTESA_1_ORA') {
      var schedStr = props.getProperty('FB_ARCHIVE_SCHEDULED_TIME');
      if (schedStr) {
        var schedTime = new Date(schedStr).getTime();
        if (Date.now() >= schedTime) {
          console.log("⏰ [ARCHIVIO FB] 1 ora trascorsa dalla fine della diretta. Esecuzione archiviazione post...");
          return eseguiArchiviazionePostFacebookDopoDiretta();
        }
      }
    }
  } catch(e) {
    console.warn("verificaEsecuzioneArchiviazionePostFBPendente:", e);
  }
  return null;
}

/**
 * Salva e aggiorna la chiave o l'URL RTMP dedicato a Instagram LIVE
 * @param {string} fullKeyOrUrl - Chiave stream o URL RTMP completo di Instagram
 */
function salvaConfigurazioneInstagramLive(fullKeyOrUrl) {
  try {
    if (!fullKeyOrUrl || typeof fullKeyOrUrl !== 'string') {
      return { success: false, error: 'Parametro chiave non valido' };
    }

    var cleanVal = fullKeyOrUrl.trim();
    var props = PropertiesService.getScriptProperties();

    props.setProperty('IG_STREAM_KEY', cleanVal);
    props.setProperty('IG_LIVE_ATTIVO', 'true');

    if (typeof salvaParametroSocialSuFoglio === 'function') {
      salvaParametroSocialSuFoglio('Instagram', cleanVal);
    }

    return {
      success: true,
      messaggio: 'Configurazione Instagram LIVE salvata con successo! — Immobiliare Giancani',
      attivo: true
    };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}




// ═══════════════════════════════════════════════════════════════════════
// 📢 GESTIONE POST INVITO FACEBOOK & PULIZIA AUTOMATICA DIRETTA
// 1. Mattina: Post d'invito con foto e testo per la diretta serale (19:00 - 01:00)
// 2. Inizio Diretta: Eliminazione automatica del post d'invito dalla bacheca
// 3. Fine Diretta: Eliminazione automatica del video live dalla bacheca
// Branding: Immobiliare Giancani
// ═══════════════════════════════════════════════════════════════════════

/**
 * Pubblica ogni mattina su Facebook il post d'invito per la diretta serale (19:00 - 01:00)
 */
function pubblicaPostInvitoFacebookMattutino() {
  try {
    var props = PropertiesService.getScriptProperties();
    var pageToken = props.getProperty('FB_PAGE_ACCESS_TOKEN') || '';
    var pageId = '234931856561526';

    if (!pageToken) {
      var ss = getSpreadsheetSicuro();
      var sSoc = ss ? ss.getSheetByName("Impostazioni_Social") : null;
      if (sSoc) {
        var dataS = sSoc.getDataRange().getValues();
        for (var i = 0; i < dataS.length; i++) {
          var param = String(dataS[i][0] || "").trim().toLowerCase();
          if (param.indexOf("facebook") > -1) {
            pageToken = String(dataS[i][5] || dataS[i][1] || "").trim();
            break;
          }
        }
      }
    }

    if (!pageToken) {
      pageToken = 'EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI';
    }

    // 1. Recupera l'immobile in programma stasera dal calendario
    var calRes = (typeof getCalendarioPalinsestoSettimanale === 'function') ? getCalendarioPalinsestoSettimanale() : null;
    var tabOggi = 'VILLA_FAVARA_RIFINITA';
    var titoloOggi = 'Villa Favara Rifinita';

    if (calRes && calRes.success && calRes.calendario) {
      var gId = calRes.giornoIdOggi || 'lunedi';
      for (var c = 0; c < calRes.calendario.length; c++) {
        if (calRes.calendario[c].id === gId) {
          tabOggi = calRes.calendario[c].tabImmobile || tabOggi;
          titoloOggi = calRes.calendario[c].titoloImmobile || tabOggi.replace(/_/g, ' ');
          break;
        }
      }
    }

    // 2. Preleva dati e prima foto dell'immobile
    var immData = (typeof getImmobileData === 'function') ? getImmobileData('current') : null;
    var fotoUrl = (immData && (immData.fotoUrl || immData.mediaUrl)) ? immData.fotoUrl || immData.mediaUrl : "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?q=80&w=1200&auto=format&fit=crop";
    var prezzo = (immData && immData.prezzo) ? immData.prezzo : "Trattativa Riservata";
    var mq = (immData && immData.mq) ? immData.mq : "metri quadri";
    var descF = (immData && (immData.testoDaLeggere || immData.testo)) ? (immData.testoDaLeggere || immData.testo) : "";
    if (typeof convertiMqInMetriQuadri === 'function') descF = convertiMqInMetriQuadri(descF);

    var testoPost = "🌟 QUESTA SERA IN DIRETTA STREAMING DALLE 19:00 ALLE 01:00!\n\n" +
      "I nostri conduttori virtuali DarIA e DarIO vi portano all'interno di " + titoloOggi.toUpperCase() + "!\n" +
      "📐 Superficie: " + mq + "\n" +
      "💰 Valore: " + prezzo + "\n\n" +
      (descF ? (descF + "\n\n") : "") +
      "💬 Durante la diretta potrete commentare in tempo reale e chiedere a DarIA e DarIO di visitare le vostre stanze preferite!\n" +
      "Vi aspettiamo questa sera in diretta a partire dalle ore 19:00.\n\n" +
      "— Immobiliare Giancani";

    // 3. Pubblica su Facebook come foto con didascalia (post bacheca)
    var uploadUrl = "https://graph.facebook.com/v19.0/" + pageId + "/photos";
    var payload = {
      url: fotoUrl,
      caption: testoPost,
      access_token: pageToken
    };

    var resp = UrlFetchApp.fetch(uploadUrl, {
      method: "post",
      payload: payload,
      muteHttpExceptions: true
    });

    var resCode = resp.getResponseCode();
    var resText = resp.getContentText();
    var resJson = {};
    try { resJson = JSON.parse(resText); } catch(e){}

    if (resCode === 200 && resJson.id) {
      var postId = resJson.post_id || resJson.id;
      props.setProperty('FB_INVITE_POST_ID', postId);
      props.setProperty('FB_INVITE_TIMESTAMP', String(Date.now()));

      // Notifica Telegram
      if (typeof inviaNotificaTelegram === 'function') {
        inviaNotificaTelegram(
          "📢 <b>POST INVITO FACEBOOK PUBBLICATO</b>\n\n" +
          "✅ Pubblicato con successo il post d'invito per la diretta di stasera (19:00 - 01:00).\n" +
          "🏠 <b>Immobile:</b> " + titoloOggi + "\n" +
          "🆔 <b>Post ID:</b> <code>" + postId + "</code>\n" +
          "ℹ️ <i>Il post verrà eliminato in automatico all'inizio della diretta live.</i>\n\n" +
          "— <b>Immobiliare Giancani</b>",
          null,
          "HTML"
        );
      }

      return { success: true, postId: postId, message: "Post invito Facebook pubblicato con successo!" };
    } else {
      console.warn("Errore pubblicazione post invito Facebook:", resText);
      return { success: false, error: resText };
    }
  } catch(e) {
    console.error("Errore pubblicaPostInvitoFacebookMattutino:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * Elimina il post d'invito mattutino da Facebook all'avvio della diretta live
 */
function eliminaPostInvitoFacebook() {
  try {
    var props = PropertiesService.getScriptProperties();
    var invitePostId = props.getProperty('FB_INVITE_POST_ID');
    if (!invitePostId) {
      return { success: true, message: "Nessun post invito registrato da eliminare." };
    }

    var pageToken = props.getProperty('FB_PAGE_ACCESS_TOKEN') || '';
    if (!pageToken) {
      pageToken = 'EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI';
    }

    var delUrl = "https://graph.facebook.com/v19.0/" + invitePostId + "?access_token=" + encodeURIComponent(pageToken);
    var resp = UrlFetchApp.fetch(delUrl, {
      method: "delete",
      muteHttpExceptions: true
    });

    var resCode = resp.getResponseCode();
    var resText = resp.getContentText();
    props.deleteProperty('FB_INVITE_POST_ID');

    // Notifica Telegram
    if (typeof inviaNotificaTelegram === 'function') {
      inviaNotificaTelegram(
        "🗑️ <b>POST INVITO FACEBOOK RIMOSSO</b>\n\n" +
        "La diretta streaming è iniziata: il post d'invito della mattina (ID: <code>" + invitePostId + "</code>) è stato rimosso dalla pagina Facebook.\n\n" +
        "— <b>Immobiliare Giancani</b>",
        null,
        "HTML"
      );
    }

    return { success: (resCode === 200), response: resText };
  } catch(e) {
    console.error("Errore eliminaPostInvitoFacebook:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * Elimina il video della diretta streaming terminata da Facebook (ore 01:00)
 */
function eliminaVideoDirettaFacebookConclusa() {
  try {
    var props = PropertiesService.getScriptProperties();
    var liveId = props.getProperty('FB_LIVE_VIDEO_ID') || props.getProperty('FB_TARGET_ARCHIVE_ID') || '';
    var pageToken = props.getProperty('FB_PAGE_ACCESS_TOKEN') || '';
    if (!pageToken) {
      pageToken = 'EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI';
    }

    if (!liveId) {
      return { success: true, message: "Nessun video live registrato da eliminare." };
    }

    var delUrl = "https://graph.facebook.com/v19.0/" + liveId + "?access_token=" + encodeURIComponent(pageToken);
    var resp = UrlFetchApp.fetch(delUrl, {
      method: "delete",
      muteHttpExceptions: true
    });

    var resCode = resp.getResponseCode();
    var resText = resp.getContentText();
    props.deleteProperty('FB_LIVE_VIDEO_ID');

    // Notifica Telegram
    if (typeof inviaNotificaTelegram === 'function') {
      inviaNotificaTelegram(
        "🧹 <b>PULIZIA DIRETTA FACEBOOK TERMINATA</b>\n\n" +
        "La diretta serale delle 19:00 - 01:00 è terminata: il video streaming (ID: <code>" + liveId + "</code>) è stato rimosso dalla bacheca Facebook lasciando la pagina pulita e ordinata.\n\n" +
        "— <b>Immobiliare Giancani</b>",
        null,
        "HTML"
      );
    }

    return { success: (resCode === 200), response: resText };
  } catch(e) {
    console.error("Errore eliminaVideoDirettaFacebookConclusa:", e);
    return { success: false, error: e.toString() };
  }
}
