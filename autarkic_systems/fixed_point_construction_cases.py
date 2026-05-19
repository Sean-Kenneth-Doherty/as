"""Open proof-case map for the AS fixed-point construction blocker.

This module validates a finite checklist of proof cases needed after the
checked fixed-point equation bridge target. It only records dependencies and
non-claims; it does not prove substitution representability, graph
correctness, bridge equality, a fixed-point equation, or self-consistency.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.diagonal_construction import (
    load_diagonal_construction_targets,
    validate_diagonal_construction_targets,
)
from autarkic_systems.fixed_point import (
    load_fixed_point_targets,
    validate_fixed_point_targets,
)
from autarkic_systems.fixed_point_equation_bridge import (
    load_fixed_point_equation_bridge_targets,
    validate_fixed_point_equation_bridge_targets,
)
from autarkic_systems.fixed_point_diagonal_instance_closure import (
    load_fixed_point_diagonal_instance_closure,
    validate_fixed_point_diagonal_instance_closure,
)
from autarkic_systems.formal_code import (
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.substitution_graph_correctness import (
    load_substitution_graph_correctness_targets,
    validate_substitution_graph_correctness_targets,
)
from autarkic_systems.substitution_graph_correctness_cases import (
    load_substitution_graph_correctness_cases,
    validate_substitution_graph_correctness_cases,
)
from autarkic_systems.substitution_representability import (
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)


DEFAULT_CASES = Path("claims/fixed_point_construction_cases.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_CASE_KINDS = (
    "diagonal-instance-closure",
    "substitution-representability-proof",
    "substitution-graph-correctness-proof",
    "bridge-equality-proof",
    "fixed-point-equation-lifting",
)
REQUIRED_DEPENDENCIES_BY_KIND = {
    "diagonal-instance-closure": (
        "fixed_point",
        "diagonal_construction",
        "fixed_point_equation_bridge",
        "diagonal_instance_closure",
    ),
    "substitution-representability-proof": (
        "substitution_representability",
        "substitution_graph_correctness_cases",
        "fixed_point_equation_bridge",
    ),
    "substitution-graph-correctness-proof": (
        "substitution_graph_correctness",
        "substitution_graph_correctness_cases",
    ),
    "bridge-equality-proof": (
        "fixed_point_equation_bridge",
        "substitution_representability",
        "substitution_graph_correctness_cases",
    ),
    "fixed-point-equation-lifting": (
        "fixed_point",
        "fixed_point_equation_bridge",
        "codebook",
    ),
}
REQUIRED_FUTURE_WORK = (
    "substitution-representability-proof",
    "substitution-graph-correctness-proof",
    "bridge-equality-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)


@dataclass(frozen=True)
class FixedPointConstructionCase:
    """One open proof case for the fixed-point construction blocker."""

    case_id: str
    case_kind: str
    target_id: str
    status: str
    required_dependency_subjects: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointConstructionCaseManifest:
    """Loaded manifest for fixed-point construction proof cases."""

    path: Path
    schema_version: int
    case_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    fixed_point_targets_path: str
    diagonal_construction_targets_path: str
    substitution_representability_targets_path: str
    substitution_graph_correctness_targets_path: str
    substitution_graph_correctness_cases_path: str
    fixed_point_equation_bridge_targets_path: str
    diagonal_instance_closure_path: str
    cases: tuple[FixedPointConstructionCase, ...]


@dataclass(frozen=True)
class FixedPointConstructionCaseValidation:
    """One validation result for a fixed-point construction case map."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointConstructionCaseObservation:
    """Observed dependency facts for one proof case."""

    case_id: str
    case_kind: str
    target_id: str
    status: str
    observed_dependency_count: int
    all_required_dependencies_present: bool


@dataclass(frozen=True)
class FixedPointConstructionCaseReport:
    """Validation report for fixed-point construction proof cases."""

    manifest: FixedPointConstructionCaseManifest
    formal_language_path: Path
    codebook_path: Path
    fixed_point_targets_path: Path
    diagonal_construction_targets_path: Path
    substitution_representability_targets_path: Path
    substitution_graph_correctness_targets_path: Path
    substitution_graph_correctness_cases_path: Path
    fixed_point_equation_bridge_targets_path: Path
    diagonal_instance_closure_path: Path
    willard_map_path: Path
    results: tuple[FixedPointConstructionCaseValidation, ...]
    observations: tuple[FixedPointConstructionCaseObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every construction-case validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def case_count(self) -> int:
        """Return the number of checked construction cases."""

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


def load_fixed_point_construction_cases(
    path: Path | str = DEFAULT_CASES,
) -> FixedPointConstructionCaseManifest:
    """Load the fixed-point construction case manifest from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return FixedPointConstructionCaseManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        case_set_id=_required_text(data, "case_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        diagonal_construction_targets_path=_required_text(
            data,
            "diagonal_construction_targets_path",
        ),
        substitution_representability_targets_path=_required_text(
            data,
            "substitution_representability_targets_path",
        ),
        substitution_graph_correctness_targets_path=_required_text(
            data,
            "substitution_graph_correctness_targets_path",
        ),
        substitution_graph_correctness_cases_path=_required_text(
            data,
            "substitution_graph_correctness_cases_path",
        ),
        fixed_point_equation_bridge_targets_path=_required_text(
            data,
            "fixed_point_equation_bridge_targets_path",
        ),
        diagonal_instance_closure_path=_required_text(
            data,
            "diagonal_instance_closure_path",
        ),
        cases=tuple(_parse_case(item) for item in _required_list(data, "cases")),
    )


def validate_fixed_point_construction_cases(
    manifest: FixedPointConstructionCaseManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointConstructionCaseReport:
    """Validate fixed-point construction proof cases and dependencies."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)
    checked_diagonal_path = Path(manifest.diagonal_construction_targets_path)
    checked_witness_path = Path(manifest.substitution_representability_targets_path)
    checked_graph_correctness_path = Path(
        manifest.substitution_graph_correctness_targets_path
    )
    checked_graph_cases_path = Path(manifest.substitution_graph_correctness_cases_path)
    checked_bridge_path = Path(manifest.fixed_point_equation_bridge_targets_path)
    checked_diagonal_closure_path = Path(manifest.diagonal_instance_closure_path)

    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    fixed_point_targets = load_fixed_point_targets(checked_fixed_point_path)
    fixed_point_report = validate_fixed_point_targets(
        fixed_point_targets,
        checked_willard_map_path,
        checked_language_path,
    )
    diagonal_targets = load_diagonal_construction_targets(checked_diagonal_path)
    diagonal_report = validate_diagonal_construction_targets(
        diagonal_targets,
        checked_language_path,
        checked_willard_map_path,
    )
    witnesses = load_substitution_representability_targets(checked_witness_path)
    witness_report = validate_substitution_representability_targets(
        witnesses,
        checked_language_path,
        checked_willard_map_path,
    )
    graph_correctness = load_substitution_graph_correctness_targets(
        checked_graph_correctness_path,
    )
    graph_correctness_report = validate_substitution_graph_correctness_targets(
        graph_correctness,
        checked_willard_map_path,
    )
    graph_cases = load_substitution_graph_correctness_cases(checked_graph_cases_path)
    graph_case_report = validate_substitution_graph_correctness_cases(
        graph_cases,
        checked_willard_map_path,
    )
    bridge_targets = load_fixed_point_equation_bridge_targets(checked_bridge_path)
    bridge_report = validate_fixed_point_equation_bridge_targets(
        bridge_targets,
        checked_language_path,
        checked_willard_map_path,
    )
    diagonal_closure = load_fixed_point_diagonal_instance_closure(
        checked_diagonal_closure_path
    )
    diagonal_closure_report = validate_fixed_point_diagonal_instance_closure(
        diagonal_closure,
        checked_willard_map_path,
    )

    results: list[FixedPointConstructionCaseValidation] = [
        _accepted("manifest", f"loaded {len(manifest.cases)} case(s)")
    ]
    observations: list[FixedPointConstructionCaseObservation] = []
    results.extend(_validate_references(manifest))
    dependency_results, accepted_dependencies = _validate_dependency_reports(
        codebook_report,
        fixed_point_report,
        diagonal_report,
        witness_report,
        graph_correctness_report,
        graph_case_report,
        bridge_report,
        diagonal_closure_report,
    )
    results.extend(dependency_results)
    case_results, observations = _validate_cases(manifest.cases, accepted_dependencies)
    results.extend(case_results)

    return FixedPointConstructionCaseReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        fixed_point_targets_path=checked_fixed_point_path,
        diagonal_construction_targets_path=checked_diagonal_path,
        substitution_representability_targets_path=checked_witness_path,
        substitution_graph_correctness_targets_path=checked_graph_correctness_path,
        substitution_graph_correctness_cases_path=checked_graph_cases_path,
        fixed_point_equation_bridge_targets_path=checked_bridge_path,
        diagonal_instance_closure_path=checked_diagonal_closure_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def fixed_point_construction_cases_payload(
    report: FixedPointConstructionCaseReport,
) -> dict[str, Any]:
    """Return a JSON-ready fixed-point construction case payload."""

    observations = {observation.case_id: observation for observation in report.observations}
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "case_manifest": str(report.manifest.path),
        "case_set_id": report.manifest.case_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "diagonal_construction_targets_path": str(
            report.diagonal_construction_targets_path
        ),
        "substitution_representability_targets_path": str(
            report.substitution_representability_targets_path
        ),
        "substitution_graph_correctness_targets_path": str(
            report.substitution_graph_correctness_targets_path
        ),
        "substitution_graph_correctness_cases_path": str(
            report.substitution_graph_correctness_cases_path
        ),
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "diagonal_instance_closure_path": str(report.diagonal_instance_closure_path),
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


def format_fixed_point_construction_cases_report(
    report: FixedPointConstructionCaseReport,
) -> str:
    """Format a concise human-readable construction-case report."""

    observations = {observation.case_id: observation for observation in report.observations}
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point construction cases: {status}",
        f"Case set: {report.manifest.case_set_id}",
        f"Cases: {report.case_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for case in report.manifest.cases:
        observation = observations.get(case.case_id)
        dependency_count = "unknown"
        if observation is not None:
            dependency_count = str(observation.observed_dependency_count)
        lines.extend([
            f"- {case.case_id}",
            f"  Kind: {case.case_kind}",
            f"  Status: {case.status}",
            f"  Dependencies: {_joined_or_none(case.required_dependency_subjects)}",
            f"  Observed dependency count: {dependency_count}",
            "  Future work: " + _joined_or_none(case.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_construction_cases_cli(argv: list[str] | None = None) -> int:
    """Run fixed-point construction case validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_construction_cases",
        description="Validate AS fixed-point construction proof cases.",
    )
    parser.add_argument(
        "--cases",
        default=str(DEFAULT_CASES),
        help="Path to the fixed-point construction case manifest.",
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

    manifest = load_fixed_point_construction_cases(args.cases)
    report = validate_fixed_point_construction_cases(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(fixed_point_construction_cases_payload(report), sort_keys=True))
    else:
        print(format_fixed_point_construction_cases_report(report))
    return 0 if report.accepted else 1


def _case_payload(
    case: FixedPointConstructionCase,
    observation: FixedPointConstructionCaseObservation | None,
) -> dict[str, Any]:
    payload = {
        "case_id": case.case_id,
        "case_kind": case.case_kind,
        "target_id": case.target_id,
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
            "observed_dependency_count": observation.observed_dependency_count,
            "observed_all_required_dependencies_present": (
                observation.all_required_dependencies_present
            ),
        })
    return payload


def _validate_references(
    manifest: FixedPointConstructionCaseManifest,
) -> list[FixedPointConstructionCaseValidation]:
    expected = (
        (
            "formal_language_path",
            manifest.formal_language_path,
            "language/formal_arithmetic_language.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "fixed_point_targets_path",
            manifest.fixed_point_targets_path,
            "claims/fixed_point_targets.json",
        ),
        (
            "diagonal_construction_targets_path",
            manifest.diagonal_construction_targets_path,
            "claims/diagonal_construction_targets.json",
        ),
        (
            "substitution_representability_targets_path",
            manifest.substitution_representability_targets_path,
            "claims/substitution_representability_targets.json",
        ),
        (
            "substitution_graph_correctness_targets_path",
            manifest.substitution_graph_correctness_targets_path,
            "claims/substitution_graph_correctness_targets.json",
        ),
        (
            "substitution_graph_correctness_cases_path",
            manifest.substitution_graph_correctness_cases_path,
            "claims/substitution_graph_correctness_cases.json",
        ),
        (
            "fixed_point_equation_bridge_targets_path",
            manifest.fixed_point_equation_bridge_targets_path,
            "claims/fixed_point_equation_bridge_targets.json",
        ),
        (
            "diagonal_instance_closure_path",
            manifest.diagonal_instance_closure_path,
            "claims/fixed_point_diagonal_instance_closure.json",
        ),
    )
    results: list[FixedPointConstructionCaseValidation] = []
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
    fixed_point_report: Any,
    diagonal_report: Any,
    witness_report: Any,
    graph_correctness_report: Any,
    graph_case_report: Any,
    bridge_report: Any,
    diagonal_closure_report: Any,
) -> tuple[list[FixedPointConstructionCaseValidation], frozenset[str]]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        ("fixed_point", fixed_point_report, "fixed-point target"),
        ("diagonal_construction", diagonal_report, "diagonal construction"),
        ("substitution_representability", witness_report, "substitution witness"),
        (
            "substitution_graph_correctness",
            graph_correctness_report,
            "substitution graph correctness target",
        ),
        (
            "substitution_graph_correctness_cases",
            graph_case_report,
            "substitution graph correctness cases",
        ),
        (
            "fixed_point_equation_bridge",
            bridge_report,
            "fixed-point equation bridge",
        ),
        (
            "diagonal_instance_closure",
            diagonal_closure_report,
            "fixed-point diagonal instance closure",
        ),
    )
    results: list[FixedPointConstructionCaseValidation] = []
    accepted_dependencies: set[str] = set()
    for subject, report, label in checks:
        if report.accepted:
            results.append(_accepted(subject, f"{label} accepted"))
            accepted_dependencies.add(subject)
        else:
            results.append(
                _rejected(
                    subject,
                    f"{label} rejected: " + _joined_or_none(report.failed_subjects),
                )
            )
    return results, frozenset(accepted_dependencies)


def _validate_cases(
    cases: tuple[FixedPointConstructionCase, ...],
    accepted_dependencies: frozenset[str],
) -> tuple[list[FixedPointConstructionCaseValidation], list[FixedPointConstructionCaseObservation]]:
    if not cases:
        return [_rejected("cases", "no fixed-point construction cases")], []

    results: list[FixedPointConstructionCaseValidation] = []
    observations: list[FixedPointConstructionCaseObservation] = []
    case_ids = [case.case_id for case in cases]
    duplicate_ids = _duplicates(case_ids)
    if duplicate_ids:
        results.append(
            _rejected("cases.case_id", "duplicate case ids: " + ", ".join(duplicate_ids))
        )
    else:
        results.append(_accepted("cases.case_id", "case ids are unique"))

    observed_kinds = tuple(case.case_kind for case in cases)
    if observed_kinds != REQUIRED_CASE_KINDS:
        results.append(
            _rejected(
                "cases.case_kind",
                "case kind order mismatch: " + ", ".join(observed_kinds),
            )
        )
    else:
        results.append(_accepted("cases.case_kind", "required case kinds are present"))

    for case in cases:
        case_results, observation = _validate_case(case, accepted_dependencies)
        results.extend(case_results)
        observations.append(observation)
    results.append(_accepted("cases", f"checked {len(cases)} case(s)"))
    return results, observations


def _validate_case(
    case: FixedPointConstructionCase,
    accepted_dependencies: frozenset[str],
) -> tuple[list[FixedPointConstructionCaseValidation], FixedPointConstructionCaseObservation]:
    subject = case.case_id
    results: list[FixedPointConstructionCaseValidation] = []
    expected_dependencies = REQUIRED_DEPENDENCIES_BY_KIND.get(case.case_kind)

    if case.status == "fixed-point-equation-proved":
        results.append(
            _rejected(
                f"{subject}.status",
                "proved fixed-point construction cases are not supported",
            )
        )
    elif case.status != "proof-case-open":
        results.append(_rejected(f"{subject}.status", f"unknown status: {case.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "status preserves non-claim"))

    if expected_dependencies is None:
        results.append(_rejected(f"{subject}.case_kind", "unknown case kind"))
        expected_dependencies = ()
    elif case.required_dependency_subjects != expected_dependencies:
        results.append(
            _rejected(
                f"{subject}.dependencies",
                "dependency list mismatch: expected "
                + ", ".join(expected_dependencies)
                + " got "
                + ", ".join(case.required_dependency_subjects),
            )
        )
    else:
        results.append(_accepted(f"{subject}.dependencies", "dependency list matches"))

    all_required_dependencies_present = all(
        dependency in accepted_dependencies
        for dependency in case.required_dependency_subjects
    )
    if all_required_dependencies_present:
        results.append(
            _accepted(f"{subject}.accepted_dependencies", "required dependencies are accepted")
        )
    else:
        missing = [
            dependency
            for dependency in case.required_dependency_subjects
            if dependency not in accepted_dependencies
        ]
        results.append(
            _rejected(
                f"{subject}.accepted_dependencies",
                "missing accepted dependencies: " + ", ".join(missing),
            )
        )

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

    if case.next_as_action.strip():
        results.append(_accepted(f"{subject}.next_as_action", "next action present"))
    else:
        results.append(_rejected(f"{subject}.next_as_action", "missing next action"))

    observation = FixedPointConstructionCaseObservation(
        case_id=case.case_id,
        case_kind=case.case_kind,
        target_id=case.target_id,
        status=case.status,
        observed_dependency_count=len(case.required_dependency_subjects),
        all_required_dependencies_present=all_required_dependencies_present,
    )
    return results, observation


def _parse_case(item: dict[str, Any]) -> FixedPointConstructionCase:
    return FixedPointConstructionCase(
        case_id=_required_text(item, "case_id"),
        case_kind=_required_text(item, "case_kind"),
        target_id=_required_text(item, "target_id"),
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
        return "fixed-point-construction-case-status"
    if subject.endswith(".dependencies") or subject.endswith(".accepted_dependencies"):
        return "fixed-point-construction-case-dependency"
    if subject.endswith(".case_kind") or subject == "cases.case_kind":
        return "fixed-point-construction-case-kind"
    if subject.endswith(".required_future_work"):
        return "fixed-point-construction-case-future-work"
    if subject.endswith(".non_claims"):
        return "fixed-point-construction-case-non-claim"
    if subject.endswith(".next_as_action"):
        return "fixed-point-construction-case-next-action"
    if subject.startswith("cases"):
        return "fixed-point-construction-case"
    if subject in {
        "codebook",
        "fixed_point",
        "diagonal_construction",
        "substitution_representability",
        "substitution_graph_correctness",
        "substitution_graph_correctness_cases",
        "fixed_point_equation_bridge",
        "diagonal_instance_closure",
    }:
        return "fixed-point-construction-case-dependency"
    if subject.endswith("_path"):
        return "fixed-point-construction-case-reference"
    return "fixed-point-construction-case"


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
) -> FixedPointConstructionCaseValidation:
    return FixedPointConstructionCaseValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointConstructionCaseValidation:
    return FixedPointConstructionCaseValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_construction_cases_cli())
