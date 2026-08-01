from pathlib import Path

from evident_core import EvidenceLevel, Outcome

from evident import scan

REPO_ROOT = Path(__file__).resolve().parents[4]
EXAMPLE_DIR = REPO_ROOT / "examples" / "model_card_deployment"


def test_scan_produces_expected_finding():
    report = scan(
        model_card_path=EXAMPLE_DIR / "model_card.json",
        approval_path=EXAMPLE_DIR / "approval.json",
        deployment_path=EXAMPLE_DIR / "deployment.json",
    )

    assert len(report.graph.nodes) == 3
    assert len(report.graph.edges) == 2
    assert len(report.findings) == 1

    finding = report.findings[0]
    assert finding.rule_id == "approval-precedes-deployment"
    assert finding.level == EvidenceLevel.CONSISTENCY
    assert finding.outcome == Outcome.EXPECTATION_NOT_MET


def test_report_trace_delegates_to_graph():
    report = scan(
        model_card_path=EXAMPLE_DIR / "model_card.json",
        approval_path=EXAMPLE_DIR / "approval.json",
        deployment_path=EXAMPLE_DIR / "deployment.json",
    )
    assert report.trace("n3") == report.graph.trace("n3")


def test_report_to_dict_matches_serialization_versions():
    report = scan(
        model_card_path=EXAMPLE_DIR / "model_card.json",
        approval_path=EXAMPLE_DIR / "approval.json",
        deployment_path=EXAMPLE_DIR / "deployment.json",
    )
    d = report.to_dict()
    assert d["graph"]["egs_version"] == "0.1"
    assert d["findings"][0]["res_version"] == "0.1"
