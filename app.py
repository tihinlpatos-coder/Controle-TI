from flask import Flask, render_template, request, redirect, session, url_for, send_file
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import tempfile
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "hospital-secret-key")

database_url = os.getenv("DATABASE_URL", "sqlite:///estoque.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

USUARIO = "admin"
SENHA = "1234"

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    quantidade = db.Column(db.Integer, default=0)
    lote = db.Column(db.String(50))
    fabricacao = db.Column(db.String(20))
    validade = db.Column(db.String(20))

class Movimentacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        if request.form.get("usuario") == USUARIO and request.form.get("senha") == SENHA:
            session["logado"] = True
            return redirect(url_for("sistema"))
        erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/sistema")
def sistema():
    if not session.get("logado"):
        return redirect(url_for("login"))
    produtos = Produto.query.order_by(Produto.nome).all()
    movimentacoes = Movimentacao.query.order_by(Movimentacao.data_hora.desc()).limit(20).all()
    return render_template(
        "dashboard.html",
        produtos=produtos,
        movimentacoes=movimentacoes,
        total_produtos=len(produtos),
        total_estoque=sum(p.quantidade for p in produtos),
        estoque_baixo=sum(1 for p in produtos if p.quantidade < 10),
        entradas_totais=sum(m.quantidade for m in movimentacoes if m.tipo == "Entrada"),
    )

@app.route("/novo", methods=["POST"])
def novo():
    if not session.get("logado"):
        return redirect(url_for("login"))
    db.session.add(Produto(
        nome=request.form["nome"],
        quantidade=int(request.form.get("quantidade", 0)),
        lote=request.form.get("lote", ""),
        fabricacao=request.form.get("fabricacao", ""),
        validade=request.form.get("validade", "")
    ))
    db.session.commit()
    return redirect(url_for("sistema"))

@app.route("/movimentar/<int:produto_id>", methods=["POST"])
def movimentar(produto_id):
    if not session.get("logado"):
        return redirect(url_for("login"))
    produto = Produto.query.get_or_404(produto_id)
    qtd = int(request.form.get("quantidade", 0))
    tipo = request.form["tipo"]
    if tipo == "Entrada":
        produto.quantidade += qtd
    else:
        produto.quantidade -= qtd
    db.session.add(Movimentacao(produto=produto.nome, tipo=tipo, quantidade=qtd))
    db.session.commit()
    return redirect(url_for("sistema"))


@app.route("/relatorio_excel")
def relatorio_excel():
    if not session.get("logado"):
        return redirect(url_for("login"))
    produtos = Produto.query.order_by(Produto.nome).all()
    wb = Workbook()
    ws = wb.active
    ws.title = "Estoque"
    ws.append(["ID", "Produto", "Quantidade", "Lote", "Fabricação", "Validade"])
    for p in produtos:
        ws.append([p.id, p.nome, p.quantidade, p.lote, p.fabricacao, p.validade])
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(tmp.name)
    return send_file(tmp.name, as_attachment=True, download_name="relatorio_estoque.xlsx")

@app.route("/relatorio_pdf")
def relatorio_pdf():
    if not session.get("logado"):
        return redirect(url_for("login"))
    produtos = Produto.query.order_by(Produto.nome).all()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    data = [["ID", "Produto", "Qtd", "Lote", "Fabricação", "Validade"]]
    for p in produtos:
        data.append([str(p.id), p.nome, str(p.quantidade), p.lote or "", p.fabricacao or "", p.validade or ""])
    table = Table(data, colWidths=[35, 180, 40, 70, 90, 90])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    doc.build([table])
    return send_file(tmp.name, as_attachment=True, download_name="relatorio_estoque.pdf")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
