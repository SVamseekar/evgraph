"""Rule discovery via Python entry_points (importlib.metadata).

This is the one concrete extension-discovery mechanism the reference
implementation uses, built before PES was written — PES-v0.1 is extracted
from this module, not designed in advance (ADR-0002).

Only rules are discovered this way. Reporters are selected explicitly by the
caller (`report.to_markdown()`, `report.to_sarif()`), and adapters are still
constructed directly — neither has demonstrated a need for discovery yet
(see `docs/specs/PES-v0.1.md` §1.3).
"""

from __future__ import annotations

from importlib.metadata import entry_points

from evident_core import Rule

ENTRY_POINT_GROUP = "evident.rules"


def discover_rules() -> list[Rule]:
    """Instantiates every Rule registered under the "evident.rules" entry_point
    group across all installed packages, in whatever order importlib.metadata
    returns them — per RES §3.1, a Rule's return order carries no meaning, so
    discovery order is not a meaningful property either.
    """
    rules: list[Rule] = []
    for ep in entry_points(group=ENTRY_POINT_GROUP):
        rule_class = ep.load()
        rules.append(rule_class())
    return rules
