from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from database import get_db

app = Flask(__name__)
app.config.from_object(Config)


# =====================================
# CRIAÇÃO DAS TABELAS
# =====================================

def criar_tabelas():

    conn = get_db()
    cur = conn.cursor()

    # Usuários
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios(
            id SERIAL PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            usuario VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            perfil VARCHAR(50) NOT NULL
        );
    """)

    # Setores
    cur.execute("""
        CREATE TABLE IF NOT EXISTS setores(
            id SERIAL PRIMARY KEY,
            nome VARCHAR(150) UNIQUE NOT NULL
        );
    """)

    # Equipamentos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS equipamentos(
            id SERIAL PRIMARY KEY,
            patrimonio VARCHAR(50),
            tipo VARCHAR(100),
            marca VARCHAR(100),
            modelo VARCHAR(100),
            numero_serie VARCHAR(100),
            setor VARCHAR(150),
            status VARCHAR(50)
        );
    """)

    # Chamados
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chamados(
            id SERIAL PRIMARY KEY,
            solicitante VARCHAR(150),
            setor VARCHAR(150),
            descricao TEXT,
            prioridade VARCHAR(20),
            status VARCHAR(30),
            tecnico VARCHAR(150),
            data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Produtos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos(
            id SERIAL PRIMARY KEY,
            nome VARCHAR(200),
            quantidade INTEGER DEFAULT 0,
            estoque_minimo INTEGER DEFAULT 0
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    # =====================================
# CRIA USUÁRIO ADMINISTRADOR
# =====================================

def criar_admin():

    conn = get_db()
    cur = conn.cursor()

    senha_hash = generate_password_hash("admin123")

    cur.execute("""
        DELETE FROM usuarios
        WHERE usuario='admin'
    """)

    cur.execute("""
        INSERT INTO usuarios
        (nome, usuario, senha, perfil)
        VALUES (%s,%s,%s,%s)
    """,
    (
        "Administrador",
        "admin",
        senha_hash,
        "ADMIN"
    ))

    conn.commit()
    cur.close()
    conn.close()


# =====================================
# INICIALIZA O BANCO
# =====================================

criar_tabelas()

criar_admin()
# =====================================
# PÁGINA INICIAL
# =====================================

@app.route("/")
def index():
    return redirect(url_for("login"))


# =====================================
# LOGIN
# =====================================

@app.route("/login", methods=["GET", "POST"])
def login():

    erro = None

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, nome, usuario, senha, perfil
            FROM usuarios
            WHERE usuario=%s
        """, (usuario,))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:

            senha_banco = user[3]

            if check_password_hash(senha_banco, senha):

                session["id"] = user[0]
                session["nome"] = user[1]
                session["usuario"] = user[2]
                session["perfil"] = user[4]

                return redirect(url_for("dashboard"))

        erro = "Usuário ou senha inválidos."

    return render_template("login.html", erro=erro)


# =====================================
# DASHBOARD
# =====================================

@app.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        usuario=session["nome"],
        perfil=session["perfil"]
    )


# =====================================
# LOGOUT
# =====================================

# =====================================
# LISTAR USUÁRIOS
# =====================================

@app.route("/usuarios")
def usuarios():

    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, usuario, perfil
        FROM usuarios
        ORDER BY nome
    """)

    usuarios = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "usuarios.html",
        usuarios=usuarios
    )


# =====================================
# NOVO USUÁRIO
# =====================================

@app.route("/usuarios/novo", methods=["GET", "POST"])
def novo_usuario():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session["perfil"] != "ADMIN":
        return "Acesso negado", 403

    if request.method == "POST":

        nome = request.form["nome"]
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        perfil = request.form["perfil"]

        senha_hash = generate_password_hash(senha)

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO usuarios
            (nome, usuario, senha, perfil)
            VALUES (%s,%s,%s,%s)
        """,
        (
            nome,
            usuario,
            senha_hash,
            perfil
        ))

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("usuarios"))

    return render_template("usuario_novo.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))
    
# =====================================
# EDITAR USUÁRIO
# =====================================

@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session["perfil"] != "ADMIN":
        return "Acesso negado", 403

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":

        nome = request.form["nome"]
        usuario = request.form["usuario"]
        perfil = request.form["perfil"]

        cur.execute("""
            UPDATE usuarios
            SET nome=%s,
                usuario=%s,
                perfil=%s
            WHERE id=%s
        """,
        (
            nome,
            usuario,
            perfil,
            id
        ))

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("usuarios"))

    cur.execute("""
        SELECT id,nome,usuario,perfil
        FROM usuarios
        WHERE id=%s
    """,(id,))

    usuario = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "usuario_editar.html",
        usuario=usuario
    )

# =====================================
# EXCLUIR USUÁRIO
# =====================================

@app.route("/usuarios/excluir/<int:id>")
def excluir_usuario(id):

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session["perfil"] != "ADMIN":
        return "Acesso negado",403

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM usuarios WHERE id=%s",
        (id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("usuarios"))

