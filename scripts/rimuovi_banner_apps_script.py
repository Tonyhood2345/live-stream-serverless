#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rimuove categoricamente il banner disclaimer di Google Apps Script
("Questa applicazione è stata creata da un altro utente...")
collegandosi a Google Chrome tramite CDP (Chrome DevTools Protocol) sulla porta 9222.
— Immobiliare Giancani
"""

import time
import sys

def rimuovi_banner_via_cdp():
    print("═" * 70)
    print("🧹 RIMOZIONE BANNER GOOGLE APPS SCRIPT VIA CDP — IMMOBILIARE GIANCANI")
    print("═" * 70)
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("⚠️ Playwright non installato.")
        return False

    max_attempts = 15
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"[{attempt}/{max_attempts}] Connessione a Chrome (http://127.0.0.1:9222)...")
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=5000)
                contexts = browser.contexts
                if not contexts or not contexts[0].pages:
                    print("   Nessuna pagina aperta trovata, attendo...")
                    time.sleep(2)
                    continue

                page = contexts[0].pages[0]
                print(f"   Pagina rilevata: {page.title()[:60]} ({page.url[:60]}...)")
                
                # Applica la rimozione e l'iniezione dello stile permanente
                res = page.evaluate("""() => {
                    let actions = [];
                    // 1. Nascondi e rimuovi #warning
                    const w = document.getElementById('warning');
                    if (w) {
                        w.style.setProperty('display', 'none', 'important');
                        w.remove();
                        actions.push('warning_removed');
                    }
                    
                    // 2. Nascondi prima riga della tabella contenitore
                    const tbl = document.getElementById('warning-bar-table');
                    if (tbl && tbl.rows && tbl.rows.length > 1) {
                        tbl.rows[0].style.display = 'none';
                        actions.push('first_row_hidden');
                    }
                    
                    // 3. Inietta foglio di stile globale che garantisce la scomparsa permanente
                    if (!document.getElementById('kill-apps-script-banner')) {
                        const style = document.createElement('style');
                        style.id = 'kill-apps-script-banner';
                        style.innerHTML = `
                            #warning,
                            .warning-bar,
                            .warning-banner-bar,
                            #warning-bar-table tr:first-child,
                            .docs-butter-bar-container {
                                display: none !important;
                                height: 0px !important;
                                min-height: 0px !important;
                                max-height: 0px !important;
                                padding: 0 !important;
                                margin: 0 !important;
                                border: 0 !important;
                                overflow: hidden !important;
                                visibility: hidden !important;
                                opacity: 0 !important;
                                pointer-events: none !important;
                            }
                            #warning-bar-table,
                            #warning-bar-table tbody,
                            #warning-bar-table tr:last-child,
                            #warning-bar-table td {
                                height: 100vh !important;
                                width: 100vw !important;
                                margin: 0 !important;
                                padding: 0 !important;
                                border: none !important;
                            }
                            #sandboxFrame {
                                height: 100% !important;
                                width: 100% !important;
                                margin: 0 !important;
                                padding: 0 !important;
                                border: none !important;
                            }
                            html, body {
                                overflow: hidden !important;
                                margin: 0 !important;
                                padding: 0 !important;
                                width: 100% !important;
                                height: 100% !important;
                            }
                        `;
                        document.head.appendChild(style);
                        actions.push('css_injected');
                    }
                    return actions;
                }""")
                print(f"✅ Banner rimosso con successo! Azioni eseguite: {res}")
                print("— Immobiliare Giancani")
                return True
        except Exception as e:
            print(f"   In attesa di Chrome ({e})...")
            time.sleep(2)

    print("⚠️ Timeout nel collegamento CDP a Chrome.")
    return False

if __name__ == "__main__":
    success = rimuovi_banner_via_cdp()
    sys.exit(0 if success else 1)
