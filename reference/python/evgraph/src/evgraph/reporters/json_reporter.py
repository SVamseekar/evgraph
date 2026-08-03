"""Plain JSON reporter matching EGS §5 / RES §6 serialization. No HTML/PDF/SARIF (Stage 3)."""

from __future__ import annotations

import json
from typing import Any

from evgraph_core import EvidenceGraph, Finding, finding_to_dict, graph_to_dict


def to_dict(graph: EvidenceGraph, findings: list[Finding]) -> dict[str, Any]:
    return {
        "graph": graph_to_dict(graph),
        "findings": [finding_to_dict(f) for f in findings],
    }


def to_json(graph: EvidenceGraph, findings: list[Finding], *, indent: int | None = 2) -> str:
    return json.dumps(to_dict(graph, findings), indent=indent)
