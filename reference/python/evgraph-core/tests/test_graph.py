from datetime import datetime, timezone

import pytest

from evgraph_core import EvidenceEdge, EvidenceGraph, EvidenceLevel, EvidenceNode


def make_node(node_id: str, level: EvidenceLevel = EvidenceLevel.STRUCTURAL) -> EvidenceNode:
    return EvidenceNode(
        id=node_id,
        type="TestNode",
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        source={"path": "test.json"},
        evidence_level=level,
        attributes={},
    )


def make_edge(source_id: str, target_id: str, edge_type: str = "RELATES_TO") -> EvidenceEdge:
    return EvidenceEdge(
        source_id=source_id,
        target_id=target_id,
        type=edge_type,
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def make_graph(nodes, edges) -> EvidenceGraph:
    return EvidenceGraph(
        graph_id="g1",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        nodes=tuple(nodes),
        edges=tuple(edges),
    )


def test_duplicate_node_ids_rejected():
    with pytest.raises(ValueError):
        make_graph([make_node("n1"), make_node("n1")], [])


def test_edge_referencing_unknown_node_rejected():
    with pytest.raises(ValueError):
        make_graph([make_node("n1")], [make_edge("n1", "n2")])


def test_neighbors():
    graph = make_graph(
        [make_node("n1"), make_node("n2"), make_node("n3")],
        [make_edge("n1", "n2"), make_edge("n3", "n1")],
    )
    neighbor_ids = {n.id for n in graph.neighbors("n1")}
    assert neighbor_ids == {"n2", "n3"}


def test_ancestors_and_descendants():
    graph = make_graph(
        [make_node("n1"), make_node("n2"), make_node("n3")],
        [make_edge("n1", "n2"), make_edge("n2", "n3")],
    )
    assert {n.id for n in graph.descendants("n1")} == {"n2", "n3"}
    assert {n.id for n in graph.ancestors("n3")} == {"n1", "n2"}
    assert graph.ancestors("n1") == []
    assert graph.descendants("n3") == []


def test_trace_follows_backward_edges_to_root():
    graph = make_graph(
        [make_node("n1"), make_node("n2"), make_node("n3")],
        [make_edge("n1", "n2"), make_edge("n2", "n3")],
    )
    path = graph.trace("n3")
    assert [e.source_id for e in path] == ["n2", "n1"]


def test_trace_on_root_is_empty():
    graph = make_graph([make_node("n1")], [])
    assert graph.trace("n1") == []


def test_node_lookup_raises_for_unknown_id():
    graph = make_graph([make_node("n1")], [])
    with pytest.raises(KeyError):
        graph.node("does-not-exist")
