"""An MLflow model registry adapter, conforming to APS-Core v0.1.

Built against a real, locally running MLflow 3.14 tracking server — not
against documentation or memory of MLflow's API — per the same grounding
discipline used for the OSCAL reporter (docs/research/oscal-roundtrip.md).
Findings from that process are recorded in
docs/research/mlflow-adapter-validation.md.

Deliberately narrow scope (docs/ROADMAP.md Stage 4.5 Goal 2): only
RegisteredModel, ModelVersion, and Run are mapped. MLflow also exposes
experiments, metrics, params beyond what's read here, artifacts, registry
stage/alias transitions, and deployment jobs — none of those are mapped,
because no rule has yet demonstrated a need for them. This is "an MLflow
adapter," not "MLflow support" (APS-Core §1.1's grounding discipline extended
to adapter scope, not just spec scope).

Produces a standalone graph — no edges to any other adapter's output (mirrors
the dataset-manifest adapter's precedent, APS-Core Stage 2).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from evgraph_core import (
    AdapterError,
    AdapterInvocation,
    Assumption,
    EvidenceEdge,
    EvidenceGraph,
    EvidenceLevel,
    EvidenceNode,
)

ADAPTER_NAME = "evgraph-adapter-mlflow"
ADAPTER_VERSION = "0.1.0"
EVIDENCE_LEVEL = EvidenceLevel.STRUCTURAL
EXTRACTION_METHOD = "mlflow client API read"
SUPPORTED_SOURCE_KINDS = ["mlflow-tracking-server"]
ASSUMPTIONS = [
    Assumption(
        id="MLF-001",
        statement=(
            "MLflow creation_timestamp/last_updated_timestamp fields (epoch milliseconds) "
            "are interpreted as UTC datetimes"
        ),
    ),
    Assumption(
        id="MLF-002",
        statement=(
            "a ModelVersion with an empty run_id is treated as evidence that no training run "
            "is linked to this version, not as an extraction failure — MLflow's API itself "
            "permits registering a model version with no run_id (e.g. a manually uploaded "
            "artifact), so this is a real, representable state, not malformed data"
        ),
    ),
    Assumption(
        id="MLF-003",
        statement=(
            "an empty ModelVersion.description or empty RegisteredModel.tags is preserved as "
            "empty/absent, not substituted with a placeholder value"
        ),
    ),
]


@dataclass(frozen=True)
class MLflowModelSource:
    """Identifies which registered model to scan from the MLflow client this
    adapter is given. APS-Core §1.3 does not standardize an adapter's
    invocation signature — this shape is specific to what this adapter needs.
    """

    registered_model_name: str


def _epoch_millis_to_datetime(epoch_millis: int) -> datetime:
    return datetime.fromtimestamp(epoch_millis / 1000, tz=timezone.utc)


class MLflowAdapter:
    """APS-Core §3.1 Adapter."""

    name = ADAPTER_NAME
    version = ADAPTER_VERSION
    evidence_level = EVIDENCE_LEVEL
    extraction_method = EXTRACTION_METHOD
    assumptions = ASSUMPTIONS
    supported_source_kinds = SUPPORTED_SOURCE_KINDS

    def scan(self, client: Any, source: MLflowModelSource) -> EvidenceGraph:
        """Converts one MLflow RegisteredModel, its ModelVersions, and any Runs
        they reference into a standalone EvidenceGraph.

        `client` is an `mlflow.tracking.MlflowClient` instance (or anything
        exposing the same `get_registered_model`/`search_model_versions`/
        `get_run` methods) — not imported as a hard evgraph dependency, since
        `mlflow` is a development/validation dependency of this repo, not a
        runtime dependency of the `evgraph` package (docs/ROADMAP.md Stage 4.5
        Goal 2).
        """
        observed_at = datetime.now(timezone.utc)

        try:
            registered_model = client.get_registered_model(source.registered_model_name)
        except Exception as exc:
            raise AdapterError(
                adapter_name=self.name,
                adapter_version=self.version,
                message=f"could not retrieve registered model '{source.registered_model_name}'",
            ) from exc

        model_node_id = f"mlflow_model_{registered_model.name}"
        nodes = [
            EvidenceNode(
                id=model_node_id,
                type="MLflowRegisteredModel",
                observed_at=observed_at,
                source={"mlflow_registered_model_name": registered_model.name},
                evidence_level=self.evidence_level,
                attributes={
                    "name": registered_model.name,
                    "description": registered_model.description or "",
                    "created_at": _epoch_millis_to_datetime(
                        registered_model.creation_timestamp
                    ).isoformat(),
                },
            )
        ]
        edges: list[EvidenceEdge] = []

        try:
            versions = list(
                client.search_model_versions(f"name='{registered_model.name}'")
            )
        except Exception as exc:
            raise AdapterError(
                adapter_name=self.name,
                adapter_version=self.version,
                message=f"could not list model versions for '{registered_model.name}'",
            ) from exc

        for mv in versions:
            version_node_id = f"mlflow_version_{registered_model.name}_{mv.version}"
            nodes.append(
                EvidenceNode(
                    id=version_node_id,
                    type="MLflowModelVersion",
                    observed_at=observed_at,
                    source={
                        "mlflow_registered_model_name": registered_model.name,
                        "mlflow_version": mv.version,
                    },
                    evidence_level=self.evidence_level,
                    attributes={
                        "version": mv.version,
                        "status": mv.status,
                        "description": mv.description or "",
                        "source": mv.source or "",
                        "created_at": _epoch_millis_to_datetime(mv.creation_timestamp).isoformat(),
                        "has_linked_run": bool(mv.run_id),
                    },
                )
            )
            edges.append(
                EvidenceEdge(
                    source_id=version_node_id,
                    target_id=model_node_id,
                    type="MODEL_VERSION_OF",
                    observed_at=observed_at,
                )
            )

            # MLF-002: an empty run_id is evidence (no training run is linked),
            # not an interpretation failure — the adapter simply omits the
            # TRAINED_BY edge and run node rather than raising or fabricating one.
            if mv.run_id:
                run_node_id = f"mlflow_run_{mv.run_id}"
                if not any(n.id == run_node_id for n in nodes):
                    try:
                        run = client.get_run(mv.run_id)
                    except Exception as exc:
                        raise AdapterError(
                            adapter_name=self.name,
                            adapter_version=self.version,
                            message=f"model version {mv.version} references run_id "
                            f"'{mv.run_id}' but it could not be retrieved",
                        ) from exc
                    nodes.append(
                        EvidenceNode(
                            id=run_node_id,
                            type="MLflowRun",
                            observed_at=observed_at,
                            source={"mlflow_run_id": run.info.run_id},
                            evidence_level=self.evidence_level,
                            attributes={
                                "run_id": run.info.run_id,
                                "status": run.info.status,
                                "user_id": run.info.user_id or "",
                                "tags": dict(run.data.tags or {}),
                            },
                        )
                    )
                edges.append(
                    EvidenceEdge(
                        source_id=version_node_id,
                        target_id=run_node_id,
                        type="TRAINED_BY",
                        observed_at=observed_at,
                    )
                )

        return EvidenceGraph(
            graph_id=f"scan_{observed_at.isoformat()}_{uuid.uuid4().hex[:6]}",
            created_at=observed_at,
            nodes=tuple(nodes),
            edges=tuple(edges),
            adapter_manifest=(AdapterInvocation(adapter=self.name, version=self.version),),
        )
