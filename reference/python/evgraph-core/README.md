# evgraph-core

Core library for [Evgraph](https://github.com/SVamseekar/evgraph).

Provides the foundational types every other package builds on:

- `EvidenceGraph`, `EvidenceNode`, `EvidenceEdge`
- `EvidenceLevel`
- `Rule`, `Finding`
- `Adapter`, `AdapterError`, `Assumption`
- Graph serialization helpers

This package has **no** runtime dependency on other Evgraph packages. Higher
layers (`evgraph-rules`, `evgraph`, `evgraph-cli`) depend on it.

## Install

```bash
pip install -e .
```

## Docs

- Main project: https://github.com/SVamseekar/evgraph
- Specs: `docs/specs/` (EGS, RES)
- Architecture: `docs/ARCHITECTURE.md`

## License

BSD 3-Clause — see the monorepo `LICENSE`.
