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

@app.route('/agendamento', methods=['GET', 'POST'])
def agendamento():
    if request.method == 'POST':
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        id_servico = request.form.get("id_servico", "").strip()
        data = request.form.get("data", "").strip()
        hora = request.form.get("hora", "").strip()

        if not nome or not telefone or not id_servico or not data or not hora:
            flash("Preencha todos os campos.", "warning")
            return render_template("agendamento.html")
        
        try:
            with get_conn() as conn, conn.cursor() as cur:

                cur.execute(
                    "INSERT INTO cliente (nome, telefone) VALUES (%s, %s) RETURNING id_cliente",
                    (nome, telefone)
                )
                id_cliente = cur.fetchone()[0]

                cur.execute(
                    """
                    INSERT INTO agendamento (data, hora, status, id_cliente, id_servico)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (data, hora, "Pendente", id_cliente, id_servico)
                )

                conn.commit()

            flash("Agendamento realizado com sucesso!", "success")
            return redirect(url_for("index"))
        
        except Exception as e:
            flash(f"Erro ao agendar: {e}", "danger")
            return render_template("agendamento.html")

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

@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da conta.", "info")
    return redirect(url_for("login"))

@app.route('/painel-barbeiro')
def painel_barbeiro():
    if "usuario_id" not in session:
        flash("Faça login para acessar o painel do barbeiro.", "warning")
        return redirect(url_for("login"))
    
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT
                    ag.id_agendamento,
                    ag.data,
                    ag.hora,
                    ag.status,
                    c.nome AS nome_cliente,
                    c.telefone,
                    s.nome AS nome_servico_nome,
                    s.preco,
                    s.duracao
            FROM agendamento ag
            JOIN cliente c ON ag.id_cliente = c.id_cliente
            JOIN servico s ON ag.id_servico = s.id_servico
            ORDER BY ag.data, ag.hora;
        """)
        agendamentos = cur.fetchall()
    
    return render_template("painel_barbeiro.html", agendamentos=agendamentos)
       

if __name__ == '__main__':
    app.run(debug=True) 
 