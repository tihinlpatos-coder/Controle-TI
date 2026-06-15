from flask import Flask, render_template_string, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

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
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(200) NOT NULL,
        usuario VARCHAR(100) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        perfil VARCHAR(50) DEFAULT 'usuario'
    )
    """)

    # Produtos / Almoxarifado
    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(200) NOT NULL,
        quantidade INTEGER NOT NULL
    )
    """)

    # Setores
    cur.execute("""
    CREATE TABLE IF NOT EXISTS setores (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(200) NOT NULL
    )
    """)

    # Chamados de TI
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chamados (
        id SERIAL PRIMARY KEY,
        solicitante VARCHAR(200),
        setor VARCHAR(200),
        descricao TEXT,
        status VARCHAR(50) DEFAULT 'ABERTO',
        data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, quantidade
        FROM produtos
        ORDER BY id DESC
    """)

    produtos = cur.fetchall()

    cur.close()
    conn.close()

    return """
<h1>Sistema Hospitalar</h1>
<p>Banco funcionando.</p>
"""

@app.route("/novo", methods=["POST"])
def novo():
    nome = request.form["nome"]
    quantidade = request.form["quantidade"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO produtos (nome, quantidade) VALUES (%s, %s)",
        (nome, quantidade)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
