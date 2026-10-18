# Sources

Everything in this skill comes from Google's own pages and code, read on 2026-10-17 and 2026-10-18, plus W3C's WCAG 2.2
and MDN for web-platform facts. Each reference file names its sources; this file is the index. M3 changes every year (Expressive in May 2025, the layout system in May 2026): when a rule matters, check its page.

## m3.material.io (fetched headless; the site renders in the browser)

| Area | Pages |
|---|---|
| Overview | `/`, `/get-started`, `/develop`, `/develop/web`, `/develop/flutter`, `/blog/whats-new-at-io26`, `/blog/building-with-m3-expressive`, `/blog/material-is-compose-first`, `/blog/m3-expressive-motion-theming` |
| Color | `/styles/color/system/overview`, `/styles/color/roles`, `/styles/color/choosing-a-scheme`, `/styles/color/static/baseline`, `/styles/color/static/custom-brand`, `/styles/color/dynamic/*`, `/styles/color/advanced/*`, `/styles/color/system/how-the-system-works`, `/foundations/customization`, `/foundations/design-tokens/*` |
| Type | `/styles/typography/overview`, `/styles/typography/fonts`, `/styles/typography/type-scale-tokens`, `/styles/typography/applying-type`, `/styles/typography/editorial-treatments` |
| Shape | `/styles/shape/overview-principles`, `/styles/shape/corner-radius-scale`, `/styles/shape/shape-morph` |
| Elevation and states | `/styles/elevation/*`, `/foundations/interaction/states/*` |
| Icons | `/styles/icons/*` |
| Motion | `/styles/motion/overview`, `/styles/motion/easing-and-duration/*`, `/styles/motion/transitions/*` |
| Layout | `/foundations/layout/layout-overview/*`, `/foundations/layout/breakpoints/*`, `/foundations/layout/scaffold/*`, `/foundations/layout/canonical-examples/*`, `/foundations/layout/grids-spacing/*`, `/styles/spacing/*`, `/foundations/layout/bidirectionality-rtl` |
| Usability, writing, content | `/foundations/usability/applying-m3-expressive`, `/foundations/designing/*`, `/foundations/writing/*`, `/foundations/content-design/*` |
| Accessibility | `/foundations/overview/*`, `/foundations/designing/color-contrast`, `/foundations/designing/structure`, `/foundations/designing/flow`, component `/accessibility` tabs |
| Components | `/components` and each component's `/overview`, `/guidelines`, `/specs`, `/accessibility` |

## Google's token files (in `tests/fixtures/google/`, with `manifest.json`)

| Folder | Repository and path | Commit (date) | What it gives |
|---|---|---|---|
| `flutter/` | flutter/flutter `dev/tools/gen_defaults/data` | 182c266961f8 (2024-09-04) | the baseline token database v6.1.0: color role mapping, type scale, shape, elevation, state, components |
| `compose/` | androidx/androidx `compose/material3/.../tokens` | 160825094a81 (2026-08-05) | Expressive corner steps, spring tokens, Expressive component sizes (button sizes, FABs, rails, app bars, toolbars) |
| `web/` | material-components/material-web `tokens/versions/v0_192` | 60c0cfa58ad1 (2025-10-07) | the `md-sys-*` names for CSS, easing and duration tokens |
| `web-latest/` | material-components/material-web `tokens/versions/latest/sass` | 763a97326fc2 (2026-04-06), Version 34.0.21 | emphasized type styles, the focus indicator, contrast-level color sets |

## Code and docs

- Color: `@material/material-color-utilities` 0.4.0 (npm, in `scripts/node_modules`); github.com/material-foundation/material-color-utilities (main has a 2026 spec and a CMF variant that npm lacks).
- Accessibility engine: `axe-core` 4.14.0 (Deque, npm).
- Flutter: the local SDK 3.44.1 (`/opt/homebrew/share/flutter`, read only); docs.flutter.dev (Material 3 migration, breaking changes, material_ui); api.flutter.dev (`ColorScheme.fromSeed`, `DynamicSchemeVariant`, `SpringDescription`); pub.dev `material_ui` 1.7.0.
- Compose: developer.android.com (Material 3 reference, adaptive layouts, window size classes); androidx release notes (material3 1.5.0-beta01, 2026-10-07).
- Material Web: github.com/material-components/material-web (README, docs/theming, docs/components, roadmap, releases v2.5.0).
- Icons: github.com/google/material-design-icons; fonts.google.com/icons.
- Android: developer.android.com/about/versions/16/behavior-changes-16 (orientation and resizability ignored at
  600 dp and wider for apps targeting API 36; read 2026-10-18).
- Flutter's engine and framework source in the local SDK: `engine/src/flutter/shell/platform/darwin/ios/framework/Source/AccessibilityFeatures.swift`
  (iOS Reduce Motion sets only `reduceMotion`), `material/app_bar.dart` (the scrolled app bar's tint),
  `material/tooltip.dart` (Material 2 tooltip defaults), `flutter_test/lib/src/accessibility.dart` (the guidelines).
- Compose source: androidx `compose/material3/.../ProgressIndicator.kt` (`ProgressAnimationSpec`, read 2026-10-18).
- WCAG 2.2: w3.org/TR/WCAG22 and its Understanding documents.
- MDN: CSS `linear()` easing, `prefers-reduced-motion`, browser support.

## Refreshing

1. `python3 tools/fetch_tokens.py` — re-download the token files; `manifest.json` records the commits.
2. `python3 tools/fetch_page.py --out <notes-folder>/<topic> <url>…` — re-read pages headless (keep the notes outside
   the skill).
3. Update the reference file from the notes, then run `python3 tests/run_all.py`.
4. If Flutter changes, `python3 tests/run_all.py --refresh-flutter` re-runs Flutter's own `fromSeed` for check 2.
