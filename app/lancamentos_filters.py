from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from decimal import Decimal

from sqlalchemy import func

from .models import Lancamento


def build_lancamentos_query(args: Mapping[str, str]) -> tuple[object, dict[str, str], list[tuple[str, str]]]:
    """
    Monta query filtrada e lista de (categoria, mensagem) para flash.
    Retorna (query, filtros, flashes).
    """
    q = (args.get("q") or "").strip()
    tipo = (args.get("tipo") or "").strip().upper()
    situacao = (args.get("situacao") or "").strip().upper()
    de = (args.get("de") or "").strip()
    ate = (args.get("ate") or "").strip()

    flashes: list[tuple[str, str]] = []
    query = Lancamento.query

    if q:
        query = query.filter(Lancamento.descricao.ilike(f"%{q}%"))
    if tipo in {"RECEITA", "DESPESA"}:
        query = query.filter(Lancamento.tipo_lancamento == tipo)
    if situacao in {"PAGO", "EM_ABERTO"}:
        query = query.filter(Lancamento.situacao == situacao)
    if de:
        try:
            query = query.filter(Lancamento.data_lancamento >= date.fromisoformat(de))
        except ValueError:
            flashes.append(("warning", "Filtro 'de' inválido."))
    if ate:
        try:
            query = query.filter(Lancamento.data_lancamento <= date.fromisoformat(ate))
        except ValueError:
            flashes.append(("warning", "Filtro 'até' inválido."))

    filtros = {"q": q, "tipo": tipo, "situacao": situacao, "de": de, "ate": ate}
    return query, filtros, flashes


def kpis_for_query(query) -> dict[str, Decimal]:
    """Totais de receita, despesa e saldo respeitando os mesmos filtros da listagem."""
    base = query.order_by(None)
    receita_total = (
        base.with_entities(func.coalesce(func.sum(Lancamento.valor), 0))
        .filter(Lancamento.tipo_lancamento == "RECEITA")
        .scalar()
    )
    despesa_total = (
        base.with_entities(func.coalesce(func.sum(Lancamento.valor), 0))
        .filter(Lancamento.tipo_lancamento == "DESPESA")
        .scalar()
    )
    saldo = Decimal(str(receita_total)) - Decimal(str(despesa_total))
    return {
        "receitas": receita_total,
        "despesas": despesa_total,
        "saldo": saldo,
    }
