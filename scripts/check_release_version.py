#!/usr/bin/env python3
"""Ensure the four evgraph packages stay on one lockstep version.

Each package must also pin its evgraph dependencies to exactly that version, so
installing evgraph-cli==X.Y.Z can never pull a different evgraph release.

Usage:
    python scripts/check_release_version.py           # versions must match each other
    python scripts/check_release_version.py v0.1.1    # also must match this tag
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ("evgraph-core", "evgraph-rules", "evgraph", "evgraph-cli")
VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
DEPENDENCIES_RE = re.compile(r"^dependencies\s*=\s*\[(.*?)\]", re.MULTILINE | re.DOTALL)
INTERNAL_DEP_RE = re.compile(r'"(evgraph(?:-core|-rules|-cli)?)\s*([^"]*)"')


def read_version(pyproject: Path) -> str:
    text = pyproject.read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if match is None:
        raise SystemExit(f"No version field in {pyproject}")
    return match.group(1)


def internal_pins(pyproject: Path) -> dict[str, str]:
    """{dependency name: version specifier} for the evgraph packages a pyproject depends on."""
    match = DEPENDENCIES_RE.search(pyproject.read_text(encoding="utf-8"))
    if match is None:
        return {}
    return {name: spec.strip() for name, spec in INTERNAL_DEP_RE.findall(match.group(1))}


def main(argv: list[str]) -> int:
    expected = argv[1].removeprefix("v") if len(argv) == 2 else None
    if len(argv) > 2:
        print("Usage: check_release_version.py [vX.Y.Z]", file=sys.stderr)
        return 2

    versions: dict[str, str] = {}
    for name in PACKAGES:
        path = ROOT / "reference" / "python" / name / "pyproject.toml"
        versions[name] = read_version(path)

    unique = set(versions.values())
    if len(unique) != 1:
        print("Package versions are not lockstep:", file=sys.stderr)
        for name, ver in versions.items():
            print(f"  {name}: {ver}", file=sys.stderr)
        return 1

    actual = unique.pop()
    loose = []
    for name in PACKAGES:
        path = ROOT / "reference" / "python" / name / "pyproject.toml"
        for dep, spec in internal_pins(path).items():
            if spec != f"=={actual}":
                loose.append(f"  {name} depends on {dep}{spec or ' (unpinned)'}, expected {dep}=={actual}")
    if loose:
        print("Internal dependencies are not pinned to the lockstep version:", file=sys.stderr)
        print("\n".join(loose), file=sys.stderr)
        return 1

    if expected is not None and actual != expected:
        print(
            f"Tag version {expected!r} does not match package version {actual!r}",
            file=sys.stderr,
        )
        return 1

    print(f"All packages at version {actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
