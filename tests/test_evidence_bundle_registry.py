import unittest
from dataclasses import replace
from pathlib import Path
import json
import tempfile

from autarkic_systems.evidence_bundle import (
    load_evidence_bundle_registry,
    validate_evidence_bundle_registry,
)


REGISTRY = Path("evidence/manifest.json")
BUNDLE = Path("evidence/recipient_init_command_message_bundle.json")
BUNDLE_ID = "recipient-init-command-message-transition-evidence-bundle"
CLAIM_ID = "UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED"
STATUS = "recipient-init-command-message-processed"
REJECTION_BUNDLE = Path("evidence/recipient_non_init_command_rejection_bundle.json")
REJECTION_BUNDLE_ID = "recipient-non-init-command-rejection-evidence-bundle"
REJECTION_CLAIM_ID = "UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED"
REJECTION_STATUS = "rejected-input"
MULTI_COMMAND_BUNDLE = Path("evidence/multi_command_recipient_rejection_bundle.json")
MULTI_COMMAND_BUNDLE_ID = "multi-command-recipient-rejection-evidence-bundle"
SELF_MAILBOX_BUNDLE = Path("evidence/self_mailbox_init_bundle.json")
SELF_MAILBOX_BUNDLE_ID = "self-mailbox-init-evidence-bundle"
SELF_MAILBOX_CLAIM_ID = "UC-STEM-SELF-MAILBOX-INIT-COMMAND"
SELF_MAILBOX_STATUS = "self-mailbox-processed"
UNSUPPORTED_MAILBOX_BUNDLE = Path("evidence/self_mailbox_unsupported_bundle.json")
UNSUPPORTED_MAILBOX_BUNDLE_ID = "self-mailbox-unsupported-evidence-bundle"
UNSUPPORTED_MAILBOX_CLAIM_ID = "UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED"
UNSUPPORTED_MAILBOX_STATUS = "self-mailbox-unsupported"
SELF_COMMAND_BUFFER_BUNDLE = Path("evidence/self_command_buffer_init_bundle.json")
SELF_COMMAND_BUFFER_BUNDLE_ID = "self-command-buffer-init-evidence-bundle"
SELF_COMMAND_BUFFER_CLAIM_ID = "UC-STEM-COMMAND-BUFFER-SELF-INIT"
SELF_COMMAND_BUFFER_STATUS = "stem-command-buffer-self-processed"
UNSUPPORTED_COMMAND_BUFFER_BUNDLE = Path("evidence/command_buffer_unsupported_bundle.json")
UNSUPPORTED_COMMAND_BUFFER_BUNDLE_ID = "command-buffer-unsupported-evidence-bundle"
UNSUPPORTED_COMMAND_BUFFER_CLAIM_ID = "UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED"
UNSUPPORTED_COMMAND_BUFFER_STATUS = "stem-buffer-appended"


class EvidenceBundleRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_evidence_bundle_registry(REGISTRY)

    def test_registry_names_the_transition_evidence_surface(self):
        self.assertEqual(self.registry.schema_version, 1)
        self.assertEqual(self.registry.registry_id, "transition-evidence-bundle-registry")
        self.assertEqual(self.registry.reviewed_at, "2026-05-17")
        self.assertIn("transition evidence bundles", self.registry.purpose)

    def test_registry_records_the_recipient_init_bundle(self):
        entries = {entry.bundle_id: entry for entry in self.registry.bundles}
        entry = entries[BUNDLE_ID]

        self.assertEqual(entry.bundle_id, BUNDLE_ID)
        self.assertEqual(entry.path, BUNDLE)
        self.assertEqual(entry.claim_id, CLAIM_ID)
        self.assertEqual(entry.expected_status, STATUS)

    def test_registry_records_the_recipient_non_init_rejection_bundle(self):
        entries = {entry.bundle_id: entry for entry in self.registry.bundles}
        entry = entries[REJECTION_BUNDLE_ID]

        self.assertEqual(entry.path, REJECTION_BUNDLE)
        self.assertEqual(entry.claim_id, REJECTION_CLAIM_ID)
        self.assertEqual(entry.expected_status, REJECTION_STATUS)

    def test_registry_records_the_multi_command_rejection_bundle(self):
        entries = {entry.bundle_id: entry for entry in self.registry.bundles}
        entry = entries[MULTI_COMMAND_BUNDLE_ID]

        self.assertEqual(len(self.registry.bundles), 7)
        self.assertEqual(entry.path, MULTI_COMMAND_BUNDLE)
        self.assertEqual(entry.claim_id, REJECTION_CLAIM_ID)
        self.assertEqual(entry.expected_status, REJECTION_STATUS)

    def test_registry_records_the_self_mailbox_init_bundle(self):
        entries = {entry.bundle_id: entry for entry in self.registry.bundles}
        entry = entries[SELF_MAILBOX_BUNDLE_ID]

        self.assertEqual(entry.path, SELF_MAILBOX_BUNDLE)
        self.assertEqual(entry.claim_id, SELF_MAILBOX_CLAIM_ID)
        self.assertEqual(entry.expected_status, SELF_MAILBOX_STATUS)

    def test_registry_records_the_unsupported_self_mailbox_bundle(self):
        entries = {entry.bundle_id: entry for entry in self.registry.bundles}
        entry = entries[UNSUPPORTED_MAILBOX_BUNDLE_ID]

        self.assertEqual(entry.path, UNSUPPORTED_MAILBOX_BUNDLE)
        self.assertEqual(entry.claim_id, UNSUPPORTED_MAILBOX_CLAIM_ID)
        self.assertEqual(entry.expected_status, UNSUPPORTED_MAILBOX_STATUS)

    def test_registry_records_the_self_command_buffer_init_bundle(self):
        entries = {entry.bundle_id: entry for entry in self.registry.bundles}
        entry = entries[SELF_COMMAND_BUFFER_BUNDLE_ID]

        self.assertEqual(entry.path, SELF_COMMAND_BUFFER_BUNDLE)
        self.assertEqual(entry.claim_id, SELF_COMMAND_BUFFER_CLAIM_ID)
        self.assertEqual(entry.expected_status, SELF_COMMAND_BUFFER_STATUS)

    def test_registry_records_the_unsupported_command_buffer_bundle(self):
        entries = {entry.bundle_id: entry for entry in self.registry.bundles}
        entry = entries[UNSUPPORTED_COMMAND_BUFFER_BUNDLE_ID]

        self.assertEqual(entry.path, UNSUPPORTED_COMMAND_BUFFER_BUNDLE)
        self.assertEqual(entry.claim_id, UNSUPPORTED_COMMAND_BUFFER_CLAIM_ID)
        self.assertEqual(entry.expected_status, UNSUPPORTED_COMMAND_BUFFER_STATUS)

    def test_registry_validates_all_registered_bundles(self):
        results = validate_evidence_bundle_registry(self.registry)

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            {result.subject for result in results},
            {
                "registry-schema",
                "registry-entries",
                "registry-bundle-paths",
                "registry-bundle-validation",
                "registry-completeness",
            },
        )

    def test_duplicate_bundle_ids_are_rejected(self):
        entry = self.registry.bundles[0]
        drifted = replace(self.registry, bundles=(entry, entry))

        results = validate_evidence_bundle_registry(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "registry-entries"
                and "duplicate bundle ids" in result.detail
                for result in results
            ),
            results,
        )

    def test_missing_bundle_path_is_rejected(self):
        entry = self.registry.bundles[0]
        drifted_entry = replace(entry, path=Path("evidence/missing_bundle.json"))
        drifted = replace(self.registry, bundles=(drifted_entry,))

        results = validate_evidence_bundle_registry(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "registry-bundle-paths"
                and "missing bundle" in result.detail
                for result in results
            ),
            results,
        )

    def test_unregistered_sibling_bundle_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "manifest.json"
            registered_bundle = Path(tmp) / "registered_bundle.json"
            unregistered_bundle = Path(tmp) / "unregistered_bundle.json"

            registered_bundle.write_text(
                BUNDLE.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            unregistered_bundle.write_text(
                REJECTION_BUNDLE.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            registry_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "registry_id": "drifted-registry",
                        "reviewed_at": "2026-05-17",
                        "purpose": "Exercise unregistered bundle detection.",
                        "bundles": [
                            {
                                "bundle_id": BUNDLE_ID,
                                "path": str(registered_bundle),
                                "claim_id": CLAIM_ID,
                                "expected_status": STATUS,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            registry = load_evidence_bundle_registry(registry_path)
            results = validate_evidence_bundle_registry(registry)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "registry-completeness"
                and "unregistered bundle files" in result.detail
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
