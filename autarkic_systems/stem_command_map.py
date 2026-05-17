"""Stem command-buffer map support.

This module makes PRC's five-bit stem command-buffer encoding explicit without
executing the decoded commands. Execution belongs in a later ADR.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


COMMAND_BUFFER_WIDTH = 5
COMMAND_BUFFER_VALUE_COUNT = 2**COMMAND_BUFFER_WIDTH
EXPECTED_TARGET_RANGES = (
    (0, 7, "self"),
    (8, 15, "neighbor-a"),
    (16, 23, "neighbor-b"),
    (24, 31, "neighbor-c"),
)
EXPECTED_COMMANDS = (
    (0, "standard-signal"),
    (1, "stem-init"),
    (2, "wire-r-init"),
    (3, "wire-l-init"),
    (4, "proc-r-init"),
    (5, "proc-l-init"),
    (6, "write-buf-zero"),
    (7, "write-buf-one"),
)


@dataclass(frozen=True)
class TargetRange:
    """One contiguous command-value range for a command target."""

    target_id: str
    value_start: int
    value_end: int
    summary: str

    def contains(self, value: int) -> bool:
        """Return true when the decoded command value falls in this range."""

        return self.value_start <= value <= self.value_end


@dataclass(frozen=True)
class CommandEntry:
    """One command selected by an offset inside a target range."""

    offset: int
    command_id: str
    summary: str


@dataclass(frozen=True)
class DecodedStemCommand:
    """Decoded target and command for one five-bit stem buffer."""

    value: int
    bits: tuple[int, ...]
    target_id: str
    command_id: str


@dataclass(frozen=True)
class StemCommandBufferMap:
    """Loaded stem command-buffer map artifact."""

    schema_version: int
    map_id: str
    reviewed_at: str
    source_witness_id: str
    local_witness: str
    source_locus: str
    bit_order: str
    buffer_width: int
    target_ranges: tuple[TargetRange, ...]
    commands: tuple[CommandEntry, ...]

    def decode_cases(self) -> tuple[DecodedStemCommand, ...]:
        """Return the complete decoded 0-31 command surface."""

        return tuple(self.decode_value(value) for value in range(COMMAND_BUFFER_VALUE_COUNT))

    def decode_buffer(self, buffer: tuple[int, ...]) -> DecodedStemCommand:
        """Decode one five-bit buffer using the map's bit-order convention."""

        if len(buffer) != COMMAND_BUFFER_WIDTH:
            raise ValueError("stem command buffer must contain exactly five bits")
        if any(bit not in (0, 1) for bit in buffer):
            raise ValueError("stem command buffer bits must be 0 or 1")

        value = 0
        for bit in buffer:
            value = (value << 1) | bit
        return self.decode_value(value)

    def decode_value(self, value: int) -> DecodedStemCommand:
        """Decode one integer command-buffer value."""

        if value < 0 or value >= COMMAND_BUFFER_VALUE_COUNT:
            raise ValueError(f"command value out of range: {value}")

        target_range = _target_for_value(self.target_ranges, value)
        command = _command_for_offset(self.commands, value - target_range.value_start)
        bits = tuple((value >> shift) & 1 for shift in range(COMMAND_BUFFER_WIDTH - 1, -1, -1))
        return DecodedStemCommand(
            value=value,
            bits=bits,
            target_id=target_range.target_id,
            command_id=command.command_id,
        )


@dataclass(frozen=True)
class StemCommandMapValidation:
    """One validation result for the stem command-buffer map."""

    subject: str
    accepted: bool
    detail: str


def load_stem_command_buffer_map(path: Path | str) -> StemCommandBufferMap:
    """Load a stem command-buffer map from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return StemCommandBufferMap(
        schema_version=_required_int(data, "schema_version"),
        map_id=_required_text(data, "map_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        source_witness_id=_required_text(data, "source_witness_id"),
        local_witness=_required_text(data, "local_witness"),
        source_locus=_required_text(data, "source_locus"),
        bit_order=_required_text(data, "bit_order"),
        buffer_width=_required_int(data, "buffer_width"),
        target_ranges=tuple(
            _parse_target_range(item) for item in _required_list(data, "target_ranges")
        ),
        commands=tuple(_parse_command(item) for item in _required_list(data, "commands")),
    )


def validate_stem_command_buffer_map(
    command_map: StemCommandBufferMap,
) -> list[StemCommandMapValidation]:
    """Validate the command-buffer map shape and complete decode surface."""

    results: list[StemCommandMapValidation] = []

    if command_map.buffer_width != COMMAND_BUFFER_WIDTH:
        results.append(_rejected("buffer_width", "buffer width is not five bits"))
    else:
        results.append(_accepted("buffer_width", "buffer width is five bits"))

    if command_map.bit_order != "accumulated-msb-first":
        results.append(_rejected("bit_order", "unknown bit order"))
    else:
        results.append(_accepted("bit_order", "bit order is explicit"))

    covered_values: list[int] = []
    for target_range in command_map.target_ranges:
        if target_range.value_start > target_range.value_end:
            results.append(_rejected("target_ranges", "target range is inverted"))
        covered_values.extend(range(target_range.value_start, target_range.value_end + 1))

    target_shapes = tuple(
        sorted(
            (
                target_range.value_start,
                target_range.value_end,
                target_range.target_id,
            )
            for target_range in command_map.target_ranges
        )
    )
    if sorted(covered_values) != list(range(COMMAND_BUFFER_VALUE_COUNT)):
        results.append(_rejected("target_ranges", "target ranges do not cover 0-31 exactly"))
    elif len(set(covered_values)) != COMMAND_BUFFER_VALUE_COUNT:
        results.append(_rejected("target_ranges", "target ranges overlap"))
    elif target_shapes != EXPECTED_TARGET_RANGES:
        results.append(_rejected("target_ranges", "target ranges are not the PRC four-range map"))
    else:
        results.append(_accepted("target_ranges", "target ranges cover 0-31 exactly"))

    command_offsets = sorted(command.offset for command in command_map.commands)
    command_pairs = tuple(
        sorted((command.offset, command.command_id) for command in command_map.commands)
    )
    if command_offsets != list(range(8)):
        results.append(_rejected("commands", "command offsets do not cover 0-7"))
    elif len({command.command_id for command in command_map.commands}) != 8:
        results.append(_rejected("commands", "command ids are not unique"))
    elif command_pairs != EXPECTED_COMMANDS:
        results.append(_rejected("commands", "commands are not the PRC eight-command map"))
    else:
        results.append(_accepted("commands", "command offsets cover 0-7"))

    try:
        cases = command_map.decode_cases()
    except ValueError as exc:
        results.append(_rejected("decode_cases", str(exc)))
    else:
        if len(cases) != COMMAND_BUFFER_VALUE_COUNT:
            results.append(_rejected("decode_cases", "decoded case count is not 32"))
        elif {case.value for case in cases} != set(range(COMMAND_BUFFER_VALUE_COUNT)):
            results.append(_rejected("decode_cases", "decoded values are incomplete"))
        else:
            results.append(_accepted("decode_cases", "decoded cases cover 0-31"))

    return results


def _parse_target_range(item: Any) -> TargetRange:
    target_range = _require_dict_value(item, "target_range")
    return TargetRange(
        target_id=_required_text(target_range, "target_id"),
        value_start=_required_int(target_range, "value_start"),
        value_end=_required_int(target_range, "value_end"),
        summary=_required_text(target_range, "summary"),
    )


def _parse_command(item: Any) -> CommandEntry:
    command = _require_dict_value(item, "command")
    return CommandEntry(
        offset=_required_int(command, "offset"),
        command_id=_required_text(command, "command_id"),
        summary=_required_text(command, "summary"),
    )


def _target_for_value(
    target_ranges: tuple[TargetRange, ...],
    value: int,
) -> TargetRange:
    for target_range in target_ranges:
        if target_range.contains(value):
            return target_range
    raise ValueError(f"no target range for command value {value}")


def _command_for_offset(
    commands: tuple[CommandEntry, ...],
    offset: int,
) -> CommandEntry:
    for command in commands:
        if command.offset == offset:
            return command
    raise ValueError(f"no command for offset {offset}")


def _required_list(item: dict[str, Any], key: str) -> list[Any]:
    value = item.get(key)
    if not isinstance(value, list):
        raise ValueError(f"required list field missing: {key}")
    return value


def _require_dict_value(value: Any, key: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"required object missing: {key}")
    return value


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if not isinstance(value, int):
        raise ValueError(f"required integer field missing: {key}")
    return value


def _accepted(subject: str, detail: str) -> StemCommandMapValidation:
    return StemCommandMapValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> StemCommandMapValidation:
    return StemCommandMapValidation(subject=subject, accepted=False, detail=detail)
