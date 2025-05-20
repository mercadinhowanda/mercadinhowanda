from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configurações do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Panqueca1.'
app.config['MYSQL_DB'] = 'mercadinho'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    data_limite = (datetime.today() + timedelta(days=60)).date()

    consulta = """
        SELECT 
            i.codigo,
            i.descricao,
            i.apresentacao,
            MIN(e.validade) AS validade_proxima,
            COALESCE(SUM(e.quantidade), 0) - COALESCE((
                SELECT SUM(s.quantidade) FROM saidas s WHERE s.item_id = i.id
            ), 0) AS saldo
        FROM itens i
        LEFT JOIN entradas e ON i.id = e.item_id
        GROUP BY i.id, i.codigo, i.descricao, i.apresentacao
        HAVING saldo > 0 AND validade_proxima <= %s
        ORDER BY validade_proxima ASC
    """
    cur.execute(consulta, (data_limite,))
    entradas = cur.fetchall()
    print(entradas)
    cur.close()
    return render_template('index.html', entradas=entradas)


@app.route('/consultas')
def consultas():
    cur = mysql.connection.cursor()
    consulta = """
        SELECT 
            i.codigo,
            i.descricao,
            i.apresentacao,
            MIN(e.validade) AS validade_proxima,
            COALESCE(SUM(e.quantidade), 0) - COALESCE((
                SELECT SUM(s.quantidade) FROM saidas s WHERE s.item_id = i.id
            ), 0) AS saldo
        FROM itens i
        LEFT JOIN entradas e ON i.id = e.item_id
        GROUP BY i.id, i.codigo, i.descricao, i.apresentacao
        HAVING saldo > 0
        ORDER BY i.descricao
    """
    cur.execute(consulta)
    itens = cur.fetchall()

    cur.close()
    return render_template('consultas.html', itens=itens)


@app.route('/entradas', methods=['GET', 'POST'])
def entradas():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        item_id = request.form['item_id']
        lote = request.form['lote']
        validade = request.form['validade']
        quantidade = request.form['quantidade']
        nota_fiscal = request.form['nota_fiscal']
        data = request.form['data']
        valor_unitario = float(request.form['valor_unitario'])
        valor_total = valor_unitario * int(quantidade)

        cur.execute("INSERT INTO entradas (item_id, lote, validade, quantidade, nota_fiscal, data, valor_unitario, valor_total) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", 
            (item_id, lote, validade, quantidade, nota_fiscal, data, valor_unitario, valor_total))
        mysql.connection.commit()
        return redirect(url_for('entradas'))

    cur.execute("SELECT id, descricao FROM itens")
    itens = cur.fetchall()
    cur.close()
    return render_template('entradas.html', itens=itens)


@app.route('/itens', methods=['GET', 'POST'])
def itens():
    cur = mysql.connection.cursor()
    if 'delete' in request.args:
        cur.execute("DELETE FROM itens WHERE id = %s", (request.args['delete'],))
        mysql.connection.commit()
    elif request.method == 'POST':
        cur.execute("INSERT INTO itens (codigo, descricao, apresentacao, marca, tipo) VALUES (%s, %s, %s, %s, %s)",
                    (request.form['codigo'],
                     request.form['descricao'],
                     request.form['apresentacao'],
                     request.form['marca'],
                     request.form['tipo']))
        mysql.connection.commit()
    cur.execute("SELECT * FROM itens")
    itens = cur.fetchall()
    cur.close()
    return render_template('itens.html', itens=itens)


@app.route('/saidas', methods=['GET', 'POST'])
def saidas():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        cur.execute("INSERT INTO saidas (item_id, quantidade, data) VALUES (%s, %s, %s)",
                    (request.form['item_id'], request.form['quantidade'], request.form['data']))
        cur.execute("UPDATE itens SET quantidade = quantidade - %s WHERE id = %s",
                    (request.form['quantidade'], request.form['item_id']))
        mysql.connection.commit()
    cur.execute("SELECT * FROM itens")
    itens = cur.fetchall()
    cur.close()
    return render_template('saidas.html', itens=itens)

@app.route('/cadastros')
def cadastros():
    return render_template('cadastros.html')

@app.route('/usuarios', methods=['GET', 'POST'])
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


@app.route('/fornecedores', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    app.run(debug=True)
