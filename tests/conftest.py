from __future__ import annotations

import pytest

from app.app import create_app
from app.db import db
from app.models import Usuario


@pytest.fixture
def app(tmp_path):
    db_file = tmp_path / "test.db"
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_file.as_posix()}",
            "SECRET_KEY": "test-secret",
            "MAIL_SUPPRESS_SEND": True,
        }
    )
    with application.app_context():
        user = Usuario(
            nome="Tester",
            login="tester",
            senha="secret",
            situacao="ATIVO",
            email="tester@example.com",
        )
        db.session.add(user)
        db.session.commit()

    application.config["_mail_outbox"] = []
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(client, app):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    return client
