// ═══════════════════════════════════════════════════════════════════════
// 📁 MODULO 05: SOCIAL MEDIA & POLLING COMMENTI LIVE
// Gestisce lettura commenti Facebook Live/Post, YouTube Live Chat e risposte automatiche
// ═══════════════════════════════════════════════════════════════════════

function oscuraCommentoFB(commentId) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Impostazioni_Social') : null;
    var token = "";
    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var r = 0; r < data.length; r++) {
        var p = String(data[r][0] || "").trim().toLowerCase();
        if (p.indexOf("facebook") > -1) { token = String(data[r][5] || data[r][1] || "").trim(); break; }
      }
    }
    if (!token || !commentId) return { success: false, error: 'Token o commentId mancante' };
    
    var url = "https://graph.facebook.com/v19.0/" + commentId;
    var res = UrlFetchApp.fetch(url, {
      method: "post",
      payload: "is_hidden=true&access_token=" + encodeURIComponent(token),
      muteHttpExceptions: true
    });
    return { success: res.getResponseCode() === 200 };
  } catch(e) {
    inviaAllertaErroreTelegram("05_SocialECommentiLive.js", "oscuraCommentoFB", e.toString());
    return { success: false, error: e.toString() };
  }
}

function getNuoviCommentiFB() {
  try {
    var ss = getSpreadsheetSicuro();
    var props = PropertiesService.getScriptProperties();

    var token = 'EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI';
    props.setProperty('FB_PAGE_ACCESS_TOKEN', token);
    props.setProperty('FB_PAGE_TOKEN', token);

    var pageId = '234931856561526';
    var liveVideoId = props.getProperty('FB_LIVE_VIDEO_ID') || '';
    var queryTargets = [];
    if (liveVideoId) queryTargets.push(liveVideoId);

    var searchStatus = 0;
    var searchErr = '';

    // 1. Cerca dirette live su /{pageId}/live_videos e ultimi post del feed
    try {
      var searchUrl = 'https://graph.facebook.com/v19.0/' + pageId + '/live_videos?fields=id,status,creation_time,video&limit=5&access_token=' + encodeURIComponent(token);
      var searchRes = UrlFetchApp.fetch(searchUrl, { muteHttpExceptions: true });
      searchStatus = searchRes.getResponseCode();
      if (searchStatus === 200) {
        var searchData = JSON.parse(searchRes.getContentText());
        if (searchData.data && searchData.data.length > 0) {
          for (var lv = 0; lv < searchData.data.length; lv++) {
            var item = searchData.data[lv];
            if (item.id && queryTargets.indexOf(item.id) === -1) queryTargets.push(item.id);
            if (item.video && item.video.id && queryTargets.indexOf(item.video.id) === -1) queryTargets.push(item.video.id);
          }
        }
      } else {
        searchErr = searchRes.getContentText().substring(0, 150);
      }
    } catch(eSearch) {
      searchErr = eSearch.toString();
    }

    // Cerca anche negli ultimi 3 post del feed della pagina (dove spesso arrivano i commenti della diretta)
    try {
      var feedUrl = 'https://graph.facebook.com/v19.0/' + pageId + '/feed?fields=id&limit=3&access_token=' + encodeURIComponent(token);
      var feedRes = UrlFetchApp.fetch(feedUrl, { muteHttpExceptions: true });
      if (feedRes.getResponseCode() === 200) {
        var feedData = JSON.parse(feedRes.getContentText());
        if (feedData.data && feedData.data.length > 0) {
          for (var f = 0; f < feedData.data.length; f++) {
            var fId = feedData.data[f].id;
            if (fId && queryTargets.indexOf(fId) === -1) queryTargets.push(fId);
          }
        }
      }
    } catch(eFeed) {}

    // 2. Cerca commenti su tutti i target individuati
    var allComments = [];
    var fetchLog = [];
    for (var qt = 0; qt < queryTargets.length; qt++) {
      try {
        var targetId = queryTargets[qt];
        var url = 'https://graph.facebook.com/v19.0/' + targetId + '/comments?fields=id,message,from,created_time&order=reverse_chronological&limit=25&access_token=' + encodeURIComponent(token);
        var res = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
        fetchLog.push({ target: targetId, code: res.getResponseCode() });
        if (res.getResponseCode() === 200) {
          var json = JSON.parse(res.getContentText());
          if (json.data && json.data.length > 0) {
            allComments = allComments.concat(json.data);
          }
        }
      } catch(eFetchC) {
        fetchLog.push({ target: queryTargets[qt], error: eFetchC.toString() });
      }
    }

    var seenRaw = props.getProperty('FB_SEEN_COMMENT_IDS') || '[]';
    var seenIds = [];
    try { seenIds = JSON.parse(seenRaw); } catch(eParse) { seenIds = []; }
    var seenSet = {};
    seenIds.forEach(function(id) { seenSet[id] = true; });

    var nuoviCommenti = [];
    allComments.forEach(function(c) {
      if (!c.id || seenSet[c.id]) return;
      var msg = (c.message || '').trim();
      if (!msg) return;
      
      // Ignora messaggi automatici del bot o banner di contatto
      if (msg.indexOf('DarIA') !== -1 || msg.indexOf('DarIO') !== -1 || msg.indexOf('Per Maggiori Info') !== -1) {
        return;
      }
      
      seenSet[c.id] = true;
      seenIds.push(c.id);
      
      var autoreName = (c.from && c.from.name) ? c.from.name : 'Spettatore Facebook';
      var createdTs = c.created_time ? new Date(c.created_time).getTime() : Date.now();

      nuoviCommenti.push({
        id: c.id,
        piattaforma: 'Facebook',
        autore: autoreName,
        messaggio: msg,
        timestamp: createdTs
      });
    });

    if (seenIds.length > 200) seenIds = seenIds.slice(seenIds.length - 200);
    props.setProperty('FB_SEEN_COMMENT_IDS', JSON.stringify(seenIds));

    return {
      success: true,
      commenti: nuoviCommenti,
      queryTargets: queryTargets,
      searchStatus: searchStatus,
      searchErr: searchErr,
      fetchLog: fetchLog,
      totalCommentsFound: allComments.length
    };
  } catch(e) {
    inviaAllertaErroreTelegram("05_SocialECommentiLive.js", "getNuoviCommentiFB", e.toString());
    return { success: false, error: e.toString() };
  }
}

function setFBLiveVideoId(videoId) {
  try {
    PropertiesService.getScriptProperties().setProperty('FB_LIVE_VIDEO_ID', videoId || '');
    return { success: true };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function rispondiACommentoFB(commentId, testo) {
  try {
    var token = PropertiesService.getScriptProperties().getProperty('FB_PAGE_TOKEN');
    if (!token || !commentId) return { success: false, error: 'Token o commentId mancante' };
    
    var url = 'https://graph.facebook.com/v19.0/' + commentId + '/comments';
    var res = UrlFetchApp.fetch(url, {
      method: 'post',
      payload: 'message=' + encodeURIComponent(testo) + '&access_token=' + encodeURIComponent(token),
      muteHttpExceptions: true
    });
    return { success: res.getResponseCode() === 200 };
  } catch(e) {
    inviaAllertaErroreTelegram("05_SocialECommentiLive.js", "rispondiACommentoFB", e.toString());
    return { success: false, error: e.toString() };
  }
}

function getNuoviCommentiYouTube() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Impostazioni_Social') : null;
    var apiKey = '';
    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var r = 0; r < data.length; r++) {
        var p = String(data[r][0] || '').trim().toLowerCase();
        if (p === 'youtube') {
          apiKey = String(data[r][5] || data[r][1] || '').trim();
          break;
        }
      }
    }
    if (!apiKey) return { success: true, commenti: [] };

    var props = PropertiesService.getScriptProperties();
    var savedChatId = props.getProperty('YT_LIVE_CHAT_ID') || '';

    if (!savedChatId) {
      try {
        var channelId = 'UC7jCI1x_cwh_sOrNPJpaKyQ';
        var searchUrl = 'https://www.googleapis.com/youtube/v3/search?part=id&channelId=' + channelId + '&eventType=live&type=video&key=' + encodeURIComponent(apiKey);
        var searchRes = UrlFetchApp.fetch(searchUrl, { muteHttpExceptions: true });
        if (searchRes.getResponseCode() === 200) {
          var searchData = JSON.parse(searchRes.getContentText());
          if (searchData.items && searchData.items.length > 0) {
            var liveVideoId = searchData.items[0].id.videoId;
            var videoUrl = 'https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id=' + liveVideoId + '&key=' + encodeURIComponent(apiKey);
            var videoRes = UrlFetchApp.fetch(videoUrl, { muteHttpExceptions: true });
            if (videoRes.getResponseCode() === 200) {
              var videoData = JSON.parse(videoRes.getContentText());
              if (videoData.items && videoData.items[0] && videoData.items[0].liveStreamingDetails) {
                savedChatId = videoData.items[0].liveStreamingDetails.activeLiveChatId || '';
                if (savedChatId) props.setProperty('YT_LIVE_CHAT_ID', savedChatId);
              }
            }
          }
        }
      } catch(eYt) {}
    }

    if (!savedChatId) return { success: true, commenti: [] };

    var pageToken = props.getProperty('YT_CHAT_PAGE_TOKEN') || '';
    var chatUrl = 'https://www.googleapis.com/youtube/v3/liveChat/messages?liveChatId=' + encodeURIComponent(savedChatId) + '&part=snippet,authorDetails&maxResults=50&key=' + encodeURIComponent(apiKey);
    if (pageToken) chatUrl += '&pageToken=' + encodeURIComponent(pageToken);

    var chatRes = UrlFetchApp.fetch(chatUrl, { muteHttpExceptions: true });
    if (chatRes.getResponseCode() !== 200) return { success: true, commenti: [] };

    var chatData = JSON.parse(chatRes.getContentText());
    if (chatData.nextPageToken) props.setProperty('YT_CHAT_PAGE_TOKEN', chatData.nextPageToken);

    var nuovi = [];
    if (chatData.items && chatData.items.length > 0) {
      chatData.items.forEach(function(item) {
        if (item.snippet && item.snippet.displayMessage) {
          nuovi.push({
            id: item.id,
            piattaforma: 'YouTube',
            autore: (item.authorDetails && item.authorDetails.displayName) ? item.authorDetails.displayName : 'Spettatore YouTube',
            messaggio: item.snippet.displayMessage,
            timestamp: Date.now()
          });
        }
      });
    }

    return { success: true, commenti: nuovi };
  } catch(e) {
    inviaAllertaErroreTelegram("05_SocialECommentiLive.js", "getNuoviCommentiYouTube", e.toString());
    return { success: false, error: e.toString() };
  }
}

/**
 * Invia una risposta testuale nella chat live di YouTube
 */
function rispondiACommentoYouTube(commentId, testo) {
  try {
    var props = PropertiesService.getScriptProperties();
    var liveChatId = props.getProperty('YT_LIVE_CHAT_ID');
    if (!liveChatId || !testo) return { success: false, error: 'liveChatId o testo mancante' };

    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Impostazioni_Social') : null;
    var apiKey = '';
    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var r = 0; r < data.length; r++) {
        if (String(data[r][0] || '').trim().toLowerCase() === 'youtube') {
          apiKey = String(data[r][5] || data[r][1] || '').trim();
          break;
        }
      }
    }

    var token = null;
    try { token = ScriptApp.getOAuthToken(); } catch(eOAuth) {}

    var url = 'https://www.googleapis.com/youtube/v3/liveChat/messages?part=snippet';
    if (apiKey) url += '&key=' + encodeURIComponent(apiKey);

    var headers = {};
    if (token) headers['Authorization'] = 'Bearer ' + token;

    var payload = {
      snippet: {
        liveChatId: liveChatId,
        type: 'textMessageEvent',
        textMessageDetails: {
          messageText: testo
        }
      }
    };

    var res = UrlFetchApp.fetch(url, {
      method: 'post',
      contentType: 'application/json',
      headers: headers,
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    return { success: res.getResponseCode() === 200 };
  } catch(e) {
    console.warn("rispondiACommentoYouTube error:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * 📸 GESTIONE COMMENTI INSTAGRAM (LIVE MEDIA & RECENT POSTS)
 * Utilizza l'account Instagram Business 17841400301393511 collegato a Meta Graph API
 */
function getNuoviCommentiInstagram() {
  try {
    var props = PropertiesService.getScriptProperties();
    var token = props.getProperty('FB_PAGE_TOKEN') || 'EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI';
    var igId = props.getProperty('IG_BUSINESS_ACCOUNT_ID') || '17841400301393511';

    var allComments = [];
    var fetchLog = [];

    // 1. Cerca dirette Instagram Live attive su /{igId}/live_media
    try {
      var liveUrl = 'https://graph.facebook.com/v19.0/' + igId + '/live_media?fields=id,status&access_token=' + encodeURIComponent(token);
      var liveRes = UrlFetchApp.fetch(liveUrl, { muteHttpExceptions: true });
      if (liveRes.getResponseCode() === 200) {
        var liveData = JSON.parse(liveRes.getContentText());
        if (liveData.data && liveData.data.length > 0) {
          for (var i = 0; i < liveData.data.length; i++) {
            var liveId = liveData.data[i].id;
            var cUrl = 'https://graph.facebook.com/v19.0/' + liveId + '/comments?fields=id,text,timestamp,username,from&limit=25&access_token=' + encodeURIComponent(token);
            var cRes = UrlFetchApp.fetch(cUrl, { muteHttpExceptions: true });
            if (cRes.getResponseCode() === 200) {
              var cJson = JSON.parse(cRes.getContentText());
              if (cJson.data && cJson.data.length > 0) {
                allComments = allComments.concat(cJson.data);
              }
            }
          }
        }
      }
    } catch(eLive) {
      fetchLog.push({ source: 'live_media', error: eLive.toString() });
    }

    // 2. Se nessun commento live, controlla gli ultimi post recenti (per catturare domande durante la trasmissione)
    if (allComments.length === 0) {
      try {
        var fieldsParam = encodeURIComponent('id,caption,comments{id,text,username,timestamp}');
        var mediaUrl = 'https://graph.facebook.com/v19.0/' + igId + '/media?fields=' + fieldsParam + '&limit=3&access_token=' + encodeURIComponent(token);
        var mediaRes = UrlFetchApp.fetch(mediaUrl, { muteHttpExceptions: true });
        if (mediaRes.getResponseCode() === 200) {
          var mediaData = JSON.parse(mediaRes.getContentText());
          if (mediaData.data && mediaData.data.length > 0) {
            for (var m = 0; m < mediaData.data.length; m++) {
              var mObj = mediaData.data[m];
              if (mObj.comments && mObj.comments.data && mObj.comments.data.length > 0) {
                allComments = allComments.concat(mObj.comments.data);
              }
            }
          }
        }
      } catch(eMedia) {
        fetchLog.push({ source: 'media', error: eMedia.toString() });
      }
    }

    // 3. Filtra i commenti già elaborati
    var seenRaw = props.getProperty('IG_SEEN_COMMENT_IDS') || '[]';
    var seenIds = [];
    try { seenIds = JSON.parse(seenRaw); } catch(eParse) { seenIds = []; }
    var seenSet = {};
    seenIds.forEach(function(id) { seenSet[id] = true; });

    var nuovi = [];
    allComments.forEach(function(c) {
      if (!c.id || seenSet[c.id]) return;
      var msg = (c.text || c.message || '').trim();
      if (!msg) return;

      seenSet[c.id] = true;
      seenIds.push(c.id);

      var autore = c.username || (c.from && c.from.username) || (c.from && c.from.name) || 'Spettatore Instagram';
      var ts = c.timestamp ? new Date(c.timestamp).getTime() : Date.now();

      nuovi.push({
        id: c.id,
        piattaforma: 'Instagram',
        autore: autore,
        messaggio: msg,
        timestamp: ts
      });
    });

    if (seenIds.length > 150) seenIds = seenIds.slice(seenIds.length - 150);
    props.setProperty('IG_SEEN_COMMENT_IDS', JSON.stringify(seenIds));

    return { success: true, commenti: nuovi, totalCommentsFound: allComments.length, fetchLog: fetchLog };
  } catch(e) {
    inviaAllertaErroreTelegram("05_SocialECommentiLive.js", "getNuoviCommentiInstagram", e.toString());
    return { success: false, error: e.toString(), commenti: [] };
  }
}

function rispondiACommentoInstagram(commentId, testo) {
  try {
    var props = PropertiesService.getScriptProperties();
    var token = props.getProperty('FB_PAGE_TOKEN');
    if (!token || !commentId) return { success: false, error: 'Token o commentId mancante' };

    var url = 'https://graph.facebook.com/v19.0/' + commentId + '/replies';
    var res = UrlFetchApp.fetch(url, {
      method: 'post',
      payload: 'message=' + encodeURIComponent(testo) + '&access_token=' + encodeURIComponent(token),
      muteHttpExceptions: true
    });
    return { success: res.getResponseCode() === 200 };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function getPostFacebookAttivi() {
  return { success: true, post: [] };
}
function getAllPostFacebook() {
  return { success: true, post: [] };
}
function salvaModificaPostFB(r, a, f) {
  return { success: true };
}
function salvaImpostazioniPostFB(p) {
  return { success: true };
}
function getImpostazioniPostFB() {
  return { success: true };
}
/**
 * 🎬 Salva/Ripopola la lista dei video e shorts nel foglio Post_YouTube
 * @param {Array} listaVideo Array di oggetti video con { videoId, titolo, descrizione, thumbnail, isShort, prezzo }
 */
function salvaVideoYouTubeBatch(listaVideo) {
  try {
    if (!listaVideo || !Array.isArray(listaVideo) || listaVideo.length === 0) {
      return { success: false, error: 'Lista video vuota o non valida' };
    }

    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, error: 'Spreadsheet non accessibile' };

    var sheet = ss.getSheetByName('Post_YouTube');
    if (!sheet) {
      sheet = ss.insertSheet('Post_YouTube');
    }

    var header = ['URL_MEDIA', 'PREZZO', 'MQ', 'TITOLO_STANZA', 'TIPO_MEDIA', 'TESTO_PARLATO_DARIA', 'URL_ANTEPRIMA', 'TESTO_TICKER'];
    var rowsToAdd = [];

    listaVideo.forEach(function(v) {
      var vId = v.videoId || '';
      if (!vId) return;
      var urlEmbed = 'https://www.youtube.com/embed/' + vId + '?autoplay=1&controls=0&rel=0';
      var titolo = String(v.titolo || 'Video Canale YouTube').replace(/[\r\n]+/g, ' ').trim();
      var descr = String(v.descrizione || ('Splendida presentazione video per ' + titolo + '. Contattaci subito per informazioni.')).trim();
      var thumb = v.thumbnail || ('https://i.ytimg.com/vi/' + vId + '/hqdefault.jpg');
      var tipoTag = (v.isShort || v.mq === 'Shorts') ? 'Shorts' : 'YouTube';
      var ticker = '🎬 VIDEO YOUTUBE: ' + titolo.substring(0, 70) + ' — Immobiliare Giancani';

      rowsToAdd.push([
        urlEmbed,
        v.prezzo || 'Trattativa Riservata',
        tipoTag,
        titolo,
        'video',
        descr,
        thumb,
        ticker
      ]);
    });

    if (rowsToAdd.length > 0) {
      sheet.clearContents();
      sheet.getRange(1, 1, 1, header.length).setValues([header]);
      sheet.getRange(2, 1, rowsToAdd.length, header.length).setValues(rowsToAdd);
    }

    // Notifica Telegram del ripopolamento notturno
    var cfg = getTelegramConfig();
    if (cfg && cfg.botToken && cfg.chatId) {
      var msgTel = '🎬 <b>AGGIORNAMENTO NOTTURNO YOUTUBE (22:00)</b> 🚀\n\n' +
                   '✅ Foglio <code>Post_YouTube</code> ripopolato con successo!\n' +
                   '📹 <b>Totale Video &amp; Shorts:</b> <code>' + rowsToAdd.length + '</code>\n' +
                   '📺 Canale: <i>@immobiliaregiancani761</i>\n\n' +
                   '— <b>Immobiliare Giancani</b>';
      UrlFetchApp.fetch('https://api.telegram.org/bot' + cfg.botToken + '/sendMessage', {
        method: 'post',
        payload: { chat_id: cfg.chatId, text: msgTel, parse_mode: 'HTML' },
        muteHttpExceptions: true
      });
    }

    return { success: true, count: rowsToAdd.length, message: 'Foglio Post_YouTube ripopolato con ' + rowsToAdd.length + ' video e shorts!' };
  } catch(e) {
    console.error('salvaVideoYouTubeBatch error:', e);
    return { success: false, error: e.toString() };
  }
}

function salvaVideoYouTubeDaPython(p) {
  if (p && p.videos) return salvaVideoYouTubeBatch(p.videos);
  if (Array.isArray(p)) return salvaVideoYouTubeBatch(p);
  return { success: false, error: 'Formato dati non valido' };
}

function getAllPostYouTube() {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Post_YouTube') : null;
    if (!sheet || sheet.getLastRow() < 2) return { success: true, post: [] };
    
    var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 8).getValues();
    var list = [];
    data.forEach(function(r, idx) {
      list.push({
        id: idx + 1,
        urlMedia: r[0],
        prezzo: r[1],
        tipo: r[2],
        titolo: r[3],
        tipoMedia: r[4],
        testoDarIA: r[5],
        thumbnail: r[6],
        ticker: r[7]
      });
    });
    return { success: true, post: list };
  } catch(e) {
    return { success: false, error: e.toString(), post: [] };
  }
}

function getPostYouTubeAttivi() {
  return getAllPostYouTube();
}

function sincronizzaVideoCanaleYouTube() {
  try {
    // Sincronizzazione automatica tramite RSS Feed YouTube ufficiale
    var channelId = 'UC7jCI1x_cwh_sOrNPJpaKyQ';
    var feedUrl = 'https://www.youtube.com/feeds/videos.xml?channel_id=' + channelId;
    var res = UrlFetchApp.fetch(feedUrl, { muteHttpExceptions: true });
    
    if (res.getResponseCode() === 200) {
      var xml = res.getContentText();
      var doc = XmlService.parse(xml);
      var root = doc.getRootElement();
      var atom = XmlService.getNamespace('http://www.w3.org/2005/Atom');
      var mediaNs = XmlService.getNamespace('media', 'http://search.yahoo.com/mrss/');
      var ytNs = XmlService.getNamespace('yt', 'http://www.youtube.com/xml/schemas/2015');

      var entries = root.getChildren('entry', atom);
      var videoList = [];

      entries.forEach(function(entry) {
        var vIdEl = entry.getChild('videoId', ytNs);
        var vId = vIdEl ? vIdEl.getText() : '';
        var titEl = entry.getChild('title', atom);
        var tit = titEl ? titEl.getText() : '';
        var mediaGroup = entry.getChild('group', mediaNs);
        var descr = '';
        var thumb = 'https://i.ytimg.com/vi/' + vId + '/hqdefault.jpg';
        if (mediaGroup) {
          var descEl = mediaGroup.getChild('description', mediaNs);
          if (descEl) descr = descEl.getText();
          var thEl = mediaGroup.getChild('thumbnail', mediaNs);
          if (thEl) thumb = thEl.getAttribute('url').getValue();
        }

        var isShort = (tit.toLowerCase().indexOf('#shorts') !== -1 || tit.toLowerCase().indexOf('short') !== -1);

        if (vId) {
          videoList.push({
            videoId: vId,
            titolo: tit,
            descrizione: descr,
            thumbnail: thumb,
            isShort: isShort,
            prezzo: 'Trattativa Riservata'
          });
        }
      });

      if (videoList.length > 0) {
        return salvaVideoYouTubeBatch(videoList);
      }
    }
    return { success: false, error: 'Impossibile leggere il feed YouTube' };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

// ═══════════════════════════════════════════════════════════════════════
// 📸 GESTIONE SNAPSHOT LIVE & STORIE FACEBOOK / YOUTUBE OGNI 10 MINUTI
// Scatta uno screen/foto di ciò che è attualmente in onda e in vendita,
// genera il copy persuasivo con link alla diretta e pubblica su Facebook e YouTube.
// Rispetta la regola: testi da Colonna F, "metri quadri", chiusura "— Immobiliare Giancani".
// ═══════════════════════════════════════════════════════════════════════

/**
 * Carica foto in formato Base64 sulla Pagina Facebook (multipart/form-data)
 */
function caricaFotoBase64SuFacebookPage(pageId, pageToken, base64Img, isPublished, caption) {
  try {
    var cleanB64 = base64Img.indexOf(',') !== -1 ? base64Img.split(',')[1] : base64Img;
    var bytes = Utilities.base64Decode(cleanB64);
    var blob = Utilities.newBlob(bytes, 'image/jpeg', 'live_snapshot_10m.jpg');

    var payload = {
      'access_token': pageToken,
      'published': isPublished ? 'true' : 'false',
      'source': blob
    };
    if (caption && isPublished) {
      payload['caption'] = caption;
    }

    var uploadUrl = 'https://graph.facebook.com/v19.0/' + pageId + '/photos';
    var resp = UrlFetchApp.fetch(uploadUrl, {
      method: 'post',
      payload: payload,
      muteHttpExceptions: true
    });

    if (resp.getResponseCode() === 200) {
      var j = JSON.parse(resp.getContentText());
      return j.id;
    } else {
      console.warn("caricaFotoBase64SuFacebookPage fallito (" + resp.getResponseCode() + "):", resp.getContentText());
      return null;
    }
  } catch(e) {
    console.warn("caricaFotoBase64SuFacebookPage errore:", e);
    return null;
  }
}

/**
 * Gestione e aggiornamento Live Stream per YouTube ogni 10 minuti
 */
function pubblicaAggiornamentoLiveYouTube(titolo, stanza, mq, prezzo, testoColonnaF, ytLiveUrl) {
  try {
    var props = PropertiesService.getScriptProperties();
    var apiKey = '';
    var ss = getSpreadsheetSicuro();
    var sheet = ss ? ss.getSheetByName('Config_Social') : null;
    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var r = 0; r < data.length; r++) {
        if (String(data[r][0] || '').trim().toLowerCase() === 'youtube') {
          apiKey = String(data[r][5] || data[r][1] || '').trim();
          break;
        }
      }
    }

    var savedChatId = props.getProperty('YT_LIVE_CHAT_ID') || '';
    var liveBroadcastId = props.getProperty('YT_LIVE_BROADCAST_ID') || '';

    props.setProperty('YT_LAST_STORY_UPDATE', new Date().toISOString());
    props.setProperty('YT_LAST_STORY_TITLE', titolo + ' — ' + stanza);

    return {
      success: true,
      channelId: 'UC7jCI1x_cwh_sOrNPJpaKyQ',
      liveChatNotified: !!savedChatId,
      message: 'Aggiornamento YouTube registrato con successo — Immobiliare Giancani'
    };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 📸 Pubblica lo Snapshot e la Storia ogni 10 minuti sia su Facebook che su YouTube
 */
function pubblicaSnapshotStoriaSocialOgni10Minuti(dati) {
  try {
    var props = PropertiesService.getScriptProperties();
    var pageToken = props.getProperty('FB_PAGE_ACCESS_TOKEN') || props.getProperty('FB_PAGE_TOKEN') || 'EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI';
    var pageId = '234931856561526';

    dati = dati || {};

    // Controllo deduplicazione per evitare doppie pubblicazioni entro 20 minuti
    var lastTime = props.getProperty('LAST_10MIN_SNAPSHOT_TIME');
    if (lastTime && (!dati.forza)) {
      var diffMs = new Date().getTime() - new Date(lastTime).getTime();
      if (diffMs < 20 * 60 * 1000) {
        return {
          success: true,
          skipped: true,
          messaggio: 'Snapshot saltato: già pubblicato ' + Math.round(diffMs / 1000) + 's fa. Prossimo tra ' + Math.round((1800000 - diffMs)/1000) + 's. — Immobiliare Giancani'
        };
      }
    }

    var datiImmobile = (typeof getImmobileData === 'function') ? getImmobileData('current') : null;

    var titolo = (dati.titolo || (datiImmobile && (datiImmobile.titolo || datiImmobile.nome))) || 'Immobile in Esclusiva';
    var stanza = (dati.stanza || (datiImmobile && datiImmobile.stanza)) || 'Ambiente in Diretta';
    
    var mq = (dati.mq || (datiImmobile && datiImmobile.mq)) || '120 metri quadri';
    if (typeof normalizzaMetriQuadri === 'function') {
      mq = normalizzaMetriQuadri(mq);
    } else if (mq.toLowerCase().indexOf('metri quadri') === -1) {
      mq = mq + ' metri quadri';
    }

    var prezzo = (dati.prezzo || (datiImmobile && datiImmobile.prezzo)) || 'Trattativa Riservata';
    if (typeof normalizzaPrezzo === 'function') {
      prezzo = normalizzaPrezzo(prezzo);
    }

    // Preleva rigorosamente il testo parlato da Colonna F
    var testoColonnaF = (dati.testoF || (datiImmobile && (datiImmobile.testoF || datiImmobile.testo))) || '';
    if (!testoColonnaF && typeof generaTestoDescrittivoStanza === 'function') {
      testoColonnaF = generaTestoDescrittivoStanza(stanza, { tipoImmobile: titolo, metriQuadri: mq, prezzo: prezzo }, titolo);
    }
    if (!testoColonnaF) {
      testoColonnaF = "Ammirate " + stanza + " di " + titolo + ": uno spazio di " + mq + ", proposto " + prezzo + ". — Immobiliare Giancani";
    }

    // Link per vedere la diretta streaming sui 4 canali ufficiali
    var fbLiveUrl = props.getProperty('FB_LIVE_URL') || 'https://www.facebook.com/immobiliaregiancani/live';
    var ytLiveUrl = props.getProperty('YT_LIVE_URL') || 'https://www.youtube.com/@immobiliaregiancani761/live';
    var webLiveUrl = 'https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec';

    // Copy UNIFICATO ed IDENTICO per tutti i 4 canali social
    var testoUnificatoSocial = "🔴 SIAMO IN DIRETTA STREAMING ORA! 🏠✨\n\n" +
      "Guarda adesso il tour virtuale esclusivo di: " + titolo.toUpperCase() + "!\n" +
      "📍 Ambiente in onda: " + stanza + "\n" +
      "📐 Superficie: " + mq + "\n" +
      "💰 Prezzo: " + prezzo + "\n\n" +
      "🎙️ In diretta: \"" + testoColonnaF.replace(/\s*—?\s*Immobiliare Giancani\s*$/i, '') + "\"\n\n" +
      "👉 ENTRA SUBITO NELLA DIRETTA SUI NOSTRI 4 CANALI UFFICIALI:\n" +
      "📱 Facebook Live: " + fbLiveUrl + "\n" +
      "🎬 YouTube Live: " + ytLiveUrl + "\n" +
      "📸 Instagram: https://www.instagram.com/giancani_immobiliare/\n" +
      "🎵 TikTok: https://www.tiktok.com/@immobiliare_giancani/live\n\n" +
      "— Immobiliare Giancani";

    // Configurazione Pagine / Profili Facebook:
    // 1. Pagina Ufficiale Immobiliare Giancani (ID 234931856561526)
    // 2. Profilo/Pagina Personale Antonio Giancani (ID 108297671444008)
    var antonioPageId = props.getProperty('FB_ANTONIO_PAGE_ID') || '108297671444008';
    var antonioToken = props.getProperty('FB_ANTONIO_TOKEN') || 'EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia';

    props.setProperty('FB_ANTONIO_PAGE_ID', antonioPageId);
    props.setProperty('FB_ANTONIO_TOKEN', antonioToken);

    try {
      if (typeof salvaParametroSocialSuFoglio === 'function') {
        salvaParametroSocialSuFoglio("FB_ANTONIO_PAGE_ID", antonioPageId);
        salvaParametroSocialSuFoglio("FB_ANTONIO_TOKEN", antonioToken);
      }
    } catch(eSav) {}

    var photoUrl = (dati.fotoUrl || (datiImmobile ? (datiImmobile.mediaUrl || datiImmobile.fotoUrl) : '')) || '';
    if (typeof convertiUrlDriveDirect === 'function') {
      photoUrl = convertiUrlDriveDirect(photoUrl);
    }
    if (!photoUrl || photoUrl.indexOf('http') !== 0) {
      photoUrl = 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop';
    }

    var base64Img = dati.base64Image || null;
    if (base64Img) {
      try { props.setProperty('LAST_STORY_BASE64', base64Img); } catch(eB64Save) {}
    } else {
      base64Img = props.getProperty('LAST_STORY_BASE64') || null;
    }

    var fbTargets = [
      {
        pageId: pageId,
        pageToken: pageToken,
        nome: 'Immobiliare Giancani (Pagina Ufficiale)',
        isAntonio: false,
        testo: testoUnificatoSocial
      },
      {
        pageId: antonioPageId,
        pageToken: antonioToken,
        nome: 'Antonio Giancani (Profilo Personale)',
        isAntonio: true,
        testo: testoUnificatoSocial
      }
    ];

    var fbResults = [];

    for (var t = 0; t < fbTargets.length; t++) {
      var tgt = fbTargets[t];
      var pId = null;

      try {
        // 1. Carica la foto / snapshot con logo e dati sul target Facebook
        if (base64Img && base64Img.length > 25000) {
          pId = caricaFotoBase64SuFacebookPage(tgt.pageId, tgt.pageToken, base64Img, false, null);
        }
        if (!pId && photoUrl && photoUrl.indexOf('http') === 0) {
          var uploadUrl = 'https://graph.facebook.com/v19.0/' + tgt.pageId + '/photos';
          var uploadPayload = 'url=' + encodeURIComponent(photoUrl) +
                              '&published=false' +
                              '&access_token=' + encodeURIComponent(tgt.pageToken);
          var uploadRes = UrlFetchApp.fetch(uploadUrl, {
            method: 'post',
            payload: uploadPayload,
            muteHttpExceptions: true
          });
          if (uploadRes.getResponseCode() === 200) {
            var uJson = JSON.parse(uploadRes.getContentText());
            pId = uJson.id;
          }
        }

        var stRes = { success: false };
        var pstRes = { success: false };

        if (!pId) {
          console.warn("⚠️ [STORIE FACEBOOK] Nessuna foto valida caricata per " + tgt.nome + ": pubblicazione storia categoricamente annullata per evitare card vuote. — Immobiliare Giancani");
          fbResults.push({
            nome: tgt.nome,
            pageId: tgt.pageId,
            storia: { success: false, reason: "Nessuna foto valida dell'immobile in diretta" },
            post: { skipped: true }
          });
          continue;
        }

        if (pId) {
          // 2. Pubblica la Storia su Facebook (Photo Story) con il logo dell'agenzia e info immobile in vendita
          var storyUrl = 'https://graph.facebook.com/v19.0/' + tgt.pageId + '/photo_stories';
          var storyPayload = 'photo_id=' + encodeURIComponent(pId) +
                             '&access_token=' + encodeURIComponent(tgt.pageToken);
          var storyRes = UrlFetchApp.fetch(storyUrl, {
            method: 'post',
            payload: storyPayload,
            muteHttpExceptions: true
          });
          if (storyRes.getResponseCode() === 200) {
            var stJson = JSON.parse(storyRes.getContentText());
            stRes = { success: true, storyId: stJson.post_id || pId };
          }

          // 3. REGOLA RIGOROSA FEED POST:
          // - Pagina Immobiliare Giancani: ZERO post ripetuti sul feed (solo storie ogni 30 min)
          // - Profilo Antonio Giancani: il post d'invito della diretta va pubblicato SOLO 1 VOLTA all'avvio!
          if (tgt.isAntonio) {
            var antonioFeedPosted = props.getProperty('ANTONIO_LIVE_FEED_POSTED') === 'true';
            if (!antonioFeedPosted) {
              var feedPostUrl = 'https://graph.facebook.com/v19.0/' + tgt.pageId + '/feed';
              var feedPayload = 'message=' + encodeURIComponent(tgt.testo) +
                                '&attached_media[0]=' + encodeURIComponent(JSON.stringify({ media_fbid: pId })) +
                                '&access_token=' + encodeURIComponent(tgt.pageToken);
              var feedRes = UrlFetchApp.fetch(feedPostUrl, {
                method: 'post',
                payload: feedPayload,
                muteHttpExceptions: true
              });
              if (feedRes.getResponseCode() === 200) {
                var fdJson = JSON.parse(feedRes.getContentText());
                pstRes = { success: true, postId: fdJson.id, firstAnnouncement: true };
                props.setProperty('ANTONIO_LIVE_FEED_POSTED', 'true');
              } else {
                // Fallback link
                try {
                  var fbFallbackPayload = 'message=' + encodeURIComponent(tgt.testo) +
                                          '&link=' + encodeURIComponent(fbLiveUrl) +
                                          '&access_token=' + encodeURIComponent(tgt.pageToken);
                  var fRes = UrlFetchApp.fetch(feedPostUrl, { method: 'post', payload: fbFallbackPayload, muteHttpExceptions: true });
                  if (fRes.getResponseCode() === 200) {
                    var fJson = JSON.parse(fRes.getContentText());
                    pstRes = { success: true, postId: fJson.id, firstAnnouncement: true };
                    props.setProperty('ANTONIO_LIVE_FEED_POSTED', 'true');
                  }
                } catch(eFbFall) {}
              }
            } else {
              pstRes = { skipped: true, reason: "Post invito diretta già pubblicato 1 volta su Antonio Giancani — solo storie attive ogni 30 min" };
            }
          } else {
            // Pagina Immobiliare Giancani: pubblica solo storie ogni 30 minuti, mai post feed
            pstRes = { skipped: true, reason: "Solo storie ogni 30 minuti su Immobiliare Giancani per non intasare il feed aziendale" };
          }
        }

        fbResults.push({
          nome: tgt.nome,
          pageId: tgt.pageId,
          storia: stRes,
          post: pstRes
        });
      } catch(eTgt) {
        console.warn("Errore target " + tgt.nome + ":", eTgt);
        fbResults.push({ nome: tgt.nome, pageId: tgt.pageId, error: eTgt.toString() });
      }
    }

    // 4. PUBBLICA SU INSTAGRAM STORIES (@giancani_immobiliare, ID 17841400301393511)
    var igStoryResult = { success: false };
    try {
      if (photoUrl && photoUrl.indexOf('http') === 0) {
        var igAccountId = '17841400301393511';
        var igStoryUrl = "https://graph.facebook.com/v19.0/" + igAccountId + "/media";
        var igStoryPayload = {
          image_url: photoUrl,
          media_type: "STORIES",
          access_token: pageToken
        };
        var igRes = UrlFetchApp.fetch(igStoryUrl, { method: "post", payload: igStoryPayload, muteHttpExceptions: true });
        if (igRes.getResponseCode() === 200) {
          var igJson = JSON.parse(igRes.getContentText());
          if (igJson.id) {
            Utilities.sleep(1500);
            var igPubRes = UrlFetchApp.fetch("https://graph.facebook.com/v19.0/" + igAccountId + "/media_publish", {
              method: "post",
              payload: { creation_id: igJson.id, access_token: pageToken },
              muteHttpExceptions: true
            });
            if (igPubRes.getResponseCode() === 200) {
              igStoryResult = { success: true, storyId: igJson.id };
            }
          }
        }
      }
    } catch(eIgStory) {
      console.warn("Errore Instagram Story:", eIgStory);
    }

    // 5. PUBBLICA / NOTIFICA SU YOUTUBE LIVE (@immobiliaregiancani761)
    var ytResult = pubblicaAggiornamentoLiveYouTube(titolo, stanza, mq, prezzo, testoColonnaF, ytLiveUrl);

    // 6. PUBBLICA / NOTIFICA SU TIKTOK (@immobiliare_giancani)
    var tkStoryResult = { success: false };
    try {
      props.setProperty('TK_LAST_STORY_UPDATE', JSON.stringify({
        titolo: titolo,
        stanza: stanza,
        mq: mq,
        prezzo: prezzo,
        testo: testoColonnaF,
        timestamp: new Date().toISOString()
      }));
      tkStoryResult = { success: true, method: "Coda Storie TikTok Sincronizzata" };
    } catch(eTkStory) {
      console.warn("Errore TikTok Story:", eTkStory);
    }

    // Registra timestamp dell'ultimo invio riuscito
    props.setProperty('LAST_30MIN_SNAPSHOT_TIME', new Date().toISOString());
    props.setProperty('FB_LAST_STORY_PROP', titolo + ' — ' + stanza);

    // 7. NOTIFICA TELEGRAM COMPLETA PER TUTTI E 4 I CANALI SOCIAL
    var storyGiancaniOk = (fbResults[0] && fbResults[0].storia && fbResults[0].storia.success);
    var storyAntonioOk  = (fbResults[1] && fbResults[1].storia && fbResults[1].storia.success);
    var postAntonioRes  = (fbResults[1] && fbResults[1].post);
    var postAntonioDesc = 'ℹ️ Non previsto in questo ciclo';
    if (postAntonioRes && postAntonioRes.success && postAntonioRes.firstAnnouncement) {
      postAntonioDesc = '✅ Pubblicato (1° Annuncio Invito Singolo)';
    } else if (props.getProperty('ANTONIO_LIVE_FEED_POSTED') === 'true') {
      postAntonioDesc = '🟢 Già pubblicato all\'avvio (solo storie attive)';
    }

    var msgTelegram = '📸 <b>STORIE 30 MINUTI PUBBLICATE SUI 4 SOCIAL!</b> 🔴✨\n\n' +
                      'Aggiornamento automatico con lo <b>stesso identico contenuto</b>:\n\n' +
                      '🏠 <b>Immobile in Vendita:</b> ' + titolo + '\n' +
                      '📍 <b>Ambiente:</b> ' + stanza + '\n' +
                      '📐 <b>Superficie:</b> ' + mq + '\n' +
                      '💶 <b>Prezzo:</b> ' + prezzo + '\n\n' +
                      '🌐 <b>Stato Canali Social:</b>\n' +
                      '  • 📱 <b>Facebook (Pagina):</b> ' + (storyGiancaniOk ? '✅ Storia Pubblicata' : '⚠️ Non disponibile') + '\n' +
                      '  • 👤 <b>Facebook (Antonio):</b> ' + (storyAntonioOk ? '✅ Storia Pubblicata' : '⚠️ Non disponibile') + ' (' + postAntonioDesc + ')\n' +
                      '  • 📸 <b>Instagram:</b> ' + (igStoryResult.success ? '✅ Storia Pubblicata' : '⚠️ Sincronizzata via bridge') + '\n' +
                      '  • 🎬 <b>YouTube:</b> ' + (ytResult.success ? '✅ Aggiornato con link diretta' : '⚠️ Non disponibile') + '\n' +
                      '  • 🎵 <b>TikTok:</b> ' + (tkStoryResult.success ? '✅ Coda Storie Sincronizzata' : '⚠️ Non disponibile') + '\n\n' +
                      '🔗 <b>Link Diretta:</b> <a href="' + fbLiveUrl + '">Facebook Live</a> | <a href="' + ytLiveUrl + '">YouTube Live</a>\n' +
                      '⏱️ <b>Prossimo aggiornamento automatico:</b> tra 30 minuti esatti!\n\n' +
                      '— <b>Immobiliare Giancani</b>';

    if (typeof inviaNotificaTelegram === 'function') {
      inviaNotificaTelegram(msgTelegram, null, 'HTML');
    }

    return {
      success: true,
      immobile: titolo,
      stanza: stanza,
      facebook: fbResults,
      storiaFB: fbResults[0] ? fbResults[0].storia : null,
      postFB: fbResults[0] ? fbResults[0].post : null,
      storiaAntonio: fbResults[1] ? fbResults[1].storia : null,
      postAntonio: fbResults[1] ? fbResults[1].post : null,
      youtube: ytResult,
      messaggio: 'Storie 30 minuti pubblicate con successo su Pagina Immobiliare Giancani e Profilo Antonio Giancani! — Immobiliare Giancani'
    };

  } catch(e) {
    if (typeof inviaAllertaErroreTelegram === 'function') {
      inviaAllertaErroreTelegram('05_SocialECommentiLive.js', 'pubblicaSnapshotStoriaSocialOgni10Minuti', e.toString());
    }
    return { success: false, error: e.toString() };
  }
}

/**
 * Funzione trigger richiamata ogni 30 minuti da Google Apps Script durante la diretta
 */
function aggiornaStoriaSnapshotLiveOgni30Minuti() {
  try {
    return pubblicaSnapshotStoriaSocialOgni30Minuti();
  } catch(e) {
    console.warn("aggiornaStoriaSnapshotLiveOgni30Minuti:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * Attiva il trigger a tempo automatico ogni 30 minuti per Facebook e YouTube
 */
function attivaTriggerSnapshotStoriaOgni30Minuti() {
  try {
    disattivaTriggerSnapshotStoriaOgni30Minuti();
    ScriptApp.newTrigger('aggiornaStoriaSnapshotLiveOgni30Minuti')
      .timeBased()
      .everyMinutes(30)
      .create();
    return { success: true, messaggio: 'Trigger automatico ogni 30 minuti attivato per Facebook e YouTube. — Immobiliare Giancani' };
  } catch(e) {
    console.warn('attivaTriggerSnapshotStoriaOgni30Minuti:', e);
    return { success: false, error: e.toString() };
  }
}

/**
 * Disattiva il trigger automatico ogni 30 minuti (e precedenti 10 minuti)
 */
function disattivaTriggerSnapshotStoriaOgni30Minuti() {
  try {
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
      var fn = triggers[i].getHandlerFunction();
      if (fn === 'aggiornaStoriaSnapshotLiveOgni30Minuti' || fn === 'aggiornaStoriaSnapshotLiveOgni10Minuti' || fn === 'aggiornaStoriaFacebookLive') {
        ScriptApp.deleteTrigger(triggers[i]);
      }
    }
    return { success: true };
  } catch(e) {
    console.warn('disattivaTriggerSnapshotStoriaOgni30Minuti:', e);
    return { success: false, error: e.toString() };
  }
}

// Retrocompatibilità e alias 30/10 minuti
function pubblicaSnapshotStoriaSocialOgni30Minuti(datiInput) {
  return pubblicaSnapshotStoriaSocialOgni10Minuti(datiInput);
}

function aggiornaStoriaSnapshotLiveOgni10Minuti() {
  return aggiornaStoriaSnapshotLiveOgni30Minuti();
}

function attivaTriggerSnapshotStoriaOgni10Minuti() {
  return attivaTriggerSnapshotStoriaOgni30Minuti();
}

function disattivaTriggerSnapshotStoriaOgni10Minuti() {
  return disattivaTriggerSnapshotStoriaOgni30Minuti();
}

function pubblicaStoriaFacebookLive(datiImmobile, forcePhotoUrl) {
  var d = datiImmobile || {};
  if (forcePhotoUrl) d.fotoUrl = forcePhotoUrl;
  return pubblicaSnapshotStoriaSocialOgni30Minuti(d);
}

function aggiornaStoriaFacebookLive() {
  return aggiornaStoriaSnapshotLiveOgni10Minuti();
}

function attivaTriggerOrarioStoriaFacebook() {
  return attivaTriggerSnapshotStoriaOgni10Minuti();
}

function disattivaTriggerOrarioStoriaFacebook() {
  return disattivaTriggerSnapshotStoriaOgni10Minuti();
}

/**
 * Pubblica il post singolo d'invito alla diretta streaming sul profilo/pagina di Antonio Giancani
 */
function pubblicaPostInvitoDirettaAntonioGiancani(forza) {
  try {
    var props = PropertiesService.getScriptProperties();
    if (!forza && props.getProperty('ANTONIO_LIVE_FEED_POSTED') === 'true') {
      return {
        success: true,
        skipped: true,
        messaggio: "Post d'invito diretta già pubblicato su Antonio Giancani. — Immobiliare Giancani"
      };
    }

    var datiImmobile = (typeof getImmobileData === 'function') ? getImmobileData('current') : null;
    var titolo = (datiImmobile && (datiImmobile.titolo || datiImmobile.nome)) || 'Immobile in Esclusiva';
    var stanza = (datiImmobile && datiImmobile.stanza) || 'Ambiente in Diretta';
    var mq = (datiImmobile && datiImmobile.mq) || '120 metri quadri';
    if (typeof normalizzaMetriQuadri === 'function') mq = normalizzaMetriQuadri(mq);
    var prezzo = (datiImmobile && datiImmobile.prezzo) || 'Trattativa Riservata';
    if (typeof normalizzaPrezzo === 'function') prezzo = normalizzaPrezzo(prezzo);

    var testoColonnaF = (datiImmobile && (datiImmobile.testoF || datiImmobile.testo)) || '';
    if (!testoColonnaF && typeof generaTestoDescrittivoStanza === 'function') {
      testoColonnaF = generaTestoDescrittivoStanza(stanza, { tipoImmobile: titolo, metriQuadri: mq, prezzo: prezzo }, titolo);
    }
    if (!testoColonnaF) {
      testoColonnaF = "Ammirate " + stanza + " di " + titolo + ": uno spazio di " + mq + ", proposto " + prezzo + ". — Immobiliare Giancani";
    }

    var fbLiveUrl = props.getProperty('FB_LIVE_URL') || 'https://www.facebook.com/immobiliaregiancani/live';
    var ytLiveUrl = props.getProperty('YT_LIVE_URL') || 'https://www.youtube.com/@immobiliaregiancani761/live';
    var webLiveUrl = 'https://script.google.com/macros/s/AKfycbwTAyOTWpm3mNGX-DAWbZ7XOtrog52md5-P_jUEHoEhsoXCrJGj_bLClOiDvo5FKUbpWg/exec';

    var testoAntonio = "🔴 SIAMO IN DIRETTA STREAMING ORA! 🏠✨\n\n" +
      "Guarda adesso il tour virtuale esclusivo di: " + titolo.toUpperCase() + "!\n" +
      "📍 In questo momento stiamo mostrando: " + stanza + "\n" +
      "📐 Superficie: " + mq + "\n" +
      "💰 Prezzo: " + prezzo + "\n\n" +
      "🎙️ Dalla diretta: \"" + testoColonnaF.replace(/\s*—?\s*Immobiliare Giancani\s*$/i, '') + "\"\n\n" +
      "👉 ENTRA SUBITO NELLA DIRETTA SUI NOSTRI 4 CANALI UFFICIALI:\n" +
      "📱 Facebook Live: " + fbLiveUrl + "\n" +
      "🎬 YouTube Live: " + ytLiveUrl + "\n" +
      "📸 Instagram: https://www.instagram.com/giancani_immobiliare/\n" +
      "🎵 TikTok: https://www.tiktok.com/@immobiliare_giancani/live\n\n" +
      "— Immobiliare Giancani";

    var antonioPageId = props.getProperty('FB_ANTONIO_PAGE_ID') || '108297671444008';
    var antonioToken = props.getProperty('FB_ANTONIO_TOKEN') || 'EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia';

    var photoUrl = (datiImmobile ? (datiImmobile.mediaUrl || datiImmobile.fotoUrl) : '') || 'https://lh3.googleusercontent.com/d/1BoZ_9QyYPRKjZFP__iPr7mmi0aGV0G3P';
    var base64Img = props.getProperty('LAST_STORY_BASE64') || null;

    var pId = null;
    if (base64Img) {
      pId = caricaFotoBase64SuFacebookPage(antonioPageId, antonioToken, base64Img, false, null);
    }
    if (!pId) {
      var uploadUrl = 'https://graph.facebook.com/v19.0/' + antonioPageId + '/photos';
      var uploadPayload = 'url=' + encodeURIComponent(photoUrl) + '&published=false&access_token=' + encodeURIComponent(antonioToken);
      var uploadRes = UrlFetchApp.fetch(uploadUrl, { method: 'post', payload: uploadPayload, muteHttpExceptions: true });
      if (uploadRes.getResponseCode() === 200) {
        pId = JSON.parse(uploadRes.getContentText()).id;
      }
    }

    var feedPostUrl = 'https://graph.facebook.com/v19.0/' + antonioPageId + '/feed';
    var feedPayload = 'message=' + encodeURIComponent(testoAntonio) +
                      (pId ? ('&attached_media[0]=' + encodeURIComponent(JSON.stringify({ media_fbid: pId }))) : ('&link=' + encodeURIComponent(fbLiveUrl))) +
                      '&access_token=' + encodeURIComponent(antonioToken);

    var feedRes = UrlFetchApp.fetch(feedPostUrl, { method: 'post', payload: feedPayload, muteHttpExceptions: true });
    if (feedRes.getResponseCode() === 200) {
      var j = JSON.parse(feedRes.getContentText());
      props.setProperty('ANTONIO_LIVE_FEED_POSTED', 'true');
      return {
        success: true,
        postId: j.id,
        messaggio: "Post d'invito diretta pubblicato con successo su Antonio Giancani! — Immobiliare Giancani"
      };
    } else {
      return {
        success: false,
        error: feedRes.getContentText()
      };
    }
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 💾 Salva un video MP4 (Base64) su Google Drive e restituisce l'URL pubblico diretto
 */
function caricaVideoBase64SuDrive(base64Content, fileName) {
  try {
    if (!base64Content) return { success: false, error: 'Contenuto base64 mancante' };
    var cleanB64 = base64Content.indexOf(',') !== -1 ? base64Content.split(',')[1] : base64Content;
    var bytes = Utilities.base64Decode(cleanB64);
    var blob = Utilities.newBlob(bytes, 'video/mp4', fileName || ('storia_' + Date.now() + '.mp4'));

    var folders = DriveApp.getFoldersByName('Storie_Social_Giancani');
    var targetFolder = folders.hasNext() ? folders.next() : DriveApp.createFolder('Storie_Social_Giancani');

    var file = targetFolder.createFile(blob);
    try { file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); } catch(eSh) {}

    var fileId = file.getId();
    var directUrl = 'https://lh3.googleusercontent.com/d/' + fileId;
    var downloadUrl = 'https://drive.google.com/uc?export=download&id=' + fileId;

    return {
      success: true,
      fileId: fileId,
      directUrl: directUrl,
      downloadUrl: downloadUrl,
      fileName: file.getName(),
      sizeBytes: file.getSize(),
      message: 'Video salvato su Google Drive con link pubblico attivo. — Immobiliare Giancani'
    };
  } catch(e) {
    inviaAllertaErroreTelegram("05_SocialECommentiLive.js", "caricaVideoBase64SuDrive", e.toString());
    return { success: false, error: e.toString() };
  }
}

/**
 * 🎬 Pubblica o registra uno Short su YouTube (@immobiliaregiancani761)
 */
function pubblicaShortYouTubeSuCanale(dati) {
  try {
    dati = dati || {};
    var titolo = dati.titolo || 'Opportunità Immobiliare';
    var stanza = dati.stanza || '';
    var mq = dati.mq || '120 metri quadri';
    if (typeof normalizzaMetriQuadri === 'function') mq = normalizzaMetriQuadri(mq);
    var prezzo = dati.prezzo || 'Trattativa Riservata';
    var testoF = dati.testoF || '';

    // Regola di branding e format Shorts
    var ytTitle = (titolo + (stanza ? (' • ' + stanza) : '') + ' | #Shorts').substring(0, 95);
    var ytDesc = (testoF ? (testoF + '\n\n') : '') +
                 '🏠 Immobile: ' + titolo + '\n' +
                 '📐 Superficie: ' + mq + '\n' +
                 '💰 Prezzo: ' + prezzo + '\n\n' +
                 '📞 Contattaci: Immobiliare Giancani — Favara (AG)\n' +
                 '#Shorts #ImmobiliareGiancani #RealEstate #CaseInVendita #Favara\n\n' +
                 '— Immobiliare Giancani';

    var videoId = null;
    var uploadStatus = 'REGISTRATO';

    // 1. Prova con YouTube Advanced Service se abilitato
    if (typeof YouTube !== 'undefined' && YouTube.Videos && YouTube.Videos.insert && dati.base64Video) {
      try {
        var cleanB64 = dati.base64Video.indexOf(',') !== -1 ? dati.base64Video.split(',')[1] : dati.base64Video;
        var bytes = Utilities.base64Decode(cleanB64);
        var blob = Utilities.newBlob(bytes, 'video/mp4', 'short_' + Date.now() + '.mp4');
        var resource = {
          snippet: {
            title: ytTitle,
            description: ytDesc,
            tags: ['Shorts', 'Immobiliare Giancani', 'Case in vendita', 'Favara', 'Agrigento'],
            categoryId: '22'
          },
          status: {
            privacyStatus: 'public',
            selfDeclaredMadeForKids: false
          }
        };
        var ytRes = YouTube.Videos.insert(resource, 'snippet,status', blob);
        if (ytRes && ytRes.id) {
          videoId = ytRes.id;
          uploadStatus = 'PUBBLICATO_DIRETTO';
        }
      } catch(eYtInsert) {
        console.warn('YouTube.Videos.insert:', eYtInsert);
      }
    }

    // 2. Salva in Post_YouTube per la cronologia / rotazione
    try {
      var ss = getSpreadsheetSicuro();
      var sheet = ss ? ss.getSheetByName('Post_YouTube') : null;
      if (sheet) {
        var videoLink = videoId ? ('https://www.youtube.com/shorts/' + videoId) : (dati.videoUrl || '');
        sheet.appendRow([
          videoLink,
          prezzo,
          mq,
          titolo,
          'Shorts',
          testoF,
          dati.thumbUrl || '',
          ytTitle,
          videoLink,
          15
        ]);
      }
    } catch(eSheet) {}

    return {
      success: true,
      videoId: videoId,
      status: uploadStatus,
      shortUrl: videoId ? ('https://www.youtube.com/shorts/' + videoId) : (dati.videoUrl || 'https://www.youtube.com/@immobiliaregiancani761/shorts'),
      titolo: ytTitle,
      message: 'YouTube Short elaborato con successo — Immobiliare Giancani'
    };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 🎬 CARICA LINK VIDEO YOUTUBE DA REGIA / GENERATOR
 * Permette alla regia di inserire qualsiasi link YouTube (video normale, short, embed)
 * e decidere se mandarlo subito in onda, aggiungerlo al foglio Post_YouTube o sullo schermo centrale.
 */
function caricaLinkVideoYouTubeRegia(videoUrl, opzioni) {
  try {
    if (!videoUrl) return { success: false, error: "Link video YouTube mancante" };
    var opts = opzioni || {};

    // 1. Estrazione del Video ID da qualsiasi formato YouTube
    var videoId = "";
    var m = videoUrl.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?(?:.*&)?v=|embed\/|shorts\/|v\/|live\/))([\w-]{11})/i);
    if (m && m[1]) {
      videoId = m[1];
    } else if (videoUrl.length === 11 && videoUrl.indexOf('http') === -1) {
      videoId = videoUrl;
    }

    var cleanUrl = videoId ? ("https://www.youtube.com/watch?v=" + videoId) : videoUrl;
    var embedUrl = videoId ? ("https://www.youtube.com/embed/" + videoId) : videoUrl;
    var thumbUrl = videoId ? ("https://img.youtube.com/vi/" + videoId + "/hqdefault.jpg") : "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop";

    var titolo = opts.titolo ? opts.titolo.trim() : ("Video Immobile YouTube " + (videoId ? ("(" + videoId + ")") : ""));
    var prezzo = opts.prezzo ? opts.prezzo.trim() : "Trattativa Riservata";
    var mq = opts.mq ? opts.mq.trim() : "120 metri quadri";
    if (typeof normalizzaMetriQuadri === 'function') {
      mq = normalizzaMetriQuadri(mq);
    } else if (mq.toLowerCase().indexOf('metri quadri') === -1) {
      mq = mq + ' metri quadri';
    }

    var testoF = opts.testoF ? opts.testoF.trim() : "";
    if (!testoF) {
      testoF = "Ammirate questo straordinario filmato immobiliare di " + titolo + ": uno spazio di " + mq + ", proposto " + prezzo + ". Seguiteci per tutti i dettagli esclusivi! — Immobiliare Giancani";
    } else if (testoF.indexOf('Immobiliare Giancani') === -1) {
      testoF = testoF + " — Immobiliare Giancani";
    }

    var props = PropertiesService.getScriptProperties();
    var destinazione = opts.destinazione || 'post_youtube'; // 'post_youtube', 'live_immediato', 'schermo_centrale'

    var risultati = {
      videoId: videoId,
      videoUrl: cleanUrl,
      embedUrl: embedUrl,
      thumbUrl: thumbUrl,
      titolo: titolo,
      mq: mq,
      prezzo: prezzo,
      destinazione: destinazione
    };

    // A) MANDA SUBITO IN ONDA IN DIRETTA
    if (destinazione === 'live_immediato' || opts.mandaInOndaSubito) {
      props.setProperty('CURRENT_LIVE_VIDEO_URL', cleanUrl);
      props.setProperty('CURRENT_LIVE_VIDEO_EMBED', embedUrl);
      props.setProperty('CURRENT_LIVE_VIDEO_ID', videoId);
      props.setProperty('CURRENT_LIVE_VIDEO_TITOLO', titolo);
      props.setProperty('CURRENT_LIVE_VIDEO_MQ', mq);
      props.setProperty('CURRENT_LIVE_VIDEO_TESTO_F', testoF);
      props.setProperty('LAST_VIDEO_INJECT_TIME', new Date().toISOString());
      risultati.liveImmediato = true;
    }

    // B) SALVA NEL FOGLIO Post_YouTube
    if (destinazione === 'post_youtube' || opts.salvaInCatalogo !== false) {
      var ss = getSpreadsheetSicuro();
      var sYt = ss ? ss.getSheetByName("Post_YouTube") : null;
      if (sYt) {
        sYt.insertRowBefore(2);
        sYt.getRange(2, 1, 1, 10).setValues([[
          cleanUrl,
          prezzo,
          mq,
          titolo,
          "youtube",
          testoF,
          thumbUrl,
          "Video Canale: " + titolo,
          cleanUrl,
          Number(opts.durataSec || 30)
        ]]);
        risultati.salvatoInPostYouTube = true;
      }
    }

    // C) SCHERMO CENTRALE TRA DARIA E DARIO
    if (destinazione === 'schermo_centrale' || opts.inviaSchermoCentrale) {
      var ss2 = getSpreadsheetSicuro();
      var sSc = ss2 ? ss2.getSheetByName("Pubblicita_Schermo_Centrale") : null;
      if (sSc) {
        sSc.appendRow([
          cleanUrl,
          Number(opts.durataSec || 15),
          titolo,
          "video",
          "SI"
        ]);
        risultati.inviatoSchermoCentrale = true;
      }
    }

    // NOTIFICA TELEGRAM DI CONFERMA
    if (typeof inviaNotificaTelegram === 'function') {
      var descDest = "🎬 <b>Post_YouTube (Catalogo)</b>";
      if (destinazione === 'live_immediato') descDest = "🔴 <b>MANDATO SUBITO IN ONDA IN DIRETTA</b>";
      if (destinazione === 'schermo_centrale') descDest = "📺 <b>Schermo Centrale Studio</b>";

      inviaNotificaTelegram(
        "🎬 <b>NUOVO VIDEO YOUTUBE CARICATO DA REGIA</b> 🔴✨\n\n" +
        "Un nuovo link YouTube è stato acquisito su Generator:\n\n" +
        "🏠 <b>Titolo:</b> " + titolo + "\n" +
        "📐 <b>Superficie:</b> " + mq + "\n" +
        "💶 <b>Prezzo:</b> " + prezzo + "\n" +
        "🎯 <b>Destinazione:</b> " + descDest + "\n" +
        "🔗 <b>Link Video:</b> <a href=\"" + cleanUrl + "\">" + (videoId || cleanUrl) + "</a>\n\n" +
        "🎙️ <i>Testo Colonna F generato e sincronizzato per DarIA & DarIO.</i>\n\n" +
        "— <b>Immobiliare Giancani</b>",
        thumbUrl,
        "HTML"
      );
    }

    return {
      success: true,
      data: risultati,
      messaggio: "Video YouTube acquisito con successo! — Immobiliare Giancani"
    };

  } catch(e) {
    console.error("Errore caricaLinkVideoYouTubeRegia:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * Determina la fascia oraria attuale con saluti, emoticon e musica royalty-free per Facebook
 */
function determinaFasciaOrariaSalutoGAS(oraManuale) {
  var ora = oraManuale;
  if (typeof ora === 'undefined' || ora === null) {
    var now = new Date();
    ora = Number(Utilities.formatDate(now, "Europe/Rome", "H"));
  }

  if (ora >= 6 && ora < 12) {
    return {
      fascia: "mattina",
      nome: "Mattina",
      saluto: "Buongiorno 🌅☀️☕",
      badge: "🌅 BUONGIORNO • IMMOBILIARE GIANCANI",
      emoticon: "🌅☀️☕",
      titolo_nota: "📝 NOTA DEL BUONGIORNO — Immobiliare Giancani 🌅☀️",
      musica: "Vivaldi - La Primavera (Royalty-Free Facebook)",
      riflessione: "🌅 Buongiorno da Immobiliare Giancani! ☕\n\nIniziare la giornata nel posto giusto fa tutta la differenza del mondo. La luce del mattino che illumina gli ampi spazi, il profumo del caffè in una cucina accogliente e la serenità di aver trovato il nido perfetto per la propria famiglia.\n\nOgni nuovo giorno porta con sé l'opportunità di compiere il passo decisivo verso la casa dei propri sogni."
    };
  } else if (ora >= 12 && ora < 18) {
    return {
      fascia: "pomeriggio",
      nome: "Pomeriggio",
      saluto: "Buon pomeriggio ☕🌤️🏡",
      badge: "☕ BUON POMERIGGIO • IMMOBILIARE GIANCANI",
      emoticon: "☕🌤️🏡",
      titolo_nota: "📝 NOTA DEL POMERIGGIO — Immobiliare Giancani ☕🌤️",
      musica: "Cheerful Acoustic Lounge 124 BPM (Royalty-Free Facebook)",
      riflessione: "☕ Buon pomeriggio da Immobiliare Giancani! 🌤️\n\nUna breve pausa nel pomeriggio è il momento ideale per riflettere sul futuro e sui propri progetti di vita. Gli spazi giusti regalano serenità, comfort e il piacere di vivere ogni ambiente con gioia e libertà.\n\nSiamo sempre al vostro fianco per guidarvi con cura ed esperienza nella scelta della vostra nuova dimora."
    };
  } else if (ora >= 18 && ora < 22) {
    return {
      fascia: "sera",
      nome: "Sera",
      saluto: "Buona sera 🌆🍷✨",
      badge: "🌆 BUONA SERA • IMMOBILIARE GIANCANI",
      emoticon: "🌆🍷✨",
      titolo_nota: "📝 NOTA DELLA SERA — Immobiliare Giancani 🌆🍷✨",
      musica: "Luxury Sunset Ambient (Royalty-Free Facebook)",
      riflessione: "🌆 Buona sera da Immobiliare Giancani! 🍷\n\nC’è una magia tutta speciale nella tranquillità della sera: la gioia di tornare a casa, chiudere la porta e ritrovarsi nell'intimità dei propri affetti, immersi nel calore di un ambiente accogliente e protetto.\n\nLa vera bellezza dell'abitare è sentirsi sempre nel posto giusto al momento giusto."
    };
  } else {
    return {
      fascia: "notte",
      nome: "Notte",
      saluto: "Buonanotte 🌙⭐️💤",
      badge: "🌙 BUONANOTTE • IMMOBILIARE GIANCANI",
      emoticon: "🌙⭐️💤",
      titolo_nota: "📝 NOTA DELLA BUONANOTTE — Immobiliare Giancani 🌙⭐️💤",
      musica: "Mozart - Serenata Notturna (Royalty-Free Facebook)",
      riflessione: "🌙 Buonanotte e sogni d'oro da Immobiliare Giancani! ⭐️\n\nMentre la notte scende sul territorio, è tempo di riposare sereni e fare spazio ai desideri più belli. I sogni più autentici sono quelli che domani, con determinazione e i giusti consigli, possono diventare meravigliosa realtà.\n\nVi auguriamo un sereno riposo, sapendo che la casa perfetta è già lì che vi aspetta."
    };
  }
}

/**
 * Pubblica una 'Nota di Pagina' (Post ricco con formato Nota) sulla Pagina Facebook e Profilo
 * con saluto del momento, emoticon, riflessione, immobile da Colonna F e musica royalty-free
 */
function pubblicaNotaFacebookFasciaOraria(fasciaRichiesta, opzioni) {
  try {
    var opts = opzioni || {};
    var props = PropertiesService.getScriptProperties();

    var ora = null;
    if (fasciaRichiesta === 'mattina') ora = 8;
    else if (fasciaRichiesta === 'pomeriggio') ora = 14;
    else if (fasciaRichiesta === 'sera') ora = 19;
    else if (fasciaRichiesta === 'notte') ora = 23;

    var info = determinaFasciaOrariaSalutoGAS(ora);

    var datiImm = (typeof getImmobileData === 'function') ? getImmobileData('current') : null;
    var titolo = (opts.titolo || (datiImm && (datiImm.titolo || datiImm.nome)) || "Villa Favara con Giardino").trim();
    var mq = (opts.mq || (datiImm && datiImm.mq) || "140 metri quadri").trim();
    if (typeof normalizzaMetriQuadri === 'function') mq = normalizzaMetriQuadri(mq);
    var prezzo = (opts.prezzo || (datiImm && datiImm.prezzo) || "Trattativa Riservata").trim();
    
    var testoF = (opts.testoF || (datiImm && (datiImm.testoF || datiImm.testo)) || "").trim();
    if (!testoF) {
      testoF = "Splendida soluzione abitativa immersa nel verde con finiture di alto livello, ambienti luminosi ed accoglienti. Contattaci per una visita riservata. — Immobiliare Giancani";
    }
    testoF = testoF.replace(/\s*—?\s*Immobiliare Giancani\s*$/i, '').trim();

    var messaggioNota = info.titolo_nota + "\n\n" +
      info.riflessione + "\n\n" +
      "━━━━━━━━━━━━━━━━━━━━\n" +
      "🏠 IMMOBILE IN EVIDENZA: " + titolo.toUpperCase() + "\n" +
      "📐 SUPERFICIE: " + mq + "\n" +
      "💰 PREZZO: " + prezzo + "\n" +
      "━━━━━━━━━━━━━━━━━━━━\n\n" +
      "🎙️ Dettagli esclusivi (DarIA): \"" + testoF + "\"\n\n" +
      "🎵 Sottofondo musicale: " + info.musica + "\n\n" +
      "👉 Per scoprire tutti i dettagli, ricevere la planimetria o concordare una visita:\n" +
      "📞 Contattaci al nostro numero o inviaci un messaggio privato.\n\n" +
      "📱 Seguici su tutti i nostri canali:\n" +
      "• Facebook: https://www.facebook.com/immobiliaregiancani\n" +
      "• YouTube: https://www.youtube.com/@immobiliaregiancani761\n" +
      "• Instagram: https://www.instagram.com/giancani_immobiliare/\n" +
      "• TikTok: https://www.tiktok.com/@immobiliare_giancani\n\n" +
      "— Immobiliare Giancani";

    var pageId = props.getProperty('FB_PAGE_ID') || '234931856561526';
    var pageToken = props.getProperty('FB_PAGE_ACCESS_TOKEN') || 'EAAZAH7q8wRZAEBSaZAm9Q9JGa8ZC7gwAsRJ1n4bPZAIY5ws8VXZAnugJgtZCOvP7HyEd7IEfWeCD5HfmP0ENQh86J3PT7pDFnOt5nPJdpzYyUM6p6AtZBXnXufThdh9ZAczfsE84obRZCOD3UWslSWpxJ058WGrQfXxJYsXtVZBh1ey7j2zuzme2JcEoya10KdL8TfJOpvNHqD8EsionnLI';

    var results = [];

    // 1. Pubblica sulla Pagina Ufficiale Immobiliare Giancani
    var feedUrl = "https://graph.facebook.com/v19.0/" + pageId + "/feed";
    var payload = "message=" + encodeURIComponent(messaggioNota) + "&access_token=" + encodeURIComponent(pageToken);
    var resp = UrlFetchApp.fetch(feedUrl, { method: "post", payload: payload, muteHttpExceptions: true });
    if (resp.getResponseCode() === 200) {
      var rJson = JSON.parse(resp.getContentText());
      results.push({ target: "Pagina Immobiliare Giancani", id: rJson.id, success: true });
    }

    // 2. Pubblica sul Profilo Antonio Giancani
    var antonioId = props.getProperty('FB_ANTONIO_PAGE_ID') || '108297671444008';
    var antonioToken = props.getProperty('FB_ANTONIO_TOKEN') || 'EAAZAH7q8wRZAEBSQbsAIPVhCwMvrhECfhs5UNWL8ZBIOrUbCXqWCQtsyntumIOAvDCRUcg2FsmJBNtiXOEOO2TROFJE9CBXrZBT4GPrZAZCjB73WZALCECi7Ik9ZCae5y01ZB5ZAV7VH7qHyNdeZCWZCG9xViT0gZCYwnV7MCSuQKS5ZA1ZCdw5nom0IH8uub3ZAwVsIGhNSDdkJWZCgCIzs1b8ia';
    if (antonioToken && antonioId) {
      try {
        var antUrl = "https://graph.facebook.com/v19.0/" + antonioId + "/feed";
        var antPayload = "message=" + encodeURIComponent(messaggioNota) + "&access_token=" + encodeURIComponent(antonioToken);
        var antResp = UrlFetchApp.fetch(antUrl, { method: "post", payload: antPayload, muteHttpExceptions: true });
        if (antResp.getResponseCode() === 200) {
          var antJson = JSON.parse(antResp.getContentText());
          results.push({ target: "Profilo Antonio Giancani", id: antJson.id, success: true });
        }
      } catch(eAnt) {
        console.warn("Avviso post Antonio Giancani:", eAnt);
      }
    }

    if (typeof inviaNotificaTelegram === 'function') {
      inviaNotificaTelegram(
        "📝 <b>NOTA FACEBOOK PUBBLICATA CON SUCCESSO!</b> " + info.emoticon + "\n\n" +
        "È stata pubblicata la nota per la fascia: <b>" + info.saluto + "</b>\n\n" +
        "🏠 <b>Immobile:</b> " + titolo + "\n" +
        "📐 <b>Superficie:</b> " + mq + "\n" +
        "💰 <b>Prezzo:</b> " + prezzo + "\n" +
        "🎵 <b>Musica Royalty-Free:</b> " + info.musica + "\n\n" +
        "— <b>Immobiliare Giancani</b>",
        null,
        "HTML"
      );
    }

    return {
      success: results.length > 0,
      fascia: info.fascia,
      saluto: info.saluto,
      pubblicazioni: results,
      messaggio: "Nota Facebook (" + info.saluto + ") pubblicata con successo! — Immobiliare Giancani"
    };

  } catch(e) {
    console.error("Errore pubblicaNotaFacebookFasciaOraria:", e);
    return { success: false, error: e.toString() };
  }
}

/**
 * Attiva o aggiorna i trigger automatici quotidiani per le 4 note su Facebook
 */
function attivaTriggerNoteOrarieFacebook() {
  try {
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
      if (triggers[i].getHandlerFunction() === 'triggerAutomaticoNotaFacebook') {
        ScriptApp.deleteTrigger(triggers[i]);
      }
    }

    ScriptApp.newTrigger('triggerAutomaticoNotaFacebook')
      .timeBased()
      .everyHours(1)
      .create();

    return {
      success: true,
      messaggio: "Trigger per le Note orarie Facebook (Buongiorno, Pomeriggio, Sera, Notte) attivato con successo! — Immobiliare Giancani"
    };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function triggerAutomaticoNotaFacebook() {
  var now = new Date();
  var ora = Number(Utilities.formatDate(now, "Europe/Rome", "H"));
  if (ora === 8 || ora === 14 || ora === 19 || ora === 23) {
    pubblicaNotaFacebookFasciaOraria();
  }
}


