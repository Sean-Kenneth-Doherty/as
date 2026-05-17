import contextlib
import io
import subprocess
import sys
import unittest
from pathlib import Path

from autarkic_systems.chain_evidence_bundle import run_chain_evidence_bundle_cli


BUNDLE = Path("evidence/chains/neighbor_delivery_chain_bundle.json")
REGISTRY = Path("evidence/chains/manifest.json")


class ChainEvidenceCliTargetSelectionTests(unittest.TestCase):
    def test_cli_rejects_bundle_and_registry_together(self):
        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                run_chain_evidence_bundle_cli(
                    ["--bundle", str(BUNDLE), "--registry", str(REGISTRY)]
                )

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("not allowed with argument", stderr.getvalue())

    def test_module_execution_rejects_ambiguous_target_selection(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.chain_evidence_bundle",
                "--bundle",
                str(BUNDLE),
                "--registry",
                str(REGISTRY),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("not allowed with argument", completed.stderr)


if __name__ == "__main__":
    unittest.main()
