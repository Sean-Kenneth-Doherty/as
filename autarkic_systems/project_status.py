"""Operator-facing project status over the current AS evidence surface.

The project has separate validators for transition evidence bundles,
transition-chain evidence bundles, and source-status records that explain why
some command-token semantics remain blocked. This module gathers those
existing artifacts into one report without adding new validation semantics.
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
from autarkic_systems.evidence_bundle import (
    load_evidence_bundle_registry,
    registry_validation_report_payload,
    validate_evidence_bundle_registry,
)


DEFAULT_TRANSITION_REGISTRY = Path("evidence/manifest.json")
DEFAULT_CHAIN_REGISTRY = Path("evidence/chains/manifest.json")
DEFAULT_SOURCE_STATUS_PATHS = (
    Path("sources/recipient_non_init_command_source_status.json"),
    Path("sources/standard_signal_command_semantics_status.json"),
    Path("sources/write_buffer_command_semantics_status.json"),
)
BLOCKED_COMMAND_ORDER = (
    "standard-signal",
    "write-buf-zero",
    "write-buf-one",
)


def build_project_status_report(
    transition_registry_path: Path | str = DEFAULT_TRANSITION_REGISTRY,
    chain_registry_path: Path | str = DEFAULT_CHAIN_REGISTRY,
    source_status_paths: list[Path | str] | tuple[Path | str, ...] = DEFAULT_SOURCE_STATUS_PATHS,
) -> dict[str, Any]:
    """Build a status report from registries and source-status records."""

    transition_summary = _transition_registry_summary(transition_registry_path)
    chain_summary = _chain_registry_summary(chain_registry_path)
    frontier = _frontier_summary(source_status_paths)
    accepted = (
        transition_summary["accepted"]
        and chain_summary["accepted"]
        and not frontier["missing_source_statuses"]
        and not frontier["invalid_source_statuses"]
    )
    return {
        "accepted": accepted,
        "transition_evidence": transition_summary,
        "chain_evidence": chain_summary,
        "frontier": frontier,
    }


def format_project_status_report(report: dict[str, Any]) -> str:
    """Format a concise human-readable project status report."""

    status = "accepted" if report["accepted"] else "rejected"
    transition = report["transition_evidence"]
    chain = report["chain_evidence"]
    frontier = report["frontier"]
    transition_status = "accepted" if transition["accepted"] else "rejected"
    chain_status = "accepted" if chain["accepted"] else "rejected"
    blocked_commands = frontier["blocked_commands"] or []
    missing_registries = [
        summary["path"]
        for summary in (transition, chain)
        if "registry-file" in summary["failed_subjects"]
    ]
    invalid_registries = [
        summary["path"]
        for summary in (transition, chain)
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
        "Blocked commands: "
        + (", ".join(blocked_commands) if blocked_commands else "none"),
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
        "--source-status",
        action="append",
        default=None,
        help="Source-status JSON path to include in the frontier summary.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
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
        source_status_paths=source_status_paths,
    )
    if args.format == "json":
        print(json.dumps(report, sort_keys=True))
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


def _registry_summary(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    failed_subjects = [
        result["subject"] for result in payload["results"] if not result["accepted"]
    ]
    return {
        "registry_id": payload["registry_id"],
        "path": str(path),
        "accepted": payload["accepted"],
        "bundle_count": payload["bundle_count"],
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
            invalid.append({"path": str(path), "error": str(exc)})
            continue

        safe_next_slice = _optional_text(data, "safe_next_slice")
        if safe_next_slice:
            safe_next_slices.append(safe_next_slice)
        blocked_commands.update(_blocked_commands_from_status(data))
        source_statuses.append(
            {
                "path": str(path),
                "decision": _optional_text(data, "decision"),
                "safe_next_slice": safe_next_slice,
                "as_boundary": _optional_text(data, "as_boundary"),
            }
        )

    failed_subjects = []
    if missing:
        failed_subjects.append("source-status-file")
    if invalid:
        failed_subjects.append("source-status-json")
    return {
        "blocked_commands": _ordered_blocked_commands(blocked_commands),
        "failed_subjects": failed_subjects,
        "safe_next_slice": _common_or_joined(safe_next_slices),
        "source_statuses": source_statuses,
        "missing_source_statuses": missing,
        "invalid_source_statuses": invalid,
    }


def _blocked_commands_from_status(data: dict[str, Any]) -> set[str]:
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
