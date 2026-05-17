"""Proof-certificate checks for AS transition claims.

This module is deliberately smaller than a theorem prover. It validates
explicit certificate records against the current claim manifest, giving AS a
first inspectable proof-object layer while avoiding premature claims about
SJAS-level self-justification.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from autarkic_systems import transition_predicates
from autarkic_systems.claim_manifest import Claim


MANIFEST_EXAMPLE_RULE = "manifest-example"


@dataclass(frozen=True)
class CertificateStep:
    """One proof-certificate clause for a claim example."""

    rule: str
    example: str
    expected: bool


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


def load_proof_certificates(path: Path | str) -> list[ClaimCertificate]:
    """Load proof certificates from a JSON manifest."""

    certificate_path = Path(path)
    data = json.loads(certificate_path.read_text(encoding="utf-8"))
    certificates = data.get("certificates")
    if not isinstance(certificates, list):
        raise ValueError("proof certificate manifest must contain a certificates list")
    return [_parse_certificate(item) for item in certificates]


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

    for step in certificate.steps:
        if step.rule != MANIFEST_EXAMPLE_RULE:
            return _rejected(
                claim.claim_id, f"unknown certificate rule: {step.rule}"
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
        observed = bool(predicate_result.holds)
        if observed != example.expected:
            return _rejected(
                claim.claim_id,
                "predicate mismatch for "
                f"{step.example}: observed {observed}, "
                f"expected {example.expected}",
            )

    return CertificateVerification(
        claim_id=claim.claim_id,
        accepted=True,
        detail=f"verified {len(certificate.steps)} manifest-example steps",
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
