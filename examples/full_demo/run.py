"""One five-minute, end-to-end demo of everything Evident's reference
implementation does today. No explanation needed to run it — just:

    pip install -e reference/python/evident-core
    pip install -e reference/python/evident-rules
    pip install -e reference/python/evident
    pip install mlflow   # only needed for the MLflow section below
    python examples/full_demo/run.py

What this script does, source by source:

  1. Model Card / JSON  -> scan()                 -> approval-precedes-deployment
  2. Dataset manifest / CSV -> scan_dataset_manifest() -> dataset-manifest-complete
  3. MLflow (a real, ephemeral local tracking server this script starts itself,
     seeds with one clean and one messy model version, and tears down when
     done) -> MLflowAdapter -> model-version-has-training-provenance

Every rule below is auto-discovered via the "evident.rules" entry_point group
(reference/python/evident/src/evident/discovery.py) — none of them is
hardcoded into this script.

Every Report is then rendered through all four reporters (JSON, Markdown,
SARIF, OSCAL Assessment Results) to show the same Finding data translated
into each format without any of the underlying evidence changing.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
REPO_ROOT = HERE.parents[1]


def _print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def _print_all_formats(report) -> None:
    print("\n--- JSON ---")
    print(report.to_json())
    print("\n--- Markdown ---")
    print(report.to_markdown())
    print("\n--- SARIF ---")
    print(report.to_sarif())
    print("\n--- OSCAL Assessment Results ---")
    print(report.to_oscal_assessment_results())


def run_model_card_section() -> None:
    from evident import scan

    _print_header("1. Model Card / JSON  ->  approval-precedes-deployment")
    example_dir = REPO_ROOT / "examples" / "model_card_deployment"
    report = scan(
        example_dir / "model_card.json",
        example_dir / "approval.json",
        example_dir / "deployment.json",
    )
    _print_all_formats(report)


def run_dataset_manifest_section() -> None:
    from evident import scan_dataset_manifest

    _print_header("2. Dataset manifest / CSV  ->  dataset-manifest-complete")
    example_dir = REPO_ROOT / "examples" / "dataset_manifest"
    report = scan_dataset_manifest(example_dir / "dataset_manifest.csv")
    _print_all_formats(report)


def run_mlflow_section() -> None:
    try:
        import mlflow  # noqa: F401
    except ImportError:
        print(
            "\n(Skipping MLflow section: `pip install mlflow` to include it. "
            "This is a demo/dev-only dependency, never a runtime dependency "
            "of the `evident` package itself.)"
        )
        return

    _print_header("3. MLflow (real, ephemeral local server)  ->  model-version-has-training-provenance")

    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "mlflow",
            "server",
            "--host",
            "127.0.0.1",
            "--port",
            "5099",
            "--backend-store-uri",
            "sqlite:////tmp/evident_demo_mlflow.db",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(5)  # give the ephemeral server a moment to come up

        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri("http://127.0.0.1:5099")
        client = MlflowClient()

        mlflow.set_experiment("evident-demo")
        with mlflow.start_run(run_name="demo-training-run") as run:
            mlflow.log_metric("accuracy", 0.94)
            run_id = run.info.run_id

        model_name = "evident-demo-model"
        client.create_registered_model(model_name, description="Demo model for Evident's full_demo example")
        client.create_model_version(name=model_name, source=f"runs:/{run_id}/model", run_id=run_id)
        # A second, messy version registered with no run_id at all — a real,
        # valid MLflow state (a manually uploaded artifact), not an error.
        client.create_model_version(name=model_name, source="s3://demo-bucket/manual-upload")

        from evident.adapters.mlflow_adapter import MLflowAdapter, MLflowModelSource
        from evident.discovery import discover_rules
        from evident.report import Report

        graph = MLflowAdapter().scan(client, MLflowModelSource(registered_model_name=model_name))
        findings = []
        for rule in discover_rules():
            findings.extend(rule.evaluate(graph))
        report = Report(graph=graph, findings=tuple(findings))
        _print_all_formats(report)
    finally:
        server.terminate()
        server.wait(timeout=10)


if __name__ == "__main__":
    run_model_card_section()
    run_dataset_manifest_section()
    run_mlflow_section()

    _print_header("Done")
    print(
        "Three different source shapes (JSON documents, a CSV manifest, a live "
        "MLflow server), normalized through three adapters into one EvidenceGraph "
        "shape, evaluated by rules discovered automatically at runtime, and "
        "rendered through four independent reporters — with zero changes to "
        "evident-core, EGS, or RES anywhere in this script."
    )
