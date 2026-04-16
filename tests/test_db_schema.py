"""Tipo: inspeção de schema / tabelas após create_all."""

from __future__ import annotations

from sqlalchemy import inspect

from app.db import db


# Inspeciona o banco para garantir que a tabela de usuário possui os campos críticos de segurança e login.
def test_usuario_table_has_expected_columns(app):
    with app.app_context():
        cols = {c["name"] for c in inspect(db.engine).get_columns("usuario")}
        assert "login" in cols
        assert "email" in cols
        assert "senha" in cols


# Valida se a tabela de lançamentos foi criada corretamente durante a inicialização do app.
def test_lancamento_table_exists(app):
    with app.app_context():
        tables = inspect(db.engine).get_table_names()
        assert "lancamento" in tables
