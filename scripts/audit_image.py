"""Measure what a picture of a design can tell, for audits with only a screenshot or a design export (no page, no code):
contrast inside text and icon boxes, and target sizes; plus a numbered picture of every finding, the measured ones and
the design notes written by whoever looked at the picture.

The boxes come from that look (Claude reads the picture and writes them) as a JSON spec:
  {"scale": 2,                                   image pixels per CSS px or dp (a 2x phone screenshot: 2)
   "items": [
     {"label": "Body text", "kind": "text", "box": [x, y, w, h]},             box in image pixels
     {"label": "Hero title", "kind": "text", "box": [x, y, w, h], "large": true},
                                                 large text (24 px, or 18.66 px bold) needs 3:1, other text 4.5:1
     {"label": "Menu icon", "kind": "icon", "box": [x, y, w, h]},              icons and UI parts need 3:1
     {"label": "Header button", "kind": "target", "box": [x, y, w, h]},        the tappable area as drawn
     {"label": "The main action gets the least space", "kind": "note", "list": "differs", "box": [x, y, w, h],
      "why": "...", "fix": "..."}]}
Text and icons are measured in vertical stripes about as wide as the box is tall. In each stripe the most common
color is the background and the ink farthest from it (the glyphs' cores, not their soft edges) is the text, so text
over a photo or a gradient is judged against what is behind each part of it. The lowest stripe counts.
Pixel estimates: on known color pairs (tests/test_image_audit.py) a 2x picture measures exactly; at 1x anti-aliasing
thins small glyphs and a ratio reads up to 12% low, never high, so a 1x picture errs only towards a false failure.
A ratio within 0.3 of the limit is marked borderline.

Usage: python3 scripts/audit_image.py <picture> <spec.json> --out <dir>
Writes findings.json, findings.md and audit-image.png.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_web import SEVERITY_ORDER, TARGET_M3, TARGET_WCAG  # noqa: E402
from lib.pixels import draw_markers, measure_contrast  # noqa: E402  one reading for every audit

def item_finding(img: Image.Image, it: dict, scale: float) -> tuple[dict | None, dict]:
    """A finding (or None) and the measurement for one spec item."""
    kind, label, box = it["kind"], it.get("label", it["kind"]), [round(v) for v in it["box"]]
    where = f'{label} (box {box[0]},{box[1]} {box[2]}x{box[3]} px)'
    if kind == "note":
        lst = it.get("list", "differs")
        return ({"rule": "note", "list": lst, "severity": it.get("severity", "minor"), "what": label, "where": where,
                 "why": it.get("why", ""), "fix": it.get("fix", ""), "box": box}, {"label": label, "kind": kind})
    if kind == "target":
        w, h = box[2] / scale, box[3] / scale
        m = {"label": label, "kind": kind, "w": round(w, 1), "h": round(h, 1)}
        side = min(w, h)
        if side < TARGET_WCAG:
            return ({"rule": "target-wcag", "list": "broken", "severity": "major", "what": f"Target {w:.0f}x{h:.0f}, below 24 x 24",
                     "where": where, "why": "WCAG 2.2 SC 2.5.8 Target Size (Minimum); the picture cannot show whether the spacing exception applies.",
                     "fix": "Give the control a 48 x 48 box; draw a smaller visual inside it if the design needs one.", "box": box}, m)
        if side < TARGET_M3:
            return ({"rule": "target-m3", "list": "broken", "severity": "minor", "what": f"Touch target {w:.0f}x{h:.0f}, below M3's 48 x 48",
                     "where": where, "why": "M3 accessibility: touch targets of at least 48 x 48 dp.",
                     "fix": "Make the tappable box 48 high (padding); keep the visible container inside it.", "box": box}, m)
        return None, m
    need = 3.0 if kind == "icon" or it.get("large") else 4.5
    m = measure_contrast(img, box)
    if m is None:
        return None, {"label": label, "kind": kind, "ratio": None, "note": "no text found in the box: missing, or the box is off"}
    m = {"label": label, "kind": kind, "need": need, **m}
    borderline = abs(m["ratio"] - need) < 0.3
    m["borderline"] = borderline
    if m["ratio"] >= need:
        return None, m
    faint_note = "; faint, below 1.5:1" if m.get("faint") else ""
    what = f'{"Icon" if kind == "icon" else "Text"} contrast {m["ratio"]}:1, needs {need}:1 ({m["fg"]} on {m["bg"]}{faint_note}' \
           f'{", lowest of " + str(m["stripes"]) + " stripes, median " + str(m["median"]) if m["stripes"] > 1 else ""}' \
           f'{"; borderline: a pixel estimate" if borderline else ""})'
    return ({"rule": "contrast", "list": "broken", "severity": "critical" if m["ratio"] < need - 1.5 else "major",
             "what": what, "where": where, "why": "WCAG 1.4.3 (text) or 1.4.11 (icons); M3 pairs every on-color with its container for this reason.",
             "fix": f"Use the role's on-color or a tone that reaches {need}:1.", "box": box}, m)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("picture")
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    img = Image.open(args.picture).convert("RGB")
    spec = json.loads(Path(args.spec).read_text())
    scale = float(spec.get("scale", 1))
    found, measured = [], []
    for it in spec["items"]:
        if it["kind"] not in ("text", "icon", "target", "note"):
            raise SystemExit(f"unknown kind {it['kind']}: text, icon, target or note")
        f, m = item_finding(img, it, scale)
        measured.append(m)
        if f:
            found.append(f)
    found.sort(key=lambda f: (0 if f["list"] == "broken" else 1, SEVERITY_ORDER[f["severity"]]))
    for i, f in enumerate(found, 1):
        f["n"] = i
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    draw_markers(img, [{"n": f["n"], "list": f["list"], "box": f["box"]} for f in found], scale, out / "audit-image.png")
    meta = {"picture": str(Path(args.picture).resolve()), "size": list(img.size), "scale": scale, "date": date.today().isoformat()}
    (out / "findings.json").write_text(json.dumps({"meta": meta, "findings": found, "measured": measured}, indent=1) + "\n")
    broken = [f for f in found if f["list"] == "broken"]
    differs = [f for f in found if f["list"] == "differs"]
    L = [f"# Material 3 audit (picture only): {Path(args.picture).name}", "",
         f"{meta['date']} · {img.size[0]} x {img.size[1]} px at {scale:g}x · pixel estimates, not code", "",
         f"## Broken ({len(broken)})", ""]
    L += [f"{f['n']}. **[{f['severity']}] {f['what']}** — {f['where']}\n   Why: {f['why']} Fix: {f['fix']}" for f in broken] or ["Nothing broken was found."]
    L += ["", f"## Differs from M3 ({len(differs)})", ""]
    L += [f"{f['n']}. {f['what']} — {f['where']}\n   {f['why']} {f['fix']}" for f in differs] or ["No differences noted."]
    missed = [m for m in measured if m["kind"] in ("text", "icon") and m.get("ratio") is None]
    if missed:
        L += ["", f"## Not measured ({len(missed)})", "", "Look at these by hand.", ""]
        L += [f"- **{m['label']}:** {m['note']}" for m in missed]
    L += ["", "## Measured", ""]
    for m in measured:
        if m["kind"] in ("text", "icon"):
            L.append(f"- **{m['label']}:** " + (f"{m['ratio']}:1 lowest, {m['median']}:1 median ({m['fg']} on {m['bg']}), needs {m['need']}:1"
                                               + (", borderline" if m.get("borderline") else "") if m.get("ratio") else m.get("note", "")))
        elif m["kind"] == "target":
            L.append(f"- **{m['label']}:** {m['w']:g} x {m['h']:g}")
    (out / "findings.md").write_text("\n".join(L) + "\n")
    print(f"{len(broken)} broken, {len(differs)} differ from M3 -> {out}/findings.md, audit-image.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
