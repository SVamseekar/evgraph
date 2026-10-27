from datetime import datetime, timezone

import pytest

from evgraph_core import EvidenceEdge, EvidenceGraph, EvidenceLevel, EvidenceNode, Finding, Outcome

from evgraph.reporters.oscal_reporter import to_oscal_assessment_results_dict

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_graph() -> EvidenceGraph:
    approval = EvidenceNode(
        id="n2",
        type="HumanApproval",
        observed_at=NOW,
        source={"path": "approval.json"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={"approved_at": "2026-06-15T00:00:00Z"},
    )
    deployment = EvidenceNode(
        id="n3",
        type="DeploymentRecord",
        observed_at=NOW,
        source={"path": "deployment.json"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={"deployed_at": "2026-06-10T00:00:00Z"},
    )
    edge = EvidenceEdge(source_id="n3", target_id="n2", type="REQUIRES_APPROVAL", observed_at=NOW)
    return EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(deployment, approval), edges=(edge,))


def make_finding() -> Finding:
    return Finding(
        id="f1",
        rule_id="approval-precedes-deployment",
        level=EvidenceLevel.CONSISTENCY,
        outcome=Outcome.EXPECTATION_NOT_MET,
        statement="deployment preceded approval",
        cited_node_ids=("n3", "n2"),
        trace=(),
    )


def test_top_level_shape_is_assessment_results():
    doc = to_oscal_assessment_results_dict(make_graph(), [])
    assert "assessment-results" in doc
    ar = doc["assessment-results"]
    assert "uuid" in ar
    assert ar["metadata"]["oscal-version"] == "1.1.2"
    assert len(ar["results"]) == 1


def test_every_node_becomes_an_observation():
    doc = to_oscal_assessment_results_dict(make_graph(), [])
    observations = doc["assessment-results"]["results"][0]["observations"]
    assert len(observations) == 2
    for obs in observations:
        assert obs["methods"] == ["TEST"]
        assert "uuid" in obs


def test_evidence_level_carried_as_prop_extension_on_observation():
    doc = to_oscal_assessment_results_dict(make_graph(), [])
    observations = doc["assessment-results"]["results"][0]["observations"]
    for obs in observations:
        level_props = [p for p in obs["props"] if p["name"] == "evidence-level"]
        assert len(level_props) == 1
        assert level_props[0]["value"] == "STRUCTURAL"
        assert level_props[0]["ns"] == "https://github.com/SVamseekar/evgraph/ns/oscal"


def test_finding_references_related_observations():
    doc = to_oscal_assessment_results_dict(make_graph(), [make_finding()])
    findings = doc["assessment-results"]["results"][0]["findings"]
    assert len(findings) == 1
    finding = findings[0]
    assert finding["title"] == "approval-precedes-deployment"
    assert finding["description"] == "deployment preceded approval"
    assert len(finding["related-observations"]) == 2


def test_finding_level_carried_as_prop_extension_not_risk_severity():
    doc = to_oscal_assessment_results_dict(make_graph(), [make_finding()])
    finding = doc["assessment-results"]["results"][0]["findings"][0]
    level_props = [p for p in finding["props"] if p["name"] == "evidence-level"]
    outcome_props = [p for p in finding["props"] if p["name"] == "outcome"]
    assert level_props[0]["value"] == "CONSISTENCY"
    assert outcome_props[0]["value"] == "EXPECTATION_NOT_MET"
    assert "risk" not in doc["assessment-results"]["results"][0]


def test_no_findings_omits_the_findings_list():
    # OSCAL arrays carry minItems 1, so an empty list would make the document invalid.
    doc = to_oscal_assessment_results_dict(make_graph(), [])
    assert "findings" not in doc["assessment-results"]["results"][0]


def _resources(doc):
    return {r["uuid"]: r for r in doc["assessment-results"]["back-matter"]["resources"]}


def test_import_ap_points_at_a_back_matter_resource():
    doc = to_oscal_assessment_results_dict(make_graph(), [make_finding()])
    href = doc["assessment-results"]["import-ap"]["href"]
    assert href.startswith("#")
    assert href[1:] in _resources(doc)


def test_result_declares_reviewed_controls():
    doc = to_oscal_assessment_results_dict(make_graph(), [make_finding()])
    selections = doc["assessment-results"]["results"][0]["reviewed-controls"]["control-selections"]
    assert len(selections) >= 1


@pytest.mark.parametrize(
    "outcome,state,reason",
    [
        (Outcome.EXPECTATION_MET, "satisfied", "pass"),
        (Outcome.EXPECTATION_NOT_MET, "not-satisfied", "fail"),
        (Outcome.INCONCLUSIVE, "not-satisfied", "other"),
    ],
)
def test_finding_target_status_follows_the_outcome(outcome, state, reason):
    finding = Finding(
        id="f1",
        rule_id="approval-precedes-deployment",
        level=EvidenceLevel.CONSISTENCY,
        outcome=outcome,
        statement="s",
        cited_node_ids=("n3", "n2"),
    )
    target = to_oscal_assessment_results_dict(make_graph(), [finding])["assessment-results"]["results"][0][
        "findings"
    ][0]["target"]
    assert target["type"] == "objective-id"
    assert target["target-id"] == "approval-precedes-deployment"
    assert target["status"] == {"state": state, "reason": reason}


def test_observation_subjects_are_back_matter_resources():
    doc = to_oscal_assessment_results_dict(make_graph(), [])
    resources = _resources(doc)
    for obs in doc["assessment-results"]["results"][0]["observations"]:
        subject = obs["subjects"][0]
        assert subject["type"] == "resource"
        assert subject["subject-uuid"] in resources
        assert subject["subject-uuid"] != obs["uuid"]


def test_same_report_renders_the_same_document():
    first = to_oscal_assessment_results_dict(make_graph(), [make_finding()])
    second = to_oscal_assessment_results_dict(make_graph(), [make_finding()])
    for doc in (first, second):
        del doc["assessment-results"]["metadata"]["last-modified"]
    assert first == second
