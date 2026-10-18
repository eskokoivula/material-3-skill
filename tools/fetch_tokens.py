"""Download Google's machine-readable Material 3 token sources into tests/fixtures/google/.

Sources (all Google repositories):
  flutter/   flutter/flutter dev/tools/gen_defaults/data/*.json  (baseline M3 token database)
  compose/   androidx/androidx compose/material3/.../tokens/*.kt (the only source with Expressive values)
  web/       material-components/material-web tokens/versions/v0_192/_md-*.scss (the md-sys-* names)
  web-latest/ the same repo's tokens/versions/latest/sass (newest generated set: emphasized type, focus indicator)
Writes manifest.json with each directory's source URL and the latest commit that touched it.
Usage: python3 tools/fetch_tokens.py
"""
import json
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "google"
SOURCES = {
    "flutter": ("flutter/flutter", "master", "dev/tools/gen_defaults/data", lambda n: n.endswith(".json")),
    "compose": ("androidx/androidx", "androidx-main",
                "compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens",
                lambda n: n.endswith(".kt")),
    "web": ("material-components/material-web", "main", "tokens/versions/v0_192",
            lambda n: n.startswith("_md-") and n.endswith(".scss")),
    # The newest generated web set (Sass variables): emphasized type, Expressive corners, the focus indicator.
    "web-latest": ("material-components/material-web", "main", "tokens/versions/latest/sass",
                   lambda n: n.startswith(("_md-sys", "_md-ref")) and n.endswith(".scss")),
}


def get(url: str) -> bytes:
    # curl uses the system certificates; this Python build has none of its own.
    return subprocess.run(["curl", "-sfL", "-A", "material-3-skill", url], check=True, capture_output=True).stdout


def main() -> None:
    manifest = {"fetched": date.today().isoformat(), "sources": {}}
    for key, (repo, branch, path, keep) in SOURCES.items():
        listing = json.loads(get(f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"))
        commit = json.loads(get(f"https://api.github.com/repos/{repo}/commits?path={path}&sha={branch}&per_page=1"))[0]
        out = ROOT / key
        out.mkdir(parents=True, exist_ok=True)
        names = sorted(e["name"] for e in listing if e["type"] == "file" and keep(e["name"]))
        for n in names:
            (out / n).write_bytes(get(f"https://raw.githubusercontent.com/{repo}/{commit['sha']}/{path}/{n}"))
        manifest["sources"][key] = {
            "repo": repo, "path": path, "commit": commit["sha"],
            "commit_date": commit["commit"]["committer"]["date"], "files": len(names),
        }
        print(f"{key}: {len(names)} files at {commit['sha'][:10]} ({commit['commit']['committer']['date'][:10]})")
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")


if __name__ == "__main__":
    main()
