"""Tipo: testes de rotas HTTP / API (cliente de teste do Flask)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.db import db
from app.models import Lancamento


def test_login_get_returns_200(client):
    res = client.get("/login")
    assert res.status_code == 200


def test_root_redirects_guest_to_login(client):
    res = client.get("/", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers.get("Location", "")


def test_lancamentos_requires_login(client):
    res = client.get("/lancamentos", follow_redirects=False)
    assert res.status_code == 302


def test_lancamentos_ok_when_authenticated(authenticated_client):
    res = authenticated_client.get("/lancamentos")
    assert res.status_code == 200


def test_login_post_sets_session_and_redirects(client, app):
    res = client.post(
        "/login",
        data={"login": "tester", "senha": "secret", "next": "/lancamentos"},
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert "/lancamentos" in res.headers.get("Location", "")


def test_create_lancamento_post_persists(authenticated_client, app):
    app.config["_mail_outbox"] = []
    res = authenticated_client.post(
        "/lancamentos/novo",
        data={
            "descricao": "Novo item HTTP",
            "data_lancamento": "2026-04-02",
            "valor": "55.00",
            "tipo_lancamento": "RECEITA",
            "situacao": "PAGO",
        },
        follow_redirects=False,
    )
    assert res.status_code == 302
    with app.app_context():
        row = Lancamento.query.filter_by(descricao="Novo item HTTP").first()
        assert row is not None


def test_create_lancamento_sends_notification_to_outbox(authenticated_client, app):
    app.config["_mail_outbox"] = []
    authenticated_client.post(
        "/lancamentos/novo",
        data={
            "descricao": "Com email",
            "data_lancamento": "2026-04-03",
            "valor": "10.00",
            "tipo_lancamento": "DESPESA",
            "situacao": "EM_ABERTO",
        },
        follow_redirects=True,
    )
    out = app.config.get("_mail_outbox", [])
    assert len(out) >= 1
    assert "tester@example.com" in out[-1]["to"]


def test_export_pdf_requires_login(client):
    res = client.get("/lancamentos/exportar-pdf", follow_redirects=False)
    assert res.status_code == 302


def test_export_pdf_returns_pdf_mime(authenticated_client):
    res = authenticated_client.get("/lancamentos/exportar-pdf")
    assert res.status_code == 200
    assert res.mimetype == "application/pdf"
    assert res.data[:4] == b"%PDF"


def test_delete_lancamento(authenticated_client, app):
    with app.app_context():
        l = Lancamento(
            descricao="Para excluir",
            data_lancamento=date(2026, 4, 5),
            valor=Decimal("1.00"),
            tipo_lancamento="DESPESA",
            situacao="PAGO",
        )
        db.session.add(l)
        db.session.commit()
        lid = l.id

    res = authenticated_client.post(f"/lancamentos/{lid}/excluir", follow_redirects=False)
    assert res.status_code == 302
    with app.app_context():
        assert db.session.get(Lancamento, lid) is None
