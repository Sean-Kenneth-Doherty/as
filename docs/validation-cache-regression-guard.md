# Validation Cache Regression Guard

Status: process-local fixed-point validation performance guard, 2026-05-20.

ADR-0271 adds `tests/test_fixed_point_validation_cache.py` to keep the
fixed-point validation cache from silently regressing after ADR-0269 expanded
default discovery through bridge-equality evaluation.

## Purpose

The fixed-point construction-case validator and bridge-equality evaluation
validator derive finite evidence reports from checked manifests. Repeating the
same default-manifest validation inside one Python process should reuse the
same derived report instead of recomputing the whole evidence stack.

This protects the default suite from drifting into extended-suite behavior.
Slow, broader regressions should remain explicit extended checks; repeated
default validation of the same immutable manifest should stay cheap.

## Run

```sh
python -m unittest tests.test_fixed_point_validation_cache
python -m unittest tests.test_fixed_point_bridge_equality_evaluation tests.test_fixed_point_construction_cases
```

The guard checks that:

- repeated checked-in construction-case validation records one cache miss and
  then a cache hit;
- a temp construction-case manifest with a stale dependency list receives its
  own cache miss and fails closed;
- repeated checked-in bridge-equality evaluation validation records one cache
  miss and then a cache hit; and
- a temp bridge-equality evaluation manifest with a stale output length
  receives its own cache miss and fails closed.

## Boundary

The cache is not a proof shortcut. It does not accept stale, modified, or
missing evidence. It only reuses a report when the loaded immutable manifest
value and validation paths are equal inside the current process. Distinct temp
manifests remain distinct cache keys and are validated independently.
