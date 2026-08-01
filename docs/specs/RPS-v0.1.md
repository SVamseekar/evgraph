# Reporting Protocol Specification (RPS)

**Version:** 0.1 (Proposed)
**Status:** Draft — extracted, not designed in advance. Unlike EGS/RES/APS-Core (Type A, specified before implementation, per ADR-0002), RPS is a Type B/emergent specification: it codifies only what the reference implementation's three reporters (JSON, Markdown, SARIF) already demonstrated in common. It is expected to be thinner than the Type A specs, and to grow only as further reporters demonstrate more shared structure.

---

## 1. Scope and Non-Goals

### 1.1 Scope

RPS defines the contract every **Reporter** in the reference implementation was observed to satisfy:

- The two inputs every reporter needs (an `EvidenceGraph` and a `list[Finding]`) and nothing more
- The one behavioral constraint every reporter already followed: findings are rendered without inferring meaning from their list order
- That a reporter is a pure transformation — it reads `Finding`/`EvidenceGraph` fields and produces output; it never mutates them or re-derives new claims about them

RPS does **not** define a common output type, a shared base class, a plugin/registration mechanism, or a required set of output fields beyond the two inputs above. None of that was demonstrated as shared — see §1.2.

### 1.2 What Was Actually Observed (the grounding for this document)

Three reporters exist in the reference implementation: `json_reporter` (`to_dict`/`to_json`), `markdown_reporter` (`to_markdown`), and `sarif_reporter` (`to_sarif_dict`/`to_sarif`). Comparing them directly:

| Property | JSON | Markdown | SARIF |
|---|---|---|---|
| Input | `(EvidenceGraph, list[Finding])` | `(EvidenceGraph, list[Finding])` | `(EvidenceGraph, list[Finding])` |
| Output shape | flat `{graph, findings}` dict | prose with per-finding headings | nested `runs[].results[]` |
| `Finding.level` handling | serialized as-is (`EvidenceLevel.name`) | rendered as-is | placed in a `properties` extension field, not SARIF's own `level` |
| `Finding.outcome` handling | serialized as-is | rendered as a human label | mapped into SARIF's own `level` vocabulary (a translation, not a re-interpretation — see the SARIF reporter's own documentation on why `EXPECTATION_NOT_MET` → `warning` is a structural, not severity, mapping) |
| Order sensitivity | none | none (documented) | none |
| Mutates input | no | no | no |

The only things genuinely common across all three are: the two-input shape, purity, and order-independence. Everything else — output type, vocabulary, structural shape — differs completely reporter to reporter. RPS v0.1 reflects exactly that: a thin contract, not a rich one, because a rich one was not demonstrated.

### 1.3 Non-Goals (v0.1)

| Deferred concept | Why deferred |
|---|---|
| **A common `Reporter` base class or Protocol with a standardized method name** | The three reference reporters use different function names and different return types (`dict`, `str`, `dict`/`str`) suited to their own output format. Forcing a common method signature (e.g., `render(graph, findings) -> str`) would require SARIF and JSON reporters — whose most useful form is a `dict` for further processing, not a pre-serialized string — to adopt a shape that doesn't fit their actual use. No reference case demonstrates a need for reporters to be interchangeable behind one interface. |
| **A required/standardized set of Finding fields a reporter must render** | The three reporters use different subsets and different combinations of `Finding`'s fields (e.g., SARIF pushes `level` into an extension property, Markdown renders it as a heading field). No reference case demonstrates a common minimum. |
| **Reporter discovery/registration** | Belongs to PES (Stage 4), once real extension points exist from Stages 2–3 to generalize from (ADR-0002). |
| **Output validation against a target schema** | RPS does not require a reporter to validate its own output (e.g., against the SARIF JSON Schema). The reference SARIF reporter does not do this; introducing a validation requirement now would be speculative. |
| **Streaming/incremental rendering** | All three reference reporters render a complete `list[Finding]` at once. No reference case demonstrates a need for incremental output. |

If a future version of RPS adds any of the above, it must cite the specific reference reporter that required it, mirroring the grounding discipline used in EGS/RES/APS-Core.

---

## 2. Core Terminology

| Term | Definition |
|---|---|
| **Reporter** | A pure function (or small module of functions) that takes an `EvidenceGraph` and a `list[Finding]` and produces output in some target format. RPS does not standardize the function's name or return type. |

Terms defined in EGS (`EvidenceGraph`) and RES (`Finding`, `Outcome`, `EvidenceLevel`) are used here as defined there.

---

## 3. Reporter Contract

### 3.1 Inputs

Every conforming reporter accepts exactly two logical inputs:

```
(graph: EvidenceGraph, findings: list[Finding]) -> <reporter-defined output>
```

RPS does not standardize the output type. The reference implementation demonstrates two: a `dict` (JSON, SARIF — useful for further programmatic processing) and a `str` (Markdown, and JSON/SARIF's own string-serialization convenience wrappers).

### 3.2 Behavioral Requirements

A conforming reporter MUST:

1. **Treat `findings` order as insignificant.** Per RES §3.1, a `Rule`'s return order carries no meaning; a reporter must not infer or display any ordering-derived property (severity, priority, sequence) that isn't already present in the `Finding` data itself.
2. **Not mutate its inputs.** `graph` and `findings` are read, never written to or replaced.
3. **Translate, not invent, semantics.** A reporter may map `Finding` fields into its target format's own vocabulary (e.g., SARIF's `level`), but the mapping must be a deterministic function of fields RES already defines (`outcome`, `level`) — never of a rule's identity, a finding's content, or any other signal RES doesn't expose. This directly extends RES's confidence-inheritance discipline and APS-Core's interpretation/governance-deficiency boundary into the reporting layer: **a reporter must not introduce governance semantics (severity, risk, compliance judgment) that are absent from the `Finding`s it renders.**

### 3.3 What Is Not Required

RPS v0.1 does not require a reporter to: render every field of `Finding`, produce output conforming to any external schema, expose a specific function or class name, or be swappable with another reporter behind a common interface. Each of these may become a requirement in a future RPS version if a concrete reporter demonstrates the need (§1.3).

---

## 4. Compatibility and Versioning Rules

- RPS versions independently of EGS, RES, and APS — the same independence rule established in APS-Core §5.
- A breaking change to the reporter contract (§3) requires a version bump and must cite the reference reporter that required it.

---

## 5. Conformance Requirements

An implementation conforms to RPS v0.1 only if it:

1. Accepts `(EvidenceGraph, list[Finding])` as its two logical inputs (§3.1).
2. Does not infer meaning from `findings` list order (§3.2.1).
3. Does not mutate `graph` or `findings` (§3.2.2).
4. Does not introduce governance semantics (severity, risk, compliance judgment) absent from the `Finding`s it renders (§3.2.3).

---

## 6. Illustrative Comparison

See §1.2's table — this document's own grounding is the illustrative example. Unlike EGS/RES/APS-Core, RPS does not include a separate worked example, since the reference reporters (`reference/python/evident/src/evident/reporters/`) already are the example.

---

## Appendix: Open Questions for v0.2

- Do future reporters (e.g., HTML, JUnit XML — both still deferred per `docs/ROADMAP.md` Stage 3's own scope note that HTML is presentation-layer-over-Markdown-semantics and not worth building before RPS existed) reveal a genuinely common output shape that would justify a shared `Reporter` interface, contradicting §1.3's current non-goal?
- Should RPS eventually require reporters to declare which `Finding` fields they render, so a consumer can know in advance whether a given reporter is "lossy" relative to the full `Finding`?
- Does severity-as-policy (mentioned in the SARIF reporter's own documentation as a hypothetical future layer above RES, not part of RPS) ever get standardized, and if so, does it belong in RPS, a future rule-pack-level concept, or neither?

---

## Related documents

- `docs/ARCHITECTURE.md` — ADR-0002 (Type A vs. Type B specification timing), which RPS's extraction directly follows.
- `docs/ROADMAP.md` — Stage 3 defines what RPS is scoped to extract from.
- `docs/specs/RES-v0.1.md` — `Finding`/`Outcome`/`EvidenceLevel`, the structures every reporter renders.
- `reference/python/evident/src/evident/reporters/` — the three reporters this specification was extracted from.
