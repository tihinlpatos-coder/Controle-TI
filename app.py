from flask import Flask, request, redirect, url_for, render_template, session
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
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(200) NOT NULL,
        usuario VARCHAR(100) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        perfil VARCHAR(50) DEFAULT 'USUARIO'
    )
    """)

    # Setores
    cur.execute("""
    CREATE TABLE IF NOT EXISTS setores (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(200) NOT NULL
    )
    """)

    # Produtos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(200) NOT NULL,
        quantidade INTEGER DEFAULT 0,
        estoque_minimo INTEGER DEFAULT 0
    )
    """)

    # Equipamentos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS equipamentos (
        id SERIAL PRIMARY KEY,
        patrimonio VARCHAR(50),
        tipo VARCHAR(100),
        marca VARCHAR(100),
        modelo VARCHAR(100),
        serie VARCHAR(100),
        setor VARCHAR(100),
        status VARCHAR(50) DEFAULT 'ATIVO'
    )
    """)

    # Chamados
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chamados (
        id SERIAL PRIMARY KEY,
        solicitante VARCHAR(200),
        setor VARCHAR(200),
        descricao TEXT,
        prioridade VARCHAR(20) DEFAULT 'MEDIA',
        status VARCHAR(50) DEFAULT 'ABERTO',
        tecnico VARCHAR(200),
        data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

# Cria as tabelas automaticamente
criar_tabelas()
def criar_admin():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM usuarios
        WHERE usuario='admin'
    """)

    existe = cur.fetchone()

    if not existe:
        cur.execute("""
            INSERT INTO usuarios
            (nome, usuario, senha, perfil)
            VALUES
            ('Administrador',
             'admin',
             'admin123',
             'ADMIN')
        """)

    conn.commit()
    cur.close()
    conn.close()

criar_admin()
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT usuario, perfil
            FROM usuarios
            WHERE usuario=%s
            AND senha=%s
        """, (usuario, senha))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session["usuario"] = user[0]
            session["perfil"] = user[1]

            return redirect("/dashboard")

    return render_template("login.html")
    @app.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        perfil=session["perfil"]
    )
@app.route("/")
def index():
    return redirect("/login")
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

    html = """
    <h1>Sistema Hospitalar</h1>
    <h2>Produtos cadastrados</h2>

    <form action="/novo" method="post">
        <input type="text" name="nome" placeholder="Produto" required>
        <input type="number" name="quantidade" placeholder="Quantidade" required>
        <button type="submit">Salvar</button>
    </form>

    <hr>

    <table border="1">
        <tr>
            <th>ID</th>
            <th>Produto</th>
            <th>Quantidade</th>
        </tr>
    """

    for p in produtos:
        html += f"""
        <tr>
            <td>{p[0]}</td>
            <td>{p[1]}</td>
            <td>{p[2]}</td>
        </tr>
        """

    html += "</table>"

    return html

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
