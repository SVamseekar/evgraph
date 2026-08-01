from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from evident_core.evidence_level import EvidenceLevel


@dataclass(frozen=True)
class Assumption:
    """APS-Core §3.2. A stably-identified statement of an interpretive judgment."""

    id: str
    statement: str


class Adapter(Protocol):
    """APS-Core §3.1.

    The callable that performs extraction (commonly named `scan`) is
    intentionally not part of this Protocol — its signature is adapter-defined
    (APS-Core §1.3). Only the declarations below are standardized.
    """

    name: str
    version: str
    evidence_level: EvidenceLevel
    extraction_method: str
    assumptions: list[Assumption]
    supported_source_kinds: list[str]


class AdapterError(Exception):
    """APS-Core §4.1.

    Raised for failures of interpretation (malformed input, unreadable file,
    unsupported schema version) — never for governance deficiencies in
    otherwise-valid source data (APS-Core §4.2). Must be raised with the
    underlying cause chained (`raise AdapterError(...) from exc`).
    """

    def __init__(self, adapter_name: str, adapter_version: str, message: str) -> None:
        self.adapter_name = adapter_name
        self.adapter_version = adapter_version
        self.message = message
        super().__init__(f"[{adapter_name} {adapter_version}] {message}")
