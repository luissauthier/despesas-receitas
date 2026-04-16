# Documentação Técnica: PDF, E-mail e Testes

Este documento descreve as implementações das funcionalidades de exportação de relatórios em PDF, notificações via e-mail e a estratégia de automação de testes utilizada para validar esses serviços.

---

## 1. Exportação de PDF
A funcionalidade de geração de PDF permite que o usuário exporte seus lançamentos financeiros de forma organizada e profissional.

- **Tecnologia**: [ReportLab](https://www.reportlab.com/) (biblioteca Python para geração de PDFs).
- **Localização**: `app/pdf_export.py`.
- **Funcionamento**:
    - A função `build_lancamentos_pdf` recebe uma lista de objetos `Lancamento` e metadados (totais de receita, despesa e saldo).
    - Utiliza um objeto `BytesIO` para gerar o arquivo na memória, evitando a criação de arquivos temporários no disco.
    - Desenha uma tabela com cabeçalhos fixos e formata valores decimais para o padrão monetário.
    - Suporta quebra automática de páginas caso a lista de lançamentos exceda o limite vertical da folha A4.

---

## 2. Serviço de E-mail e Notificações
O sistema envia notificações automáticas e permite o envio de relatórios via e-mail.

- **Tecnologia**: Biblioteca nativa do Python `smtplib` e `email.message`.
- **Localização**: `app/email_service.py`.
- **Recursos**:
    - **Notificação de Eventos**: Disparada automaticamente ao criar ou atualizar um lançamento através da função `notify_lancamento_event`.
    - **Envio de Relatórios**: Permite anexar o PDF gerado diretamente em uma mensagem através da função `send_email_with_pdf`.
- **Configuração**:
    As configurações são extraídas do `app.config` (variáveis de ambiente no servidor):
    - `MAIL_SERVER` (ex: smtp.gmail.com)
    - `MAIL_PORT` (ex: 587)
    - `MAIL_USE_TLS` (True/False)
    - `MAIL_USERNAME` e `MAIL_PASSWORD`

---

## 3. Estratégia de Testes Automatizados
Dado que serviços externos (SMTP) e geração de arquivos binários (PDF) podem ser complexos de testar, adotamos as seguintes abordagens em `tests/`:

## 3. Estratégia de Testes Automatizados
A suíte de testes do projeto foi projetada para garantir a confiabilidade de todas as camadas da aplicação, desde a persistência de dados até a interface do usuário.

- **Infraestrutura**: Utilizamos [pytest](https://docs.pytest.org/).
- **Isolamento**: Cada teste é executado em um banco de dados **SQLite temporário** (criado via fixture no `conftest.py`), garantindo que não haja poluição de dados entre os testes e que o ambiente de produção permaneça intacto.

### 3.1. Categorias de Testes Implementados

#### A. Infraestrutura e Banco de Dados (`test_db_*.py`)
- **Conexão**: Valida se a aplicação consegue se comunicar com o banco de dados configurado.
- **Integridade do Esquema**: Garante que as tabelas de `Usuario` e `Lancamento` possuam todos os campos obrigatórios e tipos de dados corretos antes da aplicação subir.

#### B. Regras de Negócio e Modelos (`test_models.py`)
- Verifica a lógica interna das classes do banco de dados, como a criação de usuários e a correta atribuição de atributos aos lançamentos.

#### C. Validação de Formulários (`test_form_validation.py`)
- Testa a lógica de limpeza e validação de dados recebidos da interface (unitário, sem necessidade de servidor HTTP).
- **Cenários**: Rejeição de descrições vazias, bloqueio de valores negativos ou iguais a zero, e validação de enums (Tipo e Situação).

#### D. Consultas, Filtros e KPIs (`test_filters_queries.py`)
- Garante que o motor de busca do sistema funcione com precisão matemática.
- **Busca por Período**: Filtra lançamentos entre datas específicas.
- **Filtros por Estado**: Separa corretamente itens "Pagos" de itens "Em Aberto".
- **Cálculo de KPIs**: Valida se as somas de Receitas, Despesas e Saldo exibidas no dashboard refletem exatamente os registros filtrados na tela.

#### E. Navegação e Segurança HTTP (`test_http_routes.py`)
- Simula um navegador real fazendo requisições ao servidor.
- **Segurança**: Verifica se rotas restritas redirecionam usuários não autenticados para a página de login (Status 302).
- **CRUD**: Simula o fluxo completo de preenchimento de formulário, envio (POST) e redirecionamento após o sucesso, conferindo se o dado foi de fato persistido no banco.

#### F. Exportação de PDF e Mocks de E-mail
- **PDF**: Validamos o MIME-Type (`application/pdf`) e a assinatura binária do arquivo (`%PDF-`).
- **E-mail (Mocks)**: Usamos a flag `MAIL_SUPPRESS_SEND = True` para interceptar disparos de e-mail em uma fila na memória (`_mail_outbox`), permitindo conferir se o destinatário e o conteúdo da mensagem estão corretos sem enviar spam para caixas reais.

---

## 4. Como Executar os Testes
Para rodar todos os testes e ver o relatório de sucesso:

```bash
# Certifique-se de estar com o ambiente virtual (.venv) ativo
pytest -v
```
