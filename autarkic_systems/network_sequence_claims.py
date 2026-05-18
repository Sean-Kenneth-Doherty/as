"""Claim and proof checks for post-handoff network sequence witnesses."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from autarkic_systems import network_sequence_predicates
from autarkic_systems.network_sequence import execute_post_handoff_signal_witness
from autarkic_systems.proof_certificates import (
    ClaimCertificate,
    CertificateVerification,
    MANIFEST_EXAMPLE_RULE,
    PREDICATE_RESULT_RULE,
    load_proof_certificates,
)
from autarkic_systems.universal_cell import Cell


@dataclass(frozen=True)
class NetworkSequenceClaimExample:
    """One executable example attached to a network-sequence claim."""

    name: str
    expected: bool
    sender: Cell
    recipient: Cell
    followup_input: tuple[Any, Any, Any]


@dataclass(frozen=True)
class NetworkSequenceClaim:
    """A manifest claim over a post-handoff network sequence witness."""

    claim_id: str
    predicate: str
    description: str
    examples: tuple[NetworkSequenceClaimExample, ...]

    def with_checker(self, checker: str) -> "NetworkSequenceClaim":
        """Return a copy referencing a different sequence predicate checker."""

        return replace(self, predicate=checker)


@dataclass(frozen=True)
class NetworkSequenceExampleEvaluation:
    """Observed outcome for a network-sequence claim example."""

    claim_id: str
    example_name: str
    expected: bool
    observed: bool
    matched: bool
    detail: str


@dataclass(frozen=True)
class NetworkSequenceClaimProjectValidation:
    """One validation result for the network-sequence claim surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class NetworkSequenceClaimProjectReport:
    """Operator-facing validation report for network-sequence claims."""

    claims_path: Path
    certificates_path: Path
    claim_count: int
    certificate_count: int
    results: tuple[NetworkSequenceClaimProjectValidation, ...]


def load_network_sequence_claims(path: Path | str) -> list[NetworkSequenceClaim]:
    """Load network-sequence claims from a JSON manifest."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    claims = data.get("claims")
    if not isinstance(claims, list):
        raise ValueError("network sequence claim manifest must contain a claims list")
    return [_parse_claim(item) for item in claims]


def validate_network_sequence_claim_project(
    claims_path: Path | str = "claims/network_sequence_claims.json",
    certificates_path: Path | str = "claims/network_sequence_proof_certificates.json",
) -> NetworkSequenceClaimProjectReport:
    """Validate sequence claims and certificates as one surface."""

    claim_manifest = Path(claims_path)
    certificate_manifest = Path(certificates_path)
    claims = load_network_sequence_claims(claim_manifest)
    certificates = load_proof_certificates(certificate_manifest)
    evaluations = evaluate_network_sequence_claim_examples(claims)
    certificate_results = verify_network_sequence_claim_certificates(
        claims,
        certificates,
    )
    results = (
        _summarize_example_results(evaluations),
        _summarize_certificate_results(certificate_results),
    )
    return NetworkSequenceClaimProjectReport(
        claims_path=claim_manifest,
        certificates_path=certificate_manifest,
        claim_count=len(claims),
        certificate_count=len(certificates),
        results=results,
    )


def format_network_sequence_claim_validation_report(
    report: NetworkSequenceClaimProjectReport,
) -> str:
    """Format a concise operator report for sequence-claim validation."""

    lines = [f"Network sequence claims: {report.claims_path}"]
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def network_sequence_claim_validation_report_payload(
    report: NetworkSequenceClaimProjectReport,
) -> dict[str, Any]:
    """Return a structured sequence-claim validation report payload."""

    return {
        "accepted": all(result.accepted for result in report.results),
        "claim_count": report.claim_count,
        "certificate_count": report.certificate_count,
        "failed_subjects": [
            result.subject for result in report.results if not result.accepted
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


def run_network_sequence_claim_cli(argv: list[str] | None = None) -> int:
    """Run the network-sequence claim validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.network_sequence_claims",
        description="Validate the AS network-sequence claim surface.",
    )
    parser.add_argument(
        "--claims",
        default="claims/network_sequence_claims.json",
        help="Path to the network-sequence claim manifest.",
    )
    parser.add_argument(
        "--certificates",
        default="claims/network_sequence_proof_certificates.json",
        help="Path to the network-sequence proof certificate manifest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    report = validate_network_sequence_claim_project(
        claims_path=args.claims,
        certificates_path=args.certificates,
    )
    if args.format == "json":
        print(
            json.dumps(
                network_sequence_claim_validation_report_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_network_sequence_claim_validation_report(report))
    return 0 if all(result.accepted for result in report.results) else 1


def evaluate_network_sequence_claim_examples(
    claims: Iterable[NetworkSequenceClaim],
) -> list[NetworkSequenceExampleEvaluation]:
    """Evaluate every sequence example against its predicate checker."""

    evaluations: list[NetworkSequenceExampleEvaluation] = []
    for claim in claims:
        checker = getattr(network_sequence_predicates, claim.predicate, None)
        if checker is None:
            raise ValueError(f"unknown sequence predicate checker: {claim.predicate}")
        for example in claim.examples:
            witness = execute_post_handoff_signal_witness(
                example.sender,
                example.recipient,
                followup_input=example.followup_input,
            )
            predicate_result = checker(witness)
            observed = bool(predicate_result.holds)
            evaluations.append(
                NetworkSequenceExampleEvaluation(
                    claim_id=claim.claim_id,
                    example_name=example.name,
                    expected=example.expected,
                    observed=observed,
                    matched=observed == example.expected,
                    detail=predicate_result.detail,
                )
            )
    return evaluations


def verify_network_sequence_claim_certificates(
    claims: Iterable[NetworkSequenceClaim],
    certificates: Iterable[ClaimCertificate],
) -> list[CertificateVerification]:
    """Verify proof certificates against network-sequence claims."""

    claim_list = list(claims)
    certificate_list = list(certificates)
    claim_by_id = {claim.claim_id: claim for claim in claim_list}
    results: list[CertificateVerification] = []

    for claim in claim_list:
        matching = [
            certificate
            for certificate in certificate_list
            if certificate.claim_id == claim.claim_id
        ]
        if not matching:
            results.append(_rejected(claim.claim_id, "missing certificate for claim"))
            continue
        if len(matching) > 1:
            results.append(_rejected(claim.claim_id, "duplicate certificates for claim"))
            continue
        results.append(_verify_certificate(claim, matching[0]))

    for certificate in certificate_list:
        if certificate.claim_id not in claim_by_id:
            results.append(
                _rejected(
                    certificate.claim_id,
                    "unknown claim in certificate manifest",
                )
            )

    return results


def _verify_certificate(
    claim: NetworkSequenceClaim,
    certificate: ClaimCertificate,
) -> CertificateVerification:
    example_by_name = {example.name: example for example in claim.examples}
    step_names = [step.example for step in certificate.steps]
    step_name_set = set(step_names)
    example_name_set = set(example_by_name)

    if not certificate.steps:
        return _rejected(claim.claim_id, "certificate has no steps")
    if len(step_names) != len(step_name_set):
        return _rejected(claim.claim_id, "duplicate example steps in certificate")

    unknown_examples = sorted(step_name_set - example_name_set)
    if unknown_examples:
        return _rejected(
            claim.claim_id,
            f"unknown examples in certificate: {', '.join(unknown_examples)}",
        )

    missing_examples = sorted(example_name_set - step_name_set)
    if missing_examples:
        return _rejected(
            claim.claim_id,
            f"missing examples in certificate: {', '.join(missing_examples)}",
        )

    checker = getattr(network_sequence_predicates, claim.predicate, None)
    if checker is None:
        return _rejected(
            claim.claim_id,
            f"unknown sequence predicate checker: {claim.predicate}",
        )

    rule_counts: dict[str, int] = {}
    for step in certificate.steps:
        if step.rule not in {MANIFEST_EXAMPLE_RULE, PREDICATE_RESULT_RULE}:
            return _rejected(claim.claim_id, f"unknown certificate rule: {step.rule}")
        if step.rule == PREDICATE_RESULT_RULE:
            if not step.predicate:
                return _rejected(
                    claim.claim_id,
                    f"predicate-result step for {step.example} lacks predicate",
                )
            if step.predicate != claim.predicate:
                return _rejected(
                    claim.claim_id,
                    "predicate mismatch for "
                    f"{step.example}: certificate named {step.predicate}, "
                    f"claim uses {claim.predicate}",
                )

        example = example_by_name[step.example]
        if step.expected != example.expected:
            return _rejected(
                claim.claim_id,
                "expectation mismatch for "
                f"{step.example}: certificate expected {step.expected}, "
                f"manifest expected {example.expected}",
            )

        witness = execute_post_handoff_signal_witness(
            example.sender,
            example.recipient,
            followup_input=example.followup_input,
        )
        predicate_result = checker(witness)
        if (
            step.rule == PREDICATE_RESULT_RULE
            and predicate_result.name != step.predicate
        ):
            return _rejected(
                claim.claim_id,
                "predicate result name mismatch for "
                f"{step.example}: observed {predicate_result.name}, "
                f"certificate named {step.predicate}",
            )
        observed = bool(predicate_result.holds)
        if observed != example.expected:
            return _rejected(
                claim.claim_id,
                "predicate mismatch for "
                f"{step.example}: observed {observed}, expected {example.expected}",
            )
        rule_counts[step.rule] = rule_counts.get(step.rule, 0) + 1

    rule_summary = ", ".join(
        f"{count} {rule} steps" for rule, count in sorted(rule_counts.items())
    )
    return CertificateVerification(
        claim_id=claim.claim_id,
        accepted=True,
        detail=f"verified {len(certificate.steps)} certificate steps: {rule_summary}",
    )


def _parse_claim(item: dict[str, Any]) -> NetworkSequenceClaim:
    examples = item.get("examples")
    if not isinstance(examples, list) or not examples:
        raise ValueError(
            f"network sequence claim {item.get('id')!r} must define examples"
        )
    return NetworkSequenceClaim(
        claim_id=_required_text(item, "id"),
        predicate=_required_text(item, "predicate"),
        description=_required_text(item, "description"),
        examples=tuple(_parse_example(example) for example in examples),
    )


def _parse_example(item: dict[str, Any]) -> NetworkSequenceClaimExample:
    return NetworkSequenceClaimExample(
        name=_required_text(item, "name"),
        expected=_required_bool(item, "expected"),
        sender=_parse_cell(item["sender"]),
        recipient=_parse_cell(item["recipient"]),
        followup_input=_parse_signal(item["followup_input"]),
    )


def _parse_cell(item: dict[str, Any]) -> Cell:
    return Cell(
        role=_required_text(item, "role"),
        memory=_required_text(item, "memory"),
        upstream=_parse_signal(item.get("upstream", ["_", "_", "_"])),
        input=_parse_signal(item.get("input", ["_", "_", "_"])),
        output=_parse_signal(item.get("output", ["_", "_", "_"])),
        automail=item.get("automail", "_"),
        self_mailbox=item.get("self_mailbox", "_"),
        control=tuple(item.get("control", [])),
        buffer=tuple(item.get("buffer", [])),
    )


def _parse_signal(value: list[Any]) -> tuple[Any, Any, Any]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError("signal must be a three-item list")
    return tuple(value)


def _summarize_example_results(
    evaluations: list[NetworkSequenceExampleEvaluation],
) -> NetworkSequenceClaimProjectValidation:
    failures = [
        f"{evaluation.claim_id}/{evaluation.example_name}: {evaluation.detail}"
        for evaluation in evaluations
        if not evaluation.matched
    ]
    if failures:
        return _project_rejected("sequence-examples", " | ".join(failures))
    return _project_accepted(
        "sequence-examples",
        f"evaluated {len(evaluations)} examples",
    )


def _summarize_certificate_results(
    results: list[CertificateVerification],
) -> NetworkSequenceClaimProjectValidation:
    failures = [
        f"{result.claim_id}: {result.detail}"
        for result in results
        if not result.accepted
    ]
    if failures:
        return _project_rejected("sequence-certificates", " | ".join(failures))
    return _project_accepted(
        "sequence-certificates",
        f"verified {len(results)} certificates",
    )


def _project_accepted(
    subject: str,
    detail: str,
) -> NetworkSequenceClaimProjectValidation:
    return NetworkSequenceClaimProjectValidation(subject, True, detail)


def _project_rejected(
    subject: str,
    detail: str,
) -> NetworkSequenceClaimProjectValidation:
    return NetworkSequenceClaimProjectValidation(subject, False, detail)


def _rejected(claim_id: str, detail: str) -> CertificateVerification:
    return CertificateVerification(claim_id, False, detail)


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_bool(item: dict[str, Any], key: str) -> bool:
    value = item.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"required boolean field missing: {key}")
    return value


if __name__ == "__main__":
    raise SystemExit(run_network_sequence_claim_cli())
