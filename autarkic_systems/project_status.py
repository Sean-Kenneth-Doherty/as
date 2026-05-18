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
PROJECT_STATUS_SCHEMA_VERSION = 9
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
        "schema_version": PROJECT_STATUS_SCHEMA_VERSION,
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
        *_registry_bundle_text_lines("Transition evidence", transition),
        *_registry_bundle_text_lines("Chain evidence", chain),
        "Blocked commands: "
        + (", ".join(blocked_commands) if blocked_commands else "none"),
        *_blocked_runtime_surface_text_lines(frontier),
        *_as_boundary_text_lines(frontier),
        *_resolution_question_text_lines(frontier),
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
        if safe_next_slice:
            safe_next_slices.append(safe_next_slice)
        source_commands = _blocked_commands_from_status(data)
        blocked_commands.update(source_commands)
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
                "resolved_resolution_questions": _resolved_resolution_questions(data),
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
        resolved_questions.append(resolved_question)
    return resolved_questions


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
    if len(lines) == 1:
        return ["Resolved resolution questions: none"]
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
    if not _blocked_commands_from_status(data):
        return "source-status command fields must include at least one command token"
    surface_error = _blocked_runtime_surface_shape_error(data)
    if surface_error:
        return surface_error
    question_error = _resolution_question_shape_error(data)
    if question_error:
        return question_error
    resolved_question_error = _resolved_resolution_question_shape_error(data)
    if resolved_question_error:
        return resolved_question_error
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
