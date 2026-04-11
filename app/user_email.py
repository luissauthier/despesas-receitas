from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_usuario_email(raw: str | None) -> tuple[list[str], str | None]:
    """Retorna (erros, e-mail normalizado ou None para limpar)."""
    s = (raw or "").strip()
    if not s:
        return [], None
    if len(s) > 120:
        return ["E-mail deve ter no máximo 120 caracteres."], None
    if not _EMAIL_RE.match(s):
        return ["Informe um e-mail válido ou deixe em branco."], None
    return [], s


def recipient_from_form_and_user(form_email: str | None, user_email: str | None) -> str | None:
    """Usa o e-mail do campo do formulário; se vazio, o e-mail salvo no usuário."""
    raw = (form_email or "").strip()
    if raw:
        return raw
    u = (user_email or "").strip()
    return u or None
