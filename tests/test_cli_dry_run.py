import tempfile
import unittest
from pathlib import Path

from generator import cli


class TestCLIDryRun(unittest.TestCase):
    def test_cli_dry_run_creates_llm_file_but_not_handlers(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            name = "dry_project"
            # call CLI main non-interactively
            argv = [
                "--name",
                name,
                "--mode",
                "full",
                "--framework",
                "flask",
                "--use-llm",
                "--llm-prompt",
                "Teste",
                "--out",
                str(out),
                "--dry-run",
            ]
            res = cli.main(argv)
            self.assertEqual(res, 0)
            proj = out / name
            self.assertTrue(proj.exists())
            # llm_generated.txt should exist
            self.assertTrue((proj / "llm_generated.txt").exists())
            # llm_handlers.py should NOT exist because dry-run
            self.assertFalse((proj / "llm_handlers.py").exists())


if __name__ == "__main__":
    unittest.main()
