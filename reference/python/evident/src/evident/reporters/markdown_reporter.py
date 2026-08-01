"""Human-readable Markdown reporter, built directly against Finding/RES.

No shared reporter spec exists yet (RPS is extracted from real reporters per
ADR-0002, not designed up front) — this module makes its own decisions about
what to render, independent of json_reporter and sarif_reporter. Deliberately
plain: the goal is proving what a human-facing reporter needs from Finding,
not visual polish.
"""

from __future__ import annotations

from evident_core import EvidenceGraph, Finding, Outcome

_OUTCOME_LABEL = {
    Outcome.EXPECTATION_MET: "Expectation met",
    Outcome.EXPECTATION_NOT_MET: "Expectation not met",
    Outcome.INCONCLUSIVE: "Inconclusive",
}


def _render_finding(finding: Finding) -> str:
    lines = [
        f"### {finding.rule_id}",
        "",
        f"- **Outcome:** {_OUTCOME_LABEL[finding.outcome]}",
        f"- **Level:** {finding.level.name}",
        f"- **Statement:** {finding.statement}",
        f"- **Cited evidence:** {', '.join(finding.cited_node_ids)}",
    ]
    if finding.trace:
        trace_str = " -> ".join(f"{e.source_id} --{e.type}--> {e.target_id}" for e in finding.trace)
        lines.append(f"- **Trace:** {trace_str}")
    return "\n".join(lines)


def to_markdown(graph: EvidenceGraph, findings: list[Finding]) -> str:
    """Renders one EvidenceGraph's findings as a Markdown report.

    Findings are rendered in the order given — per RES §3.1, a Rule's
    return-order carries no meaning, so this reporter does not infer any
    ordering significance (e.g. severity) from it.
    """
    lines = [
        f"# Evident Report — {graph.graph_id}",
        "",
        f"Graph observed {len(graph.nodes)} node(s) and {len(graph.edges)} edge(s).",
        "",
    ]

    if not findings:
        lines.append("No findings.")
        return "\n".join(lines)

    lines.append(f"## Findings ({len(findings)})")
    lines.append("")
    for finding in findings:
        lines.append(_render_finding(finding))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
