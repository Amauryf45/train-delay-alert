import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SNCF_API_KEY")
BASE = "https://api.sncf.com/v1/coverage/sncf"


def get(path, params=None):
    resp = requests.get(f"{BASE}{path}", auth=(API_KEY, ""), params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def find_tgv_mode():
    data = get("/commercial_modes")
    for mode in data.get("commercial_modes", []):
        if "tgv" in mode["id"].lower() or "tgv" in mode.get("name", "").lower():
            print(f"Found mode: {mode['id']} — {mode['name']}")
    return [m for m in data["commercial_modes"] if "tgv" in m["id"].lower() or "tgv" in m.get("name", "").lower()]


def fetch_stop_areas(mode_id):
    stop_areas = []
    start_page = 0
    while True:
        data = get(f"/commercial_modes/{mode_id}/stop_areas", params={"count": 100, "start_page": start_page})
        batch = data.get("stop_areas", [])
        if not batch:
            break
        stop_areas.extend(batch)
        if len(batch) < 100:
            break
        start_page += 1
    return stop_areas


if __name__ == "__main__":
    modes = find_tgv_mode()
    if not modes:
        print("No TGV mode found. Listing all modes:")
        data = get("/commercial_modes")
        for m in data["commercial_modes"]:
            print(f"  {m['id']} — {m.get('name')}")
    else:
        all_stops = []
        for mode in modes:
            stops = fetch_stop_areas(mode["id"])
            all_stops.extend(stops)

        seen = set()
        unique = []
        for s in all_stops:
            if s["id"] not in seen:
                seen.add(s["id"])
                unique.append(s)

        unique.sort(key=lambda s: s["name"])
        print(f"\n{len(unique)} unique TGV stop areas:\n")
        print("MONITORED_STATIONS = [")
        for s in unique:
            print(f'    {{"id": "{s["id"]}", "name": "{s["name"]}"}},')
        print("]")
