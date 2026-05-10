# Copernicus web export (Meteodata -> go-tene.life)

## Co export dělá

Rozšířený skript `make_animation_copernicus.py` umí nově vygenerovat statický webový balíček:

- denní obrázky po dnech (`YYYY-MM-DD.png`)
- `manifest.json` kompatibilní se statickým JS viewerem
- volitelně `video.mp4`

## Spuštění

Příklad pro Tenerife, duben 2026:

```bash
./run.sh 2026-04 --region tenerife --web-export
```

Alternativa přímo přes Python:

```bash
.venv/bin/python make_animation_copernicus.py \
  --month 2026-04 \
  --region tenerife \
  --download \
  --web-export
```

Bez videa (jen frames + manifest):

```bash
.venv/bin/python make_animation_copernicus.py --month 2026-04 --region tenerife --web-export --skip-video
```

## Kam se výstup ukládá

Výchozí cesta:

`exports/copernicus/sea-temp/<region>/<YYYY>/<MM>/`

Např.:

`exports/copernicus/sea-temp/tenerife/2026/04/`

Obsah složky:

- `2026-04-01.png`
- `2026-04-02.png`
- ...
- `manifest.json`
- `video.mp4` (pokud není použit `--skip-video`)

## Kopie do go-tene.life

Meteodata vytvoří:

`exports/copernicus/sea-temp/tenerife/2026/04/`

Tento obsah zkopírujte do:

`go-tene.life/public/data/copernicus/sea-temp/tenerife/2026/04/`

Viewer potom načítá:

`/data/copernicus/sea-temp/tenerife/2026/04/manifest.json`

## Poznámka pro další měsíc

Pro další měsíc stačí změnit `--month YYYY-MM` a znovu spustit export.

## Co zůstává na další fázi

- Archiv více měsíců / více regionů přes jednotný index
- Automatizace měsíčního exportu (cron/CI)
- Volitelný sync script mezi repozitáři
