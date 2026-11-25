# Build tools

Scripts and source data for the guide. The repository root is the hosted site, so every script writes straight into it (`../../index.html` and `../../data/`). Run them from `tools/build/`.

## Folders
- `tools/build/` - scripts, the page template (`template.html`) and small input files (`pois.py`, `stays.json`, `trans.json`, `routes.json`, `wx.json`).
- `tools/source-data/` - raw downloads: Natural Earth land, OurAirports rows for Vanuatu, peak heights, and the Geofabrik OpenStreetMap shapefile zip (22 November 2026).

## Change the page or the places
1. Edit `pois.py` (places), `stays.json`, `trans.json`, `routes.json` or `template.html`.
2. Open a command prompt in `tools/build/` and run `python gen2.py`. It rewrites `../../index.html` and a local `../../test.html` (not committed).
3. Open `index.html` in a browser (or serve the repository root with `python -m http.server 8765`) and check it.
4. Commit and push. GitHub Pages republishes after a minute.

`gen2.py` fills five placeholders in `template.html`: `/*DATA*/`, `/*WX*/`, `/*STAYS*/`, `/*TRANS*/` and `/*ROUTES*/`. It reproduces the current `index.html` exactly, so a change should only show what you meant to change.

## Rebuild the map data (rarely needed)
These overwrite files in `data/`, so run them on a branch.
1. Install the packages once: `pip install pyshp shapely requests playwright`, then `playwright install chromium`.
2. Extract the shapefiles from `../source-data/vanuatu-261122-free.shp.zip` into `tools/build/` (the scripts expect names such as `gis_osm_roads_free_1.shp` beside them).
3. Run, in order: `python process.py`, `python roads_split.py`, `python decor.py`, `python islets.py`, `python routes.py`, `python update_airports.py`.
4. For hill and volcano heights: `python get_vanuatu_peaks.py` (writes `vanuatu-peaks-ele.csv`; move it into `../source-data/`), then `python add_peak_elevations.py`.
5. `python check.py` tests the page in a browser (set the Chrome path inside the file for Windows).

`decor_gshhg.py` is an alternative coastline script. Do not edit `data/weather.json`: the hourly workflow refreshes it.

## Claude artifact copy
`python make_artifact.py` writes `artifact/index.html` and `artifact/data-sources.html`, the only two files that differ from the hosted site (the weather credit line). Publish just those two files in patch mode.
