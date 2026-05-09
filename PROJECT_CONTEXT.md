# PROJECT_CONTEXT.md

## Stručný popis projektu

Malý Python skriptový projekt pro načtení NOAA OISST NetCDF datasetu a render výstupu teploty mořské hladiny pro oblast Kanárských ostrovů, nově i jako denní animace za březen 2026.

## Aktuální stav

- Projekt obsahuje původní skript `render_oisst.py` pro jednorázový PNG render ze souboru `data/oisst.nc`.
- Nově je přidán skript `make_animation.py` pro plně dynamický workflow animace:
  - očekává nebo automaticky stahuje NOAA OISST denní soubory do `data/daily/` pomocí přepínače `--download`
  - podporuje `--month` nebo `--start-date` a `--end-date` pro volbu časového rozpětí
  - vyrenderuje denní frame PNG do dynamicky vytvořených složek ve `frames/`
  - složí MP4 pomocí `ffmpeg` do `output/`
  - podporuje `--clean-frames` pro smazání starých frame před novým během
  - validuje `--fps > 0`
  - podporuje `--upscale-factor` (výchozí `4`) pro jemnější vykreslení SST mřížky
  - při renderu doplňuje malé pobřežní/maskované mezery v SST přes nearest interpolaci, aby nevznikaly černé „díry“ v moři
- Závislosti jsou definované v `requirements.txt`.
- V repozitáři není `README.md`.
- V repozitáři není test suite.
- Soubor `START_NEW_CODEX_CHAT.md` je repo-specifická předávací šablona pro navázání v novém chatu a má zůstávat sladěný s aktuálním stavem tohoto Python projektu.
- Vstupní NetCDF data nejsou součástí verzovaných souborů; podle `.gitignore` se očekávají v `data/*.nc`.
- Výstupní obrázky a framy se ukládají do `output/` a `frames/`, které jsou ignorované v Gitu.
- `ffmpeg` je v systému dostupný.
- NOAA OISST 0.25° je funkční pro první verzi animace, ale pro vzhled blízký referenčnímu FB reelu je dataset hrubý.
- Upscale v renderu zlepšuje vizuální plynulost, ale nepřidává novou fyzikální informaci; pro výrazně vyšší kvalitu je další krok jemnější dataset (např. Copernicus Marine).
- Nově je přidán i první paralelní skript `make_animation_copernicus.py` pro stejný výstupní workflow (daily frame + MP4) nad jemnějším zdrojem dat:
  - umí generovat dny dynamicky přes stejné CLI argumenty jako NOAA skript,
  - očekává denní Copernicus `.nc` soubory v `data/copernicus/daily/`,
  - umí přes `--download` automaticky stáhnout chybějící denní Copernicus soubory,
  - pro `--download` používá přihlášení přes argumenty (`--copernicus-username`, `--copernicus-password`) nebo env proměnné (`COPERNICUSMARINE_SERVICE_USERNAME`, `COPERNICUSMARINE_SERVICE_PASSWORD`),
  - podporuje konfigurovatelný naming přes `--filename-template` s placeholderem `{date}`,
  - umí autodetekci běžných názvů proměnných/souřadnic (`analysed_sst`/`thetao`/`sst`, `latitude|lat`, `longitude|lon`),
  - obsahuje stejné kroky jako OISST workflow: nearshore fill, volitelný upscale, `--clean-frames`, MP4 přes `ffmpeg`.
- `run.sh` nově bez argumentů automaticky vezme historický rozsah z lokálně dostupných Copernicus denních souborů (od nejstaršího po nejnovější), takže se ve výstupu neztratí historie kvůli fixnímu měsíci.
- `make_animation_copernicus.py` má explicitní validaci argumentu `--month` ve formátu `YYYY-MM`.
- `make_animation_copernicus.py` nově podporuje `--region` s presety `canary` a `tenerife`, který řídí geografický výřez pro render i automatické stahování dat.
- Skládání MP4 z frame bylo lokálně ověřeno přes `ffmpeg` na testovacím frame se jménem ve formátu `frame_YYYY-MM-DD.png`.
- End-to-end workflow pro `2026-03-01` až `2026-03-31` bylo lokálně ověřeno nad 31 NOAA denními soubory v `data/daily/`.
- Vznikl výstup `output/canary_sst_march_2026.mp4` a 31 frame v `frames/march_2026/`.
- Render běží přes `cartopy` s Natural Earth `10m` GIS vrstvami (`land` + `coastline`), takže Kanárské ostrovy i pobřeží Afriky mají korektní geometrii.
- Výchozí FPS animace je `3`, takže 31 denních frame dává video dlouhé přibližně `10.33 s`.

## Používaný stack

- Python
- `xarray`
- `netCDF4`
- `numpy`
- `matplotlib`
- `cartopy`
- `copernicusmarine`
- systémový `ffmpeg`

## Hlavní adresáře a soubory

- `render_oisst.py` - jednorázový PNG render z `data/oisst.nc`
- `make_animation.py` - dávkový render frame pro libovolné datum a NOAA data s podporou automatického stahování
- `make_animation_copernicus.py` - paralelní varianta stejného workflow pro Copernicus data
- `requirements.txt` - Python závislosti
- `.gitignore` - ignoruje `data/*.nc`, `output/`, `frames/`, `__pycache__/`, `.venv/`
- `data/` - lokální vstupní NetCDF soubory, nejsou verzované
- `data/cartopy/` - lokální cache GIS podkladů (Natural Earth), stahuje se automaticky při prvním renderu
- `frames/` - generované framy, není verzované
- `output/` - generované výstupy, není verzované

## Jak projekt spustit

Zatím není definováno v README. Ověřený lokální postup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python render_oisst.py
python make_animation.py --month 2026-04 --download
```

Pro animaci z NOAA dat skript očekává denní NOAA soubory pojmenované jako:

- `data/daily/oisst-avhrr-v02r01.YYYYMMDD.nc`

Pokud některé soubory chybí, skript je vypíše a pokračuje; MP4 vytvoří jen pokud existuje alespoň jeden vyrenderovaný frame.

## Jak projekt testovat

- Automatické testy: nezjištěno
- Formální test příkaz: zatím není definováno
- Minimální ověření kódu: `python3 -m py_compile render_oisst.py make_animation.py`
- Smoke test průchodu workflow: `python make_animation.py --month 2026-03`
- Smoke test skládání MP4: ověřeno lokálně přes `ffmpeg` nad testovacím frame exportem
- End-to-end ověření: `python make_animation.py --month 2026-03` úspěšně vyrenderoval framy a vytvořil funkční `.mp4` video.

## Jak projekt buildit

- Build proces: zatím není definováno
- Projekt se aktuálně chová jako přímo spouštěné Python skripty bez samostatného build kroku

## Známá omezení / problémy

- Skript pro animaci očekává konkrétní NOAA naming pattern denních souborů.
- Aktuální vizuální kvalita je pořád jednodušší než referenční FB reel hlavně kvůli hrubému rozlišení OISST `0.25°`.
- Není k dispozici README ani formální dokumentace spuštění.
- Není k dispozici test suite.
- `matplotlib` může v některých prostředích hlásit ne zapisovatelný defaultní config adresář.
- Při prvním běhu `cartopy` stahuje Natural Earth data; bez síťového přístupu je potřeba mít `data/cartopy/` už připravené.

## Poznámky pro další navázání

- Při navazování vždy nejdřív zkontrolovat `git status`.
- Nepředpokládat nic ze starých chatů; brát jako zdroj pravdy jen tento repozitář.
- Ověřený výstup animace má `31` frame, délku přibližně `10.33 s`, rozlišení `1424x1104` a `3 fps`.
- Pokud se změní způsob spuštění, testování nebo struktura projektu, aktualizovat tento soubor.
- Pokud přibudou důležitá technická rozhodnutí, zapsat je do `DECISIONS.md`.

- `make_animation_copernicus.py` nově podporuje `--speed-factor` pro volitelné zrychlení přehrávání výsledného MP4 (násobení FPS při kompozici videa).
- Barevná škála Copernicus SST renderu je aktuálně fixně nastavena na `17-26 °C`.

- **Duben 2026 (Tenerife)**: Úspěšně vygenerováno video za celý duben 2026 s detailním výřezem pro Tenerife pomocí Copernicus dat. Výstup: `output/tenerife_sst_2026_04_copernicus.mp4`.
- Projekt nyní obsahuje `README.md` s dokumentací.
