#!/usr/bin/env python3
"""Build wheels and sdists for every evgraph package into ./dist/<name>/."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ("evgraph-core", "evgraph-rules", "evgraph", "evgraph-cli")
DIST = ROOT / "dist"


def main() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    for name in PACKAGES:
        src = ROOT / "reference" / "python" / name
        out = DIST / name
        out.mkdir()
        print(f"Building {name} from {src} -> {out}")
        subprocess.check_call(
            [sys.executable, "-m", "build", "--outdir", str(out), str(src)]
        )

    artifacts = sorted(path for path in DIST.rglob("*") if path.is_file())
    if not artifacts:
        print("No distributions were produced", file=sys.stderr)
        return 1

    print("Built:")
    for path in artifacts:
        print(f"  {path.relative_to(DIST)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
