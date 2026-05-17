"""Minimal Universal Cell transition probe.

This module is intentionally much smaller than PRC's full Universal Cell
simulator. It captures only the fixed-role and early stem behavior needed for
AS's first executable substrate contracts: wire/proc routing, output blocking,
upstream pulling, malformed input rejection, stem-init reconfiguration, and
bounded stem command-buffer slices.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from autarkic_systems.stem_command_map import EXPECTED_COMMANDS, EXPECTED_TARGET_RANGES


Signal = Literal[
    0,
    1,
    "_",
    "si",
    "standard-signal",
    "stem-init",
    "wire-r-init",
    "wire-l-init",
    "proc-r-init",
    "proc-l-init",
    "write-buf-zero",
    "write-buf-one",
]
Role = Literal["wire", "proc", "stem"]
Memory = Literal["right", "left"]
Automail = Literal["_", "wr", "wl", "pr", "pl"]
CommandMessage = Literal[
    "_",
    "standard-signal",
    "stem-init",
    "wire-r-init",
    "wire-l-init",
    "proc-r-init",
    "proc-l-init",
    "write-buf-zero",
    "write-buf-one",
]
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
    "stem-command-buffer-neighbor-delivered",
    "stem-command-buffer-self-processed",
    "self-mailbox-processed",
    "self-mailbox-unsupported",
]

EMPTY: tuple[Signal, Signal, Signal] = ("_", "_", "_")
VALID_ROLES = {"wire", "proc", "stem"}
FIXED_ROLES = {"wire", "proc"}
VALID_MEMORY = {"right", "left"}
VALID_AUTOMAIL = {"_", "wr", "wl", "pr", "pl"}
VALID_CHANNEL_TOKENS = {
    0,
    1,
    "_",
    "si",
    "standard-signal",
    "stem-init",
    "wire-r-init",
    "wire-l-init",
    "proc-r-init",
    "proc-l-init",
    "write-buf-zero",
    "write-buf-one",
}
VALID_SELF_MAILBOX = {
    "_",
    "standard-signal",
    "stem-init",
    "wire-r-init",
    "wire-l-init",
    "proc-r-init",
    "proc-l-init",
    "write-buf-zero",
    "write-buf-one",
}
MAX_STEM_BUFFER_SIZE = 5
AUTOMAIL_RECONFIGURATION: dict[Automail, tuple[Role, Memory]] = {
    "wr": ("wire", "right"),
    "wl": ("wire", "left"),
    "pr": ("proc", "right"),
    "pl": ("proc", "left"),
}
SELF_MAILBOX_INIT_TARGETS: dict[CommandMessage, tuple[Role, Memory]] = {
    "stem-init": ("stem", "right"),
    "wire-r-init": ("wire", "right"),
    "wire-l-init": ("wire", "left"),
    "proc-r-init": ("proc", "right"),
    "proc-l-init": ("proc", "left"),
}
NEIGHBOR_OUTPUT_INDEX = {
    "neighbor-a": 0,
    "neighbor-b": 1,
    "neighbor-c": 2,
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
    self_mailbox: CommandMessage = "_"
    control: tuple[Signal, ...] = ()
    buffer: tuple[Signal, ...] = ()

    def __post_init__(self) -> None:
        _validate_role(self.role)
        _validate_memory(self.memory)
        _validate_channels("upstream", self.upstream)
        _validate_channels("input", self.input)
        _validate_channels("output", self.output)
        _validate_automail(self.automail)
        _validate_self_mailbox(self.self_mailbox)
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

    Full PRC stem behavior includes complete command decoding, target routing,
    and buffer execution. This probe covers explicit automail reconfiguration,
    standard-signal buffer accumulation, direct self-mailbox handling, and the
    narrow self-target init command-buffer dispatch slice, and neighbor-target
    command-buffer delivery onto output channels.
    """

    if cell.role != "stem":
        raise ValueError(f"stem transition requires stem role, got {cell.role!r}")

    if _non_empty(cell.output):
        return StepResult("blocked-output", cell)

    if cell.automail == "_":
        if _empty(cell.input) and cell.self_mailbox != "_":
            return _process_self_mailbox(cell)

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
        next_buffer = cell.buffer + (bit,)
        completed = _process_completed_command_buffer(
            _replace(cell, input=EMPTY, buffer=next_buffer),
        )
        if completed is not None:
            return completed
        return StepResult(
            "stem-buffer-appended",
            _replace(cell, input=EMPTY, buffer=next_buffer),
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
            self_mailbox="_",
            control=(),
            buffer=(),
        ),
    )


def _process_self_mailbox(cell: Cell) -> StepResult:
    """Process the source-stable self-mailbox init-command subset."""

    target = SELF_MAILBOX_INIT_TARGETS.get(cell.self_mailbox)
    if target is None:
        return StepResult("self-mailbox-unsupported", cell)

    role, memory = target
    return StepResult(
        "self-mailbox-processed",
        _replace(
            cell,
            role=role,
            memory=memory,
            input=EMPTY,
            output=EMPTY,
            automail="_",
            self_mailbox="_",
            control=(),
            buffer=(),
        ),
    )


def _process_completed_command_buffer(cell: Cell) -> StepResult | None:
    """Process supported just-filled command-buffer slices."""

    decoded = _decode_command_buffer(cell.buffer)
    if decoded is None:
        return None

    target_id, command_id = decoded
    if target_id == "self":
        if command_id not in SELF_MAILBOX_INIT_TARGETS:
            return None

        mailbox_cell = _replace(
            cell,
            input=EMPTY,
            output=EMPTY,
            automail="_",
            self_mailbox=command_id,
            control=(),
            buffer=(),
        )
        processed = _process_self_mailbox(mailbox_cell)
        return StepResult("stem-command-buffer-self-processed", processed.cell)

    output_index = NEIGHBOR_OUTPUT_INDEX.get(target_id)
    if output_index is None:
        return None

    output = list(EMPTY)
    output[output_index] = command_id
    return StepResult(
        "stem-command-buffer-neighbor-delivered",
        _replace(
            cell,
            input=EMPTY,
            output=tuple(output),
            automail="_",
            self_mailbox="_",
            control=(),
            buffer=(),
        ),
    )


def _decode_command_buffer(buffer: tuple[Signal, ...]) -> tuple[str, str] | None:
    """Decode a complete five-bit command buffer with the ADR-0026 map."""

    if len(buffer) != MAX_STEM_BUFFER_SIZE or any(bit not in (0, 1) for bit in buffer):
        return None

    value = 0
    for bit in buffer:
        value = (value << 1) | bit

    target_id = next(
        target
        for start, end, target in EXPECTED_TARGET_RANGES
        if start <= value <= end
    )
    command_offset = value % len(EXPECTED_COMMANDS)
    command_id = next(
        command
        for offset, command in EXPECTED_COMMANDS
        if offset == command_offset
    )
    return target_id, command_id


def _pull_upstream(cell: Cell) -> Cell:
    """Move upstream neighbor output into input, matching PRC pull semantics."""

    if _empty(cell.upstream):
        return cell
    return _replace(cell, upstream=EMPTY, input=cell.upstream)


def _to_stem(cell: Cell) -> Cell:
    """Reset a fixed cell to the stem role after a stem-init signal."""

    return _replace(
        cell,
        role="stem",
        memory="right",
        input=EMPTY,
        output=EMPTY,
        self_mailbox="_",
    )


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
        "self_mailbox": cell.self_mailbox,
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


def _validate_self_mailbox(self_mailbox: str) -> None:
    if self_mailbox not in VALID_SELF_MAILBOX:
        raise ValueError(f"unknown Universal Cell self mailbox: {self_mailbox!r}")


def _validate_channels(name: str, value: tuple[Signal, ...]) -> None:
    if len(value) != 3:
        raise ValueError(f"{name} must contain exactly three channels")
    _validate_signal_tuple(name, value)


def _validate_signal_tuple(name: str, value: tuple[Signal, ...]) -> None:
    for channel in value:
        if channel not in VALID_CHANNEL_TOKENS:
            raise ValueError(f"{name} contains invalid channel value {channel!r}")
