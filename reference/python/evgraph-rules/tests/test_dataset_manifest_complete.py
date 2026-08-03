from datetime import datetime, timezone

from evgraph_core import EvidenceGraph, EvidenceLevel, EvidenceNode, Outcome

from evgraph_rules.dataset_manifest_complete import DatasetManifestCompleteRule

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_dataset_node(dataset_id: str, license_value: str) -> EvidenceNode:
    return EvidenceNode(
        id=f"dataset_{dataset_id}",
        type="Dataset",
        observed_at=NOW,
        source={"path": "manifest.csv"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={"dataset_id": dataset_id, "source": "warehouse", "license": license_value, "contains_pii": False},
    )


def test_dataset_with_license_is_expectation_met():
    graph = EvidenceGraph(
        graph_id="g1", created_at=NOW, nodes=(make_dataset_node("d1", "CC-BY-4.0"),), edges=()
    )
    findings = DatasetManifestCompleteRule().evaluate(graph)
    assert len(findings) == 1
    assert findings[0].outcome == Outcome.EXPECTATION_MET
    assert findings[0].level == EvidenceLevel.STRUCTURAL


def test_dataset_without_license_is_expectation_not_met():
    graph = EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(make_dataset_node("d1", ""),), edges=())
    findings = DatasetManifestCompleteRule().evaluate(graph)
    assert len(findings) == 1
    assert findings[0].outcome == Outcome.EXPECTATION_NOT_MET


def test_ignores_non_dataset_nodes():
    other_node = EvidenceNode(
        id="n1",
        type="ModelCard",
        observed_at=NOW,
        source={"path": "x.json"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={},
    )
    graph = EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(other_node,), edges=())
    assert DatasetManifestCompleteRule().evaluate(graph) == []


def test_multiple_datasets_produce_multiple_findings():
    graph = EvidenceGraph(
        graph_id="g1",
        created_at=NOW,
        nodes=(make_dataset_node("d1", "CC-BY-4.0"), make_dataset_node("d2", "")),
        edges=(),
    )
    findings = DatasetManifestCompleteRule().evaluate(graph)
    assert len(findings) == 2
