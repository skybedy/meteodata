# Meteodata Visualization Tools

Tento projekt obsahuje sadu Python skriptů pro vizualizaci teploty mořské hladiny (SST) v oblasti Kanárských ostrovů. Podporuje data z NOAA OISST a Copernicus Marine Service.

## Hlavní skripty

- `make_animation.py`: Generuje animace z NOAA OISST dat (rozlišení 0.25°).
- `make_animation_copernicus.py`: Generuje animace z Copernicus Marine dat (rozlišení 0.083°), podporuje regionální výřezy (např. Tenerife) a web export.
- `render_oisst.py`: Jednorázový render PNG mapy z NOAA dat.

## Instalace

1. Vytvořte virtuální prostředí:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Nainstalujte závislosti:
   ```bash
   pip install -r requirements.txt
   ```

3. Nainstalujte `ffmpeg` (vyžadováno pro tvorbu videa).

## Použití

### Copernicus (Vysoké rozlišení)

Pro stahování dat z Copernicu je nutný účet. Přihlašovací údaje nastavte v souboru `.env` nebo jako environment proměnné:
- `COPERNICUSMARINE_SERVICE_USERNAME`
- `COPERNICUSMARINE_SERVICE_PASSWORD`

Příklad vygenerování videa pro Tenerife za duben 2026 s vlastní teplotní škálou:
```bash
./run.sh 2026-04 --region tenerife --vmin 18 --vmax 24
```

Web export (frames + manifest + volitelně video):
```bash
./run.sh 2026-04 --region tenerife --web-export
```

Více detailů: `docs/copernicus-web-export.md`.

### NOAA OISST

```bash
python make_animation.py --month 2026-04 --download
```

## Regiony (Copernicus)
V současnosti jsou podporovány tyto regiony:
- `canary`: Celá oblast Kanárských ostrovů.
- `tenerife`: Detailní výřez kolem ostrova Tenerife.

## Výstupy
- Framy (jednotlivé dny) se ukládají do složky `frames/`.
- Výsledná MP4 videa se ukládají do složky `output/`.
- Při `--web-export` se výstup ukládá do `exports/copernicus/sea-temp/<region>/<YYYY>/<MM>/`.
