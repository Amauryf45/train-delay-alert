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
    {"id": "stop_area:SNCF:87781278", "name": "Agde"},
    {"id": "stop_area:SNCF:87586008", "name": "Agen"},
    {"id": "stop_area:SNCF:87319012", "name": "Aix-en-Provence TGV"},
    {"id": "stop_area:SNCF:87741132", "name": "Aix-les-Bains - Le Revard"},
    {"id": "stop_area:SNCF:87481192", "name": "Ancenis"},
    {"id": "stop_area:SNCF:87484006", "name": "Angers Saint-Laud"},
    {"id": "stop_area:SNCF:87583005", "name": "Angoulême"},
    {"id": "stop_area:SNCF:87746008", "name": "Annecy"},
    {"id": "stop_area:SNCF:87745497", "name": "Annemasse"},
    {"id": "stop_area:SNCF:87757674", "name": "Antibes"},
    {"id": "stop_area:SNCF:87582668", "name": "Arcachon"},
    {"id": "stop_area:SNCF:87753657", "name": "Arles"},
    {"id": "stop_area:SNCF:87342014", "name": "Arras"},
    {"id": "stop_area:SNCF:87476200", "name": "Auray"},
    {"id": "stop_area:SNCF:87765008", "name": "Avignon Centre"},
    {"id": "stop_area:SNCF:87318964", "name": "Avignon TGV"},
    {"id": "stop_area:SNCF:87271494", "name": "Aéroport Charles de Gaulle 2 TGV"},
    {"id": "stop_area:SNCF:87175042", "name": "Bar-le-Duc"},
    {"id": "stop_area:SNCF:71718010", "name": "Barcelona-Sants"},
    {"id": "stop_area:SNCF:85000109", "name": "Basel SBB"},
    {"id": "stop_area:SNCF:87673004", "name": "Bayonne"},
    {"id": "stop_area:SNCF:87713545", "name": "Beaune"},
    {"id": "stop_area:SNCF:87300822", "name": "Belfort - Montbéliard TGV"},
    {"id": "stop_area:SNCF:87745000", "name": "Bellegarde-sur-Valserine Gare"},
    {"id": "stop_area:SNCF:87300863", "name": "Besançon Franche-Comté TGV"},
    {"id": "stop_area:SNCF:87718007", "name": "Besançon Viotte"},
    {"id": "stop_area:SNCF:87673400", "name": "Biarritz"},
    {"id": "stop_area:SNCF:87582478", "name": "Biganos Facture"},
    {"id": "stop_area:SNCF:87581009", "name": "Bordeaux Saint-Jean"},
    {"id": "stop_area:SNCF:87317586", "name": "Boulogne-sur-Mer"},
    {"id": "stop_area:SNCF:87743005", "name": "Bourg-en-Bresse"},
    {"id": "stop_area:SNCF:87474007", "name": "Brest"},
    {"id": "stop_area:SNCF:88140010", "name": "Bruxelles-Midi / Brussel-Zuid"},
    {"id": "stop_area:SNCF:87342006", "name": "Béthune"},
    {"id": "stop_area:SNCF:87781005", "name": "Béziers"},
    {"id": "stop_area:SNCF:87281071", "name": "Calais - Fréthun"},
    {"id": "stop_area:SNCF:87317263", "name": "Calais Ville"},
    {"id": "stop_area:SNCF:87757625", "name": "Cannes"},
    {"id": "stop_area:SNCF:87615286", "name": "Carcassonne"},
    {"id": "stop_area:SNCF:87725002", "name": "Chalon-sur-Saône"},
    {"id": "stop_area:SNCF:87741009", "name": "Chambéry - Challes-les-Eaux"},
    {"id": "stop_area:SNCF:87171926", "name": "Champagne-Ardenne TGV"},
    {"id": "stop_area:SNCF:87172007", "name": "Charleville-Mézières"},
    {"id": "stop_area:SNCF:87174003", "name": "Châlons-en-Champagne"},
    {"id": "stop_area:SNCF:87575142", "name": "Châtellerault"},
    {"id": "stop_area:SNCF:87182014", "name": "Colmar"},
    {"id": "stop_area:SNCF:87286716", "name": "Croix - Wasquehal"},
    {"id": "stop_area:SNCF:87673202", "name": "Dax"},
    {"id": "stop_area:SNCF:87713040", "name": "Dijon"},
    {"id": "stop_area:SNCF:87478073", "name": "Dol-de-Bretagne"},
    {"id": "stop_area:SNCF:87713412", "name": "Dole-Ville"},
    {"id": "stop_area:SNCF:87345009", "name": "Douai"},
    {"id": "stop_area:SNCF:87281006", "name": "Dunkerque"},
    {"id": "stop_area:SNCF:71043075", "name": "Figueres Vilafant"},
    {"id": "stop_area:SNCF:87715136", "name": "Frasne"},
    {"id": "stop_area:SNCF:80143503", "name": "Freiburg (Breisgau) Hbf"},
    {"id": "stop_area:SNCF:87324095", "name": "Futuroscope"},
    {"id": "stop_area:SNCF:85010082", "name": "Genève Cornavin"},
    {"id": "stop_area:SNCF:71793000", "name": "Girona"},
    {"id": "stop_area:SNCF:87747006", "name": "Grenoble"},
    {"id": "stop_area:SNCF:87473207", "name": "Guingamp"},
    {"id": "stop_area:SNCF:87286302", "name": "Hazebrouck"},
    {"id": "stop_area:SNCF:87677005", "name": "Hendaye"},
    {"id": "stop_area:SNCF:82002501", "name": "Howald"},
    {"id": "stop_area:SNCF:87755629", "name": "Hyères"},
    {"id": "stop_area:SNCF:87481754", "name": "La Baule-Escoublac"},
    {"id": "stop_area:SNCF:87486019", "name": "La Roche-sur-Yon"},
    {"id": "stop_area:SNCF:87485003", "name": "La Rochelle"},
    {"id": "stop_area:SNCF:87582643", "name": "La Teste"},
    {"id": "stop_area:SNCF:80143198", "name": "Lahr (Schwarzw)"},
    {"id": "stop_area:SNCF:87473108", "name": "Lamballe"},
    {"id": "stop_area:SNCF:87474239", "name": "Landerneau"},
    {"id": "stop_area:SNCF:87473223", "name": "Lannion"},
    {"id": "stop_area:SNCF:85011205", "name": "Lausanne"},
    {"id": "stop_area:SNCF:87478404", "name": "Laval"},
    {"id": "stop_area:SNCF:87694109", "name": "Le Creusot - Montceau-les-Mines - Montchanin TGV"},
    {"id": "stop_area:SNCF:87481788", "name": "Le Croisic"},
    {"id": "stop_area:SNCF:87413013", "name": "Le Havre"},
    {"id": "stop_area:SNCF:87396002", "name": "Le Mans"},
    {"id": "stop_area:SNCF:87481762", "name": "Le Pouliguen"},
    {"id": "stop_area:SNCF:87345025", "name": "Lens"},
    {"id": "stop_area:SNCF:87755447", "name": "Les Arcs - Draguignan"},
    {"id": "stop_area:SNCF:87486449", "name": "Les Sables-d'Olonne"},
    {"id": "stop_area:SNCF:87584052", "name": "Libourne"},
    {"id": "stop_area:SNCF:87223263", "name": "Lille Europe"},
    {"id": "stop_area:SNCF:87286005", "name": "Lille Flandres"},
    {"id": "stop_area:SNCF:87476002", "name": "Lorient"},
    {"id": "stop_area:SNCF:87142109", "name": "Lorraine TGV"},
    {"id": "stop_area:SNCF:87671339", "name": "Lourdes"},
    {"id": "stop_area:SNCF:87141150", "name": "Lunéville"},
    {"id": "stop_area:SNCF:82001000", "name": "Luxembourg"},
    {"id": "stop_area:SNCF:87723197", "name": "Lyon Part Dieu"},
    {"id": "stop_area:SNCF:87722025", "name": "Lyon Perrache"},
    {"id": "stop_area:SNCF:87762906", "name": "Lyon Saint-Exupéry TGV"},
    {"id": "stop_area:SNCF:87381509", "name": "Mantes-la-Jolie"},
    {"id": "stop_area:SNCF:87111849", "name": "Marne-la-Vallée - Chessy"},
    {"id": "stop_area:SNCF:87751081", "name": "Marseille Blancarde"},
    {"id": "stop_area:SNCF:87751008", "name": "Marseille Saint-Charles"},
    {"id": "stop_area:SNCF:87393579", "name": "Massy - Palaiseau"},
    {"id": "stop_area:SNCF:87393702", "name": "Massy TGV"},
    {"id": "stop_area:SNCF:87192039", "name": "Metz"},
    {"id": "stop_area:SNCF:87147322", "name": "Meuse TGV"},
    {"id": "stop_area:SNCF:83016451", "name": "Milano Porta Garibaldi"},
    {"id": "stop_area:SNCF:87753004", "name": "Miramas"},
    {"id": "stop_area:SNCF:87742007", "name": "Modane"},
    {"id": "stop_area:SNCF:87611244", "name": "Montauban Ville Bourbon"},
    {"id": "stop_area:SNCF:87713131", "name": "Montbard"},
    {"id": "stop_area:SNCF:87773002", "name": "Montpellier Saint-Roch"},
    {"id": "stop_area:SNCF:87688887", "name": "Montpellier Sud de France"},
    {"id": "stop_area:SNCF:87764001", "name": "Montélimar"},
    {"id": "stop_area:SNCF:87474338", "name": "Morlaix"},
    {"id": "stop_area:SNCF:87718833", "name": "Mouchard"},
    {"id": "stop_area:SNCF:87182063", "name": "Mulhouse"},
    {"id": "stop_area:SNCF:87725689", "name": "Mâcon"},
    {"id": "stop_area:SNCF:87725705", "name": "Mâcon Loché TGV"},
    {"id": "stop_area:SNCF:87141002", "name": "Nancy"},
    {"id": "stop_area:SNCF:87481002", "name": "Nantes"},
    {"id": "stop_area:SNCF:87781104", "name": "Narbonne"},
    {"id": "stop_area:SNCF:87756056", "name": "Nice"},
    {"id": "stop_area:SNCF:87485300", "name": "Niort"},
    {"id": "stop_area:SNCF:87743351", "name": "Nurieux Gare"},
    {"id": "stop_area:SNCF:87775007", "name": "Nîmes Centre"},
    {"id": "stop_area:SNCF:87703975", "name": "Nîmes Pont du Gard"},
    {"id": "stop_area:SNCF:80143099", "name": "Offenburg"},
    {"id": "stop_area:SNCF:87765107", "name": "Orange"},
    {"id": "stop_area:SNCF:87672253", "name": "Orthez"},
    {"id": "stop_area:SNCF:83002048", "name": "Oulx-Cesana-Claviere-Sestriere"},
    {"id": "stop_area:SNCF:87686006", "name": "Paris - Gare de Lyon"},
    {"id": "stop_area:SNCF:87391003", "name": "Paris - Montparnasse"},
    {"id": "stop_area:SNCF:87113001", "name": "Paris Est"},
    {"id": "stop_area:SNCF:87271007", "name": "Paris Nord"},
    {"id": "stop_area:SNCF:87672006", "name": "Pau"},
    {"id": "stop_area:SNCF:87784009", "name": "Perpignan"},
    {"id": "stop_area:SNCF:87473181", "name": "Plouaret Trégor"},
    {"id": "stop_area:SNCF:87575001", "name": "Poitiers"},
    {"id": "stop_area:SNCF:87481747", "name": "Pornichet"},
    {"id": "stop_area:SNCF:87474098", "name": "Quimper"},
    {"id": "stop_area:SNCF:87476317", "name": "Quimperlé"},
    {"id": "stop_area:SNCF:87317057", "name": "Rang-du-Fliers - Verton - Berck"},
    {"id": "stop_area:SNCF:87471300", "name": "Redon"},
    {"id": "stop_area:SNCF:87171009", "name": "Reims"},
    {"id": "stop_area:SNCF:87144451", "name": "Remiremont"},
    {"id": "stop_area:SNCF:87471003", "name": "Rennes"},
    {"id": "stop_area:SNCF:87172270", "name": "Rethel"},
    {"id": "stop_area:SNCF:80143255", "name": "Ringsheim Europa-Park"},
    {"id": "stop_area:SNCF:87474155", "name": "Rosporden"},
    {"id": "stop_area:SNCF:87286732", "name": "Roubaix"},
    {"id": "stop_area:SNCF:87411017", "name": "Rouen Rive Droite"},
    {"id": "stop_area:SNCF:87396408", "name": "Sablé-sur-Sarthe"},
    {"id": "stop_area:SNCF:87473009", "name": "Saint-Brieuc"},
    {"id": "stop_area:SNCF:87144014", "name": "Saint-Dié-des-Vosges"},
    {"id": "stop_area:SNCF:87677120", "name": "Saint-Jean-de-Luz - Ciboure"},
    {"id": "stop_area:SNCF:87742320", "name": "Saint-Jean-de-Maurienne Arvan"},
    {"id": "stop_area:SNCF:87485490", "name": "Saint-Maixent-l'École"},
    {"id": "stop_area:SNCF:87478107", "name": "Saint-Malo"},
    {"id": "stop_area:SNCF:87481705", "name": "Saint-Nazaire"},
    {"id": "stop_area:SNCF:87571240", "name": "Saint-Pierre-des-Corps"},
    {"id": "stop_area:SNCF:87757526", "name": "Saint-Raphaël Valescure"},
    {"id": "stop_area:SNCF:87726000", "name": "Saint-Étienne Châteaucreux"},
    {"id": "stop_area:SNCF:87215012", "name": "Sarrebourg"},
    {"id": "stop_area:SNCF:87487603", "name": "Saumur"},
    {"id": "stop_area:SNCF:87212225", "name": "Saverne"},
    {"id": "stop_area:SNCF:87172254", "name": "Sedan"},
    {"id": "stop_area:SNCF:87212027", "name": "Strasbourg"},
    {"id": "stop_area:SNCF:87485227", "name": "Surgères"},
    {"id": "stop_area:SNCF:87773200", "name": "Sète"},
    {"id": "stop_area:SNCF:87214056", "name": "Sélestat"},
    {"id": "stop_area:SNCF:87313882", "name": "TGV Haute Picardie"},
    {"id": "stop_area:SNCF:87671008", "name": "Tarbes"},
    {"id": "stop_area:SNCF:87191007", "name": "Thionville"},
    {"id": "stop_area:SNCF:87745646", "name": "Thonon-les-Bains"},
    {"id": "stop_area:SNCF:83002196", "name": "Torino Porta Nuova"},
    {"id": "stop_area:SNCF:83000356", "name": "Torino Porta Susa"},
    {"id": "stop_area:SNCF:87755009", "name": "Toulon"},
    {"id": "stop_area:SNCF:87611004", "name": "Toulouse Matabiau"},
    {"id": "stop_area:SNCF:87286542", "name": "Tourcoing"},
    {"id": "stop_area:SNCF:87571000", "name": "Tours"},
    {"id": "stop_area:SNCF:87763029", "name": "Valence TGV Rhône-Alpes Sud"},
    {"id": "stop_area:SNCF:87761007", "name": "Valence Ville"},
    {"id": "stop_area:SNCF:87343004", "name": "Valenciennes"},
    {"id": "stop_area:SNCF:85011031", "name": "Vallorbe"},
    {"id": "stop_area:SNCF:87476606", "name": "Vannes"},
    {"id": "stop_area:SNCF:87571216", "name": "Vendôme - Villiers-sur-Loir"},
    {"id": "stop_area:SNCF:87393009", "name": "Versailles Chantiers"},
    {"id": "stop_area:SNCF:87174276", "name": "Vitry-le-François"},
    {"id": "stop_area:SNCF:87471508", "name": "Vitré"},
    {"id": "stop_area:SNCF:85030007", "name": "Zürich HB"},
    {"id": "stop_area:SNCF:87144006", "name": "Épinal"},
    {"id": "stop_area:SNCF:87317065", "name": "Étaples - Le Touquet"},
    {"id": "stop_area:SNCF:87745679", "name": "Évian-les-Bains"},
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
