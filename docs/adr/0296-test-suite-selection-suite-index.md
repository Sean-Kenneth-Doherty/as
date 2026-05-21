# ADR-0296: Test Suite Selection Suite Index JSON

Date: 2026-05-21

## Status

Accepted.

## Context

ADR-0272 introduced the fail-closed unittest suite selector, and ADR-0293 made
one selected suite listable as JSON. That per-suite JSON is enough when an
operator already knows which boundary to inspect, but automation that needs a
complete view of the test surface still has to call the CLI repeatedly for
`fast`, `extended-fixed-point`, and `all`.

The suite boundary already exists as a validated `SuitePlan`: live discovery
is checked against the manifest, explicit modules must be present, leaf suites
must partition discovered modules, and `all` must equal the discovered union.
The missing surface is a single machine-readable index over that checked plan.
It should be suitable for capture by handoff scripts and future agents without
becoming a second selector or changing test membership.

## Decision

Add an explicit suite-index list mode:

```sh
python -m autarkic_systems.test_suite_selection --list-suites --format json
```

The command emits one JSON object derived from the same validated `SuitePlan`
used by per-suite list mode. The payload includes:

- `manifest_id`;
- `manifest_schema_version`;
- `index_schema_version`;
- `discovered_module_count`;
- `selectable_suites`, preserving the CLI suite order;
- `suites`, an object keyed by `fast`, `extended-fixed-point`, and `all`; and
- for each suite, `suite`, `module_count`, `modules`, and the selected
  `unittest` command metadata already exposed by ADR-0293 per-suite JSON.

Text output for `--list-suites` is not introduced in this slice. The index is
an automation surface, so callers must request `--format json`. Existing
`--suite ... --list` text and JSON behavior remains unchanged, and run mode
continues to load the selected suite through stdlib `unittest`.

Do not change suite membership, manifest semantics, run-mode selection,
proof validators, claim manifests, mathematical semantics, source-status
closure files, or skip decorators.

## Success Criteria

- Red tests fail before implementation because `--list-suites --format json`
  is unsupported.
- The JSON suite index contains `fast`, `extended-fixed-point`, and `all`.
- Top-level manifest/schema fields and discovered-module count match the
  validated plan.
- Each suite entry contains `module_count`, `modules`, and selected `unittest`
  command metadata consistent with the ADR-0293 per-suite JSON list payload.
- `selectable_suites` reflects the CLI-selectable suite order.
- Existing `--suite fast --list --format json` and text list mode continue to
  work unchanged.
- Running selected suites remains unchanged.

## Failure Criteria

- The suite index can be produced without passing manifest/discovery
  validation.
- The suite index changes suite membership, ordering, or command metadata
  relative to per-suite JSON list mode.
- Existing text list consumers see changed labels or module bullet format.
- Run mode starts emitting index JSON, stops loading modules through
  `unittest`, or changes exit-code behavior.
- The implementation edits ADR-0295 source-status closure files.

## Test Plan

- Red:
  `python -m unittest tests.test_suite_selection.TestSuiteSelectionTests.test_json_suite_index_lists_all_selectable_suites`.
- Green: `python -m unittest tests.test_suite_selection`.
- Live JSON suite-index smoke:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`.
- Parse the smoke output and assert the selectable suites, per-suite module
  counts, modules, and command metadata are internally consistent.
- Compatibility smokes:
  - `python -m autarkic_systems.test_suite_selection --suite fast --list`;
  - `python -m autarkic_systems.test_suite_selection --suite fast --list
    --format json`.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- Run the fast suite if runtime permits.

## After Action Report

The focused red run was:

```sh
python -m unittest tests.test_suite_selection.TestSuiteSelectionTests.test_json_suite_index_lists_all_selectable_suites
```

It failed before implementation with the expected `SystemExit: 2` because
argparse did not recognize `--list-suites`:

```text
error: unrecognized arguments: --list-suites
Ran 1 test in 0.004s
FAILED (errors=1)
```

The implementation stayed in `autarkic_systems.test_suite_selection`. It adds
`SUITE_INDEX_SCHEMA_VERSION = 1`, derives `build_suite_index_payload` from the
already validated `SuitePlan`, embeds the same ADR-0293 per-suite JSON payload
for every selectable suite, and exposes it only through
`--list-suites --format json`. Text `--list-suites` output is rejected with
exit code 2. Existing `--suite ... --list` text/JSON output and run mode keep
their existing paths.

After `main`, `origin/main`, and `fork/main` advanced to `c3780f1` with
ADR-0295, this branch was rebased onto `c3780f1` with `git rebase --autostash
origin/main`. The only conflict was the append-style `docs/roadmap.md` entry;
it was resolved by preserving the landed ADR-0295 section and adding ADR-0296
after it. No source-status closure files were edited.

Post-rebase focused verification passed:

```sh
python -m unittest tests.test_suite_selection
```

Observed result:

```text
Ran 10 tests in 0.058s
OK
```

The live JSON suite-index smoke ran:

```sh
python -m autarkic_systems.test_suite_selection --list-suites --format json
```

The parsed assertion confirmed manifest `as-test-suite-selection-v1`, schema
`1`, index schema `1`, 151 discovered modules, and suite counts `fast=129`,
`extended-fixed-point=22`, and `all=151`. It also checked that every suite
entry's command metadata used `python -m unittest` followed by exactly that
suite's module list, and that `all` equals the union of the two leaf suites.

Compatibility smokes preserved existing output:

```sh
python -m autarkic_systems.test_suite_selection --suite fast --list
python -m autarkic_systems.test_suite_selection --suite fast --list --format json
```

Text list output still opens with:

```text
manifest: as-test-suite-selection-v1
suite: fast
module_count: 129
modules:
- tests.test_asmsim_process_buffer_status
```

The per-suite JSON smoke confirmed `suite=fast`, `modules=129`, and
`discovered=151`.

Additional post-rebase verification passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
python -m autarkic_systems.test_suite_selection --suite fast
```

The fast suite passed:

```text
Ran 1181 tests in 226.566s
OK
manifest: as-test-suite-selection-v1 suite: fast module_count: 129
```

This remains a suite-index serialization change only. It does not change suite
membership, manifest semantics, run-mode loading, proof validators, claim
manifests, mathematical semantics, ADR-0295 source-status closure behavior,
source-status records, or skip decorators.
