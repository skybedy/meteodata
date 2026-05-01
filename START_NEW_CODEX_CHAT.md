# Start nového Codex chatu

## Prompt pro Antigravity / Gemini

Pracuj v repozitáři `/home/skybedy/Programming/cli/meteodata`.

Nejdřív si přečti:

- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `TODO.md`
- `DECISIONS.md`
- `START_NEW_CODEX_CHAT.md`

Pak spusť:

```bash
git branch --show-current
git status --short
```

Nepředpokládej kontext z předchozího chatu. Navaž jen na aktuální stav souborů a working tree. Nerevertuj nesouvisející změny. Před úpravami si vždy projdi relevantní soubory.

### Aktuální předávka

Aktuální projekt: `/home/skybedy/Programming/cli/meteodata`

Aktuální větev: `main`

Cíl projektu:

Renderovat mapové výstupy sea surface temperature pro Kanárské ostrovy z NetCDF dat, a to jak jako jednorázový PNG render, tak jako vícedenní MP4 animace.

Důležité soubory:

- `render_oisst.py`
- `make_animation.py`
- `make_animation_copernicus.py`
- `requirements.txt`
- `PROJECT_CONTEXT.md`
- `TODO.md`
- `DECISIONS.md`

Aktuální stav funkcionality:

- `render_oisst.py` dělá jednorázový PNG render ze souboru `data/oisst.nc`.
- `make_animation.py` generuje NOAA OISST animaci z denních souborů v `data/daily/`.
- NOAA skript podporuje `--month` nebo dvojici `--start-date` / `--end-date`.
- NOAA skript umí přes `--download` automaticky stáhnout chybějící denní OISST soubory.
- NOAA skript podporuje `--clean-frames`, `--fps` a `--upscale-factor`.
- `make_animation_copernicus.py` dělá stejný typ workflow nad denními Copernicus daty v `data/copernicus/daily/`.
- Copernicus skript podporuje `--filename-template` s placeholderem `{date}` a autodetekci běžných názvů proměnných a souřadnic.
- Výstupy jdou do `frames/` a `output/`, které nejsou verzované.
- Projekt zatím nemá formální test suite ani `README.md`.

Pozor:

- Jde o Python skriptový projekt, ne Go projekt.
- Při práci se drž jednoduchého současného stylu, bez zavádění nových frameworků.
- Vstupní data v `data/` nejsou verzovaná a nemají se přidávat do commitu.
- `output/`, `frames/`, `.venv/` ani citlivé lokální soubory necommitovat.
- Pokud změníš workflow, CLI argumenty nebo očekávanou strukturu vstupních dat, aktualizuj i `PROJECT_CONTEXT.md`, `TODO.md` a `DECISIONS.md`.

Ověření, které má smysl pustit po změnách:

```bash
python3 -m py_compile render_oisst.py make_animation.py make_animation_copernicus.py
```

Pokud jsou lokálně dostupná data, můžeš použít i smoke test:

```bash
python3 make_animation.py --month 2026-03
python3 make_animation_copernicus.py --month 2026-03
```

Nejbližší možné další kroky:

- Doplnit automatické stahování Copernicus dat.
- Přidat stručný `README.md` s lokálním spuštěním.
- Přidat alespoň základní smoke testy nebo jednoduché testovací scénáře.
- Doladit publikační vzhled mapy a případně Reel formát videa.

## První zpráva v novém Codex chatu

Přečti `AGENTS.md`, `PROJECT_CONTEXT.md`, `TODO.md` a `DECISIONS.md`.
Zkontroluj aktuální stav projektu přes `git status`.
Nepředpokládej žádný kontext ze starého chatu.

Pokračuj úkolem:
[sem napiš konkrétní úkol]

## Závěrečná zpráva na konci pracovního chatu

Aktualizuj `PROJECT_CONTEXT.md`, `TODO.md` a `DECISIONS.md` podle toho, co se skutečně změnilo, aby šlo bezpečně navázat v novém chatu.
Potom ukaž `git status` a navrhni commit message.
