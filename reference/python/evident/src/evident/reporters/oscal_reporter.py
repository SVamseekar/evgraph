"""OSCAL Assessment Results reporter, built directly against Finding/RES. No
shared reporter spec exists yet (RPS is extracted from real reporters per
ADR-0002, not designed up front).

Scope is deliberately narrow: this reporter produces only OSCAL's
`assessment-results` document type (per docs/ROADMAP.md Stage 4.5 Goal 1). It
does not attempt System Security Plans, Component Definitions, Catalogs,
Profiles, or Assessment Plans — those are OSCAL document types with no
current Evident use case, and adding them would be speculative per the
project's grounding discipline.

Translation table (see docs/research/standards-comparison.md §3 for the full
round-trip analysis this reporter implements):

    Evident               OSCAL
    --------               -----
    EvidenceNode        -> observation
    Finding             -> finding
    Finding.trace       -> related-observation references
    SourceReference     -> subject-reference
    Outcome             -> finding.description (free text)
    EvidenceLevel       -> documented, non-standard `prop` extension
    reasoning_class      -> documented, non-standard `prop` extension

This is a lossy, one-directional (Evident -> OSCAL) translation, following the
same precedent already accepted for the SARIF reporter (RPS §3.2.3,
"translate, not invent"): OSCAL's `finding`/`observation`/`risk` schema has no
field for a computed, inherited epistemic-certainty level (confirmed by
reading OSCAL's actual metaschema, not a secondary summary — see
docs/research/standards-comparison.md §2-3). There is nowhere in OSCAL's model
to represent RES's confidence-inheritance invariant (RES §4.3) natively, so
`EvidenceLevel` and `reasoning_class` are carried as OSCAL `prop` extensions
(OSCAL's own arbitrary name/value extension mechanism) rather than mapped into
any of OSCAL's existing fields — mapping into e.g. `risk.characterization`
would misrepresent RES's epistemic-certainty concept as OSCAL's
severity/impact concept, which are not the same thing (RES explicitly excludes
severity, RES §1.3). No adapter reads OSCAL as an input format in this
version; that is a separate, later decision not entangled with this one.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from evident_core import EvidenceGraph, EvidenceNode, Finding

OSCAL_VERSION = "1.1.2"

# OSCAL prop `ns` (namespace) for Evident's own non-standard property
# extensions, so a consumer can distinguish them from OSCAL's own vocabulary.
_EVIDENT_PROP_NAMESPACE = "https://github.com/evident-org/evident/ns/oscal"

# OSCAL observation.method is a closed enum: EXAMINE, INTERVIEW, TEST, UNKNOWN.
# Every Evident finding is produced by automated Rule evaluation over a graph,
# never a human examination or interview, so TEST is the only method that
# accurately describes how this evidence was gathered — this is a fixed
# choice, not a per-node judgment call.
_OBSERVATION_METHOD = "TEST"


def _uuid() -> str:
    return str(uuid.uuid4())


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _node_to_observation(node: EvidenceNode, observation_uuid: str) -> dict[str, Any]:
    """EvidenceNode -> OSCAL observation. SourceReference -> subject-reference."""
    return {
        "uuid": observation_uuid,
        "description": f"{node.type} node {node.id} observed by an Evident adapter.",
        "methods": [_OBSERVATION_METHOD],
        "collected": node.observed_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "subjects": [{"subject-uuid": observation_uuid, "type": "evidence-node", "title": node.id}],
        "props": [
            {
                "name": "evidence-level",
                "ns": _EVIDENT_PROP_NAMESPACE,
                "value": node.evidence_level.name,
            },
            {
                "name": "node-type",
                "ns": _EVIDENT_PROP_NAMESPACE,
                "value": node.type,
            },
        ],
        "relevant-evidence": [{"description": str(node.source)}],
    }


def _finding_to_oscal(
    finding: Finding, node_id_to_observation_uuid: dict[str, str]
) -> dict[str, Any]:
    """Finding -> OSCAL finding. Finding.trace -> related-observation references.

    Finding.level and reasoning_class have no native OSCAL field (see module
    docstring) and are carried as documented `prop` extensions rather than
    mapped into any existing OSCAL field.
    """
    related_observations = [
        {"observation-uuid": node_id_to_observation_uuid[node_id]}
        for node_id in finding.cited_node_ids
        if node_id in node_id_to_observation_uuid
    ]

    return {
        "uuid": _uuid(),
        "title": finding.rule_id,
        "description": finding.statement,
        "related-observations": related_observations,
        "props": [
            {
                "name": "evident-finding-id",
                "ns": _EVIDENT_PROP_NAMESPACE,
                "value": finding.id,
            },
            {
                "name": "outcome",
                "ns": _EVIDENT_PROP_NAMESPACE,
                "value": finding.outcome.value,
            },
            {
                "name": "evidence-level",
                "ns": _EVIDENT_PROP_NAMESPACE,
                "value": finding.level.name,
            },
        ],
    }


def to_oscal_assessment_results_dict(
    graph: EvidenceGraph, findings: list[Finding]
) -> dict[str, Any]:
    """Renders one EvidenceGraph's findings as an OSCAL Assessment Results document."""
    node_id_to_observation_uuid = {node.id: _uuid() for node in graph.nodes}
    observations = [
        _node_to_observation(node, node_id_to_observation_uuid[node.id]) for node in graph.nodes
    ]
    oscal_findings = [_finding_to_oscal(f, node_id_to_observation_uuid) for f in findings]

    now = _now_iso()
    return {
        "assessment-results": {
            "uuid": _uuid(),
            "metadata": {
                "title": f"Evident Assessment Results — {graph.graph_id}",
                "last-modified": now,
                "version": "1.0.0",
                "oscal-version": OSCAL_VERSION,
            },
            "results": [
                {
                    "uuid": _uuid(),
                    "title": f"Evident scan of {graph.graph_id}",
                    "description": (
                        f"Automated evaluation of {len(graph.nodes)} evidence node(s) "
                        f"and {len(graph.edges)} edge(s) by Evident rules."
                    ),
                    "start": now,
                    "observations": observations,
                    "findings": oscal_findings,
                }
            ],
        }
    }


def to_oscal_assessment_results(
    graph: EvidenceGraph, findings: list[Finding], *, indent: int | None = 2
) -> str:
    import json

    return json.dumps(to_oscal_assessment_results_dict(graph, findings), indent=indent)
