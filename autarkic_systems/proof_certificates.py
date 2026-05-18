"""Proof-certificate checks for AS transition claims.

This module is deliberately smaller than a theorem prover. It validates
explicit certificate records against the current claim manifest, giving AS a
first inspectable proof-object layer while avoiding premature claims about
SJAS-level self-justification.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from autarkic_systems import transition_predicates
from autarkic_systems.claim_manifest import Claim, load_transition_claims


MANIFEST_EXAMPLE_RULE = "manifest-example"
PREDICATE_RESULT_RULE = "predicate-result"


@dataclass(frozen=True)
class CertificateStep:
    """One proof-certificate clause for a claim example."""

    rule: str
    example: str
    expected: bool
    predicate: str | None = None


@dataclass(frozen=True)
class ClaimCertificate:
    """A small proof object attached to one manifest claim ID."""

    claim_id: str
    steps: tuple[CertificateStep, ...]

    def with_steps(self, steps: tuple[CertificateStep, ...]) -> "ClaimCertificate":
        """Return a copy with replacement steps for focused negative tests."""

        return replace(self, steps=steps)


@dataclass(frozen=True)
class CertificateVerification:
    """Verification result for one claim certificate."""

    claim_id: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class ProofCertificateProjectReport:
    """Operator-facing validation report for transition proof certificates."""

    claims_path: Path
    certificates_path: Path
    claim_count: int
    certificate_count: int
    results: tuple[CertificateVerification, ...]


def load_proof_certificates(path: Path | str) -> list[ClaimCertificate]:
    """Load proof certificates from a JSON manifest."""

    certificate_path = Path(path)
    data = json.loads(certificate_path.read_text(encoding="utf-8"))
    certificates = data.get("certificates")
    if not isinstance(certificates, list):
        raise ValueError("proof certificate manifest must contain a certificates list")
    return [_parse_certificate(item) for item in certificates]


def validate_proof_certificate_project(
    claims_path: Path | str = "claims/transition_claims.json",
    certificates_path: Path | str = "claims/proof_certificates.json",
) -> ProofCertificateProjectReport:
    """Validate the transition proof-certificate surface as one report."""

    claim_manifest = Path(claims_path)
    certificate_manifest = Path(certificates_path)
    claims = load_transition_claims(claim_manifest)
    certificates = load_proof_certificates(certificate_manifest)
    results = tuple(verify_claim_certificates(claims, certificates))
    return ProofCertificateProjectReport(
        claims_path=claim_manifest,
        certificates_path=certificate_manifest,
        claim_count=len(claims),
        certificate_count=len(certificates),
        results=results,
    )


def format_proof_certificate_report(report: ProofCertificateProjectReport) -> str:
    """Format a concise operator report for transition proof certificates."""

    lines = [f"Transition proof certificates: {report.certificates_path}"]
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.claim_id}: {result.detail}")
    return "\n".join(lines)


def proof_certificate_report_payload(
    report: ProofCertificateProjectReport,
) -> dict[str, Any]:
    """Return a structured proof-certificate validation payload."""

    return {
        "accepted": all(result.accepted for result in report.results),
        "claim_count": report.claim_count,
        "certificate_count": report.certificate_count,
        "result_count": len(report.results),
        "results": [
            {
                "claim_id": result.claim_id,
                "accepted": result.accepted,
                "detail": result.detail,
            }
            for result in report.results
        ],
    }


def run_proof_certificate_cli(argv: list[str] | None = None) -> int:
    """Run the transition proof-certificate validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.proof_certificates",
        description="Validate the AS transition proof-certificate surface.",
    )
    parser.add_argument(
        "--claims",
        default="claims/transition_claims.json",
        help="Path to the transition claim manifest.",
    )
    parser.add_argument(
        "--certificates",
        default="claims/proof_certificates.json",
        help="Path to the transition proof certificate manifest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    report = validate_proof_certificate_project(
        claims_path=args.claims,
        certificates_path=args.certificates,
    )
    if args.format == "json":
        print(json.dumps(proof_certificate_report_payload(report), sort_keys=True))
    else:
        print(format_proof_certificate_report(report))
    return 0 if all(result.accepted for result in report.results) else 1


def verify_claim_certificates(
    claims: Iterable[Claim], certificates: Iterable[ClaimCertificate]
) -> list[CertificateVerification]:
    """Verify certificates against every known claim.

    The result list includes one entry for each claim, plus explicit rejections
    for certificates that name unknown claim IDs. Verification failures are
    reported as rejected certificates rather than uncaught runtime errors.
    """

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
            results.append(
                CertificateVerification(
                    claim_id=claim.claim_id,
                    accepted=False,
                    detail="missing certificate for claim",
                )
            )
            continue
        if len(matching) > 1:
            results.append(
                CertificateVerification(
                    claim_id=claim.claim_id,
                    accepted=False,
                    detail="duplicate certificates for claim",
                )
            )
            continue
        results.append(_verify_certificate(claim, matching[0]))

    for certificate in certificate_list:
        if certificate.claim_id not in claim_by_id:
            results.append(
                CertificateVerification(
                    claim_id=certificate.claim_id,
                    accepted=False,
                    detail="unknown claim in certificate manifest",
                )
            )

    return results


def _verify_certificate(
    claim: Claim, certificate: ClaimCertificate
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

    checker = getattr(transition_predicates, claim.predicate, None)
    if checker is None:
        return _rejected(claim.claim_id, f"unknown predicate checker: {claim.predicate}")

    rule_counts: dict[str, int] = {}
    for step in certificate.steps:
        if step.rule not in {MANIFEST_EXAMPLE_RULE, PREDICATE_RESULT_RULE}:
            return _rejected(
                claim.claim_id, f"unknown certificate rule: {step.rule}"
            )
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

        predicate_result = checker(example.before, example.result)
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
                f"{step.example}: observed {observed}, "
                f"expected {example.expected}",
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


def _parse_certificate(item: dict[str, Any]) -> ClaimCertificate:
    steps = item.get("steps")
    if not isinstance(steps, list):
        raise ValueError(f"certificate {item.get('claim_id')!r} must define steps")
    return ClaimCertificate(
        claim_id=_required_text(item, "claim_id"),
        steps=tuple(_parse_step(step) for step in steps),
    )


def _parse_step(item: dict[str, Any]) -> CertificateStep:
    return CertificateStep(
        rule=_required_text(item, "rule"),
        example=_required_text(item, "example"),
        expected=_required_bool(item, "expected"),
        predicate=_optional_text(item, "predicate"),
    )


def _rejected(claim_id: str, detail: str) -> CertificateVerification:
    return CertificateVerification(claim_id=claim_id, accepted=False, detail=detail)


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


def _optional_text(item: dict[str, Any], key: str) -> str | None:
    if key not in item:
        return None
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"optional text field malformed: {key}")
    return value


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess tests.
    raise SystemExit(run_proof_certificate_cli())
