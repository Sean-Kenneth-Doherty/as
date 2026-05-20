"""Compact frontier status for formula-schema relation correctness support.

The formula-schema-relation module checks a finite support surface for the
substitution graph correctness stack. This module is only a handoff layer
around that surface: it finds the matching open proof case, runs the existing
support validator, and reports a compact blocked frontier without promoting
the case to a proof.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.substitution_graph_correctness_cases import (
    REQUIRED_DEPENDENCIES_BY_KIND,
    REQUIRED_NON_CLAIMS as CASE_NON_CLAIMS,
    load_substitution_graph_correctness_cases,
)
from autarkic_systems.substitution_graph_formula_schema_relation import (
    DEFAULT_WILLARD_MAP,
    REQUIRED_NON_CLAIMS as RELATION_NON_CLAIMS,
    load_substitution_graph_formula_schema_relation,
    validate_substitution_graph_formula_schema_relation,
)


DEFAULT_STATUS = Path(
    "claims/substitution_graph_formula_schema_relation_frontier_status.json"
)

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "formula-schema-relation"
REQUIRED_CASE_KIND = "formula-schema-relation"
REQUIRED_CASE_ID = "AS-SUBST-GRAPH-CORRECTNESS-FORMULA-SCHEMA-RELATION"
REQUIRED_CORRECTNESS_TARGET_ID = "AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET"
REQUIRED_SUPPORT_SUBJECTS = ("formula_schema_relation",)
REQUIRED_CASE_SUPPORT_SUBJECTS = REQUIRED_DEPENDENCIES_BY_KIND[
    REQUIRED_CASE_KIND
]
REQUIRED_STATUS_SET_ID = (
    "as-substitution-graph-formula-schema-relation-frontier-status-v1"
)
REQUIRED_RELATION_SET_ID = "as-substitution-graph-formula-schema-relation-v1"
REQUIRED_NON_CLAIMS = (
    "no formula correctness proof",
    "no substitution representability proof",
    "no diagonal lemma proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
PROOF_PROMOTION_STATUSES = {
    "formula-schema-relation-proved",
    "formula-correctness-proved",
    "substitution-representability-proved",
    "substitution-graph-correctness-proved",
    "diagonal-lemma-proved",
    "fixed-point-equation-proved",
    "arithmetized-proof-predicate-proved",
    "self-consistency-proved",
    "self-consistency-theorem-proved",
}
PROOF_PROMOTION_NON_CLAIMS = {
    "formula correctness proof",
    "substitution representability proof",
    "diagonal lemma proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "self-consistency theorem",
}
EXPECTED_CASES_PATH = "claims/substitution_graph_correctness_cases.json"
EXPECTED_RELATION_PATH = "claims/substitution_graph_formula_schema_relation.json"
EXPECTED_CASE_PATHS = {
    "correctness_targets_path": "claims/substitution_graph_correctness_targets.json",
    "formula_candidates_path": "claims/substitution_graph_formula_candidates.json",
    "formula_schema_relation_path": EXPECTED_RELATION_PATH,
}
EXPECTED_RELATION_PATHS = {
    "formal_language_path": "language/formal_arithmetic_language.json",
    "codebook_path": "language/formal_codebook.json",
    "substitution_graph_targets_path": "claims/substitution_graph_targets.json",
    "formula_candidates_path": "claims/substitution_graph_formula_candidates.json",
    "evaluation_examples_path": "claims/substitution_graph_evaluation_examples.json",
    "substitution_representability_targets_path": (
        "claims/substitution_representability_targets.json"
    ),
}
EXPECTED_RELATION_POINT_COUNT = 4


@dataclass(frozen=True)
class SubstitutionGraphFormulaSchemaRelationFrontierStatusManifest:
    """Loaded manifest for the compact formula-schema-relation frontier."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    substitution_graph_correctness_cases_path: str
    formula_schema_relation_path: str
    expected_support_surface_count: int
    expected_relation_point_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphFormulaSchemaRelationFrontierValidation:
    """One validation result for the compact frontier status."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphFormulaSchemaRelationFrontierCase:
    """Observed correctness proof case for formula-schema relation."""

    case_id: str
    case_kind: str
    correctness_target_id: str
    status: str
    support_subjects: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphFormulaSchemaRelationFrontierSupportSurface:
    """Observed finite support surface behind the open proof case."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    facts: dict[str, Any]
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphFormulaSchemaRelationFrontierStatusReport:
    """Compact validation report for formula-schema-relation handoff."""

    manifest: SubstitutionGraphFormulaSchemaRelationFrontierStatusManifest
    substitution_graph_correctness_cases_path: Path
    formula_schema_relation_path: Path
    case: SubstitutionGraphFormulaSchemaRelationFrontierCase | None
    support_surfaces: tuple[
        SubstitutionGraphFormulaSchemaRelationFrontierSupportSurface,
        ...,
    ]
    results: tuple[SubstitutionGraphFormulaSchemaRelationFrontierValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every compact status validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def frontier_status(self) -> str:
        """Return the preserved frontier status."""

        return self.manifest.frontier_status

    @property
    def frontier_blocked_by(self) -> str:
        """Return the preserved frontier blocker."""

        return self.manifest.frontier_blocked_by

    @property
    def support_surface_count(self) -> int:
        """Return the number of compact support surfaces observed."""

        return len(self.support_surfaces)

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return stable failure subjects for status automation."""

        subjects: list[str] = []
        for result in self.results:
            if result.accepted:
                continue
            subject = _failed_subject_for_result(result.subject)
            if subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)


def load_substitution_graph_formula_schema_relation_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> SubstitutionGraphFormulaSchemaRelationFrontierStatusManifest:
    """Load the formula-schema-relation frontier status manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return SubstitutionGraphFormulaSchemaRelationFrontierStatusManifest(
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
        formula_schema_relation_path=_required_text(
            data,
            "formula_schema_relation_path",
        ),
        expected_support_surface_count=_required_int(
            data,
            "expected_support_surface_count",
        ),
        expected_relation_point_count=_required_int(
            data,
            "expected_relation_point_count",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_formula_schema_relation_frontier_status(
    manifest: SubstitutionGraphFormulaSchemaRelationFrontierStatusManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphFormulaSchemaRelationFrontierStatusReport:
    """Validate the compact handoff without changing the underlying case map."""

    results: list[SubstitutionGraphFormulaSchemaRelationFrontierValidation] = [
        _accepted("manifest", f"loaded {manifest.status_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    cases_path = Path(manifest.substitution_graph_correctness_cases_path)
    relation_path = Path(manifest.formula_schema_relation_path)
    cases_manifest = None
    try:
        cases_manifest = load_substitution_graph_correctness_cases(cases_path)
        results.append(_accepted("cases_manifest", "case manifest loaded"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        results.append(
            _rejected(
                "cases_manifest",
                f"case manifest missing or invalid: {exc}",
            )
        )

    case = None
    support_surfaces: list[
        SubstitutionGraphFormulaSchemaRelationFrontierSupportSurface
    ] = []
    if cases_manifest is None:
        results.append(_rejected("case", "formula-schema-relation case unavailable"))
    else:
        results.extend(_validate_case_manifest_paths(cases_manifest))
        case, case_results = _case_summary(cases_manifest.cases)
        results.extend(case_results)
        support_surfaces.append(
            _formula_schema_relation_support_surface(
                relation_path,
                Path(willard_map_path),
            )
        )
        results.extend(_validate_support_surfaces(manifest, support_surfaces))

    return SubstitutionGraphFormulaSchemaRelationFrontierStatusReport(
        manifest=manifest,
        substitution_graph_correctness_cases_path=cases_path,
        formula_schema_relation_path=relation_path,
        case=case,
        support_surfaces=tuple(support_surfaces),
        results=tuple(results),
    )


def substitution_graph_formula_schema_relation_frontier_status_payload(
    report: SubstitutionGraphFormulaSchemaRelationFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready formula-schema-relation status payload."""

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
        "formula_schema_relation_path": str(report.formula_schema_relation_path),
        "expected_support_surface_count": (
            report.manifest.expected_support_surface_count
        ),
        "expected_relation_point_count": (
            report.manifest.expected_relation_point_count
        ),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "case": _case_payload(report.case),
        "support_surface_count": report.support_surface_count,
        "failed_subjects": list(report.failed_subjects),
        "support_surfaces": [
            _support_surface_payload(surface)
            for surface in report.support_surfaces
        ],
        "support_facts": {
            surface.subject: _json_ready_facts(surface.facts)
            for surface in report.support_surfaces
        },
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


def format_substitution_graph_formula_schema_relation_frontier_status_report(
    report: SubstitutionGraphFormulaSchemaRelationFrontierStatusReport,
) -> str:
    """Format a concise human-readable formula-schema-relation status."""

    status = "accepted" if report.accepted else "rejected"
    relation_points = "unknown"
    for surface in report.support_surfaces:
        if surface.subject == "formula_schema_relation":
            relation_points = str(surface.facts.get("relation_point_count", "unknown"))
            break
    lines = [
        f"Substitution graph formula-schema-relation frontier status: {status}",
        f"Status set: {report.manifest.status_set_id}",
        f"Frontier status: {report.frontier_status}",
        f"Blocked by: {report.frontier_blocked_by}",
        f"Support surfaces: {report.support_surface_count}",
        f"Relation points: {relation_points}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    if report.case is None:
        lines.append("Case: none")
    else:
        lines.extend([
            f"Case: {report.case.case_id}",
            f"Case kind: {report.case.case_kind}",
            f"Case status: {report.case.status}",
            "Case support: " + _joined_or_none(report.case.support_subjects),
        ])
    lines.append("Support:")
    for surface in report.support_surfaces:
        prefix = "accepted" if surface.accepted else "rejected"
        detail = surface.detail
        if surface.subject == "formula_schema_relation":
            source_counts = surface.facts.get("source_kind_counts", {})
            detail = (
                f"{detail}; relation points "
                f"{surface.facts.get('relation_point_count', 'unknown')}; "
                f"source kinds {_format_source_counts(source_counts)}"
            )
        lines.append(f"- {surface.subject}: {prefix} ({detail})")
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_formula_schema_relation_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run formula-schema-relation frontier status validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "substitution_graph_formula_schema_relation_frontier_status"
        ),
        description=(
            "Validate the AS substitution graph formula-schema-relation "
            "frontier."
        ),
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the formula-schema-relation frontier status manifest.",
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

    manifest = load_substitution_graph_formula_schema_relation_frontier_status(
        args.status
    )
    report = validate_substitution_graph_formula_schema_relation_frontier_status(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                substitution_graph_formula_schema_relation_frontier_status_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            format_substitution_graph_formula_schema_relation_frontier_status_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _validate_manifest(
    manifest: SubstitutionGraphFormulaSchemaRelationFrontierStatusManifest,
) -> list[SubstitutionGraphFormulaSchemaRelationFrontierValidation]:
    results: list[SubstitutionGraphFormulaSchemaRelationFrontierValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.status_set_id == REQUIRED_STATUS_SET_ID:
        results.append(_accepted("status_set_id", "status set id matches"))
    else:
        results.append(_rejected("status_set_id", "unexpected status set id"))

    if manifest.frontier_status == REQUIRED_FRONTIER_STATUS:
        results.append(_accepted("frontier_status", "frontier remains blocked"))
    elif manifest.frontier_status in PROOF_PROMOTION_STATUSES:
        results.append(
            _rejected(
                "frontier_status",
                "proof-promotion frontier status: " + manifest.frontier_status,
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
        results.append(_accepted("frontier_blocked_by", "blocker preserved"))
    else:
        results.append(
            _rejected(
                "frontier_blocked_by",
                f"expected {REQUIRED_FRONTIER_BLOCKER} blocker",
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

    if manifest.formula_schema_relation_path == EXPECTED_RELATION_PATH:
        results.append(
            _accepted(
                "formula_schema_relation_path",
                f"{EXPECTED_RELATION_PATH} referenced",
            )
        )
    else:
        results.append(
            _rejected(
                "formula_schema_relation_path",
                (
                    f"expected {EXPECTED_RELATION_PATH} but found "
                    f"{manifest.formula_schema_relation_path}"
                ),
            )
        )

    if manifest.expected_support_surface_count == len(REQUIRED_SUPPORT_SUBJECTS):
        results.append(_accepted("expected_support_surface_count", "one support surface"))
    else:
        results.append(
            _rejected(
                "expected_support_surface_count",
                "expected one support surface",
            )
        )

    if manifest.expected_relation_point_count == EXPECTED_RELATION_POINT_COUNT:
        results.append(_accepted("expected_relation_point_count", "four points"))
    else:
        results.append(
            _rejected(
                "expected_relation_point_count",
                "expected four relation points",
            )
        )

    missing_non_claims = _missing_items(REQUIRED_NON_CLAIMS, manifest.non_claims)
    proof_promotions = [
        item for item in manifest.non_claims if item in PROOF_PROMOTION_NON_CLAIMS
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    elif proof_promotions:
        results.append(
            _rejected(
                "non_claims",
                "proof-promotion non-claims: " + ", ".join(proof_promotions),
            )
        )
    else:
        results.append(_accepted("non_claims", "status non-claims are explicit"))

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))
    return results


def _validate_case_manifest_paths(
    manifest: Any,
) -> list[SubstitutionGraphFormulaSchemaRelationFrontierValidation]:
    results: list[SubstitutionGraphFormulaSchemaRelationFrontierValidation] = []
    if manifest.case_set_id == "as-substitution-graph-correctness-cases-v1":
        results.append(_accepted("case_set_id", "case set id matches"))
    else:
        results.append(_rejected("case_set_id", "unexpected case set id"))

    if len(tuple(manifest.cases)) == 5:
        results.append(_accepted("case_count", "five correctness cases present"))
    else:
        results.append(_rejected("case_count", "expected five correctness cases"))

    for field, expected in EXPECTED_CASE_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))
    return results


def _case_summary(
    cases: tuple[Any, ...],
) -> tuple[
    SubstitutionGraphFormulaSchemaRelationFrontierCase | None,
    list[SubstitutionGraphFormulaSchemaRelationFrontierValidation],
]:
    results: list[SubstitutionGraphFormulaSchemaRelationFrontierValidation] = []
    matches = [case for case in cases if case.case_kind == REQUIRED_CASE_KIND]
    if len(matches) != 1:
        results.append(
            _rejected(
                "case",
                f"expected one {REQUIRED_CASE_KIND} case, found {len(matches)}",
            )
        )
        return None, results

    raw_case = matches[0]
    case = SubstitutionGraphFormulaSchemaRelationFrontierCase(
        case_id=raw_case.case_id,
        case_kind=raw_case.case_kind,
        correctness_target_id=raw_case.correctness_target_id,
        status=raw_case.status,
        support_subjects=tuple(raw_case.required_dependency_subjects),
        non_claims=tuple(raw_case.non_claims),
        next_as_action=raw_case.next_as_action,
    )
    results.append(_accepted("case", "formula-schema-relation case found"))
    results.extend(_validate_case(case))
    return case, results


def _validate_case(
    case: SubstitutionGraphFormulaSchemaRelationFrontierCase,
) -> list[SubstitutionGraphFormulaSchemaRelationFrontierValidation]:
    results: list[SubstitutionGraphFormulaSchemaRelationFrontierValidation] = []
    if case.case_id == REQUIRED_CASE_ID:
        results.append(_accepted("case.case_id", "case id matches"))
    else:
        results.append(_rejected("case.case_id", "unexpected case id"))

    if case.status == "proof-case-open":
        results.append(_accepted("case.status", "case remains open"))
    elif case.status in PROOF_PROMOTION_STATUSES:
        results.append(
            _rejected(
                "case.status",
                "case is not open: proof-promotion status " + case.status,
            )
        )
    else:
        results.append(_rejected("case.status", "case is not open: " + case.status))

    if case.correctness_target_id == REQUIRED_CORRECTNESS_TARGET_ID:
        results.append(_accepted("case.target", "correctness target matches"))
    else:
        results.append(_rejected("case.target", "unknown correctness target"))

    if case.support_subjects == REQUIRED_CASE_SUPPORT_SUBJECTS:
        results.append(_accepted("case.support", "support subjects match"))
    else:
        results.append(
            _rejected(
                "case.support",
                "support subjects mismatch: expected "
                + ", ".join(REQUIRED_CASE_SUPPORT_SUBJECTS)
                + " but found "
                + _joined_or_none(case.support_subjects),
            )
        )

    missing_case_non_claims = _missing_items(CASE_NON_CLAIMS, case.non_claims)
    if missing_case_non_claims:
        results.append(
            _rejected(
                "case.non_claims",
                "missing case non-claims: " + ", ".join(missing_case_non_claims),
            )
        )
    else:
        results.append(_accepted("case.non_claims", "case non-claims explicit"))

    if case.next_as_action.strip():
        results.append(_accepted("case.next_as_action", "case next action present"))
    else:
        results.append(_rejected("case.next_as_action", "missing case next action"))
    return results


def _formula_schema_relation_support_surface(
    relation_path: Path,
    willard_map_path: Path,
) -> SubstitutionGraphFormulaSchemaRelationFrontierSupportSurface:
    try:
        relation = load_substitution_graph_formula_schema_relation(relation_path)
        report = validate_substitution_graph_formula_schema_relation(
            relation,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return SubstitutionGraphFormulaSchemaRelationFrontierSupportSurface(
            subject="formula_schema_relation",
            path=relation_path,
            accepted=False,
            failed_subjects=(
                "substitution-graph-formula-schema-relation-load",
            ),
            facts={},
            detail=f"formula-schema relation missing or invalid: {exc}",
        )

    failures = list(report.failed_subjects)
    path_failures = _relation_path_failures(relation)
    failures.extend(path_failures)
    if relation.relation_set_id != REQUIRED_RELATION_SET_ID:
        failures.append("substitution-graph-formula-schema-relation-id")
    if report.relation_point_count != EXPECTED_RELATION_POINT_COUNT:
        failures.append("substitution-graph-formula-schema-relation-count")
    if relation.expected_relation_point_count != EXPECTED_RELATION_POINT_COUNT:
        failures.append("substitution-graph-formula-schema-relation-expected-count")
    if _missing_items(RELATION_NON_CLAIMS, relation.non_claims):
        failures.append("substitution-graph-formula-schema-relation-non-claim")

    accepted = report.accepted and not failures
    detail = "formula-schema relation accepted"
    if not accepted:
        detail = "formula-schema relation rejected: " + _joined_or_none(tuple(failures))
    return SubstitutionGraphFormulaSchemaRelationFrontierSupportSurface(
        subject="formula_schema_relation",
        path=relation_path,
        accepted=accepted,
        failed_subjects=tuple(failures),
        facts={
            "relation_set_id": relation.relation_set_id,
            "relation_point_count": report.relation_point_count,
            "expected_relation_point_count": relation.expected_relation_point_count,
            "source_kind_counts": report.source_kind_counts,
            "failed_subjects": list(report.failed_subjects),
            "non_claim_count": len(relation.non_claims),
            "support_paths": {
                key: getattr(relation, key) for key in EXPECTED_RELATION_PATHS
            },
        },
        detail=detail,
    )


def _relation_path_failures(relation: Any) -> list[str]:
    failures: list[str] = []
    for field, expected in EXPECTED_RELATION_PATHS.items():
        if getattr(relation, field) != expected:
            failures.append(
                "substitution-graph-formula-schema-relation-" + field
            )
    return failures


def _validate_support_surfaces(
    manifest: SubstitutionGraphFormulaSchemaRelationFrontierStatusManifest,
    surfaces: list[SubstitutionGraphFormulaSchemaRelationFrontierSupportSurface],
) -> list[SubstitutionGraphFormulaSchemaRelationFrontierValidation]:
    results: list[SubstitutionGraphFormulaSchemaRelationFrontierValidation] = []
    subjects = tuple(surface.subject for surface in surfaces)
    if len(surfaces) == manifest.expected_support_surface_count:
        results.append(_accepted("support_surface_count", "support count matches"))
    else:
        results.append(
            _rejected(
                "support_surface_count",
                (
                    "expected "
                    + str(manifest.expected_support_surface_count)
                    + " support surface(s)"
                ),
            )
        )

    if subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(_accepted("support_subjects", "support subjects match"))
    else:
        results.append(
            _rejected(
                "support_subjects",
                "expected "
                + ", ".join(REQUIRED_SUPPORT_SUBJECTS)
                + " but found "
                + _joined_or_none(subjects),
            )
        )

    for surface in surfaces:
        if surface.accepted:
            results.append(
                _accepted(
                    f"support.{surface.subject}",
                    surface.detail,
                )
            )
        else:
            results.append(
                _rejected(
                    f"support.{surface.subject}",
                    surface.detail,
                )
            )
    return results


def _case_payload(
    case: SubstitutionGraphFormulaSchemaRelationFrontierCase | None,
) -> dict[str, Any] | None:
    if case is None:
        return None
    return {
        "case_id": case.case_id,
        "case_kind": case.case_kind,
        "correctness_target_id": case.correctness_target_id,
        "status": case.status,
        "support_subjects": list(case.support_subjects),
        "non_claims": list(case.non_claims),
        "next_as_action": case.next_as_action,
    }


def _support_surface_payload(
    surface: SubstitutionGraphFormulaSchemaRelationFrontierSupportSurface,
) -> dict[str, Any]:
    return {
        "subject": surface.subject,
        "path": str(surface.path),
        "accepted": surface.accepted,
        "failed_subjects": list(surface.failed_subjects),
        "facts": _json_ready_facts(surface.facts),
        "detail": surface.detail,
    }


def _json_ready_facts(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready_facts(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_ready_facts(item) for item in value]
    if isinstance(value, list):
        return [_json_ready_facts(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def _format_source_counts(counts: Any) -> str:
    if not isinstance(counts, dict) or not counts:
        return "none"
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def _accepted(
    subject: str,
    detail: str,
) -> SubstitutionGraphFormulaSchemaRelationFrontierValidation:
    return SubstitutionGraphFormulaSchemaRelationFrontierValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphFormulaSchemaRelationFrontierValidation:
    return SubstitutionGraphFormulaSchemaRelationFrontierValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "substitution-graph-formula-schema-relation-frontier-status"
    if subject == "non_claims":
        return "substitution-graph-formula-schema-relation-frontier-non-claim"
    if subject == "case.status":
        return "substitution-graph-formula-schema-relation-frontier-case-status"
    if subject == "case.support":
        return "substitution-graph-formula-schema-relation-frontier-case-support"
    if subject.startswith("case."):
        return "substitution-graph-formula-schema-relation-frontier-case"
    if subject in {
        "formula_schema_relation_path",
        "substitution_graph_correctness_cases_path",
    } or subject.endswith("_path"):
        return "substitution-graph-formula-schema-relation-frontier-dependency"
    if subject in {"support_surface_count", "support_subjects"}:
        return "substitution-graph-formula-schema-relation-frontier-support"
    if subject.startswith("support."):
        return "substitution-graph-formula-schema-relation-frontier-support"
    if subject in {"cases_manifest", "case", "case_set_id", "case_count"}:
        return "substitution-graph-formula-schema-relation-frontier-case"
    return "substitution-graph-formula-schema-relation-frontier"


def _missing_items(required: tuple[str, ...], observed: tuple[str, ...]) -> list[str]:
    return [item for item in required if item not in observed]


def _joined_or_none(items: tuple[str, ...] | list[str]) -> str:
    return ", ".join(items) if items else "none"


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{key} must contain non-empty strings")
        result.append(item)
    return result


if __name__ == "__main__":
    raise SystemExit(
        run_substitution_graph_formula_schema_relation_frontier_status_cli()
    )
