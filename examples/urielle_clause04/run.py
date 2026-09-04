"""Runs Urielle's Clause 04 engine and then Evgraph on the same responses, back to back.

You need evgraph-core + evgraph (already in the repo venv) and Urielle's
MVP_1 installed editable — see the README for that.

    source .venv/bin/activate
    python examples/urielle_clause04/run.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from evgraph.report import Report

from adapter import UrielleClause04Adapter, UrielleClause04Artifact
from reporter import to_urielle_sidecar_checks
from rules import Clause04QuestionHasStructuredEvidenceRule


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_urielle(handoff: Path, responses_path: Path) -> Path:
    from agentic_assessment.clause04_adapter import Clause04AssessmentResult
    from agentic_assessment.evidence_assessor import EvidenceAssessor
    from agentic_assessment.finding_generator import FindingGenerator
    from clause_04_context.run_clause04_demo import run_clause04_assessment
    import clause_04_context

    pkg = Path(clause_04_context.__file__).parent
    questions = _load_json(pkg / "questions" / "C4.json")
    responses = _load_json(responses_path)

    raw = run_clause04_assessment(
        session_id="HARBORLINE-C4-2026-09",
        questions=questions,
        responses=responses,
    )

    result = Clause04AssessmentResult(
        assessment_id="HARBORLINE-C4-2026-09",
        session_id=raw["session_id"],
        status=raw["status"],
        score=float(raw["score"]),
        evidence_records=tuple(raw["evidence_records"]),
        gaps=tuple(raw["gaps"]),
        source_result=raw,
    )

    decisions = EvidenceAssessor().assess(clause04_result=result)
    findings = FindingGenerator().generate(decisions=decisions)

    evidence_path = handoff / "urielle_evidence_records.json"
    evidence_path.write_text(
        json.dumps(list(result.evidence_records), indent=2) + "\n",
        encoding="utf-8",
    )

    summary = {
        "assessment_id": result.assessment_id,
        "session_id": result.session_id,
        "status": result.status,
        "readiness_score": result.score,
        "gaps": list(result.gaps),
        "evidence_decisions": [d.to_contract() for d in decisions],
        "findings": [f.to_contract() for f in findings],
    }
    (handoff / "urielle_assessment.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    print("=" * 70)
    print("URIELLE (his engine — score and decisions)")
    print("=" * 70)
    print(f"Readiness score: {result.score}")
    print(f"Gaps: {len(result.gaps)}")
    for gap in result.gaps:
        print(
            f"  - {gap.get('gap_type')} | {gap.get('question_id')} | "
            f"{gap.get('description')}"
        )
    print("Evidence decisions:")
    for decision in decisions:
        print(
            f"  - {decision.question_id}: {decision.decision} "
            f"(confidence={decision.confidence}, "
            f"human_review={decision.human_review_required}, "
            f"evidence_ids={list(decision.evidence_ids)})"
        )
    print(f"Draft findings: {len(findings)}")
    for finding in findings:
        print(
            f"  - {finding.finding_id} | {finding.question_id} | "
            f"{finding.human_disposition} | {finding.condition}"
        )
    print(f"Wrote {evidence_path}")
    print(f"Wrote {handoff / 'urielle_assessment.json'}")
    return evidence_path


def run_evgraph(records_path: Path, handoff: Path) -> None:
    graph = UrielleClause04Adapter().scan(
        UrielleClause04Artifact(records_path=records_path)
    )
    findings = Clause04QuestionHasStructuredEvidenceRule().evaluate(graph)
    report = Report(graph=graph, findings=tuple(findings))

    print()
    print("=" * 70)
    print("EVGRAPH (imports evgraph-core / evgraph — no ISO score)")
    print("=" * 70)
    print(report.to_markdown())

    sidecar = to_urielle_sidecar_checks(findings)
    sidecar_path = handoff / "urielle_sidecar_checks.json"
    sidecar_path.write_text(json.dumps(sidecar, indent=2) + "\n")
    print(f"Wrote {sidecar_path}")


def main() -> None:
    handoff = HERE / "handoff"
    handoff.mkdir(exist_ok=True)
    responses_path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else HERE / "artifacts" / "harborline_responses.json"
    )
    if not responses_path.is_absolute():
        responses_path = (HERE / responses_path).resolve() if not responses_path.exists() else responses_path
    print(f"Urielle input responses: {responses_path}")

    try:
        records_path = run_urielle(handoff, responses_path)
    except ImportError as exc:
        print(
            "Urielle MVP_1 is not installed in this environment.\n"
            "Install from his repo, then re-run:\n"
            "  pip install -e /path/to/Urielle-ISO42001-AIMS-Toolkit/MVP_1\n"
            f"({exc})"
        )
        print("Falling back to the static evidence snapshot.")
        records_path = HERE / "artifacts" / "clause4_evidence_records.json"

    run_evgraph(records_path, handoff)


if __name__ == "__main__":
    main()
