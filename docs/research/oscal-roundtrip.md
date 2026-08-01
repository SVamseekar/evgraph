# OSCAL Round-Trip Findings

**Status:** Research note recording the actual outcome of building the OSCAL Assessment Results reporter (`docs/ROADMAP.md` Stage 4.5 Goal 1). Confirms or challenges the predictions made on paper in `docs/research/standards-comparison.md` before any code existed. Implementation: `reference/python/evident/src/evident/reporters/oscal_reporter.py`.

---

## 1. What mapped perfectly

- **EvidenceNode → OSCAL `observation`.** Every node became one observation with no loss: `observed_at` → `collected`, `SourceReference` → `relevant-evidence.description`, `type` preserved. This was predicted in `standards-comparison.md` §3 and held exactly.
- **Finding → OSCAL `finding`.** `statement` → `description`, `rule_id` → `title`. Also predicted and held exactly.
- **`Finding.cited_node_ids` → `related-observations`.** OSCAL's UUID-reference model (`observation-uuid`) is a clean fit for RES's `cited_node_ids` — both are just "which evidence supports this conclusion," expressed as a flat list of references. No structural friction.
- **`Outcome` → `finding.description`.** `EXPECTATION_NOT_MET`'s prose statement ("DeploymentRecord n3 has deployed_at ... preceding the approved_at ...") reads naturally as OSCAL finding text without alteration. Confirms RPS's "translate, not invent" principle (RPS §3.2.3) transfers cleanly to this format too, the same way it already did for SARIF.

## 2. What required extensions

- **`EvidenceLevel` and `reasoning_class`.** Exactly as predicted: OSCAL's `observation`/`finding` schema has no field to hold "STRUCTURAL" or "CONSISTENCY." Both are carried as `prop` extensions under Evident's own namespace (`https://github.com/evident-org/evident/ns/oscal`), attached to *both* the observation (per-node evidence level) and the finding (computed `Finding.level`). This is the one place the reporter adds structure OSCAL doesn't natively have — and it's documented in the module's own docstring, not silently smuggled in.
- **`observation.methods`.** OSCAL's `method` enum (`EXAMINE`/`INTERVIEW`/`TEST`/`UNKNOWN`) required picking one fixed value (`TEST`) for every observation, since Evident's adapters are always automated extraction, never a human examination or interview. This is a real but narrow translation decision — not a gap, just a forced choice within an existing enum.

## 3. What could not be represented at all

Nothing. Every field on `Finding` and `EvidenceNode` that RES/EGS consider load-bearing made it into the OSCAL document, either natively or via a documented extension. This differs from the pre-implementation prediction in one respect: `standards-comparison.md` speculated that `Finding.level` might be awkward to place ("stuffing it into a `remarks` field... exporting metadata into an escape hatch"). In practice, OSCAL's `prop` mechanism is a first-class, schema-legal extension point (not a free-text escape hatch like `remarks` would have been), so the actual implementation is cleaner than the pre-implementation worry suggested.

## 4. Does this confirm or challenge `standards-comparison.md`?

**Confirms, with one refinement.** The paper analysis's core claim — "OSCAL has nowhere to compute RES's confidence-inheritance invariant, but nothing is lost that can't be carried as a documented extension" — held exactly under implementation. The refinement: the paper analysis undersold how well `prop` extensions fit this use case. It isn't a lossy compromise; it's a legitimate, schema-sanctioned mechanism OSCAL itself provides for exactly this purpose (vendor/tool-specific metadata that doesn't fit the core model). The reporter introduces zero new concepts into EGS or RES, required no change to either, and produces valid OSCAL structure — meeting all three of Stage 4.5 Goal 1's acceptance criteria (`docs/ROADMAP.md`).

## 5. What this does and doesn't answer

This confirms **H1** from `docs/research/validation-plan.md` (interoperability with an established standard is achievable without compromising the internal model). It says nothing about **H3** (whether anyone outside this project wants this) — that remains open, per Stage 4.5's still-pending Goal 3.

---

## Related documents

- `docs/research/standards-comparison.md` — the pre-implementation prediction this note tests against.
- `docs/research/validation-plan.md` — H1/H2/H3 and what this result means for Stage 4.5's exit condition.
- `docs/ARCHITECTURE.md` ADR-0007 — the decision this stage validates.
- `reference/python/evident/src/evident/reporters/oscal_reporter.py` — the implementation this note is about.
