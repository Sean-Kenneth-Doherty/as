"""Formal quotation sequence helpers for AS code-token numerals.

This module wraps the token numerals from :mod:`autarkic_systems.formal_quotation`
into a checked sequence object. The object is still a manifest-level surface,
not an arithmetic-language pair/list term and not a full quotation term for a
formula code.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.formal_quotation import (
    load_quotation_examples,
    numeral_to_natural,
    quote_code_tokens,
    validate_quotation_examples,
)
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_EXAMPLES = Path("language/formal_quotation_sequence_examples.json")
DEFAULT_CODEBOOK = Path("language/formal_codebook.json")
DEFAULT_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
)
VALID_SEQUENCE_KIND = "token-numeral-sequence"
VALID_SEQUENCE_STATUS = "token-numeral-sequence-only"


@dataclass(frozen=True)
class QuotationSequenceExample:
    """One checked token-numeral sequence example."""

    example_id: str
    tokens: tuple[int, ...]
    expected_token_count: int
    expected_first_token_depth: int
    expected_last_token_depth: int
    status: str


@dataclass(frozen=True)
class QuotationSequenceExampleSet:
    """Loaded token-numeral sequence quotation examples."""

    path: Path
    schema_version: int
    sequence_set_id: str
    reviewed_at: str
    purpose: str
    quotation_examples_path: str
    fixed_point_targets_path: str
    sequence_kind: str
    willard_anchor_ids: tuple[str, ...]
    examples: tuple[QuotationSequenceExample, ...]


@dataclass(frozen=True)
class QuotationSequenceValidation:
    """One validation result for the sequence quotation surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class QuotationSequenceReport:
    """Validation report for token-numeral sequence quotation examples."""

    examples: QuotationSequenceExampleSet
    codebook_path: Path
    language_path: Path
    willard_map_path: Path
    results: tuple[QuotationSequenceValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every sequence quotation validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def example_count(self) -> int:
        """Return the number of checked sequence quotation examples."""

        return len(self.examples.examples)

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return compact failure subjects for automation and reports."""

        subjects: list[str] = []
        for result in self.results:
            if result.accepted:
                continue
            subject = _failed_subject_for_result(result.subject)
            if subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)


def quote_token_sequence(tokens: tuple[int, ...] | list[int]) -> dict[str, Any]:
    """Return a manifest-level sequence object of quoted token numerals."""

    numerals = quote_code_tokens(tokens)
    return {
        "kind": VALID_SEQUENCE_KIND,
        "token_count": len(numerals),
        "items": list(numerals),
    }


def load_quotation_sequence_examples(
    path: Path | str = DEFAULT_EXAMPLES,
) -> QuotationSequenceExampleSet:
    """Load checked token-numeral sequence examples from JSON."""

    examples_path = Path(path)
    data = json.loads(examples_path.read_text(encoding="utf-8"))
    return QuotationSequenceExampleSet(
        path=examples_path,
        schema_version=_required_int(data, "schema_version"),
        sequence_set_id=_required_text(data, "sequence_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        quotation_examples_path=_required_text(data, "quotation_examples_path"),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        sequence_kind=_required_text(data, "sequence_kind"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        examples=tuple(
            _parse_example(item) for item in _required_list(data, "examples")
        ),
    )


def validate_quotation_sequence_examples(
    examples: QuotationSequenceExampleSet,
    codebook_path: Path | str = DEFAULT_CODEBOOK,
    language_path: Path | str = DEFAULT_LANGUAGE,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> QuotationSequenceReport:
    """Validate token-numeral sequence quotation examples."""

    checked_codebook_path = Path(codebook_path)
    checked_language_path = Path(language_path)
    checked_willard_map_path = Path(willard_map_path)
    quotation_examples = load_quotation_examples(examples.quotation_examples_path)
    quotation_report = validate_quotation_examples(
        quotation_examples,
        checked_codebook_path,
        checked_language_path,
        checked_willard_map_path,
    )
    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}

    results: list[QuotationSequenceValidation] = [
        _accepted("examples", f"loaded {len(examples.examples)} example(s)")
    ]
    results.extend(_validate_references(examples))
    results.extend(_validate_quotation_report(quotation_report))
    results.extend(_validate_sequence_kind(examples))
    results.extend(_validate_willard_anchors(examples, known_anchor_ids))
    results.extend(_validate_examples(examples))

    return QuotationSequenceReport(
        examples=examples,
        codebook_path=checked_codebook_path,
        language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
    )


def quotation_sequence_report_payload(
    report: QuotationSequenceReport,
) -> dict[str, Any]:
    """Return a JSON-ready sequence quotation validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.examples.schema_version,
        "examples_path": str(report.examples.path),
        "sequence_set_id": report.examples.sequence_set_id,
        "reviewed_at": report.examples.reviewed_at,
        "purpose": report.examples.purpose,
        "quotation_examples_path": report.examples.quotation_examples_path,
        "fixed_point_targets_path": report.examples.fixed_point_targets_path,
        "codebook_path": str(report.codebook_path),
        "language_path": str(report.language_path),
        "willard_map": str(report.willard_map_path),
        "sequence_kind": report.examples.sequence_kind,
        "willard_anchor_ids": list(report.examples.willard_anchor_ids),
        "example_count": report.example_count,
        "failed_subjects": list(report.failed_subjects),
        "result_count": len(report.results),
        "results": [
            {
                "subject": result.subject,
                "accepted": result.accepted,
                "detail": result.detail,
            }
            for result in report.results
        ],
    }


def format_quotation_sequence_report(report: QuotationSequenceReport) -> str:
    """Format a concise human-readable sequence quotation report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Formal quotation sequence: {status}",
        f"Examples: {report.examples.sequence_set_id}",
        f"Quotation examples: {report.examples.quotation_examples_path}",
        f"Sequence kind: {report.examples.sequence_kind}",
        f"Example count: {report.example_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
        "Validation:",
    ]
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_quotation_sequence_cli(argv: list[str] | None = None) -> int:
    """Run the sequence quotation validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.formal_quotation_sequence",
        description="Validate AS formal quotation sequence examples.",
    )
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES),
        help="Path to the quotation sequence example manifest.",
    )
    parser.add_argument(
        "--codebook",
        default=str(DEFAULT_CODEBOOK),
        help="Path to the formal codebook manifest.",
    )
    parser.add_argument(
        "--language",
        default=str(DEFAULT_LANGUAGE),
        help="Path to the formal arithmetic language manifest.",
    )
    parser.add_argument(
        "--willard-map",
        default=str(DEFAULT_WILLARD_MAP),
        help="Path to the Willard definition map.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    examples = load_quotation_sequence_examples(args.examples)
    report = validate_quotation_sequence_examples(
        examples,
        args.codebook,
        args.language,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(quotation_sequence_report_payload(report), sort_keys=True))
    else:
        print(format_quotation_sequence_report(report))
    return 0 if report.accepted else 1


def _validate_references(
    examples: QuotationSequenceExampleSet,
) -> list[QuotationSequenceValidation]:
    results: list[QuotationSequenceValidation] = []
    expected_quotation_path = "language/formal_quotation_examples.json"
    if examples.quotation_examples_path != expected_quotation_path:
        results.append(
            _rejected(
                "quotation_examples_path",
                "expected "
                + expected_quotation_path
                + " but found "
                + examples.quotation_examples_path,
            )
        )
    else:
        results.append(
            _accepted("quotation_examples_path", expected_quotation_path + " referenced")
        )

    expected_fixed_point_path = "claims/fixed_point_targets.json"
    if examples.fixed_point_targets_path != expected_fixed_point_path:
        results.append(
            _rejected(
                "fixed_point_targets_path",
                "expected "
                + expected_fixed_point_path
                + " but found "
                + examples.fixed_point_targets_path,
            )
        )
    else:
        results.append(
            _accepted(
                "fixed_point_targets_path",
                expected_fixed_point_path + " referenced",
            )
        )
    return results


def _validate_quotation_report(
    quotation_report: Any,
) -> list[QuotationSequenceValidation]:
    if quotation_report.accepted:
        return [_accepted("quotation", "formal quotation accepted")]
    return [
        _rejected(
            "quotation",
            "formal quotation rejected: "
            + _joined_or_none(quotation_report.failed_subjects),
        )
    ]


def _validate_sequence_kind(
    examples: QuotationSequenceExampleSet,
) -> list[QuotationSequenceValidation]:
    if examples.sequence_kind == VALID_SEQUENCE_KIND:
        return [_accepted("sequence_kind", VALID_SEQUENCE_KIND)]
    return [
        _rejected(
            "sequence_kind",
            f"unknown sequence kind: {examples.sequence_kind}",
        )
    ]


def _validate_willard_anchors(
    examples: QuotationSequenceExampleSet,
    known_anchor_ids: set[str],
) -> list[QuotationSequenceValidation]:
    unknown_anchor_ids = sorted(set(examples.willard_anchor_ids) - known_anchor_ids)
    missing_required = sorted(
        set(REQUIRED_WILLARD_ANCHORS) - set(examples.willard_anchor_ids)
    )
    if unknown_anchor_ids:
        return [
            _rejected(
                "willard_anchors",
                "unknown Willard anchor IDs: " + ", ".join(unknown_anchor_ids),
            )
        ]
    if missing_required:
        return [
            _rejected(
                "willard_anchors",
                "missing required Willard anchors: " + ", ".join(missing_required),
            )
        ]
    return [_accepted("willard_anchors", "required anchors are present and known")]


def _validate_examples(
    examples: QuotationSequenceExampleSet,
) -> list[QuotationSequenceValidation]:
    if not examples.examples:
        return [_rejected("examples", "quotation sequence examples must not be empty")]

    failures: list[QuotationSequenceValidation] = []
    for example in examples.examples:
        try:
            _validate_example(example)
        except ValueError as exc:
            failures.append(_rejected(f"example.{example.example_id}", str(exc)))
    if failures:
        return failures
    return [_accepted("examples", f"validated {len(examples.examples)} example(s)")]


def _validate_example(example: QuotationSequenceExample) -> None:
    if example.status != VALID_SEQUENCE_STATUS:
        raise ValueError(f"unknown sequence status: {example.status}")
    sequence = quote_token_sequence(example.tokens)
    if sequence["kind"] != VALID_SEQUENCE_KIND:
        raise ValueError(f"unexpected sequence kind: {sequence['kind']}")
    token_count = sequence["token_count"]
    if token_count != example.expected_token_count:
        raise ValueError(
            "expected token count mismatch: expected "
            + str(example.expected_token_count)
            + " got "
            + str(token_count)
        )
    first_depth = numeral_to_natural(sequence["items"][0])
    if first_depth != example.expected_first_token_depth:
        raise ValueError(
            "expected first token depth mismatch: expected "
            + str(example.expected_first_token_depth)
            + " got "
            + str(first_depth)
        )
    last_depth = numeral_to_natural(sequence["items"][-1])
    if last_depth != example.expected_last_token_depth:
        raise ValueError(
            "expected last token depth mismatch: expected "
            + str(example.expected_last_token_depth)
            + " got "
            + str(last_depth)
        )


def _parse_example(item: dict[str, Any]) -> QuotationSequenceExample:
    return QuotationSequenceExample(
        example_id=_required_text(item, "example_id"),
        tokens=tuple(_required_int_list(item, "tokens")),
        expected_token_count=_required_int(item, "expected_token_count"),
        expected_first_token_depth=_required_int(item, "expected_first_token_depth"),
        expected_last_token_depth=_required_int(item, "expected_last_token_depth"),
        status=_required_text(item, "status"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "formal-quotation-sequence-willard-anchor"
    if subject in {"quotation_examples_path", "fixed_point_targets_path"}:
        return "formal-quotation-sequence-reference"
    if subject in {"quotation", "sequence_kind"}:
        return "formal-quotation-sequence-manifest"
    if subject.startswith("example") or subject == "examples":
        return "formal-quotation-sequence-example"
    return "formal-quotation-sequence"


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"required integer field missing: {key}")
    return value


def _required_list(item: dict[str, Any], key: str) -> list[Any]:
    value = item.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"required list field missing: {key}")
    return value


def _required_text_list(item: dict[str, Any], key: str) -> list[str]:
    values = _required_list(item, key)
    text_values: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        text_values.append(value)
    return text_values


def _required_int_list(item: dict[str, Any], key: str) -> list[int]:
    value = item.get(key)
    if not isinstance(value, list):
        raise ValueError(f"required integer list missing: {key}")
    result: list[int] = []
    for list_item in value:
        if not isinstance(list_item, int) or isinstance(list_item, bool):
            raise ValueError(f"{key} contains non-integer item")
        result.append(list_item)
    return result


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> QuotationSequenceValidation:
    return QuotationSequenceValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> QuotationSequenceValidation:
    return QuotationSequenceValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_quotation_sequence_cli())
