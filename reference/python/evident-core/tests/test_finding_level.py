from datetime import datetime, timezone

import pytest

from evident_core import EvidenceLevel, EvidenceNode, Finding, Outcome, compute_finding_level


def make_node(node_id: str, level: EvidenceLevel) -> EvidenceNode:
    return EvidenceNode(
        id=node_id,
        type="TestNode",
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        source={"path": "test.json"},
        evidence_level=level,
        attributes={},
    )


@pytest.mark.parametrize(
    "reasoning_class,node_levels,expected",
    [
        (EvidenceLevel.STRUCTURAL, [EvidenceLevel.STRUCTURAL], EvidenceLevel.STRUCTURAL),
        (EvidenceLevel.CONSISTENCY, [EvidenceLevel.STRUCTURAL, EvidenceLevel.STRUCTURAL], EvidenceLevel.CONSISTENCY),
        # Reasoning class weaker than all cited evidence still wins (RES ADR-0005 case).
        (EvidenceLevel.HEURISTIC, [EvidenceLevel.STRUCTURAL, EvidenceLevel.STRUCTURAL], EvidenceLevel.HEURISTIC),
        # Evidence weaker than reasoning class still wins.
        (EvidenceLevel.STRUCTURAL, [EvidenceLevel.INTERPRETIVE], EvidenceLevel.INTERPRETIVE),
        (EvidenceLevel.CONSISTENCY, [EvidenceLevel.STRUCTURAL, EvidenceLevel.HEURISTIC], EvidenceLevel.HEURISTIC),
    ],
)
def test_compute_finding_level_is_least_certain(reasoning_class, node_levels, expected):
    nodes = [make_node(f"n{i}", lvl) for i, lvl in enumerate(node_levels)]
    assert compute_finding_level(reasoning_class, nodes) == expected


def test_compute_finding_level_requires_at_least_one_node():
    with pytest.raises(ValueError):
        compute_finding_level(EvidenceLevel.STRUCTURAL, [])


def test_finding_requires_non_empty_cited_node_ids():
    with pytest.raises(ValueError):
        Finding(
            id="f1",
            rule_id="r1",
            level=EvidenceLevel.STRUCTURAL,
            outcome=Outcome.INCONCLUSIVE,
            statement="x",
            cited_node_ids=(),
        )


def test_finding_requires_unique_cited_node_ids():
    with pytest.raises(ValueError):
        Finding(
            id="f1",
            rule_id="r1",
            level=EvidenceLevel.STRUCTURAL,
            outcome=Outcome.INCONCLUSIVE,
            statement="x",
            cited_node_ids=("n1", "n1"),
        )
