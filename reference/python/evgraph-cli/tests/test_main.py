import json
from pathlib import Path

import pytest

from evgraph_cli.main import main

REPO_ROOT = Path(__file__).resolve().parents[4]
MODEL_CARD_DIR = REPO_ROOT / "examples" / "model_card_deployment"
DATASET_DIR = REPO_ROOT / "examples" / "dataset_manifest"


def test_scan_json_output(capsys):
    exit_code = main(
        [
            "scan",
            str(MODEL_CARD_DIR / "model_card.json"),
            str(MODEL_CARD_DIR / "approval.json"),
            str(MODEL_CARD_DIR / "deployment.json"),
        ]
    )
    assert exit_code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["graph"]["egs_version"] == "0.1"
    assert len(data["findings"]) == 1


def test_scan_markdown_output(capsys):
    main(
        [
            "scan",
            str(MODEL_CARD_DIR / "model_card.json"),
            str(MODEL_CARD_DIR / "approval.json"),
            str(MODEL_CARD_DIR / "deployment.json"),
            "--format",
            "markdown",
        ]
    )
    out = capsys.readouterr().out
    assert "# Evgraph Report" in out


def test_scan_sarif_output(capsys):
    main(
        [
            "scan",
            str(MODEL_CARD_DIR / "model_card.json"),
            str(MODEL_CARD_DIR / "approval.json"),
            str(MODEL_CARD_DIR / "deployment.json"),
            "--format",
            "sarif",
        ]
    )
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["version"] == "2.1.0"


def test_scan_oscal_output(capsys):
    main(
        [
            "scan",
            str(MODEL_CARD_DIR / "model_card.json"),
            str(MODEL_CARD_DIR / "approval.json"),
            str(MODEL_CARD_DIR / "deployment.json"),
            "--format",
            "oscal",
        ]
    )
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "assessment-results" in data
    assert data["assessment-results"]["metadata"]["oscal-version"] == "1.1.2"


def test_scan_dataset_manifest(capsys):
    exit_code = main(["scan-dataset-manifest", str(DATASET_DIR / "dataset_manifest.csv")])
    assert exit_code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data["findings"]) == 2


def test_no_command_errors():
    with pytest.raises(SystemExit):
        main([])
