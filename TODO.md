# TODO.md

## Teď

- [ ] Doplnit `README.md` se skutečným návodem ke spuštění projektu
- [ ] Připravit workflow pro rendery více dní a složení MP4 animace za březen 2026
- [ ] Rozhodnout, zda mají být vstupní a výstupní cesty parametrizovatelné přes CLI argumenty

## Další kroky

- [ ] Přidat základní testy nebo alespoň jednoduché smoke testy
- [ ] Přidat do `README.md` i postup získání NOAA OISST souboru a jeho uložení do `data/oisst.nc`
- [ ] Zvážit nastavení `MPLCONFIGDIR`, pokud bude `matplotlib` cache varování při běhu obtěžovat
- [ ] Zvážit přesun konfigurace rozsahu mapy a názvu výstupu mimo natvrdo zadané konstanty
- [ ] Zvážit přidání mapových vrstev přes `cartopy` nebo jiný zdroj pobřeží a ostrovů
- [ ] Rozhodnout, zda na vizuálně podobnou FB animaci stačí OISST, nebo je potřeba jemnější dataset

## Později

- [ ] Zvážit zabalení skriptu do robustnější CLI struktury
- [ ] Zvážit automatizaci generování více datových výstupů
- [ ] Zvážit build nebo release workflow, pokud se projekt rozšíří
