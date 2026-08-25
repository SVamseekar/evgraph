# Model Promotion Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in CI gate and `scan_promotion` API (JSON-only or MLflow + JSON trio) inside the existing four packages, plus CLI flags, docs, and a sample GitHub Action.

**Architecture:** Keep the adapter → graph → `discover_rules()` → `Report` spine. Put `evaluate_gate` / `GateResult` and promotion orchestration in `evgraph` (not `evgraph-core`). Compose multi-adapter graphs by building a new immutable `EvidenceGraph`. CLI stays a thin wrapper; exit codes implement gate policy without changing SARIF mappings.

**Tech Stack:** Python 3.10+, existing `evgraph` / `evgraph-cli` / `evgraph-core` / `evgraph-rules`, pytest, optional `mlflow` extra, GitHub Actions YAML example.

**Spec:** `docs/superpowers/specs/2026-08-25-promotion-gate-design.md`

## Global Constraints

- Stay within four packages; no `evgraph-ci` or other new top-level package.
- Do not change `evgraph-core` unless absolutely unavoidable (prefer zero changes).
- Do not change SARIF outcome→level mapping for gating; exit code is the gate.
- Default CLI behavior remains exit `0` after a successful scan (no `--gate`).
- `--strict` requires `--gate`; otherwise CLI usage error exit `2`.
- Gate trips → exit `1`; adapter/tool/usage errors → exit `2`.
- Activate venv before commands: `source .venv/bin/activate`
- Run package tests from that package directory (e.g. `cd reference/python/evgraph && pytest -q`).
- No compliance verdict language in user-facing copy.

## File map

| File | Responsibility |
| --- | --- |
| `reference/python/evgraph/src/evgraph/gate.py` | `GateResult`, `evaluate_gate` |
| `reference/python/evgraph/src/evgraph/compose.py` | Merge graphs + identity link edges + PROM assumptions |
| `reference/python/evgraph/src/evgraph/scan.py` | Shared `_evaluate_graph`; `scan_promotion`; refactor `scan` / `scan_dataset_manifest` |
| `reference/python/evgraph/src/evgraph/__init__.py` | Export new public symbols |
| `reference/python/evgraph/tests/test_gate.py` | Gate matrix tests |
| `reference/python/evgraph/tests/test_compose.py` | Compose / link / no-link tests |
| `reference/python/evgraph/tests/test_scan_promotion.py` | JSON parity + MLflow mode (mocked client) |
| `reference/python/evgraph-cli/src/evgraph_cli/main.py` | `--gate`, `--strict`, `scan-promotion`, exit codes |
| `reference/python/evgraph-cli/tests/test_main.py` | CLI exit-code and usage tests |
| `examples/promotion_gate/README.md` + workflow snippet | Reviewer pack + CI example |
| `CHANGELOG.md`, package/root READMEs | Document gate modes |

---

### Task 1: `evaluate_gate` + `GateResult`

**Files:**
- Create: `reference/python/evgraph/src/evgraph/gate.py`
- Create: `reference/python/evgraph/tests/test_gate.py`
- Modify: `reference/python/evgraph/src/evgraph/__init__.py`

**Interfaces:**
- Consumes: `evgraph_core.Finding`, `evgraph_core.Outcome`; optionally `Report` (duck-type via `.findings`)
- Produces: `GateResult(should_fail: bool, reasons: tuple[str, ...])`, `evaluate_gate(report_or_findings, *, fail_on_inconclusive: bool = False) -> GateResult`

- [ ] **Step 1: Write the failing tests**

```python
# reference/python/evgraph/tests/test_gate.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd reference/python/evgraph && pytest tests/test_gate.py -q`  
Expected: FAIL (import / module missing)

- [ ] **Step 3: Implement `gate.py`**

```python
# reference/python/evgraph/src/evgraph/gate.py
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
```

- [ ] **Step 4: Export from `__init__.py`**

Add `evaluate_gate`, `GateResult` to imports and `__all__`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd reference/python/evgraph && pytest tests/test_gate.py -q`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add reference/python/evgraph/src/evgraph/gate.py \
  reference/python/evgraph/tests/test_gate.py \
  reference/python/evgraph/src/evgraph/__init__.py
git commit -m "$(cat <<'EOF'
feat(evgraph): add evaluate_gate for opt-in CI gating

EOF
)"
```

---

### Task 2: Shared `_evaluate_graph` helper

**Files:**
- Modify: `reference/python/evgraph/src/evgraph/scan.py`
- Test: existing `tests/test_scan.py` (regression only)

**Interfaces:**
- Consumes: `EvidenceGraph`, `discover_rules()`, `Report`
- Produces: `_evaluate_graph(graph: EvidenceGraph) -> Report` used by `scan`, `scan_dataset_manifest`, later `scan_promotion`

- [ ] **Step 1: Extract helper and refactor callers**

In `scan.py`:

```python
def _evaluate_graph(graph: EvidenceGraph) -> Report:
    findings: list = []
    for rule in discover_rules():
        findings.extend(rule.evaluate(graph))
    return Report(graph=graph, findings=tuple(findings))
```

Replace duplicated loops in `scan` and `scan_dataset_manifest` with `return _evaluate_graph(graph)`.

- [ ] **Step 2: Run regression**

Run: `cd reference/python/evgraph && pytest tests/test_scan.py tests/test_discovery.py -q`  
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add reference/python/evgraph/src/evgraph/scan.py
git commit -m "$(cat <<'EOF'
refactor(evgraph): share _evaluate_graph for scan entry points

EOF
)"
```

---

### Task 3: `scan_promotion` JSON-only mode

**Files:**
- Modify: `reference/python/evgraph/src/evgraph/scan.py`
- Modify: `reference/python/evgraph/src/evgraph/__init__.py`
- Create: `reference/python/evgraph/tests/test_scan_promotion.py`

**Interfaces:**
- Consumes: `ModelCardAdapter`, `_evaluate_graph`
- Produces: `scan_promotion(*, model_card_path=None, approval_path=None, deployment_path=None, mlflow_tracking_uri=None, mlflow_model_name=None, mlflow_model_version=None) -> Report`

- [ ] **Step 1: Write failing tests**

```python
# reference/python/evgraph/tests/test_scan_promotion.py
from pathlib import Path
import pytest
from evgraph import scan, scan_promotion

REPO_ROOT = Path(__file__).resolve().parents[4]
EXAMPLE_DIR = REPO_ROOT / "examples" / "model_card_deployment"


def test_scan_promotion_json_matches_scan():
    kwargs = dict(
        model_card_path=EXAMPLE_DIR / "model_card.json",
        approval_path=EXAMPLE_DIR / "approval.json",
        deployment_path=EXAMPLE_DIR / "deployment.json",
    )
    a = scan(**kwargs)
    b = scan_promotion(**kwargs)
    assert [f.outcome for f in a.findings] == [f.outcome for f in b.findings]
    assert [f.rule_id for f in a.findings] == [f.rule_id for f in b.findings]


def test_scan_promotion_rejects_partial_args():
    with pytest.raises(ValueError):
        scan_promotion(model_card_path=EXAMPLE_DIR / "model_card.json")
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `cd reference/python/evgraph && pytest tests/test_scan_promotion.py -q`

- [ ] **Step 3: Implement JSON-only `scan_promotion`**

Validation logic:

- `json_set = all three path kwargs set`
- `mlflow_set = all three mlflow kwargs set`
- If `json_set` and not any mlflow kwarg: same as `scan` path via adapter + `_evaluate_graph`
- If `mlflow_set` and `json_set`: defer to Task 5 (raise `NotImplementedError` temporarily **only if** you split commits; prefer implement Task 4–5 before leaving a stub — if implementing Tasks 3–5 in one agent session, complete compose first then wire both modes)
- Else: `raise ValueError("scan_promotion requires either JSON trio only, or MLflow kwargs plus JSON trio")`

For this task alone, implement JSON-only fully; if MLflow kwargs present, `raise ValueError` until Task 5 (document in test that MLflow mode is Task 5). Prefer adding MLflow tests only in Task 5.

- [ ] **Step 4: Export `scan_promotion` from `__init__.py`**

- [ ] **Step 5: Run tests — expect PASS**

Run: `cd reference/python/evgraph && pytest tests/test_scan_promotion.py -q`

- [ ] **Step 6: Commit**

```bash
git add reference/python/evgraph/src/evgraph/scan.py \
  reference/python/evgraph/src/evgraph/__init__.py \
  reference/python/evgraph/tests/test_scan_promotion.py
git commit -m "$(cat <<'EOF'
feat(evgraph): add scan_promotion JSON-only mode

EOF
)"
```

---

### Task 4: Graph compose + identity linking

**Files:**
- Create: `reference/python/evgraph/src/evgraph/compose.py`
- Create: `reference/python/evgraph/tests/test_compose.py`

**Interfaces:**
- Consumes: `EvidenceGraph`, `EvidenceNode`, `EvidenceEdge`, `AdapterInvocation` from `evgraph_core`
- Produces:
  - `PROMOTION_ASSUMPTIONS: list` with id `PROM-001`
  - `compose_graphs(*graphs: EvidenceGraph, link_model_name: str | None = None, link_model_version: str | None = None) -> EvidenceGraph`

**Linking rule (PROM-001):** If `link_model_name` is set, find `ModelCard` nodes whose `attributes["model_name"] == link_model_name` and `MLflowModelVersion` nodes whose registered name (from `source["mlflow_registered_model_name"]` or id pattern) equals `link_model_name` and `attributes["version"] == str(link_model_version)`. For each pair, add edge `ModelCard --REFERS_TO_REGISTRY_VERSION--> MLflowModelVersion`. If no pair matches, add **no** link edges (disconnected graph is valid).

Re-id collision safety: if node ids collide across graphs, prefix non-first graphs’ node ids (and rewrite edges) before merge — ModelCard uses `n1`/`n2`/`n3`; MLflow uses `mlflow_*` so collisions are unlikely; still implement a uniqueness check and prefix with `{graph_id}_` or `g{i}_` if needed.

- [ ] **Step 1: Write failing tests**

```python
# Use two tiny EvidenceGraph fixtures: one ModelCard named "risk-scorer",
# one MLflowModelVersion for risk-scorer version "1".
# assert compose with link_model_name="risk-scorer", link_model_version="1"
#   yields exactly one REFERS_TO_REGISTRY_VERSION edge
# assert mismatched names yield zero link edges but combined node counts
```

- [ ] **Step 2: Run — expect FAIL**

Run: `cd reference/python/evgraph && pytest tests/test_compose.py -q`

- [ ] **Step 3: Implement `compose.py`**

Build new `EvidenceGraph` with fresh `graph_id` (`uuid`), `created_at=now(UTC)`, concatenated nodes/edges/manifest, plus optional link edges. Do not mutate inputs.

- [ ] **Step 4: Run — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add reference/python/evgraph/src/evgraph/compose.py \
  reference/python/evgraph/tests/test_compose.py
git commit -m "$(cat <<'EOF'
feat(evgraph): compose evidence graphs with optional registry links

EOF
)"
```

---

### Task 5: `scan_promotion` MLflow + JSON trio mode

**Files:**
- Modify: `reference/python/evgraph/src/evgraph/scan.py`
- Modify: `reference/python/evgraph/tests/test_scan_promotion.py`

**Interfaces:**
- Consumes: `MLflowAdapter`, `MLflowModelSource`, `compose_graphs`, `ModelCardAdapter`, `_evaluate_graph`
- Produces: full `scan_promotion` per spec (both modes)

- [ ] **Step 1: Write failing tests**

Reuse `FakeMlflowClient` patterns from `tests/test_mlflow_adapter.py` (import helpers or duplicate minimal fake in this test file). Patch/inject client creation:

Prefer making `scan_promotion` accept an optional private/test hook only if needed — cleaner approach: extract `_mlflow_client(tracking_uri)` and monkeypatch it in tests:

```python
def test_scan_promotion_mlflow_composes(monkeypatch):
    # monkeypatch evgraph.scan._mlflow_client to return FakeMlflowClient(...)
    # model name must match model_card.json model_name OR use temp JSON with matching name
    report = scan_promotion(
        model_card_path=...,
        approval_path=...,
        deployment_path=...,
        mlflow_tracking_uri="http://test",
        mlflow_model_name="risk-scorer-v3",
        mlflow_model_version="1",
    )
    types = {n.type for n in report.graph.nodes}
    assert "ModelCard" in types
    assert "MLflowModelVersion" in types
```

Also test: missing mlflow import path raises clear error mentioning `pip install "evgraph[mlflow]"` (simulate by monkeypatching import to fail).

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement MLflow branch in `scan_promotion`**

```python
def _mlflow_client(tracking_uri: str):
    try:
        from mlflow.tracking import MlflowClient
    except ImportError as exc:
        raise ImportError(
            'MLflow promotion mode requires mlflow; pip install "evgraph[mlflow]"'
        ) from exc
    return MlflowClient(tracking_uri)

# Then:
# card_graph = ModelCardAdapter().scan(...)
# mlflow_graph = MLflowAdapter().scan(client, MLflowModelSource(name))
# graph = compose_graphs(card_graph, mlflow_graph, link_model_name=..., link_model_version=...)
# return _evaluate_graph(graph)
```

Note: `MLflowAdapter.scan` loads **all** versions for the registered model; linking uses `mlflow_model_version` for `REFERS_TO_REGISTRY_VERSION` only. Other version nodes remain in the graph as evidence.

- [ ] **Step 4: Run promotion + compose + scan tests**

Run: `cd reference/python/evgraph && pytest tests/test_scan_promotion.py tests/test_compose.py tests/test_scan.py -q`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add reference/python/evgraph/src/evgraph/scan.py \
  reference/python/evgraph/tests/test_scan_promotion.py
git commit -m "$(cat <<'EOF'
feat(evgraph): support MLflow+JSON scan_promotion mode

EOF
)"
```

---

### Task 6: CLI `--gate` / `--strict` on existing commands

**Files:**
- Modify: `reference/python/evgraph-cli/src/evgraph_cli/main.py`
- Modify: `reference/python/evgraph-cli/tests/test_main.py`
- Modify: `reference/python/evgraph-cli/README.md` (exit code section)

**Interfaces:**
- Consumes: `evaluate_gate`, existing `scan` / `scan_dataset_manifest`
- Produces: exit `0`/`1`/`2` per spec

- [ ] **Step 1: Write failing CLI tests**

```python
def test_scan_gate_exits_1_on_not_met(capsys):
    code = main([
        "scan",
        str(EXAMPLE_DIR / "model_card.json"),
        str(EXAMPLE_DIR / "approval.json"),
        str(EXAMPLE_DIR / "deployment.json"),
        "--gate",
        "--format", "json",
    ])
    assert code == 1
    # stdout still contains findings / report


def test_strict_without_gate_exits_2():
    code = main(["scan", "...", "...", "...", "--strict"])
    assert code == 2
```

Use real example paths like existing tests. For exit `0` without `--gate`, keep asserting current behavior.

Catch `AdapterError` / `ValueError` / `SystemExit` from argparse carefully — prefer `parser.error` only for argparse; for `--strict` without `--gate`, return `2` after parse with a message on stderr.

- [ ] **Step 2: Run — expect FAIL**

Run: `cd reference/python/evgraph-cli && pytest tests/test_main.py -q`

- [ ] **Step 3: Implement flags**

- Add `--gate` / `--strict` to `scan` and `scan-dataset-manifest` parsers.
- After printing report: if `--strict` and not `--gate` → print usage message to stderr, return `2`.
- If `--gate`: `gate = evaluate_gate(report, fail_on_inconclusive=args.strict); return 1 if gate.should_fail else 0`
- Wrap adapter failures: return `2`

- [ ] **Step 4: Update CLI README exit-code section** to match researched policy (report default; gate optional; not a compliance verdict).

- [ ] **Step 5: Run — expect PASS**

- [ ] **Step 6: Commit**

```bash
git add reference/python/evgraph-cli/src/evgraph_cli/main.py \
  reference/python/evgraph-cli/tests/test_main.py \
  reference/python/evgraph-cli/README.md
git commit -m "$(cat <<'EOF'
feat(evgraph-cli): add --gate and --strict exit codes

EOF
)"
```

---

### Task 7: CLI `scan-promotion` subcommand

**Files:**
- Modify: `reference/python/evgraph-cli/src/evgraph_cli/main.py`
- Modify: `reference/python/evgraph-cli/tests/test_main.py`

**Interfaces:**
- Consumes: `scan_promotion`, same gate flags / format flag
- Produces: `evgraph scan-promotion` per spec CLI shapes

- [ ] **Step 1: Write failing tests for JSON-only `scan-promotion` + gate**

```python
code = main([
    "scan-promotion",
    "--model-card", str(EXAMPLE_DIR / "model_card.json"),
    "--approval", str(EXAMPLE_DIR / "approval.json"),
    "--deployment", str(EXAMPLE_DIR / "deployment.json"),
    "--gate",
    "--format", "markdown",
])
assert code == 1
```

- [ ] **Step 2: Implement subparser** with `--model-card`, `--approval`, `--deployment`, `--mlflow-uri`, `--model-name`, `--model-version`, `--format`, `--gate`, `--strict`. Call `scan_promotion(...)`. Map `ValueError` / `ImportError` / `AdapterError` → exit `2`.

- [ ] **Step 3: Run full CLI tests**

Run: `cd reference/python/evgraph-cli && pytest -q`

- [ ] **Step 4: Commit**

```bash
git add reference/python/evgraph-cli/src/evgraph_cli/main.py \
  reference/python/evgraph-cli/tests/test_main.py
git commit -m "$(cat <<'EOF'
feat(evgraph-cli): add scan-promotion subcommand

EOF
)"
```

---

### Task 8: Docs, example workflow, changelog

**Files:**
- Create: `examples/promotion_gate/README.md`
- Create: `examples/promotion_gate/github-actions.yml` (example workflow; not necessarily installed under `.github/` unless desired — prefer example path to avoid changing repo CI unexpectedly)
- Modify: `README.md` (root) — short CI gate section
- Modify: `reference/python/evgraph/README.md`
- Modify: `CHANGELOG.md` — add `## [Unreleased]` with Added bullets
- Optional: mark design status Approved in the spec header

- [ ] **Step 1: Write example README** showing:
  1. Report-only scan
  2. `--gate` / `--strict`
  3. Writing Markdown + SARIF + OSCAL as reviewer pack
  4. Explicit “not a compliance verdict”

- [ ] **Step 2: Write example GitHub Actions YAML** that installs packages, runs `evgraph scan ... --format sarif`, uploads artifact; optional separate job/step with `--gate`.

- [ ] **Step 3: Update READMEs + CHANGELOG**

- [ ] **Step 4: Full regression**

```bash
source .venv/bin/activate
cd reference/python/evgraph-core && pytest -q
cd ../evgraph-rules && pytest -q
cd ../evgraph && pytest -q
cd ../evgraph-cli && pytest -q
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add examples/promotion_gate README.md \
  reference/python/evgraph/README.md \
  reference/python/evgraph-cli/README.md \
  CHANGELOG.md \
  docs/superpowers/specs/2026-08-25-promotion-gate-design.md
git commit -m "$(cat <<'EOF'
docs: document promotion gate and reviewer pack workflow

EOF
)"
```

---

## Spec coverage checklist

| Spec requirement | Task |
| --- | --- |
| `evaluate_gate` / `GateResult` | 1 |
| Default exit 0; `--gate`; `--strict` requires `--gate` | 6–7 |
| Exit 1 / 2 semantics | 6–7 |
| `scan_promotion` JSON-only | 3 |
| `scan_promotion` MLflow + JSON trio | 5 |
| Compose without mutating; PROM-001 links | 4 |
| Clear mlflow extra error | 5 |
| Keep `scan` / `scan_dataset_manifest` | 2–3 |
| Reviewer pack via existing reporters | 8 (docs/example; APIs already exist) |
| Four packages only | All |
| No SARIF mapping change | (no task touches sarif_reporter) |
| Phase 2 dataset gate deferred | (out of plan) |

## Self-review notes

- No TBD placeholders left in task steps.
- `scan_promotion` signature matches the spec.
- Linking uses ModelCard `model_name` + MLflow version attributes (model card has no version field today — version comes from the MLflow kwargs / version node).
- Tasks 3–5 are ordered so JSON mode ships before MLflow; do not leave `NotImplementedError` in main if finishing Task 5 in the same effort.
