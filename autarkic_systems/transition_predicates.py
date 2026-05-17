"""Named predicates over Universal Cell transition results.

These checks are the first bridge from raw substrate updates toward formal
claims. They do not prove PRC correctness; they name and evaluate invariants
for the small transition probe in `universal_cell.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

from autarkic_systems.universal_cell import EMPTY, Cell, StepResult


AUTOMAIL_TARGETS = {
    "wr": ("wire", "right"),
    "wl": ("wire", "left"),
    "pr": ("proc", "right"),
    "pl": ("proc", "left"),
}
STEM_BUFFER_STATUSES = {
    "stem-control-selected",
    "stem-buffer-appended",
    "stem-buffer-full",
    "rejected-input",
}
SELF_MAILBOX_INIT_TARGETS = {
    "stem-init": ("stem", "right"),
    "wire-r-init": ("wire", "right"),
    "wire-l-init": ("wire", "left"),
    "proc-r-init": ("proc", "right"),
    "proc-l-init": ("proc", "left"),
}
SELF_MAILBOX_UNSUPPORTED_COMMANDS = {
    "standard-signal",
    "write-buf-zero",
    "write-buf-one",
}
COMMAND_BUFFER_WIDTH = 5


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


def automail_reconfigures_stem(before: Cell, result: StepResult) -> PredicateResult:
    """Check that stem automail commands produce the expected fixed role."""

    name = "automail_reconfigures_stem"
    if before.role != "stem" or before.automail == "_":
        return PredicateResult(name, True, "precondition not active")
    if result.status != "automail-reconfigured":
        return PredicateResult(
            name, False, f"expected automail-reconfigured, got {result.status}"
        )
    expected = AUTOMAIL_TARGETS.get(before.automail)
    if expected is None:
        return PredicateResult(name, False, f"unexpected automail {before.automail!r}")
    expected_role, expected_memory = expected
    if (result.cell.role, result.cell.memory) != expected:
        return PredicateResult(
            name,
            False,
            "expected "
            f"{expected_role}/{expected_memory}, got "
            f"{result.cell.role}/{result.cell.memory}",
        )
    if result.cell.automail != "_":
        return PredicateResult(name, False, "automail was not cleared")
    if result.cell.input != EMPTY or result.cell.output != EMPTY:
        return PredicateResult(name, False, "input or output was not cleared")
    return PredicateResult(name, True, "automail reconfigured stem as expected")


def stem_buffer_accumulates(before: Cell, result: StepResult) -> PredicateResult:
    """Check the standard-signal stem command-buffer accumulation subset."""

    name = "stem_buffer_accumulates"
    if before.role != "stem" or before.automail != "_":
        return PredicateResult(name, True, "precondition not active")
    if result.status not in STEM_BUFFER_STATUSES:
        return PredicateResult(name, True, f"precondition not active for {result.status}")

    if result.status == "rejected-input":
        if result.cell.input != EMPTY:
            return PredicateResult(name, False, "rejected stem input was not cleared")
        if result.cell.control != before.control or result.cell.buffer != before.buffer:
            return PredicateResult(
                name,
                False,
                "rejected stem input changed control or buffer",
            )
        return PredicateResult(name, True, "malformed stem input was rejected")

    if result.status == "stem-buffer-full":
        if result.cell != before:
            return PredicateResult(name, False, "full buffer boundary changed cell")
        return PredicateResult(name, True, "full buffer boundary preserved cell")

    if not _is_one_hot_standard_signal(before.input):
        return PredicateResult(name, False, "stem buffer transition lacked one-hot input")
    if result.cell.input != EMPTY:
        return PredicateResult(name, False, "stem buffer transition left input uncleared")

    if result.status == "stem-control-selected":
        if before.control:
            return PredicateResult(name, False, "control selection ran with control set")
        if result.cell.control != before.input:
            return PredicateResult(name, False, "control rail did not match input")
        if result.cell.buffer != before.buffer:
            return PredicateResult(name, False, "control selection changed buffer")
        return PredicateResult(name, True, "stem control rail selected")

    if result.status == "stem-buffer-appended":
        if not before.control:
            return PredicateResult(name, False, "buffer append ran without control rail")
        expected_bit = 1 if before.input == before.control else 0
        expected_buffer = before.buffer + (expected_bit,)
        if result.cell.control != before.control:
            return PredicateResult(name, False, "buffer append changed control rail")
        if result.cell.buffer != expected_buffer:
            return PredicateResult(
                name,
                False,
                f"expected buffer {expected_buffer}, got {result.cell.buffer}",
            )
        return PredicateResult(name, True, "stem buffer accumulated expected bit")

    return PredicateResult(name, False, f"unexpected stem buffer status {result.status}")


def self_mailbox_executes_init_command(
    before: Cell,
    result: StepResult,
) -> PredicateResult:
    """Check the source-stable self-mailbox init-command execution subset."""

    name = "self_mailbox_executes_init_command"
    expected = SELF_MAILBOX_INIT_TARGETS.get(before.self_mailbox)
    if (
        before.role != "stem"
        or before.automail != "_"
        or before.input != EMPTY
        or before.output != EMPTY
        or expected is None
    ):
        return PredicateResult(name, True, "precondition not active")

    if result.status != "self-mailbox-processed":
        return PredicateResult(
            name,
            False,
            f"expected self-mailbox-processed, got {result.status}",
        )

    expected_role, expected_memory = expected
    if (result.cell.role, result.cell.memory) != expected:
        return PredicateResult(
            name,
            False,
            "expected "
            f"{expected_role}/{expected_memory}, got "
            f"{result.cell.role}/{result.cell.memory}",
        )
    if result.cell.self_mailbox != "_":
        return PredicateResult(name, False, "self mailbox was not cleared")
    if result.cell.input != EMPTY or result.cell.output != EMPTY:
        return PredicateResult(name, False, "input or output was not cleared")
    if result.cell.automail != "_":
        return PredicateResult(name, False, "automail was not cleared")
    if result.cell.control or result.cell.buffer:
        return PredicateResult(name, False, "control or buffer was not cleared")
    return PredicateResult(name, True, "self mailbox init command executed")


def self_mailbox_preserves_unsupported_command(
    before: Cell,
    result: StepResult,
) -> PredicateResult:
    """Check that unresolved self-mailbox commands remain unexecuted."""

    name = "self_mailbox_preserves_unsupported_command"
    if (
        before.role != "stem"
        or before.automail != "_"
        or before.input != EMPTY
        or before.output != EMPTY
        or before.self_mailbox not in SELF_MAILBOX_UNSUPPORTED_COMMANDS
    ):
        return PredicateResult(name, True, "precondition not active")

    if result.status != "self-mailbox-unsupported":
        return PredicateResult(
            name,
            False,
            f"expected self-mailbox-unsupported, got {result.status}",
        )
    if result.cell != before:
        return PredicateResult(name, False, "unsupported command changed cell state")
    return PredicateResult(name, True, "unsupported self mailbox command preserved")


def stem_command_buffer_executes_self_init(
    before: Cell,
    result: StepResult,
) -> PredicateResult:
    """Check the narrow completed-buffer self init dispatch slice."""

    name = "stem_command_buffer_executes_self_init"
    expected = _completed_self_init_target(before)
    if expected is None:
        return PredicateResult(name, True, "precondition not active")

    if result.status != "stem-command-buffer-self-processed":
        return PredicateResult(
            name,
            False,
            f"expected stem-command-buffer-self-processed, got {result.status}",
        )

    expected_role, expected_memory = expected
    if (result.cell.role, result.cell.memory) != expected:
        return PredicateResult(
            name,
            False,
            "expected "
            f"{expected_role}/{expected_memory}, got "
            f"{result.cell.role}/{result.cell.memory}",
        )
    if result.cell.input != EMPTY or result.cell.output != EMPTY:
        return PredicateResult(name, False, "input or output was not cleared")
    if result.cell.automail != "_" or result.cell.self_mailbox != "_":
        return PredicateResult(name, False, "automail or self mailbox was not cleared")
    if result.cell.control or result.cell.buffer:
        return PredicateResult(name, False, "control or buffer was not cleared")
    return PredicateResult(name, True, "self-target init command buffer executed")


def stem_command_buffer_preserves_unsupported_completion(
    before: Cell,
    result: StepResult,
) -> PredicateResult:
    """Check the unsupported completed-buffer append boundary."""

    name = "stem_command_buffer_preserves_unsupported_completion"
    decoded = _completed_command_buffer(before)
    if decoded is None:
        return PredicateResult(name, True, "precondition not active")

    target_id, command_id, completed_buffer = decoded
    if target_id != "self":
        return PredicateResult(
            name,
            True,
            "precondition not active: neighbor delivery",
        )
    if target_id == "self" and command_id in SELF_MAILBOX_INIT_TARGETS:
        return PredicateResult(
            name,
            True,
            "precondition not active: supported self init",
        )

    if result.status != "stem-buffer-appended":
        return PredicateResult(
            name,
            False,
            f"expected stem-buffer-appended, got {result.status}",
        )
    if result.cell.role != before.role or result.cell.memory != before.memory:
        return PredicateResult(
            name,
            False,
            "unsupported completion changed role or memory",
        )
    if result.cell.upstream != before.upstream:
        return PredicateResult(name, False, "unsupported completion changed upstream")
    if result.cell.input != EMPTY:
        return PredicateResult(
            name,
            False,
            "unsupported completion left input uncleared",
        )
    if result.cell.output != EMPTY:
        return PredicateResult(name, False, "unsupported completion changed output")
    if result.cell.automail != "_" or result.cell.self_mailbox != "_":
        return PredicateResult(
            name,
            False,
            "unsupported completion changed command mail",
        )
    if result.cell.control != before.control:
        return PredicateResult(
            name,
            False,
            "unsupported completion changed control rail",
        )
    if result.cell.buffer != completed_buffer:
        return PredicateResult(
            name,
            False,
            f"expected buffer {completed_buffer}, got {result.cell.buffer}",
        )
    return PredicateResult(
        name,
        True,
        f"unsupported {target_id}/{command_id} completion stayed at append boundary",
    )


def _completed_self_init_target(before: Cell) -> tuple[str, str] | None:
    decoded = _completed_command_buffer(before)
    if decoded is None:
        return None

    target_id, command_id, _completed_buffer = decoded
    if target_id != "self":
        return None
    return SELF_MAILBOX_INIT_TARGETS.get(command_id)


def _completed_command_buffer(
    before: Cell,
) -> tuple[str, str, tuple[object, ...]] | None:
    if (
        before.role != "stem"
        or before.automail != "_"
        or before.self_mailbox != "_"
        or before.output != EMPTY
        or before.input == EMPTY
        or not before.control
        or len(before.buffer) != COMMAND_BUFFER_WIDTH - 1
        or not _is_one_hot_standard_signal(before.input)
        or not _is_one_hot_standard_signal(before.control)
    ):
        return None

    completed_buffer = before.buffer + (
        1 if before.input == before.control else 0,
    )
    if any(bit not in (0, 1) for bit in completed_buffer):
        return None

    value = 0
    for bit in completed_buffer:
        value = (value << 1) | bit
    target_id = (
        "self" if value <= 7
        else "neighbor-a" if value <= 15
        else "neighbor-b" if value <= 23
        else "neighbor-c"
    )
    command_id = (
        "standard-signal",
        "stem-init",
        "wire-r-init",
        "wire-l-init",
        "proc-r-init",
        "proc-l-init",
        "write-buf-zero",
        "write-buf-one",
    )[value % 8]
    return target_id, command_id, completed_buffer


def _is_one_hot_standard_signal(signal: tuple[object, object, object]) -> bool:
    """A stem command-buffer signal has one high binary channel."""

    return all(value in (0, 1) for value in signal) and sum(signal) == 1
