# Sample app (invented test fixture)

A small, invented Flutter app and its brand colors. It is never built; checks 3, 7 and 9 read it.

- `lib/`: the Flutter scan's input (check 7). What the scan must report: 9 of the 49 color roles set and the surface
  container ladder left unset; one `BottomNavigationBar` use at `lib/widgets/bottom_nav.dart:23` (the doc comment and
  the string that name it are not uses); two looping animations with no reduced-motion check
  (`lib/widgets/pulse_ring.dart:17`, `lib/screens/hint_screen.dart:20`), while `reward_screen.dart` checks the setting;
  reduced motion read only from `disableAnimations`; portrait locked in two places (`lib/main.dart:10`,
  `lib/screens/hint_screen.dart:18`), while `DeviceOrientation.values` unlocks and is not a lock; of four icon buttons
  in `lib/widgets/actions.dart` only line 16's, with no tooltip, Semantics label or icon semanticLabel, is unlabelled.
- `brand.tokens.json`: the brand's token config (checks 3 and 9): dark only, 12 locked colors, among them a
  translucent outline and a muted text color, so some locked pairs fail and must come back with a nearest passing tone.
