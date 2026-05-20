"""Compact status surface for substitution graph correctness.

The substitution graph correctness stack already has individual validators for
targets, finite graph-domain evidence, and proof-case decomposition. This
module is deliberately smaller: it observes the current case manifest, checks
that referenced support artifacts are present and still non-promotional, and
reports the blocked frontier without running expensive proof derivations.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.substitution_graph_correctness_cases import (
    REQUIRED_CASE_KINDS,
    REQUIRED_DEPENDENCIES_BY_KIND,
    load_substitution_graph_correctness_cases,
)


DEFAULT_STATUS = Path("claims/substitution_graph_correctness_frontier_status.json")

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "substitution-graph-correctness"
REQUIRED_NON_CLAIMS = (
    "no formula correctness proof",
    "no substitution representability proof",
    "no diagonal lemma proof",
    "no fixed-point equation proof",
    "no self-consistency theorem",
)
REQUIRED_SUPPORT_SUBJECTS = (
    "correctness_target",
    "codebook",
    "quotation_term",
    "formal_substitution",
    "formula_candidate",
    "substitution_representability",
    "codebook_roundtrip",
    "quotation_term_closure",
    "meta_substitution_semantics",
    "formula_schema_relation",
    "diagonal_witness_composition",
)
FINITE_SUPPORT_BY_CASE_KIND = {
    "codebook-roundtrip": ("codebook_roundtrip",),
    "quotation-term-closure": ("quotation_term_closure",),
    "meta-substitution-semantics": ("meta_substitution_semantics",),
    "formula-schema-relation": ("formula_schema_relation",),
    "diagonal-witness-composition": ("diagonal_witness_composition",),
}
PROOF_PROMOTION_STATUSES = {
    "formula-correctness-proved",
    "substitution-representability-proved",
    "substitution-graph-correctness-proved",
    "diagonal-lemma-proved",
    "fixed-point-equation-proved",
    "self-consistency-proved",
    "self-consistency-theorem-proved",
}
EXPECTED_CASES_PATH = "claims/substitution_graph_correctness_cases.json"
EXPECTED_CASE_PATHS = {
    "formal_language_path": "language/formal_arithmetic_language.json",
    "codebook_path": "language/formal_codebook.json",
    "correctness_targets_path": "claims/substitution_graph_correctness_targets.json",
    "formal_substitution_examples_path": "language/formal_substitution_examples.json",
    "quotation_term_examples_path": "language/formal_quotation_term_examples.json",
    "formula_candidates_path": "claims/substitution_graph_formula_candidates.json",
    "substitution_representability_targets_path": (
        "claims/substitution_representability_targets.json"
    ),
    "codebook_roundtrip_path": "claims/substitution_graph_codebook_roundtrip.json",
    "quotation_term_closure_path": (
        "claims/substitution_graph_quotation_term_closure.json"
    ),
    "meta_substitution_semantics_path": (
        "claims/substitution_graph_meta_substitution_semantics.json"
    ),
    "formula_schema_relation_path": (
        "claims/substitution_graph_formula_schema_relation.json"
    ),
    "diagonal_witness_composition_path": (
        "claims/substitution_graph_diagonal_witness_composition.json"
    ),
}
SUPPORT_PATH_FIELDS = {
    "correctness_target": "correctness_targets_path",
    "codebook": "codebook_path",
    "quotation_term": "quotation_term_examples_path",
    "formal_substitution": "formal_substitution_examples_path",
    "formula_candidate": "formula_candidates_path",
    "substitution_representability": "substitution_representability_targets_path",
    "codebook_roundtrip": "codebook_roundtrip_path",
    "quotation_term_closure": "quotation_term_closure_path",
    "meta_substitution_semantics": "meta_substitution_semantics_path",
    "formula_schema_relation": "formula_schema_relation_path",
    "diagonal_witness_composition": "diagonal_witness_composition_path",
}
SUPPORT_ID_FIELDS = {
    "correctness_target": (
        "target_set_id",
        "as-substitution-graph-correctness-target-v1",
    ),
    "codebook": ("codebook_id", "as-formal-codebook-v1"),
    "quotation_term": ("term_set_id", "as-formal-quotation-term-v1"),
    "formal_substitution": ("example_set_id", "as-formal-substitution-v1"),
    "formula_candidate": (
        "candidate_set_id",
        "as-substitution-graph-formula-candidates-v1",
    ),
    "substitution_representability": (
        "witness_set_id",
        "as-substitution-representability-witness-v1",
    ),
    "codebook_roundtrip": (
        "roundtrip_set_id",
        "as-substitution-graph-codebook-roundtrip-v1",
    ),
    "quotation_term_closure": (
        "closure_set_id",
        "as-substitution-graph-quotation-term-closure-v1",
    ),
    "meta_substitution_semantics": (
        "semantics_set_id",
        "as-substitution-graph-meta-substitution-semantics-v1",
    ),
    "formula_schema_relation": (
        "relation_set_id",
        "as-substitution-graph-formula-schema-relation-v1",
    ),
    "diagonal_witness_composition": (
        "composition_set_id",
        "as-substitution-graph-diagonal-witness-composition-v1",
    ),
}


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessFrontierStatusManifest:
    """Loaded manifest for the compact correctness frontier status."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    substitution_graph_correctness_cases_path: str
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessFrontierStatusValidation:
    """One validation result for the correctness frontier status."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessFrontierSupportSurface:
    """Observed support artifact referenced by the correctness case manifest."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessFrontierCaseSupport:
    """Per-case support summary while the proof case remains open."""

    case_id: str
    case_kind: str
    correctness_target_id: str
    status: str
    support_subjects: tuple[str, ...]
    finite_support_subjects: tuple[str, ...]
    support_accepted: bool
    finite_support_accepted: bool


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessFrontierStatusReport:
    """Compact validation report for the correctness frontier."""

    manifest: SubstitutionGraphCorrectnessFrontierStatusManifest
    substitution_graph_correctness_cases_path: Path
    results: tuple[SubstitutionGraphCorrectnessFrontierStatusValidation, ...]
    support_surfaces: tuple[
        SubstitutionGraphCorrectnessFrontierSupportSurface,
        ...,
    ]
    case_supports: tuple[SubstitutionGraphCorrectnessFrontierCaseSupport, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every compact frontier validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def frontier_status(self) -> str:
        """Return the frontier status preserved by the manifest."""

        return self.manifest.frontier_status

    @property
    def frontier_blocked_by(self) -> str:
        """Return the blocker preserved by the manifest."""

        return self.manifest.frontier_blocked_by

    @property
    def case_count(self) -> int:
        """Return the number of observed correctness cases."""

        return len(self.case_supports)

    @property
    def open_case_count(self) -> int:
        """Return the number of observed cases still explicitly open."""

        return sum(1 for case in self.case_supports if case.status == "proof-case-open")

    @property
    def support_surface_count(self) -> int:
        """Return the number of observed support surfaces."""

        return len(self.support_surfaces)

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return compact failure subjects for automation and handoff reports."""

        subjects: list[str] = []
        for result in self.results:
            if result.accepted:
                continue
            subject = _failed_subject_for_result(result.subject)
            if subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)


def load_substitution_graph_correctness_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> SubstitutionGraphCorrectnessFrontierStatusManifest:
    """Load the compact substitution graph correctness frontier manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return SubstitutionGraphCorrectnessFrontierStatusManifest(
        path=status_path,
        schema_version=_required_int(data, "schema_version"),
        status_set_id=_required_text(data, "status_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        frontier_status=_required_text(data, "frontier_status"),
        frontier_blocked_by=_required_text(data, "frontier_blocked_by"),
        substitution_graph_correctness_cases_path=_required_text(
            data,
            "substitution_graph_correctness_cases_path",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_correctness_frontier_status(
    manifest: SubstitutionGraphCorrectnessFrontierStatusManifest,
) -> SubstitutionGraphCorrectnessFrontierStatusReport:
    """Validate the compact correctness frontier without deep derivations."""

    cases_path = Path(manifest.substitution_graph_correctness_cases_path)
    cases_manifest = None
    case_load_results: list[
        SubstitutionGraphCorrectnessFrontierStatusValidation
    ] = []
    try:
        cases_manifest = load_substitution_graph_correctness_cases(cases_path)
        case_load_results.append(_accepted("cases_manifest", "case manifest loaded"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        case_load_results.append(
            _rejected(
                "cases_manifest",
                f"case manifest missing or invalid: {exc}",
            )
        )

    results: list[SubstitutionGraphCorrectnessFrontierStatusValidation] = [
        _accepted("manifest", f"loaded {manifest.status_set_id}")
    ]
    results.extend(_validate_manifest(manifest))
    results.extend(case_load_results)

    support_surfaces: list[
        SubstitutionGraphCorrectnessFrontierSupportSurface
    ] = []
    case_supports: list[SubstitutionGraphCorrectnessFrontierCaseSupport] = []
    if cases_manifest is None:
        results.append(_rejected("cases", "no correctness cases observed"))
    else:
        results.extend(_validate_case_manifest(cases_manifest))
        support_surfaces = _support_surfaces(cases_manifest)
        results.extend(_validate_support_surfaces(support_surfaces))
        accepted_support_subjects = frozenset(
            surface.subject for surface in support_surfaces if surface.accepted
        )
        case_supports, case_results = _case_supports(
            cases_manifest.cases,
            accepted_support_subjects,
        )
        results.extend(case_results)

    return SubstitutionGraphCorrectnessFrontierStatusReport(
        manifest=manifest,
        substitution_graph_correctness_cases_path=cases_path,
        results=tuple(results),
        support_surfaces=tuple(support_surfaces),
        case_supports=tuple(case_supports),
    )


def substitution_graph_correctness_frontier_status_payload(
    report: SubstitutionGraphCorrectnessFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready correctness frontier status payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "status_manifest": str(report.manifest.path),
        "status_set_id": report.manifest.status_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "frontier_status": report.frontier_status,
        "frontier_blocked_by": report.frontier_blocked_by,
        "substitution_graph_correctness_cases_path": str(
            report.substitution_graph_correctness_cases_path
        ),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "support_surface_count": report.support_surface_count,
        "case_count": report.case_count,
        "open_case_count": report.open_case_count,
        "failed_subjects": list(report.failed_subjects),
        "support_surfaces": [
            {
                "subject": surface.subject,
                "path": str(surface.path),
                "accepted": surface.accepted,
                "failed_subjects": list(surface.failed_subjects),
                "detail": surface.detail,
            }
            for surface in report.support_surfaces
        ],
        "case_supports": [
            {
                "case_id": case.case_id,
                "case_kind": case.case_kind,
                "correctness_target_id": case.correctness_target_id,
                "status": case.status,
                "support_subjects": list(case.support_subjects),
                "finite_support_subjects": list(case.finite_support_subjects),
                "support_accepted": case.support_accepted,
                "finite_support_accepted": case.finite_support_accepted,
            }
            for case in report.case_supports
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


def format_substitution_graph_correctness_frontier_status_report(
    report: SubstitutionGraphCorrectnessFrontierStatusReport,
) -> str:
    """Format a concise human-readable correctness frontier report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Substitution graph correctness frontier status: {status}",
        f"Status set: {report.manifest.status_set_id}",
        f"Frontier status: {report.frontier_status}",
        f"Blocked by: {report.frontier_blocked_by}",
        f"Open correctness cases: {report.open_case_count}/{report.case_count}",
        f"Support surfaces: {report.support_surface_count}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Support:")
    for surface in report.support_surfaces:
        prefix = "accepted" if surface.accepted else "rejected"
        lines.append(f"- {surface.subject}: {prefix} ({surface.path})")
    lines.append("Correctness cases:")
    for case in report.case_supports:
        lines.extend([
            f"- {case.case_id}",
            f"  Case kind: {case.case_kind}",
            f"  Target: {case.correctness_target_id}",
            f"  Status: {case.status}",
            f"  Support: {_joined_or_none(case.support_subjects)}",
            f"  Finite support: {_joined_or_none(case.finite_support_subjects)}",
            f"  Support accepted: {case.support_accepted}",
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_correctness_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run substitution graph correctness frontier status validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.substitution_graph_correctness_frontier_status"
        ),
        description="Validate the AS substitution graph correctness frontier status.",
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the substitution graph correctness frontier status manifest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_substitution_graph_correctness_frontier_status(args.status)
    report = validate_substitution_graph_correctness_frontier_status(manifest)
    if args.format == "json":
        print(json.dumps(
            substitution_graph_correctness_frontier_status_payload(report),
            sort_keys=True,
        ))
    else:
        print(format_substitution_graph_correctness_frontier_status_report(report))
    return 0 if report.accepted else 1


def _validate_manifest(
    manifest: SubstitutionGraphCorrectnessFrontierStatusManifest,
) -> list[SubstitutionGraphCorrectnessFrontierStatusValidation]:
    results: list[SubstitutionGraphCorrectnessFrontierStatusValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if (
        manifest.status_set_id
        == "as-substitution-graph-correctness-frontier-status-v1"
    ):
        results.append(_accepted("status_set_id", "status set id matches"))
    else:
        results.append(_rejected("status_set_id", "unexpected status set id"))

    if manifest.frontier_status == REQUIRED_FRONTIER_STATUS:
        results.append(_accepted("frontier_status", "frontier remains blocked"))
    elif manifest.frontier_status in PROOF_PROMOTION_STATUSES:
        results.append(
            _rejected(
                "frontier_status",
                "overclaiming frontier status: " + manifest.frontier_status,
            )
        )
    else:
        results.append(
            _rejected(
                "frontier_status",
                "unsupported frontier status: " + manifest.frontier_status,
            )
        )

    if manifest.frontier_blocked_by == REQUIRED_FRONTIER_BLOCKER:
        results.append(
            _accepted(
                "frontier_blocked_by",
                "blocked by substitution-graph-correctness",
            )
        )
    else:
        results.append(
            _rejected(
                "frontier_blocked_by",
                "expected substitution-graph-correctness blocker",
            )
        )

    if manifest.substitution_graph_correctness_cases_path == EXPECTED_CASES_PATH:
        results.append(
            _accepted(
                "substitution_graph_correctness_cases_path",
                f"{EXPECTED_CASES_PATH} referenced",
            )
        )
    else:
        results.append(
            _rejected(
                "substitution_graph_correctness_cases_path",
                (
                    f"expected {EXPECTED_CASES_PATH} but found "
                    f"{manifest.substitution_graph_correctness_cases_path}"
                ),
            )
        )

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


def _validate_case_manifest(
    manifest: Any,
) -> list[SubstitutionGraphCorrectnessFrontierStatusValidation]:
    results: list[SubstitutionGraphCorrectnessFrontierStatusValidation] = []
    if manifest.case_set_id == "as-substitution-graph-correctness-cases-v1":
        results.append(_accepted("case_set_id", "case set id matches"))
    else:
        results.append(_rejected("case_set_id", "unexpected case set id"))

    for field, expected in EXPECTED_CASE_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))
    return results


def _support_surfaces(
    cases_manifest: Any,
) -> list[SubstitutionGraphCorrectnessFrontierSupportSurface]:
    surfaces: list[SubstitutionGraphCorrectnessFrontierSupportSurface] = []
    for subject in REQUIRED_SUPPORT_SUBJECTS:
        path = Path(getattr(cases_manifest, SUPPORT_PATH_FIELDS[subject]))
        accepted, failed_subjects, detail = _inspect_support_artifact(subject, path)
        surfaces.append(
            SubstitutionGraphCorrectnessFrontierSupportSurface(
                subject=subject,
                path=path,
                accepted=accepted,
                failed_subjects=failed_subjects,
                detail=detail,
            )
        )
    return surfaces


def _inspect_support_artifact(
    subject: str,
    path: Path,
) -> tuple[bool, tuple[str, ...], str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return (
            False,
            (f"substitution-graph-correctness-{subject}-support-load",),
            f"support artifact missing or invalid: {exc}",
        )

    failures: list[str] = []
    id_field, expected_id = SUPPORT_ID_FIELDS[subject]
    if data.get(id_field) != expected_id:
        failures.append(f"substitution-graph-correctness-{subject}-support-id")

    if subject in _finite_support_subjects():
        non_claim_failures = _support_non_claim_failures(subject, data)
        failures.extend(non_claim_failures)

    if failures:
        return False, tuple(failures), "support artifact rejected: " + ", ".join(failures)
    return True, (), "accepted"


def _support_non_claim_failures(subject: str, data: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    values = data.get("non_claims")
    if not isinstance(values, list) or not values:
        return [f"substitution-graph-correctness-{subject}-support-non-claim"]
    if any(not isinstance(value, str) or not value.strip() for value in values):
        return [f"substitution-graph-correctness-{subject}-support-non-claim"]
    missing = [item for item in REQUIRED_NON_CLAIMS if item not in values]
    if missing:
        failures.append(f"substitution-graph-correctness-{subject}-support-non-claim")
    return failures


def _validate_support_surfaces(
    surfaces: list[SubstitutionGraphCorrectnessFrontierSupportSurface],
) -> list[SubstitutionGraphCorrectnessFrontierStatusValidation]:
    results: list[SubstitutionGraphCorrectnessFrontierStatusValidation] = []
    observed_subjects = tuple(surface.subject for surface in surfaces)
    if observed_subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(_accepted("support_surfaces", "required support surfaces present"))
    else:
        results.append(_rejected("support_surfaces", "support surface order mismatch"))

    for surface in surfaces:
        if surface.accepted:
            results.append(_accepted(surface.subject, surface.detail))
        else:
            results.append(_rejected(surface.subject, surface.detail))
    return results


def _case_supports(
    cases: tuple[Any, ...],
    accepted_support_subjects: frozenset[str],
) -> tuple[
    list[SubstitutionGraphCorrectnessFrontierCaseSupport],
    list[SubstitutionGraphCorrectnessFrontierStatusValidation],
]:
    case_supports: list[SubstitutionGraphCorrectnessFrontierCaseSupport] = []
    results: list[SubstitutionGraphCorrectnessFrontierStatusValidation] = []

    if len(cases) == 5:
        results.append(_accepted("cases", "five correctness cases observed"))
    else:
        results.append(_rejected("cases", f"expected 5 correctness cases, found {len(cases)}"))

    observed_kinds = tuple(case.case_kind for case in cases)
    if observed_kinds == REQUIRED_CASE_KINDS:
        results.append(_accepted("case_kinds", "case kinds match"))
    else:
        results.append(_rejected("case_kinds", "case kinds mismatch"))

    case_ids = [case.case_id for case in cases]
    duplicates = _duplicates(case_ids)
    if duplicates:
        results.append(
            _rejected("cases.case_id", "duplicate case ids: " + ", ".join(duplicates))
        )
    else:
        results.append(_accepted("cases.case_id", "case ids are unique"))

    for case in cases:
        support_subjects = tuple(case.required_dependency_subjects)
        finite_support_subjects = FINITE_SUPPORT_BY_CASE_KIND.get(case.case_kind, ())
        support_accepted = all(
            subject in accepted_support_subjects for subject in support_subjects
        )
        finite_support_accepted = all(
            subject in accepted_support_subjects for subject in finite_support_subjects
        )
        case_supports.append(
            SubstitutionGraphCorrectnessFrontierCaseSupport(
                case_id=case.case_id,
                case_kind=case.case_kind,
                correctness_target_id=case.correctness_target_id,
                status=case.status,
                support_subjects=support_subjects,
                finite_support_subjects=finite_support_subjects,
                support_accepted=support_accepted,
                finite_support_accepted=finite_support_accepted,
            )
        )
        results.extend(
            _validate_case_support(
                case,
                support_subjects,
                finite_support_subjects,
                support_accepted,
                finite_support_accepted,
            )
        )
    return case_supports, results


def _validate_case_support(
    case: Any,
    support_subjects: tuple[str, ...],
    finite_support_subjects: tuple[str, ...],
    support_accepted: bool,
    finite_support_accepted: bool,
) -> list[SubstitutionGraphCorrectnessFrontierStatusValidation]:
    results: list[SubstitutionGraphCorrectnessFrontierStatusValidation] = []
    prefix = case.case_id

    if case.status == "proof-case-open":
        results.append(_accepted(f"{prefix}.status", "correctness case remains open"))
    elif case.status in PROOF_PROMOTION_STATUSES:
        results.append(
            _rejected(
                f"{prefix}.status",
                "proof promotion status rejected: " + case.status,
            )
        )
    else:
        results.append(
            _rejected(f"{prefix}.status", "unsupported case status: " + case.status)
        )

    if case.correctness_target_id == "AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET":
        results.append(_accepted(f"{prefix}.target", "correctness target matches"))
    else:
        results.append(
            _rejected(f"{prefix}.target", "unknown correctness target")
        )

    expected_support_subjects = REQUIRED_DEPENDENCIES_BY_KIND.get(case.case_kind, ())
    if support_subjects == expected_support_subjects:
        results.append(_accepted(f"{prefix}.support", "support subjects match"))
    else:
        missing = [
            subject for subject in expected_support_subjects if subject not in support_subjects
        ]
        extra = [
            subject for subject in support_subjects if subject not in expected_support_subjects
        ]
        detail = []
        if missing:
            detail.append("missing support subjects: " + ", ".join(missing))
        if extra:
            detail.append("unexpected support subjects: " + ", ".join(extra))
        results.append(_rejected(f"{prefix}.support", "; ".join(detail) or "support mismatch"))

    if not finite_support_subjects:
        results.append(_rejected(f"{prefix}.finite_support", "no finite support mapping"))
    elif finite_support_accepted:
        results.append(_accepted(f"{prefix}.finite_support", "finite support accepted"))
    else:
        results.append(_rejected(f"{prefix}.finite_support", "finite support rejected"))

    if support_accepted:
        results.append(_accepted(f"{prefix}.support_accepted", "support accepted"))
    else:
        results.append(_rejected(f"{prefix}.support_accepted", "support rejected"))

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in case.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                f"{prefix}.non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted(f"{prefix}.non_claims", "non-claims are explicit"))
    return results


def _finite_support_subjects() -> frozenset[str]:
    subjects: set[str] = set()
    for values in FINITE_SUPPORT_BY_CASE_KIND.values():
        subjects.update(values)
    return frozenset(subjects)


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "substitution-graph-correctness-frontier-status"
    if subject == "non_claims":
        return "substitution-graph-correctness-frontier-non-claim"
    if subject.endswith(".status"):
        return "substitution-graph-correctness-frontier-case-status"
    if subject.endswith(".non_claims"):
        return "substitution-graph-correctness-frontier-case-non-claim"
    if (
        subject in REQUIRED_SUPPORT_SUBJECTS
        or subject in SUPPORT_PATH_FIELDS.values()
        or subject in {
            "cases_manifest",
            "support_surfaces",
            "substitution_graph_correctness_cases_path",
        }
    ):
        return "substitution-graph-correctness-frontier-support"
    if subject.endswith(".finite_support") or subject.endswith(".support_accepted"):
        return "substitution-graph-correctness-frontier-support"
    if subject.endswith(".support") or subject in {"cases", "case_kinds", "cases.case_id"}:
        return "substitution-graph-correctness-frontier-case-support"
    return "substitution-graph-correctness-frontier"


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
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _accepted(
    subject: str,
    detail: str,
) -> SubstitutionGraphCorrectnessFrontierStatusValidation:
    return SubstitutionGraphCorrectnessFrontierStatusValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphCorrectnessFrontierStatusValidation:
    return SubstitutionGraphCorrectnessFrontierStatusValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_correctness_frontier_status_cli())
