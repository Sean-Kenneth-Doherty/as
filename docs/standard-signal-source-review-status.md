# Standard-Signal Source Review Status

Status: source-review snapshot, 2026-05-18.

The structured snapshot lives in
`sources/standard_signal_source_review_status.json`.

## Decision

ADR-0171 reviewed the current upstream source heads for AS, AFS, PRC, SJAS,
Proflog, and LeanTAP. None changed from the pinned source manifest remote
heads, and the local PRC witness remained at
`7e82c73fac8f108faac801a5c65e2c2b92653ba5`.

No reviewed source replaces the existing standard-signal command-token
boundary. AS therefore continues to reject delivered recipient
`standard-signal` command messages and preserve self-target `standard-signal`
command tokens as unsupported.

## Boundary

The previous active safe-next slice,
`review-new-standard-signal-command-token-source-evidence-before-execution-change`,
has been performed. The source-status records now use:

`no-standard-signal-command-token-execution-change-without-new-source-evidence`

This is a guard, not a runtime implementation lane. Future work can reopen
standard-signal command-token execution only if new source evidence replaces
the ADR-0165 preserved-unsupported boundary.

## Verification

Run:

```sh
python -m unittest tests.test_standard_signal_source_review_status
```

The tests check the review snapshot, remote-head agreement with
`sources/manifest.json`, the local PRC witness head, the linked source-status
inputs, and the standard-signal source-status backlink.
