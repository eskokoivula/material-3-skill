"""All checks of the material-3 skill. Usage: python3 tests/run_all.py [--refresh-flutter]

1-3  the color engine against Google's values (tests/test_color.mjs)
4-6  the web audit against known pages, and against axe-core (tests/test_audit.py)
7    the Flutter scan on an invented sample app (tests/test_flutter_scan.py)
8    the prototype template in Chrome and WebKit (tests/test_prototype.py) and its audit (8b, in test_audit.py)
9    the generated Dart theme under flutter analyze (tests/test_dart_theme.py; needs a Flutter SDK)
10   the picture-only audit against known colors and sizes (tests/test_image_audit.py)
--refresh-flutter re-runs Flutter's own ColorScheme.fromSeed into tests/fixtures/flutter-fromseed.json first.
Takes a few minutes: the audit opens real browsers. Run it at nice 20 when the Mac is in use.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(cmd, cwd=None, env=None):
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.startswith(("CHECK", "INFO"))]
    if p.returncode and not any(" FAIL " in l for l in lines):
        lines.append(f"CHECK ? FAIL {Path(str(cmd[1])).name} exited {p.returncode}: {(p.stderr or p.stdout).strip().splitlines()[-1:]}")
    return lines


def main() -> int:
    if "--refresh-flutter" in sys.argv:
        env = dict(os.environ, M3_REF_OUT=str(HERE / "fixtures/flutter-fromseed.json"))
        subprocess.run(["flutter", "test"], cwd=HERE / "flutter_ref", env=env, check=True)
    lines = []
    lines += run(["node", str(HERE / "test_color.mjs")])
    lines += run([sys.executable, str(HERE / "test_audit.py")])
    lines += run([sys.executable, str(HERE / "test_flutter_scan.py")])
    lines += run([sys.executable, str(HERE / "test_prototype.py")])
    lines += run([sys.executable, str(HERE / "test_dart_theme.py")])
    lines += run([sys.executable, str(HERE / "test_image_audit.py")])
    order = lambda l: (re.match(r"CHECK (\d+)", l) and int(re.match(r"CHECK (\d+)", l).group(1))) or 99
    lines.sort(key=order)
    for l in lines:
        print(l)
    failed = [l for l in lines if " FAIL " in l]
    print(f"\n{len([l for l in lines if l.startswith('CHECK')]) - len(failed)} passed, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
