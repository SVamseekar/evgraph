# evgraph-rules

[![PyPI](https://img.shields.io/pypi/v/evgraph-rules.svg)](https://pypi.org/project/evgraph-rules/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://github.com/SVamseekar/evgraph/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**The built-in rule pack for [Evgraph](https://github.com/SVamseekar/evgraph).**

## What is it

`evgraph-rules` is the reference implementation of Evgraph's rule-pack
mechanism, and the set of governance checks that ship out of the box.
Rules are deliberately shipped as their *own* package, separate from
`evgraph-core`: policy — what counts as good evidence — should be free to
evolve, gain new checks, or be replaced by an organization's own rule pack,
without ever touching the stable graph and evidence-level vocabulary that
`evgraph-core` defines. A rule pack participates in Evgraph purely by being
`pip install`-ed; `evgraph.discover_rules()` finds every rule registered
under the `evgraph.rules` entry-point group at runtime; `evgraph-rules` is
simply the first (and currently only first-party) example of that
mechanism, not a privileged one.

Each rule here is a small, pure function over an `EvidenceGraph`: it takes a
graph, cites the specific nodes and edges its conclusion rests on, and
returns `Finding`s whose certainty (`EvidenceLevel`) is never higher than the
evidence it cites — enforced by `evgraph_core.compute_finding_level()`, not
by convention.

## Main features

- **`approval-precedes-deployment`** — checks that a deployment's
  `REQUIRES_APPROVAL` edge points to a `HumanApproval` whose `approved_at`
  precedes the deployment's `deployed_at`. Reasoning class `CONSISTENCY`: it
  cross-references two structural timestamps rather than reading either in
  isolation. A missing `approved_at` stays inconclusive. The rule does not invent the timestamp. EU AI Assurance OS pins `evgraph-cli==0.1.2` so a pack and a live scan share that gap.
- **`dataset-manifest-complete`** — checks that every `Dataset` node in the
  graph declares a non-empty `license` attribute. Reasoning class
  `STRUCTURAL`: a direct presence check on a single node, with no
  cross-referencing between nodes.
- **`model-version-has-training-provenance`** — checks that every node whose
  type ends in `ModelVersion` has a `TRAINED_BY` edge to the run that
  produced it. Deliberately written against the *graph shape*
  (`…ModelVersion` node, `TRAINED_BY` edge) rather than against MLflow by
  name, entirely independent of any one adapter's implementation — so it
  applies unmodified to any future adapter (a different model registry, for
  example) that produces the same shape.
- **Entry-point registration** — all three rules register under
  `evgraph.rules` in this package's `pyproject.toml`. Installing a
  third-party rule pack the same way makes `scan()` pick it up automatically;
  no changes to `evgraph-core` or `evgraph` are required.

## Where to get it

The source is hosted on GitHub at: https://github.com/SVamseekar/evgraph

Binary installers for the latest released version are available at the
[Python Package Index (PyPI)](https://pypi.org/project/evgraph-rules/):

```bash
pip install evgraph-rules
```

From source, for contributing:

```bash
git clone https://github.com/SVamseekar/evgraph.git
cd evgraph
pip install -e reference/python/evgraph-core
pip install -e reference/python/evgraph-rules
```

## Dependencies

- [`evgraph-core`](https://pypi.org/project/evgraph-core/) — installed
  automatically as a dependency.

`pytest>=7` is required for the test suite
(`pip install "evgraph-rules[test]"`).

## Documentation

| For | Start here |
| --- | --- |
| Rule Evaluation Specification (RES) | [`docs/specs/`](https://github.com/SVamseekar/evgraph/tree/main/docs/specs) |
| How rules plug into `scan()` | [`evgraph`](https://pypi.org/project/evgraph/) package README |
| Writing a third-party rule pack | [`docs/specs/`](https://github.com/SVamseekar/evgraph/tree/main/docs/specs) (Plugin Extension Specification) |
| The full library stack | [Main project README](https://github.com/SVamseekar/evgraph) |

## Getting help

Ask questions and report bugs via
[GitHub Issues](https://github.com/SVamseekar/evgraph/issues) on the main
repository.

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
