import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SNCF_API_KEY = os.getenv("SNCF_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DELAY_THRESHOLD_MINUTES = 30
STATE_FILE = Path("state.json")

MONITORED_STATIONS = [
    # Paris & Île-de-France
    {"id": "stop_area:SNCF:87686006", "name": "Paris Gare de Lyon"},
    {"id": "stop_area:SNCF:87391003", "name": "Paris Montparnasse"},
    {"id": "stop_area:SNCF:87113001", "name": "Paris Est"},
    {"id": "stop_area:SNCF:87271007", "name": "Paris Nord"},
    {"id": "stop_area:SNCF:87001479", "name": "Marne-la-Vallée Chessy"},
    {"id": "stop_area:SNCF:87271460", "name": "CDG TGV"},
    # Nord
    {"id": "stop_area:SNCF:87286005", "name": "Lille Flandres"},
    {"id": "stop_area:SNCF:87223263", "name": "Lille Europe"},
    # Est
    {"id": "stop_area:SNCF:87212027", "name": "Strasbourg"},
    {"id": "stop_area:SNCF:87192039", "name": "Metz"},
    {"id": "stop_area:SNCF:87141002", "name": "Nancy"},
    {"id": "stop_area:SNCF:87342002", "name": "Besançon Franche-Comté TGV"},
    # Sud-Est
    {"id": "stop_area:SNCF:87723197", "name": "Lyon Part-Dieu"},
    {"id": "stop_area:SNCF:87758037", "name": "Valence TGV"},
    {"id": "stop_area:SNCF:87318964", "name": "Avignon TGV"},
    {"id": "stop_area:SNCF:87319012", "name": "Aix-en-Provence TGV"},
    {"id": "stop_area:SNCF:87751008", "name": "Marseille Saint-Charles"},
    {"id": "stop_area:SNCF:87756056", "name": "Nice Ville"},
    {"id": "stop_area:SNCF:87773002", "name": "Montpellier Saint-Roch"},
    {"id": "stop_area:SNCF:87779000", "name": "Perpignan"},
    # Sud-Ouest
    {"id": "stop_area:SNCF:87581009", "name": "Bordeaux Saint-Jean"},
    {"id": "stop_area:SNCF:87611004", "name": "Toulouse Matabiau"},
    # Ouest
    {"id": "stop_area:SNCF:87481002", "name": "Nantes"},
    {"id": "stop_area:SNCF:87471003", "name": "Rennes"},
    {"id": "stop_area:SNCF:87396002", "name": "Le Mans"},
]

LONG_DISTANCE_DESTINATIONS = [
    "Marseille", "Nice", "Montpellier", "Lyon", "Bordeaux",
    "Toulouse", "Nantes", "Strasbourg", "Lille", "Marne", "Paris",
]


def parse_sncf_time(dt_str: str) -> datetime:
    return datetime.strptime(dt_str, "%Y%m%dT%H%M%S")


def get_delayed_departures(station: dict) -> list[dict]:
    url = f"https://api.sncf.com/v1/coverage/sncf/stop_areas/{station['id']}/departures"
    resp = requests.get(
        url,
        auth=(SNCF_API_KEY, ""),
        params={"count": 50, "data_freshness": "realtime"},
        timeout=10,
    )
    resp.raise_for_status()

    delayed = []
    for dep in resp.json().get("departures", []):
        sdt = dep.get("stop_date_time", {})
        rt = sdt.get("departure_date_time")
        base = sdt.get("base_departure_date_time")

        if not rt or not base:
            continue

        rt_dt = parse_sncf_time(rt)
        base_dt = parse_sncf_time(base)
        delay_min = (rt_dt - base_dt).total_seconds() / 60

        if delay_min < DELAY_THRESHOLD_MINUTES:
            continue

        direction = dep.get("display_informations", {}).get("direction", "")
        if not any(kw.lower() in direction.lower() for kw in LONG_DISTANCE_DESTINATIONS):
            continue

        delayed.append({
            "station": station["name"],
            "train": dep.get("display_informations", {}).get("label", "?"),
            "direction": direction,
            "scheduled": base_dt.strftime("%H:%M"),
            "expected": rt_dt.strftime("%H:%M"),
            "delay_min": int(delay_min),
        })

    return delayed


def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)


def load_state() -> set[str]:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()


def save_state(alerted: set[str]):
    STATE_FILE.write_text(json.dumps(list(alerted)))


def run():
    if os.getenv("TEST_MODE"):
        send_telegram("TEST: bot Telegram OK - train TGV8412 retard +45min Marne-la-Vallee -> Marseille")
        print("Test notification sent.")
        return

    alerted = load_state()
    today = datetime.now().strftime("%Y-%m-%d")

    # Reset state daily to avoid unbounded growth
    alerted = {k for k in alerted if k.startswith(today)}

    for station in MONITORED_STATIONS:
        try:
            delayed = get_delayed_departures(station)
            for train in delayed:
                key = f"{today}-{train['train']}-{train['scheduled']}"
                if key in alerted:
                    continue
                alerted.add(key)

                msg = (
                    f"Train retard +{train['delay_min']}min\n"
                    f"{train['station']} -> {train['direction']}\n"
                    f"Prevu {train['scheduled']}, attendu {train['expected']}\n"
                    f"Train {train['train']}"
                )
                send_telegram(msg)
                print(f"ALERT: {msg}")

        except Exception as e:
            print(f"[{station['name']}] Error: {e}")

    save_state(alerted)


if __name__ == "__main__":
    run()
