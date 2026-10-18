"""Check 10: the picture-only audit (scripts/audit_image.py) measures contrast and target sizes close to the truth.

A page with known color pairs (text from 11 to 24 px, an icon, text across a two-tone background) and known button
sizes is photographed in Chrome at 2x and at 1x; the boxes come from the page, the truth from its CSS colors and the
same WCAG formula. At 2x every ratio must be within TOLERANCE of the truth (the lowest stripe for the two-tone line);
at 1x, where anti-aliasing thins small glyphs, a ratio may read low (never more than LOW_1X below) but never high,
so a 1x picture can only err towards a false failure. Targets must land in the right list.
Prints "CHECK 10 PASS|FAIL <detail>".
"""
import json
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
OUT = HERE / "out" / "image_audit"
sys.path.insert(0, str(SKILL / "scripts"))
from audit_web import contrast  # noqa: E402

TOLERANCE = 0.3
LOW_1X = 0.12  # share of the true ratio
TEXTS = [  # text color, background, size, weight
    ("#767676", "#FFFFFF", 16, 400), ("#949494", "#FFFFFF", 14, 400), ("#FFFFFF", "#6750A4", 14, 500),
    ("#1D1B20", "#E8DEF8", 16, 400), ("#9E9E9E", "#1D1B20", 12, 400), ("#CAC4D0", "#FFFFFF", 24, 400),
    ("#6750A4", "#FEF7FF", 22, 400), ("#49454F", "#F3EDF7", 11, 500), ("#EEEEEE", "#FFFFFF", 16, 400),
]
TWO_TONES = [("#777777", "#FFFFFF", "#1D1B20"), ("#EEEEEE", "#FFFFFF", "#000000")]  # the second faint on one half
TARGETS = [(32, 32, "target-m3"), (20, 20, "target-wcag"), (160, 48, None)]

PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
body { margin: 0; padding: 16px; font-family: -apple-system, system-ui, sans-serif; background: #FFFFFF; }
.row { padding: 8px 12px; margin-bottom: 8px; }
.two { padding: 8px 12px; width: 320px; margin-bottom: 8px; }
button { border: 0; border-radius: 8px; background: #E8DEF8; margin-right: 12px; }
</style></head><body>
%s
%s
<div class="row"><svg id="icon" width="24" height="24" viewBox="0 0 24 24"><path fill="#79747E" d="M12 2 2 22h20z"/></svg></div>
<div class="row">%s</div>
</body></html>"""


def run(scale: int):
    """Photograph the page at `scale`, audit the picture; the measured items, the truth and the target rules."""
    out = OUT / f"{scale}x"
    out.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(f'<div class="row" style="background:{bg}"><span id="t{i}" style="color:{fg};font-size:{s}px;font-weight:{w}">'
                     f"Sample text {i} at {s} px</span></div>" for i, (fg, bg, s, w) in enumerate(TEXTS))
    buttons = "".join(f'<button id="b{i}" style="width:{w}px;height:{h}px"></button>' for i, (w, h, _) in enumerate(TARGETS))
    twos = "\n".join(f'<div class="two" style="background: linear-gradient(90deg, {a} 50%, {b} 50%)"><span id="two{i}" '
                     f'style="color: {fg}; font-size: 16px">Text across a two-tone background, left and right</span></div>'
                     for i, (fg, a, b) in enumerate(TWO_TONES))
    html = PAGE % (rows, twos, buttons)
    (out / "page.html").write_text(html)
    box = """([id, s]) => { const el = document.getElementById(id); const r0 = el.getBoundingClientRect();
      let r = r0; if (el.tagName === 'SPAN') { const g = document.createRange(); g.selectNodeContents(el); r = g.getBoundingClientRect(); }
      return [r.left * s, r.top * s, r.width * s, r.height * s].map(Math.round); }"""
    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="chrome", headless=True)
        pg = b.new_page(viewport={"width": 480, "height": 900}, device_scale_factor=scale)
        pg.goto((out / "page.html").as_uri())
        pg.evaluate("document.fonts.ready")
        at = lambda el: pg.evaluate(box, [el, scale])  # noqa: E731
        items = [{"label": f"t{i}", "kind": "text", "box": at(f"t{i}"), "large": s >= 24} for i, (_, _, s, _) in enumerate(TEXTS)]
        items += [{"label": f"two{i}", "kind": "text", "box": at(f"two{i}")} for i in range(len(TWO_TONES))]
        items.append({"label": "icon", "kind": "icon", "box": at("icon")})
        items += [{"label": f"b{i}", "kind": "target", "box": at(f"b{i}")} for i in range(len(TARGETS))]
        pg.screenshot(path=str(out / "page.png"), full_page=True)
        b.close()
    (out / "spec.json").write_text(json.dumps({"scale": scale, "items": items}, indent=1))
    subprocess.run([sys.executable, str(SKILL / "scripts/audit_image.py"), str(out / "page.png"), str(out / "spec.json"),
                    "--out", str(out / "result")], check=True, capture_output=True)
    res = json.loads((out / "result" / "findings.json").read_text())
    measured = {m["label"]: m.get("ratio") for m in res["measured"]}
    truth = {f"t{i}": contrast(fg, bg) for i, (fg, bg, _, _) in enumerate(TEXTS)}
    for i, (fg, a, b) in enumerate(TWO_TONES):
        truth[f"two{i}"] = min(contrast(fg, a), contrast(fg, b))
    truth["icon"] = contrast("#79747E", "#FFFFFF")
    rules = {f["where"].split(" ")[0]: f["rule"] for f in res["findings"] if f["rule"].startswith("target")}
    return measured, truth, rules, (out / "result" / "audit-image.png").exists()


def main() -> int:
    problems, notes = [], []
    for scale in (2, 1):
        measured, truth, rules, pictured = run(scale)
        for k, v in truth.items():
            m = measured.get(k)
            if m is None:
                problems.append(f"{scale}x {k}: not measured")
            elif scale == 2 and abs(m - v) > TOLERANCE:
                problems.append(f"2x {k} {m} vs {v:.2f}")
            elif scale == 1 and (m > v + 0.05 or m < v * (1 - LOW_1X)):
                problems.append(f"1x {k} {m} vs {v:.2f}")
        problems += [f"{scale}x b{i}: {rules.get(f'b{i}')} (want {want})" for i, (_, _, want) in enumerate(TARGETS) if rules.get(f"b{i}") != want]
        if not pictured:
            problems.append(f"{scale}x: no audit picture")
        errs = {k: measured[k] - v for k, v in truth.items() if measured.get(k) is not None}
        notes.append(f"{scale}x largest error {max(errs.values(), key=abs):+.2f}")
    ok = not problems
    print(f"CHECK 10 {'PASS' if ok else 'FAIL'} picture-only audit: {len(TEXTS) + len(TWO_TONES) + 1} contrast ratios at 2x within {TOLERANCE} of the truth, "
          f"at 1x never high and at most {LOW_1X:.0%} low ({'; '.join(notes)}); {len(TARGETS)} targets in the right list"
          + (f"; {'; '.join(problems)}" if problems else ""))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
