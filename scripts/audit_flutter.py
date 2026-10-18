"""Static audit of a Flutter app's Material 3 use, in two lists like the web audit.

Broken: faults whatever the brand — Material 3 switched off, surface roles left unset (dialogs and menus then take
the page's own color), a type or corner scale that disagrees with itself, tap targets shrunk below 48 dp, icon
buttons without a tooltip (no accessible name), looping animations that ignore reduced motion (and iOS's Reduce
Motion, which Flutter does not fold into disableAnimations), screen orientation locks that Android 16 ignores on
large screens. Differs from M3: Material 2 widgets that M3 replaced, color roles left to Flutter's fallbacks,
literal colors in widget code, sizes and radii off M3's scales.
Comments and strings are removed before matching, so a widget named in a doc comment is not counted.

Usage: python3 scripts/audit_flutter.py <flutter-project-or-lib-dir> --out <dir>
Writes findings.json and findings.md. A static scan sees code, not pixels: pair it with screenshots of the
running app for contrast and layout.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
GOOGLE = SKILL / "tests" / "fixtures" / "google"
LEGACY = {"background", "onBackground", "surfaceVariant"}
DART_NAMES = {"inverseOnSurface": "onInverseSurface"}
# Flutter's own M2 -> M3 replacements (docs.flutter.dev, Material 3 migration guide).
REPLACED = {"BottomNavigationBar": "NavigationBar", "Drawer": "NavigationDrawer", "ToggleButtons": "SegmentedButton"}
SURFACE_LADDER = ["surfaceContainerLowest", "surfaceContainerLow", "surfaceContainer", "surfaceContainerHigh", "surfaceContainerHighest"]
GENERATED = re.compile(r"(\.g\.dart|\.freezed\.dart|\.mocks\.dart|/l10n/app_localizations[\w_]*\.dart)$")
ANIMATES = re.compile(r"\bAnimationController\b|\.animate\(")
LOOPS = re.compile(r"\.repeat\(")
# Android's Remove animations sets disableAnimations; iOS's Reduce Motion sets only accessibilityFeatures.reduceMotion
# (Flutter 3.44 engine, AccessibilityFeatures.swift), which MediaQueryData does not carry.
MOTION_AWARE = re.compile(r"disableAnimations|reduceMotion|accessibleNavigation")
LOCKS = re.compile(r"\bsetPreferredOrientations\s*\(")
LOCK_VALUES = re.compile(r'android:screenOrientation\s*=\s*"(portrait|reversePortrait|sensorPortrait|userPortrait|landscape|reverseLandscape|sensorLandscape|userLandscape)"')


def color_roles() -> list[str]:
    data = json.loads((GOOGLE / "flutter" / "color_light.json").read_text())
    camel = lambda s: re.sub(r"-([a-z])", lambda m: m.group(1).upper(), s)
    roles = [camel(k[len("md.sys.color."):]) for k in data if k.startswith("md.sys.color.")]
    return [DART_NAMES.get(r, r) for r in roles]


def m3_type_sizes() -> set[float]:
    data = json.loads((GOOGLE / "flutter" / "text_style.json").read_text())
    return {float(v) for k, v in data.items() if k.endswith(".size")}


def m3_corners() -> set[float]:
    src = (GOOGLE / "compose" / "ShapeTokens.kt").read_text()
    return {float(v) for v in re.findall(r"val CornerValue\w+ = CornerSize\(([\d.]+)\.dp\)", src)}


def strip_dart(src: str) -> str:
    """Blank out comments and string literals, keeping line breaks so line numbers stay right."""
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif src.startswith("/*", i):
            depth, j = 1, i + 2
            while j < n and depth:
                if src.startswith("/*", j):
                    depth, j = depth + 1, j + 2
                elif src.startswith("*/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            out.append(re.sub(r"[^\n]", " ", src[i:j]))
            i = j
        elif c in "'\"" or (c in "rR" and i + 1 < n and src[i + 1] in "'\"" and (i == 0 or not (src[i - 1].isalnum() or src[i - 1] == "_"))):
            raw = c in "rR"
            q0 = i + 1 if raw else i
            quote = src[q0]
            triple = src.startswith(quote * 3, q0)
            end = quote * 3 if triple else quote
            j = q0 + (3 if triple else 1)
            while j < n:
                if not raw and src[j] == "\\":
                    j += 2
                    continue
                if src.startswith(end, j):
                    j += len(end)
                    break
                if not triple and src[j] == "\n":
                    break
                j += 1
            out.append(re.sub(r"[^\n]", " ", src[i:j]))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def call_args(code: str, open_paren: int) -> str:
    """The text between a call's parentheses."""
    depth, j = 0, open_paren
    while j < len(code):
        if code[j] in "([{":
            depth += 1
        elif code[j] in ")]}":
            depth -= 1
            if depth == 0:
                return code[open_paren + 1:j]
        j += 1
    return code[open_paren + 1:]


def named_args(args: str) -> list[str]:
    names, depth = [], 0
    for m in re.finditer(r"[()\[\]{}]|\b([A-Za-z_]\w*)\s*:(?!:)", args):
        tok = m.group(0)
        if tok in "([{":
            depth += 1
        elif tok in ")]}":
            depth -= 1
        elif depth == 0 and m.group(1):
            names.append(m.group(1))
    return names


def line_of(code: str, pos: int) -> int:
    return code.count("\n", 0, pos) + 1


def finding(rule, lst, severity, what, where, why, fix, data=None):
    return {"rule": rule, "list": lst, "severity": severity, "what": what, "where": where, "why": why, "fix": fix, "data": data or {}}


def scan(root: Path) -> tuple[list[dict], dict]:
    lib = root / "lib" if (root / "lib").is_dir() else root
    files = sorted(p for p in lib.rglob("*.dart") if not GENERATED.search(p.as_posix()))
    roles = color_roles()
    flutter_roles = [r for r in roles if r not in LEGACY]
    found, schemes, replaced, literals, sizes, radii, shrink, bare_icons, m2_off = [], [], {}, [], {}, {}, [], [], []
    loops, locks, reads_disable, reads_reduce = [], [], False, False
    for f in files:
        rel = f.relative_to(lib.parent).as_posix()
        code = strip_dart(f.read_text(errors="replace"))
        themeish = bool(re.search(r"(theme|token|color|palette)", f.name, re.I))
        for m in re.finditer(r"\bColorScheme(?:\.(light|dark|fromSeed|fromImageProvider|highContrastLight|highContrastDark))?\s*\(", code):
            args = named_args(call_args(code, m.end() - 1))
            schemes.append({"where": f"{rel}:{line_of(code, m.start())}", "kind": m.group(1) or "ColorScheme",
                            "roles": [a for a in args if a in roles or a in flutter_roles]})
        for m in re.finditer(r"\b(" + "|".join(REPLACED) + r")\s*\(", code):
            replaced.setdefault(m.group(1), []).append(f"{rel}:{line_of(code, m.start())}")
        if re.search(r"useMaterial3\s*:\s*false", code):
            m2_off.append(rel)
        if not themeish:
            for m in re.finditer(r"\bColor\(\s*0x[0-9A-Fa-f]{6,8}\s*\)|\bColor\.fromARGB\(|\bColors\.(?!transparent\b)\w+", code):
                literals.append(f"{rel}:{line_of(code, m.start())}")
            for m in re.finditer(r"\bfontSize\s*:\s*([\d.]+)", code):
                sizes.setdefault(float(m.group(1)), []).append(f"{rel}:{line_of(code, m.start())}")
        for m in re.finditer(r"\b(?:BorderRadius|Radius)\.circular\(\s*([\d.]+)\s*\)", code):
            r = float(m.group(1))
            if r < 100:  # 999 and the like are the "fully round" idiom, M3's full step
                radii.setdefault(r, []).append(f"{rel}:{line_of(code, m.start())}")
        for m in re.finditer(r"MaterialTapTargetSize\.shrinkWrap|VisualDensity\.compact\b", code):
            shrink.append(f"{rel}:{line_of(code, m.start())}")
        # A Semantics(label:) or Tooltip(message:) around an icon button names it too.
        named = []
        for m in re.finditer(r"\b(Semantics|Tooltip)\s*\(", code):
            args = call_args(code, m.end() - 1)
            if ("label" if m.group(1) == "Semantics" else "message") in named_args(args):
                named.append((m.end(), m.end() + len(args)))
        for m in re.finditer(r"\bIconButton(?:\.(?:filled|filledTonal|outlined))?\s*\(", code):
            args = call_args(code, m.end() - 1)
            # Named by its tooltip, by a semanticLabel on its icon, or by a Semantics or Tooltip around it.
            if "tooltip" in named_args(args) or re.search(r"\bsemanticLabel\s*:", args) or any(a <= m.start() < b for a, b in named):
                continue
            bare_icons.append(f"{rel}:{line_of(code, m.start())}")
        reads_disable |= "disableAnimations" in code
        reads_reduce |= "reduceMotion" in code
        if ANIMATES.search(code) and not MOTION_AWARE.search(code):
            loops += [f"{rel}:{line_of(code, m.start())}" for m in LOOPS.finditer(code)]
        for m in LOCKS.finditer(code):
            values = set(re.findall(r"DeviceOrientation\.(\w+)", call_args(code, m.end() - 1)))
            if "values" in values:  # DeviceOrientation.values: every orientation, an unlock
                continue
            if values and not ({"portraitUp", "portraitDown"} & values and {"landscapeLeft", "landscapeRight"} & values):
                locks.append(f"{rel}:{line_of(code, m.start())}")
    manifest = root / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
    if manifest.is_file():
        src = manifest.read_text(errors="replace")
        locks += [f"{manifest.relative_to(root).as_posix()}:{line_of(src, m.start())}" for m in LOCK_VALUES.finditer(src)]

    if m2_off:
        found.append(finding("m3-off", "broken", "major", "Material 3 is switched off (useMaterial3: false)", ", ".join(m2_off),
                             "Flutter's Material 2 path is deprecated and will be removed; none of M3's components apply.",
                             "Remove useMaterial3: false and migrate the theme."))
    explicit = [s for s in schemes if s["kind"] in ("ColorScheme", "light", "dark")]
    for s in explicit:
        missing = [r for r in flutter_roles if r not in s["roles"]]
        ladder_missing = [r for r in SURFACE_LADDER if r not in s["roles"]]
        if ladder_missing and "surface" in s["roles"]:
            found.append(finding(
                "surface-roles-unset", "broken", "major",
                f"{len(ladder_missing)} of 5 surface container roles unset: they fall back to surface",
                s["where"], "Flutter's ColorScheme returns surface for an unset container role, so dialogs "
                "(surfaceContainerHigh), menus and navigation bars (surfaceContainer) take the page's own color and lose their edge.",
                "Set the whole surface ladder from the brand's neutral (scripts/tokens.mjs does it), or use ColorScheme.fromSeed with overrides.",
                {"missing": ladder_missing}))
        if missing:
            found.append(finding(
                "roles-unset", "differs", "minor",
                f"{len(s['roles'])} of {len(flutter_roles)} color roles set ({len(s['roles'])} of {len(roles)} in Google's list)",
                s["where"], "Unset roles fall back to a related role (primaryContainer to primary, onSurfaceVariant to onSurface), "
                "so M3's tonal hierarchy collapses.", "Generate every role (scripts/tokens.mjs) and keep the brand's locked values.",
                {"set": s["roles"], "missing": missing}))
    for widget, places in sorted(replaced.items()):
        found.append(finding(
            "m2-widget", "differs", "minor", f"{widget} used {len(places)} time(s); M3's version is {REPLACED[widget]}",
            ", ".join(places), "Flutter's Material 3 migration guide replaces it.", f"Move to {REPLACED[widget]}.",
            {"widget": widget, "uses": len(places)}))
    if len(sizes) > 10:
        found.append(finding("type-scale-inconsistent", "broken", "minor", f"{len(sizes)} literal font sizes in widget code",
                             ", ".join(f"{s:g}" for s in sorted(sizes)), "M3 builds hierarchy from a fixed type scale of 15 roles.",
                             "Use Theme.of(context).textTheme roles instead of literal sizes."))
    off = sorted(s for s in sizes if all(abs(s - x) > 0.5 for x in m3_type_sizes()))
    if off:
        found.append(finding("type-off-scale", "differs", "minor", f"Literal font sizes off M3's scale: {', '.join(f'{s:g}' for s in off)}",
                             ", ".join(sizes[off[0]][:3]), "M3's type scale sizes come from its 15 roles.", "Map each to its nearest text theme role."))
    numeric = sorted(radii)
    if len(numeric) > 6:
        found.append(finding("radius-scale-inconsistent", "broken", "minor", f"{len(numeric)} different corner radii",
                             ", ".join(f"{r:g}" for r in numeric), "M3's corner scale has a few steps so shapes read as one family.",
                             "Map each container to a corner step."))
    off_r = [r for r in numeric if all(abs(r - c) > 0.5 for c in m3_corners())]
    if off_r:
        found.append(finding("radius-off-scale", "differs", "minor", f"Corner radii off M3's scale: {', '.join(f'{r:g}' for r in off_r)}",
                             ", ".join(radii[off_r[0]][:3]), "M3's corner steps: none 0, 4, 8, 12, 16, 20, 28, 32, 48 and full.",
                             "If it is not a brand choice, use the nearest corner step."))
    if literals:
        found.append(finding("literal-colors", "differs", "minor", f"{len(literals)} literal colors in widget code",
                             ", ".join(literals[:5]), "M3 maps every color in a component to a role, so dark mode and contrast follow the scheme.",
                             "Read colors from Theme.of(context).colorScheme."))
    if shrink:
        found.append(finding("target-shrunk", "broken", "minor", f"Tap targets shrunk in {len(shrink)} place(s)",
                             ", ".join(shrink[:5]), "M3 asks for 48 x 48 dp touch targets; shrinkWrap and compact density drop below it.",
                             "Keep MaterialTapTargetSize.padded and the standard density on touch devices."))
    if loops:
        found.append(finding(
            "motion-reduce-ignored", "broken", "major", f"{len(loops)} looping animation(s) with no reduced-motion check in their file",
            ", ".join(loops[:5]), "WCAG 2.3.3 and 2.2.2; M3 gives every move a reduced-motion version. (If a shared helper "
            "in another file checks the setting, these are fine.)",
            "Stop the loop or show a still frame when MediaQuery.disableAnimationsOf(context) or "
            "View.of(context).platformDispatcher.accessibilityFeatures.reduceMotion is true."))
    if reads_disable and not reads_reduce:
        found.append(finding(
            "ios-reduce-motion-unread", "broken", "minor", "Reduced motion is read from disableAnimations only",
            "MediaQuery.disableAnimations", "iOS's Reduce Motion sets accessibilityFeatures.reduceMotion only; Flutter 3.44 "
            "does not fold it into disableAnimations (Android's Remove animations does set it), so an iPhone user who asked "
            "for less motion still gets every animation.",
            "Also read View.of(context).platformDispatcher.accessibilityFeatures.reduceMotion wherever disableAnimations is read."))
    if locks:
        found.append(finding(
            "orientation-locked", "broken", "minor", f"Screen orientation locked in {len(locks)} place(s)", ", ".join(locks[:5]),
            "Android 16: for apps targeting API 36, orientation and resizability locks are ignored on displays at least 600 dp "
            "wide (tablets, unfolded foldables), so these screens also show in landscape and in wide windows; the opt-out "
            "property ends with API 37 (developer.android.com, Android 16 behavior changes).",
            "Make the locked screens work at M3's medium and expanded widths and in landscape; keep a lock only where "
            "the shortest side is below 600 dp."))
    if bare_icons:
        found.append(finding("icon-button-unlabelled", "broken", "minor", f"{len(bare_icons)} IconButton(s) without a tooltip",
                             ", ".join(bare_icons[:5]), "An icon button needs an accessible name; Flutter's IconButton uses its tooltip as the label (WCAG 4.1.2).",
                             "Add tooltip: (or wrap in Semantics with a label)."))
    order = {"critical": 0, "major": 1, "minor": 2}
    found.sort(key=lambda f: (0 if f["list"] == "broken" else 1, order[f["severity"]], f["rule"]))
    for i, f in enumerate(found, 1):
        f["n"] = i
    facts = {"files": len(files), "color_schemes": schemes, "m2_widgets": {k: len(v) for k, v in replaced.items()},
             "font_sizes": sorted(sizes), "radii": numeric, "literal_colors": len(literals),
             "reads_disable_animations": reads_disable, "reads_reduce_motion": reads_reduce}
    return found, facts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    project = Path(args.project)
    if not project.is_dir():
        raise SystemExit(f"Not a folder: {project}")
    found, facts = scan(project)
    if not facts["files"]:
        raise SystemExit(f"No Dart files to scan under {project} (or its lib/ folder)")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"project": str(Path(args.project).resolve()), "date": date.today().isoformat()}
    (out / "findings.json").write_text(json.dumps({"meta": meta, "findings": found, "facts": facts}, indent=1) + "\n")
    broken = [f for f in found if f["list"] == "broken"]
    differs = [f for f in found if f["list"] == "differs"]
    L = [f"# Material 3 audit (Flutter code): {meta['project']}", "", f"{meta['date']} · {facts['files']} Dart files scanned", "",
         f"## Broken ({len(broken)})", ""]
    L += [f"{f['n']}. **[{f['severity']}] {f['what']}** — `{f['where']}`\n   Why: {f['why']} Fix: {f['fix']}" for f in broken] or ["Nothing broken was found by the static checks."]
    L += ["", f"## Differs from M3 ({len(differs)})", ""]
    L += [f"{f['n']}. {f['what']} — `{f['where']}`\n   {f['why']} {f['fix']}" for f in differs] or ["No differences found."]
    L += ["", "A static scan sees code, not pixels: contrast, layout and motion need the running app (screenshots, and "
          "Flutter's accessibility guidelines in a widget test: references/platform-flutter.md)."]
    (out / "findings.md").write_text("\n".join(L) + "\n")
    print(f"{len(broken)} broken, {len(differs)} differ from M3 -> {out}/findings.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
