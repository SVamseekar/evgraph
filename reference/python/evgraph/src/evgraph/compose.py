from __future__ import annotations

import uuid
from datetime import datetime, timezone

from evgraph_core import Assumption, EvidenceEdge, EvidenceGraph, EvidenceNode

REFERS_TO_REGISTRY_VERSION = "REFERS_TO_REGISTRY_VERSION"

PROMOTION_ASSUMPTIONS = [
    Assumption(
        id="PROM-001",
        statement=(
            "ModelCard and MLflow ModelVersion identities are linked by exact string "
            "equality of the model name and version supplied to the promotion scan."
        ),
    )
]


def compose_graphs(
    *graphs: EvidenceGraph,
    link_model_name: str | None = None,
    link_model_version: str | None = None,
) -> EvidenceGraph:
    """Combine immutable EvidenceGraphs with optional promotion identity links."""
    observed_at = datetime.now(timezone.utc)
    accepted_ids: set[str] = set()
    nodes: list[EvidenceNode] = []
    edges: list[EvidenceEdge] = []
    manifests = []

    for graph_index, graph in enumerate(graphs):
        id_map: dict[str, str] = {}
        planned_ids: set[str] = set()

        for node in graph.nodes:
            new_id = node.id
            while graph_index > 0 and (new_id in accepted_ids or new_id in planned_ids):
                new_id = f"g{graph_index}_{new_id}"
            id_map[node.id] = new_id
            planned_ids.add(new_id)
            nodes.append(
                EvidenceNode(
                    id=new_id,
                    type=node.type,
                    observed_at=node.observed_at,
                    source=dict(node.source),
                    evidence_level=node.evidence_level,
                    attributes=dict(node.attributes),
                )
            )

        for edge in graph.edges:
            edges.append(
                EvidenceEdge(
                    source_id=id_map[edge.source_id],
                    target_id=id_map[edge.target_id],
                    type=edge.type,
                    observed_at=edge.observed_at,
                )
            )

        accepted_ids.update(planned_ids)
        manifests.extend(graph.adapter_manifest)

    if link_model_name:
        target_version = str(link_model_version)
        model_cards = [
            node
            for node in nodes
            if node.type == "ModelCard" and node.attributes.get("model_name") == link_model_name
        ]
        model_versions = [
            node
            for node in nodes
            if node.type == "MLflowModelVersion"
            and _registered_model_name(node, target_version) == link_model_name
            and str(node.attributes.get("version")) == target_version
        ]
        for model_card in model_cards:
            for model_version in model_versions:
                edges.append(
                    EvidenceEdge(
                        source_id=model_card.id,
                        target_id=model_version.id,
                        type=REFERS_TO_REGISTRY_VERSION,
                        observed_at=observed_at,
                    )
                )

    return EvidenceGraph(
        graph_id=f"compose_{observed_at.isoformat()}_{uuid.uuid4().hex[:6]}",
        created_at=observed_at,
        nodes=tuple(nodes),
        edges=tuple(edges),
        adapter_manifest=tuple(manifests),
    )


def _registered_model_name(node: EvidenceNode, version: str) -> str | None:
    name = node.source.get("mlflow_registered_model_name")
    if name is not None:
        return str(name)

    prefix = "mlflow_version_"
    suffix = f"_{version}"
    if node.id.startswith(prefix) and node.id.endswith(suffix):
        return node.id[len(prefix) : -len(suffix)]
    return None
