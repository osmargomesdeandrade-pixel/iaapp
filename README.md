# AI App Generator (MVP)

Este repositório contém um gerador de esqueleços de aplicações (Flask, Express, FastAPI, React) com integração opcional a LLMs e um fluxo seguro de revisão.

Requisitos mínimos
- Python 3.10/3.11 (venv recomendado)

Configuração (Windows PowerShell)

```powershell
# criar e ativar venv
python -m venv .\venv
.\venv\Scripts\Activate.ps1

# instalar dependências principais
python -m pip install -r requirements.txt

# instalar dependências de desenvolvimento (opcional)
python -m pip install -r dev-requirements.txt
```

Variáveis de ambiente úteis
- `OPENAI_API_KEY` — se definido, o gerador pode chamar a API OpenAI para expandir trechos de código.
- `GENAUTH_TOKEN` — token simples para proteger endpoints de aprovação na UI (opcional).

Uso rápido
- CLI (gerar um app Flask full):

```powershell
python -m generator.cli --name myapp --mode full --framework flask
```

- CLI com LLM (dry-run):

```powershell
python -m generator.cli --name myapp --use-llm --llm-prompt "Crie um endpoint de login em Flask" --dry-run
```

- Rodar a UI do gerador (Flask):

```powershell
# opcional: defina OPENAI_API_KEY e GENAUTH_TOKEN
$env:OPENAI_API_KEY = ""
$env:GENAUTH_TOKEN = "seu_token"
python -m generator.ui
# abrir http://127.0.0.1:5000
```

Segurança e revisão de snippets LLM
- O sistema analisa automaticamente trechos gerados por LLM e marca como `pending` se detectar padrões arriscados (exec/eval/subprocess/import dinâmico).
- Snippets pendentes são gravados em `llm_pending.txt` no projeto gerado e devem ser revisados/aprovados via UI ou CLI (`approve_pending`).
- Integração automática faz backup em `llm_backup/` e grava logs em `llm_integration.log`.

Desenvolvimento e qualidade
- Instale `dev-requirements.txt` para rodar `flake8` e `mypy`.
- O CI roda os testes unitários (configurado em `.github/workflows/ci.yml`).

Próximos passos
- Melhorar análise por AST (já implementada nesta versão).
- Polir README com exemplos reais de prompts e mais templates (mobile/Django).

Contribuição
- Abra issues ou PRs com melhorias. Não faça push diretamente sem conversar antes se este repositório for privado.

Exemplos de prompts úteis para LLM
-- Gerar rota simples (Flask):

```
Crie uma rota Flask chamada /login que aceite POST com 'username' e 'password' em JSON, valide contra um dicionário em memória e retorne JSON com sucesso/erro.
```

-- Gerar CRUD básico (FastAPI):

```
Crie endpoints REST CRUD para um recurso 'note' com campos id:int, title:str, body:str usando FastAPI e uma lista em memória como armazenamento.
```

-- Gerar endpoint com autenticação JWT (Express):

```
No template Express, adicione rotas /auth/login que aceitem credenciais e retornem um JWT assinado (use uma chave em memória para teste) e uma rota /me protegida por middleware que valide o token.
```

-- Gerar testes simples (pytest):

```
Gere um arquivo de testes pytest que verifique o endpoint /hello responde 200 e contém a chave 'message' no JSON.
```

-- Refatorar para handlers (Safe integration):

```
Gere apenas o snippet de um handler que exporta uma função register(app) para Flask, sem modificar arquivos existentes; o snippet deve apenas definir rotas e funções auxiliares locais.
```

Notas sobre prompts
- Peça ao LLM para não usar exec/eval e evitar chamadas shell. Use prompts que pedem funções puras e handlers encapsulados — o gerador aplicará análise e marcará snippets arriscados como 'pending'.
