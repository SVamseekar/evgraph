"""Reads Urielle's Clause 04 evidence-record JSON and turns it into an Evgraph graph.

Source shape: https://github.com/wholidi/Urielle-ISO42001-AIMS-Toolkit
(MVP_1/clause_04_context/evidence/clause4_evidence_records.json)

Only uses evgraph-core types. Doesn't score anything and doesn't call into
Urielle's own engine.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
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

ADAPTER_NAME = "evgraph-adapter-urielle-clause04"
ADAPTER_VERSION = "0.1.0"
EVIDENCE_LEVEL = EvidenceLevel.STRUCTURAL
EXTRACTION_METHOD = "direct field mapping of Urielle Clause 04 evidence records"
SUPPORTED_SOURCE_KINDS = ["json"]
ASSUMPTIONS = [
    Assumption(
        id="UR-C4-001",
        statement=(
            "Each array element is one evidence record for one Clause 04 "
            "question. If actual_evidence_references is missing we just "
            "treat it as empty, not as a failure"
        ),
    ),
    Assumption(
        id="UR-C4-002",
        statement=(
            "confidence_score and auditor_flag get copied over as-is; "
            "we don't read anything into them or treat them as a decision"
        ),
    ),
]

REQUIRED_RECORD_KEYS = ["question_id", "clause", "question"]


@dataclass(frozen=True)
class UrielleClause04Artifact:
    records_path: Path


def _read_records(path: Path) -> list[dict[str, Any]]:
    try:
        with open(path) as f:
            data = json.load(f)
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

    if not isinstance(data, list):
        raise AdapterError(
            adapter_name=ADAPTER_NAME,
            adapter_version=ADAPTER_VERSION,
            message=f"{path} must be a JSON array of evidence records",
        )
    return data


class UrielleClause04Adapter:
    name = ADAPTER_NAME
    version = ADAPTER_VERSION
    evidence_level = EVIDENCE_LEVEL
    extraction_method = EXTRACTION_METHOD
    assumptions = ASSUMPTIONS
    supported_source_kinds = SUPPORTED_SOURCE_KINDS

    def scan(self, artifact: UrielleClause04Artifact) -> EvidenceGraph:
        observed_at = datetime.now(timezone.utc)
        records = _read_records(artifact.records_path)

        nodes: list[EvidenceNode] = []
        edges: list[EvidenceEdge] = []

        for index, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                raise AdapterError(
                    adapter_name=ADAPTER_NAME,
                    adapter_version=ADAPTER_VERSION,
                    message=f"record {index} is not an object",
                )
            missing = [k for k in REQUIRED_RECORD_KEYS if k not in record]
            if missing:
                raise AdapterError(
                    adapter_name=ADAPTER_NAME,
                    adapter_version=ADAPTER_VERSION,
                    message=(
                        f"record {index} is missing required key(s): "
                        f"{', '.join(missing)}"
                    ),
                )

            question_id = str(record["question_id"])
            refs = record.get("actual_evidence_references") or []
            if refs is None:
                refs = []
            if not isinstance(refs, list):
                raise AdapterError(
                    adapter_name=ADAPTER_NAME,
                    adapter_version=ADAPTER_VERSION,
                    message=(
                        f"{question_id}: actual_evidence_references "
                        "must be a list"
                    ),
                )

            question_node_id = f"q-{question_id}"
            expected = record.get("expected_evidence") or []
            if not isinstance(expected, list):
                expected = []

            question_node = EvidenceNode(
                id=question_node_id,
                type="UrielleAuditQuestion",
                observed_at=observed_at,
                source={
                    "path": str(artifact.records_path),
                    "question_id": question_id,
                },
                evidence_level=self.evidence_level,
                attributes={
                    "question_id": question_id,
                    "clause": str(record["clause"]),
                    "title": record.get("title", ""),
                    "question": record["question"],
                    "session_id": record.get("session_id", ""),
                    "expected_evidence": expected,
                    "reference_count": len(refs),
                    "confidence_score": record.get("confidence_score"),
                    "auditor_flag": bool(record.get("auditor_flag", False)),
                    "response_source_type": record.get(
                        "response_source_type", ""
                    ),
                },
            )
            nodes.append(question_node)

            for ref_index, ref in enumerate(refs, start=1):
                if not isinstance(ref, dict):
                    raise AdapterError(
                        adapter_name=ADAPTER_NAME,
                        adapter_version=ADAPTER_VERSION,
                        message=(
                            f"{question_id}: evidence reference "
                            f"{ref_index} is not an object"
                        ),
                    )
                reference_name = str(ref.get("reference_name") or "").strip()
                ref_node_id = f"e-{question_id}-{ref_index}"
                ref_node = EvidenceNode(
                    id=ref_node_id,
                    type="UrielleEvidenceReference",
                    observed_at=observed_at,
                    source={
                        "path": str(artifact.records_path),
                        "question_id": question_id,
                        "reference_name": reference_name,
                    },
                    evidence_level=self.evidence_level,
                    attributes={
                        "question_id": question_id,
                        "reference_name": reference_name,
                        "reference_type": ref.get("reference_type", ""),
                        "extracted_from": ref.get("extracted_from", ""),
                        "has_reference_name": bool(reference_name),
                    },
                )
                nodes.append(ref_node)
                edges.append(
                    EvidenceEdge(
                        source_id=ref_node_id,
                        target_id=question_node_id,
                        type="SUPPORTS",
                        observed_at=observed_at,
                    )
                )

        return EvidenceGraph(
            graph_id=(
                f"urielle_c4_{observed_at.isoformat()}_"
                f"{uuid.uuid4().hex[:6]}"
            ),
            created_at=observed_at,
            nodes=tuple(nodes),
            edges=tuple(edges),
            adapter_manifest=(
                AdapterInvocation(adapter=self.name, version=self.version),
            ),
        )
