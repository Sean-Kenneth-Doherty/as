"""Loader and evaluator for machine-readable AS claim manifests."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from autarkic_systems import transition_predicates
from autarkic_systems.universal_cell import Cell, StepResult


@dataclass(frozen=True)
class ClaimExample:
    """One executable example attached to a claim."""

    name: str
    expected: bool
    before: Cell
    result: StepResult


@dataclass(frozen=True)
class Claim:
    """A manifest claim that names an implemented predicate checker."""

    claim_id: str
    predicate: str
    description: str
    examples: tuple[ClaimExample, ...]

    def with_checker(self, checker: str) -> "Claim":
        """Return a copy referencing a different predicate checker."""

        return replace(self, predicate=checker)


@dataclass(frozen=True)
class ExampleEvaluation:
    """Observed outcome for a claim example."""

    claim_id: str
    example_name: str
    expected: bool
    observed: bool
    matched: bool
    detail: str


def load_transition_claims(path: Path | str) -> list[Claim]:
    """Load transition claims from a JSON manifest."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    claims = data.get("claims")
    if not isinstance(claims, list):
        raise ValueError("claim manifest must contain a claims list")
    return [_parse_claim(item) for item in claims]


def evaluate_claim_examples(claims: Iterable[Claim]) -> list[ExampleEvaluation]:
    """Evaluate every example for every claim against its predicate checker."""

    evaluations: list[ExampleEvaluation] = []
    for claim in claims:
        checker = getattr(transition_predicates, claim.predicate, None)
        if checker is None:
            raise ValueError(f"unknown predicate checker: {claim.predicate}")
        for example in claim.examples:
            predicate_result = checker(example.before, example.result)
            observed = bool(predicate_result.holds)
            evaluations.append(
                ExampleEvaluation(
                    claim_id=claim.claim_id,
                    example_name=example.name,
                    expected=example.expected,
                    observed=observed,
                    matched=observed == example.expected,
                    detail=predicate_result.detail,
                )
            )
    return evaluations


def _parse_claim(item: dict[str, Any]) -> Claim:
    examples = item.get("examples")
    if not isinstance(examples, list) or not examples:
        raise ValueError(f"claim {item.get('id')!r} must define examples")
    return Claim(
        claim_id=_required_text(item, "id"),
        predicate=_required_text(item, "predicate"),
        description=_required_text(item, "description"),
        examples=tuple(_parse_example(example) for example in examples),
    )


def _parse_example(item: dict[str, Any]) -> ClaimExample:
    return ClaimExample(
        name=_required_text(item, "name"),
        expected=_required_bool(item, "expected"),
        before=_parse_cell(item["before"]),
        result=_parse_result(item["result"]),
    )


def _parse_result(item: dict[str, Any]) -> StepResult:
    return StepResult(status=_required_text(item, "status"), cell=_parse_cell(item["cell"]))


def _parse_cell(item: dict[str, Any]) -> Cell:
    return Cell(
        role=_required_text(item, "role"),
        memory=_required_text(item, "memory"),
        upstream=_parse_signal(item.get("upstream", ["_", "_", "_"])),
        input=_parse_signal(item.get("input", ["_", "_", "_"])),
        output=_parse_signal(item.get("output", ["_", "_", "_"])),
        automail=item.get("automail", "_"),
        self_mailbox=item.get("self_mailbox", "_"),
        control=tuple(item.get("control", [])),
        buffer=tuple(item.get("buffer", [])),
    )


def _parse_signal(value: list[Any]) -> tuple[Any, Any, Any]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError("signal must be a three-item list")
    return tuple(value)


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_bool(item: dict[str, Any], key: str) -> bool:
    value = item.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"required boolean field missing: {key}")
    return value
