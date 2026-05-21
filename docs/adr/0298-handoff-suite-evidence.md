# ADR-0298: Handoff Suite Evidence

Date: 2026-05-21

## Status

Accepted.

## Context

ADR-0296 exposes a validated all-suite JSON index for the AS unittest selector:

```sh
python -m autarkic_systems.test_suite_selection --list-suites --format json
```

That index names the exact `fast`, `extended-fixed-point`, and `all` suite
boundaries without running tests. The end-of-month handoff already composes
project status, the vertical demo digest, and GitHub submission evidence, but
it does not tell a recipient which verification boundary was in force or how
to reproduce a selected suite. A handoff recipient can therefore see that the
project/demo/submission surfaces are ready while still missing the exact test
selection evidence that frames the report.

## Decision

Extend `autarkic_systems.handoff` with suite-selection evidence derived from
the same validated selector plan used by ADR-0296. The handoff will build the
suite index by loading the suite manifest, discovering test modules, deriving
the checked `SuitePlan`, and serializing the existing suite-index payload. It
will not load or run unittest suites.

The handoff JSON gains a top-level `suite_selection` object containing:

- `accepted`, true only when selector manifest/discovery validation succeeds;
- the suite-index command
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`;
- per-suite selector commands for `fast`, `extended-fixed-point`, and `all`;
- the ADR-0296 suite-index fields and per-suite command metadata when
  validation succeeds; and
- a concise error payload when suite-index validation fails.

Handoff readiness will continue to require accepted project status, accepted
vertical demo, and accepted GitHub submission evidence. It will additionally
require accepted suite-selection evidence so a stale or invalid selector
boundary cannot be handed off as ready.

Text handoff output gains a concise `Suite selection:` section between the
vertical-demo and GitHub-submission sections. The section renders the suite
index command and one line for each selectable suite:

```text
- fast: N modules; python -m autarkic_systems.test_suite_selection --suite fast
```

Do not change suite membership, selector run mode, test execution behavior,
project-status semantics, vertical-demo semantics, GitHub-submission semantics,
formal-confidence files, source-status records, claim manifests, mathematical
semantics, or skip decorators.

## Success Criteria

- Red tests fail before implementation because handoff payloads lack
  `suite_selection` and handoff text lacks the suite-selection section.
- Handoff JSON includes `suite_selection` derived from the validated suite
  index.
- Handoff text includes the suite-index command and module counts plus selected
  suite commands for `fast`, `extended-fixed-point`, and `all`.
- Handoff does not run unittest suites while building suite-selection
  evidence.
- Existing project-status, vertical-demo, and GitHub-submission handoff
  semantics remain unchanged when suite-selection evidence is accepted.
- Invalid suite-selection evidence makes handoff not-ready with a focused,
  inspectable error payload.

## Failure Criteria

- Handoff executes the selected suites while reporting suite-selection
  evidence.
- Handoff emits a ready state when suite manifest/discovery validation fails.
- Handoff invents a second suite selector or changes suite membership relative
  to ADR-0296.
- Existing project/demo/GitHub readiness rules regress.
- This lane edits `autarkic_systems/formal_confidence.py` or
  `tests/test_formal_confidence_target.py`.

## Test Plan

- Red:
  `python -m unittest tests.test_handoff_status.HandoffStatusTests.test_handoff_payload_includes_suite_selection_evidence tests.test_handoff_status.HandoffStatusTests.test_handoff_text_renders_suite_selection_section tests.test_handoff_status.HandoffStatusTests.test_handoff_rejects_when_suite_selection_rejects`.
- Green:
  `python -m unittest tests.test_handoff_status tests.test_suite_selection`.
- Live JSON assertion:
  `python -m autarkic_systems.handoff --format json`, parse the output, and
  assert `suite_selection.accepted`, the suite-index command, selectable suite
  names, and internally consistent suite counts.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.
- Run the fast suite if runtime permits.

## After Action Report

Implemented.

The first red attempt exposed a stale handoff fixture: the fake vertical-demo
digest in `tests/test_handoff_status.py` lacked the already-required
ADR-0294 `formal_confidence_validation` field, so `format_vertical_demo_digest`
raised `KeyError: 'formal_confidence_validation'` before the new assertions
could reach the ADR-0298 gap. The fixture was repaired in the owned handoff
test file.

The focused ADR-0298 red run was:

```sh
python -m unittest tests.test_handoff_status.HandoffStatusTests.test_handoff_payload_includes_suite_selection_evidence tests.test_handoff_status.HandoffStatusTests.test_handoff_text_renders_suite_selection_section tests.test_handoff_status.HandoffStatusTests.test_handoff_rejects_when_suite_selection_rejects
```

It failed as intended with:

```text
KeyError: 'suite_selection'
AssertionError: 'Suite selection:' not found
TypeError: build_handoff_status() got an unexpected keyword argument 'suite_selection_builder'
Ran 3 tests in 0.002s
FAILED (failures=1, errors=2)
```

The implementation stayed in `autarkic_systems.handoff`. It adds
`build_handoff_suite_selection`, which loads the suite manifest, discovers test
modules, derives the validated selector `SuitePlan`, and serializes the
ADR-0296 suite-index payload. It does not construct a unittest runner or run
selected suites. Handoff JSON now carries `suite_selection`; text output now
renders `Suite selection:` between vertical-demo and GitHub-submission
sections. Handoff readiness now also requires `suite_selection.accepted`, so a
suite-selector validation error returns a not-ready handoff with an error
payload.

Focused verification passed:

```sh
python -m unittest tests.test_handoff_status tests.test_suite_selection
```

Observed result:

```text
Ran 22 tests in 195.722s
OK
```

The live handoff JSON assertion ran the real command:

```sh
python -m autarkic_systems.handoff --format json
```

Before the commit was created, local `HEAD` still matched `main` at
`99319ae`; that working-tree assertion returned code 0 and `state=ready`.
After commit and push, the same current-HEAD assertion returned code 1 and
`state=not-ready` because the feature branch commit was not submitted to
`fork/main`, which preserves existing GitHub-submission semantics. In both
runs the parsed payload confirmed `suite_selection.accepted is True`, the
suite index command
`python -m autarkic_systems.test_suite_selection --list-suites --format json`,
selectable suites `fast`, `extended-fixed-point`, and `all`, and internally
consistent counts:

```text
returncode=1 state=not-ready submission=not-submitted-to-fork suite_selection=True suite_counts=fast:129 extended-fixed-point:22 all:151
```

Additional verification passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
python -m autarkic_systems.test_suite_selection --suite fast
```

The fast suite reported:

```text
Ran 1181 tests in 284.768s
OK
manifest: as-test-suite-selection-v1 suite: fast module_count: 129
```

This is a handoff reporting change only. It does not change suite membership,
selector run mode, project-status semantics, vertical-demo semantics,
GitHub-submission semantics, formal-confidence files, source-status records,
claim manifests, mathematical semantics, or skip decorators.
