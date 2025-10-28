import tempfile
import unittest
from pathlib import Path

from generator import llm
from generator.generate import create_project


class TestLLMIntegration(unittest.TestCase):
    def test_integrate_snippet_flask(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            p = create_project("p_fl", base, mode="minimal", framework="flask")
            # create a simple app.py to simulate
            app_py = p / "app.py"
            app_py.write_text(
                (
                    "from flask import Flask\n"
                    "app = Flask(__name__)\n\n"
                    "@app.route('/')\n"
                    "def index():\n"
                    "    return 'ok'\n\n"
                    "if __name__ == '__main__':\n"
                    "    app.run()\n"
                )
            )
            snippet = "@app.route('/hello')\ndef hello():\n    return {'msg': 'hi'}\n"
            ok = llm.integrate_snippet(p, "flask", snippet)
            self.assertTrue(ok)
            self.assertTrue((p / "llm_handlers.py").exists())
            # ensure app.py contains registration
            text = app_py.read_text()
            self.assertIn("llm_handlers", text)

    def test_integrate_snippet_express(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            p = create_project("p_ex", base, mode="full", framework="express")
            # create index.js if not present
            idx = p / "index.js"
            if not idx.exists():
                idx.write_text(
                    (
                        "const express = require('express');\n"
                        "const app = express();\n"
                        "app.listen(3000);\n"
                    )
                )
            snippet = "app.get('/hello', (req, res) => res.json({msg: 'hi'}));\n"
            ok = llm.integrate_snippet(p, "express", snippet)
            self.assertTrue(ok)
            self.assertTrue((p / "llm_handlers.js").exists())
            text = idx.read_text()
            self.assertIn("llm_handlers", text)

    def test_integrate_snippet_fastapi(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            p = create_project("p_fa", base, mode="full", framework="fastapi")
            main = p / "main.py"
            if not main.exists():
                main.write_text(
                    (
                        "from fastapi import FastAPI\n"
                        "app = FastAPI()\n"
                        "if __name__ == '__main__':\n"
                        "    import uvicorn\n"
                        "    uvicorn.run(app, port=8000)\n"
                    )
                )
            snippet = (
                "@app.get('/hello')\nasync def hello():\n    return {'msg': 'hi'}\n"
            )
            ok = llm.integrate_snippet(p, "fastapi", snippet)
            self.assertTrue(ok)
            self.assertTrue((p / "llm_handlers.py").exists())
            text = main.read_text()
            self.assertIn("llm_handlers", text)


if __name__ == "__main__":
    unittest.main()
