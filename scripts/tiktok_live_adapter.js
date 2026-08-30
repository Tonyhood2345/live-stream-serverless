/**
 * ═══════════════════════════════════════════════════════════════════════
 * 📁 TIKTOK LIVE ADAPTER (STANDALONE AUTOMATION MODULE)
 * Modulo dedicato e indipendente per la gestione di TikTok LIVE via browser
 * ═══════════════════════════════════════════════════════════════════════
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class TikTokLiveAdapter {
  constructor(options = {}) {
    this.options = Object.assign({
      headless: true,
      viewport: { width: 1920, height: 1080 },
      cookiesPath: fs.existsSync(path.join(__dirname, 'tiktok_cookies.json')) ? path.join(__dirname, 'tiktok_cookies.json') : '/tmp/tiktok_cookies.json',
      outputPath: '/tmp/tiktok_rtmp.txt',
      timeout: 35000,
      defaultTitle: '🔴 TOUR VIRTUALE 360° IN DIRETTA — Antonio Giancani'
    }, options);

    this.browser = null;
    this.context = null;
    this.page = null;
    this.streamInfo = { serverUrl: '', streamKey: '', fullRtmp: '' };
  }

  async initialize() {
    console.log("🎵 [TikTokAdapter] Inizializzazione browser headless Chromium...");
    this.browser = await chromium.launch({
      headless: this.options.headless,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled'
      ]
    });

    this.context = await this.browser.newContext({
      viewport: this.options.viewport,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    });

    // Carica cookie se presenti
    if (fs.existsSync(this.options.cookiesPath)) {
      try {
        const raw = fs.readFileSync(this.options.cookiesPath, 'utf8');
        const cookies = JSON.parse(raw);
        await this.context.addCookies(cookies);
        console.log("🎵 [TikTokAdapter] Cookie di sessione TikTok caricati con successo.");
      } catch (e) {
        console.warn("⚠️ [TikTokAdapter] Errore caricamento cookie:", e.message);
      }
    }

    this.page = await this.context.newPage();
  }

  async checkAuthentication() {
    console.log("🎵 [TikTokAdapter] Verifica stato di login su TikTok...");
    try {
      await this.page.goto('https://www.tiktok.com/tiktokstudio', {
        waitUntil: 'domcontentloaded',
        timeout: this.options.timeout
      });

      await this.page.waitForTimeout(3000);

      // Verifica presenza avatar utente o pulsante profilo
      const loggedSelector = 'header [data-e2e="profile-icon"], img[class*="avatar"], a[href*="/@"]';
      const isLogged = await this.page.$(loggedSelector);

      if (isLogged) {
        console.log("✅ [TikTokAdapter] Utente autenticato correttamente.");
        return true;
      }

      console.log("ℹ️ [TikTokAdapter] Nessuna sessione attiva rilevata. In attesa di login/credenziali.");
      return false;
    } catch (e) {
      console.warn("⚠️ [TikTokAdapter] Avviso verifica autenticazione:", e.message);
      return false;
    }
  }

  async prepareLiveSession(title) {
    const liveTitle = title || this.options.defaultTitle;
    console.log("🎵 [TikTokAdapter] Accesso al pannello LIVE Studio con titolo:", liveTitle);

    try {
      // Navigazione alla sezione LIVE
      await this.page.goto('https://www.tiktok.com/tiktokstudio/live', {
        waitUntil: 'networkidle',
        timeout: this.options.timeout
      });

      await this.page.waitForTimeout(2000);

      // Chiudi eventuali modali di avviso o linee guida community
      const dismissSelectors = [
        'button:has-text("Accetta")',
        'button:has-text("Ho capito")',
        'button:has-text("Got it")',
        'button:has-text("Continua")',
        'button[aria-label="Close"]'
      ];

      for (const sel of dismissSelectors) {
        const btn = await this.page.$(sel);
        if (btn) {
          console.log(`🎵 [TikTokAdapter] Chiusura popup informativo (${sel})...`);
          await btn.click().catch(() => {});
          await this.page.waitForTimeout(800);
        }
      }

      // Imposta il Titolo della LIVE
      const titleSelectors = [
        'input[placeholder*="titolo" i]',
        'input[placeholder*="title" i]',
        'textarea[placeholder*="titolo" i]',
        'input[data-e2e="live-title-input"]'
      ];

      for (const sel of titleSelectors) {
        const titleEl = await this.page.$(sel);
        if (titleEl) {
          await titleEl.fill('');
          await titleEl.fill(liveTitle);
          console.log("✅ [TikTokAdapter] Titolo impostato nel form.");
          break;
        }
      }

      // Seleziona opzione "Software di streaming / PC"
      const rtmpOption = await this.page.$('text="Software di streaming", text="PC", [value*="pc_live"]');
      if (rtmpOption) {
        await rtmpOption.click().catch(() => {});
      }

      // Recupera Server URL e Chiave di Streaming
      await this.page.waitForTimeout(2000);
      const inputValues = await this.page.$$eval('input[readonly], input[type="text"]', inputs => inputs.map(i => i.value));

      let server = inputValues.find(v => v && v.startsWith('rtmp://')) || 'rtmp://live-push.tiktok-cdns.com/live/';
      let key = inputValues.find(v => v && v.length > 20 && !v.startsWith('rtmp://')) || '';

      if (server && key) {
        const fullRtmp = server.endsWith('/') ? (server + key) : (server + '/' + key);
        this.streamInfo = { serverUrl: server, streamKey: key, fullRtmp: fullRtmp };
        fs.writeFileSync(this.options.outputPath, fullRtmp);
        console.log("✅ [TikTokAdapter] Endpoint RTMP TikTok estratto e salvato in:", this.options.outputPath);
        return this.streamInfo;
      }
    } catch (e) {
      console.warn("⚠️ [TikTokAdapter] Errore preparazione LIVE:", e.message);
    }

    return null;
  }

  async confirmGoLive() {
    console.log("🎵 [TikTokAdapter] Conferma definitiva 'Avvia LIVE'...");
    try {
      if (!this.page) return false;
      const goLiveBtn = await this.page.$('button:has-text("Avvia LIVE"), button:has-text("Go LIVE"), button[class*="go-live"]');
      if (goLiveBtn) {
        await goLiveBtn.click();
        console.log("🚀 [TikTokAdapter] LIVE avviata con successo su TikTok!");
        return true;
      }
    } catch (e) {
      console.warn("⚠️ [TikTokAdapter] Errore click Avvia LIVE:", e.message);
    }
    return false;
  }

  async endLiveSession() {
    console.log("⏹️ [TikTokAdapter] Chiusura della sessione LIVE...");
    try {
      if (!this.page) return false;
      const endBtn = await this.page.$('button:has-text("Termina"), button:has-text("End LIVE"), button:has-text("Concludi")');
      if (endBtn) {
        await endBtn.click();
        await this.page.waitForTimeout(1000);
        const confirmBtn = await this.page.$('button:has-text("Conferma"), button:has-text("Termina adesso")');
        if (confirmBtn) await confirmBtn.click();
        console.log("✅ [TikTokAdapter] LIVE terminata correttamente.");
        return true;
      }
    } catch (e) {
      console.warn("⚠️ [TikTokAdapter] Errore chiusura LIVE:", e.message);
    }
    return false;
  }

  async close() {
    if (this.browser) {
      await this.browser.close().catch(() => {});
      this.browser = null;
    }
  }
}

module.exports = TikTokLiveAdapter;

// Esecuzione autonoma CLI se invocato direttamente
if (require.main === module) {
  (async () => {
    const adapter = new TikTokLiveAdapter();
    try {
      await adapter.initialize();
      const isAuth = await adapter.checkAuthentication();
      if (isAuth) {
        await adapter.prepareLiveSession();
      }
    } catch (err) {
      console.error("Errore esecuzione TikTokLiveAdapter:", err);
    } finally {
      // Mantiene aperto se necessario o chiude
    }
  })();
}
