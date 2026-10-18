---
name: material-3
description: Design and audit interfaces the Google Material 3 (M3) way, brand first. Runs a design pipeline from a short interview to an M3 screen plan, whole-screen design directions and a clickable prototype; builds M3 tokens for the web (CSS) and Flutter (ThemeData) from Google's own color library and token files; audits any web page, screenshot or Flutter code into two lists, "Broken" and "Differs from M3", with a numbered picture. Use it whenever the user mentions Material 3, M3, Material Design, Material You, M3 Expressive, "Google Design", "Google Design Themes", "Google Design Audit", "M3 audit", asks for a design "in Google's style" or "like Google's apps", wants a UI checked against Material, or a project's CLAUDE.md points to this skill. Not for UI work that names none of these.
---

# Material 3, brand first

M3 is Google's design system for product interfaces: the rules, scales and components Google builds Android and its own
apps with. This skill gives a project M3's system — color roles, type scale, shape, spacing, states, motion,
accessibility, components, layout by window size — while the project's own brand keeps its look. It does two jobs:
**build** (design screens the M3 way and hand over a clickable prototype and tokens) and **audit** (measure an existing
design against M3 and WCAG).

Think of it as M3's engine under the brand's paint: the system decides how things work and relate; the brand decides how
they look. A prototype that merely looks like a Google app is a failure even if every rule passes.

## Start here: one question

Unless the request already answers it, ask one thing first:

> Audit something that exists, or build something?

Then, for a build: on an existing brand (read its brand book first) or from zero. Load only the file the path needs.

| The user wants | Read now | Read when you reach it |
|---|---|---|
| A design, screens, a prototype | `references/pipeline-build.md` | `screen-design.md`, `brand-first.md`, `prototype.md` |
| An audit of a page, an image or Flutter code | `references/pipeline-audit.md` | the topic file behind each finding |
| M3 tokens or a theme only | `references/brand-first.md` | `platform-web.md` or `platform-flutter.md` |
| A question about M3 | the topic file below | `sources.md` for links |

A question gets a short, direct answer from the topic file, whole but brief (a ladder or a list keeps every step), with
its source. No interview and no audit offer unless the user asks for one.

## Where M3 stops

Read `references/scope.md` before designing anything that is not an app. In short: apps and web apps are M3's home and
the skill designs them whole. On a website the skill designs the interface layer — navigation, buttons, forms, cards,
type scale, color roles, spacing, states, accessibility, interface motion, icons — and M3 Expressive's type moments. A
page's story, hero, pictures, film, illustration, logo and brand identity are not M3's; say so plainly and leave them to
the project's creative direction. Never invent "M3 rules" for them.

## Hard rules

1. **Values come from the scripts, never from memory.** Colors from `scripts/tokens.mjs` (Google's color library);
   type, shape, elevation, state and motion from Google's token files in `tests/fixtures/google/`. M3 changes every
   year; memory is out of date.
2. **Brand first.** A brand's locked values stay exact. Where an M3 signature meets a brand rule (a pill button, a corner
   radius, a typeface), show both and let the owner decide; record the answer where the project records decisions.
   Never assume M3 wins.
3. **Read before asking.** A project's CLAUDE.md, brand book, decisions file and approved pictures come first. An answer
   already given is never asked again. Interview one question per message.
4. **UI text is copy.** Labels, headings and messages in mockups and prototypes come from the project's approved copy
   or its copy process (a copywriting skill, when the user's setup has one). Any string you write yourself is a
   placeholder, marked as such on screen and listed in the hand-over.
5. **Directions are pictures, the final is HTML.** Directions go through the user's image route (a `ui-mockups` or
   `image-generation` skill, when installed) with exact hex values in the prompt; without an image tool, draw each
   direction as one HTML screen from the template. The chosen direction becomes a prototype from
   `templates/prototype/`.
6. **Evidence before showing.** Run the audit on every prototype screen; show nothing with a "Broken" finding left,
   unless it is a brand-locked value the owner must decide, listed as such.
7. **Headless browsers only.** Measure and screenshot with Playwright and real Chrome (the scripts do). Never drive the
   app's browser pane or the user's Chrome for this.
8. **No silent edits.** An audit reports; it fixes only after the user says yes. Write only into the project's files its
   own rules allow.
9. **Name the version.** When a rule depends on it, say whether it is baseline M3, M3 Expressive (2025) or the 2026
   layout update. Expressive retired several baseline components (see `components.md`).

## The scripts

The skill's base directory is where this file lives (installed as `~/.claude/skills/material-3`). If
`scripts/node_modules` is missing, run `npm --prefix <skill>/scripts install` once.

| Job | Command |
|---|---|
| Tokens (JSON, CSS, Dart, report) | `node <skill>/scripts/tokens.mjs <config.json> --out <dir>` |
| A prototype folder | `node <skill>/scripts/prototype.mjs <config.json> --out <dir> [--force]` |
| Audit a web page or file | `python3 <skill>/scripts/audit_web.py <url-or-file> --out <dir> [--sizes 390x844,1440x900] [--ignore <css>] [--decided <json>]` |
| Audit a picture (a screenshot or a design export) | `python3 <skill>/scripts/audit_image.py <picture> <spec.json> --out <dir>` |
| Audit Flutter code | `python3 <skill>/scripts/audit_flutter.py <project-or-lib> --out <dir>` |
| The skill's own checks | `python3 <skill>/tests/run_all.py` |

The config format is in `references/brand-first.md`. Heavy runs (audits, image generation) go at `nice -n 20` when the
user is working on the same machine.

## Reference files

| File | What it holds |
|---|---|
| `scope.md` | where M3 applies, where it stops, how to map a website |
| `pipeline-build.md` | the build path step by step: read, interview, screen plan, directions, prototype, hand-over |
| `screen-design.md` | designing a screen the M3 way: goals, canonical layouts, navigation, emphasis, Expressive tactics |
| `prototype.md` | building, checking and publishing the clickable prototype |
| `pipeline-audit.md` | the audit path: inputs, measurements, the two lists, the picture, the design reading |
| `brand-first.md` | the token config, mapping a brand onto roles, locked values, departures |
| `color.md` | color roles, schemes and variants, contrast levels, the 2025 spec, brand colors |
| `typography.md` | the type scale (15 roles, 15 emphasized), fonts, applying type, editorial moments |
| `shape.md` | the corner scale, shape morph, the 35-shape library |
| `surfaces-and-states.md` | elevation, tonal surfaces, state layers, focus |
| `layout.md` | breakpoints, panes, the scaffold, spacing tokens, margins, density, RTL |
| `motion.md` | motion schemes, springs, easing and duration, transition patterns, reduced motion |
| `components.md` | every component: when to use it, emphasis ladder, Expressive changes, platform availability |
| `accessibility.md` | M3's accessibility rules and the WCAG 2.2 criteria behind the audit |
| `platform-web.md` | M3 on the web without Material Web: tokens as CSS, m3.css, linear() motion, icons |
| `platform-flutter.md` | M3 in Flutter 3.44 and the new `material_ui` package; the Dart theme |
| `sources.md` | every official source, the date checked, and how to refresh |

## Showing the work

- A decision goes to the user as one picture, one sentence and one question.
- A prototype is published as an artifact (the folder's files) so the user can open it on a phone; give the link.
- An audit is shown as the numbered screenshot plus the two lists, most severe first, in the user's language, and
  what the scripts list as not measured.
- Say what was not checked (a static Flutter scan sees code, not pixels; an image-only audit estimates contrast).
