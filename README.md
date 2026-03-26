# Protótipo: Registro de Despesas e Receitas

Aplicação simples para cumprir os requisitos do trabalho (tabelas `lancamento` e `usuario`, carga inicial e tela de listagem de lançamentos).

## Como rodar (local)

```powershell
cd .\despesas-receitas-prototipo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Acesse `http://localhost:5000/lancamentos`.

## Carga inicial (seed)

Ao iniciar, se não existir nenhum registro em `lancamento`, a aplicação executa o script `app/seed.sql`.

