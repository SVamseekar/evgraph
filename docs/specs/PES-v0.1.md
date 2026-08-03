# Plugin & Extension Specification (PES)

**Version:** 0.1 (Proposed)
**Status:** Draft — extracted, not designed in advance. Like RPS, PES is a Type B/emergent specification (ADR-0002): it documents the one concrete discovery mechanism the reference implementation built and ran (`evgraph/src/evgraph/discovery.py`), not a speculative plugin architecture. It is scoped to exactly what that mechanism does.

---

## 1. Scope and Non-Goals

### 1.1 Scope

PES defines how `evgraph` discovers `Rule` implementations distributed in independently-installed packages, without `evgraph`'s source code naming them. It specifies:

- The entry_point group name rules are registered under
- What a registering package must declare
- The discovery and instantiation behavior `evgraph` performs
- The one behavioral guarantee this buys: a rule pack becomes visible to `scan()` by being installed, with no change to `evgraph`

### 1.2 What Was Actually Built (the grounding for this document)

Before PES was written, `evgraph-rules`' `pyproject.toml` was given:

```toml
[project.entry-points."evgraph.rules"]
approval_precedes_deployment = "evgraph_rules.approval_precedes_deployment:ApprovalPrecedesDeploymentRule"
dataset_manifest_complete = "evgraph_rules.dataset_manifest_complete:DatasetManifestCompleteRule"
```

and `evgraph/src/evgraph/discovery.py` was given exactly this:

```python
from importlib.metadata import entry_points

def discover_rules() -> list[Rule]:
    rules = []
    for ep in entry_points(group="evgraph.rules"):
        rule_class = ep.load()
        rules.append(rule_class())
    return rules
```

`scan.py`'s hardcoded `_MODEL_CARD_RULES = [ApprovalPrecedesDeploymentRule()]` list was then replaced with a call to `discover_rules()`. This was verified to work: both reference rules are discovered and run, and each rule's own graph-relevance check (matching on node/edge `type`, already required by RES's design — not new discovery logic) means an irrelevant rule contributes no findings rather than erroring. PES v0.1 documents exactly this mechanism — nothing more was built, so nothing more is specified.

### 1.3 Non-Goals (v0.1)

| Deferred concept | Why deferred |
|---|---|
| **Discovery for reporters** | Reporters are selected explicitly by the caller (`report.to_markdown()`, `report.to_sarif()`) — a different usage pattern than rules, which all run automatically against every graph. No reference case demonstrates reporters need to be discovered rather than directly chosen. |
| **Discovery for adapters** | Stage 2 validated APS-Core with two adapters, both explicitly constructed (`ModelCardAdapter()`, `DatasetManifestAdapter()`). No reference case demonstrates adapters need dynamic discovery; they remain immature relative to rules in this respect (`docs/ARCHITECTURE.md` ADR-0006's "multiplicity alone does not justify an abstraction" applies here too — two adapters is not evidence of a discovery need). |
| **Plugin lifecycle hooks (init/teardown/config)** | The reference mechanism does nothing beyond `entry_points(...).load()` and instantiation with no arguments. No hook, callback, or configuration-injection mechanism exists or is demonstrated as needed. |
| **Rule applicability metadata / dispatch filtering** | Every discovered rule currently runs against every graph; an irrelevant rule simply produces no findings by checking node/edge `type` itself (this was already required of rules, not new PES behavior). A rule declaring which node/edge types it applies to, so an engine could skip calling `evaluate()` entirely for irrelevant rules, would be a real optimization once the number of installed rules grows large enough to matter — but with two reference rules, there is no evidence this matters yet. Logged as an open question (Appendix), not built. |
| **Discovery ordering guarantees** | `discover_rules()` returns rules in whatever order `importlib.metadata.entry_points()` yields them. Per RES §3.1 (a `Rule`'s return order carries no meaning) and RPS §3.2.1 (a consumer must not infer meaning from finding order), discovery order is likewise not a meaningful property, and PES makes no guarantee about it. |
| **Non-Python / non-entry_points discovery mechanisms** | PES v0.1 documents the one mechanism built (Python `importlib.metadata` entry_points). Alternative discovery schemes (a config file, a registry service, namespace packages) are not considered, since none was built or demonstrated as necessary. |

If a future version of PES adds any of the above, it must cite the specific reference case that required it.

---

## 2. Core Terminology

| Term | Definition |
|---|---|
| **Entry point group** | A named group (`"evgraph.rules"`) under which installed packages register importable objects, per Python's standard `importlib.metadata` / packaging entry_points mechanism. |
| **Registration** | A package declares a `Rule` implementation under the `"evgraph.rules"` group in its own `pyproject.toml`, making it discoverable without `evgraph` importing it by name. |
| **Discovery** | The act of enumerating all registered entry points in a group across every installed package and loading/instantiating each. |

Terms defined in RES (`Rule`) are used here as defined there.

---

## 3. Discovery Contract

### 3.1 Entry Point Group

Rules are registered under the entry_point group name `"evgraph.rules"`. A package registers one entry per `Rule` implementation it provides:

```toml
[project.entry-points."evgraph.rules"]
<entry-name> = "<module.path>:<ClassName>"
```

- `<entry-name>` is an arbitrary, package-chosen string identifying the entry (not necessarily the same as `Rule.id`, though the reference implementation happens to use matching names for readability). PES does not require these to match.
- `<ClassName>` MUST be constructible with no required arguments — `discover_rules()` calls it as `rule_class()`.
- `<ClassName>` MUST satisfy the `Rule` protocol (RES §3.1) once instantiated.

### 3.2 Discovery Behavior

`evgraph.discovery.discover_rules()` is the one conforming discovery operation:

1. Enumerate every entry point registered under `"evgraph.rules"` across all installed distributions (via `importlib.metadata.entry_points(group="evgraph.rules")`).
2. For each, load the referenced class and instantiate it with no arguments.
3. Return the resulting list of `Rule` instances, in whatever order the underlying `entry_points()` call yields — no ordering guarantee is made (§1.3).

### 3.3 What Installing a Rule Pack Achieves

Per this mechanism, installing any package that registers one or more entries under `"evgraph.rules"` — including a third-party package `evgraph` has never imported — makes those rules run automatically the next time `discover_rules()` is called (i.e., the next `scan()` or `scan_dataset_manifest()` invocation), with zero change to `evgraph`'s source code. This is the concrete behavior Stage 4's exit condition requires.

---

## 4. Compatibility and Versioning Rules

- PES versions independently of EGS, RES, APS, and RPS (same independence rule as APS-Core §5, RPS §4).
- A breaking change to the entry_point group name or discovery behavior (§3) requires a version bump and must cite the reference case that required it.

---

## 5. Conformance Requirements

An implementation conforms to PES v0.1 only if it:

1. Registers `Rule` implementations under the `"evgraph.rules"` entry_point group (§3.1), each constructible with no required arguments.
2. Discovers rules via `importlib.metadata.entry_points(group="evgraph.rules")`, loading and instantiating each (§3.2).
3. Makes no ordering guarantee over discovered rules (§3.2.3).
4. Does not claim discovery support for reporters or adapters under the name "PES" (§1.3) — those remain explicitly constructed in v0.1.

---

## Appendix: Open Questions for v0.2

- Does reporter or adapter discovery ever get demonstrated as necessary, once more of either exist? (§1.3)
- Does the number of installed rules ever grow large enough that running every discovered rule against every graph (with irrelevant rules self-filtering via node/edge type checks) becomes a real performance problem, justifying rule-declared applicability metadata the engine could use to skip calling `evaluate()` for irrelevant rules? No evidence for this exists with two reference rules.
- Should `<entry-name>` be required to match `Rule.id`, to make registration and runtime identity consistent? No reference case has needed this yet — the two existing entries happen to match by convention, not by requirement.

---

## Related documents

- `docs/ARCHITECTURE.md` — ADR-0002 (Type A vs. Type B specification timing); ADR-0006 (multiplicity alone does not justify an abstraction), which is why reporter/adapter discovery remains deferred here.
- `docs/ROADMAP.md` — Stage 4 defines what PES is scoped to extract from.
- `docs/specs/RES-v0.1.md` — the `Rule` interface every discovered entry must satisfy.
- `reference/python/evgraph/src/evgraph/discovery.py` — the mechanism this specification was extracted from.
- `reference/python/evgraph-rules/pyproject.toml` — the reference registration this specification was extracted from.
