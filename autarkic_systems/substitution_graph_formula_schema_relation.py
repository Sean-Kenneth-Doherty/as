"""Finite formula-schema relation domain for substitution graph evidence.

This module checks that the current substitution graph formula candidate,
graph target, witness instance, and finite evaluation examples all state the
same concrete ``substitution_code`` graph relation. It is finite executable
evidence for the fourth correctness proof case, not a proof that the formula
schema is correct for every encoded formula and argument.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.formal_code import (
    FormalCodebook,
    decode_code,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation import numeral_to_natural
from autarkic_systems.formal_quotation_term import quote_tokens_as_term
from autarkic_systems.formal_substitution import free_variables, substitute_node
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
from autarkic_systems.substitution_graph_target import (
    SubstitutionGraphTarget,
    load_substitution_graph_targets,
    validate_substitution_graph_targets,
)
from autarkic_systems.substitution_representability import (
    SubstitutionRepresentabilityObservation,
    SubstitutionRepresentabilityWitness,
    build_substitution_witness_output_code,
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)


DEFAULT_RELATION = Path("claims/substitution_graph_formula_schema_relation.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = (
    "witness-instance",
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
class SubstitutionGraphFormulaSchemaRelationManifest:
    """Loaded manifest for the current formula-schema relation domain."""

    path: Path
    schema_version: int
    relation_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    substitution_graph_targets_path: str
    formula_candidates_path: str
    evaluation_examples_path: str
    substitution_representability_targets_path: str
    expected_relation_point_count: int
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphFormulaSchemaRelationValidation:
    """One validation result for graph formula-schema relation evidence."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphFormulaSchemaRelationPoint:
    """One finite point where the formula schema states the graph relation."""

    point_id: str
    source_kind: str
    source_id: str
    variable: str
    formula_code_length: int
    argument_code_length: int
    output_code_length: int
    schema_instance_code_length: int
    schema_instance_closed: bool
    formula_code_roundtrips: bool
    decoded_formula_matches_source: bool
    input_matches_expected_surface: bool
    relation_holds: bool
    output_matches_expected_surface: bool


@dataclass(frozen=True)
class SubstitutionGraphFormulaSchemaRelationReport:
    """Validation report over finite formula-schema relation points."""

    manifest: SubstitutionGraphFormulaSchemaRelationManifest
    formal_language_path: Path
    codebook_path: Path
    substitution_graph_targets_path: Path
    formula_candidates_path: Path
    evaluation_examples_path: Path
    substitution_representability_targets_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionGraphFormulaSchemaRelationValidation, ...]
    relation_points: tuple[SubstitutionGraphFormulaSchemaRelationPoint, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every relation validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def relation_point_count(self) -> int:
        """Return the number of checked formula-schema relation points."""

        return len(self.relation_points)

    @property
    def source_kind_counts(self) -> dict[str, int]:
        """Return observed relation point counts grouped by source kind."""

        counts = {source_kind: 0 for source_kind in REQUIRED_SOURCE_KINDS}
        for point in self.relation_points:
            counts[point.source_kind] = counts.get(point.source_kind, 0) + 1
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


def load_substitution_graph_formula_schema_relation(
    path: Path | str = DEFAULT_RELATION,
) -> SubstitutionGraphFormulaSchemaRelationManifest:
    """Load the graph formula-schema relation manifest from JSON."""

    relation_path = Path(path)
    data = json.loads(relation_path.read_text(encoding="utf-8"))
    return SubstitutionGraphFormulaSchemaRelationManifest(
        path=relation_path,
        schema_version=_required_int(data, "schema_version"),
        relation_set_id=_required_text(data, "relation_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        substitution_graph_targets_path=_required_text(
            data,
            "substitution_graph_targets_path",
        ),
        formula_candidates_path=_required_text(data, "formula_candidates_path"),
        evaluation_examples_path=_required_text(data, "evaluation_examples_path"),
        substitution_representability_targets_path=_required_text(
            data,
            "substitution_representability_targets_path",
        ),
        expected_relation_point_count=_required_int(
            data,
            "expected_relation_point_count",
        ),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_formula_schema_relation(
    manifest: SubstitutionGraphFormulaSchemaRelationManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphFormulaSchemaRelationReport:
    """Validate finite graph formula-schema relation points."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_graph_targets_path = Path(manifest.substitution_graph_targets_path)
    checked_formula_path = Path(manifest.formula_candidates_path)
    checked_evaluation_path = Path(manifest.evaluation_examples_path)
    checked_witness_path = Path(manifest.substitution_representability_targets_path)

    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    graph_manifest = load_substitution_graph_targets(checked_graph_targets_path)
    graph_report = validate_substitution_graph_targets(
        graph_manifest,
        checked_willard_map_path,
    )
    formula_manifest = load_substitution_graph_formula_candidates(
        checked_formula_path,
    )
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
    witness_manifest = load_substitution_representability_targets(
        checked_witness_path,
    )
    witness_report = validate_substitution_representability_targets(
        witness_manifest,
        checked_language_path,
        checked_willard_map_path,
    )

    results: list[SubstitutionGraphFormulaSchemaRelationValidation] = [
        _accepted("manifest", f"loaded {manifest.relation_set_id}")
    ]
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            codebook_report,
            graph_report,
            formula_report,
            evaluation_report,
            witness_report,
        )
    )
    results.extend(
        _validate_schema_alignment(
            graph_manifest.targets,
            formula_manifest.candidates,
        )
    )

    relation_points: list[SubstitutionGraphFormulaSchemaRelationPoint] = []
    try:
        relation_points = _derive_relation_points(
            graph_manifest.targets,
            formula_manifest.candidates,
            evaluation_manifest.examples,
            witness_manifest.witnesses,
            witness_report.observations,
            codebook,
            checked_witness_path,
        )
    except ValueError as exc:
        results.append(_rejected("relation_points", str(exc)))

    results.extend(_validate_relation_point_set(manifest, tuple(relation_points)))

    return SubstitutionGraphFormulaSchemaRelationReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        substitution_graph_targets_path=checked_graph_targets_path,
        formula_candidates_path=checked_formula_path,
        evaluation_examples_path=checked_evaluation_path,
        substitution_representability_targets_path=checked_witness_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        relation_points=tuple(relation_points),
    )


def substitution_graph_formula_schema_relation_report_payload(
    report: SubstitutionGraphFormulaSchemaRelationReport,
) -> dict[str, Any]:
    """Return a JSON-ready graph formula-schema relation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "relation_manifest": str(report.manifest.path),
        "relation_set_id": report.manifest.relation_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "substitution_graph_targets_path": str(
            report.substitution_graph_targets_path
        ),
        "formula_candidates_path": str(report.formula_candidates_path),
        "evaluation_examples_path": str(report.evaluation_examples_path),
        "substitution_representability_targets_path": str(
            report.substitution_representability_targets_path
        ),
        "willard_map": str(report.willard_map_path),
        "expected_relation_point_count": (
            report.manifest.expected_relation_point_count
        ),
        "relation_point_count": report.relation_point_count,
        "source_kind_counts": report.source_kind_counts,
        "required_source_kinds": list(report.manifest.required_source_kinds),
        "required_future_work": list(report.manifest.required_future_work),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "relation_points": [
            {
                "point_id": point.point_id,
                "source_kind": point.source_kind,
                "source_id": point.source_id,
                "variable": point.variable,
                "observed_formula_code_length": point.formula_code_length,
                "observed_argument_code_length": point.argument_code_length,
                "observed_output_code_length": point.output_code_length,
                "observed_schema_instance_code_length": (
                    point.schema_instance_code_length
                ),
                "observed_schema_instance_closed": (
                    point.schema_instance_closed
                ),
                "observed_formula_code_roundtrips": (
                    point.formula_code_roundtrips
                ),
                "observed_decoded_formula_matches_source": (
                    point.decoded_formula_matches_source
                ),
                "observed_input_matches_expected_surface": (
                    point.input_matches_expected_surface
                ),
                "observed_relation_holds": point.relation_holds,
                "observed_output_matches_expected_surface": (
                    point.output_matches_expected_surface
                ),
            }
            for point in report.relation_points
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


def format_substitution_graph_formula_schema_relation_report(
    report: SubstitutionGraphFormulaSchemaRelationReport,
) -> str:
    """Format a concise human-readable formula-schema relation report."""

    status = "accepted" if report.accepted else "rejected"
    failures = [
        point.point_id
        for point in report.relation_points
        if not _relation_point_accepted(point)
    ]
    source_counts = ", ".join(
        f"{source_kind}={count}"
        for source_kind, count in report.source_kind_counts.items()
    )
    lines = [
        f"Substitution graph formula schema relation: {status}",
        f"Relation set: {report.manifest.relation_set_id}",
        f"Relation points: {report.relation_point_count}",
        f"Source kinds: {source_counts}",
        f"Relation failures: {_joined_or_none(tuple(failures))}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_formula_schema_relation_cli(
    argv: list[str] | None = None,
) -> int:
    """Run finite graph formula-schema relation validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.substitution_graph_formula_schema_relation"
        ),
        description="Validate substitution graph formula-schema relation.",
    )
    parser.add_argument(
        "--relation",
        default=str(DEFAULT_RELATION),
        help="Path to the graph formula-schema relation manifest.",
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

    manifest = load_substitution_graph_formula_schema_relation(args.relation)
    report = validate_substitution_graph_formula_schema_relation(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(
            substitution_graph_formula_schema_relation_report_payload(report),
            sort_keys=True,
        ))
    else:
        print(format_substitution_graph_formula_schema_relation_report(report))
    return 0 if report.accepted else 1


def _derive_relation_points(
    graph_targets: tuple[SubstitutionGraphTarget, ...],
    candidates: tuple[SubstitutionGraphFormulaCandidate, ...],
    examples: tuple[SubstitutionGraphEvaluationExample, ...],
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    witness_observations: tuple[SubstitutionRepresentabilityObservation, ...],
    codebook: FormalCodebook,
    witness_targets_path: Path,
) -> list[SubstitutionGraphFormulaSchemaRelationPoint]:
    relation_points: list[SubstitutionGraphFormulaSchemaRelationPoint] = []
    for candidate in candidates:
        graph_target = _find_graph_target(graph_targets, candidate.target_id)
        witness = _find_witness(witnesses, candidate.witness_id)
        witness_observation = _find_witness_observation(
            witness_observations,
            candidate.witness_id,
        )
        relation_points.append(
            _witness_relation_point(
                candidate,
                graph_target,
                witness,
                witness_observation,
                codebook,
                witness_targets_path,
            )
        )
        for example in examples:
            relation_points.append(
                _evaluation_relation_point(candidate, example, codebook)
            )
    return relation_points


def _witness_relation_point(
    candidate: SubstitutionGraphFormulaCandidate,
    graph_target: SubstitutionGraphTarget,
    witness: SubstitutionRepresentabilityWitness,
    witness_observation: SubstitutionRepresentabilityObservation,
    codebook: FormalCodebook,
    witness_targets_path: Path,
) -> SubstitutionGraphFormulaSchemaRelationPoint:
    output_code = build_substitution_witness_output_code(
        witness_id=candidate.witness_id,
        targets_path=witness_targets_path,
    )
    expected_input_matches = (
        witness_observation.formula_code == graph_target.expected_witness_formula_code
        and witness_observation.argument_code
        == graph_target.expected_witness_argument_code
    )
    return _relation_point(
        point_id=f"{candidate.candidate_id}.witness_relation",
        source_kind="witness-instance",
        source_id=witness.witness_id,
        candidate=candidate,
        variable=witness.variable,
        formula_code=witness_observation.formula_code,
        argument_code=witness_observation.argument_code,
        expected_output_code=output_code,
        expected_output_code_length=graph_target.expected_witness_output_code_length,
        expected_output_code_prefix=graph_target.expected_witness_output_code_prefix,
        expected_output_free_variables=(
            graph_target.expected_witness_output_free_variables
        ),
        source_formula_node=None,
        input_matches_expected_surface=expected_input_matches,
        codebook=codebook,
    )


def _evaluation_relation_point(
    candidate: SubstitutionGraphFormulaCandidate,
    example: SubstitutionGraphEvaluationExample,
    codebook: FormalCodebook,
) -> SubstitutionGraphFormulaSchemaRelationPoint:
    formula_code = encode_node(example.formula_node, codebook)
    output_node = substitute_node(
        example.formula_node,
        example.variable,
        quote_tokens_as_term(example.argument_code),
    )
    output_code = encode_node(output_node, codebook)
    expected_input_matches = formula_code == example.expected_formula_code
    return _relation_point(
        point_id=f"{example.example_id}.formula_schema_relation",
        source_kind="finite-evaluation",
        source_id=example.example_id,
        candidate=candidate,
        variable=example.variable,
        formula_code=formula_code,
        argument_code=example.argument_code,
        expected_output_code=output_code,
        expected_output_code_length=example.expected_output_code_length,
        expected_output_code_prefix=example.expected_output_code_prefix,
        expected_output_free_variables=example.expected_output_free_variables,
        source_formula_node=example.formula_node,
        input_matches_expected_surface=bool(expected_input_matches),
        codebook=codebook,
    )


def _relation_point(
    point_id: str,
    source_kind: str,
    source_id: str,
    candidate: SubstitutionGraphFormulaCandidate,
    variable: str,
    formula_code: tuple[int, ...],
    argument_code: tuple[int, ...],
    expected_output_code: tuple[int, ...],
    expected_output_code_length: int,
    expected_output_code_prefix: tuple[int, ...],
    expected_output_free_variables: tuple[str, ...],
    source_formula_node: dict[str, Any] | None,
    input_matches_expected_surface: bool,
    codebook: FormalCodebook,
) -> SubstitutionGraphFormulaSchemaRelationPoint:
    instance = _instantiate_schema(
        candidate,
        formula_code,
        argument_code,
        expected_output_code,
    )
    instance_code = encode_node(instance, codebook)
    decoded_formula = decode_code(formula_code, codebook)
    relation_holds, evaluated_output_code, evaluated_output_free_variables = (
        _evaluate_schema_instance(instance, variable, codebook)
    )
    formula_code_roundtrips = encode_node(decoded_formula, codebook) == formula_code
    decoded_formula_matches_source = (
        source_formula_node is None
        or decoded_formula == source_formula_node
    )
    output_matches_expected_surface = (
        len(evaluated_output_code) == expected_output_code_length
        and evaluated_output_code[: len(expected_output_code_prefix)]
        == expected_output_code_prefix
        and evaluated_output_free_variables == expected_output_free_variables
    )
    return SubstitutionGraphFormulaSchemaRelationPoint(
        point_id=point_id,
        source_kind=source_kind,
        source_id=source_id,
        variable=variable,
        formula_code_length=len(formula_code),
        argument_code_length=len(argument_code),
        output_code_length=len(expected_output_code),
        schema_instance_code_length=len(instance_code),
        schema_instance_closed=not free_variables(instance),
        formula_code_roundtrips=formula_code_roundtrips,
        decoded_formula_matches_source=decoded_formula_matches_source,
        input_matches_expected_surface=input_matches_expected_surface,
        relation_holds=relation_holds,
        output_matches_expected_surface=output_matches_expected_surface,
    )


def _instantiate_schema(
    candidate: SubstitutionGraphFormulaCandidate,
    formula_code: tuple[int, ...],
    argument_code: tuple[int, ...],
    output_code: tuple[int, ...],
) -> dict[str, Any]:
    instance = candidate.formula_node
    substitutions = (
        (candidate.graph_variables["formula_code"], formula_code),
        (candidate.graph_variables["argument_code"], argument_code),
        (candidate.graph_variables["output_code"], output_code),
    )
    for variable, code in substitutions:
        instance = substitute_node(instance, variable, quote_tokens_as_term(code))
    return instance


def _evaluate_schema_instance(
    instance: dict[str, Any],
    variable: str,
    codebook: FormalCodebook,
) -> tuple[bool, tuple[int, ...], tuple[str, ...]]:
    if _node_kind(instance) != "equals":
        raise ValueError("schema instance must be an equality")
    left = _required_node(instance, "left")
    right = _required_node(instance, "right")
    if _node_kind(left) != "substitution_code":
        raise ValueError("schema instance left side must be substitution_code")
    formula_code = _tokens_from_quotation_term(_required_node(left, "left"))
    argument_code = _tokens_from_quotation_term(_required_node(left, "right"))
    expected_output_code = _tokens_from_quotation_term(right)
    formula_node = decode_code(formula_code, codebook)
    output_node = substitute_node(
        formula_node,
        variable,
        quote_tokens_as_term(argument_code),
    )
    evaluated_output_code = encode_node(output_node, codebook)
    return (
        evaluated_output_code == expected_output_code,
        evaluated_output_code,
        tuple(sorted(free_variables(output_node))),
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


def _validate_references(
    manifest: SubstitutionGraphFormulaSchemaRelationManifest,
) -> list[SubstitutionGraphFormulaSchemaRelationValidation]:
    expected = (
        (
            "formal_language_path",
            manifest.formal_language_path,
            "language/formal_arithmetic_language.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "substitution_graph_targets_path",
            manifest.substitution_graph_targets_path,
            "claims/substitution_graph_targets.json",
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
        (
            "substitution_representability_targets_path",
            manifest.substitution_representability_targets_path,
            "claims/substitution_representability_targets.json",
        ),
    )
    results: list[SubstitutionGraphFormulaSchemaRelationValidation] = []
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
    graph_report: Any,
    formula_report: Any,
    evaluation_report: Any,
    witness_report: Any,
) -> list[SubstitutionGraphFormulaSchemaRelationValidation]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        ("substitution_graph", graph_report, "substitution graph target"),
        ("formula_candidate", formula_report, "substitution graph formula"),
        (
            "evaluation_examples",
            evaluation_report,
            "substitution graph evaluation",
        ),
        (
            "substitution_representability",
            witness_report,
            "substitution representability witness",
        ),
    )
    results: list[SubstitutionGraphFormulaSchemaRelationValidation] = []
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


def _validate_schema_alignment(
    graph_targets: tuple[SubstitutionGraphTarget, ...],
    candidates: tuple[SubstitutionGraphFormulaCandidate, ...],
) -> list[SubstitutionGraphFormulaSchemaRelationValidation]:
    results: list[SubstitutionGraphFormulaSchemaRelationValidation] = []
    if not candidates:
        return [_rejected("schema_alignment", "no formula candidates")]
    for candidate in candidates:
        subject = f"{candidate.candidate_id}.schema_alignment"
        try:
            graph_target = _find_graph_target(graph_targets, candidate.target_id)
        except ValueError as exc:
            results.append(_rejected(subject, str(exc)))
            continue
        expected_schema = _schema_node(candidate.graph_variables)
        if candidate.formula_node != expected_schema:
            results.append(_rejected(subject, "formula must be substitution_code(x,y) = z"))
        elif graph_target.relation_name != candidate.relation_name:
            results.append(_rejected(subject, "graph target relation mismatch"))
        elif graph_target.formula_class != candidate.formula_class:
            results.append(_rejected(subject, "graph target formula class mismatch"))
        elif graph_target.graph_variables != candidate.graph_variables:
            results.append(_rejected(subject, "graph variable mismatch"))
        else:
            results.append(
                _accepted(
                    subject,
                    "formula schema, relation name, class, and graph variables align",
                )
            )
    return results


def _validate_relation_point_set(
    manifest: SubstitutionGraphFormulaSchemaRelationManifest,
    relation_points: tuple[SubstitutionGraphFormulaSchemaRelationPoint, ...],
) -> list[SubstitutionGraphFormulaSchemaRelationValidation]:
    results: list[SubstitutionGraphFormulaSchemaRelationValidation] = []
    point_ids = [point.point_id for point in relation_points]
    duplicate_ids = _duplicates(point_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "relation_point_ids",
                "duplicate relation point ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("relation_point_ids", "relation point ids are unique"))

    if len(relation_points) != manifest.expected_relation_point_count:
        results.append(
            _rejected(
                "expected_relation_point_count",
                "relation point count mismatch: expected "
                + str(manifest.expected_relation_point_count)
                + " got "
                + str(len(relation_points)),
            )
        )
    else:
        results.append(
            _accepted(
                "expected_relation_point_count",
                f"checked {len(relation_points)} relation point(s)",
            )
        )

    source_kinds = {point.source_kind for point in relation_points}
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
        point.point_id
        for point in relation_points
        if not _relation_point_accepted(point)
    ]
    if failures:
        results.append(
            _rejected(
                "relation_points",
                "relation failures: " + ", ".join(failures),
            )
        )
    else:
        results.append(
            _accepted(
                "relation_points",
                f"checked {len(relation_points)} formula-schema relation point(s)",
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


def _relation_point_accepted(
    point: SubstitutionGraphFormulaSchemaRelationPoint,
) -> bool:
    return (
        point.schema_instance_closed
        and point.formula_code_roundtrips
        and point.decoded_formula_matches_source
        and point.input_matches_expected_surface
        and point.relation_holds
        and point.output_matches_expected_surface
    )


def _schema_node(graph_variables: dict[str, str]) -> dict[str, Any]:
    return {
        "kind": "equals",
        "left": {
            "kind": "substitution_code",
            "left": {
                "kind": "variable",
                "name": graph_variables.get("formula_code", ""),
            },
            "right": {
                "kind": "variable",
                "name": graph_variables.get("argument_code", ""),
            },
        },
        "right": {
            "kind": "variable",
            "name": graph_variables.get("output_code", ""),
        },
    }


def _find_graph_target(
    graph_targets: tuple[SubstitutionGraphTarget, ...],
    target_id: str,
) -> SubstitutionGraphTarget:
    for graph_target in graph_targets:
        if graph_target.target_id == target_id:
            return graph_target
    raise ValueError(f"unknown substitution graph target: {target_id}")


def _find_witness(
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    witness_id: str,
) -> SubstitutionRepresentabilityWitness:
    for witness in witnesses:
        if witness.witness_id == witness_id:
            return witness
    raise ValueError(f"unknown substitution witness: {witness_id}")


def _find_witness_observation(
    observations: tuple[SubstitutionRepresentabilityObservation, ...],
    witness_id: str,
) -> SubstitutionRepresentabilityObservation:
    for observation in observations:
        if observation.witness_id == witness_id:
            return observation
    raise ValueError(f"missing witness observation: {witness_id}")


def _failed_subject_for_result(subject: str) -> str:
    if subject == "expected_relation_point_count":
        return "substitution-graph-formula-schema-relation-count"
    if subject in {"relation_point_ids", "relation_points"}:
        return "substitution-graph-formula-schema-relation-point"
    if subject == "required_source_kinds":
        return "substitution-graph-formula-schema-relation-source-kind"
    if subject == "required_future_work":
        return "substitution-graph-formula-schema-relation-future-work"
    if subject == "non_claims":
        return "substitution-graph-formula-schema-relation-non-claim"
    if subject.endswith(".schema_alignment"):
        return "substitution-graph-formula-schema-relation-schema"
    if subject in {
        "codebook",
        "substitution_graph",
        "formula_candidate",
        "evaluation_examples",
        "substitution_representability",
    }:
        return "substitution-graph-formula-schema-relation-dependency"
    if subject.endswith("_path"):
        return "substitution-graph-formula-schema-relation-reference"
    return "substitution-graph-formula-schema-relation"


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
) -> SubstitutionGraphFormulaSchemaRelationValidation:
    return SubstitutionGraphFormulaSchemaRelationValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphFormulaSchemaRelationValidation:
    return SubstitutionGraphFormulaSchemaRelationValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_formula_schema_relation_cli())
