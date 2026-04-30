# PROJECT_CONTEXT.md

## Stručný popis projektu

Malý Python skriptový projekt pro načtení NOAA OISST NetCDF datasetu a render výstupu teploty mořské hladiny pro oblast Kanárských ostrovů, nově i jako denní animace za březen 2026.

## Aktuální stav

- Projekt obsahuje původní skript `render_oisst.py` pro jednorázový PNG render ze souboru `data/oisst.nc`.
- Nově je přidán skript `make_march_2026_animation.py` pro první použitelný workflow animace:
  - očekává NOAA OISST denní soubory v `data/daily/`
  - vyrenderuje denní frame PNG do `frames/march_2026/`
  - složí MP4 do `output/canary_sst_march_2026.mp4` přes `ffmpeg`
- Závislosti jsou definované v `requirements.txt`.
- V repozitáři není `README.md`.
- V repozitáři není test suite.
- Vstupní NetCDF data nejsou součástí verzovaných souborů; podle `.gitignore` se očekávají v `data/*.nc`.
- Výstupní obrázky a framy se ukládají do `output/` a `frames/`, které jsou ignorované v Gitu.
- `ffmpeg` je v systému dostupný.
- NOAA OISST 0.25° je funkční pro první verzi animace, ale pro vzhled blízký referenčnímu FB reelu je dataset hrubý.

## Používaný stack

- Python
- `xarray`
- `netCDF4`
- `numpy`
- `matplotlib`
- systémový `ffmpeg`

## Hlavní adresáře a soubory

- `render_oisst.py` - jednorázový PNG render z `data/oisst.nc`
- `make_march_2026_animation.py` - dávkový render frame pro březen 2026 + složení MP4
- `requirements.txt` - Python závislosti
- `.gitignore` - ignoruje `data/*.nc`, `output/`, `frames/`, `__pycache__/`, `.venv/`
- `data/` - lokální vstupní NetCDF soubory, nejsou verzované
- `frames/` - generované framy, není verzované
- `output/` - generované výstupy, není verzované

## Jak projekt spustit

Zatím není definováno v README. Ověřený lokální postup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python render_oisst.py
python make_march_2026_animation.py
```

Pro animaci března 2026 skript očekává denní NOAA soubory pojmenované jako:

- `data/daily/oisst-avhrr-v02r01.20260301.nc`
- ...
- `data/daily/oisst-avhrr-v02r01.20260331.nc`

Pokud některé soubory chybí, skript je vypíše a pokračuje; MP4 vytvoří jen pokud existuje alespoň jeden vyrenderovaný frame.

## Jak projekt testovat

- Automatické testy: nezjištěno
- Formální test příkaz: zatím není definováno
- Minimální ověření kódu: `python3 -m py_compile render_oisst.py make_march_2026_animation.py`
- Smoke test průchodu workflow: `python make_march_2026_animation.py`

## Jak projekt buildit

- Build proces: zatím není definováno
- Projekt se aktuálně chová jako přímo spouštěné Python skripty bez samostatného build kroku

## Známá omezení / problémy

- Skript pro animaci očekává konkrétní NOAA naming pattern denních souborů.
- Bez lokálních denních `.nc` souborů za březen 2026 se nevyrenderují framy a MP4 se přeskočí.
- Není k dispozici README ani formální dokumentace spuštění.
- Není k dispozici test suite.
- `matplotlib` může v některých prostředích hlásit ne zapisovatelný defaultní config adresář.
- NOAA OISST používá hrubé rozlišení `0.25°`, takže pro jemnější vizuální výsledek podobný FB reelu bude pravděpodobně potřeba detailnější dataset nebo doplnění mapových vrstev.

## Poznámky pro další navázání

- Při navazování vždy nejdřív zkontrolovat `git status`.
- Nepředpokládat nic ze starých chatů; brát jako zdroj pravdy jen tento repozitář.
- Pokud se změní způsob spuštění, testování nebo struktura projektu, aktualizovat tento soubor.
- Pokud přibudou důležitá technická rozhodnutí, zapsat je do `DECISIONS.md`.
