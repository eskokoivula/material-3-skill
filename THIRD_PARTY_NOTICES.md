# Third-party notices

The skill's own code and text are under the MIT License (`LICENSE`). The parts below come from others and keep their
own licenses.

## Google's Material 3 token files (`tests/fixtures/google/`)

The skill reads M3's values from Google's own generated token files, copied unchanged at the commits recorded in
`tests/fixtures/google/manifest.json`. The scripts read them at run time, so they ship with the skill.

| Folder | Source | License |
|---|---|---|
| `flutter/` | flutter/flutter, `dev/tools/gen_defaults/data`, commit 182c266 | BSD-3-Clause, Copyright 2014 The Flutter Authors (`tests/fixtures/google/LICENSES/flutter-BSD-3-Clause.txt`) |
| `compose/` | androidx/androidx, `compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens`, commit 1608250 | Apache-2.0, Copyright The Android Open Source Project (`tests/fixtures/google/LICENSES/androidx-Apache-2.0.txt`) |
| `web/`, `web-latest/` | material-components/material-web, `tokens/versions/v0_192` (commit 60c0cfa) and `tokens/versions/latest/sass` (commit 763a973) | Apache-2.0, Copyright Google LLC (`tests/fixtures/google/LICENSES/material-web-Apache-2.0.txt`) |

## Installed at setup, not included here

- `@material/material-color-utilities` 0.4.0 (Apache-2.0, Google) and `axe-core` 4.14.0 (MPL-2.0, Deque Systems),
  installed by `npm --prefix scripts ci`.
- Playwright for Python (Apache-2.0, Microsoft) and the browsers it drives.
- Material Symbols, loaded by the prototype template from Google Fonts (Apache-2.0).

## Names

"Material Design" and "Material 3" are Google's names for its design system. This project is independent: it is not
made, endorsed or supported by Google.
