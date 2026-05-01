# DECISIONS.md

## Datum

- 2026-04-30

## Důležitá technická rozhodnutí

- Projekt je aktuálně veden jako jednoduché Python skripty bez zavádění dalšího frameworku.
- Závislosti jsou aktuálně spravované přes `requirements.txt`.
- `START_NEW_CODEX_CHAT.md` má fungovat jako lokální handoff šablona pro tento konkrétní repozitář a nesmí obsahovat přenesený kontext z jiného projektu.
- Vstupní NetCDF data nejsou součástí repozitáře a očekávají se lokálně v `data/`.
- Původní jednorázový render zůstává v `render_oisst.py` se vstupem `data/oisst.nc`.
- Skript pro animaci NOAA dat byl zobecněn a přejmenován na `make_animation.py`, který:
  - podporuje dynamické určení rozsahu dnů přes `--month YYYY-MM` nebo `--start-date` a `--end-date`,
  - načítá NOAA OISST denní soubory po jednotlivých dnech,
  - renderuje PNG framy do složek typu `frames/YYYY_MM/`,
  - skládá MP4 videa jako např. `output/canary_sst_YYYY_MM.mp4` přes `ffmpeg`.
  - navíc umí s parametrem `--download` automaticky stahovat chybějící NetCDF soubory přímo z veřejných NOAA THREDDS serverů do `data/daily/`.
- Workflow je navržen tak, aby při chybějících denních souborech pokračoval a vypsal missing seznam místo pádu.
- Skládání videa používá v `ffmpeg` glob pattern pro soubory `frame_*.png` a pad filtr na sudé rozměry, aby bylo kompatibilní s `libx264`.
- První funkční animace za březen 2026 byla úspěšně vyrenderována z 31 NOAA denních souborů do `output/canary_sst_march_2026.mp4`.
- Výchozí FPS animace bylo sníženo na `3`, aby 31 denních frame vytvořilo zhruba desetisekundové video.
- Render byl migrován na `cartopy` + Natural Earth `10m` vrstvy (`land`, `coastline`) pro korektní geometrii pobřeží a Kanárských ostrovů.
- Workflow skriptu byl doplněn o přepínač `--clean-frames`, aby šel opakovaně spouštět bez míchání starých a nových frame.
- Workflow skriptu validuje `--fps > 0`, aby se předešlo neplatné konfiguraci `ffmpeg`.
- Pro první vizuální zlepšení byly v SST renderu doplněny chybějící pobřežní pixely přes nearest interpolaci, aby v mořské části nezůstávaly černé maskované plochy.
- Workflow skriptu nově podporuje `--upscale-factor` (výchozí `4`) pro jemnější vykreslení OISST mřížky bez změny zdroje dat.
- Pro další výrazný kvalitativní posun vzhledu směrem k FB reelu je doporučený další krok jemnější SST dataset (např. Copernicus Marine), protože OISST 0.25° zůstává datově hrubý.
- Pro porovnání kvality byl přidán paralelní skript `make_animation_copernicus.py`, který kopíruje OISST workflow a také plně podporuje generování map napříč libovolnými daty přes `--month` a `--start-date`.
- Copernicus skript podporuje konfigurovatelný naming (`--filename-template`) a autodetekci běžných názvů SST proměnné a souřadnic, aby fungoval nad různými NetCDF exporty bez refaktoru.
- Copernicus workflow bylo sjednoceno s NOAA i na úrovni přepínačů: skript `make_animation_copernicus.py` nově podporuje `--download`, aby uměl automaticky stáhnout chybějící denní soubory.
- Pro Copernicus stahování je zvolena knihovna `copernicusmarine` (přidána do `requirements.txt`) a přihlašovací údaje jsou řešeny přes CLI argumenty (`--copernicus-username`, `--copernicus-password`) nebo přes env proměnné `COPERNICUSMARINE_SERVICE_USERNAME` a `COPERNICUSMARINE_SERVICE_PASSWORD`.

## Použité technologie

- Python
- `xarray`
- `netCDF4`
- `numpy`
- `matplotlib`
- `cartopy`
- systémový `ffmpeg`

## Důvody důležitých voleb

- Samostatný skript pro animaci je nejjednodušší praktický krok bez velkého refaktoru existujícího jednorázového rendereru.
- Použití NOAA naming patternu (`oisst-avhrr-v02r01.YYYYMMDD.nc`) umožňuje přímočaré mapování dne na vstupní soubor a rovnou umožňuje i spolehlivé automatické stahování z NOAA serveru.
- Tolerantní chování při chybějících souborech zjednodušuje iteraci workflow, zejména s ohledem na 14denní zpoždění dostupnosti dat NOAA v reálném čase.
- Zachování dosavadního stylu mapy (rozsah, colormap, tmavá maska pevniny, bicubic interpolace) drží vizuální kontinuitu výstupů.
- Glob pattern a padding v `ffmpeg` jsou jednodušší a robustnější než spoléhat na date-format placeholder jako vstup image sekvence.
- Nejpraktičtější další iterace už není stabilita workflow, ale vizuální kvalita a případná vhodnost výstupu pro Facebook Reel.
- Cartopy řeší přesnost pobřeží bez ručního kreslení ostrovů a drží stejný Python stack jako zbytek projektu.

## Otevřené otázky

- Zda má skript zůstat jednoduchý jednorázový nástroj, nebo se rozšířit do plnohodnotnější CLI aplikace.
- Zda sjednotit oba skripty (`render_oisst.py` a `make_animation.py`) pod jednu CLI entrypoint vrstvu.
- Zda přidat formální testy a dokumentaci spuštění.
- Zda pro animaci března 2026 použít přímo NOAA OISST, nebo hledat jemnější dataset bližší vzhledu referenčního FB reelu.

## Nezaznamenaná rozhodnutí

Další zásadní technická rozhodnutí zatím nejsou zaznamenána.
