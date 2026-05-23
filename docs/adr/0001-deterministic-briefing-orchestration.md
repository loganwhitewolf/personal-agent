# Deterministic Briefing Orchestration

The **Briefing Mattutino** is orchestrated as controlled sections from structured sources, with an LLM used only for human-facing prose such as clothing advice and the motivational closing. We deliberately avoid a fully autonomous agent loop for the first version because the briefing must not invent calendar events, weather, or destinations, and its daily Telegram format should remain predictable.

**Considered Options**

- Fully agentic orchestration with an AI agent deciding which tools to call.
- Deterministic orchestration with targeted LLM calls for natural-language advice.

**Consequences**

- New briefing sections need explicit source and formatting logic.
- LLM output is constrained to interpretation and wording rather than ownership of factual data.
