# evgraph-core

[![PyPI](https://img.shields.io/pypi/v/evgraph-core.svg)](https://pypi.org/project/evgraph-core/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://github.com/SVamseekar/evgraph/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**Foundational types for the [Evgraph](https://github.com/SVamseekar/evgraph) evidence-graph stack.**

## What is it

`evgraph-core` defines the small, stable vocabulary that every other Evgraph
package is built on: what an Evidence Graph is, how certain a piece of
evidence is allowed to claim to be, and the contracts an adapter or a rule
must honor to participate in that graph. It has no opinion about *how*
evidence gets collected or *what* should be checked — those are the concerns
of `evgraph-rules` (built-in checks) and `evgraph` (adapters, reporters, the
public `scan()` API). A missing approval timestamp stays inconclusive in a
finding. The graph does not invent the field. EU AI Assurance OS pins
`evgraph-cli==0.1.2` against this vocabulary. `evgraph-core` only defines the
shared data model those higher layers agree on, which is what lets adapters,
rule packs, and reporters be written independently and still interoperate.

The types here implement the **Evidence Graph Specification (EGS)** and the
**Rule Evaluation Specification (RES)** — normative documents in the main
repository (`docs/specs/`) that this package is the reference implementation
of. If a detail here and a spec ever disagree, the spec wins and this package
has a bug.

## Main features

- **`EvidenceGraph` / `EvidenceNode` / `EvidenceEdge`** — an immutable,
  frozen-dataclass model of a directed graph of typed facts. Node and edge
  identity is enforced at construction: duplicate node ids and edges that
  reference a missing node both raise `ValueError` immediately, so a graph
  that exists is always internally consistent.
- **`EvidenceLevel`** — an ordered `IntEnum`
  (`STRUCTURAL < CONSISTENCY < HEURISTIC < INTERPRETIVE`) expressing how
  certain a fact or a finding is. Reasoning can only ever get *less* certain
  as it propagates through a rule (`least_certain()` enforces this), never
  more — so a finding can never claim stronger evidence than the facts it
  cites.
- **`Rule` (Protocol) / `Finding` / `Outcome`** — the contract a rule
  implementation satisfies (purity, no shared-state side effects, every
  citation must point at a real node in the input graph) and the immutable,
  explainable result a rule produces: an outcome
  (`EXPECTATION_MET` / `EXPECTATION_NOT_MET` / `INCONCLUSIVE`), a level, and
  the node ids that justify it. `compute_finding_level()` is the *only*
  sanctioned way to derive `Finding.level` — rule authors never assign it
  directly, which is what keeps findings honest about their own certainty.
- **`Adapter` (Protocol) / `AdapterError` / `Assumption`** — the minimal
  surface an extractor declares (name, version, evidence level, extraction
  method, its assumptions) without standardizing how extraction itself is
  invoked, so adapters stay free to have artifact-appropriate signatures.
  `AdapterError` is reserved for failures of *interpretation* — malformed or
  unreadable input — never for governance deficiencies in otherwise-valid
  data.
- **Graph (de)serialization** — round-trippable JSON encoding for
  `EvidenceGraph`, so a graph built once can be persisted, diffed, or handed
  to a different process without re-running adapters.

This package has **no runtime dependency on any other Evgraph package** —
`evgraph-rules`, `evgraph`, and `evgraph-cli` all depend on it, never the
other way around, which keeps the core vocabulary stable independent of how
many rule packs or adapters get built on top of it.

## Where to get it

The source is hosted on GitHub at: https://github.com/SVamseekar/evgraph

Binary installers for the latest released version are available at the
[Python Package Index (PyPI)](https://pypi.org/project/evgraph-core/):

```bash
pip install evgraph-core
```

From source, for contributing:

```bash
git clone https://github.com/SVamseekar/evgraph.git
cd evgraph
pip install -e reference/python/evgraph-core
```

## Dependencies

None at runtime. `pytest>=7` is required for the test suite
(`pip install "evgraph-core[test]"`).

## Documentation

| For | Start here |
| --- | --- |
| Evidence Graph Specification (EGS) | [`docs/specs/`](https://github.com/SVamseekar/evgraph/tree/main/docs/specs) |
| Rule Evaluation Specification (RES) | [`docs/specs/`](https://github.com/SVamseekar/evgraph/tree/main/docs/specs) |
| Design principles and decisions | [`docs/ARCHITECTURE.md`](https://github.com/SVamseekar/evgraph/blob/main/docs/ARCHITECTURE.md) |
| The full library stack (adapters, rules, reporters, CLI) | [Main project README](https://github.com/SVamseekar/evgraph) |

## Getting help

Ask questions and report bugs via
[GitHub Issues](https://github.com/SVamseekar/evgraph/issues) on the main
repository — this package doesn't track issues separately from the monorepo.

## Contributing

All contributions, bug reports, and feature requests are welcome on the main
repository. See
[CONTRIBUTING.md](https://github.com/SVamseekar/evgraph/blob/main/CONTRIBUTING.md)
and the
[Code of Conduct](https://github.com/SVamseekar/evgraph/blob/main/CODE_OF_CONDUCT.md).
Security reports:
[SECURITY.md](https://github.com/SVamseekar/evgraph/blob/main/SECURITY.md).

## License

[BSD 3-Clause](https://github.com/SVamseekar/evgraph/blob/main/LICENSE).
