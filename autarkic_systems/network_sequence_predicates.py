"""Predicates over post-handoff network sequence witnesses."""

from __future__ import annotations

from dataclasses import dataclass

from autarkic_systems.network_sequence import PostHandoffSignalWitness


@dataclass(frozen=True)
class NetworkSequencePredicateResult:
    """Boolean result for a network-sequence predicate."""

    name: str
    holds: bool
    detail: str


def post_handoff_signal_routed(
    witness: PostHandoffSignalWitness,
) -> NetworkSequencePredicateResult:
    """Check the ADR-0196 post-init-handoff follow-up routing witness."""

    name = "post_handoff_signal_routed"
    if not witness.accepted or witness.status != "post-handoff-signal-routed":
        return NetworkSequencePredicateResult(
            name,
            False,
            f"sequence status {witness.status} is not post-handoff-signal-routed",
        )
    if witness.delivery_witness.status != "neighbor-delivery-consumed":
        return NetworkSequencePredicateResult(
            name,
            False,
            "delivery status "
            f"{witness.delivery_witness.status} is not neighbor-delivery-consumed",
        )
    if (
        witness.delivery_witness.recipient_result is None
        or witness.delivery_witness.recipient_result.status
        != "recipient-init-command-message-processed"
    ):
        return NetworkSequencePredicateResult(
            name,
            False,
            "delivery did not consume an init-family recipient command",
        )
    if witness.recipient_before_followup is None or witness.followup_result is None:
        return NetworkSequencePredicateResult(
            name,
            False,
            "follow-up recipient step is missing",
        )
    before = witness.recipient_before_followup
    after = witness.followup_result.cell
    if before.role != "proc" or before.memory != "left":
        return NetworkSequencePredicateResult(
            name,
            False,
            f"recipient before follow-up is {before.role}/{before.memory}, not proc/left",
        )
    if witness.followup_input != (1, 0, 0):
        return NetworkSequencePredicateResult(
            name,
            False,
            f"follow-up input {witness.followup_input} is not (1, 0, 0)",
        )
    if witness.followup_result.status != "routed":
        return NetworkSequencePredicateResult(
            name,
            False,
            f"follow-up status {witness.followup_result.status} is not routed",
        )
    if after.output != (0, 0, 1):
        return NetworkSequencePredicateResult(
            name,
            False,
            f"recipient output {after.output} is not (0, 0, 1)",
        )
    if after.memory != "right":
        return NetworkSequencePredicateResult(
            name,
            False,
            f"recipient memory {after.memory} is not right after processor toggle",
        )
    if after.input != ("_", "_", "_"):
        return NetworkSequencePredicateResult(
            name,
            False,
            "recipient input was not cleared after routing",
        )
    return NetworkSequencePredicateResult(
        name,
        True,
        "post-handoff proc/left recipient routed follow-up input to (0, 0, 1)",
    )
