# Command Runtime Frontier

ADR-0299 adds a focused runtime witness for the command-token frontier:

```sh
python -m autarkic_systems.command_runtime_frontier
python -m autarkic_systems.command_runtime_frontier --format json
```

The report first loads the ADR-0295 source-status frontier closure. If that
frontier rejects, the runtime report fails closed and does not claim
implemented runtime state. When the source frontier accepts, the report runs
live Universal Cell transitions for the current command-token boundary:

- recipient `write-buf-zero` command-message append;
- recipient/stem `write-buf-one` command-message append;
- direct self-mailbox `write-buf-one` append;
- completed self-target `write-buf-one` command-buffer append;
- recipient `standard-signal` command-message rejection;
- direct self-mailbox `standard-signal` unsupported preservation; and
- completed self-target `standard-signal` command-buffer append boundary.

This command is not a new source of command semantics. It checks that the live
runtime witnesses still agree with the accepted source-status closure:
`write-buf-zero` and `write-buf-one` remain implemented, while
`standard-signal` remains rejected or preserved unsupported unless new source
evidence replaces that boundary.

The command links existing evidence bundles for the checked runtime surfaces
and does not change Universal Cell behavior, source-status records,
transition predicates, evidence bundles, formal-confidence evidence,
project-status output, vertical-demo output, handoff output, suite selection,
claim manifests, or mathematical semantics.
