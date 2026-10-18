"""Audit a web page against Material 3 and WCAG 2.2 in real Chrome, and sort the findings into two lists.

Broken: faults whatever the brand — text and UI contrast, target size, invisible focus, a missing hover state,
a scale that disagrees with itself, sideways scroll on a phone, movement under reduced motion, a video that plays
by itself with no pause, and axe-core's WCAG violations. Differs from M3: style choices — the typeface, values off
M3's type and corner scales, the button shape, spacing off the 4 dp grid. Short and separate; never a fault by itself.
Not measured: what a check could not judge (an area that moves by itself, focus that left the window). Look at those.

Usage:
  python3 scripts/audit_web.py <url-or-file> --out <dir> [--sizes 390x844,1440x900] [--ignore CSS-selector]
                               [--decided decided.json]
A local file may carry a query and a hash: prototype/index.html?frame=full#home.
--decided names departures the project has approved, {"radius-off-scale": "2 px corners, DECISIONS 2026-10-18"};
those findings stay in Differs, marked as decided.
Before measuring, the page is scrolled through once (lazy and reveal-on-scroll content loads), then its animations
are finished and looping ones and videos paused. With a modal dialog open, only the dialog is measured.
Writes findings.json, findings.md and audit-<w>x<h>.png (the page with a numbered marker at each finding).
"""
import argparse
import io
import json
import re
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.pixels import contrast, draw_markers, luminance, measure_contrast, rgb  # noqa: E402,F401  one formula for every audit

SKILL = Path(__file__).resolve().parent.parent
GOOGLE = SKILL / "tests" / "fixtures" / "google"
MEASURE = (SKILL / "scripts" / "lib" / "audit_measure.js").read_text()
AXE = SKILL / "scripts" / "node_modules" / "axe-core" / "axe.min.js"

TARGET_WCAG = 24   # WCAG 2.2 SC 2.5.8 Target Size (Minimum), AA
TARGET_M3 = 48     # M3 accessibility: touch targets at least 48 x 48 dp
COMPACT_MAX = 599  # M3 window size classes: compact is below 600 dp
EXPANDED_MIN = 840
FOCUS_PAD = 8      # px photographed around a control: M3's ring sits 2 px out and is 3 px wide; other rings reach ~6
HOVER_SHARE = 0.02 # share of a control's box a hover state changes at least (M3: an 8% layer over all of it)
VIDEO_FRAMES = (0.2, 0.4, 0.6, 0.8)  # with the paused frame: five frames of a video behind text
M3_FONTS = {"roboto", "roboto flex", "google sans", "google sans flex", "google sans text"}
SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2}
# The page with every glyph made transparent (text, icon fonts, currentColor icons): what sits behind the text.
TEXTLESS = ("*, *::before, *::after, *::placeholder, *::marker { color: transparent !important; "
            "-webkit-text-fill-color: transparent !important; text-shadow: none !important; "
            "text-decoration-color: transparent !important; caret-color: transparent !important; transition: none !important; }")


def m3_type_sizes() -> list[float]:
    data = json.loads((GOOGLE / "flutter" / "text_style.json").read_text())
    return sorted({float(v) for k, v in data.items() if k.endswith(".size")})


def m3_corners() -> list[float]:
    src = (GOOGLE / "compose" / "ShapeTokens.kt").read_text()
    return sorted({float(v) for v in re.findall(r"val CornerValue\w+ = CornerSize\(([\d.]+)\.dp\)", src)})


def m3_component_spacing() -> set[float]:
    """The paddings and gaps Google's own components use (Compose tokens): a few are off the 4 dp grid (6, 10, 26)."""
    pat = re.compile(r"val (\w+)\s*(?::\s*[\w.]+)?\s*(?:=|\n\s*get\(\)\s*=)\s*([\d.]+)\.dp")
    out = set()
    for f in (GOOGLE / "compose").glob("*.kt"):
        out |= {float(v) for name, v in pat.findall(f.read_text()) if re.search(r"Space|Padding|Gap|Spacing|Margin", name)}
    return out


def composite(fg: list[float], bg_hex: str) -> str:
    """A color with alpha ([r, g, b, a], a 0..1) over an opaque background."""
    a = fg[3]
    return "#{:02X}{:02X}{:02X}".format(*(round(c * a + d * (1 - a)) for c, d in zip(fg[:3], rgb(bg_hex))))


def main_colors(img: Image.Image, rect: dict, scale: float, share: float = 0.1) -> list[str]:
    """The colors covering at least `share` of a box, in a picture of the page without its text."""
    box = [int(rect["x"] * scale), int(rect["y"] * scale), int((rect["x"] + rect["w"]) * scale), int((rect["y"] + rect["h"]) * scale)]
    box = [max(0, box[0]), max(0, box[1]), min(img.width, box[2]), min(img.height, box[3])]
    if box[2] - box[0] < 2 or box[3] - box[1] < 2:
        return []
    q = img.crop(box).quantize(colors=8)
    pal = q.getpalette()
    counts = q.getcolors()
    total = sum(c for c, _ in counts)
    return ["#{:02X}{:02X}{:02X}".format(*pal[i * 3:i * 3 + 3]) for c, i in counts if c / total >= share]


def changed_pixels(a: bytes, b: bytes) -> int:
    ia, ib = Image.open(io.BytesIO(a)).convert("RGB"), Image.open(io.BytesIO(b)).convert("RGB")
    if ia.size != ib.size:
        return ia.width * ia.height
    return ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v >= 6 else 0).histogram()[255]


def page_clip(r, w, h, pad):
    """A screenshot clip around the part of an element inside the window; None when less than half of it is inside.
    Playwright's clip for a window screenshot is in window coordinates (measured: page coordinates miss the element
    once the document has scrolled)."""
    if not r or r["w"] < 4 or r["h"] < 4:
        return None
    x0, y0 = max(r["vx"], 0), max(r["vy"], 0)
    x1, y1 = min(r["vx"] + r["w"], w), min(r["vy"] + r["h"], h)
    if x1 - x0 < 4 or y1 - y0 < 4 or (x1 - x0) * (y1 - y0) < 0.5 * r["w"] * r["h"]:
        return None
    x0, y0, x1, y1 = max(x0 - pad, 0), max(y0 - pad, 0), min(x1 + pad, w), min(y1 + pad, h)
    return {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}


def _center(b):
    return b["x"] + b["w"] / 2, b["y"] + b["h"] / 2


def _dist_to_box(px, py_, b):
    dx = max(b["x"] - px, 0, px - (b["x"] + b["w"]))
    dy = max(b["y"] - py_, 0, py_ - (b["y"] + b["h"]))
    return (dx * dx + dy * dy) ** 0.5


def spacing_exception(t, targets, small):
    """WCAG 2.5.8's spacing exception: a 24 px circle on the undersized target's center touches no other target
    and no other undersized target's circle."""
    cx, cy = _center(t["target"])
    for o in targets:
        if o is t:
            continue
        if _dist_to_box(cx, cy, o["target"]) < 12:
            return False
    for o in small:
        if o is t:
            continue
        ox, oy = _center(o["target"])
        if ((cx - ox) ** 2 + (cy - oy) ** 2) ** 0.5 < 24:
            return False
    return True


def finding(rule, lst, severity, what, where, why, fix, size, rect=None, data=None):
    return {"rule": rule, "list": lst, "severity": severity, "what": what, "where": where, "why": why, "fix": fix,
            "sizes": [size], "rects": {size: rect} if rect else {}, "data": data or {}}


def skipped(check, where, why, size):
    return {"check": check, "where": where, "why": why, "sizes": [size]}


# ---------- bringing a page to a still state ---------------------------------------------------------------

def scroll_through(page, h: int):
    """Smooth scrolling off, then the page scrolled through once: lazy images and reveal-on-scroll content load,
    and videos that play on the way are noted."""
    page.add_style_tag(content="html, body { scroll-behavior: auto !important; }")
    y = 0
    for _ in range(60):
        if y >= page.evaluate("document.scrollingElement.scrollHeight"):
            break
        page.evaluate("(y) => { window.scrollTo({ top: y, behavior: 'instant' }); window.__m3audit.markPlaying(); }", y)
        page.wait_for_timeout(100)
        y += int(h * 0.8)
    page.evaluate("window.scrollTo({ top: 0, behavior: 'instant' })")


def settle(page, h: int):
    scroll_through(page, h)
    page.evaluate("window.__m3audit.loaded()")
    page.wait_for_timeout(300)
    page.evaluate("window.__m3audit.settle()")


def textless(page) -> Image.Image:
    tag = page.add_style_tag(content=TEXTLESS)
    img = Image.open(io.BytesIO(page.screenshot(full_page=True))).convert("RGB")
    tag.evaluate("(e) => e.remove()")
    page.evaluate("window.__m3audit.settle()")  # finishes the color transitions the removal starts
    return img


def is_active(page, sel) -> bool:
    return page.evaluate("(s) => document.activeElement === document.querySelector(s)", sel)


# ---------- measuring one size -----------------------------------------------------------------------------

def measure(browser, url: str, w: int, h: int, ignore: str | None):
    size = f"{w}x{h}"
    found, missed = [], []
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(url, wait_until="load")
    page.add_script_tag(content=MEASURE)
    settle(page, h)
    page.mouse.move(w - 1, h - 1)
    m = page.evaluate("(sel) => window.__m3audit.collect(sel)", ignore)
    # axe-core runs on the same state as the measurement (before focus and hover move anything).
    page.add_script_tag(path=str(AXE))
    axe = page.evaluate("""async ([sel, scope]) => {
      const exclude = [['[data-audit-ignore]'], ['#__m3audit_overlay']];
      if (sel) exclude.push([sel]);
      const r = await axe.run({ include: [[scope || 'body']], exclude }, {
        runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] },
        resultTypes: ['violations', 'passes'] });
      const find = (t) => { try { return document.querySelector(t.join(' ')); } catch (e) { return null; } };
      const own = (t) => { const el = find(t); return el ? window.__m3audit.selectorOf(el) : t.join(' '); };
      const box = (t) => { const r = find(t)?.getBoundingClientRect(); return r ? { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height } : null; };
      const pick = (n) => ({ selector: own(n.target), rect: box(n.target), html: n.html.slice(0, 120), data: (n.any[0] || {}).data || null });
      return { version: axe.version,
        violations: r.violations.map((v) => ({ id: v.id, impact: v.impact, help: v.help, url: v.helpUrl, nodes: v.nodes.slice(0, 10).map(pick) })),
        contrast: [...(r.passes.find((p) => p.id === 'color-contrast')?.nodes ?? []), ...(r.violations.find((v) => v.id === 'color-contrast')?.nodes ?? [])].map(pick) };
    }""", [ignore, m["scope"]])
    compact = w <= COMPACT_MAX

    # Contrast of text and icons (WCAG 1.4.3 and 1.4.11). Where CSS cannot tell the background (a picture, a
    # gradient, a video), the page is photographed with its text hidden and the lowest ratio against the main
    # colors behind the text counts; over a video, across five of its frames.
    shot = Image.open(io.BytesIO(page.screenshot(full_page=True))).convert("RGB")
    frames = {None: [textless(page)]}
    scale = frames[None][0].width / max(m["viewport"]["w"], m["scrollWidth"])
    box_of = lambda r: [r["x"] * scale, r["y"] * scale, r["w"] * scale, r["h"] * scale]  # noqa: E731
    for vid in sorted({t["bgVideo"] for t in m["texts"] if t["bgVideo"] is not None}):
        frames[vid] = list(frames[None])
        for frac in VIDEO_FRAMES:
            if page.evaluate("([id, f]) => window.__m3audit.seek(id, f)", [vid, frac]):
                frames[vid].append(textless(page))
    ratios = {}
    for t in m["texts"]:
        if t["disabled"]:
            continue
        fg, bg, est = t["fg"], t["bg"], ""
        px = measure_contrast(shot, box_of(t["rect"])) if t["group"] else None
        if px:
            fg, bg = px["fg"], px["bg"]
            est = " (inside an element with opacity below 1: measured from pixels, an estimate)"
        elif not t["bgKnown"]:
            shots = frames[t["bgVideo"]]
            pairs = [(composite(t["fgRaw"], c), c) for img in shots for c in main_colors(img, t["rect"], scale)]
            if pairs:
                fg, bg = min(pairs, key=lambda p: contrast(*p))
                est = (f" (lowest over {len(shots)} frames of the video behind it: an estimate)" if len(shots) > 1
                       else " (background photographed with the text hidden: an estimate)")
        ratio = round(contrast(fg, bg), 2)
        if not est:
            ratios[t["selector"]] = ratio  # estimates stay out of the cross-check with axe-core
        large = t["size"] >= 24 or (t["size"] >= 18.66 and t["weight"] >= 700)
        need = 3.0 if (t["isIcon"] or large) else 4.5
        if ratio < need:
            kind = "Icon" if t["isIcon"] else "Text"
            sev = "critical" if ratio < need - 1.5 else "major"
            found.append(finding(
                "contrast", "broken", sev, f"{kind} contrast {ratio}:1, needs {need}:1{est}",
                f'{t["selector"]} "{t["text"]}"',
                "WCAG 1.4.3 (text) or 1.4.11 (icons); M3 pairs every on-color with its container for this reason.",
                f"Use the role's on-color (on-surface, on-surface-variant, on-primary...) or a tone that reaches {need}:1.",
                size, t["rect"], {"fg": fg, "bg": bg, "ratio": ratio}))

    # SVG icons that are a control's only content (WCAG 1.4.11, 3:1), measured from pixels.
    for ic in m["icons"]:
        px = measure_contrast(shot, box_of(ic["rect"]))
        where = f'{ic["selector"]} "{ic["name"]}"'
        if not px:
            missed.append(skipped("contrast", where, "the SVG icon could not be read from the pixels", size))
        elif px["ratio"] < 3.0:
            found.append(finding(
                "contrast", "broken", "critical" if px["ratio"] < 1.5 else "major",
                f"Icon contrast {px['ratio']}:1, needs 3.0:1 (an SVG icon, measured from pixels: an estimate)", where,
                "WCAG 1.4.11 Non-text Contrast: an icon that is a control's only content must reach 3:1.",
                "Draw the icon in the role's on-color (on-surface-variant on surfaces, on-primary on primary).",
                size, ic["rect"], {"fg": px["fg"], "bg": px["bg"], "ratio": px["ratio"]}))

    # Target size (WCAG 2.5.8; M3's 48 x 48 touch target).
    small = [t for t in m["targets"] if min(t["target"]["w"], t["target"]["h"]) < TARGET_WCAG and not t["inline"]]
    for t in m["targets"]:
        if t["inline"]:
            continue
        tw, th = t["target"]["w"], t["target"]["h"]
        side = min(tw, th)
        if side >= TARGET_M3 or (not compact and side >= TARGET_WCAG):
            continue
        if side < TARGET_WCAG and not spacing_exception(t, m["targets"], small):
            found.append(finding(
                "target-wcag", "broken", "major", f"Target {round(tw)}x{round(th)} px, below 24 x 24",
                f'{t["selector"]} "{t["name"]}"', "WCAG 2.2 SC 2.5.8 Target Size (Minimum).",
                "Give the control a 48 x 48 px box; draw a smaller visual inside it if the design needs one.",
                size, t["target"]))
        elif compact:
            found.append(finding(
                "target-m3", "broken", "minor", f"Touch target {round(tw)}x{round(th)} px, below M3's 48 x 48",
                f'{t["selector"]} "{t["name"]}"', "M3 accessibility: touch targets of at least 48 x 48 dp.",
                "Make the element's box 48 px (padding or min-height); keep the visible container inside it.",
                size, t["target"]))

    # Sideways scroll on a phone.
    if compact and m["scrollWidth"] > m["viewport"]["w"] + 1:
        found.append(finding(
            "sideways-scroll", "broken", "major", f'The page is {m["scrollWidth"]} px wide in a {w} px window',
            ", ".join(m["overflowing"]) or "page", "WCAG 1.4.10 Reflow; M3's compact window has one column.",
            "Let the wide element wrap or shrink: max-width: 100%, flex-wrap, min-width: 0.", size))

    # Focus that cannot be seen (WCAG 2.4.7). Each element is photographed with keyboard focus, then without it at
    # the same scroll position, then once more to see whether the area moves by itself. A visible indicator changes
    # at least half the element's outline (a 1 px ring all round changes all of it) or 1% of the photographed area;
    # an element wider than the window is judged on its visible part.
    count = page.evaluate("(sel) => window.__m3audit.focusables(sel)", ignore)
    for i in range(count):
        if i == 60:
            missed.append(skipped("focus", f"{count - 60} more focusable elements", "the check stops at 60 per page", size))
            break
        sel = f'[data-m3a-focus="{i}"]'
        info = page.evaluate("(s) => window.__m3audit.prepare(s)", sel)
        if not info:
            continue
        where = f'{info["selector"]} "{info["name"]}"'
        page.mouse.move(w - 1, h - 1)
        # Reach the element by keyboard, so the browser treats the focus as keyboard focus (:focus-visible).
        page.evaluate("(s) => document.querySelector(s).focus({ preventScroll: true })", sel)
        page.keyboard.press("Shift+Tab")
        page.keyboard.press("Tab")
        if not is_active(page, sel):
            page.evaluate("(s) => document.querySelector(s).focus()", sel)
        if not is_active(page, sel):
            missed.append(skipped("focus", where, "focus did not stay on it", size))
            continue
        page.evaluate("window.__m3audit.quiet()")
        v = page.evaluate("(s) => window.__m3audit.view(s)", sel)
        clip = page_clip(v, w, h, FOCUS_PAD)
        if not clip:
            page.evaluate("document.activeElement?.blur()")
            missed.append(skipped("focus", where, "less than half of it inside the window when focused", size))
            continue
        focused = page.screenshot(clip=clip)
        page.evaluate("document.activeElement?.blur()")
        page.evaluate("window.__m3audit.quiet()")
        v2 = page.evaluate("(s) => window.__m3audit.view(s)", sel)
        if not v2 or any(abs(v[k] - v2[k]) > 0.5 for k in ("vx", "vy", "sx", "sy")):
            missed.append(skipped("focus", where, "the page moved when focus left", size))
            continue
        plain = page.screenshot(clip=clip)
        page.wait_for_timeout(120)
        need = min(clip["width"] + clip["height"] - 4 * FOCUS_PAD, 0.01 * clip["width"] * clip["height"])
        if changed_pixels(plain, page.screenshot(clip=clip)) >= need / 2:
            missed.append(skipped("focus", where, "the area moves by itself", size))
            continue
        if changed_pixels(plain, focused) < need:
            found.append(finding(
                "focus-invisible", "broken", "major", "Keyboard focus is not visible", where,
                "WCAG 2.4.7 Focus Visible; M3 draws a focus indicator on every interactive part.",
                "Add a focus ring on :focus-visible (M3: 3 px, the secondary color, 2 px off the container).",
                size, info["page"]))

    # A missing hover state, on windows wide enough for a pointer: photographed without and with the pointer on it.
    if w >= EXPANDED_MIN:
        for t in [t for t in m["targets"] if t["buttonLike"]][:30]:
            sel = f'[data-m3a-t="{t["i"]}"]'
            info = page.evaluate("(s) => window.__m3audit.prepare(s)", sel)
            if not info:
                continue
            where = f'{t["selector"]} "{t["name"]}"'
            page.mouse.move(w - 1, h - 1)
            page.evaluate("window.__m3audit.quiet()")
            v = page.evaluate("(s) => window.__m3audit.view(s)", sel)
            clip = page_clip(v, w, h, 2)
            if not clip:
                missed.append(skipped("hover", where, "less than half of it inside the window", size))
                continue
            cx, cy = v["vx"] + v["w"] / 2, v["vy"] + v["h"] / 2
            if not page.evaluate("([s, x, y]) => window.__m3audit.hits(s, x, y)", [sel, cx, cy]):
                missed.append(skipped("hover", where, "another element covers its middle", size))
                continue
            plain = page.screenshot(clip=clip)
            page.wait_for_timeout(120)
            noise = changed_pixels(plain, page.screenshot(clip=clip))
            page.mouse.move(cx, cy)
            page.evaluate("window.__m3audit.quiet()")
            hovered = page.screenshot(clip=clip)
            page.mouse.move(w - 1, h - 1)
            need = HOVER_SHARE * clip["width"] * clip["height"]
            if noise >= need / 2:
                missed.append(skipped("hover", where, "the area moves by itself", size))
            elif changed_pixels(plain, hovered) < need:
                found.append(finding(
                    "hover-missing", "broken", "minor", "No hover state", where,
                    "M3 interaction states: hover shows an 8% state layer.",
                    "Add a hover state layer: the content color at the hover opacity over the container.",
                    size, info["page"]))

    # A video that plays by itself for more than 5 seconds needs a way to stop it (WCAG 2.2.2).
    for v in m["videos"]:
        if v["played"] and (v["loop"] or (v["duration"] or 0) > 5) and not v["controls"] and not v["pauseControl"]:
            length = "loops" if v["loop"] else f'runs {v["duration"]:g} s'
            found.append(finding(
                "video-no-pause", "broken", "major", f"A video plays by itself and {length}, with no way to pause it",
                v["selector"], "WCAG 2.2.2 Pause, Stop, Hide: movement that starts by itself and lasts over 5 seconds needs a pause.",
                "Add a visible pause button (a 48 x 48 px target), or play the video once and stop on its last frame.",
                size, v["rect"]))

    # Scales that disagree with themselves, and values off M3's scales.
    sizes_used = sorted({round(t["size"] * 2) / 2 for t in m["texts"] if not t["isIcon"]})
    if len(sizes_used) > 10:
        found.append(finding(
            "type-scale-inconsistent", "broken", "minor", f"{len(sizes_used)} font sizes on one page",
            ", ".join(f"{s:g}px" for s in sizes_used),
            "M3 Typography, type scale: every text takes one of 15 roles; more than 10 sizes on a page means text sits between roles.",
            "Map every text to a type role (display, headline, title, body, label) and drop the in-between sizes.", size))
    type_scale = m3_type_sizes()
    off = [s for s in sizes_used if all(abs(s - x) > 0.5 for x in type_scale)]
    if off:
        found.append(finding(
            "type-off-scale", "differs", "minor", f"Font sizes outside M3's type scale: {', '.join(f'{s:g}px' for s in off)}",
            "text", f"M3's type scale sizes: {', '.join(f'{s:g}' for s in type_scale)} px.",
            "If it is not a brand choice, move each to its nearest type role.", size))
    families = sorted({t["family"] for t in m["texts"] if not t["isIcon"]})
    non_m3 = [f for f in families if f.lower() not in M3_FONTS]
    if non_m3:
        found.append(finding(
            "typeface", "differs", "minor", f"Typeface: {', '.join(non_m3)}", "text",
            "M3's baseline typeface is Roboto; Expressive uses Roboto Flex and Google Sans Flex. A brand font is M3's own advice for brand expression.",
            "Keep it if it is the brand's; set it as md.ref.typeface.brand and plain.", size))
    corners = m3_corners()
    numeric = sorted({r["radius"] for r in m["radii"] if r["radius"] != "full"})
    if len(numeric) > 6:
        found.append(finding(
            "radius-scale-inconsistent", "broken", "minor", f"{len(numeric)} different corner radii",
            ", ".join(f"{r:g}px" for r in numeric),
            "M3 Shape, corner radius scale: a few steps so shapes read as one family; more than 6 radii means no scale.",
            "Map each container to a corner step (none, extra-small 4, small 8, medium 12, large 16, extra-large 28, full).", size))
    off_r = [r for r in numeric if all(abs(r - c) > 0.5 for c in corners)]
    if off_r:
        examples = [r for r in m["radii"] if r["radius"] in off_r][:4]
        found.append(finding(
            "radius-off-scale", "differs", "minor", f"Corner radii outside M3's scale: {', '.join(f'{r:g}px' for r in off_r)}",
            ", ".join(e["selector"] for e in examples), f"M3's corner steps: {', '.join(f'{c:g}' for c in corners)} px and full.",
            "If it is not a brand choice, move each container to its corner step.", size, examples[0]["rect"] if examples else None))
    square_ok = {12.0, 16.0, 20.0, 28.0}
    by_radius = {}
    for r in m["radii"]:
        if r["buttonLike"] and r["radius"] != "full" and r["radius"] not in square_ok:
            by_radius.setdefault(r["radius"], []).append(r)
    for radius, items in sorted(by_radius.items()):
        found.append(finding(
            "button-shape", "differs", "minor", f"Button corners {radius:g}px", ", ".join(i["selector"] for i in items[:3]),
            "M3 buttons are fully round; Expressive adds square buttons at 12, 16 or 28 px by size, and FABs use 16, 20 or 28.",
            "If it is not a brand choice, use full corners (or the square step for the size).", size, items[0]["rect"]))
    own_spacing = m3_component_spacing()
    off_grid = [s for s in m["spacing"] if s["value"] % 4 and s["value"] not in own_spacing]
    if off_grid:
        found.append(finding(
            "spacing-off-grid", "differs", "minor", "Spacing off the 4 dp grid: " + ", ".join(f'{s["value"]:g}px' for s in off_grid[:8]),
            ", ".join(s["selector"] for s in off_grid[:3]),
            "M3 spaces on a 4 dp baseline, in 8 dp steps for layout; values its own components use (such as 6, 10 and 26) are left out.",
            "Round paddings and gaps to multiples of 4.", size, off_grid[0]["rect"]))

    ours = {(f["rule"], f["where"].split(' "')[0]) for f in found}
    for v in axe["violations"]:
        for n in v["nodes"]:
            if v["id"] == "color-contrast" and ("contrast", n["selector"]) in ours:
                continue
            if v["id"] == "target-size" and any(k[1] == n["selector"] and k[0].startswith("target") for k in ours):
                continue
            sev = "major" if v["impact"] in ("critical", "serious") else "minor"
            found.append(finding(f"axe-{v['id']}", "broken", sev, v["help"], n["selector"],
                                 f"axe-core rule {v['id']} (WCAG 2.2 A/AA).", f"See {v['url']}", size, n.get("rect")))
    cross = []
    for n in axe["contrast"]:
        d = n.get("data") or {}
        if "contrastRatio" in d and n["selector"] in ratios and d["contrastRatio"]:
            cross.append({"selector": n["selector"], "ours": ratios[n["selector"]], "axe": round(float(d["contrastRatio"]), 2)})

    facts = {"size": size, "fonts": families, "font_sizes": sizes_used, "radii": numeric, "scope": m["scope"],
             "navigation": m["nav"], "targets": len(m["targets"]), "texts": len(m["texts"]), "videos": len(m["videos"]),
             "axe_version": axe["version"]}
    ctx.close()

    # Movement that ignores reduced motion (WCAG 2.3.3; M3 asks for reduced-motion versions).
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url, wait_until="load")
    page.add_script_tag(content=MEASURE)
    scroll_through(page, h)
    page.wait_for_timeout(1000)
    for a in page.evaluate("(sel) => window.__m3audit.stillMoving(sel)", ignore):
        what = "A video keeps playing with reduced motion on" if a["kind"] == "video" else "Movement keeps running with reduced motion on"
        found.append(finding(
            "motion-reduce", "broken", "major", what, a["selector"],
            "WCAG 2.3.3 Animation from Interactions and 2.2.2; M3 gives every move a reduced-motion version.",
            "Under prefers-reduced-motion: reduce, stop the movement or replace it with a fade.", size, a["rect"]))
    ctx.close()
    return found, facts, cross, missed


# ---------- merging, numbering, writing --------------------------------------------------------------------

def merge(all_findings):
    """One finding per rule, element and message: a size that measures something else keeps its own finding."""
    merged = {}
    for f in all_findings:
        key = (f["rule"], f["where"], f["what"])
        if key in merged:
            merged[key]["sizes"] += [s for s in f["sizes"] if s not in merged[key]["sizes"]]
            merged[key]["rects"].update(f["rects"])
        else:
            merged[key] = f
    out = list(merged.values())
    out.sort(key=lambda f: (0 if f["list"] == "broken" else 1, SEVERITY_ORDER[f["severity"]], f["rule"]))
    for i, f in enumerate(out, 1):
        f["n"] = i
    return out


def merge_skipped(items):
    merged = {}
    for s in items:
        key = (s["check"], s["where"], s["why"])
        if key in merged:
            merged[key]["sizes"] += [z for z in s["sizes"] if z not in merged[key]["sizes"]]
        else:
            merged[key] = s
    return list(merged.values())


def annotate(browser, url, w, h, findings, path: Path):
    size = f"{w}x{h}"
    marks = [{"n": f["n"], "list": f["list"], "r": f["rects"][size]} for f in findings if f["rects"].get(size)]
    ctx = browser.new_context(viewport={"width": w, "height": h})
    page = ctx.new_page()
    page.goto(url, wait_until="load")
    page.add_script_tag(content=MEASURE)
    settle(page, h)
    img = Image.open(io.BytesIO(page.screenshot(full_page=True)))
    draw_markers(img, [{"n": m["n"], "list": m["list"], "box": [m["r"]["x"], m["r"]["y"], m["r"]["w"], m["r"]["h"]]} for m in marks],
                 1, path)
    ctx.close()


def write_md(meta, findings, facts, cross, missed, path: Path):
    broken = [f for f in findings if f["list"] == "broken"]
    differs = [f for f in findings if f["list"] == "differs"]
    L = [f"# Material 3 audit: {meta['url']}", "", f"{meta['date']} · sizes {', '.join(meta['sizes'])} · "
         f"Chrome {meta['chrome']} · axe-core {meta['axe']}", ""]
    L += [f"## Broken ({len(broken)})", ""]
    if not broken:
        L.append("Nothing broken was found by the measured checks.")
    for f in broken:
        L += [f"{f['n']}. **[{f['severity']}] {f['what']}** — `{f['where']}` ({', '.join(f['sizes'])})",
              f"   Why: {f['why']} Fix: {f['fix']}"]
    L += ["", f"## Differs from M3 ({len(differs)})", ""]
    if not differs:
        L.append("No style differences from M3's scales were found.")
    for f in differs:
        dec = f" — decided: {f['decided']}" if f.get("decided") else ""
        L += [f"{f['n']}. {f['what']}{dec} — `{f['where']}` ({', '.join(f['sizes'])})", f"   {f['why']} {f['fix']}"]
    if missed:
        L += ["", f"## Not measured ({len(missed)})", "", "Checks that could not judge these; look at them by hand.", ""]
        L += [f"- **{s['check']}:** `{s['where']}` — {s['why']} ({', '.join(s['sizes'])})" for s in missed]
    L += ["", "## Facts", ""]
    for fa in facts:
        scope = f"; only the open dialog `{fa['scope']}` was measured" if fa["scope"] else ""
        L.append(f"- **{fa['size']}:** fonts {', '.join(fa['fonts']) or '-'}; font sizes {', '.join(f'{s:g}' for s in fa['font_sizes'])} px; "
                 f"corner radii {', '.join(f'{r:g}' for r in fa['radii']) or '-'} px; {fa['targets']} targets; {fa['videos']} videos; "
                 f"navigation {', '.join(str(n['items']) + ' items' for n in fa['navigation']) or 'none'}{scope}")
    if cross:
        worst = max(abs(c["ours"] - c["axe"]) for c in cross)
        L += ["", "## Cross-check with axe-core", "", f"{len(cross)} text contrast ratios measured by both; largest difference {worst:.2f}."]
    L += ["", "Measured checks only. The design reading (layout, navigation, component choice, hierarchy against M3's "
          "guidance) is written by the skill on top of this list."]
    path.write_text("\n".join(L) + "\n")


def to_url(target: str) -> str:
    """A URL as given; a local file, with any ?query and #hash kept, as a file:// URL."""
    if "://" in target:
        return target
    path, rest = re.match(r"^([^?#]*)(.*)$", target).groups()
    if not Path(path).is_file():
        raise SystemExit(f"Not a URL or a file: {target}")
    return Path(path).resolve().as_uri() + rest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--out", required=True)
    ap.add_argument("--sizes", default="390x844,1440x900")
    ap.add_argument("--ignore")
    ap.add_argument("--decided")
    args = ap.parse_args()
    url = to_url(args.target)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sizes = [tuple(int(v) for v in s.split("x")) for s in args.sizes.split(",")]
    decided = json.loads(Path(args.decided).read_text()) if args.decided else {}
    all_found, facts, cross, all_missed = [], [], [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        for w, h in sizes:
            f, fa, cr, mi = measure(browser, url, w, h, args.ignore)
            all_found += f
            facts.append(fa)
            cross += cr
            all_missed += mi
        findings = merge(all_found)
        missed = merge_skipped(all_missed)
        for f in findings:
            if f["list"] == "differs" and f["rule"] in decided:
                f["decided"] = decided[f["rule"]]
        for w, h in sizes:
            annotate(browser, url, w, h, findings, out / f"audit-{w}x{h}.png")
        meta = {"url": url, "date": date.today().isoformat(), "sizes": [f"{w}x{h}" for w, h in sizes],
                "chrome": browser.version, "axe": facts[0]["axe_version"] if facts else "?"}
        browser.close()
    (out / "findings.json").write_text(json.dumps({"meta": meta, "findings": findings, "not_measured": missed,
                                                   "facts": facts, "crosscheck": cross}, indent=1) + "\n")
    write_md(meta, findings, facts, cross, missed, out / "findings.md")
    b = sum(1 for f in findings if f["list"] == "broken")
    print(f"{b} broken, {len(findings) - b} differ from M3, {len(missed)} not measured -> {out}/findings.md, audit-*.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
