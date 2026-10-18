# The audit path: measure a design against M3

Two lists, always:

- **Broken** — faults whatever the brand: text and icon contrast, target size, keyboard focus that cannot be seen, a
  missing hover state, a scale that disagrees with itself (many radii or font sizes with no system), sideways scroll on
  a phone, movement that ignores reduced motion, a video that plays by itself with no pause (WCAG 2.2.2), WCAG
  violations (axe-core), and in Flutter: Material 3 switched off, the surface ladder left unset, shrunk tap targets,
  unlabelled icon buttons, looping animations without a reduced-motion check, iOS's Reduce Motion left unread, screen
  orientation locks that Android 16 ignores on large screens.
- **Differs from M3** — style choices: the typeface, values off M3's type or corner scale, button shape, spacing off
  the 4 dp grid, Material 2 widgets M3 replaced, color roles left to fallbacks. Short, separate, never a fault by itself.
  Values Google's own components use (a medium FAB's 20 px corners and 26 px sides, a list item's 10 px) are not listed.
- **Not measured** — what a script could not judge (an area that moves by itself, focus that left the window). Look at
  each by hand and say so; never drop it silently.

A value off M3's scale but used consistently (one 2 px corner everywhere) is a difference, not a fault. A departure the
project has already decided is marked as decided.

## 1. What is being audited

| Input | Run |
|---|---|
| A live URL or a local HTML file | `python3 <skill>/scripts/audit_web.py <url-or-file> --out <dir>` |
| A prototype screen | the same, with `?frame=full#<screen>` after the file path (see `prototype.md`) |
| Flutter code | `python3 <skill>/scripts/audit_flutter.py <project-or-lib> --out <dir>` |
| A screenshot or a design image | `python3 <skill>/scripts/audit_image.py <picture> <spec.json> --out <dir>` (section 4) |
| A running Flutter app | the code scan, screenshots from the simulator through `audit_image.py`, and Flutter's own accessibility guidelines in a widget test (`platform-flutter.md`) |

Options for the web audit: `--sizes 390x844,1440x900` (the defaults: a compact phone and a desktop), `--ignore <css>`
for parts that are not the design (a cookie banner, a debug bar), `--decided <json>` for departures the project has
approved, as `{"rule": "why"}`, for example `{"radius-off-scale": "2 px corners, DECISIONS 2026-10-18"}`.

Run audits at `nice -n 20` when the user is working on the same machine: each opens real Chrome several times.

## 2. What the web audit measures

First the page is brought to a still state: scrolled through once (lazy images and reveal-on-scroll content load),
smooth scrolling off, finished animations completed, looping animations and videos paused, nothing focused. With a
modal dialog open, only the dialog is measured: the page behind the scrim cannot be used.

- **Contrast** of every visible text and icon against what is painted under it (pseudo-element containers and layers
  with `pointer-events: none` included). Where CSS cannot tell (a picture, a gradient, a video), the page is
  photographed with its text hidden and the lowest ratio against the main colors behind the text counts; over a video,
  across five of its frames. Those are marked as estimates. Text 4.5:1, large text (24 px, or 18.66 px bold) and icons
  3:1. Disabled controls are exempt.
- **Targets:** each control's real hit area (its box, its children, its label; a visually hidden input is used through
  its label). A focusable container (a tab panel) is not a target. Under 24×24 px fails WCAG 2.5.8 unless the spacing
  exception holds; under 48×48 on a phone width misses M3's touch target.
- **Focus:** each focusable element reached by the keyboard, photographed focused and then blurred at the same scroll
  position; at least half its outline (or 1% of the area) must change. Fixed bars are measured where they stand.
- **Hover** (desktop widths): button-like controls must change on hover; a control covered by another element, or an
  area that moves by itself, goes to Not measured.
- **Sideways scroll** on a phone width.
- **Reduced motion:** with `prefers-reduced-motion: reduce`, no long or infinite movement and no looping video may keep
  running.
- **Videos:** one that plays by itself and loops or runs over 5 seconds needs a pause control (WCAG 2.2.2).
- **Scales:** distinct font sizes and corner radii; more than 10 sizes or 6 radii is Broken; values off M3's scales
  go to Differs; spacing values off the 4 dp grid go to Differs.
- **axe-core** with the WCAG 2.2 A and AA rules; its contrast numbers are cross-checked against the audit's own.

Out: `findings.md`, `findings.json` and `audit-<w>x<h>.png` with a numbered marker at each finding (red for Broken,
orange for Differs); markers on one element step aside instead of hiding each other.

## 3. The design reading (yours, on top of the numbers)

The scripts measure; they do not judge design. Read the screens against `screen-design.md` and `components.md` and add
findings in the same two lists:

- **Layout:** does the layout fit the breakpoint (one pane on compact, list-detail from expanded)? Do lines stay near
  40–60 characters?
- **Navigation:** the right component for the width and the number of destinations; never a bar and a rail together; a
  navigation bar on desktop is a Differs (M3 says rail or tabs).
- **Emphasis:** one primary action; one FAB at most; no more than three buttons in a group; two dialog actions.
- **Component choice:** each component used for its purpose (a switch that needs Save, a dialog for a low-priority
  message, a segmented button for filtering).
- **Hierarchy and states:** type roles used consistently; selected, error, empty and loading states present.
- **Version:** components M3 Expressive retired (navigation drawer, segmented button, baseline bars, small FAB) go to
  Differs with their replacements.

Broken here means the design misleads or blocks people whatever the brand (no visible primary action, two competing
FABs, a destructive action in a snackbar); everything stylistic goes to Differs.

## 4. Auditing an image only

Without a page there is nothing to measure in a browser. Say it is an estimate.

1. Read the picture yourself for layout, navigation, emphasis and components, and find its scale (a 780 px wide phone
   screenshot of a 390 px viewport is 2x).
2. Write a spec: every text and icon worth checking, every tappable area, and your design findings as notes, each with
   a box in image pixels (the format is in the script's header). Small text near a busy background first.
3. Run `audit_image.py`. Text and icons are measured stripe by stripe (glyph cores against the background behind each
   part), targets in CSS px or dp; the numbered picture carries the measured findings and your notes together.
4. Accuracy: on known pairs a 2x picture measures exactly; at 1x small text reads up to 12% low, never high. Ask for a
   2x or 3x picture when a ratio is borderline.

## 5. Showing the result

- The numbered screenshot first, then Broken (most severe first), then Differs (short), then what was not checked.
- Each finding: what, where (the element and the size), why (the M3 or WCAG rule), the fix.
- In the user's language; English rule names may stay.
- Do not fix anything until the user says yes. Then fix the Broken items first and audit again.
- A report for a client is copy: route it through the project's copy process.
