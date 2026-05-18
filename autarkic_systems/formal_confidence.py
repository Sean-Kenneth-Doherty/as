"""Checked formal-confidence target boundaries for AS.

The current repository has executable substrate evidence and local proof
certificates, but that is not the same thing as a Willard-style
self-consistency result. This module validates a small manifest that states the
candidate formal-confidence target, names the Willard anchors it depends on,
and records the blockers that prevent overclaiming.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.consistency_level import (
    load_consistency_level_targets,
    validate_consistency_level_targets,
)
from autarkic_systems.diagonal_construction import (
    load_diagonal_construction_targets,
    validate_diagonal_construction_targets,
)
from autarkic_systems.fixed_point_equation import (
    load_fixed_point_equation_candidates,
    validate_fixed_point_equation_candidates,
)
from autarkic_systems.fixed_point_obstruction import (
    load_fixed_point_obstructions,
    validate_fixed_point_obstructions,
)
from autarkic_systems.substitution_representability import (
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)
from autarkic_systems.substitution_graph_target import (
    load_substitution_graph_targets,
    validate_substitution_graph_targets,
)
from autarkic_systems.substitution_graph_formula import (
    load_substitution_graph_formula_candidates,
    validate_substitution_graph_formula_candidates,
)
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_TARGETS = Path("claims/formal_confidence_targets.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_CONFIGURATION_FIELDS = (
    "language",
    "bounded_formula_class",
    "axiom_basis",
    "deduction_method",
    "proof_code_encoding",
    "consistency_notion",
    "consistency_level_target",
    "self_reference",
    "diagonal_construction",
    "substitution_representability",
    "substitution_graph",
    "substitution_graph_formula",
    "fixed_point_equation_candidate",
    "fixed_point_obstruction",
    "substrate_bridge",
)

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.6-LEVEL-K-CONSISTENCY",
    "W2011-D5.7-SELFCONSK",
    "W2020-D3.2-SELF-JUSTIFYING-GENAC",
    "W2020-T4.4-T4.5-LEM-BOUNDARY",
)

VALID_TARGET_STATUSES = {
    "accepted",
    "blocked",
    "candidate",
    "out-of-scope",
}


@dataclass(frozen=True)
class FormalConfidenceTarget:
    """One scoped AS formal-confidence target or boundary."""

    target_id: str
    status: str
    summary: str
    willard_anchor_ids: tuple[str, ...]
    configuration: dict[str, str]
    blocked_by: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FormalConfidenceTargetManifest:
    """Loaded manifest of formal-confidence targets."""

    path: Path
    schema_version: int
    reviewed_at: str
    purpose: str
    targets: tuple[FormalConfidenceTarget, ...]


@dataclass(frozen=True)
class FormalConfidenceValidation:
    """One validation result for the formal-confidence target surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FormalConfidenceReport:
    """Validation report over formal-confidence targets and Willard anchors."""

    target_manifest: FormalConfidenceTargetManifest
    willard_map_path: Path
    results: tuple[FormalConfidenceValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every target validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def target_count(self) -> int:
        """Return the number of checked formal-confidence targets."""

        return len(self.target_manifest.targets)

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


def load_formal_confidence_targets(
    path: Path | str = DEFAULT_TARGETS,
) -> FormalConfidenceTargetManifest:
    """Load the formal-confidence target manifest from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    targets = data.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("formal-confidence target manifest must contain targets")
    return FormalConfidenceTargetManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        targets=tuple(_parse_target(target) for target in targets),
    )


def validate_formal_confidence_targets(
    manifest: FormalConfidenceTargetManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FormalConfidenceReport:
    """Validate formal-confidence targets against the Willard anchor map."""

    map_path = Path(willard_map_path)
    willard_map = load_willard_definition_map(map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}
    results: list[FormalConfidenceValidation] = [
        _accepted("manifest.targets", f"loaded {len(manifest.targets)} target(s)")
    ]
    target_ids = [target.target_id for target in manifest.targets]
    duplicate_ids = _duplicates(target_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "manifest.target_id",
                f"duplicate target ids: {', '.join(duplicate_ids)}",
            )
        )
    else:
        results.append(_accepted("manifest.target_id", "target ids are unique"))

    for target in manifest.targets:
        results.extend(_validate_target(target, known_anchor_ids))

    return FormalConfidenceReport(
        target_manifest=manifest,
        willard_map_path=map_path,
        results=tuple(results),
    )


def formal_confidence_report_payload(report: FormalConfidenceReport) -> dict[str, Any]:
    """Return a JSON-ready formal-confidence target validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.target_manifest.schema_version,
        "reviewed_at": report.target_manifest.reviewed_at,
        "target_manifest": str(report.target_manifest.path),
        "willard_map": str(report.willard_map_path),
        "target_count": report.target_count,
        "failed_subjects": list(report.failed_subjects),
        "targets": [
            {
                "target_id": target.target_id,
                "status": target.status,
                "summary": target.summary,
                "willard_anchor_ids": list(target.willard_anchor_ids),
                "configuration": dict(target.configuration),
                "blocked_by": list(target.blocked_by),
                "next_as_action": target.next_as_action,
            }
            for target in report.target_manifest.targets
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


def format_formal_confidence_report(report: FormalConfidenceReport) -> str:
    """Format a concise human-readable formal-confidence target report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Formal confidence targets: {status}",
        f"Targets: {report.target_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for target in report.target_manifest.targets:
        lines.extend([
            f"- {target.target_id}: {target.status}",
            f"  Summary: {target.summary}",
            "  Willard anchors: " + ", ".join(target.willard_anchor_ids),
            "  Blockers: " + _joined_or_none(target.blocked_by),
            f"  Next AS action: {target.next_as_action}",
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_formal_confidence_cli(argv: list[str] | None = None) -> int:
    """Run the formal-confidence target validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.formal_confidence",
        description="Validate AS formal-confidence target boundaries.",
    )
    parser.add_argument(
        "--targets",
        default=str(DEFAULT_TARGETS),
        help="Path to the formal-confidence target manifest.",
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

    manifest = load_formal_confidence_targets(args.targets)
    report = validate_formal_confidence_targets(manifest, args.willard_map)
    if args.format == "json":
        print(json.dumps(formal_confidence_report_payload(report), sort_keys=True))
    else:
        print(format_formal_confidence_report(report))
    return 0 if report.accepted else 1


def _parse_target(item: dict[str, Any]) -> FormalConfidenceTarget:
    return FormalConfidenceTarget(
        target_id=_required_text(item, "target_id"),
        status=_required_text(item, "status"),
        summary=_required_text(item, "summary"),
        willard_anchor_ids=tuple(
            _required_text_list(item, "willard_anchor_ids")
        ),
        configuration=_required_text_mapping(item, "configuration"),
        blocked_by=tuple(_required_text_list(item, "blocked_by", allow_empty=True)),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _validate_target(
    target: FormalConfidenceTarget,
    known_anchor_ids: set[str],
) -> list[FormalConfidenceValidation]:
    results: list[FormalConfidenceValidation] = []
    target_label = target.target_id

    if target.status not in VALID_TARGET_STATUSES:
        results.append(
            _rejected(
                f"{target_label}.status",
                f"unknown target status: {target.status}",
            )
        )
    else:
        results.append(_accepted(f"{target_label}.status", "target status known"))

    unknown_anchor_ids = sorted(set(target.willard_anchor_ids) - known_anchor_ids)
    missing_required = sorted(
        set(REQUIRED_WILLARD_ANCHORS) - set(target.willard_anchor_ids)
    )
    if unknown_anchor_ids:
        results.append(
            _rejected(
                f"{target_label}.willard_anchors",
                "unknown Willard anchor IDs: " + ", ".join(unknown_anchor_ids),
            )
        )
    elif missing_required:
        results.append(
            _rejected(
                f"{target_label}.willard_anchors",
                "missing required Willard anchors: " + ", ".join(missing_required),
            )
        )
    else:
        results.append(
            _accepted(
                f"{target_label}.willard_anchors",
                "required Willard anchors are present and known",
            )
        )

    missing_fields = [
        field
        for field in REQUIRED_CONFIGURATION_FIELDS
        if field not in target.configuration
    ]
    blank_fields = [
        field
        for field, value in target.configuration.items()
        if not value.strip()
    ]
    if missing_fields:
        results.append(
            _rejected(
                f"{target_label}.configuration",
                "missing configuration fields: " + ", ".join(missing_fields),
            )
        )
    elif blank_fields:
        results.append(
            _rejected(
                f"{target_label}.configuration",
                "blank configuration fields: " + ", ".join(sorted(blank_fields)),
            )
        )
    else:
        results.append(
            _accepted(
                f"{target_label}.configuration",
                "required configuration fields are present",
            )
        )

    if "consistency_level_target" in target.configuration:
        results.extend(_validate_consistency_level_target(target))

    if "diagonal_construction" in target.configuration:
        results.extend(_validate_diagonal_construction(target))

    if "substitution_representability" in target.configuration:
        results.extend(_validate_substitution_representability(target))

    if "substitution_graph" in target.configuration:
        results.extend(_validate_substitution_graph(target))

    if "substitution_graph_formula" in target.configuration:
        results.extend(_validate_substitution_graph_formula(target))

    if "fixed_point_equation_candidate" in target.configuration:
        results.extend(_validate_fixed_point_equation_candidate(target))

    if "fixed_point_obstruction" in target.configuration:
        results.extend(_validate_fixed_point_obstruction(target))

    if target.status == "blocked" and not target.blocked_by:
        results.append(
            _rejected(
                f"{target_label}.blockers",
                "blocked targets must name blockers",
            )
        )
    else:
        results.append(
            _accepted(f"{target_label}.blockers", "blocker state is explicit")
        )

    if target.next_as_action.strip():
        results.append(
            _accepted(f"{target_label}.next_as_action", "next action present")
        )
    else:
        results.append(
            _rejected(f"{target_label}.next_as_action", "missing next action")
        )

    return results


def _validate_consistency_level_target(
    target: FormalConfidenceTarget,
) -> list[FormalConfidenceValidation]:
    subject = f"{target.target_id}.consistency_level_target"
    target_path = target.configuration["consistency_level_target"]
    try:
        consistency_targets = load_consistency_level_targets(target_path)
        report = validate_consistency_level_targets(consistency_targets)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [
            _rejected(
                subject,
                "consistency-level target rejected: " + str(exc),
            )
        ]
    if report.accepted:
        return [_accepted(subject, "consistency-level target accepted")]
    return [
        _rejected(
            subject,
            "consistency-level target rejected: "
            + _joined_or_none(report.failed_subjects),
        )
    ]


def _validate_diagonal_construction(
    target: FormalConfidenceTarget,
) -> list[FormalConfidenceValidation]:
    subject = f"{target.target_id}.diagonal_construction"
    target_path = target.configuration["diagonal_construction"]
    try:
        diagonal_targets = load_diagonal_construction_targets(target_path)
        report = validate_diagonal_construction_targets(diagonal_targets)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [
            _rejected(
                subject,
                "diagonal construction rejected: " + str(exc),
            )
        ]
    if report.accepted:
        return [_accepted(subject, "diagonal construction accepted")]
    return [
        _rejected(
            subject,
            "diagonal construction rejected: "
            + _joined_or_none(report.failed_subjects),
        )
    ]


def _validate_substitution_representability(
    target: FormalConfidenceTarget,
) -> list[FormalConfidenceValidation]:
    subject = f"{target.target_id}.substitution_representability"
    target_path = target.configuration["substitution_representability"]
    try:
        witnesses = load_substitution_representability_targets(target_path)
        report = validate_substitution_representability_targets(witnesses)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [
            _rejected(
                subject,
                "substitution representability rejected: " + str(exc),
            )
        ]
    if report.accepted:
        return [_accepted(subject, "substitution representability accepted")]
    return [
        _rejected(
            subject,
            "substitution representability rejected: "
            + _joined_or_none(report.failed_subjects),
        )
    ]


def _validate_substitution_graph(
    target: FormalConfidenceTarget,
) -> list[FormalConfidenceValidation]:
    subject = f"{target.target_id}.substitution_graph"
    target_path = target.configuration["substitution_graph"]
    try:
        graph_targets = load_substitution_graph_targets(target_path)
        report = validate_substitution_graph_targets(graph_targets)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [
            _rejected(
                subject,
                "substitution graph target rejected: " + str(exc),
            )
        ]
    if report.accepted:
        return [_accepted(subject, "substitution graph target accepted")]
    return [
        _rejected(
            subject,
            "substitution graph target rejected: "
            + _joined_or_none(report.failed_subjects),
        )
    ]


def _validate_substitution_graph_formula(
    target: FormalConfidenceTarget,
) -> list[FormalConfidenceValidation]:
    subject = f"{target.target_id}.substitution_graph_formula"
    target_path = target.configuration["substitution_graph_formula"]
    try:
        candidates = load_substitution_graph_formula_candidates(target_path)
        report = validate_substitution_graph_formula_candidates(candidates)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [
            _rejected(
                subject,
                "substitution graph formula rejected: " + str(exc),
            )
        ]
    if report.accepted:
        return [_accepted(subject, "substitution graph formula accepted")]
    return [
        _rejected(
            subject,
            "substitution graph formula rejected: "
            + _joined_or_none(report.failed_subjects),
        )
    ]


def _validate_fixed_point_equation_candidate(
    target: FormalConfidenceTarget,
) -> list[FormalConfidenceValidation]:
    subject = f"{target.target_id}.fixed_point_equation_candidate"
    candidate_path = target.configuration["fixed_point_equation_candidate"]
    try:
        candidates = load_fixed_point_equation_candidates(candidate_path)
        report = validate_fixed_point_equation_candidates(candidates)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [
            _rejected(
                subject,
                "fixed-point equation candidate rejected: " + str(exc),
            )
        ]
    if report.accepted:
        return [_accepted(subject, "fixed-point equation candidate accepted")]
    return [
        _rejected(
            subject,
            "fixed-point equation candidate rejected: "
            + _joined_or_none(report.failed_subjects),
        )
    ]


def _validate_fixed_point_obstruction(
    target: FormalConfidenceTarget,
) -> list[FormalConfidenceValidation]:
    subject = f"{target.target_id}.fixed_point_obstruction"
    obstruction_path = target.configuration["fixed_point_obstruction"]
    try:
        obstructions = load_fixed_point_obstructions(obstruction_path)
        report = validate_fixed_point_obstructions(obstructions)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [
            _rejected(
                subject,
                "fixed-point obstruction rejected: " + str(exc),
            )
        ]
    if report.accepted:
        return [_accepted(subject, "fixed-point obstruction accepted")]
    return [
        _rejected(
            subject,
            "fixed-point obstruction rejected: "
            + _joined_or_none(report.failed_subjects),
        )
    ]


def _failed_subject_for_result(subject: str) -> str:
    if subject.endswith(".willard_anchors"):
        return "target-willard-anchor"
    if subject.endswith(".configuration"):
        return "target-configuration"
    if subject.endswith(".consistency_level_target"):
        return "target-consistency-level-target"
    if subject.endswith(".diagonal_construction"):
        return "target-diagonal-construction"
    if subject.endswith(".substitution_representability"):
        return "target-substitution-representability"
    if subject.endswith(".substitution_graph"):
        return "target-substitution-graph"
    if subject.endswith(".substitution_graph_formula"):
        return "target-substitution-graph-formula"
    if subject.endswith(".fixed_point_equation_candidate"):
        return "target-fixed-point-equation-candidate"
    if subject.endswith(".fixed_point_obstruction"):
        return "target-fixed-point-obstruction"
    if subject.endswith(".blockers"):
        return "target-blockers"
    if subject.endswith(".status"):
        return "target-status"
    if subject.endswith(".next_as_action"):
        return "target-next-action"
    return "target-manifest"


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


def _required_text_list(
    item: dict[str, Any],
    key: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    values = item.get(key)
    if not isinstance(values, list) or (not values and not allow_empty):
        raise ValueError(f"required list field missing: {key}")
    text_values: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        text_values.append(value)
    return text_values


def _required_text_mapping(item: dict[str, Any], key: str) -> dict[str, str]:
    value = item.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required mapping field missing: {key}")
    result: dict[str, str] = {}
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key.strip():
            raise ValueError(f"{key} contains non-text key")
        if not isinstance(map_value, str):
            raise ValueError(f"{key} contains non-text value")
        result[map_key] = map_value
    return result


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> FormalConfidenceValidation:
    return FormalConfidenceValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> FormalConfidenceValidation:
    return FormalConfidenceValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_formal_confidence_cli())
