"""Checked substitution graph formula schema surface for AS.

This module validates the first syntactic formula schema for the
``substitution_code`` graph target: ``substitution_code(x,y) = z``. It checks
that the formula is well-formed in the current codebook and that plugging in
the checked witness codes yields a closed encoded instance. It does not prove
that the formula correctly represents meta-level substitution.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.formal_arithmetic import (
    load_formal_arithmetic_language,
    validate_formal_arithmetic_language,
)
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
from autarkic_systems.substitution_graph_target import (
    SubstitutionGraphObservation,
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


DEFAULT_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

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
VALID_CANDIDATE_STATUSES = {
    "formula-schema-not-proved",
}


@dataclass(frozen=True)
class SubstitutionGraphFormulaCandidate:
    """One syntactic substitution graph formula candidate."""

    candidate_id: str
    target_id: str
    witness_id: str
    relation_name: str
    formula_class: str
    status: str
    formula_node: dict[str, Any]
    graph_variables: dict[str, str]
    expected_formula_code: tuple[int, ...]
    expected_formula_free_variables: tuple[str, ...]
    expected_witness_instance_code_length: int
    expected_witness_instance_code_prefix: tuple[int, ...]
    expected_witness_instance_free_variables: tuple[str, ...]
    expected_witness_relation_holds: bool
    expected_evaluated_output_code_length: int
    expected_evaluated_output_code_prefix: tuple[int, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphFormulaManifest:
    """Loaded manifest for substitution graph formula candidates."""

    path: Path
    schema_version: int
    candidate_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    substitution_graph_targets_path: str
    substitution_representability_targets_path: str
    candidates: tuple[SubstitutionGraphFormulaCandidate, ...]


@dataclass(frozen=True)
class SubstitutionGraphFormulaValidation:
    """One validation result for substitution graph formula candidates."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphFormulaObservation:
    """Observed formula and witness-instance facts for one candidate."""

    candidate_id: str
    target_id: str
    witness_id: str
    status: str
    formula_code: tuple[int, ...]
    formula_free_variables: tuple[str, ...]
    witness_instance_code_length: int
    witness_instance_code_prefix: tuple[int, ...]
    witness_instance_free_variables: tuple[str, ...]
    witness_relation_holds: bool
    evaluated_output_code_length: int
    evaluated_output_code_prefix: tuple[int, ...]


@dataclass(frozen=True)
class SubstitutionGraphFormulaReport:
    """Validation report over substitution graph formula candidates."""

    manifest: SubstitutionGraphFormulaManifest
    formal_language_path: Path
    codebook_path: Path
    substitution_graph_targets_path: Path
    substitution_representability_targets_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionGraphFormulaValidation, ...]
    observations: tuple[SubstitutionGraphFormulaObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every formula-candidate validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def candidate_count(self) -> int:
        """Return the number of checked formula candidates."""

        return len(self.manifest.candidates)

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


def load_substitution_graph_formula_candidates(
    path: Path | str = DEFAULT_CANDIDATES,
) -> SubstitutionGraphFormulaManifest:
    """Load substitution graph formula candidates from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return SubstitutionGraphFormulaManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        candidate_set_id=_required_text(data, "candidate_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        substitution_graph_targets_path=_required_text(
            data,
            "substitution_graph_targets_path",
        ),
        substitution_representability_targets_path=_required_text(
            data,
            "substitution_representability_targets_path",
        ),
        candidates=tuple(
            _parse_candidate(item) for item in _required_list(data, "candidates")
        ),
    )


def validate_substitution_graph_formula_candidates(
    manifest: SubstitutionGraphFormulaManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphFormulaReport:
    """Validate substitution graph formula candidates and dependencies."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_graph_target_path = Path(manifest.substitution_graph_targets_path)
    checked_witness_path = Path(manifest.substitution_representability_targets_path)

    language = load_formal_arithmetic_language(checked_language_path)
    language_report = validate_formal_arithmetic_language(
        language,
        checked_willard_map_path,
    )
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    graph_targets = load_substitution_graph_targets(checked_graph_target_path)
    graph_report = validate_substitution_graph_targets(
        graph_targets,
        checked_willard_map_path,
    )
    witness_manifest = load_substitution_representability_targets(checked_witness_path)
    witness_report = validate_substitution_representability_targets(
        witness_manifest,
        checked_language_path,
        checked_willard_map_path,
    )

    results: list[SubstitutionGraphFormulaValidation] = [
        _accepted("manifest", f"loaded {len(manifest.candidates)} candidate(s)")
    ]
    observations: list[SubstitutionGraphFormulaObservation] = []
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            language_report,
            codebook_report,
            graph_report,
            witness_report,
        )
    )
    candidate_results, observations = _validate_candidates(
        manifest.candidates,
        codebook,
        graph_report.observations,
        witness_manifest.witnesses,
        witness_report.observations,
        checked_witness_path,
    )
    results.extend(candidate_results)

    return SubstitutionGraphFormulaReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        substitution_graph_targets_path=checked_graph_target_path,
        substitution_representability_targets_path=checked_witness_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def substitution_graph_formula_report_payload(
    report: SubstitutionGraphFormulaReport,
) -> dict[str, Any]:
    """Return a JSON-ready substitution graph formula payload."""

    observations = {
        observation.candidate_id: observation
        for observation in report.observations
    }
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "candidate_manifest": str(report.manifest.path),
        "candidate_set_id": report.manifest.candidate_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "substitution_graph_targets_path": str(report.substitution_graph_targets_path),
        "substitution_representability_targets_path": str(
            report.substitution_representability_targets_path
        ),
        "willard_map": str(report.willard_map_path),
        "candidate_count": report.candidate_count,
        "failed_subjects": list(report.failed_subjects),
        "candidates": [
            _candidate_payload(candidate, observations.get(candidate.candidate_id))
            for candidate in report.manifest.candidates
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


def format_substitution_graph_formula_report(
    report: SubstitutionGraphFormulaReport,
) -> str:
    """Format a concise human-readable formula candidate report."""

    observations = {
        observation.candidate_id: observation
        for observation in report.observations
    }
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Substitution graph formula candidates: {status}",
        f"Candidate set: {report.manifest.candidate_set_id}",
        f"Candidates: {report.candidate_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for candidate in report.manifest.candidates:
        observation = observations.get(candidate.candidate_id)
        formula_length = "unknown"
        instance_length = "unknown"
        if observation is not None:
            formula_length = str(len(observation.formula_code))
            instance_length = str(observation.witness_instance_code_length)
            relation_holds = str(observation.witness_relation_holds).lower()
            evaluated_length = str(observation.evaluated_output_code_length)
        else:
            relation_holds = "unknown"
            evaluated_length = "unknown"
        lines.extend([
            f"- {candidate.candidate_id}",
            f"  Target: {candidate.target_id}",
            f"  Relation: {candidate.relation_name}",
            f"  Formula class: {candidate.formula_class}",
            f"  Status: {candidate.status}",
            f"  Formula code length: {formula_length}",
            f"  Witness instance code length: {instance_length}",
            f"  Witness relation holds: {relation_holds}",
            f"  Evaluated output code length: {evaluated_length}",
            "  Future work: " + _joined_or_none(candidate.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_formula_cli(argv: list[str] | None = None) -> int:
    """Run substitution graph formula candidate validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.substitution_graph_formula",
        description="Validate AS substitution graph formula candidates.",
    )
    parser.add_argument(
        "--candidates",
        default=str(DEFAULT_CANDIDATES),
        help="Path to the substitution graph formula candidate manifest.",
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

    manifest = load_substitution_graph_formula_candidates(args.candidates)
    report = validate_substitution_graph_formula_candidates(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(substitution_graph_formula_report_payload(report), sort_keys=True))
    else:
        print(format_substitution_graph_formula_report(report))
    return 0 if report.accepted else 1


def _candidate_payload(
    candidate: SubstitutionGraphFormulaCandidate,
    observation: SubstitutionGraphFormulaObservation | None,
) -> dict[str, Any]:
    payload = {
        "candidate_id": candidate.candidate_id,
        "target_id": candidate.target_id,
        "witness_id": candidate.witness_id,
        "relation_name": candidate.relation_name,
        "formula_class": candidate.formula_class,
        "status": candidate.status,
        "formula_node": candidate.formula_node,
        "graph_variables": dict(candidate.graph_variables),
        "expected_formula_code": list(candidate.expected_formula_code),
        "expected_formula_free_variables": list(
            candidate.expected_formula_free_variables
        ),
        "expected_witness_instance_code_length": (
            candidate.expected_witness_instance_code_length
        ),
        "expected_witness_instance_code_prefix": list(
            candidate.expected_witness_instance_code_prefix
        ),
        "expected_witness_instance_free_variables": list(
            candidate.expected_witness_instance_free_variables
        ),
        "expected_witness_relation_holds": candidate.expected_witness_relation_holds,
        "expected_evaluated_output_code_length": (
            candidate.expected_evaluated_output_code_length
        ),
        "expected_evaluated_output_code_prefix": list(
            candidate.expected_evaluated_output_code_prefix
        ),
        "required_future_work": list(candidate.required_future_work),
        "non_claims": list(candidate.non_claims),
        "next_as_action": candidate.next_as_action,
    }
    if observation is None:
        payload.update({
            "observed_formula_code": None,
            "observed_formula_free_variables": None,
            "observed_witness_instance_code_length": None,
            "observed_witness_instance_code_prefix": None,
            "observed_witness_instance_free_variables": None,
            "observed_witness_relation_holds": None,
            "observed_evaluated_output_code_length": None,
            "observed_evaluated_output_code_prefix": None,
        })
    else:
        payload.update({
            "observed_formula_code": list(observation.formula_code),
            "observed_formula_free_variables": list(
                observation.formula_free_variables
            ),
            "observed_witness_instance_code_length": (
                observation.witness_instance_code_length
            ),
            "observed_witness_instance_code_prefix": list(
                observation.witness_instance_code_prefix
            ),
            "observed_witness_instance_free_variables": list(
                observation.witness_instance_free_variables
            ),
            "observed_witness_relation_holds": observation.witness_relation_holds,
            "observed_evaluated_output_code_length": (
                observation.evaluated_output_code_length
            ),
            "observed_evaluated_output_code_prefix": list(
                observation.evaluated_output_code_prefix
            ),
        })
    return payload


def _validate_references(
    manifest: SubstitutionGraphFormulaManifest,
) -> list[SubstitutionGraphFormulaValidation]:
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
            "substitution_representability_targets_path",
            manifest.substitution_representability_targets_path,
            "claims/substitution_representability_targets.json",
        ),
    )
    results: list[SubstitutionGraphFormulaValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_dependency_reports(
    language_report: Any,
    codebook_report: Any,
    graph_report: Any,
    witness_report: Any,
) -> list[SubstitutionGraphFormulaValidation]:
    checks = (
        ("formal_language", language_report, "formal arithmetic language"),
        ("codebook", codebook_report, "formal codebook"),
        ("substitution_graph", graph_report, "substitution graph target"),
        (
            "substitution_representability",
            witness_report,
            "substitution representability witness",
        ),
    )
    results: list[SubstitutionGraphFormulaValidation] = []
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


def _validate_candidates(
    candidates: tuple[SubstitutionGraphFormulaCandidate, ...],
    codebook: FormalCodebook,
    graph_observations: tuple[SubstitutionGraphObservation, ...],
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    witness_observations: tuple[SubstitutionRepresentabilityObservation, ...],
    witness_targets_path: Path,
) -> tuple[
    list[SubstitutionGraphFormulaValidation],
    list[SubstitutionGraphFormulaObservation],
]:
    if not candidates:
        return [_rejected("candidates", "no substitution graph formula candidates")], []

    results: list[SubstitutionGraphFormulaValidation] = []
    observations: list[SubstitutionGraphFormulaObservation] = []
    candidate_ids = [candidate.candidate_id for candidate in candidates]
    duplicate_ids = _duplicates(candidate_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "candidates.candidate_id",
                "duplicate candidate ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("candidates.candidate_id", "candidate ids are unique"))

    for candidate in candidates:
        candidate_results, observation = _validate_candidate(
            candidate,
            codebook,
            graph_observations,
            witnesses,
            witness_observations,
            witness_targets_path,
        )
        results.extend(candidate_results)
        if observation is not None:
            observations.append(observation)
    results.append(_accepted("candidates", f"checked {len(candidates)} candidate(s)"))
    return results, observations


def _validate_candidate(
    candidate: SubstitutionGraphFormulaCandidate,
    codebook: FormalCodebook,
    graph_observations: tuple[SubstitutionGraphObservation, ...],
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    witness_observations: tuple[SubstitutionRepresentabilityObservation, ...],
    witness_targets_path: Path,
) -> tuple[
    list[SubstitutionGraphFormulaValidation],
    SubstitutionGraphFormulaObservation | None,
]:
    subject = candidate.candidate_id
    results: list[SubstitutionGraphFormulaValidation] = []

    if candidate.status in {
        "formula-correctness-proved",
        "substitution-representability-proved",
    }:
        results.append(
            _rejected(
                f"{subject}.status",
                "proved formula correctness is not supported",
            )
        )
    elif candidate.status not in VALID_CANDIDATE_STATUSES:
        results.append(_rejected(f"{subject}.status", f"unknown status: {candidate.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "status preserves non-claim"))

    if candidate.relation_name != "subst_code_graph":
        results.append(
            _rejected(f"{subject}.relation_name", "expected subst_code_graph")
        )
    else:
        results.append(_accepted(f"{subject}.relation_name", "relation schema named"))

    if candidate.formula_class != "delta0":
        results.append(
            _rejected(f"{subject}.formula_class", "expected delta0 formula class")
        )
    else:
        results.append(_accepted(f"{subject}.formula_class", "delta0 schema selected"))

    try:
        graph_observation = _find_graph_observation(
            graph_observations,
            candidate.target_id,
        )
        witness_target = _find_witness(
            witnesses,
            candidate.witness_id,
        )
        witness_observation = _find_witness_observation(
            witness_observations,
            candidate.witness_id,
        )
    except ValueError as exc:
        results.append(_rejected(f"{subject}.target", str(exc)))
        return results, None

    if graph_observation.witness_id != candidate.witness_id:
        results.append(
            _rejected(
                f"{subject}.target",
                "target witness mismatch: expected "
                + graph_observation.witness_id
                + " but found "
                + candidate.witness_id,
            )
        )
    else:
        results.append(_accepted(f"{subject}.target", "graph target and witness agree"))

    formula_results = _validate_formula_schema(candidate, codebook)
    results.extend(formula_results)

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in candidate.required_future_work
    ]
    if missing_future_work:
        results.append(
            _rejected(
                f"{subject}.required_future_work",
                "missing future work: " + ", ".join(missing_future_work),
            )
        )
    else:
        results.append(_accepted(f"{subject}.required_future_work", "future work is explicit"))

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in candidate.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                f"{subject}.non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted(f"{subject}.non_claims", "non-claims are explicit"))

    try:
        observation = _observe_candidate_instance(
            candidate,
            codebook,
            witness_target,
            witness_observation,
            witness_targets_path,
        )
    except ValueError as exc:
        results.append(_rejected(f"{subject}.witness_instance", str(exc)))
        return results, None

    results.extend(_validate_witness_instance(candidate, observation))
    results.extend(_validate_witness_evaluation(candidate, observation))
    return results, observation


def _validate_formula_schema(
    candidate: SubstitutionGraphFormulaCandidate,
    codebook: FormalCodebook,
) -> list[SubstitutionGraphFormulaValidation]:
    subject = f"{candidate.candidate_id}.formula"
    expected_node = _schema_node(candidate.graph_variables)
    if candidate.formula_node != expected_node:
        return [_rejected(subject, "formula must be substitution_code(x,y) = z")]

    try:
        formula_code = encode_node(candidate.formula_node, codebook)
        formula_free_variables = tuple(sorted(free_variables(candidate.formula_node)))
    except ValueError as exc:
        return [_rejected(subject, str(exc))]

    if formula_code != candidate.expected_formula_code:
        return [
            _rejected(
                subject,
                "formula code mismatch: expected "
                + _format_code(candidate.expected_formula_code)
                + " got "
                + _format_code(formula_code),
            )
        ]
    if formula_free_variables != candidate.expected_formula_free_variables:
        return [
            _rejected(
                subject,
                "formula free variables mismatch: expected "
                + _joined_or_none(candidate.expected_formula_free_variables)
                + " got "
                + _joined_or_none(formula_free_variables),
            )
        ]
    return [_accepted(subject, "formula schema accepted")]


def _observe_candidate_instance(
    candidate: SubstitutionGraphFormulaCandidate,
    codebook: FormalCodebook,
    witness_target: SubstitutionRepresentabilityWitness,
    witness: SubstitutionRepresentabilityObservation,
    witness_targets_path: Path,
) -> SubstitutionGraphFormulaObservation:
    output_code = build_substitution_witness_output_code(
        witness_id=candidate.witness_id,
        targets_path=witness_targets_path,
    )
    instance = candidate.formula_node
    substitutions = (
        (candidate.graph_variables["formula_code"], witness.formula_code),
        (candidate.graph_variables["argument_code"], witness.argument_code),
        (candidate.graph_variables["output_code"], output_code),
    )
    for variable, code in substitutions:
        instance = substitute_node(instance, variable, quote_tokens_as_term(code))
    instance_code = encode_node(instance, codebook)
    relation_holds, evaluated_output_code = _evaluate_witness_relation(
        instance,
        witness_target.variable,
        codebook,
    )
    return SubstitutionGraphFormulaObservation(
        candidate_id=candidate.candidate_id,
        target_id=candidate.target_id,
        witness_id=candidate.witness_id,
        status=candidate.status,
        formula_code=encode_node(candidate.formula_node, codebook),
        formula_free_variables=tuple(sorted(free_variables(candidate.formula_node))),
        witness_instance_code_length=len(instance_code),
        witness_instance_code_prefix=instance_code[
            : len(candidate.expected_witness_instance_code_prefix)
        ],
        witness_instance_free_variables=tuple(sorted(free_variables(instance))),
        witness_relation_holds=relation_holds,
        evaluated_output_code_length=len(evaluated_output_code),
        evaluated_output_code_prefix=evaluated_output_code[
            : len(candidate.expected_evaluated_output_code_prefix)
        ],
    )


def _validate_witness_instance(
    candidate: SubstitutionGraphFormulaCandidate,
    observation: SubstitutionGraphFormulaObservation,
) -> list[SubstitutionGraphFormulaValidation]:
    subject = f"{candidate.candidate_id}.witness_instance"
    if observation.witness_instance_code_length != candidate.expected_witness_instance_code_length:
        return [
            _rejected(
                subject,
                "witness instance code length mismatch: expected "
                + str(candidate.expected_witness_instance_code_length)
                + " got "
                + str(observation.witness_instance_code_length),
            )
        ]
    if observation.witness_instance_code_prefix != candidate.expected_witness_instance_code_prefix:
        return [
            _rejected(
                subject,
                "witness instance code prefix mismatch: expected "
                + _format_code(candidate.expected_witness_instance_code_prefix)
                + " got "
                + _format_code(observation.witness_instance_code_prefix),
            )
        ]
    if observation.witness_instance_free_variables != candidate.expected_witness_instance_free_variables:
        return [
            _rejected(
                subject,
                "witness instance free variables mismatch: expected "
                + _joined_or_none(candidate.expected_witness_instance_free_variables)
                + " got "
                + _joined_or_none(observation.witness_instance_free_variables),
            )
        ]
    return [_accepted(subject, "closed witness instance accepted")]


def _validate_witness_evaluation(
    candidate: SubstitutionGraphFormulaCandidate,
    observation: SubstitutionGraphFormulaObservation,
) -> list[SubstitutionGraphFormulaValidation]:
    subject = f"{candidate.candidate_id}.witness_evaluation"
    if observation.witness_relation_holds != candidate.expected_witness_relation_holds:
        return [
            _rejected(
                subject,
                "witness relation truth mismatch: expected "
                + str(candidate.expected_witness_relation_holds).lower()
                + " got "
                + str(observation.witness_relation_holds).lower(),
            )
        ]
    if observation.evaluated_output_code_length != candidate.expected_evaluated_output_code_length:
        return [
            _rejected(
                subject,
                "evaluated output code length mismatch: expected "
                + str(candidate.expected_evaluated_output_code_length)
                + " got "
                + str(observation.evaluated_output_code_length),
            )
        ]
    if observation.evaluated_output_code_prefix != candidate.expected_evaluated_output_code_prefix:
        return [
            _rejected(
                subject,
                "evaluated output code prefix mismatch: expected "
                + _format_code(candidate.expected_evaluated_output_code_prefix)
                + " got "
                + _format_code(observation.evaluated_output_code_prefix),
            )
        ]
    return [_accepted(subject, "concrete witness relation evaluated true")]


def _evaluate_witness_relation(
    instance: dict[str, Any],
    variable: str,
    codebook: FormalCodebook,
) -> tuple[bool, tuple[int, ...]]:
    if _node_kind(instance) != "equals":
        raise ValueError("witness instance must be an equality formula")
    left = _required_node(instance, "left")
    right = _required_node(instance, "right")
    if _node_kind(left) != "substitution_code":
        raise ValueError("witness instance left side must be substitution_code")
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
    return evaluated_output_code == expected_output_code, evaluated_output_code


def _tokens_from_quotation_term(term: dict[str, Any]) -> tuple[int, ...]:
    kind = _node_kind(term)
    if kind == "sequence_nil":
        return ()
    if kind == "sequence_cons":
        head = numeral_to_natural(_required_node(term, "head"))
        return (head, *_tokens_from_quotation_term(_required_node(term, "tail")))
    raise ValueError(f"expected quotation sequence term, got {kind}")


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


def _find_graph_observation(
    observations: tuple[SubstitutionGraphObservation, ...],
    target_id: str,
) -> SubstitutionGraphObservation:
    for observation in observations:
        if observation.target_id == target_id:
            return observation
    raise ValueError(f"unknown substitution graph target: {target_id}")


def _find_witness_observation(
    observations: tuple[SubstitutionRepresentabilityObservation, ...],
    witness_id: str,
) -> SubstitutionRepresentabilityObservation:
    for observation in observations:
        if observation.witness_id == witness_id:
            return observation
    raise ValueError(f"unknown substitution witness: {witness_id}")


def _find_witness(
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    witness_id: str,
) -> SubstitutionRepresentabilityWitness:
    for witness in witnesses:
        if witness.witness_id == witness_id:
            return witness
    raise ValueError(f"unknown substitution witness: {witness_id}")


def _parse_candidate(item: dict[str, Any]) -> SubstitutionGraphFormulaCandidate:
    return SubstitutionGraphFormulaCandidate(
        candidate_id=_required_text(item, "candidate_id"),
        target_id=_required_text(item, "target_id"),
        witness_id=_required_text(item, "witness_id"),
        relation_name=_required_text(item, "relation_name"),
        formula_class=_required_text(item, "formula_class"),
        status=_required_text(item, "status"),
        formula_node=_required_mapping(item, "formula_node"),
        graph_variables=_required_text_mapping(item, "graph_variables"),
        expected_formula_code=tuple(_required_int_list(item, "expected_formula_code")),
        expected_formula_free_variables=tuple(
            _required_text_list(item, "expected_formula_free_variables", allow_empty=True)
        ),
        expected_witness_instance_code_length=_required_int(
            item,
            "expected_witness_instance_code_length",
        ),
        expected_witness_instance_code_prefix=tuple(
            _required_int_list(item, "expected_witness_instance_code_prefix")
        ),
        expected_witness_instance_free_variables=tuple(
            _required_text_list(
                item,
                "expected_witness_instance_free_variables",
                allow_empty=True,
            )
        ),
        expected_witness_relation_holds=_required_bool(
            item,
            "expected_witness_relation_holds",
        ),
        expected_evaluated_output_code_length=_required_int(
            item,
            "expected_evaluated_output_code_length",
        ),
        expected_evaluated_output_code_prefix=tuple(
            _required_int_list(item, "expected_evaluated_output_code_prefix")
        ),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject.endswith(".status"):
        return "substitution-graph-formula-status"
    if subject.endswith(".relation_name"):
        return "substitution-graph-formula-relation"
    if subject.endswith(".formula_class"):
        return "substitution-graph-formula-class"
    if subject.endswith(".target"):
        return "substitution-graph-formula-target"
    if subject.endswith(".formula"):
        return "substitution-graph-formula-schema"
    if subject.endswith(".witness_instance"):
        return "substitution-graph-formula-witness-instance"
    if subject.endswith(".witness_evaluation"):
        return "substitution-graph-formula-witness-evaluation"
    if subject.endswith(".required_future_work"):
        return "substitution-graph-formula-future-work"
    if subject.endswith(".non_claims"):
        return "substitution-graph-formula-non-claim"
    if subject in {
        "formal_language",
        "codebook",
        "substitution_graph",
        "substitution_representability",
    }:
        return "substitution-graph-formula-dependency"
    if subject.endswith("_path"):
        return "substitution-graph-formula-reference"
    if subject.startswith("candidates"):
        return "substitution-graph-formula-candidate"
    return "substitution-graph-formula"


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


def _required_bool(item: dict[str, Any], key: str) -> bool:
    value = item.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"required boolean field missing: {key}")
    return value


def _required_list(item: dict[str, Any], key: str) -> list[Any]:
    value = item.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"required list field missing: {key}")
    return value


def _required_mapping(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"required mapping field missing: {key}")
    return value


def _required_text_mapping(item: dict[str, Any], key: str) -> dict[str, str]:
    value = item.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"required mapping field missing: {key}")
    result: dict[str, str] = {}
    for item_key, item_value in value.items():
        if not isinstance(item_key, str) or not item_key.strip():
            raise ValueError(f"{key} contains non-text key")
        if not isinstance(item_value, str) or not item_value.strip():
            raise ValueError(f"{key} contains non-text value")
        result[item_key] = item_value
    return result


def _required_text_list(
    item: dict[str, Any],
    key: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    values = item.get(key)
    if not isinstance(values, list) or (not values and not allow_empty):
        raise ValueError(f"required list field missing: {key}")
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        result.append(value)
    return result


def _required_int_list(item: dict[str, Any], key: str) -> list[int]:
    values = item.get(key)
    if not isinstance(values, list) or not values:
        raise ValueError(f"required integer list missing: {key}")
    result: list[int] = []
    for value in values:
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{key} contains non-natural item")
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


def _accepted(subject: str, detail: str) -> SubstitutionGraphFormulaValidation:
    return SubstitutionGraphFormulaValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(subject: str, detail: str) -> SubstitutionGraphFormulaValidation:
    return SubstitutionGraphFormulaValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _format_code(values: tuple[int, ...]) -> str:
    return "[" + ", ".join(str(value) for value in values) + "]"


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _node_kind(node: dict[str, Any]) -> str:
    kind = node.get("kind")
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError("node is missing kind")
    return kind


def _required_node(node: dict[str, Any], key: str) -> dict[str, Any]:
    value = node.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"node is missing child: {key}")
    return value


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_formula_cli())
