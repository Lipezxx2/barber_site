import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "segredo-local")

def get_conn():
    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL"),
            sslmode="require"
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        raise

@app.route('/')
def index():
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id_galeria, caminho_imagem, descricao
            FROM galeria
            ORDER BY data_upload DESC
        """)
        imagens = cur.fetchall()

    return render_template('index.html', imagens=imagens)

@app.route('/agendamento', methods=['GET', 'POST'])
def agendamento():
    if request.method == 'POST':
        print("=== INICIANDO PROCESSAMENTO DO AGENDAMENTO ===")
        
        # Captura os dados do formulário
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        id_servico = request.form.get("id_servico", "").strip()
        data = request.form.get("data", "").strip()
        hora = request.form.get("hora", "").strip()

        print(f"Dados recebidos: nome={nome}, telefone={telefone}, servico={id_servico}, data={data}, hora={hora}")

        # Validação básica
        if not nome or not telefone or not id_servico or not data or not hora:
            flash("Preencha todos os campos.", "warning")
            print("ERRO: Campos vazios")
            return render_template("agendamento.html")
        
        conn = None
        cur = None
        
        try:
            conn = get_conn()
            cur = conn.cursor()

            print("Conexão estabelecida com sucesso")

            # 1. Insere o cliente
            cur.execute(
                "INSERT INTO cliente (nome, telefone) VALUES (%s, %s) RETURNING id_cliente",
                (nome, telefone)
            )
            id_cliente = cur.fetchone()[0]
            print(f"Cliente inserido com ID: {id_cliente}")

            # 2. Insere o agendamento
            cur.execute(
                """
                INSERT INTO agendamento (data, hora, status, id_cliente, id_servico)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_agendamento
                """,
                (data, hora, "Pendente", id_cliente, int(id_servico))
            )
            id_agendamento = cur.fetchone()[0]
            print(f"Agendamento inserido com ID: {id_agendamento}")

            # 3. Commit das transações
            conn.commit()
            print("Commit realizado com sucesso")

            flash("Agendamento realizado com sucesso!", "success")
            print("=== AGENDAMENTO CONCLUÍDO COM SUCESSO ===")
            return redirect(url_for("index"))
        
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"Erro de banco de dados: {e}")
            print(f"Código do erro: {e.pgcode}")
            print(f"Mensagem: {e.pgerror}")
            flash(f"Erro ao agendar: {str(e)}", "danger")
            return render_template("agendamento.html")
        
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro inesperado: {e}")
            flash(f"Erro ao agendar: {str(e)}", "danger")
            return render_template("agendamento.html")
        
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    # GET request - exibe o formulário
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
            ORDER BY ag.data DESC, ag.hora DESC;
        """)
        agendamentos = cur.fetchall()
    
    return render_template("painel_barbeiro.html", agendamentos=agendamentos)

@app.route("/upload-galeria", methods=["POST"])
def upload_galeria():
    # 1. Bloqueia se não estiver logado
    if "usuario_id" not in session:
        flash("Você precisa estar logado para adicionar imagens.", "danger")
        return redirect(url_for("login"))

    # 2. Lê a descrição
    descricao = request.form.get("descricao", "").strip()

    # 3. Lê a imagem
    if "imagem" not in request.files:
        flash("Nenhuma imagem enviada.", "danger")
        return redirect(url_for("index"))

    imagem = request.files["imagem"]

    # 4. Valida se o arquivo tem nome
    if imagem.filename == "":
        flash("Arquivo inválido.", "danger")
        return redirect(url_for("index"))

    # 5. Gera nome seguro
    filename = secure_filename(imagem.filename)

    # 6. Monta caminho e salva a imagem
    caminho_completo = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    imagem.save(caminho_completo)

    # 7. Insere no banco
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO galeria (caminho_imagem, descricao, id_usuario)
                VALUES (%s, %s, %s)
            """, (
                filename,
                descricao,
                session["usuario_id"]
            ))
            conn.commit()

        flash("Imagem adicionada com sucesso!", "success")

    except Exception as e:
        print("Erro ao salvar imagem:", e)
        flash("Erro ao salvar imagem.", "danger")

    # 8. Redireciona para o index
    return redirect(url_for("index"))

       

if __name__ == '__main__':
    app.run(debug=True) 
 