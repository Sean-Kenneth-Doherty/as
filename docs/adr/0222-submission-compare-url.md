# ADR-0222: Submission Compare URL

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0218 through ADR-0221 made the handoff report link directly to the upstream
project, fork `main`, the submitted fork commit, and the tracking issue. A
reviewer can now navigate to the right places, but the report still does not
provide one direct diff URL for the submitted changes.

Because direct upstream pushes remain permission-blocked, the most reliable
local compare URL is hosted on the fork and compares the refreshed
`origin/main` commit to the submitted `HEAD` commit. That URL lets reviewers
open the exact patch set even while upstream `main` remains unchanged.

## Decision

Add a derived `fork_compare_url` to `autarkic_systems.github_submission`, using
the normalized fork web URL plus the inspected `origin/main` and `HEAD`
commits.

The JSON payload will include `fork_main.compare_url`, and text output will
render `Fork compare: ...`. Handoff output will inherit the expanded GitHub
submission payload and formatter output.

This does not contact GitHub APIs, change submission acceptance, change remote
refresh behavior, change handoff readiness, or change project-status,
vertical-demo, evidence, claim, proof, source-status, runtime, trace/SVG,
scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because submission JSON/text lacks a
  fork compare URL.
- JSON output includes `fork_main.compare_url`.
- Text output renders `Fork compare: ...`.
- SSH-normalized fork remotes produce the same canonical compare URL.
- Handoff output inherits the expanded submission surface.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_github_submission_status
  tests.test_handoff_status`.
- Green: the same focused suite passes after implementation.
- Regression: run live GitHub submission text/JSON, live handoff with
  `--refresh-remotes`, compileall, `git diff --check`, and the full default
  suite.

## After Action Report

Implemented in `autarkic_systems/github_submission.py`, with focused coverage
in `tests/test_github_submission_status.py` and inherited handoff coverage in
`tests/test_handoff_status.py`.

The red focused run failed as intended because submission JSON lacked
`fork_main.compare_url`, submission text lacked `Fork compare: ...`, and
handoff output did not inherit either surface.

The implementation adds a derived `fork_compare_url` property to
`GitHubSubmissionStatus`, includes it in JSON under `fork_main.compare_url`,
and renders it in text output as `Fork compare: ...`. It reuses the ADR-0219
GitHub remote web URL normalizer and compares the inspected `origin/main`
commit to the submitted `HEAD` commit on the fork.

Focused GitHub-submission and handoff tests passed 18 tests. Live
GitHub-submission text/JSON and handoff commands reported accepted status and
displayed the fork compare URL. `compileall`, `git diff --check`, and the full
default suite passed; the full suite ran 910 tests.
