# TODO.md

## Teď (Plán na zítra)

- [x] Vytvořit bezplatný účet na portálu Copernicus Marine Service
- [x] Zprovoznit autentizaci pro stahování dat (přes modul `copernicusmarine`)
- [x] Doprogramovat automatické stahování (přepínač `--download`) do `make_animation_copernicus.py`
- [ ] Ověřit Copernicus `--download` end-to-end nad březnem 2026 s reálnými přihlašovacími údaji
- [ ] Ověřit nové výchozí chování `run.sh` bez argumentů na plném historickém rozsahu (`data/copernicus/daily`) a změřit dobu běhu pro větší rozsah dní

## Další kroky

- [ ] Přidat základní testy nebo alespoň jednoduché smoke testy
- [ ] Přidat do `README.md` i postup k automatickému stahování NOAA OISST dat a práci s daty Copernicus
- [ ] Zvážit nastavení `MPLCONFIGDIR`, pokud bude `matplotlib` cache varování při běhu obtěžovat
- [ ] Zvážit přesun konfigurace rozsahu mapy a názvu výstupu mimo natvrdo zadané konstanty
- [ ] Zvážit přidání dalších mapových vrstev přes `cartopy` nebo jiný zdroj pobřeží a ostrovů
- [ ] Rozhodnout, zda na vizuálně podobnou FB animaci stačí OISST, nebo je potřeba jemnější dataset
- [x] Připravit první variantu workflow nad jemnějším datasetem (např. Copernicus Marine) pro porovnání proti OISST
- [ ] Ověřit Copernicus workflow nad reálnými denními soubory za březen/duben 2026
- [ ] Zvážit změnu layoutu videa pro Facebook Reel formát
- [ ] Doladit styling mapy (labely, grid, colormap) pro publikační verzi na Facebook

## Později

- [ ] Zvážit zabalení skriptu do robustnější CLI struktury
- [ ] Zvážit automatizaci generování více datových výstupů
- [ ] Zvážit build nebo release workflow, pokud se projekt rozšíří

- [ ] Otestovat `--speed-factor 2` na dlouhém rozsahu (rok 2025) a ověřit cílovou délku videa.
