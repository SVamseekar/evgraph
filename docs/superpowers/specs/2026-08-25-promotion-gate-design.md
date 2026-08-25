# Design: Model Promotion Gate + Reviewer Pack (Phase 1)

**Date:** 2026-08-25  
**Status:** Approved  
**Package constraint:** Stay within the existing four packages (`evgraph-core`, `evgraph-rules`, `evgraph`, `evgraph-cli`). No fifth package.

## 1. Problem

ML platform engineers need a CI-usable check that model promotion evidence is consistent (and optionally complete). Model risk / governance reviewers need the same scan as an explainable evidence pack (Markdown / SARIF / OSCAL), not a compliance certificate.

Evgraph already has adapters, rules, reporters, and a CLI that always exits 0. What is missing is a **unified promotion entry point**, an **opt-in gate** over existing `Outcome`s, and a **documented CI + reviewer workflow** — without inventing verdicts or growing the package set.

## 2. Goals and non-goals

### Goals (Phase 1)

- Opt-in CI gate: report by default; `--gate` / `--strict` when callers want non-zero exit.
- `scan_promotion` in `evgraph`: JSON-only trio **or** MLflow model/version **plus** the same JSON trio → one `Report`.
- Reuse existing reporters as a “reviewer pack” (Markdown + SARIF + OSCAL).
- Example GitHub Actions workflow showing report-always + optional gate.
- Keep `scan()` / `scan_dataset_manifest()` unchanged and working.

### Non-goals (Phase 1)

- Dataset release gate (Phase 2; same `evaluate_gate` pattern later).
- New packages (`evgraph-ci`, etc.).
- Compliance / legal verdicts, severity scores, or PASS/FAIL vocabulary in core.
- Adapter or reporter discovery (still out of scope per PES / ADR-0006).
- Changing EGS/RES epistemic model or SARIF outcome→level mapping for gating.

## 3. Audience and success criteria

| Audience | Success looks like |
| --- | --- |
| CI / ML platform | One command or Action; optional fail on inconsistency; SARIF annotations |
| Governance / MRM | Same run yields Markdown + OSCAL with citable findings |
| Library maintainers | Still four packages; gate logic not in `evgraph-core` |

Measurable: tests for gate matrix + CLI exit codes; JSON `scan_promotion` matches today’s `scan` findings; docs show both soft and strict CI usage.

## 4. Approach

**Chosen:** Unified promotion API + gate + pack inside existing `evgraph` / `evgraph-cli` (Approach 2 from brainstorm).

**Rejected:** Thin gate-only (too weak for MLflow/real promotion); new package / mini-platform (overbuild vs grounding discipline).

## 5. Architecture

Spine unchanged:

```
artifacts → adapter(s) → EvidenceGraph → discover_rules() → Findings → Report
                                                              ↓
                                                    evaluate_gate()  (optional)
                                                              ↓
                                              reporters (JSON / Markdown / SARIF / OSCAL)
```

| Package | Change |
| --- | --- |
| `evgraph-core` | No change unless a shared type proves unavoidable (prefer not). |
| `evgraph-rules` | No change unless a demonstrated promotion gap appears; reuse existing rules first. |
| `evgraph` | `evaluate_gate`, `scan_promotion`, shared evaluate helper, compose helper for multi-source graphs. |
| `evgraph-cli` | Flags and exit codes only; no business logic beyond dispatch. |

### Gate policy (researched)

Aligned with Conftest-style deny/warn and Evgraph’s “evidence over verdicts”:

| Mode | Behavior |
| --- | --- |
| Default (no `--gate`) | Always exit `0` after a successful scan (today’s behavior). |
| `--gate` | Exit `1` if any finding has `EXPECTATION_NOT_MET`. |
| `--gate --strict` | Also exit `1` if any finding has `INCONCLUSIVE`. |
| Tool / adapter / usage error | Exit `2`. |

Rationale: `EXPECTATION_NOT_MET` is demonstrated inconsistency; `INCONCLUSIVE` is missing evidence (common in the wild). Failing on inconclusive by default would block adoption; making it opt-in (`--strict`) serves governance teams that require complete packs. SARIF mapping stays as today (`NOT_MET`→`warning`, `INCONCLUSIVE`→`note`); **exit code is the gate**, not a severity rewrite in the reporter.

## 6. Public API

### Library (`evgraph`)

```python
# Existing (unchanged)
scan(model_card_path, approval_path, deployment_path) -> Report
scan_dataset_manifest(manifest_path) -> Report

# New
scan_promotion(
    *,
    model_card_path=None,
    approval_path=None,
    deployment_path=None,
    mlflow_tracking_uri=None,
    mlflow_model_name=None,
    mlflow_model_version=None,
) -> Report

evaluate_gate(
    report_or_findings,
    *,
    fail_on_inconclusive: bool = False,
) -> GateResult
```

`GateResult` (in `evgraph`, not core):

- `should_fail: bool`
- `reasons: tuple[str, ...]` — derived only from finding `rule_id` + `outcome` (+ short statement optional); no new governance semantics.

`scan_promotion` modes (keyword-only; exactly one mode per call):

1. **JSON-only** — `model_card_path`, `approval_path`, and `deployment_path` all set; all MLflow kwargs unset. Must produce the same findings as `scan()` for identical inputs (shared internal path).
2. **MLflow + JSON trio** — `mlflow_tracking_uri`, `mlflow_model_name`, `mlflow_model_version`, **and** the full JSON trio all set. Requires `evgraph[mlflow]`. Reuses `ModelCardAdapter` as-is (it always needs all three files); composes with `MLflowAdapter` output per §7. No half-adapter for “approval+deploy only” in Phase 1.

Any other combination raises `ValueError` (CLI maps to exit `2`).

Implementation sketch: adapters build node/edge lists → **one new** `EvidenceGraph` at construction time (ADR-0004) → `discover_rules()` → `Report`.

### CLI (`evgraph-cli`)

```bash
evgraph scan MODEL_CARD APPROVAL DEPLOYMENT [--format ...] [--gate] [--strict]
evgraph scan-promotion --model-card ... --approval ... --deployment ...
evgraph scan-promotion --mlflow-uri ... --model-name ... --model-version ... \
  --model-card ... --approval ... --deployment ...
```

**`--strict` requires `--gate`.** If `--strict` is passed without `--gate`, the CLI exits `2` with a usage error. `--strict` means `fail_on_inconclusive=True`.

## 7. Multi-source graph composition

Today the MLflow adapter emits a **standalone** graph (no edges to other adapters). Promotion must not mutate graphs.

**Compose rules:**

1. Concatenate nodes and edges from Model Card / approval / deployment adapter output and MLflow adapter output into one new `EvidenceGraph`, with a fresh `graph_id` / `created_at` and combined `adapter_manifest`.
2. Add linking edges **only** when identity keys match (e.g. model name / version between registry version and card/approval/deploy records).
3. Linking must declare assumptions on the orchestration helper (e.g. `PROM-001`: name/version string equality means same model version). Extraction/interpretation stays honest; no silent edges.
4. If nothing matches, nodes coexist disconnected; rules may return `INCONCLUSIVE` — that is correct evidence state, not an adapter error.

Do not put compose logic in `evgraph-core`. Keep adapters themselves unchanged in behavior for their native single-source scans.

## 8. Error handling

| Case | Result |
| --- | --- |
| Adapter cannot interpret source | `AdapterError`; CLI exit `2` |
| Missing `mlflow` extra when MLflow mode requested | Clear error directing to `pip install "evgraph[mlflow]"`; exit `2` |
| Incomplete / conflicting CLI args | Usage error; exit `2` |
| Gate tripped | Findings still emitted; exit `1` |
| Successful scan, no gate trip | Exit `0` |

## 9. Testing

- Unit: `evaluate_gate` for MET / NOT_MET / INCONCLUSIVE × `fail_on_inconclusive` on/off.
- CLI: exit codes `0` / `1` / `2` for `--gate` / `--strict` / adapter failure.
- `scan_promotion` JSON path: findings match `scan()` on example fixtures.
- MLflow path: mocked client or existing test fixtures; identity-link and no-link cases.
- Full regression: existing tests in all four packages still pass.

## 10. Documentation and examples

- Root / package READMEs: CI gate modes in plain language; “not a compliance verdict.”
- Example GitHub Actions workflow: write SARIF (and optionally Markdown/OSCAL artifacts); gate step optional / separate.
- CHANGELOG entry under the next version bump (version number chosen at implementation time).

## 11. Phase 2 (out of scope now, reserved)

Dataset release gate: reuse `evaluate_gate` + CLI flags on `scan-dataset-manifest` (or a thin `scan_dataset_release` alias). No new package.

## 12. Risks

| Risk | Mitigation |
| --- | --- |
| Linking MLflow ↔ approval invents relationships | Explicit assumptions; link only on clear identity match; prefer INCONCLUSIVE over invented edges |
| Gate feels like a compliance verdict | Docs + naming (`evaluate_gate` / `--gate`); default remain report-only |
| Scope creep into fifth package | Hard constraint in this doc |

## 13. Decisions log (brainstorm)

- Optimize for CI (A) + governance reviewers (B), phased: model promotion first, dataset later.
- Inputs: both JSON trio and MLflow behind one promotion UX.
- Fail policy: researched hybrid (report default; `--gate`; `--strict` for inconclusive).
- Stay at four packages.
