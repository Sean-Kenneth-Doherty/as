"""Finite meta-substitution semantics domain for substitution graph evidence.

This module checks the concrete meta-level substitutions currently exercised by
the substitution graph formula candidate and finite evaluation examples. It is
finite executable evidence for the third correctness proof case, not a proof
that the substitution helper is correct for every formal node.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.formal_code import (
    FormalCodebook,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_substitution import (
    free_variables,
    load_substitution_examples,
    substitute_node,
    validate_substitution_examples,
)
from autarkic_systems.formal_quotation_term import quote_tokens_as_term
from autarkic_systems.substitution_graph_evaluation import (
    SubstitutionGraphEvaluationExample,
    load_substitution_graph_evaluation_examples,
    validate_substitution_graph_evaluation_examples,
)
from autarkic_systems.substitution_graph_formula import (
    SubstitutionGraphFormulaCandidate,
    load_substitution_graph_formula_candidates,
    validate_substitution_graph_formula_candidates,
)
from autarkic_systems.substitution_representability import (
    SubstitutionRepresentabilityObservation,
    SubstitutionRepresentabilityWitness,
    build_substitution_witness_output_code,
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)


DEFAULT_SEMANTICS = Path("claims/substitution_graph_meta_substitution_semantics.json")
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
class SubstitutionGraphMetaSubstitutionSemanticsManifest:
    """Loaded manifest for the current graph meta-substitution domain."""

    path: Path
    schema_version: int
    semantics_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    formal_substitution_examples_path: str
    formula_candidates_path: str
    evaluation_examples_path: str
    expected_subject_count: int
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphMetaSubstitutionSemanticsValidation:
    """One validation result for graph meta-substitution semantics."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphMetaSubstitutionSemanticsSubject:
    """One observed finite meta-substitution semantics subject."""

    subject_id: str
    source_kind: str
    source_id: str
    variable: str
    replacement_role: str
    replacement_code_length: int
    input_free_variables: tuple[str, ...]
    output_free_variables: tuple[str, ...]
    expected_output_free_variables: tuple[str, ...]
    variable_was_free: bool
    replacement_closed: bool
    free_variables_preserved: bool
    output_matches_expected_surface: bool
    no_op_when_variable_not_free: bool


@dataclass(frozen=True)
class SubstitutionGraphMetaSubstitutionSemanticsReport:
    """Validation report over finite graph meta-substitution subjects."""

    manifest: SubstitutionGraphMetaSubstitutionSemanticsManifest
    formal_language_path: Path
    codebook_path: Path
    formal_substitution_examples_path: Path
    formula_candidates_path: Path
    evaluation_examples_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionGraphMetaSubstitutionSemanticsValidation, ...]
    subjects: tuple[SubstitutionGraphMetaSubstitutionSemanticsSubject, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every semantics validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def subject_count(self) -> int:
        """Return the number of checked meta-substitution subjects."""

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


def load_substitution_graph_meta_substitution_semantics(
    path: Path | str = DEFAULT_SEMANTICS,
) -> SubstitutionGraphMetaSubstitutionSemanticsManifest:
    """Load the graph meta-substitution semantics manifest from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return SubstitutionGraphMetaSubstitutionSemanticsManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        semantics_set_id=_required_text(data, "semantics_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        formal_substitution_examples_path=_required_text(
            data,
            "formal_substitution_examples_path",
        ),
        formula_candidates_path=_required_text(data, "formula_candidates_path"),
        evaluation_examples_path=_required_text(data, "evaluation_examples_path"),
        expected_subject_count=_required_int(data, "expected_subject_count"),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_meta_substitution_semantics(
    manifest: SubstitutionGraphMetaSubstitutionSemanticsManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphMetaSubstitutionSemanticsReport:
    """Validate finite graph meta-substitution semantics subjects."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_substitution_path = Path(manifest.formal_substitution_examples_path)
    checked_formula_path = Path(manifest.formula_candidates_path)
    checked_evaluation_path = Path(manifest.evaluation_examples_path)

    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    substitution_examples = load_substitution_examples(checked_substitution_path)
    substitution_report = validate_substitution_examples(
        substitution_examples,
        checked_codebook_path,
        checked_language_path,
        checked_willard_map_path,
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

    results: list[SubstitutionGraphMetaSubstitutionSemanticsValidation] = [
        _accepted("manifest", f"loaded {manifest.semantics_set_id}")
    ]
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            codebook_report,
            substitution_report,
            formula_report,
            evaluation_report,
        )
    )

    subjects: list[SubstitutionGraphMetaSubstitutionSemanticsSubject] = []
    try:
        subjects = _derive_semantics_subjects(
            formula_manifest.candidates,
            evaluation_manifest.examples,
            codebook,
            formula_manifest.substitution_representability_targets_path,
            checked_willard_map_path,
        )
    except ValueError as exc:
        results.append(_rejected("semantics_subjects", str(exc)))

    results.extend(_validate_subject_set(manifest, tuple(subjects)))

    return SubstitutionGraphMetaSubstitutionSemanticsReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        formal_substitution_examples_path=checked_substitution_path,
        formula_candidates_path=checked_formula_path,
        evaluation_examples_path=checked_evaluation_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        subjects=tuple(subjects),
    )


def substitution_graph_meta_substitution_semantics_report_payload(
    report: SubstitutionGraphMetaSubstitutionSemanticsReport,
) -> dict[str, Any]:
    """Return a JSON-ready graph meta-substitution semantics payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "semantics_manifest": str(report.manifest.path),
        "semantics_set_id": report.manifest.semantics_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "formal_substitution_examples_path": str(
            report.formal_substitution_examples_path
        ),
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
                "variable": subject.variable,
                "replacement_role": subject.replacement_role,
                "observed_replacement_code_length": (
                    subject.replacement_code_length
                ),
                "observed_input_free_variables": list(
                    subject.input_free_variables
                ),
                "observed_output_free_variables": list(
                    subject.output_free_variables
                ),
                "observed_expected_output_free_variables": list(
                    subject.expected_output_free_variables
                ),
                "observed_variable_was_free": subject.variable_was_free,
                "observed_replacement_closed": subject.replacement_closed,
                "observed_free_variables_preserved": (
                    subject.free_variables_preserved
                ),
                "observed_output_matches_expected_surface": (
                    subject.output_matches_expected_surface
                ),
                "observed_no_op_when_variable_not_free": (
                    subject.no_op_when_variable_not_free
                ),
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


def format_substitution_graph_meta_substitution_semantics_report(
    report: SubstitutionGraphMetaSubstitutionSemanticsReport,
) -> str:
    """Format a concise human-readable meta-substitution semantics report."""

    status = "accepted" if report.accepted else "rejected"
    failures = [
        subject.subject_id for subject in report.subjects if not _subject_accepted(subject)
    ]
    source_counts = ", ".join(
        f"{source_kind}={count}"
        for source_kind, count in report.source_kind_counts.items()
    )
    lines = [
        f"Substitution graph meta-substitution semantics: {status}",
        f"Semantics set: {report.manifest.semantics_set_id}",
        f"Subjects: {report.subject_count}",
        f"Source kinds: {source_counts}",
        f"Semantic failures: {_joined_or_none(tuple(failures))}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_meta_substitution_semantics_cli(
    argv: list[str] | None = None,
) -> int:
    """Run finite graph meta-substitution semantics validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.substitution_graph_meta_substitution_semantics"
        ),
        description="Validate substitution graph meta-substitution semantics.",
    )
    parser.add_argument(
        "--semantics",
        default=str(DEFAULT_SEMANTICS),
        help="Path to the graph meta-substitution semantics manifest.",
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

    manifest = load_substitution_graph_meta_substitution_semantics(args.semantics)
    report = validate_substitution_graph_meta_substitution_semantics(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(substitution_graph_meta_substitution_semantics_report_payload(report), sort_keys=True))
    else:
        print(format_substitution_graph_meta_substitution_semantics_report(report))
    return 0 if report.accepted else 1


def _derive_semantics_subjects(
    candidates: tuple[SubstitutionGraphFormulaCandidate, ...],
    examples: tuple[SubstitutionGraphEvaluationExample, ...],
    codebook: FormalCodebook,
    representability_targets_path: str,
    willard_map_path: Path,
) -> list[SubstitutionGraphMetaSubstitutionSemanticsSubject]:
    subjects: list[SubstitutionGraphMetaSubstitutionSemanticsSubject] = []
    witness_manifest = load_substitution_representability_targets(
        representability_targets_path,
    )
    witness_report = validate_substitution_representability_targets(
        witness_manifest,
        willard_map_path=willard_map_path,
    )
    if not witness_report.accepted:
        raise ValueError(
            "substitution representability rejected: "
            + _joined_or_none(witness_report.failed_subjects)
        )

    for candidate in candidates:
        witness_target = _find_witness(witness_manifest.witnesses, candidate.witness_id)
        witness = _find_witness_observation(
            witness_report.observations,
            candidate.witness_id,
        )
        subjects.extend(
            _candidate_subjects(
                candidate,
                witness_target,
                witness,
                codebook,
                representability_targets_path,
            )
        )

    for example in examples:
        subjects.append(_evaluation_subject(example, codebook))

    return subjects


def _candidate_subjects(
    candidate: SubstitutionGraphFormulaCandidate,
    witness_target: SubstitutionRepresentabilityWitness,
    witness: SubstitutionRepresentabilityObservation,
    codebook: FormalCodebook,
    representability_targets_path: str,
) -> list[SubstitutionGraphMetaSubstitutionSemanticsSubject]:
    output_code = build_substitution_witness_output_code(
        witness_id=candidate.witness_id,
        targets_path=representability_targets_path,
    )
    current = candidate.formula_node
    substitutions = (
        (
            "formula_code",
            candidate.graph_variables["formula_code"],
            witness.formula_code,
        ),
        (
            "argument_code",
            candidate.graph_variables["argument_code"],
            witness.argument_code,
        ),
        (
            "output_code",
            candidate.graph_variables["output_code"],
            output_code,
        ),
    )
    subjects: list[SubstitutionGraphMetaSubstitutionSemanticsSubject] = []
    for replacement_role, variable, code in substitutions:
        before = current
        replacement = quote_tokens_as_term(code)
        after = substitute_node(before, variable, replacement)
        current = after
        output_matches_expected_surface = True
        if replacement_role == "output_code":
            output_code_observed = encode_node(after, codebook)
            output_matches_expected_surface = (
                len(output_code_observed)
                == candidate.expected_witness_instance_code_length
                and output_code_observed[
                    : len(candidate.expected_witness_instance_code_prefix)
                ]
                == candidate.expected_witness_instance_code_prefix
                and tuple(sorted(free_variables(after)))
                == candidate.expected_witness_instance_free_variables
            )
            relation_holds, _evaluated_output_code = _evaluate_witness_relation(
                after,
                witness_target.variable,
                codebook,
            )
            output_matches_expected_surface = (
                output_matches_expected_surface
                and relation_holds == candidate.expected_witness_relation_holds
            )
        subjects.append(
            _semantics_subject(
                subject_id=f"{candidate.candidate_id}.{replacement_role}_substitution",
                source_kind="formula-candidate",
                source_id=candidate.candidate_id,
                variable=variable,
                replacement_role=replacement_role,
                replacement_code=code,
                before=before,
                replacement=replacement,
                after=after,
                output_matches_expected_surface=output_matches_expected_surface,
            )
        )
    return subjects


def _evaluation_subject(
    example: SubstitutionGraphEvaluationExample,
    codebook: FormalCodebook,
) -> SubstitutionGraphMetaSubstitutionSemanticsSubject:
    replacement = quote_tokens_as_term(example.argument_code)
    after = substitute_node(example.formula_node, example.variable, replacement)
    output_code = encode_node(after, codebook)
    output_matches_expected_surface = (
        len(output_code) == example.expected_output_code_length
        and output_code[: len(example.expected_output_code_prefix)]
        == example.expected_output_code_prefix
        and tuple(sorted(free_variables(after))) == example.expected_output_free_variables
    )
    return _semantics_subject(
        subject_id=f"{example.example_id}.argument_substitution",
        source_kind="finite-evaluation",
        source_id=example.example_id,
        variable=example.variable,
        replacement_role="argument_code",
        replacement_code=example.argument_code,
        before=example.formula_node,
        replacement=replacement,
        after=after,
        output_matches_expected_surface=output_matches_expected_surface,
    )


def _semantics_subject(
    subject_id: str,
    source_kind: str,
    source_id: str,
    variable: str,
    replacement_role: str,
    replacement_code: tuple[int, ...],
    before: dict[str, Any],
    replacement: dict[str, Any],
    after: dict[str, Any],
    output_matches_expected_surface: bool,
) -> SubstitutionGraphMetaSubstitutionSemanticsSubject:
    input_free_variables = tuple(sorted(free_variables(before)))
    output_free_variables = tuple(sorted(free_variables(after)))
    replacement_free_variables = free_variables(replacement)
    expected_output_free_variables = tuple(
        sorted(set(input_free_variables) - {variable})
    )
    variable_was_free = variable in input_free_variables
    return SubstitutionGraphMetaSubstitutionSemanticsSubject(
        subject_id=subject_id,
        source_kind=source_kind,
        source_id=source_id,
        variable=variable,
        replacement_role=replacement_role,
        replacement_code_length=len(replacement_code),
        input_free_variables=input_free_variables,
        output_free_variables=output_free_variables,
        expected_output_free_variables=expected_output_free_variables,
        variable_was_free=variable_was_free,
        replacement_closed=not replacement_free_variables,
        free_variables_preserved=(
            output_free_variables == expected_output_free_variables
        ),
        output_matches_expected_surface=output_matches_expected_surface,
        no_op_when_variable_not_free=(
            not variable_was_free
            and after == before
        ),
    )


def _evaluate_witness_relation(
    instance: dict[str, Any],
    variable: str,
    codebook: FormalCodebook,
) -> tuple[bool, tuple[int, ...]]:
    if _node_kind(instance) != "equals":
        raise ValueError("witness instance must be an equality")
    left = _required_node(instance, "left")
    right = _required_node(instance, "right")
    if _node_kind(left) != "substitution_code":
        raise ValueError("witness left side must be substitution_code")
    formula_code = _tokens_from_quotation_term(_required_node(left, "left"))
    argument_code = _tokens_from_quotation_term(_required_node(left, "right"))
    expected_output_code = _tokens_from_quotation_term(right)
    formula_node = _decode_formula_code(formula_code, codebook)
    evaluated_node = substitute_node(
        formula_node,
        variable,
        quote_tokens_as_term(argument_code),
    )
    evaluated_output_code = encode_node(evaluated_node, codebook)
    return evaluated_output_code == expected_output_code, evaluated_output_code


def _decode_formula_code(
    formula_code: tuple[int, ...],
    codebook: FormalCodebook,
) -> dict[str, Any]:
    from autarkic_systems.formal_code import decode_code

    return decode_code(formula_code, codebook)


def _tokens_from_quotation_term(term: dict[str, Any]) -> tuple[int, ...]:
    from autarkic_systems.formal_quotation import numeral_to_natural

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


def _validate_references(
    manifest: SubstitutionGraphMetaSubstitutionSemanticsManifest,
) -> list[SubstitutionGraphMetaSubstitutionSemanticsValidation]:
    expected = (
        (
            "formal_language_path",
            manifest.formal_language_path,
            "language/formal_arithmetic_language.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "formal_substitution_examples_path",
            manifest.formal_substitution_examples_path,
            "language/formal_substitution_examples.json",
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
    results: list[SubstitutionGraphMetaSubstitutionSemanticsValidation] = []
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
    substitution_report: Any,
    formula_report: Any,
    evaluation_report: Any,
) -> list[SubstitutionGraphMetaSubstitutionSemanticsValidation]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        ("formal_substitution", substitution_report, "formal substitution"),
        ("formula_candidates", formula_report, "substitution graph formula"),
        ("evaluation_examples", evaluation_report, "substitution graph evaluation"),
    )
    results: list[SubstitutionGraphMetaSubstitutionSemanticsValidation] = []
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
    manifest: SubstitutionGraphMetaSubstitutionSemanticsManifest,
    subjects: tuple[SubstitutionGraphMetaSubstitutionSemanticsSubject, ...],
) -> list[SubstitutionGraphMetaSubstitutionSemanticsValidation]:
    results: list[SubstitutionGraphMetaSubstitutionSemanticsValidation] = []
    subject_ids = [subject.subject_id for subject in subjects]
    duplicate_ids = _duplicates(subject_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "semantics_subject_ids",
                "duplicate subject ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("semantics_subject_ids", "subject ids are unique"))

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
        if not _subject_accepted(subject)
    ]
    if failures:
        results.append(
            _rejected(
                "semantics_subjects",
                "semantic failures: " + ", ".join(failures),
            )
        )
    else:
        results.append(
            _accepted(
                "semantics_subjects",
                f"checked {len(subjects)} graph-domain substitution(s)",
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


def _subject_accepted(
    subject: SubstitutionGraphMetaSubstitutionSemanticsSubject,
) -> bool:
    return (
        subject.replacement_closed
        and subject.free_variables_preserved
        and subject.output_matches_expected_surface
        and (
            subject.variable_was_free
            or subject.no_op_when_variable_not_free
        )
    )


def _find_witness(
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    witness_id: str,
) -> SubstitutionRepresentabilityWitness:
    for witness in witnesses:
        if witness.witness_id == witness_id:
            return witness
    raise ValueError(f"unknown witness: {witness_id}")


def _find_witness_observation(
    observations: tuple[SubstitutionRepresentabilityObservation, ...],
    witness_id: str,
) -> SubstitutionRepresentabilityObservation:
    for observation in observations:
        if observation.witness_id == witness_id:
            return observation
    raise ValueError(f"missing witness observation: {witness_id}")


def _failed_subject_for_result(subject: str) -> str:
    if subject == "expected_subject_count":
        return "substitution-graph-meta-substitution-semantics-count"
    if subject in {"semantics_subject_ids", "semantics_subjects"}:
        return "substitution-graph-meta-substitution-semantics-subject"
    if subject == "required_source_kinds":
        return "substitution-graph-meta-substitution-semantics-source-kind"
    if subject == "required_future_work":
        return "substitution-graph-meta-substitution-semantics-future-work"
    if subject == "non_claims":
        return "substitution-graph-meta-substitution-semantics-non-claim"
    if subject in {
        "codebook",
        "formal_substitution",
        "formula_candidates",
        "evaluation_examples",
    }:
        return "substitution-graph-meta-substitution-semantics-dependency"
    if subject.endswith("_path"):
        return "substitution-graph-meta-substitution-semantics-reference"
    return "substitution-graph-meta-substitution-semantics"


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
) -> SubstitutionGraphMetaSubstitutionSemanticsValidation:
    return SubstitutionGraphMetaSubstitutionSemanticsValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphMetaSubstitutionSemanticsValidation:
    return SubstitutionGraphMetaSubstitutionSemanticsValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_meta_substitution_semantics_cli())
