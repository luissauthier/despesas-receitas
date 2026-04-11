"""Tipo: teste de conexão / engine com o banco."""

from __future__ import annotations

from sqlalchemy import inspect, text

from app.db import db


def test_engine_connects(app):
    with app.app_context():
        with db.engine.connect() as conn:
            row = conn.execute(text("SELECT 1")).scalar()
            assert row == 1


def test_sqlite_uri_configured(app):
    assert "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]
