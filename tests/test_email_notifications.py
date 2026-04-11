"""Tipo: envio de e-mail (suprimido em teste, caixa de saída em memória)."""

from __future__ import annotations

from app.email_service import notify_lancamento_event, send_plaintext_email


def test_send_plaintext_with_suppress_populates_outbox(app):
    app.config["_mail_outbox"] = []
    with app.app_context():
        send_plaintext_email(app, ["a@b.com"], "Assunto", "Corpo")
    out = app.config.get("_mail_outbox", [])
    assert len(out) == 1
    assert out[0]["to"] == ["a@b.com"]
    assert out[0]["subject"] == "Assunto"


def test_notify_skips_when_no_email(app):
    app.config["_mail_outbox"] = []
    with app.app_context():
        notify_lancamento_event(
            app,
            None,
            event="create",
            descricao="X",
            data_str="2026-04-01",
            valor_str="1",
            tipo="RECEITA",
            situacao="PAGO",
        )
    assert app.config.get("_mail_outbox", []) == []


def test_notify_create_includes_subject_and_body(app):
    app.config["_mail_outbox"] = []
    with app.app_context():
        notify_lancamento_event(
            app,
            "user@example.com",
            event="create",
            descricao="Aluguel",
            data_str="2026-04-01",
            valor_str="500.00",
            tipo="DESPESA",
            situacao="PAGO",
        )
    out = app.config["_mail_outbox"]
    assert len(out) == 1
    assert "criado" in out[0]["subject"].lower()
    assert "Aluguel" in out[0]["body"]
