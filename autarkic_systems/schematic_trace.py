"""Single-node PRC schematic trace support.

This module validates the first concrete bridge from PRC hardware witnesses to
AS executable behavior. The artifact is intentionally modest: one triangular
RLEM/Universal Cell schematic key and one Universal Cell transition trace.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from autarkic_systems.prc_hardware_map import (
    PRCHardwareWitnessMap,
    REQUIRED_WITNESS_IDS,
)
from autarkic_systems.universal_cell import Cell, step_fixed_cell, step_stem_cell


SINGLE_NODE_TRACE_ARTIFACT_ID = (
    "single-node-triangular-rlem-schematic-and-uc-transition-trace"
)
PROCESSOR_MEMORY_TOGGLE_TRACE_ARTIFACT_ID = (
    "processor-memory-toggle-schematic-and-uc-transition-trace"
)
STEM_AUTOMAIL_RECONFIGURATION_TRACE_ARTIFACT_ID = (
    "stem-automail-reconfiguration-schematic-and-uc-transition-trace"
)
VALID_SCHEMATIC_TRACE_ARTIFACT_IDS = (
    SINGLE_NODE_TRACE_ARTIFACT_ID,
    PROCESSOR_MEMORY_TOGGLE_TRACE_ARTIFACT_ID,
    STEM_AUTOMAIL_RECONFIGURATION_TRACE_ARTIFACT_ID,
)

REQUIRED_INTERPRETIVE_LAYERS = (
    "symbolic-rlem-behavior",
    "gelc-geometry",
    "uc-state",
    "candidate-physical-implementation",
)

REQUIRED_CELL_FIELDS = (
    "role",
    "memory",
    "upstream",
    "input",
    "output",
    "automail",
    "control",
    "buffer",
)

VALID_PORT_ORIENTATIONS = {"north", "east", "west"}
VALID_TRANSITION_FUNCTIONS = {"step_fixed_cell", "step_stem_cell"}


@dataclass(frozen=True)
class SchematicPort:
    """One oriented port on the triangular single-node schematic."""

    port_id: str
    label: str
    orientation: str
    signal_index: int
    summary: str


@dataclass(frozen=True)
class InterpretiveLayer:
    """A boundary between schematic meanings that must not be conflated."""

    layer_id: str
    summary: str
    boundary: str
    witness_ids: tuple[str, ...]


@dataclass(frozen=True)
class SingleNodeSchematic:
    """Triangular RLEM/Universal Cell node description."""

    node_id: str
    geometry: str
    memory_direction: str
    ports: tuple[SchematicPort, ...]
    layers: tuple[InterpretiveLayer, ...]


@dataclass(frozen=True)
class RecordedTransitionTrace:
    """One executable UC transition linked to the schematic key."""

    trace_id: str
    transition_function: str
    cell_fields: tuple[str, ...]
    before_cell: dict[str, Any]
    expected_status: str
    expected_after_cell: dict[str, Any]
    routed_signal_flow: tuple[str, ...]


@dataclass(frozen=True)
class SingleNodeSchematicTrace:
    """Loaded single-node schematic trace artifact."""

    schema_version: int
    artifact_id: str
    reviewed_at: str
    purpose: str
    required_witness_ids: tuple[str, ...]
    schematic: SingleNodeSchematic
    trace: RecordedTransitionTrace

    def without_interpretive_layer(self, layer_id: str) -> "SingleNodeSchematicTrace":
        """Return a copy with one interpretive layer removed for tests."""

        schematic = replace(
            self.schematic,
            layers=tuple(
                layer for layer in self.schematic.layers if layer.layer_id != layer_id
            ),
        )
        return replace(self, schematic=schematic)


@dataclass(frozen=True)
class SchematicTraceValidation:
    """One validation result for the schematic trace artifact."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SchematicTraceExecution:
    """Computed result of replaying the recorded transition."""

    status: str
    after_cell: dict[str, Any]


def load_schematic_trace(path: Path | str) -> SingleNodeSchematicTrace:
    """Load a schematic trace artifact from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return SingleNodeSchematicTrace(
        schema_version=_required_int(data, "schema_version"),
        artifact_id=_required_text(data, "artifact_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        required_witness_ids=tuple(
            _text_items(data.get("required_witness_ids"), "required_witness_ids")
        ),
        schematic=_parse_schematic(_required_dict(data, "schematic")),
        trace=_parse_trace(_required_dict(data, "trace")),
    )


def load_single_node_schematic_trace(path: Path | str) -> SingleNodeSchematicTrace:
    """Load the ADR-0016 single-node schematic trace artifact from JSON."""

    return load_schematic_trace(path)


def validate_schematic_trace(
    schematic_trace: SingleNodeSchematicTrace,
    *,
    hardware_witness_map: PRCHardwareWitnessMap,
) -> list[SchematicTraceValidation]:
    """Validate artifact identity, schematic vocabulary, witnesses, and trace."""

    results: list[SchematicTraceValidation] = []
    witnesses_by_id = hardware_witness_map.witnesses_by_id()

    if schematic_trace.artifact_id not in VALID_SCHEMATIC_TRACE_ARTIFACT_IDS:
        results.append(
            _rejected("artifact_id", "artifact id is not a known schematic trace")
        )
    else:
        results.append(_accepted("artifact_id", "artifact id is known"))

    results.extend(_validate_required_witnesses(schematic_trace, witnesses_by_id))
    results.extend(_validate_ports(schematic_trace.schematic.ports))
    results.extend(_validate_layers(schematic_trace.schematic.layers, witnesses_by_id))
    results.extend(_validate_schematic_trace_alignment(schematic_trace))
    results.extend(_validate_trace_contract(schematic_trace.trace))
    results.extend(_validate_trace_execution(schematic_trace))

    return results


def validate_single_node_schematic_trace(
    schematic_trace: SingleNodeSchematicTrace,
    *,
    hardware_witness_map: PRCHardwareWitnessMap,
) -> list[SchematicTraceValidation]:
    """Validate the original ADR-0016 trace against ADR-0015's recommendation."""

    results = validate_schematic_trace(
        schematic_trace,
        hardware_witness_map=hardware_witness_map,
    )

    if schematic_trace.artifact_id != SINGLE_NODE_TRACE_ARTIFACT_ID:
        results.append(
            _rejected("artifact_id", "artifact id does not match ADR-0015 target")
        )
    else:
        results.append(_accepted("artifact_id", "artifact id matches ADR-0015 target"))

    if schematic_trace.artifact_id != hardware_witness_map.recommended_next_artifact:
        results.append(
            _rejected(
                "hardware_witness_map",
                "artifact id does not match hardware witness map recommendation",
            )
        )
    else:
        results.append(
            _accepted("hardware_witness_map", "artifact matches witness-map target")
        )

    return results


def execute_schematic_trace(
    schematic_trace: SingleNodeSchematicTrace,
) -> SchematicTraceExecution:
    """Replay the recorded transition through the current AS UC implementation."""

    trace = schematic_trace.trace
    cell = _cell_from_mapping(trace.before_cell)

    if trace.transition_function == "step_fixed_cell":
        result = step_fixed_cell(cell)
    elif trace.transition_function == "step_stem_cell":
        result = step_stem_cell(cell)
    else:
        raise ValueError(f"unknown transition function: {trace.transition_function!r}")

    return SchematicTraceExecution(
        status=result.status,
        after_cell=_cell_to_mapping(result.cell),
    )


def _parse_schematic(item: dict[str, Any]) -> SingleNodeSchematic:
    ports = _required_list(item, "ports")
    layers = _required_list(item, "layers")
    return SingleNodeSchematic(
        node_id=_required_text(item, "node_id"),
        geometry=_required_text(item, "geometry"),
        memory_direction=_required_text(item, "memory_direction"),
        ports=tuple(_parse_port(port) for port in ports),
        layers=tuple(_parse_layer(layer) for layer in layers),
    )


def _parse_port(item: Any) -> SchematicPort:
    port = _require_dict_value(item, "port")
    return SchematicPort(
        port_id=_required_text(port, "port_id"),
        label=_required_text(port, "label"),
        orientation=_required_text(port, "orientation"),
        signal_index=_required_int(port, "signal_index"),
        summary=_required_text(port, "summary"),
    )


def _parse_layer(item: Any) -> InterpretiveLayer:
    layer = _require_dict_value(item, "layer")
    return InterpretiveLayer(
        layer_id=_required_text(layer, "layer_id"),
        summary=_required_text(layer, "summary"),
        boundary=_required_text(layer, "boundary"),
        witness_ids=tuple(_text_items(layer.get("witness_ids"), "witness_ids")),
    )


def _parse_trace(item: dict[str, Any]) -> RecordedTransitionTrace:
    return RecordedTransitionTrace(
        trace_id=_required_text(item, "trace_id"),
        transition_function=_required_text(item, "transition_function"),
        cell_fields=tuple(_text_items(item.get("cell_fields"), "cell_fields")),
        before_cell=_normalize_cell_mapping(_required_dict(item, "before_cell")),
        expected_status=_required_text(item, "expected_status"),
        expected_after_cell=_normalize_cell_mapping(
            _required_dict(item, "expected_after_cell")
        ),
        routed_signal_flow=tuple(
            _text_items(item.get("routed_signal_flow"), "routed_signal_flow")
        ),
    )


def _validate_required_witnesses(
    schematic_trace: SingleNodeSchematicTrace,
    witnesses_by_id: dict[str, object],
) -> list[SchematicTraceValidation]:
    results: list[SchematicTraceValidation] = []

    if schematic_trace.required_witness_ids != REQUIRED_WITNESS_IDS:
        results.append(
            _rejected("required_witness_ids", "artifact does not cite every PRC witness")
        )
    else:
        results.append(_accepted("required_witness_ids", "all PRC witnesses cited"))

    for witness_id in schematic_trace.required_witness_ids:
        if witness_id not in witnesses_by_id:
            results.append(_rejected(witness_id, "unknown PRC witness id"))
        else:
            results.append(_accepted(witness_id, "known PRC witness id"))

    return results


def _validate_ports(
    ports: tuple[SchematicPort, ...],
) -> list[SchematicTraceValidation]:
    results: list[SchematicTraceValidation] = []

    if len(ports) != 3:
        results.append(_rejected("ports", "schematic must name exactly three ports"))
    else:
        results.append(_accepted("ports", "schematic names exactly three ports"))

    orientations = [port.orientation for port in ports]
    if set(orientations) != VALID_PORT_ORIENTATIONS or len(set(orientations)) != 3:
        results.append(_rejected("ports", "ports must be north/east/west"))
    else:
        results.append(_accepted("ports", "port orientations are explicit"))

    indices = [port.signal_index for port in ports]
    if set(indices) != {0, 1, 2} or len(set(indices)) != 3:
        results.append(_rejected("ports", "ports must map signal indices 0, 1, 2"))
    else:
        results.append(_accepted("ports", "port signal indices are explicit"))

    if len({port.port_id for port in ports}) != len(ports):
        results.append(_rejected("ports", "duplicate port ids"))
    else:
        results.append(_accepted("ports", "port ids are unique"))

    return results


def _validate_layers(
    layers: tuple[InterpretiveLayer, ...],
    witnesses_by_id: dict[str, object],
) -> list[SchematicTraceValidation]:
    results: list[SchematicTraceValidation] = []
    layer_ids = tuple(layer.layer_id for layer in layers)

    for required_layer in REQUIRED_INTERPRETIVE_LAYERS:
        if required_layer not in layer_ids:
            results.append(_rejected(required_layer, "missing interpretive layer"))
        else:
            results.append(_accepted(required_layer, "interpretive layer present"))

    if layer_ids == REQUIRED_INTERPRETIVE_LAYERS:
        results.append(_accepted("layers", "interpretive layers are in canonical order"))
    else:
        results.append(_rejected("layers", "interpretive layers are not canonical"))

    for layer in layers:
        if not layer.boundary:
            results.append(_rejected(layer.layer_id, "missing layer boundary"))
        else:
            results.append(_accepted(layer.layer_id, "layer boundary present"))

        for witness_id in layer.witness_ids:
            if witness_id not in witnesses_by_id:
                results.append(_rejected(layer.layer_id, f"unknown witness {witness_id}"))
            else:
                results.append(_accepted(layer.layer_id, f"known witness {witness_id}"))

    return results


def _validate_schematic_trace_alignment(
    schematic_trace: SingleNodeSchematicTrace,
) -> list[SchematicTraceValidation]:
    results: list[SchematicTraceValidation] = []
    before_role = schematic_trace.trace.before_cell.get("role")

    if before_role == "stem":
        results.extend(_validate_stem_automail_trace_alignment(schematic_trace))
        return results

    if schematic_trace.schematic.geometry != "triangular-rlem-node":
        results.append(_rejected("geometry", "schematic geometry is not triangular"))
    else:
        results.append(_accepted("geometry", "schematic geometry is triangular"))

    trace_memory = schematic_trace.trace.before_cell.get("memory")
    if schematic_trace.schematic.memory_direction != trace_memory:
        results.append(
            _rejected("memory_direction", "schematic memory does not match trace memory")
        )
    else:
        results.append(_accepted("memory_direction", "schematic memory matches trace"))

    expected_flow_by_memory = {
        "right": (
            "input[2] -> output[0]",
            "input[0] -> output[1]",
            "input[1] -> output[2]",
        ),
        "left": (
            "input[1] -> output[0]",
            "input[2] -> output[1]",
            "input[0] -> output[2]",
        ),
    }
    expected_flow = expected_flow_by_memory.get(schematic_trace.schematic.memory_direction)
    if expected_flow is None:
        results.append(_rejected("memory_direction", "unknown schematic memory"))
    elif schematic_trace.trace.routed_signal_flow != expected_flow:
        results.append(_rejected("routed_signal_flow", "memory flow mismatch"))
    else:
        results.append(_accepted("routed_signal_flow", "memory flow is explicit"))

    before_memory = schematic_trace.trace.before_cell.get("memory")
    after_memory = schematic_trace.trace.expected_after_cell.get("memory")
    if before_role == "proc":
        expected_after_memory = "right" if before_memory == "left" else "left"
        if after_memory != expected_after_memory:
            results.append(
                _rejected(
                    "processor-memory-toggle",
                    "processor trace does not toggle memory",
                )
            )
        else:
            results.append(
                _accepted(
                    "processor-memory-toggle",
                    "processor trace toggles memory",
                )
            )

    return results


def _validate_stem_automail_trace_alignment(
    schematic_trace: SingleNodeSchematicTrace,
) -> list[SchematicTraceValidation]:
    results: list[SchematicTraceValidation] = []

    if schematic_trace.schematic.geometry != "triangular-rlem-node":
        results.append(_rejected("geometry", "schematic geometry is not triangular"))
    else:
        results.append(_accepted("geometry", "schematic geometry is triangular"))

    automail = schematic_trace.trace.before_cell.get("automail")
    expected_targets = {
        "wr": ("wire", "right"),
        "wl": ("wire", "left"),
        "pr": ("proc", "right"),
        "pl": ("proc", "left"),
    }
    target = expected_targets.get(automail)
    if target is None:
        results.append(
            _rejected("stem-automail-reconfiguration", "unknown stem automail")
        )
        return results

    expected_role, expected_memory = target
    after = schematic_trace.trace.expected_after_cell

    if schematic_trace.schematic.memory_direction != expected_memory:
        results.append(
            _rejected(
                "memory_direction",
                "schematic memory does not match automail target",
            )
        )
    else:
        results.append(_accepted("memory_direction", "schematic memory matches target"))

    expected_flow = (
        f"automail[{automail}] -> role {expected_role}",
        f"automail[{automail}] -> memory {expected_memory}",
        f"automail[{automail}] consumed -> _",
    )
    if schematic_trace.trace.routed_signal_flow != expected_flow:
        results.append(
            _rejected("routed_signal_flow", "stem automail flow mismatch")
        )
    else:
        results.append(_accepted("routed_signal_flow", "stem automail flow explicit"))

    if (
        after.get("role") != expected_role
        or after.get("memory") != expected_memory
        or after.get("automail") != "_"
    ):
        results.append(
            _rejected(
                "stem-automail-reconfiguration",
                "stem automail target or consumption mismatch",
            )
        )
    else:
        results.append(
            _accepted(
                "stem-automail-reconfiguration",
                "stem automail target and consumption match",
            )
        )

    return results


def _validate_trace_contract(
    trace: RecordedTransitionTrace,
) -> list[SchematicTraceValidation]:
    results: list[SchematicTraceValidation] = []

    if trace.transition_function not in VALID_TRANSITION_FUNCTIONS:
        results.append(
            _rejected("transition_function", "unknown transition function")
        )
    else:
        results.append(_accepted("transition_function", "transition function known"))

    if trace.cell_fields != REQUIRED_CELL_FIELDS:
        results.append(_rejected("cell_fields", "trace does not map every Cell field"))
    else:
        results.append(_accepted("cell_fields", "trace maps every Cell field"))

    for cell_name, cell_mapping in (
        ("before_cell", trace.before_cell),
        ("expected_after_cell", trace.expected_after_cell),
    ):
        missing = [
            field for field in REQUIRED_CELL_FIELDS if field not in cell_mapping
        ]
        if missing:
            results.append(
                _rejected(cell_name, f"missing fields: {', '.join(missing)}")
            )
        else:
            results.append(_accepted(cell_name, "all Cell fields present"))

    if not trace.routed_signal_flow:
        results.append(_rejected("routed_signal_flow", "missing routed signal flow"))
    else:
        results.append(_accepted("routed_signal_flow", "signal flow recorded"))

    return results


def _validate_trace_execution(
    schematic_trace: SingleNodeSchematicTrace,
) -> list[SchematicTraceValidation]:
    try:
        execution = execute_schematic_trace(schematic_trace)
    except ValueError as exc:
        return [_rejected("execution", str(exc))]

    results: list[SchematicTraceValidation] = []
    if execution.status != schematic_trace.trace.expected_status:
        results.append(
            _rejected(
                "execution",
                f"status {execution.status!r} != {schematic_trace.trace.expected_status!r}",
            )
        )
    else:
        results.append(_accepted("execution", "recorded status matches execution"))

    if execution.after_cell != schematic_trace.trace.expected_after_cell:
        results.append(_rejected("execution", "recorded after-cell does not match"))
    else:
        results.append(_accepted("execution", "recorded after-cell matches execution"))

    return results


def _cell_from_mapping(mapping: dict[str, Any]) -> Cell:
    return Cell(
        role=mapping["role"],
        memory=mapping["memory"],
        upstream=tuple(mapping["upstream"]),
        input=tuple(mapping["input"]),
        output=tuple(mapping["output"]),
        automail=mapping["automail"],
        control=tuple(mapping["control"]),
        buffer=tuple(mapping["buffer"]),
    )


def _cell_to_mapping(cell: Cell) -> dict[str, Any]:
    return {
        "role": cell.role,
        "memory": cell.memory,
        "upstream": list(cell.upstream),
        "input": list(cell.input),
        "output": list(cell.output),
        "automail": cell.automail,
        "control": list(cell.control),
        "buffer": list(cell.buffer),
    }


def _normalize_cell_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(mapping)
    for field in ("upstream", "input", "output", "control", "buffer"):
        value = normalized.get(field)
        if not isinstance(value, list):
            raise ValueError(f"{field} must be a JSON list")
    return normalized


def _required_dict(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    return _require_dict_value(value, key)


def _required_list(item: dict[str, Any], key: str) -> list[Any]:
    value = item.get(key)
    if not isinstance(value, list):
        raise ValueError(f"required list field missing: {key}")
    return value


def _require_dict_value(value: Any, key: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"required object missing: {key}")
    return value


def _text_items(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty list")
    text_values: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{field} contains non-text item")
        text_values.append(item)
    return text_values


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


def _accepted(subject: str, detail: str) -> SchematicTraceValidation:
    return SchematicTraceValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> SchematicTraceValidation:
    return SchematicTraceValidation(subject=subject, accepted=False, detail=detail)
