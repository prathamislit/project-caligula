"""Find Permian-related EIA series IDs."""
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
key = os.getenv("EIA_API_KEY")

if not key:
    print("ERROR: EIA_API_KEY not found in .env")
    raise SystemExit(1)

url = "https://api.eia.gov/v2/steo/data/"
params = {
    "api_key": key,
    "frequency": "monthly",
    "data[0]": "value",
    "start": "2024-01",
    "end": "2024-03",
    "offset": 0,
    "length": 5000,
}

r = requests.get(url, params=params, timeout=30)
print("HTTP status:", r.status_code)

if r.status_code != 200:
    print("Body:", r.text[:500])
    raise SystemExit(1)

data = r.json().get("response", {}).get("data", [])
print(f"Total rows returned: {len(data)}")

permian = [d for d in data if "permian" in (
    d.get("seriesDescription") or "").lower()]
print(f"\nPermian-related series found: {len(permian)}")

seen = set()
for d in permian:
    sid = d.get("seriesId")
    if sid not in seen:
        seen.add(sid)
        print(f"  {sid}: {d.get('seriesDescription')}")

if not permian:
    print("\nNo 'permian' matches. Sample of what came back:")
    for d in data[:5]:
        print(f"  {d.get('seriesId')}: {d.get('seriesDescription')}")
