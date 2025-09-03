from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# HTML do formulário (mesmo código anterior)
HTML_FORMULARIO = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Agendamento - Barbearia</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
        .mensagem { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .sucesso { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .erro { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        input, select { width: 100%; padding: 8px; margin: 5px 0; box-sizing: border-box; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>Agendamento Barbearia</h1>
    
    {% if mensagem %}
        <div class="mensagem {{ 'sucesso' if cor == 'green' else 'erro' }}">
            {{ mensagem }}
        </div>
    {% endif %}
    
    <form action="/agendar" method="POST">
        <p>
            <label>Nome:</label><br>
            <input type="text" name="nome" placeholder="Digite seu nome" required>
        </p>
        
        <p>
            <label>Telefone:</label><br>
            <input type="tel" name="telefone" placeholder="(34) 99999-9999" required>
        </p>
        
        <p>
            <label>Data:</label><br>
            <input type="date" name="data" required>
        </p>
        
        <p>
            <label>Horário:</label><br>
            <select name="horario" required>
                <option value="">Selecione um horário</option>
                <option value="08:00">08:00</option>
                <option value="08:30">08:30</option>
                <option value="09:00">09:00</option>
                <option value="09:30">09:30</option>
                <option value="10:00">10:00</option>
                <option value="10:30">10:30</option>
                <option value="11:00">11:00</option>
                <option value="11:30">11:30</option>
                <option value="14:00">14:00</option>
                <option value="14:30">14:30</option>
                <option value="15:00">15:00</option>
                <option value="15:30">15:30</option>
                <option value="16:00">16:00</option>
                <option value="16:30">16:30</option>
                <option value="17:00">17:00</option>
                <option value="17:30">17:30</option>
            </select>
        </p>
        
        <p>
            <label>Serviço:</label><br>
            <select name="servico" required>
                <option value="">Selecione o serviço</option>
                <option value="Corte">Corte - R$ 25,00</option>
                <option value="Barba">Barba - R$ 20,00</option>
                <option value="Corte + Barba">Corte + Barba - R$ 45,00</option>
            </select>
        </p>
        
        <p>
            <button type="submit">Agendar Horário</button>
        </p>
    </form>

    <hr>
    
    <h2>Agendamentos de Hoje</h2>
    {% if agendamentos %}
        {% for agendamento in agendamentos %}
            <p><strong>{{ agendamento[0] }}</strong> - {{ agendamento[1] }} - {{ agendamento[2] }} ({{ agendamento[3] }})</p>
        {% endfor %}
    {% else %}
        <p><em>Nenhum agendamento para hoje.</em></p>
    {% endif %}
</body>
</html>
'''

def criar_banco():
    """Cria as tabelas do banco"""
    conn = sqlite3.connect('barbearia.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data DATE,
            horario TIME,
            servico TEXT,
            status TEXT DEFAULT 'Agendado',
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def adicionar_cliente(nome, telefone):
    """Adiciona cliente no banco ou retorna ID se já existe"""
    conn = sqlite3.connect('barbearia.db')
    cursor = conn.cursor()
    
    try:
        # Verifica se cliente já existe pelo telefone
        cursor.execute('SELECT id FROM clientes WHERE telefone = ?', (telefone,))
        cliente_existente = cursor.fetchone()
        
        if cliente_existente:
            conn.close()
            return cliente_existente[0]
        
        # Insere novo cliente
        cursor.execute('INSERT INTO clientes (nome, telefone) VALUES (?, ?)', (nome, telefone))
        cliente_id = cursor.lastrowid  # 🔧 CORREÇÃO: usar cursor.lastrowid
        conn.commit()
        
        return cliente_id
        
    except sqlite3.Error as e:
        print(f"Erro ao adicionar cliente: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def verificar_horario_disponivel(data, horario):
    """Verifica se horário está livre"""
    conn = sqlite3.connect('barbearia.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT COUNT(*) FROM agendamentos 
            WHERE data = ? AND horario = ? AND status = 'Agendado'
        ''', (data, horario))
        resultado = cursor.fetchone()
        return resultado[0] == 0
    except sqlite3.Error as e:
        print(f"Erro ao verificar horário: {e}")
        return False
    finally:
        conn.close()

def criar_agendamento(cliente_id, data, horario, servico):
    """Cria agendamento"""
    conn = sqlite3.connect('barbearia.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO agendamentos (cliente_id, data, horario, servico)
            VALUES (?, ?, ?, ?)
        ''', (cliente_id, data, horario, servico))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao criar agendamento: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def listar_agendamentos_hoje():
    """Lista agendamentos de hoje"""
    conn = sqlite3.connect('barbearia.db')
    cursor = conn.cursor()
    
    try:
        hoje = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT c.nome, c.telefone, a.horario, a.servico
            FROM agendamentos a
            JOIN clientes c ON a.cliente_id = c.id
            WHERE a.data = ? AND a.status = 'Agendado'
            ORDER BY a.horario
        ''', (hoje,))
        
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao listar agendamentos: {e}")
        return []
    finally:
        conn.close()

@app.route('/')
def home():
    """Página inicial com formulário"""
    agendamentos = listar_agendamentos_hoje()
    return render_template_string(HTML_FORMULARIO, agendamentos=agendamentos)

@app.route('/agendar', methods=['POST'])
def agendar():
    """Processa o agendamento"""
    try:
        nome = request.form['nome'].strip()
        telefone = request.form['telefone'].strip()
        data = request.form['data']
        horario = request.form['horario']
        servico = request.form['servico']
        
        # Validações básicas
        if not all([nome, telefone, data, horario, servico]):
            agendamentos = listar_agendamentos_hoje()
            return render_template_string(HTML_FORMULARIO, 
                                        mensagem="❌ Todos os campos são obrigatórios!", 
                                        cor="red",
                                        agendamentos=agendamentos)
        
        # Verifica se horário está disponível
        if not verificar_horario_disponivel(data, horario):
            agendamentos = listar_agendamentos_hoje()
            return render_template_string(HTML_FORMULARIO, 
                                        mensagem="❌ Horário não disponível! Escolha outro horário.", 
                                        cor="red",
                                        agendamentos=agendamentos)
        
        # Cria cliente e agendamento
        cliente_id = adicionar_cliente(nome, telefone)
        
        if cliente_id is None:
            agendamentos = listar_agendamentos_hoje()
            return render_template_string(HTML_FORMULARIO, 
                                        mensagem="❌ Erro ao cadastrar cliente. Tente novamente.", 
                                        cor="red",
                                        agendamentos=agendamentos)
        
        if criar_agendamento(cliente_id, data, horario, servico):
            agendamentos = listar_agendamentos_hoje()
            return render_template_string(HTML_FORMULARIO, 
                                        mensagem=f"✅ Agendamento criado com sucesso! {nome} - {data} às {horario}", 
                                        cor="green",
                                        agendamentos=agendamentos)
        else:
            agendamentos = listar_agendamentos_hoje()
            return render_template_string(HTML_FORMULARIO, 
                                        mensagem="❌ Erro ao criar agendamento. Tente novamente.", 
                                        cor="red",
                                        agendamentos=agendamentos)
            
    except Exception as e:
        print(f"Erro no agendamento: {e}")
        agendamentos = listar_agendamentos_hoje()
        return render_template_string(HTML_FORMULARIO, 
                                    mensagem="❌ Erro interno. Tente novamente.", 
                                    cor="red",
                                    agendamentos=agendamentos)

if __name__ == '__main__':
    criar_banco()  # Cria banco na primeira vez
    print("🚀 Servidor rodando em: http://localhost:5000")
    app.run(debug=True)