# Evidence Bundle Registry

ADR-0066 adds `evidence/manifest.json`, the project registry for transition
evidence bundles.

The registry currently lists:

- `evidence/recipient_init_command_message_bundle.json`, the ADR-0065 bundle
  for the positive fixed-upstream recipient init command-message transition;
- `evidence/recipient_non_init_command_rejection_bundle.json`, the ADR-0068
  bundle for the positive upstream `standard-signal` rejection boundary;
- `evidence/multi_command_recipient_rejection_bundle.json`, the ADR-0069
  bundle for the positive direct simultaneous-command rejection boundary;
- `evidence/self_mailbox_init_bundle.json`, the ADR-0072 bundle for the
  positive direct self-mailbox init transition;
- `evidence/self_mailbox_unsupported_bundle.json`, the ADR-0073 bundle for the
  positive direct unsupported self-mailbox preservation boundary;
- `evidence/self_command_buffer_init_bundle.json`, the ADR-0074 bundle for the
  positive completed self-target command-buffer init dispatch;
- `evidence/command_buffer_unsupported_bundle.json`, the ADR-0075 bundle for
  the positive completed self-target non-init command-buffer append boundary;
- `evidence/neighbor_command_buffer_delivery_bundle.json`, the ADR-0076 bundle
  for the positive completed neighbor-target command-buffer delivery path.

Future bundle-producing ADRs should add one entry per bundle.

Transition-chain evidence bundles are intentionally separate. ADR-0081 stores
the first composed-chain bundle under `evidence/chains/` so the top-level
closed registry remains a single-transition evidence index.

## Validation

`autarkic_systems/evidence_bundle.py` provides
`load_evidence_bundle_registry` and `validate_evidence_bundle_registry`.

The registry validator checks:

- registry schema and metadata;
- duplicate bundle IDs and paths;
- missing bundle files;
- agreement between each registry entry and the loaded bundle; and
- the full cross-layer validation for every registered bundle.

ADR-0070 also makes the registry a closed index over sibling `*_bundle.json`
files. If a bundle file sits beside `evidence/manifest.json` but is not listed
in the manifest, validation rejects the registry.

ADR-0067 adds an operator-facing command over the same validator:

```sh
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

The command prints one `OK` or `FAIL` line per validation subject and exits
with code `0` only when every registry and bundle validation passes.

ADR-0071 adds machine-readable output for the same command:

```sh
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json
```

The JSON payload records the registry ID, overall accepted status, bundle
count, validation result count, one structured record per registered bundle,
and one structured record per validation result.

ADR-0113 makes the JSON payload self-describing by including a `bundles` array
with each registered bundle ID, path, claim ID, and expected status.

## Boundary

The registry is an index and batch-verification surface. It does not create new
Universal Cell behavior, new claims, or new source authority.

## Verification

Run:

```sh
python -m unittest tests.test_evidence_bundle_registry
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json
```

The tests cover registry loading, the current ADR-0065, ADR-0068, ADR-0069,
ADR-0072, ADR-0073, ADR-0074, ADR-0075, and ADR-0076 bundle entries, whole
registry validation, duplicate bundle-ID rejection, missing bundle-path
rejection, and unregistered sibling bundle-file rejection.
