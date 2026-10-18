"""Pixel measurements shared by the web audit and the picture audit: the WCAG contrast formula, the reading of text
or an icon against its background inside a box of a screenshot, and numbered markers drawn onto a picture.

Reading a box: it is cut into vertical stripes about as wide as the box is tall. In each stripe the most common color
is the background and the ink farthest from it (the glyphs' cores, not their soft edges) is the foreground, so text
over a photo or a gradient is judged against what is behind each part of it; the lowest stripe counts. A stripe whose
ink is fainter than 1.5:1 is matched against the foreground found in the box's other stripes; a box with no clear ink
anywhere is searched for faint ink as a whole.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

COLORS = {"broken": "#D32F2F", "differs": "#E65100"}
FONTS = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FAINT = 12  # levels on a channel: closer to the background than this is the background


def _lin(c: float) -> float:
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(hex_color: str) -> float:
    r, g, b = rgb(hex_color)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def hexc(c) -> str:
    return "#{:02X}{:02X}{:02X}".format(*(round(v) for v in c[:3]))


def _background(crop: Image.Image) -> tuple[list[int], str]:
    q = crop.quantize(colors=6)
    pal = q.getpalette()
    _, i = max(q.getcolors())
    base = pal[i * 3:i * 3 + 3]
    return base, hexc(base)


def _cores(ink: list[tuple[float, int, tuple]], total: int) -> str:
    """The mean color of the ink pixels farthest from the background, 30% of them: the glyphs' cores."""
    core, count = [], 0
    for _, n, c in reversed(ink):
        core.append((n, c))
        count += n
        if count >= max(3, total * 0.3):
            break
    return hexc([sum(n * c[k] for n, c in core) / count for k in range(3)])


def stripe(img: Image.Image, box, fg_hint: str | None = None) -> tuple[float, str, str, bool] | None:
    """(ratio, foreground, background, faint) in one stripe; None when it holds no ink (the gap between words).
    With `fg_hint`, a stripe without clear ink is checked for that foreground faintly drawn on its background."""
    crop = img.crop(box)
    base, bg = _background(crop)
    colors = crop.getcolors(1 << 20)
    ink = sorted((contrast(hexc(c), bg), n, c) for n, c in colors if contrast(hexc(c), bg) >= 1.5)
    total = sum(n for _, n, _ in ink)
    if total >= 6:
        fg = _cores(ink, total)
        return contrast(fg, bg), fg, bg, False
    if fg_hint and max(abs(a - b) for a, b in zip(rgb(fg_hint), base)) >= FAINT:
        near = sum(n for n, c in colors if max(abs(c[k] - rgb(fg_hint)[k]) for k in range(3)) < FAINT)
        if near >= max(6, 0.01 * sum(n for n, _ in colors)):
            return contrast(fg_hint, bg), fg_hint, bg, True
    return None


def faint(img: Image.Image, box: list[int]) -> tuple[float, str, str] | None:
    """Ink fainter than 1.5:1 across a whole box: the colors at least FAINT levels away from the background on a
    channel, covering 1% to 60% of the box; their cores against the background. None when there is none."""
    x, y, w, h = box
    crop = img.crop((x, y, x + w, y + h))
    base, bg = _background(crop)
    colors = crop.getcolors(1 << 20)
    far = sorted((contrast(hexc(c), bg), n, c) for n, c in colors if max(abs(c[k] - base[k]) for k in range(3)) >= FAINT)
    total, share = sum(n for n, _ in colors), sum(n for _, n, _ in far)
    if not far or not 0.01 <= share / total <= 0.6:
        return None
    fg = _cores(far, share)
    return contrast(fg, bg), fg, bg


def measure_contrast(img: Image.Image, box: list[int]) -> dict | None:
    """The lowest stripe's ratio in a box [x, y, w, h] of image pixels, with the median; None when no ink is found."""
    x, y, w, h = [round(v) for v in box]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(img.width, x + w), min(img.height, y + h)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None
    step = max(8, y1 - y0)
    spans = [(sx, min(sx + step, x1)) for sx in range(x0, x1, step)]
    rows = [(stripe(img, (a, y0, b, y1)), a) for a, b in spans]
    clear = [(r, a) for r, a in rows if r]
    if clear:
        # The foreground most stripes agree on; stripes without clear ink are checked for it, drawn faintly.
        hint = sorted(clear, key=lambda t: t[0][0])[len(clear) // 2][0][1]
        rows = clear + [(stripe(img, (a, y0, b, y1), hint), a) for (r, a), (_, b) in zip(rows, spans) if not r]
        rows = [(r, a) for r, a in rows if r]
    else:
        f = faint(img, [x0, y0, x1 - x0, y1 - y0])
        if not f:
            return None
        return {"ratio": round(f[0], 2), "fg": f[1], "bg": f[2], "at_x": x0, "stripes": 0, "median": round(f[0], 2), "faint": True}
    (ratio, fg, bg, is_faint), at = min(rows, key=lambda t: t[0][0])
    ratios = sorted(r[0] for r, _ in rows)
    return {"ratio": round(ratio, 2), "fg": fg, "bg": bg, "at_x": at, "stripes": len(rows),
            "median": round(ratios[len(ratios) // 2], 2), "faint": is_faint}


def draw_markers(img: Image.Image, marks: list[dict], scale: float, path: Path):
    """A numbered tag and an outline for each mark {n, list, box: [x, y, w, h] in image pixels}; tags on one spot step
    sideways instead of hiding each other. Drawn on the picture itself, so nothing on the page (a modal dialog in the
    browser's top layer, a fixed bar) can cover them."""
    out = img.convert("RGB")
    d = ImageDraw.Draw(out)
    size = max(12, round(12 * scale))
    font = next((ImageFont.truetype(f, size) for f in FONTS if Path(f).exists()), None) or ImageFont.load_default(size=size)
    line, tag_h = max(2, round(2 * scale)), round(20 * scale)
    placed = []
    for m in marks:
        x, y, w, h = m["box"]
        c = COLORS[m["list"]]
        d.rectangle((x - line, y - line, x + w + line, y + h + line), outline=c, width=line)
        tx, ty = max(0, x - tag_h // 2), max(0, y - tag_h // 2)
        while any(abs(px - tx) < tag_h * 1.3 and abs(py - ty) < tag_h * 1.1 for px, py in placed):
            tx += round(tag_h * 1.4)
        placed.append((tx, ty))
        text = str(m["n"])
        tw = max(tag_h, d.textlength(text, font=font) + tag_h * 0.5)
        d.rounded_rectangle((tx, ty, tx + tw, ty + tag_h), radius=tag_h // 2, fill=c)
        d.text((tx + tw / 2, ty + tag_h / 2), text, font=font, fill="#FFFFFF", anchor="mm")
    out.save(path)
