# The build path: from a request to a clickable prototype

The design work is the core of this path. Tokens are the engine underneath; the user judges screens, not swatches.

## 1. Read first

- The project's CLAUDE.md (or AGENTS.md), its brand book, its decisions file, and approved pictures or prototypes.
- Note every locked brand value (colors, typefaces, corner rules, motion rules) and every departure already decided.
- An answer already given is never asked again; an approved look is the target, not a new question.
- If the project has its own design process (phases, gates), work inside it and say which step this is.

## 2. Interview, one question per message

Ask only what the reading did not answer, in this order, one question per message, each anchored in something concrete:

1. What is it, and who uses it where (phone in one hand, desktop at work, both)?
2. The key tasks, and the first 3–5 screens that carry them.
3. Platform: web, Flutter, or both (decides the hand-over format, not the design).
4. The brand: its locked values, or none (from zero).
5. The mood in three words (calm, energetic, serious...). This picks the scheme variant and motion scheme later.
6. Light, dark, or both.

When the user says "just decide", decide, and say each choice in one line so it can be overruled.

## 3. The screen plan (read `screen-design.md`)

Write it before any picture. For each screen:

- **Goal:** the primary task, then secondary ones; one primary task per screen.
- **Layout:** canonical layout (feed, list-detail, supporting pane) or single pane; what changes at each breakpoint.
- **Navigation:** which component at which width (navigation bar on compact, rail from medium up; never both).
- **Components:** each task's component and its emphasis (FAB, filled, tonal, outlined, text; chips vs segmented;
  dialog vs snackbar), and why, citing the M3 rule.
- **Hierarchy:** which type role each text takes; where the brand color may appear; the one hero moment, if any.
- **Flow:** how screens connect, and the transition pattern for each move (forward/backward, top level, enter/exit).

Keep it short: a table per screen. It is the brief for the pictures and the prototype.

## 4. Directions: whole screens, not swatches

Show 3–4 directions. Each is a real M3 combination, computed before it is drawn:

| Knob | Options (pick per direction) |
|---|---|
| Scheme variant | tonal spot (calm default), neutral, vibrant, expressive, fidelity or content (closest to the brand's color), monochrome, rainbow, fruit salad |
| Style | baseline M3, or M3 Expressive (emphasized type, more shape contrast, springier motion, new components) |
| Shape | the default corner scale, or a brand override (for example all small corners) |
| Type | the brand's typefaces on the M3 scale; emphasized styles for the hero lines |
| Motion | standard (calm, functional) or expressive (bouncy) |
| Density | default; a denser layout only for data-heavy tools |

For each direction:

1. Write a config and run `node <skill>/scripts/tokens.mjs <config> --out <dir>`; read `report.md` (contrast, locked
   values, adjustments).
2. Draw one picture of the key screen with the user's image route (a `ui-mockups` or `image-generation` skill, when
   installed; otherwise one HTML screen from the template): the screen plan's layout and components, the exact hex
   values from `tokens.json`, the real UI text from the project's copy or its copy process, the type roles by size.
3. Show each direction as one image with one sentence, then one question: which one, or which parts of which.

Generated images get counted things, small text and exact icons wrong; never take a number or glyph from them.

## 5. The clickable prototype (read `prototype.md`)

The chosen direction becomes HTML from the template: 3–5 key screens, phone and desktop, light and dark, every state the
screen plan names (pressed, selected, error, empty, loading), M3's transitions, the reduced-motion version. Audit every
screen (`audit_web.py`); fix every Broken finding the design caused; then publish it as an artifact and give the user the
link to open on a phone.

## 6. Hand-over

- `tokens.json`, `tokens.css` (the `--md-sys-*` custom properties), `m3_tokens.dart` (Flutter), `report.md`.
- The screen plan with its M3 reasons.
- The departures from the brand book, each as a question for the owner (M3's way vs the book's way, with a picture).
- What M3 did not decide (the scope boundary) and what was not checked.

## 7. Closing check

Run the audit on the final prototype at 390×844 and 1440×900. Done means zero Broken findings, except brand-locked values
listed for the owner. Report the numbers, not an impression.
