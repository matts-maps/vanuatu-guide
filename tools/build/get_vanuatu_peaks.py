"""Download Vanuatu peaks and volcanoes, with their elevation tags, from OpenStreetMap.

Writes vanuatu-peaks-ele.csv next to this script.
Needs Python 3 and the requests package.
"""
import csv
import sys
from pathlib import Path

import requests

QUERY = """
[out:json][timeout:120];
(
  node["natural"~"^(peak|volcano)$"](-20.5,166.4,-13.0,170.4);
);
out tags center;
"""

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

data = None
for url in MIRRORS:
    try:
        print("Trying", url)
        r = requests.post(url, data={"data": QUERY}, timeout=180,
                          headers={"User-Agent": "vanuatu-guide-peaks/1.0"})
        r.raise_for_status()
        data = r.json()
        break
    except Exception as e:
        print("  failed:", e)

if data is None:
    sys.exit("All Overpass servers failed. Try again in a few minutes.")

out = Path(__file__).with_name("vanuatu-peaks-ele.csv")
rows = []
for el in data["elements"]:
    t = el.get("tags", {})
    rows.append([el["id"], el["lat"], el["lon"], t.get("name", ""),
                 t.get("natural", ""), t.get("ele", "")])

with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["osm_id", "lat", "lon", "name", "natural", "ele"])
    w.writerows(rows)

with_ele = sum(1 for r in rows if r[5])
print(f"Saved {len(rows)} peaks and volcanoes ({with_ele} with an elevation) to {out}")
