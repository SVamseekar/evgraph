from __future__ import annotations

from pathlib import Path

from evgraph_core import EvidenceGraph

from evgraph.adapters.dataset_manifest import DatasetManifestAdapter, DatasetManifestArtifact
from evgraph.adapters.mlflow_adapter import MLflowAdapter, MLflowModelSource
from evgraph.adapters.model_card import ModelCardAdapter, ModelCardArtifacts
from evgraph.compose import compose_graphs
from evgraph.discovery import discover_rules
from evgraph.report import Report


def _evaluate_graph(graph: EvidenceGraph) -> Report:
    findings: list = []
    for rule in discover_rules():
        findings.extend(rule.evaluate(graph))
    return Report(graph=graph, findings=tuple(findings))


def _mlflow_client(tracking_uri: str):
    try:
        from mlflow.tracking import MlflowClient
    except ImportError as exc:
        raise ImportError(
            'MLflow promotion mode requires mlflow; pip install "evgraph[mlflow]"'
        ) from exc
    return MlflowClient(tracking_uri)


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
    return _evaluate_graph(graph)


def scan_promotion(
    *,
    model_card_path: str | Path | None = None,
    approval_path: str | Path | None = None,
    deployment_path: str | Path | None = None,
    mlflow_tracking_uri: str | None = None,
    mlflow_model_name: str | None = None,
    mlflow_model_version: str | None = None,
) -> Report:
    """Promotion-gate scan: JSON trio via ModelCardAdapter, or MLflow compose.

    Keyword-only entry point for CI promotion gates. JSON-only mode matches ``scan()``
    findings for the same three artifact paths.
    """
    _MSG = "scan_promotion requires either JSON trio only, or MLflow kwargs plus JSON trio"

    json_set = all(p is not None for p in (model_card_path, approval_path, deployment_path))
    mlflow_args = (mlflow_tracking_uri, mlflow_model_name, mlflow_model_version)
    mlflow_any = any(k is not None for k in mlflow_args)
    mlflow_set = all(k is not None for k in mlflow_args)

    if json_set and mlflow_set:
        artifacts = ModelCardArtifacts(
            model_card_path=Path(model_card_path),
            approval_path=Path(approval_path),
            deployment_path=Path(deployment_path),
        )
        card_graph = ModelCardAdapter().scan(artifacts)
        client = _mlflow_client(mlflow_tracking_uri)
        mlflow_graph = MLflowAdapter().scan(
            client,
            MLflowModelSource(registered_model_name=mlflow_model_name),
        )
        graph = compose_graphs(
            card_graph,
            mlflow_graph,
            link_model_name=mlflow_model_name,
            link_model_version=str(mlflow_model_version),
        )
        return _evaluate_graph(graph)

    if json_set and not mlflow_any:
        return scan(model_card_path, approval_path, deployment_path)

    raise ValueError(_MSG)


def scan_dataset_manifest(manifest_path: str | Path) -> Report:
    """The dataset-manifest / CSV adapter, run through every discovered Rule, wrapped in a Report.

    A separate function rather than a dispatch branch inside scan(), since
    there is no adapter-selection abstraction yet (Stage 2 explicitly defers
    orchestration across heterogeneous adapters, per APS-Core §1.3).
    """
    artifact = DatasetManifestArtifact(manifest_path=Path(manifest_path))
    graph = DatasetManifestAdapter().scan(artifact)
    return _evaluate_graph(graph)
