# material-3 skill

A Claude Code skill that designs and audits interfaces the Material 3 way, brand first. Decisions: `DECISIONS.md`.
Installed by a link: `~/.claude/skills/material-3` points to this folder (see README).

## Commands

- All checks: `python3 tests/run_all.py` (from this folder).
- Node dependencies: `npm --prefix scripts ci` (the color library and axe-core, pinned in `scripts/package-lock.json`).

## Rules

- Values come from Google's code and token files (`tests/fixtures/google/`, `scripts/tokens.mjs`), never from memory.
- Reference files are written in our own words from the official pages; every file names its sources and the date.
- When M3 changes, refresh `references/sources.md` first (`tools/fetch_page.py`), then the files that cite it.
- Site visits are headless (Playwright with real Chrome).
- Test fixtures are invented (`tests/fixtures/sample-app/`, `tests/fixtures/audit/`): never copy a real project's code,
  brand or screenshots into this repository.
