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
- ADR-0048 adds `sources/recipient_command_consumption_source_status.json`,
  `docs/recipient-command-consumption-source-status.md`, and
  `tests/test_recipient_command_consumption_source_status.py`. It restores the
  PRC source cache at commit `7e82c73fac8f108faac801a5c65e2c2b92653ba5` as
  ADR evidence and permits only recipient-side init-family command-message
  consumption as the next executable slice.
- ADR-0049 adds `docs/recipient-init-command-message-consumption.md` and
  `tests/test_recipient_init_command_messages.py`. `step_fixed_cell` and
  `step_stem_cell` now consume single input-channel init-family command-message
  tokens with status `recipient-init-command-message-processed`, while
  `standard-signal`, write-buffer, and multi-command inputs remain rejected.
- ADR-0050 adds `docs/recipient-init-command-message-claim.md` and
  `tests/test_recipient_init_command_message_claim.py`. The claim
  `UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED` is checked by
  `recipient_init_command_message_processed` and covers fixed upstream, stem
  direct-input, and negative wrong-target examples.
- ADR-0051 adds `docs/recipient-init-command-message-trace.md`,
  `schematics/recipient_init_command_message_trace.json`, and
  `tests/test_recipient_init_command_message_trace.py`. The trace replays a
  fixed processor-left recipient consuming upstream `wire-r-init` into
  wire-right state with status `recipient-init-command-message-processed`.
- ADR-0052 adds `docs/recipient-init-command-message-svg.md`,
  `schematics/recipient_init_command_message_trace.svg`, and
  `tests/test_recipient_init_command_message_svg.py`. The renderer now has a
  recipient init command-message summary branch exposing upstream before/after
  and cleared command state.
- ADR-0053 adds `sources/recipient_non_init_command_source_status.json`,
  `docs/recipient-non-init-command-source-status.md`, and
  `tests/test_recipient_non_init_command_source_status.py`. It blocks
  recipient `standard-signal`, write-buffer, and multi-command input execution
  and selects a named rejection-boundary claim as the next safe slice.
- ADR-0054 adds `docs/recipient-non-init-command-rejection-claim.md` and
  `tests/test_recipient_non_init_command_rejection_claim.py`. The claim
  `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` is checked by
  `recipient_non_init_command_message_rejected` and covers fixed direct,
  fixed upstream, and stem multi-command rejection boundaries.
- ADR-0055 adds `docs/recipient-non-init-command-rejection-trace.md`,
  `schematics/recipient_non_init_command_rejection_trace.json`, and
  `tests/test_recipient_non_init_command_rejection_trace.py`. The trace replays
  a fixed processor-left recipient rejecting an upstream `standard-signal`
  command-message token while preserving role/memory and clearing upstream
  command state.
- ADR-0056 adds `docs/recipient-non-init-command-rejection-svg.md`,
  `schematics/recipient_non_init_command_rejection_trace.svg`, and
  `tests/test_recipient_non_init_command_rejection_svg.py`. The renderer now
  has a recipient non-init rejection summary branch exposing upstream
  before/after state, role/memory preservation, and cleared command channels.
- ADR-0057 adds `docs/write-buffer-command-semantics-status.md`,
  `sources/write_buffer_command_semantics_status.json`, and
  `tests/test_write_buffer_command_semantics_status.py`. It keeps
  `write-buf-zero` and `write-buf-one` execution blocked because formal, RAA,
  SEMSIM, and FSMSIM witnesses do not agree on append, clearing, and
  buffer-full boundaries.
- ADR-0058 adds `docs/standard-signal-command-semantics-status.md`,
  `sources/standard_signal_command_semantics_status.json`, and
  `tests/test_standard_signal_command_semantics_status.py`. It keeps
  `standard-signal` command-token execution blocked because formal
  command-table placement, ordinary binary-input standard-signal behavior, and
  legacy special-message sketches do not define the same runtime surface.
  ADR-0059 later selects the multi-command recipient input policy.
- ADR-0059 adds `docs/multi-command-recipient-input-policy-status.md`,
  `sources/multi_command_recipient_input_policy_status.json`, and
  `tests/test_multi_command_recipient_input_policy_status.py`. It selects
  reject-and-clear for two or more simultaneous recipient command-message
  inputs, adds an all-init conflict example to
  `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`, and moves the next safe
  slice to a multi-command rejection trace.
- ADR-0060 adds `docs/multi-command-recipient-rejection-trace.md`,
  `schematics/multi_command_recipient_rejection_trace.json`, and
  `tests/test_multi_command_recipient_rejection_trace.py`. It reuses the
  recipient non-init rejection trace validator for a fixed direct
  `wire-r-init` plus `proc-l-init` conflict and sets up the multi-command
  rejection SVG slice completed by ADR-0061.
- ADR-0061 adds `docs/multi-command-recipient-rejection-svg.md`,
  `schematics/multi_command_recipient_rejection_trace.svg`, and
  `tests/test_multi_command_recipient_rejection_svg.py`. The renderer reuses
  the recipient non-init rejection summary branch for the direct
  `wire-r-init` plus `proc-l-init` conflict, and the frontier returns to
  source resolution for `standard-signal` or write-buffer command semantics.
- ADR-0062 adds `docs/guile-asmsim-command-semantics-status.md`,
  `sources/guile_asmsim_command_semantics_status.json`, and
  `tests/test_guile_asmsim_command_semantics_status.py`. It records
  `guile-asmsim.scm` as blocker-strengthening evidence: init-family-only
  special messages, binary/numeric write-buffer behavior, and a divergent
  command-list expression rather than executable standard-signal/write-buffer
  command-token semantics.
- ADR-0063 adds `docs/asmsim-process-buffer-status.md`,
  `sources/asmsim_process_buffer_status.json`, and
  `tests/test_asmsim_process_buffer_status.py`. It records
  `practice/asmsim.scm` as blocker-strengthening process-buffer evidence:
  explicit documentation/code-confirmation warnings, code-shape predicates,
  and a `msg-list` placeholder rather than resolved named command-token
  semantics.
- ADR-0064 adds `docs/official-tla-universal-cell-status.md`,
  `sources/official_tla_universal_cell_status.json`, and
  `tests/test_official_tla_universal_cell_status.py`. It records PRC's
  official TLA files as partial, stub, or empty and not executable Universal
  Cell or command-semantics authority.
- ADR-0065 adds `docs/recipient-init-transition-evidence-bundle.md`,
  `evidence/recipient_init_command_message_bundle.json`,
  `autarkic_systems/evidence_bundle.py`, and
  `tests/test_recipient_init_transition_evidence_bundle.py`. It validates one
  recipient init transition across claim, proof, schematic trace, SVG render,
  hardware witness map, and source-status boundaries.
- ADR-0066 adds `docs/evidence-bundle-registry.md`,
  `evidence/manifest.json`, and `tests/test_evidence_bundle_registry.py`. It
  makes transition evidence bundles discoverable and batch-validates every
  registered bundle through the cross-layer bundle validator.
- ADR-0067 adds `tests/test_evidence_bundle_cli.py` and a module CLI in
  `autarkic_systems/evidence_bundle.py`: run
  `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json`
  to validate the evidence registry with `OK`/`FAIL` output and exit codes.
- ADR-0068 adds `docs/recipient-non-init-evidence-bundle.md`,
  `evidence/recipient_non_init_command_rejection_bundle.json`, and
  `tests/test_recipient_non_init_evidence_bundle.py`. It registers the
  recipient upstream `standard-signal` rejection boundary as the second
  evidence bundle.
- ADR-0069 adds `docs/multi-command-rejection-evidence-bundle.md`,
  `evidence/multi_command_recipient_rejection_bundle.json`, and
  `tests/test_multi_command_evidence_bundle.py`. It registers the direct
  simultaneous `wire-r-init` plus `proc-l-init` rejection boundary as the third
  evidence bundle.
- ADR-0070 adds registry completeness checking in
  `autarkic_systems/evidence_bundle.py`. The evidence registry CLI now reports
  `registry-completeness` and rejects sibling `*_bundle.json` files that are
  not listed in `evidence/manifest.json`.
- ADR-0071 adds `--format json` to
  `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json`.
  The JSON report includes registry ID, accepted status, bundle count, result
  count, and per-result subject/accepted/detail records.
- ADR-0072 adds `docs/self-mailbox-init-evidence-bundle.md`,
  `evidence/self_mailbox_init_bundle.json`, and
  `tests/test_self_mailbox_init_evidence_bundle.py`. It registers the direct
  self-mailbox `proc-l-init` transition as the fourth evidence bundle and
  aligns the checked trace/SVG fixture with the named claim example.
- ADR-0073 adds `docs/self-mailbox-unsupported-evidence-bundle.md`,
  `evidence/self_mailbox_unsupported_bundle.json`, and
  `tests/test_self_mailbox_unsupported_evidence_bundle.py`. It registers the
  direct unsupported self-mailbox `write-buf-one` preservation boundary as the
  fifth evidence bundle and aligns the checked trace/SVG fixture with the
  named claim example.
- ADR-0074 adds `docs/self-command-buffer-init-evidence-bundle.md`,
  `evidence/self_command_buffer_init_bundle.json`, and
  `tests/test_self_command_buffer_init_evidence_bundle.py`. It registers the
  completed self-target `self/proc-l-init` command-buffer dispatch as the
  sixth evidence bundle.
- ADR-0075 adds `docs/command-buffer-unsupported-evidence-bundle.md`,
  `evidence/command_buffer_unsupported_bundle.json`, and
  `tests/test_command_buffer_unsupported_evidence_bundle.py`. It registers the
  completed self-target `self/write-buf-one` command-buffer append boundary as
  the seventh evidence bundle.
- ADR-0076 adds `docs/neighbor-command-buffer-delivery-evidence-bundle.md`,
  `evidence/neighbor_command_buffer_delivery_bundle.json`, and
  `tests/test_neighbor_command_buffer_delivery_evidence_bundle.py`. It
  registers the completed neighbor-target `neighbor-b/proc-l-init`
  command-buffer delivery path as the eighth evidence bundle.
- ADR-0077 adds `docs/neighbor-delivery-recipient-chain.md`,
  `autarkic_systems/transition_chains.py`, and
  `tests/test_neighbor_delivery_recipient_chain.py`. It composes the
  `neighbor-b/proc-l-init` delivery output into an empty recipient upstream
  tuple and consumes it through the existing recipient init-family command
  logic, while reporting explicit precondition and non-init boundaries.
- ADR-0078 adds `docs/neighbor-delivery-chain-claim.md`,
  `claims/transition_chain_claims.json`,
  `claims/transition_chain_proof_certificates.json`,
  `autarkic_systems/transition_chain_predicates.py`,
  `autarkic_systems/chain_claims.py`, and
  `tests/test_neighbor_delivery_chain_claim.py`. It creates a separate
  manifest-example claim/proof surface for the ADR-0077 two-step handoff
  rather than forcing chain claims into the single-transition claim language.
- ADR-0079 adds `docs/transition-chain-claim-language.md`,
  `language/transition_chain_claim_language.json`,
  `autarkic_systems/chain_object_language.py`, and
  `tests/test_chain_object_language.py`. It validates the explicit
  transition-chain claim language, including chain statuses, implemented chain
  predicates, `UC-CHAIN-` sentence prefixes, proof rules, and the current chain
  claim/certificate surface.
- ADR-0080 adds `docs/adr/0080-transition-chain-claim-cli.md` and
  `tests/test_transition_chain_claim_cli.py`, and extends
  `autarkic_systems/chain_claims.py` with
  `python -m autarkic_systems.chain_claims`. The CLI validates the chain
  language manifest, executable examples, proof certificates, and claim surface
  in text or JSON form.
- ADR-0081 adds `docs/neighbor-delivery-chain-evidence-bundle.md`,
  `evidence/chains/neighbor_delivery_chain_bundle.json`,
  `autarkic_systems/chain_evidence_bundle.py`, and
  `tests/test_neighbor_delivery_chain_evidence_bundle.py`. Chain evidence
  bundles live under `evidence/chains/` so `evidence/manifest.json` remains the
  closed single-transition evidence registry.
- ADR-0082 adds `docs/neighbor-delivery-chain-trace.md`,
  `schematics/chains/neighbor_delivery_recipient_chain_trace.json`,
  `autarkic_systems/chain_trace.py`, and
  `tests/test_neighbor_delivery_chain_trace.py`. It records the sender step,
  handoff tuple, recipient step, and whole-chain helper replay for the first
  transition-chain handoff, and the ADR-0081 evidence bundle now validates it.
- ADR-0083 adds `docs/neighbor-delivery-chain-svg.md`,
  `schematics/chains/neighbor_delivery_recipient_chain_trace.svg`,
  `autarkic_systems/chain_svg.py`, and
  `tests/test_neighbor_delivery_chain_svg.py`. The checked SVG must exactly
  match renderer output, and the ADR-0081 evidence bundle now validates it.
- ADR-0084 adds `docs/chain-evidence-bundle-registry.md`,
  `evidence/chains/manifest.json`, and
  `tests/test_chain_evidence_bundle_registry.py`. The registry validates
  transition-chain evidence bundles separately from the top-level
  single-transition `evidence/manifest.json` registry.
- ADR-0085 makes `--bundle` and `--registry` mutually exclusive for
  `python -m autarkic_systems.chain_evidence_bundle`; supplying both exits
  through argparse with code `2`.
- ADR-0086 adds a `bundles` array to chain evidence registry JSON output,
  listing each registered bundle ID, path, chain claim ID, and expected status.
- ADR-0087 adds `failed_subjects` to chain evidence registry JSON output so
  failed registry runs summarize rejected validation subjects directly.
- ADR-0088 adds `failed_subjects` to single-bundle chain evidence JSON output
  so failed bundle runs summarize rejected validation subjects directly.
- ADR-0089 adds `autarkic_systems.chain_demo`, a text/JSON first-run report
  over the current transition-chain claim, validation result, trace, SVG,
  lower-level evidence bundles, source-status boundaries, and explicit
  boundary terms.
- ADR-0090 adds per-layer `exists` flags and top-level
  `missing_evidence_paths` to the chain demo report so artifact presence is
  explicit in text and JSON output.
- ADR-0091 adds `neighbor_delivery_rejected_by_recipient` and
  `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED`, naming the delivered
  non-init recipient rejection boundary as a second transition-chain claim.
- ADR-0092 adds
  `schematics/chains/neighbor_delivery_rejection_chain_trace.json` and lets
  chain traces validate expected rejection statuses when replayed status and
  cells match.
- ADR-0093 adds
  `schematics/chains/neighbor_delivery_rejection_chain_trace.svg` and updates
  chain SVG rendering/validation to derive the visible handoff channel from
  the delivered tuple.
- ADR-0094 adds
  `evidence/chains/neighbor_delivery_rejection_chain_bundle.json` and registers
  it in `evidence/chains/manifest.json`, bringing the chain evidence registry
  to two bundles.
- ADR-0095 adds `--registry` mode to `autarkic_systems.chain_demo`, so the
  vertical demo report can summarize every registered transition-chain
  evidence bundle, including accepted/failed counts, missing paths, and
  structured failure output for missing registered bundle files.
- ADR-0096 adds `autarkic_systems.project_status`, a text/JSON status command
  that validates the transition evidence registry and chain evidence registry,
  reports 8 transition bundles and 2 chain bundles on the checked-in path, and
  summarizes the blocked `standard-signal`, `write-buf-zero`, and
  `write-buf-one` command-token frontier from source-status JSON.
- ADR-0097 hardens `autarkic_systems.project_status` so missing transition or
  chain registry paths produce structured rejected text/JSON status output
  with `failed_subjects: ["registry-file"]` instead of a traceback.
- ADR-0098 refines `autarkic_systems.project_status` so malformed transition
  or chain registry files report `failed_subjects: ["registry-json"]` and text
  output names invalid registry files separately from missing registry files.
- ADR-0099 adds `frontier.failed_subjects` to `autarkic_systems.project_status`:
  checked-in status reports `[]`, missing source-status files report
  `source-status-file`, malformed source-status files report
  `source-status-json`, and mixed failures preserve that order.
- ADR-0100 makes `autarkic_systems.project_status` reject source-status JSON
  that parses but lacks a top-level object, non-empty `decision`, and non-empty
  `safe_next_slice`, reporting `source-status-schema`.
- ADR-0101 adds top-level `schema_version: 1` to
  `autarkic_systems.project_status` JSON output so automation can detect
  future contract changes.
- ADR-0102 makes `autarkic_systems.project_status` reject source-status JSON
  that has process fields but no extractable command tokens, reporting
  `source-status-schema` instead of accepting an empty blocked-command
  frontier.
- ADR-0103 bumps `autarkic_systems.project_status` to `schema_version: 2` and
  adds a per-source `commands` list to accepted `frontier.source_statuses`
  entries so the status report attributes blocked commands to source-status
  artifacts.
- ADR-0104 makes `autarkic_systems.project_status` reject blank command-token
  strings in source-status command fields as `source-status-schema`, preserving
  `schema_version: 2`.
- ADR-0105 makes `autarkic_systems.project_status` reject whitespace-only
  `decision` and `safe_next_slice` fields as `source-status-schema`, preserving
  `schema_version: 2`.
- ADR-0106 makes `autarkic_systems.project_status` reject non-text entries in
  source-status command-token lists as `source-status-schema`, preserving
  `schema_version: 2`.
- ADR-0107 makes `autarkic_systems.project_status` reject malformed
  source-status command-token field containers as `source-status-schema`,
  preserving `schema_version: 2`.
- ADR-0108 bumps `autarkic_systems.project_status` to `schema_version: 3` and
  adds per-source `required_resolution_questions` IDs to accepted
  `frontier.source_statuses` entries.
- ADR-0109 makes `autarkic_systems.project_status` reject malformed
  source-status `required_resolution_questions` metadata as
  `source-status-schema`, preserving `schema_version: 3`.
- ADR-0110 makes the default `autarkic_systems.project_status` text report
  render the checked standard-signal and write-buffer resolution question IDs,
  preserving `schema_version: 3`.
- ADR-0111 bumps `autarkic_systems.project_status` to `schema_version: 4` and
  adds summary-bearing per-source `resolution_questions` objects while keeping
  the existing `required_resolution_questions` ID lists.
- ADR-0112 bumps `autarkic_systems.project_status` to `schema_version: 5`,
  adds per-source `blocked_runtime_surfaces`, renders them in text status, and
  rejects malformed surface lists as `source-status-schema`.
- ADR-0113 adds a `bundles` array to transition evidence registry JSON output,
  listing each registered bundle ID, path, claim ID, and expected status.
- ADR-0114 adds `failed_subjects` to transition evidence registry JSON output,
  matching the compact failure-summary shape already used by chain registry
  JSON.
- ADR-0115 bumps `autarkic_systems.project_status` to `schema_version: 6` and
  adds transition and chain registry `bundles` arrays to the project status
  JSON summaries.
- ADR-0116 makes the default `autarkic_systems.project_status` text report
  render transition and chain registry bundle IDs and paths while preserving
  `schema_version: 6`.
- ADR-0117 requires non-empty top-level `as_boundary` text on source-status
  records consumed by project status and adds that boundary to the recipient
  non-init command-message source-status artifact.
- ADR-0118 makes the default `autarkic_systems.project_status` text report
  render source-status AS boundaries while preserving `schema_version: 6`.
- ADR-0119 expands the unsupported self-mailbox and self-target command-buffer
  claim/proof surfaces so `standard-signal`, `write-buf-zero`, and
  `write-buf-one` each have explicit positive self-command boundary examples.
- ADR-0120 adds optional transition evidence bundle `covered_positive_examples`
  validation and uses it on the unsupported self-mailbox and self-target
  command-buffer bundles so the integrated evidence layer reflects ADR-0119's
  explicit command coverage.
- ADR-0121 exposes transition evidence bundle `positive_example` and
  `covered_positive_examples` in registry JSON and project-status JSON,
  bumping project status to `schema_version: 7`.
- ADR-0122 renders transition evidence bundle `positive_example` and
  `covered_positive_examples` in default project-status text while preserving
  project status `schema_version: 7`.
- ADR-0123 exposes source-status `additional_source_statuses` cross-links in
  project-status JSON and bumps project status to `schema_version: 8`, with
  schema failures for malformed cross-link metadata.
- ADR-0124 renders source-status `additional_source_statuses` cross-links in
  default project-status text while preserving project status
  `schema_version: 8`.
- ADR-0125 makes project-status source-status cross-links fail closed when
  `additional_source_statuses[].path` does not point to an existing file,
  preserving project status `schema_version: 8`.
- ADR-0126 makes those project-status source-status cross-links fail closed
  when the target file does not contain parseable top-level JSON object
  content, preserving project status `schema_version: 8`.
- ADR-0127 adds the PRC formal-model self-mailbox exception to
  `sources/standard_signal_command_semantics_status.json`: ordinary productive
  standard-signal behavior must not be applied by default to stem
  self-mailbox `standard-signal` command tokens, so runtime behavior remains
  blocked pending a later preserve/clear/no-op semantics decision.
- ADR-0128 resolves the standard-signal `command-table-offset` question in
  favor of the formal PRC map encoded by `sources/stem_command_buffer_map.json`
  (`standard-signal` offset `0`) and removes that question from the project
  status unresolved queue; command-token execution remains blocked.
- ADR-0129 adds `command_bit_source` to
  `sources/write_buffer_command_semantics_status.json`, recording that
  `write-buf-zero` and `write-buf-one` carry literal `0` and `1` append bits
  across the formal model and RAA/SEMSIM/FSMSIM witnesses. Runtime behavior and
  the unresolved write-buffer question queue remain unchanged.
- ADR-0130 bumps project status to `schema_version: 9` and exposes
  `resolved_resolution_questions` in JSON/text, so the standard-signal
  `command-table-offset` decision is visible as settled from the first status
  command while the remaining command-token questions stay open.
- ADR-0131 makes project-status resolved-question `source_status` paths fail
  closed when the target is missing, invalid JSON, or non-object JSON,
  preserving project status `schema_version: 9`.
- ADR-0132 bumps project status to `schema_version: 10` and preserves optional
  resolved-question details in JSON/text, including the standard-signal
  `formal_command_offset: 0` and the RAA legacy divergence.
- ADR-0133 adds the `predicate-result` proof-certificate rule for transition
  claims, migrates the fixed-output preservation certificate to that rule, and
  updates the transition object-language proof-object rules accordingly.
- ADR-0172 migrates the consumed-input clearing proof certificate to
  `predicate-result`, so the two foundational fixed-cell proof certificates
  now name their evaluated predicates directly.
- ADR-0173 migrates the fixed-role memory-rule proof certificate to
  `predicate-result`, extending explicit predicate-named proof steps across
  the first three foundational fixed-cell claims.
- ADR-0174 migrates the stem-init reset proof certificate to
  `predicate-result`, completing explicit predicate-named proof steps for the
  four original fixed-cell claims.
- ADR-0175 migrates the automail reconfiguration proof certificate to
  `predicate-result`, extending explicit predicate-named proof steps into the
  first stem reconfiguration claim.
- ADR-0134 adds `python -m autarkic_systems.proof_certificates` with text/JSON
  validation of the transition proof-certificate surface and failing exit codes
  for rejected certificate manifests.
- ADR-0135 adds `python -m autarkic_systems.claim_manifest` with text/JSON
  validation of the base transition claim examples and failing exit codes for
  mismatched manifest expectations.
- ADR-0136 adds `python -m autarkic_systems.object_language` with text/JSON
  validation of the transition claim language and checked claim/proof surface,
  including failing exit codes for rejected language surfaces.
- ADR-0137 adds `python -m autarkic_systems.chain_object_language` with
  text/JSON validation of the transition-chain claim language and checked chain
  claim/proof surface.
- ADR-0138 bumps `autarkic_systems.project_status` to `schema_version: 11` and
  adds `transition_language` and `chain_language` summaries for the base and
  chain object-language surfaces.
- ADR-0139 adds a default project-status text `Language failures:` section,
  while preserving project status `schema_version: 11`.
- ADR-0140 bumps `autarkic_systems.project_status` to `schema_version: 12` and
  adds `transition_claims` and `transition_proof_certificates` summaries for
  the base transition claim-example and proof-certificate validators.
- ADR-0141 bumps `autarkic_systems.project_status` to `schema_version: 13` and
  adds a `chain_claims` summary for the transition-chain claim validator.
- ADR-0142 resolves the write-buffer `standard-signal-interaction` blocker as
  literal command-bit source evidence rather than high-rail-derived behavior,
  leaving execution surface, buffer-full behavior, and post-append clearing in
  the unresolved write-buffer queue.
- ADR-0143 resolves the standard-signal
  `self-mailbox-standard-signal-binary-input-equivalence` detail: a stem
  self-mailbox `standard-signal` command must not be treated as ordinary
  binary-input standard-signal behavior, while the broader self-target-surface
  command-token behavior remains unresolved.
- ADR-0144 bumps `autarkic_systems.project_status` to `schema_version: 14` and
  exposes `resolution_question_evidence` for unresolved standard-signal and
  write-buffer blockers in JSON/text, with fail-closed schema validation.
- ADR-0145 adds `python -m autarkic_systems.source_status` as a focused
  text/JSON CLI over the same blocked command-token source-status frontier
  consumed by project status, with JSON `schema_version: 1`.
- ADR-0146 makes source-status `resolution_question_evidence[].question_id`
  values fail closed unless they match unresolved
  `required_resolution_questions[].question_id` values in the same record.
- ADR-0147 makes source-status `resolution_question_evidence` fail closed
  unless it covers every unresolved `required_resolution_questions` ID in the
  same record.
- ADR-0148 resolves the standard-signal `recipient-surface` question through
  the existing recipient non-init rejection boundary, leaving
  `command-token-vs-binary-input` and `self-target-surface` as the live
  standard-signal unresolved questions.
- ADR-0149 makes unresolved and resolved source-status question IDs disjoint,
  so a source-status record cannot present a blocker as both live and settled.
- ADR-0150 resolves standard-signal `command-token-vs-binary-input` as
  `do-not-replay-ordinary-binary-input-standard-signal`, leaving only
  `self-target-surface` unresolved for standard-signal command tokens.
- ADR-0151 resolves standard-signal `self-target-surface` through existing
  unsupported preservation boundaries, leaving no unresolved standard-signal
  source-status questions.
- ADR-0152 resolves write-buffer `recipient-surface` through the existing
  recipient non-init rejection boundary, replacing the old unresolved
  `recipient-vs-stem-surface` question with `self-target-surface`.
- ADR-0153 resolves write-buffer `self-target-surface` through the existing
  unsupported self-mailbox and self-target command-buffer boundaries, leaving
  only `buffer-full-boundary` and `post-append-clearing` unresolved for
  write-buffer command-token execution.
- ADR-0154 adds source-status `execution_readiness` gates. Project status now
  reports schema 15, source-status frontier reports schema 2, and write-buffer
  append execution is explicitly blocked by `buffer-full-boundary` and
  `post-append-clearing`.
- ADR-0155 tightens `execution_readiness`: when readiness is `blocked`,
  `blocked_by_resolution_questions` must cover every live unresolved
  `required_resolution_questions` ID. The JSON shapes stay at project status
  schema 15 and source-status schema 2.
- ADR-0156 adds the inverse execution-readiness guard: execution changes cannot
  be allowed while any unresolved `required_resolution_questions` remain. The
  JSON shapes stay at project status schema 15 and source-status schema 2.
- ADR-0157 makes execution readiness internally consistent: a record whose
  readiness decision is `blocked` cannot allow execution changes. The JSON
  shapes stay at project status schema 15 and source-status schema 2.
- ADR-0158 makes source-status question IDs unique within each unresolved and
  resolved question list. Duplicate live blockers or duplicate settled
  decisions now fail as `source-status-schema`, while project status remains
  schema 15 and source-status remains schema 2.
- ADR-0159 resolves write-buffer `buffer-full-boundary` as
  `preserve-existing-full-buffer-boundary-before-write-buffer-append`, based
  on the formal less-than-full write guard and RAA `buffer-full?` guard.
  Write-buffer execution remains blocked only by `post-append-clearing`; the
  JSON shapes stay at project status schema 15 and source-status schema 2.
- ADR-0160 resolves write-buffer `post-append-clearing` as
  `preserve-appended-buffer-clear-command-source`, selecting RAA/FSMSIM buffer
  preservation and recording SEMSIM's buffer-clearing wrapper as divergent
  legacy behavior. Write-buffer append execution is source-ready for a later
  implementation ADR; project status remains schema 15 and source-status
  remains schema 2.
- ADR-0161 implements direct self-mailbox and completed self-target
  command-buffer write-buffer append execution. The old unsupported
  self-mailbox and command-buffer boundaries now cover `standard-signal` only;
  write-buffer has explicit transition claims and proof certificates, project
  status reports 15 transition claims / 37 matched examples / 15 certificates,
  and recipient write-buffer command-message input remains rejected by the
  recipient non-init boundary.
- ADR-0162 registers direct self-mailbox and completed self-target
  command-buffer write-buffer append execution as integrated transition
  evidence bundles. Transition evidence now has ten bundles, and the
  write-buffer safe next slice is recipient write-buffer command-message source
  resolution rather than another self-target evidence artifact.
- ADR-0163 extends `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` with
  explicit upstream `write-buf-zero` and `write-buf-one` rejection examples,
  adds matching proof-certificate steps, and expands the recipient non-init
  evidence bundle's covered examples while leaving recipient write-buffer
  command-message execution blocked.
- ADR-0164 extends the transition-chain claim/proof surface with delivered
  neighbor-c `write-buf-zero` examples: negative for consumed-chain behavior
  and positive for rejected-chain behavior. Chain claim validation now
  evaluates nine examples without changing runtime, traces, SVGs, or evidence
  bundles.
- ADR-0165 adds standard-signal `execution_readiness` as
  `preserved-unsupported`: there are no live standard-signal resolution
  questions, but execution changes remain disallowed unless new source
  evidence replaces the existing unsupported self-target boundaries.
- ADR-0166 narrows the safe-next queue after ADR-0165: standard-signal points
  to new command-token source evidence before execution changes, while
  recipient non-init and multi-command status records point to recipient
  write-buffer command-message semantics.
- ADR-0167 makes `recipient-command-message-surface` a live write-buffer
  source-status question. Write-buffer readiness is now
  `self-target-implemented-recipient-blocked`: self-target append execution is
  implemented, but delivered recipient write-buffer command-message execution
  remains blocked pending that question.
- ADR-0168 resolves `recipient-command-message-surface` as
  `execute-recipient-write-buffer-command-message-append`. Write-buffer
  readiness became `recipient-command-message-source-ready`: recipient
  append behavior was source-resolved while current runtime still rejected
  delivered recipient write-buffer command messages.
- ADR-0169 implements recipient write-buffer command-message append execution.
  Single delivered `write-buf-zero` and `write-buf-one` tokens now append
  literal `0` and `1`, clear the active command source, preserve role/memory/
  output/command state, and keep the full-buffer boundary. The recipient
  non-init rejection claim now covers `standard-signal` and multi-command
  conflicts only; delivered write-buffer neighbor handoffs are consumed-chain
  examples, delivered `standard-signal` is the rejection-chain witness, and
  the blocked command frontier is `standard-signal` only.
- ADR-0170 registers the recipient write-buffer command-message evidence
  bundle. Transition evidence now has 11 bundles, write-buffer evidence-bundle
  status is implemented for direct self-mailbox, completed self-target, and
  recipient command-message surfaces, leaving standard-signal source review as
  the next frontier before ADR-0171.
- ADR-0171 records the 2026-05-18 standard-signal source-review snapshot.
  Upstream AS/AFS/PRC/SJAS/Proflog/LeanTAP heads matched the pinned manifest,
  PRC stayed at `7e82c73fac8f108faac801a5c65e2c2b92653ba5`, no new
  standard-signal command-token execution evidence was found, and the active
  aggregate safe-next now renders as none while `standard-signal` remains
  blocked behind a `no-` source-evidence guard.
