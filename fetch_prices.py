import requests, json, os
from datetime import datetime, timedelta

ZONE = "PCB"
today = datetime.now().strftime("%Y-%m-%d")
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

prices = {}
headers = {"User-Agent": "Mozilla/5.0"}

for date in [today, tomorrow]:
    url = f"https://api.preciodelaluz.org/v1/prices/all?zone={ZONE}&date={date}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        prices[date] = r.json()
        print(f"OK: {date} — {len(prices[date])} horas")
    except Exception as e:
        print(f"ERROR {date}: {e}")

os.makedirs("data", exist_ok=True)
with open("data/prices.json", "w") as f:
    json.dump({"updated": datetime.now().isoformat(), "prices": prices}, f)

print("Guardado en data/prices.json")
