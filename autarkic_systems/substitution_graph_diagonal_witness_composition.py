"""Finite diagonal-witness composition domain for substitution graph evidence.

This module checks that the current substitution graph correctness target,
formula-schema relation witness point, substitution-representability witness,
diagonal seed, and fixed-point target all identify the same concrete
self-application route. It is finite executable evidence for the fifth
correctness proof case, not a diagonal lemma or representability proof.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.diagonal_construction import (
    DiagonalConstructionObservation,
    DiagonalConstructionTarget,
    build_diagonal_instance_code,
    load_diagonal_construction_targets,
    validate_diagonal_construction_targets,
)
from autarkic_systems.fixed_point import (
    FixedPointTarget,
    load_fixed_point_targets,
    validate_fixed_point_targets,
)
from autarkic_systems.formal_code import (
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.substitution_graph_correctness import (
    SubstitutionGraphCorrectnessTarget,
    load_substitution_graph_correctness_targets,
    validate_substitution_graph_correctness_targets,
)
from autarkic_systems.substitution_graph_formula import (
    SubstitutionGraphFormulaCandidate,
    load_substitution_graph_formula_candidates,
    validate_substitution_graph_formula_candidates,
)
from autarkic_systems.substitution_graph_formula_schema_relation import (
    SubstitutionGraphFormulaSchemaRelationPoint,
    load_substitution_graph_formula_schema_relation,
    validate_substitution_graph_formula_schema_relation,
)
from autarkic_systems.substitution_representability import (
    SubstitutionRepresentabilityObservation,
    SubstitutionRepresentabilityWitness,
    build_substitution_witness_output_code,
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)


DEFAULT_COMPOSITION = Path(
    "claims/substitution_graph_diagonal_witness_composition.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = ("diagonal-witness",)
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
class SubstitutionGraphDiagonalWitnessCompositionManifest:
    """Loaded manifest for the current diagonal-witness composition domain."""

    path: Path
    schema_version: int
    composition_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    correctness_targets_path: str
    formula_candidates_path: str
    formula_schema_relation_path: str
    substitution_representability_targets_path: str
    diagonal_construction_targets_path: str
    fixed_point_targets_path: str
    expected_composition_count: int
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphDiagonalWitnessCompositionValidation:
    """One validation result for diagonal-witness composition evidence."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphDiagonalWitnessComposition:
    """One finite diagonal-witness composition check."""

    composition_id: str
    source_kind: str
    correctness_target_id: str
    formula_candidate_id: str
    witness_id: str
    construction_id: str
    fixed_point_target_id: str
    variable: str
    seed_code_length: int
    witness_formula_code_length: int
    witness_argument_code_length: int
    diagonal_instance_code_length: int
    witness_output_code_length: int
    target_chain_aligned: bool
    self_application_inputs_match: bool
    output_codes_match: bool
    output_surface_matches: bool
    schema_relation_witness_present: bool
    schema_relation_witness_accepted: bool


@dataclass(frozen=True)
class SubstitutionGraphDiagonalWitnessCompositionReport:
    """Validation report over finite diagonal-witness composition checks."""

    manifest: SubstitutionGraphDiagonalWitnessCompositionManifest
    formal_language_path: Path
    codebook_path: Path
    correctness_targets_path: Path
    formula_candidates_path: Path
    formula_schema_relation_path: Path
    substitution_representability_targets_path: Path
    diagonal_construction_targets_path: Path
    fixed_point_targets_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionGraphDiagonalWitnessCompositionValidation, ...]
    compositions: tuple[SubstitutionGraphDiagonalWitnessComposition, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every composition validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def composition_count(self) -> int:
        """Return the number of checked diagonal-witness compositions."""

        return len(self.compositions)

    @property
    def source_kind_counts(self) -> dict[str, int]:
        """Return observed composition counts grouped by source kind."""

        counts = {source_kind: 0 for source_kind in REQUIRED_SOURCE_KINDS}
        for composition in self.compositions:
            counts[composition.source_kind] = (
                counts.get(composition.source_kind, 0) + 1
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


def load_substitution_graph_diagonal_witness_composition(
    path: Path | str = DEFAULT_COMPOSITION,
) -> SubstitutionGraphDiagonalWitnessCompositionManifest:
    """Load the graph diagonal-witness composition manifest from JSON."""

    composition_path = Path(path)
    data = json.loads(composition_path.read_text(encoding="utf-8"))
    return SubstitutionGraphDiagonalWitnessCompositionManifest(
        path=composition_path,
        schema_version=_required_int(data, "schema_version"),
        composition_set_id=_required_text(data, "composition_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        correctness_targets_path=_required_text(data, "correctness_targets_path"),
        formula_candidates_path=_required_text(data, "formula_candidates_path"),
        formula_schema_relation_path=_required_text(
            data,
            "formula_schema_relation_path",
        ),
        substitution_representability_targets_path=_required_text(
            data,
            "substitution_representability_targets_path",
        ),
        diagonal_construction_targets_path=_required_text(
            data,
            "diagonal_construction_targets_path",
        ),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        expected_composition_count=_required_int(
            data,
            "expected_composition_count",
        ),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_diagonal_witness_composition(
    manifest: SubstitutionGraphDiagonalWitnessCompositionManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphDiagonalWitnessCompositionReport:
    """Validate finite graph diagonal-witness composition checks."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_correctness_path = Path(manifest.correctness_targets_path)
    checked_formula_path = Path(manifest.formula_candidates_path)
    checked_schema_relation_path = Path(manifest.formula_schema_relation_path)
    checked_witness_path = Path(manifest.substitution_representability_targets_path)
    checked_diagonal_path = Path(manifest.diagonal_construction_targets_path)
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)

    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    correctness_manifest = load_substitution_graph_correctness_targets(
        checked_correctness_path,
    )
    correctness_report = validate_substitution_graph_correctness_targets(
        correctness_manifest,
        checked_willard_map_path,
    )
    formula_manifest = load_substitution_graph_formula_candidates(
        checked_formula_path,
    )
    formula_report = validate_substitution_graph_formula_candidates(
        formula_manifest,
        checked_willard_map_path,
    )
    schema_relation_manifest = load_substitution_graph_formula_schema_relation(
        checked_schema_relation_path,
    )
    schema_relation_report = validate_substitution_graph_formula_schema_relation(
        schema_relation_manifest,
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
    diagonal_manifest = load_diagonal_construction_targets(checked_diagonal_path)
    diagonal_report = validate_diagonal_construction_targets(
        diagonal_manifest,
        checked_language_path,
        checked_willard_map_path,
    )
    fixed_point_manifest = load_fixed_point_targets(checked_fixed_point_path)
    fixed_point_report = validate_fixed_point_targets(
        fixed_point_manifest,
        checked_willard_map_path,
        checked_language_path,
    )

    results: list[SubstitutionGraphDiagonalWitnessCompositionValidation] = [
        _accepted("manifest", f"loaded {manifest.composition_set_id}")
    ]
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            codebook_report,
            correctness_report,
            formula_report,
            schema_relation_report,
            witness_report,
            diagonal_report,
            fixed_point_report,
        )
    )

    compositions: list[SubstitutionGraphDiagonalWitnessComposition] = []
    try:
        compositions = _derive_compositions(
            correctness_manifest.targets,
            formula_manifest.candidates,
            schema_relation_report.relation_points,
            witness_manifest.witnesses,
            witness_report.observations,
            diagonal_manifest.constructions,
            diagonal_report.observations,
            fixed_point_manifest.targets,
            checked_witness_path,
            checked_diagonal_path,
            checked_fixed_point_path,
            checked_codebook_path,
        )
    except ValueError as exc:
        results.append(_rejected("compositions", str(exc)))

    results.extend(_validate_composition_set(manifest, tuple(compositions)))

    return SubstitutionGraphDiagonalWitnessCompositionReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        correctness_targets_path=checked_correctness_path,
        formula_candidates_path=checked_formula_path,
        formula_schema_relation_path=checked_schema_relation_path,
        substitution_representability_targets_path=checked_witness_path,
        diagonal_construction_targets_path=checked_diagonal_path,
        fixed_point_targets_path=checked_fixed_point_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        compositions=tuple(compositions),
    )


def substitution_graph_diagonal_witness_composition_report_payload(
    report: SubstitutionGraphDiagonalWitnessCompositionReport,
) -> dict[str, Any]:
    """Return a JSON-ready graph diagonal-witness composition payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "composition_manifest": str(report.manifest.path),
        "composition_set_id": report.manifest.composition_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "correctness_targets_path": str(report.correctness_targets_path),
        "formula_candidates_path": str(report.formula_candidates_path),
        "formula_schema_relation_path": str(report.formula_schema_relation_path),
        "substitution_representability_targets_path": str(
            report.substitution_representability_targets_path
        ),
        "diagonal_construction_targets_path": str(
            report.diagonal_construction_targets_path
        ),
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "willard_map": str(report.willard_map_path),
        "expected_composition_count": report.manifest.expected_composition_count,
        "composition_count": report.composition_count,
        "source_kind_counts": report.source_kind_counts,
        "required_source_kinds": list(report.manifest.required_source_kinds),
        "required_future_work": list(report.manifest.required_future_work),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "compositions": [
            {
                "composition_id": composition.composition_id,
                "source_kind": composition.source_kind,
                "correctness_target_id": composition.correctness_target_id,
                "formula_candidate_id": composition.formula_candidate_id,
                "witness_id": composition.witness_id,
                "construction_id": composition.construction_id,
                "fixed_point_target_id": composition.fixed_point_target_id,
                "variable": composition.variable,
                "observed_seed_code_length": composition.seed_code_length,
                "observed_witness_formula_code_length": (
                    composition.witness_formula_code_length
                ),
                "observed_witness_argument_code_length": (
                    composition.witness_argument_code_length
                ),
                "observed_diagonal_instance_code_length": (
                    composition.diagonal_instance_code_length
                ),
                "observed_witness_output_code_length": (
                    composition.witness_output_code_length
                ),
                "observed_target_chain_aligned": (
                    composition.target_chain_aligned
                ),
                "observed_self_application_inputs_match": (
                    composition.self_application_inputs_match
                ),
                "observed_output_codes_match": composition.output_codes_match,
                "observed_output_surface_matches": (
                    composition.output_surface_matches
                ),
                "observed_schema_relation_witness_present": (
                    composition.schema_relation_witness_present
                ),
                "observed_schema_relation_witness_accepted": (
                    composition.schema_relation_witness_accepted
                ),
            }
            for composition in report.compositions
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


def format_substitution_graph_diagonal_witness_composition_report(
    report: SubstitutionGraphDiagonalWitnessCompositionReport,
) -> str:
    """Format a concise human-readable diagonal-witness composition report."""

    status = "accepted" if report.accepted else "rejected"
    failures = [
        composition.composition_id
        for composition in report.compositions
        if not _composition_accepted(composition)
    ]
    source_counts = ", ".join(
        f"{source_kind}={count}"
        for source_kind, count in report.source_kind_counts.items()
    )
    lines = [
        f"Substitution graph diagonal witness composition: {status}",
        f"Composition set: {report.manifest.composition_set_id}",
        f"Compositions: {report.composition_count}",
        f"Source kinds: {source_counts}",
        f"Composition failures: {_joined_or_none(tuple(failures))}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_diagonal_witness_composition_cli(
    argv: list[str] | None = None,
) -> int:
    """Run finite graph diagonal-witness composition validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.substitution_graph_diagonal_witness_composition"
        ),
        description="Validate substitution graph diagonal-witness composition.",
    )
    parser.add_argument(
        "--composition",
        default=str(DEFAULT_COMPOSITION),
        help="Path to the graph diagonal-witness composition manifest.",
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

    manifest = load_substitution_graph_diagonal_witness_composition(
        args.composition
    )
    report = validate_substitution_graph_diagonal_witness_composition(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(
            substitution_graph_diagonal_witness_composition_report_payload(report),
            sort_keys=True,
        ))
    else:
        print(format_substitution_graph_diagonal_witness_composition_report(report))
    return 0 if report.accepted else 1


def _derive_compositions(
    correctness_targets: tuple[SubstitutionGraphCorrectnessTarget, ...],
    candidates: tuple[SubstitutionGraphFormulaCandidate, ...],
    schema_relation_points: tuple[SubstitutionGraphFormulaSchemaRelationPoint, ...],
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    witness_observations: tuple[SubstitutionRepresentabilityObservation, ...],
    constructions: tuple[DiagonalConstructionTarget, ...],
    construction_observations: tuple[DiagonalConstructionObservation, ...],
    fixed_point_targets: tuple[FixedPointTarget, ...],
    witness_targets_path: Path,
    diagonal_targets_path: Path,
    fixed_point_targets_path: Path,
    codebook_path: Path,
) -> list[SubstitutionGraphDiagonalWitnessComposition]:
    compositions: list[SubstitutionGraphDiagonalWitnessComposition] = []
    for correctness_target in correctness_targets:
        candidate = _find_candidate(candidates, correctness_target.formula_candidate_id)
        witness = _find_witness(witnesses, candidate.witness_id)
        witness_observation = _find_witness_observation(
            witness_observations,
            witness.witness_id,
        )
        construction = _find_construction(constructions, witness.construction_id)
        construction_observation = _find_construction_observation(
            construction_observations,
            construction.construction_id,
        )
        fixed_point_target = _find_fixed_point_target(
            fixed_point_targets,
            witness.target_id,
        )
        schema_relation_point = _find_schema_relation_witness_point(
            schema_relation_points,
            witness.witness_id,
        )
        compositions.append(
            _composition(
                correctness_target,
                candidate,
                schema_relation_point,
                witness,
                witness_observation,
                construction,
                construction_observation,
                fixed_point_target,
                witness_targets_path,
                diagonal_targets_path,
                fixed_point_targets_path,
                codebook_path,
            )
        )
    return compositions


def _composition(
    correctness_target: SubstitutionGraphCorrectnessTarget,
    candidate: SubstitutionGraphFormulaCandidate,
    schema_relation_point: SubstitutionGraphFormulaSchemaRelationPoint | None,
    witness: SubstitutionRepresentabilityWitness,
    witness_observation: SubstitutionRepresentabilityObservation,
    construction: DiagonalConstructionTarget,
    construction_observation: DiagonalConstructionObservation,
    fixed_point_target: FixedPointTarget,
    witness_targets_path: Path,
    diagonal_targets_path: Path,
    fixed_point_targets_path: Path,
    codebook_path: Path,
) -> SubstitutionGraphDiagonalWitnessComposition:
    witness_output_code = build_substitution_witness_output_code(
        witness_id=witness.witness_id,
        targets_path=witness_targets_path,
        diagonal_targets_path=diagonal_targets_path,
        fixed_point_targets_path=fixed_point_targets_path,
        codebook_path=codebook_path,
    )
    diagonal_instance_code = build_diagonal_instance_code(
        construction_id=construction.construction_id,
        targets_path=diagonal_targets_path,
        fixed_point_targets_path=fixed_point_targets_path,
        codebook_path=codebook_path,
    )
    target_chain_aligned = (
        correctness_target.formula_candidate_id == candidate.candidate_id
        and correctness_target.graph_target_id == candidate.target_id
        and correctness_target.relation_name == candidate.relation_name
        and correctness_target.formula_class == candidate.formula_class
        and candidate.witness_id == witness.witness_id
        and witness.construction_id == construction.construction_id
        and witness.target_id == construction.target_id
        and witness.target_id == fixed_point_target.target_id
        and witness.variable == fixed_point_target.template_variable
    )
    self_application_inputs_match = (
        construction_observation.seed_code == witness_observation.formula_code
        and witness_observation.formula_code == witness_observation.argument_code
    )
    output_codes_match = witness_output_code == diagonal_instance_code
    output_surface_matches = (
        len(diagonal_instance_code) == construction.expected_instance_code_length
        and len(witness_output_code) == witness.expected_output_code_length
        and diagonal_instance_code[: len(construction.expected_instance_code_prefix)]
        == construction.expected_instance_code_prefix
        and witness_output_code[: len(witness.expected_output_code_prefix)]
        == witness.expected_output_code_prefix
        and construction_observation.instance_free_variables
        == construction.expected_instance_free_variables
        and witness_observation.output_free_variables
        == witness.expected_output_free_variables
    )
    schema_relation_witness_present = schema_relation_point is not None
    schema_relation_witness_accepted = False
    if schema_relation_point is not None:
        schema_relation_witness_accepted = (
            schema_relation_point.source_kind == "witness-instance"
            and schema_relation_point.source_id == witness.witness_id
            and schema_relation_point.formula_code_length
            == len(witness_observation.formula_code)
            and schema_relation_point.argument_code_length
            == len(witness_observation.argument_code)
            and schema_relation_point.output_code_length == len(witness_output_code)
            and schema_relation_point.schema_instance_closed
            and schema_relation_point.formula_code_roundtrips
            and schema_relation_point.input_matches_expected_surface
            and schema_relation_point.relation_holds
            and schema_relation_point.output_matches_expected_surface
        )
    return SubstitutionGraphDiagonalWitnessComposition(
        composition_id="AS-SUBST-GRAPH-DIAGONAL-WITNESS-COMPOSITION",
        source_kind="diagonal-witness",
        correctness_target_id=correctness_target.target_id,
        formula_candidate_id=candidate.candidate_id,
        witness_id=witness.witness_id,
        construction_id=construction.construction_id,
        fixed_point_target_id=fixed_point_target.target_id,
        variable=witness.variable,
        seed_code_length=len(construction_observation.seed_code),
        witness_formula_code_length=len(witness_observation.formula_code),
        witness_argument_code_length=len(witness_observation.argument_code),
        diagonal_instance_code_length=len(diagonal_instance_code),
        witness_output_code_length=len(witness_output_code),
        target_chain_aligned=target_chain_aligned,
        self_application_inputs_match=self_application_inputs_match,
        output_codes_match=output_codes_match,
        output_surface_matches=output_surface_matches,
        schema_relation_witness_present=schema_relation_witness_present,
        schema_relation_witness_accepted=schema_relation_witness_accepted,
    )


def _validate_references(
    manifest: SubstitutionGraphDiagonalWitnessCompositionManifest,
) -> list[SubstitutionGraphDiagonalWitnessCompositionValidation]:
    expected = (
        (
            "formal_language_path",
            manifest.formal_language_path,
            "language/formal_arithmetic_language.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "correctness_targets_path",
            manifest.correctness_targets_path,
            "claims/substitution_graph_correctness_targets.json",
        ),
        (
            "formula_candidates_path",
            manifest.formula_candidates_path,
            "claims/substitution_graph_formula_candidates.json",
        ),
        (
            "formula_schema_relation_path",
            manifest.formula_schema_relation_path,
            "claims/substitution_graph_formula_schema_relation.json",
        ),
        (
            "substitution_representability_targets_path",
            manifest.substitution_representability_targets_path,
            "claims/substitution_representability_targets.json",
        ),
        (
            "diagonal_construction_targets_path",
            manifest.diagonal_construction_targets_path,
            "claims/diagonal_construction_targets.json",
        ),
        (
            "fixed_point_targets_path",
            manifest.fixed_point_targets_path,
            "claims/fixed_point_targets.json",
        ),
    )
    results: list[SubstitutionGraphDiagonalWitnessCompositionValidation] = []
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
    correctness_report: Any,
    formula_report: Any,
    schema_relation_report: Any,
    witness_report: Any,
    diagonal_report: Any,
    fixed_point_report: Any,
) -> list[SubstitutionGraphDiagonalWitnessCompositionValidation]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        ("correctness_target", correctness_report, "correctness target"),
        ("formula_candidate", formula_report, "substitution graph formula"),
        (
            "formula_schema_relation",
            schema_relation_report,
            "formula-schema relation",
        ),
        (
            "substitution_representability",
            witness_report,
            "substitution representability witness",
        ),
        ("diagonal_construction", diagonal_report, "diagonal construction"),
        ("fixed_point", fixed_point_report, "fixed-point target"),
    )
    results: list[SubstitutionGraphDiagonalWitnessCompositionValidation] = []
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


def _validate_composition_set(
    manifest: SubstitutionGraphDiagonalWitnessCompositionManifest,
    compositions: tuple[SubstitutionGraphDiagonalWitnessComposition, ...],
) -> list[SubstitutionGraphDiagonalWitnessCompositionValidation]:
    results: list[SubstitutionGraphDiagonalWitnessCompositionValidation] = []
    composition_ids = [composition.composition_id for composition in compositions]
    duplicate_ids = _duplicates(composition_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "composition_ids",
                "duplicate composition ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("composition_ids", "composition ids are unique"))

    if len(compositions) != manifest.expected_composition_count:
        results.append(
            _rejected(
                "expected_composition_count",
                "composition count mismatch: expected "
                + str(manifest.expected_composition_count)
                + " got "
                + str(len(compositions)),
            )
        )
    else:
        results.append(
            _accepted(
                "expected_composition_count",
                f"checked {len(compositions)} composition(s)",
            )
        )

    source_kinds = {composition.source_kind for composition in compositions}
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
        composition.composition_id
        for composition in compositions
        if not _composition_accepted(composition)
    ]
    if failures:
        results.append(
            _rejected(
                "compositions",
                "composition failures: " + ", ".join(failures),
            )
        )
    else:
        results.append(
            _accepted(
                "compositions",
                f"checked {len(compositions)} diagonal witness composition(s)",
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


def _composition_accepted(
    composition: SubstitutionGraphDiagonalWitnessComposition,
) -> bool:
    return (
        composition.target_chain_aligned
        and composition.self_application_inputs_match
        and composition.output_codes_match
        and composition.output_surface_matches
        and composition.schema_relation_witness_present
        and composition.schema_relation_witness_accepted
    )


def _find_candidate(
    candidates: tuple[SubstitutionGraphFormulaCandidate, ...],
    candidate_id: str,
) -> SubstitutionGraphFormulaCandidate:
    for candidate in candidates:
        if candidate.candidate_id == candidate_id:
            return candidate
    raise ValueError(f"unknown formula candidate: {candidate_id}")


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


def _find_construction(
    constructions: tuple[DiagonalConstructionTarget, ...],
    construction_id: str,
) -> DiagonalConstructionTarget:
    for construction in constructions:
        if construction.construction_id == construction_id:
            return construction
    raise ValueError(f"unknown diagonal construction: {construction_id}")


def _find_construction_observation(
    observations: tuple[DiagonalConstructionObservation, ...],
    construction_id: str,
) -> DiagonalConstructionObservation:
    for observation in observations:
        if observation.construction_id == construction_id:
            return observation
    raise ValueError(f"missing diagonal construction observation: {construction_id}")


def _find_fixed_point_target(
    targets: tuple[FixedPointTarget, ...],
    target_id: str,
) -> FixedPointTarget:
    for target in targets:
        if target.target_id == target_id:
            return target
    raise ValueError(f"unknown fixed-point target: {target_id}")


def _find_schema_relation_witness_point(
    relation_points: tuple[SubstitutionGraphFormulaSchemaRelationPoint, ...],
    witness_id: str,
) -> SubstitutionGraphFormulaSchemaRelationPoint | None:
    for point in relation_points:
        if point.source_kind == "witness-instance" and point.source_id == witness_id:
            return point
    return None


def _failed_subject_for_result(subject: str) -> str:
    if subject == "expected_composition_count":
        return "substitution-graph-diagonal-witness-composition-count"
    if subject in {"composition_ids", "compositions"}:
        return "substitution-graph-diagonal-witness-composition"
    if subject == "required_source_kinds":
        return "substitution-graph-diagonal-witness-composition-source-kind"
    if subject == "required_future_work":
        return "substitution-graph-diagonal-witness-composition-future-work"
    if subject == "non_claims":
        return "substitution-graph-diagonal-witness-composition-non-claim"
    if subject in {
        "codebook",
        "correctness_target",
        "formula_candidate",
        "formula_schema_relation",
        "substitution_representability",
        "diagonal_construction",
        "fixed_point",
    }:
        return "substitution-graph-diagonal-witness-composition-dependency"
    if subject.endswith("_path"):
        return "substitution-graph-diagonal-witness-composition-reference"
    return "substitution-graph-diagonal-witness-composition"


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
) -> SubstitutionGraphDiagonalWitnessCompositionValidation:
    return SubstitutionGraphDiagonalWitnessCompositionValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphDiagonalWitnessCompositionValidation:
    return SubstitutionGraphDiagonalWitnessCompositionValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_diagonal_witness_composition_cli())
