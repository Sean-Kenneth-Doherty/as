"""Inspectable two-cell execution witnesses over existing UC transitions.

This module deliberately does not add scheduler, topology, timing, or output
clearing semantics. It wraps the existing neighbor-delivery chain helper and
records the sender step, optional handoff installation, and optional recipient
step as a small network-shaped witness.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any, Literal

from autarkic_systems.transition_chains import (
    ChainStatus,
    execute_neighbor_delivery_recipient_chain,
)
from autarkic_systems.universal_cell import Cell, Signal, StepResult


WitnessEventPhase = Literal[
    "sender-step",
    "handoff",
    "handoff-blocked",
    "recipient-step",
]


@dataclass(frozen=True)
class NetworkWitnessEvent:
    """One observable event in the bounded two-cell witness."""

    phase: WitnessEventPhase
    actor: str
    status: str
    detail: str
    delivered_tuple: tuple[Signal, Signal, Signal] | None = None


@dataclass(frozen=True)
class TwoCellNetworkWitness:
    """A bounded two-cell run using the existing neighbor-delivery chain."""

    status: ChainStatus
    accepted: bool
    sender_id: str
    recipient_id: str
    sender_before: Cell
    recipient_before: Cell
    sender_result: StepResult
    recipient_before_step: Cell | None
    recipient_result: StepResult | None
    events: tuple[NetworkWitnessEvent, ...]
    detail: str

    @property
    def sender_after(self) -> Cell:
        """Sender state after the sender transition has executed."""

        return self.sender_result.cell

    @property
    def recipient_after(self) -> Cell:
        """Recipient state after the witness run.

        If delivery was not installed or no recipient step ran, the recipient
        remains at its original state. This avoids silently overwriting pending
        recipient input or upstream state.
        """

        if self.recipient_result is None:
            return self.recipient_before
        return self.recipient_result.cell

    @property
    def delivered_tuple(self) -> tuple[Signal, Signal, Signal] | None:
        """Tuple installed as recipient upstream, if installation occurred."""

        if self.recipient_before_step is None:
            return None
        return self.recipient_before_step.upstream


def execute_two_cell_neighbor_delivery_witness(
    sender: Cell,
    recipient: Cell,
    *,
    sender_id: str = "sender",
    recipient_id: str = "recipient",
) -> TwoCellNetworkWitness:
    """Execute and record a two-cell neighbor-delivery witness."""

    chain = execute_neighbor_delivery_recipient_chain(sender, recipient)
    events: list[NetworkWitnessEvent] = [
        NetworkWitnessEvent(
            phase="sender-step",
            actor=sender_id,
            status=chain.sender_result.status,
            detail="sender executed through the existing stem transition",
        )
    ]

    if chain.status == "sender-not-delivered":
        return TwoCellNetworkWitness(
            status=chain.status,
            accepted=chain.accepted,
            sender_id=sender_id,
            recipient_id=recipient_id,
            sender_before=sender,
            recipient_before=recipient,
            sender_result=chain.sender_result,
            recipient_before_step=None,
            recipient_result=None,
            events=tuple(events),
            detail=chain.detail,
        )

    actor = f"{sender_id}->{recipient_id}"
    if chain.status == "recipient-not-ready":
        events.append(
            NetworkWitnessEvent(
                phase="handoff-blocked",
                actor=actor,
                status=chain.status,
                detail=chain.detail,
            )
        )
        return TwoCellNetworkWitness(
            status=chain.status,
            accepted=chain.accepted,
            sender_id=sender_id,
            recipient_id=recipient_id,
            sender_before=sender,
            recipient_before=recipient,
            sender_result=chain.sender_result,
            recipient_before_step=None,
            recipient_result=None,
            events=tuple(events),
            detail=chain.detail,
        )

    if chain.recipient_before is None or chain.recipient_result is None:
        raise ValueError(f"unexpected incomplete chain for status {chain.status!r}")

    delivered = chain.recipient_before.upstream
    events.append(
        NetworkWitnessEvent(
            phase="handoff",
            actor=actor,
            status="installed-upstream",
            detail="sender output installed as recipient upstream",
            delivered_tuple=delivered,
        )
    )
    events.append(
        NetworkWitnessEvent(
            phase="recipient-step",
            actor=recipient_id,
            status=chain.recipient_result.status,
            detail="recipient executed through the existing fixed/stem transition",
        )
    )
    return TwoCellNetworkWitness(
        status=chain.status,
        accepted=chain.accepted,
        sender_id=sender_id,
        recipient_id=recipient_id,
        sender_before=sender,
        recipient_before=recipient,
        sender_result=chain.sender_result,
        recipient_before_step=chain.recipient_before,
        recipient_result=chain.recipient_result,
        events=tuple(events),
        detail=chain.detail,
    )


def two_cell_network_witness_payload(
    witness: TwoCellNetworkWitness,
) -> dict[str, Any]:
    """Return a JSON-serializable witness payload."""

    return {
        "schema_version": 1,
        "witness_id": "two-cell-neighbor-delivery-witness",
        "status": witness.status,
        "accepted": witness.accepted,
        "detail": witness.detail,
        "delivered_tuple": _optional_signal_tuple_payload(witness.delivered_tuple),
        "sender": {
            "id": witness.sender_id,
            "before": _cell_payload(witness.sender_before),
            "after_step": _cell_payload(witness.sender_after),
        },
        "recipient": {
            "id": witness.recipient_id,
            "before": _cell_payload(witness.recipient_before),
            "before_step": _optional_cell_payload(witness.recipient_before_step),
            "after": _cell_payload(witness.recipient_after),
        },
        "events": [
            {
                "phase": event.phase,
                "actor": event.actor,
                "status": event.status,
                "detail": event.detail,
                "delivered_tuple": _optional_signal_tuple_payload(
                    event.delivered_tuple
                ),
            }
            for event in witness.events
        ],
    }


def format_two_cell_network_witness(witness: TwoCellNetworkWitness) -> str:
    """Format a compact operator-facing witness report."""

    delivered = (
        _format_signal_tuple(witness.delivered_tuple)
        if witness.delivered_tuple is not None
        else "none"
    )
    lines = [
        f"Two-cell network witness: {witness.status}",
        f"Accepted: {'yes' if witness.accepted else 'no'}",
        f"Delivered tuple: {delivered}",
        f"Detail: {witness.detail}",
    ]
    for event in witness.events:
        suffix = ""
        if event.delivered_tuple is not None:
            suffix = f" [{_format_signal_tuple(event.delivered_tuple)}]"
        lines.append(f"{event.phase} {event.actor}: {event.status}{suffix}")
    lines.extend(
        [
            "Sender after: " + _format_cell_summary(witness.sender_after),
            "Recipient after: " + _format_cell_summary(witness.recipient_after),
        ]
    )
    return "\n".join(lines)


def run_network_witness_cli(argv: list[str] | None = None) -> int:
    """Run the two-cell network witness command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.network_witness",
        description="Render a bounded two-cell neighbor-delivery witness.",
    )
    parser.add_argument(
        "--case",
        choices=tuple(_FIXTURE_CASES),
        default="init-consumed",
        help="Named fixture case to execute.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    args = parser.parse_args(argv)

    sender, recipient = _fixture_cells(args.case)
    witness = execute_two_cell_neighbor_delivery_witness(sender, recipient)
    if args.format == "json":
        print(json.dumps(two_cell_network_witness_payload(witness), sort_keys=True))
    else:
        print(format_two_cell_network_witness(witness))
    return 0 if witness.accepted else 1


def _cell_payload(cell: Cell) -> dict[str, Any]:
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


def _optional_cell_payload(cell: Cell | None) -> dict[str, Any] | None:
    if cell is None:
        return None
    return _cell_payload(cell)


def _optional_signal_tuple_payload(
    signal: tuple[Signal, Signal, Signal] | None,
) -> list[Signal] | None:
    if signal is None:
        return None
    return list(signal)


def _format_signal_tuple(signal: tuple[Signal, ...]) -> str:
    return ", ".join(str(channel) for channel in signal)


def _format_cell_summary(cell: Cell) -> str:
    return (
        f"role={cell.role} memory={cell.memory} "
        f"upstream={_format_signal_tuple(cell.upstream)} "
        f"input={_format_signal_tuple(cell.input)} "
        f"output={_format_signal_tuple(cell.output)} "
        f"buffer={_format_signal_tuple(cell.buffer)}"
    )


def _fixture_cells(case: str) -> tuple[Cell, Cell]:
    try:
        return _FIXTURE_CASES[case]()
    except KeyError as exc:
        raise ValueError(f"unknown witness fixture case: {case!r}") from exc


def _init_consumed_fixture() -> tuple[Cell, Cell]:
    return (
        Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        ),
        Cell(role="wire", memory="right"),
    )


def _write_buffer_one_consumed_fixture() -> tuple[Cell, Cell]:
    return (
        Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 1, 1),
        ),
        Cell(role="wire", memory="right"),
    )


def _standard_signal_rejected_fixture() -> tuple[Cell, Cell]:
    return (
        Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 0, 0),
        ),
        Cell(role="wire", memory="right"),
    )


def _recipient_not_ready_fixture() -> tuple[Cell, Cell]:
    return (
        Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        ),
        Cell(role="wire", memory="right", upstream=(0, "_", "_")),
    )


def _sender_not_delivered_fixture() -> tuple[Cell, Cell]:
    return (
        Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(1, 0, 0),
            buffer=(0, 0, 0, 0),
        ),
        Cell(role="wire", memory="right"),
    )


_FIXTURE_CASES = {
    "init-consumed": _init_consumed_fixture,
    "write-buffer-one-consumed": _write_buffer_one_consumed_fixture,
    "standard-signal-rejected": _standard_signal_rejected_fixture,
    "recipient-not-ready": _recipient_not_ready_fixture,
    "sender-not-delivered": _sender_not_delivered_fixture,
}


if __name__ == "__main__":
    raise SystemExit(run_network_witness_cli())
