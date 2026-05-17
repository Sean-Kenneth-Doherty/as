"""Structured PRC hardware witness-map support.

The witness map validated here is the bridge from PRC's hardware prose and
research artifacts to AS's later schematic or simulation work. It records the
minimum source anchors needed before AS can claim that a hardware/schematic
artifact honors PRC rather than merely resembling it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable


REQUIRED_WITNESS_IDS = (
    "PRC-README-UC-CRITERIA",
    "PRC-GELC-GEOMETRY",
    "PRC-RLEM-LITERATURE",
    "PRC-CIRCULATOR-PHYSICAL",
    "PRC-RALA-RECONFIGURATION",
    "PRC-UC-FORMAL-MODEL",
    "PRC-ASM-SIMULATOR",
    "PRC-SCHEMATIC-FIGURES",
)

VALID_HARDWARE_ROLES = {
    "abstract-cell-requirements",
    "executable-transition-semantics",
    "formal-transition-model",
    "geometric-circuit-model",
    "physical-implementation-candidate",
    "prior-art-reconfiguration",
    "reversible-logic-foundation",
    "schematic-source",
}

REQUIRED_WITNESS_FIELDS = (
    "witness_id",
    "source_id",
    "local_witness",
    "locus",
    "hardware_role",
    "summary",
    "as_relevance",
    "simulation_constraint",
    "next_as_action",
)


@dataclass(frozen=True)
class PRCHardwareWitness:
    """One PRC source anchor relevant to hardware or schematic evidence."""

    witness_id: str
    source_id: str
    local_witness: Path
    locus: str
    hardware_role: str
    summary: str
    as_relevance: tuple[str, ...]
    simulation_constraint: str
    next_as_action: str


@dataclass(frozen=True)
class PRCHardwareWitnessMap:
    """Loaded map of PRC hardware witnesses and next artifact target."""

    schema_version: int
    reviewed_at: str
    reviewed_commit: str
    purpose: str
    recommended_next_artifact: str
    witnesses: tuple[PRCHardwareWitness, ...]

    def witnesses_by_id(self) -> dict[str, PRCHardwareWitness]:
        """Index witnesses by their stable witness IDs."""

        return {witness.witness_id: witness for witness in self.witnesses}

    def without_witness(self, witness_id: str) -> "PRCHardwareWitnessMap":
        """Return a copy without one witness for negative validation tests."""

        return replace(
            self,
            witnesses=tuple(
                witness
                for witness in self.witnesses
                if witness.witness_id != witness_id
            ),
        )


@dataclass(frozen=True)
class PRCHardwareValidation:
    """One validation result for the PRC hardware witness map."""

    subject: str
    accepted: bool
    detail: str


def load_prc_hardware_witness_map(path: Path | str) -> PRCHardwareWitnessMap:
    """Load the PRC hardware witness map from JSON."""

    map_path = Path(path)
    data = json.loads(map_path.read_text(encoding="utf-8"))
    witnesses = data.get("witnesses")
    if not isinstance(witnesses, list):
        raise ValueError("PRC hardware witness map must contain a witnesses list")

    return PRCHardwareWitnessMap(
        schema_version=_required_int(data, "schema_version"),
        reviewed_at=_required_text(data, "reviewed_at"),
        reviewed_commit=_required_text(data, "reviewed_commit"),
        purpose=_required_text(data, "purpose"),
        recommended_next_artifact=_required_text(
            data, "recommended_next_artifact"
        ),
        witnesses=tuple(_parse_witness(witness) for witness in witnesses),
    )


def validate_prc_hardware_witness_map(
    witness_map: PRCHardwareWitnessMap,
    *,
    required_witness_ids: Iterable[str] = REQUIRED_WITNESS_IDS,
    witness_root: Path | str = Path("/home/sean/Projects/_upstream/prc"),
    require_existing_witnesses: bool = False,
) -> list[PRCHardwareValidation]:
    """Validate coverage, source paths, uniqueness, and AS relevance."""

    root = Path(witness_root).resolve()
    results: list[PRCHardwareValidation] = []
    witnesses_by_id = witness_map.witnesses_by_id()

    for witness_id in required_witness_ids:
        if witness_id not in witnesses_by_id:
            results.append(_rejected(witness_id, "missing required witness"))
        else:
            results.append(_accepted(witness_id, "required witness present"))

    duplicate_ids = _duplicates([witness.witness_id for witness in witness_map.witnesses])
    if duplicate_ids:
        results.append(
            _rejected("witness_id", f"duplicate witness ids: {', '.join(duplicate_ids)}")
        )
    else:
        results.append(_accepted("witness_id", "witness ids are unique"))

    duplicate_loci = _duplicates(
        [
            f"{witness.source_id}:{witness.locus}"
            for witness in witness_map.witnesses
        ]
    )
    if duplicate_loci:
        results.append(
            _rejected("locus", f"duplicate source loci: {', '.join(duplicate_loci)}")
        )
    else:
        results.append(_accepted("locus", "source loci are unique"))

    if not witness_map.recommended_next_artifact:
        results.append(
            _rejected("recommended_next_artifact", "missing recommended artifact")
        )
    else:
        results.append(
            _accepted("recommended_next_artifact", "recommended artifact present")
        )

    for witness in witness_map.witnesses:
        results.extend(
            _validate_witness(witness, root, require_existing_witnesses)
        )

    return results


def _parse_witness(item: dict[str, Any]) -> PRCHardwareWitness:
    for field in REQUIRED_WITNESS_FIELDS:
        if field not in item:
            raise ValueError(f"PRC hardware witness missing field: {field}")

    relevance = item["as_relevance"]
    if not isinstance(relevance, list) or not relevance:
        raise ValueError("PRC hardware witness as_relevance must be non-empty")

    return PRCHardwareWitness(
        witness_id=_required_text(item, "witness_id"),
        source_id=_required_text(item, "source_id"),
        local_witness=Path(_required_text(item, "local_witness")),
        locus=_required_text(item, "locus"),
        hardware_role=_required_text(item, "hardware_role"),
        summary=_required_text(item, "summary"),
        as_relevance=tuple(_text_items(relevance, "as_relevance")),
        simulation_constraint=_required_text(item, "simulation_constraint"),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _validate_witness(
    witness: PRCHardwareWitness,
    witness_root: Path,
    require_existing_witnesses: bool,
) -> list[PRCHardwareValidation]:
    results: list[PRCHardwareValidation] = []

    if witness.hardware_role not in VALID_HARDWARE_ROLES:
        results.append(
            _rejected(
                witness.witness_id,
                f"unknown hardware role: {witness.hardware_role}",
            )
        )
    else:
        results.append(_accepted(witness.witness_id, "hardware role known"))

    path = witness.local_witness.expanduser().resolve()
    if not path.is_relative_to(witness_root):
        results.append(
            _rejected(
                witness.witness_id,
                f"witness outside expected PRC root: {path}",
            )
        )
    elif require_existing_witnesses and not path.exists():
        results.append(_rejected(witness.witness_id, f"missing witness: {path}"))
    else:
        results.append(_accepted(witness.witness_id, "local witness path pinned"))

    if not witness.simulation_constraint:
        results.append(_rejected(witness.witness_id, "missing simulation constraint"))
    else:
        results.append(_accepted(witness.witness_id, "simulation constraint present"))

    if not all(
        relevance.startswith("AFS-R") or relevance.startswith("P")
        for relevance in witness.as_relevance
    ):
        results.append(
            _rejected(
                witness.witness_id,
                "AS relevance must cite AFS requirements or open-problem IDs",
            )
        )
    else:
        results.append(_accepted(witness.witness_id, "AS relevance is explicit"))

    if not witness.next_as_action:
        results.append(_rejected(witness.witness_id, "missing next AS action"))
    else:
        results.append(_accepted(witness.witness_id, "next AS action present"))

    return results


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _text_items(values: list[Any], field: str) -> list[str]:
    text_values: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value:
            raise ValueError(f"{field} contains non-text item")
        text_values.append(value)
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


def _accepted(subject: str, detail: str) -> PRCHardwareValidation:
    return PRCHardwareValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> PRCHardwareValidation:
    return PRCHardwareValidation(subject=subject, accepted=False, detail=detail)
