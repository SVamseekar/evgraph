from __future__ import annotations

from dataclasses import dataclass

from evident_core import EvidenceEdge, EvidenceGraph, Finding

from evident.reporters.json_reporter import to_dict, to_json
from evident.reporters.markdown_reporter import to_markdown
from evident.reporters.oscal_reporter import (
    to_oscal_assessment_results,
    to_oscal_assessment_results_dict,
)
from evident.reporters.sarif_reporter import to_sarif, to_sarif_dict


@dataclass(frozen=True)
class Report:
    """Wraps one EvidenceGraph and the Findings produced by evaluating it."""

    graph: EvidenceGraph
    findings: tuple[Finding, ...]

    def trace(self, node_id: str) -> list[EvidenceEdge]:
        """Delegates to EGS §6 EvidenceGraph.trace()."""
        return self.graph.trace(node_id)

    def to_dict(self) -> dict:
        return to_dict(self.graph, list(self.findings))

    def to_json(self, *, indent: int | None = 2) -> str:
        return to_json(self.graph, list(self.findings), indent=indent)

    def to_markdown(self) -> str:
        return to_markdown(self.graph, list(self.findings))

    def to_sarif_dict(self) -> dict:
        return to_sarif_dict(self.graph, list(self.findings))

    def to_sarif(self, *, indent: int | None = 2) -> str:
        return to_sarif(self.graph, list(self.findings), indent=indent)

    def to_oscal_assessment_results_dict(self) -> dict:
        return to_oscal_assessment_results_dict(self.graph, list(self.findings))

    def to_oscal_assessment_results(self, *, indent: int | None = 2) -> str:
        return to_oscal_assessment_results(self.graph, list(self.findings), indent=indent)
