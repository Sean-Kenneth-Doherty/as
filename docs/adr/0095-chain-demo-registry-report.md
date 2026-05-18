# ADR-0095: Chain Demo Registry Report

Date: 2026-05-17

## Status

Accepted.

## Context

The vertical chain demo report currently renders one transition-chain evidence
bundle at a time. ADR-0094 brought the chain evidence registry to two bundles:
the positive init-consumption path and the non-init rejection path.

Operators can validate both bundles through the chain evidence registry, but
the first-run demo surface still defaults to a single bundle. That makes the
project's current two-path vertical artifact less visible than it should be.

## Decision

Extend `autarkic_systems.chain_demo` with a registry mode. The registry report
will:

- validate the chain evidence registry through the existing registry validator;
- build a vertical demo report for every registered bundle;
- summarize bundle count, accepted count, failed count, and missing evidence
  paths; and
- expose text and JSON CLI output through `--registry`.

`--bundle` and `--registry` will be mutually exclusive. With neither option,
the CLI will preserve the existing default single-bundle report.
If a registry entry names a missing bundle file, registry mode will return a
structured rejected report rather than crashing during per-bundle report
construction.

## Success Criteria

- Red tests fail before implementation because registry demo report functions
  and CLI target selection are missing.
- Registry JSON reports two bundle reports, both accepted, and no missing
  evidence paths.
- Registry text output names both the consumed and rejected chain bundles.
- CLI `--registry ... --format json` emits the registry report and exits `0`.
- Supplying both `--bundle` and `--registry` exits through argparse with code
  `2`.
- A missing registered bundle path exits `1`, records the missing path, and
  preserves the registry failed-subject summary.
- Existing single-bundle demo behavior remains green.

## Consequences

The first-run demo surface can now show the whole current transition-chain
evidence registry without duplicating validation semantics.

## Test Plan

- Red: `python -m unittest tests.test_chain_demo_report` fails before registry
  demo support exists.
- Green: the focused demo report test passes after implementation.
- Regression: run chain evidence registry tests, registry demo CLI text/JSON,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The initial red run of `python -m unittest tests.test_chain_demo_report`
failed because `build_chain_demo_registry_report` did not exist. After the
normal registry path passed, a second red test exposed that a missing registered
bundle path raised `FileNotFoundError` instead of producing a rejected demo
report.

`autarkic_systems.chain_demo` now accepts `--registry`, validates the registry,
builds per-bundle demo reports for existing registered bundles, reports
registered missing bundle paths, and rejects ambiguous `--bundle` plus
`--registry` target selection through argparse.

Verification:

- `python -m unittest tests.test_chain_demo_report` passed 13 tests.
- `python -m unittest tests.test_chain_demo_report tests.test_chain_evidence_bundle_registry tests.test_neighbor_delivery_chain_evidence_bundle tests.test_neighbor_delivery_rejection_chain_evidence_bundle` passed 40 tests.
- `python -m autarkic_systems.chain_demo --registry evidence/chains/manifest.json --format json` reported `accepted: true`, `bundle_count: 2`, `accepted_count: 2`, `failed_count: 0`, and `missing_evidence_paths: []`.
- `python -m autarkic_systems.chain_demo --registry evidence/chains/manifest.json` named both chain evidence bundles.
- `python -m py_compile autarkic_systems/chain_demo.py tests/test_chain_demo_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 536 tests.
