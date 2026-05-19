from flask import Flask, request, redirect, session, url_for, render_template
import os
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "hospital-secret-key")
USERS = {
    "admin": {"senha": "1234", "perfil": "Administrador"},
    "farmacia": {"senha": "1234", "perfil": "Operador"},
    "auditor": {"senha": "1234", "perfil": "Leitura"},
}
@app.route("/", methods=["GET","POST"])
def login():
    erro = None
    if request.method == "POST":
        u = request.form.get("usuario")
        s = request.form.get("senha")
        if u in USERS and USERS[u]["senha"] == s:
            session["usuario"] = u
            session["perfil"] = USERS[u]["perfil"]
            return redirect(url_for("sistema"))
        erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)
@app.route("/sistema")
def sistema():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", usuario=session["usuario"], perfil=session["perfil"], usuarios=USERS)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
