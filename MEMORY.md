# Project Memory

- Autarkic Systems is an umbrella project over Autarkic Formal Systems,
  Pervasively Reconfigurable Computing, and Self-Justifying Axiom Systems. It
  should integrate formal confidence and embodied computational sovereignty,
  not drift into a generic AI-research bucket.
- The initial `as` repository had no implementation code. First-order progress
  therefore begins with explicit orientation, literature/subordinate review,
  ADR discipline, and a roadmap before adding artifacts.
- `jpt4/afs` was only a placeholder README at the first review snapshot, so
  `as` currently has to supply the integrative AFS structure rather than rely
  on a mature subordinate repo.
- `jpt4/prc` is the hardware/body side: Universal Cells, RLEM/GELC universality,
  explicit signal and power routing, reversible/asynchronous operation, and
  component-wise reconfigurability.
- `jpt4/sjas` is the logic/self-confidence side: Willard-style systems,
  self-provability of consistency under expressivity constraints, Type NS
  languages, proof coding, substitution, and finite executable substrates.
- The upstream default branch for `as` is `main`; the generic instructions say
  `master`, but local integration should target the actual default branch until
  the owner changes it.
- `jpt4/proflog` is a relevant adjacent public repository, but public `main` at
  `77af848` does not contain the newer Proflog ADR-006x frontier described in
  SJAS `nachlass/LOG.md`.
- On this machine, `guile proflog.scm` in public `jpt4/proflog` fails with
  `Unbound variable: even` at the embedded example program, so it should not be
  treated as passing executable evidence without further repair or a different
  intended Scheme environment.
- `sources/manifest.json` is the repo-owned source baseline for AS, AFS, PRC,
  SJAS, and adjacent Proflog; update it when reviewed commits or source status
  changes.
- The first executable AS probe is `autarkic_systems/universal_cell.py`; run
  `python -m unittest discover` for the current fast test suite.
- `autarkic_systems/transition_predicates.py` is the first named predicate
  bridge over Universal Cell transition results.
- `docs/literature-map.md` is the first source-to-claim map; `docs/open-problems.md`
  ranks likely next ADRs, with transition-claim formalization as the top near-term
  problem.
- `claims/transition_claims.json` plus `autarkic_systems/claim_manifest.py`
  make the current transition predicates executable as named AS claims.
- `step_stem_cell` in `autarkic_systems/universal_cell.py` covers the stem
  automail reconfiguration subset (`wr`, `wl`, `pr`, `pl`) and the first
  standard-signal command-buffer accumulation subset. It still does not decode
  full buffers or route commands.
- `automail_reconfigures_stem` is the predicate/claim bridge for stem automail;
  `claim_manifest.py` must preserve `automail`, `control`, and `buffer` when
  parsing manifest cells.
- `docs/willard-definition-map.md`, `sources/willard_definition_map.json`, and
  `autarkic_systems/willard_map.py` are the first definition-granularity Willard
  anchor layer for P5. The required core sources are Willard2001, Willard2011,
  Willard2016, and Willard2020.
- The Willard map is an anchor index, not an SJAS proof implementation. It
  constrains future formal-confidence work around exact syntax, deduction
  apparatus, proof-code/self-reference, consistency level, and excluded-middle
  boundary choices.
- Direct pushes to `jpt4/as` are blocked for `Sean-Kenneth-Doherty`; current AS
  work is published at `https://github.com/Sean-Kenneth-Doherty/as`, and
  upstream issue `jpt4/as#1` records the permission blocker and fork handoff.
- `sources/proflog_frontier_status.json` and
  `docs/proflog-frontier-status.md` are the P6 source-status record. Public
  `jpt4/proflog` main at `77af848` is background only, not dependency-ready
  executable evidence; the active ADR-0063 through ADR-0068 frontier described
  in SJAS logs is missing from public main. Upstream issue `jpt4/proflog#1`
  asks where that source lives.
- `docs/prc-hardware-witness-map.md`,
  `sources/prc_hardware_witness_map.json`, and
  `autarkic_systems/prc_hardware_map.py` are the P7 hardware/schematic witness
  layer. The next recommended artifact is
  `single-node-triangular-rlem-schematic-and-uc-transition-trace`.
- `schematics/single_node_triangular_rlem_trace.json`,
  `docs/single-node-schematic-trace.md`, and
  `autarkic_systems/schematic_trace.py` implement that first P7 schematic trace:
  one triangular RLEM/Universal Cell key plus one executable `step_fixed_cell`
  replay. It is the structured source for the rendered SVG.
- `schematics/single_node_triangular_rlem_trace.svg`,
  `docs/single-node-schematic-svg.md`, and `autarkic_systems/schematic_svg.py`
  render that first P7 trace. The SVG is generated from the JSON trace and must
  exactly match renderer output in tests.
- `schematics/processor_memory_toggle_trace.json`,
  `docs/processor-memory-toggle-trace.md`, and
  `tests/test_processor_memory_toggle_trace.py` add the second P7 schematic
  trace. It covers processor `step_fixed_cell` behavior with left-memory
  routing and memory toggle to right.
- `schematics/processor_memory_toggle_trace.svg`,
  `docs/processor-memory-toggle-svg.md`, and
  `tests/test_processor_memory_toggle_svg.py` render the processor trace. The
  generic SVG renderer must keep both wire and processor SVGs exactly matched
  to their JSON traces.
- `schematics/stem_automail_reconfiguration_trace.json`,
  `docs/stem-automail-reconfiguration-trace.md`, and
  `tests/test_stem_automail_reconfiguration_trace.py` add the third P7
  schematic trace. It covers the existing `step_stem_cell` automail subset for
  `pl`, reconfiguring stem to processor-left and consuming automail.
- `schematics/stem_automail_reconfiguration_trace.svg`,
  `docs/stem-automail-reconfiguration-svg.md`, and
  `tests/test_stem_automail_svg.py` render the stem automail trace. The SVG
  must expose role and automail before/after fields so reconfiguration is not
  hidden behind a generic triangular node render.
- `docs/stem-buffer-accumulation.md` and
  `tests/test_stem_buffer_accumulation.py` add the first non-automail stem
  behavior: one-hot high-rail selection, 1/0 bit append, full-buffer boundary,
  malformed-input rejection, and automail priority.
- `UC-STEM-BUFFER-ACCUMULATES`, `stem_buffer_accumulates`, and
  `docs/stem-buffer-claim.md` promote that buffer subset into the claim and
  proof-certificate surface. It still excludes command decoding and target
  routing.
- `schematics/stem_buffer_accumulation_trace.json`,
  `docs/stem-buffer-accumulation-trace.md`, and
  `tests/test_stem_buffer_accumulation_trace.py` add a schematic-linked trace
  for one matching-input stem buffer append.
- `schematics/stem_buffer_accumulation_trace.svg`,
  `docs/stem-buffer-accumulation-svg.md`, and
  `tests/test_stem_buffer_svg.py` render that buffer trace and must expose
  control and buffer before/after details.
- `sources/stem_command_buffer_map.json`,
  `autarkic_systems/stem_command_map.py`, and
  `docs/stem-command-buffer-map.md` map five-bit stem command buffers to
  target/command pairs. This is decoder preparation only, not command
  execution.
- `sources/stem_command_execution_source_status.json` and
  `docs/stem-command-execution-source-status.md` record that full stem command
  execution is blocked until AS models self mailbox delivery, command-message
  outputs, and the observed legacy source divergences.
- ADR-0028 adds `Cell.self_mailbox`, command-message vocabulary in
  `language/transition_claim_language.json`, and self-mailbox coverage in the
  checked schematic traces. This is representation only, not command
  execution.
- ADR-0029 expands Universal Cell channel tokens and transition-language
  `signals` to include ADR-0026 command messages. This is representation only:
  command-message input is still rejected by current stem behavior rather than
  executed.
- ADR-0030 processes self-mailbox init-family commands
  (`stem-init`, `wire-r-init`, `wire-l-init`, `proc-r-init`, `proc-l-init`) in
  `step_stem_cell`. It intentionally leaves `standard-signal`,
  `write-buf-zero`, `write-buf-one`, and neighbor-side command consumption
  open.
- ADR-0031 promotes that self-mailbox init execution subset into
  `UC-STEM-SELF-MAILBOX-INIT-COMMAND`,
  `self_mailbox_executes_init_command`, and matching proof-certificate
  coverage. It still does not claim write-buffer, standard-signal, neighbor
  delivery, or full command-buffer execution.
- ADR-0032 adds `schematics/self_mailbox_init_trace.json`, a schematic-linked
  replay for one `proc-l-init` self-mailbox command. The validator now routes
  stem traces with non-empty `self_mailbox` through a self-mailbox init
  alignment check instead of the stem buffer check.
- ADR-0033 adds `schematics/self_mailbox_init_trace.svg`; the SVG renderer now
  treats self-mailbox consumption as its own summary case before generic
  role-change reconfiguration so mailbox before/after and control/buffer
  clearing stay visible.
- ADR-0034 promotes unsupported self-mailbox commands into
  `UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED` and
  `self_mailbox_preserves_unsupported_command`. This is a preservation
  boundary for `standard-signal`, `write-buf-zero`, and `write-buf-one`, not an
  execution semantics claim.
- ADR-0035 adds `schematics/self_mailbox_unsupported_trace.json`; the
  schematic trace validator now routes `self-mailbox-unsupported` mailbox
  traces through a preservation check instead of the self-mailbox init check.
- ADR-0036 adds `schematics/self_mailbox_unsupported_trace.svg`; the SVG
  renderer now has a separate unsupported-mailbox summary case so mailbox,
  control, and buffer preservation stay visible.
- ADR-0037 adds the first narrow command-buffer-to-behavior path:
  `step_stem_cell` decodes a just-completed five-bit buffer and processes it
  only when it is a self-target init-family command. ADR-0044 later changes
  neighbor targets from append-boundary cases into output-channel delivery
  cases; self-target non-init commands still stop at `stem-buffer-appended`.
- ADR-0038 promotes ADR-0037 into `UC-STEM-COMMAND-BUFFER-SELF-INIT` and
  `stem_command_buffer_executes_self_init`, with manifest examples and
  proof-certificate coverage. It still excludes neighbor-target delivery until
  ADR-0044 and self non-init command semantics.
- ADR-0039 adds `schematics/self_command_buffer_init_trace.json`,
  `docs/self-command-buffer-init-trace.md`, and
  `tests/test_self_command_buffer_init_trace.py` for one completed
  `self/proc-l-init` command-buffer dispatch. The schematic trace validator
  now separates `stem-command-buffer-self-processed` traces from ordinary
  buffer accumulation.
- ADR-0040 adds `schematics/self_command_buffer_init_trace.svg`,
  `docs/self-command-buffer-init-svg.md`, and
  `tests/test_self_command_buffer_init_svg.py`. The SVG renderer now gives
  command-buffer init dispatch its own summary branch before generic
  reconfiguration or buffer rendering.
- ADR-0041 promotes completed command buffers outside the self-target init
  slice into `UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED` and
  `stem_command_buffer_preserves_unsupported_completion`. ADR-0044 later
  narrows this live boundary to self-target non-init completed buffers because
  neighbor-target completions now deliver to output channels.
- ADR-0042 adds `schematics/command_buffer_unsupported_trace.json`,
  `docs/command-buffer-unsupported-trace.md`, and
  `tests/test_command_buffer_unsupported_trace.py`. ADR-0044 revises the
  trace from the original `neighbor-a/stem-init` example to a self-target
  `write-buf-one` example preserved at the append boundary.
- ADR-0043 adds `schematics/command_buffer_unsupported_trace.svg`,
  `docs/command-buffer-unsupported-svg.md`, and
  `tests/test_command_buffer_unsupported_svg.py`. The SVG renderer gives
  unsupported command-buffer traces their own summary branch before generic
  buffer rendering; ADR-0044 updates the rendered example to the self-target
  non-init boundary.
- ADR-0044 adds `stem-command-buffer-neighbor-delivered` and implements
  neighbor-target command-buffer delivery onto output channels 0, 1, and 2 for
  `neighbor-a`, `neighbor-b`, and `neighbor-c`. It still does not execute
  command-message inputs on recipient cells.
- ADR-0045 promotes ADR-0044 neighbor-target command-buffer delivery into
  `UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED` and
  `stem_command_buffer_delivers_neighbor_command`, with manifest examples and
  proof-certificate coverage. Recipient-side command-message consumption
  remains open.
- ADR-0046 adds `schematics/neighbor_command_buffer_delivery_trace.json`,
  `docs/neighbor-command-buffer-delivery-trace.md`, and
  `tests/test_neighbor_command_buffer_delivery_trace.py` for one completed
  `neighbor-b/proc-l-init` command buffer delivered to output channel 1.
- ADR-0047 adds `schematics/neighbor_command_buffer_delivery_trace.svg`,
  `docs/neighbor-command-buffer-delivery-svg.md`, and
  `tests/test_neighbor_command_buffer_delivery_svg.py`. The SVG renderer now
  has a neighbor-delivery command-buffer summary branch before generic buffer
  rendering.
