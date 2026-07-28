# Rule Evaluation Specification (RES)

**Version:** 0.1 (Proposed)
**Status:** Draft — not an industry standard. This is a proposed specification for the `evident` open-source Python ecosystem. It is expected to change based on findings from the reference implementation.

---

## 1. Scope and Non-Goals

### 1.1 Scope

RES defines how a **Rule** evaluates an **Evidence Graph** (EGS) and produces **Finding**s. It specifies:

- The `Rule` interface and the invariants every rule must satisfy
- The `Finding` structure
- The evidence-level hierarchy's confidence-inheritance rule, formalized as a type invariant on `Finding.level`
- The outcome vocabulary a `Finding` may use to express agreement/disagreement with a rule's expectation
- Lifecycle and reproducibility guarantees for rule evaluation

RES exists to test one hypothesis: **that graph evaluation can produce explainable, traceable findings without ever claiming an epistemic certainty the evidence graph itself does not support, and without issuing a compliance verdict.** As with EGS, every concept here is included because a concrete case in the `evident` reference implementation required it.

### 1.2 Fundamental Principle

> **Information flow in RES is monotonic with respect to epistemic certainty. Rule evaluation must never produce a finding that is presented as more certain than either its supporting evidence or the reasoning process used to derive it.**

Every other rule in this document is a consequence of this principle, not an independent design choice. §4.3 formalizes it as a type invariant.

### 1.3 Non-Goals (v0.1)

| Deferred concept | Why deferred |
|---|---|
| **Requirement / Assessment aggregation** | RES v0.1 defines only `Rule → Finding`. It does not define how multiple findings combine into a higher-level object (a "Requirement," "Control," "Obligation," or equivalent), because no reference rule pack yet exists to demonstrate a stable aggregation pattern — whether one requirement maps to one rule or many, whether one rule satisfies multiple requirements, or whether "Requirement" is even the right abstraction versus "Control" or "Policy." Revisit once multiple reference rule packs demonstrate a common pattern. |
| **Recommendation generation** | A rule identifying a deviation does not imply it can prescribe a fix. Recommendations, if they exist, are a separate layer built on top of `Finding`, not a field within it. |
| **Rule scheduling, dispatch, and indexing** | RES defines what a rule *is* (a pure function over a graph), not how an engine schedules, parallelizes, or optimizes rule execution. That is APS/engine territory. In particular, RES v0.1 does not define a subscription or node-type-filtering mechanism — a rule receives the whole graph and uses EGS's traversal operations (EGS §6) itself. |
| **Confidence combination across findings** | If two findings about the same subject disagree or reinforce each other, RES v0.1 does not define how to combine their confidence. No reference case has required this yet; it is likely entangled with the deferred Requirement/Assessment question above. |
| **Compliance verdicts, severity, or PASS/FAIL** | Explicitly and permanently out of scope — not a "not yet," but a hard boundary. See §1.1 and the project README. A `Finding.outcome` expresses agreement with a rule's own stated expectation, never a legal or regulatory judgment. |

If a future version of RES adds any of the above, it must cite the specific reference-implementation case that required it, per §1.1.

---

## 2. Core Terminology

| Term | Definition |
|---|---|
| **Rule** | A pure function that evaluates an `EvidenceGraph` and produces zero or more `Finding`s. |
| **Reasoning Class** | An `EvidenceLevel` (EGS §3.4) declared by a rule, representing the strongest epistemic claim its reasoning *process* can support — independent of the evidence level of the nodes it happens to cite. |
| **Finding** | A rule's output: a traceable, evidence-cited statement of what was observed, together with whether it matches the rule's own declared expectation. Never a verdict. |
| **Outcome** | One of `EXPECTATION_MET`, `EXPECTATION_NOT_MET`, `INCONCLUSIVE` — see §4.2. Expresses agreement with the rule's expectation, not compliance with any external standard. |

Terms defined in EGS (`EvidenceGraph`, `EvidenceNode`, `EvidenceEdge`, `EvidenceLevel`, `trace`) are used here as defined there and are not redefined. Terms not defined in either document (`Requirement`, `Assessment`, `Recommendation`) are out of scope for RES v0.1 (§1.3).

---

## 3. Rule Model

### 3.1 Rule Interface

```
Rule:
    id: str                      # unique identifier for this rule
    name: str                    # human-readable name
    reasoning_class: EvidenceLevel   # epistemic ceiling of this rule's reasoning method

    evaluate(graph: EvidenceGraph) -> list[Finding]
```

- `evaluate` receives the complete, immutable `EvidenceGraph` (EGS §3.5, §4) and returns zero, one, or many `Finding`s.
- A rule uses the traversal operations guaranteed by EGS §6 (`neighbors`, `ancestors`, `descendants`, `trace`) to navigate the graph. RES defines no additional query mechanism.
- Rules may return findings in arbitrary order; consumers MUST NOT depend on list order to infer meaning (e.g., severity, priority, or sequence).
- `reasoning_class` is declared once per rule, not computed. It describes the method — e.g., an exact-equality/existence check declares `STRUCTURAL`; a cross-node timestamp comparison declares `CONSISTENCY`; a fuzzy-matching or pattern-based check declares `HEURISTIC`; a rule requiring human-level judgment to be reliable (including any LLM-assisted evaluation) declares `INTERPRETIVE`.

### 3.2 Rule Invariants

A conforming `Rule` implementation MUST satisfy:

1. **Purity** — no mutation of the input graph, no mutation of state shared with other rules, no side effects (no I/O, no network calls, no persistence).
2. **Evidentiary closure** — every `cited_node_ids` entry in every `Finding` a rule returns must be the `id` of a node present in the input graph. A rule must not cite evidence that does not exist in the graph it was given.
3. **Order independence** — the result of evaluating a set of independent rules must not depend on the order in which they are run.
4. **Reproducibility** — given the same `EvidenceGraph` and the same rule implementation, `evaluate` must produce identical `Finding`s. This follows from purity but is stated separately because it is the property that makes rules testable, cacheable, and auditable: a `Finding` must be re-derivable from its cited evidence at any later time, not merely produced once.

---

## 4. Finding Model

### 4.1 Finding Structure

```
Finding:
    id: str                       # unique identifier for this finding
    rule_id: str                  # id of the Rule that produced this finding
    level: EvidenceLevel           # see §4.3 — computed, never declared directly
    outcome: Outcome                # see §4.2
    statement: str                  # neutral, evidence-centric assertion of what was observed
    cited_node_ids: list[str]       # subset of the input graph's node ids (§3.2.2)
    trace: list[EvidenceEdge]       # ordered path from EGS trace(), supporting the statement
```

- `trace` is a supporting lineage path returned by EGS `trace()` (EGS §6). It is not guaranteed to be a complete subgraph containing every node in `cited_node_ids` — depending on graph topology, cited nodes may not all lie on a single traceable path back to a common root. `trace` supports the `statement`; it does not redefine or constrain `cited_node_ids`.

- `statement` is a description of what was observed, phrased neutrally. It states a fact relative to the rule's expectation (e.g., "Deployment record's `deployed_at` precedes Human Approval's `approved_at`"), not a judgment about whether that fact is acceptable. Verdict, severity, or compliance language (e.g., "violation," "non-compliant," "critical") MUST NOT appear in `statement`. A `statement` SHOULD be declarative and independently understandable without reading the rule's implementation — a reader should be able to evaluate its plausibility from the statement and cited evidence alone.
- `cited_node_ids` MUST be non-empty — a `Finding` with no cited evidence is not a finding, it is an unsupported assertion, which RES does not permit. `cited_node_ids` MUST contain unique node ids (a rule must not cite the same node twice within one finding).

### 4.2 Outcome

```
Outcome (enum):
    EXPECTATION_MET          # the observed evidence matches what the rule expected
    EXPECTATION_NOT_MET      # the observed evidence deviates from what the rule expected
    INCONCLUSIVE             # the graph does not contain enough evidence for the rule to determine a match or deviation
```

- "Expectation" belongs to the rule, not to any external legal or regulatory standard. A rule's expectation is whatever it was written to check (e.g., "approval should precede deployment"); RES makes no claim about whether that expectation is itself correct, complete, or legally required.
- `INCONCLUSIVE` exists so that a rule facing insufficient evidence produces a `Finding` saying so, rather than either fabricating a match/deviation or silently returning nothing. A rule MAY still choose to return no `Finding` at all when it has nothing to say; `INCONCLUSIVE` is for the case where the rule has something to say about *why* it can't determine an outcome.

### 4.3 Confidence-Inheritance Invariant (Finding.level)

The evidence-level hierarchy (EGS §3.4) is ordered from most to least certain:

```
STRUCTURAL  >  CONSISTENCY  >  HEURISTIC  >  INTERPRETIVE
(most certain)                        (least certain)
```

Define `leastCertain(a, b)` as the level further right in this ordering (i.e., the more epistemically weaker of the two).

> **`Finding.level` is always computed. It is never declared directly by a rule author, and no rule implementation may override it.** This is one of the defining guarantees of the entire system: no matter how a rule is written, its output cannot claim more certainty than its inputs support.

**Invariant:** `Finding.level` MUST be computed, never declared directly by the rule author, as:

```
Finding.level = leastCertain(
    rule.reasoning_class,
    leastCertain(evidence_level of every node in cited_node_ids)
)
```

In prose: a finding's level is the least-certain level among the rule's own reasoning class and the evidence levels of every node it cites. A `Finding` can never be presented as more certain than either its weakest input evidence or the reasoning method that produced it. This is the formalization of §1.2's Fundamental Principle and directly extends EGS §3.4's statement that "RES findings inherit and may only lower confidence relative to the evidence levels of the nodes they cite."

This computation is why `reasoning_class` (§3.1) is a necessary concept distinct from evidence level: a rule performing inference over purely `STRUCTURAL` nodes (e.g., pattern-matching across several structural facts to infer an undocumented change) still introduces its own epistemic weakness, which the evidence levels of its inputs alone would not capture.

---

## 5. Lifecycle

- A `Finding` is produced by exactly one `evaluate()` call of exactly one `Rule`, over exactly one `EvidenceGraph` snapshot (EGS §4). It is not mutated afterward.
- `Finding`s are not combined, aggregated, or reconciled with each other in RES v0.1 (§1.3). A consumer receives the flat list of `Finding`s produced by running a set of rules over a graph; anything beyond that list is out of scope.
- Because rules are pure and reproducible (§3.2), re-running the same rule over the same graph snapshot is always safe and must yield identical findings — RES defines no separate caching mechanism, since reproducibility makes external caching trivially correct.

---

## 6. Serialization Format

- The canonical serialization of a `Finding` is JSON, with the structure in §4.1 encoded directly.
- `EvidenceLevel` and `Outcome` values serialize as their enum name strings (e.g., `"STRUCTURAL"`, `"EXPECTATION_NOT_MET"`).
- Schema versioning: every serialized `Finding` (or collection thereof) MUST include a `res_version` field (e.g., `"res_version": "0.1"`), matching EGS's `egs_version` convention (EGS §5).
- No further compatibility guarantees are made in v0.1 (see §7).

---

## 7. Compatibility and Versioning Rules

- RES versions follow `MAJOR.MINOR`. v0.1 is pre-1.0: no compatibility guarantees are made between 0.x versions.
- A breaking change to the `Rule` or `Finding` structural model (§3, §4) requires a version bump and must cite the reference-implementation case that required it, per §1.1.
- Rule packs SHOULD declare which RES version they were built against (`res_version`, §6).

---

## 8. Extension Points

RES v0.1 defines exactly one extension point: **rule authorship itself** — any implementation of the `Rule` interface (§3.1) satisfying the invariants in §3.2 is a conforming rule, regardless of what it checks or how it traverses the graph.

No rule-pack packaging format, plugin discovery mechanism, or rule-registration protocol is defined here. Those belong to APS-Core/APS-Extensions, not RES, which governs only the evaluation contract between a graph and a rule.

---

## 9. Conformance Requirements

An implementation conforms to RES v0.1 if it:

1. Represents rules as pure functions matching the interface in §3.1, satisfying all invariants in §3.2.
2. Represents findings as the structure in §4.1, with `cited_node_ids` a non-empty subset of the input graph's node ids.
3. Computes `Finding.level` exactly per the invariant in §4.3 — never allowing a rule to declare a finding's level directly.
4. Uses only the outcome vocabulary in §4.2, with no additional verdict, severity, or compliance labels.
5. Can serialize findings to the JSON format in §6, including the `res_version` field.
6. Does not claim support for any item listed as a non-goal in §1.3 under the name "RES."

---

## 10. Illustrative Example

Continuing EGS §10's example graph (a Model Card, a Human Approval, and a Deployment Record, where the deployment's `deployed_at` precedes the approval's `approved_at`):

```json
{
  "res_version": "0.1",
  "rule_id": "approval-precedes-deployment",
  "findings": [
    {
      "id": "f1",
      "rule_id": "approval-precedes-deployment",
      "level": "CONSISTENCY",
      "outcome": "EXPECTATION_NOT_MET",
      "statement": "DeploymentRecord n3 has deployed_at (2026-06-10T00:00:00Z) preceding the approved_at (2026-06-15T00:00:00Z) of the HumanApproval n2 it requires.",
      "cited_node_ids": ["n2", "n3"],
      "trace": [
        {"source_id": "n3", "target_id": "n2", "type": "REQUIRES_APPROVAL", "observed_at": "2026-07-28T00:00:00Z"}
      ]
    }
  ]
}
```

The rule `approval-precedes-deployment` declares `reasoning_class: CONSISTENCY` (it cross-references two structural timestamps). Both cited nodes (`n2`, `n3`) are `STRUCTURAL` (EGS §10). Per §4.3: `leastCertain(CONSISTENCY, leastCertain(STRUCTURAL, STRUCTURAL)) = leastCertain(CONSISTENCY, STRUCTURAL) = CONSISTENCY`. The finding's `statement` reports the observed fact and its `outcome` reports that it deviates from the rule's expectation — it does not say "violation" or "non-compliant."

---

## Appendix: Open Questions for v0.2

Tracked here, not resolved, per the grounding discipline in §1.1 — each requires a concrete reference-implementation case before being addressed:

- Does a stable aggregation pattern emerge across multiple reference rule packs, and if so, is "Requirement" the right name for it, or would "Control," "Obligation," or "Policy" fit better? (§1.3)
- Do rules ever need to cite other findings (not just graph nodes) as input — e.g., a higher-order rule that reasons over the output of other rules? No reference case has required this; `cited_node_ids` in v0.1 only ever references `EvidenceNode`s.
- Does confidence ever need to *combine* (not just inherit downward) across multiple findings about the same subject? (§1.3)
- Should `INCONCLUSIVE` carry a structured reason code (e.g., "missing node type X"), or remain a free-text `statement`?
- Does a `Finding` represent a directly observed relationship or a conclusion inferred by rule evaluation? v0.1 treats these as the same thing (a `Finding` is simply "what a rule determined"). Future work may distinguish them if a reference implementation demonstrates value in doing so — e.g., separating "the graph contains nodes A and B with edge E" from "therefore the rule concludes X" as two different traceable claims.
