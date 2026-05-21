# ADR-0292: Origin Main Ref Freshness

Date: 2026-05-21

## Status

Accepted.

## Context

ADR-0256 made source `origin/main` the preferred accepted submission target
when it matches the current `HEAD`, while preserving `fork/main` as a fallback
accepted path. ADR-0192 still reports remote-tracking ref freshness only for
`fork/main`.

That creates an asymmetric handoff surface: operators can see whether fork
submission evidence is based on a recent local remote-tracking ref, but cannot
see the same freshness evidence for the preferred source target. Since
`--refresh-remotes` already fetches both `fork/main` and `origin/main` into
local remote-tracking refs, the accepted source path should expose the same
local freshness evidence as the fallback fork path.

## Decision

Extend `autarkic_systems.github_submission` so `GitHubSubmissionStatus`
records freshness for `refs/remotes/origin/main` as
`origin_main_ref_freshness`, using the same reflog-based freshness helper,
clock seam, freshness window, and unknown/fresh/stale state model already used
for `fork/main`.

The JSON payload will add
`origin_main.remote_ref_freshness` while preserving the existing
`fork_main.remote_ref_freshness` shape. Text output will render both
`fork/main freshness: ...` and `origin/main freshness: ...`.

Do not change accepted/submission-state semantics, refresh semantics, remote
URLs, compare URLs, handoff readiness rules, project-status behavior, or any
formal-confidence/source-status evidence.

## Success Criteria

- Red tests fail before implementation because origin freshness is absent and
  the remote-ref freshness text helper is hardcoded to `fork/main`.
- `GitHubSubmissionStatus` includes origin-main remote-ref freshness computed
  from `refs/remotes/origin/main`.
- GitHub submission JSON includes `origin_main.remote_ref_freshness` with the
  same shape as `fork_main.remote_ref_freshness`.
- GitHub submission text reports `origin/main freshness: fresh (...)` when the
  local origin remote-tracking reflog is fresh.
- Unknown and stale freshness states work for `origin/main` as they already do
  for `fork/main`.
- Accepted and `submission_state` semantics do not change.
- Handoff JSON/text inherits the new embedded origin freshness while remaining
  accepted when the underlying project, vertical demo, and submission evidence
  are accepted.

## Test Plan

- Red:
  `python -m unittest tests.test_github_submission_status.GitHubSubmissionStatusTests.test_status_payload_reports_fork_submission_and_origin_divergence tests.test_github_submission_status.GitHubSubmissionStatusTests.test_text_status_reports_operator_submission_summary tests.test_github_submission_status.GitHubSubmissionStatusTests.test_status_reports_stale_origin_main_ref_freshness tests.test_github_submission_status.GitHubSubmissionStatusTests.test_status_reports_unknown_origin_main_ref_freshness`.
- Green:
  `python -m unittest tests.test_github_submission_status tests.test_handoff_status tests.test_suite_selection`.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- Run the fast suite if runtime permits.

## After Action Report

The focused red run was:

```sh
python -m unittest tests.test_github_submission_status.GitHubSubmissionStatusTests.test_status_payload_reports_fork_submission_and_origin_divergence tests.test_github_submission_status.GitHubSubmissionStatusTests.test_text_status_reports_operator_submission_summary tests.test_github_submission_status.GitHubSubmissionStatusTests.test_status_reports_stale_origin_main_ref_freshness tests.test_github_submission_status.GitHubSubmissionStatusTests.test_status_reports_unknown_origin_main_ref_freshness
```

It failed as intended in four places: three errors because
`origin_main.remote_ref_freshness` was absent from the JSON payload, and one
text failure because only `fork/main freshness: ...` was rendered. The red run
executed 4 tests in 0.004s.

The implementation added `ORIGIN_MAIN_REMOTE_REF`, computed
`origin_main_ref_freshness` with the existing reflog freshness helper, added
`origin_main.remote_ref_freshness` to the JSON payload, and made the freshness
formatter take an explicit ref label so `fork/main` and `origin/main` text use
the same implementation path. Handoff fixtures now include the new dataclass
field and assert that inherited JSON/text renders source freshness.

The exact red run passed after implementation:

```text
Ran 4 tests in 0.001s
OK
```

Focused verification passed:

```sh
python -m unittest tests.test_github_submission_status tests.test_handoff_status tests.test_suite_selection
```

Observed result:

```text
Ran 29 tests in 248.472s
OK
```

Additional verification passed:

```sh
python -m compileall -q autarkic_systems tests
git diff --check
python -m autarkic_systems.test_suite_selection --suite fast
```

The fast suite reported manifest `as-test-suite-selection-v1`, suite `fast`,
129 modules, and 1173 tests passed in 360.837s. No JSON files changed in this
slice. Accepted/submission-state semantics, refresh semantics, handoff
readiness, project-status behavior, and formal-confidence/source-status
evidence remain unchanged.
