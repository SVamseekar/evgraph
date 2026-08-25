# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Package versions in this monorepo (`evgraph-core`, `evgraph-rules`, `evgraph`,
`evgraph-cli`) are released together under a shared tag of the form `vX.Y.Z`.

## [Unreleased]

### Added

- GitHub Actions publish workflow using PyPI Trusted Publishing (OIDC).
  Production uploads are triggered by `v*` tags; TestPyPI uploads are
  triggered by workflow dispatch. No production PyPI token is stored in the
  repository. Each package uses its own GitHub environment (`pypi-evgraph`,
  `pypi-evgraph-core`, …). See [`docs/publishing.md`](docs/publishing.md).
- CI now also checks lockstep package versions, builds wheels/sdists, and
  runs `twine check --strict`.
- Maintainer scripts: `scripts/build_dists.py`, `scripts/check_release_version.py`.
- Dependabot for GitHub Actions.
- Promotion scan API and CLI workflow documentation for `scan_promotion`,
  `evaluate_gate`, `evgraph scan-promotion`, `--gate`, and `--strict`.
- Promotion gate example with report-only scans, reviewer-pack outputs
  (Markdown, SARIF, OSCAL), and a sample GitHub Actions workflow.

## [0.1.1] - 2026-08-17

Documentation-only release. No code changes.

### Changed

- Rewrote the root README and all four package READMEs
  (`evgraph-core`, `evgraph-rules`, `evgraph`, `evgraph-cli`) with
  PyPI/pandas-style structure: "What is it", "Main features", "Where to get
  it", "Dependencies", "Documentation", "Getting help", and "Contributing"
  sections, plus per-package PyPI version badges.
- `pip install` is now the primary install path in every README; the
  editable/source install is kept as a "for contributing" fallback.

## [0.1.0] - 2026-07-28

Initial public release of the Evgraph library stack and specifications.
Published to PyPI on 2026-08-17: [`evgraph-core`](https://pypi.org/project/evgraph-core/),
[`evgraph-rules`](https://pypi.org/project/evgraph-rules/),
[`evgraph`](https://pypi.org/project/evgraph/),
[`evgraph-cli`](https://pypi.org/project/evgraph-cli/).

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

[Unreleased]: https://github.com/SVamseekar/evgraph/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/SVamseekar/evgraph/releases/tag/v0.1.1
[0.1.0]: https://github.com/SVamseekar/evgraph/releases/tag/v0.1.0
