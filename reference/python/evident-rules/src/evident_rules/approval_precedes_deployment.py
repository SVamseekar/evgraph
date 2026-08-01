"""The approval-precedes-deployment rule, worked out fully in RES §10.

Checks that a DeploymentRecord's REQUIRES_APPROVAL edge points to a
HumanApproval whose approved_at precedes the deployment's deployed_at.
reasoning_class is CONSISTENCY: this cross-references two structural
timestamps rather than observing either fact in isolation (RES §3.1).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from evident_core import (
    EvidenceGraph,
    EvidenceLevel,
    Finding,
    Outcome,
    compute_finding_level,
)

RULE_ID = "approval-precedes-deployment"
RULE_NAME = "Approval precedes deployment"
REASONING_CLASS = EvidenceLevel.CONSISTENCY


def _parse_datetime(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


class ApprovalPrecedesDeploymentRule:
    """RES §3.1 Rule: evaluate(graph) -> list[Finding]. Pure; no graph mutation."""

    id = RULE_ID
    name = RULE_NAME
    reasoning_class = REASONING_CLASS

    def evaluate(self, graph: EvidenceGraph) -> list[Finding]:
        findings: list[Finding] = []
        for edge in graph.edges:
            if edge.type != "REQUIRES_APPROVAL":
                continue
            deployment = graph.node(edge.source_id)
            approval = graph.node(edge.target_id)

            if deployment.type != "DeploymentRecord" or approval.type != "HumanApproval":
                continue

            cited_nodes = [deployment, approval]
            level = compute_finding_level(self.reasoning_class, cited_nodes)

            if "deployed_at" not in deployment.attributes or "approved_at" not in approval.attributes:
                findings.append(
                    Finding(
                        id=f"finding_{uuid.uuid4().hex[:8]}",
                        rule_id=self.id,
                        level=level,
                        outcome=Outcome.INCONCLUSIVE,
                        statement=(
                            f"DeploymentRecord {deployment.id} or HumanApproval {approval.id} "
                            "is missing a timestamp needed to compare deployment and approval order."
                        ),
                        cited_node_ids=(deployment.id, approval.id),
                        trace=(edge,),
                    )
                )
                continue

            deployed_at = _parse_datetime(deployment.attributes["deployed_at"])
            approved_at = _parse_datetime(approval.attributes["approved_at"])

            outcome = (
                Outcome.EXPECTATION_MET
                if approved_at <= deployed_at
                else Outcome.EXPECTATION_NOT_MET
            )
            statement = (
                f"DeploymentRecord {deployment.id} has deployed_at "
                f"({deployment.attributes['deployed_at']}) "
                f"{'not preceding' if outcome == Outcome.EXPECTATION_MET else 'preceding'} "
                f"the approved_at ({approval.attributes['approved_at']}) of the "
                f"HumanApproval {approval.id} it requires."
            )

            findings.append(
                Finding(
                    id=f"finding_{uuid.uuid4().hex[:8]}",
                    rule_id=self.id,
                    level=level,
                    outcome=outcome,
                    statement=statement,
                    cited_node_ids=(deployment.id, approval.id),
                    trace=(edge,),
                )
            )
        return findings
