"""Capture-avoiding substitution over AS formal code nodes.

This module performs the first checked substitution operation over the
canonical node dictionaries encoded by :mod:`autarkic_systems.formal_code`.
It is intentionally narrow: it substitutes term nodes for free variables,
respects binders, and rejects capture. It does not construct a fixed point,
prove a diagonal lemma, or check deductions.
"""

from __future__ import annotations

import argparse
import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.formal_code import (
    decode_code,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_EXAMPLES = Path("language/formal_substitution_examples.json")
DEFAULT_CODEBOOK = Path("language/formal_codebook.json")
DEFAULT_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
)

VALID_SEMANTICS = "capture-avoiding-free-variable-substitution"


@dataclass(frozen=True)
class SubstitutionExample:
    """One checked substitution example over formal code nodes."""

    example_id: str
    node: dict[str, Any]
    variable: str
    replacement: dict[str, Any]
    expected_node: dict[str, Any]
    expected_code: tuple[int, ...]


@dataclass(frozen=True)
class SubstitutionExampleSet:
    """Loaded substitution example manifest."""

    path: Path
    schema_version: int
    example_set_id: str
    reviewed_at: str
    purpose: str
    codebook_id: str
    semantics: str
    willard_anchor_ids: tuple[str, ...]
    examples: tuple[SubstitutionExample, ...]


@dataclass(frozen=True)
class SubstitutionValidation:
    """One validation result for the substitution surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionReport:
    """Validation report for substitution examples and code outputs."""

    examples: SubstitutionExampleSet
    codebook_path: Path
    language_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every substitution validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def example_count(self) -> int:
        """Return the number of checked substitution examples."""

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


def load_substitution_examples(
    path: Path | str = DEFAULT_EXAMPLES,
) -> SubstitutionExampleSet:
    """Load checked substitution examples from JSON."""

    examples_path = Path(path)
    data = json.loads(examples_path.read_text(encoding="utf-8"))
    return SubstitutionExampleSet(
        path=examples_path,
        schema_version=_required_int(data, "schema_version"),
        example_set_id=_required_text(data, "example_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        codebook_id=_required_text(data, "codebook_id"),
        semantics=_required_text(data, "semantics"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        examples=tuple(
            _parse_example(item) for item in _required_list(data, "examples")
        ),
    )


def validate_substitution_examples(
    examples: SubstitutionExampleSet,
    codebook_path: Path | str = DEFAULT_CODEBOOK,
    language_path: Path | str = DEFAULT_LANGUAGE,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionReport:
    """Validate substitution examples against the formal codebook."""

    checked_codebook_path = Path(codebook_path)
    checked_language_path = Path(language_path)
    checked_willard_map_path = Path(willard_map_path)
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}

    results: list[SubstitutionValidation] = [
        _accepted("examples", f"loaded {len(examples.examples)} example(s)")
    ]
    results.extend(_validate_codebook_reference(examples, codebook, codebook_report))
    results.extend(_validate_semantics(examples))
    results.extend(_validate_willard_anchors(examples, known_anchor_ids))
    results.extend(_validate_examples(examples, codebook))

    return SubstitutionReport(
        examples=examples,
        codebook_path=checked_codebook_path,
        language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
    )


def free_variables(node: dict[str, Any]) -> frozenset[str]:
    """Return the free variables in a canonical formal node."""

    kind = _node_kind(node)
    if kind == "variable":
        return frozenset({_required_text(node, "name")})
    if kind in {"zero", "sequence_nil"}:
        return frozenset()
    if kind == "successor":
        return free_variables(_required_node(node, "term"))
    if kind == "sequence_cons":
        return free_variables(_required_node(node, "head")) | free_variables(
            _required_node(node, "tail")
        )
    if kind in {"addition", "multiplication", "equals", "less_than", "and", "or", "implies"}:
        return free_variables(_required_node(node, "left")) | free_variables(
            _required_node(node, "right")
        )
    if kind == "not":
        return free_variables(_required_node(node, "body"))
    if kind in {"forall", "exists", "pi1", "sigma1"}:
        binder = _required_text(node, "variable")
        return free_variables(_required_node(node, "body")) - frozenset({binder})
    if kind in {"bounded_forall", "bounded_exists"}:
        binder = _required_text(node, "variable")
        return free_variables(_required_node(node, "bound")) | (
            free_variables(_required_node(node, "body")) - frozenset({binder})
        )
    if kind == "proof_line":
        return free_variables(_required_node(node, "formula"))
    raise ValueError(f"unknown node kind: {kind}")


def substitute_node(
    node: dict[str, Any],
    variable: str,
    replacement: dict[str, Any],
) -> dict[str, Any]:
    """Substitute a term for free occurrences of a variable in a node."""

    if not isinstance(variable, str) or not variable.strip():
        raise ValueError("substitution variable must be non-empty text")
    if not _is_term_node(replacement):
        raise ValueError("replacement must be a term node")
    return _substitute(node, variable, replacement)


def substitution_report_payload(report: SubstitutionReport) -> dict[str, Any]:
    """Return a JSON-ready substitution validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.examples.schema_version,
        "examples_path": str(report.examples.path),
        "example_set_id": report.examples.example_set_id,
        "reviewed_at": report.examples.reviewed_at,
        "purpose": report.examples.purpose,
        "codebook_path": str(report.codebook_path),
        "codebook_id": report.examples.codebook_id,
        "language_path": str(report.language_path),
        "willard_map": str(report.willard_map_path),
        "semantics": report.examples.semantics,
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


def format_substitution_report(report: SubstitutionReport) -> str:
    """Format a concise human-readable substitution report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Formal substitution: {status}",
        f"Examples: {report.examples.example_set_id}",
        f"Codebook: {report.examples.codebook_id}",
        f"Semantics: {report.examples.semantics}",
        f"Example count: {report.example_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
        "Validation:",
    ]
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_cli(argv: list[str] | None = None) -> int:
    """Run the formal substitution validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.formal_substitution",
        description="Validate the AS formal substitution examples.",
    )
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES),
        help="Path to the formal substitution example manifest.",
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

    examples = load_substitution_examples(args.examples)
    report = validate_substitution_examples(
        examples,
        args.codebook,
        args.language,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(substitution_report_payload(report), sort_keys=True))
    else:
        print(format_substitution_report(report))
    return 0 if report.accepted else 1


def _substitute(
    node: dict[str, Any],
    variable: str,
    replacement: dict[str, Any],
) -> dict[str, Any]:
    kind = _node_kind(node)
    if kind == "variable":
        if _required_text(node, "name") == variable:
            return _clone_node(replacement)
        return _clone_node(node)
    if kind in {"zero", "sequence_nil"}:
        return _clone_node(node)
    if kind == "successor":
        return {
            "kind": "successor",
            "term": _substitute(_required_node(node, "term"), variable, replacement),
        }
    if kind == "sequence_cons":
        return {
            "kind": "sequence_cons",
            "head": _substitute(_required_node(node, "head"), variable, replacement),
            "tail": _substitute(_required_node(node, "tail"), variable, replacement),
        }
    if kind in {"addition", "multiplication", "equals", "less_than", "and", "or", "implies"}:
        return {
            "kind": kind,
            "left": _substitute(_required_node(node, "left"), variable, replacement),
            "right": _substitute(_required_node(node, "right"), variable, replacement),
        }
    if kind == "not":
        return {
            "kind": "not",
            "body": _substitute(_required_node(node, "body"), variable, replacement),
        }
    if kind in {"forall", "exists", "pi1", "sigma1"}:
        return _substitute_binder(node, variable, replacement)
    if kind in {"bounded_forall", "bounded_exists"}:
        return _substitute_bounded_binder(node, variable, replacement)
    if kind == "proof_line":
        return {
            "kind": "proof_line",
            "line": _required_positive_int(node, "line"),
            "rule": _required_text(node, "rule"),
            "formula": _substitute(
                _required_node(node, "formula"),
                variable,
                replacement,
            ),
            "premises": _required_int_list(node, "premises"),
        }
    raise ValueError(f"unknown node kind: {kind}")


def _substitute_binder(
    node: dict[str, Any],
    variable: str,
    replacement: dict[str, Any],
) -> dict[str, Any]:
    kind = _node_kind(node)
    binder = _required_text(node, "variable")
    body = _required_node(node, "body")
    if binder == variable:
        return {"kind": kind, "variable": binder, "body": _clone_node(body)}
    _reject_capture_if_needed(binder, body, variable, replacement)
    return {
        "kind": kind,
        "variable": binder,
        "body": _substitute(body, variable, replacement),
    }


def _substitute_bounded_binder(
    node: dict[str, Any],
    variable: str,
    replacement: dict[str, Any],
) -> dict[str, Any]:
    kind = _node_kind(node)
    binder = _required_text(node, "variable")
    bound = _required_node(node, "bound")
    body = _required_node(node, "body")
    substituted_bound = _substitute(bound, variable, replacement)
    if binder == variable:
        return {
            "kind": kind,
            "variable": binder,
            "bound": substituted_bound,
            "body": _clone_node(body),
        }
    _reject_capture_if_needed(binder, body, variable, replacement)
    return {
        "kind": kind,
        "variable": binder,
        "bound": substituted_bound,
        "body": _substitute(body, variable, replacement),
    }


def _reject_capture_if_needed(
    binder: str,
    body: dict[str, Any],
    variable: str,
    replacement: dict[str, Any],
) -> None:
    if variable in free_variables(body) and binder in free_variables(replacement):
        raise ValueError(f"substitution would capture variable: {binder}")


def _validate_codebook_reference(
    examples: SubstitutionExampleSet,
    codebook: Any,
    codebook_report: Any,
) -> list[SubstitutionValidation]:
    if examples.codebook_id != codebook.codebook_id:
        return [
            _rejected(
                "codebook",
                f"examples codebook {examples.codebook_id} does not match "
                f"{codebook.codebook_id}",
            )
        ]
    if not codebook_report.accepted:
        return [
            _rejected(
                "codebook",
                "formal codebook rejected: "
                + _joined_or_none(codebook_report.failed_subjects),
            )
        ]
    return [_accepted("codebook", "formal codebook accepted")]


def _validate_semantics(
    examples: SubstitutionExampleSet,
) -> list[SubstitutionValidation]:
    if examples.semantics == VALID_SEMANTICS:
        return [_accepted("semantics", VALID_SEMANTICS)]
    return [_rejected("semantics", f"unknown semantics: {examples.semantics}")]


def _validate_willard_anchors(
    examples: SubstitutionExampleSet,
    known_anchor_ids: set[str],
) -> list[SubstitutionValidation]:
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
    examples: SubstitutionExampleSet,
    codebook: Any,
) -> list[SubstitutionValidation]:
    if not examples.examples:
        return [_rejected("examples", "substitution examples must not be empty")]

    failures: list[SubstitutionValidation] = []
    for example in examples.examples:
        try:
            substituted = substitute_node(
                example.node,
                example.variable,
                example.replacement,
            )
            if substituted != example.expected_node:
                failures.append(
                    _rejected(
                        f"example.{example.example_id}",
                        "expected node mismatch",
                    )
                )
                continue
            encoded = encode_node(substituted, codebook)
            if encoded != example.expected_code:
                failures.append(
                    _rejected(
                        f"example.{example.example_id}",
                        "expected code mismatch: expected "
                        + _format_code(example.expected_code)
                        + " got "
                        + _format_code(encoded),
                    )
                )
                continue
            decoded = decode_code(example.expected_code, codebook)
            if decoded != example.expected_node:
                failures.append(
                    _rejected(
                        f"example.{example.example_id}",
                        "expected code did not decode to expected node",
                    )
                )
        except ValueError as exc:
            failures.append(_rejected(f"example.{example.example_id}", str(exc)))
    if failures:
        return failures
    return [_accepted("examples", f"validated {len(examples.examples)} example(s)")]


def _parse_example(item: dict[str, Any]) -> SubstitutionExample:
    return SubstitutionExample(
        example_id=_required_text(item, "example_id"),
        node=_required_node(item, "node"),
        variable=_required_text(item, "variable"),
        replacement=_required_node(item, "replacement"),
        expected_node=_required_node(item, "expected_node"),
        expected_code=tuple(_required_int_list(item, "expected_code")),
    )


def _node_kind(node: dict[str, Any]) -> str:
    return _required_text(node, "kind")


def _is_term_node(node: dict[str, Any]) -> bool:
    kind = _node_kind(node)
    if kind in {"variable", "zero", "sequence_nil"}:
        return True
    if kind == "successor":
        return _is_term_node(_required_node(node, "term"))
    if kind == "sequence_cons":
        return _is_term_node(_required_node(node, "head")) and _is_term_node(
            _required_node(node, "tail")
        )
    if kind in {"addition", "multiplication"}:
        return _is_term_node(_required_node(node, "left")) and _is_term_node(
            _required_node(node, "right")
        )
    return False


def _clone_node(node: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(node)


def _failed_subject_for_result(subject: str) -> str:
    if subject in {"codebook", "semantics"}:
        return "formal-substitution-manifest"
    if subject == "willard_anchors":
        return "formal-substitution-willard-anchor"
    if subject.startswith("example") or subject == "examples":
        return "formal-substitution-example"
    return "formal-substitution"


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


def _required_positive_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"required positive integer field missing: {key}")
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


def _required_node(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required node field missing: {key}")
    return value


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


def _format_code(code: tuple[int, ...]) -> str:
    return "[" + ", ".join(str(value) for value in code) + "]"


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> SubstitutionValidation:
    return SubstitutionValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> SubstitutionValidation:
    return SubstitutionValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_substitution_cli())
