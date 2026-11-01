# 📜 REGOLE MANDATORIE DI PROGETTO — IMMOBILIARE GIANCANI

Tutte le sessioni, agenti AI e script operativi all'interno di questo workspace devono rispettare rigorosamente le seguenti direttive.

---

## 🎯 1. Coerenza Visiva e Tematica Rigorosa (Immagini Contestuali e Sempre Diverse)
> **REGOLA MANDATORIA RICHIESTA DALL'UTENTE**:
> Le immagini utilizzate per la generazione dei video e delle storie (Reels, Storie verticali 9:16, Flyer) **devono essere rigorosamente contestuali e perfettamente coerenti con il testo pronunciato o con il tema specifico trattato in ciascuna scena**.
- **ASSOLUTO OBBLIGO DI DIVERSITÀ AD OGNI STORIA**:
  - È vietato pubblicare la stessa foto o grafica consecutivamente. Ogni storia deve selezionare un'immagine sempre diversa dal catalogo immobiliare e ruotare stile grafico.
- **DIVIETO ASSOLUTO**:
  - Immagini generiche, "standard", casuali o astratte.
  - Ritratti scuri in penombra, volti non attinenti, o ambienti non pertinenti (ad es. cucine/chef, persone sconosciute fuori contesto).
- **STANDARD VISIVO OBBLIGATORIO**:
  - Ogni scena deve rappresentare esattamente l'oggetto del testo recitato:
    - *Rogito / Contratti / Caparra*: Contratti formali con penna stilografica di pregio, riga di firma, documenti notarili autentici.
    - *Conformità Urbanistica / Catasto*: Planimetrie architettoniche su tavoli da disegno tecnici con righe e compassi.
    - *Consegna Immobile / Sicurezza Acquisto*: Chiavi di casa con portachiavi, plastico di casa su tavolo in legno, stretta di mano d'accordo.
    - *Agevolazioni Fiscali / Mutuo / Spese*: Documenti di calcolo, consulenza finanziaria su tavolo, liberatorie.
    - *Immobili*: Living contemporanei luminosi ad alta definizione, ville di pregio rifinite e architetture curate.

---

## 📊 2. Estrazione Dati Rigorosamente da Colonna F
- I testi recitati e le narrazioni video/storie devono essere estratti tassativamente dalla **Colonna F** del database di riferimento (`database_pillole_immobiliari_legali.csv`, `database_storie_*.csv`, o fogli Google Sheet).
- Nessuna alterazione arbitraria del copione autorizzato.

---

## ⭐ 3. Personal Branding Obbligatorio in Chiusura
- Ogni output di testo generato dallo script, copy descrittivo, sottotitolo o messaggio social deve sempre terminare mettendo in massimo risalto:
  > **`— Immobiliare Giancani`**

---

## 📐 4. Dicitura Metri Quadri per Esteso
- Nelle descrizioni, nelle didascalie e nelle trascrizioni vocali, le superfici devono essere riportate per esteso come **"metri quadri"** (mai abbreviazioni come `mq`, `mq.`, `m²` o `MQ`).

---

## 🎭 5. Orchestrazione Alternata 15 Minuti (Bot Immagini & Bot Video)
- Il sistema esegue un ciclo ogni 15 minuti, 24 ore su 24, alternando:
  1. **Ciclo Immagini**: Storie verticali 9:16 generate dal Motore Grafico Unificato con rotazione continua dei 10 stili approvati (*Split-Screen Ribbon*, *Luxury Glass*, *Editorial Magazine*, *Gabetti Diagonal*, *Capellupo Sidebar*, *Marketing Banner*, *Minimal Clean*, *Coldwell Banker Curved Wave*, *Twilight Penthouse*, *Mediterranean Coastal*). Fondo dei form/card semi-trasparente per dare priorità visiva all'immagine.
  2. **Ciclo Video**: Spezzone video reale 30s da archivio YouTube o animazione dinamica Ken Burns, con card descrittiva semi-trasparente in basso e logo protetto in alto.

---

## 🌐 6. Canali di Distribuzione Social: Tassativamente nelle Storie
I contenuti generati vengono pubblicati automaticamente sui canali ufficiali dell'agenzia:
- **Facebook Stories**: Pagina Ufficiale Immobiliare Giancani (ID `234931856561526`) e profilo personale Antonio Giancani.
- **Instagram Stories**: Profilo `@giancani_immobiliare`.
- **YouTube Shorts / Storie**: Canale `@immobiliaregiancani761`. Poiché YouTube ha ritirato la funzione Storie provvisorie nel 2023, i contenuti verticali 9:16 vengono pubblicati pubblicamente nella sezione **Shorts** con tag `#Shorts` e `#Stories`.
- **TikTok Stories**: Profilo `@immobiliare_giancani`. **Obbligo assoluto di pubblicazione nelle Storie** (TikTok Stories) tramite Playwright, selezionando il selettore dedicato e non il feed post tradizionale.

---

## 🔕 7. Notifiche Telegram: Esclusivamente Report Cumulativo ogni 4 Ore
- **Divieto di spam**: Non inviare notifiche a ogni singolo ciclo di 15 minuti.
- Viene inviato **1 solo messaggio ogni 4 ore** (ogni 16 cicli) alla chat Telegram ID `1723292483`.
- Il messaggio deve contenere **esclusivamente i link diretti delle pubblicazioni effettuate** (Facebook, Instagram, YouTube Shorts, TikTok Stories) per un monitoraggio rapido e pulito.

---
*Documento di configurazione attiva per l'ecosistema Immobiliare Giancani.*
