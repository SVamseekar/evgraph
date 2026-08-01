# evident-core

Core library for [Evident](https://github.com/SVamseekar/evident).

Provides the foundational types every other package builds on:

- `EvidenceGraph`, `EvidenceNode`, `EvidenceEdge`
- `EvidenceLevel`
- `Rule`, `Finding`
- `Adapter`, `AdapterError`, `Assumption`
- Graph serialization helpers

This package has **no** runtime dependency on other Evident packages. Higher
layers (`evident-rules`, `evident`, `evident-cli`) depend on it.

## Install

```bash
pip install -e .
```

## Docs

- Main project: https://github.com/SVamseekar/evident
- Specs: `docs/specs/` (EGS, RES)
- Architecture: `docs/ARCHITECTURE.md`

## License

BSD 3-Clause — see the monorepo `LICENSE`.
