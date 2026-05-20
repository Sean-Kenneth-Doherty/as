# ADR-0271: Validation Cache Regression Guard

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0269 landed finite bridge-equality evaluation evidence and connected it to
the fixed-point construction-case validator. That made default discovery
exercise a larger fixed-point evidence stack. A regression in this area can be
pathological: repeated validation of the same checked-in manifests can make
the default suite behave like an extended suite even when no new logical
surface has been added.

The current validators use process-local `lru_cache` wrappers over immutable
loaded manifest dataclasses. This is a runtime guard, not a proof rule. It may
reuse a derived report for the same manifest value inside one Python process,
but changed manifests still load as distinct values and must be validated on
their own merits.

## Decision

Add a focused regression test for the fixed-point validation cache contract.

The guard checks that:

- repeated validation of the checked-in fixed-point construction-case manifest
  returns the cached report and records a cache hit;
- a temp construction-case manifest with a stale dependency list receives a
  separate cache miss and fails closed;
- repeated validation of the checked-in bridge-equality evaluation manifest
  returns the cached report and records a cache hit; and
- a temp bridge-equality evaluation manifest with a stale output length
  receives a separate cache miss and fails closed.

No proof decision is delegated to the cache. The validators still derive and
check the same finite evidence reports. The cache only avoids recomputing the
same report for the same immutable manifest value during one process-local
run.

## Success Criteria

- Red tests fail without the cache behavior because the validation functions
  do not expose cache telemetry and repeated default validation does not
  produce a hit.
- The checked-in default manifests validate once and then reuse a cached
  process-local report for an equal loaded manifest.
- Distinct temp/modified manifests are not masked by the default cache entry
  and fail closed on their own stale facts.
- The test avoids timing thresholds; it asserts cache identity and cache
  hit/miss counts.
- The documentation explains that the cache is not a proof shortcut.
- The documentation explains that the cache protects the default suite from
  accidentally becoming an extended suite.

## Test Plan

- Red/green: `python -m unittest tests.test_fixed_point_validation_cache`.
- Regression: run the ADR-0269 focused tests,
  `python -m unittest tests.test_fixed_point_bridge_equality_evaluation
  tests.test_fixed_point_construction_cases`.
- Hygiene: `python -m compileall autarkic_systems tests` and
  `git diff --check`.

## After Action Report

Implemented 2026-05-20.

The focused regression guard now checks cache behavior directly through
`cache_info()` and report object identity. It covers both fixed-point
construction-case validation and bridge-equality evaluation validation, and it
proves that stale temp manifests remain separate validations by expecting
their existing fail-closed stale-dependency and stale-output-length results.

No production validator change was needed: the process-local caches introduced
around the ADR-0269 landing already satisfy the guard. The boundary remains
unchanged: this is finite validation caching only, not a bridge equality proof,
not a fixed-point equation proof, not an arithmetized proof predicate, and not
self-consistency evidence.
