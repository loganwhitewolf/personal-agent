import json
import logging
import os
import re
from datetime import datetime

log = logging.getLogger(__name__)

FAMILY_CONTEXT = """\
Famiglia: 2 adulti e 2 bambine (5 e 9 anni).
Stile culinario: cucina mediterranea, semplice e genuina.
Vincoli alimentari:
- Un adulto è intollerante al lattosio: evitare latte, formaggi, burro (ok yogurt senza lattosio, ok parmigiano stagionato in piccole quantità)
- Un adulto ha colite ulcerosa sotto controllo: evitare cibi fritti, molto piccanti, legumi in grandi quantità, verdure crude a foglia larga, eccesso di fibre; \
preferire cotture leggere (vapore, forno, griglia), cibi facilmente digeribili
- Le bambine apprezzano piatti semplici, non troppo elaborati\
"""


def _meals_file() -> str:
    data_path = os.getenv("DATA_PATH", "./data")
    return os.path.join(data_path, "meals.json")


def _load() -> dict:
    try:
        with open(_meals_file(), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"week": "", "meals": []}


def _save(data: dict) -> None:
    path = _meals_file()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _current_week() -> str:
    return datetime.now().strftime("%Y-W%V")


def _recent_summary(meals_data: dict) -> str:
    meals = meals_data.get("meals", [])
    if not meals:
        return "Nessun pasto registrato di recente."
    recent = meals[-7:]
    return "\n".join(
        f"- {m['date']}: pranzo → {m['lunch']} | cena → {m['dinner']}"
        for m in recent
    )


def suggest_menu() -> tuple[str, str]:
    from llm import chat

    meals_data = _load()
    recent_summary = _recent_summary(meals_data)
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_label = datetime.now().strftime("%A %d %B %Y")

    prompt = f"""\
Sei un nutrizionista esperto di cucina mediterranea.
Oggi è {today_label}.

{FAMILY_CONTEXT}

Pasti degli ultimi giorni (evita ripetizioni):
{recent_summary}

Suggerisci pranzo e cena per oggi: piatti bilanciati, vari, adatti a tutta la famiglia.
Rispondi ESCLUSIVAMENTE con un oggetto JSON valido, senza testo aggiuntivo, in questo formato:
{{"lunch": "nome del piatto con ingredienti principali", "dinner": "nome del piatto con ingredienti principali"}}"""

    raw = chat([{"role": "user", "content": prompt}], temperature=0.8)

    lunch, dinner = "Suggerimento non disponibile", "Suggerimento non disponibile"
    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            menu = json.loads(match.group())
            lunch = menu.get("lunch", lunch)
            dinner = menu.get("dinner", dinner)
    except (json.JSONDecodeError, KeyError) as e:
        log.warning("Parsing menu fallito: %s — raw: %s", e, raw)

    # Persisti il menu di oggi
    current_week = _current_week()
    if meals_data.get("week") != current_week:
        # Nuova settimana: resetta ma tieni gli ultimi 2 giorni per contesto
        meals_data = {"week": current_week, "meals": meals_data.get("meals", [])[-2:]}

    meals_data["meals"] = [m for m in meals_data["meals"] if m.get("date") != today_str]
    meals_data["meals"].append({"date": today_str, "lunch": lunch, "dinner": dinner})
    _save(meals_data)

    return lunch, dinner
