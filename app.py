from flask import Flask, render_template, session, redirect, url_for

from config import Config
from database import criar_tabelas, criar_admin

app = Flask(__name__)
app.config.from_object(Config)

# Inicializa o banco
criar_tabelas()
criar_admin()


@app.route("/")
def index():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ==========================
# LOGIN
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():
    from routes.auth import login_usuario
    return login_usuario()


# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==========================
# DASHBOARD
# ==========================
@app.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        perfil=session["perfil"]
    )


# ==========================
# USUÁRIOS
# ==========================
@app.route("/usuarios")
def usuarios():

    if "usuario" not in session:
        return redirect(url_for("login"))

    from routes.usuarios import listar_usuarios
    return listar_usuarios()


# ==========================
# EQUIPAMENTOS
# ==========================
@app.route("/equipamentos")
def equipamentos():

    if "usuario" not in session:
        return redirect(url_for("login"))

    from routes.equipamentos import listar_equipamentos
    return listar_equipamentos()


# ==========================
# CHAMADOS
# ==========================
@app.route("/chamados")
def chamados():

    if "usuario" not in session:
        return redirect(url_for("login"))

    from routes.chamados import listar_chamados
    return listar_chamados()


# ==========================
# ALMOXARIFADO
# ==========================
@app.route("/almoxarifado")
def almoxarifado():

    if "usuario" not in session:
        return redirect(url_for("login"))

    from routes.almoxarifado import listar_produtos
    return listar_produtos()


# ==========================
# RELATÓRIOS
# ==========================
@app.route("/relatorios")
def relatorios():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template("relatorios.html")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
