"""Compact status surface for the codebook-roundtrip correctness frontier.

The existing roundtrip module owns the finite executable check over graph
domain codes. This module is a smaller handoff layer: it confirms that the
matching substitution-graph correctness proof case remains open, that the
roundtrip support surface still accepts, and that neither artifact is being
treated as a general correctness proof.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.substitution_graph_codebook_roundtrip import (
    REQUIRED_NON_CLAIMS as ROUNDTRIP_NON_CLAIMS,
    load_substitution_graph_codebook_roundtrip,
    validate_substitution_graph_codebook_roundtrip,
)
from autarkic_systems.substitution_graph_correctness_cases import (
    REQUIRED_DEPENDENCIES_BY_KIND,
    REQUIRED_NON_CLAIMS as CASE_NON_CLAIMS,
    load_substitution_graph_correctness_cases,
)


DEFAULT_STATUS = Path(
    "claims/substitution_graph_codebook_roundtrip_frontier_status.json"
)

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "codebook-roundtrip"
REQUIRED_CASE_KIND = "codebook-roundtrip"
REQUIRED_CASE_STATUS = "proof-case-open"
EXPECTED_ROUNDTRIP_SUBJECT_COUNT = 12
EXPECTED_SUPPORT_SURFACE_COUNT = 2
REQUIRED_SUPPORT_SUBJECTS = (
    "substitution_graph_correctness_cases",
    "codebook_roundtrip",
)
REQUIRED_NON_CLAIMS = (
    "no formula correctness proof",
    "no substitution representability proof",
    "no diagonal lemma proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "substitution_graph_correctness_cases_path": (
        "claims/substitution_graph_correctness_cases.json"
    ),
    "codebook_roundtrip_path": "claims/substitution_graph_codebook_roundtrip.json",
    "codebook_path": "language/formal_codebook.json",
    "formula_candidates_path": "claims/substitution_graph_formula_candidates.json",
    "evaluation_examples_path": "claims/substitution_graph_evaluation_examples.json",
}
PROOF_PROMOTION_STATUSES = {
    "codebook-roundtrip-proved",
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


@dataclass(frozen=True)
class SubstitutionGraphCodebookRoundtripFrontierStatusManifest:
    """Loaded compact manifest for the codebook-roundtrip frontier."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    substitution_graph_correctness_cases_path: str
    codebook_roundtrip_path: str
    codebook_path: str
    formula_candidates_path: str
    evaluation_examples_path: str
    required_case_kind: str
    required_case_status: str
    expected_roundtrip_subject_count: int
    expected_support_surface_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphCodebookRoundtripFrontierStatusValidation:
    """One validation result for the compact frontier status."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphCodebookRoundtripFrontierProofCase:
    """Compact view of the matching substitution graph correctness case."""

    case_id: str
    case_kind: str
    correctness_target_id: str
    status: str
    required_dependency_subjects: tuple[str, ...]
    non_claims: tuple[str, ...]


@dataclass(frozen=True)
class SubstitutionGraphCodebookRoundtripFrontierSupportSurface:
    """Observed status of one support surface used by this handoff."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphCodebookRoundtripFrontierStatusReport:
    """Validation report for the compact codebook-roundtrip frontier."""

    manifest: SubstitutionGraphCodebookRoundtripFrontierStatusManifest
    substitution_graph_correctness_cases_path: Path
    codebook_roundtrip_path: Path
    codebook_path: Path
    formula_candidates_path: Path
    evaluation_examples_path: Path
    proof_case: SubstitutionGraphCodebookRoundtripFrontierProofCase
    support_surfaces: tuple[
        SubstitutionGraphCodebookRoundtripFrontierSupportSurface,
        ...
    ]
    support_facts: dict[str, dict[str, Any]]
    results: tuple[
        SubstitutionGraphCodebookRoundtripFrontierStatusValidation,
        ...
    ]

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
        """Return the proof case that still blocks this frontier."""

        return self.manifest.frontier_blocked_by

    @property
    def support_surface_count(self) -> int:
        """Return the number of compact support surfaces inspected."""

        return len(self.support_surfaces)

    @property
    def roundtrip_subject_count(self) -> int:
        """Return the observed finite roundtrip subject count, if available."""

        return int(
            self.support_facts
            .get("codebook_roundtrip", {})
            .get("subject_count", 0)
        )

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
class _SupportLoad:
    """Small result shim for loading support manifests fail-closed."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    facts: dict[str, Any]


def load_substitution_graph_codebook_roundtrip_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> SubstitutionGraphCodebookRoundtripFrontierStatusManifest:
    """Load the compact codebook-roundtrip frontier manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return SubstitutionGraphCodebookRoundtripFrontierStatusManifest(
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
        codebook_roundtrip_path=_required_text(data, "codebook_roundtrip_path"),
        codebook_path=_required_text(data, "codebook_path"),
        formula_candidates_path=_required_text(data, "formula_candidates_path"),
        evaluation_examples_path=_required_text(data, "evaluation_examples_path"),
        required_case_kind=_required_text(data, "required_case_kind"),
        required_case_status=_required_text(data, "required_case_status"),
        expected_roundtrip_subject_count=_required_int(
            data,
            "expected_roundtrip_subject_count",
        ),
        expected_support_surface_count=_required_int(
            data,
            "expected_support_surface_count",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_codebook_roundtrip_frontier_status(
    manifest: SubstitutionGraphCodebookRoundtripFrontierStatusManifest,
) -> SubstitutionGraphCodebookRoundtripFrontierStatusReport:
    """Validate the compact codebook-roundtrip frontier handoff."""

    paths = _manifest_paths(manifest)
    results: list[
        SubstitutionGraphCodebookRoundtripFrontierStatusValidation
    ] = [_accepted("manifest", f"loaded {manifest.status_set_id}")]
    results.extend(_validate_manifest(manifest))

    cases_manifest, cases_load = _load_correctness_cases(
        paths["substitution_graph_correctness_cases_path"]
    )
    roundtrip_manifest, roundtrip_load = _load_codebook_roundtrip(
        paths["codebook_roundtrip_path"]
    )

    proof_case = _find_codebook_roundtrip_case(cases_manifest)
    results.extend(_validate_proof_case(proof_case))
    results.extend(
        _validate_support_path_alignment(
            manifest,
            cases_manifest,
            roundtrip_manifest,
        )
    )

    support_loads = {
        "substitution_graph_correctness_cases": cases_load,
        "codebook_roundtrip": roundtrip_load,
    }
    support_surfaces = _support_surfaces(paths, support_loads)
    results.extend(_validate_support_surfaces(manifest, support_surfaces))
    results.extend(_validate_case_support(proof_case, support_surfaces))

    return SubstitutionGraphCodebookRoundtripFrontierStatusReport(
        manifest=manifest,
        substitution_graph_correctness_cases_path=paths[
            "substitution_graph_correctness_cases_path"
        ],
        codebook_roundtrip_path=paths["codebook_roundtrip_path"],
        codebook_path=paths["codebook_path"],
        formula_candidates_path=paths["formula_candidates_path"],
        evaluation_examples_path=paths["evaluation_examples_path"],
        proof_case=proof_case,
        support_surfaces=tuple(support_surfaces),
        support_facts={
            subject: dict(load.facts) for subject, load in support_loads.items()
        },
        results=tuple(results),
    )


def substitution_graph_codebook_roundtrip_frontier_status_payload(
    report: SubstitutionGraphCodebookRoundtripFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready codebook-roundtrip frontier payload."""

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
            "codebook_roundtrip": str(report.codebook_roundtrip_path),
            "codebook": str(report.codebook_path),
            "formula_candidates": str(report.formula_candidates_path),
            "evaluation_examples": str(report.evaluation_examples_path),
        },
        "proof_case": {
            "case_id": report.proof_case.case_id,
            "case_kind": report.proof_case.case_kind,
            "correctness_target_id": report.proof_case.correctness_target_id,
            "status": report.proof_case.status,
            "required_dependency_subjects": list(
                report.proof_case.required_dependency_subjects
            ),
        },
        "expected_roundtrip_subject_count": (
            report.manifest.expected_roundtrip_subject_count
        ),
        "roundtrip_subject_count": report.roundtrip_subject_count,
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
        "support_facts": report.support_facts,
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


def format_substitution_graph_codebook_roundtrip_frontier_status_report(
    report: SubstitutionGraphCodebookRoundtripFrontierStatusReport,
) -> str:
    """Format a concise human-readable codebook-roundtrip frontier report."""

    status = "accepted" if report.accepted else "rejected"
    case = report.proof_case
    lines = [
        f"Substitution graph codebook roundtrip frontier status: {status}",
        f"Status set: {report.manifest.status_set_id}",
        f"Frontier status: {report.frontier_status}",
        f"Blocked by: {report.frontier_blocked_by}",
        f"Proof case: {case.case_id}",
        f"Case kind: {case.case_kind}",
        f"Case status: {case.status}",
        f"Roundtrip subjects: {report.roundtrip_subject_count}",
        f"Support surfaces: {report.support_surface_count}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Support:")
    for surface in report.support_surfaces:
        prefix = "accepted" if surface.accepted else "rejected"
        lines.append(f"- {surface.subject}: {prefix} ({surface.path}) {surface.detail}")
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_codebook_roundtrip_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run codebook-roundtrip frontier status validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "substitution_graph_codebook_roundtrip_frontier_status"
        ),
        description=(
            "Validate the AS substitution graph codebook-roundtrip frontier "
            "status."
        ),
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the codebook-roundtrip frontier status manifest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_substitution_graph_codebook_roundtrip_frontier_status(
        args.status
    )
    report = validate_substitution_graph_codebook_roundtrip_frontier_status(
        manifest
    )
    if args.format == "json":
        print(
            json.dumps(
                substitution_graph_codebook_roundtrip_frontier_status_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            format_substitution_graph_codebook_roundtrip_frontier_status_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: SubstitutionGraphCodebookRoundtripFrontierStatusManifest,
) -> dict[str, Path]:
    return {
        "substitution_graph_correctness_cases_path": Path(
            manifest.substitution_graph_correctness_cases_path
        ),
        "codebook_roundtrip_path": Path(manifest.codebook_roundtrip_path),
        "codebook_path": Path(manifest.codebook_path),
        "formula_candidates_path": Path(manifest.formula_candidates_path),
        "evaluation_examples_path": Path(manifest.evaluation_examples_path),
    }


def _load_correctness_cases(path: Path) -> tuple[Any | None, _SupportLoad]:
    try:
        loaded = load_substitution_graph_correctness_cases(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None, _SupportLoad(
            accepted=False,
            failed_subjects=("substitution-graph-correctness-cases-load",),
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

    proof_case = _find_codebook_roundtrip_case(loaded)
    if proof_case.case_kind != REQUIRED_CASE_KIND:
        failures.append("substitution-graph-codebook-roundtrip-case-missing")
    return loaded, _SupportLoad(
        accepted=not failures,
        failed_subjects=tuple(failures),
        facts={
            "case_set_id": getattr(loaded, "case_set_id", ""),
            "case_count": len(cases),
            "codebook_roundtrip_case_status": proof_case.status,
        },
    )


def _load_codebook_roundtrip(path: Path) -> tuple[Any | None, _SupportLoad]:
    try:
        loaded = load_substitution_graph_codebook_roundtrip(path)
        report = validate_substitution_graph_codebook_roundtrip(loaded)
    except (OSError, ValueError, json.JSONDecodeError):
        return None, _SupportLoad(
            accepted=False,
            failed_subjects=("substitution-graph-codebook-roundtrip-load",),
            facts={},
        )

    failures = list(report.failed_subjects)
    if loaded.roundtrip_set_id != "as-substitution-graph-codebook-roundtrip-v1":
        failures.append("substitution-graph-codebook-roundtrip-id")
    if report.subject_count != EXPECTED_ROUNDTRIP_SUBJECT_COUNT:
        failures.append("substitution-graph-codebook-roundtrip-count")
    if loaded.expected_subject_count != EXPECTED_ROUNDTRIP_SUBJECT_COUNT:
        failures.append("substitution-graph-codebook-roundtrip-expected-count")
    if _missing_items(ROUNDTRIP_NON_CLAIMS, loaded.non_claims):
        failures.append("substitution-graph-codebook-roundtrip-non-claim")

    return loaded, _SupportLoad(
        accepted=report.accepted and not failures,
        failed_subjects=tuple(failures),
        facts={
            "roundtrip_set_id": loaded.roundtrip_set_id,
            "subject_count": report.subject_count,
            "expected_subject_count": loaded.expected_subject_count,
            "source_kind_counts": report.source_kind_counts,
            "failed_subjects": list(report.failed_subjects),
            "non_claim_count": len(loaded.non_claims),
        },
    )


def _validate_manifest(
    manifest: SubstitutionGraphCodebookRoundtripFrontierStatusManifest,
) -> list[SubstitutionGraphCodebookRoundtripFrontierStatusValidation]:
    results: list[
        SubstitutionGraphCodebookRoundtripFrontierStatusValidation
    ] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    expected_status_id = (
        "as-substitution-graph-codebook-roundtrip-frontier-status-v1"
    )
    if manifest.status_set_id == expected_status_id:
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
        results.append(_accepted("frontier_blocked_by", "blocked by codebook-roundtrip"))
    else:
        results.append(
            _rejected("frontier_blocked_by", "expected codebook-roundtrip blocker")
        )

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.required_case_kind == REQUIRED_CASE_KIND:
        results.append(_accepted("required_case_kind", "codebook-roundtrip case"))
    else:
        results.append(_rejected("required_case_kind", "unexpected proof case kind"))

    if manifest.required_case_status == REQUIRED_CASE_STATUS:
        results.append(_accepted("required_case_status", "proof case remains open"))
    else:
        results.append(_rejected("required_case_status", "unexpected proof case status"))

    if manifest.expected_roundtrip_subject_count == EXPECTED_ROUNDTRIP_SUBJECT_COUNT:
        results.append(_accepted("expected_roundtrip_subject_count", "12 checked"))
    else:
        results.append(
            _rejected(
                "expected_roundtrip_subject_count",
                "expected 12 roundtrip subjects",
            )
        )

    if manifest.expected_support_surface_count == EXPECTED_SUPPORT_SURFACE_COUNT:
        results.append(_accepted("expected_support_surface_count", "two surfaces"))
    else:
        results.append(
            _rejected(
                "expected_support_surface_count",
                "expected two support surfaces",
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


def _find_codebook_roundtrip_case(
    cases_manifest: Any | None,
) -> SubstitutionGraphCodebookRoundtripFrontierProofCase:
    if cases_manifest is None:
        return SubstitutionGraphCodebookRoundtripFrontierProofCase(
            case_id="missing",
            case_kind="missing",
            correctness_target_id="missing",
            status="missing",
            required_dependency_subjects=(),
            non_claims=(),
        )
    for case in tuple(getattr(cases_manifest, "cases", ())):
        if getattr(case, "case_kind", None) != REQUIRED_CASE_KIND:
            continue
        return SubstitutionGraphCodebookRoundtripFrontierProofCase(
            case_id=case.case_id,
            case_kind=case.case_kind,
            correctness_target_id=case.correctness_target_id,
            status=case.status,
            required_dependency_subjects=tuple(case.required_dependency_subjects),
            non_claims=tuple(case.non_claims),
        )
    return SubstitutionGraphCodebookRoundtripFrontierProofCase(
        case_id="missing",
        case_kind="missing",
        correctness_target_id="missing",
        status="missing",
        required_dependency_subjects=(),
        non_claims=(),
    )


def _validate_proof_case(
    proof_case: SubstitutionGraphCodebookRoundtripFrontierProofCase,
) -> list[SubstitutionGraphCodebookRoundtripFrontierStatusValidation]:
    results: list[
        SubstitutionGraphCodebookRoundtripFrontierStatusValidation
    ] = []
    if proof_case.case_kind == REQUIRED_CASE_KIND:
        results.append(_accepted("proof_case.kind", "codebook-roundtrip case found"))
    else:
        results.append(_rejected("proof_case.kind", "codebook-roundtrip case missing"))

    if proof_case.status == REQUIRED_CASE_STATUS:
        results.append(_accepted("proof_case.status", "proof case remains open"))
    elif proof_case.status in PROOF_PROMOTION_STATUSES:
        results.append(
            _rejected(
                "proof_case.status",
                "proof case is not open: " + proof_case.status,
            )
        )
    else:
        results.append(
            _rejected(
                "proof_case.status",
                "unsupported proof case status: " + proof_case.status,
            )
        )

    expected_dependencies = REQUIRED_DEPENDENCIES_BY_KIND[REQUIRED_CASE_KIND]
    if proof_case.required_dependency_subjects == expected_dependencies:
        results.append(
            _accepted(
                "proof_case.required_dependency_subjects",
                "dependency subjects match",
            )
        )
    else:
        results.append(
            _rejected(
                "proof_case.required_dependency_subjects",
                "dependency subjects mismatch: expected "
                + ", ".join(expected_dependencies)
                + " but found "
                + _joined_or_none(proof_case.required_dependency_subjects),
            )
        )

    missing_non_claims = _missing_items(CASE_NON_CLAIMS, proof_case.non_claims)
    if missing_non_claims:
        results.append(
            _rejected(
                "proof_case.non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted("proof_case.non_claims", "non-claims are explicit"))
    return results


def _validate_support_path_alignment(
    manifest: SubstitutionGraphCodebookRoundtripFrontierStatusManifest,
    cases_manifest: Any | None,
    roundtrip_manifest: Any | None,
) -> list[SubstitutionGraphCodebookRoundtripFrontierStatusValidation]:
    results: list[
        SubstitutionGraphCodebookRoundtripFrontierStatusValidation
    ] = []
    if cases_manifest is not None:
        results.extend([
            _path_alignment_result(
                "cases_manifest.codebook_path",
                getattr(cases_manifest, "codebook_path", ""),
                manifest.codebook_path,
            ),
            _path_alignment_result(
                "cases_manifest.codebook_roundtrip_path",
                getattr(cases_manifest, "codebook_roundtrip_path", ""),
                manifest.codebook_roundtrip_path,
            ),
        ])
    else:
        results.append(
            _rejected(
                "cases_manifest.paths",
                "cannot check case manifest path alignment",
            )
        )

    if roundtrip_manifest is not None:
        results.extend([
            _path_alignment_result(
                "roundtrip_manifest.codebook_path",
                getattr(roundtrip_manifest, "codebook_path", ""),
                manifest.codebook_path,
            ),
            _path_alignment_result(
                "roundtrip_manifest.formula_candidates_path",
                getattr(roundtrip_manifest, "formula_candidates_path", ""),
                manifest.formula_candidates_path,
            ),
            _path_alignment_result(
                "roundtrip_manifest.evaluation_examples_path",
                getattr(roundtrip_manifest, "evaluation_examples_path", ""),
                manifest.evaluation_examples_path,
            ),
        ])
    else:
        results.append(
            _rejected(
                "roundtrip_manifest.paths",
                "cannot check roundtrip manifest path alignment",
            )
        )
    return results


def _path_alignment_result(
    subject: str,
    actual: str,
    expected: str,
) -> SubstitutionGraphCodebookRoundtripFrontierStatusValidation:
    if actual == expected:
        return _accepted(subject, f"{expected} aligned")
    return _rejected(subject, f"expected {expected} but found {actual}")


def _support_surfaces(
    paths: dict[str, Path],
    support_loads: dict[str, _SupportLoad],
) -> list[SubstitutionGraphCodebookRoundtripFrontierSupportSurface]:
    path_by_subject = {
        "substitution_graph_correctness_cases": paths[
            "substitution_graph_correctness_cases_path"
        ],
        "codebook_roundtrip": paths["codebook_roundtrip_path"],
    }
    surfaces: list[SubstitutionGraphCodebookRoundtripFrontierSupportSurface] = []
    for subject in REQUIRED_SUPPORT_SUBJECTS:
        load = support_loads[subject]
        surfaces.append(
            SubstitutionGraphCodebookRoundtripFrontierSupportSurface(
                subject=subject,
                path=path_by_subject[subject],
                accepted=load.accepted,
                failed_subjects=load.failed_subjects,
                detail=_support_detail(subject, load),
            )
        )
    return surfaces


def _support_detail(subject: str, load: _SupportLoad) -> str:
    if not load.accepted:
        return "rejected: " + _joined_or_none(load.failed_subjects)
    if subject == "substitution_graph_correctness_cases":
        return "case count " + str(load.facts.get("case_count"))
    if subject == "codebook_roundtrip":
        return "roundtrip subjects " + str(load.facts.get("subject_count"))
    return "accepted"


def _validate_support_surfaces(
    manifest: SubstitutionGraphCodebookRoundtripFrontierStatusManifest,
    surfaces: list[SubstitutionGraphCodebookRoundtripFrontierSupportSurface],
) -> list[SubstitutionGraphCodebookRoundtripFrontierStatusValidation]:
    results: list[
        SubstitutionGraphCodebookRoundtripFrontierStatusValidation
    ] = []
    observed_subjects = tuple(surface.subject for surface in surfaces)
    if observed_subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(_accepted("support_surfaces", "required support surfaces present"))
    else:
        results.append(_rejected("support_surfaces", "support surface order mismatch"))

    if len(surfaces) == manifest.expected_support_surface_count:
        results.append(_accepted("support_surface_count", "support surface count matches"))
    else:
        results.append(
            _rejected(
                "support_surface_count",
                "expected "
                + str(manifest.expected_support_surface_count)
                + " support surfaces",
            )
        )

    for surface in surfaces:
        if surface.accepted:
            results.append(_accepted(surface.subject, surface.detail))
        else:
            results.append(_rejected(surface.subject, surface.detail))
    return results


def _validate_case_support(
    proof_case: SubstitutionGraphCodebookRoundtripFrontierProofCase,
    surfaces: list[SubstitutionGraphCodebookRoundtripFrontierSupportSurface],
) -> list[SubstitutionGraphCodebookRoundtripFrontierStatusValidation]:
    required_surface_subjects = {"codebook_roundtrip"}
    accepted_surface_subjects = {surface.subject for surface in surfaces if surface.accepted}
    missing = sorted(required_surface_subjects - accepted_surface_subjects)
    if missing:
        return [
            _rejected(
                "proof_case.support",
                "support surfaces rejected: " + ", ".join(missing),
            )
        ]

    if "codebook_roundtrip" not in proof_case.required_dependency_subjects:
        return [
            _rejected(
                "proof_case.support",
                "codebook_roundtrip dependency missing from proof case",
            )
        ]

    return [_accepted("proof_case.support", "codebook roundtrip support accepted")]


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "substitution-graph-codebook-roundtrip-frontier-status"
    if subject == "non_claims":
        return "substitution-graph-codebook-roundtrip-frontier-non-claim"
    if subject == "proof_case.status":
        return "substitution-graph-codebook-roundtrip-frontier-case-status"
    if subject == "proof_case.non_claims":
        return "substitution-graph-codebook-roundtrip-frontier-case-non-claim"
    if subject in {
        "proof_case.required_dependency_subjects",
        "proof_case.support",
    }:
        return "substitution-graph-codebook-roundtrip-frontier-case-support"
    if (
        subject.endswith("_path")
        or subject.endswith(".paths")
        or ".codebook_path" in subject
        or ".codebook_roundtrip_path" in subject
        or ".formula_candidates_path" in subject
        or ".evaluation_examples_path" in subject
    ):
        return "substitution-graph-codebook-roundtrip-frontier-dependency"
    if subject in REQUIRED_SUPPORT_SUBJECTS or subject in {
        "support_surfaces",
        "support_surface_count",
    }:
        return "substitution-graph-codebook-roundtrip-frontier-support"
    return "substitution-graph-codebook-roundtrip-frontier"


def _missing_items(
    required: tuple[str, ...],
    observed: tuple[str, ...],
) -> list[str]:
    return [item for item in required if item not in observed]


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


def _accepted(
    subject: str,
    detail: str,
) -> SubstitutionGraphCodebookRoundtripFrontierStatusValidation:
    return SubstitutionGraphCodebookRoundtripFrontierStatusValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphCodebookRoundtripFrontierStatusValidation:
    return SubstitutionGraphCodebookRoundtripFrontierStatusValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(
        run_substitution_graph_codebook_roundtrip_frontier_status_cli()
    )
