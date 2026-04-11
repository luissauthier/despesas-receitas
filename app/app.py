from __future__ import annotations

import os
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import inspect, text

from .db import db
from .email_service import notify_lancamento_event
from .lancamento_form import parse_lancamento_form
from .lancamentos_filters import build_lancamentos_query, kpis_for_query
from .models import Lancamento, Usuario
from .pdf_export import build_lancamentos_pdf


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)

    base_dir = Path(__file__).resolve().parent.parent
    instance_dir = base_dir / "instance"
    instance_dir.mkdir(exist_ok=True)
    db_path = instance_dir / "app.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["MAIL_SUPPRESS_SEND"] = os.getenv("MAIL_SUPPRESS_SEND", "").lower() in ("1", "true", "yes")
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "")

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        _migrate_sqlite_usuario_email()
        if not app.config.get("TESTING"):
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

    def _notify_lancamento_saved(lanc: Lancamento, *, event: str) -> None:
        user = _current_user()
        notify_lancamento_event(
            app,
            user.email if user else None,
            event=event,
            descricao=lanc.descricao,
            data_str=lanc.data_lancamento.isoformat(),
            valor_str=str(lanc.valor),
            tipo=lanc.tipo_lancamento,
            situacao=lanc.situacao,
        )

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

        query, filtros, filter_flashes = build_lancamentos_query(request.args)
        for category, message in filter_flashes:
            flash(message, category)

        lancamentos = query.order_by(Lancamento.data_lancamento.desc(), Lancamento.id.desc()).all()
        kpis = kpis_for_query(query)

        return render_template(
            "lancamentos.html",
            lancamentos=lancamentos,
            user=_current_user(),
            filtros=filtros,
            kpis=kpis,
        )

    @app.get("/lancamentos/exportar-pdf")
    def exportar_lancamentos_pdf():
        guard = _require_login()
        if guard is not None:
            return guard

        query, filtros, filter_flashes = build_lancamentos_query(request.args)
        for category, message in filter_flashes:
            flash(message, category)

        lancamentos = query.order_by(Lancamento.data_lancamento.desc(), Lancamento.id.desc()).all()
        kpis = kpis_for_query(query)

        pdf_bytes = build_lancamentos_pdf(
            lancamentos,
            titulo="Lançamentos (exportação)",
            receitas=kpis["receitas"],
            despesas=kpis["despesas"],
            saldo=kpis["saldo"],
        )
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=lancamentos.pdf"},
        )

    @app.get("/lancamentos/novo")
    def novo_lancamento():
        guard = _require_login()
        if guard is not None:
            return guard
        form = {
            "descricao": "",
            "data_lancamento": date.today().isoformat(),
            "valor": "",
            "tipo_lancamento": "RECEITA",
            "situacao": "EM_ABERTO",
        }
        return render_template(
            "lancamento_form.html",
            user=_current_user(),
            page_title="Novo lançamento",
            page_subtitle="Cadastrar receita ou despesa",
            form=form,
            form_action=url_for("novo_lancamento_post"),
            show_delete=False,
            lancamento_id=None,
        )

    @app.post("/lancamentos/novo")
    def novo_lancamento_post():
        guard = _require_login()
        if guard is not None:
            return guard

        errors, cleaned, parsed_date, parsed_valor, tipo, situacao = parse_lancamento_form(
            request.form.to_dict()
        )
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "lancamento_form.html",
                user=_current_user(),
                page_title="Novo lançamento",
                page_subtitle="Cadastrar receita ou despesa",
                form=cleaned,
                form_action=url_for("novo_lancamento_post"),
                show_delete=False,
                lancamento_id=None,
            )

        lanc = Lancamento(
            descricao=cleaned["descricao"],
            data_lancamento=parsed_date,
            valor=parsed_valor,
            tipo_lancamento=tipo,
            situacao=situacao,
        )
        db.session.add(lanc)
        db.session.commit()
        _notify_lancamento_saved(lanc, event="create")
        flash("Lançamento criado com sucesso.", "success")
        return redirect(url_for("listar_lancamentos"))

    @app.get("/lancamentos/<int:lancamento_id>/editar")
    def editar_lancamento(lancamento_id: int):
        guard = _require_login()
        if guard is not None:
            return guard
        lanc = db.session.get(Lancamento, lancamento_id)
        if lanc is None:
            abort(404)
        form = {
            "descricao": lanc.descricao,
            "data_lancamento": lanc.data_lancamento.isoformat(),
            "valor": str(lanc.valor),
            "tipo_lancamento": lanc.tipo_lancamento,
            "situacao": lanc.situacao,
        }
        return render_template(
            "lancamento_form.html",
            user=_current_user(),
            page_title=f"Editar lançamento #{lanc.id}",
            page_subtitle="Atualize os dados e salve",
            form=form,
            form_action=url_for("editar_lancamento_post", lancamento_id=lanc.id),
            show_delete=True,
            lancamento_id=lanc.id,
        )

    @app.post("/lancamentos/<int:lancamento_id>/editar")
    def editar_lancamento_post(lancamento_id: int):
        guard = _require_login()
        if guard is not None:
            return guard
        lanc = db.session.get(Lancamento, lancamento_id)
        if lanc is None:
            abort(404)

        errors, cleaned, parsed_date, parsed_valor, tipo, situacao = parse_lancamento_form(
            request.form.to_dict()
        )
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "lancamento_form.html",
                user=_current_user(),
                page_title=f"Editar lançamento #{lanc.id}",
                page_subtitle="Atualize os dados e salve",
                form=cleaned,
                form_action=url_for("editar_lancamento_post", lancamento_id=lanc.id),
                show_delete=True,
                lancamento_id=lanc.id,
            )

        lanc.descricao = cleaned["descricao"]
        lanc.data_lancamento = parsed_date
        lanc.valor = parsed_valor
        lanc.tipo_lancamento = tipo
        lanc.situacao = situacao
        db.session.commit()
        _notify_lancamento_saved(lanc, event="update")
        flash("Lançamento atualizado com sucesso.", "success")
        return redirect(url_for("listar_lancamentos"))

    @app.post("/lancamentos/<int:lancamento_id>/excluir")
    def excluir_lancamento(lancamento_id: int):
        guard = _require_login()
        if guard is not None:
            return guard
        lanc = db.session.get(Lancamento, lancamento_id)
        if lanc is None:
            abort(404)
        db.session.delete(lanc)
        db.session.commit()
        flash(f"Lançamento #{lancamento_id} excluído.", "success")
        return redirect(url_for("listar_lancamentos"))

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


def _migrate_sqlite_usuario_email() -> None:
    uri = db.engine.url.drivername
    if uri != "sqlite":
        return
    try:
        cols = {c["name"] for c in inspect(db.engine).get_columns("usuario")}
    except Exception:
        return
    if "email" in cols:
        return
    with db.engine.begin() as conn:
        conn.execute(text("ALTER TABLE usuario ADD COLUMN email VARCHAR(120)"))


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
