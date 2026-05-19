from flask import Flask, render_template, request, redirect, session, url_for
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "hospital-secret-key")

USERS = {
    "admin": {"senha": "1234", "perfil": "Administrador"},
    "farmacia": {"senha": "1234", "perfil": "Operador"},
    "auditor": {"senha": "1234", "perfil": "Leitura"},
}

PRODUTOS = [
    {"nome": "Pulseira Azul", "quantidade": 500},
    {"nome": "Pulseira Amarela", "quantidade": 200},
    {"nome": "Pulseira Verde", "quantidade": 80},
]

def login_required():
    return "usuario" in session

@app.route("/", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")
        if usuario in USERS and USERS[usuario]["senha"] == senha:
            session["usuario"] = usuario
            session["perfil"] = USERS[usuario]["perfil"]
            return redirect(url_for("sistema"))
        erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)

@app.route("/sistema")
def sistema():
    if not login_required():
        return redirect(url_for("login"))
    total_produtos = len(PRODUTOS)
    total_estoque = sum(p["quantidade"] for p in PRODUTOS)
    estoque_baixo = sum(1 for p in PRODUTOS if p["quantidade"] < 100)
    entradas_totais = total_estoque
    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        perfil=session["perfil"],
        produtos=PRODUTOS,
        total_produtos=total_produtos,
        total_estoque=total_estoque,
        estoque_baixo=estoque_baixo,
        entradas_totais=entradas_totais,
    )

@app.route("/novo", methods=["POST"])
def novo():
    if not login_required():
        return redirect(url_for("login"))
    nome = request.form.get("nome", "").strip()
    quantidade = int(request.form.get("quantidade", "0") or 0)
    if nome:
        PRODUTOS.append({"nome": nome, "quantidade": quantidade})
    return redirect(url_for("sistema"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
