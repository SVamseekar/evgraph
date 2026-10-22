from pathlib import Path

from evgraph_core import EvidenceLevel, Outcome

from evgraph import scan

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


def test_scan_refuses_to_run_without_any_rule(monkeypatch):
    import pytest
    from importlib import import_module

    from evgraph.scan import NoRulesDiscoveredError

    scan_module = import_module("evgraph.scan")
    monkeypatch.setattr(scan_module, "discover_rules", lambda: [])
    with pytest.raises(NoRulesDiscoveredError, match="evgraph.rules"):
        scan(
            model_card_path=EXAMPLE_DIR / "model_card.json",
            approval_path=EXAMPLE_DIR / "approval.json",
            deployment_path=EXAMPLE_DIR / "deployment.json",
        )


def _scan_with(tmp_path, card: dict, approval: dict, deployment: dict):
    import json

    paths = []
    for name, data in (("card.json", card), ("approval.json", approval), ("deploy.json", deployment)):
        path = tmp_path / name
        path.write_text(json.dumps(data), encoding="utf-8")
        paths.append(path)
    return scan(*paths)


_ON_TIME = {"approver": "J. Smith", "approved_at": "2026-06-01T00:00:00Z"}
_DEPLOYED = {"deployed_at": "2026-06-10T00:00:00Z"}


def test_scan_reports_a_rejected_approval(tmp_path):
    report = _scan_with(tmp_path, {"model_name": "m"}, {**_ON_TIME, "decision": "rejected"}, _DEPLOYED)
    assert [f.outcome for f in report.findings] == [Outcome.EXPECTATION_NOT_MET]


def test_scan_reads_status_as_the_approval_decision(tmp_path):
    report = _scan_with(tmp_path, {"model_name": "m"}, {**_ON_TIME, "status": "pending"}, _DEPLOYED)
    assert [f.outcome for f in report.findings] == [Outcome.EXPECTATION_NOT_MET]


def test_scan_reports_an_approval_for_a_different_model(tmp_path):
    report = _scan_with(tmp_path, {"model_name": "m"}, {**_ON_TIME, "model_name": "other"}, _DEPLOYED)
    assert [f.outcome for f in report.findings] == [Outcome.EXPECTATION_NOT_MET]


def test_scan_reports_a_deployment_of_a_different_model(tmp_path):
    report = _scan_with(tmp_path, {"model_name": "m"}, _ON_TIME, {**_DEPLOYED, "model_name": "other"})
    assert [f.outcome for f in report.findings] == [Outcome.EXPECTATION_NOT_MET]
