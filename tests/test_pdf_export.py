"""Tipo: geração de PDF."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.models import Lancamento
from app.pdf_export import build_lancamentos_pdf


# Verifica a "assinatura" do arquivo (Magic Number).
# Todo PDF válido deve começar com os bytes "%PDF".
def test_pdf_magic_number(app):
    pdf = build_lancamentos_pdf([], receitas=0, despesas=0, saldo=0)
    assert pdf[:4] == b"%PDF"


# Valida se a inclusão de dados reais no PDF gera um arquivo com conteúdo (tamanho maior que o cabeçalho mínimo).
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
