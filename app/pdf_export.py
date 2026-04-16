from __future__ import annotations

from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from .models import Lancamento


# Função principal para geração do relatório PDF. 
# Recebe os dados processados e os totais para compor o cabeçalho e a tabela.
def build_lancamentos_pdf(
    lancamentos: list[Lancamento],
    *,
    titulo: str = "Lançamentos",
    receitas: Decimal | float | int = 0,
    despesas: Decimal | float | int = 0,
    saldo: Decimal | float | int = 0,
) -> bytes:
    # Utiliza BytesIO para gerar o PDF inteiramente em memória,
    # evitando escrita em disco e melhorando a performance/segurança.
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, y, titulo)
    y -= 0.8 * cm
    c.setFont("Helvetica", 10)
    c.drawString(
        2 * cm,
        y,
        f"Resumo — Receitas: R$ {float(receitas):.2f} | Despesas: R$ {float(despesas):.2f} | Saldo: R$ {float(saldo):.2f}",
    )
    y -= 1 * cm

    headers = ["ID", "Descrição", "Data", "Valor", "Tipo", "Situação"]
    col_x = [2 * cm, 2.8 * cm, 10.5 * cm, 12.2 * cm, 14.5 * cm, 16.8 * cm]
    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers):
        c.drawString(col_x[i], y, h)
    y -= 0.35 * cm
    c.setStrokeColor(colors.grey)
    c.line(2 * cm, y, width - 2 * cm, y)
    y -= 0.45 * cm

    c.setFont("Helvetica", 8)
    for l in lancamentos:
        # Verifica se o cursor Y atingiu o limite inferior da página para realizar a quebra automática.
        if y < 2.5 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 8)

        desc = (l.descricao[:42] + "…") if len(l.descricao) > 43 else l.descricao
        c.drawString(col_x[0], y, str(l.id))
        c.drawString(col_x[1], y, desc)
        c.drawString(col_x[2], y, l.data_lancamento.strftime("%d/%m/%Y"))
        c.drawString(col_x[3], y, f"{float(l.valor):.2f}")
        c.drawString(col_x[4], y, l.tipo_lancamento[:8])
        c.drawString(col_x[5], y, l.situacao[:10])
        y -= 0.42 * cm

    c.save()
    pdf = buf.getvalue()
    buf.close()
    return pdf
