# Why Evident? A Comparative Analysis of Existing Standards

**Status:** Research deliverable, not a specification. Produced before Stage 5 per the project's own grounding discipline — this document exists to determine, with evidence, whether EGS/RES should adopt, adapt, integrate with, or be replaced by an existing standard, rather than assuming a new specification was warranted. Ends in a proposed ADR seed, not a final decision.

---

## 1. Executive Summary

**Verdict: Integrate, not adopt or replace.** EGS/RES should keep their internal runtime model exactly as it is, and OSCAL's `assessment-results` layer should become an export target — a fourth reporter, architecturally identical to the existing JSON/Markdown/SARIF reporters — not a replacement for EGS's graph model. This is not a defensive conclusion reached to preserve existing work: it follows from a field-by-field reading of OSCAL's actual `observation`/`finding`/`risk` schemas (fetched directly from NIST's metaschema source, not summarized secondhand). OSCAL has no computed, inherited epistemic-level concept anywhere in its model — nothing analogous to RES's confidence-inheritance invariant exists to lose by exporting into it, and nothing forces EGS to give it up. PROV-O is the correct model for `EvidenceEdge`'s *lineage* semantics and is worth citing as prior art for that specific piece, but it has no analog to `EvidenceLevel`, `Rule`, or `Finding` at all — it is not a competing runtime model, it is a competing vocabulary for one-third of what EGS does. OpenLineage is the least relevant of the three: its object model (Job/Run/Dataset/Facet) presumes a running data pipeline, which no adapter here does.

---

## 2. Comparison Table

| Capability | OSCAL | PROV-O | OpenLineage | OpenTelemetry (plugin philosophy only) | EGS / RES / RPS / PES |
|---|---|---|---|---|---|
| Runtime evidence representation | `observation`/`finding`/`risk` assemblies within `assessment-results` | `Entity` (a thing) | `Dataset` (input/output of a `Job`) | n/a (traces/spans, not governance evidence) | `EvidenceNode`/`EvidenceEdge` (EGS §3.2–3.3) |
| Graph/traversal model | None — flat lists of findings/observations linked by UUID reference (`related-observation`), no traversal API | Directed graph implied by relations; no formal cycle prohibition stated | Lineage graph *emerges* by aggregating events across runs — no first-class traversal API either | n/a | Explicit DAG with 4 guaranteed ops: `neighbors`/`ancestors`/`descendants`/`trace` (EGS §6) |
| Evidence-level / epistemic-status concept | **No analog.** `observation.method` is an enum (`EXAMINE`/`INTERVIEW`/`TEST`/`UNKNOWN`) describing *how* evidence was gathered, not how certain it is | **No analog.** No confidence/uncertainty field on any class | **No analog** | n/a | `EvidenceLevel` (STRUCTURAL→CONSISTENCY→HEURISTIC→INTERPRETIVE), computed and inherited (RES §4.3) |
| Immutable snapshot semantics | Not specified — `assessment-results` is a document; nothing mandates immutability of a `result` once produced | Not specified as a mutability constraint | Explicitly additive/event-sourced (`START`, `COMPLETE`, ... events accumulate) — opposite model: mutation-by-append, not snapshot | n/a | Immutable once constructed; union at construction time (EGS §4, ADR-0004) |
| Trace/lineage | `related-observation`/`associated-risk` are bare UUID references — no path/edge object, no ordering | This *is* PROV-O's core purpose: `wasDerivedFrom`/`wasGeneratedBy`/`used` chains | Lineage graph woven from Job/Dataset edges across events | n/a | `trace()` returns an ordered `list[EvidenceEdge]` (EGS §6) |
| Rule/finding evaluation model | `finding` is authored (by a human assessor or a tool that "generated" it via `origin`), not computed by an invariant; `related-observation`/`associated-risk` are asserted links, not derived | No rule/finding concept at all | No rule/finding concept at all | n/a | `Rule.evaluate(graph) -> list[Finding]`; `Finding.level` is computed, never declared (RES §4.3) |
| Serialization | JSON, XML, and YAML, all first-class | RDF (Turtle, JSON-LD, etc.) — ontology-native | JSON (event-based) | n/a | JSON only in v0.1 (EGS §5) |
| Plugin/discovery model | No entry_point-style discovery; content-authoring tooling only | n/a (an ontology, not a runtime) | `Facets` — arbitrary extra metadata attached to core objects, not a discovery mechanism | Instrumentation libraries auto-register with a collector via SDK conventions — closest real analog to PES's entry_point approach | `"evident.rules"` Python entry_point group (PES §3.1) |

---

## 3. Round-Trip Analysis (EGS §10 / RES §10 worked example)

The scenario: a `ModelCard` node (n1), a `HumanApproval` node (n2, `approved_at: 2026-06-15`), a `DeploymentRecord` node (n3, `deployed_at: 2026-06-10`), a `REQUIRES_APPROVAL` edge n3→n2. The rule `approval-precedes-deployment` (`reasoning_class: CONSISTENCY`) produces `Finding.level = CONSISTENCY`, `outcome: EXPECTATION_NOT_MET`.

**Into OSCAL, field by field:**

- n2 and n3 → two OSCAL `observation`s. Each observation needs `method` (closest fit: `TEST`, since this was an automated check, not an inspection or interview) and `collected` (maps to `observed_at`). Straightforward — EGS's `SourceReference` maps naturally onto `subject-reference`.
- The rule's conclusion → one OSCAL `finding`, with `related-observation` entries pointing at both observation UUIDs. Structurally this works.
- **Where it breaks:** OSCAL's `finding` has no field to carry `Finding.level`. There is no slot for "CONSISTENCY" anywhere in the schema — not on `finding`, not on `observation`, not on `risk`. You could stuff it into a `remarks` field or a custom `prop` (OSCAL's `property` assembly does allow arbitrary name/value extension pairs), but that is exporting metadata into an escape hatch, not representing it in the model. More importantly: OSCAL has **no mechanism to compute** a finding's level from its observations' levels, because observations don't have levels to compute from. RES's confidence-inheritance invariant (`leastCertain(reasoning_class, cited node levels)`) has literally nowhere to attach on the OSCAL side. Exporting the *outcome* (`EXPECTATION_NOT_MET`) is trivial (maps to a `finding.description` and an unstructured `status`-like statement); exporting the *epistemic status* of that outcome is not representable without a custom property extension.
- **The reverse direction is easier and lossless in the other direction**: any OSCAL `observation`/`finding`/`risk` document could be read by an adapter into `EvidenceNode`s at `evidence_level: STRUCTURAL` (an OSCAL document's existence and stated contents are objective facts) with `attributes` carrying the OSCAL fields verbatim. Nothing is lost going OSCAL → EGS; something is lost going EGS/RES → OSCAL unless a property extension is used.

**Into PROV-O:** n1/n2/n3 map cleanly to `Entity`; the adapter maps to `Activity` (`wasGeneratedBy`); `REQUIRES_APPROVAL` isn't a native PROV-O relation, but `wasDerivedFrom` misrepresents it (approval doesn't derive from deployment). PROV-O has no `Rule`/`Finding`/`Outcome` concept whatsoever — a `Finding` isn't a provenance assertion, it's an evaluation result, which is simply outside PROV-O's scope. There's nothing to lose here because PROV-O was never trying to solve RES's problem.

---

## 4. Identified Gaps

**What EGS/RES express that these standards cannot cleanly represent:**
- A computed, non-overridable confidence/certainty ceiling that inherits from both evidence and reasoning method (RES §4.3 / ADR-0005). This does not exist in OSCAL, PROV-O, or OpenLineage in any form — not even as an unstructured convention.
- A hard, type-enforced ban on verdict language (`Outcome` has no PASS/FAIL). OSCAL's `finding.description` is free markup text — nothing stops an assessor from writing "PASS" into it. RES enforces the ban structurally; OSCAL does not (and, per its stated purpose serving FedRAMP assessors producing SARs, arguably shouldn't — assessors *are* supposed to render judgment, unlike Evident's rules).

**What these standards have that EGS/RES lack:**
- OSCAL has a mature `risk`/`characterization`/`mitigating-factor` model — genuine severity/impact semantics — that RES deliberately excludes (RES §1.3, "Compliance verdicts, severity ... permanently out of scope"). This is a scope difference, not a gap Evident failed to fill.
- OSCAL has three first-class serializations (XML/JSON/YAML) versus EGS's JSON-only v0.1.
- PROV-O has 15+ years of tooling, reasoners, and cross-domain adoption for the specific sub-problem of "what produced this and from what" — genuinely more mature than EGS's four traversal ops for that narrow slice.

---

## 5. N×M Interoperability Hypothesis

This is the crux question and the one prior research left open. Testing the hypothesis directly: **"evidence sources × governance consumers."**

Sources: MLflow, LangSmith, GitHub, CI systems, model registries, dataset catalogs. Consumers: rule packs (EU AI Act, ISO 42001, internal policy), reporters (JSON, Markdown, SARIF, OSCAL-as-reporter), possibly a future OSCAL/GRC-tool integration. If this framing holds, Evident's IR removes the N×M integration cost of every source writing a bespoke exporter for every consumer.

**Does it hold up under scrutiny? Partially, and the honest answer is: not yet demonstrated, only plausible.** The Arrow/OpenTelemetry precedent had a *measured, pre-existing* integration cost multiple parties were independently paying before the IR existed (every DB team already maintaining N serialization adapters; every observability vendor already maintaining bespoke instrumentation per language). No equivalent has been measured here. Two adapters and two rules is not evidence of an N×M problem — it's evidence that the *contract* between one adapter and one rule works, which Stage 1–2 already proved. The N×M claim requires showing that a *third party* (not Evident's own reference implementation) was independently building redundant point-to-point integrations between a governance artifact source and a governance consumer, and chose Evident's IR to avoid it. That hasn't happened. **Concrete verdict: no measured N×M pressure exists yet. The hypothesis is plausible and worth stating as the project's working thesis, but it is currently a hypothesis, not a demonstrated fact, and ADR-0001's own citation of Arrow/OpenTelemetry overstates this by analogy rather than by evidence.**

---

## 6. Decision Recommendation: Integrate

Testing the specific hypothesis posed: *"EGS is Evident's internal runtime model; OSCAL assessment-results becomes an export target (a reporter), not a replacement for EGS."*

**This hypothesis survives the round-trip analysis.** Section 3 shows the EGS→OSCAL direction loses exactly one thing (the computed `Finding.level`, recoverable only via a non-standard property extension) and gains exactly one thing (interoperability with the FedRAMP/NIST tooling ecosystem that already consumes OSCAL). That is precisely the shape of a legitimate reporter: RPS §3.2.3 already requires a reporter to "translate, not invent" — mapping `Finding.level` into an OSCAL `prop` extension is a translation (lossy in the same documented way SARIF's `level` mapping is already lossy and already disclosed, RPS §1.2), not an invention of new governance semantics. Adopting OSCAL as the *internal* model would require giving up the confidence-inheritance invariant entirely, since OSCAL has nowhere to compute it — that would be Replace, and Replace is not justified by anything in this analysis. Adapting OSCAL syntax without its semantics would just be reinventing EGS with extra ceremony. **Integrate is the only option consistent with what was actually found.**

---

## ADR Candidate — OSCAL as an export target, not a replacement for EGS

**Decision (proposed):** `evident` gains a fourth reporter, `oscal_reporter`, mapping `EvidenceGraph`/`Finding` into OSCAL `assessment-results` (`observation` per cited node, `finding` per `Finding`, `Finding.level`/`reasoning_class` carried in a documented `prop` extension). EGS/RES's internal model is unchanged. No adapter reads OSCAL as an input format yet — that's a separate, later decision, not entangled with this one.

**Reasoning:** A field-by-field reading of OSCAL's actual metaschema (not secondary summaries) shows no computed epistemic-level concept exists in OSCAL to adopt in place of RES's confidence-inheritance invariant, and no structural reason EGS needs to give up its model to interoperate with OSCAL-consuming tooling (FedRAMP-adjacent GRC platforms). This mirrors RPS's already-accepted precedent (SARIF `level` as a documented, lossy structural translation of `Outcome`) rather than introducing a new class of decision.

**Alternatives considered:** Replace EGS's model with OSCAL's (rejected — Section 3 shows this discards the confidence-inheritance invariant with no compensating capability gained, since OSCAL has no equivalent to recover it into); do nothing until a concrete OSCAL-consuming user appears (defensible under the Grounding Discipline, but the round-trip analysis is cheap and now already done — building the reporter is a small, bounded cost relative to the interoperability optionality it buys).

**Status:** Proposed — not accepted. This is a recommendation for the project owner to ratify or reject, consistent with `docs/ARCHITECTURE.md` §6's decision-log format; it is not self-executing.
