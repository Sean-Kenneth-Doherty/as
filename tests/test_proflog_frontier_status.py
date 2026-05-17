import json
import unittest
from pathlib import Path


STATUS = Path("sources/proflog_frontier_status.json")
PROFLOG_ROOT = Path("/home/sean/Projects/_upstream/proflog")
SJAS_LOG = Path("/home/sean/Projects/_upstream/sjas/nachlass/LOG.md")


class ProflogFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))

    def test_public_main_is_recorded_as_visible_but_not_dependency_ready(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(self.status["repository"], "jpt4/proflog")
        self.assertEqual(
            self.status["decision"],
            "do-not-depend-on-public-main",
        )
        self.assertEqual(
            self.status["public_remote_head"],
            "77af8481d9f41a439eb42e1d8268a5b39f7c5c33",
        )
        self.assertEqual(
            self.status["local_public_head"],
            self.status["public_remote_head"],
        )
        self.assertEqual(self.status["visible_public_branches"], ["main"])

    def test_required_local_witness_paths_are_pinned(self):
        self.assertEqual(Path(self.status["local_public_path"]), PROFLOG_ROOT)
        self.assertEqual(Path(self.status["sjas_log_path"]), SJAS_LOG)

    def test_sjas_frontier_terms_are_recorded_as_missing_from_public_main(self):
        missing_terms = set(self.status["missing_public_frontier_terms"])

        for term in [
            "ADR-0063",
            "ADR-0068",
            "tableau-proof/3",
            "subst-prf/4",
            "subst-code/2",
            "SelfCons1",
            "IS#_D(beta)",
            "lt(1,2)",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, missing_terms)

    def test_smoke_test_failure_is_explicit(self):
        smoke = self.status["smoke_test"]

        self.assertEqual(smoke["command"], "guile proflog.scm")
        self.assertEqual(smoke["status"], "failed")
        self.assertIn("Unbound variable: even", smoke["failure"])


if __name__ == "__main__":
    unittest.main()
