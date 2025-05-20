from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from app import mysql
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    hoje = datetime.today().date()
    aviso_data = hoje + timedelta(days=7)
    cur = mysql.connection.cursor()
    cur.execute("SELECT nome, validade FROM itens WHERE validade IS NOT NULL AND validade <= %s", (aviso_data,))
    avisos = cur.fetchall()
    cur.close()
    return render_template('index.html', avisos=avisos)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
        user = cur.fetchone()
        cur.close()
        if user:
            session['usuario'] = user[1]
            flash('Login realizado com sucesso!')
            return redirect(url_for('main.index'))
        else:
            flash('Email ou senha incorretos.')
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Logout realizado.')
    return redirect(url_for('main.login'))

@main.route('/consultas')
def consultas():
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT i.id, i.nome, i.quantidade,
          IFNULL(SUM(e.quantidade), 0) AS total_entradas,
          IFNULL(SUM(s.quantidade), 0) AS total_saidas,
          i.validade, i.categoria
        FROM itens i
        LEFT JOIN entradas e ON i.id = e.item_id
        LEFT JOIN saidas s ON i.id = s.item_id
        GROUP BY i.id
    ''')
    estoque = cur.fetchall()
    cur.close()
    return render_template('consultas.html', estoque=estoque)

@main.route('/entradas', methods=['GET', 'POST'])
def entradas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nome FROM itens")
    itens = cur.fetchall()
    if request.method == 'POST':
        item_id = request.form['item_id']
        quantidade = request.form['quantidade']
        data = request.form['data']
        cur.execute("INSERT INTO entradas (item_id, quantidade, data) VALUES (%s, %s, %s)", (item_id, quantidade, data))
        mysql.connection.commit()
        flash('Entrada registrada.')
    cur.close()
    return render_template('entradas.html', itens=itens)

@main.route('/saidas', methods=['GET', 'POST'])
def saidas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nome FROM itens")
    itens = cur.fetchall()
    if request.method == 'POST':
        item_id = request.form['item_id']
        quantidade = request.form['quantidade']
        data = request.form['data']
        cur.execute("INSERT INTO saidas (item_id, quantidade, data) VALUES (%s, %s, %s)", (item_id, quantidade, data))
        mysql.connection.commit()
        flash('Saída registrada.')
    cur.close()
    return render_template('saidas.html', itens=itens)

@main.route('/cadastros')
def cadastros():
    return render_template('cadastros.html')

@main.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    cur = mysql.connection.cursor()
    if 'delete' in request.args:
        cur.execute("DELETE FROM usuarios WHERE id = %s", (request.args['delete'],))
        mysql.connection.commit()
    elif request.method == 'POST':
        cur.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
                    (request.form['nome'], request.form['email'], request.form['senha']))
        mysql.connection.commit()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    return render_template('usuarios.html', usuarios=usuarios)

@main.route('/itens', methods=['GET', 'POST'])
def itens():
    cur = mysql.connection.cursor()
    if 'delete' in request.args:
        cur.execute("DELETE FROM itens WHERE id = %s", (request.args['delete'],))
        mysql.connection.commit()
    elif request.method == 'POST':
        cur.execute("INSERT INTO itens (nome, quantidade, validade, categoria) VALUES (%s, %s, %s, %s)",
                    (request.form['nome'], request.form['quantidade'], request.form['validade'], request.form['categoria']))
        mysql.connection.commit()
    cur.execute("SELECT * FROM itens")
    itens = cur.fetchall()
    cur.close()
    return render_template('itens.html', itens=itens)

@main.route('/fornecedores', methods=['GET', 'POST'])
def fornecedores():
    cur = mysql.connection.cursor()
    if 'delete' in request.args:
        cur.execute("DELETE FROM fornecedores WHERE id = %s", (request.args['delete'],))
        mysql.connection.commit()
    elif request.method == 'POST':
        cur.execute("INSERT INTO fornecedores (nome, contato) VALUES (%s, %s)",
                    (request.form['nome'], request.form['contato']))
        mysql.connection.commit()
    cur.execute("SELECT * FROM fornecedores")
    fornecedores = cur.fetchall()
    cur.close()
    return render_template('fornecedores.html', fornecedores=fornecedores)
