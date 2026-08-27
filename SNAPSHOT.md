# Reef Step 4 snapshot — dynaconf

This repository is a frozen snapshot of `dynaconf/dynaconf`, prepared for grading.
**This commit is the `base_commit`.** It is the held-out-tests commit; nothing is
appended after it. Every graded item must reproduce at this tree.

## Provenance

| | |
|---|---|
| upstream | `https://github.com/dynaconf/dynaconf` (default branch `master`) |
| **C — base of the snapshot** | `fb8468d805a6f059355a1685c9ff66b003871df4` (2026-07-29, "fix: Django early validation integration code bug (#1432)") |
| freeze commit | `8363ba8e503886c71d400f49ecfd1dff0741a6ba` ("reef: freeze snapshot …") |
| this commit | held-out tests + this file — **the `base_commit`** |
| tags | none pushed. dynaconf takes its version from `dynaconf/VERSION` (`3.3.4-dev0`), not from git |

Source is untouched at C: this commit adds only test files, and the freeze commit
changed only paths under `.github/`.

## Removals (all in the freeze commit `8363ba8`)

Deleted — 13 workflows plus one non-workflow file that lived among them:

```
.github/workflows/benchmark.yml          .github/workflows/publish.yml
.github/workflows/build-dist.yml         .github/workflows/release-backport.yml
.github/workflows/build-docs.yml         .github/workflows/release-rolling.yml
.github/workflows/ci-update.yml          .github/workflows/scheduled__update-contributors.yml
.github/workflows/lint.yml               .github/workflows/smoke-test.yml
.github/workflows/main.yml               .github/workflows/test.yml
.github/workflows/publish-docs.yml       .github/workflows/galaxy_tox.ini   (not a workflow)
.github/stale.yml                        (Probot Stale App config — GitHub-side, survives deleting workflows)
```

Added: `.github/workflows/baseline.yml`.

Three of the removed workflows triggered on `push` (`main.yml`, `publish.yml`,
`ci-update.yml`) and one carried a monthly cron
(`scheduled__update-contributors.yml`).

**Repository settings** (not files, and invisible to any tree census): Dependabot
vulnerability alerts and automated security fixes were **disabled** at the destination.
No `dependabot.yml` ever existed in this tree — the alerts were on regardless.

### ⚠ Deliberately KEPT — `.github/scripts/`

`.github/scripts/` is **load-bearing and must never be removed**.
`tests/test_release_utility.py` does `from release_utility import …`, which resolves to
`.github/scripts/release_utility.py`, installed as the local package
`dynaconf-release-utility` via `[tool.uv.sources]`. **56 of the 752 `pass_to_pass` ids live
in that file.** Removing it turns all 56 into a collection ImportError → exit 2 →
`HARNESS_FAULT`. The tree-diff gate excludes `.github`, so it would not notice.

## Install (measured; reproduces upstream CI exactly)

```bash
uv export --no-hashes --only-group test -o requirements.txt
pip install -r requirements.txt      # includes -e ./.github/scripts
pip install -e .
```

- There is **no `test` extra**; `pip install .[test]` fails. Test deps are PEP 735
  `[dependency-groups]`.
- `--no-hashes` is **mandatory** — without it uv emits `--hash=` lines and pip exits 1 on
  the editable local path source.
- `--only-group` (103 pins) is what CI uses; plain `--group` gives 136.
- Python **3.12**. Everything was measured on 3.12 only.

Acceptance check, **after** the install (it fails on a bare interpreter because
`release_utility` imports `git_changelog` at module scope):

```bash
python -c "import release_utility"
```

## Graded invocation

```
python -m pytest <targets…> -p no:cacheprovider -p no:randomly -o addopts= \
  --rootdir=/testbed --junit-xml=/out/report.xml -q
```

Collected at this commit: **798**. At C alone: 787 (= upstream CI at C: 777 passed +
10 skipped, 0 failed).

## Items — 7 (6 maintainer-fixed + 1 open)

| issue | fix commit (upstream) | node ids |
|---|---|---|
| 1430 | `b56a831` | 1 |
| 974 | `ec3bc09` | 1 |
| 1210 | `be353f7` | 1 |
| 1278 | `5a0ebf1` | 4 (parametrized) |
| 1439 | `3c0cb3c` | 2 (methods on `TestDataDict`) |
| 1187 | `0e26bd6` | 1 |
| **1299 (OPEN)** | none merged — arm 2 uses **unmerged PR #1374**, saved as `dc-1299-SUGGESTED-code.patch` | 1 |

`tests/test_load_file_types.py` is **reef-authored**, transcribed from open issue #1299.
It is the only test file here not written by a dynaconf maintainer. Its arm 2 is the
community fix in unmerged PR #1374 — no fix was written by Reef.

## `pass_to_pass` — 752

Derived from what is green **in the sealed container**, never from CI (CI has a Docker
daemon and passes 17 redis/vault tests that cannot pass sealed).

```
798 collected − 11 targets − 14 redis/vault errors − 3 environmental
    − 10 skipped/xfailed = 760 sealed green;  − 8 order-dependent = 752
```

**⚠ The 752 set is INDIVISIBLE.** It was verified as a whole, per item, under each item's
exact graded argv. A trimmed per-module set is a different scope and re-triggers F-131:
8 tests green in a full run go red under a narrowed argv, 6 of them in
`tests/test_env_loader.py`. Excluded by name:

```
tests/test_base.py::TestIndexMerge::test_dotted_set_with_index_merge_disabled
tests/test_env_loader.py::test_dotenv_loader
tests/test_env_loader.py::test_env_loader
tests/test_env_loader.py::test_fresh_context
tests/test_env_loader.py::test_get_fresh
tests/test_env_loader.py::test_load_dunder
tests/test_env_loader.py::test_load_signed_integer
tests/test_yaml_loader.py::test_load_single_key
```

## ⚠ Every verdict depends on the container running as root

`tests/test_utils.py::test_read_file_permission_error` is in `pass_to_pass` and is green
**only because the graded container runs as root** — it chmods a file unreadable and
asserts `PermissionError`, which root never raises, so its own "DID NOT RAISE" guard fires
as non-root. If the harness ever drops privileges, this test flips red and **all seven
items become permanently unresolvable at once**, with no payload to distinguish it from
genuine regressions. The count would move 752 → 753.

The container UID is **not captured in `resource_envelope_version`**. Two runs with
identical envelope versions can disagree on this test.
