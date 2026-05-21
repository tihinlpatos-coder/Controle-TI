from flask import Flask, render_template, request, redirect, session
import psycopg2
import os
from datetime import date

app = Flask(__name__)
app.secret_key = "hospital-secret-key"

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_db()
    cur = conn.cursor()

    with open("database/schema.sql", "r", encoding="utf-8") as f:
        cur.execute(f.read())

    # usuário admin padrão
    cur.execute("""
        INSERT INTO usuarios (usuario, senha, perfil)
        VALUES ('admin', '1234', 'Administrador')
        ON CONFLICT (usuario) DO NOTHING
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT usuario, perfil
            FROM usuarios
            WHERE usuario=%s AND senha=%s
        """, (usuario, senha))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session["usuario"] = user[0]
            session["perfil"] = user[1]

            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/dashboard")
def dashboard():

    if not session.get("usuario"):
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM produtos WHERE quantidade < 10")
    estoque_baixo = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM produtos
        WHERE validade < CURRENT_DATE
    """)
    vencidos = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_produtos=total_produtos,
        estoque_baixo=estoque_baixo,
        vencidos=vencidos
    )


@app.route("/produtos")
def produtos():

    if not session.get("usuario"):
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, quantidade,
        lote, fabricacao, validade
        FROM produtos
        ORDER BY nome
    """)

    produtos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "produtos.html",
        produtos=produtos
    )


@app.route("/cadastrar", methods=["POST"])
def cadastrar():

    if not session.get("usuario"):
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO produtos
        (nome, quantidade, lote, fabricacao, validade)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        request.form["nome"],
        request.form["quantidade"],
        request.form["lote"],
        request.form["fabricacao"],
        request.form["validade"]
    ))

    conn.commit()

    cur.close()
    conn.close()

    return redirect("/produtos")


@app.route("/movimentacoes")
def movimentacoes():

    if not session.get("usuario"):
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
        m.id,
        p.nome,
        m.tipo,
        m.quantidade,
        m.usuario,
        m.data_movimentacao
        FROM movimentacoes m
        JOIN produtos p
        ON p.id = m.produto_id
        ORDER BY m.data_movimentacao DESC
    """)

    dados = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "movimentacoes.html",
        dados=dados
    )


if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

else:

    try:
        init_db()
    except:
        pass
