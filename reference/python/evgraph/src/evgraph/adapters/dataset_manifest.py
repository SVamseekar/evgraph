"""A minimal dataset-manifest / CSV adapter, conforming to APS-Core v0.1.

Deliberately structurally different from the Model Card/JSON adapter (Stage
1): a single tabular source with one row per Dataset, rather than several
linked JSON documents. Converts each CSV row into one Dataset EvidenceNode.

Produces a standalone graph — no edges to any other adapter's output. The CSV
does not declare which model(s) a dataset trained, so this adapter has no
basis to emit a cross-adapter edge (e.g. TRAINED_ON); doing so would be
inventing a relationship the source artifact doesn't state, which APS-Core
§1.2 (adapters interpret reality, they do not invent it) forbids.
"""

from __future__ import annotations

import csv
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from evgraph_core import (
    AdapterError,
    AdapterInvocation,
    Assumption,
    EvidenceGraph,
    EvidenceLevel,
    EvidenceNode,
)

ADAPTER_NAME = "evgraph-adapter-dataset-manifest"
ADAPTER_VERSION = "0.1.0"
EVIDENCE_LEVEL = EvidenceLevel.STRUCTURAL
EXTRACTION_METHOD = "csv column mapping"
SUPPORTED_SOURCE_KINDS = ["csv"]
REQUIRED_COLUMNS = ["dataset_id", "source", "license", "contains_pii"]
ASSUMPTIONS = [
    Assumption(
        id="DM-001",
        statement="contains_pii is interpreted as the literal string 'true' (case-insensitive); any other value, including empty, is false",
    ),
    Assumption(
        id="DM-002",
        statement="an empty license field is preserved as an empty string, not treated as a missing column",
    ),
]


@dataclass(frozen=True)
class DatasetManifestArtifact:
    """Path to the source CSV file this adapter expects."""

    manifest_path: Path


def _read_rows(path: Path) -> list[dict[str, str]]:
    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise AdapterError(
                    adapter_name=ADAPTER_NAME,
                    adapter_version=ADAPTER_VERSION,
                    message=f"{path} has no header row",
                )
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise AdapterError(
                    adapter_name=ADAPTER_NAME,
                    adapter_version=ADAPTER_VERSION,
                    message=f"{path} is missing required column(s): {', '.join(missing)}",
                )
            return list(reader)
    except FileNotFoundError as exc:
        raise AdapterError(
            adapter_name=ADAPTER_NAME,
            adapter_version=ADAPTER_VERSION,
            message=f"source file not found: {path}",
        ) from exc
    except csv.Error as exc:
        raise AdapterError(
            adapter_name=ADAPTER_NAME,
            adapter_version=ADAPTER_VERSION,
            message=f"{path} is not valid CSV",
        ) from exc


class DatasetManifestAdapter:
    """APS-Core §3.1 Adapter."""

    name = ADAPTER_NAME
    version = ADAPTER_VERSION
    evidence_level = EVIDENCE_LEVEL
    extraction_method = EXTRACTION_METHOD
    assumptions = ASSUMPTIONS
    supported_source_kinds = SUPPORTED_SOURCE_KINDS

    def scan(self, artifact: DatasetManifestArtifact) -> EvidenceGraph:
        """Converts each CSV row into a standalone Dataset EvidenceNode.

        A row missing dataset_id (the adapter's structural requirement for
        node identity) is an interpretation failure (APS-Core §4.2). A row
        with an empty license is not — that's incomplete governance evidence,
        represented as an empty attribute for a rule to reason about.
        """
        observed_at = datetime.now(timezone.utc)
        rows = _read_rows(artifact.manifest_path)

        nodes = []
        for i, row in enumerate(rows):
            dataset_id = row.get("dataset_id", "").strip()
            if not dataset_id:
                raise AdapterError(
                    adapter_name=self.name,
                    adapter_version=self.version,
                    message=f"row {i} in {artifact.manifest_path} has an empty dataset_id",
                )
            nodes.append(
                EvidenceNode(
                    id=f"dataset_{dataset_id}",
                    type="Dataset",
                    observed_at=observed_at,
                    source={"path": str(artifact.manifest_path), "row": i},
                    evidence_level=self.evidence_level,
                    attributes={
                        "dataset_id": dataset_id,
                        "source": row.get("source", ""),
                        "license": row.get("license", ""),
                        "contains_pii": row.get("contains_pii", "").strip().lower() == "true",
                    },
                )
            )

        return EvidenceGraph(
            graph_id=f"scan_{observed_at.isoformat()}_{uuid.uuid4().hex[:6]}",
            created_at=observed_at,
            nodes=tuple(nodes),
            edges=(),
            adapter_manifest=(AdapterInvocation(adapter=self.name, version=self.version),),
        )
