# Development Log

## 2026-05-16 - Initial Orientation Scaffold

- Cloned `https://github.com/jpt4/as` at commit
  `1a2fc06b75f5d33aee6655956c2a56df07a7bfb0`. The repository initially
  contained only `AGENTS.md` and `AGENTS.md~`.
- Reviewed the project prelude in `AGENTS.md`: Autarkic Systems is an
  open-ended cross-disciplinary investigation that subsumes AFS, PRC, and
  SJAS, with a lower-bound objective of theory plus machinic implementation of
  an artificial entity demonstrating cognitive sovereignty.
- Fetched the three referenced subordinate repositories for review:
  - `jpt4/afs` at `a61592eab02a93d480149ce3465af5e3271ca213`.
  - `jpt4/prc` at `7e82c73fac8f108faac801a5c65e2c2b92653ba5`.
  - `jpt4/sjas` at `f1c11af5f310d39f487c3b91ee1ca70f4ade8871`.
- Checked GitHub metadata and issues. `jpt4/as`, `jpt4/afs`, and `jpt4/sjas`
  had no listed issues; `jpt4/prc` had one closed typo issue.
- Attempted to retrieve the referenced X/Twitter status
  `https://x.com/jpt401/status/1556420237163118598`. The web fetch exposed no
  usable text, and web search did not surface a reliable mirror. Treat that
  reference as uncaptured until a better source is available.
- Added the first ADR-backed documentation scaffold so future work has a
  current public entrypoint, chronological log, durable context, subordinate
  review, and initial roadmap.

## 2026-05-16 - AFS Requirement Definition

- Re-read the live project `AGENTS.md` before continuing work. The active rules
  require ADRs before feature implementation, careful documentation layering,
  active forward motion, and structured tools where useful.
- Listed public repositories under `jpt4` and identified `jpt4/proflog` as a
  relevant adjacent executable frontier because SJAS `nachlass/LOG.md` records
  recent Proflog-side SJAS work.
- Cloned `jpt4/proflog` at `77af848`. The public main branch contains
  `proflog.scm` and `LPTableaus.pdf`, but not the ADR-0063 through ADR-0068
  material described in the SJAS log.
- Ran `guile proflog.scm`; it failed at the embedded `P1` program definition
  with `Unbound variable: even`. Treat public Proflog main as relevant
  background, not as a passing executable dependency.
- Added `docs/glossary.md`, `docs/afs-requirements.md`, and
  `docs/adr/0002-afs-requirements.md` to turn AFS from a placeholder name into
  a concrete requirement matrix with a gap register and a recommended first
  executable probe.

## 2026-05-16 - Source Manifest

- Added `sources/manifest.json` to pin the reviewed source baseline for AS,
  AFS, PRC, SJAS, and adjacent Proflog.
- Added `docs/source-manifest.md` and `docs/adr/0003-source-manifest.md` to
  explain the manifest, verification commands, and status of each source.
- Verified that `jq` is available for structural manifest checks.

## 2026-05-16 - Universal Cell Transition Probe

- Added ADR-0004 for the first code-bearing AS artifact: a tiny fixed-role
  Universal Cell transition probe.
- Wrote `tests/test_universal_cell.py` before implementation. The first run of
  `python -m unittest tests.test_universal_cell` failed with
  `ModuleNotFoundError: No module named 'autarkic_systems'`, confirming the red
  step.
- Implemented `autarkic_systems/universal_cell.py` with immutable `Cell` and
  `StepResult` records plus `step_fixed_cell`.
- Covered wire right-rotation, processor left-rotation and memory toggle,
  blocked output, upstream pull, stem-init reconfiguration, malformed input
  clearing, invalid role rejection, and invalid memory rejection.
- Added `tests/__init__.py` so the default fast command
  `python -m unittest discover` actually discovers the suite.
- Verified `python -m unittest discover`, `python -m py_compile
  autarkic_systems/universal_cell.py autarkic_systems/__init__.py
  tests/__init__.py tests/test_universal_cell.py`, and `git diff --check`.

## 2026-05-16 - Transition Predicate Bridge

- Added ADR-0005 for named predicates over Universal Cell transition results.
- Wrote `tests/test_transition_predicates.py` before implementation. The first
  targeted run failed with `ModuleNotFoundError: No module named
  'autarkic_systems.transition_predicates'`, confirming the red step.
- Implemented `autarkic_systems/transition_predicates.py` with
  `PredicateResult`, `output_not_overwritten`, `consumed_input_cleared`,
  `fixed_role_memory_rule`, and `stem_init_resets_to_stem`.
- Verified `python -m unittest tests.test_transition_predicates` passed 8
  tests, `python -m unittest discover` passed 16 tests, and `git diff --check`
  passed.

## 2026-05-17 - Literature Map And Open Problems

- Added `docs/adr/0006-literature-map.md` for the first literature/open-problem
  mapping slice.
- Added `docs/literature-map.md`, organizing AS, AFS, PRC, SJAS, and adjacent
  Proflog/Fitting sources by their role in the AS project.
- Added `docs/open-problems.md`, ranking the next project questions from
  transition-claim formalization through hardware/schematic evidence.
- Corrected the roadmap's duplicate ADR-0005 heading by making the literature
  map ADR-0006.

## 2026-05-17 - Transition Claim Manifest

- Added ADR-0007 for a machine-readable bridge from transition predicate code
  to explicit AS claims.
- Wrote `tests/test_claim_manifest.py` before implementation. The first run
  failed with `ModuleNotFoundError: No module named
  'autarkic_systems.claim_manifest'`, confirming the red step.
- Added `claims/transition_claims.json` with four transition claims, each with
  positive and negative executable examples.
- Added `autarkic_systems/claim_manifest.py` to load and evaluate the manifest
  against implemented predicate functions.
- Verified `python -m unittest tests.test_claim_manifest` passed 4 tests,
  `python -m unittest discover` passed 20 tests, `jq -e
  claims/transition_claims.json` passed, and `git diff --check` passed.

## 2026-05-17 - Stem Automail Probe

- Added ADR-0008 for the first tested stem/reconfiguration slice.
- Wrote `tests/test_stem_automail.py` before implementation. The first run
  failed because `step_stem_cell` did not exist, confirming the red step.
- Extended `Cell` with stem-state fields for `automail`, `control`, and
  `buffer`.
- Added `step_stem_cell` for the automail subset: `wr`, `wl`, `pr`, and `pl`
  reconfigure a stem cell into the corresponding fixed role and memory.
- Verified `python -m unittest tests.test_stem_automail` passed 8 tests,
  `python -m unittest discover` passed 28 tests, and `git diff --check`
  passed.

## 2026-05-17 - Stem Automail Claim

- Added ADR-0009 to promote stem automail behavior into the named AS claim
  surface.
- Wrote predicate tests before implementation. The first run failed because
  `automail_reconfigures_stem` did not exist, confirming the red step.
- Implemented `automail_reconfigures_stem` and added the
  `UC-STEM-AUTOMAIL-RECONFIGURES` claim to `claims/transition_claims.json`.
- The claim manifest evaluator initially caught a mismatch because
  `claim_manifest.py` was not preserving stem fields such as `automail` when
  parsing cells. Fixed the loader to parse automail, control, and buffer.
- Verified `python -m unittest tests.test_transition_predicates` passed 10
  tests, `python -m unittest tests.test_claim_manifest` passed 4 tests,
  `python -m unittest discover` passed 30 tests, JSON checks passed, and
  `git diff --check` passed.

## 2026-05-17 - Proof Apparatus Options

- Re-read `/home/sean/Projects/AGENTS.md`, the AS `AGENTS.md`, and the active
  thread goal before continuing. The project remains an open end-of-month AS
  work goal, and the live branch is `adr-0010-proof-apparatus-options`.
- Cloned and reviewed `namin/leanTAP` at
  `c17864a911c0c3cbd727b43743fdcb19b43714b8` because SJAS ISLA notes point to
  alphaLeanTAP as a possible tableaux direction.
- Reviewed the visible public Proflog source and the SJAS `nachlass/LOG.md`
  Proflog boundary notes again. Public Proflog remains relevant background, but
  it still does not expose the active ADR-006x frontier described by SJAS.
- Added ADR-0010 and `docs/proof-apparatus-options.md`. The decision is to
  start with a minimal AS-local proof-certificate checker for the current
  transition claims, use LeanTAP as a transparent design reference, and defer
  Proflog as a dependency until its active frontier is recovered or replaced.

## 2026-05-17 - Proof Certificate Checker

- Added ADR-0011 for the first proof-object layer over current transition
  claims.
- Wrote `tests/test_proof_certificates.py` before implementation. The red run
  failed because `autarkic_systems.proof_certificates` did not exist.
- Added `claims/proof_certificates.json` with one certificate per current
  transition claim. The first rule is `manifest-example`, tying proof steps to
  named claim examples and their expected predicate outcomes.
- Added `autarkic_systems/proof_certificates.py` to load certificates and
  reject missing claim certificates, unknown claims, unknown rules, missing
  examples, duplicate examples, and mismatched expectations.
- Verified `python -m unittest tests.test_proof_certificates` passed 6 tests,
  `python -m unittest discover` passed 36 tests, py_compile passed for the new
  module and tests, JSON checks passed, and `git diff --check` passed.

## 2026-05-17 - Transition Claim Object Language

- Added ADR-0012 for the first explicit AS object language.
- Wrote `tests/test_object_language.py` before implementation. The red run
  failed because `autarkic_systems.object_language` did not exist.
- Added `language/transition_claim_language.json` with explicit syntax classes
  for terms, formulae, sentences, proof objects, and substrate claims.
- Added `autarkic_systems/object_language.py` to validate the language manifest
  and the current transition-claim/proof-certificate surface.
- Added `docs/transition-claim-language.md` as the human-facing note for the
  language boundary.
- Verified `python -m unittest tests.test_object_language` passed 6 tests,
  `python -m unittest discover` passed 42 tests, py_compile passed for the new
  module and tests, JSON checks passed, and `git diff --check` passed.
