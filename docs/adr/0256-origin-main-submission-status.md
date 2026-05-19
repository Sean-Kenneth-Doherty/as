# ADR-0256: Origin Main Submission Status

Date: 2026-05-18

## Status

Accepted.

## Context

Earlier GitHub submission status work treated `fork/main` as the accepted
publication target because direct pushes to `jpt4/as` were permission-blocked.
That was correct while AS work could only be preserved on the fork.

The repository invitation has now been accepted and `jpt4/as` reports WRITE
permission. ADR-0255 was pushed to `origin/main`, but the handoff still labeled
the same state as `submitted-to-fork` even when `origin/main` matched `HEAD`.

The submission report should prefer source-repository evidence when available,
while retaining the fork path as a fallback for future permission or outage
cases.

## Decision

Teach `autarkic_systems.github_submission` to classify a matching
`origin/main` as `submitted-to-origin`. A matching source repo should be
accepted even if `fork/main` is stale or missing the current `HEAD`. If
`origin/main` does not match but `fork/main` does, preserve the existing
`submitted-to-fork` fallback state.

The text report will render `origin/main: matches HEAD (...)` when the source
repo points at the inspected `HEAD`; otherwise it will keep the existing
ahead/behind divergence line.

This changes local reporting only. It does not contact GitHub APIs, change git
remote URLs, delete fork history, open pull requests, or alter source evidence.

## Success Criteria

- Red tests fail before implementation because a matching `origin/main` is
  still labeled `submitted-to-fork`.
- The JSON payload reports `submission_state: submitted-to-origin` when
  `origin/main` matches `HEAD`.
- The text report renders `GitHub submission status: submitted-to-origin` and
  `origin/main: matches HEAD (...)` for source-submitted states.
- Submission remains accepted when `origin/main` matches `HEAD` even if
  `fork/main` does not.
- The existing fork fallback remains accepted as `submitted-to-fork` when only
  `fork/main` matches `HEAD`.
- Handoff JSON/text inherits the source-submitted state.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_github_submission_status
  tests.test_handoff_status`.
- Green: the same focused suite passes after implementation.
- Regression: run live GitHub submission text/JSON with `--refresh-remotes`,
  live handoff with `--refresh-remotes`, `git diff --check`, and the full
  default suite.

## After Action Report

Implemented in `autarkic_systems/github_submission.py`, with focused tests in
`tests/test_github_submission_status.py` and inherited handoff coverage in
`tests/test_handoff_status.py`.

The red focused run failed before implementation because matching
`origin/main` states still reported `submitted-to-fork`, and handoff rejected a
source-submitted state when `fork/main` was stale.

The green implementation makes `origin/main` the preferred accepted submission
target. If the source repo points at `HEAD`, JSON reports
`submitted-to-origin`, text reports `origin/main: matches HEAD (...)`, and
handoff remains ready even if the fork ref is stale. If the source repo does
not match but `fork/main` does, the existing `submitted-to-fork` fallback is
preserved.

Focused GitHub submission and handoff tests passed 21 tests. This is a local
reporting change only; it does not change remotes, delete fork history, open a
pull request, or contact GitHub APIs.
