# Protótipo: Registro de Despesas e Receitas

Aplicação simples para cumprir os requisitos do trabalho (tabelas `lancamento` e `usuario`, carga inicial e tela de listagem de lançamentos).

## Entrega (links e credenciais)

- **Repositório**: https://github.com/luissauthier/despesas-receitas
- **URL pública (VM)**: `http://177.44.248.12/lancamentos`
- **Credenciais (seed)**:
  - **Usuário**: `admin`
  - **Senha**: `admin123`

## Passo 1 — Aplicação

### Stack

- **Linguagem**: Python 3
- **Framework web**: Flask
- **Banco de dados**: SQLite
- **ORM**: SQLAlchemy (via Flask-SQLAlchemy)

### Número de classes da aplicação

Classes de domínio (models):

- `Usuario`
- `Lancamento`

Arquivos principais:

- `app/models.py`: models SQLAlchemy (`Usuario`, `Lancamento`)
- `app/app.py`: criação da aplicação Flask e rota de listagem (`/lancamentos`)
- `app/templates/lancamentos.html`: interface HTML da listagem
- `app/seed.sql`: script SQL de carga inicial
- `run.py`: ponto de entrada

### Modelagem do banco de dados

Tabela `lancamento`:

- **id** (INTEGER, PK)
- **descricao** (TEXT/VARCHAR, NOT NULL)
- **data_lancamento** (DATE, NOT NULL)
- **valor** (NUMERIC(12,2), NOT NULL)
- **tipo_lancamento** (VARCHAR, NOT NULL) — valores esperados: `RECEITA` | `DESPESA`
- **situacao** (VARCHAR, NOT NULL) — ex.: `ATIVO`

Tabela `usuario`:

- **id** (INTEGER, PK)
- **nome** (VARCHAR, NOT NULL)
- **login** (VARCHAR, NOT NULL, UNIQUE)
- **senha** (VARCHAR, NOT NULL)
- **situacao** (VARCHAR, NOT NULL) — ex.: `ATIVO`

### Carga inicial (seed)

- O seed está em `app/seed.sql` e cria:
  - **1 usuário**: `admin` / `admin123`
  - **10 lançamentos** (misturando `RECEITA` e `DESPESA`)
- Ao iniciar, se **não existir nenhum registro** em `lancamento`, a aplicação executa o `seed.sql`.

### Interface desenvolvida

- **Tela**: login + listagem de lançamentos cadastrados
- **Rotas**:
  - `GET /login` (formulário)
  - `POST /login` (autenticação)
  - `POST /logout` (encerrar sessão)
  - `GET /lancamentos` (listagem, protegida por login)
- **O que exibe**: tabela com `id`, `descrição`, `data`, `valor`, `tipo` e `situação`

## Como rodar (local)

```powershell
cd .\despesas-receitas
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Acesse `http://localhost:5000/lancamentos`.

## Passo 2 — Publicação (VM)

### Como acessar a VM

Exemplo (substitua usuário e IP conforme sua VM):

```bash
ssh univates@177.44.248.12
```

### Instalação das ferramentas (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip nginx
```

### Implantação da aplicação

#### 1) Clonar o repositório na VM

```bash
cd ~
git clone <URL_DO_SEU_REPO_GITHUB>
cd despesas-receitas
```

#### 2) Criar ambiente virtual e instalar dependências

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### 3) Criar serviço systemd (Gunicorn)

Crie o arquivo:

```bash
sudo nano /etc/systemd/system/despesas.service
```

Conteúdo (ajuste `User` e `WorkingDirectory` se necessário):

```ini
[Unit]
Description=Despesas/Receitas (Flask + Gunicorn)
After=network.target

[Service]
User=univates
WorkingDirectory=/home/univates/despesas-receitas
ExecStart=/home/univates/despesas-receitas/.venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now despesas
sudo systemctl status despesas --no-pager
```

#### 4) Configurar Nginx como proxy reverso (porta 80)

```bash
sudo nano /etc/nginx/sites-available/despesas
```

Conteúdo:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Habilitar e reiniciar:

```bash
sudo ln -sf /etc/nginx/sites-available/despesas /etc/nginx/sites-enabled/despesas
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### 5) Liberar firewall (se estiver ativo)

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status verbose || true
```

### URL de acesso

- `http://177.44.248.12/lancamentos`

## Passo 3 — Tempos (preencher)

Preencha com os tempos reais gastos:

- **Desenvolvimento da aplicação**: ___ min
- **Criação do ambiente na VM** (instalações): ___ min
- **Publicação/implantação** (serviço + nginx + liberação de portas): ___ min

## Gerar PDF a partir deste Markdown (opcional)

Opção simples (local, usando Node + Markdown-PDF):

```bash
npm i -g markdown-pdf
markdown-pdf README.md -o DOCUMENTACAO.pdf
```

Alternativas:

- Colar o conteúdo no Google Docs/Word e exportar como PDF.

