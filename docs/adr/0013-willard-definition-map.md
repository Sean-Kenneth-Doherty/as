# ADR-0013: Willard Definition Map

Date: 2026-05-17

Status: Accepted

## Context

P5 asks which definitions and theorem statements from Willard 2001, 2011,
2016, and 2020 are actually needed for AS's first formal-confidence claim.
The current AS repository has transition claims, proof certificates, and a
transition-claim object language, but these are still far below an SJAS-level
self-consistency result.

The next useful move is not another broad literature summary. AS needs a
definition-granularity map that names the exact Willard loci future ADRs must
preserve before claiming self-justification, proof-code self-reference,
tangibility, or a specific proof apparatus.

## Decision

Add a structured Willard definition map with executable validation:

- `sources/willard_definition_map.json` records the required source anchors;
- `autarkic_systems/willard_map.py` loads and validates the map;
- `tests/test_willard_definition_map.py` checks the four core Willard sources,
  local PDF witnesses, unique anchor loci, and AS relevance links;
- `docs/willard-definition-map.md` explains the map and how it constrains later
  AS work.

The first map covers:

- Willard 2001: Prenex* syntax, tangibility, IS(A), and IS(.) consistency
  preservation;
- Willard 2011: generic configurations, Level(k) consistency, SelfCons_k, and
  EA-stable self-justification;
- Willard 2016: Hilbert-style deduction, self-justifying configurations,
  theta-style indeterminacy, and IQFS consistency preservation;
- Willard 2020: GenAC self-justification, Type-NS/S/A/M classification,
  tableau variants, and the excluded-middle boundary.

## Success Criteria

- Red tests fail before implementation because the Willard map module or source
  manifest is absent.
- The map contains anchors for Willard 2001, 2011, 2016, and 2020.
- Each required source has at least one definition and at least one theorem or
  construction anchor.
- Every anchor pins a local SJAS witness path under
  `/home/sean/Projects/_upstream/sjas`; live source checkout existence was
  verified during the ADR run but is not required by the default fast suite.
- Anchor IDs and source loci are unique.
- Every anchor names AS requirements or open-problem IDs that it constrains.

## Consequences

- AS can now talk about Willard sources with specific anchor IDs instead of
  broad repository-level gestures.
- Future proof-apparatus ADRs have a concrete checklist: language, formula
  class, axiom basis, deduction method, proof-code encoding, and consistency
  level.
- The map is still a research index. It does not prove the Willard theorems,
  formalize their definitions, or implement IS(A), SelfCons_k, IQFS, or
  tableaux deduction.

## After Action Report

Red step:

- `python -m unittest tests.test_willard_definition_map` failed with
  `ModuleNotFoundError: No module named 'autarkic_systems.willard_map'`.

Green step:

- Added `autarkic_systems/willard_map.py`.
- Added `sources/willard_definition_map.json`.
- Added `docs/willard-definition-map.md`.
- `python -m unittest tests.test_willard_definition_map` passed 4 tests.
- `python -m unittest discover` passed 46 tests.
- `python -m py_compile autarkic_systems/willard_map.py
  tests/test_willard_definition_map.py` passed.
- `jq -e . sources/willard_definition_map.json` passed.
- `git diff --check` passed.

Coverage limits:

- The map relies on local PDF text extraction and source-locus labels; it is not
  a formal mechanization of the papers.
- Default fast tests validate pinned witness paths, not the availability of the
  disposable `_upstream` source cache.
- It anchors only the first core Willard set named by P5: 2001, 2011, 2016,
  and 2020.
- Willard 1993, 1997, 2005, 2014, secondary literature, and Proflog ADR-006x
  implementation details remain outside this slice.
