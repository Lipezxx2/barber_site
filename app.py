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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/agendamento')
def agendamento():
    return render_template('agendamento.html')  

@app.route('/login', methods=['POST'])
def login_post():
   
    pass
@app.route('/cadastro', methods=['POST'])
def cadastro_post():
    
    pass

if __name__ == '__main__':
    app.run(debug=True) 
 