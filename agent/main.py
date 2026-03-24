import logging
import os
import sys
from datetime import datetime

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

# Carica .env prima di tutto (locale: ./data, Docker: sovrascritta da env_file)
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("morning-agent")


def _motivational_quote() -> str:
    from llm import chat

    return chat(
        [
            {
                "role": "user",
                "content": (
                    "Dammi una breve frase motivazionale in italiano (massimo 2 righe), "
                    "originale, ispirata e adatta a iniziare bene la giornata. "
                    "Rispondi con la sola frase, senza virgolette né commenti."
                ),
            }
        ],
        temperature=0.9,
    )


def run_briefing() -> None:
    log.info("▶ Avvio briefing mattutino")

    # Import lazy: così gli errori di config esplodono a runtime, non all'avvio
    from notifiers.telegram import send_message
    from tools.menu import suggest_menu
    from tools.tasks import format_tasks, get_top_tasks
    from tools.weather import get_weather_report

    now = datetime.now()
    # Formato italiano: "Martedì 25 Marzo 2025"
    locale_days = [
        "Lunedì",
        "Martedì",
        "Mercoledì",
        "Giovedì",
        "Venerdì",
        "Sabato",
        "Domenica",
    ]
    locale_months = [
        "",
        "Gennaio",
        "Febbraio",
        "Marzo",
        "Aprile",
        "Maggio",
        "Giugno",
        "Luglio",
        "Agosto",
        "Settembre",
        "Ottobre",
        "Novembre",
        "Dicembre",
    ]
    date_str = (
        f"{locale_days[now.weekday()]} {now.day} {locale_months[now.month]} {now.year}"
    )

    # 1. Meteo
    log.info("Recupero meteo...")
    weather = get_weather_report()

    # 2. Menu
    log.info("Generazione menu...")
    lunch, dinner = suggest_menu()

    # 3. Task
    log.info("Lettura task...")
    tasks = get_top_tasks(3)
    tasks_text = format_tasks(tasks)

    # 4. Frase motivazionale
    log.info("Generazione frase motivazionale...")
    quote = _motivational_quote()

    message = (
        f"🌅 *Buongiorno! Briefing del {date_str}*\n"
        f"\n"
        f"☀️ *METEO*\n"
        f"{weather}\n"
        f"\n"
        f"🍽️ *MENU DI OGGI*\n"
        f"• Pranzo: {lunch}\n"
        f"• Cena: {dinner}\n"
        f"\n"
        f"✅ *TOP 3 TASK*\n"
        f"{tasks_text}\n"
        f"\n"
        f"💡 *FRASE DEL GIORNO*\n"
        f"_{quote}_"
    )

    log.info("Invio notifica...")
    send_message(message)
    log.info("✓ Briefing completato")


def main() -> None:
    run_now = os.getenv("RUN_NOW", "false").lower() == "true"
    hour = int(os.getenv("BRIEFING_HOUR", "7"))
    minute = int(os.getenv("BRIEFING_MINUTE", "0"))
    tz = pytz.timezone("Europe/Rome")

    if run_now:
        log.info("RUN_NOW=true → esecuzione immediata")
        run_briefing()

    scheduler = BlockingScheduler(timezone=tz)
    scheduler.add_job(run_briefing, "cron", hour=hour, minute=minute)
    log.info(
        "Scheduler avviato: briefing ogni giorno alle %02d:%02d (Europe/Rome)",
        hour,
        minute,
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler fermato.")


if __name__ == "__main__":
    main()
