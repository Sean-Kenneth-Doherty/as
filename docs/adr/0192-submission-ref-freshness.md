# ADR-0192: Submission Ref Freshness

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0190 added a local GitHub submission command, and ADR-0191 composed that
submission evidence into the end-of-month handoff command. Both commands report
whether `fork/main` matches the current `HEAD`, but they do not report how
fresh the local `fork/main` remote-tracking ref is.

That matters because these commands intentionally avoid GitHub API calls. A
local remote-tracking ref can be stale, so an operator should see whether the
evidence was refreshed recently enough to be trusted as current local
submission evidence.

## Decision

Record `fork/main` remote-tracking ref freshness in the GitHub submission
status. Use the local reflog timestamp for `refs/remotes/fork/main`, classify
the ref as fresh when it was updated within the configured freshness window,
and expose the result in text and JSON output. The handoff command will inherit
the same submission payload and text.

## Success Criteria

- Red tests fail before implementation because submission status has no remote
  freshness fields.
- `build_github_submission_status` accepts a clock and freshness window for
  deterministic tests.
- JSON output includes `fork_main.remote_ref_freshness` with state,
  `checked_ref`, `updated_at_unix`, `age_seconds`, and `max_age_seconds`.
- Text output includes a remote-ref freshness line.
- The live command reports `fork/main` freshness without contacting GitHub APIs.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_github_submission_status
  tests.test_handoff_status`.
- Green: the same focused suite passes after implementation.
- Regression: run `python -m autarkic_systems.github_submission`,
  `python -m autarkic_systems.handoff`, `python -m compileall -q
  autarkic_systems tests`, `git diff --check`, and the full default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_github_submission_status tests.test_handoff_status`
run failed because `GitHubSubmissionStatus` did not accept freshness metadata,
the submission builder did not accept a clock, and the JSON/text reports had no
remote-ref freshness fields.

The implementation added local `fork/main` remote-tracking ref freshness to
`autarkic_systems/github_submission.py`. It reads
`refs/remotes/fork/main` from the local git reflog, classifies the ref as
fresh or stale against a configurable freshness window, and exposes the result
in text and JSON output. The field is informational rather than a submission
gate: stale local refs make the evidence weaker, but do not rewrite whether the
local `fork/main` commit matches `HEAD`.

The focused GitHub-submission and handoff suites passed with 11 tests. Live
submission and handoff text/JSON commands reported `fork/main` freshness as
fresh before this ADR was committed. `compileall`, `git diff --check`, and the
full default suite also passed; the full suite ran 802 tests.
