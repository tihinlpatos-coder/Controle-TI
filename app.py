from flask import Flask, render_template, request, redirect, session, url_for
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
