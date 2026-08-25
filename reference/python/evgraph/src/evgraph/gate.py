from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Union

from evgraph_core import Finding, Outcome

from evgraph.report import Report

ReportOrFindings = Union[Report, Iterable[Finding]]


@dataclass(frozen=True)
class GateResult:
    should_fail: bool
    reasons: tuple[str, ...]


def evaluate_gate(
    report_or_findings: ReportOrFindings,
    *,
    fail_on_inconclusive: bool = False,
) -> GateResult:
    findings = (
        list(report_or_findings.findings)
        if isinstance(report_or_findings, Report)
        else list(report_or_findings)
    )
    reasons: list[str] = []
    for f in findings:
        if f.outcome is Outcome.EXPECTATION_NOT_MET:
            reasons.append(f"{f.rule_id}: {f.outcome.value}: {f.statement}")
        elif fail_on_inconclusive and f.outcome is Outcome.INCONCLUSIVE:
            reasons.append(f"{f.rule_id}: {f.outcome.value}: {f.statement}")
    return GateResult(should_fail=bool(reasons), reasons=tuple(reasons))
