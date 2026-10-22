"""The approval-precedes-deployment rule, worked out fully in RES §10.

Checks that a DeploymentRecord's REQUIRES_APPROVAL edge points to a
HumanApproval whose approved_at precedes the deployment's deployed_at.
reasoning_class is CONSISTENCY: this cross-references two structural
timestamps rather than observing either fact in isolation (RES §3.1).

A record only counts as the approval the deployment requires when it is one:
a stated decision or status that is not an approval (rejected, pending, ...)
or a stated model name that differs from the deployed model is
EXPECTATION_NOT_MET, and a record with no approver or an unrecognised
decision or status is INCONCLUSIVE.
Records that state no decision are treated as approvals (adapter assumption).
"""

from __future__ import annotations

from datetime import datetime, timezone

from evgraph_core import (
    EvidenceGraph,
    EvidenceLevel,
    EvidenceNode,
    Finding,
    Outcome,
    compute_finding_level,
    stable_finding_id,
)

RULE_ID = "approval-precedes-deployment"
RULE_NAME = "Approval precedes deployment"
REASONING_CLASS = EvidenceLevel.CONSISTENCY

APPROVED_DECISIONS = frozenset({"approved", "approve", "granted", "accepted"})
NOT_APPROVED_DECISIONS = frozenset(
    {
        "rejected",
        "reject",
        "denied",
        "declined",
        "revoked",
        "withdrawn",
        "pending",
        "requested",
        "not_approved",
        "not approved",
    }
)


def _parse_datetime(value: object) -> datetime | None:
    """Parse an ISO-8601 timestamp. Returns None when the value is not a valid timestamp string."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
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

            model_card = _deployed_model_card(graph, deployment)
            cited_nodes = [deployment, approval] + ([model_card] if model_card is not None else [])
            outcome, statement = self._judge(deployment, approval, model_card)
            cited_ids = [n.id for n in cited_nodes]
            findings.append(
                Finding(
                    id=stable_finding_id(self.id, cited_ids, f"{edge.source_id}->{edge.target_id}"),
                    rule_id=self.id,
                    level=compute_finding_level(self.reasoning_class, cited_nodes),
                    outcome=outcome,
                    statement=statement,
                    cited_node_ids=tuple(cited_ids),
                    trace=(edge,),
                )
            )
        return findings

    def _judge(
        self, deployment: EvidenceNode, approval: EvidenceNode, model_card: EvidenceNode | None
    ) -> tuple[Outcome, str]:
        mismatch = _model_mismatch(deployment, approval, model_card)
        if mismatch is not None:
            return Outcome.EXPECTATION_NOT_MET, mismatch

        # Both fields are read: any one that says "not approved" wins, and any unreadable one is
        # inconclusive, so a stale "approved" next to a "rejected" can never pass.
        stated = [
            (name, approval.attributes[name])
            for name in ("decision", "status")
            if approval.attributes.get(name) is not None
        ]
        for name, value in stated:
            if str(value).strip().lower() in NOT_APPROVED_DECISIONS:
                return (
                    Outcome.EXPECTATION_NOT_MET,
                    f"HumanApproval {approval.id} records the {name} '{value}', which is not an "
                    f"approval, so DeploymentRecord {deployment.id} has no approval.",
                )
        for name, value in stated:
            if str(value).strip().lower() not in APPROVED_DECISIONS:
                return (
                    Outcome.INCONCLUSIVE,
                    f"HumanApproval {approval.id} records the {name} '{value}', which this rule "
                    "cannot read as approved or not approved.",
                )

        approver = approval.attributes.get("approver")
        if not isinstance(approver, str) or not approver.strip():
            return (
                Outcome.INCONCLUSIVE,
                f"HumanApproval {approval.id} names no approver, so it cannot show that a person "
                f"approved DeploymentRecord {deployment.id}.",
            )

        if "deployed_at" not in deployment.attributes or "approved_at" not in approval.attributes:
            return (
                Outcome.INCONCLUSIVE,
                f"DeploymentRecord {deployment.id} or HumanApproval {approval.id} "
                "is missing a timestamp needed to compare deployment and approval order.",
            )

        deployed_at = _parse_datetime(deployment.attributes["deployed_at"])
        approved_at = _parse_datetime(approval.attributes["approved_at"])
        if deployed_at is None or approved_at is None:
            bad_fields = []
            if deployed_at is None:
                bad_fields.append(f"deployed_at of DeploymentRecord {deployment.id}")
            if approved_at is None:
                bad_fields.append(f"approved_at of HumanApproval {approval.id}")
            return (
                Outcome.INCONCLUSIVE,
                "Cannot compare deployment and approval order: "
                + " and ".join(bad_fields)
                + " is not a valid ISO-8601 timestamp.",
            )

        outcome = Outcome.EXPECTATION_MET if approved_at <= deployed_at else Outcome.EXPECTATION_NOT_MET
        statement = (
            f"DeploymentRecord {deployment.id} has deployed_at "
            f"({deployment.attributes['deployed_at']}) "
            f"{'not preceding' if outcome == Outcome.EXPECTATION_MET else 'preceding'} "
            f"the approved_at ({approval.attributes['approved_at']}) of the "
            f"HumanApproval {approval.id} it requires."
        )
        return outcome, statement


def _deployed_model_card(graph: EvidenceGraph, deployment: EvidenceNode) -> EvidenceNode | None:
    for edge in graph.edges:
        if edge.type == "DEPLOYS" and edge.source_id == deployment.id:
            target = graph.node(edge.target_id)
            if target.type == "ModelCard":
                return target
    return None


def _model_mismatch(
    deployment: EvidenceNode, approval: EvidenceNode, model_card: EvidenceNode | None
) -> str | None:
    """A statement when the records name different models, else None. Absent names are not compared."""
    card_name = model_card.attributes.get("model_name") if model_card is not None else None
    deployed_name = deployment.attributes.get("model_name")
    if card_name is not None and deployed_name is not None and str(deployed_name) != str(card_name):
        return (
            f"DeploymentRecord {deployment.id} names model '{deployed_name}', but the ModelCard "
            f"{model_card.id} it deploys describes '{card_name}'."
        )
    reference = deployed_name if deployed_name is not None else card_name
    approved_name = approval.attributes.get("model_name")
    if approved_name is not None and reference is not None and str(approved_name) != str(reference):
        return (
            f"HumanApproval {approval.id} approves model '{approved_name}', but DeploymentRecord "
            f"{deployment.id} deploys '{reference}'."
        )
    return None
