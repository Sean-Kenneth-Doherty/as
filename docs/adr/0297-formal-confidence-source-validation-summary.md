# ADR-0297: Formal Confidence Source Validation Summary

Date: 2026-05-21

## Status

Accepted.

## Context

ADR-0288 and ADR-0291 made aggregate project status expose a compact
formal-confidence validation summary derived from `formal_confidence.results`.
ADR-0294 then carried the same summary into the vertical demo digest. Those
surfaces let operators and automation see that the source-level
formal-confidence validation has 19 accepted validations, 0 failed
validations, and an accepted
`AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`
dependency.

The source command remains less direct:

```sh
python -m autarkic_systems.formal_confidence --format json
```

It emits the raw validation `results`, but automation still has to rescan
those results to recover the same compact summary. This inverts the authority
chain: project status and the vertical demo can show a derived summary, but the
source formal-confidence report does not name the summary it owns.

## Decision

Add a source-level `validation_summary` field to
`formal_confidence_report_payload(report)`, derived only from
`report.results`.

The summary contains:

- `accepted_validation_count`;
- `failed_validation_count`;
- `accepted_frontier_subjects`; and
- `accepted_frontier_labels`.

Text output from `format_formal_confidence_report(report)` will include one
compact line before the raw validation list:

```text
Validation summary: 19 accepted, 0 failed; fixed_point_construction_frontier_status accepted
```

The accepted frontier list is the currently checked formal-confidence frontier
dependency with compact label `fixed_point_construction_frontier_status`.

Do not change validation semantics, target blockers, proof status,
formal-confidence target manifest shape, project-status schema, vertical-demo
schema, handoff behavior, fixed-point validators, or source-status behavior.

## Success Criteria

- Red tests fail before implementation because the source JSON payload lacks
  `validation_summary`.
- Red tests fail before implementation because source text output lacks the
  `Validation summary:` line.
- Source JSON includes `validation_summary` with 19 accepted validations, 0
  failed validations, the accepted
  `AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`
  subject, and compact label `fixed_point_construction_frontier_status`.
- Source text includes the same accepted/failed counts and compact accepted
  frontier label.
- Project-status and vertical-demo derived summaries still agree with the
  source-level summary on checked-in targets.
- Existing target blockers, proof status, failed subjects, result list, and
  target payload shape remain unchanged.

## Failure Criteria

- The summary changes any validation result or acceptance decision.
- The formal-confidence target is promoted beyond its current blocked status.
- Project-status schema or vertical-demo schema changes in this slice.
- The source summary is hand-authored rather than derived from
  `report.results`.

## Test Plan

- Red:
  `python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_json_payload_exposes_validation_summary tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_text_report_exposes_validation_summary`.
- Green:
  `python -m unittest tests.test_formal_confidence_target`.
- Agreement check:
  `python -m unittest tests.test_project_status_report tests.test_vertical_demo_digest tests.test_suite_selection`.
- Live JSON assertion:
  `python -m autarkic_systems.formal_confidence --format json`.
- Assert accepted status, 19 accepted validations, 0 failed validations, the
  accepted fixed-point construction frontier subject, and compact frontier
  label.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- Run the fast suite if runtime permits.

## After Action Report

Implemented.

The focused red run was:

```sh
python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_json_payload_exposes_validation_summary tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_text_report_exposes_validation_summary
```

It failed as intended because the JSON payload had no `validation_summary`
field and the text report had no `Validation summary:` line.

The implementation stays in `autarkic_systems.formal_confidence`. It adds a
derived `formal_confidence_validation_summary(report)` helper, includes that
summary in `formal_confidence_report_payload(report)`, and renders the same
accepted/failed counts plus compact accepted frontier label in text output.
The helper derives the summary from `report.results`; it does not change any
validation result, target blocker, proof status, target manifest shape,
project-status schema, vertical-demo schema, handoff behavior, fixed-point
validator, or source-status behavior.

Focused verification passed:

```sh
python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_json_payload_exposes_validation_summary tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_text_report_exposes_validation_summary
```

Observed result:

```text
Ran 2 tests in 201.574s
OK
```
