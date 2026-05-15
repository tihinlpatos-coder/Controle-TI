from flask import Flask, render_template, request, redirect, session, url_for
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "hospital-secret-key")

USUARIO = "admin"
SENHA = "1234"

produtos = []

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
    total_produtos = len(produtos)
    total_estoque = sum(int(p["quantidade"]) for p in produtos) if produtos else 0
    estoque_baixo = sum(1 for p in produtos if int(p["quantidade"]) < 10)
    entradas_totais = sum(max(0, int(p["quantidade"])) for p in produtos) if produtos else 0
    busca = request.args.get("q", "").lower()
    lista = [p for p in produtos if busca in p["nome"].lower()] if busca else produtos
    return render_template(
        "dashboard.html",
        produtos=lista,
        total_produtos=total_produtos,
        total_estoque=total_estoque,
        estoque_baixo=estoque_baixo,
        entradas_totais=entradas_totais,
        busca=busca
    )

@app.route("/novo", methods=["POST"])
def novo():
    if not session.get("logado"):
        return redirect(url_for("login"))
    nome = request.form.get("nome", "").strip()
    quantidade = request.form.get("quantidade", "0").strip()
    lote = request.form.get("lote", "").strip()
    if nome:
        produtos.append({"nome": nome, "quantidade": quantidade or "0", "lote": lote})
    return redirect(url_for("sistema"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
