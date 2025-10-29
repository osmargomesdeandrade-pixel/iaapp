"""Gerador simples de esqueleto de app Flask.

Este script não depende de bibliotecas externas — usa apenas a stdlib.
Ele cria uma pasta em `generated/<project_name>` com um `app.py` minimal,
`requirements.txt` e `README.md` para executar o app.

Uso:
  python generator/generate.py

O script pergunta o nome do projeto e gera os arquivos.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

APP_PY_TEMPLATE = """from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
     return "Hello from {project_name}!"

if __name__ == '__main__':
     app.run(debug=True, host='127.0.0.1', port=5000)
"""

README_TEMPLATE = """# {project_name}

Pequeno app Flask gerado automaticamente.

Como executar:

1. (Opcional) crie e ative um venv:

    python -m venv venv
    # Windows (PowerShell)
    venv\\Scripts\\Activate.ps1

2. Instale dependências:

    pip install -r requirements.txt

3. Execute:

    python app.py

Abra http://127.0.0.1:5000 no navegador.
"""

REQUIREMENTS = "Flask>=2.0"

GITIGNORE = """__pycache__/
venv/
*.pyc
.env
"""

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def copy_tree(src: Path, dst: Path, context: dict | None = None) -> None:
    """Copy files from src to dst (similar to distutils.dir_util.copy_tree but simple).

    Preserva subfolders. Overwrites existing files if present.
    """
    # no local alias required here
    # local alias for Jinja2 Template if available
    _JINJA_TEMPLATE: Any = None
    try:
        from jinja2 import Template as _JINJA_TEMPLATE  # type: ignore
    except Exception:
        _JINJA_TEMPLATE = None

    for p in src.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        # try to render text files with Jinja2 if available
        try:
            data = p.read_bytes()
            text_like = True
            try:
                data_text = data.decode("utf-8")
            except Exception:
                text_like = False
            if text_like and _JINJA_TEMPLATE and context:
                rendered = _JINJA_TEMPLATE(data_text).render(**context)
                target.write_text(rendered)
            else:
                target.write_bytes(data)
        except Exception:
            # fallback binary copy
            target.write_bytes(p.read_bytes())


def create_project(
    project_name: str,
    target_dir: Path,
    mode: str = "minimal",
    framework: str = "flask",
    author: str | None = None,
    license: str | None = None,
    description: str | None = None,
) -> Path:
    project_dir = target_dir / project_name
    if project_dir.exists():
        print(f"Pasta {project_dir} já existe. Abortando para evitar sobrescrita.")
        return project_dir

    project_dir.mkdir(parents=True)

    if mode == "full":
        template_name = f"{framework}_full"
        template_path = TEMPLATES_DIR / template_name
        if not template_path.exists():
            print(f"Template '{template_name}' não encontrado. Abortando.")
            return project_dir
        context = {
            "project_name": project_name,
            "author": author or "",
            "license": license or "",
            "description": description or "",
        }
        copy_tree(template_path, project_dir, context=context)
    else:
        # minimal
        (project_dir / "app.py").write_text(
            APP_PY_TEMPLATE.format(project_name=project_name)
        )
        (project_dir / "requirements.txt").write_text(REQUIREMENTS + "\n")
        # render README with placeholders
        readme_text = README_TEMPLATE.format(project_name=project_name)
        if author:
            readme_text = readme_text + f"\nAuthor: {author}\n"
        if license:
            readme_text = readme_text + f"License: {license}\n"
        if description:
            readme_text = readme_text + f"\n{description}\n"
        (project_dir / "README.md").write_text(readme_text)
        (project_dir / ".gitignore").write_text(GITIGNORE)

    print(f"Projeto gerado em: {project_dir}")
    return project_dir


def main() -> int:
    print("Gerador de app Flask (simples)")
    project_name = input("Nome do projeto (ex: my_flask_app): ").strip()
    if not project_name:
        print("Nome inválido. Saindo.")
        return 1
    cwd = Path.cwd()
    generated_dir = cwd / "generated"
    generated_dir.mkdir(exist_ok=True)
    create_project(project_name, generated_dir)
    print("Feito. Veja a pasta 'generated' no workspace.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
