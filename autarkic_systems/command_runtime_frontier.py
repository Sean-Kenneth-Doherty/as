"""Runtime witness summary for the AS command-token frontier.

The source-status frontier says which command-token surfaces are implemented
and which remain blocked. This module checks that statement against a small
set of live Universal Cell transitions without changing the runtime, source
status records, or evidence bundles.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from autarkic_systems.source_status import build_source_status_frontier_report
from autarkic_systems.universal_cell import Cell, StepResult, step_fixed_cell, step_stem_cell


COMMAND_RUNTIME_FRONTIER_SCHEMA_VERSION = 1

TransitionRunner = Callable[[Cell], StepResult]


def build_command_runtime_frontier_report(
    source_status_paths: list[Path | str] | tuple[Path | str, ...] | None = None,
) -> dict[str, Any]:
    """Build the command-runtime frontier report.

    If source-status validation rejects, the report fails closed and does not
    claim runtime implemented state. When source status accepts, the report
    executes the fixed set of runtime witness cases and accepts only if every
    observed status matches the expected frontier boundary.
    """

    source_status = (
        build_source_status_frontier_report()
        if source_status_paths is None
        else build_source_status_frontier_report(source_status_paths)
    )
    source_summary = _source_status_summary(source_status)
    if not source_status["accepted"]:
        return {
            "schema_version": COMMAND_RUNTIME_FRONTIER_SCHEMA_VERSION,
            "accepted": False,
            "source_status": source_summary,
            "runtime_cases": [],
            "evidence_bundles": [],
        }

    runtime_cases = [_runtime_case_payload(case) for case in _runtime_cases()]
    evidence_bundles = _unique_evidence_bundles(runtime_cases)
    return {
        "schema_version": COMMAND_RUNTIME_FRONTIER_SCHEMA_VERSION,
        "accepted": all(case["accepted"] for case in runtime_cases),
        "source_status": source_summary,
        "runtime_cases": runtime_cases,
        "evidence_bundles": evidence_bundles,
    }


def format_command_runtime_frontier_report(report: dict[str, Any]) -> str:
    """Format the command-runtime frontier report for operators."""

    status = "accepted" if report["accepted"] else "rejected"
    source_status = "accepted" if report["source_status"]["accepted"] else "rejected"
    closure = report["source_status"]["closure_summary"]
    lines = [
        f"Command runtime frontier: {status}",
        f"Source-status frontier: {source_status}",
        f"Safe-next queue: {closure['safe_next_slice_state']}",
        "Remaining blocked commands: "
        + _command_text(closure["remaining_blocked_commands"]),
        "Implemented commands: " + _command_text(closure["implemented_commands"]),
        "Preserved unsupported commands: "
        + _command_text(closure["preserved_unsupported_commands"]),
        "Execution changes allowed: "
        + ("yes" if closure["execution_change_allowed"] else "no"),
        f"Reason: {closure['reason']}",
        "Runtime cases:",
    ]
    if not report["runtime_cases"]:
        lines.append("  none")
        return "\n".join(lines)

    for case in report["runtime_cases"]:
        case_status = "accepted" if case["accepted"] else "rejected"
        lines.append(
            f"  {case['case_id']}: {case_status}; "
            f"{case['observed_status']} ({case['transition_function']}); "
            f"evidence: {case['evidence_bundle']}"
        )
    return "\n".join(lines)


def run_command_runtime_frontier_cli(argv: list[str] | None = None) -> int:
    """Run the command-runtime frontier CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.command_runtime_frontier",
        description="Render the AS command-token runtime frontier.",
    )
    parser.add_argument(
        "--source-status",
        action="append",
        default=None,
        help="Source-status JSON path to include in the source frontier.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the runtime frontier report.",
    )
    args = parser.parse_args(argv)
    source_status_paths = (
        [Path(path) for path in args.source_status]
        if args.source_status is not None
        else None
    )
    report = build_command_runtime_frontier_report(source_status_paths)
    if args.format == "json":
        print(json.dumps(report, sort_keys=True))
    else:
        print(format_command_runtime_frontier_report(report))
    return 0 if report["accepted"] else 1


def _source_status_summary(source_status: dict[str, Any]) -> dict[str, Any]:
    frontier = source_status["frontier"]
    return {
        "schema_version": source_status["schema_version"],
        "accepted": source_status["accepted"],
        "blocked_commands": list(frontier["blocked_commands"]),
        "safe_next_slice": frontier["safe_next_slice"],
        "closure_summary": frontier["closure_summary"],
        "failed_subjects": list(frontier["failed_subjects"]),
    }


def _runtime_cases() -> tuple[dict[str, Any], ...]:
    """Return the fixed command-frontier runtime cases.

    These cases deliberately cover both implemented write-buffer command-token
    surfaces and the non-executing standard-signal command-token boundary.
    """

    return (
        {
            "case_id": "recipient-write-buffer-zero",
            "command": "write-buf-zero",
            "surface": "recipient-command-message",
            "runner": step_fixed_cell,
            "transition_function": "step_fixed_cell",
            "cell": Cell(
                role="wire",
                memory="right",
                upstream=("write-buf-zero", "_", "_"),
                buffer=(1,),
            ),
            "expected_status": "recipient-write-buffer-command-message-appended",
            "evidence_bundle": "evidence/recipient_write_buffer_command_message_bundle.json",
        },
        {
            "case_id": "recipient-write-buffer-one",
            "command": "write-buf-one",
            "surface": "recipient-command-message",
            "runner": step_stem_cell,
            "transition_function": "step_stem_cell",
            "cell": Cell(
                role="stem",
                memory="right",
                input=("_", "_", "write-buf-one"),
                self_mailbox="proc-r-init",
                control=(0, 1, 0),
                buffer=(1, 0),
            ),
            "expected_status": "recipient-write-buffer-command-message-appended",
            "evidence_bundle": "evidence/recipient_write_buffer_command_message_bundle.json",
        },
        {
            "case_id": "self-mailbox-write-buffer-one",
            "command": "write-buf-one",
            "surface": "self-mailbox-command",
            "runner": step_stem_cell,
            "transition_function": "step_stem_cell",
            "cell": Cell(
                role="stem",
                memory="left",
                self_mailbox="write-buf-one",
                control=(1, 0, 0),
                buffer=(0,),
            ),
            "expected_status": "self-mailbox-write-buffer-appended",
            "evidence_bundle": "evidence/self_mailbox_write_buffer_bundle.json",
        },
        {
            "case_id": "self-command-buffer-write-buffer-one",
            "command": "write-buf-one",
            "surface": "self-target-command-buffer",
            "runner": step_stem_cell,
            "transition_function": "step_stem_cell",
            "cell": Cell(
                role="stem",
                memory="left",
                input=(0, 1, 0),
                control=(0, 1, 0),
                buffer=(0, 0, 1, 1),
            ),
            "expected_status": "stem-command-buffer-self-write-buffer-appended",
            "evidence_bundle": "evidence/self_command_buffer_write_buffer_bundle.json",
        },
        {
            "case_id": "recipient-standard-signal",
            "command": "standard-signal",
            "surface": "recipient-command-message",
            "runner": step_fixed_cell,
            "transition_function": "step_fixed_cell",
            "cell": Cell(
                role="wire",
                memory="right",
                input=("standard-signal", "_", "_"),
            ),
            "expected_status": "rejected-input",
            "evidence_bundle": "evidence/recipient_non_init_command_rejection_bundle.json",
        },
        {
            "case_id": "self-mailbox-standard-signal",
            "command": "standard-signal",
            "surface": "self-mailbox-command",
            "runner": step_stem_cell,
            "transition_function": "step_stem_cell",
            "cell": Cell(
                role="stem",
                memory="right",
                self_mailbox="standard-signal",
                control=(0, 1, 0),
                buffer=(1,),
            ),
            "expected_status": "self-mailbox-unsupported",
            "evidence_bundle": "evidence/self_mailbox_unsupported_bundle.json",
        },
        {
            "case_id": "self-command-buffer-standard-signal",
            "command": "standard-signal",
            "surface": "self-target-command-buffer",
            "runner": step_stem_cell,
            "transition_function": "step_stem_cell",
            "cell": Cell(
                role="stem",
                memory="right",
                input=(1, 0, 0),
                control=(0, 1, 0),
                buffer=(0, 0, 0, 0),
            ),
            "expected_status": "stem-buffer-appended",
            "evidence_bundle": "evidence/command_buffer_unsupported_bundle.json",
        },
    )


def _runtime_case_payload(case: dict[str, Any]) -> dict[str, Any]:
    runner: TransitionRunner = case["runner"]
    before = case["cell"]
    result = runner(before)
    expected_status = case["expected_status"]
    return {
        "case_id": case["case_id"],
        "command": case["command"],
        "surface": case["surface"],
        "transition_function": case["transition_function"],
        "accepted": result.status == expected_status,
        "expected_status": expected_status,
        "observed_status": result.status,
        "evidence_bundle": case["evidence_bundle"],
        "before": _cell_payload(before),
        "after": _cell_payload(result.cell),
    }


def _cell_payload(cell: Cell) -> dict[str, Any]:
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


def _unique_evidence_bundles(runtime_cases: list[dict[str, Any]]) -> list[str]:
    bundles: list[str] = []
    for case in runtime_cases:
        bundle = case["evidence_bundle"]
        if bundle not in bundles:
            bundles.append(bundle)
    return bundles


def _command_text(commands: list[str]) -> str:
    return ", ".join(commands) if commands else "none"


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess tests.
    raise SystemExit(run_command_runtime_frontier_cli())
