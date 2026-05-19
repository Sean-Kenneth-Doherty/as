"""Open proof cases for substitution graph correctness.

The correctness target says that the checked ``substitution_code(x,y) = z``
schema still needs a proof. This module decomposes that missing proof into
auditable cases tied to existing checked surfaces. It validates the case
boundary and dependencies only; it does not prove the cases or promote the
substitution graph target to a representability theorem.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.formal_code import (
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation_term import (
    load_quotation_term_examples,
    validate_quotation_term_examples,
)
from autarkic_systems.formal_substitution import (
    load_substitution_examples,
    validate_substitution_examples,
)
from autarkic_systems.substitution_graph_codebook_roundtrip import (
    load_substitution_graph_codebook_roundtrip,
    validate_substitution_graph_codebook_roundtrip,
)
from autarkic_systems.substitution_graph_quotation_term_closure import (
    load_substitution_graph_quotation_term_closure,
    validate_substitution_graph_quotation_term_closure,
)
from autarkic_systems.substitution_graph_meta_substitution_semantics import (
    load_substitution_graph_meta_substitution_semantics,
    validate_substitution_graph_meta_substitution_semantics,
)
from autarkic_systems.substitution_graph_correctness import (
    SubstitutionGraphCorrectnessObservation,
    load_substitution_graph_correctness_targets,
    validate_substitution_graph_correctness_targets,
)
from autarkic_systems.substitution_graph_formula import (
    load_substitution_graph_formula_candidates,
    validate_substitution_graph_formula_candidates,
)
from autarkic_systems.substitution_representability import (
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)


DEFAULT_CASES = Path("claims/substitution_graph_correctness_cases.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_CASE_KINDS = (
    "codebook-roundtrip",
    "quotation-term-closure",
    "meta-substitution-semantics",
    "formula-schema-relation",
    "diagonal-witness-composition",
)
REQUIRED_DEPENDENCIES_BY_KIND = {
    "codebook-roundtrip": ("correctness_target", "codebook", "codebook_roundtrip"),
    "quotation-term-closure": (
        "correctness_target",
        "codebook",
        "quotation_term",
        "quotation_term_closure",
    ),
    "meta-substitution-semantics": (
        "correctness_target",
        "formal_substitution",
        "meta_substitution_semantics",
    ),
    "formula-schema-relation": ("correctness_target", "formula_candidate"),
    "diagonal-witness-composition": (
        "correctness_target",
        "substitution_representability",
    ),
}
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
VALID_CASE_STATUSES = {
    "proof-case-open",
}
PROVED_STATUS_REJECTIONS = {
    "formula-correctness-proved",
    "substitution-representability-proved",
    "diagonal-lemma-proved",
    "fixed-point-equation-proved",
    "self-consistency-proved",
}


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessCase:
    """One open proof case for substitution graph correctness."""

    case_id: str
    case_kind: str
    correctness_target_id: str
    status: str
    required_dependency_subjects: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessCaseManifest:
    """Loaded manifest for substitution graph correctness proof cases."""

    path: Path
    schema_version: int
    case_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    correctness_targets_path: str
    formal_substitution_examples_path: str
    quotation_term_examples_path: str
    formula_candidates_path: str
    substitution_representability_targets_path: str
    codebook_roundtrip_path: str
    quotation_term_closure_path: str
    meta_substitution_semantics_path: str
    cases: tuple[SubstitutionGraphCorrectnessCase, ...]


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessCaseValidation:
    """One validation result for correctness proof cases."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessCaseObservation:
    """Observed target and dependency facts for one proof case."""

    case_id: str
    case_kind: str
    correctness_target_id: str
    status: str
    dependency_count: int
    all_required_dependencies_present: bool


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessCaseReport:
    """Validation report over substitution graph correctness proof cases."""

    manifest: SubstitutionGraphCorrectnessCaseManifest
    formal_language_path: Path
    codebook_path: Path
    correctness_targets_path: Path
    formal_substitution_examples_path: Path
    quotation_term_examples_path: Path
    formula_candidates_path: Path
    substitution_representability_targets_path: Path
    codebook_roundtrip_path: Path
    quotation_term_closure_path: Path
    meta_substitution_semantics_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionGraphCorrectnessCaseValidation, ...]
    observations: tuple[SubstitutionGraphCorrectnessCaseObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every correctness-case validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def case_count(self) -> int:
        """Return the number of checked correctness proof cases."""

        return len(self.manifest.cases)

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


def load_substitution_graph_correctness_cases(
    path: Path | str = DEFAULT_CASES,
) -> SubstitutionGraphCorrectnessCaseManifest:
    """Load substitution graph correctness proof cases from JSON."""

    cases_path = Path(path)
    data = json.loads(cases_path.read_text(encoding="utf-8"))
    return SubstitutionGraphCorrectnessCaseManifest(
        path=cases_path,
        schema_version=_required_int(data, "schema_version"),
        case_set_id=_required_text(data, "case_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        correctness_targets_path=_required_text(data, "correctness_targets_path"),
        formal_substitution_examples_path=_required_text(
            data,
            "formal_substitution_examples_path",
        ),
        quotation_term_examples_path=_required_text(
            data,
            "quotation_term_examples_path",
        ),
        formula_candidates_path=_required_text(data, "formula_candidates_path"),
        substitution_representability_targets_path=_required_text(
            data,
            "substitution_representability_targets_path",
        ),
        codebook_roundtrip_path=_required_text(data, "codebook_roundtrip_path"),
        quotation_term_closure_path=_required_text(
            data,
            "quotation_term_closure_path",
        ),
        meta_substitution_semantics_path=_required_text(
            data,
            "meta_substitution_semantics_path",
        ),
        cases=tuple(_parse_case(item) for item in _required_list(data, "cases")),
    )


def validate_substitution_graph_correctness_cases(
    manifest: SubstitutionGraphCorrectnessCaseManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphCorrectnessCaseReport:
    """Validate proof cases and all checked dependency surfaces."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_correctness_path = Path(manifest.correctness_targets_path)
    checked_substitution_path = Path(manifest.formal_substitution_examples_path)
    checked_quotation_term_path = Path(manifest.quotation_term_examples_path)
    checked_formula_path = Path(manifest.formula_candidates_path)
    checked_representability_path = Path(
        manifest.substitution_representability_targets_path
    )
    checked_roundtrip_path = Path(manifest.codebook_roundtrip_path)
    checked_closure_path = Path(manifest.quotation_term_closure_path)
    checked_meta_substitution_path = Path(manifest.meta_substitution_semantics_path)

    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    correctness_targets = load_substitution_graph_correctness_targets(
        checked_correctness_path,
    )
    correctness_report = validate_substitution_graph_correctness_targets(
        correctness_targets,
        checked_willard_map_path,
    )
    substitution_examples = load_substitution_examples(checked_substitution_path)
    substitution_report = validate_substitution_examples(
        substitution_examples,
        checked_codebook_path,
        checked_language_path,
        checked_willard_map_path,
    )
    quotation_terms = load_quotation_term_examples(checked_quotation_term_path)
    quotation_term_report = validate_quotation_term_examples(
        quotation_terms,
        checked_codebook_path,
        checked_language_path,
        checked_willard_map_path,
    )
    formula_candidates = load_substitution_graph_formula_candidates(
        checked_formula_path,
    )
    formula_report = validate_substitution_graph_formula_candidates(
        formula_candidates,
        checked_willard_map_path,
    )
    representability_targets = load_substitution_representability_targets(
        checked_representability_path,
    )
    representability_report = validate_substitution_representability_targets(
        representability_targets,
        checked_language_path,
        checked_willard_map_path,
    )
    roundtrip_manifest = load_substitution_graph_codebook_roundtrip(
        checked_roundtrip_path,
    )
    roundtrip_report = validate_substitution_graph_codebook_roundtrip(
        roundtrip_manifest,
        checked_willard_map_path,
    )
    closure_manifest = load_substitution_graph_quotation_term_closure(
        checked_closure_path,
    )
    closure_report = validate_substitution_graph_quotation_term_closure(
        closure_manifest,
        checked_willard_map_path,
    )
    meta_substitution_manifest = load_substitution_graph_meta_substitution_semantics(
        checked_meta_substitution_path,
    )
    meta_substitution_report = validate_substitution_graph_meta_substitution_semantics(
        meta_substitution_manifest,
        checked_willard_map_path,
    )

    results: list[SubstitutionGraphCorrectnessCaseValidation] = [
        _accepted("manifest", f"loaded {len(manifest.cases)} case(s)")
    ]
    results.extend(_validate_references(manifest))
    dependency_results, accepted_dependencies = _validate_dependency_reports(
        codebook_report,
        correctness_report,
        substitution_report,
        quotation_term_report,
        formula_report,
        representability_report,
        roundtrip_report,
        closure_report,
        meta_substitution_report,
    )
    results.extend(dependency_results)
    case_results, observations = _validate_cases(
        manifest.cases,
        correctness_report.observations,
        accepted_dependencies,
    )
    results.extend(case_results)

    return SubstitutionGraphCorrectnessCaseReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        correctness_targets_path=checked_correctness_path,
        formal_substitution_examples_path=checked_substitution_path,
        quotation_term_examples_path=checked_quotation_term_path,
        formula_candidates_path=checked_formula_path,
        substitution_representability_targets_path=checked_representability_path,
        codebook_roundtrip_path=checked_roundtrip_path,
        quotation_term_closure_path=checked_closure_path,
        meta_substitution_semantics_path=checked_meta_substitution_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def substitution_graph_correctness_cases_report_payload(
    report: SubstitutionGraphCorrectnessCaseReport,
) -> dict[str, Any]:
    """Return a JSON-ready correctness-case report."""

    observations = {
        observation.case_id: observation for observation in report.observations
    }
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "case_manifest": str(report.manifest.path),
        "case_set_id": report.manifest.case_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "correctness_targets_path": str(report.correctness_targets_path),
        "formal_substitution_examples_path": str(
            report.formal_substitution_examples_path
        ),
        "quotation_term_examples_path": str(report.quotation_term_examples_path),
        "formula_candidates_path": str(report.formula_candidates_path),
        "substitution_representability_targets_path": str(
            report.substitution_representability_targets_path
        ),
        "codebook_roundtrip_path": str(report.codebook_roundtrip_path),
        "quotation_term_closure_path": str(report.quotation_term_closure_path),
        "meta_substitution_semantics_path": str(
            report.meta_substitution_semantics_path
        ),
        "willard_map": str(report.willard_map_path),
        "case_count": report.case_count,
        "failed_subjects": list(report.failed_subjects),
        "cases": [
            _case_payload(case, observations.get(case.case_id))
            for case in report.manifest.cases
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


def format_substitution_graph_correctness_cases_report(
    report: SubstitutionGraphCorrectnessCaseReport,
) -> str:
    """Format a concise human-readable correctness-case report."""

    observations = {
        observation.case_id: observation for observation in report.observations
    }
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Substitution graph correctness cases: {status}",
        f"Case set: {report.manifest.case_set_id}",
        f"Cases: {report.case_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for case in report.manifest.cases:
        observation = observations.get(case.case_id)
        dependency_count = "unknown"
        dependencies_present = "unknown"
        if observation is not None:
            dependency_count = str(observation.dependency_count)
            dependencies_present = str(observation.all_required_dependencies_present).lower()
        lines.extend([
            f"- {case.case_id}",
            f"  Case kind: {case.case_kind}",
            f"  Target: {case.correctness_target_id}",
            f"  Status: {case.status}",
            "  Dependencies: " + _joined_or_none(case.required_dependency_subjects),
            f"  Dependency count: {dependency_count}",
            f"  Dependencies present: {dependencies_present}",
            "  Future work: " + _joined_or_none(case.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_correctness_cases_cli(
    argv: list[str] | None = None,
) -> int:
    """Run substitution graph correctness-case validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.substitution_graph_correctness_cases",
        description="Validate AS substitution graph correctness proof cases.",
    )
    parser.add_argument(
        "--cases",
        default=str(DEFAULT_CASES),
        help="Path to the substitution graph correctness case manifest.",
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

    cases = load_substitution_graph_correctness_cases(args.cases)
    report = validate_substitution_graph_correctness_cases(
        cases,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(substitution_graph_correctness_cases_report_payload(report), sort_keys=True))
    else:
        print(format_substitution_graph_correctness_cases_report(report))
    return 0 if report.accepted else 1


def _case_payload(
    case: SubstitutionGraphCorrectnessCase,
    observation: SubstitutionGraphCorrectnessCaseObservation | None,
) -> dict[str, Any]:
    payload = {
        "case_id": case.case_id,
        "case_kind": case.case_kind,
        "correctness_target_id": case.correctness_target_id,
        "status": case.status,
        "required_dependency_subjects": list(case.required_dependency_subjects),
        "required_future_work": list(case.required_future_work),
        "non_claims": list(case.non_claims),
        "next_as_action": case.next_as_action,
    }
    if observation is None:
        payload.update({
            "observed_dependency_count": None,
            "observed_all_required_dependencies_present": None,
        })
    else:
        payload.update({
            "observed_dependency_count": observation.dependency_count,
            "observed_all_required_dependencies_present": (
                observation.all_required_dependencies_present
            ),
        })
    return payload


def _validate_references(
    manifest: SubstitutionGraphCorrectnessCaseManifest,
) -> list[SubstitutionGraphCorrectnessCaseValidation]:
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
            "formal_substitution_examples_path",
            manifest.formal_substitution_examples_path,
            "language/formal_substitution_examples.json",
        ),
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
            "substitution_representability_targets_path",
            manifest.substitution_representability_targets_path,
            "claims/substitution_representability_targets.json",
        ),
        (
            "codebook_roundtrip_path",
            manifest.codebook_roundtrip_path,
            "claims/substitution_graph_codebook_roundtrip.json",
        ),
        (
            "quotation_term_closure_path",
            manifest.quotation_term_closure_path,
            "claims/substitution_graph_quotation_term_closure.json",
        ),
        (
            "meta_substitution_semantics_path",
            manifest.meta_substitution_semantics_path,
            "claims/substitution_graph_meta_substitution_semantics.json",
        ),
    )
    results: list[SubstitutionGraphCorrectnessCaseValidation] = []
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
    substitution_report: Any,
    quotation_term_report: Any,
    formula_report: Any,
    representability_report: Any,
    roundtrip_report: Any,
    closure_report: Any,
    meta_substitution_report: Any,
) -> tuple[list[SubstitutionGraphCorrectnessCaseValidation], frozenset[str]]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        ("correctness_target", correctness_report, "correctness target"),
        ("formal_substitution", substitution_report, "formal substitution"),
        ("quotation_term", quotation_term_report, "quotation term"),
        ("formula_candidate", formula_report, "formula candidate"),
        (
            "substitution_representability",
            representability_report,
            "substitution representability",
        ),
        ("codebook_roundtrip", roundtrip_report, "codebook roundtrip"),
        ("quotation_term_closure", closure_report, "quotation term closure"),
        (
            "meta_substitution_semantics",
            meta_substitution_report,
            "meta-substitution semantics",
        ),
    )
    results: list[SubstitutionGraphCorrectnessCaseValidation] = []
    accepted_dependencies: set[str] = set()
    for subject, report, label in checks:
        if report.accepted:
            accepted_dependencies.add(subject)
            results.append(_accepted(subject, f"{label} accepted"))
        else:
            results.append(
                _rejected(
                    subject,
                    f"{label} rejected: " + _joined_or_none(report.failed_subjects),
                )
            )
    return results, frozenset(accepted_dependencies)


def _validate_cases(
    cases: tuple[SubstitutionGraphCorrectnessCase, ...],
    correctness_observations: tuple[SubstitutionGraphCorrectnessObservation, ...],
    accepted_dependencies: frozenset[str],
) -> tuple[
    list[SubstitutionGraphCorrectnessCaseValidation],
    list[SubstitutionGraphCorrectnessCaseObservation],
]:
    if not cases:
        return [_rejected("cases", "no substitution graph correctness cases")], []

    results: list[SubstitutionGraphCorrectnessCaseValidation] = []
    observations: list[SubstitutionGraphCorrectnessCaseObservation] = []
    case_ids = [case.case_id for case in cases]
    duplicate_ids = _duplicates(case_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "cases.case_id",
                "duplicate case ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("cases.case_id", "case ids are unique"))

    for case in cases:
        case_results, observation = _validate_case(
            case,
            correctness_observations,
            accepted_dependencies,
        )
        results.extend(case_results)
        if observation is not None:
            observations.append(observation)
    results.append(_accepted("cases", f"checked {len(cases)} case(s)"))
    return results, observations


def _validate_case(
    case: SubstitutionGraphCorrectnessCase,
    correctness_observations: tuple[SubstitutionGraphCorrectnessObservation, ...],
    accepted_dependencies: frozenset[str],
) -> tuple[
    list[SubstitutionGraphCorrectnessCaseValidation],
    SubstitutionGraphCorrectnessCaseObservation | None,
]:
    subject = case.case_id
    results: list[SubstitutionGraphCorrectnessCaseValidation] = []

    if case.status in PROVED_STATUS_REJECTIONS:
        results.append(
            _rejected(
                f"{subject}.status",
                "proved correctness cases are not supported",
            )
        )
    elif case.status not in VALID_CASE_STATUSES:
        results.append(_rejected(f"{subject}.status", f"unknown status: {case.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "status preserves non-claim"))

    if case.case_kind not in REQUIRED_CASE_KINDS:
        results.append(_rejected(f"{subject}.case_kind", f"unknown case kind: {case.case_kind}"))
    else:
        results.append(_accepted(f"{subject}.case_kind", "case kind is known"))

    try:
        _find_correctness_observation(
            correctness_observations,
            case.correctness_target_id,
        )
    except ValueError as exc:
        results.append(_rejected(f"{subject}.target", str(exc)))
        return results, None

    dependency_results, all_required_dependencies_present = _validate_case_dependencies(
        case,
        accepted_dependencies,
    )
    results.extend(dependency_results)

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in case.required_future_work
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
        item for item in REQUIRED_NON_CLAIMS if item not in case.non_claims
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

    if not all_required_dependencies_present:
        return results, None

    observation = SubstitutionGraphCorrectnessCaseObservation(
        case_id=case.case_id,
        case_kind=case.case_kind,
        correctness_target_id=case.correctness_target_id,
        status=case.status,
        dependency_count=len(case.required_dependency_subjects),
        all_required_dependencies_present=True,
    )
    return results, observation


def _validate_case_dependencies(
    case: SubstitutionGraphCorrectnessCase,
    accepted_dependencies: frozenset[str],
) -> tuple[list[SubstitutionGraphCorrectnessCaseValidation], bool]:
    subject = f"{case.case_id}.dependencies"
    required = REQUIRED_DEPENDENCIES_BY_KIND.get(case.case_kind)
    if required is None:
        return [_rejected(subject, f"unknown dependency plan for {case.case_kind}")], False

    missing_required = [
        dependency
        for dependency in required
        if dependency not in case.required_dependency_subjects
    ]
    if missing_required:
        return [
            _rejected(
                subject,
                "missing required dependencies: " + ", ".join(missing_required),
            )
        ], False

    unknown_dependencies = [
        dependency
        for dependency in case.required_dependency_subjects
        if dependency not in _all_dependency_subjects()
    ]
    if unknown_dependencies:
        return [
            _rejected(
                subject,
                "unknown dependencies: " + ", ".join(unknown_dependencies),
            )
        ], False

    unavailable_dependencies = [
        dependency
        for dependency in case.required_dependency_subjects
        if dependency not in accepted_dependencies
    ]
    if unavailable_dependencies:
        return [
            _rejected(
                subject,
                "dependencies not accepted: " + ", ".join(unavailable_dependencies),
            )
        ], False

    return [_accepted(subject, "required dependencies are accepted")], True


def _all_dependency_subjects() -> frozenset[str]:
    subjects: set[str] = set()
    for dependencies in REQUIRED_DEPENDENCIES_BY_KIND.values():
        subjects.update(dependencies)
    return frozenset(subjects)


def _find_correctness_observation(
    observations: tuple[SubstitutionGraphCorrectnessObservation, ...],
    target_id: str,
) -> SubstitutionGraphCorrectnessObservation:
    for observation in observations:
        if observation.target_id == target_id:
            return observation
    raise ValueError(f"unknown correctness target: {target_id}")


def _parse_case(
    item: dict[str, Any],
) -> SubstitutionGraphCorrectnessCase:
    return SubstitutionGraphCorrectnessCase(
        case_id=_required_text(item, "case_id"),
        case_kind=_required_text(item, "case_kind"),
        correctness_target_id=_required_text(item, "correctness_target_id"),
        status=_required_text(item, "status"),
        required_dependency_subjects=tuple(
            _required_text_list(item, "required_dependency_subjects")
        ),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject.endswith(".status"):
        return "substitution-graph-correctness-case-status"
    if subject.endswith(".case_kind"):
        return "substitution-graph-correctness-case-kind"
    if subject.endswith(".target"):
        return "substitution-graph-correctness-case-target"
    if subject.endswith(".dependencies"):
        return "substitution-graph-correctness-case-dependency"
    if subject.endswith(".required_future_work"):
        return "substitution-graph-correctness-case-future-work"
    if subject.endswith(".non_claims"):
        return "substitution-graph-correctness-case-non-claim"
    if subject in _all_dependency_subjects():
        return "substitution-graph-correctness-case-dependency"
    if subject.endswith("_path"):
        return "substitution-graph-correctness-case-reference"
    if subject.startswith("cases"):
        return "substitution-graph-correctness-case"
    return "substitution-graph-correctness-case"


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
) -> SubstitutionGraphCorrectnessCaseValidation:
    return SubstitutionGraphCorrectnessCaseValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphCorrectnessCaseValidation:
    return SubstitutionGraphCorrectnessCaseValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_correctness_cases_cli())
