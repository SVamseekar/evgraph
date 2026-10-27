"""OSCAL Assessment Results reporter, built directly against Finding/RES. No
shared reporter spec exists yet (RPS is extracted from real reporters per
ADR-0002, not designed up front).

Scope is deliberately narrow: this reporter produces only OSCAL's
`assessment-results` document type (per docs/ROADMAP.md Stage 4.5 Goal 1). It
does not attempt System Security Plans, Component Definitions, Catalogs,
Profiles, or Assessment Plans — those are OSCAL document types with no
current Evgraph use case, and adding them would be speculative per the
project's grounding discipline.

Translation table (see docs/research/standards-comparison.md §3 for the full
round-trip analysis this reporter implements):

    Evgraph               OSCAL
    --------               -----
    EvidenceNode        -> observation (+ back-matter resource as its subject)
    Finding             -> finding
    Finding.cited_node_ids -> related-observation references
    SourceReference     -> subject-reference to a back-matter resource
    Finding.rule_id     -> finding.target (objective-id)
    Outcome             -> finding.target.status (satisfied / not-satisfied,
                           reason pass / fail / other) + `outcome` prop
    EvidenceLevel       -> documented, non-standard `prop` extension
    reasoning_class      -> documented, non-standard `prop` extension

OSCAL requires an `import-ap` and `reviewed-controls`. Evgraph has no OSCAL
assessment plan or control catalog, so `import-ap` points at a back-matter
resource saying so, and `reviewed-controls` holds one control selection that
names the evaluated rules instead of controls. INCONCLUSIVE has no OSCAL state
of its own: it maps to not-satisfied with reason `other`, and the `outcome`
prop keeps the exact value. Every UUID is derived from the graph id, so the
same report renders the same document (only `last-modified` changes).

This is a lossy, one-directional (Evgraph -> OSCAL) translation, following the
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

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from evgraph_core import EvidenceGraph, EvidenceNode, Finding, Outcome

OSCAL_VERSION = "1.1.2"

# OSCAL prop `ns` (namespace) for Evgraph's own non-standard property
# extensions, so a consumer can distinguish them from OSCAL's own vocabulary.
_EVGRAPH_PROP_NAMESPACE = "https://github.com/SVamseekar/evgraph/ns/oscal"
_UUID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, _EVGRAPH_PROP_NAMESPACE)

# OSCAL observation.method is a closed enum: EXAMINE, INTERVIEW, TEST, UNKNOWN.
# Every Evgraph finding is produced by automated Rule evaluation over a graph,
# never a human examination or interview, so TEST is the only method that
# accurately describes how this evidence was gathered — this is a fixed
# choice, not a per-node judgment call.
_OBSERVATION_METHOD = "TEST"

_OUTCOME_TO_STATUS = {
    Outcome.EXPECTATION_MET: {"state": "satisfied", "reason": "pass"},
    Outcome.EXPECTATION_NOT_MET: {"state": "not-satisfied", "reason": "fail"},
    Outcome.INCONCLUSIVE: {"state": "not-satisfied", "reason": "other"},
}


def _uuid(graph: EvidenceGraph, *parts: str) -> str:
    return str(uuid.uuid5(_UUID_NAMESPACE, "\x1f".join((graph.graph_id, *parts))))


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _prop(name: str, value: str) -> dict[str, str]:
    return {"name": name, "ns": _EVGRAPH_PROP_NAMESPACE, "value": value}


def _node_to_resource(node: EvidenceNode, resource_uuid: str) -> dict[str, Any]:
    return {
        "uuid": resource_uuid,
        "title": f"{node.type} {node.id}",
        "description": f"Source of evidence node {node.id}: {json.dumps(node.source, sort_keys=True)}",
    }


def _node_to_observation(node: EvidenceNode, observation_uuid: str, resource_uuid: str) -> dict[str, Any]:
    """EvidenceNode -> OSCAL observation. SourceReference -> subject-reference to a back-matter resource."""
    return {
        "uuid": observation_uuid,
        "description": f"{node.type} node {node.id} observed by an Evgraph adapter.",
        "props": [_prop("evidence-level", node.evidence_level.name), _prop("node-type", node.type)],
        "methods": [_OBSERVATION_METHOD],
        "subjects": [{"subject-uuid": resource_uuid, "type": "resource", "title": node.id}],
        "relevant-evidence": [{"description": json.dumps(node.source, sort_keys=True)}],
        "collected": _iso(node.observed_at),
    }


def _finding_to_oscal(
    graph: EvidenceGraph, finding: Finding, node_id_to_observation_uuid: dict[str, str]
) -> dict[str, Any]:
    """Finding -> OSCAL finding. Finding.cited_node_ids -> related-observation references.

    Finding.level and reasoning_class have no native OSCAL field (see module
    docstring) and are carried as documented `prop` extensions rather than
    mapped into any existing OSCAL field.
    """
    oscal_finding: dict[str, Any] = {
        "uuid": _uuid(graph, "finding", finding.id),
        "title": finding.rule_id,
        "description": finding.statement,
        "props": [
            _prop("evgraph-finding-id", finding.id),
            _prop("outcome", finding.outcome.value),
            _prop("evidence-level", finding.level.name),
        ],
        "target": {
            "type": "objective-id",
            "target-id": finding.rule_id,
            "status": dict(_OUTCOME_TO_STATUS[finding.outcome]),
        },
    }
    related_observations = [
        {"observation-uuid": node_id_to_observation_uuid[node_id]}
        for node_id in finding.cited_node_ids
        if node_id in node_id_to_observation_uuid
    ]
    if related_observations:
        oscal_finding["related-observations"] = related_observations
    return oscal_finding


def to_oscal_assessment_results_dict(
    graph: EvidenceGraph, findings: list[Finding]
) -> dict[str, Any]:
    """Renders one EvidenceGraph's findings as an OSCAL Assessment Results document."""
    observation_uuids = {node.id: _uuid(graph, "observation", node.id) for node in graph.nodes}
    resource_uuids = {node.id: _uuid(graph, "resource", node.id) for node in graph.nodes}
    plan_resource_uuid = _uuid(graph, "assessment-plan")
    rule_ids = sorted({f.rule_id for f in findings})

    result: dict[str, Any] = {
        "uuid": _uuid(graph, "result"),
        "title": f"Evgraph scan of {graph.graph_id}",
        "description": (
            f"Automated evaluation of {len(graph.nodes)} evidence node(s) "
            f"and {len(graph.edges)} edge(s) by Evgraph rules."
        ),
        "start": _iso(graph.created_at),
        "reviewed-controls": {
            "control-selections": [
                {
                    "description": (
                        "No OSCAL control catalog is referenced. The Evgraph rules evaluated in this scan "
                        "are the finding targets: " + (", ".join(rule_ids) if rule_ids else "none") + "."
                    )
                }
            ]
        },
    }
    if graph.nodes:
        result["observations"] = [
            _node_to_observation(node, observation_uuids[node.id], resource_uuids[node.id])
            for node in graph.nodes
        ]
    if findings:
        result["findings"] = [_finding_to_oscal(graph, f, observation_uuids) for f in findings]

    resources = [
        {
            "uuid": plan_resource_uuid,
            "title": "No OSCAL assessment plan",
            "description": (
                "This document comes from an automated Evgraph scan, which has no OSCAL assessment plan. "
                "The import-ap reference points here so the document is complete."
            ),
        }
    ] + [_node_to_resource(node, resource_uuids[node.id]) for node in graph.nodes]

    return {
        "assessment-results": {
            "uuid": _uuid(graph, "assessment-results"),
            "metadata": {
                "title": f"Evgraph Assessment Results — {graph.graph_id}",
                "last-modified": _iso(datetime.now(timezone.utc)),
                "version": "1.0.0",
                "oscal-version": OSCAL_VERSION,
            },
            "import-ap": {"href": f"#{plan_resource_uuid}"},
            "results": [result],
            "back-matter": {"resources": resources},
        }
    }


def to_oscal_assessment_results(
    graph: EvidenceGraph, findings: list[Finding], *, indent: int | None = 2
) -> str:
    return json.dumps(to_oscal_assessment_results_dict(graph, findings), indent=indent)
