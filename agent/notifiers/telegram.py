import logging
import os

import requests

log = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
# Telegram ha un limite di 4096 caratteri per messaggio
MAX_LENGTH = 4096


def send_message(text: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        _print_fallback(text)
        return

    # Spezza messaggi troppo lunghi
    chunks = _split(text, MAX_LENGTH)
    for chunk in chunks:
        _send_chunk(token, chat_id, chunk)


def _send_chunk(token: str, chat_id: str, text: str) -> None:
    url = TELEGRAM_API.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        log.info("Messaggio Telegram inviato (chat_id=%s, %d chars)", chat_id, len(text))
    except requests.RequestException as e:
        log.error("Errore invio Telegram: %s", e)
        _print_fallback(text)


def _split(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:max_len])
        text = text[max_len:]
    return chunks


def _print_fallback(text: str) -> None:
    separator = "=" * 60
    print(f"\n{separator}")
    print("TELEGRAM non configurato — output su stdout:")
    print(separator)
    print(text)
    print(f"{separator}\n")
