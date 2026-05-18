# Source-Status Frontier

ADR-0145 adds `autarkic_systems/source_status.py`, a focused report over the
command-token source-status records that currently bound AS runtime semantics.

## Purpose

The full project status report validates evidence registries, claim/proof
surfaces, object languages, and the source-status frontier. When the immediate
question is only "what command-token semantics are still blocked, and why?",
that broad report can obscure the answer.

The source-status frontier report narrows the first-run surface to the current
command-token blockers:

- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

## Run

```sh
python -m autarkic_systems.source_status
python -m autarkic_systems.source_status --format json
```

Use repeated `--source-status <path>` arguments to validate a specific frontier
subset or a scratch fixture.

The report names:

- accepted or rejected state;
- failed subjects for missing, malformed, or schema-invalid source-status
  records;
- blocked command tokens;
- accepted source-status file paths and decisions;
- blocked runtime surfaces;
- AS boundaries;
- unresolved resolution questions and summaries;
- source evidence explaining why unresolved questions remain open;
- resolved resolution questions and details;
- source-status cross-links behind the blocker trail;
- the safe next slice; and
- missing or invalid source-status paths.

JSON mode emits the same surface with top-level `schema_version: 1`.

## Boundary

This is not a separate source-status authority. It reuses the same frontier
validation used by `python -m autarkic_systems.project_status` so the focused
command and the aggregate command cannot accept different command-token
schemas.
