from evgraph_core import EvidenceLevel, Finding, Outcome
from evgraph.gate import evaluate_gate


def _f(rule_id: str, outcome: Outcome) -> Finding:
    return Finding(
        id="f1",
        rule_id=rule_id,
        level=EvidenceLevel.STRUCTURAL,
        outcome=outcome,
        statement="test",
        cited_node_ids=("n1",),
    )


def test_gate_passes_when_only_expectation_met():
    result = evaluate_gate([_f("r", Outcome.EXPECTATION_MET)])
    assert result.should_fail is False
    assert result.reasons == ()


def test_gate_fails_on_expectation_not_met():
    result = evaluate_gate([_f("approval-precedes-deployment", Outcome.EXPECTATION_NOT_MET)])
    assert result.should_fail is True
    assert any("EXPECTATION_NOT_MET" in r for r in result.reasons)


def test_gate_ignores_inconclusive_by_default():
    result = evaluate_gate([_f("r", Outcome.INCONCLUSIVE)])
    assert result.should_fail is False


def test_gate_fails_on_inconclusive_when_strict():
    result = evaluate_gate([_f("r", Outcome.INCONCLUSIVE)], fail_on_inconclusive=True)
    assert result.should_fail is True
