"""Checked deduction-apparatus target selection for AS.

This module selects the current AS-local proof-certificate checker as the
deduction-apparatus target for the executable substrate surfaces. It validates
that the transition, transition-chain, and network-sequence certificate
manifests are still using `predicate-result` steps. It deliberately does not
claim Hilbert completeness, tableau proof search, an arithmetized proof
predicate, or self-justification.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.chain_object_language import (
    validate_transition_chain_claim_language_project,
)
from autarkic_systems.formal_code import load_formal_codebook, validate_formal_codebook
from autarkic_systems.network_sequence_object_language import (
    validate_network_sequence_claim_language_project,
)
from autarkic_systems.object_language import validate_transition_claim_language_project
from autarkic_systems.proof_certificates import (
    MANIFEST_EXAMPLE_RULE,
    PREDICATE_RESULT_RULE,
    load_proof_certificates,
)
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_TARGETS = Path("claims/deduction_apparatus_targets.json")
DEFAULT_FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2016-D3.2-HILBERT-STYLE",
    "W2016-D3.4-SELF-JUSTIFYING-CONFIGURATION",
    "W2020-D3.2-SELF-JUSTIFYING-GENAC",
    "W2020-SEC4-TAB-XTAB-TAB1",
    "W2020-T4.4-T4.5-LEM-BOUNDARY",
)
REQUIRED_CERTIFICATE_SURFACES = (
    "transition",
    "transition-chain",
    "network-sequence",
)
VALID_TARGET_STATUSES = {
    "target-selected-not-self-justifying",
}
SUPPORTED_APPARATUS_ID = "as-local-predicate-result-proof-certificate-checker"
SUPPORTED_FAMILY = "as-local-certificate-checker"
DISALLOWED_SELECTED_FAMILIES = {
    "hilbert-style",
    "semantic-tableau",
    "xtab",
    "tab-1",
}
PROOF_RULE_REPORT_ORDER = (
    PREDICATE_RESULT_RULE,
    MANIFEST_EXAMPLE_RULE,
)
PROOF_RULE_BASELINE_ORDER = (
    MANIFEST_EXAMPLE_RULE,
    PREDICATE_RESULT_RULE,
)


@dataclass(frozen=True)
class DeductionApparatusTarget:
    """One selected deduction-apparatus target, not a self-justification claim."""

    target_id: str
    apparatus_id: str
    family: str
    rule: str
    status: str
    proof_code_status: str
    selected_for: tuple[str, ...]
    excluded_apparatuses: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class CertificateSurface:
    """One substrate certificate surface covered by the apparatus target."""

    surface_id: str
    language_path: str
    claims_path: str
    certificates_path: str
    required_rule: str


@dataclass(frozen=True)
class DeductionApparatusManifest:
    """Loaded manifest selecting the current AS deduction-apparatus target."""

    path: Path
    schema_version: int
    target_set_id: str
    reviewed_at: str
    purpose: str
    formal_codebook_path: str
    willard_anchor_ids: tuple[str, ...]
    targets: tuple[DeductionApparatusTarget, ...]
    certificate_surfaces: tuple[CertificateSurface, ...]


@dataclass(frozen=True)
class SurfaceRuleSummary:
    """Rule-count summary for one checked certificate surface."""

    surface_id: str
    certificates_path: str
    accepted: bool
    step_count: int
    rule_counts: dict[str, int]
    failed_subjects: tuple[str, ...]


@dataclass(frozen=True)
class DeductionApparatusValidation:
    """One validation result for deduction-apparatus target selection."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class DeductionApparatusReport:
    """Validation report over the deduction-apparatus target surface."""

    manifest: DeductionApparatusManifest
    willard_map_path: Path
    formal_language_path: Path
    formal_codebook_path: Path
    surface_rule_summaries: tuple[SurfaceRuleSummary, ...]
    results: tuple[DeductionApparatusValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every deduction-apparatus validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def target_count(self) -> int:
        """Return the number of checked deduction-apparatus targets."""

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

    @property
    def total_step_count(self) -> int:
        """Return the total certificate steps covered by the apparatus target."""

        return sum(summary.step_count for summary in self.surface_rule_summaries)

    @property
    def combined_rule_counts(self) -> dict[str, int]:
        """Return combined proof-rule counts across all covered surfaces."""

        counts = _empty_rule_counts()
        for summary in self.surface_rule_summaries:
            for rule, count in summary.rule_counts.items():
                counts[rule] = counts.get(rule, 0) + count
        return counts


def load_deduction_apparatus_targets(
    path: Path | str = DEFAULT_TARGETS,
) -> DeductionApparatusManifest:
    """Load deduction-apparatus targets from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return DeductionApparatusManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        target_set_id=_required_text(data, "target_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_codebook_path=_required_text(data, "formal_codebook_path"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        targets=tuple(_parse_target(item) for item in _required_list(data, "targets")),
        certificate_surfaces=tuple(
            _parse_surface(item)
            for item in _required_list(data, "certificate_surfaces")
        ),
    )


def validate_deduction_apparatus_targets(
    manifest: DeductionApparatusManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
    formal_language_path: Path | str = DEFAULT_FORMAL_LANGUAGE,
) -> DeductionApparatusReport:
    """Validate the selected apparatus target against current proof surfaces."""

    checked_willard_map_path = Path(willard_map_path)
    checked_formal_language_path = Path(formal_language_path)
    checked_formal_codebook_path = Path(manifest.formal_codebook_path)

    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}
    codebook = load_formal_codebook(checked_formal_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_formal_language_path,
        checked_willard_map_path,
    )

    results: list[DeductionApparatusValidation] = [
        _accepted("manifest", f"loaded {len(manifest.targets)} target(s)")
    ]
    results.extend(_validate_willard_anchors(manifest, known_anchor_ids))
    results.extend(_validate_formal_codebook_report(codebook_report))
    results.extend(_validate_targets(manifest.targets))
    target_rule = manifest.targets[0].rule if manifest.targets else PREDICATE_RESULT_RULE
    surface_rule_summaries, surface_results = _validate_certificate_surfaces(
        manifest.certificate_surfaces,
        target_rule,
    )
    results.extend(surface_results)

    return DeductionApparatusReport(
        manifest=manifest,
        willard_map_path=checked_willard_map_path,
        formal_language_path=checked_formal_language_path,
        formal_codebook_path=checked_formal_codebook_path,
        surface_rule_summaries=tuple(surface_rule_summaries),
        results=tuple(results),
    )


def deduction_apparatus_report_payload(
    report: DeductionApparatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready deduction-apparatus validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "target_manifest": str(report.manifest.path),
        "target_set_id": report.manifest.target_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "formal_codebook_path": str(report.formal_codebook_path),
        "willard_map": str(report.willard_map_path),
        "willard_anchor_ids": list(report.manifest.willard_anchor_ids),
        "target_count": report.target_count,
        "failed_subjects": list(report.failed_subjects),
        "total_step_count": report.total_step_count,
        "combined_rule_counts": report.combined_rule_counts,
        "targets": [
            {
                "target_id": target.target_id,
                "apparatus_id": target.apparatus_id,
                "family": target.family,
                "rule": target.rule,
                "status": target.status,
                "proof_code_status": target.proof_code_status,
                "selected_for": list(target.selected_for),
                "excluded_apparatuses": list(target.excluded_apparatuses),
                "non_claims": list(target.non_claims),
                "next_as_action": target.next_as_action,
            }
            for target in report.manifest.targets
        ],
        "certificate_surfaces": [
            {
                "surface_id": summary.surface_id,
                "certificates_path": summary.certificates_path,
                "accepted": summary.accepted,
                "step_count": summary.step_count,
                "rule_counts": summary.rule_counts,
                "failed_subjects": list(summary.failed_subjects),
            }
            for summary in report.surface_rule_summaries
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


def format_deduction_apparatus_report(report: DeductionApparatusReport) -> str:
    """Format a concise human-readable deduction-apparatus report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Deduction apparatus targets: {status}",
        f"Target set: {report.manifest.target_set_id}",
        f"Targets: {report.target_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
        f"Rule counts: {_format_rule_counts(report.combined_rule_counts)}",
    ]
    for target in report.manifest.targets:
        lines.extend([
            f"- {target.target_id}: {target.apparatus_id}",
            f"  Family: {target.family}",
            f"  Rule: {target.rule}",
            f"  Status: {target.status}",
            f"  Next AS action: {target.next_as_action}",
        ])
    lines.append("Certificate surfaces:")
    for summary in report.surface_rule_summaries:
        surface_status = "accepted" if summary.accepted else "rejected"
        lines.append(
            f"- {summary.surface_id}: {surface_status}; "
            f"steps={summary.step_count}; "
            f"rules={_format_rule_counts(summary.rule_counts)}"
        )
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_deduction_apparatus_cli(argv: list[str] | None = None) -> int:
    """Run the deduction-apparatus target validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.deduction_apparatus",
        description="Validate AS deduction-apparatus target selection.",
    )
    parser.add_argument(
        "--targets",
        default=str(DEFAULT_TARGETS),
        help="Path to the deduction-apparatus target manifest.",
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

    manifest = load_deduction_apparatus_targets(args.targets)
    report = validate_deduction_apparatus_targets(
        manifest,
        args.willard_map,
        args.formal_language,
    )
    if args.format == "json":
        print(json.dumps(deduction_apparatus_report_payload(report), sort_keys=True))
    else:
        print(format_deduction_apparatus_report(report))
    return 0 if report.accepted else 1


def _validate_willard_anchors(
    manifest: DeductionApparatusManifest,
    known_anchor_ids: set[str],
) -> list[DeductionApparatusValidation]:
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


def _validate_formal_codebook_report(
    codebook_report: Any,
) -> list[DeductionApparatusValidation]:
    if codebook_report.accepted:
        return [_accepted("formal_codebook", "formal codebook accepted")]
    return [
        _rejected(
            "formal_codebook",
            "formal codebook rejected: "
            + _joined_or_none(codebook_report.failed_subjects),
        )
    ]


def _validate_targets(
    targets: tuple[DeductionApparatusTarget, ...],
) -> list[DeductionApparatusValidation]:
    if not targets:
        return [_rejected("targets", "no deduction-apparatus targets")]

    results: list[DeductionApparatusValidation] = []
    target_ids = [target.target_id for target in targets]
    duplicate_ids = _duplicates(target_ids)
    if duplicate_ids:
        results.append(
            _rejected("targets.target_id", "duplicate target ids: " + ", ".join(duplicate_ids))
        )
    else:
        results.append(_accepted("targets.target_id", "target ids are unique"))

    for target in targets:
        results.extend(_validate_target(target))
    return results


def _validate_target(
    target: DeductionApparatusTarget,
) -> list[DeductionApparatusValidation]:
    results: list[DeductionApparatusValidation] = []
    target_label = target.target_id

    if target.apparatus_id != SUPPORTED_APPARATUS_ID:
        results.append(
            _rejected(
                f"{target_label}.apparatus_id",
                f"unsupported apparatus: {target.apparatus_id}",
            )
        )
    else:
        results.append(_accepted(f"{target_label}.apparatus_id", "apparatus selected"))

    if target.family in DISALLOWED_SELECTED_FAMILIES:
        results.append(
            _rejected(
                f"{target_label}.family",
                "Hilbert/tableau apparatus overclaim: " + target.family,
            )
        )
    elif target.family != SUPPORTED_FAMILY:
        results.append(
            _rejected(f"{target_label}.family", f"unsupported family: {target.family}")
        )
    else:
        results.append(_accepted(f"{target_label}.family", "local family selected"))

    if target.rule != PREDICATE_RESULT_RULE:
        results.append(
            _rejected(
                f"{target_label}.rule",
                f"unsupported proof rule: {target.rule}",
            )
        )
    else:
        results.append(_accepted(f"{target_label}.rule", "predicate-result selected"))

    if target.status == "self-justifying-proved":
        results.append(
            _rejected(
                f"{target_label}.status",
                "self-justifying status is not supported",
            )
        )
    elif target.status not in VALID_TARGET_STATUSES:
        results.append(
            _rejected(f"{target_label}.status", f"unknown status: {target.status}")
        )
    else:
        results.append(_accepted(f"{target_label}.status", "status preserves non-claim"))

    missing_surfaces = sorted(set(REQUIRED_CERTIFICATE_SURFACES) - set(target.selected_for))
    if missing_surfaces:
        results.append(
            _rejected(
                f"{target_label}.selected_for",
                "missing selected surfaces: " + ", ".join(missing_surfaces),
            )
        )
    else:
        results.append(_accepted(f"{target_label}.selected_for", "target covers required surfaces"))

    missing_exclusions = sorted(
        DISALLOWED_SELECTED_FAMILIES - set(target.excluded_apparatuses)
    )
    if missing_exclusions:
        results.append(
            _rejected(
                f"{target_label}.excluded_apparatuses",
                "missing overclaim exclusions: " + ", ".join(missing_exclusions),
            )
        )
    else:
        results.append(_accepted(f"{target_label}.excluded_apparatuses", "overclaim exclusions are explicit"))

    if not target.non_claims:
        results.append(_rejected(f"{target_label}.non_claims", "non-claims must be explicit"))
    else:
        results.append(_accepted(f"{target_label}.non_claims", "non-claims are explicit"))
    return results


def _validate_certificate_surfaces(
    surfaces: tuple[CertificateSurface, ...],
    target_rule: str,
) -> tuple[list[SurfaceRuleSummary], list[DeductionApparatusValidation]]:
    summaries: list[SurfaceRuleSummary] = []
    results: list[DeductionApparatusValidation] = []

    surface_ids = [surface.surface_id for surface in surfaces]
    missing_surfaces = sorted(set(REQUIRED_CERTIFICATE_SURFACES) - set(surface_ids))
    duplicate_surfaces = _duplicates(surface_ids)
    if missing_surfaces:
        results.append(
            _rejected(
                "certificate_surfaces",
                "missing certificate surfaces: " + ", ".join(missing_surfaces),
            )
        )
    elif duplicate_surfaces:
        results.append(
            _rejected(
                "certificate_surfaces",
                "duplicate certificate surfaces: " + ", ".join(duplicate_surfaces),
            )
        )
    else:
        results.append(_accepted("certificate_surfaces", "required surfaces present"))

    for surface in surfaces:
        surface_summary, surface_results = _validate_certificate_surface(
            surface,
            target_rule,
        )
        summaries.append(surface_summary)
        results.extend(surface_results)
    return summaries, results


def _validate_certificate_surface(
    surface: CertificateSurface,
    target_rule: str,
) -> tuple[SurfaceRuleSummary, list[DeductionApparatusValidation]]:
    results: list[DeductionApparatusValidation] = []
    subject = f"{surface.surface_id}.surface"

    if surface.surface_id not in REQUIRED_CERTIFICATE_SURFACES:
        results.append(_rejected(subject, f"unknown certificate surface: {surface.surface_id}"))

    if surface.required_rule != target_rule:
        results.append(
            _rejected(
                f"{surface.surface_id}.required_rule",
                f"required rule {surface.required_rule} does not match target {target_rule}",
            )
        )
    elif surface.required_rule != PREDICATE_RESULT_RULE:
        results.append(
            _rejected(
                f"{surface.surface_id}.required_rule",
                f"unsupported required rule: {surface.required_rule}",
            )
        )
    else:
        results.append(
            _accepted(
                f"{surface.surface_id}.required_rule",
                "predicate-result required",
            )
        )

    project_result = _validate_surface_project(surface)
    results.append(project_result)
    rule_summary = _surface_rule_summary(surface)

    non_required_rules = sorted(
        rule
        for rule, count in rule_summary.rule_counts.items()
        if rule != PREDICATE_RESULT_RULE and count
    )
    if non_required_rules:
        results.append(
            _rejected(
                f"{surface.surface_id}.proof_rules",
                "non-predicate-result rules: " + ", ".join(non_required_rules),
            )
        )
    else:
        results.append(
            _accepted(
                f"{surface.surface_id}.proof_rules",
                f"{rule_summary.step_count} predicate-result step(s)",
            )
        )
    return rule_summary, results


def _validate_surface_project(surface: CertificateSurface) -> DeductionApparatusValidation:
    try:
        if surface.surface_id == "transition":
            report = validate_transition_claim_language_project(
                surface.language_path,
                surface.claims_path,
                surface.certificates_path,
            )
        elif surface.surface_id == "transition-chain":
            report = validate_transition_chain_claim_language_project(
                surface.language_path,
                surface.claims_path,
                surface.certificates_path,
            )
        elif surface.surface_id == "network-sequence":
            report = validate_network_sequence_claim_language_project(
                surface.language_path,
                surface.claims_path,
                surface.certificates_path,
            )
        else:
            return _rejected(
                f"{surface.surface_id}.project",
                f"unknown certificate surface: {surface.surface_id}",
            )
    except Exception as exc:
        return _rejected(
            f"{surface.surface_id}.project",
            f"{type(exc).__name__}: {exc}",
        )

    failed_subjects = [
        result.subject for result in report.results if not result.accepted
    ]
    if failed_subjects:
        return _rejected(
            f"{surface.surface_id}.project",
            "surface rejected: " + ", ".join(failed_subjects),
        )
    return _accepted(
        f"{surface.surface_id}.project",
        f"{report.claim_count} claim(s), {report.certificate_count} certificate(s)",
    )


def _surface_rule_summary(surface: CertificateSurface) -> SurfaceRuleSummary:
    path = Path(surface.certificates_path)
    try:
        certificates = load_proof_certificates(path)
    except Exception as exc:
        return SurfaceRuleSummary(
            surface_id=surface.surface_id,
            certificates_path=str(path),
            accepted=False,
            step_count=0,
            rule_counts=_empty_rule_counts(),
            failed_subjects=(f"{type(exc).__name__}: {exc}",),
        )

    counts = _empty_rule_counts()
    step_count = 0
    for certificate in certificates:
        for step in certificate.steps:
            step_count += 1
            counts[step.rule] = counts.get(step.rule, 0) + 1
    failed_subjects = tuple(
        rule
        for rule, count in counts.items()
        if rule != PREDICATE_RESULT_RULE and count
    )
    return SurfaceRuleSummary(
        surface_id=surface.surface_id,
        certificates_path=str(path),
        accepted=not failed_subjects,
        step_count=step_count,
        rule_counts=counts,
        failed_subjects=failed_subjects,
    )


def _parse_target(item: dict[str, Any]) -> DeductionApparatusTarget:
    return DeductionApparatusTarget(
        target_id=_required_text(item, "target_id"),
        apparatus_id=_required_text(item, "apparatus_id"),
        family=_required_text(item, "family"),
        rule=_required_text(item, "rule"),
        status=_required_text(item, "status"),
        proof_code_status=_required_text(item, "proof_code_status"),
        selected_for=tuple(_required_text_list(item, "selected_for")),
        excluded_apparatuses=tuple(_required_text_list(item, "excluded_apparatuses")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _parse_surface(item: dict[str, Any]) -> CertificateSurface:
    return CertificateSurface(
        surface_id=_required_text(item, "surface_id"),
        language_path=_required_text(item, "language_path"),
        claims_path=_required_text(item, "claims_path"),
        certificates_path=_required_text(item, "certificates_path"),
        required_rule=_required_text(item, "required_rule"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "deduction-apparatus-willard-anchor"
    if subject.endswith(".proof_rules") or subject.endswith(".rule") or subject.endswith(".required_rule"):
        return "deduction-apparatus-proof-rule"
    if subject == "certificate_surfaces" or subject.endswith(".surface") or subject.endswith(".project"):
        return "deduction-apparatus-surface"
    if subject.endswith(".family"):
        return "deduction-apparatus-family"
    if subject.endswith(".status"):
        return "deduction-apparatus-status"
    if subject == "formal_codebook":
        return "deduction-apparatus-dependency"
    if subject.startswith("targets"):
        return "deduction-apparatus-target"
    return "deduction-apparatus-manifest"


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


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _empty_rule_counts() -> dict[str, int]:
    return {rule: 0 for rule in PROOF_RULE_BASELINE_ORDER}


def _format_rule_counts(counts: dict[str, int]) -> str:
    return ", ".join(
        f"{rule}={counts.get(rule, 0)}" for rule in PROOF_RULE_REPORT_ORDER
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> DeductionApparatusValidation:
    return DeductionApparatusValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> DeductionApparatusValidation:
    return DeductionApparatusValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_deduction_apparatus_cli())
