"""Refresh data/weather.json from Open-Meteo for Port Vila, Santo and Tanna.

Runs from the repository root: python scripts/update_weather.py [output file]
The output file defaults to data/weather.json.
Uses only the Python standard library. Open-Meteo needs no key for this use
(non-commercial, licence CC BY 4.0, credit is on the guide's information page).
"""
import json, sys, urllib.request
from datetime import datetime, timezone

PLACES = {'Port Vila': (-17.73, 168.33), 'Santo': (-15.52, 167.17), 'Tanna': (-19.53, 169.27)}
URL = ('https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
       '&current=temperature_2m,weather_code'
       '&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max'
       '&timezone=Pacific%2FEfate&forecast_days=8')

def condition(code):
    """Map a World Meteorological Organization weather code to the guide's six conditions."""
    if code in (0,): return 'sunny'
    if code in (1, 2): return 'partly_cloudy'
    if code in (51, 53, 55, 56, 57): return 'drizzle'
    if code in (61, 63, 65, 66, 67, 80, 81, 82): return 'rain'
    if code in (95, 96, 99): return 'thunderstorm'
    return 'cloudy'

def fetch(lat, lon):
    req = urllib.request.Request(URL.format(lat=lat, lon=lon), headers={'User-Agent': 'vanuatu-guide-weather'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def shape(j):
    d = j['daily']
    days = [{'date': d['time'][i],
             'high': round(d['temperature_2m_max'][i], 1),
             'low': round(d['temperature_2m_min'][i], 1),
             'precipitation_chance': int(d['precipitation_probability_max'][i] or 0),
             'condition': condition(d['weather_code'][i])} for i in range(len(d['time']))]
    cur = {'temperature': round(j['current']['temperature_2m'], 1), 'condition': condition(j['current']['weather_code'])}
    return cur, days

def main(path='data/weather.json'):
    isl = {}
    for name, (lat, lon) in PLACES.items():
        cur, days = shape(fetch(lat, lon))
        isl[name] = {'cur': cur, 'days': days}
    now = datetime.now(timezone.utc)
    out = {'asof': isl['Port Vila']['days'][0]['date'], 'loc': 'Port Vila',
           'cur': isl['Port Vila']['cur'], 'days': isl['Port Vila']['days'],
           'updated': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'isl': isl}
    json.dump(out, open(path, 'w', encoding='utf-8'), separators=(',', ':'))
    print('weather updated', out['updated'])

if __name__ == '__main__':
    try:
        main(sys.argv[1]) if len(sys.argv) > 1 else main()
    except Exception as e:
        print('weather update failed:', e)
        sys.exit(1)
