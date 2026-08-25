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


def test_scan_default_returns_0_even_with_not_met_findings(capsys):
    exit_code = main(
        [
            "scan",
            str(MODEL_CARD_DIR / "model_card.json"),
            str(MODEL_CARD_DIR / "approval.json"),
            str(MODEL_CARD_DIR / "deployment.json"),
            "--format",
            "json",
        ]
    )
    assert exit_code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["findings"][0]["outcome"] == "EXPECTATION_NOT_MET"


def test_scan_gate_exits_1_on_not_met(capsys):
    exit_code = main(
        [
            "scan",
            str(MODEL_CARD_DIR / "model_card.json"),
            str(MODEL_CARD_DIR / "approval.json"),
            str(MODEL_CARD_DIR / "deployment.json"),
            "--gate",
            "--format",
            "json",
        ]
    )
    assert exit_code == 1
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["findings"][0]["rule_id"] == "approval-precedes-deployment"


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


def test_strict_without_gate_exits_2_for_scan(capsys):
    exit_code = main(
        [
            "scan",
            str(MODEL_CARD_DIR / "model_card.json"),
            str(MODEL_CARD_DIR / "approval.json"),
            str(MODEL_CARD_DIR / "deployment.json"),
            "--strict",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "requires --gate" in captured.err
    assert captured.out == ""


def test_strict_without_gate_exits_2_for_dataset_manifest(capsys):
    exit_code = main(
        [
            "scan-dataset-manifest",
            str(DATASET_DIR / "dataset_manifest.csv"),
            "--strict",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "requires --gate" in captured.err
    assert captured.out == ""


def test_no_command_errors():
    with pytest.raises(SystemExit):
        main([])


def test_scan_promotion_gate_exits_1_on_not_met(capsys):
    exit_code = main(
        [
            "scan-promotion",
            "--model-card",
            str(MODEL_CARD_DIR / "model_card.json"),
            "--approval",
            str(MODEL_CARD_DIR / "approval.json"),
            "--deployment",
            str(MODEL_CARD_DIR / "deployment.json"),
            "--gate",
            "--format",
            "markdown",
        ]
    )
    assert exit_code == 1
    out = capsys.readouterr().out
    assert "# Evgraph Report" in out


def test_scan_promotion_json_output(capsys):
    exit_code = main(
        [
            "scan-promotion",
            "--model-card",
            str(MODEL_CARD_DIR / "model_card.json"),
            "--approval",
            str(MODEL_CARD_DIR / "approval.json"),
            "--deployment",
            str(MODEL_CARD_DIR / "deployment.json"),
        ]
    )
    assert exit_code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["graph"]["egs_version"] == "0.1"
    assert len(data["findings"]) == 1
    assert data["findings"][0]["outcome"] == "EXPECTATION_NOT_MET"


def test_scan_promotion_default_returns_0_even_with_not_met_findings(capsys):
    exit_code = main(
        [
            "scan-promotion",
            "--model-card",
            str(MODEL_CARD_DIR / "model_card.json"),
            "--approval",
            str(MODEL_CARD_DIR / "approval.json"),
            "--deployment",
            str(MODEL_CARD_DIR / "deployment.json"),
            "--format",
            "json",
        ]
    )
    assert exit_code == 0


def test_scan_promotion_rejects_partial_args(capsys):
    exit_code = main(
        [
            "scan-promotion",
            "--model-card",
            str(MODEL_CARD_DIR / "model_card.json"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "evgraph: error:" in captured.err
    assert captured.out == ""


def test_strict_without_gate_exits_2_for_scan_promotion(capsys):
    exit_code = main(
        [
            "scan-promotion",
            "--model-card",
            str(MODEL_CARD_DIR / "model_card.json"),
            "--approval",
            str(MODEL_CARD_DIR / "approval.json"),
            "--deployment",
            str(MODEL_CARD_DIR / "deployment.json"),
            "--strict",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "requires --gate" in captured.err
    assert captured.out == ""
