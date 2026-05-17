# Proflog Frontier Status

Status: public-main source-status decision, 2026-05-17.

## Decision

Do not depend on public `jpt4/proflog` `main` as an AS implementation
dependency.

Public Proflog remains relevant background for Fitting-style semantic tableaux,
but it is not the active SJAS/Proflog frontier described in SJAS logs and it
does not run under Guile in this environment.

The structured status lives in `sources/proflog_frontier_status.json`.

## Evidence

Remote branch check:

```sh
git ls-remote https://github.com/jpt4/proflog.git HEAD refs/heads/*
```

Observed result:

- `HEAD` and `refs/heads/main` both point to
  `77af8481d9f41a439eb42e1d8268a5b39f7c5c33`;
- no public ADR or alternate branch refs were visible.

Public checkout payload:

- `proflog.scm`;
- `LPTableaus.pdf`.

SJAS log frontier:

- `ADR-0063` through `ADR-0068`;
- `tableau-proof/3`;
- `subst-prf/4`;
- `subst-code/2`;
- `SelfCons1`;
- `IS#_D(beta)`;
- structural code decoding for `wff/1`, `neg-pair/2`, and
  `delta-star-0-code`;
- a promoted `lt(1,2)` proof-code example.

Public-main smoke result:

```sh
cd /home/sean/Projects/_upstream/proflog
guile proflog.scm
```

Observed result:

- failed at `proflog.scm:893:5`;
- failure: `Unbound variable: even`.

## AS Interpretation

The active SJAS log describes a much more advanced Proflog surface than public
`main` exposes. It includes code-level formula parsing, proof-code targets,
substitution-proof vocabulary, and finite generated `IS#_D(beta)` support. None
of those terms are present in public Proflog main.

Therefore AS should preserve three separate claims:

- Public Proflog is relevant to the long-term proof-apparatus direction.
- Public Proflog main is not dependency-ready executable evidence.
- The active Proflog ADR-006x source must be recovered, published, or replaced
  before AS builds on it.

## Maintainer Question

Where does the Proflog ADR-0063 through ADR-0068 implementation described by
`sjas/nachlass/LOG.md` live?

If it is available, AS should pin that source and reassess the proof-apparatus
roadmap. If it is not available, AS should continue with local proof
certificates and Willard anchor work until a replacement tableaux/code-level
apparatus is chosen.

This question was filed upstream as `jpt4/proflog#1`.

## Verification

Run:

```sh
python -m unittest tests.test_proflog_frontier_status
```

The test validates the recorded public head, decision, missing frontier terms,
pinned source paths, and Guile smoke-test failure.
