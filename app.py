import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "segredo-local")

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agendamento')
def agendamento():
    return render_template('agendamento.html')  

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        if not nome or not email or not senha:
            flash("Preencha todos os campos.", "warning")
            return render_template("cadastro.html")

        senha_hash = generate_password_hash(senha)

        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)",
                    (nome, email, senha_hash)
                )
                conn.commit()

            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("login"))

        except psycopg2.errors.UniqueViolation:
            flash("Este email já está em uso.", "danger")

    return render_template("cadastro.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        if not email or not senha:
            flash("Preencha todos os campos.", "warning")
            return render_template("login.html")

        with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id_usuario, nome, senha FROM usuario WHERE email = %s", (email,))
            user = cur.fetchone()

        if user and check_password_hash(user["senha"], senha):
            session["usuario_id"] = user["id_usuario"]
            session["nome"] = user["nome"]
            flash(f"Bem-vindo, {user['nome']}!", "success")
            return redirect(url_for("index"))

        flash("Email ou senha inválidos.", "danger")

    return render_template("login.html")

    

if __name__ == '__main__':
    app.run(debug=True) 
 