from datetime import datetime, timezone

from evgraph_core import EvidenceGraph, EvidenceLevel, EvidenceNode, Finding, Outcome

from evgraph.reporters.sarif_reporter import to_sarif_dict

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_graph() -> EvidenceGraph:
    node = EvidenceNode(
        id="n1",
        type="Dataset",
        observed_at=NOW,
        source={"path": "x.csv"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={},
    )
    return EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(node,), edges=())


def make_finding(outcome: Outcome, rule_id: str = "test-rule") -> Finding:
    return Finding(
        id="f1",
        rule_id=rule_id,
        level=EvidenceLevel.STRUCTURAL,
        outcome=outcome,
        statement="a statement",
        cited_node_ids=("n1",),
        trace=(),
    )


def test_sarif_has_required_top_level_shape():
    sarif = to_sarif_dict(make_graph(), [])
    assert sarif["version"] == "2.1.0"
    assert "runs" in sarif
    assert sarif["runs"][0]["tool"]["driver"]["name"] == "evgraph"


def test_outcome_maps_to_sarif_level():
    sarif = to_sarif_dict(make_graph(), [make_finding(Outcome.EXPECTATION_MET)])
    assert sarif["runs"][0]["results"][0]["level"] == "none"

    sarif = to_sarif_dict(make_graph(), [make_finding(Outcome.EXPECTATION_NOT_MET)])
    assert sarif["runs"][0]["results"][0]["level"] == "warning"

    sarif = to_sarif_dict(make_graph(), [make_finding(Outcome.INCONCLUSIVE)])
    assert sarif["runs"][0]["results"][0]["level"] == "note"


def test_mapping_is_independent_of_rule_identity():
    """The same Outcome must map to the same SARIF level regardless of which
    rule produced it — the reporter must not grade severity by rule."""
    sarif = to_sarif_dict(
        make_graph(),
        [
            make_finding(Outcome.EXPECTATION_NOT_MET, rule_id="rule-a"),
            make_finding(Outcome.EXPECTATION_NOT_MET, rule_id="rule-b"),
        ],
    )
    levels = {r["level"] for r in sarif["runs"][0]["results"]}
    assert levels == {"warning"}


def test_result_preserves_evgraph_specific_fields_in_properties():
    sarif = to_sarif_dict(make_graph(), [make_finding(Outcome.EXPECTATION_NOT_MET)])
    props = sarif["runs"][0]["results"][0]["properties"]
    assert props["evgraphLevel"] == "STRUCTURAL"
    assert props["evgraphOutcome"] == "EXPECTATION_NOT_MET"
    assert props["citedNodeIds"] == ["n1"]


def test_rules_listed_once_per_distinct_rule_id():
    sarif = to_sarif_dict(
        make_graph(),
        [make_finding(Outcome.EXPECTATION_MET, rule_id="rule-a"), make_finding(Outcome.INCONCLUSIVE, rule_id="rule-a")],
    )
    rules = sarif["runs"][0]["tool"]["driver"]["rules"]
    assert rules == [{"id": "rule-a"}]
