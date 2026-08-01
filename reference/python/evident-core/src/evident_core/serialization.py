from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from evident_core.finding import Finding
from evident_core.graph import AdapterInvocation, EvidenceEdge, EvidenceGraph, EvidenceNode

EGS_VERSION = "0.1"
RES_VERSION = "0.1"


def _iso(dt: datetime) -> str:
    """EGS §5: datetime fields serialize as ISO 8601 strings (UTC)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def node_to_dict(node: EvidenceNode) -> dict[str, Any]:
    return {
        "id": node.id,
        "type": node.type,
        "observed_at": _iso(node.observed_at),
        "source": node.source,
        "evidence_level": node.evidence_level.name,
        "attributes": node.attributes,
    }


def edge_to_dict(edge: EvidenceEdge) -> dict[str, Any]:
    return {
        "source_id": edge.source_id,
        "target_id": edge.target_id,
        "type": edge.type,
        "observed_at": _iso(edge.observed_at),
    }


def adapter_invocation_to_dict(inv: AdapterInvocation) -> dict[str, Any]:
    return {"adapter": inv.adapter, "version": inv.version}


def graph_to_dict(graph: EvidenceGraph) -> dict[str, Any]:
    """EGS §5 canonical JSON serialization."""
    return {
        "egs_version": EGS_VERSION,
        "graph_id": graph.graph_id,
        "created_at": _iso(graph.created_at),
        "nodes": [node_to_dict(n) for n in graph.nodes],
        "edges": [edge_to_dict(e) for e in graph.edges],
        "adapter_manifest": [adapter_invocation_to_dict(a) for a in graph.adapter_manifest],
    }


def finding_to_dict(finding: Finding) -> dict[str, Any]:
    """RES §6 canonical JSON serialization."""
    return {
        "res_version": RES_VERSION,
        "id": finding.id,
        "rule_id": finding.rule_id,
        "level": finding.level.name,
        "outcome": finding.outcome.value,
        "statement": finding.statement,
        "cited_node_ids": list(finding.cited_node_ids),
        "trace": [edge_to_dict(e) for e in finding.trace],
    }
