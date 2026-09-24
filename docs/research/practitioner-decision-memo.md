# Practitioner Validation — Decision Memo (Stage 4.5 Goal 3)

**Status:** Decision aid for the project owner after interviews. Does not grant Stage 5 by itself — applies `docs/ROADMAP.md` Stage 4.5 whole-stage exit and `docs/research/validation-plan.md` (especially H3).

**Preparation:** `practitioner-outreach-kit.md`  
**Evidence store:** `practitioner-interview-log.md`  
**Prior desk research:** `practitioner-and-market-check.md` (skeptical baseline; interviews may overturn or sharpen it)

---

## What is already decided without Goal 3

| Track | Status | Implication |
| --- | --- | --- |
| H1 — OSCAL interoperability without changing EGS/RES | Met (`oscal-roundtrip.md`) | Supports **exit path B** (OSCAL-only) if practitioners do not confirm H3 |
| H2 — Real external adapter (MLflow) without changing EGS/APS | Met (`mlflow-adapter-validation.md`) | Technical foundation OK; does **not** by itself justify Stage 5 ecosystem investment |
| H3 — Recurring practitioner problem Evgraph addresses | Open until interviews | This memo |

Market/ecosystem adoption remains an **unproven hypothesis** (ADR-0007). Never invent adopters.

---

## Minimum interview bar

| Rule | Default |
| --- | --- |
| Independent conversations | **N = 5–8** before a Stage 4.5 practitioner decision |
| Stop early | Only if the same pattern (or same anti-pattern) is unambiguous by ~5 and further calls add no new classes |
| One conversation | Does not confirm H3, even if enthusiastic |
| “Looks cool” | Discard for H3 |

---

## Exit checklist (pick exactly one primary path)

### Path A — Exit Stage 4.5 via practitioners (H3 confirmed)

Use when **all** of the following hold:

- [ ] ≥5 independent interviews logged
- [ ] ≥1 **recurring** problem pattern (≥2 independent people, same problem class, in their words)
- [ ] That pattern maps to what Evgraph **already ships** (adapters → graph → rules → findings → reporters / promotion gate) — not to a hypothetical Stage 5 feature
- [ ] Anti-patterns do not dominate (majority are not “no problem,” “docs never written,” or “already solved by X”)

**Then:** Proceed toward Stage 5 **only** as scoped by the named pattern (what practitioners asked for), not by defaulting to `evgraph-provenance` / `evgraph-context` / regulatory packs. Update README/roadmap language carefully; still no ecosystem-adoption claim without a third-party adopter.

**Next human action after Path A:** Write a one-page “pattern → roadmap implication” note citing interview IDs; only then open Stage 5 design for that pattern.

---

### Path B — Exit Stage 4.5 via OSCAL-only track (H3 not confirmed; H1 stands)

Use when:

- [ ] Interviews completed to the N bar (or clearly saturated), **and**
- [ ] No recurring problem maps to Evgraph as shipped, **and**
- [ ] You still judge OSCAL Assessment Results export valuable as **interoperability evidence** independent of market adoption (already documented in `oscal-roundtrip.md`)

**Then:** Stage 4.5 may exit on whole-stage condition (2) from the roadmap. Treat Evgraph primarily as a **validated reference + interoperability demo**, not as demand-proven infrastructure. Stage 5 remains optional and should be **narrow or deferred** unless a new concrete need appears.

**Next human action after Path B:** Update README / architecture-validation hypothesis 8 to “falsified or unsupported by interviews”; state OSCAL track as the Stage 4.5 exit basis; do **not** start Stage 5 by default.

---

### Path C — Do not start Stage 5 (reposition / narrow / conclude reference value)

Use when:

- [ ] Interviews show no recurring mappable problem, **and**
- [ ] You do **not** want to treat OSCAL alone as sufficient strategic justification to expand the research track, **or**
- [ ] Dominant finding is upstream of Evgraph (no artifacts produced; fragmented ownership; commercial MRM already covers the niche)

**Then:** Do **not** invent Stage 5 work to fill the gap. Per ADR-0007 and the roadmap: reposition, narrow scope, or explicitly conclude **architectural / reference** value. Record the finding; keep the libraries maintainable; reopen only if new evidence arrives.

**Next human action after Path C:** Short ADR or README status note: “H3 unsupported; Stage 5 blocked by choice / evidence”; list any narrow maintenance-only work if needed.

---

## Quick decision table

| Interview outcome | Path |
| --- | --- |
| Recurring problem maps to shipped Evgraph | **A** |
| No recurring map; keep OSCAL as interoperability win and pause product expansion | **B** |
| No recurring map; also decline expanding on OSCAL alone | **C** |
| Recurring problem is real but **outside** current design (e.g. “force people to write cards”) | **C** (or redesign positioning) — **not** Stage 5 as currently listed |

---

## Explicit next action after N conversations

After **5–8** independent interviews (or earlier saturation):

1. Freeze the pattern board in `practitioner-interview-log.md`.
2. Check Path A / B / C above; pick one.
3. Update `docs/validation/architecture-validation.md` hypothesis 8 status with a citation to this memo + log.
4. Update `docs/ROADMAP.md` Stage 4.5 Goal 3 from OPEN to the chosen exit wording.
5. **Only if Path A:** scope Stage 5 (or a revised stage) from the pattern — do not start blocked research packages otherwise.

Until step 1–2 happen, Goal 3 remains **open** even though this preparation kit exists.
