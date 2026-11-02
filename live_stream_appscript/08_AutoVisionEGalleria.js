// ═══════════════════════════════════════════════════════════════════════
// 📁 MODULO 08: AUTO-VISION, GALLERIA FOTO & GOOGLE DRIVE
// Gestisce sincronizzazione immagini, salvataggio testi Colonna F e cartelle Drive
// ═══════════════════════════════════════════════════════════════════════


/**
 * 🏷️ Estrae la tipologia principale dell'immobile dal nome della cartella o del foglio
 * Es: "appartamento in via xx yyy" -> "Appartamento", "villa con piscina" -> "Villa"
 */
function estraiTipoImmobileDaNomeCartella(nomeCartellaOTab) {
  if (!nomeCartellaOTab) return "Appartamento";
  var clean = String(nomeCartellaOTab).replace(/_/g, ' ').trim();
  var lower = clean.toLowerCase();

  if (lower.indexOf("villa") !== -1) return "Villa";
  if (lower.indexOf("appartamento") !== -1) return "Appartamento";
  if (lower.indexOf("attico") !== -1) return "Attico";
  if (lower.indexOf("casa indipendente") !== -1 || lower.indexOf("indipendente") !== -1) return "Casa Indipendente";
  if (lower.indexOf("rustico") !== -1 || lower.indexOf("casale") !== -1) return "Rustico";
  if (lower.indexOf("monolocale") !== -1) return "Monolocale";
  if (lower.indexOf("bilocale") !== -1) return "Bilocale";
  if (lower.indexOf("trilocale") !== -1) return "Trilocale";
  if (lower.indexOf("quadrilocale") !== -1) return "Quadrilocale";
  if (lower.indexOf("mansarda") !== -1) return "Mansarda";
  if (lower.indexOf("duplex") !== -1) return "Duplex";
  if (lower.indexOf("palazzina") !== -1 || lower.indexOf("stabile") !== -1) return "Palazzina";
  if (lower.indexOf("ufficio") !== -1) return "Ufficio";
  if (lower.indexOf("commerciale") !== -1 || lower.indexOf("locale") !== -1 || lower.indexOf("negozio") !== -1) return "Locale Commerciale";
  if (lower.indexOf("garage") !== -1 || lower.indexOf("box") !== -1) return "Garage";
  if (lower.indexOf("terreno") !== -1) return "Terreno";
  if (lower.indexOf("deposito") !== -1 || lower.indexOf("magazzino") !== -1) return "Magazzino";

  var primaParola = clean.split(/\s+/)[0];
  if (primaParola && primaParola.length >= 4 && !primaParola.match(/^\d+$/)) {
    return primaParola.charAt(0).toUpperCase() + primaParola.slice(1).toLowerCase();
  }
  return "Appartamento";
}

/**
 * 🧹 Sanitizza il nome del foglio/tab per Google Sheets
 * Rimuove caratteri vietati da Sheets ([ ] * ? : / \ ') ed emoji, e limita a 80 caratteri
 */
function sanitizzaNomeTabPerGoogleSheets(nome) {
  if (!nome) return "Immobile";
  var s = String(nome).trim();
  // Rimuovi prefissi grafici tipo [CARTELLA MASTER], emoji o parentesi quadre
  s = s.replace(/\[.*?\]/g, '').replace(/🌟|📁|📂/g, '');
  // Rimuovi caratteri vietati da Google Sheets: [ ] * ? : / \ '
  s = s.replace(/[\[\]\*?\:\/\\']/g, '');
  // Sostituisci caratteri speciali, spazi multipli o trattini con underscore
  s = s.replace(/\s+/g, '_').replace(/[^\w\d_À-ÿ]/g, '_');
  // Rimuovi underscore ripetuti e trimma
  s = s.replace(/_+/g, '_').replace(/^_+|_+$/g, '');
  if (!s) s = "Immobile";
  if (s.length > 80) s = s.substring(0, 80);
  return s;
}

/**
 * 🔍 Riconosce la stanza dal nome del file (o fallback al tipo immobile se non riconosciuto)
 * Es: se vede wc/bagno scrive "Bagno", se non capisce scrive "Appartamento" (o "Villa")
 */
function deduciStanzaOImmobile(rawBase, tipoImmobileDefault) {
  var fallbackTipo = tipoImmobileDefault || "Appartamento";
  if (!rawBase) return fallbackTipo;
  var bLow = rawBase.toLowerCase().trim();

  // 1. Sanitari / WC / Bagno ("se vede il wc scrive bagno")
  if (bLow.match(/\b(wc|bagno|toilette|servizio|doccia|lavanderia|bidet|bath|water)\b/) || bLow.indexOf("wc") !== -1 || bLow.indexOf("bagno") !== -1) {
    return "Bagno";
  }
  // 2. Cucina
  if (bLow.match(/\b(cucina|cottura|kitchen|angolo_cottura|tinello|pranzo)\b/) || bLow.indexOf("cucina") !== -1) {
    return "Cucina";
  }
  // 3. Camera da letto
  if (bLow.match(/\b(camera|letto|matrimoniale|notte|singola|padronale|bed)\b/) || bLow.indexOf("camera") !== -1) {
    return "Camera da letto";
  }
  // 4. Cameretta
  if (bLow.indexOf("cameretta") !== -1 || bLow.indexOf("ragazzi") !== -1 || bLow.indexOf("bambin") !== -1) {
    return "Cameretta";
  }
  // 5. Soggiorno / Living / Salone
  if (bLow.match(/\b(soggiorno|salone|living|salotto|relax)\b/) || bLow.indexOf("soggiorno") !== -1 || bLow.indexOf("salone") !== -1) {
    return "Soggiorno";
  }
  // 6. Terrazzo / Balcone
  if (bLow.match(/\b(terrazz|balcon|verand|loggia|vista|panorama)\b/) || bLow.indexOf("terrazz") !== -1 || bLow.indexOf("balcon") !== -1) {
    return "Terrazzo";
  }
  // 7. Esterno / Giardino / Facciata
  if (bLow.match(/\b(giardin|estern|cortil|portic|facciata|prospetto)\b/) || bLow.indexOf("giardin") !== -1 || bLow.indexOf("estern") !== -1) {
    return "Esterno";
  }
  // 8. Garage / Box
  if (bLow.match(/\b(garage|box|auto|posto_auto)\b/) || bLow.indexOf("garage") !== -1) {
    return "Garage";
  }
  // 9. Ingresso / Corridoio
  if (bLow.match(/\b(ingresso|entrata|corridoio|disimpegno|atrio)\b/) || bLow.indexOf("ingresso") !== -1) {
    return "Ingresso";
  }

  // Se è un file camera generico (IMG, DSC, numeri) o se non capisce: scrive il tipo immobile (es. Appartamento)
  return fallbackTipo;
}

function getListaCartelleDrive() {
  return getListaCartelleDriveUtente();
}

/**
 * 📂 Recupera la lista di tutte le cartelle Google Drive dell'utente per il menu 1-Tap da cellulare
 * Scansiona in modo prioritario la Cartella Master "1ftayZvmtRjwIxZd_ctBSy0wuTH_3lijM" e tutte le sue sottocartelle
 */
function getListaCartelleDriveUtente() {
  try {
    var result = [];
    var seenIds = {};

    function aggiungiCartella(f, prefisso) {
      if (!f) return;
      try {
        var fId = f.getId();
        if (seenIds[fId]) return;
        seenIds[fId] = true;
        var fName = (prefisso ? (prefisso + " ") : "") + f.getName();
        result.push({
          id: fId,
          name: fName,
          fileCount: 0,
          url: f.getUrl()
        });
      } catch(e) {}
    }

    // 1. Scansiona prioritariamente la Cartella Master Progetti se accessibile
    var masterId = (typeof DRIVE_MASTER_FOLDER_ID !== 'undefined' && DRIVE_MASTER_FOLDER_ID) ? DRIVE_MASTER_FOLDER_ID : "1ftayZvmtRjwIxZd_ctBSy0wuTH_3lijM";
    try {
      var masterFolder = DriveApp.getFolderById(masterId);
      if (masterFolder) {
        aggiungiCartella(masterFolder, "🌟 [CARTELLA MASTER]");
        var subFolders = masterFolder.getFolders();
        while (subFolders.hasNext()) {
          var sf = subFolders.next();
          aggiungiCartella(sf, "📂");
        }
      }
    } catch(eMaster) {
      console.warn("Cartella master Drive non trovata:", eMaster.toString());
    }

    // 2. Cartelle nella Root del Google Drive dell'utente
    try {
      var rootFolders = DriveApp.getRootFolder().getFolders();
      while (rootFolders.hasNext() && result.length < 40) {
        aggiungiCartella(rootFolders.next(), "📁");
      }
    } catch(eRoot) {
      var errR = eRoot.toString();
      if (errR.indexOf('autorizzazione') !== -1 || errR.indexOf('auth/drive') !== -1) {
        return { success: false, unauthorized: true, error: "Autorizzazione Google Drive necessaria" };
      }
    }

    // 3. Tutte le cartelle di Google Drive dell'utente
    try {
      var allF = DriveApp.getFolders();
      while (allF.hasNext() && result.length < 80) {
        aggiungiCartella(allF.next(), "📁");
      }
    } catch(eAll) {
      console.warn("Avviso allF:", eAll.toString());
    }

    // 4. Cartelle condivise o trovate tramite ricerca
    try {
      if (result.length < 15) {
        var searchF = DriveApp.searchFolders("trashed = false");
        while (searchF.hasNext() && result.length < 60) {
          aggiungiCartella(searchF.next(), "📂");
        }
      }
    } catch(eSearch) {}

    // Ordina alfabeticamente
    result.sort(function(a, b) {
      return a.name.localeCompare(b.name);
    });

    result.success = true;
    result.folders = result;
    return result;
  } catch(e) {
    var errStr = e.toString();
    if (errStr.indexOf('autorizzazione') !== -1 || errStr.indexOf('auth/drive') !== -1) {
      return { success: false, unauthorized: true, error: "Autorizzazione Google Drive necessaria" };
    }
    console.warn("getListaCartelleDriveUtente:", errStr);
    var fallback = [];
    fallback.success = false;
    fallback.folders = [];
    fallback.error = errStr;
    return fallback;
  }
}

/**
 * 🔑 FUNZIONE MASTER 1-CLICK PER AUTORIZZARE TUTTI I PERMESSI GOOGLE (DRIVE + TRIGGERS + SHEETS)
 * Esegui questa funzione nell'editor Google Apps Script per concedere tutti i permessi in un colpo solo!
 */
function autorizzaTuttiIPermessiGoogle() {
  // 1. Permesso Google Drive
  var root = DriveApp.getRootFolder();
  var masterId = "1ftayZvmtRjwIxZd_ctBSy0wuTH_3lijM";
  var f = DriveApp.getFolderById(masterId);
  var nomeFolder = f ? f.getName() : "Root";

  // 2. Permesso ScriptApp (Triggers e Maratone)
  var trigs = ScriptApp.getProjectTriggers();

  // 3. Permesso Spreadsheet
  var ss = SpreadsheetApp.getActiveSpreadsheet() || (typeof getSpreadsheetSicuro === 'function' ? getSpreadsheetSicuro() : null);

  Logger.log("✅ TUTTI I PERMESSI GOOGLE (DRIVE + TRIGGERS + SHEETS) AUTORIZZATI CON SUCCESSO!");
  return "✅ TUTTI I PERMESSI GOOGLE AUTORIZZATI CON SUCCESSO PER: " + nomeFolder;
}

function autorizzaAccessoGoogleDrive() {
  return autorizzaTuttiIPermessiGoogle();
}

/**
 * 🖼️ Genera anteprima visuale veloce dei file foto/video all'interno di una cartella Drive
 */
function getAnteprimaFileCartellaDrive(folderIdOrName) {
  try {
    var folder = null;
    var query = (folderIdOrName || "").trim();
    if (!query) return [];

    var folderIdMatch = query.match(/folders\/([a-zA-Z0-9_-]+)/) || query.match(/id=([a-zA-Z0-9_-]+)/);
    var folderId = folderIdMatch ? folderIdMatch[1] : (query.length > 20 && query.indexOf(' ') === -1 ? query : null);

    if (folderId) {
      try { folder = DriveApp.getFolderById(folderId); } catch(e1) {}
    }
    if (!folder) {
      try {
        var folders = DriveApp.getFoldersByName(query);
        if (folders.hasNext()) folder = folders.next();
      } catch(e2) {}
    }
    if (!folder) return [];

    var result = [];
    var files = folder.getFiles();
    var count = 0;

    while (files.hasNext() && count < 24) {
      var file = files.next();
      var mime = file.getMimeType();
      var isImage = mime.indexOf("image/") !== -1;
      var isVideo = mime.indexOf("video/") !== -1;

      if (!isImage && !isVideo) continue;

      try { file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); } catch(es) {}
      var fileUrl = convertiUrlDriveDirect(file.getUrl());

      result.push({
        id: file.getId(),
        name: file.getName(),
        mime: mime,
        url: fileUrl,
        isImage: isImage,
        isVideo: isVideo
      });

      count++;
    }

    return result;
  } catch(e) {
    var errStr = e.toString();
    if (errStr.indexOf('autorizzazione') === -1 && errStr.indexOf('auth/drive') === -1) {
      inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "getAnteprimaFileCartellaDrive", errStr);
    }
    console.warn("getAnteprimaFileCartellaDrive:", errStr);
    return [];
  }
}

/**
 * 📋 GESTIONE METADATI SCHEDA IMMOBILE & REGIA DARIA
 */
function salvaSchedaImmobileDati(tabName, scheda) {
  try {
    if (!tabName || !scheda) return { success: false, error: "Dati mancanti" };
    var cleanTab = String(tabName).replace(/\s+/g, '_');
    var key = "SCHEDA_IMMOBILE_" + cleanTab;

    if (scheda.metriQuadri) scheda.metriQuadri = normalizzaMetriQuadri(scheda.metriQuadri);
    if (scheda.prezzo) scheda.prezzo = normalizzaPrezzo(scheda.prezzo);

    PropertiesService.getScriptProperties().setProperty(key, JSON.stringify(scheda));
    return { success: true, scheda: scheda };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function getSchedaImmobileDati(tabName) {
  try {
    if (!tabName) return {};
    var cleanTab = String(tabName).replace(/\s+/g, '_');
    var key = "SCHEDA_IMMOBILE_" + cleanTab;
    var raw = PropertiesService.getScriptProperties().getProperty(key);
    var obj = raw ? JSON.parse(raw) : {};

    // Fallback: se qualche valore manca, prova a recuperarlo dalla riga 2 del Foglio Google
    var ss = getSpreadsheetSicuro();
    if (ss) {
      var sheet = ss.getSheetByName(cleanTab);
      if (sheet && sheet.getLastRow() >= 2) {
        var r2 = sheet.getRange(2, 1, 1, 8).getValues()[0];
        if (!obj.prezzo && r2[1]) obj.prezzo = String(r2[1]).trim();
        if (!obj.metriQuadri && r2[2]) obj.metriQuadri = normalizzaMetriQuadri(r2[2]);
        if (!obj.tipoImmobile && r2[7]) {
          var tStr = String(r2[7]);
          var mTipo = tStr.split(' — ')[0] || '';
          if (mTipo) obj.tipoImmobile = mTipo.trim();
        }
      }
    }
    return obj;
  } catch(e) {
    return {};
  }
}

function normalizzaMetriQuadri(mqRaw) {
  if (!mqRaw) return "120 metri quadri";
  var s = String(mqRaw).trim();
  s = s.replace(/\s*m[q²]\b/gi, ' metri quadri');
  if (s.toLowerCase().indexOf('metri quadri') === -1) {
    var digits = s.match(/[\d.,]+/);
    if (digits) {
      s = digits[0] + " metri quadri";
    } else {
      s = s + " metri quadri";
    }
  }
  return s;
}

function normalizzaPrezzo(prezzoRaw) {
  if (!prezzoRaw) return "Trattativa Riservata";
  var s = String(prezzoRaw).trim();
  if (s.toLowerCase().indexOf('trattativa') !== -1 || s.toLowerCase() === 'riservata') return "Trattativa Riservata";
  if (s.indexOf('€') === -1 && s.match(/\d/)) {
    return "€ " + s;
  }
  return s;
}

/**
 * 🎙️ Genera testo descrittivo parlato per DarIA in base alla stanza, tipo immobile, MQ, zona, prezzo, stato e note.
 * Fortemente orientato sulle EMOZIONI e sul vissuto sensoriale dello specifico contesto della stanza.
 * Rispetta rigorosamente la terminazione con ' — Immobiliare Giancani' e l'uso di 'metri quadri'.
 */
function generaTestoDescrittivoStanza(stanzaNome, scheda, nomeCartella) {
  scheda = scheda || {};
  var cartellaClean = (nomeCartella || "Immobile").replace(/_/g, ' ');
  var tipo = (scheda.tipoImmobile || "questo immobile").trim();
  var mq = normalizzaMetriQuadri(scheda.metriQuadri);
  var zona = (scheda.zona || "").trim();
  var zonaFrase = zona ? (" a " + zona) : "";
  var prezzo = normalizzaPrezzo(scheda.prezzo);
  var prezzoFrase = (prezzo && prezzo !== "Trattativa Riservata") ? (" proposto a " + prezzo) : " con trattativa riservata";
  
  var stato = (scheda.stato || "rifinito con cura").trim();
  if (scheda.statoDettaglio && scheda.statoDettaglio.trim()) {
    stato += " con " + scheda.statoDettaglio.trim();
  }

  var note = "";
  if (scheda.noteDaria && scheda.noteDaria.trim()) {
    var n = scheda.noteDaria.trim();
    if (!n.endsWith(".") && !n.endsWith("!") && !n.endsWith("?")) n += ".";
    note = " " + n;
  }

  var st = (stanzaNome || "Ambiente").trim();
  var stLow = st.toLowerCase();

  // 1. TENTATIVO GENERAZIONE EMOZIONALE INTELLIGENTE VIA GROQ AI MULTI-KEY (se disponibile)
  if (typeof eseguiChiamataGroqMultiKey === 'function') {
    try {
      var systemPromptAI = "Sei la voce narrante televisiva virtuale ed empatica di DarIA per Immobiliare Giancani.\n" +
        "Il tuo compito è comporre una descrizione emozionale indimenticabile per un ambiente immobiliare durante il tour virtuale in diretta.\n" +
        "REGOLE TASSATIVE:\n" +
        "1. EMOZIONI E CONTESTO: Parla profondamente delle emozioni, dei profumi, della luce e delle sensazioni del vivere quotidiano legate alla stanza specifica (es. i pranzi in famiglia e il profumo del caffè in cucina, il relax sul divano e il calore dell'accoglienza nel living, l'intimità protetta e il silenzio riposante nella camera da letto, la cura di sé e il benessere come in una spa nel bagno, la brezza serale e gli aperitivi al tramonto sul terrazzo, ecc.).\n" +
        "2. METRI QUADRI: Scrivi SEMPRE per esteso 'metri quadri', non abbreviare mai in 'mq' o 'm2'.\n" +
        "3. PERSONAL BRANDING: La frase deve concludersi TASSATIVAMENTE mettendo in risalto ' — Immobiliare Giancani'.\n" +
        "4. LUNGHEZZA: Massimo 3 frasi armoniose, fluide e naturali per la lettura vocale (circa 50-70 parole).";

      var userPromptAI = "Crea una descrizione emozionale ad alto impatto per:\n" +
        "- Stanza/Ambiente: " + st + "\n" +
        "- Tipologia: " + tipo + "\n" +
        "- Zona: " + (zona || "Favara ed Agrigento") + "\n" +
        "- Superficie: " + mq + "\n" +
        "- Condizioni/Finiture: " + stato + "\n" +
        (note ? ("- Dettagli extra: " + note + "\n") : "") +
        "- Prezzo: " + prezzo + "\n\n" +
        "Restituisci direttamente il testo finito pronto per essere letto da DarIA:";

      var aiText = eseguiChiamataGroqMultiKey(systemPromptAI, userPromptAI, { max_tokens: 220, temperature: 0.65 });
      if (aiText && aiText.length > 50) {
        var cleanAi = aiText.replace(/```[a-z]*/gi, '').replace(/```/g, '').trim();
        cleanAi = normalizzaMetriQuadri(cleanAi);
        if (cleanAi.indexOf('Immobiliare Giancani') === -1) {
          cleanAi += " — Immobiliare Giancani";
        } else if (!cleanAi.endsWith("— Immobiliare Giancani")) {
          cleanAi = cleanAi.replace(/\s*—?\s*Immobiliare Giancani\s*$/i, '') + " — Immobiliare Giancani";
        }
        return cleanAi;
      }
    } catch(errAI) {
      console.warn("Generazione Groq AI non riuscita, attivo generatore emozionale procedurale:", errAI);
    }
  }

  // 2. GENERATORE EMOZIONALE PROCEDURALE AVANZATO (FALLBACK AD ALTA QUALITÀ LIRICA E SENSORIALE)
  var testo = "";

  if (stLow.indexOf('cucina') !== -1 || stLow.indexOf('cottura') !== -1 || stLow.indexOf('tinello') !== -1) {
    testo = "Entriamo nel cuore pulsante e conviviale della casa: una splendida cucina dove ogni risveglio profuma di caffè e i pranzi della domenica riuniscono chi amate in un'atmosfera calda e autentica. Uno spazio accogliente e " + stato + ", che celebra al meglio i " + mq + " totali di " + (tipo.toLowerCase().indexOf('questo') !== -1 ? tipo : "questo " + tipo) + zonaFrase + "," + prezzoFrase + "." + note + " Il luogo ideale dove condividere sorrisi, ricette e ricordi preziosi con tutta la famiglia. — Immobiliare Giancani";
  } else if (stLow.indexOf('salon') !== -1 || stLow.indexOf('soggiorno') !== -1 || stLow.indexOf('living') !== -1 || stLow.indexOf('pranzo') !== -1 || stLow.indexOf('salotto') !== -1) {
    testo = "Ammirate la magnificenza di questa luminosa zona giorno: un salone concepito per avvolgervi in una sensazione di assoluto benessere e prestigio. Lasciatevi cullare dalla luce pomeridiana che esalta ogni finitura e immaginate la gioia di rilassarvi sul divano dopo una lunga giornata o di brindare con gli amici in uno spazio " + stato + ", che nobilita i suoi " + mq + " complessivi" + zonaFrase + "," + prezzoFrase + "." + note + " Il piacere puro e impagabile di sentirsi finalmente e profondamente a casa. — Immobiliare Giancani";
  } else if (stLow.indexOf('camera') !== -1 || stLow.indexOf('letto') !== -1 || stLow.indexOf('matrimoniale') !== -1 || stLow.indexOf('notte') !== -1) {
    testo = "Varcate la soglia di questa intima camera padronale: una vera oasi di pace e silenzio dove il riposo diventa un abbraccio rigenerante per mente e corpo. Uno spazio ovattato, morbido e " + stato + ", progettato per regalarvi privacy totale e risvegli sereni all'interno dei " + mq + " di " + (tipo.toLowerCase().indexOf('questo') !== -1 ? tipo : "questo " + tipo) + zonaFrase + "," + prezzoFrase + "." + note + " Il vostro rifugio esclusivo dove ricaricare le energie e sognare in piena tranquillità. — Immobiliare Giancani";
  } else if (stLow.indexOf('cameretta') !== -1 || stLow.indexOf('ragazzi') !== -1 || stLow.indexOf('bambin') !== -1 || stLow.indexOf('studio') !== -1) {
    testo = "Ecco un ambiente arioso, protetto e pieno di energia positiva, perfetto per accompagnare la crescita, i giochi e le passioni dei vostri figli o per ospitare il vostro studio personale. Uno spazio versatile, allegro e " + stato + ", meravigliosamente integrato nei " + mq + " dell'abitazione" + zonaFrase + "," + prezzoFrase + "." + note + " Il nido stimolante e sicuro dove coltivare sogni e progetti per il futuro. — Immobiliare Giancani";
  } else if (stLow.indexOf('bagno') !== -1 || stLow.indexOf('servizio') !== -1 || stLow.indexOf('lavanderia') !== -1 || stLow.indexOf('wc') !== -1 || stLow.indexOf('toilette') !== -1) {
    testo = "Concedetevi una parentesi di puro benessere e freschezza in questo bagno curato nei minimi dettagli, pensato come una piccola spa privata all'interno della propria casa. Superfici armoniose, igiene impeccabile e comfort moderno in un contesto " + stato + ", a servizio dei " + mq + " complessivi dell'immobile" + zonaFrase + "," + prezzoFrase + "." + note + " Lo spazio intimo ideale per iniziare e concludere ogni giornata con energia e serenità. — Immobiliare Giancani";
  } else if (stLow.indexOf('balcon') !== -1 || stLow.indexOf('terrazz') !== -1 || stLow.indexOf('verand') !== -1 || stLow.indexOf('loggia') !== -1 || stLow.indexOf('panorama') !== -1 || stLow.indexOf('vista') !== -1) {
    testo = "Aprite le porte ed entrate in questo suggestivo terrazzo: una magnifica apertura verso l'orizzonte dove respirare libertà e godersi la brezza siciliana. Immaginate la magia di un aperitivo al tramonto sotto le stelle o la quiete di una colazione all'aperto, un plus irrinunciabile che valorizza i " + mq + " di " + (tipo.toLowerCase().indexOf('questo') !== -1 ? tipo : "questo " + tipo) + zonaFrase + "," + prezzoFrase + "." + note + " Lo sfogo all'aperto che trasforma ogni bella giornata in un momento di vacanza quotidiana. — Immobiliare Giancani";
  } else if (stLow.indexOf('giardin') !== -1 || stLow.indexOf('corte') !== -1 || stLow.indexOf('portic') !== -1 || stLow.indexOf('estern') !== -1) {
    testo = "Riconnettetevi con la natura in questo splendido giardino riservato: un angolo verde e profumato dove i bambini e gli animali domestici possono correre felici in totale sicurezza. Il luogo perfetto per pranzi e grigliate all'aria aperta nelle calde giornate estive, a corredo dei " + mq + " della proprietà" + zonaFrase + "," + prezzoFrase + "." + note + " Un'emozione di verde e libertà che non ha prezzo per tutta la famiglia. — Immobiliare Giancani";
  } else if (stLow.indexOf('garage') !== -1 || stLow.indexOf('box') !== -1 || stLow.indexOf('auto') !== -1) {
    testo = "La totale tranquillità mentale di rientrare e trovare sempre il proprio posto auto sicuro e riparato: ecco il comodo garage a servizio di " + (tipo.toLowerCase().indexOf('questo') !== -1 ? tipo : "questo " + tipo) + zonaFrase + ". Uno spazio custodito e versatile che completa i " + mq + " complessivi," + prezzoFrase + "." + note + " La serenità e la comodità quotidiana di proteggere il proprio veicolo e i propri hobby. — Immobiliare Giancani";
  } else if (stLow.indexOf('magazzin') !== -1 || stLow.indexOf('deposit') !== -1 || stLow.indexOf('cantin') !== -1 || stLow.indexOf('ripostigli') !== -1) {
    testo = "Uno spazio prezioso che dona armonia e ordine a tutta la casa: questo pratico " + st.toLowerCase() + " " + stato + " è il perfetto alleato per custodire attrezzature e ricordi in totale facilità, a corredo dei " + mq + " totali" + zonaFrase + "," + prezzoFrase + "." + note + " La funzionalità intelligente che rende l'abitare quotidiano rilassante e organizzato. — Immobiliare Giancani";
  } else if (stLow.indexOf('corridoio') !== -1 || stLow.indexOf('disimpegno') !== -1 || stLow.indexOf('ingresso') !== -1 || stLow.indexOf('entrata') !== -1 || stLow.indexOf('atrio') !== -1) {
    testo = "La rassicurante sensazione del varcare la soglia e sentirsi accolti nel proprio nido protetto: questo elegante ingresso " + stato + " distribuisce con armonia e proporzione i " + mq + " di " + (tipo.toLowerCase().indexOf('questo') !== -1 ? tipo : "questo " + tipo) + zonaFrase + "," + prezzoFrase + "." + note + " Il primo caloroso benvenuto che apre le porte a nuovi capitoli di vita felice. — Immobiliare Giancani";
  } else {
    testo = "Ammirate l'atmosfera calda e curata di " + st + " in " + (tipo.toLowerCase().indexOf('questo') !== -1 ? tipo : "questo splendido " + tipo) + zonaFrase + ". Un ambiente " + stato + " e ricco di fascino, studiato per regalarvi emozioni autentiche e massimo comfort all'interno dei suoi " + mq + " complessivi," + prezzoFrase + "." + note + " Un'opportunità immobiliare esclusiva presentata con passione e competenza da Immobiliare Giancani.";
  }

  // Rispetta rigorosamente la regola finale: deve sempre terminare con — Immobiliare Giancani
  if (testo.indexOf("— Immobiliare Giancani") === -1 && testo.indexOf("Immobiliare Giancani") === -1) {
    testo += " — Immobiliare Giancani";
  } else if (!testo.endsWith("— Immobiliare Giancani")) {
    testo = testo.replace(/\s*—?\s*Immobiliare Giancani\s*$/i, '') + " — Immobiliare Giancani";
  }

  return normalizzaMetriQuadri(testo);
}

/**
 * 🔄 Sincronizza una cartella Google Drive esistente popolando il Foglio Google corrispondente
 */
function sincronizzaDaCartellaDriveEsistente(data) {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, error: "Database Google Sheets non accessibile." };

    var folderQuery = (data && data.folderInput ? data.folderInput : "").trim();
    var logoPos = (data && data.logoPos) ? data.logoPos : "centrale_semitrasparente";
    var datiScheda = (data && data.datiScheda) ? data.datiScheda : {};

    if (!folderQuery) return { success: false, error: "Inserisci il nome o l'ID della cartella Google Drive." };

    // Pulisci query da prefissi grafici o emoji
    var cleanFolderQuery = folderQuery.replace(/^(\s*🌟\s*\[CARTELLA MASTER\]|\s*📂|\s*📁)\s*/i, '').trim();

    var folderIdMatch = cleanFolderQuery.match(/folders\/([a-zA-Z0-9_-]+)/) || cleanFolderQuery.match(/id=([a-zA-Z0-9_-]+)/) || folderQuery.match(/folders\/([a-zA-Z0-9_-]+)/) || folderQuery.match(/id=([a-zA-Z0-9_-]+)/);
    var folder = null;
    var folderId = folderIdMatch ? folderIdMatch[1] : ((cleanFolderQuery.length > 20 && cleanFolderQuery.indexOf(' ') === -1) ? cleanFolderQuery : null);

    if (folderId) {
      try { folder = DriveApp.getFolderById(folderId); } catch(errF) {}
    }
    if (!folder && cleanFolderQuery) {
      try {
        var folders = DriveApp.getFoldersByName(cleanFolderQuery);
        if (folders.hasNext()) folder = folders.next();
      } catch(eClean) {}
    }
    if (!folder && folderQuery !== cleanFolderQuery) {
      try {
        var foldersRaw = DriveApp.getFoldersByName(folderQuery);
        if (foldersRaw.hasNext()) folder = foldersRaw.next();
      } catch(eRaw) {}
    }

    if (!folder) {
      return { success: false, error: "Cartella Google Drive non trovata: '" + (cleanFolderQuery || folderQuery) + "'. Verifica il nome o l'ID." };
    }

    var nomeCartella = folder.getName();
    var nomeTab = sanitizzaNomeTabPerGoogleSheets(nomeCartella);

    // Salva metadati scheda immobile se forniti, altrimenti leggi esistenti
    if (datiScheda && (datiScheda.tipoImmobile || datiScheda.metriQuadri || datiScheda.zona || datiScheda.prezzo || datiScheda.noteDaria)) {
      salvaSchedaImmobileDati(nomeTab, datiScheda);
    } else {
      datiScheda = getSchedaImmobileDati(nomeTab);
    }

    var prezzoImmobile = normalizzaPrezzo(datiScheda.prezzo || "Trattativa Riservata");
    var mqImmobile = normalizzaMetriQuadri(datiScheda.metriQuadri || "120 metri quadri");

    var sheet = ss.getSheetByName(nomeTab);
    if (!sheet) {
      sheet = ss.insertSheet(nomeTab);
      sheet.appendRow([
        "Stanza_Ambiente", 
        "Prezzo_B2", 
        "MQ_C2", 
        "Titolo_D2", 
        "Tipo_Media_E2", 
        "Testo_Parlato_F2", 
        "Lingua_G2", 
        "Ticker_H2", 
        "Link_Annuncio_I2",
        "Audio_Colonna_J"
      ]);
      sheet.getRange("A1:J1").setFontWeight("bold").setBackground("#c9a35e").setFontColor("#ffffff");
    }

    var existingUrls = [];
    if (sheet.getLastRow() > 1) {
      var dataVals = sheet.getRange(2, 1, sheet.getLastRow() - 1, 10).getValues();
      dataVals.forEach(function(r) {
        if (r[0]) existingUrls.push(r[0].toString().trim());
      });
    }

    var files = folder.getFiles();
    var nuoviCaricati = 0;

    while (files.hasNext()) {
      var file = files.next();
      var mime = file.getMimeType();
      var isImage = mime.indexOf("image/") !== -1;
      var isVideo = mime.indexOf("video/") !== -1;

      if (!isImage && !isVideo) continue;

      try { file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); } catch(es) {}
      var fileUrl = convertiUrlDriveDirect(file.getUrl());

      var giaPresente = existingUrls.some(function(u) { return u.indexOf(file.getId()) !== -1 || u === fileUrl; });
      if (giaPresente) continue;

      var fileName = file.getName();
      var rawBase = fileName.split('.')[0].trim();
      var tipoDefault = estraiTipoImmobileDaNomeCartella(nomeCartella);
      var stanzaNome = deduciStanzaOImmobile(rawBase, tipoDefault);

      var lower = fileName.toLowerCase();
      var mediaType = 'foto';
      if (lower.indexOf('360') !== -1 || stanzaNome.toLowerCase().indexOf('360') !== -1) mediaType = '360';
      else if (isVideo) mediaType = 'video';

      var cartellaClean = nomeCartella.replace(/_/g, ' ');
      var testoDescrittivo = generaTestoDescrittivoStanza(stanzaNome, datiScheda, nomeCartella);

      var tickerText = (datiScheda.tipoImmobile || cartellaClean) + 
                       (datiScheda.zona ? " " + datiScheda.zona : "") + 
                       " (" + mqImmobile + ") — " + stanzaNome + " | Immobiliare Giancani";

      sheet.appendRow([
        fileUrl, 
        prezzoImmobile, 
        mqImmobile, 
        stanzaNome, 
        mediaType + "|" + logoPos, 
        testoDescrittivo, 
        "it-IT", 
        tickerText, 
        "https://www.immobiliaregiancani.it",
        ""
      ]);

      nuoviCaricati++;
    }

    setImmobileAttivoInDiretta(nomeTab);

    // 🚀 NUOVA ENTRATA: Pubblica istantaneamente l'immobile su WordPress in prima linea!
    if (sheet.getLastRow() === 2) {
      try {
        inviaNuovoImmobileAWordPress(datiScheda, nomeCartella, fileUrl, testoDescrittivo);
      } catch(eWp) {
        Logger.log("Errore pubblicazione WP: " + eWp.toString());
      }
    }

    return {
      success: true,
      tabName: nomeTab,
      nuoviCaricati: nuoviCaricati
    };
  } catch(e) {
    inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "sincronizzaDaCartellaDriveEsistente", e.toString());
    return { success: false, error: e.toString() };
  }
}

function getOrCreateDriveFolder(parentFolder, folderName) {
  var cleanName = (folderName || "Nuovo_Immobile").trim();

  // 1. Prova all'interno della cartella master se specificata o presente
  var master = parentFolder;
  if (!master && typeof DRIVE_MASTER_FOLDER_ID !== 'undefined' && DRIVE_MASTER_FOLDER_ID) {
    try { master = DriveApp.getFolderById(DRIVE_MASTER_FOLDER_ID); } catch(eM) {}
  }
  
  if (master) {
    try {
      var folders = master.getFoldersByName(cleanName);
      if (folders.hasNext()) return folders.next();
      var newF = master.createFolder(cleanName);
      try { newF.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); } catch(eSh) {}
      return newF;
    } catch(errMasterCreate) {
      console.warn("Impossibile creare cartella nella master folder (" + errMasterCreate.toString() + "). Fallback su Drive root...");
    }
  }

  // 2. Fallback su DriveApp generale (cerca prima di creare)
  try {
    var generalFolders = DriveApp.getFoldersByName(cleanName);
    if (generalFolders.hasNext()) return generalFolders.next();
    var rootF = DriveApp.createFolder(cleanName);
    try { rootF.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); } catch(eSh2) {}
    return rootF;
  } catch(errRoot) {
    console.warn("Fallback su getRootFolder:", errRoot.toString());
    try {
      var rootFolder = DriveApp.getRootFolder();
      var rFolders = rootFolder.getFoldersByName(cleanName);
      if (rFolders.hasNext()) return rFolders.next();
      var createdRoot = rootFolder.createFolder(cleanName);
      try { createdRoot.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); } catch(eSh3) {}
      return createdRoot;
    } catch(errFinal) {
      inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "getOrCreateDriveFolder", errFinal.toString());
      return null;
    }
  }
}

function getOrCreateSheetSubFolder(sheetName) {
  try {
    return getOrCreateDriveFolder(null, sheetName);
  } catch(e) {
    return null;
  }
}

function salvaModificaStanzaGalleria(tabName, rowIndex, nuovaStanza) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = tabName ? ss.getSheetByName(tabName) : getActiveImmobileSheet(ss, null);
    if (!sheet) return { success: false, error: "Foglio non trovato" };
    sheet.getRange(rowIndex, 4).setValue(nuovaStanza);

    // Rigenera la descrizione per la stanza modificata usando la scheda immobile e termina con Immobiliare Giancani
    var cleanTab = sheet.getName();
    var scheda = getSchedaImmobileDati(cleanTab);
    var nuovoTesto = generaTestoDescrittivoStanza(nuovaStanza, scheda, cleanTab);
    sheet.getRange(rowIndex, 6).setValue(nuovoTesto); // Salva in Colonna F

    // Aggiorna anche il ticker in Colonna H
    var mq = normalizzaMetriQuadri(scheda.metriQuadri || "120 metri quadri");
    var tickerText = (scheda.tipoImmobile || cleanTab.replace(/_/g, ' ')) + 
                     (scheda.zona ? " " + scheda.zona : "") + 
                     " (" + mq + ") — " + nuovaStanza + " | Immobiliare Giancani";
    sheet.getRange(rowIndex, 8).setValue(tickerText);

    return { success: true, stanza: nuovaStanza, nuovoTesto: nuovoTesto };
  } catch(e) {
    inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "salvaModificaStanzaGalleria", e.toString());
    return { success: false, error: e.toString() };
  }
}

function salvaModificaTestoGalleria(tabName, rowIndex, nuovoTesto) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = tabName ? ss.getSheetByName(tabName) : getActiveImmobileSheet(ss, null);
    if (!sheet) return { success: false, error: "Foglio non trovato" };
    var t = pulisciTestoPerTTSBackend(nuovoTesto);
    sheet.getRange(rowIndex, 6).setValue(t); // Colonna F
    return { success: true, testo: t };
  } catch(e) {
    inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "salvaModificaTestoGalleria", e.toString());
    return { success: false, error: e.toString() };
  }
}

function salvaModificheGalleriaBulk(tabName, modifiche) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = tabName ? ss.getSheetByName(tabName) : getActiveImmobileSheet(ss, null);
    if (!sheet || !modifiche || modifiche.length === 0) return { success: false };

    for (var i = 0; i < modifiche.length; i++) {
      var m = modifiche[i];
      if (m.rowIndex && m.rowIndex >= 2) {
        if (m.stanza) sheet.getRange(m.rowIndex, 4).setValue(m.stanza);
        if (m.tipo) {
          var tMedia = (m.tipo || 'foto').toLowerCase().trim();
          if (tMedia !== '360' && tMedia !== 'video') tMedia = 'foto';
          sheet.getRange(m.rowIndex, 5).setValue(tMedia);
        }
        if (m.testo) {
          var t = pulisciTestoPerTTSBackend(m.testo);
          sheet.getRange(m.rowIndex, 6).setValue(t); // Colonna F
        }
      }
    }
    return { success: true, count: modifiche.length };
  } catch(e) {
    inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "salvaModificheGalleriaBulk", e.toString());
    return { success: false, error: e.toString() };
  }
}

function modificaTipoMediaGalleria(tabName, rowIndex, nuovoTipo) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = tabName ? ss.getSheetByName(tabName) : getActiveImmobileSheet(ss, null);
    if (!sheet) return { success: false, error: "Foglio non trovato" };
    var tMedia = (nuovoTipo || 'foto').toLowerCase().trim();
    if (tMedia !== '360' && tMedia !== 'video') tMedia = 'foto';
    sheet.getRange(rowIndex, 5).setValue(tMedia);
    return { success: true, tipo: tMedia };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function eliminaMediaGalleria(tabName, rowIndex) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = tabName ? ss.getSheetByName(tabName) : getActiveImmobileSheet(ss, null);
    if (!sheet) return { success: false, error: "Foglio non trovato" };
    sheet.deleteRow(rowIndex);
    return { success: true };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function eliminaMediaGalleriaBulk(tabName, indices) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = tabName ? ss.getSheetByName(tabName) : getActiveImmobileSheet(ss, null);
    if (!sheet || !indices || indices.length === 0) return { success: false };
    indices.sort(function(a, b){ return b - a; });
    indices.forEach(function(idx) {
      if (idx >= 2 && idx <= sheet.getLastRow()) sheet.deleteRow(idx);
    });
    return { success: true, count: indices.length };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function rigeneraTestiAutoVision(tabName, forzaTutti) {
  return analizzaStanzeMassivoGemini(tabName, forzaTutti);
}

function salvaAudioInColonnaJ(tabName, rowIndex, audioUrl) { return { success: true }; }
function convertiTuttiILinkGoogleTranslateInDriveMP3(tabName) { return { success: true }; }

/**
 * 🖼️ Recupera l'elenco completo dei media per la galleria di un immobile
 */
function getMediaPerImmobile(tabName) {
  try {
    var ss = getSpreadsheetSicuro();
    var sheet = tabName ? ss.getSheetByName(tabName) : null;
    if (!sheet) sheet = getActiveImmobileSheet(ss, null);
    if (!sheet || sheet.getLastRow() < 2) return [];

    var lastRow = sheet.getLastRow();
    var lastCol = Math.max(sheet.getLastColumn(), 10);
    var rows = sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();

    var result = [];
    for (var i = 0; i < rows.length; i++) {
      var row = rows[i];
      var testo = (row[5] || '').toString().trim(); // Colonna F = Testo Parlato
      var stanza = (row[3] || '').toString().trim(); // Colonna D
      var tipoTab = estraiTipoImmobileDaNomeCartella(tabName || (sheet ? sheet.getName() : ''));
      if (!stanza || stanza.toLowerCase() === 'ambiente' || stanza.toLowerCase().indexOf('ambiente ') === 0) {
        stanza = tipoTab;
      }

      var hasContent = row.some(function(v) { return (v || '').toString().trim().length > 0; });
      if (!hasContent) continue;

      var rawMedia = (row[0] || '').toString().trim();
      var mediaUrl = convertiUrlDriveDirect(rawMedia);
      var tipo = (row[4] || 'foto').toString().toLowerCase().trim();
      if (tipo.indexOf('360') !== -1 || stanza.toLowerCase().indexOf('360') !== -1) tipo = '360';
      else if (tipo.indexOf('video') !== -1 || rawMedia.match(/\.(mp4|mov|avi|mkv)/i)) tipo = 'video';
      else tipo = 'foto';

      result.push({
        rowIndex: i + 2,
        idx: i + 2,
        stanza: stanza || tipoTab,
        tipo: tipo,
        tipoMedia: tipo,
        url: mediaUrl,
        mediaUrl: mediaUrl,
        testo: testo,
        colJ: (row[9] || '').toString().trim(),
        rowValues: row.map(function(v) { return (v || '').toString().trim(); })
      });
    }
    return result;
  } catch(e) {
    inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "getMediaPerImmobile", e.toString());
    return [];
  }
}

/**
 * 📤 Caricamento Nuova Proprietà e File da Mobile
 */
function caricaNuovaProprietaEFile(data) {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, error: "Spreadsheet non accessibile" };

    var rawNome = (data && data.nomeCartella ? data.nomeCartella : "Nuovo_Immobile").trim();
    var nomeTab = sanitizzaNomeTabPerGoogleSheets(rawNome);
    var nomeCartella = rawNome.replace(/\s+/g, '_');
    var datiScheda = (data && data.datiScheda) ? data.datiScheda : {};

    if (datiScheda && (datiScheda.tipoImmobile || datiScheda.metriQuadri || datiScheda.zona || datiScheda.prezzo || datiScheda.noteDaria)) {
      salvaSchedaImmobileDati(nomeTab, datiScheda);
    } else {
      datiScheda = getSchedaImmobileDati(nomeTab);
    }

    var prezzoImmobile = normalizzaPrezzo(datiScheda.prezzo || "Trattativa Riservata");
    var mqImmobile = normalizzaMetriQuadri(datiScheda.metriQuadri || "120 metri quadri");

    var sheet = ss.getSheetByName(nomeTab);
    if (!sheet) {
      sheet = ss.insertSheet(nomeTab);
      sheet.appendRow([
        "Stanza_Ambiente", 
        "Prezzo_B2", 
        "MQ_C2", 
        "Titolo_D2", 
        "Tipo_Media_E2", 
        "Testo_Parlato_F2", 
        "Lingua_G2", 
        "Ticker_H2", 
        "Link_Annuncio_I2",
        "Audio_Colonna_J"
      ]);
      sheet.getRange("A1:J1").setFontWeight("bold").setBackground("#c9a35e").setFontColor("#ffffff");
    }

    var folder = getOrCreateDriveFolder(null, nomeCartella);
    if (!folder) {
      var errFold = "Impossibile creare o accedere alla cartella Google Drive: " + nomeCartella;
      inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "caricaNuovaProprietaEFile", errFold);
      return { success: false, error: errFold };
    }

    var fileCaricati = [];
    var files = (data && data.files) ? data.files : [];

    for (var i = 0; i < files.length; i++) {
      var fileObj = files[i];
      if (!fileObj || !fileObj.base64Data) continue;
      var mediaType = fileObj.tipoMedia || 'foto';

      var rawB64 = fileObj.base64Data;
      if (rawB64.indexOf(',') !== -1) rawB64 = rawB64.split(',')[1];
      rawB64 = rawB64.replace(/\s/g, '+');
      var bytes = Utilities.base64Decode(rawB64);
      var blob = Utilities.newBlob(bytes, fileObj.mimeType || 'image/jpeg', fileObj.fileName);

      var driveFile = folder.createFile(blob);
      try { driveFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); } catch(eSh) {}
      var fileUrl = "https://lh3.googleusercontent.com/d/" + driveFile.getId();

      var rawBase = fileObj.fileName.split('.')[0].trim();
      var tipoDefault = estraiTipoImmobileDaNomeCartella(nomeCartella);
      var stanzaNome = deduciStanzaOImmobile(rawBase, tipoDefault);

      var cartellaClean = nomeCartella.replace(/_/g, ' ');
      var testoDescrittivo = generaTestoDescrittivoStanza(stanzaNome, datiScheda, nomeCartella);

      var tickerText = (datiScheda.tipoImmobile || cartellaClean) + 
                       (datiScheda.zona ? " " + datiScheda.zona : "") + 
                       " (" + mqImmobile + ") — " + stanzaNome + " | Immobiliare Giancani";

      sheet.appendRow([
        fileUrl, 
        prezzoImmobile, 
        mqImmobile, 
        stanzaNome, 
        mediaType, 
        testoDescrittivo, 
        "it-IT", 
        tickerText, 
        "https://www.immobiliaregiancani.it",
        ""
      ]);

      fileCaricati.push({
        fileName: fileObj.fileName,
        url: fileUrl,
        stanza: stanzaNome,
        tipo: mediaType
      });
    }

    setImmobileAttivoInDiretta(nomeTab);

    // 🎵 Assicura e recupera la cartella Basi Musicali Professionali su Google Drive
    var basiFolder = getOrCreateBasiMusicaliDriveFolder();

    return {
      success: true,
      tabName: nomeTab,
      caricatiCount: fileCaricati.length,
      files: fileCaricati,
      cartellaImmobileUrl: (folder ? folder.getUrl() : ''),
      cartellaImmobileId: (folder ? folder.getId() : ''),
      cartellaBasiMusicaliUrl: basiFolder.url,
      cartellaBasiMusicaliId: basiFolder.id,
      basiMusicaliCount: (basiFolder.brani ? basiFolder.brani.length : 0)
    };
  } catch(e) {
    inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "caricaNuovaProprietaEFile", e.toString());
    return { success: false, error: e.toString() };
  }
}

/**
 * 📤 Caricamento Singolo File su Drive & Scheda Immobile con Notifica Dettagliata
 */
function caricaSingoloFileSuDriveEProprieta(data) {
  try {
    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, fileName: (data && data.file ? data.file.fileName : ''), error: "Spreadsheet non accessibile" };

    var rawNome = (data && data.nomeCartella ? data.nomeCartella : "Nuovo_Immobile").trim();
    var nomeTab = sanitizzaNomeTabPerGoogleSheets(rawNome);
    var nomeCartella = rawNome.replace(/\s+/g, '_');
    var datiScheda = (data && data.datiScheda) ? data.datiScheda : {};

    if (datiScheda && (datiScheda.tipoImmobile || datiScheda.metriQuadri || datiScheda.zona || datiScheda.prezzo || datiScheda.noteDaria)) {
      salvaSchedaImmobileDati(nomeTab, datiScheda);
    } else {
      datiScheda = getSchedaImmobileDati(nomeTab);
    }

    var prezzoImmobile = normalizzaPrezzo(datiScheda.prezzo || "Trattativa Riservata");
    var mqImmobile = normalizzaMetriQuadri(datiScheda.metriQuadri || "120 metri quadri");

    var sheet = ss.getSheetByName(nomeTab);
    if (!sheet) {
      sheet = ss.insertSheet(nomeTab);
      sheet.appendRow([
        "Stanza_Ambiente", 
        "Prezzo_B2", 
        "MQ_C2", 
        "Titolo_D2", 
        "Tipo_Media_E2", 
        "Testo_Parlato_F2", 
        "Lingua_G2", 
        "Ticker_H2", 
        "Link_Annuncio_I2",
        "Audio_Colonna_J"
      ]);
      sheet.getRange("A1:J1").setFontWeight("bold").setBackground("#c9a35e").setFontColor("#ffffff");
    }

    var folder = getOrCreateDriveFolder(null, nomeCartella);
    var fileObj = data ? data.file : null;
    if (!fileObj || !fileObj.base64Data) {
      return { success: false, fileName: (fileObj ? fileObj.fileName : 'Sconosciuto'), error: "Dati Base64 mancanti" };
    }

    if (!folder) {
      var errF = "Impossibile creare o accedere alla cartella Google Drive: " + nomeCartella;
      inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "caricaSingoloFileSuDriveEProprieta", errF);
      return { success: false, fileName: fileObj.fileName, error: errF };
    }

    var mediaType = fileObj.tipoMedia || 'foto';
    var rawB64 = fileObj.base64Data;
    if (rawB64.indexOf(',') !== -1) rawB64 = rawB64.split(',')[1];
    rawB64 = rawB64.replace(/\s/g, '+');
    var bytes = Utilities.base64Decode(rawB64);
    var blob = Utilities.newBlob(bytes, fileObj.mimeType || 'image/jpeg', fileObj.fileName);

    var driveFile = folder.createFile(blob);
    try { driveFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); } catch(eSh) {}
    var fileUrl = "https://lh3.googleusercontent.com/d/" + driveFile.getId();

    var rawBase = fileObj.fileName.split('.')[0].trim();
    var tipoDefault = estraiTipoImmobileDaNomeCartella(nomeCartella);
    var stanzaNome = deduciStanzaOImmobile(rawBase, tipoDefault);

    var cartellaClean = nomeCartella.replace(/_/g, ' ');
    var testoDescrittivo = generaTestoDescrittivoStanza(stanzaNome, datiScheda, nomeCartella);

    var tickerText = (datiScheda.tipoImmobile || cartellaClean) + 
                     (datiScheda.zona ? " " + datiScheda.zona : "") + 
                     " (" + mqImmobile + ") — " + stanzaNome + " | Immobiliare Giancani";

    sheet.appendRow([
      fileUrl, 
      prezzoImmobile, 
      mqImmobile, 
      stanzaNome, 
      mediaType, 
      testoDescrittivo, 
      "it-IT", 
      tickerText, 
      "https://www.immobiliaregiancani.it",
      ""
    ]);

    setImmobileAttivoInDiretta(nomeTab);

    var basiFolder = getOrCreateBasiMusicaliDriveFolder();

    return {
      success: true,
      tabName: nomeTab,
      fileName: fileObj.fileName,
      url: fileUrl,
      stanza: stanzaNome,
      tipo: mediaType,
      cartellaImmobileUrl: (folder ? folder.getUrl() : ''),
      cartellaImmobileId: (folder ? folder.getId() : ''),
      cartellaBasiMusicaliUrl: basiFolder.url,
      cartellaBasiMusicaliId: basiFolder.id
    };
  } catch(e) {
    inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "caricaSingoloFileSuDriveEProprieta", e.toString());
    return { success: false, fileName: (data && data.file ? data.file.fileName : ''), error: e.toString() };
  }
}

/**
 * 🎙️ Generatore MP3 da Testo Lungo
 */
function generaAudioMP3DaTestoLungo(testo) {
  if (!testo) return null;
  try {
    var encodedTxt = encodeURIComponent(testo.toString().substring(0, 200));
    var audioUrl = "https://translate.google.com/translate_tts?ie=UTF-8&q=" + encodedTxt + "&tl=it&client=tw-ob";
    return audioUrl;
  } catch(e) {
    return null;
  }
}

function convertiLetteraColonnaInNumero(colStr) {
  if (!colStr) return 1;
  if (typeof colStr === 'number') return colStr;
  colStr = colStr.toString().toUpperCase().trim();
  var num = 0;
  for (var i = 0; i < colStr.length; i++) {
    num = num * 26 + (colStr.charCodeAt(i) - 64);
  }
  return num > 0 ? num : 1;
}

function estraiIdSpreadsheet(urlOrId) {
  if (!urlOrId || typeof urlOrId !== 'string') return '';
  urlOrId = urlOrId.trim();
  if (urlOrId.indexOf('docs.google.com') !== -1) {
    var match = urlOrId.match(/\/d\/([^\/\?]+)/) || urlOrId.match(/key=([^\&]+)/);
    if (match && match[1]) return match[1];
  }
  return urlOrId;
}

function leggiRigheTestoAzureTTS(config) {
  try {
    var sheetId = config && config.sheetUrlOrId ? estraiIdSpreadsheet(config.sheetUrlOrId) : SHEET_ID;
    var ss = sheetId ? SpreadsheetApp.openById(sheetId) : getSpreadsheetSicuro();
    if (!ss) return { success: false, error: "Foglio non trovato" };

    var sheetName = config.sheetName ? config.sheetName.trim() : null;
    var sheet = sheetName ? ss.getSheetByName(sheetName) : ss.getSheets()[0];
    if (!sheet || sheet.getLastRow() < 1) return { success: false, error: "Foglio vuoto" };

    var colTestoNum = convertiLetteraColonnaInNumero(config.colonnaTesto || 'F');
    var colOutputNum = convertiLetteraColonnaInNumero(config.colonnaOutput || 'J');
    var startRow = (config.saltaIntestazione !== false && config.saltaIntestazione !== "false") ? 2 : 1;

    var lastRow = sheet.getLastRow();
    var maxCols = Math.max(colTestoNum, colOutputNum);
    var rangeData = sheet.getRange(startRow, 1, (lastRow - startRow + 1), maxCols).getValues();

    var items = [];
    for (var i = 0; i < rangeData.length; i++) {
      var rigaAttuale = startRow + i;
      var testoValore = (rangeData[i][colTestoNum - 1] || '').toString().trim();
      var linkEsistente = (rangeData[i][colOutputNum - 1] || '').toString().trim();
      if (testoValore.length > 0) {
        items.push({ rowNumber: rigaAttuale, text: testoValore, existingLink: linkEsistente });
      }
    }

    return { success: true, totalRows: items.length, items: items, sheetName: sheet.getName(), sheetId: sheetId };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

function elaboraSingoloTestoAzureTTS(config, item) {
  return { success: true, rowNumber: item ? item.rowNumber : 0 };
}

function generaAudioPiperTTSLocale(testo, voce) {
  return { success: true, url: generaAudioMP3DaTestoLungo(testo) };
}

function elaboraMessaggioInArrivo(msg) {
  return { success: true, testo: msg };
}



/**
 * 🚀 Pubblicazione automatica nuovo immobile su WordPress in prima linea
 */
function inviaNuovoImmobileAWordPress(datiScheda, nomeCartella, fileUrl, testoColonnaF) {
  try {
    var rawNome = (nomeCartella || "Nuovo Immobile").replace(/_/g, ' ');
    var tipo = (datiScheda && datiScheda.tipoImmobile) ? datiScheda.tipoImmobile : estraiTipoImmobileDaNomeCartella(rawNome);
    var zona = (datiScheda && datiScheda.zona) ? datiScheda.zona : "Favara";
    var titolo = tipo + " a " + zona;
    if (rawNome && rawNome.toLowerCase().indexOf(zona.toLowerCase()) === -1 && rawNome.toLowerCase() !== tipo.toLowerCase()) {
      titolo = rawNome;
    }
    titolo = titolo.charAt(0).toUpperCase() + titolo.slice(1);

    var prezzo = (datiScheda && datiScheda.prezzo) ? normalizzaPrezzo(datiScheda.prezzo) : "Trattativa Riservata";
    var mq = (datiScheda && datiScheda.metriQuadri) ? normalizzaMetriQuadri(datiScheda.metriQuadri) : "120 metri quadri";
    var camere = (datiScheda && datiScheda.camere) ? String(datiScheda.camere) : "";
    var bagni = (datiScheda && datiScheda.bagni) ? String(datiScheda.bagni) : "";

    // Testo rigorosamente da Colonna F con personal branding obbligatorio
    var desc = testoColonnaF || ("Splendida opportunita immobiliare a " + zona + " (" + mq + ") proposta in esclusiva da Immobiliare Giancani.");
    if (desc.indexOf("Immobiliare Giancani") === -1) {
      desc += "\n\n— Immobiliare Giancani";
    }

    var wpPayload = {
      token: "wpmcp_fc2b5449",
      titolo: titolo,
      citta: zona,
      prezzo: prezzo,
      superficie: mq,
      camere: camere,
      bagni: bagni,
      tipo: tipo,
      descrizione: desc,
      foto_url: fileUrl || ""
    };

    var wpUrl = "https://www.immobiliaregiancani.it/wp-json/giancani/v1/publish-immobile";
    var options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(wpPayload),
      muteHttpExceptions: true
    };

    var resp = UrlFetchApp.fetch(wpUrl, options);
    var resCode = resp.getResponseCode();
    var resText = resp.getContentText();
    Logger.log("Pubblicazione WP (" + resCode + "): " + resText);

    if (resCode === 200) {
      var notifica = "🔥 *NUOVA ENTRATA PUBBLICATA IN PRIMA LINEA!* 🔥\n\n" +
                     "🏠 *Immobile:* " + titolo + "\n" +
                     "📍 *Zona:* " + zona + "\n" +
                     "💰 *Prezzo:* " + prezzo + "\n" +
                     "📐 *Superficie:* " + mq + "\n\n" +
                     "🚀 L'immobile è ora visibile al primo posto sulla homepage di [immobiliaregiancani.it](https://www.immobiliaregiancani.it)!\n\n" +
                     "— *Immobiliare Giancani*";
      if (typeof inviaTelegramBoss === 'function') {
        inviaTelegramBoss(notifica);
      } else if (typeof inviaNotificaTelegram === 'function') {
        inviaNotificaTelegram(notifica);
      }
    }
    return { success: (resCode === 200), response: resText };
  } catch(eWp) {
    if (typeof inviaAllertaErroreTelegram === 'function') {
      inviaAllertaErroreTelegram("08_AutoVisionEGalleria.js", "inviaNuovoImmobileAWordPress", eWp.toString());
    }
    return { success: false, error: eWp.toString() };
  }
}


// ═══════════════════════════════════════════════════════════════════════
// 🎵 SEZIONE BASI MUSICALI PROFESSIONALI & GENERATORE REEL 9:16
// ═══════════════════════════════════════════════════════════════════════

/**
 * 🎵 Gestione Cartella Basi Musicali Professionali su Google Drive
 * Crea o recupera la cartella dedicata 'Basi_Musicali_Professionali'
 * dove caricare tracce audio di sottofondo MP3 per Reel e Dirette.
 */
function getOrCreateBasiMusicaliDriveFolder() {
  try {
    var folderName = "Basi_Musicali_Professionali";
    var master = null;
    
    if (typeof DRIVE_MASTER_FOLDER_ID !== 'undefined' && DRIVE_MASTER_FOLDER_ID) {
      try { master = DriveApp.getFolderById(DRIVE_MASTER_FOLDER_ID); } catch(eM) {}
    }
    if (!master && typeof CONFIG !== 'undefined' && CONFIG.DRIVE_ROOT_FOLDER_ID) {
      try {
        var rootFolders = DriveApp.getFoldersByName(CONFIG.DRIVE_ROOT_FOLDER_ID);
        if (rootFolders.hasNext()) master = rootFolders.next();
      } catch(eR) {}
    }
    
    var folder = null;
    if (master) {
      var sub = master.getFoldersByName(folderName);
      if (sub.hasNext()) {
        folder = sub.next();
      } else {
        folder = master.createFolder(folderName);
      }
    } else {
      var general = DriveApp.getFoldersByName(folderName);
      if (general.hasNext()) {
        folder = general.next();
      } else {
        folder = DriveApp.createFolder(folderName);
      }
    }
    
    try {
      folder.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    } catch(eSh) {}

    var brani = [];
    try {
      var files = folder.getFiles();
      while (files.hasNext()) {
        var f = files.next();
        var mime = f.getMimeType();
        var name = f.getName();
        if (mime.indexOf('audio') !== -1 || name.match(/\.(mp3|wav|m4a|aac|ogg)$/i)) {
          brani.push({
            id: f.getId(),
            name: name,
            size: (f.getSize() / (1024 * 1024)).toFixed(2) + " MB",
            url: f.getUrl()
          });
        }
      }
    } catch(eFiles) {
      Logger.log("Errore lettura brani musicali: " + eFiles);
    }

    return {
      success: true,
      id: folder.getId(),
      name: folderName,
      url: folder.getUrl(),
      brani: brani
    };
  } catch(e) {
    Logger.log("Errore getOrCreateBasiMusicaliDriveFolder: " + e);
    return {
      success: false,
      error: e.toString(),
      url: "https://drive.google.com",
      brani: []
    };
  }
}

/**
 * 🎵 Restituisce l'elenco delle basi musicali e l'URL della cartella su Google Drive
 */
function getListaBasiMusicaliDrive() {
  return getOrCreateBasiMusicaliDriveFolder();
}

/**
 * 🎬 Avvia la generazione del Video Reel 9:16 direttamente da Studio Galleria
 * Legge rigorosamente la Colonna F, mappa video e traccia musicale,
 * ed esegue il dispatch verso GitHub Actions con consegna via email.
 */
function avviaGenerazioneReelDaGalleria(payload) {
  try {
    var tabName = (payload && payload.tabName) ? payload.tabName : '';
    var riga = (payload && payload.riga) ? parseInt(payload.riga, 10) : 2;
    var ss = getSpreadsheetSicuro();
    if (!ss) return { success: false, error: 'Spreadsheet non accessibile' };

    var sheet = tabName ? ss.getSheetByName(tabName) : ss.getActiveSheet();
    if (!sheet) return { success: false, error: 'Scheda immobile non trovata: ' + tabName };

    var testoColonnaF = (payload && payload.testoF) ? payload.testoF : '';
    var videoDriveId = (payload && payload.videoDriveId) ? payload.videoDriveId : '';
    var musicaDriveId = (payload && payload.musicaDriveId) ? payload.musicaDriveId : '';

    var numRighe = sheet.getLastRow();
    if (!testoColonnaF && riga <= numRighe) {
      // Colonna F è la colonna 6
      testoColonnaF = String(sheet.getRange(riga, 6).getValue() || '').trim();
    }

    // Se non troviamo video esplicito, cerca nella prima riga con tipo 'video' o URL video
    if (!videoDriveId) {
      for (var r = 2; r <= Math.min(numRighe, 30); r++) {
        var tipoMedia = String(sheet.getRange(r, 5).getValue() || '').toLowerCase();
        var urlMedia = String(sheet.getRange(r, 1).getValue() || '');
        if (tipoMedia === 'video' || urlMedia.indexOf('.mp4') !== -1 || urlMedia.indexOf('video') !== -1) {
          videoDriveId = urlMedia;
          break;
        }
      }
    }

    var ghUser = (typeof CONFIG !== 'undefined' && CONFIG.GITHUB_USER) ? CONFIG.GITHUB_USER : 'Tonyhood2345';
    var ghRepo = 'live-stream-serverless';
    var ghToken = (typeof CONFIG !== 'undefined' && CONFIG.GITHUB_TOKEN) ? CONFIG.GITHUB_TOKEN : '';
    var emailDest = (payload && payload.email) ? payload.email : ((typeof CONFIG !== 'undefined' && CONFIG.PRIMARY_EMAIL) ? CONFIG.PRIMARY_EMAIL : 'giancaniimmobiliare@gmail.com');

    if (!ghToken) {
      return { success: false, error: 'Token GitHub non configurato in CONFIG.GITHUB_TOKEN' };
    }

    var dispatchUrl = 'https://api.github.com/repos/' + ghUser + '/' + ghRepo + '/actions/workflows/genera_reel_immobile.yml/dispatches';
    var reqBody = {
      ref: 'main',
      inputs: {
        riga_foglio: String(riga),
        email_destinatario: emailDest,
        video_drive_id: videoDriveId,
        musica_drive_id: musicaDriveId,
        forza_testo_colonna_f: testoColonnaF
      }
    };

    var res = UrlFetchApp.fetch(dispatchUrl, {
      method: 'post',
      contentType: 'application/json',
      headers: {
        'Authorization': 'token ' + ghToken,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Giancani-StudioGalleria-Reels'
      },
      payload: JSON.stringify(reqBody),
      muteHttpExceptions: true
    });

    var code = res.getResponseCode();
    if (code === 204 || code === 200 || code === 201) {
      return {
        success: true,
        msg: 'Workflow Reel avviato con successo su GitHub Actions! Riceverai il file MP4 montato e il copy via email su ' + emailDest + ' — Immobiliare Giancani'
      };
    } else {
      return {
        success: false,
        error: 'Errore GitHub (' + code + '): ' + res.getContentText()
      };
    }
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}
