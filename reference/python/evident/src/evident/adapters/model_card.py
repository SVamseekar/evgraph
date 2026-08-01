"""A minimal Model Card / JSON adapter, conforming to APS-Core v0.1.

Converts three known-shape JSON documents (a Model Card, a human approval
record, a deployment record) into one EvidenceGraph (EGS §3.5), mirroring the
illustrative example in EGS §10.

Every node this adapter produces is declared STRUCTURAL (EGS §3.4): it reports
only what the source JSON states, with no cross-referencing or inference.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from evident_core import (
    AdapterError,
    AdapterInvocation,
    Assumption,
    EvidenceEdge,
    EvidenceGraph,
    EvidenceLevel,
    EvidenceNode,
)

ADAPTER_NAME = "evident-adapter-modelcard"
ADAPTER_VERSION = "0.1.0"
EVIDENCE_LEVEL = EvidenceLevel.STRUCTURAL
EXTRACTION_METHOD = "direct field mapping"
SUPPORTED_SOURCE_KINDS = ["json"]
ASSUMPTIONS = [
    Assumption(
        id="MC-001",
        statement="approved_at and deployed_at are interpreted as ISO 8601 timestamps",
    ),
    Assumption(
        id="MC-002",
        statement=(
            "a missing intended_use field is treated as has_intended_use: false, "
            "not as an extraction failure"
        ),
    ),
]


@dataclass(frozen=True)
class ModelCardArtifacts:
    """Paths to the three source JSON files this adapter expects.

    APS-Core §1.3 does not standardize an adapter's invocation signature —
    this shape is specific to what this adapter consumes.
    """

    model_card_path: Path
    approval_path: Path
    deployment_path: Path


def _read_json(path: Path) -> dict[str, Any]:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise AdapterError(
            adapter_name=ADAPTER_NAME,
            adapter_version=ADAPTER_VERSION,
            message=f"source file not found: {path}",
        ) from exc
    except json.JSONDecodeError as exc:
        raise AdapterError(
            adapter_name=ADAPTER_NAME,
            adapter_version=ADAPTER_VERSION,
            message=f"{path} is not valid JSON",
        ) from exc


def _require_keys(data: dict[str, Any], keys: list[str], path: Path) -> None:
    """APS-Core §4.2: missing keys the adapter structurally requires to produce
    any node at all are an interpretation failure, not governance evidence."""
    missing = [k for k in keys if k not in data]
    if missing:
        raise AdapterError(
            adapter_name=ADAPTER_NAME,
            adapter_version=ADAPTER_VERSION,
            message=f"{path} is missing required key(s): {', '.join(missing)}",
        )


class ModelCardAdapter:
    """APS-Core §3.1 Adapter."""

    name = ADAPTER_NAME
    version = ADAPTER_VERSION
    evidence_level = EVIDENCE_LEVEL
    extraction_method = EXTRACTION_METHOD
    assumptions = ASSUMPTIONS
    supported_source_kinds = SUPPORTED_SOURCE_KINDS

    def scan(self, artifacts: ModelCardArtifacts) -> EvidenceGraph:
        """Converts the three source JSON artifacts into one EvidenceGraph (EGS §3.5).

        Produces exactly the three-node, two-edge shape illustrated in EGS §10:
        a ModelCard, a HumanApproval, and a DeploymentRecord, with DEPLOYS and
        REQUIRES_APPROVAL edges from the deployment record.
        """
        observed_at = datetime.now(timezone.utc)

        model_card = _read_json(artifacts.model_card_path)
        approval = _read_json(artifacts.approval_path)
        deployment = _read_json(artifacts.deployment_path)

        _require_keys(model_card, ["model_name"], artifacts.model_card_path)
        _require_keys(approval, ["approver"], artifacts.approval_path)

        # deployed_at / approved_at may be absent: that is governance evidence
        # (APS-Core §4.2), not an interpretation failure — the adapter still
        # produces a node, just without that attribute, and the rule that
        # consumes it (RES §4.2) reports INCONCLUSIVE rather than the adapter
        # refusing to produce a graph.

        model_card_node = EvidenceNode(
            id="n1",
            type="ModelCard",
            observed_at=observed_at,
            source={"path": str(artifacts.model_card_path)},
            evidence_level=self.evidence_level,
            attributes={
                "model_name": model_card["model_name"],
                "has_intended_use": "intended_use" in model_card,
            },
        )
        approval_attributes: dict[str, Any] = {"approver": approval["approver"]}
        if "approved_at" in approval:
            approval_attributes["approved_at"] = approval["approved_at"]
        approval_node = EvidenceNode(
            id="n2",
            type="HumanApproval",
            observed_at=observed_at,
            source={"path": str(artifacts.approval_path)},
            evidence_level=self.evidence_level,
            attributes=approval_attributes,
        )
        deployment_attributes: dict[str, Any] = {}
        if "deployed_at" in deployment:
            deployment_attributes["deployed_at"] = deployment["deployed_at"]
        deployment_node = EvidenceNode(
            id="n3",
            type="DeploymentRecord",
            observed_at=observed_at,
            source={"path": str(artifacts.deployment_path)},
            evidence_level=self.evidence_level,
            attributes=deployment_attributes,
        )

        deploys_edge = EvidenceEdge(
            source_id="n3",
            target_id="n1",
            type="DEPLOYS",
            observed_at=observed_at,
        )
        requires_approval_edge = EvidenceEdge(
            source_id="n3",
            target_id="n2",
            type="REQUIRES_APPROVAL",
            observed_at=observed_at,
        )

        return EvidenceGraph(
            graph_id=f"scan_{observed_at.isoformat()}_{uuid.uuid4().hex[:6]}",
            created_at=observed_at,
            nodes=(model_card_node, approval_node, deployment_node),
            edges=(deploys_edge, requires_approval_edge),
            adapter_manifest=(AdapterInvocation(adapter=self.name, version=self.version),),
        )


def scan_model_card_artifacts(artifacts: ModelCardArtifacts) -> EvidenceGraph:
    """Module-level convenience wrapper, preserved for existing callers."""
    return ModelCardAdapter().scan(artifacts)
