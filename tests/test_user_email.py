"""Tipo: validação de e-mail do usuário (unitário)."""

from __future__ import annotations

from app.user_email import recipient_from_form_and_user, validate_usuario_email


def test_validate_accepts_valid_email():
    errs, norm = validate_usuario_email("  a@b.co  ")
    assert errs == []
    assert norm == "a@b.co"


def test_validate_empty_clears():
    errs, norm = validate_usuario_email("   ")
    assert errs == []
    assert norm is None


def test_validate_rejects_invalid():
    errs, norm = validate_usuario_email("sem-arroba")
    assert errs
    assert norm is None


def test_recipient_prefers_form_over_saved():
    assert recipient_from_form_and_user("novo@x.com", "velho@x.com") == "novo@x.com"


def test_recipient_falls_back_to_saved():
    assert recipient_from_form_and_user("", "salvo@x.com") == "salvo@x.com"
    assert recipient_from_form_and_user("  ", "salvo@x.com") == "salvo@x.com"
