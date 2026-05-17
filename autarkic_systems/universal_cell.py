"""Minimal Universal Cell transition probe.

This module is intentionally much smaller than PRC's full Universal Cell
simulator. It captures only the fixed-role behavior needed for AS's first
executable substrate contract: wire/proc routing, output blocking, upstream
pulling, malformed input rejection, and stem-init reconfiguration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Signal = Literal[0, 1, "_", "si"]
Role = Literal["wire", "proc", "stem"]
Memory = Literal["right", "left"]
Automail = Literal["_", "wr", "wl", "pr", "pl"]
Status = Literal[
    "idle",
    "automail-reconfigured",
    "blocked-output",
    "rejected-input",
    "routed",
    "stem-init",
    "stem-buffer-appended",
    "stem-buffer-full",
    "stem-control-selected",
]

EMPTY: tuple[Signal, Signal, Signal] = ("_", "_", "_")
VALID_ROLES = {"wire", "proc", "stem"}
FIXED_ROLES = {"wire", "proc"}
VALID_MEMORY = {"right", "left"}
VALID_AUTOMAIL = {"_", "wr", "wl", "pr", "pl"}
MAX_STEM_BUFFER_SIZE = 5
AUTOMAIL_RECONFIGURATION: dict[Automail, tuple[Role, Memory]] = {
    "wr": ("wire", "right"),
    "wl": ("wire", "left"),
    "pr": ("proc", "right"),
    "pl": ("proc", "left"),
}


@dataclass(frozen=True)
class Cell:
    """A compact Universal Cell state for the first AS transition probe.

    The PRC notes model more fields than this class exposes. This probe keeps
    only the fixed-role fields needed for a high-level activation step.
    """

    role: Role
    memory: Memory
    upstream: tuple[Signal, Signal, Signal] = EMPTY
    input: tuple[Signal, Signal, Signal] = EMPTY
    output: tuple[Signal, Signal, Signal] = EMPTY
    automail: Automail = "_"
    control: tuple[Signal, ...] = ()
    buffer: tuple[Signal, ...] = ()

    def __post_init__(self) -> None:
        _validate_role(self.role)
        _validate_memory(self.memory)
        _validate_channels("upstream", self.upstream)
        _validate_channels("input", self.input)
        _validate_channels("output", self.output)
        _validate_automail(self.automail)
        _validate_signal_tuple("control", self.control)
        _validate_signal_tuple("buffer", self.buffer)


@dataclass(frozen=True)
class StepResult:
    """Result of one high-level fixed-cell activation."""

    status: Status
    cell: Cell


def step_fixed_cell(cell: Cell) -> StepResult:
    """Perform one fixed-role Universal Cell activation.

    This function intentionally rejects `stem` cells. Stem behavior is the
    reconfiguration machinery, while this first probe checks the simpler fixed
    wire/proc transition surface.
    """

    if cell.role not in FIXED_ROLES:
        raise ValueError(f"fixed transition requires wire/proc role, got {cell.role!r}")

    if _non_empty(cell.output):
        return StepResult("blocked-output", cell)

    active = cell
    if _empty(active.input):
        active = _pull_upstream(active)
        if _empty(active.input):
            return StepResult("idle", active)

    if _is_stem_init(active.input):
        return StepResult("stem-init", _to_stem(active))

    if not _is_standard_signal(active.input):
        return StepResult("rejected-input", _replace(active, input=EMPTY))

    routed = _route(active.input, active.memory)
    next_memory = _toggle(active.memory) if active.role == "proc" else active.memory
    return StepResult(
        "routed",
        _replace(active, input=EMPTY, output=routed, memory=next_memory),
    )


def step_stem_cell(cell: Cell) -> StepResult:
    """Perform one high-level stem activation for the first stem subsets.

    Full PRC stem behavior includes command decoding, target routing, and
    buffer execution. This probe covers explicit automail reconfiguration plus
    the first standard-signal buffer accumulation rule.
    """

    if cell.role != "stem":
        raise ValueError(f"stem transition requires stem role, got {cell.role!r}")

    if _non_empty(cell.output):
        return StepResult("blocked-output", cell)

    if cell.automail == "_":
        if _empty(cell.input):
            return StepResult("idle", cell)

        if not _is_one_hot_standard_signal(cell.input):
            return StepResult("rejected-input", _replace(cell, input=EMPTY))

        if not cell.control:
            return StepResult(
                "stem-control-selected",
                _replace(cell, input=EMPTY, control=cell.input),
            )

        if len(cell.buffer) >= MAX_STEM_BUFFER_SIZE:
            return StepResult("stem-buffer-full", cell)

        bit = 1 if cell.input == cell.control else 0
        return StepResult(
            "stem-buffer-appended",
            _replace(cell, input=EMPTY, buffer=cell.buffer + (bit,)),
        )

    role, memory = AUTOMAIL_RECONFIGURATION[cell.automail]
    return StepResult(
        "automail-reconfigured",
        _replace(
            cell,
            role=role,
            memory=memory,
            input=EMPTY,
            output=EMPTY,
            automail="_",
            control=(),
            buffer=(),
        ),
    )


def _pull_upstream(cell: Cell) -> Cell:
    """Move upstream neighbor output into input, matching PRC pull semantics."""

    if _empty(cell.upstream):
        return cell
    return _replace(cell, upstream=EMPTY, input=cell.upstream)


def _to_stem(cell: Cell) -> Cell:
    """Reset a fixed cell to the stem role after a stem-init signal."""

    return _replace(cell, role="stem", memory="right", input=EMPTY, output=EMPTY)


def _route(
    signal: tuple[Signal, Signal, Signal], memory: Memory
) -> tuple[Signal, Signal, Signal]:
    """Rotate a standard signal through right or left cell memory."""

    a, b, c = signal
    if memory == "right":
        return (c, a, b)
    return (b, c, a)


def _toggle(memory: Memory) -> Memory:
    """Processor cells flip their memory after routing a standard signal."""

    return "left" if memory == "right" else "right"


def _is_standard_signal(signal: tuple[Signal, Signal, Signal]) -> bool:
    """A standard fixed-role signal has exactly three binary channels."""

    return all(value in (0, 1) for value in signal)


def _is_stem_init(signal: tuple[Signal, Signal, Signal]) -> bool:
    """Stem-init is a single special token embedded in otherwise empty input."""

    return signal.count("si") == 1 and signal.count("_") == 2


def _is_one_hot_standard_signal(signal: tuple[Signal, Signal, Signal]) -> bool:
    """A stem command-buffer signal has one high binary channel."""

    return all(value in (0, 1) for value in signal) and sum(signal) == 1


def _empty(signal: tuple[Signal, Signal, Signal]) -> bool:
    return signal == EMPTY


def _non_empty(signal: tuple[Signal, Signal, Signal]) -> bool:
    return signal != EMPTY


def _replace(cell: Cell, **changes: object) -> Cell:
    """Return a validated updated cell while preserving immutable state."""

    data = {
        "role": cell.role,
        "memory": cell.memory,
        "upstream": cell.upstream,
        "input": cell.input,
        "output": cell.output,
        "automail": cell.automail,
        "control": cell.control,
        "buffer": cell.buffer,
    }
    data.update(changes)
    return Cell(**data)  # type: ignore[arg-type]


def _validate_role(role: str) -> None:
    if role not in VALID_ROLES:
        raise ValueError(f"unknown Universal Cell role: {role!r}")


def _validate_memory(memory: str) -> None:
    if memory not in VALID_MEMORY:
        raise ValueError(f"unknown Universal Cell memory: {memory!r}")


def _validate_automail(automail: str) -> None:
    if automail not in VALID_AUTOMAIL:
        raise ValueError(f"unknown Universal Cell automail: {automail!r}")


def _validate_channels(name: str, value: tuple[Signal, ...]) -> None:
    if len(value) != 3:
        raise ValueError(f"{name} must contain exactly three channels")
    _validate_signal_tuple(name, value)


def _validate_signal_tuple(name: str, value: tuple[Signal, ...]) -> None:
    for channel in value:
        if channel not in (0, 1, "_", "si"):
            raise ValueError(f"{name} contains invalid channel value {channel!r}")
