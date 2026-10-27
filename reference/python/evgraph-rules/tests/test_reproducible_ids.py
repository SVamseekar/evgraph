"""RES §3.2 reproducibility: evaluating the same graph twice yields the same findings, ids included."""

from datetime import datetime, timezone

from evgraph_core import EvidenceEdge, EvidenceGraph, EvidenceLevel, EvidenceNode

from evgraph_rules import (
    ApprovalPrecedesDeploymentRule,
    DatasetManifestCompleteRule,
    ModelVersionHasTrainingProvenanceRule,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _node(node_id, node_type, attributes):
    return EvidenceNode(
        id=node_id,
        type=node_type,
        observed_at=NOW,
        source={},
        evidence_level=EvidenceLevel.STRUCTURAL,
        attributes=attributes,
    )


GRAPH = EvidenceGraph(
    graph_id="g",
    created_at=NOW,
    nodes=(
        _node("n2", "HumanApproval", {"approver": "a", "approved_at": "2026-01-01T00:00:00Z"}),
        _node("n3", "DeploymentRecord", {"deployed_at": "2026-01-02T00:00:00Z"}),
        _node("d1", "Dataset", {"dataset_id": "d1", "license": "MIT"}),
        _node("v1", "MLflowModelVersion", {"version": "1"}),
    ),
    edges=(EvidenceEdge(source_id="n3", target_id="n2", type="REQUIRES_APPROVAL", observed_at=NOW),),
)


def test_every_built_in_rule_produces_the_same_ids_twice():
    for rule in (ApprovalPrecedesDeploymentRule(), DatasetManifestCompleteRule(), ModelVersionHasTrainingProvenanceRule()):
        first = rule.evaluate(GRAPH)
        second = rule.evaluate(GRAPH)
        assert first, rule.id
        assert first == second, rule.id
