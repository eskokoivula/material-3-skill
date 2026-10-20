"""Rebuild the README's before-and-after example. Usage, from the skill folder:

  python3 examples/before-after/build.py

1. Refreshes the after/ prototype from brand.json (scripts/prototype.mjs keeps after/index.html).
2. Audits before.html and every after screen, light and dark, with scripts/audit_web.py (into out/). This takes
   several minutes: each audit opens Chrome many times.
3. Takes screenshots in headless Chrome at a phone size (390x844) and a desktop size (1440x900).
4. Puts the pictures side by side in docs/images/ and prints the audit counts the README quotes.
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent
OUT = HERE / "out"
IMAGES = SKILL / "docs" / "images"
PHONE, DESKTOP = (390, 844), (1440, 900)
AFTER = HERE / "after" / "index.html"
AFTER_SCREENS = ("invoices", "invoice", "clients", "reports", "settings")
SCREENS = {
    "before": lambda theme: (HERE / "before.html").as_uri(),
    "after": lambda theme: f"{AFTER.as_uri()}?frame=full&theme={theme}&chrome=0#invoices",
}
INK, PAPER, EDGE = (29, 27, 32), (255, 255, 255), (220, 220, 224)


def audit(name: str, target: str) -> dict:
    out = OUT / f"audit-{name}"
    subprocess.run([sys.executable, str(SKILL / "scripts" / "audit_web.py"), target, "--out", str(out)], check=True,
                   stdout=subprocess.DEVNULL)
    return json.loads((out / "findings.json").read_text())


def counts(findings: dict) -> dict:
    result = {}
    for f in findings["findings"]:
        result[f["list"]] = result.get(f["list"], 0) + 1
    return result


def shoot(page, url: str, size: tuple[int, int], path: Path) -> None:
    page.set_viewport_size({"width": size[0], "height": size[1]})
    page.goto(url, wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(400)
    page.screenshot(path=str(path))


def font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Helvetica.ttc", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def board(panels: list[tuple[str, Path]], path: Path, panel_width: int, row: bool = True, gap: int = 48) -> None:
    """Pictures of one width in a row (or a column) on a white board, each with a caption above it."""
    pics = []
    for _, p in panels:
        im = Image.open(p).convert("RGB")
        pics.append(im.resize((panel_width, round(im.height * panel_width / im.width)), Image.LANCZOS))
    head, pad = 64, 40
    if row:
        width = panel_width * len(pics) + gap * (len(pics) - 1) + pad * 2
        height = max(im.height for im in pics) + head + pad
    else:
        width = panel_width + pad * 2
        height = sum(im.height + head for im in pics) + gap * (len(pics) - 1) + pad
    canvas = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(canvas)
    x = y = 0
    for (caption, _), im in zip(panels, pics):
        left, top = pad + x, head + y
        draw.text((left, top - 44), caption, fill=INK, font=font(26))
        canvas.paste(im, (left, top))
        draw.rectangle([left - 1, top - 1, left + im.width, top + im.height], outline=EDGE)
        if row:
            x += panel_width + gap
        else:
            y += im.height + head + gap
    canvas.save(path, optimize=True)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)
    subprocess.run(["node", str(SKILL / "scripts" / "prototype.mjs"), str(HERE / "brand.json"), "--out",
                    str(HERE / "after")], check=True, stdout=subprocess.DEVNULL)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(device_scale_factor=2)
        for name, url in SCREENS.items():
            for theme in (("light",) if name == "before" else ("light", "dark")):
                for label, size in (("phone", PHONE), ("desktop", DESKTOP)):
                    shoot(page, url(theme), size, OUT / f"{name}-{label}-{theme}.png")
        browser.close()

    results = {"before": audit("before", str(HERE / "before.html"))}
    for screen in AFTER_SCREENS:
        for theme in ("light", "dark"):
            results[f"after-{screen}-{theme}"] = audit(f"after-{screen}-{theme}",
                                                       f"{AFTER}?frame=full&theme={theme}#{screen}")
    for name, findings in results.items():
        print(name, counts(findings))
    after = [counts(f).get("broken", 0) for name, f in results.items() if name.startswith("after")]
    print(f"after: {sum(after)} Broken findings in {len(after)} audits")

    board([("Before", OUT / "before-phone-light.png"),
           ("Before, audited", OUT / "audit-before" / "audit-390x844.png"),
           ("After, light", OUT / "after-phone-light.png"),
           ("After, dark", OUT / "after-phone-dark.png")],
          IMAGES / "before-after-phone.png", panel_width=390)
    board([("Before", OUT / "before-desktop-light.png"), ("After", OUT / "after-desktop-light.png")],
          IMAGES / "before-after-desktop.png", panel_width=1200, row=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
