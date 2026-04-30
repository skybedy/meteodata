# DECISIONS.md

## Datum

- 2026-04-30

## Důležitá technická rozhodnutí

- Projekt je aktuálně veden jako jednoduché Python skripty bez zavádění dalšího frameworku.
- Závislosti jsou aktuálně spravované přes `requirements.txt`.
- Vstupní NetCDF data nejsou součástí repozitáře a očekávají se lokálně v `data/`.
- Původní jednorázový render zůstává v `render_oisst.py` se vstupem `data/oisst.nc`.
- Pro první použitelný workflow animace za březen 2026 byl přidán samostatný skript `make_march_2026_animation.py`, který:
  - načítá NOAA OISST denní soubory po jednotlivých dnech,
  - renderuje PNG frame do `frames/march_2026/`,
  - skládá MP4 do `output/canary_sst_march_2026.mp4` přes `ffmpeg`.
- Workflow je navržen tak, aby při chybějících denních souborech pokračoval a vypsal missing seznam místo pádu.
- Skládání videa používá v `ffmpeg` glob pattern pro soubory `frame_*.png` a pad filtr na sudé rozměry, aby bylo kompatibilní s `libx264`.
- První funkční animace za březen 2026 byla úspěšně vyrenderována z 31 NOAA denních souborů do `output/canary_sst_march_2026.mp4`.

## Použité technologie

- Python
- `xarray`
- `netCDF4`
- `numpy`
- `matplotlib`
- systémový `ffmpeg`

## Důvody důležitých voleb

- Samostatný skript pro animaci je nejjednodušší praktický krok bez velkého refaktoru existujícího jednorázového rendereru.
- Použití NOAA naming patternu (`oisst-avhrr-v02r01.YYYYMMDD.nc`) umožňuje přímočaré mapování dne na vstupní soubor.
- Tolerantní chování při chybějících souborech zjednodušuje první iteraci workflow i průběžné testování.
- Zachování dosavadního stylu mapy (rozsah, colormap, tmavá maska pevniny, bicubic interpolace) drží vizuální kontinuitu výstupů.
- Glob pattern a padding v `ffmpeg` jsou jednodušší a robustnější než spoléhat na date-format placeholder jako vstup image sekvence.
- Nejpraktičtější další iterace už není stabilita workflow, ale vizuální kvalita a případná vhodnost výstupu pro Facebook Reel.

## Otevřené otázky

- Zda má skript zůstat jednoduchý jednorázový nástroj, nebo se rozšířit do plnohodnotnější CLI aplikace.
- Zda sjednotit oba skripty (`render_oisst.py` a `make_march_2026_animation.py`) pod jednu CLI entrypoint vrstvu.
- Zda přidat formální testy a dokumentaci spuštění.
- Zda pro animaci března 2026 použít přímo NOAA OISST, nebo hledat jemnější dataset bližší vzhledu referenčního FB reelu.

## Nezaznamenaná rozhodnutí

Další zásadní technická rozhodnutí zatím nejsou zaznamenána.
