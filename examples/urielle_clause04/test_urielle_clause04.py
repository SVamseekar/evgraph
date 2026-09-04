from pathlib import Path

import pytest
from evgraph_core import AdapterError, EvidenceLevel, Outcome

from adapter import UrielleClause04Adapter, UrielleClause04Artifact
from reporter import to_urielle_sidecar_checks
from rules import Clause04QuestionHasStructuredEvidenceRule

HERE = Path(__file__).parent
RECORDS = HERE / "artifacts" / "clause4_evidence_records.json"


def test_adapter_declares_aps_core_fields():
    adapter = UrielleClause04Adapter()
    assert adapter.name == "evgraph-adapter-urielle-clause04"
    assert adapter.evidence_level == EvidenceLevel.STRUCTURAL
    assert adapter.supported_source_kinds == ["json"]
    assert adapter.assumptions


def test_scan_harborline_records():
    graph = UrielleClause04Adapter().scan(
        UrielleClause04Artifact(records_path=RECORDS)
    )
    questions = [n for n in graph.nodes if n.type == "UrielleAuditQuestion"]
    refs = [n for n in graph.nodes if n.type == "UrielleEvidenceReference"]
    assert {q.attributes["question_id"] for q in questions} == {
        "C4-Q01",
        "C4-Q02",
        "C4-Q03",
        "C4-Q04",
    }
    assert len(refs) == 3
    by_id = {q.attributes["question_id"]: q for q in questions}
    assert by_id["C4-Q01"].attributes["reference_count"] == 1
    assert by_id["C4-Q04"].attributes["reference_count"] == 0
    assert by_id["C4-Q02"].attributes["auditor_flag"] is True
    assert all(n.evidence_level == EvidenceLevel.STRUCTURAL for n in graph.nodes)


def test_rule_flags_missing_structured_evidence():
    graph = UrielleClause04Adapter().scan(
        UrielleClause04Artifact(records_path=RECORDS)
    )
    findings = Clause04QuestionHasStructuredEvidenceRule().evaluate(graph)
    by_q = {}
    for finding in findings:
        key = finding.statement.split(" ", 1)[0]
        by_q[key] = finding
    assert by_q["C4-Q01"].outcome is Outcome.EXPECTATION_MET
    assert by_q["C4-Q02"].outcome is Outcome.EXPECTATION_MET
    assert by_q["C4-Q03"].outcome is Outcome.EXPECTATION_MET
    assert by_q["C4-Q04"].outcome is Outcome.EXPECTATION_NOT_MET
    assert all(f.level is EvidenceLevel.STRUCTURAL for f in findings)


def test_sidecar_does_not_invent_urielle_decision():
    graph = UrielleClause04Adapter().scan(
        UrielleClause04Artifact(records_path=RECORDS)
    )
    findings = Clause04QuestionHasStructuredEvidenceRule().evaluate(graph)
    sidecar = to_urielle_sidecar_checks(findings)
    assert len(sidecar) == 4
    for check in sidecar:
        assert check["check_type"] == "EVIDENCE_TYPE_VALID"
        assert "decision" not in check
        assert "confidence" not in check
        assert "readiness" not in check
    statuses = {c["check_id"]: c["status"] for c in sidecar}
    assert statuses["CHK-C4-Q04-EVGRAPH-EVIDENCE"] == "FAILED"
    assert statuses["CHK-C4-Q01-EVGRAPH-EVIDENCE"] == "PASSED"


def test_missing_file_raises_adapter_error(tmp_path):
    with pytest.raises(AdapterError):
        UrielleClause04Adapter().scan(
            UrielleClause04Artifact(records_path=tmp_path / "missing.json")
        )


def test_missing_question_id_raises_adapter_error(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('[{"clause": "4.1", "question": "x"}]')
    with pytest.raises(AdapterError):
        UrielleClause04Adapter().scan(UrielleClause04Artifact(records_path=path))
