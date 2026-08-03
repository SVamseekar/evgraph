from __future__ import annotations

from typing import Iterable, Protocol

from evgraph_core.evidence_level import EvidenceLevel, least_certain
from evgraph_core.finding import Finding
from evgraph_core.graph import EvidenceGraph, EvidenceNode


class Rule(Protocol):
    """RES §3.1.

    Implementations MUST satisfy the invariants in RES §3.2: purity (no mutation of
    the input graph, no shared-state side effects), evgraphiary closure (every
    Finding.cited_node_ids entry must be a node id present in the input graph),
    order independence, and reproducibility.
    """

    id: str
    name: str
    reasoning_class: EvidenceLevel

    def evaluate(self, graph: EvidenceGraph) -> list[Finding]: ...


def compute_finding_level(
    reasoning_class: EvidenceLevel, cited_nodes: Iterable[EvidenceNode]
) -> EvidenceLevel:
    """RES §4.3: Finding.level = leastCertain(reasoning_class, cited node evidence levels).

    This is the only sanctioned way to produce a Finding.level — a rule author
    must never assign it directly.
    """
    node_levels = [n.evidence_level for n in cited_nodes]
    if not node_levels:
        raise ValueError("compute_finding_level requires at least one cited node (RES §4.1)")
    return least_certain(reasoning_class, least_certain(*node_levels))
