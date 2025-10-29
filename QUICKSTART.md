# QUICKSTART

Este é um guia rápido para começar com o gerador de aplicações.

Requisitos
- Python 3.10/3.11
- (Opcional) `OPENAI_API_KEY` para integração LLM

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

Uso rápido

- Gerar app Flask (mode full):

```powershell
python -m generator.cli --name myapp --mode full --framework flask
```

- Rodar UI local (http://127.0.0.1:5000):

```powershell
# opcional: defina OPENAI_API_KEY e GENAUTH_TOKEN
$env:OPENAI_API_KEY = ""
$env:GENAUTH_TOKEN = "seu_token"
python -m generator.ui
```

Segurança LLM

O sistema marca snippets suspeitos como `pending` e grava em `llm_pending.txt` para revisão.

Para aprová-los via CLI:

```powershell
python -m generator.llm approve_pending --project myapp
```
# Quickstart

1. Crie e ative um venv (Windows PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Instale dependências básicas:

```powershell
pip install -r requirements.txt
pip install -r dev-requirements.txt  # opcional para linters
```

3. Inicie a UI localmente:

```powershell
& "./venv/Scripts/python.exe" -m generator.ui
```

4. Acesse: http://127.0.0.1:5000
