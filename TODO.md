# TODO.md

## Teď (Plán na zítra)

- [ ] Vytvořit bezplatný účet na portálu Copernicus Marine Service
- [ ] Zprovoznit autentizaci pro stahování dat (přes modul `copernicusmarine`)
- [ ] Doprogramovat automatické stahování (přepínač `--download`) do `make_animation_copernicus.py`

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
