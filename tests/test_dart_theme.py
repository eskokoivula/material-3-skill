"""Check 9: the Dart theme the skill writes passes `flutter analyze --fatal-infos` with no issues, under the lints
`flutter create` sets up (package:flutter_lints, from the local pub cache).

Two themes: the baseline, and the sample brand (tests/fixtures/sample-app; dark only, locked colors) with every option
switched on — a variable font, a type size override and a corner override. Each is written into a copy of tests/flutter_ref with a
file that builds a ThemeData from it. A planted file with an unnecessary import proves the lints are on. Needs a
Flutter SDK; without one it prints INFO and passes nothing.
Prints "CHECK 9 PASS|FAIL <detail>".
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
OUT = HERE / "out" / "dart_check"

PLANTED = """import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';

/// The mistake the skill once wrote: physics.dart imported beside material.dart, which already exports it. (With only
/// SpringDescription used, either import could go and the analyzer flags neither; a Color makes physics.dart the extra.)
final SpringDescription planted = SpringDescription.withDampingRatio(mass: 1, stiffness: 380, ratio: 0.8);
const Color plantedColor = Colors.black;
"""

USE = """import 'package:flutter/material.dart';

import '{file}';

/// Builds every theme the file offers, so the analyzer checks the calls as a project would make them.
List<ThemeData> themes() => [{calls}];
"""


def main() -> int:
    if not shutil.which("flutter"):
        print("INFO check 9 skipped: no Flutter SDK on PATH")
        return 0
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(HERE / "flutter_ref", OUT, ignore=shutil.ignore_patterns(".dart_tool", "build", "pubspec.lock", "test"))
    (OUT / "lib").mkdir()
    brand = json.loads((HERE / "fixtures/sample-app/brand.tokens.json").read_text())
    brand["type"] = {**brand["type"], "brand": "O'Brien Sans", "variable": True,
                     "weights": {"regular": 450, "medium": 600, "bold": 800},
                     "scale": {"display-large": {"size": 52, "lineHeight": 60}}}
    brand["shape"] = {"medium": 10}
    configs = {"baseline": {"name": "baseline"}, "brand": brand}
    for name, config in configs.items():
        cfg = OUT / f"{name}.json"
        cfg.write_text(json.dumps(config))
        subprocess.run(["node", str(SKILL / "scripts/tokens.mjs"), str(cfg), "--out", str(OUT / name)], check=True, capture_output=True)
        shutil.copy(OUT / name / "m3_tokens.dart", OUT / "lib" / f"{name}_tokens.dart")
        schemes = ["M3Tokens.lightScheme", "M3Tokens.darkScheme"] if name == "baseline" else ["M3Tokens.darkScheme"]
        (OUT / "lib" / f"{name}_use.dart").write_text(USE.format(file=f"{name}_tokens.dart",
                                                                 calls=", ".join(f"M3Tokens.theme({s})" for s in schemes)))
    pubspec = (OUT / "pubspec.yaml").read_text()
    (OUT / "pubspec.yaml").write_text(pubspec.replace("dev_dependencies:\n", "dev_dependencies:\n  flutter_lints: ^6.0.0\n"))
    (OUT / "analysis_options.yaml").write_text("include: package:flutter_lints/flutter.yaml\n")
    (OUT / "lib" / "planted.dart").write_text(PLANTED)
    subprocess.run(["flutter", "pub", "get", "--offline"], cwd=OUT, capture_output=True, text=True)
    p = subprocess.run(["flutter", "analyze", "--fatal-infos", "lib"], cwd=OUT, capture_output=True, text=True)
    lines = [l.strip() for l in p.stdout.splitlines() if " • " in l]
    dart = (OUT / "lib" / "brand_tokens.dart").read_text().splitlines()
    body = next((l for l in dart if l.strip().startswith("bodyLarge:")), "")
    display = next((l for l in dart if l.strip().startswith("displayLarge:")), "")
    carried = "fontFamily: 'O\\'Brien Sans'" in display and "FontWeight.w500" in body and "FontVariation('wght', 450)" in body
    planted = [l for l in lines if "planted.dart" in l and "unnecessary_import" in l]
    issues = [l for l in lines if "planted.dart" not in l]
    ok = bool(planted) and not issues and carried
    print(f"CHECK 9 {'PASS' if ok else 'FAIL'} m3_tokens.dart for {len(configs)} configs (one with a variable font and "
          f"type and corner overrides): flutter analyze --fatal-infos with flutter_lints, {len(issues)} issues; "
          f"planted unnecessary import {'caught' if planted else 'NOT caught'}; a quoted font name and the brand's "
          f"weights {'carried' if carried else 'NOT carried'}"
          + (f"; {'; '.join(issues[:4])}" if issues else "") + ("" if planted else f"; {(p.stderr or p.stdout)[-300:]}"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
