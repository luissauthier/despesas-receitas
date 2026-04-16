from __future__ import annotations

import pytest

from app.app import create_app
from app.db import db
from app.models import Usuario


# Fixture principal que configura a aplicação em modo de teste.
# Cria um banco de dados SQLite temporário para isolar os dados de cada execução.
@pytest.fixture
def app(tmp_path):
    db_file = tmp_path / "test.db"
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_file.as_posix()}",
            "SECRET_KEY": "test-secret",
            # MAIL_SUPPRESS_SEND evita disparos reais de e-mail durante a suíte de testes.
            "MAIL_SUPPRESS_SEND": True,
        }
    )
    with application.app_context():
        # Cria um usuário padrão para facilitar testes que exigem autenticação.
        user = Usuario(
            nome="Tester",
            login="tester",
            senha="secret",
            situacao="ATIVO",
            email="tester@example.com",
        )
        db.session.add(user)
        db.session.commit()

    # Inicializa a caixa de saída em memória (mock) para inspeção nos testes.
    application.config["_mail_outbox"] = []
    yield application


# Fixture para simular um cliente HTTP (navegador).
@pytest.fixture
def client(app):
    return app.test_client()


# Fixture que injeta uma sessão autenticada, permitindo testar rotas protegidas.
@pytest.fixture
def authenticated_client(client, app):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    return client
