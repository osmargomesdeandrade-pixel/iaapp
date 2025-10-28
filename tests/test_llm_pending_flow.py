import tempfile
import unittest
from pathlib import Path

from generator import llm
from generator.generate import create_project


class TestLLMPendingFlow(unittest.TestCase):
    def test_pending_and_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            p = create_project("ppend", base, mode="minimal", framework="flask")
            # create a simple app.py
            app_py = p / "app.py"
            app_py.write_text(
                "from flask import Flask\napp = Flask(__name__)\n\nif __name__ == '__main__':\n    app.run()\n"
            )
            risky = "import subprocess\nsubprocess.Popen(['echo','hi'])\n"
            res = llm.process_snippet(p, "flask", risky, force=False, dry_run=False)
            self.assertFalse(res["integrated"])
            self.assertTrue(res["pending"])
            self.assertTrue((p / "llm_pending.txt").exists())
            # approve pending
            ok = llm.approve_pending(p, "flask")
            self.assertTrue(ok)
            # pending should be removed and handlers created
            self.assertFalse((p / "llm_pending.txt").exists())
            self.assertTrue((p / "llm_handlers.py").exists())


if __name__ == "__main__":
    unittest.main()
