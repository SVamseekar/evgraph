from datetime import datetime, timezone

from evgraph_core import AdapterInvocation, EvidenceEdge, EvidenceGraph, EvidenceLevel, EvidenceNode

from evgraph.compose import PROMOTION_ASSUMPTIONS, compose_graphs


OBSERVED_AT = datetime(2026, 8, 25, tzinfo=timezone.utc)


def _graph(
    *,
    graph_id: str,
    nodes: tuple[EvidenceNode, ...],
    edges: tuple[EvidenceEdge, ...] = (),
    adapter: str,
) -> EvidenceGraph:
    return EvidenceGraph(
        graph_id=graph_id,
        created_at=OBSERVED_AT,
        nodes=nodes,
        edges=edges,
        adapter_manifest=(AdapterInvocation(adapter=adapter, version="0.1.0"),),
    )


def _model_card_graph(model_name: str = "risk-scorer") -> EvidenceGraph:
    return _graph(
        graph_id="model-card",
        nodes=(
            EvidenceNode(
                id="n1",
                type="ModelCard",
                observed_at=OBSERVED_AT,
                source={"path": "model_card.json"},
                evidence_level=EvidenceLevel.STRUCTURAL,
                attributes={"model_name": model_name},
            ),
        ),
        adapter="modelcard",
    )


def _mlflow_graph(
    *,
    registered_model_name: str = "risk-scorer",
    version: str | int = "1",
    source: dict | None = None,
) -> EvidenceGraph:
    return _graph(
        graph_id="mlflow",
        nodes=(
            EvidenceNode(
                id="mlflow_version_risk-scorer_1",
                type="MLflowModelVersion",
                observed_at=OBSERVED_AT,
                source=source
                if source is not None
                else {"mlflow_registered_model_name": registered_model_name},
                evidence_level=EvidenceLevel.STRUCTURAL,
                attributes={"version": version},
            ),
        ),
        adapter="mlflow",
    )


def test_compose_links_matching_model_card_to_mlflow_version():
    graph = compose_graphs(
        _model_card_graph(),
        _mlflow_graph(),
        link_model_name="risk-scorer",
        link_model_version="1",
    )

    link_edges = [e for e in graph.edges if e.type == "REFERS_TO_REGISTRY_VERSION"]
    assert len(link_edges) == 1
    assert link_edges[0].source_id == "n1"
    assert link_edges[0].target_id == "mlflow_version_risk-scorer_1"
    assert PROMOTION_ASSUMPTIONS[0].id == "PROM-001"


def test_compose_without_match_combines_nodes_without_link_edges():
    graph = compose_graphs(
        _model_card_graph("risk-scorer"),
        _mlflow_graph(registered_model_name="other-model"),
        link_model_name="risk-scorer",
        link_model_version="1",
    )

    assert len(graph.nodes) == 2
    assert [e for e in graph.edges if e.type == "REFERS_TO_REGISTRY_VERSION"] == []


def test_compose_reids_colliding_nodes_and_rewrites_edges():
    first = _model_card_graph()
    second = _graph(
        graph_id="second",
        nodes=(
            EvidenceNode(
                id="n1",
                type="MLflowRegisteredModel",
                observed_at=OBSERVED_AT,
                source={"mlflow_registered_model_name": "risk-scorer"},
                evidence_level=EvidenceLevel.STRUCTURAL,
                attributes={"name": "risk-scorer"},
            ),
            EvidenceNode(
                id="n2",
                type="MLflowModelVersion",
                observed_at=OBSERVED_AT,
                source={"mlflow_registered_model_name": "risk-scorer"},
                evidence_level=EvidenceLevel.STRUCTURAL,
                attributes={"version": 1},
            ),
        ),
        edges=(
            EvidenceEdge(
                source_id="n2",
                target_id="n1",
                type="MODEL_VERSION_OF",
                observed_at=OBSERVED_AT,
            ),
        ),
        adapter="mlflow",
    )

    graph = compose_graphs(
        first,
        second,
        link_model_name="risk-scorer",
        link_model_version="1",
    )

    assert [n.id for n in graph.nodes] == ["n1", "g1_n1", "n2"]
    assert any(e.source_id == "n2" and e.target_id == "g1_n1" for e in graph.edges)
    assert any(
        e.source_id == "n1"
        and e.target_id == "n2"
        and e.type == "REFERS_TO_REGISTRY_VERSION"
        for e in graph.edges
    )
    assert first.nodes[0].id == "n1"


def test_compose_avoids_prefixed_id_collisions_with_later_nodes():
    first = _graph(
        graph_id="first",
        nodes=(
            EvidenceNode(
                id="x",
                type="ModelCard",
                observed_at=OBSERVED_AT,
                source={"path": "model_card.json"},
                evidence_level=EvidenceLevel.STRUCTURAL,
                attributes={"model_name": "risk-scorer"},
            ),
        ),
        adapter="modelcard",
    )
    second = _graph(
        graph_id="second",
        nodes=(
            EvidenceNode(
                id="x",
                type="MLflowRegisteredModel",
                observed_at=OBSERVED_AT,
                source={"mlflow_registered_model_name": "risk-scorer"},
                evidence_level=EvidenceLevel.STRUCTURAL,
                attributes={"name": "risk-scorer"},
            ),
            EvidenceNode(
                id="g1_x",
                type="MLflowModelVersion",
                observed_at=OBSERVED_AT,
                source={"mlflow_registered_model_name": "risk-scorer"},
                evidence_level=EvidenceLevel.STRUCTURAL,
                attributes={"version": "1"},
            ),
        ),
        edges=(
            EvidenceEdge(
                source_id="g1_x",
                target_id="x",
                type="MODEL_VERSION_OF",
                observed_at=OBSERVED_AT,
            ),
        ),
        adapter="mlflow",
    )

    graph = compose_graphs(first, second)
    node_ids = [n.id for n in graph.nodes]

    assert len(node_ids) == len(set(node_ids))
    assert len(node_ids) == 3
    assert all(e.source_id in node_ids and e.target_id in node_ids for e in graph.edges)
