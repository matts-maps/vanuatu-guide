"""Add OpenStreetMap elevation (ele tag) to the hills and volcanoes in ../../data/decor.json.

Reads ../source-data/vanuatu-peaks-ele.csv (from get_vanuatu_peaks.py).
Each peak becomes [lon, lat, type, name, ele or null]. Hills with a recorded
height of 0 or under 150 m are removed, so hill symbols only sit on high ground.
Run from the build folder: python add_peak_elevations.py
"""
import csv, json, math, sys
src = sys.argv[1] if len(sys.argv) > 1 else '../source-data/vanuatu-peaks-ele.csv'
rows = list(csv.DictReader(open(src, encoding='utf-8')))
dec = json.load(open('../../data/decor.json', encoding='utf-8'))
out, dropped = [], []
for p in dec['peaks']:
    p = p[:4]
    best = min(rows, key=lambda r: math.hypot(float(r['lon']) - p[0], float(r['lat']) - p[1]))
    ok = math.hypot(float(best['lon']) - p[0], float(best['lat']) - p[1]) < 0.003
    ele = int(float(best['ele'])) if ok and best['ele'].strip() else None
    if p[2] == 1 and ele is not None and (ele <= 0 or ele < 150):
        dropped.append((p[3] or 'unnamed', ele)); continue
    out.append(p + [ele])
dec['peaks'] = out
json.dump(dec, open('../../data/decor.json', 'w', encoding='utf-8', newline=''), separators=(',', ':'), ensure_ascii=False)
print(len(out), 'kept;', 'with height:', sum(1 for p in out if p[4] is not None), '; removed:', dropped)
