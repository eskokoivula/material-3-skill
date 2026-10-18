"""Fetch pages headless with real Chrome and save their readable text.

m3.material.io renders in the browser, so plain HTTP fetches return almost nothing.
Usage: python3 tools/fetch_page.py --out DIR URL [URL ...]
Saves DIR/<slug>.txt per URL (the page's main text, then its same-site links) and prints one line per page.
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


def slug(url: str) -> str:
    p = urlparse(url)
    s = (p.netloc + p.path).strip("/").replace("/", "__")
    s = re.sub(r"[^A-Za-z0-9_.-]", "-", s) or "index"
    # A hash of the whole URL keeps apart pages whose names would collide (a query, /a/b against /a__b).
    return f"{s}--{hashlib.sha1(url.encode()).hexdigest()[:8]}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("urls", nargs="+")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    failed = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        for url in args.urls:
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(1500)
                root = page.query_selector("main") or page.query_selector("body")
                text = root.inner_text()
                host = urlparse(url).netloc
                links = page.eval_on_selector_all(
                    "main a[href], article a[href]",
                    "els => [...new Set(els.map(e => e.href.split('#')[0].split('?')[0]))]",
                )
                links = [l for l in links if urlparse(l).netloc == host]
                f = out / f"{slug(url)}.txt"
                f.write_text(f"URL: {url}\nTITLE: {page.title()}\n\n{text}\n\nLINKS:\n" + "\n".join(links) + "\n")
                print(f"ok {len(text):6d} chars  {f}")
            except Exception as e:  # keep going; report the failure
                print(f"FAIL {url}: {e}", file=sys.stderr)
                failed += 1
        browser.close()
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
