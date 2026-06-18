from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "hinl2026"

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )


def criar_tabelas():

    conn = get_db()
    cur = conn.cursor()

    # Usuários
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id SERIAL PRIMARY KEY,
        nome VARCHAR(200),
        usuario VARCHAR(100) UNIQUE,
        senha VARCHAR(200),
        perfil VARCHAR(50)
    )
    """)

    # Produtos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos(
        id SERIAL PRIMARY KEY,
        nome VARCHAR(200),
        quantidade INTEGER DEFAULT 0,
        estoque_minimo INTEGER DEFAULT 0
    )
    """)

    # Equipamentos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS equipamentos(
        id SERIAL PRIMARY KEY,
        patrimonio VARCHAR(50),
        tipo VARCHAR(100),
        marca VARCHAR(100),
        modelo VARCHAR(100),
        serie VARCHAR(100),
        setor VARCHAR(100),
        status VARCHAR(50)
    )
    """)

    # Setores
    cur.execute("""
    CREATE TABLE IF NOT EXISTS setores(
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100)
    )
    """)

    # Chamados
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chamados(
        id SERIAL PRIMARY KEY,
        solicitante VARCHAR(200),
        setor VARCHAR(100),
        descricao TEXT,
        prioridade VARCHAR(20),
        status VARCHAR(20),
        tecnico VARCHAR(100),
        data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cur.close()
    conn.close()
    

def criar_admin():

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM usuarios WHERE usuario=%s",
        ("admin",)
    )

    existe = cur.fetchone()

    if not existe:

        cur.execute("""
        INSERT INTO usuarios
        (nome, usuario, senha, perfil)
        VALUES
        (%s,%s,%s,%s)
        """,
        (
            "Administrador",
            "admin",
            "admin123",
            "ADMIN"
        ))

    conn.commit()
    cur.close()
    conn.close()


criar_tabelas()
criar_admin()

@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT usuario, perfil
            FROM usuarios
            WHERE usuario=%s
            AND senha=%s
            """,
            (usuario, senha)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session["usuario"] = user[0]
            session["perfil"] = user[1]

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


@app.route("/novo", methods=["POST"])
def novo():

    nome = request.form["nome"]
    quantidade = request.form["quantidade"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO produtos (nome, quantidade)
        VALUES (%s, %s)
        """,
        (nome, quantidade)
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
