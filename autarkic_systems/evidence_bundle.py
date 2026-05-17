"""Integrated evidence bundles for AS transition slices.

Evidence bundles do not add new Universal Cell behavior. They make an already
implemented slice inspectable across the project layers that justify it:
runtime example, claim, proof certificate, schematic trace, rendered SVG, and
source-status boundaries.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.claim_manifest import (
    Claim,
    ClaimExample,
    evaluate_claim_examples,
    load_transition_claims,
)
from autarkic_systems.prc_hardware_map import load_prc_hardware_witness_map
from autarkic_systems.proof_certificates import (
    load_proof_certificates,
    verify_claim_certificates,
)
from autarkic_systems.schematic_svg import render_schematic_svg, validate_schematic_svg
from autarkic_systems.schematic_trace import (
    execute_schematic_trace,
    load_schematic_trace,
    validate_schematic_trace,
)
from autarkic_systems.universal_cell import Cell


@dataclass(frozen=True)
class TransitionEvidenceBundle:
    """One inspectable path from transition behavior to supporting evidence."""

    schema_version: int
    bundle_id: str
    reviewed_at: str
    purpose: str
    claim_id: str
    predicate: str
    positive_example: str
    transition_function: str
    expected_status: str
    claim_manifest_path: Path
    proof_certificate_path: Path
    schematic_trace_path: Path
    schematic_svg_path: Path
    hardware_witness_map_path: Path
    source_status_paths: tuple[Path, ...]
    boundaries: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceBundleValidation:
    """One validation result for a transition evidence bundle."""

    subject: str
    accepted: bool
    detail: str


def load_transition_evidence_bundle(path: Path | str) -> TransitionEvidenceBundle:
    """Load a transition evidence bundle from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    artifacts = _required_dict(data, "artifacts")
    source_status_paths = _required_text_list(artifacts, "source_statuses")
    return TransitionEvidenceBundle(
        schema_version=_required_int(data, "schema_version"),
        bundle_id=_required_text(data, "bundle_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        claim_id=_required_text(data, "claim_id"),
        predicate=_required_text(data, "predicate"),
        positive_example=_required_text(data, "positive_example"),
        transition_function=_required_text(data, "transition_function"),
        expected_status=_required_text(data, "expected_status"),
        claim_manifest_path=Path(_required_text(artifacts, "claim_manifest")),
        proof_certificate_path=Path(_required_text(artifacts, "proof_certificates")),
        schematic_trace_path=Path(_required_text(artifacts, "schematic_trace")),
        schematic_svg_path=Path(_required_text(artifacts, "schematic_svg")),
        hardware_witness_map_path=Path(_required_text(artifacts, "hardware_witness_map")),
        source_status_paths=tuple(Path(path) for path in source_status_paths),
        boundaries=tuple(_required_text_list(data, "boundaries")),
    )


def validate_transition_evidence_bundle(
    bundle: TransitionEvidenceBundle,
) -> list[EvidenceBundleValidation]:
    """Validate a bundle across claim, proof, trace, render, and source layers."""

    results = [_validate_schema(bundle)]
    claim, example, claim_result = _validate_claim_example(bundle)
    results.append(claim_result)
    results.append(_validate_proof_certificate(bundle))
    results.append(_validate_schematic_trace(bundle, example))
    results.append(_validate_schematic_svg(bundle))
    results.append(_validate_source_statuses(bundle))
    results.append(_validate_boundary(bundle))
    return results


def _validate_schema(bundle: TransitionEvidenceBundle) -> EvidenceBundleValidation:
    if bundle.schema_version != 1:
        return _rejected("schema", f"unsupported schema version {bundle.schema_version}")
    if not bundle.bundle_id:
        return _rejected("schema", "bundle id is empty")
    if not bundle.boundaries:
        return _rejected("schema", "bundle must record semantic boundaries")
    return _accepted("schema", "schema version and required fields accepted")


def _validate_claim_example(
    bundle: TransitionEvidenceBundle,
) -> tuple[Claim | None, ClaimExample | None, EvidenceBundleValidation]:
    try:
        claims = load_transition_claims(bundle.claim_manifest_path)
    except Exception as exc:  # pragma: no cover - defensive path for drifted files.
        return None, None, _rejected("claim-example", f"claim manifest error: {exc}")

    claim = next((claim for claim in claims if claim.claim_id == bundle.claim_id), None)
    if claim is None:
        return None, None, _rejected("claim-example", f"missing claim {bundle.claim_id}")
    if claim.predicate != bundle.predicate:
        return (
            claim,
            None,
            _rejected(
                "claim-example",
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
            _rejected("claim-example", f"missing example {bundle.positive_example}"),
        )
    if not example.expected:
        return claim, example, _rejected("claim-example", "bundle example is not positive")
    if example.result.status != bundle.expected_status:
        return (
            claim,
            example,
            _rejected(
                "claim-example",
                f"status mismatch: example has {example.result.status}",
            ),
        )

    evaluations = evaluate_claim_examples([claim])
    matching = next(
        (
            evaluation
            for evaluation in evaluations
            if evaluation.claim_id == bundle.claim_id
            and evaluation.example_name == bundle.positive_example
        ),
        None,
    )
    if matching is None:
        return claim, example, _rejected("claim-example", "example was not evaluated")
    if not matching.matched or not matching.observed:
        return (
            claim,
            example,
            _rejected("claim-example", f"example evaluation failed: {matching.detail}"),
        )

    return claim, example, _accepted("claim-example", "claim example evaluated true")


def _validate_proof_certificate(
    bundle: TransitionEvidenceBundle,
) -> EvidenceBundleValidation:
    try:
        claims = load_transition_claims(bundle.claim_manifest_path)
        certificates = load_proof_certificates(bundle.proof_certificate_path)
        results = verify_claim_certificates(claims, certificates)
    except Exception as exc:  # pragma: no cover - defensive path for drifted files.
        return _rejected("proof-certificate", f"proof certificate error: {exc}")

    certificate = next(
        (certificate for certificate in certificates if certificate.claim_id == bundle.claim_id),
        None,
    )
    if certificate is None:
        return _rejected("proof-certificate", f"missing certificate {bundle.claim_id}")

    result = next(
        (result for result in results if result.claim_id == bundle.claim_id),
        None,
    )
    if result is None:
        return _rejected("proof-certificate", f"missing verification {bundle.claim_id}")
    if not result.accepted:
        return _rejected("proof-certificate", result.detail)
    return _accepted("proof-certificate", result.detail)


def _validate_schematic_trace(
    bundle: TransitionEvidenceBundle,
    example: ClaimExample | None,
) -> EvidenceBundleValidation:
    try:
        trace = load_schematic_trace(bundle.schematic_trace_path)
        witness_map = load_prc_hardware_witness_map(bundle.hardware_witness_map_path)
        execution = execute_schematic_trace(trace)
        trace_results = validate_schematic_trace(trace, hardware_witness_map=witness_map)
    except Exception as exc:
        return _rejected("schematic-trace", f"schematic trace error: {exc}")

    if trace.trace.transition_function != bundle.transition_function:
        return _rejected(
            "schematic-trace",
            f"transition mismatch: trace has {trace.trace.transition_function}",
        )
    if trace.trace.expected_status != bundle.expected_status:
        return _rejected(
            "schematic-trace",
            f"status mismatch: trace has {trace.trace.expected_status}",
        )
    if execution.status != bundle.expected_status:
        return _rejected(
            "schematic-trace",
            f"execution status mismatch: {execution.status}",
        )
    if not all(result.accepted for result in trace_results):
        detail = "; ".join(
            result.detail for result in trace_results if not result.accepted
        )
        return _rejected("schematic-trace", detail)

    if example is not None:
        expected_before = _cell_to_dict(example.before)
        expected_after = _cell_to_dict(example.result.cell)
        if trace.trace.before_cell != expected_before:
            return _rejected("schematic-trace", "trace before cell differs from claim")
        if trace.trace.expected_after_cell != expected_after:
            return _rejected("schematic-trace", "trace after cell differs from claim")

    return _accepted("schematic-trace", "trace executes and matches claim example")


def _validate_schematic_svg(
    bundle: TransitionEvidenceBundle,
) -> EvidenceBundleValidation:
    try:
        trace = load_schematic_trace(bundle.schematic_trace_path)
        try:
            svg_text = bundle.schematic_svg_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return _rejected("schematic-svg", f"missing SVG {bundle.schematic_svg_path}")
        if svg_text != render_schematic_svg(trace):
            return _rejected("schematic-svg", "committed SVG differs from renderer output")
        results = validate_schematic_svg(trace, svg_text=svg_text)
    except Exception as exc:
        return _rejected("schematic-svg", f"schematic SVG error: {exc}")

    if not all(result.accepted for result in results):
        detail = "; ".join(result.detail for result in results if not result.accepted)
        return _rejected("schematic-svg", detail)
    return _accepted("schematic-svg", "committed SVG matches renderer output")


def _validate_source_statuses(
    bundle: TransitionEvidenceBundle,
) -> EvidenceBundleValidation:
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


def _validate_boundary(bundle: TransitionEvidenceBundle) -> EvidenceBundleValidation:
    joined = " ".join(bundle.boundaries).lower()
    required_terms = ("init-family", "non-init", "standard-signal", "write-buffer")
    missing = [term for term in required_terms if term not in joined]
    if missing:
        return _rejected("boundary", f"missing boundary terms: {', '.join(missing)}")
    return _accepted("boundary", "bundle boundaries keep blocked semantics explicit")


def _cell_to_dict(cell: Cell) -> dict[str, Any]:
    return {
        "role": cell.role,
        "memory": cell.memory,
        "upstream": list(cell.upstream),
        "input": list(cell.input),
        "output": list(cell.output),
        "automail": cell.automail,
        "self_mailbox": cell.self_mailbox,
        "control": list(cell.control),
        "buffer": list(cell.buffer),
    }


def _accepted(subject: str, detail: str) -> EvidenceBundleValidation:
    return EvidenceBundleValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> EvidenceBundleValidation:
    return EvidenceBundleValidation(subject=subject, accepted=False, detail=detail)


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
