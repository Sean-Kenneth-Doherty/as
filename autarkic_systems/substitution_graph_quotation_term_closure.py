"""Finite quotation-term closure domain for substitution graph evidence.

This module checks that the graph-domain code subjects currently exercised by
the substitution graph formula candidate and finite evaluation examples quote
to closed nested sequence terms. It is finite executable evidence for the
second correctness proof case, not a proof of general quotation closure.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from autarkic_systems.formal_code import (
    FormalCodebook,
    decode_code,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation import numeral_to_natural
from autarkic_systems.formal_quotation_term import (
    load_quotation_term_examples,
    quote_tokens_as_term,
    validate_quotation_term_examples,
)
from autarkic_systems.formal_substitution import free_variables
from autarkic_systems.substitution_graph_codebook_roundtrip import (
    derive_substitution_graph_code_subjects,
)
from autarkic_systems.substitution_graph_evaluation import (
    load_substitution_graph_evaluation_examples,
    validate_substitution_graph_evaluation_examples,
)
from autarkic_systems.substitution_graph_formula import (
    load_substitution_graph_formula_candidates,
    validate_substitution_graph_formula_candidates,
)


DEFAULT_CLOSURE = Path("claims/substitution_graph_quotation_term_closure.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = (
    "formula-candidate",
    "finite-evaluation",
)
REQUIRED_FUTURE_WORK = (
    "formula-correctness-proof",
    "substitution-representability-proof",
    "diagonal-lemma-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
REQUIRED_NON_CLAIMS = (
    "no formula correctness proof",
    "no substitution representability proof",
    "no diagonal lemma proof",
    "no fixed-point equation proof",
    "no self-consistency theorem",
)


@dataclass(frozen=True)
class SubstitutionGraphQuotationTermClosureManifest:
    """Loaded manifest for the current graph quotation-term closure domain."""

    path: Path
    schema_version: int
    closure_set_id: str
    reviewed_at: str
    purpose: str
    codebook_path: str
    quotation_term_examples_path: str
    formula_candidates_path: str
    evaluation_examples_path: str
    expected_subject_count: int
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphQuotationTermClosureValidation:
    """One validation result for graph quotation-term closure."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphQuotationTermClosureSubject:
    """One observed graph-domain quotation-term closure subject."""

    subject_id: str
    source_kind: str
    source_id: str
    code_role: str
    token_count: int
    term_code_length: int
    closed: bool
    tokens_recovered: bool
    code_roundtrip_ok: bool


@dataclass(frozen=True)
class SubstitutionGraphQuotationTermClosureReport:
    """Validation report over the finite quotation-term closure domain."""

    manifest: SubstitutionGraphQuotationTermClosureManifest
    codebook_path: Path
    quotation_term_examples_path: Path
    formula_candidates_path: Path
    evaluation_examples_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionGraphQuotationTermClosureValidation, ...]
    subjects: tuple[SubstitutionGraphQuotationTermClosureSubject, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every closure validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def subject_count(self) -> int:
        """Return the number of checked quotation-term closure subjects."""

        return len(self.subjects)

    @property
    def source_kind_counts(self) -> dict[str, int]:
        """Return observed subject counts grouped by source kind."""

        counts = {source_kind: 0 for source_kind in REQUIRED_SOURCE_KINDS}
        for subject in self.subjects:
            counts[subject.source_kind] = counts.get(subject.source_kind, 0) + 1
        return counts

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


def load_substitution_graph_quotation_term_closure(
    path: Path | str = DEFAULT_CLOSURE,
) -> SubstitutionGraphQuotationTermClosureManifest:
    """Load the graph quotation-term closure manifest from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return SubstitutionGraphQuotationTermClosureManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        closure_set_id=_required_text(data, "closure_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        codebook_path=_required_text(data, "codebook_path"),
        quotation_term_examples_path=_required_text(
            data,
            "quotation_term_examples_path",
        ),
        formula_candidates_path=_required_text(data, "formula_candidates_path"),
        evaluation_examples_path=_required_text(data, "evaluation_examples_path"),
        expected_subject_count=_required_int(data, "expected_subject_count"),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_quotation_term_closure(
    manifest: SubstitutionGraphQuotationTermClosureManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphQuotationTermClosureReport:
    """Validate finite graph-domain quotation-term closure."""

    checked_willard_map_path = Path(willard_map_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_quotation_path = Path(manifest.quotation_term_examples_path)
    checked_formula_path = Path(manifest.formula_candidates_path)
    checked_evaluation_path = Path(manifest.evaluation_examples_path)

    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        willard_map_path=checked_willard_map_path,
    )
    quotation_terms = load_quotation_term_examples(checked_quotation_path)
    quotation_report = validate_quotation_term_examples(
        quotation_terms,
        checked_codebook_path,
        willard_map_path=checked_willard_map_path,
    )
    formula_manifest = load_substitution_graph_formula_candidates(checked_formula_path)
    formula_report = validate_substitution_graph_formula_candidates(
        formula_manifest,
        checked_willard_map_path,
    )
    evaluation_manifest = load_substitution_graph_evaluation_examples(
        checked_evaluation_path,
    )
    evaluation_report = validate_substitution_graph_evaluation_examples(
        evaluation_manifest,
        checked_willard_map_path,
    )

    results: list[SubstitutionGraphQuotationTermClosureValidation] = [
        _accepted("manifest", f"loaded {manifest.closure_set_id}")
    ]
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            codebook_report,
            quotation_report,
            formula_report,
            evaluation_report,
        )
    )
    subjects: list[SubstitutionGraphQuotationTermClosureSubject] = []
    try:
        code_subjects = derive_substitution_graph_code_subjects(
            formula_manifest.candidates,
            evaluation_manifest.examples,
            codebook,
            formula_manifest.substitution_representability_targets_path,
            checked_willard_map_path,
        )
        subjects = [
            _closure_subject(code_subject, codebook)
            for code_subject in code_subjects
        ]
    except ValueError as exc:
        results.append(_rejected("closure_subjects", str(exc)))

    results.extend(_validate_subject_set(manifest, tuple(subjects)))

    return SubstitutionGraphQuotationTermClosureReport(
        manifest=manifest,
        codebook_path=checked_codebook_path,
        quotation_term_examples_path=checked_quotation_path,
        formula_candidates_path=checked_formula_path,
        evaluation_examples_path=checked_evaluation_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        subjects=tuple(subjects),
    )


def substitution_graph_quotation_term_closure_report_payload(
    report: SubstitutionGraphQuotationTermClosureReport,
) -> dict[str, Any]:
    """Return a JSON-ready quotation-term closure payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "closure_manifest": str(report.manifest.path),
        "closure_set_id": report.manifest.closure_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "codebook_path": str(report.codebook_path),
        "quotation_term_examples_path": str(report.quotation_term_examples_path),
        "formula_candidates_path": str(report.formula_candidates_path),
        "evaluation_examples_path": str(report.evaluation_examples_path),
        "willard_map": str(report.willard_map_path),
        "expected_subject_count": report.manifest.expected_subject_count,
        "subject_count": report.subject_count,
        "source_kind_counts": report.source_kind_counts,
        "required_source_kinds": list(report.manifest.required_source_kinds),
        "required_future_work": list(report.manifest.required_future_work),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "subjects": [
            {
                "subject_id": subject.subject_id,
                "source_kind": subject.source_kind,
                "source_id": subject.source_id,
                "code_role": subject.code_role,
                "observed_token_count": subject.token_count,
                "observed_term_code_length": subject.term_code_length,
                "observed_closed": subject.closed,
                "observed_tokens_recovered": subject.tokens_recovered,
                "observed_code_roundtrip_ok": subject.code_roundtrip_ok,
            }
            for subject in report.subjects
        ],
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


def format_substitution_graph_quotation_term_closure_report(
    report: SubstitutionGraphQuotationTermClosureReport,
) -> str:
    """Format a concise human-readable quotation-term closure report."""

    status = "accepted" if report.accepted else "rejected"
    failures = [
        subject.subject_id
        for subject in report.subjects
        if not (
            subject.closed
            and subject.tokens_recovered
            and subject.code_roundtrip_ok
        )
    ]
    source_counts = ", ".join(
        f"{source_kind}={count}"
        for source_kind, count in report.source_kind_counts.items()
    )
    lines = [
        f"Substitution graph quotation term closure: {status}",
        f"Closure set: {report.manifest.closure_set_id}",
        f"Subjects: {report.subject_count}",
        f"Source kinds: {source_counts}",
        f"Closure failures: {_joined_or_none(tuple(failures))}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_quotation_term_closure_cli(
    argv: list[str] | None = None,
) -> int:
    """Run finite graph-domain quotation-term closure validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.substitution_graph_quotation_term_closure",
        description="Validate substitution graph quotation-term closure subjects.",
    )
    parser.add_argument(
        "--closure",
        default=str(DEFAULT_CLOSURE),
        help="Path to the graph quotation-term closure manifest.",
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

    manifest = load_substitution_graph_quotation_term_closure(args.closure)
    report = validate_substitution_graph_quotation_term_closure(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(substitution_graph_quotation_term_closure_report_payload(report), sort_keys=True))
    else:
        print(format_substitution_graph_quotation_term_closure_report(report))
    return 0 if report.accepted else 1


def _closure_subject(
    code_subject: Any,
    codebook: FormalCodebook,
) -> SubstitutionGraphQuotationTermClosureSubject:
    term = quote_tokens_as_term(code_subject.code)
    recursion_limit = _recursion_limit_for_quotation_code(code_subject.code)
    with _expanded_recursion_limit(recursion_limit):
        encoded_term = encode_node(term, codebook)
        decoded_term = decode_code(encoded_term, codebook)
        closed = not free_variables(term)
        code_roundtrip_ok = decoded_term == term
    recovered_tokens = _tokens_from_quotation_term(term)
    return SubstitutionGraphQuotationTermClosureSubject(
        subject_id=code_subject.subject_id,
        source_kind=code_subject.source_kind,
        source_id=code_subject.source_id,
        code_role=code_subject.code_role,
        token_count=len(recovered_tokens),
        term_code_length=len(encoded_term),
        closed=closed,
        tokens_recovered=recovered_tokens == code_subject.code,
        code_roundtrip_ok=code_roundtrip_ok,
    )


def _tokens_from_quotation_term(term: dict[str, Any]) -> tuple[int, ...]:
    tokens: list[int] = []
    current = term
    while True:
        kind = _node_kind(current)
        if kind == "sequence_nil":
            return tuple(tokens)
        if kind != "sequence_cons":
            raise ValueError(f"unexpected quotation term node: {kind}")
        tokens.append(numeral_to_natural(_required_node(current, "head")))
        current = _required_node(current, "tail")


def _recursion_limit_for_quotation_code(code: tuple[int, ...]) -> int:
    """Return a local recursion budget for deeply nested quotation terms."""

    max_token_depth = max(code, default=0)
    return max(sys.getrecursionlimit(), (len(code) * 2) + max_token_depth + 1000)


@contextmanager
def _expanded_recursion_limit(limit: int) -> Iterator[None]:
    """Temporarily raise recursion depth for one finite deep-term check."""

    previous = sys.getrecursionlimit()
    if limit > previous:
        sys.setrecursionlimit(limit)
    try:
        yield
    finally:
        if limit > previous:
            sys.setrecursionlimit(previous)


def _validate_references(
    manifest: SubstitutionGraphQuotationTermClosureManifest,
) -> list[SubstitutionGraphQuotationTermClosureValidation]:
    expected = (
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "quotation_term_examples_path",
            manifest.quotation_term_examples_path,
            "language/formal_quotation_term_examples.json",
        ),
        (
            "formula_candidates_path",
            manifest.formula_candidates_path,
            "claims/substitution_graph_formula_candidates.json",
        ),
        (
            "evaluation_examples_path",
            manifest.evaluation_examples_path,
            "claims/substitution_graph_evaluation_examples.json",
        ),
    )
    results: list[SubstitutionGraphQuotationTermClosureValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_dependency_reports(
    codebook_report: Any,
    quotation_report: Any,
    formula_report: Any,
    evaluation_report: Any,
) -> list[SubstitutionGraphQuotationTermClosureValidation]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        ("quotation_term", quotation_report, "formal quotation term"),
        ("formula_candidates", formula_report, "substitution graph formula"),
        ("evaluation_examples", evaluation_report, "substitution graph evaluation"),
    )
    results: list[SubstitutionGraphQuotationTermClosureValidation] = []
    for subject, report, label in checks:
        if report.accepted:
            results.append(_accepted(subject, f"{label} accepted"))
        else:
            results.append(
                _rejected(
                    subject,
                    f"{label} rejected: " + _joined_or_none(report.failed_subjects),
                )
            )
    return results


def _validate_subject_set(
    manifest: SubstitutionGraphQuotationTermClosureManifest,
    subjects: tuple[SubstitutionGraphQuotationTermClosureSubject, ...],
) -> list[SubstitutionGraphQuotationTermClosureValidation]:
    results: list[SubstitutionGraphQuotationTermClosureValidation] = []
    subject_ids = [subject.subject_id for subject in subjects]
    duplicate_ids = _duplicates(subject_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "closure_subject_ids",
                "duplicate subject ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("closure_subject_ids", "subject ids are unique"))

    if len(subjects) != manifest.expected_subject_count:
        results.append(
            _rejected(
                "expected_subject_count",
                "subject count mismatch: expected "
                + str(manifest.expected_subject_count)
                + " got "
                + str(len(subjects)),
            )
        )
    else:
        results.append(
            _accepted(
                "expected_subject_count",
                f"checked {len(subjects)} subject(s)",
            )
        )

    source_kinds = {subject.source_kind for subject in subjects}
    missing_source_kinds = [
        source_kind
        for source_kind in REQUIRED_SOURCE_KINDS
        if source_kind not in manifest.required_source_kinds
        or source_kind not in source_kinds
    ]
    if missing_source_kinds:
        results.append(
            _rejected(
                "required_source_kinds",
                "missing source kinds: " + ", ".join(missing_source_kinds),
            )
        )
    else:
        results.append(_accepted("required_source_kinds", "source kinds covered"))

    failures = [
        subject.subject_id
        for subject in subjects
        if not (
            subject.closed
            and subject.tokens_recovered
            and subject.code_roundtrip_ok
        )
    ]
    if failures:
        results.append(
            _rejected(
                "closure_subjects",
                "closure failures: " + ", ".join(failures),
            )
        )
    else:
        results.append(
            _accepted(
                "closure_subjects",
                f"closed {len(subjects)} graph-domain quotation term(s)",
            )
        )

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in manifest.required_future_work
    ]
    if missing_future_work:
        results.append(
            _rejected(
                "required_future_work",
                "missing future work: " + ", ".join(missing_future_work),
            )
        )
    else:
        results.append(_accepted("required_future_work", "future work is explicit"))

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in manifest.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted("non_claims", "non-claims are explicit"))

    return results


def _failed_subject_for_result(subject: str) -> str:
    if subject == "expected_subject_count":
        return "substitution-graph-quotation-term-closure-count"
    if subject in {"closure_subject_ids", "closure_subjects"}:
        return "substitution-graph-quotation-term-closure-subject"
    if subject == "required_source_kinds":
        return "substitution-graph-quotation-term-closure-source-kind"
    if subject == "required_future_work":
        return "substitution-graph-quotation-term-closure-future-work"
    if subject == "non_claims":
        return "substitution-graph-quotation-term-closure-non-claim"
    if subject in {
        "codebook",
        "quotation_term",
        "formula_candidates",
        "evaluation_examples",
    }:
        return "substitution-graph-quotation-term-closure-dependency"
    if subject.endswith("_path"):
        return "substitution-graph-quotation-term-closure-reference"
    return "substitution-graph-quotation-term-closure"


def _node_kind(node: dict[str, Any]) -> str:
    kind = node.get("kind")
    if not isinstance(kind, str) or not kind:
        raise ValueError("node kind missing")
    return kind


def _required_node(node: dict[str, Any], key: str) -> dict[str, Any]:
    value = node.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required node missing: {key}")
    return value


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


def _required_text_list(item: dict[str, Any], key: str) -> list[str]:
    values = item.get(key)
    if not isinstance(values, list) or not values:
        raise ValueError(f"required list field missing: {key}")
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        result.append(value)
    return result


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _accepted(
    subject: str,
    detail: str,
) -> SubstitutionGraphQuotationTermClosureValidation:
    return SubstitutionGraphQuotationTermClosureValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphQuotationTermClosureValidation:
    return SubstitutionGraphQuotationTermClosureValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_quotation_term_closure_cli())
