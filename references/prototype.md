# The clickable prototype

The final design artefact: real M3 components on the project's tokens, screens the user can click on a phone. It is
built from `templates/prototype/` and checked before anyone sees it.

## Make the folder

```bash
node <skill>/scripts/prototype.mjs <config.json> --out <project>/<prototype-dir>
```

It writes `index.html` (the template's example screens, only when the folder has none), `tokens.css` (from the config),
`m3.css` (the components), `prototype.css` and `prototype.js` (the viewer and router) and `tokens-report.md`.
Re-running refreshes everything except `index.html`; `--force` replaces that too.

## Write the screens

Keep the viewer (stage, device, bar, script) and replace the example screens in `index.html`:

```html
<div id="app" class="md-window md-surface">
  <nav class="md-nav-rail md-from-medium" aria-label="Main">…rail items with data-nav…</nav>
  <div class="proto-main">
    <div class="screens">
      <section class="screen" data-screen="inbox" data-title="Inbox" data-section="inbox" aria-label="Inbox">…</section>
      <section class="screen" data-screen="thread" data-title="Thread" data-section="inbox" aria-label="Thread" hidden>…</section>
    </div>
    <nav class="md-nav-bar md-only-compact" aria-label="Main">…bar items with data-nav…</nav>
  </div>
  <div class="md-scrim" id="dialog-delete" hidden>…<div class="md-dialog" role="dialog" aria-modal="true">…</div></div>
  <div class="proto-snackbar-slot"><div class="md-snackbar" id="snack-sent" role="status" hidden>…</div></div>
</div>
```

- **Screen names:** `data-screen` only; never give a screen an `id` equal to its hash, or the browser focuses the
  whole screen and draws a ring around the page.
- **Moving between screens:** `<a href="#thread" data-transition="forward">`, or any element with `data-go="thread"`.
  The transition pattern is a design decision; use M3's:
  - `forward` / `backward` — down or up one level of hierarchy (list to detail and back).
  - `top-level` — switching navigation destinations (bar, rail).
  - `fade` — anything else small.
  The router runs them on M3's easing tokens (Emphasized, 450 ms, the fade split at 35%); under reduced motion every
  move becomes a short fade without movement.
- **Navigation that persists:** put `data-nav="<section>"` on bar and rail items; `data-section` on screens marks
  which item is current.
- **Dialogs and snackbars:** `data-open="<id>"` opens; `data-close` inside a dialog closes; Escape and a scrim tap close;
  focus moves into the dialog and back to the opener.
- **Window sizes:** the app is a container (`md-window`), so layout follows the frame, not the browser:
  `md-only-compact`, `md-from-medium` and `md-from-expanded` show and hide parts at 600 and 840 px;
  `md-list-detail` turns into two panes from 840 px. Add container queries of your own for anything else.
- **Components:** use the classes in `m3.css` (buttons in five styles and five Expressive sizes, icon buttons, FABs,
  cards, chips, text fields, switches, checkboxes, radios, segmented buttons, tabs, lists, menus, app bars, navigation
  bar and rail, drawer, search, toolbar, dialogs, sheets, snackbars, tooltips, badges, progress). Their sizes and roles
  come from Google's component tokens; read the top of `m3.css` for the touch-target rule.
- **Icons:** Material Symbols from Google Fonts in the template. On a privacy-minded production site, self-host a subset
  instead (`platform-web.md`).
- **Text:** real UI text from the project's copy. Placeholders only where the copy does not exist yet, marked as such.
  Sample content (names, listings, numbers) and accessible names (`aria-label`) count as text: mark sample content on
  screen ("Sample data") and list every placeholder in the hand-over.
- **States:** show each state the screen plan names (pressed, selected, error, empty, loading) somewhere a click away.

## Check it before showing it

1. Open each screen at a phone and a desktop size and look at it (headless screenshots are fine):
   `index.html?frame=full&theme=light#<screen>` and `?frame=desktop&theme=dark#<screen>`.
2. Audit every screen and fix every Broken finding the design caused:
   ```bash
   python3 <skill>/scripts/audit_web.py "<prototype>/index.html?frame=full&theme=light#<screen>" --out <dir>/audit-<screen>
   ```
   The viewer's control bar carries `data-audit-ignore`, so it is not measured. A file path may carry the query and
   the hash as above. Audit a dialog or sheet state by opening it first (a `?demo=` switch in the screen's script):
   with a modal open, the audit measures only the modal.
3. Click through every screen in Chrome and WebKit at 375×812 and 1440×900, as `tests/test_prototype.py` does for the
   template (it reaches every screen by clicking, checks sideways scroll, the theme switch, dialog focus and Escape, and
   that reduced motion removes movement). Copy its approach for a project's screens when the flow matters.

## Publish it

Publish the folder as an artifact so the user can open it on a phone: the page is `index.html`; `tokens.css`, `m3.css`,
`prototype.css` and `prototype.js` go in as the artifact's supporting files at the same relative paths. Load the
artifact-design guidance first if the host requires it. On a phone the prototype fills the screen (frame `full`) and the
viewer's controls sit below it.

URL parameters for direct links: `frame` (phone, tablet, desktop, full), `theme` (light, dark, system), `motion`
(normal, reduced), `chrome=0` (hide the controls), and the screen as the hash.
