import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.project_status import (
    build_project_status_report,
    format_project_status_report,
    run_project_status_cli,
)


TRANSITION_REGISTRY = Path("evidence/manifest.json")
CHAIN_REGISTRY = Path("evidence/chains/manifest.json")
RECIPIENT_STATUS = Path("sources/recipient_non_init_command_source_status.json")
STANDARD_SIGNAL_STATUS = Path("sources/standard_signal_command_semantics_status.json")
WRITE_BUFFER_STATUS = Path("sources/write_buffer_command_semantics_status.json")
BLOCKED_COMMANDS = ["standard-signal", "write-buf-zero", "write-buf-one"]
SAFE_NEXT_SLICE = "revisit-standard-signal-or-write-buffer-command-semantics"
PROJECT_STATUS_SCHEMA_VERSION = 8
BLOCKED_RUNTIME_SURFACES = [
    "recipient-command-message",
    "self-mailbox-command",
    "self-target-command-buffer",
]
RECIPIENT_NON_INIT_AS_BOUNDARY = (
    "Continue rejecting recipient non-init command-message inputs while AS "
    "keeps standard-signal and write-buffer command tokens source-blocked; "
    "the accepted behavior is the ADR-0054 rejection boundary, with "
    "multi-command conflicts assigned to ADR-0059 reject-and-clear."
)
STANDARD_SIGNAL_AS_BOUNDARY = (
    "Continue rejecting or preserving standard-signal command tokens at the "
    "existing claimed boundaries. AS already has ordinary standard-signal "
    "routing and stem buffer accumulation for binary input; this artifact "
    "blocks only command-token execution."
)
WRITE_BUFFER_AS_BOUNDARY = (
    "Continue rejecting or preserving write-buffer commands at the existing "
    "claimed boundaries until a later ADR selects one source-backed execution "
    "semantics."
)
TRANSITION_BUNDLES = [
    {
        "bundle_id": "recipient-init-command-message-transition-evidence-bundle",
        "path": "evidence/recipient_init_command_message_bundle.json",
        "claim_id": "UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED",
        "expected_status": "recipient-init-command-message-processed",
        "positive_example": "fixed upstream wire right init processed",
        "covered_positive_examples": ["fixed upstream wire right init processed"],
    },
    {
        "bundle_id": "recipient-non-init-command-rejection-evidence-bundle",
        "path": "evidence/recipient_non_init_command_rejection_bundle.json",
        "claim_id": "UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED",
        "expected_status": "rejected-input",
        "positive_example": "fixed upstream standard-signal command rejected",
        "covered_positive_examples": ["fixed upstream standard-signal command rejected"],
    },
    {
        "bundle_id": "multi-command-recipient-rejection-evidence-bundle",
        "path": "evidence/multi_command_recipient_rejection_bundle.json",
        "claim_id": "UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED",
        "expected_status": "rejected-input",
        "positive_example": "fixed all-init command conflict rejected",
        "covered_positive_examples": ["fixed all-init command conflict rejected"],
    },
    {
        "bundle_id": "self-mailbox-init-evidence-bundle",
        "path": "evidence/self_mailbox_init_bundle.json",
        "claim_id": "UC-STEM-SELF-MAILBOX-INIT-COMMAND",
        "expected_status": "self-mailbox-processed",
        "positive_example": "processor left mailbox init",
        "covered_positive_examples": ["processor left mailbox init"],
    },
    {
        "bundle_id": "self-mailbox-unsupported-evidence-bundle",
        "path": "evidence/self_mailbox_unsupported_bundle.json",
        "claim_id": "UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED",
        "expected_status": "self-mailbox-unsupported",
        "positive_example": "write buffer one unsupported preserved",
        "covered_positive_examples": [
            "standard signal unsupported preserved",
            "write buffer zero unsupported preserved",
            "write buffer one unsupported preserved",
        ],
    },
    {
        "bundle_id": "self-command-buffer-init-evidence-bundle",
        "path": "evidence/self_command_buffer_init_bundle.json",
        "claim_id": "UC-STEM-COMMAND-BUFFER-SELF-INIT",
        "expected_status": "stem-command-buffer-self-processed",
        "positive_example": "self command buffer processor left init",
        "covered_positive_examples": ["self command buffer processor left init"],
    },
    {
        "bundle_id": "command-buffer-unsupported-evidence-bundle",
        "path": "evidence/command_buffer_unsupported_bundle.json",
        "claim_id": "UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED",
        "expected_status": "stem-buffer-appended",
        "positive_example": "self write buffer command remains appended",
        "covered_positive_examples": [
            "self standard signal command remains appended",
            "self write buffer zero command remains appended",
            "self write buffer command remains appended",
        ],
    },
    {
        "bundle_id": "neighbor-command-buffer-delivery-evidence-bundle",
        "path": "evidence/neighbor_command_buffer_delivery_bundle.json",
        "claim_id": "UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED",
        "expected_status": "stem-command-buffer-neighbor-delivered",
        "positive_example": "neighbor b proc left command delivered",
        "covered_positive_examples": ["neighbor b proc left command delivered"],
    },
]
CHAIN_BUNDLES = [
    {
        "bundle_id": "neighbor-delivery-recipient-chain-evidence-bundle",
        "path": "evidence/chains/neighbor_delivery_chain_bundle.json",
        "chain_claim_id": "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED",
        "expected_status": "neighbor-delivery-consumed",
    },
    {
        "bundle_id": "neighbor-delivery-recipient-rejection-chain-evidence-bundle",
        "path": "evidence/chains/neighbor_delivery_rejection_chain_bundle.json",
        "chain_claim_id": "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED",
        "expected_status": "recipient-not-consumed",
    },
]
STANDARD_SIGNAL_QUESTIONS = [
    "command-token-vs-binary-input",
    "recipient-surface",
    "self-target-surface",
]
WRITE_BUFFER_QUESTIONS = [
    "recipient-vs-stem-surface",
    "buffer-full-boundary",
    "post-append-clearing",
    "standard-signal-interaction",
]
STANDARD_SIGNAL_RESOLUTION_QUESTIONS = [
    {
        "question_id": "command-token-vs-binary-input",
        "summary": (
            "Decide whether a standard-signal command token is supposed to "
            "reproduce ordinary binary-input standard-signal behavior or "
            "remain a separate unsupported command."
        ),
    },
    {
        "question_id": "recipient-surface",
        "summary": (
            "Decide whether delivered recipient command-message inputs may "
            "execute standard-signal at all, or whether standard-signal "
            "remains limited to ordinary binary channel input."
        ),
    },
    {
        "question_id": "self-target-surface",
        "summary": (
            "Decide whether self-mailbox and self-target command-buffer "
            "standard-signal tokens should execute, be preserved, or be "
            "reported as unsupported."
        ),
    },
]
WRITE_BUFFER_RESOLUTION_QUESTIONS = [
    {
        "question_id": "recipient-vs-stem-surface",
        "summary": (
            "Decide whether write-buffer command messages execute on fixed "
            "recipient cells, stem cells only, or only through self-mailbox / "
            "command-buffer surfaces."
        ),
    },
    {
        "question_id": "buffer-full-boundary",
        "summary": (
            "Decide whether write-buffer commands are ignored, rejected, "
            "preserve state, or report a status when the command buffer is "
            "full."
        ),
    },
    {
        "question_id": "post-append-clearing",
        "summary": (
            "Decide whether write-buffer execution preserves the appended "
            "buffer, clears it like SEMSIM's stem wrapper, or clears only "
            "input/mail state."
        ),
    },
    {
        "question_id": "standard-signal-interaction",
        "summary": (
            "Decide how write-buffer commands interact with the high rail and "
            "standard-signal command-buffer path."
        ),
    },
]
STANDARD_SIGNAL_ADDITIONAL_SOURCE_STATUSES = [
    {
        "adr": "ADR-0062",
        "path": "sources/guile_asmsim_command_semantics_status.json",
        "summary": (
            "guile-asmsim.scm keeps standard signals as ordinary binary input "
            "while process-buffer appends numeric standard-signals to its "
            "command list; this strengthens the command-token blocker rather "
            "than resolving it."
        ),
    },
    {
        "adr": "ADR-0063",
        "path": "sources/asmsim_process_buffer_status.json",
        "summary": (
            "practice/asmsim.scm uses process-buffer code-shape predicates and "
            "a tar+sic? helper rather than the formal standard-signal command "
            "token, with comments warning that message codes need "
            "documentation and confirmation."
        ),
    },
    {
        "adr": "ADR-0064",
        "path": "sources/official_tla_universal_cell_status.json",
        "summary": (
            "The official PRC TLA files are partial/stub/empty and do not "
            "define standard-signal command-token semantics."
        ),
    },
]
WRITE_BUFFER_ADDITIONAL_SOURCE_STATUSES = [
    {
        "adr": "ADR-0062",
        "path": "sources/guile_asmsim_command_semantics_status.json",
        "summary": (
            "guile-asmsim.scm exposes binary write-buf and self-mailbox "
            "numeric append behavior, but omits named "
            "write-buf-zero/write-buf-one command tokens from its "
            "special-message list."
        ),
    },
    {
        "adr": "ADR-0063",
        "path": "sources/asmsim_process_buffer_status.json",
        "summary": (
            "practice/asmsim.scm process-buffer code has id+10b5?/id+11b5? "
            "branches and explicit message-code uncertainty, but no named "
            "write-buf-zero/write-buf-one command-token surface."
        ),
    },
    {
        "adr": "ADR-0064",
        "path": "sources/official_tla_universal_cell_status.json",
        "summary": (
            "The official PRC TLA files are partial/stub/empty and do not "
            "define write-buf-zero or write-buf-one command-token semantics."
        ),
    },
]


class ProjectStatusReportTests(unittest.TestCase):
    def test_status_payload_summarizes_evidence_registries_and_frontier(self):
        report = build_project_status_report()

        self.assertTrue(report["accepted"])
        self.assertEqual(report["schema_version"], PROJECT_STATUS_SCHEMA_VERSION)
        self.assertEqual(
            report["transition_evidence"]["registry_id"],
            "transition-evidence-bundle-registry",
        )
        self.assertTrue(report["transition_evidence"]["accepted"])
        self.assertEqual(report["transition_evidence"]["bundle_count"], 8)
        self.assertEqual(
            report["transition_evidence"]["bundles"],
            TRANSITION_BUNDLES,
        )
        self.assertEqual(
            report["chain_evidence"]["registry_id"],
            "transition-chain-evidence-bundle-registry",
        )
        self.assertTrue(report["chain_evidence"]["accepted"])
        self.assertEqual(report["chain_evidence"]["bundle_count"], 2)
        self.assertEqual(report["chain_evidence"]["bundles"], CHAIN_BUNDLES)
        self.assertEqual(report["frontier"]["blocked_commands"], BLOCKED_COMMANDS)
        self.assertEqual(report["frontier"]["failed_subjects"], [])
        self.assertEqual(report["frontier"]["safe_next_slice"], SAFE_NEXT_SLICE)
        self.assertEqual(report["frontier"]["missing_source_statuses"], [])
        self.assertEqual(
            [item["path"] for item in report["frontier"]["source_statuses"]],
            [
                str(RECIPIENT_STATUS),
                str(STANDARD_SIGNAL_STATUS),
                str(WRITE_BUFFER_STATUS),
            ],
        )
        self.assertEqual(
            [item["commands"] for item in report["frontier"]["source_statuses"]],
            [
                BLOCKED_COMMANDS,
                ["standard-signal"],
                ["write-buf-zero", "write-buf-one"],
            ],
        )
        self.assertEqual(
            [
                item["blocked_runtime_surfaces"]
                for item in report["frontier"]["source_statuses"]
            ],
            [
                [],
                BLOCKED_RUNTIME_SURFACES,
                BLOCKED_RUNTIME_SURFACES,
            ],
        )
        self.assertEqual(
            [
                item["as_boundary"]
                for item in report["frontier"]["source_statuses"]
            ],
            [
                RECIPIENT_NON_INIT_AS_BOUNDARY,
                STANDARD_SIGNAL_AS_BOUNDARY,
                WRITE_BUFFER_AS_BOUNDARY,
            ],
        )
        self.assertEqual(
            [
                item["required_resolution_questions"]
                for item in report["frontier"]["source_statuses"]
            ],
            [
                [],
                STANDARD_SIGNAL_QUESTIONS,
                WRITE_BUFFER_QUESTIONS,
            ],
        )
        self.assertEqual(
            [
                item["resolution_questions"]
                for item in report["frontier"]["source_statuses"]
            ],
            [
                [],
                STANDARD_SIGNAL_RESOLUTION_QUESTIONS,
                WRITE_BUFFER_RESOLUTION_QUESTIONS,
            ],
        )
        self.assertEqual(
            [
                item["additional_source_statuses"]
                for item in report["frontier"]["source_statuses"]
            ],
            [
                [],
                STANDARD_SIGNAL_ADDITIONAL_SOURCE_STATUSES,
                WRITE_BUFFER_ADDITIONAL_SOURCE_STATUSES,
            ],
        )

    def test_text_status_names_green_evidence_and_blocked_commands(self):
        report = build_project_status_report()

        text = format_project_status_report(report)

        self.assertIn("Autarkic Systems project status: accepted", text)
        self.assertIn("Transition evidence: accepted (8 bundles)", text)
        self.assertIn("Chain evidence: accepted (2 bundles)", text)
        self.assertIn("Transition evidence bundles:", text)
        self.assertIn(
            "recipient-init-command-message-transition-evidence-bundle -> "
            "evidence/recipient_init_command_message_bundle.json",
            text,
        )
        self.assertIn(
            "neighbor-command-buffer-delivery-evidence-bundle -> "
            "evidence/neighbor_command_buffer_delivery_bundle.json",
            text,
        )
        self.assertIn(
            "positive example: write buffer one unsupported preserved",
            text,
        )
        self.assertIn(
            "covered examples: standard signal unsupported preserved; "
            "write buffer zero unsupported preserved; "
            "write buffer one unsupported preserved",
            text,
        )
        self.assertIn(
            "positive example: self write buffer command remains appended",
            text,
        )
        self.assertIn(
            "covered examples: self standard signal command remains appended; "
            "self write buffer zero command remains appended; "
            "self write buffer command remains appended",
            text,
        )
        self.assertIn("Chain evidence bundles:", text)
        self.assertIn(
            "neighbor-delivery-recipient-chain-evidence-bundle -> "
            "evidence/chains/neighbor_delivery_chain_bundle.json",
            text,
        )
        self.assertIn(
            "neighbor-delivery-recipient-rejection-chain-evidence-bundle -> "
            "evidence/chains/neighbor_delivery_rejection_chain_bundle.json",
            text,
        )
        self.assertIn(
            "Blocked commands: standard-signal, write-buf-zero, write-buf-one",
            text,
        )
        self.assertIn("Blocked runtime surfaces:", text)
        self.assertIn(
            "standard-signal: recipient-command-message, "
            "self-mailbox-command, self-target-command-buffer",
            text,
        )
        self.assertIn("AS boundaries:", text)
        self.assertIn(
            "standard-signal, write-buf-zero, write-buf-one: "
            f"{RECIPIENT_NON_INIT_AS_BOUNDARY}",
            text,
        )
        self.assertIn(
            f"standard-signal: {STANDARD_SIGNAL_AS_BOUNDARY}",
            text,
        )
        self.assertIn(
            f"write-buf-zero, write-buf-one: {WRITE_BUFFER_AS_BOUNDARY}",
            text,
        )
        self.assertIn(
            "Safe next slice: revisit-standard-signal-or-write-buffer-command-semantics",
            text,
        )
        self.assertIn("Missing source-status files: none", text)

    def test_text_status_names_no_blocked_runtime_surfaces_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            no_surface_status = Path(tmp) / "no_surface_status.json"
            no_surface_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[no_surface_status],
            )

        text = format_project_status_report(report)
        self.assertIn("Blocked runtime surfaces: none", text)

    def test_text_status_names_resolution_question_summaries(self):
        report = build_project_status_report()

        text = format_project_status_report(report)

        self.assertIn("Resolution questions:", text)
        self.assertIn("standard-signal:", text)
        self.assertIn(
            "command-token-vs-binary-input: Decide whether a standard-signal "
            "command token is supposed to reproduce ordinary binary-input "
            "standard-signal behavior or remain a separate unsupported command.",
            text,
        )
        self.assertIn("write-buf-zero, write-buf-one:", text)
        self.assertIn(
            "post-append-clearing: Decide whether write-buffer execution "
            "preserves the appended buffer, clears it like SEMSIM's stem "
            "wrapper, or clears only input/mail state.",
            text,
        )

    def test_text_status_names_additional_source_statuses(self):
        report = build_project_status_report()

        text = format_project_status_report(report)

        self.assertIn("Additional source statuses:", text)
        self.assertIn("standard-signal:", text)
        self.assertIn(
            "ADR-0062 -> sources/guile_asmsim_command_semantics_status.json: "
            "guile-asmsim.scm keeps standard signals as ordinary binary input "
            "while process-buffer appends numeric standard-signals to its "
            "command list; this strengthens the command-token blocker rather "
            "than resolving it.",
            text,
        )
        self.assertIn(
            "ADR-0063 -> sources/asmsim_process_buffer_status.json: "
            "practice/asmsim.scm uses process-buffer code-shape predicates and "
            "a tar+sic? helper rather than the formal standard-signal command "
            "token, with comments warning that message codes need "
            "documentation and confirmation.",
            text,
        )
        self.assertIn(
            "ADR-0064 -> sources/official_tla_universal_cell_status.json: "
            "The official PRC TLA files are partial/stub/empty and do not "
            "define standard-signal command-token semantics.",
            text,
        )
        self.assertIn("write-buf-zero, write-buf-one:", text)
        self.assertIn(
            "ADR-0062 -> sources/guile_asmsim_command_semantics_status.json: "
            "guile-asmsim.scm exposes binary write-buf and self-mailbox "
            "numeric append behavior, but omits named "
            "write-buf-zero/write-buf-one command tokens from its "
            "special-message list.",
            text,
        )
        self.assertIn(
            "ADR-0064 -> sources/official_tla_universal_cell_status.json: "
            "The official PRC TLA files are partial/stub/empty and do not "
            "define write-buf-zero or write-buf-one command-token semantics.",
            text,
        )

    def test_text_status_names_no_additional_source_statuses_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            no_additional_status = Path(tmp) / "no_additional_status.json"
            no_additional_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[no_additional_status],
            )

        text = format_project_status_report(report)
        self.assertIn("Additional source statuses: none", text)

    def test_text_status_names_no_resolution_questions_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            no_question_status = Path(tmp) / "no_question_status.json"
            no_question_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[no_question_status],
            )

        text = format_project_status_report(report)
        self.assertIn("Resolution questions: none", text)

    def test_json_cli_reports_project_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_project_status_cli(["--format", "json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["schema_version"], PROJECT_STATUS_SCHEMA_VERSION)
        self.assertEqual(payload["transition_evidence"]["bundle_count"], 8)
        self.assertEqual(
            payload["transition_evidence"]["bundles"],
            TRANSITION_BUNDLES,
        )
        self.assertEqual(payload["chain_evidence"]["bundle_count"], 2)
        self.assertEqual(payload["chain_evidence"]["bundles"], CHAIN_BUNDLES)
        self.assertEqual(payload["frontier"]["blocked_commands"], BLOCKED_COMMANDS)
        self.assertEqual(payload["frontier"]["failed_subjects"], [])
        self.assertEqual(
            [item["commands"] for item in payload["frontier"]["source_statuses"]],
            [
                BLOCKED_COMMANDS,
                ["standard-signal"],
                ["write-buf-zero", "write-buf-one"],
            ],
        )
        self.assertEqual(
            [
                item["blocked_runtime_surfaces"]
                for item in payload["frontier"]["source_statuses"]
            ],
            [
                [],
                BLOCKED_RUNTIME_SURFACES,
                BLOCKED_RUNTIME_SURFACES,
            ],
        )
        self.assertEqual(
            [
                item["required_resolution_questions"]
                for item in payload["frontier"]["source_statuses"]
            ],
            [
                [],
                STANDARD_SIGNAL_QUESTIONS,
                WRITE_BUFFER_QUESTIONS,
            ],
        )
        self.assertEqual(
            [
                item["resolution_questions"]
                for item in payload["frontier"]["source_statuses"]
            ],
            [
                [],
                STANDARD_SIGNAL_RESOLUTION_QUESTIONS,
                WRITE_BUFFER_RESOLUTION_QUESTIONS,
            ],
        )
        self.assertEqual(
            [
                item["additional_source_statuses"]
                for item in payload["frontier"]["source_statuses"]
            ],
            [
                [],
                STANDARD_SIGNAL_ADDITIONAL_SOURCE_STATUSES,
                WRITE_BUFFER_ADDITIONAL_SOURCE_STATUSES,
            ],
        )

    def test_missing_source_status_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_status = Path(tmp) / "missing_status.json"

            report = build_project_status_report(
                source_status_paths=[missing_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-file"],
        )
        self.assertEqual(
            report["frontier"]["missing_source_statuses"],
            [str(missing_status)],
        )
        self.assertEqual(report["frontier"]["source_statuses"], [])

    def test_invalid_source_status_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "invalid_status.json"
            invalid_status.write_text("{not-json", encoding="utf-8")

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-json"],
        )
        self.assertEqual(report["frontier"]["missing_source_statuses"], [])
        self.assertEqual(
            [item["path"] for item in report["frontier"]["invalid_source_statuses"]],
            [str(invalid_status)],
        )

    def test_schema_invalid_source_status_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "schema_invalid_status.json"
            invalid_status.write_text("{}", encoding="utf-8")

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertEqual(report["frontier"]["missing_source_statuses"], [])
        self.assertEqual(
            [item["path"] for item in report["frontier"]["invalid_source_statuses"]],
            [str(invalid_status)],
        )

    def test_non_object_source_status_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "list_status.json"
            invalid_status.write_text("[]", encoding="utf-8")

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertEqual(
            [item["path"] for item in report["frontier"]["invalid_source_statuses"]],
            [str(invalid_status)],
        )

    def test_commandless_source_status_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "commandless_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertEqual(report["frontier"]["missing_source_statuses"], [])
        self.assertEqual(
            [item["path"] for item in report["frontier"]["invalid_source_statuses"]],
            [str(invalid_status)],
        )
        self.assertIn(
            "command",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_source_status_command_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_command_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "commands": ["standard-signal", "  "],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertEqual(report["frontier"]["missing_source_statuses"], [])
        self.assertEqual(
            [item["path"] for item in report["frontier"]["invalid_source_statuses"]],
            [str(invalid_status)],
        )
        self.assertIn(
            "non-empty",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_source_status_decision_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_decision_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "   ",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertEqual(
            [item["path"] for item in report["frontier"]["invalid_source_statuses"]],
            [str(invalid_status)],
        )
        self.assertIn(
            "decision",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_source_status_safe_next_slice_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_safe_next_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "\t ",
                    "command": "standard-signal",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertEqual(
            [item["path"] for item in report["frontier"]["invalid_source_statuses"]],
            [str(invalid_status)],
        )
        self.assertIn(
            "safe_next_slice",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_missing_source_status_as_boundary_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "missing_as_boundary_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertEqual(
            [item["path"] for item in report["frontier"]["invalid_source_statuses"]],
            [str(invalid_status)],
        )
        self.assertIn(
            "as_boundary",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_source_status_as_boundary_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_as_boundary_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "  ",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertEqual(
            [item["path"] for item in report["frontier"]["invalid_source_statuses"]],
            [str(invalid_status)],
        )
        self.assertIn(
            "as_boundary",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_non_text_source_status_command_entry_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "non_text_command_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "commands": ["standard-signal", 0],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertEqual(
            [item["path"] for item in report["frontier"]["invalid_source_statuses"]],
            [str(invalid_status)],
        )
        self.assertIn(
            "text",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_non_text_source_status_command_field_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "non_text_command_field_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": ["standard-signal"],
                    "commands": ["write-buf-zero"],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "command",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_scalar_source_status_commands_field_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "scalar_commands_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "commands": "write-buf-zero",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "commands",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_scalar_blocked_runtime_commands_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "scalar_blocked_runtime_commands.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "blocked_runtime_commands": "write-buf-one",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "blocked_runtime_commands",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_scalar_blocked_runtime_surfaces_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "scalar_blocked_runtime_surfaces.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "blocked_runtime_surfaces": "recipient-command-message",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "blocked_runtime_surfaces",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_non_text_blocked_runtime_surface_entry_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "non_text_blocked_runtime_surface.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "blocked_runtime_surfaces": ["recipient-command-message", 0],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "runtime surface",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_blocked_runtime_surface_entry_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_blocked_runtime_surface.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "blocked_runtime_surfaces": ["recipient-command-message", " "],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "non-empty",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_scalar_resolution_questions_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "scalar_resolution_questions.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "required_resolution_questions": "recipient-surface",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "required_resolution_questions",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_non_object_resolution_question_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "non_object_resolution_question.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "required_resolution_questions": ["recipient-surface"],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "resolution question",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_resolution_question_id_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_resolution_question_id.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "required_resolution_questions": [{"question_id": "  "}],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "question_id",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_scalar_additional_source_statuses_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "scalar_additional_source_statuses.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "additional_source_statuses": "sources/other_status.json",
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "additional_source_statuses",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_non_object_additional_source_status_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "non_object_additional_source_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "additional_source_statuses": ["sources/other_status.json"],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "additional source-status entries",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_additional_source_status_path_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_additional_source_status_path.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "additional_source_statuses": [
                        {
                            "adr": "ADR-0000",
                            "path": " ",
                            "summary": "Other source status remains relevant.",
                        }
                    ],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "path",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_missing_additional_source_status_path_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "missing_additional_source_status_path.json"
            missing_source_status = Path(tmp) / "missing_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "additional_source_statuses": [
                        {
                            "adr": "ADR-0000",
                            "path": str(missing_source_status),
                            "summary": "Other source status remains relevant.",
                        }
                    ],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "path",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )
        self.assertIn(
            "exist",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_invalid_json_additional_source_status_path_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "invalid_json_additional_source_status_path.json"
            linked_source_status = Path(tmp) / "linked_status.json"
            linked_source_status.write_text("{not-json", encoding="utf-8")
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "additional_source_statuses": [
                        {
                            "adr": "ADR-0000",
                            "path": str(linked_source_status),
                            "summary": "Other source status remains relevant.",
                        }
                    ],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "JSON",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )
        self.assertIn(
            str(linked_source_status),
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_non_object_additional_source_status_path_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "non_object_additional_source_status_path.json"
            linked_source_status = Path(tmp) / "linked_status.json"
            linked_source_status.write_text("[]", encoding="utf-8")
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "additional_source_statuses": [
                        {
                            "adr": "ADR-0000",
                            "path": str(linked_source_status),
                            "summary": "Other source status remains relevant.",
                        }
                    ],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                source_status_paths=[invalid_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-schema"],
        )
        self.assertIn(
            "object",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )
        self.assertIn(
            str(linked_source_status),
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_frontier_failed_subjects_preserve_mixed_failure_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_status = Path(tmp) / "missing_status.json"
            invalid_status = Path(tmp) / "invalid_status.json"
            invalid_status.write_text("{not-json", encoding="utf-8")

            report = build_project_status_report(
                source_status_paths=[invalid_status, missing_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(
            report["frontier"]["failed_subjects"],
            ["source-status-file", "source-status-json"],
        )

    def test_missing_transition_registry_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_registry = Path(tmp) / "missing_transition_manifest.json"

            report = build_project_status_report(
                transition_registry_path=missing_registry,
            )

        self.assertFalse(report["accepted"])
        self.assertFalse(report["transition_evidence"]["accepted"])
        self.assertEqual(report["transition_evidence"]["registry_id"], "")
        self.assertEqual(report["transition_evidence"]["path"], str(missing_registry))
        self.assertEqual(report["transition_evidence"]["bundle_count"], 0)
        self.assertEqual(report["transition_evidence"]["bundles"], [])
        self.assertEqual(
            report["transition_evidence"]["failed_subjects"],
            ["registry-file"],
        )
        self.assertIn(
            str(missing_registry),
            report["transition_evidence"]["results"][0]["detail"],
        )
        self.assertTrue(report["chain_evidence"]["accepted"])

    def test_missing_chain_registry_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_registry = Path(tmp) / "missing_chain_manifest.json"

            report = build_project_status_report(
                chain_registry_path=missing_registry,
            )

        self.assertFalse(report["accepted"])
        self.assertTrue(report["transition_evidence"]["accepted"])
        self.assertFalse(report["chain_evidence"]["accepted"])
        self.assertEqual(report["chain_evidence"]["registry_id"], "")
        self.assertEqual(report["chain_evidence"]["path"], str(missing_registry))
        self.assertEqual(report["chain_evidence"]["bundle_count"], 0)
        self.assertEqual(report["chain_evidence"]["bundles"], [])
        self.assertEqual(
            report["chain_evidence"]["failed_subjects"],
            ["registry-file"],
        )

    def test_json_cli_reports_missing_registry_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_registry = Path(tmp) / "missing_transition_manifest.json"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = run_project_status_cli(
                    [
                        "--transition-registry",
                        str(missing_registry),
                        "--format",
                        "json",
                    ]
                )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1, payload)
        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["transition_evidence"]["failed_subjects"],
            ["registry-file"],
        )
        self.assertEqual(
            payload["transition_evidence"]["path"],
            str(missing_registry),
        )
        self.assertEqual(payload["transition_evidence"]["bundles"], [])

    def test_invalid_transition_registry_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_registry = Path(tmp) / "invalid_transition_manifest.json"
            invalid_registry.write_text("{not-json", encoding="utf-8")

            report = build_project_status_report(
                transition_registry_path=invalid_registry,
            )

        self.assertFalse(report["accepted"])
        self.assertFalse(report["transition_evidence"]["accepted"])
        self.assertEqual(report["transition_evidence"]["path"], str(invalid_registry))
        self.assertEqual(report["transition_evidence"]["bundle_count"], 0)
        self.assertEqual(report["transition_evidence"]["bundles"], [])
        self.assertEqual(
            report["transition_evidence"]["failed_subjects"],
            ["registry-json"],
        )

    def test_invalid_chain_registry_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_registry = Path(tmp) / "invalid_chain_manifest.json"
            invalid_registry.write_text("{}", encoding="utf-8")

            report = build_project_status_report(
                chain_registry_path=invalid_registry,
            )

        self.assertFalse(report["accepted"])
        self.assertTrue(report["transition_evidence"]["accepted"])
        self.assertFalse(report["chain_evidence"]["accepted"])
        self.assertEqual(report["chain_evidence"]["path"], str(invalid_registry))
        self.assertEqual(report["chain_evidence"]["bundle_count"], 0)
        self.assertEqual(report["chain_evidence"]["bundles"], [])
        self.assertEqual(
            report["chain_evidence"]["failed_subjects"],
            ["registry-json"],
        )

    def test_text_status_names_missing_registry_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_registry = Path(tmp) / "missing_chain_manifest.json"

            report = build_project_status_report(
                chain_registry_path=missing_registry,
            )

        text = format_project_status_report(report)
        self.assertIn("Autarkic Systems project status: rejected", text)
        self.assertIn("Chain evidence: rejected (0 bundles)", text)
        self.assertIn("Chain evidence bundles: none", text)
        self.assertIn(f"Missing registry files: {missing_registry}", text)

    def test_text_status_names_invalid_registry_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_registry = Path(tmp) / "invalid_chain_manifest.json"
            invalid_registry.write_text("{}", encoding="utf-8")

            report = build_project_status_report(
                chain_registry_path=invalid_registry,
            )

        text = format_project_status_report(report)
        self.assertIn("Autarkic Systems project status: rejected", text)
        self.assertIn("Chain evidence: rejected (0 bundles)", text)
        self.assertIn("Chain evidence bundles: none", text)
        self.assertIn(f"Invalid registry files: {invalid_registry}", text)

    def test_module_execution_runs_text_status_report(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.project_status"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Autarkic Systems project status: accepted", completed.stdout)
        self.assertIn("Transition evidence: accepted (8 bundles)", completed.stdout)
        self.assertIn("Chain evidence: accepted (2 bundles)", completed.stdout)


if __name__ == "__main__":
    unittest.main()
