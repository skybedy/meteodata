# TODO.md

## Teď

- [ ] Doplnit `README.md` se skutečným návodem ke spuštění projektu
- [x] Zobecnit skripty pro animaci, aby fungovaly pro libovolný měsíc nebo časový úsek (např. --month 2026-04 nebo --start-date)
- [x] Přidat automatické stahování chybějících NOAA dat ze serveru (přepínač --download)
- [ ] Rozhodnout, jak moc chceme jít za vizuální podobností s referenčním FB reelem

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
