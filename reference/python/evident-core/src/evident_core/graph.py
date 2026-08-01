from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from evident_core.evidence_level import EvidenceLevel

JSONValue = Any  # str | int | float | bool | None | list | dict, per EGS §5

SourceReference = dict[str, JSONValue]
"""EGS §3.2 / Appendix: adapter-defined shape, not standardized in v0.1."""


@dataclass(frozen=True)
class EvidenceNode:
    """EGS §3.2."""

    id: str
    type: str
    observed_at: datetime
    source: SourceReference
    evidence_level: EvidenceLevel
    attributes: dict[str, JSONValue] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceEdge:
    """EGS §3.3."""

    source_id: str
    target_id: str
    type: str
    observed_at: datetime


@dataclass(frozen=True)
class AdapterInvocation:
    """EGS §3.5 — minimal manifest entry; full schema belongs to APS-Core."""

    adapter: str
    version: str


@dataclass(frozen=True)
class EvidenceGraph:
    """EGS §3.5. Immutable snapshot (EGS §4) — no method on this class mutates it."""

    graph_id: str
    created_at: datetime
    nodes: tuple[EvidenceNode, ...]
    edges: tuple[EvidenceEdge, ...]
    adapter_manifest: tuple[AdapterInvocation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        ids = [n.id for n in self.nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("EvidenceGraph node ids must be unique within the graph (EGS §3.1)")
        node_ids = set(ids)
        for e in self.edges:
            if e.source_id not in node_ids or e.target_id not in node_ids:
                raise ValueError(
                    f"EvidenceEdge references unknown node id(s): {e.source_id!r} -> {e.target_id!r}"
                )

    def node(self, node_id: str) -> EvidenceNode:
        for n in self.nodes:
            if n.id == node_id:
                return n
        raise KeyError(f"No node with id {node_id!r} in graph {self.graph_id!r}")

    # --- EGS §6 traversal operations ---

    def neighbors(self, node_id: str) -> list[EvidenceNode]:
        """Nodes directly connected to node_id by one edge, either direction."""
        self.node(node_id)  # raises KeyError if node_id is not in the graph
        neighbor_ids: list[str] = []
        for e in self.edges:
            if e.source_id == node_id:
                neighbor_ids.append(e.target_id)
            elif e.target_id == node_id:
                neighbor_ids.append(e.source_id)
        return [self.node(nid) for nid in neighbor_ids]

    def ancestors(self, node_id: str) -> list[EvidenceNode]:
        """All nodes reachable by following edges backward (target -> source), transitively."""
        self.node(node_id)
        seen: set[str] = set()
        frontier = [node_id]
        while frontier:
            current = frontier.pop()
            for e in self.edges:
                if e.target_id == current and e.source_id not in seen:
                    seen.add(e.source_id)
                    frontier.append(e.source_id)
        return [self.node(nid) for nid in seen]

    def descendants(self, node_id: str) -> list[EvidenceNode]:
        """All nodes reachable by following edges forward (source -> target), transitively."""
        self.node(node_id)
        seen: set[str] = set()
        frontier = [node_id]
        while frontier:
            current = frontier.pop()
            for e in self.edges:
                if e.source_id == current and e.target_id not in seen:
                    seen.add(e.target_id)
                    frontier.append(e.target_id)
        return [self.node(nid) for nid in seen]

    def trace(self, node_id: str) -> list[EvidenceEdge]:
        """The edge path connecting node_id back to its root ancestor(s) (EGS §6).

        Follows backward edges (target -> source) from node_id until no further
        backward edge exists. Returns the ordered path closest-first. If a node has
        multiple incoming edges, the first encountered (by edge list order) is followed —
        EGS v0.1 defines no tie-breaking rule beyond this for multi-parent nodes.
        """
        self.node(node_id)
        path: list[EvidenceEdge] = []
        current = node_id
        visited: set[str] = {current}
        while True:
            parent_edge = next((e for e in self.edges if e.target_id == current), None)
            if parent_edge is None or parent_edge.source_id in visited:
                break
            path.append(parent_edge)
            current = parent_edge.source_id
            visited.add(current)
        return path
