import json
import unittest
from pathlib import Path


STATUS = Path("sources/standard_signal_source_review_status.json")
MANIFEST = Path("sources/manifest.json")
STANDARD_SIGNAL_STATUS = Path("sources/standard_signal_command_semantics_status.json")
PRC_ROOT = Path("/home/sean/Projects/_upstream/prc")
NO_STANDARD_SIGNAL_SAFE_NEXT = (
    "no-standard-signal-command-token-execution-change-without-new-source-evidence"
)


class StandardSignalSourceReviewStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))

    def test_review_snapshot_closes_active_standard_signal_source_review_gate(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(self.status["reviewed_at"], "2026-05-18")
        self.assertEqual(
            self.status["review_id"],
            "standard-signal-command-token-source-review-2026-05-18",
        )
        self.assertEqual(
            self.status["decision"],
            "no-new-standard-signal-command-token-execution-evidence",
        )
        self.assertEqual(self.status["runtime_change"], "none-source-review-only")
        self.assertEqual(self.status["command"], "standard-signal")
        self.assertEqual(
            self.status["review_scope"]["safe_next_slice_closed"],
            "review-new-standard-signal-command-token-source-evidence-before-execution-change",
        )
        self.assertIn(
            "standard-signal command-token",
            self.status["review_scope"]["reviewed_question"],
        )

    def test_remote_head_checks_cover_manifest_sources_without_prc_drift(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest_by_id = {repo["id"]: repo for repo in manifest["repositories"]}
        checks = {check["id"]: check for check in self.status["remote_head_checks"]}

        self.assertEqual(
            set(checks),
            {"as", "afs", "prc", "sjas", "proflog", "leantap"},
        )
        for source_id, check in checks.items():
            with self.subTest(source_id=source_id):
                manifest_repo = manifest_by_id[source_id]
                self.assertEqual(check["clone_url"], manifest_repo["clone_url"])
                self.assertEqual(
                    check["public_remote_head"],
                    manifest_repo["public_remote_head_at_review"],
                )
                self.assertEqual(
                    check["manifest_remote_head"],
                    manifest_repo["public_remote_head_at_review"],
                )
                self.assertFalse(check["changed_since_manifest"])
                self.assertIn("standard-signal", check["standard_signal_relevance"])

        self.assertEqual(
            checks["prc"]["public_remote_head"],
            "7e82c73fac8f108faac801a5c65e2c2b92653ba5",
        )

    def test_primary_prc_local_witness_and_source_status_inputs_are_recorded(self):
        local_prc = self.status["local_prc_review"]

        self.assertEqual(Path(local_prc["local_path"]), PRC_ROOT)
        self.assertEqual(
            local_prc["head"],
            "7e82c73fac8f108faac801a5c65e2c2b92653ba5",
        )
        self.assertEqual(local_prc["status"], "unchanged-primary-command-token-witness")
        self.assertIn("formal-model.txt", local_prc["formal_model_loci"][0])

        self.assertEqual(
            set(self.status["source_status_inputs"]),
            {
                "sources/standard_signal_command_semantics_status.json",
                "sources/recipient_non_init_command_source_status.json",
                "sources/guile_asmsim_command_semantics_status.json",
                "sources/asmsim_process_buffer_status.json",
                "sources/official_tla_universal_cell_status.json",
            },
        )

    def test_execution_boundary_keeps_standard_signal_unsupported(self):
        boundary = self.status["execution_boundary"]

        self.assertFalse(boundary["replaces_existing_boundary"])
        self.assertFalse(boundary["standard_signal_execution_change_allowed"])
        self.assertEqual(
            boundary["status_safe_next_slice"],
            NO_STANDARD_SIGNAL_SAFE_NEXT,
        )
        self.assertIn("unsupported", boundary["summary"])
        self.assertIn("new source evidence", boundary["summary"])

    def test_standard_signal_source_status_links_latest_review(self):
        standard_signal_status = json.loads(
            STANDARD_SIGNAL_STATUS.read_text(encoding="utf-8")
        )

        latest = standard_signal_status["latest_source_review"]
        self.assertEqual(latest["path"], str(STATUS))
        self.assertEqual(latest["review_id"], self.status["review_id"])
        self.assertEqual(latest["decision"], self.status["decision"])
        self.assertFalse(latest["execution_change_allowed"])
        self.assertEqual(
            standard_signal_status["safe_next_slice"],
            NO_STANDARD_SIGNAL_SAFE_NEXT,
        )
        self.assertTrue(
            any(
                item["adr"] == "ADR-0171" and item["path"] == str(STATUS)
                for item in standard_signal_status["additional_source_statuses"]
            )
        )


if __name__ == "__main__":
    unittest.main()
