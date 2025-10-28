# Contributing

Obrigado por querer contribuir! Algumas diretrizes rápidas:

- Use o venv local e rode `black` / `isort` antes de abrir PR.
- Rode os testes: `python -m unittest discover -s tests -v`.
- Siga o estilo (flake8) e tipos (mypy). Veja `dev-requirements.txt`.
- Para mudanças que afetem templates ou integração LLM, adicione testes cobrindo o fluxo.

Processo
1. Crie uma branch com nome descritivo.
2. Faça mudanças pequenas e atômicas.
3. Rode formatação e testes localmente.
4. Abra um Pull Request com descrição do que mudou e porquê.

Não faça push direto para `main` sem revisão.
