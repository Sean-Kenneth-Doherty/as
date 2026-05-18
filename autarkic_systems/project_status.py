"""Operator-facing project status over the current AS evidence surface.

The project has separate validators for transition evidence bundles,
transition-chain evidence bundles, and source-status records that explain why
some command-token semantics remain blocked. This module gathers those
existing artifacts into one report while also enforcing the shared
source-status frontier schema used by the focused source-status CLI.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from autarkic_systems.chain_evidence_bundle import (
    chain_registry_validation_report_payload,
    load_chain_evidence_bundle_registry,
    validate_chain_evidence_bundle_registry,
)
from autarkic_systems.chain_claims import (
    chain_claim_validation_report_payload,
    validate_transition_chain_claim_project,
)
from autarkic_systems.chain_object_language import (
    transition_chain_claim_language_report_payload,
    validate_transition_chain_claim_language_project,
)
from autarkic_systems.claim_manifest import (
    transition_claim_report_payload,
    validate_transition_claim_project,
)
from autarkic_systems.evidence_bundle import (
    load_evidence_bundle_registry,
    registry_validation_report_payload,
    validate_evidence_bundle_registry,
)
from autarkic_systems.network_sequence_evidence_bundle import (
    load_network_sequence_evidence_bundle_registry,
    network_sequence_registry_validation_report_payload,
    validate_network_sequence_evidence_bundle_registry,
)
from autarkic_systems.object_language import (
    transition_claim_language_report_payload,
    validate_transition_claim_language_project,
)
from autarkic_systems.proof_certificates import (
    MANIFEST_EXAMPLE_RULE,
    PREDICATE_RESULT_RULE,
    load_proof_certificates,
    proof_certificate_report_payload,
    validate_proof_certificate_project,
)


DEFAULT_TRANSITION_REGISTRY = Path("evidence/manifest.json")
DEFAULT_CHAIN_REGISTRY = Path("evidence/chains/manifest.json")
DEFAULT_SEQUENCE_REGISTRY = Path("evidence/sequences/manifest.json")
DEFAULT_TRANSITION_LANGUAGE = Path("language/transition_claim_language.json")
DEFAULT_TRANSITION_CLAIMS = Path("claims/transition_claims.json")
DEFAULT_TRANSITION_CERTIFICATES = Path("claims/proof_certificates.json")
DEFAULT_CHAIN_LANGUAGE = Path("language/transition_chain_claim_language.json")
DEFAULT_CHAIN_CLAIMS = Path("claims/transition_chain_claims.json")
DEFAULT_CHAIN_CERTIFICATES = Path("claims/transition_chain_proof_certificates.json")
DEFAULT_SOURCE_STATUS_PATHS = (
    Path("sources/recipient_non_init_command_source_status.json"),
    Path("sources/standard_signal_command_semantics_status.json"),
    Path("sources/write_buffer_command_semantics_status.json"),
)
PROJECT_STATUS_SCHEMA_VERSION = 17
PROOF_RULE_TEXT_ORDER = (
    PREDICATE_RESULT_RULE,
    MANIFEST_EXAMPLE_RULE,
)
PROOF_RULE_BASELINE_ORDER = (
    MANIFEST_EXAMPLE_RULE,
    PREDICATE_RESULT_RULE,
)
BLOCKED_COMMAND_ORDER = (
    "standard-signal",
    "write-buf-zero",
    "write-buf-one",
)


def build_project_status_report(
    transition_registry_path: Path | str = DEFAULT_TRANSITION_REGISTRY,
    chain_registry_path: Path | str = DEFAULT_CHAIN_REGISTRY,
    sequence_registry_path: Path | str = DEFAULT_SEQUENCE_REGISTRY,
    transition_language_path: Path | str = DEFAULT_TRANSITION_LANGUAGE,
    transition_claims_path: Path | str = DEFAULT_TRANSITION_CLAIMS,
    transition_certificates_path: Path | str = DEFAULT_TRANSITION_CERTIFICATES,
    chain_language_path: Path | str = DEFAULT_CHAIN_LANGUAGE,
    chain_claims_path: Path | str = DEFAULT_CHAIN_CLAIMS,
    chain_certificates_path: Path | str = DEFAULT_CHAIN_CERTIFICATES,
    source_status_paths: list[Path | str] | tuple[Path | str, ...] = DEFAULT_SOURCE_STATUS_PATHS,
) -> dict[str, Any]:
    """Build a status report from registries and source-status records."""

    transition_summary = _transition_registry_summary(transition_registry_path)
    chain_summary = _chain_registry_summary(chain_registry_path)
    sequence_summary = _sequence_registry_summary(sequence_registry_path)
    transition_claims = _transition_claim_summary(transition_claims_path)
    transition_proof_certificates = _transition_proof_certificate_summary(
        transition_claims_path,
        transition_certificates_path,
    )
    chain_claims = _chain_claim_summary(
        chain_language_path,
        chain_claims_path,
        chain_certificates_path,
    )
    proof_rule_audit = _proof_rule_audit_summary(
        transition_certificates_path,
        chain_certificates_path,
    )
    transition_language = _transition_language_summary(
        transition_language_path,
        transition_claims_path,
        transition_certificates_path,
    )
    chain_language = _chain_language_summary(
        chain_language_path,
        chain_claims_path,
        chain_certificates_path,
    )
    frontier = _frontier_summary(source_status_paths)
    accepted = (
        transition_summary["accepted"]
        and chain_summary["accepted"]
        and sequence_summary["accepted"]
        and transition_claims["accepted"]
        and transition_proof_certificates["accepted"]
        and chain_claims["accepted"]
        and proof_rule_audit["accepted"]
        and transition_language["accepted"]
        and chain_language["accepted"]
        and not frontier["missing_source_statuses"]
        and not frontier["invalid_source_statuses"]
    )
    return {
        "schema_version": PROJECT_STATUS_SCHEMA_VERSION,
        "accepted": accepted,
        "transition_evidence": transition_summary,
        "chain_evidence": chain_summary,
        "sequence_evidence": sequence_summary,
        "transition_claims": transition_claims,
        "transition_proof_certificates": transition_proof_certificates,
        "chain_claims": chain_claims,
        "proof_rule_audit": proof_rule_audit,
        "transition_language": transition_language,
        "chain_language": chain_language,
        "frontier": frontier,
    }


def format_project_status_report(report: dict[str, Any]) -> str:
    """Format a concise human-readable project status report."""

    status = "accepted" if report["accepted"] else "rejected"
    transition = report["transition_evidence"]
    chain = report["chain_evidence"]
    sequence = report["sequence_evidence"]
    transition_claims = report["transition_claims"]
    transition_proof_certificates = report["transition_proof_certificates"]
    chain_claims = report["chain_claims"]
    proof_rule_audit = report["proof_rule_audit"]
    transition_language = report["transition_language"]
    chain_language = report["chain_language"]
    frontier = report["frontier"]
    transition_status = "accepted" if transition["accepted"] else "rejected"
    chain_status = "accepted" if chain["accepted"] else "rejected"
    sequence_status = "accepted" if sequence["accepted"] else "rejected"
    blocked_commands = frontier["blocked_commands"] or []
    missing_registries = [
        summary["path"]
        for summary in (transition, chain, sequence)
        if "registry-file" in summary["failed_subjects"]
    ]
    invalid_registries = [
        summary["path"]
        for summary in (transition, chain, sequence)
        if "registry-json" in summary["failed_subjects"]
    ]
    missing = frontier["missing_source_statuses"] or []
    invalid = [
        f"{item['path']}: {item['error']}"
        for item in frontier["invalid_source_statuses"]
    ]
    lines = [
        f"Autarkic Systems project status: {status}",
        f"Transition evidence: {transition_status} ({transition['bundle_count']} bundles)",
        f"Chain evidence: {chain_status} ({chain['bundle_count']} bundles)",
        (
            f"Network sequence evidence: {sequence_status} "
            f"({_bundle_count_text(sequence['bundle_count'])})"
        ),
        _transition_claim_text_line(transition_claims),
        _transition_proof_certificate_text_line(transition_proof_certificates),
        *_claim_proof_failure_text_lines(
            transition_claims,
            transition_proof_certificates,
        ),
        _chain_claim_text_line(chain_claims),
        *_chain_claim_failure_text_lines(chain_claims),
        _proof_rule_audit_text_line(proof_rule_audit),
        _language_text_line("Transition language", transition_language),
        _language_text_line("Chain language", chain_language),
        *_language_failure_text_lines(transition_language, chain_language),
        *_registry_bundle_text_lines("Transition evidence", transition),
        *_registry_bundle_text_lines("Chain evidence", chain),
        *_registry_bundle_text_lines("Network sequence evidence", sequence),
        "Blocked commands: "
        + (", ".join(blocked_commands) if blocked_commands else "none"),
        *_blocked_runtime_surface_text_lines(frontier),
        *_as_boundary_text_lines(frontier),
        *_execution_readiness_text_lines(frontier),
        *_resolution_question_text_lines(frontier),
        *_resolution_question_evidence_text_lines(frontier),
        *_resolved_resolution_question_text_lines(frontier),
        *_additional_source_status_text_lines(frontier),
        f"Safe next slice: {frontier['safe_next_slice'] or 'none'}",
        "Missing registry files: "
        + (", ".join(missing_registries) if missing_registries else "none"),
        "Invalid registry files: "
        + (", ".join(invalid_registries) if invalid_registries else "none"),
        "Missing source-status files: "
        + (", ".join(missing) if missing else "none"),
    ]
    if invalid:
        lines.append(f"Invalid source-status files: {', '.join(invalid)}")
    return "\n".join(lines)


def format_project_status_summary(report: dict[str, Any]) -> str:
    """Format the compact operator summary for the current status payload."""

    status = "accepted" if report["accepted"] else "rejected"
    transition = report["transition_evidence"]
    chain = report["chain_evidence"]
    sequence = report["sequence_evidence"]
    transition_claims = report["transition_claims"]
    chain_claims = report["chain_claims"]
    proof_rule_audit = report["proof_rule_audit"]
    frontier = report["frontier"]
    blocked_commands = frontier["blocked_commands"] or []
    return "\n".join([
        f"Autarkic Systems summary: {status}",
        (
            f"Evidence: {transition['bundle_count']} transition bundles; "
            f"{chain['bundle_count']} chain bundles; "
            f"{sequence['bundle_count']} sequence "
            f"{_bundle_noun(sequence['bundle_count'])}"
        ),
        (
            f"Claims: {transition_claims['claim_count']} transition claims/"
            f"{transition_claims['matched_count']} matched examples; "
            f"{chain_claims['claim_count']} chain claims/"
            f"{chain_claims['certificate_count']} certificates"
        ),
        f"Proof rules: {_proof_rule_counts_text(proof_rule_audit)}",
        "Blocked commands: "
        + (", ".join(blocked_commands) if blocked_commands else "none"),
        f"Safe next slice: {frontier['safe_next_slice'] or 'none'}",
    ])


def run_project_status_cli(argv: list[str] | None = None) -> int:
    """Run the project status report CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.project_status",
        description="Render the AS project evidence and frontier status.",
    )
    parser.add_argument(
        "--transition-registry",
        default=str(DEFAULT_TRANSITION_REGISTRY),
        help="Path to the transition evidence registry JSON.",
    )
    parser.add_argument(
        "--chain-registry",
        default=str(DEFAULT_CHAIN_REGISTRY),
        help="Path to the transition-chain evidence registry JSON.",
    )
    parser.add_argument(
        "--sequence-registry",
        default=str(DEFAULT_SEQUENCE_REGISTRY),
        help="Path to the network-sequence evidence registry JSON.",
    )
    parser.add_argument(
        "--transition-language",
        default=str(DEFAULT_TRANSITION_LANGUAGE),
        help="Path to the transition claim language manifest.",
    )
    parser.add_argument(
        "--transition-claims",
        default=str(DEFAULT_TRANSITION_CLAIMS),
        help="Path to the transition claim manifest.",
    )
    parser.add_argument(
        "--transition-certificates",
        default=str(DEFAULT_TRANSITION_CERTIFICATES),
        help="Path to the transition proof certificate manifest.",
    )
    parser.add_argument(
        "--chain-language",
        default=str(DEFAULT_CHAIN_LANGUAGE),
        help="Path to the transition-chain claim language manifest.",
    )
    parser.add_argument(
        "--chain-claims",
        default=str(DEFAULT_CHAIN_CLAIMS),
        help="Path to the transition-chain claim manifest.",
    )
    parser.add_argument(
        "--chain-certificates",
        default=str(DEFAULT_CHAIN_CERTIFICATES),
        help="Path to the transition-chain proof certificate manifest.",
    )
    parser.add_argument(
        "--source-status",
        action="append",
        default=None,
        help="Source-status JSON path to include in the frontier summary.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "summary"),
        default="text",
        help="Output format for the status report.",
    )
    args = parser.parse_args(argv)

    source_status_paths = (
        [Path(path) for path in args.source_status]
        if args.source_status is not None
        else DEFAULT_SOURCE_STATUS_PATHS
    )
    report = build_project_status_report(
        transition_registry_path=args.transition_registry,
        chain_registry_path=args.chain_registry,
        sequence_registry_path=args.sequence_registry,
        transition_language_path=args.transition_language,
        transition_claims_path=args.transition_claims,
        transition_certificates_path=args.transition_certificates,
        chain_language_path=args.chain_language,
        chain_claims_path=args.chain_claims,
        chain_certificates_path=args.chain_certificates,
        source_status_paths=source_status_paths,
    )
    if args.format == "json":
        print(json.dumps(report, sort_keys=True))
    elif args.format == "summary":
        print(format_project_status_summary(report))
    else:
        print(format_project_status_report(report))
    return 0 if report["accepted"] else 1


def _transition_registry_summary(registry_path: Path | str) -> dict[str, Any]:
    path = Path(registry_path)
    try:
        registry = load_evidence_bundle_registry(path)
    except Exception as exc:
        return _registry_failure_summary(path, exc)

    results = validate_evidence_bundle_registry(registry)
    payload = registry_validation_report_payload(registry, results)
    return _registry_summary(payload, path)


def _chain_registry_summary(registry_path: Path | str) -> dict[str, Any]:
    path = Path(registry_path)
    try:
        registry = load_chain_evidence_bundle_registry(path)
    except Exception as exc:
        return _registry_failure_summary(path, exc)

    results = validate_chain_evidence_bundle_registry(registry)
    payload = chain_registry_validation_report_payload(registry, results)
    return _registry_summary(payload, path)


def _sequence_registry_summary(registry_path: Path | str) -> dict[str, Any]:
    path = Path(registry_path)
    try:
        registry = load_network_sequence_evidence_bundle_registry(path)
    except Exception as exc:
        return _registry_failure_summary(path, exc)

    results = validate_network_sequence_evidence_bundle_registry(registry)
    payload = network_sequence_registry_validation_report_payload(registry, results)
    return _registry_summary(payload, path)


def _transition_claim_summary(claims_path: Path | str) -> dict[str, Any]:
    path = Path(claims_path)
    try:
        report = validate_transition_claim_project(claims_path=path)
    except Exception as exc:
        return _transition_claim_failure_summary(path, exc)

    payload = transition_claim_report_payload(report)
    failed_subjects = [
        f"{result['claim_id']}/{result['example_name']}"
        for result in payload["results"]
        if not result["matched"]
    ]
    return {
        "claims_path": str(path),
        "accepted": payload["accepted"],
        "claim_count": payload["claim_count"],
        "example_count": payload["example_count"],
        "matched_count": payload["matched_count"],
        "failed_subjects": failed_subjects,
        "result_count": payload["result_count"],
        "results": payload["results"],
    }


def _transition_proof_certificate_summary(
    claims_path: Path | str,
    certificates_path: Path | str,
) -> dict[str, Any]:
    claims = Path(claims_path)
    certificates = Path(certificates_path)
    try:
        report = validate_proof_certificate_project(
            claims_path=claims,
            certificates_path=certificates,
        )
    except Exception as exc:
        return _transition_proof_certificate_failure_summary(
            claims,
            certificates,
            exc,
        )

    payload = proof_certificate_report_payload(report)
    failed_subjects = [
        result["claim_id"] for result in payload["results"] if not result["accepted"]
    ]
    return {
        "claims_path": str(claims),
        "certificates_path": str(certificates),
        "accepted": payload["accepted"],
        "claim_count": payload["claim_count"],
        "certificate_count": payload["certificate_count"],
        "failed_subjects": failed_subjects,
        "result_count": payload["result_count"],
        "results": payload["results"],
    }


def _chain_claim_summary(
    language_path: Path | str,
    claims_path: Path | str,
    certificates_path: Path | str,
) -> dict[str, Any]:
    language = Path(language_path)
    claims = Path(claims_path)
    certificates = Path(certificates_path)
    try:
        report = validate_transition_chain_claim_project(
            language_path=language,
            claims_path=claims,
            certificates_path=certificates,
        )
    except Exception as exc:
        return _chain_claim_failure_summary(language, claims, certificates, exc)

    payload = chain_claim_validation_report_payload(report)
    failed_subjects = [
        result["subject"] for result in payload["results"] if not result["accepted"]
    ]
    return {
        "language_id": payload["language_id"],
        "language_path": str(language),
        "claims_path": str(claims),
        "certificates_path": str(certificates),
        "accepted": payload["accepted"],
        "claim_count": payload["claim_count"],
        "certificate_count": payload["certificate_count"],
        "failed_subjects": failed_subjects,
        "result_count": payload["result_count"],
        "results": payload["results"],
    }


def _proof_rule_audit_summary(
    transition_certificates_path: Path | str,
    chain_certificates_path: Path | str,
) -> dict[str, Any]:
    transition = _proof_rule_source_summary(
        transition_certificates_path,
        missing_subject="certificate-file",
        invalid_subject="proof-json",
    )
    chain = _proof_rule_source_summary(
        chain_certificates_path,
        missing_subject="chain-certificate-file",
        invalid_subject="chain-json",
    )
    combined_counts = _combine_rule_counts(
        transition["rule_counts"],
        chain["rule_counts"],
    )
    failed_subjects = _unique_texts(
        [*transition["failed_subjects"], *chain["failed_subjects"]]
    )
    return {
        "accepted": transition["accepted"] and chain["accepted"],
        "transition": transition,
        "chain": chain,
        "combined": {
            "step_count": transition["step_count"] + chain["step_count"],
            "rule_counts": combined_counts,
            "failed_subjects": failed_subjects,
        },
    }


def _proof_rule_source_summary(
    certificates_path: Path | str,
    missing_subject: str,
    invalid_subject: str,
) -> dict[str, Any]:
    path = Path(certificates_path)
    try:
        certificates = load_proof_certificates(path)
    except FileNotFoundError:
        return _proof_rule_source_failure(path, missing_subject)
    except Exception:
        return _proof_rule_source_failure(path, invalid_subject)

    rule_counts = _empty_proof_rule_counts()
    step_count = 0
    for certificate in certificates:
        for step in certificate.steps:
            step_count += 1
            rule_counts[step.rule] = rule_counts.get(step.rule, 0) + 1
    return {
        "certificates_path": str(path),
        "accepted": True,
        "step_count": step_count,
        "rule_counts": rule_counts,
        "failed_subjects": [],
    }


def _proof_rule_source_failure(path: Path, subject: str) -> dict[str, Any]:
    return {
        "certificates_path": str(path),
        "accepted": False,
        "step_count": 0,
        "rule_counts": _empty_proof_rule_counts(),
        "failed_subjects": [subject],
    }


def _empty_proof_rule_counts() -> dict[str, int]:
    return {rule: 0 for rule in PROOF_RULE_BASELINE_ORDER}


def _combine_rule_counts(
    first: dict[str, int],
    second: dict[str, int],
) -> dict[str, int]:
    combined = _empty_proof_rule_counts()
    for counts in (first, second):
        for rule, count in counts.items():
            combined[rule] = combined.get(rule, 0) + count
    return combined


def _unique_texts(values: list[str]) -> list[str]:
    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique


def _transition_language_summary(
    language_path: Path | str,
    claims_path: Path | str,
    certificates_path: Path | str,
) -> dict[str, Any]:
    language = Path(language_path)
    claims = Path(claims_path)
    certificates = Path(certificates_path)
    try:
        report = validate_transition_claim_language_project(
            language_path=language,
            claims_path=claims,
            certificates_path=certificates,
        )
    except Exception as exc:
        return _language_failure_summary(language, claims, certificates, exc)

    payload = transition_claim_language_report_payload(report)
    return _language_summary(payload)


def _chain_language_summary(
    language_path: Path | str,
    claims_path: Path | str,
    certificates_path: Path | str,
) -> dict[str, Any]:
    language = Path(language_path)
    claims = Path(claims_path)
    certificates = Path(certificates_path)
    try:
        report = validate_transition_chain_claim_language_project(
            language_path=language,
            claims_path=claims,
            certificates_path=certificates,
        )
    except Exception as exc:
        return _language_failure_summary(language, claims, certificates, exc)

    payload = transition_chain_claim_language_report_payload(report)
    return _language_summary(payload)


def _language_summary(payload: dict[str, Any]) -> dict[str, Any]:
    failed_subjects = [
        result["subject"] for result in payload["results"] if not result["accepted"]
    ]
    return {
        "language_id": payload["language_id"],
        "language_path": payload["language_path"],
        "claims_path": payload["claims_path"],
        "certificates_path": payload["certificates_path"],
        "accepted": payload["accepted"],
        "claim_count": payload["claim_count"],
        "certificate_count": payload["certificate_count"],
        "failed_subjects": failed_subjects,
        "result_count": payload["result_count"],
        "results": payload["results"],
    }


def _language_failure_summary(
    language_path: Path,
    claims_path: Path,
    certificates_path: Path,
    exc: Exception,
) -> dict[str, Any]:
    subject = "language-file" if isinstance(exc, FileNotFoundError) else "language-json"
    detail = f"{type(exc).__name__}: {exc}"
    return {
        "language_id": "",
        "language_path": str(language_path),
        "claims_path": str(claims_path),
        "certificates_path": str(certificates_path),
        "accepted": False,
        "claim_count": 0,
        "certificate_count": 0,
        "failed_subjects": [subject],
        "result_count": 1,
        "results": [
            {
                "subject": subject,
                "accepted": False,
                "detail": detail,
            }
        ],
    }


def _transition_claim_failure_summary(path: Path, exc: Exception) -> dict[str, Any]:
    subject = "claim-file" if isinstance(exc, FileNotFoundError) else "claim-json"
    detail = f"{type(exc).__name__}: {exc}"
    return {
        "claims_path": str(path),
        "accepted": False,
        "claim_count": 0,
        "example_count": 0,
        "matched_count": 0,
        "failed_subjects": [subject],
        "result_count": 1,
        "results": [
            {
                "subject": subject,
                "accepted": False,
                "detail": detail,
            }
        ],
    }


def _transition_proof_certificate_failure_summary(
    claims_path: Path,
    certificates_path: Path,
    exc: Exception,
) -> dict[str, Any]:
    subject = _proof_certificate_failure_subject(claims_path, certificates_path, exc)
    detail = f"{type(exc).__name__}: {exc}"
    return {
        "claims_path": str(claims_path),
        "certificates_path": str(certificates_path),
        "accepted": False,
        "claim_count": 0,
        "certificate_count": 0,
        "failed_subjects": [subject],
        "result_count": 1,
        "results": [
            {
                "subject": subject,
                "accepted": False,
                "detail": detail,
            }
        ],
    }


def _proof_certificate_failure_subject(
    claims_path: Path,
    certificates_path: Path,
    exc: Exception,
) -> str:
    if isinstance(exc, FileNotFoundError):
        if not claims_path.is_file():
            return "claim-file"
        if not certificates_path.is_file():
            return "certificate-file"
        return "proof-file"
    if not claims_path.is_file():
        return "claim-file"
    if not certificates_path.is_file():
        return "certificate-file"
    return "proof-json"


def _chain_claim_failure_summary(
    language_path: Path,
    claims_path: Path,
    certificates_path: Path,
    exc: Exception,
) -> dict[str, Any]:
    subject = _chain_claim_failure_subject(
        language_path,
        claims_path,
        certificates_path,
        exc,
    )
    detail = f"{type(exc).__name__}: {exc}"
    return {
        "language_id": "",
        "language_path": str(language_path),
        "claims_path": str(claims_path),
        "certificates_path": str(certificates_path),
        "accepted": False,
        "claim_count": 0,
        "certificate_count": 0,
        "failed_subjects": [subject],
        "result_count": 1,
        "results": [
            {
                "subject": subject,
                "accepted": False,
                "detail": detail,
            }
        ],
    }


def _chain_claim_failure_subject(
    language_path: Path,
    claims_path: Path,
    certificates_path: Path,
    exc: Exception,
) -> str:
    if isinstance(exc, FileNotFoundError):
        if not language_path.is_file():
            return "chain-language-file"
        if not claims_path.is_file():
            return "chain-claim-file"
        if not certificates_path.is_file():
            return "chain-certificate-file"
        return "chain-file"
    if not language_path.is_file():
        return "chain-language-file"
    if not claims_path.is_file():
        return "chain-claim-file"
    if not certificates_path.is_file():
        return "chain-certificate-file"
    return "chain-json"


def _registry_summary(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    failed_subjects = [
        result["subject"] for result in payload["results"] if not result["accepted"]
    ]
    return {
        "registry_id": payload["registry_id"],
        "path": str(path),
        "accepted": payload["accepted"],
        "bundle_count": payload["bundle_count"],
        "bundles": payload["bundles"],
        "failed_subjects": failed_subjects,
        "result_count": payload["result_count"],
        "results": payload["results"],
    }


def _registry_failure_summary(path: Path, exc: Exception) -> dict[str, Any]:
    subject = "registry-file" if isinstance(exc, FileNotFoundError) else "registry-json"
    detail = f"{type(exc).__name__}: {exc}"
    return {
        "registry_id": "",
        "path": str(path),
        "accepted": False,
        "bundle_count": 0,
        "bundles": [],
        "failed_subjects": [subject],
        "result_count": 1,
        "results": [
            {
                "subject": subject,
                "accepted": False,
                "detail": detail,
            }
        ],
    }


def _frontier_summary(
    source_status_paths: list[Path | str] | tuple[Path | str, ...],
) -> dict[str, Any]:
    source_statuses: list[dict[str, Any]] = []
    missing: list[str] = []
    invalid: list[dict[str, str]] = []
    blocked_commands: set[str] = set()
    safe_next_slices: list[str] = []

    for source_status_path in source_status_paths:
        path = Path(source_status_path)
        if not path.is_file():
            missing.append(str(path))
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive drift path.
            invalid.append({
                "path": str(path),
                "subject": "source-status-json",
                "error": str(exc),
            })
            continue

        schema_error = _source_status_schema_error(data)
        if schema_error:
            invalid.append({
                "path": str(path),
                "subject": "source-status-schema",
                "error": schema_error,
            })
            continue

        safe_next_slice = _optional_text(data, "safe_next_slice")
        if safe_next_slice and not safe_next_slice.startswith("no-"):
            safe_next_slices.append(safe_next_slice)
        source_commands = _source_commands_from_status(data)
        blocked_commands.update(_blocked_commands_from_status(data))
        source_statuses.append(
            {
                "path": str(path),
                "decision": _optional_text(data, "decision"),
                "safe_next_slice": safe_next_slice,
                "as_boundary": _optional_text(data, "as_boundary"),
                "commands": _ordered_blocked_commands(source_commands),
                "blocked_runtime_surfaces": _blocked_runtime_surfaces(data),
                "required_resolution_questions": _resolution_question_ids(data),
                "resolution_questions": _resolution_questions(data),
                "resolution_question_evidence": _resolution_question_evidence(data),
                "resolved_resolution_questions": _resolved_resolution_questions(data),
                "execution_readiness": _execution_readiness(data),
                "additional_source_statuses": _additional_source_statuses(data),
            }
        )

    failed_subjects = []
    if missing:
        failed_subjects.append("source-status-file")
    invalid_subjects = {item["subject"] for item in invalid}
    if "source-status-json" in invalid_subjects:
        failed_subjects.append("source-status-json")
    if "source-status-schema" in invalid_subjects:
        failed_subjects.append("source-status-schema")
    return {
        "blocked_commands": _ordered_blocked_commands(blocked_commands),
        "failed_subjects": failed_subjects,
        "safe_next_slice": _common_or_joined(safe_next_slices),
        "source_statuses": source_statuses,
        "missing_source_statuses": missing,
        "invalid_source_statuses": invalid,
    }


def _source_commands_from_status(data: dict[str, Any]) -> set[str]:
    commands: set[str] = set()
    blocked_runtime_commands = data.get("blocked_runtime_commands")
    if isinstance(blocked_runtime_commands, list):
        commands.update(item for item in blocked_runtime_commands if isinstance(item, str))
    command = data.get("command")
    if isinstance(command, str):
        commands.add(command)
    command_list = data.get("commands")
    if isinstance(command_list, list):
        commands.update(item for item in command_list if isinstance(item, str))
    return commands


def _blocked_commands_from_status(data: dict[str, Any]) -> set[str]:
    commands: set[str] = set()
    blocked_runtime_commands = data.get("blocked_runtime_commands")
    if isinstance(blocked_runtime_commands, list):
        commands.update(item for item in blocked_runtime_commands if isinstance(item, str))

    if not _status_declares_active_blocker(data):
        return commands

    command = data.get("command")
    if isinstance(command, str):
        commands.add(command)
    command_list = data.get("commands")
    if isinstance(command_list, list):
        commands.update(item for item in command_list if isinstance(item, str))
    return commands


def _status_declares_active_blocker(data: dict[str, Any]) -> bool:
    if _blocked_runtime_surfaces(data) or _resolution_question_ids(data):
        return True
    decision = _optional_text(data, "decision")
    return decision.startswith("do-not-") or "blocked" in decision


def _resolution_question_ids(data: dict[str, Any]) -> list[str]:
    questions = data.get("required_resolution_questions")
    if not isinstance(questions, list):
        return []
    question_ids: list[str] = []
    for question in questions:
        if isinstance(question, dict):
            question_id = question.get("question_id")
            if isinstance(question_id, str) and question_id:
                question_ids.append(question_id)
    return question_ids


def _resolution_questions(data: dict[str, Any]) -> list[dict[str, str]]:
    questions = data.get("required_resolution_questions")
    if not isinstance(questions, list):
        return []
    resolution_questions: list[dict[str, str]] = []
    for question in questions:
        if not isinstance(question, dict):
            continue
        question_id = question.get("question_id")
        if not isinstance(question_id, str) or not question_id:
            continue
        resolution_questions.append({
            "question_id": question_id,
            "summary": _optional_text(question, "summary"),
        })
    return resolution_questions


def _resolved_resolution_questions(data: dict[str, Any]) -> list[dict[str, str]]:
    questions = data.get("resolved_resolution_questions")
    if not isinstance(questions, list):
        return []
    resolved_questions: list[dict[str, str]] = []
    for question in questions:
        if not isinstance(question, dict):
            continue
        question_id = question.get("question_id")
        decision = question.get("decision")
        if not isinstance(question_id, str) or not question_id:
            continue
        if not isinstance(decision, str) or not decision:
            continue
        resolved_question = {
            "question_id": question_id,
            "decision": decision,
        }
        source_status = question.get("source_status")
        if isinstance(source_status, str) and source_status:
            resolved_question["source_status"] = source_status
        if "formal_command_offset" in question:
            resolved_question["formal_command_offset"] = question["formal_command_offset"]
        legacy_divergence = question.get("legacy_divergence")
        if isinstance(legacy_divergence, str) and legacy_divergence:
            resolved_question["legacy_divergence"] = legacy_divergence
        resolved_questions.append(resolved_question)
    return resolved_questions


def _resolution_question_evidence(data: dict[str, Any]) -> list[dict[str, str]]:
    evidence_entries = data.get("resolution_question_evidence")
    if not isinstance(evidence_entries, list):
        return []
    resolution_evidence: list[dict[str, str]] = []
    for evidence_entry in evidence_entries:
        if not isinstance(evidence_entry, dict):
            continue
        question_id = evidence_entry.get("question_id")
        evidence = evidence_entry.get("evidence")
        if not isinstance(question_id, str) or not question_id:
            continue
        if not isinstance(evidence, str) or not evidence:
            continue
        resolution_evidence.append({
            "question_id": question_id,
            "evidence": evidence,
        })
    return resolution_evidence


def _additional_source_statuses(data: dict[str, Any]) -> list[dict[str, str]]:
    source_statuses = data.get("additional_source_statuses")
    if not isinstance(source_statuses, list):
        return []
    return [
        {
            "adr": source_status["adr"],
            "path": source_status["path"],
            "summary": source_status["summary"],
        }
        for source_status in source_statuses
    ]


def _execution_readiness(data: dict[str, Any]) -> dict[str, Any]:
    readiness = data.get("execution_readiness")
    if not isinstance(readiness, dict):
        return {}
    return {
        "decision": readiness["decision"],
        "execution_change_allowed": readiness["execution_change_allowed"],
        "blocked_by_resolution_questions": list(
            readiness["blocked_by_resolution_questions"]
        ),
        "summary": readiness["summary"],
    }


def _blocked_runtime_surfaces(data: dict[str, Any]) -> list[str]:
    surfaces = data.get("blocked_runtime_surfaces")
    if not isinstance(surfaces, list):
        return []
    return [surface for surface in surfaces if isinstance(surface, str)]


def _blocked_runtime_surface_text_lines(frontier: dict[str, Any]) -> list[str]:
    lines = ["Blocked runtime surfaces:"]
    for source_status in frontier["source_statuses"]:
        surfaces = source_status["blocked_runtime_surfaces"]
        if not surfaces:
            continue
        command_label = ", ".join(source_status["commands"]) or source_status["path"]
        lines.append(f"  {command_label}: {', '.join(surfaces)}")
    if len(lines) == 1:
        return ["Blocked runtime surfaces: none"]
    return lines


def _registry_bundle_text_lines(label: str, summary: dict[str, Any]) -> list[str]:
    bundles = summary["bundles"]
    if not bundles:
        return [f"{label} bundles: none"]
    lines = [f"{label} bundles:"]
    for bundle in bundles:
        lines.append(f"  {bundle['bundle_id']} -> {bundle['path']}")
        positive_example = bundle.get("positive_example")
        if positive_example:
            lines.append(f"    positive example: {positive_example}")
        covered_examples = bundle.get("covered_positive_examples")
        if covered_examples:
            lines.append(f"    covered examples: {'; '.join(covered_examples)}")
    return lines


def _bundle_count_text(count: int) -> str:
    return f"{count} {_bundle_noun(count)}"


def _bundle_noun(count: int) -> str:
    return "bundle" if count == 1 else "bundles"


def _language_text_line(label: str, summary: dict[str, Any]) -> str:
    status = "accepted" if summary["accepted"] else "rejected"
    return (
        f"{label}: {status} "
        f"({summary['claim_count']} claims, "
        f"{summary['certificate_count']} certificates)"
    )


def _transition_claim_text_line(summary: dict[str, Any]) -> str:
    status = "accepted" if summary["accepted"] else "rejected"
    return (
        f"Transition claims: {status} "
        f"({summary['claim_count']} claims, "
        f"{summary['example_count']} examples, "
        f"{summary['matched_count']} matched)"
    )


def _transition_proof_certificate_text_line(summary: dict[str, Any]) -> str:
    status = "accepted" if summary["accepted"] else "rejected"
    return (
        f"Transition proof certificates: {status} "
        f"({summary['claim_count']} claims, "
        f"{summary['certificate_count']} certificates)"
    )


def _chain_claim_text_line(summary: dict[str, Any]) -> str:
    status = "accepted" if summary["accepted"] else "rejected"
    return (
        f"Transition chain claims: {status} "
        f"({summary['claim_count']} claims, "
        f"{summary['certificate_count']} certificates)"
    )


def _claim_proof_failure_text_lines(
    transition_claims: dict[str, Any],
    transition_proof_certificates: dict[str, Any],
) -> list[str]:
    lines = ["Claim/proof failures:"]
    failed_claims = transition_claims["failed_subjects"]
    if failed_claims:
        lines.append(f"  Transition claim failures: {', '.join(failed_claims)}")
    failed_certificates = transition_proof_certificates["failed_subjects"]
    if failed_certificates:
        lines.append(
            "  Transition proof certificate failures: "
            + ", ".join(failed_certificates)
        )
    if len(lines) == 1:
        return ["Claim/proof failures: none"]
    return lines


def _chain_claim_failure_text_lines(summary: dict[str, Any]) -> list[str]:
    failed_subjects = summary["failed_subjects"]
    if not failed_subjects:
        return ["Chain claim failures: none"]
    return [f"Chain claim failures: {', '.join(failed_subjects)}"]


def _proof_rule_audit_text_line(summary: dict[str, Any]) -> str:
    if not summary["accepted"]:
        failed_subjects = summary["combined"]["failed_subjects"]
        subjects = ", ".join(failed_subjects) if failed_subjects else "unknown"
        return f"Proof rule audit: rejected ({subjects})"

    return f"Proof rule audit: {_proof_rule_counts_text(summary)}"


def _proof_rule_counts_text(summary: dict[str, Any]) -> str:
    rule_counts = summary["combined"]["rule_counts"]
    return ", ".join(
        f"{rule}={rule_counts.get(rule, 0)}" for rule in PROOF_RULE_TEXT_ORDER
    )


def _language_failure_text_lines(
    transition_language: dict[str, Any],
    chain_language: dict[str, Any],
) -> list[str]:
    lines = ["Language failures:"]
    for label, summary in (
        ("Transition language", transition_language),
        ("Chain language", chain_language),
    ):
        failed_subjects = summary["failed_subjects"]
        if failed_subjects:
            lines.append(f"  {label} failures: {', '.join(failed_subjects)}")
    if len(lines) == 1:
        return ["Language failures: none"]
    return lines


def _as_boundary_text_lines(frontier: dict[str, Any]) -> list[str]:
    lines = ["AS boundaries:"]
    for source_status in frontier["source_statuses"]:
        boundary = source_status["as_boundary"]
        if not boundary:
            continue
        command_label = ", ".join(source_status["commands"]) or source_status["path"]
        lines.append(f"  {command_label}: {boundary}")
    if len(lines) == 1:
        return ["AS boundaries: none"]
    return lines


def _execution_readiness_text_lines(frontier: dict[str, Any]) -> list[str]:
    lines = ["Execution readiness:"]
    for source_status in frontier["source_statuses"]:
        readiness = source_status["execution_readiness"]
        if not readiness:
            continue
        command_label = ", ".join(source_status["commands"]) or source_status["path"]
        allowed = "yes" if readiness["execution_change_allowed"] else "no"
        blockers = readiness["blocked_by_resolution_questions"]
        blocker_text = ", ".join(blockers) if blockers else "none"
        lines.append(
            f"  {command_label}: {readiness['decision']}; "
            f"execution changes allowed: {allowed}; blockers: {blocker_text}"
        )
        summary = readiness["summary"]
        if summary:
            lines.append(f"    summary: {summary}")
    if len(lines) == 1:
        return ["Execution readiness: none"]
    return lines


def _resolution_question_text_lines(frontier: dict[str, Any]) -> list[str]:
    lines = ["Resolution questions:"]
    for source_status in frontier["source_statuses"]:
        questions = source_status["resolution_questions"]
        if not questions:
            continue
        command_label = ", ".join(source_status["commands"]) or source_status["path"]
        lines.append(f"  {command_label}:")
        for question in questions:
            question_summary = question["summary"]
            if question_summary:
                lines.append(f"    {question['question_id']}: {question_summary}")
            else:
                lines.append(f"    {question['question_id']}")
    if len(lines) == 1:
        return ["Resolution questions: none"]
    return lines


def _resolved_resolution_question_text_lines(frontier: dict[str, Any]) -> list[str]:
    lines = ["Resolved resolution questions:"]
    for source_status in frontier["source_statuses"]:
        questions = source_status["resolved_resolution_questions"]
        if not questions:
            continue
        command_label = ", ".join(source_status["commands"]) or source_status["path"]
        lines.append(f"  {command_label}:")
        for question in questions:
            detail = f"{question['question_id']}: {question['decision']}"
            source_status_path = question.get("source_status")
            if source_status_path:
                detail = f"{detail} ({source_status_path})"
            lines.append(f"    {detail}")
            if "formal_command_offset" in question:
                lines.append(
                    f"      formal command offset: {question['formal_command_offset']}"
                )
            legacy_divergence = question.get("legacy_divergence")
            if legacy_divergence:
                lines.append(f"      legacy divergence: {legacy_divergence}")
    if len(lines) == 1:
        return ["Resolved resolution questions: none"]
    return lines


def _resolution_question_evidence_text_lines(frontier: dict[str, Any]) -> list[str]:
    lines = ["Resolution question evidence:"]
    for source_status in frontier["source_statuses"]:
        evidence_entries = source_status["resolution_question_evidence"]
        if not evidence_entries:
            continue
        command_label = ", ".join(source_status["commands"]) or source_status["path"]
        lines.append(f"  {command_label}:")
        for evidence_entry in evidence_entries:
            lines.append(
                f"    {evidence_entry['question_id']}: "
                f"{evidence_entry['evidence']}"
            )
    if len(lines) == 1:
        return ["Resolution question evidence: none"]
    return lines


def _additional_source_status_text_lines(frontier: dict[str, Any]) -> list[str]:
    lines = ["Additional source statuses:"]
    for source_status in frontier["source_statuses"]:
        additional_statuses = source_status["additional_source_statuses"]
        if not additional_statuses:
            continue
        command_label = ", ".join(source_status["commands"]) or source_status["path"]
        lines.append(f"  {command_label}:")
        for additional_status in additional_statuses:
            lines.append(
                "    "
                f"{additional_status['adr']} -> {additional_status['path']}: "
                f"{additional_status['summary']}"
            )
    if len(lines) == 1:
        return ["Additional source statuses: none"]
    return lines


def _source_status_schema_error(data: Any) -> str:
    if not isinstance(data, dict):
        return "source-status JSON must be an object"
    if not _is_nonempty_text(data.get("decision")):
        return "source-status decision must be non-empty text"
    if not _is_nonempty_text(data.get("safe_next_slice")):
        return "source-status safe_next_slice must be non-empty text"
    command_shape_error = _command_field_shape_error(data)
    if command_shape_error:
        return command_shape_error
    command_type_error = _command_token_type_error(data)
    if command_type_error:
        return command_type_error
    command_error = _blank_command_token_error(data)
    if command_error:
        return command_error
    if not _source_commands_from_status(data):
        return "source-status command fields must include at least one command token"
    surface_error = _blocked_runtime_surface_shape_error(data)
    if surface_error:
        return surface_error
    question_error = _resolution_question_shape_error(data)
    if question_error:
        return question_error
    duplicate_question_error = _duplicate_resolution_question_id_error(data)
    if duplicate_question_error:
        return duplicate_question_error
    question_evidence_error = _resolution_question_evidence_shape_error(data)
    if question_evidence_error:
        return question_evidence_error
    resolved_question_error = _resolved_resolution_question_shape_error(data)
    if resolved_question_error:
        return resolved_question_error
    duplicate_resolved_question_error = (
        _duplicate_resolved_resolution_question_id_error(data)
    )
    if duplicate_resolved_question_error:
        return duplicate_resolved_question_error
    question_disjointness_error = _resolution_question_disjointness_error(data)
    if question_disjointness_error:
        return question_disjointness_error
    execution_readiness_error = _execution_readiness_shape_error(data)
    if execution_readiness_error:
        return execution_readiness_error
    additional_source_status_error = _additional_source_status_shape_error(data)
    if additional_source_status_error:
        return additional_source_status_error
    if not _is_nonempty_text(data.get("as_boundary")):
        return "source-status as_boundary must be non-empty text"
    return ""


def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _command_field_shape_error(data: dict[str, Any]) -> str:
    command = data.get("command")
    if "command" in data and not isinstance(command, str):
        return "source-status command field must be text"
    for key in ("commands", "blocked_runtime_commands"):
        value = data.get(key)
        if key in data and not isinstance(value, list):
            return f"source-status {key} field must be a list"
    return ""


def _command_token_type_error(data: dict[str, Any]) -> str:
    for key in ("commands", "blocked_runtime_commands"):
        value = data.get(key)
        if isinstance(value, list):
            for item in value:
                if not isinstance(item, str):
                    return "source-status command tokens must be text"
    return ""


def _blank_command_token_error(data: dict[str, Any]) -> str:
    command = data.get("command")
    if isinstance(command, str) and not command.strip():
        return "source-status command tokens must be non-empty text"
    for key in ("commands", "blocked_runtime_commands"):
        value = data.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and not item.strip():
                    return "source-status command tokens must be non-empty text"
    return ""


def _blocked_runtime_surface_shape_error(data: dict[str, Any]) -> str:
    if "blocked_runtime_surfaces" not in data:
        return ""
    surfaces = data.get("blocked_runtime_surfaces")
    if not isinstance(surfaces, list):
        return "source-status blocked_runtime_surfaces field must be a list"
    for surface in surfaces:
        if not isinstance(surface, str):
            return "source-status runtime surfaces must be text"
        if not surface.strip():
            return "source-status runtime surfaces must be non-empty text"
    return ""


def _resolution_question_shape_error(data: dict[str, Any]) -> str:
    if "required_resolution_questions" not in data:
        return ""
    questions = data.get("required_resolution_questions")
    if not isinstance(questions, list):
        return "source-status required_resolution_questions field must be a list"
    for question in questions:
        if not isinstance(question, dict):
            return "source-status resolution question entries must be objects"
        if not _is_nonempty_text(question.get("question_id")):
            return "source-status resolution question_id must be non-empty text"
    return ""


def _resolved_resolution_question_shape_error(data: dict[str, Any]) -> str:
    if "resolved_resolution_questions" not in data:
        return ""
    questions = data.get("resolved_resolution_questions")
    if not isinstance(questions, list):
        return "source-status resolved_resolution_questions field must be a list"
    for question in questions:
        if not isinstance(question, dict):
            return "source-status resolved resolution question entries must be objects"
        if not _is_nonempty_text(question.get("question_id")):
            return (
                "source-status resolved resolution question_id must be "
                "non-empty text"
            )
        if not _is_nonempty_text(question.get("decision")):
            return (
                "source-status resolved resolution question decision must be "
                "non-empty text"
            )
        if "source_status" in question and not _is_nonempty_text(
            question.get("source_status")
        ):
            return (
                "source-status resolved resolution question source_status "
                "must be non-empty text"
            )
        if "formal_command_offset" in question:
            offset = question.get("formal_command_offset")
            if not isinstance(offset, int) or isinstance(offset, bool):
                return (
                    "source-status resolved resolution question "
                    "formal_command_offset must be an integer"
                )
        if "legacy_divergence" in question and not _is_nonempty_text(
            question.get("legacy_divergence")
        ):
            return (
                "source-status resolved resolution question legacy_divergence "
                "must be non-empty text"
            )
        source_status = question.get("source_status")
        if isinstance(source_status, str):
            source_status_path = Path(source_status)
            if not source_status_path.is_file():
                return (
                    "source-status resolved resolution question "
                    f"source_status path must exist: {source_status_path}"
                )
            try:
                linked_source_status = json.loads(
                    source_status_path.read_text(encoding="utf-8")
                )
            except json.JSONDecodeError:
                return (
                    "source-status resolved resolution question "
                    f"source_status path must contain JSON: {source_status_path}"
                )
            if not isinstance(linked_source_status, dict):
                return (
                    "source-status resolved resolution question "
                    "source_status path must contain a JSON object: "
                    f"{source_status_path}"
                )
    return ""


def _resolved_resolution_question_ids(data: dict[str, Any]) -> list[str]:
    questions = data.get("resolved_resolution_questions")
    if not isinstance(questions, list):
        return []
    question_ids: list[str] = []
    for question in questions:
        if isinstance(question, dict):
            question_id = question.get("question_id")
            if isinstance(question_id, str) and question_id:
                question_ids.append(question_id)
    return question_ids


def _duplicate_resolution_question_id_error(data: dict[str, Any]) -> str:
    return _duplicate_question_id_error(
        _resolution_question_ids(data),
        "resolution question_id",
    )


def _duplicate_resolved_resolution_question_id_error(data: dict[str, Any]) -> str:
    return _duplicate_question_id_error(
        _resolved_resolution_question_ids(data),
        "resolved resolution question_id",
    )


def _duplicate_question_id_error(question_ids: list[str], label: str) -> str:
    seen: set[str] = set()
    for question_id in question_ids:
        if question_id in seen:
            return f"source-status duplicate {label}: {question_id}"
        seen.add(question_id)
    return ""


def _resolution_question_disjointness_error(data: dict[str, Any]) -> str:
    overlapping_question_ids = sorted(
        set(_resolution_question_ids(data))
        & set(_resolved_resolution_question_ids(data))
    )
    if overlapping_question_ids:
        return (
            "source-status question_id cannot be both unresolved and resolved: "
            + ", ".join(overlapping_question_ids)
        )
    return ""


def _resolution_question_evidence_shape_error(data: dict[str, Any]) -> str:
    required_question_ids = set(_resolution_question_ids(data))
    if "resolution_question_evidence" not in data:
        if required_question_ids:
            return (
                "source-status resolution_question_evidence must cover "
                "required_resolution_questions"
            )
        return ""
    evidence_entries = data.get("resolution_question_evidence")
    if not isinstance(evidence_entries, list):
        return "source-status resolution_question_evidence field must be a list"
    evidence_question_ids: set[str] = set()
    for evidence_entry in evidence_entries:
        if not isinstance(evidence_entry, dict):
            return "source-status resolution question evidence entries must be objects"
        if not _is_nonempty_text(evidence_entry.get("question_id")):
            return (
                "source-status resolution question evidence question_id must "
                "be non-empty text"
            )
        if evidence_entry["question_id"] not in required_question_ids:
            return (
                "source-status resolution question evidence question_id must "
                "match required_resolution_questions"
            )
        evidence_question_ids.add(evidence_entry["question_id"])
        if not _is_nonempty_text(evidence_entry.get("evidence")):
            return (
                "source-status resolution question evidence must be "
                "non-empty text"
            )
    if required_question_ids - evidence_question_ids:
        return (
            "source-status resolution_question_evidence must cover "
            "required_resolution_questions"
        )
    return ""


def _execution_readiness_shape_error(data: dict[str, Any]) -> str:
    if "execution_readiness" not in data:
        return ""
    readiness = data.get("execution_readiness")
    if not isinstance(readiness, dict):
        return "source-status execution_readiness field must be an object"
    if not _is_nonempty_text(readiness.get("decision")):
        return "source-status execution_readiness decision must be non-empty text"
    allowed = readiness.get("execution_change_allowed")
    if not isinstance(allowed, bool):
        return (
            "source-status execution_readiness execution_change_allowed "
            "must be a boolean"
        )
    blockers = readiness.get("blocked_by_resolution_questions")
    if not isinstance(blockers, list):
        return (
            "source-status execution_readiness "
            "blocked_by_resolution_questions field must be a list"
        )
    required_question_ids = set(_resolution_question_ids(data))
    for blocker in blockers:
        if not isinstance(blocker, str):
            return (
                "source-status execution_readiness "
                "blocked_by_resolution_questions entries must be text"
            )
        if not blocker.strip():
            return (
                "source-status execution_readiness "
                "blocked_by_resolution_questions entries must be non-empty text"
            )
        if blocker not in required_question_ids:
            return (
                "source-status execution_readiness "
                "blocked_by_resolution_questions must match "
                "required_resolution_questions"
            )
    if allowed and blockers:
        return (
            "source-status execution_readiness cannot allow execution changes "
            "while blocked_by_resolution_questions is non-empty"
        )
    if readiness["decision"] == "blocked" and allowed:
        return (
            "source-status execution_readiness cannot use decision blocked "
            "while allowing execution changes"
        )
    if allowed and required_question_ids:
        return (
            "source-status execution_readiness cannot allow execution changes "
            "while unresolved required_resolution_questions remain"
        )
    if readiness["decision"] == "blocked" and required_question_ids - set(blockers):
        return (
            "source-status execution_readiness "
            "blocked_by_resolution_questions must cover "
            "required_resolution_questions"
        )
    if not _is_nonempty_text(readiness.get("summary")):
        return "source-status execution_readiness summary must be non-empty text"
    return ""


def _additional_source_status_shape_error(data: dict[str, Any]) -> str:
    if "additional_source_statuses" not in data:
        return ""
    source_statuses = data.get("additional_source_statuses")
    if not isinstance(source_statuses, list):
        return "source-status additional_source_statuses field must be a list"
    for source_status in source_statuses:
        if not isinstance(source_status, dict):
            return "source-status additional source-status entries must be objects"
        for key in ("adr", "path", "summary"):
            if not _is_nonempty_text(source_status.get(key)):
                return (
                    "source-status additional source-status "
                    f"{key} must be non-empty text"
                )
        source_status_path = Path(source_status["path"])
        if not source_status_path.is_file():
            return (
                "source-status additional source-status "
                f"path must exist: {source_status_path}"
            )
        try:
            linked_source_status = json.loads(
                source_status_path.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError:
            return (
                "source-status additional source-status "
                f"path must contain JSON: {source_status_path}"
            )
        if not isinstance(linked_source_status, dict):
            return (
                "source-status additional source-status "
                f"path must contain a source-status object: {source_status_path}"
            )
    return ""


def _ordered_blocked_commands(commands: set[str]) -> list[str]:
    ordered = [command for command in BLOCKED_COMMAND_ORDER if command in commands]
    ordered.extend(sorted(commands - set(ordered)))
    return ordered


def _common_or_joined(values: list[str]) -> str:
    unique = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique[0] if len(unique) == 1 else ", ".join(unique)


def _optional_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    return value if isinstance(value, str) else ""


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess tests.
    raise SystemExit(run_project_status_cli())
