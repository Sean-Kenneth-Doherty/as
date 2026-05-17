# Evidence Bundle Registry

ADR-0066 adds `evidence/manifest.json`, the project registry for transition
evidence bundles.

The registry currently lists:

- `evidence/recipient_init_command_message_bundle.json`, the ADR-0065 bundle
  for the positive fixed-upstream recipient init command-message transition;
- `evidence/recipient_non_init_command_rejection_bundle.json`, the ADR-0068
  bundle for the positive upstream `standard-signal` rejection boundary.
- `evidence/multi_command_recipient_rejection_bundle.json`, the ADR-0069
  bundle for the positive direct simultaneous-command rejection boundary.
- `evidence/self_mailbox_init_bundle.json`, the ADR-0072 bundle for the
  positive direct self-mailbox init transition.

Future bundle-producing ADRs should add one entry per bundle.

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
count, validation result count, and one structured record per validation
result.

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

The tests cover registry loading, the current ADR-0065, ADR-0068, ADR-0069, and
ADR-0072 bundle entries, whole registry validation, duplicate bundle-ID
rejection, missing bundle-path rejection, and unregistered sibling bundle-file
rejection.
