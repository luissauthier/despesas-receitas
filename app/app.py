from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

from .db import db
from .models import Lancamento, Usuario


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

    def _current_user() -> Usuario | None:
        user_id = session.get("user_id")
        if not user_id:
            return None
        return Usuario.query.filter_by(id=user_id, situacao="ATIVO").first()

    def _require_login():
        if _current_user() is None:
            return redirect(url_for("login", next=request.full_path))
        return None

    @app.get("/")
    def index():
        guard = _require_login()
        if guard is not None:
            return guard
        return redirect(url_for("listar_lancamentos"))

    @app.get("/lancamentos")
    def listar_lancamentos():
        guard = _require_login()
        if guard is not None:
            return guard
        lancamentos = (
            Lancamento.query.order_by(Lancamento.data_lancamento.desc(), Lancamento.id.desc()).all()
        )
        return render_template("lancamentos.html", lancamentos=lancamentos, user=_current_user())

    @app.get("/login")
    def login():
        if _current_user() is not None:
            return redirect(url_for("listar_lancamentos"))
        next_url = request.args.get("next") or url_for("listar_lancamentos")
        return render_template("login.html", next_url=next_url, error=None)

    @app.post("/login")
    def login_post():
        login_value = (request.form.get("login") or "").strip()
        senha = request.form.get("senha") or ""
        next_url = request.form.get("next") or url_for("listar_lancamentos")

        user = Usuario.query.filter_by(login=login_value, situacao="ATIVO").first()
        if user is None or user.senha != senha:
            return render_template(
                "login.html",
                next_url=next_url,
                error="Login ou senha inválidos.",
            )

        session["user_id"] = user.id
        return redirect(next_url)

    @app.post("/logout")
    def logout():
        session.pop("user_id", None)
        return redirect(url_for("login"))

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

