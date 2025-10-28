import tempfile
import unittest
from pathlib import Path

from generator.generate import create_project


class TestGenerateThree(unittest.TestCase):
    def test_generate_three_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            # minimal
            p1 = create_project("p_minimal", base, mode="minimal", framework="flask")
            self.assertTrue((p1 / "app.py").exists())
            # full flask
            p2 = create_project("p_full_flask", base, mode="full", framework="flask")
            self.assertTrue((p2 / "app.py").exists())
            self.assertTrue((p2 / "templates" / "index.html").exists())
            # full express
            p3 = create_project(
                "p_full_express", base, mode="full", framework="express"
            )
            self.assertTrue((p3 / "index.js").exists())
            self.assertTrue((p3 / "public" / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
