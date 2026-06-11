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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(200) NOT NULL,
        quantidade INTEGER NOT NULL
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Sistema Hospitalar</title>
<style>
body{font-family:Arial;background:#f4f4f4;padding:30px}
.card{background:white;padding:20px;border-radius:10px}
input,button{padding:10px;margin:5px;width:100%}
table{width:100%;margin-top:20px;border-collapse:collapse}
th,td{border:1px solid #ccc;padding:10px}
button{background:#2563eb;color:white;border:none}
</style>
</head>
<body>
<div class="card">

<h1>Sistema Hospitalar</h1>

<form method="POST" action="/novo">
<input type="text" name="nome" placeholder="Nome do produto" required>
<input type="number" name="quantidade" placeholder="Quantidade" required>
<button type="submit">Cadastrar Produto</button>
</form>

<table>
<tr>
<th>ID</th>
<th>Produto</th>
<th>Quantidade</th>
</tr>

{% for p in produtos %}
<tr>
<td>{{p[0]}}</td>
<td>{{p[1]}}</td>
<td>{{p[2]}}</td>
</tr>
{% endfor %}

</table>

</div>
</body>
</html>
"""

criar_tabelas()

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

    return render_template_string(HTML, produtos=produtos)

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
