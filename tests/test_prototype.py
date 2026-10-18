"""Check 8 (part 1): the prototype template works in Chrome and WebKit at a phone and a desktop size.

Every screen is reached by clicking, nothing scrolls sideways, the light and dark switch changes the surface,
a dialog opens with focus inside and everything behind it inert and closes on Escape, segmented buttons and tabs
select (tabs with the arrow keys too), and reduced motion removes movement from transitions.
Prints "CHECK 8a PASS|FAIL <detail>".
"""
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SIZES = [("phone", 375, 812, "full"), ("desktop", 1440, 900, "desktop")]

VISIBLE_TARGETS = """() => [...document.querySelectorAll('#app [href^="#"], #app [data-go]')]
  .filter((el) => el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden')
  .map((el) => el.dataset.go ?? el.getAttribute('href').slice(1))"""

NO_SIDEWAYS_SCROLL = """() => {
  const doc = document.scrollingElement;
  const bad = [];
  if (doc.scrollWidth > window.innerWidth + 1) bad.push(`page ${doc.scrollWidth}>${window.innerWidth}`);
  for (const s of document.querySelectorAll('.screen:not([hidden])')) {
    if (s.scrollWidth > s.clientWidth + 1) bad.push(`${s.dataset.screen} ${s.scrollWidth}>${s.clientWidth}`);
  }
  return bad;
}"""


def build() -> Path:
    out = HERE / "out" / "prototype"
    subprocess.run(["node", str(SKILL / "scripts/prototype.mjs"), str(HERE / "fixtures/baseline.tokens.json"),
                    "--out", str(out), "--force"], check=True, capture_output=True)
    return out / "index.html"


def check_size(browser, url: str, label: str, w: int, h: int, frame: str) -> list[str]:
    problems = []
    ctx = browser.new_context(viewport={"width": w, "height": h})
    page = ctx.new_page()
    page.goto(f"{url}?frame={frame}&theme=light#home", wait_until="load")
    page.wait_for_timeout(300)
    screens = page.evaluate("m3proto.screens()")
    reached, frontier = {"home"}, ["home"]
    while frontier:
        start = frontier.pop(0)
        page.evaluate(f"m3proto.show('{start}', 'fade', {{ instant: true }})")
        for target in sorted(set(page.evaluate(VISIBLE_TARGETS)) - reached):
            if target not in screens:
                continue
            page.evaluate(f"m3proto.show('{start}', 'fade', {{ instant: true }})")
            page.locator(f'#app [href="#{target}"]:visible, #app [data-go="{target}"]:visible').first.click()
            page.wait_for_timeout(700)
            synced = page.evaluate("document.querySelector('.proto-bar [name=screen]')?.value === m3proto.current()")
            if not synced:
                problems.append(f"{label}: the screen menu did not follow the move to {target}")
            if page.evaluate("m3proto.current()") == target:
                reached.add(target)
                frontier.append(target)
            else:
                problems.append(f"{label}: clicking towards {target} from {start} did not arrive")
    missing = set(screens) - reached
    if missing:
        problems.append(f"{label}: not reachable by clicking: {', '.join(sorted(missing))}")
    for s in screens:
        page.evaluate(f"m3proto.show('{s}', 'fade', {{ instant: true }})")
        bad = page.evaluate(NO_SIDEWAYS_SCROLL)
        if bad:
            problems.append(f"{label}: sideways scroll on {s}: {bad}")
    light = page.evaluate("getComputedStyle(document.getElementById('app')).backgroundColor")
    page.select_option(".proto-bar [name=theme]", "dark")
    dark = page.evaluate("getComputedStyle(document.getElementById('app')).backgroundColor")
    if light == dark:
        problems.append(f"{label}: the theme switch did not change the surface ({light})")
    opener = page.locator("#app [data-open^='dialog']:visible").first
    if opener.count() == 0:
        page.evaluate("m3proto.show('feedback', 'fade', { instant: true })")
        opener = page.locator("#app [data-open^='dialog']:visible").first
    opener.click()
    page.wait_for_timeout(400)
    inside = page.evaluate("!!document.activeElement.closest('.md-dialog')")
    reachable = page.evaluate("""() => [...document.querySelectorAll('a[href], button, input, select, textarea, [tabindex]')]
      .filter((el) => el.getClientRects().length && !el.closest('.md-scrim:not([hidden])') && !el.closest('[inert]')).length""")
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
    closed = page.evaluate("[...document.querySelectorAll('.md-scrim')].every((s) => s.hidden)")
    restored = page.evaluate("!document.querySelector('[inert]')")
    if not inside or reachable or not closed or not restored:
        problems.append(f"{label}: dialog focus inside={inside}, {reachable} controls reachable behind it, "
                        f"closed on Escape={closed}, inert lifted={restored}")
    page.evaluate("m3proto.show('components', 'fade', { instant: true })")
    page.locator("#app .md-segmented__button:has-text('Week')").click()
    pressed = page.evaluate("[...document.querySelectorAll('#app .md-segmented__button')].map((b) => b.getAttribute('aria-pressed')).join()")
    page.locator("#app [role=tab]:has-text('Second')").click()
    page.keyboard.press("ArrowRight")
    selected = page.evaluate("[...document.querySelectorAll('#app [role=tab]')].map((t) => t.getAttribute('aria-selected')).join()")
    if pressed != "false,true,false" or selected != "false,false,true":
        problems.append(f"{label}: segmented {pressed}, tabs {selected}")
    ctx.close()

    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(f"{url}?frame={frame}&theme=light#home", wait_until="load")
    page.wait_for_timeout(300)
    page.evaluate("""() => {
      window.__moves = [];
      const orig = Element.prototype.animate;
      Element.prototype.animate = function (k, o) {
        const frames = Array.isArray(k) ? k : [k];
        if (frames.some((f) => f.transform && f.transform !== 'none')) window.__moves.push(this.className);
        return orig.call(this, k, o);
      };
    }""")
    page.locator('#app [href="#detail"]:visible').first.click()
    page.wait_for_timeout(400)
    page.locator('#app [data-go="home"]:visible').first.click()
    page.wait_for_timeout(400)
    moves = page.evaluate("window.__moves")
    if moves:
        problems.append(f"{label}: movement under reduced motion: {moves}")
    ctx.close()
    return problems


def main() -> int:
    url = build().as_uri()
    problems = []
    with sync_playwright() as p:
        engines = [("chrome", lambda: p.chromium.launch(channel="chrome", headless=True)),
                   ("webkit", lambda: p.webkit.launch(headless=True))]
        for name, launch in engines:
            browser = launch()
            for label, w, h, frame in SIZES:
                problems += [f"{name} {x}" for x in check_size(browser, url, label, w, h, frame)]
            browser.close()
    ok = not problems
    print(f"CHECK 8a {'PASS' if ok else 'FAIL'} template in Chrome and WebKit at 375x812 and 1440x900: "
          + ("every screen reached by click, no sideways scroll, theme switch, dialog focus, inert background and Escape, "
             "segmented buttons and tabs select, no movement under reduced motion"
             if ok else "; ".join(problems)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
