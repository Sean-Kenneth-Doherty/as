# Source Manifest

The machine-readable manifest is `sources/manifest.json`.

It records the source repositories that currently define the AS working
context:

- `as`: the root Autarkic Systems repository;
- `afs`: the named Autarkic Formal Systems subordinate program;
- `prc`: the embodied substrate and reconfigurable hardware program;
- `sjas`: the self-justifying logic program;
- `proflog`: an adjacent semantic-tableaux candidate referenced by current
  SJAS notes but not yet confirmed as the active executable frontier;
- `leantap`: an adjacent transparent tableaux reference named by ISLA notes and
  reviewed for ADR-0010.

## Verification

Fast structural check:

```sh
jq -e . sources/manifest.json
```

Manual source checks:

```sh
git -C /home/sean/Projects/as rev-parse HEAD
git -C /home/sean/Projects/_upstream/afs rev-parse HEAD
git -C /home/sean/Projects/_upstream/prc rev-parse HEAD
git -C /home/sean/Projects/_upstream/sjas rev-parse HEAD
git -C /home/sean/Projects/_upstream/proflog rev-parse HEAD
git -C /home/sean/Projects/_upstream/leanTAP rev-parse HEAD
```

## Notes

- The current GitHub account has WRITE access to `jpt4/as`; current AS work is
  pushed to source `origin/main` when a slice lands. The fork remote remains
  preserved as a fallback and historical trace for earlier permission-blocked
  submissions.
- The AS `reviewed_commit` records the local integration baseline before
  ADR-0003. The commit containing the manifest necessarily advances AS beyond
  that value, so exact HEAD equality is expected only for the upstream reference
  repositories.
- `jpt4/proflog` is included as adjacent, not subordinate. It is relevant
  because SJAS `nachlass/LOG.md` records recent Proflog-side SJAS work, but the
  public Proflog main branch does not contain the newer ADR-006x material.
- Public Proflog did not pass an execution smoke test under Guile in this
  environment. That failure is a gap to track, not a reason to block AS work.
- LeanTAP is included as a design witness for a compact transparent tableaux
  prover. ADR-0010 does not make it a required runtime dependency.
