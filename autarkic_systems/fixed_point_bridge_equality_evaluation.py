"""Finite evaluation for the fixed-point bridge-equality construction case.

This module evaluates the current left bridge term
``substitution_code(quote(seed), quote(seed))`` at the meta level and checks
that its output tokens match the right bridge term ``quote(diagonal_instance)``.
It is finite evaluation evidence only; it does not prove the general bridge
equality, a fixed-point equation, an arithmetized proof predicate, or
self-consistency.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.diagonal_construction import (
    build_diagonal_instance_code,
    build_diagonal_seed_node,
)
from autarkic_systems.fixed_point import (
    load_fixed_point_targets,
    validate_fixed_point_targets,
)
from autarkic_systems.fixed_point_bridge_equality_alignment import (
    load_fixed_point_bridge_equality_alignment,
    validate_fixed_point_bridge_equality_alignment,
)
from autarkic_systems.fixed_point_construction_cases import (
    load_fixed_point_construction_cases,
)
from autarkic_systems.fixed_point_equation_bridge import (
    FixedPointEquationBridgeObservation,
    load_fixed_point_equation_bridge_targets,
    validate_fixed_point_equation_bridge_targets,
)
from autarkic_systems.formal_code import (
    decode_code,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation import numeral_to_natural
from autarkic_systems.formal_quotation_term import quote_tokens_as_term
from autarkic_systems.formal_substitution import substitute_node
from autarkic_systems.substitution_representability import (
    build_substitution_witness_output_code,
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)


DEFAULT_EVALUATION = Path("claims/fixed_point_bridge_equality_evaluation.json")
DEFAULT_FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = ("bridge-equality-evaluation",)
REQUIRED_FUTURE_WORK = (
    "bridge-equality-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
REQUIRED_NON_CLAIMS = (
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
REQUIRED_CONSTRUCTION_DEPENDENCIES = (
    "fixed_point_equation_bridge",
    "substitution_representability",
    "substitution_graph_correctness_cases",
    "bridge_equality_alignment",
    "bridge_equality_evaluation",
)


@dataclass(frozen=True)
class FixedPointBridgeEqualityEvaluationManifest:
    """Loaded manifest for finite bridge-equality evaluation evidence."""

    path: Path
    schema_version: int
    evaluation_set_id: str
    reviewed_at: str
    purpose: str
    fixed_point_construction_cases_path: str
    fixed_point_targets_path: str
    fixed_point_equation_bridge_targets_path: str
    substitution_representability_targets_path: str
    bridge_equality_alignment_path: str
    codebook_path: str
    expected_evaluation_count: int
    expected_formula_code_length: int
    expected_argument_code_length: int
    expected_output_code_length: int
    expected_bridge_equation_code_length: int
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityEvaluationValidation:
    """One validation result for bridge-equality evaluation evidence."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityEvaluation:
    """One finite bridge-equality evaluation check."""

    evaluation_id: str
    source_kind: str
    target_id: str
    construction_case_id: str
    equation_bridge_id: str
    witness_id: str
    bridge_equality_alignment_id: str
    formula_code_length: int
    argument_code_length: int
    output_code_length: int
    right_quoted_code_length: int
    bridge_equation_code_length: int
    construction_case_is_open: bool
    construction_case_requires_evaluation: bool
    left_term_is_substitution_code: bool
    left_formula_decodes_to_seed: bool
    self_application_argument_matches_seed: bool
    evaluated_output_matches_witness: bool
    evaluated_output_matches_right_quote: bool
    bridge_equality_alignment_accepted: bool
    route_ids_match: bool
    all_dependencies_accepted: bool


@dataclass(frozen=True)
class FixedPointBridgeEqualityEvaluationReport:
    """Validation report over finite bridge-equality evaluation evidence."""

    manifest: FixedPointBridgeEqualityEvaluationManifest
    fixed_point_construction_cases_path: Path
    fixed_point_targets_path: Path
    fixed_point_equation_bridge_targets_path: Path
    substitution_representability_targets_path: Path
    bridge_equality_alignment_path: Path
    codebook_path: Path
    formal_language_path: Path
    willard_map_path: Path
    results: tuple[FixedPointBridgeEqualityEvaluationValidation, ...]
    evaluations: tuple[FixedPointBridgeEqualityEvaluation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every bridge-equality evaluation validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def evaluation_count(self) -> int:
        """Return the number of checked bridge-equality evaluations."""

        return len(self.evaluations)

    @property
    def source_kind_counts(self) -> dict[str, int]:
        """Return observed evaluation counts grouped by source kind."""

        counts = {source_kind: 0 for source_kind in REQUIRED_SOURCE_KINDS}
        for evaluation in self.evaluations:
            counts[evaluation.source_kind] = (
                counts.get(evaluation.source_kind, 0) + 1
            )
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


@dataclass(frozen=True)
class _DependencyFailure:
    """Small report shim for dependencies that cannot be loaded."""

    accepted: bool
    failed_subjects: tuple[str, ...]


def load_fixed_point_bridge_equality_evaluation(
    path: Path | str = DEFAULT_EVALUATION,
) -> FixedPointBridgeEqualityEvaluationManifest:
    """Load the bridge-equality evaluation manifest from JSON."""

    evaluation_path = Path(path)
    data = json.loads(evaluation_path.read_text(encoding="utf-8"))
    return FixedPointBridgeEqualityEvaluationManifest(
        path=evaluation_path,
        schema_version=_required_int(data, "schema_version"),
        evaluation_set_id=_required_text(data, "evaluation_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        fixed_point_construction_cases_path=_required_text(
            data,
            "fixed_point_construction_cases_path",
        ),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        fixed_point_equation_bridge_targets_path=_required_text(
            data,
            "fixed_point_equation_bridge_targets_path",
        ),
        substitution_representability_targets_path=_required_text(
            data,
            "substitution_representability_targets_path",
        ),
        bridge_equality_alignment_path=_required_text(
            data,
            "bridge_equality_alignment_path",
        ),
        codebook_path=_required_text(data, "codebook_path"),
        expected_evaluation_count=_required_int(data, "expected_evaluation_count"),
        expected_formula_code_length=_required_int(
            data,
            "expected_formula_code_length",
        ),
        expected_argument_code_length=_required_int(
            data,
            "expected_argument_code_length",
        ),
        expected_output_code_length=_required_int(
            data,
            "expected_output_code_length",
        ),
        expected_bridge_equation_code_length=_required_int(
            data,
            "expected_bridge_equation_code_length",
        ),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_bridge_equality_evaluation(
    manifest: FixedPointBridgeEqualityEvaluationManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
    formal_language_path: Path | str = DEFAULT_FORMAL_LANGUAGE,
) -> FixedPointBridgeEqualityEvaluationReport:
    """Validate finite bridge-equality evaluation evidence.

    The loaded manifest dataclass is immutable, so a process-local cache can
    safely reuse the expensive derived report for repeated aggregate checks.
    Tests that mutate a manifest write a fresh file and therefore load a
    distinct manifest value, which receives its own fail-closed validation.
    """

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(formal_language_path)
    checked_construction_cases_path = Path(
        manifest.fixed_point_construction_cases_path
    )
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)
    checked_equation_bridge_path = Path(
        manifest.fixed_point_equation_bridge_targets_path
    )
    checked_witness_path = Path(manifest.substitution_representability_targets_path)
    checked_bridge_equality_alignment_path = Path(
        manifest.bridge_equality_alignment_path
    )
    checked_codebook_path = Path(manifest.codebook_path)

    construction_cases: Any = None
    fixed_point_targets: Any = None
    equation_bridge: Any = None
    substitution_witnesses: Any = None
    bridge_equality_alignment: Any = None
    codebook: Any = None

    try:
        construction_cases = load_fixed_point_construction_cases(
            checked_construction_cases_path
        )
        construction_case_report: Any = _DependencyFailure(True, ())
    except (OSError, ValueError, json.JSONDecodeError):
        construction_case_report = _DependencyFailure(
            False,
            ("fixed-point-construction-cases-load",),
        )

    try:
        fixed_point_targets = load_fixed_point_targets(checked_fixed_point_path)
        fixed_point_report: Any = validate_fixed_point_targets(
            fixed_point_targets,
            checked_willard_map_path,
            checked_language_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        fixed_point_report = _DependencyFailure(False, ("fixed-point-target-load",))

    try:
        equation_bridge = load_fixed_point_equation_bridge_targets(
            checked_equation_bridge_path
        )
        equation_bridge_report: Any = validate_fixed_point_equation_bridge_targets(
            equation_bridge,
            checked_language_path,
            checked_willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        equation_bridge_report = _DependencyFailure(
            False,
            ("fixed-point-equation-bridge-load",),
        )

    try:
        substitution_witnesses = load_substitution_representability_targets(
            checked_witness_path
        )
        substitution_witness_report: Any = validate_substitution_representability_targets(
            substitution_witnesses,
            checked_language_path,
            checked_willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        substitution_witness_report = _DependencyFailure(
            False,
            ("substitution-witness-load",),
        )

    try:
        bridge_equality_alignment = load_fixed_point_bridge_equality_alignment(
            checked_bridge_equality_alignment_path
        )
        bridge_equality_alignment_report: Any = (
            validate_fixed_point_bridge_equality_alignment(
                bridge_equality_alignment,
                checked_willard_map_path,
            )
        )
    except (OSError, ValueError, json.JSONDecodeError):
        bridge_equality_alignment_report = _DependencyFailure(
            False,
            ("bridge-equality-alignment-load",),
        )

    try:
        codebook = load_formal_codebook(checked_codebook_path)
        codebook_report: Any = validate_formal_codebook(
            codebook,
            checked_language_path,
            checked_willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        codebook_report = _DependencyFailure(False, ("codebook-load",))

    results: list[FixedPointBridgeEqualityEvaluationValidation] = [
        _accepted("manifest", f"loaded {manifest.evaluation_set_id}")
    ]
    results.extend(_validate_references(manifest))
    results.extend(_validate_manifest_lists(manifest))
    results.extend(
        _validate_dependency_reports(
            construction_case_report,
            fixed_point_report,
            equation_bridge_report,
            substitution_witness_report,
            bridge_equality_alignment_report,
            codebook_report,
        )
    )

    evaluations: tuple[FixedPointBridgeEqualityEvaluation, ...] = ()
    dependency_statuses = (
        construction_case_report,
        fixed_point_report,
        equation_bridge_report,
        substitution_witness_report,
        bridge_equality_alignment_report,
        codebook_report,
    )
    can_derive = (
        all(report.accepted for report in dependency_statuses)
        and construction_cases is not None
        and fixed_point_targets is not None
        and equation_bridge is not None
        and substitution_witnesses is not None
        and bridge_equality_alignment is not None
        and codebook is not None
    )
    if can_derive:
        try:
            evaluations = _derive_evaluations(
                construction_cases,
                fixed_point_targets.targets,
                equation_bridge,
                equation_bridge_report.observations,
                substitution_witnesses.witnesses,
                bridge_equality_alignment_report.alignments,
                checked_fixed_point_path,
                checked_equation_bridge_path,
                checked_witness_path,
                checked_codebook_path,
                codebook,
            )
        except ValueError as exc:
            results.append(_rejected("evaluations", str(exc)))
    else:
        results.append(
            _rejected(
                "evaluations",
                "dependency load or validation failed; evaluation not derived",
            )
        )
    results.extend(_validate_evaluation_set(manifest, evaluations))

    return FixedPointBridgeEqualityEvaluationReport(
        manifest=manifest,
        fixed_point_construction_cases_path=checked_construction_cases_path,
        fixed_point_targets_path=checked_fixed_point_path,
        fixed_point_equation_bridge_targets_path=checked_equation_bridge_path,
        substitution_representability_targets_path=checked_witness_path,
        bridge_equality_alignment_path=checked_bridge_equality_alignment_path,
        codebook_path=checked_codebook_path,
        formal_language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        evaluations=evaluations,
    )


def fixed_point_bridge_equality_evaluation_payload(
    report: FixedPointBridgeEqualityEvaluationReport,
) -> dict[str, Any]:
    """Return a JSON-ready bridge-equality evaluation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "evaluation_manifest": str(report.manifest.path),
        "evaluation_set_id": report.manifest.evaluation_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "fixed_point_construction_cases_path": str(
            report.fixed_point_construction_cases_path
        ),
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "substitution_representability_targets_path": str(
            report.substitution_representability_targets_path
        ),
        "bridge_equality_alignment_path": str(
            report.bridge_equality_alignment_path
        ),
        "codebook_path": str(report.codebook_path),
        "formal_language_path": str(report.formal_language_path),
        "willard_map": str(report.willard_map_path),
        "expected_evaluation_count": report.manifest.expected_evaluation_count,
        "evaluation_count": report.evaluation_count,
        "source_kind_counts": report.source_kind_counts,
        "required_source_kinds": list(report.manifest.required_source_kinds),
        "required_future_work": list(report.manifest.required_future_work),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "evaluations": [
            {
                "evaluation_id": evaluation.evaluation_id,
                "source_kind": evaluation.source_kind,
                "target_id": evaluation.target_id,
                "construction_case_id": evaluation.construction_case_id,
                "equation_bridge_id": evaluation.equation_bridge_id,
                "witness_id": evaluation.witness_id,
                "bridge_equality_alignment_id": (
                    evaluation.bridge_equality_alignment_id
                ),
                "observed_formula_code_length": evaluation.formula_code_length,
                "observed_argument_code_length": evaluation.argument_code_length,
                "observed_output_code_length": evaluation.output_code_length,
                "observed_right_quoted_code_length": (
                    evaluation.right_quoted_code_length
                ),
                "observed_bridge_equation_code_length": (
                    evaluation.bridge_equation_code_length
                ),
                "observed_construction_case_is_open": (
                    evaluation.construction_case_is_open
                ),
                "observed_construction_case_requires_evaluation": (
                    evaluation.construction_case_requires_evaluation
                ),
                "observed_left_term_is_substitution_code": (
                    evaluation.left_term_is_substitution_code
                ),
                "observed_left_formula_decodes_to_seed": (
                    evaluation.left_formula_decodes_to_seed
                ),
                "observed_self_application_argument_matches_seed": (
                    evaluation.self_application_argument_matches_seed
                ),
                "observed_evaluated_output_matches_witness": (
                    evaluation.evaluated_output_matches_witness
                ),
                "observed_evaluated_output_matches_right_quote": (
                    evaluation.evaluated_output_matches_right_quote
                ),
                "observed_bridge_equality_alignment_accepted": (
                    evaluation.bridge_equality_alignment_accepted
                ),
                "observed_route_ids_match": evaluation.route_ids_match,
                "observed_all_dependencies_accepted": (
                    evaluation.all_dependencies_accepted
                ),
            }
            for evaluation in report.evaluations
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


def format_fixed_point_bridge_equality_evaluation_report(
    report: FixedPointBridgeEqualityEvaluationReport,
) -> str:
    """Format a concise bridge-equality evaluation report."""

    status = "accepted" if report.accepted else "rejected"
    failures = [
        evaluation.evaluation_id
        for evaluation in report.evaluations
        if not _evaluation_accepted(evaluation)
    ]
    source_counts = ", ".join(
        f"{source_kind}={count}"
        for source_kind, count in report.source_kind_counts.items()
    )
    lines = [
        f"Fixed-point bridge equality evaluation: {status}",
        f"Evaluation set: {report.manifest.evaluation_set_id}",
        f"Bridge-equality evaluations: {report.evaluation_count}",
        f"Source kinds: {source_counts}",
        f"Evaluation failures: {_joined_or_none(tuple(failures))}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for evaluation in report.evaluations:
        lines.extend(
            (
                f"Evaluation {evaluation.evaluation_id}:",
                f"  Formula code length: {evaluation.formula_code_length}",
                f"  Argument code length: {evaluation.argument_code_length}",
                f"  Output code length: {evaluation.output_code_length}",
                f"  Right quoted code length: {evaluation.right_quoted_code_length}",
                (
                    "  Bridge equation code length: "
                    f"{evaluation.bridge_equation_code_length}"
                ),
                (
                    "  Checks: "
                    f"construction_case_open={evaluation.construction_case_is_open}, "
                    "requires_evaluation="
                    f"{evaluation.construction_case_requires_evaluation}, "
                    "left_term_substitution_code="
                    f"{evaluation.left_term_is_substitution_code}, "
                    "left_formula_decodes_to_seed="
                    f"{evaluation.left_formula_decodes_to_seed}, "
                    "self_application_argument_matches_seed="
                    f"{evaluation.self_application_argument_matches_seed}, "
                    "output_matches_witness="
                    f"{evaluation.evaluated_output_matches_witness}, "
                    "output_matches_right_quote="
                    f"{evaluation.evaluated_output_matches_right_quote}, "
                    "alignment_accepted="
                    f"{evaluation.bridge_equality_alignment_accepted}, "
                    f"route_ids_match={evaluation.route_ids_match}, "
                    "dependencies_accepted="
                    f"{evaluation.all_dependencies_accepted}"
                ),
            )
        )
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_bridge_equality_evaluation_cli(
    argv: list[str] | None = None,
) -> int:
    """Run finite bridge-equality evaluation validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_bridge_equality_evaluation",
        description="Validate AS fixed-point bridge-equality evaluation evidence.",
    )
    parser.add_argument(
        "--evaluation",
        default=str(DEFAULT_EVALUATION),
        help="Path to the bridge-equality evaluation manifest.",
    )
    parser.add_argument(
        "--willard-map",
        default=str(DEFAULT_WILLARD_MAP),
        help="Path to the Willard definition map.",
    )
    parser.add_argument(
        "--language",
        default=str(DEFAULT_FORMAL_LANGUAGE),
        help="Path to the formal arithmetic language manifest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_fixed_point_bridge_equality_evaluation(args.evaluation)
    report = validate_fixed_point_bridge_equality_evaluation(
        manifest,
        args.willard_map,
        args.language,
    )
    if args.format == "json":
        print(json.dumps(
            fixed_point_bridge_equality_evaluation_payload(report),
            sort_keys=True,
        ))
    else:
        print(format_fixed_point_bridge_equality_evaluation_report(report))
    return 0 if report.accepted else 1


def _derive_evaluations(
    construction_cases: Any,
    fixed_point_targets: tuple[Any, ...],
    equation_bridge: Any,
    equation_observations: tuple[FixedPointEquationBridgeObservation, ...],
    witnesses: tuple[Any, ...],
    bridge_equality_alignments: tuple[Any, ...],
    fixed_point_targets_path: Path,
    equation_bridge_targets_path: Path,
    witness_targets_path: Path,
    codebook_path: Path,
    codebook: Any,
) -> tuple[FixedPointBridgeEqualityEvaluation, ...]:
    construction_case = _find_case(construction_cases.cases, "bridge-equality-proof")
    target = _find_target(fixed_point_targets, construction_case.target_id)
    equation_observation = _find_equation_observation(
        equation_observations,
        construction_case.target_id,
    )
    bridge_equality_alignment = _find_bridge_equality_alignment(
        bridge_equality_alignments,
        construction_case.target_id,
        equation_observation.bridge_id,
    )
    witness = _find_witness(witnesses, equation_observation.witness_id)

    seed_node = build_diagonal_seed_node(target)
    seed_code = encode_node(seed_node, codebook)
    seed_quote = quote_tokens_as_term(seed_code)
    diagonal_instance_code = build_diagonal_instance_code(
        construction_id=equation_observation.construction_id,
        targets_path=equation_bridge.diagonal_construction_targets_path,
        fixed_point_targets_path=fixed_point_targets_path,
        codebook_path=codebook_path,
    )
    diagonal_instance_node = substitute_node(
        seed_node,
        witness.variable,
        seed_quote,
    )
    direct_target_slot = quote_tokens_as_term(diagonal_instance_code)
    direct_target_node = substitute_node(
        target.template_node,
        target.template_variable,
        direct_target_slot,
    )
    left_term = _target_slot(diagonal_instance_node)
    right_term = _target_slot(direct_target_node)
    formula_code, argument_code, decoded_formula, evaluated_output_code = (
        _evaluate_substitution_code_term(left_term, witness.variable, codebook)
    )
    right_quoted_code = _tokens_from_quotation_term(right_term)
    witness_output_code = build_substitution_witness_output_code(
        witness_id=equation_observation.witness_id,
        targets_path=witness_targets_path,
        diagonal_targets_path=equation_bridge.diagonal_construction_targets_path,
        fixed_point_targets_path=fixed_point_targets_path,
        codebook_path=codebook_path,
    )
    route_ids_match = (
        construction_case.target_id
        == target.target_id
        == equation_observation.target_id
        == bridge_equality_alignment.target_id
        and equation_observation.bridge_id
        == bridge_equality_alignment.equation_bridge_id
        and equation_observation.witness_id == witness.witness_id
    )
    return (
        FixedPointBridgeEqualityEvaluation(
            evaluation_id="AS-FIXED-POINT-BRIDGE-EQUALITY-EVALUATION",
            source_kind="bridge-equality-evaluation",
            target_id=construction_case.target_id,
            construction_case_id=construction_case.case_id,
            equation_bridge_id=equation_observation.bridge_id,
            witness_id=witness.witness_id,
            bridge_equality_alignment_id=bridge_equality_alignment.alignment_id,
            formula_code_length=len(formula_code),
            argument_code_length=len(argument_code),
            output_code_length=len(evaluated_output_code),
            right_quoted_code_length=len(right_quoted_code),
            bridge_equation_code_length=(
                equation_observation.bridge_equation_code_length
            ),
            construction_case_is_open=construction_case.status == "proof-case-open",
            construction_case_requires_evaluation=(
                construction_case.required_dependency_subjects
                == REQUIRED_CONSTRUCTION_DEPENDENCIES
            ),
            left_term_is_substitution_code=left_term.get("kind") == "substitution_code",
            left_formula_decodes_to_seed=decoded_formula == seed_node,
            self_application_argument_matches_seed=(
                formula_code == argument_code == seed_code
            ),
            evaluated_output_matches_witness=(
                evaluated_output_code == witness_output_code
            ),
            evaluated_output_matches_right_quote=(
                evaluated_output_code == right_quoted_code == diagonal_instance_code
            ),
            bridge_equality_alignment_accepted=(
                bridge_equality_alignment.route_ids_match
                and bridge_equality_alignment.bridge_equation_matches_schema_instance
            ),
            route_ids_match=route_ids_match,
            all_dependencies_accepted=True,
        ),
    )


def _validate_references(
    manifest: FixedPointBridgeEqualityEvaluationManifest,
) -> list[FixedPointBridgeEqualityEvaluationValidation]:
    expected = (
        (
            "fixed_point_construction_cases_path",
            manifest.fixed_point_construction_cases_path,
            "claims/fixed_point_construction_cases.json",
        ),
        (
            "fixed_point_targets_path",
            manifest.fixed_point_targets_path,
            "claims/fixed_point_targets.json",
        ),
        (
            "fixed_point_equation_bridge_targets_path",
            manifest.fixed_point_equation_bridge_targets_path,
            "claims/fixed_point_equation_bridge_targets.json",
        ),
        (
            "substitution_representability_targets_path",
            manifest.substitution_representability_targets_path,
            "claims/substitution_representability_targets.json",
        ),
        (
            "bridge_equality_alignment_path",
            manifest.bridge_equality_alignment_path,
            "claims/fixed_point_bridge_equality_alignment.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
    )
    results: list[FixedPointBridgeEqualityEvaluationValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_manifest_lists(
    manifest: FixedPointBridgeEqualityEvaluationManifest,
) -> list[FixedPointBridgeEqualityEvaluationValidation]:
    results: list[FixedPointBridgeEqualityEvaluationValidation] = []
    if manifest.required_source_kinds == REQUIRED_SOURCE_KINDS:
        results.append(_accepted("required_source_kinds", "source kinds match"))
    else:
        results.append(_rejected("required_source_kinds", "source kind mismatch"))

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

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))
    return results


def _validate_dependency_reports(
    construction_case_report: Any,
    fixed_point_report: Any,
    equation_bridge_report: Any,
    substitution_witness_report: Any,
    bridge_equality_alignment_report: Any,
    codebook_report: Any,
) -> list[FixedPointBridgeEqualityEvaluationValidation]:
    checks = (
        (
            "fixed_point_construction_cases",
            construction_case_report,
            "fixed-point construction cases",
        ),
        ("fixed_point", fixed_point_report, "fixed-point target"),
        (
            "fixed_point_equation_bridge",
            equation_bridge_report,
            "fixed-point equation bridge",
        ),
        (
            "substitution_representability",
            substitution_witness_report,
            "substitution witness",
        ),
        (
            "bridge_equality_alignment",
            bridge_equality_alignment_report,
            "fixed-point bridge equality alignment",
        ),
        ("codebook", codebook_report, "formal codebook"),
    )
    results: list[FixedPointBridgeEqualityEvaluationValidation] = []
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


def _validate_evaluation_set(
    manifest: FixedPointBridgeEqualityEvaluationManifest,
    evaluations: tuple[FixedPointBridgeEqualityEvaluation, ...],
) -> list[FixedPointBridgeEqualityEvaluationValidation]:
    results: list[FixedPointBridgeEqualityEvaluationValidation] = []
    if len(evaluations) == manifest.expected_evaluation_count:
        results.append(
            _accepted(
                "expected_evaluation_count",
                f"evaluation count {len(evaluations)} matches manifest",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_evaluation_count",
                "evaluation count mismatch: expected "
                f"{manifest.expected_evaluation_count} but found {len(evaluations)}",
            )
        )

    if len(evaluations) != 1:
        return results
    evaluation = evaluations[0]
    length_checks = (
        (
            "expected_formula_code_length",
            manifest.expected_formula_code_length,
            evaluation.formula_code_length,
            "formula code length",
        ),
        (
            "expected_argument_code_length",
            manifest.expected_argument_code_length,
            evaluation.argument_code_length,
            "argument code length",
        ),
        (
            "expected_output_code_length",
            manifest.expected_output_code_length,
            evaluation.output_code_length,
            "output length",
        ),
        (
            "expected_bridge_equation_code_length",
            manifest.expected_bridge_equation_code_length,
            evaluation.bridge_equation_code_length,
            "bridge equation length",
        ),
    )
    for subject, expected, actual, label in length_checks:
        if expected == actual:
            results.append(_accepted(subject, f"{label} matches manifest"))
        else:
            results.append(
                _rejected(
                    subject,
                    f"{label} mismatch: expected {expected} but found {actual}",
                )
            )

    bool_checks = (
        (
            "evaluation.construction_case_is_open",
            evaluation.construction_case_is_open,
            "construction case remains open",
            "construction case is not open",
        ),
        (
            "evaluation.construction_case_requires_evaluation",
            evaluation.construction_case_requires_evaluation,
            "construction case requires bridge-equality evaluation",
            "construction case does not require bridge-equality evaluation",
        ),
        (
            "evaluation.left_term_is_substitution_code",
            evaluation.left_term_is_substitution_code,
            "left bridge term is substitution_code",
            "left bridge term is not substitution_code",
        ),
        (
            "evaluation.left_formula_decodes_to_seed",
            evaluation.left_formula_decodes_to_seed,
            "left formula quotation decodes to the seed",
            "left formula quotation does not decode to the seed",
        ),
        (
            "evaluation.self_application_argument_matches_seed",
            evaluation.self_application_argument_matches_seed,
            "self-application argument matches the seed code",
            "self-application argument diverges from the seed code",
        ),
        (
            "evaluation.evaluated_output_matches_witness",
            evaluation.evaluated_output_matches_witness,
            "evaluated output matches the substitution witness",
            "evaluated output does not match the substitution witness",
        ),
        (
            "evaluation.evaluated_output_matches_right_quote",
            evaluation.evaluated_output_matches_right_quote,
            "evaluated output matches the right quoted bridge term",
            "evaluated output does not match the right quoted bridge term",
        ),
        (
            "evaluation.bridge_equality_alignment_accepted",
            evaluation.bridge_equality_alignment_accepted,
            "bridge-equality alignment remains accepted",
            "bridge-equality alignment is not accepted",
        ),
        (
            "evaluation.route_ids_match",
            evaluation.route_ids_match,
            "target, bridge, and witness route ids match",
            "target, bridge, or witness route ids diverge",
        ),
        (
            "evaluation.all_dependencies_accepted",
            evaluation.all_dependencies_accepted,
            "all dependency surfaces accepted",
            "one or more dependency surfaces rejected",
        ),
    )
    for subject, accepted, ok_detail, fail_detail in bool_checks:
        if accepted:
            results.append(_accepted(subject, ok_detail))
        else:
            results.append(_rejected(subject, fail_detail))
    return results


def _evaluation_accepted(evaluation: FixedPointBridgeEqualityEvaluation) -> bool:
    return (
        evaluation.construction_case_is_open
        and evaluation.construction_case_requires_evaluation
        and evaluation.left_term_is_substitution_code
        and evaluation.left_formula_decodes_to_seed
        and evaluation.self_application_argument_matches_seed
        and evaluation.evaluated_output_matches_witness
        and evaluation.evaluated_output_matches_right_quote
        and evaluation.bridge_equality_alignment_accepted
        and evaluation.route_ids_match
        and evaluation.all_dependencies_accepted
    )


def _evaluate_substitution_code_term(
    term: dict[str, Any],
    variable: str,
    codebook: Any,
) -> tuple[tuple[int, ...], tuple[int, ...], dict[str, Any], tuple[int, ...]]:
    if term.get("kind") != "substitution_code":
        raise ValueError("left bridge term is not substitution_code")
    formula_code = _tokens_from_quotation_term(_required_node(term, "left"))
    argument_code = _tokens_from_quotation_term(_required_node(term, "right"))
    formula_node = decode_code(formula_code, codebook)
    output_node = substitute_node(
        formula_node,
        variable,
        quote_tokens_as_term(argument_code),
    )
    output_code = encode_node(output_node, codebook)
    return formula_code, argument_code, formula_node, output_code


def _tokens_from_quotation_term(term: dict[str, Any]) -> tuple[int, ...]:
    tokens: list[int] = []
    current = term
    while True:
        kind = current.get("kind")
        if kind == "sequence_nil":
            return tuple(tokens)
        if kind != "sequence_cons":
            raise ValueError("quotation term must be sequence_cons/sequence_nil")
        tokens.append(numeral_to_natural(_required_node(current, "head")))
        current = _required_node(current, "tail")


def _target_slot(node: dict[str, Any]) -> dict[str, Any]:
    if node.get("kind") not in {"pi1", "sigma1"}:
        raise ValueError("bridge target must be a pi1 or sigma1 sentence")
    body = _required_node(node, "body")
    if body.get("kind") != "less_than":
        raise ValueError("bridge target body must be less_than")
    return _required_node(body, "right")


def _find_case(cases: tuple[Any, ...], case_kind: str) -> Any:
    for case in cases:
        if case.case_kind == case_kind:
            return case
    raise ValueError(f"missing construction case kind: {case_kind}")


def _find_witness(witnesses: tuple[Any, ...], witness_id: str) -> Any:
    for witness in witnesses:
        if witness.witness_id == witness_id:
            return witness
    raise ValueError(f"missing substitution witness: {witness_id}")


def _find_target(targets: tuple[Any, ...], target_id: str) -> Any:
    matches = [target for target in targets if target.target_id == target_id]
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one fixed-point target {target_id}, found {len(matches)}"
        )
    return matches[0]


def _find_equation_observation(
    observations: tuple[FixedPointEquationBridgeObservation, ...],
    target_id: str,
) -> FixedPointEquationBridgeObservation:
    matches = [
        observation
        for observation in observations
        if observation.target_id == target_id
    ]
    if len(matches) != 1:
        raise ValueError(
            "expected exactly one fixed-point equation bridge observation "
            f"for {target_id}, found {len(matches)}"
        )
    return matches[0]


def _find_bridge_equality_alignment(
    alignments: tuple[Any, ...],
    target_id: str,
    equation_bridge_id: str,
) -> Any:
    matches = [
        alignment
        for alignment in alignments
        if alignment.target_id == target_id
        and alignment.equation_bridge_id == equation_bridge_id
    ]
    if len(matches) != 1:
        raise ValueError(
            "expected exactly one bridge-equality alignment for "
            f"{target_id}/{equation_bridge_id}, found {len(matches)}"
        )
    return matches[0]


def _required_node(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a node")
    return value


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointBridgeEqualityEvaluationValidation:
    return FixedPointBridgeEqualityEvaluationValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointBridgeEqualityEvaluationValidation:
    return FixedPointBridgeEqualityEvaluationValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "expected_evaluation_count":
        return "fixed-point-bridge-equality-evaluation-count"
    if subject == "expected_output_code_length":
        return "fixed-point-bridge-equality-evaluation-output-length"
    if subject == "expected_bridge_equation_code_length":
        return "fixed-point-bridge-equality-evaluation-bridge-length"
    if subject in {"expected_formula_code_length", "expected_argument_code_length"}:
        return "fixed-point-bridge-equality-evaluation-input-length"
    if subject == "non_claims":
        return "fixed-point-bridge-equality-evaluation-non-claim"
    if subject == "required_future_work":
        return "fixed-point-bridge-equality-evaluation-future-work"
    if subject == "required_source_kinds":
        return "fixed-point-bridge-equality-evaluation-source-kind"
    if subject == "next_as_action":
        return "fixed-point-bridge-equality-evaluation-next-action"
    if subject == "evaluations":
        return "fixed-point-bridge-equality-evaluation-derivation"
    if subject.startswith("evaluation."):
        return "fixed-point-bridge-equality-evaluation-check"
    if subject.endswith("_path"):
        return "fixed-point-bridge-equality-evaluation-path"
    return subject


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return value


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_bridge_equality_evaluation_cli())
