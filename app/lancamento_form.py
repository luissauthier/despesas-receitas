from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation


def parse_lancamento_form(form: dict[str, str]):
    """Valida dados do formulário de lançamento. Retorna (errors, cleaned, parsed_date, parsed_valor, tipo, situacao)."""
    descricao = (form.get("descricao") or "").strip()
    data_raw = (form.get("data_lancamento") or "").strip()
    valor_raw = (form.get("valor") or "").strip().replace(",", ".")
    tipo = (form.get("tipo_lancamento") or "").strip().upper()
    situacao = (form.get("situacao") or "").strip().upper()

    errors: list[str] = []

    if not descricao:
        errors.append("Descrição é obrigatória.")
    elif len(descricao) > 255:
        errors.append("Descrição deve ter no máximo 255 caracteres.")

    parsed_date: date | None = None
    if not data_raw:
        data_raw = date.today().isoformat()
    try:
        parsed_date = date.fromisoformat(data_raw)
    except ValueError:
        errors.append("Data inválida.")

    parsed_valor: Decimal | None = None
    if not valor_raw:
        errors.append("Valor é obrigatório.")
    else:
        try:
            parsed_valor = Decimal(valor_raw)
        except (InvalidOperation, ValueError):
            errors.append("Valor inválido. Use formato como 123.45")
        else:
            if parsed_valor <= 0:
                errors.append("Valor deve ser maior que zero.")

    if tipo not in {"RECEITA", "DESPESA"}:
        errors.append("Tipo deve ser RECEITA ou DESPESA.")

    if situacao not in {"PAGO", "EM_ABERTO"}:
        errors.append("Situação deve ser PAGO ou EM_ABERTO.")

    cleaned = {
        "descricao": descricao,
        "data_lancamento": data_raw,
        "valor": (form.get("valor") or "").strip(),
        "tipo_lancamento": tipo or "RECEITA",
        "situacao": situacao or "EM_ABERTO",
    }

    return errors, cleaned, parsed_date, parsed_valor, tipo, situacao
