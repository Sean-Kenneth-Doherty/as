"""Operator-facing vertical reports for transition-chain evidence.

The project deliberately stores claims, proof certificates, language manifests,
traces, rendered schematics, source-status records, and evidence bundles as
separate artifacts. This module provides a first-run view over that split
surface without becoming a second validator: it delegates acceptance checks to
``chain_evidence_bundle`` and formats the already-validated path as a compact
claim-to-evidence report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from autarkic_systems.chain_evidence_bundle import (
    chain_evidence_bundle_report_payload,
    chain_registry_validation_report_payload,
    load_chain_evidence_bundle_registry,
    load_transition_chain_evidence_bundle,
    validate_chain_evidence_bundle_registry,
    validate_transition_chain_evidence_bundle,
)


DEFAULT_CHAIN_BUNDLE = Path("evidence/chains/neighbor_delivery_chain_bundle.json")
DEFAULT_CHAIN_REGISTRY = Path("evidence/chains/manifest.json")


def build_chain_demo_report(
    bundle_path: Path | str = DEFAULT_CHAIN_BUNDLE,
) -> dict[str, Any]:
    """Build one vertical report over a transition-chain evidence bundle."""

    bundle = load_transition_chain_evidence_bundle(bundle_path)
    results = validate_transition_chain_evidence_bundle(bundle)
    validation = chain_evidence_bundle_report_payload(bundle, results)
    evidence_layers = _evidence_layers(bundle)
    return {
        "accepted": validation["accepted"],
        "bundle_id": bundle.bundle_id,
        "chain_claim_id": bundle.chain_claim_id,
        "predicate": bundle.predicate,
        "positive_example": bundle.positive_example,
        "transition_chain_function": bundle.transition_chain_function,
        "expected_status": bundle.expected_status,
        "validation": {
            "accepted": validation["accepted"],
            "failed_subjects": validation["failed_subjects"],
            "result_count": validation["result_count"],
            "results": validation["results"],
        },
        "evidence_layers": evidence_layers,
        "missing_evidence_paths": _missing_evidence_paths(evidence_layers),
        "boundaries": list(bundle.boundaries),
    }


def format_chain_demo_report(report: dict[str, Any]) -> str:
    """Format a human-readable vertical chain evidence report."""

    layers = report["evidence_layers"]
    transition_bundles = _paths_for_role(layers, "transition-bundle")
    source_statuses = _paths_for_role(layers, "source-status")
    validation = report["validation"]
    status = "accepted" if report["accepted"] else "rejected"
    failed_subjects = validation["failed_subjects"] or []
    missing_paths = report["missing_evidence_paths"] or []

    lines = [
        f"Vertical chain demo: {report['bundle_id']}",
        f"Claim: {report['chain_claim_id']}",
        f"Predicate: {report['predicate']}",
        f"Example: {report['positive_example']}",
        f"Chain function: {report['transition_chain_function']}",
        f"Expected status: {report['expected_status']}",
        f"Validation: {status}",
        f"Validation checks: {validation['result_count']}",
        f"Failed subjects: {', '.join(failed_subjects) if failed_subjects else 'none'}",
        f"Missing evidence paths: {', '.join(missing_paths) if missing_paths else 'none'}",
        f"Claim manifest: {_path_for_role(layers, 'chain-claim-manifest')}",
        f"Proof certificates: {_path_for_role(layers, 'chain-proof-certificates')}",
        f"Language: {_path_for_role(layers, 'chain-language')}",
        f"Trace: {_path_for_role(layers, 'chain-trace')}",
        f"SVG: {_path_for_role(layers, 'chain-svg')}",
        f"Transition bundles: {len(transition_bundles)}",
    ]
    lines.extend(f"- {path}" for path in transition_bundles)
    lines.append(f"Source-status boundaries: {len(source_statuses)}")
    lines.extend(f"- {path}" for path in source_statuses)
    lines.append("Boundary terms:")
    lines.extend(f"- {boundary}" for boundary in report["boundaries"])
    return "\n".join(lines)


def build_chain_demo_registry_report(
    registry_path: Path | str = DEFAULT_CHAIN_REGISTRY,
) -> dict[str, Any]:
    """Build vertical demo reports for every bundle in a chain registry."""

    registry = load_chain_evidence_bundle_registry(registry_path)
    registry_results = validate_chain_evidence_bundle_registry(registry)
    validation = chain_registry_validation_report_payload(registry, registry_results)
    bundle_reports = [
        build_chain_demo_report(entry.path)
        for entry in registry.bundles
        if entry.path.exists()
    ]
    missing_paths = sorted({
        str(entry.path) for entry in registry.bundles if not entry.path.exists()
    } | {
        path
        for report in bundle_reports
        for path in report["missing_evidence_paths"]
    })
    accepted_count = sum(1 for report in bundle_reports if report["accepted"])
    return {
        "accepted": validation["accepted"]
        and all(report["accepted"] for report in bundle_reports),
        "registry_id": registry.registry_id,
        "bundle_count": len(registry.bundles),
        "accepted_count": accepted_count,
        "failed_count": len(registry.bundles) - accepted_count,
        "missing_evidence_paths": missing_paths,
        "validation": {
            "accepted": validation["accepted"],
            "failed_subjects": validation["failed_subjects"],
            "result_count": validation["result_count"],
            "results": validation["results"],
        },
        "bundle_reports": bundle_reports,
    }


def format_chain_demo_registry_report(report: dict[str, Any]) -> str:
    """Format a human-readable report for a chain demo registry."""

    missing_paths = report["missing_evidence_paths"] or []
    lines = [
        f"Vertical chain demo registry: {report['registry_id']}",
        f"Bundles: {report['bundle_count']}",
        f"Accepted: {report['accepted_count']}",
        f"Failed: {report['failed_count']}",
        f"Missing evidence paths: {', '.join(missing_paths) if missing_paths else 'none'}",
    ]
    for bundle_report in report["bundle_reports"]:
        status = "accepted" if bundle_report["accepted"] else "rejected"
        lines.extend(
            [
                "",
                f"- {bundle_report['bundle_id']}: {status}",
                f"  Claim: {bundle_report['chain_claim_id']}",
                f"  Expected status: {bundle_report['expected_status']}",
                "  Missing evidence paths: "
                + (
                    ", ".join(bundle_report["missing_evidence_paths"])
                    if bundle_report["missing_evidence_paths"]
                    else "none"
                ),
            ]
        )
    return "\n".join(lines)


def run_chain_demo_cli(argv: list[str] | None = None) -> int:
    """Run the vertical chain demo report CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.chain_demo",
        description="Render an AS transition-chain evidence demo report.",
    )
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "--bundle",
        default=None,
        help="Path to the transition-chain evidence bundle JSON.",
    )
    target_group.add_argument(
        "--registry",
        default=None,
        help="Path to a transition-chain evidence registry JSON.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the demo report.",
    )
    args = parser.parse_args(argv)

    if args.registry is not None:
        report = build_chain_demo_registry_report(args.registry)
        if args.format == "json":
            print(json.dumps(report, sort_keys=True))
        else:
            print(format_chain_demo_registry_report(report))
        return 0 if report["accepted"] else 1

    report = build_chain_demo_report(args.bundle or DEFAULT_CHAIN_BUNDLE)
    if args.format == "json":
        print(json.dumps(report, sort_keys=True))
    else:
        print(format_chain_demo_report(report))
    return 0 if report["accepted"] else 1


def _evidence_layers(bundle: Any) -> list[dict[str, Any]]:
    layers = [
        {
            "role": "chain-claim-manifest",
            "path": str(bundle.chain_claim_manifest_path),
        },
        {
            "role": "chain-proof-certificates",
            "path": str(bundle.chain_proof_certificate_path),
        },
        {
            "role": "chain-language",
            "path": str(bundle.chain_language_path),
        },
        {
            "role": "chain-claim-validator",
            "path": str(bundle.chain_claim_validator_path),
        },
        {
            "role": "chain-trace",
            "path": str(bundle.chain_trace_path),
        },
        {
            "role": "chain-svg",
            "path": str(bundle.chain_svg_path),
        },
    ]
    layers.extend(
        {"role": "transition-bundle", "path": str(path)}
        for path in bundle.transition_bundle_paths
    )
    layers.extend(
        {"role": "source-status", "path": str(path)}
        for path in bundle.source_status_paths
    )
    return [_with_presence(layer) for layer in layers]


def _with_presence(layer: dict[str, str]) -> dict[str, Any]:
    return {
        "role": layer["role"],
        "path": layer["path"],
        "exists": Path(layer["path"]).is_file(),
    }


def _missing_evidence_paths(layers: list[dict[str, Any]]) -> list[str]:
    return [layer["path"] for layer in layers if not layer["exists"]]


def _path_for_role(layers: list[dict[str, Any]], role: str) -> str:
    for layer in layers:
        if layer["role"] == role:
            return layer["path"]
    raise ValueError(f"missing evidence layer role {role}")


def _paths_for_role(layers: list[dict[str, Any]], role: str) -> list[str]:
    return [layer["path"] for layer in layers if layer["role"] == role]


if __name__ == "__main__":
    raise SystemExit(run_chain_demo_cli())
