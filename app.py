
from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "hospital-secret-key"

DB_NAME = "hospital.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT,
        perfil TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        quantidade INTEGER,
        lote TEXT,
        fabricacao TEXT,
        validade TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        tipo TEXT,
        quantidade INTEGER,
        usuario TEXT,
        data_movimentacao TEXT
    )
    ''')

    cur.execute(
        "INSERT OR IGNORE INTO usuarios(usuario, senha, perfil) VALUES (?, ?, ?)",
        ("admin", "1234", "Administrador")
    )

    conn.commit()
    conn.close()

@app.route("/novo")
def novo():
    if not session.get("usuario"):
        return redirect("/")

    return render_template("novo.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM usuarios WHERE usuario=? AND senha=?",
            (usuario, senha)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["usuario"] = user["usuario"]
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

    hoje = str(date.today())

    cur.execute("SELECT COUNT(*) FROM produtos WHERE validade < ?", (hoje,))
    vencidos = cur.fetchone()[0]

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

    cur.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = cur.fetchall()

    conn.close()

    return render_template("produtos.html", produtos=produtos)

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    if not session.get("usuario"):
        return redirect("/")

    nome = request.form["nome"]
    quantidade = int(request.form["quantidade"])
    lote = request.form["lote"]
    fabricacao = request.form["fabricacao"]
    validade = request.form["validade"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        '''
        INSERT INTO produtos(nome, quantidade, lote, fabricacao, validade)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (nome, quantidade, lote, fabricacao, validade)
    )

    conn.commit()
    conn.close()

    return redirect("/produtos")

@app.route("/entrada/<int:id>", methods=["POST"])
def entrada(id):
    quantidade = int(request.form["quantidade"])

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?",
        (quantidade, id)
    )

    cur.execute(
        '''
        INSERT INTO movimentacoes(produto_id, tipo, quantidade, usuario, data_movimentacao)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (id, "Entrada", quantidade, session["usuario"], datetime.now())
    )

    conn.commit()
    conn.close()

    return redirect("/produtos")

@app.route("/saida/<int:id>", methods=["POST"])
def saida(id):
    quantidade = int(request.form["quantidade"])

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?",
        (quantidade, id)
    )

    cur.execute(
        '''
        INSERT INTO movimentacoes(produto_id, tipo, quantidade, usuario, data_movimentacao)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (id, "Saída", quantidade, session["usuario"], datetime.now())
    )

    conn.commit()
    conn.close()

    return redirect("/produtos")

@app.route("/movimentacoes")
def movimentacoes():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
    SELECT m.id, p.nome, m.tipo, m.quantidade, m.usuario, m.data_movimentacao
    FROM movimentacoes m
    JOIN produtos p ON p.id = m.produto_id
    ORDER BY m.id DESC
    ''')

    dados = cur.fetchall()

    conn.close()

    return render_template("movimentacoes.html", dados=dados)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    init_db()
