# Shape

Checked 2026-10-18: m3.material.io shape pages; Compose and Material Web latest token files. Sources: `sources.md`.

## The corner scale

Ten steps named by roundness (M2 had three named by component size).

| Step | Value | Since | Typical components |
|---|---|---|---|
| none | 0 | baseline | app bars, navigation bar and rail containers, list items, tabs, docked toolbar, full-screen dialog |
| extra-small | 4 | baseline | menus, outlined text field, plain tooltip, snackbar; filled text field uses its top corners |
| small | 8 | baseline | chips; the pressed shape of XS and S buttons |
| medium | 12 | baseline | cards, rich tooltip; square XS and S buttons |
| large | 16 | baseline | FAB, extended FAB, docked date picker, modal expanded rail, navigation drawer's end corners |
| large-increased | 20 | Expressive | medium FAB and extended FAB |
| extra-large | 28 | baseline | dialogs, modal date picker, time picker, large FAB, carousel items, bottom sheet's top corners; square L and XL buttons |
| extra-large-increased | 32 | Expressive | no component yet |
| extra-extra-large | 48 | Expressive | no component yet |
| full | fully round | baseline (own value since Expressive) | buttons, icon buttons, badges, search bar, slider, switch, active indicators, floating toolbar, chips when selected (Compose 2026) |

On the web, full is `9999px`. Partial tokens exist for one side (`extra-small.top`, `large.start`, `large.end`,
`extra-large.top`).

## Rules

- Stay on M3's steps in general; customizing is allowed, even encouraged, for hero moments and custom components.
- Two ways to customize: change a step's value (every component on that step follows) or move one component to
  another step. Changing medium changes cards and square small buttons together.
- By default buttons are full; remap them to small or medium for a less round product. That is a brand choice (record
  it as a departure from M3).
- Don't put large or full corners on information-dense components such as cards.
- Nested shapes: inner radius = outer radius − padding (48 − 14 = 34 dp). Never reuse the outer radius inside.
- Rounded or cut corners; cut corners clip more and need more padding (Material Web supports only rounded).
- State changes shape (Expressive): pressed buttons shrink to a smaller step; selected toggle buttons swap round and
  square.

## Shape library and morph (M3 Expressive, 2025)

- 35 shapes: Circle, Square, Slanted, Arch, Fan, Arrow, SemiCircle, Oval, Pill, Triangle, Diamond, ClamShell, Pentagon,
  Gem, Sunny, VerySunny, Cookie4Sided, Cookie6Sided, Cookie7Sided, Cookie9Sided, Cookie12Sided, Ghostish, Clover4Leaf,
  Clover8Leaf, Burst, SoftBurst, Boom, SoftBoom, Flower, Puffy, PuffyDiamond, PixelCircle, PixelTriangle, Bun, Heart.
- They live in the Figma kit and Jetpack Compose (`MaterialShapes`, still experimental); there is no web or Flutter
  version. On the web, draw them as SVG clip paths or masks from the Figma kit's geometry; never invent look-alikes and
  call them M3's.
- Use them mainly on visual elements: image crops, avatar masks, decorative areas. Avoid them on text-heavy containers;
  use sparingly; smaller shapes can make an essential action look less important.
- Shapes carry no fixed meaning (a wave is not "progress").
- Morph links shape to function: states (selection), work in progress (typing, loading), surroundings (sound, time).
  Material uses it in the standard button group and the loading indicator. It runs on the expressive motion scheme by
  default; reduced motion turns it off.
- Tension: mixing square and round directs attention; let one element break the surrounding shape style to pull the eye.

## The tokens

CSS: `--md-sys-shape-corner-<step>` (none, extra-small, small, medium, large, large-increased, extra-large,
extra-large-increased, extra-extra-large, full). Flutter: `M3Tokens.corner<Step>` constants in `m3_tokens.dart`; when the
config overrides steps, `M3Tokens.theme()` carries them into the button, card, dialog, FAB, input, chip, snackbar and
bottom-sheet themes. In the config: `"shape": { "medium": 2 }` (each override is a departure, listed in the report).
