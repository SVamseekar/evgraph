"""Turns Evgraph findings into the check format Urielle already uses.

We're not inventing a new check type here — just emitting the same kind of
EVIDENCE_TYPE_VALID check Urielle's own assessor produces. We never touch
decision, confidence, readiness score, or human disposition.
"""

from __future__ import annotations

from typing import Any

from evgraph_core import Finding, Outcome


def to_urielle_sidecar_checks(findings: list[Finding] | tuple[Finding, ...]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for finding in findings:
        if finding.rule_id != "clause04-question-has-structured-evidence":
            continue
        question_id = _question_id_from_statement(finding.statement)
        status = "PASSED" if finding.outcome is Outcome.EXPECTATION_MET else "FAILED"
        if finding.outcome is Outcome.INCONCLUSIVE:
            status = "NOT_RUN"
        checks.append(
            {
                "check_id": f"CHK-{question_id}-EVGRAPH-EVIDENCE",
                "check_type": "EVIDENCE_TYPE_VALID",
                "status": status,
                "observation": finding.statement,
                "evgraph": {
                    "finding_id": finding.id,
                    "rule_id": finding.rule_id,
                    "level": finding.level.name,
                    "outcome": finding.outcome.value,
                    "cited_node_ids": list(finding.cited_node_ids),
                },
            }
        )
    return checks


def _question_id_from_statement(statement: str) -> str:
    token = statement.split(" ", 1)[0]
    return token if token.startswith("C4-") else "C4-UNKNOWN"
