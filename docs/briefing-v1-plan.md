# Briefing Mattutino v1 Plan

## Scope

La v1 dell'**Assistente Personale Interno** consegna un **Briefing Mattutino** quotidiano via Telegram, eseguito dentro un container Docker persistente sul NAS Ugreen.

Il briefing serve a preparare la giornata ordinaria, assumendo Cherasco come **Contesto Locale** e usando il calendario per capire se ci sono impegni o viaggi rilevanti.

## In Scope

- Meteo di Cherasco per la giornata corrente.
- Suggerimento pratico su cosa indossare per un uomo di 44 anni.
- Lettura read-only di Google Calendar.
- Riassunto compatto di tutti gli eventi di oggi.
- Riconoscimento di viaggi a partire da location o linguaggio esplicito negli eventi.
- Meteo aggiuntivo per le destinazioni dei viaggi.
- Suggerimento abbigliamento basato su Cherasco, destinazioni, meteo e durata fuori casa.
- Frase motivazionale finale breve.
- Invio Telegram outbound.
- Fallback su stdout quando Telegram non e configurato.
- Esecuzione Docker persistente con scheduler interno.
- Invio anticipato quando il calendario mostra un viaggio presto.
- Degradazione controllata quando una fonte dati non e disponibile.

## Out of Scope

- Task Inbox e gestione task.
- Menu pranzo/cena.
- Input Telegram in ingresso.
- Knowledge Base Personale.
- Contesto meeting basato su note o documenti personali.
- Vacanze e soggiorni multi-giorno.
- Hermes o altro agente autonomo per l'orchestrazione.
- Calcolo dell'ora di partenza consigliata o routing/traffico.

## Data Sources

- OpenWeatherMap per meteo locale e meteo destinazioni.
- Google Calendar in sola lettura per eventi giornalieri.
- LLM configurabile via provider esistente per suggerimento abbigliamento e frase motivazionale.

OpenWeatherMap resta la fonte meteo della v1.

## Google Calendar Authorization

- Aggiungere un comando manuale `make auth-calendar` da eseguire sul Mac.
- Il comando apre il flusso OAuth utente e salva il refresh token in `data/token.json`.
- Tenere il client OAuth Google in `data/google-credentials.json`.
- Tenere `data/google-credentials.json` e `data/token.json` fuori da Git.
- Il file `data/token.json` va poi copiato o sincronizzato nel volume dati usato dal container sul NAS.
- Il container non deve richiedere interazione browser durante l'esecuzione normale.

## Calendar Rules

- Leggere il calendario principale Google.
- Consentire una allowlist configurabile di calendari aggiuntivi.
- Escludere calendari non selezionati, inclusi compleanni/festivita se non aggiunti esplicitamente.
- Considerare solo eventi della giornata corrente.
- Mostrare tutti gli eventi in forma compatta.
- Usare titolo, orario, location e descrizione essenziale.

## Travel Rules

Un evento e un **Viaggio** quando:

- ha una location fuori dal **Contesto Locale**;
- oppure contiene parole o destinazioni esplicite nel titolo o nella descrizione, per esempio treno, volo, aeroporto, hotel, trasferta, viaggio, Milano, Torino.

La **Destinazione** va ricavata prima dalla location dell'evento, poi dal titolo o dalla descrizione.

Per la v1, normalizzare la destinazione a una citta o localita cercabile da OpenWeather:

- `Milano` resta `Milano`;
- `Via Roma 10, Torino` diventa `Torino`;
- `Aeroporto Malpensa` diventa `Malpensa` o `Milano/Malpensa`;
- se non emerge un luogo plausibile, non richiedere meteo destinazione.

La v1 assume rientro a Cherasco in giornata, salvo evidenza contraria. Le vacanze restano fuori scope.

## Briefing Timing

- Default: 07:00 Europe/Rome, configurabile.
- Controllo anticipato: configurabile, default 05:15 Europe/Rome.
- Se il calendario mostra un viaggio o evento fuori Cherasco prima delle 08:30, inviare il briefing al controllo anticipato.
- Altrimenti inviare all'orario default.
- Inviare al massimo un briefing al giorno.
- Salvare lo stato di deduplica in `data/briefing-state.json` tramite `DATA_PATH`, cosi resta valido anche dopo riavvii del container.
- Scheduler v1: un job di controllo anticipato legge il calendario ogni giorno e invia solo se necessario; un job default invia alle 07:00 se il briefing non e gia stato inviato.
- `RUN_NOW=true` deve inviare sempre e ignorare la deduplica, per permettere test e debug manuali.

## Message Shape

Struttura proposta del messaggio Telegram:

1. Saluto e data.
2. Meteo Cherasco.
3. Calendario di oggi.
4. Viaggi e meteo destinazioni, se presenti.
5. Suggerimento abbigliamento per l'intera giornata.
6. Frase motivazionale finale breve.

Usare Markdown Telegram ed emoji di sezione come nel messaggio attuale, ma mantenere il template controllato dal codice. Gli output LLM devono essere testo semplice senza Markdown libero.

Il briefing deve essere scritto in italiano. I titoli degli eventi calendario vanno preservati come sono.

## Failure Behavior

Il briefing deve essere degradabile:

- se Google Calendar non risponde, inviare meteo, abbigliamento locale e frase, indicando che il calendario non e disponibile;
- se il meteo non risponde, inviare calendario e frase, indicando che meteo e abbigliamento non sono disponibili;
- se il LLM non risponde, inviare i dati strutturati senza suggerimento abbigliamento o frase motivazionale.

## Test Strategy

Testare con unit test le regole locali:

- riconoscimento **Viaggio**;
- estrazione **Destinazione**;
- decisione di invio anticipato;
- deduplica giornaliera;
- formattazione calendario vuoto e non vuoto.

Non testare direttamente API esterne nei test automatici della v1.

## Implementation Steps

1. Rimuovere dalla v1 le sezioni menu e task dal messaggio principale.
2. Aggiungere un tool Google Calendar read-only con OAuth utente e token persistito in `DATA_PATH`.
3. Aggiungere `make auth-calendar` per generare il token dal Mac.
4. Aggiungere un modello interno per eventi giornalieri e viaggi rilevati.
5. Estendere il tool meteo per accettare destinazioni dinamiche.
6. Aggiungere generazione LLM del suggerimento abbigliamento usando solo dati strutturati forniti dal sistema.
7. Aggiornare lo scheduler per supportare controllo anticipato e deduplica giornaliera.
8. Aggiornare configurazione Docker/NAS e documentare il setup OAuth iniziale.
9. Aggiungere test mirati sulle regole locali.
10. Verificare con `make run-now` e con container Docker locale prima del deploy NAS.

## Key Decisions

- Orchestrazione deterministica con LLM mirato, documentata in `docs/adr/0001-deterministic-briefing-orchestration.md`.
- Google Calendar via user OAuth read-only con token persistente, documentata in `docs/adr/0002-google-calendar-user-oauth.md`.
