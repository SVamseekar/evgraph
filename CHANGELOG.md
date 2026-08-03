# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Package versions in this monorepo (`evgraph-core`, `evgraph-rules`, `evgraph`,
`evgraph-cli`) are released together under a shared tag of the form `vX.Y.Z`.

## [0.1.0] - 2026-07-28

Initial public release of the Evgraph library stack and specifications.

### Added

#### Specifications

- Evidence Graph Specification (EGS) v0.1
- Rule Evaluation Specification (RES) v0.1
- Adapter Protocol Specification (APS) v0.1
- Reporting Specification (RPS) v0.1
- Plugin Extension Specification (PES) v0.1
- Cross-Vocabulary Specification (CVS) v0.1

#### Packages

- **`evgraph-core` 0.1.0** — foundational types: `EvidenceGraph`,
  `EvidenceNode`, `EvidenceEdge`, `EvidenceLevel`, `Rule`, `Finding`,
  `Adapter`, `AdapterError`, `Assumption`, graph serialization
- **`evgraph-rules` 0.1.0** — built-in rule pack
  (`approval-precedes-deployment`, `dataset-manifest-complete`,
  `model-version-has-training-provenance`), registered via the
  `evgraph.rules` entry-point group
- **`evgraph` 0.1.0** — adapters (Model Card / JSON, dataset-manifest / CSV,
  MLflow model registry), reporters (JSON, Markdown, SARIF, OSCAL), public
  `scan()` / `scan_dataset_manifest()` API, and `discover_rules()`
- **`evgraph-cli` 0.1.0** — `evgraph scan` and `evgraph scan-dataset-manifest`
  command-line entry points

#### Documentation and examples

- Architecture constitution and ADR decision log (`docs/ARCHITECTURE.md`)
- Capability-staged roadmap (`docs/ROADMAP.md`)
- Research notes on standards comparison, practitioner/market check, OSCAL
  round-trip, and MLflow adapter validation (`docs/research/`)
- Runnable examples under `examples/`

[0.1.0]: https://github.com/SVamseekar/evgraph/releases/tag/v0.1.0
