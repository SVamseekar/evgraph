from datetime import datetime, timezone

import pytest
from evgraph_core import EvidenceEdge, EvidenceGraph, EvidenceLevel, EvidenceNode, Outcome

from evgraph_rules.approval_precedes_deployment import ApprovalPrecedesDeploymentRule

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
_MISSING = object()


def make_graph(deployed_at: object = _MISSING, approved_at: object = _MISSING) -> EvidenceGraph:
    deployment_attrs = {} if deployed_at is _MISSING else {"deployed_at": deployed_at}
    approval_attrs = {} if approved_at is _MISSING else {"approved_at": approved_at}

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
