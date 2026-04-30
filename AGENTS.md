# AGENTS.md

## Role Codexu v projektu

Codex v tomto repozitáři funguje jako průběžný technický spolupracovník, který navazuje pouze podle souborů v repozitáři a podle aktuálního stavu working tree. Nesmí spoléhat na historii starých chatů.

## Aktuálně zjištěný stack

- Hlavní jazyk projektu: Python
- Správa závislostí: `requirements.txt`
- Použité knihovny: `xarray`, `netCDF4`, `numpy`, `matplotlib`
- Aktuální forma projektu: jednoduchý CLI / skriptový nástroj pro render výstupu z NetCDF dat

## Obecné preference uživatele

- Hlavní jazyk preferuj Go, pokud projekt neurčuje jinak.
- Frontend preferuj Vanilla JavaScript.
- UI navrhuj jednoduše, čistě a prakticky.
- Pokud je potřeba stylování, preferuj Tailwind.
- Nepřidávej zbytečně složité frameworky.
- Vývoj probíhá na Linux Mint.
- Nasazení serveru bývá typicky Ubuntu VPS.

## Pravidla práce

- Nejdřív vždy čti aktuální stav projektu.
- Vždy zkontroluj `git status`.
- Nepředpokládej kontext ze starých chatů.
- Před větší změnou stručně popiš plán.
- Po změně spusť dostupné testy nebo build.
- Důležitá rozhodnutí zapisuj do `DECISIONS.md`.
- Aktuální stav zapisuj do `PROJECT_CONTEXT.md`.
- Další kroky zapisuj do `TODO.md`.
- Nepřidávej do commitu `.env` ani jiné citlivé soubory.

## Poznámka k tomuto repozitáři

Aktuální repozitář je nyní Python projekt, takže preference pro Go se zde nepoužije, pokud se projekt zásadně nepřestaví.
