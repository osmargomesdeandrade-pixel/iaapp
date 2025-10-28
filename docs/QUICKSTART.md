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
