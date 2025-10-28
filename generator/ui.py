"""UI web mínima para orquestrar o gerador de apps.

Rota principal ('/') mostra um formulário para nome, modo e framework. Submissão gera o projeto
na pasta `generated/` e mostra um link para abrir o diretório no sistema de arquivos.

Executar:
  & "C:/Users/User/Desktop/inteligencia artificial/venv/Scripts/python.exe" -m generator.ui

Observação: requer Flask (já instalado no venv do workspace).
"""

from __future__ import annotations

import difflib
import os
from pathlib import Path

from flask import Flask, redirect, render_template_string, request, url_for

from . import llm as llm_module
from .generate import create_project

app = Flask(__name__)

INDEX_HTML = """<!doctype html>
<title>AI App Generator</title>
<h1>Gerador de Apps</h1>
<form method="post">
  <label>Nome do projeto: <input name="name" required></label><br>
    <label>Modo:
        <select name="mode">
            <option value="minimal">minimal</option>
            <option value="full">full</option>
        </select>
    </label><br>
    <label>Framework:
        <select name="framework">
            <option value="flask">flask</option>
            <option value="express">express</option>
        </select>
    </label><br>
  <label>Usar LLM para gerar um snippet (experimental): <input type="checkbox" name="use_llm" value="1"></label><br>
  <label>Preview only (não integrar): <input type="checkbox" name="dry_run" value="1"></label><br>
    <label>Prompt para LLM (se usado):<br>
        <textarea name="prompt" rows="4" cols="60"
            placeholder="Ex: Gere uma rota /hello que retorna JSON"></textarea></label><br>
  <button type="submit">Gerar</button>
</form>
{% if project_path %}
  <p>Projeto gerado em: {{ project_path }}</p>
  <p>Abra a pasta gerada no seu explorador de arquivos.</p>
{% endif %}
{% if llm_output %}
  <h3>LLM output</h3>
  <pre>{{ llm_output }}</pre>
{% endif %}
"""

REVIEWS_HTML = """<!doctype html>
<title>LLM Reviews</title>
<h1>Revisões de LLM</h1>
<ul>
{% for p in projects %}
  <li><a href="/reviews/{{ p }}">{{ p }}</a></li>
{% endfor %}
</ul>
"""

REVIEW_DETAIL_HTML = """<!doctype html>
<title>Review - {{ project }}</title>
<h1>Review - {{ project }}</h1>
{% if llm %}
  <h2>LLM Output</h2>
  <pre>{{ llm }}</pre>
  <form method="post" action="/reviews/{{ project }}/approve">
    <button type="submit">Aprovar e integrar</button>
  </form>
  <form method="post" action="/reviews/{{ project }}/dismiss"
      onsubmit="return confirm('Descartar snippet?');">
    <button type="submit">Descartar</button>
  </form>
{% else %}
  <p>Nenhum output LLM encontrado.</p>
{% endif %}
{% if diff %}
  <h2>Diff</h2>
  <pre>{{ diff }}</pre>
{% endif %}
<p><a href="/reviews">Voltar</a></p>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    project_path = None
    llm_output = None

    if request.method == "POST":
        name = request.form.get("name")
        mode = request.form.get("mode", "minimal")
        framework = request.form.get("framework", "flask")
        use_llm = bool(request.form.get("use_llm"))
        dry_run = bool(request.form.get("dry_run"))
        prompt = request.form.get("prompt", "").strip()

        target = Path.cwd() / "generated"
        target.mkdir(exist_ok=True)
        project_dir = create_project(name, target, mode=mode, framework=framework)
        project_path = str(project_dir)

        if use_llm:
            # call the LLM module (it will return an informative message if not configured)
            try:
                result = llm_module.generate_code_from_prompt(
                    prompt or f"Gerar código para projeto {name}"
                )
            except Exception as e:
                result = f"# Erro gerando via LLM: {e}"

            # save output to a file inside the project for inspection
            try:
                (project_dir / "llm_generated.txt").write_text(result)
            except Exception:
                pass

            # integrate only if not dry_run
            integrated = False
            if not dry_run:
                try:
                    integrated = llm_module.integrate_snippet(
                        project_dir, framework, result
                    )
                    if integrated:
                        result = (
                            result + "\n\n[LLM snippet integrated into project files]"
                        )
                except Exception:
                    integrated = False
            llm_output = result

    return render_template_string(
        INDEX_HTML, project_path=project_path, llm_output=llm_output
    )


@app.route("/reviews")
def reviews():
    base = Path.cwd() / "generated"
    projects = []
    if base.exists():
        for p in base.iterdir():
            if p.is_dir():
                projects.append(p.name)
    return render_template_string(REVIEWS_HTML, projects=projects)


@app.route("/reviews/<project>")
def review_detail(project):
    base = Path.cwd() / "generated" / project
    llm_text = None
    diff_text = None
    if base.exists():
        llm_file = base / "llm_generated.txt"
        if llm_file.exists():
            llm_text = llm_file.read_text()
        # check for pending snippet
        pending_file = base / "llm_pending.txt"
        if pending_file.exists():
            llm_text = pending_file.read_text()
        # attempt to find backups and show diffs
        backup_dir = base / "llm_backup"
        if backup_dir.exists():
            diffs = []
            for b in backup_dir.iterdir():
                orig = base / b.name
                if orig.exists():
                    before = b.read_text().splitlines(keepends=True)
                    after = orig.read_text().splitlines(keepends=True)
                    ud = difflib.unified_diff(
                        before, after, fromfile=str(b), tofile=str(orig)
                    )
                    diffs.extend(list(ud))
            if diffs:
                diff_text = "".join(diffs)
    return render_template_string(
        REVIEW_DETAIL_HTML, project=project, llm=llm_text, diff=diff_text
    )


@app.route("/reviews/<project>/approve", methods=["POST"])
def review_approve(project):
    base = Path.cwd() / "generated" / project
    # require token if configured
    token = os.environ.get("GENAUTH_TOKEN")
    if token:
        form_token = request.form.get("auth_token")
        if not form_token or form_token != token:
            return "Unauthorized", 401
    # attempt to approve pending
    try:
        ok = llm_module.approve_pending(base, _detect_framework(base))
        if ok:
            return redirect(url_for("review_detail", project=project))
    except Exception:
        pass
    return redirect(url_for("review_detail", project=project))


@app.route("/reviews/<project>/dismiss", methods=["POST"])
def review_dismiss(project):
    base = Path.cwd() / "generated" / project
    # require token if configured
    token = os.environ.get("GENAUTH_TOKEN")
    if token:
        form_token = request.form.get("auth_token")
        if not form_token or form_token != token:
            return "Unauthorized", 401
    pending = base / "llm_pending.txt"
    if pending.exists():
        try:
            pending.unlink()
            llm_module._write_log(base, ["Pending snippet dismissed via UI"])  # type: ignore
        except Exception:
            pass
    return redirect(url_for("review_detail", project=project))


def _detect_framework(project_path: Path) -> str:
    # naive detection by file presence
    p = Path(project_path)
    if (p / "app.py").exists():
        # could be flask
        return "flask"
    if (p / "main.py").exists():
        return "fastapi"
    if (p / "index.js").exists():
        return "express"
    return "flask"


def main() -> int:
    # roda a UI em debug local
    app.run(debug=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
