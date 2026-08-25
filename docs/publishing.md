# Publishing Evgraph to PyPI

This is the maintainer runbook. Contributors should read
[CONTRIBUTING.md](../CONTRIBUTING.md) instead.

**Rule:** GitHub holds source. PyPI holds built wheels (`.whl`) and source
archives (`.tar.gz`). CI builds those files from a version tag and uploads them
with [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC).
Do **not** store a production PyPI API token on your machine or in GitHub
secrets.

```text
main (reviewed, tests green)
   ↓
lockstep version bump + CHANGELOG
   ↓
git tag vX.Y.Z && git push origin vX.Y.Z
   ↓
GitHub Actions workflow: publish.yml
   ↓
test on 3.10–3.12 → build four packages → twine check
   ↓
OIDC upload to PyPI → GitHub Release with the same artifacts
```

## Packages published together

One tag publishes four PyPI projects. Versions must be identical.

| PyPI project | What users install | Built from |
| --- | --- | --- |
| [evgraph-core](https://pypi.org/project/evgraph-core/) | `pip install evgraph-core` | `reference/python/evgraph-core` |
| [evgraph-rules](https://pypi.org/project/evgraph-rules/) | `pip install evgraph-rules` | `reference/python/evgraph-rules` |
| [evgraph](https://pypi.org/project/evgraph/) | `pip install evgraph` | `reference/python/evgraph` |
| [evgraph-cli](https://pypi.org/project/evgraph-cli/) | `pip install evgraph-cli` | `reference/python/evgraph-cli` |

`evgraph` depends on `evgraph-core` and `evgraph-rules`. `evgraph-cli` depends
on `evgraph`. Users of the Python API normally only need `pip install evgraph`.

Each package's `README.md` is the long description shown on PyPI. Keep those
files self-contained and use **absolute** GitHub URLs for documentation links
so they render on both GitHub and PyPI.

## Versioning

Semantic Versioning: `MAJOR.MINOR.PATCH`.

| Kind of change | Version bump | Example |
| --- | --- | --- |
| Breaking public API | major | `1.4.2` → `2.0.0` |
| Compatible new API | minor | `1.4.2` → `1.5.0` |
| Bug fix | patch | `1.4.2` → `1.4.3` |

While the stack is `0.x`, a **minor** bump may include breaking changes
(`0.1.1` → `0.2.0`). Patch stays bug-fix / docs-only unless you choose a
feature patch deliberately. Stay on `0.x` until you are ready to freeze the
public API as `1.0.0`.

Set `version = "X.Y.Z"` in **all four** `pyproject.toml` files in the same
commit. The publish workflow runs `scripts/check_release_version.py` and
refuses to upload if the Git tag (without the leading `v`) does not match.

## One-time setup (Trusted Publishing)

Do this before the first OIDC upload. You need a
[PyPI](https://pypi.org/account/register/) account **and** a separate
[TestPyPI](https://test.pypi.org/account/register/) account.

All four Evgraph projects **already exist** on production PyPI (first uploaded
manually at `0.1.0` / `0.1.1`). For those, add a Trusted Publisher on each
**existing** project (project settings → Publishing). That is not a “pending”
publisher and is **not** limited by PyPI’s three-pending-publisher cap.

TestPyPI may still need pending publishers if those project names were never
created there — see the TestPyPI section below.

### 1. Why each package has its own GitHub environment

Pending Trusted Publishers are unique on
`(GitHub owner, repository, workflow filename, environment)`. You cannot
register the same tuple for two project names. This monorepo therefore uses
**one GitHub environment per package** so TestPyPI (and any future new name)
can use OIDC without colliding, and production stays consistent with that
layout.

### 2. GitHub environments

Create these eight [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
under **Settings → Environments**. Names must match exactly:

| Environment | PyPI project | Index |
| --- | --- | --- |
| `pypi-evgraph` | `evgraph` | production |
| `pypi-evgraph-core` | `evgraph-core` | production |
| `pypi-evgraph-rules` | `evgraph-rules` | production |
| `pypi-evgraph-cli` | `evgraph-cli` | production |
| `testpypi-evgraph` | `evgraph` | TestPyPI |
| `testpypi-evgraph-core` | `evgraph-core` | TestPyPI |
| `testpypi-evgraph-rules` | `evgraph-rules` | TestPyPI |
| `testpypi-evgraph-cli` | `evgraph-cli` | TestPyPI |

Do **not** reuse a single environment named `pypi` or `testpypi` for all four.

Required reviewers on the `pypi-*` environments are recommended once you have
a collaborator who can approve. A solo maintainer cannot require self-review.
Do **not** enable "Prevent self-review" on a one-person project or you will be
unable to publish.

### 3. Trusted publishers on production PyPI (existing projects)

For each project
([evgraph](https://pypi.org/manage/project/evgraph/settings/publishing/),
[evgraph-core](https://pypi.org/manage/project/evgraph-core/settings/publishing/),
[evgraph-rules](https://pypi.org/manage/project/evgraph-rules/settings/publishing/),
[evgraph-cli](https://pypi.org/manage/project/evgraph-cli/settings/publishing/)),
add a Trusted Publisher:

| Field | Value |
| --- | --- |
| Owner | `SVamseekar` |
| Repository | `evgraph` |
| Workflow | `publish.yml` |
| Environment | `pypi-<project>` (e.g. `pypi-evgraph-core`) |

The workflow name is the **filename only**, not `.github/workflows/publish.yml`.

### 4. Pending publishers on TestPyPI (wave 1 if names are new)

PyPI’s **pending** publisher limit is three per account. If the names do not
yet exist on TestPyPI, register at most three first:

| Project name | Owner | Repository | Workflow | Environment name |
| --- | --- | --- | --- | --- |
| `evgraph` | `SVamseekar` | `evgraph` | `publish.yml` | `testpypi-evgraph` |
| `evgraph-core` | `SVamseekar` | `evgraph` | `publish.yml` | `testpypi-evgraph-core` |
| `evgraph-rules` | `SVamseekar` | `evgraph` | `publish.yml` | `testpypi-evgraph-rules` |

Leave `evgraph-cli` until wave 2 (after the first three uploads succeed and free
pending slots). Open
<https://test.pypi.org/manage/account/publishing/>.

If the TestPyPI projects already exist, add Trusted Publishers on each project
the same way as production (no pending wave needed).

### 5. What not to create

- Do **not** add `PYPI_API_TOKEN` or `TEST_PYPI_API_TOKEN` GitHub secrets.
- Do **not** put a PyPI token in `~/.pypirc` for production releases.
- Do **not** run `twine upload` to production PyPI from your laptop.

A TestPyPI API token is acceptable only as an emergency fallback. Prefer OIDC.

## Local validation (optional, no upload)

From the repository root, with the dev environment activated:

```bash
python -m pip install --upgrade build twine
python scripts/check_release_version.py
python scripts/build_dists.py
python -m twine check --strict dist/*/*
```

Install wheels in a **clean** virtualenv in dependency order:

```bash
python -m venv /tmp/evgraph-wheel-check
source /tmp/evgraph-wheel-check/bin/activate
python -m pip install dist/evgraph-core/*.whl dist/evgraph-rules/*.whl
python -m pip install dist/evgraph/*.whl
python -m pip install dist/evgraph-cli/*.whl
python -c "from evgraph import scan, evaluate_gate; print(scan, evaluate_gate)"
evgraph --help
```

`dist/` is generated output and is gitignored. Do not commit it.

Before sibling packages exist on an index, always install local wheels in that
order. A bare `pip install dist/evgraph/*.whl` will pull `evgraph-core` /
`evgraph-rules` from PyPI.

## TestPyPI dry run

1. Push `main` so `.github/workflows/publish.yml` exists on GitHub.
2. Configure TestPyPI trusted / pending publishers (section above).
3. GitHub → **Actions** → **Publish** → **Run workflow**.
4. If using pending publishers, wave 1 may leave `evgraph-cli` failing until
   you register it and re-run (`fail-fast: false`, `skip-existing: true`).
5. Confirm the TestPyPI project pages.

The workflow tests, builds, and uploads to TestPyPI. It does **not**
create a GitHub Release and does **not** upload to production PyPI.

After a successful dry run:

```bash
python -m venv /tmp/evgraph-testpypi
source /tmp/evgraph-testpypi/bin/activate
python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  evgraph evgraph-cli
python -c "from evgraph import scan; print(scan)"
evgraph --help
```

`--extra-index-url` is useful when TestPyPI lacks a dependency that production
PyPI has. Open each TestPyPI project page and confirm the README, license, and
project URLs render.

TestPyPI **does not allow reusing a version**. If you need another dry run of
the same code, bump to a local/dev version such as `0.1.2rc1` in all four
files, or wait until the next real version. `skip-existing: true` only skips
files that already exist; it cannot replace them.

## Production release

1. Tests on `main` are green.
2. Set `version = "X.Y.Z"` in all four `pyproject.toml` files.
3. Move notes in `CHANGELOG.md` from **Unreleased** into `## [X.Y.Z] — YYYY-MM-DD`.
4. Commit and push `main`:

   ```bash
   git add -u
   git commit -m "chore: release vX.Y.Z"
   git push origin main
   ```

5. Tag the **same** commit (annotated tag):

   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

6. Watch **Actions → Publish**. On success:
   - all four projects receive the new version on PyPI
   - a GitHub Release named `vX.Y.Z` is created with the wheels and sdists
     attached
7. Verify from a clean environment:

   ```bash
   python -m pip install -U evgraph evgraph-cli
   python -c "from evgraph import scan; print(scan)"
   evgraph --help
   ```

PyPI versions are immutable. A broken `X.Y.Z` is fixed by publishing
`X.Y.Z+1` (usually a patch). You may [yank](https://pypi.org/help/#yanked) a
bad version so new installs skip it; yanking does not delete files already
downloaded.

Do **not** retag `v0.1.1` (already published). The next train after the
promotion-gate work is typically `0.1.2` or `0.2.0`.

## Workflow behaviour

File: [`.github/workflows/publish.yml`](../.github/workflows/publish.yml)

| Trigger | Tests | Build | PyPI | TestPyPI | GitHub Release |
| --- | --- | --- | --- | --- | --- |
| Push tag `v*` | yes | yes | yes | no | yes |
| `workflow_dispatch` | yes | yes | no | yes | no |
| Push / PR to `main` | [ci.yml](../.github/workflows/ci.yml) only | check only | no | no | no |

The publish job uses `permissions: id-token: write` so GitHub can mint a
short-lived OIDC token. PyPI exchanges that token for a one-time upload
credential. The `pypa/gh-action-pypi-publish` action also generates
[PEP 740](https://peps.python.org/pep-740/) attestations by default.

Build and publish are **separate jobs**. The publish job only downloads the
already-built artifacts. That is required by PyPA's Trusted Publishing guide.

## GitHub settings to keep

These match GitHub's recommended defaults for a public library:

- Default branch: `main`
- Actions: allow GitHub-hosted runners; `pypa/gh-action-pypi-publish` must
  remain allowed
- Dependabot: enabled for `github-actions` (see `.github/dependabot.yml`)
- Delete head branches on merge: enabled
- Do not grant `id-token: write` or `contents: write` at the workflow level
  globally. Those permissions stay on the individual publish / release jobs

Recommended later, when there is more than one maintainer:

- Branch protection on `main`: require the CI workflow, disallow force pushes
- Required reviewers on the `pypi-*` environments

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `You can't register more than 3 pending trusted publishers at once` | Account limit. Keep three pending on TestPyPI, publish them, then add `evgraph-cli` |
| `A pending trusted publisher matching this configuration has already been registered for a different project name` | Two pending publishers share the same `(repo, publish.yml, environment)`. Each package needs its own `pypi-<name>` / `testpypi-<name>` environment |
| `Trusted publishing exchange failure` | Publisher fields do not match: owner, repo, `publish.yml`, or environment name |
| Version check fails | Tag `v0.1.2` but a `pyproject.toml` still says another version (not lockstep) |
| TestPyPI 400 "file already exists" | That version was already uploaded; bump the version |
| `pip install evgraph` cannot find `evgraph-core` | Core was not published, or PyPI index lag of a few minutes |
| GitHub Release step fails after PyPI succeeded | Re-run only the release job, or `gh release create` manually; do not retag the same version |

## References

- [PyPA: publishing with GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [Making a PyPI-friendly README](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
