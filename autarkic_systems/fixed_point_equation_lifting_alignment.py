"""Finite alignment for lifting the checked fixed-point equation bridge.

This module checks that the open fixed-point-equation-lifting construction
case is aligned with the selected pi1 target context, the checked equation
bridge, the bridge-equality alignment surface, and the formal codebook. It is
only a finite context-alignment check; it does not prove bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_substitution import free_variables


DEFAULT_ALIGNMENT = Path("claims/fixed_point_equation_lifting_alignment.json")
DEFAULT_FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = ("equation-lifting-alignment",)
REQUIRED_FUTURE_WORK = (
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
REQUIRED_NON_CLAIMS = (
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
REQUIRED_CONSTRUCTION_DEPENDENCIES = {
    "fixed_point",
    "fixed_point_equation_bridge",
    "codebook",
    "equation_lifting_alignment",
}


@dataclass(frozen=True)
class FixedPointEquationLiftingAlignmentManifest:
    """Loaded manifest for finite fixed-point equation lifting alignment."""

    path: Path
    schema_version: int
    alignment_set_id: str
    reviewed_at: str
    purpose: str
    fixed_point_construction_cases_path: str
    fixed_point_targets_path: str
    fixed_point_equation_bridge_targets_path: str
    bridge_equality_alignment_path: str
    codebook_path: str
    expected_alignment_count: int
    expected_direct_target_code_length: int
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointEquationLiftingAlignmentValidation:
    """One validation result for equation-lifting alignment evidence."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointEquationLiftingAlignment:
    """One finite equation-lifting alignment check."""

    alignment_id: str
    source_kind: str
    target_id: str
    construction_case_id: str
    equation_bridge_id: str
    bridge_equality_alignment_id: str
    direct_target_code_length: int
    construction_case_is_open: bool
    construction_case_requires_alignment: bool
    target_is_pi1_template: bool
    target_variable_matches: bool
    bridge_direct_target_closed: bool
    bridge_target_skeleton_matches: bool
    bridge_slot_quotes_diagonal_instance: bool
    bridge_equality_alignment_accepted: bool
    bridge_alignment_route_matches: bool
    direct_target_context_matches: bool
    route_ids_match: bool
    all_dependencies_accepted: bool


@dataclass(frozen=True)
class FixedPointEquationLiftingAlignmentReport:
    """Validation report over finite equation-lifting alignment evidence."""

    manifest: FixedPointEquationLiftingAlignmentManifest
    fixed_point_construction_cases_path: Path
    fixed_point_targets_path: Path
    fixed_point_equation_bridge_targets_path: Path
    bridge_equality_alignment_path: Path
    codebook_path: Path
    formal_language_path: Path
    willard_map_path: Path
    results: tuple[FixedPointEquationLiftingAlignmentValidation, ...]
    alignments: tuple[FixedPointEquationLiftingAlignment, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every equation-lifting validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def alignment_count(self) -> int:
        """Return the number of checked equation-lifting alignments."""

        return len(self.alignments)

    @property
    def source_kind_counts(self) -> dict[str, int]:
        """Return observed alignment counts grouped by source kind."""

        counts = {source_kind: 0 for source_kind in REQUIRED_SOURCE_KINDS}
        for alignment in self.alignments:
            counts[alignment.source_kind] = counts.get(alignment.source_kind, 0) + 1
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


def load_fixed_point_equation_lifting_alignment(
    path: Path | str = DEFAULT_ALIGNMENT,
) -> FixedPointEquationLiftingAlignmentManifest:
    """Load the equation-lifting alignment manifest from JSON."""

    alignment_path = Path(path)
    data = json.loads(alignment_path.read_text(encoding="utf-8"))
    return FixedPointEquationLiftingAlignmentManifest(
        path=alignment_path,
        schema_version=_required_int(data, "schema_version"),
        alignment_set_id=_required_text(data, "alignment_set_id"),
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
        bridge_equality_alignment_path=_required_text(
            data,
            "bridge_equality_alignment_path",
        ),
        codebook_path=_required_text(data, "codebook_path"),
        expected_alignment_count=_required_int(data, "expected_alignment_count"),
        expected_direct_target_code_length=_required_int(
            data,
            "expected_direct_target_code_length",
        ),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_equation_lifting_alignment(
    manifest: FixedPointEquationLiftingAlignmentManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
    formal_language_path: Path | str = DEFAULT_FORMAL_LANGUAGE,
) -> FixedPointEquationLiftingAlignmentReport:
    """Validate finite fixed-point equation lifting alignment evidence."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(formal_language_path)
    checked_construction_cases_path = Path(
        manifest.fixed_point_construction_cases_path
    )
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)
    checked_equation_bridge_path = Path(
        manifest.fixed_point_equation_bridge_targets_path
    )
    checked_bridge_equality_alignment_path = Path(
        manifest.bridge_equality_alignment_path
    )
    checked_codebook_path = Path(manifest.codebook_path)

    construction_cases = load_fixed_point_construction_cases(
        checked_construction_cases_path
    )
    fixed_point_targets = load_fixed_point_targets(checked_fixed_point_path)
    fixed_point_report = validate_fixed_point_targets(
        fixed_point_targets,
        checked_willard_map_path,
        checked_language_path,
    )
    equation_bridge = load_fixed_point_equation_bridge_targets(
        checked_equation_bridge_path
    )
    equation_bridge_report = validate_fixed_point_equation_bridge_targets(
        equation_bridge,
        checked_language_path,
        checked_willard_map_path,
    )
    bridge_equality_alignment = load_fixed_point_bridge_equality_alignment(
        checked_bridge_equality_alignment_path
    )
    bridge_equality_alignment_report = validate_fixed_point_bridge_equality_alignment(
        bridge_equality_alignment,
        checked_willard_map_path,
    )
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )

    results: list[FixedPointEquationLiftingAlignmentValidation] = [
        _accepted("manifest", f"loaded {manifest.alignment_set_id}")
    ]
    results.extend(_validate_references(manifest))
    results.extend(_validate_manifest_lists(manifest))
    results.extend(
        _validate_dependency_reports(
            fixed_point_report,
            equation_bridge_report,
            bridge_equality_alignment_report,
            codebook_report,
        )
    )

    alignments: tuple[FixedPointEquationLiftingAlignment, ...] = ()
    try:
        alignments = _derive_alignments(
            construction_cases,
            fixed_point_report.accepted,
            fixed_point_targets.targets,
            equation_bridge_report.accepted,
            equation_bridge_report.observations,
            bridge_equality_alignment_report.accepted,
            bridge_equality_alignment_report.alignments,
            codebook_report.accepted,
        )
    except ValueError as exc:
        results.append(_rejected("alignments", str(exc)))
    results.extend(_validate_alignment_set(manifest, alignments))

    return FixedPointEquationLiftingAlignmentReport(
        manifest=manifest,
        fixed_point_construction_cases_path=checked_construction_cases_path,
        fixed_point_targets_path=checked_fixed_point_path,
        fixed_point_equation_bridge_targets_path=checked_equation_bridge_path,
        bridge_equality_alignment_path=checked_bridge_equality_alignment_path,
        codebook_path=checked_codebook_path,
        formal_language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        alignments=alignments,
    )


def fixed_point_equation_lifting_alignment_payload(
    report: FixedPointEquationLiftingAlignmentReport,
) -> dict[str, Any]:
    """Return a JSON-ready equation-lifting alignment payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "alignment_manifest": str(report.manifest.path),
        "alignment_set_id": report.manifest.alignment_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "fixed_point_construction_cases_path": str(
            report.fixed_point_construction_cases_path
        ),
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "bridge_equality_alignment_path": str(
            report.bridge_equality_alignment_path
        ),
        "codebook_path": str(report.codebook_path),
        "formal_language_path": str(report.formal_language_path),
        "willard_map": str(report.willard_map_path),
        "expected_alignment_count": report.manifest.expected_alignment_count,
        "alignment_count": report.alignment_count,
        "expected_direct_target_code_length": (
            report.manifest.expected_direct_target_code_length
        ),
        "source_kind_counts": report.source_kind_counts,
        "required_source_kinds": list(report.manifest.required_source_kinds),
        "required_future_work": list(report.manifest.required_future_work),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "alignments": [
            {
                "alignment_id": alignment.alignment_id,
                "source_kind": alignment.source_kind,
                "target_id": alignment.target_id,
                "construction_case_id": alignment.construction_case_id,
                "equation_bridge_id": alignment.equation_bridge_id,
                "bridge_equality_alignment_id": (
                    alignment.bridge_equality_alignment_id
                ),
                "observed_direct_target_code_length": (
                    alignment.direct_target_code_length
                ),
                "observed_construction_case_is_open": (
                    alignment.construction_case_is_open
                ),
                "observed_construction_case_requires_alignment": (
                    alignment.construction_case_requires_alignment
                ),
                "observed_target_is_pi1_template": (
                    alignment.target_is_pi1_template
                ),
                "observed_target_variable_matches": (
                    alignment.target_variable_matches
                ),
                "observed_bridge_direct_target_closed": (
                    alignment.bridge_direct_target_closed
                ),
                "observed_bridge_target_skeleton_matches": (
                    alignment.bridge_target_skeleton_matches
                ),
                "observed_bridge_slot_quotes_diagonal_instance": (
                    alignment.bridge_slot_quotes_diagonal_instance
                ),
                "observed_bridge_equality_alignment_accepted": (
                    alignment.bridge_equality_alignment_accepted
                ),
                "observed_direct_target_context_matches": (
                    alignment.direct_target_context_matches
                ),
                "observed_bridge_alignment_route_matches": (
                    alignment.bridge_alignment_route_matches
                ),
                "observed_route_ids_match": alignment.route_ids_match,
                "observed_all_dependencies_accepted": (
                    alignment.all_dependencies_accepted
                ),
            }
            for alignment in report.alignments
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


def format_fixed_point_equation_lifting_alignment_report(
    report: FixedPointEquationLiftingAlignmentReport,
) -> str:
    """Format a concise equation-lifting alignment report."""

    status = "accepted" if report.accepted else "rejected"
    failures = [
        alignment.alignment_id
        for alignment in report.alignments
        if not _alignment_accepted(alignment)
    ]
    source_counts = ", ".join(
        f"{source_kind}={count}"
        for source_kind, count in report.source_kind_counts.items()
    )
    lines = [
        f"Fixed-point equation lifting alignment: {status}",
        f"Alignment set: {report.manifest.alignment_set_id}",
        f"Equation-lifting alignments: {report.alignment_count}",
        f"Source kinds: {source_counts}",
        f"Alignment failures: {_joined_or_none(tuple(failures))}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_equation_lifting_alignment_cli(
    argv: list[str] | None = None,
) -> int:
    """Run finite fixed-point equation lifting alignment validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_equation_lifting_alignment",
        description="Validate AS fixed-point equation lifting alignment evidence.",
    )
    parser.add_argument(
        "--alignment",
        default=str(DEFAULT_ALIGNMENT),
        help="Path to the equation-lifting alignment manifest.",
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

    manifest = load_fixed_point_equation_lifting_alignment(args.alignment)
    report = validate_fixed_point_equation_lifting_alignment(
        manifest,
        args.willard_map,
        args.language,
    )
    if args.format == "json":
        print(json.dumps(
            fixed_point_equation_lifting_alignment_payload(report),
            sort_keys=True,
        ))
    else:
        print(format_fixed_point_equation_lifting_alignment_report(report))
    return 0 if report.accepted else 1


def _derive_alignments(
    construction_cases: Any,
    fixed_point_accepted: bool,
    fixed_point_targets: tuple[Any, ...],
    equation_bridge_accepted: bool,
    equation_observations: tuple[FixedPointEquationBridgeObservation, ...],
    bridge_equality_alignment_accepted: bool,
    bridge_equality_alignments: tuple[Any, ...],
    codebook_accepted: bool,
) -> tuple[FixedPointEquationLiftingAlignment, ...]:
    construction_case = _find_case(
        construction_cases.cases,
        "fixed-point-equation-lifting",
    )
    target = _first_or_none(fixed_point_targets)
    equation_observation = _first_or_none(equation_observations)
    bridge_equality_alignment = _first_or_none(bridge_equality_alignments)
    if target is None:
        raise ValueError("missing fixed-point target")
    if equation_observation is None:
        raise ValueError("missing fixed-point equation bridge observation")
    if bridge_equality_alignment is None:
        raise ValueError("missing bridge-equality alignment")

    target_is_pi1_template = (
        target.sentence_class == "pi1"
        and target.template_node.get("kind") == "pi1"
    )
    target_variable_matches = (
        target.template_variable == "n"
        and target.template_variable in free_variables(target.template_node)
    )
    route_ids_match = (
        construction_case.target_id
        == target.target_id
        == equation_observation.target_id
        == bridge_equality_alignment.target_id
        and equation_observation.bridge_id
        == bridge_equality_alignment.equation_bridge_id
    )
    bridge_alignment_route_matches = (
        bridge_equality_alignment.route_ids_match
        and bridge_equality_alignment.bridge_equation_matches_schema_instance
        and route_ids_match
    )
    direct_target_context_matches = (
        equation_observation.direct_target_closed
        and equation_observation.target_skeleton_matches
        and equation_observation.direct_slot_quotes_diagonal_instance
    )
    dependencies_accepted = (
        fixed_point_accepted
        and equation_bridge_accepted
        and bridge_equality_alignment_accepted
        and codebook_accepted
    )
    return (
        FixedPointEquationLiftingAlignment(
            alignment_id="AS-FIXED-POINT-EQUATION-LIFTING-ALIGNMENT",
            source_kind="equation-lifting-alignment",
            target_id=construction_case.target_id,
            construction_case_id=construction_case.case_id,
            equation_bridge_id=equation_observation.bridge_id,
            bridge_equality_alignment_id=bridge_equality_alignment.alignment_id,
            direct_target_code_length=equation_observation.direct_target_code_length,
            construction_case_is_open=construction_case.status == "proof-case-open",
            construction_case_requires_alignment=(
                REQUIRED_CONSTRUCTION_DEPENDENCIES.issubset(
                    set(construction_case.required_dependency_subjects)
                )
            ),
            target_is_pi1_template=target_is_pi1_template,
            target_variable_matches=target_variable_matches,
            bridge_direct_target_closed=equation_observation.direct_target_closed,
            bridge_target_skeleton_matches=(
                equation_observation.target_skeleton_matches
            ),
            bridge_slot_quotes_diagonal_instance=(
                equation_observation.direct_slot_quotes_diagonal_instance
            ),
            bridge_equality_alignment_accepted=(
                bridge_equality_alignment_accepted
                and bridge_equality_alignment.route_ids_match
                and bridge_equality_alignment.bridge_equation_matches_schema_instance
            ),
            bridge_alignment_route_matches=bridge_alignment_route_matches,
            direct_target_context_matches=direct_target_context_matches,
            route_ids_match=route_ids_match,
            all_dependencies_accepted=dependencies_accepted,
        ),
    )


def _validate_references(
    manifest: FixedPointEquationLiftingAlignmentManifest,
) -> list[FixedPointEquationLiftingAlignmentValidation]:
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
            "bridge_equality_alignment_path",
            manifest.bridge_equality_alignment_path,
            "claims/fixed_point_bridge_equality_alignment.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
    )
    results: list[FixedPointEquationLiftingAlignmentValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_manifest_lists(
    manifest: FixedPointEquationLiftingAlignmentManifest,
) -> list[FixedPointEquationLiftingAlignmentValidation]:
    results: list[FixedPointEquationLiftingAlignmentValidation] = []
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
    fixed_point_report: Any,
    equation_bridge_report: Any,
    bridge_equality_alignment_report: Any,
    codebook_report: Any,
) -> list[FixedPointEquationLiftingAlignmentValidation]:
    checks = (
        ("fixed_point", fixed_point_report, "fixed-point target"),
        (
            "fixed_point_equation_bridge",
            equation_bridge_report,
            "fixed-point equation bridge",
        ),
        (
            "bridge_equality_alignment",
            bridge_equality_alignment_report,
            "fixed-point bridge equality alignment",
        ),
        ("codebook", codebook_report, "formal codebook"),
    )
    results: list[FixedPointEquationLiftingAlignmentValidation] = []
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


def _validate_alignment_set(
    manifest: FixedPointEquationLiftingAlignmentManifest,
    alignments: tuple[FixedPointEquationLiftingAlignment, ...],
) -> list[FixedPointEquationLiftingAlignmentValidation]:
    results: list[FixedPointEquationLiftingAlignmentValidation] = []
    if len(alignments) == manifest.expected_alignment_count:
        results.append(
            _accepted(
                "expected_alignment_count",
                f"alignment count {len(alignments)} matches manifest",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_alignment_count",
                "alignment count mismatch: expected "
                f"{manifest.expected_alignment_count} but found {len(alignments)}",
            )
        )

    if len(alignments) != 1:
        return results
    alignment = alignments[0]
    if (
        alignment.direct_target_code_length
        == manifest.expected_direct_target_code_length
    ):
        results.append(
            _accepted(
                "expected_direct_target_code_length",
                "direct target length matches manifest",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_direct_target_code_length",
                "direct target length mismatch: expected "
                f"{manifest.expected_direct_target_code_length} but found "
                f"{alignment.direct_target_code_length}",
            )
        )

    bool_checks = (
        (
            "alignment.construction_case_is_open",
            alignment.construction_case_is_open,
            "construction case remains open",
            "construction case is not open",
        ),
        (
            "alignment.construction_case_requires_alignment",
            alignment.construction_case_requires_alignment,
            "construction case requires equation-lifting alignment",
            "construction case does not require equation-lifting alignment",
        ),
        (
            "alignment.target_is_pi1_template",
            alignment.target_is_pi1_template,
            "selected target remains a pi1 template",
            "selected target is not a pi1 template",
        ),
        (
            "alignment.target_variable_matches",
            alignment.target_variable_matches,
            "selected target free code variable matches",
            "selected target free code variable diverges",
        ),
        (
            "alignment.bridge_direct_target_closed",
            alignment.bridge_direct_target_closed,
            "bridge direct target remains closed",
            "bridge direct target is not closed",
        ),
        (
            "alignment.bridge_target_skeleton_matches",
            alignment.bridge_target_skeleton_matches,
            "bridge target skeleton matches selected context",
            "bridge target skeleton diverges from selected context",
        ),
        (
            "alignment.bridge_slot_quotes_diagonal_instance",
            alignment.bridge_slot_quotes_diagonal_instance,
            "bridge direct slot quotes the diagonal instance",
            "bridge direct slot does not quote the diagonal instance",
        ),
        (
            "alignment.bridge_equality_alignment_accepted",
            alignment.bridge_equality_alignment_accepted,
            "bridge-equality alignment remains accepted",
            "bridge-equality alignment is not accepted",
        ),
        (
            "alignment.direct_target_context_matches",
            alignment.direct_target_context_matches,
            "direct target context matches the checked bridge",
            "direct target context does not match the checked bridge",
        ),
        (
            "alignment.bridge_alignment_route_matches",
            alignment.bridge_alignment_route_matches,
            "bridge-equality route aligns with equation bridge",
            "bridge-equality route diverges from equation bridge",
        ),
        (
            "alignment.route_ids_match",
            alignment.route_ids_match,
            "target and bridge route ids match",
            "target or bridge route ids diverge",
        ),
        (
            "alignment.all_dependencies_accepted",
            alignment.all_dependencies_accepted,
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


def _alignment_accepted(alignment: FixedPointEquationLiftingAlignment) -> bool:
    return (
        alignment.construction_case_is_open
        and alignment.construction_case_requires_alignment
        and alignment.target_is_pi1_template
        and alignment.target_variable_matches
        and alignment.bridge_direct_target_closed
        and alignment.bridge_target_skeleton_matches
        and alignment.bridge_slot_quotes_diagonal_instance
        and alignment.bridge_equality_alignment_accepted
        and alignment.direct_target_context_matches
        and alignment.bridge_alignment_route_matches
        and alignment.route_ids_match
        and alignment.all_dependencies_accepted
    )


def _find_case(cases: tuple[Any, ...], case_kind: str) -> Any:
    for case in cases:
        if case.case_kind == case_kind:
            return case
    raise ValueError(f"missing construction case kind: {case_kind}")


def _first_or_none(items: tuple[Any, ...]) -> Any | None:
    if not items:
        return None
    return items[0]


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointEquationLiftingAlignmentValidation:
    return FixedPointEquationLiftingAlignmentValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointEquationLiftingAlignmentValidation:
    return FixedPointEquationLiftingAlignmentValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "expected_alignment_count":
        return "fixed-point-equation-lifting-alignment-count"
    if subject == "expected_direct_target_code_length":
        return "fixed-point-equation-lifting-alignment-length"
    if subject == "non_claims":
        return "fixed-point-equation-lifting-alignment-non-claim"
    if subject == "required_future_work":
        return "fixed-point-equation-lifting-alignment-future-work"
    if subject == "required_source_kinds":
        return "fixed-point-equation-lifting-alignment-source-kind"
    if subject == "next_as_action":
        return "fixed-point-equation-lifting-alignment-next-action"
    if subject == "alignments":
        return "fixed-point-equation-lifting-alignment-derivation"
    if subject.startswith("alignment."):
        return "fixed-point-equation-lifting-alignment-check"
    if subject.endswith("_path"):
        return "fixed-point-equation-lifting-alignment-path"
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
    raise SystemExit(run_fixed_point_equation_lifting_alignment_cli())
