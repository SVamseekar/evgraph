from __future__ import annotations

from pathlib import Path

from evgraph.adapters.dataset_manifest import DatasetManifestAdapter, DatasetManifestArtifact
from evgraph.adapters.model_card import ModelCardAdapter, ModelCardArtifacts
from evgraph.discovery import discover_rules
from evgraph.report import Report


def scan(model_card_path: str | Path, approval_path: str | Path, deployment_path: str | Path) -> Report:
    """The Model Card / JSON adapter, run through every discovered Rule, wrapped in a Report.

    Signature is explicit about the three artifacts this adapter expects rather
    than a single generic parameter — APS-Core §1.3 does not standardize an
    adapter's invocation signature, and there is no adapter-dispatch mechanism
    yet (that's future orchestration in `evgraph`, also out of APS-Core's scope).

    Every rule discovered via the "evgraph.rules" entry_point group (§discovery.py)
    is run against the graph, not just rules this package knows about by name —
    this is what lets a third-party rule pack affect scan() output purely by
    being pip installed, with no change to evgraph's source.
    """
    artifacts = ModelCardArtifacts(
        model_card_path=Path(model_card_path),
        approval_path=Path(approval_path),
        deployment_path=Path(deployment_path),
    )
    graph = ModelCardAdapter().scan(artifacts)

    findings = []
    for rule in discover_rules():
        findings.extend(rule.evaluate(graph))

    return Report(graph=graph, findings=tuple(findings))


def scan_dataset_manifest(manifest_path: str | Path) -> Report:
    """The dataset-manifest / CSV adapter, run through every discovered Rule, wrapped in a Report.

    A separate function rather than a dispatch branch inside scan(), since
    there is no adapter-selection abstraction yet (Stage 2 explicitly defers
    orchestration across heterogeneous adapters, per APS-Core §1.3).
    """
    artifact = DatasetManifestArtifact(manifest_path=Path(manifest_path))
    graph = DatasetManifestAdapter().scan(artifact)

    findings = []
    for rule in discover_rules():
        findings.extend(rule.evaluate(graph))

    return Report(graph=graph, findings=tuple(findings))
