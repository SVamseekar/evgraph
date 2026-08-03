# MLflow Adapter Validation Findings

**Status:** Research note recording the actual outcome of building an MLflow model-registry adapter (`docs/ROADMAP.md` Stage 4.5 Goal 2). Built and tested against a real, locally running MLflow 3.14 tracking server (`mlflow server`, SQLite backend) — not against documentation or memory of MLflow's API. Implementation: `reference/python/evgraph/src/evgraph/adapters/mlflow_adapter.py`. Test rule: `reference/python/evgraph-rules/src/evgraph_rules/model_version_has_training_provenance.py`.

---

## 1. What was tested

A local MLflow tracking server was seeded with two real scenarios via `mlflow.tracking.MlflowClient`:

- **Clean case:** a real training run (params, metrics, tags logged), registered as model version 1 of `risk-scorer`, linked via `run_id`.
- **Messy case:** model version 2 of the same model, registered directly from an S3 path with no `run_id`, no description, no tags — a real, valid MLflow state (manually uploaded artifacts, not trained through a tracked run), confirmed via `client.search_model_versions()` to return `run_id=''`, `description=''`, `tags={}` exactly as MLflow's real API returns them, not as an assumption about what it might return.

## 2. What mapped directly

- `RegisteredModel` → `EvidenceNode(type="MLflowRegisteredModel")`: `name`, `description`, `creation_timestamp` (converted from epoch milliseconds to UTC ISO 8601) all mapped with no ambiguity.
- `ModelVersion` → `EvidenceNode(type="MLflowModelVersion")`, linked to its `RegisteredModel` via a `MODEL_VERSION_OF` edge: `version`, `status`, `description`, `source` mapped directly.
- `Run` → `EvidenceNode(type="MLflowRun")`, linked from its `ModelVersion` via a `TRAINED_BY` edge, but **only when a run is actually linked** — `run_id`, `status`, `user_id`, `tags` mapped directly from the real `Run.info`/`Run.data` objects.

## 3. What required interpretation

- **Epoch-millisecond timestamps.** MLflow's `creation_timestamp`/`last_updated_timestamp` are ints, not datetimes (confirmed by direct inspection: `type(rm.creation_timestamp) == int`). Required an explicit conversion (`MLF-001`), the same category of interpretive judgment the Model Card adapter already makes for ISO 8601 strings.
- **The empty-`run_id` case.** This is the adapter's most important finding. MLflow's real API permits a `ModelVersion` with `run_id=''` — not a null, not an error, an empty string, meaning "no run is linked." Per APS-Core §4.2 (interpretation failure vs. governance deficiency), this is not malformed data the adapter should reject; it's a real, representable state. The adapter does not raise `AdapterError` for this — it sets `has_linked_run: False` on the `EvidenceNode` and simply omits the `TRAINED_BY` edge and any `MLflowRun` node. This is the exact distinction APS-Core was designed to enforce, now exercised against a real external system rather than a synthetic one.

## 4. What assumptions the adapter had to make

Three, recorded as `Assumption`s per APS-Core §3.2 (`MLF-001` through `MLF-003`): timestamp interpretation, empty-`run_id`-as-evidence, and empty-string preservation (an empty `description`/`tags` is preserved as empty, never substituted with a placeholder). All three are stated in the adapter's own docstring and `ASSUMPTIONS` list, following the same pattern as the Model Card adapter's `MC-001`/`MC-002`.

## 5. Did APS or EGS need to change?

**No.** The adapter conforms to APS-Core's `Adapter` protocol exactly as specified — same declarations (`name`, `version`, `evidence_level`, `extraction_method`, `assumptions`, `supported_source_kinds`), same `AdapterError` model, same four-step lifecycle. No new EGS structural concept was needed: `EvidenceNode`/`EvidenceEdge` accommodated MLflow's three real object types (`RegisteredModel`, `ModelVersion`, `Run`) with only new `type` strings and `attributes` keys — exactly the open-string extensibility EGS §3.2/§8 already provides for.

## 6. The unanticipated-rule test

A new rule, `model-version-has-training-provenance`, was written **after** the adapter was built, deliberately named around the graph shape (any node type ending in `"ModelVersion"`, checked for a `TRAINED_BY` edge) rather than around MLflow specifically — so it would also apply to a future, different model-registry adapter producing the same shape. Registered via the existing `"evgraph.rules"` entry_point mechanism (PES §3.1), it was picked up by `discover_rules()` with zero changes to `scan.py`, the MLflow adapter, or any core package.

Run against the real seeded server: version 1 (linked to a real run) → `EXPECTATION_MET`; version 2 (the messy, unlinked case) → `EXPECTATION_NOT_MET`. Both at `STRUCTURAL` level, computed correctly via `compute_finding_level`.

**The MLflow adapter successfully supported a rule that was not considered during adapter design. No modifications to APS, EGS, RES, or the adapter implementation were required.**

## 7. What this does and doesn't answer

This confirms **H2** from `docs/research/validation-plan.md`: APS-Core's adapter contract generalizes to a real external system's actual artifact shapes, not just the two synthetic reference adapters it was validated against in Stage 2. It says nothing about **H3** (whether anyone outside this project wants this) — that remains open, per Stage 4.5's still-pending Goal 3.

---

## Related documents

- `docs/research/validation-plan.md` — H1/H2/H3 and what this result means for Stage 4.5's exit condition.
- `docs/research/oscal-roundtrip.md` — the analogous validation note for Goal 1 (OSCAL reporter).
- `docs/ARCHITECTURE.md` ADR-0007 — the decision this stage validates.
- `reference/python/evgraph/src/evgraph/adapters/mlflow_adapter.py` — the implementation this note is about.
- `reference/python/evgraph-rules/src/evgraph_rules/model_version_has_training_provenance.py` — the unanticipated-rule test.
