from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template, url_for

from .db import db
from .models import Lancamento


def create_app() -> Flask:
    app = Flask(__name__)

    base_dir = Path(__file__).resolve().parent.parent
    instance_dir = base_dir / "instance"
    instance_dir.mkdir(exist_ok=True)
    db_path = instance_dir / "app.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    db.init_app(app)

    with app.app_context():
        db.create_all()
        _seed_if_empty(db_path=db_path)

    @app.get("/")
    def index():
        return redirect(url_for("listar_lancamentos"))

    @app.get("/lancamentos")
    def listar_lancamentos():
        lancamentos = (
            Lancamento.query.order_by(Lancamento.data_lancamento.desc(), Lancamento.id.desc()).all()
        )
        return render_template("lancamentos.html", lancamentos=lancamentos)

    return app


def _seed_if_empty(db_path: Path) -> None:
    if Lancamento.query.first() is not None:
        return

    seed_file = Path(__file__).resolve().parent / "seed.sql"
    sql = seed_file.read_text(encoding="utf-8")
    con = sqlite3.connect(db_path)
    try:
        con.executescript(sql)
        con.commit()
    finally:
        con.close()


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)

