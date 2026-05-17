"""Integrated evidence bundles for composed transition-chain slices.

Chain evidence bundles sit above single-transition evidence bundles. They do
not claim a new Universal Cell transition; they make one composed chain
auditable across its chain claim, proof certificate, object language,
supporting transition bundles, and source-status boundaries.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems import transition_chain_predicates, transition_chains
from autarkic_systems.chain_claims import (
    ChainClaim,
    ChainClaimExample,
    load_transition_chain_claims,
    verify_chain_claim_certificates,
)
from autarkic_systems.chain_object_language import (
    load_transition_chain_claim_language,
    validate_chain_claim_surface,
    validate_chain_language_manifest,
)
from autarkic_systems.chain_svg import validate_transition_chain_svg
from autarkic_systems.chain_trace import (
    load_transition_chain_trace,
    validate_transition_chain_trace,
)
from autarkic_systems.evidence_bundle import (
    load_transition_evidence_bundle,
    validate_transition_evidence_bundle,
)
from autarkic_systems.proof_certificates import load_proof_certificates


@dataclass(frozen=True)
class TransitionChainEvidenceBundle:
    """One inspectable path from chain behavior to supporting evidence."""

    schema_version: int
    bundle_id: str
    reviewed_at: str
    purpose: str
    chain_claim_id: str
    predicate: str
    positive_example: str
    transition_chain_function: str
    expected_status: str
    chain_claim_manifest_path: Path
    chain_proof_certificate_path: Path
    chain_language_path: Path
    chain_claim_validator_path: Path
    chain_trace_path: Path
    chain_svg_path: Path
    transition_bundle_paths: tuple[Path, ...]
    source_status_paths: tuple[Path, ...]
    boundaries: tuple[str, ...]


@dataclass(frozen=True)
class ChainEvidenceBundleValidation:
    """One validation result for a transition-chain evidence bundle."""

    subject: str
    accepted: bool
    detail: str


def load_transition_chain_evidence_bundle(
    path: Path | str,
) -> TransitionChainEvidenceBundle:
    """Load a transition-chain evidence bundle from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    artifacts = _required_dict(data, "artifacts")
    return TransitionChainEvidenceBundle(
        schema_version=_required_int(data, "schema_version"),
        bundle_id=_required_text(data, "bundle_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        chain_claim_id=_required_text(data, "chain_claim_id"),
        predicate=_required_text(data, "predicate"),
        positive_example=_required_text(data, "positive_example"),
        transition_chain_function=_required_text(data, "transition_chain_function"),
        expected_status=_required_text(data, "expected_status"),
        chain_claim_manifest_path=Path(_required_text(artifacts, "chain_claims")),
        chain_proof_certificate_path=Path(
            _required_text(artifacts, "chain_proof_certificates")
        ),
        chain_language_path=Path(_required_text(artifacts, "chain_language")),
        chain_claim_validator_path=Path(
            _required_text(artifacts, "chain_claim_validator")
        ),
        chain_trace_path=Path(_required_text(artifacts, "chain_trace")),
        chain_svg_path=Path(_required_text(artifacts, "chain_svg")),
        transition_bundle_paths=tuple(
            Path(path) for path in _required_text_list(artifacts, "transition_bundles")
        ),
        source_status_paths=tuple(
            Path(path) for path in _required_text_list(artifacts, "source_statuses")
        ),
        boundaries=tuple(_required_text_list(data, "boundaries")),
    )


def validate_transition_chain_evidence_bundle(
    bundle: TransitionChainEvidenceBundle,
) -> list[ChainEvidenceBundleValidation]:
    """Validate a chain bundle across chain and transition evidence layers."""

    results = [_validate_schema(bundle)]
    _claim, _example, claim_result = _validate_chain_claim_example(bundle)
    results.append(claim_result)
    results.append(_validate_chain_proof_certificate(bundle))
    results.append(_validate_chain_language(bundle))
    results.append(_validate_chain_trace(bundle))
    results.append(_validate_chain_svg(bundle))
    results.append(_validate_underlying_transition_bundles(bundle))
    results.append(_validate_source_statuses(bundle))
    results.append(_validate_boundary(bundle))
    return results


def format_chain_evidence_bundle_report(
    bundle: TransitionChainEvidenceBundle,
    results: list[ChainEvidenceBundleValidation],
) -> str:
    """Format a concise operator report for chain bundle validation."""

    lines = [f"Transition chain evidence bundle: {bundle.bundle_id}"]
    for result in results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def chain_evidence_bundle_report_payload(
    bundle: TransitionChainEvidenceBundle,
    results: list[ChainEvidenceBundleValidation],
) -> dict[str, Any]:
    """Return a structured chain bundle validation payload."""

    return {
        "bundle_id": bundle.bundle_id,
        "accepted": all(result.accepted for result in results),
        "chain_claim_id": bundle.chain_claim_id,
        "result_count": len(results),
        "results": [
            {
                "subject": result.subject,
                "accepted": result.accepted,
                "detail": result.detail,
            }
            for result in results
        ],
    }


def run_chain_evidence_bundle_cli(argv: list[str] | None = None) -> int:
    """Run transition-chain evidence bundle validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.chain_evidence_bundle",
        description="Validate an AS transition-chain evidence bundle.",
    )
    parser.add_argument(
        "--bundle",
        default="evidence/chains/neighbor_delivery_chain_bundle.json",
        help="Path to the transition-chain evidence bundle JSON.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    bundle = load_transition_chain_evidence_bundle(args.bundle)
    results = validate_transition_chain_evidence_bundle(bundle)
    if args.format == "json":
        payload = chain_evidence_bundle_report_payload(bundle, results)
        print(json.dumps(payload, sort_keys=True))
    else:
        print(format_chain_evidence_bundle_report(bundle, results))
    return 0 if all(result.accepted for result in results) else 1


def _validate_schema(
    bundle: TransitionChainEvidenceBundle,
) -> ChainEvidenceBundleValidation:
    if bundle.schema_version != 1:
        return _rejected("schema", f"unsupported schema version {bundle.schema_version}")
    if not bundle.bundle_id:
        return _rejected("schema", "bundle id is empty")
    if not bundle.boundaries:
        return _rejected("schema", "bundle must record semantic boundaries")
    if not bundle.chain_claim_validator_path.exists():
        return _rejected(
            "schema",
            f"missing chain claim validator: {bundle.chain_claim_validator_path}",
        )
    return _accepted("schema", "schema version and required fields accepted")


def _validate_chain_claim_example(
    bundle: TransitionChainEvidenceBundle,
) -> tuple[ChainClaim | None, ChainClaimExample | None, ChainEvidenceBundleValidation]:
    try:
        claims = load_transition_chain_claims(bundle.chain_claim_manifest_path)
    except Exception as exc:  # pragma: no cover - defensive path for drifted files.
        return None, None, _rejected(
            "chain-claim-example",
            f"chain claim manifest error: {exc}",
        )

    claim = next(
        (claim for claim in claims if claim.claim_id == bundle.chain_claim_id),
        None,
    )
    if claim is None:
        return (
            None,
            None,
            _rejected("chain-claim-example", f"missing claim {bundle.chain_claim_id}"),
        )
    if claim.predicate != bundle.predicate:
        return (
            claim,
            None,
            _rejected(
                "chain-claim-example",
                f"predicate mismatch: claim has {claim.predicate}",
            ),
        )

    example = next(
        (
            example
            for example in claim.examples
            if example.name == bundle.positive_example
        ),
        None,
    )
    if example is None:
        return (
            claim,
            None,
            _rejected(
                "chain-claim-example",
                f"missing example {bundle.positive_example}",
            ),
        )
    if not example.expected:
        return (
            claim,
            example,
            _rejected("chain-claim-example", "bundle example is not positive"),
        )

    helper = getattr(transition_chains, bundle.transition_chain_function, None)
    if helper is None:
        return (
            claim,
            example,
            _rejected(
                "chain-claim-example",
                f"unknown chain helper: {bundle.transition_chain_function}",
            ),
        )
    checker = getattr(transition_chain_predicates, bundle.predicate, None)
    if checker is None:
        return (
            claim,
            example,
            _rejected(
                "chain-claim-example",
                f"unknown chain predicate checker: {bundle.predicate}",
            ),
        )

    chain = helper(example.sender, example.recipient)
    if chain.status != bundle.expected_status:
        return (
            claim,
            example,
            _rejected(
                "chain-claim-example",
                f"status mismatch: chain has {chain.status}",
            ),
        )
    predicate_result = checker(chain)
    if not predicate_result.holds:
        return (
            claim,
            example,
            _rejected(
                "chain-claim-example",
                f"predicate failed: {predicate_result.detail}",
            ),
        )
    return (
        claim,
        example,
        _accepted("chain-claim-example", "chain example evaluated true"),
    )


def _validate_chain_proof_certificate(
    bundle: TransitionChainEvidenceBundle,
) -> ChainEvidenceBundleValidation:
    try:
        claims = load_transition_chain_claims(bundle.chain_claim_manifest_path)
        certificates = load_proof_certificates(bundle.chain_proof_certificate_path)
        results = verify_chain_claim_certificates(claims, certificates)
    except Exception as exc:  # pragma: no cover - defensive path for drifted files.
        return _rejected(
            "chain-proof-certificate",
            f"chain proof certificate error: {exc}",
        )

    result = next(
        (result for result in results if result.claim_id == bundle.chain_claim_id),
        None,
    )
    if result is None:
        return _rejected(
            "chain-proof-certificate",
            f"missing verification {bundle.chain_claim_id}",
        )
    if not result.accepted:
        return _rejected("chain-proof-certificate", result.detail)
    return _accepted("chain-proof-certificate", result.detail)


def _validate_chain_language(
    bundle: TransitionChainEvidenceBundle,
) -> ChainEvidenceBundleValidation:
    try:
        language = load_transition_chain_claim_language(bundle.chain_language_path)
        claims = load_transition_chain_claims(bundle.chain_claim_manifest_path)
        certificates = load_proof_certificates(bundle.chain_proof_certificate_path)
        language_results = validate_chain_language_manifest(language)
        surface_results = validate_chain_claim_surface(language, claims, certificates)
    except Exception as exc:  # pragma: no cover - defensive path for drifted files.
        return _rejected("chain-language", f"chain language error: {exc}")

    failures = [
        f"{result.subject}: {result.detail}"
        for result in (*language_results, *surface_results)
        if not result.accepted
    ]
    if failures:
        return _rejected("chain-language", " | ".join(failures))
    return _accepted(
        "chain-language",
        f"validated {len(language_results)} language clauses and {len(surface_results)} surface clauses",
    )


def _validate_chain_trace(
    bundle: TransitionChainEvidenceBundle,
) -> ChainEvidenceBundleValidation:
    try:
        trace = load_transition_chain_trace(bundle.chain_trace_path)
        results = validate_transition_chain_trace(trace)
    except Exception as exc:  # pragma: no cover - defensive path for drifted files.
        return _rejected("chain-trace", f"chain trace error: {exc}")

    if trace.claim_id != bundle.chain_claim_id:
        return _rejected("chain-trace", f"claim id mismatch: {trace.claim_id}")
    if trace.expected_status != bundle.expected_status:
        return _rejected("chain-trace", f"status mismatch: {trace.expected_status}")

    failures = [
        f"{result.subject}: {result.detail}"
        for result in results
        if not result.accepted
    ]
    if failures:
        return _rejected("chain-trace", " | ".join(failures))
    return _accepted("chain-trace", f"validated {len(results)} chain trace checks")


def _validate_chain_svg(
    bundle: TransitionChainEvidenceBundle,
) -> ChainEvidenceBundleValidation:
    try:
        trace = load_transition_chain_trace(bundle.chain_trace_path)
        svg_text = bundle.chain_svg_path.read_text(encoding="utf-8")
        results = validate_transition_chain_svg(trace, svg_text=svg_text)
    except Exception as exc:  # pragma: no cover - defensive path for drifted files.
        return _rejected("chain-svg", f"chain SVG error: {exc}")

    failures = [
        f"{result.subject}: {result.detail}"
        for result in results
        if not result.accepted
    ]
    if failures:
        return _rejected("chain-svg", " | ".join(failures))
    return _accepted("chain-svg", f"validated {len(results)} chain SVG checks")


def _validate_underlying_transition_bundles(
    bundle: TransitionChainEvidenceBundle,
) -> ChainEvidenceBundleValidation:
    if not bundle.transition_bundle_paths:
        return _rejected(
            "underlying-transition-bundles",
            "no transition bundle paths recorded",
        )

    failures: list[str] = []
    for path in bundle.transition_bundle_paths:
        try:
            transition_bundle = load_transition_evidence_bundle(path)
            results = validate_transition_evidence_bundle(transition_bundle)
        except Exception as exc:
            failures.append(f"{path}: {exc}")
            continue
        rejected = [result.detail for result in results if not result.accepted]
        if rejected:
            failures.append(f"{path}: {'; '.join(rejected)}")

    if failures:
        return _rejected("underlying-transition-bundles", " | ".join(failures))
    return _accepted(
        "underlying-transition-bundles",
        f"validated {len(bundle.transition_bundle_paths)} transition bundles",
    )


def _validate_source_statuses(
    bundle: TransitionChainEvidenceBundle,
) -> ChainEvidenceBundleValidation:
    if not bundle.source_status_paths:
        return _rejected("source-statuses", "no source-status paths recorded")

    missing: list[str] = []
    invalid: list[str] = []
    for path in bundle.source_status_paths:
        if not path.exists():
            missing.append(str(path))
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            invalid.append(str(path))

    if missing:
        return _rejected("source-statuses", f"missing source-statuses: {', '.join(missing)}")
    if invalid:
        return _rejected("source-statuses", f"invalid JSON: {', '.join(invalid)}")
    return _accepted(
        "source-statuses",
        f"loaded {len(bundle.source_status_paths)} source-status files",
    )


def _validate_boundary(
    bundle: TransitionChainEvidenceBundle,
) -> ChainEvidenceBundleValidation:
    joined = " ".join(bundle.boundaries).lower()
    required_terms = (
        "init-family",
        "non-init",
        "standard-signal",
        "write-buffer",
        "scheduler",
        "topology",
    )
    missing = [term for term in required_terms if term not in joined]
    if missing:
        return _rejected("boundary", f"missing boundary terms: {', '.join(missing)}")
    return _accepted("boundary", "bundle boundaries keep chain limits explicit")


def _accepted(subject: str, detail: str) -> ChainEvidenceBundleValidation:
    return ChainEvidenceBundleValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> ChainEvidenceBundleValidation:
    return ChainEvidenceBundleValidation(subject=subject, accepted=False, detail=detail)


def _required_dict(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required object field missing: {key}")
    return value


def _required_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if not isinstance(value, int):
        raise ValueError(f"required integer field missing: {key}")
    return value


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_text_list(item: dict[str, Any], key: str) -> list[str]:
    value = item.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"required text list missing: {key}")
    if not all(isinstance(entry, str) and entry for entry in value):
        raise ValueError(f"text list has invalid entries: {key}")
    return value


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_chain_evidence_bundle_cli())
