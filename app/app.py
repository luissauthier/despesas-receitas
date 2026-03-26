from __future__ import annotations

import os
import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func

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

    def _parse_lancamento_form(form: dict[str, str]):
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

        q = (request.args.get("q") or "").strip()
        tipo = (request.args.get("tipo") or "").strip().upper()
        situacao = (request.args.get("situacao") or "").strip().upper()
        de = (request.args.get("de") or "").strip()
        ate = (request.args.get("ate") or "").strip()

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
                flash("Filtro 'de' inválido.", "warning")
        if ate:
            try:
                query = query.filter(Lancamento.data_lancamento <= date.fromisoformat(ate))
            except ValueError:
                flash("Filtro 'até' inválido.", "warning")

        lancamentos = query.order_by(Lancamento.data_lancamento.desc(), Lancamento.id.desc()).all()

        receita_total = (
            query.with_entities(func.coalesce(func.sum(Lancamento.valor), 0))
            .filter(Lancamento.tipo_lancamento == "RECEITA")
            .scalar()
        )
        despesa_total = (
            query.with_entities(func.coalesce(func.sum(Lancamento.valor), 0))
            .filter(Lancamento.tipo_lancamento == "DESPESA")
            .scalar()
        )
        saldo = Decimal(str(receita_total)) - Decimal(str(despesa_total))

        filtros = {"q": q, "tipo": tipo, "situacao": situacao, "de": de, "ate": ate}
        kpis = {"receitas": receita_total, "despesas": despesa_total, "saldo": saldo}

        return render_template(
            "lancamentos.html",
            lancamentos=lancamentos,
            user=_current_user(),
            filtros=filtros,
            kpis=kpis,
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

        errors, cleaned, parsed_date, parsed_valor, tipo, situacao = _parse_lancamento_form(
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
        flash("Lançamento criado com sucesso.", "success")
        return redirect(url_for("listar_lancamentos"))

    @app.get("/lancamentos/<int:lancamento_id>/editar")
    def editar_lancamento(lancamento_id: int):
        guard = _require_login()
        if guard is not None:
            return guard
        lanc = Lancamento.query.get_or_404(lancamento_id)
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
        lanc = Lancamento.query.get_or_404(lancamento_id)

        errors, cleaned, parsed_date, parsed_valor, tipo, situacao = _parse_lancamento_form(
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
        flash("Lançamento atualizado com sucesso.", "success")
        return redirect(url_for("listar_lancamentos"))

    @app.post("/lancamentos/<int:lancamento_id>/excluir")
    def excluir_lancamento(lancamento_id: int):
        guard = _require_login()
        if guard is not None:
            return guard
        lanc = Lancamento.query.get_or_404(lancamento_id)
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

