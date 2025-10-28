import unittest

from generator import llm


class TestLLMAnalysis(unittest.TestCase):
    def test_analyze_snippet_flags(self):
        s = "import os\nimport subprocess\nexec('rm -rf /')\n"
        res = llm.analyze_snippet(s)
        self.assertTrue(res["has_exec"])
        self.assertTrue(res["has_subprocess"])
        self.assertIn("os", res["imports"])
        self.assertIn("subprocess", res["imports"])


if __name__ == "__main__":
    unittest.main()
