# Chain Evidence Bundle Registry

ADR-0084 adds `evidence/chains/manifest.json`, the project registry for
transition-chain evidence bundles.

The registry currently lists:

- `evidence/chains/neighbor_delivery_chain_bundle.json`, the ADR-0081 bundle
  for the positive neighbor delivery recipient-consumption chain.
- `evidence/chains/neighbor_delivery_rejection_chain_bundle.json`, the
  ADR-0094 bundle for the delivered non-init recipient rejection chain.

## Validation

`autarkic_systems/chain_evidence_bundle.py` provides
`load_chain_evidence_bundle_registry` and
`validate_chain_evidence_bundle_registry`.

The registry validator checks:

- registry schema and metadata;
- duplicate bundle IDs and paths;
- missing bundle files;
- agreement between each registry entry and the loaded chain bundle;
- the full cross-layer validation for every registered chain bundle; and
- closed-index completeness over sibling `*_bundle.json` files in
  `evidence/chains/`.

Run:

```sh
python -m autarkic_systems.chain_evidence_bundle --registry evidence/chains/manifest.json
python -m autarkic_systems.chain_evidence_bundle --registry evidence/chains/manifest.json --format json
```

The command prints one `OK` or `FAIL` line per validation subject in text mode,
emits structured JSON in JSON mode, and exits with code `0` only when every
registry and chain bundle validation passes.

ADR-0086 makes the JSON payload self-describing by including a `bundles` array
with each registered bundle ID, path, chain claim ID, and expected status.
ADR-0087 adds `failed_subjects`, an ordered list of rejected validation
subjects for failed registry runs.
ADR-0088 adds the same `failed_subjects` contract to single-bundle chain
evidence JSON output.
ADR-0094 registers the rejection chain bundle, so the registry now validates
two composed-chain evidence paths.

ADR-0085 makes the target selection explicit: `--bundle` and `--registry` are
mutually exclusive. Supplying both fails during argument parsing with exit code
`2`.

## Boundary

This registry is for composed transition-chain evidence only. The top-level
`evidence/manifest.json` remains the closed registry for single-transition
evidence bundles.
