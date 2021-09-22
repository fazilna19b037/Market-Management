from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
#from flask_login import LoginManager
#import mysql.connector
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
#db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='FAZil@33'
app.config['MYSQL_DB']='market'

mysql=MySQL(app)

'''login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"'''
from market import routes

'''mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="FAZil@33",
    database="dbfootball"
    )'''