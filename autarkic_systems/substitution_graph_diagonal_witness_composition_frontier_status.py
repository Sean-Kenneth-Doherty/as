"""Compact frontier status for diagonal-witness composition support.

The finite diagonal-witness-composition module checks one concrete
self-application route. This module is a deliberately smaller handoff layer:
it confirms that the matching substitution graph correctness case remains
open, that the finite support surface still accepts, and that neither artifact
is being promoted to a formula-correctness, representability, diagonal-lemma,
fixed-point, proof-predicate, or self-consistency theorem.
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
from autarkic_systems.substitution_graph_diagonal_witness_composition import (
    DEFAULT_WILLARD_MAP,
    REQUIRED_NON_CLAIMS as COMPOSITION_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_substitution_graph_diagonal_witness_composition,
    validate_substitution_graph_diagonal_witness_composition,
)


DEFAULT_STATUS = Path(
    "claims/substitution_graph_diagonal_witness_composition_frontier_status.json"
)

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "diagonal-witness-composition"
REQUIRED_CASE_KIND = "diagonal-witness-composition"
REQUIRED_CASE_ID = "AS-SUBST-GRAPH-CORRECTNESS-DIAGONAL-WITNESS-COMPOSITION"
REQUIRED_CASE_STATUS = "proof-case-open"
REQUIRED_CORRECTNESS_TARGET_ID = "AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET"
REQUIRED_SUPPORT_SUBJECTS = (
    "substitution_graph_correctness_cases",
    "diagonal_witness_composition",
)
REQUIRED_CASE_SUPPORT_SUBJECTS = REQUIRED_DEPENDENCIES_BY_KIND[
    REQUIRED_CASE_KIND
]
REQUIRED_STATUS_SET_ID = (
    "as-substitution-graph-diagonal-witness-composition-frontier-status-v1"
)
REQUIRED_COMPOSITION_SET_ID = (
    "as-substitution-graph-diagonal-witness-composition-v1"
)
EXPECTED_COMPOSITION_COUNT = 1
REQUIRED_NON_CLAIMS = (
    "no formula correctness proof",
    "no substitution representability proof",
    "no diagonal lemma proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
PROOF_PROMOTION_STATUSES = {
    "formula-correctness-proved",
    "substitution-representability-proved",
    "diagonal-lemma-proved",
    "fixed-point-equation-proved",
    "arithmetized-proof-predicate-proved",
    "diagonal-witness-composition-proved",
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
EXPECTED_DEPENDENCY_PATHS = {
    "substitution_graph_correctness_cases_path": (
        "claims/substitution_graph_correctness_cases.json"
    ),
    "diagonal_witness_composition_path": (
        "claims/substitution_graph_diagonal_witness_composition.json"
    ),
    "formal_language_path": "language/formal_arithmetic_language.json",
    "codebook_path": "language/formal_codebook.json",
    "correctness_targets_path": (
        "claims/substitution_graph_correctness_targets.json"
    ),
    "formula_candidates_path": "claims/substitution_graph_formula_candidates.json",
    "formula_schema_relation_path": (
        "claims/substitution_graph_formula_schema_relation.json"
    ),
    "substitution_representability_targets_path": (
        "claims/substitution_representability_targets.json"
    ),
    "diagonal_construction_targets_path": (
        "claims/diagonal_construction_targets.json"
    ),
    "fixed_point_targets_path": "claims/fixed_point_targets.json",
}


@dataclass(frozen=True)
class SubstitutionGraphDiagonalWitnessCompositionFrontierStatusManifest:
    """Loaded manifest for the compact diagonal-witness frontier."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    substitution_graph_correctness_cases_path: str
    diagonal_witness_composition_path: str
    formal_language_path: str
    codebook_path: str
    correctness_targets_path: str
    formula_candidates_path: str
    formula_schema_relation_path: str
    substitution_representability_targets_path: str
    diagonal_construction_targets_path: str
    fixed_point_targets_path: str
    required_case_kind: str
    required_case_status: str
    expected_support_surface_count: int
    expected_composition_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphDiagonalWitnessCompositionFrontierValidation:
    """One validation result for the compact frontier status."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphDiagonalWitnessCompositionFrontierProofCase:
    """Compact view of the matching correctness proof case."""

    case_id: str
    case_kind: str
    correctness_target_id: str
    status: str
    required_dependency_subjects: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphDiagonalWitnessCompositionFrontierSupportSurface:
    """Observed support surface used by this compact handoff."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    facts: dict[str, Any]
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphDiagonalWitnessCompositionFrontierStatusReport:
    """Validation report for the compact diagonal-witness frontier."""

    manifest: SubstitutionGraphDiagonalWitnessCompositionFrontierStatusManifest
    substitution_graph_correctness_cases_path: Path
    diagonal_witness_composition_path: Path
    formal_language_path: Path
    codebook_path: Path
    correctness_targets_path: Path
    formula_candidates_path: Path
    formula_schema_relation_path: Path
    substitution_representability_targets_path: Path
    diagonal_construction_targets_path: Path
    fixed_point_targets_path: Path
    proof_case: SubstitutionGraphDiagonalWitnessCompositionFrontierProofCase
    support_surfaces: tuple[
        SubstitutionGraphDiagonalWitnessCompositionFrontierSupportSurface,
        ...
    ]
    support_facts: dict[str, dict[str, Any]]
    results: tuple[SubstitutionGraphDiagonalWitnessCompositionFrontierValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every compact frontier validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def frontier_status(self) -> str:
        """Return the frontier status preserved by this handoff."""

        return self.manifest.frontier_status

    @property
    def frontier_blocked_by(self) -> str:
        """Return the still-open proof case that blocks this frontier."""

        return self.manifest.frontier_blocked_by

    @property
    def support_surface_count(self) -> int:
        """Return the number of compact support surfaces inspected."""

        return len(self.support_surfaces)

    @property
    def composition_count(self) -> int:
        """Return the observed finite composition count, if available."""

        return int(
            self.support_facts
            .get("diagonal_witness_composition", {})
            .get("composition_count", 0)
        )

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return stable failure subjects for automation and reports."""

        subjects: list[str] = []
        for result in self.results:
            if result.accepted:
                continue
            subject = _failed_subject_for_result(result.subject)
            if subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)


@dataclass(frozen=True)
class _SupportLoad:
    """Small fail-closed load summary for support manifests."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    facts: dict[str, Any]


def load_substitution_graph_diagonal_witness_composition_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> SubstitutionGraphDiagonalWitnessCompositionFrontierStatusManifest:
    """Load the diagonal-witness-composition frontier status manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return SubstitutionGraphDiagonalWitnessCompositionFrontierStatusManifest(
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
        diagonal_witness_composition_path=_required_text(
            data,
            "diagonal_witness_composition_path",
        ),
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
        required_case_kind=_required_text(data, "required_case_kind"),
        required_case_status=_required_text(data, "required_case_status"),
        expected_support_surface_count=_required_int(
            data,
            "expected_support_surface_count",
        ),
        expected_composition_count=_required_int(
            data,
            "expected_composition_count",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_diagonal_witness_composition_frontier_status(
    manifest: SubstitutionGraphDiagonalWitnessCompositionFrontierStatusManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphDiagonalWitnessCompositionFrontierStatusReport:
    """Validate the compact handoff without promoting the proof case."""

    paths = _manifest_paths(manifest)
    results: list[
        SubstitutionGraphDiagonalWitnessCompositionFrontierValidation
    ] = [_accepted("manifest", f"loaded {manifest.status_set_id}")]
    results.extend(_validate_manifest(manifest))

    cases_manifest, cases_load = _load_correctness_cases(
        paths["substitution_graph_correctness_cases_path"]
    )
    composition_manifest, composition_load = _load_diagonal_composition(
        paths["diagonal_witness_composition_path"],
        Path(willard_map_path),
    )

    proof_case = _find_diagonal_witness_case(cases_manifest)
    results.extend(_validate_case_manifest_paths(cases_manifest))
    results.extend(_validate_proof_case(proof_case))
    results.extend(
        _validate_support_path_alignment(
            manifest,
            cases_manifest,
            composition_manifest,
        )
    )

    support_loads = {
        "substitution_graph_correctness_cases": cases_load,
        "diagonal_witness_composition": composition_load,
    }
    support_surfaces = _support_surfaces(paths, support_loads)
    results.extend(_validate_support_surfaces(manifest, support_surfaces))

    return SubstitutionGraphDiagonalWitnessCompositionFrontierStatusReport(
        manifest=manifest,
        substitution_graph_correctness_cases_path=paths[
            "substitution_graph_correctness_cases_path"
        ],
        diagonal_witness_composition_path=paths[
            "diagonal_witness_composition_path"
        ],
        formal_language_path=paths["formal_language_path"],
        codebook_path=paths["codebook_path"],
        correctness_targets_path=paths["correctness_targets_path"],
        formula_candidates_path=paths["formula_candidates_path"],
        formula_schema_relation_path=paths["formula_schema_relation_path"],
        substitution_representability_targets_path=paths[
            "substitution_representability_targets_path"
        ],
        diagonal_construction_targets_path=paths[
            "diagonal_construction_targets_path"
        ],
        fixed_point_targets_path=paths["fixed_point_targets_path"],
        proof_case=proof_case,
        support_surfaces=tuple(support_surfaces),
        support_facts={
            subject: dict(load.facts) for subject, load in support_loads.items()
        },
        results=tuple(results),
    )


def substitution_graph_diagonal_witness_composition_frontier_status_payload(
    report: SubstitutionGraphDiagonalWitnessCompositionFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready diagonal-witness frontier payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "status_manifest": str(report.manifest.path),
        "status_set_id": report.manifest.status_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "frontier_status": report.frontier_status,
        "frontier_blocked_by": report.frontier_blocked_by,
        "support_paths": {
            "substitution_graph_correctness_cases": str(
                report.substitution_graph_correctness_cases_path
            ),
            "diagonal_witness_composition": str(
                report.diagonal_witness_composition_path
            ),
            "formal_language": str(report.formal_language_path),
            "codebook": str(report.codebook_path),
            "correctness_targets": str(report.correctness_targets_path),
            "formula_candidates": str(report.formula_candidates_path),
            "formula_schema_relation": str(report.formula_schema_relation_path),
            "substitution_representability_targets": str(
                report.substitution_representability_targets_path
            ),
            "diagonal_construction_targets": str(
                report.diagonal_construction_targets_path
            ),
            "fixed_point_targets": str(report.fixed_point_targets_path),
        },
        "proof_case": {
            "case_id": report.proof_case.case_id,
            "case_kind": report.proof_case.case_kind,
            "correctness_target_id": report.proof_case.correctness_target_id,
            "status": report.proof_case.status,
            "required_dependency_subjects": list(
                report.proof_case.required_dependency_subjects
            ),
            "non_claims": list(report.proof_case.non_claims),
            "next_as_action": report.proof_case.next_as_action,
        },
        "expected_support_surface_count": (
            report.manifest.expected_support_surface_count
        ),
        "expected_composition_count": report.manifest.expected_composition_count,
        "composition_count": report.composition_count,
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "support_surface_count": report.support_surface_count,
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
        "support_facts": _json_ready_facts(report.support_facts),
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


def format_substitution_graph_diagonal_witness_composition_frontier_status_report(
    report: SubstitutionGraphDiagonalWitnessCompositionFrontierStatusReport,
) -> str:
    """Format a concise human-readable diagonal-witness frontier report."""

    status = "accepted" if report.accepted else "rejected"
    case = report.proof_case
    lines = [
        (
            "Substitution graph diagonal-witness-composition frontier "
            f"status: {status}"
        ),
        f"Status set: {report.manifest.status_set_id}",
        f"Frontier status: {report.frontier_status}",
        f"Blocked by: {report.frontier_blocked_by}",
        f"Proof case: {case.case_id}",
        f"Case kind: {case.case_kind}",
        f"Case status: {case.status}",
        f"Compositions: {report.composition_count}",
        f"Support surfaces: {report.support_surface_count}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Support:")
    for surface in report.support_surfaces:
        prefix = "accepted" if surface.accepted else "rejected"
        detail = surface.detail
        if surface.subject == "diagonal_witness_composition":
            count = surface.facts.get("composition_count", "unknown")
            detail = f"{detail}; compositions {count}"
        lines.append(f"- {surface.subject}: {prefix} ({surface.path}) {detail}")
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_diagonal_witness_composition_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run diagonal-witness-composition frontier status validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "substitution_graph_diagonal_witness_composition_frontier_status"
        ),
        description=(
            "Validate the AS substitution graph diagonal-witness-composition "
            "frontier status."
        ),
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the diagonal-witness frontier status manifest.",
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

    manifest = load_substitution_graph_diagonal_witness_composition_frontier_status(
        args.status
    )
    report = validate_substitution_graph_diagonal_witness_composition_frontier_status(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(
            substitution_graph_diagonal_witness_composition_frontier_status_payload(
                report
            ),
            sort_keys=True,
        ))
    else:
        print(
            format_substitution_graph_diagonal_witness_composition_frontier_status_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: SubstitutionGraphDiagonalWitnessCompositionFrontierStatusManifest,
) -> dict[str, Path]:
    return {
        "substitution_graph_correctness_cases_path": Path(
            manifest.substitution_graph_correctness_cases_path
        ),
        "diagonal_witness_composition_path": Path(
            manifest.diagonal_witness_composition_path
        ),
        "formal_language_path": Path(manifest.formal_language_path),
        "codebook_path": Path(manifest.codebook_path),
        "correctness_targets_path": Path(manifest.correctness_targets_path),
        "formula_candidates_path": Path(manifest.formula_candidates_path),
        "formula_schema_relation_path": Path(manifest.formula_schema_relation_path),
        "substitution_representability_targets_path": Path(
            manifest.substitution_representability_targets_path
        ),
        "diagonal_construction_targets_path": Path(
            manifest.diagonal_construction_targets_path
        ),
        "fixed_point_targets_path": Path(manifest.fixed_point_targets_path),
    }


def _load_correctness_cases(path: Path) -> tuple[Any | None, _SupportLoad]:
    try:
        loaded = load_substitution_graph_correctness_cases(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None, _SupportLoad(
            accepted=False,
            failed_subjects=(
                "substitution-graph-correctness-cases-load",
            ),
            facts={},
        )

    failures: list[str] = []
    cases = tuple(getattr(loaded, "cases", ()))
    if getattr(loaded, "case_set_id", None) != (
        "as-substitution-graph-correctness-cases-v1"
    ):
        failures.append("substitution-graph-correctness-cases-id")
    if len(cases) != 5:
        failures.append("substitution-graph-correctness-cases-count")
    proof_case = _find_diagonal_witness_case(loaded)
    if proof_case.case_kind != REQUIRED_CASE_KIND:
        failures.append(
            "substitution-graph-diagonal-witness-composition-case-missing"
        )

    return loaded, _SupportLoad(
        accepted=not failures,
        failed_subjects=tuple(failures),
        facts={
            "case_set_id": getattr(loaded, "case_set_id", ""),
            "case_count": len(cases),
            "diagonal_witness_composition_case_status": proof_case.status,
        },
    )


def _load_diagonal_composition(
    path: Path,
    willard_map_path: Path,
) -> tuple[Any | None, _SupportLoad]:
    try:
        loaded = load_substitution_graph_diagonal_witness_composition(path)
        report = validate_substitution_graph_diagonal_witness_composition(
            loaded,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return None, _SupportLoad(
            accepted=False,
            failed_subjects=(
                "substitution-graph-diagonal-witness-composition-load",
            ),
            facts={},
        )

    failures = list(report.failed_subjects)
    if loaded.composition_set_id != REQUIRED_COMPOSITION_SET_ID:
        failures.append("substitution-graph-diagonal-witness-composition-id")
    if report.composition_count != EXPECTED_COMPOSITION_COUNT:
        failures.append("substitution-graph-diagonal-witness-composition-count")
    if loaded.expected_composition_count != EXPECTED_COMPOSITION_COUNT:
        failures.append(
            "substitution-graph-diagonal-witness-composition-expected-count"
        )
    if tuple(loaded.required_source_kinds) != REQUIRED_SOURCE_KINDS:
        failures.append(
            "substitution-graph-diagonal-witness-composition-source-kind"
        )
    if _missing_items(COMPOSITION_NON_CLAIMS, loaded.non_claims):
        failures.append("substitution-graph-diagonal-witness-composition-non-claim")

    return loaded, _SupportLoad(
        accepted=report.accepted and not failures,
        failed_subjects=tuple(failures),
        facts={
            "composition_set_id": loaded.composition_set_id,
            "composition_count": report.composition_count,
            "expected_composition_count": loaded.expected_composition_count,
            "source_kind_counts": dict(report.source_kind_counts),
            "required_source_kinds": list(loaded.required_source_kinds),
            "failed_subjects": list(report.failed_subjects),
            "non_claim_count": len(loaded.non_claims),
            "formal_language_path": loaded.formal_language_path,
            "codebook_path": loaded.codebook_path,
            "correctness_targets_path": loaded.correctness_targets_path,
            "formula_candidates_path": loaded.formula_candidates_path,
            "formula_schema_relation_path": loaded.formula_schema_relation_path,
            "substitution_representability_targets_path": (
                loaded.substitution_representability_targets_path
            ),
            "diagonal_construction_targets_path": (
                loaded.diagonal_construction_targets_path
            ),
            "fixed_point_targets_path": loaded.fixed_point_targets_path,
        },
    )


def _validate_manifest(
    manifest: SubstitutionGraphDiagonalWitnessCompositionFrontierStatusManifest,
) -> list[SubstitutionGraphDiagonalWitnessCompositionFrontierValidation]:
    results: list[
        SubstitutionGraphDiagonalWitnessCompositionFrontierValidation
    ] = []
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

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.required_case_kind == REQUIRED_CASE_KIND:
        results.append(_accepted("required_case_kind", "case kind matches"))
    else:
        results.append(_rejected("required_case_kind", "unexpected case kind"))

    if manifest.required_case_status == REQUIRED_CASE_STATUS:
        results.append(_accepted("required_case_status", "case remains open"))
    else:
        results.append(_rejected("required_case_status", "unexpected case status"))

    if manifest.expected_support_surface_count == len(REQUIRED_SUPPORT_SUBJECTS):
        results.append(_accepted("expected_support_surface_count", "two surfaces"))
    else:
        results.append(
            _rejected(
                "expected_support_surface_count",
                "expected two support surfaces",
            )
        )

    if manifest.expected_composition_count == EXPECTED_COMPOSITION_COUNT:
        results.append(_accepted("expected_composition_count", "one composition"))
    else:
        results.append(
            _rejected(
                "expected_composition_count",
                "expected one composition",
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
        results.append(_accepted("non_claims", "non-claims are explicit"))

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))
    return results


def _validate_case_manifest_paths(
    manifest: Any | None,
) -> list[SubstitutionGraphDiagonalWitnessCompositionFrontierValidation]:
    results: list[
        SubstitutionGraphDiagonalWitnessCompositionFrontierValidation
    ] = []
    if manifest is None:
        return [_rejected("case_set_id", "case manifest unavailable")]

    if manifest.case_set_id == "as-substitution-graph-correctness-cases-v1":
        results.append(_accepted("case_set_id", "case set id matches"))
    else:
        results.append(_rejected("case_set_id", "unexpected case set id"))

    for field in (
        "formal_language_path",
        "codebook_path",
        "correctness_targets_path",
        "formula_candidates_path",
        "formula_schema_relation_path",
        "substitution_representability_targets_path",
        "diagonal_witness_composition_path",
    ):
        expected = EXPECTED_DEPENDENCY_PATHS[field]
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))
    return results


def _find_diagonal_witness_case(
    cases_manifest: Any | None,
) -> SubstitutionGraphDiagonalWitnessCompositionFrontierProofCase:
    if cases_manifest is None:
        return SubstitutionGraphDiagonalWitnessCompositionFrontierProofCase(
            case_id="missing",
            case_kind="missing",
            correctness_target_id="missing",
            status="missing",
            required_dependency_subjects=(),
            non_claims=(),
            next_as_action="missing",
        )
    for case in tuple(getattr(cases_manifest, "cases", ())):
        if getattr(case, "case_kind", None) != REQUIRED_CASE_KIND:
            continue
        return SubstitutionGraphDiagonalWitnessCompositionFrontierProofCase(
            case_id=case.case_id,
            case_kind=case.case_kind,
            correctness_target_id=case.correctness_target_id,
            status=case.status,
            required_dependency_subjects=tuple(case.required_dependency_subjects),
            non_claims=tuple(case.non_claims),
            next_as_action=case.next_as_action,
        )
    return SubstitutionGraphDiagonalWitnessCompositionFrontierProofCase(
        case_id="missing",
        case_kind="missing",
        correctness_target_id="missing",
        status="missing",
        required_dependency_subjects=(),
        non_claims=(),
        next_as_action="missing",
    )


def _validate_proof_case(
    case: SubstitutionGraphDiagonalWitnessCompositionFrontierProofCase,
) -> list[SubstitutionGraphDiagonalWitnessCompositionFrontierValidation]:
    results: list[
        SubstitutionGraphDiagonalWitnessCompositionFrontierValidation
    ] = []
    if case.case_id == REQUIRED_CASE_ID:
        results.append(_accepted("proof_case.case_id", "case id matches"))
    else:
        results.append(_rejected("proof_case.case_id", "unexpected case id"))

    if case.case_kind == REQUIRED_CASE_KIND:
        results.append(_accepted("proof_case.case_kind", "case kind matches"))
    else:
        results.append(_rejected("proof_case.case_kind", "case kind missing"))

    if case.status == REQUIRED_CASE_STATUS:
        results.append(_accepted("proof_case.status", "case remains open"))
    elif case.status in PROOF_PROMOTION_STATUSES:
        results.append(
            _rejected(
                "proof_case.status",
                "case is not open: proof-promotion status " + case.status,
            )
        )
    else:
        results.append(
            _rejected("proof_case.status", "case is not open: " + case.status)
        )

    if case.correctness_target_id == REQUIRED_CORRECTNESS_TARGET_ID:
        results.append(_accepted("proof_case.target", "correctness target matches"))
    else:
        results.append(_rejected("proof_case.target", "unknown correctness target"))

    if case.required_dependency_subjects == REQUIRED_CASE_SUPPORT_SUBJECTS:
        results.append(
            _accepted("proof_case.required_dependency_subjects", "support subjects match")
        )
    else:
        results.append(
            _rejected(
                "proof_case.required_dependency_subjects",
                "support subjects mismatch: expected "
                + ", ".join(REQUIRED_CASE_SUPPORT_SUBJECTS)
                + " but found "
                + _joined_or_none(case.required_dependency_subjects),
            )
        )

    missing_non_claims = _missing_items(CASE_NON_CLAIMS, case.non_claims)
    if missing_non_claims:
        results.append(
            _rejected(
                "proof_case.non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted("proof_case.non_claims", "case non-claims explicit"))

    if case.next_as_action.strip():
        results.append(_accepted("proof_case.next_as_action", "case next action present"))
    else:
        results.append(_rejected("proof_case.next_as_action", "missing next action"))
    return results


def _validate_support_path_alignment(
    manifest: SubstitutionGraphDiagonalWitnessCompositionFrontierStatusManifest,
    cases_manifest: Any | None,
    composition_manifest: Any | None,
) -> list[SubstitutionGraphDiagonalWitnessCompositionFrontierValidation]:
    results: list[
        SubstitutionGraphDiagonalWitnessCompositionFrontierValidation
    ] = []
    if cases_manifest is not None:
        for field in (
            "formal_language_path",
            "codebook_path",
            "correctness_targets_path",
            "formula_candidates_path",
            "formula_schema_relation_path",
            "substitution_representability_targets_path",
            "diagonal_witness_composition_path",
        ):
            results.append(
                _path_alignment_result(
                    "cases_manifest." + field,
                    getattr(cases_manifest, field),
                    getattr(manifest, field),
                )
            )
    else:
        results.append(
            _rejected("cases_manifest.paths", "case path alignment unavailable")
        )

    if composition_manifest is not None:
        for field in (
            "formal_language_path",
            "codebook_path",
            "correctness_targets_path",
            "formula_candidates_path",
            "formula_schema_relation_path",
            "substitution_representability_targets_path",
            "diagonal_construction_targets_path",
            "fixed_point_targets_path",
        ):
            results.append(
                _path_alignment_result(
                    "composition_manifest." + field,
                    getattr(composition_manifest, field),
                    getattr(manifest, field),
                )
            )
    else:
        results.append(
            _rejected("composition_manifest.paths", "composition path alignment unavailable")
        )
    return results


def _support_surfaces(
    paths: dict[str, Path],
    support_loads: dict[str, _SupportLoad],
) -> list[SubstitutionGraphDiagonalWitnessCompositionFrontierSupportSurface]:
    surfaces: list[
        SubstitutionGraphDiagonalWitnessCompositionFrontierSupportSurface
    ] = []
    path_key_by_subject = {
        "substitution_graph_correctness_cases": (
            "substitution_graph_correctness_cases_path"
        ),
        "diagonal_witness_composition": "diagonal_witness_composition_path",
    }
    for subject in REQUIRED_SUPPORT_SUBJECTS:
        load = support_loads[subject]
        if load.accepted:
            detail = "support accepted"
        else:
            detail = "support rejected"
            if load.failed_subjects:
                detail += ": " + ", ".join(load.failed_subjects)
        surfaces.append(
            SubstitutionGraphDiagonalWitnessCompositionFrontierSupportSurface(
                subject=subject,
                path=paths[path_key_by_subject[subject]],
                accepted=load.accepted,
                failed_subjects=load.failed_subjects,
                facts=dict(load.facts),
                detail=detail,
            )
        )
    return surfaces


def _validate_support_surfaces(
    manifest: SubstitutionGraphDiagonalWitnessCompositionFrontierStatusManifest,
    surfaces: list[SubstitutionGraphDiagonalWitnessCompositionFrontierSupportSurface],
) -> list[SubstitutionGraphDiagonalWitnessCompositionFrontierValidation]:
    results: list[
        SubstitutionGraphDiagonalWitnessCompositionFrontierValidation
    ] = []
    subjects = tuple(surface.subject for surface in surfaces)
    if subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(_accepted("support_surfaces", "support surface order matches"))
    else:
        results.append(_rejected("support_surfaces", "support surface order mismatch"))

    if len(surfaces) == manifest.expected_support_surface_count:
        results.append(_accepted("support_surface_count", "support count matches"))
    else:
        results.append(_rejected("support_surface_count", "support count mismatch"))

    for surface in surfaces:
        if surface.accepted and not surface.failed_subjects:
            results.append(_accepted(surface.subject, surface.detail))
            continue
        detail = surface.detail
        if surface.failed_subjects:
            detail += "; failed subjects: " + ", ".join(surface.failed_subjects)
        results.append(_rejected(surface.subject, detail))
    return results


def _path_alignment_result(
    subject: str,
    actual: str,
    expected: str,
) -> SubstitutionGraphDiagonalWitnessCompositionFrontierValidation:
    if actual == expected:
        return _accepted(subject, f"{expected} referenced")
    return _rejected(subject, f"expected {expected} but found {actual}")


def _accepted(
    subject: str,
    detail: str,
) -> SubstitutionGraphDiagonalWitnessCompositionFrontierValidation:
    return SubstitutionGraphDiagonalWitnessCompositionFrontierValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphDiagonalWitnessCompositionFrontierValidation:
    return SubstitutionGraphDiagonalWitnessCompositionFrontierValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _missing_items(required: tuple[str, ...], actual: tuple[str, ...]) -> list[str]:
    return [item for item in required if item not in actual]


def _joined_or_none(items: tuple[str, ...]) -> str:
    if not items:
        return "none"
    return ", ".join(items)


def _json_ready_facts(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_ready_facts(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_ready_facts(item) for item in value]
    if isinstance(value, list):
        return [_json_ready_facts(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "substitution-graph-diagonal-witness-composition-frontier-status"
    if subject == "non_claims":
        return "substitution-graph-diagonal-witness-composition-frontier-non-claim"
    if subject.endswith("_path") or ".paths" in subject:
        return "substitution-graph-diagonal-witness-composition-frontier-dependency"
    if subject in {
        "cases_manifest.diagonal_witness_composition_path",
        "composition_manifest.formal_language_path",
        "composition_manifest.codebook_path",
        "composition_manifest.correctness_targets_path",
        "composition_manifest.formula_candidates_path",
        "composition_manifest.formula_schema_relation_path",
        "composition_manifest.substitution_representability_targets_path",
        "composition_manifest.diagonal_construction_targets_path",
        "composition_manifest.fixed_point_targets_path",
    }:
        return "substitution-graph-diagonal-witness-composition-frontier-dependency"
    if subject == "proof_case.status":
        return "substitution-graph-diagonal-witness-composition-frontier-case-status"
    if subject == "proof_case.required_dependency_subjects":
        return "substitution-graph-diagonal-witness-composition-frontier-case-support"
    if subject == "proof_case.non_claims":
        return "substitution-graph-diagonal-witness-composition-frontier-case-non-claim"
    if subject in {
        "support_surfaces",
        "support_surface_count",
        "substitution_graph_correctness_cases",
        "diagonal_witness_composition",
    }:
        return "substitution-graph-diagonal-witness-composition-frontier-support"
    return "substitution-graph-diagonal-witness-composition-frontier-status"


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


if __name__ == "__main__":
    raise SystemExit(
        run_substitution_graph_diagonal_witness_composition_frontier_status_cli()
    )
