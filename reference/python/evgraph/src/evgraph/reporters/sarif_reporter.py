"""SARIF (Static Analysis Results Interchange Format) reporter, built directly
against Finding/RES. No shared reporter spec exists yet (RPS is extracted from
real reporters per ADR-0002, not designed up front).

SARIF's `level` field is used solely to preserve the structural distinction
already present in `Finding.outcome` (RES §4.2) — Evgraph does not interpret
these values as governance severity or compliance risk, and this reporter
introduces no severity concept RES doesn't already have. The mapping is a
deterministic, outcome-to-outcome translation into the nearest SARIF
vocabulary, not a judgment about how serious any given finding is: every
EXPECTATION_NOT_MET finding maps to the same SARIF level regardless of which
rule produced it or what it cites — nothing about a rule's identity or a
finding's content changes the mapping.
"""

from __future__ import annotations

from typing import Any

from evgraph_core import EvidenceGraph, Finding, Outcome

SARIF_VERSION = "2.1.0"
SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"

_OUTCOME_TO_SARIF_LEVEL = {
    Outcome.EXPECTATION_MET: "none",
    Outcome.EXPECTATION_NOT_MET: "warning",
    Outcome.INCONCLUSIVE: "note",
}


def _rule_ids(findings: list[Finding]) -> list[str]:
    seen: list[str] = []
    for f in findings:
        if f.rule_id not in seen:
            seen.append(f.rule_id)
    return seen


def _result_to_dict(finding: Finding) -> dict[str, Any]:
    return {
        "ruleId": finding.rule_id,
        "level": _OUTCOME_TO_SARIF_LEVEL[finding.outcome],
        "message": {"text": finding.statement},
        "properties": {
            "evgraphFindingId": finding.id,
            "evgraphLevel": finding.level.name,
            "evgraphOutcome": finding.outcome.value,
            "citedNodeIds": list(finding.cited_node_ids),
        },
    }


def to_sarif_dict(graph: EvidenceGraph, findings: list[Finding]) -> dict[str, Any]:
    """Renders one EvidenceGraph's findings as a SARIF 2.1.0 log."""
    rules = [{"id": rule_id} for rule_id in _rule_ids(findings)]

    return {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "evgraph",
                        "informationUri": "https://github.com/evgraph-org/evgraph",
                        "rules": rules,
                    }
                },
                "properties": {"evgraphGraphId": graph.graph_id},
                "results": [_result_to_dict(f) for f in findings],
            }
        ],
    }


def to_sarif(graph: EvidenceGraph, findings: list[Finding], *, indent: int | None = 2) -> str:
    import json

    return json.dumps(to_sarif_dict(graph, findings), indent=indent)
