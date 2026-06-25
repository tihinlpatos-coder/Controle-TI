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

```
conn = get_db()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios(
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200),
    usuario VARCHAR(100) UNIQUE,
    senha VARCHAR(200),
    perfil VARCHAR(50)
)
""")

conn.commit()
cur.close()
conn.close()
```

def criar_admin():

```
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
    VALUES (%s,%s,%s,%s)
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
```

criar_tabelas()
criar_admin()

@app.route("/")
def index():
return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():

```
erro = None

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

        return redirect(url_for("dashboard"))

    erro = "Usuário ou senha inválidos"

return render_template("login.html", erro=erro)
```

@app.route("/dashboard")
def dashboard():

```
if "usuario" not in session:
    return redirect(url_for("login"))

return render_template(
    "dashboard.html",
    usuario=session["usuario"],
    perfil=session["perfil"]
)
```

@app.route("/logout")
def logout():

```
session.clear()

return redirect(url_for("login"))
```

if **name** == "**main**":
app.run(
host="0.0.0.0",
port=int(os.environ.get("PORT", 10000))
)
