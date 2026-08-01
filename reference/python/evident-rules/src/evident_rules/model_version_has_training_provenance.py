"""The model-version-has-training-provenance rule.

Checks that every ModelVersion-shaped node has a TRAINED_BY edge to a run
that produced it. reasoning_class is STRUCTURAL: this is a direct edge-
existence check, no cross-referencing of attribute values needed.

Deliberately not named after MLflow: this rule was written against the graph
shape (a node whose type ends in "ModelVersion", connected or not connected
by a TRAINED_BY edge), not against MLflow specifically, so any future adapter
producing the same shape (e.g. a different model registry) is covered without
modification. This rule was written entirely independently of the MLflow
adapter's implementation — it exercises only the EvidenceGraph the adapter
produces, per docs/ROADMAP.md Stage 4.5 Goal 2's validation criterion: "a rule
that was never anticipated by the adapter, without modifying the adapter or
EGS."
"""

from __future__ import annotations

import uuid

from evident_core import EvidenceGraph, EvidenceLevel, Finding, Outcome, compute_finding_level

RULE_ID = "model-version-has-training-provenance"
RULE_NAME = "Model version has training provenance"
REASONING_CLASS = EvidenceLevel.STRUCTURAL


class ModelVersionHasTrainingProvenanceRule:
    """RES §3.1 Rule: evaluate(graph) -> list[Finding]. Pure; no graph mutation."""

    id = RULE_ID
    name = RULE_NAME
    reasoning_class = REASONING_CLASS

    def evaluate(self, graph: EvidenceGraph) -> list[Finding]:
        findings: list[Finding] = []
        version_nodes = [n for n in graph.nodes if n.type.endswith("ModelVersion")]

        for version_node in version_nodes:
            level = compute_finding_level(self.reasoning_class, [version_node])
            has_trained_by = any(
                e.source_id == version_node.id and e.type == "TRAINED_BY" for e in graph.edges
            )

            if has_trained_by:
                outcome = Outcome.EXPECTATION_MET
                statement = (
                    f"{version_node.type} {version_node.id} has a TRAINED_BY edge "
                    "linking it to the run that produced it."
                )
            else:
                outcome = Outcome.EXPECTATION_NOT_MET
                statement = (
                    f"{version_node.type} {version_node.id} has no TRAINED_BY edge — "
                    "no training run is linked to this version."
                )

            findings.append(
                Finding(
                    id=f"finding_{uuid.uuid4().hex[:8]}",
                    rule_id=self.id,
                    level=level,
                    outcome=outcome,
                    statement=statement,
                    cited_node_ids=(version_node.id,),
                    trace=(),
                )
            )
        return findings
