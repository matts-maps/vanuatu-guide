"""Make the files for the Claude artifact copy of the guide in artifact/.

Run from tools/build:  python make_artifact.py
The repository root is the hosted site (GitHub Pages) and is the source of truth.
The artifact copy differs in one line only: the weather credit on data-sources.html,
which names Open-Meteo on the hosted site and says "an online weather service" in the artifact.
Writes artifact/index.html and artifact/data-sources.html. Publish those two files plus the
six files in ../../fonts/ (as fonts/...) in patch mode, and never overwrite data/weather.json (the hourly
task refreshes it). The artifact has no sw.js, manifest or icons, which is fine: the page ignores a
missing service worker.
"""
import os, shutil
root, dst = '../..', 'artifact'
os.makedirs(dst, exist_ok=True)
shutil.copyfile(f'{root}/index.html', f'{dst}/index.html')
ds = open(f'{root}/data-sources.html', encoding='utf-8').read()
old = 'Weather: forecasts from <a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo.com</a> (licence CC BY 4.0), refreshed about hourly.'
new = 'Weather: forecasts from an online weather service, refreshed about hourly.'
assert old in ds, 'Open-Meteo credit line not found in data-sources.html'
open(f'{dst}/data-sources.html', 'w', encoding='utf-8').write(ds.replace(old, new, 1))
print('artifact files ready in tools/build/artifact/')
