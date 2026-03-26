from __future__ import annotations

from datetime import date

from .db import db


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    login = db.Column(db.String(80), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    situacao = db.Column(db.String(20), nullable=False, default="ATIVO")


class Lancamento(db.Model):
    __tablename__ = "lancamento"

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    data_lancamento = db.Column(db.Date, nullable=False, default=date.today)
    valor = db.Column(db.Numeric(12, 2), nullable=False)
    tipo_lancamento = db.Column(db.String(20), nullable=False)  # RECEITA | DESPESA
    situacao = db.Column(db.String(20), nullable=False, default="ATIVO")

