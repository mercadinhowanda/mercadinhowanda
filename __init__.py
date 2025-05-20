from flask import Flask
from flask_mysqldb import MySQL
from app.routes import main

app = Flask(__name__)
app.config.from_object('config.Config')
mysql = MySQL(app)

app.register_blueprint(main)