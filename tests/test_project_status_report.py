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
BLOCKED_COMMANDS = ["standard-signal"]
STANDARD_SIGNAL_SAFE_NEXT_SLICE = (
    "no-standard-signal-command-token-execution-change-without-new-source-evidence"
)
RECIPIENT_WRITE_BUFFER_SAFE_NEXT_SLICE = (
    "no-write-buffer-follow-up-pending-after-recipient-evidence-bundle"
)
SAFE_NEXT_SLICE = ""
PROJECT_STATUS_SCHEMA_VERSION = 15
STANDARD_SIGNAL_BLOCKED_RUNTIME_SURFACES = [
    "self-mailbox-command",
    "self-target-command-buffer",
]
WRITE_BUFFER_BLOCKED_RUNTIME_SURFACES = []
RECIPIENT_NON_INIT_AS_BOUNDARY = (
    "Continue rejecting recipient non-init command-message inputs for "
    "standard-signal command tokens and multi-command conflicts; standard-signal "
    "recipient input is a resolved rejection boundary and standard-signal "
    "self-target command execution is preserved unsupported unless new source "
    "evidence replaces that boundary. ADR-0171 reviewed current source heads "
    "and found no new standard-signal execution evidence, while direct "
    "self-mailbox and completed self-target write-buffer execution are "
    "implemented by ADR-0161 and recipient write-buffer command-message "
    "execution is implemented by ADR-0169. The accepted current runtime "
    "behavior rejects only standard-signal command messages and multi-command "
    "conflicts."
)
STANDARD_SIGNAL_AS_BOUNDARY = (
    "Continue rejecting or preserving standard-signal command tokens at the "
    "existing claimed boundaries. AS already has ordinary standard-signal "
    "routing and stem buffer accumulation for binary input; ADR-0171 found no "
    "new source evidence replacing the unsupported command-token boundary."
)
WRITE_BUFFER_AS_BOUNDARY = (
    "Direct self-mailbox and completed self-target command-buffer "
    "write-buffer execution are implemented through ADR-0161 append behavior "
    "and bundled as integrated evidence by ADR-0162. Delivered recipient "
    "write-buffer command-message inputs are implemented by ADR-0169 append "
    "behavior; no write-buffer runtime surface remains blocked."
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
        "covered_positive_examples": [
            "fixed upstream standard-signal command rejected",
        ],
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
        "positive_example": "standard signal unsupported preserved",
        "covered_positive_examples": [
            "standard signal unsupported preserved",
        ],
    },
    {
        "bundle_id": "self-mailbox-write-buffer-evidence-bundle",
        "path": "evidence/self_mailbox_write_buffer_bundle.json",
        "claim_id": "UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED",
        "expected_status": "self-mailbox-write-buffer-appended",
        "positive_example": "self mailbox write buffer one appended",
        "covered_positive_examples": [
            "self mailbox write buffer zero appended",
            "self mailbox write buffer one appended",
        ],
    },
    {
        "bundle_id": "recipient-write-buffer-command-message-evidence-bundle",
        "path": "evidence/recipient_write_buffer_command_message_bundle.json",
        "claim_id": "UC-RECIPIENT-WRITE-BUFFER-COMMAND-MESSAGE-APPENDED",
        "expected_status": "recipient-write-buffer-command-message-appended",
        "positive_example": "fixed upstream write-buf-zero command appended",
        "covered_positive_examples": [
            "fixed upstream write-buf-zero command appended",
            "stem recipient write-buf-one command appended",
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
        "positive_example": "self standard signal command remains appended",
        "covered_positive_examples": [
            "self standard signal command remains appended",
        ],
    },
    {
        "bundle_id": "self-command-buffer-write-buffer-evidence-bundle",
        "path": "evidence/self_command_buffer_write_buffer_bundle.json",
        "claim_id": "UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED",
        "expected_status": "stem-command-buffer-self-write-buffer-appended",
        "positive_example": "self command buffer write buffer one appended",
        "covered_positive_examples": [
            "self command buffer write buffer zero appended",
            "self command buffer write buffer one appended",
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
TRANSITION_LANGUAGE = {
    "language_id": "as-transition-claim-v1",
    "language_path": "language/transition_claim_language.json",
    "claims_path": "claims/transition_claims.json",
    "certificates_path": "claims/proof_certificates.json",
    "claim_count": 16,
    "certificate_count": 16,
    "result_count": 72,
}
CHAIN_LANGUAGE = {
    "language_id": "as-transition-chain-claim-v1",
    "language_path": "language/transition_chain_claim_language.json",
    "claims_path": "claims/transition_chain_claims.json",
    "certificates_path": "claims/transition_chain_proof_certificates.json",
    "claim_count": 2,
    "certificate_count": 2,
    "result_count": 32,
}
TRANSITION_CLAIMS = {
    "claims_path": "claims/transition_claims.json",
    "claim_count": 16,
    "example_count": 40,
    "matched_count": 40,
    "result_count": 40,
}
TRANSITION_PROOF_CERTIFICATES = {
    "claims_path": "claims/transition_claims.json",
    "certificates_path": "claims/proof_certificates.json",
    "claim_count": 16,
    "certificate_count": 16,
    "result_count": 16,
}
CHAIN_CLAIMS = {
    "language_id": "as-transition-chain-claim-v1",
    "language_path": "language/transition_chain_claim_language.json",
    "claims_path": "claims/transition_chain_claims.json",
    "certificates_path": "claims/transition_chain_proof_certificates.json",
    "claim_count": 2,
    "certificate_count": 2,
    "result_count": 4,
}
STANDARD_SIGNAL_QUESTIONS = []
STANDARD_SIGNAL_RESOLUTION_QUESTIONS = []
STANDARD_SIGNAL_RESOLUTION_QUESTION_EVIDENCE = []
STANDARD_SIGNAL_RESOLVED_QUESTIONS = [
    {
        "question_id": "command-table-offset",
        "decision": "preserve-formal-command-offset-0",
        "source_status": "sources/stem_command_buffer_map.json",
        "formal_command_offset": 0,
        "legacy_divergence": (
            "RAA maps its final command-buffer case to standard-signal, but AS "
            "preserves the formal PRC command-buffer map from ADR-0026."
        ),
    },
    {
        "question_id": "self-mailbox-standard-signal-binary-input-equivalence",
        "decision": "do-not-treat-self-mailbox-standard-signal-as-binary-input",
        "source_status": "sources/standard_signal_command_semantics_status.json",
        "legacy_divergence": (
            "The formal model excludes standard signals sent to the "
            "self-mailbox of a stem cell from productive ordinary "
            "standard-signal behavior; legacy witnesses exclude "
            "standard-signal from special messages and do not provide a "
            "matching command-token execution rule."
        ),
    },
    {
        "question_id": "recipient-surface",
        "decision": "reject-recipient-standard-signal-command-message-as-non-init",
        "source_status": "sources/recipient_non_init_command_source_status.json",
        "legacy_divergence": (
            "The formal model provides no recipient execution rule for "
            "delivered standard-signal command messages; RAA, SEMSIM, and "
            "FSMSIM exclude standard-signal from special-message sets, and "
            "AS already claims UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED."
        ),
    },
    {
        "question_id": "command-token-vs-binary-input",
        "decision": "do-not-replay-ordinary-binary-input-standard-signal",
        "source_status": "sources/standard_signal_command_semantics_status.json",
        "legacy_divergence": (
            "The formal model separately names ordinary standard-signal "
            "processing and the command-table standard-signal entry; RAA, "
            "SEMSIM, and FSMSIM exclude standard-signal from special-message "
            "dispatch and treat ordinary standard input separately."
        ),
    },
    {
        "question_id": "self-target-surface",
        "decision": "preserve-self-target-standard-signal-as-unsupported",
        "source_status": "sources/standard_signal_command_semantics_status.json",
        "legacy_divergence": (
            "AS already preserves direct self-mailbox standard-signal under "
            "UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED and preserves "
            "completed self-target command-buffer standard-signal under "
            "UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED."
        ),
    },
]
WRITE_BUFFER_RESOLVED_QUESTIONS = [
    {
        "question_id": "standard-signal-interaction",
        "decision": "write-buffer-command-bits-are-literal-not-high-rail-derived",
        "source_status": "sources/write_buffer_command_semantics_status.json",
        "legacy_divergence": (
            "The formal model, RAA, SEMSIM, and FSMSIM agree that "
            "write-buf-zero and write-buf-one carry literal 0 and 1 "
            "append bits; ADR-0161 implements the source-resolved "
            "self-target append surfaces."
        ),
    },
    {
        "question_id": "recipient-surface",
        "decision": "execute-recipient-write-buffer-command-message-append",
        "source_status": "sources/write_buffer_command_semantics_status.json",
        "legacy_divergence": (
            "The formal model routes input-channel special messages through "
            "process-special-message; RAA and FSMSIM route write-buf-zero and "
            "write-buf-one to literal append behavior while clearing "
            "command-source input. SEMSIM clears the buffer after append, but "
            "AS preserves appended-buffer behavior consistently with ADR-0160. "
            "ADR-0169 implements this recipient command-message append surface "
            "as checked runtime behavior."
        ),
    },
    {
        "question_id": "recipient-command-message-surface",
        "decision": "execute-recipient-write-buffer-command-message-append",
        "source_status": "sources/write_buffer_command_semantics_status.json",
        "legacy_divergence": (
            "The formal model routes input-channel special messages through "
            "process-special-message; RAA and FSMSIM route write-buf-zero and "
            "write-buf-one to literal append behavior while clearing "
            "command-source input. SEMSIM clears the buffer after append, but "
            "AS preserves appended-buffer behavior consistently with ADR-0160. "
            "ADR-0169 implements this recipient command-message append surface "
            "as checked runtime behavior."
        ),
    },
    {
        "question_id": "self-target-surface",
        "decision": "execute-self-target-write-buffer-append",
        "source_status": "sources/write_buffer_command_semantics_status.json",
        "legacy_divergence": (
            "AS now executes direct self-mailbox write-buffer command tokens "
            "under UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED and completed "
            "self-target command-buffer write-buffer commands under "
            "UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED; "
            "standard-signal remains the preserved unsupported self-target "
            "command."
        ),
    },
    {
        "question_id": "buffer-full-boundary",
        "decision": "preserve-existing-full-buffer-boundary-before-write-buffer-append",
        "source_status": "sources/write_buffer_command_semantics_status.json",
        "legacy_divergence": (
            "The formal model gates writes to the stem buffer on less-than-full "
            "state and RAA write-buf appends only when buffer-full? is false; "
            "SEMSIM and FSMSIM omit a matching named command-token full-buffer "
            "rule but provide no contrary full-buffer policy."
        ),
    },
    {
        "question_id": "post-append-clearing",
        "decision": "preserve-appended-buffer-clear-command-source",
        "source_status": "sources/write_buffer_command_semantics_status.json",
        "legacy_divergence": (
            "RAA and FSMSIM preserve the appended literal bit while clearing "
            "the active command source; SEMSIM clears the buffer through its "
            "stem special-message wrapper, so AS records SEMSIM as divergent "
            "legacy behavior."
        ),
    },
]
WRITE_BUFFER_QUESTIONS = []
WRITE_BUFFER_RESOLUTION_QUESTIONS = []
WRITE_BUFFER_RESOLUTION_QUESTION_EVIDENCE = []
STANDARD_SIGNAL_EXECUTION_READINESS = {
    "decision": "preserved-unsupported",
    "execution_change_allowed": False,
    "blocked_by_resolution_questions": [],
    "summary": (
        "Standard-signal command-token execution remains preserved as "
        "unsupported at the self-target boundaries; execution changes require "
        "new source evidence that replaces the existing boundary."
    ),
}
WRITE_BUFFER_EXECUTION_READINESS = {
    "decision": "implemented",
    "execution_change_allowed": False,
    "blocked_by_resolution_questions": [],
    "summary": (
        "Write-buffer append execution is implemented for direct self-mailbox, "
        "completed self-target command-buffer, and single recipient "
        "command-message surfaces."
    ),
}
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
    {
        "adr": "ADR-0171",
        "path": "sources/standard_signal_source_review_status.json",
        "summary": (
            "The 2026-05-18 source-review snapshot found no new "
            "standard-signal command-token execution evidence and keeps "
            "execution changes disallowed without new source evidence."
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
        self.assertEqual(report["transition_evidence"]["bundle_count"], 11)
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
        self.assertTrue(report["transition_claims"]["accepted"])
        for key, expected in TRANSITION_CLAIMS.items():
            self.assertEqual(report["transition_claims"][key], expected)
        self.assertEqual(report["transition_claims"]["failed_subjects"], [])
        self.assertEqual(
            report["transition_claims"]["results"][0],
            {
                "claim_id": "UC-FIXED-OUTPUT-PRESERVED",
                "example_name": "blocked output preserved",
                "expected": True,
                "observed": True,
                "matched": True,
                "detail": "occupied output was preserved",
            },
        )
        self.assertTrue(report["transition_proof_certificates"]["accepted"])
        for key, expected in TRANSITION_PROOF_CERTIFICATES.items():
            self.assertEqual(report["transition_proof_certificates"][key], expected)
        self.assertEqual(
            report["transition_proof_certificates"]["failed_subjects"],
            [],
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][0],
            {
                "claim_id": "UC-FIXED-OUTPUT-PRESERVED",
                "accepted": True,
                "detail": "verified 2 certificate steps: 2 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][1],
            {
                "claim_id": "UC-FIXED-CONSUMED-INPUT-CLEARED",
                "accepted": True,
                "detail": "verified 2 certificate steps: 2 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][2],
            {
                "claim_id": "UC-FIXED-MEMORY-RULE",
                "accepted": True,
                "detail": "verified 2 certificate steps: 2 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][3],
            {
                "claim_id": "UC-FIXED-STEM-INIT-RESET",
                "accepted": True,
                "detail": "verified 2 certificate steps: 2 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][4],
            {
                "claim_id": "UC-STEM-AUTOMAIL-RECONFIGURES",
                "accepted": True,
                "detail": "verified 2 certificate steps: 2 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][5],
            {
                "claim_id": "UC-STEM-BUFFER-ACCUMULATES",
                "accepted": True,
                "detail": "verified 4 certificate steps: 4 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][6],
            {
                "claim_id": "UC-STEM-SELF-MAILBOX-INIT-COMMAND",
                "accepted": True,
                "detail": "verified 2 certificate steps: 2 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][7],
            {
                "claim_id": "UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED",
                "accepted": True,
                "detail": "verified 2 certificate steps: 2 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][8],
            {
                "claim_id": "UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED",
                "accepted": True,
                "detail": "verified 3 certificate steps: 3 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][9],
            {
                "claim_id": "UC-STEM-COMMAND-BUFFER-SELF-INIT",
                "accepted": True,
                "detail": "verified 2 certificate steps: 2 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][10],
            {
                "claim_id": "UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED",
                "accepted": True,
                "detail": "verified 2 certificate steps: 2 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][11],
            {
                "claim_id": (
                    "UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED"
                ),
                "accepted": True,
                "detail": "verified 3 certificate steps: 3 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][12],
            {
                "claim_id": "UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED",
                "accepted": True,
                "detail": "verified 2 certificate steps: 2 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][13],
            {
                "claim_id": "UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED",
                "accepted": True,
                "detail": "verified 3 certificate steps: 3 predicate-result steps",
            },
        )
        self.assertEqual(
            report["transition_proof_certificates"]["results"][14],
            {
                "claim_id": (
                    "UC-RECIPIENT-WRITE-BUFFER-COMMAND-MESSAGE-APPENDED"
                ),
                "accepted": True,
                "detail": "verified 3 certificate steps: 3 predicate-result steps",
            },
        )
        self.assertTrue(report["chain_claims"]["accepted"])
        for key, expected in CHAIN_CLAIMS.items():
            self.assertEqual(report["chain_claims"][key], expected)
        self.assertEqual(report["chain_claims"]["failed_subjects"], [])
        self.assertEqual(
            report["chain_claims"]["results"],
            [
                {
                    "subject": "chain-language-manifest",
                    "accepted": True,
                    "detail": "validated 28 language clauses",
                },
                {
                    "subject": "chain-examples",
                    "accepted": True,
                    "detail": "evaluated 9 examples",
                },
                {
                    "subject": "chain-certificates",
                    "accepted": True,
                    "detail": "verified 2 certificates",
                },
                {
                    "subject": "chain-surface",
                    "accepted": True,
                    "detail": "validated 2 chain claims",
                },
            ],
        )
        self.assertTrue(report["transition_language"]["accepted"])
        for key, expected in TRANSITION_LANGUAGE.items():
            self.assertEqual(report["transition_language"][key], expected)
        self.assertEqual(report["transition_language"]["failed_subjects"], [])
        self.assertTrue(report["chain_language"]["accepted"])
        for key, expected in CHAIN_LANGUAGE.items():
            self.assertEqual(report["chain_language"][key], expected)
        self.assertEqual(report["chain_language"]["failed_subjects"], [])
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
                STANDARD_SIGNAL_BLOCKED_RUNTIME_SURFACES,
                WRITE_BUFFER_BLOCKED_RUNTIME_SURFACES,
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
                item["resolved_resolution_questions"]
                for item in report["frontier"]["source_statuses"]
            ],
            [
                [],
                STANDARD_SIGNAL_RESOLVED_QUESTIONS,
                WRITE_BUFFER_RESOLVED_QUESTIONS,
            ],
        )
        self.assertEqual(
            [
                item["resolution_question_evidence"]
                for item in report["frontier"]["source_statuses"]
            ],
            [
                [],
                STANDARD_SIGNAL_RESOLUTION_QUESTION_EVIDENCE,
                WRITE_BUFFER_RESOLUTION_QUESTION_EVIDENCE,
            ],
        )
        self.assertEqual(
            [
                item["execution_readiness"]
                for item in report["frontier"]["source_statuses"]
            ],
            [
                {},
                STANDARD_SIGNAL_EXECUTION_READINESS,
                WRITE_BUFFER_EXECUTION_READINESS,
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
        self.assertIn("Transition evidence: accepted (11 bundles)", text)
        self.assertIn("Chain evidence: accepted (2 bundles)", text)
        self.assertIn(
            "Transition claims: accepted (16 claims, 40 examples, 40 matched)",
            text,
        )
        self.assertIn(
            "Transition proof certificates: accepted (16 claims, 16 certificates)",
            text,
        )
        self.assertIn("Claim/proof failures: none", text)
        self.assertIn(
            "Transition chain claims: accepted (2 claims, 2 certificates)",
            text,
        )
        self.assertIn("Chain claim failures: none", text)
        self.assertIn("Transition language: accepted (16 claims, 16 certificates)", text)
        self.assertIn("Chain language: accepted (2 claims, 2 certificates)", text)
        self.assertIn("Language failures: none", text)
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
            "positive example: standard signal unsupported preserved",
            text,
        )
        self.assertIn(
            "covered examples: standard signal unsupported preserved",
            text,
        )
        self.assertIn(
            "positive example: self standard signal command remains appended",
            text,
        )
        self.assertIn(
            "covered examples: self standard signal command remains appended",
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
            "Blocked commands: standard-signal",
            text,
        )
        self.assertIn("Blocked runtime surfaces:", text)
        self.assertIn(
            "standard-signal: self-mailbox-command, self-target-command-buffer",
            text,
        )
        self.assertNotIn(
            "write-buf-zero, write-buf-one: recipient-command-message",
            text,
        )
        self.assertIn("AS boundaries:", text)
        self.assertIn(
            f"standard-signal: {RECIPIENT_NON_INIT_AS_BOUNDARY}",
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
        self.assertIn("Safe next slice: none", text)
        self.assertNotIn("add-write-buffer-command-execution-evidence-bundle", text)
        self.assertIn("Missing source-status files: none", text)

    def test_text_status_names_transition_language_failed_subjects(self):
        with tempfile.TemporaryDirectory() as tmp:
            language_path = Path(tmp) / "transition_claim_language.json"
            data = json.loads(
                Path("language/transition_claim_language.json").read_text(
                    encoding="utf-8"
                )
            )
            del data["syntax_classes"]["formulae"]
            language_path.write_text(json.dumps(data), encoding="utf-8")

            report = build_project_status_report(
                transition_language_path=language_path,
            )

        text = format_project_status_report(report)
        self.assertFalse(report["accepted"])
        self.assertIn("Transition language: rejected", text)
        self.assertIn("Language failures:", text)
        self.assertIn("Transition language failures: formulae", text)

    def test_text_status_names_chain_language_failed_subjects(self):
        with tempfile.TemporaryDirectory() as tmp:
            language_path = Path(tmp) / "transition_chain_claim_language.json"
            data = json.loads(
                Path("language/transition_chain_claim_language.json").read_text(
                    encoding="utf-8"
                )
            )
            del data["syntax_classes"]["chain_formulae"]
            language_path.write_text(json.dumps(data), encoding="utf-8")

            report = build_project_status_report(
                chain_language_path=language_path,
            )

        text = format_project_status_report(report)
        self.assertFalse(report["accepted"])
        self.assertIn("Chain language: rejected", text)
        self.assertIn("Language failures:", text)
        self.assertIn("Chain language failures: chain_formulae", text)

    def test_text_status_names_transition_claim_failed_subjects(self):
        with tempfile.TemporaryDirectory() as tmp:
            claims_path = Path(tmp) / "transition_claims.json"
            data = json.loads(
                Path("claims/transition_claims.json").read_text(encoding="utf-8")
            )
            data["claims"][0]["examples"][0]["expected"] = False
            claims_path.write_text(json.dumps(data), encoding="utf-8")

            report = build_project_status_report(
                transition_claims_path=claims_path,
            )

        text = format_project_status_report(report)
        self.assertFalse(report["accepted"])
        self.assertFalse(report["transition_claims"]["accepted"])
        self.assertIn(
            "UC-FIXED-OUTPUT-PRESERVED/blocked output preserved",
            report["transition_claims"]["failed_subjects"],
        )
        self.assertIn("Transition claims: rejected", text)
        self.assertIn("Claim/proof failures:", text)
        self.assertIn(
            "Transition claim failures: "
            "UC-FIXED-OUTPUT-PRESERVED/blocked output preserved",
            text,
        )

    def test_text_status_names_transition_proof_failed_subjects(self):
        with tempfile.TemporaryDirectory() as tmp:
            certificates_path = Path(tmp) / "proof_certificates.json"
            data = json.loads(
                Path("claims/proof_certificates.json").read_text(encoding="utf-8")
            )
            data["certificates"][0]["steps"][0]["expected"] = False
            certificates_path.write_text(json.dumps(data), encoding="utf-8")

            report = build_project_status_report(
                transition_certificates_path=certificates_path,
            )

        text = format_project_status_report(report)
        self.assertFalse(report["accepted"])
        self.assertFalse(report["transition_proof_certificates"]["accepted"])
        self.assertIn(
            "UC-FIXED-OUTPUT-PRESERVED",
            report["transition_proof_certificates"]["failed_subjects"],
        )
        self.assertIn("Transition proof certificates: rejected", text)
        self.assertIn("Claim/proof failures:", text)
        self.assertIn(
            "Transition proof certificate failures: UC-FIXED-OUTPUT-PRESERVED",
            text,
        )

    def test_text_status_names_chain_claim_failed_subjects(self):
        with tempfile.TemporaryDirectory() as tmp:
            certificates_path = Path(tmp) / "transition_chain_proof_certificates.json"
            certificates_path.write_text(
                json.dumps({
                    "schema_version": 1,
                    "certificates": [
                        {
                            "claim_id": (
                                "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED"
                            ),
                            "steps": [
                                {
                                    "rule": "manifest-example",
                                    "example": (
                                        "neighbor b proc left delivery consumed "
                                        "by empty recipient"
                                    ),
                                    "expected": True,
                                }
                            ],
                        }
                    ],
                }),
                encoding="utf-8",
            )

            report = build_project_status_report(
                chain_certificates_path=certificates_path,
            )

        text = format_project_status_report(report)
        self.assertFalse(report["accepted"])
        self.assertFalse(report["chain_claims"]["accepted"])
        self.assertIn("chain-certificates", report["chain_claims"]["failed_subjects"])
        self.assertIn("Transition chain claims: rejected", text)
        self.assertIn("Chain claim failures:", text)
        self.assertIn("chain-certificates", text)

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
        self.assertNotIn(
            "command-token-vs-binary-input: Decide whether a standard-signal",
            text,
        )
        self.assertNotIn(
            "self-target-surface: Decide whether self-mailbox and self-target",
            text,
        )
        self.assertIn("Resolution questions: none", text)
        self.assertNotIn(
            "recipient-command-message-surface: Decide whether delivered "
            "recipient write-buffer command messages",
            text,
        )
        self.assertNotIn("buffer-full-boundary: Decide whether", text)
        self.assertNotIn("post-append-clearing: Decide whether", text)
        self.assertNotIn("recipient-vs-stem-surface", text)

    def test_text_status_names_resolution_question_evidence(self):
        report = build_project_status_report()

        text = format_project_status_report(report)

        self.assertIn("Resolution question evidence:", text)
        self.assertIn("Resolution question evidence: none", text)
        self.assertNotIn(
            "recipient-command-message-surface: The formal model and legacy "
            "RAA/FSMSIM witnesses route input-channel write-buffer",
            text,
        )
        self.assertNotIn(
            "command-token-vs-binary-input: The formal model names",
            text,
        )
        self.assertNotIn(
            "self-target-surface: The formal model excludes standard signals",
            text,
        )
        self.assertNotIn("buffer-full-boundary: RAA guards", text)
        self.assertNotIn("post-append-clearing: RAA preserves", text)
        self.assertNotIn("recipient-vs-stem-surface", text)

    def test_text_status_names_resolved_resolution_questions(self):
        report = build_project_status_report()

        text = format_project_status_report(report)

        self.assertIn("Resolved resolution questions:", text)
        self.assertIn("standard-signal:", text)
        self.assertIn(
            "command-table-offset: preserve-formal-command-offset-0 "
            "(sources/stem_command_buffer_map.json)",
            text,
        )
        self.assertIn("formal command offset: 0", text)
        self.assertIn(
            "legacy divergence: RAA maps its final command-buffer case to "
            "standard-signal, but AS preserves the formal PRC command-buffer "
            "map from ADR-0026.",
            text,
        )
        self.assertIn(
            "self-mailbox-standard-signal-binary-input-equivalence: "
            "do-not-treat-self-mailbox-standard-signal-as-binary-input "
            "(sources/standard_signal_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "recipient-surface: "
            "reject-recipient-standard-signal-command-message-as-non-init "
            "(sources/recipient_non_init_command_source_status.json)",
            text,
        )
        self.assertIn(
            "command-token-vs-binary-input: "
            "do-not-replay-ordinary-binary-input-standard-signal "
            "(sources/standard_signal_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "self-target-surface: "
            "preserve-self-target-standard-signal-as-unsupported "
            "(sources/standard_signal_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "legacy divergence: The formal model excludes standard signals "
            "sent to the self-mailbox of a stem cell from productive "
            "ordinary standard-signal behavior; legacy witnesses exclude "
            "standard-signal from special messages and do not provide a "
            "matching command-token execution rule.",
            text,
        )
        self.assertIn(
            "legacy divergence: The formal model provides no recipient "
            "execution rule for delivered standard-signal command messages; "
            "RAA, SEMSIM, and FSMSIM exclude standard-signal from "
            "special-message sets, and AS already claims "
            "UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED.",
            text,
        )
        self.assertIn(
            "legacy divergence: The formal model separately names ordinary "
            "standard-signal processing and the command-table standard-signal "
            "entry; RAA, SEMSIM, and FSMSIM exclude standard-signal from "
            "special-message dispatch and treat ordinary standard input "
            "separately.",
            text,
        )
        self.assertIn(
            "legacy divergence: AS already preserves direct self-mailbox "
            "standard-signal under UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED "
            "and preserves completed self-target command-buffer "
            "standard-signal under "
            "UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED.",
            text,
        )
        self.assertIn("write-buf-zero, write-buf-one:", text)
        self.assertIn(
            "standard-signal-interaction: "
            "write-buffer-command-bits-are-literal-not-high-rail-derived "
            "(sources/write_buffer_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "recipient-surface: "
            "execute-recipient-write-buffer-command-message-append "
            "(sources/write_buffer_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "legacy divergence: The formal model, RAA, SEMSIM, and FSMSIM "
            "agree that write-buf-zero and write-buf-one carry literal 0 "
            "and 1 append bits; ADR-0161 implements the source-resolved "
            "self-target append surfaces.",
            text,
        )
        self.assertIn(
            "legacy divergence: The formal model routes input-channel "
            "special messages through process-special-message; RAA and "
            "FSMSIM route write-buf-zero and write-buf-one to literal append "
            "behavior while clearing command-source input. SEMSIM clears the "
            "buffer after append, but AS preserves appended-buffer behavior "
            "consistently with ADR-0160. ADR-0169 implements this recipient "
            "command-message append surface as checked runtime behavior.",
            text,
        )
        self.assertIn(
            "recipient-command-message-surface: "
            "execute-recipient-write-buffer-command-message-append "
            "(sources/write_buffer_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "self-target-surface: "
            "execute-self-target-write-buffer-append "
            "(sources/write_buffer_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "legacy divergence: AS now executes direct self-mailbox "
            "write-buffer command tokens under "
            "UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED and completed "
            "self-target command-buffer write-buffer commands under "
            "UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED; "
            "standard-signal remains the preserved unsupported self-target "
            "command.",
            text,
        )
        self.assertIn(
            "buffer-full-boundary: "
            "preserve-existing-full-buffer-boundary-before-write-buffer-append "
            "(sources/write_buffer_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "legacy divergence: The formal model gates writes to the stem "
            "buffer on less-than-full state and RAA write-buf appends only "
            "when buffer-full? is false; SEMSIM and FSMSIM omit a matching "
            "named command-token full-buffer rule but provide no contrary "
            "full-buffer policy.",
            text,
        )
        self.assertIn(
            "post-append-clearing: preserve-appended-buffer-clear-command-source "
            "(sources/write_buffer_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "legacy divergence: RAA and FSMSIM preserve the appended literal "
            "bit while clearing the active command source; SEMSIM clears the "
            "buffer through its stem special-message wrapper, so AS records "
            "SEMSIM as divergent legacy behavior.",
            text,
        )

    def test_text_status_names_execution_readiness(self):
        report = build_project_status_report()

        text = format_project_status_report(report)

        self.assertIn("Execution readiness:", text)
        self.assertIn(
            "standard-signal: preserved-unsupported; execution changes "
            "allowed: no; blockers: none",
            text,
        )
        self.assertIn(
            "summary: Standard-signal command-token execution remains "
            "preserved as unsupported at the self-target boundaries; "
            "execution changes require new source evidence that replaces the "
            "existing boundary.",
            text,
        )
        self.assertIn(
            "write-buf-zero, write-buf-one: "
            "implemented; execution changes allowed: no; blockers: none",
            text,
        )
        self.assertIn(
            "summary: Write-buffer append execution is implemented for direct "
            "self-mailbox, completed self-target command-buffer, and single "
            "recipient command-message surfaces.",
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
        self.assertIn(
            "ADR-0171 -> sources/standard_signal_source_review_status.json: "
            "The 2026-05-18 source-review snapshot found no new "
            "standard-signal command-token execution evidence and keeps "
            "execution changes disallowed without new source evidence.",
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
        self.assertIn("Resolved resolution questions: none", text)

    def test_json_cli_reports_project_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_project_status_cli(["--format", "json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["schema_version"], PROJECT_STATUS_SCHEMA_VERSION)
        self.assertEqual(payload["transition_evidence"]["bundle_count"], 11)
        self.assertEqual(
            payload["transition_evidence"]["bundles"],
            TRANSITION_BUNDLES,
        )
        self.assertEqual(payload["chain_evidence"]["bundle_count"], 2)
        self.assertEqual(payload["chain_evidence"]["bundles"], CHAIN_BUNDLES)
        self.assertTrue(payload["transition_claims"]["accepted"])
        for key, expected in TRANSITION_CLAIMS.items():
            self.assertEqual(payload["transition_claims"][key], expected)
        self.assertEqual(payload["transition_claims"]["failed_subjects"], [])
        self.assertEqual(
            payload["transition_claims"]["results"][0]["claim_id"],
            "UC-FIXED-OUTPUT-PRESERVED",
        )
        self.assertTrue(payload["transition_proof_certificates"]["accepted"])
        for key, expected in TRANSITION_PROOF_CERTIFICATES.items():
            self.assertEqual(payload["transition_proof_certificates"][key], expected)
        self.assertEqual(
            payload["transition_proof_certificates"]["failed_subjects"],
            [],
        )
        self.assertEqual(
            payload["transition_proof_certificates"]["results"][0]["claim_id"],
            "UC-FIXED-OUTPUT-PRESERVED",
        )
        self.assertTrue(payload["chain_claims"]["accepted"])
        for key, expected in CHAIN_CLAIMS.items():
            self.assertEqual(payload["chain_claims"][key], expected)
        self.assertEqual(payload["chain_claims"]["failed_subjects"], [])
        self.assertEqual(
            payload["chain_claims"]["results"][0]["subject"],
            "chain-language-manifest",
        )
        self.assertTrue(payload["transition_language"]["accepted"])
        for key, expected in TRANSITION_LANGUAGE.items():
            self.assertEqual(payload["transition_language"][key], expected)
        self.assertEqual(payload["transition_language"]["failed_subjects"], [])
        self.assertTrue(payload["chain_language"]["accepted"])
        for key, expected in CHAIN_LANGUAGE.items():
            self.assertEqual(payload["chain_language"][key], expected)
        self.assertEqual(payload["chain_language"]["failed_subjects"], [])
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
                STANDARD_SIGNAL_BLOCKED_RUNTIME_SURFACES,
                WRITE_BUFFER_BLOCKED_RUNTIME_SURFACES,
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
                item["resolved_resolution_questions"]
                for item in payload["frontier"]["source_statuses"]
            ],
            [
                [],
                STANDARD_SIGNAL_RESOLVED_QUESTIONS,
                WRITE_BUFFER_RESOLVED_QUESTIONS,
            ],
        )
        self.assertEqual(
            [
                item["resolution_question_evidence"]
                for item in payload["frontier"]["source_statuses"]
            ],
            [
                [],
                STANDARD_SIGNAL_RESOLUTION_QUESTION_EVIDENCE,
                WRITE_BUFFER_RESOLUTION_QUESTION_EVIDENCE,
            ],
        )
        self.assertEqual(
            [
                item["execution_readiness"]
                for item in payload["frontier"]["source_statuses"]
            ],
            [
                {},
                STANDARD_SIGNAL_EXECUTION_READINESS,
                WRITE_BUFFER_EXECUTION_READINESS,
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

    def test_duplicate_resolution_question_id_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "duplicate_resolution_question_id.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "write-buf-zero",
                    "as_boundary": "Keep this command blocked here.",
                    "required_resolution_questions": [
                        {
                            "question_id": "buffer-full-boundary",
                            "summary": "Decide buffer-full behavior.",
                        },
                        {
                            "question_id": "buffer-full-boundary",
                            "summary": "Still decide buffer-full behavior.",
                        },
                    ],
                    "resolution_question_evidence": [
                        {
                            "question_id": "buffer-full-boundary",
                            "evidence": "Sources diverge here.",
                        }
                    ],
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
            "duplicate resolution question_id",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_scalar_resolution_question_evidence_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "scalar_resolution_question_evidence.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolution_question_evidence": "source conflict",
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
            "resolution_question_evidence",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_resolution_question_evidence_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_resolution_question_evidence.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolution_question_evidence": [
                        {
                            "question_id": "recipient-surface",
                            "evidence": " ",
                        }
                    ],
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
            "evidence",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_unmatched_resolution_question_evidence_id_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "unmatched_resolution_question_evidence.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "required_resolution_questions": [
                        {
                            "question_id": "recipient-surface",
                            "summary": "Decide the recipient surface.",
                        }
                    ],
                    "resolution_question_evidence": [
                        {
                            "question_id": "recipent-surface",
                            "evidence": "Typo should not attach evidence.",
                        }
                    ],
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
            "match required_resolution_questions",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_missing_resolution_question_evidence_coverage_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "missing_resolution_question_evidence.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "required_resolution_questions": [
                        {
                            "question_id": "recipient-surface",
                            "summary": "Decide the recipient surface.",
                        }
                    ],
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
            "cover required_resolution_questions",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_scalar_execution_readiness_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "scalar_execution_readiness.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "write-buf-zero",
                    "as_boundary": "Keep this command blocked here.",
                    "execution_readiness": "blocked",
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
            "execution_readiness",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_non_bool_execution_change_allowed_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "non_bool_execution_readiness.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "write-buf-zero",
                    "as_boundary": "Keep this command blocked here.",
                    "execution_readiness": {
                        "decision": "blocked",
                        "execution_change_allowed": "no",
                        "blocked_by_resolution_questions": [],
                        "summary": "Keep execution blocked.",
                    },
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
            "execution_change_allowed",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_execution_readiness_blocker_must_match_unresolved_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "unmatched_execution_readiness_blocker.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "write-buf-zero",
                    "as_boundary": "Keep this command blocked here.",
                    "required_resolution_questions": [
                        {
                            "question_id": "buffer-full-boundary",
                            "summary": "Decide buffer-full behavior.",
                        }
                    ],
                    "resolution_question_evidence": [
                        {
                            "question_id": "buffer-full-boundary",
                            "evidence": "Sources diverge here.",
                        }
                    ],
                    "execution_readiness": {
                        "decision": "blocked",
                        "execution_change_allowed": False,
                        "blocked_by_resolution_questions": [
                            "post-append-clearing",
                        ],
                        "summary": "Keep execution blocked.",
                    },
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
            "blocked_by_resolution_questions",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blocked_execution_readiness_must_cover_unresolved_questions(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "partial_execution_readiness_blockers.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "write-buf-zero",
                    "as_boundary": "Keep this command blocked here.",
                    "required_resolution_questions": [
                        {
                            "question_id": "buffer-full-boundary",
                            "summary": "Decide buffer-full behavior.",
                        },
                        {
                            "question_id": "post-append-clearing",
                            "summary": "Decide post-append clearing.",
                        },
                    ],
                    "resolution_question_evidence": [
                        {
                            "question_id": "buffer-full-boundary",
                            "evidence": "Sources diverge here.",
                        },
                        {
                            "question_id": "post-append-clearing",
                            "evidence": "Sources diverge here too.",
                        },
                    ],
                    "execution_readiness": {
                        "decision": "blocked",
                        "execution_change_allowed": False,
                        "blocked_by_resolution_questions": [
                            "buffer-full-boundary",
                        ],
                        "summary": "Keep execution blocked.",
                    },
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
            "cover required_resolution_questions",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_execution_readiness_cannot_allow_with_unresolved_questions(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "allowed_with_unresolved_questions.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "write-buf-zero",
                    "as_boundary": "Keep this command blocked here.",
                    "required_resolution_questions": [
                        {
                            "question_id": "buffer-full-boundary",
                            "summary": "Decide buffer-full behavior.",
                        }
                    ],
                    "resolution_question_evidence": [
                        {
                            "question_id": "buffer-full-boundary",
                            "evidence": "Sources diverge here.",
                        }
                    ],
                    "execution_readiness": {
                        "decision": "ready",
                        "execution_change_allowed": True,
                        "blocked_by_resolution_questions": [],
                        "summary": "Execution is ready.",
                    },
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
            "unresolved required_resolution_questions",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blocked_execution_readiness_cannot_allow_execution_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blocked_but_execution_allowed.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "write-buf-zero",
                    "as_boundary": "Keep this command blocked here.",
                    "execution_readiness": {
                        "decision": "blocked",
                        "execution_change_allowed": True,
                        "blocked_by_resolution_questions": [],
                        "summary": "Execution is blocked.",
                    },
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
            "blocked",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_partial_resolution_question_evidence_coverage_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "partial_resolution_question_evidence.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "required_resolution_questions": [
                        {
                            "question_id": "recipient-surface",
                            "summary": "Decide the recipient surface.",
                        },
                        {
                            "question_id": "self-target-surface",
                            "summary": "Decide the self-target surface.",
                        },
                    ],
                    "resolution_question_evidence": [
                        {
                            "question_id": "recipient-surface",
                            "evidence": "Recipient evidence is present.",
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
            "cover required_resolution_questions",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_scalar_resolved_resolution_questions_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "scalar_resolved_resolution_questions.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolved_resolution_questions": "command-table-offset",
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
            "resolved_resolution_questions",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_resolved_resolution_question_id_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_resolved_resolution_question_id.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolved_resolution_questions": [
                        {"question_id": " ", "decision": "resolved"}
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
            "resolved resolution question_id",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_resolved_resolution_question_decision_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_resolved_resolution_question_decision.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolved_resolution_questions": [
                        {"question_id": "command-table-offset", "decision": "  "}
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
            "resolved resolution question decision",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_duplicate_resolved_resolution_question_id_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "duplicate_resolved_resolution_question_id.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolved_resolution_questions": [
                        {
                            "question_id": "recipient-surface",
                            "decision": "reject-recipient-command",
                        },
                        {
                            "question_id": "recipient-surface",
                            "decision": "reject-recipient-command-again",
                        },
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
            "duplicate resolved resolution question_id",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_missing_resolved_resolution_question_source_path_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "missing_source_status.json"
            invalid_status = Path(tmp) / "missing_resolved_source_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolved_resolution_questions": [
                        {
                            "question_id": "command-table-offset",
                            "decision": "resolved",
                            "source_status": str(missing_path),
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
            "resolved resolution question source_status path must exist",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_invalid_json_resolved_resolution_question_source_path_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_json_path = Path(tmp) / "invalid_source_status.json"
            invalid_json_path.write_text("{not-json", encoding="utf-8")
            invalid_status = Path(tmp) / "invalid_resolved_source_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolved_resolution_questions": [
                        {
                            "question_id": "command-table-offset",
                            "decision": "resolved",
                            "source_status": str(invalid_json_path),
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
            "resolved resolution question source_status path must contain JSON",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_non_object_resolved_resolution_question_source_path_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            non_object_path = Path(tmp) / "non_object_source_status.json"
            non_object_path.write_text("[]", encoding="utf-8")
            invalid_status = Path(tmp) / "non_object_resolved_source_status.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolved_resolution_questions": [
                        {
                            "question_id": "command-table-offset",
                            "decision": "resolved",
                            "source_status": str(non_object_path),
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
            "resolved resolution question source_status path must contain a JSON object",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_non_integer_resolved_resolution_question_offset_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "non_integer_resolved_offset.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolved_resolution_questions": [
                        {
                            "question_id": "command-table-offset",
                            "decision": "resolved",
                            "formal_command_offset": "0",
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
            "formal_command_offset",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_blank_resolved_resolution_question_legacy_divergence_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "blank_resolved_legacy_divergence.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "resolved_resolution_questions": [
                        {
                            "question_id": "command-table-offset",
                            "decision": "resolved",
                            "legacy_divergence": "  ",
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
            "legacy_divergence",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_overlapping_unresolved_and_resolved_question_id_is_structured_failure_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_status = Path(tmp) / "overlapping_resolution_question.json"
            invalid_status.write_text(
                json.dumps({
                    "decision": "do-not-implement-command-yet",
                    "safe_next_slice": "revisit-command-source-evidence",
                    "command": "standard-signal",
                    "as_boundary": "Keep this command blocked here.",
                    "required_resolution_questions": [
                        {
                            "question_id": "recipient-surface",
                            "summary": "Decide the recipient surface.",
                        }
                    ],
                    "resolution_question_evidence": [
                        {
                            "question_id": "recipient-surface",
                            "evidence": "Evidence keeps the unresolved shape valid.",
                        }
                    ],
                    "resolved_resolution_questions": [
                        {
                            "question_id": "recipient-surface",
                            "decision": "resolved",
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
            "cannot be both unresolved and resolved",
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
        self.assertIn("Transition evidence: accepted (11 bundles)", completed.stdout)
        self.assertIn("Chain evidence: accepted (2 bundles)", completed.stdout)


if __name__ == "__main__":
    unittest.main()
