from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "hinl2026"


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario == "admin" and senha == "admin123":

            session["usuario"] = usuario
            session["perfil"] = "ADMIN"

            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        perfil=session["perfil"]
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
