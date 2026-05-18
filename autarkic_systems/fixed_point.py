"""Checked fixed-point target surface for AS.

This module validates the first self-reference target template over the
existing formal codebook and capture-avoiding substitution machinery. It
checks that a template has the intended free code variable and that the
checked substitution instance matches the expected node and code. It does not
prove a diagonal lemma, construct a real quotation term, or claim
self-consistency.
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
from autarkic_systems.deduction_apparatus import (
    load_deduction_apparatus_targets,
    validate_deduction_apparatus_targets,
)
from autarkic_systems.formal_code import (
    decode_code,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_substitution import (
    free_variables,
    load_substitution_examples,
    substitute_node,
    validate_substitution_examples,
)
from autarkic_systems.formal_quotation import (
    load_quotation_examples,
    validate_quotation_examples,
)
from autarkic_systems.formal_quotation_sequence import (
    load_quotation_sequence_examples,
    validate_quotation_sequence_examples,
)
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_TARGETS = Path("claims/fixed_point_targets.json")
DEFAULT_FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.6-LEVEL-K-CONSISTENCY",
    "W2011-D5.7-SELFCONSK",
    "W2020-D3.2-SELF-JUSTIFYING-GENAC",
)
VALID_TARGET_STATUSES = {
    "target-selected-not-constructed",
}
SUPPORTED_SENTENCE_CLASS = "pi1"
REQUIRED_FUTURE_WORK = (
    "quotation-term-construction",
    "diagonal-lemma-proof",
    "fixed-point-equation-proof",
)


@dataclass(frozen=True)
class FixedPointTarget:
    """One selected fixed-point target template, not a proved fixed point."""

    target_id: str
    sentence_class: str
    template_variable: str
    template_node: dict[str, Any]
    quote_placeholder: dict[str, Any]
    expected_instance_node: dict[str, Any]
    expected_instance_code: tuple[int, ...]
    status: str
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointManifest:
    """Loaded manifest selecting the current AS fixed-point target."""

    path: Path
    schema_version: int
    target_set_id: str
    reviewed_at: str
    purpose: str
    codebook_path: str
    substitution_examples_path: str
    quotation_examples_path: str
    quotation_sequence_examples_path: str
    consistency_level_targets_path: str
    deduction_apparatus_targets_path: str
    willard_anchor_ids: tuple[str, ...]
    targets: tuple[FixedPointTarget, ...]


@dataclass(frozen=True)
class FixedPointValidation:
    """One validation result for fixed-point target selection."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointReport:
    """Validation report over fixed-point target templates."""

    manifest: FixedPointManifest
    codebook_path: Path
    substitution_examples_path: Path
    quotation_examples_path: Path
    quotation_sequence_examples_path: Path
    consistency_level_targets_path: Path
    deduction_apparatus_targets_path: Path
    formal_language_path: Path
    willard_map_path: Path
    results: tuple[FixedPointValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every fixed-point validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def target_count(self) -> int:
        """Return the number of checked fixed-point targets."""

        return len(self.manifest.targets)

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


def load_fixed_point_targets(
    path: Path | str = DEFAULT_TARGETS,
) -> FixedPointManifest:
    """Load fixed-point targets from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return FixedPointManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        target_set_id=_required_text(data, "target_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        codebook_path=_required_text(data, "codebook_path"),
        substitution_examples_path=_required_text(data, "substitution_examples_path"),
        quotation_examples_path=_required_text(data, "quotation_examples_path"),
        quotation_sequence_examples_path=_required_text(data, "quotation_sequence_examples_path"),
        consistency_level_targets_path=_required_text(data, "consistency_level_targets_path"),
        deduction_apparatus_targets_path=_required_text(data, "deduction_apparatus_targets_path"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        targets=tuple(_parse_target(item) for item in _required_list(data, "targets")),
    )


def validate_fixed_point_targets(
    manifest: FixedPointManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
    formal_language_path: Path | str = DEFAULT_FORMAL_LANGUAGE,
) -> FixedPointReport:
    """Validate fixed-point target templates against current dependencies."""

    checked_willard_map_path = Path(willard_map_path)
    checked_formal_language_path = Path(formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_substitution_path = Path(manifest.substitution_examples_path)
    checked_quotation_path = Path(manifest.quotation_examples_path)
    checked_quotation_sequence_path = Path(manifest.quotation_sequence_examples_path)
    checked_consistency_path = Path(manifest.consistency_level_targets_path)
    checked_deduction_path = Path(manifest.deduction_apparatus_targets_path)

    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_formal_language_path,
        checked_willard_map_path,
    )
    substitution = load_substitution_examples(checked_substitution_path)
    substitution_report = validate_substitution_examples(
        substitution,
        checked_codebook_path,
        checked_formal_language_path,
        checked_willard_map_path,
    )
    quotation = load_quotation_examples(checked_quotation_path)
    quotation_report = validate_quotation_examples(
        quotation,
        checked_codebook_path,
        checked_formal_language_path,
        checked_willard_map_path,
    )
    quotation_sequence = load_quotation_sequence_examples(checked_quotation_sequence_path)
    quotation_sequence_report = validate_quotation_sequence_examples(
        quotation_sequence,
        checked_codebook_path,
        checked_formal_language_path,
        checked_willard_map_path,
    )
    consistency = load_consistency_level_targets(checked_consistency_path)
    consistency_report = validate_consistency_level_targets(
        consistency,
        willard_map_path=checked_willard_map_path,
    )
    deduction = load_deduction_apparatus_targets(checked_deduction_path)
    deduction_report = validate_deduction_apparatus_targets(
        deduction,
        checked_willard_map_path,
        checked_formal_language_path,
    )

    results: list[FixedPointValidation] = [
        _accepted("manifest", f"loaded {len(manifest.targets)} target(s)")
    ]
    results.extend(_validate_willard_anchors(manifest, known_anchor_ids))
    results.extend(_validate_dependency_references(manifest))
    results.extend(
        _validate_dependency_reports(
            codebook_report,
            substitution_report,
            quotation_report,
            quotation_sequence_report,
            consistency_report,
            deduction_report,
        )
    )
    results.extend(_validate_targets(manifest.targets, codebook))

    return FixedPointReport(
        manifest=manifest,
        codebook_path=checked_codebook_path,
        substitution_examples_path=checked_substitution_path,
        quotation_examples_path=checked_quotation_path,
        quotation_sequence_examples_path=checked_quotation_sequence_path,
        consistency_level_targets_path=checked_consistency_path,
        deduction_apparatus_targets_path=checked_deduction_path,
        formal_language_path=checked_formal_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
    )


def fixed_point_report_payload(report: FixedPointReport) -> dict[str, Any]:
    """Return a JSON-ready fixed-point target validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "target_manifest": str(report.manifest.path),
        "target_set_id": report.manifest.target_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "codebook_path": str(report.codebook_path),
        "substitution_examples_path": str(report.substitution_examples_path),
        "quotation_examples_path": str(report.quotation_examples_path),
        "quotation_sequence_examples_path": str(report.quotation_sequence_examples_path),
        "consistency_level_targets_path": str(report.consistency_level_targets_path),
        "deduction_apparatus_targets_path": str(report.deduction_apparatus_targets_path),
        "formal_language_path": str(report.formal_language_path),
        "willard_map": str(report.willard_map_path),
        "willard_anchor_ids": list(report.manifest.willard_anchor_ids),
        "target_count": report.target_count,
        "failed_subjects": list(report.failed_subjects),
        "targets": [
            {
                "target_id": target.target_id,
                "sentence_class": target.sentence_class,
                "template_variable": target.template_variable,
                "template_node": target.template_node,
                "quote_placeholder": target.quote_placeholder,
                "expected_instance_node": target.expected_instance_node,
                "expected_instance_code": list(target.expected_instance_code),
                "status": target.status,
                "required_future_work": list(target.required_future_work),
                "non_claims": list(target.non_claims),
                "next_as_action": target.next_as_action,
            }
            for target in report.manifest.targets
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


def format_fixed_point_report(report: FixedPointReport) -> str:
    """Format a concise human-readable fixed-point target report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point targets: {status}",
        f"Target set: {report.manifest.target_set_id}",
        f"Targets: {report.target_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for target in report.manifest.targets:
        lines.extend([
            f"- {target.target_id}: {target.sentence_class}",
            f"  Template variable: {target.template_variable}",
            f"  Status: {target.status}",
            "  Future work: " + _joined_or_none(target.required_future_work),
            f"  Next AS action: {target.next_as_action}",
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_cli(argv: list[str] | None = None) -> int:
    """Run the fixed-point target validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point",
        description="Validate AS fixed-point target selection.",
    )
    parser.add_argument(
        "--targets",
        default=str(DEFAULT_TARGETS),
        help="Path to the fixed-point target manifest.",
    )
    parser.add_argument(
        "--formal-language",
        default=str(DEFAULT_FORMAL_LANGUAGE),
        help="Path to the formal arithmetic language manifest.",
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

    manifest = load_fixed_point_targets(args.targets)
    report = validate_fixed_point_targets(
        manifest,
        args.willard_map,
        args.formal_language,
    )
    if args.format == "json":
        print(json.dumps(fixed_point_report_payload(report), sort_keys=True))
    else:
        print(format_fixed_point_report(report))
    return 0 if report.accepted else 1


def _validate_willard_anchors(
    manifest: FixedPointManifest,
    known_anchor_ids: set[str],
) -> list[FixedPointValidation]:
    unknown_anchor_ids = sorted(set(manifest.willard_anchor_ids) - known_anchor_ids)
    missing_required = sorted(
        set(REQUIRED_WILLARD_ANCHORS) - set(manifest.willard_anchor_ids)
    )
    if unknown_anchor_ids:
        return [
            _rejected(
                "willard_anchors",
                "unknown Willard anchor IDs: " + ", ".join(unknown_anchor_ids),
            )
        ]
    if missing_required:
        return [
            _rejected(
                "willard_anchors",
                "missing required Willard anchors: " + ", ".join(missing_required),
            )
        ]
    return [_accepted("willard_anchors", "required anchors are present and known")]


def _validate_dependency_references(
    manifest: FixedPointManifest,
) -> list[FixedPointValidation]:
    expected = (
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "substitution_examples_path",
            manifest.substitution_examples_path,
            "language/formal_substitution_examples.json",
        ),
        (
            "quotation_examples_path",
            manifest.quotation_examples_path,
            "language/formal_quotation_examples.json",
        ),
        (
            "quotation_sequence_examples_path",
            manifest.quotation_sequence_examples_path,
            "language/formal_quotation_sequence_examples.json",
        ),
        (
            "consistency_level_targets_path",
            manifest.consistency_level_targets_path,
            "claims/consistency_level_targets.json",
        ),
        (
            "deduction_apparatus_targets_path",
            manifest.deduction_apparatus_targets_path,
            "claims/deduction_apparatus_targets.json",
        ),
    )
    results: list[FixedPointValidation] = []
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
    substitution_report: Any,
    quotation_report: Any,
    quotation_sequence_report: Any,
    consistency_report: Any,
    deduction_report: Any,
) -> list[FixedPointValidation]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        ("substitution", substitution_report, "formal substitution"),
        ("quotation", quotation_report, "formal quotation"),
        ("quotation_sequence", quotation_sequence_report, "formal quotation sequence"),
        ("consistency", consistency_report, "consistency-level target"),
        ("deduction", deduction_report, "deduction-apparatus target"),
    )
    results: list[FixedPointValidation] = []
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


def _validate_targets(
    targets: tuple[FixedPointTarget, ...],
    codebook: Any,
) -> list[FixedPointValidation]:
    if not targets:
        return [_rejected("targets", "no fixed-point targets")]

    results: list[FixedPointValidation] = []
    target_ids = [target.target_id for target in targets]
    duplicate_ids = _duplicates(target_ids)
    if duplicate_ids:
        results.append(
            _rejected("targets.target_id", "duplicate target ids: " + ", ".join(duplicate_ids))
        )
    else:
        results.append(_accepted("targets.target_id", "target ids are unique"))

    for target in targets:
        results.extend(_validate_target(target, codebook))
    results.append(_accepted("targets", f"checked {len(targets)} target(s)"))
    return results


def _validate_target(
    target: FixedPointTarget,
    codebook: Any,
) -> list[FixedPointValidation]:
    results: list[FixedPointValidation] = []
    target_label = target.target_id

    if target.sentence_class != SUPPORTED_SENTENCE_CLASS:
        results.append(
            _rejected(
                f"{target_label}.sentence_class",
                f"unsupported sentence class: {target.sentence_class}",
            )
        )
    elif target.template_node.get("kind") != SUPPORTED_SENTENCE_CLASS:
        results.append(
            _rejected(
                f"{target_label}.sentence_class",
                "template node is not pi1",
            )
        )
    else:
        results.append(_accepted(f"{target_label}.sentence_class", "pi1 target"))

    template_free_variables = free_variables(target.template_node)
    if target.template_variable not in template_free_variables:
        results.append(
            _rejected(
                f"{target_label}.template_variable",
                f"template variable {target.template_variable} is not free",
            )
        )
    else:
        results.append(
            _accepted(
                f"{target_label}.template_variable",
                "template variable is free",
            )
        )

    if target.status == "fixed-point-proved":
        results.append(
            _rejected(
                f"{target_label}.status",
                "proved fixed points are not supported",
            )
        )
    elif target.status not in VALID_TARGET_STATUSES:
        results.append(
            _rejected(f"{target_label}.status", f"unknown status: {target.status}")
        )
    else:
        results.append(_accepted(f"{target_label}.status", "status preserves non-claim"))

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in target.required_future_work
    ]
    if missing_future_work:
        results.append(
            _rejected(
                f"{target_label}.required_future_work",
                "missing future work: " + ", ".join(missing_future_work),
            )
        )
    else:
        results.append(
            _accepted(f"{target_label}.required_future_work", "future work is explicit")
        )

    if not target.non_claims:
        results.append(_rejected(f"{target_label}.non_claims", "non-claims must be explicit"))
    else:
        results.append(_accepted(f"{target_label}.non_claims", "non-claims are explicit"))

    results.extend(_validate_instance(target, codebook))
    return results


def _validate_instance(
    target: FixedPointTarget,
    codebook: Any,
) -> list[FixedPointValidation]:
    target_label = target.target_id
    try:
        instance = substitute_node(
            target.template_node,
            target.template_variable,
            target.quote_placeholder,
        )
    except ValueError as exc:
        return [_rejected(f"{target_label}.instance", str(exc))]

    if instance != target.expected_instance_node:
        return [_rejected(f"{target_label}.instance", "expected instance node mismatch")]

    encoded = encode_node(instance, codebook)
    if encoded != target.expected_instance_code:
        return [
            _rejected(
                f"{target_label}.instance",
                "expected instance code mismatch: expected "
                + _format_code(target.expected_instance_code)
                + " got "
                + _format_code(encoded),
            )
        ]

    try:
        decoded = decode_code(target.expected_instance_code, codebook)
    except ValueError as exc:
        return [_rejected(f"{target_label}.instance", str(exc))]
    if decoded != target.expected_instance_node:
        return [
            _rejected(
                f"{target_label}.instance",
                "expected instance code did not decode to expected node",
            )
        ]
    return [_accepted(f"{target_label}.instance", "substitution instance validated")]


def _parse_target(item: dict[str, Any]) -> FixedPointTarget:
    return FixedPointTarget(
        target_id=_required_text(item, "target_id"),
        sentence_class=_required_text(item, "sentence_class"),
        template_variable=_required_text(item, "template_variable"),
        template_node=_required_node(item, "template_node"),
        quote_placeholder=_required_node(item, "quote_placeholder"),
        expected_instance_node=_required_node(item, "expected_instance_node"),
        expected_instance_code=tuple(_required_int_list(item, "expected_instance_code")),
        status=_required_text(item, "status"),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "fixed-point-willard-anchor"
    if subject.endswith(".template_variable"):
        return "fixed-point-template-variable"
    if subject.endswith(".instance"):
        return "fixed-point-instance"
    if subject.endswith(".status"):
        return "fixed-point-status"
    if subject.endswith(".sentence_class"):
        return "fixed-point-sentence-class"
    if subject in {
        "codebook",
        "substitution",
        "quotation",
        "quotation_sequence",
        "consistency",
        "deduction",
    }:
        return "fixed-point-dependency"
    if subject in {
        "codebook_path",
        "substitution_examples_path",
        "quotation_examples_path",
        "quotation_sequence_examples_path",
        "consistency_level_targets_path",
        "deduction_apparatus_targets_path",
    }:
        return "fixed-point-reference"
    if subject.startswith("targets"):
        return "fixed-point-target"
    if subject.startswith("AS-FIXED-POINT"):
        return "fixed-point-target"
    return "fixed-point-manifest"


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
    text_values: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        text_values.append(value)
    return text_values


def _required_node(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required node field missing: {key}")
    return value


def _required_int_list(item: dict[str, Any], key: str) -> list[int]:
    value = item.get(key)
    if not isinstance(value, list):
        raise ValueError(f"required integer list missing: {key}")
    result: list[int] = []
    for list_item in value:
        if not isinstance(list_item, int) or isinstance(list_item, bool):
            raise ValueError(f"{key} contains non-integer item")
        result.append(list_item)
    return result


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _format_code(code: tuple[int, ...]) -> str:
    return "[" + ", ".join(str(item) for item in code) + "]"


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> FixedPointValidation:
    return FixedPointValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> FixedPointValidation:
    return FixedPointValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_fixed_point_cli())
