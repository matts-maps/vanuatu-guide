# Vanuatu: Interactive Guide

A hand-drawn interactive map and guide to Vanuatu. It starts on Port Vila and Efate and covers things to do, dive and snorkel sites, volcanoes, history, annual events, hotels, airports and ports, day plans and a trip planner with export.

It is a static website: `index.html` plus lazy-loaded data files in `data/`. There is no build step on GitHub.

## Put it online (GitHub Pages)
Open a command prompt in this folder.

1. Create an empty public repository named `vanuatu-guide` on GitHub (Pages on a free account needs a public repository). Do not add a README or licence there.
2. Run these commands, replacing `matts-maps` if the repository is under another account:
   - `git init -b main`
   - `git add .`
   - `git commit -m "Vanuatu guide"`
   - `git remote add origin https://github.com/matts-maps/vanuatu-guide.git`
   - `git push -u origin main`
3. On GitHub open the repository, then Settings, Pages. Under Build and deployment choose Deploy from a branch, branch `main`, folder `/ (root)`, and save.
4. After a minute the guide is at `https://matts-maps.github.io/vanuatu-guide/`.
5. For the hourly weather: Settings, Actions, General, Workflow permissions, choose Read and write permissions, and save. Then open the Actions tab, choose Update weather and press Run workflow once to test it.

## Weather
`.github/workflows/update-weather.yml` runs every hour and runs `scripts/update_weather.py`. The script reads Open-Meteo for Port Vila, Santo and Tanna and rewrites `data/weather.json`, and the workflow commits it when it changes. GitHub switches off scheduled workflows after 60 days without repository activity, so open Actions and re-enable it if the weather bar starts showing "out of date". The guide itself marks forecasts older than three hours as out of date.

## Updating the guide
The source lives in the Claude project folder `cowork-projects/travel/2026-interactive-guide-vanuatu/build/`. After a change, run `python gen2.py` then `python make_site.py` there, copy everything inside the new `site/` folder over this repository (keep `data/weather.json` from here, not the older copy), then commit and push.

## Data and credits
- Roads, rivers, villages, houses, hills and volcano heights: OpenStreetMap contributors, Open Database Licence, extracted by Geofabrik on 22 November 2026.
- Coastlines: Natural Earth (public domain) and the Global Self-consistent Hierarchical High-resolution Geography database.
- Airports: OurAirports (public domain). Port Vila main port: World Port Index, United States National Geospatial-Intelligence Agency.
- Weather: Open-Meteo.com, licence CC BY 4.0.
- Map fonts: Google Fonts (Caveat, Caveat Brush, Patrick Hand, Space Mono).

No licence file is included yet. Choose one before inviting others to reuse the code.
