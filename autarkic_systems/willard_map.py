"""Structured Willard definition-map support.

The map validated by this module is a research index, not a proof checker. Its
job is to keep AS's formal-confidence claims tied to exact Willard source
anchors before later ADRs attempt an object language, proof-code encoding, or
self-consistency claim.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable


REQUIRED_CORE_SOURCES = (
    "Willard2001",
    "Willard2011",
    "Willard2016",
    "Willard2020",
)

VALID_ANCHOR_KINDS = {
    "boundary",
    "conjecture",
    "construction",
    "definition",
    "theorem",
}

REQUIRED_ANCHOR_FIELDS = (
    "anchor_id",
    "source_id",
    "year",
    "title",
    "local_witness",
    "locus",
    "kind",
    "summary",
    "as_relevance",
    "next_as_action",
)


@dataclass(frozen=True)
class WillardAnchor:
    """One source-local definition, theorem, or construction AS must track."""

    anchor_id: str
    source_id: str
    year: int
    title: str
    local_witness: Path
    locus: str
    kind: str
    summary: str
    as_relevance: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class WillardDefinitionMap:
    """Loaded map of Willard anchors relevant to AS formal confidence."""

    schema_version: int
    reviewed_at: str
    purpose: str
    anchors: tuple[WillardAnchor, ...]

    def anchors_by_source(self) -> dict[str, tuple[WillardAnchor, ...]]:
        """Group anchors by Willard source ID."""

        grouped: dict[str, list[WillardAnchor]] = {}
        for anchor in self.anchors:
            grouped.setdefault(anchor.source_id, []).append(anchor)
        return {
            source_id: tuple(source_anchors)
            for source_id, source_anchors in grouped.items()
        }

    def without_source(self, source_id: str) -> "WillardDefinitionMap":
        """Return a copy without anchors from one source for negative tests."""

        return replace(
            self,
            anchors=tuple(
                anchor for anchor in self.anchors if anchor.source_id != source_id
            ),
        )


@dataclass(frozen=True)
class WillardMapValidation:
    """One validation result for the structured Willard map."""

    subject: str
    accepted: bool
    detail: str


def load_willard_definition_map(path: Path | str) -> WillardDefinitionMap:
    """Load a structured Willard definition map from JSON."""

    map_path = Path(path)
    data = json.loads(map_path.read_text(encoding="utf-8"))
    anchors = data.get("anchors")
    if not isinstance(anchors, list):
        raise ValueError("Willard definition map must contain an anchors list")

    return WillardDefinitionMap(
        schema_version=_required_int(data, "schema_version"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        anchors=tuple(_parse_anchor(anchor) for anchor in anchors),
    )


def validate_willard_definition_map(
    definition_map: WillardDefinitionMap,
    *,
    required_sources: Iterable[str] = REQUIRED_CORE_SOURCES,
    witness_root: Path | str = Path("/home/sean/Projects/_upstream/sjas"),
    require_existing_witnesses: bool = False,
) -> list[WillardMapValidation]:
    """Validate coverage, uniqueness, local witnesses, and AS relevance."""

    root = Path(witness_root).resolve()
    results: list[WillardMapValidation] = []
    anchors_by_source = definition_map.anchors_by_source()

    for source_id in required_sources:
        if source_id not in anchors_by_source:
            results.append(_rejected(source_id, "missing required source anchors"))
        else:
            results.append(_accepted(source_id, "required source anchors present"))

    anchor_ids = [anchor.anchor_id for anchor in definition_map.anchors]
    duplicate_anchor_ids = _duplicates(anchor_ids)
    if duplicate_anchor_ids:
        results.append(
            _rejected(
                "anchor_id",
                f"duplicate anchor ids: {', '.join(duplicate_anchor_ids)}",
            )
        )
    else:
        results.append(_accepted("anchor_id", "anchor ids are unique"))

    loci = [(anchor.source_id, anchor.locus) for anchor in definition_map.anchors]
    duplicate_loci = _duplicates([f"{source_id}:{locus}" for source_id, locus in loci])
    if duplicate_loci:
        results.append(
            _rejected("locus", f"duplicate source loci: {', '.join(duplicate_loci)}")
        )
    else:
        results.append(_accepted("locus", "source loci are unique"))

    for anchor in definition_map.anchors:
        results.extend(_validate_anchor(anchor, root, require_existing_witnesses))

    return results


def _parse_anchor(item: dict[str, Any]) -> WillardAnchor:
    for field in REQUIRED_ANCHOR_FIELDS:
        if field not in item:
            raise ValueError(f"Willard anchor missing field: {field}")

    relevance = item["as_relevance"]
    if not isinstance(relevance, list) or not relevance:
        raise ValueError("Willard anchor as_relevance must be a non-empty list")

    return WillardAnchor(
        anchor_id=_required_text(item, "anchor_id"),
        source_id=_required_text(item, "source_id"),
        year=_required_int(item, "year"),
        title=_required_text(item, "title"),
        local_witness=Path(_required_text(item, "local_witness")),
        locus=_required_text(item, "locus"),
        kind=_required_text(item, "kind"),
        summary=_required_text(item, "summary"),
        as_relevance=tuple(_text_items(relevance, "as_relevance")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _validate_anchor(
    anchor: WillardAnchor, witness_root: Path, require_existing_witnesses: bool
) -> list[WillardMapValidation]:
    results: list[WillardMapValidation] = []

    if anchor.kind not in VALID_ANCHOR_KINDS:
        results.append(_rejected(anchor.anchor_id, f"unknown anchor kind: {anchor.kind}"))
    else:
        results.append(_accepted(anchor.anchor_id, "anchor kind known"))

    witness = anchor.local_witness.expanduser().resolve()
    if not witness.is_relative_to(witness_root):
        results.append(
            _rejected(
                anchor.anchor_id,
                f"witness outside expected SJAS root: {witness}",
            )
        )
    elif require_existing_witnesses and not witness.exists():
        results.append(_rejected(anchor.anchor_id, f"missing witness: {witness}"))
    else:
        results.append(_accepted(anchor.anchor_id, "local witness path pinned"))

    if not anchor.as_relevance:
        results.append(_rejected(anchor.anchor_id, "missing AS relevance"))
    elif not all(item.startswith("AFS-R") or item.startswith("P") for item in anchor.as_relevance):
        results.append(
            _rejected(
                anchor.anchor_id,
                "AS relevance must cite AFS requirements or open-problem IDs",
            )
        )
    else:
        results.append(_accepted(anchor.anchor_id, "AS relevance is explicit"))

    if not anchor.next_as_action:
        results.append(_rejected(anchor.anchor_id, "missing next AS action"))
    else:
        results.append(_accepted(anchor.anchor_id, "next AS action present"))

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


def _accepted(subject: str, detail: str) -> WillardMapValidation:
    return WillardMapValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> WillardMapValidation:
    return WillardMapValidation(subject=subject, accepted=False, detail=detail)
