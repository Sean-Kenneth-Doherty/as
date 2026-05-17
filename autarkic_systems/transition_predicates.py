"""Named predicates over Universal Cell transition results.

These checks are the first bridge from raw substrate updates toward formal
claims. They do not prove PRC correctness; they name and evaluate invariants
for the small transition probe in `universal_cell.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

from autarkic_systems.universal_cell import EMPTY, Cell, StepResult


@dataclass(frozen=True)
class PredicateResult:
    """A named claim result that can later be attached to proof artifacts."""

    name: str
    holds: bool
    detail: str


def output_not_overwritten(before: Cell, result: StepResult) -> PredicateResult:
    """Check the blocked-output invariant.

    When a cell begins with occupied output, the transition probe should report
    blocked output and preserve the output channels exactly.
    """

    name = "output_not_overwritten"
    if before.output == EMPTY:
        return PredicateResult(name, True, "precondition not active: output was empty")
    if result.status != "blocked-output":
        return PredicateResult(name, False, f"expected blocked-output, got {result.status}")
    if result.cell.output != before.output:
        return PredicateResult(name, False, "blocked output changed during transition")
    return PredicateResult(name, True, "occupied output was preserved")


def consumed_input_cleared(before: Cell, result: StepResult) -> PredicateResult:
    """Check that terminal processing clears consumed input.

    Routed, rejected, and stem-init transitions consume the active input. Idle
    and blocked transitions do not have the same obligation.
    """

    name = "consumed_input_cleared"
    if result.status not in {"routed", "rejected-input", "stem-init"}:
        return PredicateResult(name, True, f"precondition not active for {result.status}")
    if result.cell.input != EMPTY:
        return PredicateResult(name, False, "terminal transition left input uncleared")
    if before.input == EMPTY and before.upstream == EMPTY:
        return PredicateResult(name, False, "terminal transition had no visible input source")
    return PredicateResult(name, True, "terminal transition cleared consumed input")


def fixed_role_memory_rule(before: Cell, result: StepResult) -> PredicateResult:
    """Check the fixed-role memory rule for routed transitions."""

    name = "fixed_role_memory_rule"
    if result.status != "routed":
        return PredicateResult(name, True, f"precondition not active for {result.status}")
    if before.role == "wire" and result.cell.memory != before.memory:
        return PredicateResult(name, False, "wire routing changed memory")
    if before.role == "proc" and result.cell.memory == before.memory:
        return PredicateResult(name, False, "processor routing did not toggle memory")
    if before.role not in {"wire", "proc"}:
        return PredicateResult(name, False, f"unexpected fixed role {before.role!r}")
    return PredicateResult(name, True, "fixed-role memory rule held")


def stem_init_resets_to_stem(before: Cell, result: StepResult) -> PredicateResult:
    """Check that stem-init returns a fixed cell to the canonical stem state."""

    name = "stem_init_resets_to_stem"
    if result.status != "stem-init":
        return PredicateResult(name, True, f"precondition not active for {result.status}")
    if result.cell.role != "stem":
        return PredicateResult(name, False, "stem-init did not set role to stem")
    if result.cell.memory != "right":
        return PredicateResult(name, False, "stem-init did not reset memory to right")
    if result.cell.input != EMPTY or result.cell.output != EMPTY:
        return PredicateResult(name, False, "stem-init left input or output non-empty")
    if before.role not in {"wire", "proc"}:
        return PredicateResult(name, False, f"unexpected source role {before.role!r}")
    return PredicateResult(name, True, "stem-init reset fixed cell to stem")
