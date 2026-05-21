# ADR-0289: Handoff Reuses Project Status For Vertical Demo

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0215 made handoff readiness compose project status, vertical-demo status,
and GitHub submission status. ADR-0286 through ADR-0288 then put the
formal-confidence fixed-point frontier status into the project-status stack
and made its validation visible in handoff summaries.

That composition is correct, but the implementation now performs avoidable
work. `build_handoff_status` builds project status once for the project
summary, then calls `build_vertical_demo_digest`, which builds the same
project-status report again before deriving digest counts and frontier fields.
The process-local formal-confidence cache makes this less costly than a full
cold duplicate traversal, but handoff still walks the project-status surface
twice in one command even though the vertical demo needs the same payload that
handoff has already built.

The fix should be plumbing, not a reporting change. The CLI output and JSON
payload shape should remain stable, and the vertical demo should still build
its own project status when used directly.

## Decision

Allow `build_vertical_demo_digest` to accept an optional already-built
project-status payload. When that payload is supplied, derive digest fields
from it instead of calling `build_project_status_report` again.

Update `build_handoff_status` so it:

- builds project status exactly once;
- passes that same payload object into vertical-demo digest construction; and
- formats the project summary from that same payload.

Keep `build_vertical_demo_digest()` without arguments as the direct CLI/default
path, preserving existing behavior for `python -m autarkic_systems.vertical_demo`.

Do not change formal-confidence semantics, project-status semantics, GitHub
submission semantics, vertical-demo validation rules, output schema, or text
formatting.

## Success Criteria

- Red tests fail before implementation because `build_vertical_demo_digest`
  cannot consume an injected project-status payload and because handoff invokes
  project-status construction twice through the vertical-demo builder path.
- `build_vertical_demo_digest(project_status=...)` does not call
  `build_project_status_report` and preserves accepted digest values/text for
  the supplied status payload.
- `build_handoff_status` builds project status once, passes the same payload
  object to the vertical-demo builder, and preserves existing handoff payload
  and text behavior.
- Direct vertical-demo CLI behavior remains unchanged.
- No schema version, acceptance rule, validation rule, formal-confidence rule,
  or GitHub submission rule changes.

## Test Plan

- Red:
  `python -m unittest tests.test_vertical_demo_digest.VerticalDemoDigestTests.test_digest_accepts_prebuilt_project_status_without_rebuilding tests.test_handoff_status.HandoffStatusTests.test_handoff_reuses_project_status_for_vertical_demo`.
- Green:
  `python -m unittest tests.test_vertical_demo_digest tests.test_handoff_status tests.test_suite_selection`.
- Live smoke:
  `python -m autarkic_systems.handoff --format json`, then parse the JSON and
  assert that the payload still contains project, vertical-demo, and GitHub
  submission sections with a ready or not-ready handoff state.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- Parse changed JSON with `python -m json.tool` if JSON files change.
- Run the fast suite if runtime permits.

## After Action Report

The focused red run was:

```sh
python -m unittest tests.test_vertical_demo_digest.VerticalDemoDigestTests.test_digest_accepts_prebuilt_project_status_without_rebuilding tests.test_handoff_status.HandoffStatusTests.test_handoff_reuses_project_status_for_vertical_demo
```

It failed in the two expected places:

```text
TypeError: build_vertical_demo_digest() got an unexpected keyword argument 'project_status'
TypeError: HandoffStatusTests.test_handoff_reuses_project_status_for_vertical_demo.<locals>.vertical_demo_from_handoff_project_status() missing 1 required keyword-only argument: 'project_status'

Ran 2 tests in 0.002s
FAILED (errors=2)
```

The implementation adds an optional `project_status` payload to
`build_vertical_demo_digest`. Direct callers still build project status
internally, while handoff passes its already-built status payload into the
vertical-demo builder and formats the project summary from that same payload.

The exact red pair then passed:

```text
Ran 2 tests in 0.002s
OK
```

An initial focused-suite run caught one remaining test double that still used
the old zero-argument vertical-demo builder shape. Updating that fake to accept
the optional `project_status` argument preserved the rejected-demo test while
keeping the new handoff contract explicit.

The requested focused suite passed:

```text
python -m unittest tests.test_vertical_demo_digest tests.test_handoff_status tests.test_suite_selection
Ran 19 tests in 512.978s
OK
```

Live handoff smoke passed:

```text
handoff json smoke ok: ready project= True vertical= True github= True
```

The smoke took 2m48.145s and asserted that
`python -m autarkic_systems.handoff --format json` still returns a ready or
not-ready handoff state with `project_status`, `vertical_demo`, and
`github_submission` sections.

Additional verification passed:

```text
python -m compileall autarkic_systems tests
git diff --check
python -m autarkic_systems.test_suite_selection --suite fast
```

`compileall` completed in 2.400s. No JSON files changed, so there were no
changed JSON files to parse with `json.tool`. The fast suite reported manifest
`as-test-suite-selection-v1`, suite `fast`, 129 modules, and 1170 tests passed
in 217.588s.

This is a reuse optimization only. It does not change formal-confidence
semantics, project-status schema or acceptance, GitHub submission semantics,
vertical-demo validation rules, or handoff output shape.
