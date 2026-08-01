from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from evident_core.evidence_level import EvidenceLevel
from evident_core.graph import EvidenceEdge


class Outcome(Enum):
    """RES §4.2. Expresses agreement with a rule's own expectation, never a compliance verdict."""

    EXPECTATION_MET = "EXPECTATION_MET"
    EXPECTATION_NOT_MET = "EXPECTATION_NOT_MET"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class Finding:
    """RES §4.1.

    `level` must be constructed via `evident_core.compute_finding_level` (RES §4.3) —
    never assigned directly by a rule author.
    """

    id: str
    rule_id: str
    level: EvidenceLevel
    outcome: Outcome
    statement: str
    cited_node_ids: tuple[str, ...]
    trace: tuple[EvidenceEdge, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.cited_node_ids:
            raise ValueError("Finding.cited_node_ids must be non-empty (RES §4.1)")
        if len(self.cited_node_ids) != len(set(self.cited_node_ids)):
            raise ValueError("Finding.cited_node_ids must contain unique node ids (RES §4.1)")
