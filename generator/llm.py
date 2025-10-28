"""Stub para integração com LLMs (opcional).

Este módulo oferece um wrapper mínimo que pode ser estendido para usar OpenAI
ou outros provedores. Por segurança, nenhuma chamada externa é feita sem a
existência da variável de ambiente `OPENAI_API_KEY`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")


def generate_code_from_prompt(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """Gera texto/código a partir do prompt usando OpenAI quando a chave estiver definida.

    Retorna mensagem explicativa se a chave não estiver disponível.
    """
    if not OPENAI_KEY:
        return "# LLM não configurado. Defina OPENAI_API_KEY para habilitar geração via LLM."

    try:
        import openai

        openai.api_key = OPENAI_KEY
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.2,
        )
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        return f"# Erro ao chamar LLM: {e}"


def integrate_snippet(project_dir, framework: str, snippet: str) -> bool:
    """Integrate a generated snippet into the generated project.

    Strategy:
    - For Python frameworks (flask, fastapi): create `llm_handlers.py` with a
      `def register(app):` wrapper around the snippet, and then modify the main
      app file to call that register(app) before the server start.
    - For express: create `llm_handlers.js` that exports a function (app) and
      call it from `index.js` before app.listen.

    Returns True on success.
    """
    from pathlib import Path

    p = Path(project_dir)
    try:
        # analyze snippet for risky constructs
        analysis = analyze_snippet(snippet)
        # prepare log
        log_lines = []
        log_lines.append(f"Snippet analysis: {analysis}")
        from datetime import datetime, timezone

        log_lines.append(f"Timestamp: {datetime.now(timezone.utc).isoformat()}Z")
        if framework.lower() in ("flask", "fastapi"):
            handlers = p / "llm_handlers.py"
            # wrap snippet into register(app)
            indented = "\n".join(
                ("    " + line) if line.strip() else "" for line in snippet.splitlines()
            )
            content = f"def register(app):\n{indented}\n"
            handlers.write_text(content)
            log_lines.append("Wrote llm_handlers.py")

            # find main file to modify
            main_candidates = ["app.py", "main.py"]
            main_file = None
            for name in main_candidates:
                if (p / name).exists():
                    main_file = p / name
                    break
            if not main_file:
                # nothing to modify, but handlers file written
                _write_log(project_dir, log_lines)
                return True

            # backup original
            backup_dir = p / "llm_backup"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / main_file.name
            backup_path.write_bytes(main_file.read_bytes())
            log_lines.append(f"Backed up {main_file.name} to {backup_path}")

            text = main_file.read_text()
            insert_point = text.rfind('\nif __name__ == "__main__":')
            register_code = (
                "\n\ntry:\n"
                "    from llm_handlers import register as _llm_register\n"
                "    _llm_register(app)\n"
                "except Exception as _e:\n"
                "    print('LLM handlers registration failed:', _e)\n"
            )
            if insert_point != -1:
                new_text = text[:insert_point] + register_code + text[insert_point:]
            else:
                new_text = text + register_code
            main_file.write_text(new_text)
            log_lines.append(f"Modified {main_file.name} to call llm_handlers.register")
            _write_log(project_dir, log_lines)
            return True

        elif framework.lower() == "express":
            handlers = p / "llm_handlers.js"
            # wrap snippet into module.exports = function(app) { ... }
            indented = "\n".join(
                ("  " + line) if line.strip() else "" for line in snippet.splitlines()
            )
            content = f"module.exports = function(app) {{\n{indented}\n}}\n"
            handlers.write_text(content)
            log_lines.append("Wrote llm_handlers.js")

            index_js = p / "index.js"
            if not index_js.exists():
                _write_log(project_dir, log_lines)
                return True
            # backup
            backup_dir = p / "llm_backup"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / index_js.name
            backup_path.write_bytes(index_js.read_bytes())
            log_lines.append(f"Backed up {index_js.name} to {backup_path}")

            text = index_js.read_text()
            # insert require and call before app.listen
            call_code = "\nconst llm_handlers = require('./llm_handlers');\nllm_handlers(app);\n"
            listen_idx = text.rfind("\napp.listen(")
            if listen_idx != -1:
                new_text = text[:listen_idx] + call_code + text[listen_idx:]
            else:
                new_text = text + call_code
            index_js.write_text(new_text)
            log_lines.append(f"Modified {index_js.name} to call llm_handlers")
            _write_log(project_dir, log_lines)
            return True

        else:
            # unsupported framework: just save snippet file
            (p / "llm_generated.txt").write_text(snippet)
            log_lines.append("Saved llm_generated.txt for unsupported framework")
            _write_log(project_dir, log_lines)
            return True
    except Exception:
        try:
            _write_log(project_dir, [f"Integration failed: {sys.exc_info()}"])
        except Exception:
            pass
        return False


def process_snippet(
    project_dir,
    framework: str,
    snippet: str,
    force: bool = False,
    dry_run: bool = False,
) -> dict:
    """Process a snippet: analyze and either integrate, save pending, or save as dry-run.

    Returns dict with keys: integrated(bool), pending(bool), reason(str)
    """
    p = Path(project_dir)
    analysis = analyze_snippet(snippet)
    # consider risky if exec/eval/subprocess present
    risky = (
        analysis.get("has_exec")
        or analysis.get("has_eval")
        or analysis.get("has_subprocess")
    )
    if dry_run:
        try:
            (p / "llm_generated.txt").write_text(snippet)
            _write_log(
                p, ["Dry-run saved snippet (no integration)", f"Analysis: {analysis}"]
            )
        except Exception:
            pass
        return {"integrated": False, "pending": False, "reason": "dry-run saved"}

    if risky and not force:
        # save pending file for manual approval
        try:
            (p / "llm_pending.txt").write_text(snippet)
            _write_log(p, [f"Snippet marked as pending due to risk: {analysis}"])
        except Exception:
            pass
        return {
            "integrated": False,
            "pending": True,
            "reason": "risky snippet saved as pending",
        }

    # safe or forced -> integrate
    ok = integrate_snippet(project_dir, framework, snippet)
    if ok:
        _write_log(p, ["Snippet integrated successfully", f"Analysis: {analysis}"])
        return {"integrated": True, "pending": False, "reason": "integrated"}
    else:
        _write_log(p, ["Integration attempted but failed", f"Analysis: {analysis}"])
        return {"integrated": False, "pending": False, "reason": "integration_failed"}


def approve_pending(project_dir, framework: str) -> bool:
    """Approve a pending snippet: read llm_pending.txt and integrate forcefully."""
    p = Path(project_dir)
    pending = p / "llm_pending.txt"
    if not pending.exists():
        return False
    snippet = pending.read_text()
    # integrate forcefully
    res = integrate_snippet(project_dir, framework, snippet)
    if res:
        try:
            pending.unlink()
            _write_log(p, ["Pending snippet approved and integrated"])
        except Exception:
            pass
        return True
    return False


def analyze_snippet(snippet: str) -> dict:
    """Simple static analysis of the snippet to detect risky constructs.

    Returns a dictionary with boolean flags and a list of imported modules.
    """
    import ast

    flags = {
        "has_exec": False,
        "has_eval": False,
        "has_subprocess": False,
        "has_importlib": False,
        "has___import__": False,
        "imports": [],
    }

    try:
        tree = ast.parse(snippet)
    except SyntaxError:
        # if snippet is not valid Python, fall back to simple heuristics
        return flags

    for node in ast.walk(tree):
        # detect exec/eval usage
        if isinstance(node, ast.Call):
            # function name can be many shapes
            func = node.func
            if isinstance(func, ast.Name):
                if func.id == "exec":
                    flags["has_exec"] = True
                if func.id == "eval":
                    flags["has_eval"] = True
                if func.id == "__import__":
                    flags["has___import__"] = True
            elif isinstance(func, ast.Attribute):
                # e.g., importlib.import_module, subprocess.run
                value = func.value
                attr = func.attr
                if isinstance(value, ast.Name):
                    if value.id == "subprocess" or attr in ("Popen", "call", "run"):
                        flags["has_subprocess"] = True
                    if value.id == "importlib" and attr == "import_module":
                        flags["has_importlib"] = True
                # detect os.system
                if (
                    isinstance(value, ast.Name)
                    and value.id == "os"
                    and attr == "system"
                ):
                    flags["has_subprocess"] = True

        # detect use of subprocess module name in attribute access
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "subprocess":
                flags["has_subprocess"] = True

        # collect imports
        if isinstance(node, ast.Import):
            for n in node.names:
                flags["imports"].append(n.name.split(".")[0])
        if isinstance(node, ast.ImportFrom):
            if node.module:
                flags["imports"].append(node.module.split(".")[0])

    # normalize booleans
    # if snippet imports subprocess or os, consider subprocess usage risky
    if "subprocess" in flags.get("imports", []) or "os" in flags.get("imports", []):
        flags["has_subprocess"] = True
    else:
        flags["has_subprocess"] = bool(flags.get("has_subprocess"))
    flags["has_exec"] = bool(flags.get("has_exec"))
    flags["has_eval"] = bool(flags.get("has_eval"))
    flags["has_importlib"] = bool(flags.get("has_importlib"))
    flags["has___import__"] = bool(flags.get("has___import__"))

    return flags


def _write_log(project_dir, lines):
    try:
        from datetime import datetime, timezone

        p = Path(project_dir)
        log = p / "llm_integration.log"
        with log.open("a", encoding="utf-8") as f:
            f.write("---\n")
            f.write(datetime.now(timezone.utc).isoformat() + "Z\n")
            for line in lines:
                f.write(str(line) + "\n")
    except Exception:
        pass
