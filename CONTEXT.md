# Personal Internal Assistant

This context defines the language for a private assistant that gathers personal information, organizes it, and helps with daily planning.

## Language

**Assistente Personale Interno**:
A private assistant that helps its owner plan, remember, and organize personal information.
_Avoid_: personal agent, bot generico, sistema AI generico

**Briefing Mattutino**:
A daily message that gathers practical signals and suggestions useful for the current day.
_Avoid_: report, digest, notifica generica

**Orario Briefing**:
The time when the owner expects to receive the **Briefing Mattutino**.
_Avoid_: cron, schedule tecnico, trigger

**Meteo Giornaliero**:
The weather conditions that matter for planning the owner's day.
_Avoid_: forecast generico, previsioni grezze

**Suggerimento Abbigliamento**:
A practical clothing recommendation for the owner based on weather, travel, and time spent away from home.
_Avoid_: outfit, consiglio moda

**Routine**:
A recurring assistant behavior that happens on a schedule or in response to a recurring situation.
_Avoid_: job, automazione, workflow

**Task**:
A personal action item that the owner can complete.
_Avoid_: todo, attività, promemoria

**Task Inbox**:
The entry point where the owner captures candidate **Task** items before they are clarified, prioritized, or completed.
_Avoid_: inbox generica, lista task, backlog personale

**Canale di Conversazione**:
The place where the owner sends messages to and receives messages from the **Assistente Personale Interno**.
_Avoid_: notifier, integrazione, interfaccia

**Calendario**:
The owner's time-based commitments and events.
_Avoid_: agenda

**Contesto Locale**:
The owner's normal day-to-day location context, centered on Cherasco.
_Avoid_: base, citta principale, casa

**Viaggio**:
A planned movement to a destination outside the owner's normal local context.
_Avoid_: trasferta, spostamento, gita

**Vacanza**:
An exceptional multi-day period away from the **Contesto Locale** that may not be fully represented in the **Calendario**.
_Avoid_: viaggio lungo, ferie, assenza

**Destinazione**:
The place where the owner is expected to be during a **Viaggio**.
_Avoid_: location, luogo, posto

**Contesto Meeting**:
The relevant background needed to enter a meeting prepared.
_Avoid_: prep, riassunto meeting, reminder meeting

**Knowledge Base Personale**:
The owner's organized personal knowledge collected from notes, links, documents, and messages.
_Avoid_: wiki LLM, archivio, memoria generica

## Relationships

- An **Assistente Personale Interno** owns many **Routine**.
- A **Canale di Conversazione** connects the owner and the **Assistente Personale Interno**.
- In the first version, the **Canale di Conversazione** is used only for outbound messages.
- A **Briefing Mattutino** is one **Routine**.
- The default **Orario Briefing** is 07:00 Europe/Rome and can be configured.
- The **Orario Briefing** may be anticipated when the **Calendario** shows an early **Viaggio**.
- A **Briefing Mattutino** includes the **Meteo Giornaliero** for the owner's normal local context.
- A **Briefing Mattutino** includes a **Suggerimento Abbigliamento** for the owner.
- A **Briefing Mattutino** summarizes the **Calendario** for the day.
- A **Briefing Mattutino** may still be valid when one information source is unavailable, as long as the missing part is made explicit.
- In the first version, the **Assistente Personale Interno** only reads the **Calendario**.
- In the first version, the **Calendario** is limited to the owner's primary calendar plus explicitly selected calendars.
- The **Calendario** summary in the **Briefing Mattutino** includes all events for the current day in compact form.
- A **Contesto Locale** may be used to distinguish ordinary calendar events from **Viaggi**.
- A **Viaggio** has at least one **Destinazione**.
- A **Vacanza** is not treated as an ordinary **Viaggio** in the first version.
- When a **Viaggio** is planned, the **Briefing Mattutino** includes the **Meteo Giornaliero** for each relevant **Destinazione**.
- A **Task Inbox** contains candidate **Task** items.
- A **Briefing Mattutino** may include **Task**, **Calendario**, **Contesto Meeting**, and entries from the **Knowledge Base Personale**.
- In the first version, **Contesto Meeting** is derived only from the **Calendario**.
- In a future version, **Contesto Meeting** may also use the **Knowledge Base Personale**.

## Example dialogue

> **Dev:** "Are we building only the morning message?"
> **Domain expert:** "No. The **Briefing Mattutino** is the first **Routine** of the **Assistente Personale Interno**."

## Flagged ambiguities

- "agent AI" is resolved as **Assistente Personale Interno** when discussing product behavior.
- "Hermes" is not a domain term and is not part of the first version; it remains an optional future technical choice.
- A captured item is a **Task** only when it implies a completable next action; otherwise it belongs to the **Calendario** or **Knowledge Base Personale**.
- A calendar event counts as a **Viaggio** when it has a **Destinazione** outside the **Contesto Locale** or uses explicit travel language.
- The first version of the **Briefing Mattutino** excludes menu suggestions and **Task** items.
- The first version assumes an ordinary day in the **Contesto Locale** unless the **Calendario** clearly indicates a **Viaggio**.
- **Vacanza** support is a future capability, not part of the first version.
- **Knowledge Base Personale** support is a future capability, not part of the first version.
- The first version sends at most one **Briefing Mattutino** per day.
