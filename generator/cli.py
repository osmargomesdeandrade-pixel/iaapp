"""CLI simples para o gerador de apps.

Uso:
  python -m generator.cli --name myapp --mode full
  python -m generator.cli --name myapp --mode minimal

Se nenhum argumento for passado, o CLI fará perguntas interativas.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .generate import create_project


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Gerador de esqueleto de apps (Flask)")
    p.add_argument("--name", "-n", help="Nome do projeto a gerar")
    p.add_argument(
        "--mode",
        "-m",
        choices=("minimal", "full"),
        default="minimal",
        help="Modo de template (minimal ou full)",
    )
    p.add_argument(
        "--framework",
        "-f",
        choices=("flask", "express"),
        default="flask",
        help="Framework alvo (flask ou express)",
    )
    p.add_argument(
        "--port",
        "-p",
        type=int,
        default=5000,
        help="Porta padrão para o app gerado (apenas informativa)",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help="Habilitar modo debug na geração (apenas flag)",
    )
    p.add_argument("--author", help="Nome do autor para inserir nos templates")
    p.add_argument("--license", help="Licença do projeto (ex: MIT)")
    p.add_argument("--description", help="Breve descrição do projeto")
    p.add_argument("--out", "-o", default="generated", help="Diretório de saída")
    p.add_argument(
        "--batch", "-b", help="Arquivo JSON com lista de projetos para gerar (batch)"
    )
    p.add_argument(
        "--use-llm",
        action="store_true",
        help="Usar LLM para gerar snippet e integrá-lo ao projeto (se chave disponível)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Somente gerar o snippet via LLM e salvar (não integrar)",
    )
    p.add_argument(
        "--llm-prompt", help="Prompt a ser passado ao LLM se --use-llm for usado"
    )
    p.add_argument(
        "--approve-all",
        action="store_true",
        help="Aprovar todos os snippets pendentes em 'generated' (aplica approve_pending em todos)",
    )
    p.add_argument(
        "--approve",
        help="Aprovar o snippet pendente para um projeto específico (nome de pasta em generated)",
    )
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if not args.name:
        # interação simples
        name = input("Nome do projeto (ex: my_flask_app): ").strip()
        if not name:
            print("Nome inválido. Saindo.")
            return 1
        args.name = name

    target = Path.cwd() / args.out
    target.mkdir(exist_ok=True)

    # batch mode
    if args.batch:
        import json

        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"Arquivo de batch não encontrado: {batch_path}")
            return 1
        data = json.loads(batch_path.read_text())
        if not isinstance(data, list):
            print("Arquivo de batch deve conter uma lista de projetos")
            return 1
        for item in data:
            name = item.get("name")
            mode = item.get("mode", "minimal")
            framework = item.get("framework", args.framework)
            outdir = Path(item.get("out", args.out))
            outdir = Path.cwd() / outdir
            outdir.mkdir(parents=True, exist_ok=True)
            author = item.get("author") or args.author
            license = item.get("license") or args.license
            description = item.get("description") or args.description
            project_dir = create_project(
                name,
                outdir,
                mode=mode,
                framework=framework,
                author=author,
                license=license,
                description=description,
            )
            # LLM integration for batch items
            use_llm_item = item.get("use_llm", False) or args.use_llm
            prompt_item = item.get("llm_prompt") or args.llm_prompt
            if use_llm_item:
                try:
                    from . import llm as _llm

                    prompt_text = (
                        prompt_item
                        or f"Gerar snippet para projeto {name} ({framework})"
                    )
                    snippet = _llm.generate_code_from_prompt(prompt_text)
                    # if dry-run requested for batch item, only save snippet
                    if item.get("dry_run", False) or args.dry_run:
                        try:
                            (project_dir / "llm_generated.txt").write_text(snippet)
                        except Exception:
                            pass
                    else:
                        _llm.integrate_snippet(project_dir, framework, snippet)
                except Exception:
                    pass
        return 0

    project_dir = create_project(
        args.name,
        target,
        mode=args.mode,
        framework=args.framework,
        author=args.author,
        license=args.license,
        description=args.description,
    )
    if args.use_llm:
        try:
            from . import llm as _llm

            prompt = (
                args.llm_prompt
                or f"Gerar snippet para projeto {args.name} ({args.framework})"
            )
            snippet = _llm.generate_code_from_prompt(prompt)
            if args.dry_run:
                try:
                    (project_dir / "llm_generated.txt").write_text(snippet)
                except Exception:
                    pass
            else:
                _llm.integrate_snippet(project_dir, args.framework, snippet)
        except Exception:
            pass
    # approval actions
    if args.approve:
        try:
            from . import llm as _llm

            ok = _llm.approve_pending(Path(target) / args.approve, args.framework)
            if ok:
                print(f"Aprovado pending para: {args.approve}")
        except Exception:
            pass
    if args.approve_all:
        try:
            from . import llm as _llm

            base = Path.cwd() / args.out
            if base.exists():
                for p in base.iterdir():
                    if p.is_dir():
                        _llm.approve_pending(p, "flask")
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
