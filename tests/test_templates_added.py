import tempfile
import unittest
from pathlib import Path

from generator.generate import create_project


class TestTemplatesAdded(unittest.TestCase):
    def test_fastapi_and_react_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            p_fast = create_project(
                "p_fast_api", base, mode="full", framework="fastapi"
            )
            self.assertTrue((p_fast / "main.py").exists())
            self.assertTrue((p_fast / "requirements.txt").exists())

            p_react = create_project("p_react", base, mode="full", framework="react")
            # react template includes public/index.html and src/App.js
            self.assertTrue((p_react / "public" / "index.html").exists())
            self.assertTrue((p_react / "src" / "App.js").exists())


if __name__ == "__main__":
    unittest.main()
