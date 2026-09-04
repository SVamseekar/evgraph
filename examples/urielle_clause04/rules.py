"""One rule: does this Clause 04 question have a structured evidence reference or not.

That's it. No readiness score, no ISO 42001 pass/fail.
"""

from __future__ import annotations

import uuid

from evgraph_core import (
    EvidenceGraph,
    EvidenceLevel,
    Finding,
    Outcome,
    compute_finding_level,
)

RULE_ID = "clause04-question-has-structured-evidence"
RULE_NAME = "Clause 04 question has structured evidence references"
REASONING_CLASS = EvidenceLevel.STRUCTURAL


class Clause04QuestionHasStructuredEvidenceRule:
    id = RULE_ID
    name = RULE_NAME
    reasoning_class = REASONING_CLASS

    def evaluate(self, graph: EvidenceGraph) -> list[Finding]:
        findings: list[Finding] = []
        for node in graph.nodes:
            if node.type != "UrielleAuditQuestion":
                continue

            level = compute_finding_level(self.reasoning_class, [node])
            question_id = node.attributes.get("question_id", node.id)
            reference_count = node.attributes.get("reference_count", 0)

            if isinstance(reference_count, int) and reference_count > 0:
                outcome = Outcome.EXPECTATION_MET
                statement = (
                    f"{question_id} has {reference_count} structured "
                    "evidence reference(s)."
                )
            else:
                outcome = Outcome.EXPECTATION_NOT_MET
                statement = (
                    f"{question_id} has no structured evidence references."
                )

            findings.append(
                Finding(
                    id=f"finding_{uuid.uuid4().hex[:8]}",
                    rule_id=self.id,
                    level=level,
                    outcome=outcome,
                    statement=statement,
                    cited_node_ids=(node.id,),
                    trace=tuple(graph.trace(node.id)),
                )
            )
        return findings
