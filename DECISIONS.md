# DECISIONS.md

## Datum

- 2026-04-30

## Důležitá technická rozhodnutí

- Projekt je aktuálně veden jako jednoduchý Python skript bez zavádění dalšího frameworku.
- Závislosti jsou aktuálně spravované přes `requirements.txt`.
- Vstupní NetCDF data nejsou součástí repozitáře a očekávají se lokálně v `data/`.
- Vstupní NOAA OISST soubor se v projektu používá pod lokálním názvem `data/oisst.nc`, i když stažený originál může mít jiný NOAA název.
- Aktuální render používá převedené longitude do západních hodnot `-20 .. -10`, tmavou masku pevniny a jemnější interpolaci, aby byl výstup čitelnější i bez dalších mapových knihoven.

## Použité technologie

- Python
- `xarray`
- `netCDF4`
- `numpy`
- `matplotlib`

## Důvody důležitých voleb

- Jednoduchá skriptová forma odpovídá současnému malému rozsahu projektu.
- `requirements.txt` je pro aktuální rozsah projektu nejjednodušší a dostatečný způsob evidence závislostí.
- Ignorování vstupních dat a výstupů v Gitu odpovídá tomu, že jde o generované nebo objemné soubory.
- Stabilní lokální název `data/oisst.nc` zjednodušuje skript i onboarding bez nutnosti hned zavádět CLI parametry.
- Současný projekt zůstává bez nových těžších závislostí, dokud nebude rozhodnuto, zda chceme jít cestou rychlé OISST animace, nebo přesnější mapové vizualizace.

## Otevřené otázky

- Zda má skript zůstat jednoduchý jednorázový nástroj, nebo se rozšířit do plnohodnotnější CLI aplikace.
- Zda parametrizovat vstup, výstup, datum a geografický výřez.
- Zda přidat formální testy a dokumentaci spuštění.
- Zda pro animaci března 2026 použít přímo NOAA OISST, nebo hledat jemnější dataset bližší vzhledu referenčního FB reelu.

## Nezaznamenaná rozhodnutí

Další zásadní technická rozhodnutí zatím nejsou zaznamenána.
