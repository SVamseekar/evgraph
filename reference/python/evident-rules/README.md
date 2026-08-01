# evident-rules

Reference rule pack for [Evident](https://github.com/souravamseekarmarti/evident).

Rules are registered under the `evident.rules` entry-point group and discovered
by `evident.discover_rules()` without importing this package from
`evident-core`.

Included rules:

- `approval-precedes-deployment`
- `dataset-manifest-complete`
- `model-version-has-training-provenance`

## Install

```bash
pip install -e .
```

Requires `evident-core`.

## License

BSD 3-Clause. See the monorepo `LICENSE` file.
