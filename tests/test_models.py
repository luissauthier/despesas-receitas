"""Tipo: testes de modelo ORM."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.db import db
from app.models import Lancamento, Usuario


# Garante que as propriedades básicas do Usuário são persistidas corretamente no banco.
def test_usuario_persisted_fields(app):
    with app.app_context():
        u = Usuario.query.filter_by(login="tester").first()
        assert u is not None
        assert u.email == "tester@example.com"
        assert u.situacao == "ATIVO"


# Testa a inserção de um lançamento e valida a integridade do tipo Decimal para valores monetários.
def test_lancamento_insert_and_query(app):
    with app.app_context():
        l = Lancamento(
            descricao="Teste",
            data_lancamento=date(2026, 4, 1),
            valor=Decimal("10.50"),
            tipo_lancamento="DESPESA",
            situacao="PAGO",
        )
        db.session.add(l)
        db.session.commit()
        found = Lancamento.query.filter_by(descricao="Teste").first()
        assert found is not None
        assert found.valor == Decimal("10.50")
