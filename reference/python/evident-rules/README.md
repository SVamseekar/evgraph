# evident-rules

Built-in rule pack for [Evident](https://github.com/SVamseekar/evident).

Rules ship as a separate package so policy can evolve without changing
`evident-core`. They register under the `evident.rules` entry-point group and
are loaded automatically by `evident.discover_rules()`.

Included rules:

- `approval-precedes-deployment` — deployment time must not precede approval
- `dataset-manifest-complete` — required manifest fields are present
- `model-version-has-training-provenance` — model versions should link to training runs

## Install

```bash
pip install -e .
```

Requires `evident-core`.

## License

BSD 3-Clause — see the monorepo `LICENSE`.
