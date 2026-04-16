"""Tipo: validação de dados de formulário (unitário, sem HTTP)."""

from __future__ import annotations

from datetime import date

from app.lancamento_form import parse_lancamento_form


# Testa o parsing de um formulário preenchido corretamente.
# Valida a conversão de strings para tipos Python (date e Decimal).
def test_parse_valid_form():
    form = {
        "descricao": "Conta de luz",
        "data_lancamento": "2026-04-01",
        "valor": "99.90",
        "tipo_lancamento": "DESPESA",
        "situacao": "PAGO",
    }
    errors, cleaned, parsed_date, parsed_valor, tipo, situacao = parse_lancamento_form(form)
    assert errors == []
    assert parsed_date == date(2026, 4, 1)
    assert str(parsed_valor) == "99.90"
    assert tipo == "DESPESA"
    assert situacao == "PAGO"


def test_parse_rejects_empty_descricao():
    form = {
        "descricao": "",
        "data_lancamento": "2026-04-01",
        "valor": "10",
        "tipo_lancamento": "RECEITA",
        "situacao": "EM_ABERTO",
    }
    errors, *_ = parse_lancamento_form(form)
    assert any("Descrição" in e for e in errors)


# Valida se o sistema rejeita valores negativos ou iguais a zero, conforme regra de negócio.
def test_parse_rejects_non_positive_valor():
    form = {
        "descricao": "X",
        "data_lancamento": "2026-04-01",
        "valor": "0",
        "tipo_lancamento": "RECEITA",
        "situacao": "PAGO",
    }
    errors, *_ = parse_lancamento_form(form)
    assert any("maior que zero" in e for e in errors)


def test_parse_rejects_invalid_tipo():
    form = {
        "descricao": "X",
        "data_lancamento": "2026-04-01",
        "valor": "10",
        "tipo_lancamento": "XYZ",
        "situacao": "PAGO",
    }
    errors, *_ = parse_lancamento_form(form)
    assert any("RECEITA" in e for e in errors)


def test_parse_rejects_invalid_situacao():
    form = {
        "descricao": "X",
        "data_lancamento": "2026-04-01",
        "valor": "10",
        "tipo_lancamento": "RECEITA",
        "situacao": "INVALIDO",
    }
    errors, *_ = parse_lancamento_form(form)
    assert any("Situação" in e for e in errors)
