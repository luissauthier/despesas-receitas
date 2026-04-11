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
- **Geração de PDF**: ReportLab
- **Testes**: Pytest

### Estrutura do projeto

Classes de domínio (models):

- `Usuario` (agora com campo `email`)
- `Lancamento`

Arquivos principais e novos módulos:

- `app/models.py`: models SQLAlchemy (`Usuario`, `Lancamento`)
- `app/app.py`: criação da aplicação Flask e rotas
- `app/email_service.py`: integração para envio de e-mails e notificações
- `app/pdf_export.py`: lógica de geração do relatório PDF usando ReportLab
- `app/lancamentos_filters.py`: lógica de filtros refinados e cálculo de KPIs
- `app/templates/`: interfaces HTML (listagem, formulários, login)
- `app/seed.sql`: script SQL de carga inicial
- `tests/`: suíte de testes automatizados
- `run.py`: ponto de entrada

### Modelagem do banco de dados

Tabela `lancamento`:

- **id** (INTEGER, PK)
- **descricao** (TEXT/VARCHAR, NOT NULL)
- **data_lancamento** (DATE, NOT NULL)
- **valor** (NUMERIC(12,2), NOT NULL)
- **tipo_lancamento** (VARCHAR, NOT NULL) — valores esperados: `RECEITA` | `DESPESA`
- **situacao** (VARCHAR, NOT NULL) — valores esperados: `PAGO` | `EM_ABERTO`

Tabela `usuario`:

- **id** (INTEGER, PK)
- **nome** (VARCHAR, NOT NULL)
- **login** (VARCHAR, NOT NULL, UNIQUE)
- **email** (VARCHAR) — novo campo para notificações
- **senha** (VARCHAR, NOT NULL)
- **situacao** (VARCHAR, NOT NULL) — ex.: `ATIVO`

### Carga inicial (seed)

- O seed está em `app/seed.sql` e cria:
  - **1 usuário**: `admin` / `admin123`
  - **10 lançamentos** (misturando `RECEITA` e `DESPESA`)
- Ao iniciar, se **não existir nenhum registro** em `lancamento`, a aplicação executa o `seed.sql`.
- Importante: em produção/VM, o banco fica em `instance/app.db`. Em atualizações da aplicação, o banco **não é recriado** (o seed não roda novamente se já houver dados).

### Interface desenvolvida

- **Tela**: login + gestão de lançamentos (listagem + CRUD)
- **Listagem e Relatórios**:
  - Tabela com `id`, `descrição`, `data`, `valor`, `tipo`, `situação` e ações.
  - **Exportação PDF**: Botão para gerar um relatório PDF dos lançamentos filtrados.
  - **Envio por E-mail**: Opção para enviar o relatório PDF diretamente para o e-mail do usuário ou outro destinatário informado.
- **Cadastro/edição/exclusão**:
  - formulário de lançamento com data, valor, tipo e situação
  - exclusão com confirmação
- **KPIs e filtros**:
  - Cards com **ganhos no período**, **gastos no período** e **saldo**.
  - Filtros por texto (descrição), data inicial/final, tipo e situação.
  - **Preservação de filtros**: Os filtros aplicados são mantidos ao navegar entre criação e edição.
- **Notificações**:
  - Disparo de e-mail automático ao criar ou atualizar um lançamento (se o e-mail do usuário estiver configurado).
- **Rotas**:
  - `GET /login` / `POST /login` / `POST /logout`
  - `GET /lancamentos` (listagem principal)
  - `GET /lancamentos/exportar-pdf` (gera e baixa o PDF)
  - `POST /lancamentos/enviar-pdf-email` (envia o PDF por e-mail)
  - `POST /lancamentos/salvar-email` (configura e-mail de notificação do usuário)
  - `GET /lancamentos/novo` / `POST /lancamentos/novo` (CRUD)
  - `GET /lancamentos/<id>/editar` / `POST /lancamentos/<id>/editar` (CRUD)
  - `POST /lancamentos/<id>/excluir` (CRUD)

## Testes Automatizados

A aplicação possui uma suíte de testes que cobre rotas HTTP, modelos, validação de formulários, geração de PDF e integração de e-mail.

### Como rodar os testes

Certifique-se de estar com o ambiente virtual ativo e as dependências instaladas:

```powershell
pytest
```

Para ver detalhes da execução (verbose):

```powershell
pytest -v
```

### O que é testado

- **Rotas e Autenticação**: Proteção de rotas, login/logout e acessibilidade das páginas de CRUD.
- **Formulários**: Validação de campos obrigatórios, tipos de dados (data, valor) e integridade dos inputs.
- **Exportação (PDF)**: Verificação se o arquivo PDF é gerado corretamente com os cabeçalhos esperados.
- **E-mail**: Mocking do serviço de e-mail para validar o disparo de notificações e envio de anexos.
- **Modelos e Filtros**: Consultas ao banco de dados, cálculos de KPIs (Ganhos, Gastos, Saldo) e aplicação correta de filtros de busca.

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

### Como atualizar a aplicação na VM (quando houver novos commits)

Quando você fizer `git push` para o repositório, atualize a VM assim:

```bash
ssh univates@177.44.248.12
cd ~/despesas-receitas
git pull
source .venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart despesas
sudo systemctl status despesas --no-pager
```

Se você alterou apenas HTML/CSS/Python e **não mudou** dependências, ainda é seguro rodar o `pip install -r requirements.txt` (ele só confirma o que já existe).

#### Ver logs (se der erro)

Aplicação (Gunicorn/systemd):

```bash
sudo journalctl -u despesas -n 200 --no-pager
```

Nginx:

```bash
sudo journalctl -u nginx -n 200 --no-pager
sudo nginx -t
```

#### Dica: não perder o banco em atualizações

- O SQLite fica em `~/despesas-receitas/instance/app.db`.
- Atualizar o código com `git pull` **não apaga** o banco.
- O seed (`app/seed.sql`) só roda se **não existir** nenhum registro em `lancamento`.

### URL de acesso

- `http://177.44.248.12/lancamentos`

## Passo 3 — Tempos (preencher)

Tempos aproximados gastos:

- **Desenvolvimento da aplicação**: 70 min
- **Criação do ambiente na VM** (instalações): 20 min
- **Publicação/implantação** (serviço + nginx + liberação de portas): 5 min

## Gerar PDF a partir deste Markdown (opcional)

Opção simples (local, usando Node + Markdown-PDF):

```bash
npm i -g markdown-pdf
markdown-pdf README.md -o DOCUMENTACAO.pdf
```

Alternativas:

- Colar o conteúdo no Google Docs/Word e exportar como PDF.

