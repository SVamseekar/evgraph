from datetime import datetime, timezone

import pytest
from evgraph_core import EvidenceEdge, EvidenceGraph, EvidenceLevel, EvidenceNode, Outcome

from evgraph_rules.approval_precedes_deployment import ApprovalPrecedesDeploymentRule

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
_MISSING = object()


def make_graph(deployed_at: object = _MISSING, approved_at: object = _MISSING) -> EvidenceGraph:
    deployment_attrs = {} if deployed_at is _MISSING else {"deployed_at": deployed_at}
    approval_attrs = {"approver": "J. Smith"}
    if approved_at is not _MISSING:
        approval_attrs["approved_at"] = approved_at

    deployment = EvidenceNode(
        id="n3",
        type="DeploymentRecord",
        observed_at=NOW,
        source={"path": "deploy.json"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes=deployment_attrs,
    )
    approval = EvidenceNode(
        id="n2",
        type="HumanApproval",
        observed_at=NOW,
        source={"path": "approval.json"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes=approval_attrs,
    )
    edge = EvidenceEdge(source_id="n3", target_id="n2", type="REQUIRES_APPROVAL", observed_at=NOW)
    return EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(deployment, approval), edges=(edge,))


def test_approval_after_deployment_is_expectation_not_met():
    graph = make_graph(deployed_at="2026-06-10T00:00:00Z", approved_at="2026-06-15T00:00:00Z")
    findings = ApprovalPrecedesDeploymentRule().evaluate(graph)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.outcome == Outcome.EXPECTATION_NOT_MET
    assert finding.level == EvidenceLevel.CONSISTENCY
    assert set(finding.cited_node_ids) == {"n2", "n3"}
    assert len(finding.trace) == 1
    assert finding.trace[0].type == "REQUIRES_APPROVAL"


def test_approval_before_deployment_is_expectation_met():
    graph = make_graph(deployed_at="2026-06-15T00:00:00Z", approved_at="2026-06-10T00:00:00Z")
    findings = ApprovalPrecedesDeploymentRule().evaluate(graph)

    assert len(findings) == 1
    assert findings[0].outcome == Outcome.EXPECTATION_MET
    assert findings[0].level == EvidenceLevel.CONSISTENCY


def test_missing_timestamp_is_inconclusive():
    graph = make_graph(approved_at="2026-06-10T00:00:00Z")
    findings = ApprovalPrecedesDeploymentRule().evaluate(graph)

    assert len(findings) == 1
    assert findings[0].outcome == Outcome.INCONCLUSIVE


def test_no_findings_when_no_requires_approval_edge():
    deployment = EvidenceNode(
        id="n3",
        type="DeploymentRecord",
        observed_at=NOW,
        source={"path": "deploy.json"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={"deployed_at": "2026-06-10T00:00:00Z"},
    )
    graph = EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(deployment,), edges=())
    findings = ApprovalPrecedesDeploymentRule().evaluate(graph)
    assert findings == []


@pytest.mark.parametrize("bad", ["yesterday", "2026-13-01T00:00:00Z", "", 20260101, None])
def test_malformed_approved_at_is_inconclusive(bad):
    graph = make_graph(deployed_at="2026-06-10T00:00:00Z", approved_at=bad)
    findings = ApprovalPrecedesDeploymentRule().evaluate(graph)

    assert len(findings) == 1
    assert findings[0].outcome == Outcome.INCONCLUSIVE
    assert "approved_at" in findings[0].statement


def test_malformed_deployed_at_is_inconclusive():
    graph = make_graph(deployed_at="not-a-date", approved_at="2026-06-01T00:00:00Z")
    findings = ApprovalPrecedesDeploymentRule().evaluate(graph)

    assert len(findings) == 1
    assert findings[0].outcome == Outcome.INCONCLUSIVE
    assert "deployed_at" in findings[0].statement
    assert "approved_at" not in findings[0].statement


def test_timezone_less_timestamps_are_treated_as_utc():
    graph = make_graph(deployed_at="2026-06-10T00:00:00", approved_at="2026-06-09T23:00:00Z")
    findings = ApprovalPrecedesDeploymentRule().evaluate(graph)

    assert findings[0].outcome == Outcome.EXPECTATION_MET


def make_linked_graph(
    *,
    approval_attrs: dict,
    deployment_attrs: dict | None = None,
    card_model_name: str = "risk-scorer-v3",
) -> EvidenceGraph:
    card = EvidenceNode(
        id="n1",
        type="ModelCard",
        observed_at=NOW,
        source={"path": "card.json"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={"model_name": card_model_name, "has_intended_use": True},
    )
    approval = EvidenceNode(
        id="n2",
        type="HumanApproval",
        observed_at=NOW,
        source={"path": "approval.json"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={"approver": "J. Smith", "approved_at": "2026-06-01T00:00:00Z", **approval_attrs},
    )
    deployment = EvidenceNode(
        id="n3",
        type="DeploymentRecord",
        observed_at=NOW,
        source={"path": "deploy.json"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={"deployed_at": "2026-06-10T00:00:00Z", **(deployment_attrs or {})},
    )
    edges = (
        EvidenceEdge(source_id="n3", target_id="n1", type="DEPLOYS", observed_at=NOW),
        EvidenceEdge(source_id="n3", target_id="n2", type="REQUIRES_APPROVAL", observed_at=NOW),
    )
    return EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(card, approval, deployment), edges=edges)


@pytest.mark.parametrize("decision", ["rejected", "Denied", "pending", "REVOKED"])
def test_a_negative_decision_is_not_an_approval(decision):
    findings = ApprovalPrecedesDeploymentRule().evaluate(make_linked_graph(approval_attrs={"decision": decision}))
    assert [f.outcome for f in findings] == [Outcome.EXPECTATION_NOT_MET]
    assert decision in findings[0].statement


@pytest.mark.parametrize("decision", ["approved", "APPROVED", "granted"])
def test_an_explicit_approval_decision_still_compares_timestamps(decision):
    findings = ApprovalPrecedesDeploymentRule().evaluate(make_linked_graph(approval_attrs={"decision": decision}))
    assert [f.outcome for f in findings] == [Outcome.EXPECTATION_MET]


def test_an_unrecognised_decision_is_inconclusive():
    findings = ApprovalPrecedesDeploymentRule().evaluate(
        make_linked_graph(approval_attrs={"decision": "approved with conditions"})
    )
    assert [f.outcome for f in findings] == [Outcome.INCONCLUSIVE]


@pytest.mark.parametrize("approver", ["", "   ", None])
def test_an_approval_without_an_approver_is_inconclusive(approver):
    findings = ApprovalPrecedesDeploymentRule().evaluate(make_linked_graph(approval_attrs={"approver": approver}))
    assert [f.outcome for f in findings] == [Outcome.INCONCLUSIVE]
    assert "approver" in findings[0].statement


def test_an_approval_for_another_model_is_not_met():
    findings = ApprovalPrecedesDeploymentRule().evaluate(
        make_linked_graph(approval_attrs={"model_name": "some-other-model"})
    )
    assert [f.outcome for f in findings] == [Outcome.EXPECTATION_NOT_MET]
    assert "some-other-model" in findings[0].statement
    assert set(findings[0].cited_node_ids) == {"n1", "n2", "n3"}


def test_a_deployment_of_another_model_is_not_met():
    findings = ApprovalPrecedesDeploymentRule().evaluate(
        make_linked_graph(approval_attrs={}, deployment_attrs={"model_name": "shadow-model"})
    )
    assert [f.outcome for f in findings] == [Outcome.EXPECTATION_NOT_MET]


def test_matching_model_names_compare_timestamps():
    findings = ApprovalPrecedesDeploymentRule().evaluate(
        make_linked_graph(
            approval_attrs={"model_name": "risk-scorer-v3"},
            deployment_attrs={"model_name": "risk-scorer-v3"},
        )
    )
    assert [f.outcome for f in findings] == [Outcome.EXPECTATION_MET]


def test_any_negative_value_among_decision_and_status_is_not_met():
    findings = ApprovalPrecedesDeploymentRule().evaluate(
        make_linked_graph(approval_attrs={"decision": "approved", "status": "rejected"})
    )
    assert [f.outcome for f in findings] == [Outcome.EXPECTATION_NOT_MET]


def test_an_unreadable_status_beside_an_approval_is_inconclusive():
    findings = ApprovalPrecedesDeploymentRule().evaluate(
        make_linked_graph(approval_attrs={"decision": "approved", "status": "on hold?"})
    )
    assert [f.outcome for f in findings] == [Outcome.INCONCLUSIVE]
