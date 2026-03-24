import json
import logging
import os

log = logging.getLogger(__name__)


def _tasks_file() -> str:
    data_path = os.getenv("DATA_PATH", "./data")
    return os.path.join(data_path, "tasks.json")


def get_top_tasks(n: int = 3) -> list[dict]:
    try:
        with open(_tasks_file(), encoding="utf-8") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        log.warning("tasks.json non trovato in %s", _tasks_file())
        return []
    except json.JSONDecodeError as e:
        log.error("tasks.json malformato: %s", e)
        return []

    active = [t for t in tasks if not t.get("done", False)]
    active.sort(key=lambda t: t.get("priority", 999))
    return active[:n]


def format_tasks(tasks: list[dict]) -> str:
    if not tasks:
        return "_Nessun task attivo._"

    priority_icon = {1: "🔴", 2: "🟡", 3: "🟢"}
    lines = []
    for i, task in enumerate(tasks, 1):
        icon = priority_icon.get(task.get("priority", 3), "⚪")
        line = f"{i}. {icon} *{task['title']}*"
        if task.get("notes"):
            line += f"\n   _{task['notes']}_"
        lines.append(line)

    return "\n".join(lines)
