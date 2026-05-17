# ADR-0070: Evidence Registry Completeness

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0066 through ADR-0069 created an evidence bundle registry, CLI, and three
registered recipient command-message bundles. The registry validates every
listed bundle, but it does not yet prove that every bundle file in `evidence/`
is listed.

That leaves a drift path: a future ADR could add `*_bundle.json` under
`evidence/` but forget the manifest entry. The CLI would still pass because the
new bundle was invisible to the registry.

## Decision

Extend registry validation with a completeness check over sibling
`*_bundle.json` files.

The check will compare the bundle files discovered beside `evidence/manifest.json`
with the paths listed in the registry. Any unregistered bundle file will reject
the registry.

This ADR does not add new Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because registry validation has no
  completeness result and does not reject an unregistered sibling bundle file.
- The checked-in registry validates with a new `registry-completeness` result.
- A registry with an extra unregistered sibling `*_bundle.json` file is
  rejected.
- The evidence registry CLI reports the completeness result.
- Runtime behavior remains unchanged.

## Consequences

The evidence registry becomes a closed index over bundle files in its directory.
Future agents cannot add a bundle artifact beside the manifest without also
registering it.

## Test Plan

- Red: `python -m unittest tests.test_evidence_bundle_registry
  tests.test_evidence_bundle_cli` fails before completeness support exists.
- Green: the same focused tests pass after adding completeness validation.
- Regression: run the evidence registry CLI and the full default suite before
  commit.

## After Action Report

Implemented in `autarkic_systems/evidence_bundle.py`.

The focused red run failed because registry validation did not emit a
`registry-completeness` result and did not reject an unregistered sibling
bundle file. The green implementation records the registry source path at load
time, discovers sibling `*_bundle.json` files beside the manifest, and rejects
any discovered bundle file absent from the registry entries.

The CLI now reports:

```text
OK registry-completeness: all 3 discovered bundle files are registered
```

Runtime behavior remains unchanged.
