import tempfile
import unittest
from pathlib import Path

from generator.generate import create_project


class TestGeneratorMinimal(unittest.TestCase):
    def test_create_minimal_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            project_name = "test_minimal"
            project_dir = create_project(project_name, target, mode="minimal")
            # check files exist
            self.assertTrue((project_dir / "app.py").exists())
            self.assertTrue((project_dir / "requirements.txt").exists())
            self.assertTrue((project_dir / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
