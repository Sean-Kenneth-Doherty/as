"""Recorded traces for composed Universal Cell transition chains."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from autarkic_systems import transition_chains
from autarkic_systems.universal_cell import Cell, step_fixed_cell, step_stem_cell


NEIGHBOR_DELIVERY_CHAIN_TRACE_ARTIFACT_ID = "neighbor-delivery-recipient-chain-trace"
VALID_CHAIN_TRACE_ARTIFACT_IDS = (NEIGHBOR_DELIVERY_CHAIN_TRACE_ARTIFACT_ID,)
REQUIRED_CELL_FIELDS = (
    "role",
    "memory",
    "upstream",
    "input",
    "output",
    "automail",
    "self_mailbox",
    "control",
    "buffer",
)
EMPTY_SIGNAL = ["_", "_", "_"]


@dataclass(frozen=True)
class ChainTraceStep:
    """One recorded single-cell step inside a composed transition chain."""

    step_id: str
    transition_function: str
    before_cell: dict[str, Any]
    expected_status: str
    expected_after_cell: dict[str, Any]
    routed_signal_flow: tuple[str, ...]


@dataclass(frozen=True)
class ChainTraceHandoff:
    """Recorded state transfer between sender and recipient steps."""

    source_step: str
    source_field: str
    target_step: str
    target_field: str
    delivered_tuple: tuple[Any, ...]
    expected_recipient_before_cell: dict[str, Any]


@dataclass(frozen=True)
class TransitionChainTrace:
    """Loaded trace for one composed transition-chain handoff."""

    schema_version: int
    artifact_id: str
    reviewed_at: str
    purpose: str
    claim_id: str
    chain_helper: str
    expected_status: str
    recipient_initial_cell: dict[str, Any]
    sender_step: ChainTraceStep
    handoff: ChainTraceHandoff
    recipient_step: ChainTraceStep
    boundaries: tuple[str, ...]

    def with_recipient_initial_cell(
        self,
        cell: dict[str, Any],
    ) -> "TransitionChainTrace":
        """Return a copy with a replacement initial recipient cell."""

        return replace(self, recipient_initial_cell=cell)


@dataclass(frozen=True)
class ChainTraceExecution:
    """Computed result of replaying a transition-chain trace."""

    status: str
    accepted: bool
    sender_after_cell: dict[str, Any]
    recipient_before_cell: dict[str, Any] | None
    recipient_after_cell: dict[str, Any] | None
    detail: str


@dataclass(frozen=True)
class ChainTraceValidation:
    """One validation result for a transition-chain trace artifact."""

    subject: str
    accepted: bool
    detail: str


def load_transition_chain_trace(path: Path | str) -> TransitionChainTrace:
    """Load a transition-chain trace artifact from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return TransitionChainTrace(
        schema_version=_required_int(data, "schema_version"),
        artifact_id=_required_text(data, "artifact_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        claim_id=_required_text(data, "claim_id"),
        chain_helper=_required_text(data, "chain_helper"),
        expected_status=_required_text(data, "expected_status"),
        recipient_initial_cell=_parse_cell_mapping(
            _required_dict(data, "recipient_initial_cell")
        ),
        sender_step=_parse_step(_required_dict(data, "sender_step")),
        handoff=_parse_handoff(_required_dict(data, "handoff")),
        recipient_step=_parse_step(_required_dict(data, "recipient_step")),
        boundaries=tuple(_required_text_list(data, "boundaries")),
    )


def execute_transition_chain_trace(trace: TransitionChainTrace) -> ChainTraceExecution:
    """Replay the trace through the recorded chain helper."""

    helper = getattr(transition_chains, trace.chain_helper, None)
    if helper is None:
        raise ValueError(f"unknown chain helper: {trace.chain_helper}")

    chain = helper(
        _cell_from_mapping(trace.sender_step.before_cell),
        _cell_from_mapping(trace.recipient_initial_cell),
    )
    return ChainTraceExecution(
        status=chain.status,
        accepted=chain.accepted,
        sender_after_cell=_cell_to_mapping(chain.sender_result.cell),
        recipient_before_cell=(
            None if chain.recipient_before is None else _cell_to_mapping(chain.recipient_before)
        ),
        recipient_after_cell=(
            None
            if chain.recipient_result is None
            else _cell_to_mapping(chain.recipient_result.cell)
        ),
        detail=chain.detail,
    )


def validate_transition_chain_trace(
    trace: TransitionChainTrace,
) -> list[ChainTraceValidation]:
    """Validate the trace schema, steps, handoff, and full chain replay."""

    return [
        _validate_schema(trace),
        _validate_participants(trace),
        _validate_step("sender-step", trace.sender_step),
        _validate_handoff(trace),
        _validate_step("recipient-step", trace.recipient_step),
        _validate_chain_execution(trace),
        _validate_boundary(trace),
    ]


def _parse_step(item: dict[str, Any]) -> ChainTraceStep:
    return ChainTraceStep(
        step_id=_required_text(item, "step_id"),
        transition_function=_required_text(item, "transition_function"),
        before_cell=_parse_cell_mapping(_required_dict(item, "before_cell")),
        expected_status=_required_text(item, "expected_status"),
        expected_after_cell=_parse_cell_mapping(
            _required_dict(item, "expected_after_cell")
        ),
        routed_signal_flow=tuple(_required_text_list(item, "routed_signal_flow")),
    )


def _parse_handoff(item: dict[str, Any]) -> ChainTraceHandoff:
    return ChainTraceHandoff(
        source_step=_required_text(item, "source_step"),
        source_field=_required_text(item, "source_field"),
        target_step=_required_text(item, "target_step"),
        target_field=_required_text(item, "target_field"),
        delivered_tuple=tuple(_required_list(item, "delivered_tuple")),
        expected_recipient_before_cell=_parse_cell_mapping(
            _required_dict(item, "expected_recipient_before_cell")
        ),
    )


def _validate_schema(trace: TransitionChainTrace) -> ChainTraceValidation:
    if trace.schema_version != 1:
        return _rejected("schema", f"unsupported schema version {trace.schema_version}")
    if trace.artifact_id not in VALID_CHAIN_TRACE_ARTIFACT_IDS:
        return _rejected("schema", f"unknown artifact id: {trace.artifact_id}")
    if not trace.boundaries:
        return _rejected("schema", "trace must record semantic boundaries")
    if getattr(transition_chains, trace.chain_helper, None) is None:
        return _rejected("schema", f"unknown chain helper: {trace.chain_helper}")
    return _accepted("schema", "schema version and artifact identity accepted")


def _validate_participants(trace: TransitionChainTrace) -> ChainTraceValidation:
    missing = []
    for label, cell in (
        ("sender", trace.sender_step.before_cell),
        ("recipient", trace.recipient_initial_cell),
    ):
        absent = [field for field in REQUIRED_CELL_FIELDS if field not in cell]
        missing.extend(f"{label}.{field}" for field in absent)
    if missing:
        return _rejected("participants", f"missing fields: {', '.join(missing)}")
    if trace.recipient_initial_cell["upstream"] != EMPTY_SIGNAL:
        return _rejected("participants", "recipient initial upstream is not empty")
    if trace.recipient_initial_cell["input"] != EMPTY_SIGNAL:
        return _rejected("participants", "recipient initial input is not empty")
    return _accepted("participants", "sender and initial recipient cells recorded")


def _validate_step(subject: str, step: ChainTraceStep) -> ChainTraceValidation:
    try:
        status, after_cell = _execute_step(step)
    except ValueError as exc:
        return _rejected(subject, str(exc))
    if status != step.expected_status:
        return _rejected(subject, f"status mismatch: {status}")
    if after_cell != step.expected_after_cell:
        return _rejected(subject, "after-cell mismatch")
    if not step.routed_signal_flow:
        return _rejected(subject, "routed signal flow is empty")
    return _accepted(subject, "recorded step matches execution")


def _validate_handoff(trace: TransitionChainTrace) -> ChainTraceValidation:
    handoff = trace.handoff
    if handoff.source_step != trace.sender_step.step_id:
        return _rejected("handoff", "handoff source step does not match sender step")
    if handoff.target_step != trace.recipient_step.step_id:
        return _rejected("handoff", "handoff target step does not match recipient step")
    if handoff.source_field != "output" or handoff.target_field != "upstream":
        return _rejected("handoff", "handoff must connect output to upstream")

    delivered = list(handoff.delivered_tuple)
    if delivered != trace.sender_step.expected_after_cell["output"]:
        return _rejected("handoff", "delivered tuple differs from sender output")
    if handoff.expected_recipient_before_cell != trace.recipient_step.before_cell:
        return _rejected("handoff", "recipient handoff cell differs from recipient step")

    expected_recipient = dict(trace.recipient_initial_cell)
    expected_recipient["upstream"] = delivered
    if handoff.expected_recipient_before_cell != expected_recipient:
        return _rejected("handoff", "recipient handoff cell does not install delivery")
    return _accepted("handoff", "sender output is installed as recipient upstream")


def _validate_chain_execution(trace: TransitionChainTrace) -> ChainTraceValidation:
    try:
        execution = execute_transition_chain_trace(trace)
    except ValueError as exc:
        return _rejected("chain-execution", str(exc))

    failures: list[str] = []
    if execution.status != trace.expected_status:
        failures.append(f"status mismatch: {execution.status}")
    if not execution.accepted:
        failures.append(f"chain rejected: {execution.detail}")
    if execution.sender_after_cell != trace.sender_step.expected_after_cell:
        failures.append("sender after-cell mismatch")
    if execution.recipient_before_cell != trace.handoff.expected_recipient_before_cell:
        failures.append("recipient handoff cell mismatch")
    if execution.recipient_after_cell != trace.recipient_step.expected_after_cell:
        failures.append("recipient after-cell mismatch")
    if failures:
        return _rejected("chain-execution", "; ".join(failures))
    return _accepted("chain-execution", "recorded chain matches helper execution")


def _validate_boundary(trace: TransitionChainTrace) -> ChainTraceValidation:
    joined = " ".join(trace.boundaries).lower()
    required_terms = (
        "scheduler",
        "topology",
        "non-init",
        "standard-signal",
        "write-buffer",
    )
    missing = [term for term in required_terms if term not in joined]
    if missing:
        return _rejected("boundary", f"missing boundary terms: {', '.join(missing)}")
    return _accepted("boundary", "trace boundaries keep chain limits explicit")


def _execute_step(step: ChainTraceStep) -> tuple[str, dict[str, Any]]:
    cell = _cell_from_mapping(step.before_cell)
    if step.transition_function == "step_stem_cell":
        result = step_stem_cell(cell)
    elif step.transition_function == "step_fixed_cell":
        result = step_fixed_cell(cell)
    else:
        raise ValueError(f"unknown transition function: {step.transition_function}")
    return result.status, _cell_to_mapping(result.cell)


def _parse_cell_mapping(item: dict[str, Any]) -> dict[str, Any]:
    parsed = dict(item)
    for field in REQUIRED_CELL_FIELDS:
        if field not in parsed:
            raise ValueError(f"cell mapping missing field: {field}")
    for field in ("upstream", "input", "output", "control", "buffer"):
        parsed[field] = list(_required_list(parsed, field))
    return parsed


def _cell_from_mapping(mapping: dict[str, Any]) -> Cell:
    return Cell(
        role=mapping["role"],
        memory=mapping["memory"],
        upstream=tuple(mapping["upstream"]),
        input=tuple(mapping["input"]),
        output=tuple(mapping["output"]),
        automail=mapping["automail"],
        self_mailbox=mapping["self_mailbox"],
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
        "self_mailbox": cell.self_mailbox,
        "control": list(cell.control),
        "buffer": list(cell.buffer),
    }


def _accepted(subject: str, detail: str) -> ChainTraceValidation:
    return ChainTraceValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> ChainTraceValidation:
    return ChainTraceValidation(subject=subject, accepted=False, detail=detail)


def _required_dict(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required object field missing: {key}")
    return value


def _required_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if not isinstance(value, int):
        raise ValueError(f"required integer field missing: {key}")
    return value


def _required_list(item: dict[str, Any], key: str) -> list[Any]:
    value = item.get(key)
    if not isinstance(value, list):
        raise ValueError(f"required list field missing: {key}")
    return value


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_text_list(item: dict[str, Any], key: str) -> list[str]:
    value = item.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"required text list missing: {key}")
    if not all(isinstance(entry, str) and entry for entry in value):
        raise ValueError(f"text list has invalid entries: {key}")
    return value
