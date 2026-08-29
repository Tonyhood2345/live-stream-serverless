const { chromium } = require('playwright');
const fs = require('fs');

async function getInstagramLiveKey() {
  console.log("📸 [Instagram Bot] Avvio browser headless per estrazione automatica chiave Live...");
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  // Load cookies if present
  const cookiesPath = '/tmp/instagram_cookies.json';
  if (fs.existsSync(cookiesPath)) {
    try {
      const cookies = JSON.parse(fs.readFileSync(cookiesPath, 'utf8'));
      await context.addCookies(cookies);
      console.log("📸 [Instagram Bot] Cookie di sessione Instagram caricati con successo.");
    } catch(e) {
      console.warn("Avviso caricamento cookie:", e);
    }
  }

  const page = await context.newPage();

  try {
    console.log("📸 [Instagram Bot] Navigazione verso instagram.com...");
    await page.goto('https://www.instagram.com/', { waitUntil: 'networkidle', timeout: 30000 });

    // Controlla se siamo loggati
    const isLogged = await page.$('svg[aria-label="Crea"], svg[aria-label="Nuovo post"], svg[aria-label="Direct"]');
    if (!isLogged) {
      console.log("⚠️ [Instagram Bot] Sessione non attiva. Richiesta chiave manuale o cookie aggiornati.");
      await browser.close();
      return null;
    }

    console.log("📸 [Instagram Bot] Sessione attiva! Apertura modale Diretta...");
    // Clicca Crea
    await page.click('svg[aria-label="Crea"]');
    await page.waitForTimeout(1000);

    // Clicca Video in diretta se presente
    const liveBtn = await page.$('text="Video in diretta"');
    if (liveBtn) {
      await liveBtn.click();
      await page.waitForTimeout(2000);

      // Inserisci titolo
      const titleInput = await page.$('input[placeholder="Aggiungi un titolo"], input[type="text"]');
      if (titleInput) {
        await titleInput.fill('Tour Virtuale 360° — Immobiliare Giancani');
      }

      // Clicca Avanti
      const nextBtn = await page.$('button:has-text("Avanti")');
      if (nextBtn) {
        await nextBtn.click();
        await page.waitForTimeout(3000);

        // Estrai URL e Stream Key
        const textInputs = await page.$$eval('input[type="text"], input[readonly]', inputs => inputs.map(i => i.value));
        console.log("📸 [Instagram Bot] Valori estratti dalla schermata:", textInputs);

        let streamUrl = textInputs.find(v => v.startsWith('rtmps://')) || '';
        let streamKey = textInputs.find(v => v.length > 20 && !v.startsWith('rtmps://')) || '';

        if (streamUrl && streamKey) {
          const fullRtmp = streamUrl.endsWith('/') ? (streamUrl + streamKey) : (streamUrl + '/' + streamKey);
          fs.writeFileSync('/tmp/instagram_rtmp.txt', fullRtmp);
          console.log("✅ [Instagram Bot] Chiave RTMP Instagram salvata con successo!");

          // Salva istanza page per cliccare "Trasmetti in diretta" dopo che FFmpeg è partito
          setTimeout(async () => {
            try {
              console.log("📸 [Instagram Bot] Clicco su 'Trasmetti in diretta'...");
              const goLiveBtn = await page.$('button:has-text("Trasmetti in diretta"), button:has-text("Go Live")');
              if (goLiveBtn) await goLiveBtn.click();
            } catch(eLive) {}
          }, 15000);

          return fullRtmp;
        }
      }
    }
  } catch(e) {
    console.warn("⚠️ [Instagram Bot] Dettagli esecuzione:", e.message);
  }

  await browser.close();
  return null;
}

getInstagramLiveKey().catch(console.error);
