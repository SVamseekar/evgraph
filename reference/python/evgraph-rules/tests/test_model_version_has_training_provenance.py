from datetime import datetime, timezone

from evgraph_core import EvidenceEdge, EvidenceGraph, EvidenceLevel, EvidenceNode, Outcome

from evgraph_rules.model_version_has_training_provenance import (
    ModelVersionHasTrainingProvenanceRule,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_version_node(node_id: str) -> EvidenceNode:
    return EvidenceNode(
        id=node_id,
        type="MLflowModelVersion",
        observed_at=NOW,
        source={"path": "mlflow"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={},
    )


def make_run_node(node_id: str) -> EvidenceNode:
    return EvidenceNode(
        id=node_id,
        type="MLflowRun",
        observed_at=NOW,
        source={"path": "mlflow"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={},
    )


def test_version_with_trained_by_edge_is_expectation_met():
    version = make_version_node("v1")
    run = make_run_node("r1")
    edge = EvidenceEdge(source_id="v1", target_id="r1", type="TRAINED_BY", observed_at=NOW)
    graph = EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(version, run), edges=(edge,))

    findings = ModelVersionHasTrainingProvenanceRule().evaluate(graph)
    assert len(findings) == 1
    assert findings[0].outcome == Outcome.EXPECTATION_MET
    assert findings[0].level == EvidenceLevel.STRUCTURAL


def test_version_without_trained_by_edge_is_expectation_not_met():
    version = make_version_node("v2")
    graph = EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(version,), edges=())

    findings = ModelVersionHasTrainingProvenanceRule().evaluate(graph)
    assert len(findings) == 1
    assert findings[0].outcome == Outcome.EXPECTATION_NOT_MET


def test_ignores_non_version_nodes():
    other = EvidenceNode(
        id="n1",
        type="ModelCard",
        observed_at=NOW,
        source={"path": "x"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={},
    )
    graph = EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(other,), edges=())
    assert ModelVersionHasTrainingProvenanceRule().evaluate(graph) == []


def test_rule_matches_any_adapter_producing_modelversion_suffixed_type():
    """The rule is written against the graph shape, not MLflow specifically —
    any node type ending in "ModelVersion" is matched."""
    version = EvidenceNode(
        id="v1",
        type="CustomRegistryModelVersion",
        observed_at=NOW,
        source={"path": "x"},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes={},
    )
    graph = EvidenceGraph(graph_id="g1", created_at=NOW, nodes=(version,), edges=())
    findings = ModelVersionHasTrainingProvenanceRule().evaluate(graph)
    assert len(findings) == 1
    assert findings[0].outcome == Outcome.EXPECTATION_NOT_MET
