# TODO.md

## Teď

- [ ] Doplnit `README.md` se skutečným návodem ke spuštění projektu
- [x] Připravit workflow pro rendery více dní a složení MP4 animace za březen 2026
- [x] Ověřit workflow s reálnými NOAA denními soubory za celé období `2026-03-01` až `2026-03-31`
- [ ] Připravit skript nebo návod na získání denních NOAA souborů do `data/daily/`
- [ ] Rozhodnout, jak moc chceme jít za vizuální podobností s referenčním FB reelem
- [x] Zpomalit výsledné video, aby netrvalo jen zhruba dvě sekundy
- [x] Přepnout render na GIS vrstvy pobřeží a ostrovů přes `cartopy`
- [x] Doplnit opakovatelnost workflow přes volbu `--clean-frames` a validaci `--fps`
- [x] Omezit černé maskované plochy v moři doplněním pobřežních SST mezer
- [x] Přidat jemnější vykreslení přes `--upscale-factor` pro méně kostičkovaný vizuál

## Další kroky

- [ ] Přidat základní testy nebo alespoň jednoduché smoke testy
- [ ] Přidat do `README.md` i postup získání NOAA OISST denních souborů a jejich uložení do `data/daily/`
- [ ] Rozhodnout, zda mají být vstupní a výstupní cesty dál parametrizovatelné přes CLI argumenty i v `render_oisst.py`
- [ ] Zvážit nastavení `MPLCONFIGDIR`, pokud bude `matplotlib` cache varování při běhu obtěžovat
- [ ] Zvážit přesun konfigurace rozsahu mapy a názvu výstupu mimo natvrdo zadané konstanty
- [ ] Zvážit přidání mapových vrstev přes `cartopy` nebo jiný zdroj pobřeží a ostrovů
- [ ] Rozhodnout, zda na vizuálně podobnou FB animaci stačí OISST, nebo je potřeba jemnější dataset
- [x] Připravit první variantu workflow nad jemnějším datasetem (např. Copernicus Marine) pro porovnání proti OISST
- [ ] Ověřit Copernicus workflow nad reálnými denními soubory za `2026-03-01` až `2026-03-31`
- [ ] Zvážit změnu layoutu videa pro Facebook Reel formát
- [ ] Doladit styling mapy (labely, grid, colormap) pro publikační verzi na Facebook

## Později

- [ ] Zvážit zabalení skriptu do robustnější CLI struktury
- [ ] Zvážit automatizaci generování více datových výstupů
- [ ] Zvážit build nebo release workflow, pokud se projekt rozšíří
