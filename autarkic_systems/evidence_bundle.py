"""Integrated evidence bundles for AS transition slices.

Evidence bundles do not add new Universal Cell behavior. They make an already
implemented slice inspectable across the project layers that justify it:
runtime example, claim, proof certificate, schematic trace, rendered SVG, and
source-status boundaries.
"""

from __future__ import annotations

import argparse
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
class EvidenceBundleRegistryEntry:
    """One registered transition evidence bundle."""

    bundle_id: str
    path: Path
    claim_id: str
    expected_status: str


@dataclass(frozen=True)
class EvidenceBundleRegistry:
    """Project-level index of transition evidence bundles."""

    schema_version: int
    registry_id: str
    reviewed_at: str
    purpose: str
    bundles: tuple[EvidenceBundleRegistryEntry, ...]
    source_path: Path | None = None


@dataclass(frozen=True)
class EvidenceBundleValidation:
    """One validation result for a transition evidence bundle."""

    subject: str
    accepted: bool
    detail: str


def load_evidence_bundle_registry(path: Path | str) -> EvidenceBundleRegistry:
    """Load the project transition evidence bundle registry."""

    registry_path = Path(path)
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    bundles = data.get("bundles")
    if not isinstance(bundles, list) or not bundles:
        raise ValueError("evidence bundle registry must contain a non-empty bundles list")
    return EvidenceBundleRegistry(
        schema_version=_required_int(data, "schema_version"),
        registry_id=_required_text(data, "registry_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        bundles=tuple(_parse_registry_entry(entry) for entry in bundles),
        source_path=registry_path,
    )


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


def validate_evidence_bundle_registry(
    registry: EvidenceBundleRegistry,
) -> list[EvidenceBundleValidation]:
    """Validate every bundle listed in a registry."""

    results = [
        _validate_registry_schema(registry),
        _validate_registry_entries(registry),
        _validate_registry_bundle_paths(registry),
    ]
    results.append(_validate_registry_bundles(registry))
    results.append(_validate_registry_completeness(registry))
    return results


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


def format_registry_validation_report(
    registry: EvidenceBundleRegistry,
    results: list[EvidenceBundleValidation],
) -> str:
    """Format a concise operator report for registry validation results."""

    lines = [f"Evidence bundle registry: {registry.registry_id}"]
    for result in results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_evidence_bundle_cli(argv: list[str] | None = None) -> int:
    """Run the evidence bundle registry validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.evidence_bundle",
        description="Validate the AS transition evidence bundle registry.",
    )
    parser.add_argument(
        "--registry",
        default="evidence/manifest.json",
        help="Path to the evidence bundle registry JSON.",
    )
    args = parser.parse_args(argv)

    registry = load_evidence_bundle_registry(args.registry)
    results = validate_evidence_bundle_registry(registry)
    print(format_registry_validation_report(registry, results))
    return 0 if all(result.accepted for result in results) else 1


def _validate_registry_schema(
    registry: EvidenceBundleRegistry,
) -> EvidenceBundleValidation:
    if registry.schema_version != 1:
        return _rejected(
            "registry-schema",
            f"unsupported schema version {registry.schema_version}",
        )
    if not registry.registry_id:
        return _rejected("registry-schema", "registry id is empty")
    if not registry.bundles:
        return _rejected("registry-schema", "registry has no bundles")
    return _accepted("registry-schema", "registry schema accepted")


def _validate_registry_entries(
    registry: EvidenceBundleRegistry,
) -> EvidenceBundleValidation:
    bundle_ids = [entry.bundle_id for entry in registry.bundles]
    paths = [entry.path for entry in registry.bundles]
    duplicate_ids = sorted(_duplicates(bundle_ids))
    duplicate_paths = sorted(str(path) for path in _duplicates(paths))
    details: list[str] = []
    if duplicate_ids:
        details.append(f"duplicate bundle ids: {', '.join(duplicate_ids)}")
    if duplicate_paths:
        details.append(f"duplicate bundle paths: {', '.join(duplicate_paths)}")
    if details:
        return _rejected("registry-entries", "; ".join(details))
    return _accepted("registry-entries", f"registered {len(registry.bundles)} bundles")


def _validate_registry_bundle_paths(
    registry: EvidenceBundleRegistry,
) -> EvidenceBundleValidation:
    missing = [str(entry.path) for entry in registry.bundles if not entry.path.exists()]
    if missing:
        return _rejected("registry-bundle-paths", f"missing bundle: {', '.join(missing)}")
    return _accepted("registry-bundle-paths", "all registered bundle paths exist")


def _validate_registry_bundles(
    registry: EvidenceBundleRegistry,
) -> EvidenceBundleValidation:
    failures: list[str] = []
    for entry in registry.bundles:
        try:
            bundle = load_transition_evidence_bundle(entry.path)
        except Exception as exc:
            failures.append(f"{entry.path}: {exc}")
            continue

        if bundle.bundle_id != entry.bundle_id:
            failures.append(
                f"{entry.path}: bundle id mismatch {bundle.bundle_id}"
            )
        if bundle.claim_id != entry.claim_id:
            failures.append(f"{entry.path}: claim id mismatch {bundle.claim_id}")
        if bundle.expected_status != entry.expected_status:
            failures.append(
                f"{entry.path}: status mismatch {bundle.expected_status}"
            )

        bundle_results = validate_transition_evidence_bundle(bundle)
        rejected = [result.detail for result in bundle_results if not result.accepted]
        if rejected:
            failures.append(f"{entry.path}: {'; '.join(rejected)}")

    if failures:
        return _rejected("registry-bundle-validation", " | ".join(failures))
    return _accepted(
        "registry-bundle-validation",
        f"validated {len(registry.bundles)} bundles",
    )


def _validate_registry_completeness(
    registry: EvidenceBundleRegistry,
) -> EvidenceBundleValidation:
    registry_dir = _registry_directory(registry)
    registered = {_normalized_path(entry.path) for entry in registry.bundles}
    discovered = {
        _normalized_path(path)
        for path in sorted(registry_dir.glob("*_bundle.json"))
    }
    unregistered = sorted(discovered - registered)
    if unregistered:
        display = ", ".join(str(path) for path in unregistered)
        return _rejected(
            "registry-completeness",
            f"unregistered bundle files: {display}",
        )
    return _accepted(
        "registry-completeness",
        f"all {len(discovered)} discovered bundle files are registered",
    )


def _registry_directory(registry: EvidenceBundleRegistry) -> Path:
    if registry.source_path is None:
        return Path("evidence")
    return registry.source_path.parent


def _parse_registry_entry(item: dict[str, Any]) -> EvidenceBundleRegistryEntry:
    return EvidenceBundleRegistryEntry(
        bundle_id=_required_text(item, "bundle_id"),
        path=Path(_required_text(item, "path")),
        claim_id=_required_text(item, "claim_id"),
        expected_status=_required_text(item, "expected_status"),
    )


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


def _duplicates(items: list[Any]) -> set[Any]:
    seen: set[Any] = set()
    duplicates: set[Any] = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return duplicates


def _normalized_path(path: Path) -> Path:
    return path.resolve(strict=False)


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
    raise SystemExit(run_evidence_bundle_cli())
