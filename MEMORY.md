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
- `step_stem_cell` in `autarkic_systems/universal_cell.py` covers only the
  stem automail reconfiguration subset (`wr`, `wl`, `pr`, `pl`), not full stem
  buffer processing.
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
