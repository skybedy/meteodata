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
- Skládání MP4 z frame bylo lokálně ověřeno přes `ffmpeg` na testovacím frame se jménem ve formátu `frame_YYYY-MM-DD.png`.
- End-to-end workflow pro `2026-03-01` až `2026-03-31` bylo lokálně ověřeno nad 31 NOAA denními soubory v `data/daily/`.
- Vznikl výstup `output/canary_sst_march_2026.mp4` a 31 frame v `frames/march_2026/`.
- Do renderu byla doplněna přibližná ručně kreslená vrstva hlavních Kanárských ostrovů, aby byly v animaci viditelné i bez GIS knihoven.
- Výchozí FPS animace je `3`, takže 31 denních frame dává video dlouhé přibližně `10.33 s`.

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
- Smoke test skládání MP4: ověřeno lokálně přes `ffmpeg` nad testovacím frame exportem
- End-to-end ověření: `python make_march_2026_animation.py` úspěšně vyrenderoval 31 frame a vytvořil `output/canary_sst_march_2026.mp4`

## Jak projekt buildit

- Build proces: zatím není definováno
- Projekt se aktuálně chová jako přímo spouštěné Python skripty bez samostatného build kroku

## Známá omezení / problémy

- Skript pro animaci očekává konkrétní NOAA naming pattern denních souborů.
- Bez lokálních denních `.nc` souborů za březen 2026 se nevyrenderují framy a MP4 se přeskočí.
- Aktuální vizuální kvalita je pořád výrazně jednodušší než referenční FB reel, hlavně kvůli hrubému rozlišení OISST a chybějícím přesným GIS mapovým vrstvám.
- Vrstva Kanárských ostrovů je zatím ručně kreslená aproximace pomocí elips, ne přesná pobřežní geometrie.
- Není k dispozici README ani formální dokumentace spuštění.
- Není k dispozici test suite.
- `matplotlib` může v některých prostředích hlásit ne zapisovatelný defaultní config adresář.
- NOAA OISST používá hrubé rozlišení `0.25°`, takže pro jemnější vizuální výsledek podobný FB reelu bude pravděpodobně potřeba detailnější dataset nebo doplnění mapových vrstev.

## Poznámky pro další navázání

- Při navazování vždy nejdřív zkontrolovat `git status`.
- Nepředpokládat nic ze starých chatů; brát jako zdroj pravdy jen tento repozitář.
- Ověřený výstup animace má `31` frame, délku přibližně `10.33 s`, rozlišení `1424x1104` a `3 fps`.
- Pokud se změní způsob spuštění, testování nebo struktura projektu, aktualizovat tento soubor.
- Pokud přibudou důležitá technická rozhodnutí, zapsat je do `DECISIONS.md`.
