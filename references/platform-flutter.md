# M3 in Flutter

Checked 2026-10-18 against Flutter 3.44.1 (the local SDK, read only), docs.flutter.dev, api.flutter.dev and pub.dev.
Sources: `sources.md`.

## Where Material lives

- **`package:flutter/material.dart` (3.44 and earlier):** M3 by default since 3.16 (`useMaterial3: true`); the widgets
  follow the baseline token set v6.1; no M3 Expressive. Contributions to it were frozen in 3.44.
- **`package:material_ui` (Flutter 3.47 and later):** Material moved into its own package (1.7.0, October 2026). Expressive
  is "under development": a `StyleVariant { material3, material3Expressive }` and an Expressive `IconButton`
  (sizes, widths, round or square) so far; contrast-level baselines through `ThemeData(contrastLevel:)`.
  Switching: be on Flutter 3.47+, run `dart fix --apply --code=migrate_design_widgets`, change imports to
  `package:material_ui/material_ui.dart`.
- The M3 site's Flutter page is out of date ("opt in with useMaterial3", "Expressive not available").

Check which one a project imports before generating a theme; `m3_tokens.dart` targets `package:flutter/material.dart`.

## The theme the skill writes

`node <skill>/scripts/tokens.mjs <config> --out <dir>` writes `m3_tokens.dart`:

- `M3Tokens.lightScheme` / `darkScheme`: `ColorScheme` with all 46 current roles (the three deprecated ones,
  `background`, `onBackground` and `surfaceVariant`, are left out), brand-locked values exact.
- `M3Tokens.textTheme`: the 15 roles (`displayLarge` … `labelSmall`) with the brand and plain faces, sizes, heights
  (line height ÷ size), letter spacing and weights; the emphasized styles as `M3Tokens.emphasized<Role>` constants.
- Corner constants; every spring as a `SpringDescription.withDampingRatio(mass: 1, ...)`.
- `M3Tokens.theme(scheme)`: `ThemeData(useMaterial3: true, colorScheme, textTheme)`; an app bar theme with
  `surfaceTintColor: Colors.transparent` (Flutter still tints a scrolled app bar with `surfaceTint`, a tint M3 retired:
  the bar turns surfaceContainer only); a tooltip theme on inverse-surface with body-small (Flutter still draws Material
  2 tooltips, 90% white in a dark theme); component themes that carry overridden corner steps when the config changes
  M3's shapes. It needs Flutter 3.35 or later (`AppBarThemeData`).
- With `"type": { "variable": true }` every style also sets its `wght` axis (`fontVariations`), and the emphasized
  titles and labels take M3's variable weight 600 instead of 700.
- `surfaceTint` equals the final primary, a locked one included.

Why not `ColorScheme.fromSeed`? It is fine without a brand (the skill's colors equal Flutter's own `fromSeed` exactly for
every variant and contrast level, checked on 5,060 values), but it cannot keep an exact brand color in a role or prove
locked pairs. Flutter's `ThemeData(colorSchemeSeed:)` also cannot set a variant or contrast level; use
`ColorScheme.fromSeed(seedColor:, dynamicSchemeVariant:, contrastLevel:)` when no brand is locked. `fromSeed` runs the
2021 color spec (the Dart color library has no 2025 spec).

## ColorScheme facts

- Unset roles fall back to a related role: `primaryContainer` → `primary`, `onSurfaceVariant` → `onSurface`,
  `surfaceContainer` and `surfaceContainerHigh` → `surface`, fixed roles → their base. A hand-made `ColorScheme` with a
  few roles therefore collapses M3's hierarchy: dialogs (surface-container-high) and menus take the page's color. The
  Flutter audit reports it as Broken.
- `ColorScheme.highContrastLight/Dark` are Material 2; for M3 use `fromSeed(contrastLevel: 0.5 or 1.0)`.
- `DynamicSchemeVariant.expressive` is an old color variant, unrelated to "M3 Expressive".

## Widgets: M2 to M3

| Material 2 | Material 3 |
|---|---|
| `BottomNavigationBar` | `NavigationBar` |
| `Drawer` (as navigation) | `NavigationDrawer` (and in Expressive, an expanded rail) |
| `ToggleButtons` | `SegmentedButton` |
| `DropdownButton` | `DropdownMenu` |
| `PopupMenuButton` | `MenuAnchor` |
| `ButtonBar` (deprecated) | `OverflowBar` |
| one `Card` style | `Card`, `Card.filled`, `Card.outlined` |
| `IconButton` alone | plus `.filled`, `.filledTonal`, `.outlined` |
| `AppBar` | plus `SliverAppBar.medium` / `.large` |

`Slider`, `LinearProgressIndicator` and `CircularProgressIndicator` still default to `year2023: true` (the old look).
`year2023: false` opts into the December 2023 spec with the stop indicator, but the flag itself is deprecated since
3.27 (the analyzer reports `deprecated_member_use`): set it per widget where the new look matters and remove it when
Flutter flips the default, or style the parts through `SliderThemeData` and `ProgressIndicatorThemeData`.

## Expressive in Flutter today

No button groups, split button, FAB menu, loading indicator, toolbars, flexible app bars or flexible navigation bar in
`material.dart`. A design that needs them builds them from basic widgets on the tokens (shapes, springs, roles), or waits
for `material_ui`. Say which, per component.

## Platform defaults that matter

- Desktop platforms (macOS, Windows, Linux, and the web in a desktop browser) default to `VisualDensity.compact` and
  `MaterialTapTargetSize.shrinkWrap`: icon buttons 40×40 and buttons 32 high, below M3's 44 / 48. For touch-first apps
  on those platforms set `visualDensity: VisualDensity.standard` and `materialTapTargetSize: MaterialTapTargetSize.padded`.
- Keyboard focus shows only as a 10% overlay; add a visible focus decoration for keyboard users.
- `MediaQuery.highContrast` only updates on iOS.
- Reduced motion: read both `MediaQuery.disableAnimationsOf(context)` (Android) and
  `View.of(context).platformDispatcher.accessibilityFeatures.reduceMotion` (iOS; Flutter 3.44's engine sets only this
  flag for Reduce Motion). `AnimationController` shortens animations to 5% but does not turn slides into fades.
- Fonts: the bundled font files must cover every weight the type scale uses (400, 500, 700, or a variable file);
  a missing weight is faked or swapped for the nearest one. (A Flutter app bundling Inter 400 and 700 only renders
  M3's 500 styles wrong.)
- Orientation: on Android 16, apps targeting API 36 have orientation and resizability locks ignored on displays at
  least 600 dp wide; the opt-out property ends with API 37. Design every screen for M3's medium and expanded widths.

## Checking a running app

The code scan sees code; Flutter's own accessibility guidelines see the rendered widgets. Pump the app's real screens
with its real theme in a widget test and assert the guidelines, which measure tap targets, labels and text contrast:

```dart
final handle = tester.ensureSemantics();
await tester.pumpWidget(MaterialApp(theme: M3Tokens.theme(M3Tokens.lightScheme), home: const MyScreen()));
await expectLater(tester, meetsGuideline(androidTapTargetGuideline)); // 48 x 48 dp
await expectLater(tester, meetsGuideline(iOSTapTargetGuideline));     // 44 x 44 pt
await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
await expectLater(tester, meetsGuideline(textContrastGuideline));
handle.dispose();
```

Screens with a looping animation never settle; pump a fixed duration instead of `pumpAndSettle`.

## The Flutter audit

`python3 <skill>/scripts/audit_flutter.py <project> --out <dir>` scans the Dart code (comments and strings removed):
`useMaterial3: false`, ColorScheme coverage and the unset surface ladder, the M2 widgets above, literal colors and font
sizes in widget code, corner radii, shrunk tap targets, icon buttons without a tooltip, looping animations with no
reduced-motion check in their file, reading `disableAnimations` without iOS's `reduceMotion`, and orientation locks
(`setPreferredOrientations`, `android:screenOrientation`). It sees code, not pixels: pair it
with screenshots of the running app (iOS Simulator or Android emulator) for contrast and layout.
