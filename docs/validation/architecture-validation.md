# Architecture Validation Summary

**Status:** Living summary, not a specification. This is the single document to read to understand what has actually been demonstrated about Evident's architecture versus what remains an open hypothesis. It does not introduce new claims — every row cites the stage, test, or research note where the evidence actually lives. Update it when a hypothesis's status changes; do not use it as a place to argue for a status it doesn't have evidence for yet.

---

## Validated hypotheses

| # | Hypothesis | Status | Evidence |
|---|---|---|---|
| 1 | A canonical graph representation (nodes/edges, epistemically leveled) can represent heterogeneous governance artifacts and support deterministic rule evaluation producing traceable, non-verdict findings. | ✅ Validated | Stage 1 — `evident-core`, one adapter, one rule, one reporter; RES §10's worked example reproduced exactly (`docs/ROADMAP.md` Stage 1). |
| 2 | APS-Core's `Adapter` contract generalizes across structurally different artifact shapes without adapter-specific carve-outs. | ✅ Validated | Stage 2 — Model Card/JSON and dataset-manifest/CSV adapters, both conforming with no spec changes (`docs/ROADMAP.md` Stage 2). |
| 3 | Rule packs and reporters can be distributed as independent packages without violating the layered architecture. | ✅ Validated | Stage 3 — `evident-rules` extracted as its own package; three reporters (JSON/Markdown/SARIF) coexist on the same `Finding` list (`docs/ROADMAP.md` Stage 3). |
| 4 | A third-party rule pack can be discovered and affect `scan()` output purely by being installed, with zero changes to any `evident-*` package. | ✅ Validated | Stage 4 — real entry_point-based discovery; a scratch third-party package (`third-party-rule`) proved and cleanly reverted (`docs/ROADMAP.md` Stage 4). |
| 5 | EGS/RES's internal model (in particular `EvidenceLevel` and RES's confidence-inheritance invariant) is not redundant with an existing governance-evidence standard, and can interoperate with one without being replaced by it. | ✅ Validated | Stage 4.5 Goal 1 — OSCAL Assessment Results reporter; field-by-field round-trip against the real OSCAL metaschema, zero changes to EGS/RES (`docs/research/oscal-roundtrip.md`). |
| 6 | APS-Core's adapter contract survives contact with a real, unmodified external production system, including that system's messy/incomplete real states. | ✅ Validated | Stage 4.5 Goal 2 — MLflow adapter, built and tested against a real MLflow 3.14 server; the empty-`run_id` case (a real MLflow state) represented as evidence, not an adapter failure. |
| 7 | An independently authored rule, unanticipated during adapter design, can evaluate an adapter's graph output with zero changes to the adapter, EGS, RES, or APS-Core. | ✅ Validated | Stage 4.5 Goal 2 — `model-version-has-training-provenance`, written after and independently of the MLflow adapter, discovered automatically, correctly distinguished clean vs. messy model versions (`docs/research/mlflow-adapter-validation.md`). |

## Open hypotheses

| # | Hypothesis | Status | What would resolve it |
|---|---|---|---|
| 8 | Practitioners who actually own AI governance evidence day to day (ML platform engineers, MLOps engineers, model risk managers, AI governance leads) recognize a real, recurring problem that Evident's architecture addresses. | ⏳ Open | Stage 4.5 Goal 3 — direct practitioner conversations, one question ("what problem, if any, would this solve for you?"), looking for a recurring pattern across independent conversations, not positive feedback (`docs/ROADMAP.md` Stage 4.5, `docs/research/validation-plan.md` H3). This is explicitly not a coding task and requires the project owner to run it directly. |
| 9 | A genuine N×M interoperability pressure (analogous to what justified Arrow/OpenTelemetry) exists for AI governance evidence specifically. | ⏳ Open, and explicitly not yet demonstrated | An independent third party — not this project's own reference implementation — is shown to be building redundant point-to-point integrations between a governance evidence source and a governance evidence consumer, and adopts Evident's IR to avoid it (`docs/research/standards-comparison.md` §5). |

---

## What this table does and doesn't say

**Validated** means: built, tested against real or realistic conditions (including a real external system in #6–7), and the specific claim held without requiring a workaround, carve-out, or spec change. It does not mean "proven correct forever" — per `docs/ARCHITECTURE.md`'s Grounding Discipline, any of these could still be revised if a future concrete case demonstrates a gap, the same way ADR-0005 corrected an earlier RES design flaw.

**Open** means exactly that — not "probably true," not "likely false." Hypotheses 8 and 9 are the only two remaining claims in this project that are not yet backed by evidence either way. Per `docs/ARCHITECTURE.md` ADR-0007, no claim of market necessity or ecosystem adoption should be treated as established until one of these resolves.

**What changes if hypothesis 8 or 9 resolves negatively:** per `docs/ROADMAP.md` Stage 4.5's exit condition, that is not treated as project failure — it is treated the same way any other falsified hypothesis in this project has been treated (e.g., RES's Requirement/Assessment aggregation question, ADR-0006): as a recorded, evidence-based finding that informs what happens next, rather than something to route around quietly.

---

## Related documents

- `docs/ARCHITECTURE.md` — the constitution and full decision log (ADRs) each validated hypothesis traces back to.
- `docs/ROADMAP.md` — the stage-by-stage record each row cites.
- `docs/research/` — `standards-comparison.md`, `practitioner-and-market-check.md`, `validation-plan.md`, `oscal-roundtrip.md`, `mlflow-adapter-validation.md` — the underlying research and validation notes.
