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
</head>
<body>
    <h1>Agendamento Barbearia</h1>
    
    {% if mensagem %}
        <p style="color: {{ cor }}; background: #f0f0f0; padding: 10px;">
            {{ mensagem }}
        </p>
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
    {% for agendamento in agendamentos %}
        <p>{{ agendamento[0] }} - {{ agendamento[1] }} - {{ agendamento[2] }} ({{ agendamento[3] }})</p>
    {% endfor %}
</body>
</html>
'''

def criar_banco():
    """Cria as tabelas do banco"""
    conn = sqlite3.connect('barbearia.db')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
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
    """Adiciona cliente no banco"""
    conn = sqlite3.connect('barbearia.db')
    conn.execute('INSERT INTO clientes (nome, telefone) VALUES (?, ?)', (nome, telefone))
    conn.commit()
    cliente_id = conn.lastrowid
    conn.close()
    return cliente_id

def verificar_horario_disponivel(data, horario):
    """Verifica se horário está livre"""
    conn = sqlite3.connect('barbearia.db')
    resultado = conn.execute('''
        SELECT COUNT(*) FROM agendamentos 
        WHERE data = ? AND horario = ? AND status = 'Agendado'
    ''', (data, horario)).fetchone()
    conn.close()
    return resultado[0] == 0

def criar_agendamento(cliente_id, data, horario, servico):
    """Cria agendamento"""
    conn = sqlite3.connect('barbearia.db')
    conn.execute('''
        INSERT INTO agendamentos (cliente_id, data, horario, servico)
        VALUES (?, ?, ?, ?)
    ''', (cliente_id, data, horario, servico))
    conn.commit()
    conn.close()

def listar_agendamentos_hoje():
    """Lista agendamentos de hoje"""
    conn = sqlite3.connect('barbearia.db')
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    agendamentos = conn.execute('''
        SELECT c.nome, c.telefone, a.horario, a.servico
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        WHERE a.data = ? AND a.status = 'Agendado'
        ORDER BY a.horario
    ''', (hoje,)).fetchall()
    
    conn.close()
    return agendamentos

@app.route('/')
def home():
    """Página inicial com formulário"""
    agendamentos = listar_agendamentos_hoje()
    return render_template_string(HTML_FORMULARIO, agendamentos=agendamentos)

@app.route('/agendar', methods=['POST'])
def agendar():
    """Processa o agendamento"""
    nome = request.form['nome']
    telefone = request.form['telefone']
    data = request.form['data']
    horario = request.form['horario']
    servico = request.form['servico']
    
    # Verifica se horário está disponível
    if not verificar_horario_disponivel(data, horario):
        agendamentos = listar_agendamentos_hoje()
        return render_template_string(HTML_FORMULARIO, 
                                    mensagem="❌ Horário não disponível!", 
                                    cor="red",
                                    agendamentos=agendamentos)
    
    # Cria cliente e agendamento
    cliente_id = adicionar_cliente(nome, telefone)
    criar_agendamento(cliente_id, data, horario, servico)
    
    agendamentos = listar_agendamentos_hoje()
    return render_template_string(HTML_FORMULARIO, 
                                mensagem=f"✅ Agendamento criado! {nome} - {data} às {horario}", 
                                cor="green",
                                agendamentos=agendamentos)

if __name__ == '__main__':
    criar_banco()  # Cria banco na primeira vez
    print("🚀 Servidor rodando em: http://localhost:5000")
    app.run(debug=True)