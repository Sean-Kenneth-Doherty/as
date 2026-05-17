"""Predicates over composed Universal Cell transition chains."""

from __future__ import annotations

from dataclasses import dataclass

from autarkic_systems.transition_chains import (
    NEIGHBOR_DELIVERY_STATUS,
RECIPIENT_CONSUMED_STATUS,
    NeighborDeliveryRecipientChain,
)


@dataclass(frozen=True)
class ChainPredicateResult:
    """Boolean result for a transition-chain predicate."""

    name: str
    holds: bool
    detail: str


def neighbor_delivery_consumed_by_recipient(
    chain: NeighborDeliveryRecipientChain,
) -> ChainPredicateResult:
    """Check the narrow ADR-0077 neighbor-delivery consumption handoff."""

    name = "neighbor_delivery_consumed_by_recipient"
    if not chain.accepted or chain.status != "neighbor-delivery-consumed":
        return ChainPredicateResult(
            name,
            False,
            f"chain status {chain.status} is not neighbor-delivery-consumed",
        )
    if chain.sender_result.status != NEIGHBOR_DELIVERY_STATUS:
        return ChainPredicateResult(
            name,
            False,
            f"sender status {chain.sender_result.status} is not {NEIGHBOR_DELIVERY_STATUS}",
        )
    if chain.recipient_before is None or chain.recipient_result is None:
        return ChainPredicateResult(name, False, "recipient handoff is missing")
    if chain.recipient_before.upstream != chain.sender_result.cell.output:
        return ChainPredicateResult(
            name,
            False,
            "recipient upstream does not match delivered sender output",
        )
    if chain.recipient_result.status != RECIPIENT_CONSUMED_STATUS:
        return ChainPredicateResult(
            name,
            False,
            "recipient status "
            f"{chain.recipient_result.status} is not {RECIPIENT_CONSUMED_STATUS}",
        )
    if chain.recipient_result.cell.upstream != ("_", "_", "_"):
        return ChainPredicateResult(name, False, "recipient upstream was not cleared")
    if chain.recipient_result.cell.input != ("_", "_", "_"):
        return ChainPredicateResult(name, False, "recipient input was not cleared")
    return ChainPredicateResult(
        name,
        True,
        "neighbor delivery output was consumed by recipient init-family logic",
    )


def neighbor_delivery_rejected_by_recipient(
    chain: NeighborDeliveryRecipientChain,
) -> ChainPredicateResult:
    """Check the narrow neighbor-delivered non-init rejection boundary."""

    name = "neighbor_delivery_rejected_by_recipient"
    if chain.status != "recipient-not-consumed":
        return ChainPredicateResult(
            name,
            False,
            f"chain status {chain.status} is not recipient-not-consumed",
        )
    if chain.sender_result.status != NEIGHBOR_DELIVERY_STATUS:
        return ChainPredicateResult(
            name,
            False,
            f"sender status {chain.sender_result.status} is not {NEIGHBOR_DELIVERY_STATUS}",
        )
    if chain.recipient_before is None or chain.recipient_result is None:
        return ChainPredicateResult(name, False, "recipient handoff is missing")
    if chain.recipient_before.upstream != chain.sender_result.cell.output:
        return ChainPredicateResult(
            name,
            False,
            "recipient upstream does not match delivered sender output",
        )
    if chain.recipient_result.status != "rejected-input":
        return ChainPredicateResult(
            name,
            False,
            f"recipient status {chain.recipient_result.status} is not rejected-input",
        )
    if chain.recipient_result.cell.upstream != ("_", "_", "_"):
        return ChainPredicateResult(name, False, "recipient upstream was not cleared")
    if chain.recipient_result.cell.input != ("_", "_", "_"):
        return ChainPredicateResult(name, False, "recipient input was not cleared")
    if chain.recipient_result.cell.output != ("_", "_", "_"):
        return ChainPredicateResult(name, False, "recipient output was not empty")
    return ChainPredicateResult(
        name,
        True,
        "neighbor delivery output was rejected by recipient non-init boundary",
    )
