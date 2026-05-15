from flask import Flask, request, redirect, session, render_template_string
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "hospital-secret-key")

USUARIO = "admin"
SENHA = "1234"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("usuario") == USUARIO and request.form.get("senha") == SENHA:
            session["logado"] = True
            return redirect("/sistema")
        return "<h3>Usuário ou senha inválidos.</h3><a href='/'>Voltar</a>"
    return """
    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css' rel='stylesheet'>
    <div class='container mt-5' style='max-width:420px'>
      <div class='card shadow border-0 rounded-4'><div class='card-body p-4'>
        <h2 class='mb-4'>🏥 Sistema Hospitalar</h2>
        <form method='post'>
          <input class='form-control mb-3' name='usuario' placeholder='Usuário'>
          <input class='form-control mb-3' type='password' name='senha' placeholder='Senha'>
          <button class='btn btn-primary w-100'>Entrar</button>
        </form>
        <small class='text-muted d-block mt-3'>Usuário: admin | Senha: 1234</small>
      </div></div>
    </div>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/sistema")
def sistema():
    if not session.get("logado"):
        return redirect("/")
    return """
    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css' rel='stylesheet'>
    <div class='container mt-4'>
      <div class='p-4 bg-white rounded shadow-sm'>
        <h1>🏥 Sistema Hospitalar</h1>
        <p class='text-muted'>Controle de Estoque</p>
        <hr>
        <h4>Nenhum produto cadastrado</h4>
        <p>Clique em 'Novo Produto' para começar.</p>
        <a href='/logout' class='btn btn-outline-secondary'>Sair</a>
      </div>
    </div>
    """

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
