# ADR-0294: Vertical Demo Formal Confidence Summary

Date: 2026-05-21

## Status

Accepted.

## Context

ADR-0214 introduced the top-level vertical demo digest so a first-run reader
can see the accepted transition, chain, sequence, proof-rule, command-frontier,
and reproduction surfaces in one place. ADR-0288 and ADR-0291 then made the
formal-confidence validation frontier visible in project status, including a
top-level `formal_confidence_validation` JSON summary derived from
`formal_confidence.results`.

The vertical demo already delegates acceptance and status evidence to project
status, and ADR-0289 allows callers such as handoff to pass the same
project-status payload into `build_vertical_demo_digest`. The digest now
omits the formal-confidence validation frontier even when that already-built
payload exposes it. That forces readers of the demo to leave the digest to
learn whether the fixed-point construction frontier validation is accepted.

## Decision

Extend `autarkic_systems.vertical_demo` so the digest includes a compact
`formal_confidence_validation` field derived from the project-status payload.

When project status already exposes top-level
`formal_confidence_validation`, the vertical demo reuses that field as the
source of truth. If an older or narrowed project-status payload lacks that
top-level field but still includes nested `formal_confidence.results`, the
vertical demo may derive the same accepted/failed validation counts and
accepted frontier subject/label lists from those existing status results. It
must not independently load or revalidate formal-confidence targets.

Text output will add one concise formal-confidence validation line, including
accepted/failed validation counts and the compact accepted frontier label such
as `fixed_point_construction_frontier_status accepted`.

Do not change project-status schema or acceptance semantics, formal-confidence
validation semantics, proof status, blockers, transition/chain/sequence
evidence counts, sequence evidence trail, reproduction commands, or boundary
text.

## Success Criteria

- Red tests fail before implementation because
  `build_vertical_demo_digest(project_status=...)` lacks
  `formal_confidence_validation`.
- Red tests fail before implementation because formatted vertical-demo text
  lacks `fixed_point_construction_frontier_status accepted`.
- Digest JSON includes `formal_confidence_validation` with accepted/failed
  validation counts, accepted frontier subjects, and accepted frontier labels
  inherited from project status when present.
- The digest can derive the same compact summary from existing nested
  `project_status["formal_confidence"]["results"]` when the top-level summary
  is absent.
- Text output includes a concise formal-confidence validation line.
- Existing digest fields, acceptance semantics, sequence evidence trail,
  reproduction commands, and boundary text remain unchanged.

## Test Plan

- Red:
  `python -m unittest tests.test_vertical_demo_digest.VerticalDemoDigestTests.test_digest_reuses_project_status_formal_confidence_validation_summary tests.test_vertical_demo_digest.VerticalDemoDigestTests.test_text_output_names_formal_confidence_validation_frontier`.
- Green:
  `python -m unittest tests.test_vertical_demo_digest tests.test_suite_selection`.
- Live JSON assertion:
  `python -m autarkic_systems.vertical_demo --format json`.
- Assert the live digest is accepted and includes 19 accepted
  formal-confidence validations, 0 failed validations, the accepted
  `AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`
  subject, and compact label `fixed_point_construction_frontier_status`.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- Run the fast suite if runtime permits.

## After Action Report

The focused red run was:

```sh
python -m unittest tests.test_vertical_demo_digest.VerticalDemoDigestTests.test_digest_reuses_project_status_formal_confidence_validation_summary tests.test_vertical_demo_digest.VerticalDemoDigestTests.test_text_output_names_formal_confidence_validation_frontier
```

It failed in the two expected places: the digest raised `KeyError:
'formal_confidence_validation'`, and formatted text did not contain
`fixed_point_construction_frontier_status accepted`. The red run executed 2
tests in 0.002s.

The implementation stayed in `autarkic_systems.vertical_demo`. It adds a
`formal_confidence_validation` digest field that reuses the top-level
project-status summary when present and otherwise derives the same compact
accepted/failed counts and accepted frontier subject/label lists from the
already-built nested `formal_confidence.results` status payload. Text output
now renders a concise line such as:

```text
Formal confidence validation: 19 accepted, 0 failed; fixed_point_construction_frontier_status accepted
```

No formal-confidence target loading or independent revalidation was added.
Project-status schema and acceptance semantics, formal-confidence validation
semantics, proof status, blockers, evidence counts, the sequence evidence
trail, reproduction commands, and boundary text remain unchanged.

The exact red pair then passed:

```text
Ran 2 tests in 0.002s
OK
```

After `main`, `origin/main`, and `fork/main` advanced to `5fc025b` with
ADR-0293, this branch was rebased onto `5fc025b`. The append-style conflicts
in `docs/roadmap.md` and `MEMORY.md` were resolved by preserving both the
landed ADR-0293 entries and the new ADR-0294 entries; no
test-suite-selection source files were edited in this lane.

Post-refresh focused verification passed:

```sh
python -m unittest tests.test_vertical_demo_digest tests.test_suite_selection
```

Observed result:

```text
Ran 16 tests in 398.122s
OK
```

The live JSON assertion ran the real module command:

```sh
python -m autarkic_systems.vertical_demo --format json
```

It completed in 179.771s and confirmed accepted vertical-demo status, 19
accepted formal-confidence validations, 0 failed validations, the accepted
`AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`
subject, and compact label `fixed_point_construction_frontier_status`.

Additional verification passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
```

`compileall` completed successfully, `git diff --check` reported no
whitespace errors, and no JSON files changed in this slice.

The fast suite also passed:

```sh
python -m autarkic_systems.test_suite_selection --suite fast
```

Observed result:

```text
Ran 1176 tests in 230.513s
OK
manifest: as-test-suite-selection-v1 suite: fast module_count: 129
```

This remains a digest/readability improvement only. It does not prove or
promote fixed-point construction, substitution correctness, bridge equality,
arithmetized proof predicates, self-consistency, or any command-token runtime
semantics.
