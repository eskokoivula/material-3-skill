"""Check 7: the Flutter scan on an invented sample app (tests/fixtures/sample-app) reports what was planted in it.

The app's theme sets 9 of the 49 color roles in Google's list and leaves the surface container ladder unset; it uses
BottomNavigationBar once (lib/widgets/bottom_nav.dart:23), and the doc comment and the string that name it must not
count. Two looping animations ignore reduced motion (pulse_ring.dart:17, hint_screen.dart:20; reward_screen.dart checks
it), the app reads only disableAnimations (never iOS's reduceMotion), and portrait is locked in two places
(main.dart:10, hint_screen.dart:18; DeviceOrientation.values is an unlock). Of four icon buttons only the one with
no tooltip, no Semantics label and no icon semanticLabel is unlabelled (actions.dart:16).
Prints "CHECK 7 PASS|FAIL <detail>".
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent


def main() -> int:
    out = HERE / "out" / "flutter-sample"
    subprocess.run([sys.executable, str(SKILL / "scripts/audit_flutter.py"), str(HERE / "fixtures/sample-app"),
                    "--out", str(out)], check=True, capture_output=True)
    res = json.loads((out / "findings.json").read_text())
    by_rule = {f["rule"]: f for f in res["findings"]}
    roles = by_rule.get("roles-unset", {}).get("data", {}).get("set", [])
    bnb = by_rule.get("m2-widget", {})
    loops = by_rule.get("motion-reduce-ignored", {}).get("where", "")
    locks = by_rule.get("orientation-locked", {})
    problems = []
    if len(roles) != 9:
        problems.append(f"roles set {len(roles)}, expected 9")
    if bnb.get("data", {}).get("uses") != 1 or "lib/widgets/bottom_nav.dart:23" not in bnb.get("where", ""):
        problems.append(f"BottomNavigationBar: {bnb.get('where')}, expected one use at lib/widgets/bottom_nav.dart:23")
    if "surface-roles-unset" not in by_rule or by_rule["surface-roles-unset"]["list"] != "broken":
        problems.append("the unset surface ladder was not reported as Broken")
    if "pulse_ring.dart:17" not in loops or "hint_screen.dart:20" not in loops or "reward_screen" in loops:
        problems.append(f"looping animations without reduced motion: {loops or 'none'}")
    if "ios-reduce-motion-unread" not in by_rule:
        problems.append("reading only disableAnimations was not reported")
    if locks.get("where") != "lib/main.dart:10, lib/screens/hint_screen.dart:18":
        problems.append(f"orientation locks: {locks.get('where')}")
    icons = by_rule.get("icon-button-unlabelled", {}).get("where")
    if icons != "lib/widgets/actions.dart:16":
        problems.append(f"unlabelled icon buttons: {icons}")
    ok = not problems
    print(f"CHECK 7 {'PASS' if ok else 'FAIL'} invented sample app: {len(roles)} of 49 roles set; BottomNavigationBar "
          f"{bnb.get('data', {}).get('uses')} use at {bnb.get('where')}; unset surface ladder reported as Broken; "
          f"2 loops without reduced motion, iOS Reduce Motion unread, portrait locked in 2 places, 1 of 4 icon buttons unlabelled"
          + (f"; {'; '.join(problems)}" if problems else ""))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
