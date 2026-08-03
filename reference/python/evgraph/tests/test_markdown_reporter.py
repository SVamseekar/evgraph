from datetime import datetime, timezone

from evgraph_core import EvidenceEdge, EvidenceGraph, EvidenceLevel, EvidenceNode, Finding, Outcome

from evgraph.reporters.markdown_reporter import to_markdown

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


def make_finding(outcome: Outcome, trace: tuple = ()) -> Finding:
    return Finding(
        id="f1",
        rule_id="test-rule",
        level=EvidenceLevel.STRUCTURAL,
        outcome=outcome,
        statement="a statement",
        cited_node_ids=("n1",),
        trace=trace,
    )


def test_no_findings_renders_placeholder():
    md = to_markdown(make_graph(), [])
    assert "No findings." in md


def test_finding_fields_are_rendered():
    md = to_markdown(make_graph(), [make_finding(Outcome.EXPECTATION_NOT_MET)])
    assert "test-rule" in md
    assert "Expectation not met" in md
    assert "STRUCTURAL" in md
    assert "a statement" in md
    assert "n1" in md


def test_trace_is_rendered_when_present():
    edge = EvidenceEdge(source_id="n1", target_id="n2", type="RELATES_TO", observed_at=NOW)
    md = to_markdown(make_graph(), [make_finding(Outcome.EXPECTATION_MET, trace=(edge,))])
    assert "Trace" in md
    assert "n1 --RELATES_TO--> n2" in md


def test_multiple_findings_each_rendered():
    findings = [make_finding(Outcome.EXPECTATION_MET), make_finding(Outcome.INCONCLUSIVE)]
    md = to_markdown(make_graph(), findings)
    assert md.count("### test-rule") == 2
