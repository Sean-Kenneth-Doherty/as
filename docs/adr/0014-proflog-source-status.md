# ADR-0014: Proflog Source Status

Date: 2026-05-17

Status: Accepted

## Context

P6 asks where the active Proflog ADR-006x work described in SJAS logs lives and
whether AS should depend on it. ADR-0010 deliberately deferred public Proflog
as a dependency because the visible public repository did not match the active
SJAS frontier.

This question blocks any honest AS proof-apparatus claim. Public Proflog is
conceptually close to the desired direction because it is Fitting-style semantic
tableaux, but AS cannot treat a missing or non-running source tree as
executable evidence.

## Decision

Record Proflog as a relevant background source, but do not depend on public
`jpt4/proflog` `main` for AS implementation or verification.

Add:

- `sources/proflog_frontier_status.json`, a structured source-status artifact;
- `tests/test_proflog_frontier_status.py`, checking the recorded decision,
  public head, missing ADR-006x terms, and smoke-test failure;
- `docs/proflog-frontier-status.md`, a human-readable source-status note and
  maintainer question.

## Evidence

- `git ls-remote https://github.com/jpt4/proflog.git HEAD refs/heads/*`
  returned only `main` at
  `77af8481d9f41a439eb42e1d8268a5b39f7c5c33`.
- The public checkout contains only `proflog.scm` and `LPTableaus.pdf` as
  project payload.
- `rg` found the ADR-006x frontier terms only in
  `/home/sean/Projects/_upstream/sjas/nachlass/LOG.md`, not in public Proflog.
- `guile proflog.scm` failed with `Unbound variable: even` at
  `proflog.scm:893:5`.

## Success Criteria

- Red tests fail before implementation because
  `sources/proflog_frontier_status.json` is absent.
- The structured status records the public remote head and visible public
  branches.
- The status records the SJAS-log frontier terms missing from public main:
  ADR-0063 through ADR-0068, `tableau-proof/3`, `subst-prf/4`,
  `subst-code/2`, `SelfCons1`, and related code-level terms.
- The status records the local Guile smoke-test failure.
- The decision is explicit: `do-not-depend-on-public-main`.

## Consequences

- AS may cite public Proflog as background for the Fitting-style tableaux
  direction.
- AS must not cite public Proflog main as passing SJAS implementation evidence.
- The next proof-apparatus implementation should either recover the active
  Proflog source, repair/publish it, or continue with AS-local proof objects
  until a replacement tableaux/code apparatus is chosen.

## After Action Report

Red step:

- `python -m unittest tests.test_proflog_frontier_status` failed with
  `FileNotFoundError` for `sources/proflog_frontier_status.json`.

Green step:

- Added `sources/proflog_frontier_status.json`.
- Added `tests/test_proflog_frontier_status.py`.
- Added `docs/proflog-frontier-status.md`.
- `python -m unittest tests.test_proflog_frontier_status` passed 4 tests.
- `python -m unittest discover` passed 50 tests.
- `python -m py_compile autarkic_systems/willard_map.py
  tests/test_willard_definition_map.py tests/test_proflog_frontier_status.py`
  passed.
- `jq -e .` passed for `sources/proflog_frontier_status.json`,
  `sources/willard_definition_map.json`, and `sources/manifest.json`.
- `git diff --check` passed.

Coverage limits:

- The status note does not recover the missing ADR-006x source.
- The default fast test validates the recorded source-status facts and pinned
  paths; it does not require the disposable `_upstream` clones to be present.
- The Guile smoke result is a compatibility signal for this environment, not a
  complete portability audit across Chez, Racket, or other Scheme runtimes.
