import os
import logging
from datetime import datetime, date

import requests

log = logging.getLogger(__name__)

FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

FASCE = [
    ("🌙 Notte",      0,  6),
    ("🌅 Mattina",    6, 12),
    ("☀️ Pomeriggio", 12, 18),
    ("🌆 Sera",       18, 24),
]


def _fetch_forecast(city: str) -> dict:
    api_key = os.getenv("OPENWEATHER_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_KEY non configurata")

    resp = requests.get(
        FORECAST_URL,
        params={"q": city, "appid": api_key, "units": "metric", "lang": "it", "cnt": 16},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _parse_fasce(data: dict, today: date) -> dict:
    """Raggruppa le previsioni orarie nelle 4 fasce del giorno."""
    fasce_data = {label: [] for label, _, _ in FASCE}

    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        if dt.date() != today:
            continue
        hour = dt.hour
        for label, start, end in FASCE:
            if start <= hour < end:
                fasce_data[label].append({
                    "desc": item["weather"][0]["description"].capitalize(),
                    "temp": round(item["main"]["temp"]),
                    "feels_like": round(item["main"]["feels_like"]),
                    "humidity": item["main"]["humidity"],
                    "wind_kmh": round(item["wind"]["speed"] * 3.6),
                })
                break

    return fasce_data


def _format_city(city: str, today: date) -> str:
    data = _fetch_forecast(city)
    fasce_data = _parse_fasce(data, today)

    lines = [f"*{city}*:"]
    wind_vals, hum_vals = [], []

    for label, _, _ in FASCE:
        slots = fasce_data[label]
        if not slots:
            continue
        # media temperatura, descrizione più frequente
        avg_temp = round(sum(s["temp"] for s in slots) / len(slots))
        avg_feels = round(sum(s["feels_like"] for s in slots) / len(slots))
        desc = max(set(s["desc"] for s in slots), key=lambda d: sum(1 for s in slots if s["desc"] == d))
        wind_vals.extend(s["wind_kmh"] for s in slots)
        hum_vals.extend(s["humidity"] for s in slots)
        lines.append(f"  {label}: {desc}, {avg_temp}°C (percepiti {avg_feels}°C)")

    if wind_vals and hum_vals:
        avg_wind = round(sum(wind_vals) / len(wind_vals))
        avg_hum = round(sum(hum_vals) / len(hum_vals))
        lines.append(f"  💨 Vento: {avg_wind} km/h | 💧 Umidità: {avg_hum}%")

    return "\n".join(lines)


def get_weather_report() -> str:
    primary_city = os.getenv("CITY", "Cherasco")
    cities = [primary_city]

    # Il mercoledì (weekday == 2) aggiungi Milano e Torino
    if datetime.now().weekday() == 2:
        cities += ["Milano", "Torino"]

    today = date.today()
    blocks = []
    for city in cities:
        try:
            blocks.append(_format_city(city, today))
        except Exception as e:
            log.warning("Meteo non disponibile per %s: %s", city, e)
            blocks.append(f"*{city}*: meteo non disponibile")

    return "\n\n".join(blocks)
