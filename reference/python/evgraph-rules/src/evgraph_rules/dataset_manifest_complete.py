"""The dataset-manifest-complete rule.

Checks that each Dataset node declares a non-empty license. reasoning_class
is STRUCTURAL: this is a direct presence check on a single node's attribute,
with no cross-referencing between nodes (unlike approval-precedes-deployment's
CONSISTENCY) — pressure-tests that RES's reasoning_class/Finding.level model
generalizes across rules with different epistemic weight.
"""

from __future__ import annotations

import uuid

from evgraph_core import EvidenceGraph, EvidenceLevel, Finding, Outcome, compute_finding_level

RULE_ID = "dataset-manifest-complete"
RULE_NAME = "Dataset manifest declares a license"
REASONING_CLASS = EvidenceLevel.STRUCTURAL


class DatasetManifestCompleteRule:
    """RES §3.1 Rule: evaluate(graph) -> list[Finding]. Pure; no graph mutation."""

    id = RULE_ID
    name = RULE_NAME
    reasoning_class = REASONING_CLASS

    def evaluate(self, graph: EvidenceGraph) -> list[Finding]:
        findings: list[Finding] = []
        for node in graph.nodes:
            if node.type != "Dataset":
                continue

            level = compute_finding_level(self.reasoning_class, [node])
            license_value = node.attributes.get("license", "")

            if license_value:
                outcome = Outcome.EXPECTATION_MET
                statement = (
                    f"Dataset {node.attributes.get('dataset_id', node.id)} "
                    f"declares license '{license_value}'."
                )
            else:
                outcome = Outcome.EXPECTATION_NOT_MET
                statement = (
                    f"Dataset {node.attributes.get('dataset_id', node.id)} "
                    "does not declare a license."
                )

            findings.append(
                Finding(
                    id=f"finding_{uuid.uuid4().hex[:8]}",
                    rule_id=self.id,
                    level=level,
                    outcome=outcome,
                    statement=statement,
                    cited_node_ids=(node.id,),
                    trace=(),
                )
            )
        return findings
