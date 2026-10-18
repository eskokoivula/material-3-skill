"""Checks 4, 4b, 5, 6 and 8b: the web audit against pages whose answers are known.

4. Recall: every fault planted in fixtures/audit/faults.html is found, in the right list, and none of the
   findings the page is built to tempt (expected.json, must_not) is made.
4b. With a modal dialog open (fixtures/audit/modal.html), the dialog is measured and the page behind it is not.
5. No false alarms: the template's screens (built only from m3.css and Google's tokens) have zero Broken findings;
   they are opened as a file path with a query and a hash.
6. Cross-check: the audit's text contrast ratios agree with axe-core's within 0.1 on both pages.
8b. The same zero-Broken result is the template's audit half of check 8.
Prints "CHECK <n> PASS|FAIL <detail>".
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
OUT = HERE / "out" / "audit"
SCREENS = ["home", "detail", "components", "feedback"]


def audit(target: str, out: Path) -> dict:
    subprocess.run([sys.executable, str(SKILL / "scripts/audit_web.py"), target, "--out", str(out)],
                   check=True, capture_output=True, text=True)
    return json.loads((out / "findings.json").read_text())


def matches(f: dict, e: dict) -> bool:
    return (f["rule"] == e["rule"] and (not e.get("list") or f["list"] == e["list"])
            and (not e.get("match") or e["match"] in f["where"]) and (not e.get("what_has") or e["what_has"] in f["what"]))


def main() -> int:
    ok_all = True
    faults = audit(str(HERE / "fixtures/audit/faults.html"), OUT / "faults")
    expected = json.loads((HERE / "fixtures/audit/expected.json").read_text())
    missed = []
    for e in expected["faults"]:
        hit = [f for f in faults["findings"] if matches(f, e)]
        if e.get("rect_max_y") is not None:
            hit = [f for f in hit if f["rects"] and all(r["y"] <= e["rect_max_y"] for r in f["rects"].values())]
        if e.get("has_rect"):
            hit = [f for f in hit if f["rects"]]
        if not hit:
            missed.append(f"{e['rule']} {e.get('match') or e.get('what_has') or ''} ({e['list']})")
    wrong = [f"{e['rule']} {e.get('match') or e.get('what_has')}" for e in expected["must_not"]
             if any(matches(f, e) for f in faults["findings"])]
    ok = not missed and not wrong
    ok_all &= ok
    n = len(expected["faults"])
    print(f"CHECK 4 {'PASS' if ok else 'FAIL'} {n - len(missed)}/{n} planted faults found in the right list; "
          f"{len(wrong)} of {len(expected['must_not'])} tempting non-faults reported"
          + (f"; missed: {', '.join(missed)}" if missed else "") + (f"; wrongly reported: {', '.join(wrong)}" if wrong else ""))

    modal = audit(str(HERE / "fixtures/audit/modal.html"), OUT / "modal")
    inside_f = next((f for f in modal["findings"] if f["rule"] == "contrast" and "p.inside" in f["where"]), None)
    inside = inside_f is not None
    # The marker sits on top of the dialog in the picture (a modal dialog is in the browser's top layer).
    marked = False
    if inside_f and inside_f["rects"].get("390x844"):
        from PIL import Image
        r = inside_f["rects"]["390x844"]
        img = Image.open(OUT / "modal" / "audit-390x844.png").convert("RGB")
        edge = [img.getpixel((int(r["x"] + i), max(0, int(r["y"]) - 2))) for i in range(int(r["w"]))]
        marked = any(abs(c[0] - 0xD3) < 20 and abs(c[1] - 0x2F) < 20 and abs(c[2] - 0x2F) < 20 for c in edge)
    behind = [f"{f['rule']} {f['where']}" for f in modal["findings"] if "behind" in f["where"]]
    scoped = all(fa["scope"] for fa in modal["facts"])
    ok = inside and not behind and scoped and marked
    ok_all &= ok
    print(f"CHECK 4b {'PASS' if ok else 'FAIL'} open dialog: its low contrast {'found' if inside else 'missed'} and "
          f"{'marked on top of the dialog' if marked else 'NOT marked visibly'}; "
          f"{len(behind)} findings behind it; scope {'set' if scoped else 'missing'}" + (f"; {'; '.join(behind[:3])}" if behind else ""))

    proto = HERE / "out" / "prototype" / "index.html"
    subprocess.run(["node", str(SKILL / "scripts/prototype.mjs"), str(HERE / "fixtures/baseline.tokens.json"),
                    "--out", str(proto.parent), "--force"], check=True, capture_output=True)
    broken, cross = [], list(faults["crosscheck"])
    for s in SCREENS:
        res = audit(f"{proto}?frame=full&theme=light#{s}", OUT / f"clean-{s}")
        broken += [f"{s}: {f['what']} at {f['where']}" for f in res["findings"] if f["list"] == "broken"]
        cross += res["crosscheck"]
    ok = not broken
    ok_all &= ok
    print(f"CHECK 5 {'PASS' if ok else 'FAIL'} {len(SCREENS)} template screens at 390x844 and 1440x900: {len(broken)} Broken findings"
          + (f"; {'; '.join(broken[:5])}" if broken else ""))
    print(f"CHECK 8b {'PASS' if ok else 'FAIL'} the template's audit: {len(broken)} Broken findings")

    worst = max((abs(c["ours"] - c["axe"]) for c in cross), default=None)
    ok = worst is not None and worst <= 0.1
    ok_all &= ok
    print(f"CHECK 6 {'PASS' if ok else 'FAIL'} {len(cross)} text contrast ratios measured by both the audit and axe-core; "
          f"largest difference {worst if worst is None else round(worst, 2)}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
