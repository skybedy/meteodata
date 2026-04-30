# PROJECT_CONTEXT.md

## Stručný popis projektu

Malý Python skript pro načtení NOAA OISST NetCDF datasetu a vyrenderování obrázku teploty mořské hladiny pro oblast Kanárských ostrovů.

## Aktuální stav

- Projekt obsahuje jeden hlavní skript `render_oisst.py`.
- Závislosti jsou definované v `requirements.txt`.
- V repozitáři není `README.md`.
- V repozitáři není test suite.
- Vstupní NetCDF data nejsou součástí verzovaných souborů; podle `.gitignore` se očekávají v `data/*.nc`.
- Výstupní obrázky se ukládají do `output/`, který je ignorovaný v Gitu.
- End-to-end běh byl lokálně ověřen se souborem `data/oisst.nc`.
- Ověřený výstupní soubor je `output/canary_sst_2024-03-01.png`.
- Vizualizace byla upravena tak, aby používala západní délky `-20 .. -10`, tmavou masku pevniny a jemnější interpolaci.
- `ffmpeg` je v systému dostupný, takže je možné skládat rendery do MP4 animace.

## Používaný stack

- Python
- `xarray`
- `netCDF4`
- `numpy`
- `matplotlib`

## Hlavní adresáře a soubory

- `render_oisst.py` - hlavní skript pro načtení datasetu a render PNG mapy
- `requirements.txt` - Python závislosti
- `.gitignore` - ignoruje `data/*.nc`, `output/`, `frames/`, `__pycache__/`, `.venv/`
- `data/` - lokální vstupní NetCDF soubory, nejsou verzované
- `output/` - vytváří se za běhu, není verzovaný

## Jak projekt spustit

Zatím není definováno v README. Ověřený lokální postup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python render_oisst.py
```

Před spuštěním musí existovat vstupní soubor `data/oisst.nc`.

## Jak projekt testovat

- Automatické testy: nezjištěno
- Formální test příkaz: zatím není definováno
- Minimální ověření kódu: lze spustit syntaktickou kontrolu `python3 -m py_compile render_oisst.py`
- Smoke test průchodu: `python render_oisst.py` v aktivované `.venv`

## Jak projekt buildit

- Build proces: zatím není definováno
- Projekt se aktuálně chová jako přímo spouštěný Python skript bez samostatného build kroku

## Známá omezení / problémy

- Skript má natvrdo zadané vstupní i výstupní cesty.
- Skript má natvrdo zadaný název výstupního souboru a datum v titulku grafu.
- Bez `data/oisst.nc` skript nepůjde spustit.
- Není k dispozici README ani formální dokumentace spuštění.
- Není k dispozici test suite.
- `matplotlib` v tomto prostředí hlásil ne zapisovatelný defaultní config adresář a použil dočasný cache adresář v `/tmp`; běh tím nebyl zablokovaný.
- NOAA OISST v tomto projektu používá hrubé rozlišení `0.25°`, takže výstup nestačí na detail a vzhled referenčního FB reelu bez lepších dat nebo mapových vrstev.
- V prostředí zatím není nainstalovaný `cartopy`, `scipy` ani `imageio`.

## Poznámky pro další navázání

- Při navazování vždy nejdřív zkontrolovat `git status`.
- Nepředpokládat nic ze starých chatů; brát jako zdroj pravdy jen tento repozitář.
- Poslední ověřený běh pro `2024-03-01` vypsal `shape (32, 40)`, `lat range 24.125 .. 31.875`, `lon range 340.125 .. 349.875`, `min 14.420`, `max 22.020`, `mean 19.864`.
- Byl analyzován referenční FB reel: `18.4 s`, `944x720`, `30 fps`, datově pokrývá přibližně `2026-03-01` až `2026-03-22`, používá škálu zhruba `16.0 .. 20.0 °C` a obsahuje pobřeží Afriky i Kanárské ostrovy.
- Pokud se změní způsob spuštění, testování nebo struktura projektu, aktualizovat tento soubor.
- Pokud přibudou důležitá technická rozhodnutí, zapsat je do `DECISIONS.md`.
