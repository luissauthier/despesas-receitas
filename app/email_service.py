from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask


def send_plaintext_email(
    app: Flask,
    to_addrs: list[str],
    subject: str,
    body: str,
) -> bool:
    """Envia e-mail em texto plano. Com MAIL_SUPPRESS_SEND=True, só registra na caixa de teste. Retorna True se enfileirado/enviado."""
    recipients = [a.strip() for a in to_addrs if a and a.strip()]
    if not recipients:
        return False

    if app.config.get("MAIL_SUPPRESS_SEND"):
        outbox: list[dict] = app.config.setdefault("_mail_outbox", [])
        outbox.append({"to": recipients, "subject": subject, "body": body, "attachments": []})
        return True

    server = app.config.get("MAIL_SERVER")
    port = int(app.config.get("MAIL_PORT") or 587)
    user = app.config.get("MAIL_USERNAME") or ""
    password = app.config.get("MAIL_PASSWORD") or ""
    use_tls = app.config.get("MAIL_USE_TLS", True)
    sender = app.config.get("MAIL_DEFAULT_SENDER") or user or "noreply@localhost"

    if not server:
        app.logger.warning("MAIL_SERVER não configurado; e-mail não enviado.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

    with smtplib.SMTP(server, port, timeout=30) as smtp:
        if use_tls:
            smtp.starttls()
        if user:
            smtp.login(user, password)
        smtp.send_message(msg)
    return True


def send_email_with_pdf(
    app: Flask,
    to_addrs: list[str],
    subject: str,
    body: str,
    pdf_bytes: bytes,
    filename: str = "lancamentos.pdf",
) -> bool:
    """Envia e-mail com PDF anexo. Retorna True se enfileirado/enviado."""
    recipients = [a.strip() for a in to_addrs if a and a.strip()]
    if not recipients:
        return False

    if app.config.get("MAIL_SUPPRESS_SEND"):
        outbox: list[dict] = app.config.setdefault("_mail_outbox", [])
        outbox.append(
            {
                "to": recipients,
                "subject": subject,
                "body": body,
                "attachments": [{"filename": filename, "size": len(pdf_bytes)}],
            }
        )
        return True

    server = app.config.get("MAIL_SERVER")
    port = int(app.config.get("MAIL_PORT") or 587)
    user = app.config.get("MAIL_USERNAME") or ""
    password = app.config.get("MAIL_PASSWORD") or ""
    use_tls = app.config.get("MAIL_USE_TLS", True)
    sender = app.config.get("MAIL_DEFAULT_SENDER") or user or "noreply@localhost"

    if not server:
        app.logger.warning("MAIL_SERVER não configurado; e-mail com PDF não enviado.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=filename)

    with smtplib.SMTP(server, port, timeout=30) as smtp:
        if use_tls:
            smtp.starttls()
        if user:
            smtp.login(user, password)
        smtp.send_message(msg)
    return True


def notify_lancamento_event(
    app: Flask,
    user_email: str | None,
    *,
    event: str,
    descricao: str,
    data_str: str,
    valor_str: str,
    tipo: str,
    situacao: str,
) -> None:
    if not user_email or not user_email.strip():
        return
    action = "criado" if event == "create" else "atualizado"
    subject = f"Lançamento {action}: {descricao[:60]}"
    body = (
        f"Seu lançamento foi {action}.\n\n"
        f"Descrição: {descricao}\n"
        f"Data: {data_str}\n"
        f"Valor: {valor_str}\n"
        f"Tipo: {tipo}\n"
        f"Situação: {situacao}\n"
    )
    send_plaintext_email(app, [user_email.strip()], subject, body)
