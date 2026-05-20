"""Compact status surface for the AS fixed-point construction frontier.

The surrounding modules validate finite support artifacts for the current
fixed-point construction stack. This module only gathers those artifacts into a
fail-closed frontier report. It deliberately preserves the blocked boundary and
does not promote any construction case to a proved fixed-point equation.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Callable

from autarkic_systems.fixed_point_bridge_equality_alignment import (
    load_fixed_point_bridge_equality_alignment,
)
from autarkic_systems.fixed_point_bridge_equality_evaluation import (
    load_fixed_point_bridge_equality_evaluation,
)
from autarkic_systems.fixed_point_construction_cases import (
    load_fixed_point_construction_cases,
)
from autarkic_systems.fixed_point_diagonal_instance_candidate_surface import (
    load_fixed_point_diagonal_instance_candidate_surface,
)
from autarkic_systems.fixed_point_equation_lifting_alignment import (
    load_fixed_point_equation_lifting_alignment,
)
from autarkic_systems.fixed_point_substitution_graph_correctness_bridge import (
    load_fixed_point_substitution_graph_correctness_bridge,
)
from autarkic_systems.fixed_point_substitution_witness_bridge import (
    load_fixed_point_substitution_witness_bridge,
)


DEFAULT_STATUS = Path("claims/fixed_point_construction_frontier_status.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "fixed-point-construction"
REQUIRED_DEPENDENCY_SUBJECTS = (
    "fixed_point_construction_cases",
    "diagonal_instance_candidate_surface",
    "substitution_witness_bridge",
    "substitution_graph_correctness_bridge",
    "bridge_equality_alignment",
    "bridge_equality_evaluation",
    "equation_lifting_alignment",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "fixed_point_construction_cases_path": "claims/fixed_point_construction_cases.json",
    "diagonal_instance_candidate_surface_path": (
        "claims/fixed_point_diagonal_instance_candidate_surface.json"
    ),
    "substitution_witness_bridge_path": (
        "claims/fixed_point_substitution_witness_bridge.json"
    ),
    "substitution_graph_correctness_bridge_path": (
        "claims/fixed_point_substitution_graph_correctness_bridge.json"
    ),
    "bridge_equality_alignment_path": (
        "claims/fixed_point_bridge_equality_alignment.json"
    ),
    "bridge_equality_evaluation_path": (
        "claims/fixed_point_bridge_equality_evaluation.json"
    ),
    "equation_lifting_alignment_path": (
        "claims/fixed_point_equation_lifting_alignment.json"
    ),
}
SUPPORT_BY_CASE_KIND = {
    "diagonal-instance-closure": ("diagonal_instance_candidate_surface",),
    "substitution-representability-proof": ("substitution_witness_bridge",),
    "substitution-graph-correctness-proof": (
        "substitution_graph_correctness_bridge",
    ),
    "bridge-equality-proof": (
        "bridge_equality_alignment",
        "bridge_equality_evaluation",
    ),
    "fixed-point-equation-lifting": ("equation_lifting_alignment",),
}


@dataclass(frozen=True)
class FixedPointConstructionFrontierStatusManifest:
    """Loaded compact manifest for the fixed-point construction frontier."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    fixed_point_construction_cases_path: str
    diagonal_instance_candidate_surface_path: str
    substitution_witness_bridge_path: str
    substitution_graph_correctness_bridge_path: str
    bridge_equality_alignment_path: str
    bridge_equality_evaluation_path: str
    equation_lifting_alignment_path: str
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointConstructionFrontierStatusValidation:
    """One validation result for the frontier status report."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointConstructionFrontierSupportSurface:
    """Observed state of one finite support surface."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class FixedPointConstructionFrontierCaseSupport:
    """Per-case view of finite support while the proof case remains open."""

    case_id: str
    case_kind: str
    target_id: str
    status: str
    finite_support_subjects: tuple[str, ...]
    finite_support_accepted: bool


@dataclass(frozen=True)
class FixedPointConstructionFrontierStatusReport:
    """Validation report for the compact construction frontier status."""

    manifest: FixedPointConstructionFrontierStatusManifest
    willard_map_path: Path
    fixed_point_construction_cases_path: Path
    diagonal_instance_candidate_surface_path: Path
    substitution_witness_bridge_path: Path
    substitution_graph_correctness_bridge_path: Path
    bridge_equality_alignment_path: Path
    bridge_equality_evaluation_path: Path
    equation_lifting_alignment_path: Path
    results: tuple[FixedPointConstructionFrontierStatusValidation, ...]
    support_surfaces: tuple[FixedPointConstructionFrontierSupportSurface, ...]
    case_supports: tuple[FixedPointConstructionFrontierCaseSupport, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every frontier status validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def frontier_status(self) -> str:
        """Return the manifest frontier status for payloads and tests."""

        return self.manifest.frontier_status

    @property
    def frontier_blocked_by(self) -> str:
        """Return the blocker that this status surface preserves."""

        return self.manifest.frontier_blocked_by

    @property
    def case_count(self) -> int:
        """Return the number of observed construction cases."""

        return len(self.case_supports)

    @property
    def open_case_count(self) -> int:
        """Return the number of construction cases still explicitly open."""

        return sum(1 for case in self.case_supports if case.status == "proof-case-open")

    @property
    def support_surface_count(self) -> int:
        """Return the number of required support surfaces inspected."""

        return len(self.support_surfaces)

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
    """Small report shim used when a dependency cannot even be loaded."""

    accepted: bool
    failed_subjects: tuple[str, ...]


def load_fixed_point_construction_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> FixedPointConstructionFrontierStatusManifest:
    """Load the fixed-point construction frontier status manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return FixedPointConstructionFrontierStatusManifest(
        path=status_path,
        schema_version=_required_int(data, "schema_version"),
        status_set_id=_required_text(data, "status_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        frontier_status=_required_text(data, "frontier_status"),
        frontier_blocked_by=_required_text(data, "frontier_blocked_by"),
        fixed_point_construction_cases_path=_required_text(
            data,
            "fixed_point_construction_cases_path",
        ),
        diagonal_instance_candidate_surface_path=_required_text(
            data,
            "diagonal_instance_candidate_surface_path",
        ),
        substitution_witness_bridge_path=_required_text(
            data,
            "substitution_witness_bridge_path",
        ),
        substitution_graph_correctness_bridge_path=_required_text(
            data,
            "substitution_graph_correctness_bridge_path",
        ),
        bridge_equality_alignment_path=_required_text(
            data,
            "bridge_equality_alignment_path",
        ),
        bridge_equality_evaluation_path=_required_text(
            data,
            "bridge_equality_evaluation_path",
        ),
        equation_lifting_alignment_path=_required_text(
            data,
            "equation_lifting_alignment_path",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_construction_frontier_status(
    manifest: FixedPointConstructionFrontierStatusManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointConstructionFrontierStatusReport:
    """Validate the compact fixed-point construction frontier status."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)

    construction_cases, construction_case_report = _load_dependency_manifest(
        "fixed_point_construction_cases",
        paths["fixed_point_construction_cases_path"],
        load_fixed_point_construction_cases,
        "fixed-point-construction-cases-load",
    )
    dependency_reports = {
        "fixed_point_construction_cases": construction_case_report,
        "diagonal_instance_candidate_surface": _load_dependency_manifest(
            "diagonal_instance_candidate_surface",
            paths["diagonal_instance_candidate_surface_path"],
            load_fixed_point_diagonal_instance_candidate_surface,
            "fixed-point-diagonal-instance-candidate-surface-load",
        )[1],
        "substitution_witness_bridge": _load_dependency_manifest(
            "substitution_witness_bridge",
            paths["substitution_witness_bridge_path"],
            load_fixed_point_substitution_witness_bridge,
            "fixed-point-substitution-witness-bridge-load",
        )[1],
        "substitution_graph_correctness_bridge": _load_dependency_manifest(
            "substitution_graph_correctness_bridge",
            paths["substitution_graph_correctness_bridge_path"],
            load_fixed_point_substitution_graph_correctness_bridge,
            "fixed-point-substitution-graph-correctness-bridge-load",
        )[1],
        "bridge_equality_alignment": _load_dependency_manifest(
            "bridge_equality_alignment",
            paths["bridge_equality_alignment_path"],
            load_fixed_point_bridge_equality_alignment,
            "fixed-point-bridge-equality-alignment-load",
        )[1],
        "bridge_equality_evaluation": _load_dependency_manifest(
            "bridge_equality_evaluation",
            paths["bridge_equality_evaluation_path"],
            load_fixed_point_bridge_equality_evaluation,
            "fixed-point-bridge-equality-evaluation-load",
        )[1],
        "equation_lifting_alignment": _load_dependency_manifest(
            "equation_lifting_alignment",
            paths["equation_lifting_alignment_path"],
            load_fixed_point_equation_lifting_alignment,
            "fixed-point-equation-lifting-alignment-load",
        )[1],
    }

    results: list[FixedPointConstructionFrontierStatusValidation] = [
        _accepted("manifest", f"loaded {manifest.status_set_id}")
    ]
    results.extend(_validate_manifest(manifest))
    support_surfaces = _support_surfaces(paths, dependency_reports)
    results.extend(_validate_support_surfaces(support_surfaces))
    case_supports, case_results = _case_supports(
        construction_cases,
        frozenset(
            surface.subject for surface in support_surfaces if surface.accepted
        ),
    )
    results.extend(case_results)

    return FixedPointConstructionFrontierStatusReport(
        manifest=manifest,
        willard_map_path=checked_willard_map_path,
        fixed_point_construction_cases_path=paths["fixed_point_construction_cases_path"],
        diagonal_instance_candidate_surface_path=paths[
            "diagonal_instance_candidate_surface_path"
        ],
        substitution_witness_bridge_path=paths["substitution_witness_bridge_path"],
        substitution_graph_correctness_bridge_path=paths[
            "substitution_graph_correctness_bridge_path"
        ],
        bridge_equality_alignment_path=paths["bridge_equality_alignment_path"],
        bridge_equality_evaluation_path=paths["bridge_equality_evaluation_path"],
        equation_lifting_alignment_path=paths["equation_lifting_alignment_path"],
        results=tuple(results),
        support_surfaces=tuple(support_surfaces),
        case_supports=tuple(case_supports),
    )


def fixed_point_construction_frontier_status_payload(
    report: FixedPointConstructionFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready fixed-point construction frontier payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "status_manifest": str(report.manifest.path),
        "status_set_id": report.manifest.status_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "frontier_status": report.frontier_status,
        "frontier_blocked_by": report.frontier_blocked_by,
        "willard_map": str(report.willard_map_path),
        "fixed_point_construction_cases_path": str(
            report.fixed_point_construction_cases_path
        ),
        "diagonal_instance_candidate_surface_path": str(
            report.diagonal_instance_candidate_surface_path
        ),
        "substitution_witness_bridge_path": str(
            report.substitution_witness_bridge_path
        ),
        "substitution_graph_correctness_bridge_path": str(
            report.substitution_graph_correctness_bridge_path
        ),
        "bridge_equality_alignment_path": str(report.bridge_equality_alignment_path),
        "bridge_equality_evaluation_path": str(report.bridge_equality_evaluation_path),
        "equation_lifting_alignment_path": str(report.equation_lifting_alignment_path),
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
                "target_id": case.target_id,
                "status": case.status,
                "finite_support_subjects": list(case.finite_support_subjects),
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


def format_fixed_point_construction_frontier_status_report(
    report: FixedPointConstructionFrontierStatusReport,
) -> str:
    """Format a concise human-readable frontier status report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point construction frontier status: {status}",
        f"Status set: {report.manifest.status_set_id}",
        f"Frontier status: {report.frontier_status}",
        f"Blocked by: {report.frontier_blocked_by}",
        f"Open construction cases: {report.open_case_count}/{report.case_count}",
        f"Support surfaces: {report.support_surface_count}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Support:")
    for surface in report.support_surfaces:
        prefix = "accepted" if surface.accepted else "rejected"
        lines.append(f"- {surface.subject}: {prefix} ({surface.path})")
    lines.append("Construction cases:")
    for case in report.case_supports:
        lines.extend([
            f"- {case.case_id}",
            f"  Kind: {case.case_kind}",
            f"  Status: {case.status}",
            f"  Finite support: {_joined_or_none(case.finite_support_subjects)}",
            f"  Support accepted: {case.finite_support_accepted}",
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_construction_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run fixed-point construction frontier status validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_construction_frontier_status",
        description="Validate the AS fixed-point construction frontier status.",
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the fixed-point construction frontier status manifest.",
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

    manifest = load_fixed_point_construction_frontier_status(args.status)
    report = validate_fixed_point_construction_frontier_status(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(
            fixed_point_construction_frontier_status_payload(report),
            sort_keys=True,
        ))
    else:
        print(format_fixed_point_construction_frontier_status_report(report))
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointConstructionFrontierStatusManifest,
) -> dict[str, Path]:
    return {
        "fixed_point_construction_cases_path": Path(
            manifest.fixed_point_construction_cases_path
        ),
        "diagonal_instance_candidate_surface_path": Path(
            manifest.diagonal_instance_candidate_surface_path
        ),
        "substitution_witness_bridge_path": Path(
            manifest.substitution_witness_bridge_path
        ),
        "substitution_graph_correctness_bridge_path": Path(
            manifest.substitution_graph_correctness_bridge_path
        ),
        "bridge_equality_alignment_path": Path(
            manifest.bridge_equality_alignment_path
        ),
        "bridge_equality_evaluation_path": Path(
            manifest.bridge_equality_evaluation_path
        ),
        "equation_lifting_alignment_path": Path(
            manifest.equation_lifting_alignment_path
        ),
    }


def _load_dependency_manifest(
    subject: str,
    path: Path,
    loader: Callable[[Path], Any],
    load_failure_subject: str,
) -> tuple[Any | None, Any]:
    try:
        loaded = loader(path)
        return loaded, _validate_loaded_support_manifest(subject, loaded)
    except (OSError, ValueError, json.JSONDecodeError):
        return None, _DependencyFailure(False, (load_failure_subject,))


def _validate_loaded_support_manifest(subject: str, loaded: Any) -> _DependencyFailure:
    """Check cheap status invariants for an already factored support surface.

    The individual support modules own the expensive evidence derivations. This
    frontier layer only verifies that the expected compact surface is present
    and still carries its non-promotional boundary.
    """

    failures: list[str] = []
    if subject == "fixed_point_construction_cases":
        cases = tuple(loaded.cases)
        if loaded.case_set_id != "as-fixed-point-construction-cases-v1":
            failures.append("fixed-point-construction-cases-id")
        if len(cases) != 5:
            failures.append("fixed-point-construction-cases-count")
        if any(case.status != "proof-case-open" for case in cases):
            failures.append("fixed-point-construction-frontier-case-status")
        for case in cases:
            missing = [item for item in REQUIRED_NON_CLAIMS if item not in case.non_claims]
            if missing:
                failures.append("fixed-point-construction-cases-non-claim")
                break
    elif subject == "diagonal_instance_candidate_surface":
        _require_attr_value(
            loaded,
            "candidate_surface_set_id",
            "as-fixed-point-diagonal-instance-candidate-surface-v1",
            "fixed-point-diagonal-instance-candidate-surface-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_candidate_count",
            1,
            "fixed-point-diagonal-instance-candidate-surface-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-diagonal-instance-candidate-surface-non-claim")
    elif subject == "substitution_witness_bridge":
        _require_attr_value(
            loaded,
            "bridge_set_id",
            "as-fixed-point-substitution-witness-bridge-v1",
            "fixed-point-substitution-witness-bridge-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_bridge_count",
            1,
            "fixed-point-substitution-witness-bridge-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-substitution-witness-bridge-non-claim")
    elif subject == "substitution_graph_correctness_bridge":
        _require_attr_value(
            loaded,
            "bridge_set_id",
            "as-fixed-point-substitution-graph-correctness-bridge-v1",
            "fixed-point-substitution-graph-correctness-bridge-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_bridge_count",
            1,
            "fixed-point-substitution-graph-correctness-bridge-count",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_correctness_case_count",
            5,
            "fixed-point-substitution-graph-correctness-bridge-case-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-substitution-graph-correctness-bridge-non-claim")
    elif subject == "bridge_equality_alignment":
        _require_attr_value(
            loaded,
            "alignment_set_id",
            "as-fixed-point-bridge-equality-alignment-v1",
            "fixed-point-bridge-equality-alignment-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_alignment_count",
            1,
            "fixed-point-bridge-equality-alignment-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-bridge-equality-alignment-non-claim")
    elif subject == "bridge_equality_evaluation":
        _require_attr_value(
            loaded,
            "evaluation_set_id",
            "as-fixed-point-bridge-equality-evaluation-v1",
            "fixed-point-bridge-equality-evaluation-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_evaluation_count",
            1,
            "fixed-point-bridge-equality-evaluation-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-bridge-equality-evaluation-non-claim")
    elif subject == "equation_lifting_alignment":
        _require_attr_value(
            loaded,
            "alignment_set_id",
            "as-fixed-point-equation-lifting-alignment-v1",
            "fixed-point-equation-lifting-alignment-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_alignment_count",
            1,
            "fixed-point-equation-lifting-alignment-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-equation-lifting-alignment-non-claim")
    else:
        failures.append("fixed-point-construction-frontier-unknown-support")

    return _DependencyFailure(not failures, tuple(failures))


def _require_attr_value(
    loaded: Any,
    attr: str,
    expected: Any,
    failure: str,
    failures: list[str],
) -> None:
    if getattr(loaded, attr, None) != expected:
        failures.append(failure)


def _require_non_claims(
    loaded: Any,
    failures: list[str],
    failure: str,
) -> None:
    non_claims = tuple(getattr(loaded, "non_claims", ()))
    if not non_claims:
        failures.append(failure)
        return
    if any(claim in non_claims for claim in (
        "fixed-point-equation-proved",
        "self-consistency-theorem-proved",
    )):
        failures.append(failure)


def _support_surfaces(
    paths: dict[str, Path],
    dependency_reports: dict[str, Any],
) -> list[FixedPointConstructionFrontierSupportSurface]:
    path_by_subject = {
        "fixed_point_construction_cases": paths["fixed_point_construction_cases_path"],
        "diagonal_instance_candidate_surface": paths[
            "diagonal_instance_candidate_surface_path"
        ],
        "substitution_witness_bridge": paths["substitution_witness_bridge_path"],
        "substitution_graph_correctness_bridge": paths[
            "substitution_graph_correctness_bridge_path"
        ],
        "bridge_equality_alignment": paths["bridge_equality_alignment_path"],
        "bridge_equality_evaluation": paths["bridge_equality_evaluation_path"],
        "equation_lifting_alignment": paths["equation_lifting_alignment_path"],
    }
    surfaces: list[FixedPointConstructionFrontierSupportSurface] = []
    for subject in REQUIRED_DEPENDENCY_SUBJECTS:
        report = dependency_reports[subject]
        failed_subjects = tuple(report.failed_subjects)
        accepted = bool(report.accepted)
        detail = "accepted" if accepted else "rejected: " + _joined_or_none(failed_subjects)
        surfaces.append(
            FixedPointConstructionFrontierSupportSurface(
                subject=subject,
                path=path_by_subject[subject],
                accepted=accepted,
                failed_subjects=failed_subjects,
                detail=detail,
            )
        )
    return surfaces


def _validate_manifest(
    manifest: FixedPointConstructionFrontierStatusManifest,
) -> list[FixedPointConstructionFrontierStatusValidation]:
    results: list[FixedPointConstructionFrontierStatusValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.status_set_id == "as-fixed-point-construction-frontier-status-v1":
        results.append(_accepted("status_set_id", "status set id matches"))
    else:
        results.append(_rejected("status_set_id", "unexpected status set id"))

    if manifest.frontier_status == REQUIRED_FRONTIER_STATUS:
        results.append(_accepted("frontier_status", "frontier remains blocked"))
    elif manifest.frontier_status == "fixed-point-equation-proved":
        results.append(
            _rejected(
                "frontier_status",
                "overclaiming frontier status: fixed-point-equation-proved",
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
        results.append(_accepted("frontier_blocked_by", "blocked by fixed-point-construction"))
    else:
        results.append(
            _rejected(
                "frontier_blocked_by",
                "expected fixed-point-construction blocker",
            )
        )

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

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


def _validate_support_surfaces(
    surfaces: list[FixedPointConstructionFrontierSupportSurface],
) -> list[FixedPointConstructionFrontierStatusValidation]:
    results: list[FixedPointConstructionFrontierStatusValidation] = []
    observed_subjects = tuple(surface.subject for surface in surfaces)
    if observed_subjects == REQUIRED_DEPENDENCY_SUBJECTS:
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
    construction_cases: Any | None,
    accepted_support_subjects: frozenset[str],
) -> tuple[
    list[FixedPointConstructionFrontierCaseSupport],
    list[FixedPointConstructionFrontierStatusValidation],
]:
    if construction_cases is None:
        return [], [_rejected("cases", "construction cases could not be loaded")]

    case_supports: list[FixedPointConstructionFrontierCaseSupport] = []
    results: list[FixedPointConstructionFrontierStatusValidation] = []
    cases = tuple(construction_cases.cases)
    if len(cases) == 5:
        results.append(_accepted("cases", "five construction cases observed"))
    else:
        results.append(_rejected("cases", f"expected 5 construction cases, found {len(cases)}"))

    for case in cases:
        finite_support_subjects = SUPPORT_BY_CASE_KIND.get(case.case_kind, ())
        finite_support_accepted = all(
            subject in accepted_support_subjects for subject in finite_support_subjects
        )
        case_supports.append(
            FixedPointConstructionFrontierCaseSupport(
                case_id=case.case_id,
                case_kind=case.case_kind,
                target_id=case.target_id,
                status=case.status,
                finite_support_subjects=finite_support_subjects,
                finite_support_accepted=finite_support_accepted,
            )
        )

        if case.status == "proof-case-open":
            results.append(_accepted(f"{case.case_id}.status", "construction case remains open"))
        else:
            results.append(
                _rejected(
                    f"{case.case_id}.status",
                    f"construction case is not open: {case.status}",
                )
            )

        if not finite_support_subjects:
            results.append(_rejected(f"{case.case_id}.finite_support", "no finite support mapping"))
        elif finite_support_accepted:
            results.append(_accepted(f"{case.case_id}.finite_support", "finite support accepted"))
        else:
            missing = [
                subject
                for subject in finite_support_subjects
                if subject not in accepted_support_subjects
            ]
            results.append(
                _rejected(
                    f"{case.case_id}.finite_support",
                    "support surfaces rejected: " + ", ".join(missing),
                )
            )
    return case_supports, results


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "fixed-point-construction-frontier-status"
    if subject.endswith(".status"):
        return "fixed-point-construction-frontier-case-status"
    if subject == "non_claims":
        return "fixed-point-construction-frontier-non-claim"
    if subject in REQUIRED_DEPENDENCY_SUBJECTS or subject.endswith("_path"):
        return "fixed-point-construction-frontier-dependency"
    if subject.endswith(".finite_support") or subject in {"cases", "support_surfaces"}:
        return "fixed-point-construction-frontier-support"
    return "fixed-point-construction-frontier"


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


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointConstructionFrontierStatusValidation:
    return FixedPointConstructionFrontierStatusValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointConstructionFrontierStatusValidation:
    return FixedPointConstructionFrontierStatusValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_construction_frontier_status_cli())
