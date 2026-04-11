"""Tipo: geração de PDF."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.models import Lancamento
from app.pdf_export import build_lancamentos_pdf


def test_pdf_starts_with_pdf_magic():
    pdf = build_lancamentos_pdf([], receitas=0, despesas=0, saldo=0)
    assert pdf[:4] == b"%PDF"


def test_pdf_non_empty_with_rows():
    l = Lancamento(
        descricao="Supermercado",
        data_lancamento=date(2026, 1, 15),
        valor=Decimal("12.34"),
        tipo_lancamento="RECEITA",
        situacao="PAGO",
    )
    pdf = build_lancamentos_pdf([l])
    assert len(pdf) > 400
    assert pdf.startswith(b"%PDF")
