# Project Status Report

ADR-0096 adds `autarkic_systems/project_status.py`, a compact status report
over the current executable evidence surface and blocked command-token
frontier.

## Purpose

AS now has separate commands for transition evidence bundles, composed-chain
evidence bundles, and chain demo reports. Those surfaces are useful, but they
do not by themselves answer the operator question:

What is green now, and what remains blocked?

The project status report answers that by reusing existing validators and
source-status records.

## Run

```sh
python -m autarkic_systems.project_status
python -m autarkic_systems.project_status --format json
```

For the command-token source-status frontier alone, use:

```sh
python -m autarkic_systems.source_status
python -m autarkic_systems.source_status --format json
```

The report validates:

- `evidence/manifest.json`, the transition evidence registry;
- `evidence/chains/manifest.json`, the transition-chain evidence registry;
- `claims/transition_claims.json`, the base transition claim examples;
- `claims/proof_certificates.json`, the base transition proof certificates;
- `claims/transition_chain_claims.json` and
  `claims/transition_chain_proof_certificates.json`, the transition-chain
  claim and proof-certificate surface;
- `language/transition_claim_language.json`, the base transition claim
  language and checked claim/proof surface;
- `language/transition_chain_claim_language.json`, the transition-chain claim
  language and checked chain claim/proof surface;
- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

The text report names:

- overall accepted or rejected status;
- transition evidence accepted or rejected state and bundle count;
- chain evidence accepted or rejected state and bundle count;
- transition claim accepted or rejected state, claim count, example count, and
  matched-example count;
- transition proof-certificate accepted or rejected state and certificate
  count;
- claim/proof failed subjects when either lower surface is rejected;
- transition-chain claim accepted or rejected state and certificate count;
- transition-chain claim failed subjects when that surface is rejected;
- transition language accepted or rejected state and claim/certificate counts;
- chain language accepted or rejected state and claim/certificate counts;
- language failed subjects when a language summary is rejected;
- transition and chain evidence bundle IDs and paths;
- transition bundle primary positive examples and covered examples;
- blocked command tokens;
- blocked runtime surfaces;
- source-status AS boundaries;
- source-status execution-readiness decisions, allowed-change flags, blockers,
  and summaries;
- blocker resolution question IDs and summaries;
- source evidence explaining why unresolved blocker questions remain open;
- resolved blocker question IDs, decisions, and optional detail fields;
- source-status cross-links behind the current blocker trail; and
- the safe next slice from the source-status records.

JSON mode emits the same surface for automation and includes top-level
`schema_version: 15`. If a registry file is missing, the corresponding registry
summary reports `registry-file`; if a registry file is present but malformed,
it reports `registry-json`. Missing or invalid source-status files are also
reported as structured rejected output instead of a traceback. ADR-0099 adds
`frontier.failed_subjects`, which reports `source-status-file` for missing
source-status files and `source-status-json` for malformed source-status
files. ADR-0100 adds `source-status-schema` for source-status JSON that parses
but is not a usable source-status object. ADR-0101 adds the schema version.
ADR-0102 requires accepted source-status records to expose at least one
blocked command token through `command`, `commands`, or
`blocked_runtime_commands`. ADR-0103 adds those extracted commands to each
accepted `frontier.source_statuses` entry and bumps the schema version to `2`.
ADR-0104 rejects blank command-token strings as `source-status-schema`
failures. ADR-0105 rejects whitespace-only `decision` and `safe_next_slice`
text as source-status schema failures. ADR-0106 rejects non-text command-list
entries as source-status schema failures. ADR-0107 rejects malformed
command-token field container shapes. ADR-0108 adds per-source
`required_resolution_questions` and bumps the schema version to `3`. ADR-0109
rejects malformed resolution-question metadata when that optional field is
present. ADR-0110 renders the accepted resolution question IDs in the default
text report without changing the JSON shape. ADR-0111 adds per-source
`resolution_questions` objects with `question_id` and `summary`, renders those
summaries in text, and bumps the schema version to `4`. ADR-0112 adds
per-source `blocked_runtime_surfaces`, renders those surfaces in text, rejects
malformed surface lists as source-status schema failures, and bumps the schema
version to `5`. ADR-0115 adds registry `bundles` arrays to both
`transition_evidence` and `chain_evidence`, reports `bundles: []` for registry
load failures, and bumps the schema version to `6`.
ADR-0116 renders the accepted registry bundle IDs and paths in the default text
report without changing the JSON schema.
ADR-0117 requires every accepted source-status record to provide non-empty
top-level `as_boundary` text, preserving `schema_version: 6` while preventing
blank boundary explanations in `frontier.source_statuses`.
ADR-0118 renders those AS boundaries in the default text report without
changing the JSON schema.
ADR-0121 adds `positive_example` and `covered_positive_examples` to transition
evidence bundle entries in JSON and bumps the schema version to `7`.
ADR-0122 renders those transition bundle positive and covered examples in the
default text report while preserving `schema_version: 7`.
ADR-0123 adds per-source `additional_source_statuses` cross-links to project
status JSON, rejects malformed cross-link metadata, and bumps the schema
version to `8`.
ADR-0124 renders those source-status cross-links in the default text report
while preserving `schema_version: 8`.
ADR-0125 requires each source-status cross-link path to exist, reporting
missing cross-link targets as `source-status-schema` while preserving
`schema_version: 8`.
ADR-0126 requires each source-status cross-link path target to contain
parseable top-level JSON object content, reporting invalid or non-object
targets as `source-status-schema` while preserving `schema_version: 8`.
ADR-0128 removes `command-table-offset` from the unresolved standard-signal
resolution questions after resolving that ordering in favor of the formal PRC
stem command-buffer map, while preserving `schema_version: 8`.
ADR-0130 adds `resolved_resolution_questions` to accepted source-status entries,
renders them in the default text report, rejects malformed resolved-question
metadata as `source-status-schema`, and bumps the schema version to `9`.
ADR-0131 requires each resolved question `source_status` path to exist and
contain parseable top-level JSON object content, reporting missing, invalid, or
non-object targets as `source-status-schema` while preserving
`schema_version: 9`.
ADR-0132 carries optional resolved-question detail fields such as
`formal_command_offset` and `legacy_divergence` into project status JSON/text,
rejects malformed detail metadata as `source-status-schema`, and bumps the
schema version to `10`.
ADR-0138 adds `transition_language` and `chain_language` summaries to project
status JSON/text, includes failed-subject lists for rejected language results,
and bumps the schema version to `11`.
ADR-0139 renders those language failed-subject lists in the default text report
as a compact `Language failures:` section while preserving `schema_version: 11`.
ADR-0140 adds `transition_claims` and `transition_proof_certificates`
summaries to project status JSON/text, includes failed-subject lists for
rejected claim/proof results, and bumps the schema version to `12`.
ADR-0141 adds a `chain_claims` summary to project status JSON/text, includes
failed-subject lists for rejected chain-claim results, and bumps the schema
version to `13`.
ADR-0142 records the write-buffer `standard-signal-interaction` question as
resolved in the source-status frontier while preserving project status
`schema_version: 13`.
ADR-0143 records the standard-signal self-mailbox equivalence question as a
resolved source-status detail while preserving project status
`schema_version: 13`.
ADR-0144 adds `resolution_question_evidence` to accepted source-status entries,
renders that evidence in default text output, rejects malformed evidence
metadata as `source-status-schema`, and bumps the schema version to `14`.
ADR-0145 adds `python -m autarkic_systems.source_status` as a focused text/JSON
CLI over the same source-status frontier payload.
ADR-0146 makes `resolution_question_evidence[].question_id` fail closed unless
it matches an unresolved `required_resolution_questions[].question_id` in the
same source-status record, preserving `schema_version: 14`.
ADR-0147 requires `resolution_question_evidence` to cover every unresolved
`required_resolution_questions[].question_id` in the same source-status record,
preserving `schema_version: 14`.
ADR-0148 resolves the standard-signal `recipient-surface` question through the
existing recipient non-init rejection boundary, preserving
`schema_version: 14`.
ADR-0149 rejects source-status records that list the same `question_id` as both
unresolved and resolved, preserving `schema_version: 14`.
ADR-0150 resolves the standard-signal `command-token-vs-binary-input` question
as a negative equivalence decision while leaving project status
`schema_version: 14`.
ADR-0151 resolves the standard-signal `self-target-surface` question through
the existing unsupported preservation boundaries while leaving project status
`schema_version: 14`.
ADR-0152 resolves the write-buffer `recipient-surface` question through the
existing recipient non-init rejection boundary and replaces the old
`recipient-vs-stem-surface` unresolved question with `self-target-surface`,
preserving project status `schema_version: 14`.
ADR-0153 resolves that write-buffer `self-target-surface` question through the
existing unsupported preservation boundaries, leaving only
`buffer-full-boundary` and `post-append-clearing` unresolved while preserving
project status `schema_version: 14`.
ADR-0154 adds optional per-source `execution_readiness` objects to project
status JSON/text, rejects malformed readiness metadata as
`source-status-schema`, and bumps the schema version to `15`.

## Boundary

This is not a simulator, proof checker, registry replacement, or source-status
authority. It delegates registry validation to the existing validators and
reads the current source-status records only to summarize the blocked
command-token frontier.
