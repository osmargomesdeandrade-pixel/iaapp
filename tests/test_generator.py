import tempfile
import unittest
from pathlib import Path

from generator.generate import create_project


class TestGenerator(unittest.TestCase):
    def test_create_full_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            project_name = "test_full"
            project_dir = create_project(project_name, target, mode="full")
            # check files exist
            self.assertTrue((project_dir / "app.py").exists())
            self.assertTrue((project_dir / "templates" / "index.html").exists())
            self.assertTrue((project_dir / "static" / "css" / "style.css").exists())


if __name__ == "__main__":
    unittest.main()
