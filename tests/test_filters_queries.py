"""Tipo: consultas e filtros no banco (SQLAlchemy)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.db import db
from app.lancamentos_filters import build_lancamentos_query, kpis_for_query
from app.models import Lancamento


def _seed_lancamentos(app):
    with app.app_context():
        rows = [
            Lancamento(
                descricao="A",
                data_lancamento=date(2026, 4, 1),
                valor=Decimal("100"),
                tipo_lancamento="RECEITA",
                situacao="PAGO",
            ),
            Lancamento(
                descricao="B",
                data_lancamento=date(2026, 4, 10),
                valor=Decimal("40"),
                tipo_lancamento="DESPESA",
                situacao="EM_ABERTO",
            ),
        ]
        db.session.add_all(rows)
        db.session.commit()


def test_filter_by_situacao(app):
    _seed_lancamentos(app)
    with app.app_context():
        query, filtros, flashes = build_lancamentos_query({"situacao": "EM_ABERTO"})
        assert flashes == []
        items = query.all()
        assert len(items) == 1
        assert items[0].descricao == "B"


def test_filter_by_date_range(app):
    _seed_lancamentos(app)
    with app.app_context():
        query, _, _ = build_lancamentos_query({"de": "2026-04-05", "ate": "2026-04-30"})
        items = query.all()
        assert len(items) == 1
        assert items[0].descricao == "B"


def test_kpis_reflect_filtered_rows(app):
    _seed_lancamentos(app)
    with app.app_context():
        query, _, _ = build_lancamentos_query({"tipo": "RECEITA"})
        k = kpis_for_query(query)
        assert float(k["receitas"]) == 100.0
        assert float(k["despesas"]) == 0.0


def test_invalid_date_filter_yields_flash_message(app):
    with app.app_context():
        _, _, flashes = build_lancamentos_query({"de": "not-a-date"})
        assert any("de" in m for _, m in flashes)
